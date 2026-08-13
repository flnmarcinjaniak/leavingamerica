import React from 'react';
import { AbsoluteFill } from 'remotion';
import { CountUp, KineticText, Label, Row } from './components';
import { Particles, ScaleBars } from './visuals';
import { Scene, SceneSpec, starts, totalFrames } from './Scene';
import { C } from './theme';
import { get } from './data';

/* Attacks the country everyone recommends. Spain and Malaysia score identically on
   healthcare and safety; Malaysia costs half. Same story for Italy and Costa Rica. */
const spain = get('spain');
const malaysia = get('malaysia');
const italy = get('italy');
const costaRica = get('costa-rica');
const saving = Math.round((1 - malaysia.cost / spain.cost) * 100);

const SCENES: SceneSpec[] = [
  { vo: 'half-price-1', frames: 278, bg: 'spain', push: 'in' },
  { vo: 'half-price-2', frames: 311, bg: 'spain', push: 'out', dim: 0.5 },
  { vo: 'half-price-3', frames: 365, bg: 'malaysia', dim: 0.5 },
  { vo: 'half-price-4', frames: 338, bg: 'map', dim: 0.62 },
  { vo: 'half-price-5', frames: 182, bg: 'cafe-laptop', push: 'in' },
];
const S = starts(SCENES);
export const TOTAL_FRAMES = totalFrames(SCENES);

const Scores: React.FC<{ h: number; s: number; top: number; delay: number }> = ({ h, s, top, delay }) => (
  <>
    <Label text={`healthcare ${h}/10`} top={top} delay={delay} size={44} color={C.white} />
    <Label text={`safety ${s}/10`} top={top + 80} delay={delay + 14} size={44} color={C.white} />
  </>
);

export const HalfPrice: React.FC = () => (
  <AbsoluteFill>
    <Scene spec={SCENES[0]} from={S[0]}>
      <Particles />
      <KineticText text="Everyone tells you to move to Spain." size={94} top={520} />
      <KineticText text="Almost nobody mentions the country at half the price." size={64} color={C.gray} delay={64} top={980} />
    </Scene>

    <Scene spec={SCENES[1]} from={S[1]}>
      <Label text={spain.name} top={440} size={62} color={C.white} />
      <CountUp value={spain.cost} prefix="$" top={600} delay={12} color={C.red} size={230} />
      <Label text="per month, one person" top={930} delay={56} />
      <Scores h={spain.health} s={spain.safety} top={1090} delay={78} />
    </Scene>

    <Scene spec={SCENES[2]} from={S[2]}>
      <Label text={malaysia.name} top={400} size={62} color={C.white} />
      <CountUp value={malaysia.cost} prefix="$" top={550} delay={12} color={C.green} size={230} />
      <Label text="per month, one person" top={880} delay={56} />
      <Scores h={malaysia.health} s={malaysia.safety} top={1000} delay={78} />
      <ScaleBars
        top={1240}
        delay={120}
        a={{ label: spain.name, value: spain.cost, display: `$${spain.cost}`, color: C.red }}
        b={{ label: malaysia.name, value: malaysia.cost, display: `$${malaysia.cost}`, color: C.green }}
      />
      <Label text={`${saving}% cheaper, identical scores`} top={1700} delay={190} size={46} color={C.cyan} />
    </Scene>

    <Scene spec={SCENES[3]} from={S[3]}>
      <Label text="Same story, other favourites" top={430} size={46} color={C.white} />
      {[
        { left: `${italy.name} $${italy.cost}`, right: `vs $${malaysia.cost}`, pct: 100 },
        { left: `${costaRica.name} $${costaRica.cost}`, right: `vs $${malaysia.cost}`, pct: 76 },
        { left: `${spain.name} $${spain.cost}`, right: `vs $${malaysia.cost}`, pct: 96 },
      ].map((r, i) => (
        <Row key={i} index={i} top={600 + i * 150} left={r.left} right={r.right} color={C.cyan} pct={r.pct} />
      ))}
      <KineticText
        text="Popularity and value are not the same thing."
        size={62}
        delay={110}
        top={1180}
      />
    </Scene>

    <Scene spec={SCENES[4]} from={S[4]}>
      <Particles />
      <KineticText text="Compare any two countries." size={92} top={580} />
      <Label text="free · 74 countries · no signup" top={820} delay={20} size={40} />
      <KineticText text="leavingamerica.co" size={74} color={C.cyan} delay={34} top={950} />
    </Scene>
  </AbsoluteFill>
);
