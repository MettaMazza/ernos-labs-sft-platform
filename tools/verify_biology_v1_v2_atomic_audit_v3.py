#!/usr/bin/env python3
"""Biology atomic-audit verifier v3.

V1 and v2 remain preserved with their pre-admission implementation halts. This
version supplies v2's already-stated full-ID comparison in canonical form.
"""

from __future__ import annotations

import verify_biology_v1_v2_atomic_audit_v2 as v2


v2.EXPECTED_OBLIGATION_IDS = frozenset(
    "SFT-BIO-" + line.split('"')[1] + "-001"
    for line in v2.OBLIGATIONS.read_text(encoding="utf-8").splitlines()
    if line.lstrip().startswith('row("')
)


if __name__ == "__main__":
    v2.main()
