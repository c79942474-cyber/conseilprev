/* RECETTE — NIST SP 800-53 ET SA SURCHARGE INDUSTRIELLE, À L'ÉCRAN
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE : ajouter 800-53 et 800-82 aux normes maîtrisées, avec
 * questionnaires, taux de conformité et plan.
 *
 * CE QUE LES RÈGLES PYTHON NE PEUVENT PAS VOIR. Elles lisent les fichiers et
 * font tourner les moteurs ; elles ne savent pas si le questionnaire PEINT,
 * si répondre met le verdict à jour, ni si le plafond de la surcharge
 * s'affiche. Or c'est précisément là qu'est le sérieux de ces deux modules :
 * un axe industriel déclaré au-dessus de la famille 800-53 qu'il taille doit
 * être RAMENÉ à elle, et le dépassement SIGNALÉ. Rabattre en silence ferait
 * disparaître de l'écran le défaut qu'il faut montrer.
 *
 * LE CONTRÔLE QUI COMPTE EST DIFFÉRENTIEL. On déclare d'abord la segmentation
 * OT « prouvée » avec les familles SC et AC vides : le plafond doit tomber et
 * le dépassement s'afficher. Puis on renseigne SC et AC, et le même axe doit
 * cesser d'être signalé. Un contrôle qui ne vérifierait que le premier état
 * passerait sur un module qui signale tout, tout le temps.
 *
 * LES AUTRES CONTRÔLES : les dix-huit familles et les dix axes sont peints,
 * le socle annoncé sans appréciation du risque lève son verrou, les deux
 * déclarations arrivent dans CONF_DECL — dont le socle est EXCLU, sans quoi
 * il serait pris pour un code de famille inconnu et l'évaluation refusée —,
 * le parcours guidé existe, et les deux écrans se lisent en anglais.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = 'recette_locale_idf_0123456789abcdef';
let ko = 0, n = 0;
const ok = (t, c, d) => { n++; if (!c) ko++;
  console.log((c ? '  OK   ' : '  KO   ') + t + (d ? ' — ' + d : '')); };

const repondre = (prefixe, cle, valeur) => {
  const sel = document.querySelector('#' + prefixe + '-' + cle + ' select.q-sel');
  if (!sel) return false;
  sel.value = valeur;
  sel.dispatchEvent(new Event('change', { bubbles: true }));
  return true;
};

(async () => {
  const nav = await chromium.launch({ args: ['--no-sandbox', '--disable-blink-features=AutomationControlled'] });
  const ctx = await nav.newContext({ viewport: { width: 1500, height: 1000 }, locale: 'fr-FR',
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36' });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr', 'en-US'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e).slice(0, 180)));
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'domcontentloaded' });
  await pg.goto(BASE + '/sentinel?goto=nist53-socle', { waitUntil: 'load' });
  await pg.waitForFunction(() => {
    const b = document.getElementById('nist53-body');
    return b && !b.classList.contains('veille-loading');
  }, { timeout: 25000 }).catch(() => {});
  await pg.waitForTimeout(1200);
  await pg.addScriptTag({ content: 'window.__rep = ' + repondre.toString() + ';' });

  /* ── LE CATALOGUE ─────────────────────────────────────────────────────── */
  const a = await pg.evaluate(() => ({
    familles: document.querySelectorAll('#nist53-body .nist-cat').length,
    groupes: document.querySelectorAll('#nist53-body h2.sec-h').length,
    socles: document.querySelectorAll('#nist53-body select').length,
    reserve: (document.getElementById('nist53-reserve') || {}).textContent || '',
    commande: /commande les autres/.test(document.getElementById('nist53-body').textContent)
  }));
  ok('les dix-huit familles sont peintes', a.familles === 18, String(a.familles));
  ok('réparties en cinq groupes', a.groupes === 5, String(a.groupes));
  ok('le groupe qui commande est signalé comme tel', a.commande, '');
  ok('le millésime est dit AVANT le premier chiffre',
     /révision 4/i.test(a.reserve) && /certifie pas/i.test(a.reserve),
     a.reserve.slice(0, 74) + '…');

  /* ── LE VERROU DU SOCLE ───────────────────────────────────────────────── */
  await pg.evaluate(() => {
    const s = document.querySelector('#nist53-body select');
    s.value = 'high'; s.dispatchEvent(new Event('change', { bubbles: true }));
  });
  await pg.waitForTimeout(900);
  const v1 = await pg.evaluate(() =>
    (document.getElementById('nist53-verdict') || {}).textContent || '');
  ok('socle High sans appréciation du risque : le verrou se lève',
     /appréciation du risque \(RA\) est absente/.test(v1),
     v1.replace(/\s+/g, ' ').slice(0, 88));

  await pg.evaluate(() => window.__rep('nist53', 'RA', 'tenu'));
  await pg.waitForTimeout(900);
  const v2 = await pg.evaluate(() =>
    (document.getElementById('nist53-verdict') || {}).textContent || '');
  ok('RA renseignée : le verrou tombe, le verdict se met à jour',
     !/appréciation du risque \(RA\) est absente/.test(v2) && /renseignée/.test(v2),
     v2.replace(/\s+/g, ' ').slice(0, 72));

  /* ── LA SURCHARGE, ET SON PLAFOND ─────────────────────────────────────── */
  await pg.evaluate(() => { go('nist82-ot', null, 'NIST 800-82', 'Surcharge industrielle'); nist82Init(); });
  await pg.waitForFunction(() => {
    const b = document.getElementById('nist82-body');
    return b && !b.classList.contains('veille-loading');
  }, { timeout: 25000 }).catch(() => {});
  await pg.waitForTimeout(900);
  await pg.addScriptTag({ content: 'window.__rep = ' + repondre.toString() + ';' });
  const b = await pg.evaluate(() => ({
    axes: document.querySelectorAll('#nist82-body .nist-cat').length,
    reserve: (document.getElementById('nist82-reserve') || {}).textContent || '',
    taille: /taille/.test(document.getElementById('nist82-body').textContent)
  }));
  ok('les dix axes industriels sont peints', b.axes === 10, String(b.axes));
  ok('chaque axe dit quelles familles 800-53 il taille', b.taille, '');
  ok('la surcharge dit ce qu’elle est, et son millésime',
     /185 mesures/.test(b.reserve) && /révision 2/i.test(b.reserve),
     b.reserve.replace(/\s+/g, ' ').slice(0, 78) + '…');

  /* LE CONTRÔLE DIFFÉRENTIEL : d'abord au-dessus du socle, puis dessous. */
  await pg.evaluate(() => window.__rep('nist82', 'segmentation', 'prouve'));
  await pg.waitForTimeout(900);
  const d1 = await pg.evaluate(() =>
    (document.getElementById('nist82-verdict') || {}).textContent || '');
  ok('un axe déclaré au-dessus de son socle est SIGNALÉ, pas rabattu en silence',
     /au-dessus de son socle 800-53/.test(d1),
     d1.replace(/\s+/g, ' ').slice(0, 86));

  await pg.evaluate(() => { go('nist53-socle', null, 'NIST 800-53', 'Socle'); nist53Init(); });
  await pg.waitForTimeout(1200);
  await pg.addScriptTag({ content: 'window.__rep = ' + repondre.toString() + ';' });
  await pg.evaluate(() => { window.__rep('nist53', 'SC', 'prouve'); });
  await pg.waitForTimeout(500);
  await pg.evaluate(() => { window.__rep('nist53', 'AC', 'prouve'); });
  await pg.waitForTimeout(700);
  await pg.evaluate(() => { go('nist82-ot', null, 'NIST 800-82', 'Surcharge'); nist82Init(); });
  await pg.waitForTimeout(1400);
  const d2 = await pg.evaluate(() =>
    (document.getElementById('nist82-verdict') || {}).textContent || '');
  ok('TÉMOIN — une fois SC et AC prouvées, le même axe n’est plus signalé',
     !/Segmentation et protection de frontière[^<]*au-dessus/.test(d2)
     && !/au-dessus de son socle 800-53/.test(d2.split('Sûreté')[0] || ''),
     d2.replace(/\s+/g, ' ').slice(0, 86));

  /* ── CE QUI PART VERS LE TAUX ─────────────────────────────────────────── */
  const decl = await pg.evaluate(() => ({
    d53: window.CONF_DECL ? window.CONF_DECL.nist_800_53 : null,
    d82: window.CONF_DECL ? window.CONF_DECL.nist_800_82 : null
  }));
  ok('la déclaration 800-53 rejoint CONF_DECL',
     decl.d53 && Object.keys(decl.d53).length >= 3, JSON.stringify(decl.d53));
  ok('le socle en est EXCLU — sinon il passerait pour une famille inconnue',
     decl.d53 && !('__socle' in decl.d53), '');
  ok('la déclaration industrielle rejoint CONF_DECL',
     decl.d82 && Object.keys(decl.d82).length >= 1, JSON.stringify(decl.d82));

  /* ── LE PARCOURS, ET L’ANGLAIS ────────────────────────────────────────── */
  const p = await pg.evaluate(() => {
    const x = (typeof GUIDED_PATHS !== 'undefined' ? GUIDED_PATHS : [])
      .find(g => g.id === 'nist_800_53_82');
    return x ? { etapes: x.steps.map(s => s.id) } : null;
  });
  ok('un parcours guidé atteint les deux écrans',
     p && p.etapes.indexOf('nist53-socle') >= 0 && p.etapes.indexOf('nist82-ot') >= 0
       && p.etapes.indexOf('conf-taux') >= 0,
     p ? p.etapes.join(' → ') : 'absent');

  await pg.evaluate(() => sentSetLang('en'));
  await pg.waitForTimeout(700);
  const en = await pg.evaluate(() => ({
    h1: (document.querySelector('#p-nist82-ot .page-h') || {}).textContent || '',
    eb: (document.querySelector('#p-nist82-ot .eyebrow') || {}).textContent || '',
    fil: (document.getElementById('tb-sec') || {}).textContent || ''
  }));
  ok('l’écran industriel se lit en anglais',
     /What industry/.test(en.h1) && /Rev\. 2/.test(en.eb),
     (en.h1 + ' · ' + en.eb).slice(0, 62));
  ok('et le nom du référentiel traverse la bascule inchangé',
     /NIST 800-8/.test(en.fil), en.fil);
  await pg.evaluate(() => sentSetLang('fr'));

  ok('aucune erreur JavaScript', err.length === 0, err.join(' | '));
  await nav.close();
  console.log('\n' + (n - ko) + ' contrôles passés, ' + ko + ' en échec');
  process.exit(ko ? 1 : 0);
})().catch(e => { console.error('KO rompu : ' + e); process.exit(2); });
