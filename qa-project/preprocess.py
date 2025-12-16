import spacy

nlp = spacy.load("pl_core_news_sm")

def preprocess(text):
    doc = nlp(text.lower())
    tokens = [
        token.lemma_
        for token in doc
        if not token.is_stop and not token.is_punct
    ]
    return tokens