#!/usr/bin/env python3
"""Freeze the complete pre-VALID Chemistry empirical evidence vector.

This is a mechanical custody build.  It does not choose a scientific survivor,
alter an existing claim, or call the admission engine.  Every already admitted
Chemistry empirical record is retained, hashed and assigned to every applicable
VALID vector.  Original target-custody certificates remain the authority for
whether their targets opened after their prediction seals.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "experiments/external_sources/chemistry/valid_001_012_complete_empirical_vector_v1.json"
REPAIR_AUDIT = ROOT / "audits/CHEMISTRY_EMPIRICAL_UNRESOLVED_REPAIR_BATCH_2026-07-28.json"
EXPECTED_BASE_COUNT = 254


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def obligation_from_certificate(claim_id: str, certificate: dict, frozen_rows: dict[str, dict]) -> str:
    explicit = certificate.get("chemistry_obligation")
    if explicit:
        return str(explicit)
    row = frozen_rows.get(claim_id)
    if row is None:
        raise ValueError(f"no frozen Chemistry obligation owns {claim_id}")
    return str(row["obligation_id"])


def obligation_family(obligation_id: str) -> tuple[str, int]:
    pieces = obligation_id.split("-")
    if len(pieces) < 5:
        raise ValueError(f"invalid Chemistry obligation identity: {obligation_id}")
    family = pieces[3]
    try:
        number = int(pieces[4])
    except ValueError:
        number = 1
    return family, number


def vector_memberships(claim_id: str, obligation_id: str, source_count: int) -> tuple[str, ...]:
    family, number = obligation_family(obligation_id)
    memberships: set[str] = {"012"}

    if (
        (family == "PROP" and number in {1, 3, 4})
        or (family == "INORG" and number in {2, 3, 4, 5, 15, 16})
        or (family == "ANAL" and number in {16, 17, 21})
        or any(token in claim_id for token in ("MOL-GEOMETRY", "BOND-LENGTH", "X-RAY", "DIFFRACTION"))
    ):
        memberships.add("001")

    if (
        (family == "PROP" and number in {2, 13, 14})
        or (family == "THERMO" and number in {3, 4, 6, 7, 8, 15})
        or any(token in claim_id for token in ("THERMO", "ENTHALP", "ENERGY", "HEAT-WORK"))
    ):
        memberships.add("002")

    if (
        (family == "THERMO" and number in set(range(7, 16)))
        or (family == "ECHEM" and number in {2, 3, 4})
        or (family == "NUCHEM" and number in {5, 7})
        or any(token in claim_id for token in ("-EQ-", "EQUILIBRIUM", "SOLUTION-EQUILIBRIUM", "PHASE-RULE"))
    ):
        memberships.add("003")

    if (
        family == "KIN"
        or (family == "ECHEM" and number == 9)
        or (family == "NUCHEM" and number == 8)
        or any(token in claim_id for token in ("-KIN-", "RATE", "MECHANISM", "INTERMEDIATE", "CATALYT"))
    ):
        memberships.add("004")

    if (
        (family == "ANAL" and number in set(range(6, 18)))
        or (family == "PROP" and number in {9, 10, 12})
        or (family == "ELEC" and number in {9, 10, 13, 14})
        or any(token in claim_id for token in ("SPEC-", "SPECTR", "NMR", "RAMAN", "FLUORESC", "PHOSPHORESC"))
    ):
        memberships.add("005")

    if family == "ECHEM" or any(token in claim_id for token in ("ELECTROCHEM", "REDOX", "ELECTRODE")):
        memberships.add("006")

    if (
        family == "INORG"
        or (family == "PROP" and number == 12)
        or (family == "ELEC" and number in set(range(2, 16)))
        or any(token in claim_id for token in ("COORDINATION", "INORGANIC", "ORGANOMETALLIC", "METAL-", "MAGNETIC"))
    ):
        memberships.add("007")

    if (
        family == "ORG"
        or (family == "KIN" and number in set(range(6, 14)))
        or any(token in claim_id for token in ("ORGANIC", "STEREO", "CHIRAL", "ENANTIOMER", "DIASTEREOMER"))
    ):
        memberships.add("008")

    if family == "POLY" or "POLYMER" in claim_id:
        memberships.add("009")

    if source_count >= 2:
        memberships.add("010")

    # Every admitted empirical claim carries at least one falsification control;
    # VALID-011 deliberately retains the complete adverse/control surface rather
    # than selecting only claims whose prose happens to contain one keyword.
    memberships.add("011")
    return tuple(sorted(memberships))


def main() -> None:
    census = read(ROOT / "census/claims.json")
    chemistry_rows = sorted(
        (row for row in census["claims"] if row.get("branch") == "chemistry"),
        key=lambda row: row["claim_id"],
    )
    if len(chemistry_rows) != EXPECTED_BASE_COUNT:
        raise SystemExit(f"expected {EXPECTED_BASE_COUNT} admitted Chemistry claims, found {len(chemistry_rows)}")
    if any(not row.get("model_admitted") for row in chemistry_rows):
        raise SystemExit("the Chemistry census contains a non-admitted row")

    obligations = read(ROOT / "census/chemistry_discipline_obligations.json")["obligations"]
    frozen_rows: dict[str, dict] = {}
    for obligation in obligations:
        for claim_id in obligation.get("current_claim_ids", ()):
            frozen_rows[str(claim_id)] = obligation

    claim_vector: list[dict[str, object]] = []
    vector_claim_ids = {f"{number:03d}": [] for number in range(1, 13)}
    measurement_line_total = 0
    source_identity_total = 0
    tampered_control_total = 0
    explicit_status_line_total = 0
    status_terms = ("adverse", "unfavorable", "unfavourable", "absent", "unavailable", "unresolved", "mismatch", "inconsistent", "failed", "halt")

    for census_row in chemistry_rows:
        claim_id = str(census_row["claim_id"])
        package = ROOT / "claims" / claim_id
        registration_path = package / "registration.json"
        certificate_path = package / "certificate.json"
        empirical_path = package / "empirical_validation.json"
        receipt_path = ROOT / str(census_row["receipt_path"])
        for path in (registration_path, certificate_path, empirical_path, receipt_path):
            if not path.is_file():
                raise SystemExit(f"missing required Chemistry evidence: {path.relative_to(ROOT)}")

        registration = read(registration_path)
        certificate = read(certificate_path)
        empirical = read(empirical_path)
        receipt = read(receipt_path)
        if receipt.get("claim_id") != claim_id or not receipt.get("model_admitted"):
            raise SystemExit(f"invalid admitted receipt for {claim_id}")
        if receipt.get("receipt_hash") != census_row.get("receipt_hash"):
            raise SystemExit(f"census/receipt identity mismatch for {claim_id}")
        if certificate.get("engine_receipt_hash") != census_row.get("receipt_hash"):
            raise SystemExit(f"certificate/receipt identity mismatch for {claim_id}")
        if certificate.get("derivation_seal_hash") != empirical.get("validated_seal_hash"):
            raise SystemExit(f"derivation/empirical seal mismatch for {claim_id}")
        if not all(
            (
                empirical.get("passed") is True,
                empirical.get("evaluator_verified_seal") is True,
                empirical.get("target_opened_after_seal") is True,
                empirical.get("all_rows_preserved") is True,
                empirical.get("target_custody_certificate", {}).get("released_after_prediction_seal") is True,
                empirical.get("target_custody_certificate", {}).get("target_absent_until_prediction_seal") is True,
                receipt.get("closure_status") == "depth_independent",
                all(row.get("passed") is True for row in receipt.get("gate_results", ())),
            )
        ):
            raise SystemExit(f"incomplete empirical custody or engine gate for {claim_id}")

        sources = tuple(str(source) for source in empirical.get("data_source_ids", ()))
        measurements = tuple(str(line) for line in empirical.get("measurements", ()))
        if not sources or not measurements:
            raise SystemExit(f"empty empirical source or measurement vector for {claim_id}")
        tampered = sum("tamper" in line.casefold() for line in measurements)
        statuses = sum(any(term in line.casefold() for term in status_terms) for line in measurements)
        if tampered < 1:
            raise SystemExit(f"no retained tampered/falsification control for {claim_id}")
        obligation_id = obligation_from_certificate(claim_id, certificate, frozen_rows)
        memberships = vector_memberships(claim_id, obligation_id, len(sources))
        for number in memberships:
            vector_claim_ids[number].append(claim_id)

        claim_vector.append(
            {
                "claim_id": claim_id,
                "obligation_id": obligation_id,
                "vector_memberships": memberships,
                "registration_path": str(registration_path.relative_to(ROOT)),
                "registration_sha256": digest(registration_path),
                "certificate_path": str(certificate_path.relative_to(ROOT)),
                "certificate_sha256": digest(certificate_path),
                "empirical_validation_path": str(empirical_path.relative_to(ROOT)),
                "empirical_validation_sha256": digest(empirical_path),
                "receipt_path": str(receipt_path.relative_to(ROOT)),
                "receipt_file_sha256": digest(receipt_path),
                "receipt_hash": str(census_row["receipt_hash"]),
                "derivation_seal_hash": str(empirical["validated_seal_hash"]),
                "measurement_receipt_hash": str(empirical["measurement_receipt_hash"]),
                "prediction_seal_hash": str(empirical["target_custody_certificate"]["prediction_seal_hash"]),
                "target_identity_hash": str(empirical["target_custody_certificate"]["registered_target_identity_hash"]),
                "target_custody_certificate_hash": str(empirical["target_custody_certificate"]["certificate_hash"]),
                "source_ids": sources,
                "source_identity_count": len(sources),
                "measurement_line_count": len(measurements),
                "tampered_control_line_count": tampered,
                "explicit_adverse_absent_unavailable_unresolved_or_halt_line_count": statuses,
                "all_rows_preserved": True,
                "target_opened_after_seal": True,
                "model_admitted": True,
            }
        )
        measurement_line_total += len(measurements)
        source_identity_total += len(sources)
        tampered_control_total += tampered
        explicit_status_line_total += statuses

    if any(not vector_claim_ids[number] for number in vector_claim_ids):
        raise SystemExit("one or more VALID vectors has no evidence members")

    repair = read(REPAIR_AUDIT)
    payload: dict[str, object] = {
        "schema": "sft-v3-chemistry-valid-001-012-complete-empirical-vector/1",
        "date": "2026-07-28",
        "authority": "Maria Smith",
        "provenance": "aggregate reconstruction of individually sealed empirical comparisons; no new unknown-target blindness is claimed",
        "non_retirement_rule": "A failed attempt remains evidence and earns no closure credit. Every scientific obligation stays active until a distinct route succeeds through the untouched engine or a complete independently reconstructed enumeration proves impossibility.",
        "base_admitted_chemistry_claim_count": len(claim_vector),
        "base_measurement_line_count": measurement_line_total,
        "base_source_identity_occurrence_count": source_identity_total,
        "base_tampered_control_line_count": tampered_control_total,
        "base_explicit_adverse_absent_unavailable_unresolved_or_halt_line_count": explicit_status_line_total,
        "all_base_claims_model_admitted": True,
        "all_base_claims_depth_independent": True,
        "all_base_claims_target_opened_after_seal": True,
        "all_base_claims_rows_preserved": True,
        "all_base_claims_have_target_custody_certificate": True,
        "repair_audit_path": str(REPAIR_AUDIT.relative_to(ROOT)),
        "repair_audit_sha256": digest(REPAIR_AUDIT),
        "reopened_scientific_surface_count": repair["atomic_empirical_file_audit"]["actual_reopened_scientific_surfaces"],
        "attempt_status_constitution": repair["attempt_status_constitution"],
        "vector_claim_ids": vector_claim_ids,
        "vector_claim_counts": {number: len(claim_ids) for number, claim_ids in vector_claim_ids.items()},
        "claims": claim_vector,
        "protected_engine_or_verifier_edit_made": False,
    }
    payload["complete_vector_identity"] = canonical_digest(payload)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT.relative_to(ROOT)),
        "sha256": digest(OUTPUT),
        "complete_vector_identity": payload["complete_vector_identity"],
        "claim_count": len(claim_vector),
        "measurement_line_count": measurement_line_total,
        "source_identity_occurrence_count": source_identity_total,
        "vector_claim_counts": payload["vector_claim_counts"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
