#!/usr/bin/env python3
"""Build the atomic V1/V2 obligation ledger for the Foundation branch.

The prior sources are observational reconstruction requirements, never executable
premises.  Composite rows are split here so that a Foundation component cannot
be hidden inside a Physics, Mathematics, Information or engine-method row.
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "audits/v1_theorem_manifest_observation_census.json"
V2 = ROOT / "audits/v2_407_step_observation_census.json"
OUTPUT = ROOT / "census/foundation_prior_obligations.json"

NEWLY_RECONSTRUCTED_ATOMS = {
    "V1-Q1-UNISON", "V1-Q2-FOLD-ACTION", "V1-Q7-UNIFORM-FOLD-INVARIANCE",
    "V1-Q11-DOMAIN-CLOSURE", "V1-Q13-PHASE-ANTIPODE", "V1-Q14-FOLD-FIBRE",
    "V2-003-EXACT-DOMAIN", "V2-003-CAST", "V2-003-FOLD", "V2-003-TAKE",
    "V2-003-TRACE", "V2-004-FORCING-ENFORCEMENT", "V2-024-HALF-ONE",
    "V2-024-SELF-COMPLEMENT", "V2-024-GROUND-FOLD", "V2-024-ONE-FIXED",
    "V2-025-PRIMITIVE-GRAMMAR", "V2-025-UNIQUE-GENERATOR",
    "V2-025-CONDITIONAL-SCOPE", "V2-182-ONE-FOLD-EQUATION",
    "V2-256-REPLAYABLE-DERIVATION", "V2-401-COMPOSITION-ENUMERATION",
    "V2-401-LEAST-SIZE-UNIQUENESS", "V2-401-GRAMMAR-BOUNDARY",
}


def atom(
    atomic_id: str,
    statement: str,
    owner: str,
    claims: tuple[str, ...] = (),
    closed: bool = False,
    reason: str = "",
) -> dict[str, object]:
    return {
        "atomic_obligation_id": atomic_id,
        "prior_observation": statement,
        "categorical_owner": owner,
        "v3_claim_ids": list(claims),
        "same_strength_closed": closed,
        "disposition": "closed" if closed else "open_reconstruction_required",
        "reason": reason,
    }


V1_DECOMPOSITION: dict[str, tuple[dict[str, object], ...]] = {
    "Q1": (
        atom("V1-Q1-ONE", "The One is the exact unity/whole.", "foundation", ("SFT-FOUNDATION-ONE-001",), True, "The structural One claim closes the exact self-whole identity."),
        atom("V1-Q1-POSITION", "A position is an exact positive part of the One.", "foundation", ("SFT-FOUNDATION-PART-001",), True, "The exact positive part-coordinate claim closes this component."),
        atom("V1-Q1-UNISON", "Unison is the exact identity relation of the One.", "foundation", ("SFT-FOUNDATION-EXACT-OPERATIONS-001",), False),
    ),
    "Q2": (atom("V1-Q2-FOLD-ACTION", "Fold doubles an exact part and casts out complete Ones.", "foundation", ("SFT-FOUNDATION-EXACT-OPERATIONS-001",), False),),
    "Q3": (
        atom("V1-Q3-RATIO", "The relation of two exact magnitudes is their positive ratio.", "mathematics"),
        atom("V1-Q3-SEPARATION", "Separation is the shorter exact positive part between two positions.", "mathematics"),
    ),
    "Q4": (atom("V1-Q4-FOLD-SUPPORT", "Each Fold successor appends both held fibre labels to every prior word.", "foundation", ("SFT-FOUNDATION-FOLD-ASSEMBLY-001", "SFT-FOUNDATION-COUNT-001"), True, "The depth-independent Fold-word base/successor certificate closes the generated support count without importing exponentiation."),),
    "Q5": (atom("V1-Q5-RECONSTRUCTION-INFORMATION", "One held fibre distinction is revealed per Fold and the retained word reconstructs the part.", "information_science"),),
    "Q6": (atom("V1-Q6-COUNT-MEASURE", "Generated support count and one-part measure compose to the One.", "mathematics"),),
    "Q7": (atom("V1-Q7-UNIFORM-FOLD-INVARIANCE", "A complete uniform division remains complete and uniform under Fold.", "foundation", ("SFT-FOUNDATION-FOLD-DYNAMICS-001",), False),),
    "Q8": (atom("V1-Q8-SEPARATION-DYNAMICS", "Local separation advances by the Fold factor before the cast boundary.", "mathematics"),),
    "Q9": (atom("V1-Q9-RELATIVE-VIEW-COMPOSITION", "Exact relative views compose and telescope.", "mathematics"),),
    "Q10": (atom("V1-Q10-HOLDING-THRESHOLD", "The m-fold holding threshold is the positive part (m less One)/m.", "mathematics"),),
    "Q11": (atom("V1-Q11-DOMAIN-CLOSURE", "Fold maps every admitted exact part back into the exact positive domain through the One.", "foundation", ("SFT-FOUNDATION-EXACT-OPERATIONS-001", "SFT-FOUNDATION-FOLD-DYNAMICS-001"), False),),
    "Q12": (atom("V1-Q12-RECIPROCAL-OPPOSITION", "A positive ratio composed with its reciprocal returns the One.", "mathematics"),),
    "Q13": (atom("V1-Q13-PHASE-ANTIPODE", "Half-One phase translation is the exact maximal positional separation.", "foundation", ("SFT-FOUNDATION-FOLD-DYNAMICS-001",), False),),
    "Q14": (atom("V1-Q14-FOLD-FIBRE", "A position and its half-One phase antipode are the two distinct preimages identified by Fold.", "foundation", ("SFT-FOUNDATION-FOLD-DYNAMICS-001",), False),),
}


V2_DECOMPOSITION: dict[int, tuple[dict[str, object], ...]] = {
    3: (
        atom("V2-003-EXACT-DOMAIN", "Every derivational magnitude is an exact positive part through the One and violations halt.", "foundation", ("SFT-FOUNDATION-EXACT-OPERATIONS-001",), False),
        atom("V2-003-ONE", "The exact whole is the One.", "foundation", ("SFT-FOUNDATION-ONE-001",), True),
        atom("V2-003-CAST", "Cast removes complete Ones and represents a full turn as the One rather than numerical zero.", "foundation", ("SFT-FOUNDATION-EXACT-OPERATIONS-001",), False),
        atom("V2-003-FOLD", "Fold is exact doubling followed by cast.", "foundation", ("SFT-FOUNDATION-EXACT-OPERATIONS-001",), False),
        atom("V2-003-TAKE", "Take is permitted only as a guarded positive difference from the strictly larger part.", "foundation", ("SFT-FOUNDATION-EXACT-OPERATIONS-001",), False),
        atom("V2-003-RHYTHM", "Fold return period, phase and beat are generated exact dynamical relations.", "mathematics"),
        atom("V2-003-TRACE", "Every generated value retains a replayable dependency trace to the One.", "foundation", ("SFT-FOUNDATION-DERIVATION-TRACE-001",), False),
    ),
    4: (
        atom("V2-004-PERIOD-SPECTRUM", "Fold periods of exact unit parts are generated and ordered without target selection.", "mathematics"),
        atom("V2-004-BINARY-GENERATOR", "The first non-One period is the binary generator.", "physics"),
        atom("V2-004-COLOUR-GENERATOR", "The next distinct period is the colour/generator-three count.", "physics"),
        atom("V2-004-COVER", "Covering depth is the first generated support that completely covers a registered volume.", "mathematics"),
        atom("V2-004-FORCING-ENFORCEMENT", "Admission halts unless the complete census has one forced survivor and no selection, fitting or domain breach occurs.", "foundation", ("SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001",), False),
        atom("V2-004-MEASUREMENT-BOUNDARY", "Measured targets cannot enter derivation and may open only at the one-way comparison boundary after sealing.", "foundation", ("SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",), True, "The one-way measured-value boundary closes this component."),
    ),
    24: (
        atom("V2-024-FOLD-FACTOR", "The minimal nontrivial Fold supplies exactly two held fibres.", "foundation", ("SFT-FOUNDATION-FOLD-001",), True),
        atom("V2-024-HALF-ONE", "There is one exact positive part whose self-junction is the One.", "foundation", ("SFT-FOUNDATION-HALF-ONE-001",), False),
        atom("V2-024-SELF-COMPLEMENT", "That half-One is the unique part equal to its complement within the One.", "foundation", ("SFT-FOUNDATION-HALF-ONE-001",), False),
        atom("V2-024-GROUND-FOLD", "Folding the half-One returns the One.", "foundation", ("SFT-FOUNDATION-HALF-ONE-001",), False),
        atom("V2-024-ONE-FIXED", "Folding the One returns the One.", "foundation", ("SFT-FOUNDATION-HALF-ONE-001",), False),
    ),
    25: (
        atom("V2-025-PRIMITIVE-GRAMMAR", "The declared size-at-most-two parameter-free self-map grammar has exactly four operational equivalence classes.", "foundation", ("SFT-FOUNDATION-PRIMITIVE-MAP-UNIQUENESS-001",), False),
        atom("V2-025-UNIQUE-GENERATOR", "Within that grammar only Fold is nonstatic, noncollapsing and recurrent, so least-size generation selects it uniquely.", "foundation", ("SFT-FOUNDATION-PRIMITIVE-MAP-UNIQUENESS-001",), False),
        atom("V2-025-CONDITIONAL-SCOPE", "The uniqueness theorem is explicitly conditional on its mechanically declared grammar and generator predicate.", "foundation", ("SFT-FOUNDATION-PRIMITIVE-MAP-UNIQUENESS-001",), False),
    ),
    27: (atom("V2-027-ORBIT-ORDER", "Fold return periods on unit parts coincide with the multiplicative order of the binary count.", "mathematics"),),
    182: (atom("V2-182-ONE-FOLD-EQUATION", "The first nonstatic recurrent Fold orbit has two phase-antipodal members and Fold composed twice is identity on that orbit.", "foundation", ("SFT-FOUNDATION-FOLD-DYNAMICS-001",), False),),
    219: (atom("V2-219-GENERAL-COVERING", "An m-labelled successor has m times the prior support at every generated finite depth.", "mathematics"),),
    256: (atom("V2-256-REPLAYABLE-DERIVATION", "A derivation is an exact ordered playthrough whose intermediates, dependencies and final identity can be independently replayed.", "foundation", ("SFT-FOUNDATION-DERIVATION-TRACE-001",), False),),
    401: (
        atom("V2-401-COMPOSITION-ENUMERATION", "Ordered compositions of the four primitive self-maps are mechanically enumerated through word size three as 4, 16 and 64 forms.", "foundation", ("SFT-FOUNDATION-PRIMITIVE-MAP-UNIQUENESS-001",), False),
        atom("V2-401-LEAST-SIZE-UNIQUENESS", "Larger compositions do not displace the uniquely generating least-size primitive Fold.", "foundation", ("SFT-FOUNDATION-PRIMITIVE-MAP-UNIQUENESS-001",), False),
        atom("V2-401-GRAMMAR-BOUNDARY", "The extended uniqueness result remains conditional on the explicit ordered-composition grammar.", "foundation", ("SFT-FOUNDATION-PRIMITIVE-MAP-UNIQUENESS-001",), False),
    ),
    402: (
        atom("V2-402-EMPTY-ONE-BASE", "The structural empty One word is the complete base support before a Fold.", "foundation", ("SFT-FOUNDATION-FOLD-ASSEMBLY-001",), True),
        atom("V2-402-TWO-LABEL-SUCCESSOR", "Each Fold successor appends both held labels exactly once to every prior word.", "foundation", ("SFT-FOUNDATION-FOLD-ASSEMBLY-001",), True),
        atom("V2-402-DERIVED-RESOURCE-RECURRENCES", "Information, circuit, quantum-support, reverse-record and channel recurrences inherit the same generated support successor.", "computation"),
    ),
}


def main() -> None:
    v1 = json.loads(V1.read_text(encoding="utf-8"))
    v2 = json.loads(V2.read_text(encoding="utf-8"))
    v1_rows = {row["v1_claim_id"]: row for row in v1["rows"]}
    v2_rows = {row["step"]: row for row in v2["steps"]}
    if set(V1_DECOMPOSITION) - set(v1_rows):
        raise SystemExit("Foundation V1 decomposition cites an absent bound source row")
    if set(V2_DECOMPOSITION) - set(v2_rows):
        raise SystemExit("Foundation V2 decomposition cites an absent bound source step")

    source_entries: list[dict[str, object]] = []
    for source_id, atoms in V1_DECOMPOSITION.items():
        row = v1_rows[source_id]
        source_entries.append({
            "source": "v1",
            "source_entry": source_id,
            "source_hash": row["source_row_sha256"],
            "source_observation": row["prior_result_observation"],
            "atomic_obligations": list(atoms),
        })
    for step, atoms in V2_DECOMPOSITION.items():
        row = v2_rows[step]
        source_entries.append({
            "source": "v2",
            "source_entry": step,
            "source_hash": row["source_block_sha256"],
            "source_observation": row["title"],
            "atomic_obligations": list(atoms),
        })

    admitted = {
        row["claim_id"]
        for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
        if row.get("model_admitted")
    }
    all_atoms = [item for entry in source_entries for item in entry["atomic_obligations"]]
    for item in all_atoms:
        if item["atomic_obligation_id"] not in NEWLY_RECONSTRUCTED_ATOMS:
            continue
        mapped = set(item["v3_claim_ids"])
        if not mapped or not mapped.issubset(admitted):
            raise SystemExit(
                "same-strength Foundation disposition lacks all mapped admitted claims: "
                + str(item["atomic_obligation_id"])
            )
        item["same_strength_closed"] = True
        item["disposition"] = "closed"
        item["reason"] = (
            "The mapped V3 claim or claims reconstruct this atomic prior observation "
            "at the registered exact formal strength and carry model-admitted receipts."
        )
    foundation_atoms = [item for item in all_atoms if item["categorical_owner"] == "foundation"]
    payload = {
        "schema": "sft-v3-foundation-prior-obligation-ledger/1",
        "status": "open" if any(not item["same_strength_closed"] for item in foundation_atoms) else "closed",
        "source_policy": {
            "prior_results_are_observational_reconstruction_requirements": True,
            "prior_executable_answers_are_not_derivational_inputs": True,
            "composite_rows_are_decomposed_without_dropping_nonfoundation_components": True,
            "one_owner_per_atomic_obligation": True,
        },
        "reviewed_source_surface": {
            "v1_total_rows": v1["source_row_count"],
            "v2_total_steps": v2["source_step_count"],
            "review_complete_for_branch_ownership": True,
            "reviewed_entry_count": v1["source_row_count"] + v2["source_step_count"],
            "foundation_relevant_v1_rows": list(V1_DECOMPOSITION),
            "foundation_relevant_v2_steps": list(V2_DECOMPOSITION),
            "reviewed_nonfoundation_v1_rows": [value for value in v1_rows if value not in V1_DECOMPOSITION],
            "reviewed_nonfoundation_v2_steps": [value for value in v2_rows if value not in V2_DECOMPOSITION],
        },
        "source_entries": source_entries,
        "foundation_summary": {
            "atomic_obligation_count": len(foundation_atoms),
            "same_strength_closed_count": sum(bool(item["same_strength_closed"]) for item in foundation_atoms),
            "open_count": sum(not bool(item["same_strength_closed"]) for item in foundation_atoms),
            "open_atomic_obligation_ids": [item["atomic_obligation_id"] for item in foundation_atoms if not item["same_strength_closed"]],
        },
    }
    exclusion_identity = json.dumps(
        {
            "v1": payload["reviewed_source_surface"]["reviewed_nonfoundation_v1_rows"],
            "v2": payload["reviewed_source_surface"]["reviewed_nonfoundation_v2_steps"],
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    payload["reviewed_source_surface"]["nonfoundation_exclusion_identity"] = (
        "sha256:" + hashlib.sha256(exclusion_identity).hexdigest()
    )
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"wrote {OUTPUT.relative_to(ROOT)}: "
        f"foundation={len(foundation_atoms)} open={payload['foundation_summary']['open_count']}"
    )


if __name__ == "__main__":
    main()
