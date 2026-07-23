from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.foundation.form_grammar import FormGrammarProgram
from sft.verification import ClaimExecution
def build_execution(root:Path):
 f=(root/"sft/foundation/form_grammar.py",root/"claims/SFT-FOUNDATION-FORM-GRAMMAR-001/execution.py");h=build_source_manifest(root,f).manifest_hash;v=root/"claims/SFT-FOUNDATION-FORM-GRAMMAR-001/independent_validator.py";return ClaimExecution(FormGrammarProgram(h),ExternalCommandValidator("sft-form-grammar-independent-python/1",(sys.executable,str(v)),v.parent,(v,)),f)
