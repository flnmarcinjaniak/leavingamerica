import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

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
      filter: (page) => !page.includes('/404'),
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
