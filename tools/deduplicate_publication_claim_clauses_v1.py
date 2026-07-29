#!/usr/bin/env python3
"""Move verbatim repeated claim prose into traceable shared-clause appendices.

The transformation never deletes wording: each selected paragraph is retained
once, verbatim, in the same paper and every former occurrence becomes a stable
clause reference. Literal identifiers, hashes, sources, lists, tables, code and
short phrases are excluded.
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPENDIX = "## Shared claim-record clauses"


@dataclass(frozen=True)
class Target:
    code: str
    path: str


TARGETS = (
    Target("MATH", "publications/successors/mathematics/FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_5.md"),
    Target("INFO", "publications/successors/information_science/FROM_DISTINCTION_TO_INFORMATION_PAPER_001_V1_4.md"),
    Target("COMP", "publications/successors/computation/AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_4.md"),
    Target("QUANT", "publications/successors/quantum_computation/THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_4.md"),
    Target("PHYS", "publications/successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_3.md"),
    Target("CHEM", "publications/successors/chemistry/FROM_FOLD_TO_CHEMISTRY_PAPER_001_V1_3.md"),
    Target("MAT", "publications/successors/materials/FROM_FOLD_TO_MATERIALS_PAPER_001_V1_3.md"),
)


def normal(paragraph: str) -> str:
    return " ".join(paragraph.split())


def eligible(paragraph: str) -> bool:
    stripped = paragraph.strip()
    compact = normal(paragraph)
    if len(compact) < 180:
        return False
    if stripped.startswith(("#", "|", "- ", "* ", ">", "```", "    ")):
        return False
    if "```" in stripped:
        return False
    if re.search(r"\bSFT-[A-Z0-9-]+\b", stripped):
        return False
    if re.search(r"sha256:|https?://|10\.5281/zenodo\.", stripped, re.IGNORECASE):
        return False
    return True


def paragraph_map(text: str) -> tuple[list[str], dict[str, list[int]]]:
    parts = re.split(r"(\n\s*\n)", text)
    locations: dict[str, list[int]] = defaultdict(list)
    fenced = False
    for index in range(0, len(parts), 2):
        paragraph = parts[index]
        fence_count = paragraph.count("```")
        if not fenced and eligible(paragraph):
            locations[normal(paragraph)].append(index)
        if fence_count % 2:
            fenced = not fenced
    return parts, locations


def selected_clauses(text: str) -> list[tuple[str, list[int]]]:
    _, locations = paragraph_map(text)
    selected = [
        (paragraph, indices)
        for paragraph, indices in locations.items()
        if len(indices) >= 8
    ]
    return sorted(selected, key=lambda item: item[1][0])


def report() -> None:
    for target in TARGETS:
        path = ROOT / target.path
        text = path.read_text(encoding="utf-8")
        clauses = selected_clauses(text)
        occurrences = sum(len(indices) for _, indices in clauses)
        print(f"{target.code}: {len(clauses)} clauses; {occurrences} occurrences")
        for number, (paragraph, indices) in enumerate(clauses, 1):
            print(
                f"  {target.code}-S{number:03d}: {len(indices)}x - "
                f"{paragraph[:220]}"
            )


def apply_target(target: Target) -> bool:
    path = ROOT / target.path
    text = path.read_text(encoding="utf-8")
    if APPENDIX in text:
        return False
    parts, locations = paragraph_map(text)
    clauses = [
        (paragraph, indices)
        for paragraph, indices in locations.items()
        if len(indices) >= 8
    ]
    clauses.sort(key=lambda item: item[1][0])
    if not clauses:
        return False

    appendix = [
        APPENDIX,
        "",
        "The clauses below previously appeared verbatim in multiple claim records.",
        "They are preserved once here to reduce mechanical repetition. Each in-text",
        "clause reference applies this exact wording at that claim location; no",
        "scientific statement, status, condition or qualification has been removed.",
        "",
    ]
    for number, (paragraph, indices) in enumerate(clauses, 1):
        clause_id = f"{target.code}-S{number:03d}"
        reference = (
            f"**Shared claim-record clause `{clause_id}` applies.** "
            "The full, unchanged clause is preserved in the shared-clause appendix."
        )
        for index in indices:
            parts[index] = reference
        appendix.extend(
            [
                f"### `{clause_id}` — applied at {len(indices)} claim locations",
                "",
                paragraph,
                "",
            ]
        )

    revised = "".join(parts)
    reference_heading = list(re.finditer(r"(?m)^## References(?:\b| and)", revised))
    if not reference_heading:
        raise SystemExit(f"no References heading in {target.path}")
    insertion = reference_heading[-1].start()
    revised = revised[:insertion] + "\n".join(appendix) + "\n" + revised[insertion:]
    path.write_text(revised, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.apply:
        report()
        return
    changed = sum(apply_target(target) for target in TARGETS)
    print(f"shared-clause deduplication v1: updated {changed} paper(s)")


if __name__ == "__main__":
    main()
