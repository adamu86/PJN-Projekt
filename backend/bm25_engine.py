"""Silnik wyszukiwania oparty na algorytmie BM25.

Wykorzystuje bibliotekę `rank_bm25` do rankingu pasażów tekstowych
na podstawie dopasowania słów kluczowych do zapytania.
"""

from rank_bm25 import BM25Plus
# from rank_bm25 import BM25Okapi
from preprocess import preprocess

class BM25Engine:
    """Silnik wyszukiwania oparty na BM25.

    Indeksuje podane pasaże tekstowe po ich tokenizacji i lematyzacji,
    a następnie umożliwia rankingowe wyszukiwanie na podstawie zapytań.
    """

    def __init__(self, passages, passage_ids=None):
        """Buduje indeks BM25 dla podanych pasażów.

        Args:
            passages: Lista tekstów pasażów do zaindeksowania.
            passage_ids: Opcjonalna lista identyfikatorów pasażów.
                Jeśli None, przypisuje kolejne liczby od 0.
        """
        self.passages = passages
        self.passage_ids = passage_ids if passage_ids is not None else list(range(len(passages)))
        tokenized = [preprocess(p) for p in passages]
        self.bm25 = BM25Plus(tokenized)

    def query(self, question, k=10):
        """Wyszukuje pasaże najlepiej dopasowane do zapytania.

        Args:
            question: Tekst zapytania.
            k: Liczba wyników do zwrócenia.

        Returns:
            Lista krotek (passage_id, passage_text, score) posortowana
            malejąco po score.
        """
        q_tokens = preprocess(question)
        scores = self.bm25.get_scores(q_tokens)
        ranked = sorted(
            zip(self.passage_ids, self.passages, scores),
            key=lambda x: x[2],
            reverse=True
        )
        return ranked[:k]