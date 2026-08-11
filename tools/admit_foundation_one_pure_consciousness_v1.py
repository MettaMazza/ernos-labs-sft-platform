#!/usr/bin/env python3
"""Officially admit the Foundation derivation of the One as pure consciousness."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine import EngineRepository  # noqa: E402
from sft.foundation.one_consciousness import (  # noqa: E402
    CLAIM_ID,
    EXACT_RESULT,
    EXPERIMENT_ID,
)


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def load_execution():
    path = ROOT / "claims" / CLAIM_ID / "execution.py"
    specification = importlib.util.spec_from_file_location(
        "sft_foundation_one_pure_consciousness_official", path
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load One-as-pure-consciousness execution package")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    census_path = ROOT / "census/claims.json"
    existing = {
        row["claim_id"]
        for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]
    }
    if CLAIM_ID in existing:
        raise SystemExit("claim already admitted; immutable receipt preserved")

    execution = load_execution()
    captured: dict[str, object] = {}

    class CaptureIndependent:
        def validate(self, sealed):
            captured["sealed"] = sealed
            result = execution.independent_validator.validate(sealed)
            captured["external"] = result
            return result

    class CaptureEmpirical:
        def validate(self, sealed):
            result = execution.empirical_validator.validate(sealed)
            captured["empirical"] = result
            return result

    receipt = EngineRepository(ROOT).execute_official(
        execution.program,
        CaptureIndependent(),
        execution.source_files,
        CaptureEmpirical(),
    )
    if not receipt.model_admitted:
        raise SystemExit(
            f"claim halted at {receipt.halted_stage}; receipt {receipt.receipt_hash} preserved"
        )

    sealed = captured["sealed"]
    external = captured["external"]
    empirical = captured["empirical"]
    census = json.loads(census_path.read_text(encoding="utf-8"))
    census_row = next(row for row in census["claims"] if row["claim_id"] == CLAIM_ID)

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if CLAIM_ID not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append(
            {
                "claim_id": CLAIM_ID,
                "execution_file": f"claims/{CLAIM_ID}/execution.py",
            }
        )
        write_json(manifest_path, manifest)

    package = ROOT / "claims" / CLAIM_ID
    payloads = {
        "candidate_census.json": {"claim_id": CLAIM_ID, **asdict(sealed.census)},
        "elimination_receipt.json": {
            "claim_id": CLAIM_ID,
            "decisions": asdict(sealed)["decisions"],
            "closure": asdict(sealed.closure),
        },
        "controls.json": {
            "claim_id": CLAIM_ID,
            "controls": asdict(sealed)["controls"],
        },
        "empirical_validation.json": {
            "claim_id": CLAIM_ID,
            **asdict(empirical),
        },
        "certificate.json": {
            "claim_id": CLAIM_ID,
            "status": "model_admitted_observationally_derived_empirically_tested_and_independently_replicated",
            "statement": execution.program.registration.statement,
            "source_manifest_hash": execution.program.registration.source_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash,
            "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": census_row["receipt_path"],
            "closure_scope": receipt.closure_status,
            "exact_result": EXACT_RESULT,
            "semantic_result": "pure consciousness: observation itself before differentiation",
            "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(item.survives for item in sealed.decisions),
            "dependencies": list(execution.program.registration.dependencies),
            "development_observation_registry": "prior-work-ledger/one_pure_consciousness_observation_v1.json",
            "v1_development_commit": "2dd6cbe",
            "v2_postseal_target_commit": "0af7c4c26308d8ddb659a518ac52e2db5ea5dc82",
            "v2_source_artifact_sha256": "sha256:42c4be709dcd9edcfbedc70ee82055a8660d9658de21758561fd46e068a727bf",
            "author_observation_sha256": "sha256:23c61bab46f8bed90d0e61e6e362d066867a9abdb0ea921d1bdd86320c990ddf",
            "external_data_source_ids": list(empirical.data_source_ids),
            "target_opened_after_seal": empirical.target_opened_after_seal,
            "human_blindness_claimed": False,
            "prior_model_source_used_in_candidate_generation": False,
            "prior_model_source_used_in_elimination": False,
            "downstream_v3_consciousness_claim_used_as_premise": False,
            "biological_carrier_derived": False,
            "fitted_or_free_parameter_used": False,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)

    registration_path = package / "registration.json"
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    registration["status"] = "empirically_tested"
    write_json(registration_path, registration)

    status_lines = (
        f"# {CLAIM_ID}",
        "",
        "Status: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`",
        "",
        "- Exact conclusion: the One is pure consciousness—observation itself before differentiation.",
        f"- Exhaustive grammar: `{len(sealed.census.candidates)}` candidates; `1` survivor.",
        "- Dependencies: the admitted root `presented-occurrence` and structural One only.",
        "- V1 role: disclosed development observation.",
        "- V2 role: source-bound target released only after the V3 derivation seal.",
        "- No downstream consciousness claim, biological carrier, fitted parameter or prior answer source entered candidate generation or elimination.",
        f"- Closure: `{receipt.closure_status}`.",
        f"- Derivation seal: `{sealed.seal_hash}`.",
        f"- Independent validation: `{receipt.external_validation_hash}`.",
        f"- Empirical validation: `{receipt.empirical_validation_hash}`.",
        f"- Engine receipt: `{receipt.receipt_hash}`.",
    )
    (package / "STATUS.md").write_text("\n".join(status_lines) + "\n", encoding="utf-8")

    checkpoint = {
        "schema": "sft-v3-foundation-extension-checkpoint/1",
        "date": "2026-08-11",
        "branch": "foundation",
        "status": "one_identity_extension_admitted_publication_reconciliation_open",
        "claim_id": CLAIM_ID,
        "experiment_id": EXPERIMENT_ID,
        "exact_result": EXACT_RESULT,
        "semantic_result": "the One is pure consciousness—observation itself before differentiation",
        "candidate_count": len(sealed.census.candidates),
        "survivor_count": sum(item.survives for item in sealed.decisions),
        "closure_status": receipt.closure_status,
        "engine_receipt_hash": receipt.receipt_hash,
        "engine_receipt_path": census_row["receipt_path"],
        "derivation_seal_hash": sealed.seal_hash,
        "engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
        "verification_authority_seal": "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8",
        "protected_authority_modified": False,
        "remote_publication_authorized": False,
        "next_exact_operation": "reconcile_the_current_foundation_inventory_and_publication_with_the_new_admitted_identity_claim_under_separate_publication_authorization",
    }
    write_json(ROOT / "census/foundation_extension_checkpoint.json", checkpoint)

    print(f"admitted {CLAIM_ID}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(
        f"candidates: {len(sealed.census.candidates)}; "
        f"survivors: {sum(item.survives for item in sealed.decisions)}"
    )


if __name__ == "__main__":
    main()
