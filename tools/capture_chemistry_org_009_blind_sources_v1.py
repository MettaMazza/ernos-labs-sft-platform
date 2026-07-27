#!/usr/bin/env python3
"""Capture the three preregistered Rhea release-141 ORG-009 payloads once."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.request import Request, urlopen
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ROOT / "experiments/external_sources/chemistry/org_009_target_identities_v1.json"
PRESEAL = ROOT / "experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_source_v1.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-rhea-blind-v1"
EXPECTED_IDENTITY = "sha256:5d5640cfe54794a2c588031f7fb2b0479a6fe0fc798295a892dbc19aceb10f27"
EXPECTED_PRESEAL = "sha256:b2c56dfb6e6b70cdf984d48bf08151d4de1269884645bea5ca74cb1da34c7a1e"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def fetch(uri: str) -> tuple[bytes, int, dict[str, str]]:
    request = Request(
        uri,
        headers={"User-Agent": "Ernos-Labs-SFT/3 (Maria.Smith.Sftoe@gmail.com)"},
    )
    try:
        with urlopen(request, timeout=120) as response:
            return (
                response.read(),
                response.status,
                {key.lower(): value for key, value in response.headers.items()},
            )
    except URLError:
        curl = shutil.which("curl")
        if curl is None:
            raise
        with tempfile.TemporaryDirectory(prefix="sft-org009-rhea-") as temporary:
            body = Path(temporary) / "body"
            header = Path(temporary) / "headers"
            completed = subprocess.run(
                (
                    curl, "-fsSL", "--max-time", "120",
                    "-A", "Ernos-Labs-SFT/3 (Maria.Smith.Sftoe@gmail.com)",
                    "-D", str(header), "-o", str(body), uri,
                ),
                text=True,
                capture_output=True,
                check=False,
            )
            if completed.returncode != 0:
                raise RuntimeError("curl fallback failed: " + completed.stderr.strip())
            blocks = [block for block in header.read_text().replace("\r\n", "\n").split("\n\n") if block.strip()]
            lines = blocks[-1].splitlines()
            status = int(lines[0].split()[1])
            headers = {
                key.strip().lower(): value.strip()
                for line in lines[1:] if ":" in line
                for key, value in (line.split(":", 1),)
            }
            return body.read_bytes(), status, headers


def main() -> None:
    if digest(IDENTITY.read_bytes()) != EXPECTED_IDENTITY:
        raise SystemExit("ORG-009 target identity changed before capture")
    if digest(PRESEAL.read_bytes()) != EXPECTED_PRESEAL:
        raise SystemExit("ORG-009 prediction seal changed before capture")
    identity = json.loads(IDENTITY.read_text())
    if identity.get("external_values_products_equations_smiles_or_outcomes_present") is not False:
        raise SystemExit("ORG-009 identity is not outcome-free")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    filenames = {
        "SFT-CHEM-ORG-009-RHEA-EC-MAP": "rhea2ec.tsv",
        "SFT-CHEM-ORG-009-RHEA-DIRECTIONS": "rhea-directions.tsv",
        "SFT-CHEM-ORG-009-RHEA-SMILES": "rhea-reaction-smiles.tsv",
    }
    rows = []
    for source in identity["outcome_unopened_rows"]:
        path = OUTPUT / filenames[source["target_id"]]
        if path.exists():
            raise SystemExit(f"ORG-009 source already exists; recapture prohibited: {path}")
        payload, status, headers = fetch(source["uri"])
        registered = source["registered_http_head"]
        if status != 200 or len(payload) != registered["content_length"]:
            raise SystemExit(f"ORG-009 registered source response changed: {source['target_id']}")
        if headers.get("etag", "").strip('"') != registered["etag"]:
            raise SystemExit(f"ORG-009 registered source ETag changed: {source['target_id']}")
        path.write_bytes(payload)
        rows.append(
            {
                **source,
                "capture_status": "captured_once_after_claim_specific_seal",
                "http_status": status,
                "opened_snapshot_path": path.relative_to(ROOT).as_posix(),
                "opened_snapshot_bytes": len(payload),
                "opened_snapshot_sha256": digest(payload),
                "response_last_modified": headers.get("last-modified"),
                "response_etag": headers.get("etag"),
                "response_content_type": headers.get("content-type"),
            }
        )
    inventory = {
        "schema": "sft-v3-chemistry-org-009-rhea-capture-inventory/1",
        "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
        "prediction_seal_path": PRESEAL.relative_to(ROOT).as_posix(),
        "prediction_seal_sha256": EXPECTED_PRESEAL,
        "source_recapture_count": 0,
        "all_payloads_opened_only_after_seal": True,
        "rows": rows,
    }
    inventory_path = OUTPUT / "source-inventory-v1.json"
    inventory_path.write_text(
        json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"inventory": inventory_path.relative_to(ROOT).as_posix(), "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
