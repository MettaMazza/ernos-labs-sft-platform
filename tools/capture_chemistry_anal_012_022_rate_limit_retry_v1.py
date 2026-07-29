#!/usr/bin/env python3
"""Append-only, rate-limited completion of ANAL-012--022 linked NIST records."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup
import requests


ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "experiments/external_sources/chemistry/snapshots/anal-012-022-whole-subfield-v1"
FIRST = ROOT / "experiments/external_sources/chemistry/anal_012_022_source_transport_addendum_v1.json"
RETRY = ROOT / "experiments/external_sources/chemistry/anal_012_022_rate_limit_retry_addendum_v1.json"
EXPECTED_ENGINE = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
EXPECTED_AUTHORITY = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"
USER_AGENT = "Ernos-Labs-SFT-V3-rate-limited-source-retry/1 (Maria.Smith.Sftoe@gmail.com)"


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


def request_with_backoff(session: requests.Session, url: str) -> requests.Response:
    for attempt in range(1, 8):
        response = session.get(url, timeout=90, allow_redirects=True)
        if response.status_code != 429:
            response.raise_for_status()
            if not response.content:
                raise ValueError("empty response body")
            return response
        wait = min(30, int(response.headers.get("retry-after", "0") or 0) or attempt * 4)
        time.sleep(wait)
    raise requests.HTTPError(f"persistent 429 after seven attempts: {url}")


def fetch(session: requests.Session, source_id: str, relationship: str, url: str, path: Path) -> dict:
    if path.exists():
        data = path.read_bytes()
        status: int | str = "resumed-local-rate-limit-retry"
        final_url = url
        content_type = "application/octet-stream"
    else:
        response = request_with_backoff(session, url)
        data = response.content
        path.write_bytes(data)
        status = response.status_code
        final_url = response.url
        content_type = response.headers.get("content-type", "")
        time.sleep(1)
    return {
        "source_id": source_id,
        "relationship": relationship,
        "url": url,
        "final_url": final_url,
        "http_status": status,
        "content_type": content_type,
        "path": path.relative_to(ROOT).as_posix(),
        "byte_count": len(data),
        "sha256": digest(data),
    }


def main() -> None:
    if RETRY.exists():
        raise SystemExit("rate-limit retry addendum already exists; overwrite prohibited")
    verify_seals()
    first = json.loads(FIRST.read_text())
    already = {row["url"] for row in first["captured_artifacts"]}
    pages = [row for row in first["captured_artifacts"] if row["relationship"] == "linked-complete-ir-record-page"]
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    captured: list[dict] = []
    failures: list[dict] = []

    for page in sorted(pages, key=lambda row: (row["source_id"], row["url"])):
        soup = BeautifulSoup((ROOT / page["path"]).read_bytes(), "html.parser")
        cas = parse_qs(urlparse(page["url"]).query)["ID"][0]
        index = parse_qs(urlparse(page["url"]).query)["Index"][0]
        expected = (
            (f"https://webbook.nist.gov/cgi/cbook.cgi?JCAMP={cas}&Index={index}&Type=IR", "linked-complete-ir-jcamp", "jdx"),
            (f"https://webbook.nist.gov/cgi/cbook.cgi?Spec={cas}&Index={index}&Type=IR", "linked-complete-ir-render", "png"),
        )
        # Require the expected identities to be evidenced by the captured page.
        page_urls = {
            requests.compat.urljoin(page["url"], node.get("href") or node.get("src"))
            for node in soup.select("a[href],img[src]")
        }
        for url, relationship, extension in expected:
            if url in already:
                continue
            if url not in page_urls:
                failures.append({"source_id": page["source_id"], "url": url, "error": "expected linked identity absent from immutable IR page"})
                continue
            path = SNAP / f"{page['path'].rsplit('/', 1)[-1].removesuffix('.html')}-{extension}.{extension}"
            try:
                row = fetch(session, page["source_id"], relationship, url, path)
                captured.append(row)
                already.add(url)
            except Exception as exc:
                failures.append({"source_id": page["source_id"], "url": url, "error": type(exc).__name__ + ": " + str(exc)})

    for source_id, cas in (
        ("NIST-WEBBOOK-BENZENE-MULTIMODAL", "C71432"),
        ("NIST-WEBBOOK-ACETONE-MULTIMODAL", "C67641"),
        ("NIST-WEBBOOK-CYCLOHEXANE-MULTIMODAL", "C110827"),
    ):
        url = f"https://webbook.nist.gov/cgi/cbook.cgi?JCAMP={cas}&Index=0&Type=Mass"
        if url in already:
            continue
        path = SNAP / f"{source_id.casefold().replace('_', '-')}-mass-index-000-jdx.jdx"
        try:
            captured.append(fetch(session, source_id, "linked-complete-mass-jcamp", url, path))
            already.add(url)
        except Exception as exc:
            failures.append({"source_id": source_id, "url": url, "error": type(exc).__name__ + ": " + str(exc)})

    payload = {
        "schema": "sft-v3-rate-limited-source-retry-addendum/1",
        "family": "ANAL-012-022-WHOLE-ANALYTICAL-CHEMISTRY-CONTINUATION",
        "created_date": "2026-07-28",
        "prior_addendum_path": FIRST.relative_to(ROOT).as_posix(),
        "prior_addendum_sha256": digest(FIRST.read_bytes()),
        "append_only": True,
        "changes_law_candidate_target_or_survivor": False,
        "retry_reason": "The complete first bulk request preserved 61 HTTP 429 outcomes after securing all 63 IR identity pages; this pass uses bounded backoff and one-second pacing to retrieve only those missing linked records.",
        "captured_artifact_count": len(captured),
        "transport_failure_count": len(failures),
        "captured_artifacts": captured,
        "transport_failures": failures,
    }
    payload["addendum_payload_sha256"] = canonical_digest(payload)
    RETRY.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    verify_seals()
    print(json.dumps({
        "addendum": RETRY.relative_to(ROOT).as_posix(),
        "addendum_sha256": digest(RETRY.read_bytes()),
        "captured_artifacts": len(captured),
        "captured_bytes": sum(row["byte_count"] for row in captured),
        "transport_failures": len(failures),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
