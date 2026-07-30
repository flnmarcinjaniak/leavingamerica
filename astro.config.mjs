import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { COMPARE_PAIRS } from './src/data/compare-pairs.mjs';

// Reversed-order compare slugs are redirect stubs; the sitemap must list only canonical pages.
const CANONICAL_COMPARE = new Set(COMPARE_PAIRS);
const isCompareRedirect = (page) => {
  const m = page.match(/\/compare\/([^/]+)\/?$/);
  return m ? !CANONICAL_COMPARE.has(m[1]) : false;
};

export default defineConfig({
  output: 'static',
  site: 'https://leavingamerica.co',
  trailingSlash: 'always',
  integrations: [
    sitemap({
      changefreq: 'weekly',
      priority: 0.7,
      lastmod: new Date(),
      customPages: [],
      filter: (page) => !page.includes('/404') && !isCompareRedirect(page),
      serialize(item) {
        // Higher priority for main tools and hub pages
        if (item.url === 'https://leavingamerica.co/') {
          return { ...item, priority: 1.0, changefreq: 'daily' };
        }
        if (
          item.url.includes('/fire') ||
          item.url.includes('/country-match') ||
          item.url.includes('/countries') ||
          item.url.includes('/taxes')
        ) {
          return { ...item, priority: 0.9, changefreq: 'weekly' };
        }
        if (item.url.includes('/countries/goals/')) {
          return { ...item, priority: 0.8, changefreq: 'weekly' };
        }
        return { ...item, priority: 0.6, changefreq: 'monthly' };
      },
    }),
  ],
});
