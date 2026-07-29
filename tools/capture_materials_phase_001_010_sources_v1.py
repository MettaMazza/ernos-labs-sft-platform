#!/usr/bin/env python3
"""Capture the complete preregistered PHASE-001--010 authoritative source set."""

from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/materials_phase_001_010_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/materials/phase_001_010_v1"


REMOTE = (
    ("NIST-LEVER-RULE-SOLIDIFICATION", "https://www.ctcms.nist.gov/~kattner/solidifc/lever.html", "nist-lever-rule-solidification.html"),
    ("NIST-LLE-TERNARY-TIE-LINES", "https://trc.nist.gov/TDE/Help/TDE103b/The_Navigation_Tree/Navigation_Tree_%28Mixtures%29/LLEDataSummary_View-Ternary.htm", "nist-lle-ternary-tie-lines.html"),
    ("NIST-SAT-TMMC-COEXISTENCE", "https://www.nist.gov/mml/csd/chemical-informatics-group/sat-tmmc-liquid-vapor-coexistence-properties-linear-force-0", "nist-sat-tmmc-coexistence.html"),
    ("NIST-ORDER-DISORDER-SEPARATION", "https://www.nist.gov/publications/order-disorder-and-phase-separation", "nist-order-disorder-separation.html"),
    ("NIST-BINARY-HALIDE-TRANSFORMATIONS", "https://nvlpubs.nist.gov/nistpubs/Legacy/NSRDS/nbsnsrds41.pdf", "nist-binary-halide-transformations.pdf"),
    ("NIST-MARTENSITIC-MATERIALS-STUDY", "https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nbsir83-1690.pdf", "nist-martensitic-materials-study.pdf"),
    ("NIST-PHASE-TRANSITION-TEMPERATURES", "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=958924", "nist-phase-transition-temperatures-2025.pdf"),
)


EXISTING = (
    ("NIST-TEXTURE-PHASE-FRACTION", "https://www.nist.gov/publications/quantitative-texture-and-phase-fraction-analysis-diffraction-data", "experiments/external_sources/materials/snapshots/nist-texture-phase-fraction.html"),
    ("NIST-LIQUID-WATER-METASTABLE", "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=905052", "experiments/external_sources/materials/snapshots/nist-liquid-water-properties-2026-07-27.pdf"),
    ("NIST-GLASS-TRANSITION", "https://www.nist.gov/publications/glass-transition-its-measurement-and-underlying-physics", "experiments/external_sources/materials/snapshots/nist-glass-transition.html"),
    ("NIST-SOLIDIFICATION", "https://www.nist.gov/programs-projects/solidification", "experiments/external_sources/materials/snapshots/nist-solidification.html"),
)


def digest(body):
    return "sha256:" + sha256(body).hexdigest()


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def fetch(uri):
    request = Request(uri, headers={"User-Agent": "Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"})
    with urlopen(request, timeout=120) as response:
        body = response.read()
        return body, getattr(response, "status", 200), response.headers.get("Content-Type", "unreported")


def main():
    registry_bytes = REGISTRY.read_bytes()
    registry = json.loads(registry_bytes)
    if registry["target_count"] != 10 or registry["target_content_present"] is not False:
        raise SystemExit("PHASE capture halted: target registry changed")
    if OUT.exists():
        raise SystemExit("refusing to overwrite PHASE source custody")
    OUT.mkdir(parents=True)
    documents = []
    for source_id, uri, filename in REMOTE:
        body, status, content_type = fetch(uri)
        if status != 200 or len(body) < 1000:
            raise SystemExit(f"PHASE capture halted: {source_id} returned {status} and {len(body)} bytes")
        path = OUT / filename
        path.write_bytes(body)
        documents.append({"source_id": source_id, "source_uri": uri, "snapshot_path": path.relative_to(ROOT).as_posix(), "snapshot_hash": digest(body), "byte_count": len(body), "http_status": status, "content_type": content_type, "status": "captured_post_registry", "used_for_favourable_comparison": True})
    for source_id, uri, relative in EXISTING:
        path = ROOT / relative
        body = path.read_bytes()
        documents.append({"source_id": source_id, "source_uri": uri, "snapshot_path": relative, "snapshot_hash": digest(body), "byte_count": len(body), "http_status": "preexisting", "content_type": "preserved-official-snapshot", "status": "captured_preexisting_official_snapshot", "used_for_favourable_comparison": True})
    registered = {source for target in registry["targets"] for source in target["source_identities"]}
    captured = {row["source_id"] for row in documents}
    if registered != captured:
        raise SystemExit(f"PHASE capture halted: source identity mismatch missing={sorted(registered-captured)} extra={sorted(captured-registered)}")
    payload = {
        "schema": "sft-v3-materials-phase-source-custody/1",
        "target_registry_path": REGISTRY.relative_to(ROOT).as_posix(),
        "target_registry_hash": digest(registry_bytes),
        "target_registry_identity": registry["registry_identity"],
        "documents": documents,
        "document_count": len(documents),
        "captured_count": len(documents),
        "unavailable_count": 0,
        "all_registered_source_identities_accounted_for": True,
        "all_favourable_adverse_absent_unavailable_unresolved_rows_retained": True,
    }
    payload["manifest_identity"] = canonical(payload)
    (OUT / "source_custody_manifest.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"document_count": len(documents), "manifest_identity": payload["manifest_identity"]}, indent=2))


if __name__ == "__main__":
    main()
