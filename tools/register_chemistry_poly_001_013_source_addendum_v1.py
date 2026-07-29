#!/usr/bin/env python3
"""Register supplementary Polymer measurement identities before capture."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "experiments/external_sources/chemistry/poly_001_013_quantitative_source_addendum_v1.json"
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/poly-001-013-quantitative-addendum-v1"


SOURCES = (
    {
        "source_id": "NIST-STOCHASTIC-PHOTOPOLYMER-NETWORK-GROWTH",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://www.nist.gov/programs-projects/stochastic-network-growth-simulation-photopolymerization",
        "capture_url": "https://www.nist.gov/programs-projects/stochastic-network-growth-simulation-photopolymerization",
        "purpose": "initiation, propagation, crosslinking, conversion, network structure and kinetics custody",
    },
    {
        "source_id": "NIST-RING-OPENING-COPOLYMER-SEQUENCE",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=911008",
        "capture_url": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=911008",
        "purpose": "quantitative monomer composition, dyad/triad sequence distribution and conversion boundary",
    },
    {
        "source_id": "NIST-MONODISPERSE-PAMS-KINETIC-NETWORK",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://nvlpubs.nist.gov/nistpubs/jres/83/jresv83n4p371_A1b.pdf",
        "capture_url": "https://nvlpubs.nist.gov/nistpubs/jres/83/jresv83n4p371_A1b.pdf",
        "purpose": "complete initiation, propagation, transfer, termination, conversion and molecular-size kinetic record",
    },
    {
        "source_id": "NIST-QUINTUPLE-DETECTOR-COPOLYMER",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://www.nist.gov/publications/characterization-copolymers-and-blends-quintuple-detector-size-exclusion-chromatography",
        "capture_url": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=910004",
        "purpose": "complete copolymer composition, molecular-size distribution, sequence regime, conformation and cross-method record",
    },
    {
        "source_id": "NIST-PRECISION-DEUTERATED-POLYETHYLENE",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://www.nist.gov/publications/precision-tunable-deuterated-polyethylene-polyhomologation",
        "capture_url": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=926318",
        "purpose": "statistical and triblock sequence identities, composition, chain ends and narrow-distribution record",
    },
    {
        "source_id": "NIST-CROSSLINKED-PHOTOPOLYMER-CONVERSION",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=852833",
        "capture_url": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=852833",
        "purpose": "complete composition, conversion, crosslink, viscosity, phase and property vector",
    },
)


def sha(path: Path) -> str:
    import hashlib
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUTPUT.exists() or SNAPSHOT.exists():
        raise SystemExit("Polymer quantitative source addendum already exists")
    seals = []
    for value in range(1, 14):
        path = ROOT / f"experiments/sealed_predictions/chemistry_poly_{value:03d}_pre_source_v1.json"
        if not path.is_file():
            raise SystemExit("all original Polymer seals are required")
        seals.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path)})
    payload = {
        "schema": "sft-v3-postseal-source-identity-addendum/1",
        "family": "POLY-001-013-QUANTITATIVE-POLYMER-CHEMISTRY",
        "registered_date": "2026-07-28",
        "registered_before_addendum_capture": True,
        "reason": "The initial registered corpus did not supply the full quantitative chain-growth, step-growth and copolymer sequence surfaces required by the frozen POLY obligations. This addendum strengthens those tests without changing any law, candidate, survivor, original target identity or original seal.",
        "discovery_exposure_disclosure": "Search-result summaries exposed broad mechanisms, named variables and selected values including copolymer reactivity ratios, a historical shrinkage percentage, qualitative conversion findings and the existence of initiation/propagation/transfer/termination rows. Complete source files, tables, figures and claim comparison vectors remained unopened before this addendum registration. No exposed value, equation, model or outcome may select or alter a native law.",
        "values_or_outcomes_allowed_to_select_native_law": False,
        "original_seals": seals,
        "sources": SOURCES,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(f"registered {len(SOURCES)} post-seal source identities: {sha(OUTPUT)}")


if __name__ == "__main__":
    main()
