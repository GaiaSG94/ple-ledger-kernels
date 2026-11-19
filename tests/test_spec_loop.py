"""The ledger-bound loop: provenance in, cited kernels, derived facts out."""

import pytest

from harness.kernels import contract
from harness.spec import SpecError, Workspace


def seeded():
    led = Workspace()
    led.assert_facts([
        {"fid": "F1", "kind": "span", "value": 6.0, "unit": "m", "source": "plan S-101"},
        {"fid": "F2", "kind": "udl", "value": 25.0, "unit": "kN/m", "source": "loading note"},
    ])
    return led


def test_contract_declares_dimensions():
    c = contract("beam-udl-max")
    assert c["params"] == {"L": "length", "w": "force_per_length"}
    assert c["results"]["Mmax_kNm"] == "kN.m"
    assert contract("mna-ac")["params"]["elements"] is None
    with pytest.raises(ValueError):
        contract("nope")


def test_assert_facts_requires_provenance_and_unique_ids():
    led = Workspace()
    with pytest.raises(SpecError, match="source"):
        led.assert_facts([{"fid": "F1", "kind": "span", "value": 6.0, "unit": "m"}])
    with pytest.raises(SpecError, match="fid"):
        led.assert_facts([
            {"fid": "", "kind": "span", "value": 6.0, "unit": "m", "source": "plan"},
        ])
    bad = [
        {"fid": "F9", "kind": "span", "value": 1.0, "unit": "m", "source": "plan"},
        {"fid": "F10", "kind": "span", "value": 1.0, "unit": "m"},
    ]
    with pytest.raises(SpecError):
        led.assert_facts(bad)
    assert led.ledger.get("F9") is None  # all-or-nothing batch
    led.assert_facts([{"fid": "F1", "kind": "span", "value": 6.0, "unit": "m", "source": "plan"}])
    with pytest.raises(SpecError, match="duplicate"):
        led.assert_facts([
            {"fid": "F1", "kind": "span", "value": 7.0, "unit": "m", "source": "plan B"},
        ])


def test_bare_unit_bearing_number_is_refused():
    led = seeded()
    with pytest.raises(SpecError, match="cite a fact"):
        led.compute("beam-udl-max", {"L": 6.0, "w": "F2"})
    with pytest.raises(SpecError, match="unknown fact"):
        led.compute("beam-udl-max", {"L": "F9", "w": "F2"})
    with pytest.raises(SpecError, match="unknown arguments"):
        led.compute("beam-udl-max", {"L": "F1", "w": "F2", "E": "F3"})


def test_dimension_mismatch_between_fact_and_argument():
    led = seeded()
    led.assert_facts([
        {"fid": "F3", "kind": "udl", "value": 25.0, "unit": "kN", "source": "note bis"},
    ])
    with pytest.raises(SpecError, match="force_per_length"):
        led.compute("beam-udl-max", {"L": "F1", "w": "F3"})
    assert led.audit()["counts"].get("VIOLATION") == 1


def test_kernel_output_becomes_auditable_fact():
    led = seeded()
    out = led.compute("beam-udl-max", {"L": "F1", "w": "F2"})
    assert out["results"]["Mmax_kNm"] == pytest.approx(112.5)
    assert out["cited"] == ["F1", "F2"]
    fact = led.ledger.get("K1.Mmax_kNm")
    assert (fact.value, fact.unit) == (112.5, "kN.m")
    assert "F1" in fact.source and "F2" in fact.source
    report = led.audit()
    assert report["clean"] is True
    assert report["counts"].get("VIOLATION", 0) == 0
    assert report["kernel_calls"] == 1


def test_chain_three_phase_into_cable_sizing():
    led = Workspace()
    led.assert_facts([
        {"fid": "V1", "kind": "line_voltage", "value": 400.0, "unit": "V", "source": "single line"},
        {"fid": "P1", "kind": "active_power", "value": 30.0, "unit": "kW", "source": "load schedule"},
        {"fid": "PF", "kind": "power_factor", "value": 0.8, "unit": "-", "source": "load schedule"},
        {"fid": "LEN", "kind": "run_length", "value": 50.0, "unit": "m", "source": "cable route"},
        {"fid": "DROP", "kind": "drop_limit", "value": 5.0, "unit": "%", "source": "design note"},
    ])
    tp = led.compute(
        "three-phase",
        {"V_LL": "V1", "P_kW": "P1", "pf": "PF", "connection": "star"},
    )
    assert tp["results"]["I_line_A"] == pytest.approx(54.1266, abs=1e-3)
    cable = led.compute("cable-size", {
        "I": "K1.I_line_A",
        "L": "LEN",
        "V": "V1",
        "system": "three",
        "material": "cu",
        "max_drop_pct": "DROP",
    })
    assert cable["results"]["A_selected_mm2"] == 6.0
    assert cable["results"]["dV_pct"] == pytest.approx(3.418, abs=1e-3)
    assert cable["cited"][0] == "K1.I_line_A"
    assert led.audit()["clean"] is True
