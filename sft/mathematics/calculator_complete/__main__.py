"""Cross-platform entry point for the complete calculator and law explorer."""

from __future__ import annotations

from dataclasses import asdict
import argparse
import json
import sys

from sft.mathematics.calculator.values import CalculatorHalt

from .evidence import calculation_evidence_json
from .explorer import RegisteredMathematicsExplorer
from .gui import launch_gui
from .presentation import friendly
from .session import CalculatorSession


def _print_calculation(calculation, proof: bool) -> None:
    if proof:
        print(calculation_evidence_json(calculation), end="")
    else:
        print(friendly(calculation.value))


def _interactive(session: CalculatorSession, proof: bool) -> int:
    print("Smithian Fold Scientific Calculator. Type 1+1=, :help, or :quit.")
    while True:
        try:
            expression = input("sft> ").strip()
        except EOFError:
            return 0
        if expression.lower() in {":quit", "quit", "exit"}:
            return 0
        if expression == ":help":
            print("Use ordinary calculator expressions. Commands: :rad :deg :grad :mc :mr :ms :m+ :m- :history :clear :quit")
            continue
        if expression in {":rad", ":deg", ":grad"}:
            session.set_angle_mode(expression[1:])
            print("Angle mode:", expression[1:].upper())
            continue
        if expression == ":mc":
            session.memory_clear()
            print("Memory cleared")
            continue
        if expression == ":mr":
            print("Memory:", session.memory)
            continue
        if expression == ":ms":
            session.memory_store()
            print("Memory stored")
            continue
        if expression == ":m+":
            session.memory_add()
            print("Memory updated")
            continue
        if expression == ":m-":
            session.memory_subtract()
            print("Memory updated")
            continue
        if expression == ":history":
            for item in session.history:
                print(f"{item.index}: {item.expression} = {friendly(item.calculation.value)}")
            continue
        if expression == ":clear":
            session.clear_history()
            session.all_clear()
            print("Calculator and history cleared; memory retained")
            continue
        if not expression:
            continue
        try:
            _print_calculation(session.evaluate(expression), proof)
        except CalculatorHalt as error:
            print(f"Cannot calculate: {error}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="sft-calculator",
        description="Familiar scientific calculator with exact Smithian Fold proof output",
    )
    parser.add_argument("expression", nargs="?", help="ordinary calculator expression")
    parser.add_argument("--gui", action="store_true", help="open the desktop application")
    parser.add_argument("--terminal", action="store_true", help="open the interactive terminal")
    parser.add_argument("--places", type=int, default=18, help="readable decimal places, from 1 through 60")
    parser.add_argument("--limit", type=int, default=10000, help="positive counted operation boundary")
    parser.add_argument("--angle", choices=("rad", "deg", "grad"), default="rad")
    parser.add_argument("--proof", action="store_true", help="print exact JSON proof output")
    parser.add_argument("--law", help="explain a registered Mathematics claim")
    parser.add_argument("--replay-law", help="locally replay a registered Mathematics enumeration")
    arguments = parser.parse_args()

    try:
        if arguments.law or arguments.replay_law:
            explorer = RegisteredMathematicsExplorer()
            if arguments.law:
                print(json.dumps(asdict(explorer.summary(arguments.law)), indent=2, sort_keys=True))
            else:
                print(explorer.replay(arguments.replay_law).to_json(), end="")
            return 0
        if arguments.gui or (arguments.expression is None and not arguments.terminal):
            launch_gui(places=arguments.places, operation_limit=arguments.limit)
            return 0
        session = CalculatorSession(
            places=arguments.places,
            angle_mode=arguments.angle,
            operation_limit=arguments.limit,
        )
        if arguments.expression is not None:
            _print_calculation(session.evaluate(arguments.expression), arguments.proof)
            return 0
        return _interactive(session, arguments.proof)
    except (CalculatorHalt, KeyError) as error:
        print(f"Cannot calculate: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
