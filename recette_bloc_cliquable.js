/* RECETTE — LE BLOC ENTIER EST LE LIEN, PAS SEULEMENT SON PIED
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE : « rediriger le bloc Formation et Accompagnement et le bloc
 * Gouvernance GRC respectivement vers les modules Sentinel ». Les deux
 * destinations étaient déjà justes ; ce qui ne l'était pas, c'est que seule
 * l'étiquette « Ouvrir le module » les déclenchait. Cliquer le titre,
 * l'icône ou la description d'une carte ne faisait rien.
 *
 * CE QUE LES RÈGLES PYTHON NE PEUVENT PAS VOIR. Elles lisent la feuille de
 * style ; elles ne savent pas OÙ la surface étirée se pose, ni ce qu'un clic
 * atteint. Le défaut d'origine tenait à la rencontre de deux règles écrites
 * à deux mille lignes d'écart : `inset:0` se résout contre le plus proche
 * ancêtre POSITIONNÉ, et une règle décorative positionnait déjà le pied de
 * carte. La surface mesurait alors 152 × 36 px — la taille de l'étiquette —
 * au lieu de 388 × 356. Chaque ligne de CSS était juste ; leur somme ne
 * l'était pas. Seul le navigateur pouvait le dire.
 *
 * DEUX PIÈGES DE MESURE, appris à mes dépens et gardés ici pour qu'ils ne
 * reviennent pas :
 *   · `html{scroll-behavior:smooth}` : lire le rectangle d'un élément juste
 *     après `scrollIntoView` rend les coordonnées D'AVANT le défilement, et
 *     `elementFromPoint` ne trouve alors plus rien. D'où `behavior:'instant'`.
 *   · le protecteur anti-abus du serveur répond 429 au troisième chargement
 *     de page. D'où UN SEUL `goto`, et toute la mesure sur la page chargée.
 *
 * LES CONTRÔLES :
 *   1-3.  La surface étirée couvre la CARTE, des deux côtés, et le pied
 *         n'est pas redevenu son propre bloc conteneur.
 *   4-6.  Le corps des six cartes de service navigue — description, titre,
 *         icône — et les deux cartes nommées par la demande mènent bien au
 *         hub de formation et à la gouvernance opérationnelle de l'IA.
 *   7-8.  Les treize flèches de puce ouvrent LEUR module ; le texte d'une
 *         puce, lui, appartient à la surface de la carte.
 *   9.    Les huit cartes de risque, étiquette de catégorie comprise.
 *  10-13. Rien d'imbriqué, un curseur qui le dit, un pied encore lui-même
 *         sous le pointeur, rien qui déborde, aucune erreur de script.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5901';
let ko = 0, n = 0;
const ok = (t, c, d) => { n++; if (!c) ko++;
  console.log((c ? '  OK   ' : '  KO   ') + t + (d ? ' — ' + d : '')); };

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1400, height: 1200 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e).slice(0, 160)));
  const rep = await pg.goto(BASE + '/', { waitUntil: 'domcontentloaded' });
  ok('la page répond', rep && rep.status() === 200,
     rep ? 'HTTP ' + rep.status() : 'pas de réponse');
  if (!rep || rep.status() !== 200) { await nav.close(); process.exit(2); }
  await pg.waitForTimeout(2200);

  /* ── LA GÉOMÉTRIE : LA SURFACE COUVRE-T-ELLE LA CARTE ? ───────────── */
  const geo = await pg.evaluate(() => {
    const mes = (sc, sp) => {
      const c = document.querySelector(sc); if (!c) return null;
      const a = c.querySelector(sp);
      const rc = c.getBoundingClientRect();
      const st = getComputedStyle(a, '::after');
      return { cw: rc.width, ch: rc.height,
               sw: parseFloat(st.width), sh: parseFloat(st.height),
               pos: getComputedStyle(a).position };
    };
    return { s: mes('#services .diff-card', '.sv-card-go'),
             r: mes('#risques .risk-card', '.risk-go') };
  });
  /* LA TOLÉRANCE EST LA BORDURE : `inset:0` se résout contre la boîte de
     padding, donc la surface vaut la carte MOINS ses deux bordures d'1px. */
  const colle = (m) => m && Math.abs(m.cw - m.sw) <= 3 && Math.abs(m.ch - m.sh) <= 3;
  ok('la surface étirée d’une carte de service couvre la CARTE',
     colle(geo.s), geo.s ? Math.round(geo.s.sw) + '×' + Math.round(geo.s.sh)
       + ' pour une carte de ' + Math.round(geo.s.cw) + '×' + Math.round(geo.s.ch)
       + ' (pied ' + geo.s.pos + ')' : 'carte introuvable');
  /* ET SUR UNE CARTE DE RISQUE, IL NE DOIT Y AVOIR AUCUNE SURFACE. Le
     pseudo-élément n'existe plus : ses dimensions se lisent NaN, et c'est
     la seule forme sous laquelle une absence se mesure ici. */
  ok('une carte de risque n’a PAS de surface étirée',
     geo.r && !(geo.r.sw > 0), geo.r
       ? Math.round(geo.r.sw) + '×' + Math.round(geo.r.sh) + ' de surface sur '
         + 'une carte de ' + Math.round(geo.r.cw) + '×' + Math.round(geo.r.ch)
       : 'carte introuvable',
     'aucune');

  /* ── LE CLIC : ON INTERCEPTE AU LIEU DE SUIVRE ────────────────────── */
  await pg.evaluate(() => {
    window.__ALLE = [];
    document.addEventListener('click', function (e) {
      const a = e.target.closest('a');
      if (a && a.getAttribute('href')) { e.preventDefault();
        window.__ALLE.push(a.getAttribute('href')); }
    }, true);
    window.__viser = (el) => {
      window.__ALLE = [];
      if (!el) return 'SÉLECTEUR INTROUVABLE';
      el.scrollIntoView({ block: 'center', behavior: 'instant' });
      const r = el.getBoundingClientRect();
      const cible = document.elementFromPoint(r.left + r.width / 2,
                                              r.top + r.height / 2);
      if (!cible) return 'HORS DE L’ÉCRAN';
      cible.click();
      return window.__ALLE[0] || 'AUCUNE NAVIGATION';
    };
  });

  const cartes = await pg.evaluate(() =>
    [...document.querySelectorAll('#services .diff-card')].map((c, i) => {
      const att = c.querySelector('.sv-card-go').getAttribute('href');
      const h = c.querySelector('.diff-title');
      return { t: h.textContent.trim(), cle: h.getAttribute('data-i18n'), att: att,
        desc:  window.__viser(c.querySelector('.diff-desc')),
        titre: window.__viser(c.querySelector('.diff-title')),
        ico:   window.__viser(c.querySelector('.diff-ico')) };
    }));
  const mauvaises = cartes.filter(c =>
    c.desc !== c.att || c.titre !== c.att || c.ico !== c.att);
  ok('le CORPS des six cartes de service navigue (description, titre, icône)',
     mauvaises.length === 0,
     mauvaises.length ? mauvaises.map(c => c.t + ' : ' + c.desc + '/' + c.titre
       + '/' + c.ico + ' ≠ ' + c.att).join(' | ')
     : cartes.map(c => c.att.split('=')[1]).join(' · '));
  console.log('       titres : ' + cartes.map(c => JSON.stringify(c.t)).join(' | '));
  const form = cartes.find(c => c.att === '/sentinel?goto=training');
  ok('« Formation & Accompagnement » mène au hub de formation',
     form && form.titre === '/sentinel?goto=training'
          && form.cle === 'sv.form.t',
     form ? form.cle + ' « ' + form.t + ' » → ' + form.titre
          : 'aucune carte ne vise training');
  const gouv = cartes.find(c => c.att === '/sentinel?goto=gouvernance');
  ok('« Gouvernance & GRC » mène à la gouvernance opérationnelle de l’IA',
     gouv && gouv.titre === '/sentinel?goto=gouvernance'
          && gouv.cle === 'sv.grc.t',
     gouv ? gouv.cle + ' « ' + gouv.t + ' » → ' + gouv.titre
          : 'aucune carte ne vise gouvernance');

  /* ── LES FLÈCHES DE PUCE GARDENT LEUR PROPRE DESTINATION ──────────── */
  const fl = await pg.evaluate(() =>
    [...document.querySelectorAll('#services .sv-go')].map(a => ({
      sien: a.getAttribute('href'), atteint: window.__viser(a) })));
  const det = fl.filter(x => x.sien !== x.atteint);
  ok('les ' + fl.length + ' flèches de puce ouvrent LEUR module, pas celui de la carte',
     fl.length === 13 && det.length === 0,
     det.length ? det.map(x => x.sien + ' → ' + x.atteint).join(', ')
                : fl.length + ' flèches');

  /* LE TEXTE D'UNE PUCE, LUI, APPARTIENT À LA CARTE — c'est le choix fait :
     seule la flèche s'échappe. On le mesure pour que le choix soit tenu. */
  const puce = await pg.evaluate(() => {
    const c = document.querySelector('#services .diff-card');
    return { att: c.querySelector('.sv-card-go').getAttribute('href'),
             vu: window.__viser(c.querySelector('.diff-sublist li span')) };
  });
  ok('le TEXTE d’une puce appartient à la surface de la carte',
     puce.vu === puce.att, puce.vu + ' (carte : ' + puce.att + ')');

  /* ── LES HUIT CARTES DE RISQUE N'EN SONT PAS, ET C'EST VOULU ───────
     Sur elles, seul « Ouvrir le module » redirige : une carte de risque est
     un CONSTAT qu'on lit pour lui-même, pas un appel. Le détail est mesuré
     par recette_appel_seul_risques.js, qui intercepte aussi `window.open` ;
     ici on vérifie seulement que le motif ne leur est pas revenu. */
  const risques = await pg.evaluate(() =>
    [...document.querySelectorAll('#risques .risk-card')].map(c => ({
      t: c.querySelector('.risk-title').textContent.trim(),
      att: c.querySelector('.risk-go').getAttribute('href'),
      desc: window.__viser(c.querySelector('.risk-desc')),
      curseur: getComputedStyle(c).cursor })));
  const fuites = risques.filter(c => c.desc !== 'AUCUNE NAVIGATION');
  ok('le corps des huit cartes de risque ne navigue PAS',
     risques.length === 8 && fuites.length === 0,
     fuites.map(c => c.t + ' : ' + c.desc).join(' | ')
       || '8 corps inertes, 8 appels intacts');
  ok('et elles n’annoncent pas un clic qu’elles ne rendent pas',
     risques.every(c => c.curseur !== 'pointer'),
     'cursor:' + (risques[0] || {}).curseur);

  /* ── CE QUI NE DOIT PAS AVOIR CHANGÉ ──────────────────────────────── */
  const sain = await pg.evaluate(() => ({
    imbriques: [...document.querySelectorAll('#services a, #risques a')]
      .filter(a => !!a.parentElement.closest('a')).length,
    curseur: getComputedStyle(document.querySelector('#services .diff-card')).cursor,
    lisible: (() => { const a = document.querySelector('#services .sv-card-go');
      a.scrollIntoView({ block: 'center', behavior: 'instant' });
      const r = a.getBoundingClientRect();
      const c = document.elementFromPoint(r.left + r.width/2, r.top + r.height/2);
      return c ? (c.closest('.sv-card-go') ? true
                  : c.tagName + '.' + c.className) : 'rien sous le pointeur'; })(),
    deb: Math.max(0, document.documentElement.scrollWidth
                     - document.documentElement.clientWidth)
  }));
  ok('aucun lien n’est imbriqué dans un autre', sain.imbriques === 0,
     sain.imbriques + ' imbriqué(s)');
  ok('la carte annonce qu’elle est cliquable', sain.curseur === 'pointer',
     'cursor:' + sain.curseur);
  ok('le pied reste lui-même sous le pointeur', sain.lisible === true,
     String(sain.lisible));
  ok('rien ne déborde', sain.deb === 0, sain.deb + ' px');
  ok('aucune erreur JavaScript', err.length === 0, err.join(' | '));

  await nav.close();
  console.log('\n' + (n - ko) + ' contrôles passés, ' + ko + ' en échec');
  process.exit(ko ? 1 : 0);
})().catch(e => { console.error('KO   rompu : ' + e); process.exit(2); });
