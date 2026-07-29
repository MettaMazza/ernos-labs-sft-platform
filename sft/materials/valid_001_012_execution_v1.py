import json,sys
from pathlib import Path
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
from sft.materials.valid_001_012_laws_v1 import REGISTRY_PATH,SPECS,ValidationProgram
from sft.materials.valid_001_012_external_v1 import MaterialsValidationVectorValidator,VECTOR
def cert(root,cid):
 row=next(x for x in json.loads((root/"census/claims.json").read_text())["claims"] if x["claim_id"]==cid);m=[p for p in sorted((root/"claims"/cid).glob("certificate*.json")) if json.loads(p.read_text()).get("engine_receipt_hash")==row["receipt_hash"]]
 if len(m)!=1:raise ValueError(f"{cid} current certificate count {len(m)}")
 return m[0]
def build_execution(root:Path,cid:str,execution_file:Path):
 s=SPECS[cid];files=(root/"sft/materials/valid_001_012_laws_v1.py",root/"sft/materials/valid_001_012_external_v1.py",root/"sft/materials/valid_001_012_execution_v1.py",root/"sft/physics/structural_constants.py",REGISTRY_PATH,root/VECTOR,execution_file);files+=tuple(p for d in s.dependencies for p in (root/"claims"/d/"registration.json",cert(root,d)));files=tuple(dict.fromkeys(files));h=build_source_manifest(root,files).manifest_hash;v=root/"generated/materials/valid_001_012_validator_v1.py";ind=ExternalCommandValidator("sft-materials-valid-001-012-independent-python/1",(sys.executable,str(v),cid,str(root)),v.parent,(v,));return ClaimExecution(ValidationProgram(s,h),ind,files,MaterialsValidationVectorValidator(root,s))
