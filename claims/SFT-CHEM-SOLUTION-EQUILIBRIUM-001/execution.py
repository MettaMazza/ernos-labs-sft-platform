"""Official execution binding for SFT-CHEM-SOLUTION-EQUILIBRIUM-001."""
from dataclasses import replace
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_law import GeneratedEmpiricalChemistryProgram
from sft.chemistry.generated_multi_source_law import BlindMultiSourceAuthorityValidator
from sft.chemistry.thermochemistry_batch_1 import THERMOCHEMISTRY_BATCH_1_SPECS
from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
 raw_spec=next(x for x in THERMOCHEMISTRY_BATCH_1_SPECS if x.claim_id=='SFT-CHEM-SOLUTION-EQUILIBRIUM-001')
 spec=replace(raw_spec,dependencies=tuple(dict.fromkeys(raw_spec.dependencies)))
 source_files=(root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_multi_source_law.py",root/"sft/chemistry/thermochemistry_derivation.py",root/"sft/chemistry/thermochemistry_batch_1.py",root/"experiments/sealed_predictions/chemistry_thermochemistry_batch_1_pre_source.json",root/"claims/SFT-CHEM-SOLUTION-EQUILIBRIUM-001/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/engine/fold_language.py",root/"sft/engine/custody.py",root/"sft/engine/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py")
 source_hash=build_source_manifest(root,source_files).manifest_hash
 validator=root/"claims/SFT-CHEM-SOLUTION-EQUILIBRIUM-001/independent_validator.py"
 return ClaimExecution(program=GeneratedEmpiricalChemistryProgram(spec,source_hash),independent_validator=ExternalCommandValidator('sft-chem-solution-equilibrium-001'+"-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),source_files=source_files,empirical_validator=BlindMultiSourceAuthorityValidator(root,spec))
