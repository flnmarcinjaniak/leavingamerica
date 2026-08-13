# Metodologia tworzenia filmów pionowych

Stan na 6 sierpnia 2026. Dokument żywy — aktualizowany po każdej większej zmianie.
Powstał po dwóch nieudanych podejściach, których błędy są opisane na końcu, żeby
ich nie powtarzać.

---

## 1. ARCHITEKTURA

Wszystko żyje w `video/`. Osobny `package.json`, żeby nie mieszać zależności
Remotion z Astro.

| Plik | Rola |
|---|---|
| `src/theme.ts` | kolory, czcionki, format (1080×1920, 30 fps) |
| `src/data.ts` | **czyta bezpośrednio `../../src/data/quality-scores.json`** |
| `src/components.tsx` | klocki tekstowe: `KineticText`, `CountUp`, `Label`, `Row` |
| `src/visuals.tsx` | klocki danych: `ScaleBars`, `CountryGrid`, `TimelineFill`, `Particles` |
| `src/Background.tsx` | zdjęcie w tle + najazd + stonowanie + przyciemnienie + podpis licencji |
| `src/<Nazwa>.tsx` | pojedynczy film, składa klocki w sekwencje |
| `src/Root.tsx` | rejestr kompozycji (id, długość w klatkach) |
| `fetch-backgrounds.mjs` | pobiera zdjęcia z Wikimedia Commons |
| `public/bg/` | pobrane zdjęcia + `credits.json` z licencjami |

**Zasada nadrzędna:** dane w filmach pochodzą z tego samego pliku co strona.
Nigdy nie wpisujemy liczb ręcznie — inaczej film i strona się rozjadą.

---

## 2. KOMENDY

```bash
cd video

npm run studio                                  # podgląd na żywo w przeglądarce
npx remotion render <id> out/<nazwa>.mp4         # render filmu
npx remotion still <id> ../shots/x.png --frame=N # pojedyncza klatka do oceny
node fetch-backgrounds.mjs                       # dociągnij nowe tła
```

**Przy pracy nad wyglądem renderuj pojedyncze klatki, nie całe filmy.**
Klatka to sekundy, film to minuty.

---

## 2a. ⭐ SYNCHRONIZACJA LEKTORA — OBOWIĄZUJĄCY STANDARD (13 sie 2026)

**To jest sposób, w jaki robimy każdy short. Bez wyjątków.**

### Zasada
**Jedna ścieżka audio na scenę, wewnątrz jej własnej `<Sequence>`.**
Nigdy jedna długa ścieżka na cały film.

### Dlaczego
Pojedyncza ścieżka rozjeżdża się z cięciami. W pierwszej wersji `visa-trap`
narracja mówiła o paszporcie, gdy na ekranie odliczało się 11,9 roku — użytkownik
od razu to wychwycił („lektor jeszcze czyta o paszporcie, a już jest kolejne
ujęcie"). Przy audio wewnątrz sekwencji rozjazd jest **fizycznie niemożliwy**.

### Procedura
1. **Napisz narrację per scena** — każde zdanie opisuje to, co widać w TEJ scenie
2. Wygeneruj osobne pliki: `<film>-1.mp3`, `<film>-2.mp3`, …
3. **Zmierz każdy** (`ffmpeg -i plik.mp3` → Duration)
4. Ustaw długość sceny = **czas mowy + ~1 sekunda** na doczytanie
5. Długość filmu licz automatycznie z sumy scen, nigdy ręcznie

```tsx
const SCENES = [
  { id: 'film-1', frames: 165 },  // 5.5s (mowa 4.6)
  { id: 'film-2', frames: 220 },  // 7.3s (mowa 6.5)
];
const START = SCENES.reduce<number[]>((acc,_s,i) => {
  acc.push(i===0 ? 0 : acc[i-1] + SCENES[i-1].frames); return acc; }, []);
export const TOTAL_FRAMES = START.at(-1)! + SCENES.at(-1)!.frames;

const Vo: React.FC<{id:string}> = ({id}) =>
  (voAvailable as string[]).includes(id)
    ? <Audio src={staticFile(`vo/${id}.mp3`)} /> : null;

<Sequence from={START[0]} durationInFrames={SCENES[0].frames}>
  <Vo id="film-1" />
  <Background src="...">…</Background>
</Sequence>
```

`TOTAL_FRAMES` eksportuj i użyj w `Root.tsx` — dwa razy zdarzyło się, że zmiana
scen nie została odzwierciedlona w ręcznie wpisanej długości i film się urywał.

### Wynikowa długość
Nie trzymaj się sztywno 16 s. `visa-trap` ma **31 s** i to jest dobre — Shorts
przyjmuje do 60 s, a widz musi zdążyć przeczytać dane. **Tempo dyktuje narracja,
nie z góry przyjęta długość.**

---

## 3. STRUKTURA FILMU — 5 UDERZEŃ

Sprawdzony układ, trzymamy się go:

| # | Rola | Klatki | Czas |
|---|---|---|---|
| 1 | **Hook** — sprzeczność w jednym zdaniu | 0–90 | 3 s |
| 2 | **Liczba** — odliczanie + wizualizacja | 90–195 | 3,5 s |
| 3 | **Zwrot** — porównanie, które boli | 195–315 | 4 s |
| 4 | **Skala** — że to nie wyjątek | 315–420 | 3,5 s |
| 5 | **CTA** — „link in bio" | 420–495 | 2,5 s |

Pamiętaj o aktualizacji `durationInFrames` w `Root.tsx` po zmianie długości.

---

## 4. ZASADY PROJEKTOWE (wypracowane, nie teoretyczne)

### 4.1 Pokazuj liczbę, nie opisuj jej
Najmocniejszy element, jaki powstał: **dwa paski w jednej skali** — 11,9 roku
wypełnia całą szerokość, 30 dni to przy nim włos. Nikt tego nie musi czytać.

Jeśli jakieś uderzenie ma tylko tekst i liczbę, jest niedokończone. Pytanie
kontrolne brzmi: **czy da się to zobaczyć zamiast przeczytać?**

Dostępne narzędzia: `ScaleBars` (porównanie), `CountryGrid` (74 kafelki,
podświetl podzbiór), `TimelineFill` (upływ czasu).

### 4.2 Tło musi coś przedstawiać
Sam gradient nie wystarcza — to była dwukrotna, słuszna reklamacja użytkownika.
Każda scena dostaje zdjęcie tematycznie związane z treścią.

Ustawienia, które działają (w `Background.tsx`):
- `brightness(1.18) contrast(1.12) saturate(0.78)` — zdjęcia z Wikimedia bywają ciemne
- przyciemnienie `dim = 0.40`, wyżej tylko gdy dużo tekstu
- najazd na przemian `in` / `out` między scenami, żeby cięcia nie nudziły
- **cień pod każdym tekstem** — bez tego biel ginie na jasnym niebie

### 4.3 Ruch bez przerwy
Tekst wjeżdża słowo po słowie (`KineticText`), liczby odliczają ze sprężynowym
wyhamowaniem (`CountUp`), zdjęcia mają najazd, w tle dryfują cząstki
(`Particles`). Nic nie stoi.

### 4.4 Pierwsze dwie sekundy
Żadnych intro, żadnego logo na starcie. Od razu sprzeczność:
*„Your $100,000 buys 12 years here. Your passport gets you 30 days."*

### 4.5 Hooki i CTA — mechanika komentarzowa (7 sie 2026)
- **Hook w drugiej osobie, zakotwiczony w pieniądzach widza** („Your $100k...",
  „How much do you make a month?"), nie w abstrakcyjnym kraju.
- **CTA = zaproszenie do komentarza z obietnicą konkretnej odpowiedzi**
  („Drop your savings number, I'll run it for you"), NIE „link in bio".
  Komentarze to najsilniejszy sygnał algorytmu, a odpowiadanie liczbami
  z datasetu to przewaga nie do skopiowania.
- Podpisy do postów + zasady obsługi komentarzy: `CAPTIONS.md`.
- Teksty lektora w `generate-voice.mjs` trzymają tę samą mechanikę.

---

## 5. ŹRÓDŁA TŁA — DECYZJA: PEXELS (7 sie 2026)

**Wybrane: Pexels API**, `fetch-media.mjs`. Klucz darmowy i natychmiastowy
(pexels.com/api), limit 200 zapytań/h i 20 tys./mies. — z zapasem.

Dlaczego nie Wikimedia (poprzednie rozwiązanie, `fetch-backgrounds.mjs`):

| | Wikimedia | Pexels |
|---|---|---|
| klipy wideo | praktycznie brak materiału podróżniczego | tysiące profesjonalnych ujęć |
| format pionowy | brak filtru | `orientation=portrait` w API |
| jakość | wrzuty wolontariuszy | stock profesjonalny |
| atrybucja | autor + licencja pod każdym plikiem | jedna linijka „footage via Pexels" |

Decydujące było wideo — na Wikimedia po prostu nie ma czego szukać.
`fetch-backgrounds.mjs` zostaje w repo jako awaryjne źródło zdjęć bez klucza.

**Konfiguracja:** `video/.env` (w .gitignore):
```
PEXELS_API_KEY=...
```

`Background.tsx` domyślnie bierze `<slot>.mp4`; `still` przełącza na `<slot>.jpg`.

---

## 6. LEKTOR

`generate-voice.mjs` — teksty narracji trzymane w tym samym pliku (`SCRIPTS`),
pisane **pod mówienie, nie pod czytanie**: krótkie zdania, liczby zapisane
słowami tak, jak człowiek je wypowiada („eleven point nine", nie „11.9").

Dwaj dostawcy, ten sam interfejs, przełącznik `VOICE_PROVIDER` w `.env`:

| | Koszt | Uwagi |
|---|---|---|
| **openai** (`gpt-4o-mini-tts`) | ~$0.015/min, czyli grosze | sterowanie tonem przez `instructions`, komercyjne OK |
| **elevenlabs** (`eleven_multilingual_v2`) | od $6/mies. | najbardziej naturalny, ale **darmowy plan zabrania użytku komercyjnego** |

⚠️ **Pułapka licencyjna:** darmowy plan ElevenLabs (10 tys. znaków) **nie
obejmuje użytku komercyjnego**. Kanał zarabiający na afiliacjach to użytek
komercyjny — potrzebny płatny plan od 6 dolarów.

Głosy amerykańskie: `ash`, `onyx` (męskie), `nova` (żeński) — ustawiasz
przez `VOICE_NAME` w `.env`.

Audio wchodzi do kompozycji przez `<Audio src={staticFile('vo/<id>.mp3')} />`
na poziomie całego filmu.

---

## 5a. TEMPO (ustalone 7 sie 2026)

Gęste sceny (paski, siatka) dostają **4,5-5 s**, proste (hook, CTA) 2,5-3 s.
Obecny visa-trap: 3 / 3,5 / 5 / 4,5 / 2,5 = 18,5 s. Zasada: **jedna myśl na
scenę** — jeśli scena ma wykres I dwie etykiety I licznik, wydłuż ją albo
coś wytnij. Lekko za szybko bywa zaletą (pętla = drugi obieg algorytmu),
ale tylko na scenach prostych, nigdy na tych z danymi.

## 5b. MUZYKA — decyzja: NIE wgrywać w plik

Podkład dodaje się **w aplikacji przy publikacji** (TikTok/Reels: dźwięki
z trendów, głośność 15-25%). Powody: (1) algorytm promuje treści używające
dźwięków z biblioteki, wgrana muzyka tego nie liczy; (2) muzyka zaszyta
w MP4 = ryzyko roszczeń praw na YouTube; (3) ten sam plik działa na
wszystkich platformach. Render zostaje niemy albo tylko z lektorem.

## 5d. NORMALIZACJA KLIPÓW — obowiązkowa po każdym pobraniu

**Zawsze uruchamiaj `node normalize-clips.mjs` po `fetch-media.mjs`.**

Objaw, gdy się tego nie zrobi: render przerywa się komunikatem
`Compositor error: No frame found at position N for source <plik>.mp4`.

Dwie przyczyny, obie usuwane jednym przebiegiem:
1. **Różne liczby klatek** — Pexels zwraca klipy 25, 29.97 i 60 fps. Scena prosząca
   o znacznik czasu, który nie trafia w istniejącą klatkę, wysypuje render.
2. **Klipy krótsze niż sceny** — sceny sięgają 12 s, klipy bywają 6-sekundowe.
   Każde żądanie poza końcem materiału kończy się tym samym błędem.

Skrypt wymusza stałe 30 fps i **zapętla każdy klip do 45 sekund**, czyli więcej
niż najdłuższa kompozycja. Po tym żadna scena nie może wyjść poza materiał.

## 5e. TŁO MUSI ZGADZAĆ SIĘ Z KRAJEM SCENY — sprawdzian mechaniczny

Reguła z 5c okazała się niewystarczająca. Przy budowie filmów 3 i 4 **sam
złamałem ją trzy razy w jednej sesji**: scena o Malezji dostała Bangkok, scena
o Hiszpanii — Lizbonę, scena o Indiach — Hanoi. Sąsiedni kraj albo region to
ten sam błąd co chorwacka flaga na Albanii.

**Sprawdzian przed renderem:** dla każdej sceny nazwanej po kraju, slot tła musi
nazywać się tak samo jak ten kraj. Jeśli slotu nie ma — **dociągnij klip**
(`fetch-media.mjs` + nowy wpis w `SLOTS`), nie podstawiaj sąsiada.

Dozwolone wyjątki: sceny nietematyczne (`money`, `map`, `cafe-laptop`,
`passport`, `airport`, `hospital`) — one nie twierdzą niczego o miejscu.

## 5c. KONTROLA MATERIAŁU Z BANKU — obowiązkowa

**TRZY WPADKI TEJ SAMEJ KLASY, wszystkie wychwycone przez użytkownika, nie przeze mnie:**
1. „passport travel document" → **paszport rosyjski** w filmie o amerykańskich wizach
2. klatka z klipu Lizbony → **druty trakcyjne** zamiast miasta
3. pula regionalna „balkans" → **zamek w Dubrowniku z chorwacką flagą** na pinach
   Albanii i Bułgarii; osobno: Litwa dostała **port w Kaliningradzie (Rosja)**,
   Panama dostała **Cartagenę (Kolumbia)**

**REGUŁY, KTÓRE Z TEGO WYNIKAJĄ:**
- **Nigdy nie grupuj krajów w pule regionalne.** Jeden kraj = jedno własne zdjęcie,
  wyszukiwane po jego własnym mieście z `quality-scores.json`.
- **Nigdy nie podstawiaj cudzego kraju jako zastępnika.** Gdy nie ma zdjęcia,
  użyj neutralnego (mapa, pieniądze, laptop) — generyk jest uczciwy, cudzy zabytek kłamie.
- **Nazwy mylące wymagają nadpisania:** Georgia (stan USA), Turkey (ptak),
  Lithuania (Kaliningrad), Panama (Cartagena). Lista w `fetch-photos.mjs`.
- **Zdjęcia, nie klatki z wideo** — klatka to przypadkowy moment, zdjęcie jest skomponowane.
- **Automatyczna kontrola:** `fetch-photos.mjs` zapisuje `photo-log.json` z opisem
  każdego zdjęcia od Pexels. Porównanie opisu z nazwą kraju wykrywa rozjazdy bez oglądania.
- **Arkusz kontrolny:** `node fetch-photos.mjs --sheet` → wszystkie tła w jednym
  obrazie do przejrzenia w 10 sekund. **Rób to przed każdą publikacją.**

⚠️ Pexels zwraca klipy "tematycznie podobne", nie "poprawne". Wpadka:
fraza "passport travel document" zwróciła **paszport ROSYJSKI** w filmie
o amerykańskich wizach — wychwycone dopiero na screenie użytkownika.
Zasada: po pobraniu klipów **obejrzyj klatkę z każdego** (remotion still)
i sprawdź: flagi, dokumenty, napisy w tle, kierownice aut. Frazy do
wyszukiwania muszą zawierać narodowość, gdy rekwizyt ją ma ("american
passport", nie "passport").

## 6. CZEGO NIE ROBIĆ — nauczone na własnych błędach

| Podejście | Dlaczego odpadło |
|---|---|
| **SVG + sharp → statyczne PNG** | wyglądało jak slajdy z prezentacji, zero ruchu |
| **PNG + ffmpeg zoompan** | ruch był, ale tło dalej puste i nic nieznaczące |
| **Okrąg imitujący pieczątkę** | wyglądał jak przypadkowa figura, mącił przekaz |
| **Ręczny montaż w CapCut** | 20 min na film, użytkownik słusznie odmówił |

**Wniosek do zapamiętania:** dwukrotnie zbudowałem dopracowaną warstwę danych
przy pustej warstwie wizualnej. Za każdym razem to użytkownik musiał to
wychwycić. Przy nowej kompozycji **najpierw pytanie, co widać w tle i co się
rusza**, dopiero potem liczby.

---

## 7. STATUS

**Gotowe:** `visa-trap` (Egipt: 11,9 roku runway vs 30 dni wizy)

**Do zrobienia** — pozostałe pięć, klocki już są, więc pójdzie szybciej:
1. `income-threshold` — $2000/mies. pokrywa 49 z 74 krajów
2. `cheap-not-livable` — tylko 13 z 74 przechodzi filtr jakości
3. `cheapest-city` — Batumi za 350 dolarów
4. `nomad-visa-gap` — tylko 35 z 74 ma wizę nomadzką
5. `vietnam-winner` — najlepszy stosunek jakości do ceny

**Podpisy do postów:** w `scripts/generate-shorts.mjs` w polu `caption`
każdego filmu (ten skrypt to poprzednia generacja, ale teksty zostają aktualne).

**Otwarte kwestie:**
- Wikimedia z podpisami czy Pexels bez? (czeka na decyzję)
- Czy dodawać lektora TTS, czy zostawić same napisy
- Klipy wideo zamiast zdjęć (Remotion obsługuje przez `<OffthreadVideo>`)
