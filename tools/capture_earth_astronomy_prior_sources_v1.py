#!/usr/bin/env python3
"""Identity-first OpenAlex capture for the Earth/Astronomy prior-return family."""

from hashlib import sha256
import json
from pathlib import Path
import time
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/external/astronomy/prior_return_2026-07-28"
QUERIES = (
    ("earth-tipping", "Earth system tipping points bistability hysteresis observations"),
    ("solar-radio-release", "solar flare magnitude frequency power law exponent"),
    ("fast-radio-burst", "fast radio burst energy distribution power law"),
    ("planetary-spacing", "Titius Bode planetary spacing exoplanet systems test"),
    ("lithium-seven", "cosmological lithium problem stellar depletion lithium-7 abundance"),
)


def get(url):
    req = Request(url, headers={"User-Agent": "Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"})
    with urlopen(req, timeout=40) as r:
        return r.read()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    selected = []
    for family, query in QUERIES:
        url = "https://api.openalex.org/works?" + urlencode({"search": query, "per-page": "5", "select": "id,doi,title,publication_year"})
        data = json.loads(get(url))
        for row in data["results"]:
            selected.append({"class": family, "query": query, "openalex_id": row["id"].rsplit("/", 1)[-1], "doi": row.get("doi"), "title": row.get("title"), "publication_year": row.get("publication_year")})
        time.sleep(0.3)
    registration = {
        "schema": "sft-v3-earth-astronomy-prior-target-identities/1",
        "selection_rule": "All five identity-only query result sets were registered before any full work record or abstract was fetched; all selected identities are retained regardless of relevance or outcome.",
        "selected": selected,
        "target_content_present": False,
        "formal_predecessor_receipts": {
            "tipping": "sha256:3a8ebb9a7cc49c18c5615b8744e02128bcd6414c2300362b1f8458e2b78eec9a",
            "unit_release": "sha256:edf91022ff2d28e6865c002825eb0e508f2215b912e2bd66b5b161cbe0272958",
            "atomic_burst": "sha256:caedea69c14b9220fea53c58cefabbac44224e2dbceb634737c9cb072b521b66",
            "planetary_ladder": "sha256:316542613f55d9f07e05141976cc889c47c787a61886f0aee26f6612db844a4e",
            "lithium": "sha256:f295654ffdde16ad962d59c6af7ed9808f82b902a78f1c55785e01acea42ccb4"
        }
    }
    reg_bytes = (json.dumps(registration, indent=2, sort_keys=True) + "\n").encode(); (OUT / "target_identities.json").write_bytes(reg_bytes)
    documents = []
    for row in selected:
        body = get("https://api.openalex.org/works/" + quote(row["openalex_id"]))
        path = OUT / ("openalex_" + row["openalex_id"] + ".json"); path.write_bytes(body)
        documents.append({"class": row["class"], "openalex_id": row["openalex_id"], "snapshot_path": path.relative_to(ROOT).as_posix(), "snapshot_hash": "sha256:" + sha256(body).hexdigest(), "source_uri": "https://openalex.org/" + row["openalex_id"]})
        time.sleep(0.2)
    observations = {"schema": "sft-v3-earth-astronomy-prior-source-custody/1", "target_identity_registration_path": (OUT / "target_identities.json").relative_to(ROOT).as_posix(), "target_identity_registration_hash": "sha256:" + sha256(reg_bytes).hexdigest(), "documents": documents, "all_documents_retained": True}
    (OUT / "observations.json").write_text(json.dumps(observations, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"registered": len(selected), "captured": len(documents), "identity_hash": observations["target_identity_registration_hash"]}, indent=2))


if __name__ == "__main__": main()
