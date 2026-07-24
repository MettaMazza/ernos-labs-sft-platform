"""Materialize the immutable second Chemistry measurement-identity batch."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.measurement_identity_batch_2 import (  # noqa: E402
    MEASUREMENT_IDENTITY_BATCH_2_SPECS,
)
from tools.scaffold_chemistry_ready_claims import (  # noqa: E402
    claim_registration,
    experiment_registration,
    independent_source,
    note,
    write,
)


def execution_source(spec, catalog_module: str, catalog_symbol: str, catalog_path: str) -> str:
    return f'''"""Official execution binding for {spec.claim_id}."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from {catalog_module} import {catalog_symbol}
from sft.chemistry.generated_law import BlindExternalChemistryValidator, GeneratedEmpiricalChemistryProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in {catalog_symbol} if item.claim_id == {spec.claim_id!r})
    source_files = (
        root / "sft/chemistry/generated_law.py",
        root / {catalog_path!r},
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
        empirical_validator=BlindExternalChemistryValidator(root, spec),
    )
'''


def scaffold_specs(specs, catalog_module: str, catalog_symbol: str, catalog_path: str) -> None:
    admitted = {
        row["claim_id"]
        for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
    }
    for spec in specs:
        if spec.claim_id in admitted:
            print(f"preserved admitted package {spec.claim_id}")
            continue
        package = ROOT / "claims" / spec.claim_id
        write(package / "registration.json", json.dumps(claim_registration(spec), indent=2, sort_keys=True) + "\n")
        write(
            package / "execution.py",
            execution_source(spec, catalog_module, catalog_symbol, catalog_path),
        )
        write(package / "independent_validator.py", independent_source(spec))
        write(package / "WHY_DERIVATION_CHECK.md", note(spec))
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        experiment = ROOT / "experiments/chemistry" / spec.experiment_id
        write(
            experiment / "registration.json",
            json.dumps(experiment_registration(spec), indent=2, sort_keys=True) + "\n",
        )
        print(f"scaffolded {spec.claim_id}")


def main() -> None:
    scaffold_specs(
        MEASUREMENT_IDENTITY_BATCH_2_SPECS,
        "sft.chemistry.measurement_identity_batch_2",
        "MEASUREMENT_IDENTITY_BATCH_2_SPECS",
        "sft/chemistry/measurement_identity_batch_2.py",
    )


if __name__ == "__main__":
    main()
