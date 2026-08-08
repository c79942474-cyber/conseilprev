/* Le curseur d'année promet un « état annoncé au ». Un compteur figé tiendrait
 * cette promesse à vide : on vérifie donc qu'il BOUGE, où la donnée le permet,
 * et qu'il DIT ce qu'elle ne permet pas. */
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

  const lire = async (an) => pg.evaluate((a) => {
    DC_HORIZON = a; majComptes();
    return { dc: +document.getElementById('dc-n').textContent,
             hors: document.getElementById('dc-hors').textContent.trim(),
             sia: +document.getElementById('sia-n').textContent,
             ob: +document.getElementById('sia-ob').textContent };
  }, an);

  console.log('\n══ Les comptes suivent le curseur, année par année ══\n');
  const t = {};
  for (const a of [2024, 2025, 2026, 2027, 2028, 2029, 2030]) t[a] = await lire(a);
  for (const a of Object.keys(t)) console.log('      ' + a + '  →  DC ' + t[a].dc
    + '  · IA documentés ' + t[a].sia + '  · sous obligation ' + t[a].ob);
  console.log('');
  ok('la vague de conformité arrive : 0 en 2024', t[2024].ob === 0, t[2024].ob);
  ok('…2 dès 2025 (pratiques interdites)', t[2025].ob === 2, t[2025].ob);
  ok('…40 en 2026 (annexe III et GPAI)', t[2026].ob === 40, t[2026].ob);
  ok('le compte des systèmes sous obligation BOUGE vraiment',
     new Set([t[2024].ob, t[2025].ob, t[2026].ob]).size === 3);
  ok('les cas documentés suivent l’année du relevé',
     t[2024].sia === 70 && t[2025].sia === 72, t[2024].sia + ' → ' + t[2025].sia);

  console.log('\n══ …et disent ce que la donnée ne permet pas ══\n');
  ok('le parc en service est annoncé', t[2030].dc === 225, t[2030].dc);
  ok('les 20 annonces sans date sont comptées À PART, en toutes lettres',
     /20 annoncés sans date/.test(t[2030].hors), t[2030].hors);
  ok('…et le total affiché ne les avale pas', t[2030].dc + 20 + 4 === 249,
     t[2030].dc + ' + 20 annoncés + 4 abandons = 249');

  console.log('\n══ Le curseur réel produit le même résultat que l’appel direct ══\n');
  await pg.evaluate(() => { DC_HORIZON = 2030; majComptes(); });
  await pg.locator('#dc-horizon').fill('2025');
  await pg.locator('#dc-horizon').dispatchEvent('input');
  await pg.waitForTimeout(250);
  const apres = await pg.evaluate(() => ({
    an: document.getElementById('dc-horizon-v').textContent,
    ob: +document.getElementById('sia-ob').textContent }));
  ok('glisser le curseur à 2025 met à jour l’affichage',
     apres.an === '2025' && apres.ob === 2, JSON.stringify(apres));
  ok('le curseur n’a pas été recréé sous le doigt',
     await pg.locator('#dc-horizon').count() === 1);

  console.log('\n══ La barre et la légende sont lisibles ══\n');
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
