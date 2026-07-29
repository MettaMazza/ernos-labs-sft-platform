#!/usr/bin/env python3
"""Register PubMed identities without abstracts, then capture all selected content."""

from hashlib import sha256
import json
from pathlib import Path
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/external/consciousness/nonordinary_2026-07-28"
SELECTED = (
    ("synaesthesia", "39922140", "synaesthesia consistency inducer concurrent"),
    ("synaesthesia", "36707026", "synaesthesia consistency inducer concurrent"),
    ("synaesthesia", "34551015", "synaesthesia consistency inducer concurrent"),
    ("synaesthesia", "31630652", "synaesthesia consistency inducer concurrent"),
    ("synaesthesia-control", "42168874", "synesthesia grapheme color consistency"),
    ("nonordinary", "42475469", "altered states consciousness multidimensional experience neural"),
    ("nonordinary", "42030660", "altered states consciousness multidimensional experience neural"),
    ("nonordinary", "41451954", "altered states consciousness multidimensional experience neural"),
    ("nonordinary", "39191666", "altered states consciousness multidimensional experience neural"),
    ("nonordinary", "34646576", "altered states consciousness multidimensional experience neural"),
    ("nonordinary-control", "30245648", "altered states consciousness multidimensional experience neural"),
    ("sleep-cycle", "40128477", "sleep architecture NREM REM cycling human review"),
    ("sleep-cycle", "39400423", "sleep architecture NREM REM cycling human review"),
    ("sleep-cycle", "39280264", "ultradian sleep cycle REM NREM duration"),
    ("sleep-cycle", "38390949", "ultradian sleep cycle REM NREM duration"),
    ("sleep-dream-control", "37972882", "dreaming REM NREM consciousness review"),
    ("cessation", "42342408", "brain death integrated function cellular persistence"),
    ("cessation", "42310452", "brain death integrated function cellular persistence"),
    ("cessation", "42229499", "brain death integrated function cellular persistence"),
    ("cessation", "42213325", "brain death integrated function cellular persistence"),
    ("cessation-control", "41985771", "brain death integrated function cellular persistence"),
)


def get(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT/3 source-custody"})
    with urlopen(request, timeout=30) as response:
        return response.read()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    selected = tuple({"class": family, "pmid": pmid, "identity_query": query} for family, pmid, query in SELECTED)
    registration = {
        "schema": "sft-v3-consciousness-nonordinary-target-identities/1",
        "selection_rule": "All identities returned by the frozen ID-only PubMed searches are registered before any abstract or article content is fetched; no content-dependent survivor selection is permitted.",
        "selected": selected,
        "target_content_present": False,
        "formal_predecessor_receipts": {
            "directional_synaesthesia": "sha256:827a629893b47f98576e3dac63d66528a3838db90389f274c042fe9ed186a01d",
            "three_quality_nonordinary": "sha256:8ccf5643bbf358627986218d2b9291cd2ddde37f6ec2cc938bde54fe85c72aa7",
            "sleep_dream": "sha256:96e900518c135df090379516e5793e174c96a8fab7e59d6030254c965fbe1f51",
            "cessation": "sha256:8662c2274a82541f6c313b81263e388801e591ebc72ff93bc0bdf511fe15c2d7"
        },
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
        "schema": "sft-v3-consciousness-nonordinary-source-custody/1",
        "target_identity_registration_path": (OUT / "target_identities.json").relative_to(ROOT).as_posix(),
        "target_identity_registration_hash": "sha256:" + sha256(registration_bytes).hexdigest(),
        "documents": documents,
        "all_documents_retained": True,
    }
    (OUT / "observations.json").write_text(json.dumps(observations, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"registered": len(selected), "captured": len(documents), "identity_hash": observations["target_identity_registration_hash"]}, indent=2))


if __name__ == "__main__":
    main()
