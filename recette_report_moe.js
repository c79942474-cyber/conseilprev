/* LE REPORT DU CHIFFRAGE VERS L'AUTRE SITE — le parcours entier, dans le navigateur.
 *
 * CE QUE CE CONTRÔLE ÉPROUVE, ET QU'AUCUN TEST DE MODULE NE PEUT VOIR : les
 * deux extrémités du pont se parlent. Le contrat Python peut être parfait et
 * la chaîne rester cassée — un bouton qui n'écoute rien, un paramètre lu sous
 * un autre nom, un champ rempli avant d'exister.
 *
 * LE PARCOURS :
 *   Sentinel /enveloppe → calculer l'enveloppe → chiffrer la MOE → créer le
 *   lien → LIRE CE QU'IL PORTE → puis ouvrir la même adresse sur
 *   conseilprevcyber et vérifier que les deux champs sont pré-remplis, que la
 *   provenance est écrite, et que le chiffrage part sans rien retaper.
 *
 * MÉNAGER LES DEUX LIMITEURS : images et polices bloquées, un seul calcul.
 *
 *   POUR L'EXÉCUTER :
 *     BASE=http://127.0.0.1:5401 CYBER=http://127.0.0.1:5404 node recette_report_moe.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5401';
const CYBER = process.env.CYBER || 'http://127.0.0.1:5404';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
const MAIL = process.env.MAIL || 'recette@local.test';
const MDP = process.env.MDP || 'RecetteLocale!2026';
let ko = 0;
const ok = (n, c, d) => {
  console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : ''));
  if (!c) ko++;
};
const titre = t => console.log('\n══ ' + t + ' ══\n');

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1500, height: 1100 } });
  await ctx.route('**/*', r =>
    (['image', 'font', 'media'].includes(r.request().resourceType())
      ? r.abort() : r.continue()));
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));

  titre('1. Sentinel : l’enveloppe, puis le chiffrage de MOE');

  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.goto(BASE + '/enveloppe', { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(
    () => document.querySelectorAll('#fin-pays button[data-p]').length > 0,
    null, { timeout: 30000 });
  await pg.click('#fin-go');
  await pg.waitForSelector('#fin-res .fin-dos', { state: 'attached', timeout: 60000 });
  ok('l’enveloppe est calculée',
     (await pg.locator('#fin-res .fin-dos').count()) > 0);

  await pg.locator('#moe-go').scrollIntoViewIfNeeded();
  await pg.click('#moe-go');
  await pg.waitForSelector('#moe-out .moe-tab', { timeout: 45000 });
  const chiffrage = await pg.evaluate(() => ({
    total: (document.querySelector('#moe-out .moe-tot') || {}).textContent || '',
    pont: !!document.getElementById('moe-pont-go'),
    /* Le montant à comparer avec l'autre site, lu au même endroit que le
       lecteur le lit. */
    nombre: parseFloat(((document.querySelector('#moe-out .moe-tot') || {})
      .textContent || '').replace(/\s/g, '').replace(',', '.')) || 0,
  }));
  ok('la MOE est chiffrée', /M€/.test(chiffrage.total),
     chiffrage.total.replace(/\s+/g, ' ').slice(0, 58));
  ok('LE BOUTON DE REPORT N’APPARAÎT QU’ICI, sous un chiffrage abouti',
     chiffrage.pont);

  titre('2. Le lien est fabriqué, et il DIT ce qu’il porte');

  await pg.click('#moe-pont-go');
  await pg.waitForSelector('#moe-pont-out .pont-url', { timeout: 20000 });
  const lien = await pg.evaluate(() => {
    const z = document.getElementById('moe-pont-out');
    return { url: (z.querySelector('.pont-url') || {}).textContent || '',
             texte: (z.innerText || '').replace(/\s+/g, ' '),
             av: (z.querySelector('.moe-pont-av') || {}).textContent || '' };
  });
  ok('une adresse est proposée', /^https:\/\//.test(lien.url), lien.url.slice(0, 96));
  ok('…elle vise LE BLOC DE MOE de l’ingénierie de projet',
     /\/ingenierie-datacenter\?/.test(lien.url) && /#ig-moe$/.test(lien.url));
  ok('…elle porte le montant des travaux', /travaux_meur=/.test(lien.url));
  ok('…et la part du lot technique', /part_technique=/.test(lien.url));
  ok('…et le pays de l’étude', /pays=[A-Z]{2}/.test(lien.url));
  ok('LE MONTANT TRANSPORTÉ EST ANNONCÉ AVANT LE CLIC',
     /Ce que le lien porte/.test(lien.texte)
     && /Montant des travaux/.test(lien.texte));
  ok('…l’arrondi est dit', /arrondi/.test(lien.texte));
  ok('LE PIÈGE EST NOMMÉ : une adresse se colle dans un courriel',
     /MONTANT/.test(lien.av) && /courriel/.test(lien.av), lien.av.slice(0, 62) + '…');
  ok('…et ce que le lien NE porte PAS est listé aussi',
     /ne porte pas/.test(lien.texte) && /client/.test(lien.texte));

  /* Rien de nominatif dans la requête — on regarde les VALEURS, pas l'adresse
     entière : « conSEilprevcyber » contient des suites de lettres qui font de
     faux positifs. */
  const valeurs = (lien.url.split('?')[1] || '').split('#')[0].split('&')
    .filter(p => p.indexOf('=') > 0).map(p => p.split('=')[1]);
  ok('aucune valeur transmise n’est un nom',
     valeurs.every(v => /^[\d.\-]+$|^[A-Z]{2}$/.test(v)), valeurs.join(' · '));

  titre('3. LE POINT QUI DÉCIDE : l’autre site reçoit et pré-remplit');

  const cible = lien.url.replace('https://conseilprevcyber.onrender.com', CYBER);
  const pg2 = await ctx.newPage();
  pg2.on('pageerror', e => err.push('[cyber] ' + String(e)));
  await pg2.goto(CYBER + '/connexion', { waitUntil: 'domcontentloaded' });
  await pg2.evaluate(async (c) => {
    await fetch('/api/auth/login', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: c.m, password: c.p }) });
  }, { m: MAIL, p: MDP });

  await pg2.goto(cible, { waitUntil: 'domcontentloaded' });
  await pg2.waitForSelector('#ig-moe-trav', { timeout: 30000 });
  await pg2.waitForTimeout(700);

  const recu = await pg2.evaluate(() => ({
    trav: (document.getElementById('ig-moe-trav') || {}).value || '',
    pt: (document.getElementById('ig-moe-pt') || {}).value || '',
    bandeau: (document.querySelector('.moe-recu') || {}).innerText || '',
  }));
  ok('LE MONTANT DES TRAVAUX EST PRÉ-REMPLI', !!recu.trav, recu.trav);
  ok('LA PART DU LOT TECHNIQUE AUSSI — c’est elle qui pesait le plus',
     !!recu.pt, recu.pt + ' %');
  ok('…les deux valeurs sont celles du lien',
     lien.url.indexOf('travaux_meur=' + recu.trav) > 0
     && lien.url.indexOf('part_technique=' + recu.pt) > 0);
  ok('LA PROVENANCE EST ÉCRITE — sinon on croirait à un calcul de cette page',
     /conseilprev/.test(recu.bandeau) && /pas de cette page/.test(recu.bandeau),
     recu.bandeau.slice(0, 66) + '…');
  ok('…et le pays est rappelé sans laisser croire qu’il module le barème',
     /ne varie pas d’un pays/.test(recu.bandeau));
  ok('…les champs restent MODIFIABLES', await pg2.evaluate(
     () => !document.getElementById('ig-moe-trav').readOnly
        && !document.getElementById('ig-moe-trav').disabled));

  titre('4. Et le chiffrage part, sans rien retaper');

  await pg2.locator('#ig-moe-go').scrollIntoViewIfNeeded();
  await pg2.click('#ig-moe-go');
  await pg2.waitForSelector('#ig-moe-out .moe-tab', { timeout: 30000 });
  const res = await pg2.evaluate(() => ({
    tot: (document.querySelector('#ig-moe-out .moe-tot') || {}).textContent || '',
    lignes: document.querySelectorAll('#ig-moe-out .moe-tab tbody tr').length,
    nombre: parseFloat(((document.querySelector('#ig-moe-out .moe-tot') || {})
      .textContent || '').replace(/\s/g, '').replace(',', '.')) || 0,
  }));
  ok('les honoraires sont chiffrés sur le montant reçu',
     /M€/.test(res.tot) && res.lignes >= 10,
     res.tot.replace(/\s+/g, ' ').slice(0, 70) + ' · ' + res.lignes + ' missions');
  ok('…et le total cite bien le montant des travaux repris',
     res.tot.indexOf(recu.trav.split('-')[0]) > 0
     || /travaux/.test(res.tot), res.tot.replace(/\s+/g, ' ').slice(0, 64));

  /* LE CONTRÔLE QUI MANQUAIT, ET QUI EST LE VRAI SUJET DU REPORT. Tout le
     reste peut être vert pendant que les deux sites annoncent des honoraires
     DIFFÉRENTS sur le même projet et le même barème — c'est exactement ce qui
     se passait : Sentinel envoyait la part technique rapportée à l'ENVELOPPE
     là où l'autre module la lit comme une part des TRAVAUX, treize points plus
     bas. 50,9 M€ ici, 53,9 M€ là-bas, et rien pour le dire. Deux chiffres pour
     un seul barème, c'est le report qui perd tout son sens. */
  const ecart = Math.abs(res.nombre - chiffrage.nombre)
    / Math.max(chiffrage.nombre, 1);
  ok('LES DEUX SITES ANNONCENT LE MÊME PRIX — même barème, même projet',
     ecart < 0.005,
     'Sentinel ' + chiffrage.nombre + ' M€ · conseilprevcyber ' + res.nombre
     + ' M€ — écart ' + (ecart * 100).toFixed(2) + ' %');

  titre('5. LE RETOUR DIRECT : la page se souvient de l’étude');

  /* CE QUE LE LIEN SEUL NE RÉSOUT PAS. Le client mène son enveloppe sur
     Sentinel, suit le lien une fois — puis revient sur la page par le MENU,
     le lendemain. Sans mémoire, il retrouve deux champs vides et retape ; et
     retaper la part du lot technique, c'est la laisser vide, donc retomber sur
     l'hypothèse à 70 %. */
  await pg2.goto(CYBER + '/ingenierie-datacenter', { waitUntil: 'domcontentloaded' });
  await pg2.waitForSelector('#ig-moe-trav', { timeout: 30000 });
  await pg2.waitForTimeout(600);
  const memo = await pg2.evaluate(() => ({
    trav: (document.getElementById('ig-moe-trav') || {}).value || '',
    pt: (document.getElementById('ig-moe-pt') || {}).value || '',
    bandeau: (document.querySelector('.moe-recu') || {}).innerText || '',
    url: window.location.search,
  }));
  ok('l’adresse ne porte PLUS aucun paramètre', memo.url === '', memo.url || 'nue');
  ok('LES DEUX CHAMPS SONT QUAND MÊME PRÉ-REMPLIS',
     memo.trav === recu.trav && memo.pt === recu.pt,
     memo.trav + ' M€ · ' + memo.pt + ' %');
  ok('…et le bandeau dit que c’est une MÉMOIRE, pas le calcul du jour',
     /mémoris/i.test(memo.bandeau), memo.bandeau.slice(0, 62) + '…');
  ok('…il propose de l’oublier — c’est un montant sur l’appareil du client',
     await pg2.evaluate(() => !!document.querySelector('[data-moe-oubli]')));

  titre('6. Une enveloppe trop vieille n’est PAS re-injectée en silence');

  await pg2.evaluate(() => {
    const b = JSON.parse(window.localStorage.getItem('cp.moe.enveloppe.v1'));
    b.quand = Date.now() - 95 * 86400000;          /* 95 jours */
    window.localStorage.setItem('cp.moe.enveloppe.v1', JSON.stringify(b));
  });
  await pg2.reload({ waitUntil: 'domcontentloaded' });
  await pg2.waitForSelector('#ig-moe-trav', { timeout: 30000 });
  await pg2.waitForTimeout(600);
  const vieux = await pg2.evaluate(() => ({
    trav: (document.getElementById('ig-moe-trav') || {}).value || '',
    pt: (document.getElementById('ig-moe-pt') || {}).value || '',
    bandeau: (document.querySelector('.moe-recu') || {}).innerText || '',
    ambre: !!document.querySelector('.moe-recu-vieux'),
  }));
  ok('AUCUN CHAMP N’EST REMPLI par une valeur de 95 jours',
     !vieux.trav && !vieux.pt, (vieux.trav || 'vide') + ' / ' + (vieux.pt || 'vide'));
  ok('…mais l’abandon est ANNONCÉ, pas silencieux',
     /écartée/i.test(vieux.bandeau) && /95 jours/.test(vieux.bandeau),
     vieux.bandeau.slice(0, 66) + '…');
  ok('…et il se distingue à l’œil d’un report réussi', vieux.ambre);
  ok('…il dit quoi faire : relancer l’étude', /Relancez/i.test(vieux.bandeau));

  titre('7. Oublier la valeur la retire vraiment de l’appareil');

  await pg2.click('[data-moe-oubli]');
  await pg2.waitForTimeout(200);
  const apres = await pg2.evaluate(() => ({
    reste: window.localStorage.getItem('cp.moe.enveloppe.v1'),
    dit: (document.querySelector('.moe-recu') || {}).innerText || '',
  }));
  ok('plus rien n’est mémorisé', !apres.reste, apres.reste || 'rien');
  ok('…et le geste se voit', /oubliée/i.test(apres.dit), apres.dit.slice(0, 48));

  await pg2.reload({ waitUntil: 'domcontentloaded' });
  await pg2.waitForSelector('#ig-moe-trav', { timeout: 30000 });
  await pg2.waitForTimeout(500);
  const nu = await pg2.evaluate(() => ({
    trav: (document.getElementById('ig-moe-trav') || {}).value || '',
    bandeau: !!document.querySelector('.moe-recu'),
  }));
  ok('aucun champ n’est pré-rempli sans lien ni mémoire', !nu.trav,
     nu.trav || 'vide');
  ok('…et aucun bandeau de provenance ne s’affiche pour rien', !nu.bandeau);

  titre('8. Ce qui est écrit doit être LISIBLE — contraste réellement peint');

  /* UN CONTRÔLE QU'AUCUNE LECTURE DU SOURCE NE REMPLACE. `getComputedStyle`
     rend « transparent » pour un fond hérité et ignore l'opacité : il annonçait
     18,55:1 sur un bouton qui s'affichait à 6,7. On compose donc les couches
     jusqu'au premier fond opaque, et on applique l'opacité — c'est ce que
     l'œil reçoit.

     CE QU'IL A ATTRAPÉ, ET QUE LA CAPTURE D'ÉCRAN M'A FAIT VOIR : j'avais posé
     des jetons de thème CLAIR (--white, --muted2) sur une page sombre. Le
     bouton « oublier » sortait beige sur blanc — 1,76:1. Et la page portait
     déjà la même faute sur ses pastilles de phase : décochée, une phase
     passait à 1,13:1, c'est-à-dire qu'elle DISPARAISSAIT — le client ne
     voyait plus ce qu'il venait d'écarter, donc ne pouvait plus le reprendre. */
  await pg2.goto(CYBER + '/ingenierie-datacenter?travaux_meur=600-750'
                 + '&part_technique=70&pays=FR', { waitUntil: 'domcontentloaded' });
  await pg2.waitForSelector('#ig-moe-trav', { timeout: 30000 });
  await pg2.waitForTimeout(700);
  await pg2.goto(CYBER + '/ingenierie-datacenter', { waitUntil: 'domcontentloaded' });
  await pg2.waitForSelector('.moe-oubli', { timeout: 30000 });
  await pg2.click('#ig-moe-phases button');
  await pg2.waitForTimeout(250);

  const contrastes = await pg2.evaluate(() => {
    const px = c => c.match(/[\d.]+/g).map(Number);
    const melange = (av, ar, a) => av.map((v, i) => v * a + ar[i] * (1 - a));
    const fondPeint = (el) => {
      let couches = [], n = el.parentElement;
      while (n) {
        const p = px(getComputedStyle(n).backgroundColor);
        const a = p[3] === undefined ? 1 : p[3];
        if (p.length >= 3 && a > 0) { couches.unshift([p.slice(0, 3), a]);
                                      if (a === 1) break; }
        n = n.parentElement;
      }
      let fond = [255, 255, 255];
      couches.forEach(([c, a]) => { fond = melange(c, fond, a); });
      return fond;
    };
    const lum = c => { const [r, g, b] = c.map(v => { v /= 255;
      return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); });
      return .2126 * r + .7152 * g + .0722 * b; };
    const ratio = (a, b) => { const l1 = lum(a), l2 = lum(b);
      return +(((Math.max(l1, l2) + .05) / (Math.min(l1, l2) + .05)).toFixed(2)); };
    const m = (sel) => {
      const el = document.querySelector(sel);
      if (!el) return null;
      const cs = getComputedStyle(el), fond = fondPeint(el);
      return ratio(melange(px(cs.color).slice(0, 3), fond,
                           parseFloat(cs.opacity) || 1), fond);
    };
    return { bouton: m('.moe-oubli'),
             decochee: m('#ig-moe-phases button:not(.on)'),
             bandeau: m('.moe-recu') };
  });
  ok('le bouton « oublier » est lisible', contrastes.bouton >= 4.5,
     contrastes.bouton + ':1');
  ok('UNE PHASE DÉCOCHÉE RESTE VISIBLE — sinon on ne peut plus la reprendre',
     contrastes.decochee >= 4.5, contrastes.decochee + ':1');
  ok('…et le bandeau de provenance aussi', contrastes.bandeau >= 4.5,
     contrastes.bandeau + ':1');

  ok('aucune erreur de script sur les deux sites', err.length === 0,
     err.slice(0, 2).join(' | '));

  await nav.close();
  console.log('\n' + (ko ? ko + ' contrôle(s) en échec' : 'tout est vert') + '\n');
  process.exit(ko ? 1 : 0);
})();
