"""Build a standalone executable for the GUI using PyInstaller.

Run:
    python build_exe.py

Requires the 'pyinstaller' package. The resulting executable will be
located in the 'dist' directory.
"""

import PyInstaller.__main__


def build() -> None:
    PyInstaller.__main__.run(
        [
            "src/rc_rl_calculator/main.py",
            "--name",
            "rc_rl_calculator",
            "--onefile",
            "--windowed",
        ]
    )


if __name__ == "__main__":
    build()
