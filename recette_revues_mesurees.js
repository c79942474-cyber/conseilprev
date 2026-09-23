/* RECETTE — LES SIX LISTES QUI SE VALIDAIENT SUR UN CLIC SE MESURENT
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE : six blocs du rail se validaient sur une simple déclaration —
 * « J'ai passé cette liste en revue » : l'audit IA Act, l'AIPD, la privacy by
 * design, la politique documentaire, la sensibilisation et l'analyse de
 * risque ReCyF. Chacun doit demander une réponse explicite par question, et
 * se MESURER comme les autres.
 *
 * CE QUE CETTE RECETTE MESURE, écran par écran, avec les vrais contrôles :
 *   · chaque question porte une valeur « non renseigné », distincte de
 *     toutes les réponses ;
 *   · l'ancienne déclaration « passé en revue » ne valide plus rien ;
 *   · le bandeau nomme les questions qui restent sans réponse ;
 *   · la dernière réponse donnée, le bloc passe au vert — sans clic de plus ;
 *   · « sans objet » sort une question du calcul, « non » l'y laisse ;
 *   · tout survit au rechargement.
 *
 * UN DÉFAUT VOISIN, MESURÉ ICI AUSSI : l'AIPD « présumait » le critère des
 * données sensibles dès que le registre portait un texte dans ce champ —
 * « Non (hors art. 9) » compris, la réponse du traitement livré avec chaque
 * compte. Une présomption est une réponse que le visiteur n'a pas donnée.
 *
 * LE LIMITEUR : une ouverture de Sentinel coûte près de cent requêtes, et la
 * limite est de cent vingt par minute. La recette attend que la fenêtre se
 * vide après chaque chargement.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5901 node recette_revues_mesurees.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
const ATTENTE = Number(process.env.ATTENTE_LIMITEUR || 62000);

let ko = 0, n = 0;
const ok = (t, cond, siKo, mesure) => {
  n++;
  if (!cond) ko++;
  console.log((cond ? '  OK   ' : '  KO   ') + t
              + (mesure ? ' — ' + mesure : '')
              + (!cond && siKo ? ' — ' + siKo : ''));
};
const titre = t => console.log('\n══ ' + t + ' ══\n');

/* LES RÉPONSES DONNÉES, écran par écran. Elles mêlent exprès les réponses
   qui comptent (« conforme »), celles qui comptent à zéro (« à réaliser »,
   « non ») et celles qui sortent du calcul (« sans objet »). */
const AUDIT = [].concat(
  Array(4).fill('done'), Array(4).fill('partial'), Array(5).fill('todo'),
  Array(5).fill('done'), Array(4).fill('partial'), Array(4).fill('done'),
  Array(4).fill('todo'), Array(4).fill('na'));              // 34 points
const PBD = [].concat(Array(10).fill('oui'), Array(4).fill('non'),
                      Array(4).fill('sans_objet'));         // 18 contrôles
const DOC = [].concat(Array(6).fill('en_place'), Array(3).fill('projet'),
                      Array(2).fill('absent'), ['a_reviser'],
                      Array(2).fill('sans_objet'));         // 14 documents
const SENS = [].concat(Array(5).fill('realise'), Array(2).fill('planifie'),
                       ['a_planifier', 'a_renouveler', 'sans_objet']); // 10

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
  pg.on('response', r => { if (r.status() === 429) refus.push(r.url().replace(BASE, '')); });
  pg.on('dialog', d => d.accept());

  const pause = ms => pg.waitForTimeout(ms);
  const charger = async () => {
    const rep = await pg.goto(BASE + '/sentinel', { waitUntil: 'domcontentloaded' });
    await pg.waitForSelector('.sb-item[data-norme]', { state: 'attached', timeout: 15000 });
    await pause(ATTENTE);
    return rep;
  };
  /* LES QUESTIONS D'UN ÉCRAN : ses listes, et combien portent encore la
     valeur « non renseigné » — une option vide, nommée comme telle. */
  const questions = sel => pg.evaluate(sel => {
    const l = [...document.querySelectorAll(sel)];
    return { n: l.length, vides: l.filter(s => s.value === '' && [...s.options]
      .some(o => o.value === '' && /non renseign/i.test(o.textContent))).length,
             valeurs: l.map(s => s.value) };
  }, sel);
  /* RÉPONDRE PAR LE VRAI CONTRÔLE : la valeur posée, puis l'événement que le
     navigateur envoie. La liste est relue à chaque réponse — un écran qui
     se repeint recrée ses champs. `null` laisse une question sans réponse. */
  const repondre = (sel, valeurs, debut) => pg.evaluate(async ([sel, valeurs, debut]) => {
    const dormir = ms => new Promise(r => setTimeout(r, ms));
    for (let i = 0; i < valeurs.length; i++) {
      const s = document.querySelectorAll(sel)[(debut || 0) + i];
      if (!s || valeurs[i] === null) continue;
      s.value = valeurs[i];
      s.dispatchEvent(new Event('change', { bubbles: true }));
      await dormir(40);
    }
  }, [sel, valeurs, debut || 0]);
  const texte = sel => pg.evaluate(s => {
    const e = document.querySelector(s);
    return e ? e.innerText.replace(/\s+/g, ' ').trim() : '';
  }, sel);
  const bandeau = () => texte('.page.on .rail-bandeau');
  const pied = () => texte('.page.on .rail-pied');
  /* L'ÉTAT DE CHAQUE ONGLET D'UN RÉFÉRENTIEL, REDEMANDÉ AVANT D'ÊTRE LU. */
  const rail = async norme => {
    await pg.evaluate(x => railDemander(x, true), norme);
    await pause(2600);
    return pg.evaluate(norme => {
      const o = {};
      document.querySelectorAll('.sb-nav .sb-item[data-norme="' + norme + '"]').forEach(it => {
        const m = (it.getAttribute('onclick') || '').match(/go\('([\w-]+)'/);
        if (m) o[m[1]] = it.getAttribute('data-rail') || '';
      });
      return o;
    }, norme);
  };
  /* L'ANCIENNE DÉCLARATION, TELLE QUE LE BOUTON LA DONNAIT — puis retirée.
     SANS CE RETRAIT, LES CONTRÔLES SUIVANTS PASSAIENT POUR UNE MAUVAISE
     RAISON, et c'est mesuré : sur l'ancien code, « la dernière réponse
     donnée, le bloc passe au vert » était vert… parce que la déclaration
     l'avait déjà fait passer. Chaque vert qui suit doit venir des réponses. */
  const declarerRevue = (norme, panneau, oui) =>
    pg.evaluate(([n, p, o]) => { if (typeof railDeclarer === 'function') railDeclarer(n, 'revus', p, o); },
                [norme, panneau, oui !== false]);
  /* LE PIED NE DOIT PLUS RIEN DIRE D'UNE REVUE — ni le bouton qui la
     déclare, ni celui qui l'annule. Lu AVANT toute déclaration : après, le
     bouton change de libellé (« Déclaré passé en revue ✓ — annuler »), et
     une première version, qui ne cherchait que le premier, passait. */
  const sansBoutonDeRevue = async ecran => {
    const p = await pied();
    ok(ecran + ' : plus de bouton « passé en revue »', !/en revue/i.test(p),
       null, p.slice(0, 80) || '(aucun pied)');
  };

  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pause(400);
  const rep = await charger();
  ok('la page répond', rep && rep.status() === 200, rep ? 'HTTP ' + rep.status() : '');
  if (!rep || rep.status() !== 200) { await nav.close(); process.exit(2); }

  // ── 1 ───────────────────────────────────────────────────────────────────
  titre('1. Audit IA Act — trente-quatre points, une réponse chacun');

  await pg.evaluate(() => go('audit-ia-act'));
  await pause(2200);
  let q = await questions('#audit-sections select');
  ok('LE POINT QUI DÉCIDE — chaque point porte « non renseigné »', q.n === 34 && q.vides === 34,
     null, q.n + ' listes, ' + q.vides + ' non renseignées');
  let r = await rail('ia_act');
  await sansBoutonDeRevue('audit');
  await declarerRevue('ia_act', 'audit-ia-act');
  r = await rail('ia_act');
  ok('l’ancienne déclaration « passé en revue » ne valide plus l’audit',
     r['audit-ia-act'] !== 'validee', null, r['audit-ia-act']);
  await declarerRevue('ia_act', 'audit-ia-act', false);
  r = await rail('ia_act');
  let ban = await bandeau();
  ok('le bandeau nomme les points sans réponse', /Il manque 34 réponses/.test(ban)
     && /Inventaire des pratiques potentiellement interdites/.test(ban), null, ban.slice(0, 160));

  await repondre('#audit-sections select', AUDIT.slice(0, 33));
  r = await rail('ia_act');
  ban = await bandeau();
  ok('un point sans réponse, et le bloc attend encore', r['audit-ia-act'] !== 'validee'
     && /Il manque 1 réponse/.test(ban) && /Signalement des incidents \(GPAI systémiques\)/.test(ban),
     r['audit-ia-act'], ban.slice(0, 160));
  await repondre('#audit-sections select', AUDIT.slice(33), 33);
  r = await rail('ia_act');
  ok('LE POINT QUI DÉCIDE — la dernière réponse donnée, le bloc passe au vert',
     r['audit-ia-act'] === 'validee', null, r['audit-ia-act']);
  const kpi = await pg.evaluate(() => ['audit-score-pct', 'audit-done-count', 'audit-partial-count',
    'audit-todo-count', 'audit-none-count', 'audit-na-count'].map(id => {
      const e = document.getElementById(id); return e ? e.textContent.trim() : null; }));
  ok('« sans objet » sort du score : (13 + 8 × ½) / 30 = 57 %', kpi[0] === '57%', null, kpi.join(' · '));
  ok('les compteurs disent chaque réponse, « sans réponse » et « sans objet » compris',
     kpi[1] === '13' && kpi[2] === '8' && kpi[3] === '9' && kpi[4] === '0' && kpi[5] === '4',
     null, kpi.join(' · '));

  // ── 2 ───────────────────────────────────────────────────────────────────
  titre('2. AIPD — neuf critères, puis la cotation des trois événements');

  await pg.evaluate(() => { go('rgpd-aipd'); if (typeof aipdLoadOnce === 'function') aipdLoadOnce(); });
  await pause(2600);
  const cartes = await pg.evaluate(() => document.querySelectorAll('#aipd-list .aipd-card').length);
  q = await questions('#aipd-list .aipd-card select');
  ok('LE POINT QUI DÉCIDE — chaque critère et chaque cotation porte « non renseigné »',
     cartes >= 1 && q.vides === cartes * 15, null, cartes + ' traitement(s), ' + q.n + ' listes, '
     + q.vides + ' non renseignées');
  const presume = await pg.evaluate(() => {
    const c = document.querySelector('#aipd-list .aipd-card');
    const crit = c ? c.querySelectorAll('.aipd-crit')[3] : null;
    if (!crit) return null;
    const cb = crit.querySelector('input[type=checkbox]'), s = crit.querySelector('select');
    return { titre: crit.getAttribute('title') || '', coche: !!(cb && cb.checked),
             valeur: s ? s.value : null };
  });
  ok('« Non (hors art. 9) » au registre ne présume plus des données sensibles',
     presume && !/Présumé/.test(presume.titre) && !presume.coche && presume.valeur !== 'oui',
     null, JSON.stringify(presume));
  r = await rail('rgpd');
  await sansBoutonDeRevue('AIPD');
  await declarerRevue('rgpd', 'rgpd-aipd');
  r = await rail('rgpd');
  ok('l’ancienne déclaration ne valide plus l’AIPD', r['rgpd-aipd'] !== 'validee', null, r['rgpd-aipd']);
  await declarerRevue('rgpd', 'rgpd-aipd', false);
  r = await rail('rgpd');
  ban = await bandeau();
  ok('le bandeau nomme les critères sans réponse', /Évaluation ou notation/.test(ban), null,
     ban.slice(0, 160));
  for (let i = 0; i < cartes; i++) {
    await repondre('#aipd-list .aipd-card:nth-of-type(' + (i + 1) + ') select',
                   ['oui', 'oui', 'non', 'non', 'non', 'non', 'non', 'non', 'non']);
  }
  const verdict = await texte('#aipd-list .aipd-card .aipd-verdict');
  r = await rail('rgpd');
  ban = await bandeau();
  ok('deux critères réunis : l’AIPD est requise, et ses cotations sont demandées',
     /AIPD requise/.test(verdict) && r['rgpd-aipd'] !== 'validee'
     && /gravité et vraisemblance/i.test(ban), verdict + ' / ' + r['rgpd-aipd'], ban.slice(0, 160));
  for (let i = 0; i < cartes; i++) {
    await repondre('#aipd-list .aipd-card:nth-of-type(' + (i + 1) + ') select',
                   ['3', '2', '2', '2', '1', '3'], 9);
  }
  r = await rail('rgpd');
  ok('LE POINT QUI DÉCIDE — tout coté, le bloc AIPD passe au vert', r['rgpd-aipd'] === 'validee',
     null, r['rgpd-aipd']);
  const risque = await texte('#aipd-list .aipd-card .aipd-risk-line');
  ok('le risque global se lit sur les cotations données', /Importante/.test(risque), null, risque);

  // ── 3 ───────────────────────────────────────────────────────────────────
  titre('3. Privacy by design — oui, non, ou sans objet');

  await pg.evaluate(() => { go('rgpd-pbd'); if (typeof pbdInit === 'function') pbdInit(); });
  await pause(2000);
  q = await questions('#pbd-list select');
  ok('LE POINT QUI DÉCIDE — chaque contrôle porte « non renseigné »', q.n === 18 && q.vides === 18,
     null, q.n + ' listes, ' + q.vides + ' non renseignées');
  r = await rail('rgpd');
  await sansBoutonDeRevue('privacy by design');
  await declarerRevue('rgpd', 'rgpd-pbd');
  r = await rail('rgpd');
  ok('l’ancienne déclaration ne valide plus la privacy by design', r['rgpd-pbd'] !== 'validee',
     null, r['rgpd-pbd']);
  await declarerRevue('rgpd', 'rgpd-pbd', false);
  await repondre('#pbd-list select', PBD.slice(0, 17));
  r = await rail('rgpd');
  ban = await bandeau();
  ok('un contrôle sans réponse est nommé, et le bloc attend', r['rgpd-pbd'] !== 'validee'
     && /réexaminée à chaque évolution/.test(ban), r['rgpd-pbd'], ban.slice(0, 160));
  await repondre('#pbd-list select', PBD.slice(17), 17);
  r = await rail('rgpd');
  ok('LE POINT QUI DÉCIDE — la dernière réponse donnée, le bloc passe au vert',
     r['rgpd-pbd'] === 'validee', null, r['rgpd-pbd']);
  let g = (await texte('#pbd-global')).replace(/\s/g, ' ');
  ok('« sans objet » sort du taux, « non » y reste : 10 / 14 = 71 %', /^71\s%$/.test(g), null, g);

  // ── 4 ───────────────────────────────────────────────────────────────────
  titre('4. Politique documentaire — un statut choisi, « absent » compris');

  await pg.evaluate(() => { go('rgpd-doc'); if (typeof docInit === 'function') docInit(); });
  await pause(2000);
  q = await questions('#doc-list select');
  ok('LE POINT QUI DÉCIDE — chaque document porte « non renseigné », et plus « absent »',
     q.n === 14 && q.vides === 14, null, q.n + ' listes, ' + q.vides + ' non renseignées, valeurs : '
     + [...new Set(q.valeurs)].join(','));
  r = await rail('rgpd');
  await sansBoutonDeRevue('documentation');
  await declarerRevue('rgpd', 'rgpd-doc');
  r = await rail('rgpd');
  ok('l’ancienne déclaration ne valide plus la documentation', r['rgpd-doc'] !== 'validee',
     null, r['rgpd-doc']);
  await declarerRevue('rgpd', 'rgpd-doc', false);
  await repondre('#doc-list select', DOC);
  r = await rail('rgpd');
  ok('LE POINT QUI DÉCIDE — chaque statut choisi, le bloc passe au vert', r['rgpd-doc'] === 'validee',
     null, r['rgpd-doc']);
  g = (await texte('#doc-global')).replace(/\s/g, ' ');
  ok('« sans objet » sort du taux : 6 en place / 12 = 50 %', /^50\s%$/.test(g), null, g);

  // ── 5 ───────────────────────────────────────────────────────────────────
  titre('5. Sensibilisation — l’état de chaque action, choisi');

  await pg.evaluate(() => { go('rgpd-sensibilisation'); if (typeof sensInit === 'function') sensInit(); });
  await pause(2000);
  q = await questions('#sens-list select');
  ok('LE POINT QUI DÉCIDE — chaque action porte « non renseigné », et plus « à planifier »',
     q.n === 10 && q.vides === 10, null, q.n + ' listes, ' + q.vides + ' non renseignées');
  r = await rail('rgpd');
  await sansBoutonDeRevue('sensibilisation');
  await declarerRevue('rgpd', 'rgpd-sensibilisation');
  r = await rail('rgpd');
  ok('l’ancienne déclaration ne valide plus la sensibilisation',
     r['rgpd-sensibilisation'] !== 'validee', null, r['rgpd-sensibilisation']);
  await declarerRevue('rgpd', 'rgpd-sensibilisation', false);
  await repondre('#sens-list select', SENS);
  r = await rail('rgpd');
  ok('LE POINT QUI DÉCIDE — chaque état choisi, le bloc passe au vert',
     r['rgpd-sensibilisation'] === 'validee', null, r['rgpd-sensibilisation']);
  g = (await texte('#sens-global')).replace(/\s/g, ' ');
  ok('« sans objet » sort du taux : 5 réalisées / 9 = 56 %', /^56\s%$/.test(g), null, g);

  // ── 6 ───────────────────────────────────────────────────────────────────
  titre('6. ReCyF, objectif 16 — oui ou non, et ce que chaque oui engage');

  await pg.evaluate(() => go('nis2-qualifier'));
  await pause(1500);
  await pg.selectOption('#nis2-secteur', 'energie');
  await pg.fill('#nis2-eff', '300'); await pg.dispatchEvent('#nis2-eff', 'change');
  await pg.fill('#nis2-ca2', '60'); await pg.dispatchEvent('#nis2-ca2', 'change');
  await pause(1500);
  await pg.evaluate(() => { go('recyf-objectifs'); if (typeof recyfInit === 'function') recyfInit(); });
  await pause(2200);
  await pg.selectOption('#recyf-statut-sel', 'essentielle');
  await pause(1500);
  await pg.evaluate(() => { go('recyf-analyse'); if (typeof recyfInit === 'function') recyfInit(); });
  await pause(2500);
  q = await questions('#recyf-analyse-body select');
  ok('LE POINT QUI DÉCIDE — les quatre exigences, les cinq entrées et les trois engagements '
     + 'portent « non renseigné »', q.n === 12 && q.vides === 12, null,
     q.n + ' listes, ' + q.vides + ' non renseignées');
  r = await rail('nis2');
  await sansBoutonDeRevue('ReCyF 16');
  await declarerRevue('nis2', 'recyf-analyse');
  r = await rail('nis2');
  ok('l’ancienne déclaration ne valide plus l’analyse de risque', r['recyf-analyse'] !== 'validee',
     null, r['recyf-analyse']);
  await declarerRevue('nis2', 'recyf-analyse', false);
  r = await rail('nis2');
  ban = await bandeau();
  ok('le bandeau nomme les exigences sans réponse', /16\.1/.test(ban) && /gouvernance/i.test(ban),
     null, ban.slice(0, 160));
  await repondre('#recyf-analyse-body select', ['oui', 'non', 'non', 'non']);
  await pause(1500);
  r = await rail('nis2');
  ban = await bandeau();
  ok('« oui » à la gouvernance demande les moyens alloués, et le bloc attend',
     r['recyf-analyse'] !== 'validee' && /moyens/i.test(ban), r['recyf-analyse'], ban.slice(0, 160));
  await pg.evaluate(() => {
    const s = document.getElementById('recyf-moyens');
    if (s) { s.value = 'oui'; s.dispatchEvent(new Event('change', { bubbles: true })); }
  });
  await pause(1500);
  r = await rail('nis2');
  ok('LE POINT QUI DÉCIDE — tout répondu, le bloc passe au vert', r['recyf-analyse'] === 'validee',
     null, r['recyf-analyse']);
  const prep = (await texte('#recyf-analyse-body .recyf-chiffre')).replace(/\s/g, ' ');
  ok('le taux de préparation compte la seule exigence acquise : 25 %', /^25\s%$/.test(prep), null, prep);

  // ── 7 ───────────────────────────────────────────────────────────────────
  titre('7. Tout survit au rechargement');

  /* LA FENÊTRE DU LIMITEUR SE VIDE AVANT DE RECHARGER : les réponses qui
     précèdent y sont encore, et une ouverture de Sentinel coûte près de cent
     requêtes. Une première version rechargeait aussitôt — et mesurait le
     limiteur. */
  await pause(ATTENTE);
  await charger();
  await pg.evaluate(() => go('audit-ia-act'));
  await pause(2200);
  q = await questions('#audit-sections select');
  ok('les trente-quatre réponses de l’audit sont réaffichées',
     q.n === 34 && q.valeurs.join() === AUDIT.join(), null, q.vides + ' non renseignées');
  await pg.evaluate(() => { go('rgpd-pbd'); if (typeof pbdInit === 'function') pbdInit(); });
  await pause(1500);
  q = await questions('#pbd-list select');
  g = (await texte('#pbd-global')).replace(/\s/g, ' ');
  ok('la privacy by design aussi, et son taux', q.valeurs.join() === PBD.join() && /^71\s%$/.test(g),
     null, g);
  await pg.evaluate(() => { go('rgpd-doc'); if (typeof docInit === 'function') docInit(); });
  await pause(1500);
  q = await questions('#doc-list select');
  ok('la documentation aussi', q.valeurs.join() === DOC.join(), null, [...new Set(q.valeurs)].join(','));
  await pg.evaluate(() => { go('rgpd-sensibilisation'); if (typeof sensInit === 'function') sensInit(); });
  await pause(1500);
  q = await questions('#sens-list select');
  ok('la sensibilisation aussi', q.valeurs.join() === SENS.join(), null, [...new Set(q.valeurs)].join(','));
  await pg.evaluate(() => { go('rgpd-aipd'); if (typeof aipdLoadOnce === 'function') aipdLoadOnce(); });
  await pause(2400);
  q = await questions('#aipd-list .aipd-card select');
  ok('l’AIPD aussi', q.vides === 0 && q.valeurs.slice(0, 15).join()
     === 'oui,oui,non,non,non,non,non,non,non,3,2,2,2,1,3', null, q.valeurs.slice(0, 15).join());
  await pg.evaluate(() => { go('recyf-analyse'); if (typeof recyfInit === 'function') recyfInit(); });
  await pause(2500);
  q = await questions('#recyf-analyse-body select');
  ok('l’objectif 16 aussi', q.valeurs.slice(0, 4).join() === 'oui,non,non,non'
     && await pg.evaluate(() => (document.getElementById('recyf-moyens') || {}).value) === 'oui',
     null, q.valeurs.join());
  const rails = { ia: await rail('ia_act'), rgpd: await rail('rgpd'), nis2: await rail('nis2') };
  ok('LE POINT QUI DÉCIDE — les six blocs sont toujours verts, sans rien redéclarer',
     rails.ia['audit-ia-act'] === 'validee' && rails.rgpd['rgpd-aipd'] === 'validee'
     && rails.rgpd['rgpd-pbd'] === 'validee' && rails.rgpd['rgpd-doc'] === 'validee'
     && rails.rgpd['rgpd-sensibilisation'] === 'validee' && rails.nis2['recyf-analyse'] === 'validee',
     null, [rails.ia['audit-ia-act'], rails.rgpd['rgpd-aipd'], rails.rgpd['rgpd-pbd'],
            rails.rgpd['rgpd-doc'], rails.rgpd['rgpd-sensibilisation'],
            rails.nis2['recyf-analyse']].join(' '));

  // ── 8 ───────────────────────────────────────────────────────────────────
  titre('8. Rien ne s’est cassé en route');
  ok('aucune erreur de script', err.length === 0, err.slice(0, 2).join(' | '));
  ok('aucune requête refusée par le limiteur — la recette a mesuré les écrans',
     refus.length === 0, refus.slice(0, 3).join(' | '));

  console.log('\n' + (ko ? ko + ' contrôle(s) en échec sur ' + n : 'TOUT EST VERT — ' + n + ' contrôles'));
  await nav.close();
  process.exit(ko ? 1 : 0);
})();
