/* RECETTE — SUR LES HUIT RISQUES, SEUL L'APPEL REDIRIGE
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE : « pour les 8 risques systémiques, seul le cliquage sur Ouvrir
 * le module de chaque bloc doit rediriger vers la bonne page Sentinel ».
 *
 * CE QUE LA MESURE A TROUVÉ, ET QUI N'ÉTAIT PAS DANS LE CSS. Un bloc de
 * `index.page.js` rendait cliquables `.sector-card, .norm-card, .risk-card`
 * et ouvrait « /sentinel » — l'ACCUEIL — dans un nouvel onglet. Sur les huit
 * cartes de risque, qui portent toutes leur propre appel vers LEUR module,
 * il faisait deux dégâts : cliquer le corps ouvrait le sommaire au lieu du
 * module annoncé, et cliquer « Ouvrir le module » déclenchait LES DEUX —
 * le lien dans l'onglet courant, l'accueil dans un second par-dessus.
 *
 * POURQUOI AUCUNE SONDE NE L'AVAIT VU. `window.open` n'est pas une
 * navigation de lien. Une recette qui n'écoute que les clics sur <a> a
 * déclaré ces cartes « inertes » alors qu'elles ouvraient un onglet à chaque
 * clic. Une sonde qui ne connaît qu'une sortie certifie l'absence de toutes
 * les autres — celle-ci intercepte les deux, et compte les sorties.
 *
 * CE QU'ELLE VÉRIFIE AUSSI, ET QUI EST L'AUTRE MOITIÉ DE LA DEMANDE : les
 * six cartes de SERVICE gardent leur surface étirée. Le bloc entier y reste
 * un appel, parce qu'une offre est un appel — un constat de risque, non.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5901';
let ko = 0, n = 0;
const ok = (t, c, d) => { n++; if (!c) ko++;
  console.log((c ? '  OK   ' : '  KO   ') + t + (d ? ' — ' + d : '')); };
(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1400, height: 1100 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator,'webdriver',{get:()=>false});
    Object.defineProperty(navigator,'plugins',{get:()=>[1,2,3]});
    Object.defineProperty(navigator,'languages',{get:()=>['fr-FR','fr']});
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e).slice(0,160)));
  await pg.goto(BASE + '/', { waitUntil:'domcontentloaded' });
  await pg.waitForTimeout(2200);
  /* ON INTERCEPTE LES DEUX FAÇONS DE PARTIR, ET C'EST LE POINT.
     Une première version n'écoutait que les clics sur <a>. Elle a déclaré
     « 32 points inertes » sur des cartes qui ouvraient en réalité l'accueil
     de Sentinel dans un nouvel onglet, par `window.open` — invisible pour
     elle. Une sonde qui ne connaît qu'une sortie certifie l'absence de
     toutes les autres. */
  await pg.evaluate(() => {
    window.__A = [];
    window.__OUVRE = [];
    const vrai = window.open;
    window.open = function (u) { window.__OUVRE.push(String(u)); return null; };
    window.__openVrai = vrai;
    document.addEventListener('click', function (e) {
      const a = e.target.closest('a');
      if (a && a.getAttribute('href')) { e.preventDefault();
        window.__A.push(a.getAttribute('href')); }
    }, true);
    window.__viser = (el) => {
      window.__A = []; window.__OUVRE = [];
      if (!el) return 'ABSENT';
      el.scrollIntoView({ block:'center', behavior:'instant' });
      const r = el.getBoundingClientRect();
      const c = document.elementFromPoint(r.left + r.width/2, r.top + r.height/2);
      if (!c) return 'HORS ÉCRAN';
      c.click();
      const sorties = window.__A.concat(
        window.__OUVRE.map(u => 'NOUVEL ONGLET ' + u));
      return sorties.length === 0 ? 'RIEN'
           : sorties.length === 1 ? sorties[0]
           : 'DEUX SORTIES : ' + sorties.join(' + ');
    };
  });

  /* ── LES HUIT RISQUES : LE CORPS NE DOIT PLUS NAVIGUER ────────────── */
  const r = await pg.evaluate(() =>
    [...document.querySelectorAll('#risques .risk-card')].map(c => ({
      t: c.querySelector('.risk-title').textContent.trim(),
      attendu: c.querySelector('.risk-go').getAttribute('href'),
      titre: window.__viser(c.querySelector('.risk-title')),
      desc:  window.__viser(c.querySelector('.risk-desc')),
      ico:   window.__viser(c.querySelector('.risk-ico')),
      tag:   window.__viser(c.querySelector('.risk-tag')),
      appel: window.__viser(c.querySelector('.risk-go')),
      curseur: getComputedStyle(c).cursor })));
  ok('les huit cartes de risque sont là', r.length === 8, r.length + '');
  const fuites = r.filter(c => [c.titre, c.desc, c.ico, c.tag].some(v => v !== 'RIEN'));
  ok('le CORPS des huit cartes ne redirige plus (titre, description, icône, étiquette)',
     fuites.length === 0,
     fuites.map(c => c.t + ' : ' + [c.titre,c.desc,c.ico,c.tag].join('/')).join(' | ')
       || '32 points inertes');
  const manques = r.filter(c => c.appel !== c.attendu);
  ok('« Ouvrir le module » redirige, sur les huit',
     manques.length === 0,
     manques.map(c => c.t + ' : ' + c.appel + ' ≠ ' + c.attendu).join(' | ')
       || r.map(c => c.attendu.replace('/sentinel?goto=','')).join(' · '));
  ok('la carte de risque n’annonce plus un clic qu’elle ne rend pas',
     r.every(c => c.curseur !== 'pointer'), 'cursor:' + (r[0]||{}).curseur);
  const doubles = r.filter(c => /DEUX SORTIES/.test(c.appel));
  ok('« Ouvrir le module » ne déclenche QU’UNE seule sortie',
     doubles.length === 0,
     doubles.map(c => c.t + ' : ' + c.appel).join(' | ') || '8 appels, 8 sorties');
  const annonce = await pg.evaluate(() =>
    [...document.querySelectorAll('#risques .risk-card')]
      .filter(c => c.getAttribute('role') || c.getAttribute('tabindex')).length);
  ok('la carte n’est plus annoncée comme un lien par un lecteur d’écran',
     annonce === 0, annonce + ' carte(s) portent role/tabindex');

  /* ── LES SIX OFFRES : MÊME RÈGLE ──────────────────────────────────── */
  const s = await pg.evaluate(() =>
    [...document.querySelectorAll('#services .diff-card')].map(c => ({
      t: c.querySelector('.diff-title').textContent.trim(),
      attendu: c.querySelector('.sv-card-go').getAttribute('href'),
      titre: window.__viser(c.querySelector('.diff-title')),
      desc:  window.__viser(c.querySelector('.diff-desc')),
      ico:   window.__viser(c.querySelector('.diff-ico')),
      appel: window.__viser(c.querySelector('.sv-card-go')),
      curseur: getComputedStyle(c).cursor })));
  const fuitesS = s.filter(c => [c.titre, c.desc, c.ico].some(v => v !== 'RIEN'));
  ok('le CORPS des six offres ne redirige plus (titre, description, icône)',
     s.length === 6 && fuitesS.length === 0,
     fuitesS.map(c => c.t + ' : ' + [c.titre,c.desc,c.ico].join('/')).join(' | ')
       || '18 points inertes');
  const manquesS = s.filter(c => c.appel !== c.attendu);
  ok('« Ouvrir le module » redirige, sur les six',
     manquesS.length === 0,
     manquesS.map(c => c.t + ' : ' + c.appel + ' ≠ ' + c.attendu).join(' | ')
       || s.map(c => c.attendu.replace('/sentinel?goto=','')).join(' · '));
  ok('et elles n’annoncent plus un clic qu’elles ne rendent pas',
     s.every(c => c.curseur !== 'pointer'), 'cursor:' + (s[0]||{}).curseur);

  /* LES DEUX DESTINATIONS NOMMÉES PAR LA DEMANDE D'AVANT, reprises de la
     recette du bloc cliquable devenue sans objet. La carte se désigne par sa
     CLÉ de traduction : la page peut s'afficher en anglais, et « Formation »
     devient « Training ». */
  const cles = await pg.evaluate(() =>
    [...document.querySelectorAll('#services .diff-card')].map(c => ({
      cle: c.querySelector('.diff-title').getAttribute('data-i18n'),
      t: c.querySelector('.diff-title').textContent.trim(),
      h: c.querySelector('.sv-card-go').getAttribute('href') })));
  for (const [cle, cible, quoi] of [
        ['sv.form.t', '/sentinel?goto=training', 'le hub de formation'],
        ['sv.grc.t', '/sentinel?goto=gouvernance',
         'la gouvernance opérationnelle de l’IA']]) {
    const c = cles.find(x => x.cle === cle);
    ok('« ' + cle + ' » mène à ' + quoi, c && c.h === cible,
       c ? c.t + ' → ' + c.h : 'carte introuvable');
  }
  const fl = await pg.evaluate(() =>
    [...document.querySelectorAll('#services .sv-go')].map(a => ({
      sien: a.getAttribute('href'), atteint: window.__viser(a) })));
  /* LES FLÈCHES N'ONT PLUS RIEN AU-DESSUS D'ELLES : plus de surface, plus
     de z-index à leur défendre. Elles doivent ouvrir leur module sans aide. */
  ok('les 13 flèches de puce ouvrent LEUR module, sans z-index pour les défendre',
     fl.length === 13 && fl.every(x => x.sien === x.atteint),
     fl.filter(x => x.sien !== x.atteint).map(x => x.sien + ' → ' + x.atteint).join(', ')
       || fl.length + ' flèches');
  ok('aucune erreur JavaScript', err.length === 0, err.join(' | '));
  await nav.close();
  console.log('\n' + (n - ko) + ' contrôles passés, ' + ko + ' en échec');
  process.exit(ko ? 1 : 0);
})().catch(e => { console.error('KO rompu : ' + e); process.exit(2); });
