#!/usr/bin/env python3
"""Upload, verify and optionally publish an existing Zenodo draft deposit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


API = "https://zenodo.org/api"


def request(token: str, method: str, url: str, data: bytes | None = None, content_type: str | None = None):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if content_type:
        headers["Content-Type"] = content_type
    call = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(call, timeout=180) as response:
            body = response.read()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Zenodo {method} failed with HTTP {exc.code}: {detail}") from exc


def checksum(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_mapping(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("file must be PUBLIC_NAME=LOCAL_PATH")
    public_name, local_name = value.split("=", 1)
    local = Path(local_name).expanduser().resolve()
    if not public_name or not local.is_file():
        raise argparse.ArgumentTypeError(f"invalid file mapping: {value}")
    return public_name, local


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft", required=True)
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--file", action="append", default=[], type=file_mapping)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    if not args.file:
        parser.error("at least one --file is required")

    token_file = Path(os.environ.get("ZENODO_TOKEN_FILE", "~/.zenodo_token")).expanduser()
    token = token_file.read_text(encoding="utf-8").strip()
    if not token:
        raise SystemExit("Zenodo token file is empty")
    metadata_document = json.loads(args.metadata.read_text(encoding="utf-8"))
    metadata = {"metadata": metadata_document["metadata"]}

    draft_url = f"{API}/deposit/depositions/{args.draft}"
    draft = request(token, "GET", draft_url)
    if draft.get("submitted"):
        raise RuntimeError("the supplied deposit is already published")
    for inherited in draft.get("files", []):
        request(token, "DELETE", inherited["links"]["self"])

    bucket = draft["links"]["bucket"].rstrip("/")
    expected = {}
    for public_name, local in args.file:
        encoded = urllib.parse.quote(public_name, safe="")
        request(token, "PUT", f"{bucket}/{encoded}", local.read_bytes(), "application/octet-stream")
        expected[public_name] = (local.stat().st_size, checksum(local))
        print(f"UPLOADED {public_name} bytes={expected[public_name][0]} md5={expected[public_name][1]}")

    request(token, "PUT", draft_url, json.dumps(metadata).encode("utf-8"), "application/json")
    verified = request(token, "GET", draft_url)
    actual = {
        item["filename"]: (int(item["filesize"]), item["checksum"].removeprefix("md5:"))
        for item in verified.get("files", [])
    }
    if actual != expected:
        raise RuntimeError(f"uploaded-file verification failed: expected={expected}, actual={actual}")
    if verified.get("metadata", {}).get("title") != metadata["metadata"]["title"]:
        raise RuntimeError("metadata title verification failed")
    print(f"VERIFIED draft={args.draft} files={len(actual)}")

    if not args.publish:
        print("DRAFT_READY not_published=1")
        return
    published = request(token, "POST", f"{draft_url}/actions/publish")
    print(
        "PUBLISHED "
        f"record={published.get('record_id') or published.get('id')} "
        f"doi={published.get('doi')} conceptdoi={published.get('conceptdoi')}"
    )


if __name__ == "__main__":
    main()
