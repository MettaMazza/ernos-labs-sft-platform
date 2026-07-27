from pathlib import Path
import json,sys
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.metal_cluster_bonding_batch_v1 import FAMILY_BOUNDARY_PATH,FAMILY_INVENTORY_PATH,FAMILY_REGISTRY_PATH,IDENTITY_PATH,METAL_CLUSTER_BONDING_SPEC,PRIMARY_PATH,TARGET_PATH
from sft.chemistry.metal_cluster_bonding_validation_v1 import MetalClusterBondingValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root:Path):
 ids=json.loads((root/IDENTITY_PATH).read_text());snaps=tuple(dict.fromkeys(x["snapshot_path"] for x in ids["rows"]));files=(root/"sft/chemistry/metal_cluster_bonding_law_v1.py",root/"sft/chemistry/metal_cluster_bonding_batch_v1.py",root/"sft/chemistry/metal_cluster_bonding_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"sft/physics/generated_empirical_law.py",root/"tools/build_chemistry_inorg_014_017_identities_v1.py",root/"tools/build_chemistry_inorg_014_017_primary_v1.py",root/FAMILY_BOUNDARY_PATH,root/FAMILY_REGISTRY_PATH,root/FAMILY_INVENTORY_PATH,root/IDENTITY_PATH,root/TARGET_PATH,root/PRIMARY_PATH,*(root/x for x in snaps),root/"claims/SFT-CHEM-METAL-CLUSTER-BONDING-014/execution.py");files=tuple(dict.fromkeys(files));h=build_source_manifest(root,files).manifest_hash;v=root/"claims/SFT-CHEM-METAL-CLUSTER-BONDING-014/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(METAL_CLUSTER_BONDING_SPEC,h),ExternalCommandValidator("sft-chem-metal-cluster-014-independent-python/1",(sys.executable,str(v)),v.parent,(v,)),files,MetalClusterBondingValidator(root))
