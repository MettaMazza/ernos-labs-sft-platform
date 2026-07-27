#!/usr/bin/env python3
"""Capture every registered ORG-006 v2 provider and SI route after value sealing."""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402

SOURCE_ADDENDUM = ROOT / "experiments/external_sources/chemistry/org_006_value_blind_source_identity_addendum_v2.json"
SOURCE_ADDENDUM_HASH = "sha256:5e53e3d3278b4ae93e6f2ca3e30459ff5afd5c85e99bdd3dd13d4867e93af8c3"
TARGET_ADDENDUM = ROOT / "experiments/external_sources/chemistry/org_006_target_identity_addendum_v2.json"
TARGET_ADDENDUM_HASH = "sha256:57d621771714955e5ba9b161526aecf9df27dc2b1ad1a3eedad8f6148d590a80"
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_006_conformer_population_ordering_pre_source_v2.json"
PREDICTION_FILE_HASH = "sha256:75f66cb389e8ff9e1e7007046e3b8bd4125bd2c2af5a9bfc8a6ff56ca0c446db"
PREDICTION_PAYLOAD_HASH = "sha256:b97bb9ba2150c46cb028632f6e5fac5031b54c194b9e3ce09e27d9d4177c0edf"
V1_INVENTORY = ROOT / "experiments/external_sources/chemistry/snapshots/org-006-blind-v1/source-inventory-v1.json"
V1_INVENTORY_HASH = "sha256:6b3fbef19c0bdf233691edcb5cf74856626d273338910ec76becbe313d1f6c31"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-006-value-blind-v2"
INVENTORY = OUTPUT / "source-inventory-v2.json"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "a" and self._href is not None:
            self.links.append((self._href, re.sub(r"\s+", " ", " ".join(self._text)).strip()))
            self._href = None
            self._text = []


def fetch(uri: str) -> tuple[bytes, int | None, str, str]:
    request = Request(uri, headers={"User-Agent": "Ernos-Labs-SFT-v3-source-capture/1.0"})
    try:
        with urlopen(request, timeout=60) as response:
            return response.read(), getattr(response, "status", None), response.geturl(), response.headers.get("Content-Type", "")
    except Exception as exc:
        return str(exc).encode("utf-8", errors="replace"), None, uri, "capture-error-text/plain"


def save(path: Path, payload: bytes, uri: str, status: int | None, final_uri: str, content_type: str) -> dict:
    path.write_bytes(payload)
    return {
        "requested_uri": uri,
        "http_status": status,
        "final_uri": final_uri,
        "content_type": content_type,
        "capture_status": "captured_complete_response" if status is not None else "capture_error_preserved",
        "snapshot_path": str(path.relative_to(ROOT)),
        "snapshot_sha256": hash_file(path),
        "snapshot_bytes": path.stat().st_size,
    }


def selected_links(group_id: str, base_uri: str, payload: bytes, content_type: str) -> list[str]:
    if "html" not in content_type.casefold():
        return []
    parser = LinkParser()
    parser.feed(payload.decode("utf-8", errors="replace"))
    selected = []
    for href, text in parser.links:
        uri = urljoin(base_uri, href)
        host = urlparse(uri).netloc.casefold()
        combined = (uri + " " + text).casefold()
        if group_id.startswith("PUBMED"):
            if host.endswith("nih.gov") and "pubmed.ncbi.nlm.nih.gov" not in host:
                selected.append(uri)
            elif any(token in host for token in ("aip.org", "silverchair", "core.ac.uk")) or "doi.org/10.1063/1.4904822" in combined:
                selected.append(uri)
        else:
            if any(token in combined for token in ("jp404315t_si_001", "supplement", "suppinfo", "figshare", "supporting information")):
                selected.append(uri)
    return list(dict.fromkeys(selected))


def main() -> None:
    if OUTPUT.exists() or INVENTORY.exists():
        raise SystemExit("ORG-006 v2 capture already exists; preserved without recapture")
    if (
        hash_file(SOURCE_ADDENDUM) != SOURCE_ADDENDUM_HASH
        or hash_file(TARGET_ADDENDUM) != TARGET_ADDENDUM_HASH
        or hash_file(PREDICTION) != PREDICTION_FILE_HASH
        or hash_file(V1_INVENTORY) != V1_INVENTORY_HASH
    ):
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 v2 sealed identity or predecessor evidence changed")
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    claimed = prediction.pop("sealed_payload_hash", None)
    if claimed != PREDICTION_PAYLOAD_HASH or sha256_identity(prediction) != PREDICTION_PAYLOAD_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 v2 value seal changed")
    registry = json.loads(SOURCE_ADDENDUM.read_text(encoding="utf-8"))
    groups = registry.get("source_groups", [])
    if len(groups) != 2 or registry.get("exact_values_data_rows_attachment_contents_provider_outcomes_or_payload_hashes_present") is not False:
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 v2 identity group changed")
    OUTPUT.mkdir(parents=True, exist_ok=False)
    rows = []
    for group_ordinal, group in enumerate(groups, 1):
        payload, status, final_uri, content_type = fetch(group["uri"])
        base_name = "pubmed-25591384" if group_ordinal == 1 else "acs-jp404315t"
        primary = save(OUTPUT / f"{base_name}-primary.html", payload, group["uri"], status, final_uri, content_type)
        links = selected_links(group["source_group_id"], final_uri, payload, content_type)
        linked = []
        for link_ordinal, uri in enumerate(links, 1):
            linked_payload, linked_status, linked_final, linked_type = fetch(uri)
            extension = ".pdf" if linked_payload.startswith(b"%PDF") else ".txt" if "text/plain" in linked_type.casefold() else ".bin"
            linked.append(save(OUTPUT / f"{base_name}-linked-{link_ordinal:02d}{extension}", linked_payload, uri, linked_status, linked_final, linked_type))
        rows.append({
            **group,
            "primary_capture": primary,
            "complete_selected_link_count": len(links),
            "complete_selected_links": links,
            "complete_linked_captures": linked,
            "all_selected_links_captured_without_stopping_on_success": len(linked) == len(links),
        })
    inventory = {
        "schema": "sft-v3-complete-source-group-capture-inventory/2",
        "claim_id": registry["claim_id"],
        "source_identity_registry": (str(SOURCE_ADDENDUM.relative_to(ROOT)), SOURCE_ADDENDUM_HASH),
        "target_identity_addendum": (str(TARGET_ADDENDUM.relative_to(ROOT)), TARGET_ADDENDUM_HASH),
        "prediction_seal": (str(PREDICTION.relative_to(ROOT)), PREDICTION_PAYLOAD_HASH),
        "preserved_v1_capture": (str(V1_INVENTORY.relative_to(ROOT)), V1_INVENTORY_HASH),
        "source_recapture_count": 0,
        "all_favourable_adverse_absent_unavailable_and_unresolved_results_preserved": True,
        "rows": rows,
    }
    INVENTORY.write_text(json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(INVENTORY.relative_to(ROOT), hash_file(INVENTORY))
    for row in rows:
        print(row["source_group_id"], row["primary_capture"]["http_status"], row["complete_selected_link_count"])
        for linked in row["complete_linked_captures"]:
            print(" linked", linked["http_status"], linked["content_type"], linked["snapshot_bytes"], linked["snapshot_sha256"])


if __name__ == "__main__":
    main()
