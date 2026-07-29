#!/usr/bin/env python3
"""Capture the post-seal authoritative source surface for Biology MOLX."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/external_sources/biology/molx_001_014_v1"
SNAPSHOTS = OUT / "snapshots"
MANIFEST = OUT / "source_custody_manifest.json"
FORMAL_SEAL = "sha256:662421bd75301c6511aa0889c27a5b254967528392b3f82e12607bf8e36953ee"
REGISTRY = "sha256:ae8d5c4e9d47270d7dd795a4ac34e1bc916a712622d90ed6ccfaaa1bd33b5733"
USER_AGENT = "ErnosLabs-SFT/3.0 (Maria.Smith.Sftoe@gmail.com)"

SOURCES = (
    ("RHEA-REST-API", "rhea_rest_api.html", "https://www.rhea-db.org/help/rest-api"),
    ("RHEA-REACTION-SIDES-DIRECTION", "rhea_reaction_sides_direction.html", "https://www.rhea-db.org/help/reaction-side-direction"),
    ("RHEA-RELEASE-STATISTICS", "rhea_statistics.html", "https://www.rhea-db.org/statistics"),
    ("RHEA-REDOX-10020", "rhea_10020.tsv", "https://www.rhea-db.org/rhea/?query=rhea%3A10020&columns=rhea-id,equation,chebi-id,ec,uniprot,pubmed&format=tsv&limit=10"),
    ("RHEA-ATP-TRANSPORT-57720", "rhea_57720.tsv", "https://www.rhea-db.org/rhea/?query=rhea%3A57720&columns=rhea-id,equation,chebi-id,ec,uniprot,pubmed&format=tsv&limit=10"),
    ("RHEA-CARBON-FIXATION-23124", "rhea_23124.tsv", "https://www.rhea-db.org/rhea/?query=rhea%3A23124&columns=rhea-id,equation,chebi-id,ec,uniprot,pubmed&format=tsv&limit=10"),
    ("RHEA-GLYCOGEN-SYNTHASE-18549", "rhea_18549.tsv", "https://www.rhea-db.org/rhea/?query=rhea%3A18549&columns=rhea-id,equation,chebi-id,ec,uniprot,pubmed&format=tsv&limit=10"),
    ("RHEA-ASPARTATE-AMINOTRANSFERASE-21824", "rhea_21824.tsv", "https://www.rhea-db.org/rhea/?query=rhea%3A21824&columns=rhea-id,equation,chebi-id,ec,uniprot,pubmed&format=tsv&limit=10"),
    ("RHEA-PHOSPHOLIPID-QUERY", "rhea_phospholipid.tsv", "https://www.rhea-db.org/rhea/?query=phospholipid&columns=rhea-id,equation,chebi-id,ec,uniprot,pubmed&format=tsv&limit=10"),
    ("UNIPROT-P00509-REVIEWED-ENZYME", "uniprot_p00509.tsv", "https://rest.uniprot.org/uniprotkb/search?query=%28accession%3AP00509%29+AND+%28reviewed%3Atrue%29&fields=accession,id,protein_name,cc_catalytic_activity,cc_cofactor,rhea&format=tsv&size=5"),
    ("UNIPROT-P69448-REVIEWED-ATP-SYNTHASE", "uniprot_p69448.json", "https://rest.uniprot.org/uniprotkb/P69448.json"),
    ("PMC6713963-PRIMARY-ENZYME-KINETICS", "pmc6713963.xml", "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/PMC6713963/unicode"),
    ("SABIO-RK-REST-MANUAL", "sabio_rk_rest_manual.html", "https://sabiork.h-its.org/sabioRestWebServices"),
    ("MW-ST004494-CARBON-FLUX-STUDY", "mw_st004494.html", "https://www.metabolomicsworkbench.org/data/DRCCMetadata.php?Mode=Study&ResultType=1&StudyID=ST004494&StudyType=MS"),
    ("MW-REST-API-SPECIFICATION", "mw_rest_api_v1.pdf", "https://www.metabolomicsworkbench.org/tools/MWRestAPIv1.0.pdf"),
    ("QUICKGO-NITROGEN-PROCESS", "quickgo_go_0006807.json", "https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0006807"),
    ("QUICKGO-SULFUR-PROCESS", "quickgo_go_0006790.json", "https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0006790"),
    ("QUICKGO-PHOSPHORUS-PROCESS", "quickgo_go_0006793.json", "https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0006793"),
    ("QUICKGO-LIPID-PROCESS", "quickgo_go_0006629.json", "https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0006629"),
    ("QUICKGO-COFACTOR-PROCESS", "quickgo_go_0051186.json", "https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0051186"),
    ("LIPID-MAPS-LMSD-OVERVIEW", "lipid_maps_lmsd_overview.html", "https://www.lipidmaps.org/databases/lmsd/overview"),
    ("METABOLIGHTS-OPEN-REPOSITORY", "metabolights_home.html", "https://www.ebi.ac.uk/metabolights/"),
    ("METABOLIGHTS-DOWNLOAD-CUSTODY", "metabolights_download.html", "https://www.ebi.ac.uk/metabolights/download"),
)


def canonical(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + sha256(raw).hexdigest()


def file_hash(path: Path) -> str:
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if MANIFEST.exists():
        raise SystemExit("refusing to overwrite Biology MOLX source custody")
    seal = json.loads((ROOT / "census/biology_molx_001_014_formal_prediction_seal_v1.json").read_text())
    if seal["formal_prediction_seal_identity"] != FORMAL_SEAL or seal["target_registry_identity"] != REGISTRY:
        raise SystemExit("Biology MOLX formal prediction seal changed")
    SNAPSHOTS.mkdir(parents=True, exist_ok=False)
    documents = []
    for source_id, filename, url in SOURCES:
        destination = SNAPSHOTS / filename
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
        status = "unavailable"
        content_type = "unavailable"
        error = None
        data = b""
        try:
            with urlopen(request, timeout=45) as response:
                data = response.read()
                status = f"http_{response.status}"
                content_type = response.headers.get_content_type()
        except (HTTPError, URLError, TimeoutError) as exc:
            error = f"{type(exc).__name__}: {exc}"
        if data:
            destination.write_bytes(data)
            snapshot_path = str(destination.relative_to(ROOT))
            snapshot_hash = file_hash(destination)
            byte_count: int | str = len(data)
        else:
            snapshot_path = "structural-absence"
            snapshot_hash = "structural-absence"
            byte_count = "structural-absence"
        documents.append(
            {
                "source_id": source_id,
                "requested_url": url,
                "status": status,
                "content_type": content_type,
                "snapshot_path": snapshot_path,
                "snapshot_hash": snapshot_hash,
                "byte_count": byte_count,
                "error": error or "structural-absence",
            }
        )
        print(source_id, status, byte_count, flush=True)
    payload = {
        "schema": "sft-v3-biology-molx-source-custody/1",
        "authority": "Maria Smith",
        "date": "2026-07-29",
        "family": "living_biochemistry_and_molecular_processes",
        "target_registry_identity": REGISTRY,
        "formal_prediction_seal_identity": FORMAL_SEAL,
        "selection_occurred_after_formal_seal": True,
        "document_count": len(documents),
        "available_document_count": sum(row["status"] == "http_200" for row in documents),
        "unavailable_document_count": sum(row["status"] != "http_200" for row in documents),
        "documents": documents,
        "all_source_routes_preserved": True,
    }
    payload["manifest_identity"] = canonical(payload)
    OUT.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: payload[key] for key in ("document_count", "available_document_count", "unavailable_document_count", "manifest_identity")}, indent=2))


if __name__ == "__main__":
    main()
