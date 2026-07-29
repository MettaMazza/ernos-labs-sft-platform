#!/usr/bin/env python3
"""Third identity-first source batch for completed objective experiments."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
import tools.capture_medicine_placebo_sources_v1 as capture

capture.OUT = capture.ROOT / "evidence/external/medicine/placebo_nocebo_2026-07-28_retry_2"
capture.EXCLUDED = set(capture.EXCLUDED) | {"41966073", "42296699", "42308284", "42056755", "41663169", "42320075"}
capture.QUERIES = (
    ("objective-placebo-positive", '("placebo-induced"[Title/Abstract] OR "placebo analgesia"[Title]) AND (opioid OR dopamine OR cytokine OR PET OR fMRI) AND humans[MeSH Terms]'),
    ("objective-nocebo-completed", '("nocebo hyperalgesia"[Title/Abstract] OR "nocebo response"[Title/Abstract]) AND (cortisol OR ACTH OR fMRI OR EEG OR physiological) AND humans[MeSH Terms] NOT protocol[Title]'),
    ("objective-context-control", '"placebo effect"[Title] AND (objective OR biomarker OR imaging) AND humans[MeSH Terms] NOT review[Publication Type]'),
)

if __name__ == "__main__": capture.main()
