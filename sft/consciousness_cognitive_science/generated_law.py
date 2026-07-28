"""Generated candidate grammar for the Consciousness foundation."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from sft.consciousness_cognitive_science.obligations import CONSCIOUSNESS_OBLIGATIONS, FAMILY_ORDER, ConsciousnessObligation
from sft.consciousness_cognitive_science.structural_model import structural_witnesses
from sft.physics.generated_empirical_law import LawDimension, dimension


BASE_DEPENDENCIES = (
    "SFT-FOUNDATION-ONE-001",
    "SFT-FOUNDATION-FOLD-001",
    "SFT-FOUNDATION-FOLD-DYNAMICS-001",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-MATH-CATEGORY-TYPE-COMPOSITION-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-QUANTITY-001",
    "SFT-INFO-MUTUAL-CONDITIONAL-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-COMP-FORM-COMPOSITION-001",
    "SFT-COMP-FORM-RECURSIVE-FUNCTION-001",
    "SFT-COMP-LEARN-INFERENCE-001",
    "SFT-COMP-LEARN-REPRESENTATION-001",
    "SFT-PHYS-MEAS-OBSERVATION-CARRIER-001",
    "SFT-BIO-INSIDE-OUTSIDE-001",
    "SFT-BIO-LIFE-IDENTITY-TURNOVER-001",
    "SFT-MED-SYMPTOM-001",
)


@dataclass(frozen=True)
class ConsciousnessBlueprint:
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
        if not self.claim_id.startswith("SFT-CONSC-") or not self.experiment_id.startswith("SFT-EXP-CONSC-"):
            raise ValueError("Consciousness claim identity is invalid")
        if not self.dependencies or len(self.dimensions) != 8:
            raise ValueError("Consciousness claim lacks dependencies or eight dimensions")
        if len({item.key for item in self.dimensions}) != 8:
            raise ValueError("Consciousness dimensions repeat")
        if any(len(item.choices) != 2 for item in self.dimensions):
            raise ValueError("each Consciousness dimension must contain two exhaustive registered forms")
        if not all(passed for _, _, passed in self.operational_witnesses):
            raise ValueError("a Consciousness operational witness failed")
        if self.exact_result != "__".join(item.admitted_choice.name for item in self.dimensions):
            raise ValueError("the registered result differs from the preserving form")


def _dimensions(item: ConsciousnessObligation) -> tuple[LawDimension, ...]:
    return (
        dimension("carrier", "carrier-absent-or-description-only", "A missing carrier or mere description cannot instantiate the claimed relation.", item.carrier, "The complete declared carrier is retained."),
        dimension("distinction", "distinction-collapsed-or-conflated", "Collapsing the named distinction substitutes one evidence or process class for another.", item.distinction, "The claim-specific distinction remains held."),
        dimension("operation", "operation-imported-fitted-or-missing", "An imported, fitted or absent operation can manufacture a familiar theory of mind.", item.operation, "Only the generated Fold relation and admitted dependencies act."),
        dimension("record", "favourable-output-without-complete-trace", "An output without its source, transition, missing and adverse records is not auditable.", item.retained_record, "The complete required record is retained."),
        dimension("evidence", "report-behaviour-correlation-or-confidence-substituted", "A report, behaviour, neural correlation or model confidence cannot silently become phenomenal occurrence.", item.evidence_boundary, "The exact evidence class and any bridge are named."),
        dimension("provenance", "prior-consensus-target-or-application-selected", "Prior SFT, consensus, targets or applications may register questions or test consequences but cannot select the law.", "root-bound-forward-forcing", "Every result traces through admitted dependencies to There Is No Nothing."),
        dimension("generality", "one-favourable-instance-with-erased-alternatives", "One favorable instance cannot close a generated class while adverse and uncertain alternatives are erased.", "positive-finite-successor-with-all-alternatives", "The base and every supplied positive finite successor preserve all favorable, adverse, absent and unresolved distinctions."),
        dimension("extension", "free-parameter-exception-or-opaque-oracle", "A fitted parameter, exception or opaque oracle can force a preferred answer.", "no-extra-rule", "No rule beyond the admitted Fold dependencies and generated preservation conditions is added."),
    )


def _witnesses(item: ConsciousnessObligation) -> tuple[tuple[str, str, bool], ...]:
    exact = structural_witnesses()
    family_witness = {
        FAMILY_ORDER[0]: exact["two_preimages_share_one_image"],
        FAMILY_ORDER[1]: exact["unretained_observation_is_not_reversible"],
        FAMILY_ORDER[2]: exact["observer_observed_partition_the_one"] and exact["binding_lock_completes"],
        FAMILY_ORDER[3]: exact["two_preimages_are_distinct"],
        FAMILY_ORDER[4]: exact["retained_observation_is_reversible"] and exact["unretained_observation_is_not_reversible"],
        FAMILY_ORDER[5]: exact["complementary_pair_recurs"],
        FAMILY_ORDER[6]: exact["self_model_closes_in_two_nonidentity_acts"],
        FAMILY_ORDER[7]: exact["two_preimages_are_distinct"],
        FAMILY_ORDER[8]: exact["two_preimages_share_one_image"],
        FAMILY_ORDER[9]: exact["observer_observed_partition_the_one"],
        FAMILY_ORDER[10]: exact["three_quality_support_recurs"],
        FAMILY_ORDER[11]: exact["red_of_red_form_is_complete"],
    }[item.family]
    return (
        ("claim-carrier", "the claim retains a nonempty named carrier", bool(item.carrier.strip())),
        ("distinction-operation", "the retained distinction is not collapsed into its operation", item.distinction != item.operation),
        ("evidence-boundary", "the evidence class does not silently become the carrier", item.evidence_boundary not in {item.carrier, item.distinction}),
        ("exact-fold-witness", "the family's exact Fold construction reproduces", family_witness),
    )


def _blueprints() -> tuple[ConsciousnessBlueprint, ...]:
    output: list[ConsciousnessBlueprint] = []
    previous_family_terminal: str | None = None
    family_rows: list[ConsciousnessObligation] = []
    for family in FAMILY_ORDER:
        family_rows = [row for row in CONSCIOUSNESS_OBLIGATIONS if row.family == family]
        previous_in_family: str | None = None
        for item in family_rows:
            local = (() if previous_in_family is None else (previous_in_family,))
            inherited = (() if previous_family_terminal is None else (previous_family_terminal,))
            dependencies = tuple(dict.fromkeys(BASE_DEPENDENCIES + inherited + local))
            dimensions = _dimensions(item)
            blueprint = ConsciousnessBlueprint(
                claim_id=item.claim_id,
                title=item.title,
                family=item.family,
                statement=item.statement,
                dependencies=dependencies,
                generation_rule="Generate the literal Cartesian product of all eight registered binary preservation dimensions before any external consciousness, cognitive, neural, behavioural or colour outcome is opened.",
                grammar_boundary="Exactly eight binary structural and evidential dimensions, giving 256 forms. The form closure is depth-independent under the stated positive-finite successor, while empirical correspondence remains source- and protocol-bound.",
                dimensions=dimensions,
                exact_result="__".join(row.admitted_choice.name for row in dimensions),
                induction_base="The least complete carrier retains the claimed roles, transition, record, evidence class and root provenance without an extra rule.",
                induction_step="Adding one lawful finite state, participant, content, observation or realizing component preserves every earlier identity, transition, adverse row and boundary and appends the new trace.",
                exclusions=("semantic numerical zero", "negative proof quantity", "irrational or imaginary proof value", "completed infinity", "ungenerated continuum", "free or fitted parameter", "target-selected survivor", "prior answer as premise", "report substituted for experience", "behaviour substituted for experience", "neural correlation substituted for experience", "language fluency or confidence substituted for experience", "opaque predictor", "erased adverse, absent or unresolved row"),
                operational_witnesses=_witnesses(item),
                experiment_id="SFT-EXP-" + item.claim_id.removeprefix("SFT-") + "-E1",
                predicted_observation_label="consciousness:" + item.carrier + "__" + item.distinction + "__" + item.operation + "__" + item.retained_record + "__" + item.evidence_boundary,
                falsification_condition="Reject if another generated form preserves every registered dimension, if a required structural witness fails, if purpose-matched evidence contradicts the sealed consequence, or if report, behaviour, biology, computation, physical measurement or public colour naming is substituted for phenomenal occurrence without a separately derived bridge.",
            )
            blueprint.validate()
            output.append(blueprint)
            previous_in_family = item.claim_id
        previous_family_terminal = family_rows[-1].claim_id
    return tuple(output)


CONSCIOUSNESS_BLUEPRINTS = _blueprints()
BLUEPRINT_BY_CLAIM = {item.claim_id: item for item in CONSCIOUSNESS_BLUEPRINTS}


def candidate_forms(blueprint: ConsciousnessBlueprint) -> tuple[tuple[str, ...], ...]:
    blueprint.validate()
    return tuple(tuple(choice.name for choice in choices) for choices in product(*(item.choices for item in blueprint.dimensions)))


def unique_survivor(blueprint: ConsciousnessBlueprint) -> tuple[str, ...]:
    admitted = tuple(item.admitted_choice.name for item in blueprint.dimensions)
    survivors = tuple(form for form in candidate_forms(blueprint) if form == admitted)
    if len(survivors) != 1:
        raise ValueError("Consciousness grammar did not produce one unique preserving form")
    return survivors[0]


def validate_blueprints() -> None:
    if len(CONSCIOUSNESS_BLUEPRINTS) != len(CONSCIOUSNESS_OBLIGATIONS):
        raise ValueError("Consciousness blueprint count differs from the frozen obligations")
    if len(BLUEPRINT_BY_CLAIM) != len(CONSCIOUSNESS_BLUEPRINTS):
        raise ValueError("Consciousness blueprint identities repeat")
    for blueprint in CONSCIOUSNESS_BLUEPRINTS:
        if len(candidate_forms(blueprint)) != 256:
            raise ValueError("Consciousness candidate census is incomplete")
        if "__".join(unique_survivor(blueprint)) != blueprint.exact_result:
            raise ValueError("Consciousness survivor reconstruction failed")


validate_blueprints()

