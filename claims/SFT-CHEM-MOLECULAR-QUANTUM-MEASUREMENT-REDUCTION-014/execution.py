from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.molecular_measurement_batch_v1 import MOLECULAR_MEASUREMENT_SPEC
from sft.chemistry.molecular_measurement_validation_v1 import MolecularMeasurementValidator
from sft.verification import ClaimExecution
def build_execution(root:Path):
 s=MOLECULAR_MEASUREMENT_SPEC;files=(root/"sft/chemistry/molecular_measurement_law_v1.py",root/"sft/chemistry/molecular_measurement_batch_v1.py",root/"sft/chemistry/molecular_measurement_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"claims/SFT-CHEM-MOLECULAR-QUANTUM-MEASUREMENT-REDUCTION-014/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py");h=build_source_manifest(root,files).manifest_hash;v=root/"claims/SFT-CHEM-MOLECULAR-QUANTUM-MEASUREMENT-REDUCTION-014/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(s,h),ExternalCommandValidator("sft-chem-molecular-quantum-measurement-reduction-014-independent-python/1",(sys.executable,str(v)),v.parent,(v,)),files,MolecularMeasurementValidator(root))
