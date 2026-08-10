/* Une consigne ne doit jamais désigner un objet que la page n'affiche pas.
 *
 * D'OÙ VIENT CE CONTRÔLE. Sur l'autre site du cabinet, une page invitait à
 * « choisir une phase dans la frise ci-dessus » alors que la frise n'était
 * dessinée qu'après la saisie d'un champ — et ne l'était donc jamais à
 * l'ouverture. Le défaut n'était pas dans la frise mais dans la CONSIGNE, qui
 * s'affichait sans consulter l'état de ce qu'elle désignait.
 *
 * On a cherché la même famille de défaut ici. Le panorama s'en tire bien : les
 * quatre blocs filtrables annoncent tous leur vide en toutes lettres. Restait
 * un point : les deux phrases d'introduction qui PROMETTENT UN GESTE —
 * « cliquez un pays pour ouvrir le détail de son parc », « cliquez sur un pays
 * pour ouvrir le détail » — restaient affichées au-dessus d'un bloc que le
 * filtre venait de vider. Deux textes qui se contredisent à deux lignes
 * d'écart font douter du reste de la page.
 *
 * CE QUE CE FICHIER PROTÈGE :
 *   1. tout bloc vidé par un filtre le DIT ;
 *   2. la phrase qui promet un clic se retire avec le contenu qu'elle décrit ;
 *   3. et elle revient dès que le filtre est levé — un guide qui disparaît
 *      définitivement au premier filtre serait un autre défaut.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = 'http://127.0.0.1:5401';
let ko = 0;
const ok = (n, c, d) => { console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : '')); if (!c) ko++; };

/* Les couples RÉELS, lus dans le code : tfCompte(idBarre, cléFiltre, …). Les
   deux blocs du comparateur partagent la clé « imp » tout en ayant chacun leur
   zone de vide — les apparier de travers ferait conclure à un défaut qui
   n'existe pas, ce qui est arrivé au premier essai. */
/* Attention aux sélecteurs : le bloc « empreinte » s'appelle `emp-table` mais
   n'est PAS un tableau — c'est une grille de tuiles `.pgr-t`. Deux essais s'y
   sont cassés avant de le mesurer dans le navigateur plutôt que de le déduire
   du nom. */
const BLOCS = [
  { nom: 'classement du comparateur', cle: 'imp', rendu: 'renderImplClassement',
    zone: '#tf-imp-vide', liste: '#imp-classement .cres-pays', guide: null },
  { nom: 'fiches avantages / inconvénients', cle: 'imp', rendu: 'renderImplAvis',
    zone: '#tf-avis-vide', liste: '#imp-avis .imp-fiche', guide: '#imp-guide-avis' },
  { nom: 'empreinte par pays', cle: 'emp', rendu: 'renderEmpreinte',
    zone: '#tf-emp-vide', liste: '#emp-table .pgr-t[data-pays]', guide: '#emp-guide-tab' },
];

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1440, height: 1000 } });
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
  await pg.waitForFunction(() => typeof IMPL !== 'undefined' && IMPL && IMPL.pays,
                           null, { timeout: 40000 });
  await pg.waitForTimeout(2500);

  console.log('\n══ 1. En état nominal, chaque consigne a des cibles ══\n');

  /* Détecteur générique : toute consigne VISIBLE qui nomme un geste, et le
     nombre de cibles cliquables du panneau qui la porte. */
  const consignes = await pg.evaluate(() => {
    const MOT = /\b(Cliquez|Choisissez|Sélectionnez)\b/;
    const CIBLES = 'button,[data-phase],[data-code],[data-pays],[data-podium],'
      + 'a[href],select,input,[role="button"]';
    const vu = new Set(), out = [];
    document.querySelectorAll('p,span,li').forEach(e => {
      const t = (e.textContent || '').replace(/\s+/g, ' ').trim();
      if (!MOT.test(t) || t.length > 220 || e.querySelector('p,span,li')) return;
      const r = e.getBoundingClientRect();
      if (!r.width || !r.height) return;
      const p = e.closest('section,.panel') || document.body;
      const k = t.slice(0, 60);
      if (vu.has(k)) return; vu.add(k);
      out.push({ t: t.slice(0, 64), n: p.querySelectorAll(CIBLES).length,
                 p: p.id || '(corps)' });
    });
    return out;
  });
  ok('des consignes de geste sont affichées', consignes.length >= 3, consignes.length);
  consignes.forEach(c => ok('« ' + c.t + ' » a des cibles dans ' + c.p, c.n > 0, c.n + ' cibles'));

  console.log('\n══ 2. Un bloc vidé par un filtre le dit, et la consigne se retire ══\n');

  const vider = (b) => pg.evaluate((b) => {
    TF[b.cle] = { pays: 'ZZ-INEXISTANT', q: 'zzzzzzzz', pays_nom: 'ZZ-INEXISTANT' };
    window[b.rendu]();
    const vu = (e) => !!e && !e.hidden && getComputedStyle(e).display !== 'none'
      && e.getBoundingClientRect().height > 0;
    return { restant: document.querySelectorAll(b.liste).length,
             vide: vu(document.querySelector(b.zone)),
             guide: b.guide ? vu(document.querySelector(b.guide)) : null };
  }, b);
  const lever = (b) => pg.evaluate((b) => {
    TF[b.cle] = {};
    window[b.rendu]();
    const vu = (e) => !!e && !e.hidden && getComputedStyle(e).display !== 'none'
      && e.getBoundingClientRect().height > 0;
    return { restant: document.querySelectorAll(b.liste).length,
             vide: vu(document.querySelector(b.zone)),
             guide: b.guide ? vu(document.querySelector(b.guide)) : null };
  }, b);

  for (const b of BLOCS) {
    const v = await vider(b);
    if (v.restant > 0) {
      // Ce bloc ne se vide pas avec cette clé : on le dit plutôt que de le taire.
      ok(b.nom + ' : ce filtre ne le vide pas, rien à vérifier ici', true,
         v.restant + ' éléments restants');
    } else {
      ok(b.nom + ' : le vide est ANNONCÉ', v.vide);
      if (b.guide) {
        // LE contrôle de ce fichier.
        ok('…et la phrase qui promet un clic se retire', v.guide === false);
      }
    }
    const l = await lever(b);
    ok(b.nom + ' : le contenu revient quand on lève le filtre', l.restant > 0, l.restant);
    if (b.guide) ok('…et la phrase qui le décrit revient avec lui', l.guide === true);
  }

  console.log('\n══ 3. Discrimination : ce garde-fou n’existait pas ══\n');

  const src = require('fs').readFileSync('/home/user/conseilprev/panorama.html', 'utf8');
  const { execSync } = require('child_process');
  const avant = execSync('git -C /home/user/conseilprev show HEAD:panorama.html',
                         { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
  ok('les deux phrases existaient déjà',
     /id="imp-guide-avis"/.test(avant) && /id="emp-guide-tab"/.test(avant));
  ok('…mais rien ne les retirait quand leur bloc se vidait',
     !/imp-guide-avis"\)[\s\S]{0,80}hidden/.test(avant)
     && !/emp-guide-tab"\)[\s\S]{0,80}hidden/.test(avant));
  ok('…alors qu’aujourd’hui elles suivent le contenu qu’elles décrivent',
     /gA\.hidden = !lignes\.length/.test(src) && /gE\.hidden = !paysVus\.length/.test(src));
  ok('les messages de vide, eux, existaient déjà — ce site n’avait pas le défaut',
     /tf-imp-vide/.test(avant) && /tf-emp-vide/.test(avant) && /tf-avis-vide/.test(avant));

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0, err.slice(0, 2).join(' | '));

  await nav.close();
  console.log(ko ? '\n' + ko + ' contrôle(s) en échec\n' : '\ntout est vert\n');
  process.exit(ko ? 1 : 0);
})();
