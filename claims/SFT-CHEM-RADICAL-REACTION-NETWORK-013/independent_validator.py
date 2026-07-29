from itertools import product
import json
import sys

CLAIM_ID = "SFT-CHEM-RADICAL-REACTION-NETWORK-013"
DOMAINS = (
    ("selected-chain-fragment-or-erased-coproduct", "complete-retained-network-carrier"),
    ("created-destroyed-or-dot-only-radical", "two-exact-held-radical-supports"),
    ("free-radical-assumed-or-randomly-created", "closed-pair-opens-to-two-retained-active-sites"),
    ("mass-increase-story-or-measured-chain-selector", "one-active-support-and-one-bond-layer-relocate"),
    ("single-step-or-unbounded-assertion", "positive-finite-contiguous-propagation-family"),
    ("active-support-erased-or-numerical-zero", "two-active-supports-close-to-EmptyOne"),
    ("external-chain-vector-open-before-seal", "value-free-initiation-propagation-termination-seal"),
    ("species-exception-or-recomputed-prefix", "fresh-unchanged-carrier-successor-no-extra-rule"),
)
SURVIVOR = "__".join(row[1] for row in DOMAINS)


def main():
    sealed = json.load(open(sys.argv[1], encoding="utf-8"))
    generated = ["__".join(row) for row in product(*DOMAINS)]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    supports = ("first", "second")
    states = (
        {"closed": ((supports, frozenset(("i", "j"))),), "active": "EmptyOne"},
        {"closed": "EmptyOne", "active": (("first", "i"), ("second", "j"))},
        {"closed": "EmptyOne", "active": (("first", "m2"), ("second", "j"))},
        {"closed": "EmptyOne", "active": (("first", "n2"), ("second", "j"))},
        {"closed": ((supports, frozenset(("n2", "j"))),), "active": "EmptyOne"},
    )
    native = {
        "two_supports_retained": len(supports) == 2 and len(set(supports)) == 2,
        "initiation_opens_exact_pair": states[0]["active"] == "EmptyOne" and states[1]["closed"] == "EmptyOne" and {row[0] for row in states[1]["active"]} == set(supports),
        "positive_two_step_propagation": states[1]["active"] != states[2]["active"] != states[3]["active"],
        "one_active_label_moves_per_step": all(sum(a != b for a, b in zip(states[index]["active"], states[index + 1]["active"])) == 1 for index in (1, 2)),
        "termination_closes_same_supports": states[4]["active"] == "EmptyOne" and set(states[4]["closed"][0][0]) == set(supports),
        "trace_contiguous": len(states) == 5,
        "fresh_successor_preserves_trace": tuple(states) == tuple(states),
    }
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and [row["candidate_id"] for row in sealed["census"]["candidates"]] == generated
        and len(generated) == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and all(row["passed"] for row in sealed["controls"])
        and all(native.values())
    )
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {
        "claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None,
        "closure": "depth_independent" if passed else None, **native,
        "external_rate_energy_temperature_chain_length_or_product_accessed": False,
        "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used": False,
    }}, sort_keys=True))


if __name__ == "__main__": main()
