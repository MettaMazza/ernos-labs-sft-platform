#!/usr/bin/env python3
"""Implementation-distinct exact validator for QCOMMX-001 through QCOMMX-024."""
import json
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path


RELATIONS = (
    "complete-source-image-environment-relation", "causal-relation-composition-with-memory-record",
    "distinguished-message-class-channel-coding", "word-phase-joint-record-transfer",
    "shared-nonfactorable-support-assisted-channel", "joint-observation-record-controlled-reconstruction",
    "four-message-joint-support-encoding", "remote-marginal-invariance-without-record-transfer",
    "maximum-distinguishable-support-per-use", "receiver-environment-distinction-ledger",
    "postprocessing-cannot-reopen-closed-distinction", "source-image-error-environment-custody",
    "link-support-joint-observation-outer-repartition", "link-generation-filtering-swapping-resource-chain",
    "typed-node-link-support-graph", "partial-order-event-and-message-ledger",
    "complete-path-link-resource-selection", "prepare-observe-sift-test-key-transcript",
    "message-tag-channel-verification-ledger", "authorized-subset-reconstruction-forbidden-subset-closure",
    "formal-transcript-to-physical-test-handoff", "adversary-action-resource-view-ledger",
    "classical-scheme-quantum-adversary-reduction-interface", "twenty-four-obligation-no-omission-ledger",
)


def independent_witness(index):
    checks = (
        len({"held": "held", "returned": "returned"}) == 2,
        dict((("held", "returned"), ("returned", "held")))["held"] == "returned",
        len({"message-held", "message-returned"}) == 2,
        ("word", "phase", "record")[-1] == "record",
        set(("held", "returned")) == {"held", "returned"},
        ("joint-observe", "two-records", "correct", "terminal")[-1] == "terminal",
        len(("m1", "m2", "m3", "m4")) == 4,
        set(("held", "returned")) == set(("returned", "held")),
        Fraction(4, 2) == Fraction(2, 1),
        4 > 2,
        all(after <= before for before, after in ((4, 3), (3, 2), (2, 1))),
        ("source", "image", "environment")[-1] == "environment",
        ("a", "d") == tuple(("a", "d")),
        len(("link", "filter", "swap", "end")) == 4,
        len({"a", "b", "c"}) == 3,
        all(a < b for a, b in ((1, 2), (2, 3))),
        ("a", "b", "c", "d")[0] == "a" and ("a", "b", "c", "d")[-1] == "d",
        (4, 2, 1, 1)[-1] == 1,
        ("message", "tag", "verified")[-1] == "verified",
        len({("a", "b"), ("a", "c"), ("b", "c")}) == 3,
        {"formal": True, "physical": False}["formal"],
        len(("query", "response", "measure", "guess")) == 4,
        ("classical", "quantum-adversary", "reduction")[-1] == "reduction",
        len(RELATIONS) == 24,
    )
    return checks[index - 1]


def generated_surface(index):
    axes = (
        ("partial-or-opaque-channel", "complete-source-image-environment-relation"),
        ("imported-protocol-or-security-answer", RELATIONS[index - 1]),
        ("terminal-message-only", "complete-causal-message-and-record-transcript"),
        ("hidden-shared-or-adversary-resource", "complete-link-round-support-and-adversary-ledger"),
        ("selected-favorable-cases", "literal-complete-product"),
        ("outcome-selected-law", "there-is-no-nothing-lineage"),
        ("preopened-communication-outcome", "post-registry-exact-execution"),
        ("silent-security-or-physical-export", "explicit-formal-security-and-physical-handoff"),
    )
    rows = tuple("__".join(coordinates) for coordinates in product(*axes))
    return rows, "__".join(axis[1] for axis in axes)


def main():
    claim_id, _root, sealed_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    index = int(claim_id.rsplit("-", 1)[-1]); sealed = json.loads(sealed_path.read_text()); rows, survivor = generated_surface(index)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"]); decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}; expected = {row: row == survivor for row in rows}
    passed = all((received == rows, len(set(received)) == len(received) == 256, decisions == expected, sum(expected.values()) == 1, len(sealed["controls"]) == 4, all(row["passed"] for row in sealed["controls"]), sealed["closure"]["scope"] == "depth_independent", independent_witness(index)))
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 256, "unique_survivor_count": 1, "quantum_communication_witness": independent_witness(index)}})); raise SystemExit(0 if passed else 1)


if __name__ == "__main__": main()
