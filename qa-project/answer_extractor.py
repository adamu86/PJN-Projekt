import spacy

nlp = spacy.load("pl_core_news_sm")

def answer_extraction(results, question):
    answers = []
    for p, score in results:
        doc = nlp(p)
        for ent in doc.ents:
            answers.append(ent)
    return answers