"""Pre-source generated candidate grammar for the Earth foundation."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from sft.earth_environment.obligations import EARTH_ENVIRONMENT_OBLIGATIONS, FAMILY_ORDER, EarthEnvironmentObligation
from sft.earth_environment.structural_model import structural_witnesses


BASE_DEPENDENCIES = (
    "SFT-FOUNDATION-ONE-001",
    "SFT-FOUNDATION-FOLD-001",
    "SFT-FOUNDATION-FOLD-DYNAMICS-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-PROBABILITY-STATISTICS-001",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-MATH-CATEGORY-TYPE-COMPOSITION-001",
    "SFT-INFO-QUANTITY-001",
    "SFT-INFO-ENTROPY-UNCERTAINTY-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-COMP-FORM-COMPOSITION-001",
    "SFT-PHYS-MEAS-OBSERVATION-CARRIER-001",
    "SFT-PHYS-MEAS-UNCERTAINTY-001",
    "SFT-PHYS-MECH-CONSERVATION-001",
    "SFT-PHYS-THERMO-FIRST-LAW-001",
    "SFT-PHYS-THERMO-SECOND-LAW-001",
    "SFT-PHYS-FLUID-CONSERVATION-001",
    "SFT-PHYS-WAVE-PROPAGATION-001",
    "SFT-CHEM-MEAS-SUBSTANCE-001",
    "SFT-CHEM-STOICH-CONSERVATION-001",
    "SFT-CHEM-PHASE-CHEMICAL-001",
    "SFT-MAT-MEAS-MATERIAL-001",
    "SFT-MAT-MEAS-PROPERTY-001",
    "SFT-MAT-THERM-CONDUCTION-001",
    "SFT-BIO-ECOSYSTEM-001",
    "SFT-BIO-BIO-HANDOFF-001",
)


@dataclass(frozen=True)
class EarthChoice:
    name: str
    properties: frozenset[str]
    explanation: str


@dataclass(frozen=True)
class EarthDimension:
    key: str
    required_property: str
    choices: tuple[EarthChoice, EarthChoice]

    def validate(self) -> None:
        if len(self.choices) != 2:
            raise ValueError("an Earth dimension must have two exhaustive registered forms")
        if len({choice.name for choice in self.choices}) != 2:
            raise ValueError("an Earth dimension repeats a form")
        if sum(self.required_property in choice.properties for choice in self.choices) != 1:
            raise ValueError("an Earth dimension must have exactly one structurally preserving form")


def dimension(key: str, rejected: str, rejection: str, preserving: str, preservation: str) -> EarthDimension:
    required = "preserves-" + key
    return EarthDimension(
        key,
        required,
        (
            EarthChoice(rejected, frozenset(), rejection),
            EarthChoice(preserving, frozenset((required,)), preservation),
        ),
    )


@dataclass(frozen=True)
class EarthBlueprint:
    claim_id: str
    title: str
    family: str
    statement: str
    dependencies: tuple[str, ...]
    generation_rule: str
    grammar_boundary: str
    dimensions: tuple[EarthDimension, ...]
    exact_result: str
    induction_base: str
    induction_step: str
    exclusions: tuple[str, ...]
    operational_witnesses: tuple[tuple[str, str, bool], ...]
    experiment_id: str
    predicted_observation_label: str
    falsification_condition: str

    def validate(self) -> None:
        if not self.claim_id.startswith("SFT-EARTH-") or not self.experiment_id.startswith("SFT-EXP-EARTH-"):
            raise ValueError("Earth claim identity is invalid")
        if not self.dependencies or len(self.dimensions) != 8:
            raise ValueError("Earth claim lacks dependencies or eight dimensions")
        if len({item.key for item in self.dimensions}) != 8:
            raise ValueError("Earth dimensions repeat")
        for item in self.dimensions:
            item.validate()
        if not all(passed for _, _, passed in self.operational_witnesses):
            raise ValueError("an Earth operational witness failed")
        if self.exact_result != "__".join(choice.name for choice in unique_survivor(self)):
            raise ValueError("the registered Earth result differs from the independently filtered preserving form")


def _dimensions(item: EarthEnvironmentObligation) -> tuple[EarthDimension, ...]:
    return (
        dimension("carrier", "answer-only-or-unbounded-carrier", "An answer-only value or unbounded object erases the Earth carrier.", item.carrier, "The complete claim-specific carrier is retained."),
        dimension("boundary", "boundary-or-interface-erased", "Erasing the spatial, temporal or categorical boundary makes stocks, flows and observations incomparable.", item.evidence_boundary, "The exact observation and system boundary remains explicit."),
        dimension("relation", "imported-fitted-or-missing-relation", "An imported, fitted or absent relation can manufacture the intended Earth result.", item.relation, "Only generated Fold relations and admitted upstream dependencies act."),
        dimension("record", "favourable-output-with-incomplete-record", "A favorable output without stocks, transfers, time, missing and adverse records is not reconstructible.", item.retained_record, "The complete required record is retained."),
        dimension("evidence", "model-proxy-forecast-or-observation-conflated", "Earth evidence classes cannot silently substitute for one another.", "evidence-class-explicit", "Direct observation, retrieval, proxy, reconstruction, model and forecast remain distinguishable."),
        dimension("provenance", "prior-target-consensus-or-application-selected", "Earlier SFT answers, target values and consensus models cannot select a V3 law.", "root-bound-forward-forcing", "Every result traces through admitted dependencies to There Is No Nothing."),
        dimension("generality", "one-favourable-case-with-erased-alternatives", "One favorable site, event or interval cannot close a generated class.", "positive-finite-successor-retains-all-rows", "Every supplied finite extension retains favorable, adverse, absent and unresolved rows."),
        dimension("extension", "free-parameter-exception-or-opaque-oracle", "Fitting, exceptions and opaque predictors can force a preferred answer.", "no-extra-rule", "No rule beyond the admitted dependencies and registered preservation conditions is added."),
    )


def candidate_forms(blueprint: EarthBlueprint) -> tuple[tuple[EarthChoice, ...], ...]:
    return tuple(tuple(form) for form in product(*(item.choices for item in blueprint.dimensions)))


def candidate_preserves(blueprint: EarthBlueprint, form: tuple[EarthChoice, ...]) -> bool:
    if len(form) != len(blueprint.dimensions):
        return False
    return all(dimension.required_property in choice.properties for dimension, choice in zip(blueprint.dimensions, form))


def unique_survivor(blueprint: EarthBlueprint) -> tuple[EarthChoice, ...]:
    survivors = tuple(form for form in candidate_forms(blueprint) if candidate_preserves(blueprint, form))
    if len(survivors) != 1:
        raise ValueError("Earth grammar did not produce one unique preserving form")
    return survivors[0]


def _family_witness(family: str) -> bool:
    exact = structural_witnesses()
    return {
        FAMILY_ORDER[0]: exact["observation_statuses_remain_distinct"],
        FAMILY_ORDER[1]: exact["reservoir_partition_closes"] and exact["boundary_transfer_is_two_sided"],
        FAMILY_ORDER[2]: exact["layers_are_positive_and_ordered"],
        FAMILY_ORDER[3]: exact["layers_are_positive_and_ordered"] and exact["boundary_transfer_is_two_sided"],
        FAMILY_ORDER[4]: exact["unit_exponent_is_uniquely_enumerated"],
        FAMILY_ORDER[5]: exact["complementary_cycle_recurs"] and exact["reservoir_partition_closes"],
        FAMILY_ORDER[6]: exact["bounded_cavity_has_distinct_modes"],
        FAMILY_ORDER[7]: exact["coupled_cycle_recurs_and_closes"],
        FAMILY_ORDER[8]: exact["tipping_basins_share_image_without_physical_assignment"],
        FAMILY_ORDER[9]: exact["coupled_cycle_recurs_and_closes"],
        FAMILY_ORDER[10]: exact["boundary_transfer_is_two_sided"],
        FAMILY_ORDER[11]: exact["observation_statuses_remain_distinct"],
    }[family]


def _predicted_label(item: EarthEnvironmentObligation) -> str:
    base = "earth:" + "__".join((item.carrier, item.relation, item.retained_record, item.evidence_boundary))
    additions = {
        "SFT-EARTH-QUAKE-MAGNITUDE-FREQUENCY-001": "__exact-unit-exponent-presealed",
        "SFT-EARTH-EARTH-IONOSPHERE-RESONANCE-001": "__bounded-discrete-modes-dimensional-frequency-measured",
        "SFT-EARTH-EARTH-SYSTEM-TIPPING-001": "__two-basin-structure-no-universal-physical-half-threshold",
    }
    return base + additions.get(item.claim_id, "")


def _blueprints() -> tuple[EarthBlueprint, ...]:
    output: list[EarthBlueprint] = []
    previous_family_terminal: str | None = None
    for family in FAMILY_ORDER:
        rows = [row for row in EARTH_ENVIRONMENT_OBLIGATIONS if row.family == family]
        previous_in_family: str | None = None
        for item in rows:
            local = () if previous_in_family is None else (previous_in_family,)
            inherited = () if previous_family_terminal is None else (previous_family_terminal,)
            dependencies = tuple(dict.fromkeys(BASE_DEPENDENCIES + inherited + local))
            dimensions = _dimensions(item)
            provisional = EarthBlueprint(
                claim_id=item.claim_id,
                title=item.title,
                family=item.family,
                statement=item.statement,
                dependencies=dependencies,
                generation_rule="Generate the literal Cartesian product of eight registered binary carrier, boundary, relation, record, evidence, provenance, generality and extension dimensions before external Earth-source identities or outcomes are opened. Filter only by the preregistered property required by each dimension.",
                grammar_boundary="Exactly eight binary preservation dimensions, giving 256 forms. Form closure is depth-independent under the stated positive-finite successor; empirical correspondence remains source, place, time, method and protocol bounded.",
                dimensions=dimensions,
                exact_result="",
                induction_base="The least complete Earth carrier retains its boundary, relation, record, evidence class and root provenance without an extra rule.",
                induction_step="Adding one lawful finite reservoir, interface, observation, event, time, species or location preserves all earlier identities, transfers, adverse rows and boundaries and appends the new trace.",
                exclusions=("semantic numerical zero", "negative proof quantity", "irrational or imaginary proof value", "completed infinity", "ungenerated continuum", "free or fitted parameter", "target-selected survivor", "prior answer as premise", "conventional Earth model as premise", "proxy or retrieval relabelled as direct observation", "model or forecast relabelled as observation", "opaque predictor as law", "erased adverse, absent, censored, missing or unresolved row"),
                operational_witnesses=(
                    ("carrier-present", "the claim retains a nonempty named carrier", bool(item.carrier.strip())),
                    ("relation-distinct", "the carrier and relation are not silently conflated", item.carrier != item.relation),
                    ("evidence-boundary", "the evidence boundary remains distinct from the result carrier", item.evidence_boundary != item.carrier),
                    ("exact-fold-witness", "the family's pre-source exact Fold construction reproduces", _family_witness(item.family)),
                ),
                experiment_id="SFT-EXP-" + item.claim_id.removeprefix("SFT-") + "-E1",
                predicted_observation_label=_predicted_label(item),
                falsification_condition=item.falsification_condition,
            )
            exact_result = "__".join(choice.name for choice in unique_survivor(provisional))
            blueprint = EarthBlueprint(**{**provisional.__dict__, "exact_result": exact_result})
            blueprint.validate()
            output.append(blueprint)
            previous_in_family = item.claim_id
        previous_family_terminal = rows[-1].claim_id
    return tuple(output)


EARTH_BLUEPRINTS = _blueprints()
BLUEPRINT_BY_CLAIM = {item.claim_id: item for item in EARTH_BLUEPRINTS}


def validate_blueprints() -> None:
    if len(EARTH_BLUEPRINTS) != len(EARTH_ENVIRONMENT_OBLIGATIONS):
        raise ValueError("Earth blueprint count differs from the frozen obligations")
    if len(BLUEPRINT_BY_CLAIM) != len(EARTH_BLUEPRINTS):
        raise ValueError("Earth blueprint identities repeat")
    for blueprint in EARTH_BLUEPRINTS:
        if len(candidate_forms(blueprint)) != 256:
            raise ValueError("Earth candidate census is incomplete")
        if not candidate_preserves(blueprint, unique_survivor(blueprint)):
            raise ValueError("Earth survivor reconstruction failed")


validate_blueprints()


__all__ = (
    "BASE_DEPENDENCIES", "EarthChoice", "EarthDimension", "EarthBlueprint",
    "EARTH_BLUEPRINTS", "BLUEPRINT_BY_CLAIM", "candidate_forms",
    "candidate_preserves", "unique_survivor", "validate_blueprints",
)
