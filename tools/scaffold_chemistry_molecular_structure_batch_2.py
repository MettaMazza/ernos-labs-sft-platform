"""Materialize the pre-source-sealed Molecular Structure batch."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.molecular_structure_batch_2 import (  # noqa: E402
    MOLECULAR_STRUCTURE_BATCH_2_SPECS,
)
from tools.scaffold_chemistry_ready_claims import (  # noqa: E402
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
from sft.chemistry.generated_goldbook_extended_law import BlindExtendedGoldBookValidator
from sft.chemistry.generated_law import GeneratedEmpiricalChemistryProgram
from sft.chemistry.molecular_structure_batch_2 import MOLECULAR_STRUCTURE_BATCH_2_SPECS
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in MOLECULAR_STRUCTURE_BATCH_2_SPECS if item.claim_id == {spec.claim_id!r})
    source_files = (
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_goldbook_extended_law.py",
        root / "sft/chemistry/molecular_structure_derivation.py",
        root / "sft/chemistry/molecular_structure_batch_2.py",
        root / "experiments/sealed_predictions/chemistry_molecular_structure_batch_2_pre_source.json",
        root / "experiments/sealed_predictions/chemistry_molecular_structure_batch_2_dependency_amendment.json",
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
        empirical_validator=BlindExtendedGoldBookValidator(root, spec),
    )
'''


def main() -> None:
    admitted = {
        row["claim_id"]
        for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
    }
    for spec in MOLECULAR_STRUCTURE_BATCH_2_SPECS:
        if spec.claim_id in admitted:
            print(f"preserved admitted package {spec.claim_id}")
            continue
        package = ROOT / "claims" / spec.claim_id
        registration = claim_registration(spec)
        registration["pre_source_derivation_seal"] = (
            "experiments/sealed_predictions/chemistry_molecular_structure_batch_2_pre_source.json"
        )
        registration["dependency_identity_amendment"] = (
            "experiments/sealed_predictions/chemistry_molecular_structure_batch_2_dependency_amendment.json"
        )
        write(
            package / "registration.json",
            json.dumps(registration, indent=2, sort_keys=True) + "\n",
        )
        write(package / "execution.py", execution_source(spec))
        write(package / "independent_validator.py", independent_source(spec))
        why = note(spec).replace(
            "The prediction specification contains the public source and snapshot identities,",
            "The Fold grammar and consequence were byte-sealed before source selection. The later binding contains the public source and snapshot identities,",
        )
        write(package / "WHY_DERIVATION_CHECK.md", why)
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        experiment = ROOT / "experiments/chemistry" / spec.experiment_id
        record = experiment_registration(spec)
        record["pre_source_derivation_seal"] = (
            "experiments/sealed_predictions/chemistry_molecular_structure_batch_2_pre_source.json"
        )
        record["dependency_identity_amendment"] = (
            "experiments/sealed_predictions/chemistry_molecular_structure_batch_2_dependency_amendment.json"
        )
        write(
            experiment / "registration.json",
            json.dumps(record, indent=2, sort_keys=True) + "\n",
        )
        print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()
