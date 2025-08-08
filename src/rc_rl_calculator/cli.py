"""Command line interface for the RC and RL calculator."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Iterable, Optional

from rc_rl_calculator.core.calculations import (
    calculate_parallel_rlc_circuit,
    calculate_series_ac_circuit,
    calculate_series_rlc_circuit,
)


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description=(
            "Solve series RL/RC or series/parallel RLC circuits given "
            "the necessary parameters."
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
        "--inductance",
        type=float,
        help="Inductance in henries for RLC circuits",
    )
    parser.add_argument(
        "--capacitance",
        type=float,
        help="Capacitance in farads for RLC circuits",
    )
    parser.add_argument(
        "--frequency",
        type=float,
        help="Frequency in hertz",
    )
    parser.add_argument(
        "--circuit",
        choices=["RL", "RC", "RLC_SERIES", "RLC_PARALLEL"],
        required=True,
        help="Circuit type to solve",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    return parser


def main(argv: Optional[Iterable[str]] = None) -> None:
    """Execute the CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.circuit in {"RL", "RC"}:
            result = calculate_series_ac_circuit(
                V_rms=args.voltage,
                R=args.resistance,
                component_val=args.component,
                reactance_val=args.reactance,
                f=args.frequency,
                circuit_type=args.circuit,
            )
        else:
            if (
                args.inductance is None
                or args.capacitance is None
                or args.frequency is None
            ):
                parser.error(
                    "--inductance, --capacitance and --frequency are required for RLC circuits"
                )
            if args.circuit == "RLC_SERIES":
                result = calculate_series_rlc_circuit(
                    V_rms=args.voltage,
                    R=args.resistance,
                    L=args.inductance,
                    C=args.capacitance,
                    f=args.frequency,
                )
            else:
                result = calculate_parallel_rlc_circuit(
                    V_rms=args.voltage,
                    R=args.resistance,
                    L=args.inductance,
                    C=args.capacitance,
                    f=args.frequency,
                )

        if args.json:
            print(json.dumps(result))
        else:
            for key, value in result.items():
                print(f"{key}: {value}")
    except ValueError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
