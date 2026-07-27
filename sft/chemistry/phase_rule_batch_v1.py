"""Registered THERMO-011 law and complete IUPAC/NIST phase-rule structure surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.phase_rule_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/thermo-011-phase-rule-v2"
SPEC_PATH = "experiments/external_sources/chemistry/phase_rule_capture_spec_v2.json"
SPEC_HASH = "sha256:5c95f5c680081ee849143256ddc87683a61dc078fd7911467100b4dc48ddadd8"
IUPAC_PATH = f"{SNAPSHOT_ROOT}/iupac-goldbook-P04533-phase-rule.html"
IUPAC_HASH = "sha256:49cb8a30304e143e190be51be1a9fcd9045e0581718d0da2bc1ebcdd73152477"
NIST_PATH = f"{SNAPSHOT_ROOT}/nist-general-discussion-glossary-phase-diagrams.pdf"
NIST_HASH = "sha256:8572fe338cf9256c9510d89cfc0d62b16d272575d69d89e6584e39cb629fc5f6"
NIST_TEXT_PATH = f"{SNAPSHOT_ROOT}/nist-phase-diagram-glossary-extracted-pages-v1.json"
NIST_TEXT_HASH = "sha256:f9bf7385989e3434d93e0825ce4b80e4eeae0d1965c5708948fccf85f18b708d"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/phase-rule-primary-records-v1.json"
PRIMARY_HASH = "sha256:a679c64cba292806c4eed580f763c16f092c115b6952fd83809eba1f814f2bf6"
IDENTITY_PATH = "experiments/external_sources/chemistry/phase_rule_target_identities_v2.json"
IDENTITY_HASH = "sha256:371bbbdfc44c2564fbe3e70534e2fa8cd04efe61fcf1bdf2a3d37e53990a224b"
TARGET_PATH = "experiments/external_sources/chemistry/phase_rule_withheld_targets_v2.json"
TARGET_HASH = "sha256:512a909e7f7e2b72b15830cf688eadcd73ea5b63ae3418d85d0bd908ebd8774c"


for path, expected in (
    (SPEC_PATH, SPEC_HASH),
    (IUPAC_PATH, IUPAC_HASH),
    (NIST_PATH, NIST_HASH),
    (NIST_TEXT_PATH, NIST_TEXT_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"THERMO-011 registered source changed: {path}")


_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
_targets = json.loads((ROOT / TARGET_PATH).read_text())
if (
    _primary.get("complete_component_count_classes") != 4
    or _primary.get("complete_component_phase_identity_count") != 18
    or _primary.get("positive_degree_support_target_count") != 14
    or _primary.get("external_zero_glyph_degree_target_count") != 4
    or _primary.get("nist_complete_page_count") != 32
    or _identities.get("complete_target_count") != 18
    or _identities.get("all_degree_support_outcome_source_fragment_and_target_hash_values_absent") is not True
    or len(_identities.get("rows", ())) != 18
    or _targets.get("complete_target_count") != 18
    or len(_targets.get("rows", ())) != 18
):
    raise ValueError("THERMO-011 complete source boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"],
        source_id="IUPAC-GOLDBOOK-P04533-AND-NIST-PHASE-DIAGRAM-GLOSSARY",
        source_locator=(
            f"component identity {row['component_count_identity']}; phase identity {row['phase_count_identity']}"
        ),
        snapshot_path=PRIMARY_PATH,
        snapshot_hash=PRIMARY_HASH,
    )
    for row in _identities["rows"]
)


PHASE_RULE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-PHASE-RULE-STRUCTURAL-011",
    title="Chemical phase-rule structural relation",
    statement=(
        "A complete equilibrium account contains one coordinate carrier per independent component and the two "
        "held environmental carriers. Each coexisting phase cancels exactly one available carrier. The uncancelled "
        "finite carrier word is the independent degree support; complete cancellation is structural EmptyOne. "
        "This relation is forced without importing the subtractive phase-rule equation or numerical zero."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, components, phases, environment, relation, absence, observation "
        "and extension forms; decide all 256 candidates only from admitted finite-support, composition, exact "
        "cancellation, equilibrium, structural-absence and successor laws."
    ),
    grammar_boundary=(
        "Every finite positive component word, positive coexisting-phase word and exactly two held environmental "
        "coordinate carriers for which phase cancellation does not exceed complete carrier support. External "
        "testing preserves the complete 18-row component/phase identity product for one through four components, "
        "all 14 positive degree-support outcomes, four invariant EmptyOne outcomes, the full IUPAC term and the "
        "complete 32-page NIST source."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One component carrier and the two held environment carriers form the least complete support word; one "
        "coexisting phase cancels one carrier and leaves two independent carriers."
    ),
    induction_step=(
        "Appending one independent component adds one carrier and appending one coexisting phase cancels exactly "
        "that one added carrier, preserving the prior uncancelled support word at every finite depth."
    ),
    exclusions=(
        "no numerical zero; complete cancellation is structural EmptyOne and the external zero glyph remains an interface inscription",
        "no subtraction, signed count, negative, irrational, imaginary, floating or continuum SFT proof value",
        "no imported Gibbs phase-rule equation, Gibbs-Duhem equation or algebraic rearrangement",
        "no free intensive coordinate, selected phase diagram, selected component/phase row or target-derived correction",
        "no degree outcome, invariant classification, source equation fragment or target hash before prediction seal",
        "every external count and equation remains a post-seal source-bound comparison record",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-PHASE-RULE-STRUCTURAL-011",
    expected_observation_label="complete-component-phase-degree-support-correspondence",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if any component, phase or held environmental carrier is erased; if a phase does not "
        "cancel exactly one available carrier; if complete cancellation becomes numerical zero; if an imported "
        "phase-rule equation, subtraction, signed count, continuum coordinate, selected diagram or target-derived "
        "correction enters; if the joint component/phase successor changes degree support; if any target opens "
        "before all 18 identities seal; if any of 18 rows, 14 positive outcomes, four EmptyOne boundaries, full "
        "IUPAC term or complete 32-page NIST source is omitted; or if a target degree outcome is tampered."
    ),
)
PHASE_RULE_SPEC.validate()


__all__ = (
    "IDENTITY_HASH", "IDENTITY_PATH", "IUPAC_HASH", "IUPAC_PATH", "NIST_HASH", "NIST_PATH",
    "NIST_TEXT_HASH", "NIST_TEXT_PATH", "PHASE_RULE_SPEC", "PRIMARY_HASH", "PRIMARY_PATH",
    "SPEC_HASH", "SPEC_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
