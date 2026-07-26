#!/usr/bin/env python3
"""Submit mediator range/channel closure to the frozen engine."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine import EngineRepository  # noqa: E402
from sft.physics.mediator_range_channel_terminal_law_v1 import CLAIM_ID, SPEC  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / CLAIM_ID / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_mediator_range_channel", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load mediator range/channel execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    expected_engine = "ad30f4866c18b2adbade95a0b2de40d5caa61308"
    actual_engine = subprocess.run(("git", "rev-parse", "HEAD:sft/engine"), cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    if actual_engine != expected_engine or subprocess.run(("git", "diff", "--quiet", "--", "sft/engine"), cwd=ROOT).returncode != 0:
        raise SystemExit("frozen engine identity changed; admission halted")
    census_path = ROOT / "census/claims.json"
    existing = {row["claim_id"] for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    if CLAIM_ID in existing:
        raise SystemExit(f"{CLAIM_ID} is already admitted; immutable receipt retained")
    execution = load_execution()
    receipt = EngineRepository(ROOT).execute_official(execution.program, execution.independent_validator, execution.source_files)
    print(f"admitted {CLAIM_ID}: {receipt.receipt_hash}")
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if CLAIM_ID not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": CLAIM_ID, "execution_file": f"claims/{CLAIM_ID}/execution.py"})
        write_json(manifest_path, manifest)
    completed = subprocess.run((sys.executable, str(ROOT / "tools/materialize_claim_evidence.py"), CLAIM_ID, SPEC.exact_result), cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)
    package = ROOT / "claims" / CLAIM_ID
    registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
    registration["status"] = "independently_replicated_with_inherited_postseal_comparison"
    write_json(package / "registration.json", registration)
    row = next(item for item in json.loads(census_path.read_text(encoding="utf-8"))["claims"] if item["claim_id"] == CLAIM_ID)
    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    (package / "STATUS.md").write_text("\n".join((f"# {CLAIM_ID}", "", "Status: `independently_replicated_with_inherited_postseal_comparison`", "", "- The formal preserved/broken channel and range law is independently replicated.", "- The admitted electroweak and residual-range dependencies supply the already sealed W/Z and mediator comparisons.", "- The native finite trace is not misreported as a universal hard physical cutoff.", f"- Closure: `{certificate['closure_scope']}`", f"- Derivation seal: `{certificate['derivation_seal_hash']}`", f"- Independent validation: `{certificate['external_validation_hash']}`", f"- Engine receipt: `{receipt.receipt_hash}`", f"- Receipt path: `{row['receipt_path']}`", "")), encoding="utf-8")
    print(completed.stdout.strip())


if __name__ == "__main__":
    main()
