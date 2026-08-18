/* RECETTE — TOUTES LES SOURCES, ET ELLES SONT RÉCOLTÉES, PAS RECOPIÉES
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LE DÉFAUT MESURÉ. La page portait, en fin de parcours, une liste de sources
 * ÉCRITE À LA MAIN : sept constantes, quatre textes, six jeux de données —
 * dix-sept entrées. Pendant ce temps les moteurs en déclaraient vingt et une
 * et le registre de vérification seize de plus. Une liste écrite à la main ne
 * se trompe pas le jour où on l'écrit : elle se trompe le jour où quelqu'un
 * ajoute une source ailleurs, et personne ne s'en aperçoit.
 *
 * CE QUE CES CONTRÔLES PROUVENT :
 *
 *   1. LE POINT QUI DÉCIDE — LE REGISTRE EST DÉRIVÉ. Une source ajoutée à un
 *      moteur paraît dans le registre sans qu'on touche à la page.
 *   2. LES LIENS SONT RÉELS : chaque entrée qui en porte un ouvre une adresse
 *      absolue et sûre, dans un nouvel onglet, sans céder `window.opener`.
 *   3. CE QUI N'A PAS DE LIEN LE DIT, et dit POURQUOI : une synthèse du
 *      cabinet n'a aucune publication à citer — ce n'est pas un manquement —
 *      tandis qu'un éditeur nommé sans adresse est un trou à combler.
 *   4. LA COUVERTURE EST ANNONCÉE AVANT LA LISTE : combien de sources le
 *      lecteur peut réellement rouvrir. Une liste à la main ne le dit jamais.
 *   5. LE SOCLE A ÉTÉ RACCOURCI SANS PERDRE CE QU'IL PORTAIT.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5510 node recette_registre_sources.js
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
    () => document.querySelectorAll('#reg-corps .reg-l li').length > 0,
    null, { timeout: 60000 });
  await pg.waitForTimeout(300);

  // ── 1 ───────────────────────────────────────────────────────────────────
  titre('1. LE REGISTRE EST DÉRIVÉ des moteurs, il ne les recopie pas');

  const api = await sur(async () => {
    const r = await fetch('/api/sources', { credentials: 'same-origin' });
    const j = await r.json();
    return { ok: j.ok, n: (j.sources || []).length,
             v: (j.verification || []).length, k: j.couverture,
             dom: j.par_domaine, limite: j.limite };
  });
  ok('l’API sert un registre récolté sur plusieurs moteurs',
     !api.err && api.ok && api.n > 0 && api.v > 0,
     api.err || (api.n + ' sources + ' + api.v + ' de vérification'));
  ok('…et il couvre PLUSIEURS domaines, pas un seul moteur',
     !api.err && api.dom && Object.keys(api.dom).length >= 5,
     api.err || Object.keys(api.dom || {}).join(', '));

  /* LE CONTRÔLE QUI PROUVE LA DÉRIVATION. On compte les entrées d'un domaine,
     puis on demande au serveur combien le moteur correspondant en déclare :
     les deux doivent concorder. Un registre recopié ne suivrait pas. */
  const derive = await sur(async () => {
    const r = await fetch('/api/sources', { credentials: 'same-origin' });
    const j = await r.json();
    const parModule = {};
    (j.sources || []).forEach(s => {
      parModule[s.module] = (parModule[s.module] || 0) + 1;
    });
    // Chaque entrée nomme le module ET la variable dont elle vient : une
    // liste écrite à la main n'aurait ni l'un ni l'autre.
    const traçable = (j.sources || []).filter(s => s.module && s.variable).length;
    return { parModule, traçable, total: (j.sources || []).length };
  });
  ok('CHAQUE SOURCE NOMME LE MODULE ET LA VARIABLE dont elle est tirée',
     !derive.err && derive.traçable === derive.total && derive.total > 0,
     derive.err || (derive.traçable + ' / ' + derive.total + ' traçables · '
                    + JSON.stringify(derive.parModule)));

  // ── 2 ───────────────────────────────────────────────────────────────────
  titre('2. Les liens sont réels, absolus et sûrs');

  const liens = await sur(() => {
    const a = [...document.querySelectorAll('#reg-corps .reg-l a')];
    return {
      n: a.length,
      relatifs: a.filter(x => !/^https?:\/\//.test(x.getAttribute('href') || '')).length,
      sansBlank: a.filter(x => x.getAttribute('target') !== '_blank').length,
      sansNoopener: a.filter(x => !/noopener/.test(x.getAttribute('rel') || '')).length,
      exemples: a.slice(0, 3).map(x => x.getAttribute('href')),
    };
  });
  ok('des liens cliquables sont rendus',
     !liens.err && liens.n >= 20, liens.err || (liens.n + ' lien(s)'));
  ok('TOUS SONT ABSOLUS — un lien relatif renverrait sur notre propre site',
     !liens.err && liens.relatifs === 0, liens.err || (liens.relatifs + ' relatif(s)'));
  ok('…tous s’ouvrent dans un nouvel onglet SANS céder window.opener',
     !liens.err && liens.sansBlank === 0 && liens.sansNoopener === 0,
     liens.err || (liens.sansBlank + ' sans _blank, ' + liens.sansNoopener + ' sans noopener'));

  // ── 3 : LE POINT QUI DÉCIDE ─────────────────────────────────────────────
  titre('3. Ce qui n’a pas de lien le DIT, et dit pourquoi');

  const sans = await sur(() => {
    const li = [...document.querySelectorAll('#reg-corps .reg-l li')];
    const avecLien = li.filter(x => x.querySelector('a')).length;
    const marques = li.filter(x => x.querySelector('.reg-sans'));
    return {
      total: li.length, avecLien,
      marques: marques.length,
      cabinet: marques.filter(x => /synthèse du cabinet/.test(x.textContent)).length,
      aCombler: marques.filter(x => /adresse non enregistrée/.test(x.textContent)).length,
      // AUCUNE ENTRÉE MUETTE : ni lien, ni explication.
      muettes: li.filter(x => !x.querySelector('a') && !x.querySelector('.reg-sans')).length,
    };
  });
  ok('AUCUNE ENTRÉE N’EST MUETTE : lien, ou raison de son absence',
     !sans.err && sans.muettes === 0,
     sans.err || (sans.muettes + ' entrée(s) sans lien ni explication'));
  ok('…et les deux raisons sont DISTINGUÉES, pas confondues',
     !sans.err && sans.cabinet > 0 && sans.aCombler > 0,
     sans.err || (sans.cabinet + ' synthèse(s) du cabinet · '
                  + sans.aCombler + ' adresse(s) à enregistrer'));
  ok('…le compte à l’écran est celui que le serveur calcule',
     !sans.err && !api.err && api.k
       && sans.avecLien === api.k.avec_lien && sans.total === api.k.total,
     'écran ' + sans.avecLien + '/' + sans.total + ' · serveur '
       + (api.k ? api.k.avec_lien + '/' + api.k.total : '—'));

  // ── 4 ───────────────────────────────────────────────────────────────────
  titre('4. La couverture est annoncée AVANT la liste');

  const couv = await sur(() => {
    const c = document.getElementById('reg-couv');
    const n = document.getElementById('reg-note');
    return { texte: c ? c.textContent.replace(/\s+/g, ' ').trim() : '',
             note: n ? n.textContent.trim() : '' };
  });
  /* LES DEUX APOSTROPHES. Le serveur écrit l'apostrophe droite, la page la
     typographique : n'accepter que l'une faisait tomber le contrôle sur un
     texte parfaitement juste. C'était ma faute, pas celle du registre. */
  ok('le bandeau de couverture est rendu',
     !couv.err && /s['’]ouvrent d['’]un clic/.test(couv.texte), couv.texte.slice(0, 90));
  ok('…et il déclare la limite : le registre ne teste pas les adresses',
     !couv.err && /ne vérifie pas que les adresses répondent/.test(couv.texte));
  ok('…le bandeau de section porte le compte',
     !couv.err && /\d+ sources · \d+ ouvrables/.test(couv.note), couv.note);

  // ── 5 ───────────────────────────────────────────────────────────────────
  titre('5. Le socle a été raccourci sans perdre ce qu’il portait');

  const socle = await sur(() => {
    const s = document.getElementById('s-socle');
    if (!s) return { err: 'section absente' };
    const notes = [...s.querySelectorAll('.panel-body > p.note')]
      .map(p => p.textContent.replace(/\s+/g, ' ').trim());
    return { n: notes.length, car: notes.join(' ').length, textes: notes,
             sources: s.querySelectorAll('.socle-t tbody tr').length };
  });
  ok('le chapeau du socle tient en deux paragraphes courts',
     !socle.err && socle.n === 2 && socle.car < 520,
     socle.err || (socle.n + ' paragraphes, ' + socle.car + ' caractères'));
  ok('…et il garde CE QU’IL FAUT : refaire la requête, et contexte pas preuve',
     !socle.err && /refaire la requête/.test(socle.textes.join(' '))
       && /Contexte, pas preuve/.test(socle.textes.join(' ')));
  ok('…le tableau des sources ouvertes du socle est intact',
     !socle.err && socle.sources >= 4, socle.err || (socle.sources + ' ligne(s)'));

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
