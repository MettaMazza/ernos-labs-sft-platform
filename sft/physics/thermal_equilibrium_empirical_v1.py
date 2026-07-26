"""Post-seal thermometry and thermal-noise test of Claim 043."""

from dataclasses import replace

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    GeneratedEmpiricalPhysicsProgram,
    empirical_dimensions,
)
from sft.physics.thermal_equilibrium_response_terminal_law_v1 import theorem_certificate


CLAIM_ID = "SFT-PHYS-VALIDATION-THERMAL-EQUILIBRIUM-044"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-THERMAL-EQUILIBRIUM-044"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/thermal-equilibrium-postseal-source-record.json"
SOURCE_HASH = "sha256:8048a2397c064290a0b948b4238b4133c1a2e5c76a72ecf0c47222c9a951d7b5"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/nist-codata-2022-allascii.txt", "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67"),
    ("experiments/external_sources/physics/snapshots/nist-acoustic-boltzmann-2017.pdf", "sha256:1cbb21f0e5817270b5e028105aa79fea22017fd84130c2c4b79d1492fb37e418"),
    ("experiments/external_sources/physics/snapshots/nist-electronic-boltzmann-2011.pdf", "sha256:187066b5390d57a3c058e0a34f6c7803a659045ba714ca4b25eed7b84b212bbb"),
)
SOURCE_IDS = (
    "NIST-CODATA-2022-BOLTZMANN",
    "NIM-NIST-ACOUSTIC-BOLTZMANN-2017",
    "NIST-JOHNSON-NOISE-BOLTZMANN-2011",
)
OBSERVATION_LABEL = "sealed-thermal-equilibrium__two-independent-thermometry-intervals-and-noise-response-pass__formal-coordinate-limits-retained"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(
            super().registration,
            provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
        )


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Post-seal acoustic and Johnson-noise thermometry test",
    statement=(
        "After the complete temperature, finite equilibrium and fluctuation-response law is sealed, "
        "the exact SI Boltzmann carrier and two physically distinct thermometry determinations are opened. "
        "Both complete measured intervals contain the exact carrier. Acoustic thermometry independently ties "
        "temperature to mean kinetic energy, while Johnson-noise thermometry measures thermal noise response to "
        "temperature and resistance. The external records do not report the internal dyadic population ladder or "
        "the three-quarter/quarter Fold coordinates as universal measured values, and that limitation is retained."
    ),
    dependencies=(
        "SFT-PHYS-THERMAL-EQUILIBRIUM-RESPONSE-TERMINAL-043",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis product of the sealed thermal law, exact source-bound intervals, target custody, complete row retention and formal/measurement separation.",
    grammar_boundary="The sealed finite-population theorem; exact SI k_B; the complete acoustic and electronic k_B standard-uncertainty intervals; the kinetic-temperature and Johnson-noise relation rows; both explicit nonmeasurement boundaries; and every source/custody row.",
    dimensions=empirical_dimensions(
        "sealed-thermal-law-versus-complete-acoustic-and-Johnson-noise-vector",
        "Claim 043 and its 256-form survivor were fixed before the three target snapshots were bound.",
    ),
    exact_result=(
        "With all values carried as exact integers over 10^30 J/K, exact SI k_B is 13806490/10^30. "
        "The acoustic result is (13806484 +/- 28)/10^30 and therefore gives [13806456,13806512]/10^30; "
        "the Johnson-noise result is (13806510 +/- 170)/10^30 and gives [13806340,13806680]/10^30. "
        "Both intervals contain the exact carrier. The two measurement routes are physically distinct. The acoustic "
        "record identifies thermodynamic temperature with mean kinetic energy, and the electronic record reports "
        "Johnson noise power as jointly dependent on temperature and resistance to one part per million in its "
        "declared regime. No external row claims the Fold dyadic ladder or 3/4:1/4 response coordinates as universal measured values."
    ),
    induction_base="The admitted formal receipt fixes the finite mean, half-One equilibrium and complementary response structure before any target is released.",
    induction_step="Each additional measurement route, uncertainty endpoint and limitation row is retained exactly once and cannot alter the formal survivor.",
    exclusions=(
        "no target readable by the formal generator",
        "no fitted Boltzmann carrier, temperature scale or response coefficient",
        "no conventional continuum distribution imported into the formal proof",
        "no claim that the dyadic ladder or 3/4:1/4 coordinates were directly measured",
        "no omitted unfavorable, uncertainty or applicability row",
        "no numerical-zero, negative, irrational, imaginary, floating, NaN, continuum or completed-infinity Fold proof magnitude",
    ),
    operational_witnesses=(
        ("temperature", "The exact finite mean and total identity are closed.", theorem_certificate()["temperature"]),
        ("equilibrium", "The complete paired-population and canonical censuses are closed.", theorem_certificate()["equilibrium"] and theorem_certificate()["canonical"] and theorem_certificate()["weights"]),
        ("response", "The complementary fluctuation-response and deterministic cycle are closed.", theorem_certificate()["fluctuation"] and theorem_certificate()["noise"]),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=tuple(
        ExternalTargetRow(target, source, description, OBSERVATION_LABEL)
        for target, source, description in (
            ("EXACT-KB", SOURCE_IDS[0], "Exact SI Boltzmann carrier"),
            ("ACOUSTIC-THERMOMETRY", SOURCE_IDS[1], "Acoustic k_B interval and kinetic-temperature relation"),
            ("JOHNSON-NOISE-THERMOMETRY", SOURCE_IDS[2], "Electronic k_B interval and thermal-noise response relation"),
        )
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if any source or row changes; either complete measured interval excludes exact SI k_B; the routes are "
        "not physically distinct; the kinetic-temperature or Johnson-noise response row is absent; a limitation row "
        "is omitted; an internal Fold coordinate is relabelled as directly measured; or target data alter the formal survivor."
    ),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "EXPERIMENT_ID", "OBSERVATION_LABEL", "ObservationalEmpiricalPhysicsProgram",
    "SOURCE_FILES", "SOURCE_HASH", "SOURCE_IDS", "SOURCE_PATH", "SPEC",
)
