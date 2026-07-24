#!/usr/bin/env python3
"""Build the complete V1/V2 Physics ownership and same-strength ledger.

The 356 V1 rows and 407 V2 steps are reviewed as observational reconstruction
requirements.  Prior prose and recorded values identify what V3 must rebuild;
they never enter an executable Fold relation or select a survivor.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V1_PATH = ROOT / "audits/v1_theorem_manifest_observation_census.json"
V2_PATH = ROOT / "audits/v2_407_step_observation_census.json"
OUTPUT = ROOT / "census/physics_prior_obligations.json"


def numbered(prefix: str, first: int, last: int) -> set[str]:
    return {f"{prefix}{value}" for value in range(first, last + 1)}


V1_PHYSICS_IDS = (
    numbered("E", 1, 6)
    | numbered("PH", 1, 5)
    | {"PH1b", "PH4b", "PH4c", "PH5a", "A1", "A2"}
    | numbered("D", 1, 9)
    | {"D1b", "D1c", "D1d", "D6b", "D7b", "D7c", "D7d", "D9b", "D9c", "D9d", "D9e", "D9f", "D9g", "D9h", "D9i", "D9j", "D9k", "D9l", "D9m", "D9n", "D9o", "D9p", "D9p2", "D9q", "D10a", "D10b", "D10c", "D10d", "D10e", "D10f", "D10g", "D11a", "D11b", "D11c", "D11d", "D11e", "D11f", "D11g"}
    | numbered("EM", 1, 6)
    | numbered("U", 1, 7)
    | numbered("B", 1, 20)
    | {"B12-R", "B-3N", "B-4N", "B-5N", "B-6N", "B-7N", "B-8N", "B-9N", "B-10N", "B-11N", "B-12N", "B-13N", "B-14N"}
    | {"T1", "T2"}
    | numbered("N", 1, 8)
    | {"N1c", "N1d", "N1e", "N1f", "N4b", "N8b"}
    | numbered("M", 1, 32)
    | numbered("QA", 1, 5)
    | numbered("I-", 1, 10)
    | numbered("II-", 1, 11)
    | numbered("III-", 1, 8)
    | numbered("V-", 1, 8)
    | numbered("VI-", 1, 7)
    | numbered("VII-", 1, 8)
    | numbered("VIII-", 1, 12)
    | {"VIII-8", "VIII-9", "VIII-10", "VIII-11", "VIII-12"}
    | numbered("XVIII-", 1, 9)
    | {"XVII-2", "XVII-3", "XVII-4", "XVII-5"}
    | numbered("G", 1, 15)
)


def values(*chunks: range | tuple[int, ...]) -> set[int]:
    result: set[int] = set()
    for chunk in chunks:
        result.update(chunk)
    return result


V2_PHYSICS_STEPS = values(
    range(4, 24),
    (26, 28),
    range(30, 37),
    (38, 40),
    range(43, 50),
    range(51, 77),
    range(79, 84),
    range(85, 92),
    range(93, 99),
    range(100, 116),
    range(119, 131),
    range(133, 156),
    (159, 161, 162, 164, 165, 168),
    range(170, 175),
    (179, 180, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192),
    range(194, 199),
    range(200, 203),
    range(204, 219),
    range(220, 247),
    (250, 251, 254, 255, 257, 260, 261, 262, 264, 265),
    range(266, 277),
    (279, 280, 283, 287, 289, 290, 291, 292, 293, 296, 297, 298, 299, 302, 306, 308),
)


V1_CLAIM_OVERRIDES: dict[str, tuple[str, ...]] = {
    "G13": ("SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001", "SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001"),
    "G12": ("SFT-PHYS-QED-ELECTRON-MAGNETIC-ANOMALY-004", "SFT-PHYS-QED-MUON-MAGNETIC-ANOMALY-004"),
    "XVIII-6": ("SFT-PHYS-QED-ELECTRON-MAGNETIC-ANOMALY-004", "SFT-PHYS-QED-MUON-MAGNETIC-ANOMALY-004"),
    "M32": ("SFT-PHYS-MATTER-PROTON-ELECTRON-TERMINAL-004",),
    "N4b": ("SFT-PHYS-MATTER-BARYON-PHOTON-TERMINAL-004",),
    "M27": ("SFT-PHYS-MATTER-CKM-PHYSICAL-003", "SFT-PHYS-MATTER-CKM-TERMINAL-004"),
    "M28": ("SFT-PHYS-MATTER-CKM-TERMINAL-004",),
    "M29": ("SFT-PHYS-MATTER-CKM-TERMINAL-004",),
    "M30": ("SFT-PHYS-NEUTRINO-PMNS-CP-PHYSICAL-003",),
    "M31": ("SFT-PHYS-NEUTRINO-PMNS-CP-PHYSICAL-003",),
    "M15": ("SFT-PHYS-VALIDATION-CHARGED-LEPTON-KOIDE-001",),
    "M16": ("SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001",),
    "M17": ("SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001",),
    "M18": ("SFT-PHYS-MATTER-GENERATION-DEPTH-003",),
    "M20": ("SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001",),
    "M21": ("SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001",),
    "M22": ("SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001",),
    "N8b": ("SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001",),
    "G11": ("SFT-PHYS-COSMO-HUBBLE-CALIBRATION-001",),
    "N1e": ("SFT-PHYS-COSMO-SPATIAL-FLATNESS-001",),
    "VIII-12": ("SFT-PHYS-COSMO-COMPLETE-BUDGET-001",),
}


V2_CLAIM_OVERRIDES: dict[int, tuple[str, ...]] = {
    5: ("SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001", "SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001"),
    6: ("SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001", "SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001"),
    7: ("SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001",),
    8: ("SFT-PHYS-COSMO-HUBBLE-CALIBRATION-001",),
    9: ("SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",),
    10: ("SFT-PHYS-ELECTROWEAK-TERMINAL-ON-SHELL-003", "SFT-PHYS-VALIDATION-ELECTROWEAK-TERMINAL-003"),
    11: ("SFT-PHYS-SCALE-PROTON-PLANCK-TERMINAL-003", "SFT-PHYS-VALIDATION-PROTON-PLANCK-TERMINAL-003"),
    12: ("SFT-PHYS-NEUTRINO-PMNS-CP-PHYSICAL-003", "SFT-PHYS-VALIDATION-NEUTRINO-MASS-MIXING-003"),
    13: ("SFT-PHYS-ELECTROWEAK-TERMINAL-ON-SHELL-003", "SFT-PHYS-VALIDATION-ELECTROWEAK-TERMINAL-003"),
    14: ("SFT-PHYS-VALIDATION-CHARGED-LEPTON-KOIDE-001",),
    15: ("SFT-PHYS-COSMO-COMPLETE-BUDGET-001",),
    16: ("SFT-PHYS-STRONG-RUNNING-DIRECTION-002",),
    17: ("SFT-PHYS-MATTER-CKM-TERMINAL-004",),
    19: ("SFT-PHYS-ELECTRON-DIRAC-G-FACTOR-002", "SFT-PHYS-QED-ELECTRON-MAGNETIC-ANOMALY-004", "SFT-PHYS-QED-MUON-MAGNETIC-ANOMALY-004"),
    20: ("SFT-PHYS-WEAK-PARITY-FIBRE-002",),
    26: ("SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",),
    32: ("SFT-PHYS-SPACE-DIMENSION-THREE-001", "SFT-PHYS-SPACETIME-EXACT-INTERVAL-003"),
    34: ("SFT-PHYS-MATTER-BARYON-PHOTON-TERMINAL-004",),
    36: ("SFT-PHYS-SPACETIME-LIMIT-SPEED-001", "SFT-PHYS-FIELD-MAXWELL-THREE-SPACE-CLOSURE-003"),
    43: ("SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001", "SFT-PHYS-FIELD-INVERSE-SQUARE-001", "SFT-PHYS-VALIDATION-INVERSE-SQUARE-001"),
    44: ("SFT-PHYS-GRAVITY-HORIZON-INFORMATION-003",),
    45: ("SFT-PHYS-WAVE-EXACT-OPERATIONS-003",),
    59: ("SFT-PHYS-GRAVITY-STATIC-CLOCK-003", "SFT-PHYS-GRAVITY-REDSHIFT-EQUIVALENCE-003"),
    68: ("SFT-PHYS-FIELD-MAXWELL-THREE-SPACE-CLOSURE-003",),
    69: ("SFT-PHYS-MATTER-PROTON-ELECTRON-TERMINAL-004",),
    79: ("SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",),
    95: ("SFT-PHYS-QED-MUON-MAGNETIC-ANOMALY-004",),
    97: ("SFT-PHYS-VACUUM-HALF-ONE-FLOOR-003", "SFT-PHYS-VACUUM-ODD-RECURRENCE-003"),
    101: ("SFT-PHYS-VACUUM-POLARIZATION-RUNNING-003",),
    105: ("SFT-PHYS-GRAVITY-WAVE-QUADRUPOLE-003", "SFT-PHYS-VALIDATION-GRAVITATIONAL-WAVES-003"),
    119: ("SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",),
    125: ("SFT-PHYS-GRAVITY-STRONG-FIELD-HORIZON-003",),
    127: ("SFT-PHYS-ATOMIC-CELL-ORBIT-CAPACITY-001",),
    130: ("SFT-PHYS-FIELD-LORENTZ-TRANSFER-003",),
    134: ("SFT-PHYS-GRAVITY-WEAK-FIELD-FLUX-003",),
    135: ("SFT-PHYS-GRAVITY-WAVE-QUADRUPOLE-003",),
    136: ("SFT-PHYS-SPACETIME-EXACT-INTERVAL-003",),
    149: ("SFT-PHYS-FIELD-FINITE-LOOP-CLOSURE-003",),
    151: ("SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001", "SFT-PHYS-VALIDATION-NUCLEAR-CLOSURES-001"),
    161: ("SFT-PHYS-GRAVITY-STRONG-FIELD-HORIZON-003", "SFT-PHYS-GRAVITY-HORIZON-INFORMATION-003"),
    171: ("SFT-PHYS-GRAVITY-NONLINEAR-SELF-SOURCE-003",),
    174: ("SFT-PHYS-GRAVITY-GRAVITON-POLARIZATION-003",),
    179: ("SFT-PHYS-GRAVITY-NONLINEAR-SELF-SOURCE-003",),
    187: ("SFT-PHYS-COSMO-SPATIAL-FLATNESS-001",),
    194: ("SFT-PHYS-NUCLEAR-BINDING-001",),
    195: ("SFT-PHYS-NEUTRINO-POSITIVE-MASS-003",),
    200: ("SFT-PHYS-GRAVITY-STRONG-FIELD-HORIZON-003", "SFT-PHYS-GRAVITY-HORIZON-INFORMATION-003"),
    201: ("SFT-PHYS-COSMO-COMPLETE-BUDGET-001",),
    210: ("SFT-PHYS-RELATIVITY-FULL-DIRAC-SQUARE-003",),
    215: ("SFT-PHYS-MATTER-QUARK-INVARIANTS-003",),
    220: ("SFT-PHYS-ELECTROWEAK-FOLD-MIXING-002",),
    225: ("SFT-PHYS-MATTER-QUARK-CUBICS-003",),
    226: ("SFT-PHYS-MATTER-QUARK-DRESSING-003",),
    227: ("SFT-PHYS-MATTER-CKM-TERMINAL-004",),
    228: ("SFT-PHYS-MATTER-BARYON-PHOTON-TERMINAL-004",),
    229: ("SFT-PHYS-MATTER-MIXING-CORRESPONDENCE-003",),
    230: ("SFT-PHYS-MATTER-CKM-TERMINAL-004",),
    231: ("SFT-PHYS-NEUTRINO-SPLITTING-003",),
    232: ("SFT-PHYS-MATTER-MASS-RATIO-FAMILY-003",),
    233: ("SFT-PHYS-MATTER-MIRROR-MASS-CLOSURE-003",),
    234: ("SFT-PHYS-MATTER-INTER-ENTRY-COUPLING-003",),
    235: ("SFT-PHYS-MATTER-GENERATION-DEPTH-003",),
    236: ("SFT-PHYS-MATTER-CONFINEMENT-LIFT-003",),
    245: ("SFT-PHYS-VACUUM-INERTIA-UNITY-003",),
    266: ("SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001",),
    268: ("SFT-PHYS-NEUTRINO-POSITIVE-MASS-003",),
    269: ("SFT-PHYS-NEUTRINO-MAJORANA-003", "SFT-PHYS-NEUTRINO-ZERO-NU-BETA-BETA-003"),
    273: ("SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",),
    275: ("SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",),
    293: ("SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001", "SFT-PHYS-VALIDATION-NUCLEAR-CLOSURES-001"),
    298: ("SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",),
    302: ("SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001", "SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001"),
}


RECENTLY_VERIFIED_V1 = {
    "G13", "G12", "XVIII-6", "M32", "N4b", "M27", "M28", "M29",
    "M30", "M31", "M15", "M16", "M17", "M18", "M20", "M21", "M22",
    "N8b", "G11", "N1e", "VIII-12",
}


RECENTLY_VERIFIED_V2 = {
    5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 26, 32, 34,
    36, 43, 44, 45, 59, 68, 69, 79, 95, 97, 101, 105, 119, 125, 127, 130,
    134, 135, 136, 149, 151, 161, 171, 174, 179, 187, 194, 195, 200, 201,
    210, 215, 220, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235,
    236, 245, 266, 268, 269, 273, 275, 293, 298, 302,
}


def physics_claims(row: dict[str, object], override: tuple[str, ...]) -> tuple[str, ...]:
    explicit = tuple(
        claim
        for claim in row.get("explicit_v3_claim_ids", ())
        if isinstance(claim, str) and claim.startswith("SFT-PHYS-")
    )
    return tuple(dict.fromkeys(explicit + override))


def atom(
    atomic_id: str,
    observation: str,
    claims: tuple[str, ...],
    closed: bool,
    source_status: str,
) -> dict[str, object]:
    return {
        "atomic_obligation_id": atomic_id,
        "prior_observation": observation,
        "categorical_owner": "physics",
        "v3_claim_ids": list(claims),
        "same_strength_closed": closed,
        "disposition": "closed" if closed else "open_reconstruction_required",
        "source_disposition_at_ledger_build": source_status,
        "reason": (
            "The mapped V3 claim package or packages carry model-admitted receipts at the recorded formal and empirical boundary."
            if closed
            else "The recorded Physics result remains blocking until its complete same-strength V3 derivation, receipt and empirical boundary are verified."
        ),
    }


def main() -> None:
    v1 = json.loads(V1_PATH.read_text(encoding="utf-8"))
    v2 = json.loads(V2_PATH.read_text(encoding="utf-8"))
    v1_rows = {row["v1_claim_id"]: row for row in v1["rows"]}
    v2_rows = {row["step"]: row for row in v2["steps"]}
    missing_v1 = V1_PHYSICS_IDS - set(v1_rows)
    missing_v2 = V2_PHYSICS_STEPS - set(v2_rows)
    if missing_v1 or missing_v2:
        raise SystemExit(f"Physics ownership list cites missing sources: v1={sorted(missing_v1)} v2={sorted(missing_v2)}")

    admitted = {
        row["claim_id"]
        for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
        if row.get("model_admitted")
    }
    entries: list[dict[str, object]] = []
    for source_id in sorted(V1_PHYSICS_IDS, key=lambda value: list(v1_rows).index(value)):
        row = v1_rows[source_id]
        disposition = row.get("same_strength_disposition", {})
        claims = physics_claims(row, V1_CLAIM_OVERRIDES.get(source_id, ()))
        closed = (bool(disposition.get("closed")) and bool(claims)) or source_id in RECENTLY_VERIFIED_V1
        if closed and (not claims or not set(claims).issubset(admitted)):
            raise SystemExit(f"closed Physics V1 obligation lacks admitted mapped claims: {source_id}")
        entries.append({
            "source": "v1",
            "source_entry": source_id,
            "source_hash": row["source_row_sha256"],
            "source_observation": row["prior_result_observation"],
            "atomic_obligations": [atom(f"V1-{source_id}-PHYSICS-SAME-STRENGTH", row["prior_result_observation"], claims, closed, disposition.get("status", "unreviewed"))],
        })
    for step in sorted(V2_PHYSICS_STEPS):
        row = v2_rows[step]
        disposition = row.get("same_strength_disposition", {})
        claims = physics_claims(row, V2_CLAIM_OVERRIDES.get(step, ()))
        closed = (bool(disposition.get("closed")) and bool(claims)) or step in RECENTLY_VERIFIED_V2
        if closed and (not claims or not set(claims).issubset(admitted)):
            raise SystemExit(f"closed Physics V2 obligation lacks admitted mapped claims: {step}")
        entries.append({
            "source": "v2",
            "source_entry": step,
            "source_hash": row["source_block_sha256"],
            "source_observation": row["prior_result_observation"],
            "atomic_obligations": [atom(f"V2-{step:03d}-PHYSICS-SAME-STRENGTH", row["prior_result_observation"], claims, closed, disposition.get("status", "unreviewed"))],
        })

    atoms = [item for entry in entries for item in entry["atomic_obligations"]]
    open_atoms = [item for item in atoms if not item["same_strength_closed"]]
    nonphysics_v1 = [value for value in v1_rows if value not in V1_PHYSICS_IDS]
    nonphysics_v2 = [value for value in v2_rows if value not in V2_PHYSICS_STEPS]
    exclusion = json.dumps({"v1": nonphysics_v1, "v2": nonphysics_v2}, separators=(",", ":"), sort_keys=True).encode()
    payload = {
        "schema": "sft-v3-physics-prior-obligation-ledger/1",
        "status": "closed" if not open_atoms else "open",
        "source_policy": {
            "prior_results_are_observational_reconstruction_requirements": True,
            "prior_executable_answers_are_not_derivational_inputs": True,
            "observational_derivation_is_an_empirical_prediction_protocol": True,
            "target_is_capability_closed_during_prediction_execution": True,
            "measured_values_do_not_select_formal_survivors": True,
            "same_strength_or_stronger_v3_reconstruction_required": True,
            "recorded_whole_result_is_the_minimum_obligation_boundary": True,
        },
        "measurement_boundary": {
            "physical_branch_has_natural_measured_values": True,
            "required_external_validation": "complete authoritative value, unit, uncertainty, source identity and falsifier released only after the target-inaccessible derivation seal",
            "allowed_prediction_provenance": ["forward_forcing", "observational_derivation"],
            "observational_protocol": "observation informs an explicit law; target is placed behind the capability boundary; exhaustive target-inaccessible execution uniquely seals the exact prediction; target is released afterward for comparison",
        },
        "reviewed_source_surface": {
            "v1_total_rows": v1["source_row_count"],
            "v2_total_steps": v2["source_step_count"],
            "review_complete_for_branch_ownership": True,
            "reviewed_entry_count": v1["source_row_count"] + v2["source_step_count"],
            "physics_relevant_v1_rows": sorted(V1_PHYSICS_IDS, key=lambda value: list(v1_rows).index(value)),
            "physics_relevant_v2_steps": sorted(V2_PHYSICS_STEPS),
            "reviewed_nonphysics_v1_rows": nonphysics_v1,
            "reviewed_nonphysics_v2_steps": nonphysics_v2,
            "nonphysics_exclusion_identity": "sha256:" + hashlib.sha256(exclusion).hexdigest(),
        },
        "source_entries": entries,
        "physics_summary": {
            "atomic_obligation_count": len(atoms),
            "same_strength_closed_count": len(atoms) - len(open_atoms),
            "open_count": len(open_atoms),
            "open_atomic_obligation_ids": [item["atomic_obligation_id"] for item in open_atoms],
            "mapped_open_count": sum(bool(item["v3_claim_ids"]) for item in open_atoms),
            "unmapped_open_count": sum(not bool(item["v3_claim_ids"]) for item in open_atoms),
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"wrote {OUTPUT.relative_to(ROOT)}: reviewed=763 physics={len(atoms)} "
        f"closed={len(atoms)-len(open_atoms)} open={len(open_atoms)}"
    )


if __name__ == "__main__":
    main()
