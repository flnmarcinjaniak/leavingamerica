import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { C, FONT, FONT_BODY } from './theme';

/* ── background: subtle animated gradient so the frame is never dead ── */
export const Backdrop: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const drift = interpolate(frame, [0, 450], [0, 8], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(${170 + drift}deg, ${C.bg1} 0%, ${C.bg2} 100%)`,
        fontFamily: FONT,
      }}
    >
      {/* soft glow that breathes */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at 50% ${38 + drift / 2}%, rgba(34,211,238,0.10), transparent 62%)`,
        }}
      />
      {children}
      <Badge />
    </AbsoluteFill>
  );
};

const Badge: React.FC = () => (
  <div
    style={{
      position: 'absolute',
      bottom: 96,
      left: 0,
      right: 0,
      textAlign: 'center',
      fontFamily: FONT_BODY,
      fontSize: 34,
      color: 'rgba(255,255,255,0.42)',
      letterSpacing: 1,
    }}
  >
    leavingamerica.co
  </div>
);

/* ── words fly in one by one, the single biggest "made by a human" signal ── */
export const KineticText: React.FC<{
  text: string;
  size?: number;
  color?: string;
  delay?: number;
  top?: number;
}> = ({ text, size = 96, color = C.white, delay = 0, top = 620 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const words = text.split(' ');

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: 70,
        right: 70,
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'center',
        gap: '0 18px',
      }}
    >
      {words.map((w, i) => {
        const s = spring({
          frame: frame - delay - i * 2.5,
          fps,
          config: { damping: 14, stiffness: 120, mass: 0.6 },
        });
        return (
          <span
            key={i}
            style={{
              fontSize: size,
              fontWeight: 900,
              color,
              lineHeight: 1.14,
              opacity: s,
              transform: `translateY(${(1 - s) * 42}px)`,
              textShadow: '0 4px 28px rgba(0,0,0,0.75), 0 1px 4px rgba(0,0,0,0.6)',
              display: 'inline-block',
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};

/* ── the money shot: a number that actually counts, with real easing ── */
export const CountUp: React.FC<{
  value: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  size?: number;
  color?: string;
  top?: number;
  delay?: number;
}> = ({ value, decimals = 0, prefix = '', suffix = '', size = 250, color = C.cyan, top = 780, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - delay,
    fps,
    config: { damping: 200, stiffness: 42, mass: 1.6 },
    durationInFrames: 42,
  });
  const shown = (value * progress).toFixed(decimals);

  // tiny pop the moment it lands
  const pop = spring({ frame: frame - delay - 40, fps, config: { damping: 9, stiffness: 180 } });
  const scale = 1 + pop * 0.045 * Math.max(0, 1 - (frame - delay - 46) / 18);

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: 0,
        right: 0,
        textAlign: 'center',
        fontSize: size,
        fontWeight: 900,
        color,
        letterSpacing: -4,
        transform: `scale(${Math.max(1, scale)})`,
        textShadow: `0 0 70px ${color}66, 0 5px 30px rgba(0,0,0,0.7)`,
      }}
    >
      {prefix}
      {shown}
      {suffix}
    </div>
  );
};

export const Label: React.FC<{
  text: string;
  top: number;
  size?: number;
  color?: string;
  delay?: number;
}> = ({ text, top, size = 46, color = C.gray, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 16, stiffness: 90 } });
  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: 60,
        right: 60,
        textAlign: 'center',
        fontFamily: FONT_BODY,
        fontSize: size,
        color,
        letterSpacing: 3,
        textTransform: 'uppercase',
        textShadow: '0 3px 18px rgba(0,0,0,0.95), 0 1px 3px rgba(0,0,0,0.9)',
        opacity: s,
        transform: `translateY(${(1 - s) * 16}px)`,
      }}
    >
      {text}
    </div>
  );
};

/* ── ranked rows that slide in and fill, for list-style beats ── */
export const Row: React.FC<{
  left: string;
  right: string;
  index: number;
  top: number;
  color?: string;
  pct?: number;
}> = ({ left, right, index, top, color = C.cyan, pct = 100 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({
    frame: frame - index * 5,
    fps,
    config: { damping: 15, stiffness: 110, mass: 0.7 },
  });
  const fill = interpolate(s, [0, 1], [0, pct]);

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: 80,
        right: 80,
        opacity: s,
        transform: `translateX(${(1 - s) * -60}px)`,
      }}
    >
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `${color}1c`,
          borderRadius: 18,
          width: `${fill}%`,
        }}
      />
      <div
        style={{
          position: 'relative',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '20px 26px',
          fontSize: 50,
          fontWeight: 900,
        }}
      >
        <span style={{ color: C.white }}>{left}</span>
        <span style={{ color }}>{right}</span>
      </div>
    </div>
  );
};
