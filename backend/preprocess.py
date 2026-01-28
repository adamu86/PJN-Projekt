"""Moduł preprocessingu tekstowego dla języka polskiego.

Ładuje model spaCy `pl_core_news_lg`
i udostępnia funkcję lematyzacji tekstów polskich.
"""

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
    """Tokenizacja i lematyzacja tekstu polskiego.

    Args:
        text: Tekst do przetwarzenia.
        remove_stopwords: Jeśli True, usuwa stop words z wyniku.

    Returns:
        Lista lematów (tokenów w formie podstawowej).
    """
    doc = nlp(text.lower())

    if remove_stopwords:
        tokens = [
            token.lemma_
            #token.text
            for token in doc
            if not token.is_stop and not token.is_punct
        ]
    else:
        tokens = [
            token.lemma_
            #token.text
            for token in doc
            if not token.is_punct
        ]

    return tokens