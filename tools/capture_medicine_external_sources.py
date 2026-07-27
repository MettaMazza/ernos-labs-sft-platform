#!/usr/bin/env python3
"""Capture every registered Medicine source and preserve all transport outcomes."""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.request import Request, urlopen

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = ROOT / "experiments/external_sources/medicine/source_registration.json"
BASE = ROOT / "experiments/external_sources/medicine/snapshots"
MANIFEST = ROOT / "experiments/external_sources/medicine/source_manifest.json"


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.suppressed = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self.suppressed += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self.suppressed:
            self.suppressed -= 1

    def handle_data(self, data: str) -> None:
        if not self.suppressed:
            self.parts.append(data)


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def html_to_text(data: bytes) -> str:
    parser = TextExtractor()
    parser.feed(data.decode("utf-8", errors="replace"))
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip() + "\n"


def main() -> None:
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    prior_rows = {}
    if MANIFEST.is_file():
        prior_rows = {row["source_id"]: row for row in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]}
    rows = []
    for source in registration["sources"]:
        source_id = source["source_id"]
        prior = prior_rows.get(source_id)
        if prior and prior.get("transport_status") == "captured" and (ROOT / prior["snapshot_path"]).is_file() and (ROOT / prior["text_path"]).is_file():
            rows.append(prior)
            print(f"{source_id}: retained captured snapshot", flush=True)
            continue
        media_type = source["media_type"]
        raw_path = BASE / f"{source_id}.{'pdf' if media_type == 'pdf' else 'html'}"
        text_path = BASE / f"{source_id}.txt"
        record = {**source, "transport_status": "unresolved", "content_status": "unresolved"}
        if prior:
            record["prior_attempt"] = prior
        try:
            request = Request(source["source_uri"], headers={"User-Agent": "Ernos-Labs-SFT-Medicine-Audit/1.0 (+https://github.com/MettaMazza)"})
            with urlopen(request, timeout=60) as response:
                data = response.read()
                record["http_status"] = response.status
                record["final_uri"] = response.geturl()
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.write_bytes(data)
            if media_type == "pdf":
                try:
                    run = subprocess.run(["pdftotext", "-layout", str(raw_path), str(text_path)], check=False, capture_output=True, text=True)
                    if run.returncode:
                        raise RuntimeError("pdftotext failed: " + run.stderr.strip())
                    record["text_extractor"] = "pdftotext-layout"
                except FileNotFoundError:
                    pages = PdfReader(raw_path).pages
                    write_text(text_path, "\n\n".join((page.extract_text() or "") for page in pages) + "\n")
                    record["text_extractor"] = "pypdf-6"
            else:
                write_text(text_path, html_to_text(data))
            corpus = text_path.read_text(encoding="utf-8", errors="replace")
            record.update({
                "transport_status": "captured",
                "content_status": "nonempty" if corpus.strip() else "empty",
                "snapshot_path": str(raw_path.relative_to(ROOT)),
                "snapshot_hash": sha(raw_path),
                "text_path": str(text_path.relative_to(ROOT)),
                "text_hash": sha(text_path),
                "text_character_count": len(corpus),
            })
        except Exception as exc:
            failure_path = BASE / f"{source_id}.failure.txt"
            write_text(failure_path, f"{type(exc).__name__}: {exc}\n")
            record.update({
                "transport_status": "failed",
                "content_status": "unavailable",
                "failure_path": str(failure_path.relative_to(ROOT)),
                "failure_hash": sha(failure_path),
            })
        rows.append(record)
        print(f"{source_id}: {record['transport_status']} / {record['content_status']}", flush=True)
    payload = {
        "schema": "sft-v3-medicine-external-source-manifest/1",
        "source_registration_hash": registration["registration_hash"],
        "all_registered_rows_preserved": len(rows) == registration["source_count"],
        "captured_count": sum(row["transport_status"] == "captured" for row in rows),
        "failed_count": sum(row["transport_status"] == "failed" for row in rows),
        "sources": rows,
    }
    payload["manifest_hash"] = "sha256:" + hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Medicine source capture complete: {payload['captured_count']} captured; {payload['failed_count']} failed")
    print(payload["manifest_hash"])


if __name__ == "__main__":
    main()
