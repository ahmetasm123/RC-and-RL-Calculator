"""Command line interface for the RC and RL calculator."""

from __future__ import annotations

import argparse
from typing import Iterable, Optional

from rc_rl_calculator.core.calculations import calculate_series_ac_circuit


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description=(
            "Solve series RC or RL circuits given voltage, resistance and "
            "two of component value, reactance or frequency."
        )
    )
    parser.add_argument(
        "--voltage",
        type=float,
        required=True,
        help="Source voltage in volts RMS",
    )
    parser.add_argument(
        "--resistance",
        type=float,
        required=True,
        help="Resistance in ohms",
    )
    parser.add_argument(
        "--component",
        type=float,
        help="Inductance (H) for RL or capacitance (F) for RC",
    )
    parser.add_argument(
        "--reactance",
        type=float,
        help="Reactance magnitude in ohms",
    )
    parser.add_argument(
        "--frequency",
        type=float,
        help="Frequency in hertz",
    )
    parser.add_argument(
        "--circuit",
        choices=["RL", "RC"],
        required=True,
        help="Circuit type to solve",
    )
    return parser


def main(argv: Optional[Iterable[str]] = None) -> None:
    """Execute the CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    result = calculate_series_ac_circuit(
        V_rms=args.voltage,
        R=args.resistance,
        component_val=args.component,
        reactance_val=args.reactance,
        f=args.frequency,
        circuit_type=args.circuit,
    )

    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
