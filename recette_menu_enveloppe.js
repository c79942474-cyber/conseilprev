/* LE MODULE « ENVELOPPE D'INVESTISSEMENT » DANS LE MENU DE SENTINEL.
 *
 * Ce que ce contrôle éprouve, et que recette_vues.js ne voit pas : le MENU.
 * recette_vues.js ouvre /enveloppe directement et prouve que la vue s'y
 * applique ; il ne dit rien de la façon dont on y arrive. Or c'était la
 * demande — un module à part, dans « Évaluer le risque », à la suite du
 * panorama, parce que c'en est la suite : on situe le terrain, puis on chiffre.
 *
 * MÉNAGER LE LIMITEUR. Sentinel précharge maintenant TROIS pages complètes en
 * cadres — panorama, enveloppe, observatoire. C'est assez pour épuiser le
 * budget de requêtes par IP et se faire bloquer par le site qu'on éprouve, et
 * « trop de requêtes » se lit alors comme une panne du module testé. On ne
 * laisse donc passer que le cadre qui nous intéresse.
 *
 *   POUR L'EXÉCUTER :  BASE=http://127.0.0.1:5401 node recette_menu_enveloppe.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5401';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
let ko = 0;
const ok = (n, c, d) => {
  console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : ''));
  if (!c) ko++;
};
const titre = t => console.log('\n══ ' + t + ' ══\n');

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1500, height: 1000 } });
  await ctx.route('**/*', r => {
    const t = r.request().resourceType(), u = r.request().url();
    if (['image', 'font', 'media'].includes(t)) return r.abort();
    if (/\/observatoire|\/panorama/.test(u)) return r.abort();
    return r.continue();
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));

  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'domcontentloaded' });
  await pg.waitForSelector('.sb-item', { timeout: 30000 });

  titre('1. L’entrée est là, au bon endroit');

  const m = await pg.evaluate(() => {
    const items = [...document.querySelectorAll('.sb-item')];
    const i = items.findIndex(x => /Enveloppe d’investissement/.test(x.textContent));
    const sect = (el) => {
      let n = el.previousElementSibling;
      while (n && !n.classList.contains('sb-section')) n = n.previousElementSibling;
      return n ? n.textContent.trim() : '';
    };
    return { i, total: items.length,
             section: i >= 0 ? sect(items[i]) : '',
             precedent: i > 0 ? items[i - 1].textContent.trim() : '',
             titre: i >= 0 ? (items[i].getAttribute('title') || '') : '',
             onclick: i >= 0 ? (items[i].getAttribute('onclick') || '') : '' };
  });
  ok('le module figure au menu', m.i >= 0, 'rang ' + m.i + ' sur ' + m.total);
  ok('…dans « Évaluer le risque »', /Évaluer le risque/.test(m.section), m.section);
  ok('…juste après le panorama, dont il est la suite',
     /Panorama/.test(m.precedent), m.precedent);
  ok('…avec une infobulle qui dit ce qu’on y trouve', m.titre.length > 60,
     m.titre.slice(0, 68) + '…');
  ok('…et il annonce sa section et son titre au fil d’Ariane',
     /ÉVALUER LE RISQUE/.test(m.onclick) && /GO \/ NO GO/.test(m.onclick),
     m.onclick.slice(0, 80));

  titre('2. Il ouvre bien l’étude, et elle seule');

  await pg.click('.sb-item:has-text("Enveloppe d’investissement")');
  await pg.waitForFunction(() => {
    const f = document.getElementById('enveloppe-iframe');
    return f && f.getAttribute('src');
  }, null, { timeout: 30000 });
  const v = await pg.evaluate(() => {
    const p = document.getElementById('p-enveloppe');
    const f = document.getElementById('enveloppe-iframe');
    const autres = [...document.querySelectorAll('.page')]
      .filter(x => x.id !== 'p-enveloppe' && getComputedStyle(x).display !== 'none');
    return { ouverte: !!p && getComputedStyle(p).display !== 'none',
             src: f ? f.getAttribute('src') : null,
             seule: autres.length === 0,
             autres: autres.map(x => x.id).slice(0, 3) };
  });
  ok('la page du module s’affiche', v.ouverte);
  ok('…et elle est seule à l’écran', v.seule, v.autres.join(', ') || 'seule');
  ok('LE CADRE POINTE SUR /enveloppe, pas sur le panorama entier',
     v.src === '/enveloppe?embed=1', v.src);

  titre('3. Chaque cadre garde SA hauteur');

  /* Les deux cadres servent le même document et annoncent donc tous deux
     « pan-height ». Router ce message sur le TYPE ferait redimensionner le
     panorama avec la hauteur de l'enveloppe. On vérifie que les écouteurs
     reconnaissent l'émetteur par sa fenêtre. */
  const routage = await pg.evaluate(() => {
    const src = [...document.querySelectorAll('script')]
      .map(s => s.textContent).join('\n');
    return { parFenetre: (src.match(/contentWindow === (ev\.)?source/g) || []).length,
             enDur: /var f = document\.getElementById\('pan-sia-iframe'\);\s*\n\s*if\(!f\) return;\s*\n\s*var h/.test(src) };
  });
  ok('les écouteurs de hauteur identifient l’émetteur par sa fenêtre',
     routage.parFenetre >= 2, routage.parFenetre + ' écouteur(s)');
  ok('…et aucun ne vise plus un cadre en dur', !routage.enDur);

  ok('aucune erreur de script', err.length === 0, err.slice(0, 2).join(' | '));

  await nav.close();
  console.log('\n' + (ko ? ko + ' contrôle(s) en échec' : 'tout est vert') + '\n');
  process.exit(ko ? 1 : 0);
})();
