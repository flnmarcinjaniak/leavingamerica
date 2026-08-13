# Brief: generator shortów wideo z danych

Samodzielny opis pipeline'u do produkcji pionowych filmów (TikTok / Reels /
YouTube Shorts) z danych, z lektorem i animacjami — **jedną komendą, bez
edytora wideo**.

Wklej ten plik w nowy czat jako kontekst. Zawiera stack, architekturę, wzorce
kodu i — najważniejsze — **listę błędów, które już popełniliśmy**, żeby nie
powtarzać ich od zera.

---

## 1. STACK

| Warstwa | Narzędzie | Koszt |
|---|---|---|
| Silnik wideo | **Remotion** (React → MP4) | darmowy dla osób prywatnych i firm do 3 osób |
| Materiał wideo/foto | **Pexels API** | darmowy klucz, natychmiastowy |
| Lektor | **OpenAI `gpt-4o-mini-tts`** | ~$0.015/min, czyli grosze za film |
| Runtime | Node.js 20+ | — |

**Dlaczego Remotion, a nie generatory AI:** kontrola nad każdą klatką, prawdziwe
animacje (sprężyny, easing, odliczanie liczb), podgląd na żywo w przeglądarce,
dane wprost z pliku projektu. Generatory typu Pictory dają generyczne slajdy,
które widz rozpoznaje i przewija.

**Dlaczego nie ElevenLabs:** ich **darmowy plan zabrania użytku komercyjnego**.
Kanał zarabiający na czymkolwiek to użytek komercyjny. Płatny start od $6/mies.
OpenAI kosztuje ułamek tego i licencja jest czysta.

---

## 2. INSTALACJA OD ZERA

```bash
mkdir video && cd video
npm init -y
npm install remotion @remotion/cli @remotion/bundler @remotion/renderer react react-dom
npm install -D @types/react typescript
```

`package.json` → dodaj:
```json
"scripts": {
  "studio": "remotion studio",
  "render": "remotion render"
}
```

`remotion.config.ts`:
```ts
import { Config } from '@remotion/cli/config';
Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setEntryPoint('src/index.ts');
```

`.env` (dodaj do `.gitignore`):
```
PEXELS_API_KEY=...
OPENAI_API_KEY=sk-...
VOICE_NAME=ash
```

---

## 3. STRUKTURA PLIKÓW

```
video/
├── package.json
├── remotion.config.ts
├── .env                    # klucze API (gitignore)
├── fetch-media.mjs         # pobiera klipy z Pexels
├── generate-voice.mjs      # generuje lektora (TTS)
├── public/
│   ├── bg/                 # pobrane klipy .mp4
│   └── vo/                 # wygenerowane .mp3 + available.json
└── src/
    ├── index.ts            # registerRoot
    ├── Root.tsx            # rejestr kompozycji
    ├── theme.ts            # kolory, czcionki, format
    ├── data.ts             # czyta dane projektu
    ├── components.tsx      # klocki tekstowe
    ├── visuals.tsx         # klocki danych (wykresy)
    ├── Background.tsx      # wideo + stonowanie + przyciemnienie
    └── <NazwaFilmu>.tsx    # pojedynczy film
```

**Zasada:** dane w filmach czytane z tego samego pliku co reszta projektu.
Nigdy nie wpisuj liczb ręcznie — film rozjedzie się ze źródłem.

---

## 4. KLUCZOWE KOMPONENTY

### theme.ts
```ts
export const C = {
  bg1: '#0B1220', bg2: '#12243F',
  white: '#FFFFFF', cyan: '#22D3EE', red: '#EF4444', green: '#34D399',
  gray: '#E2E8F0',   // JASNY — ciemny szary ginie na wideo
  dim: '#B6C2D4',
} as const;
export const FONT = '"Arial Black", "Segoe UI", system-ui, sans-serif';
export const FONT_BODY = 'Arial, "Segoe UI", system-ui, sans-serif';
export const FPS = 30, W = 1080, H = 1920;
```

### Background.tsx — wideo w tle
```tsx
import { AbsoluteFill, OffthreadVideo, interpolate, staticFile, useCurrentFrame } from 'remotion';

export const Background: React.FC<{src?: string; dim?: number; children: React.ReactNode}> =
({ src, dim = 0.34, children }) => {
  const frame = useCurrentFrame();
  // jedno stonowanie dla wszystkich ujęć = spójna seria
  const grade = 'saturate(0.74) contrast(1.10) brightness(1.06)';
  return (
    <AbsoluteFill style={{ backgroundColor: C.bg1, overflow: 'hidden', fontFamily: FONT }}>
      {src && (
        <>
          <OffthreadVideo src={staticFile(`bg/${src}.mp4`)} muted
            style={{ width:'100%', height:'100%', objectFit:'cover', filter: grade,
              transform: `scale(${interpolate(frame,[0,130],[1.03,1.10],{extrapolateRight:'clamp'})})` }} />
          {/* tint marki */}
          <AbsoluteFill style={{ background:`linear-gradient(180deg,${C.bg1}99,${C.bg2}3a 45%,${C.bg1}b0)`,
            mixBlendMode:'multiply' }} />
          {/* przyciemnienie pod tekst */}
          <AbsoluteFill style={{ background:
            `radial-gradient(ellipse at 50% 46%, rgba(6,12,24,${dim*0.38}), rgba(6,12,24,${dim}) 58%, rgba(6,12,24,${Math.min(dim+0.22,0.78)}))` }} />
        </>
      )}
      {children}
    </AbsoluteFill>
  );
};
```

### components.tsx — tekst wjeżdżający słowo po słowie
```tsx
export const KineticText: React.FC<{text:string; size?:number; color?:string; delay?:number; top?:number}> =
({ text, size=96, color=C.white, delay=0, top=620 }) => {
  const frame = useCurrentFrame(); const { fps } = useVideoConfig();
  return (
    <div style={{position:'absolute',top,left:70,right:70,display:'flex',
      flexWrap:'wrap',justifyContent:'center',gap:'0 18px'}}>
      {text.split(' ').map((w,i) => {
        const s = spring({ frame: frame-delay-i*2.5, fps,
          config:{damping:14,stiffness:120,mass:0.6} });
        return <span key={i} style={{fontSize:size,fontWeight:900,color,lineHeight:1.14,
          opacity:s, transform:`translateY(${(1-s)*42}px)`, display:'inline-block',
          textShadow:'0 4px 28px rgba(0,0,0,0.75), 0 1px 4px rgba(0,0,0,0.6)'}}>{w}</span>;
      })}
    </div>
  );
};
```

### components.tsx — liczba, która odlicza
```tsx
export const CountUp: React.FC<{value:number; decimals?:number; size?:number;
  color?:string; top?:number; delay?:number}> =
({ value, decimals=0, size=250, color=C.cyan, top=780, delay=0 }) => {
  const frame = useCurrentFrame(); const { fps } = useVideoConfig();
  const progress = spring({ frame: frame-delay, fps,
    config:{damping:200,stiffness:42,mass:1.6}, durationInFrames:42 });
  // lekkie "pyknięcie" w momencie wyladowania
  const pop = spring({ frame: frame-delay-40, fps, config:{damping:9,stiffness:180} });
  const scale = 1 + pop*0.045*Math.max(0, 1-(frame-delay-46)/18);
  return (
    <div style={{position:'absolute',top,left:0,right:0,textAlign:'center',
      fontSize:size,fontWeight:900,color,letterSpacing:-4,
      transform:`scale(${Math.max(1,scale)})`,
      textShadow:`0 0 70px ${color}66, 0 5px 30px rgba(0,0,0,0.7)`}}>
      {(value*progress).toFixed(decimals)}
    </div>
  );
};
```

### visuals.tsx — NAJWAŻNIEJSZY klocek: dwa paski w jednej skali
To był przełom w całym projekcie. Zamiast pisać „11,9 roku kontra 30 dni",
pokazujesz **pełny pasek obok włosa**. Argument bez czytania.

```tsx
export const ScaleBars: React.FC<{
  a:{label:string; value:number; display:string; color:string};
  b:{label:string; value:number; display:string; color:string};
  top?:number; delay?:number;
}> = ({ a, b, top=700, delay=0 }) => {
  const frame = useCurrentFrame(); const { fps } = useVideoConfig();
  const max = Math.max(a.value, b.value);
  const grow = (d:number) => spring({ frame: frame-delay-d, fps,
    config:{damping:200,stiffness:34,mass:1.2}, durationInFrames:40 });
  const Bar = ({item,d}:{item:typeof a; d:number}) => {
    const g = grow(d);
    return (
      <div style={{marginBottom:78}}>
        <div style={{fontFamily:FONT_BODY,fontSize:38,color:C.gray,letterSpacing:3,
          textTransform:'uppercase',marginBottom:18,opacity:g,
          textShadow:'0 2px 14px rgba(0,0,0,0.9)'}}>{item.label}</div>
        <div style={{height:104,borderRadius:16,background:'rgba(255,255,255,0.05)',
          position:'relative',overflow:'hidden'}}>
          <div style={{position:'absolute',inset:0,width:`${(item.value/max)*100*g}%`,
            background:`linear-gradient(90deg,${item.color}dd,${item.color})`,
            borderRadius:16, boxShadow:`0 0 50px ${item.color}55`}} />
          <div style={{position:'absolute',left:26,top:0,bottom:0,display:'flex',
            alignItems:'center',fontSize:58,fontWeight:900,color:C.white,opacity:g}}>
            {item.display}
          </div>
        </div>
      </div>
    );
  };
  return <div style={{position:'absolute',top,left:80,right:80}}>
    <Bar item={a} d={0} /><Bar item={b} d={22} />
  </div>;
};
```

Pozostałe przydatne klocki: **siatka kafelków** (np. 74 kwadraty, 10 zapala się
na czerwono — pokazuje skalę zjawiska), **pasek postępu czasu**, **dryfujące
cząstki** w tle.

---

## 5. STRUKTURA FILMU — 5 UDERZEŃ

| # | Rola | Czas | Uwagi |
|---|---|---|---|
| 1 | **Hook** — sprzeczność w jednym zdaniu | 3 s | druga osoba, liczba widza |
| 2 | **Liczba** — odliczanie + wizualizacja | 3,5 s | |
| 3 | **Zwrot** — porównanie, które boli | **5 s** | najgęstsza scena |
| 4 | **Skala** — że to nie wyjątek | **4,5 s** | |
| 5 | **CTA** — konkretne narzędzie | 3 s | |

Razem ~19 s. Sceny gęste dostają 4,5-5 s, proste 3 s.
**Jedna myśl na scenę.**

```tsx
<Sequence durationInFrames={90}>...</Sequence>
<Sequence from={90} durationInFrames={105}>...</Sequence>
```
Pamiętaj o aktualizacji `durationInFrames` w `Root.tsx`.

---

## 6. POBIERANIE MATERIAŁU (Pexels)

```js
const res = await fetch('https://api.pexels.com/videos/search?' + new URLSearchParams({
  query: term, orientation: 'portrait', size: 'medium', per_page: '10'
}), { headers: { Authorization: KEY } });

// klipy 5-30 s, wybierz najwiekszy pionowy plik >= 1080 szerokosci
const vid = res.videos.filter(v => v.duration >= 5 && v.duration <= 30)
  .sort((a,b) => b.width*b.height - a.width*a.height)[0];
```

⚠️ **Definiuj 2-3 frazy zapasowe na slot** — pierwsza często nic nie zwraca.

### ⚠️ OBOWIĄZKOWY KROK PO POBRANIU: normalizacja

Bez tego render przerwie się komunikatem
`Compositor error: No frame found at position N`.

```js
// normalize-clips.mjs — uruchamiaj po KAZDYM fetch-media.mjs
await run(ffmpeg.path, [
  '-stream_loop', '-1',      // zapetl zrodlo...
  '-i', src,
  '-t', '45',                // ...i utnij na stalej dlugosci
  '-r', '30', '-vsync', 'cfr',   // wymus stale 30 fps
  '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
  '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart',
  '-y', tmp,
]);
```

Dwa problemy usuwane naraz: klipy z banku mają 25/29.97/60 fps (scena prosi
o znacznik czasu, który nie trafia w klatkę), a bywają krótsze niż scena
(żądanie poza końcem materiału). Zapętlenie do 45 s eliminuje oba.

---

## 7. LEKTOR (OpenAI TTS)

```js
const r = await fetch('https://api.openai.com/v1/audio/speech', {
  method:'POST',
  headers:{ Authorization:`Bearer ${KEY}`, 'Content-Type':'application/json' },
  body: JSON.stringify({
    model: 'gpt-4o-mini-tts',
    voice: 'ash',            // ash/onyx = męski US, nova = żeński US
    input: text,
    instructions: 'Speak as a calm, confident American narrator. Conversational, not newsreader. Slight emphasis on the numbers. Natural pauses between sentences.',
    response_format: 'mp3',
  }),
});
```

**Teksty pisz POD MÓWIENIE, nie pod czytanie:**
- krótkie zdania
- liczby słowami tak, jak człowiek je wypowiada: `eleven point nine`, nie `11.9`
- `instructions` realnie steruje tonem — używaj

### ⭐ NAJWAŻNIEJSZE: jedna ścieżka NA SCENĘ, nie na film

To jest jedyny sposób, w jaki dźwięk nie rozjedzie się z obrazem.

**Nie rób tego:**
```tsx
<AbsoluteFill>
  <Audio src={staticFile('vo/film.mp3')} />   {/* ❌ rozjedzie sie z cieciami */}
  <Sequence>…</Sequence>
</AbsoluteFill>
```

**Rób tak:**
```tsx
const SCENES = [
  { id: 'film-1', frames: 165 },  // 5.5s (mowa 4.6)
  { id: 'film-2', frames: 220 },  // 7.3s (mowa 6.5)
  { id: 'film-3', frames: 250 },  // 8.3s (mowa 7.3)
];
const START = SCENES.reduce<number[]>((acc,_s,i) => {
  acc.push(i===0 ? 0 : acc[i-1] + SCENES[i-1].frames); return acc; }, []);
export const TOTAL_FRAMES = START.at(-1)! + SCENES.at(-1)!.frames;

<Sequence from={START[0]} durationInFrames={SCENES[0].frames}>
  <Audio src={staticFile('vo/film-1.mp3')} />
  <Background src="...">…</Background>
</Sequence>
```

**Procedura:**
1. Narracja pisana **per scena** — zdanie opisuje to, co widać w TEJ scenie
2. Osobne pliki `<film>-1.mp3`, `<film>-2.mp3`, …
3. Zmierz każdy: `ffmpeg -i plik.mp3` → Duration
4. Długość sceny = **czas mowy + ~1 s** na doczytanie
5. `TOTAL_FRAMES` licz z sumy scen i eksportuj do `Root.tsx`

**Objaw, gdy się tego nie zrobi:** narracja mówi o jednej rzeczy, a na ekranie
jest już następna. Wyłapane w produkcji: lektor czytał o paszporcie, gdy
odliczała się liczba lat.

**Długość filmu wynika z narracji, nie odwrotnie.** 30 s jest w porządku —
Shorts przyjmuje 60 s, a widz musi zdążyć przeczytać dane.

**Zrób lektora opcjonalnym**, żeby render nie wywalał się przy braku pliku:
```tsx
import available from '../public/vo/available.json';
{(available as string[]).includes('nazwa') && <Audio src={staticFile('vo/nazwa.mp3')} />}
```

---

## 8. KOMENDY

```bash
node fetch-media.mjs                              # pobierz klipy
node generate-voice.mjs                           # wygeneruj lektora
npm run studio                                    # podglad na zywo
npx remotion still <id> out/x.png --frame=250     # POJEDYNCZA KLATKA do oceny
npx remotion render <id> out/film.mp4             # render
```

⚠️ **Przy pracy nad wyglądem renderuj pojedyncze klatki, nie filmy.**
Klatka to sekundy, film to minuty.

---

## 9. ZASADY PROJEKTOWE (wypracowane, nie teoretyczne)

**9.1 Pokazuj liczbę, nie opisuj jej.**
Pytanie kontrolne dla każdej sceny: *czy tę liczbę da się ZOBACZYĆ zamiast
przeczytać?* Jeśli scena ma tylko tekst i cyfrę — jest niedokończona.

**9.2 Tło musi coś przedstawiać.**
Sam gradient nie wystarcza. Każda scena dostaje klip tematycznie związany
z treścią. To była **dwukrotna reklamacja użytkownika** — nie skracaj tego kroku.

**9.3 Ruch bez przerwy.**
Tekst wjeżdża słowo po słowie, liczby odliczają, klip ma najazd, w tle dryfują
cząstki. Nic nie stoi.

**9.4 Cień pod każdym tekstem.**
Biel ginie na jasnym niebie. Bez wyjątków.

**9.5 Jasne szarości.**
`#94A3B8` jest nieczytelny na wideo. Używaj `#E2E8F0`.

**9.6 Hook w drugiej osobie, zakotwiczony w widzu.**
„Your $100,000 buys 12 years here", nie „Egypt offers 12 years".

**9.7 CTA na narzędzie, nie na komentarze.**
Jeśli obiecasz odpowiedź w komentarzu, widz dostanie ją za darmo i nie kliknie.
Kieruj na kalkulator / stronę — coś, czego nie da się oddać w komentarzu.

**9.8 Muzyki NIE wgrywaj w plik.**
Dodajesz dźwięk z trendów w aplikacji przy publikacji. Powody: algorytm
premiuje dźwięki z biblioteki, wgrana muzyka to ryzyko roszczeń na YouTube,
a jeden niemy plik działa na wszystkich platformach.

**9.9 Pierwsze dwie sekundy.**
Żadnych intro, żadnego logo na starcie. Od razu sprzeczność.

---

## 10. BŁĘDY, KTÓRE JUŻ POPEŁNILIŚMY

| Błąd | Skutek | Zapobieganie |
|---|---|---|
| **Materiał z banku bez kontroli** | „passport" zwrócił **paszport rosyjski** w filmie o amerykańskich wizach | Fraza musi zawierać narodowość: `american passport`. Obejrzyj klatkę z każdego klipu |
| **Pule regionalne zamiast osobnych ujęć** | zamek chorwacki z flagą na materiale o Albanii i Bułgarii | Jeden temat = jedno własne ujęcie. Nigdy nie podstawiaj cudzego kraju |
| **Nazwy mylące wyszukiwarkę** | „Georgia" → stan USA, „Turkey" → ptak, „Lithuania" → Kaliningrad | Lista nadpisań z konkretnym zabytkiem |
| **Tytuł obiecuje więcej niż widać** | tytuł „13 krajów", na obrazku 6 | Tytuł musi opisywać to, co widać. Liczba szersza idzie do opisu |
| **Statyczne slajdy** (pierwsze podejście: SVG+sharp) | wyglądało jak prezentacja korporacyjna | Remotion od początku |
| **Utrata `fontFamily` przy podmianie komponentu tła** | czcionka przeskoczyła na szeryfową | `fontFamily` ustawiaj na najwyższym kontenerze |
| **Zbyt ciemne przyciemnienie** | zdjęcie zatopione, tło nic nie wnosi | `dim` 0.34-0.44, jaśniej niż intuicja podpowiada |
| **Kopiowanie ozdobników** | okrąg imitujący pieczątkę wyglądał jak przypadkowa figura | Każdy element musi coś znaczyć albo wylatuje |

---

## 11. WERYFIKACJA PRZED PUBLIKACJĄ

- [ ] Obejrzana klatka z **każdego** klipu tła — flagi, dokumenty, napisy, kierownice
- [ ] Tytuł/napisy zgodne z tym, co widać
- [ ] Wszystkie liczby zgodne ze źródłem danych
- [ ] Tekst czytelny na najjaśniejszej klatce każdej sceny
- [ ] Sceny z danymi trwają 4,5 s+
- [ ] Zero myślników i klisz językowych w napisach
- [ ] Render 1080×1920, 30 fps

---

## 12. PROMPT DO NOWEGO CZATU

> Zbuduj mi generator pionowych shortów w Remotion według załączonego briefu.
> Temat: **[TWÓJ TEMAT]**. Dane wejściowe: **[plik/źródło]**.
> Chcę pipeline, w którym jedna komenda generuje gotowy MP4 z klipami z Pexels,
> lektorem OpenAI i animowanymi wizualizacjami danych.
> Trzymaj się struktury 5 uderzeń i zasad projektowych z sekcji 9.
> Zacznij od jednego filmu, pokaż mi pojedyncze klatki do oceny przed renderem
> całości.
