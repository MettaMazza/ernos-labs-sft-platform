from pathlib import Path
import json,sys
from sft.chemistry.electrophilic_substitution_batch_v1 import CAPTURE_INVENTORY_PATH,ELECTROPHILIC_SUBSTITUTION_SPEC,FAMILY_BOUNDARY_PATH,FAMILY_INVENTORY_PATH,FAMILY_REGISTRY_PATH,IDENTITY_PATH,PRE_SOURCE_PATH,PRIMARY_PATH,TARGET_PATH
from sft.chemistry.electrophilic_substitution_validation_v1 import ElectrophilicSubstitutionValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def _paths(v):
 if isinstance(v,dict):
  for x in v.values():yield from _paths(x)
 elif isinstance(v,list):
  for x in v:yield from _paths(x)
 elif isinstance(v,str) and not v.startswith("sha256:") and "/" in v and len(v)<512:yield Path(v)
def build_execution(root):
 t=json.loads((root/TARGET_PATH).read_text());refs=tuple(p for p in _paths(t) if (root/p).is_file());fixed=("sft/chemistry/electrophilic_substitution_law_v1.py","sft/chemistry/electrophilic_substitution_batch_v1.py","sft/chemistry/electrophilic_substitution_validation_v1.py","sft/chemistry/nucleophilic_substitution_law_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py","tools/capture_chemistry_org_008_blind_sources_v1.py","tools/build_chemistry_org_008_external_v1.py",FAMILY_BOUNDARY_PATH,FAMILY_REGISTRY_PATH,FAMILY_INVENTORY_PATH,IDENTITY_PATH,CAPTURE_INVENTORY_PATH,PRE_SOURCE_PATH,TARGET_PATH,PRIMARY_PATH,"claims/SFT-CHEM-ELECTROPHILIC-SUBSTITUTION-FAMILY-008/execution.py");files=tuple(dict.fromkeys(root/p for p in (*fixed,*refs)));sh=build_source_manifest(root,files).manifest_hash;ind=root/"claims/SFT-CHEM-ELECTROPHILIC-SUBSTITUTION-FAMILY-008/independent_validator.py"
 return ClaimExecution(GeneratedObservationalChemistryProgram(ELECTROPHILIC_SUBSTITUTION_SPEC,sh),ExternalCommandValidator("sft-chem-electrophilic-substitution-008-independent-python/1",(sys.executable,str(ind)),ind.parent,(ind,)),files,ElectrophilicSubstitutionValidator(root))
