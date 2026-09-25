/* RECETTE — LE CORPS DE SENTINEL SE TRADUIT PAR CONTENU, ET REVIENT INTACT
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * CE QUI EXISTAIT. La bascule FR/EN traduisait la COQUILLE : menu, fil
 * d'Ariane, surtitre, titre et chapeau des pages. Le corps des 118 pages et
 * tout ce que le JavaScript rend restaient en français. Mesuré sur cette
 * recette, colonne « avant » (commit 6662357) : en EN, le chapeau de la page
 * Formations, le paragraphe à lien de Mon espace, le chapeau à gras du Cadre
 * normatif, le `title` de l'audit et les cartes de formation rendues après
 * coup restent en français ; la route /sentinel.en.json répond 404.
 *
 * CE QUE CETTE RECETTE MESURE, ET QUE LES RÈGLES PYTHON NE PEUVENT PAS VOIR :
 * ce qu'il reste À L'ÉCRAN après le passage de la traduction par contenu, et
 * ce qu'il en reste après le RETOUR au français.
 *   · les entrées de i18n/sentinel/_exemple.json s'affichent en anglais ;
 *   · un paragraphe qui contient un LIEN garde son lien — même href — après
 *     traduction du texte qui l'entoure (le piège de l'accueil, payé deux
 *     fois dans ce dépôt) ;
 *   · un chapeau avec du GRAS est traduit en bloc et garde son <b> ;
 *   · un attribut `title` est traduit ;
 *   · une entrée à CHIFFRES (« Toutes (15) », « FORMATION 01 ») garde ses
 *     chiffres dans la valeur anglaise ;
 *   · ce que le JavaScript rend APRÈS COUP (les cartes de formation, peintes
 *     par go('training')) est traduit, et un nœud inséré après la bascule
 *     l'est aussi, par l'observateur ;
 *   · le retour en FR restitue l'innerHTML OCTET POUR OCTET ;
 *   · un dictionnaire injoignable (route en 500 simulée) laisse la coquille
 *     traduite, sans erreur de page.
 *
 * Usage :
 *   (cd <dossier> && PORT=9917 AUTH_MASTER_TOKEN=recette_locale_idf_0123456789abcdef nohup python app.py > log 2>&1 &)
 *   BASE=http://127.0.0.1:9917 node recette_sentinel_langue_moteur.js
 */
const fs = require('fs');
const path = require('path');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:9917';
const TOKEN = 'recette_locale_idf_0123456789abcdef';
let ko = 0, n = 0;
const ok = (t, c, d) => { n++; if (!c) ko++;
  console.log((c ? '  OK   ' : '  KO   ') + t + (d ? ' — ' + d : '')); };

/* LES ATTENDUS SONT LUS DANS LE DICTIONNAIRE D'EXEMPLE, pas recopiés : une
   valeur changée dans le fichier et pas ici ferait tomber la recette sur un
   écart qui n'existe pas dans le produit. */
const EX = JSON.parse(fs.readFileSync(
  path.join(__dirname, 'i18n', 'sentinel', '_exemple.json'), 'utf8'));
const T = EX.texte, B = EX.bloc;
const EN_FORMATIONS = T['Modules certifiants — progression calculée à partir de vos scores réels de l Audit de maturité IA par pilier.'];
const EN_ESPACE = T['Votre activité récente et les actions à traiter en priorité — pour une vue exécutive et des KPIs de pilotage, consultez le'];
const EN_TITLE = T['Un expert CONSEILPREV vous accompagne à chaque étape.'];
const EN_PROGRAMME = T['Programme détaillé'];
const EN_CADRE = Object.values(B)[0];

const RELEVE = () => {
  const q = (s) => document.querySelector(s);
  const lead = (id) => q('#p-' + id + ' .page-lead');
  const aud = q('.audit-aide a');
  return {
    langue: document.documentElement.lang,
    menu: [...document.querySelectorAll('.sb-section [data-i18n]')].map(e => e.textContent),
    formations: lead('training') && lead('training').textContent,
    espaceHtml: lead('espace') && lead('espace').innerHTML,
    espaceTexte: lead('espace') && lead('espace').firstChild && lead('espace').firstChild.nodeValue,
    espaceLien: lead('espace') && lead('espace').querySelector('a') && {
      href: lead('espace').querySelector('a').getAttribute('href'),
      onclick: lead('espace').querySelector('a').getAttribute('onclick'),
      texte: lead('espace').querySelector('a').textContent },
    cadreHtml: lead('cadre-normatif') && lead('cadre-normatif').innerHTML,
    cadreGras: lead('cadre-normatif') && lead('cadre-normatif').querySelectorAll('b').length,
    titre: aud && aud.getAttribute('title'),
    filtres: [...document.querySelectorAll('#form-cat-filters button')].map(b => b.textContent),
    cartes: [...document.querySelectorAll('#form-cat-grid summary')].map(s => s.textContent),
    numeros: [...document.querySelectorAll('#form-cat-grid .t-card > div > span:last-child')].map(s => s.textContent).slice(0, 2),
    insere: (q('#recette-insere') || {}).textContent || null,
    observateur: typeof SENT_CORPS_OBS !== 'undefined' && !!SENT_CORPS_OBS,
  };
};

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1500, height: 1000 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  /* LES ERREURS QU'ON COMPTE : les exceptions de page, et les erreurs
     console qui ne sont pas un chargement de ressource — le bac à sable de
     recette n'atteint ni les polices ni les CDN (ERR_CERT_AUTHORITY_INVALID),
     et ce n'est pas le produit qu'on mesure là. */
  const RESSOURCE = /Failed to load resource/;
  const err = []; pg.on('pageerror', e => err.push(String(e).slice(0, 180)));
  const con = []; pg.on('console', m => {
    if (m.type() === 'error' && !RESSOURCE.test(m.text())) con.push(m.text().slice(0, 160)); });
  /* UN SEUL CHARGEMENT DE SENTINEL. La page tire plus de cent appels d'API
     à l'ouverture ; deux ouvertures dans la même minute dépassent la limite
     de débit du serveur (120/min par adresse, mesuré : 429 puis blocage
     trente secondes). La connexion par jeton atterrit sur /sentinel, et la
     page témoin s'ouvre ensuite par go(), sans recharger. */
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.waitForFunction(() => typeof sentSetLang === 'function', null, { timeout: 30000 });
  await pg.waitForTimeout(2500);
  await pg.evaluate(() => go('espace'));
  await pg.waitForTimeout(400);

  const route = await pg.evaluate(async () => {
    const r = await fetch('/sentinel.en.json'); return { st: r.status, cc: r.headers.get('cache-control'), et: r.headers.get('etag') };
  });
  ok('la route /sentinel.en.json répond, en cache public, avec un ETag',
     route.st === 200 && /public/.test(route.cc || '') && !!route.et,
     'HTTP ' + route.st + ' · ' + route.cc + ' · ' + route.et);

  /* ── AVANT LA BASCULE : le français, octet pour octet ─────────────── */
  const fr = await pg.evaluate(RELEVE);
  ok('la page est en français et les témoins sont là',
     fr.langue === 'fr' && !!fr.formations && !!fr.espaceHtml && !!fr.cadreHtml && !!fr.titre,
     'lang=' + fr.langue + ' · titre=' + (fr.titre || '∅'));
  ok('le paragraphe témoin contient un lien vers le Reporting',
     fr.espaceLien && /go\('report'/.test(fr.espaceLien.onclick || ''), JSON.stringify(fr.espaceLien));
  ok('le chapeau témoin porte du gras', fr.cadreGras === 1, fr.cadreGras + ' <b>');

  /* ── ON BASCULE ───────────────────────────────────────────────────── */
  await pg.evaluate(() => sentSetLang('en'));
  await pg.waitForTimeout(1500);
  const en = await pg.evaluate(RELEVE);
  ok('la coquille est en anglais', en.langue === 'en' && en.menu.includes('Steering'), en.menu.slice(0, 3).join(' · '));
  ok('le chapeau de la page Formations (régime TEXTE) est traduit',
     en.formations === EN_FORMATIONS, (en.formations || '∅').slice(0, 60));
  ok('le texte AUTOUR du lien est traduit', (en.espaceTexte || '').trim() === EN_ESPACE,
     (en.espaceTexte || '∅').slice(0, 60));
  ok('et le lien SURVIT : même href, même onclick, même texte',
     en.espaceLien && fr.espaceLien && en.espaceLien.href === fr.espaceLien.href
       && en.espaceLien.onclick === fr.espaceLien.onclick && en.espaceLien.texte === fr.espaceLien.texte,
     JSON.stringify(en.espaceLien));
  /* LE DICTIONNAIRE DIT « ISO/IEC # » ; l'écran doit dire « ISO/IEC 42001 » :
     c'est le chiffre du français, réinjecté. */
  ok('le chapeau à gras (régime BLOC) est traduit, garde son <b> et ses chiffres',
     (en.cadreHtml || '').replace(/[0-9]+/g, '#') === EN_CADRE && /42001/.test(en.cadreHtml || '')
       && en.cadreGras === 1, (en.cadreHtml || '∅').slice(0, 60));
  ok('l’attribut title est traduit', en.titre === EN_TITLE, en.titre);

  /* ── CE QUE LE JAVASCRIPT REND APRÈS COUP ─────────────────────────── */
  await pg.evaluate(() => go('training'));
  await pg.waitForTimeout(800);
  const tr = await pg.evaluate(RELEVE);
  ok('les cartes de formation, peintes par go(), sont traduites',
     tr.cartes.length >= 10 && tr.cartes.every(c => c === EN_PROGRAMME),
     tr.cartes.length + ' cartes · ' + (tr.cartes[0] || '∅'));
  ok('une entrée à CHIFFRES garde ses chiffres : « Toutes (15) » → « All (15) »',
     /^All \(\d+\)$/.test(tr.filtres[0] || '') && !/Toutes/.test(tr.filtres[0] || ''), tr.filtres[0]);
  ok('« FORMATION 01 » → « TRAINING 01 »', /^TRAINING 0?1$/.test(tr.numeros[0] || ''), tr.numeros[0]);
  ok('l’observateur est actif en anglais', tr.observateur === true, String(tr.observateur));

  await pg.evaluate(() => {
    const p = document.createElement('p'); p.id = 'recette-insere';
    p.textContent = 'Programme détaillé';
    document.getElementById('p-training').appendChild(p);
  });
  await pg.waitForTimeout(300);
  const ins = await pg.evaluate(RELEVE);
  ok('un nœud inséré APRÈS la bascule est traduit par l’observateur',
     ins.insere === EN_PROGRAMME, ins.insere);

  /* ── LE RETOUR EN FRANÇAIS RESTITUE OCTET POUR OCTET ──────────────── */
  await pg.evaluate(() => sentSetLang('fr'));
  await pg.waitForTimeout(500);
  const re = await pg.evaluate(RELEVE);
  ok('le paragraphe à lien revient à l’identique (innerHTML)', re.espaceHtml === fr.espaceHtml,
     re.espaceHtml === fr.espaceHtml ? 'identique' : (re.espaceHtml || '∅').slice(0, 60));
  ok('le chapeau à gras revient à l’identique (innerHTML)', re.cadreHtml === fr.cadreHtml,
     re.cadreHtml === fr.cadreHtml ? 'identique' : (re.cadreHtml || '∅').slice(0, 60));
  ok('le chapeau Formations et le title reviennent', re.formations === fr.formations && re.titre === fr.titre,
     (re.titre || '∅'));
  ok('le nœud inséré revient en français', re.insere === 'Programme détaillé', re.insere);
  ok('l’observateur est arrêté en français', re.observateur === false, String(re.observateur));
  ok('aucune erreur de page sur tout le parcours', err.length === 0 && con.length === 0,
     (err.concat(con).slice(0, 2).join(' | ') || 'rien'));

  /* ── UN DICTIONNAIRE INJOIGNABLE NE CASSE RIEN ────────────────────────
     Sur la MÊME page (voir plus haut pourquoi on ne recharge pas) : le
     dictionnaire reçu est oublié, la route est mise en panne, et l'anglais
     est redemandé — c'est aussi le chemin du RÉESSAI après un échec. */
  const avantPanne = err.length + con.length;
  await pg.route('**/sentinel.en.json*', r => r.fulfill({ status: 500, body: 'panne simulée' }));
  await pg.evaluate(() => { SENT_CORPS = null; SENT_CORPS_ATTENTE = null; sentSetLang('en'); });
  await pg.waitForTimeout(1200);
  const panne = await pg.evaluate(RELEVE);
  ok('dictionnaire en 500 : la coquille est traduite quand même',
     panne.langue === 'en' && panne.menu.includes('Steering'), panne.menu.slice(0, 3).join(' · '));
  ok('dictionnaire en 500 : le corps reste en français, le lien intact',
     panne.formations === fr.formations && panne.espaceHtml === fr.espaceHtml, (panne.formations || '∅').slice(0, 50));
  ok('dictionnaire en 500 : aucune erreur de page, aucune erreur console hors la ressource elle-même',
     err.length + con.length === avantPanne, (err.concat(con).slice(-2).join(' | ') || 'rien'));
  await pg.evaluate(() => sentSetLang('fr'));

  await nav.close();
  console.log('\n' + (n - ko) + ' / ' + n + ' contrôles verts');
  process.exit(ko ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
