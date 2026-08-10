/* Un critère qui existe dans le module et pas à l'écran ne sert personne. On
 * vérifie qu'il a son curseur, sa colonne, sa valeur brute — et surtout qu'il
 * DÉPLACE le classement quand on le pondère. */
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

  console.log('\n══ Le critère arrive jusqu’à l’écran ══\n');
  const d = await pg.evaluate(() => ({
    n: IMPL.criteres.length,
    cles: IMPL.criteres.map(c => c.cle),
    socle: IMPL.criteres.filter(c => c.famille === 'socle').map(c => c.cle),
    aleas: IMPL.criteres.filter(c => c.famille === 'aleas').length,
    poids: IMPL_POIDS.climat_physique,
    version: IMPL.version,
    fr: (IMPL.pays.find(p => p.pays === 'FR') || {}).climat_physique,
    se: (IMPL.pays.find(p => p.pays === 'SE') || {}).notes.climat_physique,
  }));
  // Les six critères d'aléas s'AJOUTENT : le socle historique doit rester
  // intact et dans son ordre, sinon les poids réglés désigneraient d'autres
  // critères que ceux que le lecteur a vus.
  ok('les dix critères de socle sont intacts et dans l’ordre',
     d.socle.join(',') === 'carbone,mix,eau,climat,prix,parc,climat_physique,feux,inondations,pipeline', d.socle.join(','));
  ok('…et les six aléas s’y ajoutent, tous en famille « aleas »',
     d.aleas === 6, d.aleas);

  ok('climat_physique en fait partie', d.cles.includes('climat_physique'), d.cles.join(','));
  ok('il a un poids par défaut', d.poids === 2, d.poids);
  ok('référentiel 2026-08-d', d.version === '2026-08-d', d.version);
  ok('la France porte 26 % à haut risque, 18 % après ingénierie',
     d.fr && d.fr.haut_risque_pct === 26 && d.fr.haut_risque_adapte_pct === 18, JSON.stringify(d.fr));
  ok('la Suède n’a PAS de note — hors classement', d.se === null, d.se);

  console.log('\n══ Il a son curseur et son libellé ══\n');
  const cur = await pg.locator('input[data-critere="climat_physique"]').count();
  ok('un curseur de poids lui est dédié', cur === 1, cur);
  const lab = await pg.locator('.imp-c-climat_physique .imp-p-nom').innerText().catch(() => '');
  ok('son intitulé nomme XDI', /XDI/.test(lab), lab.trim().slice(0, 60));
  const src = await pg.locator('.imp-c-climat_physique .imp-p-src').innerText().catch(() => '');
  ok('sa formule dit le sort des non-classés', /hors classement/.test(src), src.slice(0, 70));
  const srcs = await pg.locator('#imp-sources').innerText().catch(() => '');
  ok('la source XDI est citée dans le pied de section', /XDI/.test(srcs));

  console.log('\n══ …et il DÉPLACE réellement le classement ══\n');
  const podium = async () => pg.evaluate(() => {
    renderImplClassement();
    return [...document.querySelectorAll('.cres-p b')].map(e => e.textContent.trim());
  });
  await pg.evaluate(() => { IMPL_POIDS.climat_physique = 0; });
  const sans = await podium();
  await pg.evaluate(() => { IMPL_POIDS.climat_physique = 4; Object.keys(IMPL_POIDS)
    .forEach(k => { if (k !== 'climat_physique') IMPL_POIDS[k] = 1; }); });
  const avec = await podium();
  console.log('      poids 0 → ' + sans.join(' · '));
  console.log('      poids 4 → ' + avec.join(' · ') + '\n');
  ok('le podium change quand on pondère le risque climatique',
     JSON.stringify(sans) !== JSON.stringify(avec));

  console.log('\n══ La valeur brute est recopiable, la carte est colorée ══\n');
  await pg.evaluate(() => { IMPL_POIDS.climat_physique = 2; renderImplClassement(); });
  // La valeur brute vit dans l'INFOBULLE de la carte, construite au survol :
  // la chercher dans le HTML au repos ne prouvait rien, elle n'y est pas
  // encore. On survole donc la France, comme le ferait un lecteur.
  await pg.locator('[data-cres] [data-code="FR"]').first()
    .dispatchEvent('mouseover').catch(() => {});
  await pg.waitForTimeout(350);
  const tip = await pg.locator('.cres-tip').innerText().catch(() => '');
  ok('l’infobulle du pays s’ouvre', tip.length > 20, tip.split('\n')[0]);
  ok('elle porte la note du risque climatique et son poids',
     /Risque climatique physique/.test(tip), (tip.match(/Risque[^\n]*/) || [''])[0]);
  ok('elle porte la valeur brute XDI, recopiable dans un dossier',
     /XDI 26 % à haut risque/.test(tip), (tip.match(/XDI[^\n]*/) || ['introuvable'])[0]);
  ok('…avec la part restant après ingénierie', /18 % après ingénierie/.test(tip));
  ok('…et l’aléa moteur nommé', /submersion côtière/.test(tip));
  const colores = await pg.locator('#imp-classement [fill]:not([fill="none"])').count();
  ok('la carte du comparateur est bien peinte', colores > 10, colores + ' formes');
  ok('aucune erreur JavaScript', err.length === 0, err.slice(0, 2).join(' | '));

  await nav.close();
  console.log('');
  console.log(ko ? ko + ' contrôle(s) en échec\n' : 'tout est vert\n');
  process.exit(ko ? 1 : 0);
})();
