"""Application entry point for the GUI."""

import ttkbootstrap as ttkb
from rc_rl_calculator.gui.app import ACCircuitSolverApp


def main() -> None:
    """Launch the AC Circuit Solver GUI with a modern themed window."""
    root = ttkb.Window(themename="flatly")
    _app = ACCircuitSolverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
