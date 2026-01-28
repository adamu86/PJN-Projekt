"""Silnik wyszukiwania oparty na TF-IDF.

Wykorzystuje macierz TF-IDF z sklearn z niestandardowym analizatorem
opartym o lematyzację spaCy, a następnie tworzy ranking wyników
na podstawie podobieństwa cosinusowego.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from preprocess import preprocess


class TFIDFEngine:
    """Silnik wyszukiwania oparty na TF-IDF + cosine similarity.

    Buduje macierz TF-IDF dla pasażów, wykorzystując lematyzację
    z modelu spaCy jako analizator tokenów.
    """

    def __init__(self, passages, passage_ids=None):
        """Buduje macierz TF-IDF dla podanych pasażów.

        Args:
            passages: Lista tekstów pasażów do zaindeksowania.
            passage_ids: Opcjonalna lista identyfikatorów pasażów.
                Jeśli None, przypisuje kolejne liczby od 0.
        """
        self.passages = passages
        self.passage_ids = passage_ids if passage_ids is not None else list(range(len(passages)))
        self.vectorizer = TfidfVectorizer(analyzer=lambda text: preprocess(text))
        self.tfidf_matrix = self.vectorizer.fit_transform(passages)

    def query(self, question, k=10):
        """Wyszukuje pasaże najbardziej dopasowane do zapytania.

        Args:
            question: Tekst zapytania.
            k: Liczba wyników do zwrócenia.

        Returns:
            Lista krotek (passage_id, passage_text, score) posortowana
            malejąco po score (podobieństwo cosinusowe TF-IDF).
        """
        q_vec = self.vectorizer.transform([question])
        scores = cosine_similarity(q_vec, self.tfidf_matrix)[0]
        ranked = sorted(
            zip(self.passage_ids, self.passages, scores),
            key=lambda x: x[2],
            reverse=True
        )
        return ranked[:k]
