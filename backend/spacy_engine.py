"""Silnik wyszukiwania oparty na wektorach spaCy.

Wykorzystuje średnie wektory słów z modelu `pl_core_news_lg`
do obliczenia podobieństwa cosinusowego między zapytaniem a pasażami.
"""

import numpy as np
from preprocess import nlp


class SpacyEngine:
    """Silnik wyszukiwania oparty na wektorach dokumentów spaCy.

    Oblicza wektory pasażów jako średnie wektorów słów z modelu spaCy,
    a następnie tworzy ranking wyników na podstawie podobieństwa cosinusowego.
    """

    def __init__(self, passages, passage_ids=None):
        """Oblicza i normalizuje wektory dla wszystkich pasażów.

        Args:
            passages: Lista tekstów pasażów do zaindeksowania.
            passage_ids: Opcjonalna lista identyfikatorów pasażów.
                Jeśli None, przypisuje kolejne liczby od 0.
        """
        self.passages = passages
        self.passage_ids = passage_ids if passage_ids is not None else list(range(len(passages)))
        self.passage_vectors = np.array([nlp(p.lower()).vector for p in passages])
        norms = np.linalg.norm(self.passage_vectors, axis=1, keepdims=True)
        self.passage_vectors_norm = self.passage_vectors / (norms + 1e-8)

    def query(self, question, k=10):
        """Wyszukuje pasaże najbardziej podobne do zapytania.

        Args:
            question: Tekst zapytania.
            k: Liczba wyników do zwrócenia.

        Returns:
            Lista krotek (passage_id, passage_text, score) posortowana
            malejąco po score (podobieństwo cosinusowe).
        """
        q_vec = nlp(question.lower()).vector
        q_norm = q_vec / (np.linalg.norm(q_vec) + 1e-8)
        scores = self.passage_vectors_norm @ q_norm
        ranked = sorted(
            zip(self.passage_ids, self.passages, scores.tolist()),
            key=lambda x: x[2],
            reverse=True
        )
        return ranked[:k]
