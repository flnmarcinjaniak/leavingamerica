import React from 'react';
import { AbsoluteFill, Img, staticFile } from 'remotion';
import { C, FONT, FONT_BODY } from '../theme';

/* ─────────────────────────────────────────────────────────────
   Pinterest pins: 1000x1500 (2:3).
   Hard constraint that drives every decision below: the pin is
   first seen as a 236x354 thumbnail. If the headline and the
   number are not readable at ~24% scale, the pin does not exist.
   So: few words, enormous type, brutal contrast.
   ───────────────────────────────────────────────────────────── */

export const PW = 1000;
export const PH = 1500;

const Shell: React.FC<{
  bg?: string;
  dim?: number;
  children: React.ReactNode;
}> = ({ bg, dim = 0.62, children }) => (
  <AbsoluteFill style={{ backgroundColor: C.bg1, fontFamily: FONT, overflow: 'hidden' }}>
    {bg && (
      <>
        <Img
          src={staticFile(`bg/${bg}.jpg`)}
          style={{
            width: '100%', height: '100%', objectFit: 'cover',
            filter: 'saturate(0.8) contrast(1.08) brightness(1.02)',
          }}
        />
        <AbsoluteFill
          style={{
            background: `linear-gradient(180deg, rgba(6,12,24,${dim + 0.22}) 0%, rgba(6,12,24,${dim - 0.14}) 38%, rgba(6,12,24,${dim + 0.30}) 100%)`,
          }}
        />
      </>
    )}
    {!bg && (
      <AbsoluteFill style={{ background: `linear-gradient(165deg, ${C.bg1} 0%, ${C.bg2} 100%)` }} />
    )}
    {children}
    <Brand />
  </AbsoluteFill>
);

/* Persistent brand bar. Recognition across a 250-pin library is what turns
   one good pin into a follower, so it never moves and never changes. */
const Brand: React.FC = () => (
  <div
    style={{
      position: 'absolute', left: 0, right: 0, bottom: 0, height: 96,
      background: 'rgba(6,12,24,0.88)',
      borderTop: `4px solid ${C.cyan}`,
      display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 14,
    }}
  >
    <span style={{ fontFamily: FONT_BODY, fontSize: 34, color: '#fff', fontWeight: 700, letterSpacing: 0.5 }}>
      leavingamerica.co
    </span>
    <span style={{ fontFamily: FONT_BODY, fontSize: 26, color: C.cyan }}>· free tools</span>
  </div>
);

const Eyebrow: React.FC<{ text: string; color?: string }> = ({ text, color = C.cyan }) => (
  <div
    style={{
      display: 'inline-block',
      background: color,
      color: '#06263d',
      fontFamily: FONT_BODY,
      fontSize: 30,
      fontWeight: 900,
      letterSpacing: 3,
      textTransform: 'uppercase',
      padding: '12px 24px',
      borderRadius: 8,
    }}
  >
    {text}
  </div>
);

const Headline: React.FC<{ text: string; size?: number }> = ({ text, size = 82 }) => (
  <div
    style={{
      fontSize: size,
      fontWeight: 900,
      color: '#fff',
      lineHeight: 1.08,
      letterSpacing: -1.5,
      textShadow: '0 6px 30px rgba(0,0,0,0.85)',
      marginTop: 26,
    }}
  >
    {text}
  </div>
);

/** The single number that must survive thumbnail scale. */
const HeroNumber: React.FC<{
  value: string;
  caption: string;
  color?: string;
}> = ({ value, caption, color = C.cyan }) => (
  <div style={{ marginTop: 'auto', marginBottom: 34 }}>
    <div
      style={{
        fontSize: 190,
        fontWeight: 900,
        color,
        lineHeight: 0.92,
        letterSpacing: -8,
        textShadow: `0 0 80px ${color}55, 0 8px 34px rgba(0,0,0,0.7)`,
      }}
    >
      {value}
    </div>
    <div
      style={{
        fontFamily: FONT_BODY,
        fontSize: 38,
        color: '#E2E8F0',
        letterSpacing: 2,
        textTransform: 'uppercase',
        marginTop: 10,
        textShadow: '0 3px 16px rgba(0,0,0,0.9)',
      }}
    >
      {caption}
    </div>
  </div>
);

const Pad: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div
    style={{
      position: 'absolute', inset: 0, padding: '70px 62px 130px',
      display: 'flex', flexDirection: 'column',
    }}
  >
    {children}
  </div>
);

/* ── 1. COUNTRY: the workhorse, one per tracked country ── */
export type CountryPinProps = {
  name: string; bg?: string;
  monthly: number; years: number;
  health: number; safety: number;
  visa: number | null; nomad: boolean;
};

export const CountryPin: React.FC<CountryPinProps> = ({
  name, bg, monthly, years, health, safety, visa, nomad,
}) => (
  <Shell bg={bg}>
    <Pad>
      <div><Eyebrow text="cost of living" /></div>
      <Headline text={`Retire in ${name}`} size={name.length > 12 ? 74 : 88} />
      <HeroNumber value={`$${monthly.toLocaleString()}`} caption="per month, one person" />

      <div style={{ display: 'flex', gap: 12, marginBottom: 8 }}>
        {[
          { k: 'Runway on $100k', v: `${years} yrs` },
          { k: 'Healthcare', v: `${health}/10` },
          { k: 'Safety', v: `${safety}/10` },
        ].map(s => (
          <div
            key={s.k}
            style={{
              flex: 1,
              background: 'rgba(255,255,255,0.10)',
              border: '1px solid rgba(255,255,255,0.20)',
              borderRadius: 14,
              padding: '16px 12px',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: 40, fontWeight: 900, color: '#fff' }}>{s.v}</div>
            <div style={{ fontFamily: FONT_BODY, fontSize: 20, color: '#CBD5E1', marginTop: 4 }}>{s.k}</div>
          </div>
        ))}
      </div>

      <div style={{ fontFamily: FONT_BODY, fontSize: 26, color: '#CBD5E1' }}>
        {visa === null ? 'Visa data on site' : `${visa} days visa-free`}
        {nomad ? ' · digital nomad visa available' : ' · no nomad visa'}
      </div>
    </Pad>
  </Shell>
);

/* ── 2. CITY: city-level numbers beat country averages, and nobody publishes them ── */
export type CityPinProps = { city: string; country: string; bg?: string; monthly: number; years: number };

export const CityPin: React.FC<CityPinProps> = ({ city, country, bg, monthly, years }) => (
  <Shell bg={bg}>
    <Pad>
      <div><Eyebrow text="city cost" color={C.green} /></div>
      <Headline text={`Live in ${city}`} size={city.length > 11 ? 74 : 88} />
      <div style={{ fontFamily: FONT_BODY, fontSize: 34, color: '#E2E8F0', marginTop: 8 }}>{country}</div>
      <HeroNumber value={`$${monthly.toLocaleString()}`} caption="per month, all in" color={C.green} />
      <div
        style={{
          background: 'rgba(255,255,255,0.10)',
          border: '1px solid rgba(255,255,255,0.20)',
          borderRadius: 14, padding: '20px 22px',
        }}
      >
        <div style={{ fontSize: 42, fontWeight: 900, color: '#fff' }}>{years} years</div>
        <div style={{ fontFamily: FONT_BODY, fontSize: 24, color: '#CBD5E1', marginTop: 4 }}>
          that is how long $100,000 lasts here
        </div>
      </div>
    </Pad>
  </Shell>
);

/* ── 3. LIST: the format Pinterest rewards most - saveable reference ── */
export type ListPinProps = {
  eyebrow: string; title: string; bg?: string;
  rows: { left: string; right: string }[];
  accent?: string;
  /** What the right-hand number MEANS. Without it "9.3 yrs" is unreadable. */
  metric?: string;
};

export const ListPin: React.FC<ListPinProps> = ({ eyebrow, title, bg, rows, accent = C.cyan, metric }) => (
  <Shell bg={bg} dim={0.74}>
    <Pad>
      <div><Eyebrow text={eyebrow} color={accent} /></div>
      <Headline text={title} size={title.length > 30 ? 62 : 74} />
      {metric && (
        <div
          style={{
            marginTop: 16, fontSize: 30, fontWeight: 700, letterSpacing: 1.5,
            color: 'rgba(255,255,255,0.82)', textTransform: 'uppercase',
            textShadow: '0 2px 12px rgba(0,0,0,0.9)',
          }}
        >
          {metric}
        </div>
      )}
      <div style={{ marginTop: 26, display: 'flex', flexDirection: 'column', gap: 12 }}>
        {rows.map((r, i) => (
          <div
            key={i}
            style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              background: i % 2 ? 'rgba(255,255,255,0.06)' : 'rgba(255,255,255,0.12)',
              borderLeft: `6px solid ${accent}`,
              borderRadius: 10, padding: '18px 22px',
            }}
          >
            <span style={{ fontSize: 40, fontWeight: 900, color: '#fff' }}>{r.left}</span>
            <span style={{ fontSize: 40, fontWeight: 900, color: accent }}>{r.right}</span>
          </div>
        ))}
      </div>
    </Pad>
  </Shell>
);

/* ── 4. CONTRAST: the visa trap and US-vs-abroad comparisons ── */
export type ContrastPinProps = {
  eyebrow: string; title: string; bg?: string;
  a: { label: string; value: string };
  b: { label: string; value: string };
  note?: string;
};

export const ContrastPin: React.FC<ContrastPinProps> = ({ eyebrow, title, bg, a, b, note }) => (
  <Shell bg={bg} dim={0.70}>
    <Pad>
      <div><Eyebrow text={eyebrow} color={C.red} /></div>
      <Headline text={title} size={title.length > 26 ? 66 : 78} />

      <div style={{ marginTop: 'auto', marginBottom: 30 }}>
        {[{ ...a, c: C.cyan }, { ...b, c: C.red }].map((x, i) => (
          <div key={i} style={{ marginBottom: i === 0 ? 26 : 0 }}>
            <div
              style={{
                fontFamily: FONT_BODY, fontSize: 30, color: '#E2E8F0',
                letterSpacing: 2, textTransform: 'uppercase', marginBottom: 6,
              }}
            >
              {x.label}
            </div>
            <div
              style={{
                fontSize: 128, fontWeight: 900, color: x.c, lineHeight: 1,
                letterSpacing: -5, textShadow: `0 0 70px ${x.c}44, 0 6px 26px rgba(0,0,0,0.7)`,
              }}
            >
              {x.value}
            </div>
          </div>
        ))}
        {note && (
          <div style={{ fontFamily: FONT_BODY, fontSize: 27, color: '#CBD5E1', marginTop: 22 }}>
            {note}
          </div>
        )}
      </div>
    </Pad>
  </Shell>
);
