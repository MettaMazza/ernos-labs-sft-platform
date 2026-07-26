"""Empirical comparison for the terminal Fold waveform sequence."""

from dataclasses import replace

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    GeneratedEmpiricalPhysicsProgram,
    empirical_dimensions,
)
from sft.physics.gravitational_wave_chirp_ringdown_terminal_law_v1 import theorem_certificate


CLAIM_ID = "SFT-PHYS-VALIDATION-GRAVITATIONAL-WAVE-CHIRP-RINGDOWN-074"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-GRAVITATIONAL-WAVE-CHIRP-RINGDOWN-074"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/gravitational-wave-chirp-ringdown-postseal-source-record.json"
SOURCE_HASH = "sha256:b24e9d1e8fc37f39bcbc692ac7cfaddbe7666bc4e161880ff45708d958ed1d92"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/ligo-p150914-gw150914-discovery.pdf", "sha256:e5e864c23d015b69be17e5b5d51b5b462d2829353a867513414b6728f54589c4"),
    ("experiments/external_sources/physics/snapshots/ligo-p151226-gw151226-discovery.pdf", "sha256:a59bb954e9850a8800e2b62e1808553012e791b879e00f108b0bf061bf530e72"),
    ("experiments/external_sources/physics/snapshots/ligo-p2000020-gw190521-discovery.pdf", "sha256:4d6661f18168267249b3ca043b0692d88376c9db9b3d9146a9500763f7b438a7"),
)
SOURCE_IDS = (
    "LIGO-VIRGO-GW151226-DISCOVERY-2016",
    "LIGO-VIRGO-GW190521-DISCOVERY-2020",
)
OBSERVATION_LABEL = "sealed-Fold-chirp-merger-ringdown-sequence-versus-complete-postseal-LIGO-vector"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


_theorem = theorem_certificate()

SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Complete empirical gravitational-wave chirp, merger and ringdown comparison",
    statement=(
        "Claim 073 independently enumerated and sealed the exact Fold sequence. GW150914 remains disclosed as "
        "pre-seal observational context and is not relabelled as a blind prediction. The separately bound post-seal "
        "GW151226 record directly reports frequency and amplitude increasing across 55 cycles from 35 to 450 Hz, "
        "positive radiated energy and a two-component-to-one-remnant transition. The post-seal GW190521 record "
        "separately supports a decaying least-damped quadrupolar remnant mode while retaining the conditional "
        "quasicircular interpretation, short-signal boundary and alternative interpretations. Together the complete "
        "record validates the rising-chirp, merger and damped-ringdown classes without claiming that dimensional "
        "frequencies or half-One damping are universal measured Fold coordinates."
    ),
    dependencies=(
        "SFT-PHYS-GRAVITATIONAL-WAVE-CHIRP-RINGDOWN-TERMINAL-073",
        "SFT-PHYS-VALIDATION-GRAVITATIONAL-WAVES-003",
        "SFT-PHYS-VALIDATION-GRAVITY-HORIZONS-003",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule=(
        "Generate the complete eight-axis product of sealed Fold sequence, complete post-seal event vector, source "
        "custody, rising-chirp ordering, two-to-one remnant transition, damped-mode support, scope retention and no-extra-rule."
    ),
    grammar_boundary=(
        "The immutable Claim 073 receipt; disclosed GW150914 development context; every GW151226 frequency, "
        "amplitude, cycle, source, remnant, energy, uncertainty and model-role row; every GW190521 duration, cycle, "
        "frequency, source, remnant, ringdown and conditional-interpretation row; and all hostile controls."
    ),
    dimensions=empirical_dimensions(
        OBSERVATION_LABEL,
        "Retain every rising-chirp, merger, ringdown, uncertainty, model-role and pre-seal/post-seal provenance row.",
    ),
    exact_result=(
        "The complete empirical record supports all three forced waveform stages. GW151226 rises from 35 to 450 Hz "
        "and in amplitude over 55 cycles, retains positive radiated energy and records two initial components joining "
        "one final remnant. GW190521 retains a decaying least-damped l=m=2 remnant mode compatible with its full "
        "waveform analysis. Its short duration, conditional quasicircular interpretation and alternative-source "
        "boundary remain explicit. GW150914 is retained as observational development evidence, not counted as a "
        "blind target. No external value selects or modifies the 4096-form Claim 073 survivor, and no dimensional "
        "frequency or fitted damping value becomes a Fold proof scalar."
    ),
    induction_base="The admitted Claim 073 receipt exists before either withheld post-seal source is bound.",
    induction_step="Each complete event row appends once with its provenance and scope; no row changes the formal survivor or is promoted beyond its measurement role.",
    exclusions=(
        "no claim that GW150914 was unseen before Claim 073",
        "no use of GW151226 or GW190521 values to select or alter the formal survivor",
        "no fitted chirp mass, waveform, merger time, damping coefficient, tone or tolerance",
        "no model-assisted remnant property relabelled as direct model-free measurement",
        "no claim that half-One damping or normalized Fold frequency was directly measured",
        "no omitted uncertainty, short-signal, conditional-interpretation or alternative-source row",
    ),
    operational_witnesses=(
        ("formal-chirp", "The exact chirp ordering was sealed before withheld target binding.", _theorem["all_chirps_close"]),
        ("formal-merger", "The exact two-to-one contact successor was sealed.", _theorem["merger_closes"]),
        ("formal-ringdown", "The positive finite damping class was sealed.", _theorem["all_ringdowns_close"]),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=(
        ExternalTargetRow("GW151226-COMPLETE-CHIRP-MERGER", SOURCE_IDS[0], "all signal, source, remnant, energy, uncertainty and model-role rows", OBSERVATION_LABEL),
        ExternalTargetRow("GW190521-COMPLETE-RINGDOWN", SOURCE_IDS[1], "all signal, remnant, mode, decay and conditional-scope rows", OBSERVATION_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if a post-seal source changes; rising frequency/amplitude, positive radiation, two-to-one merger or "
        "decaying quadrupolar remnant support fails; any uncertainty or conditional/model boundary is omitted; "
        "GW150914 is relabelled as blind; a dimensional target selects Claim 073; or any hostile control passes."
    ),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "EXPERIMENT_ID", "OBSERVATION_LABEL", "ObservationalEmpiricalPhysicsProgram",
    "SOURCE_FILES", "SOURCE_HASH", "SOURCE_IDS", "SOURCE_PATH", "SPEC",
)
