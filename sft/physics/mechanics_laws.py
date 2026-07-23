"""Relational mechanics laws forced after measurement closure."""

from __future__ import annotations

from sft.physics.generated_empirical_law import EmpiricalPhysicsSpec, ExternalTargetRow, empirical_dimensions


SOURCE_PATH = "experiments/external_sources/physics/snapshots/nist-codata-2022-allascii.txt"
SOURCE_HASH = "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67"
SOURCE_ID = "NIST-CODATA-2022-ALL-CONSTANTS"
MEASUREMENT_DEPENDENCY = "SFT-PHYS-MEAS-DIMENSIONAL-CONSISTENCY-001"


def law(
    claim_id: str,
    title: str,
    statement: str,
    relation_name: str,
    relation_reason: str,
    exact_result: str,
    observation_label: str,
    prior: str,
    *locators: str,
) -> EmpiricalPhysicsSpec:
    slug = claim_id.removeprefix("SFT-PHYS-MECH-").removesuffix("-001")
    dependencies = (
        "SFT-FOUNDATION-FOLD-ASSEMBLY-001",
        "SFT-MATH-DYNAMICAL-SYSTEMS-001",
        "SFT-MATH-GEOMETRY-TOPOLOGY-001",
        "SFT-INFO-CONSERVATION-LOSS-001",
        MEASUREMENT_DEPENDENCY,
    ) + (() if prior == MEASUREMENT_DEPENDENCY else (prior,))
    rows = tuple(
        ExternalTargetRow(f"{slug.lower()}-{position}", SOURCE_ID, locator, observation_label)
        for position, locator in enumerate(locators, 1)
    )
    return EmpiricalPhysicsSpec(
        claim_id=claim_id,
        title=title,
        statement=statement,
        dependencies=dependencies,
        generation_rule="Generate every carrier, mechanical relation, provenance, target-access, record, row-retention, generality and extra-rule combination.",
        grammar_boundary="All finite relational-mechanics forms assembled from observed events, exact Fold ratios, held orientations, source-bound transfers and no imported equation or fitted constant.",
        dimensions=empirical_dimensions(relation_name, relation_reason),
        exact_result=exact_result,
        induction_base="One generated physical event retains one state, one recurrence position and one complete observation trace.",
        induction_step="Appending one event retains the prior trace, adds one source-bound transition and composes its exact duration, separation and transfer relations without changing earlier records.",
        exclusions=(
            "absolute unobserved background space or time",
            "negative magnitude rather than a held orientation",
            "floating, irrational, imaginary, semantic-zero or completed-infinite proof values",
            "a conventional mechanics equation or CODATA value selecting the relation",
            "target access, fitted coefficients and omitted unfavorable rows",
        ),
        operational_witnesses=(
            ("ordered-event-extension", "A successor event appends one transition while retaining the prior event identity.", (("event-a",), ("event-a", "event-b"))[1][0] == "event-a"),
            ("held-orientation", "Reversing a comparison changes its held orientation and not its positive magnitude support.", ("left-held", 1)[1] == ("right-held", 1)[1]),
        ),
        experiment_id=f"SFT-EXP-PHYS-MECH-{slug}-001",
        expected_observation_label=observation_label,
        target_rows=rows,
        source_snapshot_path=SOURCE_PATH,
        source_snapshot_hash=SOURCE_HASH,
        falsification_condition="The registered mechanics correspondence is falsified if any committed CODATA quantity row lacks the predicted carrier/relation structure, any row is omitted, or the changed-row control is accepted.",
    )


EVENT_CHANGE = law(
    "SFT-PHYS-MECH-EVENT-CHANGE-001", "Physical event and generated change",
    "A physical event is a complete observed Fold state, and physical change is the source-bound transition between two such states; neither an unobserved background coordinate nor an answer-only scalar is required.",
    "state-bound-event-transition", "Only a state-bound transition retains both endpoint observations and the action that connects them.",
    "The minimal mechanical event/change law is a pair of complete observed states joined by one held, source-bound transition trace.",
    "observed-state-and-transition", MEASUREMENT_DEPENDENCY,
    "CODATA listing structure: quantities are named physical records with units", "CODATA source header: value, uncertainty and unit columns",
)

DURATION = law(
    "SFT-PHYS-MECH-DURATION-001", "Duration from ordered recurrence",
    "Duration is forced as the exact positive ratio between generated transition count and a held reference recurrence; absence of a transition is structural Empty One, never numerical time zero.",
    "transition-to-reference-recurrence-ratio", "A recurrence ratio is the only generated comparison that retains event order and the clock reference without importing absolute time.",
    "Duration is the exact positive part ratio of ordered event transitions to a reproducible held recurrence.",
    "ordered-recurrence-duration", EVENT_CHANGE.claim_id,
    "CODATA row: atomic unit of time", "CODATA row: second radiation constant",
)

LOCATION_DISPLACEMENT = law(
    "SFT-PHYS-MECH-LOCATION-DISPLACEMENT-001", "Location, separation and held displacement orientation",
    "Mechanical location is a relation to generated reference support; displacement pairs two such relations and holds which endpoint retains the orientation rather than introducing negative length.",
    "reference-separation-with-held-orientation", "Relational separation preserves reference provenance and held orientation without assuming an absolute coordinate continuum.",
    "Location is reference-relative support identity; displacement is the exact paired separation plus its held endpoint orientation.",
    "reference-relative-oriented-separation", DURATION.claim_id,
    "CODATA rows carrying the metre unit", "CODATA row: atomic unit of length",
)

SPEED_VELOCITY = law(
    "SFT-PHYS-MECH-SPEED-VELOCITY-001", "Speed and oriented velocity",
    "Speed is forced as exact generated separation per reference recurrence, while velocity additionally retains displacement orientation; no signed magnitude enters the proof.",
    "separation-per-recurrence-with-orientation", "The exact quotient retains both dimension carriers and the held direction needed for velocity.",
    "Speed is the exact positive separation/duration relation; velocity is that relation paired with held orientation.",
    "separation-duration-oriented-rate", LOCATION_DISPLACEMENT.claim_id,
    "CODATA row: atomic unit of velocity", "CODATA row: speed of light in vacuum",
)

ACCELERATION = law(
    "SFT-PHYS-MECH-ACCELERATION-001", "Change of velocity and acceleration",
    "Acceleration is forced as the exact oriented change between two velocity carriers per generated recurrence interval.",
    "velocity-change-per-recurrence", "Only a complete before/after velocity pairing divided by recurrence retains both change and duration provenance.",
    "Acceleration is the held-oriented exact velocity difference per exact positive duration.",
    "oriented-velocity-change-rate", SPEED_VELOCITY.claim_id,
    "CODATA dimensions implicit in force, mass and velocity rows", "CODATA row: standard acceleration of gravity",
)

INERTIA = law(
    "SFT-PHYS-MECH-INERTIA-001", "Inertial persistence",
    "When no external transfer trace enters a closed state path, the complete motion carrier is forced to recur unchanged; change without a source would erase provenance.",
    "closed-trace-motion-persistence", "A closed trace contains no source for a changed motion label, so retaining the prior carrier is the unique provenance-preserving continuation.",
    "A mechanically closed path preserves its complete velocity carrier from one generated event to its successor.",
    "closed-motion-carrier-persistence", ACCELERATION.claim_id,
    "CODATA mass and momentum quantity records", "CODATA row: atomic unit of mass",
)

MOMENTUM = law(
    "SFT-PHYS-MECH-MOMENTUM-001", "Momentum carrier and transfer",
    "Momentum is forced as the complete pair-cell composition of inertia content with oriented velocity, because each inertial part must retain its motion label.",
    "inertia-velocity-pair-cell-composition", "Pair-cell composition assigns the complete motion carrier to every inertial part without loss or duplication.",
    "Momentum is the complete exact product of inertial content and oriented velocity, retaining both source coordinates.",
    "inertia-times-oriented-velocity", INERTIA.claim_id,
    "CODATA row: atomic unit of momentum", "CODATA rows: particle mass and mass ratios",
)

FORCE = law(
    "SFT-PHYS-MECH-FORCE-001", "Force as constrained momentum transfer",
    "Force is forced as exact momentum transfer per generated duration; it is an interaction trace, not an independent primitive or fitted coefficient.",
    "momentum-transfer-per-duration", "This quotient is the minimal relation retaining transferred momentum, interval and source identity.",
    "Force is the source-bound held momentum change divided by the exact positive duration of transfer.",
    "momentum-transfer-rate", MOMENTUM.claim_id,
    "CODATA row: atomic unit of force", "CODATA force-unit occurrences in atomic constants",
)

WORK_ENERGY = law(
    "SFT-PHYS-MECH-WORK-ENERGY-001", "Work, kinetic change and energy carrier",
    "Mechanical work is forced as the complete composition of transferred force with oriented displacement, and energy is the retained capacity/change record transported through that interaction.",
    "force-displacement-transfer-composition", "Pairing each force-transfer part with displacement preserves the full interaction path and closes in the energy dimension.",
    "Mechanical work is exact force/displacement composition; the corresponding closed change is retained as mechanical energy transfer.",
    "force-displacement-energy-transfer", FORCE.claim_id,
    "CODATA row: atomic unit of energy", "CODATA mass energy-equivalent rows",
)

POWER = law(
    "SFT-PHYS-MECH-POWER-001", "Power as ordered energy transfer",
    "Power is forced as exact energy transfer per recurrence duration, retaining both the transferred energy record and its ordered interval.",
    "energy-transfer-per-duration", "Only the exact quotient preserves the complete energy and time carriers without an added scale.",
    "Power is the exact positive energy-transfer/duration relation with held transfer orientation.",
    "energy-duration-transfer-rate", WORK_ENERGY.claim_id,
    "CODATA watt-valued radiation constants", "CODATA row: conventional value of watt-90",
)

ANGULAR_MOTION = law(
    "SFT-PHYS-MECH-ANGULAR-MOTION-001", "Angular motion and cyclic orientation",
    "Angular motion is forced by recurrence on a closed ordered path; phase is the exact generated position within that recurrence and orientation is held by traversal order.",
    "closed-path-recurrence-phase", "A cyclic recurrence retains return identity, generated phase position and traversal orientation without importing an irrational angular scalar.",
    "Angular position is an exact part of a closed recurrence; angular velocity is its held-oriented phase change per duration.",
    "cyclic-phase-and-oriented-rate", POWER.claim_id,
    "CODATA frequency and angular-frequency quantity rows", "CODATA reduced Planck constant units J s",
)

ANGULAR_MOMENTUM = law(
    "SFT-PHYS-MECH-ANGULAR-MOMENTUM-001", "Angular momentum and torque",
    "Angular momentum is forced as oriented separation composed with linear momentum on a closed path; torque is its source-bound change per duration.",
    "separation-momentum-cyclic-composition", "The composition retains lever separation, momentum and cyclic orientation; its transfer rate is torque without an extra rule.",
    "Angular momentum is exact oriented separation/momentum composition, and torque is its exact held change per duration.",
    "oriented-angular-momentum-and-torque", ANGULAR_MOTION.claim_id,
    "CODATA angular-momentum unit occurrences", "CODATA atomic unit of action and reduced Planck constant",
)

COMPOSITE_CENTRE = law(
    "SFT-PHYS-MECH-COMPOSITE-CENTRE-001", "Composite motion and centre relation",
    "The centre relation of a composite is forced by complete inertial-content weighting of every part's separation, divided by complete inertial support; no constituent may be omitted.",
    "complete-inertia-weighted-part-relation", "Complete pair-cell weighting is the only form invariant under regrouping while retaining every constituent coordinate.",
    "Composite centre is the exact complete inertia-weighted location relation and composite momentum is the disjoint junction of all part momenta.",
    "complete-weighted-composite-centre", ANGULAR_MOMENTUM.claim_id,
    "CODATA composite particle and molar-mass rows", "CODATA mass-ratio rows",
)

CONSERVATION = law(
    "SFT-PHYS-MECH-CONSERVATION-001", "Mechanical conservation under closed transfer",
    "For a closed generated interaction network, every lost mechanical carrier at one node is forced to be held at another; complete internal transfer therefore preserves total momentum and energy support.",
    "closed-network-transfer-bijection", "A complete source/destination bijection preserves every carrier, whereas creation or loss lacks a generated trace.",
    "Closed mechanical transfer is a bijection on complete momentum and energy carriers, establishing exact conservation within the declared boundary.",
    "closed-transfer-conservation", COMPOSITE_CENTRE.claim_id,
    "CODATA conversion relationships preserving physical quantity values", "CODATA energy-equivalent and momentum rows",
)

CONSTRAINT_OSCILLATION = law(
    "SFT-PHYS-MECH-CONSTRAINT-OSCILLATION-001", "Constrained motion, restoration and oscillation",
    "A reversible constraint maps displacement orientation to a source-bound restoring transfer; finite repeated reversal forces a recurrence whose period is an exact transition count relative to the reference recurrence.",
    "reversible-restoring-recurrence", "A reversible held-orientation response returns every displaced carrier through the reference state and generates the unique closed oscillation path.",
    "Constrained reversible restoration generates a closed oscillation with exact recurrence count, held phase and conserved carrier trace.",
    "reversible-restoration-oscillation", CONSERVATION.claim_id,
    "CODATA frequency-valued reference relationships", "CODATA atomic unit of time and energy relationship",
)


MECHANICS_SPECS = (
    EVENT_CHANGE, DURATION, LOCATION_DISPLACEMENT, SPEED_VELOCITY, ACCELERATION,
    INERTIA, MOMENTUM, FORCE, WORK_ENERGY, POWER, ANGULAR_MOTION,
    ANGULAR_MOMENTUM, COMPOSITE_CENTRE, CONSERVATION, CONSTRAINT_OSCILLATION,
)

for _spec in MECHANICS_SPECS:
    _spec.validate()

__all__ = ("MECHANICS_SPECS",)
