import json,sys
from pathlib import Path
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.materials.mech_001_014_external_v1 import MANIFEST,REGISTRY,VECTOR,MechExternalValidator
from sft.materials.mech_001_014_laws_v1 import MechProgram,SPECS
from sft.verification import ClaimExecution
def cert(root,cid):
 row=next(x for x in json.loads((root/"census/claims.json").read_text())["claims"] if x["claim_id"]==cid);m=[p for p in (root/"claims"/cid).glob("certificate*.json") if json.loads(p.read_text()).get("engine_receipt_hash")==row["receipt_hash"]]
 if len(m)!=1:raise ValueError("certificate count")
 return m[0]
def build_execution(root,claim_id,execution_file):
 spec=SPECS[claim_id];man=json.loads((root/MANIFEST).read_text());vec=json.loads((root/VECTOR).read_text());fixed=(root/"sft/materials/mech_001_014_laws_v1.py",root/"sft/materials/mech_001_014_external_v1.py",root/"sft/materials/mech_001_014_execution_v1.py",root/"sft/physics/structural_constants.py",root/REGISTRY,root/MANIFEST,root/VECTOR,execution_file);sources=tuple(root/x["snapshot_path"] for x in man["documents"]);texts=tuple(root/x["text_path"] for x in vec["pdf_text_reconstructions"]);deps=tuple(p for d in spec.dependencies for p in (root/"claims"/d/"registration.json",cert(root,d)));files=tuple(dict.fromkeys(fixed+sources+texts+deps));sh=build_source_manifest(root,files).manifest_hash;val=root/"generated/materials/mech_001_014_validator_v1.py";ind=ExternalCommandValidator("sft-materials-mech-001-014-independent-python/1",(sys.executable,str(val),claim_id,str(root)),val.parent,(val,));return ClaimExecution(MechProgram(spec,sh),ind,files,MechExternalValidator(root,spec))
