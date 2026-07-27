from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.state_symmetry_batch_v1 import STATE_SYMMETRY_SPEC
from sft.chemistry.state_symmetry_validation_v1 import StateSymmetryValidator
from sft.verification import ClaimExecution
def build_execution(root:Path):
 s=STATE_SYMMETRY_SPEC; files=(root/"sft/chemistry/state_symmetry_law_v1.py",root/"sft/chemistry/state_symmetry_batch_v1.py",root/"sft/chemistry/state_symmetry_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"claims/SFT-CHEM-STATE-SYMMETRY-DEGENERACY-005/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py"); source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/SFT-CHEM-STATE-SYMMETRY-DEGENERACY-005/independent_validator.py"; return ClaimExecution(GeneratedObservationalChemistryProgram(s,source_hash),ExternalCommandValidator("sft-chem-state-symmetry-degeneracy-005-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,StateSymmetryValidator(root))
