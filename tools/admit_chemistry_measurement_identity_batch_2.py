"""Admit and materialize the immutable second Chemistry identity batch."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.measurement_identity_batch_2 import (  # noqa: E402
    MEASUREMENT_IDENTITY_BATCH_2_SPECS,
)
from sft.engine import EngineRepository  # noqa: E402


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location(
        "sft_chemistry_batch_2_" + claim_id.replace("-", "_"), path
    )
    if definition is None or definition.loader is None:
        raise RuntimeError(f"cannot load {claim_id}")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _ensure_manifest_entry(claim_id: str) -> None:
    path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    known = [row["claim_id"] for row in manifest["claims"]]
    if claim_id not in known:
        manifest["claims"].append(
            {"claim_id": claim_id, "execution_file": f"claims/{claim_id}/execution.py"}
        )
        write_json(path, manifest)


def _materialize(spec, execution, receipt, captured) -> None:
    sealed = captured["sealed"]
    external = captured["external"]
    empirical = captured["empirical"]
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
    row = next(item for item in census["claims"] if item["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
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
            "status": "authoritatively_corresponded_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": row["receipt_path"],
            "exact_result": spec.exact_result,
            "closure_scope": receipt.closure_status,
            "controls_passed": all(item.passed for item in sealed.controls),
            "independently_recomputed": external.passed,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "external_evidence_class": "categorical_authoritative_correspondence",
            "numerical_measurement_claimed": False,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)

    registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
    registration["status"] = "empirically_tested"
    write_json(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment["status"] = "authoritatively_corresponded"
    write_json(experiment_path, experiment)
    certificate = payloads["certificate.json"]
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `authoritatively_corresponded_and_independently_replicated`\n\n"
        f"- Closure: `{certificate['closure_scope']}`\n"
        f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
        f"- Independent validation: `{certificate['external_validation_hash']}`\n"
        f"- Post-seal authoritative correspondence: `{certificate['empirical_validation_hash']}`\n"
        f"- External receipt: `{certificate['measurement_receipt_hash']}`\n"
        f"- Engine receipt: `{row['receipt_hash']}`\n"
        f"- External source IDs: {', '.join(certificate['external_data_source_ids'])}\n"
        "- Numerical measurement claimed: `false`\n",
        encoding="utf-8",
    )
    print(
        f"materialized {spec.claim_id}: {len(sealed.census.candidates)} candidates; "
        f"{len(empirical.measurements)} external rows"
    )


def admit_specs(specs) -> None:
    repository = EngineRepository(ROOT)
    for index, spec in enumerate(specs, 1):
        execution = load_execution(spec.claim_id)
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

        receipt = repository.execute_official(
            execution.program,
            CaptureIndependent(),
            execution.source_files,
            CaptureEmpirical(),
        )
        _ensure_manifest_entry(spec.claim_id)
        _materialize(spec, execution, receipt, captured)
        print(
            f"[{index}/{len(specs)}] admitted "
            f"{spec.claim_id}: {receipt.receipt_hash}"
        )

    from tools.freeze_chemistry_inventory import main as refresh_inventory

    refresh_inventory()


def main() -> None:
    admit_specs(MEASUREMENT_IDENTITY_BATCH_2_SPECS)


if __name__ == "__main__":
    main()
