"""Materialize the frozen Chemistry obligation inventory without admission."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.obligations import OBLIGATIONS, SUBBRANCH_ORDER  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


def main() -> None:
    external_path = ROOT / "experiments/external_sources/chemistry/authoritative_sources.json"
    external = json.loads(external_path.read_text(encoding="utf-8"))
    sources = {row["source_id"]: row for row in external["sources"]}
    missing_ids = sorted({source for row in OBLIGATIONS for source in row.external_source_ids} - set(sources))
    if missing_ids:
        raise SystemExit("unregistered Chemistry external sources: " + ", ".join(missing_ids))
    for source in sources.values():
        snapshot = ROOT / source["snapshot_path"]
        if not snapshot.is_file():
            raise SystemExit(f"missing Chemistry snapshot: {source['snapshot_path']}")
        if hash_file(snapshot) != source["snapshot_hash"]:
            raise SystemExit(f"changed Chemistry snapshot: {source['source_id']}")

    admitted = {
        row["claim_id"]
        for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
    }
    rows = []
    for position, obligation in enumerate(OBLIGATIONS, 1):
        values = asdict(obligation)
        values["position"] = position
        values["status"] = "model_admitted" if obligation.claim_id in admitted else "registered_not_admitted"
        rows.append(values)
    counts = Counter(row.subbranch for row in OBLIGATIONS)
    payload = {
        "schema": "sft-v3-chemistry-branch-inventory/1",
        "branch_id": "chemistry",
        "inventory_frozen": True,
        "inventory_date": "2026-07-24",
        "scope": "Complete categorical Chemistry reconstruction through chemical observation and identity; elements and periodicity; composition and stoichiometry; bonding and molecular organization; acid/base, redox and electrochemistry; reactions, kinetics and thermochemistry; catalysis, networks and interfaces; stereochemistry, organic and polymer structure; analytical and spectroscopic correspondence; and explicit g-block, Smithium and periodic-endpoint predictions.",
        "exclusions": [
            "materials bulk-property reconstruction belongs to Materials Science",
            "cellular, organismal and ecological functions belong to Biology",
            "clinical intervention and population health belong to Medicine and Health Sciences",
            "environmental fate and Earth-system chemistry belong to Earth and Environmental Sciences",
            "application systems cannot select chemical laws",
            "unobserved Smithium and endpoint claims are sealed predictions, not measured discoveries"
        ],
        "subbranch_order": list(SUBBRANCH_ORDER),
        "subbranch_counts": {name: counts[name] for name in SUBBRANCH_ORDER},
        "required_claim_count": len(OBLIGATIONS),
        "required_claim_ids": [row.claim_id for row in OBLIGATIONS],
        "admitted_claim_count_at_freeze": sum(row.claim_id in admitted for row in OBLIGATIONS),
        "unclassified_obligations": [],
        # Every current-knowledge derivational obligation is classified and
        # admitted.  These are future empirical targets for sealed standing
        # predictions, not unclosed derivations and therefore must not be
        # represented as frontier obligations at the publication gate.
        "frontier_obligations": [],
        "unobserved_prediction_targets": [
            "external observation of element 126 chemistry",
            "external observation of any generated g-block member beyond the known periodic table",
            "external observation of the proposed periodic endpoint"
        ],
        "external_source_registry_path": "experiments/external_sources/chemistry/authoritative_sources.json",
        "external_source_registry_hash": sha256_identity(external),
        "obligations": rows,
    }
    payload["inventory_hash"] = sha256_identity(payload)
    destination = ROOT / "publications/inventories/chemistry.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"frozen Chemistry inventory: {len(OBLIGATIONS)} obligations; "
        f"{payload['admitted_claim_count_at_freeze']} admitted"
    )


if __name__ == "__main__":
    main()
