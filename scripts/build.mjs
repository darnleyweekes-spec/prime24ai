import { cp, mkdir, rm } from 'node:fs/promises';

// Pages serves these files directly. Preserve their URLs and classic script semantics.
const entries = [
  '.nojekyll', 'CNAME', 'index.html', 'styles.css', 'app.js', 'alpha.js',
  'analytics.js', 'favicon.svg', 'robots.txt', 'sitemap.xml', 'assets',
  'contact', 'faq', 'follow-up', 'how-it-works', 'pilot', 'proposals',
  'vendor-packet-rescue',
];

await rm('dist', { recursive: true, force: true });
await mkdir('dist');
for (const entry of entries) {
  await cp(entry, `dist/${entry}`, { recursive: true });
}
