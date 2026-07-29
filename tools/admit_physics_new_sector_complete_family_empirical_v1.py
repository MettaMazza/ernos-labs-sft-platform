#!/usr/bin/env python3
"""Admit complete empirical new-sector Claim 095 through the frozen engine."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_seals() -> None:
    for tool, expected in (("verify_engine_seal.py", "VALID_CANONICAL_ENGINE"), ("verify_verification_authority_seal.py", "VALID_CANONICAL_VERIFICATION_AUTHORITY")):
        completed = subprocess.run((sys.executable, str(ROOT / "tools" / tool), "--json"), cwd=ROOT, text=True, capture_output=True)
        if completed.returncode or json.loads(completed.stdout).get("status") != expected:
            raise SystemExit(completed.stdout + completed.stderr + "\nNew-sector empirical admission halted")


def load_execution():
    path = ROOT / "claims/SFT-PHYS-VALIDATION-NEW-SECTOR-COMPLETE-FAMILY-095/execution.py"
    definition = importlib.util.spec_from_file_location("sft_new_sector_empirical_submission", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load new-sector empirical execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    verify_seals()
    from sft.engine import EngineRepository
    from sft.engine.source import hash_file
    from sft.physics.new_sector_complete_family_empirical_v1 import CLAIM_ID, PREREGISTRATION_HASH, PREREGISTRATION_PATH, SOURCE_FILES, SOURCE_HASH, SOURCE_PATH, SPEC
    from sft.physics.new_sector_complete_family_empirical_validation_v1 import NewSectorCompleteFamilyMeasurementValidator

    if hash_file(ROOT / SOURCE_PATH) != SOURCE_HASH or hash_file(ROOT / PREREGISTRATION_PATH) != PREREGISTRATION_HASH:
        raise SystemExit("new-sector record or preregistration hash mismatch")
    for path, expected in SOURCE_FILES:
        if hash_file(ROOT / path) != expected:
            raise SystemExit(f"new-sector source hash mismatch: {path}")
    direct = NewSectorCompleteFamilyMeasurementValidator(ROOT).direct_source_certificate()
    if not all((direct["all_passed"], direct["standing_predictions_retained"], direct["nonobservation_not_retirement"])):
        raise SystemExit("new-sector direct source reconstruction failed")
    census_path = ROOT / "census/claims.json"
    census = json.loads(census_path.read_text(encoding="utf-8"))
    admitted = {row["claim_id"] for row in census["claims"]}
    missing = tuple(dependency for dependency in SPEC.dependencies if dependency not in admitted)
    if missing:
        raise SystemExit("new-sector empirical dependencies absent: " + ", ".join(missing))
    if CLAIM_ID in admitted:
        raise SystemExit(f"{CLAIM_ID} already has an admitted receipt")

    experiment_path = ROOT / "experiments" / "physics" / SPEC.experiment_id / "registration.json"
    write_json(experiment_path, {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": SPEC.experiment_id,
        "claim_id": CLAIM_ID,
        "evidence_mode": "observational_derivation_post_formal_seal",
        "historical_access_disclosed": True,
        "blind_numerical_prediction_claimed": False,
        "formal_predecessors_sealed_before_combined_source_record": list(SPEC.dependencies[:7]),
        "source_identity_preregistration_hash": PREREGISTRATION_HASH,
        "source_record_path": SOURCE_PATH,
        "source_record_hash": SOURCE_HASH,
        "source_hashes": dict(SOURCE_FILES),
        "target_ids": [row.target_id for row in SPEC.target_rows],
        "complete_row_policy": "retain all five sources and every favorable, adverse, absent, searched, model-dependent and unresolved row",
        "formal_relation": SPEC.exact_result,
        "falsification_condition": SPEC.falsification_condition,
        "controls": [{"kind": kind, "expected": "halt or reject on changed source, omitted result type, fabricated discovery or false retirement"} for kind in ("false_premise", "tampered_source", "tampered_artifact", "boundary", "unfavorable_measurement")],
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-28",
        "status": "registered",
    })
    execution = load_execution()
    receipt = EngineRepository(ROOT).execute_official(execution.program, execution.independent_validator, execution.source_files, execution.empirical_validator)
    if not receipt.model_admitted:
        raise RuntimeError("new-sector empirical successor did not enter the model")
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["claims"].append({"claim_id": CLAIM_ID, "execution_file": f"claims/{CLAIM_ID}/execution.py"})
    write_json(manifest_path, manifest)
    materialized = subprocess.run((sys.executable, str(ROOT / "tools/materialize_empirical_claim_evidence.py"), CLAIM_ID, SPEC.exact_result), cwd=ROOT, text=True, capture_output=True)
    if materialized.returncode:
        raise RuntimeError(materialized.stdout + materialized.stderr)
    package = ROOT / "claims" / CLAIM_ID
    write_json(package / "registration.json", {
        "$schema": "../../governance/claim.schema.json",
        "branch": "physics",
        "candidate_grammar": {"boundary": SPEC.grammar_boundary, "completeness_certificate": "generated by the untouched admission engine from the complete declared product", "generator": SPEC.generation_rule},
        "claim_id": CLAIM_ID,
        "dependencies": list(SPEC.dependencies),
        "excluded_inputs": list(SPEC.exclusions),
        "empirical_protocol": f"experiments/physics/{SPEC.experiment_id}/registration.json",
        "intended_certificate": "Complete 256-form comparison census, independent reconstruction, ten direct checks and complete standing-prediction retention.",
        "provenance_classes": ["observational_derivation"],
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-28",
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary", "unfavorable_measurement"],
        "statement": SPEC.exact_result,
        "status": "empirically_tested_and_independently_replicated",
        "title": SPEC.title,
    })
    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    (package / "STATUS.md").write_text("\n".join((
        f"# {CLAIM_ID}", "", "Status: `empirically_tested_and_independently_replicated`", "",
        "- All seven formal new-sector laws sealed before the combined record.",
        "- Known 3/8 carrier anchors and known fermion categories are retained.",
        "- Axion-like, heavy-neutral-lepton and supersymmetric classes remain searched hypotheses, not invented discoveries.",
        "- ATLAS dark-jet and missing-momentum searches support the search-class correspondence while retaining model-dependent limits.",
        "- No penta/hepta carrier, slope or Smithion mass is relabelled as measured.",
        "- Present non-observation does not retire the standing exact predictions.",
        f"- Closure: `{certificate['closure_scope']}`",
        f"- Empirical validation: `{certificate['empirical_validation_hash']}`",
        f"- Engine receipt: `{receipt.receipt_hash}`", "",
    )), encoding="utf-8")
    verify_seals()
    print(f"admitted {CLAIM_ID}: {receipt.receipt_hash}")
    print(materialized.stdout.strip())


if __name__ == "__main__": main()
