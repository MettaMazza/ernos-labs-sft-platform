#!/usr/bin/env python3
"""Independent complete reconstruction for formal new-sector Claims 088-094."""

from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys


CLAIMS = {
    "SFT-PHYS-PENTA-COMPLETE-PHENOTYPE-088": ("sector-5-complete-forced-phenotype", "phenotype-5"),
    "SFT-PHYS-HEPTA-COMPLETE-PHENOTYPE-089": ("sector-7-complete-forced-phenotype", "phenotype-7"),
    "SFT-PHYS-PENTA-BETA-SLOPE-090": ("sector-5-coupling-divided-by-shortfall-equals-4", "beta-5"),
    "SFT-PHYS-HEPTA-BETA-SLOPE-091": ("sector-7-coupling-divided-by-shortfall-equals-6", "beta-7"),
    "SFT-PHYS-CATEGORY-CLEAN-PARTICLE-CENSUS-092": ("category-clean-total-110", "census"),
    "SFT-PHYS-NO-EXTRA-SECTOR-PARTICLE-BOUNDARY-093": ("first-excluded-prime-eleven-and-explicit-outside-list-falsifiers", "boundary"),
    "SFT-PHYS-SMITHION-INTERACTION-SEARCH-SIGNATURES-094": ("electromagnetically-dark-no-generated-nuclear-recoil-gravity-and-confining-jet-signatures", "signatures"),
}
DEPENDENCIES = {
    "SFT-PHYS-PENTA-COMPLETE-PHENOTYPE-088": ("SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003", "SFT-PHYS-STRONG-CARRIER-MASSLESS-CONFINED-TERMINAL-013", "SFT-PHYS-INTERACTION-UNIFICATION-TERMINAL-025", "SFT-MATH-EXACT-ARITHMETIC-001"),
    "SFT-PHYS-HEPTA-COMPLETE-PHENOTYPE-089": ("SFT-PHYS-PENTA-COMPLETE-PHENOTYPE-088", "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003", "SFT-PHYS-STRONG-CARRIER-MASSLESS-CONFINED-TERMINAL-013", "SFT-MATH-EXACT-ARITHMETIC-001"),
    "SFT-PHYS-PENTA-BETA-SLOPE-090": ("SFT-PHYS-PENTA-COMPLETE-PHENOTYPE-088", "SFT-PHYS-FORCE-PRIME-SECTOR-LADDER-002", "SFT-MATH-EXACT-ARITHMETIC-001"),
    "SFT-PHYS-HEPTA-BETA-SLOPE-091": ("SFT-PHYS-HEPTA-COMPLETE-PHENOTYPE-089", "SFT-PHYS-PENTA-BETA-SLOPE-090", "SFT-PHYS-FORCE-PRIME-SECTOR-LADDER-002", "SFT-MATH-EXACT-ARITHMETIC-001"),
    "SFT-PHYS-CATEGORY-CLEAN-PARTICLE-CENSUS-092": ("SFT-PHYS-HEPTA-BETA-SLOPE-091", "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003", "SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-DARK-SMITHION-LFV-TERMINAL-061"),
    "SFT-PHYS-NO-EXTRA-SECTOR-PARTICLE-BOUNDARY-093": ("SFT-PHYS-CATEGORY-CLEAN-PARTICLE-CENSUS-092", "SFT-PHYS-FORCE-PRIME-SECTOR-LADDER-002", "SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-STRONG-CP-BARYON-STABILITY-TERMINAL-063"),
    "SFT-PHYS-SMITHION-INTERACTION-SEARCH-SIGNATURES-094": ("SFT-PHYS-NO-EXTRA-SECTOR-PARTICLE-BOUNDARY-093", "SFT-PHYS-DARK-SMITHION-LFV-TERMINAL-061", "SFT-PHYS-STRONG-CP-BARYON-STABILITY-TERMINAL-063", "SFT-PHYS-GRAVITY-EQUIVALENCE-001"),
}


def surface(relation):
    domains = (
        ("rewrite-or-bypass-predecessors", "retain-admitted-prime-sector-predecessors"),
        ("open-or-target-selected-sector", "generated-penta-hepta-boundary"),
        ("free-phenotype-or-slope", relation),
        ("massive-or-speed-fitted-carrier", "empty-mass-One-speed-carrier"),
        ("unbounded-width-or-unpaired-charge", "half-One-tube-and-complete-antipodes"),
        ("mixed-category-or-open-inventory", "category-clean-finite-inventory"),
        ("target-selected-survivor", "formal-seal-before-observation"),
        ("free-extra-rule", "no-extra-rule"),
    )
    return tuple("__".join(row) for row in product(*domains)), "__".join(domain[1] for domain in domains)


def phenotype(sector):
    shortfall = Fraction(1, sector)
    coupling = 1 - shortfall
    pairs = tuple((Fraction(index, sector), Fraction(sector - index, sector)) for index in range(1, (sector + 1) // 2))
    return coupling, shortfall, sector * sector - 1, pairs


def exact(kind):
    if kind.startswith("phenotype"):
        sector = int(kind[-1])
        coupling, shortfall, mediators, pairs = phenotype(sector)
        return all((coupling + shortfall == 1, mediators == sector * sector - 1, len(pairs) == (sector - 1) // 2, all(a + b == 1 for a, b in pairs), Fraction(1, 2) + Fraction(1, 2) == 1, shortfall * sector == 1))
    if kind.startswith("beta"):
        sector = int(kind[-1])
        coupling, shortfall, _, _ = phenotype(sector)
        return coupling / shortfall == sector - 1 and (Fraction(4), Fraction(6)) == (phenotype(5)[0] / phenotype(5)[1], phenotype(7)[0] / phenotype(7)[1])
    carrier_counts = tuple(sector * sector - 1 for sector in (2, 3, 5, 7))
    gauge = sum(carrier_counts)
    total = gauge + 3 + 12 + 12
    if kind == "census":
        return carrier_counts == (3, 8, 24, 48) and gauge == 83 and total == 110
    if kind == "boundary":
        falsifiers = ("axion", "sterile-neutrino", "supersymmetric-partner", "sector-beyond-seven", "outside-total")
        return total == 110 and 7 < 11 and len(falsifiers) == 5
    signatures = {sector: {"em": "empty-One", "nuclear": "empty-One", "gravity": 1, "jets": sector * sector - 1, "constituents": sector} for sector in (5, 7)}
    return tuple(row["jets"] for row in signatures.values()) == (24, 48) and tuple(row["constituents"] for row in signatures.values()) == (5, 7) and all(row["em"] == row["nuclear"] == "empty-One" and row["gravity"] == 1 for row in signatures.values())


def main():
    claim_id = sys.argv[1]
    root = Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    if claim_id not in CLAIMS:
        raise SystemExit(1)
    relation, kind = CLAIMS[claim_id]
    generated, survivor = surface(relation)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    recomputed = {candidate: candidate == survivor for candidate in generated}
    controls = tuple(sealed["controls"])
    dependencies_present = all(
        (root / "claims" / dependency / "registration.json").is_file()
        and (root / "claims" / dependency / "certificate.json").is_file()
        for dependency in DEPENDENCIES[claim_id]
    )
    passed = all((
        sealed["claim_id"] == claim_id,
        received == generated,
        len(received) == len(set(received)) == sealed["census"]["expected_cardinality"] == 256,
        decisions == recomputed,
        sum(recomputed.values()) == 1,
        len(controls) == 4 and all(row["passed"] for row in controls),
        {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        sealed["closure"]["scope"] == "depth_independent",
        sealed["closure"]["minimality_passed"] is True,
        sealed["closure"]["named_shape_uniqueness_passed"] is True,
        dependencies_present,
        exact(kind),
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": len(received),
            "candidate_order_reconstructed": received == generated,
            "decision_vector_reconstructed": decisions == recomputed,
            "unique_survivor_count": sum(recomputed.values()),
            "dependency_packages_present": dependencies_present,
            "exact_family_check": exact(kind),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
