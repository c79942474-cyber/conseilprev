/* Le curseur d'année promet un « état annoncé au ». Un compteur figé tiendrait
 * cette promesse à vide : on vérifie donc qu'il BOUGE, où la donnée le permet,
 * et qu'il DIT ce qu'elle ne permet pas.
 *
 * Ce qu'on a corrigé, et que ce fichier surveille : l'estompe reposait sur
 * `annee_service`, qu'AUCUN projet ne porte. Le test était faux à toutes les
 * années, et glisser le curseur de 2025 à 2030 ne changeait rien à l'écran —
 * ni les drapeaux, ni les compteurs. Désormais un projet entre au parc à son
 * HORIZON ANNONCÉ, et les douze projets sans calendrier public restent visibles
 * à toutes les années plutôt que d'être rejetés dans un avenir inventé. */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = 'http://127.0.0.1:5401';
let ko = 0;
const ok = (n, c, d) => { console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : '')); if (!c) ko++; };

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1440, height: 950 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));
  await pg.goto(BASE + '/auth/recette_locale_idf_0123456789abcdef', { waitUntil: 'domcontentloaded' });
  await pg.goto(BASE + '/panorama', { waitUntil: 'networkidle' });
  await pg.waitForFunction(() => document.getElementById('sia-ob'), null, { timeout: 30000 });

  /* Un relevé complet à une année : compteurs, et ce que la carte DESSINE
     vraiment. Compter les anneaux plutôt que croire le compteur : c'est le seul
     moyen de savoir si le curseur a touché l'écran ou seulement un nombre. */
  const lire = async (an) => pg.evaluate((a) => {
    DC_HORIZON = a; renderDC(true); majComptes();
    const g = document.querySelector('#panmap #dc-couche');
    const cs = Array.from(g.querySelectorAll('circle[stroke]'));
    return { dc: +document.getElementById('dc-n').textContent,
             hors: document.getElementById('dc-hors').textContent.trim(),
             sia: +document.getElementById('sia-n').textContent,
             ob: +document.getElementById('sia-ob').textContent,
             or: cs.filter(c => c.getAttribute('stroke') === '#C9A227').length,
             pointilles: cs.filter(c => c.getAttribute('stroke-dasharray')).length,
             estompes: g.querySelectorAll('.dc-pt[opacity], .dc-reg[opacity]').length,
             /* Sites DÉJÀ ouverts mais après l'année lue : ils sont estompés au
                même titre qu'un projet annoncé plus tard, sans être un projet.
                Les deux statuts corrigés en 2026-08-d en font partie. */
             pasEncore: (DC.sites || []).filter(s => s.statut === 'service'
               && s.annee_service && s.annee_service > a).length,
             parc: parcAu(a) };
  }, an);

  console.log('\n══ 1. Les comptes suivent le curseur, année par année ══\n');
  const t = {};
  for (const a of [2024, 2025, 2026, 2027, 2028, 2029, 2030]) t[a] = await lire(a);
  console.log('      année   parc   attendus   au-delà   sans date   anneaux or   estompés');
  for (const a of Object.keys(t)) console.log('       ' + a + '    ' + String(t[a].dc).padStart(4)
    + String(t[a].parc.attendus).padStart(10) + String(t[a].parc.plusTard).padStart(10)
    + String(t[a].parc.sansDate).padStart(12) + String(t[a].or).padStart(13)
    + String(t[a].estompes).padStart(11));
  console.log('');
  ok('la vague de conformité arrive : 0 en 2024', t[2024].ob === 0, t[2024].ob);
  ok('…2 dès 2025 (pratiques interdites)', t[2025].ob === 2, t[2025].ob);
  ok('…40 en 2026 (annexe III et GPAI)', t[2026].ob === 40, t[2026].ob);
  ok('le compte des systèmes sous obligation BOUGE vraiment',
     new Set([t[2024].ob, t[2025].ob, t[2026].ob]).size === 3);
  ok('les cas documentés suivent l’année du relevé',
     t[2024].sia === 70 && t[2025].sia === 72, t[2024].sia + ' → ' + t[2025].sia);

  console.log('\n══ 2. LE point signalé : les constructions prévues apparaissent ══\n');
  const parc = Object.keys(t).map(a => t[a].dc);
  ok('le parc CHANGE le long du curseur — c’est ce qui manquait',
     new Set(parc).size > 1, parc.join(' → '));
  ok('…et il ne décroît jamais : un site ouvert ne referme pas',
     parc.every((v, i) => i === 0 || v >= parc[i - 1]), parc.join(' → '));
  ok('225 sites en 2024, 233 en 2030', t[2024].dc === 225 && t[2030].dc === 233,
     t[2024].dc + ' → ' + t[2030].dc);
  ok('le saut de 2027 vaut cinq chantiers annoncés pour cette année-là',
     t[2027].dc - t[2026].dc === 5 && t[2027].parc.attendus === 5,
     t[2026].dc + ' → ' + t[2027].dc);
  ok('…et Fos-sur-Mer s’ajoute en 2028', t[2028].dc - t[2027].dc === 1
     && t[2028].parc.attendus === 6, t[2027].dc + ' → ' + t[2028].dc);
  ok('les six projets datés sont TOUS entrés au parc en 2030',
     t[2030].parc.attendus === 6 && t[2030].parc.plusTard === 0,
     JSON.stringify(t[2030].parc));

  console.log('\n══ 3. Ce que le curseur DESSINE, pas seulement ce qu’il compte ══\n');
  ok('aucun anneau doré avant la première échéance',
     t[2024].or === 0 && t[2026].or === 0, t[2026].or);
  ok('cinq anneaux dorés en 2027, six en 2028',
     t[2027].or === 5 && t[2028].or === 6, t[2027].or + ' puis ' + t[2028].or);
  ok('…et les projets encore à venir sont estompés, en nombre décroissant',
     t[2024].estompes === 8 && t[2026].estompes === 6 && t[2028].estompes === 0,
     [t[2024], t[2026], t[2028]].map(x => x.estompes).join(' → '));
  /* Or et estompe se relaient : à chaque année, un site daté est dans l'un ou
     dans l'autre, jamais nulle part. La somme n'est pas constante — elle vaut
     les six projets datés PLUS les sites en service pas encore ouverts, dont
     les deux statuts corrigés (Waltham Cross 2025, Eclairion 2026). */
  ok('or et estompe se relaient exactement : rien ne disparaît entre deux états',
     Object.keys(t).every(a => t[a].or + t[a].estompes === 6 + t[a].pasEncore),
     Object.keys(t).map(a => t[a].or + '+' + t[a].estompes + '/' + t[a].pasEncore).join(' '));
  ok('…et les deux sites corrigés sortent bien de l’estompe à leur ouverture',
     t[2024].pasEncore === 2 && t[2025].pasEncore === 1 && t[2026].pasEncore === 0,
     [2024, 2025, 2026].map(a => t[a].pasEncore).join(' → '));
  ok('les douze projets sans date restent visibles à TOUTES les années',
     Object.keys(t).every(a => t[a].parc.sansDate === 12 && t[a].pointilles === 12),
     Object.keys(t).map(a => t[a].pointilles).join(' '));
  // DISCRIMINATION : sans horizon, les six projets datés seraient dans le même
  // sac que les douze autres et le curseur n'aurait toujours rien à montrer.
  ok('…et ils ne sont PAS confondus avec les projets datés',
     t[2030].parc.sansDate === 12 && t[2030].parc.attendus === 6);

  console.log('\n══ 4. …et le compteur dit ce que la donnée ne permet pas ══\n');
  ok('les projets sans date sont comptés À PART, en toutes lettres',
     /12 projets sans date publiée/.test(t[2030].hors), t[2030].hors);
  ok('en 2024, la barre annonce aussi les annonces au-delà',
     /8 annoncés au-delà/.test(t[2024].hors), t[2024].hors);
  ok('en 2028, plus rien « au-delà » : la phrase disparaît au lieu d’afficher 0',
     !/au-delà/.test(t[2028].hors), t[2028].hors);
  ok('…et les six attendus sont dits « d’ici là », pas « en service »',
     /dont 6 attendus d’ici là/.test(t[2028].hors), t[2028].hors);
  ok('le total affiché n’avale ni les sans-date ni les abandons',
     t[2030].dc + t[2030].parc.sansDate + 4 === 249,
     t[2030].dc + ' + 12 sans date + 4 abandons = 249');

  console.log('\n══ 5. Discrimination : l’ancienne règle, rejouée sur cette page ══\n');
  /* On remet en place le test d'AVANT — « estompé si `annee_service` est
     postérieure à l'année lue et que le site n'est pas en service » — et on
     redemande le même parcours d'années. S'il faisait bouger quoi que ce soit,
     le défaut signalé n'aurait pas existé et tout ce qui précède ne prouverait
     rien. On restaure ensuite la vraie règle. */
  const ancien = await pg.evaluate(() => {
    const vrai = etatDC;
    etatDC = function (s, annee) {
      if (s.statut === 'abandonne') return 'abandonne';
      const futur = s.annee_service && s.annee_service > annee && s.statut !== 'service';
      return futur ? 'plus_tard' : 'service';
    };
    const r = {};
    for (const a of [2024, 2026, 2028, 2030]) {
      DC_HORIZON = a; renderDC(true); majComptes();
      r[a] = { dc: +document.getElementById('dc-n').textContent,
               or: document.querySelectorAll('#dc-couche circle[stroke="#C9A227"]').length };
    }
    etatDC = vrai;
    DC_HORIZON = 2030; renderDC(true); majComptes();
    return r;
  });
  const av = Object.keys(ancien).map(a => ancien[a].dc);
  ok('avec l’ancienne règle, le parc ne bouge plus d’un site',
     new Set(av).size === 1, av.join(' → '));
  ok('…et aucun chantier annoncé n’apparaît jamais',
     Object.keys(ancien).every(a => ancien[a].or === 0),
     Object.keys(ancien).map(a => ancien[a].or).join(' '));
  ok('…c’est bien le défaut signalé : un curseur sans effet',
     ancien[2024].dc === ancien[2030].dc, ancien[2024].dc);
  ok('la vraie règle est bien revenue',
     await pg.evaluate(() => parcAu(2030).attendus) === 6);

  console.log('\n══ 6. La légende explique les trois signes ══\n');
  const lg = await pg.evaluate(() => document.getElementById('lg-dc').textContent);
  ok('elle annonce ce que montre le curseur',
     /Ce que montre le curseur d’année/.test(lg));
  ok('anneau doré = projet attendu d’ici l’année choisie',
     /anneau doré.*attendu/.test(lg), lg.slice(0, 0));
  ok('estompé = annoncé au-delà', /estompé.*au-delà/.test(lg));
  ok('pointillé = sans date publiée, et le compte est donné',
     /anneau pointillé.*sans date publiée \(12 sur 18\)/.test(lg));
  ok('…et dit qu’ils sont montrés à toutes les années',
     /montré à toutes les années/.test(lg));

  console.log('\n══ 7. Le curseur réel produit le même résultat que l’appel direct ══\n');
  await pg.evaluate(() => { DC_HORIZON = 2030; renderDC(true); majComptes(); });
  await pg.locator('#dc-horizon').fill('2025');
  await pg.locator('#dc-horizon').dispatchEvent('input');
  await pg.waitForTimeout(250);
  const apres = await pg.evaluate(() => ({
    an: document.getElementById('dc-horizon-v').textContent,
    ob: +document.getElementById('sia-ob').textContent,
    dc: +document.getElementById('dc-n').textContent,
    or: document.querySelectorAll('#dc-couche circle[stroke="#C9A227"]').length }));
  ok('glisser le curseur à 2025 met à jour l’affichage',
     apres.an === '2025' && apres.ob === 2 && apres.dc === 226, JSON.stringify(apres));
  ok('…y compris les anneaux : le glissement redessine, il n’écrit pas qu’un nombre',
     apres.or === 0, apres.or);
  await pg.locator('#dc-horizon').fill('2028');
  await pg.locator('#dc-horizon').dispatchEvent('input');
  await pg.waitForTimeout(250);
  const fin = await pg.evaluate(() => ({
    dc: +document.getElementById('dc-n').textContent,
    or: document.querySelectorAll('#dc-couche circle[stroke="#C9A227"]').length,
    n: document.querySelectorAll('#dc-horizon').length }));
  ok('…et repartir vers 2028 fait réapparaître les six chantiers',
     fin.dc === 233 && fin.or === 6, JSON.stringify(fin));
  ok('le curseur n’a pas été recréé sous le doigt', fin.n === 1, fin.n);

  console.log('\n══ 8. La barre et la légende sont lisibles ══\n');
  const px = async (sel, prop) => pg.evaluate(([s, p]) => {
    const e = document.querySelector(s); return e ? getComputedStyle(e)[p] : null; }, [sel, prop]);
  ok('la barre est passée de 10 à 12 px', await px('.map-barre', 'fontSize') === '12px',
     await px('.map-barre', 'fontSize'));
  ok('les lignes de légende à 11.5 px', await px('#lg-dc .lg-row', 'fontSize') === '11.5px',
     await px('#lg-dc .lg-row', 'fontSize'));
  ok('le curseur est plus large', await px('#dc-horizon', 'width') === '130px',
     await px('#dc-horizon', 'width'));
  ok('la barre ne déborde pas de la carte', await pg.evaluate(() => {
    const b = document.querySelector('.map-barre'), m = document.getElementById('panmap');
    return b.getBoundingClientRect().width <= m.getBoundingClientRect().width + 1; }));
  ok('aucune erreur JavaScript', err.length === 0, err.slice(0, 2).join(' | '));

  await nav.close();
  console.log('');
  console.log(ko ? ko + ' contrôle(s) en échec\n' : 'tout est vert\n');
  process.exit(ko ? 1 : 0);
})();
