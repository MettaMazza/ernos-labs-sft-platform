from sft.physics.helium_isotope_closure_terminal_execution_v1 import build_execution as _build_execution


def build_execution(root):
    return _build_execution(root, root / "claims/SFT-PHYS-THERMAL-HELIUM-ISOTOPE-TERMINAL-057/execution.py")


__all__ = ("build_execution",)
