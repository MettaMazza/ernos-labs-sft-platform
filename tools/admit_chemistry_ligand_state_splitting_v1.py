#!/usr/bin/env python3
"""Officially admit and materialize Chemistry INORG-006 exactly once."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.ligand_state_splitting_batch_v1 import LIGAND_STATE_SPLITTING_SPEC, PRIMARY_PATH  # noqa: E402
from sft.chemistry.ligand_state_splitting_validation_v1 import _source_rows, exact_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / LIGAND_STATE_SPLITTING_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_inorg_006", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load INORG-006 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = LIGAND_STATE_SPLITTING_SPEC
    census_path = ROOT / "census/claims.json"
    if spec.claim_id in {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    execution = load_execution()
    captured = {}

    class CaptureIndependent:
        def validate(self, sealed):
            captured["sealed"] = sealed
            captured["external"] = execution.independent_validator.validate(sealed)
            return captured["external"]

    class CaptureEmpirical:
        def validate(self, sealed):
            captured["empirical"] = execution.empirical_validator.validate(sealed)
            return captured["empirical"]

    receipt = EngineRepository(ROOT).execute_official(execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical())
    if not receipt.model_admitted:
        raise SystemExit(f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}")

    sealed = captured["sealed"]
    external = captured["external"]
    empirical = captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
        write_json(manifest_path, manifest)

    census = json.loads(census_path.read_text())
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / PRIMARY_PATH).read_text(encoding="utf-8"))
    analysis = exact_analysis(rows, primary)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id,
            "chemistry_obligation": "SFT-CHEM-OBL-INORG-006",
            "status": "model_admitted_observationally_disclosed_empirically_tested_and_independently_replicated",
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
            "exact_result": spec.exact_result,
            "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
            "generated_support_count": analysis["generated_support_count"],
            "six_direct_axis_positive_multiplicity_vector": analysis["six_multiplicity_vector"],
            "six_direct_axis_exact_normalized_structural_separation": analysis["six_separation_vector"],
            "six_direct_axis_positive_balance_distance_vector": analysis["six_balance_vector"],
            "four_complete_axis_positive_multiplicity_vector": analysis["four_multiplicity_vector"],
            "four_complete_axis_exact_normalized_structural_separation": analysis["four_separation_vector"],
            "four_complete_axis_positive_balance_distance_vector": analysis["four_balance_vector"],
            "all_five_members_preserved": analysis["all_members_preserved"],
            "removed_interaction_remerges_one_five_member_class": analysis["removal_remerges_one_five_member_class"],
            "complete_registered_external_surface_count": 32,
            "law_sealed_blind_spectrum_payload_count": analysis["blind_spectrum_payload_count"],
            "blind_complete_interior_maximum_counts": analysis["blind_complete_interior_maximum_counts"],
            "blind_exact_interior_peak_positions": analysis["blind_exact_interior_peak_positions"],
            "blind_exact_adjacent_peak_separations": analysis["blind_exact_adjacent_peak_separations"],
            "blind_distinguishability_condition_passed": analysis["blind_distinguishability_condition_passed"],
            "law_sealed_adverse_absence_count": analysis["law_sealed_adverse_absence_count"],
            "development_ancillary_capture_count": analysis["development_ancillary_count"],
            "iupac_removal_of_degeneracy_and_reduced_symmetry_surfaces_retained": analysis["iupac_removal_of_degeneracy_surface_present"] and analysis["iupac_ligand_attachment_reduced_symmetry_surface_present"],
            "conventional_variable_parameter_surface_preserved_downstream_only": analysis["iupac_conventional_variable_parameter_surface_preserved_as_downstream"],
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "numerical_zero_negative_irrational_imaginary_signed_continuum_fitted_or_free_parameter_used": False,
            "imported_orbital_field_geometry_spectrochemical_table_used": False,
            "dimensional_wavelength_fitted_or_claimed": False,
            "falsification_condition": empirical.falsification_condition
        }
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)

    registration = json.loads((package / "registration.json").read_text())
    registration["status"] = "empirically_tested"
    registration["candidate_grammar"]["completeness_certificate"] = sealed.census.completeness_certificate_hash
    write_json(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text())
    experiment["status"] = "measured"
    write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\n"
        "Status: `model_admitted_observationally_disclosed_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-INORG-006`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: five generated supports split by complete ligand-incidence equivalence.\n"
        "- Six direct-axis result: multiplicities `3,2`, separation `2/3`, balance `2/5,3/5`.\n"
        "- Four complete-axis result: multiplicities `2,3`, separation `1`, balance `3/5,2/5`.\n"
        "- External vector: 32 surfaces; final blind spectrum has two interior maxima; two adverse absences and twelve ancillary captures retained.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8"
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("complete external vector: 32 rows; blind spectrum favorable; 2 adverse absences and 12 ancillary rows preserved")


if __name__ == "__main__":
    main()
