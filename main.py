import logging
import tkinter as tk

from gui.app import ACCircuitSolverApp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Launch the AC Circuit Solver GUI."""
    logger.info("Starting ACCircuitSolverApp")
    root = tk.Tk()
    _app = ACCircuitSolverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
