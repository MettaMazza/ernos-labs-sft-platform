"""Registered ORG-015 reversible protecting-group law."""
from __future__ import annotations
from pathlib import Path
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.protecting_group_reversible_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file

ROOT=Path(__file__).resolve().parents[2]; CLAIM_ID="SFT-CHEM-PROTECTING-GROUP-REVERSIBLE-STATE-015"; OBLIGATION_ID="SFT-CHEM-OBL-ORG-015"
IDENTITY_PATH="experiments/external_sources/chemistry/org_015_target_identities_v1.json"
PRESEAL_PATH="experiments/sealed_predictions/chemistry_org_015_protecting_group_pre_source_v1.json"
PROTECT_PATH="experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/iupac-09560.json"
DEPROTECT_PATH="experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/iupac-09466.json"
AUTHORITIES=(
 ("audits/CHEMISTRY_ORG_001_016_FAMILY_BOUNDARY_2026-07-27.json","sha256:ccbc91e9873a84f31b50670c9a8f063ee6a6096d3dd216b5e7c3bf86521681b2"),
 ("experiments/external_sources/chemistry/org_001_016_family_source_identity_registry_v1.json","sha256:12c6822a695eb7135081ef8d044a3136c2fee2b0d486c9164b1f1166ef087381"),
 ("sft/chemistry/protecting_group_reversible_law_v1.py","sha256:b1564ea6a5f54845c6a9808ffc778995dee439c535926bdf10057a676b15be01"),
 (IDENTITY_PATH,"sha256:adc812bdfd62b3cefb907e8f027fbfc97e10f38be1f77d0685a9c4d9e6b90111"),
 (PRESEAL_PATH,"sha256:de84f2eb598466aebf3690b182551bd49b86256d8ddfb41a1bb512b406e70fcd"),
 (PROTECT_PATH,"sha256:b2fad3b9d173988485096e13f5385b4f19e0b1be2bae0ed8c4b89e6e922f2712"),
 (DEPROTECT_PATH,"sha256:943eafca8aae28d1169771bb9db93bf1c2182b8a05130fadfb0d4bf079158c55"),
)
for p,h in AUTHORITIES:
 if hash_file(ROOT/p)!=h: raise ValueError(f"ORG-015 authority changed: {p}")
TARGET_REFERENCES=(
 ChemistryTargetReference("SFT-CHEM-ORG-015-PROTECT-TEMPORARY","IUPAC-09560","temporary use",PROTECT_PATH,AUTHORITIES[5][1]),
 ChemistryTargetReference("SFT-CHEM-ORG-015-PROTECT-TRANSFORM","IUPAC-09560","reactive group transformed",PROTECT_PATH,AUTHORITIES[5][1]),
 ChemistryTargetReference("SFT-CHEM-ORG-015-PROTECT-CHALLENGE","IUPAC-09560","does not react under declared conditions",PROTECT_PATH,AUTHORITIES[5][1]),
 ChemistryTargetReference("SFT-CHEM-ORG-015-DEPROTECT-REMOVAL","IUPAC-09466","protecting group removal",DEPROTECT_PATH,AUTHORITIES[6][1]),
 ChemistryTargetReference("SFT-CHEM-ORG-015-DEPROTECT-SCOPE","IUPAC-09466","narrow polymeric-resist scope retained",DEPROTECT_PATH,AUTHORITIES[6][1]),
)
PROTECTING_GROUP_SPEC=EmpiricalChemistrySpec(
 claim_id=CLAIM_ID,title="Fold protecting-group reversible state and exact restoration",
 statement="A complete retained carrier undergoes a temporary held functional transform, remains unchanged through a declared challenge and returns to the exact source function while protector absence is structural EmptyOne.",
 dependencies=DEPENDENCIES,generation_rule="Generate the literal product of eight registered binary protection-cycle decisions.",
 grammar_boundary="Eight dimensions exhaust carrier, target, transform, protector, challenge, restore, absence and extension.",dimensions=DIMENSIONS,exact_result=EXACT_RESULT,
 induction_base="One complete carrier supplies a transform/challenge/exact-restoration cycle.",induction_step="One fresh carrier occurrence preserves the entire prior cycle without a new rule.",
 exclusions=("no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter","no group name external example or source phrase selects the survivor","the narrow source scope is preserved and never inflated into the formal exact-restoration result"),
 operational_witnesses=OPERATIONAL_WITNESSES,experiment_id="SFT-EXP-CHEM-PROTECTING-GROUP-REVERSIBLE-STATE-015",expected_observation_label="complete-protection-deprotection-observable-and-preservation-vector",target_rows=TARGET_REFERENCES,observation_registry_path=IDENTITY_PATH,
 falsification_condition="The claim fails if more than one form survives; carrier, target, protector, protected interval or exact endpoint is lost; endpoint absence is numerical; either complete IUPAC record or its narrow scope is omitted; or an external phrase selects the native law.",
)
PROTECTING_GROUP_SPEC.validate(); COMPLETENESS_CERTIFICATE=sha256_identity((CLAIM_ID,tuple(x.target_id for x in TARGET_REFERENCES),EXACT_RESULT))
__all__=("AUTHORITIES","CLAIM_ID","COMPLETENESS_CERTIFICATE","DEPROTECT_PATH","IDENTITY_PATH","OBLIGATION_ID","PRESEAL_PATH","PROTECTING_GROUP_SPEC","PROTECT_PATH","TARGET_REFERENCES")
