#!/usr/bin/env python3
"""Verify the actual SFT engine bytes without importing the engine package."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "sft" / "engine_seal.py"


def _load_seal_module():
    spec = importlib.util.spec_from_file_location("_sft_engine_seal_verifier", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("engine seal verifier cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed unless the runtime SFT engine matches the canonical public seal."
    )
    parser.add_argument("--json", action="store_true", help="emit the complete machine-readable attestation")
    args = parser.parse_args()

    module = _load_seal_module()
    attestation = module.verify_engine_seal(ROOT)
    if args.json:
        print(json.dumps(attestation.to_dict(), indent=2, sort_keys=True))
    elif attestation.violations:
        print("SFT ENGINE SEAL VIOLATION — VOID / INVALID / HALTED", file=sys.stderr)
        print(f"Canonical seal: {attestation.seal_id}", file=sys.stderr)
        for violation in attestation.violations:
            print(f"- {violation}", file=sys.stderr)
    else:
        print("SFT ENGINE SEAL: VALID CANONICAL ENGINE")
        print(f"Seal: {attestation.seal_id}")
        print(f"Git tree: {attestation.engine_git_tree}")
        print(f"Runtime files verified: {attestation.verified_file_count}")
    return 0 if not attestation.violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
