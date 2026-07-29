#!/usr/bin/env python3
"""Freeze value-free authoritative targets for Biology MOLX-001--014."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/biology_molx_001_014_target_registry_v1.json"

ROWS = (
    ("001", "SFT-BIO-MOLX-REACTION-BALANCE-001", "biological reaction equation, participant identity, direction and exact stoichiometric balance", ("RHEA-CURATED-REACTION-SERVICE", "CHEBI-CURATED-CHEMICAL-IDENTITIES")),
    ("002", "SFT-BIO-MOLX-ENZYME-SPECIFICITY-002", "reviewed enzyme, substrate, product and catalytic-activity correspondence", ("UNIPROTKB-REVIEWED-ENZYME-RECORD", "RHEA-CATALYTIC-ACTIVITY-XREF")),
    ("003", "SFT-BIO-MOLX-ENZYME-FINITE-THROUGHPUT-003", "experimental enzyme-rate, substrate-range and inhibitor-condition record", ("SABIO-RK-CURATED-KINETIC-RECORD", "BRENDA-PRIMARY-LITERATURE-IDENTITY")),
    ("004", "SFT-BIO-MOLX-REDOX-CARRIER-004", "curated biological redox reaction with donor, acceptor and transferred carrier identities", ("RHEA-CURATED-REDOX-REACTION", "UNIPROTKB-REVIEWED-OXIDOREDUCTASE")),
    ("005", "SFT-BIO-MOLX-COUPLED-WORK-005", "curated ATP-coupled biological reaction and retained participant ledger", ("RHEA-CURATED-ATP-COUPLED-REACTION", "UNIPROTKB-REVIEWED-ATPASE")),
    ("006", "SFT-BIO-MOLX-CHEMIOSMOTIC-TRANSPORT-006", "membrane-side, ion-gradient, transport-route and coupled-product observation", ("UNIPROTKB-REVIEWED-ATP-SYNTHASE", "PDB-EXPERIMENTAL-ATP-SYNTHASE-STRUCTURE")),
    ("007", "SFT-BIO-MOLX-CARBON-FIXATION-007", "curated carbon-fixation reaction with source carbon and product identities retained", ("RHEA-CURATED-CARBON-FIXATION-REACTION", "UNIPROTKB-REVIEWED-CARBON-FIXATION-ENZYME")),
    ("008", "SFT-BIO-MOLX-CARBON-BRANCH-ALLOCATION-008", "isotope-resolved central-carbon branch allocation with inputs, products, condition and uncertainty", ("METABOLOMICS-WORKBENCH-CURATED-ISOTOPE-STUDY", "METABOLIGHTS-CURATED-FLUX-STUDY")),
    ("009", "SFT-BIO-MOLX-NUTRIENT-CYCLE-009", "biological nitrogen, sulfur and phosphorus transformation routes and carrier conservation", ("RHEA-CURATED-NUTRIENT-REACTIONS", "QUICKGO-CURATED-NUTRIENT-PROCESSES")),
    ("010", "SFT-BIO-MOLX-LIPID-LIFECYCLE-010", "lipid identity, synthesis, membrane incorporation, remodelling and degradation records", ("LIPID-MAPS-CURATED-STRUCTURE-DATABASE", "RHEA-CURATED-LIPID-REACTIONS")),
    ("011", "SFT-BIO-MOLX-CARBOHYDRATE-STORAGE-011", "curated carbohydrate synthesis, storage and mobilization reactions", ("RHEA-CURATED-CARBOHYDRATE-REACTIONS", "UNIPROTKB-REVIEWED-GLYCOGEN-ENZYME")),
    ("012", "SFT-BIO-MOLX-AMINO-ACID-ROUTING-012", "curated amino-acid transformation with nitrogen and carbon-skeleton fate", ("RHEA-CURATED-AMINOTRANSFER-REACTION", "UNIPROTKB-REVIEWED-AMINOTRANSFERASE")),
    ("013", "SFT-BIO-MOLX-COFACTOR-DEPENDENCE-013", "reviewed cofactor-dependent catalytic record and cofactor identity", ("UNIPROTKB-REVIEWED-COFACTOR-ANNOTATION", "RHEA-COFACTOR-PARTICIPANT-RECORD")),
    ("014", "SFT-BIO-MOLX-METABOLOME-FLUX-CUSTODY-014", "source-bound metabolomics study with detected, missing, uncertain and condition-specific records", ("METABOLOMICS-WORKBENCH-CURATED-STUDY", "METABOLIGHTS-CURATED-STUDY")),
)


def canonical(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + sha256(raw).hexdigest()


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing to overwrite frozen Biology MOLX registry")
    payload = {
        "schema": "sft-v3-biology-molx-target-identities/1",
        "authority": "Maria Smith",
        "date": "2026-07-29",
        "family": "living_biochemistry_and_molecular_processes",
        "selection_rule": "All fourteen obligations, comparison classes and authoritative source identities are frozen as one whole subfield before external outcome extraction.",
        "custody_disclosure": "The registry contains source identities and target classes only; it contains no measured value, source fragment, candidate, survivor or comparison outcome.",
        "targets": [
            {
                "obligation_id": f"SFT-BIO-OBL-MOLX-{number}",
                "claim_id": claim_id,
                "target_class": target,
                "source_identities": list(sources),
            }
            for number, claim_id, target, sources in ROWS
        ],
        "target_count": len(ROWS),
        "all_family_members_registered": True,
        "target_content_present": False,
        "survivor_identity_present": False,
        "measured_value_present": False,
        "outcome_present": False,
        "failed_route_retires_obligation": False,
    }
    payload["registry_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"target_count": len(ROWS), "registry_identity": payload["registry_identity"]}, indent=2))


if __name__ == "__main__":
    main()
