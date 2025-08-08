import math
from typing import Dict, Optional, Tuple
import cmath

SQRT_2 = math.sqrt(2)
TWO_PI = 2 * math.pi
PI_OVER_2 = math.pi / 2


def calculate_derived_reactance_params(
    component_val: Optional[float],
    reactance_val: Optional[float],
    omega: Optional[float],
    param_type: str,  # 'L' or 'C'
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Derive the missing reactance parameter for RL or RC circuits.

    The routine implements the relationships :math:`X_L = ω L` and
    :math:`X_C = 1/(ω C)` to compute whichever quantity is absent from the
    input.  At least two of ``component_val``, ``reactance_val`` and ``omega``
    must be supplied.  The function performs extensive validation: negative
    numbers are rejected, zero and infinite reactances are handled explicitly
    (e.g. a capacitor at DC is treated as an open circuit), and all derived
    values are cross‑checked for internal consistency.

    Parameters
    ----------
    component_val : Optional[float]
        Inductance in henries for RL circuits or capacitance in farads for RC
        circuits.  ``None`` if the value is unknown and should be calculated.
    reactance_val : Optional[float]
        Magnitude of the reactance (``X_L`` or ``X_C``) in ohms.  ``None`` if
        unknown.
    omega : Optional[float]
        Angular frequency in radians per second.  ``None`` if unknown.
    param_type : str
        ``'L'`` to treat the component as an inductor or ``'C'`` for a
        capacitor.

    Returns
    -------
    Tuple[Optional[float], Optional[float], Optional[float]]
        A tuple ``(component_val, reactance_val, omega)`` with the missing
        element filled in whenever it can be determined.

    Raises
    ------
    ValueError
        If inputs are negative, mathematically inconsistent or would require a
        division by zero to compute.
    """
    if component_val is not None and component_val < 0:
        raise ValueError(f"{param_type} cannot be negative.")
    if reactance_val is not None and reactance_val < 0:
        raise ValueError(f"Reactance magnitude (X_{param_type}) cannot be negative.")
    if omega is not None and omega < 0:
        raise ValueError("Angular frequency (omega) cannot be negative.")
    if param_type == "C" and component_val is not None and component_val <= 0:
        raise ValueError("Capacitance (C) must be positive.")

    inputs_provided = sum(x is not None for x in [component_val, reactance_val, omega])
    if inputs_provided < 2:
        return component_val, reactance_val, omega

    derived_component = component_val
    derived_reactance = reactance_val
    derived_omega = omega

    try:
        if omega is not None and component_val is not None and reactance_val is None:
            if omega == 0:
                derived_reactance = 0.0 if param_type == "L" else float("inf")
            elif param_type == "L":
                derived_reactance = omega * component_val
            else:
                if component_val == 0:
                    raise ValueError("Capacitance cannot be zero.")
                derived_reactance = 1.0 / (omega * component_val)

        elif omega is not None and reactance_val is not None and component_val is None:
            if omega == 0:
                if param_type == "L":
                    if reactance_val == 0:
                        derived_component = None
                    else:
                        raise ValueError(
                            "Inconsistency: X_L must be 0 if frequency is 0 Hz."
                        )
                else:
                    raise ValueError(
                        f"Cannot determine C from X_C ({reactance_val} Ω) if frequency is 0 Hz."
                    )
            elif param_type == "L":
                if omega == 0:
                    raise ValueError(
                        "Cannot determine L if frequency is 0 Hz (unless X_L is also 0)."
                    )
                derived_component = reactance_val / omega
            else:
                if reactance_val == 0:
                    raise ValueError("Cannot determine C if X_C is 0.")
                if omega == 0:
                    raise ValueError("Cannot determine C if frequency is 0 Hz.")
                derived_component = 1.0 / (omega * reactance_val)

        elif component_val is not None and reactance_val is not None and omega is None:
            if param_type == "L":
                if component_val == 0:
                    if reactance_val == 0:
                        derived_omega = None
                    else:
                        raise ValueError(
                            "Cannot calculate frequency from X_L if L is 0."
                        )
                else:
                    derived_omega = reactance_val / component_val
            else:
                if component_val <= 0:
                    raise ValueError("Capacitance must be positive.")
                if reactance_val == 0:
                    raise ValueError(
                        "Cannot calculate frequency if X_C is 0 (implies infinite frequency or C=inf)."
                    )
                if reactance_val == float("inf"):
                    derived_omega = 0.0
                else:
                    derived_omega = 1.0 / (component_val * reactance_val)

    except ZeroDivisionError:
        raise ValueError("Calculation error: Division by zero occurred.")

    final_vals = (derived_component, derived_reactance, derived_omega)
    if all(x is not None for x in final_vals):
        c, r, w = final_vals
        expected_reactance = None
        if param_type == "C" and (c is None or c <= 0):
            pass
        elif param_type == "L" and c is None:
            pass
        elif w == 0:
            expected_reactance = 0.0 if param_type == "L" else float("inf")
        elif param_type == "L":
            expected_reactance = w * c
        else:
            expected_reactance = 1.0 / (w * c)

        if expected_reactance is not None:
            r_is_finite = not math.isinf(r)
            exp_is_finite = not math.isinf(expected_reactance)

            if r_is_finite != exp_is_finite:
                consistent = False
            elif not r_is_finite:
                consistent = True
            else:
                consistent = math.isclose(
                    r, expected_reactance, rel_tol=1e-6, abs_tol=1e-9
                )

            if not consistent:
                param_name = "X_L" if param_type == "L" else "X_C"
                comp_name = "L" if param_type == "L" else "C"
                r_str = f"{r:.4g}" if r != float("inf") else "Infinity"
                exp_str = (
                    f"{expected_reactance:.4g}"
                    if expected_reactance != float("inf")
                    else "Infinity"
                )
                raise ValueError(
                    f"Inconsistent input: Provided/derived {param_name} ({r_str} Ω) "
                    f"does not match calculated value ({exp_str} Ω) from {comp_name} and frequency."
                )

    return derived_component, derived_reactance, derived_omega


def calculate_series_ac_circuit(
    V_rms: float,
    R: float,
    component_val: Optional[float],
    reactance_val: Optional[float],
    f: Optional[float],
    circuit_type: str,
) -> Dict[str, Optional[float]]:
    """Solve a series RL or RC circuit and return its key parameters.

    The function expects the RMS supply voltage and resistance together with
    any two of component value, reactance magnitude and frequency.  Missing
    values are derived by :func:`calculate_derived_reactance_params` using the
    appropriate reactance relationship for inductors or capacitors.  After the
    component parameters are resolved the routine computes impedance, phase
    angle, currents and voltage drops.  Numerous validation steps guard against
    negative inputs, inconsistent combinations and special cases such as a
    capacitor acting as an open circuit at DC.

    Parameters
    ----------
    V_rms : float
        Source voltage in volts RMS.
    R : float
        Resistance in ohms.
    component_val : Optional[float]
        Inductance (henries) for an RL circuit or capacitance (farads) for an
        RC circuit.
    reactance_val : Optional[float]
        Reactance magnitude ``X_L`` or ``X_C`` in ohms.
    f : Optional[float]
        Frequency in hertz.
    circuit_type : str
        ``'RL'`` for resistor–inductor circuits or ``'RC'`` for
        resistor–capacitor circuits.

    Returns
    -------
    Dict[str, Optional[float]]
        Mapping of calculated circuit attributes including impedance ``Z``,
        phase angle ``phi``, current and component voltages.  Inputs are echoed
        back alongside derived values.

    Raises
    ------
    ValueError
        If provided values are negative, insufficient to perform the
        calculation or mutually inconsistent.
    """
    if V_rms < 0:
        raise ValueError("V RMS must be non-negative.")
    if R < 0:
        raise ValueError("Resistance (R) must be non-negative.")
    if f is not None and f < 0:
        raise ValueError("Frequency (f) must be non-negative.")

    param_type = "L" if circuit_type == "RL" else "C"
    omega = TWO_PI * f if f is not None else None

    try:
        final_comp, final_reactance, final_omega = calculate_derived_reactance_params(
            component_val, reactance_val, omega, param_type
        )
    except ValueError as e:
        raise ValueError(f"Parameter Derivation Error ({circuit_type}): {e}") from e

    is_dc_open_circuit = circuit_type == "RC" and final_reactance == float("inf")
    if final_reactance is None or (final_omega is None and not is_dc_open_circuit):
        raise ValueError(
            f"Insufficient parameters for {circuit_type} circuit. "
            f"Need V_rms, R, and two of ({param_type}, X_{param_type}, f)."
        )

    if final_omega is not None:
        final_f = final_omega / TWO_PI
    elif is_dc_open_circuit:
        final_f = 0.0
        final_omega = 0.0
    else:
        final_f = None

    is_rc = circuit_type == "RC"
    if final_reactance is None:
        raise ValueError("Internal Error: Reactance could not be determined.")

    reactance_signed = final_reactance if not is_rc else -final_reactance

    if final_reactance == float("inf"):
        Z = float("inf")
        phi = -90.0
        I_rms = 0.0
        V_rms_R = 0.0
        V_rms_X = V_rms
    elif R == 0 and final_reactance == 0:
        Z = 0.0
        phi = 0.0
        if V_rms > 0:
            I_rms = float("inf")
            V_rms_R = 0.0
            V_rms_X = 0.0
        else:
            I_rms = 0.0
            V_rms_R = 0.0
            V_rms_X = 0.0
    else:
        Z = math.hypot(R, final_reactance)
        phi = math.degrees(math.atan2(reactance_signed, R))
        if Z == 0:
            I_rms = float("inf") if V_rms > 0 else 0.0
        else:
            I_rms = V_rms / Z
        V_rms_R = (
            I_rms * R
            if I_rms != float("inf")
            else (float("inf") if R > 0 and V_rms > 0 else 0.0)
        )
        V_rms_X = (
            I_rms * final_reactance
            if I_rms != float("inf")
            else (float("inf") if final_reactance > 0 and V_rms > 0 else 0.0)
        )

    V_peak = V_rms * SQRT_2
    I_peak = I_rms * SQRT_2 if I_rms != float("inf") else float("inf")

    results = {
        "V_rms": V_rms,
        "R": R,
        "f": final_f,
        "omega": final_omega,
        param_type: final_comp,
        f"X_{param_type}": final_reactance,
        "X": final_reactance,
        "Z": Z,
        "phi": phi,
        "I_rms": I_rms,
        "I_peak": I_peak,
        "V_rms_R": V_rms_R,
        "V_rms_X": V_rms_X,
        "V_peak": V_peak,
        "_input_L": component_val if circuit_type == "RL" else None,
        "_input_C": component_val if circuit_type == "RC" else None,
        "_input_XL": reactance_val if circuit_type == "RL" else None,
        "_input_XC": reactance_val if circuit_type == "RC" else None,
        "_input_f": f,
    }
    return results


def calculate_series_rlc_circuit(
    V_rms: float,
    R: float,
    L: float,
    C: float,
    f: float,
) -> Dict[str, float]:
    """Compute parameters for a series RLC circuit.

    Parameters
    ----------
    V_rms : float
        Source voltage in volts RMS.
    R : float
        Resistance in ohms.
    L : float
        Inductance in henries.
    C : float
        Capacitance in farads.
    f : float
        Frequency in hertz.
    """

    if any(x < 0 for x in [V_rms, R, L, C, f]):
        raise ValueError("All parameters must be non-negative.")
    if any(x <= 0 for x in [L, C, f]):
        raise ValueError(
            "Inductance, capacitance and frequency must be greater than zero for RLC analysis."
        )

    omega = TWO_PI * f
    X_L = omega * L
    X_C = 1.0 / (omega * C)
    X = X_L - X_C
    Z = math.hypot(R, X)
    phi = math.degrees(math.atan2(X, R))
    if Z == 0:
        I_rms = float("inf") if V_rms > 0 else 0.0
    else:
        I_rms = V_rms / Z
    V_rms_R = I_rms * R if I_rms != float("inf") else float("inf")
    V_rms_L = I_rms * X_L if I_rms != float("inf") else float("inf")
    V_rms_C = I_rms * X_C if I_rms != float("inf") else float("inf")
    V_peak = V_rms * SQRT_2
    I_peak = I_rms * SQRT_2 if I_rms != float("inf") else float("inf")

    return {
        "V_rms": V_rms,
        "R": R,
        "L": L,
        "C": C,
        "f": f,
        "omega": omega,
        "X_L": X_L,
        "X_C": X_C,
        "X": X,
        "Z": Z,
        "phi": phi,
        "I_rms": I_rms,
        "I_peak": I_peak,
        "V_rms_R": V_rms_R,
        "V_rms_L": V_rms_L,
        "V_rms_C": V_rms_C,
        "V_peak": V_peak,
    }


def calculate_parallel_rlc_circuit(
    V_rms: float,
    R: float,
    L: float,
    C: float,
    f: float,
) -> Dict[str, float]:
    """Compute parameters for a parallel RLC circuit."""

    if any(x < 0 for x in [V_rms, R, L, C, f]):
        raise ValueError("All parameters must be non-negative.")
    if any(x <= 0 for x in [L, C, f]):
        raise ValueError(
            "Inductance, capacitance and frequency must be greater than zero for RLC analysis."
        )

    omega = TWO_PI * f
    X_L = omega * L
    X_C = 1.0 / (omega * C)

    Z_R = complex(R, 0)
    Z_L = complex(0, X_L)
    Z_C = complex(0, -X_C)
    Y_total = 1 / Z_R + 1 / Z_L + 1 / Z_C
    if Y_total == 0:
        Z_total = complex(float("inf"))
    else:
        Z_total = 1 / Y_total
    Z = abs(Z_total)
    phi = math.degrees(cmath.phase(Z_total))

    if Z == 0:
        I_rms = float("inf") if V_rms > 0 else 0.0
    else:
        I_rms = V_rms / Z

    I_rms_R = V_rms / R if R != 0 else float("inf")
    I_rms_L = V_rms / X_L if X_L != 0 else float("inf")
    I_rms_C = V_rms / X_C if X_C != 0 else float("inf")
    V_peak = V_rms * SQRT_2
    I_peak = I_rms * SQRT_2 if I_rms != float("inf") else float("inf")

    return {
        "V_rms": V_rms,
        "R": R,
        "L": L,
        "C": C,
        "f": f,
        "omega": omega,
        "X_L": X_L,
        "X_C": X_C,
        "Z": Z,
        "phi": phi,
        "I_rms": I_rms,
        "I_peak": I_peak,
        "I_rms_R": I_rms_R,
        "I_rms_L": I_rms_L,
        "I_rms_C": I_rms_C,
        "V_peak": V_peak,
    }
