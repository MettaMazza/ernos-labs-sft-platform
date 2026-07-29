#!/usr/bin/env python3
"""Select PubMed identities without abstracts, register them, then open content."""

from hashlib import sha256
import json
from pathlib import Path
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/external/medicine/placebo_nocebo_2026-07-28"
EXCLUDED = {
    "38733772", "20679593", "29755621", "11498597", "28321201", "27461877",
    "37900300", "41588673", "14508021", "25776211", "36932915", "41114660",
    "34716408", "16120776", "19888784", "31886161", "33684624", "27436632",
    "32701847", "7607192", "37043203", "7888260", "30457698", "36340278",
    "31350784", "36351953", "17108175", "42138727", "30296557", "39537677",
}
QUERIES = (
    ("objective-placebo", 'placebo[Title] AND (biomarker OR cytokine OR dopamine OR opioid OR fMRI) AND humans[MeSH Terms]'),
    ("objective-nocebo", 'nocebo[Title] AND (biomarker OR cortisol OR fMRI OR physiological) AND humans[MeSH Terms]'),
    ("bounded-null", 'placebo[Title] AND randomized controlled trial[Publication Type] AND humans[MeSH Terms]'),
)


def get(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT/3 source-custody"})
    with urlopen(request, timeout=30) as response:
        return response.read()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    selected = []
    for label, query in QUERIES:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urlencode({"db": "pubmed", "term": query, "retmode": "json", "retmax": "20", "sort": "pub date"})
        payload = json.loads(get(url))
        ids = [item for item in payload["esearchresult"]["idlist"] if item not in EXCLUDED]
        if not ids:
            raise SystemExit(f"no unexposed PubMed identity for {label}")
        selected.append({"class": label, "query": query, "pmid": ids[0]})
        time.sleep(1)
    registration = {
        "schema": "sft-v3-medicine-placebo-target-identities/1",
        "selection_rule": "Newest PubMed identity returned by each frozen query after removing every pre-seal or search-exposed PMID; identity list selected without fetching abstracts.",
        "selected": selected,
        "excluded_pmids": sorted(EXCLUDED),
        "target_content_present": False,
        "formal_predecessor_receipts": {
            "fibre": "sha256:84338832d2057f854707262e2c59af07a41c65451c3d823567596d98185ed555",
            "available_state": "sha256:183d1cc98d5d834ec6b5b44b90c76b5dfed458ed591da348166d868824e8a594",
            "record_separation": "sha256:b80dc8fea8258a86a5017270ce9fd9205354705a9ba4faa9295fd2f67929910c"
        }
    }
    registration_bytes = (json.dumps(registration, indent=2, sort_keys=True) + "\n").encode()
    (OUT / "target_identities.json").write_bytes(registration_bytes)
    documents = []
    for row in selected:
        pmid = row["pmid"]
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + urlencode({"db": "pubmed", "id": pmid, "retmode": "xml"})
        body = get(url)
        path = OUT / f"pubmed_{pmid}.xml"
        path.write_bytes(body)
        documents.append({"class": row["class"], "pmid": pmid, "snapshot_path": path.relative_to(ROOT).as_posix(), "snapshot_hash": "sha256:" + sha256(body).hexdigest(), "source_uri": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"})
        time.sleep(1)
    observations = {
        "schema": "sft-v3-medicine-placebo-source-custody/1",
        "target_identity_registration_path": (OUT / "target_identities.json").relative_to(ROOT).as_posix(),
        "target_identity_registration_hash": "sha256:" + sha256(registration_bytes).hexdigest(),
        "documents": documents,
        "all_documents_retained": True,
    }
    (OUT / "observations.json").write_text(json.dumps(observations, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(observations, indent=2))


if __name__ == "__main__": main()
