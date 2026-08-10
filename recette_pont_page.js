/* LE PONT VERS L'ÉTUDE DE DURABILITÉ, SUR LA PAGE — et le seul piège qui compte.
 *
 * Le module `pont_dc.py` tient le contrat et sa recette le fige. Ce qu'il ne
 * peut pas savoir, c'est QUEL PAYS la page lui donne. C'est là qu'est le vrai
 * risque, et il est silencieux :
 *
 *   La grille et le tableau du comparateur se trient et se filtrent, et leur
 *   tri PAR DÉFAUT est alphabétique. Leur première ligne n'est donc pas le
 *   premier du classement — c'est l'Allemagne. Un lien bâti sur « la première
 *   ligne » partirait avec l'Allemagne en se réclamant du comparateur pondéré :
 *   une valeur fausse sous une étiquette juste, qui ne se verrait qu'au bilan
 *   carbone, des semaines plus tard, sur l'autre site.
 *
 *   Le PODIUM, lui, est bâti sur le classement COMPLET trié par score. Il ne
 *   bouge ni au tri ni au filtre. C'est lui que le pont doit lire.
 *
 * CETTE RECETTE VÉRIFIE DONC QUE LES DEUX DIFFÈRENT, PUIS QUE C'EST LE PODIUM
 * QUI GAGNE. Si un jour ils cessaient de différer, le contrôle ne prouverait
 * plus rien — il le dit alors au lieu de passer au vert.
 *
 * Elle vérifie ensuite la bascule : une fois l'enveloppe d'investissement
 * calculée, c'est SON classement — par coût total de possession — qui fournit
 * le pays, et la page doit dire laquelle des deux origines a joué. Les deux ne
 * donnent pas toujours le même pays.
 *
 *   POUR L'EXÉCUTER :
 *     AUTH_MASTER_TOKEN=recette_locale_idf_0123456789abcdef python3 app.py &
 *     PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node recette_pont_page.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5401';
const JETON = process.env.JETON || 'recette_locale_idf_0123456789abcdef';
let ko = 0;
const ok = (n, c, d) => {
  console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : ''));
  if (!c) ko++;
};

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1440, height: 1150 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));

  await pg.goto(BASE + '/auth/' + JETON, { waitUntil: 'domcontentloaded' });
  await pg.goto(BASE + '/panorama', { waitUntil: 'networkidle' });
  await pg.waitForFunction(
    () => document.querySelector('#imp-classement .cres-pod [data-podium]'),
    null, { timeout: 40000 });

  console.log('\n══ 1. Les deux blocs sont là, sous les deux calculs ══\n');

  const blocs = await pg.evaluate(() => {
    const où = id => {
      const b = document.getElementById(id);
      if (!b) return null;
      /* De quelle section relève le bloc : c'est la promesse faite au client
         — « en fonction du résultat » de CE calcul-là. */
      const s = b.closest('section');
      return { existe: true, section: s ? s.id : null,
               bouton: !!b.querySelector('[data-pont-go]'),
               voies: b.querySelectorAll('[data-pont-voie] option').length };
    };
    return { imp: où('pont-imp'), fin: où('pont-fin') };
  });
  ok('un bloc sous le comparateur pondéré', !!(blocs.imp && blocs.imp.existe));
  ok('un bloc sous l’enveloppe d’investissement', !!(blocs.fin && blocs.fin.existe));
  ok('les deux portent un bouton', !!(blocs.imp && blocs.imp.bouton && blocs.fin.bouton));
  ok('les voies viennent du serveur, pas du balisage',
     !!(blocs.imp && blocs.imp.voies >= 2), blocs.imp && blocs.imp.voies);

  console.log('\n══ 2. Le podium, PAS la première ligne affichée ══\n');

  const av = await pg.evaluate(() => ({
    podium: (document.querySelector('#imp-classement .cres-pod [data-podium]') || {})
              .getAttribute ? document.querySelector('#imp-classement .cres-pod [data-podium]')
              .getAttribute('data-podium') : null,
    premiereLigne: (() => {
      const t = document.querySelector('#imp-classement .imp-l[data-pays]');
      return t ? t.getAttribute('data-pays') : null;
    })(),
    tri: (document.querySelector('#tf-imp [data-tf="tri"]') || {}).value,
  }));
  ok('le tri par défaut du comparateur est alphabétique',
     !av.tri, JSON.stringify(av.tri));
  /* SANS CET ÉCART, LE CONTRÔLE SUIVANT NE PROUVE RIEN. On le dit plutôt que
     de laisser un vert qui ne discrimine plus. */
  ok('le podium et la première ligne affichée DIFFÈRENT — sinon rien à prouver',
     av.podium && av.premiereLigne && av.podium !== av.premiereLigne,
     'podium ' + av.podium + ' · première ligne ' + av.premiereLigne);

  await pg.click('#pont-imp [data-pont-go]');
  await pg.waitForSelector('#pont-imp .pont-url', { timeout: 20000 });
  const r1 = await pg.evaluate(() => {
    const z = document.getElementById('pont-imp');
    return { url: z.querySelector('.pont-url').textContent,
             porte: (z.querySelector('.pont-porte') || {}).textContent || '',
             refus: (z.querySelector('.pont-refus') || {}).textContent || '' };
  });
  ok('le lien porte le pays du PODIUM', r1.url.indexOf('pays=' + av.podium) > 0,
     r1.url);
  ok('…et surtout PAS celui de la première ligne affichée',
     r1.url.indexOf('pays=' + av.premiereLigne) < 0, r1.url);
  ok('la page dit que ce pays vient du comparateur pondéré',
     /comparateur pondéré/.test(r1.porte), r1.porte.slice(0, 160));
  ok('le lien vise bien l’étude de durabilité de l’autre site',
     /^https:\/\/conseilprevcyber\.onrender\.com\/datacenter#voie=/.test(r1.url),
     r1.url);

  console.log('\n══ 3. Ce que le lien ne porte pas est écrit, avant de partir ══\n');
  const dit = await pg.evaluate(() => {
    const z = document.getElementById('pont-imp');
    const e = z.querySelector('.pont-exclus');
    return { exclus: e ? e.textContent : '',
             lignes: e ? e.querySelectorAll('li').length : 0,
             ouvre: !!z.querySelector('.pont-l a[target="_blank"]'),
             copie: !!z.querySelector('[data-pont-copier]') };
  });
  ok('la liste de ce qui ne voyage pas est affichée', dit.lignes >= 4, dit.lignes);
  ok('…et elle nomme le nominatif', /client|société|projet/i.test(dit.exclus));
  ok('le lien est offert, jamais suivi — il faut cliquer', dit.ouvre);
  ok('…et il peut se copier', dit.copie);
  ok('aucun montant dans le lien construit',
     !/(meur|euro|cout|tco|enveloppe)=/i.test(r1.url), r1.url);

  console.log('\n══ 4. L’enveloppe calculée reprend la main, et la page le dit ══\n');

  await pg.fill('#fin-mw', '45');
  await pg.click('#fin-go');
  await pg.waitForFunction(() => window.PONT_DC && window.PONT_DC.pays,
                           null, { timeout: 60000 });
  const dep = await pg.evaluate(() => ({ pays: window.PONT_DC.pays,
                                         mw: window.PONT_DC.mw,
                                         de: window.PONT_DC.de }));
  ok('l’enveloppe publie son pays de tête et sa puissance',
     !!dep.pays && dep.mw === 45, JSON.stringify(dep));

  await pg.click('#pont-fin [data-pont-go]');
  await pg.waitForSelector('#pont-fin .pont-url', { timeout: 20000 });
  const r2 = await pg.evaluate(() => {
    const z = document.getElementById('pont-fin');
    return { url: z.querySelector('.pont-url').textContent,
             porte: (z.querySelector('.pont-porte') || {}).textContent || '' };
  });
  ok('le lien prend le pays publié par l’enveloppe',
     r2.url.indexOf('pays=' + dep.pays) > 0, r2.url);
  /* LES DEUX CLASSEMENTS PEUVENT DÉSIGNER LE MÊME PAYS. C'est le cas ici, et
     ce n'est pas un défaut — mais alors le contrôle ci-dessus ne prouve PLUS
     que c'est bien l'enveloppe qui a fourni la valeur. Ce qui le prouve dans ce
     cas, c'est la phrase d'origine, vérifiée juste après. On le dit au lieu de
     laisser croire à une démonstration qui n'a pas eu lieu. */
  if (dep.pays === av.podium) {
    console.log('  ··   comparateur et coût total de possession désignent tous '
      + 'deux ' + dep.pays + ' : seule la phrase d’origine départage ici.');
  }
  ok('la puissance part convertie en kilowatts',
     r2.url.indexOf('puissance_it_kw=45000') > 0, r2.url);
  ok('la page nomme l’AUTRE origine — le coût total de possession',
     /coût total de possession/.test(r2.porte), r2.porte.slice(0, 200));
  ok('…et ne se réclame plus du comparateur pondéré',
     !/comparateur pondéré/.test(r2.porte), r2.porte.slice(0, 200));

  console.log('\n══ 5. Rien ne casse ══\n');
  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 3).join(' | '));

  await nav.close();
  console.log('\n' + (ko ? ko + ' contrôle(s) en échec' : 'tout est vert') + '\n');
  process.exit(ko ? 1 : 0);
})();
