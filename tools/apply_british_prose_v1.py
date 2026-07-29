#!/usr/bin/env python3
"""Apply British spelling only to clearly human-readable publication prose.

Exact claim records, identifiers, hashes, source material, quotations, code,
tables containing machine identities and shared clauses moved verbatim from
claim records are preserved for review rather than changed automatically.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPERS = (
    "publications/successors/mathematics/FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_5.md",
    "publications/successors/information_science/FROM_DISTINCTION_TO_INFORMATION_PAPER_001_V1_4.md",
    "publications/successors/computation/AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_4.md",
    "publications/successors/quantum_computation/THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_4.md",
    "publications/successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_3.md",
    "publications/successors/chemistry/FROM_FOLD_TO_CHEMISTRY_PAPER_001_V1_3.md",
    "publications/successors/materials/FROM_FOLD_TO_MATERIALS_PAPER_001_V1_3.md",
)


SPELLINGS = {
    "analyze": "analyse",
    "analyzed": "analysed",
    "analyzing": "analysing",
    "behavior": "behaviour",
    "behaviors": "behaviours",
    "centered": "centred",
    "color": "colour",
    "colors": "colours",
    "favor": "favour",
    "favored": "favoured",
    "favorable": "favourable",
    "favorably": "favourably",
    "unfavorable": "unfavourable",
    "unfavorably": "unfavourably",
    "finalize": "finalise",
    "finalized": "finalised",
    "generalize": "generalise",
    "generalized": "generalised",
    "harmonize": "harmonise",
    "labeled": "labelled",
    "modeling": "modelling",
    "normalize": "normalise",
    "normalized": "normalised",
    "organization": "organisation",
    "organizations": "organisations",
    "organize": "organise",
    "organized": "organised",
    "parameterization": "parameterisation",
    "recognized": "recognised",
    "standardize": "standardise",
    "standardized": "standardised",
    "summarize": "summarise",
    "summarized": "summarised",
    "utilize": "use",
    "utilized": "used",
}


PROTECTED_RECORD_MARKERS = re.compile(
    r"(?i)(?:"
    r"\*\*(?:exact statement|statement|claim|question|why|derivation|check|"
    r"generated grammar|axis-by-axis|candidate|decision|survivor|closure|"
    r"base and successor|falsification|controls?|source|evidence|chronology|"
    r"formal status|empirical status|independent reconstruction|meaning|"
    r"scientific meaning|what it means|post-seal|external empirical|"
    r"receipt|machine identit)[^*]*\*\*"
    r"|Claim ID:|Source ID:|Receipt ID:|Family: `|Obligation: `|Field: `"
    r")"
)
LITERAL_SIGNAL = re.compile(
    r"SFT-[A-Z0-9-]+|sha256:|https?://|10\.5281/zenodo\.|"
    r"prediction_seal|receipt_hash|claim_id|source_id"
)
TOKEN = re.compile(
    "|".join(rf"\b{re.escape(word)}\b" for word in sorted(SPELLINGS, key=len, reverse=True)),
    re.IGNORECASE,
)
PROTECTED_INLINE = re.compile(r"(`[^`]*`|https?://\S+|\]\([^)]*\))")


def preserve_case(source: str, replacement: str) -> str:
    if source.isupper():
        return replacement.upper()
    if source[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def replace_segment(segment: str, changed: Counter) -> str:
    def repl(match: re.Match[str]) -> str:
        source = match.group(0)
        target = SPELLINGS[source.lower()]
        changed[f"{source.lower()}->{target}"] += 1
        return preserve_case(source, target)

    return TOKEN.sub(repl, segment)


def replace_safe_prose(paragraph: str, changed: Counter) -> str:
    parts = PROTECTED_INLINE.split(paragraph)
    for index in range(0, len(parts), 2):
        parts[index] = replace_segment(parts[index], changed)
    return "".join(parts)


def protected(paragraph: str, after_references: bool, in_fence: bool) -> bool:
    stripped = paragraph.strip()
    if in_fence or after_references:
        return True
    if not stripped:
        return True
    if stripped.startswith((">", "```", "    ")):
        return True
    if "## Shared claim-record clauses" in stripped:
        return True
    if PROTECTED_RECORD_MARKERS.search(stripped):
        return True
    if LITERAL_SIGNAL.search(stripped):
        return True
    return False


def process(path: Path, apply: bool) -> dict:
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"(\n\s*\n)", text)
    changed: Counter = Counter()
    preserved: Counter = Counter()
    after_references = False
    in_fence = False

    for index in range(0, len(parts), 2):
        paragraph = parts[index]
        if re.search(r"(?m)^## References(?:\b| and)", paragraph):
            after_references = True
        fence_count = paragraph.count("```")
        is_protected = protected(paragraph, after_references, in_fence)
        matches = TOKEN.findall(paragraph)
        if is_protected:
            preserved.update(word.lower() for word in matches)
        else:
            parts[index] = replace_safe_prose(paragraph, changed)
        if fence_count % 2:
            in_fence = not in_fence

    revised = "".join(parts)
    if apply:
        path.write_text(revised, encoding="utf-8")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "safe_changes": dict(sorted(changed.items())),
        "protected_for_manual_or_literal_review": dict(sorted(preserved.items())),
        "safe_change_count": sum(changed.values()),
        "protected_occurrence_count": sum(preserved.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    reports = [process(ROOT / paper, args.apply) for paper in PAPERS]
    result = {
        "schema": "sft-v3-british-prose-editorial-pass/1",
        "applied": args.apply,
        "papers": reports,
        "summary": {
            "safe_changes": sum(item["safe_change_count"] for item in reports),
            "protected_occurrences": sum(
                item["protected_occurrence_count"] for item in reports
            ),
        },
    }
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        destination = args.json_out
        if not destination.is_absolute():
            destination = ROOT / destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    action = "applied" if args.apply else "proposed"
    print(
        f"British prose v1 {action}: {result['summary']['safe_changes']} safe "
        f"changes; {result['summary']['protected_occurrences']} protected occurrences"
    )


if __name__ == "__main__":
    main()
