#!/usr/bin/env python3
"""Submit accumulated coupling separation to the frozen engine."""

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
from sft.physics.coupling_accumulated_separation_terminal_law_v1 import (  # noqa: E402
    CLAIM_ID,
    SPEC,
)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / CLAIM_ID / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_coupling_accumulated", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load accumulated coupling execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    expected_engine = "ad30f4866c18b2adbade95a0b2de40d5caa61308"
    actual_engine = subprocess.run(
        ("git", "rev-parse", "HEAD:sft/engine"),
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if actual_engine != expected_engine:
        raise SystemExit("frozen engine identity changed; admission halted")

    existing = {
        row["claim_id"]: row
        for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))[
            "claims"
        ]
    }
    if CLAIM_ID in existing:
        raise SystemExit(f"{CLAIM_ID} is already admitted; immutable receipt retained")

    execution = load_execution()
    receipt = EngineRepository(ROOT).execute_official(
        execution.program,
        execution.independent_validator,
        execution.source_files,
    )
    print(f"admitted {CLAIM_ID}: {receipt.receipt_hash}")

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if CLAIM_ID not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append(
            {"claim_id": CLAIM_ID, "execution_file": f"claims/{CLAIM_ID}/execution.py"}
        )
        write_json(manifest_path, manifest)

    completed = subprocess.run(
        (
            sys.executable,
            str(ROOT / "tools/materialize_claim_evidence.py"),
            CLAIM_ID,
            SPEC.exact_result,
        ),
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)

    package = ROOT / "claims" / CLAIM_ID
    registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
    registration["status"] = "independently_replicated"
    write_json(package / "registration.json", registration)
    row = next(
        item
        for item in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))[
            "claims"
        ]
        if item["claim_id"] == CLAIM_ID
    )
    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    (package / "STATUS.md").write_text(
        "\n".join(
            (
                f"# {CLAIM_ID}",
                "",
                "Status: `independently_replicated`",
                "",
                f"- Closure: `{certificate['closure_scope']}`",
                "- Empirical status: exact formal successor of an already empirically tested running law",
                f"- Derivation seal: `{certificate['derivation_seal_hash']}`",
                f"- Independent validation: `{certificate['external_validation_hash']}`",
                f"- Engine receipt: `{receipt.receipt_hash}`",
                f"- Receipt path: `{row['receipt_path']}`",
                "",
            )
        ),
        encoding="utf-8",
    )
    print(completed.stdout.strip())


if __name__ == "__main__":
    main()
