import re
from importlib.resources import path
from bm25_engine import BM25Engine
from answer_extractor import answer_extraction

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
    # answers = answer_extraction(results, q)
    # print("\nZnalezione NER: ")
    # for ner in answers:
    #     print(f"{ner.text} ({ner.label_})")
    print("\nRanking:")
    for p, score in results:
        print(f"[{score:.2f}] {p}")
    print("\n")
