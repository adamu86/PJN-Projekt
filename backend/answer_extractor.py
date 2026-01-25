import spacy
import subprocess
import sys
import re


try:
    nlp = spacy.load("pl_core_news_md")
except OSError:
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "pl_core_news_md"])
    nlp = spacy.load("pl_core_news_md")

QUESTION_TYPES = {
    "number": ["ile", "koszt", "opłata", "kwota", "wysokość", "wynosi"],
    "date": ["kiedy", "termin", "od", "do", "deadline", "data"],
    "place": ["miejsce", "w", "na", "adres", "lokalizacja"],
    "person_organization": ["kto", "osoba", "organ", "instytucja"]
}

def question_type(question):
    question_lower = question.lower()

    for question_type, keywords in QUESTION_TYPES.items():
        if any(word in question_lower for word in keywords):
            return question_type
        
    return "text"

def extract_date_regex(text):
    months = r"(stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)"
    
    match_text = re.findall(fr"\b\d{{1,2}}\s+{months}(?:\s+\d{{4}}\s*r?\.)?\b", text, re.IGNORECASE)
    if match_text:
        return match_text
    
    match_digit = re.findall(r"\b\d{1,2}[.-]\d{1,2}[.-]\d{2,4}\b", text)
    if match_digit:
        return match_digit
    
    return None

def extract_number_regex(text):
    match = re.findall(r"\b\d+(?:[.,]\d+)?\b", text)
    if match:
        return match
    
    return None

def answer_extraction(results, question):
    qtype = question_type(question)

    for p, score in results:
        doc = nlp(p)

        ents = [ent for ent in doc.ents]

        if qtype == "number":
            numbers = [ent.text for ent in ents if ent.label_ in ["MONEY", "CARDINAL"]]
            if not numbers:
                regex_number = extract_number_regex(p)
                if regex_number:
                    numbers = [regex_number]
            if numbers:
                return numbers, p
            
        elif qtype == "date":
            dates = [ent.text for ent in ents if ent.label_ in ["DATE", "TIME"]]
            if not dates:
                regex_date = extract_date_regex(p)
                if regex_date:
                    dates = [regex_date]
            if dates:
                return dates, p
            
        elif qtype == "place":
            places = [ent.text for ent in ents if ent.label_ in ["LOC", "GPE", "FACILITY", "ORG"]]
            if places:
                return places, p
        
        elif qtype == "person_organization":
            per_org = [ent.text for ent in ents if ent.label_ in ["PER", "ORG"]]
            if per_org:
                return per_org, p
        
        else:
            return p, p

    return results[0][0], results[0][0]
