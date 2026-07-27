"""First molecular-electronic Chemistry specification.

The IUPAC record is disclosed as a development observation and withheld
post-seal target.  It identifies the question; it is not executable input to
the derivation, candidate generator or survivor selector.
"""

from __future__ import annotations

from pathlib import Path

from sft.chemistry.electronic_structure_derivation import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
    PREDICTED_OBSERVATION_LABEL,
)
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = "experiments/external_sources/chemistry/snapshots/goldbook-terms/ET07026.json"
SNAPSHOT_HASH = "sha256:c22eb092dceb58f901486e494d81b2528a74a60cdd6caa39d9890f69975bef13"
OBSERVATIONS_PATH = "experiments/external_sources/chemistry/observations_electronic_structure_batch_1.json"


if hash_file(ROOT / SNAPSHOT_PATH) != SNAPSHOT_HASH:
    raise ValueError("IUPAC electronic-state snapshot differs from its registered identity")


ELECTRONIC_STRUCTURE_BATCH_1_SPECS = (
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-ELECTRONIC-STATE-IDENTITY-001",
        title="Molecular electronic carrier and retained state identity",
        statement=(
            "A molecular electronic state is the complete finite arrangement of every retained electron occurrence, "
            "held spin label and joint electronic support inside one identified molecular carrier that preserves the "
            "admitted quantum constraints and remains distinguishable under a retained chemical observation record."
        ),
        dependencies=DEPENDENCIES,
        generation_rule=(
            "Generate the literal Cartesian product of carrier, occurrence, arrangement, admissibility, composition, "
            "distinction, record and extension choices; decide every product by preservation of admitted molecular, "
            "quantum, information and observation dependencies."
        ),
        grammar_boundary=(
            "Every exact positive-finite molecular carrier and its generated finite electron-occurrence support at a "
            "declared chemical observation resolution. The certificate is depth-independent because adding one "
            "electron occurrence repeats the same required occurrence, support, held-label and record checks."
        ),
        dimensions=DIMENSIONS,
        exact_result=EXACT_RESULT,
        induction_base=(
            "One retained electron occurrence requires one molecular carrier, one held spin label, one support row and "
            "one observation signature; erasing any coordinate loses the registered distinction."
        ),
        induction_step=(
            "For any complete positive-finite state, adjoining one generated electron occurrence forces one new unique "
            "occurrence identity, held spin label and support row while preserving the same carrier, quantum constraints "
            "and observation record; no new rule or measured value is introduced."
        ),
        exclusions=(
            "no IUPAC wording or target label in candidate generation or survivor selection",
            "no imported molecular Hamiltonian, wavefunction, orbital table or continuum state space",
            "no numerical zero, negative, irrational, imaginary or floating proof value",
            "no fitted, learned, target-derived or species-specific free parameter",
            "no application output or opaque predictor as chemical law",
            "external target opens only after the derivation and prediction seal",
        ),
        operational_witnesses=OPERATIONAL_WITNESSES,
        experiment_id="SFT-EXP-CHEM-ELECTRONIC-STATE-IDENTITY-001",
        expected_observation_label=PREDICTED_OBSERVATION_LABEL,
        target_rows=(
            ChemistryTargetReference(
                target_id="electronic-state-iupac-et07026",
                source_id="IUPAC-GOLD-BOOK-ET07026-2026",
                source_locator="https://goldbook.iupac.org/terms/view/ET07026/json :: current definition",
                snapshot_path=SNAPSHOT_PATH,
                snapshot_hash=SNAPSHOT_HASH,
            ),
        ),
        observation_registry_path=OBSERVATIONS_PATH,
        falsification_condition=(
            "The claim fails if any generated finite electron occurrence can be omitted, duplicated or detached from "
            "the molecular carrier while preserving electronic-state identity; if an arrangement violating an admitted "
            "quantum constraint survives; if the official source-derived target differs from the sealed consequence; "
            "or if any target, source, candidate, receipt or unfavorable control is omitted or altered."
        ),
    ),
)


for _spec in ELECTRONIC_STRUCTURE_BATCH_1_SPECS:
    _spec.validate()


__all__ = ("ELECTRONIC_STRUCTURE_BATCH_1_SPECS",)
