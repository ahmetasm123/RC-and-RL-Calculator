import tkinter as tk
from rc_rl_calculator.gui.app import ACCircuitSolverApp


def main() -> None:
    """Launch the AC Circuit Solver GUI."""
    root = tk.Tk()
    app = ACCircuitSolverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
