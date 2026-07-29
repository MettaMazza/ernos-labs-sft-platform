"""Frozen registrations for whole-subfield COMP-001--014."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.computational_chemistry_laws_v1 import LAW_ROWS
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_PATH = "experiments/external_sources/chemistry/snapshots/comp-001-014-whole-subfield-v1/complete-postseal-analysis-v1.json"
ANALYSIS_HASH = "sha256:2345e47957e56c5fd682fbc56adc0a3bcb99aa7d6a75226e6c1661acfd17a461"

TARGET_HASHES = {
    "001": "sha256:1d10cd3a650e4c18dd9cd7624ec5e7ca41b55f6e74b6ed11a3a35b85286205f6",
    "002": "sha256:b0cea409ab46c5402e2d4e6b184f70f07ade846d72a9dcdab44645dc9379fdbe",
    "003": "sha256:841bda3e8197abae66d95d2be59c65c3a1040fdf7afc7a79dc93ef75cef1c390",
    "004": "sha256:c2d15e6726ebd54fd3c9f0b703852f5bfeaa79f1d4157f1c9f9bda4c14279a9d",
    "005": "sha256:9ed14f184809d120085c01204525358fd457b15533e3a5c918c2327b28bcad50",
    "006": "sha256:a5a1d761c25bf97557e8f9ce5162b6b78257c1a72c0cfc08274caf08fd68f89f",
    "007": "sha256:703bc6e6c45e55623a4183b9b2aaf3a8cbbb2b7799d0c6da06303d7bcb7e2400",
    "008": "sha256:7725329745bc2494ce789ecac782e1a7bdb6623c1c7abfc1443e0bc4fa958a52",
    "009": "sha256:06fc91af474e8b889aaf80c5f552319d151eb074f44288c869d775a1b7df6521",
    "010": "sha256:d54337ff27fe88f2397a886290df6d9a30daf705436e9491246e6699740c070b",
    "011": "sha256:045b6a2b20ecefe832e10a0bdf72d73d65bd8a6d512c37f3f2fc050eb3fed878",
    "012": "sha256:fc35a86e4bcf3c9ed8846c63c614f9520be6b9f05745e3db6bcd5dd9ce093e76",
    "013": "sha256:f7600b0944c1a08b8bbcc9c129a0fea3c69db23863af9f2ab77258d8a6b990e6",
    "014": "sha256:5b35d1f59a5aa8098f46ea1065a95fe374e4f2576526033a5842fe952a7a42ce",
}
SEAL_HASHES = {
    "001": "sha256:f8e0cbf3f0db832d60cf3c0007f04db96d3ae17e8abdb166a1bd10d63f7a14a0",
    "002": "sha256:36fd050fee566c281214b255fa6122da4610ceea6f9ae2866697901dd8f2df42",
    "003": "sha256:57521214e63c46c63c770ea593d83de64c1c10759fd0089d197f2c8c22b65886",
    "004": "sha256:da3f2d88406999c866517dc48636207c50dc474d8e1881ba74b3a5c0dc14640d",
    "005": "sha256:e1357c44e79535fe2c93fed7ad5591ae7aeaefef247b2d5479870e9e998b44ee",
    "006": "sha256:6c391953c753dcd0df3561c416a9bb43628a6af6b535593977f48fe500ce0fb1",
    "007": "sha256:4ad646abe4c7a77e488443bdd6860773e8450761b890773d80fa543f41aefabf",
    "008": "sha256:b23424f954a426fad8c6b862914248a3a4ce41b987ae2dc037abc185f6f8f734",
    "009": "sha256:63e13fb54c3d2a1ad2281f4fd7f22386676eab3abe1ed076a22f19c0f321fa16",
    "010": "sha256:2e481b9b549fb9f6a51b2c0386214ed98d08ece57ea880a76c01d941fa272002",
    "011": "sha256:81113c72ee31350a4c0d21a2a37c037cedd3169fc96dcc84ba5e2e88549aa323",
    "012": "sha256:73c5cf90107c8834f3b05891eebb6d9911583723131e773d1aa2055500af864b",
    "013": "sha256:0157b7842ffbbea2de7559efa75e359d15e24a5c351c69a5ca1da1f0196aecf7",
    "014": "sha256:7a52bdc0b4726077eb4d2ddf372797c37000576887457cfd1deef6652601dcdc",
}

AUTHORITIES = (
    ("audits/CHEMISTRY_COMP_001_014_WHOLE_SUBFIELD_BATCH_BOUNDARY_2026-07-28.json", "sha256:af6f51337015ad5bac45fc2f8727e6025d22b812274c72069a566bde8740e6c6"),
    ("sft/chemistry/computational_chemistry_laws_v1.py", "sha256:d44e97cccd47b0422bf5849da29f1bc91a8b10b4e044504ffebb2d4a7b6f6c96"),
    ("experiments/external_sources/chemistry/comp_001_014_whole_subfield_source_identity_registry_v1.json", "sha256:544ba3fcb61dd7ec336536535a8982d541b47f989d5b36285b7855c71f98b811"),
    ("experiments/external_sources/chemistry/snapshots/comp-001-014-whole-subfield-v1/source-inventory-v1.json", "sha256:63f8418f886ad4aca88e345f291d0c492c2ee56fea7c437e02507b17e02bf39c"),
    ("experiments/external_sources/chemistry/comp_004_formula_linked_source_identity_addendum_v1.json", "sha256:1e1855376d657644e1ddd4914ecb95c35548594497bf1e6326c965972f468052"),
    ("experiments/external_sources/chemistry/comp_004_formula_linked_transport_addendum_v1.json", "sha256:19655b76b0559f80e27d53cae514ca2fd00316d8c7152ba21d1239f765b03b04"),
    ("experiments/external_sources/chemistry/comp_008_009_atom_mapping_dependency_addendum_v1.json", "sha256:646b93e7f26389f31677672a71190d2fd022bcc50f91cf1d95c32aba519585f2"),
    (ANALYSIS_PATH, ANALYSIS_HASH),
    ("tools/seal_chemistry_comp_001_014_predictions_v1.py", "sha256:3ddef18f00062fe161d3e0f1667d4c41b324eabb20162f5c1b63df910e3cf617"),
    ("tools/capture_chemistry_comp_001_014_sources_v1.py", "sha256:0533dab2615573205f1afde8758c03df214d8855b9651db0e924c777173e686c"),
    ("tools/register_chemistry_comp_004_formula_linked_addendum_v1.py", "sha256:aac9385e7382b91f0b1d7972a5c2760214f71e3ce9147185a3de326274282acc"),
    ("tools/capture_chemistry_comp_004_formula_linked_v1.py", "sha256:9487c90666c1bc428a90339ef693a1a98eb61fc2a234dc46699201ca9bf1cb5e"),
    ("tools/build_chemistry_comp_001_014_external_v1.py", "sha256:8d2e818021a75f10f6fe49da9b85039d5b9bb4ed38d2ac423266660fad147ebd"),
) + tuple((f"experiments/external_sources/chemistry/comp_{number}_target_identities_v1.json", TARGET_HASHES[number]) for number in sorted(TARGET_HASHES)) + tuple((f"experiments/sealed_predictions/chemistry_comp_{number}_pre_source_v1.json", SEAL_HASHES[number]) for number in sorted(SEAL_HASHES))

for path, expected in AUTHORITIES:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"COMP-001--014 authority changed: {path}")

_analysis = json.loads((ROOT / ANALYSIS_PATH).read_text())
if _analysis["schema"] != "sft-v3-computational-chemistry-complete-postseal-analysis/1":
    raise ValueError("COMP-001--014 analysis schema changed")
SOURCE_ARTIFACTS = tuple((row["path"], row["sha256"]) for row in _analysis["complete_source_manifest"])
for path, expected in SOURCE_ARTIFACTS:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"COMP-001--014 captured source changed: {path}")


def _targets(number: str) -> tuple[ChemistryTargetReference, ...]:
    identity = json.loads((ROOT / f"experiments/external_sources/chemistry/comp_{number}_target_identities_v1.json").read_text())
    sources = tuple(identity["source_ids"])
    return tuple(ChemistryTargetReference(target, sources[index % len(sources)], target.casefold().replace("-", " "), ANALYSIS_PATH, ANALYSIS_HASH) for index, target in enumerate(identity["target_ids"]))


def _spec(number: str) -> EmpiricalChemistrySpec:
    law = LAW_ROWS[number]
    return EmpiricalChemistrySpec(
        claim_id=law["claim_id"], title=law["title"], statement=law["statement"], dependencies=law["dependencies"],
        generation_rule=f"Generate the literal product of the eight frozen COMP-{number} chemical-information custody decisions.",
        grammar_boundary=f"Eight binary dimensions exhaust the registered COMP-{number} identity, exact-support, equivalence, provenance, falsification and extension forms; 2^8 = 256 generated candidates.",
        dimensions=law["dimensions"], exact_result=law["result"],
        induction_base=f"One complete held COMP-{number} carrier and its exact finite record supply the base case.",
        induction_step="Every successor appends a complete held carrier, mapping, transition or evidence record without changing any earlier canonical identity, comparison, adverse outcome or resource boundary.",
        exclusions=(
            "no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter",
            "no external database encoding algorithm score value equation model fit outcome or software library selects the survivor",
            "all favorable adverse absent unavailable unresolved low-confidence transport conflict and declared resource-halt rows remain",
        ),
        operational_witnesses=law["operational_witnesses"],
        experiment_id=f"SFT-EXP-CHEM-{law['claim_id'].removeprefix('SFT-CHEM-')}",
        expected_observation_label=f"complete-comp-{number}-postseal-source-vector",
        target_rows=_targets(number), observation_registry_path=ANALYSIS_PATH,
        falsification_condition=f"COMP-{number} halts if its survivor is nonunique; a registered target, source route, graph, atom, bond, orientation, mapping, reaction row, provenance record, database conflict, adverse result or resource halt is omitted; the implementation-distinct reconstruction disagrees; a dependency is absent; or external data selects the native law.",
    )


SPECS_BY_NUMBER = {number: _spec(number) for number in tuple(f"{value:03d}" for value in range(1, 15))}
SPECS = tuple(SPECS_BY_NUMBER[number] for number in sorted(SPECS_BY_NUMBER))
for spec in SPECS:
    spec.validate()

COMPLETENESS_CERTIFICATES = {spec.claim_id: sha256_identity((spec.claim_id, tuple(row.target_id for row in spec.target_rows), 256, 8, spec.exact_result)) for spec in SPECS}

__all__ = ("ANALYSIS_HASH", "ANALYSIS_PATH", "AUTHORITIES", "COMPLETENESS_CERTIFICATES", "SOURCE_ARTIFACTS", "SPECS", "SPECS_BY_NUMBER")
