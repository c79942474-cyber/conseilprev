/* Trois lectures d'un même relevé — et ce que chacune doit tenir.
 *
 * 1. LA SOUSTRACTION EXIGE SES DEUX TERMES. Quatre pays sur sept n'ont pas de
 *    lieu de travail publié : ils n'ont donc PAS de solde. Les poser à zéro
 *    les ferait passer pour équilibrés, ce qui est faux et flatteur — un zéro
 *    affiché serait une absence de calcul, pas une absence de mouvement. Ils
 *    doivent être nommés, avec le motif de leur absence.
 *
 * 2. UNE VALEUR NON PUBLIÉE NE SE DESSINE PAS COMME UNE VALEUR. Là où la
 *    source donne une fourchette (« 2–4 % »), la barre est hachurée et posée
 *    au milieu ; là où elle ne donne rien, il n'y a pas de barre du tout.
 *
 * 3. L'ÉCHELLE DIVERGENTE EST SYMÉTRIQUE. Un axe qui s'arrêterait à +29 d'un
 *    côté et à −14 de l'autre ferait paraître la perte chinoise plus grande
 *    qu'elle n'est. Zéro doit être au milieu, et le zéro doit se voir.
 *
 * 4. LES TROIS VUES DISENT LES MÊMES CHIFFRES. Trois formes, un seul relevé :
 *    si l'une d'elles s'écartait du tableau, c'est la page entière qui
 *    perdrait sa crédibilité.
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
  await pg.waitForFunction(() => document.querySelector('#tal-maps svg'), null, { timeout: 30000 });

  const vue = async (v) => {
    await pg.click('#tal-vues [data-tvue="' + v + '"]');
    await pg.waitForTimeout(400);
  };

  console.log('\n══ 1. Trois lectures, et chacune dit ce qu’elle tait ══\n');
  const onglets = await pg.evaluate(() => [...document.querySelectorAll('#tal-vues [data-tvue]')]
    .map(b => ({ v: b.getAttribute('data-tvue'), t: b.textContent.trim() })));
  ok('trois onglets', onglets.length === 3, onglets.map(o => o.v).join(','));
  ok('…le flux d’origine reste le premier, et par défaut',
     onglets[0].v === 'flux', onglets[0].t);
  ok('…suivi des deux lectures en barres',
     onglets[1].v === 'barres' && onglets[2].v === 'solde',
     onglets.map(o => o.t).join(' | '));

  const E = {};
  for (const v of ['flux', 'barres', 'solde']) {
    await vue(v);
    E[v] = await pg.evaluate(() => ({
      vue: TAL_VUE,
      titre: document.getElementById('t-tal').textContent,
      lecture: document.getElementById('tal-lecture').innerText,
      alt: document.querySelector('#tal-maps svg').getAttribute('aria-label'),
      selected: document.querySelector('#tal-vues [aria-selected="true"]').getAttribute('data-tvue'),
      legende: document.querySelector('#tal-maps .tal-leg').innerText,
    }));
  }
  ok('chaque onglet change la vue', Object.keys(E).every(v => E[v].vue === v));
  ok('…et l’état sélectionné suit pour le lecteur d’écran',
     Object.keys(E).every(v => E[v].selected === v));
  ok('trois titres de panneau distincts',
     new Set(Object.keys(E).map(v => E[v].titre)).size === 3,
     E.barres.titre + ' / ' + E.solde.titre);
  ok('…celui du solde annonce des POINTS, pas des pourcentages',
     /solde net.*en points/i.test(E.solde.titre), E.solde.titre);
  ok('trois textes de lecture distincts',
     new Set(Object.keys(E).map(v => E[v].lecture)).size === 3);
  ok('…et chacun écrit ce qu’il ne montre pas',
     Object.keys(E).every(v => /ne montre pas/i.test(E[v].lecture)));
  ok('trois descriptions alternatives distinctes et chiffrées',
     new Set(Object.keys(E).map(v => E[v].alt)).size === 3
     && Object.keys(E).every(v => /\d/.test(E[v].alt)));
  ok('chaque vue porte sa propre légende',
     new Set(Object.keys(E).map(v => E[v].legende)).size === 3);

  console.log('\n══ 2. Une valeur non publiée ne se dessine pas comme une valeur ══\n');
  await vue('barres');
  const bar = await pg.evaluate(() => {
    const svg = document.querySelector('#tal-maps svg');
    const pleines = [...svg.querySelectorAll('path[fill]')]
      .filter(p => /^#/.test(p.getAttribute('fill')));
    const hach = [...svg.querySelectorAll('path[fill^="url(#tal-hach"]')];
    const nd = [...svg.querySelectorAll('.tal-nd')].map(t => t.textContent.trim());
    const pays = DATA.talents.pays;
    return { rangs: svg.querySelectorAll('.tal-row').length,
             pleines: pleines.length, hachurees: hach.length, nd: nd,
             sansT: pays.filter(p => typeof p.t !== 'number').length,
             avecT: pays.filter(p => typeof p.t === 'number').length,
             fourchettes: pays.filter(p => /\d\s*[–-]\s*\d/.test(p.tn || '')).length,
             rien: pays.filter(p => typeof p.t !== 'number'
                                 && !/\d\s*[–-]\s*\d/.test(p.tn || '')).length };
  });
  ok('sept pays, sept lignes', bar.rangs === 7, bar.rangs);
  /* Une barre pleine par origine (7) + une par lieu de travail publié (3). */
  ok('dix barres pleines : sept origines, trois lieux de travail publiés',
     bar.pleines === bar.rangs + bar.avecT, bar.pleines + ' pour 7 + ' + bar.avecT);
  ok('…et trois barres HACHURÉES, une par fourchette publiée',
     bar.hachurees === bar.fourchettes && bar.fourchettes === 3,
     bar.hachurees + ' hachures pour ' + bar.fourchettes + ' fourchettes');
  ok('le pays sans aucune valeur n’a PAS de barre — juste la mention',
     bar.rien === 1 && bar.nd.indexOf('n.d.') >= 0, bar.nd.join(' · '));
  ok('…et chaque valeur non publiée est écrite en toutes lettres',
     bar.nd.length === bar.sansT, bar.nd.length + ' mentions pour ' + bar.sansT + ' inconnues');
  ok('la légende nomme la hachure', /valeur non publiée/i.test(E.barres.legende),
     E.barres.legende);
  /* DISCRIMINATION : la barre hachurée est posée au MILIEU de la fourchette,
     pas à son maximum — un maximum serait la lecture la plus flatteuse. */
  const milieu = await pg.evaluate(() => {
    const svg = document.querySelector('#tal-maps svg');
    const h = svg.querySelector('path[fill^="url(#tal-hach"]');
    const t = h.querySelector('title').textContent;
    return { titre: t, milieu: /au milieu de la fourchette/.test(t) };
  });
  ok('…et son infobulle dit qu’elle est posée au MILIEU de la fourchette',
     milieu.milieu, milieu.titre.slice(0, 80));

  console.log('\n══ 3. La soustraction exige ses deux termes ══\n');
  await vue('solde');
  const sol = await pg.evaluate(() => {
    const svg = document.querySelector('#tal-maps svg');
    const barres = [...svg.querySelectorAll('.tal-row')].map(g => ({
      pays: g.getAttribute('data-pays'),
      fill: g.querySelector('path[fill]').getAttribute('fill'),
      w: Math.round(g.querySelector('path[fill]').getBoundingClientRect().width),
      x: Math.round(g.querySelector('path[fill]').getBoundingClientRect().left) }));
    const pays = DATA.talents.pays;
    const calculables = pays.filter(p => talSolde(p) !== null);
    const absents = document.querySelector('#tal-maps p.note');
    return { barres: barres,
             calculables: calculables.length, total: pays.length,
             absents: absents ? absents.innerText : null,
             etiq: [...svg.querySelectorAll('.tal-sol')].map(t => t.textContent) };
  });
  ok('trois barres seulement, une par solde calculable',
     sol.barres.length === sol.calculables && sol.calculables === 3,
     sol.barres.length + ' barres pour ' + sol.calculables + ' soldes');
  /* LE contrôle : les quatre autres ne sont NULLE PART sur le graphique. */
  ok('…les quatre autres n’ont pas de barre nulle',
     sol.barres.length === 3 && sol.total === 7);
  ok('…mais ils sont NOMMÉS sous le graphique, avec leur motif',
     !!sol.absents && /Inde/.test(sol.absents) && /France/.test(sol.absents)
     && /Allemagne/.test(sol.absents) && /Canada/.test(sol.absents),
     (sol.absents || '').slice(0, 70));
  ok('…et le texte dit pourquoi : une soustraction exige ses deux termes',
     /soustraction exige ses deux termes/.test(sol.absents || ''));
  ok('…et refuse explicitement la barre nulle',
     /pas de barre plutôt qu’une barre nulle/.test(sol.absents || ''));
  ok('le compte est annoncé : 4 pays sur 7',
     /4 pays sur 7/.test(sol.absents || ''), (sol.absents || '').slice(0, 40));

  console.log('\n══ 4. L’axe divergent est symétrique, et son zéro se voit ══\n');
  const axe = await pg.evaluate(() => {
    const svg = document.querySelector('#tal-maps svg');
    const grad = [...svg.querySelectorAll('.tal-axe')].map(t => t.textContent.trim())
      .filter(t => /^[+−]?\d+$/.test(t));
    const zero = [...svg.querySelectorAll('.tal-grille')]
      .find(l => l.getAttribute('stroke') === '#8A8A8A');
    return { grad: grad, zeroMarque: !!zero,
             sens: [...svg.querySelectorAll('.tal-axe')].map(t => t.textContent.trim())
               .filter(t => /EXPORTE|ATTIRE/.test(t)) };
  });
  ok('les graduations vont de −30 à +30, symétriquement',
     axe.grad.join(' ') === '−30 −20 −10 0 +10 +20 +30', axe.grad.join(' '));
  /* Une échelle qui s'arrêterait à la valeur extrême de chaque côté ferait
     paraître −14 aussi long que +29. */
  ok('…et non de −14 à +29, ce qui égaliserait deux écarts inégaux',
     axe.grad.indexOf('−30') === 0 && axe.grad[axe.grad.length - 1] === '+30');
  ok('le zéro porte un trait plus marqué que les autres', axe.zeroMarque);
  ok('les deux côtés sont nommés', axe.sens.length === 2
     && axe.sens.join(' ').indexOf('EXPORTE') >= 0
     && axe.sens.join(' ').indexOf('ATTIRE') >= 0, axe.sens.join(' | '));
  ok('les longueurs suivent les valeurs : +29 est deux fois plus long que −14',
     Math.abs(sol.barres[0].w / sol.barres[2].w - 29 / 14) < 0.12,
     sol.barres[0].w + ' px vs ' + sol.barres[2].w + ' px');
  ok('la barre négative part bien à GAUCHE du zéro',
     sol.barres[2].x < sol.barres[0].x, sol.barres[2].x + ' < ' + sol.barres[0].x);
  ok('les couleurs opposent les deux sens',
     sol.barres[0].fill !== sol.barres[2].fill,
     sol.barres[0].fill + ' vs ' + sol.barres[2].fill);
  /* Une légende qui annonce un état qu'aucune barre n'occupe fait chercher au
     lecteur ce qui n'existe pas. */
  ok('la légende n’annonce pas l’état neutre, qu’aucune barre n’occupe',
     !/inférieur à 1,5/.test(E.solde.legende), E.solde.legende);

  console.log('\n══ 5. Le signe « moins » est le vrai, partout ══\n');
  const signes = await pg.evaluate(async () => {
    const lu = {};
    for (const v of ['flux', 'solde']) {
      document.querySelector('#tal-vues [data-tvue="' + v + '"]').click();
      await new Promise(r => setTimeout(r, 150));
      lu[v] = [...document.querySelectorAll('#tal-maps .tal-sol')].map(t => t.textContent.trim());
    }
    return lu;
  });
  /* U+2212 et non le trait d'union du clavier : le texte du panneau écrit
     « −14 points » et le graphique écrivait « -14 pts ». */
  ok('la vue solde écrit « −14 pts » avec un vrai moins',
     signes.solde.some(t => t.indexOf('−') === 0), signes.solde.join(' · '));
  ok('…et aucune étiquette ne porte le trait d’union',
     signes.solde.every(t => t.indexOf('-') < 0), signes.solde.join(' · '));
  ok('la vue flux a été alignée sur la même règle',
     signes.flux.some(t => t.indexOf('−') === 0)
     && signes.flux.every(t => t.indexOf('-') < 0), signes.flux.join(' · '));

  console.log('\n══ 6. Trois formes, un seul relevé ══\n');
  const memes = await pg.evaluate(async () => {
    const lu = {};
    for (const v of ['flux', 'barres', 'solde']) {
      document.querySelector('#tal-vues [data-tvue="' + v + '"]').click();
      await new Promise(r => setTimeout(r, 150));
      lu[v] = [...document.querySelectorAll('#tal-table tbody tr')]
        .map(tr => [...tr.children].map(c => c.textContent.trim()).join('|')).join(' ~ ');
    }
    /* L'ordre se relève sur la vue qui porte TOUS les pays : la vue solde n'en
       montre que trois, et y vérifier un classement complet ne prouverait
       rien. */
    document.querySelector('#tal-vues [data-tvue="barres"]').click();
    await new Promise(r => setTimeout(r, 150));
    const ordre = [...document.querySelectorAll('#tal-maps .tal-row')]
      .map(g => g.getAttribute('data-pays'));
    return { lu: lu, ordre: ordre };
  });
  ok('le tableau de données est le même sous les trois vues',
     memes.lu.flux === memes.lu.barres && memes.lu.barres === memes.lu.solde,
     memes.lu.solde.split(' ~ ')[0]);
  ok('…et il porte les sept pays', memes.lu.solde.split(' ~ ').length === 7);
  ok('les sept pays sont rangés du plus attractif au plus exportateur',
     memes.ordre.length === 7 && memes.ordre[0] === 'US' && memes.ordre[2] === 'CN',
     memes.ordre.join(','));
  /* Les soldes non calculables ferment la marche : ils ne se comparent à rien,
     et les glisser au milieu du classement leur prêterait un rang. */
  ok('…et les quatre sans solde ferment la marche',
     ['IN', 'FR', 'DE', 'CA'].every(c => memes.ordre.indexOf(c) >= 3),
     memes.ordre.slice(3).join(','));

  console.log('\n══ 7. Ce que les deux vues ne devaient PAS casser ══\n');
  await vue('flux');
  const flux = await pg.evaluate(() => {
    const svg = document.querySelector('#tal-maps svg');
    return { lignes: svg.querySelectorAll('.tal-row').length,
             fleches: svg.querySelectorAll('[marker-end]').length,
             creux: svg.querySelectorAll('circle[stroke-dasharray]').length,
             soldes: svg.querySelectorAll('.tal-sol').length };
  });
  ok('la figure de flux garde ses sept lignes', flux.lignes === 7, flux.lignes);
  ok('…ses flèches de sens', flux.fleches >= 2, flux.fleches);
  ok('…ses cercles creux pour les valeurs non publiées', flux.creux === 4, flux.creux);
  ok('…et sa colonne de soldes', flux.soldes === 7, flux.soldes);
  const survol = await pg.evaluate(() => {
    const g = document.querySelector('#tal-maps .tal-row');
    g.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true, clientX: 300, clientY: 300 }));
    const t = document.querySelector('.tip, #tip, .obs-tip');
    return t ? t.innerText.slice(0, 60) : null;
  });
  ok('le survol répond toujours', !!survol, survol);
  ok('aucune erreur JavaScript', err.length === 0, err.slice(0, 2).join(' | '));

  await nav.close();
  console.log('');
  console.log(ko ? ko + ' contrôle(s) en échec\n' : 'tout est vert\n');
  process.exit(ko ? 1 : 0);
})();
