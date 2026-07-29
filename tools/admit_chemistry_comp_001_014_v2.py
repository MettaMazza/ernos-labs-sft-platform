#!/usr/bin/env python3
"""Versioned workflow wrapper selecting preserved-retry execution_v2 sources."""

import importlib.util
from pathlib import Path

import admit_chemistry_comp_001_014_v1 as v1


def build_execution(claim):
    path = v1.ROOT / "claims" / claim.claim_id / "execution_v2.py"
    spec = importlib.util.spec_from_file_location("admit_v2_" + claim.claim_id.rsplit("-", 1)[-1], path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module.build_execution(v1.ROOT)


v1.build_execution = build_execution

if __name__ == "__main__":
    v1.main()
