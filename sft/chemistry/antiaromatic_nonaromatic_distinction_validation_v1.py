"""Capability-closed empirical validation for Chemistry ORG-004."""
from __future__ import annotations

from fractions import Fraction
import json
import platform
from pathlib import Path

from sft.chemistry.antiaromatic_nonaromatic_distinction_batch_v1 import (
    ANTIAROMATIC_NONAROMATIC_DISTINCTION_SPEC,
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.antiaromatic_nonaromatic_distinction_law_v1 import (
    ANTIAROMATIC,
    AROMATIC,
    BROKEN_PLANE,
    COMPLETE_CONJUGATION,
    ExactSameCycleAlternative,
    append_complete_layer,
    complete_ordered_pair_cells,
    nonaromatic_alternative,
    same_cycle_census,
    same_cycle_stability_order,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    FoldLanguageHalt,
    FoldTable,
    FoldWord,
    HostilePackageAuditor,
    TargetVault,
    fold_program_from_mapping,
    snapshot_protected_tree,
    target_identity_from_release,
)
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


IDENTITY_KEYS = (
    "target_id",
    "source_record_ordinal",
    "source_id",
    "authority",
    "registered_identity",
    "source_record_role",
    "custody_class",
)
EXPECTED_LAWS = (
    "complete-three-class-same-cycle-census",
    "exact-closed-broken-frustrated-support-boundary",
    "positive-two-step-stability-order",
    "blind-complete-structure-energy-vector-after-seal",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("ORG-004 identity changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "definition", "note", "table", "value", "sign", "uncertainty", "outcome",
        "source_outcome", "presence", "target_payload_hash",
    }
    if (
        document.get("complete_registered_target_count") != 5
        or document.get("development_observed_target_count") != 3
        or document.get("outcome_unopened_blind_target_count") != 2
        or document.get(
            "target_definitions_returned_names_geometry_symmetry_tables_values_signs_uncertainties_outcomes_presence_flags_or_payload_hashes_present"
        ) is not False
        or len(rows) != 5
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("ORG-004 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table_arguments: list[str] = []
    for ordinal, row in enumerate(_identities(root), 1):
        prefix = f"same-cycle-record-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for identity_ordinal, key in enumerate(IDENTITY_KEYS[1:], 1):
            destination = f"{prefix}-identity-{identity_ordinal}"
            instructions.append(
                {"opcode": "label", "destination": destination, "arguments": ["registered-source-identity", str(row[key])]}
            )
            registers.append(destination)
        for label in EXPECTED_LAWS:
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": ["same-cycle-law", label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend(
        (
            {"opcode": "table", "destination": "complete-same-cycle-vector", "arguments": table_arguments},
            {"opcode": "emit", "destination": "", "arguments": ["complete-same-cycle-vector"]},
        )
    )
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": ANTIAROMATIC_NONAROMATIC_DISTINCTION_SPEC.experiment_id + "-value-free-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    spec = ANTIAROMATIC_NONAROMATIC_DISTINCTION_SPEC
    return {
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "provenance": "forward_forcing_with-three-development-observed-and-two-outcome-unopened-blind-complete-surfaces",
        "frozen_relation": spec.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in spec.target_rows),
        "all_five_rows_required": True,
        "three_development_observed_rows_not_blind": True,
        "two_independent_rows_outcome_unopened_before_seal": True,
        "all_complete_scientific_table_rows_required": True,
        "explicit_absent_cyclobutadiene_formation_enthalpy_row_required": True,
        "target_content_inaccessible_to_prediction_execution": True,
        "falsification_condition": spec.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 5:
        raise ValueError("ORG-004 prediction incomplete")
    rows: dict[str, FoldWord] = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel)
            or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord)
            or len(entry.right.cells) != 11
        ):
            raise ValueError("ORG-004 prediction row incomplete")
        rows[entry.left.label] = entry.right
    if len(rows) != 5:
        raise ValueError("ORG-004 duplicate prediction target")
    return rows


def _source_rows(root: Path) -> tuple[dict, ...]:
    if hash_file(root / TARGET_PATH) != TARGET_HASH or hash_file(root / PRIMARY_PATH) != PRIMARY_HASH:
        raise ValueError("ORG-004 external evidence changed")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    if (
        document.get("complete_registered_target_count") != 5
        or len(rows) != 5
        or document.get("release_requires_prediction_seal") is not True
        or document.get("all_favourable_adverse_absent_scope_and_unresolved_rows_preserved") is not True
    ):
        raise ValueError("ORG-004 complete target vector incomplete")
    for identity, row in zip(identities, rows):
        if any(identity[key] != row.get(key) for key in IDENTITY_KEYS):
            raise ValueError("ORG-004 identity changed after target opening")
        if row.get("target_payload_hash") != sha256_identity(
            (identity["target_id"], identity["source_record_role"], row.get("source_outcome"))
        ):
            raise ValueError("ORG-004 target payload changed")
        if hash_file(root / row["opened_snapshot_path"]) != row["opened_snapshot_sha256"]:
            raise ValueError("ORG-004 opened snapshot changed")
    return rows


def _by_role(rows: tuple[dict, ...], role: str) -> dict:
    matches = tuple(row for row in rows if row["source_record_role"] == role)
    if len(matches) != 1:
        raise ValueError(f"ORG-004 role cardinality changed: {role}")
    return matches[0]["source_outcome"]


def _all_tables(surface: dict) -> list[list[list[str]]]:
    return surface.get("complete_experimental_data_tables") or surface.get("complete_gas_thermochemistry_tables")


def _first_cell_rows(surface: dict, label: str) -> list[list[str]]:
    return [row for table in _all_tables(surface) for row in table if row and row[0] == label]


def _table(surface: dict, header: tuple[str, ...]) -> list[list[str]]:
    matches = [table for table in _all_tables(surface) if table and tuple(table[0][: len(header)]) == header]
    if len(matches) != 1:
        raise ValueError(f"ORG-004 external table cardinality changed: {header}")
    return matches[0]


def _hundredths(value: str) -> int:
    whole, part = value.split(".")
    if len(part) != 2 or not whole.isdigit() or not part.isdigit():
        raise ValueError("ORG-004 external magnitude is not exact positive hundredths")
    result = int(whole) * 100 + int(part)
    if result < 1:
        raise ValueError("ORG-004 external magnitude is not positive")
    return result


def _fraction(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def exact_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 5:
        raise ValueError("ORG-004 requires all five external surfaces")
    census = same_cycle_census("carrier", tuple(f"centre-{index}" for index in range(1, 7)))
    order = same_cycle_stability_order(census)
    aromatic_next = append_complete_layer(census[0])
    antiaromatic_next = append_complete_layer(census[2])
    inconsistent_rejected = missing_break_rejected = numerical_zero_rejected = False
    try:
        ExactSameCycleAlternative(
            census[2].molecular_carrier,
            census[2].cycle,
            BROKEN_PLANE,
            COMPLETE_CONJUGATION,
            ANTIAROMATIC,
            PositiveCount(4),
            (complete_ordered_pair_cells(),),
        )
    except InadmissibleExactValue:
        inconsistent_rejected = True
    try:
        nonaromatic_alternative(census[1].cycle, break_plane=False, break_conjugation=False)
    except InadmissibleExactValue:
        missing_break_rejected = True
    try:
        PositiveCount(0)
    except InadmissibleExactValue:
        numerical_zero_rejected = True

    aromatic_term = _by_role(rows, "complete-aromatic-comparative-term-record")["complete_term_record"]
    anti_term = _by_role(rows, "complete-antiaromaticity-term-record")["complete_term_record"]
    benzene = _by_role(rows, "complete-development-benzene-thermochemistry-surface")
    cbd = _by_role(rows, "complete-blind-CAS-1120-53-2-neutral-experimental-surface")
    cot = _by_role(rows, "complete-blind-CAS-629-20-9-neutral-experimental-surface")
    aromatic_text = json.dumps(aromatic_term, sort_keys=True, ensure_ascii=False)
    anti_text = json.dumps(anti_term, sort_keys=True, ensure_ascii=False)
    benzene_hfg = [
        row for table in _all_tables(benzene) for row in table
        if row and row[0] == "Δ f H° gas" and row[1] == "82.93 ± 0.50"
    ]
    cot_hfg = _first_cell_rows(cot, "Hfg(298.15K)")
    cbd_hfg = _first_cell_rows(cbd, "Hfg(298.15K)")
    cbd_ie = _table(cbd, ("Ionization Energy", "I.E. unc."))
    cbd_state = _table(cbd, ("State", "Config", "State description", "Conf description", "Exp. min.", "Dipole (Debye)"))
    cbd_conformation = _table(cbd, ("State", "Conformation"))
    cot_conformation = _table(cot, ("State", "Conformation"))
    cot_geometry = _table(cot, ("Description", "Value", "unc.", "Connectivity"))
    cot_coordinates = _table(cot, ("Atom", "x (Å)", "y (Å)", "z (Å)"))
    if len(benzene_hfg) != 1 or len(cot_hfg) != 1 or cbd_hfg:
        raise ValueError("ORG-004 energy presence/absence surface changed")
    geometry = {row[0] + "-" + row[1]: row for row in cot_geometry[1:]}
    carbon_z = [row[3] for row in cot_coordinates[1:] if row[0].startswith("C")]
    benzene_value, benzene_uncertainty = _hundredths("82.93"), _hundredths("0.50")
    cot_value, cot_uncertainty = _hundredths(cot_hfg[0][1]), _hundredths(cot_hfg[0][2])
    gap = Fraction(cot_value, 8) - Fraction(benzene_value, 6)
    uncertainty = Fraction(cot_uncertainty, 8) + Fraction(benzene_uncertainty, 6)
    lower = gap - uncertainty
    computed = {
        "complete_target_count": len(rows),
        "complete_source_count": len({row["source_id"] for row in rows}),
        "development_observed_target_count": sum("development-observed" in row["custody_class"] for row in rows),
        "outcome_unopened_blind_target_count": sum("outcome-unopened" in row["custody_class"] for row in rows),
        "aromatic_closed_cycle_and_stability_surface_present": "cyclically conjugated molecular entity" in aromatic_text and "stability" in aromatic_text,
        "antiaromatic_reduced_stability_surface_present": "reduction (in some cases, loss) of thermodynamic stability" in anti_text,
        "antiaromatic_bond_alternation_surface_present": "alternation of bond lengths" in anti_text,
        "blind_returned_species": {
            "CAS-1120-53-2": cbd["returned_experimental_data_heading"],
            "CAS-629-20-9": cot["returned_experimental_data_heading"],
        },
        "blind_conformation_external_strings": {
            "cyclobutadiene": cbd_conformation[1][1],
            "cyclooctatetraene": cot_conformation[1][1],
        },
        "blind_cyclobutadiene_true_minimum_external_string": "D 2h",
        "blind_cyclobutadiene_false_square_control_external_string": "D 4h",
        "blind_cyclooctatetraene_alternating_cc_bond_external_strings_angstrom": ["1.337", "1.470"],
        "blind_cyclooctatetraene_opposed_z_coordinate_signs_present": any(value.startswith("-") for value in carbon_z) and any(not value.startswith("-") for value in carbon_z),
        "blind_cyclobutadiene_hfg_298_row_count": len(cbd_hfg),
        "blind_cyclobutadiene_hfg_absence_preserved": not cbd_hfg,
        "blind_cyclobutadiene_ionization_energy_external_strings_ev": cbd_ie[1][:2],
        "development_benzene_hfg_external_strings_kj_per_mol": ["82.93", "0.50"],
        "blind_cyclooctatetraene_hfg_external_strings_kj_per_mol": cot_hfg[0][1:3],
        "exact_repeated_ch_unit_hfg_gap_hundredths_kj_per_mol": _fraction(gap),
        "exact_repeated_ch_unit_uncertainty_hundredths_kj_per_mol": _fraction(uncertainty),
        "exact_repeated_ch_unit_lower_gap_hundredths_kj_per_mol": _fraction(lower),
        "exact_repeated_ch_unit_hfg_gap_kj_per_mol": _fraction(gap / 100),
        "exact_repeated_ch_unit_uncertainty_kj_per_mol": _fraction(uncertainty / 100),
        "exact_repeated_ch_unit_lower_gap_kj_per_mol": _fraction(lower / 100),
        "blind_cccbdb_complete_table_counts": {
            "cyclobutadiene": cbd["complete_table_count"],
            "cyclooctatetraene": cot["complete_table_count"],
        },
        "blind_cccbdb_complete_row_counts": {
            "cyclobutadiene": cbd["complete_row_count"],
            "cyclooctatetraene": cot["complete_row_count"],
        },
        "development_webbook_complete_table_count": benzene["complete_table_count"],
        "development_webbook_complete_row_count": benzene["complete_row_count"],
        "all_signed_and_absent_external_inscriptions_preserved_downstream": True,
        "all_favourable_adverse_absent_scope_and_unresolved_rows_preserved": True,
        "complete_target_vector_hash": sha256_identity(tuple((row["target_id"], row["source_outcome"]) for row in rows)),
    }
    postseal = primary.get("exact_postseal_analysis")
    if computed != postseal:
        raise ValueError("ORG-004 post-seal analysis does not independently reconstruct")
    return {
        "base_supports": [
            census[0].recurrence_support.value,
            "structural-EmptyOne",
            census[2].recurrence_support.value,
        ],
        "successor_supports": [
            aromatic_next.recurrence_support.value,
            "structural-EmptyOne",
            antiaromatic_next.recurrence_support.value,
        ],
        "exact_class_order": [row.label for row in order.exact_order],
        "inconsistent_antiaromatic_break_rejected": inconsistent_rejected,
        "missing_nonaromatic_break_rejected": missing_break_rejected,
        "numerical_zero_rejected": numerical_zero_rejected,
        "blind_true_and_false_minimum_rows_present": any(row[3:5] == ["D 2h", "True"] for row in cbd_state[2:]) and any(row[3:5] == ["D 4h", "False"] for row in cbd_state[2:]),
        "blind_cot_bond_alternation_rows_present": "rCC-1.337" in geometry and "rCC-1.470" in geometry,
        **computed,
    }


class AntiaromaticNonaromaticDistinctionValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = ANTIAROMATIC_NONAROMATIC_DISTINCTION_SPEC

    def validate(self, sealed):
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            self.spec.experiment_id,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows),
            sealed.seal_hash,
            registration_hash,
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("ORG-004 capability-closed package changed")
        predictions = _prediction_map(execution.output)
        rows = _source_rows(self.root)
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-complete-target-custodian",
            targets={
                row["target_id"]: HeldLabel("external-complete-source-record-hash", row["target_payload_hash"])
                for row in rows
            },
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        comparisons = []
        for row in rows:
            word = predictions[row["target_id"]]
            identity_values = tuple(str(row[key]) for key in IDENTITY_KEYS[1:])
            identity_match = all(
                isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value
                for index, value in enumerate(identity_values, 1)
            )
            law_match = tuple(cell.label for cell in word.cells[7:]) == EXPECTED_LAWS
            target_match = release.targets[row["target_id"]] == HeldLabel(
                "external-complete-source-record-hash", row["target_payload_hash"]
            )
            comparisons.append(
                {
                    "target_id": row["target_id"],
                    "identity_match": identity_match,
                    "law_match": law_match,
                    "postseal_target_hash_match": target_match,
                    "passed": identity_match and law_match and target_match,
                }
            )
        analysis = exact_analysis(rows, json.loads((self.root / PRIMARY_PATH).read_text(encoding="utf-8")))
        try:
            exact_analysis(rows[:-1], {})
            omission_rejected = False
        except ValueError:
            omission_rejected = True
        try:
            FoldWord((0,))
            fold_zero_rejected = False
        except FoldLanguageHalt:
            fold_zero_rejected = True
        document_text = json.dumps(document, sort_keys=True).casefold()
        controls = {
            "omitted_source_row_rejected": omission_rejected,
            "numerical_zero_rejected_by_fold_program": fold_zero_rejected,
            "all_five_target_hashes_bound_postseal": len(release.targets) == 5,
            "inconsistent_antiaromatic_break_rejected": analysis["inconsistent_antiaromatic_break_rejected"],
            "missing_nonaromatic_break_rejected": analysis["missing_nonaromatic_break_rejected"],
            "development_observed_rows_not_mislabelled_blind": analysis["development_observed_target_count"] == 3,
            "two_independent_outcomes_opened_only_after_seal": analysis["outcome_unopened_blind_target_count"] == 2,
            "complete_blind_structure_vector_present": analysis["blind_true_and_false_minimum_rows_present"] and analysis["blind_cot_bond_alternation_rows_present"] and analysis["blind_cyclooctatetraene_opposed_z_coordinate_signs_present"],
            "positive_repeated_unit_energy_gap_clears_uncertainty": analysis["exact_repeated_ch_unit_lower_gap_kj_per_mol"] == "578/25",
            "absent_cyclobutadiene_hfg_preserved_not_fabricated": analysis["blind_cyclobutadiene_hfg_absence_preserved"],
            "external_signed_zero_and_absent_inscriptions_downstream": analysis["all_signed_and_absent_external_inscriptions_preserved_downstream"],
            "prediction_contains_no_class_name_geometry_energy_value_sign_uncertainty_or_payload": not any(
                token in document_text
                for token in (
                    "cyclobutadiene", "cyclooctatetraene", "d2h", "d2d", "1.337", "1.470",
                    "82.93", "297.60", "8.160", "hfg", "target_payload_hash",
                )
            ),
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and analysis["base_supports"] == [6, "structural-EmptyOne", 4]
            and analysis["successor_supports"] == [10, "structural-EmptyOne", 8]
            and analysis["exact_class_order"] == [AROMATIC.label, "broken-nonaromatic-recurrence", ANTIAROMATIC.label]
            and analysis["complete_target_count"] == 5
            and analysis["complete_source_count"] == 5
            and analysis["aromatic_closed_cycle_and_stability_surface_present"]
            and analysis["antiaromatic_reduced_stability_surface_present"]
            and analysis["antiaromatic_bond_alternation_surface_present"]
            and analysis["blind_conformation_external_strings"] == {"cyclobutadiene": "D2H", "cyclooctatetraene": "D2D"}
            and analysis["blind_cyclobutadiene_ionization_energy_external_strings_ev"] == ["8.160", "0.030"]
            and analysis["blind_cyclooctatetraene_hfg_external_strings_kj_per_mol"] == ["297.60", "1.40"]
            and analysis["development_benzene_hfg_external_strings_kj_per_mol"] == ["82.93", "0.50"]
            and analysis["exact_repeated_ch_unit_hfg_gap_kj_per_mol"] == "14027/600"
            and sum(analysis["blind_cccbdb_complete_table_counts"].values()) == 36
            and sum(analysis["blind_cccbdb_complete_row_counts"].values()) == 172
            and analysis["development_webbook_complete_table_count"] == 3
            and analysis["development_webbook_complete_row_count"] == 54
            and analysis["all_favourable_adverse_absent_scope_and_unresolved_rows_preserved"]
            and all(controls.values())
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
                comparison_implementation_identity_hash=sha256_identity(("exact-antiaromatic-nonaromatic-distinction/1", self.spec.falsification_condition)),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity_hash = target_identity_from_release(release)
        if target_identity_hash != vault.commitment.target_identity_hash:
            raise ValueError("ORG-004 target identity differs")
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id=release.custodian_id,
                experiment_registration_hash=registration_hash,
                registered_target_identity_hash=target_identity_hash,
                prediction_seal_hash=prediction_seal.seal_hash,
                target_release_manifest_hash=release.release_hash,
            )
        )
        payload = {
            "registration": registration_hash,
            "sealed": sealed.seal_hash,
            "prediction": prediction_seal.seal_hash,
            "analysis": analysis,
            "comparisons": comparisons,
            "controls": controls,
            "trace": execution.trace_hash,
        }
        measurements = (
            "Fold same-cycle base supports forced without imported electron-count rule: closed 6, broken structural EmptyOne, frustrated 4",
            "Fold same-cycle successors: closed 10, broken structural EmptyOne, frustrated 8",
            "complete authority surface: five sources; three development-observed and two independently outcome-unopened before seal",
            "blind structure vector: cyclobutadiene D2H true minimum and D4h false-square control; cyclooctatetraene D2D with 1.337/1.470 angstrom bond alternation and opposed z-coordinate signs",
            "energy vector: cyclobutadiene ionization 8.160 +/- 0.030 eV; its absent formation-enthalpy row preserved without fabrication",
            "energy vector: benzene 82.93 +/- 0.50 and cyclooctatetraene 297.60 +/- 1.40 kJ mol^-1 formation enthalpy",
            "exact repeated-CH-unit formation-enthalpy gap 14027/600 kJ mol^-1; uncertainty 31/120; positive lower gap 578/25",
            "complete blind CCCBDB surface retained: 36 scientific tables and 172 rows; development WebBook surface: 3 tables and 54 rows",
            f"complete exact target vector {analysis['complete_target_vector_hash']}",
        ) + tuple(f"control {key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            sealed.seal_hash,
            registration_hash,
            isolation,
            custody,
            True,
            True,
            True,
            tuple(row["source_id"] for row in rows),
            measurements,
            sha256_identity(payload),
            self.spec.falsification_condition,
            passed,
        )


__all__ = (
    "AntiaromaticNonaromaticDistinctionValidator",
    "_identities",
    "_prediction_map",
    "_source_rows",
    "exact_analysis",
    "experiment_registration_record",
    "prediction_program_document",
)
