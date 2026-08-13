import React from 'react';
import { AbsoluteFill } from 'remotion';
import { CountUp, KineticText, Label, Row } from './components';
import { Particles, ScaleBars } from './visuals';
import { Scene, SceneSpec, starts, totalFrames } from './Scene';
import { C } from './theme';
import { rows } from './data';

/* The single sharpest contrast in the dataset: the 4% rule applied abroad.
   US baseline $3,500/mo -> $1,050,000. Egypt $700/mo -> $210,000. */
const US_MONTHLY = 3500;
const usFire = US_MONTHLY * 12 * 25;

const fireOf = (r: { cost: number }) => Math.round((r.cost * 12 * 25) / 1000) * 1000;
const cheapest = [...rows].sort((a, b) => a.cost - b.cost).slice(0, 6);
const eg = cheapest[0];

const SCENES: SceneSpec[] = [
  { vo: 'fire-number-1', frames: 243, bg: 'money', push: 'in' },
  { vo: 'fire-number-2', frames: 248, bg: 'cafe-laptop', push: 'out' },
  { vo: 'fire-number-3', frames: 328, bg: 'cairo', dim: 0.42 },
  { vo: 'fire-number-4', frames: 238, bg: 'map', dim: 0.62 },
  { vo: 'fire-number-5', frames: 158, bg: 'danang', push: 'in' },
];
const S = starts(SCENES);
export const TOTAL_FRAMES = totalFrames(SCENES);

export const FireNumber: React.FC = () => (
  <AbsoluteFill>
    <Scene spec={SCENES[0]} from={S[0]}>
      <Particles />
      <KineticText text="You are not $1,000,000 away from retiring." size={92} top={520} />
      <KineticText text="You might be $210,000 away." size={76} color={C.cyan} delay={60} top={1000} />
    </Scene>

    <Scene spec={SCENES[1]} from={S[1]}>
      <Particles />
      <Label text="Typical US city · the 4% rule" top={470} size={44} color={C.white} />
      <CountUp value={usFire / 1000} decimals={0} prefix="$" suffix="K" top={640} delay={12} color={C.red} size={220} />
      <Label text="what you need saved to stop working" top={980} delay={60} />
      <Label text="based on $3,500 a month" top={1080} delay={78} size={34} color={C.dim} />
    </Scene>

    <Scene spec={SCENES[2]} from={S[2]}>
      <Label text="Same rule, different country" top={430} size={44} color={C.white} />
      <ScaleBars
        top={580}
        delay={30}
        a={{ label: 'United States', value: usFire, display: `$${(usFire / 1000).toFixed(0)}K`, color: C.red }}
        b={{ label: eg.name, value: fireOf(eg), display: `$${(fireOf(eg) / 1000).toFixed(0)}K`, color: C.cyan }}
      />
      <Label text={`$${((usFire - fireOf(eg)) / 1000).toFixed(0)},000 of difference`} top={1150} delay={110} size={44} color={C.cyan} />
    </Scene>

    <Scene spec={SCENES[3]} from={S[3]}>
      <Label text="Lowest FIRE numbers tracked" top={420} size={46} color={C.white} />
      {cheapest.map((r, i) => (
        <Row
          key={r.slug}
          index={i}
          top={560 + i * 132}
          left={r.name}
          right={`$${(fireOf(r) / 1000).toFixed(0)}K`}
          color={C.green}
          pct={(fireOf(r) / usFire) * 100}
        />
      ))}
      <Label text={`the US figure is $${(usFire / 1000).toFixed(0)}K`} top={1400} delay={80} size={46} color={C.white} />
    </Scene>

    <Scene spec={SCENES[4]} from={S[4]}>
      <Particles />
      <KineticText text="Run your own number." size={96} top={580} />
      <Label text="free calculator · 74 countries · no signup" top={820} delay={20} size={40} />
      <KineticText text="leavingamerica.co" size={74} color={C.cyan} delay={34} top={950} />
    </Scene>
  </AbsoluteFill>
);
