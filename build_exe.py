"""Build and run a standalone executable for the GUI using PyInstaller.

Run ``python build_exe.py`` to create ``rc_rl_calculator.exe`` in the
``dist`` directory and automatically launch it. A clear error message is
reported if the build fails or the executable cannot be found.

Requires the :mod:`pyinstaller` package.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Final

import PyInstaller.__main__


DIST_DIR: Final = Path("dist")
EXE_NAME: Final = "rc_rl_calculator.exe"


def build() -> Path:
    """Run PyInstaller and return the path to the built executable."""
    try:
        PyInstaller.__main__.run(
            [
                "src/rc_rl_calculator/main.py",
                "--name",
                "rc_rl_calculator",
                "--onefile",
                "--windowed",
            ]
        )
    except SystemExit as exc:  # pragma: no cover - exercised during manual runs
        code = exc.code if isinstance(exc.code, int) else 1
        raise RuntimeError(f"PyInstaller failed with exit code {code}") from None

    exe_path = DIST_DIR / EXE_NAME
    if not exe_path.is_file():
        raise FileNotFoundError(f"Expected executable not found: {exe_path}")

    return exe_path


def main() -> None:
    try:
        exe_path = build()
    except Exception as exc:  # pragma: no cover - exercised during manual runs
        print(f"Build failed: {exc}")
        raise SystemExit(1)

    print(f"Launching {exe_path}...")
    try:
        subprocess.run([str(exe_path)], check=True)  # pragma: no cover - manual
    except Exception as exc:  # pragma: no cover - manual execution only
        print(f"Failed to launch executable: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
