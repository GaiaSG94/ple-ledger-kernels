"""Typed engineering facts with provenance, the substrate the LLM specifies against."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Fact:
    fid: str
    kind: str
    value: float
    unit: str
    source: str
    label: str = ""
    confidence: float = 1.0

    def describe(self) -> str:
        return f"[{self.fid}] {self.label or self.kind} = {self.value} {self.unit} ({self.source})"


class Ledger:
    """Collection of typed facts; ids are unique and cited everywhere downstream."""

    def __init__(self):
        self._facts: dict[str, Fact] = {}

    def add(self, fact: Fact) -> None:
        if fact.fid in self._facts:
            raise ValueError(f"duplicate fact id: {fact.fid}")
        self._facts[fact.fid] = fact

    def get(self, fid: str) -> Optional[Fact]:
        return self._facts.get(fid)

    def all(self) -> list[Fact]:
        return list(self._facts.values())

    def by_kind(self, kind: str) -> list[Fact]:
        return [f for f in self._facts.values() if f.kind == kind]

    def as_context(self) -> str:
        lines = [f.describe() for f in self._facts.values()]
        return "\n".join(lines)
