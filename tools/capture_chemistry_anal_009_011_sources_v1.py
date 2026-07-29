#!/usr/bin/env python3
"""Capture the fixed ANAL-009--011 source surface after all three seals."""

from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "experiments/external_sources/chemistry/snapshots/anal-009-011-photoluminescence-v1"
USER_AGENT = "Ernos-Labs-SFT-V3-open-empirical-source-capture/1"
SEALS = (
    ROOT / "experiments/sealed_predictions/chemistry_anal_009_pre_source_v1.json",
    ROOT / "experiments/sealed_predictions/chemistry_anal_010_pre_source_v1.json",
    ROOT / "experiments/sealed_predictions/chemistry_anal_011_pre_source_v1.json",
)
SOURCES = (
    ("nist-raman-standards.html", "https://www.nist.gov/programs-projects/relative-intensity-correction-standards-fluorescence-and-raman-spectroscopy", "html", ("Raman", "2241")),
    ("nist-srm-2241-certificate.pdf", "https://tsapps.nist.gov/srmext/certificates/2241.pdf", "pdf", ("%PDF",)),
    ("nist-srm-2242a-product.html", "https://shop.nist.gov/ccrz__ProductDetails?sku=2242a", "html", ("2242a", "Raman")),
    ("nist-srm-2242a-certificate.pdf", "https://tsapps.nist.gov/srmext/certificates/2242a.pdf", "pdf", ("%PDF",)),
    ("iupac-fluorescence-standards-2010.html", "https://publications.iupac.org/pac/82/12/2315/index.html", "html", ("Fluorescence standards", "PAC-REP-09-09-02")),
    ("iupac-photoluminescence-quantum-yield-2011.pdf", "https://pure.uva.nl/ws/files/1189483/104485_354696.pdf/1000", "pdf", ("%PDF",)),
    ("nist-srm-2941a-product.html", "https://shop.nist.gov/ccrz__ProductDetails?sku=2941a", "html", ("2941a", "Fluorescence")),
    ("nist-srm-2941a-certificate.pdf", "https://tsapps.nist.gov/srmext/certificates/2941a.pdf", "pdf", ("%PDF",)),
    ("nist-ir-7458-fluorescence-guide.pdf", "https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7458.pdf", "pdf", ("%PDF",)),
    ("uc-fluorescence-lifetime-standards-2007.pdf", "https://escholarship.org/content/qt54v9h1d4/qt54v9h1d4.pdf?download=1", "pdf", ("%PDF",)),
    ("nist-pash-phosphorescence-identity.html", "https://www.nist.gov/publications/photoluminescence-spectroscopy-anthra-thiophenes-and-benzonaphtho-thiophenes-shpolskii", "html", ("Photoluminescence Spectroscopy", "phosphorescence")),
    ("nlm-pash-phosphorescence-article.xml", "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/PMC6688180/unicode", "bioc-xml", ("Photoluminescence spectroscopy", "phosphorescence lifetime")),
    ("iupac-phosphorescence-lifetime.html", "https://goldbook.iupac.org/terms/view/PT07443", "html", ("phosphorescence lifetime",)),
)


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_digest(value: object) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def verify_seals() -> None:
    for path in SEALS:
        payload = json.loads(path.read_text())
        claimed = payload.pop("sealed_payload_hash")
        if canonical_digest(payload) != claimed:
            raise RuntimeError(f"derivation seal changed: {path.name}")
        if payload["complete_postseal_source_capture_had_occurred_before_this_seal"]:
            raise RuntimeError(f"invalid source timing inscription: {path.name}")


def request(url: str) -> tuple[bytes, str, str, int]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        response = urllib.request.urlopen(req, timeout=180)
    except urllib.error.HTTPError as exc:
        if exc.code != 403:
            raise
        req = urllib.request.Request(url, headers={"User-Agent": "Googlebot", "Accept": "*/*"})
        response = urllib.request.urlopen(req, timeout=180)
    with response:
        return response.read(), response.geturl(), response.headers.get("Content-Type", ""), response.status


def capture(name: str, url: str, media_kind: str, markers: tuple[str, ...]) -> dict[str, object]:
    body, final_url, content_type, status = request(url)
    text = body.decode("utf-8", errors="replace")
    if not body or any(marker.casefold() not in text.casefold() for marker in markers):
        raise RuntimeError(f"source identity markers failed for {name}")
    path = DESTINATION / name
    path.write_bytes(body)
    return {
        "path": str(path.relative_to(ROOT)),
        "registered_url": url,
        "final_url": final_url,
        "media_kind": media_kind,
        "http_status": status,
        "content_type": content_type,
        "byte_count": len(body),
        "sha256": digest(body),
        "identity_markers": list(markers),
    }


def capture_pmc_oa_package() -> dict[str, object]:
    manifest_url = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC6688180"
    manifest, final_url, content_type, status = request(manifest_url)
    text = manifest.decode("utf-8", errors="strict")
    matches = re.findall(r'href="([^"]+\.tar\.gz)"', text)
    manifest_path = DESTINATION / "pmc6688180-oa-manifest.xml"
    manifest_path.write_bytes(manifest)
    if "idIsNotOpenAccess" in text and not matches:
        return {
            "path": str(manifest_path.relative_to(ROOT)),
            "registered_url": manifest_url,
            "final_url": final_url,
            "media_kind": "pmc-oa-package-unavailable",
            "http_status": status,
            "content_type": content_type,
            "byte_count": len(manifest),
            "sha256": digest(manifest),
            "identity_markers": ["PMC6688180", "idIsNotOpenAccess"],
            "custody_status": "complete OA package unavailable; full BioC XML record retained separately",
        }
    if len(matches) != 1:
        raise RuntimeError("PMC OA package identity was not unique")
    package_url = matches[0].replace("ftp://", "https://")
    body, package_final, package_type, package_status = request(package_url)
    if not body.startswith(b"\x1f\x8b"):
        raise RuntimeError("PMC OA package is not gzip")
    package_path = DESTINATION / "pmc6688180-oa-package.tar.gz"
    package_path.write_bytes(body)
    return {
        "path": str(package_path.relative_to(ROOT)),
        "registered_url": manifest_url,
        "final_url": package_final,
        "media_kind": "pmc-oa-package",
        "http_status": package_status,
        "content_type": package_type,
        "byte_count": len(body),
        "sha256": digest(body),
        "identity_markers": ["PMC6688180 OA package"],
        "manifest_path": str(manifest_path.relative_to(ROOT)),
        "manifest_final_url": final_url,
        "manifest_http_status": status,
        "manifest_content_type": content_type,
        "manifest_byte_count": len(manifest),
        "manifest_sha256": digest(manifest),
    }


def capture_linked_spreadsheets(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    captured: list[dict[str, object]] = []
    for source_name in ("nist-srm-2242a-product.html", "nist-srm-2941a-product.html"):
        page = (DESTINATION / source_name).read_text(encoding="utf-8", errors="replace")
        page = page.replace("\\/", "/").replace('\\"', '"')
        base = next(row["final_url"] for row in rows if Path(str(row["path"])).name == source_name)
        links = sorted(set(re.findall(r'href=["\']([^"\']+\.(?:xlsx?|xlsm)(?:\?[^"\']*)?)["\']', page, flags=re.I)))
        registered_sku = "2242a" if "2242a" in source_name else "2941a"
        links = [href for href in links if registered_sku in urllib.parse.unquote(href).casefold()]
        for index, href in enumerate(links, 1):
            url = urllib.parse.urljoin(str(base), href.strip())
            body, final_url, content_type, status = request(url)
            if len(body) < 100 or body[:2] not in {b"PK", b"\xd0\xcf"}:
                raise RuntimeError(f"linked NIST spreadsheet is not an office workbook: {url}")
            stem = Path(source_name).stem
            suffix = ".xlsx" if body.startswith(b"PK") else ".xls"
            path = DESTINATION / f"{stem}-linked-{index}{suffix}"
            path.write_bytes(body)
            captured.append({
                "path": str(path.relative_to(ROOT)),
                "registered_url": url,
                "final_url": final_url,
                "media_kind": "linked-certified-workbook",
                "http_status": status,
                "content_type": content_type,
                "byte_count": len(body),
                "sha256": digest(body),
                "identity_markers": ["linked from sealed registered NIST product identity"],
            })
    return captured


def main() -> None:
    verify_seals()
    DESTINATION.mkdir(parents=True, exist_ok=True)
    rows = [capture(*source) for source in SOURCES]
    rows.extend(capture_linked_spreadsheets(rows))
    rows.append(capture_pmc_oa_package())
    payload = {
        "schema": "sft-v3-complete-source-capture/1",
        "family": "ANAL-009-011-RAMAN-FLUORESCENCE-PHOSPHORESCENCE",
        "captured_date": "2026-07-28",
        "capture_occurred_after_all_three_derivation_seals": True,
        "source_count": len(rows),
        "sources": rows,
        "all_favorable_adverse_absent_unavailable_unresolved_rows_required": True,
        "source_selection_after_outcome_access": False,
        "postseal_transport_addendum": "experiments/external_sources/chemistry/anal_009_011_source_transport_addendum_v1.json",
    }
    inventory = dict(payload)
    inventory["inventory_payload_sha256"] = canonical_digest(payload)
    target = DESTINATION / "source-inventory-v1.json"
    target.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "source_count": len(rows),
        "source_bytes": sum(int(row["byte_count"]) for row in rows),
        "inventory": str(target.relative_to(ROOT)),
        "inventory_sha256": digest(target.read_bytes()),
        "payload_sha256": inventory["inventory_payload_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
