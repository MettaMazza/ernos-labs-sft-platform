"""Frozen registrations for the separate ANAL-006--008 NMR claims."""

from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.nmr_chemical_shift_law_v1 import (
    DEPENDENCIES as A6_DEPS,
    DIMENSIONS as A6_DIMS,
    EXACT_RESULT as A6_RESULT,
    OPERATIONAL_WITNESSES as A6_WITNESSES,
)
from sft.chemistry.nmr_spin_coupling_law_v1 import (
    DEPENDENCIES as A7_DEPS,
    DIMENSIONS as A7_DIMS,
    EXACT_RESULT as A7_RESULT,
    OPERATIONAL_WITNESSES as A7_WITNESSES,
)
from sft.chemistry.nmr_relaxation_exchange_law_v1 import (
    DEPENDENCIES as A8_DEPS,
    DIMENSIONS as A8_DIMS,
    EXACT_RESULT as A8_RESULT,
    OPERATIONAL_WITNESSES as A8_WITNESSES,
)
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_PATH = "experiments/external_sources/chemistry/snapshots/anal-006-008-nmr-v1/complete-postseal-analysis-v1.json"
ANALYSIS_HASH = "sha256:a95a8b59121d797be9d6603d39da196c08bfad173965090b879f6a0644c1280d"
AUTHORITIES = (
    ("audits/CHEMISTRY_ANAL_001_022_FAMILY_BOUNDARY_2026-07-28.json", "sha256:605cddeba92d16b319a24297668554cc206e625f5289cded52577ca887248260"),
    ("audits/CHEMISTRY_ANAL_006_008_NMR_FAMILY_BOUNDARY_2026-07-28.json", "sha256:2b8579803361ffe5b267a0e0d65cb3338c3d51b7ede1de20a99275328a49938e"),
    ("experiments/external_sources/chemistry/anal_006_008_nmr_family_source_identity_registry_v1.json", "sha256:950840a96de33154c23fa847add17399b65699352c97df693423f0033c2d7fa7"),
    ("sft/chemistry/nmr_chemical_shift_law_v1.py", "sha256:f00b7dc7c53519e7e4d6f062f4f23ab10ee410298692d1281587b360845fa17e"),
    ("sft/chemistry/nmr_spin_coupling_law_v1.py", "sha256:0d12a0a06c4174a145cc391e073a3be45f2671c7c18541c9f271b3685cdc9853"),
    ("sft/chemistry/nmr_relaxation_exchange_law_v1.py", "sha256:750b46fae6f5d13731510198ee2a02a70e7b1e2b16210bf3a241635205948dc2"),
    ("experiments/external_sources/chemistry/anal_006_target_identities_v1.json", "sha256:1f8af2daba858aa98d6ca18d94721550c61cc0885efb9bbce8f15d4a620c9ff9"),
    ("experiments/external_sources/chemistry/anal_007_target_identities_v1.json", "sha256:8eed065abaca7e37aa4816ff6e8a63fe0c2a86af83d5cb519765b0bdc81b7fba"),
    ("experiments/external_sources/chemistry/anal_008_target_identities_v1.json", "sha256:06822fa5fcb28bfe75289ec3e7343221fe21147eab781df0fb986714a1ae68be"),
    ("experiments/sealed_predictions/chemistry_anal_006_pre_source_v1.json", "sha256:bb7ae8fad44af4891c5fe714bef66acfe35c0c39319def26bc3d0ee477724aa7"),
    ("experiments/sealed_predictions/chemistry_anal_007_pre_source_v1.json", "sha256:57418fb9574d9d94649d7cce83c0b8540d61e35d40c37dd7b296d630717d4460"),
    ("experiments/sealed_predictions/chemistry_anal_008_pre_source_v1.json", "sha256:c0dc7b9c31d6f03961f2465804cdf0c3e3a409b41f962d10636ce655579e6ca4"),
    ("experiments/external_sources/chemistry/snapshots/anal-006-008-nmr-v1/source-inventory-v1.json", "sha256:2120fe7316f1a09594cdbc68c58d3bb102e92511ed7818049ce384c6890eefc6"),
    ("experiments/external_sources/chemistry/snapshots/anal-006-008-nmr-v1/iupac-nmr-nomenclature-2001.html", "sha256:862a0dab10d6146825f15a76b415685707e37883f8e25f750cdbf236eff3b4d9"),
    ("experiments/external_sources/chemistry/snapshots/anal-006-008-nmr-v1/iupac-nmr-nomenclature-2001.pdf", "sha256:772abc498ad57710f93767c244a92711cd51e21fab59ba6827b1f7a6b87b0a2c"),
    ("experiments/external_sources/chemistry/snapshots/anal-006-008-nmr-v1/bmrb-68-summary.html", "sha256:572e016ec0324915efee409c7ef1ba7ebf465987192fc0318afa8a0453cc841e"),
    ("experiments/external_sources/chemistry/snapshots/anal-006-008-nmr-v1/bmr68_3.str", "sha256:40e4271ad186ac101cfdb9920a80ba59c1004656ca20e89fe4d359a9b24893f2"),
    ("experiments/external_sources/chemistry/snapshots/anal-006-008-nmr-v1/bmrb-16582-summary.html", "sha256:f7b8cec5b11041dee84015757b352164ad1986d2b30732531c536836e504ea2c"),
    ("experiments/external_sources/chemistry/snapshots/anal-006-008-nmr-v1/bmr16582_3.str", "sha256:96ff2c9aa43fb16cdd58b01305516c620ff9b6307aafe9f8995da1eaea6a9138"),
    ("experiments/external_sources/chemistry/snapshots/anal-006-008-nmr-v1/bmrb-52365-summary.html", "sha256:ca70d61797ee432b9d7345e5a78cc56ad48a1d876de3d1d25ac0e5234a75e17d"),
    ("experiments/external_sources/chemistry/snapshots/anal-006-008-nmr-v1/bmr52365_3.str", "sha256:6ac4bb1a545b0cf6e488591c0409500dbb99ad55c676b25e824eefef6032e28d"),
    ("experiments/external_sources/chemistry/snapshots/anal-006-008-nmr-v1/bmrb-27257-summary.html", "sha256:4ccbde267dbef2832bd614e054bb1fcc80e09c3b14b9e33e1a81e32f4cb53184"),
    ("experiments/external_sources/chemistry/snapshots/anal-006-008-nmr-v1/bmr27257_3.str", "sha256:08c3400a988ffe0eac00455f947f716a7b349ea0653b4fb5d5872ea17ee21306"),
    (ANALYSIS_PATH, ANALYSIS_HASH),
    ("tools/capture_chemistry_anal_006_008_sources_v1.py", "sha256:2cd42a682e0f107c562dd107380e67a4edbf8ee471549b6c6738169e5dee6b95"),
    ("tools/build_chemistry_anal_006_008_external_v1.py", "sha256:8b71d326afdcbd6d304dc725e5cbf058e24a6cb7340ca86c586eb1e213d2fcd3"),
)
for path, expected in AUTHORITIES:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"ANAL-006--008 authority changed: {path}")


def targets(number: str, names: tuple[str, ...], sources: tuple[str, ...]):
    return tuple(
        ChemistryTargetReference(
            f"SFT-CHEM-ANAL-{number}-{name}",
            "ANAL-006-008-NMR-SOURCE-INVENTORY" if name == "COMPLETE-SOURCE" else sources[index % len(sources)],
            name.casefold().replace("-", " "),
            ANALYSIS_PATH,
            ANALYSIS_HASH,
        )
        for index, name in enumerate(names)
    )


A6_TARGETS = targets("006", (
    "IDENTITY", "REFERENCE", "NUCLEUS-SITE", "SOLVENT-CONDITION",
    "COMPLETE-SHIFT-VECTOR", "UNCERTAINTY-AMBIGUITY", "STATUS-ADVERSE-ABSENT", "COMPLETE-SOURCE",
), ("IUPAC-NMR-NOMENCLATURE-2001", "BMRB-ENTRY-68-CHEMICAL-SHIFTS"))
A7_TARGETS = targets("007", (
    "IDENTITY", "SPIN-PAIR", "BOND-PATH", "COMPLETE-COUPLING-VECTOR",
    "VALUE-ERROR-RANGE", "CONDITION", "STATUS-ADVERSE-ABSENT", "COMPLETE-SOURCE",
), ("IUPAC-NMR-NOMENCLATURE-2001", "BMRB-ENTRY-16582-SCALAR-COUPLINGS"))
A8_TARGETS = targets("008", (
    "IDENTITY", "RELAXATION-PROCESSES", "COMPLETE-RELAXATION-VECTOR", "EXCHANGE-STATES",
    "COMPLETE-EXCHANGE-VECTOR", "TIME-RATE-UNITS-ERRORS", "STATUS-ADVERSE-ABSENT", "COMPLETE-SOURCE",
), ("IUPAC-NMR-NOMENCLATURE-2001", "BMRB-ENTRY-52365-RELAXATION", "BMRB-ENTRY-27257-H-EXCHANGE"))


def spec(claim, title, statement, deps, dims, result, witnesses, experiment, label, target_rows, boundary, base, step):
    return EmpiricalChemistrySpec(
        claim_id=claim,
        title=title,
        statement=statement,
        dependencies=deps,
        generation_rule="Generate the literal product of eight registered NMR-custody decisions.",
        grammar_boundary=boundary,
        dimensions=dims,
        exact_result=result,
        induction_base=base,
        induction_step=step,
        exclusions=(
            "no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter",
            "no external value reference equation conventional model threshold or selected successful row chooses the survivor",
            "all measured adverse absent unavailable unresolved error ambiguity bound condition unit and historical inscriptions remain",
        ),
        operational_witnesses=witnesses,
        experiment_id=experiment,
        expected_observation_label=label,
        target_rows=target_rows,
        observation_registry_path=ANALYSIS_PATH,
        falsification_condition=(
            "The claim halts if its survivor is nonunique; any registered NMR value, site, reference, condition, "
            "unit, uncertainty, ambiguity, absent field, adverse orientation, page or source byte is omitted; "
            "the independent reconstruction disagrees; or any external result selects the law. " + boundary
        ),
    )


SHIFT_SPEC = spec(
    "SFT-CHEM-NMR-CHEMICAL-SHIFT-006",
    "Fold NMR chemical-shift relation",
    "Held molecular, nucleus-site, reference and condition identities force an exact held-side chemical-shift relation with complete row custody.",
    A6_DEPS, A6_DIMS, A6_RESULT, A6_WITNESSES,
    "SFT-EXP-CHEM-NMR-CHEMICAL-SHIFT-006", "complete-nmr-chemical-shift-vector", A6_TARGETS,
    "Eight dimensions exhaust carrier, nucleus, site, reference, environment, exact relation, custody and extension.",
    "One referenced nucleus-site observation supplies the first exact held-side relation.",
    "Every successor appends one complete referenced site without changing prior rows.",
)
COUPLING_SPEC = spec(
    "SFT-CHEM-NMR-SPIN-COUPLING-007",
    "Fold NMR scalar spin-coupling relation",
    "Two held nucleus sites, their counted path and held spin orientation force an exact positive coupling magnitude or structural absence with complete custody.",
    A7_DEPS, A7_DIMS, A7_RESULT, A7_WITNESSES,
    "SFT-EXP-CHEM-NMR-SPIN-COUPLING-007", "complete-nmr-spin-coupling-vector", A7_TARGETS,
    "Eight dimensions exhaust pair, spin relation, counted path, condition, exact magnitude, symmetry, custody and extension.",
    "One held nucleus-site pair and path supplies the first coupling relation.",
    "Every successor appends one complete pair without altering prior relations.",
)
RELAXATION_SPEC = spec(
    "SFT-CHEM-NMR-RELAXATION-EXCHANGE-008",
    "Fold NMR relaxation and exchange law",
    "Held sites, states, processes and finite observation conditions force exact positive relaxation-time or exchange-rate records with complete absence custody.",
    A8_DEPS, A8_DIMS, A8_RESULT, A8_WITNESSES,
    "SFT-EXP-CHEM-NMR-RELAXATION-EXCHANGE-008", "complete-nmr-relaxation-exchange-vector", A8_TARGETS,
    "Eight dimensions exhaust carrier/site, states, process, finite resource, exact relation, observation, adversity and extension.",
    "One held site/process/state observation supplies the first timed transition.",
    "Every successor appends one complete transition without changing earlier evidence.",
)
SPECS = (SHIFT_SPEC, COUPLING_SPEC, RELAXATION_SPEC)
for item in SPECS:
    item.validate()

COMPLETENESS_CERTIFICATES = {
    item.claim_id: sha256_identity((
        item.claim_id,
        tuple(target.target_id for target in item.target_rows),
        10,
        1633,
        item.exact_result,
    ))
    for item in SPECS
}

__all__ = (
    "ANALYSIS_HASH", "ANALYSIS_PATH", "AUTHORITIES", "COMPLETENESS_CERTIFICATES",
    "COUPLING_SPEC", "RELAXATION_SPEC", "SHIFT_SPEC", "SPECS",
)
