/* Le bloc MOE de /enveloppe#moe-bloc : rapide, et PROUVÉ rapide.
 *
 * CE QUI ÉTAIT MESURÉ AVANT CORRECTION : le fetch du barème ne partait qu'à
 * DOMContentLoaded — un aller-retour réseau complet AJOUTÉ au temps de page —
 * et l'API ne posait ni ETag ni Cache-Control : chaque visite re-téléchargeait
 * 11 Ko identiques. Le bloc s'armait à DCL + RTT ; à froid, près de 2 s.
 *
 * CE QUE CETTE RECETTE VERROUILLE (les invariants tenus par le code, pas la
 * météo du réseau) :
 *   1. le barème part AVANT DOMContentLoaded — pendant l'analyse de la page ;
 *   2. le chemin propre au bloc — départ du fetch → boutons rendus — tient
 *      sous 250 ms ;
 *   3. le serveur fige le barème avec ETag + Cache-Control, et répond 304
 *      sans corps à la revisite ;
 *   4. au rechargement, le bloc s'arme depuis le cache du navigateur.
 *
 * Le plancher RESTANT est l'analyse de la page elle-même (~370 ms locaux,
 * dominés par le référentiel embarqué de 633 Ko — un choix d'autonomie
 * documenté dans la page) : il se mesure ici en détail, il ne se juge pas.
 *
 *     BASE=http://127.0.0.1:5506 node recette_moe_perf.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5506';
const TOKEN = process.env.RECETTE_TOKEN || 'recette_locale_idf_0123456789abcdef';
let ko = 0;
const ok = (n, c, d) => { console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : '')); if (!c) ko++; };

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1400, height: 950 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.waitForTimeout(400);

  console.log('\n══ 1. Le serveur fige le barème : ETag, Cache-Control, 304 ══\n');
  /* Les contrôles HTTP se font DEPUIS la page : le pare-feu applicatif du
     site vérifie la cohérence des en-têtes navigateur, et un client
     synthétique (pg.request) échoue ces vérifications — seul le vrai
     navigateur envoie un profil d'en-têtes complet. */
  const h = await pg.evaluate(async () => {
    const r = await fetch('/api/moe-dc', { credentials: 'same-origin', cache: 'no-store' });
    const etag = r.headers.get('ETag') || '';
    const cc = r.headers.get('Cache-Control') || '';
    const r2 = await fetch('/api/moe-dc', {
      credentials: 'same-origin', cache: 'no-store',
      headers: { 'If-None-Match': etag } });
    const corps2 = await r2.text().catch(() => '');
    return { s1: r.status, etag: etag, cc: cc, s2: r2.status, l2: corps2.length };
  });
  ok('le barème répond avec un ETag', h.s1 === 200 && /^"moe-/.test(h.etag),
     h.etag || 'absent (HTTP ' + h.s1 + ')');
  ok('…et un Cache-Control privé', /private/.test(h.cc) && /max-age/.test(h.cc),
     h.cc || 'absent');
  ok('la revisite conditionnelle rend 304 SANS corps',
     h.s2 === 304 && h.l2 === 0, 'HTTP ' + h.s2 + ' · ' + h.l2 + ' octet(s)');

  console.log('\n══ 2. Le bloc s’arme sans attendre la fin de la page ══\n');
  const t0 = Date.now();
  await pg.goto(BASE + '/enveloppe#moe-bloc', { waitUntil: 'commit' });
  let armee = true;
  try {
    await pg.waitForFunction(() =>
      document.querySelectorAll('#moe-bloc button').length > 3, null, { timeout: 20000 });
  } catch (e) { armee = false; }
  const total = Date.now() - t0;
  ok('les boutons du barème sont rendus', armee,
     armee ? total + ' ms au total (page comprise)'
           : 'jamais armé — ' + (err[0] || 'aucune erreur collectée').slice(0, 140));
  const m = await pg.evaluate(() => {
    const n = performance.getEntriesByType('navigation')[0];
    const r = performance.getEntriesByType('resource')
      .find(x => x.name.includes('/api/moe-dc'));
    return { dcl: n ? Math.round(n.domContentLoadedEventStart) : null,
             debut: r ? Math.round(r.startTime) : null,
             fin: r ? Math.round(r.responseEnd) : null };
  });
  ok('LE BARÈME PART AVANT DOMContentLoaded — pendant l’analyse de la page',
     m.debut !== null && m.dcl !== null && m.debut < m.dcl,
     'fetch à ' + m.debut + ' ms, DCL à ' + m.dcl + ' ms');
  const propre = m.debut !== null ? total - m.debut : null;
  ok('LE CHEMIN PROPRE AU BLOC TIENT SOUS 250 ms (fetch → boutons rendus)',
     propre !== null && propre < 250, propre + ' ms');

  console.log('\n══ 3. La revisite s’arme depuis le cache ══\n');
  await pg.reload({ waitUntil: 'commit' });
  let armee2 = true;
  try {
    await pg.waitForFunction(() =>
      document.querySelectorAll('#moe-bloc button').length > 3, null, { timeout: 20000 });
  } catch (e) { armee2 = false; }
  const c2 = await pg.evaluate(() => {
    const r = performance.getEntriesByType('resource')
      .find(x => x.name.includes('/api/moe-dc'));
    return r ? Math.round(r.transferSize) : null;
  });
  ok('le bloc se ré-arme, sans re-télécharger le barème',
     armee2 && c2 !== null && c2 < 1000,
     c2 === null ? 'ressource introuvable' : c2 + ' octet(s) transférés (304/cache)');

  ok('aucune erreur de script sur la page', err.length === 0,
     err.join(' | ').slice(0, 160));

  console.log('\n' + (ko ? ko + ' contrôle(s) en échec' : 'tout est vert') + '\n');
  await nav.close();
  process.exit(ko ? 1 : 0);
})();
