/* RECETTE — LA QUALIFICATION ASSISTÉE, À L'ÉCRAN
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE : le SDK automatise la qualification des systèmes du registre,
 * en conservant une validation humaine.
 *
 * CE QUE LES RÈGLES PYTHON NE PEUVENT PAS VOIR. Elles font tourner le moteur
 * et les routes ; elles ne savent pas si l'écran PEINT une proposition, s'il
 * montre les extraits cités, si les deux boutons de décision existent, ni si
 * la laisse du moteur est écrite là où un auditeur la lira — c'est-à-dire à
 * l'écran, pas dans le code.
 *
 * LE CONTRÔLE QUI COMPTE EST DIFFÉRENTIEL, ICI AUSSI. Deux propositions sont
 * injectées : une VÉRIFIÉE, qui doit montrer sa classe, son article, ses
 * citations et ses deux boutons ; une TOMBÉE sur « à compléter », qui ne doit
 * montrer AUCUN bouton de validation et doit dire ce qui manque. Un écran qui
 * peindrait les deux de la même façon laisserait valider un refus.
 *
 * LES PROPOSITIONS SONT INJECTÉES, PAS DEMANDÉES À UN MODÈLE : la recette
 * mesure l'écran, et un écran qui dépendrait de la disponibilité d'une clé
 * d'API ne se mesurerait pas deux fois de la même façon.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = 'recette_locale_idf_0123456789abcdef';
let ko = 0, n = 0;
const ok = (t, c, d) => { n++; if (!c) ko++;
  console.log((c ? '  OK   ' : '  KO   ') + t + (d ? ' — ' + d : '')); };

const PROPOSITIONS = [
  { id: 901, systeme_id: 11, systeme_nom: 'Scoring credit automatise',
    classe_proposee: 'haut', classe_nom: 'Haut risque', article: 'annexe_iii',
    article_texte: 'Art. 6 §2 et annexe III — domaines à haut risque',
    motivation: 'Acces a un service financier essentiel.',
    indices: ["Evaluer la solvabilite pour l'octroi de credit", 'historique credit'],
    appui: 0.82, fragile: false, confiance_declaree: 0.9, a_completer: false,
    motif: null, motif_texte: null, moteur: 'sdk', modele: 'claude-sonnet-5',
    statut: 'en_attente', classe_retenue: null, corrigee: false,
    decide_par: null, decide_le: null, manquants: [],
    ecart: { avant: 'a_evaluer', avant_nom: 'À évaluer', apres: 'haut',
             apres_nom: 'Haut risque', change: true, premiere_classification: true } },
  { id: 902, systeme_id: 12, systeme_nom: 'Outil interne sans finalite',
    classe_proposee: null, classe_nom: null, article: null, article_texte: null,
    motivation: '', indices: [], appui: 0, fragile: true,
    confiance_declaree: null, a_completer: true, motif: 'champs_manquants',
    motif_texte: "La déclaration ne porte pas les champs sans lesquels aucune "
                 + "qualification n'est possible.",
    moteur: 'sdk', modele: 'claude-sonnet-5', statut: 'en_attente',
    classe_retenue: null, corrigee: false, decide_par: null, decide_le: null,
    manquants: [{ champ: 'finalite', nom: 'Finalité', obligatoire: true,
                  pourquoi: "L'annexe III est une liste de finalités. Sans "
                            + "finalité écrite, il n'y a rien à lui comparer." }] },
];

(async () => {
  const nav = await chromium.launch({ args: ['--no-sandbox', '--disable-blink-features=AutomationControlled'] });
  const ctx = await nav.newContext({ viewport: { width: 1500, height: 1000 }, locale: 'fr-FR',
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36' });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr', 'en-US'] });
  });

  /* Seule la LISTE est simulée. Le référentiel — donc la laisse du moteur —
     vient du vrai serveur : c'est justement ce qu'on veut mesurer. */
  await ctx.route('**/api/qualification/propositions*', r => r.fulfill({
    status: 200, contentType: 'application/json',
    body: JSON.stringify({ propositions: PROPOSITIONS, statut: 'en_attente',
                           reserve: 'reserve de recette' }) }));

  let decision = null;
  await ctx.route('**/api/qualification/*/decider', r => {
    decision = { url: r.request().url(), corps: r.request().postDataJSON() };
    pg.evaluate(() => { window.__qualifEnvoye = true; }).catch(() => {});
    return r.fulfill({ status: 200, contentType: 'application/json',
      body: JSON.stringify({ ok: true, statut: 'validee',
                             decide_par: 'C. Cerf — DPO', registre_modifie: true }) });
  });

  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e).slice(0, 180)));
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'domcontentloaded' });
  await pg.goto(BASE + '/sentinel?goto=qualif-assistee', { waitUntil: 'load' });
  /* LA PREMIÈRE ÉCRITURE ATTENDAIT « plus de Chargement » — et une liste
     ENCORE VIDE satisfait cette condition aussi bien qu'une liste peinte.
     La recette passait donc une fois sur deux, selon que la seconde requête
     était revenue ou non. On attend maintenant les cartes elles-mêmes. */
  /* AUCUN APPEL À `qualifInit()` ICI, ET C'EST LE CONTRÔLE. Le lien profond
     `?goto=` et les étapes d'un parcours guidé passent par `go()` sans
     exécuter le `;qualifInit()` écrit dans le `onclick` du menu : la page
     s'ouvrait VIDE pour qui n'y arrivait pas par la barre latérale — donc
     pour le parcours du directeur de programme, où elle figure. La recette
     l'a montré en passant une fois sur deux ; `go()` aiguille maintenant. */
  await pg.waitForFunction(
    () => document.querySelectorAll('#qualif-liste .tbl-wrap').length >= 2,
    { timeout: 25000 }).catch(() => {});
  await pg.waitForTimeout(400);

  console.log('\n── LE PANNEAU S\'OUVRE ─────────────────────────────────────');
  const visible = await pg.evaluate(() => {
    const p = document.getElementById('p-qualif-assistee');
    return !!p && getComputedStyle(p).display !== 'none';
  });
  ok('le panneau de la qualification assistée est affiché', visible);

  console.log('\n── LA LAISSE DU MOTEUR EST ÉCRITE À L\'ÉCRAN ──────────────');
  const moteur = await pg.evaluate(() =>
    (document.getElementById('qualif-moteur') || {}).textContent || '');
  ok('l\'écran nomme le moteur retenu', /sdk|API Messages/i.test(moteur),
     moteur.slice(0, 70));
  ok('l\'écran dit « aucun outil »', /aucun outil/.test(moteur));
  ok('l\'écran nomme Read, Edit et Bash parmi les refusés',
     /Read/.test(moteur) && /Edit/.test(moteur) && /Bash/.test(moteur));
  ok('l\'écran dit que le moteur n\'écrit nulle part',
     /n’écrit nulle part|n'écrit nulle part/.test(moteur));

  console.log('\n── LA PROPOSITION VÉRIFIÉE ───────────────────────────────');
  const t = await pg.evaluate(() =>
    (document.getElementById('qualif-liste') || {}).textContent || '');
  ok('la classe proposée est affichée', /Haut risque/.test(t));
  ok('l\'article invoqué est affiché', /annexe III/.test(t));
  ok('les extraits cités sont affichés',
     /Evaluer la solvabilite pour l.octroi de credit/.test(t));
  ok('l\'écart avant → après est affiché', /À évaluer/.test(t) && /→/.test(t));
  ok('l\'appui est affiché sans la confiance du modèle',
     /appui 0\.82/.test(t) && !/0\.9\b/.test(t.replace(/0\.82/g, '')));

  console.log('\n── LE REFUS NE SE VALIDE PAS ─────────────────────────────');
  const boutons = await pg.evaluate(() => {
    const res = {};
    [901, 902].forEach(id => {
      const s = document.getElementById('qualif-classe-' + id);
      res[id] = {
        choix: !!s,
        valider: !!document.querySelector(
          '[onclick="qualifDecider(' + id + ',\'valider\')"]'),
      };
    });
    return res;
  });
  ok('la proposition vérifiée porte ses deux commandes',
     boutons[901].choix && boutons[901].valider);
  ok('la proposition tombée n\'offre AUCUNE validation',
     !boutons[902].choix && !boutons[902].valider);
  ok('la proposition tombée dit ce qui manque',
     /Finalité/.test(t) && /Aucune proposition/.test(t));

  console.log('\n── LA DÉCISION PART AVEC LE NOM ──────────────────────────');
  await pg.waitForSelector('#qualif-classe-901', { timeout: 10000 });
  await pg.evaluate(() => {
    document.getElementById('qualif-decideur').value = 'C. Cerf — DPO';
  });
  await pg.click('[onclick="qualifDecider(901,\'valider\')"]');
  await pg.waitForFunction(() => window.__qualifEnvoye === true, { timeout: 8000 })
    .catch(() => {});
  await pg.waitForTimeout(400);
  ok('la décision a été envoyée', !!decision, decision ? decision.url : 'aucune');
  ok('elle porte le nom saisi',
     !!decision && decision.corps.decideur === 'C. Cerf — DPO',
     decision ? String(decision.corps.decideur) : '');
  ok('elle porte la classe retenue',
     !!decision && decision.corps.classe_retenue === 'haut',
     decision ? String(decision.corps.classe_retenue) : '');
  ok('elle vise la bonne proposition',
     !!decision && /\/901\/decider$/.test(decision.url));

  console.log('\n── LA PAGE EN ANGLAIS ────────────────────────────────────');
  /* PREMIÈRE ÉCRITURE, ET POURQUOI ELLE MESURAIT MAL : elle posait une clé
     de stockage inventée puis rechargeait la page. La bascule passe par
     `sentSetLang()`, qui connaît la vraie clé — le contrôle échouait donc
     sur la méthode de la recette, pas sur la traduction. */
  await pg.evaluate(() => sentSetLang('en'));
  await pg.waitForTimeout(500);
  const en = await pg.evaluate(() => ({
    h1: (document.querySelector('#p-qualif-assistee .page-h') || {}).textContent || '',
    eb: (document.querySelector('#p-qualif-assistee .eyebrow') || {}).textContent || '',
    p: (document.querySelector('#p-qualif-assistee .page-lead') || {}).textContent || '',
    fil: (document.getElementById('tb-pg') || {}).textContent || ''
  }));
  ok('le titre anglais est servi', /Assisted/i.test(en.h1), en.h1.slice(0, 60));
  ok('l’accroche anglaise dit que le moteur n’écrit rien',
     /writes nothing/i.test(en.p), en.p.slice(0, 70));
  ok('le fil d’Ariane suit la bascule', /Assisted/i.test(en.fil), en.fil);
  await pg.evaluate(() => sentSetLang('fr'));

  console.log('\n── AUCUNE ERREUR DE PAGE ─────────────────────────────────');
  ok('la console ne porte aucune erreur', err.length === 0, err.join(' | '));

  await nav.close();
  console.log('\n' + (ko ? 'KO ' + ko + '/' + n : 'OK ' + n + '/' + n));
  process.exit(ko ? 1 : 0);
})();
