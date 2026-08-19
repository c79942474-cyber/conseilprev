/* RECETTE — LA BARRE LATÉRALE DE SENTINEL
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE : « faire la même chose pour la barre latérale de Sentinel »,
 * après le menu de l'autre site du cabinet.
 *
 * CE QUI MANQUAIT ICI N'ÉTAIT PAS LA MÊME CHOSE. Les cinquante onglets
 * portaient DÉJÀ leur icône. Ce qui manquait, c'est le niveau au-dessus : les
 * douze titres de rubrique n'étaient que du texte gris de neuf pixels, et les
 * cinquante puces étaient toutes de la même couleur. On lisait la colonne de
 * haut en bas pour retrouver où l'on était.
 *
 * CE QUE CES CONTRÔLES GARDENT :
 *
 *   1. CHAQUE RUBRIQUE PORTE SON ICÔNE ET SA TEINTE — et ses onglets la
 *      reprennent. C'est la teinte partagée qui fait le bloc ; un onglet resté
 *      gris au milieu d'un groupe coloré paraîtrait rangé ailleurs.
 *   2. LA COULEUR N'EST JAMAIS LE SEUL SIGNAL (WCAG 1.4.1). Sept teintes pour
 *      douze rubriques : ce sont les silhouettes qui distinguent, et elles
 *      sont toutes différentes.
 *   3. AUCUNE SILHOUETTE NE SE RÉPÈTE DANS UNE MÊME RUBRIQUE, ni entre un
 *      onglet et le chapeau qui le coiffe. Deux défauts mesurés au départ :
 *      « Cartographie des traitements » ne se distinguait de « Vue d'ensemble »
 *      que par des coins arrondis, et « Géopolitique » reprenait le globe de
 *      « Cartographie ».
 *   4. LES ICÔNES SONT MUETTES POUR LES AIDES VOCALES. L'intitulé est écrit
 *      juste à côté ; l'annoncer deux fois n'aide personne.
 *   5. LE SURVOL ET L'ONGLET COURANT GARDENT LEUR PROPRE LANGAGE — la terre
 *      cuite du site. Elle dit « ici » ; la teinte de rubrique dit « quel
 *      groupe ». Si la teinte l'emportait sur l'état, on ne saurait plus lire
 *      où l'on se trouve.
 *   6. RIEN N'EST POUSSÉ HORS DE LA COLONNE — 240 px, et des intitulés qui se
 *      replient sur deux lignes.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5901 node recette_barre_sentinel.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';

let ko = 0;
/* `mesure` s'affiche toujours, `siKo` seulement en cas d'échec. Les confondre
   fait lire « OK — sans icône : » sur une ligne verte, et un motif d'échec qui
   paraît sans échec apprend à ne plus le croire. */
const ok = (t, cond, siKo, mesure) => {
  console.log((cond ? '  OK   ' : '  KO   ') + t
              + (mesure ? ' — ' + mesure : '')
              + (!cond && siKo ? ' — ' + siKo : ''));
  if (!cond) ko++;
};
const titre = t => console.log('\n══ ' + t + ' ══\n');

/* LA BARRE EST UNE SUITE DE FRÈRES, pas un arbre : les onglets suivent leur
   titre sans être dedans. Ce regroupement est donc refait ICI, dans le
   navigateur, à partir du document — jamais recopié d'une liste écrite à la
   main, qui cesserait d'être vraie au premier onglet ajouté. */
const RELEVE = () => {
  const secs = [...document.querySelectorAll('.sb-nav .sb-section')];
  const grp = secs.map(s => {
    const items = [];
    let n = s.nextElementSibling;
    while (n && !n.classList.contains('sb-section')) {
      if (n.classList.contains('sb-item')) items.push(n);
      n = n.nextElementSibling;
    }
    const svc = s.querySelector('svg.sb-sec-ic');
    return {
      titre: s.textContent.trim(),
      grp: s.getAttribute('data-grp'),
      teinte: getComputedStyle(s).getPropertyValue('--sb-ic').trim(),
      couleurIc: svc ? getComputedStyle(svc).color : null,
      dessin: svc ? svc.innerHTML.replace(/\s+/g, '') : null,
      muette: svc ? svc.getAttribute('aria-hidden') === 'true' : null,
      onglets: items.map(a => {
        const sv = a.querySelector('.sb-icon svg');
        const ch = a.querySelector('.sb-icon');
        return {
          label: a.textContent.trim(),
          grp: a.getAttribute('data-grp'),
          dessin: sv ? sv.innerHTML.replace(/\s+/g, '') : null,
          muette: sv ? sv.getAttribute('aria-hidden') === 'true' : null,
          focusable: sv ? sv.getAttribute('focusable') !== 'false' : null,
          couleur: ch ? getComputedStyle(ch).color : null,
          actif: a.classList.contains('on')
        };
      })
    };
  });
  return { grp, sections: secs.length };
};

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1500, height: 1000 } });
  /* SANS CE MASQUE, LE SERVEUR BLOQUE L'ADRESSE POUR 1800 s. */
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e).slice(0, 140)));
  const sur = async (fn, arg) => {
    try { return await pg.evaluate(fn, arg); }
    catch (e) { return { err: String(e && e.message || e) }; }
  };

  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.waitForTimeout(400);
  const rep = await pg.goto(BASE + '/sentinel', { waitUntil: 'domcontentloaded' });
  ok('la page répond', rep && rep.status() === 200,
     rep ? 'HTTP ' + rep.status() : 'pas de réponse');
  if (!rep || rep.status() !== 200) { await nav.close(); process.exit(2); }
  await pg.waitForTimeout(2500);

  const R = await sur(RELEVE);
  if (R.err) { ok('la barre a pu être relevée', false, R.err); await nav.close(); process.exit(2); }
  const G = R.grp;
  const tousOnglets = G.reduce((a, s) => a.concat(s.onglets), []);

  // ── 1 ───────────────────────────────────────────────────────────────────
  titre('1. Chaque rubrique porte son icône, et chaque onglet la sienne');

  ok('la barre est construite', G.length >= 10, null, G.length + ' rubrique(s)');
  const secSans = G.filter(s => !s.dessin).map(s => s.titre);
  ok('AUCUNE rubrique n’est laissée sans repère', secSans.length === 0,
     secSans.join(', '));
  const ongSans = tousOnglets.filter(o => !o.dessin).map(o => o.label);
  ok('…et aucun onglet non plus', ongSans.length === 0, ongSans.slice(0, 4).join(' | '),
     tousOnglets.length + ' onglet(s)');

  // ── 2 : LE POINT QUI DÉCIDE ─────────────────────────────────────────────
  titre('2. La couleur n’est pas le seul signal (WCAG 1.4.1)');

  const silSec = new Set(G.map(s => s.dessin));
  ok('LE POINT QUI DÉCIDE — les douze silhouettes de rubrique sont TOUTES '
     + 'différentes',
     silSec.size === G.length, null,
     silSec.size + ' silhouette(s) pour ' + G.length + ' rubriques');

  const collisions = [];
  const echos = [];
  G.forEach(s => {
    const vus = {};
    s.onglets.forEach(o => {
      if (!o.dessin) return;
      if (vus[o.dessin]) collisions.push(s.titre + ' : « ' + o.label + ' » et « '
                                         + vus[o.dessin] + ' »');
      vus[o.dessin] = o.label;
      if (o.dessin === s.dessin) echos.push(s.titre + ' → ' + o.label);
    });
  });
  ok('…deux onglets d’UNE MÊME rubrique ne partagent jamais un dessin',
     collisions.length === 0, collisions.slice(0, 4).join(' | '));
  ok('…et aucun onglet ne recopie le dessin de son propre chapeau',
     echos.length === 0, echos.slice(0, 4).join(' | '));

  const teintesSec = new Set(G.map(s => s.couleurIc));
  ok('les teintes sont variées sans avoir à être uniques',
     teintesSec.size >= 5, null,
     teintesSec.size + ' teinte(s) pour ' + G.length + ' rubriques');

  // ── 3 ───────────────────────────────────────────────────────────────────
  titre('3. L’onglet reprend la teinte de SA rubrique');

  /* CE QUI FAIT LE BLOC, C'EST LA TEINTE PARTAGÉE. Un onglet resté gris au
     milieu d'un groupe coloré se lirait comme rangé ailleurs. L'onglet COURANT
     est écarté : sa puce est pleine et terre cuite, c'est voulu (contrôle 5). */
  let apparies = 0, orphelins = [];
  G.forEach(s => s.onglets.forEach(o => {
    if (o.actif) return;
    if (o.grp === s.grp && o.couleur === s.couleurIc) apparies++;
    else orphelins.push(s.titre + ' → ' + o.label + ' (' + o.couleur + ' ≠ '
                        + s.couleurIc + ')');
  }));
  ok('LE POINT QUI DÉCIDE — chaque onglet au repos porte la teinte de sa '
     + 'rubrique',
     orphelins.length === 0, orphelins.slice(0, 3).join(' | '),
     apparies + ' onglet(s) appariés');
  /* …ET LES RUBRIQUES NE PORTENT PAS TOUTES LA MÊME. Sans ce contrôle, une
     feuille de style qui perdrait `--sb-ic` rendrait tout gris — et le
     contrôle ci-dessus passerait quand même, tout étant « apparié ». */
  const teintesOnglets = new Set(tousOnglets.filter(o => !o.actif).map(o => o.couleur));
  ok('…et ces teintes ne sont pas toutes la même',
     teintesOnglets.size >= 5, null, teintesOnglets.size + ' teinte(s) au repos');

  // ── 4 ───────────────────────────────────────────────────────────────────
  titre('4. Les icônes sont muettes pour les aides vocales');

  ok('les icônes de rubrique sont masquées',
     G.every(s => s.muette === true),
     G.filter(s => s.muette !== true).map(s => s.titre).join(', '));
  const parlantes = tousOnglets.filter(o => o.muette !== true).map(o => o.label);
  ok('…celles des onglets aussi', parlantes.length === 0,
     parlantes.length + ' annoncée(s) : ' + parlantes.slice(0, 3).join(', '));
  ok('…et aucune n’attrape la tabulation',
     tousOnglets.every(o => o.focusable === false),
     tousOnglets.filter(o => o.focusable !== false).length + ' focusable(s)');
  const muets = tousOnglets.filter(o => o.label.replace(/\s/g, '').length < 2);
  ok('…l’intitulé écrit reste le seul nom de l’onglet', muets.length === 0,
     muets.length + ' onglet(s) sans texte');

  // ── 5 ───────────────────────────────────────────────────────────────────
  titre('5. L’état « ici » garde son propre langage');

  const etat = await sur(() => {
    const a = document.querySelector('.sb-item.on');
    if (!a) return { err: 'aucun onglet courant' };
    const ch = a.querySelector('.sb-icon');
    const cs = getComputedStyle(ch);
    const repos = [...document.querySelectorAll('.sb-item:not(.on) .sb-icon')]
      .map(x => getComputedStyle(x).backgroundColor);
    return { fond: cs.backgroundColor, encre: cs.color,
             fondsAuRepos: [...new Set(repos)].length };
  });
  /* La puce de l'onglet courant est PLEINE et terre cuite : c'est le seul
     endroit où le fond est saturé, et c'est ce qui répond à « où suis-je ». */
  ok('la puce de l’onglet courant reste pleine et terre cuite',
     !etat.err && /rgba?\(\s*184,\s*50,\s*34/.test(etat.fond || ''),
     etat.err || ('fond ' + etat.fond), etat.err ? '' : 'encre ' + etat.encre);
  ok('…et les puces au repos, elles, sont teintées par rubrique',
     !etat.err && etat.fondsAuRepos >= 5, etat.err,
     etat.err ? '' : etat.fondsAuRepos + ' fond(s) distincts au repos');

  // ── 6 ───────────────────────────────────────────────────────────────────
  titre('6. Rien n’est poussé hors de la colonne de 240 px');

  const geo = await sur(() => {
    const sb = document.querySelector('.sb');
    const r = sb.getBoundingClientRect();
    let debord = 0, replis = 0, decale = 0;
    const glissees = [], debordants = [];
    let pire = 0;
    [...document.querySelectorAll('.sb-nav .sb-section, .sb-nav .sb-item')]
      .forEach(el => {
        const b = el.getBoundingClientRect();
        if (b.right > r.right + 1) { debord++; debordants.push(el.textContent.trim()); }
      });
    /* L'ICÔNE DÉSIGNE LA PREMIÈRE LIGNE d'un intitulé replié, pas le vide
       entre les deux — le défaut mesuré sur l'autre site du cabinet. */
    [...document.querySelectorAll('.sb-nav .sb-item')].forEach(a => {
      const ch = a.querySelector('.sb-icon');
      if (!ch) return;
      const li = parseFloat(getComputedStyle(a).lineHeight) || 20;
      const rb = a.getBoundingClientRect(), rc = ch.getBoundingClientRect();
      const texte = a.clientHeight - parseFloat(getComputedStyle(a).paddingTop) * 2;
      if (texte > li * 1.5) {
        replis++;
        const ecart = Math.abs((rc.top + rc.height / 2) - (rb.top + li / 2
          + parseFloat(getComputedStyle(a).paddingTop)));
        if (ecart > pire) pire = ecart;
        if (ecart > 6) { decale++; glissees.push(a.textContent.trim()); }
      }
    });
    return { debord, debordants: debordants.slice(0, 3), replis, decale,
             glissees: glissees.slice(0, 3), pire: Math.round(pire * 10) / 10,
             larg: Math.round(r.width) };
  });
  ok('aucun titre ni onglet ne déborde de la barre',
     !geo.err && geo.debord === 0,
     geo.err || (geo.debord + ' : ' + (geo.debordants || []).join(', ')),
     geo.err ? '' : 'barre de ' + geo.larg + ' px');
  ok('des intitulés se replient bel et bien — il y a donc de quoi mesurer',
     !geo.err && geo.replis > 0, geo.err,
     geo.err ? '' : geo.replis + ' intitulé(s) sur deux lignes');
  ok('…et l’icône y désigne LA PREMIÈRE LIGNE, pas le vide entre les deux',
     !geo.err && geo.decale === 0,
     geo.err || (geo.glissees || []).join(' | '),
     geo.err ? '' : 'pire écart ' + geo.pire + ' px, limite 6');

  // ── 7 ───────────────────────────────────────────────────────────────────
  titre('7. Ce que la barre faisait déjà, elle le fait encore');

  const survit = await sur(() => {
    const secs = [...document.querySelectorAll('.sb-nav .sb-section')];
    /* Le pager remonte de rubrique en rubrique par `offsetTop` : ajouter une
       icône dans le titre ne doit pas casser cet ordre. */
    const tops = secs.map(s => s.offsetTop);
    const croissants = tops.every((v, i) => i === 0 || v > tops[i - 1]);
    /* Les gestionnaires de clic sont lus dans l'attribut `onclick` par
       plusieurs modules (`hubGo`, `confOpen`, `aipdOpenFria`…). */
    const avecGo = [...document.querySelectorAll('.sb-item')]
      .filter(a => /go\('[\w-]+'/.test(a.getAttribute('onclick') || '')).length;
    /* Une recette voisine retrouve sa rubrique par le TEXTE du titre. */
    const parTexte = secs.filter(s => /Évaluer le risque/.test(s.textContent)).length;
    return { croissants, avecGo, total: document.querySelectorAll('.sb-item').length,
             parTexte };
  });
  ok('les rubriques restent dans l’ordre du document (le pager s’en sert)',
     !survit.err && survit.croissants === true, survit.err);
  ok('tous les onglets gardent leur gestionnaire de clic',
     !survit.err && survit.avecGo === survit.total, survit.err,
     survit.err ? '' : survit.avecGo + ' / ' + survit.total);
  ok('…et un titre reste retrouvable par son texte',
     !survit.err && survit.parTexte === 1, survit.err);

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
