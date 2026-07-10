"""Unit tests for parsing + chunking against a handcrafted mini 10-K."""

from filinglens.chunk import MAX_WORDS, chunk_filing, chunk_section
from filinglens.parse import find_sections, html_to_text, parse_filing

# Mini 10-K: a table of contents (the classic false-positive source) followed
# by real sections. Paragraphs are long enough to survive MIN_WORDS.
PARA = "The company designs products and sells them worldwide through many channels. " * 8
RISK = "Competition in our markets is intense and could harm future results badly. " * 8
MDNA = "Revenue increased compared to the prior fiscal year due to product demand. " * 8

FAKE_10K = f"""
<html><head><style>p {{color: black}}</style>
<script>var tracking = 1;</script></head><body>
<h1>FORM 10-K</h1>
<p>TABLE OF CONTENTS</p>
<p>Item 1. Business</p>
<p>Item 1A. Risk Factors</p>
<p>Item 7. Management&#8217;s Discussion and Analysis</p>
<p>PART I</p>
<p>Item 1. Business</p>
<p>{PARA}</p>
<p>{PARA}</p>
<p>Item 1A. Risk Factors</p>
<p>{RISK}</p>
<p>See Item 7 for more discussion of results.</p>
<p>{RISK}</p>
<p>Item 7. Management&#8217;s Discussion and Analysis</p>
<p>{MDNA}</p>
</body></html>
"""


def _parsed():
    text, sections = parse_filing(FAKE_10K)
    return {
        "ticker": "TEST",
        "fiscal_year": "2025",
        "source_url": "https://example.com/f.htm",
        "text": text,
        "sections": [
            {"item": s.item, "title": s.title, "char_start": s.char_start, "char_end": s.char_end}
            for s in sections
        ],
    }


def test_html_to_text_strips_script_and_style():
    text = html_to_text(FAKE_10K)
    assert "tracking" not in text and "color" not in text
    assert "FORM 10-K" in text


def test_finds_real_sections_not_toc():
    text, sections = parse_filing(FAKE_10K)
    assert [s.item for s in sections] == ["1", "1A", "7"]
    # Real Item 1 section must contain body text; the ToC entry has none.
    item1 = next(s for s in sections if s.item == "1")
    assert "designs products" in text[item1.char_start : item1.char_end]
    # ToC lines appear BEFORE the first detected section
    assert text[: item1.char_start].count("Item 1.") >= 1


def test_cross_reference_does_not_split_sections():
    # "See Item 7 for more..." sits mid-section and must not become a heading;
    # Item 1A must run until the real Item 7 heading.
    text, sections = parse_filing(FAKE_10K)
    item1a = next(s for s in sections if s.item == "1A")
    assert "See Item 7" in text[item1a.char_start : item1a.char_end]


def test_section_fallback_on_garbage():
    text, sections = parse_filing("<html><body><p>hello world</p></body></html>")
    assert len(sections) == 1
    assert sections[0].item == "FULL"
    assert (sections[0].char_start, sections[0].char_end) == (0, len(text))


def test_chunks_round_trip_and_respect_sections():
    parsed = _parsed()
    chunks = chunk_filing(parsed)
    assert chunks, "expected at least one chunk"
    sections = {s["item"]: s for s in parsed["sections"]}
    for c in chunks:
        # Citation guarantee: offsets reproduce the chunk text exactly
        assert parsed["text"][c.char_start : c.char_end] == c.text
        # Never cross a section boundary
        s = sections[c.item]
        assert s["char_start"] <= c.char_start and c.char_end <= s["char_end"]


def test_chunk_ids_unique_and_descriptive():
    chunks = chunk_filing(_parsed())
    ids = [c.id for c in chunks]
    assert len(ids) == len(set(ids))
    assert ids[0].startswith("TEST_2025_item1_")


def test_long_section_is_split_with_overlap():
    long_para = "word " * 80
    text = "\n\n".join(f"paragraph {i} " + long_para for i in range(12))
    section = {"item": "7", "title": "MD&A", "char_start": 0, "char_end": len(text)}
    chunks = chunk_section(text, section, "TEST", "2025", "http://x")
    assert len(chunks) > 1
    for c in chunks:
        assert len(c.text.split()) <= MAX_WORDS + 90  # budget + overlap paragraph
    # Consecutive chunks share the overlap paragraph
    for a, b in zip(chunks, chunks[1:]):
        assert b.char_start < a.char_end


def test_oversized_single_paragraph_is_hard_split():
    text = "word " * (MAX_WORDS * 3)
    section = {"item": "1", "title": "Business", "char_start": 0, "char_end": len(text)}
    chunks = chunk_section(text.strip(), section, "TEST", "2025", "http://x")
    assert all(len(c.text.split()) <= MAX_WORDS for c in chunks)
