"""Post-seal neutron-EDM and proton-stability comparison for Claim 063."""

from dataclasses import replace

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    GeneratedEmpiricalPhysicsProgram,
    empirical_dimensions,
)
from sft.physics.strong_cp_baryon_stability_terminal_law_v1 import theorem_certificate


CLAIM_ID = "SFT-PHYS-VALIDATION-STRONG-CP-BARYON-STABILITY-064"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-STRONG-CP-BARYON-STABILITY-064"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/strong-cp-baryon-stability-postseal-source-record.json"
SOURCE_HASH = "sha256:80475bde8d961642a902c84e0e1043c36a8a55d12430b72b18c6015e0c7a51db"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/arxiv-2001.11966-nedm.pdf", "sha256:1afeb830f372c7725cca9fd3d004333fe19cade698fd9798af9dfac7adc5c180"),
    ("experiments/external_sources/physics/snapshots/arxiv-2010.16098-proton-e-pi0.pdf", "sha256:6fa532b3b2671e8d6e028308297b95837567a6e3608b471aaa8af00fff6a9679"),
    ("experiments/external_sources/physics/snapshots/arxiv-2409.19633-proton-eta.pdf", "sha256:5b4bf694378930d7e38935546fea9c5deced9531137b0da276778e7b67fb4937"),
    ("experiments/external_sources/physics/snapshots/arxiv-2604.10975-proton-two-pi0.pdf", "sha256:06d10f843d39b54a14465628d72a9af18920976369326b1c717e3621b2109c98"),
)
SOURCE_IDS = (
    "NEDM-2020-PSI-PERMANENT-EDM",
    "SUPERK-2020-PROTON-E-MU-PI0",
    "SUPERK-2024-PROTON-E-MU-ETA",
    "SUPERK-2026-PROTON-E-MU-TWO-PI0",
)
OBSERVATION_LABEL = "sealed-strong-aligned-One-and-fibre-preserving-baryon-One-prediction"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


_theorem = theorem_certificate()

SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Blind neutron-EDM and multi-channel proton-stability validation",
    statement=(
        "Only after Claim 063 sealed, the PSI neutron-EDM measurement and six direct Super-Kamiokande proton-decay "
        "modes were released to the comparator. PSI reports a null central displacement with positive statistical "
        "and systematic uncertainties and a 90-percent upper limit of 1.8 times ten-to-the-minus-26 elementary-charge "
        "centimetres. This finite limit is consistent with the structurally absent strong electric-dipole carrier but "
        "is not relabelled as an exact proof scalar. Super-Kamiokande reports no decay indication across e/mu plus "
        "pi-zero, eta and two-pi-zero modes, with all six finite 90-percent partial-lifetime lower limits retained. "
        "Candidate events explicitly classified as atmospheric-neutrino-background compatible remain candidates, not "
        "fabricated decays. The complete registered vector therefore leaves the sealed aligned-One and proton-stability "
        "laws unviolated at current experimental sensitivity."
    ),
    dependencies=(
        "SFT-PHYS-STRONG-CP-BARYON-STABILITY-TERMINAL-063",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule=(
        "Generate the complete eight-axis product of sealed formal carrier, all registered EDM and proton-search rows, "
        "source binding, capability closure, proof/measurement separation, row completeness, successor closure and no-extra-rule."
    ),
    grammar_boundary=(
        "The sealed Claim 063; the direct neutron-EDM central-status, statistical uncertainty, systematic uncertainty "
        "and upper-limit rows; all six registered Super-Kamiokande mode limits and candidate interpretations; all four "
        "primary source snapshots; and no target access before the prediction seal."
    ),
    dimensions=empirical_dimensions(
        "sealed-strong-alignment-and-baryon-stability-versus-complete-registered-direct-search-vector",
        "Every registered uncertainty, finite bound, mode and candidate interpretation is retained without converting a null result into proof-zero, a candidate into decay, or a finite lower limit into completed infinity.",
    ),
    exact_result=(
        "The PSI result retains its null central status, positive 1.1 and 0.2 times ten-to-the-minus-26 uncertainty "
        "magnitudes and positive 1.8 times ten-to-the-minus-26 90-percent upper bound. The six proton modes retain "
        "90-percent partial-lifetime lower limits 2.4e34, 1.6e34, 1.4e34, 7.3e33, 7.2e33 and 4.5e33 years. No source "
        "reports a statistically significant proton-decay signal; the explicitly retained candidates are background "
        "compatible. Thus no registered row violates the sealed aligned-One or fibre-preserving baryon-One predictions."
    ),
    induction_base="The formal receipt is sealed and hashed before the neutron-EDM target is released.",
    induction_step="Each proton-decay mode and its full candidate interpretation is appended once; no row can alter the formal survivor or change evidential type.",
    exclusions=(
        "no neutron-EDM value, uncertainty, proton candidate or lifetime limit in formal survivor selection",
        "no null central estimate relabelled as conventional numerical proof zero",
        "no finite experimental upper or lower limit relabelled as an exact absence or completed infinity",
        "no background-compatible event relabelled as proton decay and no candidate row omitted",
        "no fitted theta, axion coefficient, decay rate, lifetime, confidence multiplier or tolerance",
        "no negative, irrational, imaginary, floating, NaN, continuum or infinite Fold proof scalar",
    ),
    operational_witnesses=(
        ("formal-alignment", "The formal carrier is aligned One before measurement.", _theorem["alignment"]["strong_phase"][0] == "aligned-One"),
        ("formal-empty-dipole", "The formal strong electric-dipole carrier is empty-One before measurement.", _theorem["alignment"]["electric_dipole_carrier"][0] == "empty-One"),
        ("formal-sector-exclusion", "All formal mediator actions preserve fibre and no cross-fibre action exists.", _theorem["actions"]["all_actions_fibre_preserving"] and _theorem["actions"]["generated_cross_fibre_actions"] == ()),
        ("formal-baryon-One", "The proton baryon-One invariant is closed before measurement.", _theorem["baryon_One_invariant"]),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=(
        ExternalTargetRow("NEDM-COMPLETE", SOURCE_IDS[0], "Central status, both uncertainties, 90-percent upper limit and unit", OBSERVATION_LABEL),
        ExternalTargetRow("PROTON-E-PI0", SOURCE_IDS[1], "Candidate record and 90-percent partial-lifetime lower limit", OBSERVATION_LABEL),
        ExternalTargetRow("PROTON-MU-PI0", SOURCE_IDS[1], "Candidate record and 90-percent partial-lifetime lower limit", OBSERVATION_LABEL),
        ExternalTargetRow("PROTON-E-ETA", SOURCE_IDS[2], "No-significant-excess status and 90-percent partial-lifetime lower limit", OBSERVATION_LABEL),
        ExternalTargetRow("PROTON-MU-ETA", SOURCE_IDS[2], "No-significant-excess status and 90-percent partial-lifetime lower limit", OBSERVATION_LABEL),
        ExternalTargetRow("PROTON-E-TWO-PI0", SOURCE_IDS[3], "Background-compatible candidate and 90-percent partial-lifetime lower limit", OBSERVATION_LABEL),
        ExternalTargetRow("PROTON-MU-TWO-PI0", SOURCE_IDS[3], "Background-compatible candidate and 90-percent partial-lifetime lower limit", OBSERVATION_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if any source changes; the direct EDM record reports a confirmed nonempty displacement; any proton mode "
        "reports a statistically significant decay signal; a candidate or uncertainty is omitted or relabelled; a "
        "finite limit is called exact absence/infinity; target data select the formal law; or any hostile control passes incorrectly."
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
