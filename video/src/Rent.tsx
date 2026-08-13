import React from 'react';
import { AbsoluteFill } from 'remotion';
import { CountUp, KineticText, Label, Row } from './components';
import { Particles, ScaleBars } from './visuals';
import { Scene, SceneSpec, starts, totalFrames } from './Scene';
import { C } from './theme';
import { cities } from './data';

/* Makes it personal in one sentence: whatever you pay in rent is a whole life
   somewhere else. Batumi at $350 all-in is the sharpest example in the set. */
const US_MONTHLY = 3500;
const cheapest = cities[0];
const cheapYears = +(100000 / cheapest.monthly_usd / 12).toFixed(1);
const usYears = +(100000 / US_MONTHLY / 12).toFixed(1);
const top5 = cities.slice(0, 5);

const SCENES: SceneSpec[] = [
  { vo: 'rent-1', frames: 202, bg: 'money', push: 'in' },
  { vo: 'rent-2', frames: 306, bg: 'batumi', push: 'out', dim: 0.46 },
  { vo: 'rent-3', frames: 308, bg: 'batumi', dim: 0.56 },
  { vo: 'rent-4', frames: 248, bg: 'map', dim: 0.62 },
  { vo: 'rent-5', frames: 171, bg: 'cafe-laptop', push: 'in' },
];
const S = starts(SCENES);
export const TOTAL_FRAMES = totalFrames(SCENES);

export const Rent: React.FC = () => (
  <AbsoluteFill>
    <Scene spec={SCENES[0]} from={S[0]}>
      <Particles />
      <KineticText text="Whatever you pay in rent" size={92} top={560} />
      <KineticText text="is a whole life somewhere else." size={84} color={C.cyan} delay={50} top={960} />
    </Scene>

    <Scene spec={SCENES[1]} from={S[1]}>
      <Label text={`${cheapest.name}, ${cheapest.country}`} top={450} size={54} color={C.white} />
      <CountUp value={cheapest.monthly_usd} prefix="$" top={600} delay={12} size={250} />
      <Label text="per month, everything included" top={930} delay={58} />
      <Label text="rent · food · transport" top={1040} delay={76} size={38} color={C.dim} />
    </Scene>

    <Scene spec={SCENES[2]} from={S[2]}>
      <Label text="What $100,000 buys you" top={430} size={48} color={C.white} />
      <ScaleBars
        top={580}
        delay={24}
        a={{ label: cheapest.name, value: cheapYears, display: `${cheapYears} years`, color: C.cyan }}
        b={{ label: 'Typical US city', value: usYears, display: `${usYears} years`, color: C.red }}
      />
      <Label text="same money, same lifestyle" top={1150} delay={110} size={44} />
    </Scene>

    <Scene spec={SCENES[3]} from={S[3]}>
      <Label text="Cheapest cities tracked" top={430} size={46} color={C.white} />
      {top5.map((c, i) => (
        <Row
          key={c.name}
          index={i}
          top={580 + i * 140}
          left={c.name}
          right={`$${c.monthly_usd}`}
          color={C.cyan}
          pct={(c.monthly_usd / US_MONTHLY) * 100}
        />
      ))}
      <Label text={`${cities.length} cities, not national averages`} top={1320} delay={90} size={42} />
    </Scene>

    <Scene spec={SCENES[4]} from={S[4]}>
      <Particles />
      <KineticText text="Check your own city." size={94} top={580} />
      <Label text="222 cities · free · no signup" top={820} delay={20} size={40} />
      <KineticText text="leavingamerica.co" size={74} color={C.cyan} delay={34} top={950} />
    </Scene>
  </AbsoluteFill>
);
