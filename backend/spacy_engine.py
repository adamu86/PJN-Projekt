import numpy as np
from preprocess import nlp


class SpacyEngine:
    def __init__(self, passages, passage_ids=None):
        self.passages = passages
        self.passage_ids = passage_ids if passage_ids is not None else list(range(len(passages)))
        self.passage_vectors = np.array([nlp(p.lower()).vector for p in passages])
        norms = np.linalg.norm(self.passage_vectors, axis=1, keepdims=True)
        self.passage_vectors_norm = self.passage_vectors / (norms + 1e-8)

    def query(self, question, k=10):
        q_vec = nlp(question.lower()).vector
        q_norm = q_vec / (np.linalg.norm(q_vec) + 1e-8)
        scores = self.passage_vectors_norm @ q_norm
        ranked = sorted(
            zip(self.passage_ids, self.passages, scores.tolist()),
            key=lambda x: x[2],
            reverse=True
        )
        return ranked[:k]
