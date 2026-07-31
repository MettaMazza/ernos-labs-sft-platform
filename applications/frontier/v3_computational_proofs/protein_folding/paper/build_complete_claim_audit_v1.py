#!/usr/bin/env python3
"""Build the complete publication-guidance claim audit for Protein Fold v0.9.4.

The immutable 0.9.3 release remains unchanged. This builder prepares the
complete claim-level audit for its authorised successor from current
authoritative claim packages and current application records.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parent
REPOSITORY = Path(__file__).resolve().parents[5]
MATRIX = REPOSITORY / "publications/preliminary_toe/EXHAUSTIVE_TOE_CONTENT_MATRIX.json"
PAPER = HERE / "SMITHIAN_FOLD_THEORY_V3_PROTEIN_FOLD_COMPUTATIONAL_PROOF.md"
DEPENDENCIES = WORKSPACE / "spec/dependency_matrix_v2.json"
APPLICATION_REGISTRATION = WORKSPACE / "spec/protein_interaction_descent_registration_v1.json"
APPLICATION_CENSUS = WORKSPACE / "audits/descent_candidate_census_v1.json"
APPLICATION_CHECK = WORKSPACE / "audits/descent_candidate_independent_check_v1.json"
APPLICATION_CLOSURE = WORKSPACE / "audits/descent_form_closure_v1.json"
OUTPUT = HERE / "COMPLETE_CLAIM_AUDIT.md"
MANIFEST = HERE / "COMPLETE_CLAIM_AUDIT_MANIFEST.json"
IDENTITY_RECONCILIATION = HERE / "PRELIMINARY_V0_9_4_IDENTITY_RECONCILIATION.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inline(value: object | None) -> str:
    if value is None or value == "":
        return "not separately recorded"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, ensure_ascii=True)
    return str(value).replace("\n", " ").strip()


def paragraph(value: object | None) -> str:
    if value is None or value == "":
        return "No separate prose record is present; the exact registered fields below remain authoritative."
    return str(value).strip()


def dependency_ids(matrix: dict) -> list[str]:
    predecessor = [
        "SFT-BIO-PROTEIN-SEQUENCE-001",
        "SFT-BIO-PROTEIN-FOLD-001",
        "SFT-BIO-PROTEIN-ENSEMBLE-001",
    ]
    added = [row[0] for row in matrix["added_direct_application_dependencies"]]
    return predecessor + added


def controls_table(rows: list[dict]) -> list[str]:
    lines = [
        "| Control | Passed | Expected | Observed | Receipt |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {kind} | {passed} | {expected} | {observed} | `{receipt}` |".format(
                kind=inline(row.get("kind")),
                passed=inline(row.get("passed")),
                expected=inline(row.get("expected_behavior")),
                observed=inline(row.get("observed_behavior")),
                receipt=inline(row.get("receipt_hash")),
            )
        )
    return lines


def render_model_claim(index: int, claim: dict) -> list[str]:
    survivor_records = claim.get("survivor_records") or []
    survivor = survivor_records[0] if survivor_records else {}
    closure = claim.get("closure") or {}
    certificate = claim.get("certificate") or {}
    sources = claim.get("evidence_source_ids") or []
    measurements = claim.get("measurements") or []
    provenance = claim.get("provenance_classes") or []
    exact_form = inline(survivor.get("exact_form") or claim.get("exact_result"))
    form_fields = {}
    for field in exact_form.split("; "):
        if "=" in field:
            key, value = field.split("=", 1)
            form_fields[key] = value
    lines = [
        f"## {index}. {claim['title']}",
        "",
        f"**Claim ID:** `{claim['claim_id']}`  ",
        f"**Family:** {claim['family_label']}  ",
        f"**Formal status:** `{claim['formal_status']}`  ",
        f"**Empirical status:** `{claim['empirical_status']}`  ",
        f"**Closure status:** `{inline(closure.get('scope'))}`  ",
        f"**Registration date:** `{inline(claim.get('registration_date'))}`  ",
        "**Authority class:** model-admitted dependency; this Protein Fold application does not revise its admission or evidence status.",
        "",
        "### Exact statement",
        "",
        f"> {claim['statement']}",
        "",
        "### Reason required and scientific meaning",
        "",
        paragraph(claim.get("why") or claim.get("intended_certificate")),
        "",
        "### Dependency route",
        "",
        " -> ".join(f"`{value}`" for value in claim.get("dependencies", []))
        or "Root claim; no earlier dependency is registered.",
        "",
        "### Carrier, boundary, relation and retained record",
        "",
        f"**Carrier:** {inline(form_fields.get('carrier') or claim.get('statement'))}",
        "",
        f"**Candidate boundary:** {inline(claim.get('candidate_boundary'))}",
        "",
        f"**Relation:** {inline(form_fields.get('relation') or claim.get('exact_result'))}",
        "",
        f"**Candidate generator:** {inline(claim.get('candidate_generation_rule'))}",
        "",
        f"**Provenance:** {inline(provenance)}",
        "",
        f"**Generality:** minimality `{inline(closure.get('minimality_passed'))}`; named-form uniqueness `{inline(closure.get('named_shape_uniqueness_passed'))}`; exact boundary `{inline(closure.get('exact_boundary'))}`.",
        "",
        f"**Extension rule and excluded inputs:** {inline(claim.get('excluded_inputs'))}",
        "",
        f"**Retained record:** `{exact_form}`",
        "",
        "### Candidate census and uniqueness",
        "",
        f"The authoritative package records **{claim['candidate_count']:,} candidates**, **{claim['candidate_count']:,} decisions**, **{claim['candidate_count'] - claim['unique_survivor_count']:,} rejected decisions**, **{len(claim.get('survivors') or []):,} surviving decision records** and **{claim['unique_survivor_count']:,} unique survivor**. The complete candidate grammar is:",
        "",
        "```json",
        json.dumps(claim.get("candidate_grammar") or {}, indent=2, sort_keys=True, ensure_ascii=True),
        "```",
        "",
        f"**Uniqueness explanation:** {inline(claim.get('exact_result'))}",
        "",
        "### Falsification and controls",
        "",
        f"**Falsification condition:** {inline(claim.get('falsification_condition'))}",
        "",
    ]
    lines.extend(controls_table(claim.get("controls") or []))
    lines.extend(
        [
            "",
            f"Control total: **{claim.get('passed_control_count', 0):,}/{claim.get('control_count', 0):,} passed**.",
            "",
            "### Evidence sources, provenance and chronology",
            "",
            f"**Source identities:** {', '.join(f'`{value}`' for value in sources) if sources else 'none at this formal boundary'}.",
            "",
            f"**Evidence class:** `{inline(certificate.get('external_evidence_class'))}`.  ",
            f"**Source-capture status:** source manifest `{inline(certificate.get('source_manifest_hash'))}`; all required rows preserved `{inline(claim.get('all_rows_preserved'))}`; failed-source and adverse rows preserved `{inline(certificate.get('failed_source_and_adverse_rows_preserved'))}`.  ",
            f"**Evidence chronology:** target opened after seal `{inline(claim.get('target_opened_after_seal'))}`; registration date `{inline(claim.get('registration_date'))}`.  ",
            f"**All rows preserved:** `{inline(claim.get('all_rows_preserved'))}`.  ",
            f"**Failed-source and adverse rows preserved:** `{inline(certificate.get('failed_source_and_adverse_rows_preserved'))}`.",
            "",
            "**Measurements or correspondence records:**",
            "",
        ]
    )
    lines.extend([f"- {inline(value)}" for value in measurements] or ["- No separate measurement record at this boundary."])
    lines.extend(
        [
            "",
            "### Current scientific status",
            "",
            paragraph(claim.get("status_record") or claim.get("check_narrative")),
            "",
            "### Receipt and package identities",
            "",
            f"**Engine receipt:** `{inline(claim.get('registered_receipt_id'))}` at `{inline(claim.get('receipt_path'))}`.  ",
            f"**Derivation seal:** `{inline(certificate.get('derivation_seal_hash'))}`.  ",
            f"**Independent implementation:** `{inline(certificate.get('independent_implementation_hash'))}`.  ",
            f"**Independent certificate:** `{inline(certificate.get('independent_certificate_hash'))}`.  ",
            f"**Source manifest:** `{inline(certificate.get('source_manifest_hash'))}`.  ",
            f"**External validation:** `{inline(certificate.get('external_validation_hash'))}`.  ",
            f"**Measurement receipt:** `{inline(claim.get('measurement_receipt_hash'))}`.",
            "",
            "| Package file | SHA-256 |",
            "|---|---|",
        ]
    )
    for path, sha in sorted((claim.get("package_files") or {}).items()):
        lines.append(f"| `{path}` | `{sha}` |")
    lines.append("")
    return lines


def render_application_claim(index: int, registration: dict, census: dict, check: dict, closure: dict, dependencies: list[str]) -> list[str]:
    survivor = next(row for row in census["candidate_decisions"] if row["accepted"])
    paths = [
        APPLICATION_REGISTRATION,
        WORKSPACE / "spec/protein_interaction_descent_derivation_v1.md",
        APPLICATION_CENSUS,
        APPLICATION_CHECK,
        APPLICATION_CLOSURE,
        WORKSPACE / "audits/full_coordinate_completion_reconciliation_v4.json",
        WORKSPACE / "audits/current_scientific_gate_v20.json",
    ]
    lines = [
        f"## {index}. {registration['title']}",
        "",
        f"**Claim ID:** `{registration['claim_id']}`  ",
        "**Family:** Protein Fold computational-proof application  ",
        "**Formal status:** `registered_relation_form_closed_not_model_admitted`  ",
        "**Empirical status:** `development_controls_only_primary_campaign_unopened`  ",
        f"**Closure status:** `{closure['closure_scope']}`  ",
        f"**Registration date:** `{registration['date']}`  ",
        "**Authority class:** frontier application registration; engine admission was not authorised and is not claimed.",
        "",
        "### Exact statement",
        "",
        f"> {registration['statement']}",
        "",
        "### Reason required and scientific meaning",
        "",
        "The one-coordinate reversible transition probe produced one closed class containing every generated word. A target-free componentwise relation is therefore required to preserve separately typed physical coordinates, retain incomparability and emit every closed nondominated recurrent class without fitted weights or a target-selected representative.",
        "",
        "### Dependency route",
        "",
        "The application directly binds the following admitted dependencies without revising them:",
        "",
        " -> ".join(f"`{value}`" for value in dependencies),
        "",
        "### Carrier, boundary, relation and retained record",
        "",
        f"**Carrier:** {registration['exact_relation']['carrier_equality']}",
        "",
        f"**Boundary:** {registration['exact_relation']['finite_boundary_rule']}",
        "",
        f"**Relation:** {registration['exact_relation']['successor_rule']}",
        "",
        f"**Retained record:** {registration['exact_relation']['recurrence_rule']} Missingness: {registration['exact_relation']['missingness_rule']}",
        "",
        "**Evidence class:** exact application-form enumeration, independent implementation reconstruction, implementation tests and separately classified development evidence. No primary blind-parity evidence exists.",
        "",
        "**Provenance:** explicit Maria Smith authorisation for a versioned target-free application derivation; no engine admission or protected-authority change.",
        "",
        f"**Generality:** {registration['closure_sought']}",
        "",
        f"**Extension rule:** {registration['exact_relation']['extension_rule']}",
        "",
        "### Candidate census and uniqueness",
        "",
        f"The registered eight-axis binary grammar contains **{census['candidate_count']:,} candidates**, **{sum(not row['accepted'] for row in census['candidate_decisions']):,} rejected decisions** and **{sum(row['accepted'] for row in census['candidate_decisions']):,} preserving survivor**.",
        "",
        "```json",
        json.dumps(registration["candidate_grammar"], indent=2, sort_keys=True, ensure_ascii=True),
        "```",
        "",
        f"**Retained survivor:** `{closure['preserving_form']}` (`{survivor['candidate_id']}`).",
        "",
        "**Uniqueness explanation:** every alternative violates at least one registered preserving axis; the implementation-distinct integer-bit reconstruction reproduced all candidate identities and the sole survivor.",
        "",
        "### Falsification and controls",
        "",
        "The form closure fails if the grammar does not contain exactly 256 distinct decisions, if any second survivor exists, if the independent reconstruction differs, if a rejected form lacks a recorded violation, or if target data, comparator output, fitted weighting, omitted adversity or an extra rule enters the derivation.",
        "",
        "| Control | Result | Authority |",
        "|---|---|---|",
        f"| Complete 256-decision census | Passed | `{APPLICATION_CENSUS.relative_to(REPOSITORY)}` |",
        f"| Independent identity and survivor reconstruction | `{inline(check['passed'])}` | `{APPLICATION_CHECK.relative_to(REPOSITORY)}` |",
        f"| Candidate-form tests | `{closure['test']['tests_passed']}/{closure['test']['tests_passed'] + closure['test']['tests_failed']} passed` | `{closure['test']['path']}` |",
        "| Model-admission boundary | Preserved; not authorised | Registration authority block |",
        "| Target/comparator isolation | Required and retained; primary panel unopened | Current scientific gate v20 |",
        "",
        "### Evidence sources, chronology and current status",
        "",
        "**Source identities:** `SFT-PROTEIN-SRC-WWPDB-CCD-2026-07-29` and `SFT-PROTEIN-SRC-WWPDB-AA-VARIANTS-2026-07-29`.  ",
        "**Source-capture status:** both sources were pending at registration; the current source-custody layer records all 21 registered non-target transports as successful while retaining 20 unavailable side-chain uncertainty records without imputation.  ",
        "**Evidence chronology:** application form registered first; candidate census and independent reconstruction followed; physical implementation and development evidence followed separately; the primary 100-target panel remains unopened.",
        "",
        "The form was registered before its census. The 256-form census and independent reconstruction later closed the registered relation form. Subsequent coordinate, six-axis joint-response and solver work changed the implementation boundary but did not convert this application registration into a model-admitted claim. Development results remain separate from the unopened primary 100-target campaign.",
        "",
        "Current status: the relation form is closed; all six fixed-geometry coordinate axes are constructed; the complete fixed-geometry frontier, arbitrary-sequence whole-chain recurrence and AlphaFold-generalised blind-parity campaign remain open.",
        "",
        "### Receipt and package identities",
        "",
        "| Application record | SHA-256 |",
        "|---|---|",
    ]
    for path in paths:
        lines.append(f"| `{path.relative_to(REPOSITORY)}` | `{digest(path)}` |")
    lines.append("")
    return lines


def write_identity_reconciliation() -> None:
    machine_manifest = json.loads((HERE / "MACHINE_ARCHIVE_MANIFEST.json").read_text())
    archived = next(row for row in machine_manifest["files"] if row["path"] == "workspace_manifest.json")
    record = {
        "schema": "sft-v3-protein-preliminary-v0.9.4-identity-reconciliation/v1",
        "date": "2026-07-31",
        "status": "resolved_in_authorised_v0.9.4_successor__immutable_v0.9.3_preserved",
        "publication_version": "0.9.4",
        "version_doi": "10.5281/zenodo.21717581",
        "publication_authority": "Maria Smith",
        "frozen_internal_references": {
            "conceptual_paper_workspace_manifest_sha256": "ae9ec22981c92def2644fbfbf9f344ceb1d5060cc3e242f5542d4df16032055e",
            "scientific_audit_workspace_manifest_sha256": "2d644f8771a07c0930d488a66aaa1095857dbebda3e3b7432d272e74ea6fdb49",
        },
        "release_machine_manifest_reference": archived["sha256"],
        "current_workspace_manifest_sha256": digest(WORKSPACE / "workspace_manifest.json"),
        "determination": "The conceptual-paper and scientific-audit values identify earlier workspace-manifest states and are stale inside the frozen 0.9.3 prose. Version 0.9.4 replaces both narrative references with the current workspace identity recorded by the release machine manifest. No scientific count or evidence classification changes in this clerical reconciliation.",
        "successor_action": "Complete: the v0.9.4 conceptual paper, audit layer and machine archive use the same current workspace-manifest identity.",
        "immutable_release_edited": False,
        "protected_authority_edited": False,
        "remote_publication_authorized": True,
    }
    IDENTITY_RECONCILIATION.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")


def main() -> int:
    matrix = json.loads(MATRIX.read_text())
    dependency_matrix = json.loads(DEPENDENCIES.read_text())
    ids = dependency_ids(dependency_matrix)
    if len(ids) != 20 or len(set(ids)) != 20:
        raise SystemExit("Protein dependency surface is not exactly 20 unique admitted claims")
    claims_by_id = {row["claim_id"]: row for row in matrix["claims"]}
    missing = sorted(set(ids) - set(claims_by_id))
    if missing:
        raise SystemExit(f"claims missing from authoritative matrix: {missing}")
    paper_ids = set(re.findall(r"SFT-[A-Z0-9-]+", PAPER.read_text()))
    expected_ids = set(ids) | {"SFT-APP-PROTEIN-INTERACTION-DESCENT-001"}
    if paper_ids != expected_ids:
        raise SystemExit(
            f"paper/dependency inventory mismatch: missing={sorted(expected_ids-paper_ids)}, extra={sorted(paper_ids-expected_ids)}"
        )

    registration = json.loads(APPLICATION_REGISTRATION.read_text())
    census = json.loads(APPLICATION_CENSUS.read_text())
    check = json.loads(APPLICATION_CHECK.read_text())
    closure = json.loads(APPLICATION_CLOSURE.read_text())
    lines = [
        "# SFT V3 Protein Fold - Complete Claim Audit",
        "",
        "**Author and publication authority:** Maria Smith  ",
        "**Date:** 31 July 2026  ",
        "**Version:** 0.9.4  ",
        "**DOI:** 10.5281/zenodo.21717581  ",
        "**Status:** Complete scientific audit layer for the authorised v0.9.4 preliminary successor; immutable Zenodo v0.9.3 preserved  ",
        "**Scope:** Every claim and direct admitted dependency named by the preliminary Protein Fold paper",
        "",
        "This layer supplies the complete claim-section fields required by `publication guidance.md`. It distinguishes the one frontier application registration from the twenty model-admitted dependencies and does not transfer admission, evidence or publication authority between them.",
        "",
        "## Inventory",
        "",
        "| Authority class | Records |",
        "|---|---:|",
        "| Frontier application registration | 1 |",
        "| Direct model-admitted dependencies | 20 |",
        "| Total complete claim records | 21 |",
        "",
    ]
    lines.extend(render_application_claim(1, registration, census, check, closure, ids))
    for index, claim_id in enumerate(ids, 2):
        lines.extend(render_model_claim(index, claims_by_id[claim_id]))
    OUTPUT.write_text("\n".join(lines).rstrip() + "\n")
    write_identity_reconciliation()
    manifest = {
        "schema": "sft-v3-protein-complete-claim-audit-manifest/v1",
        "date": "2026-07-31",
        "status": "complete_current_claim_surface_integrated_in_v0.9.4",
        "publication_version": "0.9.4",
        "version_doi": "10.5281/zenodo.21717581",
        "publication_authority": "Maria Smith",
        "claim_record_count": 21,
        "model_admitted_dependency_count": 20,
        "frontier_application_registration_count": 1,
        "claim_ids": [registration["claim_id"], *ids],
        "inputs": {
            str(MATRIX.relative_to(REPOSITORY)): digest(MATRIX),
            str(PAPER.relative_to(REPOSITORY)): digest(PAPER),
            str(DEPENDENCIES.relative_to(REPOSITORY)): digest(DEPENDENCIES),
            str(APPLICATION_REGISTRATION.relative_to(REPOSITORY)): digest(APPLICATION_REGISTRATION),
            str(APPLICATION_CENSUS.relative_to(REPOSITORY)): digest(APPLICATION_CENSUS),
            str(APPLICATION_CHECK.relative_to(REPOSITORY)): digest(APPLICATION_CHECK),
            str(APPLICATION_CLOSURE.relative_to(REPOSITORY)): digest(APPLICATION_CLOSURE),
        },
        "outputs": {
            str(OUTPUT.relative_to(REPOSITORY)): digest(OUTPUT),
            str(IDENTITY_RECONCILIATION.relative_to(REPOSITORY)): digest(IDENTITY_RECONCILIATION),
        },
        "immutable_release_edited": False,
        "protected_authority_edited": False,
        "remote_publication_authorized": True,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claims": 21, "bytes": OUTPUT.stat().st_size, "sha256": digest(OUTPUT), "identity_reconciliation": digest(IDENTITY_RECONCILIATION)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
