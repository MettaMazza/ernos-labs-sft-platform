"""Scaffold one registered empirical Physics group from its frozen spec catalog."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.physics.group_registry import GROUPS  # noqa: E402
from tools.scaffold_physics_measurement_claims import (  # noqa: E402
    claim_registration,
    experiment_registration,
    independent_source,
    note,
    write,
)


def execution_source(spec, module_name: str, variable_name: str, measured_value: bool) -> str:
    module_path = module_name.replace(".", "/") + ".py"
    measured_import = ""
    measured_source = ""
    empirical_validator = "BlindExternalMeasurementValidator(root, spec)"
    if measured_value:
        measured_import = (
            "from sft.physics.measured_value import BlindExactMeasuredValueValidator\n"
            f"from {module_name} import VALUE_SPECS\n"
        )
        measured_source = '\n        root / "sft/physics/measured_value.py",'
        empirical_validator = "BlindExactMeasuredValueValidator(root, VALUE_SPECS[spec.claim_id])"
    return f'''"""Official execution binding for {spec.claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.generated_empirical_law import BlindExternalMeasurementValidator, GeneratedEmpiricalPhysicsProgram
from {module_name} import {variable_name}
{measured_import}from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in {variable_name} if item.claim_id == {spec.claim_id!r})
    source_files = (
        root / "sft/physics/generated_empirical_law.py",
        root / {module_path!r},
        {measured_source}
        root / "claims/{spec.claim_id}/execution.py",
        root / "sft/engine/fold_language.py", root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py", root / "sft/engine/isolation.py", root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{spec.claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalPhysicsProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator({spec.claim_id.lower()!r} + "-independent-python/1", (sys.executable, str(validator)), validator.parent, (validator,)),
        source_files=source_files,
        empirical_validator={empirical_validator},
    )
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("group", choices=tuple(GROUPS))
    args = parser.parse_args()
    module_name, variable_name, specs = GROUPS[args.group]
    module = importlib.import_module(module_name)
    value_specs = getattr(module, "VALUE_SPECS", {})
    for spec in specs:
        package = ROOT / "claims" / spec.claim_id
        write(package / "registration.json", json.dumps(claim_registration(spec), indent=2) + "\n")
        write(package / "execution.py", execution_source(spec, module_name, variable_name, spec.claim_id in value_specs))
        write(package / "independent_validator.py", independent_source(spec))
        write(package / "WHY_DERIVATION_CHECK.md", note(spec))
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        experiment = ROOT / "experiments/physics" / spec.experiment_id
        write(experiment / "registration.json", json.dumps(experiment_registration(spec), indent=2) + "\n")
        print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()
