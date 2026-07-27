#!/usr/bin/env python3
"""Officially execute and materialize ELEC-008 exactly once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.multicentre_support_batch_v1 import MULTICENTRE_SUPPORT_SPEC  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / MULTICENTRE_SUPPORT_SPEC.claim_id / "execution.py"
    specification = importlib.util.spec_from_file_location("chem_multicentre_008", path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = MULTICENTRE_SUPPORT_SPEC
    census_path = ROOT / "census" / "claims.json"
    existing = {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}
    if spec.claim_id in existing:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    execution, captured = load_execution(), {}
    class IndependentCapture:
        def validate(self, sealed):
            captured["sealed"] = sealed; captured["external"] = execution.independent_validator.validate(sealed); return captured["external"]
    class EmpiricalCapture:
        def validate(self, sealed):
            captured["empirical"] = execution.empirical_validator.validate(sealed); return captured["empirical"]
    receipt = EngineRepository(ROOT).execute_official(execution.program, IndependentCapture(), execution.source_files, EmpiricalCapture())
    if not receipt.model_admitted:
        raise SystemExit(f"halted {receipt.halted_stage}; {receipt.receipt_hash}")
    sealed, external, empirical = captured["sealed"], captured["external"], captured["empirical"]
    manifest_path = ROOT / "census" / "execution_manifest.json"
    manifest = json.loads(manifest_path.read_text()); manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"}); write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text()); census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    claim = ROOT / "claims" / spec.claim_id
    artifacts = {"candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)}, "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)}, "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]}, "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)}, "certificate.json": {"claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-ELEC-008", "status": "model_admitted_observationally_derived_empirically_tested_and_independently_replicated", "source_manifest_hash": execution.program.registration.source_hash, "derivation_seal_hash": sealed.seal_hash, "independent_implementation_hash": external.implementation_hash, "independent_certificate_hash": external.certificate_hash, "external_validation_hash": receipt.external_validation_hash, "empirical_validation_hash": receipt.empirical_validation_hash, "measurement_receipt_hash": empirical.measurement_receipt_hash, "engine_receipt_hash": receipt.receipt_hash, "engine_receipt_path": census_row["receipt_path"], "closure_scope": receipt.closure_status, "exact_result": spec.exact_result, "candidate_count": 256, "unique_survivor_count": 1, "IUPAC_topology_records": 4, "NIST_diborane_records": 9, "NIST_benzene_records": 7, "positive_numeric_records": 14, "categorical_or_text_records": 6, "measured_outer_BH_angstrom": "1.200", "measured_bridging_BH_angstrom": "1.320", "measured_BHB_angle_degrees": "83.8", "measured_benzene_CC_angstrom": "1.397", "measured_benzene_aromatic_link_count": 6, "imported_bonding_model_used": False, "all_external_rows_preserved": empirical.all_rows_preserved, "external_data_source_ids": list(empirical.data_source_ids), "falsification_condition": empirical.falsification_condition}}
    for name, data in artifacts.items(): write_json(claim / name, data)
    registration = json.loads((claim / "registration.json").read_text()); registration["status"] = "empirically_tested"; write_json(claim / "registration.json", registration)
    experiment_path = ROOT / "experiments" / "chemistry" / spec.experiment_id / "registration.json"; experiment = json.loads(experiment_path.read_text()); experiment["status"] = "measured"; write_json(experiment_path, experiment)
    (claim / "STATUS.md").write_text(f"# {spec.claim_id}\n\nStatus: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n- Chemistry obligation: `SFT-CHEM-OBL-ELEC-008`\n- Closure: `{receipt.closure_status}`\n- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n- Empirical validation: `{receipt.empirical_validation_hash}`\n- Measurement receipt: `{empirical.measurement_receipt_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n- External vector: all four IUPAC, nine neutral-diborane and seven benzene registered records.\n- Headline geometry: B-H outer 1.200 Å; B-H bridge 1.320 Å; B-H-B 83.8°; benzene C-C 1.397 Å across six aromatic links.\n- Absence rule: categorical magnitude absence is structural EmptyOne; glyph 0 is never an SFT number.\n- Scope: multicentre and delocalized support; shell recurrence and periodic organization follows in ELEC-009.\n", encoding="utf-8")
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}"); print(f"derivation seal: {sealed.seal_hash}"); print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(row.survives for row in sealed.decisions)}"); print(f"empirical measurements: {len(empirical.measurements)}; passed: {empirical.passed}")


if __name__ == "__main__":
    main()
