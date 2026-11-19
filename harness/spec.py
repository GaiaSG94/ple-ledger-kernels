"""SPEC -> SOLVE -> AUDIT on a typed ledger.

The model specifies: it records facts with provenance (SPEC), calls a kernel
with fact ids (SOLVE), and every numeric output becomes a new fact that can
itself be cited. Nothing unit-bearing enters a kernel as a bare number, so
each number in a deliverable traces back either to a source or to a kernel
call on cited facts.
"""

import numbers

from harness import kernels
from harness.dimensions import DIMS, audit as audit_ledger, unit_dims
from harness.facts import Fact, Ledger

REQUIRED_FIELDS = ("fid", "kind", "value", "unit", "source")


class SpecError(ValueError):
    """The specification cannot be turned into a kernel call as written."""


def _number(value, where):
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise SpecError(f"{where} must be a number, got {type(value).__name__}")
    return float(value)


class Workspace:
    """One task's ledger plus the kernels run against it."""

    def __init__(self):
        self.ledger = Ledger()
        self.calls = []

    # -- SPEC ---------------------------------------------------------------

    def assert_facts(self, items):
        """Add facts read from the task. All-or-nothing, provenance required.

        Each item is {fid, kind, value, unit, source} plus optional label and
        confidence. Duplicate ids are refused, and a batch with one bad item
        adds nothing, so the model can resend the whole batch.
        """
        if isinstance(items, dict):
            items = [items]
        if not isinstance(items, list) or not items:
            raise SpecError("facts must be a non-empty array of objects")
        batch, seen = [], set()
        for n, item in enumerate(items):
            where = f"facts[{n}]"
            if not isinstance(item, dict):
                raise SpecError(f"{where} must be an object")
            missing = [k for k in REQUIRED_FIELDS if k not in item]
            if missing:
                raise SpecError(f"{where} is missing {', '.join(missing)}")
            fid = str(item["fid"]).strip()
            if not fid:
                raise SpecError(f"{where}.fid must be a non-empty string")
            if fid in seen or self.ledger.get(fid) is not None:
                raise SpecError(f"duplicate fact id: {fid}")
            kind = str(item["kind"]).strip()
            if not kind:
                raise SpecError(f"{where}.kind must be a non-empty string")
            unit = str(item["unit"]).strip()
            if not unit:
                raise SpecError(f"{where}.unit must be a non-empty string")
            source = str(item["source"]).strip()
            if not source:
                raise SpecError(
                    f"{where}.source must say where the number comes from"
                    " (file, page, table, line)"
                )
            seen.add(fid)
            batch.append(
                Fact(
                    fid=fid,
                    kind=kind,
                    value=_number(item["value"], f"{where}.value"),
                    unit=unit,
                    source=source,
                    label=str(item.get("label") or ""),
                    confidence=_number(
                        item.get("confidence", 1.0), f"{where}.confidence"
                    ),
                )
            )
        warnings = []
        for fact in batch:
            self.ledger.add(fact)
            if unit_dims(fact.unit) is None:
                warnings.append(
                    f"{fact.fid}: unit '{fact.unit}' is not in the registry; the"
                    " audit reports it UNKNOWN and no kernel can take it"
                )
        return {
            "added": [f.describe() for f in batch],
            "warnings": warnings,
            "facts": len(self.ledger.all()),
        }

    # -- SOLVE --------------------------------------------------------------

    def _cite(self, value, cited):
        """Replace {"fact": id} leaves inside structural arguments.

        Nodal data (coordinates, loads, member properties) cannot carry a
        dimension check, but it can still point at a ledger fact so the
        provenance of a structural result stays complete.
        """
        if isinstance(value, dict):
            if set(value) == {"fact"}:
                fid = value["fact"]
                fact = self.ledger.get(fid) if isinstance(fid, str) else None
                if fact is None:
                    raise SpecError(f"unknown fact id {fid}")
                if fid not in cited:
                    cited.append(fid)
                return fact.value
            return {k: self._cite(v, cited) for k, v in value.items()}
        if isinstance(value, list):
            return [self._cite(v, cited) for v in value]
        return value

    def resolve(self, kernel, inputs):
        """Turn declared kernel arguments into values, refusing bare quantities.

        Structural parameters (connection, system, material, elements,
        probe_nodes) take literals. Every declared physical parameter must be
        a fact id whose unit has the dimension the kernel expects.
        """
        if not isinstance(inputs, dict):
            raise SpecError("inputs must be a JSON object")
        declared = kernels.contract(kernel)
        params, required = declared["params"], declared["required"]
        extra = sorted(k for k in inputs if k not in params)
        if extra:
            raise SpecError(
                f"{kernel}: unknown arguments {extra}; expected {sorted(params)}"
            )
        kwargs, cited = {}, []
        for name, dim in params.items():
            if name not in inputs:
                if name in required:
                    raise SpecError(f"{kernel}: missing argument {name}")
                continue  # optional: the kernel default applies
            raw = inputs[name]
            if dim is None:
                kwargs[name] = self._cite(raw, cited)
                continue
            fid = raw.get("fact") if isinstance(raw, dict) else raw
            if not isinstance(fid, str) or not fid:
                raise SpecError(
                    f"{kernel}.{name} is a {dim} quantity: cite a fact id"
                    f' ("{name}": "F1"), not the bare value {raw!r}'
                )
            fact = self.ledger.get(fid)
            if fact is None:
                raise SpecError(
                    f"{kernel}.{name}: unknown fact id {fid}; assert it with"
                    " assert_facts first, or cite the fact that holds it"
                )
            got = unit_dims(fact.unit)
            if got is None:
                raise SpecError(
                    f"{kernel}.{name}: fact {fid} has unit '{fact.unit}', which"
                    " is not in the registry, so its dimension cannot be checked"
                )
            if got != DIMS[dim]:
                raise SpecError(
                    f"{kernel}.{name} expects a {dim} fact, but {fid} is"
                    f" {fact.value} {fact.unit} ({fact.kind})"
                )
            kwargs[name] = fact.value
            if fid not in cited:
                cited.append(fid)
        return kwargs, cited

    def compute(self, kernel, inputs):
        """Run one kernel on cited facts and record its outputs as facts."""
        kwargs, cited = self.resolve(kernel, inputs)
        out = kernels.run(kernel, kwargs)
        index = len(self.calls) + 1
        units = kernels.contract(kernel)["results"]
        entries = {}
        for key, unit in units.items():
            value = out.get(key)
            if isinstance(value, bool) or not isinstance(value, numbers.Real):
                continue
            fid = f"K{index}.{key}"
            fact = Fact(
                fid=fid,
                kind=f"result:{kernel}.{key}",
                value=float(value),
                unit=unit,
                source=f"{kernel}({', '.join(cited)})",
                label=key,
            )
            self.ledger.add(fact)
            entries[fid] = fact.describe()
        self.calls.append(
            {
                "call": index,
                "kernel": kernel,
                "cited": cited,
                "derived": sorted(entries),
            }
        )
        return {
            "kernel": kernel,
            "call": index,
            "cited": cited,
            "results": out,
            "ledger_entries": entries,
        }

    # -- AUDIT --------------------------------------------------------------

    def audit(self):
        """Dimensional audit of the ledger, derived results included."""
        verdicts = audit_ledger(self.ledger)
        rows = [
            {
                "fact": v.fact.fid,
                "state": v.state,
                "value": v.fact.value,
                "unit": v.fact.unit,
                "reason": v.reason,
            }
            for v in verdicts
        ]
        counts = {}
        for v in verdicts:
            counts[v.state] = counts.get(v.state, 0) + 1
        return {
            "counts": counts,
            "problems": [r for r in rows if r["state"] != "OK"],
            "kernel_calls": len(self.calls),
            "clean": not any(r["state"] == "VIOLATION" for r in rows),
        }

    def context(self):
        """The ledger as text, for the model to read back."""
        facts = self.ledger.all()
        if not facts:
            return "ledger empty: assert facts before computing"
        lines = [f.describe() for f in facts]
        return f"{len(lines)} entries (facts and derived results)\n" + "\n".join(
            lines
        )
