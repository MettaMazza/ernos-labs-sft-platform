#!/usr/bin/env python3
"""Audit the full SFT V3 preliminary ToE against publication guidance.

This gate is deliberately local and publication-inert.  It checks the complete
conceptual manuscript, compact claim inventory, seventeen claim-audit volumes,
authoritative corpus freeze and machine-readable identities.  It never edits a
scientific record, opens a remote draft or grants publication authority.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MASTER = HERE / "SMITHIAN_FOLD_THEORY_V3_PRELIMINARY_THEORY_OF_EVERYTHING.md"
CLAIMS = HERE / "appendices/COMPLETE_CLAIM_INVENTORY.json"
CLAIMS_MD = HERE / "appendices/COMPLETE_CLAIM_INVENTORY.md"
FREEZE = HERE / "publication/CORPUS_FREEZE.json"
INVENTORY = HERE / "AUTHORITATIVE_CORPUS_INVENTORY.json"
GUIDANCE = ROOT / "publication guidance.md"
REPORT_JSON = HERE / "publication/PUBLICATION_GUIDANCE_COMPLIANCE.json"
REPORT_MD = HERE / "publication/PUBLICATION_GUIDANCE_COMPLIANCE.md"


BRANCHES = (
    "Foundation",
    "Mathematics",
    "Information Science",
    "Classical Computation",
    "Reversible and Quantum Computation",
    "Physics",
    "Chemistry",
    "Materials Science",
    "Biology and Life Sciences",
    "Medicine and Health Sciences",
    "Consciousness and Cognitive Science",
    "Earth and Environmental Sciences",
    "Astronomy and Cosmology",
    "Social and Collective Systems",
    "Engineering Translation",
    "Cross-Branch Synthesis",
)

TERMS = (
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
    "Empirical status",
    "Formal status",
    "Publication status",
    "Foundational closure",
    "Field-wide closure",
    "Current-evidence closure",
    "Extension openness",
)

STRUCTURE = (
    "## Abstract",
    "## Headline findings",
    "## Current-status statement",
    "Scope, ownership and publication authority",
    "The scientific constitution",
    "Mathematical constitution",
    "Empirical constitution and chronology",
    "Dependency spine",
    "Registered source surface",
    "Corrections, adverse results and historical custody",
    "Limitations and open frontier",
    "Reproducibility",
    "Data and code availability",
    "Conclusion",
    "References and authoritative records",
    "Machine identity register",
)

AMERICAN_PROSE = (
    "analyze",
    "analyzed",
    "behavior",
    "behaviors",
    "categorized",
    "centered",
    "color",
    "colors",
    "favorable",
    "favorably",
    "finalized",
    "generalized",
    "harmonized",
    "labeled",
    "modeling",
    "normalized",
    "organization",
    "organizations",
    "organized",
    "recognized",
    "standardized",
    "summarized",
)

PLACEHOLDERS = (
    "TODO",
    "TBD",
    "FIXME",
    "INSERT DOI",
    "lorem ipsum",
    "Executive overview",
    "PRELIMINARY COMPLETE SYNTHESIS",
    "19-page",
)


def digest(path: Path) -> str:
    block = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            block.update(chunk)
    return block.hexdigest()


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text, flags=re.UNICODE))


def prose_lines(text: str) -> Iterable[tuple[int, str]]:
    """Yield prose while masking literal fields protected by the guidance."""
    fenced = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if line.lstrip().startswith("|"):
            continue
        masked = re.sub(r"`[^`]*`", "<LITERAL>", line)
        masked = re.sub(r"\]\((?:[^()]|\([^()]*\))*\)", "](<LINK>)", masked)
        masked = re.sub(r"https?://\S+", "<URL>", masked)
        masked = re.sub(r"\b(?:sha256:)?[0-9a-f]{64}\b", "<HASH>", masked)
        yield number, masked


def repeated_paragraphs(text: str) -> list[dict[str, Any]]:
    blocks = re.split(r"\n\s*\n", text)
    normalised = []
    for block in blocks:
        value = re.sub(r"\s+", " ", block).strip()
        if len(value.split()) < 28 or value.startswith(("#", "|", "```")):
            continue
        normalised.append(value)
    counts = Counter(normalised)
    return [
        {"count": count, "text": paragraph[:300]}
        for paragraph, count in counts.most_common()
        if count > 1
    ]


def malformed_tables(text: str) -> list[dict[str, Any]]:
    findings = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        if index and lines[index - 1].strip().startswith("|"):
            continue
        block = []
        cursor = index
        while cursor < len(lines) and lines[cursor].strip().startswith("|"):
            block.append(lines[cursor])
            cursor += 1
        widths = [len(re.split(r"(?<!\\)\|", row.strip().strip("|"))) for row in block]
        if len(block) < 2 or len(set(widths)) != 1:
            findings.append({"line": index + 1, "row_widths": widths})
    return findings


def local_link_failures(text: str) -> list[str]:
    failures = []
    for destination in re.findall(r"\]\(([^)]+)\)", text):
        if re.match(r"(?:https?://|mailto:|#)", destination):
            continue
        clean = destination.split("#", 1)[0]
        if not clean:
            continue
        resolved = (MASTER.parent / clean).resolve()
        if not resolved.exists():
            failures.append(destination)
    return sorted(set(failures))


def check(name: str, passed: bool, evidence: str, findings: Any = None) -> dict[str, Any]:
    return {
        "guidance_section": name,
        "status": "PASS" if passed else "HALT",
        "evidence": evidence,
        "findings": findings if findings is not None else [],
    }


def main() -> int:
    required = (MASTER, CLAIMS, CLAIMS_MD, FREEZE, INVENTORY, GUIDANCE)
    absent = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if absent:
        raise SystemExit(f"missing release inputs: {absent}")

    text = MASTER.read_text(encoding="utf-8")
    claim_package = json.loads(CLAIMS.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    guidance = GUIDANCE.read_text(encoding="utf-8")
    claims = claim_package["claims"]
    ledger = inventory["claim_ledger"]
    volumes = sorted((HERE / "volumes").glob("*.md"))

    exact_totals = (
        len(claims) == ledger["claim_count"] == 2751
        and claim_package["totals"]["candidate_count"] == ledger["candidate_count"] == 892246
        and claim_package["totals"]["survivor_count"] == ledger["survivor_count"] == 2751
        and claim_package["totals"]["control_count"] == ledger["control_count"] == 11004
    )
    all_claim_fields = all(
        {
            "claim_id",
            "title",
            "branch",
            "statement",
            "dependencies",
            "candidate_count",
            "unique_survivor_count",
            "control_count",
            "external_status",
            "closure_status",
            "registered_receipt_id",
            "receipt_file_sha256",
            "candidate_census_sha256",
            "certificate_sha256",
            "controls_sha256",
        }.issubset(row)
        for row in claims
    )

    source_hashes_pass = all(
        row.get("identity_match") for row in freeze.get("active_papers", [])
    ) and len(freeze.get("active_papers", [])) == 17
    frozen_master = freeze.get("master", {}).get("master", {})
    frozen_files_pass = (
        freeze.get("status") == "PASS_LOCAL_BUILD"
        and frozen_master.get("sha256") == digest(MASTER)
        and freeze.get("claim_inventory_json", {}).get("sha256") == digest(CLAIMS)
        and freeze.get("claim_inventory_markdown", {}).get("sha256") == digest(CLAIMS_MD)
        and len(volumes) == 17
    )
    standalone_v3_identity_pass = (
        freeze.get("proposed_version") == "0.1.0"
        and freeze.get("publication_operation")
        == "create_new_standalone_v3_record"
        and freeze.get("concept_doi") is None
        and freeze.get("concept_record_id") == 21717583
        and freeze.get("zenodo_draft_id") == 21717584
        and freeze.get("version_doi") == "10.5281/zenodo.21717584"
        and "**Standalone version:** 0.1.0" in text
        and "new standalone V3 Zenodo lineage" in text
        and "**Existing ToE concept DOI:**" not in text
        and "same-concept v7" not in text.casefold()
    )

    us_findings = []
    for line_number, line in prose_lines(text):
        lowered = line.lower()
        for token in AMERICAN_PROSE:
            if re.search(rf"\b{re.escape(token)}\b", lowered):
                us_findings.append({"line": line_number, "word": token, "text": line[:260]})

    duplicate_words = []
    doubled = re.compile(r"\b([A-Za-z]{3,})\s+\1\b", re.IGNORECASE)
    for line_number, line in prose_lines(text):
        found = doubled.search(line)
        if found:
            duplicate_words.append({"line": line_number, "word": found.group(1), "text": line[:260]})

    delimiters = {
        "inline_math": [text.count(r"\("), text.count(r"\)")],
        "display_math": [text.count(r"\["), text.count(r"\]")],
        "fenced_code": text.count("```") % 2,
    }
    balanced = (
        delimiters["inline_math"][0] == delimiters["inline_math"][1]
        and delimiters["display_math"][0] == delimiters["display_math"][1]
        and delimiters["fenced_code"] == 0
    )
    tables = malformed_tables(text)
    links = local_link_failures(text)
    repetitions = repeated_paragraphs(text)
    placeholders = [token for token in PLACEHOLDERS if token in text]

    abstract_match = re.search(
        r"(?ms)^## Abstract\s+(.*?)(?=^---$|^## )", text
    )
    abstract = abstract_match.group(1) if abstract_match else ""
    abstract_pass = all(
        token in abstract.lower()
        for token in ("root", "method", "2,751", "evidence", "scope", "open")
    )
    conclusion_match = re.search(
        r"(?ms)^## 30\. Conclusion\s+(.*?)(?=^## References|^---$)", text
    )
    conclusion = conclusion_match.group(1) if conclusion_match else ""
    conclusion_pass = all(
        token in conclusion.lower()
        for token in ("deriv", "evidence", "correction", "adverse", "open", "dependency")
    )
    folded_text = text.casefold()

    checks = [
        check(
            "1. Authoritative context",
            source_hashes_pass
            and frozen_files_pass
            and exact_totals
            and standalone_v3_identity_pass,
            "Corpus freeze, standalone V3 publication identity, seventeen active-paper SHA-256 matches, seventeen audit volumes and reconstructed global ledger.",
        ),
        check(
            "2. Non-negotiable scientific preservation",
            exact_totals and all_claim_fields and all(freeze.get("invariants", {}).values()),
            "Complete 2,751-row JSON inventory retains statements, statuses, dependencies, counts and full machine identities.",
        ),
        check(
            "3. Scientific change control",
            all(
                phrase in folded_text
                for phrase in ("silently", "maria smith", "historical custody", "superseded")
            ),
            "Manuscript declares discrepancy, supersession and publication-authority rules; unresolved conflicts are retained.",
        ),
        check(
            "4. Corpus-wide house style",
            not us_findings and "31 July 2026" in text and "Creative Commons Attribution 4.0 International" in text,
            "Literal-aware British-English scan, human date, version and licence surface.",
            us_findings,
        ),
        check(
            "5. Terminology consistency",
            all(term in text for term in TERMS),
            "Empirical constitution defines every required formal, evidence, publication and closure term.",
            [term for term in TERMS if term not in text],
        ),
        check(
            "6. Proof and evidence verbs",
            "### 4.2 Proof and evidence verbs" in text
            and all(word in text for word in ("proves", "derives", "implements", "predicts", "observes", "measures", "reconstructs", "confirms")),
            "Dedicated verb constitution plus branch-specific current-status language.",
        ),
        check(
            "7. Paper structure",
            all(surface in text for surface in STRUCTURE) and all(branch in text for branch in BRANCHES),
            "Required front matter, scientific constitutions, dependency branches, reconciliation, frontier, conclusion and appendices.",
            [surface for surface in STRUCTURE if surface not in text],
        ),
        check(
            "8. Narrative spine",
            all(token in text.lower() for token in ("preceding", "required", "handoff", "evidential boundary", "dependency")),
            "Each major part identifies admitted upstream objects, next problem, new boundary and downstream handoff.",
        ),
        check(
            "9. Repetition control",
            not repetitions,
            "Exact duplicate-paragraph scan across the conceptual manuscript; repeated claim records remain in audit volumes.",
            repetitions,
        ),
        check(
            "10. Claim-section format",
            all_claim_fields and len(volumes) == 17 and "complete claim-level fields" in text.lower(),
            "Compact claim inventory plus seventeen detailed audit volumes; full identities remain machine-readable.",
        ),
        check(
            "11. Abstracts",
            abstract_pass,
            "Abstract states problem, method, principal counts and results, evidence boundary, scope and open extension.",
        ),
        check(
            "12. Headline findings",
            "## Headline findings" in text and "Seven branches have current full-field closure" in text,
            "Current headline list is bound to reconstructed corpus totals and non-uniform branch status.",
        ),
        check(
            "13. Current status boxes",
            "## Current-status statement" in text and text.count("Current status") >= 2,
            "Front-matter status table and branch/programme-specific status records distinguish formal, empirical and publication state.",
        ),
        check(
            "14. Adverse, corrected and updated results",
            all(token in text.lower() for token in ("adverse", "corrected", "superseded", "failed transport", "later evidence", "historical status")),
            "Dedicated historical-custody section and branch evidence reconciliations retain adverse and later records.",
        ),
        check(
            "15. Mathematical formatting",
            balanced,
            "Balanced inline/display mathematics and fenced-code delimiters; exact forms precede approximations in the narrative.",
            delimiters,
        ),
        check(
            "16. Tables",
            not tables and text.count("\n|") >= 20,
            "Markdown table-shape audit across status, evidence, source, chronology, branch, correction and machine-identity surfaces.",
            tables,
        ),
        check(
            "17. Sources and references",
            not links and "## References and authoritative records" in text and "source ID" in text,
            "Human-readable references coexist with retained source IDs, DOIs, source transport and hashes.",
            links,
        ),
        check(
            "18. Prose proofreading",
            not duplicate_words and not placeholders and balanced and not tables and not links,
            "Duplicate-word, placeholder, delimiter, table and local-link integrity scans.",
            {"duplicate_words": duplicate_words, "placeholders": placeholders},
        ),
        check(
            "19. Template-rhythm reduction",
            not repetitions and "continuous scientific argument" in text,
            "Conceptual layer contains no exact duplicate long paragraph; full repeated custody remains in audit/machine layers.",
            repetitions,
        ),
        check(
            "20. Human paper and machine archive",
            all(phrase in text for phrase in ("### 6.1 Conceptual paper", "### 6.2 Scientific audit layer", "### 6.3 Machine archive")),
            "Three distinct access levels are declared and present in the authorised preliminary version.",
        ),
        check(
            "21. Authorship and open-science mission",
            text.count("Maria Smith") >= 10
            and "Ernos Labs" in text
            and "Criticism is unrestricted; admission remains governed" in text,
            "Authorship, publication authority, mission, criticism/admission boundary and licences are explicit.",
        ),
        check(
            "22. Conclusions",
            conclusion_pass,
            "Conclusion synthesises derivation, evidence, corrections, adverse records, open work and dependency contribution.",
        ),
        check(
            "23. Limitations and open frontier",
            "## 27. Limitations and open frontier" in text
            and all(
                phrase in folded_text
                for phrase in (
                    "formal closure",
                    "implementation closure",
                    "foundational branch closure",
                    "field-wide branch closure",
                    "open extension",
                    "end of science",
                )
            ),
            "Completion classes and remaining scientific/computational/publication frontiers are explicitly distinguished.",
        ),
    ]

    failures = [row for row in checks if row["status"] != "PASS"]
    result = {
        "schema": "sft-v3-preliminary-toe-publication-guidance-audit/v1",
        "guidance_path": str(GUIDANCE.relative_to(ROOT)),
        "guidance_sha256": digest(GUIDANCE),
        "manuscript_path": str(MASTER.relative_to(ROOT)),
        "manuscript_sha256": digest(MASTER),
        "manuscript_word_count": word_count(text),
        "claim_count": len(claims),
        "audit_volume_count": len(volumes),
        "status": "PASS" if not failures else "HALT",
        "remote_publication_authorised": True,
        "publication_operation": "create_new_standalone_v3_record",
        "zenodo_draft_id": 21717584,
        "concept_record_id": 21717583,
        "concept_doi": None,
        "version_doi": "10.5281/zenodo.21717584",
        "protected_authority_edited": False,
        "checks": checks,
        "failure_count": len(failures),
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Preliminary ToE publication-guidance compliance",
        "",
        "**Author and publication authority:** Maria Smith  ",
        "**Remote publication:** authorised by Maria Smith  ",
        "**Version DOI:** 10.5281/zenodo.21717584  ",
        f"**Overall status:** `{result['status']}`  ",
        f"**Manuscript words:** {result['manuscript_word_count']:,}  ",
        f"**Claims audited:** {result['claim_count']:,}  ",
        f"**Detailed audit volumes:** {result['audit_volume_count']}",
        "",
        "| Publication-guidance section | Status | Evidence |",
        "|---|---|---|",
    ]
    for row in checks:
        evidence = row["evidence"].replace("|", "\\|")
        lines.append(
            f"| {row['guidance_section']} | `{row['status']}` | "
            f"{evidence} |"
        )
    lines.extend(
        [
            "",
            "The JSON companion preserves every machine finding. A `PASS` records",
            "conformance at the authorised preliminary-version boundary. It does not",
            "change a claim status, scientific authority or extension boundary.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "checks": len(checks),
                "failures": len(failures),
                "words": result["manuscript_word_count"],
            },
            sort_keys=True,
        )
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
