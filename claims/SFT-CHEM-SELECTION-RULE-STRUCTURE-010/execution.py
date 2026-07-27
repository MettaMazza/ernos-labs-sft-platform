from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.selection_rule_batch_v1 import SELECTION_RULE_SPEC
from sft.chemistry.selection_rule_validation_v1 import SelectionRuleValidator
from sft.verification import ClaimExecution
def build_execution(root:Path):
 s=SELECTION_RULE_SPEC; files=(root/"sft/chemistry/selection_rule_law_v1.py",root/"sft/chemistry/selection_rule_batch_v1.py",root/"sft/chemistry/selection_rule_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"claims/SFT-CHEM-SELECTION-RULE-STRUCTURE-010/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py"); source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/SFT-CHEM-SELECTION-RULE-STRUCTURE-010/independent_validator.py"; return ClaimExecution(GeneratedObservationalChemistryProgram(s,source_hash),ExternalCommandValidator("sft-chem-selection-rule-structure-010-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,SelectionRuleValidator(root))
