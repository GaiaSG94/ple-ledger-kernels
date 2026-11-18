import pytest

from harness.facts import Fact, Ledger
from harness.dimensions import audit, check_consistency


def make_ledger():
    led = Ledger()
    led.add(Fact("F1", "span", 6.0, "m", "plan S-101"))
    led.add(Fact("F2", "udl", 25.0, "kN/m", "loading note"))
    return led


def test_fact_roundtrip():
    led = make_ledger()
    assert led.get("F1").value == 6.0
    assert led.by_kind("span")[0].source == "plan S-101"
    with pytest.raises(ValueError):
        led.add(Fact("F1", "span", 7.0, "m", "dup"))


def test_audit_clean():
    verdicts = audit(make_ledger())
    assert all(v.state in ("OK", "UNKNOWN") for v in verdicts)
    assert any(v.state == "OK" for v in verdicts)


def test_audit_detects_dimension_mismatch():
    led = make_ledger()
    led.add(Fact("F3", "udl", 25.0, "kN", "loading note bis"))
    verdicts = audit(led)
    assert any(v.state == "VIOLATION" for v in verdicts)


def test_consistency_unknown_unit():
    a = Fact("A", "x", 1.0, "weird", "src")
    b = Fact("B", "y", 2.0, "m", "src")
    assert check_consistency(a, b).state == "UNKNOWN"


def test_audit_result_band():
    verdicts = audit(make_ledger(), results=[("Mmax", 112.5, "kN.m")])
    assert all(v.state != "VIOLATION" for v in verdicts)
    verdicts = audit(make_ledger(), results=[("Mmax", 1e12, "kN.m")])
    assert any("outside plausible band" in v.reason for v in verdicts)
