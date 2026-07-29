"""Frozen registrations for the whole ANAL-012--022 continuation batch."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.analytical_terminal_laws_v1 import LAW_ROWS
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_PATH = "experiments/external_sources/chemistry/snapshots/anal-012-022-whole-subfield-v1/complete-postseal-analysis-v1.json"
ANALYSIS_HASH = "sha256:c4eedffde052b92f065bf990b18b96ec9941ea458f35e6e7a3fd466e6b561f4a"
AUTHORITIES = (
    ('audits/CHEMISTRY_ANAL_001_022_FAMILY_BOUNDARY_2026-07-28.json', "sha256:605cddeba92d16b319a24297668554cc206e625f5289cded52577ca887248260"),
    ('audits/CHEMISTRY_ANAL_012_022_WHOLE_SUBFIELD_BATCH_BOUNDARY_2026-07-28.json', "sha256:de8994198cf3dba8d07613481995e07d40aa59a109de2f5949a7cc39bfa26495"),
    ('sft/chemistry/analytical_terminal_laws_v1.py', "sha256:823f492e2424442534355fc2862ed3e61c49cbd891ef57a0d92e29b5c7941d75"),
    ('experiments/external_sources/chemistry/anal_012_022_whole_subfield_source_identity_registry_v1.json', "sha256:e4c01443156ba2e1367acd5427adac8a47239e36f768071ed45a81d3750eac41"),
    ('experiments/external_sources/chemistry/anal_012_022_source_transport_addendum_v1.json', "sha256:2f113a259f3e2d82f240711f71b5312f7ff5a83563afc138a0ce28d176b35a1a"),
    ('experiments/external_sources/chemistry/anal_012_022_rate_limit_retry_addendum_v1.json', "sha256:efcf41f6f4724259ea0bedde4c94da9fe91d93afdef57abecd6d8713af6d964c"),
    ('experiments/external_sources/chemistry/anal_017_neutron_complete_list_transport_addendum_v1.json', "sha256:93ae48769fcc427f6775a8db5948640645ec370753cc017d6a443e30b1034870"),
    ('experiments/external_sources/chemistry/anal_017_neutron_transport_correction_addendum_v1.json', "sha256:1fc0f60c98c8fb77c321386935777cbaaa61e9a0c460c171114ff0fdedd69dbc"),
    ('experiments/external_sources/chemistry/anal_006_008_dependency_authority_addendum_v1.json', "sha256:82b0ff8a7d8ad6746daf1cb3ffba0308a9f48259f436abfc53b649539170b8b7"),
    ('experiments/external_sources/chemistry/anal_016_srm674_ocr_reconstruction_addendum_v1.json', "sha256:0d46b28c2b7cde57e5ea033c0e80622021d13ad3343846bd36379dd10dd10100"),
    ('experiments/external_sources/chemistry/snapshots/anal-012-022-whole-subfield-v1/source-inventory-v1.json', "sha256:db8cbe081edc5538a8951840d1dc6597fa708b358e87f7814eb121571bbc981a"),
    (ANALYSIS_PATH, ANALYSIS_HASH),
    ('tools/capture_chemistry_anal_012_022_sources_v1.py', "sha256:95518d11f796bc46ee251aacd729d142a96082b34996c9f1c6af0092907e2373"),
    ('tools/capture_chemistry_anal_012_022_linked_addendum_v1.py', "sha256:df38d2bafb587fa94a78f3a232a6c3ae2580f11251f24732c0e8dc0ec75968ac"),
    ('tools/capture_chemistry_anal_012_022_rate_limit_retry_v1.py', "sha256:53b16c82ad0da6a7efa3cbcbb02464d56226f86d2930864361aecc3b968f62ec"),
    ('tools/capture_chemistry_anal_017_neutron_complete_list_addendum_v1.py', "sha256:f1601b9aa74e5b0d0f56bfdbd7e1b807d34248e4d2295942d23c8d85b2fe4f32"),
    ('tools/correct_chemistry_anal_017_neutron_transport_v1.py', "sha256:63a2429f4422900d74a3610b48ece874059dcf13028ae8f48b12881a1da8b249"),
    ('tools/register_chemistry_anal_006_008_dependency_addendum_v1.py', "sha256:81bc1d29d95ab4a4dcb6a3c58ba6a28b5ebd98cc2d39846340fb837f583cc2f7"),
    ('tools/ocr_pdf_vision.swift', "sha256:cc8d84c8e9dd13e3ea17c46d51994ebec2af553c8a0174d63df5c68dddc5fbfa"),
    ('tools/register_chemistry_anal_016_ocr_addendum_v1.py', "sha256:954a1ee4736a6466cc5617efae3429c365ddec20bfe02555993d6b7c8aa68aaf"),
    ('tools/build_chemistry_anal_012_022_external_v1.py', "sha256:fe932a91fb947cd3c7118d43ab73a41b84333dc75567de824db85d47a50fd0a8"),
    ('tools/seal_chemistry_anal_012_022_predictions_v1.py', "sha256:52023c48e881415cc761b7101707a42dacfb3142ad5f3eb67c9792deef7652e5"),
    ('experiments/external_sources/chemistry/anal_012_target_identities_v1.json', "sha256:289f1bf3c4efc83672bc06a6a33268af3c923025dc6cf92559ed7509e1d4d67f"),
    ('experiments/external_sources/chemistry/anal_013_target_identities_v1.json', "sha256:8be8947924fea31cdeb5e0d62c98f407c75aa1d99dc0b2b92d6c99af727bbb5b"),
    ('experiments/external_sources/chemistry/anal_014_target_identities_v1.json', "sha256:6bac6d7cee16cf20fe011efa5374a4759c9fac5ad645bb736db3b0584379daf4"),
    ('experiments/external_sources/chemistry/anal_015_target_identities_v1.json', "sha256:148b28090662e1409cb5334f6a3fafde3310727d14038a80c1400362f3702791"),
    ('experiments/external_sources/chemistry/anal_016_target_identities_v1.json', "sha256:30ce8550b080d87181cf422282dc01492ee88984db05439e095440fb877932b9"),
    ('experiments/external_sources/chemistry/anal_017_target_identities_v1.json', "sha256:409a965e4e7526991777f71e09fe281e9c8ec36c2eed67477c1f4d7d4b40fc69"),
    ('experiments/external_sources/chemistry/anal_018_target_identities_v1.json', "sha256:f21719afb4c2ec2e1834adee2ac98f6b966e0ebb9e3bde2ee9b385259e2d5235"),
    ('experiments/external_sources/chemistry/anal_019_target_identities_v1.json', "sha256:85948e847f7ed50494d8bb094418bf22ee1331fd632554c84923c7e3a7acfe88"),
    ('experiments/external_sources/chemistry/anal_020_target_identities_v1.json', "sha256:d0b4b2cb4cbde6c4c86fb72723ef6b18f0534aed963c217f0c6146621c364fc3"),
    ('experiments/external_sources/chemistry/anal_021_target_identities_v1.json', "sha256:734780f458aeb3dee5053672ace63700b38d9d8a3c9a6d8e356dd28174de91df"),
    ('experiments/external_sources/chemistry/anal_022_target_identities_v1.json', "sha256:26179c0872169c2c89de191f8d1bdcb3d18463bdc1aa49d517a0c7b932700adb"),
    ('experiments/sealed_predictions/chemistry_anal_012_pre_source_v1.json', "sha256:f5ebff0eec3e6b1197033fc4e6619f5794a345e6229b310a8743d0714f86adea"),
    ('experiments/sealed_predictions/chemistry_anal_013_pre_source_v1.json', "sha256:b3cb017388cc3bafe80911816feb7eb022c7ea00b519f8ca2f86da0a08def856"),
    ('experiments/sealed_predictions/chemistry_anal_014_pre_source_v1.json', "sha256:5ec7fd7d651dda88a0ca64a6e01e5f1377fbfd11504211c38b00de527202c822"),
    ('experiments/sealed_predictions/chemistry_anal_015_pre_source_v1.json', "sha256:066758573a33442e5b2ab399e9df78a39d554c8f3851309a1d99153a2fdb4bac"),
    ('experiments/sealed_predictions/chemistry_anal_016_pre_source_v1.json', "sha256:1cd148581323c67f98be22e52ffdbf15992d1cb9c889b9075cce12c2eabed3fb"),
    ('experiments/sealed_predictions/chemistry_anal_017_pre_source_v1.json', "sha256:2a93db7b2bbcf736070831ff0f1ec4951081fdc28d389fb1f1f7863b2518dbd8"),
    ('experiments/sealed_predictions/chemistry_anal_018_pre_source_v1.json', "sha256:6c68d383b80a433b30d1560a3ae27da433af0a5bdc6b32cf8c73555829fc237d"),
    ('experiments/sealed_predictions/chemistry_anal_019_pre_source_v1.json', "sha256:325bc1f2b8648d4b5a8a69cbbb8ffbf114f9114703039749f56a2cc29f3c1dd8"),
    ('experiments/sealed_predictions/chemistry_anal_020_pre_source_v1.json', "sha256:2272fb86157296c73887b457064238542c46d9082ba8216042a8f92b30dbc9f7"),
    ('experiments/sealed_predictions/chemistry_anal_021_pre_source_v1.json', "sha256:0538af5ac245a6fa28ce4a0bfcd8361a59c0287a78d8a0efadd7362f708aebdc"),
    ('experiments/sealed_predictions/chemistry_anal_022_pre_source_v1.json', "sha256:063333fc6b456dd6972f3a254190887c0cc1b0e66768e39373c14c4d45dc7f16"),
)
for path, expected in AUTHORITIES:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"ANAL-012--022 authority changed: {path}")

_analysis = json.loads((ROOT / ANALYSIS_PATH).read_text())
if _analysis["schema"] != "sft-v3-analytical-chemistry-complete-postseal-analysis/1":
    raise ValueError("ANAL-012--022 analysis schema changed")
SOURCE_ARTIFACTS = tuple((row["path"], row["sha256"]) for row in _analysis["complete_source_manifest"])
for path, expected in SOURCE_ARTIFACTS:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"ANAL-012--022 captured source changed: {path}")


def _targets(number: str) -> tuple[ChemistryTargetReference, ...]:
    identity_path = ROOT / f"experiments/external_sources/chemistry/anal_{number}_target_identities_v1.json"
    identity = json.loads(identity_path.read_text())
    source_ids = tuple(identity["source_ids"])
    return tuple(
        ChemistryTargetReference(target, source_ids[index % len(source_ids)], target.casefold().replace("-", " "), ANALYSIS_PATH, ANALYSIS_HASH)
        for index, target in enumerate(identity["target_ids"])
    )


def _spec(number: str) -> EmpiricalChemistrySpec:
    law = LAW_ROWS[number]
    title = law["title"]
    return EmpiricalChemistrySpec(
        claim_id=law["claim_id"],
        title=title,
        statement=law["statement"],
        dependencies=law["dependencies"],
        generation_rule=f"Generate the literal product of the eight frozen ANAL-{number} custody decisions.",
        grammar_boundary=f"Eight binary dimensions exhaust the registered ANAL-{number} carrier, relation, exact-support, condition, custody and extension forms; 2^8 = 256 generated candidates.",
        dimensions=law["dimensions"],
        exact_result=law["result"],
        induction_base=f"One complete held ANAL-{number} record supplies the first lawful exact support or structural EmptyOne case.",
        induction_step="Every successor appends a complete held record without changing any earlier carrier, condition, comparison, adverse result or uncertainty custody.",
        exclusions=(
            "no numerical zero negative irrational imaginary continuum fitted free random or imported native parameter",
            "no external value equation model fit sign zero outcome prominent row or favorable subset selects the survivor",
            "all favorable adverse absent unavailable unresolved predicted fitted uncertain superseded and transport rows remain",
        ),
        operational_witnesses=law["operational_witnesses"],
        experiment_id=f"SFT-EXP-CHEM-{law['claim_id'].removeprefix('SFT-CHEM-')}",
        expected_observation_label=f"complete-anal-{number}-postseal-source-vector",
        target_rows=_targets(number),
        observation_registry_path=ANALYSIS_PATH,
        falsification_condition=(
            f"ANAL-{number} halts if its survivor is nonunique; any registered source, target, value, line, page, condition, unit, uncertainty, favorable, adverse, absent, unavailable, unresolved, fitted, superseded or transport row is omitted; the implementation-distinct reconstruction disagrees; any dependency is missing; or external evidence selects the native law."
        ),
    )


SPECS_BY_NUMBER = {number: _spec(number) for number in tuple(f"{value:03d}" for value in range(12, 23))}
SPECS = tuple(SPECS_BY_NUMBER[number] for number in sorted(SPECS_BY_NUMBER))
for item in SPECS:
    item.validate()

COMPLETENESS_CERTIFICATES = {
    item.claim_id: sha256_identity((item.claim_id, tuple(row.target_id for row in item.target_rows), 256, 8, item.exact_result))
    for item in SPECS
}

__all__ = (
    "ANALYSIS_HASH", "ANALYSIS_PATH", "AUTHORITIES", "COMPLETENESS_CERTIFICATES",
    "SOURCE_ARTIFACTS", "SPECS", "SPECS_BY_NUMBER",
)
