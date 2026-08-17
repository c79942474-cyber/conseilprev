/* RECETTE — LA VÉRIFICATION ART. 50 MESURE, ELLE NE RÉCITE PAS
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LE DÉFAUT D'ORIGINE. Le registre de transparence déclarait la mention d'IA
 * du Copilote Sentinel « EN PLACE » ; la page ne la portait pas. Une case
 * cochée et un texte de registre ne se périment pas quand le code change —
 * c'est pourquoi la page porte désormais une VÉRIFICATION MESURÉE, qui relit
 * les artefacts réellement servis à chaque appel.
 *
 * CE QUE CE FICHIER PROUVE, EN CONDITIONS RÉELLES (navigateur + serveur) :
 *
 *   1. La mention d'IA est bien À L'ÉCRAN sur les deux chats — pas seulement
 *      dans le fichier : visible, avant le premier échange.
 *   2. La vue Transparence porte le panneau de mesure, la colonne « Mesuré »
 *      et le registre — et la case « Conforme » reste une case à cocher.
 *   3. LE POINT QUI DÉCIDE : la mesure est EN TEMPS RÉEL. On ampute le
 *      fichier servi de sa mention, SANS redémarrer le serveur — la mesure
 *      suivante doit tomber à non-conforme, et la contradiction avec une
 *      ligne attestée doit être nommée à l'écran.
 *   4. La réponse de l'explorateur porte le marquage lisible par machine
 *      (art. 50.2) quand une synthèse est générée — et ne le porte PAS sinon.
 *   5. Vider le registre le laisse VIDE : l'amorçage ne ressuscite plus les
 *      lignes par défaut (un registre qu'on ne peut pas vider est une
 *      brochure). Le re-amorçage reste possible, sur demande explicite.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5510 node recette_ia50_mesures.js
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE = process.env.BASE || 'http://127.0.0.1:5510';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
const ICI = __dirname;

let ko = 0;
const ok = (t, cond, detail) => {
  console.log((cond ? '  OK   ' : '  KO   ') + t + (detail ? ' — ' + detail : ''));
  if (!cond) ko++;
};
const titre = t => console.log('\n══ ' + t + ' ══\n');

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({
    viewport: { width: 1500, height: 1000 },
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
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.goto(BASE + '/sentinel', { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof window.ia50Load === 'function',
    null, { timeout: 60000 });
  await pg.waitForTimeout(900);

  /* CONVENTION DU DÉPÔT : un échec dans `evaluate` se rend en donnée. */
  const sur = async (fn, arg) => {
    try { return await pg.evaluate(fn, arg); }
    catch (e) { return { err: String(e && e.message || e) }; }
  };

  // ── 1 ─────────────────────────────────────────────────────────────────
  titre('1. La mention d’IA est à l’écran, sur les deux chats, avant tout échange');

  const mention = await sur(() => {
    const s = document.querySelector('.cpc-ia-mention');
    return { la: !!s, texte: s ? s.textContent.trim() : '',
             lien: s ? !!s.querySelector('a[href*="eur-lex"]') : false };
  });
  ok('le panneau du Copilote Sentinel porte la mention, AVANT le premier échange',
     !mention.err && mention.la && /interagissez avec une IA/.test(mention.texte),
     mention.err || mention.texte.slice(0, 80));
  ok('…avec le lien vers le texte officiel (art. 50)',
     !mention.err && mention.lien, 'eur-lex présent : ' + mention.lien);

  const pubMention = await sur(async () => {
    const r = await fetch('/index.html', { credentials: 'same-origin' });
    const t = await r.text();
    return { statut: r.status, porte: /interagissez avec une IA/.test(t) };
  });
  ok('le chat du site public la porte aussi — même formulation',
     !pubMention.err && pubMention.porte,
     pubMention.err || ('HTTP ' + pubMention.statut));

  // ── 2 ─────────────────────────────────────────────────────────────────
  titre('2. La vue Transparence : mesure d’un côté, attestation de l’autre');

  await sur(() => { window.go('ia50', null, 'ADMINISTRATION', 'Transparence'); });
  await pg.waitForFunction(() => {
    const z = document.getElementById('ia50-mesures');
    return z && !/Mesure en cours/.test(z.textContent);
  }, null, { timeout: 30000 });
  await pg.waitForTimeout(600);

  const vue = await sur(() => {
    const z = document.getElementById('ia50-mesures');
    const lignes = z ? z.textContent : '';
    const tbl = document.getElementById('ia50-liste');
    const entetes = tbl ? [...tbl.querySelectorAll('th')].map(x => x.textContent.trim()) : [];
    return {
      mesures: (lignes.match(/mesuré conforme/g) || []).length,
      partiel: /mesuré en partie/.test(lignes),
      horodate: /Mesuré le \d{4}-\d{2}-\d{2}/.test(lignes),
      colonnes: entetes,
      cases: tbl ? tbl.querySelectorAll('input[type="checkbox"]').length : 0
    };
  });
  ok('le panneau rend des mesures VERTES PARCE QUE MESURÉES — au moins quatre',
     !vue.err && vue.mesures >= 4, vue.err || (vue.mesures + ' mesure(s) conforme(s)'));
  ok('…et l’examen humain de l’art. 50.4 reste « en partie — attestation », jamais vert entier',
     !vue.err && vue.partiel === true);
  ok('…et chaque mesure est horodatée', !vue.err && vue.horodate);
  ok('le tableau du registre gagne la colonne « Mesuré », entre l’état et l’attestation',
     !vue.err && vue.colonnes.indexOf('Mesuré') >= 0
       && vue.colonnes.indexOf('Conforme') > vue.colonnes.indexOf('Mesuré'),
     (vue.colonnes || []).join(' · '));
  ok('…et la case « Conforme » reste une case à cocher — la mesure ne l’a pas remplacée',
     !vue.err && vue.cases >= 5, vue.err || (vue.cases + ' case(s)'));

  // ── 3 : LE POINT QUI DÉCIDE ───────────────────────────────────────────
  titre('3. LE POINT QUI DÉCIDE : la mesure relit le fichier SERVI, à chaque appel');

  /* On attèste d'abord la ligne du Copilote — pour que la contradiction ait
     une attestation à contredire. */
  const idSentinel = await sur(async () => {
    const j = await (await fetch('/api/ia50/usages', { credentials: 'same-origin' })).json();
    const l = (j.usages || []).find(u => /Copilote|chat plateforme/.test(u.systeme));
    if (!l) return { err: 'ligne du Copilote introuvable' };
    await fetch('/api/ia50/usages', { method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: l.id, conforme: true }) });
    return { id: l.id };
  });
  ok('la ligne du Copilote est attestée conforme (mise en scène du conflit)',
     !idSentinel.err, idSentinel.err || ('ligne ' + idSentinel.id));

  /* L'INJECTION : on ampute le fichier SERVI, serveur en marche. */
  const F = path.join(ICI, 'sentinel.html');
  const original = fs.readFileSync(F, 'utf-8');
  fs.writeFileSync(F, original.replace(/interagissez avec une IA/g,
                                       'interagissez avec un service'));
  try {
    const apres = await sur(async () => {
      const v = await (await fetch('/api/ia50/verification',
        { credentials: 'same-origin', cache: 'no-store' })).json();
      const m = (v.mesures || []).find(x => x.cle === 'chat_sentinel');
      return { statut: m && m.statut, preuve: m && m.preuve,
               contradictions: (v.contradictions || []).length,
               nomme: (v.contradictions || []).some(c => /Copilote|chat/.test(c.systeme || '')) };
    });
    ok('LA MENTION RETIRÉE DU FICHIER, LA MESURE TOMBE — sans redémarrage',
       !apres.err && apres.statut === 'non-conforme',
       apres.err || (apres.statut + ' — ' + String(apres.preuve).slice(0, 80)));
    ok('…ET LA CONTRADICTION EST NOMMÉE : attesté conforme, mesuré non conforme',
       !apres.err && apres.contradictions >= 1 && apres.nomme,
       apres.err || (apres.contradictions + ' contradiction(s)'));

    const ecran = await sur(async () => {
      await window.ia50Verifier();
      await new Promise(r => setTimeout(r, 400));
      const z = document.getElementById('ia50-mesures');
      return { texte: z ? z.textContent : '' };
    });
    ok('…et l’écran l’affiche en tête, en toutes lettres',
       !ecran.err && /contradiction/.test(ecran.texte)
         && /MESURÉ NON CONFORME/.test(ecran.texte),
       ecran.err || ecran.texte.slice(0, 100));
  } finally {
    fs.writeFileSync(F, original);
  }
  const retabli = await sur(async () => {
    const v = await (await fetch('/api/ia50/verification',
      { credentials: 'same-origin', cache: 'no-store' })).json();
    const m = (v.mesures || []).find(x => x.cle === 'chat_sentinel');
    return { statut: m && m.statut };
  });
  ok('le fichier rétabli, la mesure revient au vert — même vivacité dans les deux sens',
     !retabli.err && retabli.statut === 'conforme', retabli.err || retabli.statut);

  /* On décoche l'attestation posée pour la mise en scène. */
  await sur(async (id) => {
    await fetch('/api/ia50/usages', { method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: id, conforme: false }) });
  }, idSentinel.id);

  // ── 4 ─────────────────────────────────────────────────────────────────
  titre('4. Le marquage lisible par machine voyage avec la synthèse (art. 50.2)');

  /* La base de connaissance est fermée par clé (X-RAG-Key) : la recette la
     fournit, comme le fait la page. Sans clé le serveur répond 503 et rien
     ne serait éprouvé. */
  const expl = await sur(async (cle) => {
    const r = await fetch('/api/sentinel/explorer', {
      method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-RAG-Key': cle },
      body: JSON.stringify({ question: 'obligations de transparence', top_k: 3,
                             synthese: false })
    });
    const j = await r.json();
    return { statut: r.status, ok: j.ok, synthese: j.synthese,
             marque: 'marquage' in j, ia: 'ia_generated' in j };
  }, process.env.RAG_KEY || 'recette_rag_0123456789abcdef_0123456789');
  ok('SANS synthèse générée, la réponse ne porte AUCUN marquage — un marquage '
     + 'apposé partout ne signale plus rien',
     !expl.err && expl.ok === true && !expl.synthese && !expl.marque && !expl.ia,
     expl.err || ('HTTP ' + expl.statut + ', marquage=' + expl.marque));

  // ── 5 ─────────────────────────────────────────────────────────────────
  titre('5. Un registre qu’on vide reste vide — l’amorçage ne ressuscite plus');

  const vidage = await sur(async () => {
    const j = await (await fetch('/api/ia50/usages', { credentials: 'same-origin' })).json();
    for (const u of (j.usages || [])) {
      await fetch('/api/ia50/usages/' + u.id, { method: 'DELETE', credentials: 'same-origin' });
    }
    const j2 = await (await fetch('/api/ia50/usages', { credentials: 'same-origin' })).json();
    return { avant: (j.usages || []).length, apres: (j2.usages || []).length };
  });
  ok('TOUTES LES LIGNES SUPPRIMÉES, LE REGISTRE RESTE VIDE',
     !vidage.err && vidage.avant >= 5 && vidage.apres === 0,
     vidage.err || (vidage.avant + ' → ' + vidage.apres + ' ligne(s)'));

  const reset = await sur(async () => {
    await fetch('/api/ia50/reset', { method: 'POST', credentials: 'same-origin' });
    const j = await (await fetch('/api/ia50/usages', { credentials: 'same-origin' })).json();
    return { n: (j.usages || []).length };
  });
  ok('…et le re-amorçage reste possible — sur demande explicite seulement',
     !reset.err && reset.n >= 5, reset.err || (reset.n + ' ligne(s) restaurée(s)'));

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
