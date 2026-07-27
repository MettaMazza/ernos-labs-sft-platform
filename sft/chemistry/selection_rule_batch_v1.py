"""Registered ELEC-010 chemical selection-rule specification."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.selection_rule_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
IDENTITY_PATH = "experiments/external_sources/chemistry/selection_rule_target_identities_v1.json"
IDENTITY_HASH = "sha256:974583091f4c1cd484b8761fe014c5870db38a175a3fd5c8c2b1147b17e62e87"
TARGET_PATH = "experiments/external_sources/chemistry/selection_rule_withheld_targets_v1.json"
TARGET_HASH = "sha256:94af2d38e07bbcdd4f70e74557c5f174ebff586f4d287db541bee00ae204b56f"
SOURCE_ID = "NIST-CHEMISTRY-WEBBOOK-SRD69-H2-SELECTION-SURFACE"


for path, expected in ((IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH)):
    if hash_file(ROOT / path) != expected:
        raise ValueError("ELEC-010 registered source changed: " + path)
document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
if document.get("schema") != "sft-v3-selection-rule-identities/1" or len(document.get("rows", ())) != 63:
    raise ValueError("ELEC-010 identity registry is incomplete")
TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        str(row["target_id"]), str(row["source_id"]),
        str(row["source_url"]) + " :: " + str(row["target_kind"]),
        str(row["snapshot_path"]), str(row["snapshot_hash"]),
    )
    for row in document["rows"]
)


SELECTION_RULE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-SELECTION-RULE-STRUCTURE-010",
    title="Exact chemical observation-class and selection-rule structure",
    statement="A direct molecular observation retains spin-support multiplicity, changes a known inversion fibre, and changes axis support by no more than one generated recurrence. An observed relation outside that direct class requires a retained mediator or alternate observation channel; it does not erase the rule. Couplings, unresolved endpoints and channel absences remain separate exact classes, and absence is structural EmptyOne rather than numerical zero.",
    dependencies=DEPENDENCIES,
    generation_rule="Generate the literal product of endpoint, observation-class, multiplicity, inversion, axis, mediation, absence and complete-record forms. Decide all 256 forms only from admitted Fold observation, information-retention, state-symmetry and molecular-transition laws.",
    grammar_boundary="Every positive finite Fold axis recurrence under one direct observation action, together with mediated finite compositions and the complete registered NIST H2 transition, coupling, absence and adverse-note surface.",
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="At structural EmptyOne axis support, one direct action either retains that support or reaches the first recurrence while retaining multiplicity and changing every known complementary inversion fibre.",
    induction_step="At any positive finite axis recurrence, one additional direct Fold action reaches only the same, predecessor or successor support; a larger observed displacement factors into a positive finite mediated path whose intermediate record may not be erased.",
    exclusions=(
        "no numerical zero; glyph 0 denotes source/interface absence only",
        "no negative, irrational, imaginary, floating, signed-amplitude or continuum proof magnitude",
        "no imported spectroscopic selection-rule formula or probability threshold",
        "no NIST endpoint, transition, coupling, absence or adverse-note outcome before prediction seal",
        "no observed exception relabelled as an ordinary direct transition",
        "no selected success-only surface and no erased channel distinction",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-SELECTION-RULE-STRUCTURE-010",
    expected_observation_label="complete-direct-mediated-coupled-unresolved-closed-selection-correspondence",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition="The claim fails if a direct observation changes multiplicity, preserves a known g/u fibre, jumps more than one axis recurrence, or loses either endpoint; if an observed non-direct case is admitted without a retained mediation requirement; if channel absence is treated as numerical zero or universal nonexistence; or if any of 60 NIST transition rows, three adverse notes, 52 direct one-step records, two mediated two-step records, one unresolved endpoint, four couplings or one closed coordinate is omitted or changed.",
)
SELECTION_RULE_SPEC.validate()


__all__ = (
    "IDENTITY_HASH", "IDENTITY_PATH", "SELECTION_RULE_SPEC", "SOURCE_ID",
    "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
