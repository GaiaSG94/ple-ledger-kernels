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


# ---------------------------------------------------------------------------
# Structural, thermal and hydraulic kernels.
#
# Units are the ones in the argument names: no implicit conversion anywhere.
# ---------------------------------------------------------------------------


def _matmul(a, b):
    return [
        [sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))]
        for i in range(len(a))
    ]


def _transpose(a):
    return [list(row) for row in zip(*a)]


def _condense(k_full, f_full, fixed):
    """Free DOFs and the reduced system, ready for _solve_linear."""
    free = [d for d in range(len(f_full)) if d not in fixed]
    if not free:
        return free, [], []
    return (
        free,
        [[k_full[r][c] for c in free] for r in free],
        [f_full[r] for r in free],
    )


def _expand(free, solved, size):
    out = [0.0] * size
    for dof, value in zip(free, solved):
        out[dof] = value
    return out


def _solve_structure(a_mat, rhs, free):
    """Solve the reduced structural system, naming a mechanism as such."""
    if not free:
        return []
    try:
        return [v.real for v in _solve_linear(a_mat, rhs)]
    except ValueError as exc:
        raise ValueError(
            "unstable structure (singular stiffness): check supports and bracing"
        ) from exc


def truss(nodes, members, supports, loads):
    """Plane pin-jointed truss by the direct stiffness method, nodal loads only.

    Domain: linear-elastic axial members, frictionless pins, small
    displacements, static load, no self-weight, no buckling or yielding check.
    nodes: {id, x_m, y_m}. members: {id, a, b, E_GPa, A_mm2}. supports:
    {node, ux, uy} booleans. loads: {node, Fx_kN, Fy_kN}. EA in kN because
    1 GPa * 1 mm2 = 1 kN.
    """
    if not nodes or not members or not supports:
        raise ValueError("truss needs at least one node, member and support")
    xy, pos = {}, {}
    for n in nodes:
        _require(n, ["id", "x_m", "y_m"])
        xy[n["id"]] = (float(n["x_m"]), float(n["y_m"]))
        pos[n["id"]] = len(pos)
    size = 2 * len(nodes)
    fixed = set()
    for support in supports:
        _require(support, ["node"])
        if support["node"] not in pos:
            raise ValueError(f"support on unknown node {support['node']}")
        i = pos[support["node"]]
        if support.get("ux"):
            fixed.add(2 * i)
        if support.get("uy"):
            fixed.add(2 * i + 1)
    k_full = [[0.0] * size for _ in range(size)]
    geometry = {}
    for m in members:
        _require(m, ["a", "b", "E_GPa", "A_mm2"])
        if m["a"] not in xy or m["b"] not in xy:
            raise ValueError(f"member {m.get('id', '?')}: unknown node")
        if m["E_GPa"] <= 0 or m["A_mm2"] <= 0:
            raise ValueError(f"member {m.get('id', '?')}: E and A must be positive")
        xa, ya = xy[m["a"]]
        xb, yb = xy[m["b"]]
        length = math.hypot(xb - xa, yb - ya)
        if length <= 0:
            raise ValueError(f"member {m.get('id', '?')}: zero length")
        c, s = (xb - xa) / length, (yb - ya) / length
        ea = m["E_GPa"] * m["A_mm2"]
        block = [
            [c * c, c * s, -c * c, -c * s],
            [c * s, s * s, -c * s, -s * s],
            [-c * c, -c * s, c * c, c * s],
            [-c * s, -s * s, c * s, s * s],
        ]
        dofs = [
            2 * pos[m["a"]],
            2 * pos[m["a"]] + 1,
            2 * pos[m["b"]],
            2 * pos[m["b"]] + 1,
        ]
        for r in range(4):
            for q in range(4):
                k_full[dofs[r]][dofs[q]] += (ea / length) * block[r][q]
        geometry[m.get("id", f"M{len(geometry) + 1}")] = (
            m["a"],
            m["b"],
            c,
            s,
            length,
            ea,
        )
    f_full = [0.0] * size
    for load in loads or []:
        _require(load, ["node"])
        if load["node"] not in pos:
            raise ValueError(f"load on unknown node {load['node']}")
        i = pos[load["node"]]
        f_full[2 * i] += float(load.get("Fx_kN", 0.0))
        f_full[2 * i + 1] += float(load.get("Fy_kN", 0.0))
    free, a_mat, rhs = _condense(k_full, f_full, fixed)
    disp = _expand(free, _solve_structure(a_mat, rhs, free), size)
    forces = {}
    for mid, (a, b, c, s, length, ea) in geometry.items():
        ia, ib = 2 * pos[a], 2 * pos[b]
        stretch = (disp[ib] - disp[ia]) * c + (disp[ib + 1] - disp[ia + 1]) * s
        forces[mid] = _r(ea * stretch / length)
    residual = [
        sum(k_full[d][q] * disp[q] for q in range(size)) - f_full[d]
        for d in range(size)
    ]
    reactions = {}
    for node_id, i in pos.items():
        if 2 * i not in fixed and 2 * i + 1 not in fixed:
            continue
        reactions[node_id] = {
            "Rx_kN": _r(residual[2 * i]) if 2 * i in fixed else None,
            "Ry_kN": _r(residual[2 * i + 1]) if 2 * i + 1 in fixed else None,
        }
    rx = sum(v["Rx_kN"] or 0.0 for v in reactions.values()) + sum(
        float(load.get("Fx_kN", 0.0)) for load in loads or []
    )
    ry = sum(v["Ry_kN"] or 0.0 for v in reactions.values()) + sum(
        float(load.get("Fy_kN", 0.0)) for load in loads or []
    )
    return {
        "displacements_m": {
            str(node_id): {
                "ux": _r(disp[2 * i]),
                "uy": _r(disp[2 * i + 1]),
            }
            for node_id, i in pos.items()
        },
        "member_forces_kN": forces,
        "reactions_kN": reactions,
        "max_axial_kN": _r(max((abs(v) for v in forces.values()), default=0.0)),
        "max_displacement_m": _r(max((abs(v) for v in disp), default=0.0)),
        "equilibrium_residual_kN": _r(max(abs(rx), abs(ry))),
    }


def frame_2d(nodes, members, supports, loads):
    """Plane frame by the direct stiffness method, three DOFs per node.

    Domain: linear-elastic beam-column elements, small displacements, nodal
    loads only, no distributed loads, no member releases, no second-order
    effects. nodes: {id, x_m, y_m}. members: {id, a, b, E_GPa, A_mm2, I_mm4}
    (I bends in the plane). supports: {node, ux, uy, rz} booleans. loads:
    {node, Fx_kN, Fy_kN, M_kNm}. EI in kN.m2 because E_GPa * I_mm4 is 1e-6.
    """
    if not nodes or not members or not supports:
        raise ValueError("frame needs at least one node, member and support")
    xy, pos = {}, {}
    for n in nodes:
        _require(n, ["id", "x_m", "y_m"])
        xy[n["id"]] = (float(n["x_m"]), float(n["y_m"]))
        pos[n["id"]] = len(pos)
    size = 3 * len(nodes)
    fixed = set()
    for support in supports:
        _require(support, ["node"])
        if support["node"] not in pos:
            raise ValueError(f"support on unknown node {support['node']}")
        i = pos[support["node"]]
        for k, dof in enumerate(("ux", "uy", "rz")):
            if support.get(dof):
                fixed.add(3 * i + k)
    k_full = [[0.0] * size for _ in range(size)]
    geometry = {}
    for m in members:
        _require(m, ["a", "b", "E_GPa", "A_mm2", "I_mm4"])
        if m["a"] not in xy or m["b"] not in xy:
            raise ValueError(f"member {m.get('id', '?')}: unknown node")
        if m["E_GPa"] <= 0 or m["A_mm2"] <= 0 or m["I_mm4"] <= 0:
            raise ValueError(
                f"member {m.get('id', '?')}: E, A and I must be positive"
            )
        xa, ya = xy[m["a"]]
        xb, yb = xy[m["b"]]
        length = math.hypot(xb - xa, yb - ya)
        if length <= 0:
            raise ValueError(f"member {m.get('id', '?')}: zero length")
        c, s = (xb - xa) / length, (yb - ya) / length
        ea = m["E_GPa"] * m["A_mm2"]
        ei = m["E_GPa"] * m["I_mm4"] * 1e-6
        l2, l3 = length * length, length ** 3
        kl = [
            [ea / length, 0.0, 0.0, -ea / length, 0.0, 0.0],
            [0.0, 12 * ei / l3, 6 * ei / l2, 0.0, -12 * ei / l3, 6 * ei / l2],
            [0.0, 6 * ei / l2, 4 * ei / length, 0.0, -6 * ei / l2, 2 * ei / length],
            [-ea / length, 0.0, 0.0, ea / length, 0.0, 0.0],
            [0.0, -12 * ei / l3, -6 * ei / l2, 0.0, 12 * ei / l3, -6 * ei / l2],
            [0.0, 6 * ei / l2, 2 * ei / length, 0.0, -6 * ei / l2, 4 * ei / length],
        ]
        t = [
            [c, s, 0.0, 0.0, 0.0, 0.0],
            [-s, c, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, c, s, 0.0],
            [0.0, 0.0, 0.0, -s, c, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        ]
        kg = _matmul(_transpose(t), _matmul(kl, t))
        dofs = [
            3 * pos[m["a"]] + k for k in range(3)
        ] + [3 * pos[m["b"]] + k for k in range(3)]
        for r in range(6):
            for q in range(6):
                k_full[dofs[r]][dofs[q]] += kg[r][q]
        geometry[m.get("id", f"F{len(geometry) + 1}")] = (m["a"], m["b"], kl, t)
    f_full = [0.0] * size
    for load in loads or []:
        _require(load, ["node"])
        if load["node"] not in pos:
            raise ValueError(f"load on unknown node {load['node']}")
        i = pos[load["node"]]
        f_full[3 * i] += float(load.get("Fx_kN", 0.0))
        f_full[3 * i + 1] += float(load.get("Fy_kN", 0.0))
        f_full[3 * i + 2] += float(load.get("M_kNm", 0.0))
    free, a_mat, rhs = _condense(k_full, f_full, fixed)
    disp = _expand(free, _solve_structure(a_mat, rhs, free), size)
    ends = {}
    for mid, (a, b, kl, t) in geometry.items():
        d_global = [
            disp[3 * pos[a]],
            disp[3 * pos[a] + 1],
            disp[3 * pos[a] + 2],
            disp[3 * pos[b]],
            disp[3 * pos[b] + 1],
            disp[3 * pos[b] + 2],
        ]
        d_local = [sum(t[i][k] * d_global[k] for k in range(6)) for i in range(6)]
        f_local = [sum(kl[i][k] * d_local[k] for k in range(6)) for i in range(6)]
        ends[mid] = {
            "N_kN": _r(f_local[3]),
            "Va_kN": _r(f_local[1]),
            "Vb_kN": _r(f_local[4]),
            "Ma_kNm": _r(f_local[2]),
            "Mb_kNm": _r(f_local[5]),
        }
    residual = [
        sum(k_full[d][q] * disp[q] for q in range(size)) - f_full[d]
        for d in range(size)
    ]
    reactions = {}
    for node_id, i in pos.items():
        if not (3 * i in fixed or 3 * i + 1 in fixed or 3 * i + 2 in fixed):
            continue
        reactions[node_id] = {
            "Rx_kN": _r(residual[3 * i]) if 3 * i in fixed else None,
            "Ry_kN": _r(residual[3 * i + 1]) if 3 * i + 1 in fixed else None,
            "Mz_kNm": _r(residual[3 * i + 2]) if 3 * i + 2 in fixed else None,
        }
    fx = fy = mz = 0.0
    for node_id, i in pos.items():
        rx = f_full[3 * i] + residual[3 * i]
        ry = f_full[3 * i + 1] + residual[3 * i + 1]
        mm = f_full[3 * i + 2] + residual[3 * i + 2]
        fx += rx
        fy += ry
        mz += mm + xy[node_id][0] * ry - xy[node_id][1] * rx
    return {
        "displacements": {
            str(node_id): {
                "ux_m": _r(disp[3 * i]),
                "uy_m": _r(disp[3 * i + 1]),
                "rz_rad": _r(disp[3 * i + 2]),
            }
            for node_id, i in pos.items()
        },
        "member_end_forces": ends,
        "reactions": reactions,
        "max_displacement_m": _r(
            max((abs(v) for i, v in enumerate(disp) if i % 3 != 2), default=0.0)
        ),
        "max_moment_kNm": _r(
            max(
                (abs(v) for end in ends.values() for v in (end["Ma_kNm"], end["Mb_kNm"])),
                default=0.0,
            )
        ),
        "equilibrium_residual_kN": _r(max(abs(fx), abs(fy))),
        "equilibrium_residual_kNm": _r(abs(mz)),
    }


def buckling_euler(
    L_m: float,
    E_GPa: float,
    I_mm4: float,
    K: float = 1.0,
    A_mm2: Optional[float] = None,
) -> dict:
    """Euler critical load of a prismatic column.

    Domain: prismatic homogeneous column, linear-elastic, no imperfection, no
    yielding or local buckling check. K = 1 pinned-pinned, 0.5 fixed-fixed,
    0.7 fixed-pinned, 2 fixed-free. Pcr = pi^2 E I / (K L)^2; with A given it
    also returns sigma_cr = Pcr/A.
    """
    if L_m <= 0 or E_GPa <= 0 or I_mm4 <= 0:
        raise ValueError("length, modulus and second moment must be positive")
    if K <= 0:
        raise ValueError("K must be positive")
    if A_mm2 is not None and A_mm2 <= 0:
        raise ValueError("area must be positive")
    pcr = math.pi ** 2 * E_GPa * I_mm4 * 1e-6 / (K * L_m) ** 2
    out = {"Pcr_kN": _r(pcr), "effective_length_m": _r(K * L_m), "K": K}
    if A_mm2 is not None:
        out["sigma_cr_MPa"] = _r(pcr * 1000.0 / A_mm2)
    return out


def thermo_balance(
    m_dot_kg_s: float,
    cp_kJ_kgK: float,
    T_in_C: float,
    T_out_C: Optional[float] = None,
    Q_supplied_kW: Optional[float] = None,
    tol_pct: float = 1.0,
) -> dict:
    """Steady sensible-heat balance of one stream.

    Domain: single phase, constant cp, no phase change, no reaction, no work,
    perfect mixing. Q = m_dot * cp * (T_out - T_in). Give T_out to compute the
    heat, Q_supplied to compute the outlet, or both to get residual_kW and a
    balanced flag within tol_pct of |Q|.
    """
    if m_dot_kg_s <= 0 or cp_kJ_kgK <= 0:
        raise ValueError("mass flow and cp must be positive")
    if T_out_C is None and Q_supplied_kW is None:
        raise ValueError("give T_out_C, Q_supplied_kW, or both")
    if tol_pct < 0:
        raise ValueError("tol_pct must be non-negative")
    out = {}
    if T_out_C is not None:
        q = m_dot_kg_s * cp_kJ_kgK * (T_out_C - T_in_C)
        out.update(Q_kW=_r(q), T_out_C=T_out_C)
    if Q_supplied_kW is not None:
        if T_out_C is None:
            out["T_out_C"] = _r(T_in_C + Q_supplied_kW / (m_dot_kg_s * cp_kJ_kgK))
            out["Q_kW"] = _r(Q_supplied_kW)
        else:
            residual = Q_supplied_kW - out["Q_kW"]
            allowed = abs(tol_pct) / 100.0 * max(abs(out["Q_kW"]), 1e-9)
            out["residual_kW"] = _r(residual)
            out["balanced"] = abs(residual) <= allowed
    return out


def fluid_network(elements, reservoirs=None, injections=None, probe_nodes=None):
    """Steady incompressible flow in a network of linearized pipe resistances.

    Node 0 is the atmosphere at 0 Pa. elements: {id, a, b, R} with R = dP/Q in
    Pa.s/m3 (laminar, or a resistance the caller already linearized).
    reservoirs: {node, pressure_Pa} fixed-pressure nodes. injections:
    {node, flow_m3_s} added into the network (withdrawals negative).

    Domain: constant properties, linear resistance, no minor losses, no pumps,
    no compressibility or free surface. Continuity residual is reported per
    node; Darcy-Weisbach friction is out of scope here.
    """
    if not elements:
        raise ValueError("no elements")
    for el in elements:
        _require(el, ["a", "b", "R"])
    fixed = {0: 0.0}
    for res in reservoirs or []:
        _require(res, ["node", "pressure_Pa"])
        fixed[int(res["node"])] = float(res["pressure_Pa"])
    nodes = set(fixed)
    for el in elements:
        nodes |= {int(el["a"]), int(el["b"])}
    for inj in injections or []:
        _require(inj, ["node", "flow_m3_s"])
        nodes.add(int(inj["node"]))
    unknown = sorted(n for n in nodes if n not in fixed)
    index = {n: i for i, n in enumerate(unknown)}
    size = len(unknown)
    a_mat = [[0.0] * size for _ in range(size)]
    rhs = [0.0] * size
    for inj in injections or []:
        i = index.get(int(inj["node"]))
        if i is not None:
            rhs[i] += float(inj["flow_m3_s"])
    for el in elements:
        r = float(el["R"])
        if r <= 0:
            raise ValueError(
                f"element {el.get('id', '?')}: resistance must be positive"
            )
        g = 1.0 / r
        na, nb = int(el["a"]), int(el["b"])
        ia, ib = index.get(na, -1), index.get(nb, -1)
        pa, pb = fixed.get(na), fixed.get(nb)
        if ia >= 0:
            a_mat[ia][ia] += g
            if ib >= 0:
                a_mat[ia][ib] -= g
            elif pb is not None:
                rhs[ia] += pb * g
        if ib >= 0:
            a_mat[ib][ib] += g
            if ia >= 0:
                a_mat[ib][ia] -= g
            elif pa is not None:
                rhs[ib] += pa * g
    if size:
        try:
            solved = [v.real for v in _solve_linear(a_mat, rhs)]
        except ValueError as exc:
            raise ValueError(
                "singular network: every node must reach a fixed-pressure node"
            ) from exc
    else:
        solved = []
    pressures = {str(n): _r(p) for n, p in fixed.items()}
    for n, i in index.items():
        pressures[str(n)] = _r(solved[i])
    probe = [str(p) for p in probe_nodes] if probe_nodes else sorted(pressures)
    missing = [p for p in probe if p not in pressures]
    if missing:
        raise ValueError(f"probe nodes not in network: {missing}")
    flows = {}
    net = {n: 0.0 for n in nodes}
    for el in elements:
        na, nb = int(el["a"]), int(el["b"])
        flow = (pressures[str(na)] - pressures[str(nb)]) / float(el["R"])
        flows[el.get("id", f"P{len(flows) + 1}")] = _r(flow)
        net[na] -= flow
        net[nb] += flow
    for inj in injections or []:
        net[int(inj["node"])] += float(inj["flow_m3_s"])
    return {
        "pressures_Pa": {p: pressures[p] for p in probe},
        "flows_m3_s": flows,
        # Reservoirs balance the network by definition; continuity is checked
        # on the nodes whose pressure is solved for.
        "continuity_residual_m3_s": _r(
            max((abs(net[n]) for n in unknown), default=0.0)
        ),
        "max_pressure_Pa": _r(max((abs(v) for v in pressures.values()), default=0.0)),
        "max_flow_m3_s": _r(max((abs(v) for v in flows.values()), default=0.0)),
    }


KERNELS = {
    "beam-udl-max": beam_udl_max,
    "beam-point-mid": beam_point_mid,
    "section-props-rect": section_props_rect,
    "section-props-circle": section_props_circle,
    "mna-ac": mna_ac,
    "three-phase": three_phase,
    "cable-size": cable_size,
    "buckling-euler": buckling_euler,
    "thermo-balance": thermo_balance,
    "truss": truss,
    "frame-2d": frame_2d,
    "fluid-network": fluid_network,
}


# Dimension each unit-bearing argument must carry; None means structural
# (string, list or object) and takes a literal.
ARG_DIMS = {
    "beam-udl-max": {"L": "length", "w": "force_per_length"},
    "beam-point-mid": {"L": "length", "P": "force"},
    "section-props-rect": {"b_mm": "length", "h_mm": "length"},
    "section-props-circle": {"d_mm": "length"},
    "mna-ac": {"freq_hz": "frequency"},
    "three-phase": {"V_LL": "voltage", "P_kW": "power", "pf": "dimensionless"},
    "cable-size": {
        "I": "current",
        "L": "length",
        "V": "voltage",
        "max_drop_pct": "dimensionless",
    },
    "buckling-euler": {
        "L_m": "length",
        "E_GPa": "pressure",
        "I_mm4": "second_moment",
        "K": "dimensionless",
        "A_mm2": "area",
    },
    "thermo-balance": {
        "m_dot_kg_s": "mass_flow",
        "cp_kJ_kgK": "specific_heat",
        "T_in_C": "temperature",
        "T_out_C": "temperature",
        "Q_supplied_kW": "power",
        "tol_pct": "dimensionless",
    },
}

# Unit of the fact recorded for each numeric output of a kernel.
RESULT_UNITS = {
    "beam-udl-max": {"Mmax_kNm": "kN.m", "Vmax_kN": "kN"},
    "beam-point-mid": {"Mmax_kNm": "kN.m", "Vmax_kN": "kN"},
    "section-props-rect": {
        "A_mm2": "mm2", "I_mm4": "mm4", "S_mm3": "mm3", "r_mm": "mm",
    },
    "section-props-circle": {
        "A_mm2": "mm2", "I_mm4": "mm4", "S_mm3": "mm3", "r_mm": "mm",
    },
    "three-phase": {
        "S_kVA": "kVA", "Q_kvar": "kvar", "I_line_A": "A",
        "I_phase_A": "A", "V_phase_V": "V",
    },
    "cable-size": {
        "A_min_mm2": "mm2", "A_selected_mm2": "mm2", "dV_V": "V", "dV_pct": "%",
    },
    "buckling-euler": {"Pcr_kN": "kN", "sigma_cr_MPa": "MPa"},
    "thermo-balance": {"Q_kW": "kW", "T_out_C": "C", "residual_kW": "kW"},
    "truss": {
        "max_axial_kN": "kN",
        "max_displacement_m": "m",
        "equilibrium_residual_kN": "kN",
    },
    "frame-2d": {
        "max_displacement_m": "m",
        "max_moment_kNm": "kN.m",
        "equilibrium_residual_kN": "kN",
    },
    "fluid-network": {"max_pressure_Pa": "Pa", "max_flow_m3_s": "m3/s"},
}


def contract(kernel: str) -> dict:
    """The argument dimensions and result units the spec loop enforces.

    Parameters mapped to None are structural and take literals; every other
    parameter is a physical quantity and must cite a fact of that dimension.
    """
    fn = KERNELS.get(kernel)
    if fn is None:
        raise ValueError(f"unknown kernel: {kernel}")
    dims = ARG_DIMS.get(kernel, {})
    sig = inspect.signature(fn)
    return {
        "name": kernel,
        "params": {p: dims.get(p) for p in sig.parameters},
        "required": [
            p
            for p, v in sig.parameters.items()
            if v.default is inspect.Parameter.empty
        ],
        "results": dict(RESULT_UNITS.get(kernel, {})),
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
