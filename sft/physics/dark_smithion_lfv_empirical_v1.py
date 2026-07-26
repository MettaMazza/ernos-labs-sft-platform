"""Post-seal measured-value and standing-test record for Claim 061."""

from dataclasses import replace
from fractions import Fraction

from sft.engine import ProvenanceClass
from sft.physics.dark_smithion_lfv_terminal_law_v1 import theorem_certificate
from sft.physics.generated_empirical_law import EmpiricalPhysicsSpec, ExternalTargetRow, GeneratedEmpiricalPhysicsProgram, empirical_dimensions


CLAIM_ID = "SFT-PHYS-VALIDATION-DARK-SMITHION-LFV-062"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-DARK-SMITHION-LFV-062"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/dark-smithion-lfv-postseal-source-record.json"
SOURCE_HASH = "sha256:ed0dba82cdd49f67258eb152466a629d9086804197d2c56bcfdc49e2849345f3"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/planck-2018-density-abstract-record.json", "sha256:274e0189de5846ce0b8c2d7b83ae06c72587cf8325d4d2b2338e88dd0a74a88f"),
    ("experiments/external_sources/physics/snapshots/arxiv-1606.09251-sparc.pdf", "sha256:d089215877213661e40965543ee7e05736619082ad16d95e65ec059029588c63"),
    ("experiments/external_sources/physics/snapshots/arxiv-2504.15711-megii-lfv.pdf", "sha256:0efbf99543c92d340eb7b07f40e6fea580b7746caab26c9233d3e30e8b71a5b6"),
    ("experiments/external_sources/physics/snapshots/arxiv-0908.2381-babar-tau-lfv.pdf", "sha256:ba3e1352f4c14b1867e06f6436b4a6b1e1980cd55ce52d9a9454bd618ed70015"),
)
SOURCE_IDS = ("PLANCK-2018-VI-ABSTRACT-DENSITIES", "SPARC-2016-175-GALAXY-MASS-MODELS", "MEGII-2025-MU-E-GAMMA", "BABAR-2010-TAU-LFV-GAMMA")
OBSERVATION_LABEL = "sealed-dark-smithion-lfv-law__27-over-5-and-absolute-density-transport-pass-planck__sparc-requires-non-baryonic-gravitating-support-under-derived-inverse-square-law__all-lfv-upper-limits-retained-without-fabricated-rate-ratio__smithion-masses-standing-predictions"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


_theorem = theorem_certificate()

SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Measured dark abundance and complete Smithion/LFV standing-test record",
    statement=(
        "After the zero-parameter Claim 061 seals, the exact dark/baryon ratio 27/5 is compared with the complete "
        "Planck density-ratio interval and lies inside it. Transport of the comparison-side baryon central value gives "
        "Omega_c h-squared=0.12096, inside Planck's complete reported [0.119,0.121] interval. SPARC's complete 175-galaxy "
        "record retains observed-to-baryonic velocity discrepancies; under the separately derived inverse-square law "
        "this rejects a finite baryon-only asymptote and requires an additional gravitating distribution. MEG II and "
        "BaBar report no signal and only upper limits for the three registered radiative LFV channels. Therefore those "
        "rows do not measure the sealed 3:5:20 relative weights and are retained without manufacturing a confirmation "
        "or contradiction. The twelve Smithion mass ratios remain exact standing predictions because no corresponding "
        "measured particles exist in the registered evidence."
    ),
    dependencies=(
        "SFT-PHYS-DARK-SMITHION-LFV-TERMINAL-061",
        "SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001",
        "SFT-PHYS-FIELD-INVERSE-SQUARE-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis product of the sealed law, Planck density rows, galaxy discriminator, LFV search rows, prediction status, target isolation, complete-row custody and no-extra-rule.",
    grammar_boundary="The admitted Claim 061; both Planck density rows with uncertainties; the complete SPARC sample statement; all three registered LFV radiative upper-limit rows; every current Smithion measurement-status row; and no target access before seal.",
    dimensions=empirical_dimensions("sealed-dark-smithion-lfv-law-versus-complete-current-record", "Every available measured row is retained; an upper limit is never relabelled as a nonzero rate and an unobserved mass is never relabelled as measured."),
    exact_result=(
        "The exact 27/5 ratio lies inside the complete Planck dark/baryon interval, and 27/5 times 0.0224 gives "
        "0.12096 inside the reported cold-dark interval [0.119,0.121]. The 175-galaxy SPARC record rejects finite "
        "baryon-only inverse-square asymptotics and supports additional gravitating matter under the admitted law. "
        "MEG II and BaBar provide three positive upper limits after null searches, not three measured rates; the 3:5:20 "
        "and 4:1 LFV predictions remain standing tests. No measured Smithion mass exists, so all twelve mass-ratio "
        "enclosures remain standing predictions rather than fabricated measured-value matches."
    ),
    induction_base="The formal receipt and both complete Planck density rows are bound before the withheld target is released.",
    induction_step="Each galaxy, LFV and unobserved-mass status row is appended exactly once; its evidential type is preserved and cannot alter the formal survivor.",
    exclusions=(
        "no density, galaxy datum, search limit or particle mass in formal survivor selection",
        "no upper limit relabelled as an observed rate or relative-rate measurement",
        "no null search relabelled as proof of particle identity",
        "no unobserved Smithion relabelled as a measured discovery",
        "no fitted abundance, cross-section, mediator mass, branching fraction or uncertainty multiplier",
        "no negative, irrational, imaginary, floating, NaN, continuum or completed-infinity Fold proof magnitude",
    ),
    operational_witnesses=(
        ("formal-cross-lock", "Both quark carrier cross-locks survive before measurement.", _theorem["quark_cross_lock"]),
        ("formal-spectra", "All four spectra and twelve exact roots survive before measurement.", _theorem["four_spectra"] and _theorem["twelve_roots"] and _theorem["all_roots_disjoint_positive"]),
        ("formal-abundance", "The sealed abundance ratio is 27/5.", _theorem["abundance"]["dark_to_baryon"] == Fraction(27, 5)),
        ("formal-lfv", "The sealed LFV ratio is 3:5:20 with tau ratio four.", _theorem["lfv"]["integer_ratio"] == (3, 5, 20) and _theorem["lfv"]["tau_ratio"] == 4),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=(
        ExternalTargetRow("PLANCK-DARK-BARYON-COMPLETE", SOURCE_IDS[0], "Both density central values and both reported uncertainties", OBSERVATION_LABEL),
        ExternalTargetRow("SPARC-175-GALAXY-DISCRIMINATOR", SOURCE_IDS[1], "Complete observed-to-baryonic velocity sample statement", OBSERVATION_LABEL),
        ExternalTargetRow("MEGII-MU-E-UPPER-LIMIT", SOURCE_IDS[2], "Null result and complete 90-percent upper limit", OBSERVATION_LABEL),
        ExternalTargetRow("BABAR-TAU-E-UPPER-LIMIT", SOURCE_IDS[3], "Null result and complete 90-percent upper limit", OBSERVATION_LABEL),
        ExternalTargetRow("BABAR-TAU-MU-UPPER-LIMIT", SOURCE_IDS[3], "Null result and complete 90-percent upper limit", OBSERVATION_LABEL),
        ExternalTargetRow("SMITHION-MEASUREMENT-STATUS", SOURCE_IDS[1], "No registered measured penta/hepta Smithion mass", OBSERVATION_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="Reject if any source changes; 27/5 leaves the complete Planck ratio interval; 0.12096 leaves the complete cold-dark interval; the galaxy discrepancy row is omitted; an LFV limit is altered or relabelled as a rate; a Smithion is relabelled as measured without a source; target data select the formal law; or any hostile control passes incorrectly.",
)

SPEC.validate()

__all__ = ("CLAIM_ID", "EXPERIMENT_ID", "OBSERVATION_LABEL", "ObservationalEmpiricalPhysicsProgram", "SOURCE_FILES", "SOURCE_HASH", "SOURCE_IDS", "SOURCE_PATH", "SPEC")
