#!/usr/bin/env python3
"""Freeze the value-free complete-field Mathematics question census."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/mathematics_discipline_obligations.json"

FAMILIES = {
"ARITH": """
Generated whole succession and exact induction
Addition and disjoint-junction arithmetic
Multiplication and complete pair-cell arithmetic
Divisibility, common divisors and common multiples
Exact quotient and oriented remainder
Prime and irreducible whole structure
Unique finite factorization certificate
Canonical exact fractions and common refinement
Finite continued-fraction correspondence
Residue classes and congruence
Compatible congruence composition
Prime-power valuation and divisibility depth
Diophantine relation enumeration
Recurrence laws and exact sequences
Finite generating-function correspondence
Whole partitions and ordered compositions
Arithmetic functions and divisor ledgers
Finite prime-distribution and growth enclosures
""",
"ALEXT": """
Polynomial identity and exact root isolation
Algebraic-magnitude balance certificates
Exact finite extension towers
Finite-field correspondence
Finite Galois-orbit correspondence
Cyclotomic and root-of-unity correspondence
Held-pair complex-number correspondence
Exact real-algebraic ordering
Prime-adic valuation correspondence
Transcendental and nonrepresentability boundary
""",
"COMB": """
Product, sum and bijection counting laws
Permutation and combination enumeration
Inclusion-exclusion with complete overlap custody
Pigeonhole and occupancy forcing
Recurrence and generating-function counting
Integer partitions and Young-type incidence
Extremal finite-set systems
Probabilistic-method correspondence without ontic randomness
Design, block and incidence structures
Coding and packing combinatorics
Ramsey-type finite forcing boundaries
Species and compositional enumeration
""",
"GRAPH": """
Graph identity, adjacency and isomorphism
Paths, walks, reachability and cycles
Connectivity, cuts and flow support
Trees, forests and spanning structure
Planarity and embedding correspondence
Colouring and constraint partitions
Matching, covering and packing
Directed graphs and causal reachability
Weighted network correspondence with exact parts
Hypergraphs and higher incidence
Matroids and independence systems
Network reliability and failure custody
Spectral graph correspondence
Dynamic and temporal networks
""",
"LINEAR": """
Vectors as exact generated coordinate carriers
Linear maps and composition
Matrix representation and exact row operations
Rank, nullity and retained distinctions
Determinants and orientation custody
Exact systems of linear relations
Basis, dimension and change of basis
Inner-product and metric correspondence
Eigenvalue and invariant-support correspondence
Exact rational spectral enclosures
Multilinear maps and tensor products
Tensor contraction and index custody
Exterior and symmetric composition
Finite-dimensional operator decomposition
""",
"ALG": """
Magma and closed operation structure
Semigroup associativity witnesses
Monoid identity witnesses
Group inverse as held reversal
Permutation-group action
Quotient and normal-substructure correspondence
Ring distributive structure
Integral-domain boundary
Field correspondence under exact division
Modules and scalar-action structure
Algebras and compatible products
Ideals and quotient structures
Representation and action decomposition
Exact sequence and homological correspondence
Universal algebra and identities
Operadic algebraic composition interface
""",
"ORDER": """
Preorder and distinguishability quotient
Partial order and antisymmetry
Conditional total order
Meet, join and lattice structure
Distributive and modular lattice correspondence
Boolean-like complement correspondence
Closure operators and closure systems
Galois connections between orders
Domain approximation correspondence
Monotone maps and order preservation
Fixed-point existence on finite orders
Complete-lattice correspondence boundary
""",
"GEOM": """
Point, incidence and exact coordinate identity
Finite Euclidean-distance correspondence
Affine combinations and affine invariance
Projective incidence and perspective
Convex hulls and separation
Discrete geometry and lattice polytopes
Polyhedral faces and Euler-type incidence
Computational geometry predicates
Exact orientation and intersection tests
Algebraic-geometry solution-set correspondence
Differential-geometry finite-chart correspondence
Curvature by exact finite transport
Metric geometry and geodesic correspondence
Fractal and self-similar geometry
Packing, covering and tessellation
Geometric transformation groups
""",
"TOPO": """
Open-set correspondence on generated supports
Continuity as distinction-preserving transport
Compactness finite-subcover correspondence
Connectedness and component structure
Separation properties on finite observations
Product, quotient and subspace topology correspondence
Simplicial complexes and incidence
Homotopy path-deformation correspondence
Fundamental-cycle and group correspondence
Homology and boundary composition
Cohomology and dual-observation correspondence
Manifold finite-atlas correspondence
Knot and link finite-diagram invariants
Computational topology and persistent-feature custody
""",
"CALC": """
Exact finite difference and local change
Higher finite differences and polynomial degree
Accumulation and exact finite sums
Fundamental difference-accumulation correspondence
Product and composition difference laws
Rational enclosure convergence
Derivative correspondence through shrinking exact parts
Integral correspondence through refinement sums
Multivariable difference and directional change
Discrete divergence and flux correspondence
Variational difference and stationary structure
Continuum-limit admissibility boundary
""",
"ANAL": """
Exact sequence convergence certificates
Cauchy-type generated support correspondence
Completeness correspondence without completed continuum
Series convergence and remainder enclosures
Power-series finite truncation custody
Functional-space finite-representation correspondence
Norm, seminorm and metric correspondence
Bounded and compact operator correspondence
Harmonic and Fourier finite-support correspondence
Transform inversion on generated supports
Convolution and correlation identities
Orthogonality and basis expansion correspondence
Distributional and weak-observation correspondence
Nonlinear analysis and contraction boundaries
Complex-analysis held-pair correspondence
Operator spectral-measure correspondence
""",
"EQN": """
Ordinary difference-equation structure
Ordinary differential-equation correspondence
Partial difference-equation structure
Partial differential-equation correspondence
Boundary and initial record well-posedness
Integral-equation correspondence
Functional-equation structure
Recurrence-equation solution spaces
Green-response finite correspondence
Conservation-law weak correspondence
Stability and perturbation enclosures
Existence, uniqueness and blow-up boundaries
""",
"MEAS": """
Finite measure and exact support weight
Additivity on disjoint generated support
Outer-measure and covering correspondence
Measurable-boundary correspondence
Exact integration over finite support
Refinement-sum integration correspondence
Product measure and conditional support
Signed-measure replacement by held orientation
Distribution and generalized-observation correspondence
Convergence-of-measures finite witness boundary
""",
"PROB": """
Exact support-based probability correspondence
Conditional support and Bayes correspondence
Independence and factorization witnesses
Expectation as exact support accumulation
Variance and dispersion without negative magnitudes
Finite distribution families
Law-of-large-count correspondence under deterministic enumeration
Central-limit enclosure correspondence
Estimation and sufficient-record structure
Confidence and credible-region correspondence
Hypothesis testing and error custody
Likelihood and evidence ratios
Bayesian update as exact conditional support
Finite stochastic-process correspondence
Martingale-like conditional conservation
Statistical identifiability and nonidentifiability
""",
"OPT": """
Feasible set and objective-order structure
Exact minimum and maximum on finite support
Pareto dominance and multiobjective order
Linear-program correspondence
Integer and combinatorial optimization
Convex optimization correspondence
Duality and certificate structure
Variational optimization correspondence
Dynamic programming as compositional optimization
Optimal control on generated state paths
Game equilibrium finite correspondence
Decision theory and loss ordering
Operations-research flow and scheduling
Robust optimization under bounded uncertainty
Approximation guarantees and gaps
Infeasibility and unboundedness boundaries
""",
"DYN": """
State maps and exact orbit structure
Fixed points and periodic cycles
Recurrence and return-time structure
Invariant sets and conserved records
Stability and attraction correspondence
Bifurcation as finite distinction change
Symbolic dynamics and shift correspondence
Chaos through exact sensitivity witnesses
Ergodic-average finite correspondence
Hamiltonian and reversible-map correspondence
Dissipative dynamics and retained loss
Coupled and networked dynamical systems
""",
"LOGIC": """
Propositions as generated distinctions
Inference and consequence preservation
Soundness and completeness correspondence
Formal proof objects and checking
First-order quantifier finite-support correspondence
Model and interpretation structure
Compactness correspondence boundary
Decidability and computability interface
Incompleteness and self-reference boundary
Set-like finite collection theory
Class, universe and size boundaries
Constructive and intuitionistic correspondence
Modal and temporal logic correspondence
Nonclassical many-valued correspondence
Proof-theoretic normalization
Foundational consistency and self-verification limits
""",
"CAT": """
Objects, arrows and typed composition
Identity and associativity witnesses
Functorial structure preservation
Natural transformation correspondence
Products, coproducts and universal constructions
Limits and colimits on generated diagrams
Adjunction and paired universal maps
Monoidal composition and tensor interface
Closed structure and internal maps
Type correspondence and dependent records
Sheaf-like local-to-global custody
Operadic and higher-composition boundary
""",
"NUM": """
Exact numerical representation and rounding custody
Interval and rational enclosure arithmetic
Truncation and discretization error
Forward and backward stability
Conditioning and sensitivity
Convergence order with exact bounds
Root isolation and equation solving
Linear-system exact and approximate solvers
Interpolation and approximation
Quadrature and accumulation enclosures
Differential-equation numerical correspondence
Verified computation and certificate extraction
""",
"SYMB": """
Symbolic expression identity and canonical form
Exact simplification with provenance
Polynomial factorization and expansion
Symbolic equation solving
Rewrite termination and confluence interface
Generating-function transforms
Fourier and Laplace correspondence transforms
Special-function recurrence representation
Automated theorem search boundary
Constructive witness and certificate generation
""",
"XINT": """
Mathematics-to-Information exact-structure handoff
Mathematics-to-Computation model handoff
Mathematics-to-Physics quantity and geometry handoff
Mathematics-to-Chemistry structure handoff
Mathematics-to-Biology organization handoff
Mathematics-to-Social inference handoff
Mathematics-to-Engineering calculation handoff
Shared mathematical identity without duplicate ownership
""",
"VALID": """
Arithmetic and algebra complete validation vector
Combinatorics and graph complete validation vector
Linear and algebraic-structure validation vector
Order and geometry complete validation vector
Topology and analysis complete validation vector
Equation and measure complete validation vector
Probability and statistics complete validation vector
Optimization and dynamics complete validation vector
Logic and compositional complete validation vector
Numerical and symbolic complete validation vector
Adverse absent unresolved and boundary vector
Mathematics empirical and formal Grand Lock
""",
"HAND": """
Mathematics one-owner downstream handoff
Mathematics measurement-boundary handoff
Mathematics formal-to-empirical handoff
Mathematics conventional-correspondence handoff
Mathematics open-extension handoff
Mathematics cross-branch one-owner completeness certificate
""",
}


def canonical(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("Mathematics discipline census already frozen")
    rows = read_claims = json.loads((ROOT / "census/claims.json").read_text())["claims"]
    base = [row for row in rows if row["branch"] == "mathematics"]
    obligations = []
    for index, row in enumerate(base, 1):
        obligations.append({
            "obligation_id": f"SFT-MATH-OBL-BASE-{index:03d}", "family": "BASE",
            "title": row["title"], "exact_boundary": row["statement"],
            "owner": "mathematics", "status": "closed_current_model_admitted_receipt",
            "current_claim_ids": [row["claim_id"]], "receipt_hashes": [row["receipt_hash"]],
            "receipt_paths": [row["receipt_path"]],
            "required_strength": "existing_exact_unique_survivor_independent_reconstruction",
            "required_external_surface": "existing receipt-bound formal or empirical package",
        })
    for family, text in FAMILIES.items():
        titles = tuple(line.strip() for line in text.strip().splitlines() if line.strip())
        for index, title in enumerate(titles, 1):
            obligations.append({
                "obligation_id": f"SFT-MATH-OBL-{family}-{index:03d}", "family": family,
                "title": title,
                "exact_boundary": f"Derive {title.lower()} from generated exact Fold structures, enumerate the complete declared grammar, preserve every distinction and prove the finite-successor or explicit correspondence boundary.",
                "owner": "mathematics", "status": "open_registered_question",
                "current_claim_ids": [], "receipt_hashes": [], "receipt_paths": [],
                "required_strength": "exact_unique_survivor_depth_certificate_independent_reconstruction_and_external_comparison_where_possible",
                "required_external_surface": "post-registry exact computational observations, prior-corpus observations and authoritative external mathematical records where available",
            })
    family_counts = {"BASE": len(base), **{family: len(tuple(line for line in text.strip().splitlines() if line.strip())) for family, text in FAMILIES.items()}}
    payload = {
        "schema": "sft-v3-mathematics-discipline-question-census/1", "date": "2026-07-29",
        "authority": "Maria Smith", "branch": "mathematics", "frozen": True,
        "frozen_before_new_target_outcome_access": True, "target_content_present": False,
        "base_claim_count": len(base), "closed_obligation_count_at_freeze": len(base),
        "registered_obligation_count": len(obligations), "open_obligation_count_at_freeze": len(obligations) - len(base),
        "family_order": ("BASE",) + tuple(FAMILIES), "family_counts": family_counts,
        "completion_rule": "Every obligation requires its own untouched-engine receipt; no partial family is counted complete; closure is dated and open to lawful extension.",
        "ownership_boundary": "Mathematics owns exact structures and proof relations. Empirical sciences own physical magnitudes and observations even when expressed mathematically.",
        "extension_policy": "complete to the current registered standard and open to lawful versioned extension",
        "obligations": obligations,
    }
    payload["census_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"path": OUT.relative_to(ROOT).as_posix(), "base": len(base), "registered": len(obligations), "open": len(obligations)-len(base), "family_counts": family_counts, "identity": payload["census_identity"]}, indent=2))


if __name__ == "__main__":
    main()
