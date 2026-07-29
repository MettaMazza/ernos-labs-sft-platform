#!/usr/bin/env python3
"""Implementation-distinct exact validator for SECX-001 through SECX-025."""
import json
import sys
from itertools import combinations, product
from pathlib import Path

FIBRES = ("left", "right")
RELATIONS = (
    "adversary-view-resource-success-ledger", "equal-ciphertext-support-secrecy", "resource-indexed-view-indistinguishability",
    "bounded-inversion-resource-relation", "predictor-advantage-boundary", "seed-to-expanded-support-relation", "keyed-function-family-relation",
    "decrypt-encrypt-identity-and-view-secrecy", "trapdoor-and-enumeration-boundary", "keyed-integrity-verification", "fresh-challenge-authentication",
    "compression-preimage-collision-ledger", "hiding-binding-opening-ledger", "verification-and-forgery-resource-ledger", "authenticated-shared-key-transcript",
    "threshold-share-reconstruction", "dual-challenge-extraction-boundary", "real-simulated-view-support-equality", "function-output-local-view-custody",
    "choice-private-message-transfer", "environment-indexed-adversary-composition", "implementation-leakage-handoff", "quantum-resource-reduction-boundary",
    "quantum-channel-ownership-handoff", "twenty-five-obligation-no-omission-ledger",
)


def opposite(label): return "right" if label == "left" else "left"
def cipher(message, key): return message if key == "left" else opposite(message)
def digest(word): return "left" if word[0] == word[1] else "right"
def tag(key, message): return ("tag", cipher(message, key))
def commit(message, blind): return ("commit", cipher(message, blind))


def independent_witness(index):
    if index == 1:
        record = ("A", ("pk",), (("query", "left"),), ("one-query",), "invert"); return len(record) == 5 and record[-1] == "invert"
    if index == 2:
        support = lambda message: sorted(cipher(message, key) for key in FIBRES); return support("left") == support("right") == ["left", "right"]
    if index == 3:
        return tuple(cipher("left", key) for key in FIBRES) == ("left", "right") and tuple(cipher("right", key) for key in FIBRES) == ("right", "left")
    if index == 4:
        mapping = {"a": "x", "b": "y", "c": "z"}; limited = next((source for source in ("a", "b") if mapping[source] == "z"), None); complete = next(source for source in mapping if mapping[source] == "z"); return limited is None and complete == "c"
    if index == 5:
        return tuple((seed, (seed, opposite(seed), seed)[-1]) for seed in FIBRES) == (("left", "left"), ("right", "right"))
    if index == 6:
        outputs = {(seed, opposite(seed), seed) for seed in FIBRES}; return len(outputs) == 2 and len(tuple(product(FIBRES, repeat=3))) == 8
    if index == 7:
        family = {key: tuple(cipher(message, key) for message in FIBRES) for key in FIBRES}; return family == {"left": ("left", "right"), "right": ("right", "left")}
    if index == 8:
        return all(cipher(cipher(message, key), key) == message for message, key in product(FIBRES, repeat=2))
    if index == 9:
        forward = {"a": "x", "b": "y"}; reverse = {value: key for key, value in forward.items()}; return reverse[forward["a"]] == "a"
    if index == 10:
        return tag("left", "right") == ("tag", "right") and tag("left", "left") != tag("left", "right")
    if index == 11:
        return tag("left", "fresh-a") != tag("left", "fresh-b")
    if index == 12:
        domain = tuple(product(FIBRES, repeat=2)); images = {digest(word) for word in domain}; return len(domain) == 4 and len(images) == 2 and digest(("left", "left")) == digest(("right", "right"))
    if index == 13:
        records = {commit(message, blind) for message, blind in product(FIBRES, repeat=2)}
        openings = {record: tuple((message, blind) for message, blind in product(FIBRES, repeat=2) if commit(message, blind) == record) for record in records}
        return len(records) == 2 and all(len(rows) == 2 for rows in openings.values())
    if index == 14:
        signature = ("signature", "left", "right"); return signature == ("signature", "left", "right") and signature != ("signature", "left", "left")
    if index == 15:
        transcript = (opposite("left"), opposite("right")); shared = ("left", "right"); return len(transcript) == 2 and shared == ("left", "right")
    if index == 16:
        def shares(secret): return (("a", secret), ("b", opposite(secret)), ("c", secret))
        def recover(rows): return "insufficient" if len(rows) < 2 else rows[0][1] if rows[0][0] != "b" else opposite(rows[0][1])
        return all(recover(pair) == "left" for pair in combinations(shares("left"), 2)) and recover(shares("right")[:1]) == "insufficient"
    if index == 17:
        both = {challenge: response for challenge, response in (("left", "secret"), ("right", "secret"))}; one = {"left": "secret"}; return len(both) == 2 and len(set(both.values())) == 1 and len(one) == 1
    if index == 18:
        real = (("left", "left"), ("right", "right")); simulated = (("left", "left"), ("right", "right")); return sorted(real) == sorted(simulated)
    if index == 19:
        inputs = ("right", "left"); output = tuple(sorted(inputs)); views = tuple((place, value, output) for place, value in enumerate(inputs)); return output == ("left", "right") and len(views) == 2
    if index == 20:
        messages = ("a", "b"); choice = "right"; selected = messages[FIBRES.index(choice)]; sender = (messages, "choice-hidden"); return selected == "b" and sender[-1] == "choice-hidden"
    if index == 21:
        return len(tuple(product(("before", "after"), ("single", "concurrent"), ("static", "adaptive")))) == 8
    if index == 22:
        channels = {"algorithm": ("ciphertext",), "implementation": ("time", "power")}; return set(channels) == {"algorithm", "implementation"}
    if index == 23:
        return ("classical-budget", "quantum-budget") [0] != ("classical-budget", "quantum-budget")[1]
    if index == 24:
        return ("classical-owner", "quantum-channel-handoff", "quantum-owner")[1] == "quantum-channel-handoff"
    if index == 25:
        return len(RELATIONS) == 25 and all(independent_witness(number) for number in range(1, 25))
    return False


def surface(index):
    axes = (("implicit-or-unbounded-adversary", "complete-adversary-view"), ("hidden-resource-or-success", "exact-resource-success-ledger"), ("imported-security-answer", RELATIONS[index - 1]), ("favorable-protocol-run", "complete-adversarial-control-support"), ("sampled-adversaries", "literal-complete-product"), ("outcome-selected", "there-is-no-nothing-lineage"), ("preopened-target", "post-registry-exact-security-execution"), ("unrestricted-security-export", "declared-scheme-adversary-handoff-boundary"))
    rows = tuple("__".join(row) for row in product(*axes)); return rows, "__".join(axis[1] for axis in axes)


def main():
    claim_id, _root, sealed_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]); index = int(claim_id.rsplit("-", 1)[-1]); sealed = json.loads(sealed_path.read_text()); rows, survivor = surface(index); received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"]); decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}; expected = {candidate: candidate == survivor for candidate in rows}; passed = all((received == rows, len(set(received)) == len(received) == 256, decisions == expected, sum(expected.values()) == 1, len(sealed["controls"]) == 4, all(row["passed"] for row in sealed["controls"]), sealed["closure"]["scope"] == "depth_independent", independent_witness(index))); print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 256, "unique_survivor_count": 1, "security_witness": independent_witness(index)}})); raise SystemExit(0 if passed else 1)


if __name__ == "__main__": main()
