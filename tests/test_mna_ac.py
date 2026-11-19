import math

import pytest

from harness.kernels import run


def test_resistive_divider():
    # 10 V across 1k + 1k : V2 = 5 V, in phase, I = 5 mA.
    out = run("mna-ac", {
        "freq_hz": 50.0,
        "elements": [
            {"id": "V1", "type": "V", "a": 1, "b": 0, "value": 10.0},
            {"id": "R1", "type": "R", "a": 1, "b": 2, "value": 1.0, "unit": "kohm"},
            {"id": "R2", "type": "R", "a": 2, "b": 0, "value": 1.0, "unit": "kohm"},
        ],
    })
    assert out["probe_V"]["2"]["mag"] == pytest.approx(5.0)
    assert out["probe_V"]["2"]["phase_deg"] == pytest.approx(0.0)
    assert out["branches_A"]["R1"]["mag"] == pytest.approx(0.005, rel=1e-6)


def test_rc_lowpass_at_cutoff():
    # R=1k, C=1uF : fc = 1/(2*pi*R*C) = 159.155 Hz -> gain 1/sqrt(2), phase -45 deg.
    fc = 1.0 / (2.0 * math.pi * 1000.0 * 1e-6)
    out = run("mna-ac", {
        "freq_hz": fc,
        "elements": [
            {"id": "V1", "type": "V", "a": 1, "b": 0, "value": 1.0},
            {"id": "R1", "type": "R", "a": 1, "b": 2, "value": 1.0, "unit": "kohm"},
            {"id": "C1", "type": "C", "a": 2, "b": 0, "value": 1.0, "unit": "uF"},
        ],
        "probe_nodes": [2],
    })
    assert out["probe_V"]["2"]["mag"] == pytest.approx(1.0 / math.sqrt(2.0), rel=1e-6)
    assert out["probe_V"]["2"]["phase_deg"] == pytest.approx(-45.0, abs=1e-6)
    assert set(out["probe_V"]) == {"2"}


def test_series_rlc_resonance():
    # R=10, L=10 mH, C=1 uF : f0=1591.55 Hz, Q=10 -> I=1 A, V_C=100 V, V_R=10 V.
    f0 = 1.0 / (2.0 * math.pi * math.sqrt(0.01 * 1e-6))
    out = run("mna-ac", {
        "freq_hz": f0,
        "elements": [
            {"id": "V1", "type": "V", "a": 1, "b": 0, "value": 10.0},
            {"id": "R1", "type": "R", "a": 1, "b": 2, "value": 10.0},
            {"id": "L1", "type": "L", "a": 2, "b": 3, "value": 10.0, "unit": "mH"},
            {"id": "C1", "type": "C", "a": 3, "b": 0, "value": 1.0, "unit": "uF"},
        ],
    })
    assert out["branches_A"]["R1"]["mag"] == pytest.approx(1.0, rel=1e-6)
    assert out["sources_A"]["V1"]["mag"] == pytest.approx(1.0, rel=1e-6)
    assert out["nodes_V"]["2"]["mag"] == pytest.approx(0.0, abs=1e-6)
    assert out["nodes_V"]["3"]["mag"] == pytest.approx(100.0, rel=1e-6)


def test_current_source_and_ground():
    # 2 mA into 1k to ground : V = 2 V.
    out = run("mna-ac", {
        "freq_hz": 50.0,
        "elements": [
            {"id": "I1", "type": "I", "a": 1, "b": 0, "value": 0.002},
            {"id": "R1", "type": "R", "a": 1, "b": 0, "value": 1.0, "unit": "kohm"},
        ],
    })
    assert out["nodes_V"]["1"]["mag"] == pytest.approx(2.0, rel=1e-6)


def test_singular_network_is_rejected():
    with pytest.raises(ValueError):
        run("mna-ac", {
            "freq_hz": 50.0,
            "elements": [
                {"id": "V1", "type": "V", "a": 1, "b": 2, "value": 10.0},
                {"id": "R1", "type": "R", "a": 1, "b": 2, "value": 100.0},
            ],
        })


def test_domain_of_validity():
    with pytest.raises(ValueError):
        run("mna-ac", {"freq_hz": 0.0, "elements": []})
    with pytest.raises(ValueError):
        run("mna-ac", {
            "freq_hz": 50.0,
            "elements": [{"id": "X", "type": "Z", "a": 1, "b": 0, "value": 1.0}],
        })
