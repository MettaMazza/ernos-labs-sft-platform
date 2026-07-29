#!/usr/bin/env python3
"""Capture the frozen ORG-012 distinct-route primary-source surfaces."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
IDENTITY = (
    ROOT
    / "experiments/external_sources/chemistry"
    / "org_012_missing_measurement_source_identity_addendum_v3.json"
)
SNAPSHOT = (
    ROOT
    / "experiments/external_sources/chemistry/snapshots"
    / "org-012-missing-measurement-repair-v3"
)

SOURCES = (
    (
        "ordinal-006-breslow-guo-1988.pdf",
        "https://file1.lookchem.com/doi/2021/12/21/ab0579d7-0849-4351-a370-725998b57cbe.pdf",
        "application/pdf",
    ),
    (
        "ordinal-019-us4588591a.html",
        "https://patents.google.com/patent/US4588591A/en",
        "text/html",
    ),
    (
        "ordinal-027-henry-charlton-1973-epa-index.html",
        "https://hero.epa.gov/reference/7620907/",
        "text/html",
    ),
    (
        "ordinal-027-henry-charlton-1973-crossref.json",
        "https://api.crossref.org/works/10.1021/ja00790a006",
        "application/json",
    ),
    (
        "ordinal-027-agagnier-1973-thesis.pdf",
        "https://www.collectionscanada.gc.ca/obj/thesescanada/vol2/MWU/TC-MWU-13112.pdf",
        "application/pdf",
    ),
    (
        "ordinal-030-wipke-goeke-1974-crossref.json",
        "https://api.crossref.org/works/10.1021/ja00820a030",
        "application/json",
    ),
    (
        "ordinal-030-us20090054714a1.html",
        "https://patents.google.com/patent/US20090054714A1/en",
        "text/html",
    ),
)


def digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def fetch(uri: str) -> tuple[bytes, str]:
    request = urllib.request.Request(
        uri,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36 Ernos-Labs-SFT-v3-source-capture/1.0",
            "Accept": "*/*",
            "Referer": "https://www.google.com/",
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read(), response.headers.get_content_type()


def main() -> int:
    identity_payload = IDENTITY.read_bytes()
    registration = json.loads(identity_payload)
    if registration["status"] != "identity-exposed-distinct-route-registered-before-version-three-reconstruction":
        raise ValueError("ORG-012 repair registration status changed")

    SNAPSHOT.mkdir(parents=True, exist_ok=True)
    artifacts = []
    transport_artifacts = []
    for filename, uri, expected_type in SOURCES:
        path = SNAPSHOT / filename
        if path.exists():
            payload = path.read_bytes()
            reported_type = "preserved-first-successful-capture"
        else:
            payload, reported_type = fetch(uri)
        if not payload:
            raise ValueError(f"empty source payload: {uri}")
        if expected_type == "application/pdf" and not payload.startswith(b"%PDF"):
            pdf_start = payload.find(b"%PDF")
            if pdf_start < 1:
                raise ValueError(f"expected PDF source but received another representation: {uri}")
            envelope_path = SNAPSHOT / f"{filename}.transport-envelope"
            if not envelope_path.exists():
                envelope_path.write_bytes(payload)
            transport_artifacts.append(
                {
                    "filename": envelope_path.name,
                    "uri": uri,
                    "byte_count": len(payload),
                    "sha256": digest(payload),
                    "status": "source-returned-HTTP-envelope-preserved-before-PDF-boundary",
                    "pdf_boundary_byte_offset": pdf_start,
                }
            )
            payload = payload[pdf_start:]
            reported_type = f"{reported_type}; embedded-PDF-boundary-reconstructed"
        if not path.exists():
            path.write_bytes(payload)
        artifacts.append(
            {
                "filename": filename,
                "uri": uri,
                "expected_content_type": expected_type,
                "reported_content_type": reported_type,
                "byte_count": len(payload),
                "sha256": digest(payload),
            }
        )

    manifest = {
        "schema": "sft-v3-chemistry-org-012-missing-measurement-source-capture/3",
        "identity_path": str(IDENTITY.relative_to(ROOT)),
        "identity_sha256": digest(identity_payload),
        "blind_source_claim": False,
        "outcome_exposure_disclosed": True,
        "all_registered_sources_captured": len(artifacts) == len(SOURCES),
        "artifacts": artifacts,
        "transport_artifacts": transport_artifacts,
    }
    manifest_payload = json.dumps(manifest, indent=2, sort_keys=True).encode() + b"\n"
    (SNAPSHOT / "source-manifest-v3.json").write_bytes(manifest_payload)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
