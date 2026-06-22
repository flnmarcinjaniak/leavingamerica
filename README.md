LEAVINGAMERICA.CO — HARMONOGRAM AKTUALIZACJI DANYCH
CO MIESIĄC (np. 1. dzień miesiąca):
→ python scripts/fetch-quality-scores.py
→ python scripts/recompute-grades.py

Dane które się zmieniają: safety (GPI), 
healthcare (UHC), happiness, HDI, pollution, 
traffic, unemployment, internet, English, 
visa, tax, nomad visa, oceny ogólne

Jeśli fetch-quality-scores.py wywali się na 
Wikipedii (403) — restart modemu, potem:
→ python scripts/fetch-english-proficiency-only.py
→ python scripts/recompute-grades.py
CO 3 MIESIĄCE (raz na kwartał):
→ python scripts/fetch-monthly-budget.py

Dane: budget_single, budget_couple, cost_index, 
us_comparison (WhereNext — koszty życia nie 
zmieniają się szybko)
RAZ NA PÓŁ ROKU / RZADKO:
→ python scripts/fetch-country-facts.py

Dane: population, area, capital, languages, 
borders, itd. (REST Countries — to praktycznie 
się nie zmienia)
TYLKO PRZY DODAWANIU NOWYCH KRAJÓW:
→ python scripts/generate-quick-facts.py

Generuje akapit "WHAT X IS ACTUALLY LIKE" — 
kosztuje kredyty API, uruchamiaj tylko dla 
nowych krajów, nie całej listy 55 (chyba że 
chcesz odświeżyć styl pisania)
PO KAŻDEJ AKTUALIZACJI:
Sprawdź wizualnie 2-3 strony krajów 
(np. /countries/portugal, /countries/kenya) — 
upewnij się że Quick Facts paragraph, budget 
data i Getting Around section nadal się 
wyświetlają (to był realny incydent utraty 
danych w czerwcu 2026, sprawdzaj zawsze).
PRZYPOMNIENIE: jeśli zapomnisz kolejności albo 
szczegółów technicznych — zajrzyj do 
scripts/README.md w repo, tam jest pełna 
dokumentacja każdego skryptu.