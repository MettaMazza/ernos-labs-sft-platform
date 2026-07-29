"""Complete observational comparison for formal Tesla-family Claims 078-081."""

from dataclasses import replace

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    GeneratedEmpiricalPhysicsProgram,
    empirical_dimensions,
)
from sft.physics.tesla_resonance_family_law_v1 import (
    bounded_round_trip,
    odd_quarter_count,
    orientation_inventory,
    resonant_transfer_ledger,
)
from fractions import Fraction


CLAIM_ID = "SFT-PHYS-VALIDATION-TESLA-RESONANCE-FAMILY-082"
EXPERIMENT_ID = "SFT-EXP-PHYS-TESLA-RESONANCE-FAMILY-082"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/tesla-resonance-family-source-record-2026-07-28.json"
SOURCE_HASH = "sha256:31c3f9a9332c91994b73504e6061a5de3bc712a45b8ec6bd2f1d48504af2bdf5"
PREREGISTRATION_PATH = "experiments/physics/SFT-EXP-PHYS-TESLA-RESONANCE-FAMILY-082/source_identity_preregistration.json"
PREREGISTRATION_HASH = "sha256:145edc6e472211ca64cf67f0537f817c78d2f76af4d20d95b0a844b70b4fe2b6"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/nist-jres-quarter-wave-1935.pdf", "sha256:83488f03a4716728b2e85bafbb7002ae56f5d5923383785f5d955b105810211c"),
    ("experiments/external_sources/physics/snapshots/nist-srdata-diamond-modes-z00435.html", "sha256:1b558723d0bbc5bcf12c2710564b6bb0c6e44ea6dddd3fd5efdbcecf5f3d3cdb"),
    ("experiments/external_sources/physics/snapshots/nist-coherent-resonant-transfer-2007.pdf", "sha256:eff098b1861b28ad2b61af5f5474ab8a9e77a099aaf41dc54902e5446d132c64"),
    ("experiments/external_sources/physics/snapshots/nasa-earth-ionosphere-resonance-2003.pdf", "sha256:1a829cf7137cf62ab218017bd868f7921552e4314dc9cd465e4bcc32505a4a96"),
    ("experiments/external_sources/physics/snapshots/nasa-schumann-observation-2011.pdf", "sha256:dec386730050b71da8c3a156d40b6e57c617420128329e7e216e49727eb0e61f"),
)
SOURCE_IDS = (
    "NIST-JRES-QUARTER-WAVE-1935",
    "NIST-SRDATA-DIAMOND-MODES-Z00435",
    "NIST-COHERENT-RESONANT-TRANSFER-2007",
    "NASA-EARTH-IONOSPHERE-RESONANCE-2003",
    "NASA-SCHUMANN-OBSERVATION-2011",
)
OBSERVATION_LABEL = "complete-measured-resonance-family__bounded-and-odd-quarter-modes__one-longitudinal-two-transverse__resonant-transfer-with-loss__earth-cavity-without-source-free-power"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Complete measured Tesla-resonance family and power-boundary comparison",
    statement=(
        "The four sealed V3 laws are compared with five complete institutional records. A measured NBS quarter-wave line responds near its third and other odd harmonics; the NIST diamond record retains round-trip echoes and one longitudinal plus two separately measured transverse modes; a NIST resonant cavity transfers, stores and retrieves a prepared state while retaining decay and fidelity limits; and NASA records the bounded Earth-ionosphere mode family. The Earth modes do not equal the quarter-wave odd sequence, and proposed wireless or free-energy applications are not measurements of source-free extraction. Every favorable, adverse, limitation and delivery-type row remains held."
    ),
    dependencies=(
        "SFT-PHYS-TESLA-BOUNDED-CAVITY-078",
        "SFT-PHYS-TESLA-ODD-QUARTER-WAVE-079",
        "SFT-PHYS-TESLA-LONGITUDINAL-TRANSVERSE-080",
        "SFT-PHYS-TESLA-RESONANT-TRANSFER-081",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis product of the four sealed resonance laws, five source-bound external records, complete favorable/adverse row retention, observational provenance, measurement separation and no-extra-rule closure.",
    grammar_boundary="Formal Claims 078-081; all five frozen institutional source identities and captured artifacts; every bounded, odd-quarter, orientation, transfer, loss, Earth-cavity, speculative-power and delivery-type row; and all 256 registered comparison forms.",
    dimensions=empirical_dimensions(
        "sealed-tesla-resonance-family-versus-complete-five-source-observation-vector",
        "The exact four-claim formal chain remains fixed while every named source row, including the non-odd Earth sequence and unsupported source-free-power interpretation, is retained.",
    ),
    exact_result=(
        "The complete captured record supports bounded discrete recurrence, measured quarter-wave third and other odd harmonics, one longitudinal plus two transverse rank-three roles, and resonant connected-endpoint transfer with cavity storage. It simultaneously forces the empirical boundary: material mode speeds differ; transfer has decay, loss and fidelity limits; the Earth spherical-cavity sequence is not the quarter-wave odd sequence; and no captured experiment demonstrates source-free or unlimited power extraction."
    ),
    induction_base="The four formal predecessors fix bounded recurrence, odd-quarter closure, the complete orientation inventory and the conserved transfer ledger before this combined record is assembled.",
    induction_step="Each additional source and observation row is appended once with its source identity, classification, limitation and adverse content, without changing any sealed formal survivor.",
    exclusions=(
        "no historical Tesla reputation or V1/V2 result as a proof premise",
        "no measured frequency, apparatus length, gain or fidelity selecting a formal survivor",
        "no omission of the non-odd Earth sequence, material-speed distinctions, loss, decay, fidelity or delivery-type mismatch",
        "no inference from a proposed application to a measured source-free-energy result",
        "no universal efficiency, unlimited Earth-power or identity-of-substances claim",
        "no numerical-zero, negative, irrational, imaginary, floating or completed-infinite magnitude in the formal derivation",
    ),
    operational_witnesses=(
        ("bounded", "Seven cells retain the exact fourteen-act outward-return witness.", bounded_round_trip(7) == 14),
        ("odd", "The first five opposed-role quarter counts are the odd family.", tuple(odd_quarter_count(n) for n in range(1, 6)) == (1, 3, 5, 7, 9)),
        ("orientation", "Rank three retains one longitudinal and two transverse roles.", orientation_inventory() == {"longitudinal": 1, "transverse": 2, "complete": 3}),
        ("ledger", "A distinct positive transfer partition exactly reconstructs the One.", resonant_transfer_ledger(Fraction(1, 4), Fraction(1, 2), Fraction(1, 4))["reconstructed"] == 1),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=tuple(
        ExternalTargetRow(target_id, source_id, description, OBSERVATION_LABEL)
        for target_id, source_id, description in (
            ("QUARTER-WAVE-ODD-HARMONIC-STRUCTURE", SOURCE_IDS[0], "Measured quarter-wave third and other odd-harmonic response with nonideal line-length and gain boundaries"),
            ("LONGITUDINAL-AND-TWO-TRANSVERSE-MODES", SOURCE_IDS[1], "Evaluated round-trip ultrasonic record with one longitudinal and two transverse 111-direction rows"),
            ("RESONANT-CAVITY-TRANSFER-AND-STORAGE", SOURCE_IDS[2], "Measured resonant state transfer, storage, retrieval, decay and fidelity record"),
            ("EARTH-CAVITY-MODES-AND-POWER-BOUNDARY", SOURCE_IDS[3], "Measured Earth-ionosphere cavity modes plus explicit proposed-application versus measurement boundary"),
            ("EARTH-CAVITY-SATELLITE-DETECTION", SOURCE_IDS[4], "NASA satellite detection record with retained legacy-locator media-type mismatch"),
        )
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if any formal receipt, preregistration, source artifact or row changes; if quarter-wave odd response, the complete orientation inventory, resonant transfer/storage, or Earth-cavity detection is absent; if any loss, speed distinction, non-odd Earth sequence, speculative-power status or delivery mismatch is concealed; or if observation is allowed to alter a formal survivor."
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
