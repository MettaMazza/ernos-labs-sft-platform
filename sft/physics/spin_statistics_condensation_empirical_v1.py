"""Post-seal physical test of the finite spin-statistics and condensation law."""

from dataclasses import replace

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    GeneratedEmpiricalPhysicsProgram,
    empirical_dimensions,
)
from sft.physics.spin_statistics_condensation_terminal_law_v1 import theorem_certificate


CLAIM_ID = "SFT-PHYS-VALIDATION-SPIN-STATISTICS-CONDENSATION-046"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-SPIN-STATISTICS-CONDENSATION-046"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/spin-statistics-condensation-postseal-source-record.json"
SOURCE_HASH = "sha256:9d24c12e31092f34854c71c3dce2b355dd1d1f2ae6347a03bbea45ef01508cfa"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/ensher-bec-ground-occupation-1996.pdf", "sha256:9086058e1c750191fb36eab5acf7c65da1aa7f0e4cdcf643887e282ad3920c93"),
    ("experiments/external_sources/physics/snapshots/nist-pauli-blocking-2001.html", "sha256:82555a4057e339aef96cde7484fe3fbd190a8d2cecbf4c3de73996af473b9af7"),
    ("experiments/external_sources/physics/snapshots/rauch-spinor-rotation-1975.pdf", "sha256:11638b8c2aaf8fbdd96aa50c9496bb9f7597b308f19d780ab779cc2dd6752824"),
)
SOURCE_IDS = (
    "APS-JILA-BEC-GROUND-OCCUPATION-1996",
    "NIST-JILA-PAULI-BLOCKING-2001",
    "RAUCH-COHERENT-SPINOR-ROTATION-1975",
)
OBSERVATION_LABEL = "sealed-spin-statistics-condensation__finite-bec-pauli-blocking-and-two-turn-spinor-pass__scale-boundaries-retained"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Post-seal finite BEC, Pauli-blocking and two-turn spinor test",
    statement=(
        "After the complete finite spin-statistics and condensation law was officially sealed, three primary physical records were opened. A finite rubidium-87 Bose gas exhibits measured ground-state occupation that rises as temperature is lowered and a sharp transition at (94 +/- 5)/100 of its independently defined trap scale. A two-spin-state potassium-40 Fermi gas directly exhibits Pauli blocking, including a reported factor-two collision-cross-section reduction. Neutron interferometry measures a fermion return of 704 +/- 38 degrees, whose complete interval contains the sealed two-turn 720-degree correspondence. The trap-specific BEC temperature and collision-response magnitude remain external scale records; they are not used to manufacture the formal occupation or lock law."
    ),
    dependencies=(
        "SFT-PHYS-SPIN-STATISTICS-CONDENSATION-TERMINAL-045",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis product of the sealed spin-statistics law, finite BEC record, Pauli-blocking record, two-turn spinor interval, custody, full-row retention and formal/measurement separation.",
    grammar_boundary="The admitted 256-form formal survivor; all three bound primary records; the complete BEC transition interval and direction rows; the complete Pauli rows; the complete spinor interval and return rows; and every custody, limitation and adverse-control row.",
    dimensions=empirical_dimensions(
        "sealed-spin-statistics-condensation-law-versus-complete-finite-BEC-Pauli-and-spinor-vector",
        "Claim 045 and receipt sha256:f71da5b86f99d6569a1f33dc6fc37024cc5d458b12e625c5dbc4faf3c33ccda7 were fixed before the three target snapshots were bound.",
    ),
    exact_result=(
        "The finite Bose record measures ground-state occupation, its increase under cooling, and a sharp transition at (94 +/- 5)/100 of the declared trap scale, giving the exact interval [89,99]/100. The finite two-spin-state Fermi record directly observes Pauli blocking and a factor-two reduction in effective collision cross section. The sealed alternating-state return is two complete turns, corresponding to 720 degrees; the neutron-interferometry result is 704 +/- 38 degrees, giving [666,742], which contains 720. All three physical routes agree with their respective sealed structural distinctions. The BEC scale ratio and collision-response factor are retained as external apparatus-dependent measurements rather than relabelled universal Fold proof scalars."
    ),
    induction_base="The admitted formal receipt fixes the occupation counts, exclusion, unbounded finite preserving multiplicity, three-to-one spin composition, two-turn return and cold ground lock before target release.",
    induction_step="Each added external interval, direction, finite-population, response and limitation row is retained exactly once and cannot alter the sealed formal survivor.",
    exclusions=(
        "no BEC temperature, Pauli response, particle species or spinor angle readable by the formal generator",
        "no fitted occupation ceiling, critical temperature, collision factor or rotation interval",
        "no continuum Fermi-Dirac or Bose-Einstein function imported into the formal proof",
        "no relabelling of the apparatus-specific BEC ratio or collision reduction as a universal Fold proof scalar",
        "no omitted unfavorable, uncertainty, finite-population or applicability row",
        "no conventional numerical-nothingness, negative, irrational, imaginary, floating, NaN or continuum Fold proof magnitude",
    ),
    operational_witnesses=(
        ("occupation", "The complete finite preserving and alternating occupation censuses are closed.", theorem_certificate()["occupation"]),
        ("weights", "Every admitted finite occupation measure is exact and normalized.", theorem_certificate()["weights"]),
        ("spin", "The two-label composition and typed return orbits are closed.", theorem_certificate()["spin"]),
        ("condensation", "The first finite lock crossing and unique minimum-throw ground word are closed.", theorem_certificate()["cold"]),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=tuple(
        ExternalTargetRow(target, source, description, OBSERVATION_LABEL)
        for target, source, description in (
            ("FINITE-BEC", SOURCE_IDS[0], "Finite Bose-gas ground occupation, cooling direction and transition interval"),
            ("PAULI-BLOCKING", SOURCE_IDS[1], "Direct two-spin-state Pauli-blocking measurement"),
            ("TWO-TURN-SPINOR", SOURCE_IDS[2], "Neutron-interferometry two-turn return interval"),
        )
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if any source or row changes; finite bosons fail to accumulate in the measured ground state under cooling; Pauli blocking is absent in the declared identical-fermion regime; the complete spinor interval excludes 720 degrees; a trap-specific or response-specific value is relabelled as a universal formal scalar; an unfavorable row is omitted; or target data alter the sealed formal survivor."
    ),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "EXPERIMENT_ID",
    "OBSERVATION_LABEL",
    "ObservationalEmpiricalPhysicsProgram",
    "SOURCE_FILES",
    "SOURCE_HASH",
    "SOURCE_IDS",
    "SOURCE_PATH",
    "SPEC",
)
