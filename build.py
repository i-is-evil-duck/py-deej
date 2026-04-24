import PyInstaller.__main__
import os
from pathlib import Path

spec_dir = Path(__file__).parent

PyInstaller.__main__.run([
    str(spec_dir / "deej.py"),
    f"--name=deej",
    "--onefile",
    "--console",
    f"--add-data={spec_dir / 'config.yaml'};.",
    "--hidden-import=comtypes",
    "--hidden-import=pyserial",
    "--hidden-import=pyyaml",
    "--hidden-import=pulsectl",
    f"--distpath={spec_dir}/dist",
    f"--workpath={spec_dir}/build",
    f"--specpath={spec_dir}",
])