/* Recette de mise en page — ce qui SE PEINT se chevauche-t-il ?
 *
 * POURQUOI CE FICHIER EST ICI ET NON DANS `tests/`
 *
 * Il ouvre un navigateur et une socket. La suite de tests n'en ouvre aucune :
 * un contrôle qui dépend du réseau rougit les jours où le réseau bouge, et une
 * suite qui rougit pour une raison extérieure finit par ne plus être lue. Cette
 * recette se lance donc À LA MAIN, contre l'application servie en local :
 *
 *     PORT=5598 FLASK_SECRET_KEY=recette-locale COOKIE_NON_SECURISE=1 python3 app.py &
 *     node outils/recette_mise_en_page.js http://127.0.0.1:5598
 *
 * CE QU'ELLE VÉRIFIE : pour chacune des pages de `app.PAGES`, qu'aucune paire
 * de blocs porteurs de texte ne se recouvre à plus de 30 % de la plus petite
 * des deux, et que la page ne déborde pas horizontalement.
 *
 * CINQ PIÈGES, ET C'EST L'HISTOIRE DE CE FICHIER. La première sonde annonçait
 * 8 pages en défaut sur 25 ; il y en avait 3. Les cinq autres venaient d'elle :
 *
 *  1. LES RECOUVREMENTS VOULUS. Le bandeau de consentement recouvre la page —
 *     c'est sa fonction. Le filigrane anti-copie aussi : `#cp-watermark`, en
 *     `position:fixed`, `z-index:99999`, `pointer-events:none`, et surtout
 *     `opacity:.03`. Deux écartés par la même mesure — tout ce qui EST ou
 *     DESCEND d'un `position:fixed` —, à une correction près, qui a coûté six
 *     pages faussement en défaut : la première version partait du PARENT, si
 *     bien que le filigrane lui-même n'était jamais écarté, seulement ses
 *     enfants. Et de l'encre à 3 % n'est pas du texte : l'opacité CUMULÉE le
 *     long de la chaîne doit rester lisible.
 *  2. LES ÉLÉMENTS EN LIGNE qui passent à la ligne rendent un rectangle qui est
 *     l'UNION de leurs fragments : deux <strong> voisins d'un même paragraphe
 *     se « chevauchaient » à 100 % sans que rien ne se superpose. Seules les
 *     boîtes de bloc sont comparées.
 *  3. CE QU'UN ANCÊTRE ROGNE garde son rectangle sans être à l'écran. Le
 *     rectangle est donc INTERSECTÉ avec celui de chaque ancêtre rogneur.
 *  4. CE QUE LE NAVIGATEUR NE PEINT PAS garde aussi son rectangle : le contenu
 *     d'un <details> replié, une section sautée par `content-visibility`. D'où
 *     la règle de ce fichier : ne rien deviner de la visibilité, la DEMANDER,
 *     par `checkVisibility()`. Seul `content-visibility:auto` est neutralisé,
 *     pour juger une section hors écran sur sa mise en page rendue ; `hidden`
 *     n'est jamais touché — ce que la page cache exprès doit le rester.
 *  5. UNE PAGE QUI N'A PAS ÉTÉ SERVIE N'EST PAS UNE PAGE SANS DÉFAUT. Le
 *     premier passage contre l'application a rendu « 0 défaut sur 25 » : le
 *     limiteur de cadence répondait 429 à partir de la deuxième page, et une
 *     page vide ne chevauche rien. La recette relève donc le CODE HTTP de
 *     chaque navigation et le nombre de blocs trouvés, et REFUSE DE CONCLURE
 *     sur une page qu'elle n'a pas vue. C'est ce garde-fou qui a ensuite
 *     révélé la vraie raison : `HEADLESS_DETECTED`, la défense anti-scraping
 *     du site, qui bloque l'adresse pour trente minutes.
 *
 * D'OÙ LE CHOIX DU SERVEUR. La mise en page est entièrement décidée dans le
 * navigateur : le serveur n'en change rien. La recette mesure donc les pages
 * servies en fichiers, sans l'application ni ses défenses :
 *
 *     python3 -m http.server 5599 --bind 127.0.0.1
 *     node outils/recette_mise_en_page.js http://127.0.0.1:5599
 *
 * Il reste DEUX signaux à écarter, et ils sont dans la page : chaque
 * `.page.js` remplace le document par « Accès non autorisé » quand
 * `navigator.webdriver` est vrai OU quand l'agent contient « HeadlessChrome ».
 * Sans cela, sept pages se vident et la recette ne mesure rien — elle le DIT
 * (« non vue »), mais elle ne mesure toujours pas. On écarte donc ces deux
 * signaux-là, dans le navigateur de la recette et nulle part ailleurs : le
 * site en ligne garde sa protection entière, et c'est bien ainsi.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const BASE = process.argv[2] || 'http://127.0.0.1:5599';
const SORTIE = process.argv[3] || '';
const RACINE = path.dirname(__dirname);

// Les pages sont LUES dans app.PAGES — jamais recopiées : une page ajoutée au
// site sans l'être ici serait une page jamais mesurée, et rien ne le dirait.
function adresses() {
  const src = fs.readFileSync(path.join(RACINE, 'app.py'), 'utf8');
  const i = src.indexOf('PAGES = {');
  if (i < 0) throw new Error("app.py : bloc « PAGES = { » introuvable");
  const bloc = src.slice(i, src.indexOf('}', i) + 1);
  const out = [];
  const re = /'(\/[^']*)'\s*:\s*'([^']+\.html)'/g;
  let m; while ((m = re.exec(bloc))) out.push({ route: m[1], fichier: m[2] });
  if (out.length < 10) throw new Error('app.PAGES : ' + out.length + ' pages lues, c\'est trop peu');
  return out;
}

const SONDE = () => {
  const VU = { opacityProperty: true, visibilityProperty: true, contentVisibilityAuto: true };
  const BLOC = /^(block|flow-root|list-item|flex|grid|table|table-row|table-cell)$/;
  const inter = (a, b) => {
    const l = Math.max(a.left, b.left), r = Math.min(a.right, b.right);
    const t = Math.max(a.top, b.top),  o = Math.min(a.bottom, b.bottom);
    return { left: l, right: r, top: t, bottom: o,
             width: Math.max(0, r - l), height: Math.max(0, o - t) };
  };
  // En dessous, l'encre ne se lit plus : le filigrane est posé à 3 %.
  const ENCRE_LISIBLE = 0.15;

  function boiteVue(el) {
    let r = el.getBoundingClientRect();
    let encre = 1;
    // La chaîne part de l'ÉLÉMENT, pas de son parent : un filigrane fixe se
    // porte lui-même, et c'est lui qui recouvrait tout.
    for (let n = el; n && n !== document.documentElement; n = n.parentElement) {
      const s = getComputedStyle(n);
      if (s.position === 'fixed') return null;
      encre *= parseFloat(s.opacity);
      if (encre < ENCRE_LISIBLE) return null;
      if (n !== el && (s.overflow !== 'visible' || s.overflowY !== 'visible' || s.overflowX !== 'visible'))
        r = inter(r, n.getBoundingClientRect());
      if (r.width <= 0 || r.height <= 0) return null;
    }
    return r;
  }
  function texteDirect(el) {
    let t = ''; for (const n of el.childNodes) if (n.nodeType === 3) t += n.textContent;
    return t.trim();
  }
  const porteurs = [];
  for (const el of document.querySelectorAll('body *')) {
    if (!el.checkVisibility(VU)) continue;
    if (!BLOC.test(getComputedStyle(el).display)) continue;
    if (texteDirect(el).length <= 12) continue;
    const r = boiteVue(el);
    if (!r || r.width <= 8 || r.height <= 6) continue;
    porteurs.push({ el, r,
      nom: el.tagName.toLowerCase() + '.' + (el.className || '').toString().split(/\s+/)[0],
      t: texteDirect(el).slice(0, 46).replace(/\s+/g, ' ') });
  }
  const chev = [];
  for (let i = 0; i < porteurs.length; i++) for (let j = i + 1; j < porteurs.length; j++) {
    const a = porteurs[i], b = porteurs[j];
    if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
    const x = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left);
    const y = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
    if (x <= 4 || y <= 4) continue;
    const part = (x * y) / Math.min(a.r.width * a.r.height, b.r.width * b.r.height);
    if (part > 0.30) chev.push({ part: Math.round(part * 100),
                                 a: a.nom + ' « ' + a.t + ' »', b: b.nom + ' « ' + b.t + ' »' });
  }
  // Un <nav> imbriqué dans le contenu — un sommaire — ne doit pas porter la
  // position collante, le z-index ni la hauteur de la barre du site.
  const navs = [...document.querySelectorAll('nav')].map(n => {
    const s = getComputedStyle(n);
    return { nom: 'nav.' + (n.className || '').toString().split(/\s+/)[0], pos: s.position,
             disp: s.display, haut: Math.round(n.getBoundingClientRect().height), zi: s.zIndex,
             dansContenu: !!n.parentElement.closest('.con,.page-wrap,main,article') };
  });
  return { porteurs: porteurs.length, nb_chev: chev.length, chevauchements: chev.slice(0, 6),
           navs, deborde: document.documentElement.scrollWidth > window.innerWidth + 2,
           // La page a-t-elle été REMPLACÉE par l'écran de blocage ? Celui-ci
           // réécrit `documentElement.innerHTML` et emporte le <head> — donc le
           // <title>. C'est un signal exact, là où un seuil de blocs déclarait
           // « non vue » une page simplement courte, comme /map.
           aTitre: !!document.querySelector('head > title') };
};

(async () => {
  const PAGES = adresses();
  const nav = await chromium.launch();
  // L'agent est celui du navigateur lancé, « Headless » retiré — jamais une
  // chaîne recopiée, qui vieillirait à la première mise à jour de Chromium.
  const provisoire = await nav.newContext();
  const agentNu = (await (await provisoire.newPage())
    .evaluate(() => navigator.userAgent)).replace(/Headless/g, '');
  await provisoire.close();
  const ctx = await nav.newContext({ viewport: { width: 1280, height: 900 }, userAgent: agentNu });
  // Les deux seuls signaux écartés, et ils le sont ici seulement : chaque
  // `.page.js` remplace le document par « Accès non autorisé » quand
  // `navigator.webdriver` est vrai ou que l'agent dit « HeadlessChrome ». La
  // protection du site en ligne n'est pas touchée.
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  });
  const out = [];

  for (const p of PAGES) {
    const adr = p.route;
    const page = await ctx.newPage();
    const err = [];
    page.on('pageerror', e => err.push(String(e).slice(0, 90)));
    let fiche = { page: adr };
    try {
      const rep = await page.goto(BASE + '/' + p.fichier, { waitUntil: 'networkidle', timeout: 30000 });
      fiche.statut = rep ? rep.status() : 0;
      await page.evaluate(() => { for (const el of document.querySelectorAll('*'))
        if (getComputedStyle(el).contentVisibility === 'auto') el.style.contentVisibility = 'visible'; });
      await page.waitForTimeout(400);
      fiche = { ...fiche, ...(await page.evaluate(SONDE)), erreurs: err.length };
    } catch (e) { fiche.echec = String(e).slice(0, 110); }
    // LA PAGE A-T-ELLE ÉTÉ VUE ? Un 429, un 404, un document remplacé par
    // l'écran de blocage, un corps sans le moindre bloc de texte : dans tous
    // ces cas la recette ne conclut pas — elle le dit. C'est le piège n° 5.
    fiche.rendue = fiche.statut === 200 && fiche.aTitre === true && (fiche.porteurs || 0) >= 1;
    out.push(fiche);
    process.stderr.write(`${fiche.rendue ? '·' : '!'} ${adr} (${fiche.statut}, ${fiche.porteurs || 0} blocs)\n`);
    try { await page.close(); } catch (e) {}
    if (SORTIE) fs.writeFileSync(SORTIE, JSON.stringify(out, null, 1));
  }
  try { await nav.close(); } catch (e) {}

  const nonVues = out.filter(e => !e.rendue);
  const fautives = out.filter(e => e.rendue && (e.nb_chev || e.deborde));
  console.log('\n===== RECETTE DE MISE EN PAGE =====');
  console.log(`${out.length} adresses, ${out.length - nonVues.length} rendues, ${nonVues.length} non vues`);
  for (const e of nonVues)
    console.log(`  NON VUE   ${e.page}  statut=${e.statut} titre=${e.aTitre === true} `
                + `blocs=${e.porteurs || 0}${e.echec ? ' ' + e.echec : ''}`);
  for (const e of fautives) {
    console.log(`\n  DÉFAUT    ${e.page} — ${e.nb_chev} chevauchement(s)${e.deborde ? ', déborde' : ''}`);
    for (const c of e.chevauchements) console.log(`      ${c.part}%  ${c.a}\n           ∩ ${c.b}`);
  }
  for (const e of out.filter(x => x.rendue))
    for (const n of e.navs.filter(n => n.dansContenu && (n.pos === 'sticky' || n.pos === 'fixed')))
      console.log(`  SOMMAIRE COLLANT  ${e.page} — ${n.nom} pos=${n.pos} z=${n.zi} h=${n.haut}px`);
  if (!fautives.length && !nonVues.length) console.log('\n  Aucun chevauchement, aucun débordement.');
  process.exit(fautives.length || nonVues.length ? 1 : 0);
})();
