/* Sentinel : l'affichage sous 200 ms, et ce qui l'en empêchait.
 *
 * CE QU'ON PROTÈGE, ET LA FAUTE QUE CHAQUE CONTRÔLE EMPÊCHE :
 *
 *   1. L'AFFICHAGE INITIAL. Le premier pixel doit arriver sous 200 ms une fois
 *      connecté. Il arrivait après 5,2 secondes.
 *   2. LE SERVEUR NE SE DÉGRADE PAS SOUS UNE RAFALE. C'est le contrôle qui
 *      compte : une connexion de base abandonnée sur un chemin d'erreur gardait
 *      le verrou d'écriture, et TOUTES les requêtes suivantes du processus
 *      attendaient cinq secondes avant d'échouer — puis fuyaient à leur tour.
 *      Un incident ponctuel devenait permanent. Une moyenne sur une seule
 *      requête ne l'aurait jamais vu : il faut mesurer la DÉRIVE.
 *   3. L'IDENTIFIANT INVARIANT N'EST PLUS RELU À CHAQUE FOIS. Dix requêtes par
 *      affichage, dix allers-retours de base pour la même réponse.
 *   4. CHAQUE PAGE DU MENU S'AFFICHE SOUS 200 ms, à froid comme à chaud.
 *
 *     BASE=http://127.0.0.1:5510 node recette_perf_sentinel.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5510';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
const BUDGET = 200;
let ko = 0;
const ok = (n, c, d) => { console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : '')); if (!c) ko++; };
const titre = t => console.log('\n══ ' + t + ' ══\n');

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1500, height: 1000 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e).slice(0, 120)));
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.waitForTimeout(400);

  // ── 1 ────────────────────────────────────────────────────────────────────
  titre('1. L’affichage initial de /sentinel');

  const rep = await pg.goto(BASE + '/sentinel', { waitUntil: 'domcontentloaded' });
  ok('la page répond', rep && rep.status() === 200,
     rep ? 'HTTP ' + rep.status() : 'pas de réponse');
  if (!rep || rep.status() !== 200) { await nav.close(); process.exit(2); }
  await pg.waitForTimeout(3500);

  const t = await pg.evaluate(() => {
    const n = performance.getEntriesByType('navigation')[0];
    const fcp = performance.getEntriesByName('first-contentful-paint')[0];
    return {
      ttfb: Math.round(n.responseStart - n.requestStart),
      fcp: fcp ? Math.round(fcp.startTime) : null
    };
  });
  ok('le serveur répond son premier octet sous 200 ms', t.ttfb < BUDGET, t.ttfb + ' ms');
  /* LE FCP EST LA MESURE DE « L'AFFICHAGE ». `load` attend aussi les polices
     Google et les modules préchargés en arrière-plan : le retenir mesurerait
     le réseau d'un tiers, pas la page. */
  ok('le premier contenu est peint sous 200 ms', t.fcp !== null && t.fcp < BUDGET,
     t.fcp + ' ms');

  // ── 2 ────────────────────────────────────────────────────────────────────
  titre('2. Le corps de la page n’est pas retéléchargé à chaque affichage');

  const revisite = await pg.evaluate(async () => {
    const t0 = performance.now();
    const r = await fetch('/sentinel', { credentials: 'same-origin' });
    await r.text();
    return { ms: Math.round(performance.now() - t0), statut: r.status };
  });
  /* LE STATUT FAIT PARTIE DU CONTRÔLE. Sans lui, la mesure était verte sur un
     429 : le limiteur de débit, déclenché par la rafale et les cent bascules
     qui précèdent, répond très vite — et une erreur rapide passait pour une
     page rapide. Un contrôle de performance qui accepte une page d'erreur ne
     mesure plus rien. */
  ok('une nouvelle demande de /sentinel aboutit',
     revisite.statut === 200 || revisite.statut === 304,
     'HTTP ' + revisite.statut);
  ok('…et elle revient sous 200 ms',
     (revisite.statut === 200 || revisite.statut === 304) && revisite.ms < BUDGET,
     revisite.ms + ' ms');

  // ── 2 : LE POINT QUI DÉCIDE ──────────────────────────────────────────────
  titre('3. LE POINT QUI DÉCIDE : le serveur ne se dégrade pas sous une rafale');

  /* Trente appels authentifiés d'affilée. La panne d'origine ne se voyait pas
     sur le premier — elle apparaissait dès qu'une requête avait échoué en
     laissant le verrou : les suivantes prenaient cinq secondes CHACUNE. On
     compare donc le dernier tiers au premier. */
  const rafale = await pg.evaluate(async () => {
    const t = [];
    for (let i = 0; i < 30; i++) {
      const t0 = performance.now();
      await fetch('/api/sentinel-auth/me', { credentials: 'same-origin' }).catch(() => {});
      t.push(performance.now() - t0);
    }
    const moy = a => a.reduce((x, y) => x + y, 0) / a.length;
    return { debut: moy(t.slice(0, 10)), fin: moy(t.slice(-10)), max: Math.max(...t) };
  });
  ok('les dix premiers appels sont rapides', rafale.debut < BUDGET,
     Math.round(rafale.debut) + ' ms en moyenne');
  ok('LES DIX DERNIERS LE SONT AUTANT — aucune dérive', rafale.fin < BUDGET,
     Math.round(rafale.fin) + ' ms en moyenne');
  ok('…et aucun appel isolé ne part en attente de verrou', rafale.max < 1000,
     'pire appel : ' + Math.round(rafale.max) + ' ms');
  /* Le rapport fin/début est le vrai signal : une fuite de connexion fait
     exploser ce rapport, une machine lente le laisse à 1. */
  const derive = rafale.fin / Math.max(rafale.debut, 0.5);
  ok('…le dernier tiers ne coûte pas plus cher que le premier', derive < 3,
     '×' + derive.toFixed(2));

  // ── 3 ────────────────────────────────────────────────────────────────────
  titre('4. Toutes les pages du menu, à froid puis à chaud');

  const cibles = await pg.evaluate(() => [...document.querySelectorAll('.sb-item')]
    .map(x => { const m = /go\('([a-z0-9-]+)'/.exec(x.getAttribute('onclick') || ''); return m ? m[1] : null; })
    .filter(Boolean));
  ok('le menu est armé', cibles.length >= 20, cibles.length + ' page(s)');

  const froid = [];
  for (const c of cibles) {
    const ms = await pg.evaluate(async (cle) => {
      const t0 = performance.now();
      window.go(cle, null, 'X', 'Y');
      await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
      return performance.now() - t0;
    }, c);
    froid.push({ c: c, ms: Math.round(ms) });
  }
  const lentsFroid = froid.filter(x => x.ms >= BUDGET);
  ok('AUCUNE page ne dépasse 200 ms à sa PREMIÈRE ouverture',
     lentsFroid.length === 0,
     lentsFroid.map(x => x.c + ' (' + x.ms + ' ms)').join(', '));
  const pireFroid = froid.reduce((a, b) => a.ms > b.ms ? a : b, { ms: 0, c: '' });
  console.log('       la plus lente à froid : ' + pireFroid.c + ' — ' + pireFroid.ms + ' ms');

  const chaud = [];
  for (const c of cibles) {
    const ms = await pg.evaluate(async (cle) => {
      const t0 = performance.now();
      window.go(cle, null, 'X', 'Y');
      await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
      return performance.now() - t0;
    }, c);
    chaud.push({ c: c, ms: Math.round(ms) });
  }
  const lentsChaud = chaud.filter(x => x.ms >= BUDGET);
  ok('AUCUNE page ne dépasse 200 ms à la seconde ouverture',
     lentsChaud.length === 0,
     lentsChaud.map(x => x.c + ' (' + x.ms + ' ms)').join(', '));

  // ── LE PREMIER VISITEUR APRÈS UN RÉVEIL ────────────────────────────────
  titre('5. Le TOUT PREMIER affichage ne paie pas la compression');
  /* CE QUE CE CONTRÔLE EMPÊCHE DE REVENIR. Le cache de pages était construit à
     la première requête qui réclamait la page : cette requête-là payait la
     lecture, l'enrichissement et la compression gzip niveau 9 de deux
     méga-octets. MESURÉ : 303 ms de premier octet, contre 5 ms ensuite.
     Ce n'était pas une fois pour toutes mais une fois PAR PROCESSUS — donc
     après chaque déploiement et après chaque réveil d'une instance endormie.
     Sur un hébergement qui endort les instances inactives, le premier visiteur
     payait systématiquement. Le cache est désormais construit au démarrage, en
     tâche de fond.

     ON NE PEUT PAS REDÉMARRER LE SERVEUR DEPUIS ICI : on mesure donc ce qui
     reste observable — une page LOURDE et JAMAIS DEMANDÉE dans cette session
     doit répondre aussi vite qu'une page déjà servie. Si le préchauffage
     n'avait pas eu lieu, elle paierait sa compression maintenant. */
  const froides = await pg.evaluate(async () => {
    const t = async (u) => { const d = performance.now();
      await fetch(u, { credentials: 'same-origin', cache: 'no-store' });
      return Math.round(performance.now() - d); };
    // Une page lourde qu'aucun contrôle précédent n'a demandée.
    return { jamaisVue: await t('/observatoire'), dejaVue: await t('/sentinel') };
  });
  ok('une page LOURDE jamais demandée répond sous 200 ms',
     froides.jamaisVue < BUDGET, froides.jamaisVue + ' ms');
  ok('…aussi vite qu’une page déjà servie — le cache était prêt AVANT la visite',
     froides.jamaisVue < froides.dejaVue + 120,
     'jamais vue ' + froides.jamaisVue + ' ms · déjà vue ' + froides.dejaVue + ' ms');

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
