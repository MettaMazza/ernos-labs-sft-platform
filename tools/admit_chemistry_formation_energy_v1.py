#!/usr/bin/env python3
"""Officially admit and materialize Chemistry PROP-013 exactly once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.formation_energy_batch_v1 import FORMATION_ENERGY_SPEC, PRIMARY_PATH  # noqa: E402
from sft.chemistry.formation_energy_validation_v1 import _source_rows  # noqa: E402
from sft.claim_evidence import EmptyOne, PositiveRatio  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / FORMATION_ENERGY_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_prop_013", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load PROP-013 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def exact_value(value: object) -> dict[str, object]:
    if isinstance(value, PositiveRatio):
        return {"numerator": value.numerator.value, "denominator": value.denominator.value}
    if isinstance(value, EmptyOne):
        return {"structural_absence": "EmptyOne"}
    raise TypeError("unexpected PROP-013 exact value")


def main() -> None:
    spec = FORMATION_ENERGY_SPEC
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
    primary = json.loads((ROOT / PRIMARY_PATH).read_text(encoding="utf-8"))
    quantitative = tuple({
        "target_id": row["target_id"], "name": row["name"], "species": row["species"],
        "temperature_reference_label": row["temperature_reference_label"],
        "source_value_inscription": row["source_value_inscription"],
        "source_orientation": row["source_orientation"],
        "exact_positive_magnitude_or_structural_absence": exact_value(row["vault_value"]),
        "result_class": row["result_class"], "source_id": row["source_id"], "source_locator": row["source_locator"],
    } for row in source_rows)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-PROP-013",
            "status": "model_admitted_observationally_derived_empirically_tested_and_independently_replicated",
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
            "unique_survivor_count": sum(item.survives for item in sealed.decisions),
            "exact_reference_law": "nonempty exact composition of all named constituent reference states",
            "exact_orientation_law": "product/reference order is a held label, never a signed proof number",
            "exact_magnitude_law": "unequal endpoints force one exact positive state separation",
            "exact_equality_law": "equal endpoints are structural EmptyOne",
            "exact_successor_law": "shared state extension preserves the relation and positive repetition scales it",
            "complete_listed_species_count": primary["complete_listed_species_count"],
            "complete_unique_formula_composition_query_count": primary["complete_unique_formula_composition_query_count"],
            "complete_returned_charge_state_choice_count": primary["complete_returned_charge_state_choice_count"],
            "complete_listed_composition_without_returned_choice_count": primary["complete_listed_composition_without_returned_choice_count"],
            "complete_displayed_molecular_row_count": primary["complete_displayed_molecular_row_count"],
            "complete_external_target_count": len(source_rows),
            "printed_value_count": primary["source_value_present_count"], "blank_cell_count": primary["source_value_absent_count"],
            "product_below_reference_count": primary["product_below_reference_count"],
            "product_above_reference_count": primary["product_above_reference_count"],
            "printed_equality_structural_EmptyOne_count": primary["product_equal_reference_structural_EmptyOne_count"],
            "exact_positive_postseal_count": sum(isinstance(row["vault_value"], PositiveRatio) for row in source_rows),
            "structural_EmptyOne_postseal_count": sum(isinstance(row["vault_value"], EmptyOne) for row in source_rows),
            "quantitative_vector": quantitative, "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "all_values_presence_flags_and_orientations_released_after_relation_seal": True,
            "measured_value_in_derivation_or_prediction": False,
            "imported_reference_fitted_atomic_value_or_species_coefficient_used": False,
            "numerical_zero_used": False, "negative_irrational_imaginary_or_continuum_proof_value_used": False,
            "observational_development_disclosed": True, "falsification_condition": empirical.falsification_condition,
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
    experiment["status"] = "complete_formation_energy_vector_opened_postseal"
    write_json(experiment_path, experiment)
    status = (
        f"# {spec.claim_id}\n\nStatus: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-PROP-013`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: held product/reference order with exact positive separation or structural equality.\n"
        "- Complete NIST vector: `2,098` cells; `1,485` printed values; `613` blanks.\n"
        "- Source orientation: `756` below, `707` above and `22` printed equalities.\n"
        "- Source boundary: `2,186` listed species, `1,193` composition queries, `1,832` returned choices and `83` unreturned compositions.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n"
    )
    (package / "STATUS.md").write_text(status, encoding="utf-8")
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(item.survives for item in sealed.decisions)}")
    print(f"external cells: {len(source_rows)}; exact positive: {sum(isinstance(row['vault_value'], PositiveRatio) for row in source_rows)}; structural EmptyOne: {sum(isinstance(row['vault_value'], EmptyOne) for row in source_rows)}")


if __name__ == "__main__":
    main()
