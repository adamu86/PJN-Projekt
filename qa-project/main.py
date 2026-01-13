import re
from importlib.resources import path
from bm25_engine import BM25Engine

with open("data/regulamin.txt", encoding="utf-8") as f:
    text = f.read()

paragraphs = re.split(r"\n(?=§\s*\d+)", text)
passages = []

for para in paragraphs:
    parts = re.split(r"\n(?=\d+\.)", para)
    if len(parts) == 1:
        passages.append(" ".join(para.split()))
    else:
        for part in parts:
            passages.append(" ".join(part.split()))

engine = BM25Engine(passages)

while(1):
    q = input("\nZadaj pytanie > ")

    results = engine.query(q)
    print("\nRanking:")
    for p, score in results:
        print(f"[{score:.2f}] {p}")
    print("\n")