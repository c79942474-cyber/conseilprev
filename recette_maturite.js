/* Maturité analytique décisionnelle, sur /enveloppe — vue par un lecteur.
 *
 * CE QU'ON PROTÈGE, ET LA FAUTE QUE CHAQUE CONTRÔLE EMPÊCHE :
 *
 *   1. LE DIAGNOSTIC EST EN COMPLÉMENT, PAS FONDU DANS L'ÉTUDE. Les deux
 *      sections coexistent sur la vue enveloppe : l'une calcule sur le
 *      PROJET, l'autre évalue l'ORGANISATION. Les fondre ferait croire qu'un
 *      score de maturité déplace un montant.
 *   2. LE GLOBAL EST LE MAILLON FAIBLE. Un seul constat à zéro doit faire
 *      tomber le global à zéro À L'ÉCRAN — pas seulement dans le module.
 *      Une moyenne affichée serait plus flatteuse et enverrait travailler ce
 *      qui tient déjà.
 *   3. L'APPORT DE L'ÉTUDE EST CONSTATÉ. Sans calcul lancé, la page ne doit
 *      annoncer aucun apport disponible : promettre « l'enveloppe couvre vos
 *      projections » sans l'avoir calculée est le raccourci que ce module
 *      dénonce.
 *   4. LA RESTITUTION EST LÀ, VERDICT EN TÊTE. C'est la règle de conduite :
 *      présenter tôt, même si cela déçoit.
 *
 *     BASE=http://127.0.0.1:5510 node recette_maturite.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5510';
const TOKEN = process.env.RECETTE_TOKEN || 'recette_locale_idf_0123456789abcdef';
let ko = 0;
const ok = (n, c, d) => { console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : '')); if (!c) ko++; };
const titre = (t) => console.log('\n══ ' + t + ' ══\n');

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1400, height: 950 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.waitForTimeout(500);

  titre('1. La section est SUR la vue enveloppe, à côté de l’étude');

  const rep = await pg.goto(BASE + '/enveloppe', { waitUntil: 'domcontentloaded' });
  ok('la page répond', rep && rep.status() === 200, rep ? 'HTTP ' + rep.status() : 'pas de réponse');
  if (!rep || rep.status() !== 200) { await nav.close(); process.exit(2); }

  let arme = true;
  try {
    await pg.waitForFunction(() =>
      document.querySelectorAll('#mat-form select').length > 0, null, { timeout: 25000 });
  } catch (e) { arme = false; }
  const vue = await pg.evaluate(() => {
    const m = document.getElementById('s-maturite');
    const f = document.getElementById('s-finance');
    const vis = (e) => !!e && !e.hidden && e.getBoundingClientRect().height > 0;
    return {
      maturiteVisible: vis(m), financeVisible: vis(f),
      selects: document.querySelectorAll('#mat-form select').length,
      axes: document.querySelectorAll('#mat-form fieldset').length,
      /* L'ordre compte : le diagnostic vient APRÈS les chiffres — on ne
         demande pas à une organisation si elle sait décider avant de lui
         avoir montré sur quoi. */
      apresFinance: !!(m && f) && (f.compareDocumentPosition(m)
                                   & Node.DOCUMENT_POSITION_FOLLOWING) !== 0,
    };
  });
  ok('le questionnaire est armé depuis le serveur', arme && vue.selects > 0,
     vue.selects + ' constat(s), ' + vue.axes + ' axe(s)'
     + (err.length ? ' | erreur : ' + err[0].slice(0, 120) : ''));
  ok('LES DEUX SECTIONS COEXISTENT — complément, pas fusion',
     vue.maturiteVisible && vue.financeVisible,
     'étude: ' + vue.financeVisible + ', maturité: ' + vue.maturiteVisible);
  ok('…et le diagnostic vient APRÈS les chiffres qu’il commente',
     vue.apresFinance);
  ok('les treize constats et les quatre axes sont rendus',
     vue.selects === 13 && vue.axes === 4, vue.selects + '/13 · ' + vue.axes + '/4');

  titre('2. Le maillon faible commande — à l’écran, pas seulement au module');

  /* Tout au niveau 3 sauf UN constat à 0 : une moyenne afficherait « bon ». */
  await pg.evaluate(() => {
    document.querySelectorAll('#mat-form select').forEach(s => { s.value = '3'; });
    const faible = document.querySelector('#mat-form select[data-cr="donnee_datee"]');
    if (faible) faible.value = '0';
  });
  await pg.click('#mat-go');
  let rendu = true;
  try {
    await pg.waitForFunction(() =>
      document.querySelector('#mat-out .mat-glob'), null, { timeout: 20000 });
  } catch (e) { rendu = false; }
  const diag = await pg.evaluate(() => {
    const g = document.querySelector('#mat-out .mat-glob');
    return {
      rendu: !!g,
      texte: g ? g.textContent.replace(/\s+/g, ' ').trim() : '',
      classe: g ? g.className : '',
      decisions: [...document.querySelectorAll('#mat-out .mat-dec')].map(d => ({
        t: d.textContent.replace(/\s+/g, ' ').trim().slice(0, 60),
        c: d.className,
      })),
      actions1: [...document.querySelectorAll('#mat-out .mat-act li.r1')]
        .map(l => l.textContent.replace(/\s+/g, ' ').trim().slice(0, 60)),
    };
  });
  ok('le diagnostic s’affiche', rendu && diag.rendu, diag.texte.slice(0, 90));
  ok('UN SEUL CONSTAT À ZÉRO fait tomber le global — pas de moyenne',
     /absent/.test(diag.texte) && /pas une moyenne/.test(diag.texte)
       && /mauvais/.test(diag.classe),
     diag.texte.slice(0, 120));
  ok('…et l’axe qui bloque est NOMMÉ', /Collecte de données/.test(diag.texte));
  ok('le plan désigne le maillon faible comme seule action qui déplace',
     diag.actions1.length > 0 && diag.actions1.every(a => /Collecte/.test(a)),
     diag.actions1.join(' | ').slice(0, 110) || 'aucune action de rang 1');
  ok('les trois familles de décision sont jugées, aucune au vert',
     diag.decisions.length === 3 && diag.decisions.every(d => !/bon/.test(d.c)),
     diag.decisions.map(d => d.c.replace('mat-dec ', '')).join(', '));

  titre('3. L’apport de l’étude est CONSTATÉ, jamais supposé');

  const avant = await pg.evaluate(() => {
    const t = [...document.querySelectorAll('#mat-out .mat-ap')]
      .map(e => e.textContent.replace(/\s+/g, ' ').trim());
    return t;
  });
  ok('sans calcul lancé, AUCUN apport n’est annoncé disponible',
     avant.length > 0 && avant.every(t => /\b0\//.test(t)),
     avant[0] ? avant[0].slice(0, 100) : 'aucune ligne d’apport');
  ok('…et la page invite à lancer les blocs manquants',
     avant.some(t => /lancez les blocs manquants/i.test(t)));

  titre('4. La restitution aux sponsors : verdict en tête, recalibrage');

  const note = await pg.evaluate(() => {
    const d = document.querySelector('#mat-out .mat-rest');
    const pre = d ? d.querySelector('.mat-md') : null;
    return { present: !!d,
             resume: d ? (d.querySelector('summary') || {}).textContent || '' : '',
             txt: pre ? pre.textContent : '' };
  });
  ok('la note de restitution est servie avec le diagnostic', note.present,
     note.resume.replace(/\s+/g, ' ').trim().slice(0, 80));
  ok('…et son intitulé dit QUAND la présenter',
     /dès le départ/i.test(note.resume), note.resume.slice(0, 70));
  const iVerdict = note.txt.indexOf('Ce que ce diagnostic conclut');
  ok('LE VERDICT EST EN TÊTE de la note, pas en annexe',
     iVerdict > 0 && iVerdict < note.txt.length / 3,
     iVerdict > 0 ? 'au caractère ' + iVerdict + ' sur ' + note.txt.length : 'introuvable');
  ok('…la conclusion décevante est ASSUMÉE, avec sa raison',
     /décevante, et c'est la raison de la présenter maintenant/.test(note.txt));
  ok('…le recalibrage dit ce qui est tenable ET ce qu’il ne faut pas promettre',
     /Livrable tenable aujourd'hui/.test(note.txt)
       && /À NE PAS promettre en l'état/.test(note.txt));
  ok('…et la réserve distingue les deux questions',
     /ne dit pas si l'investissement est bon/.test(note.txt));

  titre('5. Le pilotage : seuils, formes et les trois apports augmentés');

  /* La section de pilotage vit sur la MÊME vue : le diagnostic dit ce qu'on
     peut promettre, le pilotage est ce qu'on livre. On saisit une mesure qui
     dépasse largement sa cible ET une série porteuse d'une rupture, pour
     éprouver les trois apports d'un coup. */
  let pilArme = true;
  try {
    await pg.waitForFunction(() =>
      document.querySelectorAll('#pil-form input').length > 0, null, { timeout: 20000 });
  } catch (e) { pilArme = false; }
  ok('le tableau de bord est armé depuis le serveur', pilArme,
     pilArme ? '' : 'aucun champ de mesure');

  if (pilArme) {
    await pg.evaluate(() => {
      const set = (cle, champ, v) => {
        const e = document.querySelector('#pil-form input[data-pi="' + cle
          + '"][data-ch="' + champ + '"]');
        if (e) { e.value = v; }
      };
      /* PUE promis 1,25, constaté 1,45 : au-delà de la tolérance ET de
         l'incertitude — une vraie alerte. La série porte une accélération. */
      set('pue_constate', 'valeur', '1.45');
      set('pue_constate', 'cible', '1.25');
      set('pue_constate', 'serie', '1.26, 1.27, 1.28, 1.34, 1.40, 1.45');
      /* Enveloppe +12 % sur une grandeur à ±30 % : DANS le bruit. Le module
         doit refuser d'alerter — c'est le contrôle qui compte le plus. */
      set('enveloppe_kw', 'valeur', '11200');
      set('enveloppe_kw', 'cible', '10000');
    });
    await pg.click('#pil-go');
    let rendu = true;
    try {
      await pg.waitForFunction(() =>
        document.querySelectorAll('#pil-out .pil-c').length > 0, null, { timeout: 20000 });
    } catch (e) { rendu = false; }
    const pil = await pg.evaluate(() => {
      const carte = (cle) => {
        const cs = [...document.querySelectorAll('#pil-out .pil-c')];
        return cs.find(c => (c.querySelector('.pil-t') || {}).textContent
          && /PUE constaté/.test(c.querySelector('.pil-t').textContent)) || null;
      };
      const cs = [...document.querySelectorAll('#pil-out .pil-c')].map(c => ({
        titre: (c.querySelector('.pil-t') || {}).textContent.replace(/\s+/g, ' ').trim(),
        classe: c.className,
        exp: (c.querySelector('.pil-exp') || {}).textContent || '',
        an: !!c.querySelector('.pil-an'),
        pr: (c.querySelector('.pil-pr summary') || {}).textContent || '',
        svg: !!c.querySelector('svg'),
      }));
      return {
        cartes: cs,
        glob: (document.querySelector('#pil-out .pil-glob') || {}).textContent || '',
        alertes: document.querySelectorAll('#pil-out .pil-al li').length,
      };
    });
    ok('les cartes du tableau de bord sont rendues', rendu && pil.cartes.length === 5,
       pil.cartes.length + ' carte(s)');
    const pue = pil.cartes.find(c => /PUE/.test(c.titre)) || {};
    const env = pil.cartes.find(c => /Enveloppe/.test(c.titre)) || {};
    ok('un écart démontré passe à l’alerte ou à la surveillance',
       /alerte|surveiller/.test(pue.classe || ''), pue.classe);
    ok('UN ÉCART DANS L’INCERTITUDE NE DÉCLENCHE PAS D’ALERTE',
       /indetermine/.test(env.classe || ''),
       (env.classe || 'carte introuvable') + ' — +12 % sur une grandeur à ±30 %');
    ok('…et la page l’explique au lieu de le taire',
       /incertitude/.test(pil.glob) || /non démontré/.test(env.exp || ''),
       (env.exp || '').slice(0, 100));
    ok('la figure est dessinée pour les séries fournies', !!pue.svg);
    ok('L’EXPLICATION EST COMPOSÉE, et le dit',
       /sans modèle de langage/.test(pue.exp), pue.exp.slice(0, 110));
    ok('…elle cite les valeurs MESURÉES', /1\.45/.test(pue.exp) && /1\.25/.test(pue.exp));
    ok('la détection d’anomalies est proposée sur la série', pue.an);
    ok('la projection est offerte, ou son refus motivé', !!pue.pr, pue.pr.slice(0, 60));
  }

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.join(' | ').slice(0, 160));

  console.log('\n' + (ko ? ko + ' contrôle(s) en échec' : 'tout est vert') + '\n');
  await nav.close();
  process.exit(ko ? 1 : 0);
})();
