/* RECETTE — UN CLIC VERS SENTINEL NE COÛTE PLUS LA PAGE D'ACCUEIL
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LE SIGNALEMENT : « les 8 risques systémiques et leurs liens sur les blocs
 * ne fonctionnent plus ».
 *
 * CE QUE LA MESURE A TROUVÉ. Les huit liens étaient intacts — 145 × 35 px,
 * visibles, atteignables, bonne destination, vérifiés au clic. Mais un
 * visiteur NON CONNECTÉ qui cliquait atterrissait sur
 * `/login?suite=/sentinel?goto=carto` : un formulaire de connexion, à la
 * place de la page d'accueil. Le lien marchait ; c'est la visite qui
 * s'arrêtait.
 *
 * D'OÙ VENAIT LA RÉGRESSION. Un script attrape-tout ouvrait auparavant
 * « /sentinel » dans un NOUVEL ONGLET au clic sur une carte. On l'a retiré —
 * il menait au sommaire au lieu du module, et doublait l'appel — et on a
 * emporté avec lui la seule chose qu'il faisait bien : garder l'accueil
 * ouvert. Les vingt-sept liens publics vers Sentinel portent donc désormais
 * `target="_blank" rel="noopener"`.
 *
 * CE QU'UNE RÈGLE DE SOURCE NE PEUT PAS VOIR : qu'un vrai clic laisse la
 * page d'accueil en place ET ouvre un second onglet sur la bonne
 * destination. Cette recette attend l'événement d'ouverture d'onglet, puis
 * compare les deux URL.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5901';
let ko = 0, n = 0;
const ok = (t,c,d) => { n++; if(!c) ko++;
  console.log((c?'  OK   ':'  KO   ')+t+(d?' — '+d:'')); };
(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport:{width:1400,height:1000} });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator,'webdriver',{get:()=>false});
    Object.defineProperty(navigator,'plugins',{get:()=>[1,2,3]});
    Object.defineProperty(navigator,'languages',{get:()=>['fr-FR','fr']});
  });
  const pg = await ctx.newPage();
  const err = []; pg.on('pageerror', e => err.push(String(e).slice(0,160)));
  await pg.goto(BASE + '/', { waitUntil:'domcontentloaded' });
  await pg.waitForTimeout(2200);

  const att = await pg.evaluate(() => {
    const tous = [...document.querySelectorAll(
      '#risques a.risk-go, #services a.sv-card-go, #services a.sv-go')];
    return { total: tous.length,
      sansOnglet: tous.filter(a => a.getAttribute('target') !== '_blank')
                      .map(a => a.getAttribute('href')),
      sansNoopener: tous.filter(a => !(a.getAttribute('rel')||'').includes('noopener'))
                        .map(a => a.getAttribute('href')) };
  });
  ok('les 27 liens vers Sentinel s’ouvrent dans un nouvel onglet',
     att.total === 27 && att.sansOnglet.length === 0,
     att.sansOnglet.join(', ') || att.total + ' liens');
  ok('et aucun ne laisse la main sur la page qui l’a ouvert',
     att.sansNoopener.length === 0, att.sansNoopener.join(', '));

  /* ── UN VRAI CLIC : LA PAGE D'ACCUEIL RESTE, L'ONGLET S'OUVRE ─────── */
  const avant = pg.url();
  await pg.evaluate(() => document.querySelector('#risques .risk-go')
    .scrollIntoView({ block:'center', behavior:'instant' }));
  await pg.waitForTimeout(200);
  const b = await pg.evaluate(() => {
    const r = document.querySelector('#risques .risk-go').getBoundingClientRect();
    return { x: r.left + r.width/2, y: r.top + r.height/2 };
  });
  const [neuf] = await Promise.all([
    ctx.waitForEvent('page', { timeout: 8000 }).catch(() => null),
    pg.mouse.click(b.x, b.y)
  ]);
  await pg.waitForTimeout(1200);
  ok('la page d’accueil est TOUJOURS LÀ après le clic', pg.url() === avant,
     pg.url());
  ok('un nouvel onglet s’est ouvert sur la destination', !!neuf,
     neuf ? neuf.url() : 'aucun onglet');
  if (neuf) {
    await neuf.waitForTimeout(1500);
    ok('et il vise bien le module de la carte',
       /goto=carto/.test(neuf.url()), neuf.url());
  }
  ok('aucune erreur JavaScript', err.length === 0, err.join(' | '));
  await nav.close();
  console.log('\n' + (n-ko) + ' contrôles passés, ' + ko + ' en échec');
  process.exit(ko ? 1 : 0);
})().catch(e => { console.error('KO rompu : ' + e); process.exit(2); });
