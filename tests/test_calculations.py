import pytest

from rc_rl_calculator.core.calculations import (
    calculate_derived_reactance_params,
    calculate_series_ac_circuit,
    calculate_parallel_rlc_circuit,
    calculate_series_rlc_circuit,
    equivalent_capacitance,
    equivalent_inductance,
)


@pytest.fixture
def approx_cmp():
    def _approx(value, rel=1e-6, abs=1e-9):
        return pytest.approx(value, rel=rel, abs=abs)

    return _approx


@pytest.fixture
def expect_value_error():
    def _expect(func, *args, **kwargs):
        with pytest.raises(ValueError):
            func(*args, **kwargs)

    return _expect


# Tests for calculate_derived_reactance_params


def test_inductor_zero_frequency(approx_cmp):
    L, X, w = calculate_derived_reactance_params(2.0, None, 0.0, "L")
    assert L == approx_cmp(2.0)
    assert X == approx_cmp(0.0)
    assert w == approx_cmp(0.0)


def test_capacitor_zero_frequency():
    C, X, w = calculate_derived_reactance_params(1e-6, None, 0.0, "C")
    assert C == 1e-6
    assert X == float("inf")
    assert w == 0.0


def test_negative_component_raises(expect_value_error):
    expect_value_error(calculate_derived_reactance_params, -1.0, None, 1.0, "L")


def test_inconsistent_parameters_raises(expect_value_error):
    expect_value_error(calculate_derived_reactance_params, 1.0, 10.0, 1.0, "L")


# Tests for calculate_series_ac_circuit


def test_rc_open_circuit_dc(approx_cmp):
    result = calculate_series_ac_circuit(10.0, 100.0, 1e-6, None, 0.0, "RC")
    assert result["Z"] == float("inf")
    assert result["I_rms"] == approx_cmp(0.0)
    assert result["V_rms_X"] == approx_cmp(10.0)
    assert result["phi"] == approx_cmp(-90.0)


def test_rl_zero_impedance_high_current():
    result = calculate_series_ac_circuit(5.0, 0.0, 0.0, None, 60.0, "RL")
    assert result["Z"] == 0.0
    assert result["I_rms"] == float("inf")
    assert result["V_rms_R"] == 0.0
    assert result["V_rms_X"] == 0.0


def test_negative_voltage_raises(expect_value_error):
    expect_value_error(calculate_series_ac_circuit, -1.0, 10.0, None, None, 60.0, "RL")


def test_negative_frequency_raises(expect_value_error):
    expect_value_error(calculate_series_ac_circuit, 1.0, 10.0, None, None, -1.0, "RL")


def test_series_rlc_basic(approx_cmp):
    result = calculate_series_rlc_circuit(10.0, 10.0, 0.05, 1e-6, 1000.0)
    assert result["Z"] == approx_cmp(155.3266, rel=1e-4)
    assert result["phi"] == approx_cmp(86.3087, rel=1e-4)


def test_parallel_rlc_basic(approx_cmp):
    result = calculate_parallel_rlc_circuit(10.0, 100.0, 0.1, 10e-6, 1000.0)
    assert result["Z"] == approx_cmp(16.1157, rel=1e-4)
    assert result["phi"] == approx_cmp(-80.7259, rel=1e-4)


def test_parallel_rlc_zero_inductance_short():
    result = calculate_parallel_rlc_circuit(5.0, 10.0, 0.0, 1e-6, 1000.0)
    assert result["Z"] == 0.0
    assert result["I_rms"] == float("inf")
    assert result["I_rms_R"] == float("inf")
    assert result["I_rms_L"] == float("inf")
    assert result["I_rms_C"] == float("inf")


def test_parallel_rlc_zero_resistance_short():
    result = calculate_parallel_rlc_circuit(5.0, 0.0, 0.1, 1e-6, 1000.0)
    assert result["Z"] == 0.0
    assert result["I_rms"] == float("inf")
    assert result["I_rms_R"] == float("inf")
    assert result["I_rms_L"] == float("inf")
    assert result["I_rms_C"] == float("inf")


# Tests for equivalent capacitance and inductance


def test_equivalent_capacitance(approx_cmp):
    caps = [1e-6, 2e-6, 3e-6]
    assert equivalent_capacitance(caps, "parallel") == approx_cmp(6e-6)
    series_expected = 1 / (1 / 1e-6 + 1 / 2e-6 + 1 / 3e-6)
    assert equivalent_capacitance(caps, "series") == approx_cmp(series_expected)


def test_equivalent_inductance(approx_cmp):
    inds = [1e-3, 2e-3, 3e-3]
    assert equivalent_inductance(inds, "series") == approx_cmp(6e-3)
    parallel_expected = 1 / (1 / 1e-3 + 1 / 2e-3 + 1 / 3e-3)
    assert equivalent_inductance(inds, "parallel") == approx_cmp(parallel_expected)


def test_equivalent_capacitance_invalid(expect_value_error):
    expect_value_error(equivalent_capacitance, [1e-6, -2e-6], "series")


def test_equivalent_inductance_invalid(expect_value_error):
    expect_value_error(equivalent_inductance, [1e-3, -2e-3], "parallel")
