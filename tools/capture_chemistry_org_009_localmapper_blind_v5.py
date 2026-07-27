#!/usr/bin/env python3
"""Capture the preregistered LocalMapper USPTO-FULL payload once after the V5 seal."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ROOT / "experiments/external_sources/chemistry/org_009_target_identities_v5.json"
PRESEAL = ROOT / "experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_source_v5.json"
LAW = ROOT / "sft/chemistry/addition_reaction_law_v2.py"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5"
EXPECTED_IDENTITY = "sha256:37f7837d807e0406eb9e337d1d0f0150d9c92da73af449376d9cb53151a71b2f"
EXPECTED_PRESEAL = "sha256:7a5cd44ad6eddb12716b4951a79fb9e9e7bbdd5e70758391c302c9f6eb0fa817"
EXPECTED_LAW = "sha256:e1bd9a6817d859b3b969b3fffceed12af3db609f9af40a461eefee4f0429e7d1"
EXPECTED_SEALED_PAYLOAD = "sha256:55d85fba66256c9c5ea7c3095972f6fcc88ab25fe17c982ac0407f5bec69d949"


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def md5_file(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_frozen_inputs() -> tuple[dict, dict]:
    if sha256_file(IDENTITY) != EXPECTED_IDENTITY:
        raise SystemExit("ORG-009 V5 target identity changed before capture")
    if sha256_file(PRESEAL) != EXPECTED_PRESEAL:
        raise SystemExit("ORG-009 V5 prediction seal changed before capture")
    if sha256_file(LAW) != EXPECTED_LAW:
        raise SystemExit("ORG-009 V2 law changed after the blind seal")
    identity = json.loads(IDENTITY.read_text(encoding="utf-8"))
    prediction = json.loads(PRESEAL.read_text(encoding="utf-8"))
    claimed = prediction.pop("sealed_payload_hash", None)
    canonical = sha256_bytes(
        json.dumps(prediction, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    )
    if claimed != EXPECTED_SEALED_PAYLOAD or canonical != claimed:
        raise SystemExit("ORG-009 V5 canonical prediction payload is not the frozen seal")
    if identity.get("external_values_products_reaction_rows_or_outcomes_present") is not False:
        raise SystemExit("ORG-009 V5 target identity is not outcome-free")
    if identity.get("remote_source_payload_open_count_before_v5_seal") != 0:
        raise SystemExit("ORG-009 V5 payload-open count is not structural absence")
    return identity, prediction


def main() -> None:
    identity, _ = verify_frozen_inputs()
    sources = identity["outcome_unopened_rows"]
    if len(sources) != 1:
        raise SystemExit("ORG-009 V5 must bind exactly one complete unopened payload")
    source = sources[0]
    registered = source["registered_file"]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT / registered["name"]
    inventory_path = OUTPUT / "source-inventory-v5.json"
    if destination.exists() or inventory_path.exists():
        raise SystemExit("ORG-009 V5 source or inventory already exists; recapture prohibited")
    curl = shutil.which("curl")
    if curl is None:
        raise SystemExit("curl is required for this one-time 427 MB evidence capture")
    with tempfile.TemporaryDirectory(prefix="sft-org009-localmapper-") as temporary:
        temporary_path = Path(temporary) / registered["name"]
        completed = subprocess.run(
            (
                curl,
                "--fail",
                "--location",
                "--max-time",
                "1800",
                "--user-agent",
                "Ernos-Labs-SFT/3 (Maria.Smith.Sftoe@gmail.com)",
                "--output",
                str(temporary_path),
                source["uri"],
            ),
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise SystemExit("ORG-009 V5 source capture failed: " + completed.stderr.strip())
        observed_bytes = temporary_path.stat().st_size
        observed_md5 = md5_file(temporary_path)
        if observed_bytes != registered["content_length"] or observed_md5 != registered["computed_md5"]:
            raise SystemExit("ORG-009 V5 source payload does not match the preregistered Figshare identity")
        shutil.move(str(temporary_path), destination)
    row = {
        **source,
        "capture_status": "captured_once_after_v5_claim_specific_seal",
        "opened_snapshot_path": destination.relative_to(ROOT).as_posix(),
        "opened_snapshot_bytes": destination.stat().st_size,
        "opened_snapshot_md5": md5_file(destination),
        "opened_snapshot_sha256": sha256_file(destination),
    }
    inventory = {
        "schema": "sft-v3-chemistry-org-009-localmapper-capture-inventory/5",
        "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
        "prediction_seal_path": PRESEAL.relative_to(ROOT).as_posix(),
        "prediction_seal_sha256": EXPECTED_PRESEAL,
        "law_path": LAW.relative_to(ROOT).as_posix(),
        "law_sha256": EXPECTED_LAW,
        "all_v1_v2_v3_v4_results_preserved": True,
        "source_recapture_count": 0,
        "all_payloads_opened_only_after_v5_seal": True,
        "rows": [row],
    }
    inventory_path.write_text(
        json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"inventory": inventory_path.relative_to(ROOT).as_posix(), "rows": [row]}, indent=2))


if __name__ == "__main__":
    main()
