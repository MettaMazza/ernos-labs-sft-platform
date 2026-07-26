#!/usr/bin/env python3
"""Build Methods Paper 00 version 0.2 without rewriting its published v0.1 record."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "publications/superseded/THERE_IS_NO_NOTHING_METHODS_PAPER_001.md"
OUTPUT = ROOT / "publications/successors/methods/THERE_IS_NO_NOTHING_METHODS_PAPER_001_V0_2.md"


RESULTS_FIRST = """## Results first: the method, its first proofs and the branch series it enabled

| Headline result | Exact result | Meaning |
|---|---|---|
| Premise-free operational root | A purported counterexample either presents nothing and supplies no counterexample, or presents an occurrence and is not nothing. | The two-class operational census closes without an axiom, free parameter or imported ontology. |
| Structural One | Of six complete coverage/addition forms, exactly one retains the admitted occurrence completely without omission or unforced addition. | One is a forced structural self-whole, not a conventional numeral assumed in advance. |
| Public fail-closed admission method | Registration, complete candidate generation, one decision per candidate, exactly one survivor, closure, adverse controls, independent reconstruction, sealing and—where nature is claimed—post-seal target custody are all mandatory. | A claim cannot enter through reputation, consensus, a successful example, a terminal oracle score or an edited favorable result. |
| Open scientific authority | Criticism is unrestricted; admission requires the public evidence chain and unchanged-engine receipt. Copyright preserves Maria Smith's authorship while CC BY 4.0 and Apache-2.0 preserve open inspection and reuse. | Ernos Labs is an open-source science movement and a separate revocable standards designation, not a proprietary gate on knowledge. |
| Current paper series | The inaugural two results now have a completed Foundation successor, followed by Mathematics, Information Science, Classical Computation, Quantum Computation, Chemistry and Materials papers; the expanded Physics manuscript is the next unreleased paper. | This methods update reports the platform's growth without retroactively importing later answers into the two founding proofs. Each branch remains independently versioned, falsifiable and open to lawful extension. |

"""


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"expected one methods-paper replacement, found {text.count(old)}: {old[:80]!r}")
    return text.replace(old, new, 1)


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "**Methods and Foundation Paper 001 · Third clean-room reconstruction**",
        "**Methods Paper 00 · Third clean-room reconstruction · successor version 0.2.0**",
    )
    text = replace_once(
        text,
        "**DOI:** [10.5281/zenodo.21514890](https://doi.org/10.5281/zenodo.21514890) ·\n**Version:** 0.1.0 · **Published:** 23 July 2026",
        "**DOI:** [10.5281/zenodo.21591160](https://doi.org/10.5281/zenodo.21591160) ·\n**Version:** 0.2.0 · **Published:** 26 July 2026",
    )
    old_status = """> **Exact release status.** This is the inaugural platform and methods paper,
> not a declaration that the foundation branch or a Theory of Everything is
> complete. The v3 census currently contains two admitted formal results: the
> premise-free operational root theorem and the structural One. Every later
> mathematical, computational and natural-science result remains unadmitted
> until it passes the same public engine. The foundation branch will receive
> its comprehensive branch paper only when its frozen inventory is complete.
"""
    new_status = """> **Exact release status.** Version 0.2 preserves the inaugural platform and
> methods paper and reports the publication series it enabled. This paper still
> owns and reproduces exactly two founding results: the premise-free operational
> root theorem and structural One. Later laws are not retroactive premises; they
> are separately admitted and documented in their own versioned branch papers.
> The Foundation, Mathematics, Information Science, Classical Computation,
> Quantum Computation, Chemistry and Materials papers now exist; the expanded
> Physics paper completes the present ordered publication update. Chemistry,
> Materials and every later branch remain outside this release sequence.
"""
    text = replace_once(text, old_status, new_status)
    text = replace_once(
        text,
        "[Inspect the two admitted claims](#results-of-the-third-clean-room-reconstruction) ·",
        "[Inspect the two inaugural claims](#results-of-the-third-clean-room-reconstruction) ·",
    )
    text = replace_once(
        text,
        "This result is structural only: arithmetic, parts and Fold\noperations have not yet been admitted in v3.",
        "This result is structural only. Arithmetic, parts and Fold operations were not premises of the founding run; their later admissions remain separate branch evidence.",
    )
    marker = "**Keywords:** Smithian Fold Theory; open science; computational proof;\npremise-free foundation; exact arithmetic; reproducibility; falsifiability;\nclean-room replication; scientific software; knowledge tree.\n\n"
    text = replace_once(text, marker, marker + RESULTS_FIRST)
    text = replace_once(
        text,
        "That programme is a research objective, not a present result. V3 currently has\ntwo admitted claims. No computational-science, quantum-computing or\nnatural-science branch is complete in this reconstruction. Earlier results may\nbe compared only after the corresponding v3 claim seals; they cannot be copied\nas premises or answer tables.",
        "That programme remains open-ended, but the present versioned record now includes separately admitted Foundation, Mathematics, Information Science, Classical Computation, Quantum Computation, Chemistry and Materials branches and a locally prepared expanded Physics manuscript. This methods paper does not absorb those results: it records the common admission constitution. Earlier SFT observations may define questions and external correspondence only after a V3 claim seals; they cannot be copied as executable premises or answer tables.",
    )
    text = replace_once(
        text,
        "- Two admitted claims do not complete the foundation branch.",
        "- The two claims owned by this methods paper do not replace the separately published Foundation branch.",
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(text, encoding="utf-8")
    print(f"built {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
