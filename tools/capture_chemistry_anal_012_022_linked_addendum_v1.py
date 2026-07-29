#!/usr/bin/env python3
"""Capture every linked NIST spectral record and the declared JPL transport mirror.

This is an append-only post-seal transport addendum.  It does not alter the
original source inventory, source identities, target identities, laws, or
prediction seals.  WebBook links are generated exhaustively from the three
already captured registered identity pages.  The Harvard CfA file is retained
only as a transport mirror of the unavailable registered JPL file and is never
silently relabelled as a successful JPL-origin fetch.
"""

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
SNAP = ROOT / "experiments/external_sources/chemistry/snapshots/anal-012-022-whole-subfield-v1"
PRIMARY_INVENTORY = SNAP / "source-inventory-v1.json"
ADDENDUM = ROOT / "experiments/external_sources/chemistry/anal_012_022_source_transport_addendum_v1.json"
EXPECTED_ENGINE = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
EXPECTED_AUTHORITY = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"
USER_AGENT = "Ernos-Labs-SFT-V3-complete-linked-capture/1 (Maria.Smith.Sftoe@gmail.com)"
WEBBOOK = "https://webbook.nist.gov"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_digest(value: object) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def verify_seals() -> None:
    for script, expected, key in (
        ("tools/verify_engine_seal.py", EXPECTED_ENGINE, "seal_id"),
        ("tools/verify_verification_authority_seal.py", EXPECTED_AUTHORITY, "authority_seal_id"),
    ):
        run = subprocess.run((sys.executable, script, "--json"), cwd=ROOT, text=True, capture_output=True, check=False)
        if run.returncode or json.loads(run.stdout)[key] != expected:
            raise SystemExit(f"protected seal failed: {script}")


def safe_fragment(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def fetch(session: requests.Session, *, source_id: str, url: str, filename: str, relationship: str) -> dict:
    path = SNAP / filename
    if path.exists():
        data = path.read_bytes()
        status: int | str = "resumed-local-addendum-capture"
        final_url = url
        content_type = "application/octet-stream"
    else:
        response = session.get(url, timeout=90, allow_redirects=True)
        response.raise_for_status()
        data = response.content
        if not data:
            raise ValueError("empty response body")
        path.write_bytes(data)
        status = response.status_code
        final_url = response.url
        content_type = response.headers.get("content-type", "")
    return {
        "source_id": source_id,
        "relationship": relationship,
        "discovered_from_immutable_registered_capture": True,
        "url": url,
        "final_url": final_url,
        "http_status": status,
        "content_type": content_type,
        "path": path.relative_to(ROOT).as_posix(),
        "byte_count": len(data),
        "sha256": digest(data),
    }


def main() -> None:
    if ADDENDUM.exists():
        raise SystemExit("linked transport addendum already exists; overwrite prohibited")
    verify_seals()
    primary = json.loads(PRIMARY_INVENTORY.read_text())
    if primary["transport_failure_count"] != 2:
        raise SystemExit("unexpected primary inventory transport-failure state")

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    captured: list[dict] = []
    failures: list[dict] = []
    all_urls: set[str] = set()

    pages = [
        item for item in primary["captured_artifacts"]
        if item["source_id"] in {
            "NIST-WEBBOOK-BENZENE-MULTIMODAL",
            "NIST-WEBBOOK-ACETONE-MULTIMODAL",
            "NIST-WEBBOOK-CYCLOHEXANE-MULTIMODAL",
        } and item["relationship"] == "registered-primary"
    ]
    for item in sorted(pages, key=lambda row: row["source_id"]):
        source_id = item["source_id"]
        cas = parse_qs(urlparse(item["registered_or_discovered_url"]).query)["ID"][0]
        soup = BeautifulSoup((ROOT / item["path"]).read_bytes(), "html.parser")

        # Capture every IR record listed by the registered molecule page.
        ir_heading = soup.find(id="IR-Spec")
        ir_page_urls: set[str] = set()
        if ir_heading:
            for node in ir_heading.find_all_next():
                if node is not ir_heading and node.name in {"h2", "h3"}:
                    break
                if node.name == "a" and node.get("href"):
                    linked = urljoin(item["final_url"], node["href"].split("#", 1)[0])
                    query = parse_qs(urlparse(linked).query)
                    if query.get("ID") == [cas] and query.get("Type") == ["IR-SPEC"] and "Index" in query:
                        ir_page_urls.add(linked)

        for linked in sorted(ir_page_urls, key=lambda u: int(parse_qs(urlparse(u).query)["Index"][0])):
            index = parse_qs(urlparse(linked).query)["Index"][0]
            page_name = f"{safe_fragment(source_id)}-ir-index-{int(index):03d}.html"
            try:
                page = fetch(session, source_id=source_id, url=linked, filename=page_name, relationship="linked-complete-ir-record-page")
                captured.append(page)
                ir_soup = BeautifulSoup((ROOT / page["path"]).read_bytes(), "html.parser")
                derived_urls: set[tuple[str, str]] = set()
                for anchor in ir_soup.select("a[href]"):
                    u = urljoin(linked, anchor["href"])
                    q = parse_qs(urlparse(u).query)
                    if q.get("JCAMP") == [cas] and q.get("Type") == ["IR"] and q.get("Index") == [index]:
                        derived_urls.add((u, "linked-complete-ir-jcamp"))
                for image in ir_soup.select("img[src]"):
                    u = urljoin(linked, image["src"])
                    q = parse_qs(urlparse(u).query)
                    if q.get("Spec") == [cas] and q.get("Type") == ["IR"] and q.get("Index") == [index]:
                        derived_urls.add((u, "linked-complete-ir-render"))
                for u, relationship in sorted(derived_urls):
                    suffix = "jdx" if relationship.endswith("jcamp") else "png"
                    record = fetch(
                        session, source_id=source_id, url=u,
                        filename=f"{safe_fragment(source_id)}-ir-index-{int(index):03d}-{suffix}.{suffix}",
                        relationship=relationship,
                    )
                    captured.append(record)
                    all_urls.add(u)
            except Exception as exc:
                failures.append({"source_id": source_id, "url": linked, "error": type(exc).__name__ + ": " + str(exc)})

        # Capture the complete mass-spectrum JCAMP and source-provided render.
        for relationship, query_key, type_name, extension in (
            ("linked-complete-mass-jcamp", "JCAMP", "Mass", "jdx"),
            ("linked-complete-mass-render", "Spec", "Mass", "png"),
        ):
            linked = f"{WEBBOOK}/cgi/cbook.cgi?{query_key}={cas}&Index=0&Type={type_name}"
            if linked in all_urls:
                continue
            try:
                captured.append(fetch(
                    session, source_id=source_id, url=linked,
                    filename=f"{safe_fragment(source_id)}-mass-index-000-{extension}.{extension}",
                    relationship=relationship,
                ))
                all_urls.add(linked)
            except Exception as exc:
                failures.append({"source_id": source_id, "url": linked, "error": type(exc).__name__ + ": " + str(exc)})

    # The registered JPL endpoints failed.  Preserve that fact and capture the
    # fixed c028001.cat identity through an institutional Harvard CfA mirror.
    mirror_url = "https://lweb.cfa.harvard.edu/sma/miriad/wbcorrTest/downLoad/NewFormat/miriad4.3.5beta3.1.0/build/share/miriad/cat/jplcat/c028001.cat"
    try:
        mirror = fetch(
            session,
            source_id="NASA-JPL-CO-ROTATIONAL-LINE-CATALOG-028001",
            url=mirror_url,
            filename="nasa-jpl-co-028001-harvard-cfa-transport-mirror.cat",
            relationship="institutional-transport-mirror-of-unavailable-registered-jpl-file",
        )
        mirror["original_registered_jpl_transport_remains_unavailable"] = True
        mirror["mirror_institution"] = "Harvard-Smithsonian Center for Astrophysics"
        mirror["source_identity_claim"] = "JPL catalog file c028001.cat as mirrored; byte identity with the currently unavailable JPL endpoint is not asserted without a direct comparison"
        captured.append(mirror)
    except Exception as exc:
        failures.append({"source_id": "NASA-JPL-CO-ROTATIONAL-LINE-CATALOG-028001", "url": mirror_url, "error": type(exc).__name__ + ": " + str(exc)})

    payload = {
        "schema": "sft-v3-linked-source-transport-addendum/1",
        "family": "ANAL-012-022-WHOLE-ANALYTICAL-CHEMISTRY-CONTINUATION",
        "created_date": "2026-07-28",
        "primary_inventory_path": PRIMARY_INVENTORY.relative_to(ROOT).as_posix(),
        "primary_inventory_sha256": digest(PRIMARY_INVENTORY.read_bytes()),
        "append_only": True,
        "changes_law_candidate_target_or_survivor": False,
        "selection_rule": "Capture every NIST IR record linked from each already captured registered molecule page, every corresponding IR JCAMP and render, both source-provided mass records, and the fixed-name institutional transport mirror of the unavailable registered JPL c028001.cat file.",
        "original_jpl_failures_remain_declared": primary["transport_failures"],
        "captured_artifact_count": len(captured),
        "transport_failure_count": len(failures),
        "captured_artifacts": captured,
        "transport_failures": failures,
    }
    payload["addendum_payload_sha256"] = canonical_digest(payload)
    ADDENDUM.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    verify_seals()
    print(json.dumps({
        "addendum": ADDENDUM.relative_to(ROOT).as_posix(),
        "addendum_sha256": digest(ADDENDUM.read_bytes()),
        "captured_artifacts": len(captured),
        "captured_bytes": sum(row["byte_count"] for row in captured),
        "transport_failures": len(failures),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
