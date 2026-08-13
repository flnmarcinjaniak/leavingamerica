import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { C, FONT_BODY } from './theme';

/* ─────────────────────────────────────────────────────────────
   Visual elements that carry meaning, not decoration.
   The point of each one is to SHOW the number, not caption it.
   ───────────────────────────────────────────────────────────── */

/** 74 tiles = the tracked countries. Highlight a subset to make a share feel physical. */
export const CountryGrid: React.FC<{
  total: number;
  highlight: number;
  color?: string;
  top?: number;
  delay?: number;
  cols?: number;
}> = ({ total, highlight, color = C.red, top = 1180, delay = 0, cols = 12 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const size = 58;
  const gap = 12;
  const rows = Math.ceil(total / cols);
  const width = cols * size + (cols - 1) * gap;

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: '50%',
        transform: 'translateX(-50%)',
        width,
        height: rows * size + (rows - 1) * gap,
      }}
    >
      {Array.from({ length: total }).map((_, i) => {
        const on = i < highlight;
        const s = spring({
          frame: frame - delay - i * 0.7,
          fps,
          config: { damping: 14, stiffness: 140, mass: 0.5 },
        });
        // highlighted tiles land later and harder, so the eye follows them
        const hit = on
          ? spring({ frame: frame - delay - 26 - i * 2.2, fps, config: { damping: 10, stiffness: 200 } })
          : 0;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: (i % cols) * (size + gap),
              top: Math.floor(i / cols) * (size + gap),
              width: size,
              height: size,
              borderRadius: 12,
              background: on
                ? `rgba(239,68,68,${0.25 + hit * 0.75})`
                : 'rgba(255,255,255,0.07)',
              border: on
                ? `2px solid rgba(239,68,68,${0.4 + hit * 0.6})`
                : '2px solid rgba(255,255,255,0.10)',
              boxShadow: on && hit > 0.5 ? `0 0 26px ${color}66` : 'none',
              opacity: s,
              transform: `scale(${0.6 + s * 0.4 + hit * 0.06})`,
            }}
          />
        );
      })}
    </div>
  );
};

/** Two bars on the same scale. This is the whole visa-trap argument in one picture. */
export const ScaleBars: React.FC<{
  a: { label: string; value: number; display: string; color: string };
  b: { label: string; value: number; display: string; color: string };
  top?: number;
  delay?: number;
}> = ({ a, b, top = 700, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const max = Math.max(a.value, b.value);

  const grow = (d: number) =>
    spring({ frame: frame - delay - d, fps, config: { damping: 200, stiffness: 34, mass: 1.2 }, durationInFrames: 40 });

  const Bar = ({ item, d }: { item: typeof a; d: number }) => {
    const g = grow(d);
    const pct = (item.value / max) * 100 * g;
    return (
      <div style={{ marginBottom: 78 }}>
        <div
          style={{
            fontFamily: FONT_BODY,
            fontSize: 38,
            color: C.gray,
            textShadow: '0 2px 14px rgba(0,0,0,0.9)',
            letterSpacing: 3,
            textTransform: 'uppercase',
            marginBottom: 18,
            opacity: g,
          }}
        >
          {item.label}
        </div>
        <div
          style={{
            height: 104,
            borderRadius: 16,
            background: 'rgba(255,255,255,0.05)',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              position: 'absolute',
              inset: 0,
              width: `${Math.max(pct, 0)}%`,
              background: `linear-gradient(90deg, ${item.color}dd, ${item.color})`,
              borderRadius: 16,
              boxShadow: `0 0 50px ${item.color}55`,
            }}
          />
          <div
            style={{
              position: 'absolute',
              left: 26,
              top: 0,
              bottom: 0,
              display: 'flex',
              alignItems: 'center',
              fontSize: 58,
              fontWeight: 900,
              color: C.white,
              opacity: g,
            }}
          >
            {item.display}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div style={{ position: 'absolute', top, left: 80, right: 80 }}>
      <Bar item={a} d={0} />
      <Bar item={b} d={22} />
    </div>
  );
};

/** Horizontal timeline that fills - reads as "time passing", good under runway numbers. */
export const TimelineFill: React.FC<{
  years: number;
  maxYears?: number;
  top?: number;
  delay?: number;
  color?: string;
}> = ({ years, maxYears = 12, top = 1180, delay = 0, color = C.cyan }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const g = spring({ frame: frame - delay, fps, config: { damping: 200, stiffness: 38, mass: 1.4 }, durationInFrames: 44 });
  const ticks = Math.round(maxYears);

  return (
    <div style={{ position: 'absolute', top, left: 90, right: 90 }}>
      <div
        style={{
          height: 22,
          borderRadius: 11,
          background: 'rgba(255,255,255,0.07)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            position: 'absolute',
            inset: 0,
            width: `${(years / maxYears) * 100 * g}%`,
            background: `linear-gradient(90deg, ${color}aa, ${color})`,
            boxShadow: `0 0 34px ${color}77`,
          }}
        />
      </div>
      <div style={{ position: 'relative', height: 46, marginTop: 12 }}>
        {Array.from({ length: ticks + 1 }).map((_, i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${(i / ticks) * 100}%`,
              transform: 'translateX(-50%)',
              fontFamily: FONT_BODY,
              fontSize: 24,
              color: i % 2 === 0 ? C.dim : 'transparent',
              opacity: g,
            }}
          >
            {i}
          </div>
        ))}
      </div>
    </div>
  );
};

/** Drifting particle field - background texture so the frame is never truly still. */
export const Particles: React.FC<{ count?: number }> = ({ count = 34 }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ position: 'absolute', inset: 0, overflow: 'hidden' }}>
      {Array.from({ length: count }).map((_, i) => {
        const seed = (i * 9301 + 49297) % 233280;
        const x = (seed / 233280) * 100;
        const speed = 0.22 + ((i % 5) * 0.09);
        const y = ((i * 137) % 1920) - frame * speed;
        const wrapped = ((y % 2100) + 2100) % 2100 - 90;
        const size = 2 + (i % 3);
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${x}%`,
              top: wrapped,
              width: size,
              height: size,
              borderRadius: '50%',
              background: 'rgba(148,197,255,0.30)',
            }}
          />
        );
      })}
    </div>
  );
};

/** Passport-stamp style ring that snaps in - visual punctuation for the "visa" beat. */
export const StampRing: React.FC<{ delay?: number; top?: number; size?: number }> = ({
  delay = 0,
  top = 980,
  size = 560,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 9, stiffness: 150 } });
  const rot = interpolate(s, [0, 1], [-16, -7]);

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: '50%',
        width: size,
        height: size,
        marginLeft: -size / 2,
        border: `10px solid rgba(239,68,68,${0.30 * s})`,
        borderRadius: '50%',
        transform: `translateY(-50%) rotate(${rot}deg) scale(${0.7 + s * 0.3})`,
        opacity: s,
      }}
    />
  );
};
