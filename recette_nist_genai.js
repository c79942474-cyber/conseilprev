/* LE PROFIL IA GÉNÉRATIVE, DE BOUT EN BOUT DANS UN VRAI NAVIGATEUR.
 *
 * CE QUE LA RECETTE ÉPROUVE, ET QUE LES RÈGLES PYTHON NE PEUVENT PAS : que
 * la qualification change VRAIMENT ce que l'écran affiche, que le lot
 * réponde pour toute une sous-catégorie sans refermer les <details> ouverts,
 * que la note du cadre BAISSE sur l'écran du cadre — pas seulement dans le
 * moteur —, et que la carte du taux affiche le même nombre plafonné.
 *
 * AUCUNE ÉCRITURE : le profil vit dans la mémoire de l'écran
 * (cp-sentinel-nist-genai-v1), pas dans la base. Rien n'est prélevé.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = 'http://127.0.0.1:9941', TOKEN = 'recette_locale_idf_0123456789abcdef';
const pad = (s, n) => String(s == null ? '—' : s).padEnd(n).slice(0, n);
let verdict = 0;
const dit = (ok, quoi, detail) => {
  if (!ok) verdict = 1;
  console.log('  ' + (ok ? '✓' : '✗') + ' ' + pad(quoi, 60) + (detail == null ? '' : detail));
};

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1500, height: 1400 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e).slice(0, 170)));
  pg.on('console', m => { if (m.type() === 'error'
      && !/ERR_CERT_AUTHORITY_INVALID/.test(m.text())) err.push('CONSOLE ' + m.text().slice(0, 150)); });
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.waitForFunction(() => typeof go === 'function', null, { timeout: 40000 });
  /* ON REPART D'UNE MÉMOIRE VIDE : une recette qui hérite des réponses d'un
     essai précédent ne mesure plus que le hasard de l'ordre d'exécution. */
  await pg.evaluate(() => {
    try { localStorage.removeItem('cp-sentinel-nist-genai-v1'); } catch (e) {}
    try { localStorage.removeItem('cp-sentinel-nist-profil-v1'); } catch (e) {}
  });
  await pg.reload({ waitUntil: 'commit' });
  await pg.waitForFunction(() => typeof go === 'function', null, { timeout: 40000 });
  await pg.waitForTimeout(2500);

  /* ── 1. LA QUALIFICATION N'A PAS DE RÉPONSE PAR DÉFAUT ────────────────── */
  console.log('\n══ 1. « Ce système est-il génératif ? » ══');
  await pg.evaluate(() => { go('nist-genai'); nistInit(); });
  await pg.waitForTimeout(3000);
  let r = await pg.evaluate(() => {
    const p = document.getElementById('p-nist-genai');
    const b = [...p.querySelectorAll('.gen-oui .gen-b')];
    return { risques: p.querySelectorAll('.nist-gen li').length,
             boutons: b.map(x => x.textContent.trim() + '=' + x.getAttribute('aria-pressed')),
             retenir: p.querySelectorAll('.gen-pick').length,
             details: p.querySelectorAll('details.gen-sc').length,
             muettes: p.querySelectorAll('.gen-muet code').length,
             verdict: (document.getElementById('genai-verdict') || {}).innerText || '' };
  });
  dit(r.risques === 12, 'les douze risques sont peints', r.risques + ' risques');
  dit(r.boutons.join(' ') === 'Oui, génératif=false Non=false',
      'ni « oui » ni « non » n\'est enfoncé au départ', r.boutons.join(' '));
  dit(r.retenir === 0 && r.details === 0,
      'rien à retenir ni à répondre tant qu\'on n\'a pas qualifié');
  dit(r.muettes === 23, 'les 23 sous-catégories muettes sont nommées', r.muettes);
  dit(/pas encore de réponse/.test(r.verdict),
      'le verdict dit que la question est sans réponse');

  /* ── 2. LE RAIL TIENT LE BLOC EN ATTENTE ──────────────────────────────── */
  console.log('\n══ 2. Le rail attend la qualification ══');
  let rail = await pg.evaluate(async () => {
    const d = window.declarationsDesEcrans ? window.declarationsDesEcrans() : {};
    const rep = await fetch('/api/parcours/nist_ai_rmf', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(d.nist_ai_rmf || {})
    });
    return rep.ok ? rep.json() : { http: rep.status };
  });
  const bloc = (rail.blocs || rail.lignes || []).filter(l => l.cle === 'genai')[0];
  dit(!!bloc, 'le rail porte un bloc « genai »', bloc ? bloc.nature : JSON.stringify(rail).slice(0, 90));
  dit(bloc && bloc.nature === 'saisie', 'et c\'est une SAISIE, pas une lecture',
      bloc && bloc.nature);
  dit(bloc && bloc.etat !== 'validee', 'il n\'est pas validé sans réponse',
      bloc && (bloc.etat || 'attente'));

  /* ── 3. « OUI » OUVRE LES DOUZE RISQUES ───────────────────────────────── */
  console.log('\n══ 3. La qualification ouvre les risques ══');
  await pg.evaluate(() =>
    document.querySelector('#p-nist-genai .gen-oui .gen-b[data-oui="1"]').click());
  await pg.waitForTimeout(2200);
  r = await pg.evaluate(() => {
    const p = document.getElementById('p-nist-genai');
    return { retenir: p.querySelectorAll('.gen-pick').length,
             nb: [...p.querySelectorAll('.gen-nb')].map(x => x.textContent.trim()).slice(0, 2),
             verdict: (document.getElementById('genai-verdict') || {}).innerText || '' };
  });
  dit(r.retenir === 12, 'chaque risque porte son bouton « Retenir »', r.retenir);
  dit(r.nb.every(t => /\d+ action\(s\) du §3/.test(t)),
      'chaque risque dit combien d\'actions le traitent', r.nb[0]);
  dit(/aucun des douze risques n[’']est retenu/i.test(r.verdict),
      'le verdict nomme la réponse qu\'un auditeur ouvrira en premier');

  /* ── 4. DEUX RISQUES RETENUS → LES ACTIONS APPLICABLES ────────────────── */
  console.log('\n══ 4. Les risques commandent les actions ══');
  for (const n of [2, 5]) {
    await pg.evaluate((k) =>
      document.querySelector('#p-nist-genai .gen-pick[data-n="' + k + '"]').click(), n);
    await pg.waitForTimeout(1600);
  }
  const attendu = await pg.evaluate(async () => {
    const rep = await fetch('/api/nist-ai-rmf/profil/analyser', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ profil: { genai: true, risques: [2, 5], actions: {} } })
    });
    const j = await rep.json();
    return { champ: j.analyse.champ, plafonnees: j.analyse.categories_plafonnees };
  });
  r = await pg.evaluate(() => {
    const p = document.getElementById('p-nist-genai');
    return { selects: p.querySelectorAll('details.gen-sc select.q-sel').length,
             details: p.querySelectorAll('details.gen-sc').length,
             pris: p.querySelectorAll('.nist-gen li.gen-pris').length,
             verdict: (document.getElementById('genai-verdict') || {}).innerText || '',
             plan: p.querySelectorAll('.gen-plan li').length };
  });
  dit(r.pris === 2, 'les deux risques retenus se voient', r.pris + ' retenus');
  dit(r.selects === attendu.champ,
      'l\'écran peint EXACTEMENT les actions que le serveur dit applicables',
      r.selects + ' champs / ' + attendu.champ + ' applicables');
  dit(r.details > 0 && r.details < r.selects,
      'elles sont groupées par sous-catégorie', r.details + ' sous-catégories');
  dit(/0\s*%/.test(r.verdict) && new RegExp(attendu.plafonnees + ' / 19').test(r.verdict),
      'le verdict dit 0 % et combien de catégories sont plafonnées',
      attendu.plafonnees + ' / 19');
  dit(r.plan > 0, 'le plan propose par quoi commencer', r.plan + ' actions');

  /* ── 5. LE LOT RÉPOND POUR UNE SOUS-CATÉGORIE, SANS TOUT REPEINDRE ───── */
  console.log('\n══ 5. Le lot, et les <details> qui restent ouverts ══');
  const avant = await pg.evaluate(() => {
    const d = document.querySelector('#p-nist-genai details.gen-sc');
    d.open = true;
    return { id: d.id, compteur: d.querySelector('em').textContent.trim(),
             champs: d.querySelectorAll('select.q-sel').length };
  });
  await pg.evaluate(() => {
    const d = document.querySelector('#p-nist-genai details.gen-sc');
    d.querySelector('.gen-lot .gen-b[data-etat="tenue"]').click();
  });
  await pg.waitForTimeout(2200);
  const apres = await pg.evaluate((id) => {
    const d = document.getElementById(id);
    return { ouvert: d ? d.open : null,
             compteur: d ? d.querySelector('em').textContent.trim() : null,
             tenus: d ? [...d.querySelectorAll('select.q-sel')]
                       .filter(s => s.value === 'tenue').length : null,
             verdict: (document.getElementById('genai-verdict') || {}).innerText || '' };
  }, avant.id);
  dit(apres.ouvert === true, 'la sous-catégorie ouverte le reste après le lot');
  dit(apres.tenus === avant.champs, 'toutes ses actions passent à « tenue »',
      apres.tenus + ' / ' + avant.champs);
  dit(apres.compteur !== avant.compteur && /^\d+ \/ \d+ tenue/.test(apres.compteur),
      'son compteur suit', avant.compteur + ' → ' + apres.compteur);
  dit(!/^\s*0\s*%/.test(apres.verdict.trim()) && /%/.test(apres.verdict),
      'la couverture n\'est plus à zéro',
      (apres.verdict.match(/(\d+)\s*%/) || [])[0]);

  /* ── 6. LA NOTE DU CADRE BAISSE SUR L'ÉCRAN DU CADRE ─────────────────── */
  console.log('\n══ 6. Le profil plafonne le cadre, et l\'écran le dit ══');
  await pg.evaluate(() => { go('nist-profil'); nistInit(); });
  await pg.waitForTimeout(3000);
  /* TOUT PROUVÉ : le cas où le plafond a le plus à dire, et celui où une
     erreur passerait le plus facilement — un 100 % ne choque personne. */
  const poses = await pg.evaluate(() => {
    const sels = [...document.querySelectorAll('#p-nist-profil select.q-sel')];
    sels.forEach(s => { s.value = 'prouve'; window.nistRepondre(s); });
    return sels.length;
  });
  await pg.waitForTimeout(3000);
  r = await pg.evaluate(() => {
    const v = document.getElementById('nist-verdict');
    return { texte: (v ? v.innerText : '').replace(/\s+/g, ' '),
             notes: [...(v ? v.querySelectorAll('.q-note') : [])]
                      .map(x => x.textContent.replace(/\s+/g, ' ').trim()) };
  });
  dit(poses === 19, 'les dix-neuf catégories sont renseignées', poses);
  const note = (f) => {
    const t = (r.notes.filter(x => x.replace(/\s/g, '').indexOf(f) === 0)[0] || '');
    const m = t.match(/([\d.]+)\s*\/\s*3/);
    return m ? parseFloat(m[1]) : null;
  };
  dit(note('GOVERN') !== null && note('GOVERN') < 3,
      'GOVERN tombe sous 3/3 alors que ses six catégories sont « prouvées »',
      r.notes.join(' | '));
  /* CE QUE CETTE LIGNE MESURE ET QUI COMPTE AUTANT : le profil ne punit PAS
     là où il n'a rien à dire. Avec la Confabulation et les Impacts
     environnementaux pour seuls risques, aucune action ne se rattache aux
     catégories de MAP — elles restent donc à 3/3. Un plafond qui tomberait
     partout serait un reproche inventé, et c'est le défaut le plus facile à
     commettre ici. */
  dit(note('MAP') === 3,
      'MAP reste à 3/3 : le profil ne plafonne pas là où il ne dit rien',
      'MAP ' + note('MAP'));
  /* `innerText` rend le texte TEL QU'IL EST PEINT, et la puce du bandeau est
     en petites capitales par la feuille de style : la comparaison se fait
     donc sans tenir compte de la casse. */
  dit(/plafonné par le profil ia générative/i.test(r.texte),
      'et l\'écran dit d\'où vient la baisse');

  /* ── 7. LA CARTE DU TAUX AFFICHE LE MÊME NOMBRE ──────────────────────── */
  console.log('\n══ 7. Le taux de conformité, et sa réserve ══');
  const carte = await pg.evaluate(async () => {
    const e = window.declarationsDesEcrans ? window.declarationsDesEcrans() : {};
    const rep = await fetch('/api/conformite/etat-des-lieux', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ecrans: e })
    });
    const j = await rep.json();
    const n = (j.normes || []).filter(x => x.cle === 'nist_ai_rmf')[0] || {};
    return { taux: n.taux, brut: n.brut, ecarts: n.ecarts,
             reserves: (n.reserves || []).map(x => x.cle),
             profil: !!(e.nist_ai_rmf || {}).profil };
  });
  dit(carte.profil, 'la collecte du rail emporte bien le profil');
  dit(carte.taux !== null && carte.taux < 100,
      'la carte NIST est plafonnée, alors que tout est « prouvé »',
      carte.taux + ' % (brut ' + carte.brut + ')');
  dit(carte.taux === carte.brut,
      'le plafond est DANS la note, il n\'est pas compté deux fois');
  dit(carte.reserves.includes('profil_genai'),
      'la réserve du profil part avec le taux', carte.reserves.join(', '));
  dit(carte.ecarts > 0, 'et les catégories plafonnées deviennent des écarts',
      carte.ecarts + ' écarts');

  /* ── 8. « NON GÉNÉRATIF » REND LE TAUX DU SOCLE ──────────────────────── */
  console.log('\n══ 8. Revenir à « non » rend le taux du socle ══');
  await pg.evaluate(() => { go('nist-genai'); nistInit(); });
  await pg.waitForTimeout(2500);
  await pg.evaluate(() =>
    document.querySelector('#p-nist-genai .gen-oui .gen-b[data-oui="0"]').click());
  await pg.waitForTimeout(2200);
  const rendu = await pg.evaluate(async () => {
    const e = window.declarationsDesEcrans();
    const rep = await fetch('/api/conformite/etat-des-lieux', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ecrans: e })
    });
    const j = await rep.json();
    const n = (j.normes || []).filter(x => x.cle === 'nist_ai_rmf')[0] || {};
    return { taux: n.taux, reserves: (n.reserves || []).length,
             verdict: (document.getElementById('genai-verdict') || {}).innerText || '' };
  });
  dit(rendu.taux === 100, 'le taux remonte au socle', rendu.taux + ' %');
  dit(rendu.reserves === 0, 'et la réserve du profil disparaît');
  dit(/NON génératif/.test(rendu.verdict) && /qualification/.test(rendu.verdict),
      'l\'écran dit que ce n\'est pas une dispense mais une qualification');

  console.log('\n══ Erreurs de page ══');
  dit(err.length === 0, 'aucune erreur JavaScript', err.slice(0, 3).join(' | '));

  console.log('\nVERDICT : ' + (verdict ? 'ÉCHEC' : 'OK'));
  await nav.close();
  process.exit(verdict);
})();
