import math
from typing import Dict, Optional, Tuple

SQRT_2 = math.sqrt(2)
TWO_PI = 2 * math.pi
PI_OVER_2 = math.pi / 2

def calculate_derived_reactance_params(
    component_val: Optional[float],
    reactance_val: Optional[float],
    omega: Optional[float],
    param_type: str  # 'L' or 'C'
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Calculate missing reactance-related parameter for RL or RC circuits.

    Given two of component value, reactance magnitude, or angular frequency,
    derive the third while performing basic consistency checks.
    """
    if component_val is not None and component_val < 0:
        raise ValueError(f"{param_type} cannot be negative.")
    if reactance_val is not None and reactance_val < 0:
        raise ValueError(f"Reactance magnitude (X_{param_type}) cannot be negative.")
    if omega is not None and omega < 0:
        raise ValueError("Angular frequency (omega) cannot be negative.")
    if param_type == 'C' and component_val is not None and component_val <= 0:
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
                derived_reactance = 0.0 if param_type == 'L' else float('inf')
            elif param_type == 'L':
                derived_reactance = omega * component_val
            else:
                if component_val == 0:
                    raise ValueError("Capacitance cannot be zero.")
                derived_reactance = 1.0 / (omega * component_val)

        elif omega is not None and reactance_val is not None and component_val is None:
            if omega == 0:
                if param_type == 'L':
                    if reactance_val == 0:
                        derived_component = None
                    else:
                        raise ValueError("Inconsistency: X_L must be 0 if frequency is 0 Hz.")
                else:
                    raise ValueError(
                        f"Cannot determine C from X_C ({reactance_val} Ω) if frequency is 0 Hz."
                    )
            elif param_type == 'L':
                if omega == 0:
                    raise ValueError("Cannot determine L if frequency is 0 Hz (unless X_L is also 0).")
                derived_component = reactance_val / omega
            else:
                if reactance_val == 0:
                    raise ValueError("Cannot determine C if X_C is 0.")
                if omega == 0:
                    raise ValueError("Cannot determine C if frequency is 0 Hz.")
                derived_component = 1.0 / (omega * reactance_val)

        elif component_val is not None and reactance_val is not None and omega is None:
            if param_type == 'L':
                if component_val == 0:
                    if reactance_val == 0:
                        derived_omega = None
                    else:
                        raise ValueError("Cannot calculate frequency from X_L if L is 0.")
                else:
                    derived_omega = reactance_val / component_val
            else:
                if component_val <= 0:
                    raise ValueError("Capacitance must be positive.")
                if reactance_val == 0:
                    raise ValueError(
                        "Cannot calculate frequency if X_C is 0 (implies infinite frequency or C=inf)."
                    )
                if reactance_val == float('inf'):
                    derived_omega = 0.0
                else:
                    derived_omega = 1.0 / (component_val * reactance_val)

    except ZeroDivisionError:
        raise ValueError("Calculation error: Division by zero occurred.")

    final_vals = (derived_component, derived_reactance, derived_omega)
    if all(x is not None for x in final_vals):
        c, r, w = final_vals
        expected_reactance = None
        if param_type == 'C' and (c is None or c <= 0):
            pass
        elif param_type == 'L' and c is None:
            pass
        elif w == 0:
            expected_reactance = 0.0 if param_type == 'L' else float('inf')
        elif param_type == 'L':
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
                consistent = math.isclose(r, expected_reactance, rel_tol=1e-6, abs_tol=1e-9)

            if not consistent:
                param_name = "X_L" if param_type == "L" else "X_C"
                comp_name = "L" if param_type == "L" else "C"
                r_str = f"{r:.4g}" if r != float('inf') else "Infinity"
                exp_str = (
                    f"{expected_reactance:.4g}" if expected_reactance != float('inf') else "Infinity"
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
    """Calculate parameters for a series RL or RC AC circuit."""
    if V_rms < 0:
        raise ValueError("V RMS must be non-negative.")
    if R < 0:
        raise ValueError("Resistance (R) must be non-negative.")
    if f is not None and f < 0:
        raise ValueError("Frequency (f) must be non-negative.")

    param_type = 'L' if circuit_type == 'RL' else 'C'
    omega = TWO_PI * f if f is not None else None

    try:
        final_comp, final_reactance, final_omega = calculate_derived_reactance_params(
            component_val, reactance_val, omega, param_type
        )
    except ValueError as e:
        raise ValueError(f"Parameter Derivation Error ({circuit_type}): {e}") from e

    is_dc_open_circuit = (circuit_type == 'RC' and final_reactance == float('inf'))
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

    is_rc = circuit_type == 'RC'
    if final_reactance is None:
        raise ValueError("Internal Error: Reactance could not be determined.")

    reactance_signed = final_reactance if not is_rc else -final_reactance

    if final_reactance == float('inf'):
        Z = float('inf')
        phi = -90.0
        I_rms = 0.0
        V_rms_R = 0.0
        V_rms_X = V_rms
    elif R == 0 and final_reactance == 0:
        Z = 0.0
        phi = 0.0
        if V_rms > 0:
            I_rms = float('inf')
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
            I_rms = float('inf') if V_rms > 0 else 0.0
        else:
            I_rms = V_rms / Z
        V_rms_R = I_rms * R if I_rms != float('inf') else (
            float('inf') if R > 0 and V_rms > 0 else 0.0
        )
        V_rms_X = I_rms * final_reactance if I_rms != float('inf') else (
            float('inf') if final_reactance > 0 and V_rms > 0 else 0.0
        )

    V_peak = V_rms * SQRT_2
    I_peak = I_rms * SQRT_2 if I_rms != float('inf') else float('inf')

    results = {
        'V_rms': V_rms,
        'R': R,
        'f': final_f,
        'omega': final_omega,
        param_type: final_comp,
        f'X_{param_type}': final_reactance,
        'X': final_reactance,
        'Z': Z,
        'phi': phi,
        'I_rms': I_rms,
        'I_peak': I_peak,
        'V_rms_R': V_rms_R,
        'V_rms_X': V_rms_X,
        'V_peak': V_peak,
        '_input_L': component_val if circuit_type == 'RL' else None,
        '_input_C': component_val if circuit_type == 'RC' else None,
        '_input_XL': reactance_val if circuit_type == 'RL' else None,
        '_input_XC': reactance_val if circuit_type == 'RC' else None,
        '_input_f': f,
    }
    return results
