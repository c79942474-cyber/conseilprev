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
  /* SANS CE MASQUE, LA RECETTE SE FAIT BANNIR — et bannit les suivantes. La
     page signale au serveur qu'elle se voit pilotée (`navigator.webdriver`,
     aucun greffon, aucune langue) et le serveur bloque alors l'adresse
     TRENTE MINUTES. Un fichier qui l'oublie ne rate pas seulement ses propres
     contrôles : il fait échouer toutes les recettes lancées dans la
     demi-heure, sur un site parfaitement sain. */
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });


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
  /* LE BLOC A DÉMÉNAGÉ AVEC SA SECTION. L'étude d'enveloppe est devenue un
     module à part : sur /panorama, `s-finance` est désormais masquée, et cette
     recette y attendait indéfiniment un bloc que la vue cachait. Elle mourait
     sur un délai dépassé — c'est-à-dire qu'elle ne couvrait plus rien du tout,
     sans le dire. */
  await pg.goto(BASE + '/enveloppe', { waitUntil: 'domcontentloaded' });
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

  /* ── CE QUI PEUT SE REMPLIR EST DÉJÀ REMPLI ──────────────────────────────
     Sept champs vides accueillaient le lecteur. Quatre d'entre eux portent
     pourtant une valeur écrite dans le référentiel : les laisser vides lui
     faisait porter le coût d'un choix que le module avait déjà fait et
     documenté. Le bouton qui les remplissait n'apparaissait qu'APRÈS un
     premier calcul infructueux — donc après le moment où il servait. */
  const pose = await pg.evaluate(() => {
    const l = {};
    document.querySelectorAll('#kpi-form input[id^="kpi-"]').forEach(e => {
      const cle = e.id.replace(/^kpi-/, '');
      const b = document.getElementById('kpi-o-' + cle);
      l[cle] = { v: (e.value || '').trim(),
                 badge: (b && b.textContent) || '', auto: e.dataset.auto || '' };
    });
    return { champs: l,
             refus: [...document.querySelectorAll('#kpi-form .kpi-refus')]
               .map(x => x.textContent),
             ligne: (document.getElementById('kpi-prerempli') || {}).textContent || '' };
  });
  const remplis = Object.keys(pose.champs).filter(k => pose.champs[k].v !== '');
  ok('DÈS L’OUVERTURE, les hypothèses de référentiel sont déjà posées',
     remplis.length >= 4, remplis.join(', ') || 'aucune');
  ok('…et CHACUNE dit d’où elle vient — sans badge, un chiffre posé se croit saisi',
     remplis.every(k => /référentiel|enveloppe/i.test(pose.champs[k].badge)),
     remplis.map(k => k + ' [' + pose.champs[k].badge + ']').join(' · '));

  /* LES DEUX REFUS SONT LE POINT DÉLICAT : ils doivent être VISIBLES avant le
     premier calcul, sinon deux cases obligatoires et vides se lisent comme un
     oubli du site — et se remplissent au jugé. */
  ok('LE COÛT DU CAPITAL ET L’IMPÔT RESTENT VIDES — ce sont des décisions',
     pose.champs.wacc.v === '' && pose.champs.is_taux.v === '',
     'CMPC « ' + pose.champs.wacc.v + ' », IS « ' + pose.champs.is_taux.v + ' »');
  ok('…et leur refus est AFFICHÉ dès l’arrivée, pas après un calcul pour rien',
     pose.refus.length === 2, pose.refus.length + ' motif(s) visible(s)');
  ok('…le motif dit pourquoi : proposer le taux qui juge, c’est choisir le verdict',
     pose.refus.some(t => /décision du comité/i.test(t))
       && pose.refus.some(t => /véhicule qui portera/i.test(t)),
     pose.refus.map(t => t.slice(0, 55)).join(' | '));
  ok('…et le relevé annonce ce qui est posé ET ce qui reste',
     /déjà posée/i.test(pose.ligne) && /Il vous en reste/i.test(pose.ligne),
     pose.ligne.replace(/\s+/g, ' ').slice(0, 120));

  /* LE REVENU N'EST PAS POSÉ D'OFFICE, et c'est délibéré : le seul montant que
     ce module sache calculer est le revenu d'ÉQUILIBRE, celui qui annule
     l'EVA. Le poser sans le dire ferait répondre « à l'équilibre » aux trois
     indicateurs — l'hypothèse renvoyée au lecteur, prise pour un résultat. */
  ok('LE REVENU N’EST PAS POSÉ D’OFFICE — il annulerait l’EVA par construction',
     pose.champs.revenu_meur_an.v === '',
     '« ' + pose.champs.revenu_meur_an.v + ' »');

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

  titre('3 bis. La durée d’amortissement suit l’étude, la saisie est protégée');

  /* AMORTIR SUR UNE AUTRE DURÉE QUE L'ÉTUDE laisse en fin d'horizon une valeur
     résiduelle qui n'apparaît dans aucun des trois indicateurs. Le référentiel
     propose 20 ans, l'étude en retient 10 : c'est l'étude qui doit gagner une
     fois qu'elle a tourné. */
  const amort = await pg.evaluate(() => {
    const c = document.getElementById('kpi-amort_ans');
    const b = document.getElementById('kpi-o-amort_ans');
    const d = window.FIN_DERNIER && window.FIN_DERNIER();
    return { v: (c.value || '').trim(), badge: (b && b.textContent) || '',
             etude: d && d.entree ? d.entree.annees : null };
  });
  ok('l’enveloppe calculée ALIGNE la durée d’amortissement sur l’étude',
     amort.etude != null && Number(amort.v.replace(',', '.')) === Number(amort.etude),
     amort.v + ' pour une étude sur ' + amort.etude + ' ans');
  ok('…et le badge cesse de dire « référentiel » : la provenance a changé',
     /enveloppe/i.test(amort.badge), amort.badge);

  /* CE QUE LE LECTEUR A TAPÉ N'EST JAMAIS REMPLACÉ, même par une valeur que la
     page avait posée elle-même auparavant. */
  const garde = await pg.evaluate(async () => {
    const c = document.getElementById('kpi-montee_ans');
    c.value = '7';
    c.dispatchEvent(new Event('input', { bubbles: true }));
    document.dispatchEvent(new CustomEvent('fin-calcul'));
    await new Promise(r => setTimeout(r, 500));
    const b = document.getElementById('kpi-o-montee_ans');
    return { v: (c.value || '').trim(), badge: (b && b.textContent) || '' };
  });
  ok('une valeur SAISIE survit à un nouveau calcul d’enveloppe',
     garde.v === '7', '« ' + garde.v + ' »');
  ok('…et son badge dit « votre saisie », pas « référentiel »',
     /saisie/i.test(garde.badge), garde.badge);

  titre('3 ter. Le revenu d’équilibre est un GESTE, et il s’annonce comme tel');

  /* LE SEUL REVENU QUE CE MODULE SACHE CALCULER EST CELUI QUI ANNULE L'EVA.
     Le poser d'office ferait répondre « à l'équilibre » aux trois indicateurs :
     l'hypothèse renvoyée au lecteur, prise pour un résultat. Il reste donc un
     bouton — et le bouton doit DIRE ce qu'il fait. */
  await pg.fill('#kpi-wacc', '8');
  await pg.fill('#kpi-is_taux', '25');
  await pg.click('#kpi-go');
  await pg.waitForTimeout(2600);
  const geste = await pg.evaluate(() => {
    const b = document.getElementById('kpi-pre');
    return { visible: !!b && !b.hidden, libelle: (b ? b.textContent : '').trim(),
             revenu: (document.getElementById('kpi-revenu_meur_an').value || '').trim() };
  });
  /* LE MOMENT OÙ LE DÉFAUT POURRAIT SE PRODUIRE. Au chargement, le revenu
     d'équilibre n'est pas calculable — les propositions n'arrivent qu'avec le
     premier calcul. C'est ICI, propositions en main et deux taux posés, qu'un
     remplissage d'office deviendrait possible : le contrôle doit donc porter
     à cet instant précis, et non seulement à l'ouverture. */
  ok('APRÈS CALCUL ET DEUX TAUX POSÉS, le revenu reste vide sans geste du lecteur',
     geste.revenu === '', '« ' + geste.revenu + ' »');
  ok('le bouton du revenu d’équilibre est offert une fois les deux taux posés',
     geste.visible);
  ok('…et son libellé annonce l’équilibre, pas une prévision',
     /équilibre/i.test(geste.libelle) && !/prévision/i.test(geste.libelle),
     geste.libelle);

  const apresGeste = await pg.evaluate(async () => {
    document.getElementById('kpi-pre').click();
    await new Promise(r => setTimeout(r, 500));
    return { revenu: (document.getElementById('kpi-revenu_meur_an').value || '').trim(),
             dit: (document.getElementById('kpi-prerempli') || {}).textContent || '' };
  });
  ok('le geste pose un revenu chiffré', /\d/.test(apresGeste.revenu),
     apresGeste.revenu + ' M€/an');
  ok('…et AVERTIT que les trois indicateurs diront « à l’équilibre »',
     /n’est pas une prévision/i.test(apresGeste.dit)
       && /équilibre/i.test(apresGeste.dit),
     apresGeste.dit.replace(/\s+/g, ' ').slice(0, 130));
  ok('…en nommant ce que ce cas limite sert à voir',
     /au-dessus/i.test(apresGeste.dit) && /en dessous/i.test(apresGeste.dit));

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
