"""Registered ELEC-004 finite molecular-state ordering specification."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.state_energy_order_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
IDENTITY_PATH = "experiments/external_sources/chemistry/state_energy_order_target_identities_v1.json"
IDENTITY_HASH = "sha256:513a7156a9e2c17cd4a48f51dc0dcf1382902f8f45bbcbfe97a17994bb0c23eb"
TARGET_PATH = "experiments/external_sources/chemistry/state_energy_order_withheld_targets_v1.json"
TARGET_HASH = "sha256:ce4175dff16e3b54451075e40f80a09e2dab9641a3a14a095bb0676542c16ab9"
SOURCE_ID = "NIST-CHEMISTRY-WEBBOOK-SRD69-DIATOMIC-CONSTANTS-2025"


for _path, _hash in ((IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH)):
    if hash_file(ROOT / _path) != _hash:
        raise ValueError(f"ELEC-004 registered source changed: {_path}")
_identities = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
if _identities.get("schema") != "sft-v3-state-energy-order-identities/1" or len(_identities.get("rows", ())) != 306:
    raise ValueError("ELEC-004 identity registry is incomplete")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=str(row["target_id"]),
        source_id=SOURCE_ID,
        source_locator=str(row["source_url"]) + f" :: state row {row['state_row_ordinal']} :: Te",
        snapshot_path=str(row["snapshot_path"]),
        snapshot_hash=str(row["snapshot_hash"]),
    )
    for row in _identities["rows"]
)


STATE_ENERGY_ORDER_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-STATE-ENERGY-ORDER-004",
    title="Exact finite ground and excited molecular-state ordering",
    statement=(
        "At one declared molecular composition and geometry, every finite distinguishable electronic-state support "
        "has exactly one structural least state and every excited state occupies one exact positive successor position; "
        "all distinct state pairs are comparable, every higher/lower separation remains a retained positive gap, and "
        "the complete state/support identity record is preserved."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, identity, least-state, excitation, order, gap, record and extension "
        "forms. Decide all 256 forms only by admitted exact order, distinguishability, discrete spectrum, electronic "
        "state, electron-count and molecular-support laws."
    ),
    grammar_boundary=(
        "Every positive finite set of distinguishable molecular electronic states at one declared composition and "
        "geometry. The least element is structural empty One and each remaining state is one positive successor. "
        "Closure is depth-independent because adjoining one distinguishable state forces exactly the next positive "
        "position and its comparisons with every retained predecessor."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="One retained molecular state is uniquely the structural least state; no numerical-zero energy is required as a proof object.",
    induction_step="Adjoining one new distinguishable state to a complete finite order forces one unused positive successor position, positive separations from all predecessors and preservation of every state/support identity.",
    exclusions=(
        "no numerical-zero, negative, irrational, imaginary or floating proof value",
        "no measured NIST energy or state label in candidate generation or survivor selection",
        "no imported Hamiltonian, wavefunction, molecular-orbital energy formula or fitted scale",
        "no selected state pair or omitted unfavorable state-energy row",
        "no species-specific ground-state lookup rule",
        "external decimal and source-zero inscriptions remain post-seal measurement records",
        "no fitted, learned or target-derived parameter",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-STATE-ENERGY-ORDER-004",
    expected_observation_label="unique-least-state-and-positive-successor-order",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if any declared finite molecular state support lacks one unique least state; if an excited "
        "state lacks a positive successor or retained positive gap; if any pair is incomparable or contradictory; if "
        "the source-designated X state is not the unique least orderable NIST state for any registered species; if any "
        "of the 284 excited-state values does not lie above its species ground record; if any of the 306 exact measured "
        "energy inscriptions, uncertainty-status labels or source identities is omitted; or if a tied ground, negative "
        "gap, omitted row, unit-confounded row or tampered source is accepted."
    ),
)
STATE_ENERGY_ORDER_SPEC.validate()


__all__ = ("IDENTITY_HASH", "IDENTITY_PATH", "SOURCE_ID", "STATE_ENERGY_ORDER_SPEC", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES")
