"""Complete Materials cross-branch ownership and handoff laws."""
from dataclasses import dataclass
import json
from pathlib import Path

from sft.engine import ClaimRegistration, EvidenceMode, ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram, StructuralPhysicsSpec, Witness, binary_axis

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "census/materials_hand_001_006_dependency_registry_v1.json"
REGISTRY_FILE_HASH = "sha256:8b9673ba5628747dd0066b89de85082310e0156c3df064f1d8e413c35888ca2d"
REGISTRY = json.loads(REGISTRY_PATH.read_text())
VALID_LOCK = "SFT-MAT-VALIDATION-EMPIRICAL-GRAND-LOCK-012"
DEFINITIONS = {
    "001": ("SFT-MAT-ENGINEERING-OWNERSHIP-HANDOFF-001", "Materials-to-Engineering one-owner handoff", "materials owns specimen organization, processing history and response while engineering owns designed use and implementation", "engineering_translation"),
    "002": ("SFT-MAT-BIOLOGY-OWNERSHIP-HANDOFF-002", "Materials-to-Biology one-owner handoff", "materials owns the material interface and response while biology owns living organization, adhesion and function", "biology"),
    "003": ("SFT-MAT-MEDICINE-OWNERSHIP-HANDOFF-003", "Materials-to-Medicine one-owner handoff", "materials owns delivery-medium organization and release while medicine owns intervention, dose and health outcome", "medicine"),
    "004": ("SFT-MAT-EARTH-ENVIRONMENT-OWNERSHIP-HANDOFF-004", "Materials-to-Earth and Environmental Science one-owner handoff", "materials owns material lifecycle and end-of-life custody while Earth and Environmental Science owns environmental path and receptor context", "earth_environment"),
    "005": ("SFT-MAT-ASTRONOMY-OWNERSHIP-HANDOFF-005", "Materials-to-Astronomy one-owner handoff", "materials owns radiation-conditioned response while astronomy owns the emitting source and cosmic observational context", "astronomy_cosmology"),
    "006": ("SFT-MAT-CROSS-BRANCH-ONE-OWNER-COMPLETENESS-006", "Materials cross-branch one-owner completeness certificate", "every frozen admitted claim has exactly one owner and every downstream use is a dependency edge rather than duplicate ownership", "all_registered_branches"),
}
IDS = tuple(DEFINITIONS[n][0] for n in sorted(DEFINITIONS))


@dataclass(frozen=True)
class HandoffSpec(StructuralPhysicsSpec):
    number: str = ""
    paired_claim_ids: tuple[str, ...] = ()
    downstream_owner: str = ""

    def validate(self):
        if not self.claim_id.startswith("SFT-MAT-") or len(self.axes) != 8 or not self.dependencies:
            raise ValueError("incomplete Materials HAND spec")
        if self.number != "006":
            registered = tuple(REGISTRY["paired_claim_ids"][self.number])
            if self.paired_claim_ids != registered or len(set(registered)) != len(registered):
                raise ValueError("Materials HAND paired identities changed")
        if REGISTRY["target_content_present"] is not False or REGISTRY["root_reachable_claim_count"] != REGISTRY["base_claim_count"]:
            raise ValueError("Materials HAND registry is not value-free and root-complete")
        for axis in self.axes:
            if len(axis.choices) != 2:
                raise ValueError("Materials HAND grammar incomplete")
            axis.survivor
        if not all(witness.passed for witness in self.witnesses):
            raise ValueError("Materials HAND witness failed")


class HandoffProgram(StructuralPhysicsProgram):
    @property
    def registration(self):
        return ClaimRegistration(
            claim_id=self.spec.claim_id,
            title=self.spec.title,
            branch="materials",
            statement=self.spec.statement,
            evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=self.spec.dependencies,
            axioms=(),
            free_parameters=(),
            provenance=self.spec.provenance,
            source_hash=self.source_hash,
        )


EXCLUSIONS = (
    "no downstream outcome, preferred owner, measurement value or match result selects the law",
    "no branch may duplicate ownership of a coordinate it consumes",
    "no application record may redefine a natural-law owner",
    "no missing dependency or source record is silently ignored",
    "no fitted threshold, aggregate score, numerical zero, negative, irrational, imaginary or floating proof magnitude",
    "no failed route retires an obligation",
    "no engine, verifier, prior receipt, certificate or admitted claim change",
)


def axes(relation):
    return (
        binary_axis("subject", "What crosses the branch boundary?", "anonymous-cross-branch-result", "An anonymous result loses the owned coordinate.", "complete-owned-coordinate", "The substance, structure, response or context carrier is explicit."),
        binary_axis("ownership", "How is ownership assigned?", "overlapping-or-ownerless", "Duplicate or absent ownership destroys exact provenance.", "exactly-one-owner", "Every coordinate has one declared branch owner."),
        binary_axis("relation", "What constitutes the handoff?", "branch-name-association", "A label alone is not a handoff.", relation, "The directed ownership boundary is explicit."),
        binary_axis("dependency", "How does a downstream branch consume a law?", "copied-law", "Copying a law creates duplicate ownership.", "directed-consumer-edge", "A downstream branch consumes the source law through a named dependency."),
        binary_axis("records", "Which evidence records remain?", "selected-summary", "A summary can hide one side of the boundary.", "complete-paired-receipt-records", "Both source and downstream records retain receipts and external evidence."),
        binary_axis("custody", "When may empirical outcomes open?", "outcome-before-registration", "Outcome access may choose the boundary.", "value-free-registry-before-outcomes", "Owner and claim identities are frozen before empirical rows open."),
        binary_axis("falsification", "What invalidates the boundary?", "omission-tolerated", "A missing owner, record or edge cannot close.", "duplicate-missing-or-tampered-halts", "Duplicate, missing, changed or ownerless rows halt."),
        binary_axis("extension", "How may the graph grow?", "permanent-branch-lock", "A dated graph cannot bar discovery.", "dated-complete-extension-open", "New lawful claims extend the graph with one explicit owner."),
    )


def make(number, previous):
    cid, title, relation_text, downstream = DEFINITIONS[number]
    paired = tuple(REGISTRY["paired_claim_ids"].get(number, ()))
    if number == "006":
        dependencies = (VALID_LOCK,) + IDS[:5]
        statement = f"Across the complete frozen graph of {REGISTRY['base_claim_count']} admitted claims and {REGISTRY['dependency_edge_count']} dependency edges, every claim has exactly one branch owner, every claim reaches the root theorem, and cross-branch use remains a directed dependency rather than duplicate ownership."
        relation = "complete-one-owner-root-traced-consumer-graph"
        exact = f"HAND-006 uniquely requires one owner for each of {REGISTRY['base_claim_count']} frozen claims, complete root reachability, and all {REGISTRY['dependency_edge_count']} directed dependency edges, with lawful extension adding rather than rewriting ownership."
    else:
        dependencies = (VALID_LOCK,) + paired + ((previous,) if previous else ())
        statement = f"The Materials handoff to {downstream} preserves complete paired admitted records and exactly one owner per coordinate: {relation_text}."
        relation = f"materials-to-{downstream}-directed-one-owner-handoff"
        exact = f"HAND-{number} uniquely requires the complete receipt-bound pair in which {relation_text}; consumption is a directed dependency and never duplicate ownership."
    return HandoffSpec(
        claim_id=cid,
        title=title,
        statement=statement,
        dependencies=dependencies,
        evidence_mode=EvidenceMode.EMPIRICAL,
        generation_rule=f"Generate the complete eight-axis HAND-{number} ownership product before opening the registered paired evidence.",
        grammar_boundary=f"Exactly the registered HAND-{number} owner identities, directed relations, paired receipt records, controls and extension boundary.",
        axes=axes(relation),
        exact_result=exact,
        induction_base="The first owned coordinate retains one branch, one source claim and its complete record.",
        induction_step="Each appended consumer retains every prior owner and adds one directed dependency; duplicate or missing ownership halts.",
        exclusions=EXCLUSIONS,
        witnesses=(
            Witness("value-free", "The owner registry contains no target outcomes.", REGISTRY["target_content_present"] is False),
            Witness("one-owner", "Every frozen claim has one owner.", REGISTRY["unique_owner_count"] == REGISTRY["base_claim_count"]),
            Witness("root-trace", "Every frozen claim reaches the root theorem.", REGISTRY["root_reachable_claim_count"] == REGISTRY["base_claim_count"]),
            Witness("paired-or-complete", "The law has its registered pair or complete graph.", bool(paired) or number == "006"),
        ),
        number=number,
        paired_claim_ids=paired,
        downstream_owner=downstream,
    )


specs = []
previous = None
for number in sorted(DEFINITIONS):
    spec = make(number, previous)
    specs.append(spec)
    previous = spec.claim_id
SPECS = {spec.claim_id: spec for spec in specs}
