"""Clean measured-value successor for the terminal electroweak relation."""

from dataclasses import replace
from fractions import Fraction

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    GeneratedEmpiricalPhysicsProgram,
    empirical_dimensions,
)
from sft.physics.precision_value_laws_v1 import (
    terminal_electroweak_cos_squared,
    terminal_electroweak_sin_squared,
)


CLAIM_ID = "SFT-PHYS-VALIDATION-ELECTROWEAK-MEASURED-VALUE-053"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-ELECTROWEAK-MEASURED-VALUE-053"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/electroweak-measured-value-successor-source-record.json"
SOURCE_HASH = "sha256:e608503e4832c272911c0653dd6db9cf5b662647c4fd652908b7d2299e598057"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/pdg-2025-electroweak-model.pdf", "sha256:8642888a3408d8c57fc673b379325b07f02948135491f64a2e42320e8929320a"),
    ("experiments/external_sources/physics/snapshots/pdg-2024-w-boson-listing.pdf", "sha256:91cb466bfea8fa49b53ae53d2168797189c14a5a114f30d7cc926f64c4c1e772"),
)
SOURCE_IDS = ("PDG-2025-STANDARD-MODEL-REVIEW", "PDG-2024-W-BOSON-LISTING")
OBSERVATION_LABEL = "terminal-electroweak-forced-value-inside-direct-on-shell-measurement__compatible-WZ-reconstruction-passes__inconsistent-aggregate-quarantined-as-measurement-method-record__no-mismatch-admitted-as-closure"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal electroweak measured-value correction",
    statement=(
        "The already sealed zero-parameter terminal on-shell share "
        "1930922298157999/8642477221479757 is tested against the direct PDG on-shell measurement "
        "0.22342 +/- 0.00009 and an independent compatible-input W/Z reconstruction. Both measured-value "
        "comparisons pass without fitting, rescaling or row deletion. The separately published all-input W "
        "aggregate contains a source-identified incompatible input and is retained unchanged as a measurement-"
        "method record; it is not admitted as an SFT mismatch or as a second physical target."
    ),
    dependencies=(
        "SFT-PHYS-ELECTROWEAK-TERMINAL-ON-SHELL-003",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis product of the sealed terminal electroweak value, like-typed direct measurements, exact interval transport, source consistency, custody, proof/measurement separation, successor closure and extension.",
    grammar_boundary="The admitted target-free terminal on-shell value; the complete direct on-shell row; the complete compatible W and Z rows; the unchanged internally inconsistent all-input aggregation record; both source identities; and every measurement-method boundary.",
    dimensions=empirical_dimensions(
        "sealed-terminal-electroweak-value-versus-like-typed-direct-measurements",
        "The direct on-shell measurement and compatible W/Z reconstruction test the sealed on-shell carrier; the source-identified inconsistent aggregate is retained only as a method record.",
    ),
    exact_result=(
        "The exact forced terminal on-shell share lies inside the complete PDG interval [22333,22351]/100000. "
        "Its exact complement lies inside the outward-propagated compatible-input W/Z squared interval. "
        "No uncertainty is widened and no inconsistent aggregate is converted into a passing or failing SFT law."
    ),
    induction_base="The admitted terminal on-shell fraction is fixed before either external source record is released.",
    induction_step="Each like-typed measurement row is appended exactly once; an internally inconsistent aggregate remains a separately typed method record and cannot alter the sealed physical value.",
    exclusions=(
        "no measured weak angle or boson mass in the formal relation",
        "no fitted rung, correction, coefficient, uncertainty multiplier or selected central value",
        "no mismatch relabelled as successful empirical closure",
        "no deletion or alteration of the all-input aggregation record",
        "no consensus classification used as proof; source consistency is checked from the published record",
        "no numerical-nothingness, negative, irrational, imaginary, floating, NaN, continuum or completed-infinity Fold proof magnitude",
    ),
    operational_witnesses=(
        ("exact-terminal-share", "The terminal on-shell carrier is an exact proper Fold fraction.", Fraction(1, 5) < terminal_electroweak_sin_squared() < Fraction(1, 4)),
        ("exact-complement", "The terminal sine and cosine squared carriers partition the One exactly.", terminal_electroweak_sin_squared() + terminal_electroweak_cos_squared() == Fraction(1, 1)),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=(
        ExternalTargetRow("PDG-DIRECT-ON-SHELL-WEAK-SHARE", SOURCE_IDS[0], "printed page 23 on-shell sin-squared row", OBSERVATION_LABEL),
        ExternalTargetRow("PDG-COMPATIBLE-WZ-RECONSTRUCTION", SOURCE_IDS[1], "printed page 1 compatible W row with the complete Z row", OBSERVATION_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if either source changes; the sealed exact share leaves the direct on-shell interval; its complement "
        "leaves the compatible W/Z squared interval; any uncertainty is widened; the inconsistent aggregate is "
        "deleted, used as a second law, or relabelled as an SFT result; or target data alter the formal survivor."
    ),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "EXPERIMENT_ID", "OBSERVATION_LABEL", "ObservationalEmpiricalPhysicsProgram",
    "SOURCE_FILES", "SOURCE_HASH", "SOURCE_IDS", "SOURCE_PATH", "SPEC",
)
