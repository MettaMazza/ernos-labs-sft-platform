"""Target-blind generated Fold blueprints for foundational Biology.

Every familiar biological name denotes a reconciliation question only. The
survivor is selected solely by complete preservation of the generated carrier,
relation, organization, observation class, proof record, root provenance,
finite extension and absence of an added rule. External evidence remains
structurally inaccessible until the complete blueprint set is sealed.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from sft.biology.obligations import BIOLOGY_OBLIGATIONS, BiologyObligation
from sft.biology.structural_counts import exact_codon_certificate
from sft.physics.generated_empirical_law import LawDimension, dimension


BASE_DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-ENCODING-DECODING-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-MEAS-OBSERVATION-CARRIER-001",
    "SFT-PHYS-MEAS-UNCERTAINTY-001",
    "SFT-CHEM-MEAS-CHEMICAL-ENTITY-001",
    "SFT-CHEM-RXN-IDENTITY-001",
    "SFT-CHEM-STOICH-CONSERVATION-001",
    "SFT-CHEM-STEREO-CHIRALITY-001",
    "SFT-MAT-MICRO-INTERFACE-001",
    "SFT-MAT-FUNC-BIOMATERIAL-001",
)


@dataclass(frozen=True)
class BiologyBlueprint:
    claim_id: str
    title: str
    subbranch: str
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
        if not self.claim_id.startswith("SFT-BIO-") or not self.experiment_id.startswith("SFT-EXP-BIO-"):
            raise ValueError("invalid Biology identity")
        if len(self.dimensions) != 8 or len({row.key for row in self.dimensions}) != 8:
            raise ValueError("Biology blueprint requires eight distinct dimensions")
        if any(len(row.choices) != 2 for row in self.dimensions):
            raise ValueError("each Biology dimension must exhaust two registered forms")
        if self.exact_result != "__".join(row.admitted_choice.name for row in self.dimensions):
            raise ValueError("Biology exact result is not the unique preservation survivor")
        if not self.dependencies or len(self.dependencies) != len(set(self.dependencies)):
            raise ValueError("Biology dependencies are empty or repeated")
        if not all(passed for _, _, passed in self.operational_witnesses):
            raise ValueError("Biology operational witness failed")


def _dimensions(row: BiologyObligation) -> tuple[LawDimension, ...]:
    return (
        dimension("carrier", "carrier-erased-or-answer-only", "Erasing the biological carrier prevents reconstruction of the claimed living distinction.", row.carrier, "The complete generated biological carrier is retained."),
        dimension("relation", "relation-imported-fitted-or-erased", "An imported, fitted or absent relation can select a familiar biological answer without forcing it.", row.relation, "Only the generated biological transition or comparison relation is admitted."),
        dimension("organization", "organization-collapsed", "Collapsing organization merges living states the question requires to remain distinct.", row.organization, "Every boundary, lineage, context and organization distinction required by the claim remains held."),
        dimension("observation", "observation-boundary-unrecorded", "An unrecorded organism, condition, assay, scale or interval cannot identify the biological observation class.", row.observation, "The complete declared observation boundary is retained and cannot select the law."),
        dimension("record", "result-without-transition-record", "A biological label without initial state, transitions, controls and outcomes is not auditable.", "complete-state-transition-control-record", "Initial state, transitions, controls, results and retained or lost distinctions are recorded."),
        dimension("provenance", "authority-target-or-prior-selected-law", "Authority, consensus, a prior SFT answer or target data may test but cannot select a Fold law.", "root-bound-forward-forcing", "Every decision traces through admitted dependencies to the premise-free root theorem."),
        dimension("generality", "single-specimen-favorable-instance", "One favorable organism, specimen or experiment cannot close the generated biological class.", "positive-finite-successor-and-adverse-closure", "Base carrier, every positive finite successor and all registered adverse controls preserve the relation at the stated boundary."),
        dimension("extension", "free-fit-exception-or-extra-rule", "A free coefficient, fitted threshold, exception or opaque predictor can manufacture a desired answer.", "no-extra-rule", "No rule beyond admitted Fold dependencies and generated preservation conditions is present."),
    )


def _witnesses(row: BiologyObligation) -> tuple[tuple[str, str, bool], ...]:
    witnesses: list[tuple[str, str, bool]] = [
        ("carrier", "the biological carrier is explicit and nonempty", bool(row.carrier)),
        ("relation", "relation and organization remain separately reconstructible", row.relation != row.organization),
        ("boundary", "observation boundary cannot silently become the biological law", row.observation != row.relation),
    ]
    counts = exact_codon_certificate()
    if row.claim_id == "SFT-BIO-NUCLEOTIDE-ALPHABET-001":
        witnesses.append(("four-symbol-alphabet", "two held distinctions generate exactly four distinct ordered labels", counts["alphabet_count"] == 4 and counts["alphabet_complete"] is True))
    if row.claim_id == "SFT-BIO-CODON-001":
        witnesses.append(("sixty-four-triplets", "four symbols over three ordered positions generate exactly sixty-four words", counts["word_length"] == 3 and counts["codon_count"] == 64 and counts["codon_census_complete"] is True))
    if row.claim_id == "SFT-BIO-CODON-BOX-001":
        witnesses.append(("sixteen-four-word-boxes", "prefix equivalence produces sixteen boxes of four words and partitions all sixty-four exactly once", counts["box_count"] == 16 and counts["box_widths"] == (4,) and counts["partition_complete"] is True and counts["each_word_once"] is True))
    return tuple(witnesses)


def _blueprints() -> tuple[BiologyBlueprint, ...]:
    output: list[BiologyBlueprint] = []
    previous: str | None = None
    for row in BIOLOGY_OBLIGATIONS:
        dimensions = _dimensions(row)
        dependencies = tuple(dict.fromkeys(BASE_DEPENDENCIES + (() if previous is None else (previous,))))
        blueprint = BiologyBlueprint(
            claim_id=row.claim_id,
            title=row.title,
            subbranch=row.subbranch,
            statement=row.statement,
            dependencies=dependencies,
            generation_rule="Generate the Cartesian product of every registered binary preservation dimension; do not inspect external targets or prior answers.",
            grammar_boundary="Exactly eight binary dimensions and therefore 256 forms; the statement is conditional only on this explicit complete grammar.",
            dimensions=dimensions,
            exact_result="__".join(item.admitted_choice.name for item in dimensions),
            induction_base="The least positive finite carrier retains every required biological distinction and its complete control record.",
            induction_step="Adding one lawful finite successor preserves all existing identities, relations, boundaries and provenance and appends its new transition and adverse alternatives.",
            exclusions=("numerical-zero ontology", "negative proof quantity", "irrational or imaginary proof value", "fitted coefficient or threshold", "external target leakage", "opaque predictor", "unrecorded specimen or condition", "erased adverse result", "prior answer as premise"),
            operational_witnesses=_witnesses(row),
            experiment_id="SFT-EXP-" + row.claim_id.removeprefix("SFT-") + "-E1",
            predicted_observation_label="biology:" + row.carrier + "__" + row.relation + "__" + row.organization + "__" + row.observation,
            falsification_condition="Reject if any registered authoritative biological source contradicts a required content relation, if a generated alternative also preserves every dimension, or if any specimen, control, adverse row, condition or provenance distinction is missing.",
        )
        blueprint.validate()
        output.append(blueprint)
        previous = row.claim_id
    return tuple(output)


BIOLOGY_BLUEPRINTS = _blueprints()
BLUEPRINT_BY_CLAIM = {row.claim_id: row for row in BIOLOGY_BLUEPRINTS}


def candidate_forms(blueprint: BiologyBlueprint) -> tuple[tuple[str, ...], ...]:
    blueprint.validate()
    return tuple(tuple(choice.name for choice in choices) for choices in product(*(row.choices for row in blueprint.dimensions)))


def unique_survivor(blueprint: BiologyBlueprint) -> tuple[str, ...]:
    survivors = []
    for form in candidate_forms(blueprint):
        if all(form[index] == dimension_row.admitted_choice.name for index, dimension_row in enumerate(blueprint.dimensions)):
            survivors.append(form)
    if len(survivors) != 1:
        raise ValueError("Biology grammar did not produce exactly one survivor")
    return survivors[0]


def validate_blueprints() -> None:
    if len(BIOLOGY_BLUEPRINTS) != 75:
        raise ValueError("Biology blueprint count changed")
    if len(BLUEPRINT_BY_CLAIM) != len(BIOLOGY_BLUEPRINTS):
        raise ValueError("Biology blueprint identities repeat")
    for blueprint in BIOLOGY_BLUEPRINTS:
        if len(candidate_forms(blueprint)) != 256:
            raise ValueError("Biology candidate census is incomplete")
        if "__".join(unique_survivor(blueprint)) != blueprint.exact_result:
            raise ValueError("Biology survivor reconstruction failed")


validate_blueprints()

__all__ = ("BASE_DEPENDENCIES", "BiologyBlueprint", "BIOLOGY_BLUEPRINTS", "BLUEPRINT_BY_CLAIM", "candidate_forms", "unique_survivor", "validate_blueprints")
