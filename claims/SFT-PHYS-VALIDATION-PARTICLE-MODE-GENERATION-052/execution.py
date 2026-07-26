from sft.physics.particle_mode_generation_empirical_execution_v1 import build_execution as _build_execution


def build_execution(root):
    return _build_execution(root, root / "claims/SFT-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052/execution.py")


__all__ = ("build_execution",)
