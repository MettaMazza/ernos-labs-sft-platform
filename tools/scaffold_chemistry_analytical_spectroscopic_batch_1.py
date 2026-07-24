"""Materialize the pre-source-sealed analytical/spectroscopic batch."""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.analytical_spectroscopic_batch_1 import ANALYTICAL_SPECTROSCOPIC_BATCH_1_SPECS  # noqa:E402
from tools.scaffold_chemistry_ready_claims import claim_registration, experiment_registration, independent_source, note, write  # noqa:E402


def execution_source(spec):
    return f'''"""Official execution binding for {spec.claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_law import GeneratedEmpiricalChemistryProgram
from sft.chemistry.generated_multi_source_law import BlindMultiSourceAuthorityValidator
from sft.chemistry.analytical_spectroscopic_batch_1 import ANALYTICAL_SPECTROSCOPIC_BATCH_1_SPECS
from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
 spec=next(x for x in ANALYTICAL_SPECTROSCOPIC_BATCH_1_SPECS if x.claim_id=={spec.claim_id!r})
 source_files=(root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_multi_source_law.py",root/"sft/chemistry/analytical_spectroscopic_derivation.py",root/"sft/chemistry/analytical_spectroscopic_batch_1.py",root/"experiments/sealed_predictions/chemistry_analytical_spectroscopic_batch_1_pre_source.json",root/"claims/{spec.claim_id}/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/engine/fold_language.py",root/"sft/engine/custody.py",root/"sft/engine/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py")
 source_hash=build_source_manifest(root,source_files).manifest_hash
 validator=root/"claims/{spec.claim_id}/independent_validator.py"
 return ClaimExecution(program=GeneratedEmpiricalChemistryProgram(spec,source_hash),independent_validator=ExternalCommandValidator({spec.claim_id.lower()!r}+"-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),source_files=source_files,empirical_validator=BlindMultiSourceAuthorityValidator(root,spec))
'''


def main():
    admitted = {row["claim_id"] for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]}
    for spec in ANALYTICAL_SPECTROSCOPIC_BATCH_1_SPECS:
        if spec.claim_id in admitted:
            print(f"preserved admitted package {spec.claim_id}")
            continue
        package = ROOT / "claims" / spec.claim_id
        registration = claim_registration(spec)
        registration["pre_source_derivation_seal"] = "experiments/sealed_predictions/chemistry_analytical_spectroscopic_batch_1_pre_source.json"
        write(package / "registration.json", json.dumps(registration, indent=2, sort_keys=True) + "\n")
        write(package / "execution.py", execution_source(spec))
        write(package / "independent_validator.py", independent_source(spec))
        write(package / "WHY_DERIVATION_CHECK.md", note(spec).replace("The prediction specification contains the public source and snapshot identities,", "The Fold grammar and consequence were byte-sealed before source selection. The later authority binding contains the public source-set and snapshot identities,"))
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        record = experiment_registration(spec)
        record["pre_source_derivation_seal"] = "experiments/sealed_predictions/chemistry_analytical_spectroscopic_batch_1_pre_source.json"
        record["authority_support_registry"] = "experiments/external_sources/chemistry/observations_analytical_spectroscopic_batch_1.json"
        write(ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json", json.dumps(record, indent=2, sort_keys=True) + "\n")
        print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()
