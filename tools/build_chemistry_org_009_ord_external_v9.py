#!/usr/bin/env python3
"""Open all sealed ORD products and exhaust exact addition correspondences."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq
from ord_schema.proto import reaction_pb2
from rdkit import Chem


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-ord-holdout-v9"
INVENTORY = SNAPSHOT_ROOT / "source-inventory-v9.json"
SELECTION = SNAPSHOT_ROOT / "source-only-selection-v9.json"
SELECTION_SEAL = ROOT / "experiments/sealed_predictions/chemistry_org_009_ord_source_selection_v9.json"
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_ord_v9.json"
OUTPUT = SNAPSHOT_ROOT / "product-comparison-v9.json"
EXPECTED = {
    INVENTORY: "sha256:a4fe3ee3452b423ae2fb41f1901767e6c6002604be73c7b75035fbeaf2a6dc03",
    SELECTION: "sha256:6320e2e258f264dee49265a1fc73463be5c8a944d53c807e855ec440bc6ba3e4",
    SELECTION_SEAL: "sha256:b909b6f46caf9b361cc0b1221b440f7898f679f2c935da379105f69359513994",
    PREDICTION: "sha256:045b5a0960e729450a6b5d0670fe3d6337c6d066c97ede3e865550b12fdf98cc",
}
SMILES_TYPES = {reaction_pb2.CompoundIdentifier.SMILES, reaction_pb2.CompoundIdentifier.CXSMILES}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def product_smiles(product) -> list[str]:
    return [identifier.value for identifier in product.identifiers if identifier.type in SMILES_TYPES and identifier.value]


def element_adjacency_query(molecule):
    query = Chem.RWMol()
    for atom in molecule.GetAtoms():
        query.AddAtom(Chem.AtomFromSmarts(f"[#{atom.GetAtomicNum()}]"))
    for bond in molecule.GetBonds():
        query.AddBond(bond.GetBeginAtomIdx(), bond.GetEndAtomIdx(), Chem.BondType.UNSPECIFIED)
    return query.GetMol()


def edge(left: int, right: int) -> tuple[int, int]:
    return tuple(sorted((left, right)))


def compare_product(selected: dict, smiles: str) -> dict:
    azide_smiles = selected["source_topology"]["azide_smiles"]
    alkyne_smiles = selected["source_topology"]["alkyne_smiles"]
    azide = Chem.MolFromSmiles(azide_smiles)
    alkyne = Chem.MolFromSmiles(alkyne_smiles)
    product = Chem.MolFromSmiles(smiles)
    if azide is None or alkyne is None or product is None:
        return {"status": "unresolved", "product_smiles": smiles, "reason": "RDKit could not parse one complete structure"}
    if azide.GetNumAtoms() + alkyne.GetNumAtoms() != product.GetNumAtoms():
        return {
            "status": "adverse",
            "product_smiles": smiles,
            "reason": "complete atom occurrence count differs",
            "source_atom_count": azide.GetNumAtoms() + alkyne.GetNumAtoms(),
            "product_atom_count": product.GetNumAtoms(),
        }
    azide_matches = product.GetSubstructMatches(element_adjacency_query(azide), uniquify=False, maxMatches=100000)
    alkyne_matches = product.GetSubstructMatches(element_adjacency_query(alkyne), uniquify=False, maxMatches=100000)
    outer = [ordinal - 1 for ordinal in selected["source_topology"]["azide_outer_atom_ordinals"]]
    alkyne_carbon = [ordinal - 1 for ordinal in selected["source_topology"]["alkyne_carbon_atom_ordinals"]]
    product_edges = {edge(bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()) for bond in product.GetBonds()}
    valid = []
    complete_bijection_count = 0
    for azide_match in azide_matches:
        azide_set = set(azide_match)
        for alkyne_match in alkyne_matches:
            alkyne_set = set(alkyne_match)
            if azide_set & alkyne_set or len(azide_set | alkyne_set) != product.GetNumAtoms():
                continue
            complete_bijection_count += 1
            cross = sorted(edge(left, right) for left, right in product_edges if (left in azide_set) != (right in azide_set))
            generated = {
                frozenset((edge(azide_match[outer[0]], alkyne_match[alkyne_carbon[0]]), edge(azide_match[outer[1]], alkyne_match[alkyne_carbon[1]]))),
                frozenset((edge(azide_match[outer[0]], alkyne_match[alkyne_carbon[1]]), edge(azide_match[outer[1]], alkyne_match[alkyne_carbon[0]]))),
            }
            source_edge_count = azide.GetNumBonds() + alkyne.GetNumBonds()
            changed = []
            for source, match, carrier in ((azide, azide_match, "azide"), (alkyne, alkyne_match, "alkyne")):
                for bond in source.GetBonds():
                    product_bond = product.GetBondBetweenAtoms(match[bond.GetBeginAtomIdx()], match[bond.GetEndAtomIdx()])
                    if product_bond is not None and product_bond.GetBondType() != bond.GetBondType():
                        changed.append({
                            "carrier": carrier,
                            "source_atom_ordinals": [bond.GetBeginAtomIdx() + 1, bond.GetEndAtomIdx() + 1],
                            "source_bond": str(bond.GetBondType()),
                            "product_bond": str(product_bond.GetBondType()),
                        })
            cross_set = frozenset(cross)
            if (
                len(cross) == 2
                and cross_set in generated
                and product.GetNumBonds() == source_edge_count + 2
                and changed
            ):
                valid.append({
                    "azide_atom_mapping": list(azide_match),
                    "alkyne_atom_mapping": list(alkyne_match),
                    "new_cross_adjacencies": [list(row) for row in cross],
                    "positive_finite_multiplicity_changes": changed,
                })
    return {
        "status": "favorable" if valid else "adverse",
        "product_smiles": smiles,
        "azide_embedding_count": len(azide_matches),
        "alkyne_embedding_count": len(alkyne_matches),
        "complete_element_preserving_bijection_count": complete_bijection_count,
        "valid_exact_addition_correspondence_count": len(valid),
        "valid_correspondences": valid,
    }


def main() -> None:
    for path, expected in EXPECTED.items():
        if sha256_file(path) != expected:
            raise SystemExit(f"ORG-009 V9 frozen product input changed: {path}")
    if OUTPUT.exists():
        raise SystemExit("ORG-009 V9 product comparison already exists; replay prohibited")
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    selected_rows = json.loads(SELECTION.read_text(encoding="utf-8"))["selected_in_payload_and_row_order"]
    selected = {(row["config"], row["row_ordinal"], row["reaction_id"]): row for row in selected_rows}
    results = []
    for source in inventory["rows"]:
        path = ROOT / source["opened_snapshot_path"]
        table = pq.read_table(path, columns=["reaction_id", "reaction"])
        for row_ordinal, (reaction_id, payload) in enumerate(zip(table["reaction_id"].to_pylist(), table["reaction"].to_pylist()), start=1):
            key = (source["config"], row_ordinal, reaction_id)
            if key not in selected:
                continue
            reaction = reaction_pb2.Reaction()
            reaction.ParseFromString(payload)
            products = []
            for outcome_ordinal, outcome in enumerate(reaction.outcomes, start=1):
                for product_ordinal, product in enumerate(outcome.products, start=1):
                    smiles_rows = product_smiles(product)
                    if not smiles_rows:
                        products.append({"outcome_ordinal": outcome_ordinal, "product_ordinal": product_ordinal, "status": "unresolved", "reason": "no unique SMILES or CXSMILES product identifier"})
                    else:
                        for identifier_ordinal, smiles in enumerate(smiles_rows, start=1):
                            products.append({"outcome_ordinal": outcome_ordinal, "product_ordinal": product_ordinal, "identifier_ordinal": identifier_ordinal, **compare_product(selected[key], smiles)})
            reaction_status = "favorable" if any(row["status"] == "favorable" for row in products) else ("unresolved" if not products or all(row["status"] == "unresolved" for row in products) else "adverse")
            results.append({
                "config": source["config"],
                "row_ordinal": row_ordinal,
                "reaction_id": reaction_id,
                "independent_label_tokens": selected[key]["independent_label_tokens"],
                "reaction_status": reaction_status,
                "complete_product_identifier_comparisons": products,
            })
    if len(results) != len(selected) or len(selected) != 28:
        raise SystemExit("ORG-009 V9 complete selected reaction census was not preserved")
    counts = {status: sum(row["reaction_status"] == status for row in results) for status in ("favorable", "adverse", "unresolved")}
    output = {
        "schema": "sft-v3-chemistry-org-009-ord-product-comparison/9",
        "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
        "source_inventory_sha256": EXPECTED[INVENTORY],
        "source_selection_sha256": EXPECTED[SELECTION],
        "source_selection_seal_sha256": EXPECTED[SELECTION_SEAL],
        "prediction_seal_sha256": EXPECTED[PREDICTION],
        "comparison_program_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "comparison_program_sha256": sha256_file(Path(__file__).resolve()),
        "complete_selected_reaction_count": len(results),
        "reaction_status_counts": counts,
        "no_selected_reaction_omitted": len(results) == 28,
        "no_post_outcome_filter_applied": True,
        "results_in_frozen_order": results,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "output_sha256": sha256_file(OUTPUT), "complete_selected_reaction_count": len(results), "reaction_status_counts": counts}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
