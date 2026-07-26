"""Post-seal physical test of the Fold Bell factorization boundary."""

from dataclasses import replace

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    GeneratedEmpiricalPhysicsProgram,
    empirical_dimensions,
)
from sft.physics.quantum_support_uncertainty_terminal_law_v1 import theorem_certificate


CLAIM_ID = "SFT-PHYS-VALIDATION-QUANTUM-SUPPORT-UNCERTAINTY-050"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-QUANTUM-SUPPORT-UNCERTAINTY-050"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/quantum-support-bell-postseal-source-record.json"
SOURCE_HASH = "sha256:51df41e3e1669d853ea3894b3ce039f6f631ad75d519bc632f26b013ff6a7ab1"
SOURCE_FILE = "experiments/external_sources/physics/snapshots/storz-loophole-free-bell-2023.html"
SOURCE_FILE_HASH = "sha256:fabe97e4970990cef6246f0541a8b9e80e47b0df58f10234b8f8155d1b4ade81"
SOURCE_IDS = ("NATURE-STORZ-LOOPHOLE-FREE-BELL-2023",)
OBSERVATION_LABEL = "sealed-local-factorization-boundary__measured-CHSH-interval-above-two__locality-memory-and-assumption-boundaries-retained__no-ontic-randomness-import"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Post-seal superconducting-circuit test of the Fold Bell factorization boundary",
    statement=(
        "After Claim 049 and its complete local-response census were officially sealed, the primary Storz et al. "
        "record was bound. More than one million trials measured S=(20747 +/- 33)/10000. Its complete interval "
        "[20714,20780]/10000 lies above the local-factorization bound two, with a reported P value below 10^-108. "
        "The timing record also preserves space-like separation and the memory-robust analysis. The paper's "
        "measurement-independence assumption is retained rather than hidden: this result tests local factorization "
        "under the declared experimental conditions; it does not exclude every deterministic model and it does not "
        "import random setting generation as ontic nondeterminism."
    ),
    dependencies=(
        "SFT-PHYS-QUANTUM-SUPPORT-UNCERTAINTY-TERMINAL-049",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-PHYS-QUANTUM-BELL-001",
        "SFT-PHYS-QUANTUM-NO-SIGNALLING-001",
    ),
    generation_rule="Generate the complete eight-axis product of sealed Bell boundary, external interval, provenance, target isolation, proof/measurement separation, complete condition retention, successor closure and extension.",
    grammar_boundary="The admitted Claim 049 Bell-response census; the complete primary S interval, trial-count, significance, space-like timing, memory-analysis and measurement-independence records; and every stated interpretive limitation.",
    dimensions=empirical_dimensions(
        "sealed-local-factorization-law-versus-complete-superconducting-circuit-Bell-record",
        "Claim 049 and receipt sha256:1560f2e0de3870abac2bdc6575aa9811c4dc013d5a6d705e729a832dc451b79f were fixed before the target snapshot was retrieved.",
    ),
    exact_result=(
        "The exact measured S interval [20714,20780]/10000 lies wholly above the local-factorization bound two; "
        "its central excess exceeds twenty-two stated standard uncertainties and the reported P value is below "
        "10^-108 across more than one million trials. The complete timing intervals preserve space-like separation, "
        "and the analysis retains its memory control. This physically rejects the sealed local-factorization class "
        "under the source's declared conditions while preserving deterministic complete-record admissibility, "
        "no signalling, and the explicit measurement-independence assumption. The distinct Walsh support-count "
        "product remains a formal/computational result and is not relabelled as a variance measurement."
    ),
    induction_base="The complete sixteen-record local factorization census and its three-of-four bound were admitted before the primary Bell target was opened.",
    induction_step="Each additional registered trial, timing, analysis or assumption row is retained exactly once and cannot change the sealed formal survivor.",
    exclusions=(
        "no Bell value, trial result, significance record or timing record available to formal candidate selection",
        "no claim that a Bell violation excludes all deterministic or complete-record models",
        "no import of random-number generation as ontic nondeterminism",
        "no omission of the measurement-independence assumption or the authors' stated assumption boundary",
        "no relabelling of support cardinality as statistical moment variance",
        "no claim that this Bell experiment separately measures the Walsh support product",
        "no numerical-nothingness, negative, irrational, imaginary, floating, NaN, continuum or completed-infinity Fold proof magnitude",
    ),
    operational_witnesses=(
        ("support", "The complete dyadic support census is closed.", theorem_certificate()["walsh"]),
        ("joint", "The complete joint-factorability censuses and projections are closed.", theorem_certificate()["joints"]),
        ("bell", "Every local response pair obeys three-of-four while setting-inclusive support preserves no signalling.", theorem_certificate()["bell"]),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=(
        ExternalTargetRow("BELL-S-INTERVAL", SOURCE_IDS[0], "Complete measured CHSH-type S interval and local bound", OBSERVATION_LABEL),
        ExternalTargetRow("BELL-TRIALS-SIGNIFICANCE", SOURCE_IDS[0], "Trial lower bound, standard-uncertainty excess and P-value record", OBSERVATION_LABEL),
        ExternalTargetRow("BELL-SPACE-LIKE-TIMING", SOURCE_IDS[0], "Light-travel budget and trial-duration intervals", OBSERVATION_LABEL),
        ExternalTargetRow("BELL-MEMORY-CONTROL", SOURCE_IDS[0], "Memory-robust statistical analysis", OBSERVATION_LABEL),
        ExternalTargetRow("BELL-ASSUMPTION-BOUNDARY", SOURCE_IDS[0], "Measurement-independence and unavoidable-assumption statements", OBSERVATION_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if either source identity changes; the complete S interval touches or falls below two; the trial, "
        "significance, timing or memory records fail; measurement independence or any stated limitation is omitted; "
        "the result is presented as excluding all determinism; ontic randomness is imported; the Walsh support law "
        "is called a measured variance; or any target changes the sealed survivor."
    ),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "EXPERIMENT_ID", "OBSERVATION_LABEL", "ObservationalEmpiricalPhysicsProgram",
    "SOURCE_FILE", "SOURCE_FILE_HASH", "SOURCE_HASH", "SOURCE_IDS", "SOURCE_PATH", "SPEC",
)
