#!/usr/bin/env python3
"""Build a non-admitting receipt crosswalk for every Physics prior obligation.

This tool prevents a missing ledger mapping from being mistaken for a missing
derivation.  It compares each V1/V2 observation with the complete live set of
model-admitted Physics registrations and certificates, records the strongest
lexical candidates, and binds every candidate to its immutable engine receipt.

Candidate ranking is an audit aid only.  It cannot mark an obligation closed;
same-strength closure still requires an explicit reviewed mapping.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "census/physics_prior_obligations.json"
CENSUS = ROOT / "census/claims.json"
OUTPUT = ROOT / "audits/physics_prior_receipt_reconciliation_candidates.json"


STOP = {
    "a", "all", "an", "and", "are", "as", "at", "be", "been", "being",
    "between", "by", "can", "each", "every", "for", "from", "has", "have",
    "in", "into", "is", "it", "its", "no", "not", "of", "on", "one", "or",
    "other", "over", "same", "that", "the", "their", "then", "this", "through",
    "to", "under", "using", "was", "when", "where", "which", "while", "with",
    "without", "would", "v1", "v2", "v3", "sft", "fold", "framework", "proven",
    "proves", "verified", "result", "exact", "positive", "complete",
}


CANONICAL = {
    "atomic": "atom", "atoms": "atom",
    "baryonic": "baryon", "baryons": "baryon",
    "blackbody": "blackbody", "black-body": "blackbody",
    "cosmological": "cosmology", "cosmic": "cosmology",
    "electromagnetic": "electromagnetism", "electromagnetism": "electromagnetism",
    "electronic": "electron", "electrons": "electron",
    "entangled": "entanglement",
    "fields": "field",
    "forces": "force",
    "frequencies": "frequency",
    "gravitational": "gravity", "gravitation": "gravity",
    "horizons": "horizon",
    "interferes": "interference", "interfering": "interference",
    "magnetic": "magnetism",
    "measurements": "measurement", "measured": "measurement",
    "molecular": "molecule", "molecules": "molecule",
    "neutrinos": "neutrino",
    "nuclear": "nucleus", "nuclei": "nucleus",
    "oscillations": "oscillation", "oscillators": "oscillation",
    "particles": "particle",
    "photons": "photon",
    "quantised": "quantum", "quantized": "quantum",
    "relativistic": "relativity",
    "spectra": "spectrum", "spectral": "spectrum",
    "spatial": "space",
    "thermodynamic": "thermodynamics",
    "transitions": "transition",
    "vacua": "vacuum",
    "waves": "wave",
}


def tokens(text: str) -> tuple[str, ...]:
    raw = re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)?", text.lower())
    normalized: list[str] = []
    for token in raw:
        token = CANONICAL.get(token, token)
        if token in STOP or len(token) < 2:
            continue
        if token.endswith("ies") and len(token) > 5:
            token = token[:-3] + "y"
        elif token.endswith("s") and len(token) > 5 and not token.endswith("ss"):
            token = token[:-1]
        normalized.append(CANONICAL.get(token, token))
    return tuple(normalized)


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def claim_documents() -> tuple[list[dict[str, object]], dict[str, int]]:
    census = json.loads(CENSUS.read_text(encoding="utf-8"))["claims"]
    rows: list[dict[str, object]] = []
    document_frequency: Counter[str] = Counter()
    for claim in census:
        if claim.get("branch") != "physics" or not claim.get("model_admitted"):
            continue
        claim_id = str(claim["claim_id"])
        package = ROOT / "claims" / claim_id
        registration_path = package / "registration.json"
        certificate_path = package / "certificate.json"
        registration = json.loads(registration_path.read_text(encoding="utf-8"))
        certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
        title = str(registration.get("title", claim.get("title", "")))
        statement = str(registration.get("statement", claim.get("statement", "")))
        exact_result = str(certificate.get("exact_result", ""))
        dependency_ids = tuple(str(value) for value in registration.get("dependencies", ()))
        title_tokens = tokens(claim_id.replace("SFT-PHYS-", "") + " " + title)
        body_tokens = tokens(statement + " " + exact_result + " " + " ".join(dependency_ids))
        combined = title_tokens + body_tokens
        document_frequency.update(set(combined))
        rows.append({
            "claim_id": claim_id,
            "title": title,
            "statement": statement,
            "exact_result": exact_result,
            "dependencies": dependency_ids,
            "title_tokens": title_tokens,
            "body_tokens": body_tokens,
            "all_tokens": combined,
            "receipt_hash": claim["receipt_hash"],
            "receipt_path": claim["receipt_path"],
            "external_status": claim["external_status"],
            "closure_status": claim["closure_status"],
            "registration_hash": file_hash(registration_path),
            "certificate_hash": file_hash(certificate_path),
        })
    return rows, dict(document_frequency)


def rank(observation: str, claims: list[dict[str, object]], frequency: dict[str, int]) -> list[dict[str, object]]:
    query = Counter(tokens(observation))
    candidates: list[dict[str, object]] = []
    for claim in claims:
        title = Counter(claim["title_tokens"])
        body = Counter(claim["body_tokens"])
        common = sorted(set(query) & set(title | body))
        if not common:
            continue
        weighted = 0
        title_bonus = 0
        for token in common:
            rarity = max(1, 10000 // max(1, frequency.get(token, 1)))
            overlap = min(query[token], title[token] + body[token])
            weighted += rarity * overlap
            if title[token]:
                title_bonus += rarity * min(query[token], title[token])
        score = weighted + 2 * title_bonus
        candidates.append({
            "claim_id": claim["claim_id"],
            "title": claim["title"],
            "score": score,
            "query_token_coverage": f"{sum(query[token] for token in common)}/{sum(query.values())}",
            "common_tokens": common,
            "receipt_hash": claim["receipt_hash"],
            "receipt_path": claim["receipt_path"],
            "external_status": claim["external_status"],
            "closure_status": claim["closure_status"],
            "registration_hash": claim["registration_hash"],
            "certificate_hash": claim["certificate_hash"],
        })
    return sorted(candidates, key=lambda row: (-int(row["score"]), str(row["claim_id"])))[:12]


def main() -> None:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    claims, frequency = claim_documents()
    entries: list[dict[str, object]] = []
    for source in ledger["source_entries"]:
        obligation = source["atomic_obligations"][0]
        candidates = rank(str(obligation["prior_observation"]), claims, frequency)
        entries.append({
            "source": source["source"],
            "source_entry": source["source_entry"],
            "source_hash": source["source_hash"],
            "atomic_obligation_id": obligation["atomic_obligation_id"],
            "prior_observation": obligation["prior_observation"],
            "current_same_strength_closed": obligation["same_strength_closed"],
            "current_v3_claim_ids": obligation["v3_claim_ids"],
            "review_status": "already_mapped" if obligation["same_strength_closed"] else "candidate_review_required",
            "candidate_matches": candidates,
        })
    open_entries = [row for row in entries if not row["current_same_strength_closed"]]
    payload = {
        "schema": "sft-v3-physics-prior-receipt-reconciliation-candidates/1",
        "status": "audit_candidates_only_non_admitting",
        "policy": {
            "live_receipts_are_authoritative": True,
            "missing_mapping_is_not_missing_derivation": True,
            "candidate_rank_does_not_close_obligation": True,
            "manual_same_strength_review_required": True,
            "new_derivation_forbidden_until_absence_confirmed": True,
        },
        "inputs": {
            "obligation_ledger": str(LEDGER.relative_to(ROOT)),
            "obligation_ledger_hash": file_hash(LEDGER),
            "claim_census": str(CENSUS.relative_to(ROOT)),
            "claim_census_hash": file_hash(CENSUS),
            "admitted_physics_claim_count": len(claims),
        },
        "summary": {
            "physics_obligation_count": len(entries),
            "currently_closed_count": len(entries) - len(open_entries),
            "candidate_review_required_count": len(open_entries),
            "open_with_at_least_one_candidate": sum(bool(row["candidate_matches"]) for row in open_entries),
            "open_without_candidate": sum(not row["candidate_matches"] for row in open_entries),
        },
        "entries": entries,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"wrote {OUTPUT.relative_to(ROOT)}: obligations={len(entries)} "
        f"closed={len(entries)-len(open_entries)} review={len(open_entries)} "
        f"with-candidate={payload['summary']['open_with_at_least_one_candidate']}"
    )


if __name__ == "__main__":
    main()
