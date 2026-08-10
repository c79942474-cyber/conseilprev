/* Deux aléas de plus à l'écran. Ce qui doit tenir devant un lecteur :
 * - chacun a son curseur, son libellé, sa formule et sa couleur ;
 * - pondérer les feux ou les inondations DÉPLACE le classement ;
 * - l'infobulle donne le rang recopiable, et pour un pays non classé elle dit
 *   POURQUOI — « hors de l'Union » et « hors des dix publiés » ne se
 *   confondent pas, et aucune des deux ne se lit comme un feu vert ;
 * - le pied de section porte l'échelle européenne : 18 Md€ en 2024, +110 %
 *   pour l'Île-de-France d'ici 2100.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = 'http://127.0.0.1:5401';
let ko = 0;
const ok = (n, c, d) => { console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : '')); if (!c) ko++; };

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1440, height: 1100 } });
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
  await pg.evaluate(() => chargerImplantation());
  await pg.waitForFunction(() => typeof IMPL !== 'undefined' && IMPL && IMPL.criteres, null, { timeout: 30000 });

  console.log('\n══ Les deux critères arrivent jusqu’à l’écran ══\n');
  const d = await pg.evaluate(() => ({
    n: IMPL.criteres.length,
    cles: IMPL.criteres.map(c => c.cle),
    socle: IMPL.criteres.filter(c => c.famille === 'socle').map(c => c.cle),
    aleas: IMPL.criteres.filter(c => c.famille === 'aleas').length,
    pf: IMPL_POIDS.feux, pi: IMPL_POIDS.inondations,
    version: IMPL.version,
    fr: (IMPL.pays.find(p => p.pays === 'FR') || {}).feux,
    fri: (IMPL.pays.find(p => p.pays === 'FR') || {}).inondations,
    seF: (IMPL.pays.find(p => p.pays === 'SE') || {}).notes.feux,
    chI: (IMPL.pays.find(p => p.pays === 'CH') || {}).notes.inondations,
    plF: (IMPL.pays.find(p => p.pays === 'PL') || {}).notes.feux,
  }));
  // Les six critères d'aléas s'AJOUTENT : le socle historique doit rester
  // intact et dans son ordre, sinon les poids réglés désigneraient d'autres
  // critères que ceux que le lecteur a vus.
  ok('les dix critères de socle sont intacts et dans l’ordre',
     d.socle.join(',') === 'carbone,mix,eau,climat,prix,parc,climat_physique,feux,inondations,pipeline', d.socle.join(','));
  ok('…et les six aléas s’y ajoutent, tous en famille « aleas »',
     d.aleas === 6, d.aleas);

  ok('feux et inondations en font partie',
     d.cles.includes('feux') && d.cles.includes('inondations'), d.cles.join(','));
  ok('chacun a un poids par défaut', d.pf === 1 && d.pi === 2, d.pf + ' / ' + d.pi);
  ok('référentiel 2026-08-d', d.version === '2026-08-d', d.version);
  ok('la France est 1re des feux en 2050, 2e en 2025',
     d.fr && d.fr.rang_2050 === 1 && d.fr.rang_2025 === 2, JSON.stringify(d.fr));
  ok('…et 2e des inondations, +23 % d’ici 2050',
     d.fri && d.fri.rang_2050 === 2 && d.fri.hausse_2025_2050_pct === 23,
     JSON.stringify(d.fri && d.fri.rang_2050));
  ok('la Suède, hors des dix feux, n’a PAS de note', d.seF === null, d.seF);
  ok('la Suisse, hors de l’Union, n’a PAS de note d’inondation', d.chI === null, d.chI);
  ok('le dixième des feux plafonne à 35 — une liste des pires ne sacre personne',
     d.plF === 35, d.plF);

  console.log('\n══ Curseurs, libellés, formules, couleurs ══\n');
  for (const c of ['feux', 'inondations']) {
    const n = await pg.locator('input[data-critere="' + c + '"]').count();
    ok('un curseur dédié à « ' + c + ' »', n === 1, n);
    const lab = await pg.locator('.imp-c-' + c + ' .imp-p-nom').innerText().catch(() => '');
    ok('…son intitulé nomme XDI et 2050', /XDI/.test(lab) && /2050/.test(lab), lab.trim().slice(0, 60));
    const col = await pg.locator('.imp-c-' + c).evaluate(
      e => getComputedStyle(e).getPropertyValue('--imp-c').trim()).catch(() => '');
    ok('…il a sa couleur propre', /^#[0-9A-Fa-f]{6}$/.test(col), col);
  }
  const sf = await pg.locator('.imp-c-feux .imp-p-src').innerText().catch(() => '');
  ok('la formule des feux prévient du biais de taille', /ABSOLU/.test(sf), sf.slice(0, 70));
  ok('…et du plafond à 35', /35/.test(sf));
  const si = await pg.locator('.imp-c-inondations .imp-p-src').innerText().catch(() => '');
  ok('celle des inondations exclut la submersion côtière', /submersion/.test(si), si.slice(0, 70));

  console.log('\n══ Pondérer un aléa DÉPLACE le classement ══\n');
  /* On regarde l'ORDRE COMPLET, pas le podium. La différence n'est pas un
   * détail de méthode : les trois premiers sont nordiques et ne sont classés
   * dans AUCUN des deux rapports, donc pondérer un aléa ne peut pas les
   * bouger — c'est la conséquence directe et voulue du principe « une donnée
   * absente est neutre, jamais bonne ». Un contrôle sur le podium seul se
   * serait déclaré en échec en accusant une mécanique qui fonctionne. Ce qui
   * doit bouger, et qu'on vérifie, c'est le rang des pays RÉELLEMENT classés. */
  const ordre = async () => pg.evaluate(() => {
    renderImplClassement();
    return IMPL.pays.filter(x => x.avis && implScore(x) !== null)
      .map(x => ({ p: x.pays, s: implScore(x) }))
      .sort((a, b) => b.s - a.s).map(l => l.p);
  });
  const base = await pg.evaluate(() => Object.assign({}, IMPL_POIDS));
  for (const [c, temoin] of [['feux', 'FR'], ['inondations', 'IT']]) {
    await pg.evaluate(k => { Object.keys(IMPL_POIDS).forEach(x => { IMPL_POIDS[x] = 1; });
                            IMPL_POIDS[k] = 0; }, c);
    const sans = await ordre();
    await pg.evaluate(k => { IMPL_POIDS[k] = 4; }, c);
    const avec = await ordre();
    const r0 = sans.indexOf(temoin) + 1, r4 = avec.indexOf(temoin) + 1;
    console.log('      ' + c + ' — poids 0 → ' + sans.slice(0, 5).join(' · ')
                + ' … ' + temoin + ' ' + r0 + 'e');
    console.log('      ' + c + ' — poids 4 → ' + avec.slice(0, 5).join(' · ')
                + ' … ' + temoin + ' ' + r4 + 'e\n');
    ok('l’ordre change quand on pondère « ' + c + ' »',
       JSON.stringify(sans) !== JSON.stringify(avec));
    ok('…et ' + temoin + ', premier des plus exposés, RECULE',
       r4 > r0, r0 + 'e → ' + r4 + 'e');
  }
  await pg.evaluate(p => { Object.keys(p).forEach(k => { IMPL_POIDS[k] = p[k]; });
                           renderImplClassement(); }, base);

  console.log('\n══ L’infobulle donne le rang, ou dit pourquoi il manque ══\n');
  const survoler = async code => {
    await pg.locator('[data-cres] [data-code="' + code + '"]').first()
      .dispatchEvent('mouseover').catch(() => {});
    await pg.waitForTimeout(320);
    return pg.locator('.cres-tip').innerText().catch(() => '');
  };
  const tfr = await survoler('FR');
  ok('l’infobulle de la France s’ouvre', tfr.length > 20, tfr.split('\n')[0]);
  ok('elle porte le rang de feu, recopiable dans un dossier',
     /1er des dix plus exposés en 2050/.test(tfr), (tfr.match(/feu de forêt[^\n]*/) || ['introuvable'])[0]);
  ok('…avec le rang 2025, qui montre le mouvement', /\(2e en 2025\)/.test(tfr));
  ok('…et le rang d’inondation avec sa hausse',
     /2e sur 27 en 2050 \(\+23 %/.test(tfr), (tfr.match(/inondation[^\n]*/) || ['introuvable'])[0]);
  ok('…et les deux critères apparaissent dans le détail des notes',
     /feu de forêt/i.test(tfr) && /Risque d’inondation|Risque d.inondation/.test(tfr));

  /* Le pays tiers à interroger est la NORVÈGE, pas la Suisse : le comparateur
   * ne classe que les pays dotés d'un avis, et la Suisse n'en a pas — sa carte
   * répond « hors Union européenne » sans jamais atteindre les critères. La
   * Norvège, elle, est classée ET hors Union : c'est le seul cas où la page
   * doit expliquer qu'un aléa n'a pas été mesuré pour un pays qu'elle note
   * par ailleurs. (Les textes suisses sont vérifiés côté module.) */
  const tno = await survoler('NO');
  ok('la Norvège, classée mais hors Union, le dit au lieu de se taire',
     /hors de l’Union, non analysé/.test(tno), (tno.match(/feu de forêt[^\n]*/) || ['introuvable'])[0]);
  ok('…sur les deux aléas', (tno.match(/hors de l’Union/g) || []).length >= 2,
     (tno.match(/inondation : [^\n·]*/) || ['introuvable'])[0]);
  ok('…et son score le compte comme MANQUANT, pas comme acquis',
     /critères sans donnée, exclus du calcul comme du diviseur/.test(tno));
  const tse = await survoler('SE');
  ok('la Suède dit « hors des dix publiés » — un motif DIFFÉRENT',
     /hors des dix publiés/.test(tse), (tse.match(/feu de forêt[^\n]*/) || ['introuvable'])[0]);
  ok('…tout en portant, elle, son rang d’inondation',
     /16e sur 27 en 2050/.test(tse), (tse.match(/inondation[^\n]*/) || ['introuvable'])[0]);
  const thr = await survoler('HR');
  ok('la Croatie dit qu’elle SORT des dix d’ici 2050',
     /sort des dix d’ici 2050/.test(thr), (thr.match(/feu de forêt[^\n]*/) || ['introuvable'])[0]);

  console.log('\n══ Le pied de section porte l’échelle européenne ══\n');
  const srcs = await pg.locator('#imp-sources').innerText().catch(() => '');
  ok('les deux rapports XDI 2025 sont cités en source',
     /août 2025/.test(srcs) && /septembre 2025/.test(srcs));
  ok('…avec les 18 milliards d’euros de 2024', /18 milliards/.test(srcs));
  ok('…les cinq pays qui concentrent les vingt régions les plus exposées',
     /Italie, Allemagne, France, Pologne et Belgique/.test(srcs));
  ok('…le +110 % francilien d’ici 2100', /110 % d’ici 2100/.test(srcs));
  ok('…et les 2 Md€ annuels de feux', /2 milliards/.test(srcs));
  ok('…en rappelant que 10 pays sur 27 seulement sont publiés',
     /10 premiers États membres sont publiés sur les 27/.test(srcs));
  ok('…et que les autres ne sont pas réputés sûrs', /pas réputés sûrs/.test(srcs));

  const colores = await pg.locator('#imp-classement [fill]:not([fill="none"])').count();
  ok('la carte du comparateur est toujours peinte', colores > 10, colores + ' formes');
  ok('aucune erreur JavaScript', err.length === 0, err.slice(0, 2).join(' | '));

  await nav.close();
  console.log('');
  console.log(ko ? ko + ' contrôle(s) en échec\n' : 'tout est vert\n');
  process.exit(ko ? 1 : 0);
})();
