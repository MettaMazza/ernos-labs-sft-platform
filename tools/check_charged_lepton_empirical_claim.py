#!/usr/bin/env python3
"""Execute and preserve the fail-closed charged-lepton empirical claim."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine import EngineHalt, EngineRepository  # noqa: E402
from sft.physics.charged_lepton_validation import CLAIM_ID, comparison_record  # noqa: E402


def load_execution():
    path = ROOT / "claims" / CLAIM_ID / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_charged_lepton_empirical", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load charged-lepton empirical execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    execution = load_execution()
    try:
        EngineRepository(ROOT).execute_official(
            execution.program,
            execution.independent_validator,
            execution.source_files,
            execution.empirical_validator,
        )
    except EngineHalt as halted:
        if halted.receipt.halted_stage != "empirical_validation":
            raise
        short_hash = halted.receipt.receipt_hash.removeprefix("sha256:")[:16]
        relative_receipt = f"receipts/engine/rejected/{CLAIM_ID}-{short_hash}.json"
        analysis = {
            "schema": "sft-v3-failed-empirical-comparison/1",
            "claim_id": CLAIM_ID,
            "status": "empirical_validation_failed_not_admitted",
            "comparison": comparison_record(ROOT),
            "engine_receipt_hash": halted.receipt.receipt_hash,
            "engine_receipt_path": relative_receipt,
            "halted_stage": halted.receipt.halted_stage,
            "violations": halted.receipt.violations,
        }
        output = ROOT / "audits/physics_charged_lepton_empirical_failure.json"
        output.write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        registration_path = ROOT / "claims" / CLAIM_ID / "registration.json"
        registration = json.loads(registration_path.read_text(encoding="utf-8"))
        registration["status"] = "empirical_validation_failed_not_admitted"
        registration_path.write_text(json.dumps(registration, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (ROOT / "claims" / CLAIM_ID / "STATUS.md").write_text(
            f"# {CLAIM_ID}\n\nStatus: `empirical_validation_failed_not_admitted`\n\n"
            f"- Halted stage: `{halted.receipt.halted_stage}`\n"
            f"- Rejection receipt: `{halted.receipt.receipt_hash}`\n"
            f"- Receipt path: `{relative_receipt}`\n"
            "- Result: both exact predicted ratio intervals are outside their complete CODATA one-standard-uncertainty intervals\n",
            encoding="utf-8",
        )
        print(f"expected empirical halt preserved: {halted.receipt.receipt_hash}")
        return
    raise RuntimeError("charged-lepton empirical claim unexpectedly entered the model")


if __name__ == "__main__":
    main()
