from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from preprocess import preprocess


class TFIDFEngine:
    def __init__(self, passages, passage_ids=None):
        self.passages = passages
        self.passage_ids = passage_ids if passage_ids is not None else list(range(len(passages)))
        self.vectorizer = TfidfVectorizer(analyzer=lambda text: preprocess(text))
        self.tfidf_matrix = self.vectorizer.fit_transform(passages)

    def query(self, question, k=10):
        q_vec = self.vectorizer.transform([question])
        scores = cosine_similarity(q_vec, self.tfidf_matrix)[0]
        ranked = sorted(
            zip(self.passage_ids, self.passages, scores),
            key=lambda x: x[2],
            reverse=True
        )
        return ranked[:k]
