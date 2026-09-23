/* RECETTE — LE TAUX DE CONFORMITÉ LIT CE QUE LE RAIL LIT
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE : « brancher le taux de conformité sur les mêmes déclarations
 * que le rail, pour que les deux ne se contredisent plus ».
 *
 * CE QUI A ÉTÉ MESURÉ AVANT, DANS CE NAVIGATEUR :
 *   · NIS 2 rempli par ses vrais contrôles jusqu'à trois blocs verts — et la
 *     carte NIS 2 du taux affichait « — » ;
 *   · une fois le taux ouvert, plus rien ne le recalculait de la session ;
 *   · RGPD « 0 % » avant la moindre réponse.
 *
 * CE QUE LES RÈGLES DE LA SUITE NE VOIENT PAS, ET QUE CETTE RECETTE MESURE :
 * l'état INITIAL réel des écrans (les règles le recopient), le passage d'une
 * réponse jusqu'à la carte sans rechargement, le champ « périmètre » réel
 * d'ISO 27001, DORA qui garde son propre rail, et les réponses NIST d'hier
 * relues au chargement.
 *
 * LE LIMITEUR : une ouverture de Sentinel coûte près de cent requêtes, et la
 * limite est de cent vingt par minute. La recette attend que la fenêtre se
 * vide avant de répondre, et encore après le rechargement.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5901 node recette_taux_rail.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
const ATTENTE = Number(process.env.ATTENTE_LIMITEUR || 62000);

let ko = 0, n = 0;
const ok = (t, cond, siKo, mesure) => {
  n++;
  if (!cond) ko++;
  console.log((cond ? '  OK   ' : '  KO   ') + t
              + (mesure ? ' — ' + mesure : '')
              + (!cond && siKo ? ' — ' + siKo : ''));
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
  pg.on('pageerror', e => err.push(String(e).slice(0, 160)));
  const refus = [];
  /* LA DERNIÈRE RÉPONSE DU CALCUL, TELLE QUE LE SERVEUR L'A RENDUE À LA
     PAGE — c'est sur elle qu'on lit le plan. */
  let dernier = null;
  pg.on('response', async r => {
    if (r.status() >= 400) refus.push(r.status() + ' ' + r.url().replace(BASE, ''));
    if (r.url().endsWith('/api/conformite/etat-des-lieux')) {
      try { dernier = await r.json(); } catch (e) {}
    }
  });

  const charger = async () => {
    const rep = await pg.goto(BASE + '/sentinel', { waitUntil: 'domcontentloaded' });
    await pg.waitForSelector('.sb-item[data-norme]', { state: 'attached', timeout: 15000 });
    await pg.waitForTimeout(ATTENTE);
    return rep;
  };
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.waitForTimeout(400);
  const rep = await charger();
  ok('la page répond', rep && rep.status() === 200, rep ? 'HTTP ' + rep.status() : '');
  if (!rep || rep.status() !== 200) { await nav.close(); process.exit(2); }

  const cartes = () => pg.evaluate(() => {
    const out = {};
    document.querySelectorAll('#conf-grille .conf-c').forEach(c => {
      out[c.querySelector('.conf-c-n').textContent.trim()] = {
        val: c.querySelector('.conf-c-v').textContent.trim(),
        verrous: [...c.querySelectorAll('.conf-v')].map(v => v.textContent),
        reserves: [...c.querySelectorAll('.conf-r')].map(v => v.textContent),
        dit: (c.querySelector('.conf-c-d') || {}).textContent || '' };
    });
    return out;
  });
  const ouvrirTaux = async () => {
    await pg.evaluate(() => { go('conf-taux'); confInit(); });
    await pg.waitForTimeout(2600);
    return cartes();
  };
  const ecran = () => pg.evaluate(() => (document.querySelector('.page.on') || {}).id);
  const rail = norme => pg.evaluate(n => [...document.querySelectorAll(
    '.sb-nav .sb-item[data-norme="' + n + '"]')].map(i => i.getAttribute('data-rail')), norme);

  // ── 1 ───────────────────────────────────────────────────────────────────
  titre('1. Avant toute réponse, onze tirets — et aucun zéro');

  let c = await ouvrirTaux();
  const noms = Object.keys(c);
  ok('les onze cartes sont là', noms.length === 11, '', noms.length + ' cartes');
  ok('LE POINT QUI DÉCIDE — aucune ne porte de taux sans réponse',
     noms.every(k => c[k].val === '—'),
     noms.filter(k => c[k].val !== '—').map(k => k + ' = ' + c[k].val).join(', '));
  ok('RGPD dit « — », plus « 0 % »', c['RGPD'] && c['RGPD'].val === '—',
     c['RGPD'] ? c['RGPD'].val : 'carte absente');

  // ── 2 ───────────────────────────────────────────────────────────────────
  titre('2. NIS 2 rempli par ses contrôles : le rail passe au vert, la carte suit');

  await pg.click('.sb-section[data-grp="nis2"]');
  await pg.waitForTimeout(1200);
  await pg.click('.sb-item[data-norme="nis2"] >> nth=0');
  await pg.waitForTimeout(1500);
  await pg.selectOption('#nis2-secteur', 'energie');
  await pg.fill('#nis2-eff', '300'); await pg.dispatchEvent('#nis2-eff', 'change');
  await pg.fill('#nis2-ca2', '60'); await pg.dispatchEvent('#nis2-ca2', 'change');
  await pg.waitForTimeout(1500);
  await pg.evaluate(() => go('nis2'));
  await pg.waitForTimeout(1200);
  for (let i = 0; i < 10; i++) {
    /* CHAQUE RÉPONSE REPEINT LA LISTE : le sélecteur est relu à chaque tour. */
    await pg.locator('#nis2-mesures-body select').nth(i).selectOption(i % 2 ? 'partiel' : 'conforme');
  }
  await pg.evaluate(() => go('nis2-gouvernance'));
  await pg.waitForTimeout(1200);
  const ng = await pg.locator('#nis2-gouv-body select').count();
  for (let i = 0; i < ng; i++) {
    await pg.locator('#nis2-gouv-body select').nth(i).selectOption('conforme');
  }
  await pg.waitForTimeout(1600);
  const r2 = await rail('nis2');
  ok('le rail tient les trois premiers blocs pour remplis',
     r2.slice(0, 3).every(e => e === 'validee'), '', r2.join(' '));
  c = await ouvrirTaux();
  ok('LE POINT QUI DÉCIDE — la carte NIS 2 a un taux, sans rechargement',
     /%/.test(c['NIS 2'].val), 'toujours ' + c['NIS 2'].val, c['NIS 2'].val);
  ok('…et le taux déjà ouvert une fois s\'est recalculé : le cache suit les réponses',
     c['NIS 2'].val !== '—', '');
  ok('la qualification faite, la réserve « non qualifiée » n\'est pas là',
     !c['NIS 2'].reserves.some(t => /pas qualifiée/.test(t)), c['NIS 2'].reserves.join(' | '));

  // ── 3 ───────────────────────────────────────────────────────────────────
  titre('3. « Aucune des deux annexes » : sans objet, et pas un chantier');

  await pg.evaluate(() => go('nis2-qualifier'));
  await pg.waitForTimeout(1000);
  await pg.selectOption('#nis2-secteur', 'hors_annexes');
  await pg.waitForTimeout(1500);
  const r3 = await rail('nis2');
  ok('le rail passe les blocs suivants en « sans objet »',
     r3.slice(1).every(e => e === 'sans_objet'), '', r3.join(' '));
  c = await ouvrirTaux();
  ok('LE POINT QUI DÉCIDE — la carte dit « sans objet », ni « — » ni un taux',
     c['NIS 2'].val === 'sans objet', c['NIS 2'].val, c['NIS 2'].val);
  ok('…et dit pourquoi', /Hors du champ de la directive/.test(c['NIS 2'].dit),
     c['NIS 2'].dit.slice(0, 80));
  const actionsNis2 = ((dernier || {}).plan || {}).actions
    ? dernier.plan.actions.filter(a => (a.normes || []).indexOf('nis2') >= 0) : null;
  ok('le plan ne porte aucune action NIS 2',
     actionsNis2 && actionsNis2.length === 0,
     actionsNis2 ? actionsNis2.map(a => a.quoi).join(' | ') : 'plan illisible');
  /* ON REVIENT DANS LE CHAMP POUR LA SUITE. */
  await pg.evaluate(() => go('nis2-qualifier'));
  await pg.waitForTimeout(800);
  await pg.selectOption('#nis2-secteur', 'energie');
  await pg.waitForTimeout(1200);

  // ── 4 ───────────────────────────────────────────────────────────────────
  titre('4. ISO 27001 : le périmètre a un champ, et le rail et le taux basculent ensemble');

  await pg.click('.sb-section[data-grp="iso27001"]');
  await pg.waitForTimeout(1200);
  await pg.click('.sb-item[data-norme="iso27001"] >> nth=0');
  await pg.waitForTimeout(1800);
  ok('le champ « Domaine d\'application du SMSI (art. 4.3) » est à l\'écran',
     await pg.locator('#iso27-perimetre').isVisible(), 'champ absent ou caché');
  await pg.fill('#iso27-etabli', '2026-01-10'); await pg.dispatchEvent('#iso27-etabli', 'change');
  await pg.fill('#iso27-apprecie', '2026-02-01'); await pg.dispatchEvent('#iso27-apprecie', 'change');
  await pg.waitForTimeout(900);
  await pg.click('#p-iso27001-risques button:has-text("Ajouter un risque")');
  await pg.waitForTimeout(1200);
  await pg.evaluate(() => document.querySelectorAll('#iso27-risques-body details').forEach(d => { d.open = true; }));
  await pg.fill('#iso27-risques-body input[placeholder="Intitulé du risque"]', 'Rançongiciel');
  await pg.dispatchEvent('#iso27-risques-body input[placeholder="Intitulé du risque"]', 'change');
  await pg.waitForTimeout(900);
  await pg.evaluate(() => document.querySelectorAll('#iso27-risques-body details').forEach(d => { d.open = true; }));
  await pg.fill('#iso27-risques-body input[placeholder="Propriétaire du risque"]', 'DSI');
  await pg.dispatchEvent('#iso27-risques-body input[placeholder="Propriétaire du risque"]', 'change');
  await pg.waitForTimeout(900);
  await pg.evaluate(() => document.querySelectorAll('#iso27-risques-body details').forEach(d => { d.open = true; }));
  await pg.locator('#iso27-risques-body input[type="checkbox"]').first().check();
  await pg.waitForTimeout(1600);
  let r4 = await rail('iso27001');
  const ban = await pg.evaluate(() => {
    const b = document.querySelector('.page.on .rail-bandeau');
    return b ? b.innerText.replace(/\s+/g, ' ') : ''; });
  ok('sans périmètre, le bloc « Analyse de risque » n\'est pas vert', r4[0] !== 'validee', '', r4[0]);
  ok('…et le bandeau nomme la réponse qui manque',
     /domaine d'application du SMSI/i.test(ban), ban.slice(0, 160));
  c = await ouvrirTaux();
  ok('…et le taux porte le verrou du périmètre',
     c['ISO/IEC 27001'].verrous.some(t => /périmètre/i.test(t)),
     c['ISO/IEC 27001'].verrous.join(' | ') || 'aucun verrou', c['ISO/IEC 27001'].val);
  await pg.evaluate(() => go('iso27001-risques'));
  await pg.waitForTimeout(1200);
  await pg.fill('#iso27-perimetre', 'SI de production du siège');
  await pg.dispatchEvent('#iso27-perimetre', 'change');
  await pg.waitForTimeout(1600);
  r4 = await rail('iso27001');
  ok('LE POINT QUI DÉCIDE — le périmètre écrit, le bloc passe au vert', r4[0] === 'validee', '', r4[0]);
  /* LE DÉCOMPTE VERS LE BLOC SUIVANT EST LANCÉ. On part voir son taux
     pendant ce temps — MESURÉ : on était ramené de force au bloc suivant. */
  const decompte = await pg.evaluate(() => ((document.querySelector('.page.on .rail-auto-zone') || {}).innerText || '').replace(/\s+/g, ' '));
  c = await ouvrirTaux();
  ok('…et le verrou tombe au taux, au même moment',
     !c['ISO/IEC 27001'].verrous.some(t => /périmètre/i.test(t)),
     c['ISO/IEC 27001'].verrous.join(' | '), c['ISO/IEC 27001'].val);
  await pg.waitForTimeout(3000);
  ok('le décompte était lancé quand on est parti', /Passage à/.test(decompte), decompte.slice(0, 90));
  ok('LE POINT QUI DÉCIDE — partir voir son taux annule le décompte : on reste sur le taux',
     (await ecran()) === 'p-conf-taux', 'ramené de force sur ' + (await ecran()));

  // ── 5 ───────────────────────────────────────────────────────────────────
  titre('5. DORA garde son rail — et son taux suit quand même');

  await pg.click('.sb-section[data-grp="dora"]');
  await pg.waitForTimeout(1200);
  await pg.click('.sb-item[data-norme="dora"] >> nth=0');
  await pg.waitForTimeout(1800);
  await pg.selectOption('#dora-entite', 'etablissement_credit');
  await pg.waitForTimeout(1200);
  await pg.selectOption('#dora-nis2', 'oui');
  await pg.waitForTimeout(1500);
  c = await ouvrirTaux();
  ok('LE POINT QUI DÉCIDE — l\'entité qualifiée, la carte DORA a un taux',
     /%/.test(c['DORA'].val), 'toujours ' + c['DORA'].val, c['DORA'].val);

  // ── 6 ───────────────────────────────────────────────────────────────────
  titre('6. Les réponses d\'hier : relues au chargement, pas à l\'ouverture de leur écran');

  await pg.evaluate(() => { go('nist-profil'); nistInit(); });
  await pg.waitForTimeout(1800);
  await pg.locator('#p-nist-profil .q-sel[data-cle="GOVERN 1"]').selectOption('tenu');
  await pg.waitForTimeout(1200);
  await pg.waitForTimeout(ATTENTE);
  await charger();
  c = await ouvrirTaux();
  ok('LE POINT QUI DÉCIDE — après rechargement, NIST AI RMF a son taux sans rouvrir son écran',
     /%/.test(c['NIST AI RMF'].val), 'toujours ' + c['NIST AI RMF'].val, c['NIST AI RMF'].val);

  // ── 7 ───────────────────────────────────────────────────────────────────
  titre('7. Propreté');
  ok('aucune erreur JavaScript', err.length === 0, err.join(' | '));
  ok('aucune réponse en erreur', refus.length === 0, refus.join(' | '));

  await nav.close();
  console.log('\n' + (n - ko) + ' contrôles passés, ' + ko + ' en échec'
              + (ko ? '' : ' — TOUT EST VERT'));
  process.exit(ko ? 1 : 0);
})().catch(e => { console.error('KO   la recette a rompu : ' + e); process.exit(2); });
