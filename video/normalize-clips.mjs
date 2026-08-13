// Normalises every background clip: constant 30fps, and looped to a fixed length.
//
// Two problems this solves, both of which shipped as "No frame found at position N":
//   1. Pexels clips arrive at 25, 29.97 and 60 fps. A scene asking for a timestamp
//      that does not land on a real frame in a mismatched-rate source fails.
//   2. Clips are 6-30s while scenes run up to 12s and start deep into the timeline.
//      Any request past the last frame fails.
//
// Forcing CFR 30 and looping every clip to MIN_SECONDS removes both classes at once.
//
// Usage: node normalize-clips.mjs

import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { readdirSync, renameSync, unlinkSync, statSync } from 'node:fs';
import { join } from 'node:path';
import ffmpeg from '@ffmpeg-installer/ffmpeg';

const run = promisify(execFile);
const DIR = 'public/bg';
const FPS = 30;
const MIN_SECONDS = 45; // longer than any composition, so no scene can outrun a clip

const clips = readdirSync(DIR).filter(f => f.endsWith('.mp4'));
console.log(`normalising ${clips.length} clips to CFR ${FPS}fps\n`);

for (const f of clips) {
  const src = join(DIR, f);
  const tmp = join(DIR, `_tmp_${f}`);
  const before = statSync(src).size;

  await run(ffmpeg.path, [
    '-stream_loop', '-1',       // repeat the source...
    '-i', src,
    '-t', String(MIN_SECONDS),  // ...and cut at a fixed length
    '-r', String(FPS),          // force constant frame rate
    '-vsync', 'cfr',
    '-c:v', 'libx264',
    '-preset', 'veryfast',
    '-crf', '20',
    '-pix_fmt', 'yuv420p',
    '-an',                      // background clips are muted anyway
    '-movflags', '+faststart',
    '-y', tmp,
  ]);

  unlinkSync(src);
  renameSync(tmp, src);
  const after = statSync(src).size;
  console.log(`  ${f.padEnd(18)} ${(before / 1048576).toFixed(1)} -> ${(after / 1048576).toFixed(1)} MB`);
}

console.log('\ndone. Re-run this after fetching new clips.');
