"""Post-seal IUPAC/NIST comparison for terminal atomic periodicity."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from sft.engine.source import hash_file
from sft.physics.atomic_shell_periodicity_successor_laws_v1 import (
    ATOMIC_SHELL_PERIODICITY_TERMINAL_ID,
    generated_period_closures,
    generated_period_widths,
)
from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)
from sft.physics.prior_value_laws import positive_take


SOURCE_ID = "IUPAC-NIST-ATOMIC-SHELL-PERIODICITY-2022-2026"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/atomic-shell-periodicity-successor-source-record.json"
SOURCE_HASH = "sha256:3132a0088e0346af7d0ae0b88937765b4c6dfad951d79bb9677103aa6affbdbb"
IUPAC_HASH = "sha256:ef6ca2f6d46554f96e30ad3a60693d6630fe45ad81ce83cb14e508c6cbb7d3b3"
MEASURED_LABEL = (
    "exact-shell-sum-and-generated-period-widths-match-IUPAC"
    "__NIST-configurations-and-ionization-envelope-reset-vector-passed-with-local-dips-retained"
)


def authoritative_record(root: Path) -> dict[str, object]:
    source = root / SOURCE_PATH
    if hash_file(source) != SOURCE_HASH:
        raise ValueError("atomic periodicity source record identity changed")
    payload = json.loads(source.read_text(encoding="utf-8"))
    custody = payload.get("custody", {})
    required = {
        "classification": "observational_derivation",
        "development_targets_already_known": True,
        "protocol_classification": "observational-data-informed_target-inaccessible_sealed-prediction",
        "empirical_prediction_protocol": True,
        "target_inaccessible_during_prediction_execution": True,
        "formal_relations_contain_measurement": False,
        "measurements_select_formal_survivors": False,
        "engine_prediction_sealed_before_target_release_within_run": True,
        "complete_reported_uncertainties_retained": True,
        "missing_uncertainty_display_resolution_separately_labelled": True,
        "local_nonmonotonic_rows_retained_as_adverse_evidence": True,
        "shell_capacity_and_period_width_distinguished": True,
    }
    if any(custody.get(key) != value for key, value in required.items()):
        raise ValueError("atomic periodicity custody disclosure changed")
    periodic = payload["sources"]["periodic_table"]
    snapshot = root / periodic["snapshot_path"]
    if periodic["snapshot_hash"] != IUPAC_HASH or hash_file(snapshot) != IUPAC_HASH:
        raise ValueError("IUPAC periodic-table identity changed")
    rows = payload["sources"]["ionization"]["rows"]
    required_rows = {"H", "He", "Li", "Be", "B", "N", "O", "Ne", "Na", "Mg", "Al", "Ar", "K", "Kr", "Rb", "Xe", "Cs", "Rn", "Fr"}
    if set(rows) != required_rows:
        raise ValueError("NIST periodicity row set changed")
    return payload


def ionization_interval(root: Path, symbol: str) -> tuple[Fraction, Fraction]:
    row = authoritative_record(root)["sources"]["ionization"]["rows"][symbol]
    centre = Fraction(row["value_eV"])
    spread = Fraction(row.get("uncertainty_eV", row.get("display_half_width_eV", "missing")))
    return positive_take(centre, spread), centre + spread


def atomic_periodicity_classification(root: Path) -> str:
    record = authoritative_record(root)
    periodic = record["sources"]["periodic_table"]["row"]
    if tuple(periodic["closure_atomic_numbers"]) != generated_period_closures(7):
        raise ValueError("generated closures differ from the IUPAC table")
    if tuple(periodic["period_widths"]) != generated_period_widths(7):
        raise ValueError("generated widths differ from the IUPAC table")

    rows = record["sources"]["ionization"]["rows"]
    configurations = {
        "He": "1s2", "Li": "1s2.2s", "Ne": "1s2.2s2.2p6", "Na": "[Ne].3s",
        "Ar": "[Ne].3s2.3p6", "K": "[Ar].4s", "Kr": "[Ar].3d10.4s2.4p6",
        "Rb": "[Kr].5s", "Xe": "[Cd].5p6", "Cs": "[Xe].6s", "Rn": "[Hg].6p6", "Fr": "[Rn].7s",
    }
    if any(rows[symbol]["ground_shells"] != expected for symbol, expected in configurations.items()):
        raise ValueError("registered NIST closure/successor configuration changed")

    starts_and_ends = (("H", "He"), ("Li", "Ne"), ("Na", "Ar"), ("K", "Kr"), ("Rb", "Xe"), ("Cs", "Rn"))
    if not all(ionization_interval(root, end)[0] > ionization_interval(root, start)[1] for start, end in starts_and_ends):
        raise ValueError("a registered period endpoint no longer exceeds its start")
    resets = (("He", "Li"), ("Ne", "Na"), ("Ar", "K"), ("Kr", "Rb"), ("Xe", "Cs"), ("Rn", "Fr"))
    if not all(ionization_interval(root, end)[0] > ionization_interval(root, successor)[1] for end, successor in resets):
        raise ValueError("a registered closure-to-successor ionization reset failed")
    local_dips = (("Be", "B"), ("N", "O"), ("Mg", "Al"))
    if not all(ionization_interval(root, first)[0] > ionization_interval(root, second)[1] for first, second in local_dips):
        raise ValueError("a retained local ionization dip changed")
    return MEASURED_LABEL


ATOMIC_SHELL_PERIODICITY_EMPIRICAL_SPEC = EmpiricalPhysicsSpec(
    claim_id=ATOMIC_SHELL_PERIODICITY_TERMINAL_ID,
    title="Terminal atomic shell and periodicity post-seal IUPAC/NIST comparison",
    statement=(
        "Observation informed the explicit shell/filling law.  The IUPAC closure coordinates and NIST "
        "configuration/ionization vector remain capability-closed while the engine exhausts and seals the exact "
        "target-inaccessible relation.  Post-seal comparison matches all seven period widths, every registered "
        "closure/successor configuration, six rising envelopes, six resets and three deliberately retained local dips."
    ),
    dependencies=(
        ATOMIC_SHELL_PERIODICITY_TERMINAL_ID,
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis post-seal atomic periodicity comparison product.",
    grammar_boundary="The complete generated closure/width prefix through 118, registered NIST closure/successor configurations, all six period envelopes and resets, three adverse local dips, source identities and uncertainty/display-resolution records.",
    dimensions=empirical_dimensions(
        "sealed-shell-fill-recurrence-versus-complete-IUPAC-NIST-periodicity-vector",
        "Every closure, width, configuration, exact interval and adverse local reversal remains visible in one post-seal decision.",
    ),
    exact_result="The exact closure and width vectors equal IUPAC; NIST ground configurations agree at every registered closure and successor; all period envelopes rise and reset while all three known local dips remain retained.",
    induction_base="The source record holds the first 1s closure and first successor beside the sealed shell-One result.",
    induction_step="Each later source revision creates a new comparison receipt and cannot rewrite the relation, predecessor receipts, source rows or adverse controls.",
    exclusions=(
        "no target readable by the executable law",
        "no measured value selecting the formal survivor",
        "no strict-monotonicity rewrite that erases local dips",
        "no floating-point interval decision",
        "no omitted uncertainty, display-resolution label, period or reset row",
    ),
    operational_witnesses=((
        "target-free-generated-vector",
        "The formal closure and width vectors exist exactly before source release.",
        generated_period_closures(7) == (2, 10, 18, 36, 54, 86, 118) and generated_period_widths(7) == (2, 8, 8, 18, 18, 32, 32),
    ),),
    experiment_id="SFT-EXP-PHYS-ATOMIC-SHELL-PERIODICITY-TERMINAL-005",
    expected_observation_label=MEASURED_LABEL,
    target_rows=(ExternalTargetRow(
        "IUPAC-NIST-ATOMIC-PERIODICITY-COMPLETE-VECTOR",
        SOURCE_ID,
        "IUPAC 2022 complete table through 118 and NIST ASD 5.12 registered neutral-atom configuration/ionization rows",
        MEASURED_LABEL,
    ),),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "The claim fails if any generated closure or width differs, a registered NIST configuration disagrees, "
        "a period envelope or reset fails, a retained local dip is erased, any source identity changes, target "
        "access precedes sealing, or observational development is concealed."
    ),
)


class AtomicShellPeriodicityValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        validation = BlindExternalMeasurementValidator(self.root, ATOMIC_SHELL_PERIODICITY_EMPIRICAL_SPEC).validate(sealed)
        if atomic_periodicity_classification(self.root) != MEASURED_LABEL or not validation.passed:
            raise ValueError("atomic shell periodicity authoritative classification changed")
        return validation


ATOMIC_SHELL_PERIODICITY_EMPIRICAL_SPEC.validate()


__all__ = (
    "ATOMIC_SHELL_PERIODICITY_EMPIRICAL_SPEC",
    "AtomicShellPeriodicityValidator",
    "MEASURED_LABEL",
    "SOURCE_HASH",
    "SOURCE_ID",
    "SOURCE_PATH",
    "atomic_periodicity_classification",
    "authoritative_record",
    "ionization_interval",
)
