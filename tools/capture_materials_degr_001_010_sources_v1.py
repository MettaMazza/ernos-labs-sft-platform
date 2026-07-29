#!/usr/bin/env python3
"""Capture all registered DEGR sources after the target registry is sealed."""

from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/materials_degr_001_010_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/materials/degr_001_010_v1"
REMOTE = (
    ("NIST-OXIDE-GROWTH", "https://www.nist.gov/publications/atomic-scale-mechanism-unidirectional-oxide-growth", "nist-oxide-growth.html"),
    ("NIST-ELECTROCHEMICAL-CORROSION", "https://www.nist.gov/publications/electrochemical-characterization-and-immersion-corrosion-consolidated-silver-dental", "nist-electrochemical-corrosion.html"),
    ("NIST-LOCALIZED-CORROSION-RESISTANCE", "https://www.nist.gov/publications/enhanced-localized-corrosion-resistance-ni-based-alloy-625-processed-directed-energy", "nist-localized-corrosion-resistance.html"),
    ("NIST-STRESS-CORROSION-CRACK", "https://www.nist.gov/publications/modeling-influence-crack-path-deviations-propagation-stress-corrosion-cracks", "nist-stress-corrosion-crack.html"),
    ("NIST-HYDROGEN-UPTAKE-EMBRITTLEMENT", "https://www.nist.gov/publications/effects-al-si-coating-and-zn-coating-hydrogen-uptake-and-embrittlement-ultra-high", "nist-hydrogen-uptake-embrittlement.html"),
    ("NIST-MULTIAXIAL-WEAR", "https://www.nist.gov/publications/novel-multiaxial-wear-tester-accelerated-testing-materials", "nist-multiaxial-wear.html"),
    ("NIST-UV-RADIATION-DAMAGE", "https://www.nist.gov/publications/characterization-uv-induced-radiation-damage-si-based-photodiodes-0", "nist-uv-radiation-damage.html"),
    ("NIST-PHYSICAL-AGEING-RECOVERY", "https://www.nist.gov/publications/hygrothermal-effects-physical-aging-and-structural-recovery-epoxy-thermoset", "nist-physical-ageing-recovery.html"),
    ("NIST-WEATHER-MATERIAL-RESPONSE", "https://www.nist.gov/publications/evaluating-weather-factors-and-material-response-during-outdoor-exposure-determine", "nist-weather-material-response.html"),
    ("NIST-SERVICE-LIFE-BOUNDARY", "https://www.nist.gov/publications/service-life-prediction-why-so-hard", "nist-service-life-boundary.html"),
)


def digest(body):
    return "sha256:" + sha256(body).hexdigest()


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    registry_bytes = REGISTRY.read_bytes()
    registry = json.loads(registry_bytes)
    if registry["target_count"] != 10 or registry["target_content_present"] is not False:
        raise SystemExit("DEGR registry changed")
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    OUT.mkdir(parents=True)
    documents = []
    for source_id, url, name in REMOTE:
        request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"})
        with urlopen(request, timeout=120) as response:
            body = response.read()
            status = getattr(response, "status", 200)
            content_type = response.headers.get("Content-Type", "unreported")
        if status != 200 or len(body) < 1000:
            raise SystemExit(f"DEGR capture halt {source_id} {status} {len(body)}")
        path = OUT / name
        path.write_bytes(body)
        documents.append({
            "source_id": source_id,
            "source_uri": url,
            "snapshot_path": path.relative_to(ROOT).as_posix(),
            "snapshot_hash": digest(body),
            "byte_count": len(body),
            "http_status": status,
            "content_type": content_type,
            "status": "captured_post_registry",
            "used_for_favourable_comparison": True,
        })
    registered = {source_id for target in registry["targets"] for source_id in target["source_identities"]}
    if registered != {document["source_id"] for document in documents}:
        raise SystemExit("DEGR source mismatch")
    manifest = {
        "schema": "sft-v3-materials-degr-source-custody/1",
        "target_registry_path": REGISTRY.relative_to(ROOT).as_posix(),
        "target_registry_hash": digest(registry_bytes),
        "target_registry_identity": registry["registry_identity"],
        "documents": documents,
        "document_count": len(documents),
        "captured_count": len(documents),
        "unavailable_count": 0,
        "all_registered_source_identities_accounted_for": True,
        "all_result_classes_retained": True,
        "target_or_outcome_selected_source": False,
    }
    manifest["manifest_identity"] = canonical(manifest)
    (OUT / "source_custody_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"documents": len(documents), "identity": manifest["manifest_identity"]}, indent=2))


if __name__ == "__main__":
    main()
