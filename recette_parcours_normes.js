/* RECETTE — LE RAIL DES ONZE RÉFÉRENTIELS, DANS LA BARRE ET DANS L'ÉCRAN
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE : « lorsque chaque bloc de référentiel est rempli, l'afficher en
 * vert et passer automatiquement au bloc suivant — dans NIS 2, "Suis-je
 * concerné ?" puis "Mesures art. 21 §2" — et ainsi de suite jusqu'à la fin,
 * avec des infobulles à chaque fois et une flèche vers le bas, pour les onze
 * normes ».
 *
 * CE QUE LES RÈGLES DE LA SUITE NE VOIENT PAS, ET QUE CETTE RECETTE MESURE :
 *
 *   1. LE PASSAGE AUTOMATIQUE — un minuteur, un changement d'écran, et son
 *      frein « Rester ici ». Rien de cela n'existe dans un fichier.
 *   2. LA BULLE — le `transform` du survol l'enfermait dans son onglet, et
 *      les onglets suivants la recouvraient ligne à ligne. Mesuré à l'écran,
 *      corrigé, et gardé ici.
 *   3. « LU » N'EST PAS VERT — lu sur la couleur CALCULÉE de la pastille.
 *   4. DORA PEINT SA BARRE avec son propre moteur, et la barre suit l'ordre
 *      de son rail.
 *
 * LE LIMITEUR : une ouverture de Sentinel coûte près de cent requêtes, et la
 * limite est de cent vingt par minute. La recette attend donc que la fenêtre
 * se vide avant de commencer à répondre — sans quoi elle mesurerait le
 * limiteur, pas le rail.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5901 node recette_parcours_normes.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
const ATTENTE = Number(process.env.ATTENTE_LIMITEUR || 62000);

let ko = 0;
const ok = (t, cond, siKo, mesure) => {
  console.log((cond ? '  OK   ' : '  KO   ') + t
              + (mesure ? ' — ' + mesure : '')
              + (!cond && siKo ? ' — ' + siKo : ''));
  if (!cond) ko++;
};
const titre = t => console.log('\n══ ' + t + ' ══\n');

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1440, height: 1000 } });
  /* SANS CE MASQUE, LE SERVEUR BLOQUE L'ADRESSE POUR 1800 s. */
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e).slice(0, 140)));
  const refus = [];
  pg.on('response', r => { if (r.status() === 429) refus.push(r.url()); });

  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.waitForTimeout(400);
  const rep = await pg.goto(BASE + '/sentinel', { waitUntil: 'domcontentloaded' });
  ok('la page répond', rep && rep.status() === 200, rep ? 'HTTP ' + rep.status() : 'pas de réponse');
  if (!rep || rep.status() !== 200) { await nav.close(); process.exit(2); }
  await pg.waitForSelector('.sb-item[data-norme]', { state: 'attached', timeout: 15000 });
  await pg.waitForTimeout(ATTENTE);

  const barre = n => pg.evaluate(n => [...document.querySelectorAll('.sb-nav .sb-item[data-norme="' + n + '"]')]
    .map(it => { const pc = it.querySelector('.rail-puce');
      return { etat: it.getAttribute('data-rail'), puce: pc ? pc.textContent : null,
               tab: pc ? pc.getAttribute('tabindex') : null,
               aria: pc ? pc.getAttribute('aria-label') : null,
               fond: pc ? getComputedStyle(pc).backgroundColor : null }; }), n);
  const ecran = () => pg.evaluate(() => document.querySelector('.page.on').id);
  const bandeau = () => pg.evaluate(() => {
    const b = document.querySelector('.page.on .rail-bandeau');
    return b ? b.innerText.replace(/\s+/g, ' ') : ''; });
  const vert = await pg.evaluate(() => { const t = document.createElement('i');
    t.style.color = getComputedStyle(document.documentElement).getPropertyValue('--green');
    document.body.appendChild(t); const c = getComputedStyle(t).color; t.remove(); return c; });

  // ── 1 ───────────────────────────────────────────────────────────────────
  titre('1. Le tiroir NIS 2 s’ouvre avec son rail');

  await pg.click('.sb-section[data-grp="nis2"]');
  await pg.waitForTimeout(1500);
  let b = await barre('nis2');
  ok('une pastille par onglet', b.length === 7 && b.every(x => x.puce), null,
     b.map(x => x.puce).join(' '));
  ok('LE POINT QUI DÉCIDE — la flèche vers le bas désigne le premier bloc',
     b[0].etat === 'courante' && b[0].puce === '↓', JSON.stringify(b[0]));
  ok('…et tout ce qui dépend de la qualification est verrouillé',
     b.slice(1).every(x => x.etat === 'verrouillee'), b.map(x => x.etat).join(' '));
  ok('les pastilles restent hors de la tabulation, et disent leur état',
     b.every(x => x.tab === '-1' && /—\s*\S/.test(x.aria || '')), b.map(x => x.aria).join(' | '));

  // ── 2 ───────────────────────────────────────────────────────────────────
  titre('2. L’écran dit ce qui manque, par son nom');

  await pg.click('.sb-item[data-norme="nis2"] >> nth=0');
  await pg.waitForTimeout(1800);
  let ban = await bandeau();
  ok('le bandeau situe le bloc dans le parcours', /Bloc 1 sur 7 · Suis-je concerné \?/.test(ban),
     ban.slice(0, 120));
  ok('…et nomme la réponse qui manque', /Le secteur d'activité/.test(ban), ban.slice(0, 200));

  // ── 3 ───────────────────────────────────────────────────────────────────
  titre('3. Rempli → vert → passage automatique au bloc suivant');

  await pg.selectOption('#nis2-secteur', 'energie');
  await pg.fill('#nis2-eff', '300'); await pg.dispatchEvent('#nis2-eff', 'change');
  await pg.fill('#nis2-ca2', '60'); await pg.dispatchEvent('#nis2-ca2', 'change');
  await pg.waitForTimeout(1600);
  b = await barre('nis2');
  ok('LE POINT QUI DÉCIDE — le bloc rempli passe au vert', b[0].etat === 'validee'
     && b[0].puce === '✓' && b[0].fond === vert, JSON.stringify(b[0]));
  ok('…et la flèche descend sur « Mesures art. 21 §2 »', b[1].etat === 'courante' && b[1].puce === '↓',
     JSON.stringify(b[1]));
  /* LES LIBELLÉS PORTENT DES ESPACES INSÉCABLES (« art. 21 §2 ») : le texte est
     ramené à des blancs simples avant d'être comparé. */
  const decompte = await pg.evaluate(() => ((document.querySelector('.page.on .rail-auto-zone') || {}).innerText || '').replace(/\s+/g, ' '));
  ok('le décompte annonce le passage, et se laisse arrêter',
     /↓ Passage à Mesures art\. 21 §2/.test(decompte) && /Rester ici/.test(decompte),
     decompte.replace(/\s+/g, ' ').slice(0, 120));
  await pg.waitForTimeout(4800);
  ok('LE POINT QUI DÉCIDE — l’écran des mesures s’est ouvert tout seul',
     (await ecran()) === 'p-nis2', await ecran());
  ban = await bandeau();
  ok('…avec les dix mesures qui manquent, nommées', /Bloc 2 sur 7/.test(ban)
     && /Il manque 10 réponses/.test(ban) && /Mesure a\)/.test(ban), ban.slice(0, 140));

  // ── 4 ───────────────────────────────────────────────────────────────────
  titre('4. Le frein : « Rester ici »');

  for (let i = 0; i < 10; i++) {
    /* CHAQUE RÉPONSE REPEINT LA LISTE DES MESURES : le sélecteur est relu à
       chaque tour, jamais gardé. */
    await pg.locator('#nis2-mesures-body select').nth(i).selectOption('partiel');
  }
  await pg.waitForTimeout(1500);
  const avantFrein = await pg.evaluate(() => ((document.querySelector('.page.on .rail-auto-zone') || {}).innerText || '').replace(/\s+/g, ' '));
  await pg.click('.page.on .rail-auto-zone button:has-text("Rester ici")');
  await pg.waitForTimeout(5200);
  ok('le décompte était lancé', /Passage à Gouvernance art\. 20/.test(avantFrein),
     avantFrein.replace(/\s+/g, ' ').slice(0, 100));
  ok('LE POINT QUI DÉCIDE — « Rester ici » garde l’écran', (await ecran()) === 'p-nis2',
     await ecran());

  // ── 5 ───────────────────────────────────────────────────────────────────
  titre('5. L’infobulle, au-dessus des onglets voisins');

  await pg.hover('.sb-item[data-norme="nis2"] >> nth=0 >> .rail-puce');
  await pg.waitForTimeout(450);
  const bulle = await pg.evaluate(() => {
    const pc = document.querySelector('.sb-item[data-norme="nis2"] .rail-puce');
    const it = pc.closest('.sb-item');
    const sb = document.querySelector('.sb').getBoundingClientRect(), r = it.getBoundingClientRect();
    const cs = getComputedStyle(pc, '::after');
    /* LE TEST QUI COMPTE : l'élément peint au point où la bulle devrait se
       lire, juste sous l'onglet. Si c'est l'onglet suivant, la bulle est
       dessous. */
    const x = r.left + r.width / 2, y = r.bottom + 14;
    const dessus = document.elementFromPoint(x, y);
    return { opacite: cs.opacity, zindex: getComputedStyle(it).zIndex,
             texte: (pc.getAttribute('data-tooltip') || '').split('\n')[0],
             dedans: r.right <= sb.right + 1,
             voisinDessus: !!(dessus && dessus.closest('.sb-item') && dessus.closest('.sb-item') !== it) };
  });
  ok('la bulle s’ouvre au survol, et dit le bloc et son état',
     bulle.opacite === '1' && /Suis-je concerné \? — Validé/.test(bulle.texte), JSON.stringify(bulle));
  ok('LE POINT QUI DÉCIDE — l’onglet survolé passe au-dessus de ses voisins',
     Number(bulle.zindex) > 0, 'z-index ' + bulle.zindex);
  ok('…et elle reste dans la largeur de la barre', bulle.dedans, JSON.stringify(bulle));
  await pg.mouse.move(900, 500);

  // ── 6 ───────────────────────────────────────────────────────────────────
  titre('6. Un écran à lire se marque lu — et « lu » n’est pas vert');

  await pg.evaluate(() => go('nis2-gouvernance'));
  await pg.waitForTimeout(1200);
  const ng = await pg.locator('#nis2-gouv-body select').count();
  for (let i = 0; i < ng; i++) {
    await pg.locator('#nis2-gouv-body select').nth(i).selectOption('conforme');
  }
  await pg.waitForTimeout(6000);
  ok('le décompte a mené à l’écran à lire', (await ecran()) === 'p-nis2-signalement', await ecran());
  const pied = await pg.evaluate(() => (document.querySelector('.page.on .rail-pied') || {}).innerText || '');
  ok('son pied porte le bouton de lecture', /J’ai lu cet écran — bloc suivant ↓/.test(pied),
     pied.replace(/\s+/g, ' ').slice(0, 80));
  await pg.click('.page.on .rail-pied button');
  await pg.waitForTimeout(1600);
  ok('LE POINT QUI DÉCIDE — le clic « ↓ » ouvre le bloc suivant sans décompte',
     (await ecran()) === 'p-recyf-objectifs', await ecran());
  b = await barre('nis2');
  ok('…et l’écran lu est marqué lu, pas validé', b[3].etat === 'lue', b[3].etat);
  ok('…sans le vert de la validation', b[3].fond !== vert, b[3].fond + ' / vert ' + vert);

  // ── 7 ───────────────────────────────────────────────────────────────────
  titre('7. « Aucune des deux annexes » ferme le parcours, et le dit');

  await pg.evaluate(() => go('nis2-qualifier'));
  await pg.waitForTimeout(1200);
  await pg.selectOption('#nis2-secteur', 'hors_annexes');
  await pg.waitForTimeout(1600);
  b = await barre('nis2');
  ok('tout ce qui suit la qualification est sans objet',
     b[0].etat === 'validee' && b.slice(1).every(x => x.etat === 'sans_objet'), b.map(x => x.etat).join(' '));
  ban = await bandeau();
  ok('…et le bandeau conclut sans se féliciter', /Parcours terminé/.test(ban)
     && /hors du champ de la directive/.test(ban) && /n'y en a pas/.test(ban), ban.slice(0, 200));

  // ── 8 ───────────────────────────────────────────────────────────────────
  titre('8. DORA peint sa barre avec son propre moteur');

  await pg.click('.sb-section[data-grp="dora"]');
  await pg.waitForTimeout(2500);
  b = await barre('dora');
  ok('six pastilles, la flèche sur la qualification', b.length === 6 && b[0].puce === '↓'
     && b.slice(1).every(x => x.etat === 'verrouillee'), b.map(x => x.etat + ':' + x.puce).join(' '));
  const ordre = await pg.evaluate(() => [...document.querySelectorAll('.sb-item[data-norme="dora"]')]
    .map(it => (it.getAttribute('onclick').match(/go\('([\w-]+)'/) || [])[1]));
  ok('…dans l’ordre de son rail, le SMSI en deuxième', ordre[1] === 'dora-iso', ordre.join(' '));

  // ── 9 ───────────────────────────────────────────────────────────────────
  /* CETTE SECTION DISAIT L'INVERSE, ET C'ÉTAIT LE DÉFAUT : « une liste à
     cases se valide sur une revue déclarée ». L'audit demande désormais une
     réponse par point, et se mesure — recette_revues_mesurees.js le suit
     écran par écran, pour les six listes. */
  titre('9. Une liste se mesure : plus de revue à déclarer');

  await pg.evaluate(() => go('audit-ia-act'));
  await pg.waitForTimeout(1800);
  ban = await bandeau();
  ok('le bandeau nomme les points sans réponse, et ne parle plus de revue',
     /Il manque 34 réponses/.test(ban) && !/en revue/.test(ban), ban.slice(0, 160));
  const piedAudit = await pg.evaluate(() => (document.querySelector('.page.on .rail-pied') || {}).innerText || '');
  ok('…et l’écran n’offre plus de bouton pour la déclarer', !/en revue/i.test(piedAudit),
     piedAudit.replace(/\s+/g, ' ').slice(0, 80) || '(aucun pied)');
  await pg.evaluate(() => {
    document.querySelectorAll('#audit-sections select').forEach(s => {
      s.value = 'done'; s.dispatchEvent(new Event('change', { bubbles: true })); });
  });
  await pg.waitForTimeout(2200);
  b = await barre('ia_act');
  ok('LE POINT QUI DÉCIDE — chaque point répondu, l’audit passe au vert',
     b.length === 2 && b[1].etat === 'validee' && b[1].fond === vert, JSON.stringify(b[1]));
  ok('…et la vue d’ensemble, jamais lue, reste le bloc attendu', b[0].etat === 'courante',
     b[0].etat);

  // ── 10 ──────────────────────────────────────────────────────────────────
  titre('10. Rien ne s’est cassé en route');
  ok('aucune erreur de script', err.length === 0, err.slice(0, 2).join(' | '));
  ok('aucune requête refusée par le limiteur — la recette a mesuré le rail',
     refus.length === 0, refus.slice(0, 3).join(' | '));

  console.log('\n' + (ko ? ko + ' contrôle(s) en échec' : 'TOUT EST VERT'));
  await nav.close();
  process.exit(ko ? 1 : 0);
})();
