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
    return {
      cle: (c.querySelector('.diff-title') || {}).dataset.i18n,
      bulle: c.getAttribute('data-tooltip'),
      rogne: !(haut >= -0.5 && bas >= -0.5 && gauche >= -0.5 && gauche + w <= padW + 0.5),
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

  await nav.close();
  console.log('\n' + (n - ko) + ' contrôles passés, ' + ko + ' en échec');
  process.exit(ko ? 1 : 0);
})().catch(e => { console.error('KO rompu : ' + e); process.exit(2); });
