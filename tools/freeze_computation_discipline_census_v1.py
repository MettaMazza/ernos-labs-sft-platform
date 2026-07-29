#!/usr/bin/env python3
"""Freeze the value-free complete-field Classical Computational Science census."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/computation_discipline_obligations.json"


FAMILIES = {
    "FORMX": """
Configuration identity and canonical state encoding
Partial and total transition relations
Acceptance, rejection and nontermination distinction
Language union, intersection and complement correspondence
Concatenation, iteration and generated-language closure
Grammar derivation trees and ambiguity custody
Parsing, recognition and generation correspondence
Automaton product, quotient and minimization
Finite-state transduction and output custody
Stack, queue and register storage correspondence
Rewriting termination and normal forms
Rewriting confluence and critical-pair custody
Recursive composition and finite iteration
Primitive recursion and minimization correspondence
Lambda reduction, capture avoidance and normal forms
Abstract-machine simulation invariants
Circuit fan-in, fan-out and acyclic evaluation
Sequential and combinational process correspondence
Process algebra composition and observational equivalence
Universal interpreter and self-interpretation
Effective model translation and overhead custody
Formal-computation completeness certificate
""",
    "CBLX": """
Decidable and recognizable language closure
Recognizable and co-recognizable decision boundary
Effective enumeration and dovetailing
Diagonal language construction
Self-reference and fixed-point construction
Recursion-theorem correspondence
Semantic-property undecidability boundary
Many-one reduction and composition
Turing-style reduction correspondence
Enumeration reducibility correspondence
Computability degree ordering
Jump and relative-computation succession
Oracle answer-record custody
Arithmetical-hierarchy correspondence boundary
Post-correspondence finite witness boundary
Entscheidungsproblem correspondence boundary
Incompleteness and internal consistency boundary
Busy-Beaver domination theorem
Finite Busy-Beaver census protocol
Hypercomputation admissibility and physical-record boundary
Computability completeness and no-omission certificate
""",
    "CPLXX": """
Canonical input-length and instance-family carrier
Deterministic time-class correspondence
Deterministic space-class correspondence
Time and space hierarchy succession
Nondeterministic support as complete deterministic branch support
Certificate length and verification resource
Fold-P and Fold-NP scoped equality boundary
Conventional P-versus-NP transport boundary
Co-decision and complement-class correspondence
Polynomial-space and alternating-process correspondence
Exponential-resource succession
Circuit family uniformity and nonuniformity
Circuit size, depth and width trade ledger
Formula, branching-program and circuit correspondence
Parallel depth and processor work
Communication rounds and transmitted distinctions
Decision-tree and query lower bounds
Randomized resource as unresolved deterministic support
Derandomization correspondence boundary
Counting-complexity support correspondence
Reduction closure and complete-problem construction
Upper-bound witness and exact resource certificate
Lower-bound adversary and indistinguishability certificate
Arbitrary circuit lower-bound theorem boundary
Worst-case, average-case and distribution custody
Approximation ratio as exact-part relation
Parameterized size and fixed-parameter resource
Kernelization correspondence boundary
Amortized and aggregate resource accounting
Online competitive-resource correspondence
Description and program-size complexity
Reversible time-space-record tradeoff
Complexity-family completeness certificate
""",
    "ALGX": """
Algorithm specification, invariant and termination certificate
Exact linear and ordered search
Comparison sorting and permutation custody
Noncomparison ordering correspondence
Integer addition, multiplication and division algorithms
Greatest-common-part and modular arithmetic algorithms
Exact rational-part arithmetic algorithms
String matching and finite-pattern search
Sequence alignment and edit structure
Tree traversal, balancing and search organization
Graph traversal and reachability
Shortest-path and path-composition algorithms
Spanning-tree and connectivity algorithms
Network flow and cut algorithms
Matching and assignment algorithms
Algebraic elimination and exact linear solving
Polynomial and symbolic algebra algorithms
Computational geometry orientation and intersection
Convex-hull and spatial-order algorithms
Dynamic-programming optimal-substructure law
Greedy-choice admissibility boundary
Combinatorial optimization and branch-and-bound
Randomized algorithm complete-support execution
Parallel work-depth algorithm law
Distributed local-state algorithm law
Online decision and competitive ledger
Streaming memory and approximation ledger
Numerical iteration with exact error custody
Symbolic simplification and equivalence custody
Approximation scheme and guarantee certificate
Algorithm and data-organization completeness certificate
""",
    "SEMX": """
Abstract syntax trees and well-formed program terms
Free, bound and scoped-name distinction
Alpha-equivalence and lawful renaming
Capture-avoiding substitution
Small-step operational evaluation
Big-step operational evaluation
Evaluation-context composition
Denotational meaning as compositional Fold map
Operational-denotational adequacy
Full-abstraction correspondence boundary
Type formation, introduction and elimination
Type checking and type inference correspondence
Polymorphism and parametricity boundary
Dependent evidence and proposition-as-type correspondence
State, effect and exception semantics
Contextual equivalence and bisimulation
Termination measure and well-founded descent
Partial correctness and total correctness
Assertion logic and invariant preservation
Formal specification and refinement ordering
Program transformation and optimization correctness
Compiler pass simulation and semantic preservation
Intermediate-language composition
Proof-carrying program and certificate checking
Semantics and programming-theory completeness certificate
""",
    "DISTX": """
Event identity and local process order
Concurrent interleaving and partial-order equivalence
Happens-before causality relation
Message send, receipt and channel custody
Synchronous and asynchronous execution boundary
Mutual exclusion and critical-section safety
Deadlock, livelock and progress distinction
Barrier, semaphore and rendezvous correspondence
Logical clock and causal timestamp correspondence
Broadcast, multicast and point-to-point communication
Failure-free consensus construction
Crash-fault consensus boundary
Byzantine-fault agreement boundary
Hidden-predecessor agreement impossibility
Failure detector and synchrony-assumption custody
Replication and state-machine correspondence
Linearizable and sequential consistency boundary
Causal and eventual consistency boundary
Quorum intersection and replicated decision
Distributed transaction atomicity boundary
Local, shared and common knowledge distinction
Locality radius and information-propagation lower bound
Network topology and distributed computability
Dynamic-network and partition custody
Distributed safety, liveness and fairness certificate
Concurrent and distributed completeness certificate
""",
    "SECX": """
Adversary, view, resource and success-event definition
Information-theoretic secrecy
Computational indistinguishability correspondence
One-way transformation and inversion resource
Hard-core distinction correspondence boundary
Pseudorandom generator support correspondence
Pseudorandom function correspondence
Symmetric encryption correctness and secrecy
Public-key encryption correspondence boundary
Message authentication and integrity
Entity authentication and freshness
Hash compression, preimage and collision properties
Commitment hiding and binding
Digital signature correctness and unforgeability
Key establishment and authenticated exchange
Secret sharing and reconstruction threshold
Proof of knowledge and extractor boundary
Zero-knowledge simulator correspondence
Secure multiparty computation and view custody
Oblivious-transfer correspondence boundary
Adaptive, concurrent and composable adversaries
Side-channel information ownership handoff
Post-quantum security reduction boundary
Quantum cryptography ownership handoff
Cryptographic security completeness certificate
""",
    "LEARNX": """
Learning problem, example and target identity
Hypothesis family generation and representation
Exact loss and risk as parts of a finite whole
Training, validation and held-out observation custody
Empirical-risk minimization boundary
Generalization as unseen-support preservation
Sample complexity from distinguishability count
Capacity and shattering correspondence boundary
Probably-approximately-correct correspondence
Classification and decision-boundary computation
Regression as exact representative relation
Feature selection and sufficient representation
Unsupervised partition and clustering custody
Generative-support reconstruction boundary
Deterministic-support Bayesian correspondence
Learning optimization and convergence certificate
Online learning and regret as exact ledger
Concept drift and adaptation
Search, planning and heuristic admissibility
Reinforcement state, action and return custody
Multi-agent learning and strategic observation
Interpretability as reconstructible decision trace
Robustness, distribution shift and adversarial examples
Verification of learned-process behavior
No-free-lunch and identifiability limits
Computational learning completeness certificate
""",
    "SCIX": """
Exact and approximate result distinction
Finite-precision representation correspondence
Rounding and truncation error ledger
Forward and backward error
Conditioning and sensitivity
Numerical stability under composition
Convergence order and stopping certificate
Discretization and consistency
Interpolation and approximation custody
Quadrature and exact residual bounds
Root-finding and interval custody
Exact and approximate linear-system solving
Eigenvalue and mode computation boundary
Ordinary differential-system discretization
Partial differential-system discretization
Stochastic-simulation deterministic-support correspondence
Monte-Carlo support and sampling correspondence
Inverse-problem identifiability and regularization boundary
Computational statistics and estimator custody
High-dimensional and sparse computation
Many-body state-space organization
Symbolic-numeric correspondence
Simulation verification and validation
Reproducible mathematical-model provenance
Scientific-computation completeness certificate
""",
    "VALID": """
Formal-computation complete validation vector
Computability complete validation vector
Complexity complete validation vector
Algorithms and data-organization complete validation vector
Semantics and programming-theory complete validation vector
Concurrency and distributed complete validation vector
Cryptography and security complete validation vector
Learning and intelligence complete validation vector
Scientific-computation complete validation vector
Famous-problem theorem and finite-census boundary vector
Adverse, absent, unresolved and ownership-boundary vector
Classical Computational Science empirical and formal Grand Lock
""",
    "HAND": """
Classical Computation one-owner downstream handoff
Classical Computation measurement-boundary handoff
Classical Computation formal-to-empirical handoff
Classical-to-quantum operational handoff
Classical Computation open-extension handoff
Classical Computation cross-branch completeness certificate
""",
}


PREFIX_TO_SUBBRANCH = {
    "FORM": "formal_computation",
    "CBL": "computability",
    "CPLX": "complexity",
    "ALG": "algorithms_and_data_structures",
    "SEM": "semantics_and_programming_theory",
    "DIST": "concurrent_and_distributed_computation",
    "SEC": "cryptography_and_security",
    "LEARN": "learning_and_intelligence",
    "SCI": "scientific_computation",
}


def canonical(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def claim_subbranch(claim_id: str) -> str:
    fields = claim_id.split("-")
    if len(fields) < 4 or fields[0:2] != ["SFT", "COMP"]:
        raise SystemExit(f"unrecognized Classical Computation claim identity: {claim_id}")
    try:
        return PREFIX_TO_SUBBRANCH[fields[2]]
    except KeyError as exc:
        raise SystemExit(f"unowned Classical Computation prefix in {claim_id}") from exc


def main():
    if OUT.exists():
        raise SystemExit("Classical Computation discipline census already frozen")
    rows = json.loads((ROOT / "census/claims.json").read_text())["claims"]
    base = [row for row in rows if row.get("branch") == "computation"]
    if len(base) != 117:
        raise SystemExit(f"expected 117 admitted Classical Computation base claims, found {len(base)}")
    if any(not row.get("model_admitted") for row in base):
        raise SystemExit("Classical Computation base contains a non-admitted claim")

    obligations = []
    base_coverage = Counter()
    for index, row in enumerate(base, 1):
        subbranch = claim_subbranch(row["claim_id"])
        base_coverage[subbranch] += 1
        obligations.append({
            "obligation_id": f"SFT-COMP-OBL-BASE-{index:03d}",
            "family": "BASE",
            "subbranch": subbranch,
            "title": row["title"],
            "exact_boundary": row["statement"],
            "owner": "computation",
            "status": "closed_current_model_admitted_receipt",
            "current_claim_ids": [row["claim_id"]],
            "receipt_hashes": [row["receipt_hash"]],
            "receipt_paths": [row["receipt_path"]],
            "required_strength": "existing_exact_unique_survivor_independent_reconstruction",
            "required_external_surface": "existing receipt-bound formal or empirical package",
        })

    for family, text in FAMILIES.items():
        titles = tuple(line.strip() for line in text.strip().splitlines() if line.strip())
        for index, title in enumerate(titles, 1):
            obligations.append({
                "obligation_id": f"SFT-COMP-OBL-{family}-{index:03d}",
                "family": family,
                "title": title,
                "exact_boundary": (
                    f"Derive {title.lower()} from exact generated Fold states, transitions, held records and "
                    "finite resource ledgers; enumerate the complete declared grammar; preserve every "
                    "distinction closed by observation or irreversible merging; and prove the finite-successor, "
                    "depth-independent or explicit correspondence boundary without fitted parameters."
                ),
                "owner": "computation",
                "status": "open_registered_question",
                "current_claim_ids": [],
                "receipt_hashes": [],
                "receipt_paths": [],
                "required_strength": "exact_unique_survivor_depth_certificate_independent_reconstruction_and_external_comparison_where_possible",
                "required_external_surface": "post-registry exact computational observations, prior-corpus observations and authoritative external computation records where available",
            })

    family_counts = {
        "BASE": len(base),
        **{
            family: len(tuple(line for line in text.strip().splitlines() if line.strip()))
            for family, text in FAMILIES.items()
        },
    }
    payload = {
        "schema": "sft-v3-classical-computation-discipline-question-census/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "branch": "computation",
        "frozen": True,
        "frozen_before_new_target_outcome_access": True,
        "target_content_present": False,
        "base_claim_count": len(base),
        "base_subbranch_counts": dict(sorted(base_coverage.items())),
        "closed_obligation_count_at_freeze": len(base),
        "registered_obligation_count": len(obligations),
        "open_obligation_count_at_freeze": len(obligations) - len(base),
        "family_order": ("BASE",) + tuple(FAMILIES),
        "family_counts": family_counts,
        "completion_rule": "Every obligation requires its own untouched-engine receipt; no partial family is counted complete; closure is dated, exact for the registered census and open to lawful versioned extension.",
        "ownership_boundary": "Classical Computational Science owns formal and classical processes, computability, complexity, algorithms, semantics, distributed computation, computational security, learning theory and scientific computation. Quantum operational laws remain with Quantum Computation; mathematical carrier laws remain with Mathematics; physical realizations and engineered implementations remain with their owning branches.",
        "extension_policy": "complete to the current registered standard and open to lawful versioned extension",
        "obligations": obligations,
    }
    payload["census_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "path": OUT.relative_to(ROOT).as_posix(),
        "base": len(base),
        "base_subbranch_counts": dict(sorted(base_coverage.items())),
        "registered": len(obligations),
        "open": len(obligations) - len(base),
        "family_counts": family_counts,
        "identity": payload["census_identity"],
    }, indent=2))


if __name__ == "__main__":
    main()
