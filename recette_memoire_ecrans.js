/* RECETTE — LES ÉCRANS GARDENT LEURS RÉPONSES AU RECHARGEMENT
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE : « NIS 2 perd ses réponses au rechargement de la page. Son rail
 * repart alors de « Suis-je concerné ? » » — et, mesuré ensuite, ISO 27001,
 * ISO 42001, le CRA et DORA aussi. Les réponses NIST, OWASP, 800-53 et 800-82
 * survivaient déjà ; celles-ci non.
 *
 * CE QUE LES RÈGLES DE LA SUITE NE VOIENT PAS, ET QUE CETTE RECETTE MESURE :
 * un vrai rechargement. Les réponses sont données par les vrais contrôles de
 * chaque écran, la page est rechargée, et l'on compare ce que le rail, le
 * taux de conformité et les champs AFFICHÉS disent avant et après.
 *
 * TROIS DÉFAUTS TROUVÉS EN LISANT LE CODE, MESURÉS ICI SANS RECHARGER :
 *   · ReCyF, objectif 16 : cocher « moyens alloués » décochait la case au
 *     repeint suivant — la réponse se perdait dans la session même ;
 *   · CRA : revenir sur l'analyse d'écart affichait « non renseigné » sur
 *     les exigences déjà cotées ;
 *   · DORA : revenir sur le cadre de risque affichait « non déclaré » sur
 *     les articles déjà déclarés.
 *
 * LE LIMITEUR : une ouverture de Sentinel coûte près de cent requêtes, et la
 * limite est de cent vingt par minute. La recette attend que la fenêtre se
 * vide avant chaque série de réponses, et après chaque rechargement.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5901 node recette_memoire_ecrans.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
const ATTENTE = Number(process.env.ATTENTE_LIMITEUR || 62000);
const NORMES = ['nis2', 'iso27001', 'iso42001', 'cra', 'dora'];

let ko = 0, n = 0;
const ok = (t, cond, siKo, mesure) => {
  n++;
  if (!cond) ko++;
  console.log((cond ? '  OK   ' : '  KO   ') + t
              + (mesure ? ' — ' + mesure : '')
              + (!cond && siKo ? ' — ' + siKo : ''));
};
const titre = t => console.log('\n══ ' + t + ' ══\n');

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1440, height: 1000 } });
  /* SANS CE MASQUE, LE SERVEUR BLOQUE L'ADRESSE POUR 1800 s. */
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e).slice(0, 160)));
  const refus = [];
  pg.on('response', r => {
    if (r.status() >= 400) refus.push(r.status() + ' ' + r.url().replace(BASE, ''));
  });

  const charger = async () => {
    const rep = await pg.goto(BASE + '/sentinel', { waitUntil: 'domcontentloaded' });
    await pg.waitForSelector('.sb-item[data-norme]', { state: 'attached', timeout: 15000 });
    await pg.waitForTimeout(ATTENTE);
    return rep;
  };
  const pause = ms => pg.waitForTimeout(ms);
  const aller = async (id, ms) => { await pg.evaluate(i => go(i), id); await pause(ms || 1400); };
  const remplir = async (sel, v) => {
    await pg.fill(sel, v); await pg.dispatchEvent(sel, 'change'); await pause(900);
  };
  const choisir = async (loc, v) => { await loc.selectOption(v); await pause(1100); };
  const ouvrirTiroir = async grp => {
    const ouvert = await pg.getAttribute('.sb-section[data-grp="' + grp + '"]', 'aria-expanded');
    if (ouvert !== 'true') { await pg.click('.sb-section[data-grp="' + grp + '"]'); await pause(1000); }
  };
  /* CHAQUE RAIL EST REDEMANDÉ AVANT D'ÊTRE LU. Après un rechargement, seul
     le tiroir ouvert est repeint ; lire les autres dirait « vide » pour une
     raison qui n'a rien à voir avec les réponses. */
  const rails = async () => {
    for (const nm of NORMES) await pg.evaluate(x => railDemander(x, true), nm);
    await pause(3500);
    return pg.evaluate(normes => {
      const o = {};
      normes.forEach(n => {
        o[n] = [...document.querySelectorAll('.sb-nav .sb-item[data-norme="' + n + '"]')]
          .map(i => i.getAttribute('data-rail') || '');
      });
      return o;
    }, NORMES);
  };
  const cartes = async () => {
    await pg.evaluate(() => { go('conf-taux'); confInit(); });
    await pause(2600);
    return pg.evaluate(() => {
      const out = {};
      document.querySelectorAll('#conf-grille .conf-c').forEach(c => {
        out[c.querySelector('.conf-c-n').textContent.trim()] =
          c.querySelector('.conf-c-v').textContent.trim();
      });
      return out;
    });
  };
  const valeur = sel => pg.evaluate(s => {
    const e = document.querySelector(s);
    if (!e) return null;
    return e.type === 'checkbox' ? e.checked : e.value;
  }, sel);

  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pause(400);
  const rep = await charger();
  ok('la page répond', rep && rep.status() === 200, rep ? 'HTTP ' + rep.status() : '');
  if (!rep || rep.status() !== 200) { await nav.close(); process.exit(2); }

  // ── 1 ───────────────────────────────────────────────────────────────────
  titre('1. NIS 2 et ReCyF, répondus par leurs vrais contrôles');

  await ouvrirTiroir('nis2');
  await pg.click('.sb-item[data-norme="nis2"] >> nth=0');
  await pause(1600);
  await choisir(pg.locator('#nis2-secteur'), 'energie');
  await remplir('#nis2-eff', '300');
  await remplir('#nis2-ca2', '60');
  await remplir('#nis2-bilan', '50');
  await aller('nis2');
  await choisir(pg.locator('#nis2-mesures-body select').first(), 'conforme');
  await aller('nis2-gouvernance');
  await choisir(pg.locator('#nis2-gouv-body select').first(), 'conforme');
  await aller('nis2-chiffre');
  await remplir('#nis2-ca', '450');
  await aller('recyf-objectifs', 1800);
  await choisir(pg.locator('#recyf-statut-sel'), 'essentielle');
  await pause(800);
  await choisir(pg.locator('#recyf-body select').first(), 'atteint');
  await aller('recyf-analyse', 1800);
  await pg.check('#recyf-a-gouvernance'); await pause(1400);
  await pg.check('#recyf-moyens'); await pause(1400);
  await pg.check('#recyf-e-pssi'); await pause(1400);
  const moyens = await valeur('#recyf-moyens');
  const acquis = await pg.evaluate(() => {
    const c = document.getElementById('recyf-a-gouvernance');
    return c ? c.parentElement.textContent.trim() : '';
  });
  ok('ReCyF 16.1 — la case « moyens alloués » reste cochée après deux repeints',
     moyens === true, 'décochée par le repeint : la réponse est perdue dans la session');
  ok('…et la gouvernance reste « acquise », puisque ses moyens le sont',
     /acquis/.test(acquis), 'l\'exigence est retombée à « ' + acquis + ' »');

  // ── 2 ───────────────────────────────────────────────────────────────────
  titre('2. ISO 27001 et ISO 42001');
  await pause(ATTENTE);

  await ouvrirTiroir('iso27001');
  await pg.click('.sb-item[data-norme="iso27001"] >> nth=0');
  await pause(1800);
  await remplir('#iso27-perimetre', 'SI de production du siège');
  await remplir('#iso27-etabli', '2026-01-10');
  await remplir('#iso27-apprecie', '2026-02-01');
  await pg.click('#p-iso27001-risques button:has-text("Ajouter un risque")');
  await pause(1200);
  await pg.evaluate(() => document.querySelectorAll('#iso27-risques-body details').forEach(d => { d.open = true; }));
  await remplir('#iso27-risques-body input[placeholder="Intitulé du risque"]', 'Rançongiciel');
  await aller('iso27001', 1600);
  await choisir(pg.locator('#iso27-art-body select').first(), 'conforme');
  await ouvrirTiroir('iso42001');
  await aller('iso42001', 1800);
  await choisir(pg.locator('#iso-art-body select').first(), 'conforme');

  // ── 3 ───────────────────────────────────────────────────────────────────
  titre('3. CRA');

  await ouvrirTiroir('cra');
  await aller('cra-role', 1600);
  await pg.locator('#cra-role-q input[type="checkbox"]').first().check();
  await pause(1100);
  await aller('cra', 1400);
  await pg.fill('#cra-nom', 'Routeur R1');
  await pg.click('button:has-text("Ajouter au registre")');
  await pause(1400);
  await aller('cra-ecarts', 1400);
  await choisir(pg.locator('#cra-ec-body select').first(), 'conforme');
  await aller('cra-chiffre', 1200);
  await remplir('#cra-ca', '45');
  await aller('cra', 1200);
  await aller('cra-ecarts', 1400);
  ok('CRA — revenir sur l\'analyse d\'écart montre l\'exigence cotée',
     (await pg.locator('#cra-ec-body select').first().inputValue()) === 'conforme',
     'le sélecteur est revenu à « non renseigné »');

  // ── 4 ───────────────────────────────────────────────────────────────────
  titre('4. DORA');
  await pause(ATTENTE);

  await ouvrirTiroir('dora');
  await pg.click('.sb-item[data-norme="dora"] >> nth=0');
  await pause(1800);
  await choisir(pg.locator('#dora-entite'), 'etablissement_credit');
  await choisir(pg.locator('#dora-nis2'), 'oui');
  await aller('dora-risque', 1800);
  await choisir(pg.locator('#dora-risque-body select').first(), 'tenu');
  await aller('dora-tiers', 1400);
  await choisir(pg.locator('#dora-contrat-form select').first(), 'oui');
  await aller('dora-incident', 1400);
  await choisir(pg.locator('#dora-incident-form select').first(), 'oui');
  await aller('dora-risque', 1800);
  ok('DORA — revenir sur le cadre de risque montre l\'article déclaré',
     (await pg.locator('#dora-risque-body select').first().inputValue()) === 'tenu',
     'le sélecteur est revenu à « non déclaré »');

  // ── 5 ───────────────────────────────────────────────────────────────────
  titre('5. Ce que le rail et le taux disent AVANT le rechargement');
  await pause(1500);

  const railAvant = await rails();
  const tauxAvant = await cartes();
  NORMES.forEach(nm => console.log('       rail ' + nm + ' : ' + railAvant[nm].join(' ')));
  console.log('       taux : ' + JSON.stringify(tauxAvant));
  ok('le rail NIS 2 tient « Suis-je concerné ? » pour rempli',
     railAvant.nis2[0] === 'validee', '', railAvant.nis2[0]);

  // ── 6 ───────────────────────────────────────────────────────────────────
  titre('6. Rechargement : le rail et le taux disent la même chose');
  await pause(ATTENTE);
  await charger();

  const railApres = await rails();
  NORMES.forEach(nm => {
    ok('le rail ' + nm + ' est celui d\'avant le rechargement',
       JSON.stringify(railApres[nm]) === JSON.stringify(railAvant[nm]),
       'avant : ' + railAvant[nm].join(' ') + ' | après : ' + railApres[nm].join(' '));
  });
  ok('LE POINT QUI DÉCIDE — le rail NIS 2 ne repart pas de « Suis-je concerné ? »',
     railApres.nis2[0] === 'validee', '', railApres.nis2[0]);
  const tauxApres = await cartes();
  ['NIS 2', 'ISO/IEC 27001', 'ISO/IEC 42001', 'CRA', 'DORA'].forEach(k => {
    ok('la carte ' + k + ' du taux est celle d\'avant',
       tauxApres[k] !== undefined && tauxApres[k] === tauxAvant[k],
       'avant : ' + tauxAvant[k] + ' | après : ' + tauxApres[k], tauxApres[k]);
  });

  // ── 7 ───────────────────────────────────────────────────────────────────
  titre('7. Les champs AFFICHÉS portent les réponses');

  await aller('nis2-qualifier', 1800);
  if (process.env.CAPTURE) {
    await pg.locator('#p-nis2-qualifier .memoire-note').screenshot({ path: process.env.CAPTURE });
  }
  const q = await pg.evaluate(() => ['nis2-secteur', 'nis2-eff', 'nis2-ca2', 'nis2-bilan']
    .map(i => (document.getElementById(i) || {}).value));
  ok('NIS 2 — secteur, effectif, CA et bilan réaffichés',
     JSON.stringify(q) === JSON.stringify(['energie', '300', '60', '50']), JSON.stringify(q));
  await aller('nis2', 1200);
  ok('NIS 2 — la mesure a) réaffichée',
     (await pg.locator('#nis2-mesures-body select').first().inputValue()) === 'conforme');
  await aller('nis2-gouvernance', 1200);
  ok('NIS 2 — la première ligne de gouvernance réaffichée',
     (await pg.locator('#nis2-gouv-body select').first().inputValue()) === 'conforme');
  ok('NIS 2 — le chiffre d\'affaires du groupe réaffiché', (await valeur('#nis2-ca')) === '450',
     String(await valeur('#nis2-ca')));
  await aller('recyf-objectifs', 1800);
  ok('ReCyF — la qualification réaffichée', (await valeur('#recyf-statut-sel')) === 'essentielle',
     String(await valeur('#recyf-statut-sel')));
  ok('ReCyF — le premier objectif réaffiché',
     (await pg.locator('#recyf-body select').first().inputValue().catch(() => '')) === 'atteint');
  await aller('recyf-analyse', 1800);
  ok('ReCyF — l\'objectif 16 réaffiché (gouvernance, moyens, entrée PSSI)',
     (await valeur('#recyf-a-gouvernance')) === true && (await valeur('#recyf-moyens')) === true
     && (await valeur('#recyf-e-pssi')) === true,
     JSON.stringify([await valeur('#recyf-a-gouvernance'), await valeur('#recyf-moyens'),
                     await valeur('#recyf-e-pssi')]));

  await pause(ATTENTE);
  await aller('iso27001-risques', 1800);
  const i27 = await pg.evaluate(() => ['iso27-perimetre', 'iso27-etabli', 'iso27-apprecie']
    .map(i => (document.getElementById(i) || {}).value));
  ok('ISO 27001 — périmètre et dates réaffichés',
     JSON.stringify(i27) === JSON.stringify(['SI de production du siège', '2026-01-10', '2026-02-01']),
     JSON.stringify(i27));
  ok('ISO 27001 — le risque déclaré réaffiché',
     await pg.evaluate(() => /Rançongiciel/.test((document.getElementById('iso27-risques-body') || {}).textContent || '')));
  await aller('iso27001', 1400);
  ok('ISO 27001 — le premier article réaffiché',
     (await pg.locator('#iso27-art-body select').first().inputValue()) === 'conforme');
  await aller('iso42001', 1400);
  ok('ISO 42001 — le premier article réaffiché',
     (await pg.locator('#iso-art-body select').first().inputValue()) === 'conforme');

  await aller('cra-role', 1400);
  ok('CRA — la première question du rôle réaffichée cochée',
     await pg.locator('#cra-role-q input[type="checkbox"]').first().isChecked());
  await aller('cra', 1400);
  ok('CRA — le produit déclaré réaffiché au registre',
     await pg.evaluate(() => /Routeur R1/.test((document.getElementById('cra-registre') || {}).textContent || '')));
  await aller('cra-ecarts', 1400);
  ok('CRA — l\'exigence cotée réaffichée',
     (await pg.locator('#cra-ec-body select').first().inputValue()) === 'conforme');
  ok('CRA — le chiffre d\'affaires réaffiché', (await valeur('#cra-ca')) === '45',
     String(await valeur('#cra-ca')));

  await pause(ATTENTE);
  await aller('dora-qualifier', 1800);
  ok('DORA — l\'entité et la réponse NIS 2 réaffichées',
     (await valeur('#dora-entite')) === 'etablissement_credit' && (await valeur('#dora-nis2')) === 'oui',
     JSON.stringify([await valeur('#dora-entite'), await valeur('#dora-nis2')]));
  await aller('dora-risque', 2200);
  ok('DORA — l\'article déclaré réaffiché, et le régime recalculé',
     (await pg.locator('#dora-risque-body select').first().inputValue().catch(() => '')) === 'tenu',
     await pg.evaluate(() => ((document.getElementById('dora-risque-body') || {}).innerText || '').slice(0, 90)));
  await aller('dora-tiers', 1400);
  ok('DORA — la criticité de la fonction réaffichée',
     (await pg.locator('#dora-contrat-form select').first().inputValue()) === 'oui');
  await aller('dora-incident', 1400);
  ok('DORA — la criticité de l\'incident réaffichée',
     (await pg.locator('#dora-incident-form select').first().inputValue()) === 'oui');

  // ── 8 ───────────────────────────────────────────────────────────────────
  titre('8. Une mémoire illisible ne coûte que son propre écran');
  await pause(ATTENTE);
  await pg.evaluate(() => { try { localStorage.setItem('cp-sentinel-nis2-v1', '{pas du json'); } catch (e) {} });
  const nbErr = err.length;
  await charger();
  ok('la page se charge sans erreur JavaScript', err.length === nbErr, err.slice(nbErr).join(' | '));
  const r8 = await rails();
  ok('les autres écrans gardent leurs réponses (rail DORA inchangé)',
     JSON.stringify(r8.dora) === JSON.stringify(railAvant.dora), r8.dora.join(' '));

  // ── 9 ───────────────────────────────────────────────────────────────────
  titre('9. Effacer un référentiel, et lui seul');
  await pause(ATTENTE);
  await aller('iso42001', 1800);
  ok('le premier écran ISO 42001 dit où sont les réponses',
     await pg.locator('#p-iso42001 .memoire-note').isVisible());
  let question = '';
  pg.once('dialog', d => { question = d.message(); d.accept(); });
  await Promise.all([
    pg.waitForEvent('framenavigated'),
    pg.click('#p-iso42001 .memoire-note button'),
  ]);
  await pg.waitForSelector('.sb-item[data-norme]', { state: 'attached', timeout: 15000 });
  ok('la confirmation nomme le référentiel effacé', /ISO 42001/.test(question), question);
  await pause(ATTENTE);
  const cles = await pg.evaluate(() => Object.keys(localStorage));
  ok('LE POINT QUI DÉCIDE — la mémoire ISO 42001 est effacée',
     cles.indexOf('cp-sentinel-iso42001-v1') < 0, cles.join(', '));
  ok('…et pas celle du CRA', cles.indexOf('cp-sentinel-cra-v1') >= 0, cles.join(', '));
  await aller('iso42001', 1800);
  ok('le premier article ISO 42001 est revenu à « non renseigné »',
     (await pg.locator('#iso-art-body select').first().inputValue()) === '');
  await aller('cra-chiffre', 1200);
  ok('le chiffre d\'affaires CRA est toujours là', (await valeur('#cra-ca')) === '45',
     String(await valeur('#cra-ca')));

  // ── 10 ──────────────────────────────────────────────────────────────────
  titre('10. Propreté');
  ok('aucune erreur JavaScript', err.length === 0, err.join(' | '));
  ok('aucune réponse en erreur', refus.length === 0, refus.join(' | '));

  await nav.close();
  console.log('\n' + (n - ko) + ' contrôles passés, ' + ko + ' en échec'
              + (ko ? '' : ' — TOUT EST VERT'));
  process.exit(ko ? 1 : 0);
})().catch(e => { console.error('KO   la recette a rompu : ' + e); process.exit(2); });
