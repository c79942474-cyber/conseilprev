/* RECETTE — LE BANDEAU DE CHIFFRES DE L'ACCUEIL
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE : « remplacer 6 par 25 normes couvertes ».
 *
 * CE QUE LA MESURE A TROUVÉ AVANT DE CHANGER LE CHIFFRE. Le bandeau annonçait
 * SIX normes couvertes ; trente-cinq lignes plus bas, le même écran titre
 * « 9 normes maîtrisées » au-dessus d'une grille de neuf cartes. On ne peut
 * pas maîtriser ce qu'on ne couvre pas : les deux nombres se contredisaient,
 * et aucune règle ne tenait le bandeau — c'était le seul bloc chiffré de
 * l'accueil que rien ne surveillait.
 *
 * CE QUE LES RÈGLES PYTHON NE PEUVENT PAS VOIR. `applyLang` remplace
 * l'innerHTML de tout porteur de `data-i18n`. Le LIBELLÉ doit changer avec la
 * langue, le CHIFFRE ne doit pas bouger : seule une bascule réelle, dans les
 * trois langues et retour, le prouve.
 *
 * CE QUI RESTE UNE REVENDICATION, ET QUI EST DIT COMME TEL. « 25 normes
 * couvertes » ne se compte nulle part dans ce dépôt : les énumérations
 * donnent onze normes au module de conformité, sept cadres d'explication,
 * dix-neuf références ISO tolérées. Le chiffre appartient au cabinet. Ce qui
 * se mesure, c'est sa cohérence avec le reste de la page.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:6061';
let ko = 0, n = 0;
const ok = (t, c, d) => { n++; if (!c) ko++;
  console.log((c ? '  OK   ' : '  KO   ') + t + (d ? ' — ' + d : '')); };
const RELEVE = () => [...document.querySelectorAll('.sb2 .sv')].map(v => ({
  n: (v.querySelector('.sn') || {}).textContent,
  l: (v.querySelector('.slb') || {}).textContent }));
(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1400, height: 1000 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator,'webdriver',{get:()=>false});
    Object.defineProperty(navigator,'plugins',{get:()=>[1,2,3]});
    Object.defineProperty(navigator,'languages',{get:()=>['fr-FR','fr']});
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e).slice(0,160)));
  await pg.goto(BASE + '/', { waitUntil: 'domcontentloaded' });
  await pg.waitForTimeout(2200);

  const b = await pg.evaluate(RELEVE);
  ok('les cinq chiffres sont à l’écran', b.length === 5, b.length + ' cases');
  const couv = b.find(x => /couvertes|covered|Normen/i.test(x.l));
  ok('« Normes couvertes » affiche 25', couv && couv.n === '25',
     couv ? couv.n + ' · ' + couv.l : 'case introuvable');

  /* LE CHIFFRE NE DOIT PAS BOUGER AVEC LA LANGUE : seul le libellé change. */
  for (const lg of ['en', 'de', 'fr']) {
    await pg.evaluate((l) => {
      if (typeof window.setLang === 'function') return window.setLang(l);
      window.LANG = l;
      if (typeof window.applyLang === 'function') window.applyLang();
    }, lg);
    await pg.waitForTimeout(450);
    const x = await pg.evaluate(RELEVE);
    const c = x[2];
    ok('en ' + lg + ', le chiffre reste 25 et le libellé se traduit',
       c && c.n === '25' && c.l && c.l.trim().length > 3,
       c ? c.n + ' · ' + c.l : 'case perdue');
  }

  /* LE BANDEAU SE COMPTE AUSSI CONTRE CE QUE LA PAGE MONTRE PLUS BAS. */
  const page = await pg.evaluate(() => ({
    risques: document.querySelectorAll('#risques .risk-card').length,
    titre: (document.querySelector('[data-i18n="nr.ttl"]') || {}).textContent
  }));
  ok('le bandeau compte les risques que la page montre',
     b[1] && parseInt(b[1].n, 10) === page.risques,
     b[1] ? b[1].n + ' annoncés, ' + page.risques + ' cartes' : '');
  const m = /(\d+)\s+normes/i.exec(page.titre || '') || /(\d+)\s+standards/i.exec(page.titre || '');
  ok('on ne maîtrise pas plus de normes qu’on n’en couvre',
     m && parseInt(couv.n, 10) >= parseInt(m[1], 10),
     m ? couv.n + ' couvertes · ' + m[1] + ' maîtrisées' : 'titre : ' + page.titre);

  for (const w of [1400, 900, 390]) {
    await pg.setViewportSize({ width: w, height: 900 });
    await pg.waitForTimeout(350);
    const r = await pg.evaluate(() => {
      const deb = Math.max(0, document.documentElement.scrollWidth
                            - document.documentElement.clientWidth);
      const sv = document.querySelector('.sb2 .sv .sn');
      sv.scrollIntoView({ block:'center', behavior:'instant' });
      return { deb, visible: sv.checkVisibility({ checkVisibilityCSS:true,
        contentVisibilityAuto:true, opacityProperty:true, visibilityProperty:true }),
        larg: Math.round(sv.getBoundingClientRect().width) };
    });
    ok('à ' + w + ' px : rien ne déborde et le chiffre se lit',
       r.deb === 0 && r.visible && r.larg > 8, JSON.stringify(r));
  }
  ok('aucune erreur JavaScript', err.length === 0, err.join(' | '));
  await nav.close();
  console.log('\n' + (n - ko) + ' contrôles passés, ' + ko + ' en échec');
  process.exit(ko ? 1 : 0);
})().catch(e => { console.error('KO rompu : ' + e); process.exit(2); });
