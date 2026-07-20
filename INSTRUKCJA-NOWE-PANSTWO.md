# INSTRUKCJA: DODANIE NOWEGO PAŃSTWA DO SERWISU

> Kolejność ma znaczenie — idź krok po kroku. Przykład: dodajemy fikcyjną "Panamę 2"
> o slugu `panama2`. Wszędzie gdzie piszę SLUG/NAZWA/ISO — podstaw swoje.
> Czas całości: ~1–2 h pracy + czas skryptów. Koszt: ~$0.10 API Anthropic na kraj.

---

## CO POWSTAJE AUTOMATYCZNIE PO DODANIU KRAJU

Po przejściu tej instrukcji kraj dostaje automatycznie:
- stronę `/countries/SLUG/` (pełny profil + afiliacje: SafetyWing, MyExpatTaxes, NordVPN, Saily)
- stronę `/fire/SLUG/` (kalkulator FIRE + artykuł + afiliacje) — jeśli ma budget
- miejsce w Runway Calculator `/runway/`
- miejsce w Salary Arbitrage na homepage
- miejsce w Country Match Quiz
- miejsce w rankingu `/countries/` i `/fire/`
- wpis w sitemap (generowany przy buildzie)

Opcjonalnie (osobne kroki): strony porównań `/compare/X-vs-SLUG/`, strony goals.

---

## KROK 1 — Dodaj kraj do list w skryptach Pythona · 10 min

Każdy skrypt fetch ma własną listę krajów. Dodaj NAZWĘ (po angielsku) do:

1. **`scripts/fetch-quality-scores.py`** — DWA miejsca:
   - słownik `COUNTRIES` (ok. linii 60–100): `"Nazwa": ["Nazwa", "Alias1"]`
     (aliasy = jak kraj bywa nazywany w tabelach Wikipedii, np. "Czechia" dla Czech)
   - słownik tax systems (ok. linii 150–200): `"Nazwa": "territorial"` 
     (wartości: `worldwide` / `territorial` / `zero` — sprawdź w wiarygodnym źródle!)
2. **`scripts/fetch-monthly-budget.py`** — lista krajów
3. **`scripts/fetch-country-facts.py`** — lista krajów (+ kod ISO-2)
4. **`scripts/fetch-english-proficiency-only.py`** — lista krajów

Skrypty `generate-*` iterują po slugach z JSON-a — zwykle nie wymagają edycji,
ale sprawdź czy nie mają własnych list wykluczeń.

## KROK 2 — Uruchom pipeline danych W TEJ KOLEJNOŚCI · ~20 min

```
py scripts/fetch-quality-scores.py      # metryki jakości (Numbeo, World Bank, Wiki)
py scripts/recompute-grades.py          # ZAWSZE po fetch-quality-scores
py scripts/fetch-monthly-budget.py      # budget_single/couple (WhereNext)
py scripts/fetch-country-facts.py       # geografia (REST Countries) — patrz UWAGA
py scripts/generate-quick-facts.py      # akapit "WHAT X IS LIKE" (Claude API, ~$0.02)
py scripts/generate-fire-content.py     # artykuł FIRE (Claude API, ~$0.05)
```

**UWAGA — limity:**
- `fetch-country-facts.py`: REST Countries free tier = 500 req/mies., reset 20-go.
  Jeden nowy kraj = 1 request, ale sprawdź zużycie jeśli w tym miesiącu robiłeś full refresh.
- `fetch-quality-scores.py`: Numbeo rate-limituje po IP — jak zablokuje, restart routera.
- Klucze w `.env`: `RESTCOUNTRIES_API_KEY`, `ANTHROPIC_API_KEY` (są już skonfigurowane).

**Weryfikacja:** otwórz `src/data/quality-scores.json`, znajdź swój slug i sprawdź że ma:
`budget_single`, `budget_couple`, `grade_percent`, `tax_system`, `capital`,
`quick_facts_paragraph`, `fire_article`. Jak czegoś brakuje — popraw zanim pójdziesz dalej.

## KROK 3 — Dodaj NAMES + ISO2 w plikach frontendu · 20 min

W **9 plikach** są słowniki `NAMES` (slug → nazwa wyświetlana) i `ISO2` (slug → kod
flagi, małe litery). Dodaj wpis `'SLUG':'Nazwa'` i `'SLUG':'iso'` do KAŻDEGO:

| # | Plik | Co dodać |
|---|------|----------|
| 1 | `src/pages/countries/[slug].astro` | NAMES + ISO2 |
| 2 | `src/pages/countries/index.astro` | NAMES + ISO2 |
| 3 | `src/pages/fire/[slug].astro` | NAMES + ISO2 |
| 4 | `src/pages/fire/index.astro` | NAMES + ISO2 |
| 5 | `src/pages/runway.astro` | NAMES + ISO2 |
| 6 | `src/pages/country-match/quiz.astro` | NAMES + ISO2 **+ pule cech (krok 4!)** |
| 7 | `src/pages/taxes/index.astro` | NAMES (jeśli jest słownik) |
| 8 | `src/pages/compare/[pair].astro` | NAMES + ISO2 (potrzebne dopiero przy parach) |
| 9 | `src/pages/countries/goals/[goal].astro` | NAMES + ISO2 |
| 10 | `src/pages/index.astro` (homepage) | `<option value="XX">Nazwa</option>` w selektorze Salary Arbitrage + wpis w mapie ISO→slug (szukaj `"MT": "malta"`) |

**Najprościej:** powiedz Claude'owi w Claude Code: *"dodaj kraj SLUG (Nazwa, ISO xx)
do wszystkich słowników NAMES/ISO2 zgodnie z INSTRUKCJA-NOWE-PANSTWO.md"* — zrobi
wszystkie pliki naraz.

## KROK 4 — Quiz: przypisz kraj do pul cech · 10 min

W `src/pages/country-match/quiz.astro` (ok. linii 1280–1360) są tablice-pule:
regiony, klimat, budżet itd. Nowy kraj musi trafić do właściwych pul, inaczej quiz
nigdy go nie zaproponuje. Znajdź tablice (szukaj `'malta'` jako wzoru — Malta jest
w kilku pulach) i dodaj slug tam, gdzie kraj pasuje merytorycznie.

> **Pamiętaj:** wisi też plan naprawy quizu ("naprawiamy quiz" — strefy klimatyczne,
> nowe pytanie Q9, redukcja bonusów) — jak dodajesz kilka krajów naraz, to dobry
> moment żeby zrobić oba naraz.

## KROK 5 (OPCJONALNY) — Pary compare · 15 min + ~$0.04/para

Strony `/compare/` są ręcznie kuratorowane (nie wszystkie kombinacje!):

1. W `src/pages/compare/[pair].astro` dodaj parę do tablicy `PAIRS` (ok. linii 58),
   np. `'portugal-vs-SLUG'`. Wybieraj pary, których ludzie NAPRAWDĘ szukają
   (podobne kraje, sąsiedzi, popularne alternatywy — sprawdź w GSC/Google "X vs Y").
2. Wygeneruj treść porównania:
   ```
   py scripts/generate-compare-content.py portugal-vs-SLUG
   ```

## KROK 6 — Build + weryfikacja · 10 min

```
npm run build
```

Sprawdź że powstały (w folderze `dist/`):
- `dist/countries/SLUG/index.html`
- `dist/fire/SLUG/index.html`
- flagi się wyświetlają (ISO2 poprawny), liczby wyglądają sensownie

Odpal lokalnie `npm run dev` i przeklikaj: `/countries/SLUG/`, `/fire/SLUG/`,
`/runway/` (kraj na liście?), quiz (pojawia się w wynikach przy pasujących
odpowiedziach?), homepage selector.

## KROK 7 — Publikacja · 5 min

```
git add .
git commit -m "Add [Nazwa] to all tools and pages"
git push origin main
npm run build          # jeśli deploy wymaga świeżego dist
py scripts/ping-indexnow.py
```

Na koniec: GSC → wklej URL `/countries/SLUG/` → Request Indexing (przyspiesza).

---

## CHECKLISTA SKRÓCONA (do odhaczania)

- ☐ Listy w 4 skryptach fetch (+ tax_system!)
- ☐ Pipeline: quality-scores → recompute-grades → budget → facts → quick-facts → fire-content
- ☐ Weryfikacja JSON-a (wszystkie pola są)
- ☐ NAMES/ISO2 w 9–10 plikach frontendu
- ☐ Quiz: pule cech
- ☐ (opc.) Pary compare + generate-compare-content
- ☐ Build + przeklikanie stron
- ☐ Commit + push + IndexNow + Request Indexing w GSC
