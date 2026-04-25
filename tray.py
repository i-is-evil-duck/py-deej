#!/usr/bin/env python3

import sys
import threading

try:
    from pystray import MenuItem as Item
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    pystray = None
    Item = None


_icon = None
_on_quit = None


def _create_icon_image():
    img = Image.new('RGB', (64, 64), color='#e94560')
    draw = ImageDraw.Draw(img)
    draw.rectangle([8, 8, 56, 56], outline='#fff', width=3)
    draw.line([(16, 16), (16, 48)], fill='#fff', width=4)
    draw.line([(32, 16), (32, 48)], fill='#fff', width=4)
    draw.line([(48, 16), (48, 48)], fill='#fff', width=4)
    return img


def _quit_handler(icon, item):
    if _on_quit:
        _on_quit()
    global _icon
    if _icon:
        _icon.stop()
        _icon = None


def start(on_quit=None):
    global _icon, _on_quit

    if not TRAY_AVAILABLE:
        return None

    _on_quit = on_quit

    menu = Item('Quit', _quit_handler)
    _icon = pystray.Icon("pydeej", _create_icon_image(), "PyDeej", menu)

    def run():
        _icon.run()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return _icon


def stop():
    global _icon
    if _icon:
        _icon.stop()
        _icon = None