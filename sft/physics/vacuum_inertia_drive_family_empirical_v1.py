"""Complete observational comparison for formal vacuum/inertia Claims 083-086."""

from dataclasses import replace
from fractions import Fraction

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    GeneratedEmpiricalPhysicsProgram,
    empirical_dimensions,
)
from sft.physics.vacuum_inertia_drive_family_law_v1 import (
    complete_drive_response_ledger,
    covariation_record,
    finite_depth_floor,
    local_resonant_drive,
)


CLAIM_ID = "SFT-PHYS-VALIDATION-VACUUM-INERTIA-DRIVE-FAMILY-087"
EXPERIMENT_ID = "SFT-EXP-PHYS-VACUUM-INERTIA-DRIVE-FAMILY-087"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/vacuum-inertia-drive-family-source-record-2026-07-28.json"
SOURCE_HASH = "sha256:015d584d013c1bb3daaff227cc547515d0a3c1c8f51d7488fb1c33c567f4c59b"
PREREGISTRATION_PATH = "experiments/physics/SFT-EXP-PHYS-VACUUM-INERTIA-DRIVE-FAMILY-087/source_identity_preregistration.json"
PREREGISTRATION_HASH = "sha256:2f7518d7a2a5b23cb7cde4a632d975b2e52fcabf9305b7f71e58bb1578524256"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/navair-pax205-inertial-mass-reduction-device.pdf", "sha256:6ce3f01a0e0e7cde89c0e0584a3e6e8ecaf43fc4cfd1daaae8e347434c8e02d7"),
    ("experiments/external_sources/physics/snapshots/navair-pax205-patent-documents.pdf", "sha256:75c8ec19ce7d392d4eb50b8bce4a54b55cd933cac955d170d3ce05ca1da7ef56"),
    ("experiments/external_sources/physics/snapshots/navair-pax205-patent-documents-vision-ocr.json", "sha256:ad9b37fdaab166c6e9d0e45d2e48dc46ff6b67dd1cff457c4e427008faabb5b0"),
    ("experiments/external_sources/physics/snapshots/nist-zero-point-fluctuations-2015.html", "sha256:e829ac861cca9f84f43f752465b4ee8801fb07fac76e41f0df4de98ff5f54832"),
    ("experiments/external_sources/physics/snapshots/nist-casimir-vacuum-forces-2013.html", "sha256:906e3d92d1e664daa5070bcf8cdafa4bf20fc8bb003346946870fa9b64ee7b1f"),
    ("experiments/external_sources/physics/snapshots/cnes-microscope-final.html", "sha256:65a86753705aaa80f819e833d1ca4e13f0491e56b58a218c4cddb492c9887f12"),
)
SOURCE_IDS = (
    "NAVAIR-PAX205-INERTIAL-MASS-REDUCTION-DEVICE",
    "NAVAIR-PAX205-PATENT-PROSECUTION-RECORD",
    "NIST-ZERO-POINT-FLUCTUATIONS-2015",
    "NIST-CASIMIR-VACUUM-FORCES-2013",
    "CNES-MICROSCOPE-FINAL-2022",
)
OBSERVATION_LABEL = "complete-vacuum-inertia-drive-record__official-mechanism-described__no-public-prototype-measurement-in-record__nonempty-vacuum-and-casimir-response-measured__ordinary-unity-constrained__pump-and-restoration-ledger-retained"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Complete measured vacuum/inertia-drive correspondence and apparatus boundary",
    statement=(
        "The four sealed V3 laws are compared with five official source identities. Navy records describe a driven local-vacuum/inertia mechanism while explicitly retaining theoretical, proposed-experiment and no-prototype status in the captured record. NIST measurements establish nonempty ground-state response and boundary-dependent vacuum interaction while retaining coherent-pump and no-ground-state-work boundaries. CNES constrains ordinary inertial/gravitational unity but is not a driven-inertia apparatus test. Every favorable, adverse, absent, untested and scope-limiting row remains held."
    ),
    dependencies=(
        "SFT-PHYS-VACUUM-LOCAL-RESONANT-DRIVE-083",
        "SFT-PHYS-VACUUM-INERTIA-COVARIATION-084",
        "SFT-PHYS-VACUUM-INERTIA-POSITIVE-FLOOR-085",
        "SFT-PHYS-VACUUM-INERTIA-COMPLETE-LEDGER-086",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis product of the four sealed vacuum/inertia-drive laws, five source-bound official records, complete favorable/adverse/absent/untested retention, observational provenance, measurement separation and no-extra-rule closure.",
    grammar_boundary="Formal Claims 083-086; all five frozen institutional source identities and six captured artifacts; every mechanism, theoretical-status, prototype-status, nonempty-vacuum, Casimir, pump-ledger, ordinary-unity and engineered-control-scope row; and all 256 registered comparison forms.",
    dimensions=empirical_dimensions(
        "sealed-vacuum-inertia-drive-family-versus-complete-five-source-observation-vector",
        "The exact four-claim formal chain remains fixed while the official mechanism, no-prototype status, measured vacuum response, ordinary unity constraint and all apparatus boundaries are retained together.",
    ),
    exact_result=(
        "The complete official record supports the external correspondence of the sealed structural family: a driven local-vacuum/inertia mechanism is explicitly described; nonempty vacuum response and boundary-dependent vacuum interaction are measured; and ordinary inertial/gravitational unity is constrained. It simultaneously forces the apparatus boundary: the captured Navy records call the device a theoretical concept, state that no prototype yet existed and propose later experiment; CNES does not test driven inertia; NIST retains coherent pump energy and forbids removal of real work from ground fluctuations. Therefore the exact structural channel, positive finite-depth bound and complete ledger remain admitted, while a useful device magnitude, completed public inertial-mass-reduction measurement and source-free cyclic gain are not claimed by this comparison."
    ),
    induction_base="The four formal predecessors fix local drive, unity co-variation, the finite-depth positive floor and the complete returned-cycle ledger before the combined apparatus record is assembled.",
    induction_step="Each additional official source and row is appended once with its identity, classification, limitation and absent or adverse content, without changing any sealed formal survivor.",
    exclusions=(
        "no V1/V2 executable, patent formula, target magnitude or desired apparatus result as a proof premise",
        "no patent issuance, proposed experiment or concept paper relabelled as a measured device effect",
        "no absence of a public prototype measurement relabelled as falsification of the sealed exact structural channel",
        "no MICROSCOPE equivalence result relabelled as a driven local-inertia-control test",
        "no omission of pump energy, restoration cost, no-ground-state-work or apparatus-status rows",
        "no source-free energy, universal efficiency, useful propulsion or dimensional minimum-mass claim",
        "no numerical-zero, negative, irrational, imaginary, floating or completed-infinite magnitude in the formal derivation",
    ),
    operational_witnesses=(
        ("drive", "The historical one-third to one-quarter probe retains exact transfer one-twelfth.", local_resonant_drive(Fraction(1, 3), Fraction(1, 4))["transferred"] == Fraction(1, 12)),
        ("covariation", "Both unity-related carriers change by the same exact one-twelfth.", covariation_record(Fraction(1, 3), Fraction(1, 4))["vacuum_change"] == covariation_record(Fraction(1, 3), Fraction(1, 4))["inertia_change"] == Fraction(1, 12)),
        ("floor", "Depth three retains the exact positive one-sixteenth carrier.", finite_depth_floor(3) == Fraction(1, 16)),
        ("ledger", "The complete drive-response-restoration trace closes without erasing the event.", complete_drive_response_ledger(Fraction(1, 3), Fraction(1, 4))["closed"] is True),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=tuple(
        ExternalTargetRow(target_id, source_id, description, OBSERVATION_LABEL)
        for target_id, source_id, description in (
            ("PATENT-MECHANISM-AND-APPARATUS-CLAIM", SOURCE_IDS[0], "Official Navy concept mechanism with explicit theoretical/no-prototype development boundary"),
            ("PUBLIC-DEMONSTRATOR-AND-TEST-STATUS", SOURCE_IDS[1], "Official prosecution and concept record retaining proposed-experiment rather than completed-effect status"),
            ("NONEMPTY-VACUUM-AND-PUMP-BOUNDARY", SOURCE_IDS[2], "Measured ground-state response with coherent-pump and no-real-ground-work boundaries"),
            ("BOUNDARY-DEPENDENT-VACUUM-INTERACTION", SOURCE_IDS[3], "Measured and calculated Casimir interaction at held boundaries"),
            ("INERTIAL-GRAVITATIONAL-UNITY-AND-SCOPE-CONTROL", SOURCE_IDS[4], "Precision ordinary unity comparison that does not drive local vacuum or inertia"),
        )
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if any formal receipt, preregistration, source artifact or row changes; if the official mechanism description, no-prototype/proposed-experiment status, measured nonempty vacuum response, Casimir interaction, ordinary unity constraint or pump/restoration boundary is omitted; if patent status is relabelled as measurement; if lack of public device data is relabelled as formal falsification; or if observation alters a formal survivor."
    ),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "EXPERIMENT_ID",
    "OBSERVATION_LABEL",
    "ObservationalEmpiricalPhysicsProgram",
    "PREREGISTRATION_HASH",
    "PREREGISTRATION_PATH",
    "SOURCE_FILES",
    "SOURCE_HASH",
    "SOURCE_IDS",
    "SOURCE_PATH",
    "SPEC",
)
