import spacy
import subprocess
import sys


try:
    nlp = spacy.load("pl_core_news_md")
except OSError:
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "pl_core_news_md"])
    nlp = spacy.load("pl_core_news_md")

def preprocess(text):
    doc = nlp(text.lower())
    tokens = [
        token.lemma_
        for token in doc
        if not token.is_stop and not token.is_punct
    ]
    return tokens