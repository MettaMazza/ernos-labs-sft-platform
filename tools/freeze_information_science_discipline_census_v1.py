#!/usr/bin/env python3
"""Freeze the value-free complete-field Information Science question census."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/information_science_discipline_obligations.json"

FAMILIES = {
    "SYMREP": """
Canonical alphabet generation
Symbol identity and distinguishability
Codeword formation and parsing
Prefix, uniquely decodable and instantaneous structure
Grammar-constrained representation
Representation equivalence and isomorphism
Canonicalization and normalization
Variable-length representation boundaries
Composite and product alphabets
Hierarchical and typed symbols
Representation conversion and transduction
Ambiguity detection and retained alternatives
Finite-alphabet successor law
Representation completeness and no-omission certificate
""",
    "RECORD": """
Data item and record identity
Field, tuple and relation organization
Metadata as retained interpretive record
Schema and type custody
Provenance chain composition
Integrity and tamper evidence
Version and revision identity
Missing, absent and unknown distinctions
Duplicate and alias resolution
Record linkage and identity boundaries
Dataset completeness and omission ledger
Record custody and reproducibility certificate
""",
    "SOURCE": """
Finite source-support generation
Sequence information and retained order
Process information and transition custody
Spatial information and adjacency custody
Network information and path custody
Source refinement and coarsening
Stationary-support correspondence
Nonstationary-support correspondence
Memoryless-source correspondence
Finite-memory source structure
Joint-source composition
Source dependence and common support
Source extension by exact successor
Source completeness and boundary certificate
""",
    "MEASURE": """
Distinction-count information measure
Combinatorial information quantity
Operational discrimination cost
Description length on a fixed grammar
Algorithmic-description correspondence boundary
Partition refinement information order
Additivity on independent product support
Subadditivity under shared support
Monotonicity under observation coarsening
Exact information balance ledger
Relative information between observations
Information divergence correspondence
Information geometry on exact parts
Multi-scale information decomposition
Measure conversion and unit custody
Information-measure completeness certificate
""",
    "SIGNAL": """
Signal as an ordered observation record
Amplitude-label and support separation
Sampling as retained position selection
Exact finite sampling sufficiency
Aliasing as closed distinction
Quantization as observation partition
Quantization error custody
Reconstruction from complete retained samples
Interpolation correspondence boundary
Transform representation of finite signals
Time-frequency support correspondence
Spatial and multidimensional sampling
Signal-to-record provenance
Sampling and reconstruction completeness certificate
""",
    "COMP": """
Lossless code and exact reconstruction
Prefix-tree compression structure
Dictionary compression structure
Run and recurrence compression
Transform compression correspondence
Source-model compression boundary
Redundancy as retained excess distinction
Minimum description within a fixed grammar
Lossy compression as declared coarsening
Exact distortion relation
Rate-distortion correspondence boundary
Successive and layered refinement
Compression under side information
Compression completeness and adverse-control certificate
""",
    "CHAN": """
Channel as an exact input-output relation
Deterministic channel transport
Observation-relative channel equivalence
Single-user channel capacity
Resource-bounded channel capacity
Noiseless channel composition
Cascaded channel capacity boundary
Parallel channel composition
Feedback channel correspondence
Multiple-access channel support
Broadcast channel support
Relay channel support
Interference-channel support
Bidirectional channel support
Network channel and cut boundary
Finite-use capacity succession
Channel simulation correspondence
Channel-family completeness certificate
""",
    "NOISE": """
Noise as unrecorded distinction closure
Error as source-output mismatch
Deterministic noise-pattern support
Noise transport through composition
Error detection condition
Error localization condition
Error estimation condition
Erasure and substitution distinction
Burst and correlated error structure
Adversarial error support
Noise budget and exact error ledger
Noise-family completeness certificate
""",
    "CODE": """
Code as injective representation relation
Minimum separation and correctability
Block-code structure
Linear-code correspondence
Parity and syndrome records
Repetition and majority structure
Erasure-correcting structure
Substitution-error correction
Burst-error correction
Convolutional-code correspondence
Tree and sequential decoding
Product and concatenated codes
Sparse-check code correspondence
Network coding structure
List-decoding boundary
Adversarial coding boundary
Code composition and rate custody
Coding-family completeness certificate
""",
    "REL": """
Joint information support
Conditional information by exact restriction
Mutual information by shared distinctions
Chain rule for retained information
Data-processing monotonicity
Conditional independence support
Common information correspondence
Directed information on ordered records
Interaction information correspondence
Multi-information and total dependence
Shared, unique and synergistic decomposition boundary
Information flow on causal paths
Relative information under representation change
Relational-information completeness certificate
""",
    "COARSE": """
Sufficient record for a declared observation
Minimal sufficient record
Information bottleneck as lawful coarsening
Coarse-graining partition structure
Refinement and abstraction order
Loss ledger for aggregation
Feature selection by retained distinction
State aggregation and exact lumping
Summary record reconstruction boundary
Multi-stage coarse-graining composition
Coarse-graining reversibility condition
Sufficiency and bottleneck completeness certificate
""",
    "RETR": """
Index as a source-bound location relation
Exact retrieval and membership
Inverted and forward index correspondence
Query as a declared observation
Ranking as an exact finite order
Tie and incomparability custody
Relevance as a registered relation
Precision and recall exact-part correspondence
Knowledge organization and taxonomy
Cross-reference and citation graph
Update and stale-index boundaries
Retrieval-family completeness certificate
""",
    "INFER": """
Inference as support restriction
Detection as observation-class decision
Estimation as retained representative selection
Filtering as sequential record update
Smoothing as whole-record reconstruction
Prediction as registered transition support
Evidence accumulation
Likelihood correspondence on exact support
Decision threshold without fitted scalar
False-positive and false-negative custody
Identifiability and observational equivalence
Sequential detection and stopping boundary
Multi-sensor information fusion
Inference-family completeness certificate
""",
    "PRIV": """
Information leakage as retained adversary distinction
Perfect secrecy correspondence
Side-information and disclosure boundary
Anonymity and indistinguishability classes
Access observation and least disclosure
Composition of privacy losses
Query disclosure and reconstruction risk
Privacy-utility exact trade boundary
Cryptographic ownership handoff
Privacy-interface completeness certificate
""",
    "THERM": """
Information record as a physical custody obligation
Irreversible merge and missing predecessor label
Reversible record retention
Erasure correspondence boundary
Measurement record cost
Memory reset and provenance custody
Maxwell-demon information ledger
Landauer and Bennett correspondence boundary
Information-energy non-equivalence boundary
Information-thermodynamics completeness certificate
""",
    "CORR": """
Classical symbol-information correspondence
Deterministic-support probability correspondence
Probabilistic mixture as hidden-support description
Quantum support correspondence
Quantum information unit correspondence
Composite support and product-state correspondence
Joint support and entanglement boundary
Phase information ownership handoff
Measurement support and record correspondence
Classical-to-quantum encoding boundary
Quantum-to-classical observation boundary
No-cloning information boundary correspondence
Quantum channel support correspondence
Quantum coding ownership handoff
Operational-dynamics nonduplication boundary
Classical-probabilistic-quantum completeness certificate
""",
    "SEM": """
Symbol count versus semantic content boundary
Reference and interpretation record
Context-dependent distinguishability
Biological information ownership handoff
Genetic representation correspondence
Neural and cognitive information handoff
Conscious access and reportability handoff
Social communication and shared-record handoff
Meaning-preserving translation boundary
Pragmatic action-information boundary
Cross-domain provenance and nonduplication
Semantic-handoff completeness certificate
""",
    "VALID": """
Symbol and representation complete validation vector
Record and provenance complete validation vector
Source and measure complete validation vector
Signal and sampling complete validation vector
Compression and distortion complete validation vector
Channel and capacity complete validation vector
Noise and coding complete validation vector
Relational and coarse-graining complete validation vector
Retrieval and inference complete validation vector
Privacy, thermodynamics and correspondence validation vector
Adverse, absent, unresolved and boundary vector
Information Science empirical and formal Grand Lock
""",
    "HAND": """
Information Science one-owner downstream handoff
Information Science measurement-boundary handoff
Information Science formal-to-empirical handoff
Information Science conventional-correspondence handoff
Information Science open-extension handoff
Information Science cross-branch completeness certificate
""",
}


def canonical(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("Information Science discipline census already frozen")
    rows = json.loads((ROOT / "census/claims.json").read_text())["claims"]
    base = [row for row in rows if row["branch"] == "information_science"]
    if len(base) != 12:
        raise SystemExit(f"expected twelve admitted Information Science base claims, found {len(base)}")
    obligations = []
    for index, row in enumerate(base, 1):
        obligations.append({
            "obligation_id": f"SFT-INFO-OBL-BASE-{index:03d}",
            "family": "BASE",
            "title": row["title"],
            "exact_boundary": row["statement"],
            "owner": "information_science",
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
                "obligation_id": f"SFT-INFO-OBL-{family}-{index:03d}",
                "family": family,
                "title": title,
                "exact_boundary": (
                    f"Derive {title.lower()} from exact generated Fold distinctions and records, enumerate the "
                    "complete declared grammar, preserve retained and closed distinctions, and prove the "
                    "finite-successor or explicit correspondence boundary."
                ),
                "owner": "information_science",
                "status": "open_registered_question",
                "current_claim_ids": [],
                "receipt_hashes": [],
                "receipt_paths": [],
                "required_strength": "exact_unique_survivor_depth_certificate_independent_reconstruction_and_external_comparison_where_possible",
                "required_external_surface": "post-registry exact computational observations, prior-corpus observations and authoritative external information records where available",
            })
    family_counts = {
        "BASE": len(base),
        **{
            family: len(tuple(line for line in text.strip().splitlines() if line.strip()))
            for family, text in FAMILIES.items()
        },
    }
    payload = {
        "schema": "sft-v3-information-science-discipline-question-census/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "branch": "information_science",
        "frozen": True,
        "frozen_before_new_target_outcome_access": True,
        "target_content_present": False,
        "base_claim_count": len(base),
        "closed_obligation_count_at_freeze": len(base),
        "registered_obligation_count": len(obligations),
        "open_obligation_count_at_freeze": len(obligations) - len(base),
        "family_order": ("BASE",) + tuple(FAMILIES),
        "family_counts": family_counts,
        "completion_rule": "Every obligation requires its own untouched-engine receipt; no partial family is counted complete; closure is dated and open to lawful extension.",
        "ownership_boundary": "Information Science owns structural distinctions, representations, uncertainty, channels and information transformation. Operational computation, cryptographic constructions, physical magnitudes and semantic experience remain with their owning branches.",
        "extension_policy": "complete to the current registered standard and open to lawful versioned extension",
        "obligations": obligations,
    }
    payload["census_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "path": OUT.relative_to(ROOT).as_posix(),
        "base": len(base),
        "registered": len(obligations),
        "open": len(obligations) - len(base),
        "family_counts": family_counts,
        "identity": payload["census_identity"],
    }, indent=2))


if __name__ == "__main__":
    main()
