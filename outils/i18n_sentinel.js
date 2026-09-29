#!/usr/bin/env node
/* ══ L'INVENTAIRE DE CE QU'IL Y A À TRADUIRE DANS SENTINEL ═════════════════
 *
 * CE QUE C'EST. Le corps de Sentinel se traduit PAR CONTENU (sentinel.i18n.js) :
 * la clé d'une traduction est le texte français normalisé, relevé À L'ÉCRAN.
 * Cet outil relève ces clés — TOUTES — pour que les traducteurs sachent quoi
 * traduire et que « couverture » (outils/i18n_sentinel.py) sache mesurer.
 *
 * POURQUOI UN NAVIGATEUR, ET PAS UNE LECTURE DU HTML. Ce que le lecteur voit
 * n'est pas sentinel.html : c'est le document APRÈS que sentinel.page.js a
 * peint ses cartes, ses compteurs, ses tableaux — 4 000 chaînes que le HTML
 * ne contient pas. Et la forme d'un élément (bloc ou texte) se décide sur le
 * DOM réel, pas sur une chaîne. L'outil ouvre donc Sentinel dans Chromium,
 * visite CHAQUE page de PAGE_META par go(id), attend le rendu différé, et
 * appelle sentInventaire DU MODULE sur l'élément de la page : l'inventaire
 * et la traduction obéissent ainsi aux mêmes règles, par construction —
 * une clé relevée ici sera cherchée telle quelle par le navigateur.
 *
 * CE QUI SORT : i18n/sentinel/CATALOGUE.json —
 *   { genere_le, pages, rubriques: {page: rubrique du menu},
 *     bloc:  {clé: {fr, html, pages: […], mots}},
 *     texte: {clé: {fr, pages: […], mots}},
 *     attr:  {clé: {fr, pages: […], mots}} }
 * Une clé vue hors des pages (menu, barre, fenêtres) porte la page
 * « _coquille ». Ce que couvrent déjà data-i18n / data-i18n-bloc n'est pas
 * relevé : le module le saute, donc l'inventaire aussi.
 *
 * Usage :
 *   node outils/i18n_sentinel.js extraire                 (lance le serveur lui-même)
 *   node outils/i18n_sentinel.js extraire --base http://127.0.0.1:9917 --token <jeton>
 * Options : --port 9931 (serveur lancé ici) · --sortie <fichier> · --attente <ms>
 *           (délai supplémentaire par page) · --pages a,b,c (sous-ensemble).
 *
 * Chargeable par node (require) : les fonctions pures — compterMots,
 * fusionnerInventaire, statistiques — sont exportées pour les règles.
 */
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const http = require('http');
const { spawn } = require('child_process');

const RACINE = path.dirname(__dirname);
const SORTIE_DEFAUT = path.join(RACINE, 'i18n', 'sentinel', 'CATALOGUE.json');
const JETON_DEFAUT = 'recette_locale_idf_0123456789abcdef';
const PORT_DEFAUT = 9931;
const NAVIGATEUR = 'Mozilla/5.0 (X11; Linux x86_64) Firefox/130.0';

/* UN MOT : une suite de lettres latines, accents compris. LA MÊME définition
   que outils/i18n_sentinel.py — les deux comptent les mêmes mots, sinon la
   couverture d'une page serait mesurée avec deux règles. */
const MOT = /[A-Za-zÀ-ɏ]+/g;
function compterMots(s) {
  return (String(s === null || s === undefined ? '' : s).match(MOT) || []).length;
}

function catalogueVide() {
  return { genere_le: null, pages: 0, rubriques: {}, bloc: {}, texte: {}, attr: {} };
}

/* FUSIONNE L'INVENTAIRE D'UNE PAGE (la sortie de sentInventaire) dans le
   catalogue, en étiquetant chaque clé de la page où elle a été vue. Le
   module ne date les pages que pour le régime bloc ; ici, la page est celle
   de l'appel — c'est pour cela que l'outil appelle sentInventaire PAR PAGE
   et non une fois sur le document. Rend le nombre de clés NOUVELLES. */
function fusionnerInventaire(cat, inv, page) {
  let nouvelles = 0;
  const poser = (regime, cle, fr, html) => {
    let ent = cat[regime][cle];
    if (!ent) {
      ent = cat[regime][cle] = regime === 'bloc'
        ? { fr: fr, html: html, pages: [], mots: compterMots(fr) }
        : { fr: fr, pages: [], mots: compterMots(fr) };
      nouvelles++;
    }
    if (page && ent.pages.indexOf(page) < 0) ent.pages.push(page);
  };
  for (const cle of Object.keys(inv.bloc || {})) poser('bloc', cle, inv.bloc[cle].fr, inv.bloc[cle].html);
  for (const cle of Object.keys(inv.texte || {})) poser('texte', cle, inv.texte[cle]);
  for (const cle of Object.keys(inv.attr || {})) poser('attr', cle, inv.attr[cle]);
  return nouvelles;
}

/* LES CLÉS D'UN INVENTAIRE QUI NE SONT DANS AUCUNE PAGE : la coquille. */
function fusionnerCoquille(cat, invCorps) {
  const reste = { bloc: {}, texte: {}, attr: {} };
  for (const regime of ['bloc', 'texte', 'attr']) {
    for (const cle of Object.keys(invCorps[regime] || {})) {
      if (!cat[regime][cle]) reste[regime][cle] = invCorps[regime][cle];
    }
  }
  return fusionnerInventaire(cat, reste, '_coquille');
}

/* ENTRÉES ET MOTS PAR RÉGIME, ET MOTS PAR PAGE (une entrée vue sur deux
   pages compte pour les deux : c'est ce qu'il y a à lire sur chacune). */
function statistiques(cat) {
  const regimes = {}, pages = {};
  for (const regime of ['bloc', 'texte', 'attr']) {
    let entrees = 0, mots = 0;
    for (const cle of Object.keys(cat[regime] || {})) {
      const e = cat[regime][cle];
      entrees++; mots += e.mots;
      for (const p of e.pages) {
        if (!pages[p]) pages[p] = { entrees: 0, mots: 0 };
        pages[p].entrees++; pages[p].mots += e.mots;
      }
    }
    regimes[regime] = { entrees, mots };
  }
  return { regimes, pages };
}

/* LE CATALOGUE S'ÉCRIT TRIÉ : deux extractions du même état donnent le même
   fichier, et un diff git montre ce qui a changé dans le produit. */
function trie(obj) {
  const out = {};
  for (const k of Object.keys(obj).sort()) out[k] = obj[k];
  return out;
}
function ecrireCatalogue(cat, sortie) {
  const propre = {
    genere_le: cat.genere_le, pages: cat.pages, rubriques: trie(cat.rubriques),
    bloc: trie(cat.bloc), texte: trie(cat.texte), attr: trie(cat.attr),
  };
  fs.mkdirSync(path.dirname(sortie), { recursive: true });
  fs.writeFileSync(sortie, JSON.stringify(propre, null, 1) + '\n', 'utf8');
}

/* ── LE SERVEUR LOCAL, lancé ici quand --base n'est pas donné ─────────── */
function attendreServeur(base, delai) {
  const fin = Date.now() + delai;
  return new Promise((resolve, reject) => {
    (function essai() {
      const rq = http.get(base + '/', { headers: { 'User-Agent': NAVIGATEUR } }, (r) => {
        r.resume(); resolve(r.statusCode);
      });
      rq.on('error', () => {
        if (Date.now() > fin) reject(new Error('le serveur ne répond pas sur ' + base));
        else setTimeout(essai, 250);
      });
    })();
  });
}

/* UN PORT LIBRE ENTRE 9900 ET 9960 — plusieurs recettes tournent parfois
   côte à côte sur la même machine, et un serveur qui n'a pas pu se lier
   laisserait l'outil interroger CELUI D'UN AUTRE dossier, sans le savoir. */
function portLibre(prefere) {
  const net = require('net');
  const essayer = (port) => new Promise((resolve) => {
    const s = net.createServer();
    s.once('error', () => resolve(false));
    s.listen(port, '127.0.0.1', () => s.close(() => resolve(true)));
  });
  return (async () => {
    const candidats = [prefere];
    for (let p = 9900; p <= 9960; p++) if (p !== prefere) candidats.push(p);
    for (const p of candidats) if (await essayer(p)) return p;
    throw new Error('aucun port libre entre 9900 et 9960');
  })();
}

function porteLePort(pid, port) {
  try {
    const env = fs.readFileSync('/proc/' + pid + '/environ', 'latin1');
    return env.split('\0').indexOf('PORT=' + port) >= 0;
  } catch (e) { return false; }
}

async function lancerServeur(portPrefere) {
  const port = await portLibre(portPrefere);
  const journal = path.join(os.tmpdir(), 'i18n_sentinel_serveur_' + port + '.log');
  const fd = fs.openSync(journal, 'w');
  const enfant = spawn('python', ['app.py'], {
    cwd: RACINE, detached: true, stdio: ['ignore', fd, fd],
    env: Object.assign({}, process.env, { PORT: String(port), AUTH_MASTER_TOKEN: JETON_DEFAUT }),
  });
  enfant.unref();
  const base = 'http://127.0.0.1:' + port;
  await attendreServeur(base, 60000);
  /* C'EST BIEN LE NÔTRE QUI RÉPOND : le processus lancé est encore là, et
     son environnement porte ce port. */
  if (enfant.exitCode !== null || !porteLePort(enfant.pid, port)) {
    let fin = '';
    try { fin = fs.readFileSync(journal, 'utf8').slice(-600); } catch (e) { /* rien */ }
    throw new Error('le serveur lancé (pid ' + enfant.pid + ') n\'a pas pris le port ' + port + '\n' + fin);
  }
  return { pid: enfant.pid, base, journal, port };
}

/* ARRÊT PAR PID EXACT, après avoir vérifié que ce PID porte bien NOTRE port
   dans son environnement : on ne tue jamais un serveur qu'on n'a pas lancé. */
function arreterServeur(serveur) {
  if (!serveur) return;
  if (!porteLePort(serveur.pid, serveur.port)) {
    console.error('  serveur ' + serveur.pid + ' : ne porte pas le port ' + serveur.port + ', non arrêté');
    return;
  }
  try { process.kill(serveur.pid, 'SIGTERM'); } catch (e) { /* déjà parti */ }
  try { fs.unlinkSync(serveur.journal); } catch (e) { /* rien à effacer */ }
}

/* ── L'EXTRACTION ────────────────────────────────────────────────────── */
async function extraire(opts) {
  const { chromium } = require('/opt/node22/lib/node_modules/playwright');
  let serveur = null;
  let base = opts.base;
  if (!base) {
    serveur = await lancerServeur(opts.port);
    base = serveur.base;
    console.log('  serveur lancé : ' + base + ' (pid ' + serveur.pid + ')');
  }
  const nav = await chromium.launch();
  const cat = catalogueVide();
  try {
    const ctx = await nav.newContext({ viewport: { width: 1500, height: 1000 }, userAgent: NAVIGATEUR });
    await ctx.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', { get: () => false });
      Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
    });
    const pg = await ctx.newPage();
    const erreurs = [];
    pg.on('pageerror', (e) => erreurs.push(String(e).slice(0, 160)));
    /* LA CONNEXION PAR JETON ATTERRIT SUR /sentinel ; un seul chargement,
       puis les pages s'ouvrent par go() sans recharger (la page tire plus
       de cent appels d'API à l'ouverture). */
    await pg.goto(base + '/auth/' + opts.token, { waitUntil: 'commit' });
    await pg.waitForFunction(() => typeof sentInventaire === 'function' && typeof PAGE_META === 'object'
                                   && typeof go === 'function', null, { timeout: 60000 });
    await pg.waitForTimeout(2500);
    /* LE FRANÇAIS, TOUJOURS : un inventaire relevé en anglais donnerait des
       clés anglaises. */
    await pg.evaluate(() => { if (typeof sentSetLang === 'function') sentSetLang('fr'); });

    const meta = await pg.evaluate(() => {
      const out = {};
      for (const id of Object.keys(PAGE_META)) out[id] = PAGE_META[id].section || '';
      return out;
    });
    const ids = opts.pages && opts.pages.length ? opts.pages : Object.keys(meta);
    cat.rubriques = meta;

    /* L'ATTENTE DU RENDU DIFFÉRÉ : go() programme ses rendus par
       requestAnimationFrame puis setTimeout 0 (_apresPeinture) ; deux images
       et 300 ms les couvrent, plus ce que --attente ajoute pour les rendus
       qui attendent une réponse d'API. */
    const attendreRendu = async () => {
      await pg.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(() => setTimeout(r, 300)))));
      if (opts.attente) await pg.waitForTimeout(opts.attente);
    };
    const inventaireDe = (id) => pg.evaluate((id) => {
      const el = document.getElementById('p-' + id);
      return el ? sentInventaire(el) : null;
    }, id);

    let absentes = [];
    for (let i = 0; i < ids.length; i++) {
      const id = ids[i];
      await pg.evaluate((id) => { try { go(id); } catch (e) { /* une page sans rendu propre */ } }, id);
      await attendreRendu();
      const inv = await inventaireDe(id);
      if (!inv) { absentes.push(id); continue; }
      const n = fusionnerInventaire(cat, inv, id);
      process.stdout.write('  ' + String(i + 1).padStart(3) + '/' + ids.length + '  ' + id.padEnd(28) + ' +' + n + '\n');
    }
    /* SECONDE PASSE SUR CHAQUE PAGE : ce qu'une réponse d'API a peint après
       qu'on l'a quittée est relevé quand même, à sa page. */
    for (const id of ids) {
      const inv = await inventaireDe(id);
      if (inv) fusionnerInventaire(cat, inv, id);
    }
    /* PUIS LE DOCUMENT ENTIER : ce qui n'est dans aucune page — menu,
       barre, fenêtres, pied — est la coquille. */
    const corps = await pg.evaluate(() => sentInventaire(document.body));
    const coquille = fusionnerCoquille(cat, corps);
    cat.pages = ids.length - absentes.length;
    cat.genere_le = new Date().toISOString();
    if (absentes.length) console.log('  pages de PAGE_META sans élément #p-… : ' + absentes.join(', '));
    console.log('  coquille : +' + coquille + ' clés');
    if (erreurs.length) console.log('  erreurs de page : ' + erreurs.slice(0, 3).join(' | '));
  } finally {
    await nav.close();
    arreterServeur(serveur);
  }
  ecrireCatalogue(cat, opts.sortie);
  const st = statistiques(cat);
  console.log('\n  catalogue écrit : ' + path.relative(RACINE, opts.sortie) + ' (' + cat.pages + ' pages)');
  for (const r of ['bloc', 'texte', 'attr']) {
    console.log('  ' + r.padEnd(6) + String(st.regimes[r].entrees).padStart(6) + ' entrées ' + String(st.regimes[r].mots).padStart(7) + ' mots');
  }
  const total = ['bloc', 'texte', 'attr'].reduce((s, r) => s + st.regimes[r].mots, 0);
  console.log('  total ' + String(total).padStart(7) + ' mots');
  const pages = Object.keys(st.pages).sort((a, b) => st.pages[b].mots - st.pages[a].mots).slice(0, 10);
  console.log('  les dix pages les plus lourdes :');
  for (const p of pages) console.log('    ' + p.padEnd(28) + String(st.pages[p].entrees).padStart(5) + ' entrées ' + String(st.pages[p].mots).padStart(6) + ' mots');
  return cat;
}

/* ── LA LIGNE DE COMMANDE ────────────────────────────────────────────── */
function lireOptions(argv) {
  const opts = { commande: argv[0], base: '', token: JETON_DEFAUT, port: PORT_DEFAUT,
                 sortie: SORTIE_DEFAUT, attente: 0, pages: [] };
  for (let i = 1; i < argv.length; i++) {
    const a = argv[i], v = argv[i + 1];
    if (a === '--base') { opts.base = String(v || '').replace(/\/$/, ''); i++; }
    else if (a === '--token') { opts.token = v; i++; }
    else if (a === '--port') { opts.port = parseInt(v, 10); i++; }
    else if (a === '--sortie') { opts.sortie = path.resolve(v); i++; }
    else if (a === '--attente') { opts.attente = parseInt(v, 10) || 0; i++; }
    else if (a === '--pages') { opts.pages = String(v || '').split(',').filter(Boolean); i++; }
    else throw new Error('option inconnue : ' + a);
  }
  return opts;
}

if (require.main === module) {
  const opts = lireOptions(process.argv.slice(2));
  if (opts.commande !== 'extraire') {
    console.error('usage : node outils/i18n_sentinel.js extraire [--base URL --token JETON | --port N] [--sortie F] [--attente MS] [--pages a,b]');
    process.exit(2);
  }
  extraire(opts).then(() => process.exit(0), (e) => { console.error(e); process.exit(1); });
}

module.exports = { compterMots, catalogueVide, fusionnerInventaire, fusionnerCoquille,
                   statistiques, ecrireCatalogue, lireOptions };
