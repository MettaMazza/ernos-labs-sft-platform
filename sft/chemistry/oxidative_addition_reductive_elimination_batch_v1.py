"""Registered INORG-012 law and complete sealed authority surface."""
from __future__ import annotations
import json
from pathlib import Path
from sft.chemistry.generated_law import ChemistryTargetReference,EmpiricalChemistrySpec
from sft.chemistry.oxidative_addition_reductive_elimination_law_v1 import DEPENDENCIES,DIMENSIONS,EXACT_RESULT,OPERATIONAL_WITNESSES
from sft.engine.source import hash_file
ROOT=Path(__file__).resolve().parents[2]
FAMILY_BOUNDARY_PATH="audits/CHEMISTRY_INORG_004_017_FAMILY_BOUNDARY_2026-07-27.json"; FAMILY_BOUNDARY_HASH="sha256:87998e9fa168d82dd80c28abc9910502bfb23da0c26cb6b1ecedfb88142642bc"
FAMILY_REGISTRY_PATH="experiments/external_sources/chemistry/inorg_004_017_family_source_identity_registry_v1.json"; FAMILY_REGISTRY_HASH="sha256:fce17d6e980696c8051f982ce0f4c8364520ea213f68153187253b96ec914bd2"
FAMILY_INVENTORY_PATH="experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/source-inventory-v1.json"; FAMILY_INVENTORY_HASH="sha256:e03724f16e4866b43b5f3b53a6804588a2c86f5405bcda37cfb717e5724bb7c2"
LAW_PATH="sft/chemistry/oxidative_addition_reductive_elimination_law_v1.py"; LAW_HASH="sha256:f6d25298ac89482611fec7ad7700a5ce09abd5521e6297984be54198dd6fc775"
IDENTITY_PATH="experiments/external_sources/chemistry/inorg_012_target_identities_v1.json"; IDENTITY_HASH="sha256:a103ace65a1351b493859a403b0bbb564fdea57d8299b930a5a7a959ed48f06e"
TARGET_PATH="experiments/external_sources/chemistry/inorg_012_withheld_targets_v1.json"; TARGET_HASH="sha256:b6ab8c6bb59de36c53d604c96c3c45630284f33c9554661e1b941ce4d6c38689"
PRIMARY_PATH="experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/inorg-012-primary-records-v1.json"; PRIMARY_HASH="sha256:34c79b8b441a37c81e41a7f39887db53fda71e4a5e1dae4ed3169470c8ac2b1d"
for p,h in ((FAMILY_BOUNDARY_PATH,FAMILY_BOUNDARY_HASH),(FAMILY_REGISTRY_PATH,FAMILY_REGISTRY_HASH),(FAMILY_INVENTORY_PATH,FAMILY_INVENTORY_HASH),(LAW_PATH,LAW_HASH),(IDENTITY_PATH,IDENTITY_HASH),(TARGET_PATH,TARGET_HASH),(PRIMARY_PATH,PRIMARY_HASH)):
 if hash_file(ROOT/p)!=h: raise ValueError(f"INORG-012 registered authority changed: {p}")
_identity=json.loads((ROOT/IDENTITY_PATH).read_text()); _rows=tuple(_identity.get("rows",()))
if _identity.get("complete_registered_target_count")!=5 or _identity.get("target_definitions_examples_values_outcomes_presence_flags_or_payload_hashes_present") is not False or len(_rows)!=5: raise ValueError("INORG-012 value-free target boundary changed")
TARGET_REFERENCES=tuple(ChemistryTargetReference(x["target_id"],f"{x['authority']}::{x['source_id']}::{x['source_record_role']}::{x['custody_class']}",x["registered_identity"],x["snapshot_path"],x["snapshot_sha256"]) for x in _rows)
OXIDATIVE_ADDITION_REDUCTIVE_ELIMINATION_SPEC=EmpiricalChemistrySpec(
 claim_id="SFT-CHEM-OXIDATIVE-ADDITION-REDUCTIVE-ELIMINATION-012",title="Exact oxidative-addition/reductive-elimination inverse law",
 statement="Oxidative addition preserves one or two metal occurrences and two distinct covalently bound carriers while replacing the carrier-carrier bond by two metal-carrier incidences. Exact positive electron transfer is held as two on one metal or one on each of two metals, never as signed oxidation. Reductive elimination is the unique exact inverse that removes those incidences, restores the source bond and preserves every occurrence.",dependencies=DEPENDENCIES,
 generation_rule="Generate the literal product of process carrier, source, product, conservation, transfer, partition, reverse and extension alternatives; decide all 256 forms solely from admitted transition, conservation, covalent-bond and INORG-010/011 dependencies.",
 grammar_boundary="Every finite one- or two-metal exact trace containing one two-carrier source bond, two product incidences, the complete transfer partition and its exact inverse; all five frozen IUPAC oxidative, split, radical-scope and reductive surfaces.",dimensions=DIMENSIONS,exact_result=EXACT_RESULT,
 induction_base="One retained metal and one two-carrier bond force two product incidences and exact transfer distribution two; two retained metals force distribution one and one.",induction_step="Trace composition preserves matching endpoints, every carrier and metal occurrence, transfer orientation and exact inverse without a species exception.",
 exclusions=("no numerical zero negative irrational imaginary signed continuum fitted free or imported parameter","no signed oxidation-state arithmetic formal-charge substitution or observed mechanism selection","no loss duplication or relabeling of metal or transferred carriers","no omission of radical-scope or reverse correspondence surfaces"),operational_witnesses=OPERATIONAL_WITNESSES,
 experiment_id="SFT-EXP-CHEM-OXIDATIVE-ADDITION-REDUCTIVE-ELIMINATION-012",expected_observation_label="complete-oxidative-addition-and-reductive-elimination-vector",target_rows=TARGET_REFERENCES,observation_registry_path=TARGET_PATH,
 falsification_condition="The claim fails if either carrier or any metal occurrence is lost or duplicated; if the source bond is not replaced by exactly two incidences; if the exact transfer partition differs from two or one-plus-one; if signed oxidation arithmetic enters proof; if reductive elimination is not the exact inverse; if any of five IUPAC surfaces is removed; or if outcomes open before prediction sealing.")
OXIDATIVE_ADDITION_REDUCTIVE_ELIMINATION_SPEC.validate()
__all__=("FAMILY_BOUNDARY_PATH","FAMILY_INVENTORY_PATH","FAMILY_REGISTRY_PATH","IDENTITY_HASH","IDENTITY_PATH","OXIDATIVE_ADDITION_REDUCTIVE_ELIMINATION_SPEC","PRIMARY_HASH","PRIMARY_PATH","TARGET_HASH","TARGET_PATH","TARGET_REFERENCES")
