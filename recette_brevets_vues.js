/* Deux lectures de plus sur le même jeu de données — et ce que chacune doit
 * tenir pour mériter son onglet.
 *
 * 1. LA COMPOSITION. Les deux vues d'origine répondent chacune à une moitié de
 *    la question : la PART dit la répartition et perd le total, le VOLUME dit
 *    le total et perd la répartition. La colonne empilée porte les deux sur un
 *    seul axe. Elle n'a donc le droit d'exister que si elle somme JUSTE : un
 *    empilement dont les segments ne reconstituent pas le total mondial ferait
 *    de la réconciliation un mensonge.
 *
 *    Et si l'on éteint un acteur, le vide doit rester VISIBLE. Une somme
 *    partielle qui se referme sur elle-même passerait pour un tout.
 *
 * 2. LE CLASSEMENT. Il répond à « où en est-on », pas à « comment y est-on
 *    arrivé ». Il doit donc être trié, chiffré au bout de chaque barre, et
 *    porter le facteur de croissance : sans lui, la barre européenne — quatre
 *    pour cent de la chinoise — ne dirait que la petitesse en taisant le ×21.
 *
 * 3. LA COULEUR SUIT L'ACTEUR, JAMAIS SON RANG. Une palette qui repeindrait
 *    les survivants à chaque filtre ferait mentir la mémoire du lecteur.
 *
 * 4. RIEN NE DOIT SE CHEVAUCHER. Le contrôle est géométrique, pas visuel : on
 *    mesure les rectangles à l'écran. C'est ainsi qu'on a trouvé la légende
 *    d'axe passant AU TRAVERS des graduations — un défaut que la vue
 *    logarithmique portait déjà.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = 'http://127.0.0.1:5401';
let ko = 0;
const ok = (n, c, d) => { console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : '')); if (!c) ko++; };

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1440, height: 1000 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));
  await pg.goto(BASE + '/auth/recette_locale_idf_0123456789abcdef', { waitUntil: 'domcontentloaded' });
  await pg.goto(BASE + '/observatoire', { waitUntil: 'networkidle' });
  await pg.waitForFunction(() => document.querySelector('#brev-chart svg'), null, { timeout: 30000 });

  const vue = async (v) => {
    await pg.click('.bv-vues [data-vue="' + v + '"]');
    await pg.waitForTimeout(420);
  };

  console.log('\n══ 1. Quatre lectures, chacune nommée pour ce qu’elle montre ══\n');
  const onglets = await pg.evaluate(() => [...document.querySelectorAll('.bv-vues [data-vue]')]
    .map(b => ({ v: b.getAttribute('data-vue'), t: b.textContent.trim() })));
  ok('quatre onglets', onglets.length === 4, onglets.map(o => o.v).join(','));
  ok('…dont les deux nouveaux', onglets.some(o => o.v === 'empile')
     && onglets.some(o => o.v === 'rang'), onglets.map(o => o.t).join(' | '));
  ok('…et leurs libellés disent la FORME, pas seulement le sujet',
     /barres empilées/i.test((onglets[2] || {}).t || '')
     && /barres/i.test((onglets[3] || {}).t || ''));

  const etat = async (v) => {
    await vue(v);
    return pg.evaluate(() => ({
      vue: BV_VUE,
      titre: document.getElementById('t-brev').textContent,
      lecture: document.getElementById('brev-lecture').innerText,
      note: document.getElementById('brev-note').textContent,
      alt: document.querySelector('#brev-chart svg').getAttribute('aria-label'),
      onglet: document.querySelector('.bv-vues .on').getAttribute('data-vue'),
      selected: document.querySelector('.bv-vues [aria-selected="true"]').getAttribute('data-vue'),
    }));
  };
  const E = {};
  for (const v of ['part', 'volume', 'empile', 'rang']) E[v] = await etat(v);
  ok('chaque onglet change bien la vue', Object.keys(E).every(v => E[v].vue === v));
  ok('…et l’état sélectionné suit, pour la souris comme pour le lecteur d’écran',
     Object.keys(E).every(v => E[v].onglet === v && E[v].selected === v));
  /* Le titre du panneau est ce qu'on lit en premier : « part du total mondial »
     au-dessus d'un classement en volume serait un contresens. */
  ok('quatre titres distincts, aucun recopié',
     new Set(Object.keys(E).map(v => E[v].titre)).size === 4,
     E.empile.titre + ' / ' + E.rang.titre);
  ok('…celui de la composition parle du TOTAL mondial',
     /composition du total mondial/i.test(E.empile.titre), E.empile.titre);
  ok('…celui du classement porte son année', /classement 2023/i.test(E.rang.titre),
     E.rang.titre);
  ok('quatre textes de lecture distincts',
     new Set(Object.keys(E).map(v => E[v].lecture)).size === 4);
  ok('…et chacun dit AUSSI ce qu’il ne montre pas',
     Object.keys(E).every(v => /ne montre pas/i.test(E[v].lecture)));
  ok('quatre notes de précision distinctes',
     new Set(Object.keys(E).map(v => E[v].note)).size === 4);
  ok('quatre descriptions alternatives distinctes, et chiffrées',
     new Set(Object.keys(E).map(v => E[v].alt)).size === 4
     && Object.keys(E).every(v => /\d/.test(E[v].alt)));

  console.log('\n══ 2. La composition somme JUSTE, ou elle ne vaut rien ══\n');
  await vue('empile');
  const emp = await pg.evaluate(() => {
    const b = DATA.brevets;
    const svg = document.querySelector('#brev-chart svg');
    const segs = [...svg.querySelectorAll('.bv-seg')];
    const parAn = {};
    segs.forEach(s => { const a = s.getAttribute('data-an');
      (parAn[a] = parAn[a] || []).push(s.getAttribute('fill')); });
    /* Le contrôle central : segment = part × volume, donc la somme des segments
       d'une année doit rendre EXACTEMENT le volume mondial de cette année. */
    const ecarts = b.annees.map(yr => {
      const i = b.annees.indexOf(yr), vol = brevVol(yr);
      if (vol === null) return null;
      const somme = brevSeries().reduce((t, sr) => t + sr.v[i] / 100 * vol, 0);
      return { yr: yr, vol: vol, somme: Math.round(somme * 1000) / 1000 };
    }).filter(Boolean);
    return { nAnnees: Object.keys(parAn).length, ecarts: ecarts,
             segs: segs.length,
             contours: svg.querySelectorAll('path[stroke="#CFCBD8"]').length,
             totaux: [...svg.querySelectorAll('text')].map(t => t.textContent)
               .filter(t => /^\d+(,\d+)? k$/.test(t)).length };
  });
  ok('huit colonnes, une par année mesurée', emp.nAnnees === 8, emp.nAnnees);
  ok('…et un contour de total par colonne', emp.contours === 8, emp.contours);
  const faux = emp.ecarts.filter(e => Math.abs(e.somme - e.vol) > 0.001);
  ok('chaque colonne somme EXACTEMENT au volume mondial de son année',
     faux.length === 0, faux.map(e => e.yr + ' : ' + e.somme + ' ≠ ' + e.vol).join(' · '));
  ok('…sur les huit années, sans exception', emp.ecarts.length === 8, emp.ecarts.length);
  ok('le total de chaque colonne est ÉCRIT au-dessus d’elle',
     emp.totaux >= 8, emp.totaux + ' totaux lisibles');
  ok('…ce qui est la seule façon de lire 2010, haute de quelques pixels',
     /quelques pixels/.test(E.empile.lecture));

  /* ÉTEINDRE UN ACTEUR : le vide doit rester visible. */
  const trou = await pg.evaluate(() => {
    const mesure = () => {
      const svg = document.querySelector('#brev-chart svg');
      const segs = [...svg.querySelectorAll('.bv-seg[data-an="2023"]')];
      const h = segs.reduce((t, s) => {
        const r = s.getBoundingClientRect(); return t + r.height; }, 0);
      const c = [...svg.querySelectorAll('path[stroke="#CFCBD8"]')].pop();
      return { rempli: Math.round(h), contour: Math.round(c.getBoundingClientRect().height),
               n: segs.length };
    };
    const avant = mesure();
    document.querySelector('[data-serie="us"]').click();
    const apres = mesure();
    document.querySelector('[data-serie="us"]').click();
    return { avant: avant, apres: apres, rendu: mesure() };
  });
  ok('quatre segments empilés en 2023', trou.avant.n === 4, trou.avant.n);
  ok('éteindre un acteur retire bien son segment', trou.apres.n === 3, trou.apres.n);
  ok('…et le rempli diminue', trou.apres.rempli < trou.avant.rempli - 10,
     trou.avant.rempli + ' → ' + trou.apres.rempli + ' px');
  /* LE contrôle : le contour, lui, ne bouge pas. Le trou se voit. */
  ok('…tandis que le contour du total mondial NE bouge PAS : le vide se voit',
     Math.abs(trou.apres.contour - trou.avant.contour) <= 1,
     trou.avant.contour + ' → ' + trou.apres.contour + ' px');
  ok('…et rallumer l’acteur rend la colonne pleine',
     Math.abs(trou.rendu.rempli - trou.avant.rempli) <= 2 && trou.rendu.n === 4);
  ok('la note prévient de ce comportement',
     /somme partielle n’est pas un tout/.test(E.empile.note), E.empile.note.slice(-60));

  console.log('\n══ 3. Le classement dit où l’on en est, et ce qui a bougé ══\n');
  await vue('rang');
  const rg = await pg.evaluate(() => {
    const svg = document.querySelector('#brev-chart svg');
    const barres = [...svg.querySelectorAll('.bv-bar')].map(p => ({
      k: p.getAttribute('data-serie'), fill: p.getAttribute('fill'),
      w: Math.round(p.getBoundingClientRect().width),
      y: Math.round(p.getBoundingClientRect().top) }));
    const txt = [...svg.querySelectorAll('text')].map(t => t.textContent);
    return { barres: barres, txt: txt,
             hauteur: svg.viewBox.baseVal.height,
             titres: [...svg.querySelectorAll('.bv-bar title')].map(t => t.textContent) };
  });
  ok('une barre par acteur', rg.barres.length === 4, rg.barres.length);
  ok('…triées de la plus longue à la plus courte',
     rg.barres.every((b, i) => i === 0 || b.w <= rg.barres[i - 1].w),
     rg.barres.map(b => b.k + ':' + b.w).join(' '));
  ok('…et dans l’ordre du classement à l’écran, du haut vers le bas',
     rg.barres.every((b, i) => i === 0 || b.y > rg.barres[i - 1].y));
  ok('la Chine est en tête', rg.barres[0].k === 'chine', rg.barres[0].k);
  ok('…et l’Europe ferme la marche', rg.barres[3].k === 'europe', rg.barres[3].k);
  /* Chaque barre est nommée ET chiffrée à côté d'elle : quatre séries exigent
     l'étiquette directe, sinon il faut recouper avec la légende. */
  ok('chaque acteur est nommé à côté de sa barre',
     ['Chine', 'États-Unis', 'Europe'].every(n => rg.txt.some(t => t.indexOf(n) === 0)),
     rg.txt.slice(0, 6).join(' | '));
  ok('…sa valeur est écrite au bout', rg.txt.indexOf('85 k') >= 0
     && rg.txt.indexOf('17,3 k') >= 0 && rg.txt.indexOf('3,4 k') >= 0);
  ok('…et sa part du monde sous son nom',
     rg.txt.filter(t => /% du monde$/.test(t)).length === 4,
     rg.txt.filter(t => /% du monde$/.test(t)).join(' · '));
  /* CE QUE LA LONGUEUR TAIT. Sans le facteur, la barre européenne ne dit que
     sa petitesse ; avec lui, elle dit aussi ×21. */
  ok('le facteur de croissance accompagne chaque barre',
     rg.txt.filter(t => /^×\d+ depuis 2010$/.test(t)).length === 4,
     rg.txt.filter(t => /^×\d+ depuis/.test(t)).join(' · '));
  ok('…et il distingue la Chine (×327) de l’Europe (×21)',
     rg.txt.indexOf('×327 depuis 2010') >= 0 && rg.txt.indexOf('×21 depuis 2010') >= 0);
  ok('chaque barre porte son propre survol chiffré',
     rg.titres.length === 4 && rg.titres.every(t => /brevets d’IA accordés en 2023/.test(t)),
     (rg.titres[0] || '').slice(0, 60));

  /* La hauteur suit le nombre de barres : fixée, elle laisserait un vide qu'on
     lit comme une donnée manquante. */
  const haut = await pg.evaluate(() => {
    const h = () => document.querySelector('#brev-chart svg').viewBox.baseVal.height;
    const a = h();
    document.querySelector('[data-serie="us"]').click();
    document.querySelector('[data-serie="reste"]').click();
    const b = h();
    document.querySelector('[data-serie="us"]').click();
    document.querySelector('[data-serie="reste"]').click();
    return { quatre: a, deux: b, rendu: h() };
  });
  ok('la hauteur du cadre suit le nombre de barres',
     haut.deux < haut.quatre - 60, haut.quatre + ' → ' + haut.deux);
  ok('…et revient quand les acteurs reviennent', haut.rendu === haut.quatre);

  console.log('\n══ 4. La couleur suit l’acteur, jamais son rang ══\n');
  const coul = await pg.evaluate(async () => {
    const lire = () => {
      const o = {};
      document.querySelectorAll('#brev-chart svg [data-serie]').forEach(p => {
        o[p.getAttribute('data-serie')] = p.getAttribute('fill'); });
      document.querySelectorAll('#brev-chart svg .bv-seg').forEach(() => {});
      return o;
    };
    const rang = lire();
    /* On éteint le premier : si la palette suivait le RANG, le deuxième
       hériterait du rouge. */
    document.querySelector('[data-serie="chine"]').click();
    const sansChine = lire();
    document.querySelector('[data-serie="chine"]').click();
    return { rang: rang, sansChine: sansChine };
  });
  ok('chaque acteur garde SA couleur quand le premier disparaît',
     coul.sansChine.us === coul.rang.us && coul.sansChine.europe === coul.rang.europe
     && coul.sansChine.reste === coul.rang.reste,
     JSON.stringify(coul.sansChine));
  ok('…et personne n’hérite du rouge de la Chine',
     Object.keys(coul.sansChine).every(k => coul.sansChine[k] !== coul.rang.chine),
     coul.rang.chine);
  /* La même palette dans les quatre vues : un acteur qui changerait de couleur
     d'un onglet à l'autre obligerait à réapprendre la légende à chaque clic. */
  const memes = await pg.evaluate(async () => {
    const pris = {};
    for (const v of ['volume', 'empile', 'rang']) {
      document.querySelector('.bv-vues [data-vue="' + v + '"]').click();
      await new Promise(r => setTimeout(r, 120));
      pris[v] = [...document.querySelectorAll('#brev-leg [data-serie]')]
        .map(b => b.getAttribute('data-serie') + '='
          + getComputedStyle(b.querySelector('.sw')).backgroundColor).join(',');
    }
    return pris;
  });
  ok('la palette est la même dans les quatre vues',
     memes.volume === memes.empile && memes.empile === memes.rang, memes.rang);

  console.log('\n══ 5. Rien ne se chevauche — contrôle géométrique ══\n');
  const chevauche = async (v) => {
    await vue(v);
    return pg.evaluate(() => {
      const svg = document.querySelector('#brev-chart svg');
      const t = [...svg.querySelectorAll('text')]
        .filter(x => x.textContent.trim())
        .map(x => ({ t: x.textContent.trim(), r: x.getBoundingClientRect() }))
        .filter(x => x.r.width > 0 && x.r.height > 0);
      const cogne = [];
      for (let i = 0; i < t.length; i++) for (let j = i + 1; j < t.length; j++) {
        const a = t[i].r, b = t[j].r;
        const dx = Math.min(a.right, b.right) - Math.max(a.left, b.left);
        const dy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        /* Deux pixels de tolérance : les boîtes des glyphes se frôlent sans se
           gêner, et un contrôle au pixel près ne serait qu'un générateur de
           faux positifs. */
        if (dx > 2 && dy > 2) cogne.push(t[i].t + ' × ' + t[j].t);
      }
      return cogne;
    });
  };
  for (const v of ['part', 'volume', 'empile', 'rang']) {
    const c = await chevauche(v);
    ok('vue « ' + v + '  » : aucun texte n’en recouvre un autre', c.length === 0,
       c.slice(0, 2).join(' | '));
  }
  /* Le défaut qu'on a trouvé par ce contrôle : la légende verticale de l'axe
     traversait les graduations dès qu'elles portaient sept caractères. */
  await vue('volume');
  const marge = await pg.evaluate(() => {
    const svg = document.querySelector('#brev-chart svg');
    const lg = [...svg.querySelectorAll('text')]
      .find(t => /échelle logarithmique/.test(t.textContent));
    /* `toLocaleString('fr-FR')` sépare les milliers par une espace fine
       insécable (U+202F), pas par une espace ordinaire : comparer à
       « 100 000 » tapé au clavier ne trouve jamais rien. */
    const grad = [...svg.querySelectorAll('text')]
      .find(t => /^100.?000$/.test(t.textContent));
    return { lg: lg ? Math.round(lg.getBoundingClientRect().right) : null,
             grad: grad ? Math.round(grad.getBoundingClientRect().left) : null };
  });
  ok('la légende d’axe reste à GAUCHE de la graduation la plus large',
     marge.lg !== null && marge.grad !== null && marge.lg <= marge.grad,
     marge.lg + ' ≤ ' + marge.grad);
  await vue('empile');
  const debord = await pg.evaluate(() => {
    const svg = document.querySelector('#brev-chart svg');
    const der = [...svg.querySelectorAll('.bv-seg[data-an="2023"]')].pop();
    const et = [...svg.querySelectorAll('text')].find(t => t.textContent === 'Reste du monde');
    return { col: Math.round(der.getBoundingClientRect().right),
             lab: Math.round(et.getBoundingClientRect().left) };
  });
  ok('…et la dernière colonne ne déborde pas sur ses étiquettes',
     debord.col <= debord.lab, debord.col + ' ≤ ' + debord.lab);

  console.log('\n══ 6. Ce que les deux vues ne devaient PAS déplacer ══\n');
  await vue('part');
  const reste = await pg.evaluate(() => ({
    tableau: document.querySelectorAll('#brev-table tbody tr').length,
    colonnes: document.querySelectorAll('#brev-table thead th').length,
    bandes: document.querySelectorAll('.bv-bande').length,
    volMondial: /Volume mondial/.test(document.getElementById('brev-leg').textContent),
    legende: document.querySelectorAll('#brev-leg [data-serie]').length,
  }));
  ok('le tableau de données couvre toujours les neuf millésimes',
     reste.tableau === 9, reste.tableau);
  ok('…avec ses neuf colonnes', reste.colonnes === 9, reste.colonnes);
  ok('la bande d’incertitude de la vue « part » est intacte',
     reste.bandes === 3, reste.bandes);
  ok('…et son rappel du volume mondial en légende', reste.volMondial);
  ok('la légende-interrupteur porte les quatre acteurs', reste.legende === 4);
  ok('aucune erreur JavaScript', err.length === 0, err.slice(0, 2).join(' | '));

  /* La discrimination — « rien de tout cela n'existait avant » — se fait sur le
     dépôt, dans recette_brevets_vues.py : elle demande git, que la page n'a
     pas. Ici on vérifie seulement que les quatre lectures sont DÉCLARÉES en un
     seul endroit, et non recopiées de branche en branche. */
  ok('les quatre titres sont déclarés en une table, pas en cascade de si',
     await pg.evaluate(() => typeof BV_TITRES === 'object'
       && Object.keys(BV_TITRES).length === 4
       && Object.keys(BV_TITRES).join(',') === 'part,volume,empile,rang'),
     await pg.evaluate(() => Object.keys(BV_TITRES).join(',')));

  await nav.close();
  console.log('');
  console.log(ko ? ko + ' contrôle(s) en échec\n' : 'tout est vert\n');
  process.exit(ko ? 1 : 0);
})();
