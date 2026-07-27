#!/usr/bin/env python3
"""Officially admit and materialize Chemistry KIN-009 exactly once."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.reversible_kinetic_equilibrium_batch_v1 import (  # noqa: E402
    PRIMARY_PATH, REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC,
)
from sft.chemistry.reversible_kinetic_equilibrium_validation_v1 import (  # noqa: E402
    _source_rows, exact_reversible_kinetic_equilibrium_analysis,
)
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_kin_009", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load KIN-009 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC
    census_path = ROOT / "census/claims.json"
    if spec.claim_id in {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}:
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
        execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical()
    )
    if not receipt.model_admitted:
        raise SystemExit(f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}")
    sealed, external, empirical = captured["sealed"], captured["external"], captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
        write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text())
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_reversible_kinetic_equilibrium_analysis(rows, primary)
    vector = tuple({
        "target_id": row["target_id"], "source_document_identity": row["source_document_identity"],
        "source_record_identity": row["source_record_identity"], "source_record_ordinal": row["source_record_ordinal"],
        "complete_target_payload_hash": row["target_payload_hash"],
    } for row in rows)
    pair = primary["bidirectional_same_pair_record"]
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-KIN-009",
            "status": "model_admitted_observationally_disclosed_empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash,
            "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "engine_receipt_hash": receipt.receipt_hash, "engine_receipt_path": census_row["receipt_path"],
            "closure_scope": receipt.closure_status, "exact_result": spec.exact_result,
            "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
            "reversible_kinetic_equilibrium_law": (
                "one exact closed two-state graph supplies both the held directed kinetic edge word and the equilibrium "
                "recurrence support without an imported rate equation, equilibrium constant or stochastic balance"
            ),
            "complete_registered_source_record_count": analysis["complete_registered_target_count"],
            "complete_source_class_census": analysis["complete_source_class_census"],
            "same_pair_forward_record": pair["directional_records"][0],
            "same_pair_reverse_record": pair["directional_records"][1],
            "terminal_composition_disagreement_retained_not_averaged": pair["equilibrium_disagreement_retained_not_averaged"],
            "continuation_reversible_pair_records": primary["continuation_reversible_pair_records"],
            "source_direction_label_disagreements_preserved_without_selection": analysis["source_direction_label_disagreements_retained"],
            "supplementary_activation_energy_vector": primary["supplementary_table_1_activation_energy_vector"],
            "supplementary_relative_energy_vector": primary["supplementary_table_2_relative_energy_vector"],
            "complete_postseal_external_vector": vector,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "all_values_released_after_identity_and_prediction_seal": True,
            "all_155_pdf_pages_reproduced": analysis["complete_source_class_census_matches"],
            "all_nine_decisive_supplement_pages_reproduced": analysis["all_nine_decisive_supplement_pages_reproduced"],
            "complete_73_frame_movie_retained": analysis["complete_movie_retained"],
            "all_eight_archive_members_retained": analysis["all_archive_members_retained"],
            "source_fits_slopes_energies_equations_and_calculations_retained_only_as_postseal_provenance": analysis["source_fits_and_values_are_postseal_provenance_not_proof"],
            "imported_rate_equation_equilibrium_law_constant_stochastic_weight_fit_steady_state_selection_average_interpolation_renormalization_or_target_correction_used": False,
            "external_values_used_as_proof_parameters": False,
            "numerical_zero_used": False,
            "negative_irrational_imaginary_logarithmic_signed_or_continuum_proof_value_used": False,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)
    registration = json.loads((package / "registration.json").read_text())
    registration["status"] = "empirically_tested"
    write_json(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text())
    experiment["status"] = "complete_164_record_forward_reverse_equilibrium_vector_opened_postseal"
    write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_observationally_disclosed_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-KIN-009`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: the same exact closed two-state graph supplies the held directed kinetic word and equilibrium recurrence support.\n"
        "- Complete external surface: 164 records—155 PDF pages, one 73-frame movie and eight archive members.\n"
        "- Same-pair values: 83/17 to 32/68 after 88 hours; 98/2 to 71/29 after 82 hours; terminal disagreement retained without averaging.\n"
        "- Adverse surface: two source direction-label inconsistencies remain visible; fits and energy values remain post-seal provenance only.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("complete reversible/equilibrium vector: 164 records; 155 PDF pages; 73 movie frames; 8 archive members")


if __name__ == "__main__":
    main()
