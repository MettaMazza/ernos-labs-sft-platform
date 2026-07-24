"""Question-level reconciliation of the V2 Chemistry surface.

This module is an inventory guard, not a proof import.  It records which V2
questions must receive new V3 derivations and where their evidence belongs.
No V2 value, implementation, certificate or answer is exposed to a V3
derivation program through this file.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.chemistry.obligations import OBLIGATIONS


@dataclass(frozen=True)
class V2ChemistryQuestion:
    step: int
    question: str
    required_v3_claim_ids: tuple[str, ...]
    prerequisite_claim_ids: tuple[str, ...] = ()
    prerequisite_gap: str = ""


V2_CHEMISTRY_QUESTIONS = (
    V2ChemistryQuestion(50, "acid/base conjugacy and neutral balance", ("SFT-CHEM-AB-ACID-BASE-001",)),
    V2ChemistryQuestion(
        77,
        "catalytic path lowering with catalyst retention",
        ("SFT-CHEM-CAT-CATALYST-001", "SFT-CHEM-CAT-PATHWAY-001"),
    ),
    V2ChemistryQuestion(
        78,
        "electronegativity and the covalent-to-ionic boundary",
        ("SFT-CHEM-ELECTRONEGATIVITY-001", "SFT-CHEM-BOND-POLARITY-001"),
    ),
    V2ChemistryQuestion(
        112,
        "intermolecular interaction relative to primary bonding",
        ("SFT-CHEM-MOL-INTERMOLECULAR-001",),
    ),
    V2ChemistryQuestion(
        142,
        "molecular rotational and vibrational spectral organization",
        ("SFT-CHEM-SPEC-INFRARED-001", "SFT-CHEM-SPEC-ROT-VIB-001"),
    ),
    V2ChemistryQuestion(
        144,
        "autocatalytic closure at the chemistry-to-life boundary",
        ("SFT-CHEM-NET-AUTOCATALYSIS-001", "SFT-CHEM-BIOMOLECULAR-BOUNDARY-001"),
    ),
    V2ChemistryQuestion(
        156,
        "molecular bond completion and reversible bond opening",
        ("SFT-CHEM-BOND-CHEMICAL-BOND-001", "SFT-CHEM-BOND-COVALENT-001"),
    ),
    V2ChemistryQuestion(
        157,
        "periodic recurrence under shell closure and reopening",
        ("SFT-CHEM-ELEM-PERIODIC-RECURRENCE-001", "SFT-CHEM-ELEM-GROUP-PERIOD-001"),
    ),
    V2ChemistryQuestion(
        167,
        "activation boundary and counted reaction transition rate",
        ("SFT-CHEM-KIN-ACTIVATION-001", "SFT-CHEM-KIN-RATE-001"),
    ),
    V2ChemistryQuestion(
        176,
        "stereochemical orientation and enantiomer distinction",
        ("SFT-CHEM-STEREO-CHIRALITY-001", "SFT-CHEM-STEREO-ENANTIOMER-001"),
    ),
    V2ChemistryQuestion(
        249,
        "reaction activation and thermochemical direction/accounting",
        ("SFT-CHEM-THERMO-REACTION-001", "SFT-CHEM-THERMO-DIRECTION-001"),
    ),
    V2ChemistryQuestion(
        266,
        "periodic endpoint as a pre-observation prediction",
        ("SFT-CHEM-PRED-PERIODIC-ENDPOINT-001",),
        prerequisite_claim_ids=(
            "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
            "SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001",
            "SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001",
        ),
    ),
    V2ChemistryQuestion(
        267,
        "g-block filling and element-126 chemistry as pre-observation predictions",
        ("SFT-CHEM-PRED-G-BLOCK-001", "SFT-CHEM-PRED-SMITHIUM-001"),
        prerequisite_claim_ids=(
            "SFT-PHYS-ATOMIC-CELL-ORBIT-CAPACITY-001",
            "SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001",
        ),
    ),
    V2ChemistryQuestion(
        293,
        "element-126 nuclear closure used by the Smithium prediction",
        ("SFT-CHEM-PRED-SMITHIUM-001",),
        prerequisite_claim_ids=(
            "SFT-PHYS-NUCLEAR-COLOUR-COUPLING-001",
            "SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001",
            "SFT-PHYS-VALIDATION-NUCLEAR-CLOSURES-001",
        ),
    ),
    V2ChemistryQuestion(
        294,
        "subshell-width sequence and generated g-block width",
        ("SFT-CHEM-PRED-G-BLOCK-001",),
        prerequisite_claim_ids=("SFT-PHYS-ATOMIC-CELL-ORBIT-CAPACITY-001",),
    ),
)


def validate_v2_chemistry_reconciliation() -> None:
    obligation_ids = {row.claim_id for row in OBLIGATIONS}
    steps = tuple(row.step for row in V2_CHEMISTRY_QUESTIONS)
    if len(steps) != len(set(steps)):
        raise ValueError("V2 Chemistry reconciliation contains duplicate steps")
    missing = sorted(
        claim_id
        for row in V2_CHEMISTRY_QUESTIONS
        for claim_id in row.required_v3_claim_ids
        if claim_id not in obligation_ids
    )
    if missing:
        raise ValueError("V2 Chemistry questions lack V3 obligations: " + ", ".join(missing))
    unresolved = tuple(row for row in V2_CHEMISTRY_QUESTIONS if row.prerequisite_gap)
    if unresolved:
        raise ValueError(
            "V2 Chemistry reconciliation retains unresolved prerequisite gaps: "
            + ", ".join(str(row.step) for row in unresolved)
        )
    required_prerequisites = {
        "SFT-PHYS-ATOMIC-CELL-ORBIT-CAPACITY-001",
        "SFT-PHYS-NUCLEAR-COLOUR-COUPLING-001",
        "SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001",
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001",
    }
    recorded = {
        claim_id for row in V2_CHEMISTRY_QUESTIONS for claim_id in row.prerequisite_claim_ids
    }
    if not required_prerequisites <= recorded:
        raise ValueError("V2 Chemistry reconciliation omits a closed cross-branch prerequisite")


validate_v2_chemistry_reconciliation()

__all__ = (
    "V2ChemistryQuestion",
    "V2_CHEMISTRY_QUESTIONS",
    "validate_v2_chemistry_reconciliation",
)
