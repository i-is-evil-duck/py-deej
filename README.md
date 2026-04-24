pydeej
=====

Hardware volume controller that maps Arduino slider positions to application and
master volume levels on Windows and Linux.

Built for use with the deej hardware project: https://github.com/omriharel/deej

Features
--------
- Map sliders to individual applications or master volume
- Smooth slider movement to reduce jitter
- Only update volume when changes detected (prevents audio glitches)
- Supports Windows (pycaw) and Linux (PulseAudio)
- Noise reduction with configurable buffer size and jitter threshold

Setup
-----
1. Install dependencies::

    pip install -r requirements.txt

2. Edit ``config.yaml`` to match your setup:

- ``slider_mapping``: Maps slider numbers (0-n) to application exe names or "master"
- ``jitter_threshold``: Minimum slider movement before updating (default 10)
- ``com_port``: Serial port (e.g., COM3 on Windows, /dev/ttyUSB0 on Linux)
- ``baud_rate``: Baud rate (default 9600)
- ``invert_sliders``: Set to true to invert slider values

Run::

    python deej.py

Or with options::

    python deej.py --config config.yaml --debug

List active applications::

    python deej.py --applist