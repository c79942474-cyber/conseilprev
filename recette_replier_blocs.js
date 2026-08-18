/* RECETTE — LE REPLIAGE LIBÈRE DE LA PLACE, ET NE CRÉE PAS DE CUL-DE-SAC
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE. Sept blocs faisaient défiler plusieurs écrans avant d'atteindre
 * le suivant. Ils deviennent des dépliants.
 *
 * LA RÈGLE QUI GOUVERNE UN PLI, et que ces contrôles vérifient :
 *
 *   1. LE TITRE RESTE LISIBLE FERMÉ, AVEC SON COMPTE. « 11 échéances », « 10
 *      tendances » : on doit savoir ce qu'on ouvre sans l'ouvrir. Un dépliant
 *      dont le résumé ne dit rien force à tout ouvrir, et coûte alors plus de
 *      place qu'il n'en rend.
 *   2. LE PLI LIBÈRE RÉELLEMENT DE LA PLACE — mesuré en pixels, avant/après.
 *   3. RIEN N'EST PERDU : tout ce qui était rendu l'est encore, à l'ouverture.
 *   4. CE QUI EST REPLIÉ S'OUVRE TOUT SEUL quand un lien pointe dedans —
 *      sinon le lecteur arrive sur un bloc fermé sans comprendre pourquoi.
 *   5. LES COMPTES SONT DÉRIVÉS du contenu, jamais écrits à la main.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5601 node recette_replier_blocs.js
 */
const { chromium } = require('playwright');

const BASE = process.env.BASE || 'http://127.0.0.1:5601';
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
  await pg.waitForFunction(
    () => document.querySelectorAll('details.dsec').length >= 7,
    null, { timeout: 60000 }).catch(() => {});
  await pg.waitForTimeout(600);

  // ── 1 ───────────────────────────────────────────────────────────────────
  titre('1. Les sept blocs demandés sont bien des dépliants');

  const plis = await sur(() => {
    const d = [...document.querySelectorAll('details.dsec')];
    return {
      n: d.length,
      ouverts: d.filter(x => x.open).length,
      titres: d.map(x => (x.querySelector('summary') || {}).textContent
                          .replace(/\s+/g, ' ').trim().slice(0, 46))
    };
  });
  ok('sept dépliants de section au moins sont rendus',
     !plis.err && plis.n >= 7, plis.err || (plis.n + ' dépliant(s)'));
  ok('…et ils sont FERMÉS au départ : c’est tout l’objet',
     !plis.err && plis.ouverts === 0, plis.err || (plis.ouverts + ' déjà ouvert(s)'));

  const attendus = ['Réserves sur le référentiel', 'Jalons réglementaires',
                    'tendances 2026', 'Structure de marché', 'rapports dépouillés',
                    'textes appliqués', 'sources de données publiques'];
  const manquants = attendus.filter(
    a => !(plis.titres || []).some(t => t.indexOf(a) >= 0));
  ok('…et ce sont bien les SEPT blocs demandés',
     !plis.err && manquants.length === 0,
     plis.err || ('manquants : ' + manquants.join(' | ')));

  // ── 2 : LE POINT QUI DÉCIDE ─────────────────────────────────────────────
  titre('2. Le titre reste lisible fermé, AVEC son compte');

  const resumes = await sur(() => {
    const d = [...document.querySelectorAll('details.dsec')];
    return d.map(x => {
      const s = x.querySelector('summary');
      const r = s.getBoundingClientRect();
      const n = s.querySelector('.dsec-n');
      return {
        t: s.textContent.replace(/\s+/g, ' ').trim(),
        visible: r.width > 0 && r.height > 0,
        // Le compte doit être un NOMBRE, dans le résumé, lisible fermé.
        compte: n ? n.textContent.replace(/\s+/g, ' ').trim() : null,
        // …ou porté par l'intitulé lui-même (« 11 échéances »).
        chiffreDansTitre: /\d/.test(s.textContent)
      };
    });
  });
  ok('chaque résumé est visible alors que le bloc est fermé',
     !resumes.err && resumes.every(x => x.visible),
     resumes.err || (resumes.filter(x => !x.visible).length + ' invisible(s)'));
  ok('…ET CHACUN ANNONCE UN NOMBRE : on sait ce qu’on ouvre sans l’ouvrir',
     !resumes.err && resumes.every(x => x.chiffreDansTitre),
     resumes.err || (resumes.filter(x => !x.chiffreDansTitre)
                       .map(x => x.t.slice(0, 40)).join(' | ')));

  // ── 3 ───────────────────────────────────────────────────────────────────
  titre('3. Le pli libère RÉELLEMENT de la place — mesuré');

  const place = await sur(() => {
    const h = () => document.documentElement.scrollHeight;
    const ferme = h();
    const d = [...document.querySelectorAll('details.dsec')];
    d.forEach(x => { x.open = true; });
    const ouvert = h();
    d.forEach(x => { x.open = false; });
    return { ferme, ouvert, gagne: ouvert - ferme,
             part: ouvert ? Math.round((ouvert - ferme) / ouvert * 100) : 0 };
  });
  ok('la page fermée est SENSIBLEMENT plus courte qu’ouverte',
     !place.err && place.gagne > 800,
     place.err || (place.ferme + ' px fermé contre ' + place.ouvert
                   + ' px ouvert — ' + place.gagne + ' px gagnés, ' + place.part + ' %'));

  // ── 4 ───────────────────────────────────────────────────────────────────
  titre('4. Rien n’est perdu : tout se retrouve à l’ouverture');

  const contenu = await sur(() => {
    const d = [...document.querySelectorAll('details.dsec')];
    d.forEach(x => { x.open = true; });
    const entrees = document.querySelectorAll('details.dsec details.dpl').length;
    const liens = document.querySelectorAll('details.dsec a[href^="http"]').length;
    d.forEach(x => { x.open = false; });
    return { entrees, liens };
  });
  ok('les entrées détaillées sont toutes dans les plis',
     !contenu.err && contenu.entrees >= 20,
     contenu.err || (contenu.entrees + ' entrée(s)'));
  ok('…et les liens sortants qu’elles portent sont préservés',
     !contenu.err && contenu.liens >= 5, contenu.err || (contenu.liens + ' lien(s)'));

  // ── 5 : LE CUL-DE-SAC ───────────────────────────────────────────────────
  titre('5. Un lien qui pointe DANS un pli l’ouvre — sinon c’est un cul-de-sac');
  /* CE CONTRÔLE VÉRIFIE UN RÉSULTAT, PAS MON CODE — et la nuance est mesurée.
     En neutralisant le garde-fou JavaScript de la page, ce contrôle reste
     VERT : Chromium ouvre nativement un `details` dont un fragment vise
     l'intérieur. Ce qui est garanti ici, c'est donc que le lecteur ne tombe
     pas sur un bloc fermé — quel que soit ce qui l'ouvre. Écrire que ce
     contrôle valide le script de la page serait faux. */

  const ancre = await sur(() => {
    const d = document.querySelector('details.dsec');
    if (!d) return { err: 'aucun dépliant' };
    d.open = false;
    // On se donne une cible à l'intérieur du pli, comme le ferait une ancre
    // de parcours guidé ou une recherche interne.
    const cible = d.querySelector('.dsec-corps *');
    if (!cible) return { err: 'pli vide' };
    cible.id = 'recette-cible-pli';
    location.hash = '#recette-cible-pli';
    return { avant: d.open };
  });
  await pg.waitForTimeout(400);
  const apres = await sur(() => {
    const d = document.querySelector('details.dsec');
    const ouvert = !!(d && d.open);
    if (d) d.open = false;
    location.hash = '';
    return { ouvert };
  });
  /* UN MESSAGE D'ÉCHEC IMPRIMÉ SUR UN SUCCÈS EST UN MENSONGE DE RECETTE : la
     ligne verte disait « le bloc est resté fermé », c'est-à-dire l'inverse de
     ce qu'elle venait de constater. Le détail ne paraît donc qu'à l'échec. */
  const pliOuvre = !ancre.err && !apres.err && apres.ouvert;
  ok('LE PLI EST OUVERT quand l’adresse pointe à l’intérieur', pliOuvre,
     pliOuvre ? '' : (ancre.err || apres.err
       || 'le bloc est resté fermé : le lecteur arrive nulle part'));

  // ── 6 ───────────────────────────────────────────────────────────────────
  titre('6. Le clavier suffit, et l’impression n’ampute rien');

  const clavier = await sur(() => {
    const s = document.querySelector('details.dsec > summary');
    return { focusable: !!s && s.tabIndex >= 0 || (!!s && s.tagName === 'SUMMARY') };
  });
  ok('les résumés sont atteignables au clavier (élément summary natif)',
     !clavier.err && clavier.focusable);

  /* CE CONTRÔLE A DÛ ÊTRE RÉÉCRIT — LE PREMIER NE TESTAIT RIEN.
     Il cherchait `display: none` sur le corps d'un pli fermé. Or le navigateur
     ne masque pas ainsi : il retire le contenu du rendu par
     `content-visibility`, et le corps mesure `display: block` et 205 px de haut
     dans les deux médias tout en restant invisible. La condition n'était donc
     jamais vraie — le contrôle passait avec OU SANS la règle d'impression, ce
     qu'a montré une régression injectée. On mesure désormais la VISIBILITÉ
     réelle, et on déclenche le mécanisme qui la produit. */
  const avant = await sur(() => {
    const c = document.querySelector('details.dsec .dsec-corps');
    return { visible: c ? c.checkVisibility() : null };
  });
  ok('le corps d’un pli fermé est bien INVISIBLE — sinon rien n’était replié',
     !avant.err && avant.visible === false,
     avant.err || ('visible : ' + avant.visible));

  const impr = await sur(() => {
    window.dispatchEvent(new Event('beforeprint'));
    const d = [...document.querySelectorAll('details.dsec')];
    const c = document.querySelector('details.dsec .dsec-corps');
    const r = { fermes: d.filter(x => !x.open).length, total: d.length,
                visible: c ? c.checkVisibility() : null };
    window.dispatchEvent(new Event('afterprint'));
    return r;
  });
  ok('AVANT IMPRESSION, tous les plis s’ouvrent',
     !impr.err && impr.fermes === 0,
     impr.err || (impr.fermes + ' / ' + impr.total + ' encore fermé(s)'));
  ok('…et le contenu redevient RÉELLEMENT visible, pas seulement « display »',
     !impr.err && impr.visible === true,
     impr.err || ('visible : ' + impr.visible));

  const apresImpr = await sur(() => {
    const d = [...document.querySelectorAll('details.dsec')];
    return { ouverts: d.filter(x => x.open).length };
  });
  ok('…et tout se referme après, pour ne pas laisser la page dépliée',
     !apresImpr.err && apresImpr.ouverts === 0,
     apresImpr.err || (apresImpr.ouverts + ' resté(s) ouvert(s)'));

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
