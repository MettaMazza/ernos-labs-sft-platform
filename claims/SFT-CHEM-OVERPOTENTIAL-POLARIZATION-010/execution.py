import sys
from sft.chemistry.echem_polarization_batch_v1 import AUTHORITIES, POLARIZATION_SPEC as CLAIM_SPEC
from sft.chemistry.echem_polarization_validation_v1 import OverpotentialPolarizationValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root):
 fixed=("sft/chemistry/echem_polarization_batch_v1.py","sft/chemistry/echem_polarization_validation_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),"claims/SFT-CHEM-OVERPOTENTIAL-POLARIZATION-010/execution.py");files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/SFT-CHEM-OVERPOTENTIAL-POLARIZATION-010/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(CLAIM_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-echem-010-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),files,OverpotentialPolarizationValidator(root))
