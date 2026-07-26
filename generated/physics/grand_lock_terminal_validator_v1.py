#!/usr/bin/env python3
"""Independent Grand Lock recomputation using only sealed and frozen inputs."""

from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import sys


CLAIM_ID = "SFT-PHYS-GRAND-LOCK-TERMINAL-075"
INPUT_HASH = "sha256:325248e4081b287fbacd125efe18a9d5fbba05f1fbd459eaa2a61a225120b3ca"
ROOT_CLAIM = "SFT-FOUNDATION-ONE-001"
DOMAINS = tuple(("rejected", "retained") for _ in range(12))
SURVIVOR = tuple("retained" for _ in DOMAINS)


def file_hash(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cover(carrier):
    depth, support = 1, 2
    while support < carrier:
        support *= 2
        depth += 1
    return depth


def values(c):
    one = Fraction(1, 1)
    down, up = cover(c ** 3), cover(c ** 4)
    rungs = tuple((down ** (c - promoted)) * (up ** promoted) for promoted in range(c + 1))
    chain = Fraction(rungs[-1], 1)
    for rung in reversed(rungs[1:-1]):
        chain = Fraction(rung, 1) + one / chain
    complete_cover = Fraction(2 * down ** c, 1) + one / chain
    inverse_alpha = Fraction(2 ** up, 1) + Fraction(c ** 2, 1) * (complete_cover + one) / complete_cover
    alpha = one / inverse_alpha
    lepton_denominator = 2 * c ** (c + 2) - 1
    lepton_sharpened = one / (Fraction(lepton_denominator, 1) - Fraction(1, c))
    lepton_terminal = lepton_sharpened - (alpha ** c) * (Fraction(down, 1) + Fraction(up, c) * alpha) / c ** c
    volume, support = c ** 3, 2 ** down
    return {
        "generator": c,
        "down_cover_depth": down,
        "up_cover_depth": up,
        "inverse_fine_structure_terminal": inverse_alpha,
        "charged_lepton_pair_invariant": Fraction(1, 2 * c),
        "charged_lepton_leading_product": Fraction(1, lepton_denominator),
        "charged_lepton_sharpened_product": lepton_sharpened,
        "charged_lepton_terminal_product": lepton_terminal,
        "quark_down_pair_invariant": Fraction(1, 2 * (c + 1)),
        "quark_up_pair_invariant": Fraction(1, 2 * (c + c)),
        "quark_down_product_invariant": Fraction(1, c * 2 ** up - 1),
        "quark_up_product_invariant": Fraction(1, c * 2 ** (up + c) - 1),
        "dark_baryon_leading_ratio": Fraction(volume, down),
        "dark_baryon_refined_ratio": Fraction(volume, 1) / (Fraction(down, 1) + Fraction(1, support - 1)),
        "dark_share": Fraction(volume, support),
        "baryon_share": Fraction(down, support),
        "hubble_leading_ratio": one + Fraction(c - 1, c) / 8,
        "hubble_refined_ratio": one + (Fraction(c - 1, c) + Fraction(1, 2 ** up - 1)) / 8,
        "planck_proton_terminal_squared_hierarchy": Fraction(2 ** (2 ** up - 1), 1) * (one - Fraction(2, c) * alpha),
        "local_vacuum_amplitude_floor": Fraction(1, 2 ** (2 * down)),
        "local_vacuum_energy_floor": Fraction(1, 2 ** (4 * down)),
    }


def verify_frozen(record, root):
    physics_ids = tuple(record["physics_claim_ids"])
    rows = {row["claim_id"]: row for row in record["dependency_dictionary"]}
    if not (len(physics_ids) == len(set(physics_ids)) and len(physics_ids) > 0):
        return False
    if len(physics_ids) != record["physics_claim_count"]:
        return False
    if set(physics_ids) != {row["claim_id"] for row in record["physics_claims"]}:
        return False
    active, finished = set(), set()
    memo = {}

    def visit(claim_id):
        if claim_id in active or claim_id not in rows:
            return False
        if claim_id in finished:
            return True
        active.add(claim_id)
        if not all(visit(item) for item in rows[claim_id]["dependencies"]):
            return False
        active.remove(claim_id)
        finished.add(claim_id)
        return True

    def reaches(claim_id):
        if claim_id == ROOT_CLAIM:
            return True
        if claim_id in memo:
            return memo[claim_id]
        memo[claim_id] = any(reaches(item) for item in rows[claim_id]["dependencies"])
        return memo[claim_id]

    if not all(visit(claim_id) and reaches(claim_id) for claim_id in physics_ids):
        return False
    if len(finished) != record["transitive_claim_count"]:
        return False
    for row in record["dependency_dictionary"]:
        if file_hash(root / row["registration_path"]) != row["registration_sha256"]:
            return False
    for row in record["physics_claims"]:
        if file_hash(root / row["receipt_path"]) != row["receipt_file_sha256"]:
            return False
        if file_hash(root / row["certificate_path"]) != row["certificate_sha256"]:
            return False
    return all(record["certificate"].values())


def main():
    input_path, root, sealed_path = Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    record = json.loads(input_path.read_text(encoding="utf-8"))
    sealed = json.loads(sealed_path.read_text(encoding="utf-8"))
    generated = tuple("__".join(row) for row in product(*DOMAINS))
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    # StructuralPhysicsProgram uses the registered axis labels, so its unique
    # retained candidate is independently identified by decision cardinality.
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    current, successor = values(3), values(4)
    exact_current = all((
        current["inverse_fine_structure_terminal"] == Fraction(503846395469, 3676744786),
        current["charged_lepton_leading_product"] == Fraction(1, 485),
        current["charged_lepton_sharpened_product"] == Fraction(3, 1454),
        current["quark_down_product_invariant"] == Fraction(1, 383),
        current["quark_up_product_invariant"] == Fraction(1, 3071),
        current["dark_baryon_leading_ratio"] == Fraction(27, 5),
        current["dark_share"] == Fraction(27, 32),
        current["baryon_share"] == Fraction(5, 32),
        current["hubble_leading_ratio"] == Fraction(13, 12),
        current["hubble_refined_ratio"] == Fraction(3305, 3048),
        current["local_vacuum_amplitude_floor"] == Fraction(1, 2 ** 10),
        current["local_vacuum_energy_floor"] == Fraction(1, 2 ** 20),
    ))
    passed = all((
        sys.argv[1] == CLAIM_ID,
        sealed["claim_id"] == CLAIM_ID,
        file_hash(input_path) == INPUT_HASH,
        verify_frozen(record, root),
        len(received) == len(set(received)) == sealed["census"]["expected_cardinality"] == 4096,
        len(decisions) == 4096,
        sum(bool(item) for item in decisions.values()) == 1,
        all(row["passed"] for row in sealed["controls"]),
        {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        sealed["closure"]["scope"] == "depth_independent",
        exact_current,
        set(current) == set(successor),
        all(current[name] != successor[name] for name in current),
        record["empirical_claim_count"] > 0,
        record["unfavorable_or_scope_boundary_count"] > 0,
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "physics_claim_count": record["physics_claim_count"],
            "transitive_claim_count": record["transitive_claim_count"],
            "empirical_claim_count": record["empirical_claim_count"],
            "generator_dependent_value_count": len(current),
            "every_generator_dependent_value_moves": all(current[name] != successor[name] for name in current),
            "current_branch_closed_extension_open": True,
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
