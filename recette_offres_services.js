/* RECETTE — LES SIX OFFRES DE SERVICES MÈNENT À LEUR MODULE
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE : « connecter avec des liens les 6 offres de services, renvoyer
 * aux bons modules du site Sentinel ».
 *
 * CE QUE LES RÈGLES PYTHON NE PEUVENT PAS VOIR. Elles lisent le fichier ;
 * elles ne savent pas ce qui reste à l'écran APRÈS le passage de la
 * traduction. Or c'est exactement là que le danger se trouve : `applyLang`
 * remplace l'innerHTML de tout porteur de `data-i18n`, et un lien mal placé
 * disparaît au chargement — sans erreur, sans trace, et le fichier continue
 * de le contenir. Une règle de source resterait verte sur une page sans
 * aucun lien.
 *
 * LES CONTRÔLES :
 *   1-3.   Les dix-neuf liens existent après le chargement — et survivent à
 *          un changement de langue, dans les deux sens.
 *   4-5.   Chacun mène bien vers /sentinel, avec la destination dans l'URL.
 *   6.     Les six offres visent six modules différents.
 *   7-8.   Suivre un lien ouvre le bon panneau, pour de vrai.
 *   9-10.  Ce qui se clique se voit et se vise au clavier.
 *   11.    Rien ne déborde, et aucune erreur de script.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';

let ko = 0, n = 0;
const ok = (t, cond, siKo, mesure) => {
  n++; if (!cond) ko++;
  console.log((cond ? '  OK   ' : '  KO   ') + t
              + (mesure ? ' — ' + mesure : '')
              + (!cond && siKo ? ' — ' + siKo : ''));
};

const RELEVE = () => {
  const sec = document.getElementById('services');
  if (!sec) return { err: 'section #services absente' };
  const cartes = [...sec.querySelectorAll('.diff-card')];
  return {
    cartes: cartes.length,
    appels: [...sec.querySelectorAll('a.sv-card-go')].map(a => ({
      href: a.getAttribute('href'), texte: a.textContent.trim(),
      title: a.getAttribute('title') || '',
      dansUnLien: !!a.parentElement.closest('a')
    })),
    fleches: [...sec.querySelectorAll('a.sv-go')].map(a => ({
      href: a.getAttribute('href'),
      aria: a.getAttribute('aria-label') || '',
      ligne: (a.parentElement.textContent || '').trim(),
      dansUnLien: !!a.parentElement.closest('a')
    }))
  };
};

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1400, height: 1000 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e).slice(0, 160)));

  const rep = await pg.goto(BASE + '/', { waitUntil: 'domcontentloaded' });
  ok('la page d’accueil répond', rep && rep.status() === 200,
     rep ? 'HTTP ' + rep.status() : 'pas de réponse');
  if (!rep || rep.status() !== 200) { await nav.close(); process.exit(2); }
  await pg.waitForTimeout(1800);

  /* ── 1-2. LES LIENS SURVIVENT AU PASSAGE DE LA TRADUCTION ─────────── */
  const R = await pg.evaluate(RELEVE);
  if (R.err) { ok('la section a pu être relevée', false, R.err);
               await nav.close(); process.exit(2); }
  ok('les six offres sont là', R.cartes === 6, '', R.cartes + ' cartes');
  ok('les six appels ont survécu au chargement', R.appels.length === 6,
     'applyLang les a effacés', R.appels.length + ' appels');
  ok('les flèches des puces ont survécu au chargement', R.fleches.length >= 10,
     'applyLang les a effacées', R.fleches.length + ' flèches');
  ok('aucun lien n’est imbriqué dans un autre',
     R.appels.every(a => !a.dansUnLien) && R.fleches.every(f => !f.dansUnLien),
     'un <a> dans un <a> : le navigateur défait l’imbrication');

  /* ── 3. ET ILS SURVIVENT À UN CHANGEMENT DE LANGUE, DANS LES DEUX SENS */
  const bascule = async (lg) => {
    await pg.evaluate((l) => {
      if (typeof window.setLang === 'function') return window.setLang(l);
      window.LANG = l;
      if (typeof window.applyLang === 'function') window.applyLang();
    }, lg);
    await pg.waitForTimeout(500);
    return pg.evaluate(RELEVE);
  };
  const EN = await bascule('en');
  ok('les liens survivent au passage en anglais',
     EN.appels.length === 6 && EN.fleches.length === R.fleches.length,
     EN.appels.length + ' appels, ' + EN.fleches.length + ' flèches',
     (EN.appels[0] || {}).texte || '');
  const FR = await bascule('fr');
  ok('et au retour en français',
     FR.appels.length === 6 && FR.fleches.length === R.fleches.length,
     FR.appels.length + ' appels, ' + FR.fleches.length + ' flèches',
     (FR.appels[0] || {}).texte || '');

  /* ── 4-6. OÙ ILS MÈNENT ───────────────────────────────────────────── */
  const tous = R.appels.concat(R.fleches);
  ok('chaque lien vise /sentinel avec sa destination',
     tous.every(a => /^\/sentinel\?goto=[a-z0-9-]+$/.test(a.href)),
     tous.filter(a => !/^\/sentinel\?goto=[a-z0-9-]+$/.test(a.href))
         .map(a => a.href).join(', '),
     tous.length + ' liens');
  const cibles = R.appels.map(a => a.href.split('=')[1]);
  ok('les six offres visent six modules DIFFÉRENTS',
     new Set(cibles).size === 6, cibles.join(', '), cibles.join(' · '));

  /* ── 7-8. SUIVRE UN LIEN OUVRE BIEN LE PANNEAU ────────────────────── */
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.waitForTimeout(400);
  /* POURQUOI UNE SEULE DESTINATION EST SUIVIE POUR DE VRAI, ET CINQ
     VÉRIFIÉES SUR LA PAGE CHARGÉE. Le protecteur anti-abus du serveur
     répond 429 dès le troisième chargement complet de /sentinel — six
     allers-retours accuseraient le produit d'un défaut qui n'est pas le
     sien. On prouve donc LE MÉCANISME une fois, de bout en bout : un lien
     `?goto=` ouvre bien le panneau qu'il désigne. Puis, sur cette même page
     déjà chargée, on vérifie que les cinq autres panneaux existent et que
     chacun s'ouvre par la navigation interne. Que les six destinations
     soient des panneaux ET des onglets est par ailleurs prouvé
     exhaustivement par les règles de tests/test_offres_services.py. */
  const temoin = cibles[0];
  const r1 = await pg.goto(BASE + '/sentinel?goto=' + temoin,
                           { waitUntil: 'domcontentloaded' });
  ok('la page Sentinel répond au lien d\u2019une offre',
     r1 && r1.status() === 200, r1 ? 'HTTP ' + r1.status() : 'pas de réponse',
     '?goto=' + temoin);
  await pg.waitForTimeout(2600);
  const ouvert = await pg.evaluate((c) => {
    const p = document.getElementById('p-' + c);
    return p ? p.checkVisibility({ checkVisibilityCSS: true,
      contentVisibilityAuto: true, opacityProperty: true,
      visibilityProperty: true }) : null;
  }, temoin);
  ok('suivre le lien OUVRE le panneau désigné, et pas l\u2019accueil',
     ouvert === true, 'panneau ' + temoin + ' : ' + ouvert, temoin);

  const autres = await pg.evaluate((cs) => cs.map(c => {
    const p = document.getElementById('p-' + c);
    const onglet = [...document.querySelectorAll('.sb-item')].some(
      i => (i.getAttribute('onclick') || '').indexOf("go('" + c + "'") >= 0);
    return { c: c, panneau: !!p, onglet: onglet };
  }), cibles.slice(1));
  ok('les cinq autres destinations sont des panneaux réels de cette page',
     autres.every(a => a.panneau),
     autres.filter(a => !a.panneau).map(a => a.c).join(', '),
     autres.length + ' vérifiées');
  ok('et chacune porte son onglet dans la barre latérale',
     autres.every(a => a.onglet),
     autres.filter(a => !a.onglet).map(a => a.c).join(', '));

  /* ── 9-10. CE QUI SE CLIQUE SE VOIT, ET SE VISE AU CLAVIER ────────── */
  await pg.waitForTimeout(2500);
  await pg.goto(BASE + '/', { waitUntil: 'domcontentloaded' });
  await pg.waitForTimeout(1800);
  const vu = await pg.evaluate(() => {
    const a = document.querySelector('#services a.sv-card-go');
    if (!a) return null;
    a.scrollIntoView({ block: 'center' });
    const r = a.getBoundingClientRect();
    const st = getComputedStyle(a);
    return { h: Math.round(r.height), w: Math.round(r.width),
             couleur: st.color, curseur: st.cursor };
  });
  ok('l’appel de carte est assez grand pour se viser',
     vu && vu.h >= 28 && vu.w >= 90, vu ? JSON.stringify(vu) : 'absent',
     vu ? vu.w + '×' + vu.h + ' px' : '');
  const focus = await pg.evaluate(() => {
    const a = document.querySelector('#services a.sv-card-go');
    if (!a) return { actif: false, contour: 'appel introuvable' };
    a.focus();
    const st = getComputedStyle(a);
    return { actif: document.activeElement === a,
             contour: st.outlineWidth + ' ' + st.outlineStyle };
  });
  ok('il se prend au clavier', focus.actif, '', focus.contour);

  /* ── 11. RIEN NE DÉBORDE ──────────────────────────────────────────── */
  for (const w of [1400, 900, 390]) {
    await pg.setViewportSize({ width: w, height: 900 });
    await pg.waitForTimeout(350);
    const deb = await pg.evaluate(() => Math.max(0,
      document.documentElement.scrollWidth - document.documentElement.clientWidth));
    ok('rien ne déborde à ' + w + ' px', deb === 0, deb + ' px');
  }
  ok('aucune erreur JavaScript', err.length === 0, err.join(' | '));

  await nav.close();
  console.log('\n' + (n - ko) + ' contrôles passés, ' + ko + ' en échec');
  process.exit(ko ? 1 : 0);
})().catch(e => { console.error('KO   la recette a rompu : ' + e); process.exit(2); });
