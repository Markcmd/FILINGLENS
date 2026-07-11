"""Golden Q&A evaluation: measure retrieval (and optionally answer) quality.

A golden question specifies what correct retrieval must contain: expected
ticker, acceptable 10-K items, and a phrase that must appear in the chunk
(NOT chunk ids — those change whenever chunking changes).

Metrics:
- hit@k  — fraction of questions where a matching chunk is in the top k
- MRR    — mean reciprocal rank; 1.0 = matching chunk always ranked first

--with-llm additionally asks Ollama each question and checks the answer
isn't a refusal, contains the expected keywords, and cites >=1 matching
chunk. Rough, but an honest signal to compare models with.

Run: python -m filinglens.eval [-k 6] [--with-llm] [--model llama3.2]
"""

from __future__ import annotations

import argparse
import json

from filinglens.config import ROOT_DIR
from filinglens.retrieve import Hit, retrieve

GOLDEN_PATH = ROOT_DIR / "eval" / "golden_qa.jsonl"


def load_golden(path=GOLDEN_PATH) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def hit_matches(hit: Hit, expected: dict) -> bool:
    return (
        hit.ticker == expected["ticker"]
        and hit.item in expected["items"]
        and expected["must_contain"].lower() in hit.text.lower()
    )


def match_rank(hits: list[Hit], expected: dict) -> int | None:
    """1-based rank of the first matching hit, or None if absent."""
    for i, hit in enumerate(hits):
        if hit_matches(hit, expected):
            return i + 1
    return None


def summarize(ranks: list[int | None]) -> dict:
    n = len(ranks)
    return {
        "n": n,
        "hit_rate": sum(r is not None for r in ranks) / n,
        "mrr": sum(1 / r for r in ranks if r is not None) / n,
    }


def answer_ok(result, expected: dict, keywords: list[str]) -> bool:
    """Answer passes if it's not a refusal, mentions the expected keywords,
    and at least one of its citations points at a matching chunk."""
    from filinglens.answer import NOT_FOUND

    if result.text.strip() == NOT_FOUND:
        return False
    if not all(kw.lower() in result.text.lower() for kw in keywords):
        return False
    return any(
        hit_matches(result.hits[c.marker - 1], expected) for c in result.citations
    )


def run(k: int = 6, with_llm: bool = False, model: str = "llama3.2") -> dict:
    from filinglens.embed import LocalEmbedder, get_collection

    embedder = LocalEmbedder()  # load the model once for all questions
    collection = get_collection()
    llm = None
    if with_llm:
        from filinglens.answer import OllamaLLM

        llm = OllamaLLM(model=model)

    golden = load_golden()
    ranks: list[int | None] = []
    answers_ok = []
    print(f"{'question id':<24} {'rank':>4}" + ("  answer" if with_llm else ""))
    for g in golden:
        hits = retrieve(g["question"], k=k, embedder=embedder, collection=collection)
        rank = match_rank(hits, g["expected"])
        ranks.append(rank)
        line = f"{g['id']:<24} {rank if rank else '—':>4}"
        if with_llm:
            from filinglens.answer import answer_question

            result = answer_question(
                g["question"], k=k, llm=llm, embedder=embedder, collection=collection
            )
            ok = answer_ok(result, g["expected"], g.get("answer_contains", []))
            answers_ok.append(ok)
            line += f"  {'PASS' if ok else 'FAIL'}"
        print(line)

    s = summarize(ranks)
    print(f"\nretrieval: hit@{k} = {s['hit_rate']:.0%}   MRR = {s['mrr']:.2f}   (n={s['n']})")
    if with_llm:
        s["answer_pass_rate"] = sum(answers_ok) / len(answers_ok)
        print(f"answers ({model}): {s['answer_pass_rate']:.0%} pass")
    return s


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("-k", type=int, default=6)
    p.add_argument("--with-llm", action="store_true")
    p.add_argument("--model", default="llama3.2")
    a = p.parse_args()
    run(k=a.k, with_llm=a.with_llm, model=a.model)
