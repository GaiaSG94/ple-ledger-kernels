"""WRITE renders from facts only; PROVE catches any number it cannot trace."""

import pytest

from harness.prove import extract, trace
from harness.spec import SpecError, Workspace
from harness.write import render


def seeded():
    led = Workspace()
    led.assert_facts([
        {"fid": "F1", "kind": "span", "value": 6.0, "unit": "m", "source": "plan S-101"},
        {"fid": "F2", "kind": "udl", "value": 25.0, "unit": "kN/m", "source": "loading note"},
    ])
    led.compute("beam-udl-max", {"L": "F1", "w": "F2"})
    return led


def test_render_substitutes_facts_and_results():
    out = render(seeded(), "Beam check", [
        {"heading": "Bending", "body": "Mmax = {K1.Mmax_kNm} under {F2}."},
    ])
    assert "112.5 kN.m [K1.Mmax_kNm]" in out["text"]
    assert "25 kN/m [F2]" in out["text"]
    assert out["used"] == ["K1.Mmax_kNm", "F2"]
    assert "| K1.Mmax_kNm | 112.5 | kN.m |" in out["text"]


def test_render_refuses_unknown_placeholder():
    with pytest.raises(SpecError, match="not a ledger fact"):
        render(seeded(), "x", [{"heading": "h", "body": "{Z9}"}])


def test_render_requires_sections():
    with pytest.raises(SpecError):
        render(seeded(), "x", [])


def test_rendered_text_is_traceable():
    text = render(seeded(), "Beam", [
        {"heading": "Bending", "body": "Mmax = {K1.Mmax_kNm}."},
    ])["text"]
    report = trace(seeded().ledger, text)
    assert report["traceable"] is True, report["untraceable"]


def test_trace_flags_invented_number():
    report = trace(seeded().ledger, "# Beam\n\nMmax = 118.2 kN.m [F1]\n")
    assert report["traceable"] is False
    assert [u["value"] for u in report["untraceable"]] == [118.2]


def test_trace_ignores_ids_headings_and_sources():
    text = (
        "## 3. Results\n\n"
        "See plan S-101, node K1.Mmax_kNm: 112.5 kN.m (F1).\n\n"
        "## Sources\n\n| p.2 | Table 4 |\n"
    )
    report = trace(seeded().ledger, text)
    assert report["numbers"] == 1
    assert report["traceable"] is True


def test_extract_keeps_signs_and_decimals():
    values = [item["value"] for item in extract("dw = -0.045 m, ratio 0.5, 1e+07 mm4")]
    assert values == [-0.045, 0.5, 1e07]
