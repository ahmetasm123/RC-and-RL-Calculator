import os
import sys

import pytest

# Ensure the package root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rc_rl_calculator.cli import main
from rc_rl_calculator.core.calculations import calculate_series_ac_circuit


def parse_output(output: str) -> dict:
    """Convert CLI output into a dictionary of values."""
    result = {}
    for line in output.strip().splitlines():
        key, value = line.split(": ", 1)
        try:
            result[key] = float(value)
        except ValueError:
            result[key] = value
    return result


def test_cli_output_matches_calculation(capsys):
    argv = [
        "--voltage",
        "10",
        "--resistance",
        "100",
        "--component",
        "1e-6",
        "--frequency",
        "1000",
        "--circuit",
        "RC",
    ]
    main(argv)
    cli_result = parse_output(capsys.readouterr().out)

    expected = calculate_series_ac_circuit(10.0, 100.0, 1e-6, None, 1000.0, "RC")

    assert cli_result["Z"] == pytest.approx(expected["Z"])
    assert cli_result["I_rms"] == pytest.approx(expected["I_rms"])
    assert cli_result["phi"] == pytest.approx(expected["phi"])
