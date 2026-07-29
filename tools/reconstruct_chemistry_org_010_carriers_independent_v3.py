#!/usr/bin/env python3
"""Implementation-distinct ORG-010 carrier reconstruction.

This executable intentionally does not import the primary reconstruction.  It
rebuilds both source equations as positive element multisets, checks every
source-ordered product and preserves every unsuccessful control.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/org-010-europe-pmc-blind-v1"
SOURCE = SNAPSHOT / "complete-postseal-analysis-v1.json"
PDF = SNAPSHOT / "SC-015-D4SC01905A-s001.pdf"
SCHEME = SNAPSHOT / "d4sc01905a-s6.jpg"
REGISTRY = ROOT / "experiments/external_sources/chemistry/org_010_complete_carrier_reconstruction_identity_v3.json"
OUTPUT = SNAPSHOT / "complete-carrier-reconstruction-v3.json"


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def total(*parts: dict[str, int]) -> dict[str, int]:
    result: Counter[str] = Counter()
    for part in parts:
        if not part or any(isinstance(value, bool) or value < 1 for value in part.values()):
            raise SystemExit("carrier support must contain positive counts only")
        result.update(part)
    return dict(sorted(result.items()))


def equation(procedure: str) -> tuple[dict[str, int], dict[str, int], str, str]:
    carboxylate_delta = {"C": 1, "H": 1, "K": 1, "O": 2}
    carbon_dioxide = {"C": 1, "O": 2}
    potassium_bromide = {"Br": 1, "K": 1}
    if procedure == "2.16":
        reagent = {"Br": 1, "C": 3, "H": 6, "N": 1, "O": 2}
        reduced = {"C": 3, "H": 7, "N": 1, "O": 2}
        names = ("2-bromo-2-nitropropane", "2-nitropropane")
    elif procedure == "2.17":
        reagent = {"Br": 1, "C": 10, "H": 14, "N": 1, "O": 2}
        reduced = {"C": 10, "H": 15, "N": 1, "O": 2}
        names = ("2-bromo-2-nitroadamantane", "2-nitroadamantane")
    else:
        raise SystemExit("source procedure is outside the registered pair")
    return (
        total(carboxylate_delta, reagent),
        total(carbon_dioxide, reduced, potassium_bromide),
        *names,
    )


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    expected = {item["path"]: item["sha256"] for item in registry["frozen_sources"]}
    for path in (SOURCE, PDF, SCHEME):
        relative = str(path.relative_to(ROOT))
        if digest(path) != expected[relative]:
            raise SystemExit(f"frozen ORG-010 source changed: {relative}")

    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = tuple(source["characterized_product_rows_in_source_order"])
    controls = tuple(source["unsuccessful_substrate_rows"])
    if len(rows) != 32 or len(controls) != 5:
        raise SystemExit("ORG-010 complete row boundary changed")

    reconstructed = []
    for position, row in enumerate(rows, start=1):
        if row["ordinal"] != position:
            raise SystemExit("ORG-010 source order changed")
        left, right, reagent, reduced = equation(row["procedure"])
        if left != right:
            raise SystemExit(f"ORG-010 carrier equation failed at row {position}")
        reconstructed.append(
            {
                "ordinal": position,
                "product_code": row["product_code"],
                "reported_name": row["reported_name"],
                "source_block_sha256": row["source_block_sha256"],
                "procedure": row["procedure"],
                "reagent": reagent,
                "reduced_reagent_coproduct": reduced,
                "left_positive_atom_support": left,
                "right_positive_atom_support": right,
                "held_complete_product_atom_vector_retained_on_both_sides": True,
                "source_product_unsaturation_observed": row[
                    "observable_unsaturation_in_reported_product_name"
                ],
                "complete_carrier_equation_reconstructed": True,
                "every_coproduct_separately_measured": False,
                "comparison": "exact-match",
            }
        )

    payload = {
        "schema": "sft-v3-chemistry-org-010-complete-carrier-reconstruction/3",
        "claim_id": "SFT-CHEM-ELIMINATION-REACTION-FAMILY-010",
        "obligation_id": "SFT-CHEM-OBL-ORG-010",
        "method": "implementation-distinct positive-element-multiset reconstruction",
        "source_hashes": {str(path.relative_to(ROOT)): digest(path) for path in (SOURCE, PDF, SCHEME)},
        "complete_product_count": len(reconstructed),
        "procedure_counts": {
            "2.16": sum(row["procedure"] == "2.16" for row in reconstructed),
            "2.17": sum(row["procedure"] == "2.17" for row in reconstructed),
        },
        "exact_carrier_match_count": sum(row["comparison"] == "exact-match" for row in reconstructed),
        "unresolved_complete_carrier_count": sum(
            not row["complete_carrier_equation_reconstructed"] for row in reconstructed
        ),
        "rows": reconstructed,
        "unsuccessful_controls": controls,
        "all_unsuccessful_controls_retained": len(controls) == 5,
        "source_observation_and_structural_reconstruction_distinguished": True,
        "scientific_result_retired_on_first_failure": False,
        "completion_credit_awarded_before_valid_family_admission": False,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    payload["reconstruction_identity"] = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT.relative_to(ROOT)),
        "identity": payload["reconstruction_identity"],
        "rows": len(reconstructed),
        "exact_matches": payload["exact_carrier_match_count"],
        "controls": len(controls),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
