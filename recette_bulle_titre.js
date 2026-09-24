/* RECETTE — LES `title` NATIFS SE LISENT AU DOIGT ET AU CLAVIER (/bulle-titre.js)
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LE DÉFAUT : un `title` ne s'affiche qu'à la souris posée dessus. Sur un
 * téléphone, un appui sur une pastille « P1 », un bloc de score, une ligne du
 * menu n'affiche rien ; un appui long sur une ligne du menu en SÉLECTIONNE le
 * texte. Au clavier, la tabulation atteint la ligne du menu et rien ne
 * s'affiche. Plus de quatre mille `title` dans Sentinel.
 *
 * LES CONTRÔLES T-1 À T-18 de la spécification (§6, lot 2), joués sur le vrai
 * navigateur, dans trois contextes :
 *   · « tactile »  : Pixel 7 (412 px) — gestes envoyés par le protocole de
 *                    débogage (`Input.dispatchTouchEvent`), et non fabriqués
 *                    dans la page : c'est le navigateur qui décide qu'un
 *                    geste défile, annule le pointeur, émet `contextmenu` ;
 *   · « tablette » : Galaxy Tab S4 à l'horizontale (1138 px), tactile. LE
 *                    MENU N'EXISTE PAS AU TÉLÉPHONE — mesuré : `#sb` est
 *                    translaté hors de l'écran sous 860 px, et le bouton
 *                    `#sb-toggle` que la feuille prévoit n'est dans aucune
 *                    page. Les contrôles « ligne du menu au doigt » se jouent
 *                    donc là où le menu se touche : sur une tablette ;
 *   · « poste »    : 1280 × 900, souris et clavier.
 *
 * « VISIBLE » VEUT DIRE : `#bulle-titre` sans `hidden`, son texte ÉGAL au
 * `title` de l'élément, son rectangle dans la fenêtre visuelle à 8 px près.
 *
 * CHAQUE « RIEN NE S'OUVRE » A SON TÉMOIN. Un contrôle qui attend « aucune
 * bulle » passerait aussi sur un script absent ou éteint : il ne compte que si
 * un élément voisin, dans le même contexte, S'OUVRE. C'est le défaut que ce
 * dépôt traque — une règle qui passe pour une raison sans rapport.
 *
 * LE LIMITEUR : un chargement de Sentinel coûte une centaine de requêtes pour
 * 120 par minute. Trois chargements, séparés de ATTENTE ms (62 s par défaut),
 * sur un serveur NEUF.
 */
const { chromium, devices } = require('/opt/node22/lib/node_modules/playwright');
const { execSync } = require('child_process');
const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
const ATTENTE = Number(process.env.ATTENTE || 62000);
const DEPOT = process.env.DEPOT || __dirname;
/* Pour la mise au point : SECTIONS=A,C ne joue que ces contextes. */
const SECTIONS = (process.env.SECTIONS || 'A,B,C,D,T').split(',');
const joue = (s) => SECTIONS.indexOf(s) >= 0;
let ko = 0, n = 0;
const ok = (t, c, d) => { n++; if (!c) ko++;
  console.log((c ? '  OK   ' : '  KO   ') + t + (d ? ' — ' + d : '')); };
/* CE QUI DÉPEND DU LOT 3 (noms des boutons à glyphe, boutons d'aide) : relevé,
   dit, mais NON COMPTÉ — le lot 2 ne peut pas le rendre vrai. */
const lot3 = (t, d) => console.log('  --   [lot 3] ' + t + (d ? ' — ' + d : ''));
const pause = (ms) => new Promise(r => setTimeout(r, ms));

const FURTIF = (ctx) => ctx.addInitScript(() => {
  Object.defineProperty(navigator, 'webdriver', { get: () => false });
  Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
  Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
});
/* LES COMPTEURS, posés AVANT la page : chaque passage de `#bulle-titre` de
   caché à visible, chaque `contextmenu` (lu en remontée, après le script),
   chaque `selectionchange`. */
const COMPTEURS = (ctx) => ctx.addInitScript(() => {
  window.__ouvertures = 0; window.__menus = []; window.__selections = 0; window.__clics = 0;
  /* UNE OUVERTURE, C'EST UN PASSAGE DE CACHÉ À VISIBLE — pas un
     enregistrement de mutation : réécrire `hidden` à l'identique en produit
     un aussi. Un premier compteur en comptait deux pour une. */
  let visibleAvant = false;
  new MutationObserver(rs => {
    const b = rs.map(r => r.target).find(t => t.id === 'bulle-titre');
    if (!b) return;
    const vis = !b.hasAttribute('hidden');
    if (vis && !visibleAvant) window.__ouvertures++;
    visibleAvant = vis;
  }).observe(document, { subtree: true, attributes: true, attributeFilter: ['hidden'] });
  window.addEventListener('contextmenu', e => window.__menus.push({ annule: e.defaultPrevented, type: e.pointerType }));
  document.addEventListener('selectionchange', () => { window.__selections++; });
});

/* L'ÉTAT DE LA BULLE, rapporté à l'élément marqué `data-recette`. */
const VUE = (marque) => {
  const b = document.getElementById('bulle-titre');
  const a = marque ? document.querySelector('[data-recette="' + marque + '"]') : null;
  if (!b) return { existe: false, visible: false };
  const cs = getComputedStyle(b), r = b.getBoundingClientRect();
  const vv = window.visualViewport || { offsetLeft: 0, offsetTop: 0, width: innerWidth, height: innerHeight };
  const ra = a ? a.getBoundingClientRect() : null;
  return {
    existe: true, visible: !b.hidden && cs.display !== 'none',
    texte: b.textContent, title: a ? a.getAttribute('title') : null,
    ariaHidden: b.getAttribute('aria-hidden'), z: parseInt(cs.zIndex, 10) || 0,
    rect: [r.left, r.top, r.right, r.bottom].map(Math.round),
    dansVV: r.left >= vv.offsetLeft - 8 && r.top >= vv.offsetTop - 8
            && r.right <= vv.offsetLeft + vv.width + 8 && r.bottom <= vv.offsetTop + vv.height + 8,
    droiteVV: Math.round(vv.offsetLeft + vv.width), largeurVV: Math.round(vv.width), innerWidth,
    croise: !!ra && r.left < ra.right && ra.left < r.right && r.top < ra.bottom && ra.top < r.bottom,
    ancre: ra ? [ra.left, ra.top, ra.right, ra.bottom].map(Math.round) : null,
  };
};
const visible = (v) => !!v && v.visible && v.texte === v.title && v.dansVV;
const dit = (v) => !v.existe ? '#bulle-titre absent'
  : (v.visible ? 'visible « ' + (v.texte || '').slice(0, 40) + ' »' + (v.dansVV ? '' : ' HORS fenêtre visuelle') : 'cachée');

/* MARQUER un élément, l'amener au centre de l'écran, rendre son centre. */
async function marquer(p, sel, marque, filtre) {
  return p.evaluate(([sel, marque, filtre]) => {
    const vis = e => { const q = e.getBoundingClientRect(); return q.width > 0 && q.height > 0; };
    let els = [...document.querySelectorAll(sel)].filter(vis);
    if (filtre === 'droite') els.sort((a, b) => b.getBoundingClientRect().right - a.getBoundingClientRect().right);
    if (filtre === 'pasOn') els = els.filter(e => !e.classList.contains('on'));
    const el = els[0];
    if (!el) return null;
    document.querySelectorAll('[data-recette="' + marque + '"]').forEach(e => e.removeAttribute('data-recette'));
    el.setAttribute('data-recette', marque);
    el.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'instant' });
    return true;
  }, [sel, marque, filtre || '']);
}
/* LE CENTRE, EN COORDONNÉES D'ÉCRAN. Le protocole de débogage vise la
   fenêtre VISUELLE ; `getBoundingClientRect` parle de la fenêtre de MISE EN
   PAGE. Au Pixel 7, la page est rendue à l'échelle 412/462 : sans la
   conversion, l'appui tombait sur la pastille VOISINE — mesuré, c'est ce
   qu'un premier essai de cette recette a fait. Et l'élément touché doit
   être le bon : on le vérifie au point visé. */
async function centre(p, marque) {
  const c = await p.evaluate((m) => {
    const e = document.querySelector('[data-recette="' + m + '"]'), r = e.getBoundingClientRect();
    const vv = window.visualViewport || { offsetLeft: 0, offsetTop: 0, scale: 1 };
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    const vise = document.elementFromPoint(cx, cy);
    return { x: Math.round((cx - vv.offsetLeft) * (vv.scale || 1)), y: Math.round((cy - vv.offsetTop) * (vv.scale || 1)),
             touche: !!vise && (e.contains(vise) || vise === e || e.tagName === 'IFRAME'),
             vise: vise ? vise.tagName + '.' + String(vise.className).slice(0, 30) : null };
  }, marque);
  if (!c.touche) console.log('  ..   le point visé sur « ' + marque + ' » tombe sur ' + c.vise);
  return c;
}
/* LES GESTES. */
const APPUI = async (p, cdp, m) => {
  const { x, y } = await centre(p, m);
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] });
  await p.waitForTimeout(60);
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  await p.waitForTimeout(400);
};
/* L'APPUI LONG BRUT : ce geste n'émet pas `contextmenu` — c'est lui qui
   prouve le minuteur (le chemin d'iOS). Relevé PENDANT l'appui. */
const APPUI_LONG_BRUT = async (p, cdp, m) => {
  const { x, y } = await centre(p, m);
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] });
  await p.waitForTimeout(620);
  const pendant = await p.evaluate(VUE, m);
  await p.waitForTimeout(80);
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  await p.waitForTimeout(500);
  return pendant;
};
/* L'APPUI LONG ANDROID : la souris convertie en toucher par le navigateur,
   tenue 1 s — son détecteur de gestes émet `contextmenu`. */
/* LE PIÈGE MESURÉ : sous cette émulation, `mousePressed` ne rend la main
   qu'au relâcher. L'attendre, c'est ne jamais relâcher. On l'envoie sans
   l'attendre, et le relâcher une seconde plus tard. */
const APPUI_LONG_ANDROID = async (p, cdp, m) => {
  const { x, y } = await centre(p, m);
  const borne = (pr) => Promise.race([pr.catch(() => 'erreur'), pause(4000).then(() => 'délai')]);
  await cdp.send('Emulation.setEmitTouchEventsForMouse', { enabled: true, configuration: 'mobile' });
  await borne(cdp.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y }));
  const presse = borne(cdp.send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 }));
  await p.waitForTimeout(1000);
  await borne(cdp.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 }));
  await presse;
  await p.waitForTimeout(500);
  await cdp.send('Emulation.setEmitTouchEventsForMouse', { enabled: false });
};
/* LE BALAYAGE : un contact, dix déplacements sur 200 px, un relâcher. Rend le
   défilement de la page et le plus grand nombre d'ouvertures vu en route. */
const BALAYER = async (p, cdp, m) => {
  const { x, y } = await centre(p, m);
  const y0 = await p.evaluate(() => window.scrollY);
  const o0 = await p.evaluate(() => window.__ouvertures);
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] });
  for (let i = 1; i <= 10; i++) {
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x, y: y - 20 * i }] });
    await p.waitForTimeout(16);
  }
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  await p.waitForTimeout(700);
  return { defile: Math.round((await p.evaluate(() => window.scrollY)) - y0),
           ouvertures: (await p.evaluate(() => window.__ouvertures)) - o0 };
};
/* TABULER JUSQU'À un élément : on donne le focus à celui qui le PRÉCÈDE dans
   l'ordre de tabulation, puis une vraie touche Tab. Le focus qui compte est
   celui de la touche. */
const TABULABLE = 'a[href],button:not([disabled]),input:not([disabled]),select,textarea,[tabindex]';
async function tabulerVers(p, marque) {
  const ok = await p.evaluate(([m, T]) => {
    const vis = e => { const q = e.getBoundingClientRect(); return q.width > 0 && q.height > 0; };
    const t = [...document.querySelectorAll(T)].filter(e => e.tabIndex >= 0 && vis(e));
    const i = t.indexOf(document.querySelector('[data-recette="' + m + '"]'));
    if (i < 1) return false;
    t[i - 1].focus();
    return true;
  }, [marque, TABULABLE]);
  if (!ok) return false;
  await p.waitForTimeout(1100);
  await p.keyboard.press('Tab');
  return p.evaluate(m => document.activeElement === document.querySelector('[data-recette="' + m + '"]'), marque);
}
const ouvertures = (p) => p.evaluate(() => window.__ouvertures);
async function aller(p, page) { await p.evaluate(pg => window.go(pg), page); await p.waitForTimeout(1500); }
async function nouveau(nav, options) {
  const ctx = await nav.newContext(options);
  await FURTIF(ctx); await COMPTEURS(ctx);
  const p = await ctx.newPage();
  p.on('pageerror', e => erreurs.push(String(e).slice(0, 160)));
  p.on('response', r => { if (r.status() === 429) refus.push(r.url()); });
  const cdp = await ctx.newCDPSession(p);
  return { ctx, p, cdp };
}
async function sentinel(p, ecran) {
  await p.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'domcontentloaded' });
  const rep = await p.goto(BASE + '/sentinel?goto=' + ecran, { waitUntil: 'domcontentloaded' });
  await p.waitForFunction(() => !!document.getElementById('css-bulle-ouverte'), null, { timeout: 15000 }).catch(() => {});
  await p.waitForTimeout(3000);
  await sansBandeau(p);
  return rep && rep.status();
}
/* LE BANDEAU DES COOKIES recouvre le bas de l'écran et intercepte l'appui :
   il n'est pas le sujet de cette recette. */
async function sansBandeau(p) {
  await p.evaluate(() => { const b = document.getElementById('ck-banner'); if (b) b.classList.remove('show'); });
}
const erreurs = [], refus = [];

(async () => {
  const nav = await chromium.launch();

  let ctx, p, cdp, v, o0, c, premier = true;
  const attendre = async () => { if (!premier) await pause(ATTENTE); premier = false; };
  // ══ A. TACTILE — Pixel 7 ═══════════════════════════════════════════════
  if (joue('A')) {
  await attendre();
  console.log('\n══ A. Tactile (Pixel 7) ══');
  ({ ctx, p, cdp } = await nouveau(nav, { ...devices['Pixel 7'], hasTouch: true, isMobile: true }));
  ok('la page répond', (await sentinel(p, 'audit-ia-act')) === 200);
  ok('le contexte est bien tactile', await p.evaluate(() => matchMedia('(hover:none) and (pointer:coarse)').matches));
  const script = await p.evaluate(() => ({ bulle: !!document.getElementById('bulle-titre'),
    css: !!document.getElementById('css-bulle-titre'), api: !!window.bulleTitre }));
  ok('/bulle-titre.js est chargé (bulle, feuille, API)', script.bulle && script.css && script.api, JSON.stringify(script));

  /* T-2 — L'APPUI SUR UNE PASTILLE DE PRIORITÉ. */
  console.log('\n  T-2 — appui sur span.audit-item-prio');
  await marquer(p, '#p-audit-ia-act .audit-item-prio[title]', 'prio');
  await p.waitForTimeout(300);
  await APPUI(p, cdp, 'prio');
  v = await p.evaluate(VUE, 'prio');
  ok('T-2 l’appui OUVRE la bulle, texte égal au title, dans la fenêtre visuelle', visible(v), dit(v));
  ok('T-2 …muette pour les technologies d’assistance (aria-hidden="true")', v.ariaHidden === 'true', 'aria-hidden=' + v.ariaHidden);
  ok('T-2 …sans recouvrir la pastille', v.existe && !v.croise, v.existe ? 'bulle ' + v.rect + ' / pastille ' + v.ancre : '');
  await APPUI(p, cdp, 'prio');
  v = await p.evaluate(VUE, 'prio');
  ok('T-2 un second appui la CACHE', v.existe && !v.visible, dit(v));
  await APPUI(p, cdp, 'prio');
  const rouverte = visible(await p.evaluate(VUE, 'prio'));
  await marquer(p, '#p-audit-ia-act .page-lead, #p-audit-ia-act h1', 'ailleurs');
  await p.waitForTimeout(300);
  await APPUI(p, cdp, 'ailleurs');
  v = await p.evaluate(VUE, 'prio');
  ok('T-2 un appui AILLEURS la cache', rouverte && v.existe && !v.visible, 'rouverte avant : ' + rouverte + ', après : ' + dit(v));

  /* T-16 — LE `title` CHANGÉ PENDANT LA LECTURE. Le bouton d'enregistrement
     FRIA (`saveBtn.title = …`) n'existe qu'avec un système enregistré ; le
     même cas est joué ici sur la pastille ouverte. */
  console.log('\n  T-16 — title changé pendant l’ouverture');
  /* La pastille est ramenée à l'écran : l'appui « ailleurs » a fait défiler
     la page, et un appui hors écran ne toucherait rien — mesuré. */
  await marquer(p, '#p-audit-ia-act .audit-item-prio[title]', 'prio');
  await p.waitForTimeout(300);
  await APPUI(p, cdp, 'prio');
  const t16 = await p.evaluate(async () => {
    const a = document.querySelector('[data-recette="prio"]'), b = document.getElementById('bulle-titre');
    if (!b || b.hidden) return { ouverte: false };
    const avant = a.title, neuf = 'Titre réécrit par la recette pendant la lecture';
    const t0 = performance.now(); a.title = neuf;
    while (performance.now() - t0 < 1000 && b.textContent !== neuf) await new Promise(r => requestAnimationFrame(r));
    const ms = Math.round(performance.now() - t0), texte = b.textContent;
    a.title = avant;
    return { ouverte: true, ms, a_jour: texte === neuf };
  });
  ok('T-16 le texte de la bulle suit le title réécrit, en 300 ms au plus', t16.ouverte && t16.a_jour && t16.ms <= 300,
     t16.ouverte ? (t16.a_jour ? t16.ms + ' ms' : 'jamais mis à jour') : 'bulle non ouverte');
  await p.evaluate(() => window.bulleTitre && window.bulleTitre.fermer());

  /* T-3 — UN BALAYAGE COMMENCÉ SUR UN ÉLÉMENT INERTE À `title`. */
  /* LE BLOC DE SCORE N'A PLUS DE `title` DEPUIS LE LOT 3 : son explication
     est passée dans un bouton d'aide (recette_complements.js, C-4). Le
     balayage part donc d'une pastille de priorité — un élément inerte à
     `title`, ce que ce contrôle éprouve. */
  console.log('\n  T-3 — balayage commencé sur span.audit-item-prio');
  await marquer(p, '#p-audit-ia-act .audit-item-prio[title]', 'kpi');
  await p.waitForTimeout(400);
  const b3 = await BALAYER(p, cdp, 'kpi');
  v = await p.evaluate(VUE, 'kpi');
  ok('T-3 le geste est un vrai balayage : la page a défilé', b3.defile > 50, b3.defile + ' px');
  ok('T-3 aucune bulle ouverte, ni en route ni à la fin', b3.ouvertures === 0 && !v.visible,
     b3.ouvertures + ' ouverture(s), ' + dit(v));
  await APPUI(p, cdp, 'kpi');
  v = await p.evaluate(VUE, 'kpi');
  ok('T-3 témoin : la même pastille, appuyée, S’OUVRE', visible(v), dit(v));
  await p.evaluate(() => window.bulleTitre && window.bulleTitre.fermer());

  /* T-6 — L'APPUI COURT SUR UN BOUTON À `title` : son action, pas de bulle. */
  console.log('\n  T-6 — appui court sur un button[title]');
  await marquer(p, '#p-audit-ia-act .page-guide-btn[title]', 'bouton');
  await p.evaluate(() => { const b = document.querySelector('[data-recette="bouton"]');
    window.__clicsBouton = 0; b.addEventListener('click', () => { window.__clicsBouton++; }); });
  await p.waitForTimeout(300);
  o0 = await ouvertures(p);
  await APPUI(p, cdp, 'bouton');
  await p.waitForTimeout(300);
  const c6 = await p.evaluate(() => window.__clicsBouton);
  v = await p.evaluate(VUE, 'bouton');
  ok('T-6 l’action a lieu : un clic, un seul', c6 === 1, c6 + ' clic(s)');
  ok('T-6 la bulle reste cachée', !v.visible && (await ouvertures(p)) === o0, dit(v));
  await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  await p.evaluate(() => document.querySelectorAll('.mat-modal.on,.pg-guide.on,[class*="guide"].on').forEach(e => e.classList.remove('on')));
  const pendant6 = await APPUI_LONG_BRUT(p, cdp, 'bouton');
  const c6b = await p.evaluate(() => window.__clicsBouton);
  ok('T-6 témoin : le même bouton, tenu 700 ms, ouvre sa bulle et n’agit pas', visible(pendant6) && c6b === 1,
     dit(pendant6) + ', ' + (c6b - 1) + ' clic(s) de plus');
  await p.evaluate(() => window.bulleTitre && window.bulleTitre.fermer());
  await p.evaluate(() => document.querySelectorAll('.mat-modal.on,.pg-guide.on,[class*="guide"].on').forEach(e => e.classList.remove('on')));

  /* T-7 — UN LIEN EUR-LEX : il garde son menu. */
  console.log('\n  T-7 — appui long sur a[href][title] (EUR-Lex)');
  await aller(p, 'simulateur');
  await marquer(p, '#p-simulateur a.legal-ref-link[title][href*="eur-lex"]', 'lien');
  await p.waitForTimeout(300);
  await p.evaluate(() => { window.__menus = []; });
  o0 = await ouvertures(p);
  await APPUI_LONG_ANDROID(p, cdp, 'lien');
  const m7 = await p.evaluate(() => window.__menus);
  v = await p.evaluate(VUE, 'lien');
  ok('T-7 le navigateur a bien émis contextmenu au doigt', m7.length > 0, JSON.stringify(m7));
  ok('T-7 contextmenu N’EST PAS annulé : le menu du lien est conservé', m7.length > 0 && m7.every(m => !m.annule), JSON.stringify(m7));
  ok('T-7 la bulle reste cachée', !v.visible && (await ouvertures(p)) === o0, dit(v));
  /* LE TÉMOIN (revue de conformité, constat 3) : sans lui, les trois
     contrôles ci-dessus passaient aussi sur le code d'avant — un lien sans
     script n'a pas de bulle non plus. Dans ce même contexte, le MÊME lien,
     atteint par Tab, a la sienne : il est éligible, c'est le geste du doigt
     qui ne l'ouvre pas. */
  const t7tab = await tabulerVers(p, 'lien');
  await p.waitForTimeout(650);
  v = await p.evaluate(VUE, 'lien');
  ok('T-7 témoin : le même lien, atteint par Tab, a sa bulle', t7tab && visible(v), (t7tab ? '' : 'Tab n’a pas atteint le lien ; ') + dit(v));
  await p.evaluate(() => window.bulleTitre && window.bulleTitre.fermer());

  /* T-15 — LA FENÊTRE VISUELLE PLUS ÉTROITE QUE LA MISE EN PAGE. */
  for (const [ecran, sel] of [['maturite', '#p-maturite .mat-sector-btn[title]'],
                              ['pricing', '#p-pricing button[title][onclick^="pricingSetEstim"]']]) {
    console.log('\n  T-15 — ' + ecran + ' : élément le plus à droite');
    await aller(p, ecran);
    await marquer(p, sel, 'droite-' + ecran, 'droite');
    await p.waitForTimeout(300);
    const pendant = await APPUI_LONG_BRUT(p, cdp, 'droite-' + ecran);
    ok('T-15 ' + ecran + ' : bulle ouverte, bord droit ≤ bord de la fenêtre visuelle − 8',
       visible(pendant) && pendant.rect[2] <= pendant.droiteVV - 8,
       pendant.existe ? 'innerWidth ' + pendant.innerWidth + ', fenêtre visuelle ' + pendant.largeurVV
         + ', bord droit de la bulle ' + pendant.rect[2] + ' — ' + dit(pendant) : '#bulle-titre absent');
    await p.evaluate(() => window.bulleTitre && window.bulleTitre.fermer());
  }

  /* T-17 (1) — UN IFRAME À `title` : ni appui, ni appui long.
     CE QUE CE CONTRÔLE PROUVE, ET CE QU'IL NE PROUVE PAS (revue de
     conformité, constat 8). « Aucune ouverture » passait aussi sur un
     script sans exclusion d'IFRAME : le geste va au document DE l'iframe,
     jamais au parent — aucun `pointerdown` n'y arrive. L'exclusion du
     script n'est donc qu'un filet ; ce qu'on mesure ici, c'est que le geste
     n'atteint pas le parent, avec un témoin : le même relevé compte bien
     un appui fait sur la page parente. */
  console.log('\n  T-17 — iframe[title]');
  await aller(p, 'pan-sia');
  const f17 = await marquer(p, '#pan-sia-iframe[title]', 'iframe');
  await p.waitForTimeout(800);
  await p.evaluate(() => { window.__evParent = 0;
    ['pointerdown', 'pointerup', 'contextmenu'].forEach(t => document.addEventListener(t, () => { window.__evParent++; }, true)); });
  o0 = await ouvertures(p);
  if (f17) { await APPUI(p, cdp, 'iframe'); await APPUI_LONG_BRUT(p, cdp, 'iframe'); }
  const ev17 = await p.evaluate(() => window.__evParent);
  v = await p.evaluate(VUE, 'iframe');
  ok('T-17 iframe[title] : appui et appui long n’atteignent PAS le document parent (0 événement), aucune ouverture',
     !!f17 && ev17 === 0 && (await ouvertures(p)) === o0 && !v.visible,
     f17 ? ev17 + ' événement(s) reçu(s) par le parent, ' + dit(v) : 'iframe introuvable');
  const t17 = await marquer(p, '#p-pan-sia h1, #p-pan-sia .page-h, #p-pan-sia .page-lead', 'parent17');
  if (t17) await APPUI(p, cdp, 'parent17');
  const ev17t = await p.evaluate(() => window.__evParent);
  ok('T-17 témoin : un appui sur la page parente, lui, est compté', !!t17 && ev17t >= 2, ev17t + ' événement(s)');
  await ctx.close();
  }

  // ══ B. TABLETTE — le menu au doigt ═════════════════════════════════════
  if (joue('B')) {
  await attendre();
  console.log('\n══ B. Tablette tactile (Galaxy Tab S4, horizontale) — le menu au doigt ══');
  ({ ctx, p, cdp } = await nouveau(nav, { ...devices['Galaxy Tab S4 landscape'], hasTouch: true, isMobile: true }));
  ok('la page répond', (await sentinel(p, 'dora-qualifier')) === 200);
  await p.waitForSelector('.sb-item .rail-puce', { timeout: 15000 }).catch(() => {});
  ok('le menu est à l’écran', await p.evaluate(() => document.getElementById('sb').getBoundingClientRect().right > 100));

  /* T-4 — L'APPUI LONG BRUT sur une ligne du menu. */
  console.log('\n  T-4 — appui long brut de 700 ms sur .sb-item[title]');
  await marquer(p, '#sb .sb-item[title][role=button]', 'ligne', 'pasOn');
  const avant4 = await p.evaluate(() => ({ ecran: (document.querySelector('.page.on') || {}).id,
    on: [...document.querySelectorAll('.sb-item.on')].map(e => e.textContent.trim().slice(0, 20)).join('|') }));
  await p.waitForTimeout(300);
  const pendant4 = await APPUI_LONG_BRUT(p, cdp, 'ligne');
  const apres4 = await p.evaluate(() => ({ ecran: (document.querySelector('.page.on') || {}).id,
    on: [...document.querySelectorAll('.sb-item.on')].map(e => e.textContent.trim().slice(0, 20)).join('|') }));
  ok('T-4 la bulle est visible PENDANT l’appui (minuteur de 500 ms)', visible(pendant4), dit(pendant4));
  ok('T-4 …à droite du menu, sans recouvrir la ligne', pendant4.existe && !pendant4.croise, pendant4.existe ? 'bulle ' + pendant4.rect + ' / ligne ' + pendant4.ancre : '');
  ok('T-4 l’écran actif est inchangé après le relâcher (clic avalé)', apres4.ecran === avant4.ecran, avant4.ecran + ' → ' + apres4.ecran);
  ok('T-4 aucune ligne .sb-item.on n’a changé', apres4.on === avant4.on, avant4.on + ' → ' + apres4.on);
  await p.evaluate(() => window.bulleTitre && window.bulleTitre.fermer());

  /* T-5 — L'APPUI LONG ANDROID sur une ligne du menu. */
  console.log('\n  T-5 — appui long Android sur .sb-item[title]');
  await marquer(p, '#sb .sb-item[title][role=button]', 'ligne5', 'pasOn');
  await p.waitForTimeout(300);
  await p.evaluate(() => { window.__menus = []; window.__selections = 0; getSelection().removeAllRanges(); });
  await p.waitForTimeout(200);
  await p.evaluate(() => { window.__selections = 0; });
  o0 = await ouvertures(p);
  const avant5 = await p.evaluate(() => (document.querySelector('.page.on') || {}).id);
  await APPUI_LONG_ANDROID(p, cdp, 'ligne5');
  const r5 = await p.evaluate(() => ({ menus: window.__menus, selections: window.__selections,
    selection: String(getSelection()), ecran: (document.querySelector('.page.on') || {}).id }));
  v = await p.evaluate(VUE, 'ligne5');
  ok('T-5 contextmenu est émis au doigt… et ANNULÉ', r5.menus.length > 0 && r5.menus.every(m => m.annule), JSON.stringify(r5.menus));
  ok('T-5 une seule ouverture comptée, bulle visible', (await ouvertures(p)) - o0 === 1 && visible(v),
     ((await ouvertures(p)) - o0) + ' ouverture(s), ' + dit(v));
  /* LA SÉLECTION NE SE MESURE PAS SUR LA LIGNE DU MENU (revue de
     conformité, constat 2) : `.sb-item` porte déjà `user-select:none` dans
     la feuille de Sentinel — « 0 selectionchange » y passait sur le code
     d'avant. Elle se mesure ci-dessous, sur un interactif sélectionnable. */
  console.log('  ..   T-5 (ligne du menu) sélection relevée pour mémoire, non comptée : ' + r5.selections
              + ' selectionchange, « ' + r5.selection.slice(0, 30) + ' » — la ligne est déjà en user-select:none');
  ok('T-5 l’écran actif est inchangé', r5.ecran === avant5, avant5 + ' → ' + r5.ecran);
  await p.evaluate(() => window.bulleTitre && window.bulleTitre.fermer());

  /* T-5 (sélection) — UN INTERACTIF SÉLECTIONNABLE : un <div> au curseur
     `pointer` qui écoute `click` sans `onclick`, que la feuille injectée ne
     couvre pas — c'est l'annulation de `selectstart` qui y empêche la
     sélection. Le témoin, dans le même contexte : le même <div> SANS
     `title` émet bien un `selectionchange` sous le même geste. Aucun
     élément de ce genre n'est à l'écran aujourd'hui (relevé sur six écrans) :
     la recette le pose. */
  console.log('\n  T-5 (sélection) — appui long Android sur un <div> cliquable sélectionnable');
  await p.evaluate(() => {
    const pg = document.querySelector('.page.on');
    for (const [id, titre] of [['recette-carte', 'Carte posée par la recette : un <div> qui écoute le clic'], ['recette-carte-temoin', null]]) {
      const d = document.createElement('div'); d.id = id; d.textContent = 'Carte cliquable avec du texte à sélectionner';
      d.style.cssText = 'cursor:pointer;padding:18px;margin:12px 0;background:#eef;font-size:18px';
      if (titre) d.title = titre;
      d.addEventListener('click', () => {});
      pg.insertBefore(d, pg.firstChild);
    }
  });
  const selection5 = async (m) => {
    await marquer(p, '#' + m, m); await p.waitForTimeout(300);
    await p.evaluate(() => { getSelection().removeAllRanges(); window.__menus = []; });
    await p.waitForTimeout(200);
    await p.evaluate(() => { window.__selections = 0; });
    await APPUI_LONG_ANDROID(p, cdp, m);
    return p.evaluate(() => ({ selections: window.__selections, selection: String(getSelection()), menus: window.__menus }));
  };
  const s5t = await selection5('recette-carte-temoin');
  o0 = await ouvertures(p);
  const s5 = await selection5('recette-carte');
  v = await p.evaluate(VUE, 'recette-carte');
  ok('T-5 témoin : le même <div> sans title, tenu, émet un selectionchange', s5t.selections >= 1, s5t.selections + ' selectionchange');
  ok('T-5 le <div> à title, tenu : bulle ouverte, contextmenu annulé', visible(v) && s5.menus.length > 0 && s5.menus.every(m => m.annule),
     dit(v) + ', ' + JSON.stringify(s5.menus));
  ok('T-5 …et AUCUNE sélection : 0 selectionchange, sélection vide', s5.selections === 0 && s5.selection === '',
     s5.selections + ' selectionchange, « ' + s5.selection.slice(0, 30) + ' »');
  await p.evaluate(() => { window.bulleTitre && window.bulleTitre.fermer();
    ['recette-carte', 'recette-carte-temoin'].forEach(id => { const e = document.getElementById(id); if (e) e.remove(); }); });

  /* T-8 — LA PASTILLE DU RAIL DANS UNE LIGNE DU MENU. */
  console.log('\n  T-8 — appui long sur .rail-puce dans .sb-item');
  const m8 = await marquer(p, '#sb .sb-item .rail-puce[data-tooltip]', 'puce');
  await p.waitForTimeout(300);
  o0 = await ouvertures(p);
  const pendant8 = m8 ? await APPUI_LONG_BRUT(p, cdp, 'puce') : { existe: false };
  const r8 = await p.evaluate(() => { const e = document.querySelector('[data-recette="puce"]');
    return e ? { tooltip: e.classList.contains('bulle-ouverte'), title: e.getAttribute('title') } : null; });
  ok('T-8 une pastille du rail est à l’écran', !!m8 && !!r8);
  ok('T-8 seule la bulle data-tooltip de la pastille s’ouvre', !!r8 && r8.tooltip, r8 && ('bulle-ouverte=' + r8.tooltip));
  ok('T-8 #bulle-titre reste caché, pendant et après', !!m8 && !pendant8.visible && (await ouvertures(p)) === o0,
     dit(pendant8) + ', ' + ((await ouvertures(p)) - o0) + ' ouverture(s)');
  ok('T-8 la pastille porte un title VIDE (pas de bulle native héritée de la ligne au poste)', !!r8 && r8.title === '',
     r8 ? 'title=' + JSON.stringify(r8.title) : '');

  /* T-8 bis — LA LIGNE TENUE, PUIS UN APPUI SUR SA PROPRE PASTILLE. LE
     DÉFAUT MESURÉ (revue de robustesse) : la pastille étant DANS la ligne,
     l'appui n'était pas « ailleurs » — deux bulles ouvertes, et deux Échap
     pour tout fermer. Attendu : la seule bulle de la pastille. */
  console.log('\n  T-8 bis — ligne du menu tenue, puis appui sur sa pastille');
  await p.evaluate(() => { window.bulleTitre && window.bulleTitre.fermer(); window.infobulles && window.infobulles.fermer(); });
  const l8 = await p.evaluate(() => { const pu = document.querySelector('[data-recette="puce"]');
    const li = pu && pu.closest('.sb-item[title]'); if (!li) return false;
    const c = [...li.children].find(e => e !== pu && e.getBoundingClientRect().width > 0) || li;
    c.setAttribute('data-recette', 'ligne8'); return true; });
  const tenue8 = l8 ? await APPUI_LONG_BRUT(p, cdp, 'ligne8') : { existe: false };
  if (l8) await APPUI(p, cdp, 'puce');
  const r8b = await p.evaluate(() => { const b = document.getElementById('bulle-titre');
    return { titre: !!b && !b.hidden, tooltip: document.querySelectorAll('.rail-puce.bulle-ouverte').length }; });
  ok('T-8 bis la ligne tenue ouvre sa bulle (le témoin)', l8 && tenue8.visible, dit(tenue8));
  ok('T-8 bis l’appui sur sa pastille ne laisse QU’UNE bulle, celle de la pastille', l8 && r8b.tooltip === 1 && !r8b.titre,
     JSON.stringify(r8b));
  await p.keyboard.press('Escape'); await p.waitForTimeout(200);
  const r8c = await p.evaluate(() => { const b = document.getElementById('bulle-titre');
    return { titre: !!b && !b.hidden, tooltip: document.querySelectorAll('.bulle-ouverte').length }; });
  ok('T-8 bis UN Échap ferme tout', !r8c.titre && r8c.tooltip === 0, JSON.stringify(r8c));
  await ctx.close();
  }

  // ══ C. POSTE — souris et clavier ═══════════════════════════════════════
  if (joue('C')) {
  await attendre();
  console.log('\n══ C. Poste (1280 × 900, souris et clavier) ══');
  ({ ctx, p, cdp } = await nouveau(nav, { viewport: { width: 1280, height: 900 } }));
  ok('la page répond', (await sentinel(p, 'entreprise')) === 200);

  /* T-1 — LA SOURIS N'OUVRE RIEN. */
  console.log('\n  T-1 — survol d’une ligne du menu, puis clic sur un input[title]');
  await marquer(p, '#sb .sb-item[title][role=button]', 'survol', 'pasOn');
  c = await centre(p, 'survol');
  o0 = await ouvertures(p);
  await p.mouse.move(c.x, c.y); await p.waitForTimeout(1200);
  const v1a = await p.evaluate(VUE, 'survol');
  /* LE LOT 3 A RETIRÉ LE `title` DE TOUS LES CHAMPS DE SENTINEL (§3.4 : un
     nom, ou une aide visible). Un champ à `title` reste pourtant possible —
     et l'exclusion du script doit tenir : la recette en pose un, à côté des
     vrais champs de l'écran, s'il n'y en a plus. */
  await p.evaluate(() => {
    if (document.querySelector('#p-entreprise input[title]')) return;
    const vrai = document.getElementById('ent-ent-name');
    const i = document.createElement('input');
    i.id = 'recette-champ-titre'; i.title = 'Champ à title posé par la recette';
    i.setAttribute('aria-label', 'Champ de recette');
    vrai.parentNode.insertBefore(i, vrai);
  });
  await marquer(p, '#p-entreprise input[title]', 'champ');
  c = await centre(p, 'champ');
  await p.mouse.click(c.x, c.y); await p.waitForTimeout(1200);
  const v1b = await p.evaluate(VUE, 'champ');
  const o1 = (await ouvertures(p)) - o0;
  ok('T-1 au survol et au clic d’un champ : aucune bulle, 0 ouverture', !v1a.visible && !v1b.visible && o1 === 0,
     'survol : ' + dit(v1a) + ' ; champ : ' + dit(v1b) + ' ; ' + o1 + ' ouverture(s)');

  /* T-13 (1) — LES ARRÊTS DE TABULATION DE L'AUDIT. */
  const arrets = (ecran) => p.evaluate(([ecran, T]) => {
    const vis = e => { const q = e.getBoundingClientRect(); return q.width > 0 && q.height > 0; };
    return [...document.querySelectorAll('#p-' + ecran + ' :is(' + T + ')')].filter(e => e.tabIndex >= 0 && vis(e)).length;
  }, [ecran, TABULABLE]);
  await aller(p, 'audit-ia-act');
  const t13 = { 'audit-ia-act': await arrets('audit-ia-act') };
  /* LES BOUTONS D'AIDE DU LOT 3 SONT DÉCOMPTÉS. Ils ajoutent six arrêts à
     l'audit, voulus (recette_complements.js les compte) ; sans ce décompte,
     « inchangés » contredisait le lot 3 dès qu'on fournissait T13_AVANT. */
  const aidesT13 = { 'audit-ia-act': await p.evaluate(() => [...document.querySelectorAll('#p-audit-ia-act .aide-titre')]
    .filter(e => { const q = e.getBoundingClientRect(); return q.width > 0 && q.height > 0; }).length) };

  /* T-9 — LA TABULATION JUSQU'À UNE LIGNE DU MENU. */
  console.log('\n  T-9 — Tab jusqu’à un .sb-item, attente de 600 ms');
  await p.mouse.move(640, 890);
  await marquer(p, '#sb .sb-item[title][role=button]', 'tab', 'pasOn');
  const t9 = await tabulerVers(p, 'tab');
  await p.waitForTimeout(600);
  v = await p.evaluate(VUE, 'tab');
  const sbDroite = await p.evaluate(() => Math.round(document.getElementById('sb').getBoundingClientRect().right));
  ok('T-9 le focus est arrivé sur la ligne par une touche Tab', t9);
  ok('T-9 la bulle est visible', visible(v), dit(v));
  ok('T-9 …sans recouvrir la ligne, à droite du menu', v.existe && !v.croise && v.rect[0] >= sbDroite,
     v.existe ? 'bulle ' + v.rect + ', menu jusqu’à ' + sbDroite : '');

  /* T-10 — CINQ TABULATIONS RAPIDES. */
  console.log('\n  T-10 — 5 Tab à 100 ms d’intervalle dans le menu');
  await p.evaluate(() => window.bulleTitre && window.bulleTitre.fermer());
  o0 = await ouvertures(p);
  let inter = 0;
  for (let i = 0; i < 5; i++) {
    await p.keyboard.press('Tab'); await p.waitForTimeout(100);
    inter = Math.max(inter, (await ouvertures(p)) - o0);
  }
  const dernier = await p.evaluate(() => { const a = document.activeElement;
    return { ligne: a.classList.contains('sb-item') && !!a.title, texte: a.textContent.trim().slice(0, 30) }; });
  await p.waitForTimeout(250);
  const a350 = (await ouvertures(p)) - o0;
  await p.waitForTimeout(350);
  const a700 = (await ouvertures(p)) - o0;
  ok('T-10 la cinquième tabulation s’arrête sur une ligne à title', dernier.ligne, dernier.texte);
  ok('T-10 aucune ouverture intermédiaire', inter === 0 && a350 === 0, inter + ' pendant, ' + a350 + ' à +350 ms');
  ok('T-10 une ouverture, 500 ms après la dernière', a700 === 1, a700 + ' ouverture(s) à +700 ms');

  /* T-11 (réel) — ENTRÉE SUR LE BOUTON « GUIDE D'UTILISATION », ATTEINT PAR
     TAB. LE DÉFAUT MESURÉ (revues navigateur et robustesse) : Entrée ouvre
     la fenêtre du guide SANS y déplacer le focus ; la bulle du bouton
     (10060) restait par-dessus la fenêtre (10020), et le premier Échap ne
     fermait qu'elle. La variante de la spécification (focus placé sur le ×)
     est jouée plus bas. */
  console.log('\n  T-11 (réel) — Tab jusqu’au bouton Guide, Entrée');
  await p.evaluate(() => window.bulleTitre && window.bulleTitre.fermer());
  await marquer(p, '#p-audit-ia-act .page-guide-btn[title]', 'guide');
  const t11r = await tabulerVers(p, 'guide');
  await p.waitForTimeout(650);
  const temoin11r = visible(await p.evaluate(VUE, 'guide'));
  ok('T-11 (réel) témoin : le bouton Guide, atteint par Tab, a sa bulle', t11r && temoin11r);
  await p.keyboard.press('Enter');
  await p.waitForTimeout(700);
  const r11r = await p.evaluate(() => ({ modale: !!document.querySelector('#guide-modal.on'),
    focusGarde: document.activeElement === document.querySelector('[data-recette="guide"]') }));
  v = await p.evaluate(VUE, 'guide');
  ok('T-11 (réel) Entrée ouvre la fenêtre, le focus reste sur le bouton', r11r.modale && r11r.focusGarde, JSON.stringify(r11r));
  ok('T-11 (réel) …et la bulle du bouton est CACHÉE, pas par-dessus la fenêtre', r11r.modale && !v.visible, dit(v));
  await p.keyboard.press('Escape'); await p.waitForTimeout(400);
  const e11r = await p.evaluate(() => !!document.querySelector('#guide-modal.on'));
  ok('T-11 (réel) UN Échap ferme la fenêtre', r11r.modale && !e11r, 'fenêtre ' + (e11r ? 'encore ouverte' : 'fermée'));
  await p.evaluate(() => { const m = document.getElementById('guide-modal'); if (m) m.classList.remove('on'); });

  /* T-14 — L'ÉLÉMENT MASQUÉ PAR `go()`. */
  console.log('\n  T-14 — bulle ouverte au clavier, puis go() vers un autre écran');
  await p.evaluate(() => window.bulleTitre && window.bulleTitre.fermer());
  await marquer(p, '#p-audit-ia-act .audit-export-btn[title]', 'masque');
  const t14tab = await tabulerVers(p, 'masque');
  await p.waitForTimeout(650);
  const ouvert14 = visible(await p.evaluate(VUE, 'masque'));
  const r14 = await p.evaluate(async () => {
    const b = document.getElementById('bulle-titre'); const zero = [];
    const t0 = performance.now(); window.go('iso42001');
    while (performance.now() - t0 < 1000 && b && !b.hidden) {
      const r = b.getBoundingClientRect(); if (Math.round(r.left) === 0 && Math.round(r.top) === 0) zero.push(1);
      await new Promise(res => requestAnimationFrame(res));
    }
    return { ms: Math.round(performance.now() - t0), cachee: !b || b.hidden, zero: zero.length };
  });
  ok('T-14 la bulle était ouverte au clavier sur un élément de l’écran', t14tab && ouvert14);
  ok('T-14 cachée en 300 ms au plus après go(), jamais placée à (0,0)', ouvert14 && r14.cachee && r14.ms <= 300 && r14.zero === 0,
     r14.ms + ' ms, ' + r14.zero + ' image(s) à (0,0)');
  await p.waitForTimeout(1500);
  t13['iso42001'] = await arrets('iso42001');
  await aller(p, 'iso27001');
  t13['iso27001'] = await arrets('iso27001');

  /* T-11 — ENTRÉE SUR UN BOUTON QUI OUVRE UNE FENÊTRE ET Y PLACE LE FOCUS. */
  console.log('\n  T-11 / T-12 — la fenêtre modale d’un guide de procédure');
  await aller(p, 'maturite');
  const pose = await p.evaluate(() => {
    if (typeof window.procOpenDoc !== 'function') return 'procOpenDoc absente';
    /* Le bouton qui ouvre la fenêtre ET y place le focus sur le × : la
       gestion du focus qu'une fenêtre modale doit avoir. Aucune de Sentinel
       ne la fait aujourd'hui ; la recette l'écrit. procOpenDoc n'ouvre que
       la fenêtre — la génération par IA attend un bouton jamais appuyé. */
    const b = document.createElement('button');
    b.id = 'recette-ouvre'; b.setAttribute('data-recette', 'ouvre');
    b.title = 'Ouvre la fenêtre du guide de procédure, focus sur sa fermeture';
    b.textContent = 'Ouvrir le guide';
    b.onclick = () => { window.procOpenDoc('01');
      const x = document.querySelector('#proc-modal .mat-modal-close'); if (x) x.focus(); };
    const h = document.querySelector('#p-maturite h1, #p-maturite .page-h');
    h.parentNode.insertBefore(b, h.nextSibling);
    return '';
  });
  ok('T-11 le bouton d’ouverture est posé', pose === '', pose);
  await marquer(p, '#recette-ouvre', 'ouvre');
  const t11tab = await tabulerVers(p, 'ouvre');
  await p.waitForTimeout(650);
  const temoin11 = visible(await p.evaluate(VUE, 'ouvre'));
  ok('T-11 témoin : ce bouton, atteint par Tab, a sa bulle', t11tab && temoin11);
  o0 = await ouvertures(p);
  await p.keyboard.press('Enter');
  await p.waitForTimeout(900);
  const r11 = await p.evaluate(() => ({ modale: !!document.querySelector('#proc-modal.on'),
    focusX: !!document.activeElement && document.activeElement.classList.contains('mat-modal-close'),
    xTitre: (document.querySelector('#proc-modal .mat-modal-close') || {}).title || '' }));
  v = await p.evaluate(VUE, null);
  ok('T-11 Entrée a ouvert la fenêtre et placé le focus sur le ×', r11.modale && r11.focusX, JSON.stringify(r11));
  ok('T-11 AUCUNE bulle sur ce focus programmatique', !v.visible && (await ouvertures(p)) - o0 === 0,
     dit(v) + ' — le × porte pourtant un title informatif aujourd’hui : « ' + r11.xTitre + ' »');

  /* T-12 — TAB JUSQU'AU ×, PUIS UN ÉLÉMENT INFORMATIF DANS LA FENÊTRE ; ÉCHAP. */
  await p.evaluate(() => {
    const corps = document.getElementById('proc-modal-body');
    const b = document.createElement('button');
    b.id = 'recette-info-modale'; b.textContent = 'Détail';
    b.title = 'Explication posée par la recette dans la fenêtre modale';
    corps.insertBefore(b, corps.firstChild);
  });
  await marquer(p, '#proc-modal .mat-modal-close', 'croix');
  const t12x = await tabulerVers(p, 'croix');
  await p.waitForTimeout(650);
  v = await p.evaluate(VUE, 'croix');
  lot3('T-12 le × n’a pas de bulle (title égal au nom)', 'mesuré : ' + (t12x ? dit(v) : 'focus non atteint par Tab')
       + ' — compté, avec son témoin, par recette_complements.js');
  await p.evaluate(() => window.bulleTitre && window.bulleTitre.fermer());
  await marquer(p, '#recette-info-modale', 'info');
  const t12 = await tabulerVers(p, 'info');
  await p.waitForTimeout(650);
  v = await p.evaluate(VUE, 'info');
  ok('T-12 un élément informatif de la fenêtre, atteint par Tab, a sa bulle', t12 && visible(v), dit(v));
  ok('T-12 …au-dessus de la fenêtre (z-index ≥ 10060)', v.existe && v.z >= 10060, 'z-index ' + v.z);
  await p.keyboard.press('Escape'); await p.waitForTimeout(400);
  const e1 = await p.evaluate(() => ({ modale: !!document.querySelector('#proc-modal.on') }));
  v = await p.evaluate(VUE, 'info');
  ok('T-12 le PREMIER Échap cache la bulle', v.existe && !v.visible, dit(v));
  ok('T-12 …et LAISSE la fenêtre ouverte', e1.modale);
  await p.keyboard.press('Escape'); await p.waitForTimeout(400);
  const e2 = await p.evaluate(() => ({ modale: !!document.querySelector('#proc-modal.on') }));
  ok('T-12 le SECOND Échap ferme la fenêtre', e1.modale && !e2.modale, 'ouverte avant : ' + e1.modale + ', après : ' + e2.modale);

  /* T-13 — LES ARRÊTS DE TABULATION : le lot 2 n'en ajoute aucun. */
  console.log('\n  T-13 — arrêts de tabulation');
  console.log('  ..   T-13 relevé : ' + JSON.stringify(t13));
  const t13ref = JSON.parse(process.env.T13_AVANT || 'null');
  if (t13ref) {
    ok('T-13 les arrêts de tabulation sont INCHANGÉS par rapport au code d’avant (boutons d’aide du lot 3 décomptés)',
       Object.keys(t13ref).every(k => t13ref[k] === t13[k] - (aidesT13[k] || 0)),
       'avant ' + JSON.stringify(t13ref) + ', après ' + JSON.stringify(t13) + ', dont boutons d’aide ' + JSON.stringify(aidesT13));
  } else {
    console.log('  ..   T-13 (pas de relevé d’avant fourni par T13_AVANT : comparaison à faire à la main)');
  }
  lot3('T-13 plus 6 boutons d’aide sur audit-ia-act', 'posés par le lot 3, comptés par recette_complements.js');

  /* T-11 (menu) — ENTRÉE SUR UNE LIGNE DU MENU DONT LA BULLE EST OUVERTE AU
     CLAVIER : elle navigue. LE DÉFAUT MESURÉ (revue navigateur) : la ligne
     reste visible et garde le focus, et sa bulle restait sur le nouvel
     écran. */
  console.log('\n  T-11 (menu) — Tab jusqu’à une ligne du menu, Entrée');
  await p.evaluate(() => window.bulleTitre && window.bulleTitre.fermer());
  await marquer(p, '#sb .sb-item[title][role=button]', 'nav', 'pasOn');
  const t11m = await tabulerVers(p, 'nav');
  await p.waitForTimeout(650);
  const temoin11m = visible(await p.evaluate(VUE, 'nav'));
  const pg0 = await p.evaluate(() => (document.querySelector('.page.on') || {}).id);
  await p.keyboard.press('Enter');
  await p.waitForTimeout(1200);
  const pg1 = await p.evaluate(() => (document.querySelector('.page.on') || {}).id);
  v = await p.evaluate(VUE, 'nav');
  ok('T-11 (menu) témoin : la ligne, atteinte par Tab, a sa bulle', t11m && temoin11m);
  ok('T-11 (menu) Entrée a navigué, et la bulle de la ligne est cachée', pg1 !== pg0 && !v.visible, pg0 + ' → ' + pg1 + ', ' + dit(v));
  await ctx.close();
  }

  // ══ D. PANORAMA — ses onglets ont leur propre bulle ═════════════════════
  if (joue('D')) {
  await attendre();
  console.log('\n══ D. Panorama (Pixel 7) ══');
  ({ ctx, p, cdp } = await nouveau(nav, { ...devices['Pixel 7'], hasTouch: true, isMobile: true }));
  await p.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'domcontentloaded' });
  const rp = await p.goto(BASE + '/panorama', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(4000);
  await sansBandeau(p);
  ok('le panorama répond', rp && rp.status() === 200, rp && rp.status());
  const m17 = await marquer(p, '.pnav a[data-tt]', 'onglet');
  await p.waitForTimeout(300);
  o0 = await ouvertures(p);
  if (m17) { await APPUI_LONG_BRUT(p, cdp, 'onglet'); await APPUI(p, cdp, 'onglet'); }
  const r17 = await p.evaluate(() => ({ ouvertures: window.__ouvertures }));
  v = await p.evaluate(VUE, 'onglet');
  ok('T-17 .pnav a[data-tt] : appui long et appui, aucune ouverture de #bulle-titre', !!m17 && r17.ouvertures === o0 && !v.visible,
     m17 ? dit(v) : 'onglet introuvable');
  /* Le témoin : le niveau d'agrandissement de la carte, un <div> inerte à
     `title` que le panorama laisse à /bulle-titre.js (§3.7). */
  const tem = await marquer(p, '.z-niv[title]', 'temoin-pano');
  if (tem) { await APPUI(p, cdp, 'temoin-pano'); }
  v = await p.evaluate(VUE, 'temoin-pano');
  const titreTem = v.title;
  ok('T-17 témoin : un élément inerte à title du panorama, appuyé, S’OUVRE', !!tem && visible(v),
     tem ? dit(v) + ' (title « ' + (titreTem || '').slice(0, 30) + ' »)' : 'aucun élément témoin');
  await ctx.close();
  }
  await nav.close();

  // ══ T-18 — LES RÈGLES PYTHON ═══════════════════════════════════════════
  if (joue('T')) {
  console.log('\n══ T-18 — tests/test_bulle_titre.py ══');
  let sortie = '', vert = false;
  try {
    sortie = execSync('python -m pytest -q tests/test_bulle_titre.py', { cwd: DEPOT, encoding: 'utf8', stdio: 'pipe' });
    vert = true;
  } catch (e) { sortie = String(e.stdout || e.message); }
  ok('T-18 tests/test_bulle_titre.py est vert', vert, (sortie.trim().split('\n').pop() || '').slice(0, 120));
  }

  console.log('\nerreurs de page : ' + (erreurs.length ? erreurs.slice(0, 3).join(' | ') : 'aucune')
              + ' ; refus du limiteur : ' + refus.length);
  ok('aucune erreur JavaScript dans les pages', erreurs.length === 0, erreurs.slice(0, 2).join(' | '));
  ok('aucun refus du limiteur (sinon la recette a mesuré des 429)', refus.length === 0, refus.slice(0, 2).join(' '));
  console.log('\n' + (n - ko) + '/' + n + ' contrôles verts' + (ko ? ' — ' + ko + ' en échec' : ''));
  process.exit(ko ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
