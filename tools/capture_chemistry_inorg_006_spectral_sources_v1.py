#!/usr/bin/env python3
"""Capture the value-free-sealed INORG-006 NIST spectral surface once."""

from __future__ import annotations

from collections import Counter
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


SPEC = ROOT / "experiments/external_sources/chemistry/inorg_006_spectral_source_identity_addendum_v1.json"
SPEC_HASH = "sha256:62da50e877530e09cd7f5f97b671ce2e927573fa4e59bc6799d8ceb3c1cbb7b1"
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-006-spectral-addendum-v1"
INVENTORY = SNAPSHOT / "source-inventory-v1.json"


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href = ""
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            self._href = dict(attrs).get("href") or ""
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href:
            self.links.append((self._href, " ".join(self._text).strip()))
            self._href = ""
            self._text = []


def _fetch(uri: str, user_agent: str) -> tuple[bytes, dict[str, object]]:
    request = Request(uri, headers={"User-Agent": user_agent})
    try:
        with urlopen(request, timeout=60) as response:
            payload = response.read()
            return payload, {
                "capture_status": "captured_complete_response",
                "http_status": getattr(response, "status", 200),
                "response_content_type": response.headers.get("Content-Type", ""),
                "response_final_uri": response.geturl(),
            }
    except HTTPError as exc:
        return exc.read(), {
            "capture_status": "adverse_http_response_preserved",
            "http_status": exc.code,
            "error_class": type(exc).__name__,
        }
    except (URLError, TimeoutError, OSError) as exc:
        return b"", {
            "capture_status": "unresolved_transport_failure_preserved",
            "error_class": type(exc).__name__,
            "error_text": str(exc),
        }


def main() -> None:
    if hash_file(SPEC) != SPEC_HASH:
        raise SystemExit("VOID_INVALID_HALTED: INORG-006 spectral identity addendum changed")
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    if (
        spec.get("target_values_or_outcomes_present") is not False
        or spec.get("spectrum_payload_peak_position_intensity_or_band_count_present") is not False
        or len(spec.get("sources", ())) != 3
    ):
        raise SystemExit("VOID_INVALID_HALTED: INORG-006 spectral identity addendum is not complete and value-free")
    if INVENTORY.exists() or SNAPSHOT.exists():
        raise SystemExit("INORG-006 spectral authority already captured; preserved without replay")

    SNAPSHOT.mkdir(parents=True)
    rows: list[dict[str, object]] = []
    for source_ordinal, source in enumerate(spec["sources"], start=1):
        stem = source["source_id"].lower().replace("nist-webbook-", "nist-").replace("-uvvis-complete", "")
        page_path = SNAPSHOT / f"{stem}.html"
        page_payload, page_status = _fetch(source["uri"], "Ernos-Labs-SFT-v3-inorg-006-spectral-capture/1")
        if page_payload:
            page_path.write_bytes(page_payload)
        page_row: dict[str, object] = {
            "source_ordinal": source_ordinal,
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
        if page_payload:
            page_row.update({"snapshot_bytes": len(page_payload), "snapshot_sha256": hash_file(page_path)})
        rows.append(page_row)

        discovered: list[str] = []
        if page_status["capture_status"] == "captured_complete_response":
            parser = _Links()
            parser.feed(page_payload.decode("utf-8", errors="replace"))
            for href, text in parser.links:
                marker = f"{href} {text}".lower()
                if "jcamp" in marker and "mass" not in marker and "infrared" not in marker:
                    uri = urljoin(source["uri"], href)
                    if uri not in discovered:
                        discovered.append(uri)

        if not discovered:
            rows.append({
                "source_ordinal": source_ordinal,
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
        for payload_ordinal, uri in enumerate(discovered, start=1):
            spectrum_path = SNAPSHOT / f"{stem}-spectrum-{payload_ordinal}.jdx"
            spectrum_payload, spectrum_status = _fetch(uri, "Ernos-Labs-SFT-v3-inorg-006-spectral-capture/1")
            if spectrum_payload:
                spectrum_path.write_bytes(spectrum_payload)
            spectrum_row: dict[str, object] = {
                "source_ordinal": source_ordinal,
                "payload_ordinal": payload_ordinal,
                "source_id": source["source_id"],
                "authority": source["authority"],
                "identity": source["identity"],
                "registered_source_role": source["registered_source_role"],
                "custody_status_at_registration": source["custody_status"],
                "uri": uri,
                "surface_kind": "linked-jcamp-spectrum-payload",
                "snapshot_path": str(spectrum_path.relative_to(ROOT)),
                **spectrum_status,
            }
            if spectrum_payload:
                spectrum_row.update({"snapshot_bytes": len(spectrum_payload), "snapshot_sha256": hash_file(spectrum_path)})
            rows.append(spectrum_row)

    counts = Counter(str(row["capture_status"]) for row in rows)
    inventory = {
        "schema": "sft-v3-chemistry-inorg-006-spectral-source-inventory/1",
        "identity_addendum_sha256": SPEC_HASH,
        "complete_registered_source_count": 3,
        "complete_captured_surface_row_count": len(rows),
        "all_registered_rows_and_discovered_payloads_preserved": True,
        "capture_status_counts": dict(sorted(counts.items())),
        "rows": rows,
    }
    INVENTORY.write_text(json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "statuses": dict(counts), "inventory_sha256": hash_file(INVENTORY)}, sort_keys=True))


if __name__ == "__main__":
    main()
