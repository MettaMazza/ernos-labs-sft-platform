#!/usr/bin/env python3
"""Open the frozen INORG-010--013 IUPAC outcomes after identity sealing."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402
IDENTITY_HASHES = {
    "010": "sha256:7262a7a2b3940d00812151560d243a6362bbca4edaebac98d3a67c7072c44f1d",
    "011": "sha256:a439259572b5ea2b89ca4d9b46e659a915e717920f5ff5702862872bd5aa4782",
    "012": "sha256:a103ace65a1351b493859a403b0bbb564fdea57d8299b930a5a7a959ed48f06e",
    "013": "sha256:62bdd91e56629d4c841657ea94e339dd49b00913f11e58dbb73c67537ef46fa1",
}

SURFACES = {
    "direct-metal-carbon-bond-criterion": (1, "bonds between one or more metal atoms and one or more carbon atoms"),
    "positive-metal-and-carbon-incidence-cardinality": (1, "one or more metal atoms and one or more carbon atoms"),
    "traditional-metal-and-semimetal-centre-scope": (1, "traditional metals and semimetals"),
    "expanded-boron-silicon-arsenic-selenium-centre-scope": (1, "boron, silicon, arsenic and selenium"),
    "iodo-methyl-magnesium-example": (1, "MeMgI"),
    "diethylmagnesium-example": (1, "Et2Mg"),
    "butyllithium-example": (1, "BuLi"),
    "chloro-ethoxycarbonylmethyl-zinc-example": (1, "ClZnCH2C(=O)OEt"),
    "lithium-dimethylcuprate-example": (1, "CuMe2"),
    "triethylborane-example": (1, "Et3B"),
    "delocalized-anion-context-boundary": (1, "may vary with the nature of the anionic moiety"),
    "absence-of-direct-carbon-metal-evidence-exclusion": (1, "absence of direct structural evidence for a carbon–metal bond"),
    "stable-diamagnetic-transition-metal-complex-scope": (1, "stable diamagnetic transition metal complexes"),
    "nonbonded-metal-electron-account": (1, "number of nonbonded electrons at the metal"),
    "metal-ligand-bond-electron-account": (1, "number of electrons in the metal-ligand bonds"),
    "complete-eighteen-electron-total-and-octet-analogy": (1, "should be 18"),
    "metal-complex-covalent-bond-insertion": (1, "insertion of a metal complex into a covalent bond"),
    "single-metal-two-electron-transfer": (1, "two-electron loss on one metal"),
    "two-metal-one-electron-each-transfer": (1, "one-electron loss on each of two metals"),
    "radical-chemistry-scope-distinction": (1, "In radical chemistry"),
    "reverse-of-oxidative-addition": (1, "reverse of oxidative addition"),
    "migration-plus-insertion-composition": (1, "combination of migration and insertion"),
    "organometallic-primary-use-scope": (1, "mainly used in organometallic chemistry"),
    "xz-plus-y-to-xyz-transformation": (1, "X-Z + Y -> X-Y-Z"),
    "connecting-group-replaces-xz-bond": (1, "connecting atom or group"),
    "carbene-example-introduced-with-rendered-structure-absent": (1, "An example is the carbene insertion reaction"),
    "host-crystal-lattice-scope-distinction": (2, "host crystal lattice"),
    "reverse-of-addition": (1, "reverse of an addition reaction or transformation"),
    "two-groups-lost-from-distinct-centres": (1, "two groups (called eliminands) are lost"),
    "unsaturation-or-new-ring-product": (1, "formation of an unsaturation"),
    "single-centre-carbene-product-boundary": (1, "lost from a single centre"),
}


def main() -> None:
    external_root = ROOT / "experiments/external_sources/chemistry"
    snapshot_root = external_root / "snapshots/inorg-004-017-family-v1"
    for number, expected_hash in IDENTITY_HASHES.items():
        identity_path = external_root / f"inorg_{number}_target_identities_v1.json"
        if hash_file(identity_path) != expected_hash:
            raise SystemExit(f"INORG-{number} identity seal changed")
        identity = json.loads(identity_path.read_text(encoding="utf-8"))
        source_cache = {}
        target_rows = []
        for row in identity["rows"]:
            path = ROOT / row["snapshot_path"]
            if hash_file(path) != row["snapshot_sha256"]:
                raise SystemExit(f"INORG-{number} frozen source changed: {path}")
            document = source_cache.setdefault(str(path), json.loads(path.read_text(encoding="utf-8")))
            definition_ordinal, phrase = SURFACES[row["source_record_role"]]
            term = document["term"]
            definition = term["definitions"][definition_ordinal - 1]["text"]
            outcome = {
                "source_title": term["title"],
                "source_code": term["code"],
                "source_status": term["status"],
                "definition_ordinal": definition_ordinal,
                "complete_definition_text": definition,
                "registered_surface_phrase": phrase,
                "registered_surface_present": phrase.casefold() in definition.casefold(),
                "citation": term["citation"],
                "licence": term["license"],
                "disclaimer": term["disclaimer"],
            }
            if row["source_record_role"] == "carbene-example-introduced-with-rendered-structure-absent":
                outcome["introduced_example_structure_present_after_colon"] = bool(definition.split("reaction:", 1)[-1].strip())
            target = {**row, "source_outcome": outcome}
            target["target_payload_hash"] = sha256_identity((row["target_id"], row["source_record_role"], outcome))
            target_rows.append(target)
        target_payload = {
            "schema": "sft-v3-postseal-complete-target-vector/1",
            "claim_id": identity["claim_id"],
            "identity_registry": (str(identity_path.relative_to(ROOT)), expected_hash),
            "release_requires_prediction_seal": True,
            "complete_registered_target_count": len(target_rows),
            "all_favourable_adverse_absent_scope_and_unresolved_rows_preserved": True,
            "rows": target_rows,
        }
        target_path = external_root / f"inorg_{number}_withheld_targets_v1.json"
        target_path.write_text(json.dumps(target_payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        analysis = {
            "complete_target_count": len(target_rows),
            "complete_source_count": len({row["source_id"] for row in target_rows}),
            "all_registered_surfaces_present": all(row["source_outcome"]["registered_surface_present"] for row in target_rows),
            "development_observed_target_count": sum("development-observed" in row["custody_class"] for row in target_rows),
            "identity_only_unopened_target_count": sum("identity-only-unopened" in row["custody_class"] for row in target_rows),
            "scope_distinction_count": sum("scope-distinction" in row["source_record_role"] or "context-boundary" in row["source_record_role"] for row in target_rows),
            "explicit_exclusion_count": sum("exclusion" in row["source_record_role"] for row in target_rows),
            "rendered_structure_absence_count": sum(row["source_outcome"].get("introduced_example_structure_present_after_colon") is False for row in target_rows),
            "complete_target_vector_hash": sha256_identity(tuple((row["target_id"], row["source_outcome"]) for row in target_rows)),
            "source_recapture_count": 0,
            "all_rows_preserved": True,
        }
        primary = {
            "schema": "sft-v3-postseal-primary-analysis/1",
            "claim_id": identity["claim_id"],
            "identity_registry": (str(identity_path.relative_to(ROOT)), expected_hash),
            "target_registry": (str(target_path.relative_to(ROOT)), hash_file(target_path)),
            "exact_postseal_analysis": analysis,
        }
        primary_path = snapshot_root / f"inorg-{number}-primary-records-v1.json"
        primary_path.write_text(json.dumps(primary, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        print(target_path.relative_to(ROOT), hash_file(target_path))
        print(primary_path.relative_to(ROOT), hash_file(primary_path))


if __name__ == "__main__":
    main()
