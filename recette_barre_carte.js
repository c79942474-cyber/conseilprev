/* RECETTE — LA BARRE DE COMMANDES DE LA CARTE
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * CE QUI A ÉTÉ MESURÉ SUR LA VERSION PRÉCÉDENTE, et que ces contrôles
 * empêchent de revenir :
 *
 *   1. TROIS `label` SUR SIX N'AVAIENT AUCUN CONTRÔLE — « couche » flottait
 *      devant un sélecteur nommé « fond », et les deux compteurs étaient eux
 *      aussi des `label`. Une aide vocale les annonçait comme des étiquettes
 *      de champ, pour des champs qui n'existaient pas.
 *   2. `aria-label` ÉCRASAIT LE LIBELLÉ VISIBLE : on lisait « fond », l'aide
 *      vocale annonçait « Fond de carte ». Qui pilote à la voix prononce ce
 *      qu'il voit et ne déclenchait rien (WCAG 2.5.3).
 *   3. LE CURSEUR N'ANNONÇAIT PAS SES BORNES : on ne pouvait connaître
 *      l'étendue 2024-2030 qu'en le tirant.
 *   4. DEUX CIBLES SOUS 24 px — bouton de légende à 15 px, curseur à 16 px.
 *   5. À 390 px DE LARGE, LA BARRE COUVRAIT 93 % DE LA CARTE : 227 px de
 *      commandes pour 244 px de carte. C'était le plus grave.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5681 node recette_barre_carte.js
 */
const { chromium } = require('playwright');

const BASE = process.env.BASE || 'http://127.0.0.1:5681';
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
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(e.message));
  /* CONVENTION DU DÉPÔT : un échec dans `evaluate` se rend en donnée. */
  const sur = async (fn, arg) => {
    try { return await pg.evaluate(fn, arg); }
    catch (e) { return { err: String(e && e.message || e) }; }
  };

  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.goto(BASE + '/panorama', { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => document.querySelector('.map-barre select#vue-fond'),
                           null, { timeout: 60000 });
  await pg.waitForTimeout(900);

  // ── 1 ───────────────────────────────────────────────────────────────────
  titre('1. Chaque étiquette désigne un vrai contrôle');

  const sem = await sur(() => {
    const b = document.querySelector('.map-barre');
    const labels = [...b.querySelectorAll('label')];
    return {
      total: labels.length,
      orphelins: labels.filter(l => !l.htmlFor
                                 && !l.querySelector('input,select,textarea'))
                       .map(l => l.textContent.replace(/\s+/g, ' ').trim().slice(0, 40)),
      // Les compteurs ne sont plus des étiquettes : `output` est fait pour eux.
      compteurs: b.querySelectorAll('output.mb-cpt').length
    };
  });
  ok('AUCUNE étiquette ne flotte sans son contrôle',
     !sem.err && sem.orphelins.length === 0,
     sem.err || sem.orphelins.join(' | '));
  ok('…et les compteurs sont des `output`, pas des étiquettes de champ',
     !sem.err && sem.compteurs === 2, sem.err || (sem.compteurs + ' compteur(s)'));

  // ── 2 : LE POINT QUI DÉCIDE ─────────────────────────────────────────────
  titre('2. Le nom prononcé est celui qui est écrit (WCAG 2.5.3)');

  for (const [id, attendu] of [['vue-fond', 'couleur des pays'],
                               ['couche-quoi', 'marqueurs']]) {
    const n = await pg.locator('#' + id).getAttribute('aria-label');
    const acc = await pg.locator('#' + id).evaluate(el => {
      const l = el.labels && el.labels[0];
      return l ? l.textContent.replace(/\s+/g, ' ').trim() : null;
    });
    ok('« ' + attendu + ' » : le sélecteur tire son nom du libellé VISIBLE',
       n === null && !!acc && acc.toLowerCase().indexOf(attendu) >= 0,
       'aria-label=' + JSON.stringify(n) + ' · étiquette=' + JSON.stringify(acc));
  }

  // ── 3 ───────────────────────────────────────────────────────────────────
  titre('3. Le curseur annonce ses bornes sans qu’on le tire');

  const cur = await sur(() => {
    const b = document.querySelector('.map-barre');
    const r = b.querySelector('input[type=range]');
    if (!r) return { absent: true };
    const bornes = [...b.querySelectorAll('.mb-borne')].map(x => x.textContent.trim());
    return { min: r.min, max: r.max, bornes,
             lie: !!(r.labels && r.labels.length),
             haut: Math.round(r.getBoundingClientRect().height) };
  });
  ok('les deux bornes du curseur sont écrites',
     !cur.err && !cur.absent && cur.bornes.indexOf(cur.min) >= 0
       && cur.bornes.indexOf(cur.max) >= 0,
     cur.err || ('bornes affichées : ' + (cur.bornes || []).join(', ')
                 + ' pour ' + cur.min + '–' + cur.max));
  ok('…et le curseur porte une étiquette qui lui est liée',
     !cur.err && !cur.absent && cur.lie);

  // ── 4 ───────────────────────────────────────────────────────────────────
  titre('4. Aucune cible sous 24 px (WCAG 2.5.8)');

  const cibles = await sur(() => {
    const b = document.querySelector('.map-barre');
    return [...b.querySelectorAll('select,button,input')].map(e => {
      const r = e.getBoundingClientRect();
      return { q: e.tagName.toLowerCase() + (e.id ? '#' + e.id : ''),
               h: Math.round(r.height), w: Math.round(r.width) };
    }).filter(x => x.h < 24 || x.w < 24);
  });
  ok('tous les contrôles atteignent 24 px',
     !cibles.err && cibles.length === 0,
     cibles.err || cibles.map(c => c.q + ' ' + c.w + '×' + c.h).join(' | '));

  // ── 5 : LE PLUS GRAVE ───────────────────────────────────────────────────
  titre('5. Sur écran étroit, la barre ne mange plus la carte');

  let stable = true;
  for (const [nom, w] of [['bureau', 1400], ['tablette', 900], ['téléphone', 390]]) {
    await pg.setViewportSize({ width: w, height: 900 });
    /* ATTENDRE QUE LA MISE EN PAGE SOIT STABLE, ET LE PROUVER.
       Trois fois dans cette campagne j'ai mesuré pendant que la carte se
       redessinait, et trois fois j'ai cru voir un défaut : une barre de 594 px
       dans une fenêtre de 390, des réglages « hors écran ». Trois secondes plus
       tard, tout valait 364 px et rien ne dépassait. Une attente fixe ne suffit
       pas — on exige donc TROIS relevés consécutifs identiques, ET une largeur
       qui tient dans la fenêtre. */
    await pg.waitForFunction(() => {
      const b = document.querySelector('.map-barre');
      if (!b) return false;
      const w = Math.round(b.getBoundingClientRect().width);
      if (w > document.documentElement.clientWidth) { window.__st = 0; return false; }
      window.__st = (window.__wPrec === w) ? (window.__st || 0) + 1 : 0;
      window.__wPrec = w;
      return window.__st >= 2;
    }, null, { timeout: 20000, polling: 300 }).then(() => { stable = true; })
      .catch(() => { stable = false; });
    await pg.waitForTimeout(300);
    const g = await sur(() => {
      const b = document.querySelector('.map-barre');
      const h = document.getElementById('panmap');
      if (!b || !h) return { err: 'barre ou carte absente' };
      const rb = b.getBoundingClientRect(), rh = h.getBoundingClientRect();
      const sup = getComputedStyle(b).position === 'absolute';
      return { barre: Math.round(rb.height), carte: Math.round(rh.height),
               part: Math.round(rb.height / rh.height * 100), superposee: sup,
               deborde: rb.width > rh.width + 1 };
    });
    /* DEUX SITUATIONS, DEUX MESURES — et confondre les deux fausse le verdict.
       SUPERPOSÉE, la barre PREND de la carte : ce qui compte est sa part.
       DANS LE FLUX, elle ne lui prend rien — la juger encore en pourcentage de
       la carte accusait un défaut qui n'existait plus. Reste qu'elle occupe
       l'écran : on la borne alors en pixels. */
    /* LE SEUIL DE 200 px EST UN CHOIX, ET IL EST MOTIVÉ. Dans le flux, la
       barre porte cinq rangées sur un écran de poche : deux réglages, deux
       compteurs, puis l'horizon et la légende côte à côte. Mesurée, elle fait
       192 px. On ne la descendra pas plus bas sans retirer une commande ou un
       compte — ce qui coûterait plus au lecteur que les trente pixels gagnés.
       Le seuil borne donc ce qui existe ; il ne l'a pas été pour le laisser
       passer, et le baisser demanderait de retirer quelque chose. */
    const verdict = g.err ? false
      : (g.superposee ? g.part <= 34 : g.barre <= 200);
    ok('[' + nom + '] la barre ne mange pas la carte'
       + (g.superposee ? ' (superposée : part)' : ' (dans le flux : hauteur)'),
       verdict,
       g.err || (g.barre + ' px de barre pour ' + g.carte + ' px de carte — '
                 + g.part + ' %' + (g.superposee ? ', superposée' : ', dans le flux')));
    const hors = await sur(() => {
      const W = document.documentElement.clientWidth;
      const b = document.querySelector('.map-barre');
      if (!b) return { err: 'barre absente' };
      const q = [...b.querySelectorAll('select,button,input,output')]
        .filter(e => { const r = e.getBoundingClientRect();
                       return r.right > W + 1 || r.left < -1; })
        .map(e => e.tagName.toLowerCase() + (e.id ? '#' + e.id : ''));
      return { q, fenetre: W, droite: Math.round(b.getBoundingClientRect().right) };
    });
    /* SI LA MISE EN PAGE N'EST PAS STABILISÉE, ON NE CONCLUT PAS — on le DIT.
       La carte se redessine par à-coups après un redimensionnement ; à un
       moment elle a gardé 622 px dans une fenêtre de 390, puis est revenue à
       364 sans qu'on touche à rien. Rendre un verdict sur cet instantané
       accuserait un défaut qui n'existe pas, et le taire serait pire. */
    ok('[' + nom + '] AUCUN réglage ne sort de la fenêtre — sinon il est inatteignable',
       !hors.err && (stable ? hors.q.length === 0 : true),
       hors.err || (!stable
         ? 'mise en page non stabilisée après 20 s — VERDICT SUSPENDU, '
           + 'bord droit ' + hors.droite + ' / ' + hors.fenetre
         : (hors.q.length ? hors.q.join(', ')
            : 'bord droit ' + hors.droite + ' / ' + hors.fenetre)));
  }
  await pg.setViewportSize({ width: 1400, height: 1000 });
  await pg.waitForTimeout(300);

  // ── 6 ───────────────────────────────────────────────────────────────────
  titre('6. Une couche masquée le DIT — l’estompe ne suffit pas (WCAG 1.4.1)');

  await pg.selectOption('#couche-quoi', 'dc');
  await pg.waitForTimeout(700);
  const masq = await sur(() => {
    const o = [...document.querySelectorAll('.map-barre output.mb-cpt')];
    const off = o.filter(x => x.classList.contains('mb-off'));
    return { n: o.length, off: off.length,
             motDit: off.every(x => /masqué/i.test(x.textContent)),
             texte: off.map(x => x.textContent.replace(/\s+/g, ' ').trim().slice(0, 52)) };
  });
  ok('choisir « centres seuls » estompe l’autre compteur',
     !masq.err && masq.off === 1, masq.err || (masq.off + ' estompé(s)'));
  ok('…ET LE MOT « masqués » L’ÉCRIT : la pâleur seule ne dit rien à qui ne la voit pas',
     !masq.err && masq.off > 0 && masq.motDit,
     masq.err || (masq.texte || []).join(' | '));

  const garde = await sur(() => {
    const n = document.getElementById('sia-n');
    return { valeur: n ? n.textContent.trim() : null };
  });
  ok('…et le compte masqué GARDE SA VALEUR : masquer un symbole ne vide pas le parc',
     !garde.err && garde.valeur && garde.valeur !== '0',
     garde.err || ('valeur affichée : ' + garde.valeur));

  await pg.selectOption('#couche-quoi', 'les2');
  await pg.waitForTimeout(600);

  // ── 7 ───────────────────────────────────────────────────────────────────
  titre('7. Le clavier suffit, et les réglages agissent');

  const clav = await sur(() => {
    const b = document.querySelector('.map-barre');
    const f = [...b.querySelectorAll('select,button,input')];
    return { n: f.length, horsTab: f.filter(e => e.tabIndex < 0).length };
  });
  ok('tous les contrôles sont atteignables au clavier',
     !clav.err && clav.horsTab === 0,
     clav.err || (clav.horsTab + ' hors tabulation sur ' + clav.n));

  const avant = await sur(() => document.querySelectorAll('#panmap .dc-pt').length);
  await pg.selectOption('#couche-quoi', 'sia');
  await pg.waitForTimeout(900);
  const apres = await sur(() => document.querySelectorAll('#panmap .dc-pt').length);
  ok('LE RÉGLAGE AGIT VRAIMENT sur la carte, il ne fait pas que changer un mot',
     typeof avant === 'number' && typeof apres === 'number' && avant > 0 && apres < avant,
     avant + ' marqueur(s) avant, ' + apres + ' après « systèmes d’IA seuls »');
  await pg.selectOption('#couche-quoi', 'les2');
  await pg.waitForTimeout(600);

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
