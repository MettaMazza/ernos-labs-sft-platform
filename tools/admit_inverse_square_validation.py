"""Admit and materialize the post-seal inverse-square empirical comparison."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine import EngineRepository  # noqa: E402
from sft.physics.inverse_square_validation import CLAIM_ID, EXPERIMENT_ID, SPEC  # noqa: E402


def load_execution():
    path = ROOT / "claims" / CLAIM_ID / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_inverse_square_validation_execution", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load inverse-square validation execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    execution = load_execution()
    captured = {}

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

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if CLAIM_ID not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append(
            {"claim_id": CLAIM_ID, "execution_file": f"claims/{CLAIM_ID}/execution.py"}
        )
        write_json(manifest_path, manifest)

    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
    row = next(item for item in census["claims"] if item["claim_id"] == CLAIM_ID)
    sealed = captured["sealed"]
    external = captured["external"]
    empirical = captured["empirical"]
    package = ROOT / "claims" / CLAIM_ID
    payloads = {
        "candidate_census.json": {"claim_id": CLAIM_ID, **asdict(sealed.census)},
        "elimination_receipt.json": {
            "claim_id": CLAIM_ID,
            "decisions": asdict(sealed)["decisions"],
            "closure": asdict(sealed.closure),
        },
        "controls.json": {"claim_id": CLAIM_ID, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": CLAIM_ID, **asdict(empirical)},
        "certificate.json": {
            "claim_id": CLAIM_ID,
            "status": "empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": row["receipt_path"],
            "exact_result": SPEC.exact_result,
            "closure_scope": receipt.closure_status,
            "controls_passed": all(item.passed for item in sealed.controls),
            "independently_recomputed": external.passed,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "formal_exponent_derived_from_measurement": False,
            "empirical_interpretation": "agreement_within_complete_reported_interval",
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)

    registration_path = package / "registration.json"
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    registration["status"] = "empirically_tested"
    write_json(registration_path, registration)

    experiment_path = ROOT / "experiments/physics" / EXPERIMENT_ID / "registration.json"
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment["status"] = "empirically_tested"
    experiment["measurement_receipt_hash"] = empirical.measurement_receipt_hash
    write_json(experiment_path, experiment)

    ledger_path = ROOT / "experiments/external_sources/physics/observations_inverse_square_validation.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger["current_result"]["empirical_validation_claim_admitted"] = True
    ledger["current_result"]["engine_receipt_hash"] = receipt.receipt_hash
    ledger["current_result"]["measurement_receipt_hash"] = empirical.measurement_receipt_hash
    write_json(ledger_path, ledger)

    certificate = payloads["certificate.json"]
    (package / "STATUS.md").write_text(
        f"# {CLAIM_ID}\n\nStatus: `empirically_tested_and_independently_replicated`\n\n"
        f"- Closure: `{certificate['closure_scope']}`\n"
        f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
        f"- Independent validation: `{certificate['external_validation_hash']}`\n"
        f"- Post-seal empirical validation: `{certificate['empirical_validation_hash']}`\n"
        f"- Measurement receipt: `{certificate['measurement_receipt_hash']}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n"
        "- Measurement supplied the formal exponent: `false`\n",
        encoding="utf-8",
    )
    print(f"admitted {CLAIM_ID}: {receipt.receipt_hash}")


if __name__ == "__main__":
    main()
