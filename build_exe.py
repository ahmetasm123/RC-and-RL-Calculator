"""Build and launch a standalone executable for the GUI using PyInstaller.

Run:
    python build_exe.py

Requires the 'pyinstaller' package. The resulting executable will be
located in the 'dist' directory and launched automatically.
"""

import os
import subprocess
from pathlib import Path

import PyInstaller.__main__


def build() -> Path:
    PyInstaller.__main__.run(
        [
            "src/rc_rl_calculator/main.py",
            "--name",
            "rc_rl_calculator",
            "--onefile",
            "--windowed",
        ]
    )
    exe = Path("dist") / (
        "rc_rl_calculator.exe" if os.name == "nt" else "rc_rl_calculator"
    )
    return exe


def main() -> None:
    exe = build()
    if exe.exists():
        subprocess.run([str(exe)])
    else:
        raise FileNotFoundError(f"Executable not found: {exe}")


if __name__ == "__main__":
    main()
