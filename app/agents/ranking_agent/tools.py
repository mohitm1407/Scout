from rank_bm25 import BM25Okapi
from ..base import Reference


async def rank(references, search_text, n=5) -> list[Reference]:
    corpus = [ref.reference_title.lower().split() for ref in references]

    bm25 = BM25Okapi(corpus)

    scores = bm25.get_scores(search_text.lower().split())

    ranked = sorted(
        zip(references, scores),
        key=lambda x: x[1],
        reverse=True,
    )

    return [ref for ref, _ in ranked[:n]]
