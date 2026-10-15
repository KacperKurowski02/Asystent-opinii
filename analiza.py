"""Analiza opinii: CSV -> SQLite -> zapytania -> data.json + wydruk w terminalu."""
import csv
import json
import sqlite3
from pathlib import Path

KATALOG = Path(__file__).resolve().parent
PLIK_CSV = KATALOG / "opinie.csv"
PLIK_DB = KATALOG / "opinie.db"
PLIK_JSON = KATALOG / "data.json"

ZAPYTANIE_SENTYMENT = """
SELECT sentyment,
       COUNT(*) AS liczba,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM opinie), 1) AS procent
FROM opinie
GROUP BY sentyment
ORDER BY liczba DESC;
"""

ZAPYTANIE_KATEGORIE = """
SELECT kategoria,
       COUNT(*) AS liczba,
       SUM(sentyment = 'negatywny') AS negatywne
FROM opinie
GROUP BY kategoria
ORDER BY negatywne DESC, liczba DESC, kategoria;
"""

ZAPYTANIE_NEGATYWNE = """
SELECT id, data, gosc, kategoria, opinia
FROM opinie
WHERE sentyment = 'negatywny'
ORDER BY data DESC, id DESC;
"""


def zaladuj_csv(conn):
    """Tworzy tabelę opinie od nowa i wczytuje do niej CSV."""
    conn.execute("DROP TABLE IF EXISTS opinie")
    conn.execute(
        """
        CREATE TABLE opinie (
            id         INTEGER PRIMARY KEY,
            data       TEXT,
            gosc       TEXT,
            opinia     TEXT,
            sentyment  TEXT,
            kategoria  TEXT,
            odpowiedz  TEXT,
            status     TEXT
        )
        """
    )
    with open(PLIK_CSV, encoding="utf-8", newline="") as f:
        wiersze = [
            (int(w["id"]), w["data"], w["gosc"], w["opinia"], w["sentyment"],
             w["kategoria"], w["odpowiedz"], w["status"])
            for w in csv.DictReader(f)
        ]
    conn.executemany("INSERT INTO opinie VALUES (?, ?, ?, ?, ?, ?, ?, ?)", wiersze)
    conn.commit()
    return len(wiersze)


def zapytaj(conn, sql):
    return [dict(w) for w in conn.execute(sql)]


def wypisz_tabele(tytul, wiersze):
    print(f"\n=== {tytul} ===")
    if not wiersze:
        print("(brak wyników)")
        return
    kolumny = list(wiersze[0])
    szer = {k: max(len(k), *(len(str(w[k])) for w in wiersze)) for k in kolumny}
    print("  ".join(k.ljust(szer[k]) for k in kolumny))
    print("  ".join("-" * szer[k] for k in kolumny))
    for w in wiersze:
        print("  ".join(str(w[k]).ljust(szer[k]) for k in kolumny))


def main():
    if PLIK_DB.exists():
        PLIK_DB.unlink()

    conn = sqlite3.connect(PLIK_DB)
    conn.row_factory = sqlite3.Row
    try:
        liczba = zaladuj_csv(conn)
        wyniki = {
            "liczba_opinii": liczba,
            "sentyment": zapytaj(conn, ZAPYTANIE_SENTYMENT),
            "kategorie": zapytaj(conn, ZAPYTANIE_KATEGORIE),
            "negatywne": zapytaj(conn, ZAPYTANIE_NEGATYWNE),
        }
    finally:
        conn.close()

    with open(PLIK_JSON, "w", encoding="utf-8") as f:
        json.dump(wyniki, f, ensure_ascii=False, indent=2)

    print(f"Wczytano {liczba} opinii do {PLIK_DB.name}")
    wypisz_tabele("(a) Opinie wg sentymentu", wyniki["sentyment"])
    wypisz_tabele("(b) Kategorie wg liczby negatywnych", wyniki["kategorie"])
    wypisz_tabele("(c) Opinie negatywne (od najnowszej)", wyniki["negatywne"])
    print(f"\nZapisano wyniki do {PLIK_JSON.name}")


if __name__ == "__main__":
    main()
