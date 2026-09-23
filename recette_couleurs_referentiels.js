/* RECETTE — UNE COULEUR PAR RÉFÉRENTIEL DANS LA BARRE DE SENTINEL
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE : « dans le menu latéral de Sentinel, mettre les onze
 * référentiels avec chacun une couleur différente ».
 *
 * LES RÈGLES DE LA SUITE LISENT LE FICHIER ; CETTE RECETTE LIT L'ÉCRAN. Ce
 * qu'un fichier ne montre pas, et qui a été mesuré ici :
 *
 *   1. VINGT-HUIT ONGLETS N'ONT PAS DE DESSIN dans leur pastille. Teintée à
 *      9 %, elle laissait la couleur presque invisible : à l'écran, DORA et
 *      NIS 2 paraissaient gris. D'où le point — qu'on mesure ici au pixel.
 *   2. LA COULEUR PASSE PAR UNE VARIABLE (`--sb-ic`) : rien dans le fichier ne
 *      prouve que l'icône la lit. On compare donc la couleur CALCULÉE de
 *      chaque icône à la couleur déclarée pour son référentiel.
 *   3. LA TERRE CUITE DOIT GARDER LE DERNIER MOT au survol et sur l'onglet
 *      ouvert. C'est une affaire de spécificité : ça ne se voit qu'en
 *      survolant et en ouvrant pour de bon.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5901 node recette_couleurs_referentiels.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';

let ko = 0;
const ok = (t, cond, siKo, mesure) => {
  console.log((cond ? '  OK   ' : '  KO   ') + t
              + (mesure ? ' — ' + mesure : '')
              + (!cond && siKo ? ' — ' + siKo : ''));
  if (!cond) ko++;
};
const titre = t => console.log('\n══ ' + t + ' ══\n');

/* TOUT EST RELEVÉ DANS LE NAVIGATEUR, rien n'est recopié ici : les couleurs
   déclarées sont relues dans la feuille de style de la page, converties par
   le navigateur lui-même, puis comparées à ce qu'il a calculé. */
const RELEVE = () => {
  const enRvb = v => { const t = document.createElement('i');
    t.style.color = v; document.body.appendChild(t);
    const c = getComputedStyle(t).color; t.remove(); return c; };
  const declarees = {};
  for (const f of document.styleSheets) {
    let regles; try { regles = f.cssRules; } catch (e) { continue; }
    for (const r of regles || []) {
      const m = /^\.sb-nav \.sb-item\[data-norme="([a-z0-9_]+)"\]$/.exec(r.selectorText || '');
      if (m) declarees[m[1]] = enRvb(r.style.getPropertyValue('--sb-ic').trim());
    }
  }
  const onglets = [...document.querySelectorAll('.sb-nav .sb-item')].map(a => {
    const ic = a.querySelector('.sb-icon');
    const vide = !!ic && ic.childNodes.length === 0;
    return {
      norme: a.getAttribute('data-norme'),
      grp: a.getAttribute('data-grp'),
      label: a.textContent.trim(),
      actif: a.classList.contains('on'),
      icone: ic ? getComputedStyle(ic).color : null,
      vide,
      point: vide ? getComputedStyle(ic, '::before').backgroundColor : null,
      pointLarg: vide ? getComputedStyle(ic, '::before').width : null,
      texte: getComputedStyle(a).color,
      fond: getComputedStyle(a).backgroundColor
    };
  });
  const titres = [...document.querySelectorAll('.sb-nav .sb-section[data-grp]')].map(s => {
    const svg = s.querySelector('svg.sb-sec-ic');
    return { grp: s.getAttribute('data-grp'),
             conformite: s.getAttribute('data-fam') === 'conformite',
             icone: svg ? getComputedStyle(svg).color : null };
  });
  const racine = getComputedStyle(document.documentElement);
  return { declarees, onglets, titres,
           accent: enRvb(racine.getPropertyValue('--accent').trim()),
           accent2: enRvb(racine.getPropertyValue('--accent2').trim()),
           blanc: enRvb('#fff') };
};

const rvb = s => (s || '').match(/\d+/g).slice(0, 3).map(Number);
const neutre = s => { const [r, g, b] = rvb(s);
  return Math.max(r, g, b) - Math.min(r, g, b) <= 8; };

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1440, height: 1000 } });
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
  await pg.waitForSelector('.sb-item[data-norme]', { state: 'attached', timeout: 15000 });
  await pg.waitForTimeout(1500);

  const R = await sur(RELEVE);
  if (R.err) { ok('la barre a pu être relevée', false, R.err); await nav.close(); process.exit(2); }
  const auRepos = R.onglets.filter(o => !o.actif);
  const deNorme = auRepos.filter(o => o.norme);
  const parNorme = {};
  deNorme.forEach(o => { (parNorme[o.norme] = parNorme[o.norme] || []).push(o); });

  // ── 1 ───────────────────────────────────────────────────────────────────
  titre('1. Onze référentiels, onze couleurs — lues à l’écran');

  const normes = Object.keys(parNorme);
  ok('les onze référentiels sont dans la barre', normes.length === 11,
     normes.join(', '), normes.length + ' référentiel(s)');
  const bigarres = normes.filter(n => new Set(parNorme[n].map(o => o.icone)).size !== 1);
  ok('…les onglets d’un même référentiel portent UNE seule couleur',
     bigarres.length === 0, bigarres.join(', '));
  const couleurs = new Set(normes.map(n => parNorme[n][0].icone));
  ok('LE POINT QUI DÉCIDE — onze couleurs DISTINCTES à l’écran',
     couleurs.size === 11, null, couleurs.size + ' couleur(s) calculée(s)');
  const ecarts = normes.filter(n => parNorme[n][0].icone !== R.declarees[n])
    .map(n => n + ' : ' + parNorme[n][0].icone + ' ≠ ' + R.declarees[n]);
  ok('…et chacune est EXACTEMENT celle déclarée pour son référentiel — '
     + 'l’icône lit bien la variable',
     Object.keys(R.declarees).length === 11 && ecarts.length === 0,
     ecarts.slice(0, 3).join(' | ') || Object.keys(R.declarees).length + ' déclarée(s)');

  // ── 2 ───────────────────────────────────────────────────────────────────
  titre('2. La pastille sans dessin porte la couleur par un point');

  const vides = deNorme.filter(o => o.vide);
  ok('des pastilles sans dessin existent bel et bien — il y a de quoi mesurer',
     vides.length >= 20, null, vides.length + ' pastille(s) vide(s)');
  const sansPoint = vides.filter(o => o.point !== o.icone || o.pointLarg === 'auto'
                                      || parseFloat(o.pointLarg) < 6);
  ok('LE POINT QUI DÉCIDE — chaque pastille vide montre un point de la couleur '
     + 'de son référentiel',
     sansPoint.length === 0,
     sansPoint.slice(0, 3).map(o => o.label + ' (' + o.point + ')').join(' | '),
     vides.length ? 'point de ' + vides[0].pointLarg : '');

  // ── 3 ───────────────────────────────────────────────────────────────────
  titre('3. La couleur ne teint ni le texte ni le fond de l’onglet');

  const autres = auRepos.filter(o => !o.norme && o.grp !== 'taux-conformite');
  const textes = new Set(deNorme.map(o => o.texte));
  ok('tous les onglets de référentiel écrivent leur nom dans la MÊME encre',
     textes.size === 1, [...textes].join(' | '), [...textes][0]);
  ok('…qui est celle de n’importe quel autre onglet',
     autres.length > 0 && textes.has(autres[0].texte), autres[0] && autres[0].texte);
  const fonds = new Set(deNorme.map(o => o.fond));
  ok('…et leur fond est celui des autres onglets',
     fonds.size === 1 && autres.length > 0 && fonds.has(autres[0].fond),
     [...fonds].join(' | '));

  // ── 4 ───────────────────────────────────────────────────────────────────
  titre('4. Le titre du tiroir : sa couleur, ou aucune');

  const deTiroir = {};
  deNorme.forEach(o => { (deTiroir[o.grp] = deTiroir[o.grp] || new Set()).add(o.norme); });
  const voues = R.titres.filter(t => t.conformite && deTiroir[t.grp]
                                    && deTiroir[t.grp].size === 1);
  const malTeints = voues.filter(t => t.icone !== parNorme[[...deTiroir[t.grp]][0]][0].icone)
    .map(t => t.grp + ' (' + t.icone + ')');
  ok('chaque tiroir voué à un référentiel porte SA couleur sur son titre',
     voues.length >= 8 && malTeints.length === 0, malTeints.join(' | '),
     voues.length + ' tiroir(s) voué(s)');
  const aPersonne = R.titres.filter(t => t.conformite && !voues.includes(t));
  const colores = aPersonne.filter(t => !neutre(t.icone)).map(t => t.grp + ' (' + t.icone + ')');
  ok('LE POINT QUI DÉCIDE — un tiroir à personne reste NEUTRE, pas en terre cuite',
     aPersonne.length >= 2 && colores.length === 0, colores.join(' | '),
     aPersonne.map(t => t.grp).join(', '));
  const empreinte = auRepos.find(o => !o.norme && o.grp === 'rgpd-et-privacy');
  ok('un onglet sans référentiel reprend la couleur du tiroir qui le range',
     !!empreinte && empreinte.icone === (parNorme.rgpd || [{}])[0].icone,
     empreinte ? empreinte.label + ' ' + empreinte.icone : 'aucun relevé');

  // ── 5 ───────────────────────────────────────────────────────────────────
  titre('5. L’IA Act, rangé sous « Pilotage », garde la sienne');

  const ia = deNorme.find(o => o.norme === 'ia_act');
  const voisins = auRepos.filter(o => o.grp === 'pilotage' && !o.norme);
  ok('l’IA Act ne prend pas la terre cuite de sa rubrique',
     !!ia && voisins.length > 0 && voisins.every(v => v.icone !== ia.icone),
     ia ? ia.icone : 'introuvable', ia ? ia.icone + ' parmi ' + voisins.length + ' voisin(s)' : '');

  // ── 6 ───────────────────────────────────────────────────────────────────
  titre('6. La terre cuite garde le dernier mot');

  /* LES TIROIRS SONT REPLIÉS PAR DÉFAUT : on ouvre celui de NIS 2 comme le
     ferait un utilisateur, puis on survole et on ouvre pour de bon. */
  await sur(() => { const s = document.querySelector('.sb-section[data-grp="nis2"]');
    if (s && s.getAttribute('aria-expanded') !== 'true') s.click(); });
  await pg.waitForTimeout(300);
  const cible = pg.locator('.sb-item[data-norme="nis2"]').nth(1);
  const repos = await cible.evaluate(a => getComputedStyle(a.querySelector('.sb-icon')).color);
  await cible.hover();
  await pg.waitForTimeout(450);
  const survol = await cible.evaluate(a => { const ic = a.querySelector('.sb-icon');
    return { ic: getComputedStyle(ic).color, pt: getComputedStyle(ic, '::before').backgroundColor }; });
  ok('LE POINT QUI DÉCIDE — au survol, l’icône passe à la terre cuite',
     survol.ic === R.accent2 && repos !== R.accent2, 'au repos ' + repos + ', survolée ' + survol.ic,
     repos + ' → ' + survol.ic);
  ok('…et le point la suit, parce qu’il prend `currentColor`',
     survol.pt === R.accent2, survol.pt);
  await pg.mouse.move(900, 500);
  await cible.click();
  await pg.waitForTimeout(700);
  const ouvert = await cible.evaluate(a => { const ic = a.querySelector('.sb-icon');
    return { on: a.classList.contains('on'), fond: getComputedStyle(ic).backgroundColor,
             pt: getComputedStyle(ic, '::before').backgroundColor }; });
  ok('l’onglet ouvert a sa pastille PLEINE et terre cuite',
     ouvert.on && ouvert.fond === R.accent, ouvert.fond);
  ok('…et son point passe au blanc, lisible sur ce fond', ouvert.pt === R.blanc, ouvert.pt);
  const frere = await pg.locator('.sb-item[data-norme="nis2"]:not(.on)').first()
    .evaluate(a => getComputedStyle(a.querySelector('.sb-icon')).color);
  ok('…pendant que ses voisins gardent la couleur de NIS 2',
     frere === (parNorme.nis2 || [{}])[0].icone, frere);

  // ── 7 ───────────────────────────────────────────────────────────────────
  titre('7. Rien ne s’est cassé en route');
  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko ? ko + ' contrôle(s) en échec' : 'TOUT EST VERT'));
  await nav.close();
  process.exit(ko ? 1 : 0);
})();
