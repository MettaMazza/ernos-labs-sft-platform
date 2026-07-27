"""Official execution binding for SFT-CHEM-CONFORMER-POPULATION-ORDERING-006."""
from pathlib import Path
import json,sys
from sft.chemistry.conformer_population_ordering_batch_v1 import (
 CONFORMER_POPULATION_ORDERING_SPEC,FAMILY_BOUNDARY_PATH,FAMILY_INVENTORY_PATH,FAMILY_REGISTRY_PATH,
 IDENTITY_PATH,PRE_SOURCE_PATH,PRIMARY_PATH,TARGET_PATH)
from sft.chemistry.conformer_population_ordering_validation_v1 import ConformerPopulationOrderingValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def _paths(value):
 if isinstance(value,dict):
  for item in value.values(): yield from _paths(item)
 elif isinstance(value,list):
  for item in value: yield from _paths(item)
 elif isinstance(value,str) and not value.startswith("sha256:") and "/" in value and len(value) < 512:
  path=Path(value)
  if not path.is_absolute(): yield path
def build_execution(root:Path)->ClaimExecution:
 targets=json.loads((root/TARGET_PATH).read_text()); referenced=tuple(path for path in _paths(targets) if (root/path).is_file())
 fixed=(
  "sft/chemistry/conformer_population_ordering_law_v1.py","sft/chemistry/conformer_population_ordering_batch_v1.py",
  "sft/chemistry/conformer_population_ordering_validation_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py",
  "sft/physics/generated_empirical_law.py","tools/build_chemistry_org_006_complete_external_v1.py","tools/build_chemistry_org_006_complete_external_v2.py",
  "tools/capture_chemistry_org_006_blind_sources_v1.py","tools/capture_chemistry_org_006_value_blind_sources_v2.py",
  "tools/capture_chemistry_org_006_acs_figshare_v3.py","tools/capture_chemistry_org_006_acs_figshare_file_v4.py","tools/capture_chemistry_org_006_core_direct_v5.py",
  FAMILY_BOUNDARY_PATH,FAMILY_REGISTRY_PATH,FAMILY_INVENTORY_PATH,IDENTITY_PATH,TARGET_PATH,PRIMARY_PATH,PRE_SOURCE_PATH,
  "experiments/sealed_predictions/chemistry_org_006_conformer_population_ordering_pre_source.json",
  "experiments/sealed_predictions/chemistry_org_006_conformer_population_ordering_pre_source_v2.json",
  "experiments/sealed_predictions/chemistry_org_006_conformer_population_ordering_pre_source_v3.json",
  "experiments/sealed_predictions/chemistry_org_006_conformer_population_ordering_pre_source_v4.json",
  "experiments/external_sources/chemistry/org_006_target_identities_v1.json","experiments/external_sources/chemistry/org_006_target_identity_addendum_v2.json",
  "experiments/external_sources/chemistry/org_006_target_identity_addendum_v3.json","experiments/external_sources/chemistry/org_006_target_identity_addendum_v4.json",
  "experiments/external_sources/chemistry/org_006_target_identity_addendum_v5.json","experiments/external_sources/chemistry/org_006_blind_source_identity_addendum_v1.json",
  "experiments/external_sources/chemistry/org_006_value_blind_source_identity_addendum_v2.json","experiments/external_sources/chemistry/org_006_acs_figshare_source_identity_addendum_v3.json",
  "experiments/external_sources/chemistry/org_006_acs_figshare_file_source_identity_addendum_v4.json","experiments/external_sources/chemistry/org_006_core_direct_source_identity_addendum_v5.json",
  "claims/SFT-CHEM-CONFORMER-POPULATION-ORDERING-006/execution.py",
 )
 files=tuple(dict.fromkeys(root/path for path in (*fixed,*referenced))); source_hash=build_source_manifest(root,files).manifest_hash
 independent=root/"claims/SFT-CHEM-CONFORMER-POPULATION-ORDERING-006/independent_validator.py"
 return ClaimExecution(GeneratedObservationalChemistryProgram(CONFORMER_POPULATION_ORDERING_SPEC,source_hash),
  ExternalCommandValidator("sft-chem-conformer-population-ordering-006-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),
  files,ConformerPopulationOrderingValidator(root))
