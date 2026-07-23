"""End-to-end and hostile controls for the official Fold prediction runtime."""

from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from sft.engine import (
    EMPTY_ONE,
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    CustodyHalt,
    EmptyOne,
    FoldInstruction,
    FoldLanguageHalt,
    FoldOpcode,
    FoldPair,
    FoldProgram,
    FoldTable,
    FoldWord,
    HostilePackageAuditor,
    HostilePackageHalt,
    PositiveRatio,
    TargetVault,
    fold_program_from_mapping,
    fold_value_from_mapping,
    snapshot_protected_tree,
    target_identity_from_release,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope, PredictionSeal
from sft.engine.exact import HeldLabel, PositiveCount


def instruction(opcode: FoldOpcode, destination: str, *arguments: str) -> FoldInstruction:
    return FoldInstruction(opcode, destination, arguments)


def complete_program() -> FoldProgram:
    return FoldProgram(
        "complete-runtime-witness",
        (
            instruction(FoldOpcode.INPUT, "source", "source"),
            instruction(FoldOpcode.EMPTY_ONE, "blank", "structural-empty-One"),
            instruction(FoldOpcode.LABEL, "left", "fibre", "left-held"),
            instruction(FoldOpcode.LABEL, "right", "fibre", "right-held"),
            instruction(FoldOpcode.COUNT, "two", "2"),
            instruction(FoldOpcode.RATIO, "half", "1", "2"),
            instruction(FoldOpcode.RATIO, "third", "1", "3"),
            instruction(FoldOpcode.WORD, "word", "source", "left", "blank"),
            instruction(FoldOpcode.PAIR, "pair", "left", "half"),
            instruction(FoldOpcode.TABLE, "table", "left", "half", "right", "third"),
            instruction(FoldOpcode.LOOKUP, "looked", "table", "left"),
            instruction(FoldOpcode.JUNCTION, "five-sixths", "half", "third"),
            instruction(FoldOpcode.PRODUCT, "one-sixth", "half", "third"),
            instruction(FoldOpcode.QUOTIENT, "three-halves", "half", "third"),
            instruction(FoldOpcode.SAME, "same", "looked", "half"),
            instruction(FoldOpcode.ASSERT_SAME, "", "looked", "half"),
            instruction(FoldOpcode.EMIT, "", "five-sixths"),
        ),
    )


class FoldLanguageTests(unittest.TestCase):
    def test_complete_instruction_surface_executes_exactly(self) -> None:
        execution = CapabilityClosedFoldInterpreter().execute(
            complete_program(),
            {"source": HeldLabel("input", "held")},
        )
        self.assertEqual(execution.output, PositiveRatio.from_pair(5, 6))
        self.assertEqual(len(execution.trace), len(complete_program().instructions))
        self.assertTrue(execution.completed)
        self.assertEqual(execution.trace_hash, sha256_identity(execution.trace))

    def test_exact_value_constructors_and_loader_cover_every_kind(self) -> None:
        values = (
            fold_value_from_mapping({"kind": "empty_one"}),
            fold_value_from_mapping({"kind": "count", "value": 2}),
            fold_value_from_mapping({"kind": "ratio", "numerator": 3, "denominator": 2}),
            fold_value_from_mapping({"kind": "label", "family": "f", "label": "l"}),
            fold_value_from_mapping({"kind": "word", "cells": [{"kind": "empty_one"}]}),
            fold_value_from_mapping({"kind": "pair", "left": {"kind": "count", "value": 1}, "right": {"kind": "empty_one"}}),
            fold_value_from_mapping({"kind": "table", "entries": [{"kind": "pair", "left": {"kind": "label", "family": "f", "label": "key"}, "right": {"kind": "count", "value": 1}}]}),
        )
        self.assertIsInstance(values[0], EmptyOne)
        self.assertIsInstance(values[4], FoldWord)
        self.assertIsInstance(values[5], FoldPair)
        self.assertIsInstance(values[6], FoldTable)
        self.assertEqual(PositiveRatio.from_pair(3, 2).fraction.numerator, 3)

    def test_data_only_program_loader(self) -> None:
        document = {
            "schema": "sft-v3-fold-program/1",
            "program_id": "loaded",
            "instructions": [
                {"opcode": "input", "destination": "held", "arguments": ["source"]},
                {"opcode": "emit", "destination": "", "arguments": ["held"]},
            ],
        }
        program = fold_program_from_mapping(document)
        result = CapabilityClosedFoldInterpreter().execute(program, {"source": PositiveCount(1)})
        self.assertEqual(result.output, PositiveCount(1))

    def test_program_and_instruction_forms_fail_closed(self) -> None:
        with self.assertRaises(FoldLanguageHalt):
            FoldProgram("", (instruction(FoldOpcode.EMIT, "", "held"),))
        with self.assertRaises(FoldLanguageHalt):
            FoldProgram("empty", ())
        with self.assertRaises(FoldLanguageHalt):
            FoldProgram("no-emit", (instruction(FoldOpcode.COUNT, "one", "1"),))
        with self.assertRaises(FoldLanguageHalt):
            FoldProgram("two-emits", (instruction(FoldOpcode.EMIT, "", "a"), instruction(FoldOpcode.EMIT, "", "a")))
        with self.assertRaises(FoldLanguageHalt):
            FoldInstruction("not-an-opcode", "held", ("a",))  # type: ignore[arg-type]
        with self.assertRaises(FoldLanguageHalt):
            instruction(FoldOpcode.COUNT, "", "1")
        with self.assertRaises(FoldLanguageHalt):
            FoldInstruction(FoldOpcode.COUNT, "held", ())

    def test_interpreter_rejects_invalid_inputs_and_registers(self) -> None:
        interpreter = CapabilityClosedFoldInterpreter()
        with self.assertRaises(FoldLanguageHalt):
            interpreter.execute(complete_program(), {})
        with self.assertRaises(FoldLanguageHalt):
            interpreter.execute(complete_program(), {"": PositiveCount(1)})
        with self.assertRaises(FoldLanguageHalt):
            interpreter.execute(complete_program(), {"source": 1})
        missing = FoldProgram("missing", (instruction(FoldOpcode.INPUT, "held", "absent"), instruction(FoldOpcode.EMIT, "", "held")))
        with self.assertRaises(FoldLanguageHalt):
            interpreter.execute(missing, {"source": PositiveCount(1)})
        duplicate = FoldProgram("duplicate", (instruction(FoldOpcode.INPUT, "held", "source"), instruction(FoldOpcode.COUNT, "held", "1"), instruction(FoldOpcode.EMIT, "", "held")))
        with self.assertRaises(FoldLanguageHalt):
            interpreter.execute(duplicate, {"source": PositiveCount(1)})
        unheld = FoldProgram("unheld", (instruction(FoldOpcode.WORD, "word", "absent"), instruction(FoldOpcode.EMIT, "", "word")))
        with self.assertRaises(FoldLanguageHalt):
            interpreter.execute(unheld, {"source": PositiveCount(1)})

    def test_each_invalid_operation_boundary_halts(self) -> None:
        interpreter = CapabilityClosedFoldInterpreter()
        source = {"source": PositiveCount(1)}
        programs = (
            FoldProgram("bad-empty", (instruction(FoldOpcode.EMPTY_ONE, "blank", "wrong"), instruction(FoldOpcode.EMIT, "", "blank"))),
            FoldProgram("bad-count", (instruction(FoldOpcode.COUNT, "count", "0"), instruction(FoldOpcode.EMIT, "", "count"))),
            FoldProgram("bad-table", (instruction(FoldOpcode.COUNT, "one", "1"), instruction(FoldOpcode.TABLE, "table", "one"), instruction(FoldOpcode.EMIT, "", "table"))),
            FoldProgram("bad-lookup-type", (instruction(FoldOpcode.COUNT, "one", "1"), instruction(FoldOpcode.LOOKUP, "value", "one", "one"), instruction(FoldOpcode.EMIT, "", "value"))),
            FoldProgram("bad-arithmetic", (instruction(FoldOpcode.LABEL, "label", "f", "l"), instruction(FoldOpcode.PRODUCT, "value", "label", "label"), instruction(FoldOpcode.EMIT, "", "value"))),
            FoldProgram("bad-assert", (instruction(FoldOpcode.LABEL, "left", "f", "l"), instruction(FoldOpcode.LABEL, "right", "f", "r"), instruction(FoldOpcode.ASSERT_SAME, "", "left", "right"), instruction(FoldOpcode.EMIT, "", "left"))),
        )
        for program in programs:
            with self.subTest(program=program.program_id), self.assertRaises((FoldLanguageHalt, ValueError)):
                interpreter.execute(program, source)
        for literal in ("01", "-1", "x", "٠"):
            program = FoldProgram("literal-" + literal, (instruction(FoldOpcode.COUNT, "value", literal), instruction(FoldOpcode.EMIT, "", "value")))
            with self.subTest(literal=literal), self.assertRaises((FoldLanguageHalt, ValueError)):
                interpreter.execute(program, source)

    def test_lookup_missing_duplicate_table_and_comparison_boundaries(self) -> None:
        with self.assertRaises(FoldLanguageHalt):
            FoldTable(())
        key = HeldLabel("f", "key")
        with self.assertRaises(FoldLanguageHalt):
            FoldTable((FoldPair(key, PositiveCount(1)), FoldPair(key, PositiveCount(2))))
        missing = FoldProgram(
            "lookup-missing",
            (
                instruction(FoldOpcode.LABEL, "key", "f", "key"),
                instruction(FoldOpcode.LABEL, "other", "f", "other"),
                instruction(FoldOpcode.COUNT, "one", "1"),
                instruction(FoldOpcode.TABLE, "table", "key", "one"),
                instruction(FoldOpcode.LOOKUP, "value", "table", "other"),
                instruction(FoldOpcode.EMIT, "", "value"),
            ),
        )
        with self.assertRaises(FoldLanguageHalt):
            CapabilityClosedFoldInterpreter().execute(missing, {"source": PositiveCount(1)})
        different = FoldProgram(
            "different",
            (
                instruction(FoldOpcode.LABEL, "left", "f", "left"),
                instruction(FoldOpcode.LABEL, "right", "f", "right"),
                instruction(FoldOpcode.SAME, "verdict", "left", "right"),
                instruction(FoldOpcode.EMIT, "", "verdict"),
            ),
        )
        result = CapabilityClosedFoldInterpreter().execute(different, {"source": PositiveCount(1)})
        self.assertEqual(result.output, HeldLabel("comparison", "different-form"))

    def test_loader_rejects_every_malformed_surface(self) -> None:
        valid = {
            "schema": "sft-v3-fold-program/1",
            "program_id": "loaded",
            "instructions": [{"opcode": "emit", "destination": "", "arguments": ["held"]}],
        }
        cases = (
            {"schema": "sft-v3-fold-program/1"},
            {**valid, "schema": "wrong"},
            {**valid, "program_id": 1},
            {**valid, "instructions": "not-list"},
            {**valid, "instructions": []},
            {**valid, "instructions": ["not-row"]},
            {**valid, "instructions": [{"opcode": "network", "destination": "x", "arguments": ["x"]}]},
            {**valid, "instructions": [{"opcode": "emit", "destination": 1, "arguments": ["x"]}]},
            {**valid, "instructions": [{"opcode": "emit", "destination": "", "arguments": [1]}]},
        )
        for case in cases:
            with self.subTest(case=case), self.assertRaises(FoldLanguageHalt):
                fold_program_from_mapping(case)
        bad_values = (
            {},
            {"kind": "unknown"},
            {"kind": "count", "value": True},
            {"kind": "count", "value": "1"},
            {"kind": "count", "value": 0},
            {"kind": "label", "family": 1, "label": "x"},
            {"kind": "word", "cells": "x"},
            {"kind": "word", "cells": ["x"]},
            {"kind": "pair", "left": "x", "right": {}},
            {"kind": "table", "entries": "x"},
            {"kind": "table", "entries": ["x"]},
            {"kind": "table", "entries": [{"kind": "empty_one"}]},
        )
        for case in bad_values:
            with self.subTest(value=case), self.assertRaises((FoldLanguageHalt, ValueError)):
                fold_value_from_mapping(case)

    def test_unregistered_internal_opcode_and_wrong_arity_halt(self) -> None:
        interpreter = CapabilityClosedFoldInterpreter()
        malformed = object.__new__(FoldInstruction)
        object.__setattr__(malformed, "opcode", "network")
        object.__setattr__(malformed, "destination", "x")
        object.__setattr__(malformed, "arguments", ("x",))
        with self.assertRaises(FoldLanguageHalt):
            interpreter._execute_instruction(malformed, {}, {"x": PositiveCount(1)})  # type: ignore[arg-type]
        with self.assertRaises(FoldLanguageHalt):
            interpreter._execute_instruction(instruction(FoldOpcode.PAIR, "p", "x"), {}, {"x": PositiveCount(1)})


class CustodyAndHostileAuditTests(unittest.TestCase):
    def make_boundary_and_vault(self):
        envelope = PredictionEnvelope(
            "experiment-one",
            {"input": "held"},
            ("target-one",),
            sha256_identity("relation"),
            sha256_identity("registration"),
        )
        envelope_hash = sha256_identity(envelope)
        vault = TargetVault(
            experiment_id="experiment-one",
            custodian_id="distinct-custodian",
            targets={"target-one": "measured-record"},
            custody_nonce="custodian-held-nonce",
            expected_envelope_hash=envelope_hash,
        )
        boundary = BlindExperimentBoundary(envelope)
        return boundary, vault

    def test_target_commitment_release_and_verification(self) -> None:
        boundary, vault = self.make_boundary_and_vault()
        seal = boundary.seal_prediction({"prediction": "held"}, {"trace": "complete"})
        release = vault.release(seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, seal)
        self.assertEqual(tuple(release.targets), ("target-one",))
        self.assertEqual(target_identity_from_release(release), vault.commitment.target_identity_hash)
        with self.assertRaises(CustodyHalt):
            target_identity_from_release(replace(release, target_identity_hash="invalid"))
        with self.assertRaises(CustodyHalt):
            vault.release(seal)

    def test_vault_and_release_fail_every_cross_binding_boundary(self) -> None:
        identity = sha256_identity("envelope")
        invalid_constructors = (
            {"experiment_id": "", "custodian_id": "c", "targets": {"t": "v"}, "custody_nonce": "n", "expected_envelope_hash": identity},
            {"experiment_id": "e", "custodian_id": "", "targets": {"t": "v"}, "custody_nonce": "n", "expected_envelope_hash": identity},
            {"experiment_id": "e", "custodian_id": "c", "targets": {}, "custody_nonce": "n", "expected_envelope_hash": identity},
            {"experiment_id": "e", "custodian_id": "c", "targets": {"": "v"}, "custody_nonce": "n", "expected_envelope_hash": identity},
            {"experiment_id": "e", "custodian_id": "c", "targets": {"t": "v"}, "custody_nonce": "n", "expected_envelope_hash": "bad"},
        )
        for values in invalid_constructors:
            with self.subTest(values=values), self.assertRaises(CustodyHalt):
                TargetVault(**values)
        boundary, vault = self.make_boundary_and_vault()
        good = boundary.seal_prediction("prediction", "trace")
        with self.assertRaises(CustodyHalt):
            TargetVault(
                experiment_id="experiment-one", custodian_id="c", targets={"target-one": "v"},
                custody_nonce="n", expected_envelope_hash=sha256_identity("different")
            ).release(good)
        wrong_experiment = replace(good, experiment_id="wrong")
        with self.assertRaises(CustodyHalt):
            vault.release(wrong_experiment)

    def test_release_verifier_detects_every_tampered_class(self) -> None:
        boundary, vault = self.make_boundary_and_vault()
        seal = boundary.seal_prediction("prediction", "trace")
        release = vault.release(seal)
        cases = (
            replace(release, experiment_id="wrong"),
            replace(release, custodian_id="wrong"),
            replace(release, prediction_seal_hash=sha256_identity("wrong")),
            replace(release, targets={"wrong": "value"}),
            replace(release, targets={"target-one": "changed"}),
            replace(release, release_hash=sha256_identity("wrong")),
        )
        for changed in cases:
            with self.subTest(changed=changed), self.assertRaises(CustodyHalt):
                CrossPlatformCustodyExchange.verify(vault.commitment, changed, seal)
        wrong_envelope = replace(seal, envelope_hash=sha256_identity("wrong"))
        with self.assertRaises(CustodyHalt):
            CrossPlatformCustodyExchange.verify(vault.commitment, release, wrong_envelope)

    def make_protected_root(self, root: Path) -> None:
        (root / "census").mkdir(parents=True)
        (root / "receipts/engine/model_admitted").mkdir(parents=True)
        (root / "census/claims.json").write_text("{}", encoding="utf-8")
        (root / "receipts/engine/model_admitted/receipt.json").write_text("{}", encoding="utf-8")

    def test_data_only_hostile_audit_and_protected_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_protected_root(root)
            before = snapshot_protected_tree(root)
            document = {
                "schema": "sft-v3-fold-program/1",
                "program_id": "audited",
                "instructions": [
                    {"opcode": "input", "destination": "held", "arguments": ["source"]},
                    {"opcode": "emit", "destination": "", "arguments": ["held"]},
                ],
            }
            program, certificate = HostilePackageAuditor().audit_program_document(document, before, snapshot_protected_tree(root))
            self.assertEqual(program.program_id, "audited")
            self.assertTrue(certificate.passed)
            self.assertEqual(certificate.certificate_hash, sha256_identity({
                "auditor_id": certificate.auditor_id,
                "package_hash": certificate.package_hash,
                "program_hash": certificate.program_hash,
                "executable_source_present": False,
                "additional_fields_present": False,
                "protected_tree_unchanged": True,
                "passed": True,
            }))

    def test_hostile_package_and_mutation_are_rejected(self) -> None:
        auditor = HostilePackageAuditor()
        with self.assertRaises(HostilePackageHalt):
            auditor.reject_executable_prediction_source("open('target')")
        with self.assertRaises(HostilePackageHalt):
            auditor.reject_executable_prediction_source("")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_protected_root(root)
            before = snapshot_protected_tree(root)
            (root / "census/claims.json").write_text('{"tampered":true}', encoding="utf-8")
            document = {
                "schema": "sft-v3-fold-program/1",
                "program_id": "audited",
                "instructions": [{"opcode": "emit", "destination": "", "arguments": ["held"]}],
            }
            with self.assertRaises(HostilePackageHalt):
                auditor.audit_program_document(document, before, snapshot_protected_tree(root))
            with self.assertRaises(HostilePackageHalt):
                auditor.audit_program_document({**document, "python": "malicious"}, before, before)
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(HostilePackageHalt):
                snapshot_protected_tree(Path(temporary))


if __name__ == "__main__":
    unittest.main()
