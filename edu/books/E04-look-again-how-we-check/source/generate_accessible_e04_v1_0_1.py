#!/usr/bin/env python3
"""Generate E04's semantic, scalable-text student edition for review 1.0.1."""

from __future__ import annotations

import html
import json
from pathlib import Path


BOOK_DIR = Path(__file__).resolve().parents[1]
SOURCE = BOOK_DIR / "source" / "book-v1.0.1.json"
OUTPUT = BOOK_DIR / "accessible" / "student-book-v1.0.1.html"


def paragraphs(value: str) -> str:
    blocks = [block.strip() for block in value.split("\n\n") if block.strip()]
    return "".join(
        f"<p>{'<br>'.join(html.escape(line) for line in block.splitlines())}</p>"
        for block in blocks
    )


def display_choice(choice: str) -> str:
    labels = {
        "does-not-match": "Does Not Match",
        "measure-bottom-to-top": "Measure Bottom to Top",
        "source-comparison": "Picture-Plan Comparison",
        "width-record": "Side-to-Side Ribbon",
        "height-record": "Bottom-to-Top Ribbon",
        "friend-check-record": "Ivo's Own Sign",
    }
    return labels.get(choice, choice.replace("-", " ").title())


def main() -> None:
    book = json.loads(SOURCE.read_text(encoding="utf-8"))
    pages = book["pages"]
    if book.get("version") != "1.0.1":
        raise ValueError("E04 accessible edition requires canonical version 1.0.1")
    if len(pages) != 32 or [page["page"] for page in pages] != list(range(1, 33)):
        raise ValueError("E04 accessible edition requires exactly 32 ordered pages")

    sections: list[str] = []
    for page in pages:
        number = page["page"]
        choices = ""
        if page.get("choices"):
            choice_items = "".join(
                f"<li>{html.escape(display_choice(choice))}</li>"
                for choice in page["choices"]
            )
            choices = (
                '<div class="choices" aria-label="Choices shown on this page">'
                f"<strong>Choices:</strong><ul>{choice_items}</ul></div>"
            )
        labels = ""
        if page.get("labels"):
            labels = (
                '<p class="labels"><strong>Visible labels above the pictures:</strong> '
                + "; ".join(html.escape(label) for label in page["labels"])
                + "</p>"
            )
        code = ""
        if page.get("code"):
            code = (
                '<p class="optional-code"><strong>Optional picture code:</strong> '
                f"{html.escape(page['code'])}. This code is not needed to learn or continue.</p>"
            )
        description = html.escape(page["alt"])
        section = f'''<section class="page {html.escape(page['kind'])}" id="page-{number}" aria-labelledby="page-{number}-title">
  <p class="page-number">Page {number} of 32</p>
  <h2 id="page-{number}-title">{html.escape(page['badge'])}</h2>
  {paragraphs(page['text'])}
  <p class="prompt">{html.escape(page['subtext'])}</p>
  {choices}
  {labels}
  <figure role="img" aria-label="{description}">
    <figcaption><strong>Picture description:</strong> {description}</figcaption>
  </figure>
  {code}
</section>'''
        sections.append("\n".join(line.rstrip() for line in section.splitlines()))

    page_links = " ".join(f'<a href="#page-{number}">{number}</a>' for number in range(1, 33))
    document = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(book['title'])} - accessible review 1.0.1</title>
  <style>
    :root {{ color-scheme: light; font-size: 100%; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0 auto; max-width: 54rem; padding: 1.25rem; color: #20314a; background: #fff9ea; font: 1.16rem/1.7 system-ui, sans-serif; }}
    header, nav, main, footer {{ display: block; }}
    header {{ padding: 1rem 0 1.4rem; border-bottom: .25rem solid #2c765c; }}
    h1, h2 {{ line-height: 1.15; }}
    h1 {{ font-size: clamp(2rem, 7vw, 3.5rem); margin: 0 0 .5rem; }}
    h2 {{ font-size: clamp(1.45rem, 5vw, 2rem); margin: .3rem 0 1rem; }}
    nav {{ padding: 1rem 0; line-height: 2.2; }}
    nav a {{ display: inline-block; min-width: 2.3rem; margin: .15rem; text-align: center; border: .12rem solid #2c765c; border-radius: .5rem; color: #173b34; background: white; }}
    .page {{ padding: 2rem 0; border-bottom: .18rem solid #cdbf98; }}
    .page-number {{ font-weight: 700; color: #596a74; }}
    .prompt {{ padding: .8rem 1rem; border-left: .4rem solid #6d4a91; background: white; }}
    .challenge {{ background: #f5fbfb; }}
    .reveal {{ background: #f3faf3; }}
    figure {{ margin: 1rem 0; padding: 1rem; border: .16rem solid #2c765c; border-radius: .75rem; background: white; }}
    .labels, .optional-code, .choices {{ padding: .75rem 1rem; background: white; }}
    li {{ margin: .25rem 0; }}
    a:focus-visible {{ outline: .25rem solid #6d4a91; outline-offset: .15rem; }}
    @media (prefers-reduced-motion: reduce) {{ *, *::before, *::after {{ scroll-behavior: auto !important; }} }}
    @media print {{ nav {{ display: none; }} .page {{ break-after: page; }} }}
  </style>
</head>
<body>
  <header>
    <p>SFT Open Education - Early Years - live review edition</p>
    <h1>{html.escape(book['title'])}</h1>
    <p>{html.escape(book['subtitle'])} - Version {html.escape(book['version'])}</p>
    <p>This edition includes every page's words, choices, visible labels and picture description. Optional codes never gate learning.</p>
  </header>
  <nav aria-label="Jump to a book page">{page_links}</nav>
  <main>{''.join(sections)}</main>
  <footer>
    <p>Copyright 2026 Maria Smith. CC BY 4.0. Review edition; final-publication approval pending.</p>
  </footer>
</body>
</html>
'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(document, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
