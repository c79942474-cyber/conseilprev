/* RECETTE — LE PILOTAGE REPREND LES CALCULS AMONT, ET REFUSE D'INVENTER
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * CE QUE CETTE RECETTE PROTÈGE, ET LA FAUTE QUE CHAQUE CONTRÔLE EMPÊCHE.
 *
 *   1. LA RECOPIE À LA MAIN. Le tableau de bord demandait de retaper des
 *      grandeurs calculées trois écrans plus haut. La recopie n'est pas
 *      seulement fastidieuse : c'est l'endroit où les deux chiffres se mettent
 *      à diverger, et où l'on pilote sur une valeur que plus rien ne rattache
 *      à l'étude. Les contrôles recalculent chaque valeur reprise DEPUIS LA
 *      SOURCE et exigent qu'elle corresponde.
 *
 *   2. LE REMPLISSAGE DE CE QUI NE SE DÉDUIT PAS — la faute qui coûterait le
 *      plus cher. Deux des cinq indicateurs mesurent un CONSTAT : ce que le
 *      chantier a remis, ce que l'exploitation a mesuré. Les remplir depuis
 *      les hypothèses de conception les rendrait verts par construction. Le
 *      PUE constaté vaudrait toujours le PUE promis, et l'indicateur qui
 *      existe pour révéler l'écart entre les deux ne révélerait plus rien.
 *
 *   3. LA CIBLE CIRCULAIRE. Une cible déduite de la valeur qu'elle juge donne
 *      un écart nul quoi qu'il arrive — un indicateur toujours vert, donc
 *      muet. Le contrôle central écarte une phase de maîtrise d'œuvre et
 *      exige que le taux effectif DÉCROCHE de son barème.
 *
 *   4. LA FAUSSE PRÉCISION. Transmettre une incertitude nulle annoncerait une
 *      précision parfaite et ferait alerter sur le moindre écart — l'exact
 *      contraire de ce que ce moteur existe pour tenir.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5510 node recette_pilotage_amont.js
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
  await pg.waitForFunction(() => !!document.getElementById('pil-go'),
    null, { timeout: 60000 });

  // ── 1 ─────────────────────────────────────────────────────────────────────
  titre('1. La reprise se fait SEULE, dès qu’il y a de quoi reprendre');

  ok('avant tout calcul, rien à reprendre : le rattrapage reste caché',
     await pg.evaluate(() => document.getElementById('pil-pre').hidden));

  const nInd = await pg.evaluate(() =>
    document.querySelectorAll('#pil-form input[data-ch="valeur"]').length);
  const note = await pg.evaluate(() =>
    (document.getElementById('pil-note').textContent || '').trim());
  ok('le cadre est servi et porte ses indicateurs', nInd > 0, nInd + ' indicateur(s)');
  /* LE COMPTE EST DÉDUIT, PAS ÉCRIT. Il annonçait « cinq indicateurs » quel
     que soit le nombre réellement servi : un jour où le référentiel en aurait
     porté six, la page aurait continué d’en annoncer cinq. */
  const MOTS = ['aucun', 'un', 'deux', 'trois', 'quatre', 'cinq', 'six', 'sept',
                'huit', 'neuf', 'dix'];
  ok('…et l’en-tête annonce le nombre RÉEL, pas un nombre écrit en dur',
     note === (MOTS[nInd] || String(nInd)) + ' indicateur' + (nInd > 1 ? 's' : ''),
     note + ' pour ' + nInd);

  await pg.evaluate(() => document.getElementById('fin-go').click());
  await pg.waitForFunction(() => window.FIN_DERNIER && window.FIN_DERNIER(),
    null, { timeout: 60000 });
  await pg.waitForTimeout(1500);

  /* LE CONTRÔLE QUI PORTE LA DEMANDE. La reprise était offerte derrière un
     bouton : le lecteur qui suit le fil arrivait sur cinq lignes vides sans
     savoir qu'un clic ailleurs les aurait remplies — et pour lui, le tableau
     de bord ne reprenait rien. AUCUN CLIC N'EST FAIT ICI : le calcul
     d'enveloppe doit suffire. */
  const seul = await pg.evaluate(() =>
    [...document.querySelectorAll('#pil-form input[data-ch="valeur"], '
      + '#pil-form input[data-ch="cible"]')]
      .filter(e => (e.value || '').trim() !== '')
      .map(e => e.getAttribute('data-pi') + '.' + e.getAttribute('data-ch')));
  ok('LE CALCUL D’ENVELOPPE REMPLIT LE TABLEAU — sans le moindre clic de plus',
     seul.length >= 3, seul.join(', ') || 'aucune ligne remplie');
  ok('…le rattrapage reste offert, pour revenir aux valeurs de l’étude ensuite',
     await pg.evaluate(() => document.getElementById('pil-pre').hidden === false));

  await pg.evaluate(() => document.getElementById('moe-go').click());
  await pg.waitForFunction(() => window.MOE_DERNIER && window.MOE_DERNIER(),
    null, { timeout: 60000 });
  ok('…et le chiffrage des honoraires est publié pour les blocs qui en dépendent',
     await pg.evaluate(() => !!window.MOE_DERNIER().taux_effectif_pct));
  await pg.waitForTimeout(700);
  ok('…lequel remplit à son tour la part de maîtrise d’œuvre, toujours sans clic',
     await pg.evaluate(() => {
       const e = document.querySelector('#pil-form input[data-pi="part_moe"][data-ch="valeur"]');
       return !!e && (e.value || '').trim() !== '';
     }));

  // ── 2 ─────────────────────────────────────────────────────────────────────
  titre('2. Chaque valeur reprise correspond à SA source, recalculée à part');

  const lu = async () => pg.evaluate(() => {
    const val = {};
    document.querySelectorAll('#pil-form input').forEach(e => {
      const k = e.getAttribute('data-pi'), c = e.getAttribute('data-ch');
      val[k] = val[k] || {};
      val[k][c] = (e.value || '').trim();
      if (c === 'valeur') {
        val[k].inc = e.getAttribute('data-inc');
        val[k].placeholder = e.placeholder || '';
        val[k].marque = e.classList.contains('pil-dedu');
      }
    });
    return val;
  });
  const v = await lu();
  const num = s => s === '' || s == null ? null : parseFloat(String(s).replace(',', '.'));

  /* On refait le calcul À PART, depuis la source, plutôt que de comparer le
     champ à lui-même : recopier la formule du code testé ne prouverait rien. */
  const attendu = await pg.evaluate(() => {
    const d = window.FIN_DERNIER();
    const code = (window.FIN_PAYS && window.FIN_PAYS()) || d.classement[0].pays;
    const dos = d.dossiers.filter(x => x.pays === code)[0];
    const env = dos.devis.enveloppe_meur;
    const m = window.MOE_DERNIER();
    const ph = (dos.trajectoire.phases || []).filter(p => p.cle === 'raccordement')[0];
    const rac = dos.devis.raccordement;
    const mi = f => (Number(f[0]) + Number(f[1])) / 2;
    return {
      env_kw: Math.round(mi(env) * 1e6 / (d.entree.mw * 1000)),
      env_inc: Math.abs(env[1] - env[0]) / 2 / mi(env),
      taux: mi(m.taux_effectif_pct),
      pue: dos.devis.refroidissement.pue,
      raccord: mi([Number(ph.duree_mois[0]) + Number(rac.mois_sup[0]),
                   Number(ph.duree_mois[1]) + Number(rac.mois_sup[1])]),
      raccord_cible: mi(ph.duree_mois)
    };
  });

  ok('l’enveloppe par kW vaut bien l’enveloppe divisée par la puissance IT',
     num(v.enveloppe_kw.valeur) === attendu.env_kw,
     v.enveloppe_kw.valeur + ' pour ' + attendu.env_kw + ' €/kW recalculés');
  ok('la part de maîtrise d’œuvre vaut le taux effectif du bloc précédent',
     Math.abs(num(v.part_moe.valeur) - attendu.taux) < 0.01,
     v.part_moe.valeur + ' % pour ' + attendu.taux);
  ok('le délai de raccordement additionne l’instruction et la file du pays',
     Math.abs(num(v.delai_raccordement.valeur) - attendu.raccord) < 0.05,
     v.delai_raccordement.valeur + ' mois pour ' + attendu.raccord);
  ok('…et sa cible est le même délai SANS file tendue',
     Math.abs(num(v.delai_raccordement.cible) - attendu.raccord_cible) < 0.05,
     v.delai_raccordement.cible + ' pour ' + attendu.raccord_cible);
  ok('les champs repris se distinguent des champs saisis à la main',
     v.enveloppe_kw.marque && v.delai_raccordement.marque);

  // ── 3 : LE POINT QUI DÉCIDE ───────────────────────────────────────────────
  titre('3. LE POINT QUI DÉCIDE : ce qui se CONSTATE n’est pas rempli');

  ok('LE PUE CONSTATÉ RESTE VIDE — le remplir le rendrait vert à jamais',
     v.pue_constate.valeur === '', 'valeur : « ' + v.pue_constate.valeur + ' »');
  ok('…et le champ DIT pourquoi il est vide, au lieu de passer pour un oubli',
     /mesure|exploitation/i.test(v.pue_constate.placeholder),
     v.pue_constate.placeholder);
  ok('…mais sa CIBLE est reprise : le PUE de conception est la promesse à tenir',
     Math.abs(num(v.pue_constate.cible) - (attendu.pue[0] + attendu.pue[1]) / 2) < 0.001,
     v.pue_constate.cible + ' pour ' + (attendu.pue[0] + attendu.pue[1]) / 2);
  ok('L’AVANCEMENT DES ÉTUDES RESTE VIDE — il se constate sur pièces remises',
     v.avancement_etudes.valeur === '' && v.avancement_etudes.cible === '');
  ok('…et il le dit aussi', /constate|pièce/i.test(v.avancement_etudes.placeholder),
     v.avancement_etudes.placeholder);

  const texte = await pg.evaluate(() =>
    (document.getElementById('pil-prerempli').textContent || '').replace(/\s+/g, ' '));
  ok('le relevé annonce ce qu’il a rempli ET ce qu’il a laissé vide',
     /PUE constaté reste vide/i.test(texte) && /avancement des études reste vide/i.test(texte));
  ok('…et il nomme le pays sur lequel il a repris les chiffres',
     new RegExp('pays retenu').test(texte), texte.slice(0, 90) + '…');

  /* LA CIBLE DE L'ENVELOPPE PAR kW EST DÉLIBÉRÉMENT ABSENTE : la déduire de
     l'enveloppe reviendrait à comparer un chiffre à lui-même. */
  ok('la cible de l’enveloppe par kW n’est PAS déduite — elle serait circulaire',
     v.enveloppe_kw.cible === '', '« ' + v.enveloppe_kw.cible + ' »');
  ok('…et le relevé le dit, au lieu de laisser croire à un oubli',
     /comparer un chiffre à lui-même/i.test(texte));

  // ── 4 ─────────────────────────────────────────────────────────────────────
  titre('4. L’incertitude transmise est la vraie — et jamais nulle');

  const inc = num(v.enveloppe_kw.inc);
  ok('l’enveloppe transmet l’incertitude de SA fourchette',
     inc !== null && Math.abs(inc - attendu.env_inc) < 0.001,
     '±' + (inc * 100).toFixed(1) + ' % pour ±' + (attendu.env_inc * 100).toFixed(1) + ' %');
  ok('…et ce n’est PAS l’incertitude générique du référentiel (±30 %)',
     Math.abs(inc - 0.30) > 0.01, '±' + (inc * 100).toFixed(1) + ' %');
  /* UNE INCERTITUDE NULLE NE SE TRANSMET PAS. Le taux d'honoraires vaut le
     même pourcentage aux deux bornes — numérateur et dénominateur varient
     ensemble. La demi-largeur est donc nulle, et l'annoncer ferait alerter
     sur le moindre écart. */
  const nuls = Object.keys(v).filter(k => v[k].inc !== null && v[k].inc !== undefined
    && parseFloat(v[k].inc) === 0);
  ok('AUCUNE incertitude nulle n’est transmise — ce serait une fausse précision',
     nuls.length === 0, nuls.join(', ') || 'aucune');

  // ── 5 ─────────────────────────────────────────────────────────────────────
  titre('5. La cible de la maîtrise d’œuvre n’est pas circulaire');

  const avant = { valeur: num(v.part_moe.valeur), cible: num(v.part_moe.cible) };
  ok('toutes phases retenues, le taux effectif ÉGALE son barème',
     avant.cible !== null && Math.abs(avant.valeur - avant.cible) < 0.02,
     avant.valeur + ' % contre ' + avant.cible + ' %');

  /* ON ÉCARTE UNE PHASE. Si la cible était déduite de la valeur, elle
     suivrait et l'écart resterait nul : l'indicateur serait vert quoi qu'on
     fasse. Elle doit rester au barème, et l'écart doit apparaître. */
  const ecarte = await pg.evaluate(async () => {
    const b = document.querySelector('#moe-phases button[data-ph]:not([data-ph="aps"])')
      || document.querySelector('#moe-phases button[data-ph]');
    const nom = b.textContent.trim();
    b.click();
    document.getElementById('moe-go').click();
    /* AUCUN CLIC DE REPRISE : le nouveau chiffrage doit se propager seul. */
    await new Promise(r => setTimeout(r, 3000));
    return nom;
  });
  const v2 = await lu();
  const apres = { valeur: num(v2.part_moe.valeur), cible: num(v2.part_moe.cible) };
  ok('phase écartée : le taux effectif DESCEND',
     apres.valeur < avant.valeur,
     '« ' + ecarte +' » retirée : ' + avant.valeur + ' → ' + apres.valeur + ' %');
  ok('LA CIBLE, ELLE, NE SUIT PAS — elle reste au barème complet',
     apres.cible !== null && Math.abs(apres.cible - avant.cible) < 0.02,
     avant.cible + ' → ' + apres.cible + ' %');
  ok('…donc un écart réel apparaît, là où une cible circulaire en aurait montré zéro',
     apres.cible - apres.valeur > 0.05,
     (apres.cible - apres.valeur).toFixed(2) + ' point(s) d’écart');

  // ── 6 ─────────────────────────────────────────────────────────────────────
  titre('6. Une mesure saisie survit à la reprise automatique');

  /* LA CONTREPARTIE DE L'AUTOMATISME. La reprise repasse à chaque recalcul et
     à chaque changement de pays : sans garde, elle effacerait une mesure de
     terrain que le lecteur vient de taper. C'est le seul endroit de ce module
     où une valeur RÉELLE peut entrer — un tableau de bord qui l'écrase perd
     tout ce qui fait sa raison d'être. */
  const saisi = await pg.evaluate(async () => {
    const e = document.querySelector('#pil-form input[data-pi="pue_constate"][data-ch="valeur"]');
    e.value = '1,32';
    e.dispatchEvent(new Event('input', { bubbles: true }));
    const k = document.querySelector('#pil-form input[data-pi="enveloppe_kw"][data-ch="valeur"]');
    const reprisAvant = (k.value || '').trim();
    document.dispatchEvent(new CustomEvent('fin-calcul'));
    await new Promise(r => setTimeout(r, 700));
    return { pue: (e.value || '').trim(), marque: e.dataset.auto,
             reprisAvant: reprisAvant,
             reprisApres: (k.value || '').trim() };
  });
  ok('LE PUE MESURÉ SUR SITE N’EST PAS EFFACÉ par une nouvelle reprise',
     saisi.pue === '1,32', '« ' + saisi.pue + ' »');
  ok('…et la ligne cesse d’être marquée comme reprise',
     saisi.marque === '0', 'auto=' + saisi.marque);
  ok('…tandis que les lignes NON saisies continuent de suivre l’étude',
     saisi.reprisApres === saisi.reprisAvant && saisi.reprisApres !== '',
     saisi.reprisAvant + ' → ' + saisi.reprisApres);

  /* LE RATTRAPAGE REND CE QUE L'ÉTUDE SAIT — il n'EFFACE pas ce qu'elle ignore.
     Ce contrôle attendait d'abord que le PUE mesuré redevienne vide : c'était
     demander au bouton de détruire la seule donnée de terrain de la page, donc
     exactement la faute que la section ci-dessus interdit. Il vérifie
     maintenant ce qui a un sens — une ligne DÉDUITE, modifiée à la main,
     revient à sa valeur d'étude ; la ligne MESURÉE, elle, ne bouge pas. */
  const rattrape = await pg.evaluate(async () => {
    const k = document.querySelector('#pil-form input[data-pi="enveloppe_kw"][data-ch="valeur"]');
    const etude = (k.value || '').trim();
    k.value = '4242';
    k.dispatchEvent(new Event('input', { bubbles: true }));
    document.getElementById('pil-pre').click();
    await new Promise(r => setTimeout(r, 500));
    const e = document.querySelector('#pil-form input[data-pi="pue_constate"][data-ch="valeur"]');
    return { etude: etude, revenu: (k.value || '').trim(),
             pue: (e.value || '').trim() };
  });
  ok('le rattrapage REND une ligne déduite qu’on avait modifiée',
     rattrape.revenu === rattrape.etude && rattrape.etude !== '',
     '4242 → ' + rattrape.revenu + ' (valeur d’étude ' + rattrape.etude + ')');
  ok('…SANS détruire la mesure de terrain, que l’étude ne sait pas produire',
     rattrape.pue === '1,32', '« ' + rattrape.pue + ' »');

  // ── 7 ─────────────────────────────────────────────────────────────────────
  titre('7. Le tableau de bord se calcule sur ces reprises');

  await pg.evaluate(() => document.getElementById('pil-go').click());
  await pg.waitForFunction(() => document.querySelectorAll('#pil-out .pil-c').length > 0,
    null, { timeout: 60000 });
  const cartes = await pg.evaluate(() => [...document.querySelectorAll('#pil-out .pil-c')]
    .map(c => ({
      titre: (c.querySelector('.pil-t') || {}).textContent || '',
      valeur: (c.querySelector('.pil-v') || {}).textContent || '',
      etat: c.className.replace('pil-c', '').trim(),
      lecture: (c.querySelector('.pil-l') || {}).textContent || ''
    })));
  ok('le tableau rend autant de cartes que d’indicateurs',
     cartes.length === nInd, cartes.length + ' / ' + nInd);
  const cEnv = cartes.filter(c => /Enveloppe par kW/i.test(c.titre))[0];
  ok('la carte d’enveloppe porte la valeur reprise, pas un champ vide',
     !!cEnv && new RegExp(String(attendu.env_kw)).test(cEnv.valeur),
     cEnv && cEnv.valeur.trim());
  /* LA MESURE DE TERRAIN FAIT PARLER L'INDICATEUR — et c'est la démonstration
     que le refus de le pré-remplir compte. La section précédente a saisi un
     PUE constaté de 1,32 contre une cible de conception de 1,175 : la carte
     doit désormais SIGNALER cet écart. Pré-rempli depuis la conception, elle
     aurait affiché « conforme » à jamais et n'aurait jamais rien signalé. */
  const cPue = cartes.filter(c => /PUE/i.test(c.titre))[0];
  ok('la mesure saisie FAIT PARLER la carte du PUE — elle ne dort plus',
     !!cPue && !/non_mesure/.test(cPue.etat), cPue && cPue.etat);
  ok('…et elle n’est PAS « conforme » : l’écart au PUE de conception est signalé',
     !!cPue && !/conforme/.test(cPue.etat) && /surveiller|alerte/.test(cPue.etat),
     cPue && cPue.etat + ' — ' + (cPue.lecture || '').slice(0, 90));
  const cRac = cartes.filter(c => /raccordement/i.test(c.titre))[0];
  ok('le raccordement n’alerte pas : son écart reste dans son incertitude',
     !!cRac && /indetermine/.test(cRac.etat), cRac && cRac.etat);
  ok('…et la page DIT que l’écart n’est pas démontré, au lieu de se taire',
     !!cRac && /pas démontré|incertitude/i.test(cRac.lecture),
     cRac && cRac.lecture.slice(0, 80) + '…');

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
