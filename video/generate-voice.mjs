// Generates an American-accented voiceover track per video, from the narration lines.
//
// Two providers, same interface - pick with VOICE_PROVIDER in .env:
//   openai      gpt-4o-mini-tts   ~$0.015/min, steerable tone, commercial use OK
//   elevenlabs  eleven_v3         best-in-class naturalness, needs a PAID plan for commercial use
//
// Setup:  create video/.env with
//   VOICE_PROVIDER=openai
//   OPENAI_API_KEY=sk-...
//   (or) ELEVENLABS_API_KEY=...
//
// Usage:  node generate-voice.mjs            all videos
//         node generate-voice.mjs visa-trap  one video
//
// Output: public/vo/<id>.mp3  - Remotion plays it with <Audio src={staticFile(...)} />

import { mkdirSync, writeFileSync, existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const OUT = 'public/vo';

/* ── config ── */
const env = existsSync('.env')
  ? Object.fromEntries(
      readFileSync('.env', 'utf8')
        .split('\n')
        .filter(l => l.includes('='))
        .map(l => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
    )
  : {};
const cfg = { ...env, ...process.env };
const PROVIDER = (cfg.VOICE_PROVIDER ?? 'openai').toLowerCase();

/* ── narration: one flowing paragraph per video, written to be SPOKEN not read ──
   Keep sentences short. Numbers spelled the way a person would say them. */
export const SCRIPTS = {
  // ONE TRACK PER SCENE. A single long track drifts against the cuts - the narration
  // ended up talking about the passport while the runway number was counting up.
  // Each line now lives inside its own <Sequence>, so they cannot desync.
  'visa-trap-1': {
    text: `Your hundred thousand dollars buys twelve years in Egypt.`,
    instructions: 'Calm, confident American narrator. Conversational, not newsreader. Land "twelve years" clearly.',
  },
  'visa-trap-2': {
    text: `Eleven point nine years of living costs. That is what a hundred grand buys you there.`,
    instructions: 'Calm, confident American narrator. Slight emphasis on the number, then relax.',
  },
  'visa-trap-3': {
    text: `But the tourist visa runs out after thirty days. Same country, two completely different answers.`,
    instructions: 'Calm, confident American narrator. A beat before "thirty days". Let the contrast land.',
  },
  'visa-trap-4': {
    text: `Ten of the seventy-four countries I track do exactly this.`,
    instructions: 'Calm, confident American narrator. Matter of fact, slightly weightier.',
  },
  'visa-trap-5': {
    text: `Run your own number on the free calculator.`,
    instructions: 'Calm, confident American narrator. Warm, inviting, unhurried.',
  },
  /* ── 02 FIRE number: the strongest single contrast in the dataset ── */
  'fire-number-1': {
    text: `You are not a million dollars away from retiring. You might be two hundred ten thousand away.`,
    instructions: 'Calm, confident American narrator. Let the second number land softly, almost as an aside.',
  },
  'fire-number-2': {
    text: `In a typical US city, the four percent rule puts your number at one million fifty thousand dollars.`,
    instructions: 'Calm, confident American narrator. Matter of fact.',
  },
  'fire-number-3': {
    text: `In Egypt, the same rule puts it at two hundred ten thousand. Same lifestyle. Same math. Eight hundred forty thousand dollars of difference.`,
    instructions: 'Calm, confident American narrator. A beat before the last sentence. Let it sit.',
  },
  'fire-number-4': {
    text: `These are the six lowest numbers on my list. Every one of them is under a third of the American figure.`,
    instructions: 'Calm, confident American narrator. Even pace.',
  },
  'fire-number-5': {
    text: `Run the number for any country on the free calculator.`,
    instructions: 'Calm, confident American narrator. Warm, unhurried.',
  },

  /* ── 03 popular vs underrated: attacks the country everyone recommends ── */
  'half-price-1': {
    text: `Everyone tells you to move to Spain. Almost nobody mentions the country that is half the price with identical scores.`,
    instructions: 'Calm, confident American narrator. Slight edge of "here is what they miss".',
  },
  'half-price-2': {
    text: `Spain costs about two thousand two hundred dollars a month for one person. Healthcare eight out of ten, safety eight out of ten.`,
    instructions: 'Calm, confident American narrator. Neutral, factual.',
  },
  'half-price-3': {
    text: `Malaysia costs one thousand and fifty. The same eight out of ten on healthcare. The same eight on safety. Fifty two percent cheaper for the same numbers.`,
    instructions: 'Calm, confident American narrator. Emphasise "the same" both times.',
  },
  'half-price-4': {
    text: `Italy against Malaysia is the same story. So is Costa Rica. Popularity and value are not the same thing.`,
    instructions: 'Calm, confident American narrator. Land the last sentence with weight.',
  },
  'half-price-5': {
    text: `Compare any two countries side by side, for free.`,
    instructions: 'Calm, confident American narrator. Warm, inviting.',
  },

  /* ── 04 the dangerous bargain: the trade nobody prices in ── */
  'dangerous-1': {
    text: `The country where your money lasts longest is also one of the least safe on my list.`,
    instructions: 'Calm, confident American narrator. Slightly grave.',
  },
  'dangerous-2': {
    text: `India gives you eleven point one years on a hundred thousand dollars. That is the second longest runway I track.`,
    instructions: 'Calm, confident American narrator. Neutral on the number.',
  },
  'dangerous-3': {
    text: `It also scores four out of ten on safety. Turkey scores three. Colombia scores three. Cheap countries are cheap for reasons.`,
    instructions: 'Calm, confident American narrator. Slow on the last sentence.',
  },
  'dangerous-4': {
    text: `Only thirteen of the seventy four countries I track pass a basic healthcare and safety filter.`,
    instructions: 'Calm, confident American narrator. Matter of fact, slightly weightier.',
  },
  'dangerous-5': {
    text: `Every score is published, free, on the site.`,
    instructions: 'Calm, confident American narrator. Warm, unhurried.',
  },

  /* ── 05 income threshold: flips the question ── */
  'income-1': {
    text: `Everyone asks how much they need saved. That is the wrong question.`,
    instructions: 'Calm, confident American narrator. Confident, slightly provocative.',
  },
  'income-2': {
    text: `Two thousand dollars a month covers a full life in forty nine of the seventy four countries I track.`,
    instructions: 'Calm, confident American narrator. Clear on the numbers.',
  },
  'income-3': {
    text: `A thousand a month covers eleven of them. Three thousand covers sixty seven.`,
    instructions: 'Calm, confident American narrator. Steady rhythm.',
  },
  'income-4': {
    text: `Once your income beats the local cost, your savings stop shrinking. The runway is no longer finite.`,
    instructions: 'Calm, confident American narrator. Let the last sentence breathe.',
  },
  'income-5': {
    text: `Find your own threshold on the free calculator.`,
    instructions: 'Calm, confident American narrator. Warm, inviting.',
  },

  /* ── 06 rent reframe: makes it personal in one sentence ── */
  'rent-1': {
    text: `Whatever you pay in rent is probably an entire life somewhere else.`,
    instructions: 'Calm, confident American narrator. Conversational, a little wry.',
  },
  'rent-2': {
    text: `Batumi, on the Georgian coast, costs three hundred fifty dollars a month. Rent, food, transport. All of it.`,
    instructions: 'Calm, confident American narrator. Slight surprise on the number.',
  },
  'rent-3': {
    text: `A hundred thousand dollars lasts twenty three years there. In a typical American city it lasts two point four.`,
    instructions: 'Calm, confident American narrator. A beat before the last figure.',
  },
  'rent-4': {
    text: `These are real city costs, not national averages. I tracked two hundred twenty two of them.`,
    instructions: 'Calm, confident American narrator. Matter of fact.',
  },
  'rent-5': {
    text: `Check your own city against the list, for free.`,
    instructions: 'Calm, confident American narrator. Warm, unhurried.',
  },
};

/* ── providers ── */
async function openai(text, instructions) {
  const key = cfg.OPENAI_API_KEY;
  if (!key) throw new Error('OPENAI_API_KEY missing in video/.env');
  const r = await fetch('https://api.openai.com/v1/audio/speech', {
    method: 'POST',
    headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'gpt-4o-mini-tts',
      // "onyx" and "ash" read as male American; "nova" female American
      voice: cfg.VOICE_NAME ?? 'ash',
      input: text.replace(/\s+/g, ' ').trim(),
      instructions,
      response_format: 'mp3',
    }),
  });
  if (!r.ok) throw new Error(`OpenAI ${r.status}: ${await r.text()}`);
  return Buffer.from(await r.arrayBuffer());
}

async function elevenlabs(text) {
  const key = cfg.ELEVENLABS_API_KEY;
  if (!key) throw new Error('ELEVENLABS_API_KEY missing in video/.env');
  // default: "Adam" - natural American male. Override with VOICE_ID.
  const voiceId = cfg.VOICE_ID ?? 'pNInz6obpgDQGcFmaJgB';
  const r = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`, {
    method: 'POST',
    headers: { 'xi-api-key': key, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: text.replace(/\s+/g, ' ').trim(),
      model_id: cfg.ELEVEN_MODEL ?? 'eleven_multilingual_v2',
      voice_settings: { stability: 0.45, similarity_boost: 0.75, style: 0.35, use_speaker_boost: true },
    }),
  });
  if (!r.ok) throw new Error(`ElevenLabs ${r.status}: ${await r.text()}`);
  return Buffer.from(await r.arrayBuffer());
}

/* ── run ── */
const only = process.argv.find(a => !a.startsWith('-') && SCRIPTS[a]);
const targets = only ? [only] : Object.keys(SCRIPTS);

mkdirSync(OUT, { recursive: true });
console.log(`provider: ${PROVIDER}\n`);

for (const id of targets) {
  const { text, instructions } = SCRIPTS[id];
  const file = join(OUT, `${id}.mp3`);
  try {
    const buf = PROVIDER === 'elevenlabs'
      ? await elevenlabs(text)
      : await openai(text, instructions);
    writeFileSync(file, buf);
    const chars = text.replace(/\s+/g, ' ').trim().length;
    console.log(`${id}.mp3  ${Math.round(buf.length / 1024)} KB  (${chars} chars)`);
  } catch (e) {
    console.error(`${id}: ${e.message}`);
  }
}

// Manifest so compositions can render without the audio file and not crash.
const made = targets.filter(id => existsSync(join(OUT, `${id}.mp3`)));
writeFileSync(join(OUT, 'available.json'), JSON.stringify(made, null, 2));
console.log(`\ndone -> ${OUT}/  (${made.length} tracks)`);
