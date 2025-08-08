import math
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext  # Added scrolledtext
from typing import Dict, Optional, List
from ..core.calculations import calculate_series_ac_circuit, PI_OVER_2


# --- Unit Multipliers ---
# (Keep UNIT_FACTORS as before)
UNIT_FACTORS = {
    "V": {"V": 1, "mV": 1e-3, "kV": 1e3},
    "R": {"Ω": 1, "kΩ": 1e3, "MΩ": 1e6},
    "L": {"H": 1, "mH": 1e-3, "µH": 1e-6},
    "C": {"F": 1, "mF": 1e-3, "µF": 1e-6, "nF": 1e-9, "pF": 1e-12},
    "X": {"Ω": 1, "kΩ": 1e3, "MΩ": 1e6},  # Reactance units
    "f": {"Hz": 1, "kHz": 1e3, "MHz": 1e6},
    "GENERIC": {"": 1},
}


# --- Plotting ---
def plot_waveforms(params: Dict[str, Optional[float]], circuit_type: str):
    """
    Plot voltage and current waveforms for the given circuit parameters.
    (Implementation details omitted for brevity - assume it's the same as the previous working version)
    """
    # --- Check for necessary parameters ---
    required_keys_ac = ["omega", "phi", "I_peak", "V_peak", "R", "X", "f"]
    required_keys_dc = ["V_rms", "I_rms", "V_rms_R", "V_rms_X", "f"]

    is_dc = params.get("f") is not None and math.isclose(params["f"], 0)

    if is_dc:
        missing = [key for key in required_keys_dc if params.get(key) is None]
        if missing:
            raise ValueError(
                f'Missing required parameters for DC plotting: {", ".join(missing)}'
            )
    else:  # AC case
        missing = [key for key in required_keys_ac if params.get(key) is None]
        if missing:
            raise ValueError(
                f'Missing required parameters for AC plotting: {", ".join(missing)}'
            )
        if params.get("omega", 0) <= 0:  # Check omega specifically for AC
            raise ValueError(
                "Cannot plot AC waveform without a positive angular frequency (omega)."
            )

    phi_rad = math.radians(params["phi"])  # Phase angle of impedance Z
    I_peak = params["I_peak"]
    V_peak = params["V_peak"]
    R = params["R"]
    X = params["X"]  # Magnitude of reactance

    # --- Handle edge cases before plotting ---
    if params.get("Z") == float("inf"):
        messagebox.showinfo(
            "Plot Info",
            "Cannot plot waveforms for open circuit (infinite impedance, zero current).",
        )
        return
    if I_peak == float("inf"):
        messagebox.showinfo(
            "Plot Info", "Cannot plot waveforms for short circuit (infinite current)."
        )
        return
    if V_peak == 0 and I_peak == 0:
        messagebox.showinfo(
            "Plot Info", "Input voltage is zero, waveforms are all zero."
        )
        plt.figure(figsize=(10, 6))
        plt.axhline(0, color="black", linewidth=0.8)
        plt.title(f"{circuit_type} Circuit - Zero Input")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude (V or A)")
        plt.grid(True)
        plt.ylim(-1, 1)  # Set some minimal y-limits
        plt.show()
        return

    # --- Handle DC case (f=0) ---
    if is_dc:
        messagebox.showinfo(
            "Plot Info", "Plotting waveforms for DC (0 Hz). Showing constant values."
        )
        t = np.linspace(0, 1, 2)  # Simple time vector for DC plot
        # Use RMS values directly for DC representation
        v_s_val = params["V_rms"]
        i_val = params["I_rms"]
        vr_val = params["V_rms_R"]
        vx_val = params["V_rms_X"]

        plt.figure(figsize=(10, 6))
        plt.plot(
            t,
            np.full_like(t, v_s_val),
            label=f"Source Voltage = {v_s_val:.4g} V",
            marker=".",
        )
        plt.plot(
            t,
            np.full_like(t, i_val),
            label=f"Circuit Current = {i_val:.4g} A",
            marker=".",
        )
        plt.plot(
            t,
            np.full_like(t, vr_val),
            label=f"Voltage across R = {vr_val:.4g} V",
            marker=".",
        )
        comp_label = "L (Short)" if circuit_type == "RL" else "C (Open)"
        plt.plot(
            t,
            np.full_like(t, vx_val),
            label=f"Voltage across {comp_label} = {vx_val:.4g} V",
            marker=".",
        )

        plt.xlabel("Time (arbitrary)")
        plt.ylabel("Amplitude (V or A)")
        plt.title(f"{circuit_type} Circuit DC Conditions (f=0 Hz)")
        plt.legend()
        plt.grid(True)
        # Adjust y-limits to show values clearly
        all_vals = [
            v
            for v in [v_s_val, i_val, vr_val, vx_val]
            if v is not None and not math.isinf(v)
        ]
        min_val = min(all_vals + [0]) if all_vals else 0  # Include 0
        max_val = max(all_vals + [0]) if all_vals else 0.1  # Include 0
        margin = abs(max_val - min_val) * 0.1 + 0.1  # Add margin, ensure positive
        plt.ylim(min_val - margin, max_val + margin)
        plt.tight_layout()
        plt.show()
        return

    # --- AC Plotting ---
    omega = params["omega"]
    f_val = params["f"]
    T = 1.0 / f_val  # Period
    t = np.linspace(0, 2 * T, 500)  # Time vector for 2 cycles

    # Waveforms:
    v_s = V_peak * np.sin(omega * t)
    i = I_peak * np.sin(omega * t - phi_rad)
    v_R = R * i
    phase_shift_X_rel_current = PI_OVER_2 if circuit_type == "RL" else -PI_OVER_2
    v_X = X * I_peak * np.sin(omega * t - phi_rad + phase_shift_X_rel_current)

    # --- Create Plot ---
    try:
        plt.style.use("seaborn-v0_8-darkgrid")  # Use a pleasant style
    except OSError:
        print("Seaborn style not found, using default.")  # Fallback style
        plt.style.use("default")

    plt.figure(figsize=(10, 6))

    plt.plot(t, v_s, label="Source Voltage ($V_S$)", linewidth=1.5)
    plt.plot(t, i, label="Circuit Current ($I$)", linewidth=1.5, linestyle="--")
    plt.plot(t, v_R, label="Voltage across R ($V_R$)", linewidth=1.2)
    comp_label = "L" if circuit_type == "RL" else "C"
    plt.plot(
        t, v_X, label=f"Voltage across {comp_label} ($V_{comp_label}$)", linewidth=1.2
    )

    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude (V or A)")
    freq_str = f"{f_val:.4g}"
    plt.title(f"{circuit_type} Circuit Waveforms (f = {freq_str} Hz)")
    plt.legend(loc="best")
    plt.grid(True)
    plt.axhline(0, color="black", linewidth=0.5)
    plt.xlim(0, 2 * T)
    plt.tight_layout()
    plt.show()


def plot_phasors(params: Dict[str, Optional[float]], circuit_type: str):
    """
    Plots the phasor diagram for V_S, I, V_R, V_X.

    Args:
        params: Dictionary of calculated circuit parameters.
        circuit_type: 'RL' or 'RC'.

    Raises:
        ValueError: If essential parameters for plotting are missing or invalid.
    """
    # --- Check for necessary parameters ---
    required_keys = ["V_rms", "I_rms", "V_rms_R", "V_rms_X", "phi", "f"]
    missing = [key for key in required_keys if params.get(key) is None]
    if missing:
        raise ValueError(
            f'Missing required parameters for phasor plot: {", ".join(missing)}'
        )

    # Phasors are generally not meaningful for DC (f=0)
    f_val = params["f"]
    if f_val is not None and math.isclose(f_val, 0):
        messagebox.showinfo(
            "Phasor Plot Info",
            "Phasor diagrams are typically used for AC circuits (f > 0).",
        )
        return

    # Check for infinite impedance/current
    if params.get("Z") == float("inf") or params.get("I_rms") == float("inf"):
        messagebox.showinfo(
            "Phasor Plot Info", "Cannot plot phasors for open or short circuits."
        )
        return

    # --- Get Magnitudes and Angles ---
    v_s_mag = params["V_rms"]
    i_mag = params["I_rms"]
    v_r_mag = params["V_rms_R"]
    v_x_mag = params["V_rms_X"]
    phi_impedance_deg = params["phi"]  # Angle of Z (V leads I by this)

    # Angles (in degrees, relative to V_S which is at 0 degrees)
    v_s_angle_deg = 0.0
    i_angle_deg = -phi_impedance_deg  # Current lags V_S by phi
    v_r_angle_deg = i_angle_deg  # V_R is in phase with I
    # V_L leads I by 90 deg, V_C lags I by 90 deg
    v_x_angle_deg = i_angle_deg + 90.0 if circuit_type == "RL" else i_angle_deg - 90.0

    # Convert angles to radians for plotting functions
    v_s_angle_rad = math.radians(v_s_angle_deg)
    i_angle_rad = math.radians(i_angle_deg)
    v_r_angle_rad = math.radians(v_r_angle_deg)
    v_x_angle_rad = math.radians(v_x_angle_deg)

    # --- Prepare Plot ---
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_aspect("equal")  # Ensure angles look correct
    ax.grid(True)
    ax.set_title(f"{circuit_type} Circuit Phasor Diagram (RMS Values)")
    ax.set_xlabel("Real Axis")
    ax.set_ylabel("Imaginary Axis")

    # --- Plot Phasors using quiver ---
    # quiver(x_pos, y_pos, x_dir, y_dir, angles='xy', scale_units='xy', scale=1)
    phasors = {
        "V_S": (v_s_mag, v_s_angle_rad, "red", 2),
        "I": (i_mag, i_angle_rad, "blue", 1.5),
        "V_R": (v_r_mag, v_r_angle_rad, "green", 1.5),
        f"V_{circuit_type[1]}": (v_x_mag, v_x_angle_rad, "purple", 1.5),  # V_L or V_C
    }

    max_val = 0  # To scale plot limits

    for label, (mag, angle_rad, color, width) in phasors.items():
        if mag > max_val:
            max_val = mag
        # Calculate endpoint components
        x_end = mag * math.cos(angle_rad)
        y_end = mag * math.sin(angle_rad)
        # Plot arrow from origin
        ax.quiver(
            0,
            0,
            x_end,
            y_end,
            angles="xy",
            scale_units="xy",
            scale=1,
            color=color,
            width=0.005 * width,
            label=f"{label} ({mag:.3g})",
        )

        # Add text label near the arrowhead (optional)
        # label_pos_factor = 1.1
        # ax.text(x_end * label_pos_factor, y_end * label_pos_factor, label, color=color, ha='center', va='center')

    # --- Set Plot Limits ---
    limit = max_val * 1.3  # Add some padding
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.axvline(0, color="black", linewidth=0.5)

    ax.legend(loc="best")
    plt.tight_layout()
    plt.show()


# --- GUI Application Class ---
class ACCircuitSolverApp:
    """
    GUI application for solving and visualizing simple series AC circuits (RL and RC).
    """

    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("AC Circuit Solver")
        master.minsize(550, 700)  # Increased min size for new panel

        # --- Style ---
        style = ttk.Style()
        available_themes = style.theme_names()
        preferred_themes = ["clam", "alt", "vista", "xpnative"]
        for theme in preferred_themes:
            if theme in available_themes:
                try:
                    style.theme_use(theme)
                    break
                except tk.TclError:
                    print(f"Theme '{theme}' failed to load, trying next.")
                    style.theme_use("default")

        style.configure("TLabel", padding=3, font=("Segoe UI", 9))
        style.configure("TEntry", padding=(5, 3), font=("Segoe UI", 9))
        style.configure("TButton", padding=5, font=("Segoe UI", 9, "bold"))
        style.configure("TRadiobutton", padding=(0, 5), font=("Segoe UI", 9))
        style.configure("TCombobox", padding=3, font=("Segoe UI", 9))
        style.configure("StatusBar.TLabel", padding=3, font=("Segoe UI", 8))
        style.configure(
            "Header.TLabel", font=("Segoe UI", 10, "bold")
        )  # Style for headers

        # --- Main frame ---
        # Use pack for the main frame to fill window and allow expansion
        self.frame = ttk.Frame(master, padding="10 10 10 10")
        self.frame.pack(fill=tk.BOTH, expand=True)
        # Configure column weights inside the frame for responsiveness
        self.frame.columnconfigure(0, weight=1)  # Allow content to expand horizontally
        self.frame.columnconfigure(1, weight=0)
        self.frame.columnconfigure(2, weight=0)

        # --- Variables ---
        self.circuit_var = tk.StringVar(value="RL")
        self.calc_params: Dict[str, Optional[float]] = {}  # Store calculation results
        self.input_values: Dict[str, Optional[float]] = {}  # Store raw inputs used

        # --- Widgets ---
        self.widgets: Dict[str, Dict[str, ttk.Widget]] = {}  # Store input widgets
        self.rl_widgets_ref: List[ttk.Widget] = []
        self.rc_widgets_ref: List[ttk.Widget] = []
        self._create_widgets()
        self._toggle_fields()  # Set initial state

    def _create_widgets(self):
        """Creates and grids all the GUI widgets."""
        current_row = 0

        # --- Circuit Selection ---
        sel_frame = ttk.Frame(self.frame)
        sel_frame.grid(
            row=current_row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10)
        )
        ttk.Label(sel_frame, text="Circuit Type:", style="Header.TLabel").pack(
            side=tk.LEFT, padx=(0, 10)
        )
        rl_rb = ttk.Radiobutton(
            sel_frame,
            text="RL",
            variable=self.circuit_var,
            value="RL",
            command=self._toggle_fields,
        )
        rl_rb.pack(side=tk.LEFT, padx=5)
        rc_rb = ttk.Radiobutton(
            sel_frame,
            text="RC",
            variable=self.circuit_var,
            value="RC",
            command=self._toggle_fields,
        )
        rc_rb.pack(side=tk.LEFT, padx=5)
        current_row += 1

        # --- Input Fields ---
        input_labelframe = ttk.LabelFrame(
            self.frame, text=" Inputs (* Required, [Opt] Optional) ", padding=(10, 5)
        )
        input_labelframe.grid(
            row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5)
        )
        input_labelframe.columnconfigure(
            1, weight=1
        )  # Make entry column inside frame expand
        current_row += 1
        input_row_idx = 0

        # Create input rows using helper
        self.widgets["V"] = self._make_input_row(
            input_labelframe,
            input_row_idx,
            "V RMS",
            "V",
            list(UNIT_FACTORS["V"].keys()),
            is_optional=False,
        )
        input_row_idx += 1
        self.widgets["R"] = self._make_input_row(
            input_labelframe,
            input_row_idx,
            "R",
            "Ω",
            list(UNIT_FACTORS["R"].keys()),
            is_optional=False,
        )
        input_row_idx += 1
        self.widgets["f"] = self._make_input_row(
            input_labelframe,
            input_row_idx,
            "Freq",
            "Hz",
            list(UNIT_FACTORS["f"].keys()),
            is_optional=True,
        )
        input_row_idx += 1
        self.widgets["L"] = self._make_input_row(
            input_labelframe,
            input_row_idx,
            "L",
            "mH",
            list(UNIT_FACTORS["L"].keys()),
            is_optional=True,
        )
        self.rl_widgets_ref.extend(self.widgets["L"].values())
        input_row_idx += 1
        self.widgets["XL"] = self._make_input_row(
            input_labelframe,
            input_row_idx,
            "X\u2097",
            "Ω",
            list(UNIT_FACTORS["X"].keys()),
            is_optional=True,
        )
        self.rl_widgets_ref.extend(self.widgets["XL"].values())
        input_row_idx += 1
        self.widgets["C"] = self._make_input_row(
            input_labelframe,
            input_row_idx,
            "C",
            "µF",
            list(UNIT_FACTORS["C"].keys()),
            is_optional=True,
        )
        self.rc_widgets_ref.extend(self.widgets["C"].values())
        input_row_idx += 1
        self.widgets["XC"] = self._make_input_row(
            input_labelframe,
            input_row_idx,
            "X\u1d9c",
            "Ω",
            list(UNIT_FACTORS["X"].keys()),
            is_optional=True,
        )
        self.rc_widgets_ref.extend(self.widgets["XC"].values())

        # --- Buttons ---
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=current_row, column=0, columnspan=3, pady=10)
        current_row += 1

        self.btn_solve = ttk.Button(
            button_frame, text="Solve", command=self.solve, width=10
        )
        self.btn_solve.grid(row=0, column=0, padx=5)
        self.btn_clear = ttk.Button(
            button_frame, text="Clear", command=self.clear_inputs, width=10
        )
        self.btn_clear.grid(row=0, column=1, padx=5)
        self.btn_plot_wave = ttk.Button(
            button_frame,
            text="Plot Waveforms",
            command=self.plot_waveforms_action,
            state=tk.DISABLED,
            width=15,
        )
        self.btn_plot_wave.grid(row=0, column=2, padx=5)
        # NEW Phasor Plot Button
        self.btn_plot_phasor = ttk.Button(
            button_frame,
            text="Plot Phasors",
            command=self.plot_phasors_action,
            state=tk.DISABLED,
            width=15,
        )
        self.btn_plot_phasor.grid(row=0, column=3, padx=5)

        # --- Paned Window for Results and Calculation Steps ---
        # This allows resizing the split between the two areas
        paned_window = ttk.PanedWindow(self.frame, orient=tk.VERTICAL)
        paned_window.grid(
            row=current_row,
            column=0,
            columnspan=3,
            sticky=(tk.W, tk.E, tk.N, tk.S),
            pady=(5, 5),
        )
        self.frame.rowconfigure(current_row, weight=1)  # Make paned window expand
        current_row += 1

        # --- Results Area (Top Pane) ---
        results_frame = ttk.LabelFrame(paned_window, text=" Results ", padding=(10, 5))
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        paned_window.add(results_frame, weight=1)  # Add to paned window

        self.text_output = scrolledtext.ScrolledText(
            results_frame,
            width=60,
            height=10,
            wrap=tk.WORD,
            relief=tk.SUNKEN,
            borderwidth=1,
            font=("Consolas", 9),
            state=tk.DISABLED,
        )
        self.text_output.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # --- Calculation Steps Area (Bottom Pane) ---
        steps_frame = ttk.LabelFrame(
            paned_window, text=" Calculation Steps ", padding=(10, 5)
        )
        steps_frame.rowconfigure(0, weight=1)
        steps_frame.columnconfigure(0, weight=1)
        paned_window.add(steps_frame, weight=1)  # Add to paned window

        self.text_calc_steps = scrolledtext.ScrolledText(
            steps_frame,
            width=60,
            height=8,
            wrap=tk.WORD,
            relief=tk.SUNKEN,
            borderwidth=1,
            font=("Consolas", 9),
            state=tk.DISABLED,
        )
        self.text_calc_steps.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # --- Status Bar ---
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            self.frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            style="StatusBar.TLabel",
        )
        status_bar.grid(
            row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0)
        )

    # --- Helper Methods (_make_input_row, _get_input_value, _toggle_fields, clear_inputs) ---
    # (Assume these are the same as the previous working version, with minor adjustments if needed)
    def _make_input_row(
        self,
        parent_frame: ttk.Widget,
        row: int,
        label_text: str,
        default_unit: str,
        units: list,
        is_optional: bool = False,
    ) -> Dict[str, ttk.Widget]:
        """Helper to create a Label, Entry, and Unit Combobox row within the parent_frame."""
        required_marker = "[Opt]" if is_optional else "*:"
        full_label = f"{label_text} {required_marker}"
        label_widget = ttk.Label(parent_frame, text=full_label, width=15, anchor=tk.E)
        label_widget.grid(row=row, column=0, sticky=tk.E, padx=(0, 5), pady=2)

        entry_widget = ttk.Entry(parent_frame)
        entry_widget.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)

        unit_combo = ttk.Combobox(
            parent_frame, values=units, width=5, state="readonly", justify="left"
        )
        if default_unit in units:
            unit_combo.set(default_unit)
        elif units:
            unit_combo.set(units[0])
        unit_combo.grid(row=row, column=2, sticky=tk.W, padx=(5, 0), pady=2)

        return {"label": label_widget, "entry": entry_widget, "unit": unit_combo}

    def _get_input_value(
        self, widget_key: str, component_type_key: str
    ) -> Optional[float]:
        """Gets numeric value from entry, applying unit factor."""
        if widget_key not in self.widgets:
            raise ValueError(f"Internal Error: Widget key '{widget_key}' not found.")

        input_widgets = self.widgets[widget_key]
        entry_widget = input_widgets.get("entry")
        unit_widget = input_widgets.get("unit")
        label_widget = input_widgets.get("label")

        if not all([entry_widget, unit_widget, label_widget]):
            raise ValueError(
                f"Internal Error: Missing widget components for '{widget_key}'."
            )

        try:
            full_label_text = label_widget.cget("text")
            label_text = full_label_text.split(" ")[0]
        except Exception:
            label_text = widget_key

        val_str = entry_widget.get().strip()
        if not val_str:
            # Store None for empty optional inputs
            is_optional = "[Opt]" in full_label_text
            if is_optional:
                self.input_values[widget_key] = None  # Store that it was empty
                return None
            else:
                raise ValueError(f"Input for '{label_text}'* is required.")

        try:
            value = float(val_str.replace(",", "."))
            # Store the base value entered by user before unit conversion
            self.input_values[widget_key] = value
        except ValueError:
            raise ValueError(
                f"Invalid numeric input for '{label_text}'. Please enter a number (e.g., 10.5 or 1.5e3)."
            ) from None

        try:
            unit = unit_widget.get()
            self.input_values[f"{widget_key}_unit"] = unit  # Store unit used
            if (
                component_type_key not in UNIT_FACTORS
                or unit not in UNIT_FACTORS[component_type_key]
            ):
                raise ValueError(f"Invalid unit '{unit}' selected for '{label_text}'.")
            factor = UNIT_FACTORS[component_type_key][unit]
            result_value = value * factor
            # Store value *after* unit conversion for calculation function
            self.input_values[f"{widget_key}_si"] = result_value
            return result_value
        except KeyError:
            raise ValueError(
                f"Invalid unit '{unit}' or component type '{component_type_key}' lookup."
            )

    def _toggle_fields(self, *args):
        """Enable/disable L/XL or C/XC fields based on circuit type selection."""
        is_rl = self.circuit_var.get() == "RL"
        rl_state = tk.NORMAL if is_rl else tk.DISABLED
        rc_state = tk.DISABLED if is_rl else tk.NORMAL

        for widget in self.rl_widgets_ref:
            if isinstance(widget, (ttk.Entry, ttk.Combobox)):
                widget.config(state=rl_state)
        for widget in self.rc_widgets_ref:
            if isinstance(widget, (ttk.Entry, ttk.Combobox)):
                widget.config(state=rc_state)

        if not is_rl:
            if "L" in self.widgets:
                self.widgets["L"]["entry"].delete(0, tk.END)
            if "XL" in self.widgets:
                self.widgets["XL"]["entry"].delete(0, tk.END)
        else:
            if "C" in self.widgets:
                self.widgets["C"]["entry"].delete(0, tk.END)
            if "XC" in self.widgets:
                self.widgets["XC"]["entry"].delete(0, tk.END)

        # Reset results, steps, and plot buttons when type changes
        self.text_output.config(state=tk.NORMAL)
        self.text_output.delete("1.0", tk.END)
        self.text_output.config(state=tk.DISABLED)
        self.text_calc_steps.config(state=tk.NORMAL)
        self.text_calc_steps.delete("1.0", tk.END)
        self.text_calc_steps.config(state=tk.DISABLED)
        self.btn_plot_wave.config(state=tk.DISABLED)
        self.btn_plot_phasor.config(state=tk.DISABLED)
        self.calc_params = {}
        self.input_values = {}
        self.status_var.set(f"{self.circuit_var.get()} mode selected. Ready.")

    def clear_inputs(self):
        """Clears all input fields, results, and steps."""
        for key in self.widgets:
            if "entry" in self.widgets[key]:
                self.widgets[key]["entry"].delete(0, tk.END)

        self.text_output.config(state=tk.NORMAL)
        self.text_output.delete("1.0", tk.END)
        self.text_output.config(state=tk.DISABLED)
        self.text_calc_steps.config(state=tk.NORMAL)
        self.text_calc_steps.delete("1.0", tk.END)
        self.text_calc_steps.config(state=tk.DISABLED)
        self.btn_plot_wave.config(state=tk.DISABLED)
        self.btn_plot_phasor.config(state=tk.DISABLED)
        self.calc_params = {}
        self.input_values = {}
        self.status_var.set("Inputs Cleared. Ready.")
        if "V" in self.widgets and "entry" in self.widgets["V"]:
            self.widgets["V"]["entry"].focus()

    # --- Calculation Steps Display ---
    def _display_calculation_steps(self):
        """Formats and displays the calculation steps."""
        self.text_calc_steps.config(state=tk.NORMAL)
        self.text_calc_steps.delete("1.0", tk.END)

        steps = []
        p = self.calc_params  # Shorthand
        inp = self.input_values  # Shorthand for SI values
        circuit_type = self.circuit_var.get()
        comp_char = circuit_type[1]  # 'L' or 'C'
        react_char = f"X_{comp_char}"  # 'X_L' or 'X_C'

        def fmt(val, precision="4g"):
            """Helper to format numbers for display, handling None and inf."""
            if val is None:
                return "?"
            if math.isinf(val):
                return "Infinity"
            return f"{val:.{precision}}"

        steps.append("--- Inputs (SI Units) ---")
        steps.append(f"V_rms = {fmt(inp.get('V_si'))} V")
        steps.append(f"R = {fmt(inp.get('R_si'))} Ω")
        f_in = inp.get("f_si")
        steps.append(f"f = {fmt(f_in) if f_in is not None else 'Not Provided'} Hz")
        if circuit_type == "RL":
            l_in = inp.get("L_si")
            xl_in = inp.get("XL_si")
            steps.append(f"L = {fmt(l_in) if l_in is not None else 'Not Provided'} H")
            steps.append(
                f"X_L = {fmt(xl_in) if xl_in is not None else 'Not Provided'} Ω"
            )
        else:
            c_in = inp.get("C_si")
            xc_in = inp.get("XC_si")
            steps.append(
                f"C = {fmt(c_in, '4e') if c_in is not None else 'Not Provided'} F"
            )  # Use scientific for C
            steps.append(
                f"X_C = {fmt(xc_in) if xc_in is not None else 'Not Provided'} Ω"
            )

        steps.append("\n--- Calculations ---")

        # 1. Angular Frequency (if f provided or calculated)
        omega_val = p.get("omega")
        f_val = p.get("f")
        if omega_val is not None:
            if f_in is not None:  # Calculated from input f
                steps.append(f"ω = 2π * f = 2π * {fmt(f_in)} = {fmt(omega_val)} rad/s")
            elif f_val is not None:  # f was derived
                steps.append(
                    f"ω = 2π * f (derived) = 2π * {fmt(f_val)} = {fmt(omega_val)} rad/s"
                )
            else:  # Omega derived directly?
                steps.append(f"ω (derived) = {fmt(omega_val)} rad/s")
        elif f_val == 0:
            steps.append("ω = 0 rad/s (DC)")
        else:
            steps.append("ω = ? (Could not determine)")

        # 2. Reactance (if not provided or needs consistency check)
        react_val = p.get(react_char)
        if react_val is not None:
            if circuit_type == "RL":
                l_val = p.get("L")
                if xl_in is None and omega_val is not None and l_val is not None:
                    steps.append(
                        f"X_L = ω * L = {fmt(omega_val)} * {fmt(l_val)} = {fmt(react_val)} Ω"
                    )
                elif l_in is None and omega_val is not None and react_val is not None:
                    steps.append(
                        f"L = X_L / ω = {fmt(react_val)} / {fmt(omega_val)} = {fmt(l_val)} H"
                    )
                elif f_in is None and l_val is not None and react_val is not None:
                    if l_val != 0:
                        steps.append(
                            f"ω = X_L / L = {fmt(react_val)} / {fmt(l_val)} = {fmt(omega_val)} rad/s"
                        )
                        steps.append(
                            f"f = ω / 2π = {fmt(omega_val)} / 2π = {fmt(f_val)} Hz"
                        )
                    else:
                        steps.append("Cannot derive f from X_L if L=0")
                else:  # XL was input or derived in complex way
                    steps.append(f"X_L (final) = {fmt(react_val)} Ω")
            else:  # RC
                c_val = p.get("C")
                if xc_in is None and omega_val is not None and c_val is not None:
                    if omega_val != 0 and c_val != 0:
                        steps.append(
                            f"X_C = 1 / (ω * C) = 1 / ({fmt(omega_val)} * {fmt(c_val, '4e')}) = {fmt(react_val)} Ω"
                        )
                    elif omega_val == 0:
                        steps.append("X_C = Infinity (DC open circuit)")
                    else:
                        steps.append("Cannot calculate X_C if C or ω is zero")
                elif c_in is None and omega_val is not None and react_val is not None:
                    if omega_val != 0 and react_val != 0 and not math.isinf(react_val):
                        steps.append(
                            f"C = 1 / (ω * X_C) = 1 / ({fmt(omega_val)} * {fmt(react_val)}) = {fmt(c_val, '4e')} F"
                        )
                    else:
                        steps.append("Cannot derive C if ω=0 or X_C=0 or X_C=inf")
                elif f_in is None and c_val is not None and react_val is not None:
                    if c_val != 0 and react_val != 0 and not math.isinf(react_val):
                        steps.append(
                            f"ω = 1 / (C * X_C) = 1 / ({fmt(c_val, '4e')} * {fmt(react_val)}) = {fmt(omega_val)} rad/s"
                        )
                        steps.append(
                            f"f = ω / 2π = {fmt(omega_val)} / 2π = {fmt(f_val)} Hz"
                        )
                    elif react_val == float("inf"):
                        steps.append("f = 0 Hz (from X_C = Infinity)")
                    else:
                        steps.append("Cannot derive f if C=0 or X_C=0")
                else:  # XC was input or derived in complex way
                    steps.append(f"X_C (final) = {fmt(react_val)} Ω")
        else:
            steps.append(f"{react_char} = ? (Could not determine)")

        # 3. Impedance
        Z_val = p.get("Z")
        R_val = p.get("R")
        X_val = p.get("X")  # Generic reactance magnitude
        phi_val = p.get("phi")
        if Z_val is not None and R_val is not None and X_val is not None:
            if Z_val == float("inf"):
                steps.append("Z = Infinity (Open circuit)")
            else:
                steps.append(
                    f"Z = sqrt(R² + X²) = sqrt({fmt(R_val)}² + {fmt(X_val)}²) = {fmt(Z_val)} Ω"
                )
                # 4. Phase Angle
                if phi_val is not None:
                    react_signed = X_val if circuit_type == "RL" else -X_val
                    steps.append(
                        f"φ = atan2(X_signed, R) = atan2({fmt(react_signed)}, {fmt(R_val)}) = {fmt(math.radians(phi_val), '4f')} rad"
                    )
                    steps.append(f"  = {fmt(phi_val, '4f')}°")
                else:
                    steps.append("φ = ?")
        else:
            steps.append("Z = ?")
            steps.append("φ = ?")

        # 5. Current
        I_rms_val = p.get("I_rms")
        V_rms_val = p.get("V_rms")
        if I_rms_val is not None and V_rms_val is not None and Z_val is not None:
            if Z_val == float("inf"):
                steps.append("I_rms = V_rms / Z = V_rms / Infinity = 0 A")
            elif Z_val == 0:
                steps.append(
                    f"I_rms = V_rms / Z = {fmt(V_rms_val)} / 0 = Infinity A (Short circuit)"
                )
            else:
                steps.append(
                    f"I_rms = V_rms / Z = {fmt(V_rms_val)} / {fmt(Z_val)} = {fmt(I_rms_val)} A"
                )
        else:
            steps.append("I_rms = ?")

        # 6. Component Voltages
        VR_rms_val = p.get("V_rms_R")
        VX_rms_val = p.get("V_rms_X")
        if VR_rms_val is not None and I_rms_val is not None and R_val is not None:
            if I_rms_val == float("inf"):
                steps.append(
                    f"V_R_rms = I_rms * R = Infinity * {fmt(R_val)} = {'Infinity' if R_val > 0 else '0'} V"
                )
            else:
                steps.append(
                    f"V_R_rms = I_rms * R = {fmt(I_rms_val)} * {fmt(R_val)} = {fmt(VR_rms_val)} V"
                )
        else:
            steps.append("V_R_rms = ?")

        if VX_rms_val is not None and I_rms_val is not None and X_val is not None:
            if I_rms_val == float("inf"):
                steps.append(
                    f"V_X_rms = I_rms * X = Infinity * {fmt(X_val)} = {'Infinity' if X_val > 0 else '0'} V"
                )
            else:
                steps.append(
                    f"V_X_rms = I_rms * X = {fmt(I_rms_val)} * {fmt(X_val)} = {fmt(VX_rms_val)} V"
                )
        else:
            steps.append("V_X_rms = ?")

        # 7. Verification Check (Optional but good)
        if (
            V_rms_val is not None
            and VR_rms_val is not None
            and VX_rms_val is not None
            and not math.isinf(V_rms_val)
            and not math.isinf(VR_rms_val)
            and not math.isinf(VX_rms_val)
        ):
            check_val = math.hypot(VR_rms_val, VX_rms_val)
            steps.append("\n--- Verification ---")
            steps.append(
                f"Check: sqrt(V_R² + V_X²) = sqrt({fmt(VR_rms_val)}² + {fmt(VX_rms_val)}²)"
            )
            steps.append(f"  = {fmt(check_val)} V")
            steps.append(f"Compare with V_rms = {fmt(V_rms_val)} V")
            if not math.isclose(V_rms_val, check_val, rel_tol=1e-5):
                steps.append("  (Note: Slight discrepancy may occur due to rounding)")

        # Insert steps into the text widget
        self.text_calc_steps.insert(tk.END, "\n".join(steps))
        self.text_calc_steps.config(state=tk.DISABLED)  # Make read-only

    # --- Solve Method ---
    def solve(self):
        """Gather inputs, call calculation function, display results and steps."""
        # Reset outputs
        self.text_output.config(state=tk.NORMAL)
        self.text_output.delete("1.0", tk.END)
        self.text_calc_steps.config(state=tk.NORMAL)
        self.text_calc_steps.delete("1.0", tk.END)
        self.btn_plot_wave.config(state=tk.DISABLED)
        self.btn_plot_phasor.config(state=tk.DISABLED)
        self.calc_params = {}
        self.input_values = {}  # Clear previous raw inputs
        self.status_var.set("Calculating...")
        self.master.update_idletasks()

        try:
            # --- Get Inputs (also stores raw values in self.input_values) ---
            V_rms = self._get_input_value("V", "V")
            R = self._get_input_value("R", "R")
            f = self._get_input_value("f", "f")
            L = self._get_input_value("L", "L")
            X_L = self._get_input_value("XL", "X")
            C = self._get_input_value("C", "C")
            X_C = self._get_input_value("XC", "X")

            # Basic validation already done in _get_input_value for required fields

            # --- Perform Calculation ---
            circuit_type = self.circuit_var.get()
            if circuit_type == "RL":
                self.calc_params = calculate_series_ac_circuit(
                    V_rms, R, L, X_L, f, "RL"
                )
            else:  # RC
                self.calc_params = calculate_series_ac_circuit(
                    V_rms, R, C, X_C, f, "RC"
                )

        except ValueError as e:
            messagebox.showerror("Input / Calculation Error", str(e))
            self.status_var.set("Error! See message.")
            self.text_output.config(state=tk.DISABLED)
            self.text_calc_steps.config(state=tk.DISABLED)
            return
        except Exception as e:
            messagebox.showerror(
                "Unexpected Error",
                f"An unexpected error occurred:\n{type(e).__name__}: {e}",
            )
            self.status_var.set("Unexpected Error!")
            self.text_output.config(state=tk.DISABLED)
            self.text_calc_steps.config(state=tk.DISABLED)
            import traceback

            print("--- UNEXPECTED ERROR ---")
            traceback.print_exc()
            print("------------------------")
            return

        # --- Display Results ---
        self.status_var.set("Calculation Complete.")
        self.text_output.insert(tk.END, f"--- {circuit_type} Circuit Results ---\n\n")
        # (Keep the result display logic from the previous version)
        display_map = [
            ("V_rms", "RMS Source Voltage (V\u209b)", "V"),
            ("R", "Resistance (R)", "Ω"),
            ("f", "Frequency (f)", "Hz"),
            ("L", "Inductance (L)", "H"),
            ("C", "Capacitance (C)", "F"),
            ("X_L", "Ind. Reactance (X\u2097)", "Ω"),
            ("X_C", "Cap. Reactance (X\u1d9c)", "Ω"),
            ("omega", "Angular Freq. (ω)", "rad/s"),
            ("Z", "Impedance Mag. (|Z|)", "Ω"),
            ("phi", "Impedance Phase (∠Z)", "°"),
            ("I_rms", "RMS Current (I)", "A"),
            ("I_peak", "Peak Current (I_pk)", "A"),
            ("V_peak", "Peak Source Voltage (V\u209b_pk)", "V"),
            ("V_rms_R", "RMS Voltage (V\u1d63)", "V"),
            ("V_rms_X", "RMS Voltage (V\u2093)", "V"),
        ]
        results_text = ""
        for key, label, unit in display_map:
            is_rl_key = key in ["L", "X_L"]
            is_rc_key = key in ["C", "X_C"]
            if circuit_type == "RL" and is_rc_key:
                continue
            if circuit_type == "RC" and is_rl_key:
                continue
            if key in self.calc_params and self.calc_params[key] is not None:
                value = self.calc_params[key]
                if isinstance(value, (int, float)):
                    if value == float("inf"):
                        formatted_value = "Infinity"
                    elif abs(value) > 1e7 or (abs(value) < 1e-4 and value != 0):
                        formatted_value = f"{value:.4e}"
                    else:
                        formatted_value = f"{value:.5g}"
                else:
                    formatted_value = str(value)
                display_label = label
                if key == "V_rms_X":
                    comp_sym = "\u2097" if circuit_type == "RL" else "\u1d9c"
                    display_label = f"RMS Voltage (V{comp_sym})"
                results_text += f"{display_label:<25}: {formatted_value} {unit}\n"
        if (
            self.calc_params.get("Z") is not None
            and self.calc_params.get("phi") is not None
        ):
            Z_val = self.calc_params["Z"]
            phi_val = self.calc_params["phi"]
            if Z_val == float("inf"):
                z_str = "Infinity"
            elif abs(Z_val) > 1e7 or (abs(Z_val) < 1e-4 and Z_val != 0):
                z_str = f"{Z_val:.4e}"
            else:
                z_str = f"{Z_val:.5g}"
            phi_str = f"{phi_val:.3f}"
            results_text += f"\n{'Impedance (Phasor Z)':<25}: {z_str} Ω ∠ {phi_str}°\n"
        self.text_output.insert(tk.END, results_text)
        self.text_output.config(state=tk.DISABLED)  # Make read-only

        # --- Display Calculation Steps ---
        self._display_calculation_steps()  # Call the new method

        # --- Enable Plot Buttons ---
        # Check conditions for enabling plot buttons
        f_val = self.calc_params.get("f")
        is_dc = f_val is not None and math.isclose(f_val, 0)
        is_ac = f_val is not None and f_val > 0
        no_inf = self.calc_params.get("Z") != float("inf") and self.calc_params.get(
            "I_rms"
        ) != float("inf")

        if no_inf and (
            is_ac or is_dc
        ):  # Waveforms can be plotted for AC or DC (if not open/short)
            self.btn_plot_wave.config(state=tk.NORMAL)
        else:
            self.btn_plot_wave.config(state=tk.DISABLED)

        if (
            no_inf and is_ac
        ):  # Phasors typically only plotted for AC (if not open/short)
            self.btn_plot_phasor.config(state=tk.NORMAL)
        else:
            self.btn_plot_phasor.config(state=tk.DISABLED)

        if (
            not no_inf and self.calc_params
        ):  # If calculation ran but resulted in open/short
            self.status_var.set("Calculation Complete (Open/Short Circuit).")

    # --- Plot Action Methods ---
    def plot_waveforms_action(self):
        """Calls the waveform plotting function."""
        if not self.calc_params or self.btn_plot_wave["state"] == tk.DISABLED:
            messagebox.showwarning(
                "Plot Error", "Cannot plot waveforms for the current results."
            )
            return
        try:
            self.status_var.set("Generating waveform plot...")
            self.master.update_idletasks()
            plot_waveforms(self.calc_params.copy(), self.circuit_var.get())
            self.status_var.set("Waveform Plotting Complete. Ready.")
        except ValueError as e:
            messagebox.showerror(
                "Plotting Error", f"Could not generate waveform plot:\n{e}"
            )
            self.status_var.set("Plotting Error!")
        except Exception as e:
            messagebox.showerror(
                "Plotting Error",
                f"Unexpected error during waveform plotting:\n{type(e).__name__}: {e}",
            )
            self.status_var.set("Plotting Error!")
            import traceback

            print("--- UNEXPECTED WAVE PLOT ERROR ---")
            traceback.print_exc()
            print("------------------------------")

    def plot_phasors_action(self):
        """Calls the phasor plotting function."""
        if not self.calc_params or self.btn_plot_phasor["state"] == tk.DISABLED:
            messagebox.showwarning(
                "Plot Error",
                "Cannot plot phasors for the current results (Requires AC, non-open/short).",
            )
            return
        try:
            self.status_var.set("Generating phasor plot...")
            self.master.update_idletasks()
            plot_phasors(self.calc_params.copy(), self.circuit_var.get())
            self.status_var.set("Phasor Plotting Complete. Ready.")
        except ValueError as e:
            messagebox.showerror(
                "Plotting Error", f"Could not generate phasor plot:\n{e}"
            )
            self.status_var.set("Plotting Error!")
        except Exception as e:
            messagebox.showerror(
                "Plotting Error",
                f"Unexpected error during phasor plotting:\n{type(e).__name__}: {e}",
            )
            self.status_var.set("Plotting Error!")
            import traceback

            print("--- UNEXPECTED PHASOR PLOT ERROR ---")
            traceback.print_exc()
            print("------------------------------")
