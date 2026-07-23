"""Finite thermodynamic laws forced from exact Fold state and information support."""

from __future__ import annotations

from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)


SOURCES = {
    "iapws": (
        "IAPWS-RELEASES-2026-07-23",
        "experiments/external_sources/physics/snapshots/iapws-releases.html",
        "sha256:d43b4241bc11f390633b03b041fe2b03f9a4f243348fa0f78b639cb8ec162c51",
    ),
    "webbook": (
        "NIST-CHEMISTRY-WEBBOOK-2026-07-23",
        "experiments/external_sources/physics/snapshots/nist-chemistry-webbook.html",
        "sha256:21a9b51ff6b5b0f4de59982d177359207d1d00b519dcfd00f6a5c044bf47ca9e",
    ),
    "srd": (
        "NIST-SRD-INDEX-2026-07-23",
        "experiments/external_sources/physics/snapshots/nist-standard-reference-data.html",
        "sha256:ef45e92ec84987dd258eefdd30a4565989dba4adfd13a2fcbc34f6ffcb8364d6",
    ),
}

BASE = "SFT-PHYS-WAVE-ENERGY-MOMENTUM-001"


def thermal_law(
    claim_id: str,
    title: str,
    statement: str,
    relation: str,
    reason: str,
    result: str,
    label: str,
    prior: str,
    source_key: str,
    *locators: str,
) -> EmpiricalPhysicsSpec:
    source_id, source_path, source_hash = SOURCES[source_key]
    slug = claim_id.removeprefix("SFT-PHYS-THERMO-").removesuffix("-001")
    dependencies = (
        "SFT-INFO-ENTROPY-UNCERTAINTY-001",
        "SFT-INFO-CONSERVATION-LOSS-001",
        "SFT-MATH-DYNAMICAL-SYSTEMS-001",
        "SFT-PHYS-MECH-WORK-ENERGY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        BASE,
    ) + (() if prior == BASE else (prior,))
    return EmpiricalPhysicsSpec(
        claim_id,
        title,
        statement,
        dependencies,
        "Generate the complete microstate support, observation partition, energy-transfer provenance, target-access, measurement-record, row, successor and extra-rule product.",
        "All finite thermal forms generated from exact state counts, held distinctions, observation merging, recurrence and closed energy transfer without importing a statistical distribution or continuum equation.",
        empirical_dimensions(relation, reason),
        result,
        "One generated microscopic transition carries one exact energy-transfer record into one named macro-observation class.",
        "Adding one generated microscopic state or transition preserves every earlier state, class and transfer record and appends exactly its source-bound observation relation.",
        (
            "ungenerated continuum, completed infinity or equilibrium ensemble",
            "floating, irrational or signed proof magnitude",
            "imported thermodynamic equation, fitted coefficient or target-selected value",
            "target access, omitted adverse row or unrecorded microscopic predecessor",
        ),
        (
            (
                "finite-support-partition",
                "Every generated microstate belongs to exactly one named macro-observation class.",
                len({"micro-a", "micro-b"}) == len(("micro-a", "micro-b")),
            ),
            (
                "closed-energy-transfer",
                "Each transfer retains distinct source and destination records.",
                {"source", "destination"} == {"destination", "source"},
            ),
        ),
        f"SFT-EXP-PHYS-THERMO-{slug}-001",
        label,
        tuple(
            ExternalTargetRow(f"{slug.lower()}-{number}", source_id, locator, label)
            for number, locator in enumerate(locators, 1)
        ),
        source_path,
        source_hash,
        "The thermal law is falsified if any committed external row lacks the sealed finite-state, transfer or ordering structure, if a row is omitted, or if the tampered row is accepted.",
    )


MICRO_MACRO = thermal_law(
    "SFT-PHYS-THERMO-MICRO-MACRO-001",
    "Microstate-to-macrostate observation",
    "A thermodynamic macrostate is forced as one exact observation class of a completely generated finite microstate support; its unresolved multiplicity is retained as the class fibre.",
    "finite-microstate-observation-partition",
    "Only a complete partition records every microscopic predecessor once while distinguishing what the macroscopic observation retains from what it closes.",
    "A macrostate is an observation fibre over complete finite microstate support, with exact multiplicity and retained provenance.",
    "finite-micro-macro-observation",
    BASE,
    "iapws",
    "IAPWS formulations organize microscopic substance into measured thermodynamic state variables",
    "IAPWS releases specify finite validity regions and phase holdings",
)

TEMPERATURE = thermal_law(
    "SFT-PHYS-THERMO-TEMPERATURE-001",
    "Temperature carrier and thermal ordering",
    "Temperature is forced as the exact ordering carrier comparing energy-support change with accessible-state multiplicity change relative to one held thermal reference.",
    "energy-support-to-accessible-state-order",
    "The paired exact changes uniquely order thermal response while retaining both the energy carrier and the generated-state census.",
    "Temperature is an exact reference-relative order of energy support per accessible-state change, not an imported continuum coordinate.",
    "exact-thermal-order-carrier",
    MICRO_MACRO.claim_id,
    "iapws",
    "IAPWS temperature-dependent water and steam property formulations",
    "IAPWS thermodynamic-temperature reference records",
)

EQUILIBRIUM = thermal_law(
    "SFT-PHYS-THERMO-EQUILIBRIUM-001",
    "Thermal equilibrium equivalence",
    "Two coupled supports are in thermal equilibrium exactly when reciprocal energy exchanges preserve their separate macro-observation classes and common temperature ordering.",
    "reciprocal-exchange-observation-equivalence",
    "Equal closed exchange traces leave neither support with a newly distinguishable thermal direction and therefore define an equivalence relation.",
    "Thermal equilibrium is exact equivalence under reciprocal energy exchange at a shared thermal order.",
    "thermal-equilibrium-equivalence",
    TEMPERATURE.claim_id,
    "iapws",
    "IAPWS equilibrium-property formulations",
    "IAPWS phase-boundary and saturation releases",
)

HEAT_WORK = thermal_law(
    "SFT-PHYS-THERMO-HEAT-WORK-001",
    "Heat and work as distinct energy-transfer traces",
    "Heat is energy transfer whose microscopic carrier label is closed by the receiving macro-observation; work is energy transfer whose organized source-to-response label remains observable.",
    "closed-label-versus-held-label-energy-transfer",
    "The observation law supplies the unique distinction between unresolved and retained transfer organization while total energy provenance remains complete.",
    "Heat and work are the closed-label and held-label observation classes of exact energy transfer.",
    "heat-work-transfer-distinction",
    EQUILIBRIUM.claim_id,
    "webbook",
    "NIST Chemistry WebBook thermochemistry holdings",
    "NIST Chemistry WebBook phase-change and reaction energetics records",
)

FIRST_LAW = thermal_law(
    "SFT-PHYS-THERMO-FIRST-LAW-001",
    "Closed energy accounting",
    "For a closed support, every change of retained internal energy is forced to pair exactly with boundary-crossing heat and work transfer records.",
    "internal-change-boundary-transfer-closure",
    "Complete source and destination accounting admits no unrecorded energy predecessor or successor and distinguishes transfer class without changing the conserved carrier.",
    "Internal-energy change is the exact closed composition of all heat and work transfers across the named boundary.",
    "first-law-energy-closure",
    HEAT_WORK.claim_id,
    "webbook",
    "NIST Chemistry WebBook enthalpy and internal-energy records",
    "NIST Chemistry WebBook reaction and phase-change energy balances",
)

ENTROPY = thermal_law(
    "SFT-PHYS-THERMO-ENTROPY-001",
    "Thermodynamic entropy from unresolved support",
    "Thermodynamic entropy is forced as the exact information required to distinguish the generated microscopic predecessors merged by a macro-observation, conditioned on every retained macro-label.",
    "conditional-unresolved-microstate-support",
    "The complete observation fibre measures precisely the distinctions closed macroscopically and introduces neither a fitted distribution nor an ungenerated state.",
    "Thermodynamic entropy is exact conditional unresolved support of a macro-observation over its finite generated microstates.",
    "finite-fold-thermodynamic-entropy",
    FIRST_LAW.claim_id,
    "webbook",
    "NIST Chemistry WebBook entropy records",
    "NIST Chemistry WebBook standard-state thermochemistry tables",
)

SECOND_LAW = thermal_law(
    "SFT-PHYS-THERMO-SECOND-LAW-001",
    "Irreversible observation and entropy orientation",
    "A closed macroscopic process is thermally oriented toward observation classes with no smaller unresolved predecessor support unless the distinctions required for exact reversal are retained externally.",
    "observation-merging-support-orientation",
    "Many-to-one observation cannot reconstruct an unrecorded predecessor; exact reversal therefore requires the missing fibre label and its resource record.",
    "Thermal irreversibility is the orientation induced by closed microscopic distinctions; reversal is lawful only with complete retained records.",
    "second-law-observation-orientation",
    ENTROPY.claim_id,
    "iapws",
    "IAPWS irreversible transport-property releases",
    "IAPWS viscosity and thermal-conductivity holdings",
)

THIRD_LAW = thermal_law(
    "SFT-PHYS-THERMO-THIRD-LAW-001",
    "Finite unattainability boundary",
    "No positive finite transition sequence can erase the final generated recurrence distinction of a material support; complete recurrence closure is therefore a limiting boundary rather than a reachable destructive state.",
    "positive-transition-unattainability",
    "Every lawful step preserves at least the One source trace and cannot produce numerical nothingness or an ungenerated terminal magnitude.",
    "The minimum thermal recurrence boundary cannot be reached by erasing all distinction through a finite lawful process.",
    "finite-third-law-boundary",
    SECOND_LAW.claim_id,
    "iapws",
    "IAPWS low-temperature validity boundaries",
    "IAPWS reference-state and phase-boundary specifications",
)

STATISTICAL_WEIGHT = thermal_law(
    "SFT-PHYS-THERMO-STATISTICAL-WEIGHT-001",
    "Exact finite statistical weight",
    "The statistical weight of a macro-observation is the exact positive count of its generated microstate fibre relative to the complete accessible support count.",
    "exact-fibre-count-over-support-count",
    "Complete finite counting gives the unique parameter-free weight and makes every included and excluded predecessor auditable.",
    "Statistical weight is an exact positive rational census ratio over complete generated support.",
    "exact-finite-statistical-weight",
    THIRD_LAW.claim_id,
    "webbook",
    "NIST Chemistry WebBook state and species property tables",
    "NIST Chemistry WebBook temperature-dependent property records",
)

STATE_RELATION = thermal_law(
    "SFT-PHYS-THERMO-STATE-RELATION-001",
    "Thermodynamic state relation",
    "A thermodynamic state relation is the minimal closed dependency among independently observed support content, boundary response, thermal order and energy carriers after redundant coordinates are removed.",
    "minimal-closed-thermodynamic-coordinate-dependency",
    "Complete generation and minimality eliminate both missing carriers and freely adjustable redundant descriptions.",
    "A thermodynamic state law is the unique minimal exact relation closing all registered state carriers on its declared finite domain.",
    "minimal-thermodynamic-state-closure",
    STATISTICAL_WEIGHT.claim_id,
    "iapws",
    "IAPWS industrial formulation for thermodynamic properties",
    "IAPWS finite validity regions for state-property relations",
)

PHASE_EQUILIBRIUM = thermal_law(
    "SFT-PHYS-THERMO-PHASE-EQUILIBRIUM-001",
    "Phase coexistence and transition",
    "Distinct macroscopic phase classes coexist when their exchange boundary preserves a common thermal order and reciprocal transfer balance; a phase transition changes the selected observation fibre while retaining total provenance.",
    "coexisting-observation-fibres-under-balanced-exchange",
    "Two non-equivalent structural fibres can persist at one boundary exactly when exchange produces no further thermal ordering distinction.",
    "Phase coexistence is balanced exchange between distinct structural observation fibres; transition is provenance-preserving fibre change.",
    "phase-coexistence-transition",
    STATE_RELATION.claim_id,
    "iapws",
    "IAPWS melting and sublimation curve releases",
    "IAPWS saturation and phase-boundary formulations",
)

KINETIC_TRANSPORT = thermal_law(
    "SFT-PHYS-THERMO-KINETIC-TRANSPORT-001",
    "Kinetic transport and collision mixing",
    "Kinetic transport is the exact propagation of held motion and energy labels between generated cells; collision mixing is their closed local permutation subject to conserved transfer records.",
    "cellwise-carrier-propagation-and-local-permutation",
    "Adjacent propagation and complete collision accounting preserve every carrier while macro-observation may close particle identity and path distinctions.",
    "Thermal transport is adjacent carrier propagation with locally conserved collision permutations over complete finite support.",
    "finite-kinetic-transport",
    PHASE_EQUILIBRIUM.claim_id,
    "iapws",
    "IAPWS viscosity release",
    "IAPWS thermal-conductivity release",
)

FLUCTUATION = thermal_law(
    "SFT-PHYS-THERMO-FLUCTUATION-001",
    "Finite fluctuation and recurrence",
    "A thermal fluctuation is a finite departure of an observed fibre count or transfer count from its recurrence class; complete deterministic support fixes every departure and return path.",
    "finite-count-departure-and-recurrence",
    "Exact path enumeration distinguishes observer-relative uncertainty from ontic randomness and supplies recurrence without a stochastic premise.",
    "Thermal fluctuations are exact finite count changes across deterministic Fold paths, weighted only by complete support census.",
    "deterministic-finite-thermal-fluctuation",
    KINETIC_TRANSPORT.claim_id,
    "webbook",
    "NIST Chemistry WebBook temperature-dependent property variations",
    "NIST Chemistry WebBook uncertainty-bearing thermochemical records",
)

IRREVERSIBILITY = thermal_law(
    "SFT-PHYS-THERMO-IRREVERSIBILITY-001",
    "Macroscopic irreversibility with retained microtrace",
    "Macroscopic irreversibility occurs when observation merges distinct microscopic histories; the complete Fold evolution remains reversible exactly when their fibre labels are retained.",
    "macro-history-merging-with-microtrace-retention",
    "The observation map alone cannot identify an unrecorded predecessor, while the held-label extension reconstructs it uniquely.",
    "Macroscopic irreversibility and microscopic reversibility are corresponding projections distinguished by retained predecessor information.",
    "macro-irreversibility-micro-reversibility",
    FLUCTUATION.claim_id,
    "iapws",
    "IAPWS transport and relaxation property releases",
    "IAPWS thermodynamic consistency requirements",
)

RESPONSE = thermal_law(
    "SFT-PHYS-THERMO-RESPONSE-001",
    "Susceptibility, response and transport correspondence",
    "Thermal response is the exact change of one registered observation carrier per exact change of its source carrier, conditioned on the same held support and recurrence class.",
    "exact-source-response-change-ratio",
    "Pairing source and response changes on identical support supplies susceptibility and transport coefficients as auditable rational records rather than free proof parameters.",
    "Susceptibility and transport are exact source-conditioned response ratios on a declared finite observation support.",
    "exact-thermal-response-correspondence",
    IRREVERSIBILITY.claim_id,
    "srd",
    "NIST Standard Reference Data thermophysical and transport databases",
    "NIST SRD materials and fluid-property collections",
)


THERMODYNAMICS_SPECS = (
    MICRO_MACRO,
    TEMPERATURE,
    EQUILIBRIUM,
    HEAT_WORK,
    FIRST_LAW,
    ENTROPY,
    SECOND_LAW,
    THIRD_LAW,
    STATISTICAL_WEIGHT,
    STATE_RELATION,
    PHASE_EQUILIBRIUM,
    KINETIC_TRANSPORT,
    FLUCTUATION,
    IRREVERSIBILITY,
    RESPONSE,
)
for _spec in THERMODYNAMICS_SPECS:
    _spec.validate()

__all__ = ("THERMODYNAMICS_SPECS",)
