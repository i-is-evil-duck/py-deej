# PyDeej  <br />  <img alt="Stargazers" src="https://img.shields.io/github/stars/i-is-evil-duck/py-deej?style=for-the-badge&logo=starship&color=C9CBFF&logoColor=D9E0EE&labelColor=302D41">


## PyDeej
Hardware volume controller that maps Arduino slider positions to application and master volume levels on Windows, Linux, and macOS.

## Downloads

Download the pre-built executables from the [releases](https://github.com/i-is-evil-duck/py-deej/releases) page.

| Platform | File |
|----------|------|
| Windows | `pydeej.exe` |
| Linux | `pydeej` |
| macOS | `pydeej` |

## Build from Source

```bash
# Clone the repo
git clone https://github.com/i-is-evil-duck/py-deej.git
cd py-deej

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build
python build.py
```

The executable will be in the `dist/` folder.

## Setup

Edit `config.yaml` to match your setup:

- `slider_mapping`: Maps slider numbers (0-n) to application names or "master"
- `com_port`: Serial port (e.g., COM3 on Windows, /dev/ttyUSB0 on Linux)
- `baud_rate`: Baud rate (default 9600)
- `jitter_threshold`: Minimum slider movement before updating (default 10)
- `invert_sliders`: Set to true to invert slider values
- `reconnect`: Auto-reconnect on serial disconnect (default true)

## Usage

Run the executable:
```bash
./pydeej
```

With options:
```bash
./pydeej --config config.yaml --debug
```

List active applications:
```bash
./pydeej --applist
```

## Views

<img src="https://count.getloli.com/get/@PyDeej?theme=rule34" />