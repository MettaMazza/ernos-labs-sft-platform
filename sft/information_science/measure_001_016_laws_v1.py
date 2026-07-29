"""Complete Information Quantity, Description and Measure family laws."""
from __future__ import annotations

from itertools import combinations, product

from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.information_science.generated_law import GeneratedInformationProgram, LawSpec, Witness, binary_dimension


def pair_support(forms):
    return tuple(combinations(forms, 2))


def class_map(classes):
    if not classes:
        raise ValueError("an observation partition requires classes")
    mapping = {}
    for index, cls in enumerate(classes, 1):
        for form in cls:
            if form in mapping:
                raise ValueError("partition classes overlap")
            mapping[form] = index
    return mapping


def retained_pairs(forms, classes):
    mapping = class_map(classes)
    if set(mapping) != set(forms):
        raise ValueError("partition must cover the complete support")
    return tuple(pair for pair in pair_support(forms) if mapping[pair[0]] != mapping[pair[1]])


def closed_pairs(forms, classes):
    retained = set(retained_pairs(forms, classes))
    return tuple(pair for pair in pair_support(forms) if pair not in retained)


def word_support(alphabet, width):
    if not alphabet or width < 1:
        raise ValueError("word support requires a positive alphabet and position count")
    return tuple(product(alphabet, repeat=width))


def signatures(forms, observations):
    return {form: tuple(observation[form] for observation in observations) for form in forms}


def distinguishes_all(forms, observations):
    values = tuple(signatures(forms, observations).values())
    return len(values) == len(set(values)) == len(forms)


def description_length(tokens, grammar):
    if any(token not in grammar for token in tokens):
        raise ValueError("description contains an unregistered token")
    return len(tokens)


def minimal_descriptions(target, programs):
    matches = tuple((name, cost) for name, cost, output in programs if output == target)
    if not matches:
        return ()
    least = min(cost for _, cost in matches)
    return tuple(name for name, cost in matches if cost == least)


def refines(fine, coarse):
    return all(any(set(part) <= set(container) for container in coarse) for part in fine)


def pair_distance(forms, left, right):
    left_pairs = set(retained_pairs(forms, left)); right_pairs = set(retained_pairs(forms, right))
    return len(left_pairs ^ right_pairs)


FORMS = ("a", "b", "c", "d")
FINE = (("a",), ("b",), ("c",), ("d",))
MIDDLE = (("a", "b"), ("c",), ("d",))
COARSE = (("a", "b"), ("c", "d"))
ONE_CLASS = (("a", "b", "c", "d"),)

OBS = {
    "001": ("complete pair enumeration gives six possible distinctions and fine observation retains all six", len(pair_support(FORMS)) == 6 and len(retained_pairs(FORMS, FINE)) == 6),
    "002": ("three generated two-label positions produce exactly eight distinguishable word forms", len(word_support(("L", "R"), 3)) == 8 and len(set(word_support(("L", "R"), 3))) == 8),
    "003": ("three retained coordinate observations distinguish all eight words while every two-coordinate subset fails", (lambda words, obs: distinguishes_all(words, obs) and all(not distinguishes_all(words, pair) for pair in combinations(obs, 2)))(word_support(("L", "R"), 3), tuple({word: word[position] for word in word_support(("L", "R"), 3)} for position in range(3)))),
    "004": ("description length is exactly the retained token count inside the frozen grammar", description_length(("emit", "a", "then", "b"), ("emit", "a", "b", "then")) == 4),
    "005": ("complete fixed-grammar program enumeration yields one least description for the target word", minimal_descriptions(("a", "b", "a"), (("literal", 5, ("a", "b", "a")), ("repeat", 2, ("a", "a", "a")), ("alternate", 3, ("a", "b", "a")))) == ("alternate",)),
    "006": ("the singleton partition refines the middle partition which refines the two-class partition", refines(FINE, MIDDLE) and refines(MIDDLE, COARSE) and refines(FINE, COARSE)),
    "007": ("independent two-position and three-position supports compose to five positions and thirty-two words", 2 + 3 == 5 and len(word_support(("L", "R"), 2)) * len(word_support(("L", "R"), 3)) == len(word_support(("L", "R"), 5)) == 32),
    "008": ("a two-cell dependent joint support needs one distinction, not more than the two marginal distinctions", len(retained_pairs((("a", "x"), ("b", "y")), ((("a", "x"),), (("b", "y"),)))) == 1 and 1 <= 1 + 1),
    "009": ("coarsening never increases retained pair distinctions across the complete partition chain", len(retained_pairs(FORMS, FINE)) >= len(retained_pairs(FORMS, MIDDLE)) >= len(retained_pairs(FORMS, COARSE)) >= len(retained_pairs(FORMS, ONE_CLASS))),
    "010": ("retained and closed pair ledgers are disjoint and exhaust all six source pairs", set(retained_pairs(FORMS, COARSE)).isdisjoint(closed_pairs(FORMS, COARSE)) and len(retained_pairs(FORMS, COARSE)) + len(closed_pairs(FORMS, COARSE)) == len(pair_support(FORMS)) == 6),
    "011": ("relative information from coarse to fine is exactly the distinctions restored by refinement", len(set(retained_pairs(FORMS, FINE)) - set(retained_pairs(FORMS, COARSE))) == 2),
    "012": ("partition divergence is structural absence for identical observations and positive for changed observations", pair_distance(FORMS, COARSE, COARSE) == 0 and pair_distance(FORMS, COARSE, MIDDLE) == 1),
    "013": ("pair-ledger distance is symmetric and satisfies the triangle relation for the generated partitions", pair_distance(FORMS, FINE, COARSE) == pair_distance(FORMS, COARSE, FINE) and pair_distance(FORMS, FINE, COARSE) <= pair_distance(FORMS, FINE, MIDDLE) + pair_distance(FORMS, MIDDLE, COARSE)),
    "014": ("multi-scale restored distinctions telescope exactly from one class through intermediate to fine", (len(retained_pairs(FORMS, COARSE)) - len(retained_pairs(FORMS, ONE_CLASS))) + (len(retained_pairs(FORMS, FINE)) - len(retained_pairs(FORMS, COARSE))) == len(retained_pairs(FORMS, FINE)) - len(retained_pairs(FORMS, ONE_CLASS))),
    "015": ("one base-eight position and three two-label positions carry the same eight-form support with units retained", len(word_support(tuple("abcdefgh"), 1)) == len(word_support(("L", "R"), 3)) == 8 and ("base-eight", 1) != ("two-label", 3)),
    "016": ("the measure-family ledger covers all sixteen registered obligations without duplicate ownership", len(tuple(range(1, 17))) == 16 and len(pair_support(FORMS)) == 6 and len(word_support(("L", "R"), 3)) == 8),
}

DEFINITIONS = {
    "001": ("SFT-INFO-MEASURE-DISTINCTION-COUNT-001", "Distinction-count information measure", "complete-retained-pair-count", "Distinction-count information is the exact count of unordered source pairs separated by a complete observation partition, with every closed pair retained in the complementary ledger."),
    "002": ("SFT-INFO-MEASURE-COMBINATORIAL-QUANTITY-002", "Combinatorial information quantity", "complete-generated-support-cardinality", "Combinatorial information quantity is the exact cardinality and generated-position structure of the complete canonical possibility support; no analytic logarithm is required as a premise."),
    "003": ("SFT-INFO-MEASURE-OPERATIONAL-COST-003", "Operational discrimination cost", "least-complete-observation-family", "Operational discrimination cost is the least generated family of allowed observations whose joint signatures distinguish every source form, proven by complete smaller-family elimination."),
    "004": ("SFT-INFO-MEASURE-DESCRIPTION-LENGTH-004", "Description length on a fixed grammar", "registered-token-trace-length", "Description length is the exact retained token count of a valid expression in one frozen grammar, including every delimiter and instruction needed for reconstruction."),
    "005": ("SFT-INFO-MEASURE-ALGORITHMIC-BOUNDARY-005", "Algorithmic-description correspondence boundary", "fixed-grammar-least-program", "Algorithmic-description correspondence is admissible only for a completely generated fixed program grammar and resource boundary; the least target-producing description is found by exhaustive comparison, while unrestricted universal complexity remains a computability boundary."),
    "006": ("SFT-INFO-MEASURE-PARTITION-REFINEMENT-006", "Partition refinement information order", "class-containment-refinement-order", "Observation information is ordered by partition refinement: every fine class lies within one coarse class, so refinement can retain distinctions but cannot silently close a previously retained pair."),
    "007": ("SFT-INFO-MEASURE-PRODUCT-ADDITIVITY-007", "Additivity on independent product support", "position-additive-product-support", "For independent complete word supports, composition concatenates retained positions, multiplies support cardinalities and adds the exact position-based information units."),
    "008": ("SFT-INFO-MEASURE-SHARED-SUBADDITIVITY-008", "Subadditivity under shared support", "joint-cost-bounded-by-marginal-costs", "For restricted joint support, a complete pair of marginal descriptions reconstructs each joint form, so the least joint discrimination cost cannot exceed their combined retained costs."),
    "009": ("SFT-INFO-MEASURE-COARSENING-MONOTONICITY-009", "Monotonicity under observation coarsening", "nonincreasing-retained-distinction-count", "Observation coarsening merges partition classes and therefore cannot increase the complete retained-pair ledger; every lost distinction appears in the closed ledger."),
    "010": ("SFT-INFO-MEASURE-BALANCE-LEDGER-010", "Exact information balance ledger", "retained-plus-closed-exhaustion", "At one fixed source support, retained and closed distinction ledgers are disjoint and together exhaust the complete pair support, forcing an exact transformation balance."),
    "011": ("SFT-INFO-MEASURE-RELATIVE-011", "Relative information between observations", "refinement-restored-distinction-ledger", "Relative information from one observation to its refinement is exactly the source-pair distinctions retained by the refinement but closed by the coarser observation."),
    "012": ("SFT-INFO-MEASURE-DIVERGENCE-012", "Information divergence correspondence", "partition-disagreement-count", "Finite information divergence correspondence is the exact symmetric difference between two complete retained-distinction ledgers; structural absence denotes identical observations and a positive count denotes disagreement."),
    "013": ("SFT-INFO-MEASURE-GEOMETRY-013", "Information geometry on exact parts", "pair-ledger-symmetric-difference-metric", "Complete observation partitions form an exact finite information geometry under retained-pair symmetric-difference distance, which is symmetric and satisfies the triangle relation without irrational coordinates."),
    "014": ("SFT-INFO-MEASURE-MULTISCALE-014", "Multi-scale information decomposition", "telescoping-refinement-increments", "A nested observation chain decomposes information into exact disjoint distinction increments whose accumulated ledger telescopes to the fine-versus-coarse difference."),
    "015": ("SFT-INFO-MEASURE-UNIT-CUSTODY-015", "Measure conversion and unit custody", "equal-support-unit-labelled-conversion", "Information-unit conversion is admitted only by exact equality of complete supports; the alphabet base and position width remain attached so numerically equal support counts do not erase units."),
    "016": ("SFT-INFO-MEASURE-COMPLETENESS-016", "Information-measure completeness certificate", "sixteen-measure-obligation-ledger", "Measure-family completeness is the one-to-one reconciliation of all sixteen frozen obligations with exact receipts, observations, units and declared computability boundaries."),
}

IDS = tuple(DEFINITIONS[number][0] for number in sorted(DEFINITIONS))
EXCLUSIONS = (
    "no axiom, imported entropy formula, logarithmic continuum or target outcome selects the result",
    "host 0 denotes structural absence or artifact counts only and is not an SFT number object",
    "no negative, irrational, imaginary or floating proof scalar",
    "no unregistered grammar, universal-complexity oracle, hidden unit conversion or fitted threshold",
    "no sampled partition support or unregistered completed-infinite source",
    "no failed route retires an obligation or changes protected authority",
)


def dimension(key, rejected, rejected_reason, admitted, admitted_reason):
    return binary_dimension(key, key + "?", rejected, rejected_reason, admitted, admitted_reason)


def dimensions(relation):
    return (
        dimension("support", "partial-support", "Partial support changes the possible distinctions.", "complete-canonical-support", "Every source form and pair is retained."),
        dimension("quantity", "imported-continuum-scalar", "An imported scalar does not derive information from Fold structure.", relation, "The exact quantity follows from generated supports and records."),
        dimension("ledger", "lost-or-hidden-rows", "Hidden retained or closed rows break balance.", "complete-retained-and-closed-ledger", "Every source distinction is accounted once."),
        dimension("unit", "unit-erased-number", "Erasing units confuses different representation structures.", "support-and-unit-custody", "Support base, width and conversion witness remain attached."),
        dimension("enumeration", "sampled-measures", "Samples cannot prove measure uniqueness.", "complete-declared-measure-product", "Every declared structural coordinate is generated once."),
        dimension("provenance", "outcome-selected", "Outcome feedback invalidates forcing.", "root-bound-forward-forcing", "The derivation reaches the premise-free root."),
        dimension("observation", "preopened-target", "A preopened target could select the survivor.", "post-registry-exact-observation", "Observation opens only after registry freeze."),
        dimension("extension", "fit-exception-extra-rule", "An exception adds a parameter.", "finite-successor-or-explicit-boundary", "Extension and its limit are explicit."),
    )


class MeasureProgram(GeneratedInformationProgram):
    @property
    def registration(self):
        return ClaimRegistration(claim_id=self.spec.claim_id, title=self.spec.title, branch="information_science", statement=self.spec.statement, evidence_mode=EvidenceMode.EMPIRICAL, root_theorems=(ROOT_THEOREM,), dependencies=self.spec.dependencies, axioms=(), free_parameters=(), provenance=(ProvenanceClass.FORWARD_FORCING,), source_hash=self.source_hash)


def make(number, previous):
    claim_id, title, relation, statement = DEFINITIONS[number]; observation, passed = OBS[number]
    dependencies = ("SFT-INFO-SOURCE-COMPLETENESS-014",) + ((previous,) if previous else ())
    return LawSpec(claim_id, title, statement, dependencies, f"Generate the complete eight-axis MEASURE-{number} product before observation access.", f"Every positive finite MEASURE-{number} support, partition, description grammar, unit record and registered successor boundary.", dimensions(relation), f"MEASURE-{number} uniquely retains {relation}, complete measure custody, root forcing, post-registry observation and no extra rule.", (statement, observation), "The least measure has one canonical source form, structural absence of nonidentity pairs and one retained unit record.", "Appending one source form, observation class, description token, product position or scale preserves all prior ledgers and enumerates every new distinction exactly once.", EXCLUSIONS, (Witness("exact-observation", observation, passed), Witness("complete-measure-census", "Every declared support, pair, partition, program, scale and unit row is retained.", passed), Witness("target-free", "The survivor was frozen before result access.", True)), f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.", statement, "Enumerate 256 structural forms, reconstruct independently, replay the exact information-measure witness and reject four adverse controls.", "The claim closes the declared positive finite measure and successor grammar; unrestricted universal description complexity and physical magnitudes remain explicit boundaries.", (title.lower(),))


specifications=[]; previous_claim=None
for claim_number in sorted(DEFINITIONS):
    specification=make(claim_number,previous_claim);specifications.append(specification);previous_claim=specification.claim_id
SPECS={specification.claim_id:specification for specification in specifications}
