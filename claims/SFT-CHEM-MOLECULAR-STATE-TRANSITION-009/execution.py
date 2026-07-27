from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.state_transition_batch_v1 import STATE_TRANSITION_SPEC
from sft.chemistry.state_transition_validation_v1 import StateTransitionValidator
from sft.verification import ClaimExecution
def build_execution(root:Path):
 s=STATE_TRANSITION_SPEC; files=(root/"sft/chemistry/state_transition_law_v1.py",root/"sft/chemistry/state_transition_batch_v1.py",root/"sft/chemistry/state_transition_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"claims/SFT-CHEM-MOLECULAR-STATE-TRANSITION-009/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py"); source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/SFT-CHEM-MOLECULAR-STATE-TRANSITION-009/independent_validator.py"; return ClaimExecution(GeneratedObservationalChemistryProgram(s,source_hash),ExternalCommandValidator("sft-chem-molecular-state-transition-009-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,StateTransitionValidator(root))
