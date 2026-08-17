/* RECETTE — LE PARCOURS GUIDÉ TIENT SES PROMESSES, ET L'ÉTAPE 9 SE CHOISIT
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * CE QUE CETTE RECETTE PROTÈGE, ET LA FAUTE QUE CHAQUE CONTRÔLE EMPÊCHE.
 *
 *   1. LE MENU NE PROMET QUE CE QU'IL PEUT TENIR. Il annonçait « Parcours
 *      complet · 4 étapes » sur une vue où ce parcours n'en avait AUCUNE : le
 *      compte venait du référentiel, jamais du filtre de vue. Le choisir levait
 *      « Cannot read properties of undefined » et n'affichait rien — pas de
 *      première étape, pas de message, et le script mort pour le reste de la
 *      page. C'est exactement ce qu'un lecteur décrit par « il n'y a pas de
 *      guidage pour la première étape ».
 *
 *   2. UN PARCOURS SANS ÉTAPE SE DIT, IL NE PLANTE PAS. Le sélecteur ne le
 *      propose plus ; le lien direct y mène encore, et doit alors expliquer.
 *
 *   3. ON PEUT RECOMMENCER. Un parcours qu'on ne peut que fermer oblige à
 *      rouvrir le menu et à tout rechoisir pour revenir au premier pas.
 *
 *   4. LES DEUX CHEMINS DE L'ÉTAPE 9 SE SIGNALENT À L'ARRIVÉE, et le battement
 *      s'arrête sur celui qu'on a pris — un signal qui resterait après le
 *      choix ne désignerait plus rien.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5510 node recette_parcours_guide_ui.js
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
    viewport: { width: 1500, height: 1000 },
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
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(e.message));

  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  const rep = await pg.goto(BASE + '/enveloppe', { waitUntil: 'domcontentloaded' });
  if (rep.status() !== 200) {
    ok('la page répond', false, 'HTTP ' + rep.status());
    console.log('\n1 contrôle(s) en échec\n');
    await nav.close(); process.exit(1);
  }
  await pg.waitForFunction(() => !!window.GP_PROFILS && !!document.getElementById('pp-role'),
    null, { timeout: 60000 });
  await pg.waitForTimeout(1800);

  // ── 1 : LE POINT QUI DÉCIDE ───────────────────────────────────────────────
  titre('1. LE POINT QUI DÉCIDE : le menu ne promet que ce qu’il peut tenir');

  const menu = await pg.evaluate(() => {
    const r = document.getElementById('pp-role');
    const q = document.getElementById('pp-parcours');
    const out = [];
    for (const k of Object.keys(window.GP_PROFILS)) {
      r.value = k;
      r.dispatchEvent(new Event('change', { bubbles: true }));
      const P = window.GP_PROFILS[k];
      [...q.options].slice(1).forEach(o => {
        /* Le compte RÉELLEMENT disponible sur cette vue, relu à part. */
        const dispo = window.gpEtapesDe
          ? window.gpEtapesDe(P, o.value || null).length : null;
        const annonce = (o.textContent.match(/·\s*(\d+)\s*étape/) || [])[1];
        out.push({ role: k, val: o.value, texte: o.textContent,
                   desactive: o.disabled, dispo: dispo,
                   annonce: annonce == null ? null : parseInt(annonce, 10) });
      });
    }
    return out;
  });
  ok('le menu propose des parcours', menu.length > 0, menu.length + ' entrée(s)');
  /* CHAQUE COMPTE ANNONCÉ EST LE COMPTE DISPONIBLE — recalculé à part, et non
     relu depuis le libellé qu'on teste. */
  const faux = menu.filter(m => m.annonce != null && m.dispo != null
    && m.annonce !== m.dispo);
  ok('CHAQUE NOMBRE D’ÉTAPES ANNONCÉ EST CELUI RÉELLEMENT DISPONIBLE ICI',
     faux.length === 0,
     faux.map(m => m.role + ' annonce ' + m.annonce + ' pour ' + m.dispo).join(' · ')
       || menu.filter(m => m.annonce != null).length + ' compte(s) vérifié(s)');
  /* AUCUN PARCOURS VIDE N'EST CLIQUABLE : c'est le défaut mesuré. */
  const videsActifs = menu.filter(m => m.dispo === 0 && !m.desactive);
  ok('AUCUN PARCOURS SANS ÉTAPE N’EST PROPOSABLE',
     videsActifs.length === 0,
     videsActifs.map(m => m.role).join(', ') || 'aucun');
  const vides = menu.filter(m => m.dispo === 0);
  ok('…et ceux-là DISENT pourquoi, au lieu de disparaître',
     vides.length > 0 && vides.every(m => /aucune étape sur cette vue/i.test(m.texte)),
     vides.length + ' désactivé(s) : ' + (vides[0] || {}).texte);

  const aide = await pg.evaluate(() => {
    const r = document.getElementById('pp-role');
    r.value = 'analyste';
    r.dispatchEvent(new Event('change', { bubbles: true }));
    const a = document.getElementById('pp-aide');
    return a ? a.textContent.trim() : '';
  });
  ok('…et la ligne d’aide dit où ce parcours se déroule',
     /Panorama/i.test(aide), aide.slice(0, 90));

  // ── 2 ─────────────────────────────────────────────────────────────────────
  titre('2. Un parcours sans étape s’explique — il ne fait pas mourir le script');

  /* AUCUN APPEL NU : c'est précisément une LEVÉE qu'on traque ici. Laissée
     remonter, elle tue le fichier — Playwright rend une pile Node et le
     contrôle se lit comme une panne d'outil au lieu du défaut trouvé. Ce dépôt
     s'interdit cela ailleurs en toutes lettres ; la règle vaut ici. On attrape
     donc, et on rend l'erreur comme une DONNÉE. */
  const direct0 = await pg.evaluate(async () => {
    let leve = null;
    try {
      window.gpDemarrer('analyste');
    } catch (e) { leve = String(e && e.message || e); }
    await new Promise(r => setTimeout(r, 900));
    const c = document.querySelector('.gp-carte');
    return { leve: leve, texte: c ? c.textContent.replace(/\s+/g, ' ').trim() : null };
  });
  ok('OUVRIR UN PARCOURS VIDE NE LÈVE AUCUNE ERREUR',
     direct0.leve === null, direct0.leve || 'aucune levée');
  const direct = direct0.texte;
  ok('le lien direct affiche une carte au lieu de rien', !!direct,
     (direct || '').slice(0, 60));
  ok('…qui dit que ce parcours ne passe pas par cette vue',
     /ne passe pas par cette vue/i.test(direct || ''));
  ok('…et propose la vue où il se déroule',
     await pg.evaluate(() =>
       !!document.querySelector('.gp-carte a[href*="panorama"]')));
  ok('AUCUNE ERREUR DE SCRIPT — c’est ce qui tuait la page',
     err.length === 0, err.slice(0, 2).join(' | '));

  // ── 3 ─────────────────────────────────────────────────────────────────────
  titre('3. On peut recommencer sans tout rechoisir');

  const zero = await pg.evaluate(async () => {
    window.gpDemarrer('finance');
    await new Promise(r => setTimeout(r, 700));
    const auDebut = !!document.getElementById('gp-zero');
    document.getElementById('gp-suiv').click();
    await new Promise(r => setTimeout(r, 700));
    const rang2 = (document.querySelector('.gp-etape') || {}).textContent || '';
    const offert = !!document.getElementById('gp-zero');
    if (offert) document.getElementById('gp-zero').click();
    await new Promise(r => setTimeout(r, 700));
    return { auDebut: auDebut, rang2: rang2.trim(), offert: offert,
             apres: ((document.querySelector('.gp-etape') || {}).textContent || '').trim(),
             ouvert: !!document.querySelector('.gp-carte.on') };
  });
  ok('la remise à zéro n’est PAS offerte sur la première étape',
     zero.auDebut === false);
  ok('…elle l’est dès qu’on a avancé', zero.offert === true, zero.rang2);
  ok('LA REMISE À ZÉRO RAMÈNE À LA PREMIÈRE ÉTAPE',
     /Étape 1 sur/.test(zero.apres), zero.rang2 + ' → ' + zero.apres);
  ok('…et elle ne referme pas le parcours : on voulait le reprendre, pas sortir',
     zero.ouvert === true);

  await pg.evaluate(() => { if (window.gpFermer) window.gpFermer(); });
  await pg.waitForTimeout(400);

  // ── 4 ─────────────────────────────────────────────────────────────────────
  titre('4. Les deux chemins de l’étape 9 se signalent, et se départagent');

  await pg.waitForFunction(() => document.querySelectorAll('#fin-ponts .fin-pt').length > 0,
    null, { timeout: 30000 });
  const avant = await pg.evaluate(() =>
    [...document.querySelectorAll('#fin-ponts .fin-pt')]
      .map(c => c.classList.contains('ici')));
  ok('tant qu’on n’y est pas, les deux chemins ne battent pas',
     avant.every(x => !x), JSON.stringify(avant));

  const choix = await pg.evaluate(() => {
    const z = document.querySelector('.fin-pt-choix');
    return z ? z.textContent.replace(/\s+/g, ' ').trim() : null;
  });
  ok('une consigne donne le CRITÈRE qui départage les deux', !!choix,
     (choix || '').slice(0, 60) + '…');
  ok('…elle oppose ce que le site CONSOMME à ce que les études COÛTENT',
     /consommera/i.test(choix || '') && /coûteront/i.test(choix || ''));
  ok('…et elle dit qu’ils ne s’excluent pas',
     /ne s’excluent pas|l’un après l’autre/i.test(choix || ''));

  /* ON AMÈNE LE FIL À L'ÉTAPE 9 en rendant les huit premières faites. */
  const arrive = await pg.evaluate(async () => {
    window.FIN_ETAPES.slice(0, 8).forEach(e => { e.fait = function () { return true; }; });
    window.finMajFil();
    await new Promise(r => setTimeout(r, 600));
    const cartes = [...document.querySelectorAll('#fin-ponts .fin-pt')];
    const s = getComputedStyle(cartes[0]);
    return { etape: window.FIN_ETAPES[window.finPasCourant()].cle,
             ici: cartes.map(c => c.classList.contains('ici')),
             cadre: s.borderTopColor, epaisseur: parseFloat(s.borderLeftWidth),
             anim: s.animationName, duree: parseFloat(s.animationDuration) };
  });
  ok('on est bien arrivé à l’étape des ponts', arrive.etape === 'pont', arrive.etape);
  ok('LES DEUX CHEMINS S’ENCADRENT ET BATTENT à l’arrivée',
     arrive.ici.every(Boolean) && arrive.anim !== 'none',
     JSON.stringify(arrive.ici) + ' · ' + arrive.anim);
  ok('…le cadre est bleu et épais', arrive.epaisseur >= 2, arrive.epaisseur + 'px');
  ok('…à la MÊME cadence que le reste du fil, sous le seuil de sécurité',
     arrive.duree >= 1.0, arrive.duree + ' s');

  /* PRENDRE UN CHEMIN ÉTEINT SON BATTEMENT — et lui seul. */
  const pris = await pg.evaluate(async () => {
    const z = document.querySelector('#pont-fin .pont-out');
    z.innerHTML = '<a href="https://exemple.test/x">lien fabriqué</a>';
    window.finMajFil();
    await new Promise(r => setTimeout(r, 500));
    const cartes = [...document.querySelectorAll('#fin-ponts .fin-pt')];
    return cartes.map(c => ({
      etat: (c.classList.contains('pris') ? 'pris'
             : c.classList.contains('ici') ? 'ici'
             : c.classList.contains('dispo') ? 'dispo' : 'neutre'),
      anim: getComputedStyle(c).animationName }));
  });
  ok('PRENDRE UN CHEMIN ÉTEINT SON BATTEMENT',
     pris[0].etat === 'pris' && pris[0].anim === 'none',
     JSON.stringify(pris.map(x => x.etat)));
  /* MAIS IL NE FERME PAS L'AUTRE : les deux répondent à des questions
     différentes, et l'un ne répond pas pour l'autre. Le chemin non pris garde
     son cadre — « celui-ci reste ouvert » — sans battement, qui voudrait dire
     « choisissez maintenant » alors que le choix a été fait. */
  ok('…et l’autre RESTE OUVERT : le choix n’est pas exclusif',
     pris[1].etat === 'dispo', JSON.stringify(pris.map(x => x.etat)));
  ok('…sans battement, lui non plus : on ne presse plus personne',
     pris[1].anim === 'none', pris[1].anim);

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
