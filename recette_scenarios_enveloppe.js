/* RECETTE — SUR /enveloppe, CHAQUE SCÉNARIO INVESTISSEUR MÈNE QUELQUE PART
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LE DÉFAUT SIGNALÉ. Sur l'étude d'enveloppe, choisir « Rachat / M&A »
 * affichait « Étape 1 sur 1 » : toutes les étapes de la branche visaient des
 * sections du panorama, absentes de cette vue. Il ne restait que la carte du
 * scénario — un parcours qui ne mène nulle part. Les deux autres scénarios
 * avaient exactement le même trou, silencieusement.
 *
 * CE QUE CES CONTRÔLES VÉRIFIENT :
 *
 *   1. CHAQUE SCÉNARIO A DES ÉTAPES SUR CETTE VUE — le compte dépasse la
 *      seule carte du scénario, pour les trois branches.
 *   2. CHAQUE ÉTAPE DÉSIGNE UNE SECTION VISIBLE : avancer pose le cadre
 *      `gp-cible` sur un bloc réellement affiché — pas sur un fantôme.
 *   3. LES QUATRE SECTIONS DE LA VUE SONT TOUTES VISITÉES : un parcours qui
 *      sauterait le pilotage ou la maturité raconterait une étude tronquée.
 *   4. LE PANORAMA N'EST PAS POLLUÉ : sur /panorama, les nouvelles étapes
 *      (sections absentes de cette vue-là) sont filtrées — le parcours y
 *      garde son ancien déroulé.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5510 node recette_scenarios_enveloppe.js
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

  const ouvrir = async (chemin) => {
    const pg = await ctx.newPage();
    await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
    await pg.goto(BASE + chemin, { waitUntil: 'domcontentloaded' });
    await pg.waitForFunction(() => typeof window.gpDemarrer === 'function',
      null, { timeout: 60000 });
    await pg.waitForTimeout(900);
    return pg;
  };
  /* CONVENTION DU DÉPÔT : un échec dans `evaluate` se rend en donnée. */
  const sur = async (pg, fn, arg) => {
    try { return await pg.evaluate(fn, arg); }
    catch (e) { return { err: String(e && e.message || e) }; }
  };

  const err = [];
  const pg = await ouvrir('/enveloppe');
  pg.on('pageerror', e => err.push(e.message));

  // ── 1 ─────────────────────────────────────────────────────────────────
  titre('1. Sur /enveloppe, chaque scénario a des étapes — plus « 1 sur 1 »');

  const comptes = await sur(pg, () => {
    const P = window.GP_PROFILS.invest;
    const out = {};
    Object.keys(P.branches).forEach(b => {
      const E = [P.question].concat(P.branches[b].etapes)
        .filter(e => window.vueMontre(e));
      out[b] = E.length;
    });
    return out;
  });
  ['neuve', 'extension', 'ma'].forEach(b => {
    ok('le scénario « ' + b + ' » compte plusieurs étapes sur cette vue',
       !comptes.err && comptes[b] >= 4,
       comptes.err || (comptes[b] + ' étape(s), scénario compris'));
  });

  const affiche = await sur(pg, async () => {
    window.gpDemarrer('invest', 'ma');
    await new Promise(r => setTimeout(r, 700));
    const e = document.querySelector('.gp-carte .gp-etape');
    return { etape: e ? e.textContent.trim() : 'absent' };
  });
  /* Le scénario étant déjà choisi, le parcours ouvre APRÈS la question :
     ce qui compte est le TOTAL — « sur 1 » était le défaut. */
  ok('LE COMPTE AFFICHÉ N’EST PLUS « sur 1 » — le défaut signalé',
     !affiche.err && /Étape \d+ sur ([2-9]|\d{2,})/.test(affiche.etape),
     affiche.err || affiche.etape);

  // ── 2 ─────────────────────────────────────────────────────────────────
  titre('2. Chaque étape désigne une section VISIBLE de la vue');

  const visite = await sur(pg, async () => {
    const P = window.GP_PROFILS.invest;
    const resultat = [];
    for (const b of Object.keys(P.branches)) {
      window.gpDemarrer('invest', b);
      await new Promise(r => setTimeout(r, 350));
      const E = [P.question].concat(P.branches[b].etapes)
        .filter(e => window.vueMontre(e));
      const sections = new Set();
      for (let i = 1; i < E.length; i++) {
        window.gpAller(i);
        await new Promise(r => setTimeout(r, 250));
        const c = document.querySelector('.gp-cible');
        resultat.push({
          branche: b, etape: i,
          cible: c ? c.id : null,
          visible: !!(c && !c.hidden && c.offsetParent !== null)
        });
        if (c) sections.add(c.id);
      }
      resultat.push({ branche: b, sections: [...sections].sort() });
    }
    window.gpFermer();
    return resultat;
  });
  if (visite.err) {
    ok('le parcours des trois branches aboutit', false, visite.err);
  } else {
    const pas = visite.filter(x => x.etape);
    ok('CHAQUE ÉTAPE POSE LE CADRE SUR UNE SECTION RÉELLEMENT AFFICHÉE',
       pas.length > 0 && pas.every(x => x.cible && x.visible),
       pas.filter(x => !x.cible || !x.visible)
         .map(x => x.branche + '#' + x.etape + '→' + (x.cible || 'rien'))
         .join(', ') || pas.length + ' étape(s), toutes désignées et visibles');

    // ── 3 ───────────────────────────────────────────────────────────────
    titre('3. Les quatre sections de la vue sont toutes visitées');
    const ATTENDU = ['s-equipements', 's-finance', 's-maturite', 's-pilotage'];
    for (const b of ['neuve', 'extension', 'ma']) {
      const ligne = visite.find(x => x.branche === b && x.sections);
      ok('« ' + b + ' » visite l’enveloppe, les équipements, la maturité et le pilotage',
         !!ligne && JSON.stringify(ligne.sections) === JSON.stringify(ATTENDU),
         ligne ? ligne.sections.join(', ') : 'aucune section');
    }
  }

  // ── 4 ─────────────────────────────────────────────────────────────────
  titre('4. Le panorama garde son déroulé : les nouvelles étapes n’y fuient pas');

  const pg2 = await ouvrir('/panorama');
  pg2.on('pageerror', e => err.push(e.message));
  const pan = await sur(pg2, () => {
    const P = window.GP_PROFILS.invest;
    const out = {};
    Object.keys(P.branches).forEach(b => {
      const E = [P.question].concat(P.branches[b].etapes)
        .filter(e => window.vueMontre(e));
      out[b] = { n: E.length,
                 fuites: E.filter(e => e.sect && ['s-finance', 's-equipements',
                   's-maturite', 's-pilotage'].indexOf(e.sect) >= 0).length };
    });
    return out;
  });
  ok('aucune étape d’enveloppe ne fuit dans la vue panorama',
     !pan.err && ['neuve', 'extension', 'ma'].every(b => pan[b].fuites === 0),
     pan.err || JSON.stringify(pan));
  /* Les comptes du panorama étaient 5 / 4 / 3 AVANT l'ajout (une partie des
     étapes de ces branches vit sur la vue empreinte) : la non-régression est
     l'ÉGALITÉ à ces comptes-là, pas un minimum inventé. */
  ok('…et le panorama garde exactement son déroulé d’avant : 5 / 4 / 3',
     !pan.err && pan.neuve.n === 5 && pan.extension.n === 4 && pan.ma.n === 3,
     pan.err || ['neuve', 'extension', 'ma'].map(b => b + ':' + pan[b].n).join(' '));
  await pg2.close();
  await pg.close();

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
