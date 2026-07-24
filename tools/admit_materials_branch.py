"""Execute, admit and materialize all 84 Materials laws in dependency order."""

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
from sft.materials.generated_law import MATERIALS_SPECS, PRE_SOURCE_SEAL_PATH  # noqa: E402
from tools.scaffold_materials_claims import EXACT_COUNT_CLAIMS  # noqa: E402


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location(
        "sft_materials_" + claim_id.replace("-", "_"), path
    )
    if definition is None or definition.loader is None:
        raise RuntimeError(f"cannot load {claim_id}")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _manifest_entry(claim_id: str) -> None:
    path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    known = {row["claim_id"] for row in manifest["claims"]}
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
    exact_value = EXACT_COUNT_CLAIMS.get(spec.claim_id)
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
            "status": "model_admitted_authoritatively_corresponded_and_independently_replicated",
            "pre_source_complete_branch_seal": PRE_SOURCE_SEAL_PATH,
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
            "external_evidence_class": "post_seal_measurement_body_correspondence",
            "exact_structural_value_validated": exact_value,
            "specimen_dependent_magnitude_claimed_as_universal": False,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)

    registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
    registration["status"] = "empirically_tested"
    write_json(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/materials" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment["status"] = "authoritatively_corresponded"
    write_json(experiment_path, experiment)
    certificate = payloads["certificate.json"]
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\n"
        "Status: `model_admitted_authoritatively_corresponded_and_independently_replicated`\n\n"
        f"- Closure: `{certificate['closure_scope']}`\n"
        f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
        f"- Independent validation: `{certificate['external_validation_hash']}`\n"
        f"- Post-seal authority correspondence: `{certificate['empirical_validation_hash']}`\n"
        f"- External receipt: `{certificate['measurement_receipt_hash']}`\n"
        f"- Engine receipt: `{row['receipt_hash']}`\n"
        f"- External source IDs: {', '.join(certificate['external_data_source_ids'])}\n"
        f"- Exact structural value validated: `{exact_value or 'not a universal numeric magnitude'}`\n"
        "- Specimen-dependent magnitude claimed as universal: `false`\n",
        encoding="utf-8",
    )


def main() -> None:
    repository = EngineRepository(ROOT)
    for index, spec in enumerate(MATERIALS_SPECS, 1):
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
        _manifest_entry(spec.claim_id)
        _materialize(spec, execution, receipt, captured)
        print(
            f"[{index}/{len(MATERIALS_SPECS)}] admitted and materialized {spec.claim_id}: "
            f"{receipt.receipt_hash}"
        )


if __name__ == "__main__":
    main()
