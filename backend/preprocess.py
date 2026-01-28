import spacy
import subprocess
import sys


model = "pl_core_news_lg"

try:
    nlp = spacy.load(model)
except OSError:
    subprocess.check_call([sys.executable, "-m", "spacy", "download", model])
    nlp = spacy.load(model)

def preprocess(text, remove_stopwords=True):
    
    doc = nlp(text.lower())

    if remove_stopwords:
        tokens = [
            token.lemma_
            for token in doc
            if not token.is_stop and not token.is_punct
        ]
    else:
        tokens = [
            token.lemma_
            for token in doc
            if not token.is_punct
        ]

    return tokens