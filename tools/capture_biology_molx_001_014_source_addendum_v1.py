#!/usr/bin/env python3
"""Capture registered MOLX source identities not resolved by the first pass."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/external_sources/biology/molx_001_014_v1"
SNAPSHOTS = BASE / "snapshots_addendum_v1"
OUT = BASE / "source_custody_addendum_v1.json"
BASE_MANIFEST = "sha256:e0f2a91e9dadc4783e243a05ee5d8e3978af092a17e83cd31d7b8ad73b239d11"
FORMAL_SEAL = "sha256:662421bd75301c6511aa0889c27a5b254967528392b3f82e12607bf8e36953ee"
USER_AGENT = "ErnosLabs-SFT/3.0 (Maria.Smith.Sftoe@gmail.com)"

SOURCES = (
    ("UNIPROT-P0C512-REVIEWED-CARBON-FIXATION", "uniprot_p0c512.tsv", "https://rest.uniprot.org/uniprotkb/search?query=%28accession%3AP0C512%29+AND+%28reviewed%3Atrue%29&fields=accession,id,protein_name,cc_function,cc_catalytic_activity,rhea&format=tsv&size=5"),
    ("UNIPROT-REVIEWED-GLYCOGEN-SYNTHASE", "uniprot_glycogen_synthase.tsv", "https://rest.uniprot.org/uniprotkb/search?query=%28ec%3A2.4.1.11%29+AND+%28reviewed%3Atrue%29&fields=accession,id,protein_name,cc_catalytic_activity,rhea&format=tsv&size=5"),
    ("RCSB-PDB-6CP6-ATP-SYNTHASE", "rcsb_pdb_6cp6.json", "https://data.rcsb.org/rest/v1/core/entry/6CP6"),
    ("RHEA-NITROGEN-GLUTAMINE-SYNTHETASE", "rhea_ec_6_3_1_2.tsv", "https://www.rhea-db.org/rhea/?query=ec%3A6.3.1.2&columns=rhea-id,equation,chebi-id,ec,uniprot,pubmed&format=tsv&limit=10"),
    ("RHEA-SULFUR-APS-REDUCTASE", "rhea_ec_1_8_99_2.tsv", "https://www.rhea-db.org/rhea/?query=ec%3A1.8.99.2&columns=rhea-id,equation,chebi-id,ec,uniprot,pubmed&format=tsv&limit=10"),
    ("METABOLIGHTS-MTBLS1275-INDEX", "metabolights_mtbls1275_index.html", "https://ftp.ebi.ac.uk/pub/databases/metabolights/studies/public/MTBLS1275/"),
    ("METABOLIGHTS-MTBLS1275-INVESTIGATION", "metabolights_mtbls1275_investigation.txt", "https://ftp.ebi.ac.uk/pub/databases/metabolights/studies/public/MTBLS1275/i_Investigation.txt"),
    ("METABOLIGHTS-MTBLS1275-MAF-1", "metabolights_mtbls1275_maf_1.tsv", "https://ftp.ebi.ac.uk/pub/databases/metabolights/studies/public/MTBLS1275/m_MTBLS1275_LC-MS_negative_hilic_metabolite_profiling-1_v2_maf.tsv"),
)


def canonical(value: object) -> str:
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_hash(path: Path) -> str:
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing to overwrite MOLX source addendum")
    base_manifest = json.loads((BASE / "source_custody_manifest.json").read_text())
    formal = json.loads((ROOT / "census/biology_molx_001_014_formal_prediction_seal_v1.json").read_text())
    if base_manifest["manifest_identity"] != BASE_MANIFEST or formal["formal_prediction_seal_identity"] != FORMAL_SEAL:
        raise SystemExit("MOLX sealed custody changed")
    SNAPSHOTS.mkdir(parents=True, exist_ok=False)
    rows = []
    for source_id, filename, url in SOURCES:
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
        with urlopen(request, timeout=45) as response:
            data = response.read()
            content_type = response.headers.get_content_type()
            status = response.status
        path = SNAPSHOTS / filename
        path.write_bytes(data)
        rows.append({
            "source_id": source_id,
            "requested_url": url,
            "status": f"http_{status}",
            "content_type": content_type,
            "snapshot_path": str(path.relative_to(ROOT)),
            "snapshot_hash": file_hash(path),
            "byte_count": len(data),
        })
        print(source_id, status, len(data), flush=True)
    payload = {
        "schema": "sft-v3-biology-molx-source-custody-addendum/1",
        "authority": "Maria Smith",
        "date": "2026-07-29",
        "family": "living_biochemistry_and_molecular_processes",
        "base_source_manifest_identity": BASE_MANIFEST,
        "formal_prediction_seal_identity": FORMAL_SEAL,
        "document_count": len(rows),
        "documents": rows,
        "all_registered_addendum_routes_preserved": True,
    }
    payload["addendum_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"document_count": len(rows), "addendum_identity": payload["addendum_identity"]}, indent=2))


if __name__ == "__main__":
    main()
