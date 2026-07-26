#!/usr/bin/env python3
"""Prepare local Zenodo metadata for the ordered results-first paper patches."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

UPDATES = {
    "publication/zenodo_metadata.json": (
        "0.2.0",
        "<p><strong>There Is No Nothing, Methods Paper 00 version 0.2.0</strong>, preserves the two inaugural premise-free results and updates the methods record with the branch-paper series enabled by its public fail-closed admission constitution. Later branch laws remain separate admissions and are not retroactive premises.</p>",
    ),
    "publications/successors/foundation/zenodo_metadata.json": (
        "1.2.0",
        "<p><strong>Foundation Branch Paper 001, version 1.2.0</strong>, preserves the complete sixteen-theorem Foundation record while placing its exact discoveries, meaning, authorship, open-science mission and admission boundary before artifact identities. The 5,222 candidate decisions, 64 adverse controls, 16 independent reproductions and 32/32 prior obligations are unchanged.</p>",
    ),
    "publication/mathematics_zenodo_metadata.json": (
        "1.3.0",
        "<p><strong>Mathematics Branch Paper 001, version 1.3.0</strong>, preserves the complete version 1.2 mathematical-foundations and Smithian Fold Scientific Calculator evidence while placing the exact discoveries, their meaning and the Ernos Labs public-science standard before artifact identities.</p>",
    ),
    "publication/information_science_zenodo_metadata.json": (
        "1.2.0",
        "<p><strong>Information Science Branch Paper 001, version 1.2.0</strong>, preserves the complete twelve-law and 77-obligation scientific record while front-loading the exact distinction, entropy, capacity, coding and deterministic-probability results and the integrated Ernos Labs public-science standard.</p>",
    ),
    "publication/computation_zenodo_metadata.json": (
        "1.2.0",
        "<p><strong>After Turing: The Fold Machine, version 1.2.0</strong>, preserves the exhaustive Classical Computation derivation while integrating its exact native-model headline theorems with Maria Smith's authorship, the Ernos Labs public-science mission and the precise boundary between unrestricted criticism and machine-checked scientific admission.</p>",
    ),
    "publication/quantum_computation_zenodo_metadata.json": (
        "1.2.0",
        "<p><strong>The Quantum Fold Machine, version 1.2.0</strong>, preserves the exhaustive Reversible and Quantum Computation derivation while integrating its exact structural and unbounded positive-finite fault-order results with Maria Smith's authorship and the Ernos Labs public-science constitution.</p>",
    ),
    "publication/chemistry_zenodo_metadata.json": (
        "1.1.0",
        "<p><strong>From Fold to Chemistry, version 1.1.0</strong>, preserves all 86 chemical derivations while placing the exact orbit capacities, nuclear closures, g-block, Smithium and endpoint results first and integrating Maria Smith's authorship and the Ernos Labs public-science constitution at full weight.</p>",
    ),
    "publication/materials_zenodo_metadata.json": (
        "1.1.0",
        "<p><strong>From Fold to Materials, version 1.1.0</strong>, preserves all 84 Materials Science derivations while placing the exact six-neighbour, crystallographic-order, seven-system, fourteen-Bravais and three-acoustic-branch results first and integrating Maria Smith's authorship and the Ernos Labs public-science constitution at full weight.</p>",
    ),
    "publication/physics_zenodo_metadata.json": (
        "1.1.0",
        "<p><strong>From Fold to Physics, version 1.1.0</strong>, reports the complete current 349-claim Physics reconstruction led by the exact first-principles result alpha^-1 = 503846395469/3676744786 = 137.035999177180855..., sealed and validated inside the complete CODATA 2022 interval.</p>",
    ),
}

FINAL_RELEASES = {
    "publication/zenodo_metadata.json": ("10.5281/zenodo.21591160", 21591160, "10.5281/zenodo.21514890"),
    "publications/successors/foundation/zenodo_metadata.json": ("10.5281/zenodo.21591169", 21591169, "10.5281/zenodo.21535636"),
    "publication/mathematics_zenodo_metadata.json": ("10.5281/zenodo.21591170", 21591170, "10.5281/zenodo.21558279"),
    "publication/information_science_zenodo_metadata.json": ("10.5281/zenodo.21591171", 21591171, "10.5281/zenodo.21536202"),
    "publication/computation_zenodo_metadata.json": ("10.5281/zenodo.21591174", 21591174, "10.5281/zenodo.21536437"),
    "publication/quantum_computation_zenodo_metadata.json": ("10.5281/zenodo.21591175", 21591175, "10.5281/zenodo.21536581"),
    "publication/physics_zenodo_metadata.json": ("10.5281/zenodo.21548363", 21548363, "10.5281/zenodo.21520881"),
}


def main() -> None:
    for relative, (version, first_paragraph) in UPDATES.items():
        path = ROOT / relative
        payload = json.loads(path.read_text(encoding="utf-8"))
        metadata = payload["metadata"]
        prior_description = metadata["description"]
        remainder = prior_description.split("</p>", 1)[1] if "</p>" in prior_description else ""
        metadata["description"] = first_paragraph + remainder
        metadata["version"] = version
        metadata["publication_date"] = "2026-07-26"
        if relative in FINAL_RELEASES:
            doi, draft_id, predecessor = FINAL_RELEASES[relative]
            payload["doi"] = doi
            payload["zenodo_draft_id"] = draft_id
            payload["publication_authorized"] = True
            related = [
                row for row in metadata.get("related_identifiers", [])
                if row.get("relation") != "isNewVersionOf"
            ]
            related.append({"identifier": predecessor, "relation": "isNewVersionOf", "scheme": "doi"})
            metadata["related_identifiers"] = related
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"prepared {relative} version {version}")


if __name__ == "__main__":
    main()
