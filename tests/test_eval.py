"""Tests for eval scoring logic (pure — no DB, no model, no LLM)."""

from filinglens.eval import (
    GOLDEN_PATH,
    hit_matches,
    load_golden,
    match_rank,
    summarize,
)
from test_answer import make_hit

EXPECTED = {"ticker": "AAPL", "items": ["1A", "7"], "must_contain": "final assembly"}


def test_hit_matches_requires_all_three_conditions():
    good = make_hit(text="partners for final assembly of products")
    assert hit_matches(good, EXPECTED)  # item 7, AAPL, phrase present
    assert not hit_matches(make_hit(ticker="MSFT", text="final assembly"), EXPECTED)
    assert not hit_matches(make_hit(text="no phrase here"), EXPECTED)
    wrong_item = {**EXPECTED, "items": ["2"]}
    assert not hit_matches(good, wrong_item)


def test_match_rank_is_first_match_one_based():
    hits = [
        make_hit(0, text="irrelevant"),
        make_hit(1, text="final assembly happens in Asia"),
        make_hit(2, text="final assembly also here"),
    ]
    assert match_rank(hits, EXPECTED) == 2
    assert match_rank([make_hit(text="nope")], EXPECTED) is None


def test_summarize_hit_rate_and_mrr():
    s = summarize([1, 2, None, 4])
    assert s["n"] == 4
    assert s["hit_rate"] == 0.75
    assert abs(s["mrr"] - (1 + 0.5 + 0 + 0.25) / 4) < 1e-9


def test_golden_file_is_valid():
    golden = load_golden(GOLDEN_PATH)
    assert len(golden) >= 15
    ids = [g["id"] for g in golden]
    assert len(ids) == len(set(ids))
    for g in golden:
        assert g["question"].strip().endswith("?")
        e = g["expected"]
        assert e["ticker"] in {"AAPL", "MSFT", "NVDA"}
        assert e["items"] and e["must_contain"]
