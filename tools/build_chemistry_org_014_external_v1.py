#!/usr/bin/env python3
"""Open the preregistered ORG-014 ORD row interval after its law seal."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from google.protobuf.json_format import MessageToDict
import pyarrow.parquet as pq
from ord_schema.proto import reaction_pb2


ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ROOT / "experiments/external_sources/chemistry/org_014_target_identities_v1.json"
PRESEAL = ROOT / "experiments/sealed_predictions/chemistry_org_014_selectivity_distribution_pre_source_v1.json"
PARQUET = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-ord-holdout-v9/ord_dataset-feaf1b793c6d408aaec1cac7cc3ceadc.parquet"
OUTPUT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/org-014-selectivity-distribution-v1"
OUTPUT = OUTPUT_ROOT / "complete-postseal-product-distribution-v1.json"
EXPECTED_IDENTITY = "sha256:40e157871d179786dd786c8427019541997c90ba3d3566755ce062abdbbf650a"
EXPECTED_PRESEAL = "sha256:e7d8309f8908cac4f9ab2d7588295a80877749f3a808662b7240fbd5aecef7b1"
EXPECTED_PAYLOAD = "sha256:96f07a9a84ed670574bc6dbeb9948d9eeb7694689bf06390e04d9fb294b5d669"
EXPECTED_PARQUET = "sha256:ebefbe9aba687f182d4f068e94be0f7fd71d1189bdb2eff2aca6fedf4d522bf3"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def hash_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return "sha256:" + value.hexdigest()


def numeric_values(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"value", "precision"} and isinstance(item, (int, float)) and not isinstance(item, bool):
                yield item
            yield from numeric_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from numeric_values(item)


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("ORG-014 product distribution already exists; replay prohibited")
    if hash_file(IDENTITY) != EXPECTED_IDENTITY or hash_file(PRESEAL) != EXPECTED_PRESEAL or hash_file(PARQUET) != EXPECTED_PARQUET:
        raise SystemExit("ORG-014 identity, seal or preregistered parquet changed")
    seal = json.loads(PRESEAL.read_text())
    claimed = seal.pop("sealed_payload_hash")
    if claimed != EXPECTED_PAYLOAD or digest(json.dumps(seal, sort_keys=True, separators=(",", ":")).encode()) != claimed:
        raise SystemExit("ORG-014 canonical pre-source seal changed")

    table = pq.read_table(PARQUET, columns=["reaction_id", "reaction"])
    if table.num_rows != 130:
        raise SystemExit("ORG-014 complete registered row interval changed")
    rows = []
    product_count = identifier_count = measurement_count = outcome_count = 0
    rows_with_absent_outcomes = rows_with_absent_products = rows_with_multiple_products = 0
    signed = {"negative": 0, "zero": 0, "positive": 0}
    for ordinal, (reaction_id, payload) in enumerate(zip(table["reaction_id"].to_pylist(), table["reaction"].to_pylist()), 1):
        reaction = reaction_pb2.Reaction()
        reaction.ParseFromString(payload)
        outcomes = []
        if not reaction.outcomes:
            rows_with_absent_outcomes += 1
        row_products = 0
        for outcome_ordinal, outcome in enumerate(reaction.outcomes, 1):
            complete = MessageToDict(outcome, preserving_proto_field_name=True, use_integers_for_enums=True)
            products = []
            if not outcome.products:
                rows_with_absent_products += 1
            for product_ordinal, product in enumerate(outcome.products, 1):
                product_dict = MessageToDict(product, preserving_proto_field_name=True, use_integers_for_enums=True)
                values = tuple(numeric_values(product_dict.get("measurements", [])))
                for value in values:
                    signed["negative" if value < 0 else "zero" if value == 0 else "positive"] += 1
                products.append({
                    "product_ordinal": product_ordinal,
                    "complete_product_record": product_dict,
                    "complete_product_record_sha256": digest(json.dumps(product_dict, sort_keys=True, separators=(",", ":")).encode()),
                    "identifier_count": len(product.identifiers),
                    "measurement_count": len(product.measurements),
                })
                row_products += 1
                product_count += 1
                identifier_count += len(product.identifiers)
                measurement_count += len(product.measurements)
            outcomes.append({
                "outcome_ordinal": outcome_ordinal,
                "complete_outcome_record": complete,
                "complete_outcome_record_sha256": digest(json.dumps(complete, sort_keys=True, separators=(",", ":")).encode()),
                "products_in_source_order": products,
            })
            outcome_count += 1
        if row_products > 1:
            rows_with_multiple_products += 1
        rows.append({
            "row_ordinal": ordinal,
            "reaction_id": reaction_id,
            "raw_reaction_payload_sha256": digest(payload),
            "outcomes_in_source_order": outcomes,
            "outcome_count": len(outcomes),
            "product_count": row_products,
        })

    payload = {
        "schema": "sft-v3-chemistry-org-014-complete-product-distribution/1",
        "claim_id": "SFT-CHEM-SELECTIVITY-COMPLETE-DISTRIBUTION-014",
        "obligation_id": "SFT-CHEM-OBL-ORG-014",
        "identity_sha256": EXPECTED_IDENTITY,
        "pre_source_seal_sha256": EXPECTED_PRESEAL,
        "pre_source_canonical_payload_sha256": EXPECTED_PAYLOAD,
        "parquet_sha256": EXPECTED_PARQUET,
        "complete_registered_reaction_row_count": len(rows),
        "complete_outcome_count": outcome_count,
        "complete_product_count": product_count,
        "complete_product_identifier_count": identifier_count,
        "complete_product_measurement_count": measurement_count,
        "rows_with_absent_outcomes": rows_with_absent_outcomes,
        "outcomes_with_absent_products": rows_with_absent_products,
        "rows_with_multiple_reported_products": rows_with_multiple_products,
        "numeric_measurement_inscriptions_by_sign": signed,
        "all_reaction_rows_products_identifiers_measurements_adverse_absent_and_unresolved_preserved": True,
        "major_product_filter_applied": False,
        "reaction_rows_in_preregistered_order": rows,
    }
    vector = dict(payload)
    payload["complete_result_vector_sha256"] = digest(json.dumps(vector, sort_keys=True, separators=(",", ":")).encode())
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({key: payload[key] for key in (
        "complete_registered_reaction_row_count", "complete_outcome_count", "complete_product_count",
        "complete_product_identifier_count", "complete_product_measurement_count", "rows_with_multiple_reported_products",
        "rows_with_absent_outcomes", "outcomes_with_absent_products", "numeric_measurement_inscriptions_by_sign",
        "complete_result_vector_sha256",
    )}, indent=2, sort_keys=True))
    print(hash_file(OUTPUT))


if __name__ == "__main__":
    main()
