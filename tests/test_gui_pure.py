import math

import pytest

from rc_rl_calculator.gui.app import compute_waveform_data, compute_phasor_data


def test_compute_waveform_missing_params():
    params = {"f": 60.0}
    with pytest.raises(ValueError):
        compute_waveform_data(params, "RL")


def test_compute_waveform_open_circuit():
    params = {
        "omega": 2 * math.pi * 60,
        "phi": 0.0,
        "I_peak": 1.0,
        "V_peak": 1.0,
        "R": 10.0,
        "X": 5.0,
        "f": 60.0,
        "Z": float("inf"),
    }
    with pytest.raises(ValueError):
        compute_waveform_data(params, "RL")


def test_compute_waveform_invalid_omega():
    params = {
        "omega": 0.0,
        "phi": 0.0,
        "I_peak": 1.0,
        "V_peak": 1.0,
        "R": 10.0,
        "X": 5.0,
        "f": 60.0,
    }
    with pytest.raises(ValueError):
        compute_waveform_data(params, "RL")


def test_compute_phasor_missing_params():
    with pytest.raises(ValueError):
        compute_phasor_data({"f": 60.0}, "RL")


def test_compute_phasor_dc():
    params = {
        "V_rms": 10.0,
        "I_rms": 1.0,
        "V_rms_R": 5.0,
        "V_rms_X": 5.0,
        "phi": 0.0,
        "f": 0.0,
    }
    with pytest.raises(ValueError):
        compute_phasor_data(params, "RL")


def test_compute_phasor_open_circuit():
    params = {
        "V_rms": 10.0,
        "I_rms": 1.0,
        "V_rms_R": 5.0,
        "V_rms_X": 5.0,
        "phi": 0.0,
        "f": 60.0,
        "Z": float("inf"),
    }
    with pytest.raises(ValueError):
        compute_phasor_data(params, "RL")
