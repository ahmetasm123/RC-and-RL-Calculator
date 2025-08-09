"""Build standalone executables for the GUI using PyInstaller.

This module powers the ``create-installer`` console script. It can also be run
directly to build the executable and launch it immediately.

Requires the :mod:`pyinstaller` package.
"""

from __future__ import annotations

import subprocess
import platform
from pathlib import Path
from typing import Final

import PyInstaller.__main__


APP_NAME: Final = "rc_rl_calculator"
DEFAULT_DIST_DIR: Final = Path("dist")


def build(target: str | None = None, dist_path: Path | None = None) -> Path:
    """Run PyInstaller and return the path to the built executable.

    Parameters
    ----------
    target:
        Optional target platform (``"windows"``, ``"mac"`` or ``"linux"``). If
        ``None`` the current operating system is used.
    dist_path:
        Directory where the executable should be written. Defaults to
        :data:`DEFAULT_DIST_DIR`.
    """

    if target is None:
        system = platform.system().lower()
        if system.startswith("win"):
            target = "windows"
        elif system == "darwin":
            target = "mac"
        else:
            target = "linux"
    else:
        target = target.lower()

    dist_dir = dist_path or DEFAULT_DIST_DIR

    exe_name = APP_NAME
    if target == "windows":
        exe_name += ".exe"
    elif target == "mac":
        exe_name += ".app"

    try:
        PyInstaller.__main__.run(
            [
                "src/rc_rl_calculator/main.py",
                "--name",
                APP_NAME,
                "--onefile",
                "--windowed",
                "--distpath",
                str(dist_dir),
            ]
        )
    except SystemExit as exc:  # pragma: no cover - exercised during manual runs
        code = exc.code if isinstance(exc.code, int) else 1
        raise RuntimeError(f"PyInstaller failed with exit code {code}") from None

    exe_path = dist_dir / exe_name
    if not exe_path.is_file():
        raise FileNotFoundError(f"Expected executable not found: {exe_path}")

    return exe_path


def create_installer() -> None:
    """CLI entry point that builds an installer for the current platform."""
    try:
        exe_path = build()
    except Exception as exc:  # pragma: no cover - exercised during manual runs
        print(f"Build failed: {exc}")
        raise SystemExit(1)

    print(f"Installer written to {exe_path}")


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
