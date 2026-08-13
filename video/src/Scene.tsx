import React from 'react';
import { Audio, Sequence, staticFile } from 'remotion';
import { Background } from './Background';
import voAvailable from '../public/vo/available.json';

/* ── shared scene wrapper ──
   Every composition is a list of scenes. A scene owns its own voiceover track,
   so audio can never drift against the cuts (that bug shipped once: the narration
   talked about the passport while the runway number was counting up).

   Frame counts come from measure-vo.mjs: spoken length + 1s of reading room. */

export type SceneSpec = {
  vo: string;          // id of the mp3 in public/vo
  frames: number;      // measured, do not guess
  bg?: string;         // clip slot in public/bg
  dim?: number;        // raise when a lot of text sits on top
  push?: 'in' | 'out';
};

export const starts = (scenes: SceneSpec[]) =>
  scenes.reduce<number[]>((acc, _s, i) => {
    acc.push(i === 0 ? 0 : acc[i - 1] + scenes[i - 1].frames);
    return acc;
  }, []);

export const totalFrames = (scenes: SceneSpec[]) =>
  scenes.reduce((sum, s) => sum + s.frames, 0);

const Vo: React.FC<{ id: string }> = ({ id }) =>
  (voAvailable as string[]).includes(id)
    ? <Audio src={staticFile(`vo/${id}.mp3`)} />
    : null;

export const Scene: React.FC<{
  spec: SceneSpec;
  from: number;
  children: React.ReactNode;
}> = ({ spec, from, children }) => (
  <Sequence from={from} durationInFrames={spec.frames}>
    <Vo id={spec.vo} />
    <Background src={spec.bg} dim={spec.dim} push={spec.push}>
      {children}
    </Background>
  </Sequence>
);
