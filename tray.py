#!/usr/bin/env python3

try:
    from pystray import MenuItem as Item
    import pystray
    from PIL import Image, ImageDraw
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    pystray = None
    Item = None

import threading

_icon = None
_on_open_ui = None
_on_quit = None


def _create_icon_image():
    img = Image.new('RGB', (64, 64), color='#e94560')
    draw = ImageDraw.Draw(img)
    draw.rectangle([8, 8, 56, 56], outline='#fff', width=3)
    draw.line([(16, 16), (16, 48)], fill='#fff', width=4)
    draw.line([(32, 16), (32, 48)], fill='#fff', width=4)
    draw.line([(48, 16), (48, 48)], fill='#fff', width=4)
    return img


def _open_handler(icon, item):
    try:
        if _on_open_ui:
            _on_open_ui()
    except Exception:
        pass


def _quit_handler(icon, item):
    try:
        if _on_quit:
            _on_quit()
    except Exception:
        pass


def start(on_open_ui=None, on_quit=None):
    global _icon, _on_open_ui, _on_quit
    
    if not PYSTRAY_AVAILABLE:
        return None
    
    _on_open_ui = on_open_ui
    _on_quit = on_quit
    
    menu = Item('Open Config', _open_handler), Item('Quit', _quit_handler)
    _icon = pystray.Icon("deej", _create_icon_image(), "Deej", menu)
    
    def run():
        _icon.run()
    
    threading.Thread(target=run, daemon=True).start()
    return _icon


def stop():
    global _icon
    if _icon:
        _icon.stop()
        _icon = None