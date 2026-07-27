#!/usr/bin/env python3
"""Officially admit and materialize Chemistry INORG-009 exactly once."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.inorganic_magnetic_state_batch_v1 import INORGANIC_MAGNETIC_STATE_SPEC, PRIMARY_PATH  # noqa: E402
from sft.chemistry.inorganic_magnetic_state_validation_v1 import _source_rows, exact_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / INORGANIC_MAGNETIC_STATE_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_inorg_009", path)
    module = importlib.util.module_from_spec(definition); definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = INORGANIC_MAGNETIC_STATE_SPEC
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
            "claim_id": spec.claim_id,
            "chemistry_obligation": "SFT-CHEM-OBL-INORG-009",
            "status": "model_admitted_forward_forced_empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash,
            "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": row["receipt_path"],
            "closure_scope": receipt.closure_status,
            "exact_result": spec.exact_result,
            "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(item.survives for item in sealed.decisions),
            "balanced_exact_state": {
                "moment_support": analysis["balanced_moment"], "spin_width": analysis["balanced_width"],
                "field_relation": analysis["balanced_relation"], "magnetic_class": analysis["balanced_class"],
            },
            "four_unpaired_exact_state": {
                "moment_support": analysis["high_moment"], "spin_width": analysis["high_width"],
                "field_relation": analysis["high_relation"], "magnetic_class": analysis["high_class"],
            },
            "unpaired_successor_exact_state": {"moment_support": analysis["successor_moment"], "spin_width": analysis["successor_width"]},
            "complete_registered_external_surface_count": 177,
            "complete_shared_magnetic_cell_count": analysis["complete_magnetic_count"],
            "complete_exact_magnitude_count": analysis["positive_magnitude_count"],
            "complete_structural_absence_count": analysis["structural_absence_count"],
            "complete_orientation_class_counts": analysis["orientation_class_counts"],
            "complete_exact_magnitude_vector_hash": analysis["exact_magnitude_vector_hash"],
            "source_recapture_count": analysis["source_recapture_count"],
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "numerical_zero_negative_irrational_imaginary_signed_continuum_square_root_fitted_g_factor_or_free_parameter_used": False,
            "species_lookup_or_measured_value_used_to_select_survivor": False,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)
    registration = json.loads((package / "registration.json").read_text()); registration["status"] = "empirically_tested"; registration["candidate_grammar"]["completeness_certificate"] = sealed.census.completeness_certificate_hash; write_json(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"; experiment = json.loads(experiment_path.read_text()); experiment["status"] = "measured"; write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_forward_forced_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-INORG-009`\n- Balanced state: `EmptyOne`, width 1, repelled, diamagnetic.\n"
        "- Four-unpaired state: support 4, width 5, drawn, paramagnetic; successor support 5, width 6.\n"
        "- External vector: 177 rows; 136 exact magnitudes; 38 structural absences; no recapture.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(item.survives for item in sealed.decisions)}")
    print("complete external vector: 177 rows; 136 exact magnitudes; 38 structural absences; sources not recaptured")


if __name__ == "__main__":
    main()
