"""Target-blind generated Fold blueprints for foundational Medicine."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from sft.medicine.obligations import MEDICINE_OBLIGATIONS, MedicineObligation
from sft.medicine.structural_counts import diagnostic_table_certificate, two_arm_outcome_certificate
from sft.physics.generated_empirical_law import LawDimension, dimension


BASE_DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-PROBABILITY-STATISTICS-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-MUTUAL-CONDITIONAL-001",
    "SFT-INFO-ENTROPY-UNCERTAINTY-001",
    "SFT-COMP-SEM-SPECIFICATION-001",
    "SFT-COMP-SEM-VERIFICATION-001",
    "SFT-COMP-DIST-CAUSALITY-001",
    "SFT-COMP-SCI-COMPUTATIONAL-STATISTICS-001",
    "SFT-PHYS-MEAS-OBSERVATION-CARRIER-001",
    "SFT-PHYS-MEAS-UNCERTAINTY-001",
    "SFT-CHEM-MEAS-CHEMICAL-SPECIES-001",
    "SFT-CHEM-MEAS-UNCERTAINTY-001",
    "SFT-CHEM-STEREO-ENANTIOMER-001",
    "SFT-MAT-MEAS-TRACEABILITY-001",
    "SFT-MAT-FUNC-BIOMATERIAL-001",
    "SFT-BIO-ORGANISM-001",
    "SFT-BIO-PHYSIOLOGY-001",
    "SFT-BIO-HOMEOSTASIS-001",
    "SFT-BIO-POPULATION-001",
    "SFT-BIO-BIO-CONDITION-001",
    "SFT-BIO-BIO-ASSAY-001",
    "SFT-BIO-BIO-UNCERTAINTY-001",
    "SFT-BIO-BIO-CAUSALITY-001",
)


@dataclass(frozen=True)
class MedicineBlueprint:
    claim_id: str
    title: str
    family: str
    statement: str
    dependencies: tuple[str, ...]
    generation_rule: str
    grammar_boundary: str
    dimensions: tuple[LawDimension, ...]
    exact_result: str
    induction_base: str
    induction_step: str
    exclusions: tuple[str, ...]
    operational_witnesses: tuple[tuple[str, str, bool], ...]
    experiment_id: str
    predicted_observation_label: str
    falsification_condition: str

    def validate(self) -> None:
        if not self.claim_id.startswith("SFT-MED-") or not self.experiment_id.startswith("SFT-EXP-MED-"):
            raise ValueError("invalid Medicine identity")
        if len(self.dimensions) != 8 or len({row.key for row in self.dimensions}) != 8:
            raise ValueError("Medicine blueprint requires eight distinct dimensions")
        if any(len(row.choices) != 2 for row in self.dimensions):
            raise ValueError("each Medicine dimension must exhaust two registered forms")
        if self.exact_result != "__".join(row.admitted_choice.name for row in self.dimensions):
            raise ValueError("Medicine exact result is not the unique preservation survivor")
        if not self.dependencies or len(self.dependencies) != len(set(self.dependencies)):
            raise ValueError("Medicine dependencies are empty or repeated")
        if not all(passed for _, _, passed in self.operational_witnesses):
            raise ValueError("Medicine operational witness failed")


def _dimensions(row: MedicineObligation) -> tuple[LawDimension, ...]:
    return (
        dimension("carrier", "carrier-erased-aggregate-or-answer-only", "Erasing the patient, population, specimen or evidence carrier prevents clinical reconstruction.", row.carrier, "The complete generated clinical carrier is retained."),
        dimension("relation", "relation-imported-fitted-or-erased", "An imported, fitted or absent relation can manufacture a familiar medical answer.", row.relation, "Only the generated transition or comparison relation is admitted."),
        dimension("organization", "organization-collapsed", "Collapsing person, arm, outcome, time or evidence organization merges clinically distinct states.", row.organization, "Every required clinical organization distinction remains held."),
        dimension("observation", "observation-boundary-unrecorded", "An unrecorded population, method, setting, interval or assessor cannot identify the observation class.", row.observation, "The complete declared observation boundary is retained and cannot select the law."),
        dimension("record", "favorable-result-without-complete-record", "A favorable label without protocol, transitions, missingness, adverse outcomes and controls is not auditable.", "complete-protocol-state-transition-adverse-null-record", "Initial state, transitions, protocol deviations, adverse, null, unresolved and missing rows are recorded."),
        dimension("provenance", "authority-consensus-prior-or-target-selected-law", "Authority, consensus, prior SFT work or target outcomes may test but cannot select the Fold law.", "root-bound-forward-forcing", "Every decision traces through admitted dependencies to There Is No Nothing."),
        dimension("generality", "single-patient-favorable-study", "One favorable patient, trial, population or analysis cannot close the generated clinical class.", "positive-finite-successor-and-unfavorable-closure", "The base carrier, every supplied positive finite successor and all registered unfavorable controls preserve the relation at its stated boundary."),
        dimension("extension", "free-fit-exception-opaque-model-or-extra-rule", "A free coefficient, fitted cutoff, hidden exclusion, opaque model or exception can manufacture a desired answer.", "no-extra-rule", "No rule beyond admitted Fold dependencies and generated preservation conditions is present."),
    )


def _witnesses(row: MedicineObligation) -> tuple[tuple[str, str, bool], ...]:
    witnesses: list[tuple[str, str, bool]] = [
        ("carrier", "clinical carrier is explicit and nonempty", bool(row.carrier)),
        ("relation", "relation and organization remain separately reconstructible", row.relation != row.organization),
        ("boundary", "observation boundary cannot silently become the clinical law", row.observation != row.relation),
    ]
    if row.claim_id == "SFT-MED-DIAGNOSTIC-ACCURACY-001":
        cert = diagnostic_table_certificate()
        witnesses.append(("complete-diagnostic-table", "two held diagnostic distinctions generate four cells exactly once", cert["complete"] is True and cert["cell_count"] == 4))
    if row.claim_id in {"SFT-MED-ABSOLUTE-RELATIVE-EFFECT-001", "SFT-MED-EFFICACY-001"}:
        cert = two_arm_outcome_certificate()
        witnesses.append(("complete-arm-outcome-table", "two arms crossed with two retained outcome labels generate four cells exactly once", cert["complete"] is True and cert["cell_count"] == 4))
    return tuple(witnesses)


def _blueprints() -> tuple[MedicineBlueprint, ...]:
    output: list[MedicineBlueprint] = []
    previous: str | None = None
    for row in MEDICINE_OBLIGATIONS:
        dimensions = _dimensions(row)
        dependencies = tuple(dict.fromkeys(BASE_DEPENDENCIES + (() if previous is None else (previous,))))
        blueprint = MedicineBlueprint(
            claim_id=row.claim_id,
            title=row.title,
            family=row.family,
            statement=row.statement,
            dependencies=dependencies,
            generation_rule="Generate the Cartesian product of all registered binary preservation dimensions before opening any clinical source or outcome.",
            grammar_boundary="Exactly eight binary dimensions and therefore 256 forms; closure is conditional only on this explicit complete grammar.",
            dimensions=dimensions,
            exact_result="__".join(item.admitted_choice.name for item in dimensions),
            induction_base="The least positive finite clinical carrier retains every required identity, relation, boundary, outcome and proof record.",
            induction_step="Adding one lawful finite successor preserves all earlier persons, arms, outcomes, times, adverse and missing distinctions and appends the new trace.",
            exclusions=("numerical-zero ontology", "negative proof quantity", "irrational or imaginary proof value", "fitted coefficient or cutoff", "external target leakage", "opaque predictor", "unrecorded patient or population", "erased adverse, null, absent or unresolved result", "prior answer as premise"),
            operational_witnesses=_witnesses(row),
            experiment_id="SFT-EXP-" + row.claim_id.removeprefix("SFT-") + "-E1",
            predicted_observation_label="medicine:" + row.carrier + "__" + row.relation + "__" + row.organization + "__" + row.observation,
            falsification_condition="Reject if any registered authoritative medical source contradicts a required relation, if another generated form preserves every dimension, or if any patient, arm, outcome, adverse, null, missing, consent or provenance distinction is erased.",
        )
        blueprint.validate()
        output.append(blueprint)
        previous = row.claim_id
    return tuple(output)


MEDICINE_BLUEPRINTS = _blueprints()
BLUEPRINT_BY_CLAIM = {row.claim_id: row for row in MEDICINE_BLUEPRINTS}


def candidate_forms(blueprint: MedicineBlueprint) -> tuple[tuple[str, ...], ...]:
    blueprint.validate()
    return tuple(tuple(choice.name for choice in choices) for choices in product(*(row.choices for row in blueprint.dimensions)))


def unique_survivor(blueprint: MedicineBlueprint) -> tuple[str, ...]:
    survivors = []
    for form in candidate_forms(blueprint):
        if all(form[index] == dimension_row.admitted_choice.name for index, dimension_row in enumerate(blueprint.dimensions)):
            survivors.append(form)
    if len(survivors) != 1:
        raise ValueError("Medicine grammar did not produce exactly one survivor")
    return survivors[0]


def validate_blueprints() -> None:
    if len(MEDICINE_BLUEPRINTS) != 72:
        raise ValueError("Medicine blueprint count changed")
    if len(BLUEPRINT_BY_CLAIM) != len(MEDICINE_BLUEPRINTS):
        raise ValueError("Medicine blueprint identities repeat")
    for blueprint in MEDICINE_BLUEPRINTS:
        if len(candidate_forms(blueprint)) != 256:
            raise ValueError("Medicine candidate census is incomplete")
        if "__".join(unique_survivor(blueprint)) != blueprint.exact_result:
            raise ValueError("Medicine survivor reconstruction failed")


validate_blueprints()

__all__ = ("BASE_DEPENDENCIES", "MedicineBlueprint", "MEDICINE_BLUEPRINTS", "BLUEPRINT_BY_CLAIM", "candidate_forms", "unique_survivor", "validate_blueprints")
