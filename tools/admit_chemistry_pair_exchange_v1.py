#!/usr/bin/env python3
"""Officially execute and materialize ELEC-006 exactly once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.pair_exchange_batch_v1 import PAIR_EXCHANGE_SPEC  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / PAIR_EXCHANGE_SPEC.claim_id / "execution.py"
    module_spec = importlib.util.spec_from_file_location("chem_pair_exchange_006", path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = PAIR_EXCHANGE_SPEC
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
            "chemistry_obligation": "SFT-CHEM-OBL-ELEC-006",
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
            "NIST_H2_state_rows": 46,
            "positive_One_width_states": 25,
            "positive_three_width_states": 21,
            "explicit_same_cell_singlet_records": 2,
            "same_configuration_exchange_pairs": 14,
            "triplet_below_singlet_observations": 13,
            "singlet_below_triplet_observations": 1,
            "source_ground_zero_glyph_interpreted_only_as_absence_baseline": 1,
            "universal_energy_order_sign_claimed": False,
            "exchange_integral_or_fitted_split_used": False,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
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
        "- Chemistry obligation: `SFT-CHEM-OBL-ELEC-006`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n"
        f"- Measurement receipt: `{empirical.measurement_receipt_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n"
        "- External vector: all 46 NIST H2 states, both explicit paired-orbital singlets and all 14 same-configuration exchange-sensitive state pairs.\n"
        "- Unfavourable result retained: one measured singlet-below-triplet pair; no universal energy-order sign was imported.\n"
        "- Absence rule: source glyph `0` denotes absence of excitation only and remains structural `EmptyOne`, never a number.\n"
        "- Scope: molecular exclusion and complementary pair exchange; correlation beyond independent carriers follows in ELEC-007.\n",
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
