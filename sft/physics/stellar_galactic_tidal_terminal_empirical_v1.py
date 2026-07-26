"""Post-seal stellar, galactic and tidal comparison for Claim 067."""

from dataclasses import replace

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    GeneratedEmpiricalPhysicsProgram,
    empirical_dimensions,
)
from sft.physics.stellar_galactic_tidal_terminal_law_v1 import theorem_certificate


CLAIM_ID = "SFT-PHYS-VALIDATION-STELLAR-GALACTIC-TIDAL-068"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-STELLAR-GALACTIC-TIDAL-068"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/stellar-galactic-tidal-postseal-source-record.json"
SOURCE_HASH = "sha256:37f777d96a7d4844e16f4fbe57ad1fa150882eb097f5426c6e5481d47a713f6c"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/nasa-ntrs-20010111092-helioseismology.pdf", "sha256:e523f76ba101f8becc7c18e593d9dce2ce999e4393f3efbace74bada0a51e42e"),
    ("experiments/external_sources/physics/snapshots/arxiv-1807.02568-main-sequence-relations.pdf", "sha256:38f82514c2bcc9f3732581232d86d0798fb758f84018ddce1ad5e5941a359ff3"),
    ("experiments/external_sources/physics/snapshots/arxiv-1606.09251-sparc.pdf", "sha256:d089215877213661e40965543ee7e05736619082ad16d95e65ec059029588c63"),
    ("experiments/external_sources/physics/snapshots/arxiv-1901.05966-baryonic-tully-fisher.pdf", "sha256:a35dafd7d01967b64bbd78be5d337c0011f53fe3c3f6e224b32c23a7a7ba4e3f"),
    ("experiments/external_sources/physics/snapshots/arxiv-astro-ph-0608407-bullet-cluster.pdf", "sha256:59f2fb580797de5e5007fcea490a0f6c36036364546dbbb6a319a6e2fb5d0209"),
    ("experiments/external_sources/physics/snapshots/nasa-grc-moon-tidal-locking.html", "sha256:8591513db27d380612afdf5d4c34e3fa1502fdf89100f745b88a578c49135df4"),
    ("experiments/external_sources/physics/snapshots/nasa-ntrs-20150000346-mercury-resonance.pdf", "sha256:836e77ddea47e52734be957e4f41bfcddfc247c8b9beec3a9b0eb900756cfd4e"),
)
SOURCE_IDS = (
    "NASA-NTRS-HELIOSEISMOLOGY-2001",
    "EKER-2018-MAIN-SEQUENCE-RELATIONS",
    "SPARC-2016-ROTATION-CURVES",
    "LELLI-2019-BARYONIC-TULLY-FISHER",
    "CLOWE-2006-BULLET-CLUSTER",
    "NASA-GRC-MOON-SYNCHRONOUS-ROTATION",
    "NASA-NTRS-MESSENGER-MERCURY-RESONANCE",
)
OBSERVATION_LABEL = "sealed-stellar-galactic-tidal-law-versus-complete-seven-source-record"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


_theorem = theorem_certificate()

SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Blind stellar, galactic and tidal terminal validation",
    statement=(
        "Claim 067 sealed hydrostatic restoration, the complete three/four terminal stellar luminosity classes, "
        "the flat-curve additional-support discriminator, the fourth-power baryonic rotation carrier and the isolated "
        "one-to-one tidal terminal before the seven-source target vector opened. Helioseismology records a stable "
        "solar structure at parts-per-ten-thousand sound-speed precision. All six measured piecewise stellar slopes "
        "remain present: only the high and very-high mass endpoints contain the sealed powers four and three, so no "
        "universal single-power claim is manufactured. The 153-galaxy baryonic Tully-Fisher central interval excludes "
        "four while its full reported systematic interval reaches four; both facts remain in the receipt. SPARC and the "
        "Bullet Cluster independently retain the extended-support discriminator. The Moon records 1:1 synchronous "
        "rotation, while Mercury's measured 3:2 resonance confirms the formal eccentric-forcing boundary rather than "
        "being erased as an exception."
    ),
    dependencies=(
        "SFT-PHYS-STELLAR-GALACTIC-TIDAL-TERMINAL-067",
        "SFT-PHYS-ORBITAL-DIMENSION-STABILITY-TERMINAL-009",
        "SFT-PHYS-DARK-SMITHION-LFV-TERMINAL-061",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule=(
        "Generate the complete eight-axis product of sealed physical carrier, seven-source custody, solar structure, "
        "complete six-row stellar relation, complete galaxy vector, central-plus-systematic Tully-Fisher comparison, "
        "Moon-plus-Mercury tidal boundary and no-extra-rule."
    ),
    grammar_boundary=(
        "The sealed Claim 067 receipt; every row from the seven immutable source snapshots; exact positive whole and "
        "fraction values; reported uncertainties and systematic intervals; all six stellar regimes; the complete "
        "SPARC population; the Bullet Cluster separation; the lunar 1:1 observation; the Mercury 3:2 boundary; and "
        "structural target denial before formal sealing."
    ),
    dimensions=empirical_dimensions(
        OBSERVATION_LABEL,
        "Retain favorable, central-offset, piecewise, population and resonance-boundary rows together without fitting an exponent, selecting a galaxy subset or deleting Mercury.",
    ),
    exact_result=(
        "The NASA solar record reports sound-speed and adiabatic-index inference at the 1/10000 precision order and "
        "density at 1/1000; its reference-model convective boundary 1427/2000 lies inside the observed "
        "713/1000 +/- 1/1000 interval and is retained only as external structure evidence. The complete six stellar "
        "slopes are 507/250, 1143/250, 5743/1000, 4329/1000, 3967/1000 and 573/200 with their six reported "
        "uncertainties; the 3967/1000 row contains four and the 573/200 row contains three, while the other four do "
        "not and remain explicit. SPARC contributes all 175 galaxies. The 153-galaxy baryonic Tully-Fisher result is "
        "77/20 +/- 9/100 with intrinsic scatter 3/50: its central interval excludes four, while the reported systematic "
        "interval [7/2,4] contains the sealed endpoint. The Bullet Cluster records an eight-sigma mass/plasma separation. "
        "The Moon records equal approximately-655-hour orbital and rotation periods. MESSENGER records Mercury's "
        "29323073/500000 +/- 11/1000000 day rotation and experimentally verifies its 3:2 resonance, preserving the "
        "separately generated eccentric-resonance boundary."
    ),
    induction_base="The complete formal Claim 067 receipt is sealed before any of the seven measurement objects is released.",
    induction_step="Each complete source row is appended once; no favorable row can delete a nonmatching stellar regime, central Tully-Fisher offset or Mercury boundary, and no measurement can alter the formal survivor.",
    exclusions=(
        "no source row, stellar slope, galaxy fit, tidal period or uncertainty in formal survivor selection",
        "no fitted exponent, normalization, mass-to-light choice, halo profile, tolerance or correction term",
        "no deletion of four non-endpoint stellar regimes and no universal single stellar exponent",
        "no replacement of the Tully-Fisher central interval by its systematic interval or concealment of either",
        "no relabelling of a conventional solar reference-model value as an SFT dimensional prediction",
        "no universal lunar 1:1 rule extended across the explicitly separate Mercury eccentric resonance",
        "no negative, irrational, imaginary, floating, NaN, continuum or infinite Fold proof scalar",
    ),
    operational_witnesses=(
        ("formal-radial", "The formal perfect-power radial responses restore before measurement.", _theorem["all_radial_restoring"]),
        ("formal-stellar", "The formal terminal endpoint powers are three and four.", _theorem["luminosity_exponents"] == (3, 4)),
        ("formal-galactic", "Every formal flat-curve row forces additional enclosed support.", _theorem["all_flat_rows_require_growth"]),
        ("formal-tidal", "Every registered isolated finite mismatch terminates at one-to-one.", _theorem["all_tidal_rows_lock"]),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=tuple(
        ExternalTargetRow(source_id, source_id, "complete retained source row", OBSERVATION_LABEL)
        for source_id in SOURCE_IDS
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if any source identity changes; any of the six stellar regimes, both Tully-Fisher interval classes, "
        "the full galaxy counts, the Bullet separation, the Moon terminal or the Mercury boundary is omitted; the "
        "formal law is changed after target release; a central offset is concealed; a conventional reference model is "
        "called an SFT prediction; a fitted parameter enters; or any hostile control passes incorrectly."
    ),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "EXPERIMENT_ID", "OBSERVATION_LABEL", "ObservationalEmpiricalPhysicsProgram",
    "SOURCE_FILES", "SOURCE_HASH", "SOURCE_IDS", "SOURCE_PATH", "SPEC",
)
