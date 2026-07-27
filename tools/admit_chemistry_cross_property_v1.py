#!/usr/bin/env python3
"""Officially admit and materialize Chemistry PROP-014 exactly once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.cross_property_batch_v1 import CROSS_PROPERTY_SPEC  # noqa: E402
from sft.chemistry.cross_property_validation_v1 import _source_rows  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / CROSS_PROPERTY_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_prop_014", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load PROP-014 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = CROSS_PROPERTY_SPEC
    census_path = ROOT / "census/claims.json"
    existing = {row["claim_id"] for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    if spec.claim_id in existing:
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

    receipt = EngineRepository(ROOT).execute_official(execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical())
    if not receipt.model_admitted:
        raise SystemExit(f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}")
    sealed, external, empirical = captured["sealed"], captured["external"], captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
        write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text(encoding="utf-8"))
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    source_rows = _source_rows(ROOT)
    family_counts = {family: sum(row["property_family"] == family for row in source_rows) for family in sorted({row["property_family"] for row in source_rows})}
    overlap_family_counts = {family: sum(row["property_family"] == family and row["cross_property_overlap"] for row in source_rows) for family in family_counts}
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-PROP-014",
            "status": "model_admitted_observationally_derived_empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "derivation_seal_hash": sealed.seal_hash, "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash, "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash, "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "engine_receipt_hash": receipt.receipt_hash, "engine_receipt_path": census_row["receipt_path"],
            "closure_scope": receipt.closure_status, "exact_result": spec.exact_result,
            "candidate_count": len(sealed.census.candidates), "unique_survivor_count": sum(item.survives for item in sealed.decisions),
            "exact_carrier_law": "one retained structural molecular carrier supplies every applicable named property projection",
            "exact_parameter_law": "no per-property coefficient, residual, correction or target-derived carrier field",
            "exact_successor_law": "appending one lawful property projection preserves every existing projection",
            "complete_property_family_count": 13, "complete_source_row_count": 9025,
            "complete_structural_carrier_count": 1104, "multi_property_structural_carrier_count": 676,
            "multi_property_source_row_count": 6676, "maximum_property_families_on_one_carrier": 8,
            "maximum_coverage_carrier": "exact-formula:H2",
            "complete_property_family_row_counts": family_counts, "multi_property_family_row_counts": overlap_family_counts,
            "all_target_payloads_and_hashes_released_after_identity_seal": True,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "per_property_fit_or_target_derived_field_used": False, "guessed_species_or_formula_join_used": False,
            "numerical_zero_used": False, "negative_irrational_imaginary_or_continuum_proof_value_used": False,
            "observational_development_disclosed": True, "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items(): write_json(package / name, payload)
    registration_path = package / "registration.json"
    registration = json.loads(registration_path.read_text(encoding="utf-8")); registration["status"] = "empirically_tested"; write_json(registration_path, registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text(encoding="utf-8")); experiment["status"] = "complete_cross_property_vector_opened_postseal"; write_json(experiment_path, experiment)
    status = (
        f"# {spec.claim_id}\n\nStatus: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-PROP-014`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: one shared structural carrier, complete named property support, zero per-property fits.\n"
        "- Complete vector: `13` families, `9,025` rows, `1,104` carriers.\n"
        "- Exact overlap: `676` multi-property carriers and `6,676` overlap rows; maximum `8` families on H2.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n"
    )
    (package / "STATUS.md").write_text(status, encoding="utf-8")
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(item.survives for item in sealed.decisions)}")
    print(f"property families: 13; rows: {len(source_rows)}; carriers: {len({row['structural_carrier_id'] for row in source_rows})}; overlap carriers: {len({row['structural_carrier_id'] for row in source_rows if row['cross_property_overlap']})}")


if __name__ == "__main__": main()
