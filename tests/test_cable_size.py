import pytest

from harness.kernels import run


def test_three_phase_copper():
    # 54.1266 A, 50 m, 400 V, 5 % (20 V) : A_min=4.1018 -> 6 mm2, dV=13.6727 V.
    out = run("cable-size", {
        "I": 54.12659, "L": 50.0, "V": 400.0,
        "system": "three", "material": "cu", "max_drop_pct": 5.0,
    })
    assert out["A_min_mm2"] == pytest.approx(4.10182, rel=1e-4)
    assert out["A_selected_mm2"] == 6.0
    assert out["dV_V"] == pytest.approx(13.67276, rel=1e-4)
    assert out["dV_pct"] == pytest.approx(3.41819, rel=1e-4)
    assert out["dV_pct"] <= 5.0


def test_single_phase_aluminium():
    # 20 A, 30 m, 230 V, 3 % (6.9 V) : A_min=4.904 -> 6 mm2.
    out = run("cable-size", {
        "I": 20.0, "L": 30.0, "V": 230.0,
        "system": "single", "material": "al", "max_drop_pct": 3.0,
    })
    assert out["A_min_mm2"] == pytest.approx(4.90435, rel=1e-4)
    assert out["A_selected_mm2"] == 6.0
    assert out["k"] == pytest.approx(2.0)
    assert out["dV_V"] == pytest.approx(5.64, rel=1e-2)


def test_three_phase_uses_sqrt_three():
    out = run("cable-size", {"I": 10.0, "L": 10.0, "V": 400.0})
    assert out["k"] == pytest.approx(1.732051, rel=1e-6)
    assert out["A_selected_mm2"] == 1.5


def test_section_beyond_table_is_rejected():
    with pytest.raises(ValueError):
        run("cable-size", {"I": 5000.0, "L": 1000.0, "V": 400.0})


def test_domain_of_validity():
    with pytest.raises(ValueError):
        run("cable-size", {"I": 0.0, "L": 10.0, "V": 400.0})
    with pytest.raises(ValueError):
        run("cable-size", {
            "I": 10.0, "L": 10.0, "V": 400.0, "material": "steel",
        })
    with pytest.raises(ValueError):
        run("cable-size", {"I": 10.0, "L": 10.0, "V": 400.0, "system": "2ph"})
