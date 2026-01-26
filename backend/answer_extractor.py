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
    "person_organization": ["kto", "osoba", "organ", "instytucja"],
    "yes_no": ["czy", "możliwe", "można"]
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
        return [m.strip() for m in match]
    return []

def extract_person_role_regex(text):
    
    roles = ["dziekan", "rektor", "prorektor", "prodziekan", "kierownik", 
             "przewodniczący", "komisja", "senat", "rada", "minister", 
             "student", "promotor", "opiekun", "wykładowca", "prowadzący"]
    
    action_patterns = [
        r"podejmuje\s+(\w+(?:\s+lub\s+jego\s+zastępca)?)",
        r"wydaje\s+(\w+)",
        r"decyduje\s+(\w+)",
        r"ustala\s+(\w+)",
        r"zatwierdza\s+(\w+)",
        r"powołuje\s+(\w+)"
    ]
    
    text_lower = text.lower()

    for pattern in action_patterns:
        match = re.search(pattern, text_lower)
        if match:
            candidate = match.group(1).strip()
            for role in roles:
                if role in candidate:
                    return role.capitalize()

    for role in roles:
        if role in text_lower:
            return role.capitalize()
    
    return None

def extract_yes_no_answer(sentence, passage):

    negative_patterns = [r"\bnie\s+jest\s+możliwe", r"\bnie\s+może", r"\bnie\s+wolno", r"\bzakazane", r"\bniemożliwe", r"\bnie\s+można"]
    positive_patterns = [r"\bjest\s+możliwe", r"\bmoże", r"\bma\s+prawo", r"\buprawni", r"\bmożna", r"\bdozwolone"]

    text = sentence.lower()
    
    for pattern in negative_patterns:
        if re.search(pattern, text):
            explanation = sentence.split(',')[0] if ',' in sentence else sentence
            return f"Nie. {explanation}"
    
    for pattern in positive_patterns:
        if re.search(pattern, text):
            explanation = sentence.split(',')[0] if ',' in sentence else sentence
            return f"Tak. {explanation}"
    
    return None

def select_best_date(dates, sentence, question):

    if len(dates) == 1:
        return dates[0]
    
    start_keywords = ["rozpoczyna", "zaczyna", "start", "od", "początek"]
    end_keywords = ["kończy", "koniec", "do", "zakończenie"]
    
    q_lower = question.lower()
    s_lower = sentence.lower()
    
    asking_about_start = any(word in q_lower for word in start_keywords)
    asking_about_end = any(word in q_lower for word in end_keywords)
    
    if asking_about_end:
        for keyword in end_keywords:

            pattern = fr"{keyword}\s+(?:się\s+)?(.+?)(?:\.|,|$)"
            match = re.search(pattern, s_lower)
            if match:
                date_context = match.group(1)

                for date in dates:
                    if date.lower() in date_context:
                        return date
    
    if asking_about_start:
        for keyword in start_keywords:
            pattern = fr"{keyword}\s+(?:się\s+)?(.+?)(?:\.|,|a\s)"
            match = re.search(pattern, s_lower)
            if match:
                date_context = match.group(1)
                for date in dates:
                    if date.lower() in date_context:
                        return date

    return dates[0]

def select_best_number(numbers, sentence, question):

    if len(numbers) == 1:
        return numbers[0]
    
    q_lower = question.lower()
    
    key_words = ["opłata", "koszt", "kwota", "cena", "wynosi"]
    
    for word in key_words:
        if word in q_lower:
            pattern = fr"{word}\s+\w*\s+(\d+(?:\s*zł)?)"
            match = re.search(pattern, sentence.lower())
            if match:
                found_num = match.group(1)
                for num in numbers:
                    if found_num in num or num in found_num:
                        return num
    
    return numbers[0]

def extract_best_sentence(passage, question):
    doc = nlp(passage)
    question_tokens = set(preprocess_simple(question))
    
    best_sent = None
    best_overlap = 0
    
    for sent in doc.sents:
        sent_tokens = set(preprocess_simple(sent.text))
        overlap = len(question_tokens & sent_tokens)
        
        if overlap > best_overlap:
            best_overlap = overlap
            best_sent = sent.text
    
    return best_sent if best_sent else list(doc.sents)[0].text

def preprocess_simple(text):
    doc = nlp(text.lower())
    return [token.lemma_ for token in doc if not token.is_punct]

def answer_extraction(results, question):
    if not results:
        return "Nie znaleziono odpowiedzi", None, None
    
    qtype = question_type(question)

    for passage, score in results:
        doc = nlp(passage)

        for sent in doc.sents:
            sent_text = sent.text
            ents = sent.ents

            #print(sent)

            if qtype == "person_organization":
                role = extract_person_role_regex(sent_text)
                if role:
                    return role, sent_text, passage
                
                per_org = [ent.text for ent in ents if ent.label_ in ["PER", "ORG"]]
                if per_org:
                    return per_org[0], sent_text, passage

            if qtype == "number":
                numbers = [ent.text for ent in ents if ent.label_ in ["MONEY", "CARDINAL"]]

                if not numbers:
                    numbers = extract_number_regex(sent_text)

                if numbers:
                    best_number = select_best_number(numbers, sent_text, question)
                    return best_number , sent_text, passage
                
            elif qtype == "date":
                dates = [ent.text for ent in ents if ent.label_ in ["DATE", "TIME"]]

                if not dates:
                    dates = extract_date_regex(sent_text)

                if dates:
                    best_date = select_best_date(dates, sent_text, question)
                    return best_date, sent_text, passage
                
            elif qtype == "place":
                places = [ent.text for ent in ents if ent.label_ in ["LOC", "GPE", "FACILITY", "ORG"]]
                
                if places:
                    return places, sent_text, passage
                
            elif qtype == "yes_no":
                yn_answer = extract_yes_no_answer(sent_text, passage)
                if yn_answer:
                    return yn_answer, sent_text, passage

    best_passage = results[0][0]
    best_sentence = extract_best_sentence(best_passage, question)
    
    return best_sentence, best_sentence, best_passage
