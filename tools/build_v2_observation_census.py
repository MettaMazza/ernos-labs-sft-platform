#!/usr/bin/env python3
"""Build the complete V2 observational reconstruction census.

This tool reads the bound 407-step OneFoldMaster as prior observational data.
It never imports old executable code into a V3 derivation.  The output prevents
branch inventories from omitting a prior result merely because it was not in a
later categorical checklist.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
LINEAGE = ROOT / "census/lineage_reconciliation.json"
OUTPUT = ROOT / "audits/v2_407_step_observation_census.json"


EXPLICIT_MAPPINGS: dict[int, tuple[str, ...]] = {
    4: ("SFT-PHYS-STRUCT-GENERATOR-THREE-001",),
    5: (
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001",
    ),
    6: (
        "SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001",
        "SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001",
    ),
    7: ("SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001",),
    14: ("SFT-PHYS-VALIDATION-CHARGED-LEPTON-KOIDE-001",),
    32: ("SFT-PHYS-SPACE-DIMENSION-THREE-001",),
    43: (
        "SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001",
        "SFT-PHYS-FIELD-INVERSE-SQUARE-001",
        "SFT-PHYS-VALIDATION-INVERSE-SQUARE-001",
    ),
    47: ("SFT-MAT-CRYST-CUBIC-COORDINATION-001",),
    49: (
        "SFT-MAT-CRYST-TRANSLATION-001",
        "SFT-MAT-CRYST-ROTATION-RESTRICTION-001",
        "SFT-MAT-CRYST-SYSTEMS-001",
        "SFT-MAT-CRYST-BRAVAIS-001",
    ),
    50: ("SFT-CHEM-AB-ACID-BASE-001", "SFT-CHEM-AB-PROTON-TRANSFER-001"),
    52: (
        "SFT-MAT-SC-PAIR-001",
        "SFT-MAT-SC-ZERO-RESISTANCE-001",
        "SFT-MAT-SC-MEISSNER-001",
        "SFT-MAT-SC-FLUX-QUANTIZATION-001",
        "SFT-MAT-SC-JOSEPHSON-001",
    ),
    54: ("SFT-MAT-ELEC-BAND-GAP-001", "SFT-MAT-ELEC-CONDUCTOR-CLASS-001"),
    72: ("SFT-MAT-CRYST-PHONON-001",),
    73: ("SFT-CHEM-STEREO-CHIRALITY-001", "SFT-CHEM-STEREO-ENANTIOMER-001"),
    74: ("SFT-MAT-MAG-FERROMAGNETISM-001", "SFT-MAT-MAG-ANTIFERROMAGNETISM-001"),
    75: (
        "SFT-MAT-ELEC-CARRIER-DUALITY-001",
        "SFT-MAT-SEMI-DOPING-001",
        "SFT-MAT-SEMI-PN-TYPE-001",
        "SFT-MAT-SEMI-JUNCTION-001",
        "SFT-MAT-SEMI-TRANSPORT-001",
    ),
    77: ("SFT-CHEM-CAT-CATALYST-001", "SFT-CHEM-CAT-PATHWAY-001"),
    78: ("SFT-CHEM-ELECTRONEGATIVITY-001", "SFT-CHEM-BOND-POLARITY-001"),
    112: ("SFT-CHEM-MOL-INTERMOLECULAR-001",),
    127: ("SFT-PHYS-ATOMIC-CELL-ORBIT-CAPACITY-001",),
    133: (
        "SFT-MAT-CRYST-ROTATION-RESTRICTION-001",
        "SFT-MAT-CRYST-RECIPROCAL-001",
        "SFT-MAT-CRYST-QUASICRYSTAL-001",
    ),
    137: ("SFT-MAT-SF-SUPERFLUID-001", "SFT-MAT-SF-CIRCULATION-001"),
    142: (
        "SFT-CHEM-SPEC-INFRARED-001",
        "SFT-CHEM-SPEC-UVVIS-001",
        "SFT-CHEM-SPEC-ROT-VIB-001",
    ),
    143: ("SFT-MAT-TOPO-INVARIANT-001", "SFT-MAT-TOPO-BULK-BOUNDARY-001"),
    151: (
        "SFT-PHYS-NUCLEAR-COLOUR-COUPLING-001",
        "SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001",
        "SFT-PHYS-VALIDATION-NUCLEAR-CLOSURES-001",
    ),
    156: (
        "SFT-CHEM-BOND-CHEMICAL-BOND-001",
        "SFT-CHEM-BOND-COVALENT-001",
        "SFT-CHEM-BOND-IONIC-001",
        "SFT-CHEM-BOND-METALLIC-001",
    ),
    157: (
        "SFT-CHEM-ELEM-PERIODIC-ORDER-001",
        "SFT-CHEM-ELEM-PERIODIC-RECURRENCE-001",
        "SFT-CHEM-ELEM-GROUP-PERIOD-001",
    ),
    167: (
        "SFT-CHEM-KIN-ACTIVATION-001",
        "SFT-CHEM-KIN-RATE-001",
        "SFT-CHEM-KIN-ORDER-001",
    ),
    176: (
        "SFT-CHEM-STEREO-CHIRALITY-001",
        "SFT-CHEM-STEREO-ENANTIOMER-001",
        "SFT-CHEM-STEREO-DIASTEREOMER-001",
    ),
    193: (
        "SFT-MAT-MECH-STRESS-STRAIN-001",
        "SFT-MAT-MECH-ELASTICITY-001",
        "SFT-MAT-MECH-PLASTICITY-001",
        "SFT-MAT-MECH-SLIP-001",
        "SFT-MAT-MECH-MODULUS-001",
        "SFT-MAT-MECH-STRENGTH-HARDNESS-001",
        "SFT-MAT-MECH-FRACTURE-001",
        "SFT-MAT-MECH-FATIGUE-CREEP-001",
    ),
    249: ("SFT-CHEM-THERMO-REACTION-001", "SFT-CHEM-THERMO-DIRECTION-001"),
    266: (
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001",
        "SFT-CHEM-PRED-PERIODIC-ENDPOINT-001",
    ),
    267: (
        "SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001",
        "SFT-CHEM-PRED-G-BLOCK-001",
        "SFT-CHEM-PRED-SMITHIUM-001",
    ),
    293: (
        "SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001",
        "SFT-PHYS-VALIDATION-NUCLEAR-CLOSURES-001",
        "SFT-CHEM-PRED-SMITHIUM-001",
    ),
    291: ("SFT-MAT-CRYST-QUASICRYSTAL-001",),
    298: (
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001",
    ),
    302: (
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001",
    ),
    325: ("SFT-COMP-FORM-STATE-TRANSITION-001",),
    326: ("SFT-INFO-SYMBOL-DISTINCTION-001",),
    327: ("SFT-COMP-CPLX-INPUT-SIZE-001", "SFT-COMP-CPLX-TIME-SPACE-001"),
    328: ("SFT-INFO-ENCODING-DECODING-001",),
    329: ("SFT-INFO-QUANTITY-001", "SFT-INFO-CONSERVATION-LOSS-001"),
    330: ("SFT-COMP-FORM-OPERATIONAL-PROCESS-001", "SFT-COMP-FORM-COMPOSITION-001"),
    331: ("SFT-COMP-FORM-LANGUAGE-GRAMMAR-001",),
    332: ("SFT-COMP-FORM-AUTOMATON-001",),
    333: ("SFT-COMP-FORM-REWRITING-001",),
    334: ("SFT-COMP-FORM-RECURSIVE-FUNCTION-001", "SFT-COMP-FORM-LAMBDA-CALCULUS-001"),
    335: ("SFT-COMP-FORM-MODEL-EQUIVALENCE-001",),
    336: ("SFT-COMP-FORM-UNIVERSALITY-001",),
    337: ("SFT-COMP-CBL-RECOGNITION-DECISION-001",),
    338: ("SFT-COMP-CBL-HALTING-001",),
    339: ("SFT-COMP-CBL-ENUMERATION-001",),
    340: ("SFT-COMP-CBL-REDUCTION-001",),
    341: ("SFT-COMP-CBL-UNDECIDABILITY-001",),
    342: ("SFT-COMP-CBL-RELATIVE-ORACLE-001",),
    343: ("SFT-COMP-CBL-HYPERCOMPUTATION-LIMIT-001",),
    344: ("SFT-COMP-CBL-DEGREES-001",),
    345: ("SFT-COMP-CBL-INCOMPLETENESS-001",),
    346: ("SFT-COMP-CPLX-CIRCUIT-RESOURCE-001",),
    347: ("SFT-COMP-CPLX-COMMUNICATION-QUERY-001",),
    348: ("SFT-COMP-CPLX-RANDOMNESS-001",),
    349: ("SFT-COMP-CPLX-REVERSIBILITY-COST-001",),
    350: ("SFT-COMP-CPLX-PARALLEL-001",),
    351: ("SFT-QUANTUM-COMPLEXITY-001",),
    352: ("SFT-COMP-CPLX-BOUNDS-001", "SFT-COMP-CPLX-REDUCTION-COMPLETENESS-001"),
    353: ("SFT-COMP-CPLX-AVERAGE-WORST-001",),
    354: ("SFT-COMP-CPLX-APPROXIMATION-001",),
    355: ("SFT-COMP-CPLX-PARAMETERIZED-001",),
    356: ("SFT-COMP-CPLX-DESCRIPTIVE-001",),
    357: ("SFT-COMP-ALG-SEARCH-ORDER-001",),
    358: ("SFT-COMP-ALG-ARITHMETIC-001",),
    359: ("SFT-COMP-ALG-STRINGS-SEQUENCES-001",),
    360: ("SFT-COMP-ALG-TREES-GRAPHS-001",),
    361: ("SFT-COMP-ALG-ALGEBRAIC-GEOMETRIC-001",),
    362: ("SFT-COMP-ALG-ALGEBRAIC-GEOMETRIC-001",),
    363: ("SFT-COMP-ALG-DYNAMIC-PROGRAMMING-001",),
    364: ("SFT-COMP-ALG-OPTIMIZATION-001",),
    365: ("SFT-COMP-ALG-RANDOMIZED-001",),
    366: ("SFT-COMP-ALG-PARALLEL-001",),
    367: ("SFT-COMP-ALG-DISTRIBUTED-001",),
    368: ("SFT-COMP-ALG-ONLINE-STREAMING-001",),
    369: ("SFT-COMP-ALG-NUMERICAL-001",),
    370: ("SFT-COMP-ALG-SYMBOLIC-001",),
    371: ("SFT-COMP-ALG-APPROXIMATE-001",),
    372: ("SFT-QUANTUM-ALGORITHMS-001",),
    373: ("SFT-COMP-SEM-SYNTAX-001",),
    374: ("SFT-COMP-SEM-BINDING-SUBSTITUTION-001",),
    375: ("SFT-COMP-SEM-EVALUATION-001",),
    376: ("SFT-COMP-SEM-OPERATIONAL-DENOTATIONAL-001",),
    377: ("SFT-COMP-SEM-TYPE-001",),
    378: ("SFT-COMP-SEM-PROGRAM-EQUIVALENCE-001",),
    379: ("SFT-COMP-SEM-TERMINATION-001", "SFT-COMP-SEM-CORRECTNESS-001"),
    380: ("SFT-COMP-SEM-SPECIFICATION-001",),
    381: ("SFT-COMP-SEM-TRANSFORMATION-001",),
    382: ("SFT-COMP-SEM-COMPILATION-001",),
    383: ("SFT-COMP-SEM-VERIFICATION-001",),
    384: ("SFT-INFO-ENTROPY-UNCERTAINTY-001",),
    385: ("SFT-INFO-COMPRESSION-REDUNDANCY-001",),
    386: ("SFT-INFO-CHANNEL-CAPACITY-001",),
    387: ("SFT-INFO-NOISE-ERROR-001",),
    388: ("SFT-INFO-CODING-001",),
    389: ("SFT-INFO-MUTUAL-CONDITIONAL-001",),
    390: ("SFT-INFO-CLASSICAL-PROBABILISTIC-001", "SFT-INFO-QUANTUM-CORRESPONDENCE-001"),
    391: (
        "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001",
        "SFT-MATH-COMBINATORICS-001", "SFT-MATH-GRAPH-NETWORK-001",
        "SFT-MATH-ALGEBRA-001", "SFT-MATH-ORDER-LATTICE-001",
        "SFT-MATH-GEOMETRY-TOPOLOGY-001", "SFT-MATH-PROBABILITY-STATISTICS-001",
        "SFT-MATH-OPTIMIZATION-001", "SFT-MATH-DYNAMICAL-SYSTEMS-001",
        "SFT-MATH-LOGIC-PROOF-001", "SFT-MATH-CATEGORY-TYPE-COMPOSITION-001",
    ),
    392: ("SFT-COMP-FORM-LAMBDA-CALCULUS-001", "SFT-COMP-FORM-CIRCUIT-001"),
    393: tuple(
        f"SFT-COMP-DIST-{name}-001" for name in (
            "CONCURRENCY", "CAUSALITY", "SYNCHRONIZATION", "COMMUNICATION",
            "PARTIAL-ORDER", "CONSENSUS", "AGREEMENT-IMPOSSIBILITY",
            "REPLICATION-CONSISTENCY", "FAULT-MODEL", "DISTRIBUTED-KNOWLEDGE",
            "LOCALITY", "NETWORK-COMPUTATION",
        )
    ),
    394: tuple(
        f"SFT-COMP-SEC-{name}-001" for name in (
            "ONE-WAYNESS", "SECRECY", "INTEGRITY", "AUTHENTICATION", "HASHING",
            "COMMITMENT", "SIGNATURE", "PROOF-KNOWLEDGE", "ZERO-KNOWLEDGE",
            "MULTIPARTY", "ADVERSARIAL", "SECURITY-DEFINITION", "POST-QUANTUM-BOUNDARY",
        )
    ),
    395: tuple(
        f"SFT-COMP-LEARN-{name}-001" for name in (
            "INFERENCE", "CLASSIFICATION-PREDICTION", "REPRESENTATION", "GENERALIZATION",
            "SAMPLE-COMPLEXITY", "LEARNING-OPTIMIZATION", "INDUCTION", "SEARCH-PLANNING",
            "REINFORCEMENT", "MULTIAGENT", "ADAPTATION", "LEARNING-LIMITS",
            "INTERPRETABILITY-VERIFICATION", "CLASSICAL-LEARNING",
        )
    ),
    396: tuple(
        f"SFT-COMP-SCI-{name}-001" for name in (
            "EXACT-APPROXIMATE", "STABILITY", "ERROR-PROPAGATION", "DISCRETIZATION",
            "CONVERGENCE", "SYMBOLIC", "SIMULATION", "COMPUTATIONAL-DYNAMICS",
            "INVERSE-PROBLEM", "COMPUTATIONAL-STATISTICS", "HIGH-DIMENSIONAL",
            "MANY-BODY", "MATHEMATICAL-MODELLING",
        )
    ),
    397: (
        "SFT-QUANTUM-REVERSIBLE-MODEL-001", "SFT-QUANTUM-INFORMATION-UNIT-001",
        "SFT-QUANTUM-STATE-COMPOSITION-001", "SFT-QUANTUM-SUPERPOSITION-001",
        "SFT-QUANTUM-PHASE-INTERFERENCE-001", "SFT-QUANTUM-ENTANGLEMENT-001",
        "SFT-QUANTUM-MEASUREMENT-001",
    ),
    398: (
        "SFT-QUANTUM-GATE-001", "SFT-QUANTUM-CIRCUIT-001",
        "SFT-QUANTUM-UNIVERSALITY-001", "SFT-QUANTUM-ALGORITHMS-001",
        "SFT-QUANTUM-COMPLEXITY-001",
    ),
    399: (
        "SFT-QUANTUM-COMMUNICATION-001", "SFT-QUANTUM-CODING-001",
        "SFT-QUANTUM-ERROR-CORRECTION-001", "SFT-QUANTUM-FAULT-TOLERANCE-001",
    ),
    400: (
        "SFT-QUANTUM-SIMULATION-001", "SFT-QUANTUM-VERIFICATION-001",
        "SFT-QUANTUM-LEARNING-001", "SFT-QUANTUM-CLASSICAL-CORRESPONDENCE-001",
        "SFT-QUANTUM-LIMITS-001",
    ),
    401: ("SFT-FOUNDATION-FORM-GRAMMAR-001", "SFT-FOUNDATION-FORM-ENFORCEMENT-001"),
    402: ("SFT-FOUNDATION-FORM-GRAMMAR-001",),
    403: ("SFT-QUANTUM-ERROR-CORRECTION-001", "SFT-QUANTUM-FAULT-TOLERANCE-001"),
    407: ("SFT-QUANTUM-FAULT-TOLERANCE-001",),
}


# Mapping proves that an owning V3 claim exists.  It does not by itself prove
# that the complete prior statement has been reconstructed at the same formal
# and empirical strength.  Overrides preserve a known adverse result rather
# than letting an admitted formal subclaim silently close a larger V2 step.
DISPOSITION_OVERRIDES: dict[int, dict[str, object]] = {
    6: {
        "status": "closed_by_formal_reconstruction_and_empirically_admitted_terminal_refinement",
        "closed": True,
        "reason": (
            "The exact V2 cubic invariants were independently reconstructed. Their first exact "
            "CODATA claim failed and remains preserved; the later disclosed observational derivation "
            "generated a terminal alpha/depth refinement and passed structural, independent and both-row "
            "empirical gates in one admission run."
        ),
        "failed_claim_id": "SFT-PHYS-VALIDATION-CHARGED-LEPTON-CUBIC-001",
        "failed_receipt_hash": "sha256:2b7023f72254b172e690e820cd99fa75810c261b6956bfc40dbb22ce63c66439",
        "admitted_claim_id": "SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001",
        "admitted_receipt_hash": "sha256:c74f9c45eab7c232ebf85fe2fd5aea24f07d167df3857dad50ffcc5c34732294",
    },
    7: {
        "status": "closed_by_joint_structural_and_empirical_admission",
        "closed": True,
        "reason": (
            "The exact leading 27/5 and native period-five deepening 279/52 were generated without density "
            "inputs and both passed the complete Planck cold-dark/baryon density interval in the same engine run."
        ),
        "admitted_claim_id": "SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001",
        "admitted_receipt_hash": "sha256:38b06863d5a59f8f8ea17fee7a0a1d5ff1fdcd0c6f7b9de3e9f635705d4f8cc2",
    },
    14: {
        "status": "closed_by_exact_postseal_empirical_validation",
        "closed": True,
        "reason": (
            "The exact two-thirds result is inherited from the independently reconstructed cubic invariants; "
            "both complete CODATA mass-ratio intervals were propagated through exact rational square-root "
            "enclosures and the sealed value lies inside the resulting conservative interval."
        ),
        "admitted_claim_id": "SFT-PHYS-VALIDATION-CHARGED-LEPTON-KOIDE-001",
        "admitted_receipt_hash": "sha256:369a1e48d622bba0f3e4abc1e89fef8553b17097c3d8c4427afca26386f6cbf9",
    },
}


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def excerpt(body: str, label: str) -> str | None:
    match = re.search(
        rf"\*\*{re.escape(label)}\.\*\*\s*(.+?)(?=\n\n\*\*|\n### Step|\Z)",
        body,
        flags=re.DOTALL,
    )
    if match is None:
        return None
    return " ".join(match.group(1).split())


def main() -> None:
    lineage = json.loads(LINEAGE.read_text(encoding="utf-8"))
    source = next(
        row for row in lineage["source_custody"]
        if row["source_id"] == "SFT-V2-ONE-FOLD-MASTER-407"
    )
    source_path = Path(source["path"])
    raw = source_path.read_bytes()
    if digest_bytes(raw) != "sha256:" + source["sha256"]:
        raise SystemExit("bound V2 source hash changed")
    text = raw.decode("utf-8")
    matches = tuple(re.finditer(r"^### Step (\d+) — (.+)$", text, flags=re.MULTILINE))
    if tuple(int(match.group(1)) for match in matches) != tuple(range(1, 408)):
        raise SystemExit("V2 step sequence is incomplete or out of order")

    memberships: dict[int, list[str]] = {step: [] for step in range(1, 408)}
    for group in lineage["named_consequence_groups"]:
        for step in group["source_steps"]:
            memberships[step].append(group["group_id"])

    admitted = {
        row["claim_id"] for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]
        if row.get("model_admitted")
    }
    rows: list[dict[str, object]] = []
    for index, match in enumerate(matches):
        step = int(match.group(1))
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.start():end].rstrip() + "\n"
        body = text[match.end():end]
        mapped = EXPLICIT_MAPPINGS.get(step, ())
        missing_claims = tuple(claim_id for claim_id in mapped if claim_id not in admitted)
        mapping_status = (
            "mapped_to_current_admitted_claims" if mapped and not missing_claims
            else "mapped_claim_missing" if missing_claims
            else "blocking_explicit_disposition_required"
        )
        override = DISPOSITION_OVERRIDES.get(step)
        if override is not None:
            disposition = dict(override)
        elif mapping_status == "mapped_to_current_admitted_claims":
            disposition = {
                "status": "mapped_same_strength_review_pending",
                "closed": False,
                "reason": "Claim identities are mapped; an explicit same-strength formal and empirical comparison is still required.",
            }
        else:
            disposition = {
                "status": mapping_status,
                "closed": False,
                "reason": "No complete same-strength V3 disposition is registered.",
            }
        rows.append({
            "step": step,
            "title": match.group(2).strip(),
            "source_block_sha256": digest_bytes(block.encode("utf-8")),
            "prior_result_observation": excerpt(body, "What it does"),
            "prior_measurement_observation": excerpt(body, "To measurement"),
            "recorded_check_lines": [
                line.strip() for line in body.splitlines()
                if line.strip().startswith("ok    ")
            ],
            "named_group_memberships": sorted(memberships[step]),
            "explicit_v3_claim_ids": list(mapped),
            "explicit_mapping_status": mapping_status,
            "missing_mapped_claim_ids": list(missing_claims),
            "same_strength_disposition": disposition,
        })

    payload = {
        "schema": "sft-v3-prior-observation-census/1",
        "status": "open_blocking_until_every_step_has_explicit_v3_disposition",
        "source_id": source["source_id"],
        "source_sha256": "sha256:" + source["sha256"],
        "source_step_count": len(rows),
        "policy": {
            "prior_results_are_observational_data": True,
            "prior_results_define_reconstruction_obligations": True,
            "prior_answer_artifacts_may_enter_v3_derivation": False,
            "prior_observation_may_select_v3_candidate_or_survivor": False,
            "branch_completion_requires_every_assigned_step_closed": True,
        },
        "mapped_step_count": sum(row["explicit_mapping_status"] == "mapped_to_current_admitted_claims" for row in rows),
        "unmapped_step_count": sum(row["explicit_mapping_status"] == "blocking_explicit_disposition_required" for row in rows),
        "same_strength_closed_step_count": sum(bool(row["same_strength_disposition"]["closed"]) for row in rows),
        "same_strength_open_step_count": sum(not bool(row["same_strength_disposition"]["closed"]) for row in rows),
        "steps": rows,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    print(f"steps={len(rows)} mapped={payload['mapped_step_count']} unmapped={payload['unmapped_step_count']}")


if __name__ == "__main__":
    main()
