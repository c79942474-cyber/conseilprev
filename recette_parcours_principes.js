/* RECETTE — L'AVANCEMENT NE SE CRÉDITE PAS D'UN FORMULAIRE PRÉ-REMPLI
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * D'OÙ VIENT CETTE RÈGLE. Le parcours guidé du site d'ingénierie
 * (conseilprevcyber, `guide-etapes.js`) a rencontré ce problème avant nous et
 * l'a tranché ; on applique ici la même règle, parce que deux sites du même
 * cabinet ne peuvent pas compter l'avancement de deux façons.
 *
 *   « Compter "renseigné" tout ce qui porte une valeur faisait lire "fait" à
 *     quatre étapes d'une page où le lecteur n'avait RIEN touché : le parcours
 *     se félicitait d'un formulaire livré pré-rempli, et son avancement ne
 *     voulait plus rien dire. »
 *
 * CE QUE CES CONTRÔLES PROTÈGENT.
 *
 *   1. AU CHARGEMENT, RIEN N'EST CRÉDITÉ. La page ouvre à 100 MW avec trois
 *      pays cochés ; le fil affichait « 1 / 9 » avant tout geste — mesuré.
 *      Sur-évaluer l'avancement fait croire à un travail qui n'a pas eu lieu,
 *      et c'est justement l'avancement qu'on vient demander à ce fil.
 *
 *   2. UNE RÉPONSE EST UNE VALEUR QUI A BOUGÉ. Le contrôle change la puissance
 *      et vérifie que l'étape se coche — sans cliquer sur aucune commande.
 *
 *   3. LE POINT QUI DÉCIDE — LANCER LE CALCUL VAUT VALIDATION DES ÉTAPES QUI
 *      L'ALIMENTENT. C'est l'adaptation que le site d'ingénierie n'a pas à
 *      faire : ici les étapes 1 et 2 nourrissent l'étape 3. Refuser de les
 *      créditer alors que leur résultat est à l'écran serait une rigueur qui
 *      se retourne contre le lecteur.
 *
 *   4. LE FIL N'EST PAS PÉRIMÉ. La liste des pays se peuple par requête après
 *      le premier relevé : l'état affiché ne correspondait pas à l'état
 *      calculé, et se corrigeait tout seul à la première interaction.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5510 node recette_parcours_principes.js
 */
const { chromium } = require('playwright');

const BASE = process.env.BASE || 'http://127.0.0.1:5510';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';

let ko = 0;
const ok = (t, cond, detail) => {
  console.log((cond ? '  OK   ' : '  KO   ') + t + (detail ? ' — ' + detail : ''));
  if (!cond) ko++;
};
const titre = t => console.log('\n══ ' + t + ' ══\n');

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({
    viewport: { width: 1400, height: 1000 },
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
      + '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    locale: 'fr-FR'
  });
  /* SANS CE MASQUE, LE SERVEUR BLOQUE L'ADRESSE POUR 1800 s et toutes les
     recettes suivantes échouent sur des 429 qu'on prend pour des régressions. */
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });

  const ouvrir = async () => {
    const pg = await ctx.newPage();
    await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
    await pg.goto(BASE + '/enveloppe', { waitUntil: 'domcontentloaded' });
    await pg.waitForFunction(
      () => document.querySelectorAll('#fin-pays button[data-p]').length > 0,
      null, { timeout: 60000 });
    await pg.waitForTimeout(1300);
    return pg;
  };
  const compteur = pg => pg.evaluate(() => {
    const p = document.querySelector('#fin-fil .fin-fil-pn');
    return p ? p.textContent.trim() : 'absent';
  });
  const faits = pg => pg.evaluate(() =>
    [...document.querySelectorAll('#fin-fil .fin-e')]
      .filter(x => x.classList.contains('fait')).length);

  const pg = await ouvrir();
  const err = [];
  pg.on('pageerror', e => err.push(e.message));

  // ── 1 ─────────────────────────────────────────────────────────────────────
  titre('1. Le formulaire arrive PRÉ-REMPLI — sans quoi rien ne serait à prouver');

  const depart = await pg.evaluate(() => ({
    mw: (document.getElementById('fin-mw') || {}).value,
    pays: document.querySelectorAll('#fin-pays button[data-p].on').length,
    total: document.querySelectorAll('#fin-pays button[data-p]').length
  }));
  ok('la puissance ouvre sur une valeur, sans que personne l’ait saisie',
     parseFloat(depart.mw) > 0, depart.mw + ' MW');
  ok('…et plusieurs pays sont déjà cochés',
     depart.pays >= 2, depart.pays + ' cochés sur ' + depart.total);

  // ── 2 : LE POINT QUI DÉCIDE ───────────────────────────────────────────────
  titre('2. LE POINT QUI DÉCIDE : rien n’est crédité tant que rien n’a bougé');

  const c0 = await compteur(pg);
  ok('AU CHARGEMENT, L’AVANCEMENT EST NUL — le fil ne se félicite pas d’un défaut',
     /^0\s*\/\s*\d+$/.test(c0), c0);
  ok('…et aucune étape n’est peinte en « fait »', (await faits(pg)) === 0,
     (await faits(pg)) + ' étape(s) verte(s)');

  /* LE FIL N'EST PAS PÉRIMÉ : ce qui est peint doit être ce qui est calculé.
     La liste des pays se peuple par requête APRÈS le premier relevé ; sans
     observation, l'écran montrait un état vieux d'une requête. */
  const coherent = await pg.evaluate(() => {
    const f = window.finFaites ? window.finFaites() : null;
    if (!f) return null;
    return (window.FIN_ETAPES || []).map((e, i) => {
      const li = document.querySelectorAll('#fin-fil .fin-e')[i];
      return { cle: e.cle, calcule: !!f[e.cle],
               peint: !!(li && li.classList.contains('fait')) };
    });
  });
  ok('ce que le fil PEINT est ce qu’il CALCULE — il n’est pas périmé',
     !!coherent && coherent.every(x => x.calcule === x.peint),
     (coherent || []).filter(x => x.calcule !== x.peint)
       .map(x => x.cle).join(', ') || 'tout concorde');

  // ── 3 ─────────────────────────────────────────────────────────────────────
  titre('3. Une valeur qui BOUGE est une réponse — sans cliquer sur une commande');

  await pg.evaluate(() => {
    const e = document.getElementById('fin-mw');
    e.value = '250';
    e.dispatchEvent(new Event('input', { bubbles: true }));
  });
  await pg.waitForTimeout(700);
  const c1 = await compteur(pg);
  ok('changer la puissance crédite l’étape, SANS lancer de calcul',
     /^1\s*\//.test(c1), c0 + ' → ' + c1);

  await pg.evaluate(() => {
    const b = document.querySelector('#fin-pays button[data-p]:not(.on)');
    if (b) b.click();
  });
  await pg.waitForTimeout(700);
  const c2 = await compteur(pg);
  ok('…choisir un pays crédite la sienne, elle aussi',
     /^2\s*\//.test(c2), c1 + ' → ' + c2);

  /* REVENIR EN ARRIÈRE DÉCRÉDITE : un avancement qui ne sait que monter n'est
     plus un avancement, c'est un score. */
  const retour = await pg.evaluate(async () => {
    const e = document.getElementById('fin-mw');
    e.value = '';
    e.dispatchEvent(new Event('input', { bubbles: true }));
    await new Promise(r => setTimeout(r, 700));
    return document.querySelector('#fin-fil .fin-fil-pn').textContent.trim();
  });
  ok('…et vider le champ le retire : l’avancement sait redescendre',
     /^1\s*\//.test(retour), c2 + ' → ' + retour);

  // ── 4 ─────────────────────────────────────────────────────────────────────
  titre('4. Le tout PREMIER geste compte, même si c’est un clic sur un pays');

  /* CE SCÉNARIO EST CELUI QUE L'OBSERVATION PROTÈGE, et il a failli m'échapper.
     La référence « combien de pays étaient cochés en arrivant » doit être
     figée AU MOMENT OÙ LA LISTE APPARAÎT. Sans cela, elle se fige au premier
     appel utile — c'est-à-dire APRÈS le clic du lecteur, qui n'est alors plus
     vu comme un changement. Le défaut ne se voit que si le clic sur un pays
     est le PREMIER geste : toute action antérieure fige la référence à temps
     et masque la faute. Le contrôle précédent, qui modifiait la puissance
     d'abord, la masquait exactement ainsi. */
  const pgP = await ouvrir();
  const avantP = await compteur(pgP);
  await pgP.evaluate(() => {
    const b = document.querySelector('#fin-pays button[data-p]:not(.on)');
    if (b) b.click();
  });
  await pgP.waitForTimeout(800);
  const apresP = await compteur(pgP);
  ok('LE PREMIER CLIC SUR UN PAYS EST COMPTÉ — la référence était figée à temps',
     /^0\s*\//.test(avantP) && /^1\s*\//.test(apresP),
     avantP + ' → ' + apresP);
  await pgP.close();

  // ── 5 ─────────────────────────────────────────────────────────────────────
  titre('5. Lancer le calcul vaut validation des étapes qui l’alimentent');

  /* PAGE NEUVE : on ne touche RIEN, on lance le calcul sur les valeurs par
     défaut. Les étapes 1 et 2 doivent alors se créditer — leur résultat est à
     l'écran, refuser de les compter serait une rigueur inutile. */
  const pg2 = await ouvrir();
  const avant = await compteur(pg2);
  ok('sur une page neuve, l’avancement part bien de zéro',
     /^0\s*\//.test(avant), avant);
  await pg2.evaluate(() => document.getElementById('fin-go').click());
  await pg2.waitForFunction(() => window.FIN_DERNIER && window.FIN_DERNIER(),
    null, { timeout: 60000 });
  await pg2.waitForTimeout(2600);
  const apres = await compteur(pg2);
  ok('LE CALCUL CRÉDITE LES TROIS ÉTAPES : les deux qui l’alimentent, et lui',
     /^3\s*\//.test(apres), avant + ' → ' + apres);
  const detail = await pg2.evaluate(() =>
    (window.FIN_ETAPES || []).slice(0, 3).map((e, i) => {
      const li = document.querySelectorAll('#fin-fil .fin-e')[i];
      return e.n + (li && li.classList.contains('fait') ? '✓' : '✗');
    }).join(' '));
  ok('…et ce sont bien les étapes 1, 2 et 3', detail === '1✓ 2✓ 3✓', detail);
  await pg2.close();

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
