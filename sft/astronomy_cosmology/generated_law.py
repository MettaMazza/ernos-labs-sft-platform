"""Pre-source candidate grammar for the Astronomy and Cosmology foundation."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from sft.astronomy_cosmology.obligations import ASTRONOMY_OBLIGATIONS, FAMILY_ORDER, AstronomyObligation
from sft.astronomy_cosmology.structural_model import structural_witnesses


BASE_DEPENDENCIES = (
    "SFT-FOUNDATION-ONE-001", "SFT-FOUNDATION-FOLD-001", "SFT-FOUNDATION-FOLD-DYNAMICS-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-GRAPH-NETWORK-001", "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-PROBABILITY-STATISTICS-001", "SFT-MATH-DYNAMICAL-SYSTEMS-001", "SFT-MATH-LOGIC-PROOF-001",
    "SFT-INFO-QUANTITY-001", "SFT-INFO-ENTROPY-UNCERTAINTY-001", "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-PHYS-MEAS-OBSERVATION-CARRIER-001",
    "SFT-PHYS-MEAS-UNCERTAINTY-001", "SFT-PHYS-WAVE-PROPAGATION-001", "SFT-PHYS-COSMO-REDSHIFT-001",
    "SFT-PHYS-COSMO-DISTANCE-001", "SFT-PHYS-COSMO-EXPANSION-001", "SFT-PHYS-COSMO-STRUCTURE-GROWTH-001",
    "SFT-PHYS-COSMO-BACKGROUND-001", "SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001",
    "SFT-PHYS-GRAVITY-WAVE-001", "SFT-PHYS-GRAVITY-HORIZON-001",
    "SFT-PHYS-STELLAR-GALACTIC-TIDAL-TERMINAL-067", "SFT-PHYS-STELLAR-NUCLEAR-COLLAPSE-TERMINAL-069",
    "SFT-PHYS-COMPACT-HORIZON-THERMODYNAMICS-TERMINAL-071", "SFT-CHEM-ELEM-ELEMENT-001",
    "SFT-CHEM-STOICH-CONSERVATION-001", "SFT-EARTH-HAZARD-RISK-HANDOFF-001",
)


@dataclass(frozen=True)
class Choice:
    name: str
    properties: frozenset[str]
    explanation: str


@dataclass(frozen=True)
class Dimension:
    key: str
    required_property: str
    choices: tuple[Choice, Choice]

    def validate(self) -> None:
        if len(self.choices) != 2 or len({x.name for x in self.choices}) != 2:
            raise ValueError("Astronomy dimension is not a binary exhaustive registration")
        if sum(self.required_property in x.properties for x in self.choices) != 1:
            raise ValueError("Astronomy dimension does not have one preserving form")


def dimension(key: str, rejected: str, rejection: str, preserving: str, preservation: str) -> Dimension:
    prop = "preserves-" + key
    return Dimension(key, prop, (Choice(rejected, frozenset(), rejection), Choice(preserving, frozenset((prop,)), preservation)))


@dataclass(frozen=True)
class AstronomyBlueprint:
    claim_id: str
    title: str
    family: str
    statement: str
    dependencies: tuple[str, ...]
    generation_rule: str
    grammar_boundary: str
    dimensions: tuple[Dimension, ...]
    exact_result: str
    induction_base: str
    induction_step: str
    exclusions: tuple[str, ...]
    operational_witnesses: tuple[tuple[str, str, bool], ...]
    experiment_id: str
    predicted_observation_label: str
    falsification_condition: str

    def validate(self) -> None:
        if not self.claim_id.startswith("SFT-ASTRO-") or len(self.dimensions) != 8:
            raise ValueError("Astronomy blueprint identity or arity is invalid")
        for item in self.dimensions:
            item.validate()
        if not all(ok for _, _, ok in self.operational_witnesses):
            raise ValueError("Astronomy operational witness failed")
        if self.exact_result != "__".join(x.name for x in unique_survivor(self)):
            raise ValueError("Astronomy registered result differs from reconstructed survivor")


def dimensions(item: AstronomyObligation) -> tuple[Dimension, ...]:
    return (
        dimension("carrier", "answer-only-or-unbounded-carrier", "The astronomical carrier is erased.", item.carrier, "The claim-specific carrier is retained."),
        dimension("boundary", "frame-time-or-selection-erased", "Unbounded observations cannot be compared.", item.evidence_boundary, "The exact observational boundary is explicit."),
        dimension("relation", "imported-fitted-or-missing-relation", "A target or consensus model selects the result.", item.relation, "Only generated relations and admitted dependencies act."),
        dimension("record", "favourable-output-incomplete-record", "A favorable answer without source and adverse records is unreconstructible.", item.retained_record, "The complete required record is held."),
        dimension("evidence", "observation-model-forecast-conflated", "Evidence classes silently substitute for one another.", "evidence-class-explicit", "Direct, retrieval, proxy, reconstruction, model, forecast and missing remain distinct."),
        dimension("provenance", "prior-answer-or-target-selected", "Historical SFT or measurement selects the law.", "root-bound-forward-forcing", "The result traces through admitted dependencies to There Is No Nothing."),
        dimension("generality", "one-favourable-object-erases-population", "One object cannot close a generated class.", "positive-finite-extension-retains-all-rows", "Every finite extension retains favorable, adverse, absent and unresolved rows."),
        dimension("extension", "free-parameter-exception-or-opaque-oracle", "An added choice manufactures the result.", "no-extra-rule", "No rule beyond the registered structure is introduced."),
    )


def candidate_forms(bp: AstronomyBlueprint) -> tuple[tuple[Choice, ...], ...]:
    return tuple(tuple(x) for x in product(*(d.choices for d in bp.dimensions)))


def candidate_preserves(bp: AstronomyBlueprint, form: tuple[Choice, ...]) -> bool:
    return len(form) == 8 and all(d.required_property in c.properties for d, c in zip(bp.dimensions, form))


def unique_survivor(bp: AstronomyBlueprint) -> tuple[Choice, ...]:
    rows = tuple(x for x in candidate_forms(bp) if candidate_preserves(bp, x))
    if len(rows) != 1:
        raise ValueError("Astronomy grammar did not yield exactly one preserving form")
    return rows[0]


def family_witness(family: str) -> bool:
    w = structural_witnesses()
    mapping = {
        FAMILY_ORDER[0]: w["source_path_observer_ordered"],
        FAMILY_ORDER[1]: w["evidence_classes_distinct"],
        FAMILY_ORDER[2]: w["period_two_recurs"],
        FAMILY_ORDER[3]: w["positive_ordered_history"],
        FAMILY_ORDER[4]: w["period_three_recurs"],
        FAMILY_ORDER[5]: w["period_three_partitions_one"],
        FAMILY_ORDER[6]: w["joint_population_product"] and w["rank_four_unique_in_registered_dimension_successor"],
        FAMILY_ORDER[7]: w["observation_never_recovers_unheld_predecessor"],
        FAMILY_ORDER[8]: w["positive_ordered_history"],
        FAMILY_ORDER[9]: w["period_three_partitions_one"],
        FAMILY_ORDER[10]: w["observation_never_recovers_unheld_predecessor"],
        FAMILY_ORDER[11]: w["evidence_classes_distinct"],
    }
    return mapping[family]


def build() -> tuple[AstronomyBlueprint, ...]:
    output: list[AstronomyBlueprint] = []
    family_terminal = None
    for family in FAMILY_ORDER:
        rows = [x for x in ASTRONOMY_OBLIGATIONS if x.family == family]
        local = None
        for item in rows:
            deps = tuple(dict.fromkeys(BASE_DEPENDENCIES + (() if family_terminal is None else (family_terminal,)) + (() if local is None else (local,))))
            bp = AstronomyBlueprint(
                item.claim_id, item.title, item.family, item.statement, deps,
                "Generate the literal Cartesian product of eight preregistered binary carrier, boundary, relation, record, evidence, provenance, generality and extension dimensions before external source identities or outcomes are opened; filter only by the registered preservation properties.",
                "Exactly eight binary dimensions: 256 forms. Closure is depth-independent for positive finite extension; empirical correspondence remains source, object, place, epoch, instrument and protocol bounded.",
                dimensions(item), "",
                "The least complete astronomical carrier retains source, path, observer, frame, relation, evidence class and root provenance.",
                "Adding one lawful finite source, epoch, channel, object or population member preserves all earlier identities, adverse rows and boundaries and appends its trace.",
                ("semantic numerical zero", "negative proof quantity", "irrational or imaginary proof value", "completed infinity", "ungenerated continuum", "free or fitted parameter", "target-selected survivor", "prior answer as premise", "consensus cosmology as premise", "model relabelled observation", "non-detection relabelled zero", "erased adverse or unresolved row"),
                (("carrier", "named carrier is nonempty", bool(item.carrier)), ("relation", "carrier and relation differ", item.carrier != item.relation), ("boundary", "boundary differs from carrier", item.evidence_boundary != item.carrier), ("fold", "family exact Fold witness reproduces", family_witness(item.family))),
                "SFT-EXP-" + item.claim_id.removeprefix("SFT-") + "-E1",
                "astronomy:" + "__".join((item.carrier, item.relation, item.retained_record, item.evidence_boundary)) + ("__exact-rank-four-presealed" if item.claim_id == "SFT-ASTRO-TULLY-FISHER-001" else ""),
                item.falsification_condition,
            )
            bp = AstronomyBlueprint(**{**bp.__dict__, "exact_result": "__".join(x.name for x in unique_survivor(bp))})
            bp.validate(); output.append(bp); local = item.claim_id
        family_terminal = rows[-1].claim_id
    return tuple(output)


ASTRONOMY_BLUEPRINTS = build()
BLUEPRINT_BY_CLAIM = {x.claim_id: x for x in ASTRONOMY_BLUEPRINTS}
if len(ASTRONOMY_BLUEPRINTS) != 72 or len(BLUEPRINT_BY_CLAIM) != 72 or any(len(candidate_forms(x)) != 256 for x in ASTRONOMY_BLUEPRINTS):
    raise ValueError("Astronomy blueprint census failed")

__all__ = ("BASE_DEPENDENCIES", "AstronomyBlueprint", "ASTRONOMY_BLUEPRINTS", "BLUEPRINT_BY_CLAIM", "candidate_forms", "candidate_preserves", "unique_survivor")
