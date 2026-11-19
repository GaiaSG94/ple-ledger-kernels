import math

import pytest

from harness.kernels import run


def test_rect_reference_case():
    # b=200 mm, h=500 mm : A=100 000 mm2, I=2.08333e9 mm4, S=8.33333e6 mm3
    out = run("section-props-rect", {"b_mm": 200.0, "h_mm": 500.0})
    assert out["A_mm2"] == pytest.approx(100_000.0)
    assert out["I_mm4"] == pytest.approx(2_083_333_333.333333)
    assert out["S_mm3"] == pytest.approx(8_333_333.333333)
    assert out["r_mm"] == pytest.approx(500.0 / math.sqrt(12.0))


def test_circle_reference_case():
    # d=100 mm : A=7853.98 mm2, I=4.90874e6 mm4, S=98 174.8 mm3, r=25 mm
    out = run("section-props-circle", {"d_mm": 100.0})
    assert out["A_mm2"] == pytest.approx(math.pi * 100.0 ** 2 / 4.0)
    assert out["I_mm4"] == pytest.approx(math.pi * 100.0 ** 4 / 64.0)
    assert out["S_mm3"] == pytest.approx(math.pi * 100.0 ** 3 / 32.0)
    assert out["r_mm"] == pytest.approx(25.0)


def test_scaling():
    # Doubling h multiplies I by 8 and S by 4.
    small = run("section-props-rect", {"b_mm": 100.0, "h_mm": 200.0})
    big = run("section-props-rect", {"b_mm": 100.0, "h_mm": 400.0})
    assert big["I_mm4"] == pytest.approx(8.0 * small["I_mm4"])
    assert big["S_mm3"] == pytest.approx(4.0 * small["S_mm3"])


def test_domain_of_validity():
    with pytest.raises(ValueError):
        run("section-props-rect", {"b_mm": 0.0, "h_mm": 500.0})
    with pytest.raises(ValueError):
        run("section-props-circle", {"d_mm": -10.0})
