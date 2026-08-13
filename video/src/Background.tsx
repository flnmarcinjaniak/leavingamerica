import React from 'react';
import { AbsoluteFill, Img, OffthreadVideo, interpolate, staticFile, useCurrentFrame } from 'remotion';
import { C, FONT } from './theme';

type Props = {
  /** slot name in public/bg — resolves to <slot>.mp4, falling back to <slot>.jpg */
  src?: string;
  /** force still-image mode even when an mp4 exists */
  still?: boolean;
  /** ken burns direction (stills only; clips already move) */
  push?: 'in' | 'out';
  /** scrim strength — raise when a lot of text sits on top */
  dim?: number;
  /** seconds into the clip to start, so repeated slots do not look identical */
  startFrom?: number;
  children: React.ReactNode;
};

export const Background: React.FC<Props> = ({
  src,
  still = false,
  push = 'in',
  dim = 0.34,
  startFrom = 0,
  children,
}) => {
  const frame = useCurrentFrame();

  // stills need synthetic motion; clips bring their own
  const z = push === 'in'
    ? interpolate(frame, [0, 130], [1.06, 1.20], { extrapolateRight: 'clamp' })
    : interpolate(frame, [0, 130], [1.20, 1.06], { extrapolateRight: 'clamp' });
  const pan = interpolate(frame, [0, 130], [0, -22], { extrapolateRight: 'clamp' });

  // one grade for every shot, so mixed sources still read as one series
  const grade = 'saturate(0.74) contrast(1.10) brightness(1.06)';

  return (
    <AbsoluteFill style={{ backgroundColor: C.bg1, overflow: 'hidden', fontFamily: FONT }}>
      {src && (
        <AbsoluteFill>
          {still ? (
            <Img
              src={staticFile(`bg/${src}.jpg`)}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                transform: `scale(${z}) translateY(${pan}px)`,
                filter: grade,
              }}
            />
          ) : (
            <OffthreadVideo
              src={staticFile(`bg/${src}.mp4`)}
              startFrom={startFrom}
              muted
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                filter: grade,
                // very slight push keeps even a static-ish clip alive
                transform: `scale(${interpolate(frame, [0, 130], [1.03, 1.10], { extrapolateRight: 'clamp' })})`,
              }}
            />
          )}

          {/* brand tint */}
          <AbsoluteFill
            style={{
              background: `linear-gradient(180deg, ${C.bg1}99 0%, ${C.bg2}3a 45%, ${C.bg1}b0 100%)`,
              mixBlendMode: 'multiply',
            }}
          />
          {/* readability scrim */}
          <AbsoluteFill
            style={{
              background: `radial-gradient(ellipse at 50% 46%, rgba(6,12,24,${dim * 0.38}) 0%, rgba(6,12,24,${dim}) 58%, rgba(6,12,24,${Math.min(dim + 0.22, 0.78)}) 100%)`,
            }}
          />
        </AbsoluteFill>
      )}

      {!src && (
        <AbsoluteFill style={{ background: `linear-gradient(170deg, ${C.bg1} 0%, ${C.bg2} 100%)` }} />
      )}

      {children}

      <div
        style={{
          position: 'absolute',
          bottom: 96,
          left: 0,
          right: 0,
          textAlign: 'center',
          fontFamily: 'Arial, sans-serif',
          fontSize: 34,
          color: 'rgba(255,255,255,0.52)',
          letterSpacing: 1,
          textShadow: '0 2px 14px rgba(0,0,0,0.8)',
        }}
      >
        leavingamerica.co
      </div>

      {/* Pexels API terms ask for a visible credit; one line covers the whole video */}
      <div
        style={{
          position: 'absolute',
          bottom: 40,
          left: 0,
          right: 0,
          textAlign: 'center',
          fontFamily: 'Arial, sans-serif',
          fontSize: 17,
          color: 'rgba(255,255,255,0.28)',
        }}
      >
        footage via Pexels
      </div>
    </AbsoluteFill>
  );
};
