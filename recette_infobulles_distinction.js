/* RECETTE — LES SIX INFOBULLES DE « CE QUI NOUS DISTINGUE » S'AFFICHENT
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE : « mettre des infobulles sur les 6 cartes de CE QUI NOUS
 * DISTINGUE ».
 *
 * POURQUOI CETTE RECETTE EXISTE. Les règles Python lisent les fichiers :
 * elles voient l'attribut, le dictionnaire, la boucle de traduction et la
 * géométrie déclarée. Elles ne voient pas ce que l'écran rend — et c'est
 * précisément là qu'était le piège.
 *
 * `.diff-card` porte `overflow:hidden`, et la convention maison range sa
 * bulle AU-DESSUS de l'élément. Posée telle quelle, l'infobulle tombe hors
 * de la boîte et le rognage l'efface : l'attribut est là, la règle CSS est
 * là, la carte réagit au survol — et RIEN ne s'affiche. Aucune erreur, aucune
 * trace. Ce dépôt a déjà payé deux fois ce genre de défaut silencieux.
 *
 * LE CONTRÔLE QUI COMPTE, ET IL EST DIFFÉRENTIEL. On mesure la bulle telle
 * qu'elle est réglée, puis on REMET le réglage de la convention et on mesure
 * à nouveau. Le premier relevé doit montrer six bulles entières dans leur
 * carte ; le second doit les montrer rognées. Sans ce témoin, un contrôle
 * qui trouve la bulle visible ne prouve pas que c'est le cadrage qui la rend
 * visible — il pourrait passer pour une raison sans rapport.
 *
 * L'APPEL, ARRIVÉ ENSUITE SOUS LA BULLE. Chaque carte mène désormais quelque
 * part — deux vers une grille de cette page, trois vers un module Sentinel, une
 * vers le site institutionnel. Trois choses ne se voient que dans un navigateur :
 * la bulle ne doit JAMAIS recouvrir l'appel (elle est réglée exactement là où
 * il se pose) ; les deux ancres doivent déposer leur grille SOUS l'en-tête fixe,
 * qui mange les 108 premiers pixels ; et les trois modules doivent ouvrir le bon
 * panneau, ce qu'un fichier ne peut pas dire.
 *
 * LE LIEN INSTITUTIONNEL EST MESURÉ DANS LES DEUX ÉTATS. `bascule.js` le réécrit
 * quand i-aes.com ne répond pas — ce bac à sable reproduit naturellement cet
 * état — et relabellise par `textContent` les liens dont le texte nomme le
 * domaine, ce qui effacerait le span traduit et la flèche. On vérifie que le
 * span survit et que le libellé se traduit encore, quel que soit l'état.
 *
 * LES AUTRES CONTRÔLES : la bulle est cachée au repos et pleine au survol,
 * elle tient entre les deux bords de la carte, le blob n'a hérité ni du
 * contour ni de la translation de la flèche, et les trois langues écrivent
 * bien l'ATTRIBUT — une infobulle est du contenu que `applyLang` ne voyait
 * pas avant ce changement.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = 'recette_locale_idf_0123456789abcdef';
let ko = 0, n = 0;
const ok = (t, c, d) => { n++; if (!c) ko++;
  console.log((c ? '  OK   ' : '  KO   ') + t + (d ? ' — ' + d : '')); };

/* La géométrie de la bulle dans le repère de la boîte de PADDING, celle que
 * `overflow:hidden` prend pour ciseaux. On lit offsetWidth/offsetHeight, des
 * valeurs de mise en page : le scale(1.10) du survol ne les touche pas,
 * alors qu'il fausserait un getBoundingClientRect(). */
const GEOMETRIE = () =>
  [...document.querySelectorAll('#differenciateurs .diff-card')].map(c => {
    const cs = getComputedStyle(c), ap = getComputedStyle(c, '::after');
    const bt = parseFloat(cs.borderTopWidth), bb = parseFloat(cs.borderBottomWidth);
    const bl = parseFloat(cs.borderLeftWidth), br = parseFloat(cs.borderRightWidth);
    const padH = c.offsetHeight - bt - bb, padW = c.offsetWidth - bl - br;
    const h = parseFloat(ap.height), w = parseFloat(ap.width);
    const bas = parseFloat(ap.bottom), gauche = parseFloat(ap.left);
    const haut = padH - bas - h;
    /* L'appel est relevé en coordonnées de MISE EN PAGE, comme la bulle :
     * offsetTop ne connaît pas le scale(1.10) du survol, qui fausserait un
     * getBoundingClientRect() et ferait comparer deux repères différents. */
    const a = c.querySelector('.diff-go');
    const aHaut = a ? a.offsetTop - bt : null;
    const men = c.querySelector('.diff-cnx');
    const mHaut = men ? men.offsetTop - bt : null;
    return {
      cle: (c.querySelector('.diff-title') || {}).dataset.i18n,
      bulle: c.getAttribute('data-tooltip'),
      rogne: !(haut >= -0.5 && bas >= -0.5 && gauche >= -0.5 && gauche + w <= padW + 0.5),
      recouvre: a ? (padH - bas) > aHaut + 0.5 : true,
      recouvreMention: men ? (padH - bas) > mHaut + 0.5 : false,
      mention: men ? men.textContent.trim() : null,
      mentionVisible: men ? men.checkVisibility({checkVisibilityCSS:true,
        opacityProperty:true, visibilityProperty:true}) : null,
      appel: a ? { href: a.getAttribute('href'), cible: a.getAttribute('target') || '',
                   rel: a.getAttribute('rel') || '', texte: a.textContent.trim(),
                   /* réécrit par bascule.js : ce n'est plus le lien écrit ici */
                   bascule: a.getAttribute('data-bascule') || '',
                   span: !!a.querySelector('span[data-i18n]') } : null,
      dim: Math.round(w) + '×' + Math.round(h),
      overflow: cs.overflow,
      bordureFleche: getComputedStyle(c, '::before').borderTopWidth,
      transformFleche: getComputedStyle(c, '::before').transform
    };
  });

(async () => {
  const nav = await chromium.launch({ args: ['--no-sandbox', '--disable-blink-features=AutomationControlled'] });
  const ctx = await nav.newContext({ viewport: { width: 1440, height: 1000 }, locale: 'fr-FR',
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36' });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr', 'en-US'] });
  });
  /* LE SITE INSTITUTIONNEL EST SERVI PAR UNE DOUBLURE. Un environnement qui ne
   * peut pas joindre i-aes.com ferait échouer la navigation, et le contrôle
   * mesurerait le RÉSEAU au lieu de la destination du clic. La doublure répond
   * à l'adresse réelle : l'URL de l'onglet est bien celle visée. Là où le site
   * répond vraiment, elle ne change rien à ce qui est mesuré. */
  await ctx.route('https://i-aes.com/**', r => r.fulfill({
    status: 200, contentType: 'text/html; charset=utf-8',
    body: '<!doctype html><title>doublure i-aes.com</title><p>doublure' }));
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'domcontentloaded' });
  await pg.goto(BASE + '/', { waitUntil: 'load' });
  await pg.waitForTimeout(1500);
  /* le défilement doux fausse toute mesure prise juste après */
  await pg.evaluate(() => { document.documentElement.style.scrollBehavior = 'auto'; });
  const centrer = () => pg.evaluate(() => document.getElementById('differenciateurs')
      .scrollIntoView({ behavior: 'instant', block: 'center' }));
  await centrer();
  await pg.waitForTimeout(500);

  /* ── LA BULLE TIENT DANS LA CARTE QUI ROGNE ───────────────────────── */
  const g = await pg.evaluate(GEOMETRIE);
  ok('les six cartes portent une infobulle',
     g.length === 6 && g.every(x => x.bulle && x.bulle.length > 40),
     g.map(x => x.cle + ':' + (x.bulle || '').length).join(' · '));
  ok('la carte rogne toujours ce qui déborde',
     g.every(x => x.overflow === 'hidden'), g.map(x => x.overflow).join(' '));
  ok('AUCUNE des six bulles n’est rognée',
     g.every(x => !x.rogne),
     g.filter(x => x.rogne).map(x => x.cle).join(', ') || g.map(x => x.dim).join(' · '));
  ok('le blob n’a pas hérité du contour de la flèche',
     g.every(x => parseFloat(x.bordureFleche) === 0), g[0].bordureFleche);
  ok('le blob n’a pas hérité de la translation de la flèche',
     g.every(x => x.transformFleche === 'none'), g[0].transformFleche);

  /* ── LE TÉMOIN : LE RÉGLAGE DE LA CONVENTION, LUI, EST ROGNÉ ──────── */
  await pg.evaluate(() => {
    const s = document.createElement('style');
    s.id = 'cp-temoin-convention';
    s.textContent = '.diff-card[data-tooltip]::after{top:auto!important;' +
      'bottom:calc(100% + 10px)!important;left:50%!important;right:auto!important;' +
      'max-width:220px!important;transform:translateX(-50%)!important}';
    document.head.appendChild(s);
  });
  await pg.waitForTimeout(250);
  const t = await pg.evaluate(GEOMETRIE);
  ok('TÉMOIN — avec le réglage de la convention, les six sont rognées',
     t.length === 6 && t.every(x => x.rogne),
     t.filter(x => !x.rogne).map(x => x.cle).join(', ') ||
     'c’est bien le cadrage qui les rend visibles');
  await pg.evaluate(() => document.getElementById('cp-temoin-convention').remove());
  await pg.waitForTimeout(250);

  /* ── CACHÉE AU REPOS, PLEINE AU SURVOL ────────────────────────────── */
  let vues = 0, fuites = 0;
  const restes = [];
  for (let i = 1; i <= 6; i++) {
    /* recentrer AVANT chaque survol : une carte glissée sous l’en-tête
     * collant reçoit le pointeur sur l’en-tête, pas sur elle. */
    await centrer();
    await pg.waitForTimeout(250);
    const sel = '#differenciateurs .diff-card:nth-child(' + i + ')';
    const pt = await pg.evaluate(s => { const r = document.querySelector(s).getBoundingClientRect();
      return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; }, sel);
    await pg.mouse.move(pt.x, pt.y);
    await pg.waitForTimeout(600);
    const m = await pg.evaluate(s => {
      const c = document.querySelector(s);
      return { survole: c.matches(':hover'),
               opacite: getComputedStyle(c, '::after').opacity };
    }, sel);
    if (m.survole && m.opacite === '1') vues++;
    await pg.mouse.move(700, 4);
    /* QUATRE FOIS LA TRANSITION DÉCLARÉE, ET UN SEUIL D'INVISIBILITÉ.
     * Un premier réglage relevait l'opacité 350 ms après avoir quitté la
     * carte et trouvait 0,003 sur deux cartes : la carte n'était plus
     * survolée, la bulle s'effaçait — la sonde lisait la queue de la
     * transition et appelait ça une fuite. Exiger un zéro exact à la
     * milliseconde près, c'est mesurer l'ordonnanceur du navigateur ; ce
     * qui se mesure ici, c'est qu'il ne reste rien de lisible. */
    await pg.waitForTimeout(800);
    const repos = await pg.evaluate(s => ({
      opacite: getComputedStyle(document.querySelector(s), '::after').opacity,
      survole: document.querySelector(s).matches(':hover')
    }), sel);
    if (repos.survole || parseFloat(repos.opacite) > 0.02) { fuites++; restes.push(i + ':' + repos.opacite); }
  }
  ok('les six bulles apparaissent au survol', vues === 6, vues + '/6');
  ok('et aucune ne reste affichée au repos', fuites === 0, restes.join(' ') || '');

  /* ── LES TROIS LANGUES ÉCRIVENT BIEN L’ATTRIBUT ───────────────────── */
  const par = {};
  for (const lg of ['fr', 'en', 'de']) {
    await pg.evaluate(l => setLang(l), lg);
    await pg.waitForTimeout(400);
    par[lg] = await pg.evaluate(() =>
      [...document.querySelectorAll('#differenciateurs .diff-card')]
        .map(c => c.getAttribute('data-tooltip')));
    ok('l’infobulle est écrite en ' + lg,
       par[lg].length === 6 && par[lg].every(x => x && x.length > 40),
       par[lg].map(x => (x || '').length).join('/'));
  }
  ok('les trois langues disent des choses différentes',
     par.fr.every((x, k) => x !== par.en[k] && x !== par.de[k] && par.en[k] !== par.de[k]),
     par.fr.map((x, k) => x === par.en[k] ? k + 1 : '').filter(Boolean).join(',') || '');
  await pg.evaluate(() => setLang('fr'));
  await pg.waitForTimeout(400);
  const retour = await pg.evaluate(() =>
    [...document.querySelectorAll('#differenciateurs .diff-card')].map(c => c.getAttribute('data-tooltip')));
  ok('le retour au français restitue le texte d’origine',
     retour.every((x, k) => x === par.fr[k]), '');

  /* ── ET LA TRADUCTION N’A RIEN MANGÉ AU PASSAGE ───────────────────── */
  const intact = await pg.evaluate(() =>
    [...document.querySelectorAll('#differenciateurs .diff-card')]
      .map(c => ({ ico: !!c.querySelector('.diff-ico'),
                   titre: (c.querySelector('.diff-title') || {}).textContent,
                   desc: (c.querySelector('.diff-desc') || {}).textContent })));
  ok('les six cartes gardent leur icône, leur titre et leur description',
     intact.length === 6 && intact.every(x => x.ico && x.titre && x.desc && x.desc.length > 40),
     intact.filter(x => !x.ico).length + ' icône(s) perdue(s)');
  ok('aucune erreur JavaScript', err.length === 0, err.join(' | '));

  /* ── L'APPEL : SIX DESTINATIONS, ET LA BULLE QUI LES LAISSE CLIQUABLES ── */
  const ATTENDU = [
    ['df.ai.t',   '/sentinel?goto=owasp-dix', 'p-owasp-dix'],
    ['df.ind.t',  '#secteurs',                null],
    ['df.eco.t',  '/sentinel?goto=finops',    'p-finops'],
    ['df.exp.t',  'https://i-aes.com',        null],
    ['df.jur.t',  '#normes',                  null],
    ['df.intl.t', '/sentinel?goto=carto',     'p-carto']
  ];
  const g2 = await pg.evaluate(GEOMETRIE);
  ok('les six cartes portent leur appel',
     g2.every(x => x.appel && x.appel.span),
     g2.filter(x => !x.appel).map(x => x.cle).join(', ') || '');
  ok('chaque appel mène là où la demande l’a envoyé',
     g2.every((x, k) => x.appel &&
       (x.appel.href === ATTENDU[k][1] ||
        /* état dégradé : bascule.js a réécrit le lien institutionnel */
        (ATTENDU[k][1].indexOf('i-aes.com') >= 0 && /bascule=/.test(x.appel.href)))),
     g2.map((x, k) => x.appel.href === ATTENDU[k][1] ? '' : x.cle + '→' + x.appel.href)
       .filter(Boolean).join(' ') || '');
  /* ON NE COMPTE QUE LES LIENS TELS QU'ILS SONT ÉCRITS ICI. Quand i-aes.com
   * ne répond pas, `bascule.js` réécrit le lien institutionnel vers /sentinel
   * ET lui retire son `target` — c'est sa décision, pas la nôtre, et il relaie
   * vers notre propre domaine. Une première version les comptait quand même :
   * elle trouvait quatre liens Sentinel au lieu de trois et tombait sur le
   * travail d'un autre module, pas sur un défaut de celui-ci. */
  const versSentinel = g2.filter(x => /^\/sentinel/.test(x.appel.href) && !x.appel.bascule);
  ok('les liens vers Sentinel gardent la page d’accueil',
     versSentinel.length === 3 &&
     versSentinel.every(x => x.appel.cible === '_blank' && /noopener/.test(x.appel.rel)),
     versSentinel.length + ' liens Sentinel écrits ici' +
     (g2.some(x => x.appel.bascule) ? ' (+1 réécrit par la bascule)' : ''));
  ok('les ancres restent dans l’onglet courant',
     g2.filter(x => /^#/.test(x.appel.href)).every(x => x.appel.cible === ''), '');

  /* LE CONTRÔLE QUI A COMMANDÉ TOUT LE RÉGLAGE : la bulle est posée en bas de
   * la carte, l’appel aussi. À trois largeurs et dans trois langues, aucune
   * des six ne doit recouvrir le lien qu’elle surplombe. */
  let croisements = 0, rognees2 = 0;
  const detail = [];
  for (const [largeur, hauteur, nomL] of [[1440,1000,'3 col'],[880,1000,'2 col'],[420,900,'1 col']]) {
    await pg.setViewportSize({ width: largeur, height: hauteur });
    await pg.waitForTimeout(400);
    await centrer();
    await pg.waitForTimeout(300);
    for (const lg of ['fr','en','de']) {
      await pg.evaluate(l => setLang(l), lg);
      await pg.waitForTimeout(300);
      const r = await pg.evaluate(GEOMETRIE);
      const c = r.filter(x => x.recouvre), q = r.filter(x => x.rogne);
      croisements += c.length; rognees2 += q.length;
      if (c.length || q.length) detail.push(nomL + '/' + lg + ' ' +
        c.map(x => x.cle).concat(q.map(x => x.cle + '(rognée)')).join(','));
    }
  }
  await pg.setViewportSize({ width: 1440, height: 1000 });
  await pg.evaluate(l => setLang(l), 'fr');
  await pg.waitForTimeout(400);
  ok('à trois largeurs et en trois langues, la bulle ne recouvre JAMAIS l’appel',
     croisements === 0, detail.join(' | ') || '9 relevés');
  ok('et aucune n’est rognée à ces largeurs', rognees2 === 0, '');

  /* ── LE LIEN INSTITUTIONNEL SURVIT À LA BASCULE ───────────────────────── */
  const inst = await pg.evaluate(() => {
    const a = document.querySelector('#differenciateurs .diff-card:nth-child(4) .diff-go');
    return { span: !!a.querySelector('[data-i18n="dg.exp"]'),
             fleche: /↗/.test(a.textContent),
             href: a.getAttribute('href'),
             bascule: a.getAttribute('data-bascule') || 'aucune',
             origine: a.getAttribute('data-href-origine') || a.getAttribute('href') };
  });
  ok('le lien institutionnel garde son span traduit et sa flèche',
     inst.span && inst.fleche,
     'bascule=' + inst.bascule + ' href=' + String(inst.href).slice(0, 44));
  ok('et il visait bien i-aes.com', /i-aes\.com/.test(inst.origine), inst.origine);

  /* ── LES LIBELLÉS SUIVENT LA LANGUE, LA FLÈCHE RESTE ──────────────────── */
  const lib = {};
  for (const lg of ['fr','en','de']) {
    await pg.evaluate(l => setLang(l), lg);
    await pg.waitForTimeout(350);
    lib[lg] = await pg.evaluate(() =>
      [...document.querySelectorAll('#differenciateurs .diff-go')].map(a => a.textContent.trim()));
    ok('les six libellés sont écrits en ' + lg,
       lib[lg].length === 6 && lib[lg].every(t => t.length > 6 && /[→↗]$/.test(t)),
       lib[lg].filter(t => !/[→↗]$/.test(t)).join(', ') || '');
  }
  ok('les trois langues donnent des libellés différents',
     lib.fr.every((t, k) => t !== lib.en[k] && t !== lib.de[k] && lib.en[k] !== lib.de[k]),
     lib.fr.map((t, k) => t === lib.en[k] ? String(k + 1) : '').filter(Boolean).join(',') || '');
  await pg.evaluate(() => setLang('fr'));
  await pg.waitForTimeout(350);

  /* ── LES DEUX ANCRES DÉPOSENT LEUR GRILLE SOUS L’EN-TÊTE FIXE ─────────── */
  for (const [rang, cible] of [[2, '#secteurs'], [5, '#normes']]) {
    await pg.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
    await pg.waitForTimeout(300);
    await centrer();
    await pg.waitForTimeout(250);
    await pg.click('#differenciateurs .diff-card:nth-child(' + rang + ') .diff-go');
    await pg.waitForTimeout(1400);
    const r = await pg.evaluate(c => {
      const s = document.querySelector(c);
      const t = (s.querySelector('.lb') || s.querySelector('.tt')).getBoundingClientRect();
      const grille = (s.querySelector('.sector-grid') || s.querySelector('.ng')).getBoundingClientRect();
      const bas = [...document.querySelectorAll('body *')].filter(e => {
        const p = getComputedStyle(e).position, rr = e.getBoundingClientRect();
        return (p === 'fixed' || p === 'sticky') && rr.top < 60 && rr.height > 20 && rr.height < 200;
      }).reduce((m, e) => Math.max(m, e.getBoundingClientRect().bottom), 0);
      return { hash: location.hash, surtitre: Math.round(t.top),
               grille: Math.round(grille.top), enTete: Math.round(bas) };
    }, cible);
    ok('l’ancre ' + cible + ' dépose sa grille sous l’en-tête fixe',
       r.hash === cible && r.surtitre >= r.enTete && r.grille > r.enTete,
       'surtitre à ' + r.surtitre + ', en-tête jusqu’à ' + r.enTete);
  }

  /* ── LES TROIS MODULES, PAR UN VRAI CLIC ─────────────────────────────── */
  for (const [rang, , panneau] of ATTENDU.map((a, i) => [i + 1, a[1], a[2]]).filter(a => a[2])) {
    await centrer();
    await pg.waitForTimeout(300);
    const [onglet] = await Promise.all([
      ctx.waitForEvent('page', { timeout: 25000 }),
      pg.click('#differenciateurs .diff-card:nth-child(' + rang + ') .diff-go')
    ]);
    await onglet.waitForLoadState('load');
    let vu = { ids: [], shell: false };
    for (let k = 0; k < 16; k++) {
      await onglet.waitForTimeout(800);
      vu = await onglet.evaluate(() => ({
        shell: !!document.getElementById('tb-pg'),
        ids: [...document.querySelectorAll('.page')]
               .filter(x => getComputedStyle(x).display !== 'none').map(x => x.id)
      }));
      if (vu.ids.length) break;
    }
    ok('la carte ' + rang + ' ouvre ' + panneau + ' dans un nouvel onglet',
       vu.ids.indexOf(panneau) >= 0,
       vu.shell ? ('panneau ' + (vu.ids.join(',') || 'aucun'))
                : 'la page Sentinel n’a pas été servie (limiteur de débit ?)');
    await onglet.close();
    await pg.bringToFront();
  }

  /* ── « CONNEXION REQUISE » : DIT AVANT LE CLIC ───────────────────────── */
  const g3 = await pg.evaluate(GEOMETRIE);
  ok('la mention est sur les appels qui exigent un compte, et sur eux seuls',
     g3.filter(x => x.mention).length === 3 &&
     g3.every(x => !!x.mention === /^\/sentinel/.test(String(x.appel.href))),
     g3.filter(x => x.mention).map(x => x.cle).join(', '));
  ok('les trois mentions sont réellement visibles',
     g3.filter(x => x.mentionVisible).length === 3,
     g3.map(x => x.mention ? 'oui' : '—').join('/'));
  let cM = 0;
  for (const [largeur, hauteur] of [[1440,1000],[880,1000],[420,900]]) {
    await pg.setViewportSize({ width: largeur, height: hauteur });
    await pg.waitForTimeout(350);
    await centrer();
    await pg.waitForTimeout(250);
    for (const lg of ['fr','en','de']) {
      await pg.evaluate(l => setLang(l), lg);
      await pg.waitForTimeout(280);
      cM += (await pg.evaluate(GEOMETRIE)).filter(x => x.recouvreMention).length;
    }
  }
  await pg.setViewportSize({ width: 1440, height: 1000 });
  await pg.evaluate(() => setLang('fr'));
  await pg.waitForTimeout(350);
  ok('la bulle ne recouvre jamais la mention qu’elle surplombe', cM === 0, String(cM));

  const men = {};
  for (const lg of ['fr','en','de']) {
    await pg.evaluate(l => setLang(l), lg);
    await pg.waitForTimeout(320);
    men[lg] = await pg.evaluate(() =>
      [...document.querySelectorAll('#differenciateurs .diff-cnx')].map(e => e.textContent.trim()));
  }
  ok('la mention se traduit, et garde son cadenas dans les trois langues',
     men.fr[0] !== men.en[0] && men.fr[0] !== men.de[0] && men.en[0] !== men.de[0] &&
     ['fr','en','de'].every(l => men[l].every(t => /🔒/.test(t))),
     [men.fr[0], men.en[0], men.de[0]].join(' · '));
  await pg.evaluate(() => setLang('fr'));
  await pg.waitForTimeout(320);

  /* ── L’APPEL INSTITUTIONNEL EST DÉTOURNÉ — VERS UNE PAGE PUBLIQUE ────
     CE QUE CETTE SECTION MESURAIT AVANT, ET POURQUOI ELLE A CHANGÉ.
     Elle vérifiait que l’appel « Découvrir le site institutionnel » RESTAIT
     sur i-aes.com quoi qu’il arrive. C’était la bonne exigence tant que la
     bascule menait à /sentinel : mieux valait une page en panne, qui se
     comprend, qu’un formulaire de connexion, qui ne se comprend pas.

     LE RELAIS EST DEVENU PUBLIC. /relais-iaes n’exige aucun compte, dit
     quel signal a déclenché la bascule, et REDONNE l’adresse d’origine
     pour que le visiteur réessaie lui-même. Garder l’exception coûterait
     désormais au visiteur ce qu’elle devait lui épargner : une erreur de
     navigateur, hors du site, sans explication ni retour.

     ON MESURE DONC L’INVERSE — et surtout, on mesure que la destination
     N’EST PAS un formulaire de connexion, ce qui était le défaut signalé. */
  const inst2 = await pg.evaluate(() => {
    const a = document.querySelector('#differenciateurs .diff-card:nth-child(4) .diff-go');
    return { href: a.getAttribute('href'), bascule: a.getAttribute('data-bascule') || '',
             exempt: a.hasAttribute('data-bascule-jamais'),
             origine: a.getAttribute('data-href-origine') || '' };
  });
  ok('l’appel institutionnel ne sort plus du relais', !inst2.exempt,
     'il porte encore data-bascule-jamais');
  ok('la bascule l’a bien détourné vers le relais PUBLIC',
     /^\/relais-iaes\?/.test(inst2.href) && !!inst2.bascule,
     inst2.href.slice(0, 60));
  ok('l’adresse d’origine est conservée pour le retour',
     inst2.origine === 'https://i-aes.com', inst2.origine || '(perdue)');

  /* ON MESURE OÙ LE CLIC ABOUTIT, PAS CE QUE LE RÉSEAU EN FAIT. */
  await centrer();
  await pg.waitForTimeout(300);
  /* ═══ ON LAISSE LA FENÊTRE DU LIMITEUR SE ROULER, ET C'EST MESURÉ ═══
     Le serveur local plafonne à 120 requêtes par minute et par adresse.
     Cette recette en consomme l'essentiel : arrivée ici, la navigation
     revenait 429, le document était vide — et le contrôle « ce n'est pas
     un formulaire de connexion » PASSAIT, parce qu'un titre vide ne
     contient pas le mot « connexion ». Un contrôle qui réussit sur une
     page absente ne mesure rien. On attend donc, et on exige un titre. */
  console.log('     … attente de la fenêtre de débit (65 s)');
  await pg.waitForTimeout(65000);

  await pg.click('#differenciateurs .diff-card:nth-child(4) .diff-go');
  /* ON ATTEND LA PAGE, PAS UN DÉLAI. Une première version lisait le titre
     après 1 500 ms fixes : l'adresse avait changé, le document non. */
  await pg.waitForSelector('#lien-origine', { timeout: 15000 }).catch(() => {});
  const arrivee = { url: pg.url(), titre: await pg.title() };
  ok('le clic aboutit sur une VRAIE page de relais',
     /\/relais-iaes/.test(arrivee.url) && /i-aes\.com/.test(arrivee.titre),
     (arrivee.titre || '(page vide)') + ' — ' + arrivee.url.replace(BASE, ''));
  ok('et ce n\u2019est pas un formulaire de connexion',
     !!arrivee.titre && !/connexion|login|sign/i.test(arrivee.titre),
     arrivee.titre || '(page vide — le contrôle serait faussement vert)');
  /* LE CONTRÔLE QUI COMPTE VRAIMENT : le visiteur peut-il encore atteindre
     le site qu’il venait chercher ? */
  const retourIaes = await pg.evaluate(() => {
    const a = document.getElementById('lien-origine');
    return a ? a.getAttribute('href') : null;
  });
  ok('la page de relais REDONNE l’adresse d’origine',
     retourIaes === 'https://i-aes.com', String(retourIaes));
  await pg.goBack({ waitUntil: 'domcontentloaded' }).catch(() => {});
  await pg.bringToFront();

  await nav.close();
  console.log('\n' + (n - ko) + ' contrôles passés, ' + ko + ' en échec');
  process.exit(ko ? 1 : 0);
})().catch(e => { console.error('KO rompu : ' + e); process.exit(2); });
