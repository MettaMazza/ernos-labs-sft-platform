#!/usr/bin/env python3
"""Officially admit and materialize Chemistry obligation ELEC-015."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.classical_quantum_correspondence_batch_v1 import (  # noqa: E402
    CLASSICAL_QUANTUM_SPEC,
)
from sft.chemistry.classical_quantum_correspondence_law_v1 import CERTIFICATE  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / CLASSICAL_QUANTUM_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_elec_015", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load ELEC-015 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = CLASSICAL_QUANTUM_SPEC
    census_path = ROOT / "census/claims.json"
    existing = {
        row["claim_id"]
        for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]
    }
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

    receipt = EngineRepository(ROOT).execute_official(
        execution.program,
        CaptureIndependent(),
        execution.source_files,
        empirical_validator=None,
    )
    if not receipt.model_admitted:
        raise SystemExit(
            f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}"
        )

    sealed = captured["sealed"]
    external = captured["external"]
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append(
            {"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"}
        )
        write_json(manifest_path, manifest)

    census = json.loads(census_path.read_text(encoding="utf-8"))
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {
            "claim_id": spec.claim_id,
            "decisions": asdict(sealed)["decisions"],
            "closure": asdict(sealed.closure),
        },
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "certificate.json": {
            "claim_id": spec.claim_id,
            "chemistry_obligation": "SFT-CHEM-OBL-ELEC-015",
            "status": "model_admitted_formal_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash,
            "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash,
            "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": census_row["receipt_path"],
            "closure_scope": receipt.closure_status,
            "exact_result": spec.exact_result,
            "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(item.survives for item in sealed.decisions),
            "classical_transition_rows": len(CERTIFICATE["classical_rows"]),
            "quantum_branch_rows": len(CERTIFICATE["quantum_decoded_rows"]),
            "complete_observation_records": len(CERTIFICATE["measurement_records"]),
            "inverse_restores_complete_input": CERTIFICATE["inverse_restores"],
            "branchwise_decoded_results_identical": CERTIFICATE["passed"],
            "phase_trace_preserved_as_quantum_distinction": True,
            "conventional_quantum_premise_imported": False,
            "natural_measurement_applicable": False,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)

    registration_path = package / "registration.json"
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    registration["status"] = "independently_replicated"
    write_json(registration_path, registration)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\n"
        "Status: `model_admitted_formal_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-ELEC-015`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n"
        "- Operational surface: identical decoded Chemistry for every classical and quantum branch, complete observation records, exact inverse restoration and positive resource accounting.\n"
        "- Empirical status: a new natural measurement is not applicable to this formal correspondence; its chemical transition and measurement surfaces are admitted dependencies.\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(item.survives for item in sealed.decisions)}")
    print("operational certificate: passed")


if __name__ == "__main__":
    main()
