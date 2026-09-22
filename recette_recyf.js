/* RECETTE — LE CALQUE FRANÇAIS, ET LE TAUX QUI NE SE CONFOND PAS
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * CE QUI EST EN JEU. `nis2` mesure la directive ; ce calque mesure ce que la
 * France prépare — vingt objectifs, 152 moyens pour une entité essentielle,
 * 76 pour une importante. Ni le projet de loi ni le ReCyF ne sont en vigueur.
 *
 * LE DÉFAUT QUE CETTE RECETTE TRAQUE EN PREMIER : un taux de préparation qui
 * s'afficherait comme un taux de conformité. Les règles Python vérifient que
 * le MOTEUR déclare la bonne nature ; elles ne voient pas ce que l'écran rend.
 * Or c'est l'écran qui part en comité. On mesure donc que le chiffre et la
 * phrase qui le qualifie sont dans la MÊME boîte, et que le mot
 * « conformité » n'apparaît jamais à côté du nombre.
 *
 * LE CONTRÔLE DIFFÉRENTIEL : on peint le même écran pour une entité
 * essentielle puis pour une importante. Les deux relevés doivent DIFFÉRER —
 * vingt objectifs contre quinze, 152 moyens contre 76. Un écran qui rendrait
 * la même chose aux deux aurait perdu la gradation, qui est le changement le
 * plus lourd de la transposition.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
let ko = 0, n = 0;
const ok = (t, c, d) => { n++; if (!c) ko++;
  console.log((c ? '  OK   ' : '  KO   ') + t + (d ? ' — ' + d : '')); };

const LIRE = () => {
  const b = document.getElementById('recyf-body');
  const t = b && b.querySelector('.recyf-taux');
  return {
    chiffre: t ? t.querySelector('.recyf-chiffre').textContent.trim() : null,
    quoi: t ? t.querySelector('.recyf-quoi').textContent.trim() : '',
    objectifs: b ? b.querySelectorAll('.nist-cat').length : 0,
    hors: b ? b.querySelectorAll('.nist-cat.recyf-hors').length : 0,
    selects: b ? b.querySelectorAll('.nist-cat select').length : 0,
    piliers: b ? [...b.querySelectorAll('.recyf-pilier-n')]
                   .map(e => e.textContent.trim()) : [],
  };
};

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1440, height: 980 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const p = await ctx.newPage();
  const err = [];
  p.on('pageerror', e => err.push(e.message));
  await p.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'domcontentloaded' });

  // ══ 1. LE STATUT EST LE PREMIER ÉLÉMENT DU PANNEAU ═════════════════════
  console.log('\n1. Le statut des textes, avant tout chiffre');
  await p.goto(BASE + '/sentinel?goto=recyf-objectifs', { waitUntil: 'domcontentloaded' });
  await p.waitForFunction(() => {
    const e = document.getElementById('recyf-statut');
    return e && e.textContent.indexOf('Chargement') < 0;
  }, null, { timeout: 20000 });
  const st = await p.evaluate(() => {
    const e = document.getElementById('recyf-statut');
    return { texte: e.textContent, classe: e.className };
  });
  ok('le bandeau dit que le texte n’est PAS en vigueur',
     /n’est pas en vigueur|n'est pas en vigueur/i.test(st.texte));
  ok('il porte la marque visuelle de la réserve',
     /recyf-pas-en-vigueur/.test(st.classe), st.classe);
  ok('il nomme ce qui oblige aujourd’hui',
     /directive \(UE\) 2022\/2555/.test(st.texte));
  ok('il nomme ce qui manque — vote, décret, version finale',
     /vote de la loi/.test(st.texte) && /décret/.test(st.texte));

  // ══ 2. LE REFUS SANS QUALIFICATION ═════════════════════════════════════
  console.log('\n2. Sans qualification, l’écran REFUSE de chiffrer');
  const vide = await p.evaluate(() =>
    document.getElementById('recyf-body').textContent);
  ok('aucun taux n’est affiché', !/%/.test(vide), vide.slice(0, 50));
  ok('le refus explique la raison — 152 contre 76',
     /152/.test(vide) && /76/.test(vide));

  // ══ 3. ENTITÉ ESSENTIELLE ══════════════════════════════════════════════
  console.log('\n3. Entité essentielle — vingt objectifs, 152 moyens');
  await p.selectOption('#recyf-statut-sel', 'essentielle');
  await p.waitForFunction(() =>
    !!document.querySelector('#recyf-body .recyf-taux'), null, { timeout: 15000 });
  const ee = await p.evaluate(LIRE);
  ok('vingt objectifs sont peints', ee.objectifs === 20, ee.objectifs + ' objectif(s)');
  ok('aucun n’est hors champ', ee.hors === 0, ee.hors + ' hors champ');
  ok('chacun porte son sélecteur d’état', ee.selects === 20, ee.selects);
  ok('les quatre piliers sont là',
     ee.piliers.length === 4, ee.piliers.join(' · '));
  ok('le nombre de moyens attendus est 152', /152/.test(ee.quoi));

  // ── LE CONTRÔLE QUI COMPTE : la nature voyage avec le nombre ──────────
  const meme = await p.evaluate(() => {
    const t = document.querySelector('#recyf-body .recyf-taux');
    return { boite: t.textContent,
             /* L'INTITULÉ EST LE <b> DU BLOC, pas le bloc entier. Une
                première version cherchait « taux de conformité » dans tout
                le texte et tombait sur l'AVERTISSEMENT qui contient
                justement ces mots — un contrôle qui échoue sur la
                correction et non sur le défaut. */
             intitule: (t.querySelector('.recyf-quoi b') || {}).textContent };
  });
  ok('le mot « préparation » est dans la MÊME boîte que le chiffre',
     /pr[ée]paration/i.test(meme.boite));
  ok('la boîte dit aussi ce que le taux n’est PAS',
     /n['’]est PAS un taux de conformité/i.test(meme.boite));
  ok('l’INTITULÉ du taux dit « préparation », jamais « conformité »',
     /^Taux de pr[ée]paration$/i.test((meme.intitule || '').trim()),
     meme.intitule);

  // ══ 4. ENTITÉ IMPORTANTE — LE DIFFÉRENTIEL ═════════════════════════════
  console.log('\n4. Entité importante — la gradation, mesurée par différence');
  await p.selectOption('#recyf-statut-sel', 'importante');
  await p.waitForFunction(() => {
    const q = document.querySelector('#recyf-body .recyf-quoi');
    return q && /76/.test(q.textContent);
  }, null, { timeout: 15000 });
  const ei = await p.evaluate(LIRE);
  ok('vingt objectifs restent affichés', ei.objectifs === 20, ei.objectifs);
  ok('CINQ sont hors champ', ei.hors === 5, ei.hors + ' hors champ');
  ok('seuls quinze portent un sélecteur', ei.selects === 15, ei.selects);
  ok('le nombre de moyens tombe à 76', /76/.test(ei.quoi));
  /* SANS CE TÉMOIN, les deux relevés pourraient être identiques et tout ce
     qui précède passerait quand même. */
  ok('les deux relevés DIFFÈRENT vraiment',
     ee.quoi !== ei.quoi && ee.selects !== ei.selects,
     'EE ' + ee.selects + ' sélecteurs / EI ' + ei.selects);

  // ══ 5. LE TAUX NE COMPTE PAS LE HORS-CHAMP ═════════════════════════════
  console.log('\n5. Le hors-champ ne gonfle pas le taux');
  const monte = await p.evaluate(() => {
    const s = document.querySelectorAll('#recyf-body .nist-cat select');
    s.forEach(x => { x.value = 'atteint';
      x.dispatchEvent(new Event('change', { bubbles: true })); });
    return s.length;
  });
  await p.waitForFunction(() => {
    const c = document.querySelector('#recyf-body .recyf-chiffre');
    return c && c.textContent.indexOf('100') === 0;
  }, null, { timeout: 15000 }).catch(() => {});
  const plein = await p.evaluate(LIRE);
  ok('quinze objectifs atteints donnent 100 %, pas 75 %',
     /^100/.test(plein.chiffre || ''), plein.chiffre + ' sur ' + monte);

  // ══ 6. L’OBJECTIF 16 ═══════════════════════════════════════════════════
  console.log('\n6. L’objectif 16 — hors champ pour une importante');
  /* ON CHANGE DE PANNEAU, ON NE RECHARGE PAS LA PAGE.
     Les deux panneaux vivent dans le MÊME document : un second
     `goto('/sentinel')` coûterait quatre-vingt-seize requêtes de plus et
     ferait sauter le plafond de débit local, ce qui a fait échouer cette
     section pour une raison sans rapport avec ce qu'elle mesure. C'est
     aussi le chemin réel du client : il clique dans la barre latérale. */
  await p.evaluate(() => window.go('recyf-analyse'));
  await p.waitForFunction(() => {
    const v = document.getElementById('p-recyf-analyse');
    return v && getComputedStyle(v).display !== 'none';
  }, null, { timeout: 15000 });
  await p.evaluate(() => {
    var s = document.getElementById('recyf-statut-sel');
    s.value = 'importante';
    s.dispatchEvent(new Event('change', { bubbles: true }));
  });
  await p.waitForFunction(() => {
    const e = document.getElementById('recyf-analyse-body');
    return e && /Hors champ|16\.4/.test(e.textContent);
  }, null, { timeout: 15000 });
  const imp = await p.evaluate(() =>
    document.getElementById('recyf-analyse-body').textContent);
  ok('l’écran dit « hors champ » au lieu d’afficher un zéro',
     /Hors champ pour une entité importante/i.test(imp));
  ok('aucun 0 % n’est affiché', !/\b0\s*%/.test(imp));
  ok('il dit ce que cela ne veut PAS dire',
     /ne veut\s*pas dire|Ce que cela ne veut/i.test(imp));

  console.log('\n7. L’objectif 16 — les quatre exigences pour une essentielle');
  await p.evaluate(() => {
    var s = document.getElementById('recyf-statut-sel');
    s.value = 'essentielle';
    s.dispatchEvent(new Event('change', { bubbles: true }));
  });
  await p.waitForFunction(() => {
    const e = document.getElementById('recyf-analyse-body');
    return e && /16\.4/.test(e.textContent);
  }, null, { timeout: 15000 });
  const ess = await p.evaluate(() => {
    const e = document.getElementById('recyf-analyse-body');
    return { texte: e.textContent,
             exigences: e.querySelectorAll('.nist-cat').length,
             entrees: e.querySelectorAll('[id^="recyf-e-"]').length };
  });
  ok('les quatre références 16.1 à 16.4 sont nommées',
     ['16.1', '16.2', '16.3', '16.4'].every(r => ess.texte.indexOf(r) >= 0));
  ok('les cinq entrées de l’analyse sont proposées', ess.entrees === 5, ess.entrees);
  ok('le plancher de réexamen est annoncé', /36/.test(ess.texte));
  ok('le verrou de périmètre est écrit en toutes lettres',
     /ne permet pas de justifier/i.test(ess.texte));
  ok('les deux voies de preuve sont là, avec leur borne',
     /27001:2022/.test(ess.texte) && /PACS/.test(ess.texte)
     && /couverts par la certification/i.test(ess.texte));
  ok('la charge de la preuve est dite',
     /art\. 15/.test(ess.texte) && /démontrer/i.test(ess.texte));

  console.log('\n8. La console');
  ok('aucune erreur JavaScript', err.length === 0, err.length + ' erreur(s)');

  console.log('\n' + (ko ? 'KO ' + ko + '/' + n : 'TOUT VERT ' + n + '/' + n));
  await nav.close();
  process.exit(ko ? 1 : 0);
})();
