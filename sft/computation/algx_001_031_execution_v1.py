"""Execution bindings for the complete ALGX-001 through ALGX-031 family."""
import json,sys
from pathlib import Path
from sft.computation.algx_001_031_external_v1 import AlgorithmObservationValidator,REGISTRY,VECTOR
from sft.computation.algx_001_031_laws_v1 import AlgorithmExtensionProgram,SPECS
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def current_certificate(root,claim_id):
 row=next(x for x in json.loads((root/"census/claims.json").read_text())["claims"] if x["claim_id"]==claim_id);matches=[p for p in sorted((root/"claims"/claim_id).glob("certificate*.json")) if json.loads(p.read_text()).get("engine_receipt_hash")==row["receipt_hash"]]
 if len(matches)!=1:raise ValueError(f"{claim_id} current certificate count {len(matches)}")
 return matches[0]
def build_execution(root:Path,claim_id:str,execution_file:Path):
 spec=SPECS[claim_id];source_files=[root/"sft/computation/generated_law.py",root/"sft/computation/complete_field_observation_v1.py",root/"sft/computation/algx_001_031_laws_v1.py",root/"sft/computation/algx_001_031_external_v1.py",root/"sft/computation/algx_001_031_execution_v1.py",root/REGISTRY,root/VECTOR,execution_file]
 for dependency in spec.dependencies:source_files.extend((root/"claims"/dependency/"registration.json",current_certificate(root,dependency)))
 source_files=tuple(dict.fromkeys(source_files));source_hash=build_source_manifest(root,source_files).manifest_hash;validator=root/"generated/computation/algx_001_031_validator_v1.py";independent=ExternalCommandValidator("sft-classical-computation-algx-001-031-independent-python/1",(sys.executable,str(validator),claim_id,str(root)),validator.parent,(validator,));return ClaimExecution(AlgorithmExtensionProgram(spec,source_hash),independent,source_files,AlgorithmObservationValidator(root,spec))
