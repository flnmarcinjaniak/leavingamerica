import React from 'react';
import { AbsoluteFill } from 'remotion';
import { CountUp, KineticText, Label, Row } from './components';
import { Particles } from './visuals';
import { Scene, SceneSpec, starts, totalFrames } from './Scene';
import { C } from './theme';
import { total, under } from './data';

/* Flips the question. Not "how much do you need saved" but "how little do you need
   to earn". Once income beats local cost, the runway stops being finite. */
const TIERS = [1000, 1500, 2000, 2500, 3000];

const SCENES: SceneSpec[] = [
  { vo: 'income-1', frames: 185, bg: 'cafe-laptop', push: 'in' },
  { vo: 'income-2', frames: 236, bg: 'money', push: 'out', dim: 0.5 },
  { vo: 'income-3', frames: 214, bg: 'money', dim: 0.58 },
  { vo: 'income-4', frames: 292, bg: 'danang', dim: 0.44 },
  { vo: 'income-5', frames: 151, bg: 'cafe-laptop', push: 'in' },
];
const S = starts(SCENES);
export const TOTAL_FRAMES = totalFrames(SCENES);

export const Income: React.FC = () => (
  <AbsoluteFill>
    <Scene spec={SCENES[0]} from={S[0]}>
      <Particles />
      <KineticText text="How much do you need saved?" size={92} top={560} />
      <KineticText text="Wrong question." size={96} color={C.red} delay={52} top={960} />
    </Scene>

    <Scene spec={SCENES[1]} from={S[1]}>
      <Label text="$2,000 a month covers" top={470} size={50} color={C.white} />
      <CountUp value={under(2000)} top={620} delay={12} size={260} />
      <Label text={`of ${total} countries, in full`} top={960} delay={58} />
      <Label text="rent, food, transport, one person" top={1070} delay={76} size={36} color={C.dim} />
    </Scene>

    <Scene spec={SCENES[2]} from={S[2]}>
      <Label text="What each income unlocks" top={420} size={46} color={C.white} />
      {TIERS.map((t, i) => (
        <Row
          key={t}
          index={i}
          top={580 + i * 140}
          left={`$${t.toLocaleString()}/mo`}
          right={`${under(t)} countries`}
          color={C.cyan}
          pct={(under(t) / total) * 100}
        />
      ))}
    </Scene>

    <Scene spec={SCENES[3]} from={S[3]}>
      <Particles />
      <KineticText text="Once income beats local cost," size={82} top={620} />
      <KineticText text="your savings stop shrinking." size={88} color={C.green} delay={54} top={880} />
      <Label text="the runway is no longer finite" top={1180} delay={110} size={44} />
    </Scene>

    <Scene spec={SCENES[4]} from={S[4]}>
      <Particles />
      <KineticText text="Find your own threshold." size={92} top={580} />
      <Label text="free calculator · no signup" top={820} delay={20} size={40} />
      <KineticText text="leavingamerica.co" size={74} color={C.cyan} delay={34} top={950} />
    </Scene>
  </AbsoluteFill>
);
