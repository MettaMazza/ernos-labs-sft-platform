#!/usr/bin/env python3
"""Build the authorised full-scale SFT V3 preliminary ToE version 0.1.0.

This builder never publishes by itself. It reconstructs the conceptual
monograph, compact complete claim inventory and release-freeze identities from
current authoritative repository files. Publication authority remains with
Maria Smith and is recorded separately from scientific status.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PARTS = HERE / "manuscript_parts"
APPENDICES = HERE / "appendices"
PUBLICATION = HERE / "publication"

INVENTORY = HERE / "AUTHORITATIVE_CORPUS_INVENTORY.json"
CONTENT_MATRIX = HERE / "EXHAUSTIVE_TOE_CONTENT_MATRIX.json"
CONTENT_MATRIX_SUMMARY = HERE / "EXHAUSTIVE_TOE_CONTENT_MATRIX.md"
SCIENTIFIC_AUDIT = HERE / "SCIENTIFIC_AUDIT_LAYER.md"
GUIDANCE = ROOT / "publication guidance.md"

MASTER = HERE / "SMITHIAN_FOLD_THEORY_V3_PRELIMINARY_THEORY_OF_EVERYTHING.md"
CLAIM_MD = APPENDICES / "COMPLETE_CLAIM_INVENTORY.md"
CLAIM_JSON = APPENDICES / "COMPLETE_CLAIM_INVENTORY.json"
FREEZE = PUBLICATION / "CORPUS_FREEZE.json"

PART_ORDER = [
    "00_front_matter_constitution_and_dependency_spine.md",
    "00a_historical_trajectory_and_v3_reconciliation.md",
    "01_root_mathematics_information_computation_quantum.md",
    "02_physics_chemistry_materials.md",
    "03_life_mind_earth_cosmos_society_engineering_programmes.md",
    "04_evidence_reconciliation_limitations_reproducibility_and_conclusion.md",
]

BRANCH_ORDER = [
    "foundation",
    "mathematics",
    "information_science",
    "computation",
    "quantum_computation",
    "physics",
    "chemistry",
    "materials",
    "biology",
    "medicine",
    "consciousness_cognitive_science",
    "earth_environment",
    "astronomy_cosmology",
    "social_collective_systems",
    "social_collective",
    "engineering_translation",
    "cross_branch_synthesis",
]

BRANCH_LABELS = {
    "foundation": "Foundation",
    "mathematics": "Mathematics",
    "information_science": "Information Science",
    "computation": "Classical Computation",
    "quantum_computation": "Reversible and Quantum Computation",
    "physics": "Physics",
    "chemistry": "Chemistry",
    "materials": "Materials Science",
    "biology": "Biology and Life Sciences",
    "medicine": "Medicine and Health Sciences",
    "consciousness_cognitive_science": "Consciousness and Cognitive Science",
    "earth_environment": "Earth and Environmental Sciences",
    "astronomy_cosmology": "Astronomy and Cosmology",
    "social_collective_systems": "Social and Collective Systems",
    "social_collective": "Social and Collective Returned Family",
    "engineering_translation": "Engineering Translation",
    "cross_branch_synthesis": "Cross-Branch Synthesis",
}


def digest(path: Path) -> str:
    block = sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            block.update(chunk)
    return block.hexdigest()


def file_record(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "sha256": digest(path),
    }


def escape_cell(value: Any) -> str:
    text = str(value)
    return text.replace("|", "\\|").replace("\n", " ").strip()


def count_words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text, flags=re.UNICODE))


def build_claim_inventory(inventory: dict[str, Any]) -> dict[str, Any]:
    ledger = inventory["claim_ledger"]
    claims = ledger["claims"]
    by_branch: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        by_branch[claim["branch"]].append(claim)

    missing_branches = sorted(set(by_branch) - set(BRANCH_ORDER))
    if missing_branches:
        raise RuntimeError(f"unrouted claim branches: {missing_branches}")

    lines = [
        "# Complete SFT V3 claim inventory",
        "",
        "**Author and publication authority:** Maria Smith  ",
        "**Version:** 0.1.0  ",
        "**Version DOI:** 10.5281/zenodo.21717584  ",
        "**Status:** Audit appendix for the authorised first standalone V3 preliminary publication  ",
        f"**Claims:** {ledger['claim_count']:,}  ",
        f"**Candidates:** {ledger['candidate_count']:,}  ",
        f"**Survivors:** {ledger['survivor_count']:,}  ",
        f"**Controls:** {ledger['control_count']:,}",
        "",
        "This appendix is the complete compact inventory. Exact statements, reasons,",
        "carriers, boundaries, relations, candidate grammars, elimination logic,",
        "falsification conditions, source capture, chronology and full receipt identities",
        "remain in the dependency-ordered branch audit volumes and machine packages.",
        "",
        "## Corpus totals",
        "",
        "| Branch | Claims | Candidates | Survivors | Controls | External status classes |",
        "|---|---:|---:|---:|---:|---|",
    ]

    for branch in BRANCH_ORDER:
        rows = by_branch.get(branch, [])
        if not rows:
            continue
        status_counts = Counter(row["external_status"] for row in rows)
        statuses = "; ".join(
            f"{name}: {amount:,}" for name, amount in sorted(status_counts.items())
        )
        lines.append(
            "| {label} | {claims:,} | {candidates:,} | {survivors:,} | "
            "{controls:,} | {statuses} |".format(
                label=BRANCH_LABELS[branch],
                claims=len(rows),
                candidates=sum(row["candidate_count"] for row in rows),
                survivors=sum(row["unique_survivor_count"] for row in rows),
                controls=sum(row["control_count"] for row in rows),
                statuses=escape_cell(statuses),
            )
        )

    global_index = 0
    for branch in BRANCH_ORDER:
        rows = by_branch.get(branch, [])
        if not rows:
            continue
        lines.extend(
            [
                "",
                f"## {BRANCH_LABELS[branch]}",
                "",
                "| No. | Claim ID and name | Formal status | Empirical status | Closure | Candidates | Survivors | Controls | Declared dependencies |",
                "|---:|---|---|---|---|---:|---:|---:|---|",
            ]
        )
        for row in rows:
            global_index += 1
            dependency_values = row["dependencies"]
            if len(dependency_values) > 6:
                dependencies = (
                    ", ".join(dependency_values[:4])
                    + f"; +{len(dependency_values) - 4:,} more (full array in JSON)"
                )
            else:
                dependencies = ", ".join(dependency_values) or "Root"
            formal = "model-admitted" if row["model_admitted"] else "not admitted"
            claim_identity = f"`{row['claim_id']}`<br>{row['title']}"
            lines.append(
                "| {index:,} | {identity} | {formal} | `{empirical}` | "
                "`{closure}` | {candidates:,} | {survivors:,} | {controls:,} | "
                "{dependencies} |".format(
                    index=global_index,
                    identity=escape_cell(claim_identity),
                    formal=formal,
                    empirical=escape_cell(row["external_status"]),
                    closure=escape_cell(row["closure_status"]),
                    candidates=row["candidate_count"],
                    survivors=row["unique_survivor_count"],
                    controls=row["control_count"],
                    dependencies=escape_cell(dependencies),
                )
            )

    lines.extend(
        [
            "",
            "## Machine identity boundary",
            "",
            "The adjacent JSON inventory preserves the complete exact statements, full",
            "receipt identities, candidate-census hashes, certificate hashes, control hashes",
            "and registered dependency arrays without display truncation.",
            "",
        ]
    )
    CLAIM_MD.write_text("\n".join(lines), encoding="utf-8")

    compact = {
        "schema": "sft-v3-preliminary-toe-complete-claim-inventory/v1",
        "date": inventory["date"],
        "author": "Maria Smith",
        "publication_authority": "Maria Smith",
        "publication_status": "authorised_first_standalone_v3_preliminary_publication",
        "version": "0.1.0",
        "version_doi": "10.5281/zenodo.21717584",
        "source_inventory_sha256": digest(INVENTORY),
        "totals": {
            "claim_count": ledger["claim_count"],
            "candidate_count": ledger["candidate_count"],
            "survivor_count": ledger["survivor_count"],
            "control_count": ledger["control_count"],
            "receipt_identity_match_count": ledger["receipt_identity_match_count"],
            "candidate_census_match_count": ledger["candidate_census_match_count"],
            "root_traced_count": ledger["root_traced_count"],
            "missing_dependency_count": ledger["missing_dependency_count"],
        },
        "claims": claims,
        "protected_authority_edited": False,
        "remote_publication_authorised": True,
    }
    CLAIM_JSON.write_text(
        json.dumps(compact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return compact


def build_master() -> dict[str, Any]:
    missing = [name for name in PART_ORDER if not (PARTS / name).is_file()]
    if missing:
        raise RuntimeError(f"missing manuscript parts: {missing}")

    sources = []
    parts = []
    for name in PART_ORDER:
        source_path = PARTS / name
        text = source_path.read_text(encoding="utf-8").strip()
        if not text:
            raise RuntimeError(f"empty manuscript part: {name}")
        parts.append(text)
        record = file_record(source_path)
        record["word_count"] = count_words(text)
        sources.append(record)

    master = "\n\n---\n\n".join(parts) + "\n"
    MASTER.write_text(master, encoding="utf-8")
    return {
        "master": file_record(MASTER),
        "master_word_count": count_words(master),
        "parts": sources,
    }


def build_freeze(inventory: dict[str, Any], master_record: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    active_papers = []
    for branch, registered in sorted(inventory["active_papers"].items()):
        source = ROOT / registered["path"]
        if not source.is_file():
            failures.append(f"missing active paper: {registered['path']}")
            continue
        actual = digest(source)
        if actual != registered["sha256"]:
            failures.append(
                f"active paper hash mismatch: {branch}: {actual} != {registered['sha256']}"
            )
        active_papers.append(
            {
                "branch": branch,
                **file_record(source),
                "registered_sha256": registered["sha256"],
                "identity_match": actual == registered["sha256"],
            }
        )

    required_records = [
        INVENTORY,
        CONTENT_MATRIX,
        CONTENT_MATRIX_SUMMARY,
        SCIENTIFIC_AUDIT,
        GUIDANCE,
        CLAIM_MD,
        CLAIM_JSON,
        ROOT / "audits/CURRENT_PROGRAMME_STATUS_2026-07-29.md",
        ROOT / "publication/FINAL_COMPLETE_FIELD_PUBLICATIONS_2026-07-29.md",
        ROOT / "publications/FINAL_TOE_PAPER_PROTOCOL.md",
    ]
    for source in required_records:
        if not source.is_file():
            failures.append(f"missing required record: {source.relative_to(ROOT)}")

    volume_records = []
    for source in sorted((HERE / "volumes").glob("*.md")):
        volume_records.append(file_record(source))
    if len(volume_records) != 17:
        failures.append(f"expected 17 audit volumes, found {len(volume_records)}")

    ledger = inventory["claim_ledger"]
    invariants = {
        "claim_count_is_2751": ledger["claim_count"] == 2751,
        "candidate_count_is_892246": ledger["candidate_count"] == 892246,
        "survivor_count_is_2751": ledger["survivor_count"] == 2751,
        "control_count_is_11004": ledger["control_count"] == 11004,
        "all_controls_pass": ledger["passed_control_count"]
        == ledger["control_count"],
        "all_receipts_match": ledger["receipt_identity_match_count"]
        == ledger["claim_count"],
        "all_censuses_match": ledger["candidate_census_match_count"]
        == ledger["claim_count"],
        "all_claims_root_traced": ledger["root_traced_count"]
        == ledger["claim_count"],
        "no_missing_dependencies": ledger["missing_dependency_count"] == 0,
        "seventeen_audit_volumes_present": len(volume_records) == 17,
        "all_active_paper_identities_match": all(
            row["identity_match"] for row in active_papers
        ),
    }
    failures.extend(name for name, passed in invariants.items() if not passed)

    freeze = {
        "schema": "sft-v3-preliminary-toe-corpus-freeze/v1",
        "date": str(date.today()),
        "author": "Maria Smith",
        "publication_authority": "Maria Smith",
        "proposed_version": "0.1.0",
        "publication_operation": "create_new_standalone_v3_record",
        "concept_record_id": 21717583,
        "concept_doi": None,
        "zenodo_draft_id": 21717584,
        "version_doi": "10.5281/zenodo.21717584",
        "historical_pre_v3_concept_doi": "10.5281/zenodo.21182468",
        "status": "PASS_LOCAL_BUILD" if not failures else "HALT",
        "publication_status": "authorised_for_first_standalone_v3_publication",
        "remote_publication_authorised": True,
        "protected_authority_edited": False,
        "master": master_record,
        "claim_inventory_markdown": file_record(CLAIM_MD),
        "claim_inventory_json": file_record(CLAIM_JSON),
        "active_papers": active_papers,
        "authoritative_records": [
            file_record(source) for source in required_records if source.is_file()
        ],
        "audit_volumes": volume_records,
        "invariants": invariants,
        "failure_count": len(failures),
        "failures": failures,
    }
    FREEZE.write_text(
        json.dumps(freeze, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return freeze


def main() -> int:
    APPENDICES.mkdir(parents=True, exist_ok=True)
    PUBLICATION.mkdir(parents=True, exist_ok=True)
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    build_claim_inventory(inventory)
    master = build_master()
    freeze = build_freeze(inventory, master)
    print(
        json.dumps(
            {
                "status": freeze["status"],
                "master_words": master["master_word_count"],
                "claims": inventory["claim_ledger"]["claim_count"],
                "failures": freeze["failure_count"],
            },
            sort_keys=True,
        )
    )
    return 0 if freeze["status"] == "PASS_LOCAL_BUILD" else 1


if __name__ == "__main__":
    raise SystemExit(main())
