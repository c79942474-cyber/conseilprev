/* RECETTE — CLIQUER « SUIVANT » DÉPLACE QUELQUE CHOSE, OU LE DIT
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LE DÉFAUT MESURÉ. Une étape de parcours désignait toujours une SECTION
 * entière. Or six étapes du parcours « finance » se succèdent dans
 * `s-finance` : on cliquait « Suivant » six fois et le cadre bleu ne bougeait
 * pas d'un pixel. Le lecteur ne conclut pas qu'on lui parle d'autre chose dans
 * le même bloc — il conclut que le bouton est cassé. Mesuré sur les trois
 * vues, 54 enchaînements : DIX-SEPT ne déplaçaient rien, et aucun ne le disait.
 *
 * DEUX REMÈDES, ET LE SECOND EST LA GARANTIE.
 *   - Une étape peut nommer un SOUS-BLOC (`ancre`) plutôt que sa section.
 *     Douze l'ont fait, sur des identifiants qui existent déjà dans la page —
 *     aucun n'est inventé. Les immobiles tombent de dix-sept à sept.
 *   - Pour les sept qui restent, la carte DIT que le bloc ne change pas. Une
 *     page immobile après un clic se lit comme une panne ; une page immobile
 *     qui s'explique se lit comme une lecture qui continue.
 *
 * CE QUE CES CONTRÔLES PROUVENT :
 *   1. LE POINT QUI DÉCIDE — AUCUN PAS MUET. Sur les trois vues et tous les
 *      profils : soit le bloc désigné change, soit la carte l'annonce.
 *   2. LES ANCRES DÉSIGNENT DES BLOCS QUI EXISTENT, et plus fins que la
 *      section — sinon elles ne serviraient à rien.
 *   3. CHANGER DE PARCOURS REPART DE ZÉRO : la première étape du nouveau ne
 *      se croit pas « la même » que la dernière de l'ancien.
 *   4. UN PARCOURS SANS ÉTAPE SUR LA VUE reste annoncé, pas silencieux.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5510 node recette_parcours_deplacement.js
 */
const { chromium } = require('playwright');

const BASE = process.env.BASE || 'http://127.0.0.1:5510';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
const VUES = ['/panorama', '/enveloppe', '/empreinte-parc'];

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
  const err = [];
  const ouvrir = async (vue) => {
    const pg = await ctx.newPage();
    pg.on('pageerror', e => err.push(e.message));
    await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
    await pg.goto(BASE + vue, { waitUntil: 'domcontentloaded' });
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

  // ── 1 : LE POINT QUI DÉCIDE ─────────────────────────────────────────────
  titre('1. AUCUN PAS MUET — le bloc change, ou la carte dit qu’il ne change pas');

  let pas = 0, immobiles = 0, muets = [];
  for (const vue of VUES) {
    const pg = await ouvrir(vue);
    const r = await sur(pg, async () => {
      const out = [];
      const P = window.GP_PROFILS;
      for (const cle of Object.keys(P)) {
        const p = P[cle];
        const brs = p.branches ? Object.keys(p.branches) : [null];
        for (const b of brs) {
          window.gpDemarrer(cle, b);
          await new Promise(r => setTimeout(r, 200));
          const E = (p.branches
              ? (b ? [p.question].concat(p.branches[b].etapes) : [p.question])
              : p.etapes).filter(e => window.vueMontre(e));
          let prev = null;
          for (let i = 0; i < E.length; i++) {
            window.gpAller(i);
            await new Promise(r => setTimeout(r, 130));
            const c = document.querySelector('.gp-cible');
            const id = c ? c.id : null;
            const dit = !!document.querySelector('.gp-carte .gp-meme');
            if (i > 0) out.push({ p: cle + (b ? '/' + b : ''), i,
                                  id, immobile: !!id && id === prev, dit });
            prev = id;
          }
          window.gpFermer();
        }
      }
      return out;
    });
    if (r.err) { ok('la vue ' + vue + ' se parcourt', false, r.err); continue; }
    pas += r.length;
    immobiles += r.filter(x => x.immobile).length;
    muets = muets.concat(r.filter(x => x.immobile && !x.dit)
      .map(x => vue + ' ' + x.p + ' étape ' + (x.i + 1) + ' (#' + x.id + ')'));
    await pg.close();
  }
  ok('les trois vues se parcourent en entier',
     pas >= 40, pas + ' enchaînement(s) éprouvé(s)');
  ok('AUCUN PAS IMMOBILE N’EST MUET',
     muets.length === 0,
     muets.length ? muets.slice(0, 3).join(' · ')
                  : pas + ' pas, ' + immobiles + ' immobiles, tous annoncés');
  /* SANS IMMOBILE, LE CONTRÔLE PRÉCÉDENT NE PROUVE RIEN : il passerait sur un
     dispositif qui n'aurait simplement rien à annoncer. */
  ok('…et il RESTE des pas immobiles à annoncer — sinon rien n’est éprouvé',
     immobiles > 0, immobiles + ' pas immobiles');

  // ── 2 ───────────────────────────────────────────────────────────────────
  titre('2. Les ancres désignent des blocs RÉELS, et plus fins que la section');

  const pg = await ouvrir('/enveloppe');
  const ancres = await sur(pg, () => {
    const vues = new Set(), pbs = [];
    const P = window.GP_PROFILS;
    Object.keys(P).forEach(cle => {
      const p = P[cle];
      const lots = p.branches
        ? [p.question].concat(...Object.keys(p.branches).map(b => p.branches[b].etapes))
        : p.etapes;
      lots.forEach(e => {
        if (!e || !e.ancre) return;
        vues.add(e.ancre);
        const a = document.getElementById(e.ancre);
        const s = e.sect ? document.getElementById(e.sect) : null;
        if (!a) { pbs.push(e.ancre + ' n’existe pas'); return; }
        // PLUS FINE QUE SA SECTION : une ancre égale à la section ne
        // déplacerait rien, et l'ajouter n'aurait servi à rien.
        if (a === s) pbs.push(e.ancre + ' est la section elle-même');
        if (s && !s.contains(a)) pbs.push(e.ancre + ' est hors de ' + e.sect);
      });
    });
    return { n: vues.size, liste: [...vues].sort(), pbs };
  });
  ok('des ancres sont déclarées',
     !ancres.err && ancres.n >= 6, ancres.err || (ancres.n + ' ancre(s)'));
  ok('CHACUNE EXISTE, est contenue dans sa section, et est plus fine qu’elle',
     !ancres.err && ancres.pbs.length === 0,
     ancres.err || (ancres.pbs.join(' ; ') || ancres.liste.join(', ')));

  // ── 3 ───────────────────────────────────────────────────────────────────
  titre('3. Changer de parcours repart de zéro');

  const zero = await sur(pg, async () => {
    // finir un parcours sur un bloc, en ouvrir un autre qui commence par le même
    window.gpDemarrer('finance', null);
    await new Promise(r => setTimeout(r, 250));
    window.gpAller(1);
    await new Promise(r => setTimeout(r, 200));
    const avant = (document.querySelector('.gp-cible') || {}).id;
    window.gpDemarrer('faisabilite', null);
    await new Promise(r => setTimeout(r, 350));
    return { avant, apres: (document.querySelector('.gp-cible') || {}).id,
             dit: !!document.querySelector('.gp-carte .gp-meme') };
  });
  ok('LA PREMIÈRE ÉTAPE D’UN NOUVEAU PARCOURS NE SE CROIT PAS « la même »',
     !zero.err && !zero.dit,
     zero.err || ('#' + zero.avant + ' → #' + zero.apres
                  + ' · mention « même bloc » : ' + zero.dit));

  // ── 4 ───────────────────────────────────────────────────────────────────
  titre('4. Un parcours sans étape sur la vue reste ANNONCÉ');

  const vide = await sur(pg, async () => {
    /* FERMER CE QUI TRAÎNE. La section précédente laisse un parcours ouvert,
       et le miroir des listes le reflète : le rôle qu'on pose ici serait
       aussitôt réécrit par le parcours en cours. */
    if (typeof gpFermer === 'function') gpFermer();
    await new Promise(x => setTimeout(x, 200));
    const r = document.getElementById('pp-role');
    r.value = 'credit';
    r.dispatchEvent(new Event('change', { bubbles: true }));
    await new Promise(x => setTimeout(x, 350));
    const p = document.getElementById('pp-parcours');
    const opts = [...p.options].filter(o => o.value);
    window.gpDemarrer('credit', null);
    await new Promise(x => setTimeout(x, 400));
    const c = document.querySelector('.gp-carte');
    return {
      desactivees: opts.filter(o => o.disabled).length, total: opts.length,
      libelle: (opts[0] || {}).text || '',
      aide: (document.getElementById('pp-aide') || {}).textContent || '',
      carte: c ? c.textContent.replace(/\s+/g, ' ') : '',
    };
  });
  ok('le menu DÉSACTIVE le parcours et dit pourquoi',
     !vide.err && vide.desactivees === vide.total
       && /aucune étape sur cette vue/.test(vide.libelle),
     vide.err || (vide.libelle || ('aucune option — ' + vide.total + ' parcours')));
  ok('…l’aide renvoie vers la vue où il se déroule',
     !vide.err && /Panorama/.test(vide.aide));
  /* LE PIÈGE DE LA CLÉ VIDE. L'option « Parcours complet » portait la MÊME
     valeur que l'intitulé d'attente — chaîne vide — si bien que la choisir
     était indiscernable de ne rien choisir, et le clic ne faisait rien. Le
     défaut restait masqué parce qu'un profil sans scénario démarre d'office au
     choix du rôle ; il serait apparu au premier profil linéaire à deux
     parcours. */
  const cles = await sur(pg, async () => {
    const r = document.getElementById('pp-role');
    const doublons = [];
    for (const o of [...r.options]) {
      if (!o.value) continue;
      r.value = o.value; r.dispatchEvent(new Event('change', { bubbles: true }));
      await new Promise(x => setTimeout(x, 180));
      const p = document.getElementById('pp-parcours');
      const vals = [...p.options].map(x => x.value);
      const vides = vals.filter((v, i) => v === '' && i > 0);
      if (vides.length) doublons.push(o.value);
    }
    return { doublons };
  });
  ok('AUCUN PARCOURS NE PARTAGE LA VALEUR VIDE DE L’INTITULÉ D’ATTENTE',
     !cles.err && cles.doublons.length === 0,
     cles.err || (cles.doublons.length ? cles.doublons.join(', ')
                                       : 'aucune clé ambiguë'));
  ok('…et forcer son ouverture donne une carte d’explication, pas un écran mort',
     !vide.err && /ne passe pas par cette vue/.test(vide.carte),
     vide.err || vide.carte.slice(0, 70));
  await pg.close();

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
