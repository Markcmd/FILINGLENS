"""Command-line interface.

Examples:
    python -m filinglens.cli "How does Nvidia describe data-center demand?" --ticker NVDA
    python -m filinglens.cli "What are Apple's supply chain risks?" --ticker AAPL --year 2025
    python -m filinglens.cli "segment revenue" --retrieve-only   # debug retrieval, no LLM
"""

from __future__ import annotations

import argparse

from filinglens.answer import OllamaLLM, answer_question
from filinglens.retrieve import retrieve


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="filinglens", description=__doc__)
    p.add_argument("question")
    p.add_argument("--ticker", help="restrict to one company, e.g. AAPL")
    p.add_argument("--year", help="restrict to one fiscal year, e.g. 2025")
    p.add_argument("-k", type=int, default=6, help="number of chunks to retrieve")
    p.add_argument("--model", default="llama3.2", help="Ollama model name")
    p.add_argument(
        "--retrieve-only",
        action="store_true",
        help="show raw retrieval hits with scores; skip the LLM",
    )
    args = p.parse_args(argv)

    if args.retrieve_only:
        hits = retrieve(args.question, k=args.k, ticker=args.ticker, year=args.year)
        for h in hits:
            print(f"{h.score:.3f}  {h.id}  Item {h.item} ({h.item_title})")
            print(f"       {h.text[:160]}...\n")
        return

    result = answer_question(
        args.question,
        k=args.k,
        ticker=args.ticker,
        year=args.year,
        llm=OllamaLLM(model=args.model),
    )
    print(result.text)
    if result.citations:
        print("\nSources:")
        for c in result.citations:
            print(
                f"  [{c.marker}] {c.ticker} FY{c.fiscal_year} 10-K, Item {c.item} "
                f"({c.item_title}), chars {c.char_start}-{c.char_end}"
            )
            print(f"      {c.source_url}")


if __name__ == "__main__":
    main()
