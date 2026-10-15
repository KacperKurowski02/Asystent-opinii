# Asystent opinii

Automat do analizy opinii gości hotelowych. Zbiera opinie, klasyfikuje je przy pomocy Claude API (sentyment, kategoria), przygotowuje propozycję odpowiedzi, a wyniki podsumowuje zapytaniami SQL i pokazuje na prostej stronie.

**Strona z wynikami:** https://kacperkurowski02.github.io/Asystent-opinii/

> ⚠️ **Wszystkie dane w projekcie są fikcyjne.** Opinie, imiona gości i daty zostały wymyślone na potrzeby demonstracji.

## Jak to działa

```
Google Sheets  →  n8n  →  Claude API  →  Google Sheets  →  SQL (SQLite)  →  strona WWW
 (nowe opinie)   (workflow)  (analiza)     (wyniki)        (analiza.py)    (index.html)
```

1. **Google Sheets** – arkusz z nowymi opiniami gości.
2. **n8n** – workflow pobiera kolejne opinie z arkusza i wysyła je do modelu.
3. **Claude API** – dla każdej opinii określa sentyment (pozytywny / neutralny / negatywny), kategorię (np. obsługa, pokój, gastronomia, ceny, SPA) i pisze propozycję odpowiedzi.
4. **Google Sheets** – n8n zapisuje wyniki z powrotem do arkusza (kolumny `sentyment`, `kategoria`, `odpowiedz`, `status`).
5. **SQL** – arkusz eksportowany do `opinie.csv` trafia do bazy SQLite (`opinie.db`), gdzie `analiza.py` liczy zestawienia.
6. **Strona** – `index.html` wczytuje `data.json` i pokazuje trzy tabele: sentyment, kategorie i opinie negatywne.

## Technologie

- Google Sheets
- n8n (automatyzacja workflow)
- Claude API (Anthropic)
- Python 3 (biblioteka standardowa: `csv`, `sqlite3`, `json`)
- SQLite / SQL
- HTML, CSS, JavaScript (bez frameworków i bibliotek zewnętrznych)
- GitHub Pages

## Struktura plików

| Plik          | Opis                                                        |
|---------------|-------------------------------------------------------------|
| `opinie.csv`  | Opinie wyeksportowane z arkusza (z wynikami analizy Claude) |
| `analiza.py`  | Wczytuje CSV do SQLite, uruchamia zapytania, zapisuje JSON  |
| `data.json`   | Wyniki zapytań, z których korzysta strona                   |
| `index.html`  | Strona z trzema tabelami                                    |

## Uruchomienie `analiza.py`

Wymagany jest tylko Python 3, bez dodatkowych pakietów.

```bash
python3 analiza.py
```

Skrypt:

1. tworzy od nowa bazę `opinie.db` i wczytuje do niej `opinie.csv`,
2. wykonuje trzy zapytania SQL: opinie wg sentymentu, kategorie wg liczby negatywnych opinii, lista opinii negatywnych (od najnowszej),
3. wypisuje wyniki w terminalu i zapisuje je do `data.json`.

### Podgląd strony lokalnie

Strona pobiera `data.json` przez `fetch`, więc nie zadziała po otwarciu pliku bezpośrednio z dysku. Uruchom lokalny serwer:

```bash
python3 -m http.server
```

i otwórz http://localhost:8000.
