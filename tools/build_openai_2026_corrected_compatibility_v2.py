#!/usr/bin/env python3
"""Build the corrected closed SFT compatibility classification for OpenAI 2026.

This builder deliberately separates four propositions that the historical
frontier documents had partially conflated:

1. validity of the exact frozen OpenAI artifact inside SFT;
2. existence of a total truth-preserving SFT admission of that artifact;
3. theorem status of the submitted carrier/formula inside SFT; and
4. the distinct SFT-native reconstruction.

It is a reporting layer over already admitted engine receipts.  It does not
alter the frozen admission engine or create a new outcome census.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/openai_ten_advances_2026_sft_source_validity_registry_v2.json"
COMPLETENESS = ROOT / "audits/OPENAI_2026_SFT_SOURCE_VALIDITY_COMPLETENESS_2026-08-02_V2.json"
LEAN_REPORT = ROOT / "generated/lean4_validation/reports/openai_2026_source_validity_lean4.json"
WHOLE_MODEL = ROOT / "generated/lean4_validation/reports/whole_model_validation.json"
OUT_JSON = ROOT / "audits/OPENAI_2026_SFT_COMPATIBILITY_CORRECTED_2026-08-02_V2.json"
OUT_MD = ROOT / "audits/OPENAI_2026_SFT_COMPATIBILITY_CORRECTED_2026-08-02_V2.md"


SUPERSEDED = [
    {
        "path": "frontier/openai_ten_advances_2026/STRICT_SFT_PROOF_DISPROOF_OF_OPENAI_TEN_ADVANCES_V0_1.md",
        "status": "SUPERSEDED_CATEGORY_ERROR",
        "reason": "It treated non-admission of a conventional carrier as the ordinary logical negation of the mathematical conclusion.",
    },
    {
        "path": "frontier/openai_ten_advances_2026/STRICT_SFT_PROOF_DISPROOF_OF_OPENAI_TEN_ADVANCES_V0_2.md",
        "status": "SUPERSEDED_CATEGORY_ERROR",
        "reason": "It retained the same invalid transfer from carrier exclusion to conclusion negation.",
    },
    {
        "path": "frontier/openai_ten_advances_2026/conclusion_verdict_report.json",
        "status": "SUPERSEDED_CATEGORY_ERROR",
        "reason": "Its verdict coordinate was not the registered source-validity proposition and is not an engine-admitted disproof of the exact artifact.",
    },
    {
        "path": "frontier/openai_ten_advances_2026/conclusion_translation_census.json",
        "status": "SUPERSEDED_CATEGORY_ERROR",
        "reason": "Its translation table did not establish a total truth-preserving correspondence to the exact source artifacts.",
    },
    {
        "path": "frontier/openai_ten_advances_2026/conclusion_verdict_independent_verification.json",
        "status": "SUPERSEDED_WITH_PARENT_VERDICT",
        "reason": "Independent replay of the wrong target does not repair the target error.",
    },
    {
        "path": "frontier/openai_ten_advances_2026/FORMAL_VERIFICATION_IS_NOT_FOUNDATIONAL_DERIVATION_COUNTERPAPER_V0_1.md",
        "status": "HISTORICAL_PRECURSOR_SUPERSEDED_BY_V2",
        "reason": "Its artifact boundary was directionally correct, but it predated engine-admitted source-validity obligations and the corrected Lean no-transfer result.",
    },
    {
        "path": "frontier/openai_ten_advances_2026/FORMAL_VERIFICATION_IS_NOT_FOUNDATIONAL_DERIVATION_COUNTERPAPER_V0_2.md",
        "status": "HISTORICAL_PRECURSOR_SUPERSEDED_BY_V2",
        "reason": "Its artifact boundary is retained only through the new source-bound engine receipts, not through its former comparison report.",
    },
]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_value(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, Any]:
    registry = load(REGISTRY)
    completeness = load(COMPLETENESS)
    lean = load(LEAN_REPORT)
    whole = load(WHOLE_MODEL)
    completeness_by_claim = {row["claim_id"]: row for row in completeness["rows"]}

    if completeness["status"] != "PASS" or not completeness["all_twelve_chains_pass"]:
        raise RuntimeError("source-validity completeness gate is not closed")
    if lean["status"] != "PASS" or lean["disproved_count"] != 12 or lean["open_count"] != 0:
        raise RuntimeError("Lean source-validity gate is not closed")
    if whole["status"] != "PASS" or whole["issue_count"] != 0:
        raise RuntimeError("whole-model Lean gate is not closed")

    rows: list[dict[str, Any]] = []
    for source in registry["rows"]:
        claim_id = source["claim_id"]
        completeness_row = completeness_by_claim[claim_id]
        package = ROOT / "claims" / claim_id
        correspondence = load(package / "source_validity_correspondence_certificate_v2.json")
        certificate = load(package / "certificate.json")
        target = load(package / "source_validity_target_v2.json")

        if completeness_row["source_artifact_validity"] != "DISPROVED":
            raise RuntimeError(f"{claim_id}: artifact validity is not disproved")
        if correspondence["total_truth_preserving_admission_exists"] is not False:
            raise RuntimeError(f"{claim_id}: total admission was not eliminated")
        if correspondence["native_reconstruction_transfers_source_validity"] is not False:
            raise RuntimeError(f"{claim_id}: invalid native-to-source transfer remains")
        if certificate["actual_contradiction_derived"] is not True:
            raise RuntimeError(f"{claim_id}: actual contradiction missing")

        rows.append(
            {
                "ordinal": source["ordinal"],
                "atomic_id": source["atomic_id"],
                "owner": source["owner"],
                "claim_id": claim_id,
                "exact_frozen_declaration": source["declaration"],
                "source_file": source["source_file"],
                "source_statement_hash": source["source_statement_hash"],
                "exact_quantifier_and_conjunct_order": source["source_quantifier_and_conjunct_order"],
                "registered_sft_proposition": source["sft_validity_proposition"],
                "registered_negation": target["registered_negation"],
                "source_artifact_sft_validity": "DISPROVED",
                "total_truth_preserving_sft_admission": "DOES_NOT_EXIST",
                "submitted_carrier_status_in_sft": "EXCLUDED_CLOSED_NO_SFT_THEOREM_STATUS",
                "compatibility_verdict": "INCOMPATIBLE_WITH_SFT",
                "ordinary_conclusion_negation_from_carrier_rejection": "PROHIBITED_INVALID_INFERENCE",
                "necessary_source_component": source["necessary_source_component"],
                "domain_contradiction": source["domain_contradiction"],
                "source_declared_axioms": source["source_declared_axioms"],
                "sft_registered_axioms": [],
                "governing_preexisting_claims": source["governing_preexisting_claims"],
                "native_reconstruction_claim_id": source["reconstruction_claim_id"],
                "native_reconstruction_status": "PROVED_DISTINCT",
                "native_reconstruction_validates_source_artifact": False,
                "lean_theorem": completeness_row["lean_theorem"],
                "engine_receipt_hash": completeness_row["engine_receipt_hash"],
                "proof_chain_passed": completeness_row["passed"],
                "open": False,
            }
        )

    result: dict[str, Any] = {
        "schema": "sft-openai-2026-corrected-compatibility/2",
        "audit_date": "2026-08-02",
        "status": "PASS",
        "scope": "Compatibility and theorem authority of the exact frozen OpenAI artifacts inside the admitted Smithian Fold Theory model.",
        "closed_classification": {
            "source_artifacts_incompatible": 12,
            "source_artifact_validity_disproved": 12,
            "total_truth_preserving_admissions": 0,
            "submitted_carriers_excluded": 12,
            "native_reconstructions_proved_distinct": 12,
            "native_to_source_validity_transfers": 0,
            "open": 0,
        },
        "logical_correction": {
            "category_error_removed": "An SFT-native proof P_SFT is not a proof of the exact imported artifact P_OpenAI unless a total truth-preserving correspondence is proved.",
            "correct_target": "Not SFTValid(exact frozen OpenAI artifact)",
            "correct_result": "The correct target is derived for all twelve artifacts by contradiction from the empty SFT axiom vector and admitted-carrier law against each source-bound nonempty axiom vector and theorem-specific excluded carrier.",
            "no_transfer_theorem": "The separately admitted SFT reconstruction does not validate the source artifact.",
            "closed_outside_status": "The submitted conventional carrier/formula has no SFT theorem status; this is a closed exclusion, not an open SFT obligation.",
        },
        "ownership": completeness["ownership"],
        "proof_totals": completeness["proof_totals"],
        "engine_seal": completeness["engine_seal"],
        "verification_authority_seal": completeness["verification_authority_seal"],
        "registry_identity": registry["registry_identity"],
        "completeness_audit_identity": completeness["audit_identity"],
        "lean_report_hash": file_hash(LEAN_REPORT),
        "whole_model": {
            "status": whole["status"],
            "claims": whole["claim_count"],
            "accepted_claims": whole["accepted_claim_count"],
            "branches": whole["branch_count"],
            "candidates": whole["candidate_count"],
            "decisions": whole["decision_count"],
            "controls": whole["control_count"],
            "source_binding_issues": whole["source_binding_issue_count"],
            "issues": whole["issue_count"],
        },
        "rows": rows,
        "supersession": SUPERSEDED,
    }
    result["audit_identity"] = sha256_value(result)
    return result


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Corrected SFT Compatibility Audit of OpenAI's 2026 Mathematical Artifacts",
        "",
        "Status: **PASS — CLOSED 12/12**",
        "",
        "The exact submitted OpenAI artifacts are **incompatible with SFT**. Their SFT-validity propositions are **disproved 12/12**. The separately derived SFT-native results are **proved 12/12 as distinct reconstructions**, and the Lean-verified no-transfer theorem prevents those reconstructions from being used to validate the imported artifacts.",
        "",
        "## Corrected logical classification",
        "",
        "- `P_OpenAI`: the exact frozen source artifact, including its quantifiers, carriers, imported proof environment, and declared axiom vector.",
        "- `P_SFT`: the separately admitted SFT-native reconstruction.",
        "- Proving `P_SFT` does not prove `SFTValid(P_OpenAI)`.",
        "- A total truth-preserving SFT admission/correspondence was tested and eliminated for every artifact.",
        "- Therefore `¬SFTValid(P_OpenAI)` is proved for all twelve; `P_SFT` remains a distinct SFT theorem and transfers no validity backward.",
        "- The submitted carrier/formula is categorically excluded from SFT theoremhood. This is a closed classification with **0 open obligations**.",
        "",
        "The corrected audit does **not** use carrier rejection as though it were the ordinary logical negation of a proposition stated in a different object language. The actual negated proposition is the registered SFT-validity proposition of the exact source artifact.",
        "",
        "## Twelve closed compatibility verdicts",
        "",
        "| # | Owner | Exact frozen declaration | SFT validity | Total admission | Native result | Transfer |",
        "|---:|---|---|---|---|---|---|",
    ]
    for row in result["rows"]:
        lines.append(
            f"| {row['ordinal']} | {row['owner']} | `{row['exact_frozen_declaration']}` | DISPROVED | DOES NOT EXIST | PROVED DISTINCT | FALSE |"
        )
    lines.extend(
        [
            "",
            "## Per-artifact contradiction boundary",
            "",
        ]
    )
    for row in result["rows"]:
        lines.extend(
            [
                f"### {row['ordinal']}. `{row['exact_frozen_declaration']}`",
                "",
                f"**Owner:** `{row['owner']}`  ",
                f"**Registered proposition:** `{row['registered_sft_proposition']}`  ",
                f"**Verdict:** **INCOMPATIBLE WITH SFT; SOURCE VALIDITY DISPROVED.**  ",
                f"**Exact source order:** {'; '.join(row['exact_quantifier_and_conjunct_order'])}.  ",
                f"**Necessary imported component:** {row['necessary_source_component']}.  ",
                f"**SFT contradiction:** {row['domain_contradiction']}  ",
                f"**Axiom contradiction:** SFT validity forces `[]`; the exact source exposes `{row['source_declared_axioms']}`.  ",
                f"**Distinct admitted reconstruction:** `{row['native_reconstruction_claim_id']}` — `PROVED_DISTINCT`; transfer to source validity is `false`.  ",
                f"**Receipt:** `{row['engine_receipt_hash']}`.  ",
                f"**Lean theorem:** `{row['lean_theorem']}`.",
                "",
            ]
        )
    lines.extend(
        [
            "## What was corrected",
            "",
            "The earlier conclusion-verdict layer confused three different statements: rejection of a carrier, negation of a conventional mathematical proposition, and invalidity of an imported artifact inside SFT. Only the third is established by the source-bound contradiction. The new V2 obligations register that proposition directly, derive its actual negation, and prove that the native reconstruction does not transfer validity to the source.",
            "",
            "| Historical artifact | Corrected status | Reason |",
            "|---|---|---|",
        ]
    )
    for item in result["supersession"]:
        lines.append(f"| `{item['path']}` | {item['status']} | {item['reason']} |")
    wm = result["whole_model"]
    lines.extend(
        [
            "",
            "## Closure evidence",
            "",
            f"- Source-validity proof chains: **12/12 PASS; 0 open**.",
            f"- Ownership: **{result['ownership']['mathematics']} Mathematics / {result['ownership']['computation']} Classical Computation / {result['ownership']['quantum_computation']} Quantum Computation**.",
            f"- Execution: **{result['proof_totals']['steps']} proof steps / {result['proof_totals']['checks']} executable checks / {result['proof_totals']['candidates']} candidates and decisions / {result['proof_totals']['controls']} controls**.",
            f"- Whole-model Lean: **{wm['status']} — {wm['claims']}/{wm['accepted_claims']} claims, {wm['branches']} branches, {wm['source_binding_issues']} source-binding issues, {wm['issues']} total issues**.",
            f"- Engine seal: `{result['engine_seal']}`.",
            f"- Verification-authority seal: `{result['verification_authority_seal']}`.",
            f"- Audit identity: `{result['audit_identity']}`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    result = build()
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(result), encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"wrote {OUT_MD.relative_to(ROOT)}")
    print(result["audit_identity"])


if __name__ == "__main__":
    main()
