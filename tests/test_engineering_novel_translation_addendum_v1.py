from sft.engineering.novel_translation_addendum_laws_v1 import PROTOCOL_ID, SPECS, consciousness_placebo_protocol
from sft.engineering.novel_translation_laws_v1 import COMMON_FIELDS
from sft.physics.structural_constants import candidate_rows, survivor_id

def test_addendum_products():
    for spec in SPECS.values():
        rows = candidate_rows(spec); assert len(rows) == 256; assert sum(row["candidate_id"] == survivor_id(spec) for row in rows) == 1

def test_human_participant_protocol_boundary():
    row = consciousness_placebo_protocol(); assert set(COMMON_FIELDS).issubset(row["required_fields"]); assert row["outcome_status"].startswith("unperformed"); assert "consent-or-withdrawal-violation" in row["stop_conditions"]; assert row["law_selection_by_outcome"] is False

def test_no_omission_identity():
    assert PROTOCOL_ID in SPECS
