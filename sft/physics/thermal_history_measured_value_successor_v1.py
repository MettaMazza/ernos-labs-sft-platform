"""Measured-value successor for thermal history and physical helium."""

from dataclasses import replace
from fractions import Fraction

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import EmpiricalPhysicsSpec, ExternalTargetRow, GeneratedEmpiricalPhysicsProgram, empirical_dimensions
from sft.physics.helium_isotope_closure_terminal_law_v1 import isotope_closure_ledger
from sft.physics.thermal_history_recombination_terminal_law_v1 import theorem_certificate


CLAIM_ID = "SFT-PHYS-VALIDATION-THERMAL-HISTORY-MEASURED-VALUE-058"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-THERMAL-HISTORY-MEASURED-VALUE-058"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/thermal-history-measured-value-successor-source-record.json"
SOURCE_HASH = "sha256:9b62430aa48d7f3d1811327ca147c133777c9e7c37cfcfff3e927f04e7a68641"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/thermal-history-postseal-source-record.json", "sha256:8ce41a6c68923395da2502fbb8e078dc770ac2c7648c966b241d8c671273a0d8"),
    ("experiments/external_sources/physics/snapshots/arxiv-1012.3164-cmb-temperature-redshift.pdf", "sha256:aa79c65170e84d6a8dc71dbd0876538c19619a1c926453ce5a54bd96d3f1efb7"),
    ("experiments/external_sources/physics/snapshots/arxiv-2601.22238-primordial-helium.pdf", "sha256:72f646a345c36b77211e6035d3a78345498f0766cf9fc0a54932ebe0dd670c6a"),
    ("experiments/external_sources/physics/snapshots/arxiv-1710.11129-primordial-deuterium.pdf", "sha256:1a6ec19d6568b8854a40e9dd587906f99a8ea94ecd2d5c712ad86aa506b93f4a"),
    ("experiments/external_sources/physics/snapshots/arxiv-1807.06205-planck-overview.pdf", "sha256:dca932893b7d2724aa2b8d33170fc1b5682c425dd56fcd3c5d7b2098d377db5c"),
    ("experiments/external_sources/physics/snapshots/arxiv-1807.06209-planck-cosmological-parameters.pdf", "sha256:8e172730faf07c9f4ff3fdcc7043f76ed67df6f76066d47df30d693025b6ce77"),
    ("experiments/external_sources/physics/snapshots/pdg-2025-bbang-nucleosynthesis.pdf", "sha256:1843c1d9025aa33c059700708f1041c4462364cdb582325f0c685a6ba1b38484"),
    ("claims/SFT-PHYS-THERMAL-HISTORY-RECOMBINATION-TERMINAL-037/certificate.json", "sha256:d3b85781f4413b1fe50145852f202342bb18ea31ef3db510a295f221d60c6bb3"),
    ("claims/SFT-PHYS-THERMAL-HELIUM-ISOTOPE-TERMINAL-057/certificate.json", "sha256:1222b7660115f66ca7f69affed5464c2ef65cc83e1c16dd7bf47d038a9019fa7"),
)
SOURCE_IDS = ("NOTERDAEME-ET-AL-2011-CMB-TEMPERATURE", "AVER-ET-AL-2026-PRIMORDIAL-HELIUM", "COOKE-PETTINI-STEIDEL-2018-DEUTERIUM", "PLANCK-2018-OVERVIEW-PEAKS", "PLANCK-2018-COSMOLOGICAL-PARAMETERS", "PDG-2025-BBN-REVIEW")
OBSERVATION_LABEL = "temperature-exponent-and-physical-helium-59-over-240-inside-measurements__freezeout-deuterium-recombination-and-acoustic-records-complete__no-quarter-exclusion-reward"


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


TARGET_ROWS = (
    ExternalTargetRow("CMB-TEMPERATURE-EXPONENT", SOURCE_IDS[0], "complete measured exponent interval", OBSERVATION_LABEL),
    ExternalTargetRow("PHYSICAL-PRIMORDIAL-HELIUM", SOURCE_IDS[1], "complete direct Yp interval", OBSERVATION_LABEL),
    ExternalTargetRow("PRIMORDIAL-DEUTERIUM", SOURCE_IDS[2], "complete direct D/H interval", OBSERVATION_LABEL),
    ExternalTargetRow("PLANCK-PEAK-CENSUS", SOURCE_IDS[3], "eighteen extrema and complete seven TT rows", OBSERVATION_LABEL),
    ExternalTargetRow("PLANCK-RECOMBINATION", SOURCE_IDS[4], "finite recombination-redshift record", OBSERVATION_LABEL),
    ExternalTargetRow("PDG-FREEZEOUT-CAPTURE", SOURCE_IDS[5], "complete approximate one-sixth to one-seventh sequence", OBSERVATION_LABEL),
)


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Thermal history and physical helium measured-value correction",
    statement=(
        "The analytic One/four family partition and the independently enumerated physical isotope share 59/240 remain "
        "separately typed. The forced physical share lies inside the complete direct helium interval. Exact temperature "
        "transport exponent One lies inside the high-redshift thermometry interval; the typed one-sixth to one-seventh "
        "freeze-out sequence, positive deuterium channel, finite recombination record, eighteen extrema and all seven TT "
        "peak rows are retained. Angular projection differences are method records, not rewarded mismatches."
    ),
    dependencies=(
        "SFT-PHYS-THERMAL-HISTORY-RECOMBINATION-TERMINAL-037",
        "SFT-PHYS-THERMAL-HELIUM-ISOTOPE-TERMINAL-057",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis product of physical thermal carrier, isotope relation, provenance, custody, proof/measurement separation, complete rows, successor closure and no extra rule.",
    grammar_boundary="The admitted analytic and physical-isotope receipts; complete temperature, helium, deuterium, freezeout, recombination and acoustic records; all uncertainty endpoints; all seven TT rows; all eighteen extrema; projection boundary; and every source identity.",
    dimensions=empirical_dimensions(
        "sealed-physical-thermal-values-versus-complete-measurements",
        "The exact temperature exponent and physical helium isotope share seal before their complete measured intervals open; remaining rows preserve their exact structural and observation types.",
    ),
    exact_result=(
        "Exact exponent One lies inside [49/50,517/500]. Exact physical helium-isotope share 59/240 lies inside "
        "[489/2000,2471/10000]. The one-sixth to one-seventh freezeout sequence, positive deuterium, finite "
        "recombination support, eighteen extrema and all seven TT rows remain complete. No excluded quarter or angular "
        "noninteger record is admitted as a successful result."
    ),
    induction_base="The analytic family and completed physical isotope partition seal before any thermal or abundance target opens.",
    induction_step="Each additional measurement, uncertainty endpoint or acoustic row is retained once without altering the sealed isotope share, temperature law or projection type.",
    exclusions=(
        "no measured helium central value or uncertainty in either formal survivor",
        "no fitted decay, capture, binding, reaction, projection or abundance coefficient",
        "no exact-quarter-exclusion or noninteger-angular-position mismatch rewarded as closure",
        "no deleted row or rescaled uncertainty",
        "no numerical-nothingness, negative, irrational, imaginary, floating, NaN, continuum or completed-infinity Fold proof magnitude",
    ),
    operational_witnesses=(
        ("physical-helium", "The formal physical isotope share is exactly 59/240.", isotope_closure_ledger()["physical_helium_isotope_share"] == Fraction(59, 240)),
        ("thermal-structure", "Temperature, freezeout, visibility and acoustic witnesses remain closed.", theorem_certificate()["temperature_transport"] and theorem_certificate()["visibility"] and bool(theorem_certificate()["acoustic_parity"])),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=TARGET_ROWS,
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if a source or dependency changes; exponent One or 59/240 leaves its complete measured interval; the "
        "freezeout sequence, positive deuterium, finite recombination support, extrema or TT rows are missing; an "
        "uncertainty is widened; a mismatch is rewarded; or targets alter either formal survivor."
    ),
)

SPEC.validate()

__all__ = ("CLAIM_ID", "EXPERIMENT_ID", "OBSERVATION_LABEL", "ObservationalEmpiricalPhysicsProgram", "SOURCE_FILES", "SOURCE_HASH", "SOURCE_IDS", "SOURCE_PATH", "SPEC", "TARGET_ROWS")
