import React from 'react';
import { AbsoluteFill } from 'remotion';
import { CountUp, KineticText, Label, Row } from './components';
import { CountryGrid, Particles, TimelineFill } from './visuals';
import { Scene, SceneSpec, starts, totalFrames } from './Scene';
import { C } from './theme';
import { get, rows, total } from './data';

/* The trade nobody prices in: the longest runways belong to some of the least safe
   countries. India 11.1 years at safety 4/10, Turkey 9.8 at 3/10. */
const india = get('india');
const turkey = get('turkey');
const colombia = get('colombia');
const passing = rows.filter(r => r.y100 >= 5 && r.health >= 7 && r.safety >= 7).length;

const SCENES: SceneSpec[] = [
  { vo: 'dangerous-1', frames: 253, bg: 'india', push: 'in' },
  { vo: 'dangerous-2', frames: 288, bg: 'india', push: 'out', dim: 0.52 },
  { vo: 'dangerous-3', frames: 333, bg: 'airport', dim: 0.56 },
  { vo: 'dangerous-4', frames: 225, bg: 'hospital', dim: 0.52 },
  { vo: 'dangerous-5', frames: 155, bg: 'cafe-laptop', push: 'in' },
];
const S = starts(SCENES);
export const TOTAL_FRAMES = totalFrames(SCENES);

export const Dangerous: React.FC = () => (
  <AbsoluteFill>
    <Scene spec={SCENES[0]} from={S[0]}>
      <Particles />
      <KineticText text="Where your money lasts longest" size={92} top={520} />
      <KineticText text="is also where you are least safe." size={82} color={C.red} delay={56} top={960} />
    </Scene>

    <Scene spec={SCENES[1]} from={S[1]}>
      <Label text={india.name} top={470} size={62} color={C.white} />
      <CountUp value={india.y100} decimals={1} top={620} delay={12} size={240} />
      <Label text="years on $100,000" top={960} delay={58} />
      <TimelineFill years={india.y100} maxYears={12} top={1140} delay={30} />
      <Label text="second longest runway tracked" top={1290} delay={80} size={38} color={C.dim} />
    </Scene>

    <Scene spec={SCENES[2]} from={S[2]}>
      <Label text="Safety score, out of 10" top={420} size={46} color={C.white} />
      {[india, turkey, colombia].map((r, i) => (
        <Row
          key={r.slug}
          index={i}
          top={580 + i * 150}
          left={`${r.name}  ·  ${r.y100} yrs`}
          right={`${r.safety}/10`}
          color={C.red}
          pct={r.safety * 10}
        />
      ))}
      <KineticText text="Cheap countries are cheap for reasons." size={64} delay={120} top={1180} />
    </Scene>

    <Scene spec={SCENES[3]} from={S[3]}>
      <Label text="Pass healthcare AND safety" top={430} size={46} color={C.white} />
      <CountUp value={passing} top={560} color={C.green} size={250} delay={10} />
      <Label text={`of ${total} countries tracked`} top={870} delay={48} />
      <CountryGrid total={total} highlight={passing} color={C.green} top={1000} delay={28} />
    </Scene>

    <Scene spec={SCENES[4]} from={S[4]}>
      <Particles />
      <KineticText text="Every score is published." size={92} top={580} />
      <Label text="free · 74 countries · sources listed" top={820} delay={20} size={40} />
      <KineticText text="leavingamerica.co" size={74} color={C.cyan} delay={34} top={950} />
    </Scene>
  </AbsoluteFill>
);
