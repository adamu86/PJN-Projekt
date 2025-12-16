# Pytania-odpowiedzi dla dokumentów domenowych (closed-domain QA)

System po załadowaniu pakietu dokumentów (np. regulaminy, FAQ, syllabusy)
odpowiada na pytania użytkownika, zwracając fragment źródłowy.

Dokumenty powinny zostać podzielone na mniejsze fragmenty tzw. pasusy (np. punkt
regulaminu, akapit). Użytkownik zadaje pytanie i aplikacja przygotowuje ranking
pasusów np. algorytmem BM25. (lematyzacja, usuwanie lub nie stop-słów, lower case).

W ramach znalezionego fragmentu tekstu zastosowanie reguł do precyzyjnej odpowiedzi
typu:

Pytanie: Ile wynosi opłata rejestracyjna?

Pasus: Opłata rejestracyjna samochodu (bez wymiany tablic) wynosi 160 zł. Całkowity
koszt może być wyższy i zależy od tego, czy potrzebujesz nowych tablic, pozwolenia
czasowego, tablic indywidualnych, czy też rejestrujesz pojazd z zagranicy, co wiąże się z
dodatkowymi opłatami, takimi jak akcyza.

Odpowiedź: 160zł

NER (Named Entity Recognition) do kwot, dat, miejsc, osób.
Sprawdzenie czy odpowiedzią może być: <br />
● liczba np. ["wynosi","opłata","koszt","kwota","liczba","wysokość"] <br />
● data/czas ["termin","do","od","kiedy","deadline","data"], <br />
● miejsce ["miejsce","w","na","adres","lokalizacja"] <br />
● osoba/organizacja ["kto","osoba","organ","instytucja"]

Ewaluacja na ręcznie przygotowanym zbiorze Q&A (100+):
Miary: Mean Reciprocal Rank@k, Recall@k dla wyszukiwania pasusów.

Przegląd metod i technologii do sprawdzenia/zastosowania:
Python - główny język implementacji systemu, integracja bibliotek NLP i wyszukiwania, łatwa budowa
backendu
spaCy - tokenizacja, lematyzacja, rozpoznawanie części mowy, POS tagging
rank-bm25 - BM25, wypisywanie rankingów pasusów na podstawie podobieństwa tekstu
Metryki: MRR@k, Recall@k - ocena skuteczności wyszukiwania pasusów