"""Scaffold the three clean V3 g-block prediction packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.gblock_predictions import GBLOCK_PREDICTION_SPECS  # noqa: E402
from sft.physics.generated_empirical_law import survivor_id  # noqa: E402
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
from sft.chemistry.gblock_predictions import GBLOCK_PREDICTION_SPECS
from sft.chemistry.generated_law import GeneratedEmpiricalChemistryProgram
from sft.chemistry.generated_periodic_law import BlindPeriodicChemistryValidator
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in GBLOCK_PREDICTION_SPECS if item.claim_id == {spec.claim_id!r})
    source_files = (
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_periodic_law.py",
        root / "sft/chemistry/gblock_predictions.py",
        root / "sft/physics/atomic_constants.py",
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


def note(spec) -> str:
    return f"""# {spec.title}

Claim: `{spec.claim_id}`

## WHY

{spec.statement}

## DERIVATION

The complete registered eight-axis product contains 256 forms. The sole form
that preserves the admitted Physics prerequisites, exact fill trace, source
custody, evidence-status distinction and no-extra-rule boundary is:

`{survivor_id(spec)}`

Exact consequence:

> {spec.exact_result}

Base: {spec.induction_base}

Successor/termination: {spec.induction_step}

## CHECK

The independent validator regenerates all 256 forms and the sole survivor. A
separate post-seal custodian reconstructs the official observed-table prefix
from the byte-sealed IUPAC PDF. The capability-closed prediction has no target,
filesystem, network, process, clock, environment or dynamic-import operation.
Every source row and a deliberately changed adverse control are retained.

The IUPAC record validates only the known prefix through element 118. Values
beyond 118 remain standing predictions; this package does not label them
observed or empirically confirmed.

## FALSIFICATION

{spec.falsification_condition}
"""


def main() -> None:
    for spec in GBLOCK_PREDICTION_SPECS:
        package = ROOT / "claims" / spec.claim_id
        write(package / "registration.json", json.dumps(claim_registration(spec), indent=2, sort_keys=True) + "\n")
        write(package / "execution.py", execution_source(spec))
        write(package / "independent_validator.py", independent_source(spec))
        write(package / "WHY_DERIVATION_CHECK.md", note(spec))
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        experiment = ROOT / "experiments/chemistry" / spec.experiment_id
        registration = experiment_registration(spec)
        registration["evidence_mode"] = "formal_forcing_plus_known_domain_validation_and_sealed_unobserved_prediction"
        registration["evaluation_protocol"]["acceptance_condition"] = "The official known prefix matches, every row is retained, the changed row fails, and future coordinates remain explicitly unobserved."
        write(experiment / "registration.json", json.dumps(registration, indent=2, sort_keys=True) + "\n")
        print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()
