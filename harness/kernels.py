"""Deterministic solver kernels.

Each kernel declares its domain of validity, validates its inputs and is
tested against hand-checked reference cases. The LLM never computes: it puts
facts in the ledger, then calls these kernels by name.
"""

import cmath
import inspect
import math
from typing import Optional

# Resistivity at 20 C, ohm.mm2/m.
RHO = {"cu": 0.0175, "al": 0.0282}
# Standard metric conductor sections, mm2.
STANDARD_SECTIONS_MM2 = (
    1.5, 2.5, 4.0, 6.0, 10.0, 16.0, 25.0, 35.0, 50.0,
    70.0, 95.0, 120.0, 150.0, 185.0, 240.0, 300.0,
)
THREE_PHASE = {"three", "3ph", "three-phase", "triphase"}
SINGLE_PHASE = {"single", "1ph", "single-phase", "dc"}
# Units accepted by the AC network solver, as multipliers to SI.
UNIT_SCALE = {
    "ohm": 1.0, "kohm": 1e3, "Mohm": 1e6,
    "H": 1.0, "mH": 1e-3, "uH": 1e-6,
    "F": 1.0, "mF": 1e-3, "uF": 1e-6, "nF": 1e-9, "pF": 1e-12,
}


def _require(facts: dict, names: list) -> None:
    missing = [n for n in names if n not in facts]
    if missing:
        raise ValueError(f"missing inputs: {', '.join(missing)}")


def _r(x: float, nd: int = 6) -> float:
    return round(x, nd)


def beam_udl_max(L: float, w: float) -> dict:
    """Simply supported beam under uniform load w [kN/m] over span L [m].

    Domain: prismatic, linear-elastic, small deflection, L/w geometry unrestricted.
    Returns Mmax [kN.m] (L^2/8) and delta_max [mm] = 5*w*L^4/(384*E*I) when E,I given.
    """
    if L <= 0 or w <= 0:
        raise ValueError("span and load must be positive")
    mmax = w * L ** 2 / 8.0
    v = w * L / 2.0
    return {"Mmax_kNm": round(mmax, 6), "Vmax_kN": round(v, 6)}


def beam_point_mid(L: float, P: float) -> dict:
    """Simply supported beam, point load P [kN] at midspan: Mmax = P*L/4."""
    if L <= 0 or P <= 0:
        raise ValueError("span and load must be positive")
    return {"Mmax_kNm": round(P * L / 4.0, 6), "Vmax_kN": round(P / 2.0, 6)}


def section_props_rect(b_mm: float, h_mm: float) -> dict:
    """Solid rectangle b x h [mm], bending about the axis parallel to b.

    Domain: homogeneous solid section, elastic bending, no shear lag.
    A = b*h, I = b*h^3/12, S = b*h^2/6, r = sqrt(I/A).
    """
    if b_mm <= 0 or h_mm <= 0:
        raise ValueError("b and h must be positive")
    a = b_mm * h_mm
    i = b_mm * h_mm ** 3 / 12.0
    s = b_mm * h_mm ** 2 / 6.0
    return {
        "A_mm2": _r(a),
        "I_mm4": _r(i),
        "S_mm3": _r(s),
        "r_mm": _r(math.sqrt(i / a)),
    }


def section_props_circle(d_mm: float) -> dict:
    """Solid circle of diameter d [mm]; same outputs as the rectangle kernel.

    Domain: homogeneous solid section, elastic bending.
    A = pi*d^2/4, I = pi*d^4/64, S = pi*d^3/32, r = d/4.
    """
    if d_mm <= 0:
        raise ValueError("d must be positive")
    a = math.pi * d_mm ** 2 / 4.0
    i = math.pi * d_mm ** 4 / 64.0
    s = math.pi * d_mm ** 3 / 32.0
    return {
        "A_mm2": _r(a),
        "I_mm4": _r(i),
        "S_mm3": _r(s),
        "r_mm": _r(d_mm / 4.0),
    }


def _unit_scale(el: dict, default: str) -> float:
    unit = el.get("unit", default)
    if unit not in UNIT_SCALE:
        raise ValueError(f"element {el.get('id', '?')}: unknown unit '{unit}'")
    return UNIT_SCALE[unit]


def _impedance(el: dict, omega: float) -> complex:
    kind = str(el["type"]).upper()
    if kind == "R":
        z = complex(el["value"] * _unit_scale(el, "ohm"), 0.0)
    elif kind == "L":
        z = complex(0.0, omega * el["value"] * _unit_scale(el, "H"))
    elif kind == "C":
        c = el["value"] * _unit_scale(el, "F")
        if c <= 0:
            raise ValueError(f"element {el.get('id', '?')}: capacitance must be positive")
        z = complex(0.0, -1.0 / (omega * c))
    else:
        raise ValueError(f"element {el.get('id', '?')}: unknown type '{kind}'")
    if z == 0:
        raise ValueError(f"element {el.get('id', '?')}: zero impedance")
    return z


def _solve_linear(a_mat: list, rhs: list) -> list:
    """Gaussian elimination with partial pivoting on a complex system."""
    size = len(rhs)
    m = [list(row) + [rhs[i]] for i, row in enumerate(a_mat)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-15:
            raise ValueError("singular network: every node must reach ground")
        m[col], m[pivot] = m[pivot], m[col]
        for row in range(col + 1, size):
            factor = m[row][col] / m[col][col]
            if factor:
                for c in range(col, size + 1):
                    m[row][c] -= factor * m[col][c]
    x = [0j] * size
    for row in range(size - 1, -1, -1):
        acc = m[row][size] - sum(m[row][c] * x[c] for c in range(row + 1, size))
        x[row] = acc / m[row][row]
    return x


def _phasor(z: complex) -> dict:
    return {
        "mag": _r(abs(z)),
        "phase_deg": _r(math.degrees(cmath.phase(z))),
        "re": _r(z.real),
        "im": _r(z.imag),
    }


def mna_ac(freq_hz: float, elements: list, probe_nodes: Optional[list] = None) -> dict:
    """Steady-state AC nodal analysis (modified nodal analysis) at one frequency.

    Node 0 is the ground reference. Elements are dicts with id, type, value, a,
    b (and unit where it is not the SI one):
      R  value in ohm  (unit ohm/kohm/Mohm)
      L  value in H    (unit H/mH/uH)
      C  value in F    (unit F/mF/uF/nF/pF)
      V  ideal voltage source, value in V, a = + terminal, b = - terminal
      I  ideal current source, value in A injected into a and out of b

    Domain: linear time-invariant lumped network, single frequency, no mutual
    inductance, no controlled sources. Returns node phasors, the probe subset,
    ideal-source currents and passive branch currents.
    """
    if freq_hz <= 0:
        raise ValueError("frequency must be positive")
    if not elements:
        raise ValueError("no elements")
    omega = 2.0 * math.pi * freq_hz
    for el in elements:
        _require(el, ["type", "value", "a", "b"])
    nodes = sorted({int(el["a"]) for el in elements} | {int(el["b"]) for el in elements})
    nodes = [n for n in nodes if n != 0]
    if not nodes:
        raise ValueError("no nodes to solve")
    index = {n: i for i, n in enumerate(nodes)}
    sources = [el for el in elements if str(el["type"]).upper() == "V"]
    row_of_source = {id(el): len(nodes) + j for j, el in enumerate(sources)}
    size = len(nodes) + len(sources)
    a_mat = [[0j] * size for _ in range(size)]
    rhs = [0j] * size

    def idx(node: int) -> int:
        return index.get(node, -1)

    for el in elements:
        kind = str(el["type"]).upper()
        na, nb = idx(int(el["a"])), idx(int(el["b"]))
        if kind in ("R", "L", "C"):
            y = 1.0 / _impedance(el, omega)
            if na >= 0:
                a_mat[na][na] += y
            if nb >= 0:
                a_mat[nb][nb] += y
            if na >= 0 and nb >= 0:
                a_mat[na][nb] -= y
                a_mat[nb][na] -= y
        elif kind == "I":
            if na >= 0:
                rhs[na] += complex(el["value"], 0.0)
            if nb >= 0:
                rhs[nb] -= complex(el["value"], 0.0)
        elif kind == "V":
            k = row_of_source[id(el)]
            if na >= 0:
                a_mat[na][k] += 1.0
                a_mat[k][na] += 1.0
            if nb >= 0:
                a_mat[nb][k] -= 1.0
                a_mat[k][nb] -= 1.0
            rhs[k] = complex(el["value"], 0.0)
        else:
            raise ValueError(f"element {el.get('id', '?')}: unknown type '{kind}'")

    x = _solve_linear(a_mat, rhs)
    node_v = {str(node): x[index[node]] for node in nodes}
    probe = list(probe_nodes) if probe_nodes else nodes
    unknown = [p for p in probe if str(p) not in node_v]
    if unknown:
        raise ValueError(f"probe nodes not in network: {unknown}")

    branches = {}
    for j, el in enumerate(elements):
        if str(el["type"]).upper() not in ("R", "L", "C"):
            continue
        va = x[index[int(el["a"])]] if int(el["a"]) in index else 0j
        vb = x[index[int(el["b"])]] if int(el["b"]) in index else 0j
        current = (va - vb) / _impedance(el, omega)
        branches[el.get("id", f"E{j}")] = _phasor(current)

    return {
        "freq_hz": freq_hz,
        "nodes_V": {n: _phasor(v) for n, v in node_v.items()},
        "probe_V": {str(p): _phasor(node_v[str(p)]) for p in probe},
        "sources_A": {
            el.get("id", f"V{j}"): _phasor(x[row_of_source[id(el)]])
            for j, el in enumerate(sources)
        },
        "branches_A": branches,
    }


def three_phase(V_LL: float, P_kW: float, pf: float, connection: str = "star") -> dict:
    """Balanced three-phase load from line voltage, active power and power factor.

    Domain: balanced sinusoidal steady state, constant power factor, no
    harmonics. S = P/pf, Q = sqrt(S^2 - P^2), I_line = S/(sqrt(3)*V_LL).
    Star: V_phase = V_LL/sqrt(3) and I_phase = I_line.
    Delta: V_phase = V_LL and I_phase = I_line/sqrt(3).
    """
    if V_LL <= 0 or P_kW <= 0:
        raise ValueError("line voltage and active power must be positive")
    if not 0 < pf <= 1:
        raise ValueError("power factor must be in (0, 1]")
    conn = str(connection).lower()
    if conn not in ("star", "wye", "y", "delta", "triangle", "d"):
        raise ValueError(f"unknown connection: {connection}")
    s = P_kW / pf
    q = math.sqrt(max(s * s - P_kW * P_kW, 0.0))
    i_line = s * 1000.0 / (math.sqrt(3.0) * V_LL)
    if conn in ("star", "wye", "y"):
        v_phase, i_phase = V_LL / math.sqrt(3.0), i_line
    else:
        v_phase, i_phase = V_LL, i_line / math.sqrt(3.0)
    return {
        "S_kVA": _r(s),
        "Q_kvar": _r(q),
        "I_line_A": _r(i_line),
        "I_phase_A": _r(i_phase),
        "V_phase_V": _r(v_phase),
        "connection": "star" if conn in ("star", "wye", "y") else "delta",
    }


def cable_size(
    I: float,
    L: float,
    V: float,
    system: str = "three",
    material: str = "cu",
    max_drop_pct: float = 5.0,
) -> dict:
    """Minimum conductor section from a voltage-drop limit, then the next standard size.

    Domain: resistive drop only (20 C resistivity, no reactance, no skin
    effect), single cable run, steady load. k = 2 for DC and single phase,
    k = sqrt(3) for three phase; dV = k*rho*L*I/A. Ampacity, derating and
    short-circuit withstand are out of scope and must be checked separately.
    """
    if I <= 0 or L <= 0 or V <= 0:
        raise ValueError("current, length and voltage must be positive")
    if not 0 < max_drop_pct <= 100:
        raise ValueError("max_drop_pct must be in (0, 100]")
    mat = str(material).lower()
    if mat not in RHO:
        raise ValueError(f"unknown material: {material}")
    sys_name = str(system).lower()
    if sys_name in THREE_PHASE:
        k = math.sqrt(3.0)
    elif sys_name in SINGLE_PHASE:
        k = 2.0
    else:
        raise ValueError(f"unknown system: {system}")
    dv_max = V * max_drop_pct / 100.0
    a_min = k * RHO[mat] * L * I / dv_max
    chosen = next((s for s in STANDARD_SECTIONS_MM2 if s >= a_min), None)
    if chosen is None:
        raise ValueError(
            f"required section {a_min:.1f} mm2 exceeds the standard table"
        )
    dv = k * RHO[mat] * L * I / chosen
    return {
        "A_min_mm2": _r(a_min),
        "A_selected_mm2": chosen,
        "dV_V": _r(dv),
        "dV_pct": _r(100.0 * dv / V),
        "rho_ohm_mm2_m": RHO[mat],
        "k": _r(k),
    }


KERNELS = {
    "beam-udl-max": beam_udl_max,
    "beam-point-mid": beam_point_mid,
    "section-props-rect": section_props_rect,
    "section-props-circle": section_props_circle,
    "mna-ac": mna_ac,
    "three-phase": three_phase,
    "cable-size": cable_size,
}


def catalog() -> list:
    """Every kernel with its one-line domain summary and argument names."""
    out = []
    for name, fn in KERNELS.items():
        first = (fn.__doc__ or "").strip().splitlines()
        out.append({
            "name": name,
            "summary": first[0] if first else "",
            "params": list(inspect.signature(fn).parameters),
        })
    return out


def run(kernel: str, inputs: dict) -> dict:
    if kernel not in KERNELS:
        raise ValueError(f"unknown kernel: {kernel}")
    return KERNELS[kernel](**inputs)
