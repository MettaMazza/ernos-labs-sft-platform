from sft.physics.hadron_regge_dimensional_terminal_execution_v1 import build_execution as _build_execution


def build_execution(root):
    return _build_execution(root, root / "claims/SFT-PHYS-HADRON-REGGE-DIMENSIONAL-TERMINAL-059/execution.py")


__all__ = ("build_execution",)
