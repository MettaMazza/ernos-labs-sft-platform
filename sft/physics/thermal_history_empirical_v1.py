"""Post-seal empirical test of the thermal-history terminal law."""

from __future__ import annotations

from dataclasses import replace

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    GeneratedEmpiricalPhysicsProgram,
    empirical_dimensions,
)
from sft.physics.thermal_history_recombination_terminal_law_v1 import theorem_certificate


CLAIM_ID = "SFT-PHYS-VALIDATION-THERMAL-HISTORY-RECOMBINATION-038"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-THERMAL-HISTORY-RECOMBINATION-038"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/thermal-history-postseal-source-record.json"
SOURCE_HASH = "sha256:8ce41a6c68923395da2502fbb8e078dc770ac2c7648c966b241d8c671273a0d8"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/arxiv-1012.3164-cmb-temperature-redshift.pdf", "sha256:aa79c65170e84d6a8dc71dbd0876538c19619a1c926453ce5a54bd96d3f1efb7"),
    ("experiments/external_sources/physics/snapshots/arxiv-2601.22238-primordial-helium.pdf", "sha256:72f646a345c36b77211e6035d3a78345498f0766cf9fc0a54932ebe0dd670c6a"),
    ("experiments/external_sources/physics/snapshots/arxiv-1710.11129-primordial-deuterium.pdf", "sha256:1a6ec19d6568b8854a40e9dd587906f99a8ea94ecd2d5c712ad86aa506b93f4a"),
    ("experiments/external_sources/physics/snapshots/arxiv-1807.06205-planck-overview.pdf", "sha256:dca932893b7d2724aa2b8d33170fc1b5682c425dd56fcd3c5d7b2098d377db5c"),
    ("experiments/external_sources/physics/snapshots/arxiv-1807.06209-planck-cosmological-parameters.pdf", "sha256:8e172730faf07c9f4ff3fdcc7043f76ed67df6f76066d47df30d693025b6ce77"),
    ("experiments/external_sources/physics/snapshots/pdg-2025-bbang-nucleosynthesis.pdf", "sha256:1843c1d9025aa33c059700708f1041c4462364cdb582325f0c685a6ba1b38484"),
)
SOURCE_IDS = (
    "NOTERDAEME-ET-AL-2011-CMB-TEMPERATURE",
    "AVER-ET-AL-2026-PRIMORDIAL-HELIUM",
    "COOKE-PETTINI-STEIDEL-2018-DEUTERIUM",
    "PLANCK-2018-OVERVIEW-PEAKS",
    "PLANCK-2018-COSMOLOGICAL-PARAMETERS",
    "PDG-2025-BBN-REVIEW",
)
OBSERVATION_LABEL = (
    "sealed-thermal-history-law__complete-temperature-abundance-recombination-peak-record__"
    "quarter-equality-and-angular-integer-controls-retained__no-fit"
)


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Post-seal thermal-history, nucleosynthesis and recombination test",
    statement=(
        "After formal Claim 037 is admitted, direct high-redshift CMB thermometry, primordial helium and deuterium, "
        "Planck recombination and acoustic extrema, and the PDG freeze-out synthesis are opened. The measured "
        "temperature exponent contains exact One. The independently derived One/six to One/seven neutron/proton "
        "transport matches the external analytic sequence. Current direct helium measurement lies below and excludes "
        "exact One/four at one standard interval, so the old claim that the analytic family partition is the exact "
        "measured isotope abundance is rejected rather than fitted. Deuterium remains a positive minor channel. Planck "
        "reports finite recombination support and eighteen acoustic extrema; its angular multipoles reject exact integer "
        "multiples of the first peak, validating the formal separation between internal whole modes and observation."
    ),
    dependencies=(
        "SFT-PHYS-THERMAL-HISTORY-RECOMBINATION-TERMINAL-037",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
    ),
    generation_rule=(
        "Generate the complete eight-axis product of sealed thermal relation, complete external target, source provenance, "
        "capability-closed isolation, proof/measurement separation, complete row and adverse-result retention, successor "
        "closure and extension."
    ),
    grammar_boundary=(
        "The admitted temperature exponent One, typed freeze-out/capture sequence, analytic quarter family partition, "
        "positive minor channels, finite visibility and internal acoustic parity; every registered uncertainty endpoint; "
        "all seven Planck TT peak positions and amplitudes; the eighteen-peak mission count; and explicit rejection of "
        "exact observed quarter equality and exact observed angular integer multiples."
    ),
    dimensions=empirical_dimensions(
        "sealed-thermal-history-law-versus-complete-primary-observation-record",
        "The formal receipt was fixed before the new primary snapshots and target record were opened.",
    ),
    exact_result=(
        "The direct high-redshift CMB temperature exponent interval [49/50,517/500] contains exact One. The external "
        "freeze-out sequence is approximately 1/6 then 1/7, matching the separately forced typed transport. Direct "
        "helium Yp=0.2458+/-0.0013 gives [489/2000,2471/10000], which excludes 1/4; therefore 1/4 remains the exact "
        "analytic helium-family partition and is not relabelled as the exact isotope measurement. Direct primordial "
        "deuterium (2.527+/-0.030) times 10^-5 is positive and subordinate. Planck retains z*=1089.92+/-0.25, eighteen "
        "finite extrema and seven complete TT peak rows. Those angular peak intervals are not integer multiples of the "
        "first, so the internal-whole-mode/observed-projection distinction passes and the old angular-integer reading is rejected."
    ),
    induction_base=(
        "The formal receipt fixes the exponent, freeze-out/capture types, analytic family partition, visibility support "
        "and internal acoustic labels before target release."
    ),
    induction_step=(
        "Each additional measurement row, uncertainty endpoint or acoustic extremum is retained once; an unfavorable "
        "row is recorded as a correction and cannot change the sealed survivor."
    ),
    exclusions=(
        "no external value readable by the formal candidate generator or formal independent validator",
        "no fitted cooling exponent, abundance correction, reaction rate, visibility width or angular projection",
        "no historical-blindness claim because V1/V2 named these targets",
        "no omission of the current direct helium interval that excludes exact One/four",
        "no preservation of the old exact observed-quarter or angular-integer claims by weakened comparison",
        "no numerical-zero, negative, irrational, imaginary or floating Fold proof magnitude",
    ),
    operational_witnesses=(
        ("temperature", "The formal temperature-scale invariant is exact.", theorem_certificate()["temperature_transport"]),
        ("freezeout", "The formal typed ratios are One/six and One/seven.", theorem_certificate()["freezeout_ratio"].denominator == 6 and theorem_certificate()["capture_ratio"].denominator == 7),
        ("visibility", "Finite positive visibility and acoustic parity are closed.", theorem_certificate()["visibility"] and theorem_certificate()["acoustic_parity"]),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=(
        ExternalTargetRow("CMB-TEMPERATURE-EXPONENT", SOURCE_IDS[0], "Direct high-redshift temperature exponent and uncertainty", OBSERVATION_LABEL),
        ExternalTargetRow("PRIMORDIAL-HELIUM", SOURCE_IDS[1], "Current direct helium mass fraction and unfavorable exact-quarter control", OBSERVATION_LABEL),
        ExternalTargetRow("PRIMORDIAL-DEUTERIUM", SOURCE_IDS[2], "Direct deuterium abundance and uncertainty", OBSERVATION_LABEL),
        ExternalTargetRow("PLANCK-ACOUSTIC-EXTREMA", SOURCE_IDS[3], "Complete seven TT peak rows and eighteen-extrema mission count", OBSERVATION_LABEL),
        ExternalTargetRow("PLANCK-RECOMBINATION", SOURCE_IDS[4], "Finite recombination redshift record and uncertainty", OBSERVATION_LABEL),
        ExternalTargetRow("FREEZEOUT-SEQUENCE", SOURCE_IDS[5], "One-sixth to one-seventh analytic transport benchmark", OBSERVATION_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if any source identity or registered row changes; if exact One leaves the temperature-exponent interval; "
        "if the typed One/six to One/seven sequence is absent; if the unfavorable helium exclusion is hidden or used to "
        "fit a correction; if deuterium is nonpositive; if recombination support or the acoustic census is erased; if "
        "observed peak intervals are falsely relabelled as exact integer multiples; or if any target changes the formal survivor."
    ),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "EXPERIMENT_ID", "OBSERVATION_LABEL", "ObservationalEmpiricalPhysicsProgram", "SOURCE_FILES",
    "SOURCE_HASH", "SOURCE_IDS", "SOURCE_PATH", "SPEC",
)
