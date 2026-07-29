"""Complete penta/hepta phenotype, census and signature return family."""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


ONE = Fraction(1, 1)
HALF_ONE = Fraction(1, 2)
PENTA_ID = "SFT-PHYS-PENTA-COMPLETE-PHENOTYPE-088"
HEPTA_ID = "SFT-PHYS-HEPTA-COMPLETE-PHENOTYPE-089"
PENTA_BETA_ID = "SFT-PHYS-PENTA-BETA-SLOPE-090"
HEPTA_BETA_ID = "SFT-PHYS-HEPTA-BETA-SLOPE-091"
CENSUS_ID = "SFT-PHYS-CATEGORY-CLEAN-PARTICLE-CENSUS-092"
BOUNDARY_ID = "SFT-PHYS-NO-EXTRA-SECTOR-PARTICLE-BOUNDARY-093"
SIGNATURE_ID = "SFT-PHYS-SMITHION-INTERACTION-SEARCH-SIGNATURES-094"
PRIME_SECTORS = (2, 3, 5, 7)
NEW_SECTORS = (5, 7)
KNOWN_FERMION_KINDS = (
    "electron", "muon", "tau",
    "electron-neutrino", "muon-neutrino", "tau-neutrino",
    "up", "charm", "top", "down", "strange", "bottom",
)


def sector_phenotype(sector: int) -> dict[str, object]:
    if sector not in NEW_SECTORS:
        raise ValueError("the new-sector phenotype boundary contains exactly penta and hepta")
    shortfall = Fraction(1, sector)
    coupling = ONE - shortfall
    pairs = tuple((Fraction(index, sector), Fraction(sector - index, sector)) for index in range(1, (sector + 1) // 2))
    return {
        "sector": sector,
        "shortfall": shortfall,
        "coupling": coupling,
        "colours": sector,
        "mediators": sector * sector - 1,
        "confinement_pairs": pairs,
        "confinement_pair_count": len(pairs),
        "beta_slope": coupling / shortfall,
        "carrier_mass_record": "empty-One",
        "carrier_speed": ONE,
        "flux_tube_width": HALF_ONE,
        "tube_closes_to": HALF_ONE + HALF_ONE,
        "neutral_complete_fibre": shortfall * sector,
        "neutral_pairs": tuple(left + right for left, right in pairs),
    }


def sector_beta_slope(sector: int) -> Fraction:
    phenotype = sector_phenotype(sector)
    return phenotype["coupling"] / phenotype["shortfall"]


def category_clean_particle_census() -> dict[str, object]:
    sector_carriers = tuple((sector, sector * sector - 1) for sector in PRIME_SECTORS)
    gauge_carriers = sum(count for _, count in sector_carriers)
    nonsector_bosons = ("photon", "graviton", "Higgs")
    smithion_kinds = 2 * 3 * len(NEW_SECTORS)
    total = gauge_carriers + len(nonsector_bosons) + len(KNOWN_FERMION_KINDS) + smithion_kinds
    return {
        "sector_carriers": sector_carriers,
        "gauge_carriers": gauge_carriers,
        "predicted_new_gauge_carriers": 24 + 48,
        "nonsector_bosons": nonsector_bosons,
        "known_fermion_kinds": KNOWN_FERMION_KINDS,
        "known_fermion_kind_count": len(KNOWN_FERMION_KINDS),
        "smithion_kind_count": smithion_kinds,
        "category_clean_total": total,
    }


def no_extra_boundary() -> dict[str, object]:
    census = category_clean_particle_census()
    return {
        **census,
        "last_admitted_sector": NEW_SECTORS[-1],
        "first_excluded_prime": 11,
        "outside_list_falsifiers": (
            "confirmed-fundamental-axion",
            "confirmed-fourth-or-sterile-fundamental-neutrino-kind",
            "confirmed-fundamental-supersymmetric-partner",
            "confirmed-confining-prime-sector-beyond-seven",
            "confirmed-fundamental-kind-outside-category-clean-total",
        ),
    }


def smithion_search_signatures() -> dict[int, dict[str, object]]:
    signatures = {}
    for sector in NEW_SECTORS:
        phenotype = sector_phenotype(sector)
        signatures[sector] = {
            "electromagnetic_charge_record": "empty-One",
            "cross_fibre_nuclear_recoil_carrier": "empty-One",
            "gravitational_response": ONE,
            "confining_jet_carriers": phenotype["mediators"],
            "neutral_bound_constituents": sector,
            "missing_carrier_record": "lightest-neutral-sector-singlet",
            "sector_coupling": phenotype["coupling"],
        }
    return signatures


EXCLUSIONS = (
    "no V1/V2 executable, desired phenotype, experimental target or conventional force model as a premise",
    "no free coupling, fitted slope, invented cross-fibre mediator or open-ended sector",
    "no patent, collider anomaly, null search or reputation selecting a formal survivor",
    "no confirmed discovery asserted for a penta/hepta carrier or Smithion",
    "no numerical-zero, negative, irrational, imaginary, floating or completed-infinite proof magnitude",
)


def axes(relation: str, reason: str) -> tuple:
    return (
        binary_axis("predecessor", "Are admitted predecessors retained?", "rewrite-or-bypass-predecessors", "Bypassing predecessors severs the root-directed derivation.", "retain-admitted-prime-sector-predecessors", "The existing prime-sector laws constrain the successor."),
        binary_axis("sector", "Which sector boundary is used?", "open-or-target-selected-sector", "An open or target-selected sector is a free choice.", "generated-penta-hepta-boundary", "The admitted ladder terminates at sectors five and seven."),
        binary_axis("relation", "Which exact relation survives?", "free-phenotype-or-slope", "A free phenotype or slope is a parameter.", relation, reason),
        binary_axis("carrier", "How is the carrier represented?", "massive-or-speed-fitted-carrier", "A fitted mass or speed imports an unforced magnitude.", "empty-mass-One-speed-carrier", "No generated mass record and one transition per tick force the carrier class."),
        binary_axis("confinement", "How does confinement close?", "unbounded-width-or-unpaired-charge", "Unbounded width or an unpaired charge does not close the fibre.", "half-One-tube-and-complete-antipodes", "The half-One tube and every antipodal pair close exactly."),
        binary_axis("inventory", "Which inventory is retained?", "mixed-category-or-open-inventory", "Mixed counting or an open list cannot certify completeness.", "category-clean-finite-inventory", "Every carrier and named kind is assigned once to one category."),
        binary_axis("measurement", "Can observation select the law?", "target-selected-survivor", "Target selection is fitting.", "formal-seal-before-observation", "Formal structure seals before external comparison."),
        binary_axis("extension", "Is an extra rule required?", "free-extra-rule", "An exception is an unforced parameter.", "no-extra-rule", "The admitted dependencies exhaust the declared boundary."),
    )


def phenotype_spec(claim_id: str, sector: int, dependencies: tuple[str, ...]) -> StructuralPhysicsSpec:
    phenotype = sector_phenotype(sector)
    name = "penta" if sector == 5 else "hepta"
    return StructuralPhysicsSpec(
        claim_id=claim_id,
        title=f"Complete {name} sector phenotype",
        statement=f"The generated sector-{sector} force retains its complete charge, mediator, antipodal-pair, carrier and confinement phenotype without importing a known-force template as a premise.",
        dependencies=dependencies,
        evidence_mode=EvidenceMode.FORMAL,
        generation_rule=f"Generate the complete eight-axis product for the sector-{sector} predecessor, boundary, exact phenotype, carrier, confinement, inventory, measurement direction and extension form.",
        grammar_boundary=f"The admitted prime-sector ladder at sector {sector}; all {sector - 1} nonidentity charge parts; their complete antipodal pairing; the p-squared-less-One carrier census; mass/rest, propagation and tube records; and all 256 structural forms.",
        axes=axes(f"sector-{sector}-complete-forced-phenotype", f"Sector {sector} fixes shortfall 1/{sector}, coupling {sector-1}/{sector}, {sector} charge labels, {sector*sector-1} mediators and {(sector-1)//2} antipodal pairs; the common carrier law fixes empty mass, One speed and a half-One self-confining tube."),
        exact_result=f"Sector {sector} has exact shortfall 1/{sector}, coupling {sector-1}/{sector}, {sector} charge kinds, {sector*sector-1} mediators and {(sector-1)//2} complete antipodal confinement pairs. Its carrier has an empty-One mass/rest record, advances one exact support cell per tick, and self-confines in the half-One tube that closes to the One. Every antipodal pair and the complete {sector}-constituent fibre are neutral at the One.",
        induction_base=f"The first nonidentity charge part 1/{sector} has the unique antipode {sector-1}/{sector} and closes to the One.",
        induction_step=f"Appending the next charge part either completes its already counted antipodal pair or extends the complete {sector}-part fibre without changing the common carrier or tube law.",
        exclusions=EXCLUSIONS,
        witnesses=(
            Witness("counts", f"Sector {sector} has the exact carrier and antipodal-pair counts.", phenotype["mediators"] == sector * sector - 1 and phenotype["confinement_pair_count"] == (sector - 1) // 2),
            Witness("neutral-pairs", "Every generated antipodal pair closes to the One.", all(value == ONE for value in phenotype["neutral_pairs"])),
            Witness("carrier", "The carrier is One-speed and its half-One tube closes to the One.", phenotype["carrier_speed"] == ONE and phenotype["tube_closes_to"] == ONE),
            Witness("neutral-fibre", "The complete constituent fibre closes to the One.", phenotype["neutral_complete_fibre"] == ONE),
        ),
    )


PENTA_SPEC = phenotype_spec(PENTA_ID, 5, (
    "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",
    "SFT-PHYS-STRONG-CARRIER-MASSLESS-CONFINED-TERMINAL-013",
    "SFT-PHYS-INTERACTION-UNIFICATION-TERMINAL-025",
    "SFT-MATH-EXACT-ARITHMETIC-001",
))
HEPTA_SPEC = phenotype_spec(HEPTA_ID, 7, (
    PENTA_ID,
    "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",
    "SFT-PHYS-STRONG-CARRIER-MASSLESS-CONFINED-TERMINAL-013",
    "SFT-MATH-EXACT-ARITHMETIC-001",
))


def beta_spec(claim_id: str, sector: int, dependencies: tuple[str, ...]) -> StructuralPhysicsSpec:
    slope = sector_beta_slope(sector)
    return StructuralPhysicsSpec(
        claim_id=claim_id,
        title=f"Independent sector-{sector} beta-slope law",
        statement=f"The sector-{sector} coupling-to-shortfall relation independently forces beta slope {sector-1} and its own sector-specific falsifier.",
        dependencies=dependencies,
        evidence_mode=EvidenceMode.FORMAL,
        generation_rule=f"Generate the complete eight-axis product for the independently unbundled sector-{sector} beta slope, carrier, confinement, inventory, measurement and extension forms.",
        grammar_boundary=f"Exact sector {sector}, its coupling and shortfall, every positive exact ratio reconstruction, its distinct slope falsifier and all 256 structural alternatives.",
        axes=axes(f"sector-{sector}-coupling-divided-by-shortfall-equals-{sector-1}", f"({sector-1}/{sector}) divided by (1/{sector}) is forced exactly to {sector-1}; no running target or other sector selects it."),
        exact_result=f"For sector {sector}, the exact coupling ({sector-1})/{sector} divided by the exact shortfall 1/{sector} is the positive whole {sector-1}. Thus the sector-{sector} beta-slope carrier is independently {sector-1}. A measured sector-{sector} slope unequal to {sector-1}, after a sector-{sector} carrier is identified, is its distinct falsifier and does not retire the other sector's law.",
        induction_base=f"The admitted sector-{sector} coupling and shortfall reconstruct the One and their ratio is {sector-1}.",
        induction_step="Repeating the exact comparison retains the same ratio because no scale-dependent coefficient enters this structural slope identity.",
        exclusions=EXCLUSIONS,
        witnesses=(
            Witness("exact-slope", f"The exact unbundled sector-{sector} slope is {sector-1}.", slope == sector - 1),
            Witness("reconstruction", "Coupling plus shortfall reconstructs the One.", sector_phenotype(sector)["coupling"] + sector_phenotype(sector)["shortfall"] == ONE),
            Witness("distinct", "The two new-sector slopes remain distinct.", sector_beta_slope(5) != sector_beta_slope(7)),
        ),
    )


PENTA_BETA_SPEC = beta_spec(PENTA_BETA_ID, 5, (PENTA_ID, "SFT-PHYS-FORCE-PRIME-SECTOR-LADDER-002", "SFT-MATH-EXACT-ARITHMETIC-001"))
HEPTA_BETA_SPEC = beta_spec(HEPTA_BETA_ID, 7, (HEPTA_ID, PENTA_BETA_ID, "SFT-PHYS-FORCE-PRIME-SECTOR-LADDER-002", "SFT-MATH-EXACT-ARITHMETIC-001"))


CENSUS_SPEC = StructuralPhysicsSpec(
    claim_id=CENSUS_ID,
    title="Category-clean complete particle census",
    statement="The finite prime-sector carrier inventory, named nonsector bosons, twelve known fermion kinds and twelve Smithion kinds form one category-clean census without omission or double counting.",
    dependencies=(HEPTA_BETA_ID, "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003", "SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-DARK-SMITHION-LFV-TERMINAL-061"),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete eight-axis product for retained predecessors, finite sector boundary, category-clean counts, carrier, confinement, inventory, measurement and extension.",
    grammar_boundary="All four admitted prime-sector carrier counts, photon/graviton/Higgs, the twelve category-distinct known fermion kinds, the twelve generated Smithion kinds, every category assignment and all 256 structural alternatives.",
    axes=axes("category-clean-total-110", "The disjoint counts 83 sector carriers, three named nonsector bosons, twelve known fermion kinds and twelve Smithion kinds add exactly once to 110."),
    exact_result="The category-clean inventory contains 83 sector gauge carriers (3, 8, 24 and 48), three named nonsector bosons (photon, graviton and Higgs), twelve known fermion kinds (three charged leptons, three neutrinos and six quarks), and twelve Smithion kinds. These disjoint categories total 110 named fundamental kinds under the declared counting convention; 72 of the gauge carriers and all twelve Smithions are standing predictions, not measured discoveries.",
    induction_base="Each category begins with a declared disjoint identity and each member is counted once.",
    induction_step="Appending the next member of a category increases exactly that category and the total by One while preserving every prior identity.",
    exclusions=EXCLUSIONS,
    witnesses=(
        Witness("sector-total", "The four sector-carrier counts total 83.", category_clean_particle_census()["gauge_carriers"] == 83),
        Witness("known-fermions", "The declared known-fermion category has twelve distinct kinds.", category_clean_particle_census()["known_fermion_kind_count"] == 12 and len(set(KNOWN_FERMION_KINDS)) == 12),
        Witness("smithions", "The Smithion category has twelve kinds.", category_clean_particle_census()["smithion_kind_count"] == 12),
        Witness("complete", "All disjoint categories total 110.", category_clean_particle_census()["category_clean_total"] == 110),
    ),
)


BOUNDARY_SPEC = StructuralPhysicsSpec(
    claim_id=BOUNDARY_ID,
    title="No-extra-sector and outside-particle falsification boundary",
    statement="The counted prime-sector ceiling and category-clean census force the first excluded prime and an explicit two-sided outside-list falsification boundary.",
    dependencies=(CENSUS_ID, "SFT-PHYS-FORCE-PRIME-SECTOR-LADDER-002", "SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-STRONG-CP-BARYON-STABILITY-TERMINAL-063"),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete eight-axis product for the finite sector ceiling, first excluded prime, category-clean list, explicit outside-list falsifiers, measurement direction and extension.",
    grammar_boundary="Prime sectors through seven, the next prime eleven, the complete category-clean total, all five named outside-list falsifier classes and all 256 structural alternatives.",
    axes=axes("first-excluded-prime-eleven-and-explicit-outside-list-falsifiers", "The counted ladder stops at seven, so eleven is the first excluded prime; every confirmed fundamental kind outside the complete category-clean list is a direct boundary falsifier."),
    exact_result="The admitted confining-sector ladder ends at prime seven and the first excluded prime is eleven. The 110-kind category-clean inventory is therefore extension-open only through a new lawful derivation that changes this boundary; under the present law, a confirmed fundamental axion, an additional sterile/fourth neutrino kind, a fundamental supersymmetric partner, a confining prime sector beyond seven, or any other confirmed fundamental kind outside the list falsifies this census. A null search is not such a discovery and does not close a standing prediction.",
    induction_base="The admitted sector list terminates at seven and the next prime is eleven.",
    induction_step="Every proposed new fundamental kind must either reconstruct an existing category identity or instantiate one explicit outside-list falsifier; it cannot be silently appended.",
    exclusions=EXCLUSIONS,
    witnesses=(
        Witness("ceiling", "Seven is the last admitted sector and eleven the first excluded prime.", no_extra_boundary()["last_admitted_sector"] == 7 and no_extra_boundary()["first_excluded_prime"] == 11),
        Witness("falsifiers", "Five explicit outside-list falsifier classes are retained.", len(no_extra_boundary()["outside_list_falsifiers"]) == 5),
        Witness("total", "The boundary retains the complete category-clean total.", no_extra_boundary()["category_clean_total"] == 110),
    ),
)


SIGNATURE_SPEC = StructuralPhysicsSpec(
    claim_id=SIGNATURE_ID,
    title="Exact Smithion interaction and search-signature law",
    statement="The closed penta/hepta fibres and absence of a generated cross-fibre mediator force exact electromagnetic, nuclear-recoil, gravitational and collider search classes for Smithions.",
    dependencies=(BOUNDARY_ID, "SFT-PHYS-DARK-SMITHION-LFV-TERMINAL-061", "SFT-PHYS-STRONG-CP-BARYON-STABILITY-TERMINAL-063", "SFT-PHYS-GRAVITY-EQUIVALENCE-001"),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete eight-axis product for each new sector's fibre, interaction carrier, confinement, category-clean signature inventory, measurement direction and extension.",
    grammar_boundary="Both new sectors, their complete neutral singlets, all admitted cross-fibre carrier records, universal gravitational response, 24/48 carrier jet classes, the lightest neutral relic record and all 256 structural alternatives.",
    axes=axes("electromagnetically-dark-no-generated-nuclear-recoil-gravity-and-confining-jet-signatures", "A complete penta/hepta singlet has no generated binary electromagnetic or cross-fibre nuclear carrier, while universal gravity and its own confining carrier inventory remain."),
    exact_result="For both penta and hepta Smithions, the complete new-sector singlet has an empty-One electromagnetic-charge record and no generated cross-fibre carrier for an ordinary nuclear-recoil interaction. Universal gravitational response remains at the One. If produced in a sufficiently energetic interaction, sector-five and sector-seven carriers form distinct confining classes with 24 and 48 mediator states, neutral 5- and 7-constituent bound states and a lightest neutral missing-carrier record. These are exact search classes; no cross section, threshold, rate or discovery is claimed without an apparatus successor.",
    induction_base="One complete new-sector singlet closes its own charge fibre while retaining universal gravitational response.",
    induction_step="Appending a lawful constituent or carrier remains within the same prime fibre; no cross-fibre electromagnetic or nuclear-recoil route appears without a separately generated mediator.",
    exclusions=EXCLUSIONS,
    witnesses=(
        Witness("dark", "Both new-sector singlets have empty electromagnetic and cross-fibre nuclear records.", all(row["electromagnetic_charge_record"] == row["cross_fibre_nuclear_recoil_carrier"] == "empty-One" for row in smithion_search_signatures().values())),
        Witness("gravity", "Both retain universal gravitational response at the One.", all(row["gravitational_response"] == ONE for row in smithion_search_signatures().values())),
        Witness("jets", "The two confining carrier classes contain 24 and 48 states.", tuple(row["confining_jet_carriers"] for row in smithion_search_signatures().values()) == (24, 48)),
        Witness("bound-states", "The neutral bound-state constituent counts are five and seven.", tuple(row["neutral_bound_constituents"] for row in smithion_search_signatures().values()) == (5, 7)),
    ),
)


SPECS = {spec.claim_id: spec for spec in (
    PENTA_SPEC,
    HEPTA_SPEC,
    PENTA_BETA_SPEC,
    HEPTA_BETA_SPEC,
    CENSUS_SPEC,
    BOUNDARY_SPEC,
    SIGNATURE_SPEC,
)}


__all__ = (
    "BOUNDARY_ID", "CENSUS_ID", "HEPTA_BETA_ID", "HEPTA_ID", "KNOWN_FERMION_KINDS",
    "NEW_SECTORS", "PENTA_BETA_ID", "PENTA_ID", "SIGNATURE_ID", "SPECS",
    "category_clean_particle_census", "no_extra_boundary", "sector_beta_slope",
    "sector_phenotype", "smithion_search_signatures",
)
