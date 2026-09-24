/* RECETTE — CE QU'UN `title` DISAIT, LU PAR TOUS (lot 3 : compléments dans les pages)
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LE DÉFAUT. /bulle-titre.js (lot 2) montre les `title` au doigt et au
 * clavier ; il ne peut rien pour ce que la page elle-même cache :
 *   · un bloc de score, une pastille, un en-tête de colonne ne prennent pas
 *     le focus — leur `title` ne se lit jamais au clavier ;
 *   · un bouton « × », « ‹ », « ← » s'appelle « × », « ‹ », « ← » pour un
 *     lecteur d'écran ;
 *   · un champ sans étiquette n'a pour nom que son `title` — ou rien ;
 *   · l'accueil ouvrait DEUX bulles à la souris (la native et data-tooltip) ;
 *   · un « × » de suppression était un <div> : ni focus, ni nom ;
 *   · « Terminer ✓ » ne disait qu'à la souris posée que rien n'est déclaré
 *     conforme.
 *
 * LES CONTRÔLES C-1 À C-7, T-12 ET T-13 de la spécification (§6, lot 3), plus
 * le GARDE-FOU D'INVENTAIRE (§3.1) : chaque élément inerte à `title`
 * informatif de Sentinel et de l'accueil doit être couvert par une légende
 * visible dans son écran, ou nommé dans tests/titres_generiques_admis.json.
 * Tout nouveau venu fait échouer la recette.
 *
 * DEUX COLONNES. Chaque mesure est imprimée avec sa valeur relevée sur le
 * code d'avant (commit 32fb668, par CETTE recette : AVANT ci-dessous) et sa
 * valeur maintenant. `SORTIE=fichier.json` écrit les mesures du passage ;
 * `AVANT=fichier.json` remplace la colonne d'avant par un autre relevé.
 *
 * LES CORRECTIFS DE LA REVUE DU LOT 3 (colonne « avant » : commit cbe95e2,
 * relevée par CETTE recette, serveur neuf ; les clés marquées « (cbe95e2) ») :
 *   · R-1 : un clic sur un bouton « ? » n'est pas une réponse — il lançait
 *     un POST /api/parcours/ia_act et réécrivait le bandeau du rail ;
 *   · C-4 en-têtes : le nom d'une colonne du chiffrage ne contient plus
 *     « Aide : … » (il se relisait à chaque cellule) ;
 *   · C-6 évaluation : le « × » d'une évaluation demande avant d'effacer ;
 *   · C-7 focus : après un retrait au clavier, le focus reste dans la liste ;
 *   · C-2 : le nom des dix est leur `aria-label` (et plus la bulle
 *     data-tooltip que Chromium recopiait), le globe d'i-aes.com a un nom ;
 *   · le garde-fou D : une légende ne couvre un `title` que si elle en dit
 *     les mots — plus seulement parce qu'elle porte la bonne classe.
 *
 * CHAQUE « RIEN » A SON TÉMOIN. « Le × n'a pas de bulle » passerait aussi sur
 * un script éteint : il ne compte que si, dans la même fenêtre, un élément
 * informatif S'OUVRE. C'est le défaut que ce dépôt traque — une règle qui
 * passe pour une raison sans rapport.
 *
 * AUCUNE ACTION RÉELLE. Les confirmations (prélèvement, purge, historique,
 * suppression) sont mesurées en REFUSANT la boîte de dialogue, et les routes
 * qui détruisent sont interceptées : une requête qui partirait quand même
 * est comptée, abandonnée, et fait échouer la recette.
 *
 * LE LIMITEUR : 120 requêtes par minute. Chaque chargement et chaque
 * changement d'écran attend que la fenêtre glissante le permette.
 */
const { chromium, devices } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
const DEPOT = process.env.DEPOT || __dirname;
const SECTIONS = (process.env.SECTIONS || 'A,B,C,D').split(',');
const joue = (s) => SECTIONS.indexOf(s) >= 0;
const pause = (ms) => new Promise(r => setTimeout(r, ms));

/* LA COLONNE « AVANT » : relevée par cette recette sur le commit 32fb668,
   serveur neuf (voir le rapport du lot). Une valeur absente se lit « — ». */
const AVANT_FIGE = {
  'C-1 sb-pager': '« ‹ » · « › »',
  'C-1 navInit': '« ← » · « → » · « ↑ » · « ↓ » ; raccourcis : aucun',
  'C-1 sb-lbtn': '« FR » · « EN »',
  'C-1 raci-nav': '« ▲ » · « ▼ » · « ◀ » · « ▶ »',
  'C-1 mat-modal-close': '« × » (guide) · « × » (procédure)',
  'C-2 doubles': '10',
  'C-2 noms': 'data-tooltip 10/10 ; btt « » (jamais affiché) · vbtn « 📰 Actualités IA en direct — 9 sources RSS » (la bulle data-tooltip, pas un nom)',
  'C-2 glyphes accueil': '11 sans nom ou réduits au glyphe',
  'C-3 champs': '9 champs nommés par leur seul title (« Choisir les propositions affichees. »…)',
  'C-3 aides': '0 aide visible ; parcours : rien [title]',
  'C-4 audit-kpi': 'nom « », description « Calcul : (points conformes + p… » (le title), title présent, 0 bouton d’aide',
  'C-4 bulle souris': '{"ouvre":false} (pas de bouton)',
  'C-4 bulle doigt': '{"present":false} (pas de bouton)',
  'C-4 accueil': 'title sur .cpc-sub, 0 bouton',
  'C-5 légendes': '0 écran sur 7',
  'C-5 inventaire': '151 génériques non couverts',
  'C-6 avertissements': '4 confirmations, « Terminer » : title seulement',
  'C-7 cliquables': 'registre 4 div · comparateur 2 span · évaluations 1 div ; 0 bouton',
  'C-7 Entrée': 'registre : pas de focus ; comparateur : pas de focus',
  'T-12 ×': 'bulle ouverte « Fermer cette fenêtre »',
  'T-13 arrêts': '{"audit-ia-act":41,"iso42001":36,"iso27001":34}',
  'rag-drop-zone': 'title « Glissez-deposez… », texte « Cliquez ou déposez un fichier ici »',
  /* Relevées sur cbe95e2 (le lot 3 avant ses correctifs), serveur neuf. */
  'R-1 rail': '(cbe95e2) 2 clic(s) sur « ? » : 1 POST /api/parcours/ia_act, DECL_VERSION +2',
  'C-4 en-têtes': '(cbe95e2) « Assiette annuelle Aide : Assiette annuelle »… 12 noms sur 12 embarquent « Aide : »',
  'C-6 évaluation': '(cbe95e2) aucune question : effacée d’une touche, 0 après refus ; nom « Supprimer l’évaluation 01 »',
  'C-7 focus': '(cbe95e2) comparateur : focus sur BODY',
  'C-2 btt': '(cbe95e2) aria-label « Retour en haut », ignoré par l’arbre (jamais affiché)',
  'C-2 globe': '(cbe95e2) « 🌐 » ; site basculé, description « Le site i-aes.com ne répond pas… »',
  'C-4 clic ailleurs': '(cbe95e2) bouton sans focus : bulle OUVERTE et aria-expanded="true" après un clic ailleurs',
};
let AVANT = AVANT_FIGE;
/* T-13 : LE RELEVÉ D'AVANT, PAS DES CONSTANTES. Périmètre : les éléments
   VISIBLES de #p-<écran> dont tabIndex ≥ 0 parmi TABULABLE — l'écran seul,
   sans le menu latéral ni la barre du haut. La spécification annonçait
   51 / 46 / 44 sans dire son périmètre : l'écart avec ce relevé est
   constant (10), et ce n'est pas le document entier (121 sur l'audit,
   imprimé à chaque passage). Ce qui compte ici est la DIFFÉRENCE : +6 sur
   l'audit, les boutons d'aide ; rien ailleurs. */
const T13_AVANT = JSON.parse(AVANT_FIGE['T-13 arrêts']);
if (process.env.AVANT) { try { AVANT = JSON.parse(fs.readFileSync(process.env.AVANT, 'utf8')); } catch (e) { /* on garde le figé */ } }
const MESURES = {};
let ko = 0, n = 0;
const lignes = [];
/* UNE LIGNE = un contrôle, sa mesure maintenant, sa mesure d'avant. */
function ok(cle, libelle, condition, mesure) {
  n++; if (!condition) ko++;
  const m = mesure === undefined ? '' : String(mesure);
  if (cle) MESURES[cle] = m;
  console.log((condition ? '  OK   ' : '  KO   ') + libelle + (m ? ' — ' + m.slice(0, 220) : ''));
  if (cle) lignes.push({ cle, libelle, avant: AVANT[cle] || '—', apres: m, ok: !!condition });
}
const dire = (t) => console.log('  ..   ' + t);

const FURTIF = (ctx) => ctx.addInitScript(() => {
  Object.defineProperty(navigator, 'webdriver', { get: () => false });
  Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
  Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
});
/* UNE OUVERTURE DE #bulle-titre = un passage de caché à visible. */
const COMPTEURS = (ctx) => ctx.addInitScript(() => {
  window.__ouvertures = 0;
  let vis = false;
  new MutationObserver(rs => {
    const b = rs.map(r => r.target).find(t => t.id === 'bulle-titre');
    if (!b) return;
    const v = !b.hasAttribute('hidden');
    if (v && !vis) window.__ouvertures++;
    vis = v;
  }).observe(document, { subtree: true, attributes: true, attributeFilter: ['hidden'] });
});

/* ── LE LIMITEUR ─────────────────────────────────────────────────────────
   Toutes les requêtes de tous les contextes, horodatées : avant de charger
   une page (une centaine de requêtes) on attend une fenêtre presque vide ;
   avant de changer d'écran, une fenêtre qui en laisse passer une trentaine. */
const requetes = [];
const refus = [], erreurs = [];
async function rythme(seuil) {
  for (;;) {
    const t = Date.now();
    while (requetes.length && t - requetes[0] > 61000) requetes.shift();
    if (requetes.length <= seuil) return;
    await pause(1000);
  }
}

/* ── LES ROUTES QUI DÉTRUISENT : interceptées, comptées, abandonnées. ── */
const DESTRUCTRICES = [/\/api\/clients\/billing-run/, /\/api\/rgpd\/purge(\?|$)/, /\/api\/historique\/purge-all/,
                       /\/api\/registre\/\d+/];
const detruites = [], simulations = [];
/* R-1 : les calculs d'avancement du rail de l'audit, comptés (ils partent,
   ils ne gardent rien : /api/parcours/<norme> calcule et répond). */
const railIa = [];

async function nouveau(nav, options) {
  const ctx = await nav.newContext(options);
  await FURTIF(ctx); await COMPTEURS(ctx);
  await ctx.route('**/api/**', (route) => {
    const r = route.request();
    if (DESTRUCTRICES.some(re => re.test(r.url())) && r.method() !== 'GET') {
      /* LA SIMULATION DE PURGE que l'écran RGPD lance de lui-même à
         l'ouverture (`rgpdPurge(true)`) ne modifie rien : elle est
         abandonnée comme les autres, par prudence, mais n'est pas comptée
         comme une action partie. Mesuré au premier passage : deux. */
      let corps = {}; try { corps = JSON.parse(r.postData() || '{}'); } catch (e) { /* rien */ }
      if (/\/api\/rgpd\/purge/.test(r.url()) && corps.simulation === true) simulations.push(r.url());
      else detruites.push(r.method() + ' ' + r.url());
      return route.abort();
    }
    return route.continue();
  });
  const p = await ctx.newPage();
  p.on('request', (r) => { requetes.push(Date.now());
    if (r.method() === 'POST' && /\/api\/parcours\/ia_act(\?|$)/.test(r.url())) railIa.push(Date.now()); });
  p.on('pageerror', e => erreurs.push(String(e).slice(0, 160)));
  p.on('response', r => { if (r.status() === 429) refus.push(r.url()); });
  /* LES BOÎTES DE DIALOGUE SONT REFUSÉES, TOUJOURS — et leur texte gardé. */
  p.__dialogues = [];
  p.on('dialog', d => { p.__dialogues.push(d.type() + ' : ' + d.message()); d.dismiss().catch(() => {}); });
  const cdp = await ctx.newCDPSession(p);
  return { ctx, p, cdp };
}
async function sentinel(p, ecran) {
  await rythme(15);
  await p.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'domcontentloaded' });
  const rep = await p.goto(BASE + '/sentinel' + (ecran ? '?goto=' + ecran : ''), { waitUntil: 'domcontentloaded' });
  await p.waitForFunction(() => !!document.getElementById('css-bulle-ouverte'), null, { timeout: 15000 }).catch(() => {});
  await p.waitForTimeout(3000);
  await p.evaluate(() => { const b = document.getElementById('ck-banner'); if (b) b.classList.remove('show'); });
  return rep && rep.status();
}
async function aller(p, ecran, ms) {
  await rythme(80);
  await p.evaluate(e => window.go(e), ecran);
  await p.waitForTimeout(ms || 1500);
}

/* LE NOM ET LA DESCRIPTION, tels que le navigateur les calcule (CDP). */
async function ax(cdp, sel) {
  const { root } = await cdp.send('DOM.getDocument', { depth: 0 });
  const { nodeId } = await cdp.send('DOM.querySelector', { nodeId: root.nodeId, selector: sel });
  if (!nodeId) return null;
  const r = await cdp.send('Accessibility.getPartialAXTree', { nodeId, fetchRelatives: false });
  const x = r.nodes[0] || {};
  return { role: x.role && x.role.value, nom: (x.name && x.name.value) || '',
           description: (x.description && x.description.value) || '', ignore: !!x.ignored };
}
const AXS = async (cdp, sels) => { const o = []; for (const s of sels) o.push(await ax(cdp, s)); return o; };

/* L'ÉTAT DE #bulle-titre. */
const BULLE = () => {
  const b = document.getElementById('bulle-titre');
  if (!b) return { existe: false, visible: false, texte: '' };
  const cs = getComputedStyle(b);
  return { existe: true, visible: !b.hidden && cs.display !== 'none', texte: b.textContent || '' };
};

/* TABULER JUSQU'À un élément : le focus au précédent dans l'ordre, puis une
   vraie touche Tab (même méthode que recette_bulle_titre.js). */
const TABULABLE = 'a[href],button:not([disabled]),input:not([disabled]),select,textarea,[tabindex]';
async function tabulerVers(p, sel) {
  const pret = await p.evaluate(([s, T]) => {
    const vis = e => { const q = e.getBoundingClientRect(); return q.width > 0 && q.height > 0; };
    const t = [...document.querySelectorAll(T)].filter(e => e.tabIndex >= 0 && vis(e));
    const i = t.indexOf(document.querySelector(s));
    if (i < 1) return false;
    t[i - 1].focus();
    return true;
  }, [sel, TABULABLE]);
  if (!pret) return false;
  await p.waitForTimeout(1100);
  await p.keyboard.press('Tab');
  return p.evaluate(s => document.activeElement === document.querySelector(s), sel);
}
const arrets = (p, ecran) => p.evaluate(([ecran, T]) => {
  const vis = e => { const q = e.getBoundingClientRect(); return q.width > 0 && q.height > 0; };
  return [...document.querySelectorAll('#p-' + ecran + ' :is(' + T + ')')].filter(e => e.tabIndex >= 0 && vis(e)).length;
}, [ecran, TABULABLE]);

/* LE RELEVÉ DU GARDE-FOU : les éléments INERTES à `title` informatif — le
   critère de /bulle-titre.js (§2.2), mode « appui » —, et pour chacun, la
   légende qui le couvre dans son écran. */
const RELEVE = () => {
  const norm = s => String(s == null ? '' : s).toLowerCase().replace(/["«»“”„]/g, '').replace(/\s+/g, ' ').trim().replace(/[\s.:;!?…]+$/, '');
  const RACC = /^\s*\((?:alt|ctrl|maj|shift|⌘|cmd)[^)]*\)$/i;
  const INTER = 'a[href],button,label,summary,[onclick],[role=button],[role=link],[role=tab],[role=menuitem],[role=checkbox],[role=switch],[role=option],[contenteditable=""],[contenteditable=true]';
  const nom = t => { const ids = (t.getAttribute('aria-labelledby') || '').trim();
    if (ids) { const x = ids.split(/\s+/).map(i => (document.getElementById(i) || {}).textContent || '').join(' '); if (norm(x)) return x; }
    const al = t.getAttribute('aria-label'); if (al && norm(al)) return al;
    if (t.labels && t.labels.length) { const l = [...t.labels].map(x => x.textContent).join(' '); if (norm(l)) return l; }
    return t.textContent || ''; };
  const informatif = t => { const ti = norm(t.getAttribute('title')), nm = norm(nom(t));
    if (ti.length < 2 || ti === nm) return false; if (nm && ti.indexOf(nm) === 0 && RACC.test(ti.slice(nm.length))) return false; return true; };
  const vis = e => e.getClientRects().length > 0 && e.getBoundingClientRect().width > 0;
  const sel = window.infobulles && window.infobulles.selecteur;
  const out = [];
  for (const t of document.querySelectorAll('[title]')) {
    if (!norm(t.title) || !vis(t)) continue;
    if (/^(IFRAME|INPUT|SELECT|TEXTAREA|OPTION)$/.test(t.tagName) || t.closest('select,datalist')) continue;
    if (t.closest('svg') || t.closest('[data-graphe]') || t.closest('[data-tt]')) continue;
    if (sel) { let d = null; try { d = t.closest(sel); } catch (e) { /* rien */ } if (d) continue; }
    if (!informatif(t) || t.closest(INTER) || getComputedStyle(t).cursor === 'pointer') continue;
    const ecran = (t.closest('.page') || {}).id || '(hors écran)';
    const classes = String(t.className || '').split(/\s+/).filter(Boolean);
    const portee = t.closest('.page') || document;
    /* UNE LÉGENDE NE COUVRE QUE CE QU'ELLE DIT. La première version se
       contentait de la bonne classe et de dix caractères : « Mesure en
       cours… » couvrait alors n'importe quel `title` (revue du lot 3).
       Désormais, les mots du `title` (quatre lettres et plus) doivent se
       retrouver dans les légendes de sa classe, au moins aux sept dixièmes. */
    const mots = x => (norm(x).match(/[a-zà-ÿœæ0-9]{4,}/g) || []);
    const legs = [...portee.querySelectorAll('[data-legende]')].filter(l => vis(l)
      && (l.getAttribute('data-legende') || '').split(/\s+/).some(c => classes.indexOf(c) >= 0));
    const dits = new Set(mots(legs.map(l => l.textContent).join(' ')));
    const mt = mots(t.getAttribute('title'));
    const part = mt.length ? mt.filter(m => dits.has(m)).length / mt.length : 0;
    const legende = legs.length > 0 && part >= 0.7;
    if (!t.__inv) t.__inv = (window.__invSeq = (window.__invSeq || 0) + 1);
    out.push({ inv: t.__inv, ecran, classes, legende, part: Math.round(part * 100) / 100,
               title: t.getAttribute('title').slice(0, 80), texte: (t.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 30) });
  }
  return out;
};

(async () => {
  const nav = await chromium.launch();
  let ctx, p, cdp;

  // ══ A. POSTE — Sentinel, souris et clavier ═════════════════════════════
  if (joue('A')) {
  console.log('\n══ A. Sentinel au poste (1280 × 900) ══');
  ({ ctx, p, cdp } = await nouveau(nav, { viewport: { width: 1280, height: 900 } }));
  /* Une évaluation enregistrée, pour que la liste « Mes évaluations » porte
     son « × » (le stockage de ce navigateur, rien d'autre). */
  await ctx.addInitScript(() => { try { localStorage.setItem('cpEvaluations', JSON.stringify([{ id: 424242,
    date: '2026-09-01T10:00:00Z', type: 'audit', score: 50, scoreMax: 100, level: 'moyen', badge: 'MOYEN',
    title: 'Évaluation de recette', subtitle: 'posée par recette_complements.js' }])); } catch (e) { /* rien */ } });
  ok(null, 'la page répond', (await sentinel(p, 'audit-ia-act')) === 200);

  /* C-4 — LE BLOC DE SCORE « 72 % » ET SON BOUTON D'AIDE. */
  console.log('\n  C-4 — div.audit-kpi et son bouton d’aide (souris)');
  const kpi = await ax(cdp, '#p-audit-ia-act .audit-kpi');
  const aides = await p.evaluate(() => [...document.querySelectorAll('#p-audit-ia-act .audit-kpi .aide-titre')].map(b => {
    const r = b.getBoundingClientRect(), d = document.getElementById(b.getAttribute('aria-describedby') || '');
    return { l: Math.round(r.width), h: Math.round(r.height), type: b.type, exp: b.getAttribute('aria-expanded'),
             texte: d ? d.textContent : null, cache: d ? d.hidden : null };
  }));
  const titreKpi = await p.evaluate(() => (document.querySelector('#p-audit-ia-act .audit-kpi') || {}).title || '');
  const axAide = await ax(cdp, '#p-audit-ia-act .audit-kpi .aide-titre');
  ok('C-4 audit-kpi', 'C-4 le bloc garde un nom vide (la valeur reste ce qui se lit) et perd son title',
     !!kpi && kpi.nom === '' && titreKpi === '' && aides.length === 6,
     'nom « ' + (kpi ? kpi.nom : '?') + ' », description « ' + (kpi ? kpi.description.slice(0, 30) : '') + ' », title '
       + (titreKpi ? 'présent' : 'absent') + ', ' + aides.length + ' bouton(s) d’aide');
  ok(null, 'C-4 six boutons d’aide de 24 px ou plus, type button, aria-expanded="false", texte caché non vide',
     aides.length === 6 && aides.every(a => a.l >= 24 && a.h >= 24 && a.type === 'button' && a.exp === 'false' && a.cache === true && (a.texte || '').length > 10),
     JSON.stringify(aides.map(a => a.l + '×' + a.h)));
  ok(null, 'C-4 le bouton s’appelle « Aide : Score global », sa description est l’explication',
     !!axAide && axAide.nom === 'Aide : Score global' && axAide.description === (aides[0] || {}).texte,
     axAide ? 'nom « ' + axAide.nom + ' », description « ' + axAide.description.slice(0, 40) + '… »' : 'absent');
  let c4 = { ouvre: false };
  const r0 = railIa.length, v0 = await p.evaluate(() => window.DECL_VERSION || 0);
  if (aides.length) {
    const b = await p.$('#p-audit-ia-act .audit-kpi .aide-titre');
    await b.scrollIntoViewIfNeeded(); await b.click(); await p.waitForTimeout(300);
    const v1 = await p.evaluate(BULLE), e1 = await b.getAttribute('aria-expanded');
    await b.click(); await p.waitForTimeout(300);
    const v2 = await p.evaluate(BULLE), e2 = await b.getAttribute('aria-expanded');
    c4 = { ouvre: v1.visible && v1.texte === aides[0].texte && e1 === 'true', ferme: !v2.visible && e2 === 'false' };
  }
  ok('C-4 bulle souris', 'C-4 au clic de souris, la bulle s’ouvre avec le texte et aria-expanded bascule ; au second, elle se ferme',
     c4.ouvre && c4.ferme, JSON.stringify(c4));
  /* R-1 — LIRE UNE AIDE N'EST PAS RÉPONDRE. Les deux clics ci-dessus ne
     doivent lancer aucun calcul du rail. LE TÉMOIN : un clic sur un autre
     bouton de l'écran (le guide, ouvert plus bas pour C-1), que le rail
     compte comme une réponse — il doit, lui, en lancer un. Sans lui, « 0 »
     passerait aussi sur un écouteur débranché. */
  await p.waitForTimeout(1500);
  const r1 = { clics: aides.length ? 2 : 0, post: railIa.length - r0, version: (await p.evaluate(() => window.DECL_VERSION || 0)) - v0 };

  /* C-4 CLIC AILLEURS, LE BOUTON N'AYANT JAMAIS EU LE FOCUS. Safari, et
     Firefox sous macOS, ne donnent pas le focus à un bouton cliqué : la
     bulle ne pouvait donc pas se fermer par le départ du focus, sa seule
     sortie à la souris. Reproduit ici en annulant le mousedown sur le
     bouton (le focus ne bouge pas, le clic part quand même) ; le clic
     ailleurs tombe sur la légende P1/P2/P3, du texte qui n'agit pas.
     LE TÉMOIN est dans la mesure : la bulle était ouverte, et le focus
     n'était pas sur le bouton — sinon « fermée » ne prouverait rien. */
  let c4s = { ouverte: false };
  if (aides.length) {
    /* Le contrôle précédent a laissé le focus SUR le bouton (Chromium le
       donne au clic) : on le retire d'abord — sinon le clic ailleurs
       fermerait par le départ du focus, et ne prouverait rien. */
    await p.evaluate(() => { const a = document.activeElement; if (a && a !== document.body && a.blur) a.blur();
      window.__sansFocus = e => { if (e.target.closest && e.target.closest('.aide-titre')) e.preventDefault(); };
      document.addEventListener('mousedown', window.__sansFocus, true); });
    const b = await p.$('#p-audit-ia-act .audit-kpi .aide-titre');
    await b.scrollIntoViewIfNeeded(); await b.click(); await p.waitForTimeout(300);
    const v1 = await p.evaluate(BULLE), e1 = await b.getAttribute('aria-expanded');
    const focusBouton = await p.evaluate(() => !!document.activeElement && document.activeElement.classList.contains('aide-titre'));
    const leg = await p.$('#p-audit-ia-act [data-legende="audit-item-prio"]');
    await leg.scrollIntoViewIfNeeded(); await leg.click(); await p.waitForTimeout(300);
    const v2 = await p.evaluate(BULLE), e2 = await b.getAttribute('aria-expanded');
    await p.evaluate(() => document.removeEventListener('mousedown', window.__sansFocus, true));
    c4s = { ouverte: v1.visible && e1 === 'true', focusBouton, apres: v2.visible ? 'ouverte' : 'fermée', exp: e2 };
    if (v2.visible) await b.click();
  }
  ok('C-4 clic ailleurs', 'C-4 bouton cliqué SANS prendre le focus (Safari, Firefox sous macOS) : un clic ailleurs ferme la bulle',
     c4s.ouverte && c4s.focusBouton === false && c4s.apres === 'fermée' && c4s.exp === 'false',
     'bouton sans focus : bulle ' + (c4s.apres || '?') + ', aria-expanded="' + (c4s.exp || '?') + '" après un clic ailleurs'
       + (c4s.ouverte ? '' : ' (la bulle ne s’était pas ouverte)'));

  /* C-5 — LA LÉGENDE DES PASTILLES DE PRIORITÉ. */
  const leg = async (ecran) => p.evaluate(e => [...document.querySelectorAll('#p-' + e + ' [data-legende]')]
    .filter(l => l.getClientRects().length > 0).map(l => ({ classes: l.getAttribute('data-legende'), texte: l.textContent.replace(/\s+/g, ' ').trim() })), ecran);
  const legendes = { 'audit-ia-act': await leg('audit-ia-act') };

  /* T-13 — LES ARRÊTS DE TABULATION. */
  const t13 = { 'audit-ia-act': await arrets(p, 'audit-ia-act') };
  const t13Doc = await p.evaluate(T => { const vis = e => { const q = e.getBoundingClientRect(); return q.width > 0 && q.height > 0; };
    return [...document.querySelectorAll(T)].filter(e => e.tabIndex >= 0 && vis(e)).length; }, TABULABLE);

  /* C-1 — LES BOUTONS À GLYPHE. */
  console.log('\n  C-1 — noms des boutons à glyphe');
  const pager = await AXS(cdp, ['.sb-pager-btn:nth-of-type(1)', '.sb-pager-btn:nth-of-type(2)']);
  ok('C-1 sb-pager', 'C-1 ‹ › du menu : « Section précédente », « Section suivante »',
     pager.every(Boolean) && pager[0].nom === 'Section précédente' && pager[1].nom === 'Section suivante',
     pager.map(a => '« ' + (a && a.nom) + ' »').join(' · '));
  const navs = await AXS(cdp, ['#nav-prev', '#nav-next', '#nav-top', '#nav-bottom']);
  const touches = await p.evaluate(() => ['nav-prev', 'nav-next', 'nav-top', 'nav-bottom'].map(i => {
    const b = document.getElementById(i); return b ? b.getAttribute('aria-keyshortcuts') : null; }));
  ok('C-1 navInit', 'C-1 ← → ↑ ↓ : le nom de l’action, et le raccourci dans aria-keyshortcuts',
     navs.every(Boolean) && navs.map(a => a.nom).join('|') === 'Module précédent|Module suivant|Haut de page|Bas de page'
       && touches.join('|') === 'Alt+ArrowLeft|Alt+ArrowRight|Alt+ArrowUp|Alt+ArrowDown',
     navs.map(a => '« ' + (a && a.nom) + ' »').join(' · ') + ' ; raccourcis : ' + (touches.filter(Boolean).join(', ') || 'aucun'));
  const langues = await AXS(cdp, ['.sb-lbtn[data-lang="fr"]', '.sb-lbtn[data-lang="en"]']);
  ok('C-1 sb-lbtn', 'C-1 FR / EN : le texte visible est DANS le nom, qui dit la langue (2.5.3)',
     langues.every(Boolean) && /^FR\b/.test(langues[0].nom) && langues[0].nom.length > 3 && /^EN\b/.test(langues[1].nom) && langues[1].nom.length > 3,
     langues.map(a => '« ' + (a && a.nom) + ' »').join(' · '));

  /* LA FENÊTRE DU GUIDE, puis celle d'une procédure : leur « × ». */
  const rt = railIa.length;
  await p.evaluate(() => { const b = document.querySelector('#p-audit-ia-act .page-guide-btn'); if (b) b.click(); });
  await p.waitForTimeout(1500);
  r1.temoin = railIa.length - rt;
  ok('R-1 rail', 'R-1 un clic sur « ? » ne lance aucun calcul du rail (témoin : un autre bouton de l’écran en lance un)',
     r1.clics === 2 && r1.post === 0 && r1.version === 0 && r1.temoin >= 1,
     r1.clics + ' clic(s) sur « ? » : ' + r1.post + ' POST /api/parcours/ia_act, DECL_VERSION +' + r1.version
       + ' — témoin (bouton du guide) : ' + r1.temoin + ' POST');
  const xGuide = await ax(cdp, '#guide-modal.on .mat-modal-close');
  await p.evaluate(() => { const m = document.getElementById('guide-modal'); if (m) m.classList.remove('on'); });

  /* T-12 — LE × D'UNE FENÊTRE ATTEINT PAR TAB : pas de bulle ; un élément
     informatif de la même fenêtre, lui, a la sienne (le témoin). */
  console.log('\n  T-12 — Tab jusqu’au × d’une fenêtre ; Échap');
  await aller(p, 'maturite');
  await p.evaluate(() => { if (typeof window.procOpenDoc === 'function') window.procOpenDoc('01'); });
  await p.waitForTimeout(900);
  const xProc = await ax(cdp, '#proc-modal .mat-modal-close');
  ok('C-1 mat-modal-close', 'C-1 le « × » des fenêtres s’appelle « Fermer cette fenêtre »',
     !!xGuide && !!xProc && xGuide.nom === 'Fermer cette fenêtre' && xProc.nom === 'Fermer cette fenêtre',
     '« ' + (xGuide && xGuide.nom) + ' » (guide) · « ' + (xProc && xProc.nom) + ' » (procédure)');
  await p.evaluate(() => {
    const corps = document.getElementById('proc-modal-body');
    const b = document.createElement('button'); b.id = 'recette-info-modale'; b.textContent = 'Détail';
    b.title = 'Explication posée par la recette dans la fenêtre modale';
    if (corps) corps.insertBefore(b, corps.firstChild);
  });
  const t12x = await tabulerVers(p, '#proc-modal .mat-modal-close');
  await p.waitForTimeout(700);
  const vX = await p.evaluate(BULLE);
  await p.evaluate(() => window.bulleTitre && window.bulleTitre.fermer());
  const t12i = await tabulerVers(p, '#recette-info-modale');
  await p.waitForTimeout(700);
  const vI = await p.evaluate(BULLE);
  ok('T-12 ×', 'T-12 le ×, atteint par Tab, n’a PAS de bulle (son title égale son nom)',
     t12x && !vX.visible && t12i && vI.visible,
     (vX.visible ? 'bulle ouverte « ' + vX.texte + ' »' : 'aucune bulle') + ' — témoin, un élément informatif de la fenêtre : '
       + (vI.visible ? 'bulle ouverte' : 'RIEN (le témoin ne prouve rien)'));
  await p.keyboard.press('Escape'); await p.waitForTimeout(400);
  const e1 = await p.evaluate(() => ({ bulle: !document.getElementById('bulle-titre').hidden, modale: !!document.querySelector('#proc-modal.on') }));
  await p.keyboard.press('Escape'); await p.waitForTimeout(400);
  const e2 = await p.evaluate(() => !!document.querySelector('#proc-modal.on'));
  ok(null, 'T-12 le premier Échap ferme la bulle et laisse la fenêtre, le second ferme la fenêtre',
     vI.visible && !e1.bulle && e1.modale && !e2, JSON.stringify(e1) + ', puis fenêtre ' + (e2 ? 'ouverte' : 'fermée'));

  /* LES ÉCRANS DE CONFORMITÉ : légendes et arrêts de tabulation. */
  for (const e of ['iso42001', 'iso27001', 'iso27001-soa', 'nis2-gouvernance', 'benchmark', 'ia50']) {
    await aller(p, e, 2200);
    legendes[e] = await leg(e);
    if (e === 'iso42001' || e === 'iso27001') t13[e] = await arrets(p, e);
  }
  const ecransLeg = Object.keys(legendes).filter(k => legendes[k].length > 0);
  ok('C-5 légendes', 'C-5 une légende visible sur chacun des 7 écrans à pastilles répétées',
     ecransLeg.length === 7, ecransLeg.length + ' écran(s) sur 7 : ' + ecransLeg.join(', '));
  const prio = (legendes['audit-ia-act'][0] || {}).texte || '';
  ok(null, 'C-5 la légende de l’audit dit P1, P2 et P3', /P1/.test(prio) && /P2/.test(prio) && /P3/.test(prio), prio.slice(0, 90));
  dire('T-13 document entier sur l’audit (périmètre de la spécification) : ' + t13Doc);
  ok('T-13 arrêts', 'T-13 arrêts de tabulation : le relevé d’avant + 6 boutons d’aide sur l’audit, les écrans ISO inchangés',
     t13['audit-ia-act'] === T13_AVANT['audit-ia-act'] + 6 && t13['iso42001'] === T13_AVANT['iso42001'] && t13['iso27001'] === T13_AVANT['iso27001'],
     JSON.stringify(t13));

  /* LES FLÈCHES DE LA MATRICE RACI. */
  await aller(p, 'parties', 2500);
  const raci = await AXS(cdp, ['.raci-nav-up', '.raci-nav-down', '.raci-nav-left', '.raci-nav-right']);
  ok('C-1 raci-nav', 'C-1 ▲ ▼ ◀ ▶ de la matrice RACI : « Défiler vers le haut »…',
     raci.every(Boolean) && raci.map(a => a.nom).join('|') === 'Défiler vers le haut|Défiler vers le bas|Défiler vers la gauche|Défiler vers la droite',
     raci.map(a => '« ' + (a && a.nom) + ' »').join(' · '));

  /* RAG — LA ZONE DE DÉPÔT. */
  await aller(p, 'rag');
  const rag = await p.evaluate(() => { const z = document.getElementById('rag-drop-zone');
    return z ? { title: z.getAttribute('title'), texte: z.innerText.replace(/\s+/g, ' ') } : null; });
  ok('rag-drop-zone', '§3.1 c) #rag-drop-zone : plus de title, le texte visible dit « glissez-déposez » et « cliquez »',
     !!rag && rag.title === null && /glissez-déposez/i.test(rag.texte) && /cliquez/i.test(rag.texte),
     rag ? (rag.title ? 'title « ' + rag.title + ' »' : 'pas de title') + ', texte « ' + rag.texte.slice(0, 60) + ' »' : 'absente');

  /* C-4 EN-TÊTES — LE NOM DES COLONNES DU CHIFFRAGE. Deux cas d'usage
     retenus dans l'état LOCAL du parcours (mémoire de la page, aucune
     écriture serveur), puis l'étape 4 (ROI, 8 colonnes à aide) et l'étape 3
     (priorisation, 4). Chaque <th> doit s'appeler par son libellé ; son
     bouton, lui, garde « Aide : … ». Mesuré sur cbe95e2 : « ASSIETTE
     ANNUELLE Aide : Assiette annuelle », relu à chaque cellule. */
  await aller(p, 'carto-uc', 2000);
  const colonnes = [];
  for (const etape of [4, 3]) {
    const ths = await p.evaluate(e => { window.CARTO_UC.slice(0, 2).forEach(u => { window.__cartoState.selected[window.cartoKey(u)] = true; });
      window.cartoGoStep(e);
      return [...document.querySelectorAll('.page.on th')].filter(t => t.querySelector('.aide-titre') && t.getClientRects().length)
        .map((t, i) => { t.id = 'recette-th-' + e + '-' + i; return { sel: '#' + t.id, bouton: t.querySelector('.aide-titre').getAttribute('aria-label') }; }); }, etape);
    for (const t of ths) { const a = await ax(cdp, t.sel), b = await ax(cdp, t.sel + ' .aide-titre');
      colonnes.push({ nom: a ? a.nom : null, attendu: (t.bouton || '').replace(/^Aide : /, ''), bouton: b ? b.nom : null }); }
  }
  const colOk = colonnes.filter(c => c.nom === c.attendu && !/Aide/.test(c.nom) && c.bouton === 'Aide : ' + c.attendu);
  ok('C-4 en-têtes', 'C-4 les 12 colonnes du chiffrage s’appellent par leur libellé, leur bouton garde « Aide : … »',
     colonnes.length === 12 && colOk.length === 12,
     colonnes.length + ' colonne(s) ; ' + colonnes.slice(0, 2).map(c => '« ' + c.nom + ' »').join(' · ')
       + ' … ' + (colonnes.length - colOk.length) + ' nom(s) qui ne sont pas le libellé');

  /* C-3 — LES NEUF CHAMPS SANS NOM, ET LES AIDES. */
  console.log('\n  C-3 — les champs');
  const CHAMPS = [['qualif-assistee', ['qualif-filtre', 'qualif-decideur']], ['historique', ['histo-filter-select']],
                  ['rag', ['rag-filter-select']], ['entreprise', ['ent-ent-name', 'conn-url', 'conn-sec', 'form-date']],
                  ['shadow-ai', ['shadow-risk-filter']]];
  const champs = [];
  for (const [e, ids] of CHAMPS) {
    await aller(p, e);
    for (const id of ids) {
      const a = await ax(cdp, '#' + id);
      const d = await p.evaluate(i => { const el = document.getElementById(i);
        if (!el) return null;
        const aide = (el.getAttribute('aria-describedby') || '').split(/\s+/).map(x => document.getElementById(x)).filter(Boolean)[0];
        return { title: el.getAttribute('title'), aria: el.getAttribute('aria-label'),
                 aide: aide ? { texte: aide.textContent, visible: aide.getClientRects().length > 0 && !aide.hidden } : null }; }, id);
      champs.push({ id, nom: a ? a.nom : null, description: a ? a.description : '', ...(d || {}) });
    }
  }
  const sbRole = await ax(cdp, '#sb-role');
  const sbAide = await p.evaluate(() => { const el = document.getElementById('sb-role');
    const a = el && document.getElementById(el.getAttribute('aria-describedby') || '');
    return { title: el && el.getAttribute('title'), aide: a ? a.getClientRects().length > 0 : false }; });
  const nommes = champs.filter(c => c.aria && c.nom === c.aria && !c.title);
  ok('C-3 champs', 'C-3 les 9 champs sans nom ont un nom égal à leur aria-label, et plus de title',
     nommes.length === 9, champs.map(c => c.id + ' « ' + c.nom + ' »' + (c.title ? ' [title]' : '')).join(' · ').slice(0, 400));
  const aides3 = champs.filter(c => c.aide && c.aide.visible && c.description && c.aide.texte.indexOf(c.description.replace(/\s+/g, ' ').slice(0, 20)) >= 0);
  ok('C-3 aides', 'C-3 là où le title était une aide : visible sous le champ, reliée par aria-describedby (décideur, jeton, parcours)',
     aides3.map(c => c.id).sort().join(',') === 'conn-sec,qualif-decideur' && sbAide.aide && !sbAide.title && !!sbRole && sbRole.description.length > 20,
     aides3.length + ' aide(s) visible(s) : ' + aides3.map(c => c.id).join(', ') + ' ; parcours : ' + (sbAide.aide ? 'aide visible' : 'rien') + (sbAide.title ? ' [title]' : ''));

  /* C-6 — LES CINQ AVERTISSEMENTS CRITIQUES, confirmations REFUSÉES. */
  console.log('\n  C-6 — les avertissements critiques (boîtes de dialogue refusées)');
  const avert = {};
  const essayer = async (ecran, sel, cle, attente) => {
    await aller(p, ecran, attente || 2500);
    const d0 = p.__dialogues.length, x0 = detruites.length;
    const trouve = await p.evaluate(s => { const b = document.querySelector(s); if (!b) return false; b.click(); return true; }, sel);
    await p.waitForTimeout(800);
    avert[cle] = { trouve, dialogue: p.__dialogues.slice(d0).join(' | '), requetes: detruites.length - x0 };
  };
  await essayer('clients', 'button[onclick="billingRunExecute()"]', 'prélèvement');
  await essayer('rgpd-site', 'button[onclick="rgpdPurge(false)"]', 'purge');
  await essayer('historique', 'a[onclick^="histoPurgeAll"]', 'historique', 3000);
  await essayer('registre', '.rs-del', 'suppression');
  /* LE « × » D'UNE ÉVALUATION — l'évaluation posée par la recette, dans le
     stockage de CE navigateur. Mesuré sur cbe95e2 : aucune question, effacée
     d'une touche. Refusée, elle doit rester ; et la question dit LAQUELLE. */
  await essayer('evals', '#evals-rows .suppr-x', 'évaluation');
  /* Ce qui reste se compte DANS LA LISTE PEINTE (lue du stockage à chaque
     repeint) : une seule clé de stockage dans cette recette, celle qui pose
     l'évaluation — la table de mutations la vise. */
  const evalApres = await p.evaluate(() => { const bs = document.querySelectorAll('#evals-rows .suppr-x');
    return { n: bs.length, nom: bs[0] ? bs[0].getAttribute('aria-label') : null }; });
  const ATTENDU = { 'prélèvement': /prélève réellement/, 'purge': /anonymis/, 'historique': /irréversible/i, 'suppression': /définitivement/,
                    'évaluation': /définitivement.*Évaluation de recette.* du 0?1\/09\/2026/ };
  ok('C-6 évaluation', 'C-6 le « × » d’une évaluation DEMANDE, dit laquelle, et refusé ne l’efface pas',
     avert['évaluation'].trouve && ATTENDU['évaluation'].test(avert['évaluation'].dialogue) && evalApres.n === 1
       && /Évaluation de recette/.test(evalApres.nom || ''),
     (avert['évaluation'].dialogue ? '« ' + avert['évaluation'].dialogue.slice(0, 110) + ' »' : 'aucune question')
       + ', ' + evalApres.n + ' évaluation(s) après refus ; nom « ' + (evalApres.nom || '') + ' »');
  for (const k of Object.keys(ATTENDU)) {
    ok(null, 'C-6 ' + k + ' : la boîte de dialogue dit l’avertissement AVANT l’action, et rien n’est parti',
       avert[k].trouve && ATTENDU[k].test(avert[k].dialogue) && avert[k].requetes === 0,
       (avert[k].trouve ? '' : 'contrôle introuvable ; ') + '« ' + avert[k].dialogue.slice(0, 90) + ' », ' + avert[k].requetes + ' requête(s) destructrice(s)');
  }
  /* « Terminer » : le bandeau du parcours, à sa dernière étape. */
  await rythme(80);
  const fin = await p.evaluate(() => {
    const P = (window.GUIDED_PATHS || []).find(x => x.steps && x.steps.length && !x.steps[x.steps.length - 1].go);
    if (!P) return null;
    window.guidedStartStep(P.id, P.steps.length - 1);
    const a = document.querySelector('#guided-banner .gb-actions');
    const t = [...document.querySelectorAll('#guided-banner .gb-actions button')].find(b => /Terminer/.test(b.textContent));
    return { visible: a ? a.innerText.replace(/\s+/g, ' ') : '', title: t ? t.title : '' };
  });
  await p.waitForTimeout(1500);
  const termAx = await ax(cdp, '#guided-banner .gb-next[aria-describedby], #guided-banner .gb-next:not([onclick^="guidedStartStep"])');
  const terminer = !!fin && /rien n.est déclaré conforme/.test(fin.visible);
  ok(null, 'C-6 « Terminer ✓ » : « rien n’est déclaré conforme » est ÉCRIT dans le bandeau, et porté en description',
     terminer && !!termAx && /rien n.est déclaré conforme/.test(termAx.description),
     fin ? 'texte visible « ' + fin.visible.slice(0, 110) + ' » ; description « ' + (termAx ? termAx.description.slice(0, 60) : '') + ' »' : 'aucun parcours');
  const nAvert = Object.keys(ATTENDU).filter(k => avert[k].trouve && ATTENDU[k].test(avert[k].dialogue)).length;
  ok('C-6 avertissements', 'C-6 les 5 avertissements se lisent sans survol (dont les deux « × » : registre et évaluation)', nAvert === 5 && terminer,
     nAvert + ' confirmation(s), « Terminer » : ' + (terminer ? 'texte visible' : 'title seulement'));
  await p.evaluate(() => { if (typeof window.guidedEndBanner === 'function') window.guidedEndBanner(); });

  /* C-7 — LES « × » CLIQUABLES QUI N'ÉTAIENT PAS DES BOUTONS. */
  console.log('\n  C-7 — les « × » de suppression');
  const croix = async (ecran) => { await aller(p, ecran, 2500); return p.evaluate(() => {
    const vis = e => e.getClientRects().length > 0;
    const faux = [...document.querySelectorAll('.page.on div[onclick], .page.on span[onclick]')].filter(e => vis(e) && /^\s*[×✕]/.test(e.textContent));
    const vrais = [...document.querySelectorAll('.page.on button')].filter(e => vis(e) && /^\s*[×✕]\s*$/.test(e.textContent) && !e.classList.contains('mat-modal-close'));
    return { faux: faux.map(e => e.tagName.toLowerCase()), vrais: vrais.length,
             nommes: vrais.filter(b => /^(Supprimer|Retirer) .{3,}/.test(b.getAttribute('aria-label') || '')).length };
  }); };
  const c7 = { registre: await croix('registre') };
  /* Entrée sur le premier « × » du registre : la confirmation doit venir. */
  const d7 = p.__dialogues.length;
  const f7 = await p.evaluate(() => { const b = document.querySelector('.page.on .rs-del'); if (!b) return false; b.focus(); return document.activeElement === b; });
  if (f7) { await p.keyboard.press('Enter'); await p.waitForTimeout(600); }
  const entreeReg = p.__dialogues.length > d7;
  c7.comp = await croix('comp');
  const avant7 = await p.evaluate(() => document.querySelectorAll('#cj-tags .cj-tag').length);
  const g7 = await p.evaluate(() => { const b = document.querySelector('#cj-tags .cj-tag-rm'); if (!b) return false; b.focus(); return document.activeElement === b; });
  if (g7) { await p.keyboard.press('Enter'); await p.waitForTimeout(600); }
  const apres7 = await p.evaluate(() => document.querySelectorAll('#cj-tags .cj-tag').length);
  /* C-7 FOCUS — OÙ EST LE FOCUS APRÈS LE RETRAIT ? La liste est repeinte :
     mesuré sur cbe95e2, il tombait sur <body>. */
  const focus7 = await p.evaluate(() => { const a = document.activeElement;
    return { tag: a ? a.tagName : null, id: a ? a.id : '', classe: a ? String(a.className) : '', nom: a ? a.getAttribute('aria-label') || a.textContent.trim().slice(0, 30) : '' }; });
  ok('C-7 focus', 'C-7 après un retrait au clavier, le focus reste dans la liste (« × » suivant, ou « Ajouter un pays »)',
     g7 && apres7 === avant7 - 1 && (/\bcj-tag-rm\b/.test(focus7.classe) || focus7.id === 'cj-add-btn'),
     'comparateur : focus sur ' + focus7.tag + (focus7.id ? '#' + focus7.id : '') + (focus7.nom ? ' « ' + focus7.nom + ' »' : ''));
  c7.evals = await croix('evals');
  const faux7 = c7.registre.faux.length + c7.comp.faux.length + c7.evals.faux.length;
  const vrais7 = c7.registre.vrais + c7.comp.vrais + c7.evals.vrais;
  const nommes7 = c7.registre.nommes + c7.comp.nommes + c7.evals.nommes;
  ok('C-7 cliquables', 'C-7 aucun <div>/<span> cliquable « × » ; des <button> nommés « Supprimer … » / « Retirer … »',
     faux7 === 0 && vrais7 >= 3 && nommes7 === vrais7,
     'registre ' + JSON.stringify(c7.registre) + ' · comparateur ' + JSON.stringify(c7.comp) + ' · évaluations ' + JSON.stringify(c7.evals));
  ok('C-7 Entrée', 'C-7 Entrée active le « × » : la confirmation du registre vient, le pays est retiré du comparateur',
     f7 && entreeReg && g7 && apres7 === avant7 - 1,
     (f7 ? 'registre : ' + (entreeReg ? 'confirmation' : 'rien') : 'registre : pas de focus') + ' ; '
       + (g7 ? 'comparateur : ' + avant7 + ' → ' + apres7 + ' pays' : 'comparateur : pas de focus'));
  await ctx.close();
  }

  // ══ B. TACTILE — le bouton d'aide au doigt ═════════════════════════════
  if (joue('B')) {
  console.log('\n══ B. Tactile (Pixel 7) ══');
  ({ ctx, p, cdp } = await nouveau(nav, { ...devices['Pixel 7'], hasTouch: true, isMobile: true }));
  ok(null, 'la page répond', (await sentinel(p, 'audit-ia-act')) === 200);
  const b = await p.$('#p-audit-ia-act .audit-kpi .aide-titre');
  let doigt = { present: !!b };
  if (b) {
    await b.scrollIntoViewIfNeeded(); await p.waitForTimeout(300);
    const appui = async () => {
      const c = await p.evaluate(() => { const e = document.querySelector('#p-audit-ia-act .audit-kpi .aide-titre');
        const r = e.getBoundingClientRect(), vv = window.visualViewport || { offsetLeft: 0, offsetTop: 0, scale: 1 };
        return { x: Math.round((r.left + r.width / 2 - vv.offsetLeft) * (vv.scale || 1)), y: Math.round((r.top + r.height / 2 - vv.offsetTop) * (vv.scale || 1)) }; });
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [c] });
      await p.waitForTimeout(60);
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
      await p.waitForTimeout(450);
      /* aria-expanded AUSSI : la spécification le demande au doigt comme à
         la souris ; la première version de cette recette ne le lisait pas. */
      return p.evaluate(B => ({ ...(new Function('return (' + B + ')()'))(),
        exp: document.querySelector('#p-audit-ia-act .audit-kpi .aide-titre').getAttribute('aria-expanded') }), BULLE.toString());
    };
    const texte = await p.evaluate(() => { const e = document.querySelector('#p-audit-ia-act .audit-kpi .aide-titre');
      return document.getElementById(e.getAttribute('aria-describedby')).textContent; });
    const v1 = await appui(), v2 = await appui();
    doigt = { ouvre: v1.visible && v1.texte === texte && v1.exp === 'true', ferme: !v2.visible && v2.exp === 'false', exp: [v1.exp, v2.exp] };
  } else {
    /* Le code d'avant : l'appui sur le bloc lui-même (le title). */
    doigt.bloc = 'pas de bouton d’aide';
  }
  ok('C-4 bulle doigt', 'C-4 au doigt, un appui sur « ? » ouvre la bulle avec l’explication et aria-expanded="true", un second la ferme ("false")',
     doigt.ouvre && doigt.ferme, JSON.stringify(doigt));
  await ctx.close();
  }

  // ══ C. ACCUEIL — doubles bulles, noms, bouton d'aide ═══════════════════
  if (joue('C')) {
  console.log('\n══ C. Accueil (poste) ══');
  ({ ctx, p, cdp } = await nouveau(nav, { viewport: { width: 1280, height: 900 } }));
  await rythme(15);
  await p.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'domcontentloaded' });
  const r = await p.goto(BASE + '/', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3500);
  await p.evaluate(() => { const b = document.getElementById('ck-banner'); if (b) b.classList.remove('show'); });
  ok(null, 'l’accueil répond', r && r.status() === 200);
  const doubles = await p.evaluate(() => [...document.querySelectorAll('[title][data-tooltip]')].map(e => e.id || e.className));
  ok('C-2 doubles', 'C-2 aucun élément ne porte À LA FOIS title et data-tooltip (deux bulles à la souris)',
     doubles.length === 0, doubles.length + (doubles.length ? ' : ' + doubles.join(', ') : ''));
  const DIX = ['nav-up', 'nav-down', 'cp-nav-down', 'btt', 'ck-btn', 'acc-reading-btn', 'acc-dyslexia-btn', 'acc-contrast-btn', 'vbtn', 'cp-ft-top'];
  const dix = await AXS(cdp, DIX.map(i => '#' + i));
  /* UN NŒUD QUE LE NAVIGATEUR IGNORE N'A PAS DE NOM À MESURER. Mesuré au
     premier passage : « Retour en haut » (#btt) est masqué pour de bon par la
     feuille de l'accueil (`#btt{display:none!important}`, remplacé par la
     flèche de la colonne droite) — son nom relevé était vide. Il est dit,
     et pas compté comme sans nom. */
  const ignores = DIX.filter((id, i) => dix[i] && dix[i].ignore);
  if (ignores.length) dire('ignoré(s) par l’arbre d’accessibilité (jamais affiché) : ' + ignores.join(', '));
  /* LE NOM EST L'`aria-label`, EXACTEMENT. Mesuré sur 32fb668 (revue du
     lot 3) : « 📰 » s'appelait déjà « 📰 Actualités IA en direct — 9 sources
     RSS » — Chromium recopiait dans le nom la bulle data-tooltip, que la
     feuille ajoute en contenu. « Trois lettres » passait donc SANS aucun
     `aria-label` : une règle qui passe pour une raison sans rapport. */
  const als = await p.evaluate(ids => ids.map(i => { const e = document.getElementById(i); return e ? e.getAttribute('aria-label') : null; }), DIX);
  const sansNom = DIX.filter((id, i) => !dix[i] || (!dix[i].ignore && !(als[i] && /[A-Za-zÀ-ÿ]{3,}/.test(als[i]) && dix[i].nom === als[i])));
  const tooltips = await p.evaluate(ids => ids.filter(i => { const e = document.getElementById(i); return e && e.hasAttribute('data-tooltip'); }).length, DIX);
  ok('C-2 noms', 'C-2 les dix gardent data-tooltip ; le nom calculé de chacun EST son aria-label, qui dit l’action',
     sansNom.length === 0 && tooltips === 10 && ignores.length <= 1 && ignores.every(i => i === 'btt'),
     'data-tooltip ' + tooltips + '/10 ; ' + DIX.map((id, i) => id + ' « ' + (dix[i] ? dix[i].nom : '?') + ' »').filter((x, i) => ['btt', 'vbtn'].indexOf(DIX[i]) >= 0 || sansNom.indexOf(DIX[i]) >= 0).join(' · '));
  /* « Retour en haut » (#btt), COMPTÉ À PART : jamais affiché sur
     l'accueil, l'arbre d'accessibilité l'ignore ; son nom se lit donc dans
     l'attribut — pour le jour où la feuille le montrerait. */
  const btt = dix[DIX.indexOf('btt')] || {};
  const bttAl = als[DIX.indexOf('btt')];
  ok('C-2 btt', 'C-2 #btt (jamais affiché) : ignoré par l’arbre, et un aria-label qui dit l’action',
     !!btt.ignore && !!bttAl && /[A-Za-zÀ-ÿ]{3,}/.test(bttAl),
     'aria-label « ' + (bttAl || '') + ' », ' + (btt.ignore ? 'ignoré par l’arbre (jamais affiché)' : 'affiché, nom « ' + btt.nom + ' »'));
  const cles = await p.evaluate(() => ['nav-haut', 'nav-up', 'nav-down', 'nav-bas'].map(i => (document.getElementById(i) || {}).getAttribute ? document.getElementById(i).getAttribute('aria-keyshortcuts') : null));
  ok(null, 'C-2 les flèches de section portent leur raccourci (aria-keyshortcuts)',
     cles.join('|') === 'Alt+Home|Alt+ArrowUp|Alt+ArrowDown|Alt+End', cles.join(', '));
  const GLY = ['.lbtn[data-lang="fr"]', '.lbtn[data-lang="en"]', '.lbtn[data-lang="de"]', '.ft-social[title="LinkedIn"]',
               '.ft-social[title="Email"]', '.ft-social-aies', '#xbtn', '#xcls', '#xsnd', '#vbox .cpx-expand-btn', '#cpcPanel .cpc-close'];
  const gly = [];
  for (const s of GLY) gly.push(await p.evaluate(sel => { const e = document.querySelector(sel);
    return e ? { sel, al: e.getAttribute('aria-label') || '', vis: (e.textContent || '').replace(/\s+/g, '') } : { sel, al: null }; }, s));
  const glyOk = gly.filter(g => g.al && /[A-Za-zÀ-ÿ]{3,}/.test(g.al)
    && (!/[A-Za-z]/.test(g.vis) || g.al.toLowerCase().indexOf(g.vis.toLowerCase()) >= 0));
  ok('C-2 glyphes accueil', 'C-2 (§3.2) les glyphes de l’accueil ont un nom, et le texte visible est dans le nom',
     glyOk.length === GLY.length, (GLY.length - glyOk.length) + ' sans nom ou réduits au glyphe'
       + (GLY.length - glyOk.length ? ' : ' + gly.filter(g => glyOk.indexOf(g) < 0).map(g => g.sel).join(', ') : ''));
  /* LE GLOBE D'I-AES.COM. Oublié au premier passage : exclu de la règle au
     motif que bascule.js le renommerait — faux, bascule.js ne nomme que les
     liens SANS texte, et « 🌐 » en est un. Son nom est « i-aes.com » ; quand
     le site ne répond pas, le nouvel état passe par sa DESCRIPTION (le
     `title` que bascule.js réécrit), qu'on relève aussi. */
  const globe = await p.evaluate(() => { const a = [...document.querySelectorAll('a.ft-social')].find(e => e.textContent.trim() === '🌐');
    if (!a) return null; a.id = a.id || 'recette-globe'; return { id: a.id, bascule: a.getAttribute('data-bascule') }; });
  const axGlobe = globe ? await ax(cdp, '#' + globe.id) : null;
  ok('C-2 globe', 'C-2 le lien 🌐 s’appelle « i-aes.com »',
     !!axGlobe && axGlobe.nom === 'i-aes.com' && (!globe.bascule || /ne répond pas/.test(axGlobe.description)),
     axGlobe ? '« ' + axGlobe.nom + ' »' + (globe.bascule ? ' ; site basculé (' + globe.bascule + '), description « ' + axGlobe.description.slice(0, 50) + '… »' : '') : 'introuvable');
  /* LE BOUTON D'AIDE DE L'ASSISTANT : ouvrir le panneau n'envoie rien. */
  await p.evaluate(() => { if (typeof window.cpcToggle === 'function') window.cpcToggle(); });
  await p.waitForTimeout(600);
  const acc = await p.evaluate(() => { const s = document.querySelector('#cpcPanel .cpc-sub'); const b = s && s.querySelector('.aide-titre');
    return { title: s ? s.getAttribute('title') : null, bouton: !!b }; });
  let accB = { ouvre: false };
  if (acc.bouton) {
    await p.click('#cpcPanel .cpc-sub .aide-titre'); await p.waitForTimeout(300);
    const v = await p.evaluate(BULLE);
    const t = await p.evaluate(() => document.getElementById('aide-cpc-methode').textContent);
    accB = { ouvre: v.visible && v.texte === t };
  }
  ok('C-4 accueil', 'C-4 (accueil) .cpc-sub : plus de title, un bouton d’aide qui ouvre la bulle au clic',
     acc.title === null && acc.bouton && accB.ouvre,
     (acc.title ? 'title sur .cpc-sub' : 'pas de title') + ', ' + (acc.bouton ? 'bouton, bulle ' + (accB.ouvre ? 'ouverte' : 'fermée') : '0 bouton'));
  await ctx.close();
  }

  // ══ D. LE GARDE-FOU D'INVENTAIRE ═══════════════════════════════════════
  if (joue('D')) {
  console.log('\n══ D. Garde-fou : chaque élément inerte à title informatif est couvert ══');
  const admis = JSON.parse(fs.readFileSync(path.join(DEPOT, 'tests', 'titres_generiques_admis.json'), 'utf8')).admis || [];
  const couvre = (x) => x.legende || admis.some(a => a.ecran === x.ecran && x.classes.indexOf(a.classe) >= 0);
  ({ ctx, p, cdp } = await nouveau(nav, { viewport: { width: 1280, height: 900 } }));
  await rythme(15);
  await p.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'domcontentloaded' });
  await p.goto(BASE + '/', { waitUntil: 'domcontentloaded' }); await p.waitForTimeout(3000);
  const vus = new Map();
  for (const x of await p.evaluate(RELEVE)) vus.set('accueil|' + x.inv, { ...x, ecran: 'accueil' });
  ok(null, 'la page Sentinel répond', (await sentinel(p, '')) === 200);
  const ecrans = await p.evaluate(() => [...document.querySelectorAll('.page[id^="p-"]')].map(e => e.id.slice(2)));
  for (const e of ecrans) {
    await rythme(80);
    await p.evaluate(id => window.go(id), e).catch(() => {});
    await p.waitForTimeout(1300);
    for (const x of await p.evaluate(RELEVE)) {
      const k = 's|' + x.inv;
      /* Un élément vu couvert une fois l'est : son écran portait sa légende. */
      if (!vus.has(k) || (x.legende && !vus.get(k).legende)) vus.set(k, x);
    }
  }
  const tous = [...vus.values()];
  const nus = tous.filter(x => !couvre(x));
  const parClasse = {};
  tous.forEach(x => { const c = x.ecran + ' .' + (x.classes[0] || '(sans classe)'); parClasse[c] = (parClasse[c] || 0) + 1; });
  dire(ecrans.length + ' écrans parcourus ; ' + tous.length + ' éléments inertes à title informatif : ' + JSON.stringify(parClasse));
  const couverts = tous.filter(x => x.legende);
  const pire = couverts.reduce((m, x) => (m && m.part <= x.part ? m : x), null);
  dire('part des mots du title que dit sa légende : la plus faible ' + (pire ? pire.part + ' (' + pire.ecran + ' .' + pire.classes[0] + ')' : '—'));
  const nusClasse = {};
  nus.forEach(x => { const c = x.ecran + ' .' + (x.classes.join('.') || '(sans classe)') + ' « ' + x.title.slice(0, 40) + ' »'; nusClasse[c] = (nusClasse[c] || 0) + 1; });
  ok('C-5 inventaire', 'C-5 garde-fou : chacun est couvert par une légende de son écran, ou nommé dans tests/titres_generiques_admis.json',
     tous.length > 0 && nus.length === 0,
     nus.length + ' générique(s) non couvert(s) sur ' + tous.length + (nus.length ? ' : ' + JSON.stringify(nusClasse).slice(0, 600) : ''));
  const inutiles = admis.filter(a => !tous.some(x => x.ecran === a.ecran && x.classes.indexOf(a.classe) >= 0));
  ok(null, 'C-5 la liste des admis ne nomme rien qui n’existe plus', inutiles.length === 0,
     admis.length + ' entrée(s)' + (inutiles.length ? ', dont périmée(s) : ' + inutiles.map(a => a.ecran + ' .' + a.classe).join(', ') : ''));
  await ctx.close();
  }
  await nav.close();

  ok(null, 'aucune requête destructrice n’est partie', detruites.length === 0,
     detruites.join(' ; ') + (simulations.length ? ' (' + simulations.length + ' simulation(s) de purge lancée(s) par l’écran RGPD, abandonnée(s) aussi)' : ''));
  ok(null, 'aucune erreur JavaScript dans les pages', erreurs.length === 0, erreurs.slice(0, 2).join(' | '));
  ok(null, 'aucun refus du limiteur (sinon la recette a mesuré des 429)', refus.length === 0, refus.slice(0, 2).join(' '));

  /* LES DEUX COLONNES. */
  console.log('\n══ Avant (32fb668) / après ══');
  for (const l of lignes) {
    console.log((l.ok ? '  OK ' : '  KO ') + l.cle.padEnd(22) + ' | avant : ' + String(l.avant).slice(0, 70).padEnd(70) + ' | après : ' + l.apres.slice(0, 120));
  }
  if (process.env.SORTIE) fs.writeFileSync(process.env.SORTIE, JSON.stringify(MESURES, null, 1));
  console.log('\n' + (n - ko) + '/' + n + ' contrôles verts' + (ko ? ' — ' + ko + ' en échec' : ''));
  process.exit(ko ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
