"""Measured-value successor for terminal cosmic transport."""

from dataclasses import replace
from fractions import Fraction

from sft.engine import ProvenanceClass
from sft.physics.cosmic_component_transport_terminal_law_v1 import acceleration_onset_cube, matter_vacuum_equality_cube, present_acceleration_magnitude
from sft.physics.generated_empirical_law import EmpiricalPhysicsSpec, ExternalTargetRow, GeneratedEmpiricalPhysicsProgram, empirical_dimensions


CLAIM_ID = "SFT-PHYS-VALIDATION-COSMIC-TRANSPORT-MEASURED-VALUE-055"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-COSMIC-TRANSPORT-MEASURED-VALUE-055"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/cosmic-transport-measured-value-successor-source-record.json"
SOURCE_HASH = "sha256:d4595bfbf4a8bf413fd17493eeed848da664a1d794dacd8ad90627307bcbb8a1"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/cosmic_transport_terminal-source-record.json", "sha256:6a88728657b19dba0bcf2430d28218a595c0798c6ac34bf2778ef53a1b540705"),
    ("experiments/external_sources/physics/snapshots/gomez-valent-2023-cosmic-chronometers.html", "sha256:cbd38055c3c9b27b2cbe1fb7456c60dfd7df3eeb366182932b7899d25207b128"),
    ("experiments/external_sources/physics/snapshots/planck-2018-bao-budget-record.json", "sha256:a8525585688e7ba818f8650fc0f8b73a449823d5e199a8be36e37b8e73a0e612"),
    ("experiments/external_sources/physics/snapshots/arxiv-1805.03595-source-record.json", "sha256:4ac5d80b39e3dc963d5cc7a0c1b8996b0b895a974f08fa736803186bd100f74c"),
    ("experiments/external_sources/physics/snapshots/arxiv-1810.02278-cosmic-acceleration.pdf", "sha256:55100ed889f8aad5ada957f33759d954466b944d21b461b4c63c62f0b0fb45d0"),
    ("experiments/external_sources/physics/snapshots/arxiv-2307.14802-dark-energy-state.pdf", "sha256:67c8d75e79fd85d727012e72e8838651de6720a2e8898e225e251601814c20a5"),
    ("experiments/external_sources/physics/snapshots/arxiv-2503.14738-desi-dr2.pdf", "sha256:1e82f26e4cc3901b16168cd147f252bfa804f9c3caad3f4f7e3532640d237841"),
    ("claims/SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032/certificate.json", "sha256:c83b4fc53d29e878502657b310325adcee62be483407433d61465dd744b57354"),
)
SOURCE_IDS = ("GOMEZ-VALENT-2023-CCH-32", "PLANCK-2018-BAO-BASELINE-BUDGET", "HARIDASU-2018-LATE-EXPANSION", "GOMEZ-VALENT-2019-ACCELERATION", "ESCAMILLA-2024-DARK-ENERGY-STATE", "DESI-DR2-2025-COSMOLOGY")
OBSERVATION_LABEL = "cosmic-transport-complete-normalized-residual-ledger-passes__budget-acceleration-and-static-state-values-pass__alternate-reconstructions-retained-without-mismatch-reward"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


TARGET_ROWS = tuple(
    ExternalTargetRow(f"CCH-RESIDUAL-{position:02d}", SOURCE_IDS[0], f"complete chronometer row {position}", OBSERVATION_LABEL)
    for position in range(1, 33)
) + (
    ExternalTargetRow("PLANCK-EQUALITY", SOURCE_IDS[1], "complete matter/vacuum budget interval", OBSERVATION_LABEL),
    ExternalTargetRow("PLANCK-ONSET", SOURCE_IDS[1], "twice complete matter/vacuum budget interval", OBSERVATION_LABEL),
    ExternalTargetRow("HARIDASU-Q0", SOURCE_IDS[2], "abstract q0 interval", OBSERVATION_LABEL),
    ExternalTargetRow("HARIDASU-ZT", SOURCE_IDS[2], "abstract transition-redshift interval", OBSERVATION_LABEL),
    ExternalTargetRow("STATIC-W", SOURCE_IDS[4], "constant-vacuum state interval", OBSERVATION_LABEL),
    ExternalTargetRow("ALTERNATE-ACCELERATION-RECONSTRUCTION", SOURCE_IDS[3], "complete q0 and zt method record", OBSERVATION_LABEL),
    ExternalTargetRow("DESI-MODEL-COMPARISON", SOURCE_IDS[5], "complete w0-wa model-comparison record", OBSERVATION_LABEL),
)


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal cosmic transport measured-value correction",
    statement=(
        "The zero-parameter law E2(r)=(11+5r^3)/16 is tested against all 32 direct chronometer rows by one "
        "complete exact normalized-residual ledger. Rational root enclosures refine until its decision is exact, "
        "replacing the selected two-uncertainty row rule. The exact 11/5 equality, 22/5 onset, 17/32 acceleration "
        "magnitude and tension-One state meet like-typed external intervals. Alternate reconstruction and model-fit "
        "records remain unchanged but are not rewarded as SFT mismatches."
    ),
    dependencies=(
        "SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-PROBABILITY-STATISTICS-001",
    ),
    generation_rule="Generate the complete eight-axis product of exact transport carrier, unit-normalized residual relation, provenance, custody, proof/measurement separation, complete rows, successor closure and no extra rule.",
    grammar_boundary="The admitted terminal transport receipt; all 32 CCH rows; H0 and complete Planck budget; both registered acceleration reconstructions; constant-w interval; DESI model-comparison record; exact rational root enclosures; and every source identity.",
    dimensions=empirical_dimensions(
        "sealed-cosmic-transport-versus-complete-unit-residual-and-like-typed-values",
        "Every direct expansion row contributes once to the exact mean squared standard-uncertainty ledger; separately derived observables use their complete like-typed intervals.",
    ),
    exact_result=(
        "The exact upper enclosure of the complete 32-row mean squared normalized residual is below the One after "
        "the fourth exact enclosure round (three forced bisection refinements). The exact 11/5, 22/5, 17/32 and tension-One values lie inside the "
        "complete registered Planck, Haridasu and constant-state intervals. No sigma multiplier, fitted component, "
        "uncertainty rescaling, deleted row or mismatch-as-success predicate remains."
    ),
    induction_base="At present stretch One, the admitted shares close the One and E2(One)=One before any external expansion row is released.",
    induction_step="Each direct chronometer row contributes one exact squared residual divided by its reported variance unit; complete averaging and refining rational root enclosures preserve the decision without changing the physical law.",
    exclusions=(
        "no external H, density, q, transition or state target in the formal transport law",
        "no fitted H0, density, exponent, residual coefficient or selected uncertainty multiplier",
        "no rowwise two-standard-uncertainty shortcut",
        "no DESI model preference or alternate reconstruction relabelled as an SFT result",
        "no deleted measurement row or rescaled uncertainty",
        "no numerical-nothingness, negative, irrational, imaginary, floating, NaN, continuum or completed-infinity Fold proof magnitude",
    ),
    operational_witnesses=(
        ("equality-exact", "Matter-vacuum equality is exactly 11/5.", matter_vacuum_equality_cube() == Fraction(11, 5)),
        ("onset-exact", "Acceleration onset is exactly 22/5.", acceleration_onset_cube() == Fraction(22, 5)),
        ("acceleration-exact", "Present acceleration magnitude is exactly 17/32.", present_acceleration_magnitude() == Fraction(17, 32)),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=TARGET_ROWS,
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if a source or dependency changes; the complete normalized-residual lower enclosure reaches the One; "
        "any forced threshold, acceleration or static-state value leaves its like-typed interval; any row is omitted; "
        "an uncertainty is rescaled; a method/model-comparison displacement is rewarded; or target data alter the formal survivor."
    ),
)

SPEC.validate()

__all__ = ("CLAIM_ID", "EXPERIMENT_ID", "OBSERVATION_LABEL", "ObservationalEmpiricalPhysicsProgram", "SOURCE_FILES", "SOURCE_HASH", "SOURCE_IDS", "SOURCE_PATH", "SPEC", "TARGET_ROWS")
