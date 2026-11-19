"""Golden cases for the structural, thermal and hydraulic kernels."""

import pytest

from harness.kernels import run


def test_buckling_euler_reference_case():
    # L=3 m, E=200 GPa, I=1e7 mm4, K=1 (pinned-pinned)
    # EI = 2000 kN.m2, Pcr = pi^2 * 2000 / 9 = 2193.25 kN
    out = run("buckling-euler", {"L_m": 3.0, "E_GPa": 200.0, "I_mm4": 1e7})
    assert out["Pcr_kN"] == pytest.approx(2193.25, abs=0.01)
    assert out["effective_length_m"] == pytest.approx(3.0)
    fixed_free = run("buckling-euler", {"L_m": 3.0, "E_GPa": 200.0, "I_mm4": 1e7, "K": 2.0})
    assert fixed_free["Pcr_kN"] == pytest.approx(out["Pcr_kN"] / 4, rel=1e-6)


def test_buckling_euler_domain():
    with pytest.raises(ValueError):
        run("buckling-euler", {"L_m": 0.0, "E_GPa": 200.0, "I_mm4": 1e7})
    with pytest.raises(ValueError):
        run("buckling-euler", {"L_m": 3.0, "E_GPa": 200.0, "I_mm4": 1e7, "K": 0.0})


def test_thermo_balance_both_directions():
    # 2 kg/s, cp 4.18 kJ/kg.K, 20 -> 80 C : Q = 501.6 kW
    out = run("thermo-balance", {
        "m_dot_kg_s": 2.0, "cp_kJ_kgK": 4.18, "T_in_C": 20.0, "T_out_C": 80.0,
    })
    assert out["Q_kW"] == pytest.approx(501.6)
    reverse = run("thermo-balance", {
        "m_dot_kg_s": 2.0, "cp_kJ_kgK": 4.18, "T_in_C": 20.0, "Q_supplied_kW": 501.6,
    })
    assert reverse["T_out_C"] == pytest.approx(80.0)


def test_thermo_balance_residual_and_domain():
    ok = run("thermo-balance", {
        "m_dot_kg_s": 2.0, "cp_kJ_kgK": 4.18, "T_in_C": 20.0,
        "T_out_C": 80.0, "Q_supplied_kW": 510.0, "tol_pct": 5.0,
    })
    assert ok["residual_kW"] == pytest.approx(8.4)
    assert ok["balanced"] is True
    tight = run("thermo-balance", {
        "m_dot_kg_s": 2.0, "cp_kJ_kgK": 4.18, "T_in_C": 20.0,
        "T_out_C": 80.0, "Q_supplied_kW": 510.0, "tol_pct": 1.0,
    })
    assert tight["balanced"] is False
    with pytest.raises(ValueError):
        run("thermo-balance", {"m_dot_kg_s": 2.0, "cp_kJ_kgK": 4.18, "T_in_C": 20.0})


def triangle_truss(support_two_ux=True):
    return {
        "nodes": [
            {"id": 1, "x_m": 0.0, "y_m": 0.0},
            {"id": 2, "x_m": 4.0, "y_m": 0.0},
            {"id": 3, "x_m": 0.0, "y_m": 3.0},
        ],
        "members": [
            {"id": "M13", "a": 1, "b": 3, "E_GPa": 200.0, "A_mm2": 100.0},
            {"id": "M23", "a": 2, "b": 3, "E_GPa": 200.0, "A_mm2": 100.0},
        ],
        "supports": [
            {"node": 1, "ux": True, "uy": True},
            {"node": 2, "ux": support_two_ux, "uy": True},
        ],
        "loads": [{"node": 3, "Fx_kN": 10.0}],
    }


def test_truss_reference_case():
    # Horizontal 10 kN at node 3: joint 3 gives N23 = -12.5, N13 = +7.5 kN
    out = run("truss", triangle_truss())
    assert out["member_forces_kN"]["M13"] == pytest.approx(7.5)
    assert out["member_forces_kN"]["M23"] == pytest.approx(-12.5)
    assert out["reactions_kN"][1]["Rx_kN"] == pytest.approx(0.0)
    assert out["reactions_kN"][1]["Ry_kN"] == pytest.approx(-7.5)
    assert out["reactions_kN"][2]["Rx_kN"] == pytest.approx(-10.0)
    assert out["reactions_kN"][2]["Ry_kN"] == pytest.approx(7.5)
    assert out["equilibrium_residual_kN"] == pytest.approx(0.0, abs=1e-9)


def test_truss_mechanism_is_reported():
    data = triangle_truss(support_two_ux=False)  # roller: free horizontally
    with pytest.raises(ValueError, match="unstable"):
        run("truss", data)


def test_frame_cantilever_reference_case():
    # Vertical cantilever, EI = 2000 kN.m2, L = 3 m, P = 10 kN at the tip:
    # delta = P L^3 / (3 EI) = 0.045 m, base moment = P L = 30 kN.m
    out = run("frame-2d", {
        "nodes": [
            {"id": 1, "x_m": 0.0, "y_m": 0.0},
            {"id": 2, "x_m": 0.0, "y_m": 3.0},
        ],
        "members": [
            {"id": "C1", "a": 1, "b": 2, "E_GPa": 200.0, "A_mm2": 100.0, "I_mm4": 1e7},
        ],
        "supports": [{"node": 1, "ux": True, "uy": True, "rz": True}],
        "loads": [{"node": 2, "Fx_kN": 10.0}],
    })
    assert abs(out["displacements"]["2"]["ux_m"]) == pytest.approx(0.045, rel=1e-2)
    assert abs(out["reactions"][1]["Mz_kNm"]) == pytest.approx(30.0, rel=1e-3)
    assert abs(out["reactions"][1]["Rx_kN"]) == pytest.approx(10.0, rel=1e-6)
    assert out["max_moment_kNm"] == pytest.approx(30.0, rel=1e-3)
    assert out["equilibrium_residual_kNm"] == pytest.approx(0.0, abs=1e-6)


def test_fluid_network_series_of_two_pipes():
    # 300 kPa reservoir, two 1e6 Pa.s/m3 pipes in series to atmosphere:
    # the midpoint sits at 150 kPa and both pipes carry 0.15 m3/s.
    out = run("fluid-network", {
        "elements": [
            {"id": "P1", "a": 1, "b": 2, "R": 1e6},
            {"id": "P2", "a": 2, "b": 0, "R": 1e6},
        ],
        "reservoirs": [{"node": 1, "pressure_Pa": 300000.0}],
    })
    assert out["pressures_Pa"]["2"] == pytest.approx(150000.0)
    assert out["flows_m3_s"]["P1"] == pytest.approx(0.15)
    assert out["flows_m3_s"]["P2"] == pytest.approx(0.15)
    assert out["continuity_residual_m3_s"] == pytest.approx(0.0, abs=1e-12)


def test_fluid_network_parallel_and_injection():
    # Reservoir 200 kPa -> node 2 -> atmosphere, both pipes 1e6 Pa.s/m3, with
    # 0.05 m3/s injected at node 2. Continuity at node 2 gives
    # (p2-200k)/1e6 + p2/1e6 = 0.05, so p2 = 125 kPa, A = 0.075, B = 0.125.
    out = run("fluid-network", {
        "elements": [
            {"id": "A", "a": 1, "b": 2, "R": 1e6},
            {"id": "B", "a": 2, "b": 0, "R": 1e6},
        ],
        "reservoirs": [{"node": 1, "pressure_Pa": 200000.0}],
        "injections": [{"node": 2, "flow_m3_s": 0.05}],
    })
    assert out["pressures_Pa"]["2"] == pytest.approx(125000.0)
    assert out["flows_m3_s"]["A"] == pytest.approx(0.075)
    assert out["flows_m3_s"]["B"] == pytest.approx(0.125)
    assert out["continuity_residual_m3_s"] == pytest.approx(0.0, abs=1e-9)


def test_fluid_network_floating_node_is_refused():
    with pytest.raises(ValueError, match="singular network"):
        run("fluid-network", {
            "elements": [{"id": "P1", "a": 2, "b": 3, "R": 1e6}],
        })
