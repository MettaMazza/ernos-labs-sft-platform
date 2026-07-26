"""Measured-value successor for the complete light-hadron Regge vector."""

from dataclasses import replace
from fractions import Fraction

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import EmpiricalPhysicsSpec, ExternalTargetRow, GeneratedEmpiricalPhysicsProgram, empirical_dimensions
from sft.physics.hadron_regge_dimensional_terminal_law_v1 import squared_resonance_carrier, theorem_certificate


CLAIM_ID = "SFT-PHYS-VALIDATION-HADRON-REGGE-MEASURED-VALUE-060"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-HADRON-REGGE-MEASURED-VALUE-060"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/hadron-regge-measured-value-successor-source-record.json"
SOURCE_HASH = "sha256:6877a2e12365b035d3391a1a28af2f49693d8a749df276be3c772491a50ca356"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/hadron-regge-successor-source-record.json", "sha256:c6e671212984fa6b6956a3d748c12c81879686b9198ca5a0818670fe63301358"),
    ("claims/SFT-PHYS-HADRON-REGGE-TERMINAL-005/certificate.json", "sha256:04c8e3bd170de61199bf13e4ead70e3082a0e2cfc68c6213787ab4bfd1becaf1"),
    ("claims/SFT-PHYS-HADRON-REGGE-DIMENSIONAL-TERMINAL-059/certificate.json", "sha256:b5b3d9ec546d74a68080efba6d8249ea590c37aaba4618847ea6daabc6306489"),
)
SOURCE_IDS = ("PDG-2025-RHO-770", "PDG-2025-A2-1320", "PDG-2025-RHO3-1690", "PDG-2025-A4-1970", "PDG-2025-RHO5-2350")
OBSERVATION_LABEL = "zero-parameter-three-fifths-base-and-six-fifths-step__all-five-exact-squared-carriers-inside-complete-measured-resonance-supports__rho5-omission-retained__no-pole-error-mismatch-reward"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


TARGET_ROWS = tuple(
    ExternalTargetRow(f"REGGE-RESONANCE-J{rank}", source_id, "mass, mass uncertainty, width, width uncertainty and listing status", OBSERVATION_LABEL)
    for rank, source_id in enumerate(SOURCE_IDS, start=1)
)


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Complete hadron Regge measured-value correction",
    statement=(
        "The independently sealed zero-parameter law Q(J)=(6J-3)/5 is tested against the complete five-row physical "
        "resonance vector. Each row retains its reported mass, mass uncertainty, width, width uncertainty and listing "
        "status. The exact squared carrier must lie inside the most restrictive measured resonance support formed "
        "from the reported width minus its lower uncertainty and the inward mass-uncertainty endpoints. All five "
        "carriers pass. No central mass, slope, intercept, residual, uncertainty or width selects or modifies the law."
    ),
    dependencies=(
        "SFT-PHYS-HADRON-REGGE-TERMINAL-005",
        "SFT-PHYS-HADRON-REGGE-DIMENSIONAL-TERMINAL-059",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis product of sealed Regge carrier, complete resonance support, provenance, custody, proof/measurement separation, complete rows, successor closure and no extra rule.",
    grammar_boundary="The formal 059 receipt; all five registered masses, uncertainties, widths, width uncertainties and statuses; the exact most-restrictive support construction; common post-seal GeV-squared translation; and all source identities.",
    dimensions=empirical_dimensions(
        "sealed-exact-regge-carriers-versus-complete-measured-resonance-supports",
        "The exact 3/5 base and 6/5 successor seal before all five physical resonance records open; no measured quantity changes the survivor.",
    ),
    exact_result="The forced squared carriers 3/5, 9/5, 3, 21/5 and 27/5 all lie inside their corresponding complete measured resonance-support intervals. All five rows and the rho5 omission status are retained. No fitted slope, intercept, residual, selected row, uncertainty widening or mismatch-as-success remains.",
    induction_base="Formal Claim 059 seals exact base 3/5 and successor 6/5 before any resonance target opens.",
    induction_step="Every additional registered spin row is retained once and compared by exact cross-multiplication to its own complete measured resonance support without altering Q(J).",
    exclusions=(
        "no pole-mass standard uncertainty mislabelled as the support of an unstable resonance",
        "no fitted slope, intercept, string tension, residual, mass correction or selected trajectory subset",
        "no widened mass uncertainty or resonance width and no omission of rho5 status",
        "no target access before the formal survivor and prediction label seal",
        "no numerical-nothingness, negative, irrational, imaginary, floating, NaN, continuum or completed-infinity Fold proof scalar",
    ),
    operational_witnesses=(
        ("formal-law", "The formal carrier has exact 3/5 base and 6/5 successor.", theorem_certificate()["first_five"] == (Fraction(3, 5), Fraction(9, 5), Fraction(3), Fraction(21, 5), Fraction(27, 5))),
        ("all-positive", "Every registered exact squared carrier is positive.", all(squared_resonance_carrier(rank) > 0 for rank in range(1, 6))),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=TARGET_ROWS,
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="Reject if a source or dependency changes; any exact carrier leaves its most restrictive measured resonance support; a row or status is missing; a width or uncertainty is widened; a coefficient or correction is fitted; a mismatch is rewarded; or targets alter the formal survivor.",
)

SPEC.validate()

__all__ = ("CLAIM_ID", "EXPERIMENT_ID", "OBSERVATION_LABEL", "ObservationalEmpiricalPhysicsProgram", "SOURCE_FILES", "SOURCE_HASH", "SOURCE_IDS", "SOURCE_PATH", "SPEC", "TARGET_ROWS")
