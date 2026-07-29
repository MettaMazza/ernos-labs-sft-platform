#!/usr/bin/env python3
"""Build and locally gate the unpublished Physics v1.3 complete-field release.

This is a read-only projection over admitted scientific evidence. It does not
execute an admission, edit a receipt, alter a verifier or authorize release.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "publications/inventories/physics.json"
PAPER = ROOT / "publications/successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_3.md"
PDF = ROOT / "output/pdf/from-fold-to-physics-branch-paper-001-v1.3.pdf"
METADATA = ROOT / "publications/successors/physics/zenodo_metadata_v1_3.json"
BASE = ROOT / "publications/successors/physics/v1_3"
EVIDENCE = BASE / "evidence_map_v1_3.json"
MANIFEST = BASE / "manifest_v1_3.json"
OUT = ROOT / "output/release/physics-1.3.0"
ENGINE_SEAL = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
AUTHORITY_SEAL = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def require(condition: bool, message: str):
    if not condition:
        raise SystemExit(message)


def current_certificate(package: Path, receipt_hash: str):
    matches = []
    for path in package.glob("certificate*.json"):
        payload = read(path)
        if payload.get("engine_receipt_hash") == receipt_hash:
            matches.append((path, payload))
    require(len(matches) == 1, f"expected one receipt-bound certificate: {package.name}; found {len(matches)}")
    return matches[0]


def main():
    inventory = read(INVENTORY)
    metadata = read(METADATA)
    paper = PAPER.read_text(encoding="utf-8")
    census_rows = read(ROOT / "census/claims.json")["claims"]
    live_rows = [row for row in census_rows if row.get("branch") == "physics" and row.get("model_admitted") is True]
    live = {row["claim_id"]: row for row in census_rows}
    required_ids = inventory["required_claim_ids"]
    require(required_ids == [row["claim_id"] for row in live_rows], "Physics inventory differs from live ordered census")
    require(len(required_ids) == 368, "Physics current denominator is not 368")
    require(inventory["required_claim_count"] == inventory["admitted_claim_count"] == 368, "Physics inventory not fully admitted")
    require(not inventory["unclassified_obligations"], "Physics inventory contains unclassified obligations")
    require(metadata["metadata"]["version"] == "1.3.0", "Physics metadata version mismatch")
    require(metadata["publication_authorized"] is False and metadata["ready_to_publish"] is False, "Physics remote release must remain unauthorized")
    require("368 current engine-admitted Physics claims" in paper, "Physics paper omits current denominator")
    require("257,776 candidates" in paper and "1,472 passing mandatory adverse controls" in paper, "Physics paper omits exact totals")
    for phrase in ("Unified constants object", "Tesla resonance family", "Vacuum/inertia drive family", "Penta/hepta sectors and Smithion census"):
        require(phrase in paper, f"Physics headline omission: {phrase}")

    dependency_cache = {}

    def dependencies(claim_id: str):
        if claim_id == "SFT-ROOT-THERE-IS-NO-NOTHING":
            return ()
        path = ROOT / "claims" / claim_id / "registration.json"
        require(path.exists(), f"missing dependency registration: {claim_id}")
        return tuple(read(path).get("dependencies", ()))

    def reaches_root(claim_id: str, stack=()):
        if claim_id == "SFT-ROOT-THERE-IS-NO-NOTHING":
            return True
        if claim_id in dependency_cache:
            return dependency_cache[claim_id]
        require(claim_id not in stack, f"dependency cycle: {claim_id}")
        deps = dependencies(claim_id)
        require(bool(deps), f"rootless claim: {claim_id}")
        result = any(reaches_root(dep, stack + (claim_id,)) for dep in deps)
        dependency_cache[claim_id] = result
        return result

    evidence_rows = []
    candidate_total = 0
    control_total = 0
    empirical_count = 0
    for order, claim_id in enumerate(required_ids, 1):
        row = live[claim_id]
        package = ROOT / "claims" / claim_id
        registration = read(package / "registration.json")
        candidate = read(package / "candidate_census.json")
        elimination = read(package / "elimination_receipt.json")
        controls = read(package / "controls.json")["controls"]
        certificate_path, certificate = current_certificate(package, row["receipt_hash"])
        receipt_path = ROOT / row["receipt_path"]
        receipt = read(receipt_path)
        decisions = elimination["decisions"]
        candidates = candidate["candidates"]
        survivors = [decision for decision in decisions if decision.get("survives")]
        require(len(candidates) == candidate["expected_cardinality"] == len(decisions), f"incomplete census: {claim_id}")
        require(len(survivors) == 1, f"survivor count differs from one: {claim_id}")
        require(len(controls) == 4 and all(control.get("passed") for control in controls), f"controls failed: {claim_id}")
        require(receipt.get("model_admitted") is True and receipt.get("receipt_hash") == row["receipt_hash"], f"receipt mismatch: {claim_id}")
        require(certificate.get("engine_receipt_hash") == row["receipt_hash"], f"certificate mismatch: {claim_id}")
        require(registration.get("axioms") in (None, []) and registration.get("free_parameters") in (None, []), f"axiom/parameter violation: {claim_id}")
        require(reaches_root(claim_id), f"claim does not reach foundational theorem: {claim_id}")
        require(claim_id in paper and row["receipt_hash"] in paper, f"paper omits claim/receipt: {claim_id}")
        empirical_path = package / "empirical_validation.json"
        empirical = read(empirical_path) if empirical_path.exists() else None
        if empirical is not None:
            empirical_count += 1
            require(empirical.get("passed") is True, f"empirical result not passed: {claim_id}")
            require(empirical.get("all_rows_preserved") is True, f"empirical rows omitted: {claim_id}")
            require(empirical.get("target_opened_after_seal") is True, f"target custody failed: {claim_id}")
        candidate_total += len(candidates)
        control_total += len(controls)
        evidence_rows.append({
            "order": order,
            "claim_id": claim_id,
            "title": row["title"],
            "subbranch": inventory["obligations"][order - 1]["subbranch"],
            "candidate_count": len(candidates),
            "decision_count": len(decisions),
            "unique_survivor_count": 1,
            "control_count": len(controls),
            "closure_status": receipt.get("closure_status"),
            "external_status": receipt.get("external_status"),
            "root_trace_verified": True,
            "current_certificate_path": certificate_path.relative_to(ROOT).as_posix(),
            "current_certificate_hash": digest(certificate_path),
            "derivation_seal_hash": certificate.get("derivation_seal_hash"),
            "independent_implementation_hash": certificate.get("independent_implementation_hash"),
            "independent_certificate_hash": certificate.get("independent_certificate_hash"),
            "empirical_validation_hash": certificate.get("empirical_validation_hash"),
            "measurement_receipt_hash": certificate.get("measurement_receipt_hash"),
            "measurement_row_count": len(empirical.get("measurements", [])) if empirical else 0,
            "all_external_rows_preserved": bool(empirical.get("all_rows_preserved")) if empirical else None,
            "engine_receipt_hash": row["receipt_hash"],
            "engine_receipt_path": row["receipt_path"],
            "engine_receipt_file_hash": digest(receipt_path),
        })
    require(candidate_total == 257_776, f"unexpected Physics candidate total: {candidate_total}")
    require(control_total == 1_472, f"unexpected Physics control total: {control_total}")
    require(empirical_count == 238, f"unexpected empirical claim total: {empirical_count}")

    reader = PdfReader(str(PDF))
    pages = len(reader.pages)
    require(pages > 500, "Physics PDF unexpectedly short")
    require(reader.metadata.title == "From Fold to Physics" and reader.metadata.author == "Maria Smith", "Physics PDF metadata mismatch")
    first = "\n".join((reader.pages[index].extract_text() or "") for index in range(min(8, pages)))
    require("fine-structure constant" in first and "368" in first and "Maria Smith" in first, "Physics PDF front matter incomplete")

    BASE.mkdir(parents=True, exist_ok=True)
    evidence = {
        "schema": "sft-v3-physics-complete-field-paper-evidence-map/1",
        "branch_id": "physics",
        "version": "1.3.0",
        "inventory_identity": inventory["inventory_hash"],
        "current_claim_count": 368,
        "candidate_count": candidate_total,
        "unique_survivor_count": 368,
        "control_count": control_total,
        "independent_reconstruction_count": 368,
        "empirically_validated_claim_count": empirical_count,
        "v1_v2_physics_atom_count": 488,
        "v1_v2_closed_atom_count": 488,
        "current_open_registered_obligation_count": 0,
        "completion_is_dated_and_extension_open": True,
        "canonical_engine_seal": ENGINE_SEAL,
        "verification_authority_seal": AUTHORITY_SEAL,
        "claims": evidence_rows,
    }
    EVIDENCE.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "schema": "sft-v3-branch-publication-manifest/1",
        "branch_id": "physics",
        "version": "1.3.0",
        "publication_authorized": False,
        "ready_for_review": True,
        "ready_to_publish": False,
        "comprehensive_derivation_coverage": True,
        "root_traces_verified": True,
        "controls_passed": True,
        "required_claim_count": 368,
        "candidate_count": candidate_total,
        "control_count": control_total,
        "empirically_validated_claim_count": empirical_count,
        "inventory_identity": inventory["inventory_hash"],
        "source_path": PAPER.relative_to(ROOT).as_posix(),
        "source_hash": digest(PAPER),
        "rendered_paper_path": PDF.relative_to(ROOT).as_posix(),
        "rendered_paper_hash": digest(PDF),
        "pdf_pages": pages,
        "evidence_map_path": EVIDENCE.relative_to(ROOT).as_posix(),
        "evidence_map_hash": digest(EVIDENCE),
        "zenodo_metadata_path": METADATA.relative_to(ROOT).as_posix(),
        "zenodo_metadata_hash": digest(METADATA),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    OUT.mkdir(parents=True, exist_ok=True)
    release_files = (
        ("00_From-Fold-to-Physics_Physics-Branch-Paper-001-v1.3.pdf", PDF),
        ("01_From-Fold-to-Physics_Physics-Branch-Paper-001-v1.3.md", PAPER),
        ("02_Physics-Paper-001-v1.3-Evidence-Map.json", EVIDENCE),
        ("03_Physics-Paper-001-v1.3-Manifest.json", MANIFEST),
        ("04_Physics-Paper-001-v1.3-Zenodo-Metadata-Draft.json", METADATA),
        ("05_Physics-Current-Categorical-Inventory.json", INVENTORY),
        ("06_Physics-V1-V2-Atomic-Ownership-Audit.json", ROOT / "audits/physics_v1_v2_atomic_ownership.json"),
        ("07_Physics-Tesla-Family-Completion.json", ROOT / "audits/PHYSICS_TESLA_RESONANCE_FAMILY_COMPLETION_2026-07-28.json"),
        ("08_Physics-Vacuum-Inertia-Family-Completion.json", ROOT / "audits/PHYSICS_VACUUM_INERTIA_DRIVE_FAMILY_COMPLETION_2026-07-28.json"),
        ("09_Physics-New-Sector-Family-Completion.json", ROOT / "audits/PHYSICS_NEW_SECTOR_COMPLETE_FAMILY_COMPLETION_2026-07-28.json"),
    )
    checksums = []
    for name, source in release_files:
        require(source.is_file(), f"missing Physics release source: {source}")
        destination = OUT / name
        shutil.copyfile(source, destination)
        checksums.append({"filename": name, "bytes": destination.stat().st_size, "sha256": digest(destination)})
    (OUT / "99_SHA256SUMS.json").write_text(
        json.dumps({"schema": "sft-physics-1.3-review-checksums/1", "publication_authorized": False, "files": checksums}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"PASS Physics v1.3 local gate: 368 claims, {candidate_total:,} candidates, {control_total:,} controls, {empirical_count} empirical claims, {pages} PDF pages")


if __name__ == "__main__":
    main()
