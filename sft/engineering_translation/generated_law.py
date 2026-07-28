"""Pre-source candidate grammar for Engineering Translation."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from sft.engineering_translation.obligations import ENGINEERING_OBLIGATIONS, FAMILY_ORDER, EngineeringObligation
from sft.engineering_translation.structural_model import structural_witnesses

BASE_DEPENDENCIES = (
    "SFT-FOUNDATION-ONE-001",
    "SFT-FOUNDATION-FOLD-001",
    "SFT-FOUNDATION-FOLD-DYNAMICS-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-OPTIMIZATION-001",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-INFO-QUANTITY-001",
    "SFT-INFO-CHANNEL-CAPACITY-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-COMP-SEM-CORRECTNESS-001",
    "SFT-COMP-SEM-COMPILATION-001",
    "SFT-COMP-DIST-CAUSALITY-001",
    "SFT-PHYS-MEAS-VALUE-RECORD-001",
    "SFT-PHYS-MEAS-CALIBRATION-001",
    "SFT-CHEM-MEAS-TRACEABILITY-001",
    "SFT-MAT-SUST-LIFECYCLE-001",
    "SFT-BIO-BIO-HANDOFF-001",
    "SFT-CONSC-RED-EMPIRICAL-BOUNDARY-001",
    "SFT-MED-CLINICAL-EVIDENCE-HANDOFF-001",
    "SFT-EARTH-HAZARD-RISK-HANDOFF-001",
    "SFT-ASTRO-ASTRO-HANDOFF-001",
    "SFT-SOCIAL-ENGINEERING-HANDOFF-001",
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
            raise ValueError("invalid Engineering dimension")
        if sum(self.required_property in x.properties for x in self.choices) != 1:
            raise ValueError("Engineering dimension lacks one preserving choice")


def dimension(key, rejected, rejection, preserving, preservation):
    property_name = "preserves-" + key
    return Dimension(
        key,
        property_name,
        (
            Choice(rejected, frozenset(), rejection),
            Choice(preserving, frozenset((property_name,)), preservation),
        ),
    )


@dataclass(frozen=True)
class EngineeringBlueprint:
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
        if not self.claim_id.startswith("SFT-ENG-") or len(self.dimensions) != 8:
            raise ValueError("invalid Engineering blueprint")
        for item in self.dimensions:
            item.validate()
        if not all(ok for _, _, ok in self.operational_witnesses):
            raise ValueError("Engineering witness failed")
        if self.exact_result != "__".join(x.name for x in unique_survivor(self)):
            raise ValueError("Engineering survivor changed")


def dimensions(obligation: EngineeringObligation):
    return (
        dimension("carrier", "answer-only-or-unversioned-artifact", "The artifact, user, purpose or version is erased.", obligation.carrier, "The claim-specific engineering carrier is retained."),
        dimension("boundary", "operating-test-or-lifecycle-boundary-erased", "A bounded implementation result is universalized.", obligation.evidence_boundary, "The operating, test, user and lifecycle boundary remains explicit."),
        dimension("relation", "target-fitted-status-or-application-selected-relation", "A desired outcome or application selects the relation.", obligation.relation, "Only generated relations and admitted upstream laws act."),
        dimension("record", "successful-output-only", "Requirements, versions, failures, uncertainty and rollback are erased.", obligation.retained_record, "The complete reconstructible engineering record is retained."),
        dimension("evidence", "law-design-test-simulation-demonstration-conflated", "Scientific law and implementation evidence substitute for one another.", "science-design-test-and-decision-classes-explicit", "Law, requirement, design, simulation, test, demonstration, performance and anomaly remain distinct."),
        dimension("provenance", "opaque-build-prior-output-or-authority-selected", "A hidden tool, prior output or authority selects the result.", "root-bound-forward-translation", "The trace begins at the One and names every admitted law and engineering choice."),
        dimension("generality", "single-platform-prototype-or-favourable-run-universalized", "One environment or run erases failures and portability limits.", "positive-finite-extension-preserves-platforms-failures-and-versions", "Every lawful finite extension retains platforms, versions, failures and boundaries."),
        dimension("extension", "free-weight-exception-or-silent-dependency", "A fitted weight, silent dependency or exception manufactures success.", "no-extra-rule", "No rule beyond the frozen specification is introduced."),
    )


def candidate_forms(blueprint):
    return tuple(tuple(x) for x in product(*(dimension_value.choices for dimension_value in blueprint.dimensions)))


def candidate_preserves(blueprint, form):
    return len(form) == 8 and all(d.required_property in c.properties for d, c in zip(blueprint.dimensions, form))


def unique_survivor(blueprint):
    survivors = tuple(form for form in candidate_forms(blueprint) if candidate_preserves(blueprint, form))
    if len(survivors) != 1:
        raise ValueError("Engineering grammar did not yield one survivor")
    return survivors[0]


def family_witness(family):
    witness = structural_witnesses()
    mapping = {
        FAMILY_ORDER[0]: witness["ordered_lifecycle"],
        FAMILY_ORDER[1]: witness["component_identity_retained"] and witness["directed_interface_retained"],
        FAMILY_ORDER[2]: witness["resource_account_closes"],
        FAMILY_ORDER[3]: witness["evidence_classes_distinct"],
        FAMILY_ORDER[4]: witness["three_alternatives_complete"],
        FAMILY_ORDER[5]: witness["feedback_recurrence"] and witness["merged_output_loses_unheld_predecessor"],
        FAMILY_ORDER[6]: witness["ordered_lifecycle"],
        FAMILY_ORDER[7]: witness["evidence_classes_distinct"],
        FAMILY_ORDER[8]: witness["cross_platform_count_positive_finite"],
        FAMILY_ORDER[9]: witness["ordered_lifecycle"] and witness["resource_account_closes"],
        FAMILY_ORDER[10]: witness["evidence_classes_distinct"],
        FAMILY_ORDER[11]: witness["component_identity_retained"],
    }
    return mapping[family]


def build():
    output = []
    previous_family_terminal = None
    for family in FAMILY_ORDER:
        rows = [x for x in ENGINEERING_OBLIGATIONS if x.family == family]
        previous_local = None
        for obligation in rows:
            dependencies = tuple(dict.fromkeys(BASE_DEPENDENCIES + (() if previous_family_terminal is None else (previous_family_terminal,)) + (() if previous_local is None else (previous_local,))))
            blueprint = EngineeringBlueprint(
                obligation.claim_id,
                obligation.title,
                obligation.family,
                obligation.statement,
                dependencies,
                "Generate the literal Cartesian product of eight preregistered binary carrier, boundary, relation, record, evidence, provenance, generality and extension dimensions before external standards, products, tests or outcomes are opened; filter only by registered preservation properties.",
                "Exactly eight binary dimensions: 256 forms. Structural closure is depth-independent for positive finite components, versions, platforms, tests and lifecycle records; performance remains artifact, environment, user, method and operating-boundary limited.",
                dimensions(obligation),
                "",
                "The least translation retains one admitted law or requirement, one versioned artifact, one declared boundary, one testable relation and its complete record.",
                "Adding one lawful finite component, interface, platform, requirement, test, failure, lifecycle stage or anomaly preserves every earlier identity, unfavorable row and receipt while appending its trace.",
                (
                    "semantic numerical zero",
                    "negative proof quantity",
                    "irrational or imaginary proof value",
                    "completed infinity",
                    "ungenerated continuum",
                    "free or fitted parameter",
                    "target-selected design law",
                    "application-selected scientific law",
                    "successful performance as retroactive law proof",
                    "failed implementation as automatic law falsification",
                    "simulation relabelled observation",
                    "demonstration relabelled verification or validation",
                    "single-platform success relabelled portability",
                    "hidden dependency, skipped stage or opaque oracle",
                ),
                (
                    ("carrier", "carrier nonempty", bool(obligation.carrier)),
                    ("boundary", "boundary differs from carrier", obligation.evidence_boundary != obligation.carrier),
                    ("relation", "relation differs from record", obligation.relation != obligation.retained_record),
                    ("fold", "family witness reproduces", family_witness(obligation.family)),
                ),
                "SFT-EXP-" + obligation.claim_id.removeprefix("SFT-") + "-E1",
                "engineering:" + "__".join((obligation.carrier, obligation.relation, obligation.retained_record, obligation.evidence_boundary)),
                obligation.falsification_condition,
            )
            blueprint = EngineeringBlueprint(**{**blueprint.__dict__, "exact_result": "__".join(choice.name for choice in unique_survivor(blueprint))})
            blueprint.validate()
            output.append(blueprint)
            previous_local = obligation.claim_id
        previous_family_terminal = rows[-1].claim_id
    return tuple(output)


ENGINEERING_BLUEPRINTS = build()
BLUEPRINT_BY_CLAIM = {x.claim_id: x for x in ENGINEERING_BLUEPRINTS}
if len(ENGINEERING_BLUEPRINTS) != 72 or len(BLUEPRINT_BY_CLAIM) != 72:
    raise ValueError("Engineering blueprint census failed")
if any(len(candidate_forms(x)) != 256 for x in ENGINEERING_BLUEPRINTS):
    raise ValueError("Engineering candidate census failed")
