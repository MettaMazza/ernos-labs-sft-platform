"""Clean cross-platform desktop app for the SFT scientific calculator."""

from __future__ import annotations

from fractions import Fraction

from .session import CalculatorSession
from .values import (
    CertifiedInterval,
    ComplexFibre,
    CalculatorHalt,
    EmptyOne,
    FoldScalar,
    Value,
    decimal_projection,
    exact_text,
    scalar_from_projection,
    scalar_to_fraction_for_projection,
    value_text,
)


BUTTON_ROWS = (
    ("MC", "MR", "M+", "M−", "MS", "C", "⌫"),
    ("sin", "cos", "tan", "asin", "acos", "atan"),
    ("sinh", "cosh", "tanh", "ln", "log", "log₂"),
    ("exp", "10ˣ", "cbrt", "floor", "ceil", "mod"),
    ("π", "e", "φ", "x²", "xʸ", "√"),
    ("n!", "nCr", "nPr", "1/x", "|x|", "%"),
    ("(", ")", "7", "8", "9", "÷"),
    ("gcd", "lcm", "4", "5", "6", "×"),
    ("mean", "σ", "1", "2", "3", "−"),
    ("Ans", "±", "0", ".", "=", "+"),
)


INSERTIONS = {
    "sin": "sin(", "cos": "cos(", "tan": "tan(",
    "asin": "asin(", "acos": "acos(", "atan": "atan(",
    "sinh": "sinh(", "cosh": "cosh(", "tanh": "tanh(",
    "ln": "ln(", "log": "log(", "log₂": "log2(",
    "exp": "exp(", "10ˣ": "10^(", "cbrt": "cbrt(", "floor": "floor(", "ceil": "ceil(", "mod": "mod(",
    "π": "pi", "e": "e", "φ": "phi", "x²": "^2", "xʸ": "^", "√": "sqrt(",
    "n!": "!", "nCr": "ncr(", "nPr": "npr(", "1/x": "recip(", "|x|": "abs(", "%": "%",
    "(": "(", ")": ")", "÷": "/", "×": "*", "−": "-", "+": "+",
    "gcd": "gcd(", "lcm": "lcm(", "mean": "mean(", "σ": "stddev(",
    "Ans": "ans", "0": "0", "1": "1", "2": "2", "3": "3", "4": "4",
    "5": "5", "6": "6", "7": "7", "8": "8", "9": "9", ".": ".",
}


GUIDE_TEXT = """How this calculator follows Smithian Fold Theory

Use it like a normal scientific calculator. Type an expression or press the buttons, then press = or Enter.

Examples
  1 + 1 =
  0.1 + 0.2 =
  sqrt(2)
  2^(1/3)
  sin(30) in DEG mode
  log(8, 2)
  mean(1, 2, 3, 4)

SFT value translation
• A displayed 0 is the structural empty-One form, not a numerical proof value.
• A minus sign is stored as a held orientation plus a positive magnitude.
• Entered decimals become exact fractions before calculation.
• Non-rational roots, π, e and transcendental functions return exact rational lower/upper certificates. The large decimal is a readable projection, not the proof.
• Conventional complex values are typed real and orthogonal Fold fibres; no imaginary proof scalar is introduced.
• Invalid domains, division by empty-One and any result that cannot be certified within the declared resource limit halt explicitly.

Memory
MS stores the current answer. MR inserts mem. M+ and M− update memory. MC clears it. Ans inserts the previous answer.

Evidence
The Trace tab shows every exact operation and its counted resources. Exact details exposes the retained fraction or enclosure rather than hiding it behind a decimal.
"""


def _friendly(value: Value, places: int = 16) -> str:
    if isinstance(value, CertifiedInterval):
        lower = scalar_to_fraction_for_projection(value.lower)
        upper = scalar_to_fraction_for_projection(value.upper)
        midpoint = scalar_from_projection((lower + upper) / 2)
        return "≈ " + decimal_projection(midpoint, places)
    if isinstance(value, ComplexFibre):
        return value_text(value, places)
    if isinstance(value, EmptyOne):
        return "0"
    if value.magnitude.denominator == 1:
        return ("" if value.is_forward else "−") + str(value.magnitude.numerator)
    return decimal_projection(value, places)


class SFTCalculatorApp:
    def __init__(self, root, *, places: int = 18):
        import tkinter as tk
        from tkinter import ttk

        self.tk = tk
        self.ttk = ttk
        self.root = root
        self.session = CalculatorSession(places=places)
        self.expression = tk.StringVar()
        self.result = tk.StringVar(value="0")
        self.mode = tk.StringVar(value="RAD")
        self.memory_indicator = tk.StringVar(value="")

        root.title("Smithian Fold Scientific Calculator")
        root.geometry("1040x720")
        root.minsize(860, 620)
        root.configure(background="#f3f3f3")
        try:
            root.tk.call("tk", "scaling", 1.15)
        except tk.TclError:
            pass

        style = ttk.Style(root)
        available = style.theme_names()
        if "vista" in available:
            style.theme_use("vista")
        elif "aqua" in available:
            style.theme_use("aqua")
        elif "clam" in available:
            style.theme_use("clam")
        style.configure("Display.TEntry", font=("Segoe UI", 17), padding=10)
        style.configure("Result.TLabel", font=("Segoe UI Semibold", 25), anchor="e")
        style.configure("Calc.TButton", font=("Segoe UI", 11), padding=(7, 12))
        style.configure("Equals.TButton", font=("Segoe UI Semibold", 12), padding=(7, 12))
        style.configure("Title.TLabel", font=("Segoe UI Semibold", 15))

        outer = ttk.Frame(root, padding=14)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=3)
        outer.columnconfigure(1, weight=2)
        outer.rowconfigure(0, weight=1)

        calculator = ttk.Frame(outer, padding=(0, 0, 12, 0))
        calculator.grid(row=0, column=0, sticky="nsew")
        for column in range(max(len(row) for row in BUTTON_ROWS)):
            calculator.columnconfigure(column, weight=1)

        header = ttk.Frame(calculator)
        header.grid(row=0, column=0, columnspan=7, sticky="ew", pady=(0, 8))
        ttk.Label(header, text="Scientific", style="Title.TLabel").pack(side="left")
        ttk.Label(header, textvariable=self.memory_indicator).pack(side="left", padx=12)
        mode_box = ttk.Combobox(header, textvariable=self.mode, values=("RAD", "DEG", "GRAD"), state="readonly", width=6)
        mode_box.pack(side="right")
        mode_box.bind("<<ComboboxSelected>>", self._change_mode)

        self.entry = ttk.Entry(calculator, textvariable=self.expression, justify="right", style="Display.TEntry")
        self.entry.grid(row=1, column=0, columnspan=7, sticky="ew", pady=(0, 4))
        self.entry.bind("<Return>", lambda _event: self.evaluate())
        self.entry.bind("<KP_Enter>", lambda _event: self.evaluate())
        self.entry.bind("<Escape>", lambda _event: self.clear())

        result_frame = ttk.Frame(calculator)
        result_frame.grid(row=2, column=0, columnspan=7, sticky="ew", pady=(0, 10))
        result_frame.columnconfigure(0, weight=1)
        ttk.Label(result_frame, textvariable=self.result, style="Result.TLabel").grid(row=0, column=0, sticky="ew")
        ttk.Button(result_frame, text="Copy", command=self.copy_result).grid(row=0, column=1, padx=(8, 0))

        for row_index, row in enumerate(BUTTON_ROWS, start=3):
            calculator.rowconfigure(row_index, weight=1)
            for column, label in enumerate(row):
                command = lambda item=label: self.press(item)
                style_name = "Equals.TButton" if label == "=" else "Calc.TButton"
                ttk.Button(calculator, text=label, command=command, style=style_name).grid(
                    row=row_index, column=column, sticky="nsew", padx=2, pady=2
                )

        sidebar = ttk.Notebook(outer)
        sidebar.grid(row=0, column=1, sticky="nsew")
        history_tab = ttk.Frame(sidebar, padding=10)
        trace_tab = ttk.Frame(sidebar, padding=10)
        learn_tab = ttk.Frame(sidebar, padding=10)
        sidebar.add(history_tab, text="History")
        sidebar.add(trace_tab, text="Exact details")
        sidebar.add(learn_tab, text="Learn")

        history_tab.rowconfigure(0, weight=1)
        history_tab.columnconfigure(0, weight=1)
        self.history_list = tk.Listbox(history_tab, font=("Segoe UI", 11), activestyle="none")
        self.history_list.grid(row=0, column=0, sticky="nsew")
        self.history_list.bind("<Double-Button-1>", self.restore_history)
        ttk.Button(history_tab, text="Clear history", command=self.clear_history).grid(row=1, column=0, sticky="ew", pady=(8, 0))

        trace_tab.rowconfigure(0, weight=1)
        trace_tab.columnconfigure(0, weight=1)
        self.trace_text = tk.Text(trace_tab, wrap="word", font=("Consolas", 10), relief="flat", background="#ffffff")
        self.trace_text.grid(row=0, column=0, sticky="nsew")
        self.trace_text.configure(state="disabled")

        learn_tab.rowconfigure(0, weight=1)
        learn_tab.columnconfigure(0, weight=1)
        guide = tk.Text(learn_tab, wrap="word", font=("Segoe UI", 10), relief="flat", background="#ffffff")
        guide.grid(row=0, column=0, sticky="nsew")
        guide.insert("1.0", GUIDE_TEXT)
        guide.configure(state="disabled")

        self.entry.focus_set()

    def _change_mode(self, _event=None) -> None:
        self.session.set_angle_mode(self.mode.get().lower())

    def _insert(self, text: str) -> None:
        try:
            start = self.entry.index("sel.first")
            end = self.entry.index("sel.last")
            current = self.expression.get()
            self.expression.set(current[:start] + text + current[end:])
            self.entry.icursor(start + len(text))
        except self.tk.TclError:
            position = self.entry.index("insert")
            current = self.expression.get()
            self.expression.set(current[:position] + text + current[position:])
            self.entry.icursor(position + len(text))
        self.entry.focus_set()

    def press(self, label: str) -> None:
        if label == "=":
            self.evaluate()
        elif label == "C":
            self.clear()
        elif label == "⌫":
            position = self.entry.index("insert")
            if position:
                current = self.expression.get()
                self.expression.set(current[: position - 1] + current[position:])
                self.entry.icursor(position - 1)
        elif label == "±":
            current = self.expression.get().strip()
            self.expression.set(f"-({current})" if current else "-")
            self.entry.icursor("end")
        elif label == "MC":
            self.session.memory_clear()
            self.memory_indicator.set("")
        elif label == "MR":
            self._insert("mem")
        elif label == "MS":
            self.session.memory_store()
            self.memory_indicator.set("M")
        elif label == "M+":
            self.session.memory_add()
            self.memory_indicator.set("M")
        elif label == "M−":
            self.session.memory_subtract()
            self.memory_indicator.set("M")
        elif label in {"sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh", "ln", "log₂", "exp", "cbrt", "floor", "ceil", "√", "1/x", "|x|"} and self.expression.get().strip():
            function = {
                "log₂": "log2", "√": "sqrt", "1/x": "recip", "|x|": "abs",
            }.get(label, label)
            self.expression.set(f"{function}({self.expression.get()})")
            self.entry.icursor("end")
            self.entry.focus_set()
        elif label in {"nCr", "nPr", "gcd", "lcm", "mod"} and self.expression.get().strip():
            function = {"nCr": "ncr", "nPr": "npr"}.get(label, label)
            self.expression.set(f"{function}({self.expression.get()},")
            self.entry.icursor("end")
            self.entry.focus_set()
        else:
            self._insert(INSERTIONS[label])

    def evaluate(self) -> None:
        expression = self.expression.get().strip()
        if not expression:
            return
        try:
            calculation = self.session.evaluate(expression)
        except (CalculatorHalt, ValueError) as error:
            self.result.set("HALT")
            self._set_trace("The expression was not admitted.\n\n" + str(error))
            return
        self.result.set(_friendly(calculation.value))
        self.history_list.insert("end", f"{calculation.expression.rstrip('=')}  =  {_friendly(calculation.value, 10)}")
        self.history_list.see("end")
        exact = value_text(calculation.value, self.session.places)
        trace = "Exact result\n" + exact + "\n\nProof trace\n" + "\n".join(calculation.trace)
        trace += f"\n\nResources\ntokens: {calculation.tokens_read}\noperations: {calculation.operations_executed}"
        self._set_trace(trace)
        self.expression.set("")

    def _set_trace(self, content: str) -> None:
        self.trace_text.configure(state="normal")
        self.trace_text.delete("1.0", "end")
        self.trace_text.insert("1.0", content)
        self.trace_text.configure(state="disabled")

    def clear(self) -> None:
        self.expression.set("")
        self.result.set("0")
        self.entry.focus_set()

    def clear_history(self) -> None:
        self.session.clear_history()
        self.history_list.delete(0, "end")

    def restore_history(self, _event=None) -> None:
        selection = self.history_list.curselection()
        if not selection:
            return
        entry = self.session.history[selection[0]]
        self.expression.set(entry.expression.rstrip("="))
        self.entry.icursor("end")
        self.entry.focus_set()

    def copy_result(self) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(self.result.get())


def launch_gui(*, places: int = 18) -> None:
    try:
        import tkinter as tk
    except ImportError as error:
        raise CalculatorHalt(
            "this Python installation does not include the standard Tk graphical library; the terminal calculator remains available"
        ) from error
    root = tk.Tk()
    SFTCalculatorApp(root, places=places)
    root.mainloop()


__all__ = ("BUTTON_ROWS", "GUIDE_TEXT", "SFTCalculatorApp", "launch_gui")
