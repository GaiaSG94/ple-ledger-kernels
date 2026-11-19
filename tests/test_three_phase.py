import math

import pytest

from harness.kernels import run


def test_star_reference_case():
    # 400 V, 30 kW, pf 0.8 : S=37.5 kVA, Q=22.5 kvar, I_line=54.1266 A,
    # V_phase=230.94 V, I_phase=I_line.
    out = run("three-phase", {
        "V_LL": 400.0, "P_kW": 30.0, "pf": 0.8, "connection": "star",
    })
    assert out["S_kVA"] == pytest.approx(37.5)
    assert out["Q_kvar"] == pytest.approx(22.5)
    assert out["I_line_A"] == pytest.approx(54.12659, rel=1e-6)
    assert out["V_phase_V"] == pytest.approx(400.0 / math.sqrt(3.0))
    assert out["I_phase_A"] == pytest.approx(out["I_line_A"])


def test_delta_reference_case():
    out = run("three-phase", {
        "V_LL": 400.0, "P_kW": 30.0, "pf": 0.8, "connection": "delta",
    })
    assert out["V_phase_V"] == pytest.approx(400.0)
    assert out["I_phase_A"] == pytest.approx(54.12659 / math.sqrt(3.0), rel=1e-6)
    assert out["I_line_A"] == pytest.approx(math.sqrt(3.0) * out["I_phase_A"])


def test_unity_power_factor():
    out = run("three-phase", {"V_LL": 230.0, "P_kW": 10.0, "pf": 1.0})
    assert out["Q_kvar"] == pytest.approx(0.0)
    assert out["S_kVA"] == pytest.approx(10.0)
    assert out["connection"] == "star"


def test_domain_of_validity():
    with pytest.raises(ValueError):
        run("three-phase", {"V_LL": 400.0, "P_kW": 30.0, "pf": 1.2})
    with pytest.raises(ValueError):
        run("three-phase", {"V_LL": -400.0, "P_kW": 30.0, "pf": 0.9})
    with pytest.raises(ValueError):
        run("three-phase", {
            "V_LL": 400.0, "P_kW": 30.0, "pf": 0.9, "connection": "zigzag",
        })
