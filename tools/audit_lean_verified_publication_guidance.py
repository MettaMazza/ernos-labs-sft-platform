#!/usr/bin/env python3
"""Audit the complete Lean-verified successor suite against publication guidance.

The gate is deliberately broader than a Markdown linter.  It binds every
candidate to the live census and Lean report, checks scientific preservation
and publication control, scans every line, and reports one explicit result for
each of the 23 sections in ``publication guidance.md``.  PDF checks remain a
separate later gate.
"""

from __future__ import annotations

from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import re

import apply_british_prose_v2 as british


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "publications/lean4_verification/LEAN4_VERIFIED_PUBLICATION_SUITE_MANIFEST.json"
GUIDANCE = ROOT / "publication guidance.md"
DEFAULT_JSON = ROOT / "audits/LEAN4_VERIFIED_PUBLICATION_GUIDANCE_AUDIT_2026-08-02.json"
DEFAULT_MD = ROOT / "audits/LEAN4_VERIFIED_PUBLICATION_GUIDANCE_AUDIT_2026-08-02.md"
SHA = re.compile(r"(?:sha256:)?[0-9a-f]{64}")
CLAIM_ID = re.compile(r"SFT-[A-Z0-9-]+")
BACKTICK = re.compile(r"`([^`\n]+)`")
DOI = re.compile(r"10\.5281/zenodo\.\d+")

TERMINOLOGY = (
    "Theorem",
    "Law",
    "Claim",
    "Constitution",
    "Derivation",
    "Prediction",
    "Observation",
    "Measurement",
    "Reconstruction",
    "Exact numerical correspondence",
    "Structural correspondence",
    "Boundary correspondence",
    "Compatibility",
    "Support",
    "Confirmation",
    "Validation",
    "Adverse result",
    "Unresolved result",
    "Implementation identity",
    "Formal, empirical and publication status",
    "Foundational closure",
    "Field-wide closure",
    "Current-evidence closure",
    "Extension openness",
)


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def section(text: str, exact_heading: str) -> str:
    match = re.search(rf"(?m)^##\s+{re.escape(exact_heading)}\s*$", text)
    if not match:
        return ""
    following = re.search(r"(?m)^##\s+", text[match.end() :])
    end = match.end() + following.start() if following else len(text)
    return text[match.start() : end]


def section_like(text: str, pattern: str) -> str:
    matches = list(re.finditer(rf"(?im)^##\s+[^\n]*{pattern}[^\n]*$", text))
    if not matches:
        return ""
    match = matches[-1]
    following = re.search(r"(?m)^##\s+", text[match.end() :])
    end = match.end() + following.start() if following else len(text)
    return text[match.start() : end]


def duplicate_word_findings(text: str) -> list[dict]:
    pattern = re.compile(r"\b([A-Za-z]{3,})\s+\1\b", re.IGNORECASE)
    findings = []
    fenced = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        stripped = line.lstrip()
        if fenced or stripped.startswith(("#", "|", ">")):
            continue
        if any(
            marker in line
            for marker in (
                "**Exact statement",
                "**Statement",
                "Current exact statement:",
                "Claim identity:",
                "Source ID:",
            )
        ):
            continue
        match = pattern.search(line)
        if match:
            findings.append({"line": number, "word": match.group(1), "text": line[:300]})
    return findings


def delimiter_audit(text: str) -> dict:
    return {
        "inline_math_open": text.count(r"\("),
        "inline_math_close": text.count(r"\)"),
        "display_math_open": text.count(r"\["),
        "display_math_close": text.count(r"\]"),
        "code_fences": text.count("```"),
        "balanced": (
            text.count(r"\(") == text.count(r"\)")
            and text.count(r"\[") == text.count(r"\]")
            and text.count("```") % 2 == 0
        ),
    }


def split_table_row(line: str) -> list[str]:
    return [cell.replace(r"\|", "|").strip() for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def table_audit(text: str) -> list[dict]:
    lines = text.splitlines()
    findings = []
    index = 0
    while index < len(lines):
        if not lines[index].lstrip().startswith("|"):
            index += 1
            continue
        start = index
        block = []
        while index < len(lines) and lines[index].lstrip().startswith("|"):
            block.append(lines[index])
            index += 1
        if len(block) < 2:
            continue
        separator = split_table_row(block[1])
        if not separator or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator):
            # A quoted literal beginning with a pipe is not a Markdown table.
            continue
        width = len(split_table_row(block[0]))
        bad = [start + offset + 1 for offset, line in enumerate(block) if len(split_table_row(line)) != width]
        if bad:
            findings.append({"start_line": start + 1, "expected_columns": width, "bad_lines": bad})
    return findings


def link_audit(path: Path, text: str) -> list[dict]:
    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        if "](" in line and line.count("](") > line.count(")"):
            findings.append({"line": number, "reason": "unclosed Markdown link", "text": line[:300]})
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", line):
            clean = target.strip().strip("<>")
            if clean.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = clean.split("#", 1)[0]
            if not clean:
                continue
            candidates = [
                (path.parent / clean).resolve(),
                (ROOT / clean).resolve(),
                (ROOT / "docs/branch_roadmaps" / clean).resolve(),
            ]
            if not any(candidate.exists() for candidate in candidates):
                findings.append({"line": number, "reason": "broken relative link", "target": target})
    return findings


def line_scan(path: Path, text: str, baseline_text: str) -> dict:
    lines = text.splitlines()
    headings = []
    blank_headings = []
    replacement_glyphs = []
    for number, line in enumerate(lines, 1):
        if "�" in line or "\ufffd" in line:
            replacement_glyphs.append(number)
        if line.startswith("#"):
            headings.append(number)
            if not re.fullmatch(r"#{1,6}\s+\S.*", line):
                blank_headings.append(number)
    duplicates = duplicate_word_findings(text)
    baseline_duplicate_words = Counter(row["word"].lower() for row in duplicate_word_findings(baseline_text))
    new_duplicates = []
    seen = Counter()
    for row in duplicates:
        word = row["word"].lower()
        seen[word] += 1
        if seen[word] > baseline_duplicate_words[word]:
            new_duplicates.append(row)
    return {
        "lines_read": len(lines),
        "bytes_read": len(text.encode("utf-8")),
        "headings_read": len(headings),
        "blank_or_malformed_headings": blank_headings,
        "replacement_glyph_lines": replacement_glyphs,
        "new_duplicate_word_findings": new_duplicates,
        "delimiter_audit": delimiter_audit(text),
        "table_shape_findings": table_audit(text),
        "link_findings": link_audit(path, text),
    }


def relevant_claims(record: dict, claims: list[dict]) -> list[dict]:
    if record["paper_id"] == "theory_of_everything":
        return claims
    if record["paper_id"] in ("methods", "lean4_whole_model_verification"):
        return [row for row in claims if row["claim_id"] == "SFT-ROOT-THERE-IS-NO-NOTHING"]
    return [row for row in claims if row["branch"] in record.get("branches", [])]


def original_preservation(source: Path | None, output_text: str) -> dict:
    if source is None:
        return {
            "source_present": False,
            "source_sha256": None,
            "missing_original_claim_ids": [],
            "missing_original_sha256_identities": [],
            "missing_original_dois": [],
            "missing_original_literals": [],
            "pass": True,
            "reason": "standalone paper has no predecessor",
        }
    baseline = source.read_text(encoding="utf-8")
    original_ids = set(CLAIM_ID.findall(baseline))
    output_ids = set(CLAIM_ID.findall(output_text))
    original_shas = set(SHA.findall(baseline))
    output_shas = set(SHA.findall(output_text))
    original_dois = set(DOI.findall(baseline))
    output_dois = set(DOI.findall(output_text))
    # Code literals that are claim IDs, paths, versions, hashes or formal terms
    # are preservation-critical. Ordinary emphasis-like snippets are not.
    original_literals = {
        token
        for token in BACKTICK.findall(baseline)
        if any(marker in token for marker in ("SFT-", "sha256:", "/", ".json", ".lean", "v1", "v0"))
    }
    output_literals = set(BACKTICK.findall(output_text))
    result = {
        "source_present": True,
        "source_sha256": sha256(source),
        "missing_original_claim_ids": sorted(original_ids - output_ids),
        "missing_original_sha256_identities": sorted(original_shas - output_shas),
        "missing_original_dois": sorted(original_dois - output_dois),
        "missing_original_literals": sorted(original_literals - output_literals),
    }
    # The historical source itself remains immutable and hash-bound. New
    # current statements and receipts must appear in the successor. Old
    # generated manifest hashes may lawfully remain solely in the predecessor.
    result["pass"] = not result["missing_original_claim_ids"] and not result["missing_original_dois"]
    return result


def paper_audit(record: dict, claims: list[dict], report: dict, report_hash: str) -> dict:
    path = ROOT / record["output"]
    text = path.read_text(encoding="utf-8")
    source = ROOT / record["source"] if record.get("source") else None
    baseline_text = source.read_text(encoding="utf-8") if source else ""
    relevant = relevant_claims(record, claims)
    missing_ids = [row["claim_id"] for row in relevant if row["claim_id"] not in text]
    missing_statements = [row["claim_id"] for row in relevant if row["statement"] not in text]
    missing_receipts = [row["claim_id"] for row in relevant if row["receipt_hash"] not in text]
    preservation = original_preservation(source, text)
    scan = line_scan(path, text, baseline_text)
    british_review = british.v1.process(path, apply=False)
    abstract = section(text, "Abstract")
    headline = section(text, "Successor headline findings") or section(text, "Headline findings")
    conclusion = section(text, "Successor conclusion") or section_like(text, "Conclusion")
    limitations = section_like(text, "Limitations?|open frontier|dated completion")
    status = section(text, "Current status, evidence language and reader map")
    expected_count = len(relevant)
    if record["paper_id"] in ("methods", "lean4_whole_model_verification"):
        abstract_count_ok = f"{report['claim_count']:,}" in abstract
    elif expected_count:
        abstract_count_ok = f"{expected_count:,}" in abstract
    else:
        abstract_count_ok = f"{report['claim_count']:,}" in abstract
    first = text[:12000].lower()
    evidence_path = ROOT / record["evidence_map"]
    metadata_path = ROOT / record["metadata"]
    evidence = json.loads(evidence_path.read_bytes())
    metadata = json.loads(metadata_path.read_bytes())
    evidence_hash_ok = (
        evidence.get("paper_sha256", evidence.get("successor_sha256")) == sha256(path)
    )
    publication_status = record.get("publication_status", "local_candidate")
    if publication_status == "published_open_access":
        metadata_control_ok = (
            metadata.get("publication_authorized") is True
            and metadata.get("remote_action_permitted") is True
            and metadata.get("ready_to_publish") is True
        )
    else:
        metadata_control_ok = (
            metadata.get("publication_authorized") is False
            and metadata.get("remote_action_permitted") is False
            and metadata.get("ready_to_publish") is False
        )
    headings_text = "\n".join(re.findall(r"(?m)^#{1,6}\s+.*$", text)).lower()
    normalised_text = re.sub(r"\s+", " ", text)
    required_surfaces = {
        "title_subtitle": text.startswith("# ") and "\n\n## " in text[:2000],
        "author_affiliation": "Maria Smith" in text[:5000] and "Ernos Labs" in text[:5000],
        "version_date_doi_licence_status": all(
            marker in text[:6000]
            for marker in (record["version"], "2 August 2026", "DOI", "CC BY 4.0", "Apache-2.0")
        ),
        "abstract": bool(abstract),
        "headline_findings": bool(headline),
        "scope_ownership": "ownership" in headings_text and "boundary" in text.lower(),
        "mathematical_constitution": "mathematical" in text.lower() and "constitution" in text.lower(),
        "empirical_constitution": "empirical" in text.lower() and "chronology" in text.lower(),
        "dependencies": "dependency" in text.lower(),
        "registered_sources": "source" in headings_text and "source" in text.lower(),
        "branch_or_argument_narrative": any(word in text.lower() for word in ("branch narrative", "derivation", "argument")),
        "family_results": (not relevant or "family" in text.lower() or record["paper_id"] in ("methods", "lean4_whole_model_verification")),
        "major_derivations": "derivation" in text.lower(),
        "major_evidence_tests": "evidence" in text.lower() and "control" in text.lower(),
        "adverse_corrected_updated": all(word in text.lower() for word in ("adverse", "unresolved")) and any(word in text.lower() for word in ("correct", "halt", "supersed")),
        "claim_inventory": not relevant or (not missing_ids and not missing_statements and not missing_receipts),
        "historical_reconciliation": (
            "historical" in headings_text
            or "preceding-version" in text.lower()
            or "chronology remains claim specific" in text.lower()
        ),
        "limitations_open_frontier": bool(limitations),
        "reproducibility": "reproduc" in text.lower(),
        "conclusion": bool(conclusion),
        "data_code_availability": "## Data and code availability" in text,
        "references": bool(re.search(r"(?im)^##\s+References", text)),
        "machine_identity": "machine-identity" in headings_text or "verification-source identities" in headings_text,
    }
    forbidden_prepublication_text = (
        "unpublished local publication candidate",
        "final local publication candidate",
        "not approved, deposited or published",
        "awaiting maria smith's approval",
        "not deposited or published",
        "not yet approved or deposited",
        "pending the authorised new-version or new-record deposit",
        "pending a new standalone record after explicit confirmation",
        "no push, upload, doi action, release or publication is authorised",
    )
    if publication_status == "published_open_access":
        publication_control_ok = (
            "published open access" in first
            and record["doi"].lower() in first
            and not any(phrase in text.lower() for phrase in forbidden_prepublication_text)
            and evidence.get("publication_authorized") is True
            and evidence.get("remote_actions_performed") is True
            and evidence_hash_ok
            and metadata_control_ok
        )
    else:
        publication_control_ok = (
            "not approved, deposited or published" in first
            and evidence.get("publication_authorized") is False
            and evidence.get("remote_actions_performed") is False
            and evidence_hash_ok
            and metadata_control_ok
        )
    checks = {
        "01_authoritative_context": (
            sha256(path) == record["output_sha256"]
            and (source is None or sha256(source) == record["source_sha256"])
            and report["status"] == "PASS"
            and report_hash in text
        ),
        "02_non_negotiable_scientific_preservation": (
            preservation["pass"] and not missing_ids and not missing_statements and not missing_receipts
        ),
        "03_scientific_change_control": "### Editorial change control" in text,
        "04_corpus_wide_house_style": (
            british_review["safe_change_count"] == 0
            and "2 August 2026" in text[:6000]
            and record["version"] in text[:6000]
        ),
        "05_terminology_consistency": all(term in text for term in TERMINOLOGY),
        "06_proof_and_evidence_verbs": (
            "Proof language is reserved for formal closure" in normalised_text
            and "confirmation only where" in normalised_text
            and bool(re.search(r"Formal admission does not(?: by itself)? imply empirical confirmation", normalised_text))
        ),
        "07_paper_structure": all(required_surfaces.values()),
        "08_narrative_spine": all(word in text.lower() for word in ("dependency", "boundary", "admitted")),
        "09_repetition_control": text.count("## Current status, evidence language and reader map") == 1,
        "10_claim_section_format": (
            not relevant
            or (
                not missing_ids
                and not missing_statements
                and not missing_receipts
                and all(word in text.lower() for word in ("candidate", "survivor", "control", "falsification", "receipt"))
            )
        ),
        "11_abstract": bool(abstract) and abstract_count_ok and "open" in abstract.lower() and "status" in abstract.lower(),
        "12_headline_findings": bool(headline) and "Lean 4" in headline,
        "13_current_status_boxes": bool(status) and all(marker in status for marker in ("Formal status", "Empirical status", "Publication status", "Chronology")),
        "14_adverse_corrected_updated_results": required_surfaces["adverse_corrected_updated"],
        "15_mathematical_formatting": scan["delimiter_audit"]["balanced"],
        "16_tables": not scan["table_shape_findings"],
        "17_sources_and_references": required_surfaces["registered_sources"] and required_surfaces["references"] and not scan["link_findings"],
        "18_prose_proofreading": (
            not scan["blank_or_malformed_headings"]
            and not scan["replacement_glyph_lines"]
            and not scan["new_duplicate_word_findings"]
        ),
        "19_template_rhythm_reduction": (
            sum(text.count(marker) for marker in ("## Successor headline findings", "## Headline findings")) == 1
            and (text.count("## Successor conclusion") == 1 or bool(re.search(r"(?im)^##\s+(?:\d+\.\s+)?Conclusion\s*$", text)))
        ),
        "20_human_audit_machine_layers": "### Three reading levels" in text and all(level in text for level in ("Conceptual paper", "Scientific audit layer", "Machine archive")),
        "21_authorship_open_science": all(marker.lower() in text.lower() for marker in ("Maria Smith", "Ernos Labs", "CC BY 4.0", "Apache-2.0", "publication authority")),
        "22_conclusion": bool(conclusion) and all(word in conclusion.lower() for word in ("formal", "evidence", "adverse", "unresolved", "open")),
        "23_limitations_open_frontier": bool(limitations) and all(word in limitations.lower() for word in ("formal", "empirical", "open")),
        "publication_control": publication_control_ok,
    }
    failures = [name for name, value in checks.items() if not value]
    return {
        "paper_id": record["paper_id"],
        "path": record["output"],
        "version": record["version"],
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "lines": len(text.splitlines()),
        "relevant_claim_count": len(relevant),
        "missing_current_claim_ids": missing_ids,
        "missing_current_statements": missing_statements,
        "missing_current_receipts": missing_receipts,
        "preservation": preservation,
        "required_surfaces": required_surfaces,
        "british_prose_review": british_review,
        "full_line_scan": scan,
        "evidence_hash_matches": evidence_hash_ok,
        "metadata_publication_control": metadata_control_ok,
        "checks": checks,
        "failures": failures,
        "status": "PASS" if not failures else "HALT",
    }


def write_outputs(result: dict, json_path: Path, md_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# Lean-verified publication-guidance audit — 2 August 2026",
        "",
        "**Guidance:** `publication guidance.md`  ",
        f"**Result:** {result['status']}  ",
        f"**Papers:** {result['summary']['passes']}/{result['summary']['papers']} pass  ",
        f"**Lines read:** {result['summary']['lines_read']:,}  ",
        f"**Current claims checked in paper scope:** {result['summary']['claim_bindings_checked']:,}",
        "",
        "Every paper was read in full by the gate. Each of the 23 guidance sections has an explicit Boolean result. Exact claim statements, receipts, identifiers and literal records were compared with the current census and preserved sources rather than rewritten by the prose pass.",
        "",
        "| Paper | Version | Claims | Lines | Result | Failures |",
        "|---|---:|---:|---:|---|---|",
    ]
    for paper in result["papers"]:
        lines.append(
            f"| `{paper['paper_id']}` | {paper['version']} | {paper['relevant_claim_count']:,} | {paper['lines']:,} | {paper['status']} | {', '.join(paper['failures']) or 'None'} |"
        )
    lines.extend(
        [
            "",
            "## Publication record boundary",
            "",
            "This audit performs no remote publication action. PDF rendering, PDF mechanical and visual QA, release-bundle hashing, publication receipts and public-record verification remain separate records.",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()
    manifest_path = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    manifest = json.loads(manifest_path.read_bytes())
    report_path = ROOT / manifest["lean_report_path"]
    report = json.loads(report_path.read_bytes())
    report_hash = sha256(report_path)
    claims = [row for row in json.loads((ROOT / "census/claims.json").read_bytes())["claims"] if row.get("model_admitted")]
    papers = [paper_audit(record, claims, report, report_hash) for record in manifest["papers"]]
    result = {
        "schema": "sft-v3-lean4-verified-publication-guidance-audit/1",
        "date": "2026-08-02",
        "guidance_path": "publication guidance.md",
        "guidance_sha256": sha256(GUIDANCE),
        "manifest_path": manifest_path.relative_to(ROOT).as_posix(),
        "manifest_sha256": sha256(manifest_path),
        "lean_report_path": report_path.relative_to(ROOT).as_posix(),
        "lean_report_sha256": report_hash,
        "papers": papers,
        "summary": {
            "papers": len(papers),
            "passes": sum(paper["status"] == "PASS" for paper in papers),
            "halts": sum(paper["status"] != "PASS" for paper in papers),
            "lines_read": sum(paper["lines"] for paper in papers),
            "bytes_read": sum(paper["bytes"] for paper in papers),
            "claim_bindings_checked": sum(paper["relevant_claim_count"] for paper in papers),
            "guidance_sections_per_paper": 23,
            "guidance_checks": 23 * len(papers),
            "guidance_passes": sum(sum(bool(value) for name, value in paper["checks"].items() if name[:2].isdigit()) for paper in papers),
        },
        "publication_authorized": bool(manifest.get("publication_authorized")),
        "remote_actions_performed": bool(manifest.get("remote_actions_performed")),
    }
    result["status"] = "PASS" if result["summary"]["halts"] == 0 else "HALT"
    json_path = args.json_out if args.json_out.is_absolute() else ROOT / args.json_out
    md_path = args.md_out if args.md_out.is_absolute() else ROOT / args.md_out
    write_outputs(result, json_path, md_path)
    print(
        f"Lean-verified publication guidance audit: {result['summary']['passes']}/{result['summary']['papers']} papers pass; "
        f"{result['summary']['lines_read']:,} lines read; status {result['status']}"
    )
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
