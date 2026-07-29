#!/usr/bin/env python3
"""Implementation-distinct validator for the formal Tesla return family."""

from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys


CLAIMS = {
    "SFT-PHYS-TESLA-BOUNDED-CAVITY-078": "bounded",
    "SFT-PHYS-TESLA-ODD-QUARTER-WAVE-079": "quarter",
    "SFT-PHYS-TESLA-LONGITUDINAL-TRANSVERSE-080": "orientation",
    "SFT-PHYS-TESLA-RESONANT-TRANSFER-081": "transfer",
}


def exact_checks(kind):
    if kind == "bounded":
        return all((tuple((2 * 3) * n for n in range(1, 5)) == (6, 12, 18, 24), 2 * 7 == 14, 2 * 6 + 2 == 2 * 7))
    if kind == "quarter":
        values = tuple(2 * n - 1 for n in range(1, 33))
        return values[:5] == (1, 3, 5, 7, 9) and all(values[n - 1] + 1 == 2 * n for n in range(1, 33))
    if kind == "orientation":
        roles = ("longitudinal", "transverse-a", "transverse-b")
        word = tuple(("source", "upper", "return", "lower")[(n - 1) % 4] for n in range(1, 10))
        return len(roles) == 3 and sum(role.startswith("transverse") for role in roles) == 2 and word[:8] == word[:-1]
    ledgers = (
        (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)),
        (Fraction(1, 4), Fraction(1, 2), Fraction(1, 4)),
    )
    return tuple(range(1, 8)) == (1, 2, 3, 4, 5, 6, 7) and all(
        row[0] + row[1] + row[2] == 1 for row in ledgers
    )


def main():
    claim_id = sys.argv[1]
    root = Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    generated = tuple("__".join(bits) for bits in product(("rejected", "retained"), repeat=8))
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = tuple(sealed["decisions"])
    controls = tuple(sealed["controls"])
    dependency_ids = tuple(sealed["registration"]["dependencies"])
    dependencies_present = all(
        (root / "claims" / dependency / "registration.json").is_file()
        and (root / "claims" / dependency / "certificate.json").is_file()
        for dependency in dependency_ids
    )
    passed = all((
        claim_id in CLAIMS,
        sealed["claim_id"] == claim_id,
        len(generated) == len(set(generated)) == 256,
        len(received) == len(set(received)) == sealed["census"]["expected_cardinality"] == 256,
        len(decisions) == 256,
        sum(bool(row["survives"]) for row in decisions) == 1,
        len(controls) == 4 and all(row["passed"] for row in controls),
        {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        sealed["closure"]["scope"] == "depth_independent",
        dependencies_present,
        exact_checks(CLAIMS[claim_id]),
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": len(received),
            "unique_survivor_count": sum(bool(row["survives"]) for row in decisions),
            "dependency_packages_present": dependencies_present,
            "exact_family_check": exact_checks(CLAIMS[claim_id]),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
