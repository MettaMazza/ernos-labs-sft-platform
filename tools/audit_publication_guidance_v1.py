#!/usr/bin/env python3
"""Audit the seven complete-field papers against publication guidance v1.

This is a read-only editorial gate. It reads every manuscript byte, compares
the claim-ID surface with the live census, and reports structural, style,
Markdown, repetition and terminology-review findings. It does not infer or
change scientific status and is intentionally separate from protected
scientific verification authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Paper:
    branch: str
    label: str
    path: str
    version: str
    published_doi: str
    claims: int
    candidates: int
    survivors: int
    controls: int


PAPERS = (
    Paper(
        "mathematics",
        "Mathematics",
        "publications/successors/mathematics/"
        "FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_5.md",
        "1.5.0",
        "10.5281/zenodo.21627708",
        323,
        97_280,
        323,
        1_292,
    ),
    Paper(
        "information_science",
        "Information Science",
        "publications/successors/information_science/"
        "FROM_DISTINCTION_TO_INFORMATION_PAPER_001_V1_4.md",
        "1.4.0",
        "10.5281/zenodo.21627717",
        262,
        75_776,
        262,
        1_048,
    ),
    Paper(
        "computation",
        "Classical Computation",
        "publications/successors/computation/"
        "AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_4.md",
        "1.4.0",
        "10.5281/zenodo.21627721",
        369,
        94_464,
        369,
        1_476,
    ),
    Paper(
        "quantum_computation",
        "Reversible and Quantum Computation",
        "publications/successors/quantum_computation/"
        "THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_4.md",
        "1.4.0",
        "10.5281/zenodo.21627748",
        288,
        73_728,
        288,
        1_152,
    ),
    Paper(
        "physics",
        "Physics",
        "publications/successors/physics/"
        "FROM_FOLD_TO_PHYSICS_PAPER_001_V1_3.md",
        "1.3.0",
        "10.5281/zenodo.21627765",
        368,
        94_208,
        368,
        1_472,
    ),
    Paper(
        "chemistry",
        "Chemistry",
        "publications/successors/chemistry/"
        "FROM_FOLD_TO_CHEMISTRY_PAPER_001_V1_3.md",
        "1.3.0",
        "10.5281/zenodo.21627782",
        281,
        71_936,
        281,
        1_124,
    ),
    Paper(
        "materials",
        "Materials Science",
        "publications/successors/materials/"
        "FROM_FOLD_TO_MATERIALS_PAPER_001_V1_3.md",
        "1.3.0",
        "10.5281/zenodo.21629306",
        289,
        73_984,
        289,
        1_156,
    ),
)


REQUIRED_SURFACES = {
    "title": r"(?m)^#\s+\S",
    "authorship": r"Maria Smith",
    "affiliation": r"Ernos Labs|Independent researcher",
    "version": r"\b[Vv]ersion\b",
    "date": r"\b(?:[0-3]?\d) (?:January|February|March|April|May|June|July|August|September|October|November|December) 20\d{2}\b",
    "doi": r"10\.5281/zenodo\.\d+|DOI[^\n]{0,40}pending",
    "licence_and_status": r"CC BY 4\.0|licen[cs]e",
    "abstract": r"(?im)^#{1,4}\s+Abstract\b",
    "headline_findings": r"(?im)^#{1,4}\s+.*(?:Results first|Headline findings)",
    "scope": r"(?i)\bscope\b|\bboundary\b",
    "ownership": r"(?i)\bownership\b|\bone-owner\b",
    "mathematical_constitution": r"(?i)mathematical constitution|formal constitution|derivation",
    "empirical_constitution": r"(?i)empirical constitution|evidence constitution|empirical protocol",
    "chronology": r"(?i)blind-order|chronology|post-seal|prospective|retrospective",
    "dependency_structure": r"(?i)dependency (?:structure|route|graph|order)",
    "source_surface": r"(?i)registered source|source surface|source identit|source manifest",
    "family_results": r"(?i)family results|family census|dependency-ordered famil",
    "major_derivations": r"(?i)major derivation|lead derivation|derivation ledger",
    "major_evidence_tests": r"(?i)evidence test|empirical test|validation vector|adverse control",
    "corrections_and_adverse": r"(?i)correction|adverse result|unfavourable|unfavorable",
    "claim_inventory": r"(?i)complete claim inventory|claim inventory|claim-level",
    "historical_reconciliation": r"(?i)historical reconciliation|reconciliation",
    "limitations": r"(?im)^#{1,4}\s+.*Limitations?\b|\blimitation\b",
    "open_frontier": r"(?i)open frontier|extension-open|open to lawful extension",
    "reproducibility": r"(?i)reproducib|independent reconstruction|replay",
    "conclusion": r"(?im)^#{1,4}\s+.*Conclusion\b",
    "data_and_code": r"(?i)data and code availability|code availability|data availability",
    "references": r"(?im)^#{1,4}\s+.*References?\b",
    "machine_identities": r"(?i)machine-identit|machine identit|receipt identit|SHA-256",
}


AMERICAN_TO_BRITISH = {
    "analyze": "analyse",
    "analyzed": "analysed",
    "behavior": "behaviour",
    "behaviors": "behaviours",
    "categorize": "categorise",
    "categorized": "categorised",
    "centered": "centred",
    "color": "colour",
    "colors": "colours",
    "favor": "favour",
    "favorable": "favourable",
    "favorably": "favourably",
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


EVIDENCE_VERBS = (
    "prove",
    "proves",
    "proved",
    "derive",
    "derives",
    "derived",
    "demonstrate",
    "demonstrates",
    "predict",
    "predicts",
    "validate",
    "validates",
    "verify",
    "verifies",
    "confirm",
    "confirms",
    "match",
    "matches",
    "support",
    "supports",
    "establish",
    "establishes",
    "show",
    "shows",
    "close",
    "closes",
    "complete",
    "completes",
)


CLAIM_ID = re.compile(r"\bSFT-[A-Z0-9]+(?:-[A-Z0-9]+)+\b")
INLINE_CODE = re.compile(r"`[^`]*`")
LINK_DESTINATION = re.compile(r"\]\((?:[^()]|\([^()]*\))*\)")
URL = re.compile(r"https?://\S+")


def prose_lines(text: str) -> Iterable[tuple[int, str]]:
    """Yield non-fenced prose with literal fields masked."""
    fenced = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        masked = INLINE_CODE.sub("<LITERAL>", line)
        masked = LINK_DESTINATION.sub("](<LINK>)", masked)
        masked = URL.sub("<URL>", masked)
        yield number, masked


def line_refs(matches: list[tuple[int, str]], limit: int = 25) -> dict:
    return {
        "count": len(matches),
        "examples": [
            {"line": number, "text": text.strip()[:240]}
            for number, text in matches[:limit]
        ],
    }


def markdown_links(text: str, paper_path: Path) -> list[dict]:
    broken = []
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).strip().split(maxsplit=1)[0].strip("<>")
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        clean = target.split("#", 1)[0]
        candidate = (paper_path.parent / clean).resolve()
        if not candidate.exists():
            broken.append({"target": target, "offset": match.start()})
    return broken


def repeated_paragraphs(text: str) -> list[dict]:
    paragraphs = re.split(r"\n\s*\n", text)
    locations: dict[str, list[int]] = defaultdict(list)
    for index, paragraph in enumerate(paragraphs, 1):
        normal = " ".join(paragraph.split())
        if len(normal) >= 180 and not normal.startswith(("|", "```")):
            locations[normal].append(index)
    repeated = [
        {"occurrences": len(indices), "paragraphs": indices, "text": text[:240]}
        for text, indices in locations.items()
        if len(indices) > 1
    ]
    return sorted(repeated, key=lambda item: (-item["occurrences"], item["text"]))


def table_shape_findings(text: str) -> list[dict]:
    findings = []
    block: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines() + [""], 1):
        if line.lstrip().startswith("|"):
            block.append((number, line))
            continue
        if len(block) >= 2:
            widths = Counter(row.count("|") for _, row in block)
            dominant, _ = widths.most_common(1)[0]
            for row_number, row in block:
                if row.count("|") != dominant:
                    findings.append(
                        {
                            "line": row_number,
                            "pipes": row.count("|"),
                            "expected_pipes": dominant,
                            "text": row[:240],
                        }
                    )
        block = []
    return findings


def audit_paper(paper: Paper, census_ids: set[str]) -> dict:
    path = ROOT / paper.path
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    lines = text.splitlines()
    prose = list(prose_lines(text))
    prose_text = "\n".join(line for _, line in prose)

    paper_ids = set(CLAIM_ID.findall(text))
    missing_ids = sorted(census_ids - paper_ids)
    extra_ids = sorted(paper_ids - census_ids)

    required = {
        name: bool(re.search(pattern, text))
        for name, pattern in REQUIRED_SURFACES.items()
    }

    british_findings = {}
    for american, british in AMERICAN_TO_BRITISH.items():
        pattern = re.compile(rf"\b{re.escape(american)}\b", re.IGNORECASE)
        matches = [
            (number, line)
            for number, line in prose
            if pattern.search(line)
        ]
        if matches:
            british_findings[american] = {
                "preferred": british,
                **line_refs(matches),
            }

    verb_findings = {}
    for verb in EVIDENCE_VERBS:
        pattern = re.compile(rf"\b{re.escape(verb)}\b", re.IGNORECASE)
        matches = [
            (number, line)
            for number, line in prose
            if pattern.search(line)
        ]
        if matches:
            verb_findings[verb] = line_refs(matches, limit=10)

    iso_dates = [
        (number, line)
        for number, line in prose
        if re.search(r"\b20\d{2}-[01]\d-[0-3]\d\b", line)
    ]
    long_prose = [
        (number, line)
        for number, line in prose
        if len(line) > 300 and not line.lstrip().startswith("|")
    ]
    trailing = [
        (number, line)
        for number, line in enumerate(lines, 1)
        if line.rstrip() != line
    ]

    expected_numbers = {
        "claims": paper.claims,
        "candidates": paper.candidates,
        "survivors": paper.survivors,
        "controls": paper.controls,
    }
    number_presence = {
        name: bool(
            re.search(
                rf"(?<!\d){value:,}(?!\d)|(?<!\d){value}(?!\d)",
                text,
            )
        )
        for name, value in expected_numbers.items()
    }

    hard_failures = []
    if len(census_ids) != paper.claims:
        hard_failures.append(
            f"live census has {len(census_ids)} claims; expected {paper.claims}"
        )
    if missing_ids:
        hard_failures.append(f"paper omits {len(missing_ids)} live claim IDs")
    if any(not value for value in number_presence.values()):
        hard_failures.append("one or more headline totals are absent")
    absent_surfaces = [name for name, present in required.items() if not present]
    if absent_surfaces:
        hard_failures.append(
            "required publication surfaces absent: " + ", ".join(absent_surfaces)
        )
    if text.count("```") % 2:
        hard_failures.append("unbalanced fenced-code delimiters")

    return {
        "branch": paper.branch,
        "label": paper.label,
        "path": paper.path,
        "candidate_version": paper.version,
        "current_published_doi": paper.published_doi,
        "sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "lines": len(lines),
        "words": len(re.findall(r"\S+", text)),
        "headings": [
            {"line": number, "heading": line}
            for number, line in enumerate(lines, 1)
            if re.match(r"^#{1,6}\s+", line)
        ],
        "expected_totals": expected_numbers,
        "headline_total_presence": number_presence,
        "live_census_claim_ids": len(census_ids),
        "live_claim_ids_missing_from_paper": missing_ids,
        "other_branch_or_historical_claim_ids_in_paper": extra_ids,
        "required_surfaces": required,
        "british_english_review": british_findings,
        "iso_human_date_review": line_refs(iso_dates),
        "evidence_verb_review": verb_findings,
        "trailing_whitespace": line_refs(trailing),
        "long_prose_lines": line_refs(long_prose),
        "broken_relative_links": markdown_links(text, path),
        "table_shape_findings": table_shape_findings(text),
        "repeated_paragraphs": repeated_paragraphs(text),
        "hard_failures": hard_failures,
        "status": "PASS" if not hard_failures else "REQUIRES_REVISION",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    claims_data = json.loads((ROOT / "census/claims.json").read_text())
    claims = claims_data if isinstance(claims_data, list) else claims_data["claims"]
    by_branch: dict[str, set[str]] = defaultdict(set)
    for claim in claims:
        if claim.get("model_admitted"):
            by_branch[claim["branch"]].add(claim["claim_id"])

    reports = [audit_paper(paper, by_branch[paper.branch]) for paper in PAPERS]
    result = {
        "schema": "sft-v3-publication-guidance-editorial-audit/1",
        "guidance": "publication guidance.md",
        "scope": "seven complete field-wide successor papers",
        "papers": reports,
        "summary": {
            "papers": len(reports),
            "passes": sum(report["status"] == "PASS" for report in reports),
            "requires_revision": sum(
                report["status"] != "PASS" for report in reports
            ),
            "bytes_read": sum(report["bytes"] for report in reports),
            "lines_read": sum(report["lines"] for report in reports),
            "words_read": sum(report["words"] for report in reports),
        },
    }
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        destination = args.json_out
        if not destination.is_absolute():
            destination = ROOT / destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered)
    else:
        print(rendered, end="")

    print(
        f"publication guidance audit: {result['summary']['passes']}/"
        f"{result['summary']['papers']} pass; "
        f"{result['summary']['lines_read']:,} lines read"
    )
    return 0 if result["summary"]["requires_revision"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
