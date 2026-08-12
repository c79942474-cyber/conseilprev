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

  titre('5. Une adresse sans paramètres reste une page normale');

  await pg2.goto(CYBER + '/ingenierie-datacenter', { waitUntil: 'domcontentloaded' });
  await pg2.waitForSelector('#ig-moe-trav', { timeout: 30000 });
  await pg2.waitForTimeout(500);
  const nu = await pg2.evaluate(() => ({
    trav: (document.getElementById('ig-moe-trav') || {}).value || '',
    bandeau: !!document.querySelector('.moe-recu'),
  }));
  ok('aucun champ n’est pré-rempli sans lien', !nu.trav, nu.trav || 'vide');
  ok('…et aucun bandeau de provenance ne s’affiche pour rien', !nu.bandeau);

  ok('aucune erreur de script sur les deux sites', err.length === 0,
     err.slice(0, 2).join(' | '));

  await nav.close();
  console.log('\n' + (ko ? ko + ' contrôle(s) en échec' : 'tout est vert') + '\n');
  process.exit(ko ? 1 : 0);
})();
