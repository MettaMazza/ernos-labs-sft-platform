#!/usr/bin/env python3
"""Officially admit and materialize Chemistry PROP-009."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.vibrational_frequency_batch_v1 import VIBRATIONAL_FREQUENCY_SPEC  # noqa: E402
from sft.chemistry.vibrational_frequency_validation_v1 import _source_rows  # noqa: E402
from sft.claim_evidence import EmptyOne, PositiveRatio  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / VIBRATIONAL_FREQUENCY_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_prop_009", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load PROP-009 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def exact_value(value) -> object:
    if isinstance(value, PositiveRatio):
        return {"numerator": value.numerator.value, "denominator": value.denominator.value}
    if isinstance(value, EmptyOne):
        return {"structural_absence": "EmptyOne"}
    raise TypeError("unexpected PROP-009 exact value")


def main() -> None:
    spec = VIBRATIONAL_FREQUENCY_SPEC
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

    receipt = EngineRepository(ROOT).execute_official(
        execution.program,
        CaptureIndependent(),
        execution.source_files,
        CaptureEmpirical(),
    )
    if not receipt.model_admitted:
        raise SystemExit(f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}")
    sealed, external, empirical = captured["sealed"], captured["external"], captured["empirical"]

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({
            "claim_id": spec.claim_id,
            "execution_file": f"claims/{spec.claim_id}/execution.py",
        })
        write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text(encoding="utf-8"))
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    source_rows = _source_rows(ROOT)
    quantitative = tuple({
        "target_id": row["target_id"],
        "formula": row["formula"],
        "name": row["name"],
        "mode_count": row["mode_count"],
        "symmetry_label": row["symmetry_label"],
        "molecule_count": row["molecule_count"],
        "vibration_count": row["vibration_count"],
        "measurement_present": row["measurement_present"],
        "frequency_inscription_cm_inverse": row["frequency_inscription_cm_inverse"],
        "exact_recurrence_ratio_or_absence": exact_value(row["vault_value"]),
        "measurement_unit": row["measurement_unit"],
        "source_id": row["source_id"],
        "source_locator": row["source_locator"],
    } for row in source_rows)
    measured_values = tuple(row["vault_value"].fraction for row in source_rows if row["measurement_present"])
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {
            "claim_id": spec.claim_id,
            "decisions": asdict(sealed)["decisions"],
            "closure": asdict(sealed.closure),
        },
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id,
            "chemistry_obligation": "SFT-CHEM-OBL-PROP-009",
            "status": "model_admitted_observationally_derived_empirically_tested_and_independently_replicated",
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
            "unique_survivor_count": sum(item.survives for item in sealed.decisions),
            "exact_frequency_law": "vibrational frequency = positive finite recurrence count / positive observation-interval count",
            "exact_successor_law": "equal repetition scales recurrence and interval counts together and preserves their exact ratio",
            "unit_translation_law": "reciprocal-centimeter is a held label attached only after the recurrence ratio exists",
            "source_advertised_molecule_count": 164,
            "source_advertised_vibration_count": 2452,
            "complete_displayed_molecule_count": 145,
            "complete_displayed_rows": len(source_rows),
            "source_advertised_but_undisplayed_molecule_count": 19,
            "source_advertised_but_undisplayed_vibration_count": 443,
            "measured_frequency_rows": sum(row["measurement_present"] for row in source_rows),
            "structural_measurement_absence_rows": sum(not row["measurement_present"] for row in source_rows),
            "minimum_measured_frequency_cm_inverse": {"numerator": min(measured_values).numerator, "denominator": min(measured_values).denominator},
            "maximum_measured_frequency_cm_inverse": {"numerator": max(measured_values).numerator, "denominator": max(measured_values).denominator},
            "quantitative_vector": quantitative,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "all_postseal_measurements_exact_and_positive_or_structural_EmptyOne": True,
            "theoretical_frequency_ratio_or_fitted_scale_used": False,
            "fitted_or_free_parameter_used": False,
            "measured_value_in_derivation_or_prediction": False,
            "all_measurements_released_after_relation_seal": True,
            "numerical_zero_used": False,
            "negative_irrational_imaginary_or_continuum_proof_value_used": False,
            "observational_development_disclosed": True,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)
    registration_path = package / "registration.json"
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    registration["status"] = "empirically_tested"
    write_json(registration_path, registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment["status"] = "measured"
    write_json(experiment_path, experiment)
    status = (
        f"# {spec.claim_id}\n\n"
        "Status: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-PROP-009`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: `positive finite recurrence count / positive observation-interval count`.\n"
        "- Complete displayed source: `2,009/2,009` modes across `145/145` displayed molecules.\n"
        "- External vector: `1,984` exact positive frequencies and `25` structural EmptyOne measurement absences.\n"
        "- Preserved source boundary: advertised `164/2,452`, displayed `145/2,009`, undisplayed difference `19/443`.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n"
    )
    (package / "STATUS.md").write_text(status, encoding="utf-8")
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(item.survives for item in sealed.decisions)}")
    print(f"displayed rows: {len(source_rows)}; measured: {sum(row['measurement_present'] for row in source_rows)}; absent: {sum(not row['measurement_present'] for row in source_rows)}")


if __name__ == "__main__":
    main()
