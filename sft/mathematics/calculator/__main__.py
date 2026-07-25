"""Cross-platform command line entry point."""

from __future__ import annotations

import argparse
import sys

from .gui import launch_gui
from .session import CalculatorSession
from .values import CalculatorHalt


def _print_result(calculation, show_trace: bool) -> None:
    print(calculation.render())
    if show_trace:
        print("trace:")
        for record in calculation.trace:
            print("  " + record)
        print(
            "resources: "
            f"tokens={calculation.tokens_read}, operations={calculation.operations_executed}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="python -m sft.mathematics.calculator",
        description="Exact SFT-native scientific calculator",
    )
    parser.add_argument("expression", nargs="?", help="expression to evaluate; omit for interactive mode")
    parser.add_argument("--places", type=int, default=18, help="decimal projection places (1..60)")
    parser.add_argument("--angle", choices=("rad", "deg", "grad"), default="rad", help="angle mode")
    parser.add_argument("--trace", action="store_true", help="print the complete operation trace")
    parser.add_argument("--gui", action="store_true", help="open the desktop calculator app")
    arguments = parser.parse_args()
    if arguments.gui:
        try:
            launch_gui(places=arguments.places)
            return 0
        except CalculatorHalt as error:
            print(f"HALT: {error}", file=sys.stderr)
            return 2
    session = CalculatorSession(places=arguments.places, angle_mode=arguments.angle)
    try:
        if arguments.expression is not None:
            _print_result(session.evaluate(arguments.expression), arguments.trace)
            return 0
        print("SFT exact calculator. Type an expression ending with =, or :help for commands.")
        while True:
            try:
                expression = input("sft> ").strip()
            except EOFError:
                return 0
            if expression.lower() in {"quit", "exit"}:
                return 0
            if expression == ":help":
                print("commands: :rad :deg :grad :mc :mr :ms :m+ :m- :history :clear")
                continue
            if expression in {":rad", ":deg", ":grad"}:
                session.set_angle_mode(expression[1:])
                print("angle mode:", expression[1:].upper())
                continue
            if expression == ":mc":
                session.memory_clear(); print("memory: empty-One"); continue
            if expression == ":mr":
                print("memory:", session.memory); continue
            if expression == ":ms":
                session.memory_store(); print("memory stored"); continue
            if expression == ":m+":
                session.memory_add(); print("memory updated"); continue
            if expression == ":m-":
                session.memory_subtract(); print("memory updated"); continue
            if expression == ":history":
                for item in session.history:
                    print(f"{item.index}: {item.expression} = {item.calculation.render()}")
                continue
            if expression == ":clear":
                session.clear_history(); print("history cleared"); continue
            if not expression:
                continue
            try:
                _print_result(session.evaluate(expression), arguments.trace)
            except CalculatorHalt as error:
                print(f"HALT: {error}", file=sys.stderr)
    except CalculatorHalt as error:
        print(f"HALT: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
