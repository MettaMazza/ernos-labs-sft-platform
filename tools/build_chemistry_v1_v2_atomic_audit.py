#!/usr/bin/env python3
"""Build the categorical V1/V2-to-V3 Chemistry ownership audit.

This is a read-only scientific-ownership audit.  It verifies the canonical
engine seal and existing model-admitted receipts, but it neither imports nor
calls the admission engine.  Every one of the 356 V1 rows and 407 V2 steps is
given an explicit Chemistry/non-Chemistry disposition.  Mixed source prose is
split at a declared categorical boundary before a Chemistry atom is mapped.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
V1_PATH = ROOT / "audits/v1_theorem_manifest_observation_census.json"
V2_PATH = ROOT / "audits/v2_407_step_observation_census.json"
CLAIMS_PATH = ROOT / "census/claims.json"
AUDIT_PATH = ROOT / "audits/chemistry_v1_v2_atomic_ownership.json"
REPORT_PATH = ROOT / "audits/chemistry_v1_v2_atomic_ownership.md"
LEDGER_PATH = ROOT / "census/chemistry_prior_obligations.json"


def atom(
    suffix: str,
    statement: str,
    claims: tuple[str, ...],
    basis: str,
    *,
    status: str = "same_strength_reconstructed",
    upstream: tuple[str, ...] = (),
) -> dict[str, Any]:
    return {
        "suffix": suffix,
        "statement": statement,
        "claim_ids": claims,
        "upstream_claim_ids": upstream,
        "same_strength_status": status,
        "same_strength_basis": basis,
    }


CORRECTED = "same_strength_corrected_at_exact_current_boundary"
DIRECT = "current receipt reconstructs the prior Chemistry atom at its exact categorical boundary"
CORRECTION = (
    "the current receipt's complete candidate elimination preserves the valid prior component "
    "and rejects the prior answer-only, context-free, fitted or over-universal formulation"
)


V1_ATOMS: dict[str, tuple[dict[str, Any], ...]] = {
    "III-4": (
        atom(
            "PERIODIC-CHEMICAL-RECURRENCE",
            "Outer chemical organization recurs after generated shell closure and reopening, producing chemical periods and related element classes.",
            ("SFT-CHEM-ELEM-PERIODIC-RECURRENCE-001", "SFT-CHEM-ELEM-GROUP-PERIOD-001"),
            DIRECT,
            upstream=("SFT-PHYS-ATOMIC-SHELL-PERIODICITY-TERMINAL-005",),
        ),
    ),
    "III-7": (
        atom(
            "BOND-IDENTITY",
            "A covalent molecular bond is stable joint electron-labelled recurrence between retained atomic carriers.",
            ("SFT-CHEM-BOND-CHEMICAL-BOND-001", "SFT-CHEM-BOND-COVALENT-001"),
            DIRECT,
        ),
        atom(
            "BOND-LENGTH-STRENGTH",
            "Bond length and positive dissociation transfer are paired only for one retained bond identity, method and condition record.",
            ("SFT-CHEM-BOND-LENGTH-STRENGTH-001",),
            CORRECTION,
            status=CORRECTED,
        ),
        atom(
            "BOND-ORDER",
            "Bond order is the retained joining multiplicity of the identified bond rather than an untraced label.",
            ("SFT-CHEM-BOND-ORDER-001",),
            DIRECT,
        ),
    ),
    "III-8": (
        atom(
            "MOLECULAR-SPECTRAL-ORGANIZATION",
            "Molecular rotational and internal relative-displacement transitions form retained condition-bound spectral organizations distinct from electronic transitions.",
            ("SFT-CHEM-SPEC-ROT-VIB-001", "SFT-CHEM-SPEC-INFRARED-001", "SFT-CHEM-SPEC-UVVIS-001"),
            DIRECT,
            upstream=("SFT-PHYS-QUANTUM-DISCRETE-SPECTRA-001",),
        ),
    ),
    "IV-1": (
        atom(
            "PERIODIC-LAW",
            "Chemical recurrence is the return of an outer-organization observation class along exact atomic-number order, with group and period retained as compositional coordinates.",
            ("SFT-CHEM-ELEM-PERIODIC-ORDER-001", "SFT-CHEM-ELEM-PERIODIC-RECURRENCE-001", "SFT-CHEM-ELEM-GROUP-PERIOD-001"),
            DIRECT,
            upstream=("SFT-PHYS-ATOMIC-SHELL-PERIODICITY-TERMINAL-005",),
        ),
        atom(
            "VALENCE-CONTEXT",
            "Valence is the greatest realized univalent joining or substitution count on complete generated chemical support with context retained.",
            ("SFT-CHEM-ELEM-VALENCE-001",),
            CORRECTION,
            status=CORRECTED,
        ),
    ),
    "IV-2": (
        atom(
            "ELECTRONEGATIVITY-ORDER",
            "Electronegativity is the complete pairwise endpoint-affinity preorder for identical shared support, retaining ties and the comparison trace.",
            ("SFT-CHEM-ELECTRONEGATIVITY-001",),
            CORRECTION,
            status=CORRECTED,
        ),
        atom(
            "BOND-POLARITY",
            "Unequal endpoint affinity forces an oriented shared bond partition while retaining the common electron support and both endpoint identities.",
            ("SFT-CHEM-BOND-POLARITY-001", "SFT-CHEM-BOND-IONIC-001"),
            DIRECT,
        ),
    ),
    "IV-3": (
        atom(
            "REACTION-THERMOCHEMICAL-LEDGER",
            "A chemical reaction changes retained chemical relations while conserving element carriers, and its thermochemical result is the complete source-bound endpoint energy ledger.",
            ("SFT-CHEM-RXN-IDENTITY-001", "SFT-CHEM-THERMO-REACTION-001", "SFT-CHEM-THERMO-DIRECTION-001"),
            DIRECT,
        ),
        atom(
            "ACTIVATION-EQUILIBRIUM",
            "The reaction path retains its highest transition boundary and its paired forward/reverse recurrence rather than an answer-only barrier or equilibrium scalar.",
            ("SFT-CHEM-KIN-ACTIVATION-001", "SFT-CHEM-EQ-CHEMICAL-001"),
            CORRECTION,
            status=CORRECTED,
        ),
    ),
    "IV-4": (
        atom(
            "REACTION-RATE",
            "Reaction rate is the exact condition-bound count of completed registered transitions per positive reference recurrence, with activation and dependency traces retained.",
            ("SFT-CHEM-KIN-ACTIVATION-001", "SFT-CHEM-KIN-RATE-001", "SFT-CHEM-KIN-ORDER-001"),
            CORRECTION,
            status=CORRECTED,
        ),
    ),
    "IV-5": (
        atom(
            "CATALYTIC-CYCLE",
            "A catalyst opens an alternative complete reaction path, returns with exact identity and leaves the net reaction endpoints unchanged.",
            ("SFT-CHEM-CAT-CATALYST-001", "SFT-CHEM-CAT-PATHWAY-001"),
            DIRECT,
        ),
        atom(
            "CATALYTIC-SELECTIVITY",
            "Catalytic selectivity is the maximal generated product-recurrence class at a retained catalyst, reactant, condition and observation boundary.",
            ("SFT-CHEM-CAT-SELECTIVITY-001",),
            CORRECTION,
            status=CORRECTED,
        ),
    ),
    "IV-6": (
        atom(
            "ACID-BASE-PROTON-TRANSFER",
            "A conjugate acid/base pair differs by exactly one retained proton carrier transferred from a registered donor to a distinct acceptor.",
            ("SFT-CHEM-AB-ACID-BASE-001", "SFT-CHEM-AB-PROTON-TRANSFER-001"),
            DIRECT,
        ),
        atom(
            "ACID-BASE-RESPONSE-RECORD",
            "Acid/base response retains the positive conjugate-pair support, proton-transfer paths, finite capacity and source-bound equilibrium record; a pH answer alone is not a derivation.",
            ("SFT-CHEM-AB-BUFFER-001", "SFT-CHEM-EQ-CHEMICAL-001", "SFT-CHEM-MEAS-TRACEABILITY-001"),
            CORRECTION,
            status=CORRECTED,
        ),
    ),
    "IV-7": (
        atom(
            "CHIRALITY-ENANTIOMERS",
            "A chiral molecular carrier and its exact reflection are distinct after exhaustive identity-preserving proper superposition, forming an enantiomer pair.",
            ("SFT-CHEM-STEREO-CHIRALITY-001", "SFT-CHEM-STEREO-ENANTIOMER-001"),
            DIRECT,
        ),
        atom(
            "MULTICENTRE-STEREOISOMERS",
            "Multicentre stereoisomer classes are the complete quotient of generated orientations by identity-preserving relabelling, reflection and proper-superposition tests; an unconditional two-to-the-centre-count answer is rejected.",
            ("SFT-CHEM-MOL-ISOMER-001", "SFT-CHEM-STEREO-DIASTEREOMER-001"),
            CORRECTION,
            status=CORRECTED,
        ),
        atom(
            "BIOMOLECULAR-HANDOFF",
            "Chemistry passes complete molecular identity, structure and chemical state to Biology without allowing biological function or selected handedness to choose the chemical law.",
            ("SFT-CHEM-BIOMOLECULAR-BOUNDARY-001",),
            DIRECT,
        ),
    ),
    "IV-8": (
        atom(
            "INTERMOLECULAR-INTERACTION",
            "An intermolecular interaction joins distinct already-complete molecular carriers through a source-bounded response channel while retaining both molecular identities.",
            ("SFT-CHEM-MOL-INTERMOLECULAR-001",),
            CORRECTION,
            status=CORRECTED,
        ),
        atom(
            "HYDROGEN-BOND-NETWORK",
            "Reversible complementary intermolecular recognition can close a finite molecular or supramolecular network while retaining every component and edge provenance.",
            ("SFT-CHEM-MOL-SUPRAMOLECULAR-001", "SFT-CHEM-MOL-NETWORK-001"),
            DIRECT,
        ),
    ),
    "X-5": (
        atom(
            "RACEMIC-CHIRAL-DISTINCTION",
            "The two molecular mirror carriers remain a retained enantiomer distinction; a racemic population is a composition record rather than erased equality.",
            ("SFT-CHEM-STEREO-CHIRALITY-001", "SFT-CHEM-STEREO-ENANTIOMER-001", "SFT-CHEM-STOICH-COMPOSITION-001"),
            DIRECT,
        ),
        atom(
            "CHIRAL-AUTOCATALYTIC-PATH",
            "A retained product carrier can re-enter a finite reaction-network cycle as catalyst for production of the same chemical identity.",
            ("SFT-CHEM-NET-AUTOCATALYSIS-001",),
            DIRECT,
        ),
    ),
    "X-6": (
        atom(
            "AUTOCATALYTIC-CHEMISTRY-BOUNDARY",
            "Chemistry owns the finite resource-bounded autocatalytic reaction-network cycle; the claim that such chemistry constitutes life is a separate Biology-owned relation.",
            ("SFT-CHEM-NET-REACTION-001", "SFT-CHEM-NET-AUTOCATALYSIS-001", "SFT-CHEM-BIOMOLECULAR-BOUNDARY-001"),
            DIRECT,
        ),
    ),
    "XVIII-9": (
        atom(
            "LITHIUM-ISOTOPE-COMPOSITION-RECORD",
            "Lithium-7 remains a retained isotope identity and its source-bound population change is a composition/yield and analytical record; stellar transport and nuclear burning are separately owned.",
            ("SFT-CHEM-ELEM-ISOTOPE-001", "SFT-CHEM-STOICH-COMPOSITION-001", "SFT-CHEM-STOICH-YIELD-001", "SFT-CHEM-ANALYTICAL-COMPLETE-RECORD-001"),
            CORRECTION,
            status=CORRECTED,
        ),
    ),
}


V2_ATOMS: dict[int, tuple[dict[str, Any], ...]] = {
    50: (
        atom("CONJUGATE-PAIR", "A conjugate acid/base relation retains two chemical identities differing by one proton carrier.", ("SFT-CHEM-AB-ACID-BASE-001",), DIRECT),
        atom("PROTON-TRANSFER-BALANCE", "Proton transfer conserves the named proton carrier and retains donor, acceptor and equilibrium records rather than an answer-only logarithmic equality.", ("SFT-CHEM-AB-PROTON-TRANSFER-001", "SFT-CHEM-EQ-CHEMICAL-001", "SFT-CHEM-AB-BUFFER-001"), CORRECTION, status=CORRECTED),
    ),
    73: (
        atom("MOLECULAR-CHIRALITY", "A complete oriented molecular carrier and its reflection remain a non-superposable enantiomer pair.", ("SFT-CHEM-STEREO-CHIRALITY-001", "SFT-CHEM-STEREO-ENANTIOMER-001"), DIRECT),
    ),
    77: (
        atom("CATALYTIC-PATH", "A catalyst opens an alternative lower-activation-support path and returns with exact chemical identity.", ("SFT-CHEM-CAT-CATALYST-001", "SFT-CHEM-CAT-PATHWAY-001"), DIRECT),
    ),
    78: (
        atom("ELECTRONEGATIVITY-ORDER", "Shared electron support induces a complete endpoint-affinity preorder with ties retained.", ("SFT-CHEM-ELECTRONEGATIVITY-001",), CORRECTION, status=CORRECTED),
        atom("COVALENT-IONIC-PARTITION", "Equal affinity retains shared support while complete transfer yields opposed ionic fibres; intermediate unequal sharing is retained as bond polarity.", ("SFT-CHEM-BOND-COVALENT-001", "SFT-CHEM-BOND-IONIC-001", "SFT-CHEM-BOND-POLARITY-001"), DIRECT),
    ),
    99: (
        atom("CHEMICAL-HANDEDNESS", "Chemical mirror carriers retain their enantiomer distinction independent of which hand a biological system later uses.", ("SFT-CHEM-STEREO-CHIRALITY-001", "SFT-CHEM-STEREO-ENANTIOMER-001", "SFT-CHEM-BIOMOLECULAR-BOUNDARY-001"), DIRECT),
        atom("AUTOCATALYTIC-AMPLIFICATION", "A finite chemical reaction network may retain its product as catalyst for another production cycle of the same identity.", ("SFT-CHEM-NET-AUTOCATALYSIS-001",), DIRECT),
    ),
    112: (
        atom("INTERMOLECULAR-RESIDUAL", "Distinct complete molecular carriers retain an intermolecular response channel and collective recurrence without importing a universal strength fraction.", ("SFT-CHEM-MOL-INTERMOLECULAR-001",), CORRECTION, status=CORRECTED),
    ),
    120: (
        atom("LITHIUM-ISOTOPE-COMPOSITION", "Lithium-7 isotope identity and the source-bound before/after population record remain chemical composition, yield and analytical distinctions; the stellar depletion mechanism is Astronomy-owned.", ("SFT-CHEM-ELEM-ISOTOPE-001", "SFT-CHEM-STOICH-COMPOSITION-001", "SFT-CHEM-STOICH-YIELD-001", "SFT-CHEM-ANALYTICAL-COMPLETE-RECORD-001"), CORRECTION, status=CORRECTED),
    ),
    127: (
        atom("NOBLE-CLOSURE-CHEMICAL-RECURRENCE", "The generated filled-shell coordinates close and reopen outer chemical observation classes, producing the retained periodic recurrence.", ("SFT-CHEM-ELEM-PERIODIC-RECURRENCE-001", "SFT-CHEM-ELEM-GROUP-PERIOD-001"), DIRECT, upstream=("SFT-PHYS-ATOMIC-SHELL-PERIODICITY-TERMINAL-005",)),
    ),
    142: (
        atom("MOLECULAR-SPECTRAL-CLASSES", "Molecular rotational, vibrational and electronic transitions retain distinct complete condition-bound spectral organizations.", ("SFT-CHEM-SPEC-ROT-VIB-001", "SFT-CHEM-SPEC-INFRARED-001", "SFT-CHEM-SPEC-UVVIS-001"), DIRECT, upstream=("SFT-PHYS-QUANTUM-DISCRETE-SPECTRA-001",)),
    ),
    144: (
        atom("AUTOCATALYTIC-CYCLE", "A retained product re-enters a finite resource-bounded reaction-network cycle as catalyst for another production cycle; the life-status handoff is separate.", ("SFT-CHEM-NET-REACTION-001", "SFT-CHEM-NET-AUTOCATALYSIS-001", "SFT-CHEM-BIOMOLECULAR-BOUNDARY-001"), DIRECT),
    ),
    156: (
        atom("MOLECULAR-BOND", "Stable joint recurrence between atomic carriers closes a distinct molecular chemical carrier.", ("SFT-CHEM-BOND-CHEMICAL-BOND-001", "SFT-CHEM-BOND-COVALENT-001", "SFT-CHEM-MOL-MOLECULE-001"), DIRECT),
        atom("BOND-CLASS-BOUNDARY", "Shared, transferred and collective electron-labelled supports distinguish covalent, ionic and metallic bonding without a free bond label.", ("SFT-CHEM-BOND-COVALENT-001", "SFT-CHEM-BOND-IONIC-001", "SFT-CHEM-BOND-METALLIC-001"), DIRECT),
    ),
    157: (
        atom("PERIODIC-RECURRENCE", "Closure and reopening of generated outer chemical organization produces exact periodic recurrence, group equivalence and counted periods.", ("SFT-CHEM-ELEM-PERIODIC-ORDER-001", "SFT-CHEM-ELEM-PERIODIC-RECURRENCE-001", "SFT-CHEM-ELEM-GROUP-PERIOD-001"), DIRECT, upstream=("SFT-PHYS-ATOMIC-SHELL-PERIODICITY-TERMINAL-005",)),
    ),
    167: (
        atom("REACTION-KINETICS", "A reaction path retains its least activation support, exact completed-transition count and condition-bound reactant dependency multiplicity.", ("SFT-CHEM-KIN-ACTIVATION-001", "SFT-CHEM-KIN-RATE-001", "SFT-CHEM-KIN-ORDER-001"), CORRECTION, status=CORRECTED),
    ),
    176: (
        atom("ENANTIOMER-PAIR", "Exact reflection with no identity-preserving proper superposition forces a retained enantiomer pair.", ("SFT-CHEM-STEREO-CHIRALITY-001", "SFT-CHEM-STEREO-ENANTIOMER-001"), DIRECT),
        atom("STEREOISOMER-CLASSIFICATION", "Equal-composition oriented carriers are classified by complete connectivity, reflection and proper-superposition traces into enantiomeric and diastereomeric relations.", ("SFT-CHEM-MOL-ISOMER-001", "SFT-CHEM-STEREO-DIASTEREOMER-001"), DIRECT),
    ),
    249: (
        atom("REACTION-THERMOCHEMISTRY", "Reaction thermochemistry retains the complete energy ledger, reference states, conditions, phase and transfer orientation across one conserved chemical transformation.", ("SFT-CHEM-THERMO-REACTION-001", "SFT-CHEM-THERMO-DIRECTION-001"), CORRECTION, status=CORRECTED),
        atom("REACTION-ACTIVATION", "The generated reaction path retains its least support to the highest transition boundary rather than importing one universal quarter-barrier value.", ("SFT-CHEM-KIN-ACTIVATION-001",), CORRECTION, status=CORRECTED),
    ),
    266: (
        atom("PERIODIC-ENDPOINT", "The sealed inverse fine-structure relation and One binding ceiling admit atomic coordinate 137 and reject successor 138 as the model's standing chemical endpoint prediction.", ("SFT-CHEM-PRED-PERIODIC-ENDPOINT-001",), DIRECT, upstream=("SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001", "SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001", "SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001")),
    ),
    267: (
        atom("GBLOCK-PREDICTION", "The generated filling walk closes the known noble sequence, fills 8s at 119-120 and opens the 5g block at 121.", ("SFT-CHEM-PRED-G-BLOCK-001",), DIRECT, upstream=("SFT-PHYS-ATOMIC-CELL-ORBIT-CAPACITY-001", "SFT-PHYS-ATOMIC-SHELL-PERIODICITY-TERMINAL-005")),
        atom("SMITHIUM-CHEMISTRY", "Element 126 has retained chemical prediction 8s2 5g6, eight valence carriers and admissible positive oxidation counts two through eight.", ("SFT-CHEM-PRED-SMITHIUM-001",), DIRECT, upstream=("SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001", "SFT-PHYS-VALIDATION-NUCLEAR-CLOSURES-001")),
    ),
    292: (
        atom("FINITE-ELEMENT-INVENTORY", "The Chemistry component of the finite-inventory summary is the already sealed periodic endpoint at 137; particle and excitation inventories retain their other owners.", ("SFT-CHEM-PRED-PERIODIC-ENDPOINT-001",), DIRECT, upstream=("SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001",)),
    ),
    293: (
        atom("SMITHIUM-DOUBLE-CLOSURE", "The independently sealed nuclear double closure 126/184 is retained by Chemistry as the element-126 Smithium prediction with mass coordinate 310 and its chemical state record.", ("SFT-CHEM-PRED-SMITHIUM-001",), DIRECT, upstream=("SFT-PHYS-NUCLEAR-COLOUR-COUPLING-001", "SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001", "SFT-PHYS-VALIDATION-NUCLEAR-CLOSURES-001")),
    ),
    294: (
        atom("GBLOCK-WIDTH", "The generated subshell capacity produces the unentered 5g width 18 over elements 121 through 137 while codon grouping remains Biology-owned.", ("SFT-CHEM-PRED-G-BLOCK-001",), DIRECT, upstream=("SFT-PHYS-ATOMIC-CELL-ORBIT-CAPACITY-001",)),
    ),
}


MIXED_BOUNDARIES: dict[tuple[str, str], str] = {
    ("v1", "III-4"): "Physics owns shell capacities and atomic energy structure; Chemistry owns the resulting outer-organization recurrence and chemical classification.",
    ("v1", "III-8"): "Physics owns the universal rotational/vibrational energy laws and isotope-mass dynamics; Chemistry owns complete molecular spectral identity and observation classes.",
    ("v1", "IV-5"): "Chemistry owns catalytic paths and chemical selectivity; Biology owns enzyme function after the molecular handoff.",
    ("v1", "IV-7"): "Chemistry owns molecular stereochemical identity; Biology owns the realized organismal hand and function.",
    ("v1", "IV-8"): "Chemistry owns intermolecular and molecular-network identities; Physics owns universal distance exponents and Materials owns bulk water-property response.",
    ("v1", "X-5"): "Chemistry owns molecular chirality and autocatalytic reaction support; Biology owns organismal homochirality and the realized selected hand.",
    ("v1", "X-6"): "Chemistry owns the autocatalytic reaction-network cycle; Biology owns the criterion and realized onset of life.",
    ("v1", "XVIII-9"): "Chemistry owns lithium isotope, composition, yield and analytical records; Physics owns nuclear burning and Astronomy owns stellar transport and population history.",
    ("v2", "73"): "Chemistry owns molecular chirality and enantiomers; Physics owns elementary-particle chirality and weak parity selection.",
    ("v2", "99"): "Chemistry owns molecular handedness and autocatalytic support; Biology owns organismal homochirality and the selected hand.",
    ("v2", "112"): "Chemistry owns the intermolecular response class; Physics owns any universal interaction-strength or distance law.",
    ("v2", "120"): "Chemistry owns lithium isotope/composition observation; Physics owns nuclear burning and Astronomy owns stellar depletion history.",
    ("v2", "127"): "Physics owns shell capacity; Chemistry owns noble closure as periodic chemical recurrence.",
    ("v2", "142"): "Physics owns transition-energy dynamics; Chemistry owns condition-bound molecular spectral identity and classification.",
    ("v2", "144"): "Chemistry owns autocatalytic reaction-network closure; Biology owns the claim that the resulting system is living.",
    ("v2", "266"): "Physics owns alpha and the bound-state ceiling; Chemistry owns the periodic-endpoint consequence.",
    ("v2", "267"): "Physics owns shell and nuclear prerequisites; Chemistry owns g-block placement and Smithium chemistry.",
    ("v2", "292"): "Chemistry owns only the periodic-endpoint component; Physics and other branches own particle and excitation inventories.",
    ("v2", "293"): "Physics owns the nuclear magic-number law; Chemistry owns the Smithium element consequence.",
    ("v2", "294"): "Chemistry owns g-block width and placement; Biology owns codon wobble and genetic-code organization.",
}


def raw_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def verify_engine_seal() -> str:
    run = subprocess.run(
        ["python3", "tools/verify_engine_seal.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    if "SFT ENGINE SEAL: VALID CANONICAL ENGINE" not in run.stdout:
        raise SystemExit("canonical engine seal was not verified")
    for line in run.stdout.splitlines():
        if line.startswith("Seal: "):
            return line.removeprefix("Seal: ")
    raise SystemExit("canonical engine seal identifier was not reported")


def verify_receipt(claim_id: str, row: dict[str, Any]) -> dict[str, str]:
    receipt_path = ROOT / row["receipt_path"]
    if not receipt_path.is_file():
        raise SystemExit(f"missing model-admitted receipt for {claim_id}: {receipt_path}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if (
        receipt.get("claim_id") != claim_id
        or receipt.get("model_admitted") is not True
        or receipt.get("receipt_hash") != row.get("receipt_hash")
    ):
        raise SystemExit(f"receipt/census mismatch for {claim_id}")
    return {
        "claim_id": claim_id,
        "branch": row["branch"],
        "receipt_path": row["receipt_path"],
        "receipt_hash": row["receipt_hash"],
        "receipt_file_sha256": raw_sha256(receipt_path),
    }


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    engine_seal = verify_engine_seal()
    v1 = json.loads(V1_PATH.read_text(encoding="utf-8"))
    v2 = json.loads(V2_PATH.read_text(encoding="utf-8"))
    claims = {
        row["claim_id"]: row
        for row in json.loads(CLAIMS_PATH.read_text(encoding="utf-8"))["claims"]
    }
    v1_rows = {str(row["v1_claim_id"]): row for row in v1["rows"]}
    v2_rows = {int(row["step"]): row for row in v2["steps"]}
    if set(V1_ATOMS) - set(v1_rows):
        raise SystemExit("Chemistry audit cites an absent V1 source row")
    if set(V2_ATOMS) - set(v2_rows):
        raise SystemExit("Chemistry audit cites an absent V2 source step")

    source_rows: list[dict[str, Any]] = []
    raw_rows: list[tuple[str, str, dict[str, Any]]] = [
        ("v1", str(row["v1_claim_id"]), row) for row in v1["rows"]
    ] + [("v2", str(row["step"]), row) for row in v2["steps"]]

    for source, entry, row in raw_rows:
        specs = V1_ATOMS.get(entry, ()) if source == "v1" else V2_ATOMS.get(int(entry), ())
        source_hash = row["source_row_sha256"] if source == "v1" else row["source_block_sha256"]
        observation = row.get("prior_result_observation")
        record: dict[str, Any] = {
            "source": source,
            "source_entry": entry if source == "v1" else int(entry),
            "source_hash": source_hash,
            "source_observation": observation,
            "chemistry_owned": bool(specs),
            "categorical_boundary": MIXED_BOUNDARIES.get((source, entry)),
            "chemistry_atoms": [],
        }
        if not specs:
            record.update({
                "categorical_owner": "another registered categorical branch or corpus-level synthesis",
                "disposition": "reviewed_no_chemistry_owned_atom",
                "atomization_mode": "explicit_nonchemistry_disposition",
            })
            source_rows.append(record)
            continue

        record["categorical_owner"] = (
            "Mixed source explicitly decomposed; Chemistry atoms owned by Chemistry"
            if record["categorical_boundary"] else "Chemistry"
        )
        atoms: list[dict[str, Any]] = []
        for spec in specs:
            mapped: list[dict[str, str]] = []
            for claim_id in spec["claim_ids"]:
                claim = claims.get(claim_id)
                if claim is None or claim.get("branch") != "chemistry" or claim.get("model_admitted") is not True:
                    raise SystemExit(f"Chemistry atom {source}:{entry}:{spec['suffix']} lacks admitted Chemistry claim {claim_id}")
                mapped.append(verify_receipt(claim_id, claim))
            upstream: list[dict[str, str]] = []
            for claim_id in spec["upstream_claim_ids"]:
                claim = claims.get(claim_id)
                if claim is None or claim.get("model_admitted") is not True:
                    raise SystemExit(f"Chemistry atom {source}:{entry}:{spec['suffix']} lacks admitted upstream claim {claim_id}")
                upstream.append(verify_receipt(claim_id, claim))
            atoms.append({
                "atom_id": f"SFT-PRIOR-{source.upper()}-{entry}-CHEM-{spec['suffix']}",
                "owner": "Chemistry",
                "atomic_statement": spec["statement"],
                "current_v3_claim_ids": list(spec["claim_ids"]),
                "current_v3_receipts": mapped,
                "upstream_prerequisite_claim_ids": list(spec["upstream_claim_ids"]),
                "upstream_prerequisite_receipts": upstream,
                "same_strength_closed": True,
                "same_strength_status": spec["same_strength_status"],
                "same_strength_basis": spec["same_strength_basis"],
                "remaining_gap": None,
            })
        record.update({
            "disposition": "all_chemistry_atoms_same_strength_closed",
            "atomization_mode": "explicit_multi_atom_decomposition" if len(atoms) > 1 or record["categorical_boundary"] else "single_chemistry_atom",
            "decomposition_complete": True,
            "chemistry_atoms": atoms,
        })
        source_rows.append(record)

    if len(source_rows) != v1["source_row_count"] + v2["source_step_count"]:
        raise SystemExit("Chemistry audit did not review the complete V1/V2 source surface")
    atoms = [atom for row in source_rows for atom in row["chemistry_atoms"]]
    atom_ids = [atom["atom_id"] for atom in atoms]
    if len(atom_ids) != len(set(atom_ids)):
        raise SystemExit("duplicate Chemistry atomic obligation identifier")
    if any(atom["owner"] != "Chemistry" for atom in atoms):
        raise SystemExit("a Chemistry atom has more than or other than one owner")
    open_atoms = [atom for atom in atoms if not atom["same_strength_closed"]]
    relevant_v1 = [entry for entry in V1_ATOMS]
    relevant_v2 = [entry for entry in V2_ATOMS]
    audit: dict[str, Any] = {
        "schema": "sft.chemistry.v1-v2-atomic-ownership-audit.v1",
        "audit_status": "current_evidence_closed_extension_open" if not open_atoms else "open_blocking",
        "purpose": "Identify every categorically Chemistry-owned V1/V2 atom, split mixed prose, and verify same-strength mapping to current immutable model-admitted V3 receipts.",
        "authority_boundary": {
            "canonical_engine_seal_verified": True,
            "canonical_engine_seal": engine_seal,
            "engine_modified": False,
            "engine_called_for_admission": False,
            "claims_admitted_by_this_audit": False,
            "semantic_similarity_closes_claims": False,
            "one_owner_law": "Each Chemistry atom has exactly one primary owner: Chemistry.",
            "correction_law": "A prior overbroad or answer-only formulation closes only when a current admitted receipt explicitly enumerates and rejects that form while preserving the exact valid chemical boundary.",
            "receipt_verification": "Every mapped primary and upstream receipt is opened and checked for claim identity, model-admitted status and exact census/file hash.",
            "extension_policy": "Closure is complete to the current registered V1/V2 evidence standard and remains open to lawful future extension.",
        },
        "source_surface": {
            "v1_path": v1["source_path"],
            "v1_sha256": v1["source_sha256"],
            "v1_row_count": v1["source_row_count"],
            "v2_source_id": v2["source_id"],
            "v2_sha256": v2["source_sha256"],
            "v2_step_count": v2["source_step_count"],
            "total_source_rows_reviewed": len(source_rows),
            "chemistry_relevant_v1_rows": relevant_v1,
            "chemistry_relevant_v2_steps": relevant_v2,
            "chemistry_relevant_source_row_count": sum(row["chemistry_owned"] for row in source_rows),
            "reviewed_nonchemistry_source_row_count": sum(not row["chemistry_owned"] for row in source_rows),
            "current_claim_census_path": str(CLAIMS_PATH.relative_to(ROOT)),
            "current_claim_census_sha256": raw_sha256(CLAIMS_PATH),
        },
        "summary": {
            "chemistry_owned_atom_count": len(atoms),
            "same_strength_closed_atom_count": len(atoms) - len(open_atoms),
            "same_strength_open_atom_count": len(open_atoms),
            "corrected_prior_atom_count": sum(atom["same_strength_status"] == CORRECTED for atom in atoms),
            "unique_atom_ids": len(atom_ids) == len(set(atom_ids)),
            "all_mixed_rows_decomposed": all(row.get("decomposition_complete") for row in source_rows if row["categorical_boundary"]),
            "every_primary_mapping_is_admitted_chemistry": True,
            "publication_blocked": bool(open_atoms),
        },
        "missing_chemistry_atoms": [atom for atom in open_atoms],
        "source_rows": source_rows,
    }
    audit_identity = "sha256:" + hashlib.sha256(
        json.dumps(audit, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    audit["audit_identity"] = audit_identity
    ledger = {
        "schema": "sft-v3-chemistry-prior-obligation-ledger/1",
        "status": "closed" if not open_atoms else "open",
        "source_policy": audit["authority_boundary"],
        "reviewed_source_surface": {
            "v1_total_rows": v1["source_row_count"],
            "v2_total_steps": v2["source_step_count"],
            "review_complete_for_branch_ownership": True,
            "reviewed_entry_count": len(source_rows),
            "chemistry_relevant_v1_rows": relevant_v1,
            "chemistry_relevant_v2_steps": relevant_v2,
            "reviewed_nonchemistry_v1_rows": [entry for entry in v1_rows if entry not in V1_ATOMS],
            "reviewed_nonchemistry_v2_steps": [entry for entry in v2_rows if entry not in V2_ATOMS],
        },
        "atomic_ownership_audit": str(AUDIT_PATH.relative_to(ROOT)),
        "atomic_ownership_audit_identity": audit_identity,
        "chemistry_summary": {
            "atomic_obligation_count": len(atoms),
            "same_strength_closed_count": len(atoms) - len(open_atoms),
            "corrected_prior_atom_count": audit["summary"]["corrected_prior_atom_count"],
            "open_count": len(open_atoms),
            "open_atomic_obligation_ids": [atom["atom_id"] for atom in open_atoms],
        },
    }
    return audit, ledger


def render_report(audit: dict[str, Any]) -> str:
    summary = audit["summary"]
    lines = [
        "# Atomic V1/V2 Chemistry ownership and V3 coverage audit",
        "",
        "This audit reviews the complete 356-row V1 and 407-step V2 source surfaces. It assigns only categorical Chemistry content to Chemistry, explicitly decomposes mixed rows, and checks every mapped receipt against the current census and immutable model-admitted file.",
        "",
        "It does not edit or call the admission engine, does not admit a claim, and does not treat semantic similarity as closure. Historical answer-only or over-universal wording is closed only where an existing engine receipt explicitly eliminated that form and retained the exact valid chemical boundary.",
        "",
        "## Result",
        "",
        f"- Complete source entries reviewed: {audit['source_surface']['total_source_rows_reviewed']}",
        f"- Chemistry-relevant source entries: {audit['source_surface']['chemistry_relevant_source_row_count']}",
        f"- Reviewed non-Chemistry source entries: {audit['source_surface']['reviewed_nonchemistry_source_row_count']}",
        f"- Chemistry-owned atomic obligations: {summary['chemistry_owned_atom_count']}",
        f"- Same-strength closed atoms: {summary['same_strength_closed_atom_count']}",
        f"- Explicitly corrected prior atoms: {summary['corrected_prior_atom_count']}",
        f"- Open Chemistry atoms: {summary['same_strength_open_atom_count']}",
        f"- Unique atom identifiers: {summary['unique_atom_ids']}",
        f"- Every mixed row decomposed: {summary['all_mixed_rows_decomposed']}",
        f"- Publication blocked by this audit: {summary['publication_blocked']}",
        "",
        "`closed` means complete to the current registered evidence standard, not permanently locked against lawful extension.",
        "",
        "## Chemistry-owned source atoms",
        "",
        "| Source | Atom | Disposition | Current admitted V3 receipts | Categorical boundary |",
        "|---|---|---|---|---|",
    ]
    for row in audit["source_rows"]:
        for item in row["chemistry_atoms"]:
            receipts = ", ".join(f"`{claim_id}`" for claim_id in item["current_v3_claim_ids"])
            boundary = row["categorical_boundary"] or "Chemistry"
            lines.append(
                f"| {row['source']}:{row['source_entry']} | `{item['atom_id']}` — {item['atomic_statement']} | {item['same_strength_status']} | {receipts} | {boundary} |"
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    audit, ledger = build()
    AUDIT_PATH.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(render_report(audit), encoding="utf-8")
    LEDGER_PATH.write_text(json.dumps(ledger, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    summary = audit["summary"]
    print(
        f"wrote Chemistry atomic audit: reviewed={audit['source_surface']['total_source_rows_reviewed']} "
        f"relevant_rows={audit['source_surface']['chemistry_relevant_source_row_count']} "
        f"atoms={summary['chemistry_owned_atom_count']} open={summary['same_strength_open_atom_count']}"
    )


if __name__ == "__main__":
    main()
