"""Registered ELEC-009 molecular-state transition specification."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.state_transition_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
IDENTITY_PATH = "experiments/external_sources/chemistry/state_transition_target_identities_v1.json"
IDENTITY_HASH = "sha256:3c4e8cb32c8a5f8992020d363894d2420056cc108dbf667bf5de4baba87cffc2"
TARGET_PATH = "experiments/external_sources/chemistry/state_transition_withheld_targets_v1.json"
TARGET_HASH = "sha256:219b5c70f508db7083cbc8c41a7b75118507183f8f5de91e45576835e60b6ac1"
SOURCE_ID = "NIST-CHEMISTRY-WEBBOOK-SRD69-H2-TRANSITIONS"


for path, expected in ((IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH)):
    if hash_file(ROOT / path) != expected: raise ValueError("ELEC-009 registered source changed: " + path)
document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
if document.get("schema") != "sft-v3-state-transition-identities/1" or len(document.get("rows", ())) != 60: raise ValueError("ELEC-009 identity registry is incomplete")
TARGET_REFERENCES = tuple(ChemistryTargetReference(str(row["target_id"]), str(row["source_id"]), str(row["source_url"]) + " :: " + str(row["source_row_kind"]) + " " + str(row["source_row_ordinal"]), str(row["snapshot_path"]), str(row["snapshot_hash"])) for row in document["rows"])


STATE_TRANSITION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-MOLECULAR-STATE-TRANSITION-009", title="Exact molecular-state transformation and transition law", statement="A molecular-state transformation retains one carrier, distinct state endpoints, a held orientation or coupling class, and its exact observation trace. Matching endpoints compose into finite transition paths. An absent transition coordinate is structural EmptyOne, not numerical zero. Selection criteria are not imported before their separate derivation.", dependencies=DEPENDENCIES,
    generation_rule="Generate the literal product of carrier, endpoints, orientation, absence, trace, composition, record and extension forms. Decide all 256 forms only from admitted state-transition, observation, molecular-state and exact-composition laws.", grammar_boundary="Every positive finite molecular-state transition record and every matching finite path successor, externally tested against all 46 NIST H2 primary state rows and all 14 continuation transition rows.", dimensions=DIMENSIONS, exact_result=EXACT_RESULT,
    induction_base="One observed transformation retains one carrier, two distinct endpoints, one held orientation and one exact record; one absent coordinate retains its initial state and structural EmptyOne.", induction_step="A transition whose initial state equals the prior terminal state appends one retained terminal state and orientation to the finite path without altering prior records.", exclusions=("no numerical zero; glyph 0 denotes source/interface absence only", "no negative, irrational, imaginary, floating, signed-amplitude or continuum proof magnitude", "no imported dipole, spin, parity, angular-momentum or spectroscopic selection rule", "no NIST state, transition, band or absence outcome before prediction seal", "no selected present-only row surface", "no species-specific exception"), operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-MOLECULAR-STATE-TRANSITION-009", expected_observation_label="complete-molecular-state-transition-presence-coupling-absence-correspondence", target_rows=TARGET_REFERENCES, observation_registry_path=TARGET_PATH,
    falsification_condition="The claim fails if a transition loses its carrier, either endpoint, orientation or record; if unequal endpoints compose; if absence is treated numerically; if a selection rule is imported to define transformation before ELEC-010; if any of 46 primary rows, 14 continuation rows, 55 directional records, four coupled-state records, one absent transition coordinate, 55 positive band inscriptions or five absent band coordinates is omitted, changed or reclassified.",
)
STATE_TRANSITION_SPEC.validate()


__all__ = ("IDENTITY_HASH", "IDENTITY_PATH", "SOURCE_ID", "STATE_TRANSITION_SPEC", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES")
