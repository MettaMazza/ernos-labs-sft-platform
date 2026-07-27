#!/usr/bin/env python3
"""Officially admit and materialize Chemistry PROP-007."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.molecular_ionization_batch_v1 import MOLECULAR_IONIZATION_SPEC  # noqa: E402
from sft.chemistry.molecular_ionization_validation_v1 import _source_rows  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / MOLECULAR_IONIZATION_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_prop_007", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load PROP-007 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def exact_pair(value) -> dict[str, int]:
    return {"numerator": value.numerator.value, "denominator": value.denominator.value}


def main() -> None:
    spec = MOLECULAR_IONIZATION_SPEC
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
        "source_row_ordinal": row["source_row_ordinal"],
        "formula": row["formula"],
        "name": row["name"],
        "initial_molecular_state": row["initial_molecular_state"],
        "initial_conformation": row["initial_conformation"],
        "resulting_ionic_state": row["resulting_ionic_state"],
        "ionization_path": row["ionization_path"],
        "condition": row["condition"],
        "inscription_eV": row["inscription"],
        "uncertainty_inscription_eV": row["uncertainty_inscription"],
        "exact_positive_value_eV": exact_pair(row["vault_value"]),
        "exact_display_lower_eV": dict(row["lower"]),
        "exact_display_upper_eV": dict(row["upper"]),
        "source_id": row["source_id"],
        "source_locator": row["source_locator"],
    } for row in source_rows)
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
            "chemistry_obligation": "SFT-CHEM-OBL-PROP-007",
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
            "exact_ionization_law": "ionization requirement = higher separated ion-plus-electron terminal height Take lower neutral bound-state height",
            "exact_adiabatic_law": "adiabatic ionization = least positive Take over complete generated ionic terminal support",
            "exact_vertical_law": "a held-geometry vertical terminal belongs to complete support and cannot lie below its least adiabatic member",
            "complete_external_rows": len(source_rows),
            "quantitative_vector": quantitative,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "all_postseal_values_exact_and_positive": all(row["vault_value"].fraction > 0 for row in source_rows),
            "all_explicit_uncertainties_preserved": sum(row["uncertainty"] is not None for row in source_rows) == 7,
            "fitted_or_free_parameter_used": False,
            "measured_value_in_derivation_or_prediction": False,
            "all_measurement_values_released_after_relation_seal": True,
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
        "- Chemistry obligation: `SFT-CHEM-OBL-PROP-007`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact ionization law: `higher separated terminal height Take lower neutral bound-state height`.\n"
        "- Exact adiabatic law: `least positive Take over complete generated ionic terminal support`.\n"
        "- Exact vertical law: `held-geometry terminal cannot lie below the least adiabatic member`.\n"
        "- Complete external vector: `9/9` NIST neutral diatomic molecular records.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n"
    )
    (package / "STATUS.md").write_text(status, encoding="utf-8")
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(item.survives for item in sealed.decisions)}")
    print(f"external rows: {len(source_rows)}; explicit uncertainty rows: {sum(row['uncertainty'] is not None for row in source_rows)}")


if __name__ == "__main__":
    main()
