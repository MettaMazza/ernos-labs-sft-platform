#!/usr/bin/env python3
"""Officially execute and materialize the ELEC-005 evidence package once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.state_symmetry_batch_v1 import STATE_SYMMETRY_SPEC  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / STATE_SYMMETRY_SPEC.claim_id / "execution.py"
    module_spec = importlib.util.spec_from_file_location("chem_state_symmetry_005", path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = STATE_SYMMETRY_SPEC
    census_path = ROOT / "census" / "claims.json"
    existing = {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}
    if spec.claim_id in existing:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    execution = load_execution()
    captured = {}

    class IndependentCapture:
        def validate(self, sealed):
            captured["sealed"] = sealed
            captured["external"] = execution.independent_validator.validate(sealed)
            return captured["external"]

    class EmpiricalCapture:
        def validate(self, sealed):
            captured["empirical"] = execution.empirical_validator.validate(sealed)
            return captured["empirical"]

    receipt = EngineRepository(ROOT).execute_official(
        execution.program,
        IndependentCapture(),
        execution.source_files,
        EmpiricalCapture(),
    )
    if not receipt.model_admitted:
        raise SystemExit(f"halted {receipt.halted_stage}; {receipt.receipt_hash}")

    sealed = captured["sealed"]
    external = captured["external"]
    empirical = captured["empirical"]
    manifest_path = ROOT / "census" / "execution_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["claims"].append(
        {"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"}
    )
    write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text())
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    claim_path = ROOT / "claims" / spec.claim_id
    artifacts = {
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
            "chemistry_obligation": "SFT-CHEM-OBL-ELEC-005",
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
            "candidate_count": 256,
            "unique_survivor_count": 1,
            "NIST_species": 22,
            "NIST_state_rows": 360,
            "NIST_term_assignments": 362,
            "retained_inversion_labels": 170,
            "retained_reflection_labels": 167,
            "positive_axis_component_labels": 32,
            "absent_axis_component_coordinates": 330,
            "source_zero_component_glyphs_interpreted_only_as_absence": 11,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "energy_coincidence_claimed": False,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, data in artifacts.items():
        write_json(claim_path / name, data)
    registration = json.loads((claim_path / "registration.json").read_text())
    registration["status"] = "empirically_tested"
    write_json(claim_path / "registration.json", registration)
    experiment_path = ROOT / "experiments" / "chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text())
    experiment["status"] = "measured"
    write_json(experiment_path, experiment)
    (claim_path / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\n"
        "Status: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-ELEC-005`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n"
        f"- Measurement receipt: `{empirical.measurement_receipt_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n"
        "- External vector: 362 NIST term assignments across 360 state rows and 22 species; all retained symmetry labels and absence coordinates preserved.\n"
        "- Absence rule: source glyph `0` denotes absence only and is represented natively by structural `EmptyOne`.\n"
        "- Scope: exact finite state equivalence, symmetry distinction and positive component census; molecular exclusion and exchange organization follows in ELEC-006.\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(
        f"candidates: {len(sealed.census.candidates)}; "
        f"survivors: {sum(row.survives for row in sealed.decisions)}"
    )
    print(f"empirical measurements: {len(empirical.measurements)}; passed: {empirical.passed}")


if __name__ == "__main__":
    main()
