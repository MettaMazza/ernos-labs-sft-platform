#!/usr/bin/env python3
"""Register twelve exact source-artifact validity disproof obligations.

These are version-two successors to the reconstruction-only obligations.  The
target is the SFT validity of each frozen external artifact, not the separate
SFT-native proposition already derived in version one.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V1_REGISTRY = ROOT / "census/openai_ten_advances_2026_sft_obligation_registry_v1.json"
V2_REGISTRY = ROOT / "census/openai_ten_advances_2026_sft_source_validity_registry_v2.json"
SOURCE_ROOT = (
    ROOT
    / "experiments/external_sources/mathematics/openai_ten_advances_mathematics_2026-08-01_v1/"
    "upstream_tree/ten-proofs-94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6"
)
GENERIC = (
    "SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001",
    "SFT-MATH-LOGIC-PROOF-001",
)


ROWS = (
    {
        "atomic_id": "OAI26-MATH-001",
        "claim_id": "SFT-MATH-OAI26-SPHERE-PACKING-VALIDITY-001",
        "required_source_tokens": ("SharpFullCohnElkiesManuscriptConclusions", "Tendsto", "Real.pi", "Real.exp", "atTop"),
        "necessary_component": "completed real-valued dimension limits and completed error functions",
        "domain_contradiction": "SFT admits generated exact refinement certificates and denies completed infinity or an ungenerated continuum as proof objects.",
        "domain_dependencies": ("SFT-FOUNDATION-COUNT-001", "SFT-FOUNDATION-EXACT-OPERATIONS-001", "SFT-MATH-LIMIT-CONTINUUM-002", "SFT-MATH-ANAL-HARMONIC-FOURIER-SUPPORT-009"),
    },
    {
        "atomic_id": "OAI26-MATH-002",
        "claim_id": "SFT-MATH-OAI26-BINARY-CODE-MRRW-VALIDITY-002",
        "required_source_tokens": ("binaryRate_lt_mrrw", "binaryRate", "mrrwRate", "limsup"),
        "necessary_component": "completed real asymptotic rates defined through limsup, infimum, roots and logarithms",
        "domain_contradiction": "SFT coding closes generated finite code censuses and exact enclosures, not a completed real limsup carrier.",
        "domain_dependencies": ("SFT-MATH-COMB-CODING-PACKING-010", "SFT-MATH-CALC-RATIONAL-ENCLOSURE-CONVERGENCE-006", "SFT-MATH-LIMIT-CONTINUUM-002"),
    },
    {
        "atomic_id": "OAI26-MATH-003",
        "claim_id": "SFT-MATH-OAI26-SPHERICAL-CODE-HIERARCHY-VALIDITY-003",
        "required_source_tokens": ("strict_hierarchy", "levelRate", "localizedLevelRate", "sphericalCodeRate"),
        "necessary_component": "an all-level hierarchy of completed real rate infima over an unbounded natural index",
        "domain_contradiction": "SFT retains each generated code and hierarchy stage but denies the completed ungenerated total range required by the source object.",
        "domain_dependencies": ("SFT-MATH-COMB-CODING-PACKING-010", "SFT-MATH-GEOM-PACKING-COVERING-TESSELLATION-015", "SFT-MATH-LIMIT-CONTINUUM-002"),
    },
    {
        "atomic_id": "OAI26-MATH-004",
        "claim_id": "SFT-MATH-OAI26-NONSOFIC-GROUP-VALIDITY-004",
        "required_source_tokens": ("exists_finitelyPresented_nonsofic_group", "IsFinitelyPresented", "Sofic"),
        "necessary_component": "an existential group carrier that is finitely presented and not sofic",
        "domain_contradiction": "Every admitted SFT group stage is generated with a complete finite carrier; its left-regular permutation action supplies an exact sofic model, leaving no admitted nonsofic witness.",
        "domain_dependencies": ("SFT-MATH-ALG-GROUP-HELD-INVERSE-004", "SFT-MATH-ALG-PERMUTATION-GROUP-ACTION-005", "SFT-MATH-LOGIC-MODEL-INTERPRETATION-006", "SFT-MATH-LIMIT-CONTINUUM-002"),
    },
    {
        "atomic_id": "OAI26-MATH-005",
        "claim_id": "SFT-MATH-OAI26-CONNES-RIGIDITY-VALIDITY-005",
        "required_source_tokens": ("exists_infinite_pairwise_nonisomorphic_propertyT_icc_groups_with_isomorphic_factors", "IsICC", "TracialGroupFactorsIsomorphic"),
        "necessary_component": "infinite groups, an infinite indexed family, infinite conjugacy classes and completed operator factors",
        "domain_contradiction": "SFT group, representation, operator and integration supports are generated finite objects; the source IsICC/infinite-family fields require the denied completed carrier.",
        "domain_dependencies": ("SFT-MATH-ALG-GROUP-HELD-INVERSE-004", "SFT-MATH-ALG-REPRESENTATION-ACTION-DECOMPOSITION-013", "SFT-MATH-ANAL-BOUNDED-COMPACT-OPERATOR-008", "SFT-MATH-MEAS-FINITE-SUPPORT-INTEGRATION-005", "SFT-MATH-LIMIT-CONTINUUM-002"),
    },
    {
        "atomic_id": "OAI26-COMP-001",
        "claim_id": "SFT-COMP-OAI26-PERMANENT-FORMULA-VALIDITY-001",
        "required_source_tokens": ("permanent_rational_formula_logarithmic_lower_bound", "RationalFormula", "FractionRing", "Real.logb"),
        "necessary_component": "complex fraction-ring formulas with subtraction/division and a completed real logarithmic resource scalar",
        "domain_contradiction": "SFT exact operations and circuit lower bounds apply to admitted canonical carriers and Fold edges; the source gate basis has no total SFT transport theorem.",
        "domain_dependencies": ("SFT-FOUNDATION-EXACT-OPERATIONS-001", "SFT-MATH-SYMB-CANONICAL-EXPRESSION-001", "SFT-COMP-CPLXX-FORMULA-BRANCHING-CIRCUIT-014", "SFT-COMP-CPLXX-ARBITRARY-FOLD-CIRCUIT-LOWER-024"),
    },
    {
        "atomic_id": "OAI26-QUANTUM-001",
        "claim_id": "SFT-QUANTUM-OAI26-PARALLEL-REPETITION-VALIDITY-001",
        "required_source_tokens": ("distributionUniformExponential", "DensityMatrix", "entangledValue", "Real.exp"),
        "necessary_component": "real suprema over complex density-matrix and POVM strategies followed by a completed exponential bound",
        "domain_contradiction": "SFT entanglement is generated exact nonfactorable support with no imported Hilbert-space or complex-amplitude axiom; its parallel law retains finite resource traces.",
        "domain_dependencies": ("SFT-FOUNDATION-EXACT-OPERATIONS-001", "SFT-QUANTUM-ENTANGLEMENT-001", "SFT-QUANTUM-QCPLXX-PARALLEL-016", "SFT-QUANTUM-QCPLXX-REDUCTION-018"),
    },
    {
        "atomic_id": "OAI26-COMP-002",
        "claim_id": "SFT-COMP-OAI26-GAPCVP400-VALIDITY-002",
        "required_source_tokens": ("gapCVP400IsNPHard", "IsNPHardPromise", "PromiseReduction", "gapFactor400"),
        "necessary_component": "the completed family of all bit languages and conventional reductions into signed integer lattices with a real gap factor",
        "domain_contradiction": "SFT hardness transfer requires a registered total verdict- and resource-preserving map over the declared family; untransported conventional NP authority and completed source families are excluded.",
        "domain_dependencies": ("SFT-FOUNDATION-EXACT-OPERATIONS-001", "SFT-MATH-GEOM-DISCRETE-LATTICE-POLYTOPE-006", "SFT-MATH-GEOM-EUCLIDEAN-DISTANCE-002", "SFT-COMP-CPLXX-REDUCTION-COMPLETE-PROBLEM-021", "SFT-COMP-CPLXX-APPROXIMATION-RATIO-026"),
    },
    {
        "atomic_id": "OAI26-MATH-006",
        "claim_id": "SFT-MATH-OAI26-EHRHART-VOLUME-VALIDITY-006",
        "required_source_tokens": ("ehrhart_volume_inequality_for_sets", "normalizedVolume", "barycenter", "interiorLatticePoints"),
        "necessary_component": "arbitrary subsets of a completed real space with topological interior, compactness and continuum volume",
        "domain_contradiction": "SFT convexity, lattice geometry and integration close generated hulls and finite support; arbitrary continuum sets and continuum measure are not proof objects.",
        "domain_dependencies": ("SFT-FOUNDATION-EXACT-OPERATIONS-001", "SFT-MATH-GEOM-CONVEX-HULL-SEPARATION-005", "SFT-MATH-GEOM-DISCRETE-LATTICE-POLYTOPE-006", "SFT-MATH-MEAS-FINITE-SUPPORT-INTEGRATION-005", "SFT-MATH-MEAS-CONVERGENCE-FINITE-WITNESS-010"),
    },
    {
        "atomic_id": "OAI26-MATH-007",
        "claim_id": "SFT-MATH-OAI26-MULTICOLOUR-RAMSEY-VALIDITY-007",
        "required_source_tokens": ("erdos_problem_183_explicit", "triangleRamseyNumber", "Real.exp", "Tendsto"),
        "necessary_component": "a completed Tendsto-atTop conjunct and all-colour real exp/log/fractional-power bounds",
        "domain_contradiction": "SFT Ramsey forcing closes generated finite colouring censuses and replaces limit claims by exact successor/modulus certificates; the submitted completed filter remains outside its object language.",
        "domain_dependencies": ("SFT-MATH-COMB-RAMSEY-FORCING-011", "SFT-MATH-COMB-CODING-PACKING-010", "SFT-MATH-GRAPH-COLOURING-CONSTRAINT-006", "SFT-MATH-LIMIT-CONTINUUM-002"),
    },
    {
        "atomic_id": "OAI26-MATH-008",
        "claim_id": "SFT-MATH-OAI26-COMPACTNESS-VALIDITY-008",
        "required_source_tokens": ("quantitativeCompactnessCounterexample", "UniformMemberLower", "IsCompactFamily", "atTop"),
        "necessary_component": "eventually-atTop real lower bounds, all-size fractional powers and a completed compactness predicate",
        "domain_contradiction": "SFT extremal graph laws close exact finite host/family censuses; the completed eventual filter and unrestricted real exponent required by the source witness are excluded.",
        "domain_dependencies": ("SFT-MATH-COMB-EXTREMAL-SET-SYSTEM-007", "SFT-MATH-GRAPH-MATCHING-COVERING-PACKING-007", "SFT-MATH-LIMIT-CONTINUUM-002", "SFT-FOUNDATION-EXACT-OPERATIONS-001"),
    },
    {
        "atomic_id": "OAI26-MATH-009",
        "claim_id": "SFT-MATH-OAI26-TWO-DEGENERATE-VALIDITY-009",
        "required_source_tokens": ("twoDegenerateExtremalCounterexample", "IsTwoDegenerate", "extremalNumber", "atTop"),
        "necessary_component": "positive completed real constants and an eventually-atTop lower bound with a real fractional exponent",
        "domain_contradiction": "SFT admits each generated finite graph and colouring census but not the source completed eventual filter or ungenerated real exponent witness.",
        "domain_dependencies": ("SFT-MATH-COMB-EXTREMAL-SET-SYSTEM-007", "SFT-MATH-GRAPH-COLOURING-CONSTRAINT-006", "SFT-MATH-GRAPH-MATCHING-COVERING-PACKING-007", "SFT-MATH-LIMIT-CONTINUUM-002", "SFT-FOUNDATION-EXACT-OPERATIONS-001"),
    },
)


def identity(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_seals() -> None:
    for tool, status in (
        ("verify_engine_seal.py", "VALID_CANONICAL_ENGINE"),
        ("verify_verification_authority_seal.py", "VALID_CANONICAL_VERIFICATION_AUTHORITY"),
    ):
        result = subprocess.run((sys.executable, str(ROOT / "tools" / tool), "--json"), cwd=ROOT, text=True, capture_output=True)
        payload = json.loads(result.stdout)
        if result.returncode or payload.get("status") != status:
            raise SystemExit(f"registration halted: {tool}")


def main() -> None:
    verify_seals()
    v1 = json.loads(V1_REGISTRY.read_text(encoding="utf-8"))
    v1_by_atomic = {row["atomic_id"]: row for row in v1["rows"]}
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
    admitted = {row["claim_id"] for row in census["claims"] if row.get("model_admitted") is True}
    registry_rows = []
    for order, row in enumerate(ROWS, start=1):
        original = v1_by_atomic[row["atomic_id"]]
        original_package = ROOT / "claims" / original["claim_id"]
        source_record_path = original_package / "source_statement.json"
        source_record = json.loads(source_record_path.read_text(encoding="utf-8"))
        if identity(source_record) != original["source_statement_hash"]:
            raise SystemExit(f"source record changed: {row['atomic_id']}")
        source_path = SOURCE_ROOT / source_record["source_file"]
        if file_hash(source_path) != source_record["source_file_sha256"]:
            raise SystemExit(f"source file changed: {row['atomic_id']}")
        source_text = source_path.read_text(encoding="utf-8")
        missing = [token for token in row["required_source_tokens"] if token not in source_text]
        if missing:
            raise SystemExit(f"source tokens missing for {row['atomic_id']}: {missing}")
        dependencies = tuple(dict.fromkeys(GENERIC + row["domain_dependencies"]))
        if any(dependency not in admitted for dependency in dependencies):
            raise SystemExit(f"unadmitted governing dependency: {row['claim_id']}")
        proposition = f"SFTValid(exact frozen artifact {source_record['declaration']})"
        negation = (
            f"Not {proposition}: assuming this artifact is an SFT-valid derivation forces the axiom vector to be empty "
            f"and every necessary carrier to be SFT-admitted, while the exact frozen source exposes the nonempty vector "
            f"[propext, Classical.choice, Quot.sound] and requires {row['necessary_component']}."
        )
        package = ROOT / "claims" / row["claim_id"]
        package.mkdir(parents=True, exist_ok=True)
        source_binding = {
            "schema": "sft-v3-openai-2026-exact-source-quotation/2",
            "claim_id": row["claim_id"],
            "original_reconstruction_claim_id": original["claim_id"],
            "source_statement_path": source_record_path.relative_to(ROOT).as_posix(),
            "source_statement_hash": original["source_statement_hash"],
            "source_file_path": source_path.relative_to(ROOT).as_posix(),
            "source_file_sha256": source_record["source_file_sha256"],
            "source_commit": source_record["source_commit"],
            "declaration": source_record["declaration"],
            "signature_text": source_record["signature_text"],
            "signature_sha256": source_record["signature_sha256"],
            "exact_quantifier_and_conjunct_order": source_record["exact_quantifier_and_conjunct_order"],
            "source_declared_axioms": source_record["upstream_declared_axioms"],
            "source_sorry_count": source_record["upstream_sorry_count"],
            "required_source_tokens": list(row["required_source_tokens"]),
            "quotation_preserves_source_syntax_exactly": True,
            "semantic_native_correspondence_asserted": False,
        }
        source_binding["quotation_identity"] = identity(source_binding)
        validity_target = {
            "schema": "sft-v3-openai-2026-source-validity-target/2",
            "claim_id": row["claim_id"],
            "target": proposition,
            "definition": {
                "exact_source_bound": True,
                "exact_quantifiers_and_conjuncts_retained": True,
                "registered_axioms_must_be_empty": True,
                "free_parameters_must_be_empty": True,
                "every_proof_object_must_use_the_admitted_sft_domain": True,
                "every_premise_must_trace_to_the_sft_root": True,
                "candidate_grammar_must_be_complete": True,
                "four_adverse_controls_must_pass": True,
                "implementation_distinct_validation_must_pass": True,
                "model_admission_receipt_must_exist": True,
            },
            "registered_negation": negation,
            "necessary_source_component": row["necessary_component"],
            "domain_contradiction": row["domain_contradiction"],
            "native_reconstruction": {
                "claim_id": original["claim_id"],
                "native_formula": original["native_formula"],
                "classification": "distinct_sft_native_reconstruction_only",
                "transfers_source_validity": False,
            },
        }
        validity_target["target_identity"] = identity(validity_target)
        registration = {
            "$schema": "../../governance/claim.schema.json",
            "claim_id": row["claim_id"],
            "title": f"SFT disproof of source-artifact validity: {source_record['declaration']}",
            "branch": original["owner"],
            "statement": negation,
            "dependencies": list(dependencies),
            "candidate_grammar": {
                "generator": "Compose exact source custody, exact quotation, exposed axiom/carrier evidence, pre-existing admission laws, a complete contradiction chain, executable checks and a strict native/source nontransfer boundary; no verdict coordinate.",
                "boundary": proposition,
                "completeness_certificate": "pending_frozen_derivation",
            },
            "excluded_inputs": [
                "a paraphrased declaration or changed quantifier order",
                "a missing receipt used as the contradiction",
                "carrier inadmissibility presented as the logical negation of the mathematical conclusion rather than as a failure of SFT validity",
                "the separate SFT-native reconstruction transferred back to the source artifact",
                "an outcome or verdict coordinate in the candidate grammar",
            ],
            "empirical_protocol": None,
            "intended_certificate": "Exact source quotation, actual contradiction under the defined SFT-validity proposition, complete root trace, executable checks, independent implementation and Lean 4 theorem with empty axiom audit.",
            "provenance_classes": ["forward_forcing"],
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
            "registered_by": "Maria Smith",
            "registration_date": "2026-08-02",
            "status": "registered",
        }
        write_json(package / "source_binding_v2.json", source_binding)
        write_json(package / "source_validity_target_v2.json", validity_target)
        write_json(package / "registration.json", registration)
        (package / "execution.py").write_text(
            "from pathlib import Path\n"
            "from sft.openai_2026.source_validity_execution_v2 import build_execution as assemble\n\n\n"
            "def build_execution(root: Path):\n"
            f"    return assemble(root, {row['claim_id']!r}, Path(__file__).resolve())\n",
            encoding="utf-8",
        )
        registry_rows.append({
            "ordinal": order,
            "atomic_id": row["atomic_id"],
            "claim_id": row["claim_id"],
            "owner": original["owner"],
            "declaration": source_record["declaration"],
            "source_file": source_record["source_file"],
            "source_statement_hash": original["source_statement_hash"],
            "source_file_sha256": source_record["source_file_sha256"],
            "source_declared_axioms": source_record["upstream_declared_axioms"],
            "source_quantifier_and_conjunct_order": source_record["exact_quantifier_and_conjunct_order"],
            "sft_validity_proposition": proposition,
            "registered_negation": negation,
            "necessary_source_component": row["necessary_component"],
            "domain_contradiction": row["domain_contradiction"],
            "governing_preexisting_claims": list(dependencies),
            "required_source_tokens": list(row["required_source_tokens"]),
            "reconstruction_claim_id": original["claim_id"],
            "reconstruction_is_distinct": True,
            "registered_outcome": None,
        })
    registry = {
        "schema": "sft-v3-openai-2026-source-validity-registry/2",
        "registry_date": "2026-08-02",
        "source_capture_id": v1["source_capture_id"],
        "source_commit": v1["source_commit"],
        "target_semantics": "Disprove SFTValid(exact submitted artifact), not the truth of a substituted SFT-native proposition.",
        "validity_definition_owner": "SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001",
        "verdict_selection_rule": "No verdict coordinate exists. Each registered theorem is the explicit negation of one fixed source-validity proposition and must be reached by an assumption-to-contradiction chain.",
        "counts": {"formal_declarations": 12, "mathematics": 9, "computation": 2, "quantum_computation": 1},
        "rows": registry_rows,
    }
    registry["registry_identity"] = identity(registry)
    write_json(V2_REGISTRY, registry)
    verify_seals()
    print(json.dumps({
        "status": "REGISTERED",
        "claims": len(registry_rows),
        "owners": registry["counts"],
        "registry": V2_REGISTRY.relative_to(ROOT).as_posix(),
        "registry_identity": registry["registry_identity"],
        "outcomes_assigned": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
