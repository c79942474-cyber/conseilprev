/* RECETTE — LE REGISTRE DIT SUR QUOI IL REPOSE, ET IL LE DIT À L'ÉCRAN
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LE DÉFAUT MESURÉ. Le registre affichait ses verdicts — tant de confirmés,
 * tant de corrigés — sans jamais dire sur COMBIEN DE MAISONS il s'appuie.
 * Mesuré à l'audit d'août 2026 : 27 des 40 contrôles reposaient sur le même
 * éditeur, et 20 des 27 corrections aussi. Quarante contrôles étayés par une
 * seule maison, ce sont quarante fois la même source — et le lecteur avait
 * sous les yeux un registre qui paraissait quarante fois vérifié.
 *
 * Un contrôle vérifié par trois maisons et un contrôle vérifié par une seule
 * s'affichaient à l'identique. C'est cela qu'on corrige : pas le nombre de
 * sources, mais le fait que le lecteur puisse le connaître.
 *
 * CE QUE CES CONTRÔLES PROUVENT :
 *
 *   1. LA CONCENTRATION EST À L'ÉCRAN, avec le nom de l'éditeur dominant et
 *      sa part — et le compte affiché est celui que le serveur calcule.
 *   2. LE POINT QUI DÉCIDE — UN CONTRÔLE NON RECOUPÉ LE DIT. Il ne se
 *      présente pas comme un contrôle recoupé.
 *   3. LES CORROBORATIONS SONT AFFICHÉES, avec leur lien quand il existe.
 *   4. L'ÉCART ENTRE LES DEUX SITES DU CABINET est lisible dans le registre :
 *      c'est le seul écart qu'un client puisse constater sans nous quitter.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5510 node recette_factcheck_recoupement.js
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
    () => document.querySelectorAll('#fc-registre .fc-d').length > 0,
    null, { timeout: 60000 });
  await pg.waitForTimeout(400);

  // ── 1 ───────────────────────────────────────────────────────────────────
  titre('1. Le SERVEUR calcule la concentration, il ne l’annonce pas');

  const api = await sur(async () => {
    const r = await fetch('/api/factcheck?portee=panorama');
    const j = await r.json();
    return {
      k: j.concentration,
      n: (j.controles || []).length,
      avecRecoupement: (j.controles || []).filter(c => c.recoupement).length,
      recoupes: (j.controles || []).filter(c => c.recoupement && c.recoupement.recoupe).length,
    };
  });
  ok('l’API sert une concentration calculée sur les sources',
     !api.err && api.k && api.k.total === api.n,
     api.err || (api.k ? api.k.total + ' contrôles, dominant ' + api.k.editeur_dominant
                 + ' à ' + Math.round(api.k.part_dominant * 100) + ' %' : 'absente'));
  ok('…et CHAQUE contrôle porte son propre recoupement',
     !api.err && api.avecRecoupement === api.n,
     api.err || (api.avecRecoupement + ' / ' + api.n));

  // ── 2 ───────────────────────────────────────────────────────────────────
  titre('2. La concentration est À L’ÉCRAN, pas seulement dans le JSON');

  const vu = await sur(() => {
    const c = document.querySelector('#fc-registre .fc-conc');
    return c ? { texte: c.textContent.replace(/\s+/g, ' ').trim(),
                 tendu: c.classList.contains('tendu') } : { texte: null };
  });
  ok('le bandeau de concentration est rendu',
     !vu.err && !!vu.texte, vu.err || (vu.texte || 'absent'));
  /* LE TEXTE PEUT ÊTRE ABSENT — c'est justement le défaut qu'on éprouve.
     L'appeler sans garde tuait la recette au premier échec, et les contrôles
     suivants n'étaient jamais rendus : on ne voyait qu'un KO là où il y en
     avait quatre. Mesuré par injection. */
  const T = vu.texte || '';
  ok('…il nomme l’éditeur dominant et sa part',
     !vu.err && !!api.k && T.indexOf(api.k.editeur_dominant) >= 0
       && /\d+ %/.test(T),
     T || 'bandeau absent');
  ok('…et le compte affiché est CELUI que le serveur calcule',
     !vu.err && !!api.k
       && T.indexOf(api.k.recoupes + ' / ' + api.k.total) >= 0,
     'écran « ' + T.slice(0, 40) + '… » · serveur '
       + (api.k ? api.k.recoupes + ' / ' + api.k.total : '—'));
  /* LE SIGNAL N'EST PAS QUE LA COULEUR. Un lecteur qui ne distingue pas
     l'ambre doit lire la même chose (WCAG 1.4.1). */
  ok('quand une maison porte la moitié du registre, la PHRASE le dit',
     !vu.err && (!api.k || api.k.part_dominant < 0.5
                 || /n’est pas un recoupement/.test(T)),
     api.k ? Math.round(api.k.part_dominant * 100) + ' % pour le dominant' : '—');

  // ── 3 : LE POINT QUI DÉCIDE ─────────────────────────────────────────────
  titre('3. Un contrôle non recoupé le DIT — il ne se fait pas passer pour l’autre');

  const fiches = await sur(() => {
    const out = [];
    document.querySelectorAll('#fc-registre .fc-d').forEach(d => {
      d.open = true;
      const sujet = (d.querySelector('summary') || {}).textContent || '';
      out.push({
        sujet: sujet.replace(/\s+/g, ' ').trim().slice(0, 46),
        seul: !!d.querySelector('.fc-seul'),
        corrob: d.querySelectorAll('.fc-src a').length,
        texteSeul: ((d.querySelector('.fc-seul') || {}).textContent || '')
          .replace(/\s+/g, ' ').trim(),
      });
    });
    return out;
  });
  const seuls = (fiches || []).filter(f => f.seul);
  ok('les contrôles étayés par une seule maison portent la mention',
     Array.isArray(fiches) && seuls.length > 0,
     Array.isArray(fiches) ? seuls.length + ' / ' + fiches.length + ' fiches'
       : JSON.stringify(fiches));
  ok('…et la mention NOMME la maison, au lieu d’un avertissement vague',
     seuls.length > 0 && /une seule maison \(/.test(seuls[0].texteSeul),
     (seuls[0] || {}).texteSeul || '—');
  ok('…le compte des fiches « seule maison » concorde avec le serveur',
     !!api.k && seuls.length === api.k.total - api.k.recoupes,
     seuls.length + ' à l’écran, ' + (api.k ? api.k.total - api.k.recoupes : '—') + ' au serveur');

  // ── 4 ───────────────────────────────────────────────────────────────────
  titre('4. L’écart entre les deux sites du cabinet est au registre');

  const ecart = await sur(async () => {
    const r = await fetch('/api/factcheck?portee=panorama');
    const j = await r.json();
    const c = (j.controles || []).find(x => x.cle === 'intensite_deux_sites');
    if (!c) return { absent: true };
    return { verdict: c.verdict, constat: c.constat,
             maisons: (c.recoupement || {}).nombre,
             corrob: (c.corroborations || []).map(s => s.editeur) };
  });
  ok('le contrôle d’écart inter-sites existe',
     !ecart.err && !ecart.absent, ecart.err || (ecart.absent ? 'absent' : ecart.verdict));
  ok('…il porte LES DEUX valeurs, pour qu’on reconnaisse la sienne',
     !ecart.err && !ecart.absent
       && ecart.constat.indexOf('45') > 0 && ecart.constat.indexOf('56') > 0);
  ok('…et il dit la RAISON : millésime et périmètre, pas une erreur',
     !ecart.err && !ecart.absent && /millésime/.test(ecart.constat)
       && /n'est fausse|N'EST FAUSSE/.test(ecart.constat));
  ok('…celui-là est recoupé sur trois maisons',
     !ecart.err && !ecart.absent && ecart.maisons === 3,
     (ecart.corrob || []).join(' · '));

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
