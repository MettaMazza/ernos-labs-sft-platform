#!/usr/bin/env python3
"""Build the complete V1/V2 Information Science ownership ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "audits/v1_theorem_manifest_observation_census.json"
V2 = ROOT / "audits/v2_407_step_observation_census.json"
OUTPUT = ROOT / "census/information_science_prior_obligations.json"


def atom(atomic_id: str, statement: str, claims: tuple[str, ...], resolution: str = "reconstructed") -> dict[str, object]:
    return {
        "atomic_obligation_id": atomic_id,
        "prior_observation": statement,
        "categorical_owner": "information_science",
        "v3_claim_ids": list(claims),
        "resolution_kind": resolution,
        "same_strength_closed": False,
        "disposition": "open_reconstruction_required",
        "reason": "Every mapped V3 claim must carry a model-admitted receipt at the same declared boundary.",
    }


SD = ("SFT-INFO-SYMBOL-DISTINCTION-001",)
ED = ("SFT-INFO-ENCODING-DECODING-001",)
IQ = ("SFT-INFO-QUANTITY-001",)
EU = ("SFT-INFO-ENTROPY-UNCERTAINTY-001",)
CR = ("SFT-INFO-COMPRESSION-REDUNDANCY-001",)
CC = ("SFT-INFO-CHANNEL-CAPACITY-001",)
NE = ("SFT-INFO-NOISE-ERROR-001",)
CO = ("SFT-INFO-CODING-001",)
MI = ("SFT-INFO-MUTUAL-CONDITIONAL-001",)
CL = ("SFT-INFO-CONSERVATION-LOSS-001",)
CP = ("SFT-INFO-CLASSICAL-PROBABILISTIC-001",)
QC = ("SFT-INFO-QUANTUM-CORRESPONDENCE-001",)


V1_DECOMPOSITION: dict[str, tuple[dict[str, object], ...]] = {
    "Q5": (
        atom("V1-Q5-ONE-DISTINCTION-PER-FOLD", "One Fold observation closes exactly one native fibre distinction.", IQ),
        atom("V1-Q5-RECONSTRUCTION-LABELS", "The complete held fibre-label word reconstructs the exact source part.", ED),
    ),
    "Q6": (atom("V1-Q6-EQUAL-SHARE-PARTITION", "The complete generated state family carries exact equal parts whose total is the One.", CP),),
    "PH2": (atom("V1-PH2-ENTROPY-ANTILOG", "The Fold branch count and closed-distinction depth retain the exact finite object summarized by logarithmic entropy.", EU),),
    "D6": (atom("V1-D6-SUPPORT-UNCERTAINTY", "Conjugate finite supports obey an exact product lower bound fixed by complete generated support.", ("SFT-INFO-ENTROPY-UNCERTAINTY-001", "SFT-INFO-QUANTUM-CORRESPONDENCE-001")),),
    "N7": (
        atom("V1-N7-NONINJECTIVE-LOSS", "A two-predecessor Fold image closes the predecessor distinction unless its label is retained.", CL),
        atom("V1-N7-ENTROPY-COUNT", "Each further unresolved predecessor layer multiplies exact history support by the native fibre count.", EU),
    ),
    "C2s": (atom("V1-C2S-OBSERVATION-CLASS-BLIND-SPOT", "Two exact predecessors in one observation fibre are indistinguishable from the image alone.", SD),),
    "C5s": (atom("V1-C5S-ATOMIC-OBSERVATION-SYMBOL", "One native Fold observation returns one indivisible fibre label from the generated alphabet.", SD),),
    "C8s": (
        atom("V1-C8S-ANTIPODE-DISTINCTION", "The source-versus-antipode alternative is the exact distinction closed by one binary Fold observation.", SD),
        atom("V1-C8S-ITERATED-LOSS-LEDGER", "After a counted observation prefix, the same number of predecessor labels is required for exact reconstruction.", CL),
    ),
    "I-2": (
        atom("V1-I2-CONFIGURATION-SUPPORT", "Entropy retains the complete accessible finite configuration support and observation partition.", EU),
        atom("V1-I2-COMPOSITION-ACCOUNTING", "Independent generated supports compose multiplicatively while their distinction depths compose additively.", IQ),
    ),
    "I-10": (
        atom("V1-I10-ERASURE-MERGE", "Resetting a two-form record to one image closes exactly the source distinction.", CL),
        atom("V1-I10-REVERSE-RECORD", "Exact reversal of an erased binary record requires the predecessor fibre label.", CL),
    ),
    "G1": (
        atom("V1-G1-EXACT-BRANCH-PART", "Every member of complete finite support carries its exact part of the One without a stochastic cause premise.", CP),
        atom("V1-G1-MEASUREMENT-SUPPORT-BOUNDARY", "Observation maps complete unresolved support to an exact image class and a retained reconstruction record.", QC),
    ),
    "G3": (
        atom("V1-G3-CHANNEL-PROVENANCE", "A channel must retain the source, output and path relation for every declared message alternative.", CC),
        atom("V1-G3-QUANTUM-SUPPORT-BOUNDARY", "Classical held-word copying and unresolved quantum-support correspondence are distinct registered carriers.", QC),
    ),
}


V2_DECOMPOSITION: dict[int, tuple[dict[str, object], ...]] = {
    21: (
        atom("V2-021-ONE-DISTINCTION-LOSS", "A non-injective binary Fold step closes exactly one predecessor distinction.", CL),
        atom("V2-021-UNRESOLVED-HISTORY-GROWTH", "One further reverse layer multiplies the unresolved predecessor support by the native fibre count.", EU),
    ),
    22: (atom("V2-022-SUPPORT-UNCERTAINTY", "Exact conjugate support counts obey the registered finite support-product boundary.", ("SFT-INFO-ENTROPY-UNCERTAINTY-001", "SFT-INFO-QUANTUM-CORRESPONDENCE-001")),),
    28: (atom("V2-028-THERMODYNAMIC-INFORMATION-COMPONENT", "The second-law information component is exact predecessor merging and its closed-distinction ledger.", CL),),
    38: (
        atom("V2-038-EQUAL-BRANCH-SHARE", "At declared depth k, every generated branch has exact share one-of-b-to-k and the shares partition the One.", CP),
        atom("V2-038-ATOMIC-BRANCH-SUPPORT", "A measured branch is one exact member of complete generated finite support.", QC),
    ),
    98: (
        atom("V2-098-PREDECESSOR-FIBRE-LOSS", "The two-source Fold fibre closes exactly the pair distinction at its common image.", CL),
        atom("V2-098-ENTROPY-LEDGER", "The closed distinction and exact unresolved predecessor support are retained rather than replaced by a logarithm.", EU),
    ),
    123: (
        atom("V2-123-DEMON-RECORD-ERASURE", "Resetting the demon record is a registered many-to-one information transformation.", CL),
        atom("V2-123-RECORD-ACCOUNTING", "The erased source alternative remains recoverable only through an explicit retained predecessor label.", CL),
    ),
    159: (
        atom("V2-159-DEFINITE-SUPPORT-MEMBER", "Observation resolves complete finite support to one exact observation class member.", QC),
        atom("V2-159-SUPPORT-PARTITION", "All exact branch parts jointly reconstruct the One.", CP),
    ),
    192: (
        atom("V2-192-MERGER-LOSS", "Predecessor merging closes exact distinctions and has no image-only inverse.", CL),
        atom("V2-192-RECURRENT-CONSERVATION", "A complete recurrent orbit returns its held distinctions without additional merge loss.", CL),
    ),
    203: (
        atom("V2-203-BRANCH-COUNT-ENTROPY", "The exact predecessor count and one closed distinction per Fold supply the finite entropy object.", EU),
        atom("V2-203-DETERMINISTIC-EQUAL-SHARES", "Equal shares describe unresolved deterministic histories rather than stochastic transition causes.", CP),
    ),
    252: (
        atom("V2-252-COMPLETE-CHANNEL-CENSUS", "A channel claim requires a complete generated message/path relation with no undeclared signalling cell.", CC),
        atom("V2-252-STRUCTURAL-CHANNEL-BOUNDARY", "Quantum-support correlation and a message-carrying classical relation remain distinct carriers.", QC),
    ),
    257: (atom("V2-257-OBSERVATION-IS-FOLD", "The native observation relation is the already-forced Fold fibre, not an added observer postulate.", SD),),
    326: (
        atom("V2-326-OBSERVATION-CLASSES", "Exact observation classes are the complete predecessor fibres of the Fold map.", SD),
        atom("V2-326-RETAINED-CLOSED-DISTINCTIONS", "An image retains class identity while predecessor identity is closed unless recorded.", IQ),
    ),
    328: (
        atom("V2-328-FORCED-ALPHABET", "The native symbol alphabet is generated by the exact positions in one Fold fibre.", SD),
        atom("V2-328-ROUNDTRIP-CODE", "Generated fibre-label words encode and decode every exact state bijectively.", ED),
        atom("V2-328-OBSERVATION-SUFFIX", "Observation closes the first label and retains the exact suffix class.", ED),
    ),
    329: (
        atom("V2-329-INFORMATION-DEPTH", "Information quantity is exact generated distinction depth with multiplicity b-to-k.", IQ),
        atom("V2-329-RETAINED-CLOSED-SUM", "Retained and closed distinction counts exactly reconstruct the initial depth.", CL),
        atom("V2-329-EQUAL-SHARE-PARTITION", "Every generated state carries one exact equal share and all shares reconstruct the One.", CP),
        atom("V2-329-UNCERTAINTY-SUPPORT", "Retained image support times unresolved history support reconstructs complete source support.", EU),
        atom("V2-329-MERGER-RECURRENCE", "Dyadic merging closes a distinction while complete recurrence retains its orbit distinctions.", CL),
    ),
    348: (
        atom("V2-348-RANDOMNESS-AS-UNRESOLVED-SUPPORT", "Randomness quantity is the exact unresolved deterministic predecessor support of an observation class.", CP),
        atom("V2-348-HELD-LABEL-RESOLUTION", "Supplying the held labels deterministically resolves one exact source.", ED),
    ),
    349: (
        atom("V2-349-MINIMAL-REVERSE-RECORD", "Reversing s binary mergers requires exactly s held fibre labels.", CL),
        atom("V2-349-MISSING-LABEL-AMBIGUITY", "Omitting one required reverse label leaves an exact binary predecessor ambiguity.", MI),
    ),
    356: (atom("V2-356-CONDITIONAL-DESCRIPTION", "Relative to a known observed suffix, the minimal exact source description is the closed-label record.", CR),),
    384: (
        atom("V2-384-CLOSED-DISTINCTION-ENTROPY", "Entropy is the exact closed-distinction ledger after a declared observation prefix.", EU),
        atom("V2-384-EQUAL-HISTORY-SHARES", "Each unresolved deterministic history has its exact equal support part.", CP),
        atom("V2-384-SUPPORT-PRODUCT", "Retained image support times unresolved history support equals complete source support.", EU),
    ),
    385: (
        atom("V2-385-COMPRESSED-RECORD", "Relative to a known suffix, the closed-label prefix is a complete reconstructive record.", CR),
        atom("V2-385-RECONSTRUCTION", "Joining record and suffix recovers every exact source word.", ED),
        atom("V2-385-MINIMALITY", "Any shorter generated record family cannot distinguish all compatible histories.", CR),
    ),
    386: (
        atom("V2-386-ONE-USE-CAPACITY", "One native channel use carries exactly one generated fibre distinction.", CC),
        atom("V2-386-COMPOSED-CAPACITY", "u composed uses carry the complete b-to-u message-word family.", CC),
        atom("V2-386-CHANNEL-ROUNDTRIP", "Complete encode, path and decode relations preserve every declared message.", CC),
    ),
    387: (
        atom("V2-387-NOISE-TRANSFORMATION", "Noise is a registered exact change of a transmitted fibre label.", NE),
        atom("V2-387-ERROR-LEDGER", "Error is the complete changed-position ledger between equal-length words.", NE),
        atom("V2-387-OBSERVATION-VISIBILITY", "A changed retained label remains distinguishable while a changed closed label requires the predecessor record.", NE),
    ),
    388: (
        atom("V2-388-MINIMAL-ONE-ERROR-WIDTH", "Exhaustive width generation forces binary repetition width three as the first one-error-correcting majority code.", CO),
        atom("V2-388-EXHAUSTIVE-CORRECTION", "Every single-position corruption of every encoded word decodes to its unique source.", CO),
        atom("V2-388-REDUNDANCY", "Code length and redundancy follow exactly from the forced repetition width and source length.", CO),
    ),
    389: (
        atom("V2-389-MUTUAL-RETAINED", "Mutual information is the exact distinctions retained jointly with the observed suffix.", MI),
        atom("V2-389-CONDITIONAL-CLOSED", "Conditional source information is the exact closed-label record required given that suffix.", MI),
        atom("V2-389-CHAIN-IDENTITY", "Retained and conditional distinctions reconstruct the complete source depth.", MI),
    ),
    390: (
        atom("V2-390-CLASSICAL-SINGLETON", "A classical exact state is one held generated word with singleton support.", CP),
        atom("V2-390-PROBABILISTIC-CLASS", "A probabilistic description is an exact unresolved observation class over deterministic support.", CP),
        atom("V2-390-QUANTUM-SUPPORT", "Quantum-information correspondence retains the complete generated finite alternative support and basis trace.", QC),
        atom("V2-390-MEASUREMENT-RECORD", "An observation suffix plus held predecessor labels reconstructs one exact source branch.", QC),
    ),
    402: (
        atom("V2-402-INFORMATION-SUCCESSOR", "Prepending one native label multiplies generated support by b and adds one exact distinction.", IQ),
        atom("V2-402-CAPACITY-SUCCESSOR", "The same base/successor certificate extends retained/closed support products and channel capacity to every supplied finite depth.", CC),
    ),
}


def main() -> None:
    v1 = json.loads(V1.read_text(encoding="utf-8")); v2 = json.loads(V2.read_text(encoding="utf-8"))
    v1_rows = {row["v1_claim_id"]: row for row in v1["rows"]}; v2_rows = {row["step"]: row for row in v2["steps"]}
    if set(V1_DECOMPOSITION) - set(v1_rows): raise SystemExit("Information Science V1 decomposition cites an absent row")
    if set(V2_DECOMPOSITION) - set(v2_rows): raise SystemExit("Information Science V2 decomposition cites an absent step")
    entries: list[dict[str, object]] = []
    for source_id, atoms in V1_DECOMPOSITION.items():
        row = v1_rows[source_id]
        entries.append({"source": "v1", "source_entry": source_id, "source_hash": row["source_row_sha256"], "source_observation": row["prior_result_observation"], "atomic_obligations": list(atoms)})
    for step, atoms in V2_DECOMPOSITION.items():
        row = v2_rows[step]
        entries.append({"source": "v2", "source_entry": step, "source_hash": row["source_block_sha256"], "source_observation": row["prior_result_observation"], "atomic_obligations": list(atoms)})
    admitted = {row["claim_id"] for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"] if row.get("model_admitted")}
    atoms = [item for entry in entries for item in entry["atomic_obligations"]]
    for item in atoms:
        mapped = set(item["v3_claim_ids"])
        if mapped and mapped.issubset(admitted):
            item["same_strength_closed"] = True
            item["disposition"] = "closed" if item["resolution_kind"] == "reconstructed" else item["resolution_kind"]
            item["reason"] = "Every mapped V3 claim carries a model-admitted, independently validated receipt at the exact registered boundary."
    open_atoms = [item for item in atoms if not item["same_strength_closed"]]
    noninfo_v1 = [key for key in v1_rows if key not in V1_DECOMPOSITION]
    noninfo_v2 = [key for key in v2_rows if key not in V2_DECOMPOSITION]
    exclusion = json.dumps({"v1": noninfo_v1, "v2": noninfo_v2}, separators=(",", ":"), sort_keys=True).encode()
    payload = {
        "schema": "sft-v3-information-science-prior-obligation-ledger/1",
        "status": "closed" if not open_atoms else "open",
        "measurement_boundary": {
            "formal_branch_has_natural_measured_value": False,
            "applicable_external_validation": "implementation-distinct exact regeneration of every candidate, decision, survivor, control and certificate",
            "downstream_empirical_components_retained": ["thermodynamic heat and entropy measurements: physics", "Born and measurement dynamics: physics and quantum_computation", "physical uncertainty observables: physics", "operational no-cloning and fault tolerance: quantum_computation"],
        },
        "source_policy": {"prior_results_are_observational_reconstruction_requirements": True, "prior_executable_answers_are_not_derivational_inputs": True, "composite_rows_are_decomposed": True, "downstream_empirical_components_are_not_erased_or_prematurely_claimed": True},
        "reviewed_source_surface": {
            "v1_total_rows": v1["source_row_count"], "v2_total_steps": v2["source_step_count"], "review_complete_for_branch_ownership": True,
            "reviewed_entry_count": v1["source_row_count"] + v2["source_step_count"],
            "information_science_relevant_v1_rows": list(V1_DECOMPOSITION), "information_science_relevant_v2_steps": list(V2_DECOMPOSITION),
            "reviewed_noninformation_v1_rows": noninfo_v1, "reviewed_noninformation_v2_steps": noninfo_v2,
            "noninformation_exclusion_identity": "sha256:" + hashlib.sha256(exclusion).hexdigest(),
        },
        "source_entries": entries,
        "information_science_summary": {
            "atomic_obligation_count": len(atoms), "same_strength_closed_count": len(atoms) - len(open_atoms), "open_count": len(open_atoms),
            "open_atomic_obligation_ids": [item["atomic_obligation_id"] for item in open_atoms],
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}: information_science={len(atoms)} open={len(open_atoms)}")


if __name__ == "__main__": main()
