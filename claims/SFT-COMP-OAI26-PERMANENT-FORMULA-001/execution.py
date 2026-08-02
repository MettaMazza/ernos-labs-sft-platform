from pathlib import Path
from sft.openai_2026.execution_v1 import build_execution as assemble


def build_execution(root: Path):
    return assemble(root, "SFT-COMP-OAI26-PERMANENT-FORMULA-001", Path(__file__).resolve())
