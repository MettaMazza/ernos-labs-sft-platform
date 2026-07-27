#!/usr/bin/env python3
"""Officially admit and materialize Chemistry PROP-008."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.molecular_electron_affinity_batch_v1 import MOLECULAR_ELECTRON_AFFINITY_SPEC  # noqa: E402
from sft.chemistry.molecular_electron_affinity_validation_v1 import _source_rows  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / MOLECULAR_ELECTRON_AFFINITY_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_prop_008", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load PROP-008 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = MOLECULAR_ELECTRON_AFFINITY_SPEC
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
        "source_catalog_ordinal": row["source_catalog_ordinal"],
        "molecular_catalog_ordinal": row["molecular_catalog_ordinal"],
        "measured_vector_ordinal": row["measured_vector_ordinal"],
        "formula": row["formula"],
        "name": row["name"],
        "initial_molecular_state": row["initial_molecular_state"],
        "resulting_anion_state": row["resulting_anion_state"],
        "source_orientation_glyph": row["source_orientation_glyph"],
        "fold_state_order_orientation": row["fold_state_order_orientation"],
        "magnitude_inscription_eV": row["magnitude_inscription"],
        "exact_positive_magnitude_eV": dict(row["exact_positive_magnitude"]),
        "uncertainty_inscription_eV": row["uncertainty_inscription"],
        "exact_positive_uncertainty_eV": row["exact_positive_uncertainty"],
        "exact_display_magnitude_lower_eV": dict(row["display_magnitude_lower"]),
        "exact_display_magnitude_upper_eV": dict(row["display_magnitude_upper"]),
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
            "chemistry_obligation": "SFT-CHEM-OBL-PROP-008",
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
            "exact_affinity_law": "state order is held; magnitude = higher retained state Take lower retained state",
            "bound_orientation": "anion-below-neutral-bound-attachment",
            "unbound_orientation": "anion-above-neutral-unbound-autodetachment",
            "coincident_boundary": "structural EmptyOne, never numerical zero",
            "complete_catalog_rows": 192,
            "atomic_rows_structurally_excluded": 30,
            "complete_molecular_pages": 162,
            "complete_external_rows": len(source_rows),
            "bound_orientation_rows": sum(row["fold_state_order_orientation"].startswith("anion-below") for row in source_rows),
            "unbound_orientation_rows": sum(row["fold_state_order_orientation"].startswith("anion-above") for row in source_rows),
            "explicit_uncertainty_rows": sum(row["uncertainty_inscription"] is not None for row in source_rows),
            "quantitative_vector": quantitative,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "all_postseal_magnitudes_exact_and_positive": all(row["vault_word"].cells[1].fraction > 0 for row in source_rows),
            "source_minus_glyphs_preserved_as_held_orientation": True,
            "fitted_or_free_parameter_used": False,
            "measured_value_or_orientation_in_derivation_or_prediction": False,
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
        "- Chemistry obligation: `SFT-CHEM-OBL-PROP-008`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: `held state order plus exact positive higher-state Take lower-state magnitude`.\n"
        "- Coincident boundary: `structural EmptyOne`, never numerical zero.\n"
        "- Complete source boundary: `192` catalog carriers, `30` atomic exclusions and `162` molecular pages.\n"
        "- Complete external vector: `96/96` NIST molecular records—`93` bound and `3` unbound—with `89/89` explicit uncertainties.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n"
    )
    (package / "STATUS.md").write_text(status, encoding="utf-8")
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(item.survives for item in sealed.decisions)}")
    print(f"external rows: {len(source_rows)}; bound: {sum(row['fold_state_order_orientation'].startswith('anion-below') for row in source_rows)}; unbound: {sum(row['fold_state_order_orientation'].startswith('anion-above') for row in source_rows)}")


if __name__ == "__main__":
    main()
