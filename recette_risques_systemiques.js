/* RECETTE — LES HUIT RISQUES SYSTÉMIQUES MÈNENT À LEUR MODULE
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE : « faire pareil pour les 8 risques systémiques IA que nous
 * adressons dans Sentinel » — après les six offres de services.
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
 *   1-3.   Les neuf liens — huit cartes plus la bannière — existent après le
 *          chargement, et survivent à un changement de langue dans les deux sens.
 *   4-6.   Chacun mène vers /sentinel, et les huit visent huit modules différents.
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
  const sec = document.getElementById('risques');
  if (!sec) return { err: 'section #risques absente' };
  const cartes = [...sec.querySelectorAll('.risk-card')];
  return {
    cartes: cartes.length,
    appels: [...sec.querySelectorAll('a.risk-go')].map(a => ({
      href: a.getAttribute('href'), texte: a.textContent.trim(),
      title: a.getAttribute('title') || '',
      dansUnLien: !!a.parentElement.closest('a')
    })),
    banniere: (() => {
      const b = sec.querySelector('.risk-cta-banner a');
      return b ? { href: b.getAttribute('href'),
                   title: b.getAttribute('title') || '' } : null;
    })(),
    /* L'ÉTIQUETTE DE CATÉGORIE NE DOIT PAS ÊTRE DEVENUE UN LIEN.
       Depuis que la carte entière se clique, « Sécurité » ou « ESG » font
       partie de la surface qui ouvre le module — c'est voulu. Ce qu'on
       refuse, c'est qu'elles deviennent des LIENS : soulignées au survol,
       annoncées comme destinations par un lecteur d'écran, ouvrables dans
       un nouvel onglet, pour une classification qui ne mène nulle part.
       C'est la raison pour laquelle la carte n'a pas été enveloppée dans un
       <a> et porte une surface étirée à la place. */
    tagsCliquables: [...sec.querySelectorAll('.risk-tag')]
      .filter(t => !!t.closest('a')).length
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
  ok('les huit risques sont là', R.cartes === 8, '', R.cartes + ' cartes');
  ok('les huit appels ont survécu au chargement', R.appels.length === 8,
     'applyLang les a effacés', R.appels.length + ' appels');
  ok('la bannière de pied vise le radar, et plus l’accueil',
     R.banniere && R.banniere.href === '/sentinel?goto=radar',
     R.banniere ? R.banniere.href : 'bannière absente',
     R.banniere ? R.banniere.href : '');
  ok('aucun lien n’est imbriqué dans un autre',
     R.appels.every(a => !a.dansUnLien),
     'un <a> dans un <a> : le navigateur défait l’imbrication');
  ok('les étiquettes de catégorie ne sont pas devenues des LIENS',
     R.tagsCliquables === 0,
     R.tagsCliquables + ' étiquette(s) dans un lien');

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
  ok('les liens survivent au passage en anglais', EN.appels.length === 8,
     EN.appels.length + ' appels', (EN.appels[0] || {}).texte || '');
  const FR = await bascule('fr');
  ok('et au retour en français', FR.appels.length === 8,
     FR.appels.length + ' appels', (FR.appels[0] || {}).texte || '');

  /* ── 4-6. OÙ ILS MÈNENT ───────────────────────────────────────────── */
  /* UNE DESTINATION EST UN COUPLE (PAGE, POINT) : `?point=` nomme l'endroit
     de la page où le visiteur doit arriver. Un motif qui ne connaîtrait que
     `?goto=` rejetterait le lien le plus précis des huit. */
  const FORME = /^\/sentinel\?goto=[a-z0-9-]+(?:&point=[A-Za-z0-9_-]+)?$/;
  const tous = R.appels.slice();
  ok('chaque lien vise /sentinel avec sa destination',
     tous.every(a => FORME.test(a.href)),
     tous.filter(a => !FORME.test(a.href)).map(a => a.href).join(', '),
     tous.length + ' liens');
  const cibles = R.appels.map(a => a.href.replace('/sentinel?goto=', '')
                                         .split('&')[0]);
  const endroits = R.appels.map(a => a.href.replace('/sentinel?goto=', ''));
  ok('les huit risques déposent le visiteur à huit ENDROITS différents',
     new Set(endroits).size === 8, endroits.join(', '), endroits.join(' · '));

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
  /* ON SUIT CELUI QUI VISE UN POINT, PAS LE PREMIER VENU. Un lien `?goto=`
     nu prouve qu'une page s'ouvre ; seul un lien `?point=` prouve qu'on
     arrive SUR ce que la carte annonçait — et c'est là qu'était le défaut :
     la page s'ouvrait, l'item promis restait introuvable. */
  const avecPoint = R.appels.find(a => a.href.indexOf('&point=') > 0);
  const suivi = avecPoint ? avecPoint.href.replace('/sentinel?goto=', '')
                          : cibles[0];
  const temoin = suivi.split('&')[0];
  const point = avecPoint ? avecPoint.href.split('&point=')[1] : null;
  const r1 = await pg.goto(BASE + '/sentinel?goto=' + suivi,
                           { waitUntil: 'domcontentloaded' });
  ok('la page Sentinel répond au lien d\u2019un risque',
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

  /* ── LE POINT PROMIS EST-IL SOUS LES YEUX DU VISITEUR ? ───────────── */
  if (point) {
    const p = await pg.evaluate((id) => {
      const el = document.getElementById(id);
      if (!el) return { absent: true };
      const b = el.getBoundingClientRect();
      return { texte: el.textContent.replace(/\s+/g, ' ').trim().slice(0, 60),
               visible: el.checkVisibility({ checkVisibilityCSS: true,
                 contentVisibilityAuto: true, opacityProperty: true,
                 visibilityProperty: true }),
               dansLEcran: b.top > -5 && b.bottom < window.innerHeight + 5,
               souligne: el.classList.contains('vise') };
    }, point);
    ok('le point promis par la carte est À L\u2019ÉCRAN, et désigné',
       !p.absent && p.visible && p.dansLEcran && p.souligne,
       JSON.stringify(p), p.texte || '');
    /* ET UN POINT INCONNU NE DOIT PAS EMPORTER LA PAGE AVEC LUI. */
    const apres = await pg.evaluate((c) => {
      try { window.sentinelPointer('point-qui-n-existe-pas'); } catch (e) {
        return 'le pointage a levé : ' + e; }
      const pa = document.getElementById('p-' + c);
      return pa ? pa.checkVisibility({ checkVisibilityCSS: true,
        contentVisibilityAuto: true, opacityProperty: true,
        visibilityProperty: true }) : 'panneau perdu';
    }, temoin);
    ok('un point inconnu renonce en silence, la page reste ouverte',
       apres === true, String(apres));
  }

  const autres = await pg.evaluate((cs) => cs.map(c => {
    const p = document.getElementById('p-' + c);
    const onglet = [...document.querySelectorAll('.sb-item')].some(
      i => (i.getAttribute('onclick') || '').indexOf("go('" + c + "'") >= 0);
    return { c: c, panneau: !!p, onglet: onglet };
  }), cibles.filter(c => c !== temoin));
  ok('les autres destinations sont des panneaux réels de cette page',
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
    const a = document.querySelector('#risques a.risk-go');
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
    const a = document.querySelector('#risques a.risk-go');
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
