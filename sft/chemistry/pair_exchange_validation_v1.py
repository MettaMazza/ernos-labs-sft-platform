"""Capability-closed prediction and complete NIST H2 exchange validation for ELEC-006."""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import platform
import re
from typing import Optional

from sft.chemistry.pair_exchange_batch_v1 import (
    IDENTITY_HASH,
    IDENTITY_PATH,
    PAIR_EXCHANGE_SPEC,
    SOURCE_ID,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.pair_exchange_law_v1 import (
    ALTERNATING_EXCHANGE,
    PRESERVING_EXCHANGE,
    SAME_CELL_ADMITTED,
    SAME_CELL_EXCLUDED,
    MolecularElectronPairState,
    build_same_support_pair,
    exchange_product,
    explicit_occupancy_compatible,
    pair_state_from_multiplicity,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    FoldTable,
    FoldWord,
    HostilePackageAuditor,
    PositiveRatio,
    TargetVault,
    fold_program_from_mapping,
    snapshot_protected_tree,
    target_identity_from_release,
)
from sft.claim_evidence.fold_language import EMPTY_ONE, FoldLanguageHalt
from sft.engine import (
    EmpiricalValidation,
    seal_isolation_certificate,
    seal_target_custody_certificate,
    unsealed_isolation_certificate,
    unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file


TERM_PATTERN = re.compile(r"\^([1-9][0-9]*)(Σ|Π|Δ|Φ)")
ORBITAL_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])([1-9][0-9]*)([spdfgh])\s*([σπδφ])(?:\^([1-9][0-9]*))?"
)
ENERGY_PATTERN = re.compile(r"^[\[\(]*\s*~?\s*([0-9]+(?:\.[0-9_]*)?)")


class _IndependentH2TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.table_depth = 0
        self.in_row = False
        self.in_cell = False
        self.cell_parts: list[str] = []
        self.current_row: list[str] = []
        self.rows: list[tuple[str, ...]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attributes = dict(attrs)
        if tag == "table" and "data" in (attributes.get("class") or "").split():
            self.table_depth += 1
        elif self.table_depth and tag == "tr":
            self.in_row, self.current_row = True, []
        elif self.in_row and tag in {"td", "th"}:
            self.in_cell, self.cell_parts = True, []
        elif self.in_cell and tag == "sup":
            self.cell_parts.append("^")
        elif self.in_cell and tag == "sub":
            self.cell_parts.append("_")

    def handle_endtag(self, tag: str) -> None:
        if self.in_cell and tag in {"td", "th"}:
            self.current_row.append(" ".join(unescape("".join(self.cell_parts)).split()))
            self.in_cell = False
        elif self.in_row and tag == "tr":
            if self.current_row:
                self.rows.append(tuple(self.current_row))
            self.in_row = False
        elif self.table_depth and tag == "table":
            self.table_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.cell_parts.append(data)


def _term_suffix(state_record: str, term_match: re.Match[str]) -> str:
    boundaries = tuple(
        position
        for position in (
            state_record.find(",", term_match.end()),
            state_record.find(")", term_match.end()),
            state_record.find(" ", term_match.end()),
        )
        if position >= 0
    )
    return state_record[term_match.end() : min(boundaries) if boundaries else len(state_record)]


def _exact_energy(inscription: str) -> Fraction:
    match = ENERGY_PATTERN.search(inscription)
    if match is None or "eV" in inscription:
        raise ValueError("ELEC-006 H2 row lacks one common-unit energy record")
    return Fraction(match.group(1).replace("_", ""))


def _configuration_from_state(state_record: str) -> object:
    match = ORBITAL_PATTERN.search(state_record)
    if match is None:
        return "absence"
    return {
        "positive_radial_recurrence": int(match.group(1)),
        "source_family_label": match.group(2),
        "axis_support_symbol": match.group(3),
        "positive_occupancy_count": int(match.group(4)) if match.group(4) else 1,
    }


def _configuration_key(configuration: dict[str, object]) -> tuple[int, str, str, int]:
    return (
        int(configuration["positive_radial_recurrence"]),
        str(configuration["source_family_label"]),
        str(configuration["axis_support_symbol"]),
        int(configuration["positive_occupancy_count"]),
    )


def _configuration_word(configuration: object) -> object:
    if configuration == "absence":
        return EMPTY_ONE
    if not isinstance(configuration, dict):
        raise ValueError("ELEC-006 configuration has an invalid host form")
    return FoldWord(
        (
            PositiveCount(int(configuration["positive_radial_recurrence"])),
            HeldLabel("source-family-label", str(configuration["source_family_label"])),
            HeldLabel("source-support-symbol", str(configuration["axis_support_symbol"])),
            PositiveCount(int(configuration["positive_occupancy_count"])),
        )
    )


def _identities(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("ELEC-006 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    if document.get("schema") != "sft-v3-pair-exchange-identities/1" or len(rows) != 60:
        raise ValueError("ELEC-006 identity registry is incomplete")
    if len({str(row["target_id"]) for row in rows}) != len(rows):
        raise ValueError("ELEC-006 identity registry contains duplicate targets")
    return rows


def prediction_program_document(root: Path) -> dict[str, object]:
    """Emit the universal pair-exchange law with no state or energy target."""

    _identities(root)
    instructions: list[dict[str, object]] = [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}
    ]
    table_registers: list[str] = []
    position = 0
    sector_rows = (
        (
            "positive-One-width",
            "alternating-exchange",
            "preserving-exchange",
            "same-cell-admitted",
        ),
        (
            "positive-three-width",
            "preserving-exchange",
            "alternating-exchange",
            "same-cell-excluded",
        ),
    )
    for multiplicity, spin, spatial, same_cell in sector_rows:
        for family, label in (
            ("spin-exchange-by-multiplicity", spin),
            ("spatial-exchange-by-multiplicity", spatial),
            ("same-cell-by-multiplicity", same_cell),
        ):
            position += 1
            key, value = f"key-{position}", f"value-{position}"
            instructions.extend(
                (
                    {"opcode": "label", "destination": key, "arguments": [family, multiplicity]},
                    {
                        "opcode": "label",
                        "destination": value,
                        "arguments": [
                            "same-cell-status" if family == "same-cell-by-multiplicity" else "exchange-class",
                            label,
                        ],
                    },
                )
            )
            table_registers.extend((key, value))
    for left, right, result in (
        ("preserving", "preserving", "preserving-exchange"),
        ("preserving", "alternating", "alternating-exchange"),
        ("alternating", "preserving", "alternating-exchange"),
        ("alternating", "alternating", "preserving-exchange"),
    ):
        position += 1
        key, value = f"key-{position}", f"value-{position}"
        instructions.extend(
            (
                {
                    "opcode": "label",
                    "destination": key,
                    "arguments": ["exchange-product", left + "-with-" + right],
                },
                {
                    "opcode": "label",
                    "destination": value,
                    "arguments": ["exchange-class", result],
                },
            )
        )
        table_registers.extend((key, value))
    for law_name, law_family, law_value in (
        ("total-electron-pair", "exchange-class", "alternating-exchange"),
        ("same-support-partners", "exchange-law-result", "distinct-complementary-state-identities"),
        ("energy-order", "exchange-law-result", "retained-observation-not-universal-sign"),
    ):
        position += 1
        key, value = f"key-{position}", f"value-{position}"
        instructions.extend(
            (
                {"opcode": "label", "destination": key, "arguments": ["pair-exchange-law", law_name]},
                {"opcode": "label", "destination": value, "arguments": [law_family, law_value]},
            )
        )
        table_registers.extend((key, value))
    position += 1
    instructions.extend(
        (
            {
                "opcode": "label",
                "destination": f"key-{position}",
                "arguments": ["pair-exchange-law", "maximum-orbital-occupancy"],
            },
            {"opcode": "count", "destination": f"value-{position}", "arguments": ["2"]},
        )
    )
    table_registers.extend((f"key-{position}", f"value-{position}"))
    instructions.extend(
        (
            {"opcode": "table", "destination": "complete-pair-exchange-law", "arguments": table_registers},
            {"opcode": "emit", "destination": "", "arguments": ["complete-pair-exchange-law"]},
        )
    )
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": PAIR_EXCHANGE_SPEC.experiment_id + "-pair-exchange-law-prediction",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": PAIR_EXCHANGE_SPEC.experiment_id,
        "claim_id": PAIR_EXCHANGE_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": PAIR_EXCHANGE_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "prediction_program": prediction_program_document(root),
        "target_references": tuple(
            (row.target_id, row.source_id, row.source_locator, row.snapshot_path, row.snapshot_hash)
            for row in PAIR_EXCHANGE_SPEC.target_rows
        ),
        "target_content_absent_from_prediction": True,
        "target_inaccessible_to_capability_closed_execution": True,
        "all_46_states_and_14_pairs_required": True,
        "energy_order_not_used_to_select_or_define_law": True,
        "absence_glyph_policy": "source glyph 0 denotes an absence baseline only and is never an SFT number",
        "falsification_condition": PAIR_EXCHANGE_SPEC.falsification_condition,
    }


def _resolved_targets(root: Path) -> tuple[tuple[dict[str, object], ...], tuple[dict[str, object], ...]]:
    """Independently reconstruct all 46 H2 states and all 14 exchange-sensitive pairs."""

    identities = _identities(root)
    if hash_file(root / TARGET_PATH) != TARGET_HASH:
        raise ValueError("ELEC-006 withheld target registry changed")
    target_document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    registered_states = {str(row["target_id"]): row for row in target_document.get("state_rows", ())}
    registered_pairs = {str(row["target_id"]): row for row in target_document.get("exchange_pairs", ())}
    if (
        target_document.get("schema") != "sft-v3-pair-exchange-withheld-targets/1"
        or len(registered_states) != 46
        or len(registered_pairs) != 14
        or set(registered_states) | set(registered_pairs) != {str(row["target_id"]) for row in identities}
    ):
        raise ValueError("ELEC-006 target support is incomplete or differs from identities")
    snapshot_path = root / str(identities[0]["snapshot_path"])
    if hash_file(snapshot_path) != identities[0]["snapshot_hash"]:
        raise ValueError("ELEC-006 NIST H2 snapshot changed")
    if any(
        row["snapshot_path"] != identities[0]["snapshot_path"]
        or row["snapshot_hash"] != identities[0]["snapshot_hash"]
        for row in identities
    ):
        raise ValueError("ELEC-006 target identities do not share the registered H2 snapshot")
    parser = _IndependentH2TableParser()
    parser.feed(snapshot_path.read_text(encoding="utf-8"))
    source_rows = tuple(row for row in parser.rows if len(row) == 13 and TERM_PATTERN.search(row[0]))
    if len(source_rows) != 46:
        raise ValueError("ELEC-006 independent H2 state census is incomplete")

    resolved_states = []
    groups: dict[tuple[int, str, str, int], list[dict[str, object]]] = {}
    for ordinal, source_row in enumerate(source_rows, start=1):
        matches = tuple(TERM_PATTERN.finditer(source_row[0]))
        if len(matches) != 1:
            raise ValueError("ELEC-006 H2 row does not retain exactly one term assignment")
        term = matches[0]
        multiplicity = int(term.group(1))
        suffix = _term_suffix(source_row[0], term)
        configuration = _configuration_from_state(source_row[0])
        target_id = f"H2-exchange-state-{ordinal:03d}"
        target = registered_states[target_id]
        spin_exchange = "alternating-exchange" if multiplicity == 1 else "preserving-exchange"
        spatial_exchange = "preserving-exchange" if multiplicity == 1 else "alternating-exchange"
        same_cell = (
            "same-cell-pair-recorded"
            if isinstance(configuration, dict) and int(configuration["positive_occupancy_count"]) == 2
            else "no-explicit-same-cell-pair"
        )
        reconstructed = {
            "target_id": target_id,
            "target_type": "state-exchange-assignment",
            "state_row_ordinal": ordinal,
            "state_record": source_row[0],
            "term_assignment_inscription": term.group(0) + suffix,
            "positive_spin_multiplicity": multiplicity,
            "spin_exchange_class": spin_exchange,
            "spatial_exchange_class": spatial_exchange,
            "total_exchange_class": "alternating-exchange",
            "same_cell_record": same_cell,
            "configuration": configuration,
            "energy_inscription": source_row[1],
            "snapshot_path": str(identities[0]["snapshot_path"]),
            "snapshot_hash": str(identities[0]["snapshot_hash"]),
        }
        if any(target.get(key) != value for key, value in reconstructed.items()):
            raise ValueError("ELEC-006 independent H2 state extraction differs from target")
        target_value = FoldWord(
            (
                HeldLabel("NIST-state-record", source_row[0]),
                HeldLabel("NIST-term-assignment", term.group(0) + suffix),
                PositiveCount(multiplicity),
                HeldLabel("exchange-class", spin_exchange),
                HeldLabel("exchange-class", spatial_exchange),
                ALTERNATING_EXCHANGE,
                HeldLabel("same-cell-observation", same_cell),
                _configuration_word(configuration),
                HeldLabel("NIST-energy-inscription", source_row[1]),
            )
        )
        state_row = {**reconstructed, "target_value": target_value}
        resolved_states.append(state_row)
        if isinstance(configuration, dict):
            groups.setdefault(_configuration_key(configuration), []).append(
                {
                    "target_id": target_id,
                    "ordinal": ordinal,
                    "multiplicity": multiplicity,
                    "state_record": source_row[0],
                    "energy_inscription": source_row[1],
                    "energy": _exact_energy(source_row[1]),
                }
            )

    resolved_pairs = []
    pair_ordinal = 0
    for configuration_key in sorted(groups):
        members = groups[configuration_key]
        singlets = tuple(row for row in members if row["multiplicity"] == 1)
        triplets = tuple(row for row in members if row["multiplicity"] == 3)
        for singlet in singlets:
            for triplet in triplets:
                pair_ordinal += 1
                gap = abs(singlet["energy"] - triplet["energy"])
                if gap <= 0:
                    raise ValueError("ELEC-006 registered pair lacks positive measured separation")
                held_order = (
                    "singlet-below-triplet"
                    if singlet["energy"] < triplet["energy"]
                    else "triplet-below-singlet"
                )
                target_id = f"H2-exchange-pair-{pair_ordinal:03d}"
                target = registered_pairs[target_id]
                configuration = {
                    "positive_radial_recurrence": configuration_key[0],
                    "source_family_label": configuration_key[1],
                    "axis_support_symbol": configuration_key[2],
                    "positive_occupancy_count": configuration_key[3],
                }
                reconstructed = {
                    "target_id": target_id,
                    "target_type": "same-configuration-exchange-pair",
                    "configuration": configuration,
                    "singlet_state_target_id": singlet["target_id"],
                    "singlet_state_record": singlet["state_record"],
                    "singlet_energy_inscription": singlet["energy_inscription"],
                    "triplet_state_target_id": triplet["target_id"],
                    "triplet_state_record": triplet["state_record"],
                    "triplet_energy_inscription": triplet["energy_inscription"],
                    "positive_energy_separation_numerator": gap.numerator,
                    "positive_energy_separation_denominator": gap.denominator,
                    "held_energy_order": held_order,
                    "snapshot_path": str(identities[0]["snapshot_path"]),
                    "snapshot_hash": str(identities[0]["snapshot_hash"]),
                }
                if any(target.get(key) != value for key, value in reconstructed.items()):
                    raise ValueError("ELEC-006 independent exchange-pair extraction differs from target")
                support_identity = "-".join(str(item) for item in configuration_key)
                target_value = FoldWord(
                    (
                        HeldLabel("molecular-orbital-support", support_identity),
                        HeldLabel("singlet-state-record", str(singlet["state_record"])),
                        HeldLabel("triplet-state-record", str(triplet["state_record"])),
                        HeldLabel("singlet-energy-inscription", str(singlet["energy_inscription"])),
                        HeldLabel("triplet-energy-inscription", str(triplet["energy_inscription"])),
                        PositiveRatio.from_pair(gap.numerator, gap.denominator),
                        HeldLabel("energy-order", held_order),
                    )
                )
                resolved_pairs.append(
                    {**reconstructed, "support_identity": support_identity, "target_value": target_value}
                )
    if len(resolved_pairs) != 14:
        raise ValueError("ELEC-006 independent exchange-pair census is incomplete")
    return tuple(resolved_states), tuple(resolved_pairs)


def _prediction_map(table: FoldTable) -> dict[tuple[str, str], object]:
    result = {}
    for entry in table.entries:
        if not isinstance(entry.left, HeldLabel):
            raise ValueError("ELEC-006 prediction key is not a held label")
        result[(entry.left.family, entry.left.label)] = entry.right
    if len(result) != len(table.entries):
        raise ValueError("ELEC-006 prediction contains duplicate keys")
    return result


class PairExchangeValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = PAIR_EXCHANGE_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        state_targets, pair_targets = _resolved_targets(self.root)
        all_targets = state_targets + pair_targets
        envelope = PredictionEnvelope(
            self.spec.experiment_id,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows),
            sealed.seal_hash,
            registration_hash,
        )
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-NIST-target-custodian",
            targets={str(row["target_id"]): row["target_value"] for row in all_targets},
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("ELEC-006 prediction package changed during execution")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        if not isinstance(execution.output, FoldTable):
            raise ValueError("ELEC-006 prediction is not a complete Fold table")
        predicted = _prediction_map(execution.output)

        state_comparisons = []
        state_by_id = {}
        for row in state_targets:
            multiplicity = int(row["positive_spin_multiplicity"])
            key = "positive-One-width" if multiplicity == 1 else "positive-three-width"
            pair_state = pair_state_from_multiplicity("H2", str(row["target_id"]), PositiveCount(multiplicity))
            configuration = row["configuration"]
            occupancy_passed = True
            if isinstance(configuration, dict):
                occupancy_passed = explicit_occupancy_compatible(
                    pair_state, PositiveCount(int(configuration["positive_occupancy_count"]))
                )
            same_cell_record_passed = (
                row["same_cell_record"] == "same-cell-pair-recorded"
                and pair_state.same_cell_status == SAME_CELL_ADMITTED
                if isinstance(configuration, dict) and int(configuration["positive_occupancy_count"]) == 2
                else row["same_cell_record"] == "no-explicit-same-cell-pair"
            )
            passed = (
                pair_state.spin_exchange
                == predicted[("spin-exchange-by-multiplicity", key)]
                == HeldLabel("exchange-class", str(row["spin_exchange_class"]))
                and pair_state.spatial_exchange
                == predicted[("spatial-exchange-by-multiplicity", key)]
                == HeldLabel("exchange-class", str(row["spatial_exchange_class"]))
                and pair_state.same_cell_status
                == predicted[("same-cell-by-multiplicity", key)]
                and pair_state.total_exchange
                == predicted[("pair-exchange-law", "total-electron-pair")]
                == ALTERNATING_EXCHANGE
                and occupancy_passed
                and same_cell_record_passed
            )
            comparison = {
                "target_id": row["target_id"],
                "NIST_state_record": row["state_record"],
                "NIST_term_assignment": row["term_assignment_inscription"],
                "positive_spin_multiplicity": multiplicity,
                "spin_exchange_class": row["spin_exchange_class"],
                "spatial_exchange_class": row["spatial_exchange_class"],
                "total_exchange_class": row["total_exchange_class"],
                "same_cell_record": row["same_cell_record"],
                "configuration": configuration,
                "energy_inscription": row["energy_inscription"],
                "source_ground_glyph_is_absence_baseline": row["energy_inscription"] == "0",
                "passed": passed,
            }
            state_comparisons.append(comparison)
            state_by_id[str(row["target_id"])] = pair_state

        pair_comparisons = []
        for row in pair_targets:
            singlet = state_by_id[str(row["singlet_state_target_id"])]
            triplet = state_by_id[str(row["triplet_state_target_id"])]
            pair = build_same_support_pair(
                "H2",
                str(row["support_identity"]),
                singlet.state_identity.label,
                triplet.state_identity.label,
            )
            gap = PositiveRatio.from_pair(
                int(row["positive_energy_separation_numerator"]),
                int(row["positive_energy_separation_denominator"]),
            )
            passed = (
                pair.singlet_state.spin_exchange == ALTERNATING_EXCHANGE
                and pair.triplet_state.spin_exchange == PRESERVING_EXCHANGE
                and pair.singlet_state.spatial_exchange == PRESERVING_EXCHANGE
                and pair.triplet_state.spatial_exchange == ALTERNATING_EXCHANGE
                and pair.singlet_state.state_identity != pair.triplet_state.state_identity
                and gap.numerator.value >= 1
                and predicted[("pair-exchange-law", "same-support-partners")]
                == HeldLabel("exchange-law-result", "distinct-complementary-state-identities")
                and predicted[("pair-exchange-law", "energy-order")]
                == HeldLabel("exchange-law-result", "retained-observation-not-universal-sign")
            )
            pair_comparisons.append(
                {
                    "target_id": row["target_id"],
                    "configuration": row["configuration"],
                    "singlet_state": row["singlet_state_record"],
                    "triplet_state": row["triplet_state_record"],
                    "singlet_energy_inscription": row["singlet_energy_inscription"],
                    "triplet_energy_inscription": row["triplet_energy_inscription"],
                    "positive_energy_separation_numerator": gap.numerator.value,
                    "positive_energy_separation_denominator": gap.denominator.value,
                    "held_energy_order": row["held_energy_order"],
                    "passed": passed,
                }
            )

        invalid_multiplicity_rejected = False
        try:
            pair_state_from_multiplicity("H2", "invalid", PositiveCount(2))
        except InadmissibleExactValue:
            invalid_multiplicity_rejected = True
        triplet = pair_state_from_multiplicity("H2", "triplet-control", PositiveCount(3))
        same_cell_triplet_rejected = not explicit_occupancy_compatible(triplet, PositiveCount(2))
        third_occurrence_rejected = False
        try:
            explicit_occupancy_compatible(
                pair_state_from_multiplicity("H2", "singlet-control", PositiveCount(1)),
                PositiveCount(3),
            )
        except InadmissibleExactValue:
            third_occurrence_rejected = True
        nonalternating_total_rejected = False
        try:
            MolecularElectronPairState(
                HeldLabel("molecular-carrier", "H2"),
                HeldLabel("molecular-electronic-state", "tampered"),
                PositiveCount(1),
                ALTERNATING_EXCHANGE,
                PRESERVING_EXCHANGE,
                PRESERVING_EXCHANGE,
                SAME_CELL_ADMITTED,
            )
        except InadmissibleExactValue:
            nonalternating_total_rejected = True
        same_fibre_product_rejected = (
            exchange_product(PRESERVING_EXCHANGE, PRESERVING_EXCHANGE) == PRESERVING_EXCHANGE
            and exchange_product(ALTERNATING_EXCHANGE, ALTERNATING_EXCHANGE) == PRESERVING_EXCHANGE
        )
        numeric_zero_rejected = False
        try:
            FoldWord((0,))
        except FoldLanguageHalt:
            numeric_zero_rejected = True
        first_snapshot = self.root / self.spec.target_rows[0].snapshot_path
        changed_hash = "sha256:" + sha256(first_snapshot.read_bytes() + b"tampered").hexdigest()
        counts = {
            "state_rows": len(state_comparisons),
            "singlet_states": sum(row["positive_spin_multiplicity"] == 1 for row in state_comparisons),
            "triplet_states": sum(row["positive_spin_multiplicity"] == 3 for row in state_comparisons),
            "explicit_same_cell_singlets": sum(
                row["same_cell_record"] == "same-cell-pair-recorded"
                and row["positive_spin_multiplicity"] == 1
                for row in state_comparisons
            ),
            "same_configuration_exchange_pairs": len(pair_comparisons),
            "triplet_below_singlet": sum(
                row["held_energy_order"] == "triplet-below-singlet" for row in pair_comparisons
            ),
            "singlet_below_triplet": sum(
                row["held_energy_order"] == "singlet-below-triplet" for row in pair_comparisons
            ),
            "source_ground_absence_glyphs": sum(
                bool(row["source_ground_glyph_is_absence_baseline"]) for row in state_comparisons
            ),
        }
        adverse = {
            "invalid_two-electron_multiplicity_rejected": invalid_multiplicity_rejected,
            "same_cell_triplet_rejected": same_cell_triplet_rejected,
            "third_same_support_occurrence_rejected": third_occurrence_rejected,
            "nonalternating_total_rejected": nonalternating_total_rejected,
            "same_fibre_product_retained_as_preserving_not_fermionic_total": same_fibre_product_rejected,
            "source_absence_glyph_as_numerical_value_rejected": numeric_zero_rejected,
            "omitted_state_rejected": len(state_comparisons[:-1]) != 46,
            "omitted_exchange_pair_rejected": len(pair_comparisons[:-1]) != 14,
            "selected_favourable_energy_order_rejected": counts["singlet_below_triplet"] == 1,
            "changed_measured_separation_rejected": all(
                PositiveRatio.from_pair(
                    int(row["positive_energy_separation_numerator"]),
                    int(row["positive_energy_separation_denominator"]),
                )
                != PositiveRatio.from_pair(
                    int(row["positive_energy_separation_numerator"]) + 1,
                    int(row["positive_energy_separation_denominator"]),
                )
                for row in pair_comparisons
            ),
            "tampered_snapshot_rejected": hash_file(first_snapshot)
            == self.spec.target_rows[0].snapshot_hash
            and changed_hash != self.spec.target_rows[0].snapshot_hash,
            "complete_external_vector_retained": counts
            == {
                "state_rows": 46,
                "singlet_states": 25,
                "triplet_states": 21,
                "explicit_same_cell_singlets": 2,
                "same_configuration_exchange_pairs": 14,
                "triplet_below_singlet": 13,
                "singlet_below_triplet": 1,
                "source_ground_absence_glyphs": 1,
            },
        }
        passed = (
            all(bool(row["passed"]) for row in state_comparisons)
            and all(bool(row["passed"]) for row in pair_comparisons)
            and all(adverse.values())
        )
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=self.spec.experiment_id + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=sha256_identity(
                    ("complete-NIST-H2-pair-exchange-comparator/1", self.spec.experiment_id)
                ),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("ELEC-006 released target identity differs from custody")
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id=release.custodian_id,
                experiment_registration_hash=registration_hash,
                registered_target_identity_hash=target_identity,
                prediction_seal_hash=prediction_seal.seal_hash,
                target_release_manifest_hash=release.release_hash,
            )
        )
        payload = {
            "registration_hash": registration_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "counts": counts,
            "state_comparisons": state_comparisons,
            "pair_comparisons": pair_comparisons,
            "adverse": adverse,
            "trace_hash": execution.trace_hash,
        }
        state_measurements = tuple(
            f"{row['target_id']}: NIST {row['NIST_state_record']}; term {row['NIST_term_assignment']}; "
            f"positive spin multiplicity {row['positive_spin_multiplicity']}; spin exchange "
            f"{row['spin_exchange_class']}; spatial exchange {row['spatial_exchange_class']}; total "
            f"{row['total_exchange_class']}; same-cell observation {row['same_cell_record']}; "
            f"configuration {row['configuration']}; energy inscription {row['energy_inscription']}; "
            f"source glyph 0 is absence baseline {row['source_ground_glyph_is_absence_baseline']}; "
            f"pass {row['passed']}"
            for row in state_comparisons
        )
        pair_measurements = tuple(
            f"{row['target_id']}: support {row['configuration']}; singlet {row['singlet_state']} at "
            f"{row['singlet_energy_inscription']}; triplet {row['triplet_state']} at "
            f"{row['triplet_energy_inscription']}; positive measured separation "
            f"{row['positive_energy_separation_numerator']}/{row['positive_energy_separation_denominator']} "
            f"inverse-centimetre; held order {row['held_energy_order']}; pass {row['passed']}"
            for row in pair_comparisons
        )
        measurements = (
            state_measurements
            + pair_measurements
            + tuple(f"complete count {key}: {value}" for key, value in counts.items())
            + tuple(f"adverse {key}: {value}" for key, value in adverse.items())
        )
        return EmpiricalValidation(
            sealed.seal_hash,
            registration_hash,
            isolation,
            custody,
            True,
            True,
            True,
            (SOURCE_ID,),
            measurements,
            sha256_identity(payload),
            self.spec.falsification_condition,
            passed,
        )


__all__ = ("PairExchangeValidator", "experiment_registration_record", "prediction_program_document")
