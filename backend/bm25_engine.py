from rank_bm25 import BM25Plus
# from rank_bm25 import BM25Okapi
from preprocess import preprocess

class BM25Engine:
    def __init__(self, passages, passage_ids=None):
        self.passages = passages
        self.passage_ids = passage_ids if passage_ids is not None else list(range(len(passages)))
        tokenized = [preprocess(p) for p in passages]
        self.bm25 = BM25Plus(tokenized)

    def query(self, question, k=10):
        q_tokens = preprocess(question)
        scores = self.bm25.get_scores(q_tokens)
        ranked = sorted(
            zip(self.passage_ids, self.passages, scores),
            key=lambda x: x[2],
            reverse=True
        )
        return ranked[:k]