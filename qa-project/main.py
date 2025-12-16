from importlib.resources import path
from bm25_engine import BM25Engine

with open("data/regulamin.txt", encoding="utf-8") as f:
    passages = [line.strip() for line in f if line.strip()]

engine = BM25Engine(passages)

q = input("\nZadaj pytanie > ")

results = engine.query(q)
print("\nRanking:")
for p, score in results:
    print(f"[{score:.2f}] {p}")
print("\n")