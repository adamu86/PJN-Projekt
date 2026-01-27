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

PRIORITY_KEYWORDS = {
    "person_organization": ["kto"],
    "number": ["ile"],
    "date": ["kiedy"],
    "place": ["gdzie"]
}

QUESTION_TYPES = {
    "number": ["koszt", "opłata", "kwota", "wysokość", "wynosi"],
    "date": ["termin", "deadline", "data"],
    "place": ["miejsce", "adres", "lokalizacja"],
    "person_organization": ["osoba", "organ", "instytucja"]
}

def question_type(question):
    doc = nlp(question.lower())

    for qtype, keywords in PRIORITY_KEYWORDS.items():
        if any(token.lemma_ in keywords or token.text in keywords for token in doc):
            return qtype

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
    text_cleaned = re.sub(r"(^|\s)§?\s*\d+\.\s", r"\1", text)

    word_to_num = {
        "jeden": "1", "jednego": "1", "jedna": "1", "jednej": "1",
        "dwa": "2", "dwóch": "2", "dwie": "2",
        "trzy": "3", "trzech": "3",
        "cztery": "4", "czterech": "4",
        "pięć": "5", "pięciu": "5",
        "sześć": "6", "sześciu": "6",
        "siedem": "7", "siedmiu": "7",
        "osiem": "8", "ośmiu": "8",
        "dziewięć": "9", "dziewięciu": "9",
        "dziesięć": "10", "dziesięciu": "10"
    }

    numbers = []

    text_lower = text_cleaned.lower()
    for word, num in word_to_num.items():
        if re.search(rf"\b{word}\b", text_lower):
            numbers.append(num)

    match = re.findall(r"(?<!\w)-?\d+(?:[\s.,]?\d+)*(?:[.,]\d+)?(?:\s*(?:%|zł|złotych|złote|PLN|dni|dzień|miesięcy|miesiące|rok|lat|lata))?", text_cleaned)

    if match:
        numbers.extend([m.strip() for m in match])

    return numbers if numbers else []

def extract_place_regex(text):
    academic_places = [
        r"(dziekanat|sekretariat|biuro|rektorat|wydział|uczelnia|kampus)",
        r"w\s+(dziekanacie|sekretariacie|biurze|rektoracie|wydziale|systemie)",
        r"na\s+(wydziale|uczelni|kampusie)",
        r"do\s+(dziekanatu|sekretariatu|biura|rektoratu|wydziału)",
    ]

    for pattern in academic_places:
        match = re.search(pattern, text.lower())
        if match:
            start, end = match.span()
            return text[start:end].strip()

    return None

def extract_person_role_regex(text):
    
    roles = ["nauczyciele", "dziekan", "rektor", "prorektor", "prodziekan", "kierownik", 
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

def is_relevant_number(number, sentence, question):
    s_lower = sentence.lower()
    q_lower = question.lower()

    number_str = str(number).replace(" ", "")

    if number_str.isdigit():
        num_val = int(number_str.split('.')[0])

        if num_val >= 1900 and num_val <= 2100:
            if "rok" in s_lower or "r." in sentence or "/" in sentence:
                if "ile" in q_lower and ("rok" in q_lower or "lat" in q_lower):
                    return True
                return False

        if num_val > 100 and ("uchwała" in s_lower or "nr" in s_lower.split(number_str)[0][-10:]):
            return False

    return True

def select_best_number(numbers, sentence, question):

    if len(numbers) == 1:
        return numbers[0]

    q_lower = question.lower()
    s_lower = sentence.lower()

    money_keywords = ["opłata", "koszt", "kwota", "cena", "wynosi"]
    time_keywords = ["dni", "dzień", "termin", "miesiąc", "miesięcy", "lat", "rok", "tygodni"]

    if any(word in q_lower for word in time_keywords):
        for time_word in time_keywords:
            pattern = fr"(\d+)\s*{time_word}|{time_word}\s*(\d+)"
            match = re.search(pattern, s_lower)
            if match:
                found_num = match.group(1) or match.group(2)
                for num in numbers:
                    if found_num in num or num.startswith(found_num):
                        return num

    for word in money_keywords:
        if word in q_lower:
            pattern = fr"{word}\s+\w*\s+(\d+(?:\s*zł)?)"
            match = re.search(pattern, s_lower)
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

            elif qtype == "number":
                numbers = [ent.text for ent in ents if ent.label_ in ["MONEY", "CARDINAL"]]

                if not numbers:
                    numbers = extract_number_regex(sent_text)

                relevant_numbers = [n for n in numbers if is_relevant_number(n, sent_text, question)]

                if relevant_numbers:
                    best_number = select_best_number(relevant_numbers, sent_text, question)
                    return best_number , sent_text, passage
                
            elif qtype == "date":
                dates = [ent.text for ent in ents if ent.label_ in ["DATE", "TIME"]]

                if not dates:
                    dates = extract_date_regex(sent_text)

                if dates:
                    best_date = select_best_date(dates, sent_text, question)
                    return best_date, sent_text, passage
                
            elif qtype == "place":
                place_match = extract_place_regex(sent_text)
                if place_match:
                    return place_match, sent_text, passage

                places = [ent.text for ent in ents if ent.label_ in ["LOC", "GPE", "FACILITY", "ORG"]]

                if places:
                    return places[0], sent_text, passage
            
    best_passage = results[0][0]
    best_sentence = extract_best_sentence(best_passage, question)
    
    return best_sentence, best_sentence, best_passage
