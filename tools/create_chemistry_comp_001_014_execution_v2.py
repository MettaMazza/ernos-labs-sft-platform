#!/usr/bin/env python3
"""Create versioned execution sources after the preserved v1 interface halt."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> None:
    from sft.chemistry.computational_chemistry_batch_v1 import SPECS_BY_NUMBER
    for number, claim in SPECS_BY_NUMBER.items():
        path = ROOT / "claims" / claim.claim_id / "execution_v2.py"
        if path.exists():
            raise SystemExit(f"refusing to overwrite {path.relative_to(ROOT)}")
        path.write_text(f'''import sys
from sft.chemistry.computational_chemistry_batch_v1 import AUTHORITIES,SOURCE_ARTIFACTS,SPECS_BY_NUMBER
from sft.chemistry.computational_chemistry_validation_v2 import ComputationalChemistryValidatorV2
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
CLAIM_SPEC=SPECS_BY_NUMBER[{number!r}]
def build_execution(root):
 fixed=("sft/chemistry/computational_chemistry_batch_v1.py","sft/chemistry/computational_chemistry_validation_v1.py","sft/chemistry/computational_chemistry_validation_v2.py","sft/chemistry/computational_chemistry_laws_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),*(p for p,_ in SOURCE_ARTIFACTS),"claims/{claim.claim_id}/execution_v2.py");files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/{claim.claim_id}/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(CLAIM_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-comp-{number}-independent-python/2",(sys.executable,str(independent)),independent.parent,(independent,)),files,ComputationalChemistryValidatorV2(root,CLAIM_SPEC))
''')
    print("created fourteen preserved-retry COMP execution_v2 sources")


if __name__ == "__main__":
    main()
