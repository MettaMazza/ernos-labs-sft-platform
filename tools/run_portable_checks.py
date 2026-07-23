"""Run the same dependency-free validation suite on every supported host."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_repository import validate  # noqa: E402


def main() -> None:
    errors = validate()
    if errors:
        raise SystemExit("repository validation failed:\n" + "\n".join(errors))
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print("portable repository and engine checks: PASS")
    print("host-specific scientific branches exercised: none")


if __name__ == "__main__":
    main()
