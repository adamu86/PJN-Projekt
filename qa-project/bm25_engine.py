from rank_bm25 import BM25Okapi
from preprocess import preprocess

class BM25Engine:
    def __init__(self, passages):
        self.passages = passages
        tokenized = [preprocess(p) for p in passages]
        self.bm25 = BM25Okapi(tokenized)

    def query(self, question, k=10):
        q_tokens = preprocess(question)
        scores = self.bm25.get_scores(q_tokens)
        ranked = sorted(
            zip(self.passages, scores),
            key=lambda x: x[1],
            reverse=True
        )
        return ranked[:k]