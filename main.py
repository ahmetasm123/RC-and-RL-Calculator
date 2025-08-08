import tkinter as tk
from gui.app import ACCircuitSolverApp


def main() -> None:
    """Launch the AC Circuit Solver GUI."""
    root = tk.Tk()
    _app = ACCircuitSolverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
