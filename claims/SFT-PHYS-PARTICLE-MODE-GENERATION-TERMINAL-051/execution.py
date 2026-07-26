from sft.physics.particle_mode_generation_terminal_execution_v1 import build_execution as _build_execution


def build_execution(root):
    return _build_execution(root, root / "claims/SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051/execution.py")


__all__ = ("build_execution",)
