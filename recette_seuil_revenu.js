/* RECETTE — LE MINIMUM À BATTRE : LA RÉPONSE QUI N'ATTEND PAS DE PLAN D'AFFAIRES
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * CE QUE CETTE RECETTE PROTÈGE.
 *
 * Le bloc « Création de valeur » exige sept hypothèses, dont un revenu attendu
 * que cette page ne peut pas fournir. Tant qu'il manque, les trois indicateurs
 * restent « non instruits » — et c'est leur état le plus fréquent : un lecteur
 * sans plan d'affaires repartait avec sept champs vides et aucune réponse, sur
 * la page même qui sert à décider d'un GO ou d'un NO GO.
 *
 * LA QUESTION EST DONC INVERSÉE : non pas « que rapporte ce projet ? », que nul
 * ne sait à ce stade, mais « QUE DOIT-IL RAPPORTER pour ne pas détruire de
 * valeur ? ». Ce seuil sort de l'enveloppe déjà calculée et de DEUX taux, qui
 * sont des décisions du lecteur et non des prévisions.
 *
 *   1. IL DOIT S'AFFICHER AVEC DEUX CHAMPS SUR SEPT. C'est tout le gain : s'il
 *      exigeait le revenu, il ne servirait à rien de plus que les trois
 *      indicateurs qu'il précède.
 *   2. IL DOIT ÊTRE CALCULÉ, PAS AFFICHÉ. Un nombre plausible et figé passerait
 *      tous les contrôles d'apparence. Le contrôle central mesure le seuil à
 *      trois coûts du capital et vérifie qu'il suit la DROITE que la formule
 *      impose — ce qu'aucune constante ne peut faire.
 *   3. IL NE DOIT PAS SE FAIRE PASSER POUR UNE PRÉVISION, ni rendre les trois
 *      indicateurs instruits : il répond à une autre question, il ne les
 *      remplace pas.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5510 node recette_seuil_revenu.js
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
    viewport: { width: 1280, height: 1000 },
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
  await pg.waitForFunction(() => !!document.getElementById('kpi-go'),
    null, { timeout: 60000 });
  await pg.evaluate(() => document.getElementById('fin-go').click());
  await pg.waitForFunction(() => window.FIN_DERNIER && window.FIN_DERNIER(),
    null, { timeout: 60000 });
  await pg.waitForTimeout(1500);

  const lire = () => pg.evaluate(() => {
    const z = document.querySelector('#kpi-out .kpi-seuil');
    const prem = document.querySelector('#kpi-out > *');
    if (!z) return null;
    const v = (z.querySelector('.kpi-seuil-v') || {}).textContent || '';
    const n = v.match(/[\d\s,.]+/g);
    return {
      attente: z.classList.contains('attente'),
      premier: !!prem && prem.classList.contains('kpi-seuil'),
      texte: (z.textContent || '').replace(/\s+/g, ' '),
      bornes: (n || []).slice(0, 2).map(x =>
        parseFloat(x.replace(/\s/g, '').replace(',', '.'))).filter(x => !isNaN(x))
    };
  });

  const calculer = async (wacc, is) => {
    await pg.evaluate(([w, i]) => {
      const cw = document.getElementById('kpi-wacc');
      const ci = document.getElementById('kpi-is_taux');
      if (cw) cw.value = w === null ? '' : String(w);
      if (ci) ci.value = i === null ? '' : String(i);
      document.getElementById('kpi-go').click();
    }, [wacc, is]);
    await pg.waitForTimeout(2500);
    return lire();
  };

  // ── 1 ─────────────────────────────────────────────────────────────────────
  titre('1. Sans les deux taux, le bloc dit ce qu’il attend — et ne feint rien');

  const vide = await calculer(null, null);
  ok('le bloc du seuil est présent dès le premier calcul', !!vide);
  ok('…et il annonce qu’il attend DEUX chiffres, pas sept',
     !!vide && vide.attente && /deux chiffres/i.test(vide.texte));
  ok('…il nomme lesquels', !!vide && /coût du capital/i.test(vide.texte)
     && /taux d’impôt/i.test(vide.texte));
  ok('…et AUCUN montant n’est affiché tant qu’ils manquent',
     !!vide && vide.bornes.length === 0, (vide && vide.bornes.join(' – ')) || 'aucun');

  // ── 2 : LE POINT QUI DÉCIDE ───────────────────────────────────────────────
  titre('2. LE POINT QUI DÉCIDE : deux champs sur sept suffisent');

  const remplis = await pg.evaluate(() =>
    [...document.querySelectorAll('#kpi-form input, #kpi-form select')]
      .filter(e => e.id && e.id.indexOf('kpi-') === 0 && e.tagName === 'INPUT').length);
  const a = await calculer(8, 25);
  ok('LE SEUIL S’AFFICHE SANS PLAN D’AFFAIRES — deux taux ont suffi',
     !!a && !a.attente && a.bornes.length === 2,
     a && a.bornes.join(' – ') + ' M€/an sur ' + remplis + ' champs au total');
  ok('…et il passe EN PREMIER, avant les trois indicateurs',
     !!a && a.premier);
  ok('…les deux bornes sont distinctes : l’exigence décroît avec l’amortissement',
     !!a && a.bornes[1] > a.bornes[0],
     a && a.bornes[0] + ' (dernière année) < ' + a.bornes[1] + ' (première à pleine charge)');
  ok('…et la page DIT laquelle est laquelle',
     !!a && /première à pleine charge/i.test(a.texte) && /décroît mécaniquement/i.test(a.texte));

  /* LE REVENU RESTE ABSENT : si le seuil l'avait exigé, il n'apporterait rien
     de plus que les trois indicateurs qu'il précède. */
  const revenuVide = await pg.evaluate(() => {
    const c = document.getElementById('kpi-revenu_meur_an');
    return !c || !(c.value || '').trim();
  });
  ok('LE REVENU N’A PAS ÉTÉ SAISI — c’est bien la question inversée',
     revenuVide);
  ok('…et les trois indicateurs restent non instruits : le seuil ne les remplace pas',
     await pg.evaluate(() => !!document.querySelector('#kpi-out .kpi-trous')));

  // ── 3 ─────────────────────────────────────────────────────────────────────
  titre('3. Le seuil est CALCULÉ — une constante plausible ne passerait pas');

  /* LA FORMULE EST AFFINE EN CMPC : r = (OPEX + dotation) + CE ÷ (1 − IS) × CMPC.
     Trois mesures suffisent donc à vérifier qu'on suit bien une droite — ce
     qu'aucun nombre figé, et aucune formule approchée, ne peut faire. */
  const b = await calculer(4, 25);
  const c = await calculer(12, 25);
  const y = [b.bornes[1], a.bornes[1], c.bornes[1]];
  ok('le seuil MONTE avec le coût du capital', y[0] < y[1] && y[1] < y[2],
     '4 % → ' + y[0] + ' | 8 % → ' + y[1] + ' | 12 % → ' + y[2] + ' M€/an');
  const pente1 = (y[1] - y[0]) / 4, pente2 = (y[2] - y[1]) / 4;
  ok('…et il suit la DROITE que la formule impose, à 1 % près',
     Math.abs(pente1 - pente2) / Math.max(pente1, pente2) < 0.01,
     'pente ' + pente1.toFixed(3) + ' puis ' + pente2.toFixed(3) + ' M€ par point de CMPC');
  /* L'ORDONNÉE À L'ORIGINE — le seuil à coût du capital nul — doit couvrir au
     moins l'exploitation : un projet qui ne couvre pas ses charges détruit de
     la valeur quel que soit le financement. C'est ce qui rattache ce nombre à
     l'enveloppe calculée plus haut, et non à une table. */
  const origine = y[1] - pente1 * 8;
  const opexHaut = await pg.evaluate(() => {
    const d = window.FIN_DERNIER();
    const code = (window.FIN_PAYS && window.FIN_PAYS()) || d.classement[0].pays;
    return Math.max.apply(null,
      d.dossiers.filter(x => x.pays === code)[0].exploitation.total_meur_an);
  });
  ok('…et à coût du capital nul il couvre au moins l’exploitation calculée',
     origine >= opexHaut - 0.5,
     origine.toFixed(1) + ' M€/an pour une exploitation de ' + opexHaut + ' M€/an');

  /* L'IMPÔT PÈSE, ET DANS LE BON SENS : plus il est élevé, plus il faut
     encaisser pour dégager le même résultat après impôt. */
  const d25 = a.bornes[1];
  const d40 = (await calculer(8, 40)).bornes[1];
  ok('un impôt plus lourd RELÈVE le minimum à battre', d40 > d25,
     'IS 25 % → ' + d25 + ' | IS 40 % → ' + d40 + ' M€/an');

  // ── 4 ─────────────────────────────────────────────────────────────────────
  titre('4. Il ne se fait pas passer pour une prévision');

  const fin = await calculer(8, 25);
  ok('le bloc dit explicitement que ce n’est PAS un chiffre d’affaires prévu',
     /n’est PAS une prévision|n'est PAS une prévision/i.test(fin.texte),
     fin.texte.slice(fin.texte.indexOf('Ce n'), fin.texte.indexOf('Ce n') + 70) + '…');
  ok('…et il publie sa formule, pour qu’on puisse la refaire à la main',
     /Formule/.test(fin.texte) && /CMPC/.test(fin.texte));
  ok('…il se nomme pour ce qu’il est', /minimum à battre/i.test(fin.texte));

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
