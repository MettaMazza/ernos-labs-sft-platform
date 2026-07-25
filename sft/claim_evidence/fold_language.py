"""Capability-closed exact Fold language for official blind predictions.

The interpreter receives an immutable program and immutable registered values.
Its language contains no instruction for filesystem, network, subprocess,
clock, environment, dynamic import or foreign-function access.  Host indices
and mappings are execution mechanics only; admitted values remain generated
counts, exact positive ratios, held labels, words, pairs and finite tables.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Mapping

from sft.engine.canonical import sha256_identity
from sft.engine.exact import HeldLabel, PositiveCount


class FoldLanguageHalt(RuntimeError):
    """Fail-closed rejection of an invalid program, value or operation."""


@dataclass(frozen=True)
class EmptyOne:
    """Structural absence of a generated value, never numerical zero."""

    identity: str = "empty-One"


EMPTY_ONE = EmptyOne()


@dataclass(frozen=True)
class PositiveRatio:
    """Exact ratio witnessed by two positive generated counts."""

    numerator: PositiveCount
    denominator: PositiveCount

    @classmethod
    def from_pair(cls, numerator: int, denominator: int) -> "PositiveRatio":
        return cls(PositiveCount(numerator), PositiveCount(denominator))

    @property
    def fraction(self) -> Fraction:
        return Fraction(self.numerator.value, self.denominator.value)


@dataclass(frozen=True)
class FoldWord:
    cells: tuple[object, ...]

    def __post_init__(self) -> None:
        for cell in self.cells:
            validate_fold_value(cell)


@dataclass(frozen=True)
class FoldPair:
    left: object
    right: object

    def __post_init__(self) -> None:
        validate_fold_value(self.left)
        validate_fold_value(self.right)


@dataclass(frozen=True)
class FoldTable:
    entries: tuple[FoldPair, ...]

    def __post_init__(self) -> None:
        if not self.entries:
            raise FoldLanguageHalt("a Fold table requires generated positive support")
        identities = tuple(sha256_identity(entry.left) for entry in self.entries)
        if len(set(identities)) != len(identities):
            raise FoldLanguageHalt("a Fold table cannot contain duplicate keys")


FOLD_VALUE_TYPES = (EmptyOne, PositiveCount, PositiveRatio, HeldLabel, FoldWord, FoldPair, FoldTable)


def validate_fold_value(value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, FOLD_VALUE_TYPES):
        raise FoldLanguageHalt("value is outside the capability-closed exact Fold domain")


class FoldOpcode(str, Enum):
    INPUT = "input"
    EMPTY_ONE = "empty_one"
    LABEL = "label"
    COUNT = "count"
    RATIO = "ratio"
    WORD = "word"
    PAIR = "pair"
    TABLE = "table"
    LOOKUP = "lookup"
    JUNCTION = "junction"
    PRODUCT = "product"
    QUOTIENT = "quotient"
    SAME = "same"
    ASSERT_SAME = "assert_same"
    EMIT = "emit"


@dataclass(frozen=True)
class FoldInstruction:
    opcode: FoldOpcode
    destination: str
    arguments: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.opcode, FoldOpcode):
            raise FoldLanguageHalt("unregistered Fold opcode")
        if self.opcode not in {FoldOpcode.ASSERT_SAME, FoldOpcode.EMIT} and not self.destination.strip():
            raise FoldLanguageHalt("value-producing instruction requires a destination")
        if not self.arguments:
            raise FoldLanguageHalt("every instruction requires its exact argument trace")


@dataclass(frozen=True)
class FoldProgram:
    program_id: str
    instructions: tuple[FoldInstruction, ...]

    def __post_init__(self) -> None:
        if not self.program_id.strip() or not self.instructions:
            raise FoldLanguageHalt("a Fold program requires identity and positive instruction support")
        emits = tuple(item for item in self.instructions if item.opcode is FoldOpcode.EMIT)
        if len(emits) != 1 or self.instructions[-1].opcode is not FoldOpcode.EMIT:
            raise FoldLanguageHalt("a Fold program must terminate with exactly one emit instruction")


@dataclass(frozen=True)
class FoldTraceRow:
    position: PositiveCount
    opcode: FoldOpcode
    argument_hashes: tuple[str, ...]
    output_hash: str


@dataclass(frozen=True)
class FoldExecution:
    program_id: str
    program_hash: str
    input_manifest_hash: str
    output: object
    output_hash: str
    trace: tuple[FoldTraceRow, ...]
    trace_hash: str
    completed: bool


class CapabilityClosedFoldInterpreter:
    """Total straight-line interpreter with no ambient host capabilities."""

    interpreter_id = "sft-v3-capability-closed-fold-interpreter/1"

    def execute(self, program: FoldProgram, inputs: Mapping[str, object]) -> FoldExecution:
        if not inputs:
            raise FoldLanguageHalt("official prediction requires a registered positive input manifest")
        for name, value in inputs.items():
            if not isinstance(name, str) or not name.strip():
                raise FoldLanguageHalt("registered input identity is missing")
            validate_fold_value(value)

        registers: dict[str, object] = {}
        trace: list[FoldTraceRow] = []
        emitted: object = EMPTY_ONE
        for position, instruction in enumerate(program.instructions, start=1):
            output, argument_values = self._execute_instruction(instruction, inputs, registers)
            if instruction.opcode is FoldOpcode.EMIT:
                emitted = output
            elif instruction.opcode is not FoldOpcode.ASSERT_SAME:
                if instruction.destination in registers:
                    raise FoldLanguageHalt("a Fold register may be held exactly once")
                registers[instruction.destination] = output
            trace.append(
                FoldTraceRow(
                    position=PositiveCount(position),
                    opcode=instruction.opcode,
                    argument_hashes=tuple(sha256_identity(value) for value in argument_values),
                    output_hash=sha256_identity(output),
                )
            )

        validate_fold_value(emitted)
        trace_tuple = tuple(trace)
        return FoldExecution(
            program_id=program.program_id,
            program_hash=sha256_identity(program),
            input_manifest_hash=sha256_identity(tuple(sorted(inputs.items()))),
            output=emitted,
            output_hash=sha256_identity(emitted),
            trace=trace_tuple,
            trace_hash=sha256_identity(trace_tuple),
            completed=True,
        )

    def _execute_instruction(
        self,
        instruction: FoldInstruction,
        inputs: Mapping[str, object],
        registers: Mapping[str, object],
    ) -> tuple[object, tuple[object, ...]]:
        opcode = instruction.opcode
        args = instruction.arguments
        if opcode is FoldOpcode.INPUT:
            self._arity(opcode, args, 1)
            if args[0] not in inputs:
                raise FoldLanguageHalt("program requested an unregistered input")
            return inputs[args[0]], (inputs[args[0]],)
        if opcode is FoldOpcode.EMPTY_ONE:
            self._arity(opcode, args, 1)
            if args[0] != "structural-empty-One":
                raise FoldLanguageHalt("empty One requires its registered structural literal")
            return EMPTY_ONE, (EMPTY_ONE,)
        if opcode is FoldOpcode.LABEL:
            self._arity(opcode, args, 2)
            value = HeldLabel(args[0], args[1])
            return value, (value,)
        if opcode is FoldOpcode.COUNT:
            self._arity(opcode, args, 1)
            value = PositiveCount(self._positive_literal(args[0]))
            return value, (value,)
        if opcode is FoldOpcode.RATIO:
            self._arity(opcode, args, 2)
            value = PositiveRatio.from_pair(self._positive_literal(args[0]), self._positive_literal(args[1]))
            return value, (value.numerator, value.denominator)

        values = tuple(self._register(registers, name) for name in args)
        if opcode is FoldOpcode.WORD:
            return FoldWord(values), values
        if opcode is FoldOpcode.PAIR:
            self._arity(opcode, args, 2)
            return FoldPair(values[0], values[1]), values
        if opcode is FoldOpcode.TABLE:
            if len(values) < 2 or len(values) % 2:
                raise FoldLanguageHalt("table requires complete key/value pairs")
            return FoldTable(tuple(FoldPair(values[index], values[index + 1]) for index in range(0, len(values), 2))), values
        if opcode is FoldOpcode.LOOKUP:
            self._arity(opcode, args, 2)
            table, key = values
            if not isinstance(table, FoldTable):
                raise FoldLanguageHalt("lookup requires a generated Fold table")
            matches = tuple(entry.right for entry in table.entries if entry.left == key)
            if len(matches) != 1:
                raise FoldLanguageHalt("lookup must retain exactly one registered image")
            return matches[0], values
        if opcode in {FoldOpcode.JUNCTION, FoldOpcode.PRODUCT, FoldOpcode.QUOTIENT}:
            self._arity(opcode, args, 2)
            left, right = values
            if not isinstance(left, PositiveRatio) or not isinstance(right, PositiveRatio):
                raise FoldLanguageHalt("exact arithmetic requires two positive ratios")
            if opcode is FoldOpcode.JUNCTION:
                result = left.fraction + right.fraction
            elif opcode is FoldOpcode.PRODUCT:
                result = left.fraction * right.fraction
            else:
                result = left.fraction / right.fraction
            value = PositiveRatio.from_pair(result.numerator, result.denominator)
            return value, values
        if opcode is FoldOpcode.SAME:
            self._arity(opcode, args, 2)
            return HeldLabel("comparison", "same-form" if values[0] == values[1] else "different-form"), values
        if opcode is FoldOpcode.ASSERT_SAME:
            self._arity(opcode, args, 2)
            if values[0] != values[1]:
                raise FoldLanguageHalt("asserted Fold forms are not identical")
            return EMPTY_ONE, values
        if opcode is FoldOpcode.EMIT:
            self._arity(opcode, args, 1)
            return values[0], values
        raise FoldLanguageHalt("unregistered Fold opcode")

    @staticmethod
    def _register(registers: Mapping[str, object], name: str) -> object:
        if name not in registers:
            raise FoldLanguageHalt("instruction references an unheld register")
        return registers[name]

    @staticmethod
    def _positive_literal(value: str) -> int:
        if not value.isdecimal() or value.startswith("0"):
            raise FoldLanguageHalt("count literal must be a canonical positive generated count")
        parsed = int(value)
        if parsed < 1:
            raise FoldLanguageHalt("count literal must be positive")
        return parsed

    @staticmethod
    def _arity(opcode: FoldOpcode, arguments: tuple[str, ...], expected: int) -> None:
        if len(arguments) != expected:
            raise FoldLanguageHalt(f"{opcode.value} requires exactly {expected} argument(s)")


def fold_program_from_mapping(document: Mapping[str, object]) -> FoldProgram:
    """Load a data-only program without importing or executing contributor code."""

    if set(document) != {"schema", "program_id", "instructions"}:
        raise FoldLanguageHalt("Fold program document has missing or additional fields")
    if document["schema"] != "sft-v3-fold-program/1":
        raise FoldLanguageHalt("Fold program schema identity is not admitted")
    program_id = document["program_id"]
    rows = document["instructions"]
    if not isinstance(program_id, str) or not isinstance(rows, list) or not rows:
        raise FoldLanguageHalt("Fold program identity or instruction support is invalid")
    instructions: list[FoldInstruction] = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"opcode", "destination", "arguments"}:
            raise FoldLanguageHalt("Fold instruction has missing or additional fields")
        try:
            opcode = FoldOpcode(row["opcode"])
        except (TypeError, ValueError) as exc:
            raise FoldLanguageHalt("Fold instruction names an unregistered opcode") from exc
        destination = row["destination"]
        arguments = row["arguments"]
        if not isinstance(destination, str) or not isinstance(arguments, list) or any(not isinstance(item, str) for item in arguments):
            raise FoldLanguageHalt("Fold instruction fields have invalid host types")
        instructions.append(FoldInstruction(opcode, destination, tuple(arguments)))
    return FoldProgram(program_id, tuple(instructions))


def fold_value_from_mapping(document: Mapping[str, object]) -> object:
    """Load one exact tagged Fold value from a data-only document."""

    if not isinstance(document, dict) or "kind" not in document:
        raise FoldLanguageHalt("Fold value document lacks a kind")
    kind = document["kind"]
    expected: dict[str, set[str]] = {
        "empty_one": {"kind"},
        "count": {"kind", "value"},
        "ratio": {"kind", "numerator", "denominator"},
        "label": {"kind", "family", "label"},
        "word": {"kind", "cells"},
        "pair": {"kind", "left", "right"},
        "table": {"kind", "entries"},
    }
    if kind not in expected or set(document) != expected[kind]:
        raise FoldLanguageHalt("Fold value document has missing or additional fields")
    if kind == "empty_one":
        return EMPTY_ONE
    if kind == "count":
        return PositiveCount(_mapping_positive_count(document["value"]))
    if kind == "ratio":
        return PositiveRatio.from_pair(
            _mapping_positive_count(document["numerator"]),
            _mapping_positive_count(document["denominator"]),
        )
    if kind == "label":
        family, label = document["family"], document["label"]
        if not isinstance(family, str) or not isinstance(label, str):
            raise FoldLanguageHalt("held-label document contains invalid host types")
        return HeldLabel(family, label)
    if kind == "word":
        cells = document["cells"]
        if not isinstance(cells, list):
            raise FoldLanguageHalt("word cells must be a generated list")
        return FoldWord(tuple(fold_value_from_mapping(cell) for cell in cells))
    if kind == "pair":
        left, right = document["left"], document["right"]
        if not isinstance(left, dict) or not isinstance(right, dict):
            raise FoldLanguageHalt("pair cells must be exact Fold documents")
        return FoldPair(fold_value_from_mapping(left), fold_value_from_mapping(right))
    entries = document["entries"]
    if not isinstance(entries, list):
        raise FoldLanguageHalt("table entries must be generated support")
    pairs = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise FoldLanguageHalt("table entry is not an exact Fold pair")
        value = fold_value_from_mapping(entry)
        if not isinstance(value, FoldPair):
            raise FoldLanguageHalt("table entry is not an exact Fold pair")
        pairs.append(value)
    return FoldTable(tuple(pairs))


def _mapping_positive_count(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise FoldLanguageHalt("Fold value count must be a positive generated host count")
    return value
