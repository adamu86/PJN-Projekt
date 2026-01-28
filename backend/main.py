"""Główny moduł aplikacji QA dla polskiego regulaminu uczelni.

Ładuje tekst regulaminu, dzieli go na pasaże, buduje indeks wyszukiwania
i udostępnia:
- API FastAPI (GET /ask) dla frontendu
- tryb ewaluacji (--eval) z metrykami MRR@k i Recall@k
- tryb listowania pasażów (--dump)
- interaktywny tryb konsolowy
"""

import re
import json
import sys
# from tfidf_engine import TFIDFEngine as Engine
from bm25_engine import BM25Engine as Engine
# from spacy_engine import SpacyEngine as Engine
from answer_extractor import answer_extraction
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

with open("data/regulamin.txt", encoding="utf-8") as f:
    text = f.read()

paragraphs = re.split(r"\n(?=§\s*\d+)", text)
passages = []

for para in paragraphs:
    parts = re.split(r"\n(?=\d+\.)", para)
    if len(parts) == 1:
        cleaned = re.sub(r"^§\s*\d+\.?\s*", "", para)
        passages.append(" ".join(cleaned.split()))
    else:
        for part in parts:
            cleaned = re.sub(r"^\d+\.\s*", "", part)
            passages.append(" ".join(cleaned.split()))

passage_ids = list(range(len(passages)))
engine = Engine(passages, passage_ids)

def evaluate(questions_file, k=5):
    """Ewaluacja silnika wyszukiwania na zbiorze pytań z ustalonymi pasażami.

    Oblicza MRR@k i Recall@k dla każdego pytania i drukuje podsumowanie wyników.

    Args:
        questions_file: Scieżka do JSON z pytaniami (lista obiektów
            z "question" i "relevant_ids").
        k: Liczba wyników do rozważenia przy obliczaniu metryk.
    """
    with open(questions_file, encoding="utf-8") as f:
        questions = json.load(f)

    rr_scores = []
    recall_scores = []

    for item in questions:
        q = item["question"]
        relevant_ids = set(item["relevant_ids"])

        results = engine.query(q, k=k)
        retrieved_ids = [pid for pid, _, _ in results]

        rr = 0.0
        for rank, pid in enumerate(retrieved_ids, 1):
            if pid in relevant_ids:
                rr = 1.0 / rank
                break
        rr_scores.append(rr)

        found = len(relevant_ids & set(retrieved_ids))
        recall = found / len(relevant_ids) if relevant_ids else 1.0
        recall_scores.append(recall)

        status = "+" if rr > 0 else "-"
        print(f"  [{status}] RR={rr:.2f} | {q[:70]}")
        print(f"      Znalezione: {retrieved_ids}")
        print(f"      Oczekiwane: {sorted(relevant_ids)}")

    mrr = sum(rr_scores) / len(rr_scores)
    avg_recall = sum(recall_scores) / len(recall_scores)

    print(f"\n{'---------------------------'}")
    print(f"  Ewaluacja (k={k}, n={len(questions)})")
    print(f"{'---------------------------'}")
    print(f"  MRR@{k}:    {mrr:.4f}")
    print(f"  Recall@{k}: {avg_recall:.4f}")

def dump_passages():
    """Drukuje wszystkie pasaże z ich identyfikatorami do konsoli."""
    for pid, p in zip(passage_ids, passages):
        print(f"[{pid}] {p[:120]}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--eval":
            k = int(sys.argv[3]) if len(sys.argv) > 3 else 5
            evaluate(sys.argv[2], k=k)
        elif cmd == "--dump":
            dump_passages()
    else:
        while True:
            q = input("\nZadaj pytanie > ")
            results = engine.query(q, k=10)

            passage_results = [(p, score) for _, p, score in results]
            answer, sentence, passage = answer_extraction(passage_results, q)

            print(f"\nOdpowiedź: {answer}")
            print(f"Kontekst: {passage}")

            for pid, p, score in results:
                print(f"[{score:.2f}] (ID:{pid}) {p}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ask")
def ask_question(q: str):
    """Endpoint API do zadania pytania i uzyskania odpowiedzi.

    Args:
        q: Tekst pytania (query parameter).

    Returns:
        JSON z polami: answer, sentence, passage.
    """
    results = engine.query(q, k=10)

    passage_results = [(p, score) for _, p, score in results]
    answer, sentence, passage = answer_extraction(passage_results, q)
    
    return {
        "answer": answer,
        "sentence": sentence,
        "passage": passage
    }
