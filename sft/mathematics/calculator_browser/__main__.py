"""Launch the accessible Smithian Fold calculator application."""

from __future__ import annotations

import argparse

from .app import launch_browser_calculator


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="smithian-fold-calculator",
        description="Open the dependency-free Smithian Fold scientific calculator",
    )
    parser.add_argument("--no-browser", action="store_true", help="serve without opening the browser")
    parser.add_argument("--private", action="store_true", help="limit access to this computer")
    parser.add_argument("--port", type=int, default=8765, help="first local port to try")
    parser.add_argument("--places", type=int, default=18, help="readable decimal places")
    parser.add_argument("--limit", type=int, default=10000, help="positive counted operation boundary")
    arguments = parser.parse_args()
    launch_browser_calculator(
        start_port=arguments.port,
        places=arguments.places,
        operation_limit=arguments.limit,
        open_browser=not arguments.no_browser,
        share=not arguments.private,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
