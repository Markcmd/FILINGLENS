"""Pure-logic tests for prompt building and citation parsing (no DB, no LLM)."""

from filinglens.answer import NOT_FOUND, build_prompt, cited_markers, format_excerpt
from filinglens.retrieve import Hit, build_where


def make_hit(i=0, ticker="AAPL", text="Revenue grew due to iPhone demand."):
    return Hit(
        id=f"{ticker}_2025_item7_{i:03d}",
        text=text,
        ticker=ticker,
        fiscal_year="2025",
        item="7",
        item_title="Management's Discussion and Analysis",
        char_start=100,
        char_end=100 + len(text),
        source_url="https://example.com/f.htm",
        score=0.9,
    )


def test_prompt_contains_grounding_rules_and_excerpts():
    hits = [make_hit(0), make_hit(1, text="Services revenue also increased.")]
    prompt = build_prompt("Why did revenue grow?", hits)
    assert "ONLY the numbered excerpts" in prompt
    assert NOT_FOUND in prompt  # the refusal instruction
    assert "[1] AAPL FY2025 10-K, Item 7" in prompt
    assert "Services revenue also increased." in prompt
    assert prompt.rstrip().endswith("Answer:")


def test_excerpt_header_identifies_the_filing():
    line = format_excerpt(3, make_hit()).splitlines()[0]
    assert line == "[3] AAPL FY2025 10-K, Item 7 (Management's Discussion and Analysis):"


def test_cited_markers_dedupe_and_ignore_out_of_range():
    text = "Revenue grew [1], driven by demand [2] [1]. Ignore [9] and [0]."
    assert cited_markers(text, n_hits=3) == [1, 2]


def test_cited_markers_empty_when_no_citations():
    assert cited_markers("No citations here.", n_hits=5) == []


def test_build_where_variants():
    assert build_where() is None
    assert build_where(ticker="aapl") == {"ticker": "AAPL"}
    assert build_where(year=2025) == {"fiscal_year": "2025"}
    assert build_where(ticker="MSFT", year="2024") == {
        "$and": [{"ticker": "MSFT"}, {"fiscal_year": "2024"}]
    }
