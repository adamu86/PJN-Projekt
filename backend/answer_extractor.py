import spacy
import subprocess
import sys
import re


model = "pl_core_news_lg"

try:
    nlp = spacy.load(model)
except OSError:
    subprocess.check_call([sys.executable, "-m", "spacy", "download", model])
    nlp = spacy.load(model)

QUESTION_TYPES = {
    "number": ["ile", "koszt", "opłata", "kwota", "wysokość", "wynosi"],
    "date": ["kiedy", "termin", "od", "do", "deadline", "data"],
    "place": ["miejsce", "w", "na", "gdzie", "adres", "lokalizacja"],
    "person_organization": ["kto", "osoba", "organ", "instytucja"]
}

def question_type(question):
    doc = nlp(question.lower())

    for qtype, keywords in QUESTION_TYPES.items():
        if any(token.lemma_.lower() in keywords or token.text.lower() in keywords for token in doc):
            return qtype

    return "text"

def extract_date_regex(text):
    months = r"(?:stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)"
    
    match_text = re.findall(fr"\b\d{{1,2}}\s+{months}(?:\s+\d{{4}}\s*r?\.)?\b", text, re.IGNORECASE)
    if match_text:
        return match_text
    
    match_digit = re.findall(r"\b\d{1,2}[.-]\d{1,2}[.-]\d{2,4}\b", text)
    if match_digit:
        return match_digit
    
    return []

def extract_number_regex(text):
    match = re.findall(r"(?<!\w)-?\d+(?:[\s.,]?\d+)*(?:[.,]\d+)?(?:%|zł|złotych|złote|PLN)?", text)

    if match:
        return match
    
    return []

def answer_extraction(results, question):
    qtype = question_type(question)

    for passage, score in results:
        doc = nlp(passage)

        for sent in doc.sents:
            sent_text = sent.text
            ents = sent.ents

            print(sent)

            if qtype == "number":
                numbers = [ent.text for ent in ents if ent.label_ in ["MONEY", "CARDINAL"]]

                if not numbers:
                    numbers = extract_number_regex(sent_text)

                if numbers:
                    return numbers, sent_text, passage
                
            elif qtype == "date":
                dates = [ent.text for ent in ents if ent.label_ in ["DATE", "TIME"]]

                if not dates:
                    dates = extract_date_regex(sent_text)

                if dates:
                    return dates, sent_text, passage
                
            elif qtype == "place":
                places = [ent.text for ent in ents if ent.label_ in ["LOC", "GPE", "FACILITY", "ORG"]]
                
                if places:
                    return places, sent_text, passage
            
            elif qtype == "person_organization":
                per_org = [ent.text for ent in ents if ent.label_ in ["PER", "ORG"]]

                if per_org:
                    return per_org, sent_text, passage

    return None, None, results[0][0]
