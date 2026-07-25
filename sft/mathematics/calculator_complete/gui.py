"""Progressively disclosed, cross-platform desktop calculator application."""

from __future__ import annotations

from dataclasses import asdict
import json

from sft.mathematics.calculator.values import CalculatorHalt

from .controller import (
    CalculatorController,
    FUNCTION_CATALOG,
    MAIN_BUTTON_ROWS,
)
from .explorer import RegisteredMathematicsExplorer


GUIDE_TEXT = """Use it like the calculator you already know

Type an expression or press the number and operation keys, then press = or Enter.

Try these
  1 + 1 =
  0.1 + 0.2 =
  sqrt(2)
  sin(30) in DEG mode
  mean(1, 2, 3, 4)

What is different about a Smithian Fold result?

• The screen can display 0, but the proof stores the structural empty-One form rather than a numerical zero.
• A minus sign is represented by a held direction and a positive size; the proof never stores a negative magnitude.
• A decimal you type is translated into an exact fraction before calculation.
• Values such as pi, square roots and trigonometric answers remain exact rational lower-and-upper certificates. The large decimal is a friendly view of that proof.
• A conventional complex value is represented by a real Fold fibre and an orthogonal Fold fibre, not an imaginary proof number.
• If an expression cannot obey the laws or close inside its counted resources, the calculator stops and explains why. It never hides the problem as NaN or infinity.

Nothing advanced is required for ordinary use. Select “Show SFT proof” only when you want the exact value, trace, history, complete function list, or Mathematics law explorer.

Memory
  MS stores the answer. MR recalls it. M+ and M− change the retained memory. MC clears memory. Ans means the previous answer.

Angle modes
  RAD uses radians, DEG uses degrees, and GRAD uses gradians.
"""


class SFTCalculatorApp:
    """A familiar calculator first, with complete evidence available on demand."""

    def __init__(self, root, *, places: int = 18, operation_limit: int = 10000):
        import tkinter as tk
        from tkinter import ttk

        self.tk = tk
        self.ttk = ttk
        self.root = root
        self.controller = CalculatorController(places=places, operation_limit=operation_limit)
        self.explorer = RegisteredMathematicsExplorer()
        self.expression = tk.StringVar()
        self.result = tk.StringVar(value="0")
        self.status = tk.StringVar(value="Ready")
        self.mode = tk.StringVar(value="RAD")
        self.memory_indicator = tk.StringVar(value="")
        self.details_visible = False

        root.title("Smithian Fold Scientific Calculator")
        root.geometry("760x760")
        root.minsize(720, 660)
        root.configure(background="#f3f3f3")
        try:
            root.tk.call("tk", "scaling", 1.12)
        except tk.TclError:
            pass

        style = ttk.Style(root)
        themes = style.theme_names()
        if "vista" in themes:
            style.theme_use("vista")
        elif "aqua" in themes:
            style.theme_use("aqua")
        elif "clam" in themes:
            style.theme_use("clam")
        style.configure("Display.TEntry", font=("Segoe UI", 18), padding=10)
        style.configure("Result.TLabel", font=("Segoe UI Semibold", 28), anchor="e")
        style.configure("Calc.TButton", font=("Segoe UI", 11), padding=(7, 10))
        style.configure("Equals.TButton", font=("Segoe UI Semibold", 12), padding=(7, 10))
        style.configure("Title.TLabel", font=("Segoe UI Semibold", 15))
        style.configure("Status.TLabel", font=("Segoe UI", 9), foreground="#555555")

        self.outer = ttk.Frame(root, padding=14)
        self.outer.pack(fill="both", expand=True)
        self.outer.columnconfigure(0, weight=3)
        self.outer.columnconfigure(1, weight=2)
        self.outer.rowconfigure(0, weight=1)

        calculator = ttk.Frame(self.outer)
        calculator.grid(row=0, column=0, sticky="nsew")
        for column in range(8):
            calculator.columnconfigure(column, weight=1)

        header = ttk.Frame(calculator)
        header.grid(row=0, column=0, columnspan=8, sticky="ew", pady=(0, 8))
        ttk.Label(header, text="Scientific", style="Title.TLabel").pack(side="left")
        ttk.Label(header, textvariable=self.memory_indicator).pack(side="left", padx=10)
        self.details_button = ttk.Button(header, text="Show SFT proof", command=self.toggle_details)
        self.details_button.pack(side="right", padx=(8, 0))
        ttk.Button(header, text="Learn SFT", command=self.show_learn).pack(side="right", padx=(8, 0))
        mode_box = ttk.Combobox(
            header,
            textvariable=self.mode,
            values=("RAD", "DEG", "GRAD"),
            state="readonly",
            width=6,
        )
        mode_box.pack(side="right")
        mode_box.bind("<<ComboboxSelected>>", self.change_mode)

        self.entry = ttk.Entry(
            calculator,
            textvariable=self.expression,
            justify="right",
            style="Display.TEntry",
        )
        self.entry.grid(row=1, column=0, columnspan=8, sticky="ew", pady=(0, 4))
        self.entry.bind("<Return>", lambda _event: self.evaluate())
        self.entry.bind("<KP_Enter>", lambda _event: self.evaluate())
        self.entry.bind("<Escape>", lambda _event: self.press("C"))
        self.entry.bind("<Delete>", lambda _event: self.press("CE"))

        result_frame = ttk.Frame(calculator)
        result_frame.grid(row=2, column=0, columnspan=8, sticky="ew", pady=(0, 8))
        result_frame.columnconfigure(0, weight=1)
        ttk.Label(result_frame, textvariable=self.result, style="Result.TLabel").grid(
            row=0, column=0, sticky="ew"
        )
        ttk.Button(result_frame, text="Copy", command=self.copy_result).grid(
            row=0, column=1, padx=(8, 0)
        )
        ttk.Label(calculator, textvariable=self.status, style="Status.TLabel").grid(
            row=3, column=0, columnspan=8, sticky="ew", pady=(0, 6)
        )

        for row_index, row in enumerate(MAIN_BUTTON_ROWS, start=4):
            calculator.rowconfigure(row_index, weight=1)
            for column, label in enumerate(row):
                style_name = "Equals.TButton" if label == "=" else "Calc.TButton"
                ttk.Button(
                    calculator,
                    text=label,
                    command=lambda item=label: self.press(item),
                    style=style_name,
                ).grid(row=row_index, column=column, sticky="nsew", padx=2, pady=2)

        self.details = ttk.Notebook(self.outer)
        self.details.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        self._build_details()
        self.details.grid_remove()
        self.entry.focus_set()

    def _text_tab(self, title: str):
        frame = self.ttk.Frame(self.details, padding=10)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        text = self.tk.Text(frame, wrap="word", font=("Segoe UI", 10), relief="flat", background="#ffffff")
        scroll = self.ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        self.details.add(frame, text=title)
        return frame, text

    def _build_details(self) -> None:
        history = self.ttk.Frame(self.details, padding=10)
        history.rowconfigure(0, weight=1)
        history.columnconfigure(0, weight=1)
        self.history_list = self.tk.Listbox(history, font=("Segoe UI", 10), activestyle="none")
        self.history_list.grid(row=0, column=0, sticky="nsew")
        self.history_list.bind("<Double-Button-1>", self.restore_history)
        self.ttk.Button(history, text="Clear history", command=self.clear_history).grid(
            row=1, column=0, sticky="ew", pady=(8, 0)
        )
        self.details.add(history, text="History")

        _, self.proof_text = self._text_tab("Exact proof")

        functions = self.ttk.Frame(self.details, padding=10)
        functions.columnconfigure(0, weight=1)
        functions.columnconfigure(1, weight=3)
        self.ttk.Label(functions, text="All functions", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )
        for row, (name, template, description) in enumerate(FUNCTION_CATALOG, start=1):
            self.ttk.Button(
                functions,
                text=name,
                command=lambda item=name: self.insert_catalog(item),
            ).grid(row=row, column=0, sticky="ew", padx=(0, 8), pady=2)
            self.ttk.Label(functions, text=f"{template}\n{description}").grid(
                row=row, column=1, sticky="w", pady=2
            )
        self.details.add(functions, text="Functions")

        laws = self.ttk.Frame(self.details, padding=10)
        laws.rowconfigure(2, weight=1)
        laws.columnconfigure(0, weight=1)
        self.law_choice = self.tk.StringVar(value=self.explorer.claim_ids()[0])
        law_box = self.ttk.Combobox(
            laws,
            textvariable=self.law_choice,
            values=self.explorer.claim_ids(),
            state="readonly",
        )
        law_box.grid(row=0, column=0, sticky="ew")
        law_actions = self.ttk.Frame(laws)
        law_actions.grid(row=1, column=0, sticky="ew", pady=6)
        self.ttk.Button(law_actions, text="Explain law", command=self.show_law).pack(side="left")
        self.ttk.Button(law_actions, text="Replay enumeration", command=self.replay_law).pack(
            side="left", padx=6
        )
        self.law_text = self.tk.Text(laws, wrap="word", font=("Consolas", 9), relief="flat", background="#ffffff")
        self.law_text.grid(row=2, column=0, sticky="nsew")
        self.details.add(laws, text="Mathematics")

        _, learn = self._text_tab("Learn")
        learn.insert("1.0", GUIDE_TEXT)
        learn.configure(state="disabled")

    def _set_text(self, widget, content: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", content)
        widget.configure(state="disabled")

    def _sync(self, view) -> None:
        self.expression.set(view.expression)
        self.result.set(view.result)
        self.mode.set(view.angle_mode)
        self.memory_indicator.set("M" if view.memory_active else "")
        self.status.set("Ready" if not view.error else "Cannot calculate: " + view.error)
        self._set_text(self.proof_text, view.exact_details)
        current = tuple(self.history_list.get(0, "end"))
        if current != view.history:
            self.history_list.delete(0, "end")
            for entry in view.history:
                self.history_list.insert("end", entry)

    def toggle_details(self) -> None:
        self.details_visible = not self.details_visible
        if self.details_visible:
            self.details.grid()
            self.root.geometry("1180x760")
            self.details_button.configure(text="Hide SFT proof")
        else:
            self.details.grid_remove()
            self.root.geometry("760x760")
            self.details_button.configure(text="Show SFT proof")

    def show_learn(self) -> None:
        if not self.details_visible:
            self.toggle_details()
        self.details.select(4)

    def change_mode(self, _event=None) -> None:
        self._sync(self.controller.set_angle_mode(self.mode.get()))

    def press(self, label: str) -> None:
        self.controller.set_expression(self.expression.get())
        self._sync(self.controller.press(label))
        self.entry.icursor("end")
        self.entry.focus_set()

    def evaluate(self) -> None:
        self.controller.set_expression(self.expression.get())
        self._sync(self.controller.evaluate())

    def insert_catalog(self, name: str) -> None:
        self.controller.set_expression(self.expression.get())
        self._sync(self.controller.insert_catalog(name))
        self.entry.icursor("end")
        self.entry.focus_set()

    def restore_history(self, _event=None) -> None:
        selection = self.history_list.curselection()
        if selection:
            self._sync(self.controller.restore_history(selection[0]))
            self.entry.icursor("end")
            self.entry.focus_set()

    def clear_history(self) -> None:
        self._sync(self.controller.clear_history())

    def copy_result(self) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(self.result.get())

    def show_law(self) -> None:
        summary = asdict(self.explorer.summary(self.law_choice.get()))
        self._set_text(self.law_text, json.dumps(summary, indent=2, sort_keys=True))

    def replay_law(self) -> None:
        replay = self.explorer.replay(self.law_choice.get())
        self._set_text(self.law_text, replay.to_json())


def launch_gui(*, places: int = 18, operation_limit: int = 10000) -> None:
    try:
        import tkinter as tk
    except ImportError as error:
        raise CalculatorHalt(
            "This Python installation does not include the standard graphical library. The terminal calculator remains available."
        ) from error
    root = tk.Tk()
    SFTCalculatorApp(root, places=places, operation_limit=operation_limit)
    root.mainloop()


__all__ = ("GUIDE_TEXT", "SFTCalculatorApp", "launch_gui")
