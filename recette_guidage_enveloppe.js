/* Le guidage de la vue Enveloppe : phases qui battent, flèche qui pointe.
 *
 * CE QU'ON PROTÈGE, ET LA FAUTE QUE CHAQUE CONTRÔLE EMPÊCHE :
 *
 *   1. LE GUIDAGE EST ARMÉ D'EMBLÉE. Il partait éteint : sur une page de
 *      quatorze écrans, le lecteur devait d'abord trouver le bouton
 *      « Guidez-moi » pour qu'il se passe quoi que ce soit. Un parcours guidé
 *      qu'il faut débloquer soi-même ne guide personne.
 *   2. LES PHASES NON VALIDÉES BATTENT, les validées non. Sans cela le fil ne
 *      distinguait le fait du reste que par une couleur, immobile.
 *   3. LA CADENCE RESTE SOUS LE SEUIL DE SÉCURITÉ. Au-delà de trois éclats par
 *      seconde, un clignotement devient un risque pour les personnes
 *      photosensibles. Ce contrôle mesure la durée du cycle : ce n'est pas un
 *      détail de style, c'est une limite.
 *   4. LE POINT QUI DÉCIDE — LA FLÈCHE POINTE DANS LA BONNE DIRECTION. Vers le
 *      bas quand le bloc est plus loin, vers le HAUT quand on l'a dépassé. Une
 *      flèche qui pointerait toujours vers le bas ferait descendre quelqu'un
 *      qui devait remonter, et ruinerait la confiance dans tout le guidage.
 *   5. ELLE SE TAIT QUAND ELLE N'A RIEN À DIRE : bloc sous les yeux, parcours
 *      terminé, ou guide fermé par le lecteur.
 *   6. MOUVEMENT RÉDUIT : plus rien ne bouge, et rien n'est perdu.
 *
 *     BASE=http://127.0.0.1:5510 node recette_guidage_enveloppe.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5510';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
let ko = 0;
const ok = (n, c, d) => { console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : '')); if (!c) ko++; };
const titre = t => console.log('\n══ ' + t + ' ══\n');

(async () => {
  const nav = await chromium.launch();

  const ouvrir = async (reduit) => {
    const ctx = await nav.newContext({ viewport: { width: 1500, height: 950 },
      reducedMotion: reduit ? 'reduce' : 'no-preference' });
    await ctx.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', { get: () => false });
      Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
      Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
    });
    const pg = await ctx.newPage();
    await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
    await pg.waitForTimeout(300);
    await pg.goto(BASE + '/enveloppe', { waitUntil: 'domcontentloaded' });
    await pg.waitForFunction(() => !!document.querySelector('#fin-fil .fin-fil-p'),
                             null, { timeout: 30000 }).catch(() => {});
    await pg.waitForTimeout(700);
    return pg;
  };

  const pg = await ouvrir(false);
  const err = [];
  pg.on('pageerror', e => err.push(String(e).slice(0, 130)));

  const fleche = () => pg.evaluate(() => {
    const f = document.getElementById('fin-fleche-guide');
    if (!f) return null;
    return {
      sens: f.getAttribute('data-sens'),
      fleche: (f.querySelector('.fin-fg-a') || {}).textContent || '',
      texte: f.textContent.replace(/\s+/g, ' ').trim(),
      aria: f.getAttribute('aria-label') || '',
      fixe: getComputedStyle(f).position,
      fermeture: !!f.querySelector('.fin-fg-x')
    };
  });

  // ── 1 ────────────────────────────────────────────────────────────────────
  titre('1. Le guidage est armé d’emblée — plus rien à débloquer');

  ok('le mode pas à pas est actif dès l’arrivée',
     await pg.evaluate(() => window.FIN_GUIDE === true));
  const f0 = await fleche();
  ok('une flèche de guidage est posée sans rien cliquer', !!f0,
     f0 ? f0.texte.slice(0, 50) : 'aucune');
  ok('…elle ne défile pas avec la page', !!f0 && f0.fixe === 'fixed', f0 && f0.fixe);
  ok('…elle nomme l’étape et son rang', !!f0 && /Étape \d+ sur \d+/.test(f0.texte),
     f0 && f0.texte.slice(0, 46));
  ok('…et elle porte sa propre fermeture', !!f0 && f0.fermeture);

  // ── 2 ────────────────────────────────────────────────────────────────────
  titre('2. Les phases non validées battent, les validées non');

  const bat = await pg.evaluate(() => {
    const lire = (sel) => [...document.querySelectorAll(sel)].map(e => {
      const s = getComputedStyle(e);
      return { nom: s.animationName, duree: s.animationDuration,
               iter: s.animationIterationCount };
    });
    return {
      reste: lire('#fin-fil .fin-e.reste .fin-e-n'),
      cours: lire('#fin-fil .fin-e.cours .fin-e-n'),
      fait: lire('#fin-fil .fin-e.fait .fin-e-n')
    };
  });
  ok('les étapes qui restent battent',
     bat.reste.length > 0 && bat.reste.every(x => x.nom !== 'none'),
     bat.reste.length + ' pastille(s), animation ' + (bat.reste[0] || {}).nom);
  ok('l’étape COURANTE bat aussi, et différemment',
     bat.cours.length === 1 && bat.cours[0].nom !== 'none'
       && bat.cours[0].nom !== (bat.reste[0] || {}).nom,
     (bat.cours[0] || {}).nom);
  ok('les étapes VALIDÉES ne battent pas — c’est ce qui les distingue',
     bat.fait.length > 0 && bat.fait.every(x => x.nom === 'none'),
     bat.fait.length + ' validée(s), animation ' + (bat.fait[0] || {}).nom);

  // ── 3 ────────────────────────────────────────────────────────────────────
  titre('3. La cadence reste sous le seuil de sécurité (3 éclats/seconde)');

  const cycles = [...bat.reste, ...bat.cours].map(x => parseFloat(x.duree));
  const plusRapide = Math.min.apply(null, cycles.concat([
    parseFloat(await pg.evaluate(() => {
      const f = document.getElementById('fin-fleche-guide');
      return f ? getComputedStyle(f).animationDuration : '99s';
    }))]));
  ok('aucun clignotement ne descend sous 0,34 s de cycle',
     plusRapide >= 0.34,
     'cycle le plus court : ' + plusRapide + ' s (' + (1 / plusRapide).toFixed(2) + ' Hz)');
  ok('…et la cadence retenue reste lente, donc lisible',
     plusRapide >= 1.0, plusRapide + ' s');

  // ── 4 : LE POINT QUI DÉCIDE ──────────────────────────────────────────────
  titre('4. LE POINT QUI DÉCIDE : la flèche pointe dans la bonne direction');

  /* On se place AU-DESSUS du bloc courant : elle doit inviter à descendre. */
  await pg.evaluate(() => window.scrollTo(0, 0));
  await pg.waitForTimeout(450);
  const enHaut = await fleche();
  ok('au-dessus du bloc, la flèche pointe VERS LE BAS',
     !!enHaut && enHaut.sens === 'bas' && enHaut.fleche.indexOf('▼') >= 0,
     enHaut ? enHaut.sens + ' ' + enHaut.fleche : 'aucune');
  ok('…et son libellé accessible le dit aussi',
     !!enHaut && /plus bas/.test(enHaut.aria), enHaut && enHaut.aria);

  /* On descend BIEN AU-DELÀ : elle doit inviter à remonter. */
  await pg.evaluate(() => window.scrollTo(0, document.body.scrollHeight - 1200));
  await pg.waitForTimeout(600);
  const enBas = await fleche();
  ok('sous le bloc, la flèche pointe VERS LE HAUT',
     !!enBas && enBas.sens === 'haut' && enBas.fleche.indexOf('▲') >= 0,
     enBas ? enBas.sens + ' ' + enBas.fleche : 'aucune');
  ok('…et son libellé accessible le dit aussi',
     !!enBas && /plus haut/.test(enBas.aria), enBas && enBas.aria);
  ok('LES DEUX SENS SONT BIEN DIFFÉRENTS — la flèche ne pointe pas toujours pareil',
     !!enHaut && !!enBas && enHaut.sens !== enBas.sens,
     (enHaut || {}).sens + ' puis ' + (enBas || {}).sens);

  titre('5. Elle se tait quand elle n’a rien à dire, et elle mène où elle dit');

  /* Cliquer la flèche doit conduire au bloc — et donc la faire disparaître. */
  await pg.evaluate(() => window.scrollTo(0, 0));
  await pg.waitForTimeout(400);
  const cible = await pg.evaluate(() => FIN_ETAPES[finPasCourant()].cible);
  await pg.click('#fin-fleche-guide');
  await pg.waitForTimeout(1400);
  const arrive = await pg.evaluate((id) => {
    const e = document.getElementById(id);
    if (!e) return null;
    const r = e.getBoundingClientRect();
    return { visible: r.top > -200 && r.top < window.innerHeight };
  }, cible);
  ok('cliquer la flèche mène au bloc de l’étape', !!arrive && arrive.visible);
  ok('…et une fois le bloc sous les yeux, elle s’efface',
     (await fleche()) === null);

  /* La fermeture doit tenir. */
  await pg.evaluate(() => window.scrollTo(0, 0));
  await pg.waitForTimeout(450);
  ok('elle revient quand on s’éloigne du bloc', (await fleche()) !== null);
  await pg.click('.fin-fg-x');
  await pg.waitForTimeout(300);
  ok('le lecteur peut la fermer', (await fleche()) === null);
  await pg.evaluate(() => window.scrollTo(0, 4000));
  await pg.waitForTimeout(500);
  ok('…et elle ne revient pas sans qu’il le demande', (await fleche()) === null);

  /* Couper le guidage retire tout ; le rallumer rouvre la flèche fermée. */
  await pg.evaluate(() => { document.getElementById('fin-fil-g').click(); });
  await pg.waitForTimeout(400);
  ok('couper le guidage éteint le mode', await pg.evaluate(() => window.FIN_GUIDE === false));
  await pg.evaluate(() => { document.getElementById('fin-fil-g').click(); });
  await pg.waitForTimeout(500);
  await pg.evaluate(() => window.scrollTo(0, 4000));
  await pg.waitForTimeout(500);
  ok('le rallumer rouvre la flèche, même fermée auparavant',
     (await fleche()) !== null);

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  // ── 6 ────────────────────────────────────────────────────────────────────
  titre('6. Mouvement réduit : plus rien ne bouge, et rien n’est perdu');

  const pg2 = await ouvrir(true);
  const immobile = await pg2.evaluate(() => {
    const lire = (sel) => [...document.querySelectorAll(sel)]
      .map(e => getComputedStyle(e).animationName);
    const f = document.getElementById('fin-fleche-guide');
    return {
      pastilles: lire('#fin-fil .fin-e-n'),
      fleche: f ? getComputedStyle(f).animationName : null,
      flechePresente: !!f,
      contraste: lire('#fin-fil .fin-e.cours .fin-e-n').length
    };
  });
  ok('aucune pastille ne bat', immobile.pastilles.every(n => n === 'none'),
     immobile.pastilles.filter(n => n !== 'none').join(', ') || 'toutes immobiles');
  ok('la flèche ne bat pas non plus',
     immobile.fleche === null || immobile.fleche === 'none', immobile.fleche);
  ok('…MAIS elle est toujours là : on ne prive pas de guidage',
     immobile.flechePresente);
  ok('…et l’étape courante reste distinguée', immobile.contraste === 1);
  await pg2.close();

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
