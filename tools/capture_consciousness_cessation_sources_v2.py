#!/usr/bin/env python3
"""Identity-first cessation retry after preserving the non-purpose-matched first batch."""

from hashlib import sha256
import json
from pathlib import Path
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/external/consciousness/nonordinary_2026-07-28_retry_1"
EXCLUDED = ("42342408", "42310452", "42229499", "42213325", "41985771")
SELECTED = (
    ("brain-death-integrated-function", "42425288", '"brain death"[Title] integrated function'),
    ("brain-death-integrated-function", "41559743", '"brain death"[Title] integrated function'),
    ("brain-death-cellular-boundary", "41878502", '"brain death"[Title] cellular viability'),
    ("brain-death-cellular-boundary", "41401968", '"brain death"[Title] cellular viability'),
    ("neurologic-death-review", "42135815", '"death by neurologic criteria"[Title] review'),
    ("somatic-integration-control", "31696418", '"brain death"[Title] somatic integration'),
)


def get(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT/3 source-custody"})
    with urlopen(request, timeout=30) as response:
        return response.read()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    selected = tuple({"class": family, "pmid": pmid, "identity_query": query} for family, pmid, query in SELECTED)
    registration = {
        "schema": "sft-v3-consciousness-cessation-target-identities/1",
        "selection_rule": "All identities returned by frozen ID-only title-qualified PubMed searches were registered before fetching content; the complete unsuitable first batch remains preserved as non-purpose-matched evidence.",
        "selected": selected,
        "excluded_first_batch_pmids": EXCLUDED,
        "target_content_present": False,
        "formal_predecessor_receipt": "sha256:8662c2274a82541f6c313b81263e388801e591ebc72ff93bc0bdf511fe15c2d7",
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
        time.sleep(0.4)
    observations = {
        "schema": "sft-v3-consciousness-cessation-source-custody/1",
        "target_identity_registration_path": (OUT / "target_identities.json").relative_to(ROOT).as_posix(),
        "target_identity_registration_hash": "sha256:" + sha256(registration_bytes).hexdigest(),
        "documents": documents,
        "all_documents_retained": True,
    }
    (OUT / "observations.json").write_text(json.dumps(observations, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"registered": len(selected), "captured": len(documents), "identity_hash": observations["target_identity_registration_hash"]}, indent=2))


if __name__ == "__main__":
    main()
