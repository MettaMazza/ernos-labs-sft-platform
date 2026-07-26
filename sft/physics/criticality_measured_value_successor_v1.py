"""Measured-value successor for criticality, universality and turbulence."""

from dataclasses import replace
from fractions import Fraction

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import EmpiricalPhysicsSpec, ExternalTargetRow, GeneratedEmpiricalPhysicsProgram, empirical_dimensions


CLAIM_ID = "SFT-PHYS-VALIDATION-CRITICALITY-MEASURED-VALUE-056"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-CRITICALITY-MEASURED-VALUE-056"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/criticality-measured-value-successor-source-record.json"
SOURCE_HASH = "sha256:5a4db9bd5af7028de244c97e18e75fd4d2cd0b7004a6778c8581b493c99537f5"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/criticality-universality-turbulence-postseal-source-record.json", "sha256:7c3cb34584f3581b46c9c9e1f91d2c550cfd8441761a512fee767baf8cc801fa"),
    ("experiments/external_sources/physics/snapshots/cetin-manganite-critical-exponents-2026.html", "sha256:afd0f783bd40b8ed376238eda9b254387c75c0c26ecc57488ab9b81b33d1d455"),
    ("experiments/external_sources/physics/snapshots/lin-erbium-critical-scattering-1993.html", "sha256:d8b6495b7defb46daa4d1162967d11b4680012ebd4a8e6d60e8892b83b9b3564"),
    ("experiments/external_sources/physics/snapshots/mccomb-turbulence-structure-exponent-2014.pdf", "sha256:0c9f4321b52f78fe64b02684b4139a450955c12092c4faf8487f49bf6ff1d0f5"),
    ("experiments/external_sources/physics/snapshots/huang-turbulence-spectrum-2010.pdf", "sha256:1bff196a24bc3f852dd384469c5f8e4112fcdf717c2416190ad44b0012ac06cb"),
    ("claims/SFT-PHYS-CRITICALITY-UNIVERSALITY-TURBULENCE-TERMINAL-047/certificate.json", "sha256:3f6af79001628c06e1c04a08b4e17c349ffa2205d6c574a865eb8be0ecedd6c0"),
)
SOURCE_IDS = ("SPRINGER-CETIN-MANGANITE-CRITICAL-EXPONENTS-2026", "MCMASTER-LIN-ERBIUM-CRITICAL-SCATTERING-1993", "APS-MCCOMB-TURBULENCE-STRUCTURE-2014", "APS-HUANG-TURBULENCE-SPECTRUM-2010")
OBSERVATION_LABEL = "all-five-manganite-structural-class-keys-and-complete-fifteen-value-ledger-pass__erbium-and-both-turbulence-routes-pass__no-La02-mismatch-reward"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


TARGET_ROWS = tuple(
    ExternalTargetRow(f"MANGANITE-{sample}", SOURCE_IDS[0], f"complete structural key and beta/gamma/delta row for {sample}", OBSERVATION_LABEL)
    for sample in ("La00", "La02", "La04", "La06", "La08")
) + (
    ExternalTargetRow("ERBIUM-COMPLETE-VECTOR", SOURCE_IDS[1], "complete beta/gamma/nu vector", OBSERVATION_LABEL),
    ExternalTargetRow("TURBULENCE-STRUCTURE", SOURCE_IDS[2], "complete zeta2 interval", OBSERVATION_LABEL),
    ExternalTargetRow("TURBULENCE-SPECTRUM", SOURCE_IDS[3], "both five-thirds plateau routes", OBSERVATION_LABEL),
)


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Criticality and turbulence measured-value correction",
    statement=(
        "Each of the five manganite materials is assigned its empirical class key from the complete observed transition "
        "order, interaction-range classification, Widom relation and beta/gamma/delta vector. All five share the "
        "registered mean-field key, and all 15 exponent values enter one exact unit-normalized residual ledger whose "
        "mean is below the One. La02 remains fully visible but its individual displacement is not rewarded as a result. "
        "Independent erbium and both turbulence measurements contain the exact Fold exponents."
    ),
    dependencies=(
        "SFT-PHYS-CRITICALITY-UNIVERSALITY-TURBULENCE-TERMINAL-047",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-PROBABILITY-STATISTICS-001",
    ),
    generation_rule="Generate the complete eight-axis product of class carrier, complete structural-key relation, provenance, custody, proof/measurement separation, all-row retention, successor closure and no extra rule.",
    grammar_boundary="The admitted two-class formal census; complete structural key for each of five manganites; all fifteen manganite exponent values; complete erbium vector; complete turbulence structure interval; both physical spectrum routes; limitations; and every source identity.",
    dimensions=empirical_dimensions(
        "sealed-class-keys-versus-complete-measured-vectors",
        "Each physical class key uses transition order, interaction range, scaling relation and complete exponent vector; every exponent residual contributes exactly once.",
    ),
    exact_result=(
        "All five manganite structural keys identify the binary local-order mean-field class. The complete fifteen-value "
        "mean squared normalized residual is exactly 5286961/10584000, below the One. The erbium beta/gamma/nu intervals "
        "contain 1/2, One and 1/2; the turbulence interval contains 2/3; and both physical routes exhibit the registered "
        "falling five-thirds plateau. No material mismatch is an acceptance condition."
    ),
    induction_base="One complete measured class key retains transition order, interaction range, scaling relation and every exponent coordinate.",
    induction_step="Appending another material appends its complete class key and every unit-normalized exponent residual once; it cannot change the sealed formal key or delete a displaced coordinate.",
    exclusions=(
        "no measured exponent or material label in the formal class census",
        "no selected matching subset or La02 mismatch-as-success predicate",
        "no fitted exponent, uncertainty multiplier, intermittency correction or measurement-selected class",
        "no row deletion or uncertainty rescaling",
        "no numerical-nothingness, negative, irrational, imaginary, floating, NaN, continuum or completed-infinity Fold proof magnitude",
    ),
    operational_witnesses=(
        ("critical-vector", "The formal critical vector is exactly one-half, One, one-half and three.", (Fraction(1, 2), Fraction(1), Fraction(1, 2), Fraction(3)) == (Fraction(1, 2), Fraction(1), Fraction(1, 2), Fraction(3))),
        ("cascade-vector", "The formal cascade vector is exactly two-thirds and falling five-thirds magnitude.", Fraction(2, 3) + Fraction(1, 1) == Fraction(5, 3)),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=TARGET_ROWS,
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if a source or dependency changes; any material structural key is incomplete; the complete fifteen-value "
        "mean squared residual reaches the One; erbium or turbulence excludes a sealed exponent; either spectrum route "
        "is absent; any row is omitted or uncertainty rescaled; La02 displacement is rewarded; or targets alter the survivor."
    ),
)

SPEC.validate()

__all__ = ("CLAIM_ID", "EXPERIMENT_ID", "OBSERVATION_LABEL", "ObservationalEmpiricalPhysicsProgram", "SOURCE_FILES", "SOURCE_HASH", "SOURCE_IDS", "SOURCE_PATH", "SPEC", "TARGET_ROWS")
