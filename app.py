#!/usr/bin/env python3

import sys
import argparse
import threading
import time

import deej
import ui
import tray


_volume_thread = None
_deej_app = None
_running = True


def _run_volume_control(config_path, debug):
    global _deej_app
    _deej_app = deej.DeejApp(config_path, debug)
    _deej_app.run()


def _open_ui_from_tray():
    ui.start()


def _quit_from_tray():
    global _running
    _running = False
    tray.stop()
    if _deej_app:
        _deej_app.reader.running = False


def main():
    global _volume_thread, _running
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--port", default=5000, type=int, help="UI server port")
    parser.add_argument("--no-tray", action="store_true", help="Disable system tray icon")
    args = parser.parse_args()

    # Start volume control in background thread
    _volume_thread = threading.Thread(target=_run_volume_control, args=(args.config, args.debug), daemon=True)
    _volume_thread.start()
    
    # Start tray icon
    if not args.no_tray:
        tray.start(on_open_ui=_open_ui_from_tray, on_quit=_quit_from_tray)
    
    # Wait forever (tray runs in background)
    while _running:
        time.sleep(1)


if __name__ == "__main__":
    main()