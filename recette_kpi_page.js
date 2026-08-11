/* CRÉATION DE VALEUR — ce que seul le vrai document peut prouver.
 *
 * Le moteur est éprouvé par recette_kpi_finance.py. Ce qu'un test qui lit le
 * source NE PEUT PAS voir, et qui est ici :
 *
 *   · que le bloc REPREND L'ENVELOPPE RÉELLEMENT CALCULÉE, et celle du pays
 *     le mieux classé — pas du premier dossier rendu, qui sort dans l'ordre
 *     alphabétique du code pays. C'est exactement le défaut qui avait été
 *     trouvé sur le pont vers l'étude de durabilité : la page annonçait un
 *     pays et en envoyait un autre ;
 *   · que sans hypothèses, la page affiche des QUESTIONS et non des zéros —
 *     un tableau de zéros se lit comme un résultat ;
 *   · que le verdict « indécidable » est RENDU VISIBLE, et pas noyé dans la
 *     même teinte que les deux autres ;
 *   · que la série année par année est là, puisque c'est elle qui porte le
 *     sens décisionnel et non le chiffre isolé.
 *
 * La leçon est acquise dans ce dépôt : une branche d'affichage désactivée par
 * « if (false) » laisse un test de fichier parfaitement vert. Ce qui s'affiche
 * se vérifie dans le document.
 *
 *   POUR L'EXÉCUTER :
 *     BASE=http://127.0.0.1:5401 TOKEN=... node recette_kpi_page.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5401';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
let ko = 0;
const ok = (n, c, d) => {
  console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : ''));
  if (!c) ko++;
};
const titre = t => console.log('\n══ ' + t + ' ══\n');

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1400, height: 1000 } });

  /* MÉNAGER LE LIMITEUR DE DÉBIT, sinon la recette se fait bloquer par le site
     qu'elle éprouve — et le message « trop de requêtes » se lit alors comme
     une panne du bloc testé.
     Deux précautions : on n'attend pas le chargement complet de /sentinel après
     l'authentification (le jeton est posé dès la réponse), et on renonce aux
     images et polices, qui ne servent à aucun contrôle ici mais comptent
     chacune comme une requête. */
  await ctx.route('**/*', r =>
    (['image', 'font', 'media'].includes(r.request().resourceType())
      ? r.abort() : r.continue()));

  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));

  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.goto(BASE + '/panorama', { waitUntil: 'domcontentloaded' });
  await pg.waitForSelector('#kpi-bloc', { timeout: 25000 });

  titre('1. Le bloc se présente avant tout calcul, et dit ce qui manque');

  const dep = await pg.evaluate(() => ({
    champs: document.querySelectorAll('#kpi-form .kpi-ch').length,
    cibles: document.querySelectorAll('#kpi-cibles .kpi-ch').length,
    msg: (document.getElementById('kpi-msg') || {}).textContent || '',
    out: (document.getElementById('kpi-out') || {}).innerHTML || '',
    requis: [...document.querySelectorAll('#kpi-form label')]
      .filter(l => /requis/.test(l.textContent)).length,
  }));
  ok('les hypothèses à fournir sont présentées', dep.champs >= 7,
     dep.champs + ' champ(s)');
  ok('…les trois obligatoires sont marquées comme telles', dep.requis === 3,
     dep.requis + ' marquée(s)');
  ok('les objectifs sont proposés, et facultatifs', dep.cibles === 3,
     dep.cibles + ' objectif(s)');
  ok('avant tout calcul, la page dit qu’il faut l’enveloppe',
     /enveloppe/i.test(dep.msg), dep.msg.slice(0, 70));
  ok('…et n’affiche AUCUN chiffre', dep.out.trim() === '', dep.out.slice(0, 60));

  titre('2. LE POINT QUI DÉCIDE : sans hypothèses, des QUESTIONS, pas des zéros');

  /* Calculer l'enveloppe d'abord — le bloc s'appuie dessus. */
  await pg.evaluate(() => {
    const m = document.getElementById('fin-mw'); if (m) m.value = '100';
  });
  const cases = await pg.$$('#fin-pays input[type=checkbox]');
  for (const c of cases.slice(0, 3)) { await c.check().catch(() => {}); }
  await pg.click('#fin-go');
  await pg.waitForFunction(
    () => document.querySelectorAll('#fin-res .fin-rang').length > 0,
    null, { timeout: 40000 });

  await pg.click('#kpi-go');
  await pg.waitForFunction(
    () => (document.getElementById('kpi-out') || {}).innerHTML.trim() !== '',
    null, { timeout: 20000 });
  const vide = await pg.evaluate(() => ({
    trous: !!document.querySelector('.kpi-trous'),
    questions: [...document.querySelectorAll('.kpi-trous li')]
      .map(l => l.textContent.trim()),
    zeros: (document.getElementById('kpi-out').textContent.match(/\b0,00\b/g) || []).length,
    cartes: document.querySelectorAll('.kpi-carte').length,
  }));
  ok('sans hypothèses, le bloc affiche les questions à poser', vide.trous,
     vide.questions.length + ' question(s)');
  ok('…et AUCUNE carte d’indicateur n’est rendue', vide.cartes === 0,
     vide.cartes + ' carte(s)');
  ok('…aucun zéro n’est affiché à la place d’un chiffre manquant',
     vide.zeros === 0, vide.zeros + ' zéro(s)');
  ok('les trois questions obligatoires sont posées en toutes lettres',
     vide.questions.length === 3 && vide.questions.every(q => q.indexOf('?') > 0),
     vide.questions.map(q => q.slice(0, 34)).join(' | '));

  titre('3. Le bloc reprend l’enveloppe DU PAYS LE MIEUX CLASSÉ');

  const attendu = await pg.evaluate(() => {
    const d = window.FIN_DERNIER && window.FIN_DERNIER();
    if (!d) return null;
    const code = d.classement[0].pays;
    const dos = d.dossiers.filter(x => x.pays === code)[0];
    return { code, premierRendu: d.dossiers[0].pays,
             capex: dos.devis.enveloppe_meur };
  });
  ok('la page connaît le premier du classement', !!attendu, attendu && attendu.code);
  const dit = await pg.evaluate(
    () => (document.getElementById('kpi-msg') || {}).textContent || '');
  ok('le message nomme le pays retenu, et c’est bien le mieux classé',
     attendu && dit.indexOf(attendu.code) >= 0,
     dit.slice(0, 110));
  /* LE CONTRÔLE QUI COMPTE : quand le premier du classement n'est PAS le
     premier dossier rendu, prendre l'un pour l'autre est indétectable dans le
     source et faux à l'écran. */
  if (attendu && attendu.code !== attendu.premierRendu) {
    ok('…et il diffère du premier dossier rendu : le piège est franchi',
       dit.indexOf(attendu.premierRendu) < 0,
       attendu.code + ' retenu, ' + attendu.premierRendu + ' rendu en tête');
  } else {
    console.log('  ··   les deux coïncident sur ce jeu : contrôle non concluant ici');
  }

  titre('4. Avec les hypothèses : trois cartes, un verdict, une série');

  await pg.fill('#kpi-revenu_meur_an', '210');
  await pg.fill('#kpi-wacc', '8');
  await pg.fill('#kpi-is_taux', '25');
  await pg.fill('#kpi-montee_ans', '1');
  await pg.click('#kpi-go');
  await pg.waitForFunction(
    () => document.querySelectorAll('.kpi-carte').length > 0,
    null, { timeout: 20000 });

  const r = await pg.evaluate(() => {
    const c = [...document.querySelectorAll('.kpi-carte')];
    const teinte = e => getComputedStyle(e).borderTopColor;
    return {
      n: c.length,
      noms: c.map(x => (x.querySelector('.kpi-nom') || {}).textContent || ''),
      classes: c.map(x => x.className.replace('kpi-carte', '').trim()),
      teintes: c.map(teinte),
      synth: (document.querySelector('.kpi-synth') || {}).textContent || '',
      pieges: c.filter(x => x.querySelector('.kpi-piege')).length,
      alertes: document.querySelectorAll('.kpi-alerte').length,
      lignes: document.querySelectorAll('.kpi-serie tbody tr').length,
      reserves: [...document.querySelectorAll('#kpi-out .note')]
        .map(x => x.textContent).join(' '),
    };
  });
  ok('les trois indicateurs sont rendus', r.n === 3, r.noms.join(' | '));
  ok('…dans l’ordre EVA, ROCE, free cash flow',
     /EVA/.test(r.noms[0]) && /ROCE/.test(r.noms[1]) && /Cash/i.test(r.noms[2]),
     r.noms.map(x => x.split('—')[0].trim()).join(' → '));
  ok('chacun porte le piège qu’il tend à son lecteur', r.pieges === 3,
     r.pieges + '/3');
  ok('la synthèse dit ce que l’ensemble signifie', r.synth.length > 40,
     r.synth.slice(0, 90));

  titre('5. « Indécidable » se VOIT — et le piège du ROCE est signalé');

  const idx = r.classes.indexOf('indecidable');
  ok('un verdict indécidable est présent sur ce jeu', idx >= 0,
     r.classes.join(', '));
  if (idx >= 0) {
    /* Les canaux, pas la chaîne : une bordure ambre rend « rgb(...) » ou
       « rgba(...) » selon le navigateur, et exiger « rgb( » ferait échouer un
       contrôle sur une couleur juste. */
    const autres = r.teintes.filter((_, i) => i !== idx);
    ok('…et il ne porte PAS la même teinte que les autres',
       autres.every(t => t !== r.teintes[idx]),
       r.teintes[idx] + ' vs ' + autres.join(' / '));
  }
  ok('la hausse mécanique du ROCE est signalée', r.alertes >= 1,
     r.alertes + ' alerte(s)');

  titre('6. La série est là — c’est elle qui porte le sens, pas le chiffre seul');

  await pg.evaluate(() => {
    const d = [...document.querySelectorAll('#kpi-out details')]
      .filter(x => /série/i.test(x.textContent))[0];
    if (d) d.open = true;
  });
  const serie = await pg.evaluate(() => {
    const tr = [...document.querySelectorAll('.kpi-serie tbody tr')];
    return { n: tr.length,
             colonnes: document.querySelectorAll('.kpi-serie thead th').length,
             brut: [...document.querySelectorAll('.kpi-serie thead th')]
               .some(t => /brut/i.test(t.textContent)) };
  });
  ok('la série couvre tout l’horizon', serie.n >= 10, serie.n + ' année(s)');
  ok('…et elle porte la lecture à capitaux BRUTS, sans laquelle une hausse de '
     + 'ROCE ne s’interprète pas', serie.brut, serie.colonnes + ' colonnes');
  ok('la réserve sur les hypothèses est écrite',
     /hypothèses/i.test(r.reserves), r.reserves.slice(0, 90));

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  await nav.close();
  console.log('\n' + (ko ? ko + ' contrôle(s) en échec' : 'tout est vert') + '\n');
  process.exit(ko ? 1 : 0);
})();
