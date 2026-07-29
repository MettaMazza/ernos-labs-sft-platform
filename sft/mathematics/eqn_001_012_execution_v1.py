"""Execution bindings for the complete EQN-001--012 family."""
import json,sys
from pathlib import Path
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.mathematics.eqn_001_012_laws_v1 import SPECS,EquationProgram
from sft.mathematics.eqn_001_012_external_v1 import EquationObservationValidator,REGISTRY,VECTOR
from sft.verification import ClaimExecution
def current_certificate(root,cid):
 row=next(x for x in json.loads((root/"census/claims.json").read_text())["claims"] if x["claim_id"]==cid);matches=[p for p in sorted((root/"claims"/cid).glob("certificate*.json")) if json.loads(p.read_text()).get("engine_receipt_hash")==row["receipt_hash"]]
 if len(matches)!=1:raise ValueError(f"{cid} current certificate count {len(matches)}")
 return matches[0]
def build_execution(root:Path,cid:str,execution_file:Path):
 spec=SPECS[cid];files=[root/"sft/mathematics/generated_law.py",root/"sft/mathematics/eqn_001_012_laws_v1.py",root/"sft/mathematics/eqn_001_012_external_v1.py",root/"sft/mathematics/eqn_001_012_execution_v1.py",root/REGISTRY,root/VECTOR,execution_file]
 for dep in spec.dependencies:files.extend((root/"claims"/dep/"registration.json",current_certificate(root,dep)))
 files=tuple(dict.fromkeys(files));source_hash=build_source_manifest(root,files).manifest_hash;validator=root/"generated/mathematics/eqn_001_012_validator_v1.py";independent=ExternalCommandValidator("sft-mathematics-eqn-001-012-independent-python/1",(sys.executable,str(validator),cid,str(root)),validator.parent,(validator,))
 return ClaimExecution(EquationProgram(spec,source_hash),independent,files,EquationObservationValidator(root,spec))
