/* RECETTE — LE TAUX DE CONFORMITÉ DES NEUF NORMES
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE : un taux entre 0 et 100 % pour chacune des onze normes de
 * Sentinel, tiré des analyses de risque et des réponses aux questionnaires,
 * puis un plan de mise en conformité et de remédiation.
 *
 * CE QUE LES RÈGLES PYTHON NE PEUVENT PAS VOIR. Elles lisent le moteur et la
 * source de l'écran ; elles ne savent pas ce qui s'affiche RÉELLEMENT. Trois
 * choses n'existent que dans un navigateur, et ce sont précisément celles qui
 * décident de la lecture :
 *
 *   · la phrase « 100 % ne veut pas dire… » est-elle SUR la carte, ou
 *     reléguée là où personne ne la lit ;
 *   · le trait de plafond est-il tracé, et à la bonne abscisse ;
 *   · le plan s'ouvre-t-il sur ses verrous, ou sur ce qui rapporte le plus.
 *
 * UNE MUTATION QUI NEUTRALISERAIT LA CONDITION D'AFFICHAGE SANS TOUCHER AU
 * TEXTE passerait les règles de source — elles lisent le fichier, pas l'écran.
 * C'est exactement ce que cette recette attrape.
 *
 *     BASE=http://127.0.0.1:5901 node recette_conformite.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';

let ko = 0, n = 0;
const ok = (t, cond, siKo, mesure) => {
  n++;
  if (!cond) ko++;
  console.log((cond ? '  OK   ' : '  KO   ') + t
              + (mesure ? ' — ' + mesure : '')
              + (!cond && siKo ? ' — ' + siKo : ''));
};

/* LE DOSSIER D'ESSAI est posé dans la page AVANT que l'écran s'initialise :
   c'est le seul moyen d'éprouver un rendu qui dépend de données, sans
   dépendre de ce qu'un compte de recette contient ce jour-là. */
const DOSSIER = {
  ia_act: {a5_1: 'tenu', a5_2: 'partiel', a6_1: 'tenu'},
  nis2: {nom: 'Assureur', secteur: 'finance', effectif: 900, ca_eur: 400000000,
         mesures: {a: 'conforme', b: 'conforme', c: 'conforme'},
         gouvernance: {approbation: 'tenue'}},
  owasp_llm: {LLM01: 'oui', LLM02: 'oui', LLM06: 'partiel'},
  nist_ai_rmf: {'GOVERN 1': 'tenu', 'GOVERN 2': 'amorce', 'MAP 1': 'prouve'},
  /* UNE NORME DÉLIBÉRÉMENT VERROUILLÉE. Sans elle, le contrôle du trait de
     plafond passait « 0 verrouillée(s) » — c'est-à-dire qu'il ne mesurait
     rien tout en s'affichant en vert. Les articles sont tenus, et une mesure
     est retenue SANS justification : la déclaration d'applicabilité devient
     irrecevable, l'auditeur s'arrête à la porte, et le plafond doit se voir. */
  iso42001: {nom: 'Assureur',
             articles: {'4.1': 'conforme', '4.2': 'conforme', '5.1': 'conforme'},
             mesures: {'A.2.2': {decision: 'retenue', justification: 'SoA',
                                 mise_en_oeuvre: 'conforme'},
                       'A.2.3': {decision: 'retenue'}}}
};

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1500, height: 1100 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e).slice(0, 160)));

  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.waitForTimeout(400);
  const rep = await pg.goto(BASE + '/sentinel', { waitUntil: 'domcontentloaded' });
  ok('la page répond', rep && rep.status() === 200,
     rep ? 'HTTP ' + rep.status() : 'pas de réponse');
  if (!rep || rep.status() !== 200) { await nav.close(); process.exit(2); }
  await pg.waitForTimeout(2200);

  /* ── 1-2. LE TIROIR EXISTE ET MÈNE QUELQUE PART ───────────────────── */
  const tiroir = await pg.evaluate(() => {
    const sec = document.querySelector(
      '.sb-section.sb-pliable[data-grp="taux-conformite"]');
    const items = [...document.querySelectorAll(
      '.sb-item[data-grp="taux-conformite"]')];
    return { sec: !!sec,
             titre: sec ? (sec.querySelector('span') || {}).textContent : null,
             items: items.map(i => (i.textContent || '').trim()),
             premier: sec ? [...document.querySelectorAll('.sb-section[data-fam]')]
                            .indexOf(sec) : -1 };
  });
  ok('le tiroir « taux de conformité » existe', tiroir.sec, '', tiroir.titre);
  ok('il porte ses trois écrans', tiroir.items.length === 3, '',
     tiroir.items.join(' · '));
  ok('il passe DEVANT les sept instruments — c\'est la synthèse',
     tiroir.premier === 0, 'position ' + tiroir.premier);

  /* ── 3. L'ÉCRAN S'OUVRE SUR DES DONNÉES POSÉES ───────────────────── */
  await pg.evaluate((d) => {
    window.CONF_DECL = d;
    window.AUDIT_STATE = {a5_1: 'done', a5_2: 'partial', a6_1: 'done'};
    window.CONF_ETAT = null;
  }, DOSSIER);
  await pg.evaluate(() => {
    const it = [...document.querySelectorAll('.sb-item[data-grp="taux-conformite"]')];
    it[0].click();
  });
  await pg.waitForTimeout(1800);

  const cartes = await pg.evaluate(() => {
    const vus = [...document.querySelectorAll('#conf-grille .conf-c')];
    return vus.map(c => ({
      nom: (c.querySelector('.conf-c-n') || {}).textContent,
      val: (c.querySelector('.conf-c-v') || {}).textContent,
      nature: (c.querySelector('.conf-c-nat') || {}).textContent,
      cent: !!c.querySelector('.conf-c-cent'),
      centTexte: (c.querySelector('.conf-c-cent') || {}).textContent || '',
      verrou: !!c.querySelector('.conf-v'),
      plafond: !!c.querySelector('.conf-bar-p'),
      plafondGauche: c.querySelector('.conf-bar-p')
        ? c.querySelector('.conf-bar-p').style.left : null,
      barre: (c.querySelector('.conf-bar-f') || {style: {}}).style.width,
      mene: !!c.querySelector('.conf-go')
    }));
  });
  ok('les onze normes sont rendues', cartes.length === 11, '',
     cartes.length + ' cartes');
  const dora = cartes.find(c => /DORA/.test(c.nom || ''));
  ok('DORA affiche « — » et jamais « 0 % »',
     dora && dora.val.trim() === '—', dora ? dora.val : 'carte absente',
     dora ? dora.val.trim() : '');
  ok('DORA ne mène nulle part, puisqu\'il n\'a pas de module',
     dora && !dora.mene, 'un lien pointe vers un écran inexistant');

  /* ── 4. LA PHRASE QUI EMPÊCHE DE LIRE UN TAUX COMME UNE ATTESTATION ─ */
  const mesurees = cartes.filter(c => c.val && c.val.indexOf('%') >= 0);
  ok('chaque taux mesuré porte « 100 % ne veut pas dire » SUR sa carte',
     mesurees.length > 0 && mesurees.every(c => c.cent),
     mesurees.filter(c => !c.cent).map(c => c.nom).join(', '),
     mesurees.length + ' cartes chiffrées');
  const nist = cartes.find(c => /NIST/.test(c.nom || ''));
  ok('le cadre NIST dit qu\'il n\'est pas certifiable',
     nist && /certifiable/i.test(nist.centTexte), '',
     nist ? nist.nature : '');
  ok('le NIST parle de COUVERTURE, jamais de conformité',
     nist && /couverture/i.test(nist.nature) && !/conformité/i.test(nist.nature),
     nist ? nist.nature : 'carte absente');

  /* ── 5. LE PLAFOND EST TRACÉ, ET À LA BONNE ABSCISSE ─────────────── */
  const verrouilles = cartes.filter(c => c.verrou);
  ok('le dossier d\'essai porte bien une norme verrouillée',
     verrouilles.length > 0,
     'sans verrou, les deux contrôles suivants passeraient à vide');
  ok('une norme verrouillée porte son trait de plafond',
     verrouilles.length > 0 && verrouilles.every(c => c.plafond),
     'un verrou sans trait : le lecteur ne voit pas ce qui lui est interdit',
     verrouilles.length + ' verrouillée(s)');
  /* LE TRAIT DOIT ÊTRE À L'ABSCISSE DU PLAFOND, ET LA BARRE S'ARRÊTER AVANT.
     Un trait posé à 100 % — ou une barre qui le dépasse — dirait au lecteur
     qu'il peut encore gagner ce qui lui est justement interdit. */
  const av = verrouilles[0];
  const pct = s => parseFloat(String(s || '').replace('%', '')) || 0;
  ok('le trait est posé sous 100 % et la barre ne le dépasse pas',
     av && pct(av.plafondGauche) > 0 && pct(av.plafondGauche) < 100
        && pct(av.barre) <= pct(av.plafondGauche),
     av ? ('barre ' + av.barre + ', trait ' + av.plafondGauche) : 'aucune',
     av ? (av.nom + ' : plafond ' + av.plafondGauche) : '');

  /* ── 6. CE QUI COMMANDE EST LE PLUS BAS, PAS LA MOYENNE ──────────── */
  const tete = await pg.evaluate(() => {
    const e = document.getElementById('conf-commande');
    return e ? e.textContent.trim() : null;
  });
  const bas = Math.min.apply(null, mesurees
    .map(c => parseInt(String(c.val).replace(/[^0-9]/g, ''), 10))
    .filter(x => !isNaN(x)));
  ok('la tête annonce le PLUS BAS des taux mesurés',
     tete && tete.indexOf(String(bas)) === 0 || (tete || '').startsWith(String(bas)),
     'tête : ' + String(tete).slice(0, 60), bas + ' %');
  ok('elle avertit qu\'une moyenne n\'additionne pas des natures comparables',
     /ne s’additionnent pas|ne s'additionnent pas/.test(tete || ''),
     String(tete).slice(-90));

  /* ── 7. LE PLAN S'OUVRE SUR SES VERROUS ──────────────────────────── */
  await pg.evaluate(() => {
    const it = [...document.querySelectorAll('.sb-item[data-grp="taux-conformite"]')];
    it[1].click();
  });
  await pg.waitForTimeout(900);
  const plan = await pg.evaluate(() => {
    const rangs = [...document.querySelectorAll('#conf-plan-corps .conf-rang')]
      .map(e => e.textContent.trim());
    const actions = [...document.querySelectorAll('#conf-plan-corps .conf-a')];
    return { rangs: rangs,
             actions: actions.length,
             premier: actions.length
               ? (actions[0].querySelector('.conf-a-q') || {}).textContent : null,
             premierEstRang1: actions.length
               ? actions[0].classList.contains('conf-a1') : false,
             gains: actions.length
               ? [...actions[0].querySelectorAll('.conf-g')].map(g => g.textContent)
               : [] };
  });
  ok('le plan rend des actions', plan.actions > 0, '', plan.actions + ' actions');
  ok('le premier rang est celui qui plafonne ou met en doute',
     /Rang 1/.test((plan.rangs[0] || '')), plan.rangs.join(' | '),
     plan.rangs[0]);
  ok('la première action porte la marque du rang 1',
     plan.premierEstRang1, '', String(plan.premier).slice(0, 60));

  /* ── 8. LES LIMITES SONT DITES, PAS TUES ─────────────────────────── */
  await pg.evaluate(() => {
    const it = [...document.querySelectorAll('.sb-item[data-grp="taux-conformite"]')];
    it[2].click();
  });
  await pg.waitForTimeout(900);
  const lim = await pg.evaluate(() => {
    const b = [...document.querySelectorAll('#conf-limites-corps .conf-l')];
    return { n: b.length,
             textes: b.map(x => (x.querySelector('.conf-l-q') || {}).textContent),
             tous_a_faire: b.every(x => x.querySelector('.conf-l-f')) };
  });
  ok('les limites sont affichées', lim.n >= 3, '', lim.n + ' limites');
  ok('DORA y est nommé',
     lim.textes.some(t => /DORA/.test(t || '')), lim.textes.join(' | '));
  ok('le NIST y est rappelé comme non certifiable',
     lim.textes.some(t => /NIST/.test(t || '')), '');
  ok('chacune dit ce qu\'il faut faire', lim.tous_a_faire,
     'une limite sans « à faire » est un constat, pas un conseil');

  /* ── 9. RIEN NE DÉBORDE ──────────────────────────────────────────── */
  for (const w of [1500, 900, 390]) {
    await pg.setViewportSize({ width: w, height: 1000 });
    await pg.waitForTimeout(350);
    const deb = await pg.evaluate(() => Math.max(0,
      document.documentElement.scrollWidth - document.documentElement.clientWidth));
    ok('rien ne déborde à ' + w + ' px', deb === 0, deb + ' px');
  }

  ok('aucune erreur JavaScript', err.length === 0, err.join(' | '));

  await nav.close();
  console.log('\n' + (n - ko) + ' contrôles passés, ' + ko + ' en échec');
  process.exit(ko ? 1 : 0);
})().catch(e => { console.error('KO   la recette a rompu : ' + e); process.exit(2); });
