"""Registered INORG-002 law and complete IUPAC/NIST coordination-count surface."""
from __future__ import annotations
import json
from pathlib import Path
from sft.chemistry.coordination_number_law_v1 import DEPENDENCIES,DIMENSIONS,EXACT_RESULT,OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import ChemistryTargetReference,EmpiricalChemistrySpec
from sft.engine.source import hash_file

ROOT=Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT="experiments/external_sources/chemistry/snapshots/inorg-002-coordination-number-v1"
SPEC_PATH="experiments/external_sources/chemistry/coordination_number_capture_spec_v1.json"; SPEC_HASH="sha256:1a101ccde5af91e79a07291ac76c3a4b537e0da0dbf9c2a363d468544d4be84c"
INVENTORY_PATH=f"{SNAPSHOT_ROOT}/source-inventory-v1.json"; INVENTORY_HASH="sha256:6e33fa85567afee247f09c44be5b48f40c8e5ba06c8cf92bda0e67f5f373d527"
IDENTITY_PATH="experiments/external_sources/chemistry/coordination_number_target_identities_v1.json"; IDENTITY_HASH="sha256:c018c7ca63e082958f73c5b48fe6cbc873dc020026b8e2c519e57a4bb2ed005a"
TARGET_PATH="experiments/external_sources/chemistry/coordination_number_withheld_targets_v1.json"; TARGET_HASH="sha256:507cc60f6e04d20a781fa3cefb7e0cc9f0a3d36f48b0e078e283a8850a081d4b"
PRIMARY_PATH=f"{SNAPSHOT_ROOT}/coordination-number-primary-records-v1.json"; PRIMARY_HASH="sha256:dacc826bfaa7f87a6e13d8f90164f76d5a283d8a09df7d2b2d28bb024c4073ef"
SOURCE_FILES=((f"{SNAPSHOT_ROOT}/iupac-coordination-number.json","sha256:5c995bf40117e65eb042dc5d585692c56443ef3dc93805466779053da415fb5a"),(f"{SNAPSHOT_ROOT}/nist-cccbdb-scandium-trifluoride-experimental-geometry.html","sha256:63e6ea2c88b3aef4137c15a7986358be95c411aff96a9789ec421641e20963dc"),(f"{SNAPSHOT_ROOT}/nist-cccbdb-titanium-tetrachloride-experimental-geometry.html","sha256:3cdd6c8814bb2c9efc172afc3d83cc81e45c78a94e17d6fcbffd593b5de26358"),(f"{SNAPSHOT_ROOT}/nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html","sha256:35d46ce135ea052860c42e24dce03a4211336c0038a8a64813b24136b5b1e4b4"))
for path,expected in ((SPEC_PATH,SPEC_HASH),(INVENTORY_PATH,INVENTORY_HASH),(IDENTITY_PATH,IDENTITY_HASH),(TARGET_PATH,TARGET_HASH),(PRIMARY_PATH,PRIMARY_HASH),*SOURCE_FILES):
    if hash_file(ROOT/path)!=expected: raise ValueError(f"INORG-002 registered source changed: {path}")
_identities=json.loads((ROOT/IDENTITY_PATH).read_text())
if _identities.get("complete_registered_target_count")!=23 or _identities.get("target_values_or_hashes_present") is not False: raise ValueError("INORG-002 identity boundary changed")
TARGET_REFERENCES=tuple(ChemistryTargetReference(row["target_id"],f"{row['authority']}-{row['source_record_role']}",f"{row['source_locator']} :: {row['source_record_role']}",row["snapshot_path"],row["snapshot_sha256"]) for row in _identities["rows"])
COORDINATION_NUMBER_SPEC=EmpiricalChemistrySpec(
 claim_id="SFT-CHEM-COORDINATION-NUMBER-INCIDENCE-COUNT-002",title="Exact coordination number from generated central-ligand incidence",
 statement="For an admitted complete coordination entity, the coordination number is exactly the positive cardinality of distinct direct ligand-incidence traces on the retained central occurrence. Equal ligand-group labels do not collapse occurrences; structural absence contributes no incidence; the next direct attachment preserves all prior traces and adds exactly one.",dependencies=DEPENDENCIES,
 generation_rule="Generate the literal product of carrier, membership, quantity, identity, absence, observation, boundary and extension forms. Decide all 256 forms solely from admitted complete coordination identity, exact finite incidence and source-boundary laws.",
 grammar_boundary="Every admitted positive finite single-central coordination entity and its complete distinct direct-incidence support, tested after seal against all twenty-three registered IUPAC and NIST definition, structure, count and limitation records.",dimensions=DIMENSIONS,exact_result=EXACT_RESULT,
 induction_base="One complete direct incidence on one retained central occurrence forces positive coordination count one.",induction_step="Appending the next distinct direct incidence to the same central occurrence preserves all prior traces and increments the exact positive count by one.",
 exclusions=("no numerical zero; glyph 0 is external absence only and native absence is EmptyOne","no negative irrational imaginary floating signed or continuum proof value","no imported coordination-number table, valence rule, geometry catalogue, ligand-field or bonding model","no observed 3, 4 or 5 count before prediction seal","no selected complex, omitted boundary/limitation row, fitted distance or target-derived correction"),operational_witnesses=OPERATIONAL_WITNESSES,
 experiment_id="SFT-EXP-CHEM-COORDINATION-NUMBER-INCIDENCE-COUNT-002",expected_observation_label="complete-coordination-number-vector-correspondence",target_rows=TARGET_REFERENCES,observation_registry_path=TARGET_PATH,
 falsification_condition="The claim fails if coordination number differs from the positive cardinality of complete distinct direct incidences on the retained central occurrence; if equal ligand-group labels collapse occurrences; if absence is counted; if the successor does not preserve prior traces and add one; if any of twenty-three records changes or is omitted; if the IUPAC general, inorganic sigma, pi-exclusion or crystallographic senses are mixed; if NIST ScF3, TiCl4 and Fe(CO)5 do not retain direct-link counts 3, 4 and 5; or if any imported, fitted, continuum, numerical-zero or target-derived structure enters the law.")
COORDINATION_NUMBER_SPEC.validate()
__all__=("COORDINATION_NUMBER_SPEC","IDENTITY_HASH","IDENTITY_PATH","INVENTORY_HASH","INVENTORY_PATH","PRIMARY_HASH","PRIMARY_PATH","SOURCE_FILES","SPEC_HASH","SPEC_PATH","TARGET_HASH","TARGET_PATH","TARGET_REFERENCES")
