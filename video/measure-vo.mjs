// Measures every voiceover track and prints the frame count each scene needs.
// Scene length = spoken length + 1s of reading room, at 30fps.
//
// Usage: node measure-vo.mjs [video-id ...]

import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { existsSync, writeFileSync } from 'node:fs';
import ffmpeg from '@ffmpeg-installer/ffmpeg';

const run = promisify(execFile);
const FPS = 30;
const PAD = 30; // 1s of reading room

const VIDEOS = process.argv.slice(2).length
  ? process.argv.slice(2)
  : ['visa-trap', 'fire-number', 'half-price', 'dangerous', 'income', 'rent'];

/** ffmpeg writes probe output to stderr and exits non-zero without an output file */
const duration = async (file) => {
  try {
    await run(ffmpeg.path, ['-i', file]);
    return 0;
  } catch (e) {
    const m = String(e.stderr ?? '').match(/Duration: (\d+):(\d+):([\d.]+)/);
    return m ? +m[1] * 3600 + +m[2] * 60 + +m[3] : 0;
  }
};

const out = {};
for (const v of VIDEOS) {
  const frames = [];
  const secs = [];
  for (let i = 1; i <= 5; i++) {
    const f = `public/vo/${v}-${i}.mp3`;
    if (!existsSync(f)) { frames.push(null); secs.push(null); continue; }
    const d = await duration(f);
    secs.push(+d.toFixed(1));
    frames.push(Math.ceil(d * FPS) + PAD);
  }
  out[v] = frames;
  const total = frames.reduce((a, b) => a + (b ?? 0), 0);
  console.log(
    `${v.padEnd(13)} frames [${frames.join(', ')}]  total ${(total / FPS).toFixed(1)}s` +
    `   speech [${secs.join(', ')}]`
  );
}

writeFileSync('scene-frames.json', JSON.stringify(out, null, 2));
console.log('\n-> scene-frames.json');
