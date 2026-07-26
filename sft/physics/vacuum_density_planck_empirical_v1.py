"""Post-seal Planck/CODATA test of the terminal vacuum-density scale law."""

from __future__ import annotations

from dataclasses import replace

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    GeneratedEmpiricalPhysicsProgram,
    empirical_dimensions,
)
from sft.physics.vacuum_density_scale_terminal_law_v1 import theorem_certificate


CLAIM_ID = "SFT-PHYS-VALIDATION-VACUUM-DENSITY-SCALE-036"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-VACUUM-DENSITY-SCALE-036"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/vacuum-density-planck-postseal-source-record.json"
SOURCE_HASH = "sha256:a0c8d15b9ab666329943cac4d5899ff5617871d1e1d9d6f60e5d4dd22eed4652"
PDF_PATH = "experiments/external_sources/physics/snapshots/planck-baseline-params-2018-68pc-v2.pdf"
PDF_HASH = "sha256:03038805021f2f894e09f4b21b0f20418570e352822f095abcc085942919da70"
CODATA_PATH = "experiments/external_sources/physics/snapshots/nist-codata-2022-allascii.txt"
CODATA_HASH = "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67"
SOURCE_IDS = ("PLANCK-PLA-BASE-NRUN-TTTEEE-BAO-LENSING-68PC", "NIST-CODATA-2022-EXACT-C")
OBSERVATION_LABEL = (
    "sealed-vacuum-share-and-normalized-Lambda__Planck-complete-68pc-intervals__"
    "CODATA-exact-speed-transport__local-global-type-control__corrected-primary-transcription__no-fit"
)


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Post-seal Planck/CODATA test of the Fold vacuum-density scale law",
    statement=(
        "After the formal vacuum law is admitted, the complete Planck page-225 68-percent rows and exact CODATA "
        "speed are opened. The exact terminal vacuum share 11/16 lies inside Planck's 0.6889 +/- 0.0056 interval. "
        "The separately forced normalized magnitude 33/16 lies inside the exact transported interval "
        "3(0.6889 +/- 0.0056). The Hubble interval and exact limiting speed transport the sealed coefficient to a "
        "positive exact dimensional Lambda interval in inverse square megaparsecs. The local One/2^20 floor lies "
        "outside the global vacuum-fraction interval, confirming that direct unscaled identification is a type error."
    ),
    dependencies=(
        "SFT-PHYS-VACUUM-DENSITY-SCALE-TERMINAL-035",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001",
    ),
    generation_rule=(
        "Generate the complete eight-axis product of sealed vacuum relation, Planck/CODATA target, source provenance, "
        "capability-closed isolation, proof/measurement separation, complete row and correction retention, successor "
        "closure and extension."
    ),
    grammar_boundary=(
        "The admitted exact local floor, finite mode ledger, 11/16 global share and 33/16 normalized magnitude; "
        "Planck table 12.16 page-225 H0, Omega_Lambda and Omega_m rows with complete uncertainties; CODATA exact c; "
        "the older H0 transcription correction; and the local/global adverse type control."
    ),
    dimensions=empirical_dimensions(
        "sealed-vacuum-density-law-versus-complete-Planck-CODATA-record",
        "The formal receipt is fixed before the newly retrieved primary PDF and target record are opened.",
    ),
    exact_result=(
        "The exact Fold vacuum share 11/16 is inside Planck's interval [6833/10000,1389/2000]. The normalized "
        "Fold magnitude 33/16 is inside [20499/10000,4167/2000]=3 times that interval. Using page-225 "
        "H0=67.68 +/- 0.42 km s^-1 Mpc^-1 and exact c=299792.458 km s^-1 transports Lambda to the exact positive "
        "interval [(33/16)(67.26/c)^2,(33/16)(68.10/c)^2] Mpc^-2. One/2^20 is below the global interval and is "
        "therefore retained only as the separately typed local boundary-energy floor."
    ),
    induction_base=(
        "The admitted formal claim fixes the local floor, global share, normalized coefficient and transport law "
        "before target release."
    ),
    induction_step=(
        "Each additional registered source row, uncertainty endpoint or correction is appended once without changing "
        "the sealed coefficient; a changed or omitted row halts the comparison."
    ),
    exclusions=(
        "no Planck or CODATA value readable by the formal candidate generator or independent formal validator",
        "no fit, recalibration or coefficient choice from Omega_Lambda or H0",
        "no claim of historical blindness: V1/V2 targets and an older local transcription were known",
        "no silent reuse of the older 67.66 H0 transcription where primary page 225 reports 67.68",
        "no direct equality between One/2^20, a raw radiative sum, Omega_Lambda and dimensional Lambda",
        "no numerical-zero, negative, irrational, imaginary or floating Fold proof magnitude",
    ),
    operational_witnesses=(
        ("formal-floor", "The local floor is exact and independently closed.", theorem_certificate()["energy_floor"].denominator == 2 ** 20),
        ("formal-radiative", "The finite complete radiative ledger closes at every generated depth.", theorem_certificate()["finite_radiative_ledgers_close"]),
        ("formal-lambda", "The normalized coefficient is exact and scale transport is covariant.", theorem_certificate()["normalized_cosmological_constant"].numerator == 33 and theorem_certificate()["scale_covariance"]),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=(
        ExternalTargetRow("PLANCK-VACUUM-FRACTION", SOURCE_IDS[0], "Page 225 Omega_Lambda central value and 68-percent uncertainty", OBSERVATION_LABEL),
        ExternalTargetRow("PLANCK-MATTER-CLOSURE", SOURCE_IDS[0], "Page 225 Omega_m central value and 68-percent uncertainty", OBSERVATION_LABEL),
        ExternalTargetRow("PLANCK-HUBBLE-TRANSPORT", SOURCE_IDS[0], "Page 225 H0 central value and 68-percent uncertainty", OBSERVATION_LABEL),
        ExternalTargetRow("CODATA-EXACT-SPEED", SOURCE_IDS[1], "Exact speed of light in vacuum", OBSERVATION_LABEL),
        ExternalTargetRow("TRANSCRIPTION-AND-TYPE-CONTROLS", SOURCE_IDS[0], "Corrected H0 row and local/global adverse type control", OBSERVATION_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if any source identity or registered row changes; if 11/16 leaves the complete Planck vacuum interval; "
        "if 33/16 leaves its exact three-direction transported interval; if the Planck central budget ceases to close "
        "at the One; if dimensional transport is nonpositive or scale-inconsistent; if One/2^20 is relabeled as the "
        "global fraction; if the older H0 transcription is silently substituted; or if any target changes the formal survivor."
    ),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "CODATA_HASH", "CODATA_PATH", "EXPERIMENT_ID", "OBSERVATION_LABEL",
    "ObservationalEmpiricalPhysicsProgram", "PDF_HASH", "PDF_PATH", "SOURCE_HASH", "SOURCE_IDS",
    "SOURCE_PATH", "SPEC",
)
