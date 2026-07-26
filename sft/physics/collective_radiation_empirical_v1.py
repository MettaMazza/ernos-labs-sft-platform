"""Post-seal empirical test of collective radiation response."""

from dataclasses import replace

from sft.engine import ProvenanceClass
from sft.physics.collective_radiation_response_terminal_law_v1 import theorem_certificate
from sft.physics.generated_empirical_law import EmpiricalPhysicsSpec, ExternalTargetRow, GeneratedEmpiricalPhysicsProgram, empirical_dimensions


CLAIM_ID = "SFT-PHYS-VALIDATION-COLLECTIVE-RADIATION-RESPONSE-042"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-COLLECTIVE-RADIATION-RESPONSE-042"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/collective-radiation-postseal-source-record.json"
SOURCE_HASH = "sha256:fb68982f853344dbb055e0a7bb51512d6b3f631044ae3e89b81c86ec019c7470"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/nist-blackbody-coblentz.html", "sha256:deb600e47fd138dfe82aef3271b19f2030cd7cd3e4fa202ef80f4f1ae82eec71"),
    ("experiments/external_sources/physics/snapshots/nist-diode-laser-linewidth.html", "sha256:7c0a9a1b4dc19b573cb6603f87453161508784ca59ec26ed698b0354bb7520b6"),
    ("experiments/external_sources/physics/snapshots/nist-acoustic-cavity-resonance.pdf", "sha256:f4dbf2b01604b8a6f26621bb8bafa856913e25158a8635f7454838ef5360f1b4"),
    ("experiments/external_sources/physics/snapshots/nasa-plasma-frequency-probe.html", "sha256:4fff15fe03f66e4009ca34e83f0d0ea02e66b2d40e92ee987ae46f437f39f36c"),
    ("experiments/external_sources/physics/snapshots/nasa-stereo-alfven-wave-list.html", "sha256:da0eab2e7955e0670d734c905c360758aabe57bb900de277e42da13fa0314385"),
)
SOURCE_IDS = ("NIST-COBLENTZ-BLACKBODY", "NIST-DIODE-LASER-LINEWIDTH", "NBS-ACOUSTIC-CAVITY-1986", "NASA-PLASMA-FREQUENCY-PROBE-1992", "NASA-STEREO-ALFVEN-LIST")
OBSERVATION_LABEL = "sealed-collective-response__complete-blackbody-acoustic-laser-plasma-Alfven-record__no-fit"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Post-seal blackbody, acoustic, laser, plasma and Alfvén response test",
    statement=(
        "After Claim 041 is sealed, NIST/NBS blackbody, laser and acoustic records and NASA plasma and Alfvén records are opened. "
        "The externally measured blackbody exponent is four, Coblentz's coefficient was within one percent and the spectrum shape agreed. "
        "Measured cavity resonances, strictly positive finite laser linewidths with feedback narrowing, direct density tracking by plasma frequency, "
        "and the registered 2007-2014 Alfvén-wave list all retain the formal relation directions without selecting their laws."
    ),
    dependencies=("SFT-PHYS-COLLECTIVE-RADIATION-RESPONSE-TERMINAL-041", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001", "SFT-PHYS-MEAS-TARGET-CUSTODY-001", "SFT-PHYS-MEAS-UNCERTAINTY-001"),
    generation_rule="Generate the complete eight-axis product of sealed collective response, complete targets, bound provenance, capability isolation, proof/measurement separation, complete rows, successor closure and extension.",
    grammar_boundary="The sealed finite occupation and exact scaling laws; measured exponent four; coefficient agreement bound one percent; positive measured linewidth ranges; acoustic resonance precision; direct plasma-frequency density dependence; complete Alfvén observation-year boundary; and every source/custody row.",
    dimensions=empirical_dimensions("sealed-collective-response-versus-complete-blackbody-acoustic-laser-plasma-Alfven-record", "The formal receipt was fixed before the five source snapshots were bound."),
    exact_result=(
        "External blackbody measurement reports exponent 4 exactly, matching the forced rank-three-plus-energy exponent; doubling therefore remains the exact ratio 16. "
        "The historical Stefan coefficient is reported within 1/100 of the present value and spectrum shape agreement is retained, but no dimensional coefficient is manufactured from a normalized carrier. "
        "Acoustic and microwave cavity resonances were measured to part-per-million precision. NIST reports unmodified laser linewidths of at least 10,000,000 Hz and extended-cavity linewidths no more than 500,000 Hz, so linewidth remains positive and feedback narrows it by at least factor 20. "
        "Two NASA flights directly track electron density through plasma frequency, and NASA registers Alfvén waves from 2007 through 2014. All comparisons pass at their declared relation/value type without fitting."
    ),
    induction_base="The formal receipt fixes every normalized relation before the target record is released.",
    induction_step="Each additional source row, measured bound or observation year is retained exactly once and cannot alter the formal survivor.",
    exclusions=("no target readable by the formal generator", "no fitted dimensional coefficient or converted absolute value", "no historical-blindness claim", "no omission of finite linewidth or source limitations", "no numerical-zero, negative, irrational, imaginary or floating Fold proof magnitude"),
    operational_witnesses=(("occupation", "Finite support and scale covariance are closed.", theorem_certificate()["energy_exact"] and theorem_certificate()["scale_covariant"]), ("response", "Fourth power, acoustics and laser are closed.", theorem_certificate()["fourth_power"] and theorem_certificate()["acoustic"] and theorem_certificate()["laser"]), ("collective", "Plasma and Alfvén squared carriers are closed.", theorem_certificate()["plasma"] and theorem_certificate()["alfven"])),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=tuple(ExternalTargetRow(name, source, description, OBSERVATION_LABEL) for name, source, description in (
        ("BLACKBODY", SOURCE_IDS[0], "Measured exponent, coefficient agreement and spectrum shape"),
        ("LASER", SOURCE_IDS[1], "Measured positive linewidth and feedback narrowing"),
        ("ACOUSTIC", SOURCE_IDS[2], "Measured cavity resonance frequencies and precision"),
        ("PLASMA", SOURCE_IDS[3], "Direct plasma-frequency electron-density tracking on two flights"),
        ("ALFVEN", SOURCE_IDS[4], "Registered in-situ Alfvén-wave observation interval"),
    )),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="Reject if a source or row changes; if the measured blackbody exponent is not four; if measured linewidth is empty or feedback does not narrow it; if acoustic resonances, direct plasma-frequency density dependence or Alfvén observations are absent; if a dimensional coefficient is fitted from normalized structure; or if a target changes the formal survivor.",
)


SPEC.validate()


__all__ = ("CLAIM_ID", "EXPERIMENT_ID", "OBSERVATION_LABEL", "ObservationalEmpiricalPhysicsProgram", "SOURCE_FILES", "SOURCE_HASH", "SOURCE_IDS", "SOURCE_PATH", "SPEC")
