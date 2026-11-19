"""WRITE: deterministic deliverable text from the ledger.

The model specifies structure and prose; every number enters through a
placeholder such as {F1} or {K1.Mmax_kNm}, so a deliverable cannot contain a
number that is not already a ledger fact. A Sources table is appended so each
substituted value keeps its provenance in the document itself.
"""

import re

from harness.spec import SpecError

PLACEHOLDER = re.compile(r"\{([A-Za-z0-9_.:\-]+)\}")


def _fmt(value: float) -> str:
    return f"{value:.6g}"


def _with_unit(fact) -> str:
    if fact.unit == "-":
        return _fmt(fact.value)
    if fact.unit == "%":
        return f"{_fmt(fact.value)} %"
    return f"{_fmt(fact.value)} {fact.unit}"


def render(book, title, sections) -> dict:
    """Render markdown from ledger facts and a section specification.

    sections: [{heading, body}] where body is a string or a list of
    paragraphs and may hold {fid} placeholders. Unknown placeholders are an
    error, not an empty string: a missing fact must be fixed upstream.
    """
    ledger = book.ledger
    if not isinstance(sections, list) or not sections:
        raise SpecError("sections must be a non-empty array of {heading, body}")
    used = []

    def substitute(match):
        fid = match.group(1).strip()
        fact = ledger.get(fid)
        if fact is None:
            raise SpecError(f"placeholder {{{fid}}} is not a ledger fact")
        if fid not in used:
            used.append(fid)
        return f"{_with_unit(fact)} [{fid}]"

    lines = [f"# {str(title).strip()}".rstrip()]
    for n, section in enumerate(sections):
        if not isinstance(section, dict) or "heading" not in section:
            raise SpecError(f"sections[{n}] must be an object with a heading")
        lines += ["", f"## {section['heading']}"]
        body = section.get("body", "")
        if isinstance(body, str):
            body = [body]
        if not isinstance(body, list):
            raise SpecError(
                f"sections[{n}].body must be a string or an array of strings"
            )
        for paragraph in body:
            if not isinstance(paragraph, str):
                raise SpecError(f"sections[{n}].body must contain strings")
            lines += ["", PLACEHOLDER.sub(substitute, paragraph)]
    if used:
        lines += [
            "",
            "## Sources",
            "",
            "| id | value | unit | provenance |",
            "|---|---|---|---|",
        ]
        for fid in used:
            fact = ledger.get(fid)
            lines.append(
                f"| {fid} | {_fmt(fact.value)} | {fact.unit} | {fact.source} |"
            )
    return {"text": "\n".join(lines) + "\n", "used": used}
