"""Example demonstrating core RC circuit calculation."""

from rc_rl_calculator.core.calculations import calculate_series_ac_circuit


def main() -> None:
    params = calculate_series_ac_circuit(
        V_rms=120.0,
        R=100.0,
        component_val=1e-6,
        reactance_val=None,
        f=60.0,
        circuit_type="RC",
    )
    for name, value in params.items():
        print(f"{name}: {value}")


if __name__ == "__main__":
    main()
