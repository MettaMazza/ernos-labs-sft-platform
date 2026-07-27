"""Official execution binding for SFT-MAT-CRYST-QUASICRYSTAL-INFLATION-002."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.materials.generated_law import GeneratedEmpiricalMaterialsProgram
from sft.materials.successor_evidence import BlindSuccessorMaterialsValidator, SPECS
from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
 spec=next(x for x in SPECS if x.claim_id=='SFT-MAT-CRYST-QUASICRYSTAL-INFLATION-002')
 source_files=tuple(root/x for x in (('sft/materials/successor_obligations.py', 'sft/materials/successor_structural_counts.py', 'sft/materials/successor_derivation.py', 'sft/materials/successor_evidence.py', 'claims/SFT-MAT-CRYST-QUASICRYSTAL-INFLATION-002/execution.py', 'sft/materials/generated_law.py', 'sft/physics/generated_empirical_law.py', 'sft/claim_evidence/fold_language.py', 'sft/claim_evidence/custody.py', 'sft/claim_evidence/hostile.py', 'sft/engine/isolation.py', 'sft/engine/empirical.py')))
 source_hash=build_source_manifest(root,source_files).manifest_hash
 validator=root/'claims/SFT-MAT-CRYST-QUASICRYSTAL-INFLATION-002/independent_validator.py'
 return ClaimExecution(GeneratedEmpiricalMaterialsProgram(spec,source_hash),ExternalCommandValidator('sft-mat-cryst-quasicrystal-inflation-002-independent-python/1',(sys.executable,str(validator)),validator.parent,(validator,)),source_files,BlindSuccessorMaterialsValidator(root,spec))
