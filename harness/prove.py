"""PROVE: a deliverable may not contain a number the ledger cannot vouch for.

Minimal linter: extract numbers from the text, match each against the ledger
within a relative tolerance, and report the ones with no fact behind them.
Identifiers (F1, K1.Mmax_kNm, S-101, 2D), markdown headings and the generated
Sources table are not treated as results.
"""

import re

# A number not glued to letters, digits, dots or hyphens: F1, S-101, K1.5 and
# 2D are identifiers, not values.
NUM = re.compile(
    r"(?<![\w.\-])[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?(?![\w])"
)
CONTEXT = 40


def extract(text: str) -> list:
    """Every numeric candidate with its position, spelling and context."""
    out = []
    text = text or ""
    for match in NUM.finditer(text):
        raw = match.group(0)
        try:
            value = float(raw)
        except ValueError:
            continue
        start = max(0, match.start() - CONTEXT)
        end = min(len(text), match.end() + CONTEXT)
        out.append(
            {
                "value": value,
                "text": raw,
                "start": match.start(),
                "context": " ".join(text[start:end].split()),
            }
        )
    return out


def _body(text: str) -> str:
    """Text before the generated Sources table, which is ledger output."""
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("## Sources"):
            return text[: text.find(line)]
    return text


def trace(ledger, text: str, rel_tol: float = 0.005) -> dict:
    """Match every number in `text` to a fact or a derived result."""
    facts = ledger.all()
    body = _body(text or "")
    checks = []
    for item in extract(body):
        line_start = body.rfind("\n", 0, item["start"]) + 1
        if body[line_start:].lstrip().startswith("#"):
            continue  # heading numbering is structure, not a result
        match = None
        for fact in facts:
            scale = max(abs(fact.value), 1e-12)
            if abs(item["value"] - fact.value) <= rel_tol * scale:
                match = fact.fid
                break
        checks.append({**item, "fact": match})
    untraceable = [c for c in checks if c["fact"] is None]
    return {
        "numbers": len(checks),
        "untraceable": untraceable,
        "traceable": not untraceable,
    }
