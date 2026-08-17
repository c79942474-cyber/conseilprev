/* RECETTE — LE PIED DE LA FENÊTRE DE PARCOURS RESTE À L'ÉCRAN
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LE DÉFAUT MESURÉ. La fenêtre du parcours guidé est une carte de hauteur
 * libre ancrée par le bas. Embarquée dans Sentinel, elle est posée 320 px
 * au-dessus du bas de la bande visible — mais on l'autorisait à occuper TOUTE
 * la bande. Une carte de 470 px posée à 320 px du bas dépasse de 150 px : son
 * pied, c'est-à-dire « Précédent » et « Suivant », tombait sous l'écran.
 *
 *   Le lecteur voyait la consigne et n'avait plus AUCUN moyen d'avancer. Ce
 *   n'est pas un défaut d'esthétique : c'est le parcours qui s'arrête.
 *
 * La première étape du profil investisseur est celle qui déclenche le défaut —
 * elle porte trois scénarios, et c'est la plus haute de tout le dispositif.
 *
 * CE QUE CES CONTRÔLES VÉRIFIENT.
 *
 *   1. EMBARQUÉ, la carte tient DANS la bande annoncée par la page hôte —
 *      haut ET bas. On annonce une bande étroite, celle d'un lecteur qui n'a
 *      pas déroulé : c'est le cas où la carte déborde.
 *   2. LE PIED EST ATTEIGNABLE : « Suivant » n'est pas seulement dans la
 *      bande, il reçoit le clic (rien ne le recouvre).
 *   3. LE CORPS DÉFILE au lieu de pousser le pied dehors — la carte est plus
 *      courte que son contenu, et ce contenu reste lisible en défilant.
 *   4. SERVIE SEULE, même règle contre le viewport du navigateur.
 *   5. CE N'EST PAS UN CAS PARTICULIER : on refait la mesure sur une bande
 *      très courte, où toute la place manque.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5510 node recette_fenetre_parcours.js
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
  /* SANS CE MASQUE, LE SERVEUR BLOQUE L'ADRESSE POUR 1800 s et toutes les
     recettes suivantes échouent sur des 429 qu'on prend pour des régressions. */
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

  /* CONVENTION DU DÉPÔT : une exception levée dans `evaluate` remonte comme un
     échec d'outil et non comme le défaut trouvé. On la rend en donnée. */
  const mesurer = pg => pg.evaluate(() => {
    try {
      const c = document.getElementById('gp-carte');
      if (!c || !c.classList.contains('on')) return { err: 'carte fermée' };
      const corps = c.querySelector('.gp-corps');
      const pied = c.querySelector('.gp-pied');
      const suiv = c.querySelector('#gp-suiv');
      if (!pied) return { err: 'pas de pied' };
      const r = c.getBoundingClientRect(), rp = pied.getBoundingClientRect();
      return {
        haut: Math.round(r.top), bas: Math.round(r.bottom),
        piedBas: Math.round(rp.bottom), piedHaut: Math.round(rp.top),
        piedH: Math.round(rp.height),
        corpsVisible: corps ? Math.round(corps.clientHeight) : -1,
        corpsReel: corps ? Math.round(corps.scrollHeight) : -1,
        suivant: suiv ? suiv.textContent.trim() : null,
        options: c.querySelectorAll('.gp-opt').length
      };
    } catch (e) { return { err: String(e && e.message || e) }; }
  });

  const err = [];

  // ── 1 ───────────────────────────────────────────────────────────────────
  titre('1. EMBARQUÉ — la carte tient dans la bande que l’hôte annonce');

  const pg = await ouvrir('/panorama?embed=1');
  pg.on('pageerror', e => err.push(e.message));

  /* La bande d'un lecteur qui vient d'arriver sur le module : le cadre fait
     1 600 px, il n'en voit qu'une tranche. C'est exactement la situation de la
     capture d'écran, et c'est là que le pied sortait. */
  const BANDE = { haut: 120, bas: 620 };
  const annoncer = async b => {
    await pg.evaluate(v => window.postMessage(
      { type: 'pan-vue', haut: v.haut, bas: v.bas }, '*'), b);
    await pg.waitForTimeout(250);
  };
  await annoncer(BANDE);

  const embarque = await pg.evaluate(() =>
    document.body.classList.contains('embed'));
  ok('la page est bien en mode embarqué — sans quoi rien n’est prouvé',
     embarque === true, 'body.embed = ' + embarque);

  /* LE PROFIL LE PLUS HAUT DU DISPOSITIF : sa première étape porte trois
     scénarios. Si une carte déborde, c'est celle-là. */
  await pg.evaluate(() => window.gpDemarrer('invest'));
  await pg.waitForTimeout(700);
  await annoncer(BANDE);

  const m = await mesurer(pg);
  ok('la fenêtre est ouverte et porte bien les trois scénarios',
     !m.err && m.options >= 3, m.err || (m.options + ' scénario(s)'));
  ok('LE PIED NE PASSE PAS SOUS LA BANDE — c’est le défaut signalé',
     !m.err && m.piedBas <= BANDE.bas,
     'pied à ' + m.piedBas + ' px, bas de bande à ' + BANDE.bas + ' px'
       + (m.piedBas > BANDE.bas ? ' → ' + (m.piedBas - BANDE.bas) + ' px dehors' : ''));
  ok('…et le haut de la fenêtre ne sort pas non plus par le haut',
     !m.err && m.haut >= BANDE.haut - 2,
     'haut à ' + m.haut + ' px, haut de bande à ' + BANDE.haut + ' px');

  // ── 2 ───────────────────────────────────────────────────────────────────
  titre('2. Le pied n’est pas seulement visible : il reçoit le clic');

  const clic = await pg.evaluate(() => {
    try {
      const b = document.getElementById('gp-suiv');
      if (!b) return { err: 'pas de bouton Suivant' };
      const r = b.getBoundingClientRect();
      const x = Math.round(r.left + r.width / 2), y = Math.round(r.top + r.height / 2);
      const dessus = document.elementFromPoint(x, y);
      return {
        dans: y > 0 && y < window.innerHeight,
        atteint: !!(dessus && (dessus === b || b.contains(dessus))),
        quoi: dessus ? (dessus.id || dessus.className || dessus.tagName) : 'rien'
      };
    } catch (e) { return { err: String(e && e.message || e) }; }
  });
  ok('« Suivant » est le premier élément sous son propre centre',
     !clic.err && clic.dans && clic.atteint, clic.err || ('sous le point : ' + clic.quoi));

  // ── 3 ───────────────────────────────────────────────────────────────────
  titre('3. C’est le CORPS qui défile, pas le pied qui sort');

  ok('le contenu dépasse la place — sans quoi le contrôle 1 ne prouve rien',
     !m.err && m.corpsReel > m.corpsVisible,
     'contenu ' + m.corpsReel + ' px pour ' + m.corpsVisible + ' px visibles');
  const defile = await pg.evaluate(() => {
    try {
      const c = document.querySelector('.gp-carte .gp-corps');
      if (!c) return { err: 'pas de corps' };
      const av = c.scrollTop;
      c.scrollTop = c.scrollHeight;
      return { av: av, ap: Math.round(c.scrollTop), max: Math.round(c.scrollHeight) };
    } catch (e) { return { err: String(e && e.message || e) }; }
  });
  ok('…et il défile réellement : le bas du texte reste atteignable',
     !defile.err && defile.ap > defile.av,
     defile.err || (defile.av + ' → ' + defile.ap));
  const apresDefile = await mesurer(pg);
  ok('le pied n’a pas bougé pendant le défilement du corps',
     !apresDefile.err && Math.abs(apresDefile.piedBas - m.piedBas) <= 1,
     m.piedBas + ' → ' + apresDefile.piedBas);

  // ── 4 ───────────────────────────────────────────────────────────────────
  titre('4. Bande TRÈS courte — le cas où toute la place manque');

  const COURT = { haut: 40, bas: 300 };
  await annoncer(COURT);
  await pg.evaluate(() => window.gpDemarrer('invest'));
  await pg.waitForTimeout(600);
  await annoncer(COURT);
  const mc = await mesurer(pg);
  ok('sur 260 px de bande, le pied tient encore dans la bande',
     !mc.err && mc.piedBas <= COURT.bas,
     mc.err || ('pied à ' + mc.piedBas + ' px pour un bas de bande à ' + COURT.bas));
  ok('…et la fenêtre ne se réduit pas au point de perdre son pied',
     !mc.err && mc.piedH > 20, mc.err || ('pied de ' + mc.piedH + ' px'));
  await pg.close();

  // ── 5 ───────────────────────────────────────────────────────────────────
  titre('5. SERVIE SEULE — même règle, contre le viewport du navigateur');

  const pg2 = await ctx.newPage();
  pg2.on('pageerror', e => err.push(e.message));
  await pg2.setViewportSize({ width: 1200, height: 520 });
  await pg2.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg2.goto(BASE + '/panorama', { waitUntil: 'domcontentloaded' });
  await pg2.waitForFunction(() => typeof window.gpDemarrer === 'function',
    null, { timeout: 60000 });
  await pg2.waitForTimeout(900);
  await pg2.evaluate(() => window.gpDemarrer('invest'));
  await pg2.waitForTimeout(700);
  const m2 = await pg2.evaluate(() => {
    try {
      const c = document.getElementById('gp-carte');
      const pied = c && c.querySelector('.gp-pied');
      if (!pied) return { err: 'pas de pied' };
      const rp = pied.getBoundingClientRect(), r = c.getBoundingClientRect();
      return { piedBas: Math.round(rp.bottom), haut: Math.round(r.top),
               vue: window.innerHeight };
    } catch (e) { return { err: String(e && e.message || e) }; }
  });
  ok('sur un écran bas, le pied reste dans le viewport',
     !m2.err && m2.piedBas <= m2.vue,
     m2.err || ('pied à ' + m2.piedBas + ' px pour ' + m2.vue + ' px de haut'));
  ok('…et le haut de la fenêtre n’est pas repoussé hors de l’écran',
     !m2.err && m2.haut >= 0,
     m2.err || ('haut à ' + m2.haut + ' px'));
  await pg2.close();

  // ── 6 ───────────────────────────────────────────────────────────────────
  titre('6. LA VUE EXACTE DU SIGNALEMENT — /enveloppe, scénario Rachat / M&A');

  /* C'est la copie d'écran reçue : le bandeau porte « INVESTISSEUR · RACHAT /
     M&A », le compte dit « Étape 1 sur 1 », et la carte du scénario reste
     affichée parce qu'aucune étape de cette branche ne vise une section de
     cette vue. Autre vue, autre hauteur : on remesure ici plutôt que de
     supposer que le contrôle 1 couvre le cas. */
  const pg3 = await ouvrir('/enveloppe?embed=1');
  pg3.on('pageerror', e => err.push(e.message));
  const B3 = { haut: 90, bas: 590 };
  const annoncer3 = async () => {
    await pg3.evaluate(v => window.postMessage(
      { type: 'pan-vue', haut: v.haut, bas: v.bas }, '*'), B3);
    await pg3.waitForTimeout(250);
  };
  await annoncer3();
  await pg3.evaluate(() => window.gpDemarrer('invest', 'ma'));
  await pg3.waitForTimeout(700);
  await annoncer3();
  const m3 = await pg3.evaluate(() => {
    try {
      const c = document.getElementById('gp-carte');
      const pied = c && c.querySelector('.gp-pied');
      if (!pied) return { err: 'pas de pied' };
      const t = c.querySelector('.gp-profil'), e = c.querySelector('.gp-etape');
      return { piedBas: Math.round(pied.getBoundingClientRect().bottom),
               haut: Math.round(c.getBoundingClientRect().top),
               profil: t ? t.textContent.trim() : '', etape: e ? e.textContent.trim() : '',
               suiv: !!document.getElementById('gp-suiv') };
    } catch (e) { return { err: String(e && e.message || e) }; }
  });
  ok('on est bien sur la fenêtre signalée',
     !m3.err && /M&A/.test(m3.profil), m3.err || (m3.profil + ' — ' + m3.etape));
  ok('SON PIED EST DANS LA BANDE, et « Suivant » existe',
     !m3.err && m3.piedBas <= B3.bas && m3.suiv,
     m3.err || ('pied à ' + m3.piedBas + ' px pour un bas de bande à ' + B3.bas));
  ok('…et son haut ne sort pas par le haut',
     !m3.err && m3.haut >= B3.haut - 2, m3.err || ('haut à ' + m3.haut + ' px'));
  await pg3.close();

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
