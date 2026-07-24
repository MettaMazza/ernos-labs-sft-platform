"""Execute and preserve the three expected fail-closed prerequisite receipts."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine import EngineHalt, EngineRepository  # noqa: E402
from sft.engine.source import build_source_manifest  # noqa: E402
from sft.physics.chemistry_prediction_prerequisites import QUESTIONS, build_program  # noqa: E402


SOURCE = ROOT / "sft/physics/chemistry_prediction_prerequisites.py"


class UnreachableIndependentValidator:
    def validate(self, sealed):
        raise AssertionError("an unclosed prerequisite reached independent validation")


def main() -> None:
    repository = EngineRepository(ROOT)
    source_hash = build_source_manifest(ROOT, (SOURCE,)).manifest_hash
    for question in QUESTIONS:
        try:
            repository.execute_official(
                build_program(question, source_hash),
                UnreachableIndependentValidator(),
                (SOURCE,),
            )
        except EngineHalt as halted:
            receipt = halted.receipt
            if receipt.halted_stage != "forcing" or receipt.model_admitted:
                raise RuntimeError(f"unexpected prerequisite outcome for {question.claim_id}") from halted
            print(
                f"HALTED {question.claim_id} at forcing: {receipt.receipt_hash}; "
                + "; ".join(receipt.violations)
            )
        else:
            raise RuntimeError(f"unclosed prerequisite was unexpectedly admitted: {question.claim_id}")


if __name__ == "__main__":
    main()
