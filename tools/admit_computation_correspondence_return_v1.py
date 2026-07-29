#!/usr/bin/env python3
"""Admit the frozen conditional computation-correspondence return claim."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.computation.correspondence_return_laws import CONDITIONAL_TRANSLATION  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


CLAIM_ID = CONDITIONAL_TRANSLATION.claim_id


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_seals() -> None:
    for tool, expected in (
        ("verify_engine_seal.py", "VALID_CANONICAL_ENGINE"),
        ("verify_verification_authority_seal.py", "VALID_CANONICAL_VERIFICATION_AUTHORITY"),
    ):
        completed = subprocess.run((sys.executable, str(ROOT / "tools" / tool), "--json"), cwd=ROOT, text=True, capture_output=True, check=False)
        if completed.returncode or expected not in completed.stdout:
            raise SystemExit(f"{tool} failed; admission halted\n{completed.stdout}{completed.stderr}")


def load_execution():
    path = ROOT / "claims" / CLAIM_ID / "execution.py"
    module_spec = importlib.util.spec_from_file_location("sft_comp_corr_return", path)
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    verify_seals()
    census_path = ROOT / "census" / "claims.json"
    existing = {row["claim_id"]: row for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    if CLAIM_ID in existing and existing[CLAIM_ID].get("model_admitted"):
        print("retained", CLAIM_ID, existing[CLAIM_ID]["receipt_hash"])
    else:
        execution = load_execution()
        receipt = EngineRepository(ROOT).execute_official(execution.program, execution.independent_validator, execution.source_files)
        print("admitted", CLAIM_ID, receipt.receipt_hash)

    manifest_path = ROOT / "census" / "execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if CLAIM_ID not in {item["claim_id"] for item in manifest["claims"]}:
        manifest["claims"].append({"claim_id": CLAIM_ID, "execution_file": f"claims/{CLAIM_ID}/execution.py"})
        write_json(manifest_path, manifest)

    completed = subprocess.run((sys.executable, str(ROOT / "tools" / "materialize_claim_evidence.py"), CLAIM_ID, CONDITIONAL_TRANSLATION.exact_result), cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stdout + completed.stderr)
    rows = {row["claim_id"]: row for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    package = ROOT / "claims" / CLAIM_ID
    registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
    registration["status"] = "independently_replicated"
    write_json(package / "registration.json", registration)
    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    row = rows[CLAIM_ID]
    (package / "STATUS.md").write_text(
        f"# {CLAIM_ID}\n\nStatus: `independently_replicated`\n\n"
        f"- Sub-branch: `complexity`\n- Closure: `{certificate['closure_scope']}`\n"
        f"- Empirical status: formal transport theorem; natural measurement value not applicable\n"
        f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
        f"- External validation: `{certificate['external_validation_hash']}`\n"
        f"- Engine receipt: `{row['receipt_hash']}`\n- Receipt path: `{row['receipt_path']}`\n",
        encoding="utf-8",
    )
    verify_seals()
    print(completed.stdout.strip())


if __name__ == "__main__":
    main()
