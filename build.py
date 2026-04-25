import PyInstaller.__main__
import platform
from pathlib import Path

spec_dir = Path(__file__).parent

system = platform.system()
if system == "Windows":
    ext = ".exe"
    app_name = "pydeej.exe"
    data_flag = "--add-data"
    data_sep = ";"
elif system == "Darwin":
    ext = ".app"
    app_name = "pydeej"
    data_flag = "--add-data"
    data_sep = ":"
else:
    ext = ""
    app_name = "pydeej"
    data_flag = "--add-data"
    data_sep = ":"

config_data = f"{spec_dir / 'config.yaml'}{data_sep}."

args = [
    str(spec_dir / "pydeej.py"),
    f"--name={app_name}",
    "--onefile",
    "--console",
    f"{data_flag}={config_data}",
    "--hidden-import=comtypes",
    f"--distpath={spec_dir}/dist",
    f"--workpath={spec_dir}/build",
    f"--specpath={spec_dir}",
]

PyInstaller.__main__.run(args)