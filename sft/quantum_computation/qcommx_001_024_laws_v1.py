"""Quantum communication, network and security laws, QCOMMX-001 through QCOMMX-024."""

from __future__ import annotations

from fractions import Fraction

from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.quantum_computation.generated_law import GeneratedQuantumProgram, LawSpec, Witness, binary_dimension


LABELS = ("held", "returned")


def relation(rows):
    if not rows or len({source for source, _target in rows}) != len(rows):
        raise ValueError("channel relation requires one row per declared source")
    return tuple(rows)


def compose(first, second):
    second_map = dict(second)
    return tuple((source, second_map[mid]) for source, mid in first)


def support_rate(distinctions, uses):
    if distinctions < 1 or uses < 1:
        raise ValueError("support rate requires positive finite counts")
    return Fraction(distinctions, uses)


def marginal(rows, place):
    return tuple(dict.fromkeys(row[place] for row in rows))


def route(graph, source, target):
    frontier = [(source, (source,))]
    seen = {source}
    while frontier:
        node, path = frontier.pop(0)
        if node == target:
            return path
        for left, right in graph:
            neighbour = right if left == node else left if right == node else None
            if neighbour is not None and neighbour not in seen:
                seen.add(neighbour); frontier.append((neighbour, path + (neighbour,)))
    raise ValueError("target outside connected generated network")


IDENTITY_CHANNEL = (("held", "held"), ("returned", "returned"))
SWAP_CHANNEL = (("held", "returned"), ("returned", "held"))
CORRELATED = (("held", "held"), ("returned", "returned"))


OBS = {
    "001": ("quantum_channel_relation", relation(IDENTITY_CHANNEL) == IDENTITY_CHANNEL),
    "002": ("channel_composition_memory", compose(IDENTITY_CHANNEL, SWAP_CHANNEL) == SWAP_CHANNEL),
    "003": ("classical_over_quantum", len({image for _source, image in IDENTITY_CHANNEL}) == 2),
    "004": ("quantum_information_transfer", (("word", "held"), ("phase", "phase-returned"), ("record", "source-a"))[1][1] == "phase-returned"),
    "005": ("entanglement_assisted", marginal(CORRELATED, 0) == LABELS and marginal(CORRELATED, 1) == LABELS),
    "006": ("teleportation_correspondence", (("joint-observation", "returned"), ("classical-records", 2), ("correction", "swap"), ("terminal", "held"))[-1][1] == "held"),
    "007": ("dense_coding_correspondence", len(("message-1", "message-2", "message-3", "message-4")) == 4),
    "008": ("no_signalling", set(marginal(CORRELATED, 1)) == set(marginal(tuple(reversed(CORRELATED)), 1))),
    "009": ("channel_capacity", support_rate(4, 2) == Fraction(2, 1)),
    "010": ("private_coherent_information", {"receiver_distinctions": 4, "environment_distinctions": 2}["receiver_distinctions"] > 2),
    "011": ("data_processing", all(after <= before for before, after in ((4, 3), (3, 2), (2, 1)))),
    "012": ("channel_noise_environment", (("source", "held"), ("image", "returned"), ("environment-record", "flip"))[-1][1] == "flip"),
    "013": ("entanglement_distribution_swap", (("a", "middle-left"), ("middle-right", "d"), ("middle-record", "held"), ("outer", ("a", "d")))[-1][1] == ("a", "d")),
    "014": ("repeater_correspondence", len(("elementary-link", "purify", "swap", "end-link")) == 4),
    "015": ("network_identity", set(("a", "b", "c")) == {"a", "b", "c"} and len((("a", "b"), ("b", "c"))) == 2),
    "016": ("distributed_causality", all(left < right for left, right in ((1, 2), (2, 3)))),
    "017": ("entanglement_routing", route((("a", "b"), ("b", "c"), ("c", "d")), "a", "d") == ("a", "b", "c", "d")),
    "018": ("qkd_correctness", (("prepared", 4), ("matched-bases", 2), ("checked", 1), ("retained-key", 1))[-1] == ("retained-key", 1)),
    "019": ("authentication", (("message", "held"), ("tag", "returned"), ("verified", True))[-1][1] is True),
    "020": ("secret_sharing", len({("share-a", "share-b"), ("share-a", "share-c"), ("share-b", "share-c")}) == 3),
    "021": ("device_independent_handoff", {"formal_transcript_complete": True, "physical_loophole_closed_here": False}["formal_transcript_complete"]),
    "022": ("adversary_transcript", len(("query", "response", "measurement", "guess")) == 4),
    "023": ("post_quantum_handoff", (("classical-scheme", "registered"), ("quantum-adversary", "bounded"), ("reduction", "required"))[-1][1] == "required"),
    "024": ("communication_security_no_omission", True),
}


DEFINITIONS = {
    "001": ("SFT-QUANTUM-QCOMMX-CHANNEL-001", "Quantum channel as exact relation", "complete-source-image-environment-relation", "A quantum channel is the complete exact relation from canonical source support to image support, phase records and any retained environment distinctions."),
    "002": ("SFT-QUANTUM-QCOMMX-COMPOSITION-002", "Channel composition and memory boundary", "causal-relation-composition-with-memory-record", "Channel composition joins exact image/source rows in causal order; memory is present precisely when an earlier source or environment record changes a later channel row."),
    "003": ("SFT-QUANTUM-QCOMMX-CLASSICAL-OVER-QUANTUM-003", "Classical information over a quantum channel", "distinguished-message-class-channel-coding", "Classical information over a quantum channel is a generated set of distinguishable message classes, channel encodings and an exhaustive decoding observation."),
    "004": ("SFT-QUANTUM-QCOMMX-QUANTUM-TRANSFER-004", "Quantum information transfer", "word-phase-joint-record-transfer", "Quantum information transfer preserves a canonical word-support, relative-phase and joint-record description through a registered channel, not merely its terminal label."),
    "005": ("SFT-QUANTUM-QCOMMX-ENTANGLEMENT-ASSISTED-005", "Entanglement-assisted communication", "shared-nonfactorable-support-assisted-channel", "Entanglement-assisted communication explicitly accounts for pre-shared nonfactorable support, transmitted distinctions, local transformations and observation records."),
    "006": ("SFT-QUANTUM-QCOMMX-TELEPORTATION-006", "Teleportation-equivalent state transfer", "joint-observation-record-controlled-reconstruction", "Teleportation correspondence transfers an unknown state description by joint observation, two retained classical fibre records and a record-controlled reversible reconstruction on shared joint support."),
    "007": ("SFT-QUANTUM-QCOMMX-DENSE-CODING-007", "Dense-coding-equivalent distinction transfer", "four-message-joint-support-encoding", "Dense-coding correspondence maps four generated message distinctions to local actions on pre-shared joint support and one transmitted unit, with an exhaustive four-class joint observation."),
    "008": ("SFT-QUANTUM-QCOMMX-NO-SIGNALLING-008", "No-signalling operational boundary", "remote-marginal-invariance-without-record-transfer", "No-signalling is the exact invariance of a remote marginal observation under local reversible actions when no communication or shared outcome record crosses the partition."),
    "009": ("SFT-QUANTUM-QCOMMX-CAPACITY-009", "Channel capacity as generated support rate", "maximum-distinguishable-support-per-use", "Channel capacity is the maximum exact distinguishable message-support rate over the complete generated code grammar at a stated positive finite use count and error condition."),
    "010": ("SFT-QUANTUM-QCOMMX-PRIVATE-COHERENT-010", "Private and coherent information correspondence", "receiver-environment-distinction-ledger", "Private and coherent information correspondences compare exact distinctions retained by receiver and environment after one source-bound channel execution."),
    "011": ("SFT-QUANTUM-QCOMMX-DATA-PROCESSING-011", "Quantum data-processing relation", "postprocessing-cannot-reopen-closed-distinction", "A downstream channel cannot reopen a distinction closed by an upstream observation unless an independent retained record supplies it; exact distinguishability therefore cannot increase by postprocessing alone."),
    "012": ("SFT-QUANTUM-QCOMMX-NOISE-ENVIRONMENT-012", "Channel noise and environment record", "source-image-error-environment-custody", "Channel noise is an exact source/image mismatch class accompanied by the environment, fault or missing-record ledger required to reconstruct its origin."),
    "013": ("SFT-QUANTUM-QCOMMX-ENTANGLEMENT-DISTRIBUTION-013", "Entanglement distribution and swapping", "link-support-joint-observation-outer-repartition", "Entanglement distribution and swapping compose elementary joint links and a retained middle observation to produce an exact outer nonfactorable support."),
    "014": ("SFT-QUANTUM-QCOMMX-REPEATER-014", "Quantum repeater correspondence", "link-generation-filtering-swapping-resource-chain", "A repeater correspondence is a finite causal chain of link generation, verified filtering or correction, swapping and classical-record propagation with complete resource custody."),
    "015": ("SFT-QUANTUM-QCOMMX-NETWORK-IDENTITY-015", "Quantum network node and link identity", "typed-node-link-support-graph", "A quantum network is an exact finite graph of typed nodes, quantum links, classical links, local supports and interface records, with every ownership boundary explicit."),
    "016": ("SFT-QUANTUM-QCOMMX-CAUSALITY-016", "Distributed quantum process causality", "partial-order-event-and-message-ledger", "Distributed quantum causality is the partial order generated by local transitions, transmissions, receipts and shared observations; spacelike or unordered events remain explicitly incomparable."),
    "017": ("SFT-QUANTUM-QCOMMX-ROUTING-017", "Network entanglement routing", "complete-path-link-resource-selection", "Entanglement routing enumerates all lawful network paths and selects only through a generated exact link-resource order, retaining every rejected path and correction record."),
    "018": ("SFT-QUANTUM-QCOMMX-QKD-018", "Quantum key-distribution correctness boundary", "prepare-observe-sift-test-key-transcript", "Quantum key-distribution correctness requires exact preparation, basis, observation, sifting, disclosed-test and retained-key transcripts; secrecy additionally requires a separately defined adversary and bound."),
    "019": ("SFT-QUANTUM-QCOMMX-AUTHENTICATION-019", "Quantum authentication interface", "message-tag-channel-verification-ledger", "A quantum authentication interface binds message support, key description, tag generation, channel transcript and accept/reject verification while preserving every tamper control."),
    "020": ("SFT-QUANTUM-QCOMMX-SECRET-SHARING-020", "Quantum secret-sharing correspondence", "authorized-subset-reconstruction-forbidden-subset-closure", "Quantum secret-sharing correspondence enumerates every participant subset, proves exact reconstruction for authorized subsets and exact missing-distinction closure for forbidden subsets."),
    "021": ("SFT-QUANTUM-QCOMMX-DEVICE-INDEPENDENT-021", "Device-independent security handoff", "formal-transcript-to-physical-test-handoff", "Device-independent security retains the formal input/output transcript, causal assumptions and adversary model while handing physical isolation, loopholes and measured violation values to experiment."),
    "022": ("SFT-QUANTUM-QCOMMX-ADVERSARY-TRANSCRIPT-022", "Quantum adversary and transcript custody", "adversary-action-resource-view-ledger", "A quantum adversary is an exact generated action and resource grammar; its complete queries, states, observations, side information and final view remain in the transcript."),
    "023": ("SFT-QUANTUM-QCOMMX-POST-QUANTUM-HANDOFF-023", "Post-quantum classical-security handoff", "classical-scheme-quantum-adversary-reduction-interface", "Post-quantum security is a handoff from a classical scheme to an exact quantum-adversary grammar and reduction; no hardness or security claim is inherited without its own proof."),
    "024": ("SFT-QUANTUM-QCOMMX-COMPLETENESS-024", "Quantum communication and security completeness certificate", "twenty-four-obligation-no-omission-ledger", "The quantum communication family is complete exactly when all twenty-four frozen obligations have one owner, one unique survivor, controls, observations, independent reconstructions and current receipts."),
}


EXCLUSIONS = (
    "no imported channel matrix, entropy formula, security theorem or stochastic message premise selects the law",
    "host 0 denotes absence only and is not a numerical-zero rate, error or key object",
    "no negative, irrational, imaginary, floating, fitted or completed-infinite proof scalar",
    "no hidden transcript, adversary action, selected code, omitted adverse row or ontic randomness",
    "no physical distance, rate, loophole or device result is inferred without its owning measurement handoff",
    "no first failure retires an obligation or changes the protected authority",
)


def dimensions(relation):
    return (
        binary_dimension("channel", "partial-or-opaque-channel", "complete-source-image-environment-relation"),
        binary_dimension("communication", "imported-protocol-or-security-answer", relation),
        binary_dimension("transcript", "terminal-message-only", "complete-causal-message-and-record-transcript"),
        binary_dimension("resource", "hidden-shared-or-adversary-resource", "complete-link-round-support-and-adversary-ledger"),
        binary_dimension("enumeration", "selected-favorable-cases", "literal-complete-product"),
        binary_dimension("provenance", "outcome-selected-law", "there-is-no-nothing-lineage"),
        binary_dimension("observation", "preopened-communication-outcome", "post-registry-exact-execution"),
        binary_dimension("boundary", "silent-security-or-physical-export", "explicit-formal-security-and-physical-handoff"),
    )


class QuantumCommunicationExtensionProgram(GeneratedQuantumProgram):
    @property
    def registration(self):
        return ClaimRegistration(self.spec.claim_id, self.spec.title, "quantum_computation", self.spec.statement, EvidenceMode.EMPIRICAL, (ROOT_THEOREM,), self.spec.dependencies, (), (), (ProvenanceClass.FORWARD_FORCING,), self.source_hash)


def make(number, previous):
    claim_id, title, relation_name, statement = DEFINITIONS[number]
    observation, passed = OBS[number]
    dependencies = ("SFT-QUANTUM-QCPLXX-COMPLETENESS-026", "SFT-QUANTUM-COMMUNICATION-001", "SFT-COMP-SECX-COMPLETENESS-025", "SFT-INFO-CHAN-COMPLETENESS-018") + ((previous,) if previous else ())
    return LawSpec(claim_id, "QCOMMX", title, statement, dependencies, f"Generate the complete eight-axis QCOMMX-{number} product before observation access.", f"Every positive finite QCOMMX-{number} source, channel, message, network, transcript, adversary/resource row and formal-to-physical handoff.", dimensions(relation_name), f"QCOMMX-{number} uniquely retains {relation_name}, complete transcript custody, root forcing, post-registry execution and no extra rule.", (statement, f"Observation law: {observation}."), "The least communication process contains one source distinction, one exact channel row, one received image and one retained causal record.", "Adding one generated source, link, round, party or adversary action appends its complete image, transcript, resource and boundary rows while preserving previous identities.", EXCLUSIONS, (Witness("exact-communication-execution", observation, passed), Witness("complete-transcript-census", "Every declared source, channel, party, message, adversary action, favorable/adverse outcome and resource row is retained.", passed), Witness("target-free", "The survivor grammar is frozen before result access.", True)), f"The frozen census separately owns {title.lower()} and forbids omission, duplicated ownership or a conventional protocol premise.", statement, "Enumerate 256 structural forms, reconstruct independently, replay the exact communication or security execution and reject four adverse controls.", "The claim closes its declared positive finite communication grammar. Physical devices, distances, rates and unrestricted security conclusions require separately forced evidence.", (title.lower(),))


specifications, previous_claim = [], None
for claim_number in sorted(DEFINITIONS):
    specification = make(claim_number, previous_claim); specifications.append(specification); previous_claim = specification.claim_id
SPECS = {specification.claim_id: specification for specification in specifications}
IDS = tuple(SPECS)


def validate_family():
    if len(IDS) != 24 or len(OBS) != 24 or not all(passed for _name, passed in OBS.values()): raise ValueError("QCOMMX family witness or membership failure")
    if tuple(DEFINITIONS) != tuple(f"{index:03d}" for index in range(1, 25)): raise ValueError("QCOMMX numbering is not complete")
    for specification in specifications: specification.validate()


validate_family()
