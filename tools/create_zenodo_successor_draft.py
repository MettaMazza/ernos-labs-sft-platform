#!/usr/bin/env python3
"""Create one Zenodo successor draft from an existing published version."""

import argparse
import os
from pathlib import Path

from publish_zenodo_deposit import API, request


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", required=True)
    args = parser.parse_args()
    token_file = Path(os.environ.get("ZENODO_TOKEN_FILE", "~/.zenodo_token")).expanduser()
    token = token_file.read_text(encoding="utf-8").strip()
    if not token:
        raise SystemExit("Zenodo token file is empty")
    source_url = f"{API}/deposit/depositions/{args.record}"
    source = request(token, "GET", source_url)
    if not source.get("submitted"):
        raise SystemExit(f"record {args.record} is not a published source version")
    created = request(token, "POST", f"{source_url}/actions/newversion")
    draft_url = created.get("links", {}).get("latest_draft")
    if not draft_url:
        raise SystemExit("Zenodo did not return a latest-draft link")
    draft = request(token, "GET", draft_url)
    print(
        "SUCCESSOR_DRAFT "
        f"source_record={args.record} draft={draft.get('id')} "
        f"reserved_doi={draft.get('metadata', {}).get('prereserve_doi', {}).get('doi')} "
        f"conceptdoi={draft.get('conceptdoi') or draft.get('metadata', {}).get('conceptdoi')}"
    )


if __name__ == "__main__":
    main()
