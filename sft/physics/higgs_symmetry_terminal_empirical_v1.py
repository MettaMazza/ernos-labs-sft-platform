"""Post-seal Higgs mass and self-coupling comparison for Claim 065."""

from dataclasses import replace

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    GeneratedEmpiricalPhysicsProgram,
    empirical_dimensions,
)
from sft.physics.higgs_symmetry_terminal_law_v1 import theorem_certificate


CLAIM_ID = "SFT-PHYS-VALIDATION-HIGGS-SYMMETRY-TERMINAL-066"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-HIGGS-SYMMETRY-TERMINAL-066"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/higgs-terminal-postseal-source-record.json"
SOURCE_HASH = "sha256:62d866e1b94f43e7cb73c9da46ac672434e00b4f8bc628b17f4060e8fb019d21"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/pdg-2024-standard-model-review.pdf", "sha256:4689caae925ee279228684249333a8395a40dda74a94863549b48f758d3fdd3f"),
    ("experiments/external_sources/physics/snapshots/pdg-2025-higgs-listing.pdf", "sha256:228835096e2003bb332f456ad412cbfbd628a6973be715309da7d2f419ac77bc"),
    ("experiments/external_sources/physics/snapshots/arxiv-2308.04775-atlas-higgs-mass.pdf", "sha256:b3d2c09226e54f4553a381c70e41095f8f1c18aec3aabbc845e0481aa9207e4e"),
    ("experiments/external_sources/physics/snapshots/arxiv-2409.13663-cms-higgs-mass.pdf", "sha256:8dfaa73b5df3a958998a1a95dc123dc02013ef22c0a4fc3f82253550fc1c1807"),
    ("experiments/external_sources/physics/snapshots/arxiv-2602.23991-atlas-cms-hh.pdf", "sha256:eaf44d724e33f500781a964a2918b5d2062c55be760704736346233ed02ff678"),
)
SOURCE_IDS = (
    "PDG-2024-ELECTROWEAK-VACUUM-SCALE",
    "PDG-2025-HIGGS-MASS-AVERAGE",
    "ATLAS-2023-COMBINED-HIGGS-MASS",
    "CMS-2024-FOUR-LEPTON-HIGGS-MASS",
    "ATLAS-CMS-2026-HIGGS-PAIR-COMBINATION",
)
OBSERVATION_LABEL = "sealed-terminal-Higgs-ratio-and-self-coupling-versus-complete-current-record"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


_theorem = theorem_certificate()

SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Blind terminal Higgs mass and self-coupling validation",
    statement=(
        "Claim 065 sealed the exact ratio m_H/v = 2563352914777/5038463954690 and native self-coupling "
        "6570778165695741824959729/50772238045420788745992200 before any Higgs target was released. "
        "The post-seal comparator uses the PDG electroweak scale 246.22 GeV only as a dimensional reference, "
        "giving the exact mass prediction 125.266104978... GeV. That prediction lies inside the complete PDG "
        "2025 listed-average interval 125.09--125.31 GeV. The individual ATLAS and CMS offsets are retained "
        "rather than erased: they are approximately 1.42 and 1.88 of their reported combined uncertainties. "
        "The direct ATLAS-CMS pair-production constraint remains broad and contains the normalized unity "
        "self-coupling correspondence; it is not misrepresented as a precision measurement of native lambda."
    ),
    dependencies=(
        "SFT-PHYS-HIGGS-SYMMETRY-TERMINAL-065",
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule=(
        "Generate the complete eight-axis product of sealed Higgs carrier, dimensional reference, aggregate mass, "
        "individual mass rows, source custody, self-coupling boundary, measurement separation and no-extra-rule."
    ),
    grammar_boundary=(
        "The sealed Claim 065 ratio and coupling; the PDG 246.22 GeV dimensional reference; the complete PDG "
        "listed average and uncertainty; the direct ATLAS and CMS mass rows with every reported uncertainty; the "
        "latest combined ATLAS-CMS kappa-lambda interval; all five source snapshots; and no target access before seal."
    ),
    dimensions=empirical_dimensions(
        "sealed-terminal-Higgs-ratio-and-self-coupling-versus-complete-current-record",
        "Retain aggregate agreement, both individual offsets, every uncertainty, and the direct-coupling capability boundary without choosing a coefficient, tolerance, or target-selected law.",
    ),
    exact_result=(
        "Using the post-seal PDG dimensional reference v = 12311/50 GeV, the sealed ratio predicts exactly "
        "m_H = 31557437733819647/251923197734500 GeV = 125.266104978... GeV. The PDG 2025 listed average is "
        "626/5 +/- 11/100 GeV, whose reported-uncertainty interval [12509/100,12531/100] contains the prediction; "
        "the exact displacement from its central value is 16653377460247/251923197734500 GeV. ATLAS reports "
        "12511/100 +/- 11/100 GeV and CMS reports 3126/25 +/- 3/25 GeV; their exact positive offsets remain in the "
        "certificate and are not called aggregate failures. The exact native lambda is "
        "6570778165695741824959729/50772238045420788745992200. The 2026 ATLAS-CMS 95-percent normalized "
        "kappa-lambda interval, recorded as a below-reference direction of magnitude 71/100 through 61/10, "
        "contains the SFT normalized unity correspondence but does not yet resolve native lambda precisely."
    ),
    induction_base="The formal ratio and native coupling receipt are sealed before the external dimensional scale or Higgs targets are released.",
    induction_step="Each source row and uncertainty is appended once; individual offsets cannot be deleted by the aggregate comparison and no row can alter the sealed formal survivor.",
    exclusions=(
        "no Higgs mass, VEV, self-coupling interval, uncertainty or aggregate in formal survivor selection",
        "no coefficient, correction term, target-selected tolerance, uncertainty inflation or fitted series",
        "no omission of the ATLAS or CMS individual offsets and no claim that both lie within one reported uncertainty",
        "no direct-search interval relabelled as a precision measurement of native lambda",
        "no signed external coordinate imported as a negative Fold proof scalar",
        "no negative, irrational, imaginary, floating, NaN, continuum or infinite Fold proof scalar",
    ),
    operational_witnesses=(
        ("formal-ratio", "The exact terminal mass ratio is sealed before measurement.", _theorem["terminal_mass_ratio"].numerator == 2563352914777 and _theorem["terminal_mass_ratio"].denominator == 5038463954690),
        ("formal-coupling", "The native self-coupling is sealed before measurement.", _theorem["terminal_self_coupling"].numerator == 6570778165695741824959729),
        ("formal-cross-lock", "The squared mass route equals twice the coupling route before measurement.", _theorem["route_cross_lock"]["routes_equal"]),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=(
        ExternalTargetRow("ELECTROWEAK-SCALE", SOURCE_IDS[0], "PDG electroweak dimensional reference", OBSERVATION_LABEL),
        ExternalTargetRow("PDG-HIGGS-AVERAGE", SOURCE_IDS[1], "PDG average, uncertainty, scale factor and exact interval", OBSERVATION_LABEL),
        ExternalTargetRow("ATLAS-HIGGS-MASS", SOURCE_IDS[2], "ATLAS value and statistical, systematic and combined uncertainties", OBSERVATION_LABEL),
        ExternalTargetRow("CMS-HIGGS-MASS", SOURCE_IDS[3], "CMS value and reported uncertainty", OBSERVATION_LABEL),
        ExternalTargetRow("ATLAS-CMS-KAPPA-LAMBDA", SOURCE_IDS[4], "Combined normalized trilinear interval and signal-strength record", OBSERVATION_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if any source changes; the sealed mass prediction lies outside the complete authoritative aggregate "
        "interval; normalized unity lies outside the direct self-coupling interval; an individual offset or uncertainty "
        "is omitted; a broad limit is called a precision measurement; target data select or modify the formal law; "
        "a signed external coordinate becomes a Fold proof scalar; or any hostile control passes incorrectly."
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
