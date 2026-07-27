from pathlib import Path
import json,sys
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.insertion_elimination_pathway_batch_v1 import FAMILY_BOUNDARY_PATH,FAMILY_INVENTORY_PATH,FAMILY_REGISTRY_PATH,IDENTITY_PATH,INSERTION_ELIMINATION_PATHWAY_SPEC,PRIMARY_PATH,TARGET_PATH
from sft.chemistry.insertion_elimination_pathway_validation_v1 import InsertionEliminationPathwayValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root:Path):
 ids=json.loads((root/IDENTITY_PATH).read_text());snaps=tuple(dict.fromkeys(x["snapshot_path"] for x in ids["rows"]));files=(root/"sft/chemistry/insertion_elimination_pathway_law_v1.py",root/"sft/chemistry/insertion_elimination_pathway_batch_v1.py",root/"sft/chemistry/insertion_elimination_pathway_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"sft/physics/generated_empirical_law.py",root/"tools/build_chemistry_inorg_010_013_identities_v1.py",root/"tools/build_chemistry_inorg_013_primary_correction_v1.py",root/FAMILY_BOUNDARY_PATH,root/FAMILY_REGISTRY_PATH,root/FAMILY_INVENTORY_PATH,root/IDENTITY_PATH,root/TARGET_PATH,root/PRIMARY_PATH,root/"experiments/external_sources/chemistry/inorg_013_withheld_targets_v1.json",*(root/x for x in snaps),root/"claims/SFT-CHEM-INSERTION-ELIMINATION-PATHWAY-013/execution.py");files=tuple(dict.fromkeys(files));h=build_source_manifest(root,files).manifest_hash;v=root/"claims/SFT-CHEM-INSERTION-ELIMINATION-PATHWAY-013/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(INSERTION_ELIMINATION_PATHWAY_SPEC,h),ExternalCommandValidator("sft-chem-insertion-elimination-013-independent-python/1",(sys.executable,str(v)),v.parent,(v,)),files,InsertionEliminationPathwayValidator(root))
