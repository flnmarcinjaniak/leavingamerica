# Pinterest — instrukcja

126 pinów wygenerowanych 7 sierpnia 2026. Katalog `video/pins-output/`.

**Dlaczego Pinterest, a nie kolejne shorty:** każdy pin **jest klikalnym linkiem**,
w przeciwieństwie do TikToka i Shorts, gdzie linku w filmie nie da się umieścić
na żadnej platformie. Do tego Pinterest to wyszukiwarka — pin pracuje **latami**,
nie 48 godzin. I trafia w demografię 45+, czyli w Twojego emeryta.

---

## CO MASZ

| Typ | Ile | Cel linku |
|---|---|---|
| Kraje (`country-*.png`) | 74 | `/countries/<kraj>/` |
| Miasta (`city-*.png`) | 46 | `/countries/<kraj>/` |
| Rankingi (`list-*.png`) | 4 | raport / kalkulator |
| Kontrasty (`contrast-*.png`) | 3 | raport / kalkulator |

Plus **`pins.csv`** — tytuł, opis, link i sugerowana tablica dla każdego pinu.
Otwiera się w Excelu i w Arkuszach Google.

---

## KROK 1 — konto firmowe (15 min, jednorazowo)

1. **pinterest.com/business/create** — załóż konto firmowe (darmowe).
   Osobiste nie ma statystyk ani Rich Pins.
2. **Zweryfikuj domenę:** Ustawienia → Zgłoszone konta → Zgłoś stronę.
   Dostaniesz metatag do wklejenia w `<head>`. **Powiedz mi, to wkleję.**
   Weryfikacja daje: logo przy każdym pinie z Twojej domeny, statystyki
   i wyższe zaufanie algorytmu.
3. **Włącz Rich Pins:** developers.pinterest.com/tools/url-debugger —
   wklej dowolny adres ze strony i kliknij Apply. Rich Pins automatycznie
   dociągają tytuł i opis ze strony, co podnosi klikalność.

## KROK 2 — tablice (30 min)

Załóż **7 tablic** o dokładnie tych nazwach (są w kolumnie `board` w CSV):

- Cost of Living Abroad
- Cheapest Cities to Live
- Best Countries to Move To
- FIRE and Early Retirement Abroad
- Digital Nomad Visas
- Moving Abroad Tips
- Remote Work and Income Abroad

Każda tablica potrzebuje **opisu z frazami kluczowymi** — Pinterest indeksuje
także opisy tablic. Przykład dla pierwszej:

> Real monthly cost of living for 74 countries: rent, food, transport and
> healthcare. Data for Americans planning to move abroad, retire overseas
> or work remotely. Updated 2026.

## KROK 3 — publikacja (tu jest cała gra)

⚠️ **Nie wrzucaj 126 pinów naraz.** Nowe konto publikujące hurtowo dostaje
filtr spamowy. Tempo, które działa:

| Okres | Ile dziennie |
|---|---|
| Tydzień 1-2 | **5** |
| Tydzień 3-4 | 8-10 |
| Później | 10-15 |

126 pinów rozłoży się na jakieś **3 tygodnie**. Publikuj rano czasu
amerykańskiego (15:00-17:00 u Ciebie).

**Dla każdego pinu przeklej z `pins.csv`:**
- `title` → tytuł pinu
- `description` → opis (zawiera już frazy i hasztagi)
- `link` → adres docelowy
- `board` → tablica

**Planowanie:** Pinterest ma wbudowany harmonogram (do 30 pinów naprzód,
za darmo). Tailwind robi to lepiej, ale kosztuje — na start wystarczy wbudowany.

## KROK 4 — czego się spodziewać

Uczciwie: **Pinterest rozpędza się wolno.** Pierwsze wyświetlenia po 2-4
tygodniach, sensowny ruch po 2-3 miesiącach, pełnia po pół roku. Za to
**nie spada** — pin sprzed roku nadal przynosi wejścia.

Sygnał, że działa: rosnące „zapisy" (saves). Zapis jest dla algorytmu
ważniejszy niż kliknięcie, bo oznacza, że ktoś chce wrócić.

---

## ZASADY PROJEKTOWE (dlaczego piny wyglądają tak, a nie inaczej)

Wypracowane na podstawie tego, co faktycznie konwertuje:

1. **Format 1000×1500 (2:3)** — pionowe piny zajmują więcej miejsca w siatce
   i zbierają więcej kliknięć.
2. **Czytelność w miniaturze 236×354** — tak pin widać w siatce. To był
   test decydujący: jeśli liczba nie czyta się w tym rozmiarze, pin nie istnieje.
   Stąd ogromna typografia i brutalny kontrast.
3. **Jedna liczba jako punkt ogniskowy** — `$2000`, `11.9 years`, `30 days`.
4. **Nagłówek 4-8 słów** — dłuższe nie czytają się w miniaturze.
5. **Stały pasek marki na dole** — rozpoznawalność przy 126 pinach zamienia
   jeden dobry pin w obserwującego.
6. **Zdjęcia, nie klatki z wideo.** Wyciągane klatki dają przypadkowe kadry
   (klip z Lizbony dał druty trakcyjne). `fetch-photos.mjs` pobiera
   skomponowane zdjęcia z Pexels, po nazwach konkretnych miejsc.

---

## KOMENDY

```bash
cd video

node fetch-photos.mjs            # tła (raz, chyba że chcesz odświeżyć)
node generate-pins.mjs           # wszystkie 126 pinów + pins.csv
node generate-pins.mjs --limit 5 # szybki test
npx remotion studio src/pins/index.ts   # podgląd i edycja layoutów
```

Dane pinów pochodzą z `src/data/quality-scores.json` — tego samego pliku,
co strona. Po aktualizacji danych wystarczy przegenerować.
