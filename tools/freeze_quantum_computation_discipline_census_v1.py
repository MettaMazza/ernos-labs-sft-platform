#!/usr/bin/env python3
"""Freeze the value-free complete-field Reversible and Quantum Computation census."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/quantum_computation_discipline_obligations.json"


FAMILIES = {
    "REVX": """
Reversible configuration and transition identity
Injective, surjective and bijective process distinction
Reversible language and grammar relation
Reversible automaton and transducer construction
Reversible rewriting and retained predecessor custody
Reversible tape-machine configuration law
Reversible universal interpreter
History tape and uncomputation
Ancilla preparation and exact restoration
Garbage record and cleanup boundary
Logical reversibility and physical erasure handoff
Reversible simulation of irreversible computation
Irreversible simulation of reversible computation
Reversible time, space and record tradeoff
Reversible circuit synthesis and decomposition
Reversible control and conditional execution
Reversible fault and recovery trace
Reversible-computation completeness certificate
""",
    "QSTATEX": """
Quantum information-unit identity
Finite register and word-support construction
Canonical state-description identity
State preparation and provenance
Product state and component reconstruction
Joint state and marginal support
Pure-support and mixed-record correspondence
Superposition-equivalent complete support
Relative phase-label identity
Global and relative phase distinction
Phase composition and inversion
Constructive and destructive interference classes
Path composition and predecessor merging
Which-path record and interference boundary
Bipartite nonfactorable support
Multipartite nonfactorable support
Entanglement partition and cut structure
Entanglement swapping correspondence
Monogamy and shareability boundary
State purification correspondence
Reduced observation and retained environment record
Measurement question and outcome-class identity
Measurement composition and repeatability
Compatible and incompatible observation relations
Deferred-measurement correspondence
No-cloning and exact copying boundary
No-deleting and retained-record boundary
Quantum-state structure completeness certificate
""",
    "GATEX": """
Reversible transformation identity
Single-unit permutation and phase actions
Controlled transformation law
Two-unit entangling transformation
Multi-controlled transformation
Gate composition and inverse
Gate commutation and causal reordering
Universal finite gate-description grammar
Exact gate synthesis
Approximate gate synthesis with enclosure custody
Circuit wire, register and gate syntax
Circuit branchwise operational semantics
Circuit observation semantics
Circuit inversion and uncomputation
Circuit equivalence and normal form
Circuit decomposition into local transformations
Circuit size, depth, width and live-support resources
Circuit compilation and semantic preservation
Measurement-based computation correspondence
Adiabatic computation correspondence boundary
Topological computation correspondence boundary
Gate-and-circuit completeness certificate
""",
    "QALGX": """
Quantum algorithm specification and correctness trace
Reversible oracle and query interface
Phase kickback correspondence
Quantum Fourier transform correspondence
Phase estimation correspondence
Period finding and order finding
Deutsch-style promise distinction
Simon-style hidden-structure distinction
Factorization reduction and resource custody
Unstructured search and amplitude-amplification correspondence
Quantum counting correspondence
Amplitude-estimation correspondence with exact enclosures
Quantum walk state and transition law
Quantum walk search boundary
Linear-system algorithm correspondence
Eigenvalue and mode-estimation algorithm
Hamiltonian-simulation algorithm interface
Product-formula simulation and error custody
Combinatorial optimization algorithm boundary
Variational algorithm parameter-prohibition boundary
Quantum annealing correspondence boundary
Quantum sampling and output-support custody
Bosonic-sampling correspondence boundary
Hidden-subgroup algorithm family
Quantum dynamic programming correspondence
Quantum parallelism and output-access boundary
Classical preprocessing and postprocessing custody
Speedup definition and comparison grammar
Algorithm lower and upper resource witnesses
Quantum-algorithm completeness certificate
""",
    "QCPLXX": """
Canonical quantum input-size carrier
Gate count and circuit-depth resource
Live branch-support and state-description resource
Ancilla, measurement and retained-record resource
Quantum query complexity
Quantum communication complexity
Quantum decision and recognition class
Bounded-error deterministic-support correspondence
Exact quantum decision class
One-sided-error correspondence boundary
Quantum nondeterminism correspondence boundary
Quantum polynomial-time correspondence
Quantum witness-verification class
Interactive quantum proof correspondence
Quantum space complexity
Quantum parallel complexity
Quantum circuit-family uniformity
Quantum reduction and completeness
Quantum lower-bound adversary certificate
Polynomial method correspondence boundary
Classical simulation resource boundary
Quantum advantage and separation certificate
Average-case and distribution custody
Parameterized quantum complexity
Quantum descriptive complexity
Quantum-complexity completeness certificate
""",
    "QCOMMX": """
Quantum channel as exact relation
Channel composition and memory boundary
Classical information over a quantum channel
Quantum information transfer
Entanglement-assisted communication
Teleportation-equivalent state transfer
Dense-coding-equivalent distinction transfer
No-signalling operational boundary
Channel capacity as generated support rate
Private and coherent information correspondence
Quantum data-processing relation
Channel noise and environment record
Entanglement distribution and swapping
Quantum repeater correspondence
Quantum network node and link identity
Distributed quantum process causality
Network entanglement routing
Quantum key-distribution correctness boundary
Quantum authentication interface
Quantum secret-sharing correspondence
Device-independent security handoff
Quantum adversary and transcript custody
Post-quantum classical-security handoff
Quantum communication and security completeness certificate
""",
    "QCODEX": """
Logical information and physical carrier distinction
Quantum encoder and reversible decoder
Error action and error-family registration
Error detection and syndrome distinction
Correctable-error condition correspondence
Bit-label error repetition code
Phase-label error repetition code
Joint bit-phase error composition
Single-error exhaustive recovery
Two-error exhaustive recovery
Three-error exhaustive recovery
Positive-finite multi-error successor law
Erasure error and located recovery
Amplitude-loss correspondence boundary
Dephasing correspondence boundary
Depolarizing-support correspondence boundary
Stabilizer-code correspondence
CSS-code correspondence
Subsystem-code correspondence
Topological-code correspondence boundary
Surface-code correspondence boundary
Concatenated-code composition
Logical gate and encoded transformation
Transversal-gate containment
Syndrome-extraction fault custody
Fault-tolerant location composition
Malignant-fault-set boundary
Correlated and nonlocal fault boundary
Leakage and loss fault boundary
State and magic-resource distillation correspondence
Physical threshold constant measurement handoff
Quantum coding and fault-tolerance completeness certificate
""",
    "QSIMX": """
Quantum model and simulator identity
Finite target support encoding
Digital quantum simulation
Analog quantum simulation correspondence boundary
Local interaction and update composition
Hamiltonian correspondence without imported continuum proof values
Time-evolution approximation and enclosure custody
Many-body support organization
Fermionic and bosonic encoding correspondence
Lattice and field discretization handoff
Open-system simulation and environment record
Noise simulation and source custody
Quantum chemistry simulation handoff
Materials simulation handoff
Verification of a quantum computation
Interactive quantum verification
Blind delegated-computation correspondence
Self-testing correspondence boundary
Tomography and state-reconstruction boundary
Process reconstruction and channel verification
Randomized benchmarking deterministic-support boundary
Simulation validation against owning-domain data
Reproducible quantum-workflow provenance
Quantum simulation and verification completeness certificate
""",
    "QLEARNX": """
Quantum learning problem and example identity
Classical-data quantum-process boundary
Quantum-data support and observation custody
Quantum hypothesis family generation
Quantum feature-map correspondence
Quantum kernel correspondence boundary
Quantum classification process
Quantum regression process
Quantum generative-support reconstruction
Quantum clustering correspondence
Quantum principal-structure correspondence
Quantum optimization in learning
Variational quantum learning parameter boundary
Quantum reinforcement-process correspondence
Quantum online-learning correspondence
Quantum sample complexity
Quantum query complexity of learning
Generalization and held-out target custody
Quantum advantage in learning certificate
Interpretability and branch-trace reconstruction
Verification and robustness of quantum learners
Quantum-learning completeness certificate
""",
    "QLIMITX": """
Classical-state embedding in the quantum machine
Classical reversible submodel correspondence
Classical probabilistic support correspondence
Quantum-to-classical measurement decoder
Operational simulation in both directions
Classical simulation efficient-region certificate
Phase-sensitive separation witness
Entanglement-sensitive separation witness
No-cloning computational limit
Measurement disturbance computational boundary
Quantum halting and self-reference transfer
Quantum undecidability boundary
Quantum incompleteness boundary
No-hypercomputation boundary
Finite support and completed-infinity prohibition
No unrestricted advantage from bounded examples
No physical speedup without device measurement
No hardware threshold from a formal code theorem
Energy, timing and implementation handoff
Quantum-to-Physics measurement boundary
Open extension and falsification boundary
Quantum computation limits completeness certificate
""",
    "VALID": """
Reversible-computation complete validation vector
Quantum-state-structure complete validation vector
Gate-and-circuit complete validation vector
Quantum-algorithm complete validation vector
Quantum-complexity complete validation vector
Quantum-communication and security complete validation vector
Quantum-coding and fault-tolerance complete validation vector
Quantum-simulation and verification complete validation vector
Quantum-learning complete validation vector
Classical-quantum correspondence and limits validation vector
Adverse, absent, unresolved and ownership-boundary vector
Reversible and Quantum Computation empirical and formal Grand Lock
""",
    "HAND": """
Quantum Computation one-owner downstream handoff
Quantum physical-measurement handoff
Quantum chemistry and materials handoff
Quantum software and hardware engineering handoff
Quantum Computation open-extension handoff
Quantum Computation cross-branch completeness certificate
""",
}


def canonical(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("Quantum Computation discipline census already frozen")
    claims = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
    base = [row for row in claims if row.get("branch") == "quantum_computation"]
    if len(base) != 22:
        raise SystemExit(f"expected 22 admitted Quantum Computation base claims, found {len(base)}")
    if any(not row.get("model_admitted") for row in base):
        raise SystemExit("Quantum Computation base contains a non-admitted claim")

    obligations = []
    for index, row in enumerate(base, 1):
        obligations.append(
            {
                "obligation_id": f"SFT-QUANTUM-OBL-BASE-{index:03d}",
                "family": "BASE",
                "title": row["title"],
                "exact_boundary": row["statement"],
                "owner": "quantum_computation",
                "status": "closed_current_model_admitted_receipt",
                "current_claim_ids": [row["claim_id"]],
                "receipt_hashes": [row["receipt_hash"]],
                "receipt_paths": [row["receipt_path"]],
                "required_strength": "existing_exact_unique_survivor_independent_reconstruction",
                "required_external_surface": "existing receipt-bound exact operational package",
            }
        )

    for family, text in FAMILIES.items():
        titles = tuple(line.strip() for line in text.strip().splitlines() if line.strip())
        for index, title in enumerate(titles, 1):
            obligations.append(
                {
                    "obligation_id": f"SFT-QUANTUM-OBL-{family}-{index:03d}",
                    "family": family,
                    "title": title,
                    "exact_boundary": (
                        f"Derive {title.lower()} from admitted Fold distinctions, exact finite branch support, held phase labels, "
                        "reversible source-bound transformations, retained observation records and complete resource ledgers; "
                        "enumerate the declared grammar; preserve every adverse and ownership row; and state every formal, "
                        "finite-census, physical-measurement and unrestricted boundary without importing a conventional quantum answer."
                    ),
                    "owner": "quantum_computation",
                    "status": "open_frozen_value_free_obligation",
                    "current_claim_ids": [],
                    "receipt_hashes": [],
                    "receipt_paths": [],
                    "required_strength": "exact_unique_survivor_controls_independent_reconstruction_post_registry_observation",
                    "required_external_surface": "exact operational execution or explicit downstream physical-measurement handoff",
                }
            )

    family_order = ["BASE", *FAMILIES]
    family_counts = {family: sum(row["family"] == family for row in obligations) for family in family_order}
    payload = {
        "schema": "sft-v3-quantum-computation-discipline-census/1",
        "branch": "quantum_computation",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "frozen": True,
        "frozen_before_new_target_outcome_access": True,
        "target_content_present": False,
        "ownership_boundary": (
            "Reversible and Quantum Computation owns formal and operational quantum models, algorithms, resources, "
            "communication, coding, correction, verification, learning, correspondence and limits. Natural quantum "
            "measurements belong to Physics; chemistry/materials consequences and hardware/software implementations "
            "remain explicit downstream handoffs."
        ),
        "completion_rule": (
            "Every obligation must have one current model-admitted receipt, a complete literal candidate census with one "
            "survivor, adverse controls, an implementation-distinct reconstruction, exact execution observed after a "
            "value-free registry or an explicit one-owner physical-measurement handoff, and a dependency route to "
            "SFT-ROOT-THERE-IS-NO-NOTHING. No failed attempt retires an obligation or changes the protected authority."
        ),
        "extension_policy": (
            "Completion is dated to this census and remains open to lawful versioned extension, correction and falsification. "
            "A later obligation adds evidence without rewriting a prior receipt."
        ),
        "family_order": family_order,
        "family_counts": family_counts,
        "base_claim_count": len(base),
        "registered_obligation_count": len(obligations),
        "closed_obligation_count_at_freeze": len(base),
        "open_obligation_count_at_freeze": len(obligations) - len(base),
        "obligations": obligations,
    }
    payload["census_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "census": str(OUT.relative_to(ROOT)),
        "census_identity": payload["census_identity"],
        "registered": len(obligations),
        "closed_at_freeze": len(base),
        "open_at_freeze": len(obligations) - len(base),
        "family_counts": family_counts,
    }, indent=2))


if __name__ == "__main__":
    main()
