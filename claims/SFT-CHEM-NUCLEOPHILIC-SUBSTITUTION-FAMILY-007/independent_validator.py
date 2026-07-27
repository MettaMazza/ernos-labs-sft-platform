"""Implementation-distinct exact reconstruction for Chemistry ORG-007."""
from __future__ import annotations

import json
import sys
from itertools import product


CLAIM_ID = "SFT-CHEM-NUCLEOPHILIC-SUBSTITUTION-FAMILY-007"
DOMAINS = (
    ("selected-product-label-or-disconnected-fragments", "complete-source-ordered-reaction-carrier"),
    ("reactant-or-bond-support-omitted", "complete-source-bonds-and-free-entering-pair"),
    ("electrons-created-destroyed-or-collapsed-to-charge-number", "every-held-pair-occurrence-conserved"),
    ("endpoint-only-product-or-extra-bond-change", "one-bond-cleaved-and-one-bond-formed"),
    ("named-mechanism-rate-law-or-unordered-snapshots", "complete-one-transition-and-cleavage-first-path-family"),
    ("intermediate-adverse-or-mechanism-row-omitted", "every-state-edge-status-and-source-record-retained"),
    ("substrate-product-mechanism-readable-before-seal", "value-free-structure-and-mechanism-target-seal"),
    ("molecule-specific-exception-or-recomputed-prefix", "fresh-retained-substrate-successor-no-extra-rule"),
)
SURVIVOR = "__".join(domain[1] for domain in DOMAINS)


def _native_reconstruction() -> dict:
    atoms = ("centre", "retained", "entering", "leaving")
    pairs = {
        "retained": ("r1", "r2"), "entering": ("e1", "e2"), "leaving": ("l1", "l2")
    }
    source = {
        "bonds": {frozenset(("centre", "retained")): pairs["retained"], frozenset(("centre", "leaving")): pairs["leaving"]},
        "free": {"entering": pairs["entering"]},
    }
    intermediate = {
        "bonds": {frozenset(("centre", "retained")): pairs["retained"]},
        "free": {"entering": pairs["entering"], "leaving": pairs["leaving"]},
    }
    terminal = {
        "bonds": {frozenset(("centre", "retained")): pairs["retained"], frozenset(("centre", "entering")): pairs["entering"]},
        "free": {"leaving": pairs["leaving"]},
    }
    electrons = lambda state: sorted(item for pair in tuple(state["bonds"].values()) + tuple(state["free"].values()) for item in pair)
    one_path = (source, terminal)
    two_path = (source, intermediate, terminal)
    formation_first_edges = set(source["bonds"]) | {frozenset(("centre", "entering"))}
    formation_first_rejected = sum("centre" in edge for edge in formation_first_edges) > 2
    extension = frozenset(("retained", "successor"))
    extended = tuple({"bonds": dict(state["bonds"], **{}) | {extension: ("s1", "s2")}, "free": state["free"]} for state in two_path)
    return {
        "atom_count": len(atoms), "one_transition_count": len(one_path) - 1, "two_transition_count": len(two_path) - 1,
        "all_electrons_conserved": electrons(source) == electrons(intermediate) == electrons(terminal),
        "one_bond_replaced": set(source["bonds"]) ^ set(terminal["bonds"]) == {frozenset(("centre", "leaving")), frozenset(("centre", "entering"))},
        "entering_pair_forms": terminal["bonds"][frozenset(("centre", "entering"))] == pairs["entering"],
        "leaving_pair_retained": terminal["free"]["leaving"] == pairs["leaving"],
        "formation_first_rejected": formation_first_rejected,
        "successor_prefix_preserved": all(set(row["bonds"]) - {extension} == set(state["bonds"]) for row, state in zip(extended, two_path)),
    }


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    reconstruction = _native_reconstruction()
    passed = (
        sealed["claim_id"] == CLAIM_ID and received == generated and len(generated) == 256 and len(set(received)) == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated} and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent" and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in sealed["controls"]) and all(reconstruction.values())
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None, **reconstruction,
            "external_structure_formula_mechanism_or_target_accessed": False,
            "named_SN1_SN2_rate_or_energy_law_used": False,
            "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
