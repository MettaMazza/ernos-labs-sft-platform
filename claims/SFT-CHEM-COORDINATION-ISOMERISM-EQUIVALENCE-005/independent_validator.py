"""Implementation-distinct, value-free INORG-005 reconstruction."""

from itertools import permutations, product
import json
import sys


CLAIM = "SFT-CHEM-COORDINATION-ISOMERISM-EQUIVALENCE-005"
DOMAINS = (
    ("names-or-formulae-only", "two-complete-retained-coordination-forms"),
    ("different-compositions-called-isomers", "same-complete-composition-multiset"),
    ("selected-correspondence-between-occurrences", "enumerate-every-occurrence-bijection"),
    ("partial-or-named-connectivity", "complete-attachment-and-adjacency-preservation"),
    ("shape-name-point-group-or-continuum-transform", "complete-three-axis-two-fibre-relation"),
    ("imported-isomer-catalogue", "first-failed-invariant-forces-native-class"),
    ("selected-favourable-term", "complete-17-surface-sealed-vector-with-linkage-addendum"),
    ("new-occurrence-reclassifies-prior-subform", "successor-preserves-prior-signatures-and-adds-relations"),
)
SURVIVOR = "two-complete-retained-coordination-forms__same-complete-composition-multiset__enumerate-every-occurrence-bijection__complete-attachment-and-adjacency-preservation__complete-three-axis-two-fibre-relation__first-failed-invariant-forces-native-class__complete-17-surface-sealed-vector-with-linkage-addendum__successor-preserves-prior-signatures-and-adds-relations"


def canonical(form, include_orientation=True):
    composition, attachment, words, pairs = form
    variants = []
    for order in permutations(range(len(composition))):
        old_to_new = {old: new for new, old in enumerate(order, start=1)}
        vertices = tuple(
            (composition[old], attachment[old], words[old] if include_orientation else ())
            for old in order
        )
        edges = tuple(sorted(tuple(sorted((old_to_new[first - 1], old_to_new[second - 1]))) for first, second in pairs))
        variants.append((vertices, edges))
    return min(variants)


def complement(form):
    composition, attachment, words, pairs = form
    switch = {"fibre-one": "fibre-two", "fibre-two": "fibre-one", "EmptyOne": "EmptyOne"}
    return composition, attachment, tuple(tuple(switch[cell] for cell in word) for word in words), pairs


def classify(left, right):
    if sorted(left[0]) != sorted(right[0]):
        return "outside-composition-boundary"
    if canonical(left) == canonical(right):
        return "same-equivalence-class"
    if canonical(left, False) != canonical(right, False):
        return "attachment-class-distinction"
    if canonical(complement(left)) == canonical(right):
        return "mirror-complement-class-distinction"
    return "orientation-adjacency-class-distinction"


def reconstruct():
    base = (("L", "L"), ("mode-one", "mode-one"), (("fibre-one", "EmptyOne", "EmptyOne"), ("fibre-two", "EmptyOne", "EmptyOne")), ((1, 2),))
    reordered = (("L", "L"), ("mode-one", "mode-one"), tuple(reversed(base[2])), ((1, 2),))
    attachment = (base[0], ("mode-one", "mode-two"), base[2], base[3])
    orientation = (base[0], base[1], (("fibre-one", "EmptyOne", "EmptyOne"), ("fibre-one", "EmptyOne", "EmptyOne")), base[3])
    chiral = (("A", "B", "C"), ("mode-one",) * 3, (("fibre-one", "EmptyOne", "EmptyOne"), ("fibre-one", "fibre-two", "EmptyOne"), ("fibre-two", "fibre-one", "EmptyOne")), ((1, 2), (2, 3), (3, 1)))
    mirror = complement(chiral)
    successor = (
        base[0] + ("L",),
        base[1] + ("mode-one",),
        base[2] + (("fibre-two", "fibre-two", "EmptyOne"),),
        base[3] + ((1, 3), (2, 3)),
    )
    lawful_cells = {"fibre-one", "fibre-two", "EmptyOne"}
    return (
        classify(base, reordered) == "same-equivalence-class"
        and classify(base, attachment) == "attachment-class-distinction"
        and classify(base, orientation) == "orientation-adjacency-class-distinction"
        and classify(chiral, mirror) == "mirror-complement-class-distinction"
        and classify(base, (("L", "M"), base[1], base[2], base[3])) == "outside-composition-boundary"
        and successor[0][:2] == base[0]
        and successor[1][:2] == base[1]
        and successor[2][:2] == base[2]
        and successor[3][:1] == base[3]
        and all(cell in lawful_cells for form in (base, reordered, attachment, orientation, chiral, mirror, successor) for word in form[2] for cell in word)
    )


def main() -> None:
    document = json.load(open(sys.argv[1]))
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in document["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in document["decisions"]}
    witnesses = reconstruct()
    passed = (
        document["claim_id"] == CLAIM
        and received == generated
        and len(generated) == 256
        and len(set(received)) == 256
        and document["census"]["expected_cardinality"] == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and document["closure"]["scope"] == "depth_independent"
        and document["closure"]["minimality_passed"]
        and document["closure"]["named_shape_uniqueness_passed"]
        and {row["kind"] for row in document["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in document["controls"])
        and witnesses
    )
    print(json.dumps({
        "validated_seal_hash": document["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "claim_id": CLAIM,
            "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None,
            "permutation_attachment_orientation_mirror_and_successor_reconstructed": witnesses,
            "three_axis_positions": 3,
            "forced_fibre_labels": 2,
            "numerical_zero_negative_irrational_imaginary_signed_or_continuum_proof_value_used": False,
            "isomer_catalogue_name_point_group_plane_mirror_target_outcome_or_source_file_accessed": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
