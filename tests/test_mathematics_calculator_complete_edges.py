"""Branch-completion and graphical-adapter tests for calculator claim 006."""

from __future__ import annotations

import builtins
from contextlib import redirect_stderr, redirect_stdout
from fractions import Fraction
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

from sft.mathematics.calculator.values import (
    CertifiedInterval,
    ComplexFibre,
    EMPTY_ONE,
    CalculatorHalt,
    FoldScalar,
    counter,
    forward,
)
from sft.mathematics.calculator_complete import __main__ as cli
from sft.mathematics.calculator_complete.controller import CalculatorController
from sft.mathematics.calculator_complete.evidence import (
    calculation_evidence_json,
    validate_value,
    value_form,
)
from sft.mathematics.calculator_complete import expression_census
from sft.mathematics.calculator_complete.explorer import RegisteredMathematicsExplorer
from sft.mathematics.calculator_complete.gui import SFTCalculatorApp, launch_gui
from sft.mathematics.calculator_complete.machine import calculate
from sft.mathematics.calculator_complete.operations import periodic_reduce, tan_value
from sft.mathematics.calculator_complete.presentation import friendly
from sft.mathematics.calculator_complete.session import CalculatorSession


ROOT = Path(__file__).resolve().parents[1]


class FakeTclError(Exception):
    pass


class FakeVariable:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class FakeWidget:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.options = dict(kwargs)
        self.children = []
        self.items = []
        self.selection = ()
        self.visible = True
        self.selected_tab = None
        self.textvariable = kwargs.get("textvariable")

    def pack(self, *args, **kwargs):
        self.options.update(kwargs)

    def grid(self, *args, **kwargs):
        self.visible = True
        self.options.update(kwargs)

    def grid_remove(self):
        self.visible = False

    def columnconfigure(self, *args, **kwargs):
        pass

    def rowconfigure(self, *args, **kwargs):
        pass

    def bind(self, *args, **kwargs):
        self.options["binding"] = args

    def configure(self, *args, **kwargs):
        if args:
            self.options["configure_args"] = args
        self.options.update(kwargs)

    config = configure

    def focus_set(self):
        self.options["focused"] = True

    def icursor(self, position):
        self.options["cursor"] = position

    def yview(self, *args):
        return args

    def set(self, *args):
        self.options["set"] = args

    def insert(self, index, value):
        if isinstance(value, str) and (index == "end" or isinstance(index, int)):
            self.items.append(value)

    def delete(self, start, end=None):
        self.items.clear()

    def get(self, start=None, end=None):
        if start == 0 and end == "end":
            return tuple(self.items)
        return self.textvariable.get() if self.textvariable else ""

    def curselection(self):
        return self.selection

    def add(self, frame, text=""):
        self.children.append((frame, text))

    def select(self, tab):
        self.selected_tab = tab

    def theme_names(self):
        return ("clam",)

    def theme_use(self, theme):
        self.options["theme"] = theme


class FakeRoot(FakeWidget):
    def __init__(self, fail_scaling=False):
        super().__init__()
        self.fail_scaling = fail_scaling
        self.tk = self
        self.geometries = []
        self.clipboard = ""
        self.mainloop_called = False

    def call(self, *args):
        if self.fail_scaling:
            raise FakeTclError("no scaling")
        return args

    def title(self, value):
        self.options["title"] = value

    def geometry(self, value):
        self.geometries.append(value)

    def minsize(self, *value):
        self.options["minsize"] = value

    def clipboard_clear(self):
        self.clipboard = ""

    def clipboard_append(self, value):
        self.clipboard = value

    def mainloop(self):
        self.mainloop_called = True


def fake_tk_module(root: FakeRoot):
    module = types.ModuleType("tkinter")
    module.StringVar = FakeVariable
    module.TclError = FakeTclError
    module.Text = FakeWidget
    module.Listbox = FakeWidget
    module.Tk = lambda: root
    ttk = types.SimpleNamespace(
        Style=FakeWidget,
        Frame=FakeWidget,
        Label=FakeWidget,
        Button=FakeWidget,
        Combobox=FakeWidget,
        Entry=FakeWidget,
        Notebook=FakeWidget,
        Scrollbar=FakeWidget,
    )
    module.ttk = ttk
    return module


class CompleteBranchTests(unittest.TestCase):
    def test_controller_boundary_and_remaining_state_paths(self) -> None:
        controller = CalculatorController()
        self.assertEqual(controller.evaluate().result, "0")
        controller.insert("12")
        controller.insert("x", 1)
        self.assertEqual(controller.view().expression, "1x2")
        with self.assertRaises(CalculatorHalt):
            controller.insert("x", -1)
        controller.set_expression("2")
        controller.press("+")
        self.assertEqual(controller.view().expression, "2+")
        controller.set_expression("2")
        controller.evaluate()
        controller.press("7")
        self.assertEqual(controller.view().expression, "7")
        controller.set_expression("")
        self.assertEqual(controller.press("±").expression, "-(ans)")
        with self.assertRaises(CalculatorHalt):
            controller.press("not-a-key")
        controller.insert_catalog("tau")
        self.assertTrue(controller.view().expression.endswith("tau"))
        with self.assertRaises(CalculatorHalt):
            controller.insert_catalog("unknown")
        with self.assertRaises(CalculatorHalt):
            controller.restore_history(99)

    def test_session_invalid_modes_and_all_memory_variants(self) -> None:
        with self.assertRaises(CalculatorHalt):
            CalculatorSession(angle_mode="turns")
        session = CalculatorSession()
        with self.assertRaises(CalculatorHalt):
            session.set_angle_mode("turns")
        session.evaluate("2")
        self.assertEqual(session.memory_store(forward(3)), forward(3))
        self.assertEqual(session.memory_add(forward(2)), forward(5))
        self.assertEqual(session.memory_subtract(forward(1)), forward(4))
        session.all_clear()
        self.assertIs(session.answer, EMPTY_ONE)

    def test_presentation_every_form(self) -> None:
        self.assertEqual(friendly(EMPTY_ONE), "0")
        self.assertEqual(friendly(forward(2)), "2")
        self.assertEqual(friendly(counter(2)), "−2")
        self.assertEqual(friendly(forward(Fraction(1, 3)), 6), "0.333333")
        self.assertTrue(friendly(calculate("sqrt(2)").value).startswith("≈ "))
        self.assertIn("fibre", friendly(calculate("complex(2,3)").value))

    def test_evidence_rejects_unknown_runtime_forms_and_missing_census(self) -> None:
        with self.assertRaises(TypeError):
            validate_value(object())  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            value_form(object())  # type: ignore[arg-type]
        with tempfile.TemporaryDirectory() as directory:
            payload = json.loads(calculation_evidence_json(calculate("1+1"), Path(directory)))
        self.assertIsNone(payload["official_calculator_receipt_hash"])

    def test_explorer_missing_files_unknown_claim_and_fallback_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            explorer = RegisteredMathematicsExplorer(Path(directory))
            summary = explorer.summary("SFT-MATH-EXACT-ARITHMETIC-001")
            self.assertFalse(summary.model_admitted)
            chain = explorer.dependency_chain("SFT-MATH-EXACT-ARITHMETIC-001")
            self.assertEqual(chain[-1], "SFT-MATH-EXACT-ARITHMETIC-001")
            self.assertEqual(len(explorer.summaries()), 25)
            with self.assertRaises(KeyError):
                explorer.summary("missing")

    def test_expression_census_halts_on_unknown_or_duplicate_registration(self) -> None:
        unknown = types.SimpleNamespace(claim_id="SFT-MATH-UNKNOWN")
        with patch.object(expression_census, "SPECS", (unknown,)):
            with self.assertRaises(RuntimeError):
                expression_census.expression_families()
        known = types.SimpleNamespace(claim_id="SFT-MATH-EXACT-ARITHMETIC-001")
        with patch.object(expression_census, "SPECS", (known, known)):
            with self.assertRaises(RuntimeError):
                expression_census.expression_families()

    def test_operation_internal_adverse_paths(self) -> None:
        with self.assertRaises(CalculatorHalt):
            periodic_reduce(ComplexFibre(forward(1), forward(1)))
        negative = periodic_reduce(counter(1000000), 12)
        self.assertLess(float(negative.lower.magnitude), 4)
        exact = CertifiedInterval(forward(1), forward(1), ("exact",))
        with patch(
            "sft.mathematics.calculator_complete.operations.circle_constant_enclosure",
            return_value=CertifiedInterval(forward(1), forward(2), ("deliberately-wide",)),
        ):
            with self.assertRaises(CalculatorHalt):
                periodic_reduce(forward(10**20), 18)
        with patch("sft.mathematics.calculator_complete.operations.subtract", return_value=forward(1)):
            with self.assertRaises(CalculatorHalt):
                periodic_reduce(forward(1))
        with patch("sft.mathematics.calculator_complete.operations.divide", return_value=forward(1)):
            with self.assertRaises(CalculatorHalt):
                tan_value(forward(1))

    def test_machine_aggregate_count_bound(self) -> None:
        with self.assertRaises(CalculatorHalt):
            calculate("sum(1,1,1)", operation_limit=2)


class HeadlessGraphicalAdapterTests(unittest.TestCase):
    def test_complete_gui_construction_and_all_actions(self) -> None:
        root = FakeRoot(fail_scaling=True)
        module = fake_tk_module(root)
        with patch.dict(sys.modules, {"tkinter": module}):
            app = SFTCalculatorApp(root)
        self.assertEqual(root.options["title"], "Smithian Fold Scientific Calculator")
        app.expression.set("1+1")
        app.evaluate()
        self.assertEqual(app.result.get(), "2")
        app.press("+")
        app.press("3")
        app.press("=")
        app.toggle_details()
        self.assertTrue(app.details_visible)
        app.toggle_details()
        self.assertFalse(app.details_visible)
        app.show_learn()
        self.assertEqual(app.details.selected_tab, 4)
        app.show_learn()
        app.mode.set("DEG")
        app.change_mode()
        app.insert_catalog("sum")
        app.history_list.selection = (0,)
        app.restore_history()
        app.history_list.selection = ()
        app.restore_history()
        app.clear_history()
        app.copy_result()
        self.assertEqual(root.clipboard, app.result.get())
        app.show_law()
        app.replay_law()

    def test_all_native_theme_selection_paths(self) -> None:
        for themes, expected in ((('vista',), 'vista'), (('aqua',), 'aqua'), ((), None)):
            root = FakeRoot()
            module = fake_tk_module(root)
            with patch.object(FakeWidget, "theme_names", return_value=themes), patch.dict(
                sys.modules, {"tkinter": module}
            ):
                app = SFTCalculatorApp(root)
            if expected is not None:
                self.assertEqual(app.ttk.Style(root).options.get("theme"), None)

    def test_launch_gui_success_and_missing_library(self) -> None:
        root = FakeRoot()
        module = fake_tk_module(root)
        with patch.dict(sys.modules, {"tkinter": module}):
            launch_gui()
        self.assertTrue(root.mainloop_called)

        real_import = builtins.__import__

        def missing_tk(name, *args, **kwargs):
            if name == "tkinter":
                raise ImportError("missing")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=missing_tk):
            with self.assertRaises(CalculatorHalt):
                launch_gui()


class DirectCliBranchTests(unittest.TestCase):
    def call_main(self, *arguments: str, inputs: tuple[str, ...] = ()):
        output, error = io.StringIO(), io.StringIO()
        with patch.object(sys, "argv", ["sft-calculator", *arguments]), patch(
            "builtins.input", side_effect=(*inputs, EOFError())
        ), redirect_stdout(output), redirect_stderr(error):
            code = cli.main()
        return code, output.getvalue(), error.getvalue()

    def test_main_gui_expression_law_replay_and_errors(self) -> None:
        with patch.object(cli, "launch_gui") as launched:
            code, _, _ = self.call_main("--gui")
            self.assertEqual(code, 0)
            launched.assert_called_once()
        code, output, _ = self.call_main("1+1=")
        self.assertEqual((code, output.strip()), (0, "2"))
        code, output, _ = self.call_main("sqrt(2)", "--proof")
        self.assertEqual(code, 0)
        self.assertIn('"constraint_checks"', output)
        code, output, _ = self.call_main("--law", "SFT-MATH-EXACT-ARITHMETIC-001")
        self.assertEqual(code, 0)
        self.assertIn("Exact arithmetic", output)
        code, output, _ = self.call_main("--replay-law", "SFT-MATH-EXACT-ARITHMETIC-001")
        self.assertEqual(code, 0)
        self.assertIn("calculator_law_replay", output)
        code, _, error = self.call_main("1/0")
        self.assertEqual(code, 2)
        self.assertIn("Cannot calculate", error)
        code, _, error = self.call_main("--law", "missing")
        self.assertEqual(code, 2)
        self.assertIn("unknown", error)

    def test_interactive_every_command_and_halt(self) -> None:
        inputs = (
            ":help", ":rad", ":deg", ":grad", ":mc", ":mr", ":ms", ":m+", ":m-",
            "1+1", ":history", ":clear", "1/0", "", ":quit",
        )
        code, output, error = self.call_main("--terminal", inputs=inputs)
        self.assertEqual(code, 0)
        self.assertIn("Angle mode", output)
        self.assertIn("Memory", output)
        self.assertIn("2", output)
        self.assertIn("Cannot calculate", error)
        code, output, _ = self.call_main("--terminal", inputs=())
        self.assertEqual(code, 0)
        self.assertIn("Smithian Fold", output)
        code, _, _ = self.call_main("--terminal", inputs=("exit",))
        self.assertEqual(code, 0)

    def test_module_execution_guard(self) -> None:
        output = io.StringIO()
        with patch.object(sys, "argv", ["sft-calculator", "1+1"]), redirect_stdout(output):
            with self.assertRaises(SystemExit) as stopped:
                runpy.run_module("sft.mathematics.calculator_complete.__main__", run_name="__main__")
        self.assertEqual(stopped.exception.code, 0)
        self.assertEqual(output.getvalue().strip(), "2")


if __name__ == "__main__":
    unittest.main()
