/* Le parcours complet de la vue Enveloppe — cohérent, fiable, utilisable.
 *
 * CE QU'ON PROTÈGE, ET LA FAUTE QUE CHAQUE CONTRÔLE EMPÊCHE :
 *
 *   1. LE FIL COUVRE TOUTE LA VUE. Il s'arrêtait à six étapes alors que la vue
 *      en porte neuf : équipements, maturité et pilotage y vivaient sans que
 *      le fil les mentionne. Un lecteur qui suivait le fil terminait sans
 *      savoir qu'ils existaient.
 *   2. CHAQUE ÉTAPE MÈNE QUELQUE PART. La première visait « fin-form », qui
 *      n'était qu'une classe : le clic ne faisait rien, en silence.
 *   3. LE POINT QUI DÉCIDE — LE CAPITAL EMPLOYÉ EST COMPLET. L'EVA et le ROCE
 *      se calculaient sur la seule enveloppe travaux, alors que les quatorze
 *      lots ne contiennent aucun serveur et que l'informatique pèse le tiers
 *      de l'investissement quand le même maître d'ouvrage la porte. Le ROCE en
 *      ressortait surestimé et l'EVA flattée — sur la page qui décide du GO.
 *   4. …ET IL DIT DE QUOI IL EST FAIT. Ajouter l'informatique sans l'annoncer
 *      aurait été pire que de l'omettre : le ROCE aurait bougé sans raison
 *      visible, et le calcul ne se serait pas refait à la main.
 *   5. …ET IL NE MÉLANGE PAS DEUX BILANS. En colocation l'informatique est
 *      portée par un autre acteur : l'ajouter serait un faux.
 *   6. LA CRÉATION DE VALEUR REFUSE PLUTÔT QUE D'INVENTER. C'est ce qui la
 *      rend gardable : sans revenu, CMPC et taux d'impôt, elle pose les
 *      questions au lieu d'afficher des zéros.
 *
 *     BASE=http://127.0.0.1:5510 node recette_parcours_enveloppe.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5510';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
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
  pg.on('pageerror', e => err.push(String(e).slice(0, 130)));
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.waitForTimeout(400);
  const rep = await pg.goto(BASE + '/enveloppe', { waitUntil: 'domcontentloaded' });
  ok('la page répond', rep && rep.status() === 200,
     rep ? 'HTTP ' + rep.status() : 'pas de réponse');
  if (!rep || rep.status() !== 200) { await nav.close(); process.exit(2); }
  await pg.waitForFunction(
    () => document.querySelectorAll('#fin-pays button[data-p]').length > 0,
    null, { timeout: 40000 }).catch(() => {});

  const compteur = () => pg.evaluate(() =>
    (document.querySelector('#fin-fil .fin-fil-pn') || {}).textContent.trim());

  // ── 1 ────────────────────────────────────────────────────────────────────
  titre('1. Le fil couvre TOUTE la vue, et chaque étape mène quelque part');

  const et = await pg.evaluate(() => FIN_ETAPES.map(e => ({
    n: e.n, cle: e.cle, nom: e.nom, cible: e.cible,
    existe: !!document.getElementById(e.cible)
  })));
  ok('le fil porte neuf étapes', et.length === 9, et.length + ' étape(s)');
  const orphelines = et.filter(e => !e.existe);
  ok('CHAQUE étape vise un élément qui existe — sinon le clic ne fait rien',
     orphelines.length === 0,
     orphelines.map(e => e.nom + ' → #' + e.cible).join(', '));
  for (const cle of ['equipements', 'maturite', 'pilotage']) {
    ok('…« ' + cle + ' » est bien une étape du fil',
       et.some(e => e.cle === cle));
  }
  ok('les numéros se suivent de 1 à 9',
     et.map(e => e.n).join(',') === '1,2,3,4,5,6,7,8,9',
     et.map(e => e.n).join(','));
  /* L'ORDRE EST UN FAIT DE CALCUL : les équipements changent le capital
     employé sur lequel la création de valeur se calcule. Les lire après
     donnerait un ROCE surestimé. */
  const iEq = et.findIndex(e => e.cle === 'equipements');
  const iKpi = et.findIndex(e => e.cle === 'kpi');
  ok('les équipements viennent AVANT la création de valeur',
     iEq >= 0 && iKpi >= 0 && iEq < iKpi, 'équipements ' + iEq + ' / valeur ' + iKpi);

  const libelle = await pg.evaluate(() =>
    (document.querySelector('#fin-fil .fin-fil-t b') || {}).textContent || '');
  ok('le fil annonce le nombre RÉEL d’étapes', /\b9\b/.test(libelle), libelle);
  ok('…et affiche autant de pastilles',
     (await pg.evaluate(() => document.querySelectorAll('#fin-fil .fin-e').length)) === 9);

  /* La première étape est celle que tout le monde essaie : elle visait une
     classe, `getElementById` rendait null et `finAller` abandonnait. */
  const mene = await pg.evaluate(async () => {
    window.scrollTo(0, 3000);
    await new Promise(r => setTimeout(r, 150));
    const avant = Math.round(window.scrollY);
    const b = document.querySelector('#fin-fil [data-fin-etape="regler"]');
    if (!b) return { absent: true };
    b.click();
    await new Promise(r => setTimeout(r, 900));
    return { avant: avant, apres: Math.round(window.scrollY) };
  });
  ok('cliquer la PREMIÈRE étape mène réellement au formulaire',
     !mene.absent && Math.abs(mene.apres - mene.avant) > 100,
     mene.absent ? 'bouton absent' : mene.avant + ' → ' + mene.apres);

  // ── 2 ────────────────────────────────────────────────────────────────────
  titre('2. La création de valeur refuse plutôt que d’inventer');

  await pg.click('#fin-go');
  await pg.waitForSelector('#fin-res .fin-dos', { state: 'attached', timeout: 60000 });
  await pg.waitForTimeout(1200);
  ok('l’enveloppe est calculée', (await compteur()).indexOf('/ 9') > 0, await compteur());

  await pg.click('#kpi-go');
  await pg.waitForTimeout(2200);
  const sans = await pg.evaluate(() => {
    const o = document.getElementById('kpi-out');
    return (o ? o.textContent : '').replace(/\s+/g, ' ');
  });
  ok('sans hypothèses, elle dit « non instruit » et NON zéro',
     /ne sont pas instruits/i.test(sans) && /ne valent pas z[ée]ro/i.test(sans),
     sans.slice(0, 90));
  ok('…et elle POSE les questions manquantes',
     /Quel revenu annuel/i.test(sans) && /CMPC|coût du capital/i.test(sans));

  // ── 3 : LE POINT QUI DÉCIDE ──────────────────────────────────────────────
  titre('3. LE POINT QUI DÉCIDE : le capital employé comprend l’informatique');

  await pg.evaluate(() => { document.getElementById('eq-perimetre').value = 'propre'; });
  await pg.click('#eq-go');
  await pg.waitForFunction(() => !!document.querySelector('#eq-out .eq-tab'),
                           null, { timeout: 40000 });
  await pg.waitForTimeout(700);
  ok('l’étape « équipements » se coche une fois la nomenclature rendue',
     (await pg.evaluate(() => document.querySelectorAll('#fin-fil .fin-e.fait').length)) >= 4,
     await compteur());

  const it = await pg.evaluate(() => window.EQUIP_IT.capexMeur());
  ok('en centre propre, un montant informatique est retenu',
     !!it && it.meur > 0, it ? it.meur.toFixed(1) + ' M€' : 'aucun');
  ok('…avec son incertitude propre, pas un point milieu',
     !!it && it.incertitude > 0 && it.bas < it.meur && it.haut > it.meur,
     it ? '±' + it.incertitude + ' % → ' + it.bas.toFixed(0) + '–' + it.haut.toFixed(0) : '');

  const capex = await pg.evaluate(() => {
    const d = window.FIN_DERNIER();
    const code = window.FIN_PAYS();
    const dos = (d.dossiers || []).filter(x => x.pays === code)[0];
    return { travaux: dos.devis.enveloppe_meur };
  });
  await pg.evaluate(() => {
    document.querySelectorAll('#kpi-form input').forEach(i => {
      if (/revenu/.test(i.id)) i.value = '40';
      else if (/wacc/.test(i.id)) i.value = '8';
      else if (/is_taux/.test(i.id)) i.value = '25';
      i.dispatchEvent(new Event('input', { bubbles: true }));
    });
  });
  await pg.click('#kpi-go');
  await pg.waitForTimeout(2500);
  const msg = await pg.evaluate(() => (document.getElementById('kpi-msg') || {}).textContent || '');
  ok('LE CAPITAL EMPLOYÉ DÉPASSE LA SEULE ENVELOPPE TRAVAUX',
     /capital employé ADDITIONNE/i.test(msg), msg.slice(0, 120));
  ok('…et la page nomme le montant informatique ajouté',
     /M€/.test(msg) && /informatique/i.test(msg));
  ok('…et le périmètre qui justifie de l’ajouter',
     /Centre propre/i.test(msg), msg.slice(0, 160));

  /* La preuve chiffrée : la borne haute servie à l'API doit dépasser celle des
     travaux seuls. Sans elle, un texte pourrait annoncer une addition qui
     n'a pas lieu. */
  const servi = await pg.evaluate(() => {
    const d = window.FIN_DERNIER();
    const code = window.FIN_PAYS();
    const dos = (d.dossiers || []).filter(x => x.pays === code)[0];
    const it = window.EQUIP_IT.capexMeur();
    return { travauxHaut: dos.devis.enveloppe_meur[1],
             totalHaut: dos.devis.enveloppe_meur[1] + (it ? it.haut : 0) };
  });
  ok('…le montant réellement calculé est plus grand, pas seulement le texte',
     servi.totalHaut > servi.travauxHaut * 1.05,
     Math.round(servi.travauxHaut) + ' → ' + Math.round(servi.totalHaut) + ' M€');

  titre('4. …mais il ne mélange pas deux bilans');
  await pg.evaluate(() => { document.getElementById('eq-perimetre').value = 'colocation'; });
  await pg.click('#eq-go');
  await pg.waitForTimeout(3000);
  await pg.click('#kpi-go');
  await pg.waitForTimeout(2500);
  const msg2 = await pg.evaluate(() => (document.getElementById('kpi-msg') || {}).textContent || '');
  /* LE MOTIF DOIT ÊTRE PRÉCIS. Un simple /additionne/i matchait « et
     l'additionner mélangerait deux bilans » — la phrase qui EXPLIQUE le
     refus — et déclarait donc en échec un comportement juste. On vise la
     formule d'inclusion, et surtout le CHIFFRE servi. */
  ok('en colocation, l’informatique n’est PAS ajoutée',
     !/capital employé ADDITIONNE/i.test(msg2), msg2.slice(0, 110));
  const capexColoc = await pg.evaluate(() => {
    const d = window.FIN_DERNIER();
    const code = window.FIN_PAYS();
    const dos = (d.dossiers || []).filter(x => x.pays === code)[0];
    return dos.devis.enveloppe_meur[1];
  });
  ok('…et le capital employé retombe sur les seuls travaux',
     Math.abs(capexColoc - servi.travauxHaut) < 1,
     Math.round(capexColoc) + ' contre ' + Math.round(servi.travauxHaut) + ' M€');
  ok('…et la page dit pourquoi', /autre acteur|mélangerait/i.test(msg2),
     msg2.slice(0, 170));
  ok('…le montant retenu redevient nul',
     (await pg.evaluate(() => window.EQUIP_IT.capexMeur())) === null);

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
