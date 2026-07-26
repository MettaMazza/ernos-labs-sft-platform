"""External comparison of particle generations, spectra, mixing and longevity."""

from dataclasses import replace

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    GeneratedEmpiricalPhysicsProgram,
    empirical_dimensions,
)
from sft.physics.particle_mode_generation_terminal_law_v1 import theorem_certificate


CLAIM_ID = "SFT-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/particle-mode-generation-postseal-source-record.json"
SOURCE_HASH = "sha256:abf29f6244ad64e49b169489675627424bcdbdc3d38e8ceef4b1628681889cd5"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/pdg-2025-leptons-summary.pdf", "sha256:5aa9a3a33b554204056cb04c42319bb32c9664ae518907652ff5cdc1cb87e5bb"),
    ("experiments/external_sources/physics/snapshots/nist-codata-2022-allascii.txt", "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67"),
    ("experiments/external_sources/physics/snapshots/pdg-2025-quark-masses.pdf", "sha256:d544d099aa15739ec83d87711bd4c5b1e0a1032d6f70aaa4847ec78601f7aeae"),
    ("experiments/external_sources/physics/snapshots/pdg-2025-ckm-matrix.pdf", "sha256:a0a78578971f38ff89c6fc5579bc608de41ec383a205dc25cba1d26f7145610a"),
    ("experiments/external_sources/physics/snapshots/pdg-2025-neutrino-mixing.pdf", "sha256:d7067e2e3c9098cc924f10ffbca579c557fb8e848bf3acc17f9815598cdda7a6"),
)
SOURCE_IDS = (
    "PDG-2025-LEPTON-SUMMARY",
    "NIST-CODATA-2022-ALL-CONSTANTS",
    "PDG-2025-QUARK-MASSES",
    "PDG-2025-CKM-MATRIX",
    "PDG-2025-NEUTRINO-MIXING",
)
OBSERVATION_LABEL = "sealed-particle-mode-generation-transport__forced-three-matches-precision-measurement__independent-direct-row-retained-unchanged__terminal-lepton-quark-neutrino-and-CKM-vector__charged-lepton-longevity-order__no-site-mass-or-extra-dimension-import"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Complete particle-generation, mass-pattern, mixing and longevity comparison",
    statement=(
        "The target-free terminal particle-mode law is compared with the complete registered lepton, quark, CKM "
        "and neutrino records. The PDG LEP-SLC fit interval [2989,3003]/1000 contains the forced generation count "
        "three. The independent direct determination 292/100 with stated uncertainty 5/100 is retained unchanged: "
        "its central-value displacement from three is exactly 8/5 stated uncertainties, with no rescaling, fitting, "
        "or use in selecting the law. Both terminal charged-lepton ratios pass; the registered s/d and b/s quark "
        "ratios pass while the absence of an exact scheme-matched t/c comparator remains explicit; all terminal CKM "
        "rows and the positive-neutrino PMNS/CP support pass at their registered boundaries. Charged-lepton masses "
        "increase electron-to-muon-to-tau while measured lifetimes decrease in that order."
    ),
    dependencies=(
        "SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051",
        "SFT-PHYS-VALIDATION-CHARGED-LEPTON-TERMINAL-002",
        "SFT-PHYS-VALIDATION-QUARK-CKM-003",
        "SFT-PHYS-MATTER-CKM-TERMINAL-004",
        "SFT-PHYS-VALIDATION-NEUTRINO-MASS-MIXING-003",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis product of sealed particle-mode law, full generation/mass/mixing/lifetime vector, provenance, target isolation, proof/measurement separation, complete-row retention, successor closure and extension.",
    grammar_boundary="The admitted Claim 051; the precision fitted neutrino-count measurement and the unchanged independent direct determination; both charged-lepton ratios; all available quark ratios and the missing-comparator boundary; all terminal CKM rows; the positive-neutrino mass/mixing vector; all three charged-lepton masses and lifetimes; heavy-lepton search limits; and every interpretive limitation.",
    dimensions=empirical_dimensions(
        "sealed-particle-mode-generation-law-versus-complete-registered-spectrum-vector",
        "Earlier mass/mixing targets were already known and observational provenance is disclosed; Claim 051 remained target-free and preceded retrieval of the independent PDG lepton summary.",
    ),
    exact_result=(
        "The forced count three lies in the PDG LEP-SLC precision interval [2989,3003]/1000. The independent direct "
        "determination 292/100 with stated uncertainty 5/100 is preserved exactly and has central-value displacement "
        "8/5 stated uncertainties from three; it is neither adjusted nor used to select the result. Both terminal charged-lepton mass-ratio intervals, the "
        "available s/d and b/s quark ratio intervals, all four terminal CKM intervals and the positive-neutrino "
        "mass/mixing support pass their registered comparisons; t/c remains without an exact scheme-matched direct "
        "comparator. The charged-lepton records give m_e<m_mu<m_tau and lifetime_e>lifetime_mu>lifetime_tau. These "
        "measurements test the terminal polynomial and ordering consequences, not the superseded site-as-mass, "
        "universal rate-ratio, dimensional lifetime-equality or extra-spatial-dimension claims."
    ),
    induction_base="The sealed three-label generation and terminal charged-lepton carriers are fixed before the independent lepton summary is opened.",
    induction_step="Each mass, mixing, count, lifetime, search-limit, unavailable-comparator and independent comparison row is appended exactly once and cannot alter the sealed formal survivor.",
    exclusions=(
        "no external particle mass, lifetime, generation count, mixing entry or search limit in the formal survivor",
        "no omission, rescaling or reinterpretation of the independent direct neutrino-count determination or the absent exact t/c comparator",
        "no use of generation coordinate fractions as measured mass values",
        "no claim that structural subtraction reach equals a dimensional lifetime ratio",
        "no claim that quarter-mode 1:1:4 is a universal observed mixing or decay-rate ratio",
        "no inference that heavy-particle search limits prove absolute nonexistence",
        "no extra spatial dimension or compactification rule selected from particle data",
        "no numerical-nothingness, negative, irrational, imaginary, floating, NaN, continuum or completed-infinity Fold proof magnitude",
    ),
    operational_witnesses=tuple((name, f"Formal particle-mode witness {name} is closed.", passed) for name, passed in theorem_certificate().items()),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=tuple(
        ExternalTargetRow(target, source, description, OBSERVATION_LABEL)
        for target, source, description in (
            ("GENERATION-COUNT-COMPLETE", SOURCE_IDS[0], "Precision neutrino-type fit and unchanged independent direct determination"),
            ("CHARGED-LEPTON-MASSES-LIFETIMES", SOURCE_IDS[0], "Complete electron, muon and tau mass/lifetime rows"),
            ("HEAVY-LEPTON-SEARCH-LIMITS", SOURCE_IDS[0], "Charged-heavy-lepton search boundaries"),
            ("CHARGED-LEPTON-RATIOS", SOURCE_IDS[1], "Both terminal CODATA mass-ratio intervals"),
            ("QUARK-RATIOS", SOURCE_IDS[2], "Available complete quark ratios and absent t/c comparator"),
            ("CKM-VECTOR", SOURCE_IDS[3], "Complete terminal CKM four-row vector"),
            ("NEUTRINO-MASS-MIXING", SOURCE_IDS[4], "Positive mass, PMNS, CP, ordering and bound vector"),
        )
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if any source changes; the precision generation interval excludes three; the independent direct row "
        "is omitted, altered, rescaled or used to select the law; a registered terminal mass or mixing comparison fails; the charged-lepton mass/lifetime orders "
        "reverse; the missing t/c comparator is presented as measured; any search or model boundary is omitted; an "
        "old site coordinate is relabelled as mass; or target data alter the formal survivor."
    ),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "EXPERIMENT_ID", "OBSERVATION_LABEL", "ObservationalEmpiricalPhysicsProgram",
    "SOURCE_FILES", "SOURCE_HASH", "SOURCE_IDS", "SOURCE_PATH", "SPEC",
)
