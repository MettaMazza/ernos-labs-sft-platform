#!/usr/bin/env python3
"""Officially admit and materialize Chemistry PROP-003."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.bond_angle_batch_v1 import BOND_ANGLE_SPEC  # noqa: E402
from sft.chemistry.bond_angle_law_v1 import molecular_angle_vector  # noqa: E402
from sft.chemistry.bond_angle_validation_v1 import _load_targets  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def exact_pair(value) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def load_execution():
    path = ROOT / "claims" / BOND_ANGLE_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_prop_003", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load PROP-003 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = BOND_ANGLE_SPEC
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
        execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical()
    )
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
    targets = {row["target_id"]: row for row in _load_targets(ROOT)}
    quantitative = []
    for carrier in molecular_angle_vector():
        target = targets[carrier.target_id]
        degrees = carrier.turn_fraction * 360
        quantitative.append({
            "target_id": carrier.target_id, "species": carrier.species.label,
            "geometry": carrier.geometry.label, "angle_role": carrier.angle_role.label,
            "exact_turn_fraction": exact_pair(carrier.turn_fraction),
            "postseal_degree_translation": exact_pair(degrees),
            "source_degree_inscription": target["source_inscription"],
            "exact_match": degrees == target["source_degrees"],
        })

    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-PROP-003",
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
            "exact_angle_law": "k retained equal sectors in n-sector closed turn = k/n turn",
            "quantitative_vector": quantitative, "complete_external_rows": len(targets),
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "fitted_or_free_parameter_used": False,
            "measured_degree_in_derivation_or_prediction": False,
            "all_degree_values_released_after_turn_fraction_seal": True,
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
    status_lines = [
        f"# {spec.claim_id}", "",
        "Status: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`", "",
        "- Chemistry obligation: `SFT-CHEM-OBL-PROP-003`",
        f"- Closure: `{receipt.closure_status}`",
        "- Exact law: `k retained equal sectors in an n-sector closed turn = k/n turn`.",
    ]
    for row in quantitative:
        fraction = row["exact_turn_fraction"]
        status_lines.append(
            f"- {row['target_id']}: `{fraction['numerator']}/{fraction['denominator']}` turn -> "
            f"`{row['source_degree_inscription']}` degree; exact match: `{row['exact_match']}`."
        )
    status_lines.extend((
        f"- Derivation seal: `{sealed.seal_hash}`",
        f"- Independent validation: `{receipt.external_validation_hash}`",
        f"- Empirical validation: `{receipt.empirical_validation_hash}`",
        f"- Engine receipt: `{receipt.receipt_hash}`", "",
    ))
    (package / "STATUS.md").write_text("\n".join(status_lines), encoding="utf-8")
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(item.survives for item in sealed.decisions)}")
    for row in quantitative:
        print(f"{row['target_id']}: {row['source_degree_inscription']} degree; exact match {row['exact_match']}")


if __name__ == "__main__":
    main()
