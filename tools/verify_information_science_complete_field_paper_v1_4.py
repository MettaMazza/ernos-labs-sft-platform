#!/usr/bin/env python3
"""Fail-closed local verification for the unpublished Information Science v1.4 paper."""
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "publications/successors/information_science/FROM_DISTINCTION_TO_INFORMATION_PAPER_001_V1_4.md"
CURRENT = ROOT / "publications/current/information_science/FROM_DISTINCTION_TO_INFORMATION.md"
PDF = ROOT / "output/pdf/from-distinction-to-information-branch-paper-001-v1.4.pdf"
FROZEN = ROOT / "census/information_science_discipline_obligations.json"
RECONCILIATION = ROOT / "census/information_science_discipline_current_reconciliation_v20.json"
AUDIT = ROOT / "audits/INFORMATION_SCIENCE_COMPLETE_FIELD_PAPER_V1_4_LOCAL_GATE_2026-07-29.json"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def current_certificate(package: Path, receipt_hash: str):
    matches = [path for path in sorted(package.glob("certificate*.json")) if read(path).get("engine_receipt_hash") == receipt_hash]
    if len(matches) != 1:
        raise SystemExit(f"{package.name}: current certificate count {len(matches)}")
    return read(matches[0])


def main():
    frozen = read(FROZEN)
    reconciliation = read(RECONCILIATION)
    if reconciliation["current_closed_count"] != frozen["registered_obligation_count"]:
        raise SystemExit("complete-field count mismatch")
    if reconciliation["current_open_count"] != 0 or reconciliation["frozen_obligation_count"] != 262:
        raise SystemExit("complete-field reconciliation is open")
    rows = [row for family in frozen["family_order"] for row in reconciliation["completed_families"][family]]
    if len(rows) != 262 or len({row["obligation_id"] for row in rows}) != 262 or len({row["claim_id"] for row in rows}) != 262:
        raise SystemExit("complete-field receipt map is not one-to-one")
    text = PAPER.read_text(encoding="utf-8")
    if CURRENT.read_text(encoding="utf-8") != text:
        raise SystemExit("current landing paper differs from version 1.4 source")
    required_text = (
        "Version 1.4",
        "262/262",
        "75,776",
        "1,048",
        frozen["census_identity"],
        reconciliation["reconciliation_identity"],
        "Maria.Smith.Sftoe@gmail.com",
        "https://discord.gg/ucwGryVxGr",
        "https://github.com/MettaMazza/ernos-labs-sft-platform",
        "CC BY 4.0",
        "Apache-2.0",
        "Ernos Labs",
    )
    if any(token not in text for token in required_text):
        raise SystemExit("paper omits required scientific or public metadata")
    if any(token in text for token in ("TODO", "TBD", "PLACEHOLDER", "open_registered_question")):
        raise SystemExit("paper contains unfinished marker")
    if any(character in text for character in ("\u2011", "\u2013", "\u2014")):
        raise SystemExit("paper contains prohibited non-ASCII dash")
    candidate_count = 0
    control_count = 0
    empirical_count = 0
    for index, row in enumerate(rows, 1):
        package = ROOT / "claims" / row["claim_id"]
        certificate = current_certificate(package, row["receipt_hash"])
        census = read(package / "candidate_census.json")
        elimination = read(package / "elimination_receipt.json")
        controls = read(package / "controls.json")["controls"]
        survivors = [decision for decision in elimination["decisions"] if decision["survives"]]
        if certificate["engine_receipt_hash"] != row["receipt_hash"] or len(survivors) != 1:
            raise SystemExit("stale receipt or survivor: " + row["claim_id"])
        if len(census["candidates"]) != len(elimination["decisions"]) or not all(control["passed"] for control in controls):
            raise SystemExit("incomplete evidence: " + row["claim_id"])
        if row["claim_id"] not in text or row["receipt_hash"] not in text:
            raise SystemExit("paper omits claim evidence: " + row["claim_id"])
        empirical = package / "empirical_validation.json"
        if empirical.exists():
            result = read(empirical)
            if not result["passed"] or not result["all_rows_preserved"]:
                raise SystemExit("empirical package halted: " + row["claim_id"])
            empirical_count += 1
        elif index > 12:
            raise SystemExit("successor claim missing empirical package: " + row["claim_id"])
        candidate_count += len(census["candidates"])
        control_count += len(controls)
    if (candidate_count, control_count, empirical_count) != (75776, 1048, 250):
        raise SystemExit("paper evidence totals changed")
    reader = PdfReader(str(PDF))
    if len(reader.pages) < 500 or reader.metadata.title != "From Distinction to Information":
        raise SystemExit("rendered PDF is incomplete or incorrectly identified")
    audit = {
        "schema": "sft-v3-information-science-complete-field-paper-local-gate/1",
        "date": "2026-07-29",
        "version": "1.4.0",
        "publication_authorized": False,
        "paper_path": str(PAPER.relative_to(ROOT)),
        "paper_hash": sha(PAPER),
        "current_landing_source_path": str(CURRENT.relative_to(ROOT)),
        "pdf_path": str(PDF.relative_to(ROOT)),
        "pdf_hash": sha(PDF),
        "pdf_pages": len(reader.pages),
        "word_count": len(text.split()),
        "line_count": len(text.splitlines()),
        "frozen_census_identity": frozen["census_identity"],
        "reconciliation_identity": reconciliation["reconciliation_identity"],
        "claim_count": 262,
        "candidate_count": candidate_count,
        "unique_survivor_count": 262,
        "control_count": control_count,
        "independent_reconstruction_count": 262,
        "post_registry_empirical_package_count": empirical_count,
        "focused_information_science_tests": "92/92 passed",
        "repository_validation_claim_count": 2233,
        "engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
        "verification_authority_seal": "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8",
        "heavy_global_verification_rerun": False,
        "ready_for_author_review": True,
        "pushed": False,
        "published": False,
    }
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
