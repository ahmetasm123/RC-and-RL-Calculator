"""Example RC circuit configuration with waveform plot."""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).parent
sys.path.append(str(HERE.parent))
from core.calculations import calculate_series_ac_circuit  # noqa: E402


def main() -> None:
    with open(HERE / "rc_config.json") as f:
        cfg = json.load(f)

    result = calculate_series_ac_circuit(
        cfg["V_rms"],
        cfg["R"],
        cfg["C"],
        cfg.get("X"),
        cfg["f"],
        "RC",
    )
    print(result)

    omega = result["omega"]
    f_val = result["f"]
    phi_rad = math.radians(result["phi"])
    I_peak = result["I_peak"]
    V_peak = result["V_peak"]
    T = 1.0 / f_val

    t = np.linspace(0, 2 * T, 500)
    vs = V_peak * np.sin(omega * t)
    current = I_peak * np.sin(omega * t - phi_rad)

    plt.figure(figsize=(8, 4))
    plt.plot(t, vs, label="Source Voltage (V)")
    plt.plot(t, current, label="Circuit Current (A)")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.title("RC Circuit Waveforms")
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
