// Canonical compare-page pairs, single source of truth.
// Used by src/pages/compare/[pair].astro (page + reversed-slug redirect generation)
// and by astro.config.mjs (sitemap filter: redirect stubs must stay out of the sitemap).
export const COMPARE_PAIRS = [
  'portugal-vs-spain','spain-vs-italy','portugal-vs-italy',
  'greece-vs-spain','greece-vs-portugal','malta-vs-cyprus',
  'croatia-vs-greece','croatia-vs-portugal',
  'mexico-vs-costa-rica','mexico-vs-panama','costa-rica-vs-panama',
  'mexico-vs-portugal','colombia-vs-mexico','ecuador-vs-colombia',
  'argentina-vs-chile','argentina-vs-uruguay','belize-vs-costa-rica',
  'nicaragua-vs-costa-rica','dominican-republic-vs-mexico',
  'thailand-vs-vietnam','thailand-vs-malaysia','vietnam-vs-philippines',
  'thailand-vs-philippines','malaysia-vs-indonesia','thailand-vs-portugal',
  'cambodia-vs-thailand','cambodia-vs-vietnam',
  'poland-vs-czech-republic','hungary-vs-poland','romania-vs-bulgaria',
  'czech-republic-vs-hungary','croatia-vs-slovenia','estonia-vs-lithuania',
  'latvia-vs-lithuania','albania-vs-montenegro','georgia-vs-turkey',
  'france-vs-spain','france-vs-italy','netherlands-vs-germany',
  'ireland-vs-united-kingdom','canada-vs-australia','australia-vs-new-zealand',
  'portugal-vs-costa-rica','spain-vs-mexico','panama-vs-portugal',
  'thailand-vs-mexico',
  'georgia-vs-portugal','taiwan-vs-south-korea','japan-vs-south-korea',
  'singapore-vs-malaysia','united-arab-emirates-vs-singapore',
  'south-africa-vs-portugal','morocco-vs-spain','kenya-vs-south-africa',
  'turkey-vs-greece',
];
