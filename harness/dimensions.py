"""Zero-token dimensional audit: every quantity must carry a consistent dimension."""

from dataclasses import dataclass
from typing import Optional

from harness.facts import Fact

# Exponent vectors over (L, M, T, I, Theta, N).
DIMS = {
    "length": (1, 0, 0, 0, 0, 0),
    "area": (2, 0, 0, 0, 0, 0),
    "section_modulus": (3, 0, 0, 0, 0, 0),
    "second_moment": (4, 0, 0, 0, 0, 0),
    "force": (1, 1, -2, 0, 0, 0),
    "force_per_length": (0, 1, -2, 0, 0, 0),
    "moment": (2, 1, -2, 0, 0, 0),
    "pressure": (-1, 1, -2, 0, 0, 0),
    "mass": (0, 1, 0, 0, 0, 0),
    "time": (0, 0, 1, 0, 0, 0),
    "frequency": (0, 0, -1, 0, 0, 0),
    "current": (0, 0, 0, 1, 0, 0),
    "voltage": (2, 1, -3, -1, 0, 0),
    "power": (2, 1, -3, 0, 0, 0),
    "energy": (2, 1, -2, 0, 0, 0),
    "temperature": (0, 0, 0, 0, 1, 0),
    "dimensionless": (0, 0, 0, 0, 0, 0),
}

UNIT_TO_DIMS = {
    "m": "length", "mm": "length", "cm": "length", "km": "length", "in": "length", "ft": "length",
    "m2": "area", "mm2": "area",
    "mm3": "section_modulus", "cm3": "section_modulus",
    "mm4": "second_moment", "cm4": "second_moment",
    "N": "force", "kN": "force", "MN": "force", "lbf": "force", "kip": "force",
    "N/m": "force_per_length", "kN/m": "force_per_length", "N/mm": "force_per_length",
    "N.m": "moment", "kN.m": "moment", "kNm": "moment", "lbf.ft": "moment",
    "Pa": "pressure", "kPa": "pressure", "MPa": "pressure", "psi": "pressure",
    "kg": "mass", "t": "mass", "g": "mass",
    "s": "time", "min": "time", "h": "time",
    "Hz": "frequency", "kHz": "frequency", "MHz": "frequency",
    "A": "current", "kA": "current",
    "V": "voltage", "kV": "voltage", "mV": "voltage",
    "W": "power", "kW": "power", "MW": "power",
    "VA": "power", "kVA": "power", "MVA": "power",
    "var": "power", "kvar": "power", "Mvar": "power",
    "J": "energy", "kJ": "energy", "kWh": "energy",
    "C": "temperature", "K": "temperature",
    "-": "dimensionless", "%": "dimensionless",
}

# Soft plausibility bands; violations are advisory (UNKNOWN) unless severity is hard.
PLAUSIBLE = {
    "force": (1e-3, 1e9),
    "moment": (1e-3, 1e9),
    "length": (1e-6, 1e5),
    "pressure": (1e-3, 1e10),
    "voltage": (1e-3, 1e6),
    "current": (1e-6, 1e5),
    "power": (1e-3, 1e9),
}


@dataclass
class Verdict:
    fact: Fact
    state: str
    reason: str = ""
    dims: Optional[tuple] = None


def unit_dims(unit: str) -> Optional[tuple]:
    name = UNIT_TO_DIMS.get(unit)
    return DIMS.get(name) if name else None


def check_fact(fact: Fact) -> Verdict:
    d = unit_dims(fact.unit)
    if d is None:
        return Verdict(fact, "UNKNOWN", f"unit '{fact.unit}' not in registry")
    return Verdict(fact, "OK", dims=d)


def check_consistency(a: Fact, b: Fact) -> Verdict:
    """Two facts cited for the same quantity must share a dimension."""
    da, db = unit_dims(a.unit), unit_dims(b.unit)
    if da is None or db is None:
        return Verdict(a, "UNKNOWN", "unit not in registry")
    if da != db:
        return Verdict(
            a, "VIOLATION",
            f"dimension mismatch between {a.fid} ({a.unit}) and {b.fid} ({b.unit})", da,
        )
    return Verdict(a, "OK", dims=da)


def _band_reason(fact: Fact) -> Optional[str]:
    name = UNIT_TO_DIMS.get(fact.unit)
    if not name or name not in PLAUSIBLE:
        return None
    lo, hi = PLAUSIBLE[name]
    if lo <= abs(fact.value) <= hi:
        return None
    return f"{fact.label or fact.kind}={fact.value} {fact.unit} outside plausible band"


def audit(ledger, results=None) -> list[Verdict]:
    """Audit every fact plus any computed results [(label, value, unit)].

    Facts of the same kind are checked against each other: two facts for the
    same quantity with different dimensions are a VIOLATION. Facts whose kind
    starts with 'result:' also get the plausibility band, so a slipped decimal
    in a kernel output is reported without any extra call.
    """
    facts = ledger.all()
    out = [check_fact(f) for f in facts]
    for fact, verdict in zip(facts, out):
        if verdict.state == "OK" and fact.kind.startswith("result:"):
            reason = _band_reason(fact)
            if reason:
                verdict.state, verdict.reason = "UNKNOWN", reason
    groups = {}
    for fact in facts:
        groups.setdefault(fact.kind, []).append(fact)
    for group in groups.values():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                v = check_consistency(group[i], group[j])
                if v.state == "VIOLATION":
                    out.append(v)
    if results:
        for label, value, unit in results:
            f = Fact(fid=f"result:{label}", kind="result", value=value, unit=unit, source="computation")
            v = check_fact(f)
            reason = _band_reason(f)
            if reason:
                v = Verdict(f, "UNKNOWN", reason)
            out.append(v)
    return out
