"""Zero-token dimensional audit: every quantity must carry a consistent dimension."""

from dataclasses import dataclass
from typing import Optional

from harness.facts import Fact

# Exponent vectors over (L, M, T, I, Theta, N).
DIMS = {
    "length": (1, 0, 0, 0, 0, 0),
    "area": (2, 0, 0, 0, 0, 0),
    "force": (1, 1, -2, 0, 0, 0),
    "moment": (2, 1, -2, 0, 0, 0),
    "pressure": (-1, 1, -2, 0, 0, 0),
    "mass": (0, 1, 0, 0, 0, 0),
    "time": (0, 0, 1, 0, 0, 0),
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
    "N": "force", "kN": "force", "MN": "force", "lbf": "force", "kip": "force",
    "N.m": "moment", "kN.m": "moment", "kNm": "moment", "lbf.ft": "moment",
    "Pa": "pressure", "kPa": "pressure", "MPa": "pressure", "psi": "pressure",
    "kg": "mass", "t": "mass", "g": "mass",
    "s": "time", "min": "time", "h": "time",
    "A": "current", "kA": "current",
    "V": "voltage", "kV": "voltage", "mV": "voltage",
    "W": "power", "kW": "power", "MW": "power",
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


def audit(ledger, results=None) -> list[Verdict]:
    """Audit every fact plus any computed results [(label, value, unit)]."""
    out = [check_fact(f) for f in ledger.all()]
    facts = ledger.all()
    for i in range(len(facts)):
        for j in range(i + 1, len(facts)):
            v = check_consistency(facts[i], facts[j])
            if v.state == "VIOLATION":
                out.append(v)
    if results:
        class _Res:
            pass
        for label, value, unit in results:
            f = Fact(fid=f"result:{label}", kind="result", value=value, unit=unit, source="computation")
            v = check_fact(f)
            name = UNIT_TO_DIMS.get(unit)
            if name and name in PLAUSIBLE:
                lo, hi = PLAUSIBLE[name]
                if not (lo <= abs(value) <= hi):
                    v = Verdict(f, "UNKNOWN", f"{label}={value} {unit} outside plausible band")
            out.append(v)
    return out
