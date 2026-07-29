#!/usr/bin/env python3
"""Retry target selection with mechanism-specific identity-only queries."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import tools.capture_medicine_placebo_sources_v1 as capture

capture.OUT = capture.ROOT / "evidence/external/medicine/placebo_nocebo_2026-07-28_retry_1"
capture.EXCLUDED = set(capture.EXCLUDED) | {"41966073", "42296699", "42308284"}
capture.QUERIES = (
    ("objective-placebo", '"placebo effect"[Title] AND (opioid OR dopamine OR cytokine OR fMRI OR PET OR biomarker)'),
    ("objective-nocebo", '"nocebo effect"[Title] AND (cortisol OR fMRI OR physiological OR neuroendocrine OR biomarker)'),
    ("bounded-context", '("placebo effect"[Title] OR "nocebo effect"[Title]) AND randomized[Title/Abstract] AND (expectation OR expectancy)'),
)

if __name__ == "__main__":
    capture.main()
