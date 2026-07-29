import sys
from sft.chemistry.polymer_chemistry_batch_v1 import AUTHORITIES, SPEC_BY_NUMBER
from sft.chemistry.polymer_chemistry_validation_v1 import PolymerChemistryValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
CLAIM_SPEC=SPEC_BY_NUMBER["013"]
def build_execution(root):
 fixed=("sft/chemistry/polymer_chemistry_laws_v1.py","sft/chemistry/polymer_chemistry_batch_v1.py","sft/chemistry/polymer_chemistry_validation_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),"claims/SFT-CHEM-POLYMER-MATERIALS-HANDOFF-013/execution.py");files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/SFT-CHEM-POLYMER-MATERIALS-HANDOFF-013/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(CLAIM_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-poly-013-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),files,PolymerChemistryValidator(root,CLAIM_SPEC))
