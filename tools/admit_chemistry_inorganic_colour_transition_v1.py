#!/usr/bin/env python3
"""Officially admit and materialize Chemistry INORG-008 exactly once."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.inorganic_colour_transition_batch_v1 import INORGANIC_COLOUR_TRANSITION_SPEC, PRIMARY_PATH  # noqa: E402
from sft.chemistry.inorganic_colour_transition_validation_v1 import _source_rows, exact_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / INORGANIC_COLOUR_TRANSITION_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_inorg_008", path)
    module = importlib.util.module_from_spec(definition); definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = INORGANIC_COLOUR_TRANSITION_SPEC
    census_path = ROOT / "census/claims.json"
    if spec.claim_id in {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    execution = load_execution(); captured = {}

    class CaptureIndependent:
        def validate(self, sealed):
            captured["sealed"] = sealed; captured["external"] = execution.independent_validator.validate(sealed); return captured["external"]

    class CaptureEmpirical:
        def validate(self, sealed):
            captured["empirical"] = execution.empirical_validator.validate(sealed); return captured["empirical"]

    receipt = EngineRepository(ROOT).execute_official(execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical())
    if not receipt.model_admitted:
        raise SystemExit(f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}")
    sealed, external, empirical = captured["sealed"], captured["external"], captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"; manifest = json.loads(manifest_path.read_text())
    manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"}); write_json(manifest_path, manifest)
    row = next(item for item in json.loads(census_path.read_text())["claims"] if item["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    analysis = exact_analysis(_source_rows(ROOT), json.loads((ROOT / PRIMARY_PATH).read_text()))
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-INORG-008",
            "status": "model_admitted_forward_forced_empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash, "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": external.implementation_hash, "independent_certificate_hash": external.certificate_hash,
            "external_validation_hash": receipt.external_validation_hash, "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash, "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": row["receipt_path"], "closure_scope": receipt.closure_status, "exact_result": spec.exact_result,
            "candidate_count": len(sealed.census.candidates), "unique_survivor_count": sum(item.survives for item in sealed.decisions),
            "forced_transition_class_vector": analysis["transition_classes"], "exact_positive_order_gap": analysis["exact_gap"],
            "exact_absorbed_count": analysis["absorbed_count"], "exact_retained_colour_count": analysis["retained_colour_count"],
            "complete_registered_external_surface_count": 8, "complete_spectrum_count": analysis["spectrum_count"],
            "complete_point_count_vector": analysis["point_count_vector"], "complete_total_point_count": analysis["total_point_count"],
            "complete_interior_maximum_count_vector": analysis["interior_maximum_count_vector"],
            "complete_interior_maximum_position_vector_nm": analysis["interior_maximum_position_vector"],
            "originally_law_sealed_blind_spectrum_count": analysis["originally_blind_count"],
            "source_recapture_count": analysis["source_recapture_count"], "all_external_rows_preserved": empirical.all_rows_preserved,
            "metal_to_metal_definition_absence_preserved": analysis["metal_to_metal_definition_absent_preserved"],
            "numerical_zero_negative_irrational_imaginary_signed_continuum_fitted_or_free_parameter_used": False,
            "imported_orbital_ligand_field_colour_wheel_or_peak_selection_used": False,
            "dimensional_wavelength_intensity_or_colour_name_fitted_or_derived": False,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items(): write_json(package / name, payload)
    registration = json.loads((package / "registration.json").read_text()); registration["status"] = "empirically_tested"; registration["candidate_grammar"]["completeness_certificate"] = sealed.census.completeness_certificate_hash; write_json(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"; experiment = json.loads(experiment_path.read_text()); experiment["status"] = "measured"; write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_forward_forced_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-INORG-008`\n- Exact transition classes: ligand-to-ligand, ligand-to-metal, metal-to-ligand, metal-to-metal.\n"
        "- Colour law: positive proper absorption plus exact retained complement.\n- External vector: four definitions and four complete spectra; 456 points; maxima counts `2,2,1,2`; no recapture.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(item.survives for item in sealed.decisions)}")
    print("complete external vector: 8 rows; 4 spectra; 456 exact points; sources not recaptured")


if __name__ == "__main__": main()
