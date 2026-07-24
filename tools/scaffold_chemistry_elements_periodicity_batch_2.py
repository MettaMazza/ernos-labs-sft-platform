"""Materialize the second immutable Elements and Periodicity batch."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.elements_periodicity_batch_2 import (  # noqa: E402
    ELEMENTS_PERIODICITY_BATCH_2_SPECS,
)
from tools.scaffold_chemistry_ready_claims import (  # noqa: E402
    claim_registration,
    experiment_registration,
    independent_source,
    write,
)


def execution_source(spec) -> str:
    return f'''"""Official execution binding for {spec.claim_id}."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.elements_periodicity_batch_2 import ELEMENTS_PERIODICITY_BATCH_2_SPECS
from sft.chemistry.generated_law import GeneratedEmpiricalChemistryProgram
from sft.chemistry.generated_periodic_law import BlindPeriodicChemistryValidator
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in ELEMENTS_PERIODICITY_BATCH_2_SPECS if item.claim_id == {spec.claim_id!r})
    source_files = (
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_periodic_law.py",
        root / "sft/chemistry/elements_periodicity_batch_2.py",
        root / "claims/{spec.claim_id}/execution.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/engine/fold_language.py",
        root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{spec.claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalChemistryProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            {spec.claim_id.lower()!r} + "-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=BlindPeriodicChemistryValidator(root, spec),
    )
'''


def periodic_note(spec) -> str:
    from sft.physics.generated_empirical_law import survivor_id

    return f"""# {spec.title}

Claim: `{spec.claim_id}`

## WHY

{spec.statement}

## DERIVATION

The complete content-specific eight-axis product contains 256 generated forms.
Exactly one preserves every required coordinate and contains no extra identity
or layout rule:

`{survivor_id(spec)}`

The admitted consequence is:

> {spec.exact_result}

Base: {spec.induction_base}

Successor: {spec.induction_step}

## CHECK

The prediction specification contains public source identities and hashes but
no observed target label.  A distinct post-seal custodian reconstructs the
registered categorical result from either current IUPAC Gold Book JSON or
literal text extracted from the byte-sealed official periodic-table PDF by a
standard-library parser.  Every required fragment must be present.  The
capability-closed predictor cannot read either target.  Every row is retained
and a deliberately changed target fails exact comparison.

This is categorical authoritative correspondence.  It is not a prediction of
decimal element properties, and the current element census is not promoted
into a proof that later elements are impossible.
"""


def periodic_experiment_registration(spec) -> dict[str, object]:
    record = experiment_registration(spec)
    record["evidence_mode"] = "blind_mixed_source_authoritative_correspondence"
    record["evaluation_protocol"]["evaluator_id"] = (
        spec.experiment_id + "-post-seal-mixed-source-evaluator"
    )
    record["evaluation_protocol"]["metrics"][0]["definition"] = (
        "After prediction sealing, reconstruct registered categorical features from required fragments "
        "of byte-sealed official IUPAC Gold Book JSON or periodic-table PDF content streams, then "
        "compare the resulting held label with the sealed Fold consequence."
    )
    record["evaluation_protocol"]["metrics"][0]["unit_protocol"] = (
        "Categorical authoritative correspondence; no decimal measured value is used as a proof scalar."
    )
    return record


def main() -> None:
    admitted = {
        row["claim_id"]
        for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
    }
    for spec in ELEMENTS_PERIODICITY_BATCH_2_SPECS:
        if spec.claim_id in admitted:
            print(f"preserved admitted package {spec.claim_id}")
            continue
        package = ROOT / "claims" / spec.claim_id
        write(
            package / "registration.json",
            json.dumps(claim_registration(spec), indent=2, sort_keys=True) + "\n",
        )
        write(package / "execution.py", execution_source(spec))
        write(package / "independent_validator.py", independent_source(spec))
        write(package / "WHY_DERIVATION_CHECK.md", periodic_note(spec))
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        experiment = ROOT / "experiments/chemistry" / spec.experiment_id
        write(
            experiment / "registration.json",
            json.dumps(periodic_experiment_registration(spec), indent=2, sort_keys=True) + "\n",
        )
        print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()
