import React from 'react';
import { AbsoluteFill, Audio, Sequence, staticFile } from 'remotion';
import { CountUp, KineticText, Label } from './components';
import { Background } from './Background';
import { CountryGrid, Particles, ScaleBars, TimelineFill } from './visuals';
import { C } from './theme';
import { get, thirtyDay, total, nomadCount } from './data';
import voAvailable from '../public/vo/available.json';

const eg = get('egypt');

// 30 days expressed in years, so both bars share one honest scale
const visaYears = (eg.visa ?? 30) / 365;

/* ── timing ──
   Each scene lasts as long as its own narration plus reading room. Measured speech:
   4.6 / 6.5 / 7.3 / 4.7 / 3.4 s. One long track drifted against the cuts - the
   narration talked about the passport while the runway number was counting up.
   Every line now sits inside its own Sequence, so they cannot desync. */
const SCENES = [
  { id: 'visa-trap-1', frames: 181 }, // 5.5s (speech 4.6)
  { id: 'visa-trap-2', frames: 250 }, // 7.3s (speech 6.5)
  { id: 'visa-trap-3', frames: 324 }, // 8.3s (speech 7.3)
  { id: 'visa-trap-4', frames: 173 }, // 5.7s (speech 4.7)
  { id: 'visa-trap-5', frames: 137 }, // 4.5s (speech 3.4)
];
const START = SCENES.reduce<number[]>((acc, _s, i) => {
  acc.push(i === 0 ? 0 : acc[i - 1] + SCENES[i - 1].frames);
  return acc;
}, []);
export const TOTAL_FRAMES = START[4] + SCENES[4].frames; // 940 = 31.3s

const Vo: React.FC<{ id: string }> = ({ id }) =>
  (voAvailable as string[]).includes(id)
    ? <Audio src={staticFile(`vo/${id}.mp3`)} />
    : null;

export const VisaTrap: React.FC = () => (
  <AbsoluteFill>
    {/* 1. hook */}
    <Sequence from={START[0]} durationInFrames={SCENES[0].frames}>
      <Vo id="visa-trap-1" />
      <Background src="cairo" push="in">
        <Particles />
        <KineticText text="Your $100,000 buys 12 years here." size={104} top={560} />
        <KineticText text="Your passport gets you 30 days." size={68} color={C.gray} delay={40} top={980} />
      </Background>
    </Sequence>

    {/* 2. the number */}
    <Sequence from={START[1]} durationInFrames={SCENES[1].frames}>
      <Vo id="visa-trap-2" />
      <Background src="danang" push="out">
        <Particles />
        <Label text="Egypt" top={480} size={58} color={C.white} />
        <CountUp value={eg.y100} decimals={1} top={640} delay={10} />
        <Label text="years on $100,000" top={980} delay={52} />
        <TimelineFill years={eg.y100} maxYears={12} top={1160} delay={24} />
        <Label text="years" top={1290} delay={48} size={30} color={C.dim} />
      </Background>
    </Sequence>

    {/* 3. the twist: two bars on ONE scale */}
    <Sequence from={START[2]} durationInFrames={SCENES[2].frames}>
      <Vo id="visa-trap-3" />
      <Background src="passport" dim={0.58}>
        <Label text="Same scale" top={470} size={44} color={C.white} />
        <ScaleBars
          top={620}
          delay={30}
          a={{ label: 'What you can afford', value: eg.y100, display: `${eg.y100} years`, color: C.cyan }}
          b={{ label: 'What the visa allows', value: visaYears, display: `${eg.visa} days`, color: C.red }}
        />
      </Background>
    </Sequence>

    {/* 4. the scale of it */}
    <Sequence from={START[3]} durationInFrames={SCENES[3].frames}>
      <Vo id="visa-trap-4" />
      <Background src="airport">
        <Label text="And it is not alone" top={440} size={46} color={C.white} />
        <CountUp value={thirtyDay} top={560} color={C.red} size={250} delay={8} />
        <Label text={`of ${total} countries give just 30 days`} top={870} delay={44} />
        <CountryGrid total={total} highlight={thirtyDay} top={1000} delay={26} />
        <Label text={`only ${nomadCount} have a nomad visa`} top={1560} delay={80} color={C.dim} size={38} />
      </Background>
    </Sequence>

    {/* 5. cta */}
    <Sequence from={START[4]} durationInFrames={SCENES[4].frames}>
      <Vo id="visa-trap-5" />
      <Background src="cafe-laptop" push="in">
        <Particles />
        <KineticText text="Check your own number." size={96} top={560} />
        <Label text="free calculator · 74 countries · no signup" top={800} delay={20} size={40} />
        <KineticText text="leavingamerica.co" size={74} color={C.cyan} delay={34} top={930} />
      </Background>
    </Sequence>
  </AbsoluteFill>
);
