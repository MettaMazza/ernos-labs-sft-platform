"""Post-seal PDG anchor check for the complete force-sector inventory."""

from __future__ import annotations

import json
from pathlib import Path

from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)
from sft.physics.sector_inventory_law_v1 import CLAIM_ID as FORMAL_CLAIM_ID


CLAIM_ID = "SFT-PHYS-VALIDATION-FORCE-SECTOR-ANCHORS-003"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/pdg-force-sector-anchor-record.json"
SOURCE_HASH = "sha256:bb37e82e9515ff526cbaad742167c16ac1960b7bfca32d8b39dd4384c73b7341"
EXPECTED_LABEL = "sealed-common-formula-matches-three-eight-anchors__penta-hepta-retained-as-unmeasured-predictions"


def anchor_record(root: Path) -> dict[str, object]:
    path = root / SOURCE_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("record_id") != "PDG-FORCE-SECTOR-ANCHORS-2025":
        raise ValueError("PDG force anchor identity changed")
    sources = payload.get("sources")
    if not isinstance(sources, list) or len(sources) != 2:
        raise ValueError("both PDG source documents must remain registered")
    expected_hashes = {
        "pdg-2025-qcd.pdf": "sha256:7cbb5c5ef1d217fd0a13544db36d031e600f4e4df7309af6c859a0b988ed6ada",
        "pdg-2025-electroweak-model.pdf": "sha256:8642888a3408d8c57fc673b379325b07f02948135491f64a2e42320e8929320a",
    }
    for source in sources:
        snapshot = source["snapshot"]
        if hash_file(path.parent / snapshot) != expected_hashes[snapshot]:
            raise ValueError("PDG force source snapshot changed")
    qcd, electroweak = sources
    observed = {
        "sector_two_mediators": int(electroweak["observed_mediator_kind_count"]),
        "sector_three_charges": int(qcd["observed_charge_kind_count"]),
        "sector_three_mediators": int(qcd["observed_mediator_kind_count"]),
    }
    expected = {"sector_two_mediators": 3, "sector_three_charges": 3, "sector_three_mediators": 8}
    predictions = payload["prediction_boundary"]["standing_unobserved_rows"]
    return {
        "observed": observed,
        "expected": expected,
        "anchors_pass": observed == expected,
        "standing_predictions_retained": predictions == [
            "sector-five mediator count 24",
            "sector-seven mediator count 48",
            "penta/hepta charge and matter inventories",
        ],
    }


_root = Path(__file__).resolve().parents[2]
_record = anchor_record(_root)


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Blind PDG anchor test of the complete force-sector formula",
    statement="After the four-sector inventory seals, the same p-fibre and p-squared-less-One formulas are checked against PDG's sector-two weak-mediator count and sector-three colour/gluon counts. Sector-five and sector-seven outputs remain explicitly unmeasured predictions.",
    dependencies=(FORMAL_CLAIM_ID, "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001", "SFT-PHYS-MEAS-TARGET-CUSTODY-001", "SFT-MATH-EXACT-ARITHMETIC-001"),
    generation_rule="Generate the complete eight-axis product of sealed sector carrier, common count relation, provenance, custody, separate record, complete anchors, successor closure and no-extra-rule forms.",
    grammar_boundary="Every registered known PDG anchor of the common sector formula, plus a mandatory boundary record preserving every presently unmeasured penta/hepta consequence.",
    dimensions=empirical_dimensions("sealed-sector-formula-versus-all-pdg-anchor-counts", "The sector-two and sector-three rows are checked exactly while unobserved outputs remain predictions rather than being counted as confirmations."),
    exact_result="The sealed common formula reproduces weak mediator count three, colour count three and gluon count eight; sector-five count twenty-four and sector-seven count forty-eight remain standing unmeasured predictions.",
    induction_base="The first known prime sector tests p-squared less One without modifying the sealed formula.",
    induction_step="Each additional registered sector row is appended under the same p-fibre formula; absent observations remain predictions and cannot be omitted or marked measured.",
    exclusions=("no PDG count visible to the formal sector derivation", "no imported gauge group selecting p-squared less One", "no unobserved prediction represented as confirmation", "no omitted unfavorable or tampered row"),
    operational_witnesses=(("known-anchors", "All three exact known count anchors match.", _record["anchors_pass"] is True), ("predictions-retained", "Every unmeasured penta/hepta output remains explicit.", _record["standing_predictions_retained"] is True)),
    experiment_id="SFT-EXP-PHYS-VALIDATION-FORCE-SECTOR-ANCHORS-003",
    expected_observation_label=EXPECTED_LABEL,
    target_rows=(ExternalTargetRow("PDG-FORCE-SECTOR-COMPLETE-ANCHOR-RECORD", "PDG-FORCE-SECTOR-ANCHORS-2025", "both hashed PDG reviews and the complete prediction boundary", EXPECTED_LABEL),),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="Any known count differs, a source identity changes, an unmeasured penta/hepta result is omitted or mislabelled as observed, or a tampered row is accepted.",
)


class SectorAnchorValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        record = anchor_record(self.root)
        if not record["anchors_pass"] or not record["standing_predictions_retained"]:
            raise ValueError("complete PDG sector anchor classification failed")
        return BlindExternalMeasurementValidator(self.root, SPEC).validate(sealed)


SPEC.validate()


__all__ = ("CLAIM_ID", "SPEC", "SectorAnchorValidator", "anchor_record")
