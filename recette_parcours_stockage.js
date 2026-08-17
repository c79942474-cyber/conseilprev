/* RECETTE — UN PARCOURS ENREGISTRÉ RANGE LE TRAVAIL, PAS LA PLACE
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * CE QUE CE FICHIER PROTÈGE. Enregistrer un parcours est facile ; enregistrer
 * ce qui le rend utile l'est moins. Un parcours qui ne retiendrait que son
 * rang se rouvrirait à l'étape 6 sur un formulaire revenu à 100 MW et trois
 * pays par défaut : le lecteur relirait des chiffres qui ne sont plus les
 * siens, et RIEN À L'ÉCRAN NE LE LUI DIRAIT. C'est le défaut que ces contrôles
 * rendent impossible à réintroduire en silence.
 *
 *   1. LE POINT QUI DÉCIDE — LES HYPOTHÈSES PARTENT AVEC LE RANG. On modifie
 *      le formulaire, on enregistre, on remet la page à neuf, on reprend : les
 *      valeurs doivent être REVENUES, pas seulement l'étape.
 *   2. LES CHAMPS SONT LUS SUR LA PAGE. Le relevé est comparé au formulaire
 *      réel : une liste écrite dans le code aurait cessé d'être vraie au
 *      premier champ ajouté.
 *   3. LES PAYS COMPTENT. Ce sont des boutons à bascule et non des champs ;
 *      les oublier rouvrirait l'étude sur une autre comparaison.
 *   4. CE QUI NE PEUT PAS ÊTRE REPRIS SE DIT. Une hypothèse sans champ sur la
 *      vue courante doit être annoncée, pas avalée.
 *   5. LE SERVEUR REFUSE PLUTÔT QUE DE TRONQUER, et ne sert jamais l'étude
 *      d'un autre client.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5510 node recette_parcours_stockage.js
 */
const { chromium } = require('playwright');

const BASE = process.env.BASE || 'http://127.0.0.1:5510';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';

let ko = 0;
const ok = (t, cond, detail) => {
  console.log((cond ? '  OK   ' : '  KO   ') + t + (detail ? ' — ' + detail : ''));
  if (!cond) ko++;
};
const titre = t => console.log('\n══ ' + t + ' ══\n');

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({
    viewport: { width: 1400, height: 1000 },
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
      + '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    locale: 'fr-FR'
  });
  /* SANS CE MASQUE, LE SERVEUR BLOQUE L'ADRESSE POUR 1800 s. */
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });

  const ouvrir = async () => {
    const pg = await ctx.newPage();
    await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
    await pg.goto(BASE + '/enveloppe', { waitUntil: 'domcontentloaded' });
    await pg.waitForFunction(
      () => document.querySelectorAll('#fin-pays button[data-p]').length > 0
            && typeof window.gpHypotheses === 'function',
      null, { timeout: 60000 });
    await pg.waitForTimeout(1200);
    /* Le nom du parcours passe par window.prompt : sans réponse automatique,
       la recette resterait bloquée sur une boîte de dialogue. */
    pg.on('dialog', d => d.accept(d.defaultValue() || 'recette'));
    return pg;
  };

  /* CONVENTION DU DÉPÔT : une exception levée dans `evaluate` remonte comme un
     échec d'outil et non comme le défaut trouvé. On la rend en donnée. */
  const sur = async (pg, fn, arg) => {
    try { return await pg.evaluate(fn, arg); }
    catch (e) { return { err: String(e && e.message || e) }; }
  };

  const err = [];
  const pg = await ouvrir();
  pg.on('pageerror', e => err.push(e.message));

  // ── 0 : table propre ──────────────────────────────────────────────────
  const vide = await sur(pg, async () => {
    const r = await fetch('/api/parcours', { credentials: 'same-origin' });
    const j = await r.json();
    for (const p of (j.parcours || [])) {
      await fetch('/api/parcours/' + p.id, { method: 'DELETE', credentials: 'same-origin' });
    }
    const r2 = await fetch('/api/parcours', { credentials: 'same-origin' });
    return await r2.json();
  });
  ok('le magasin de parcours répond, et part vide',
     !vide.err && vide.ok === true && (vide.parcours || []).length === 0,
     vide.err || ((vide.parcours || []).length + ' restant(s)'));

  // ── 1 ─────────────────────────────────────────────────────────────────
  titre('1. Le relevé lit le formulaire RÉEL, il ne récite pas une liste');

  const releve = await sur(pg, () => {
    const f = document.getElementById('fin-form');
    const champs = f ? [...f.querySelectorAll('input[id],select[id],textarea[id]')]
      .filter(e => e.type !== 'button' && e.type !== 'submit' && !e.disabled)
      .map(e => e.id) : [];
    const h = window.gpHypotheses();
    return { surLaPage: champs.length, releves: Object.keys(h),
             inconnus: Object.keys(h).filter(k => k !== '_pays' && champs.indexOf(k) < 0),
             pays: h._pays || null };
  });
  ok('le formulaire porte des champs — sans quoi rien n’est à prouver',
     !releve.err && releve.surLaPage >= 5, releve.err || (releve.surLaPage + ' champ(s)'));
  ok('TOUTE HYPOTHÈSE RELEVÉE CORRESPOND À UN CHAMP DE LA PAGE',
     !releve.err && releve.inconnus.length === 0,
     (releve.inconnus || []).join(', ') || 'aucune hypothèse inventée');
  ok('…et les pays cochés sont relevés, eux qui ne sont pas des champs',
     !releve.err && Array.isArray(releve.pays) && releve.pays.length >= 2,
     (releve.pays || []).join(', ') || 'aucun pays');

  // ── 2 : LE POINT QUI DÉCIDE ───────────────────────────────────────────
  titre('2. LE POINT QUI DÉCIDE : la reprise rend le TRAVAIL, pas la place');

  /* On impose une valeur qui n'est PAS celle du chargement, et un jeu de pays
     différent de celui d'origine. Une reprise qui ne rendrait que le rang
     laisserait ces deux-là à leur défaut. */
  const pose = await sur(pg, async () => {
    const mw = document.getElementById('fin-mw');
    const avant = mw.value;
    mw.value = '337';
    mw.dispatchEvent(new Event('input', { bubbles: true }));
    const b = document.querySelector('#fin-pays button[data-p]:not(.on)');
    const ajoute = b ? b.getAttribute('data-p') : null;
    if (b) b.click();
    await new Promise(r => setTimeout(r, 600));
    const pays = [...document.querySelectorAll('#fin-pays button[data-p].on')]
      .map(x => x.getAttribute('data-p'));
    return { avant, mw: mw.value, ajoute, pays };
  });
  ok('on impose une puissance qui n’est pas celle du chargement',
     !pose.err && pose.mw === '337' && pose.avant !== '337',
     pose.err || (pose.avant + ' → ' + pose.mw + ' MW'));

  const enreg = await sur(pg, async () => {
    window.gpDemarrer('invest', 'neuve');
    await new Promise(r => setTimeout(r, 700));
    const etape = window.GP.i;
    const h = window.gpHypotheses();
    const r = await fetch('/api/parcours', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ nom: 'Étude 337 MW', vue: 'enveloppe',
                             profil: 'invest', branche: 'neuve',
                             etape: etape, hypotheses: h })
    });
    const j = await r.json();
    return { ok: j.ok, n: (j.parcours || []).length, etape,
             porte: Object.keys(h).length, mw: h['fin-mw'], pays: h._pays };
  });
  ok('le parcours s’enregistre, avec ses hypothèses',
     !enreg.err && enreg.ok === true && enreg.porte >= 2,
     enreg.err || (enreg.porte + ' hypothèse(s), étape ' + enreg.etape));
  ok('…et la puissance imposée EST dans ce qui part',
     !enreg.err && enreg.mw === '337', enreg.err || ('fin-mw = ' + enreg.mw));

  /* PAGE NEUVE : c'est là que tout se joue. Le formulaire revient à ses
     défauts, et seule une reprise qui restitue les hypothèses peut le
     ramener à 337 MW. */
  const pg2 = await ouvrir();
  pg2.on('pageerror', e => err.push(e.message));
  const neuf = await sur(pg2, () => ({
    mw: document.getElementById('fin-mw').value,
    pays: [...document.querySelectorAll('#fin-pays button[data-p].on')]
      .map(x => x.getAttribute('data-p'))
  }));
  ok('une page neuve revient bien à ses défauts',
     !neuf.err && neuf.mw !== '337', neuf.err || (neuf.mw + ' MW'));

  const repris = await sur(pg2, async () => {
    const r = await fetch('/api/parcours?vue=enveloppe', { credentials: 'same-origin' });
    const j = await r.json();
    const p = (j.parcours || [])[0];
    if (!p) return { err: 'aucun parcours à reprendre' };
    await window.gpReprendre(p.id);
    await new Promise(r2 => setTimeout(r2, 1400));
    return {
      mw: document.getElementById('fin-mw').value,
      pays: [...document.querySelectorAll('#fin-pays button[data-p].on')]
        .map(x => x.getAttribute('data-p')),
      etape: window.GP.i, profil: window.GP.profil, branche: window.GP.branche,
      carte: !!document.querySelector('.gp-carte.on')
    };
  });
  ok('LA PUISSANCE ENREGISTRÉE EST REVENUE — c’est le travail, pas la place',
     !repris.err && repris.mw === '337',
     repris.err || (neuf.mw + ' → ' + repris.mw + ' MW'));
  ok('…LES PAYS COMPARÉS AUSSI',
     !repris.err && JSON.stringify((repris.pays || []).slice().sort())
       === JSON.stringify((pose.pays || []).slice().sort()),
     repris.err || ('enregistrés ' + (pose.pays || []).join('+')
       + ' · repris ' + (repris.pays || []).join('+')));
  ok('…et le parcours est rouvert au bon profil et au bon scénario',
     !repris.err && repris.profil === 'invest' && repris.branche === 'neuve'
       && repris.carte === true,
     repris.err || (repris.profil + '/' + repris.branche + ' carte=' + repris.carte));

  // ── 3 ─────────────────────────────────────────────────────────────────
  titre('3. Ce qui ne peut PAS être repris se dit, au lieu d’être avalé');

  const dit = await sur(pg2, () => {
    const m = window.gpManquants({ 'fin-mw': '1', 'champ-qui-nexiste-pas': '2' });
    return { manquants: m };
  });
  ok('une hypothèse sans champ sur la vue est repérée',
     !dit.err && dit.manquants.length === 1
       && dit.manquants[0] === 'champ-qui-nexiste-pas',
     dit.err || (dit.manquants || []).join(', '));

  const avertit = await sur(pg2, async () => {
    const r = await fetch('/api/parcours', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ nom: 'Étude avec champ disparu', vue: 'enveloppe',
                             profil: 'invest', branche: 'neuve', etape: 1,
                             hypotheses: { 'fin-mw': '412', 'champ-disparu': 'x' } })
    });
    await r.json();
    const r2 = await fetch('/api/parcours?vue=enveloppe', { credentials: 'same-origin' });
    const j2 = await r2.json();
    const p = (j2.parcours || []).find(x => x.nom === 'Étude avec champ disparu');
    if (!p) return { err: 'parcours non retrouvé' };
    await window.gpReprendre(p.id);
    await new Promise(r3 => setTimeout(r3, 1300));
    const av = document.querySelector('.gp-carte .gp-repris-mal');
    return { mw: document.getElementById('fin-mw').value,
             avert: av ? av.textContent.trim() : null };
  });
  ok('…et la reprise AVERTIT à l’écran que l’étude n’est pas dans son état',
     !avertit.err && !!avertit.avert && /champ-disparu/.test(avertit.avert),
     avertit.err || (avertit.avert || 'aucun avertissement').slice(0, 110));
  ok('…tout en reprenant ce qui pouvait l’être',
     !avertit.err && avertit.mw === '412', avertit.err || (avertit.mw + ' MW'));

  // ── 4 ─────────────────────────────────────────────────────────────────
  titre('4. Le serveur refuse plutôt que de tronquer');

  const gros = await sur(pg2, async () => {
    const h = {};
    for (let i = 0; i < 900; i++) h['champ_' + i] = 'x'.repeat(40);
    const r = await fetch('/api/parcours', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ nom: 'Trop gros', vue: 'enveloppe', profil: 'invest',
                             etape: 0, hypotheses: h })
    });
    const j = await r.json();
    return { statut: r.status, ok: j.ok, erreur: j.error };
  });
  ok('UN PARCOURS TROP LOURD EST REFUSÉ, pas tronqué en silence',
     !gros.err && gros.statut === 413 && gros.ok === false,
     gros.err || ('HTTP ' + gros.statut + ' · ' + (gros.erreur || '')));

  const sansNom = await sur(pg2, async () => {
    const r = await fetch('/api/parcours', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ nom: '  ', vue: 'enveloppe', profil: 'invest', etape: 0 })
    });
    return { statut: r.status, j: await r.json() };
  });
  ok('…un parcours sans nom est refusé : on ne range pas ce qu’on ne retrouve pas',
     !sansNom.err && sansNom.statut === 400,
     sansNom.err || ('HTTP ' + sansNom.statut));

  /* MÊME NOM, MÊME VUE : on met à jour. Sans cela, enregistrer trois fois la
     même étude produisait trois entrées et le lecteur ne savait plus laquelle
     était la dernière. */
  const deuxFois = await sur(pg2, async () => {
    const av = await (await fetch('/api/parcours?vue=enveloppe',
      { credentials: 'same-origin' })).json();
    const n0 = (av.parcours || []).length;
    for (const mw of ['500', '600']) {
      await fetch('/api/parcours', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ nom: 'Même nom', vue: 'enveloppe', profil: 'invest',
                               etape: 0, hypotheses: { 'fin-mw': mw } })
      });
    }
    const ap = await (await fetch('/api/parcours?vue=enveloppe',
      { credentials: 'same-origin' })).json();
    const l = (ap.parcours || []).filter(x => x.nom === 'Même nom');
    const un = l.length === 1
      ? await (await fetch('/api/parcours/' + l[0].id,
          { credentials: 'same-origin' })).json() : null;
    return { n0, combien: l.length,
             mw: un && un.parcours ? un.parcours.hypotheses['fin-mw'] : null };
  });
  ok('enregistrer deux fois sous le même nom MET À JOUR, ne double pas',
     !deuxFois.err && deuxFois.combien === 1,
     deuxFois.err || (deuxFois.combien + ' entrée(s) « Même nom »'));
  ok('…et c’est bien la dernière valeur qui est gardée',
     !deuxFois.err && deuxFois.mw === '600', deuxFois.err || ('fin-mw = ' + deuxFois.mw));

  const fantome = await sur(pg2, async () => {
    const r = await fetch('/api/parcours/999999', { credentials: 'same-origin' });
    return { statut: r.status };
  });
  ok('un identifiant qui n’est pas le vôtre ne rend rien',
     !fantome.err && fantome.statut === 404,
     fantome.err || ('HTTP ' + fantome.statut));

  // ── 5 ─────────────────────────────────────────────────────────────────
  titre('5. La liste est à l’écran, et elle dit ce que chaque parcours porte');

  const liste = await sur(pg2, async () => {
    window.GP_LISTE = null;
    window.gpOuvrirChoix();
    await new Promise(r => setTimeout(r, 900));
    const h = document.getElementById('gp-repris');
    const l = h ? h.querySelectorAll('.gp-l-go') : [];
    return { present: !!h, n: l.length,
             texte: l.length ? l[0].textContent.replace(/\s+/g, ' ').trim() : '',
             suppr: h ? h.querySelectorAll('[data-pdel]').length : 0 };
  });
  ok('la fenêtre de choix porte la liste des parcours enregistrés',
     !liste.err && liste.present && liste.n >= 2,
     liste.err || (liste.n + ' parcours listé(s)'));
  ok('…et chaque entrée annonce son étape ET son nombre d’hypothèses',
     !liste.err && /étape \d+, \d+ hypothèse/.test(liste.texte),
     liste.err || liste.texte.slice(0, 90));
  ok('…et chacune peut être supprimée', !liste.err && liste.suppr === liste.n,
     liste.err || (liste.suppr + ' bouton(s) de suppression'));

  await pg2.close();
  await pg.close();

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
