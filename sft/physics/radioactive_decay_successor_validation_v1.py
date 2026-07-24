"""Post-seal NUBASE2020 comparison for radioactive modes and half-lives."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import re

from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)
from sft.physics.prior_value_laws import positive_take
from sft.physics.radioactive_decay_successor_laws_v1 import (
    RADIOACTIVE_DECAY_TERMINAL_ID,
    primitive_transition_classes,
    survival_part,
    transport_half_life,
)


SOURCE_ID = "AMDC-NUBASE2020-DECAY-HALFLIFE-2021"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/radioactive-decay-successor-source-record.json"
SOURCE_HASH = "sha256:9a2275f1c4f82f0bdf3d41b25a1c8af535fefb7451ea28bad4f6cb2beec32391"
RAW_PATH = "experiments/external_sources/physics/snapshots/nubase2020-nubase_4.mas20"
RAW_HASH = "sha256:1585a5eea86c5e17e90307c7e6e786d060049c4039e392a261ff6db977df9859"
RELEASE = "boundary-release-or-decomposition"
CONVERSION = "held-label-conversion"
DEEXCITATION = "internal-level-deexcitation"
PURE_CONVERSION_CODES = frozenset({"B", "B-", "B+", "2B-", "2B+", "EC", "EC+B+", "e+"})
MEASURED_LABEL = (
    "sealed-three-primitive-radioactive-topologies-and-exact-survival-1-over-2-to-k"
    "__complete-NUBASE2020-5843-state-5500-decay-row-8718-entry-50-code-census"
    "__all-50-codes-map-to-release-conversion-deexcitation-or-ordered-composition"
    "__4700-positive-numeric-half-life-carriers-transport-without-selecting-the-law"
    "__alpha-beta-gamma-retained-as-representatives-while-literal-only-three-named-code-reading-is-rejected"
)


def authoritative_record(root: Path) -> dict[str, object]:
    if hash_file(root / SOURCE_PATH) != SOURCE_HASH or hash_file(root / RAW_PATH) != RAW_HASH:
        raise ValueError("NUBASE2020 decay source identity changed")
    payload = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    custody = payload.get("custody", {})
    required = {
        "development_targets_already_known": True,
        "protocol_classification": "observational-data-informed_target-inaccessible_sealed-prediction",
        "empirical_prediction_protocol": True,
        "target_inaccessible_during_prediction_execution": True,
        "formal_relations_contain_measurement": False,
        "measurements_select_formal_survivors": False,
        "engine_prediction_sealed_before_target_release_within_run": True,
        "complete_reported_uncertainties_retained": True,
        "all_named_modes_must_map_or_halt": True,
        "alpha_beta_gamma_are_representatives_not_only_named_codes": True,
        "no_ontic_randomness_imported": True,
    }
    if any(custody.get(key) != value for key, value in required.items()):
        raise ValueError("NUBASE2020 decay custody disclosure changed")
    census = payload["complete_decay_census"]
    expected = {
        "all_nuclear_state_rows": 5843,
        "rows_with_decay_modes": 5500,
        "decay_mode_entry_count": 8718,
        "distinct_decay_mode_code_count": 50,
        "numeric_positive_half_life_row_count": 4700,
    }
    if any(census.get(key) != value for key, value in expected.items()):
        raise ValueError("registered NUBASE2020 decay census changed")
    return payload


def mode_codes(branching_record: str) -> tuple[str, ...]:
    result: list[str] = []
    for part in branching_record.split(";"):
        match = re.match(r"([^= <~?>]+)", part.strip())
        if match and match.group(1) != "IS":
            result.append(match.group(1))
    return tuple(result)


def nubase_rows(root: Path) -> tuple[dict[str, object], ...]:
    authoritative_record(root)
    rows: list[dict[str, object]] = []
    for raw_line in (root / RAW_PATH).read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("#") or len(raw_line) < 17:
            continue
        line = raw_line.ljust(209)
        try:
            mass = int(line[0:3])
            charge = int(line[4:7])
        except ValueError:
            continue
        half_life = line[69:78].strip()
        numeric_half_life: Fraction | tuple[()] = ()
        if half_life and half_life not in {"stbl", "p-unst"} and "#" not in half_life:
            try:
                candidate = Fraction(half_life)
                if candidate > 0:
                    numeric_half_life = candidate
            except (ValueError, ZeroDivisionError):
                pass
        branching = line[119:209].strip()
        rows.append({
            "mass_number": mass,
            "charge_count": charge,
            "state_index": line[7:8],
            "nuclide": line[11:17].strip(),
            "half_life_inscription": half_life,
            "half_life": numeric_half_life,
            "half_life_unit": line[78:80].strip(),
            "half_life_uncertainty": line[81:88].strip(),
            "branching_record": branching,
            "mode_codes": mode_codes(branching),
        })
    if len(rows) != 5843:
        raise ValueError("complete NUBASE2020 state census changed")
    return tuple(rows)


def primitive_trace_for_code(code: str) -> tuple[str, ...]:
    if code == "IT":
        return (DEEXCITATION,)
    if code in PURE_CONVERSION_CODES:
        return (CONVERSION,)
    if code.startswith("B-") or code.startswith("B+"):
        return (CONVERSION, RELEASE)
    if code:
        return (RELEASE,)
    raise ValueError("empty decay code has no primitive trace")


def row_by_coordinate(root: Path, mass: int, charge: int, state: str) -> dict[str, object]:
    matches = tuple(
        row for row in nubase_rows(root)
        if row["mass_number"] == mass and row["charge_count"] == charge and row["state_index"] == state
    )
    if len(matches) != 1:
        raise ValueError("NUBASE2020 coordinate is absent or duplicated")
    return matches[0]


def exact_half_life_interval(row: dict[str, object]) -> tuple[Fraction, Fraction]:
    value = row["half_life"]
    if not isinstance(value, Fraction):
        raise ValueError("registered half-life is not a positive exact value")
    uncertainty = Fraction(str(row["half_life_uncertainty"]))
    return positive_take(value, uncertainty), value + uncertainty


def measurement_analysis(root: Path) -> dict[str, object]:
    rows = nubase_rows(root)
    decay_rows = tuple(row for row in rows if row["mode_codes"])
    numeric_rows = tuple(row for row in rows if isinstance(row["half_life"], Fraction))
    counts = Counter(code for row in decay_rows for code in row["mode_codes"])
    traces = {code: primitive_trace_for_code(code) for code in counts}
    examples = {
        "uranium238_ground": row_by_coordinate(root, 238, 92, "0"),
        "carbon14_ground": row_by_coordinate(root, 14, 6, "0"),
        "technetium99_isomer": row_by_coordinate(root, 99, 43, "1"),
        "beryllium7_ground": row_by_coordinate(root, 7, 4, "0"),
        "beryllium8_ground": row_by_coordinate(root, 8, 4, "0"),
    }
    example_intervals = {
        name: [str(value) for value in exact_half_life_interval(row)]
        for name, row in examples.items()
    }
    transported = {
        name: {
            str(rank): {
                "elapsed_in_reported_unit": str(transport_half_life(row["half_life"], rank)["elapsed_time"]),
                "survival_part": str(survival_part(rank)),
            }
            for rank in range(1, 4)
        }
        for name, row in examples.items()
        if isinstance(row["half_life"], Fraction)
    }
    return {
        "all_nuclear_state_rows": len(rows),
        "rows_with_decay_modes": len(decay_rows),
        "decay_mode_entry_count": sum(counts.values()),
        "distinct_decay_mode_code_count": len(counts),
        "numeric_positive_half_life_row_count": len(numeric_rows),
        "mode_code_counts": dict(sorted(counts.items())),
        "mode_primitive_traces": {code: list(trace) for code, trace in sorted(traces.items())},
        "all_codes_mapped": set(traces) == set(counts) and all(trace for trace in traces.values()),
        "all_three_primitives_observed": set(item for trace in traces.values() for item in trace) == {RELEASE, CONVERSION, DEEXCITATION},
        "composite_delayed_modes_observed": any(len(trace) > 1 for trace in traces.values()),
        "literal_only_three_named_codes_rejected": len(counts) > len(primitive_transition_classes()),
        "registered_examples": {
            name: {
                "nuclide": row["nuclide"],
                "half_life": row["half_life_inscription"],
                "unit": row["half_life_unit"],
                "uncertainty": row["half_life_uncertainty"],
                "branching_record": row["branching_record"],
                "mode_codes": list(row["mode_codes"]),
            }
            for name, row in examples.items()
        },
        "registered_example_intervals": example_intervals,
        "exact_half_life_transports": transported,
        "survival_law": [str(survival_part(rank)) for rank in range(1, 8)],
        "no_finite_survival_part_is_empty": all(survival_part(rank) > 0 for rank in range(1, 128)),
    }


def radioactive_decay_classification(root: Path) -> str:
    analysis = measurement_analysis(root)
    exact_counts = (
        analysis["all_nuclear_state_rows"],
        analysis["rows_with_decay_modes"],
        analysis["decay_mode_entry_count"],
        analysis["distinct_decay_mode_code_count"],
        analysis["numeric_positive_half_life_row_count"],
    )
    if exact_counts != (5843, 5500, 8718, 50, 4700):
        raise ValueError("complete NUBASE2020 decay vector changed")
    if not all(analysis[key] is True for key in (
        "all_codes_mapped",
        "all_three_primitives_observed",
        "composite_delayed_modes_observed",
        "literal_only_three_named_codes_rejected",
        "no_finite_survival_part_is_empty",
    )):
        raise ValueError("NUBASE2020 topology or half-life comparison failed")
    expected_examples = {
        "uranium238_ground": ("4.463", "Gy", "0.003", {"A", "SF", "2B-"}),
        "carbon14_ground": ("5.70", "ky", "0.03", {"B-"}),
        "technetium99_isomer": ("6.0066", "h", "0.0002", {"IT", "B-"}),
        "beryllium7_ground": ("53.22", "d", "0.06", {"EC"}),
        "beryllium8_ground": ("81.9", "as", "3.7", {"A"}),
    }
    for name, (value, unit, uncertainty, modes) in expected_examples.items():
        row = analysis["registered_examples"][name]
        if (row["half_life"], row["unit"], row["uncertainty"], set(row["mode_codes"])) != (value, unit, uncertainty, modes):
            raise ValueError(f"registered NUBASE2020 example changed: {name}")
    return MEASURED_LABEL


RADIOACTIVE_DECAY_EMPIRICAL_SPEC = EmpiricalPhysicsSpec(
    claim_id=RADIOACTIVE_DECAY_TERMINAL_ID,
    title="Terminal radioactive topology and half-life post-seal NUBASE2020 comparison",
    statement=(
        "Observation informed the explicit successor, but the complete NUBASE2020 table remains capability-closed "
        "until the three primitive topologies and exact 1/2^k survival law seal. After release, every nuclear state, "
        "decay row, named mode code, mode entry, positive numeric half-life and registered uncertainty is retained."
    ),
    dependencies=(
        RADIOACTIVE_DECAY_TERMINAL_ID,
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete post-seal 5,843-state, 5,500-decay-row, 8,718-entry, 50-code, 4,700-positive-half-life, topology, composition, uncertainty, custody and adverse-only-three product.",
    grammar_boundary="Every NUBASE2020 nuclear-state row, non-abundance decay-mode inscription, positive numeric half-life with reported unit/uncertainty, mode-to-primitive trace, composite delayed trace, registered example and source-custody state.",
    dimensions=empirical_dimensions(
        "sealed-three-topology-and-one-over-two-to-k-law-versus-complete-NUBASE2020-decay-vector",
        "Every code must map or halt; all positive half-life carriers transport the sealed survival law without selecting it.",
    ),
    exact_result=(
        "All 50 distinct NUBASE2020 decay codes across 8,718 entries map to boundary release/decomposition, held-label "
        "conversion, internal de-excitation or an ordered composition. The table contains 4,700 positive numeric "
        "half-life carriers; exact transport yields survival 1/2^k at each positive integer multiple. Alpha, beta "
        "and gamma remain canonical representatives, while the literal claim that only three named codes exist is rejected."
    ),
    induction_base="One released authoritative mode code must map to one sealed primitive trace; one positive half-life carrier transports exact survival one-half.",
    induction_step="Every additional code must map to one primitive or an ordered composition, and every additional half-life count multiplies the retained support by one-half without changing the dimensional carrier or opening the target to execution.",
    exclusions=(
        "no NUBASE row, isotope name, mode code, half-life or uncertainty readable by the executable law",
        "no literal only-three-named-decay-code claim",
        "no continuum exponential, floating-point interval decision, fitted rate or ontic random choice",
        "no omitted particle, cluster, capture, fission, delayed, abundance-boundary or composite row",
        "no measurement-to-formal-survivor flow",
    ),
    operational_witnesses=((
        "target-free-three-topology-and-survival-law",
        "Three primitive transition classes and exact survival 1/2^k exist before source release.",
        len(primitive_transition_classes()) == 3
        and tuple(survival_part(rank) for rank in range(1, 4)) == (Fraction(1, 2), Fraction(1, 4), Fraction(1, 8)),
    ),),
    experiment_id="SFT-EXP-PHYS-NUCLEAR-RADIOACTIVE-DECAY-TERMINAL-005",
    expected_observation_label=MEASURED_LABEL,
    target_rows=(
        ExternalTargetRow("NUBASE2020-COMPLETE-DECAY-CENSUS", SOURCE_ID, "NUBASE2020 complete state, decay-row, mode-entry and distinct-code census", MEASURED_LABEL),
        ExternalTargetRow("NUBASE2020-COMPLETE-HALFLIFE-CENSUS", SOURCE_ID, "NUBASE2020 all positive numeric half-life carriers, units and reported uncertainties", MEASURED_LABEL),
        ExternalTargetRow("NUBASE2020-RELEASE-REPRESENTATIVES", SOURCE_ID, "NUBASE2020 uranium-238/beryllium-8 alpha, cluster and fission records", MEASURED_LABEL),
        ExternalTargetRow("NUBASE2020-CONVERSION-REPRESENTATIVES", SOURCE_ID, "NUBASE2020 carbon-14 beta-minus and beryllium-7 electron-capture records", MEASURED_LABEL),
        ExternalTargetRow("NUBASE2020-DEEXCITATION-REPRESENTATIVE", SOURCE_ID, "NUBASE2020 technetium-99m internal-transition record", MEASURED_LABEL),
        ExternalTargetRow("NUBASE2020-ONLY-THREE-ADVERSE", SOURCE_ID, "All NUBASE2020 proton, neutron, cluster, fission, capture and delayed composite codes", MEASURED_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "The claim fails if any NUBASE2020 decay code cannot be expressed by the three primitive topologies or their "
        "composition, a positive half-life cannot transport exact finite survival, a row or uncertainty is omitted, "
        "the literal only-three-code claim is retained, or target access precedes sealing."
    ),
)


class RadioactiveDecayValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        validation = BlindExternalMeasurementValidator(
            self.root, RADIOACTIVE_DECAY_EMPIRICAL_SPEC
        ).validate(sealed)
        if radioactive_decay_classification(self.root) != MEASURED_LABEL or not validation.passed:
            raise ValueError("radioactive decay authoritative classification changed")
        return validation


RADIOACTIVE_DECAY_EMPIRICAL_SPEC.validate()


__all__ = (
    "MEASURED_LABEL",
    "RADIOACTIVE_DECAY_EMPIRICAL_SPEC",
    "RadioactiveDecayValidator",
    "RAW_HASH",
    "RAW_PATH",
    "SOURCE_HASH",
    "SOURCE_ID",
    "SOURCE_PATH",
    "authoritative_record",
    "measurement_analysis",
    "mode_codes",
    "nubase_rows",
    "primitive_trace_for_code",
    "radioactive_decay_classification",
)
