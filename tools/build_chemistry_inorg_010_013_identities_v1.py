#!/usr/bin/env python3
"""Build the value-free target identities for Chemistry INORG-010--013."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1"

SPECS = {
    "010": {
        "claim_id": "SFT-CHEM-ORGANOMETALLIC-METAL-CARBON-BOND-010",
        "obligation_id": "SFT-CHEM-OBL-INORG-010",
        "source": ("IUPAC-O04328", "organometallic compounds", "iupac-o04328.json", "sha256:4642e880dd8d36af4ddf5684a3e4597da2306919b80f6cef10ee7c05706a108c", "development_observed"),
        "roles": (
            "direct-metal-carbon-bond-criterion", "positive-metal-and-carbon-incidence-cardinality",
            "traditional-metal-and-semimetal-centre-scope", "expanded-boron-silicon-arsenic-selenium-centre-scope",
            "iodo-methyl-magnesium-example", "diethylmagnesium-example", "butyllithium-example",
            "chloro-ethoxycarbonylmethyl-zinc-example", "lithium-dimethylcuprate-example", "triethylborane-example",
            "delocalized-anion-context-boundary", "absence-of-direct-carbon-metal-evidence-exclusion",
        ),
    },
    "011": {
        "claim_id": "SFT-CHEM-ORGANOMETALLIC-ELECTRON-ACCOUNTING-011",
        "obligation_id": "SFT-CHEM-OBL-INORG-011",
        "source": ("IUPAC-E01913", "eighteen-electron rule", "iupac-e01913.json", "sha256:a9f66a6e8dcdecd013f4a320e7085df5743d770904421abdd5d370be4ce93b6e", "identity_only_unopened"),
        "roles": (
            "stable-diamagnetic-transition-metal-complex-scope", "nonbonded-metal-electron-account",
            "metal-ligand-bond-electron-account", "complete-eighteen-electron-total-and-octet-analogy",
        ),
    },
    "012": {
        "claim_id": "SFT-CHEM-OXIDATIVE-ADDITION-REDUCTIVE-ELIMINATION-012",
        "obligation_id": "SFT-CHEM-OBL-INORG-012",
        "sources": (
            ("IUPAC-O04367", "oxidative addition", "iupac-o04367.json", "sha256:976736625deeff512942168807eca813a99353ff8c8a7172f421887a543bcfd2", "development_observed", (
                "metal-complex-covalent-bond-insertion", "single-metal-two-electron-transfer", "two-metal-one-electron-each-transfer", "radical-chemistry-scope-distinction",
            )),
            ("IUPAC-R05223", "reductive elimination", "iupac-r05223.json", "sha256:ac12ca065ec50b342edf2d410d208d8e71c14bdc3d3512b9b8b6d2e4eb94a483", "development_observed", ("reverse-of-oxidative-addition",)),
        ),
    },
    "013": {
        "claim_id": "SFT-CHEM-INSERTION-ELIMINATION-PATHWAY-013",
        "obligation_id": "SFT-CHEM-OBL-INORG-013",
        "sources": (
            ("IUPAC-M03924", "migratory insertion", "iupac-m03924.json", "sha256:d5a3876c567c665359be5592e3720d8085e1c8eb82565bc21727be571f791d1a", "development_observed", (
                "migration-plus-insertion-composition", "organometallic-primary-use-scope",
            )),
            ("IUPAC-I03058", "insertion", "iupac-i03058.json", "sha256:d89a322c19e7438fdca4cf9e027521b0994574aadc5c4d920c704ad63aef368e", "identity_only_unopened", (
                "xz-plus-y-to-xyz-transformation", "connecting-group-replaces-xz-bond", "carbene-example-introduced-with-rendered-structure-absent", "host-crystal-lattice-scope-distinction",
            )),
            ("IUPAC-E02038", "elimination", "iupac-e02038.json", "sha256:0c0ccf2845dbf936369bf0c5b35fb1e59ceea70736cc250c43ff56bc024cc57d", "identity_only_unopened", (
                "reverse-of-addition", "two-groups-lost-from-distinct-centres", "unsaturation-or-new-ring-product", "single-centre-carbene-product-boundary",
            )),
        ),
    },
}


def rows_for(number: str, spec: dict) -> list[dict]:
    sources = spec.get("sources")
    if sources is None:
        source_id, identity, filename, digest, custody = spec["source"]
        sources = ((source_id, identity, filename, digest, custody, spec["roles"]),)
    rows = []
    for source_id, identity, filename, digest, custody, roles in sources:
        for role in roles:
            rows.append({
                "target_id": f"SFT-CHEM-INORG-{number}-{len(rows) + 1:03d}",
                "source_record_ordinal": len(rows) + 1,
                "source_id": source_id,
                "authority": "IUPAC",
                "registered_identity": identity,
                "source_record_role": role,
                "custody_class": "family-" + custody.replace("_", "-"),
                "snapshot_path": f"{SNAPSHOT_ROOT}/{filename}",
                "snapshot_sha256": digest,
            })
    return rows


def main() -> None:
    output_root = ROOT / "experiments/external_sources/chemistry"
    for number, spec in SPECS.items():
        rows = rows_for(number, spec)
        payload = {
            "schema": "sft-v3-value-free-target-identities/1",
            "claim_id": spec["claim_id"],
            "obligation_id": spec["obligation_id"],
            "family_boundary": "SFT-CHEM-FAMILY-INORG-004-017",
            "selection_rule": "Every separately registered definition, example, scope, adverse, absent or correspondence surface assigned to this obligation is retained in source and surface order.",
            "complete_registered_target_count": len(rows),
            "target_definitions_examples_values_outcomes_presence_flags_or_payload_hashes_present": False,
            "rows": rows,
        }
        path = output_root / f"inorg_{number}_target_identities_v1.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(path.relative_to(ROOT), len(rows))


if __name__ == "__main__":
    main()
