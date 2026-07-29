#!/usr/bin/env python3
"""Mark every pre-V3 Ernos Labs Zenodo version as replaced by V3.

This publication-metadata tool does not touch the SFT engine, verification
authority, claims, receipts, or scientific evidence.  It preserves every
historical DOI, concept DOI, version string, and file.  It changes only the
published title, the leading status notice in the description, and explicit
``isObsoletedBy`` relations to the appropriate V3 paper or papers.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


API = "https://zenodo.org/api"
LABEL = "[Depreciated and replaced by V3]"
V3_REPOSITORY = "https://github.com/MettaMazza/ernos-labs-sft-platform"

V3_PAPERS: dict[str, tuple[str, str]] = {
    "methods": (
        "10.5281/zenodo.21627646",
        "There Is No Nothing: A Premise-Free Operational Foundation and an Open Verification Platform for Smithian Fold Theory",
    ),
    "foundation": (
        "10.5281/zenodo.21627656",
        "From Nothing to Fold: A Premise-Free, Parameter-Free and Machine-Closed Foundation for Smithian Fold Theory",
    ),
    "mathematics": (
        "10.5281/zenodo.21627708",
        "From Fold to Mathematics: An Exact, Parameter-Free and Machine-Closed Derivation of Mathematical Foundations from Smithian Fold Theory",
    ),
    "information": (
        "10.5281/zenodo.21627717",
        "From Distinction to Information: An Exact, Parameter-Free and Machine-Closed Derivation of Information Science from Smithian Fold Theory",
    ),
    "classical_computation": (
        "10.5281/zenodo.21627721",
        "After Turing: The Fold Machine - An Exact, Parameter-Free and Machine-Closed Derivation of Classical Computational Science from Smithian Fold Theory",
    ),
    "quantum_computation": (
        "10.5281/zenodo.21627748",
        "The Quantum Fold Machine - An Exact, Parameter-Free and Machine-Closed Derivation of Reversible and Quantum Computation from Smithian Fold Theory",
    ),
    "physics": (
        "10.5281/zenodo.21627765",
        "From Fold to Physics: An Exact, Parameter-Free and Machine-Closed Reconstruction of Physical Science from Smithian Fold Theory",
    ),
    "chemistry": (
        "10.5281/zenodo.21627782",
        "From Fold to Chemistry: An Exact, Parameter-Free and Machine-Closed Reconstruction of Chemical Science from Smithian Fold Theory",
    ),
    "materials": (
        "10.5281/zenodo.21629306",
        "From Fold to Materials: An Exact, Parameter-Free and Machine-Closed Reconstruction of Materials Science from Smithian Fold Theory",
    ),
    "biology": (
        "10.5281/zenodo.21630203",
        "From Fold to Life: An Exact, Zero-Parameter and Machine-Closed Foundational Reconstruction of Biology and Life Sciences from Smithian Fold Theory",
    ),
    "medicine": (
        "10.5281/zenodo.21630785",
        "From Fold to Medicine: An Exact, Zero-Parameter and Machine-Closed Foundational Reconstruction of Medicine and Health Sciences from Smithian Fold Theory",
    ),
    "consciousness": (
        "10.5281/zenodo.21636397",
        "From Fold to Consciousness: An Exact, Zero-Parameter and Machine-Closed Foundational Reconstruction of Consciousness and Cognitive Science from Smithian Fold Theory",
    ),
    "earth": (
        "10.5281/zenodo.21640810",
        "From One World to Earth: An Exact, Zero-Parameter and Machine-Closed Foundational Reconstruction of Earth and Environmental Sciences from Smithian Fold Theory",
    ),
    "astronomy": (
        "10.5281/zenodo.21640812",
        "From One Sky to Cosmos: An Exact, Zero-Parameter and Machine-Closed Foundational Reconstruction of Astronomy and Cosmology from Smithian Fold Theory",
    ),
    "social": (
        "10.5281/zenodo.21640814",
        "From One Relation to Society: An Exact, Zero-Parameter and Machine-Closed Foundational Reconstruction of Social and Collective Sciences from Smithian Fold Theory",
    ),
    "engineering": (
        "10.5281/zenodo.21640816",
        "From One Law to a Working World: An Exact, Zero-Parameter and Machine-Closed Foundation for Engineering Translation from Smithian Fold Theory",
    ),
}

# The keys are historical Zenodo concept record IDs.  Every published version
# under these concepts receives the same categorical V3 successor routing.
LEGACY_CONCEPTS: dict[str, dict[str, Any]] = {
    "20590855": {"successors": ["classical_computation"], "kind": "application"},
    "20775538": {"successors": ["methods"], "kind": "software"},
    "21026312": {"successors": ["chemistry", "physics"], "kind": "paper"},
    "21026490": {"successors": ["mathematics", "physics"], "kind": "paper"},
    "21026617": {"successors": ["physics"], "kind": "paper"},
    "21028523": {"successors": ["quantum_computation"], "kind": "paper"},
    "21028591": {"successors": ["quantum_computation"], "kind": "paper"},
    "21028645": {"successors": ["quantum_computation"], "kind": "paper"},
    "21035460": {"successors": ["methods", "foundation"], "kind": "paper"},
    "21035786": {"successors": ["consciousness"], "kind": "paper"},
    "21035854": {"successors": ["consciousness"], "kind": "paper"},
    "21182468": {"successors": list(V3_PAPERS), "kind": "corpus"},
    "21217278": {"successors": ["classical_computation", "consciousness"], "kind": "application"},
    "21276950": {"successors": ["biology"], "kind": "application"},
    "21278563": {"successors": ["classical_computation"], "kind": "application"},
    "21279102": {"successors": ["physics"], "kind": "paper"},
    "21279104": {"successors": ["physics", "astronomy"], "kind": "paper"},
    "21279106": {"successors": ["physics", "earth"], "kind": "paper"},
    "21283968": {"successors": ["classical_computation"], "kind": "application"},
    "21284529": {"successors": ["methods"], "kind": "paper"},
    "21368944": {"successors": ["biology"], "kind": "application"},
    "21396742": {"successors": ["information", "classical_computation"], "kind": "application"},
    "21482127": {"successors": ["biology"], "kind": "application"},
    "21512798": {"successors": ["classical_computation", "quantum_computation"], "kind": "paper"},
}

V3_CONCEPTS = {
    "21514889", "21515628", "21516145", "21516915", "21518310",
    "21518312", "21520880", "21531454", "21532481", "21630202",
    "21630784", "21636396", "21640809", "21640811", "21640813",
    "21640815",
}


def request_json(
    url: str,
    *,
    token: str | None = None,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=90) as response:
        body = response.read()
    return json.loads(body) if body else {}


def public_catalogue() -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    page = 1
    while True:
        query = urllib.parse.urlencode(
            {
                "q": 'creators.affiliation:"Ernos Labs"',
                "size": 25,
                "page": page,
                "allversions": "true",
            }
        )
        response = request_json(f"{API}/records?{query}")
        batch = response["hits"]["hits"]
        hits.extend(batch)
        if len(batch) < 25:
            break
        page += 1
    # Zenodo's relevance ordering can shift while records are being edited.
    # De-duplicate pages by immutable record ID before any write is attempted.
    return list({str(record["id"]): record for record in hits}.values())


def notice(successor_keys: list[str], kind: str) -> str:
    links = []
    for key in successor_keys:
        doi, title = V3_PAPERS[key]
        links.append(f'<a href="https://doi.org/{doi}"><em>{title}</em></a>')
    routed = "; ".join(links)
    if kind == "application":
        scope = (
            "The application-specific clean rebuild has not yet been published; "
            "its authoritative theoretical boundary is now the governing V3 branch"
        )
    elif kind == "software":
        scope = "The former software archive is replaced by the V3 open-science platform and Methods paper"
    elif kind == "corpus":
        scope = "The former monolithic corpus is replaced by the complete V3 branch-paper series"
    else:
        scope = "This pre-V3 paper is replaced by the corresponding V3 clean-room reconstruction"
    return (
        f"<p><strong>{LABEL}</strong> {scope}: {routed}. "
        f'The V3 source platform is <a href="{V3_REPOSITORY}">{V3_REPOSITORY}</a>. '
        "The original DOI, concept DOI, version number and files are preserved for "
        "transparent historical provenance; this record must not be presented or "
        "cited as current V3 work.</p>"
    )


def mark_record(record: dict[str, Any], token: str, execute: bool) -> str:
    record_id = str(record["id"])
    concept_id = str(record["conceptrecid"])
    route = LEGACY_CONCEPTS[concept_id]
    public_metadata = record["metadata"]
    old_title = public_metadata.get("title", "")
    if old_title.startswith(LABEL):
        return "already_marked"
    if not execute:
        return "would_mark"

    url = f"{API}/deposit/depositions/{record_id}"
    deposit = request_json(url, token=token)
    if deposit.get("state") == "done":
        request_json(deposit["links"]["edit"], token=token, method="POST")
        deposit = request_json(url, token=token)
    metadata = deposit["metadata"]
    original_title = metadata["title"]
    metadata["title"] = f"{LABEL} {original_title}"
    prefix = notice(route["successors"], route["kind"])
    if not str(metadata.get("description", "")).startswith(
        f"<p><strong>{LABEL}</strong>"
    ):
        metadata["description"] = prefix + str(metadata.get("description", ""))
    relations = metadata.setdefault("related_identifiers", [])
    for successor_key in route["successors"]:
        doi, _ = V3_PAPERS[successor_key]
        relation = {"identifier": doi, "relation": "isObsoletedBy", "scheme": "doi"}
        if relation not in relations:
            relations.append(relation)
    request_json(url, token=token, method="PUT", payload={"metadata": metadata})
    request_json(deposit["links"]["publish"], token=token, method="POST")

    public = request_json(f"{API}/records/{record_id}")
    if not public["metadata"]["title"].startswith(LABEL):
        raise RuntimeError(f"public title verification failed for {record_id}")
    if public["metadata"].get("version") != public_metadata.get("version"):
        raise RuntimeError(f"version changed unexpectedly for {record_id}")
    return "marked"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--concept", action="append", default=[])
    parser.add_argument("--token-file", default="~/.zenodo_token")
    args = parser.parse_args()

    requested = set(args.concept) if args.concept else set(LEGACY_CONCEPTS)
    unknown = requested - set(LEGACY_CONCEPTS)
    if unknown:
        raise SystemExit(f"unknown legacy concept IDs: {sorted(unknown)}")
    token = ""
    if args.execute:
        token = Path(args.token_file).expanduser().read_text(encoding="utf-8").strip()
        if not token:
            raise SystemExit("empty Zenodo token")

    records = public_catalogue()
    concepts = {str(record["conceptrecid"]) for record in records}
    unexpected = concepts - set(LEGACY_CONCEPTS) - V3_CONCEPTS
    if unexpected:
        raise SystemExit(f"unclassified Ernos Labs Zenodo concepts: {sorted(unexpected)}")

    targets = [
        record
        for record in records
        if str(record["conceptrecid"]) in requested
    ]
    counts: dict[str, int] = {}
    for record in sorted(targets, key=lambda item: int(item["id"])):
        status = mark_record(record, token, args.execute)
        counts[status] = counts.get(status, 0) + 1
        print(
            f"{record['id']}\t{record['conceptrecid']}\t"
            f"{record['metadata'].get('version', '')}\t{status}"
        )
    print(json.dumps({"target_records": len(targets), "statuses": counts}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
