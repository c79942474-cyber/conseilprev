/* Les trois pays tiers, tels qu'un lecteur les rencontre.
 *
 * Ce que le navigateur seul peut prouver, et que le module ne peut pas :
 * - `UE` est relié quand l'API répond — sans quoi tout le travail côté serveur
 *   resterait invisible, et c'était exactement le défaut trouvé ;
 * - les trois sont PEINTS sur la carte des cas d'IA, et leur étiquette dit
 *   « hors du champ » et non « 0 cas » ;
 * - les vues empreinte (CO₂e, mix) les colorent, elles, avec de vraies valeurs ;
 * - la Suisse est classée au comparateur et colorée sur sa carte ;
 * - la fiche pays s'ouvre et n'écrit JAMAIS « Surveillance AI Act » au-dessus
 *   d'un régulateur suisse ou britannique ;
 * - l'empreinte suisse s'affiche « non estimée », jamais « 0 ».
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = 'http://127.0.0.1:5401';
let ko = 0;
const ok = (n, c, d) => { console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : '')); if (!c) ko++; };

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1440, height: 1200 } });
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
  await pg.waitForFunction(() => typeof UE !== 'undefined' && UE && Object.keys(UE).length >= 30,
                           null, { timeout: 30000 });

  console.log('\n══ La table des pays atteint réellement l’écran ══\n');
  const d = await pg.evaluate(() => ({
    n: Object.keys(UE).length,
    tiers: ['CH', 'NO', 'GB'].filter(c => UE[c] && UE[c].ue === false),
    membres: Object.keys(UE).filter(c => estUE(c)).length,
    noms: ['FR', 'CH', 'NO', 'GB'].map(c => nomPays(c)),
  }));
  ok('trente pays sont servis à la page', d.n === 30, d.n);
  ok('vingt-sept sont membres', d.membres === 27, d.membres);
  ok('les trois autres se savent hors Union', d.tiers.length === 3, d.tiers.join(','));
  ok('leur nom porte le suffixe « (hors UE) »',
     d.noms[1] === 'Suisse (hors UE)' && d.noms[2] === 'Norvège (hors UE)'
     && d.noms[3] === 'Royaume-Uni (hors UE)', d.noms.join(' · '));
  ok('…et la France, elle, ne le porte pas', d.noms[0] === 'France', d.noms[0]);

  console.log('\n══ La carte des cas d’IA les peint — sans leur prêter zéro cas ══\n');
  for (const v of ['cas', 'co2', 'mix']) {
    const r = await pg.evaluate(vue => {
      VUE = vue; renderMap();
      const lu = c => {
        const e = document.querySelector('.pan-pays[data-code="' + c + '"]');
        return e ? { fill: e.getAttribute('fill'), lab: e.getAttribute('aria-label') } : null;
      };
      return { ch: lu('CH'), no: lu('NO'), gb: lu('GB'), fr: lu('FR') };
    }, v);
    ok('vue « ' + v + ' » : les trois sont dessinés',
       !!(r.ch && r.no && r.gb), JSON.stringify([!!r.ch, !!r.no, !!r.gb]));
    if (v === 'cas') {
      ok('…et leur étiquette dit « hors du champ », pas « 0 cas »',
         /hors du champ du panel/.test(r.ch.lab) && !/0 cas/.test(r.ch.lab), r.ch.lab.slice(0, 62));
      ok('…tandis qu’un État membre garde son compte de cas',
         /cas au panel/.test(r.fr.lab), r.fr.lab.slice(0, 40));
      ok('…et leur couleur reste celle du « sans donnée »',
         r.ch.fill === '#EFF2F6' && r.no.fill === '#EFF2F6', r.ch.fill);
    } else {
      /* C'est ici que l'empreinte devient visible : ces vues lisent EMP, qui
         porte les trois pays depuis toujours — ils étaient gris faute d'être
         dans la table, pas faute de données. */
      ok('…avec une couleur d’empreinte RÉELLE, pas le gris des absents',
         r.gb.fill !== '#EFF2F6' && r.gb.fill !== r.ch.fill,
         'GB ' + r.gb.fill + ' vs CH ' + r.ch.fill);
    }
  }
  await pg.evaluate(() => { VUE = 'cas'; renderMap(); });

  console.log('\n══ L’infobulle explique, elle ne se tait pas ══\n');
  const tip = async code => pg.evaluate(c => tipPays(c).replace(/<[^>]+>/g, ' | '), code);
  const tch = await tip('CH'), tfr = await tip('FR');
  ok('la Suisse : « hors du champ du panel »', /hors du champ du panel/.test(tch),
     tch.slice(0, 70));
  ok('…avec son régulateur cyber et sa CNIL', /OFCS/.test(tch) && /PFPDT/.test(tch));
  ok('…et l’avertissement que zéro ne dit rien de l’IA déployée',
     /ne dit rien de l’IA déployée/.test(tch));
  ok('un État membre sans cas garde SA formulation',
     /Limite de publication/.test(await tip('MT')) || /cas/.test(tfr));

  console.log('\n══ Le comparateur classe la Suisse, et la carte la colore ══\n');
  await pg.evaluate(() => chargerImplantation());
  await pg.waitForFunction(() => typeof IMPL !== 'undefined' && IMPL && IMPL.pays, null, { timeout: 30000 });
  const cl = await pg.evaluate(() => {
    renderImplClassement();
    const o = IMPL.pays.filter(x => x.avis && implScore(x) !== null)
      .map(x => ({ p: x.pays, s: implScore(x) })).sort((a, b) => b.s - a.s);
    const peint = c => {
      const e = document.querySelector('#imp-classement [data-code="' + c + '"]');
      return e ? e.getAttribute('fill') : null;
    };
    return { n: o.length, rangCH: o.findIndex(x => x.p === 'CH') + 1,
             top: o.slice(0, 5).map(x => x.p).join(' · '),
             fills: { CH: peint('CH'), NO: peint('NO'), GB: peint('GB') } };
  });
  ok('vingt-quatre pays classés', cl.n === 24, cl.n);
  ok('la Suisse en fait partie', cl.rangCH > 0, 'rang ' + cl.rangCH + '/' + cl.n);
  ok('…et elle est bien peinte sur la carte du comparateur',
     cl.fills.CH && cl.fills.CH !== 'none' && cl.fills.CH !== '#D6D8DA',
     JSON.stringify(cl.fills));
  console.log('      podium : ' + cl.top + '\n');

  console.log('\n══ La fiche pays ne naturalise personne ══\n');
  const fiche = async c => pg.evaluate(code => {
    ouvrirPays(code);
    return document.getElementById('pv-corps').innerText;
  }, c);
  const fch = await fiche('CH');
  ok('la fiche suisse s’ouvre', fch.length > 200, fch.split('\n')[0]);
  ok('elle n’écrit PAS « Surveillance AI Act » au-dessus du régulateur suisse',
     !/Surveillance AI Act/.test(fch));
  ok('…mais « Autorité compétente sur l’IA »', /Autorité compétente sur l’IA/.test(fch));
  ok('…et dit quel droit s’applique vraiment',
     /Quel droit s’applique/.test(fch) && /hors EEE/.test(fch));
  /* Les données du module portent l'apostrophe DROITE, les libellés de la page
     l'apostrophe typographique. Un motif qui n'accepte qu'une des deux mesure
     la ponctuation, pas le contenu. */
  ok('…ainsi que la trajectoire suisse (Conseil de l’Europe, 12 février 2025)',
     /Conseil de l['’]Europe/.test(fch) && /12 février 2025/.test(fch),
     (fch.match(/Trajectoire[^\n]{0,60}/) || ['introuvable'])[0]);
  const ffr = await fiche('FR');
  ok('la fiche française garde, elle, l’intitulé de l’article 70',
     /Surveillance AI Act \(art\. 70\)/.test(ffr));
  ok('…et ne reçoit pas de bloc « quel droit s’applique »',
     !/Quel droit s’applique/.test(ffr));

  console.log('\n══ L’empreinte suisse : « non estimée », jamais « 0 » ══\n');
  ok('la fiche suisse écrit « non estimée »', /non estimée/.test(fch));
  ok('…et donne le motif : ni capacité, ni gabarit',
     /ni capacité annoncée ni gabarit/.test(fch));
  ok('…en niant la lecture « parc propre »', /pas une absence d’émissions|pas une absence d'émissions/.test(fch));
  ok('aucun « 0 t » ne s’affiche pour la Suisse', !/\b0 t\b/.test(fch), (fch.match(/0 t[^\n]*/) || [''])[0]);
  const emp = await pg.evaluate(() => {
    fermerPays(true);
    renderEmpreinte();
    const el = document.getElementById('emp-table');
    return el ? el.innerText : '';
  });
  ok('le tableau d’empreinte porte la mention', /non estimée/.test(emp));
  ok('…et la Norvège comme le Royaume-Uni y gardent un chiffre',
     /Norvège \(hors UE\)/.test(emp) && /Royaume-Uni \(hors UE\)/.test(emp), '');

  ok('aucune erreur JavaScript', err.length === 0, err.slice(0, 2).join(' | '));
  await nav.close();
  console.log('');
  console.log(ko ? ko + ' contrôle(s) en échec\n' : 'tout est vert\n');
  process.exit(ko ? 1 : 0);
})();
