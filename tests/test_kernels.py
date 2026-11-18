import pytest

from harness.kernels import run


def test_udl_reference_case():
    # L=6 m, w=25 kN/m : Mmax = w*L^2/8 = 112.5 kN.m ; V = 75 kN
    out = run("beam-udl-max", {"L": 6.0, "w": 25.0})
    assert out["Mmax_kNm"] == pytest.approx(112.5)
    assert out["Vmax_kN"] == pytest.approx(75.0)


def test_point_mid_reference_case():
    # L=4 m, P=40 kN : Mmax = P*L/4 = 40 kN.m
    out = run("beam-point-mid", {"L": 4.0, "P": 40.0})
    assert out["Mmax_kNm"] == pytest.approx(40.0)


def test_domain_of_validity():
    with pytest.raises(ValueError):
        run("beam-udl-max", {"L": -1.0, "w": 25.0})
    with pytest.raises(ValueError):
        run("beam-point-mid", {"L": 0.0, "P": 40.0})


def test_unknown_kernel():
    with pytest.raises(ValueError):
        run("does-not-exist", {})
