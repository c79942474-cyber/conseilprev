/* LE RENVOI DE conseilprevcyber VERS LE BLOC D'HONORAIRES DE SENTINEL.
 *
 * CE QU'UN LIEN ÉCRIT À LA MAIN NE GARANTIT PAS, ET QUE CECI ÉPROUVE : que
 * l'ancre visée EXISTE de l'autre côté. Un lien profond dont l'ancre a été
 * renommée continue de FONCTIONNER — il ouvre la page, en haut, et le lecteur
 * ne trouve pas ce qu'on lui a promis. C'est la panne silencieuse des liens
 * inter-sites, la même que celle des paramètres de formulaire : elle ne se
 * voit qu'en suivant le lien pour de bon.
 *
 * ON SUIT DONC LE LIEN, sur l'instance locale de l'autre site, et on vérifie
 * qu'on atterrit sur le bloc annoncé — pas sur une page où il faudrait le
 * chercher.
 *
 *   POUR L'EXÉCUTER :
 *     BASE=http://127.0.0.1:5401 CYBER=http://127.0.0.1:5404 node recette_lien_moe.js
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
  const ctx = await nav.newContext({ viewport: { width: 1400, height: 1000 } });
  await ctx.route('**/*', r => (['image', 'font', 'media'].includes(r.request().resourceType())
    ? r.abort() : r.continue()));
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));

  titre('1. Le renvoi est là, dans la section 6, et il se lit');

  await pg.goto(CYBER + '/connexion', { waitUntil: 'domcontentloaded' });
  await pg.evaluate(async (c) => {
    await fetch('/api/auth/login', { method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: c.m, password: c.p }) });
  }, { m: MAIL, p: MDP });
  await pg.goto(CYBER + '/ingenierie-datacenter', { waitUntil: 'domcontentloaded' });
  await pg.waitForSelector('#ig-moe .moe-vers', { timeout: 30000 });

  const bloc = await pg.evaluate(() => {
    const z = document.querySelector('#ig-moe .moe-vers');
    const a = z.querySelector('.moe-vers-a');
    /* Le renvoi doit précéder le champ qu'il explique : placé après, il
       répond à une question que le lecteur s'est déjà posée en vain. */
    const form = document.getElementById('ig-moe-form');
    const avant = !!(form && (z.compareDocumentPosition(form)
      & Node.DOCUMENT_POSITION_FOLLOWING));
    return { texte: (z.innerText || '').replace(/\s+/g, ' '),
             href: a ? a.getAttribute('href') : '',
             cible: a ? a.getAttribute('target') : '',
             rel: a ? a.getAttribute('rel') : '',
             avant_le_champ: avant };
  });
  ok('le renvoi figure dans la section 6', !!bloc.href);
  ok('…AVANT le champ qu’il explique', bloc.avant_le_champ);
  ok('…il nomme le bloc visé', /Honoraires de maîtrise d’œuvre/.test(bloc.texte),
     bloc.texte.slice(0, 60) + '…');
  ok('…il dit que c’est LE MÊME BARÈME des deux côtés',
     /même barème/.test(bloc.texte));
  ok('…et il prévient que l’accès y est réservé',
     /accès abonné/.test(bloc.texte));
  ok('le lien s’ouvre dans un onglet, sans céder la page en cours',
     bloc.cible === '_blank' && /noopener/.test(bloc.rel || ''));

  titre('2. LE POINT QUI DÉCIDE : l’ancre existe VRAIMENT de l’autre côté');

  ok('le lien vise le bloc, pas la page',
     /#moe-bloc$/.test(bloc.href), bloc.href);

  /* On suit le lien pour de bon, sur l'instance locale de Sentinel. Un lien
     profond dont l'ancre a disparu ouvre la page sans erreur : seule l'arrivée
     le dit. */
  const local = bloc.href.replace('https://conseilprev.onrender.com', BASE);
  const pg2 = await ctx.newPage();
  pg2.on('pageerror', e => err.push('[sentinel] ' + String(e)));
  await pg2.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg2.goto(local, { waitUntil: 'domcontentloaded' });
  /* NE PAS LEVER. Si l'ancre a été renommée de l'autre côté — le défaut même
     que ce contrôle traque — `waitForSelector` expire et tue la recette : on
     lit alors « Timeout » et l'on croit à une panne d'outil, là où le contrôle
     vient précisément de trouver ce qu'il cherchait. Il doit le DIRE. */
  const ancre = await pg2.waitForSelector('#moe-bloc', { timeout: 20000 })
    .then(() => true).catch(() => false);
  if (!ancre) {
    ok('L’ANCRE VISÉE EXISTE DE L’AUTRE CÔTÉ', false,
       'le lien pointe sur ' + bloc.href + ' — cette ancre est introuvable sur '
       + 'la page d’arrivée : le lien s’ouvrira SANS ERREUR, en haut de page, '
       + 'et le lecteur ne trouvera pas le bloc promis');
    await nav.close();
    console.log('\n' + ko + ' contrôle(s) en échec\n');
    process.exit(1);
  }
  const arrivee = await pg2.evaluate(() => {
    const b = document.getElementById('moe-bloc');
    const t = b ? b.querySelector('.kpi-t') : null;
    return { existe: !!b, visible: !!b && b.offsetParent !== null,
             titre: t ? t.textContent.trim() : '',
             section: b ? (b.closest('section.panel') || {}).id : '' };
  });
  ok('ON ARRIVE SUR LE BLOC ANNONCÉ, pas en haut d’une page à parcourir',
     arrivee.existe && arrivee.visible);
  ok('…et son titre est bien celui que le renvoi promet',
     arrivee.titre === 'Honoraires de maîtrise d’œuvre — par mission et par phase',
     arrivee.titre);
  ok('…dans la section d’enveloppe', arrivee.section === 's-finance',
     arrivee.section);

  titre('3. Le chemin fait la boucle : là-bas on chiffre, ici on reçoit');

  await pg2.waitForFunction(
    () => document.querySelectorAll('#fin-pays button[data-p]').length > 0,
    null, { timeout: 30000 });
  await pg2.click('#fin-go');
  await pg2.waitForSelector('#fin-res .fin-dos', { state: 'attached', timeout: 60000 });
  await pg2.click('#moe-go');
  await pg2.waitForSelector('#moe-out .moe-tab', { timeout: 45000 });
  const retour = await pg2.evaluate(() => !!document.getElementById('moe-pont-go'));
  ok('le bloc atteint propose le report vers cette page-ci', retour);

  ok('aucune erreur de script sur les deux sites', err.length === 0,
     err.slice(0, 2).join(' | '));

  await nav.close();
  console.log('\n' + (ko ? ko + ' contrôle(s) en échec' : 'tout est vert') + '\n');
  process.exit(ko ? 1 : 0);
})();
