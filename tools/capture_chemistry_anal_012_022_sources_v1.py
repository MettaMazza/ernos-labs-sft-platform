#!/usr/bin/env python3
"""Capture the whole ANAL-012--022 registered evidence surface post-seal."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import parse_qs, urljoin, urlparse

from bs4 import BeautifulSoup
import requests


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "experiments/external_sources/chemistry/anal_012_022_whole_subfield_source_identity_registry_v1.json"
SNAP = ROOT / "experiments/external_sources/chemistry/snapshots/anal-012-022-whole-subfield-v1"
INVENTORY = SNAP / "source-inventory-v1.json"
EXPECTED_ENGINE = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
EXPECTED_AUTHORITY = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"
USER_AGENT = "Ernos-Labs-SFT-V3-complete-source-capture/1 (Maria.Smith.Sftoe@gmail.com)"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_digest(value: object) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def verify_seals() -> None:
    for script, expected, key in (
        ("tools/verify_engine_seal.py", EXPECTED_ENGINE, "seal_id"),
        ("tools/verify_verification_authority_seal.py", EXPECTED_AUTHORITY, "authority_seal_id"),
    ):
        completed = subprocess.run((sys.executable, script, "--json"), cwd=ROOT, text=True, capture_output=True, check=False)
        if completed.returncode or json.loads(completed.stdout)[key] != expected:
            raise SystemExit(f"protected seal failed before source capture: {script}")


def safe_name(source_id: str, url: str, suffix: str = "") -> str:
    path = urlparse(url).path
    extension = Path(path).suffix.lower()
    if not extension or len(extension) > 6:
        extension = suffix or ".html"
    stem = re.sub(r"[^a-z0-9]+", "-", source_id.casefold()).strip("-")
    return stem + extension


def media_kind(data: bytes, content_type: str, url: str) -> str:
    lowered = content_type.casefold()
    if data.startswith(b"%PDF") or "pdf" in lowered:
        return "pdf"
    if data.startswith(b"PK\x03\x04"):
        return "workbook-or-archive"
    if "html" in lowered or b"<html" in data[:1000].lower():
        return "html"
    if "xml" in lowered or data.lstrip().startswith(b"<?xml"):
        return "xml"
    if "jcamp" in url.casefold() or "jdx" in url.casefold() or data.lstrip().startswith(b"##"):
        return "jcamp-dx"
    return "text-or-data"


def download(session: requests.Session, source_id: str, url: str, filename: str, relationship: str):
    path = SNAP / filename
    if path.exists():
        data = path.read_bytes()
        inferred = {
            ".html": "text/html", ".pdf": "application/pdf", ".jdx": "chemical/x-jcamp-dx",
            ".cat": "text/plain", ".xml": "text/xml",
        }.get(path.suffix.casefold(), "application/octet-stream")
        return {
            "source_id": source_id, "relationship": relationship,
            "registered_or_discovered_url": url, "final_url": url,
            "http_status": "resumed-local-capture", "content_type": inferred,
            "media_kind": media_kind(data, inferred, url),
            "path": path.relative_to(ROOT).as_posix(), "byte_count": len(data), "sha256": digest(data),
        }
    response = session.get(url, timeout=90, allow_redirects=True)
    data = response.content
    response.raise_for_status()
    if not data:
        raise ValueError("empty response body")
    path.write_bytes(data)
    return {
        "source_id": source_id,
        "relationship": relationship,
        "registered_or_discovered_url": url,
        "final_url": response.url,
        "http_status": response.status_code,
        "content_type": response.headers.get("content-type", ""),
        "media_kind": media_kind(data, response.headers.get("content-type", ""), response.url),
        "path": path.relative_to(ROOT).as_posix(),
        "byte_count": len(data),
        "sha256": digest(data),
    }


def main() -> None:
    if INVENTORY.exists():
        raise SystemExit("ANAL-012--022 source inventory already exists; overwrite prohibited")
    verify_seals()
    registry = json.loads(REGISTRY.read_text())
    for number in range(12, 23):
        if not (ROOT / f"experiments/sealed_predictions/chemistry_anal_{number:03d}_pre_source_v1.json").is_file():
            raise SystemExit(f"missing pre-source seal for ANAL-{number:03d}")
    SNAP.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    captured = []
    failures = []
    captured_urls = set()

    for source in registry["sources"]:
        url = source["capture_url"]
        if url.startswith("repository:"):
            first = source["identity_url"].removeprefix("repository:")
            last = url.removeprefix("repository:")
            for index, relative in enumerate((first, last), 1):
                path = ROOT / relative
                data = path.read_bytes()
                captured.append({
                    "source_id": source["source_id"], "relationship": f"immutable-repository-authority-{index}",
                    "registered_or_discovered_url": "repository:" + relative, "final_url": "repository:" + relative,
                    "http_status": "local-immutable", "content_type": "application/json", "media_kind": "repository-json",
                    "path": relative, "byte_count": len(data), "sha256": digest(data),
                })
            continue
        try:
            filename = safe_name(source["source_id"], url)
            item = download(session, source["source_id"], url, filename, "registered-primary")
            captured.append(item)
            captured_urls.add(item["final_url"])
        except Exception as exc:
            failures.append({"source_id": source["source_id"], "url": url, "error": type(exc).__name__ + ": " + str(exc)})
            continue

        if source.get("documentation_url"):
            doc_url = source["documentation_url"]
            try:
                captured.append(download(session, source["source_id"], doc_url, safe_name(source["source_id"] + "-documentation", doc_url, ".pdf"), "registered-documentation"))
            except Exception as exc:
                failures.append({"source_id": source["source_id"], "url": doc_url, "error": type(exc).__name__ + ": " + str(exc)})

        if source["source_id"].startswith("NIST-WEBBOOK-") and item["media_kind"] == "html":
            html = (ROOT / item["path"]).read_bytes()
            soup = BeautifulSoup(html, "html.parser")
            links = []
            registered_cas = parse_qs(urlparse(source["identity_url"]).query).get("ID", [""])[0]
            for anchor in soup.select("a[href]"):
                linked = urljoin(item["final_url"], anchor["href"])
                query = parse_qs(urlparse(linked).query)
                if "JCAMP" in query and (not registered_cas or query.get("JCAMP", [""])[0] == registered_cas):
                    links.append(linked)
            for index, linked in enumerate(sorted(set(links)), 1):
                if linked in captured_urls:
                    continue
                try:
                    linked_item = download(session, source["source_id"], linked, safe_name(source["source_id"] + f"-linked-{index}", linked, ".jdx"), "linked-machine-readable-record")
                    captured.append(linked_item)
                    captured_urls.add(linked_item["final_url"])
                except Exception as exc:
                    failures.append({"source_id": source["source_id"], "url": linked, "error": type(exc).__name__ + ": " + str(exc)})

        if source["source_id"] == "NIST-NEUTRON-SCATTERING-LENGTHS" and item["media_kind"] == "html":
            soup = BeautifulSoup((ROOT / item["path"]).read_bytes(), "html.parser")
            candidates = []
            for anchor in soup.select("a[href]"):
                label = anchor.get_text(" ", strip=True).casefold()
                linked = urljoin(item["final_url"], anchor["href"])
                if "complete list" in label or "scattering length" in label and urlparse(linked).netloc.endswith("nist.gov"):
                    candidates.append(linked)
            for index, linked in enumerate(sorted(set(candidates)), 1):
                if linked in captured_urls or linked == item["final_url"]:
                    continue
                try:
                    linked_item = download(session, source["source_id"], linked, safe_name(source["source_id"] + f"-linked-{index}", linked), "linked-complete-table")
                    captured.append(linked_item)
                    captured_urls.add(linked_item["final_url"])
                except Exception as exc:
                    failures.append({"source_id": source["source_id"], "url": linked, "error": type(exc).__name__ + ": " + str(exc)})

    inventory = {
        "schema": "sft-v3-complete-source-capture/1",
        "family": "ANAL-012-022-WHOLE-ANALYTICAL-CHEMISTRY-CONTINUATION",
        "captured_date": "2026-07-28",
        "capture_occurred_after_all_eleven_derivation_seals": True,
        "source_selection_after_outcome_access": False,
        "all_favorable_adverse_absent_unavailable_unresolved_rows_required": True,
        "registered_source_identity_count": len(registry["sources"]),
        "captured_artifact_count": len(captured),
        "transport_failure_count": len(failures),
        "captured_artifacts": captured,
        "transport_failures": failures,
    }
    inventory["inventory_payload_sha256"] = canonical_digest(inventory)
    INVENTORY.write_text(json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    verify_seals()
    print(json.dumps({
        "inventory": INVENTORY.relative_to(ROOT).as_posix(),
        "inventory_file_sha256": digest(INVENTORY.read_bytes()),
        "captured_artifacts": len(captured), "transport_failures": len(failures),
        "captured_bytes": sum(item["byte_count"] for item in captured if isinstance(item["byte_count"], int)),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
