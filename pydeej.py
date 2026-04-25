#!/usr/bin/env python3

import serial
import threading
import time
import yaml
import sys
import argparse
from pathlib import Path
from collections import deque
from queue import Queue
import logging
import platform

# ---------------- Windows ----------------
if platform.system() == "Windows":
    try:
        from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, IAudioEndpointVolume
        import comtypes
        WINDOWS = True
    except ImportError:
        WINDOWS = False
else:
    WINDOWS = False

# ---------------- Linux ----------------
if platform.system() == "Linux":
    try:
        import pulsectl
        LINUX = True
    except Exception:
        LINUX = False
else:
    LINUX = False


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pydeej")


# =========================================================
# Volume Controller
# =========================================================
class VolumeController:
    def __init__(self):
        self.sessions = {}
        self.pulse = None

        if LINUX:
            try:
                self.pulse = pulsectl.Pulse("deej")
            except:
                self.pulse = None

    # ---------------- Windows ----------------
    def refresh_windows(self):
        if not WINDOWS:
            return

        self.sessions = {}
        for s in AudioUtilities.GetAllSessions():
            if s.Process:
                self.sessions[s.Process.name().lower()] = s

    def set_windows(self, app, volume):
        for s in AudioUtilities.GetAllSessions():
            if s.Process and app in s.Process.name().lower():
                vol = s._ctl.QueryInterface(ISimpleAudioVolume)
                vol.SetMasterVolume(volume / 100.0, None)
                return

    # ---------------- Linux ----------------
    def set_linux(self, app, volume):
        if not self.pulse:
            return

        for sink in self.pulse.sink_input_list():
            props = getattr(sink, "proplist", {})
            name = props.get("application.process.binary", "").lower()

            if app in name:
                self.pulse.volume_set_all_chans(sink, volume / 100.0)
                return

    # ---------------- Master ----------------
    def set_master(self, volume):
        if WINDOWS:
            try:
                dev = AudioUtilities.GetSpeakers()
                vol = dev.EndpointVolume
                vol.SetMasterVolumeLevelScalar(volume / 100.0, None)
            except Exception as e:
                logger.error(f"Failed to set master volume: {e}")

        elif LINUX and self.pulse:
            sinks = self.pulse.sink_list()
            if sinks:
                self.pulse.volume_set_all_chans(sinks[0], volume / 100.0)

    # ---------------- Unified ----------------
    def set(self, app, volume):
        app = app.lower()

        if app == "master":
            self.set_master(volume)
        elif WINDOWS:
            self.set_windows(app, volume)
        elif LINUX:
            self.set_linux(app, volume)

    # ---------------- App list ----------------
    def list_apps(self):
        apps = set()

        if WINDOWS:
            self.refresh_windows()
            apps = set(self.sessions.keys())

        elif LINUX and self.pulse:
            for s in self.pulse.sink_input_list():
                props = getattr(s, "proplist", {})
                name = props.get("application.process.binary", "")
                if name:
                    apps.add(name.lower())

        return sorted(apps)


# =========================================================
# Noise filter
# =========================================================
class NoiseReducer:
    def __init__(self, n, size=15, threshold=10):
        self.buffers = [deque(maxlen=size) for _ in range(n)]
        self.last = [512] * n
        self.threshold = threshold

    def update(self, values):
        out = []
        for i, v in enumerate(values):
            diff = abs(v - self.last[i])
            if diff >= self.threshold:
                self.buffers[i].append(v)
                self.last[i] = v
            else:
                self.buffers[i].append(self.last[i])
            smoothed = round(sum(self.buffers[i]) / len(self.buffers[i]))
            out.append(smoothed)
        return out


# =========================================================
# Serial Reader
# =========================================================
class SerialReader:
    def __init__(self, port, baud, sliders, debug=False, jitter_threshold=10, reconnect=True):
        self.port = port
        self.baud = baud
        self.sliders = sliders
        self.debug = debug
        self.reconnect = reconnect
        self.reconnect_delay = 2

        self.serial = None
        self.running = False
        self.queue = Queue()

        self.noise = NoiseReducer(sliders, threshold=jitter_threshold)

    def connect(self):
        try:
            if self.serial and self.serial.is_open:
                return True
            self.serial = serial.Serial(self.port, self.baud, timeout=1)
            logger.info(f"Connected to {self.port}")
            return True
        except Exception as e:
            if self.debug:
                logger.error(f"Serial connect error: {e}")
            return False

    def parse(self, line):
        try:
            vals = [int(x) for x in line.strip().split("|")]
            return vals if len(vals) == self.sliders else None
        except:
            return None

    def loop(self):
        while self.running:
            if not self.serial or not self.serial.is_open:
                if self.reconnect:
                    logger.info(f"Serial disconnected, reconnecting in {self.reconnect_delay}s...")
                    time.sleep(self.reconnect_delay)
                    if not self.connect():
                        continue
                else:
                    break

            try:
                if self.serial.in_waiting:
                    line = self.serial.readline().decode(errors="ignore")
                    raw = self.parse(line)

                    if raw:
                        smooth = self.noise.update(raw)
                        self.queue.put(smooth)

                        if self.debug:
                            print("RAW   :", raw)
                            print("SMOOTH:", smooth)

                time.sleep(0.002)

            except serial.SerialException as e:
                logger.error(f"Serial error: {e}")
                if self.serial:
                    try:
                        self.serial.close()
                    except:
                        pass
                self.serial = None

            except Exception as e:
                logger.error(f"Loop error: {e}")

    def start(self):
        if not self.connect():
            if not self.reconnect:
                return False

        self.running = True
        threading.Thread(target=self.loop, daemon=True).start()
        return True

    def get(self):
        latest = None
        while not self.queue.empty():
            latest = self.queue.get()
        return latest


# =========================================================
# App
# =========================================================
class DeejApp:
    def __init__(self, config, debug=False):
        self.config = Path(config)
        self.debug = debug
        self.volume = VolumeController()
        self.reader = None
        self.running = False

    def load(self):
        with open(self.config) as f:
            return yaml.safe_load(f)

    def run(self):
        cfg = self.load()

        mapping = cfg.get("slider_mapping", {})
        port = cfg.get("com_port", "COM3")
        baud = cfg.get("baud_rate", 9600)
        jitter = cfg.get("jitter_threshold", 10)
        invert = cfg.get("invert_sliders", False)
        reconnect = cfg.get("reconnect", True)

        sliders = max(map(int, mapping.keys())) + 1

        self.reader = SerialReader(port, baud, sliders, self.debug, jitter_threshold=jitter, reconnect=reconnect)
        self.last_percent = {}
        self.invert = invert

        def handle(values):
            if self.invert:
                values = [1023 - v for v in values]

            for i, v in enumerate(values):
                key = str(i)

                if key not in mapping:
                    continue

                percent = int((v / 1023) * 100)
                apps = mapping[key]

                if key not in self.last_percent or self.last_percent[key] != percent:
                    self.last_percent[key] = percent

                    if isinstance(apps, str):
                        apps = [apps]

                    for app in apps:
                        self.volume.set(app, percent)

        if not self.reader.start():
            print("Failed to start serial")
            return

        print("Running... Right-click tray icon to quit")

        self.running = True
        while self.running:
            data = self.reader.get()
            if data:
                handle(data)
            time.sleep(0.01)

        if self.reader:
            self.reader.running = False
        print("Stopped.")


# =========================================================
# Main
# =========================================================
def get_config_path(default):
    p = Path(default)
    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).parent
        bundle_dir = Path(sys._MEIPASS)
        bundled = bundle_dir / p.name
        local = exe_dir / p.name
        if local.exists():
            return str(local)
        if bundled.exists():
            local.write_bytes(bundled.read_bytes())
            return str(local)
    elif not p.is_absolute():
        if p.exists():
            return default
    return default

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--applist", action="store_true")
    parser.add_argument("--portlist", action="store_true")
    parser.add_argument("--no-tray", action="store_true", help="Disable system tray")
    args = parser.parse_args()

    config_path = get_config_path(args.config)
    app = DeejApp(config_path, args.debug)

    # ---------------- App list mode ----------------
    if args.applist:
        vc = VolumeController()
        print("\nActive apps:\n")
        for a in vc.list_apps():
            print(" -", a)
        return

    # ---------------- Port list mode ----------------
    if args.portlist:
        import serial.tools.list_ports
        print("\nAvailable serial ports:\n")
        for port in serial.tools.list_ports.comports():
            print(f" - {port.device}  ({port.description})")
        return

    # ---------------- System tray ----------------
    if not args.no_tray:
        import tray
        def on_quit():
            app.running = False
        tray.start(on_quit=on_quit)

    app.run()


if __name__ == "__main__":
    main()