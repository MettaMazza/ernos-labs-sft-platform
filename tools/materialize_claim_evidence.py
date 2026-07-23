"""Project an admitted formal claim into its complete machine-evidence package."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine import EngineRepository  # noqa: E402
from sft.engine.receipt_io import read_receipt  # noqa: E402
from sft.engine.source import build_source_manifest  # noqa: E402


def load_execution(execution_path: Path):
    specification = importlib.util.spec_from_file_location(
        "sft_evidence_materialization", execution_path
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("execution module cannot be loaded")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("claim_id")
    parser.add_argument("exact_result")
    args = parser.parse_args()
    package = ROOT / "claims" / args.claim_id
    execution = load_execution(package / "execution.py")
    captured = {}

    class Capture:
        def validate(self, sealed):
            captured["sealed"] = sealed
            result = execution.independent_validator.validate(sealed)
            captured["external"] = result
            return result

    receipt = EngineRepository(ROOT).engine.run(
        execution.program,
        Capture(),
        executed_source_hash=build_source_manifest(
            ROOT, execution.source_files
        ).manifest_hash,
    )
    census = json.loads((ROOT / "census" / "claims.json").read_text(encoding="utf-8"))
    row = next(item for item in census["claims"] if item["claim_id"] == args.claim_id)
    if receipt != read_receipt(ROOT / row["receipt_path"]):
        raise RuntimeError("fresh receipt does not match admitted evidence")
    sealed = captured["sealed"]
    external = captured["external"]
    payloads = {
        "candidate_census.json": {"claim_id": args.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {
            "claim_id": args.claim_id,
            "decisions": asdict(sealed)["decisions"],
            "closure": asdict(sealed.closure),
        },
        "controls.json": {
            "claim_id": args.claim_id,
            "controls": asdict(sealed)["controls"],
        },
        "certificate.json": {
            "claim_id": args.claim_id,
            "status": "independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "external_validation_hash": receipt.external_validation_hash,
            "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": row["receipt_path"],
            "exact_result": args.exact_result,
            "closure_scope": receipt.closure_status,
            "controls_passed": all(item.passed for item in sealed.controls),
            "independently_recomputed": external.passed,
        },
    }
    for name, payload in payloads.items():
        (package / name).write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(f"materialized {args.claim_id}: {len(sealed.census.candidates)} candidates")


if __name__ == "__main__":
    main()
