import PyInstaller.__main__
import platform
from pathlib import Path

spec_dir = Path(__file__).parent

system = platform.system()
if system == "Windows":
    app_name = "pydeej.exe"
    data_sep = ";"
elif system == "Darwin":
    app_name = "pydeej"
    data_sep = ":"
else:
    app_name = "pydeej"
    data_sep = ":"

config_data = f"{spec_dir / 'config.yaml'}{data_sep}."

args = [
    str(spec_dir / "pydeej.py"),
    f"--name={app_name}",
    "--onefile",
    "--console",
    f"--add-data={config_data}",
    f"--distpath={spec_dir}/dist",
    f"--workpath={spec_dir}/build",
    f"--specpath={spec_dir}",
]

if system == "Windows":
    args.append("--hidden-import=comtypes")
    args.append("--exclude-module=pulsectl")
elif system in ("Linux", "Darwin"):
    args.append("--exclude-module=pycaw")
    args.append("--exclude-module=comtypes")

PyInstaller.__main__.run(args)