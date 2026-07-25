"""Pure calculator interaction controller shared by every visual adapter."""

from __future__ import annotations

from dataclasses import dataclass

from sft.mathematics.calculator.values import CalculatorHalt, EMPTY_ONE, value_text

from .presentation import friendly
from .session import CalculatorSession


MAIN_BUTTON_ROWS = (
    ("MC", "MR", "M+", "M−", "MS", "CE", "C", "⌫"),
    ("sin", "cos", "tan", "7", "8", "9", "÷", "("),
    ("asin", "acos", "atan", "4", "5", "6", "×", ")"),
    ("sinh", "cosh", "tanh", "1", "2", "3", "−", "%"),
    ("asinh", "acosh", "atanh", "±", "0", ".", "+", "="),
    ("ln", "log", "log₂", "exp", "√", "cbrt", "x²", "xʸ"),
    ("π", "e", "φ", "n!", "nCr", "nPr", "1/x", "Ans"),
    ("floor", "ceil", "gcd", "lcm", "mod", "root", "|x|", "empty"),
)


FUNCTION_CATALOG = (
    ("sum", "sum(value, ...)", "exact aggregate sum"),
    ("prod", "prod(value, ...)", "exact aggregate product"),
    ("mean", "mean(value, ...)", "exact arithmetic mean"),
    ("variance", "variance(value, ...)", "population variance"),
    ("stddev", "stddev(value, ...)", "population standard deviation"),
    ("hypot", "hypot(left, right)", "certified hypotenuse"),
    ("pow", "pow(base, exponent)", "general exact or certified power"),
    ("complex", "complex(real, orthogonal)", "typed orthogonal Fold pair"),
    ("conj", "conj(value)", "orthogonal-fibre conjugate"),
    ("tau", "tau", "certified full turn"),
    ("log10", "log10(value)", "common logarithm"),
    ("recip", "recip(value)", "exact reciprocal"),
)


INSERTIONS = {
    "sin": "sin(", "cos": "cos(", "tan": "tan(",
    "asin": "asin(", "acos": "acos(", "atan": "atan(",
    "sinh": "sinh(", "cosh": "cosh(", "tanh": "tanh(",
    "asinh": "asinh(", "acosh": "acosh(", "atanh": "atanh(",
    "ln": "ln(", "log": "log(", "log₂": "log2(", "exp": "exp(",
    "√": "sqrt(", "cbrt": "cbrt(", "floor": "floor(", "ceil": "ceil(",
    "gcd": "gcd(", "lcm": "lcm(", "mod": "mod(", "root": "root(",
    "nCr": "ncr(", "nPr": "npr(", "1/x": "recip(", "|x|": "abs(",
    "π": "pi", "e": "e", "φ": "phi", "empty": "empty", "Ans": "ans",
    "x²": "^2", "xʸ": "^", "n!": "!", "%": "%",
    "(": "(", ")": ")", "÷": "/", "×": "*", "−": "-", "+": "+",
    "0": "0", "1": "1", "2": "2", "3": "3", "4": "4",
    "5": "5", "6": "6", "7": "7", "8": "8", "9": "9", ".": ".",
}


UNARY_IMMEDIATE = {
    "sin": "sin", "cos": "cos", "tan": "tan",
    "asin": "asin", "acos": "acos", "atan": "atan",
    "sinh": "sinh", "cosh": "cosh", "tanh": "tanh",
    "asinh": "asinh", "acosh": "acosh", "atanh": "atanh",
    "ln": "ln", "log": "log", "log₂": "log2", "exp": "exp",
    "√": "sqrt", "cbrt": "cbrt", "floor": "floor", "ceil": "ceil",
    "1/x": "recip", "|x|": "abs",
}

BINARY_PREFIX = {"nCr": "ncr", "nPr": "npr", "gcd": "gcd", "lcm": "lcm", "mod": "mod", "root": "root"}
OPERATORS = {"+", "−", "×", "÷", "xʸ"}
NEW_ENTRY_LABELS = set("0123456789.") | {"π", "e", "φ", "empty", "("}


@dataclass(frozen=True)
class CalculatorView:
    expression: str
    result: str
    exact_details: str
    error: str
    memory_active: bool
    angle_mode: str
    history: tuple[str, ...]


class CalculatorController:
    def __init__(self, *, places: int = 18, operation_limit: int = 10000):
        self.session = CalculatorSession(places=places, operation_limit=operation_limit)
        self.expression = ""
        self.result = "0"
        self.exact_details = "Enter an expression or press a calculator key."
        self.error = ""
        self.just_evaluated = False

    def view(self) -> CalculatorView:
        history = tuple(
            f"{item.expression.rstrip('=')}  =  {friendly(item.calculation.value, 10)}"
            for item in self.session.history
        )
        return CalculatorView(
            self.expression,
            self.result,
            self.exact_details,
            self.error,
            self.session.memory != EMPTY_ONE,
            self.session.angle_mode.upper(),
            history,
        )

    def set_expression(self, expression: str) -> CalculatorView:
        self.expression = expression
        self.just_evaluated = False
        self.error = ""
        return self.view()

    def set_angle_mode(self, mode: str) -> CalculatorView:
        self.session.set_angle_mode(mode.lower())
        return self.view()

    def insert(self, text: str, position: int | None = None) -> CalculatorView:
        if position is None:
            position = len(self.expression)
        if position < 0 or position > len(self.expression):
            raise CalculatorHalt("insertion point is outside the editable expression")
        self.expression = self.expression[:position] + text + self.expression[position:]
        self.just_evaluated = False
        self.error = ""
        return self.view()

    def evaluate(self) -> CalculatorView:
        expression = self.expression.strip()
        if not expression:
            return self.view()
        try:
            calculation = self.session.evaluate(expression)
        except (CalculatorHalt, ValueError) as error:
            self.result = "HALT"
            self.error = str(error)
            self.exact_details = "The expression was not admitted.\n\n" + str(error)
            self.just_evaluated = False
            return self.view()
        self.result = friendly(calculation.value)
        self.error = ""
        self.exact_details = (
            "Exact result\n"
            + value_text(calculation.value, self.session.places)
            + "\n\nProof trace\n"
            + "\n".join(calculation.trace)
            + f"\n\nResources\ntokens: {calculation.tokens_read}\noperations: {calculation.operations_executed}"
        )
        self.expression = ""
        self.just_evaluated = True
        return self.view()

    def _source(self) -> str:
        return self.expression.strip() or "ans"

    def _memory(self, action: str) -> None:
        if action == "MC":
            self.session.memory_clear()
        elif action == "MS":
            self.session.memory_store()
        elif action == "M+":
            self.session.memory_add()
        else:
            self.session.memory_subtract()

    def press(self, label: str) -> CalculatorView:
        if label == "=":
            return self.evaluate()
        if label == "CE":
            self.expression = ""
            self.error = ""
            self.just_evaluated = False
            return self.view()
        if label == "C":
            self.expression = ""
            self.result = "0"
            self.exact_details = "Calculator cleared; memory and history retained."
            self.error = ""
            self.just_evaluated = False
            self.session.all_clear()
            return self.view()
        if label == "⌫":
            self.expression = self.expression[:-1]
            self.just_evaluated = False
            self.error = ""
            return self.view()
        if label in {"MC", "MS", "M+", "M−"}:
            self._memory(label)
            return self.view()
        if label == "MR":
            return self.insert("mem")
        if label == "±":
            source = self._source()
            self.expression = source[2:-1] if source.startswith("-(") and source.endswith(")") else f"-({source})"
            self.just_evaluated = False
            return self.view()
        if label in UNARY_IMMEDIATE:
            self.expression = f"{UNARY_IMMEDIATE[label]}({self._source()})"
            return self.evaluate()
        if label in BINARY_PREFIX:
            self.expression = f"{BINARY_PREFIX[label]}({self._source()},"
            self.just_evaluated = False
            return self.view()
        if label == "x²":
            self.expression = f"({self._source()})^2"
            return self.evaluate()
        if label == "n!":
            self.expression = f"({self._source()})!"
            return self.evaluate()
        if label in OPERATORS:
            operator = INSERTIONS[label]
            if not self.expression.strip():
                self.expression = "ans" + operator
            else:
                self.expression += operator
            self.just_evaluated = False
            return self.view()
        if label not in INSERTIONS:
            raise CalculatorHalt(f"unknown calculator control {label!r}")
        if self.just_evaluated and label in NEW_ENTRY_LABELS:
            self.expression = ""
        return self.insert(INSERTIONS[label])

    def insert_catalog(self, name: str) -> CalculatorView:
        catalog = {item[0]: item[1] for item in FUNCTION_CATALOG}
        if name not in catalog:
            raise CalculatorHalt(f"unknown function catalog entry {name!r}")
        template = catalog[name]
        insertion = template if name == "tau" else template.split("(", 1)[0] + "("
        return self.insert(insertion)

    def restore_history(self, index: int) -> CalculatorView:
        if index < 0 or index >= len(self.session.history):
            raise CalculatorHalt("history selection is outside the retained record")
        self.expression = self.session.history[index].expression.rstrip("=")
        self.just_evaluated = False
        return self.view()

    def clear_history(self) -> CalculatorView:
        self.session.clear_history()
        return self.view()


__all__ = (
    "BINARY_PREFIX",
    "CalculatorController",
    "CalculatorView",
    "FUNCTION_CATALOG",
    "INSERTIONS",
    "MAIN_BUTTON_ROWS",
    "OPERATORS",
    "UNARY_IMMEDIATE",
)
