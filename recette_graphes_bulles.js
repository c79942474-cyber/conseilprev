/* RECETTE — LES BULLES DES GRAPHIQUES SE LISENT AU DOIGT, AU CLAVIER, ET SE
 * FERMENT À ÉCHAP (lot 4 : le pilote `grapheBulle` de sentinel.page.js)
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LE DÉFAUT. Cinq graphiques de Sentinel — les barres géopolitiques, le radar
 * de maturité, le radar de risque, la courbe de tarification, le schéma de
 * l'écosystème — n'écoutaient que la SOURIS. Au doigt, le navigateur émet
 * des événements de souris « de compatibilité » juste après l'appui : la
 * bulle s'ouvrait et se refermait dans la foulée. Au clavier, aucune cible
 * ne prenait le focus — ou onze à la file, sans rien montrer. Échap ne
 * fermait rien.
 *
 * LES CONTRÔLES G-1 À G-12 de la spécification (§6, lot 4), et ce que le lot
 * demande en plus : UNE BULLE À LA FOIS entre les trois systèmes
 * (/infobulles.js, /bulle-titre.js, grapheBulle), l'ORDRE des écouteurs
 * d'Échap mesuré dans la page, le survol GARDÉ au poste fixe, et AUCUN
 * `title` sur une cible de graphique (sinon /bulle-titre.js, ou le
 * navigateur, ouvrirait une seconde bulle).
 *
 * DEUX CONTEXTES :
 *   · « tactile » : Pixel 7 — gestes envoyés par le protocole de débogage
 *     (`Input.dispatchTouchEvent`), en coordonnées de la fenêtre VISUELLE
 *     (voir `centre`) : c'est le navigateur qui décide qu'un geste défile ;
 *   · « poste »   : 1280 × 900, souris, clavier, et un stylet
 *     (`Input.dispatchMouseEvent`, `pointerType: 'pen'`).
 *
 * DEUX COLONNES. Chaque mesure est imprimée avec sa valeur relevée sur le
 * code d'avant (commit be93b64, par CETTE recette, serveur neuf : AVANT_FIGE)
 * et sa valeur maintenant. `SORTIE=fichier.json` écrit les mesures du
 * passage ; `AVANT=fichier.json` remplace la colonne d'avant.
 *
 * CHAQUE « RIEN » A SON TÉMOIN. « Aucune bulle ouverte » passerait aussi sur
 * un pilote éteint : il ne compte que si, dans la même fenêtre, la même
 * cible S'OUVRE à l'appui. C'est le défaut que ce dépôt traque — une règle
 * qui passe pour une raison sans rapport.
 *
 * LE LIMITEUR : 120 requêtes par minute et par processus, une centaine par
 * chargement de Sentinel. Chaque chargement attend une fenêtre glissante
 * presque vide. Un serveur NEUF par passage.
 */
const { chromium, devices } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
const SECTIONS = (process.env.SECTIONS || 'A,B').split(',');
const joue = (s) => SECTIONS.indexOf(s) >= 0;
const pause = (ms) => new Promise(r => setTimeout(r, ms));

/* LA COLONNE « AVANT » : relevée par cette recette sur le commit be93b64,
   serveur neuf, le 24 septembre 2026 : 8 contrôles verts sur 44. Les huit
   sont légitimes — la page répond (deux contextes), le contexte est
   tactile, un balayage n'ouvrait déjà rien sur l'histogramme, aucun title
   sur les graphiques, le stylet ouvrait déjà la barre (par les événements
   de souris de compatibilité), ni erreur JavaScript ni refus du limiteur.
   Une valeur absente se lit « — ». */
const AVANT_FIGE = {
  'G-1 points': '0/8 ; défilement 0 à +516 px ; ouvertes à 600 ms : 0/8',
  'G-1 haut': 'fermée (block, opacité 0) ; bulle 170,-93,304,41 / point 246,64,268,85 ; défilement 0',
  'G-2 lecture': '100 ms : fermée, 500 ms : fermée (ouverte puis refermée en 16 ms)',
  'G-2 second appui': 'fermée (block, opacité 0)',
  'G-4 ligne doigt': 'point éteint, bulle fermée, défilement 0',
  'préséance i': '« i » ouvert, graphique fermé, 1 ouverture(s) de la bulle du radar pendant l’appui',
  'une à la fois infobulles': 'point puis « i » : point FERMÉ / « i » fermé ; puis « i » ouvert / point fermé',
  'une à la fois bulle-titre': 'title seul ouvert ; point : FERMÉ, title fermé ; appui long : title ouvert, point fermé',
  'risque point': '100 ms fermée, 500 ms fermée (block, opacité 0), 2e appui fermée',
  'risque ligne': 'ligne éteinte, bulle fermée, défilement 0',
  'G-5 cibles': '24 circle, la plus étroite 8.8 × 8.8 px, 0 px au plus près entre centres, 0 arrêt(s)',
  'G-6 tarification': 'défilement 185 px, 0 ouverture(s) ; témoin : fermée (none, opacité 1)',
  'G-5 bulle doigt': '1 série(s) ; fermée (none, opacité 1)',
  'G-6 géo': 'défilement 185 px, 0 ouverture(s) ; témoin : ouverte « Haut - 1 juridictionsTensions geopolitiques  » HORS fenêtre visuelle 234,732,445,783',
  'G-8 défilement': 'page -200 px, barre DÉTRUITE par l’appui, bulle 0 px (top 732 → 732)',
  'eco doigt': '100 ms fermée, 500 ms fermée (none, opacité 1), ailleurs fermée, annonce « Lien prioritaire (établi) : classer un c »',
  'échap ordre': 'infobulles.js → bulle-titre.js',
  'survol poste': '1/5 (mat ok, risque recouvre sa cible, tarif recouvre sa cible, geo recouvre sa cible, eco recouvre sa cible)',
  'titres': '0 sur 5 graphiques (témoin : 1 title relevé(s) sur un bouton de secteur)',
  'une à la fois poste': 'survol : ouverte ; Tab + 250 ms : graphique ouvert, title fermé ; + 700 ms : title ouvert, graphique ENCORE OUVERT',
  'G-3 maturité': 'display block, opacité 0, aria-hidden null, ignorée false',
  'G-3 toutes': 'geo-tooltip=null mat-radar-tooltip=null radar-tooltip=null pricing-chart-tooltip=null carto-eco-tip=null',
  'G-4 radars': 'zones à tabindex 0 + 0 ; maturité — «  » ; risque — «  »',
  'G-4 Tab i': 'focus sur le « i », point éteint, bulle fermée, défilement 0',
  'échap une chose': 'avant : « i » ouvert, graphique ouvert ; 1re : « i » fermé, graphique OUVERT ; 2e : « i » fermé',
  'G-5 clavier': '0 arrêt(s) ; Tab → SPAN (pas de bulle) ; → mois null, bulle HORS de la bande ; Fin → null, Début → null',
  'G-5 nom et tableau': 'nom «  » ; tableau 0 × 0 ()',
  'G-12 contour': 'aucune bande focalisée au clavier',
  'G-7 clic': 'élément DÉTRUIT, 11 mutation(s) du graphique, focus sur BODY.',
  'G-7 noms': 'generic «  » · generic «  » · generic «  » · generic «  » · generic «  »',
  'G-7 puces': 'SPAN SPAN SPAN SPAN SPAN SPAN SPAN SPAN ; Entrée sur « Critique » : all=null critical=null high=null moderate=null ; sur « Tous » : all=null critical=null high=null moderate=null',
  'G-11 stylet': 'ouverte « Modere - 10 juridictionsRegulation sectoriel » (recouvre la barre)',
  'clavier géo': '0 arrêt(s) ; Tab → hors du graphique, pas de bulle ; Début → hors du graphique (pas de bulle) ; → hors du graphique (pas de bulle) ; Échap : bulle fermée, focus sur hors du graphique ; → hors du graphique (pas de bulle) ; Tab : sorti, bulle fermée',
  'voisines géo': '5/5 ouvertes, recouvrements : 1→ELLE-MÊME 10 % · 1→2 27 % · 1→3 12 % · 2→ELLE-MÊME 10 % · 2→3 27 % · 2→4 10 % · 3→ELLE-MÊME 13 % · 3→4 35 % · 3→5 17 % · 4→ELLE-MÊME 10 % · 4→5 27 % · 5→ELLE-MÊME 10 %',
  'G-9 schéma': 'svg img, 0/11 img, 0 noms commencent par le texte visible, 11 data-bulle-prete, \\u2019 PRÉSENT, 11 arrêt(s)',
  'clavier écosystème': '11 arrêt(s) ; Tab → cible 1 (l’arrêt), pas de bulle ; Début → cible 1 (pas de bulle) ; → cible 1 (pas de bulle) ; Échap : bulle fermée, focus sur cible 1 ; → cible 1 (pas de bulle) ; Tab : resté, bulle fermée',
  'voisines écosystème': '11/11 ouvertes, 11 faute(s), au plus 23 % d’un voisin (1→ELLE-MÊME 11 % · 1→6 22 % · 1→8 10 % · 2→ELLE-MÊME 10 % · 2→3 23 % · 3→ELLE-MÊME 10 % · 3→4 23 % · 4→ELLE-MÊME 12 % · 5→1 9 % · 5→ELLE-MÊME 9 % · 5→7 4 % · 5→8 9 % · 6→ELLE-MÊME 11 % · 7→ELLE-MÊME 9 % · 7→8 19 % · 8→6 19 % · 8→ELLE-MÊME 9 % · 9→ELLE-MÊME 9 % · 9→10 22 % · 10→ELLE-MÊME 9 % · 10→11 20 % · 11→ELLE-MÊME 10 %)',
  'G-10 survolable': 'survol ouverte ; sur la bulle FERMÉE ; sortie : 150 ms fermée, 500 ms fermée',
  'G-10 Échap': 'avant ouverte, Échap OUVERTE, pointeur resté ROUVERTE, retour ouverte',
};
let AVANT = AVANT_FIGE;
if (process.env.AVANT) { try { AVANT = JSON.parse(fs.readFileSync(process.env.AVANT, 'utf8')); } catch (e) { /* le figé */ } }
const MESURES = {};
let ko = 0, n = 0;
const lignes = [];
/* UNE LIGNE = un contrôle, sa mesure maintenant, sa mesure d'avant. */
function ok(cle, libelle, condition, mesure) {
  n++; if (!condition) ko++;
  const m = mesure === undefined ? '' : String(mesure);
  if (cle) MESURES[cle] = m;
  console.log((condition ? '  OK   ' : '  KO   ') + libelle + (m ? ' — ' + m.slice(0, 260) : ''));
  if (cle) lignes.push({ cle, libelle, avant: AVANT[cle] || '—', apres: m, ok: !!condition });
}
const dire = (t) => console.log('  ..   ' + t);

/* LES CIBLES ET LES BULLES, telles qu'elles s'écrivent AVANT et APRÈS le lot :
   le même relevé tourne sur les deux codes. */
const G = {
  geo:    { ecran: 'geo',      cible: '#geo-chart .geo-bar-col', bulle: '#geo-tooltip' },
  mat:    { ecran: 'maturite', cible: '.mat-radar-hitzone', bulle: '#mat-radar-tooltip', ligne: '#p-maturite .mat-pillar-row' },
  risque: { ecran: 'radar',    cible: '.radar-hitzone', bulle: '#radar-tooltip', ligne: '#radar-scores .reg-item' },
  tarif:  { ecran: 'pricing',  cible: '#pricing-chart-svg [data-graphe="tarif"], #pricing-chart-svg .pricing-chart-hover-zone', bulle: '#pricing-chart-tooltip' },
  eco:    { ecran: 'carto-uc', cible: '.carto-eco-svg .eco-node', bulle: '#carto-eco-tip' },
};
const BULLES = Object.keys(G).map(k => G[k].bulle.slice(1));

const FURTIF = (ctx) => ctx.addInitScript(() => {
  Object.defineProperty(navigator, 'webdriver', { get: () => false });
  Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
  Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
});

/* LES COMPTEURS, posés AVANT la page :
   · l'ORDRE des écouteurs `keydown` inscrits sur `window` en capture, avec le
     script qui les inscrit (lu dans la pile d'appel) — c'est l'ordre dans
     lequel Échap les traverse ;
   · chaque passage d'une bulle de graphique de cachée à ouverte, horodaté —
     une bulle « ouverte puis refermée en 16 ms » se voit ici, pas à l'œil.
     Ouverte veut dire DÉCLARÉE ouverte : `display` différent de `none`, et,
     pour les radars, la classe `on` (l'ancienne bulle s'allumait par une
     transition d'opacité, que le relevé ne doit pas manquer). */
const COMPTEURS = (ctx, ids) => ctx.addInitScript((ids) => {
  window.__echap = [];
  const inscrire = EventTarget.prototype.addEventListener;
  EventTarget.prototype.addEventListener = function (type, fn, opt) {
    if (this === window && type === 'keydown' && (opt === true || (opt && opt.capture))) {
      const pile = String(new Error().stack || '');
      const m = pile.match(/\/[\w.-]+\.js/g) || [];
      window.__echap.push(m.length ? m[0].slice(1) : '(script en ligne)');
    }
    return inscrire.call(this, type, fn, opt);
  };
  window.__bulles = { vis: {}, trans: {} };
  const declaree = (b) => {
    if (!b.isConnected) return false;
    const cs = getComputedStyle(b);
    if (cs.display === 'none') return false;
    if (b.classList.contains('mat-radar-tooltip')) return b.classList.contains('on');
    return b.getClientRects().length > 0;
  };
  const relever = () => {
    const t = Math.round(performance.now());
    for (const id of ids) {
      const b = document.getElementById(id);
      const v = !!b && declaree(b);
      if (v !== !!window.__bulles.vis[id]) (window.__bulles.trans[id] = window.__bulles.trans[id] || []).push((v ? '+' : '-') + t);
      window.__bulles.vis[id] = v;
    }
  };
  window.__releverBulles = relever;
  new MutationObserver(relever).observe(document, { subtree: true, attributes: true, childList: true,
                                                     attributeFilter: ['style', 'class', 'hidden'] });
}, ids);

/* ── LE LIMITEUR ─────────────────────────────────────────────────────── */
const requetes = [], refus = [], erreurs = [];
async function rythme(seuil) {
  for (;;) {
    const t = Date.now();
    while (requetes.length && t - requetes[0] > 61000) requetes.shift();
    if (requetes.length <= seuil) return;
    await pause(1000);
  }
}
async function nouveau(nav, options) {
  const ctx = await nav.newContext(options);
  await FURTIF(ctx); await COMPTEURS(ctx, BULLES);
  const p = await ctx.newPage();
  p.on('request', () => requetes.push(Date.now()));
  p.on('pageerror', e => erreurs.push(String(e).slice(0, 160)));
  p.on('response', r => { if (r.status() === 429) refus.push(r.url()); });
  /* AUCUNE ACTION RÉELLE : une boîte de dialogue est toujours refusée. */
  p.on('dialog', d => d.dismiss().catch(() => {}));
  const cdp = await ctx.newCDPSession(p);
  return { ctx, p, cdp };
}
async function sentinel(p, ecran) {
  await rythme(12);
  await p.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'domcontentloaded' });
  const rep = await p.goto(BASE + '/sentinel?goto=' + ecran, { waitUntil: 'domcontentloaded' });
  await p.waitForFunction(() => !!document.getElementById('css-bulle-ouverte'), null, { timeout: 15000 }).catch(() => {});
  await p.waitForTimeout(3500);
  await p.evaluate(() => { const b = document.getElementById('ck-banner'); if (b) b.classList.remove('show'); });
  return rep && rep.status();
}
async function aller(p, ecran, ms) {
  await rythme(85);
  await p.evaluate(e => window.go(e), ecran);
  await p.waitForTimeout(ms || 1800);
  await p.evaluate(() => { const b = document.getElementById('ck-banner'); if (b) b.classList.remove('show'); });
}
/* Refermer ce qui est ouvert, par le chemin que le code d'alors connaît. */
const REPOS = () => {
  if (window.grapheBulle) window.grapheBulle.fermer();
  if (window.matRadarUnhighlight) window.matRadarUnhighlight();
  if (window.radarUnhighlight) window.radarUnhighlight();
  if (window.pricingHideTooltip) window.pricingHideTooltip();
  if (window.ecoTipHide) window.ecoTipHide();
  const g = document.getElementById('geo-tooltip'); if (g) g.style.display = 'none';
  if (window.infobulles) window.infobulles.fermer();
  if (window.bulleTitre) window.bulleTitre.fermer();
  if (document.activeElement && document.activeElement !== document.body) document.activeElement.blur();
};

/* L'ÉTAT D'UNE BULLE : vue (display, visibilité, opacité, rectangle), dans la
   fenêtre visuelle à 8 px près, sous la barre du haut, au-dessus de ce qui
   l'entoure (le point de son centre est à elle), sa cible. */
const VUE = ([sel, marque]) => {
  const b = document.querySelector(sel);
  const vv = window.visualViewport || { offsetLeft: 0, offsetTop: 0, width: innerWidth, height: innerHeight, scale: 1 };
  if (!b) return { existe: false, visible: false, texte: '' };
  const cs = getComputedStyle(b), r = b.getBoundingClientRect();
  const visible = cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity) > 0.5 && r.width > 0 && r.height > 0;
  const barre = document.querySelector('header.topbar');
  const bas = barre ? barre.getBoundingClientRect().bottom : 0;
  const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
  /* AU-DESSUS DE CE QUI L'ENTOURE : le point de son centre est à elle. Une
     bulle en `pointer-events:none` (l'ancienne) serait traversée par ce
     relevé : on la rend un instant « touchable » pour le faire. */
  const pe = b.style.pointerEvents;
  b.style.pointerEvents = 'auto';
  const dessus = document.elementFromPoint(cx, cy);
  b.style.pointerEvents = pe;
  const a = marque ? document.querySelector('[data-recette="' + marque + '"]') : null;
  const ra = a ? a.getBoundingClientRect() : null;
  return {
    existe: true, visible, texte: (b.textContent || '').replace(/\s+/g, ' ').trim(),
    display: cs.display, opacite: cs.opacity, ariaHidden: b.getAttribute('aria-hidden'), pe: cs.pointerEvents,
    rect: [r.left, r.top, r.right, r.bottom].map(Math.round),
    dansVV: r.left >= vv.offsetLeft - 8 && r.top >= vv.offsetTop - 8 && r.right <= vv.offsetLeft + vv.width + 8 && r.bottom <= vv.offsetTop + vv.height + 8,
    sousBarre: r.top >= bas - 1, auDessus: !!dessus && (dessus === b || b.contains(dessus)),
    croise: !!ra && r.left < ra.right && ra.left < r.right && r.top < ra.bottom && ra.top < r.bottom,
    cible: ra ? [ra.left, ra.top, ra.right, ra.bottom].map(Math.round) : null,
    centreX: Math.round(cx), scrollY: Math.round(scrollY),
  };
};
const dit = (v) => !v || !v.existe ? 'bulle absente'
  : (v.visible ? 'ouverte « ' + v.texte.slice(0, 44) + ' »' + (v.dansVV ? '' : ' HORS fenêtre visuelle ' + v.rect) : 'fermée (' + v.display + ', opacité ' + v.opacite + ')');

/* MARQUER la i-ème cible d'un sélecteur (les éléments affichés seulement). */
async function marquer(p, sel, i, marque, amener) {
  return p.evaluate(([sel, i, marque, amener]) => {
    const vis = e => { const q = e.getBoundingClientRect(); return q.width > 0 && q.height > 0; };
    const els = [...document.querySelectorAll(sel)].filter(vis);
    const el = els[i < 0 ? els.length + i : i];
    if (!el) return null;
    document.querySelectorAll('[data-recette="' + marque + '"]').forEach(e => e.removeAttribute('data-recette'));
    el.setAttribute('data-recette', marque);
    if (amener) el.scrollIntoView({ block: 'center', inline: 'center', behavior: 'instant' });
    return els.length;
  }, [sel, i, marque, amener !== false]);
}
/* LE CENTRE, EN COORDONNÉES D'ÉCRAN. Le protocole de débogage vise la
   fenêtre VISUELLE ; `getBoundingClientRect` parle de la fenêtre de MISE EN
   PAGE (recette_bulle_titre.js l'a mesuré : sans la conversion, l'appui
   tombe sur la cible voisine). Et l'élément touché doit être le bon. */
async function centre(p, marque, dx, dy) {
  return p.evaluate(([m, dx, dy]) => {
    const e = document.querySelector('[data-recette="' + m + '"]');
    if (!e) return { x: 0, y: 0, touche: false, vise: 'absent' };
    const r = e.getBoundingClientRect();
    const vv = window.visualViewport || { offsetLeft: 0, offsetTop: 0, scale: 1 };
    const cx = r.left + r.width / 2 + (dx || 0), cy = r.top + r.height / 2 + (dy || 0);
    const vise = document.elementFromPoint(cx, cy);
    return { x: Math.round((cx - vv.offsetLeft) * (vv.scale || 1)), y: Math.round((cy - vv.offsetTop) * (vv.scale || 1)),
             touche: !!vise && (vise === e || e.contains(vise)),
             vise: vise ? vise.tagName + '.' + String(vise.className && vise.className.baseVal !== undefined ? vise.className.baseVal : vise.className).slice(0, 30) : null };
  }, [marque, dx || 0, dy || 0]);
}
const TOUCHER = async (cdp, x, y, ms) => {
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] });
  await pause(ms || 60);
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
};
async function appui(p, cdp, marque, attente) {
  const c = await centre(p, marque);
  await TOUCHER(cdp, c.x, c.y);
  await p.waitForTimeout(attente === undefined ? 450 : attente);
  return c;
}
/* LE BALAYAGE : un contact, dix déplacements sur 200 px, un relâcher. */
async function balayer(p, cdp, marque) {
  const c = await centre(p, marque);
  const y0 = await p.evaluate(() => scrollY);
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: c.x, y: c.y }] });
  for (let i = 1; i <= 10; i++) {
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: c.x, y: c.y - 20 * i }] });
    await pause(16);
  }
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  await p.waitForTimeout(700);
  return { defile: Math.round((await p.evaluate(() => scrollY)) - y0), touche: c.touche };
}
/* L'APPUI LONG BRUT (700 ms, sans `contextmenu`) : relevé PENDANT l'appui. */
async function appuiLong(p, cdp, marque, pendant) {
  const c = await centre(p, marque);
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: c.x, y: c.y }] });
  await p.waitForTimeout(620);
  const r = pendant ? await pendant() : null;
  await p.waitForTimeout(80);
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  await p.waitForTimeout(500);
  return r;
}
const transitions = (p, id) => p.evaluate((id) => { window.__releverBulles && window.__releverBulles();
  return (window.__bulles.trans[id] || []).slice(); }, id);
const ouvertures = (tr) => tr.filter(x => x[0] === '+').length;
/* La durée d'ouverture, relue dans les transitions : « +1200 -1212 » → 12 ms. */
const duree = (tr) => { const o = tr.find(x => x[0] === '+'); if (!o) return null;
  const f = tr.slice(tr.indexOf(o) + 1).find(x => x[0] === '-'); return f ? (+f.slice(1)) - (+o.slice(1)) : Infinity; };

/* LE « i » DE LA BULLE D'/infobulles.js DANS UNE LIGNE DU RADAR DE MATURITÉ. */
const BULLE_I = (marque) => {
  const w = document.querySelector('[data-recette="' + marque + '"]');
  if (!w) return { existe: false };
  const t = w.querySelector('.mat-tooltip'), cs = t ? getComputedStyle(t) : null;
  return { existe: true, visible: !!cs && cs.visibility === 'visible' && parseFloat(cs.opacity) > 0.5,
           classe: w.classList.contains('bulle-ouverte'), fermee: w.classList.contains('bulle-fermee') };
};
const BULLE_TITRE = () => { const b = document.getElementById('bulle-titre');
  return !!b && !b.hidden && getComputedStyle(b).display !== 'none'; };

/* LE CONTRASTE DU CONTOUR, SUR LES PIXELS. Deux captures de la même zone —
   la bande AVEC le focus, puis SANS — et, pour chaque pixel qui a changé, le
   rapport de contraste (WCAG) entre ses deux couleurs : c'est le contour
   contre ce qu'il recouvre. Un simple « plus sombre contre plus clair » de
   la zone passerait sur une courbe du graphique qui la traverse, focus ou
   pas — une mesure qui réussirait pour une raison sans rapport. Décodées
   dans une page vierge. */
async function contraste(ctx, pngFocus, pngRepos) {
  const d = await ctx.newPage();
  await d.setContent('<canvas id="c"></canvas>');
  const r = await d.evaluate(async ([a64, b64]) => {
    const lire = async (b) => { const img = new Image(); img.src = 'data:image/png;base64,' + b; await img.decode();
      const c = document.getElementById('c'); c.width = img.width; c.height = img.height;
      const g = c.getContext('2d'); g.clearRect(0, 0, c.width, c.height); g.drawImage(img, 0, 0);
      return { px: g.getImageData(0, 0, img.width, img.height).data, l: img.width, h: img.height }; };
    const A = await lire(a64), B = await lire(b64);
    const lin = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    const L = (p, i) => 0.2126 * lin(p[i]) + 0.7152 * lin(p[i + 1]) + 0.0722 * lin(p[i + 2]);
    const rapports = [];
    for (let i = 0; i < A.px.length; i += 4) {
      const ecart = Math.max(Math.abs(A.px[i] - B.px[i]), Math.abs(A.px[i + 1] - B.px[i + 1]), Math.abs(A.px[i + 2] - B.px[i + 2]));
      if (ecart < 24) continue;
      const a = L(A.px, i), b = L(B.px, i);
      rapports.push((Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05));
    }
    rapports.sort((x, y) => x - y);
    const med = rapports.length ? rapports[Math.floor(rapports.length / 2)] : 0;
    return { changes: rapports.length, mediane: Math.round(med * 100) / 100,
             max: rapports.length ? Math.round(rapports[rapports.length - 1] * 100) / 100 : 0, l: A.l, h: A.h };
  }, [pngFocus.toString('base64'), pngRepos.toString('base64')]);
  await d.close();
  return r;
}

/* AU CLAVIER, UN GRAPHIQUE À ARRÊT UNIQUE : Tab y entre (le focus posé sur
   ce qui le précède, puis une vraie touche) — sur l'arrêt du graphique, là
   où on l'a laissé —, Début va à la première cible, → à la suivante, Échap
   ferme sans déplacer le focus et la bulle ne revient pas tant qu'il reste
   là, → rouvre sur la suivante, Tab en sort. */
async function clavier(p, sel, bulleSel) {
  const pret = await p.evaluate((sel) => {
    const els = [...document.querySelectorAll(sel)];
    if (!els.length) return { pret: false, arrets: 0 };
    els[0].scrollIntoView({ block: 'center', behavior: 'instant' });
    const T = [...document.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select,textarea,[tabindex]')]
      .filter(e => e.tabIndex >= 0 && e.getBoundingClientRect().width > 0);
    const dans = T.filter(e => els.indexOf(e) >= 0);
    const i = dans.length ? T.indexOf(dans[0]) : -1;
    if (i >= 1) T[i - 1].focus();
    return { pret: i >= 1, arrets: dans.length };
  }, sel);
  const etat = () => p.evaluate(([sel, b]) => {
    const els = [...document.querySelectorAll(sel)], g = document.querySelector(b), cs = g && getComputedStyle(g);
    return { i: els.indexOf(document.activeElement), bulle: !!cs && cs.display !== 'none' && parseFloat(cs.opacity) > 0.5,
             texte: g ? g.textContent.replace(/\s+/g, ' ').trim().slice(0, 40) : '' };
  }, [sel, bulleSel]);
  await p.waitForTimeout(400);
  await p.keyboard.press('Tab'); await p.waitForTimeout(400);
  const arret = await p.evaluate((sel) => [...document.querySelectorAll(sel)].findIndex(e => e.getAttribute('tabindex') === '0'), sel);
  const t0 = await etat();
  await p.keyboard.press('Home'); await p.waitForTimeout(400);
  const a = await etat();
  await p.keyboard.press('ArrowRight'); await p.waitForTimeout(400);
  const b = await etat();
  await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  const e1 = await etat();
  await p.waitForTimeout(600);
  const e2 = await etat();
  await p.keyboard.press('ArrowRight'); await p.waitForTimeout(400);
  const c = await etat();
  await p.keyboard.press('Tab'); await p.waitForTimeout(400);
  const d = await etat();
  const bon = pret.pret && pret.arrets === 1 && t0.i >= 0 && t0.i === arret && t0.bulle && a.i === 0 && a.bulle
    && b.i === 1 && b.bulle && b.texte !== a.texte
    && e1.i === 1 && !e1.bulle && !e2.bulle && c.i === 2 && c.bulle && d.i === -1 && !d.bulle;
  const ou = (x) => x.i >= 0 ? 'cible ' + (x.i + 1) : 'hors du graphique';
  const rendu = pret.arrets + ' arrêt(s) ; Tab → ' + ou(t0) + (t0.i >= 0 ? (t0.i === arret ? ' (l’arrêt)' : ' (PAS l’arrêt)') : '')
    + (t0.bulle ? ', bulle' : ', pas de bulle') + ' ; Début → ' + ou(a) + (a.bulle ? ' (bulle)' : ' (pas de bulle)')
    + ' ; → ' + ou(b) + (b.bulle ? ' (bulle « ' + b.texte.slice(0, 22) + ' »)' : ' (pas de bulle)')
    + ' ; Échap : ' + (e1.bulle ? 'bulle RESTÉE' : 'bulle fermée') + ', focus sur ' + ou(e1) + (e2.bulle ? ', ROUVERTE' : '')
    + ' ; → ' + ou(c) + (c.bulle ? ' (bulle)' : ' (pas de bulle)') + ' ; Tab : ' + (d.i === -1 ? 'sorti' : 'resté') + (d.bulle ? ', bulle RESTÉE' : ', bulle fermée');
  return { bon, rendu };
}
/* LA BULLE NE VOLE PAS LE SURVOL DE SES VOISINES : chaque cible survolée à
   son tour, sa bulle comparée aux rectangles des autres — elle n'en couvre
   jamais le CENTRE, et on relève la plus grande part couverte. Le schéma de
   l'écosystème ne permet pas mieux : 54 px entre deux rangées de nœuds au
   poste, pour une bulle de 66 px ; le pilote prend alors le côté qui
   recouvre le moins. */
async function voisines(p, sel, bulleSel) {
  const n = await p.evaluate((sel) => document.querySelectorAll(sel).length, sel);
  let fautes = 0, vues = 0, partMax = 0;
  const detail = [];
  for (let i = 0; i < n; i++) {
    await p.mouse.move(2, 890);
    await p.evaluate(([sel, i]) => { const e = document.querySelectorAll(sel)[i]; e.scrollIntoView({ block: 'center', behavior: 'instant' }); }, [sel, i]);
    await p.waitForTimeout(250);
    const q = await p.evaluate(([sel, i]) => { const r = document.querySelectorAll(sel)[i].getBoundingClientRect();
      return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; }, [sel, i]);
    await p.mouse.move(q.x, q.y, { steps: 3 });
    await p.waitForTimeout(350);
    const m = await p.evaluate(([sel, i, b]) => {
      const g = document.querySelector(b), cs = g && getComputedStyle(g);
      if (!cs || cs.display === 'none' || parseFloat(cs.opacity) <= 0.5) return { vue: false, sur: [] };
      const rb = g.getBoundingClientRect(), sur = [];
      document.querySelectorAll(sel).forEach((e, j) => { const r = e.getBoundingClientRect();
        const dx = Math.min(rb.right, r.right) - Math.max(rb.left, r.left), dy = Math.min(rb.bottom, r.bottom) - Math.max(rb.top, r.top);
        if (dx <= 1 || dy <= 1) return;
        const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
        sur.push({ j, part: Math.round(100 * dx * dy / (r.width * r.height)), centre: cx > rb.left && cx < rb.right && cy > rb.top && cy < rb.bottom, soi: j === i });
      });
      return { vue: true, sur };
    }, [sel, i, bulleSel]);
    if (m.vue) vues++;
    for (const s of m.sur) {
      if (s.soi || s.centre) fautes++;
      else partMax = Math.max(partMax, s.part);
      detail.push((i + 1) + '→' + (s.soi ? 'ELLE-MÊME' : s.j + 1) + ' ' + s.part + ' %' + (s.centre ? ' CENTRE' : ''));
    }
  }
  await p.mouse.move(2, 890);
  return { n, vues, fautes, detail, partMax };
}

(async () => {
  const nav = await chromium.launch();
  let ctx, p, cdp, v, c, tr;

  // ══ A. TACTILE — Pixel 7 ═══════════════════════════════════════════════
  if (joue('A')) {
  console.log('\n══ A. Tactile (Pixel 7) ══');
  ({ ctx, p, cdp } = await nouveau(nav, { ...devices['Pixel 7'], hasTouch: true, isMobile: true }));
  ok(null, 'la page répond', (await sentinel(p, 'maturite')) === 200);
  ok(null, 'le contexte est bien tactile', await p.evaluate(() => matchMedia('(hover:none) and (pointer:coarse)').matches));
  await aller(p, 'maturite');

  /* G-1 — CHACUN DES HUIT POINTS DU RADAR DE MATURITÉ, AU DOIGT. */
  console.log('\n  G-1 — les huit points du radar de maturité, point centré');
  const g1 = [];
  for (let i = 0; i < 8; i++) {
    await p.evaluate(REPOS);
    if (!(await marquer(p, G.mat.cible, i, 'pt'))) { g1.push({ i, absent: true }); continue; }
    await p.waitForTimeout(350);
    const y0 = await p.evaluate(() => scrollY);
    c = await appui(p, cdp, 'pt', 600);
    v = await p.evaluate(VUE, [G.mat.bulle, 'pt']);
    g1.push({ i, touche: c.touche, dy: v.scrollY - Math.round(y0), vue: v.visible, dansVV: v.dansVV, sousBarre: v.sousBarre, croise: v.croise, auDessus: v.auDessus });
  }
  const g1ok = g1.filter(x => x.touche && x.dy === 0 && x.vue && x.dansVV && x.sousBarre && !x.croise && x.auDessus).length;
  const dys = g1.map(x => x.dy);
  ok('G-1 points', 'G-1 les 8 points : scrollY inchangé, bulle ouverte dans la fenêtre visuelle, ni sous la barre ni sur le point',
     g1ok === 8, g1ok + '/8 ; défilement ' + Math.min(...dys) + ' à +' + Math.max(...dys) + ' px ; ouvertes à 600 ms : '
       + g1.filter(x => x.vue).length + '/8' + (g1.some(x => !x.touche) ? ' ; appui à côté : ' + g1.filter(x => !x.touche).map(x => x.i) : ''));
  /* …ET EN HAUT DE L'ÉCRAN, LA BULLE PASSE DESSOUS. Le point le plus haut du
     radar amené juste sous la barre du haut. */
  await p.evaluate(REPOS);
  const haut = await p.evaluate((sel) => {
    const els = [...document.querySelectorAll(sel)].filter(e => e.getBoundingClientRect().width > 0);
    if (!els.length) return null;
    els.sort((a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top);
    document.querySelectorAll('[data-recette="haut"]').forEach(e => e.removeAttribute('data-recette'));
    els[0].setAttribute('data-recette', 'haut');
    const barre = document.querySelector('header.topbar');
    const bas = barre ? barre.getBoundingClientRect().bottom : 0;
    window.scrollBy(0, els[0].getBoundingClientRect().top - bas - 12);
    return true;
  }, G.mat.cible);
  await p.waitForTimeout(400);
  const y1 = await p.evaluate(() => scrollY);
  c = haut ? await appui(p, cdp, 'haut', 600) : { touche: false };
  v = await p.evaluate(VUE, [G.mat.bulle, 'haut']);
  const sousPoint = v.existe && v.cible && v.rect[1] >= v.cible[3] - 1;
  ok('G-1 haut', 'G-1 un point en haut de l’écran : bulle SOUS le point, entière, sous la barre du haut',
     c.touche && v.visible && v.dansVV && v.sousBarre && sousPoint && v.scrollY === Math.round(y1),
     dit(v) + (v.existe && v.cible ? ' ; bulle ' + v.rect + ' / point ' + v.cible : '') + ' ; défilement ' + (v.scrollY - Math.round(y1)));

  /* G-2 — LA BULLE RESTE OUVERTE ; LE SECOND APPUI LA FERME. */
  console.log('\n  G-2 — un point du radar : lue à 100 ms, puis à 500 ms');
  await p.evaluate(REPOS);
  await marquer(p, G.mat.cible, 2, 'pt2');
  await p.waitForTimeout(400);
  const t0 = (await transitions(p, 'mat-radar-tooltip')).length;
  c = await appui(p, cdp, 'pt2', 100);
  const a100 = await p.evaluate(VUE, [G.mat.bulle, 'pt2']);
  await p.waitForTimeout(400);
  const a500 = await p.evaluate(VUE, [G.mat.bulle, 'pt2']);
  tr = (await transitions(p, 'mat-radar-tooltip')).slice(t0);
  await appui(p, cdp, 'pt2', 450);
  const second = await p.evaluate(VUE, [G.mat.bulle, 'pt2']);
  const dur = duree(tr);
  ok('G-2 lecture', 'G-2 ouverte à 100 ms ET à 500 ms après l’appui', c.touche && a100.visible && a500.visible,
     '100 ms : ' + (a100.visible ? 'ouverte' : 'fermée') + ', 500 ms : ' + (a500.visible ? 'ouverte' : 'fermée')
       + (dur !== null && dur !== Infinity ? ' (ouverte puis refermée en ' + dur + ' ms)' : ''));
  ok('G-2 second appui', 'G-2 le second appui la ferme', a500.visible && !second.visible, dit(second));

  /* LA LIGNE D'UN PILIER, AU DOIGT : son point s'allume, sans bulle ni
     défilement — la ligne dit déjà tout. */
  console.log('\n  G-4 (doigt) — une ligne de la liste des piliers');
  await p.evaluate(REPOS);
  await p.evaluate(() => { document.querySelectorAll('[data-recette="ligne"]').forEach(e => e.removeAttribute('data-recette'));
    const r = document.querySelectorAll('#p-maturite .mat-pillar-row')[3]; if (!r) return;
    const d = r.querySelector('.mat-pillar-desc') || r; d.setAttribute('data-recette', 'ligne');
    d.scrollIntoView({ block: 'center', behavior: 'instant' }); });
  await p.waitForTimeout(400);
  const yl = await p.evaluate(() => scrollY);
  c = await appui(p, cdp, 'ligne', 600);
  const ligne = await p.evaluate(([bulle]) => {
    const r = document.querySelectorAll('#p-maturite .mat-pillar-row')[3];
    const f = r && r.querySelector('.mat-pillar-fill'); const pid = f && f.getAttribute('data-pillar');
    const pt = pid && document.querySelector('.mat-radar-pt[data-pillar="' + pid + '"]');
    const b = document.querySelector(bulle); const cs = b && getComputedStyle(b);
    return { allume: !!pt && pt.getAttribute('r') === '7', bulle: !!cs && cs.display !== 'none' && parseFloat(cs.opacity) > 0.5,
             y: scrollY };
  }, [G.mat.bulle]);
  ok('G-4 ligne doigt', 'G-4 appui sur une ligne : point allumé, sans bulle, sans défilement',
     c.touche && ligne.allume && !ligne.bulle && Math.round(ligne.y) === Math.round(yl),
     'point ' + (ligne.allume ? 'allumé' : 'éteint') + ', bulle ' + (ligne.bulle ? 'OUVERTE' : 'fermée') + ', défilement ' + Math.round(ligne.y - yl));

  /* UNE BULLE À LA FOIS : LE « i » (/infobulles.js) ET LE RADAR. */
  console.log('\n  Une bulle à la fois — le « i » d’une ligne et un point du radar');
  await p.evaluate(REPOS);
  await p.evaluate(() => { document.querySelectorAll('[data-recette="i"]').forEach(e => e.removeAttribute('data-recette'));
    const w = document.querySelectorAll('#p-maturite .mat-pillar-row .mat-tooltip-wrap')[1];
    if (w) { w.setAttribute('data-recette', 'i'); w.scrollIntoView({ block: 'center', behavior: 'instant' }); } });
  await p.waitForTimeout(400);
  /* LES OUVERTURES PENDANT L'APPUI, et pas seulement l'état qui suit : une
     bulle ouverte puis refermée dans la foulée est une seconde bulle. */
  const ti0 = (await transitions(p, 'mat-radar-tooltip')).length;
  c = await appui(p, cdp, 'i', 600);
  const i1 = await p.evaluate(BULLE_I, 'i');
  const g1b = await p.evaluate(VUE, [G.mat.bulle, null]);
  const ouvI = ouvertures((await transitions(p, 'mat-radar-tooltip')).slice(ti0));
  ok('préséance i', 'le « i » d’une ligne ouvre SA bulle, et aucune bulle de graphique ne s’ouvre, même un instant',
     c.touche && i1.visible && !g1b.visible && ouvI === 0,
     '« i » ' + (i1.visible ? 'ouvert' : 'fermé') + ', graphique ' + (g1b.visible ? 'OUVERT' : 'fermé') + ', ' + ouvI + ' ouverture(s) de la bulle du radar pendant l’appui');
  await marquer(p, G.mat.cible, 1, 'pti');
  await p.waitForTimeout(400);
  c = await appui(p, cdp, 'pti', 600);
  const i2 = await p.evaluate(BULLE_I, 'i');
  const g2b = await p.evaluate(VUE, [G.mat.bulle, 'pti']);
  await marquer(p, '#p-maturite .mat-pillar-row .mat-tooltip-wrap', 1, 'i');
  await p.waitForTimeout(400);
  await appui(p, cdp, 'i', 600);
  const i3 = await p.evaluate(BULLE_I, 'i');
  const g3b = await p.evaluate(VUE, [G.mat.bulle, null]);
  ok('une à la fois infobulles', 'une bulle à la fois : l’appui sur le point ferme le « i », l’appui sur le « i » ferme le point',
     g2b.visible && !i2.visible && i3.visible && !g3b.visible,
     'point puis « i » : ' + (g2b.visible ? 'point ouvert' : 'point FERMÉ') + ' / « i » ' + (i2.visible ? 'OUVERT' : 'fermé')
       + ' ; puis « i » ' + (i3.visible ? 'ouvert' : 'FERMÉ') + ' / point ' + (g3b.visible ? 'OUVERT' : 'fermé'));

  /* UNE BULLE À LA FOIS : /bulle-titre.js (appui long sur un bouton à title)
     ET LE RADAR. */
  console.log('\n  Une bulle à la fois — /bulle-titre.js et un point du radar');
  await p.evaluate(REPOS);
  await marquer(p, '#p-maturite .mat-sector-btn[title]', 0, 'secteur');
  await p.waitForTimeout(400);
  const bt1 = await appuiLong(p, cdp, 'secteur', () => p.evaluate(BULLE_TITRE));
  await marquer(p, G.mat.cible, 1, 'ptt');
  await p.waitForTimeout(400);
  await appui(p, cdp, 'ptt', 600);
  const bt2 = await p.evaluate(BULLE_TITRE);
  const gt2 = await p.evaluate(VUE, [G.mat.bulle, 'ptt']);
  await marquer(p, '#p-maturite .mat-sector-btn[title]', 0, 'secteur');
  await p.waitForTimeout(400);
  const pendant = await appuiLong(p, cdp, 'secteur', () => p.evaluate(([b]) => {
    const t = document.getElementById('bulle-titre'), g = document.querySelector(b), cs = g && getComputedStyle(g);
    return { titre: !!t && !t.hidden, graphe: !!cs && cs.display !== 'none' && parseFloat(cs.opacity) > 0.5 };
  }, [G.mat.bulle]));
  ok('une à la fois bulle-titre', 'une bulle à la fois : le point ferme la bulle du title, l’appui long sur le title ferme le point',
     bt1 && gt2.visible && !bt2 && pendant && pendant.titre && !pendant.graphe,
     'title seul ' + (bt1 ? 'ouvert' : 'NON ouvert') + ' ; point : ' + (gt2.visible ? 'ouvert' : 'FERMÉ') + ', title ' + (bt2 ? 'ENCORE ouvert' : 'fermé')
       + ' ; appui long : title ' + (pendant && pendant.titre ? 'ouvert' : 'FERMÉ') + ', point ' + (pendant && pendant.graphe ? 'ENCORE ouvert' : 'fermé'));

  /* LE RADAR DE RISQUE, AU DOIGT : le point, puis la ligne. */
  console.log('\n  Radar de risque — le point et la ligne, au doigt');
  await aller(p, 'radar', 2500);
  await p.evaluate(REPOS);
  await marquer(p, G.risque.cible, 1, 'rq');
  await p.waitForTimeout(400);
  c = await appui(p, cdp, 'rq', 100);
  const r100 = await p.evaluate(VUE, [G.risque.bulle, 'rq']);
  await p.waitForTimeout(400);
  const r500 = await p.evaluate(VUE, [G.risque.bulle, 'rq']);
  await appui(p, cdp, 'rq', 450);
  const r2 = await p.evaluate(VUE, [G.risque.bulle, 'rq']);
  ok('risque point', 'radar de risque : ouverte à 100 et 500 ms, dans la fenêtre visuelle ; le second appui la ferme',
     c.touche && r100.visible && r500.visible && r500.dansVV && !r2.visible,
     (c.touche ? '' : 'appui à côté (' + c.vise + ') ; ') + '100 ms ' + (r100.visible ? 'ouverte' : 'fermée') + ', 500 ms ' + dit(r500) + ', 2e appui ' + (r2.visible ? 'OUVERTE' : 'fermée'));
  await p.evaluate(REPOS);
  await marquer(p, G.risque.ligne, 2, 'rql');
  await p.waitForTimeout(400);
  const yr = await p.evaluate(() => scrollY);
  c = await appui(p, cdp, 'rql', 600);
  const rl = await p.evaluate(([b]) => {
    const row = document.querySelector('[data-recette="rql"]');
    const g = document.querySelector(b), cs = g && getComputedStyle(g);
    return { allume: !!row && row.classList.contains('mat-pillar-row-highlighted'), bulle: !!cs && cs.display !== 'none' && parseFloat(cs.opacity) > 0.5, y: scrollY };
  }, [G.risque.bulle]);
  ok('risque ligne', 'radar de risque : appui sur une ligne, point allumé sans bulle ni défilement',
     c.touche && rl.allume && !rl.bulle && Math.round(rl.y) === Math.round(yr),
     'ligne ' + (rl.allume ? 'allumée' : 'éteinte') + ', bulle ' + (rl.bulle ? 'OUVERTE' : 'fermée') + ', défilement ' + Math.round(rl.y - yr));

  /* G-5 (doigt) et G-6 — LA COURBE DE TARIFICATION. */
  console.log('\n  G-5 / G-6 — la courbe de tarification au doigt');
  await aller(p, 'pricing', 2500);
  await p.evaluate(REPOS);
  const cibles = await p.evaluate((sel) => {
    const els = [...document.querySelectorAll(sel)].filter(e => e.getBoundingClientRect().width > 0);
    const rs = els.map(e => e.getBoundingClientRect());
    const cs = rs.map(r => [r.left + r.width / 2, r.top + r.height / 2]);
    let min = Infinity;
    for (let i = 0; i < cs.length; i++) for (let j = i + 1; j < cs.length; j++) min = Math.min(min, Math.hypot(cs[i][0] - cs[j][0], cs[i][1] - cs[j][1]));
    const svg = document.getElementById('pricing-chart-svg');
    const arrets = svg ? [...svg.querySelectorAll('*')].filter(e => e.tabIndex >= 0 && e.getAttribute('tabindex') !== null).length : -1;
    return { n: els.length, largeur: rs.length ? Math.round(Math.min(...rs.map(r => r.width)) * 10) / 10 : 0,
             hauteur: rs.length ? Math.round(Math.min(...rs.map(r => r.height)) * 10) / 10 : 0,
             ecart: min === Infinity ? null : Math.round(min * 10) / 10, arrets, forme: els[0] ? els[0].tagName : '' };
  }, G.tarif.cible);
  ok('G-5 cibles', 'G-5 une cible par mois, 24 px de large au moins, un seul arrêt de tabulation',
     cibles.n >= 6 && cibles.n <= 18 && cibles.largeur >= 24 && cibles.arrets === 1,
     cibles.n + ' ' + cibles.forme + ', la plus étroite ' + cibles.largeur + ' × ' + cibles.hauteur + ' px, ' + cibles.ecart + ' px au plus près entre centres, ' + cibles.arrets + ' arrêt(s)');
  await marquer(p, G.tarif.cible, 2, 'tf');
  await p.waitForTimeout(400);
  const tfb = await balayer(p, cdp, 'tf');
  const trTf = await transitions(p, 'pricing-chart-tooltip');
  const ouvTf = ouvertures(trTf);
  await marquer(p, G.tarif.cible, 2, 'tf');
  await p.waitForTimeout(400);
  c = await appui(p, cdp, 'tf', 600);
  const tfv = await p.evaluate(VUE, [G.tarif.bulle, 'tf']);
  const series = ['Hybride', 'Pessimiste', 'Optimiste', 'RaaS Jalons'].filter(s => tfv.texte && tfv.texte.indexOf(s) >= 0).length;
  ok('G-6 tarification', 'G-6 un balayage à travers la courbe n’ouvre aucune bulle (témoin : l’appui qui suit l’ouvre)',
     tfb.defile !== 0 && ouvTf === 0 && tfv.visible,
     'défilement ' + tfb.defile + ' px, ' + ouvTf + ' ouverture(s) ; témoin : ' + dit(tfv));
  ok('G-5 bulle doigt', 'G-5 l’appui sur un mois ouvre sa bulle : quatre séries, dans la fenêtre visuelle, sans recouvrir la cible',
     c.touche && tfv.visible && series === 4 && tfv.dansVV && !tfv.croise && tfv.sousBarre,
     series + ' série(s) ; ' + dit(tfv) + (tfv.croise ? ' ; RECOUVRE la cible' : ''));

  /* G-6, G-8 — LES BARRES GÉOPOLITIQUES. */
  console.log('\n  G-6 / G-8 — les barres géopolitiques au doigt');
  await aller(p, 'geo', 2000);
  await p.evaluate(REPOS);
  await marquer(p, G.geo.cible, 1, 'gb');
  await p.waitForTimeout(400);
  const gbb = await balayer(p, cdp, 'gb');
  const ouvGeo = ouvertures(await transitions(p, 'geo-tooltip'));
  await marquer(p, G.geo.cible, 3, 'gb');
  await p.waitForTimeout(400);
  c = await appui(p, cdp, 'gb', 600);
  const gv = await p.evaluate(VUE, [G.geo.bulle, 'gb']);
  ok('G-6 géo', 'G-6 un balayage à travers l’histogramme n’ouvre aucune bulle (témoin : l’appui qui suit l’ouvre)',
     gbb.defile !== 0 && ouvGeo === 0 && gv.visible, 'défilement ' + gbb.defile + ' px, ' + ouvGeo + ' ouverture(s) ; témoin : ' + dit(gv));
  const g8a = await p.evaluate(() => { const e = document.querySelector('[data-recette="gb"]'); return e ? Math.round(e.getBoundingClientRect().top) : null; });
  const sy8 = await p.evaluate(() => scrollY);
  /* VERS LE HAUT : la barre descend de 200 px et garde la place de sa bulle
     au-dessus d'elle — vers le bas, elle passerait sous la barre du haut et
     la bulle basculerait dessous, ce qui ne mesurerait plus le suivi. */
  await p.evaluate(() => window.scrollBy(0, -200));
  await p.waitForTimeout(500);
  const g8v = await p.evaluate(VUE, [G.geo.bulle, 'gb']);
  const g8b = await p.evaluate(() => { const e = document.querySelector('[data-recette="gb"]'); return e ? Math.round(e.getBoundingClientRect().top) : null; });
  const defile8 = Math.round((await p.evaluate(() => scrollY)) - sy8);
  /* LA BARRE DOIT ÊTRE LA MÊME AVANT ET APRÈS, et la page avoir défilé : une
     barre redessinée par l'appui n'a plus de position à comparer — le
     relevé comparerait deux absences. */
  const dBarre = (g8a !== null && g8b !== null) ? g8b - g8a : null, dBulle = gv.existe && g8v.existe ? g8v.rect[1] - gv.rect[1] : null;
  ok('G-8 défilement', 'G-8 bulle ouverte, défilement de 200 px : la bulle SUIT la barre (2 px près) et reste ouverte',
     gv.visible && g8v.visible && Math.abs(defile8) >= 150 && dBarre !== null && dBulle !== null && Math.abs(dBulle - dBarre) <= 2,
     'page ' + defile8 + ' px, barre ' + (dBarre === null ? 'DÉTRUITE par l’appui' : dBarre + ' px') + ', bulle ' + dBulle + ' px (top ' + (gv.rect || [])[1] + ' → ' + (g8v.rect || [])[1] + ')' + (g8v.visible ? '' : ', bulle FERMÉE'));
  await appui(p, cdp, 'gb', 450);

  /* LE SCHÉMA DE L'ÉCOSYSTÈME AU DOIGT : ouvrir, relire, appui ailleurs. */
  console.log('\n  Écosystème au doigt');
  await aller(p, 'carto-uc', 2000);
  await p.evaluate(REPOS);
  await marquer(p, G.eco.cible, 1, 'eco');
  await p.waitForTimeout(400);
  c = await appui(p, cdp, 'eco', 100);
  const e100 = await p.evaluate(VUE, [G.eco.bulle, 'eco']);
  await p.waitForTimeout(400);
  const e500 = await p.evaluate(VUE, [G.eco.bulle, 'eco']);
  const annonce = await p.evaluate(() => { const r = document.getElementById('bulle-annonce'); return r ? r.textContent : ''; });
  await p.evaluate(() => { document.querySelectorAll('[data-recette="vide"]').forEach(e => e.removeAttribute('data-recette'));
    const t = document.querySelector('#p-carto-uc .carto-eco-title'); if (t) t.setAttribute('data-recette', 'vide'); });
  await appui(p, cdp, 'vide', 450);
  const eAilleurs = await p.evaluate(VUE, [G.eco.bulle, 'eco']);
  ok('eco doigt', 'écosystème : l’appui ouvre (100 et 500 ms), sans annonce ; un appui ailleurs ferme',
     c.touche && e100.visible && e500.visible && e500.dansVV && !eAilleurs.visible && annonce === '',
     '100 ms ' + (e100.visible ? 'ouverte' : 'fermée') + ', 500 ms ' + dit(e500) + ', ailleurs ' + (eAilleurs.visible ? 'OUVERTE' : 'fermée')
       + (annonce ? ', annonce « ' + annonce.slice(0, 40) + ' »' : ''));
  await ctx.close();
  }

  // ══ B. POSTE — 1280 × 900, souris, clavier, stylet ═════════════════════
  if (joue('B')) {
  console.log('\n══ B. Poste (1280 × 900) ══');
  if (joue('A')) await pause(15000);
  ({ ctx, p, cdp } = await nouveau(nav, { viewport: { width: 1280, height: 900 } }));
  ok(null, 'la page répond', (await sentinel(p, 'maturite')) === 200);
  await aller(p, 'maturite');

  /* L'ORDRE DES ÉCOUTEURS D'ÉCHAP, relevé dans la page. */
  const ordre = await p.evaluate(() => window.__echap.slice());
  const iG = ordre.indexOf('sentinel.page.js'), iI = ordre.indexOf('infobulles.js'), iT = ordre.indexOf('bulle-titre.js');
  ok('échap ordre', 'Échap : l’écouteur des graphiques passe AVANT /infobulles.js et /bulle-titre.js (window, capture)',
     iG >= 0 && iI > iG && iT > iI, ordre.join(' → ') || '(aucun)');

  /* SANS RIEN PERDRE AU POSTE : le survol ouvre chaque bulle, ancrée, sans
     double bulle ; la sortie la ferme. */
  console.log('\n  Le survol, graphique par graphique');
  const survols = {};
  for (const k of ['mat', 'risque', 'tarif', 'geo', 'eco']) {
    await aller(p, G[k].ecran, 2200);
    await p.evaluate(REPOS);
    await p.mouse.move(2, 890);
    if (!(await marquer(p, G[k].cible, 1, 'sv-' + k))) { survols[k] = { absent: true }; continue; }
    await p.waitForTimeout(400);
    c = await centre(p, 'sv-' + k);
    await p.mouse.move(c.x, c.y, { steps: 4 });
    await p.waitForTimeout(500);
    const s = await p.evaluate(VUE, [G[k].bulle, 'sv-' + k]);
    const double = await p.evaluate(() => ({ titre: !!document.getElementById('bulle-titre') && !document.getElementById('bulle-titre').hidden,
      infobulle: document.querySelectorAll('.bulle-ouverte').length }));
    const titres = await p.evaluate((m) => { const e = document.querySelector('[data-recette="' + m + '"]'); const out = [];
      for (let a = e; a && a.getAttribute; a = a.parentElement) { const t = a.getAttribute('title'); if (t && t.trim()) out.push(a.tagName + ' « ' + t.slice(0, 30) + ' »'); }
      const svg = e && e.closest('svg'); return { titres: out, svgTitle: svg ? svg.querySelectorAll('title').length : 0 }; }, 'sv-' + k);
    await p.mouse.move(2, 890, { steps: 4 });
    await p.waitForTimeout(700);
    const sortie = await p.evaluate(VUE, [G[k].bulle, 'sv-' + k]);
    survols[k] = { s, sortie, double, titres, touche: c.touche };
    dire(k + ' : ' + dit(s) + ' ; sortie ' + (sortie.visible ? 'OUVERTE' : 'fermée') + ' ; ancêtres à title ' + titres.titres.length + ', <title> ' + titres.svgTitle);
  }
  const pourquoi = (x) => !x.s ? 'absent' : !x.touche ? 'pointeur à côté' : !x.s.visible ? 'pas ouverte' : !x.s.dansVV ? 'hors fenêtre'
    : !x.s.auDessus ? 'recouverte' : x.s.croise ? 'recouvre sa cible' : x.sortie.visible ? 'reste à la sortie' : x.double.titre ? 'double bulle' : 'ok';
  const svOk = Object.keys(survols).filter(k => pourquoi(survols[k]) === 'ok');
  ok('survol poste', 'sans rien perdre au poste : le survol ouvre les 5 bulles, dans la fenêtre, sans recouvrir la cible ; la sortie les ferme',
     svOk.length === 5, svOk.length + '/5 (' + Object.keys(survols).map(k => k + ' ' + pourquoi(survols[k])).join(', ') + ')');
  const avecTitre = Object.keys(survols).filter(k => survols[k].titres && (survols[k].titres.titres.length || survols[k].titres.svgTitle));
  /* LE TÉMOIN : le même relevé, sur un bouton du même écran qui porte un
     title, en trouve un. */
  await aller(p, 'maturite', 1500);
  const temoinTitre = await p.evaluate(() => { const e = document.querySelector('#p-maturite .mat-sector-btn[title]'); let k = 0;
    for (let a = e; a && a.getAttribute; a = a.parentElement) { const t = a.getAttribute('title'); if (t && t.trim()) k++; } return k; });
  ok('titres', 'aucune cible de graphique ni aucun de ses ancêtres ne porte de title, aucun <title> SVG (pas de seconde bulle)',
     Object.keys(survols).length === 5 && avecTitre.length === 0 && temoinTitre > 0,
     (avecTitre.length ? avecTitre.map(k => k + ' ' + JSON.stringify(survols[k].titres)).join(' ; ') : '0 sur 5 graphiques')
       + ' (témoin : ' + temoinTitre + ' title relevé(s) sur un bouton de secteur)');

  /* UNE BULLE À LA FOIS, AU POSTE : la souris sur un point du radar (sa
     bulle ouverte), puis une tabulation vers une ligne du menu à `title`
     (/bulle-titre.js l'ouvre 500 ms après). Le menu est fixe : la page ne
     défile pas, la souris ne quitte pas le point — si la bulle du graphique
     se ferme, c'est que l'autre l'a fermée. LE TÉMOIN : à 250 ms, elle est
     encore là. */
  console.log('\n  Une bulle à la fois — le survol d’un point, puis Tab vers une ligne du menu');
  await aller(p, 'maturite', 1500);
  await p.evaluate(REPOS);
  await p.mouse.move(2, 890);
  const pretSb = await p.evaluate(() => {
    const vis = e => { const q = e.getBoundingClientRect(); return q.width > 0 && q.height > 0 && q.top > 60 && q.bottom < innerHeight - 20; };
    const items = [...document.querySelectorAll('#sb .sb-item[title]')].filter(vis);
    const T = [...document.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select,textarea,[tabindex]')].filter(e => e.tabIndex >= 0 && e.getBoundingClientRect().width > 0);
    for (const it of items) { const i = T.indexOf(it); if (i >= 1 && T[i - 1].closest('#sb')) {
      document.querySelectorAll('[data-recette="sb"]').forEach(e => e.removeAttribute('data-recette'));
      it.setAttribute('data-recette', 'sb'); T[i - 1].focus(); return true; } }
    return false;
  });
  await marquer(p, G.mat.cible, 3, 'ptsb');
  await p.waitForTimeout(400);
  c = await centre(p, 'ptsb');
  await p.mouse.move(c.x, c.y, { steps: 4 });
  await p.waitForTimeout(500);
  const sb0 = await p.evaluate(VUE, [G.mat.bulle, 'ptsb']);
  const ySb = await p.evaluate(() => scrollY);
  await p.keyboard.press('Tab');
  await p.waitForTimeout(250);
  const sb250 = { g: await p.evaluate(VUE, [G.mat.bulle, 'ptsb']), t: await p.evaluate(BULLE_TITRE) };
  await p.waitForTimeout(450);
  const sb700 = { g: await p.evaluate(VUE, [G.mat.bulle, 'ptsb']), t: await p.evaluate(BULLE_TITRE),
                  focus: await p.evaluate(() => document.activeElement === document.querySelector('[data-recette="sb"]')),
                  dy: Math.round((await p.evaluate(() => scrollY)) - ySb) };
  ok('une à la fois poste', 'une bulle à la fois au poste : la bulle d’un title ouverte au clavier ferme celle du graphique survolé',
     pretSb && c.touche && sb0.visible && sb250.g.visible && !sb250.t && sb700.focus && sb700.t && !sb700.g.visible && sb700.dy === 0,
     'survol : ' + (sb0.visible ? 'ouverte' : 'fermée') + ' ; Tab + 250 ms : graphique ' + (sb250.g.visible ? 'ouvert' : 'FERMÉ') + ', title ' + (sb250.t ? 'ouvert' : 'fermé')
       + ' ; + 700 ms : title ' + (sb700.t ? 'ouvert' : 'FERMÉ') + ', graphique ' + (sb700.g.visible ? 'ENCORE OUVERT' : 'fermé') + (sb700.focus ? '' : ' (le focus n’est pas sur la ligne du menu)')
       + (sb700.dy ? ', la page a défilé de ' + sb700.dy + ' px' : ''));
  await p.evaluate(() => { if (window.bulleTitre) window.bulleTitre.fermer(); if (document.activeElement) document.activeElement.blur(); });
  await p.mouse.move(2, 890, { steps: 3 });

  /* G-3 — LA BULLE DU RADAR DE MATURITÉ APRÈS SURVOL ET SORTIE. */
  console.log('\n  G-3 — #mat-radar-tooltip après survol et sortie');
  await aller(p, 'maturite', 1500);
  const g3 = await p.evaluate(() => { const b = document.getElementById('mat-radar-tooltip'); if (!b) return null;
    const cs = getComputedStyle(b); return { display: cs.display, opacite: cs.opacity, ah: b.getAttribute('aria-hidden') }; });
  const axTip = await (async () => { try {
    const { root } = await cdp.send('DOM.getDocument', { depth: 0 });
    const { nodeId } = await cdp.send('DOM.querySelector', { nodeId: root.nodeId, selector: '#mat-radar-tooltip' });
    if (!nodeId) return null;
    const r = await cdp.send('Accessibility.getPartialAXTree', { nodeId, fetchRelatives: false });
    return !!(r.nodes[0] || {}).ignored; } catch (e) { return null; } })();
  ok('G-3 maturité', 'G-3 après survol puis sortie : display:none, aria-hidden="true", ignorée par l’arbre d’accessibilité',
     !!g3 && g3.display === 'none' && g3.ah === 'true' && axTip === true,
     g3 ? 'display ' + g3.display + ', opacité ' + g3.opacite + ', aria-hidden ' + g3.ah + ', ignorée ' + axTip : 'absente');
  const ah = await p.evaluate((ids) => ids.map(id => { const b = document.getElementById(id); return id + '=' + (b ? b.getAttribute('aria-hidden') : 'absente'); }), BULLES);
  ok('G-3 toutes', 'G-3 les cinq bulles de graphique portent aria-hidden="true"', ah.every(x => /=true$/.test(x)), ah.join(' '));

  /* G-4 — LES RADARS NE PRENNENT PAS LE FOCUS ; LE « i » ALLUME SON POINT. */
  console.log('\n  G-4 — les radars et le « i » des lignes');
  const radars = await p.evaluate(([m, r]) => {
    const f = (sel) => [...document.querySelectorAll(sel)].filter(e => e.hasAttribute('tabindex')).length;
    const svgM = document.getElementById('mat-radar-svg-el'), svgR = document.getElementById('radar-svg');
    return { zonesMat: f(m), zonesRisque: f(r), mat: svgM ? (svgM.getAttribute('role') || '—') + ' « ' + (svgM.getAttribute('aria-label') || '') + ' »' : 'absent',
             risque: svgR ? (svgR.getAttribute('role') || '—') + ' « ' + (svgR.getAttribute('aria-label') || '') + ' »' : 'absent',
             okM: !!svgM && svgM.getAttribute('role') === 'img' && (svgM.getAttribute('aria-label') || '').length > 10,
             okR: !!svgR && svgR.getAttribute('role') === 'img' && (svgR.getAttribute('aria-label') || '').length > 10 };
  }, [G.mat.cible, G.risque.cible]);
  ok('G-4 radars', 'G-4 aucune zone de radar à tabindex ; chaque svg en role="img" avec un nom de synthèse',
     radars.zonesMat === 0 && radars.zonesRisque === 0 && radars.okM && radars.okR,
     'zones à tabindex ' + radars.zonesMat + ' + ' + radars.zonesRisque + ' ; maturité ' + radars.mat + ' ; risque ' + radars.risque);
  await p.evaluate(REPOS);
  await p.evaluate(() => { document.querySelectorAll('[data-recette="i4"]').forEach(e => e.removeAttribute('data-recette'));
    const w = document.querySelectorAll('#p-maturite .mat-pillar-row .mat-tooltip-wrap')[4];
    if (w) { w.setAttribute('data-recette', 'i4'); w.scrollIntoView({ block: 'center', behavior: 'instant' }); } });
  await p.waitForTimeout(500);
  const pretI = await p.evaluate(() => { const w = document.querySelector('[data-recette="i4"]'); if (!w) return false;
    const t = [...document.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select,textarea,[tabindex]')].filter(e => e.tabIndex >= 0 && e.getBoundingClientRect().width > 0);
    const i = t.indexOf(w); if (i < 1) return false; t[i - 1].focus(); return true; });
  await p.waitForTimeout(400);
  const yi = await p.evaluate(() => scrollY);
  await p.keyboard.press('Tab');
  await p.waitForTimeout(600);
  const g4 = await p.evaluate(([b]) => {
    const w = document.querySelector('[data-recette="i4"]'); const row = w && w.closest('.mat-pillar-row');
    const f = row && row.querySelector('.mat-pillar-fill'); const pid = f && f.getAttribute('data-pillar');
    const pt = pid && document.querySelector('.mat-radar-pt[data-pillar="' + pid + '"]');
    const g = document.querySelector(b), cs = g && getComputedStyle(g);
    return { focus: document.activeElement === w, allume: !!pt && pt.getAttribute('r') === '7',
             bulle: !!cs && cs.display !== 'none' && parseFloat(cs.opacity) > 0.5, y: scrollY };
  }, [G.mat.bulle]);
  ok('G-4 Tab i', 'G-4 Tab jusqu’au « i » d’une ligne : son point s’allume, sans bulle de graphique, scrollY inchangé',
     pretI && g4.focus && g4.allume && !g4.bulle && Math.round(g4.y) === Math.round(yi),
     'focus ' + (g4.focus ? 'sur le « i »' : 'AILLEURS') + ', point ' + (g4.allume ? 'allumé' : 'éteint') + ', bulle ' + (g4.bulle ? 'OUVERTE' : 'fermée') + ', défilement ' + Math.round(g4.y - yi));

  /* ÉCHAP NE FERME QU'UNE CHOSE À LA FOIS : le « i » a le focus (sa bulle
     est ouverte par /infobulles.js), la souris survole le point du même
     pilier (la bulle du graphique). */
  console.log('\n  Échap — deux bulles, deux frappes');
  const pidI = await p.evaluate(() => { const w = document.querySelector('[data-recette="i4"]'); const f = w && w.closest('.mat-pillar-row').querySelector('.mat-pillar-fill');
    const pid = f && f.getAttribute('data-pillar'); const z = pid && document.querySelector('.mat-radar-hitzone[data-pillar="' + pid + '"]');
    document.querySelectorAll('[data-recette="zi"]').forEach(e => e.removeAttribute('data-recette')); if (z) z.setAttribute('data-recette', 'zi'); return pid; });
  c = await centre(p, 'zi');
  await p.mouse.move(c.x, c.y, { steps: 4 });
  await p.waitForTimeout(500);
  const e0 = { i: await p.evaluate(BULLE_I, 'i4'), g: await p.evaluate(VUE, [G.mat.bulle, 'zi']) };
  await p.keyboard.press('Escape');
  await p.waitForTimeout(400);
  const e1 = { i: await p.evaluate(BULLE_I, 'i4'), g: await p.evaluate(VUE, [G.mat.bulle, 'zi']) };
  await p.keyboard.press('Escape');
  await p.waitForTimeout(400);
  const e2 = { i: await p.evaluate(BULLE_I, 'i4'), g: await p.evaluate(VUE, [G.mat.bulle, 'zi']) };
  ok('échap une chose', 'Échap : la 1re frappe ferme la bulle du graphique SEULE, la 2e celle du « i »',
     !!pidI && c.touche && e0.i.visible && e0.g.visible && !e1.g.visible && e1.i.visible && !e2.i.visible,
     'avant : « i » ' + (e0.i.visible ? 'ouvert' : 'fermé') + ', graphique ' + (e0.g.visible ? 'ouvert' : 'fermé')
       + ' ; 1re : « i » ' + (e1.i.visible ? 'ouvert' : 'fermé') + ', graphique ' + (e1.g.visible ? 'OUVERT' : 'fermé')
       + ' ; 2e : « i » ' + (e2.i.visible ? 'OUVERT' : 'fermé'));
  await p.mouse.move(2, 890, { steps: 3 });
  await p.evaluate(REPOS);

  /* G-5 (clavier), G-12 — LA COURBE DE TARIFICATION. */
  console.log('\n  G-5 / G-12 — la courbe de tarification au clavier');
  await aller(p, 'pricing', 2500);
  await p.evaluate(REPOS);
  await p.mouse.move(2, 890);
  const avantTf = await p.evaluate(() => {
    const svg = document.getElementById('pricing-chart-svg'); if (!svg) return null;
    svg.scrollIntoView({ block: 'center', behavior: 'instant' });
    const t = [...document.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select,textarea,[tabindex]')].filter(e => e.tabIndex >= 0 && e.getBoundingClientRect().width > 0);
    const dans = t.filter(e => svg.contains(e));
    const i = dans.length ? t.indexOf(dans[0]) : -1;
    if (i >= 1) t[i - 1].focus();
    return { arrets: dans.length, pret: i >= 1 };
  });
  await p.waitForTimeout(500);
  await p.keyboard.press('Tab');
  await p.waitForTimeout(500);
  const k1 = await p.evaluate(([b]) => { const a = document.activeElement; const g = document.querySelector(b), cs = g && getComputedStyle(g);
    return { mois: a && a.getAttribute ? a.getAttribute('data-mois') : null, tag: a ? a.tagName : null,
             bulle: !!cs && cs.display !== 'none', texte: g ? g.textContent.replace(/\s+/g, ' ').slice(0, 60) : '',
             label: a && a.getAttribute ? a.getAttribute('aria-label') : null }; }, [G.tarif.bulle]);
  await p.keyboard.press('ArrowRight');
  await p.waitForTimeout(500);
  const k2 = await p.evaluate(([b]) => { const a = document.activeElement; const g = document.querySelector(b);
    const r = a && a.getBoundingClientRect ? a.getBoundingClientRect() : null, q = g ? g.getBoundingClientRect() : null;
    return { mois: a && a.getAttribute ? a.getAttribute('data-mois') : null, bulle: !!g && getComputedStyle(g).display !== 'none',
             texte: g ? g.textContent.replace(/\s+/g, ' ').slice(0, 30) : '', dans: !!r && !!q && q.left + q.width / 2 >= r.left && q.left + q.width / 2 <= r.right,
             arrets: [...document.querySelectorAll('#pricing-chart-svg [tabindex="0"]')].length }; }, [G.tarif.bulle]);
  await p.keyboard.press('End');
  await p.waitForTimeout(300);
  const kFin = await p.evaluate(() => { const a = document.activeElement; return a && a.getAttribute ? a.getAttribute('data-mois') : null; });
  await p.keyboard.press('Home');
  await p.waitForTimeout(300);
  const kDebut = await p.evaluate(() => { const a = document.activeElement; return a && a.getAttribute ? a.getAttribute('data-mois') : null; });
  const quatre = k1.label ? ['Hybride continu', 'Pessimiste', 'Optimiste', 'RaaS Jalons'].filter(s => k1.label.indexOf(s) >= 0).length : 0;
  ok('G-5 clavier', 'G-5 un seul arrêt ; Tab ouvre le mois 1 ; → passe au mois 2, focus ET bulle (centre x dans la bande) ; Fin, Début',
     !!avantTf && avantTf.arrets === 1 && k1.mois === '1' && k1.bulle && k2.mois === '2' && k2.bulle && k2.dans && k2.arrets === 1
       && /Mois 2/.test(k2.texte) && kDebut === '1' && kFin && +kFin > 2,
     (avantTf ? avantTf.arrets : '?') + ' arrêt(s) ; Tab → ' + (k1.mois ? 'mois ' + k1.mois : k1.tag) + ' (' + (k1.bulle ? 'bulle ouverte' : 'pas de bulle') + ') ; → mois '
       + k2.mois + ', ' + (k2.dans ? 'bulle centrée sur la bande' : 'bulle HORS de la bande') + ' ; Fin → ' + kFin + ', Début → ' + kDebut);
  const table = await p.evaluate(() => { const t = document.querySelector('#pricing-chart-donnees table');
    const d = document.querySelector('#p-pricing details.chart-donnees > summary');
    return { lignes: t ? t.querySelectorAll('tbody tr').length : 0, valeurs: t ? t.querySelectorAll('tbody td').length : 0,
             entetes: t ? [...t.querySelectorAll('thead th')].map(x => x.textContent.trim()).join(' | ') : '', resume: d ? d.textContent.trim() : '',
             n: document.querySelectorAll('#pricing-chart-svg [data-graphe="tarif"]').length }; });
  ok('G-5 nom et tableau', 'G-5 chaque mois se nomme par ses quatre séries ; « Voir les données » : n lignes × 4 valeurs',
     quatre === 4 && /€/.test(k1.label || '') && table.n > 0 && table.lignes === table.n && table.valeurs === table.n * 4 && table.resume === 'Voir les données',
     'nom « ' + (k1.label || '').slice(0, 110) + ' » ; tableau ' + table.lignes + ' × ' + (table.lignes ? table.valeurs / table.lignes : 0) + ' (' + table.entetes + ')');

  /* G-12 — LE CONTOUR DE FOCUS D'UNE BANDE, MESURÉ SUR LA CAPTURE. */
  await p.keyboard.press('ArrowRight');
  await p.waitForTimeout(400);
  const zoneG12 = await p.evaluate(() => { const a = document.activeElement; if (!a || !a.getAttribute || a.getAttribute('data-graphe') !== 'tarif') return null;
    const r = a.getBoundingClientRect(), cs = getComputedStyle(a);
    return { x: Math.round(r.left) - 6, y: Math.round(r.top + r.height * 0.55), l: 12, h: 24, contour: cs.outlineStyle + ' ' + cs.outlineWidth,
             trait: cs.stroke + ' ' + cs.strokeWidth }; });
  let g12 = null;
  if (zoneG12) {
    const clip = { x: zoneG12.x, y: zoneG12.y, width: zoneG12.l, height: zoneG12.h };
    const focus = await p.screenshot({ clip });
    /* LE MÊME ENDROIT SANS LE FOCUS : on le rend au bouton qui précède. */
    await p.evaluate(() => { const a = document.activeElement; if (a && a.blur) a.blur(); });
    await p.evaluate(REPOS);
    await p.waitForTimeout(300);
    const repos = await p.screenshot({ clip });
    g12 = await contraste(ctx, focus, repos);
  }
  ok('G-12 contour', 'G-12 le focus clavier d’une bande se DESSINE (trait, pas de contour carré) ; contraste ≥ 3:1 sur la capture',
     !!zoneG12 && !!g12 && g12.changes >= zoneG12.h && g12.mediane >= 3 && /^none/.test(zoneG12.contour),
     zoneG12 ? 'contour ' + zoneG12.contour + ', trait ' + zoneG12.trait + ' ; ' + (g12 ? g12.changes + ' pixels changés, contraste médian '
       + g12.mediane + ':1 (max ' + g12.max + ':1)' : '—') : 'aucune bande focalisée au clavier');
  await p.evaluate(REPOS);

  /* G-7, G-11 — LES BARRES GÉOPOLITIQUES. */
  console.log('\n  G-7 / G-11 — les barres géopolitiques');
  await aller(p, 'geo', 2000);
  await p.evaluate(REPOS);
  await marquer(p, G.geo.cible, 2, 'gc');
  await p.waitForTimeout(400);
  await p.evaluate(() => { window.__geoMut = 0; window.__geoAvant = document.querySelector('[data-recette="gc"]');
    new MutationObserver(r => { window.__geoMut += r.length; }).observe(document.getElementById('geo-chart'), { childList: true }); });
  c = await centre(p, 'gc');
  await p.mouse.click(c.x, c.y);
  await p.waitForTimeout(500);
  const g7 = await p.evaluate(() => { const els = [...document.querySelectorAll('#geo-chart .geo-bar-col')]; const a = window.__geoAvant;
    return { meme: !!a && a.isConnected && a.isSameNode(els[2]), mut: window.__geoMut, actif: document.activeElement.tagName + '.' + String(document.activeElement.className).slice(0, 20) }; });
  ok('G-7 clic', 'G-7 un clic sur une barre ne la détruit pas : même élément, aucun redessin, focus gardé',
     g7.meme && g7.mut === 0 && !/^BODY/.test(g7.actif), (g7.meme ? 'même élément' : 'élément DÉTRUIT') + ', ' + g7.mut + ' mutation(s) du graphique, focus sur ' + g7.actif);
  const noms = [];
  for (let i = 0; i < 5; i++) {
    try {
      const { root } = await cdp.send('DOM.getDocument', { depth: 0 });
      const { nodeIds } = await cdp.send('DOM.querySelectorAll', { nodeId: root.nodeId, selector: '#geo-chart .geo-bar-col' });
      const r = await cdp.send('Accessibility.getPartialAXTree', { nodeId: nodeIds[i], fetchRelatives: false });
      const x = r.nodes[0] || {}; noms.push({ role: x.role && x.role.value, nom: (x.name && x.name.value) || '' });
    } catch (e) { noms.push({ role: '?', nom: '' }); }
  }
  const puces = await p.evaluate(() => [...document.querySelectorAll('.geo-filter-chip')].map(e => e.tagName + (e.getAttribute('aria-pressed') ? '[' + e.getAttribute('aria-pressed') + ']' : '')));
  ok('G-7 noms', 'G-7 les barres sont des images nommées (niveau, nombre, description)',
     noms.length === 5 && noms.every(x => (x.role === 'image' || x.role === 'img') && /juridiction/.test(x.nom) && / — /.test(x.nom)),
     noms.map(x => x.role + ' « ' + x.nom.slice(0, 40) + ' »').join(' · '));
  await p.evaluate(() => { const b = document.querySelector('.geo-filter-chip[data-filter="critical"]'); if (b) { b.scrollIntoView({ block: 'center' }); b.focus(); } });
  await p.keyboard.press('Enter');
  await p.waitForTimeout(300);
  const pr1 = await p.evaluate(() => [...document.querySelectorAll('.geo-filter-chip[data-filter]')].map(e => e.getAttribute('data-filter') + '=' + e.getAttribute('aria-pressed')).join(' '));
  await p.evaluate(() => { const b = document.querySelector('.geo-filter-chip[data-filter="all"]'); if (b) b.focus(); });
  await p.keyboard.press('Enter');
  await p.waitForTimeout(300);
  const pr2 = await p.evaluate(() => [...document.querySelectorAll('.geo-filter-chip[data-filter]')].map(e => e.getAttribute('data-filter') + '=' + e.getAttribute('aria-pressed')).join(' '));
  ok('G-7 puces', 'G-7 les puces sont des <button aria-pressed>, activables à Entrée',
     puces.length === 8 && puces.every(x => /^BUTTON\[(true|false)\]$/.test(x)) && /critical=true/.test(pr1) && /all=false/.test(pr1) && /all=true/.test(pr2),
     puces.join(' ') + ' ; Entrée sur « Critique » : ' + pr1 + ' ; sur « Tous » : ' + pr2);
  /* G-11 — LE STYLET QUI PLANE. */
  await p.evaluate(REPOS);
  await p.mouse.move(2, 890);
  await marquer(p, G.geo.cible, 1, 'gs');
  await p.waitForTimeout(400);
  c = await centre(p, 'gs');
  await cdp.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: c.x, y: c.y, pointerType: 'pen' });
  await p.waitForTimeout(500);
  const g11 = await p.evaluate(VUE, [G.geo.bulle, 'gs']);
  ok('G-11 stylet', 'G-11 un stylet qui plane sur une barre ouvre sa bulle', g11.visible && g11.dansVV,
     dit(g11) + (g11.croise ? ' (recouvre la barre)' : ''));
  await cdp.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: 2, y: 890, pointerType: 'pen' });
  await p.waitForTimeout(600);
  await p.mouse.move(2, 890);
  await p.evaluate(REPOS);
  const kGeo = await clavier(p, G.geo.cible, G.geo.bulle);
  ok('clavier géo', 'au clavier, les barres : un arrêt, Tab ouvre, → passe, Échap ferme sans rouvrir, Tab sort et ferme', kGeo.bon, kGeo.rendu);
  await p.evaluate(REPOS);
  const vGeo = await voisines(p, G.geo.cible, G.geo.bulle);
  ok('voisines géo', 'au survol, la bulle d’une barre ne recouvre ni sa barre ni une autre', vGeo.n === 5 && vGeo.vues === 5 && vGeo.fautes === 0 && vGeo.detail.length === 0,
     vGeo.vues + '/' + vGeo.n + ' ouvertes' + (vGeo.detail.length ? ', recouvrements : ' + vGeo.detail.join(' · ') : ', aucun recouvrement'));

  /* G-9, G-10 — LE SCHÉMA DE L'ÉCOSYSTÈME. */
  console.log('\n  G-9 / G-10 — le schéma de l’écosystème');
  await aller(p, 'carto-uc', 2000);
  await p.evaluate(REPOS);
  const g9 = await p.evaluate(() => {
    const svg = document.querySelector('.carto-eco-svg'); if (!svg) return null;
    const g = [...svg.querySelectorAll('.eco-node')];
    const brut = /\\u2019/.test(svg.outerHTML);
    return { role: svg.getAttribute('role'), n: g.length, roles: g.filter(x => x.getAttribute('role') === 'img').length,
             prets: g.filter(x => x.hasAttribute('data-bulle-prete')).length, brut,
             arrets: g.filter(x => x.tabIndex >= 0 && x.hasAttribute('tabindex')).length,
             visibles: g.map(x => (x.querySelector('.eco-t') || {}).textContent || '') };
  });
  const nomsEco = [];
  try {
    const { root } = await cdp.send('DOM.getDocument', { depth: 0 });
    const { nodeIds } = await cdp.send('DOM.querySelectorAll', { nodeId: root.nodeId, selector: '.carto-eco-svg .eco-node' });
    for (const id of nodeIds) { const r = await cdp.send('Accessibility.getPartialAXTree', { nodeId: id, fetchRelatives: false });
      const x = r.nodes[0] || {}; nomsEco.push({ nom: (x.name && x.name.value) || '', ignore: !!x.ignored }); }
  } catch (e) { /* rien */ }
  const commencent = g9 ? nomsEco.filter((x, i) => g9.visibles[i] && x.nom.indexOf(g9.visibles[i]) === 0).length : 0;
  ok('G-9 schéma', 'G-9 svg role=group, 11 nœuds role=img nommés d’abord par leur texte visible, aucun data-bulle-prete, aucun \\u2019, 1 arrêt',
     !!g9 && g9.role === 'group' && g9.n === 11 && g9.roles === 11 && commencent === 11 && g9.prets === 0 && !g9.brut && g9.arrets === 1,
     g9 ? 'svg ' + g9.role + ', ' + g9.roles + '/' + g9.n + ' img, ' + commencent + ' noms commencent par le texte visible, '
       + g9.prets + ' data-bulle-prete, \\u2019 ' + (g9.brut ? 'PRÉSENT' : 'absent') + ', ' + g9.arrets + ' arrêt(s)' : 'absent');
  const kEco = await clavier(p, G.eco.cible, G.eco.bulle);
  ok('clavier écosystème', 'au clavier, le schéma : un arrêt, Tab ouvre, → passe, Échap ferme sans rouvrir, Tab sort et ferme', kEco.bon, kEco.rendu);
  await p.evaluate(REPOS);
  const vEco = await voisines(p, G.eco.cible, G.eco.bulle);
  ok('voisines écosystème', 'au survol, la bulle d’un nœud ne couvre ni lui-même ni le CENTRE d’un autre nœud (au plus 40 % d’un voisin)',
     vEco.n === 11 && vEco.vues === 11 && vEco.fautes === 0 && vEco.partMax <= 40,
     vEco.vues + '/' + vEco.n + ' ouvertes, ' + vEco.fautes + ' faute(s), au plus ' + vEco.partMax + ' % d’un voisin'
       + (vEco.detail.length ? ' (' + vEco.detail.join(' · ') + ')' : ''));
  await p.evaluate(REPOS);
  /* G-10 — LA BULLE SE SURVOLE ; ÉCHAP LA FERME SOUS LE POINTEUR. */
  await p.mouse.move(2, 890);
  await marquer(p, G.eco.cible, 2, 'en');
  await p.waitForTimeout(400);
  c = await centre(p, 'en');
  await p.mouse.move(c.x, c.y, { steps: 4 });
  await p.waitForTimeout(500);
  const s10 = await p.evaluate(VUE, [G.eco.bulle, 'en']);
  let surBulle = { visible: false }, apres150 = { visible: false }, apres500 = { visible: true };
  if (s10.visible) {
    const bx = (s10.rect[0] + s10.rect[2]) / 2, by = (s10.rect[1] + s10.rect[3]) / 2;
    await p.mouse.move(bx, by, { steps: 8 });
    await p.waitForTimeout(600);
    surBulle = await p.evaluate(VUE, [G.eco.bulle, 'en']);
    /* SORTIR À L'HORIZONTALE, à la hauteur de la bulle : vers le bas, le
       pointeur repasserait sur le nœud, et la grâce repartirait de là. */
    await p.mouse.move(120, by, { steps: 2 });
    await p.waitForTimeout(150);
    apres150 = await p.evaluate(VUE, [G.eco.bulle, 'en']);
    await p.waitForTimeout(350);
    apres500 = await p.evaluate(VUE, [G.eco.bulle, 'en']);
  }
  ok('G-10 survolable', 'G-10 le pointeur amené sur la bulle la garde ouverte ; sortie des deux : ouverte à 150 ms, fermée à 500 ms',
     s10.visible && surBulle.visible && apres150.visible && !apres500.visible,
     'survol ' + (s10.visible ? 'ouverte' : 'fermée') + ' ; sur la bulle ' + (surBulle.visible ? 'ouverte' : 'FERMÉE') + ' ; sortie : 150 ms '
       + (apres150.visible ? 'ouverte' : 'fermée') + ', 500 ms ' + (apres500.visible ? 'OUVERTE' : 'fermée'));
  await p.mouse.move(c.x, c.y, { steps: 4 });
  await p.waitForTimeout(500);
  const avEchap = await p.evaluate(VUE, [G.eco.bulle, 'en']);
  await p.keyboard.press('Escape');
  await p.waitForTimeout(300);
  const apEchap = await p.evaluate(VUE, [G.eco.bulle, 'en']);
  for (const d of [[6, 3], [-5, 4], [4, -3]]) { await p.mouse.move(c.x + d[0], c.y + d[1], { steps: 2 }); await p.waitForTimeout(120); }
  await p.waitForTimeout(300);
  const reste = await p.evaluate(VUE, [G.eco.bulle, 'en']);
  await p.mouse.move(2, 890, { steps: 3 });
  await p.waitForTimeout(500);
  await p.mouse.move(c.x, c.y, { steps: 4 });
  await p.waitForTimeout(500);
  const retour = await p.evaluate(VUE, [G.eco.bulle, 'en']);
  ok('G-10 Échap', 'G-10 Échap ferme la bulle ; elle ne se rouvre pas tant que le pointeur reste sur le nœud (témoin : elle se rouvre au retour)',
     avEchap.visible && !apEchap.visible && !reste.visible && retour.visible,
     'avant ' + (avEchap.visible ? 'ouverte' : 'fermée') + ', Échap ' + (apEchap.visible ? 'OUVERTE' : 'fermée') + ', pointeur resté ' + (reste.visible ? 'ROUVERTE' : 'fermée')
       + ', retour ' + (retour.visible ? 'ouverte' : 'fermée'));
  await p.mouse.move(2, 890);
  await ctx.close();
  }
  await nav.close();

  ok(null, 'aucune erreur JavaScript dans les pages', erreurs.length === 0, erreurs.slice(0, 2).join(' | '));
  ok(null, 'aucun refus du limiteur (sinon la recette a mesuré des 429)', refus.length === 0, refus.slice(0, 2).join(' '));

  /* LES DEUX COLONNES. */
  console.log('\n══ Avant (be93b64) / après ══');
  for (const l of lignes) {
    console.log((l.ok ? '  OK ' : '  KO ') + l.cle.padEnd(26) + ' | avant : ' + String(l.avant).slice(0, 80).padEnd(80) + ' | après : ' + l.apres.slice(0, 140));
  }
  if (process.env.SORTIE) fs.writeFileSync(process.env.SORTIE, JSON.stringify(MESURES, null, 1));
  console.log('\n' + (n - ko) + '/' + n + ' contrôles verts' + (ko ? ' — ' + ko + ' en échec' : ''));
  process.exit(ko ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
