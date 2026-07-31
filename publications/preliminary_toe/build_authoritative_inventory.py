#!/usr/bin/env python3
"""Build the direct-source inventory for the preliminary SFT V3 ToE synthesis."""

from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re


REPOSITORY = Path(__file__).resolve().parents[2]
OUTPUT = Path(__file__).resolve().parent / "AUTHORITATIVE_CORPUS_INVENTORY.json"
HISTORICAL_REPOSITORY = Path("/Users/mettamazza/Desktop/Smithian Fold Theory")


ACTIVE_PAPERS = {
    "methods": "publications/successors/methods/THERE_IS_NO_NOTHING_METHODS_PAPER_001_V0_3.md",
    "foundation": "publications/successors/foundation/FROM_NOTHING_TO_FOLD_FOUNDATION_PAPER_001_V1_3.md",
    "mathematics": "output/release/mathematics-1.5.0/02_From-Fold-to-Mathematics_Mathematics-Branch-Paper-001-v1.5.md",
    "information_science": "output/release/information-science-1.4.0/01_From-Distinction-to-Information_Information-Science-Branch-Paper-001-v1.4.md",
    "computation": "output/release/classical-computation-1.4.0/01_After-Turing-The-Fold-Machine_Classical-Computation-Branch-Paper-001-v1.4.md",
    "quantum_computation": "output/release/quantum-computation-1.4.0/01_The-Quantum-Fold-Machine_Quantum-Computation-Branch-Paper-001-v1.4.md",
    "physics": "output/release/physics-1.3.0/01_From-Fold-to-Physics_Physics-Branch-Paper-001-v1.3.md",
    "chemistry": "output/release/chemistry-1.3.0/01_From-Fold-to-Chemistry_Chemistry-Branch-Paper-001-v1.3.md",
    "materials": "output/release/materials-1.3.0/02_From-Fold-to-Materials_Materials-Science-Branch-Paper-001-v1.3.md",
    "biology": "output/release/biology-1.0.0/02_From-Fold-to-Life_Biology-and-Life-Sciences-Foundation-Paper-001-v1.0.md",
    "medicine": "output/release/medicine-1.0.0/02_From-Fold-to-Medicine_Medicine-and-Health-Sciences-Foundation-Paper-001-v1.0.md",
    "consciousness_cognitive_science": "output/release/consciousness-cognitive-science-1.0.0/02_From-Fold-to-Consciousness_Consciousness-and-Cognitive-Science-Foundation-Paper-001-v1.0.md",
    "earth_environment": "output/release/earth-environment-1.0.0/02_From-One-World-to-Earth_Earth-and-Environmental-Sciences-Foundation-Paper-001-v1.0.md",
    "astronomy_cosmology": "output/release/astronomy-cosmology-1.0.0/02_From-One-Sky-to-Cosmos_Astronomy-and-Cosmology-Foundation-Paper-001-v1.0.md",
    "social_collective_systems": "output/release/social-collective-sciences-1.0.0/02_From-One-Relation-to-Society_Social-Collective-Sciences-Foundation-Paper-001-v1.0.md",
    "engineering_translation": "output/release/engineering-translation-1.0.0/02_From-One-Law-to-a-Working-World_Engineering-Translation-Foundation-Paper-001-v1.0.md",
    "protein_fold_preliminary": "applications/frontier/v3_computational_proofs/protein_folding/paper/SMITHIAN_FOLD_THEORY_V3_PROTEIN_FOLD_COMPUTATIONAL_PROOF.md",
}


HISTORICAL_PROGRAMME_MANIFESTS = {
    "chess_v2_2": "application_releases/2026-07-17/chess_release_manifest_v2.2.json",
    "go_v2_2": "application_releases/2026-07-17/go_release_manifest_v2.2.json",
    "protein_blind_76_v3_7": "application_releases/2026-07-17/protein_blind_76_release_manifest_v3.7.json",
    "unison_v6_3": "application_releases/2026-07-17/unison_release_manifest_v6.3.json",
}


def digest_bytes(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def relative_record(path: Path, *, root: Path = REPOSITORY) -> dict[str, object]:
    payload = path.read_bytes()
    try:
        display_path = str(path.relative_to(root))
    except ValueError:
        display_path = str(path)
    return {
        "path": display_path,
        "sha256": digest_bytes(payload),
        "bytes": len(payload),
    }


def paper_record(relative_path: str) -> dict[str, object]:
    path = REPOSITORY / relative_path
    payload = path.read_bytes()
    text = payload.decode("utf-8")
    lines = text.splitlines()
    headings = [line.strip() for line in lines if re.match(r"^#{1,6}\s+", line)]
    title = next(
        (re.sub(r"^#\s+", "", line).strip() for line in lines if line.startswith("# ")),
        None,
    )
    dois = sorted(set(re.findall(r"10\.5281/zenodo\.\d+", text)))
    version_tokens = sorted(
        set(
            re.findall(
                r"(?i)(?:version|v)\s*[0-9]+(?:\.[0-9]+){1,2}",
                "\n".join(lines[:80]),
            )
        )
    )
    return {
        "path": relative_path,
        "sha256": digest_bytes(payload),
        "bytes": len(payload),
        "line_count": len(lines),
        "heading_count": len(headings),
        "title": title,
        "doi_tokens": dois,
        "version_tokens": version_tokens,
        "full_text_read": True,
    }


def claim_package_record(claim: dict[str, object]) -> dict[str, object]:
    claim_id = str(claim["claim_id"])
    package = REPOSITORY / "claims" / claim_id
    registration_path = package / "registration.json"
    certificate_path = package / "certificate.json"
    controls_path = package / "controls.json"
    candidate_census_path = package / "candidate_census.json"
    elimination_path = package / "elimination_receipt.json"
    registration = json.loads(registration_path.read_bytes())
    certificate = json.loads(certificate_path.read_bytes())
    controls = json.loads(controls_path.read_bytes())["controls"]
    candidate_census = json.loads(candidate_census_path.read_bytes())
    elimination = (
        json.loads(elimination_path.read_bytes()) if elimination_path.exists() else None
    )
    candidates = candidate_census["candidates"]
    decisions = elimination["decisions"] if elimination else None
    candidate_count = int(
        certificate.get("candidate_count", len(candidates))
    )
    survivor_count = int(
        certificate.get(
            "unique_survivor_count",
            (
                sum(bool(row.get("survives")) for row in decisions)
                if decisions is not None
                else 0
            ),
        )
    )
    receipt_path = REPOSITORY / str(claim["receipt_path"])
    receipt_payload = receipt_path.read_bytes() if receipt_path.exists() else None
    receipt_sha256 = digest_bytes(receipt_payload) if receipt_payload else None
    receipt = json.loads(receipt_payload) if receipt_payload else {}
    registered_receipt_id = str(claim["receipt_hash"])
    receipt_identity_matches = (
        receipt.get("receipt_hash") == registered_receipt_id
        and receipt.get("claim_id") == claim_id
        and receipt.get("model_admitted") == claim["model_admitted"]
        and receipt.get("closure_status") == claim["closure_status"]
        and receipt.get("external_status") == claim["external_status"]
    )
    return {
        "claim_id": claim_id,
        "branch": claim["branch"],
        "title": claim["title"],
        "statement": claim["statement"],
        "closure_status": claim["closure_status"],
        "external_status": claim["external_status"],
        "model_admitted": claim["model_admitted"],
        "dependencies": registration.get("dependencies", []),
        "candidate_count": candidate_count,
        "candidate_count_matches_census": (
            candidate_count
            == len(candidates)
            == int(candidate_census["expected_cardinality"])
            and (decisions is None or candidate_count == len(decisions))
        ),
        "unique_survivor_count": survivor_count,
        "survivor_count_matches_decisions": (
            survivor_count == sum(bool(row.get("survives")) for row in decisions)
            if decisions is not None
            else None
        ),
        "control_count": len(controls),
        "passed_control_count": sum(bool(row.get("passed")) for row in controls),
        "receipt_path": claim["receipt_path"],
        "receipt_file_sha256": receipt_sha256,
        "registered_receipt_id": registered_receipt_id,
        "receipt_internal_id": receipt.get("receipt_hash"),
        "receipt_identity_matches": receipt_identity_matches,
        "registration_sha256": digest_bytes(registration_path.read_bytes()),
        "certificate_sha256": digest_bytes(certificate_path.read_bytes()),
        "controls_sha256": digest_bytes(controls_path.read_bytes()),
        "candidate_census_sha256": digest_bytes(candidate_census_path.read_bytes()),
        "elimination_receipt_sha256": (
            digest_bytes(elimination_path.read_bytes())
            if elimination_path.exists()
            else None
        ),
    }


def root_reachable(
    claim_id: str,
    dependencies: dict[str, tuple[str, ...]],
    known_claims: set[str],
    memo: dict[str, bool],
    visiting: set[str],
) -> bool:
    root = "SFT-ROOT-THERE-IS-NO-NOTHING"
    if claim_id == root:
        return True
    if claim_id in memo:
        return memo[claim_id]
    if claim_id in visiting:
        memo[claim_id] = False
        return False
    visiting.add(claim_id)
    result = any(
        dependency in known_claims
        and root_reachable(dependency, dependencies, known_claims, memo, visiting)
        for dependency in dependencies.get(claim_id, ())
    )
    visiting.remove(claim_id)
    memo[claim_id] = result
    return result


def main() -> int:
    claim_ledger_path = REPOSITORY / "census/claims.json"
    claim_ledger = json.loads(claim_ledger_path.read_bytes())
    claims = claim_ledger["claims"]
    package_records = [claim_package_record(claim) for claim in claims]
    known_claims = {str(row["claim_id"]) for row in claims}
    dependency_map = {
        str(row["claim_id"]): tuple(str(value) for value in row["dependencies"])
        for row in package_records
    }
    missing_dependencies = sorted(
        {
            dependency
            for dependencies in dependency_map.values()
            for dependency in dependencies
            if dependency not in known_claims
        }
    )
    memo: dict[str, bool] = {}
    root_traced = {
        claim_id: root_reachable(claim_id, dependency_map, known_claims, memo, set())
        for claim_id in known_claims
    }

    branch_rows: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in package_records:
        branch_rows[str(record["branch"])].append(record)
    branch_summary = {}
    for branch, rows in sorted(branch_rows.items()):
        branch_summary[branch] = {
            "claim_count": len(rows),
            "model_admitted_count": sum(bool(row["model_admitted"]) for row in rows),
            "candidate_count": sum(int(row["candidate_count"] or 0) for row in rows),
            "survivor_count": sum(
                int(row["unique_survivor_count"] or 0) for row in rows
            ),
            "control_count": sum(int(row["control_count"]) for row in rows),
            "passed_control_count": sum(
                int(row["passed_control_count"]) for row in rows
            ),
            "receipt_identity_match_count": sum(
                bool(row["receipt_identity_matches"]) for row in rows
            ),
            "candidate_census_match_count": sum(
                bool(row["candidate_count_matches_census"]) for row in rows
            ),
            "survivor_decision_match_count": sum(
                bool(row["survivor_count_matches_decisions"]) for row in rows
            ),
            "survivor_decision_available_count": sum(
                row["survivor_count_matches_decisions"] is not None for row in rows
            ),
            "root_traced_count": sum(
                bool(root_traced[str(row["claim_id"])]) for row in rows
            ),
            "closure_statuses": dict(
                sorted(Counter(str(row["closure_status"]) for row in rows).items())
            ),
            "external_statuses": dict(
                sorted(Counter(str(row["external_status"]) for row in rows).items())
            ),
        }

    historical_programmes = {}
    for name, relative_path in HISTORICAL_PROGRAMME_MANIFESTS.items():
        path = HISTORICAL_REPOSITORY / relative_path
        payload = path.read_bytes()
        historical_programmes[name] = {
            **relative_record(path, root=HISTORICAL_REPOSITORY),
            "manifest": json.loads(payload),
            "evidence_class": "historical_versioned_implementation_record",
            "current_v3_proof_authority": False,
        }

    active_papers = {
        branch: paper_record(path) for branch, path in ACTIVE_PAPERS.items()
    }
    direct_inputs = {
        "publication_guidance": relative_record(
            REPOSITORY / "publication guidance.md"
        ),
        "final_toe_protocol": relative_record(
            REPOSITORY / "publications/FINAL_TOE_PAPER_PROTOCOL.md"
        ),
        "current_programme_status": relative_record(
            REPOSITORY / "audits/CURRENT_PROGRAMME_STATUS_2026-07-29.md"
        ),
        "complete_field_publication_status": relative_record(
            REPOSITORY / "publication/FINAL_COMPLETE_FIELD_PUBLICATIONS_2026-07-29.md"
        ),
        "claim_ledger": relative_record(claim_ledger_path),
        "prior_v6_toe": relative_record(
            HISTORICAL_REPOSITORY / "THE_SMITHIAN_FOLD_THEORY_OF_EVERYTHING.md",
            root=HISTORICAL_REPOSITORY,
        ),
        "protein_current_gate_v20": relative_record(
            REPOSITORY
            / "applications/frontier/v3_computational_proofs/protein_folding/audits/current_scientific_gate_v20.json"
        ),
        "protein_publication_receipt": relative_record(
            REPOSITORY
            / "applications/frontier/v3_computational_proofs/protein_folding/publication/protein_fold_preliminary_zenodo_publication_receipt_v0_9_4.json"
        ),
        "unison_v3_workspace": relative_record(
            REPOSITORY
            / "applications/frontier/v3_computational_proofs/Unison Fold AI/workspace_manifest.json"
        ),
    }

    record = {
        "schema": "sft-v3-preliminary-toe-authoritative-corpus-inventory/v1",
        "date": "2026-07-31",
        "status": (
            "direct_source_inventory_complete__preliminary_toe_authoring_open__"
            "final_computational_proofs_and_full_field_programme_open"
        ),
        "authority": {
            "author": "Maria Smith",
            "publication_authority": "Maria Smith",
            "organisation": "Ernos Labs",
            "paper_status": "preliminary synthesis; not the final completed ToE",
            "protected_authority_edited": False,
        },
        "direct_inputs": direct_inputs,
        "active_papers": active_papers,
        "claim_ledger": {
            "claim_count": len(package_records),
            "model_admitted_count": sum(
                bool(row["model_admitted"]) for row in package_records
            ),
            "candidate_count": sum(
                int(row["candidate_count"] or 0) for row in package_records
            ),
            "survivor_count": sum(
                int(row["unique_survivor_count"] or 0) for row in package_records
            ),
            "control_count": sum(int(row["control_count"]) for row in package_records),
            "passed_control_count": sum(
                int(row["passed_control_count"]) for row in package_records
            ),
            "receipt_identity_match_count": sum(
                bool(row["receipt_identity_matches"]) for row in package_records
            ),
            "candidate_census_match_count": sum(
                bool(row["candidate_count_matches_census"])
                for row in package_records
            ),
            "survivor_decision_match_count": sum(
                bool(row["survivor_count_matches_decisions"])
                for row in package_records
            ),
            "survivor_decision_available_count": sum(
                row["survivor_count_matches_decisions"] is not None
                for row in package_records
            ),
            "root_traced_count": sum(root_traced.values()),
            "missing_dependency_count": len(missing_dependencies),
            "missing_dependencies": missing_dependencies,
            "unclassified_obligations": claim_ledger.get(
                "unclassified_obligations", []
            ),
            "branch_summary": branch_summary,
            "claims": package_records,
        },
        "historical_computational_programmes": historical_programmes,
        "current_v3_computational_programmes": {
            "protein_fold": {
                "status_source": direct_inputs["protein_current_gate_v20"],
                "publication_receipt": direct_inputs["protein_publication_receipt"],
                "status": (
                    "preliminary_v0.9.4_published__fixed_geometry_lower_bands_"
                    "global_frontier_whole_chain_recurrence_and_100_target_"
                    "alphafold_parity_campaign_open"
                ),
            },
            "unison_fold_ai": {
                "status_source": direct_inputs["unison_v3_workspace"],
                "status": "frontier_scaffold__mathematical_closure_open__empirical_validation_not_run",
            },
            "chess_fold": {
                "workspace_present": False,
                "status": "v3_clean_recreation_not_started_in_current_repository",
            },
            "go_fold": {
                "workspace_present": False,
                "status": "v3_clean_recreation_not_started_in_current_repository",
            },
        },
        "publication_boundary": {
            "conceptual_paper_required": True,
            "scientific_audit_layer_required": True,
            "machine_archive_required": True,
            "final_toe_protocol_satisfied": False,
            "final_computational_proofs_complete": False,
            "final_global_heavy_verification_complete": False,
            "preliminary_version_may_be_updated": True,
            "remote_publication_authorised": True,
            "publication_operation": "create_new_standalone_v3_record",
            "zenodo_draft_id": 21717584,
            "zenodo_concept_record_id": 21717583,
            "reserved_version_doi": "10.5281/zenodo.21717584",
        },
    }
    OUTPUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "path": str(OUTPUT.relative_to(REPOSITORY)),
                "sha256": digest_bytes(OUTPUT.read_bytes()),
                "claims": len(package_records),
                "candidates": record["claim_ledger"]["candidate_count"],
                "controls": record["claim_ledger"]["control_count"],
                "receipt_matches": record["claim_ledger"][
                    "receipt_identity_match_count"
                ],
                "root_traced": record["claim_ledger"]["root_traced_count"],
                "missing_dependencies": len(missing_dependencies),
                "papers_read": len(active_papers),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
