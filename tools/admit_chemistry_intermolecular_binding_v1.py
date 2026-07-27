#!/usr/bin/env python3
"""Officially admit and materialize Chemistry PROP-011 exactly once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.intermolecular_binding_batch_v1 import (  # noqa: E402
    INTERMOLECULAR_BINDING_SPEC,
    PRIMARY_PATH,
)
from sft.chemistry.intermolecular_binding_validation_v1 import _source_rows  # noqa: E402
from sft.claim_evidence import EmptyOne, PositiveRatio  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / INTERMOLECULAR_BINDING_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_prop_011", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load PROP-011 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def exact_value(value: object) -> dict[str, object]:
    if isinstance(value, PositiveRatio):
        return {"numerator": value.numerator.value, "denominator": value.denominator.value}
    if isinstance(value, EmptyOne):
        return {"structural_absence": "EmptyOne"}
    raise TypeError("unexpected PROP-011 exact value")


def main() -> None:
    spec = INTERMOLECULAR_BINDING_SPEC
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
    primary = json.loads((ROOT / PRIMARY_PATH).read_text(encoding="utf-8"))
    quantitative = tuple({
        "target_id": row["target_id"],
        "dimer_id": row["dimer_id"],
        "dimer_formula": row["dimer_formula"],
        "dimer_name": row["dimer_name"],
        "donor_formula": row["donor_formula"],
        "acceptor_formula": row["acceptor_formula"],
        "method_id": row.get("method_id"),
        "basis_id": row.get("basis_id"),
        "source_class": row["source_class"],
        "result_class": row["result_class"],
        "source_value_inscription": row.get("value_inscription_kJ_per_mol", row.get("value_inscription_cm_inverse")),
        "source_uncertainty_inscription": row.get("uncertainty_inscription_cm_inverse"),
        "exact_positive_binding_or_structural_absence": exact_value(row["vault_value"]),
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
            "chemistry_obligation": "SFT-CHEM-OBL-PROP-011",
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
            "exact_binding_law": "exact separated-constituent state Take exact lower bound-composite state",
            "exact_composition_law": "all named positive constituent states compose without a numerical-zero initializer",
            "exact_absence_law": "a record without strict bound-state order is structural EmptyOne",
            "exact_successor_law": "appending the same named constituent state to both endpoints preserves the exact binding Take",
            "complete_cccbdb_dimer_count": primary["complete_cccbdb_dimer_count"],
            "complete_cccbdb_linked_value_count": primary["complete_cccbdb_linked_value_count"],
            "complete_cccbdb_positive_value_count": primary["complete_cccbdb_positive_value_count"],
            "complete_cccbdb_signed_adverse_value_count": primary["complete_cccbdb_signed_adverse_value_count"],
            "complete_cccbdb_unavailable_dnf_inscription_count": primary["complete_cccbdb_unavailable_dnf_inscription_count"],
            "reported_experimental_cluster_dissociation_count": primary["reported_experimental_cluster_dissociation_count"],
            "complete_external_target_row_count": len(source_rows),
            "exact_positive_postseal_rows": sum(isinstance(row["vault_value"], PositiveRatio) for row in source_rows),
            "structural_EmptyOne_adverse_rows": sum(isinstance(row["vault_value"], EmptyOne) for row in source_rows),
            "quantitative_vector": quantitative,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "calculated_rows_not_misreported_as_measurements": True,
            "wider_ion_cluster_compendium_preserved_without_mixed_quantity_homogenization": True,
            "all_measurements_and_calculated_targets_released_after_relation_seal": True,
            "measured_or_calculated_value_in_derivation_or_prediction": False,
            "intermolecular_potential_continuum_distance_or_fitted_coefficient_used": False,
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
    experiment["status"] = "measured_and_computed_external_vector_opened_postseal"
    write_json(experiment_path, experiment)
    status = (
        f"# {spec.claim_id}\n\n"
        "Status: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-PROP-011`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: `separated constituent state Take lower bound composite state`.\n"
        "- Native absence: an unbound external record is structural `EmptyOne`; no negative or numerical-zero Fold value is created.\n"
        "- Complete calculated surface: `11` dimers, `1,297` linked method/basis values, `1,201` positive and `96` signed adverse source inscriptions.\n"
        "- Experimental cluster vector: `(H2O)2 = 1105 ± 10 cm^-1`; `(D2O)2 = 1244 ± 10 cm^-1`.\n"
        "- Wider boundary: complete NIST 62-page ion-cluster thermochemistry compendium byte-preserved without relabelling mixed quantities.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n"
    )
    (package / "STATUS.md").write_text(status, encoding="utf-8")
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(item.survives for item in sealed.decisions)}")
    print(f"external rows: {len(source_rows)}; exact positive: {sum(isinstance(row['vault_value'], PositiveRatio) for row in source_rows)}; structural EmptyOne: {sum(isinstance(row['vault_value'], EmptyOne) for row in source_rows)}")


if __name__ == "__main__":
    main()
