"""Registered THERMO-005 entropy/multiplicity law and external surface."""

from __future__ import annotations

from sft.chemistry.entropy_multiplicity_correspondence_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import EmpiricalChemistrySpec
from sft.chemistry.internal_energy_composition_batch_v1 import TARGET_REFERENCES


ENTROPY_MULTIPLICITY_CORRESPONDENCE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ENTROPY-MULTIPLICITY-CORRESPONDENCE-005",
    title="Chemical entropy and multiplicity correspondence",
    statement=(
        "Chemical entropy is the complete ledger of finite microstates merged by each held macro-observation: exact "
        "positive class multiplicity, exact support part, retained members and every unresolved pair. Singleton "
        "certainty is structural EmptyOne. Conventional scalar entropy remains a post-seal external inscription; no "
        "logarithm or irrational proof value enters the law."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of support, partition, multiplicity, entropy, certainty, prediction, record and "
        "extension forms; decide all 256 candidates only from admitted exact information-support, observation, "
        "combinatorial and finite chemical microstate laws."
    ),
    grammar_boundary=(
        "Every finite nonempty generated chemical microstate support and total macro-observation partition, with exact "
        "positive class counts, complete within-class pair ledgers and one-microstate successor closure. External "
        "testing retains every entropy and phase row of the frozen NIST one-bar water surface."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One chemical microstate forms one complete observation class with multiplicity One, exact whole support and "
        "structural EmptyOne unresolved distinctions."
    ),
    induction_step=(
        "Appending one fresh microstate assigns it to one retained macro-observation, increases that class's positive "
        "multiplicity, adds one pair with every prior member of that class, recalculates exact support parts and "
        "preserves every prior microstate and every unaffected class."
    ),
    exclusions=(
        "no numerical zero; singleton certainty is structural EmptyOne",
        "no negative, irrational, imaginary, logarithmic, floating or continuum SFT proof value",
        "no imported statistical distribution, partition function, fitted probability, log base or entropy convention",
        "no target payload, scalar entropy, phase, temperature or transition value before prediction seal",
        "no selected support, overlapping class, omitted distinction pair, selected phase row or deleted boundary state",
        "external scalar entropy inscriptions remain correspondence records and never become SFT proof values",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ENTROPY-MULTIPLICITY-CORRESPONDENCE-005",
    expected_observation_label="complete-chemical-entropy-multiplicity-ledger",
    target_rows=TARGET_REFERENCES,
    observation_registry_path="experiments/external_sources/chemistry/thermophysical_state_withheld_targets_v1.json",
    falsification_condition=(
        "The claim fails if chemical entropy requires a logarithmic or irrational proof scalar rather than the complete "
        "unresolved-distinction ledger; if class multiplicity is fitted; if a microstate occurs in both or neither "
        "class; if singleton certainty requires numerical zero; if successor extension changes prior identities; if "
        "any target opens before all identities seal; if any of thirteen entropy or phase rows is omitted; if the "
        "complete external entropy path or phase-transition entropy is not exact positive; if the independently "
        "recorded phase enthalpy/temperature ratio disagrees with the entropy jump beyond exact displayed-resolution "
        "bounds; or if target values select the law."
    ),
)
ENTROPY_MULTIPLICITY_CORRESPONDENCE_SPEC.validate()


__all__ = ("ENTROPY_MULTIPLICITY_CORRESPONDENCE_SPEC",)
