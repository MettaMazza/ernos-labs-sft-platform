#!/usr/bin/env python3
"""Capture the final law-sealed blind INORG-006 spectrum once."""

from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.source import hash_file  # noqa: E402


SPEC = ROOT / "experiments/external_sources/chemistry/inorg_006_spectral_source_identity_addendum_v3.json"
SPEC_HASH = "sha256:14a8af673f8996cd37560ea28877e508370b7ebec5525a68ef978fb5ad84e5cd"
LAW = ROOT / "sft/chemistry/ligand_state_splitting_law_v1.py"
LAW_HASH = "sha256:b1d1350aff301a5cb2e58471e00021897dedc3a771660f574dbbe54ef8038079"
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-006-spectral-addendum-v3"
INVENTORY = SNAPSHOT / "source-inventory-v1.json"


class _JcampLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href") or ""
        if "JCAMP=" in href and "Type=UVVis" in href and href not in self.links:
            self.links.append(href)


def _fetch(uri: str) -> tuple[bytes, dict[str, object]]:
    request = Request(uri, headers={"User-Agent": "Ernos-Labs-SFT-v3-inorg-006-blind-spectrum-capture/3"})
    try:
        with urlopen(request, timeout=60) as response:
            return response.read(), {
                "capture_status": "captured_complete_response",
                "http_status": getattr(response, "status", 200),
                "response_content_type": response.headers.get("Content-Type", ""),
                "response_final_uri": response.geturl(),
            }
    except HTTPError as exc:
        return exc.read(), {"capture_status": "adverse_http_response_preserved", "http_status": exc.code, "error_class": type(exc).__name__}
    except (URLError, TimeoutError, OSError) as exc:
        return b"", {"capture_status": "unresolved_transport_failure_preserved", "error_class": type(exc).__name__, "error_text": str(exc)}


def main() -> None:
    if hash_file(SPEC) != SPEC_HASH or hash_file(LAW) != LAW_HASH:
        raise SystemExit("VOID_INVALID_HALTED: INORG-006 law or final blind identity changed")
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    if (
        spec.get("target_values_or_outcomes_present") is not False
        or spec.get("spectrum_peak_position_intensity_or_band_count_present") is not False
    ):
        raise SystemExit("VOID_INVALID_HALTED: INORG-006 final identity is not value-free")
    if SNAPSHOT.exists() or INVENTORY.exists():
        raise SystemExit("INORG-006 final blind spectral authority already captured; preserved without replay")

    SNAPSHOT.mkdir(parents=True)
    source = spec["source"]
    rows: list[dict[str, object]] = []
    page_path = SNAPSHOT / "nist-c12146360.html"
    page, page_status = _fetch(source["uri"])
    if page:
        page_path.write_bytes(page)
    page_row: dict[str, object] = {
        "source_ordinal": 1,
        "source_id": source["source_id"],
        "authority": source["authority"],
        "identity": source["identity"],
        "registered_source_role": source["registered_source_role"],
        "custody_status_at_registration": source["custody_status"],
        "uri": source["uri"],
        "surface_kind": "complete-source-page",
        "snapshot_path": str(page_path.relative_to(ROOT)),
        **page_status,
    }
    if page:
        page_row.update({"snapshot_bytes": len(page), "snapshot_sha256": hash_file(page_path)})
    rows.append(page_row)

    parser = _JcampLinks()
    if page_status["capture_status"] == "captured_complete_response":
        parser.feed(page.decode("utf-8", errors="replace"))
    if not parser.links:
        rows.append({
            "source_ordinal": 1,
            "source_id": source["source_id"],
            "authority": source["authority"],
            "identity": source["identity"],
            "registered_source_role": source["registered_source_role"],
            "custody_status_at_registration": source["custody_status"],
            "uri": source["uri"],
            "surface_kind": "linked-jcamp-spectrum-payload",
            "capture_status": "absent_linked_jcamp_payload_preserved",
            "snapshot_path": "EmptyOne",
        })
    for payload_ordinal, href in enumerate(parser.links, start=1):
        uri = urljoin(source["uri"], href)
        spectrum_path = SNAPSHOT / f"nist-c12146360-spectrum-{payload_ordinal}.jdx"
        payload, status = _fetch(uri)
        if payload:
            spectrum_path.write_bytes(payload)
        row: dict[str, object] = {
            "source_ordinal": 1,
            "payload_ordinal": payload_ordinal,
            "source_id": source["source_id"],
            "authority": source["authority"],
            "identity": source["identity"],
            "registered_source_role": source["registered_source_role"],
            "custody_status_at_registration": source["custody_status"],
            "uri": uri,
            "surface_kind": "linked-jcamp-spectrum-payload",
            "snapshot_path": str(spectrum_path.relative_to(ROOT)),
            **status,
        }
        if payload:
            row.update({"snapshot_bytes": len(payload), "snapshot_sha256": hash_file(spectrum_path)})
        rows.append(row)

    inventory = {
        "schema": "sft-v3-chemistry-inorg-006-final-blind-spectral-source-inventory/1",
        "identity_addendum_sha256": SPEC_HASH,
        "sealed_fold_law_sha256": LAW_HASH,
        "complete_registered_source_count": 1,
        "complete_captured_surface_row_count": len(rows),
        "all_registered_rows_and_discovered_uvvis_payloads_preserved": True,
        "rows": rows,
    }
    INVENTORY.write_text(json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "inventory_sha256": hash_file(INVENTORY), "statuses": [row["capture_status"] for row in rows]}, sort_keys=True))


if __name__ == "__main__":
    main()
