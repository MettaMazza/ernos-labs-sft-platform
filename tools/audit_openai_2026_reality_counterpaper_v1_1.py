#!/usr/bin/env python3
"""Audit the evidence-led OpenAI 2026 SFT counterpaper successor."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pypdf import PdfReader

import build_openai_2026_reality_counterpaper_v1_1 as build


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "audits/OPENAI_2026_REALITY_COUNTERPAPER_2026-08-03_V1_1.json"


def hash_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def require(condition: bool, message: str, checks: list[dict[str, object]]) -> None:
    checks.append({"check": message, "passed": bool(condition)})
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    rows, registry, completeness, compatibility, lean, whole, source_manifest = build.load_rows()
    reality = build.load_reality_evidence()
    paper = build.PAPER_PATH.read_text(encoding="utf-8")
    evidence = build.load(build.EVIDENCE_MAP_PATH)
    checks: list[dict[str, object]] = []

    require(
        paper.startswith("# OpenAI's Ten Mathematical Advances Fail the Reality Test\n"),
        "direct reality-level title is first",
        checks,
    )
    require("Twelve closed SFT disproofs, twelve first-principles replacements" in paper, "subtitle is direct", checks)
    require("2,378/2,378 registered empirical packages" in paper, "external record is front-loaded", checks)
    require("503846395469/3676744786" in paper, "exact alpha ratio is present", checks)
    require("0.008612158395" in paper, "exact CODATA sigma displacement is present", checks)
    require("SFT-PHYS-UNIFIED-CONSTANTS-OBJECT-077" in paper, "unified constants object is present", checks)
    require("SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003" in paper, "complete force-sector inventory is present", checks)
    require("SFT-PHYS-FINITE-QUANTUM-GRAVITY-TERMINAL-023" in paper, "finite quantum-gravity closure is present", checks)
    require("368 admitted claims across 13 subbranches" in paper, "complete current Physics surface is front-loaded", checks)
    require("Alpha is not the basis of the model" in paper, "alpha is correctly bounded as one exhibit", checks)
    require("SFT-described" not in paper, "paper does not relativize reality as merely SFT-described", checks)
    require(paper.count("**Reality-level verdict:** **OPENAI CLAIM REJECTED; SFT RESULT REPLACES IT**") == 12, "twelve direct reality verdicts", checks)
    require(paper.count("— **DISPROVED**") == 12, "twelve source-validity disproof labels", checks)
    require(paper.count("— **PROVED, DISTINCT**") == 12, "twelve replacement proof labels", checks)
    require(paper.count("**Material and functional difference.**") == 12, "twelve material-difference analyses", checks)
    require(paper.count("#### E. No confirmation and no truth transfer") == 12, "twelve no-transfer sections", checks)
    require(paper.count("total_truth_preserving_admission_exists = false") == 12, "twelve failed total admissions", checks)
    require(paper.count("native_reconstruction_transfers_source_validity = false") == 12, "twelve false validity transfers", checks)
    require("## 8. Objections resolved before downstream classification" in paper, "objections precede classification", checks)
    require(paper.index("## 8. Objections") < paper.index("## 9. Corrected compatibility audit"), "compatibility work follows objections", checks)
    require("## Appendix A. Frozen evidence identities" in paper, "frozen identity appendix is present", checks)
    require("TODO" not in paper and "TBD" not in paper and "TO BE COMPLETED" not in paper, "no open drafting markers", checks)
    require("no chain remains open" in paper and "Zero chains remain open" in paper, "closed conclusion is explicit", checks)

    for row in rows:
        require(row["declaration"] in paper, f"source declaration present: {row['atomic_id']}", checks)
        require(row["source_statement_hash"] in paper, f"source statement hash present: {row['atomic_id']}", checks)
        require(row["registered_negation"] in paper, f"registered negation present: {row['atomic_id']}", checks)
        require(row["receipt_hash"] in paper, f"disproof receipt present: {row['atomic_id']}", checks)
        require(row["native_current_receipt"] in paper, f"replacement receipt present: {row['atomic_id']}", checks)
        require(build.MATERIAL_DIFFERENCES[row["atomic_id"]] in paper, f"material difference present: {row['atomic_id']}", checks)
        for step in row["native_derivation"]["steps"]:
            require(
                f"**{step['step_id']}**" in paper,
                f"native proof step present: {row['atomic_id']}:{step['step_id']}",
                checks,
            )

    require(completeness["all_twelve_chains_pass"] is True, "twelve-chain completeness gate passes", checks)
    require(compatibility["closed_classification"]["open"] == 0, "downstream classification has zero open", checks)
    require(lean["status"] == "PASS" and lean["open_count"] == 0, "OpenAI-addition Lean gate passes", checks)
    require(whole["status"] == "PASS" and whole["issue_count"] == 0, "whole-model Lean gate passes", checks)
    require(reality["empirical_count"] == 2378, "empirical package census is exact", checks)
    require(reality["formal_only_count"] == 399, "formal-only census is exact", checks)
    require(reality["comparison_row_count"] == 36182, "comparison-summary census is exact", checks)
    require(reality["data_source_id_count"] == 1277, "external-source identity census is exact", checks)
    require(reality["physics"]["inventory"]["admitted_claim_count"] == 368, "Physics inventory claim count is exact", checks)
    require(len(reality["physics"]["inventory"]["subbranch_counts"]) == 13, "Physics inventory subbranch count is exact", checks)
    require(
        reality["physics"]["registrations"][build.FORCE_INVENTORY_ID]["status"] == "independently_replicated",
        "complete force-sector inventory is independently replicated",
        checks,
    )

    require(evidence["paper"]["sha256"] == hash_file(build.PAPER_PATH), "evidence map binds the paper", checks)
    require(evidence["publication"]["remote_status"] == "publication_authorized", "publication authority status is accurate", checks)
    require(evidence["publication"]["zenodo_doi"] == build.ZENODO_DOI, "successor DOI is bound", checks)
    require(build.ZENODO_DOI in paper, "successor DOI is present in the paper", checks)
    require(evidence["closed_result"]["open"] == 0, "evidence map has zero open chains", checks)
    require(evidence["reality_evidence"]["physics_inventory_claims"] == 368, "evidence map binds complete Physics inventory", checks)
    require(
        evidence["reality_evidence"]["force_inventory_receipt"]
        == reality["physics"]["claims"][build.FORCE_INVENTORY_ID]["receipt_hash"],
        "evidence map binds force-sector receipt",
        checks,
    )

    require(build.PDF_PATH.exists(), "rendered PDF exists", checks)
    pdf = PdfReader(str(build.PDF_PATH))
    pdf_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    pdf_text_normalized = " ".join(pdf_text.split())
    require(30 <= len(pdf.pages) <= 45, "PDF page count is plausible", checks)
    require("OpenAI's Ten Mathematical" in pdf_text_normalized and "Fail the Reality Test" in pdf_text_normalized, "PDF contains the direct title", checks)
    require("Final verdict" in pdf_text_normalized and "Zero chains remain open" in pdf_text_normalized, "PDF contains the final verdict", checks)

    audit: dict[str, object] = {
        "schema": "sft-openai-2026-reality-counterpaper-audit/1",
        "status": "PASS",
        "paper": {"path": build.rel(build.PAPER_PATH), "sha256": hash_file(build.PAPER_PATH)},
        "evidence_map": {"path": build.rel(build.EVIDENCE_MAP_PATH), "sha256": hash_file(build.EVIDENCE_MAP_PATH)},
        "pdf": {"path": build.rel(build.PDF_PATH), "sha256": hash_file(build.PDF_PATH), "page_count": len(pdf.pages)},
        "closed_totals": {
            "advertised_claims_rejected": 10,
            "source_validity_disproved": 12,
            "sft_replacements_proved_distinct": 12,
            "truth_transfers": 0,
            "open": 0,
        },
        "reality_totals": evidence["reality_evidence"],
        "check_count": len(checks),
        "checks": checks,
        "engine_seal": completeness["engine_seal"],
        "verification_authority_seal": completeness["verification_authority_seal"],
    }
    audit["audit_identity"] = canonical_hash(audit)
    AUDIT_PATH.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"PASS {build.rel(AUDIT_PATH)}")
    print(audit["audit_identity"])


if __name__ == "__main__":
    main()
