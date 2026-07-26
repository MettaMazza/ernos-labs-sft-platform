"""Post-seal stellar nuclear/collapse comparison for Claim 069."""

from dataclasses import replace

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import EmpiricalPhysicsSpec, ExternalTargetRow, GeneratedEmpiricalPhysicsProgram, empirical_dimensions
from sft.physics.stellar_nuclear_collapse_terminal_law_v1 import theorem_certificate


CLAIM_ID = "SFT-PHYS-VALIDATION-STELLAR-NUCLEAR-COLLAPSE-070"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-STELLAR-NUCLEAR-COLLAPSE-070"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/stellar-nuclear-collapse-postseal-source-record.json"
SOURCE_HASH = "sha256:4315620e6c801de49869a6fe693e61ae5b5b5ced82bd8896b733c50f7a4809bd"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/nasa-gsfc-stellar-stage-table.html", "sha256:156c6ce406b0ec49ceac6921ad36fccf5d8778fb5cec7539e24ee8cce961a794"),
    ("experiments/external_sources/physics/snapshots/arxiv-2006.15115-borexino-cno.pdf", "sha256:d61241252a22a4c9614d5a29a05cf7d211c4a8dde9dec77fe21e242238ed736d"),
    ("experiments/external_sources/physics/snapshots/arxiv-astro-ph-0107260-sn1987a-neutrinos.pdf", "sha256:72b8acc99ba37cf8557492669ce53851bf154b95950c7fc34e53a6681599b2d2"),
    ("experiments/external_sources/physics/snapshots/arxiv-1409.5477-sn2014j-gamma.pdf", "sha256:aaf0bc90867cdc5e13a8ee2dfd83a23def499e5d5be9bf3f7506e56e6afdaae1"),
    ("experiments/external_sources/physics/snapshots/arxiv-1910.10510-gw170817-strontium.pdf", "sha256:34b7f1a277959937f868e6987ec8ce39d481165fccbea8cbab6cfa27457e77c1"),
)
SOURCE_IDS = (
    "NASA-GSFC-COSMIC-ELEMENTS-STELLAR-STAGES",
    "BOREXINO-2020-CNO-NEUTRINOS",
    "LOREDO-LAMB-2001-SN1987A-NEUTRINOS",
    "DIEHL-2014-SN2014J-GAMMA-LINES",
    "WATSON-2019-GW170817-STRONTIUM",
)
OBSERVATION_LABEL = "sealed-stellar-nuclear-collapse-law-versus-complete-five-source-record"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


_theorem = theorem_certificate()

SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Blind stellar nuclear chain, collapse and heavy-element validation",
    statement=(
        "Claim 069 sealed the stage-successor, global binding terminal, support-loss collapse, thermonuclear and "
        "neutral-capture laws before the five-source vector opened. NASA records all six major burning stages at "
        "strictly increasing temperatures from 3/100 to 33/10 billion kelvin and retains every duration, including "
        "the nonmonotonic neon/oxygen duration pair. Borexino directly detects stellar CNO fusion neutrinos at "
        "36/5 with +3 and -17/10 counts per day per 100 tonnes and better than five-sigma significance. The complete "
        "SN1987A three-detector neutrino record supports the collapse channel while its delayed-mechanism preference "
        "remains labelled model-assisted. SN2014J directly supplies both cobalt decay lines and their uncertainties; "
        "the measured ratio interval contains the registered branch ratio. GW170817 spectroscopy identifies "
        "strontium, directly locating a neutron-capture element in neutron-rich merger ejecta while retaining the "
        "source's spectral-modelling dependence."
    ),
    dependencies=(
        "SFT-PHYS-STELLAR-NUCLEAR-COLLAPSE-TERMINAL-069",
        "SFT-PHYS-NUCLEAR-FUSION-FISSION-YIELD-THRESHOLD-006",
        "SFT-PHYS-NUCLEAR-BINDING-CURVE-TERMINAL-005",
        "SFT-PHYS-NUCLEAR-RADIOACTIVE-DECAY-TERMINAL-005",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule=(
        "Generate the complete eight-axis product of sealed carrier, source custody, complete stage table, direct "
        "fusion-neutrino row, collapse-neutrino vector, thermonuclear gamma vector, neutron-capture spectrum and no-extra-rule."
    ),
    grammar_boundary=(
        "The sealed Claim 069 receipt; all five immutable sources; all six stage temperatures and durations; Borexino "
        "rate and asymmetric errors; all three SN1987A detectors and model boundary; both SN2014J lines, fluxes, errors, "
        "ratio and significance; the complete registered GW170817 strontium row; and no target access before seal."
    ),
    dimensions=empirical_dimensions(
        OBSERVATION_LABEL,
        "Retain all measured values, irregular duration rows, asymmetric errors, direct observations and model-assisted interpretations together without fitting a stage, rate or event channel.",
    ),
    exact_result=(
        "The complete six NASA stage temperatures are (3/100,1/5,4/5,3/2,2,33/10) billion kelvin and strictly "
        "increase in the formal stage order; all durations (10000000,1000000,1000,1/10,2,1/100 years) remain and are "
        "not falsely called monotonic. Borexino reports 36/5 +3 -17/10 cpd per 100 tonnes, minimum significance five "
        "sigma at 99/100 confidence. SN1987A neutrinos were recorded by three detectors; the reported two-component "
        "preference exceeds 100:1 and the sub-One-second accretion component remains model-assisted. SN2014J records "
        "847 and 1238 keV cobalt lines with fluxes 73/20 +/- 121/100 and 227/100 +/- 69/100 in 10^-4 photon units; "
        "the measured ratio 31/50 +/- 7/25 contains 17/25 and the spectrum significance is 113/10 sigma. GW170817 "
        "records the 810 nm strontium feature from 3/2 to 10 days, with 1/5-c broadening and 23/100-c blueshift."
    ),
    induction_base="Claim 069 is sealed before the five-source target object is released.",
    induction_step="Every source and uncertainty row is appended once; no favorable result deletes an irregular duration, detector, asymmetric error or model-dependence boundary.",
    exclusions=(
        "no stage temperature, neutrino event, gamma line, spectral feature, abundance or source value in formal survivor selection",
        "no fitted reaction rate, explosion energy, nickel mass, standard-candle calibration, ejecta model or target-selected tolerance",
        "no deletion of the oxygen-duration irregularity, any SN1987A detector, either cobalt line or any GW170817 modelling boundary",
        "no model-assisted interpretation relabelled as a direct SFT dimensional prediction",
        "no negative, irrational, imaginary, floating, NaN, continuum or infinite Fold proof scalar",
    ),
    operational_witnesses=(
        ("formal-stage", "Every formal stage successor has strictly greater access.", _theorem["all_chains_strict"]),
        ("formal-collapse", "Fusion support closes at the unique peak while inward gravity remains.", _theorem["support_loss"]["collapse_forced_when_no_other_support"]),
        ("formal-thermonuclear", "Every linked-fuel recurrence exhausts finite fuel.", _theorem["all_thermonuclear_finite"]),
        ("formal-capture", "Neutral capture and recorded rebalance close at every registered depth.", _theorem["all_neutral_capture_closed"]),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=tuple(ExternalTargetRow(source_id, source_id, "complete retained source row", OBSERVATION_LABEL) for source_id in SOURCE_IDS),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if any source changes; any stage, duration, detector, line, flux, uncertainty, confidence, feature or "
        "modelling boundary is omitted; the stage temperatures are not strictly ordered; the direct channel observations "
        "are absent; target data alter the sealed law; a fit enters; or any hostile control passes incorrectly."
    ),
)


SPEC.validate()


__all__ = ("CLAIM_ID", "EXPERIMENT_ID", "OBSERVATION_LABEL", "ObservationalEmpiricalPhysicsProgram", "SOURCE_FILES", "SOURCE_HASH", "SOURCE_IDS", "SOURCE_PATH", "SPEC")
