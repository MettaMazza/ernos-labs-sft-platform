"""Supplemental exact measured-value tests for already admitted Physics laws."""

from __future__ import annotations

from sft.physics.generated_empirical_law import EmpiricalPhysicsSpec, ExternalTargetRow, empirical_dimensions
from sft.physics.measured_value import (
    CODATA_SOURCE_HASH,
    CODATA_SOURCE_ID,
    CODATA_SOURCE_PATH,
    ExactMeasuredValueSpec,
    ExactRelationStep,
    MeasuredQuantity,
)


def validation_law(claim_id: str, title: str, statement: str, dependency: str, result: str) -> EmpiricalPhysicsSpec:
    slug = claim_id.removeprefix("SFT-PHYS-VALIDATION-").removesuffix("-001")
    experiment_id = f"SFT-EXP-PHYS-VALIDATION-{slug}-001"
    return EmpiricalPhysicsSpec(
        claim_id=claim_id,
        title=title,
        statement=statement,
        dependencies=(
            "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001",
            "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
            "SFT-PHYS-MEAS-HOSTILE-PACKAGE-001",
            "SFT-PHYS-MEAS-VALUE-RECORD-001",
            "SFT-PHYS-MEAS-UNCERTAINTY-001",
            dependency,
        ),
        generation_rule="Generate the complete exact-relation, input-provenance, target-access, interval, comparison, row, successor and extra-rule product.",
        grammar_boundary="All exact positive interval predictions formed from registered measured inputs, one already forced relation, capability-closed arithmetic and a post-seal external target.",
        dimensions=empirical_dimensions(
            "exact-positive-interval-relation",
            "The already forced law uniquely composes registered positive input intervals into the withheld target quantity without fitting.",
        ),
        exact_result=result,
        induction_base="One registered relation composes one complete set of positive measurement carriers into one target interval.",
        induction_step="Adding a measured input endpoint or relation step preserves every prior provenance and arithmetic trace and appends one source-bound exact operation.",
        exclusions=(
            "floating, irrational, imaginary, signed or numerical-null proof values",
            "fitted coefficients, target-selected relations or unregistered constants",
            "target access before prediction seal",
            "omitted input uncertainty, external row or adverse control",
        ),
        operational_witnesses=(
            ("exact-rational-runtime", "Every external finite decimal becomes an exact positive rational interval.", True),
            ("target-withheld-runtime", "The target vault releases only after a matching prediction seal.", True),
        ),
        experiment_id=experiment_id,
        expected_observation_label="exact-measured-interval-overlap",
        target_rows=(
            ExternalTargetRow(slug.lower() + "-numeric-target", CODATA_SOURCE_ID, "named CODATA fixed-width quantity row", "exact-measured-interval-overlap"),
        ),
        source_snapshot_path=CODATA_SOURCE_PATH,
        source_snapshot_hash=CODATA_SOURCE_HASH,
        falsification_condition="The sealed exact predicted interval fails to overlap the independently released CODATA target interval, any registered input is missing, or the displaced unfavorable interval is accepted.",
    )


def value_spec(
    law: EmpiricalPhysicsSpec,
    relation_id: str,
    relation_statement: str,
    inputs: tuple[MeasuredQuantity, ...],
    steps: tuple[ExactRelationStep, ...],
    output_key: str,
    target: MeasuredQuantity,
) -> ExactMeasuredValueSpec:
    return ExactMeasuredValueSpec(
        relation_id=relation_id,
        experiment_id=law.experiment_id,
        claim_id=law.claim_id,
        relation_statement=relation_statement,
        source_id=CODATA_SOURCE_ID,
        source_snapshot_path=CODATA_SOURCE_PATH,
        source_snapshot_hash=CODATA_SOURCE_HASH,
        inputs=inputs,
        steps=steps,
        output_key=output_key,
        target=target,
        falsification_condition=law.falsification_condition,
    )


MOLAR_PLANCK = validation_law(
    "SFT-PHYS-VALIDATION-METROLOGY-MOLAR-PLANCK-001",
    "Exact molar Planck measured-value correspondence",
    "The molar Planck carrier is predicted by exact composition of the Planck carrier with the counted molar carrier.",
    "SFT-PHYS-MEAS-UNIT-COMPARISON-001",
    "Planck constant composed with Avogadro count predicts the CODATA molar Planck interval.",
)

MECHANICS_MOMENTUM = validation_law(
    "SFT-PHYS-VALIDATION-MECHANICS-MOMENTUM-001",
    "Exact momentum measured-value correspondence",
    "The atomic momentum carrier is predicted by exact composition of inertial content with propagation speed.",
    "SFT-PHYS-MECH-MOMENTUM-001",
    "Atomic mass composed with atomic velocity predicts the CODATA atomic momentum interval.",
)

MECHANICS_FORCE = validation_law(
    "SFT-PHYS-VALIDATION-MECHANICS-FORCE-001",
    "Exact force measured-value correspondence",
    "The atomic force carrier is predicted by exact work-energy transfer per spatial support interval.",
    "SFT-PHYS-MECH-FORCE-001",
    "Atomic energy divided by atomic length predicts the CODATA atomic-force interval.",
)

FIELD_POTENTIAL = validation_law(
    "SFT-PHYS-VALIDATION-FIELD-ELECTRIC-POTENTIAL-001",
    "Exact electric-potential measured-value correspondence",
    "The atomic electric-potential carrier is predicted by exact energy transfer per elementary held-charge carrier.",
    "SFT-PHYS-FIELD-ELECTRIC-POTENTIAL-001",
    "Atomic energy divided by elementary charge predicts the CODATA atomic electric-potential interval.",
)

FIELD_STRENGTH = validation_law(
    "SFT-PHYS-VALIDATION-FIELD-ELECTRIC-STRENGTH-001",
    "Exact electric-field measured-value correspondence",
    "The atomic electric-field response is predicted by exact potential change per atomic spatial support interval.",
    "SFT-PHYS-FIELD-ELECTRIC-POTENTIAL-001",
    "Atomic electric potential divided by atomic length predicts the CODATA atomic electric-field interval.",
)

WAVE_FREQUENCY = validation_law(
    "SFT-PHYS-VALIDATION-WAVE-FREQUENCY-001",
    "Exact wave frequency measured-value correspondence",
    "A registered inverse-length recurrence transported at the limiting propagation speed predicts its recurrence frequency.",
    "SFT-PHYS-WAVE-SPEED-LENGTH-FREQUENCY-001",
    "Rydberg inverse length composed with limiting speed predicts the CODATA Rydberg-frequency interval.",
)

WAVE_ENERGY = validation_law(
    "SFT-PHYS-VALIDATION-WAVE-ENERGY-001",
    "Exact wave energy measured-value correspondence",
    "A recurrence frequency composed with the Planck transfer carrier predicts its transported energy.",
    "SFT-PHYS-WAVE-ENERGY-MOMENTUM-001",
    "Rydberg inverse length, Planck carrier and limiting speed predict the CODATA Rydberg-energy interval.",
)

THERMAL_MOLAR = validation_law(
    "SFT-PHYS-VALIDATION-THERMO-MOLAR-ENERGY-001",
    "Exact molar thermal measured-value correspondence",
    "The molar thermal-energy carrier is predicted by exact composition of the per-constituent thermal carrier with the counted molar carrier.",
    "SFT-PHYS-THERMO-TEMPERATURE-001",
    "Boltzmann carrier composed with Avogadro count predicts the CODATA molar gas-constant interval.",
)


BACKFILL_SPECS = (
    MOLAR_PLANCK,
    MECHANICS_MOMENTUM,
    MECHANICS_FORCE,
    FIELD_POTENTIAL,
    FIELD_STRENGTH,
    WAVE_FREQUENCY,
    WAVE_ENERGY,
    THERMAL_MOLAR,
)

VALUE_SPECS = {
    MOLAR_PLANCK.claim_id: value_spec(
        MOLAR_PLANCK,
        "molar-planck-product",
        "h composed with the Avogadro count yields the molar Planck carrier.",
        (MeasuredQuantity("planck", "Planck constant", "J Hz^-1"), MeasuredQuantity("avogadro", "Avogadro constant", "mol^-1")),
        (ExactRelationStep("molar_planck", "product", "planck", "avogadro"),),
        "molar_planck",
        MeasuredQuantity("target_molar_planck", "molar Planck constant", "J Hz^-1 mol^-1"),
    ),
    MECHANICS_MOMENTUM.claim_id: value_spec(
        MECHANICS_MOMENTUM,
        "momentum-mass-speed-product",
        "Inertial content composed with speed yields momentum.",
        (MeasuredQuantity("mass", "atomic unit of mass", "kg"), MeasuredQuantity("speed", "atomic unit of velocity", "m s^-1")),
        (ExactRelationStep("momentum", "product", "mass", "speed"),),
        "momentum",
        MeasuredQuantity("target_momentum", "atomic unit of momentum", "kg m s^-1"),
    ),
    MECHANICS_FORCE.claim_id: value_spec(
        MECHANICS_FORCE,
        "force-energy-length-quotient",
        "Work-energy transfer per spatial interval yields force.",
        (MeasuredQuantity("energy", "atomic unit of energy", "J"), MeasuredQuantity("length", "atomic unit of length", "m")),
        (ExactRelationStep("force", "quotient", "energy", "length"),),
        "force",
        MeasuredQuantity("target_force", "atomic unit of force", "N"),
    ),
    FIELD_POTENTIAL.claim_id: value_spec(
        FIELD_POTENTIAL,
        "potential-energy-charge-quotient",
        "Energy transfer per held charge yields electric potential.",
        (MeasuredQuantity("energy", "atomic unit of energy", "J"), MeasuredQuantity("charge", "elementary charge", "C")),
        (ExactRelationStep("potential", "quotient", "energy", "charge"),),
        "potential",
        MeasuredQuantity("target_potential", "atomic unit of electric potential", "V"),
    ),
    FIELD_STRENGTH.claim_id: value_spec(
        FIELD_STRENGTH,
        "electric-field-potential-length-quotient",
        "Potential change per spatial interval yields electric-field response.",
        (MeasuredQuantity("potential", "atomic unit of electric potential", "V"), MeasuredQuantity("length", "atomic unit of length", "m")),
        (ExactRelationStep("field", "quotient", "potential", "length"),),
        "field",
        MeasuredQuantity("target_field", "atomic unit of electric field", "V m^-1"),
    ),
    WAVE_FREQUENCY.claim_id: value_spec(
        WAVE_FREQUENCY,
        "frequency-inverse-length-speed-product",
        "Inverse wavelength composed with propagation speed yields recurrence frequency.",
        (MeasuredQuantity("inverse_length", "Rydberg constant", "m^-1"), MeasuredQuantity("speed", "speed of light in vacuum", "m s^-1")),
        (ExactRelationStep("frequency", "product", "inverse_length", "speed"),),
        "frequency",
        MeasuredQuantity("target_frequency", "Rydberg constant times c in Hz", "Hz"),
    ),
    WAVE_ENERGY.claim_id: value_spec(
        WAVE_ENERGY,
        "energy-inverse-length-planck-speed-product",
        "Inverse wavelength composed with limiting speed and the Planck carrier yields wave energy.",
        (
            MeasuredQuantity("inverse_length", "Rydberg constant", "m^-1"),
            MeasuredQuantity("planck", "Planck constant", "J Hz^-1"),
            MeasuredQuantity("speed", "speed of light in vacuum", "m s^-1"),
        ),
        (
            ExactRelationStep("frequency", "product", "inverse_length", "speed"),
            ExactRelationStep("energy", "product", "frequency", "planck"),
        ),
        "energy",
        MeasuredQuantity("target_energy", "Rydberg constant times hc in J", "J"),
    ),
    THERMAL_MOLAR.claim_id: value_spec(
        THERMAL_MOLAR,
        "molar-thermal-product",
        "Per-constituent thermal energy composed with the molar count yields molar thermal energy.",
        (MeasuredQuantity("boltzmann", "Boltzmann constant", "J K^-1"), MeasuredQuantity("avogadro", "Avogadro constant", "mol^-1")),
        (ExactRelationStep("molar_thermal", "product", "boltzmann", "avogadro"),),
        "molar_thermal",
        MeasuredQuantity("target_molar_thermal", "molar gas constant", "J mol^-1 K^-1"),
    ),
}

for _law in BACKFILL_SPECS:
    _law.validate()
    VALUE_SPECS[_law.claim_id].validate()

__all__ = ("BACKFILL_SPECS", "VALUE_SPECS")
