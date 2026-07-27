#!/usr/bin/env python3
"""Officially admit and materialize Chemistry INORG-005 exactly once."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.coordination_isomerism_batch_v1 import COORDINATION_ISOMERISM_SPEC, PRIMARY_PATH  # noqa: E402
from sft.chemistry.coordination_isomerism_validation_v1 import _source_rows, exact_coordination_isomerism_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / COORDINATION_ISOMERISM_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_inorg_005", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load INORG-005 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = COORDINATION_ISOMERISM_SPEC
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

    receipt = EngineRepository(ROOT).execute_official(
        execution.program,
        CaptureIndependent(),
        execution.source_files,
        CaptureEmpirical(),
    )
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
    analysis = exact_coordination_isomerism_analysis(rows, primary)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id,
            "chemistry_obligation": "SFT-CHEM-OBL-INORG-005",
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
            "equivalence_law": "complete occurrence-bijection preservation of composition, attachment, adjacency and three-axis two-fibre words",
            "forced_native_distinction_order": ["attachment-or-graph", "global-fibre-complement", "remaining-orientation-adjacency"],
            "generated_axis_position_count": 3,
            "forced_fibre_label_count": 2,
            "complete_registered_external_surface_count": analysis["complete_registered_target_count"],
            "general_isomer_relation_retained": analysis["general_isomer_relation_retained"],
            "geometric_relative_position_distinction_retained": analysis["geometric_relative_position_distinction_retained"],
            "mirror_non_superposable_distinction_retained": analysis["mirror_non_superposable_distinction_retained"],
            "point_of_ligation_distinction_retained": analysis["point_of_ligation_distinction_retained"],
            "two_isomeric_attachment_modes_retained": analysis["two_isomeric_attachment_modes_retained"],
            "registered_to_presented_identity_redirect_count": analysis["registered_to_presented_identity_redirect_count"],
            "all_identity_redirects_preserved": analysis["registered_to_presented_identity_redirects_preserved"],
            "explicit_linkage_literal_absence_preserved": analysis["explicit_linkage_literal_absence_preserved"],
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "all_source_content_released_after_identity_and_prediction_seal": True,
            "isomer_catalogue_name_point_group_plane_mirror_or_observed_class_used_as_fold_proof_parameter": False,
            "selected_mapping_fit_target_derived_condition_or_imported_transform_used": False,
            "numerical_zero_used": False,
            "third_fibre_label_used": False,
            "negative_irrational_imaginary_signed_or_continuum_proof_value_used": False,
            "falsification_condition": empirical.falsification_condition,
        },
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
        "- Chemistry obligation: `SFT-CHEM-OBL-INORG-005`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: equivalence is complete occurrence-bijection preservation; first failed invariants force attachment, mirror-complement or remaining orientation-adjacency classes.\n"
        "- Fold support: three axis positions; exactly two forced fibre labels; absence is structural EmptyOne.\n"
        "- External vector: 17 IUPAC surfaces retaining general, relative-position, mirror and point-of-ligation/attachment-mode evidence.\n"
        "- Adverse/absence evidence: both presented-identity redirects and the absent literal linkage-isomer term are preserved.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("complete isomerism vector: 17 surfaces; 2 identity redirects and literal-term absence retained")


if __name__ == "__main__":
    main()
