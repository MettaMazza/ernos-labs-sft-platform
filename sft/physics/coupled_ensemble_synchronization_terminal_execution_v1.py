"""Official frozen-engine binding for coupled-ensemble synchronization."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.coupled_ensemble_synchronization_terminal_law_v1 import CLAIM_ID, CoupledEnsembleSynchronizationProgram
from sft.physics.coupled_ensemble_synchronization_terminal_validation_v1 import CoupledEnsembleSynchronizationValidator
from sft.verification import ClaimExecution

def build_coupled_ensemble_synchronization_execution(root:Path,execution_file:Path)->ClaimExecution:
 source_files=(root/"sft/foundation/half_one.py",root/"sft/physics/coupled_ensemble_synchronization_terminal_law_v1.py",root/"sft/physics/coupled_ensemble_synchronization_terminal_validation_v1.py",root/"sft/physics/coupled_ensemble_synchronization_terminal_execution_v1.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/canonical.py",root/"sft/engine/exact.py",root/"sft/engine/empirical.py",root/"sft/engine/isolation.py",execution_file)
 source_hash=build_source_manifest(root,source_files).manifest_hash; validator=root/"generated/physics/coupled_ensemble_synchronization_terminal_validator_v1.py"
 return ClaimExecution(CoupledEnsembleSynchronizationProgram(source_hash),ExternalCommandValidator("sft-physics-coupled-ensemble-synchronization-independent-python/1",(sys.executable,str(validator),CLAIM_ID),validator.parent,(validator,)),source_files,CoupledEnsembleSynchronizationValidator(root))

__all__=("build_coupled_ensemble_synchronization_execution",)
