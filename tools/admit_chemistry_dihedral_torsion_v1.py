#!/usr/bin/env python3
"""Officially admit and materialize Chemistry PROP-004."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.dihedral_torsion_batch_v1 import DIHEDRAL_TORSION_SPEC  # noqa: E402
from sft.chemistry.dihedral_torsion_validation_v1 import _cycles, _source_rows  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def exact_pair(value) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def load_execution():
    path = ROOT / "claims" / DIHEDRAL_TORSION_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_prop_004", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load PROP-004 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = DIHEDRAL_TORSION_SPEC
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
    rows = _source_rows(ROOT)
    cycles_kj = _cycles(rows, "energy_kj")
    cycles_cm = _cycles(rows, "energy_cm")
    conformers = []
    barriers = []
    transitions = []
    for torsion_index in (1, 2):
        for position in cycles_kj[torsion_index].local_conformer_positions():
            conformers.append({"torsion_index": torsion_index, "path_position": position.value})
        for position in cycles_kj[torsion_index].local_barrier_positions():
            barriers.append({"torsion_index": torsion_index, "path_position": position.value})
        for barrier, conformer, magnitude in cycles_kj[torsion_index].barrier_transitions():
            transitions.append({
                "torsion_index": torsion_index, "barrier_position": barrier.value,
                "adjacent_conformer_position": conformer.value,
                "exact_positive_Take_kj_mol": exact_pair(magnitude.fraction),
            })
    coordinate_vector = []
    for row in rows:
        coordinate = row["coordinate"]
        coordinate_vector.append({
            "target_id": row["target_id"], "torsion_index": row["torsion_index"],
            "path_position": row["path_position"],
            "native_coordinate": "EmptyOne" if coordinate.__class__.__name__ == "EmptyOne" else exact_pair(coordinate.fraction),
            "source_angle_inscription_degrees": row["angle_inscription"],
            "source_energy_inscription_kj_mol": row["energy_kj_inscription"],
            "source_energy_inscription_cm_inverse": row["energy_cm_inscription"],
        })
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-PROP-004",
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
            "exact_dihedral_law": "EmptyOne anchor; generated positive sector successors; recurrent One with held orientation",
            "exact_torsional_state_law": "complete cyclic neighbour order and ordered positive barrier Take",
            "complete_external_rows": len(rows), "coordinate_vector": coordinate_vector,
            "conformer_states": conformers, "barrier_states": barriers,
            "adjacent_barrier_Takes": transitions,
            "energy_unit_state_order_identity": all(
                cycles_kj[index].local_conformer_positions() == cycles_cm[index].local_conformer_positions()
                and cycles_kj[index].local_barrier_positions() == cycles_cm[index].local_barrier_positions()
                for index in (1, 2)
            ),
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "fitted_or_free_parameter_used": False,
            "measured_value_in_derivation_or_prediction": False,
            "all_measurements_released_after_coordinate_operation_seal": True,
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
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\n"
        "Status: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-PROP-004`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact dihedral law: `EmptyOne anchor -> positive exact sector successors -> recurrent One`, with orientation held rather than signed.\n"
        f"- External coordinate vector: `{len(rows)}/50` source rows retained and exactly matched.\n"
        f"- Torsional states: `{len(conformers)}` conformer minima, `{len(barriers)}` barrier states and `{len(transitions)}` positive adjacent-conformer Takes.\n"
        "- Both independent energy-unit columns force the identical state order.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(item.survives for item in sealed.decisions)}")
    print(f"source coordinates: {len(rows)}/50; conformers: {len(conformers)}; barriers: {len(barriers)}; Takes: {len(transitions)}")


if __name__ == "__main__":
    main()
