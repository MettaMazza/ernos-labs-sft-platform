#!/usr/bin/env python3
from dataclasses import asdict
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.resonance_equivalent_representation_batch_v1 import (  # noqa: E402
    PRIMARY_PATH,
    RESONANCE_EQUIVALENT_REPRESENTATION_SPEC,
)
from sft.chemistry.resonance_equivalent_representation_validation_v1 import (  # noqa: E402
    _source_rows,
    exact_analysis,
)
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_execution():
    path = ROOT / "claims" / RESONANCE_EQUIVALENT_REPRESENTATION_SPEC.claim_id / "execution.py"
    spec = importlib.util.spec_from_file_location("org002_execution", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = RESONANCE_EQUIVALENT_REPRESENTATION_SPEC
    claims_path = ROOT / "census/claims.json"
    if spec.claim_id in {row["claim_id"] for row in json.loads(claims_path.read_text())["claims"]}:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    execution = load_execution()
    captured = {}

    class IndependentCapture:
        def validate(self, sealed):
            captured["sealed"] = sealed
            captured["independent"] = execution.independent_validator.validate(sealed)
            return captured["independent"]

    class EmpiricalCapture:
        def validate(self, sealed):
            captured["empirical"] = execution.empirical_validator.validate(sealed)
            return captured["empirical"]

    receipt = EngineRepository(ROOT).execute_official(
        execution.program,
        IndependentCapture(),
        execution.source_files,
        EmpiricalCapture(),
    )
    if not receipt.model_admitted:
        raise SystemExit(
            f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}"
        )
    sealed = captured["sealed"]
    independent = captured["independent"]
    empirical = captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["claims"].append(
        {
            "claim_id": spec.claim_id,
            "execution_file": f"claims/{spec.claim_id}/execution.py",
        }
    )
    write_json(manifest_path, manifest)
    claim_row = next(
        row for row in json.loads(claims_path.read_text(encoding="utf-8"))["claims"]
        if row["claim_id"] == spec.claim_id
    )
    package = ROOT / "claims" / spec.claim_id
    analysis = exact_analysis(
        _source_rows(ROOT), json.loads((ROOT / PRIMARY_PATH).read_text(encoding="utf-8"))
    )
    certificate = {
        "claim_id": spec.claim_id,
        "chemistry_obligation": "SFT-CHEM-OBL-ORG-002",
        "status": "model_admitted_forward_forced_empirically_tested_and_independently_replicated",
        "source_manifest_hash": execution.program.registration.source_hash,
        "derivation_seal_hash": sealed.seal_hash,
        "independent_implementation_hash": independent.implementation_hash,
        "independent_certificate_hash": independent.certificate_hash,
        "external_validation_hash": receipt.external_validation_hash,
        "empirical_validation_hash": receipt.empirical_validation_hash,
        "measurement_receipt_hash": empirical.measurement_receipt_hash,
        "engine_receipt_hash": receipt.receipt_hash,
        "engine_receipt_path": claim_row["receipt_path"],
        "closure_scope": receipt.closure_status,
        "exact_result": spec.exact_result,
        "candidate_count": len(sealed.census.candidates),
        "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
        **analysis,
        "all_external_rows_preserved": empirical.all_rows_preserved,
        "numerical_zero_negative_irrational_imaginary_signed_continuum_fitted_free_or_imported_parameter_used": False,
        "external_definition_note_example_wavefunction_coefficient_or_charge_used_to_select_survivor": False,
        "external_signed_charge_inscription_used_as_native_arithmetic": False,
        "falsification_condition": empirical.falsification_condition,
    }
    artifacts = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {
            "claim_id": spec.claim_id,
            "decisions": asdict(sealed)["decisions"],
            "closure": asdict(sealed.closure),
        },
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": certificate,
    }
    for name, payload in artifacts.items():
        write_json(package / name, payload)
    registration_path = package / "registration.json"
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    registration["status"] = "empirically_tested"
    registration["candidate_grammar"]["completeness_certificate"] = sealed.census.completeness_certificate_hash
    write_json(registration_path, registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment["status"] = "measured"
    write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\n"
        "Status: `model_admitted_forward_forced_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-ORG-002`\n"
        "- Exact one-carrier, complete-atom, complete-adjacency representation equivalence with depth-independent complement successor.\n"
        "- External vector: four complete IUPAC representation, resonance-form, contributing-structure and delocalization records.\n"
        "- Preserved adverse evidence: one V1 incomplete search-scope result, corrected separately in V2 without source recapture.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(
        f"candidates: {len(sealed.census.candidates)}; "
        f"survivors: {sum(decision.survives for decision in sealed.decisions)}"
    )


if __name__ == "__main__":
    main()
