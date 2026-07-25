"""Lexer, parser and traced execution machine for the SFT calculator."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .operations import (
    absolute,
    add,
    circle_constant_enclosure,
    combination,
    conjugate,
    cos_enclosure,
    divide,
    exp_enclosure,
    factorial,
    ln_enclosure,
    log10_enclosure,
    multiply,
    negate,
    nth_root,
    permutation,
    reciprocal,
    require_whole,
    sin_enclosure,
    subtract,
    tan_enclosure,
    whole_power,
)
from .values import (
    CertifiedInterval,
    ComplexFibre,
    EMPTY_ONE,
    CalculatorHalt,
    Value,
    forward,
    parse_exact_number,
    value_text,
)


TOKEN = re.compile(
    r"\s*(?:(?P<number>(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)|"
    r"(?P<name>[A-Za-z_][A-Za-z_0-9]*)|(?P<operator>[+\-*/^!%(),]))"
)


@dataclass(frozen=True)
class Calculation:
    expression: str
    value: Value
    trace: tuple[str, ...]
    tokens_read: int
    operations_executed: int

    def render(self, places: int = 18) -> str:
        return value_text(self.value, places)


@dataclass(frozen=True)
class _Token:
    kind: str
    text: str


class Calculator:
    """One deterministic, exact and fully traced calculator execution."""

    def __init__(self, *, places: int = 18, operation_limit: int = 10000):
        if places < 1 or places > 60:
            raise CalculatorHalt("display precision must be a counted value from 1 through 60")
        if operation_limit < 1:
            raise CalculatorHalt("operation limit must be a positive count")
        self.places = places
        self.operation_limit = operation_limit
        self._tokens: tuple[_Token, ...] = ()
        self._position = 0
        self._trace: list[str] = []
        self._operations = 0

    def calculate(self, expression: str) -> Calculation:
        self._tokens = self._lex(expression)
        self._position = 0
        self._trace = ["boundary:decimal-notation-translated-to-exact-Fold-forms"]
        self._operations = 0
        value = self._expression()
        if self._position != len(self._tokens):
            raise CalculatorHalt(f"unexpected token {self._tokens[self._position].text!r}")
        self._trace.append("halt:complete-generated-expression-consumed")
        return Calculation(expression, value, tuple(self._trace), len(self._tokens), self._operations)

    def _lex(self, expression: str) -> tuple[_Token, ...]:
        if not expression.strip():
            raise CalculatorHalt("an expression is required")
        tokens: list[_Token] = []
        position = 0
        while position < len(expression):
            match = TOKEN.match(expression, position)
            if match is None:
                if expression[position:].strip() == "":
                    break
                raise CalculatorHalt(f"ungenerated character at boundary position {position}")
            kind = "number" if match.group("number") else "name" if match.group("name") else "operator"
            tokens.append(_Token(kind, match.group(kind)))
            position = match.end()
        return tuple(tokens)

    def _peek(self, text: str | None = None) -> bool:
        if self._position >= len(self._tokens):
            return False
        return text is None or self._tokens[self._position].text == text

    def _take(self, text: str | None = None) -> _Token:
        if not self._peek(text):
            expected = text if text is not None else "a generated token"
            raise CalculatorHalt(f"expected {expected}")
        token = self._tokens[self._position]
        self._position += 1
        return token

    def _record(self, operation: str, value: Value) -> Value:
        self._operations += 1
        if self._operations > self.operation_limit:
            raise CalculatorHalt("declared operation bound exhausted")
        self._trace.append(f"{self._operations}:{operation}:{value_text(value, min(self.places, 12))}")
        return value

    def _expression(self) -> Value:
        value = self._term()
        while self._peek("+") or self._peek("-"):
            operator = self._take().text
            right = self._term()
            value = self._record("held-junction" if operator == "+" else "held-substitution", add(value, right) if operator == "+" else subtract(value, right))
        return value

    def _term(self) -> Value:
        value = self._unary()
        while self._peek("*") or self._peek("/"):
            operator = self._take().text
            right = self._unary()
            value = self._record("pair-cell-product" if operator == "*" else "common-refinement-quotient", multiply(value, right) if operator == "*" else divide(value, right))
        return value

    def _unary(self) -> Value:
        if self._peek("+"):
            self._take("+")
            return self._unary()
        if self._peek("-"):
            self._take("-")
            return self._record("held-orientation-reversal", negate(self._unary()))
        return self._power()

    def _power(self) -> Value:
        value = self._postfix()
        if self._peek("^"):
            self._take("^")
            exponent = self._unary()
            value = self._record("counted-whole-power", whole_power(value, exponent))
        return value

    def _postfix(self) -> Value:
        value = self._primary()
        while self._peek("!") or self._peek("%"):
            operator = self._take().text
            if operator == "!":
                value = self._record("generated-factorial-recurrence", factorial(value))
            else:
                value = self._record("exact-hundredth-part", divide(value, forward(100)))
        return value

    def _primary(self) -> Value:
        if self._peek("("):
            self._take("(")
            value = self._expression()
            self._take(")")
            return value
        token = self._take()
        if token.kind == "number":
            value = parse_exact_number(token.text)
            self._trace.append(f"input:{token.text}->{value_text(value, min(self.places, 12))}")
            return value
        if token.kind != "name":
            raise CalculatorHalt(f"unexpected token {token.text!r}")
        name = token.text.lower()
        if not self._peek("("):
            if name == "pi":
                return self._record("certified-circle-constant", circle_constant_enclosure())
            if name == "e":
                return self._record("certified-exp-One", exp_enclosure(forward(1), self.places))
            if name in {"empty", "empty_one"}:
                return EMPTY_ONE
            raise CalculatorHalt(f"unknown generated name {token.text!r}")
        self._take("(")
        arguments: list[Value] = []
        if not self._peek(")"):
            arguments.append(self._expression())
            while self._peek(","):
                self._take(",")
                arguments.append(self._expression())
        self._take(")")
        return self._call(name, tuple(arguments))

    def _arity(self, name: str, arguments: tuple[Value, ...], expected: int) -> None:
        if len(arguments) != expected:
            raise CalculatorHalt(f"{name} requires exactly {expected} generated argument(s)")

    def _call(self, name: str, arguments: tuple[Value, ...]) -> Value:
        if name in {"abs", "recip", "sqrt", "exp", "ln", "log10", "sin", "cos", "tan", "conj"}:
            self._arity(name, arguments, 1)
            source = arguments[0]
            functions = {
                "abs": absolute,
                "recip": reciprocal,
                "sqrt": lambda item: nth_root(item, 2),
                "exp": lambda item: exp_enclosure(item, self.places),
                "ln": lambda item: ln_enclosure(item, self.places),
                "log10": lambda item: log10_enclosure(item, self.places),
                "sin": lambda item: sin_enclosure(item, self.places),
                "cos": lambda item: cos_enclosure(item, self.places),
                "tan": lambda item: tan_enclosure(item, self.places),
                "conj": conjugate,
            }
            return self._record(f"generated-function:{name}", functions[name](source))
        if name in {"root", "pow", "ncr", "npr", "complex", "log"}:
            self._arity(name, arguments, 2)
            left, right = arguments
            if name == "root":
                result = nth_root(left, require_whole(right, allow_empty=False))
            elif name == "pow":
                result = whole_power(left, right)
            elif name == "ncr":
                result = combination(left, right)
            elif name == "npr":
                result = permutation(left, right)
            elif name == "complex":
                from .operations import require_scalar
                result = ComplexFibre(require_scalar(left), require_scalar(right))
            else:
                result = divide(ln_enclosure(left, self.places + 4), ln_enclosure(right, self.places + 4))
            return self._record(f"generated-function:{name}", result)
        raise CalculatorHalt(f"unknown generated function {name!r}")


def calculate(expression: str, *, places: int = 18) -> Calculation:
    return Calculator(places=places).calculate(expression)
