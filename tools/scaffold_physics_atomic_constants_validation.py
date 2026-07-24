"""Scaffold post-seal atomic-constant validation packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.physics.atomic_constants_validation import VALIDATION_SPECS  # noqa: E402
from tools.scaffold_physics_measurement_claims import (  # noqa: E402
    claim_registration,
    experiment_registration,
    independent_source,
    note,
    write,
)


def execution_source(spec) -> str:
    return f'''"""Official execution binding for {spec.claim_id}."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.atomic_constants_validation import VALIDATION_SPECS, VALIDATOR_BY_ID
from sft.physics.generated_empirical_law import GeneratedEmpiricalPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in VALIDATION_SPECS if item.claim_id == {spec.claim_id!r})
    source_files = (
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/measured_value.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/atomic_constants_validation.py",
        root / "claims/{spec.claim_id}/execution.py",
        root / "sft/engine/fold_language.py",
        root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{spec.claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalPhysicsProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            {spec.claim_id.lower()!r} + "-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=VALIDATOR_BY_ID[spec.claim_id](root),
    )
'''


def main() -> None:
    for spec in VALIDATION_SPECS:
        package = ROOT / "claims" / spec.claim_id
        write(package / "registration.json", json.dumps(claim_registration(spec), indent=2) + "\n")
        write(package / "execution.py", execution_source(spec))
        write(package / "independent_validator.py", independent_source(spec))
        write(package / "WHY_DERIVATION_CHECK.md", note(spec))
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        experiment = ROOT / "experiments/physics" / spec.experiment_id
        write(experiment / "registration.json", json.dumps(experiment_registration(spec), indent=2) + "\n")
        print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()
