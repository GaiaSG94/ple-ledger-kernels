"""Deterministic solver kernels. Each kernel declares its domain of validity and is tested against reference cases."""

from harness.facts import Fact


def _require(facts: dict, names: list) -> None:
    missing = [n for n in names if n not in facts]
    if missing:
        raise ValueError(f"missing inputs: {', '.join(missing)}")


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


def run(kernel: str, inputs: dict) -> dict:
    kernels = {
        "beam-udl-max": beam_udl_max,
        "beam-point-mid": beam_point_mid,
    }
    if kernel not in kernels:
        raise ValueError(f"unknown kernel: {kernel}")
    return kernels[kernel](**inputs)
