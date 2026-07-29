"""Post-registry exact execution validator for SEMX-001 through SEMX-025."""
from sft.computation.complete_field_observation_v1 import CompleteFieldObservationValidator

REGISTRY = "census/computation_semx_001_025_target_registry_v1.json"
REGISTRY_HASH = "sha256:2789cc740da30d1b574c0078c2c5a1bb357fe5d1e453679b9e5f2db55421b06d"
VECTOR = "experiments/external_sources/computation/semx_001_025_observation_vector_v1.json"
VECTOR_HASH = "sha256:02a9de1f8e90146c723623f1e4f64aab9720e59536f49da0a0797b37dd4640fe"
FALSIFICATION = "Reject if the value-free registry, complete syntax, scope ledger, semantic trace, judgment, proof, translation boundary, source identity, survivor, seal, custody record, control or independent reconstruction is missing, changed, duplicated or opened out of order."


def SemanticsObservationValidator(root, spec):
    return CompleteFieldObservationValidator(
        root,
        spec,
        "SEMX",
        REGISTRY,
        REGISTRY_HASH,
        VECTOR,
        VECTOR_HASH,
        "classical-computation-semx-observer-v1",
        FALSIFICATION,
    )
