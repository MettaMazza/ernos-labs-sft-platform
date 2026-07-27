"""Registered KIN-009 law and complete reversible/equilibrium source surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.reversible_kinetic_equilibrium_law_v1 import (
    DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES,
)
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/kin-009-reversible-kinetic-equilibrium-v1"
SPEC_PATH = "experiments/external_sources/chemistry/reversible_kinetic_equilibrium_capture_spec_v1.json"
SPEC_HASH = "sha256:cc936c64ac170830e26ec3fece37d246511b5e76e895c90db82ccaca4a5d3152"
INVENTORY_PATH = f"{SNAPSHOT_ROOT}/source-inventory-v1.json"
INVENTORY_HASH = "sha256:5d7c24d3d62d2b3217a62e7e3f34be9e7425c2d5a3f65ed6acb7b7a404542722"
IDENTITY_PATH = "experiments/external_sources/chemistry/reversible_kinetic_equilibrium_target_identities_v1.json"
IDENTITY_HASH = "sha256:512caad8d5b26bd6da8ac04ca0a9f8b68f2700f8d83444bb1abbfc457ac9a720"
TARGET_PATH = "experiments/external_sources/chemistry/reversible_kinetic_equilibrium_withheld_targets_v1.json"
TARGET_HASH = "sha256:050afd47917ceac491e51e737837e37b89fdf2e57a0a800d6706e073d7e6cf14"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/reversible-kinetic-equilibrium-primary-records-v1.json"
PRIMARY_HASH = "sha256:adceaa37dda2f748a24be6635a2c877cd575be05fc9db14c771e23949395c71b"
ARTICLE_HTML_PATH = f"{SNAPSHOT_ROOT}/article.html"
ARTICLE_HTML_HASH = "sha256:c2011aa9108d6e2baaa5beed58ab5976c5ad489d62e6af8ac0b1a4657968e7aa"
ARTICLE_PDF_PATH = f"{SNAPSHOT_ROOT}/article.pdf"
ARTICLE_PDF_HASH = "sha256:f6d481ffa2c7dfb27739bb4795f67b434e322e58abf56d729a05a7fbede922bc"
SUPPLEMENT_PATH = f"{SNAPSHOT_ROOT}/supplementary-information.pdf"
SUPPLEMENT_HASH = "sha256:3311c49444849d6932b531236e46620f2ec5fb2ecf446c4ce4a65767ca43c5d4"
DESCRIPTION_PATH = f"{SNAPSHOT_ROOT}/additional-file-description.pdf"
DESCRIPTION_HASH = "sha256:6b4df61d509ebeb24ddbeb67210b0447db859d186c19d3d66973c1945492569d"
MOVIE_PATH = f"{SNAPSHOT_ROOT}/supplementary-movie.gif"
MOVIE_HASH = "sha256:f4462d9274601b7991848b765c6b0f126253690926b5f5d60fa22a30aa3ae2d9"
SOURCE_DATA_PATH = f"{SNAPSHOT_ROOT}/source-data.zip"
SOURCE_DATA_HASH = "sha256:004410f7f073c6a7c218fa199b2df7efbc6806c6ff5be11001a12888cb8e10f9"


for path, expected in (
    (SPEC_PATH, SPEC_HASH), (INVENTORY_PATH, INVENTORY_HASH), (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (ARTICLE_HTML_PATH, ARTICLE_HTML_HASH),
    (ARTICLE_PDF_PATH, ARTICLE_PDF_HASH), (SUPPLEMENT_PATH, SUPPLEMENT_HASH),
    (DESCRIPTION_PATH, DESCRIPTION_HASH), (MOVIE_PATH, MOVIE_HASH), (SOURCE_DATA_PATH, SOURCE_DATA_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"KIN-009 registered source changed: {path}")

_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_registered_target_count") != 164
    or _primary.get("complete_pdf_page_target_count") != 155
    or _primary.get("complete_supplementary_movie_frame_count") != 73
    or _primary.get("complete_source_data_archive_member_count") != 8
    or _primary.get("complete_reversible_state_pair_count") != 3
    or _primary.get("complete_directional_experiment_count") != 4
    or _primary.get("complete_terminal_equilibrium_composition_count") != 4
    or _primary.get("equilibrium_disagreement_adverse_record_preserved") is not True
    or _primary.get("source_direction_label_disagreements_preserved_without_selection") is not True
    or _identities.get("complete_registered_target_count") != 164
    or _identities.get("target_values_or_hashes_present") is not False
    or len(_identities.get("rows", ())) != 164
):
    raise ValueError("KIN-009 complete source boundary changed")

SOURCE_FILES = (
    (ARTICLE_HTML_PATH, ARTICLE_HTML_HASH), (ARTICLE_PDF_PATH, ARTICLE_PDF_HASH),
    (SUPPLEMENT_PATH, SUPPLEMENT_HASH), (DESCRIPTION_PATH, DESCRIPTION_HASH),
    (MOVIE_PATH, MOVIE_HASH), (SOURCE_DATA_PATH, SOURCE_DATA_HASH),
)
SOURCE_HASH_BY_DOCUMENT = {
    "article.pdf": (ARTICLE_PDF_PATH, ARTICLE_PDF_HASH),
    "supplementary-information.pdf": (SUPPLEMENT_PATH, SUPPLEMENT_HASH),
    "additional-file-description.pdf": (DESCRIPTION_PATH, DESCRIPTION_HASH),
    "supplementary-movie.gif": (MOVIE_PATH, MOVIE_HASH),
    "source-data.zip": (SOURCE_DATA_PATH, SOURCE_DATA_HASH),
}

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"], source_id=row["source_id"],
        source_locator=(
            f"DOI 10.1038/s41467-023-40190-4; complete source record {row['source_record_ordinal']}; "
            f"document {row['source_document_identity']}; record {row['source_record_identity']}"
        ),
        snapshot_path=SOURCE_HASH_BY_DOCUMENT[row["source_document_identity"]][0],
        snapshot_hash=SOURCE_HASH_BY_DOCUMENT[row["source_document_identity"]][1],
    )
    for row in _identities["rows"]
)


REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-REVERSIBLE-KINETIC-EQUILIBRIUM-CORRESPONDENCE-009",
    title="Exact reversible kinetic-equilibrium correspondence law",
    statement=(
        "For two distinct retained states, exact forward and reverse transition occurrences close one and the same "
        "two-state graph. The ordered directed edges are the kinetic record and the graph's retained recurrence support "
        "is the equilibrium support. Direction is a held orientation rather than a sign; no imported reversible-rate "
        "equation, equilibrium constant, stochastic weight, fitted balance or steady-state premise enters the relation."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of support, graph, kinetics, equilibrium, composition, status, provenance and "
        "prediction forms; decide all 256 candidates only from admitted exact state-transition, energy-order, "
        "complete-channel, sequential and parallel mechanism laws."
    ),
    grammar_boundary=(
        "Every finite source-ordered family of complete two-state graphs containing two distinct registered states, one "
        "directed edge in each held orientation, one exact condition boundary and retained favorable, adverse or unresolved "
        "status. External testing binds all 164 pre-registered records: ten article pages, 144 supplementary pages, one "
        "additional-description page, one 73-frame movie and all eight source-data archive members."
    ),
    dimensions=DIMENSIONS, exact_result=EXACT_RESULT,
    induction_base=(
        "One pair of distinct states with one edge in each held orientation forces the first closed reversible graph; its "
        "directed edge word and recurrence support are two views of that same graph."
    ),
    induction_step=(
        "Appending the next complete reversible pair at the next positive source occurrence preserves every prior state, "
        "directed edge, condition, status, recurrence support and correspondence exactly."
    ),
    exclusions=(
        "no numerical zero; source glyph 0 is an external reference inscription and native absence is structural EmptyOne",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported reversible-rate equation, equilibrium law or constant, stochastic premise, direction weight or steady-state assumption",
        "no selected direction, time, state, condition, method, page, frame, archive member or row",
        "no refit, averaging, interpolation, renormalization, target correction or omission of disagreement/adverse/unresolved evidence",
        "no state, time, composition, rate, quantum yield, energy, uncertainty, fit, calculation, value or target hash before all 164 identities seal",
        "source fits, slopes, energies, equations and calculations remain post-seal provenance and never become Fold proof parameters",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-REVERSIBLE-KINETIC-EQUILIBRIUM-009",
    expected_observation_label="complete-forward-reverse-equilibrium-source-vector",
    target_rows=TARGET_REFERENCES, observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if the two directions do not close the same exact state pair; if either directed occurrence, "
        "initial or terminal composition, condition, adverse disagreement, page, movie frame, archive member or source file "
        "is omitted; if an imported rate/equilibrium law, constant, stochastic weight, fit, average, interpolation, "
        "renormalization or target correction enters; if values open before all 164 identities seal; or if tampering passes."
    ),
)
REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC.validate()


__all__ = (
    "ARTICLE_HTML_HASH", "ARTICLE_HTML_PATH", "ARTICLE_PDF_HASH", "ARTICLE_PDF_PATH", "DESCRIPTION_HASH",
    "DESCRIPTION_PATH", "IDENTITY_HASH", "IDENTITY_PATH", "INVENTORY_HASH", "INVENTORY_PATH", "MOVIE_HASH",
    "MOVIE_PATH", "PRIMARY_HASH", "PRIMARY_PATH", "REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC", "SOURCE_DATA_HASH",
    "SOURCE_DATA_PATH", "SOURCE_FILES", "SPEC_HASH", "SPEC_PATH", "SUPPLEMENT_HASH", "SUPPLEMENT_PATH",
    "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
