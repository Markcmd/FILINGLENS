"""Parse raw 10-K HTML into canonical text + a section map.

The *canonical text* is the single normalized string all citation offsets
point into, for the lifetime of the project. Sections are (item, title,
char_start, char_end) spans over it.

The tricky part is the table of contents: it lists the same "Item 1A. Risk
Factors" headings as the real sections. We keep only the LAST occurrence of
each item heading — ToC entries always precede their sections.

Run: python -m filinglens.parse
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass

import warnings

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

from filinglens.config import PARSED_DIR, RAW_DIR

# 10-K HTML files open with an XML declaration (inline XBRL); we knowingly
# parse them as HTML, so suppress bs4's warning about it.
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# Standard 10-K item titles, used when the heading line itself has no title.
ITEM_TITLES = {
    "1": "Business",
    "1A": "Risk Factors",
    "1B": "Unresolved Staff Comments",
    "1C": "Cybersecurity",
    "2": "Properties",
    "3": "Legal Proceedings",
    "4": "Mine Safety Disclosures",
    "5": "Market for Registrant's Common Equity",
    "6": "Reserved",
    "7": "Management's Discussion and Analysis",
    "7A": "Quantitative and Qualitative Disclosures About Market Risk",
    "8": "Financial Statements and Supplementary Data",
    "9": "Changes in and Disagreements with Accountants",
    "9A": "Controls and Procedures",
    "9B": "Other Information",
    "9C": "Disclosure Regarding Foreign Jurisdictions",
    "10": "Directors, Executive Officers and Corporate Governance",
    "11": "Executive Compensation",
    "12": "Security Ownership",
    "13": "Certain Relationships and Related Transactions",
    "14": "Principal Accountant Fees and Services",
    "15": "Exhibits, Financial Statement Schedules",
    "16": "Form 10-K Summary",
}

# A heading is "Item <code>" at the start of a line, followed by . : or a dash.
# Cross-references ("see Item 1A") don't start lines, so they don't match.
ITEM_HEADING_RE = re.compile(
    r"(?im)^[ \t]{0,8}item[ \t]+(\d{1,2}[A-C]?)[ \t]*[.:–—-][ \t]*(.*)$"
)

# Canonical 10-K item order, used to keep detected headings monotonic.
ITEM_ORDER = list(ITEM_TITLES)


@dataclass(frozen=True)
class Section:
    item: str  # e.g. "1A"; "FULL" for the whole-document fallback
    title: str
    char_start: int
    char_end: int


def html_to_text(html: str) -> str:
    """Extract visible text from filing HTML, deterministically normalized."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text("\n")
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)  # collapse runs of spaces/tabs
    text = re.sub(r" ?\n ?", "\n", text)  # strip spaces around newlines
    text = re.sub(r"\n{3,}", "\n\n", text)  # max one blank line
    return text.strip()


def find_sections(text: str) -> list[Section]:
    """Locate 10-K item sections in canonical text.

    Strategy: collect all heading candidates, keep the last occurrence of
    each item code (drops ToC entries), enforce canonical item order, and
    let each section run until the next one starts.
    """
    last_seen: dict[str, tuple[int, str]] = {}
    for m in ITEM_HEADING_RE.finditer(text):
        code = m.group(1).upper()
        if code not in ITEM_TITLES:
            continue
        title = m.group(2).strip() or ITEM_TITLES[code]
        last_seen[code] = (m.start(), title)

    if len(last_seen) < 3:  # detection failed; never lose data
        return [Section("FULL", "Full document", 0, len(text))]

    # Sort by position, then drop any heading that breaks canonical item
    # order (e.g. a stray late cross-reference that begins a line).
    by_pos = sorted(
        (pos, code, title) for code, (pos, title) in last_seen.items()
    )
    ordered: list[tuple[int, str, str]] = []
    for pos, code, title in by_pos:
        if ordered and ITEM_ORDER.index(code) <= ITEM_ORDER.index(ordered[-1][1]):
            continue
        ordered.append((pos, code, title))

    sections = []
    for i, (pos, code, title) in enumerate(ordered):
        end = ordered[i + 1][0] if i + 1 < len(ordered) else len(text)
        sections.append(Section(code, title[:120], pos, end))
    return sections


def parse_filing(html: str) -> tuple[str, list[Section]]:
    text = html_to_text(html)
    return text, find_sections(text)


def parse_all() -> list[dict]:
    """Parse every downloaded filing; write data/parsed/{ticker}/{fy}.json."""
    results = []
    for html_path in sorted(RAW_DIR.glob("*/*_10-K.htm")):
        meta = json.loads(html_path.with_suffix("").with_suffix(".meta.json").read_text())
        text, sections = parse_filing(html_path.read_text(errors="ignore"))
        out = {
            "ticker": meta["ticker"],
            "fiscal_year": meta["report_date"][:4],
            "source_url": meta["url"],
            "text": text,
            "sections": [asdict(s) for s in sections],
        }
        out_path = PARSED_DIR / meta["ticker"] / f"{out['fiscal_year']}.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(out))
        results.append(out)
        print(
            f"{out['ticker']} FY{out['fiscal_year']}: "
            f"{len(text):,} chars, {len(sections)} sections"
        )
    return results


if __name__ == "__main__":
    parse_all()
