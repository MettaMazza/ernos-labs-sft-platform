from pathlib import Path
import sys
from sft.social.exact_return_laws_v1 import EMPIRICAL_ID,SPECS,Program
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root,cid,execution_file):
 s=SPECS[cid];files=(root/"sft/social/exact_return_laws_v1.py",root/"sft/social/exact_return_execution_v1.py",root/"sft/physics/structural_constants.py",execution_file);emp=None
 if cid==EMPIRICAL_ID:
  from sft.social.exact_return_external_v1 import BlindSocialExternalValidator
  files+=(root/"sft/social/exact_return_external_v1.py",);emp=BlindSocialExternalValidator(root)
 files+=tuple(p for d in s.dependencies for p in (root/"claims"/d/"registration.json",root/"claims"/d/"certificate.json"));files=tuple(dict.fromkeys(files));h=build_source_manifest(root,files).manifest_hash;v=root/"generated/social/exact_return_validator_v1.py";ind=ExternalCommandValidator("sft-social-exact-independent-python/1",(sys.executable,str(v),cid,str(root)),v.parent,(v,));return ClaimExecution(Program(s,h),ind,files,emp)
