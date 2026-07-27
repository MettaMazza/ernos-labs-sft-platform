"""Registered ORG-008 acceptor-driven aromatic substitution and complete external surface."""
from __future__ import annotations
import json
from pathlib import Path
from sft.chemistry.electrophilic_substitution_law_v1 import DEPENDENCIES,DIMENSIONS,EXACT_RESULT,OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import ChemistryTargetReference,EmpiricalChemistrySpec
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file
ROOT=Path(__file__).resolve().parents[2]
FAMILY_BOUNDARY_PATH="audits/CHEMISTRY_ORG_001_016_FAMILY_BOUNDARY_2026-07-27.json";FAMILY_BOUNDARY_HASH="sha256:00ed97e8dec313d65d2b9f6af595e3e3787a99aa60b86814f1a00f318abf011e"
FAMILY_REGISTRY_PATH="experiments/external_sources/chemistry/org_001_016_family_source_identity_registry_v1.json";FAMILY_REGISTRY_HASH="sha256:12c6822a695eb7135081ef8d044a3136c2fee2b0d486c9164b1f1166ef087381"
FAMILY_INVENTORY_PATH="experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/source-inventory-v1.json";FAMILY_INVENTORY_HASH="sha256:8b35e1f37dbf80713c47404d946a320da8d7011deaa5dbee7fe8393b58793cee"
LAW_PATH="sft/chemistry/electrophilic_substitution_law_v1.py";LAW_HASH="sha256:233e2ce9274ef61b6d1316de93d91728c4b659fe1e33a930cff783b44c1ff30f"
PRE_SOURCE_PATH="experiments/sealed_predictions/chemistry_org_008_electrophilic_substitution_pre_source_v1.json";PRE_SOURCE_FILE_HASH="sha256:538e68a998ab24959f2e53065ae593adddb9878c008309dccac26d3cec88015e";PRE_SOURCE_PAYLOAD_HASH="sha256:6ee04e4bdf6f4446c43e7ddcf867db70108626b3a15a9fcea6d36dff07ee43c3"
IDENTITY_PATH="experiments/external_sources/chemistry/org_008_target_identities_v1.json";IDENTITY_HASH="sha256:d718044a43d35b2c2a01a419359cb1316053e6ec684d3dd10d4685565082b453"
CAPTURE_INVENTORY_PATH="experiments/external_sources/chemistry/snapshots/org-008-nature-blind-v1/source-inventory-v1.json";CAPTURE_INVENTORY_HASH="sha256:15297b5a43ce7b0b1fb385ab381a091ffc9078fc1c4d6876ab812fa7724230b9"
TARGET_PATH="experiments/external_sources/chemistry/org_008_complete_targets_v1.json";TARGET_HASH="sha256:41d6d0aed51dec5720ea0553351c9ec72e06e22c037bc0025ca012398787d08d"
PRIMARY_PATH="experiments/external_sources/chemistry/snapshots/org-008-nature-blind-v1/org-008-primary-record-v1.json";PRIMARY_HASH="sha256:905a31d426ef4236d216e8d74cc3e3f81b110967cae47d50e8a5e1dab961aa7f"
for path,expected in ((FAMILY_BOUNDARY_PATH,FAMILY_BOUNDARY_HASH),(FAMILY_REGISTRY_PATH,FAMILY_REGISTRY_HASH),(FAMILY_INVENTORY_PATH,FAMILY_INVENTORY_HASH),(LAW_PATH,LAW_HASH),(PRE_SOURCE_PATH,PRE_SOURCE_FILE_HASH),(IDENTITY_PATH,IDENTITY_HASH),(CAPTURE_INVENTORY_PATH,CAPTURE_INVENTORY_HASH),(TARGET_PATH,TARGET_HASH),(PRIMARY_PATH,PRIMARY_HASH)):
 if hash_file(ROOT/path)!=expected:raise ValueError(f"ORG-008 authority changed: {path}")
_p=json.loads((ROOT/PRE_SOURCE_PATH).read_text());_c=_p.pop("sealed_payload_hash",None)
if _c!=PRE_SOURCE_PAYLOAD_HASH or sha256_identity(_p)!=PRE_SOURCE_PAYLOAD_HASH or _p.get("exact_supplementary_PDF_pages_product_structures_values_controls_and_mechanistic_details_opened_before_this_seal") is not False:raise ValueError("ORG-008 prediction seal changed")
_i=tuple(json.loads((ROOT/IDENTITY_PATH).read_text())["rows"]);_t=tuple(json.loads((ROOT/TARGET_PATH).read_text())["rows"])
if len(_i)!=4 or len(_t)!=4:raise ValueError("ORG-008 target boundary changed")
TARGET_REFERENCES=tuple(ChemistryTargetReference(a["target_id"],"::".join((a["authority"],a["source_id"],a["source_record_role"],a["custody_class"])),a["registered_identity"],b["opened_snapshot_path"],b["opened_snapshot_sha256"]) for a,b in zip(_i,_t))
ELECTROPHILIC_SUBSTITUTION_SPEC=EmpiricalChemistrySpec(
 claim_id="SFT-CHEM-ELECTROPHILIC-SUBSTITUTION-FAMILY-008",title="Exact acceptor-driven aromatic substitution family law",
 statement="For every complete aromatic exchange carrier, the entering structural-EmptyOne acceptor receives both occurrences of one aromatic donor pair. The entering bond forms, the leaving bond closes, and the leaving pair restores the opened aromatic incidence. Every atom and held electron occurrence is conserved through direct exchange or addition followed by recurrence restoration.",
 dependencies=DEPENDENCIES,generation_rule="Generate the literal product of carrier, acceptor, donor, change, path, recurrence, observation and extension alternatives; decide all 256 forms solely from admitted Fold, aromatic and ORG-007 support laws.",
 grammar_boundary="Every positive finite aromatic carrier with complete donor, recurrence, entering-acceptor and leaving supports; all one- and two-transition paths; every source record; and the complete four-target, 452-page external surface.",dimensions=DIMENSIONS,exact_result=EXACT_RESULT,
 induction_base="One five-occurrence aromatic source forces transfer of the complete donor pair to the entering acceptor and restoration of the opened aromatic incidence by the complete leaving pair through exactly one or two transitions.",
 induction_step="Append one fresh aromatic occurrence and pair outside the local exchange support to every path state; every prior occurrence, state, transition and pair allocation remains unchanged without an extra rule.",
 exclusions=("no native numerical zero; structural acceptor absence is EmptyOne","no negative irrational imaginary continuum fitted free random or imported native parameter","no conventional electrophilic mechanism rate energy solvent substrate or target used to generate the survivor","three development-observed records are disclosed and never relabelled blind","all 452 PDF pages, 25 optimization rows, favorable, zero-yield, adverse, alternative and unresolved records remain retained","external signed and decimal inscriptions remain downstream evidence only"),
 operational_witnesses=OPERATIONAL_WITNESSES,experiment_id="SFT-EXP-CHEM-ELECTROPHILIC-SUBSTITUTION-FAMILY-008",expected_observation_label="complete-acceptor-donor-aromatic-exchange-path-and-postseal-supplementary-vector",target_rows=TARGET_REFERENCES,observation_registry_path=TARGET_PATH,
 falsification_condition="The claim fails if any carrier, pair, atom, bond change, recurrence state or path is omitted; if cleavage-first or a nonunique 256-form census passes; if any of four sources or 452 supplementary pages is erased; if the IUPAC donor/acceptor relations fail; if the complete PDF lacks EAS-like donor/acceptor coupling, dearomatized support and rearomatization; or if any of 25 optimization rows, including 14 displayed zero-yield rows and mechanism controls, is omitted."
);ELECTROPHILIC_SUBSTITUTION_SPEC.validate()
__all__=("CAPTURE_INVENTORY_PATH","ELECTROPHILIC_SUBSTITUTION_SPEC","FAMILY_BOUNDARY_PATH","FAMILY_INVENTORY_PATH","FAMILY_REGISTRY_PATH","IDENTITY_HASH","IDENTITY_PATH","PRE_SOURCE_PATH","PRIMARY_HASH","PRIMARY_PATH","TARGET_HASH","TARGET_PATH","TARGET_REFERENCES")
