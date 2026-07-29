"""Post-registry exact execution validator for SECX-001 through SECX-025."""
from sft.computation.complete_field_observation_v1 import CompleteFieldObservationValidator

REGISTRY = "census/computation_secx_001_025_target_registry_v1.json"
REGISTRY_HASH = "sha256:32cf86865bb5202a55907017388d04b2df29b0c8fccc49e247d318cdff294756"
VECTOR = "experiments/external_sources/computation/secx_001_025_observation_vector_v1.json"
VECTOR_HASH = "sha256:17ad3067fba9740055331b959b543ad9020b8ff3fbc436780ed115929ff29487"
FALSIFICATION = "Reject if the value-free registry, scheme, adversary, key, message, transcript, resource, success event, leakage or handoff boundary, source identity, survivor, seal, custody record, control or independent reconstruction is missing, changed, duplicated or opened out of order."


def SecurityObservationValidator(root, spec):
    return CompleteFieldObservationValidator(
        root,
        spec,
        "SECX",
        REGISTRY,
        REGISTRY_HASH,
        VECTOR,
        VECTOR_HASH,
        "classical-computation-secx-observer-v1",
        FALSIFICATION,
    )
