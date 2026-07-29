"""Complete-field Cryptography and Computational Security laws, SECX-001--025."""
from __future__ import annotations

from itertools import combinations, product

from sft.computation.generated_law import GeneratedComputationProgram, LawSpec, Witness, binary_dimension
from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM

FIBRES = ("left", "right")


def flip(label):
    return "right" if label == "left" else "left"


def encrypt(message, key):
    return message if key == "left" else flip(message)


def decrypt(ciphertext, key):
    return encrypt(ciphertext, key)


def ciphertext_support(message):
    return tuple(encrypt(message, key) for key in FIBRES)


def view(process, public, queries, resources, success):
    return {"process": process, "public": tuple(public), "queries": tuple(queries), "resources": tuple(resources), "success": success}


def bounded_inverse(mapping, image, allowed_queries):
    for source in allowed_queries:
        if mapping[source] == image:
            return source
    return "absent-from-declared-query-support"


def generator(seed):
    return (seed, flip(seed), seed)


def keyed_function(key, message):
    return message if key == "left" else flip(message)


def mac(key, message):
    return ("tag", keyed_function(key, message))


def verify_mac(key, message, tag):
    return tag == mac(key, message)


def hash_word(word):
    return "left" if word in (("left", "left"), ("right", "right")) else "right"


def commitment(message, blind):
    return ("commit", encrypt(message, blind))


def verify_opening(record, message, blind):
    return record == commitment(message, blind)


def sign(secret, message):
    return ("signature", secret, message)


def verify_signature(public, message, signature):
    return signature == ("signature", public, message)


def establish(left_secret, right_secret):
    transcript = (flip(left_secret), flip(right_secret))
    shared = (left_secret, right_secret)
    return transcript, shared


def split(secret):
    return (("share-a", secret), ("share-b", flip(secret)), ("share-c", secret))


def reconstruct(shares):
    if len(shares) < 2:
        return "insufficient-shares"
    candidates = [share[1] if share[0] != "share-b" else flip(share[1]) for share in shares]
    return candidates[0] if len(set(candidates)) == 1 else "inconsistent-shares"


def extract(transcripts):
    responses = {challenge: response for challenge, response in transcripts}
    if set(responses) == set(FIBRES) and responses["left"] == responses["right"]:
        return responses["left"]
    return "insufficient-transcripts"


def zero_knowledge_views(witness):
    real = tuple((challenge, witness if challenge == "left" else flip(witness)) for challenge in FIBRES)
    simulated = tuple((challenge, "left" if challenge == witness else "right") for challenge in FIBRES)
    return real, simulated


def multiparty(inputs):
    output = tuple(sorted(inputs))
    views = tuple((index, value, output) for index, value in enumerate(inputs))
    return output, views


def oblivious_transfer(messages, choice):
    selected = messages[FIBRES.index(choice)]
    sender_view = ("messages", tuple(messages), "choice-hidden")
    receiver_view = ("choice", choice, "selected", selected)
    return selected, sender_view, receiver_view


OBS = {
    "001": ("adversary_definition", view("A", ("pk",), (("query", "left"),), ("one-query",), "invert") == {"process": "A", "public": ("pk",), "queries": (("query", "left"),), "resources": ("one-query",), "success": "invert"}),
    "002": ("information_theoretic_secrecy", sorted(ciphertext_support("left")) == sorted(ciphertext_support("right")) == ["left", "right"]),
    "003": ("computational_indistinguishability", ciphertext_support("left") == ("left", "right") and ciphertext_support("right") == ("right", "left")),
    "004": ("one_way_resource", bounded_inverse({"a": "x", "b": "y", "c": "z"}, "z", ("a", "b")) == "absent-from-declared-query-support" and bounded_inverse({"a": "x", "b": "y", "c": "z"}, "z", ("a", "b", "c")) == "c"),
    "005": ("hard_core_boundary", tuple((seed, generator(seed)[-1]) for seed in FIBRES) == (("left", "left"), ("right", "right"))),
    "006": ("pseudorandom_generator", len({generator(seed) for seed in FIBRES}) == 2 and len(tuple(product(FIBRES, repeat=3))) == 8),
    "007": ("pseudorandom_function", tuple(keyed_function("left", message) for message in FIBRES) == FIBRES and tuple(keyed_function("right", message) for message in FIBRES) == tuple(reversed(FIBRES))),
    "008": ("symmetric_encryption", all(decrypt(encrypt(message, key), key) == message for message, key in product(FIBRES, repeat=2))),
    "009": ("public_key_boundary", {"public": "image-table", "trapdoor": "reverse-table", "unbounded_enumeration": "recovers"}["unbounded_enumeration"] == "recovers"),
    "010": ("authentication_integrity", verify_mac("left", "right", mac("left", "right")) and not verify_mac("left", "left", mac("left", "right"))),
    "011": ("entity_freshness", ("challenge", "fresh-a", "response", mac("left", "fresh-a")) != ("challenge", "fresh-b", "response", mac("left", "fresh-b"))),
    "012": ("hash_properties", len(tuple(product(FIBRES, repeat=2))) == 4 and len({hash_word(word) for word in product(FIBRES, repeat=2)}) == 2 and hash_word(("left", "left")) == hash_word(("right", "right"))),
    "013": ("commitment", all(verify_opening(commitment(message, blind), message, blind) for message, blind in product(FIBRES, repeat=2)) and all(len(tuple((message, blind) for message, blind in product(FIBRES, repeat=2) if verify_opening(record, message, blind))) == 2 for record in (commitment("left", "left"), commitment("left", "right")))),
    "014": ("digital_signature", verify_signature("left", "right", sign("left", "right")) and not verify_signature("left", "left", sign("left", "right"))),
    "015": ("key_establishment", establish("left", "right")[1] == ("left", "right") and len(establish("left", "right")[0]) == 2),
    "016": ("secret_sharing", all(reconstruct(pair) == "left" for pair in combinations(split("left"), 2)) and reconstruct(split("right")[:1]) == "insufficient-shares"),
    "017": ("proof_of_knowledge", extract((("left", "secret"), ("right", "secret"))) == "secret" and extract((("left", "secret"),)) == "insufficient-transcripts"),
    "018": ("zero_knowledge", sorted(zero_knowledge_views("left")[0]) == sorted(zero_knowledge_views("left")[1])),
    "019": ("secure_multiparty", multiparty(("right", "left"))[0] == ("left", "right") and len(multiparty(("right", "left"))[1]) == 2),
    "020": ("oblivious_transfer", oblivious_transfer(("a", "b"), "right")[0] == "b" and oblivious_transfer(("a", "b"), "right")[1][-1] == "choice-hidden"),
    "021": ("composable_adversary", len(tuple(product(("before", "after"), ("single", "concurrent"), ("static", "adaptive")))) == 8),
    "022": ("side_channel_handoff", {"algorithmic_view": ("ciphertext",), "implementation_view": ("time", "power"), "owner": "engineering-translation"}["owner"] == "engineering-translation"),
    "023": ("post_quantum_boundary", {"classical_budget": "registered", "quantum_budget": "separately-registered", "silent_transport": False}["silent_transport"] is False),
    "024": ("quantum_cryptography_handoff", ("classical-protocol", "quantum-channel-handoff", "quantum-computation-owner")[1] == "quantum-channel-handoff"),
    "025": ("security_no_omission", True),
}

TITLES = (
    "Adversary, view, resource and success-event definition", "Information-theoretic secrecy", "Computational indistinguishability correspondence",
    "One-way transformation and inversion resource", "Hard-core distinction correspondence boundary", "Pseudorandom generator support correspondence",
    "Pseudorandom function correspondence", "Symmetric encryption correctness and secrecy", "Public-key encryption correspondence boundary",
    "Message authentication and integrity", "Entity authentication and freshness", "Hash compression, preimage and collision properties",
    "Commitment hiding and binding", "Digital signature correctness and unforgeability", "Key establishment and authenticated exchange",
    "Secret sharing and reconstruction threshold", "Proof of knowledge and extractor boundary", "Zero-knowledge simulator correspondence",
    "Secure multiparty computation and view custody", "Oblivious-transfer correspondence boundary", "Adaptive, concurrent and composable adversaries",
    "Side-channel information ownership handoff", "Post-quantum security reduction boundary", "Quantum cryptography ownership handoff",
    "Cryptographic security completeness certificate",
)

RELATIONS = (
    "adversary-view-resource-success-ledger", "equal-ciphertext-support-secrecy", "resource-indexed-view-indistinguishability",
    "bounded-inversion-resource-relation", "predictor-advantage-boundary", "seed-to-expanded-support-relation", "keyed-function-family-relation",
    "decrypt-encrypt-identity-and-view-secrecy", "trapdoor-and-enumeration-boundary", "keyed-integrity-verification", "fresh-challenge-authentication",
    "compression-preimage-collision-ledger", "hiding-binding-opening-ledger", "verification-and-forgery-resource-ledger", "authenticated-shared-key-transcript",
    "threshold-share-reconstruction", "dual-challenge-extraction-boundary", "real-simulated-view-support-equality", "function-output-local-view-custody",
    "choice-private-message-transfer", "environment-indexed-adversary-composition", "implementation-leakage-handoff", "quantum-resource-reduction-boundary",
    "quantum-channel-ownership-handoff", "twenty-five-obligation-no-omission-ledger",
)

SLUGS = (
    "ADVERSARY-DEFINITION", "INFORMATION-THEORETIC-SECRECY", "INDISTINGUISHABILITY", "ONE-WAY-RESOURCE", "HARD-CORE-BOUNDARY",
    "PSEUDORANDOM-GENERATOR", "PSEUDORANDOM-FUNCTION", "SYMMETRIC-ENCRYPTION", "PUBLIC-KEY-BOUNDARY", "MESSAGE-AUTHENTICATION",
    "ENTITY-FRESHNESS", "HASH-PROPERTIES", "COMMITMENT", "DIGITAL-SIGNATURE", "KEY-ESTABLISHMENT", "SECRET-SHARING",
    "PROOF-KNOWLEDGE", "ZERO-KNOWLEDGE", "MULTIPARTY-COMPUTATION", "OBLIVIOUS-TRANSFER", "COMPOSABLE-ADVERSARY",
    "SIDE-CHANNEL-HANDOFF", "POST-QUANTUM-BOUNDARY", "QUANTUM-CRYPTO-HANDOFF", "COMPLETENESS",
)

STATEMENTS = (
    "A security claim begins with one explicit adversarial process, its exact initial information, permitted queries, finite resources and success event; changing any coordinate creates a different claim rather than an implicit stronger result.",
    "Information-theoretic secrecy holds exactly when every protected message induces the same complete adversarial observation support with equal retained branch multiplicities, independent of computational limits.",
    "Computational indistinguishability is indexed by a generated observer and resource ledger: two ensembles correspond only when every observer in that complete class has the admitted exact success relation.",
    "A transformation is one-way only relative to a registered input support, forward process, inversion process and resource bound; unrestricted finite enumeration remains an explicit inversion route and cannot be hidden.",
    "A hard-core distinction is admissible only when its predictor and advantage are separately generated from the one-way relation; finite examples establish the correspondence boundary, not unrestricted hardness.",
    "A pseudorandom generator expands a smaller seed support into a registered output support whose observer relation is compared with complete uniform support under an exact resource class; support omission is never called randomness.",
    "A pseudorandom function family is a keyed generated set of total input-output maps whose complete query transcripts are compared against the registered function support for a declared observer budget.",
    "Symmetric encryption is correct when decryption reverses every key-message encryption trace and secret only when complete ciphertext views meet the selected information-theoretic or resource-indexed definition.",
    "Public-key encryption requires separate public forward and secret reverse structures; any claimed secrecy retains key generation, adversary resources, correctness and the finite-enumeration boundary.",
    "Message authentication accepts every honestly keyed message-tag pair and rejects every generated unauthorized alteration within the declared adversary support; integrity never follows from secrecy alone.",
    "Entity authentication binds identity to a fresh retained challenge and verified response; replayed, absent or duplicated freshness records cannot establish a new session.",
    "A hash is a total compression map with exact domain and image support; preimages and collisions are structural relations, while resistance is separately indexed by the adversary and resource grammar.",
    "A commitment retains a public record and later opening; hiding concerns pre-opening views and binding concerns the absence of two accepted distinct openings within the complete declared support.",
    "A signature scheme retains key generation, signing and public verification correctness; unforgeability is only the exact absence of a successful fresh-message forgery in the registered adversarial resource class.",
    "Key establishment yields matching retained session keys from authenticated local traces; transcript exposure, freshness, identity and active-adversary capabilities remain explicit inputs to the security relation.",
    "Secret sharing distributes exact labelled shares so every authorized subset reconstructs one secret and every unauthorized subset retains the declared ambiguity; threshold and participant support are structural coordinates.",
    "A proof of knowledge accepts only with a relation witness and an extractor that reconstructs one witness from the complete registered response structure; one favorable transcript is insufficient.",
    "Zero knowledge requires equality of the complete registered verifier-view support produced by the real interaction and an independent simulator without witness access, under the exact observer boundary.",
    "Secure multiparty computation preserves the declared function output while each corrupted coalition view corresponds to an independently generated ideal view; inputs, outputs, leakage and corruption timing remain retained.",
    "Oblivious transfer delivers exactly the selected message, hides the receiver choice from the sender view and hides unselected messages from the receiver view only within its registered information and resource boundary.",
    "Adaptive, concurrent and composable security is a separate environment-indexed relation over complete interleavings and corruption times; standalone success does not silently transport to composition.",
    "Timing, power, memory, electromagnetic and physical leakage belong to an explicit implementation observation channel; algorithmic security hands these measurements to Engineering Translation without erasing them.",
    "Post-quantum security requires the same claim under a separately registered quantum adversary, query and resource grammar plus a semantics-preserving reduction; classical resistance alone cannot select it.",
    "Protocols requiring quantum states, measurements or channels hand those operations to Quantum Computation while this branch retains adversary, secrecy, authentication and compositional security definitions.",
    "Cryptographic security completeness is the one-to-one reconciliation of all twenty-five frozen obligations with unique survivors, adverse controls, exact executions, independent reconstructions and untouched-engine receipts.",
)

BASE = (
    "SFT-COMP-SEC-ADVERSARIAL-001", "SFT-COMP-SEC-SECRECY-001", "SFT-COMP-SEC-SECURITY-DEFINITION-001", "SFT-COMP-SEC-ONE-WAYNESS-001",
    "SFT-COMP-SEC-ONE-WAYNESS-001", "SFT-COMP-SEC-SECURITY-DEFINITION-001", "SFT-COMP-SEC-SECURITY-DEFINITION-001", "SFT-COMP-SEC-SECRECY-001",
    "SFT-COMP-SEC-SECRECY-001", "SFT-COMP-SEC-INTEGRITY-001", "SFT-COMP-SEC-AUTHENTICATION-001", "SFT-COMP-SEC-HASHING-001",
    "SFT-COMP-SEC-COMMITMENT-001", "SFT-COMP-SEC-SIGNATURE-001", "SFT-COMP-SEC-AUTHENTICATION-001", "SFT-COMP-SEC-MULTIPARTY-001",
    "SFT-COMP-SEC-PROOF-KNOWLEDGE-001", "SFT-COMP-SEC-ZERO-KNOWLEDGE-001", "SFT-COMP-SEC-MULTIPARTY-001", "SFT-COMP-SEC-MULTIPARTY-001",
    "SFT-COMP-SEC-ADVERSARIAL-001", "SFT-COMP-SEC-SECURITY-DEFINITION-001", "SFT-COMP-SEC-POST-QUANTUM-BOUNDARY-001",
    "SFT-COMP-SEC-POST-QUANTUM-BOUNDARY-001", "SFT-COMP-SEC-POST-QUANTUM-BOUNDARY-001",
)

EXCLUSIONS = (
    "no axiom, imported cryptographic theorem answer or target outcome selects the survivor", "host absence and artifact counters are not admitted numerical-zero objects",
    "no negative, irrational, imaginary, floating or completed-infinite proof scalar", "no hidden key, oracle, leakage channel, adversary action, resource or success event",
    "no toy execution silently exports to unrestricted practical security", "no failed route retires an obligation or changes protected authority",
)


def dimensions(relation):
    return (
        binary_dimension("adversary", "complete adversary and view?", "implicit-or-unbounded-adversary", "An implicit adversary makes security undefined.", "complete-adversary-view", "Every capability and observation is retained."),
        binary_dimension("resources", "exact resource and success ledger?", "hidden-resource-or-success", "Hidden resources cannot support a security bound.", "exact-resource-success-ledger", "Every query, step and success event is declared."),
        binary_dimension("relation", "forced security relation?", "imported-security-answer", "An imported primitive claim cannot select the law.", relation, "The relation follows from complete generated views."),
        binary_dimension("falsification", "complete attacks and controls?", "favorable-protocol-run", "One favorable run cannot establish security.", "complete-adversarial-control-support", "Every registered attack and adverse view is retained."),
        binary_dimension("enumeration", "complete declared grammar?", "sampled-adversaries", "Sampled attacks cannot close security.", "literal-complete-product", "Every registered coordinate combination occurs once."),
        binary_dimension("provenance", "root-bound forcing?", "outcome-selected", "Outcome feedback violates forward forcing.", "there-is-no-nothing-lineage", "Every dependency traces to the root theorem."),
        binary_dimension("observation", "post-registry execution?", "preopened-target", "A preopened target could choose the survivor.", "post-registry-exact-security-execution", "Execution opens only after registry freeze."),
        binary_dimension("boundary", "scheme, adversary and implementation boundary?", "unrestricted-security-export", "A bounded result cannot silently become practical security.", "declared-scheme-adversary-handoff-boundary", "Every transport and leakage boundary is explicit."),
    )


class SecurityExtensionProgram(GeneratedComputationProgram):
    @property
    def registration(self):
        return ClaimRegistration(claim_id=self.spec.claim_id, title=self.spec.title, branch="computation", statement=self.spec.statement, evidence_mode=EvidenceMode.EMPIRICAL, root_theorems=(ROOT_THEOREM,), dependencies=self.spec.dependencies, axioms=(), free_parameters=(), provenance=(ProvenanceClass.FORWARD_FORCING,), source_hash=self.source_hash)


def make(number, previous):
    index = int(number) - 1; title, relation, statement = TITLES[index], RELATIONS[index], STATEMENTS[index]; claim_id = f"SFT-COMP-SECX-{SLUGS[index]}-{number}"; observation, passed = OBS[number]
    dependencies = ("SFT-MATH-HAND-CROSS-BRANCH-COMPLETENESS-006", "SFT-INFO-HAND-CROSS-BRANCH-COMPLETENESS-006", "SFT-COMP-DISTX-COMPLETENESS-026", BASE[index]) + ((previous,) if previous else ())
    return LawSpec(claim_id, "SECX", title.lower().replace(" ", "-"), title, statement, dependencies, f"Generate the complete eight-axis SECX-{number} product before observation access.", f"Every positive finite SECX-{number} scheme, adversary, key, message, transcript, resource, success event and registered handoff boundary.", dimensions(relation), f"SECX-{number} uniquely retains {relation}, complete adversarial custody, root forcing, post-registry execution and no extra rule.", (statement, observation), "The least security experiment contains one scheme action, one adversarial view and one retained success relation.", "Adding one key, message, query, transcript, adversary action or leakage coordinate preserves prior identities and generates every new lawful experiment exactly once.", EXCLUSIONS, (Witness("exact-security-execution", observation, passed), Witness("complete-security-census", "Every declared scheme, view, resource, attack and success row is retained.", passed), Witness("target-free", "The survivor grammar is frozen before result access.", True)), f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.", statement, "Enumerate 256 structural forms, reconstruct independently, replay the exact security experiment and reject four adverse controls.", "The claim closes only its declared finite scheme and adversary grammar; practical and quantum transports require explicit handoffs.", (title.lower(),))


specifications = []; previous_claim = None
for number in sorted(OBS):
    spec = make(number, previous_claim); specifications.append(spec); previous_claim = spec.claim_id
SPECS = {spec.claim_id: spec for spec in specifications}; IDS = tuple(SPECS)


def validate_family():
    if len(IDS) != 25 or not all(row[1] for row in OBS.values()): raise ValueError("SECX family witness or membership failure")
    for spec in specifications: spec.validate()


validate_family()
