/* RECETTE — QUELLE PART DE SENTINEL EST ENCORE EN FRANÇAIS QUAND EN EST CHOISI
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * CE QU'ELLE MESURE, ET QUE RIEN D'AUTRE NE PEUT MESURER. Les règles Python
 * savent ce que le dictionnaire CONTIENT ; elles ne savent pas ce qu'un
 * lecteur VOIT. Une clé mal normalisée, un texte que le JavaScript peint
 * après coup, un attribut oublié, un bloc refusé parce qu'un span porte une
 * classe : tout cela ne se voit qu'à l'écran. Cette recette ouvre donc
 * Sentinel dans un vrai navigateur, choisit EN, attend le dictionnaire, puis
 * VISITE CHAQUE PAGE de PAGE_META et relève tout ce qui est visible — les
 * nœuds texte dont l'élément a une boîte, et les attributs title,
 * aria-label, placeholder, value des boutons, l'option choisie d'un
 * <select> — dans la page courante et, à part, dans le menu et la barre.
 *
 * CHAQUE TEXTE EST CLASSÉ français / anglais / neutre par l'heuristique de
 * outils/sentinel_langue.js (mots-outils, accents, élisions, terminaisons ;
 * un nom propre seul ou une chaîne sans lettre sont neutres). Le score
 * d'une page est mots français / (français + anglais) ; les neutres sont
 * comptés à part. Le JSON produit garde, par page, les quinze plus longs
 * textes français restants : c'est la liste de travail du lot de
 * traduction.
 *
 * LE POINT DE DÉPART est commité dans i18n/sentinel/MESURE_AVANT.json ; le
 * lot de traduction doit le battre, et le seuil (--seuil, 5 % par défaut)
 * rend un code 1 tant que la part française globale le dépasse.
 *
 * LE LIMITEUR DE DÉBIT EST RESPECTÉ, PAS CONTOURNÉ : 120 requêtes par
 * minute et par adresse, un chargement de Sentinel en coûte près de cent,
 * et plusieurs pages en tirent encore à l'ouverture. La recette compte ses
 * propres requêtes sur une minute glissante et attend avant d'ouvrir une
 * page si la fenêtre est pleine. MESURÉ : jouée moins d'une minute après
 * une autre recette, la première version a reçu 57 réponses 429 — le
 * dictionnaire n'est jamais arrivé et six pages ont été relevées sur leur
 * « Chargement… ». Chaque 429 est donc compté ; s'il en arrive pendant le
 * chargement, la page est rechargée après une minute de silence ; s'il en
 * arrive sur une page, elle est rouverte après le même silence ; et les
 * pages qui en ont reçu malgré tout sont NOMMÉES dans le JSON
 * (pages_429), pour qu'on ne lise pas un « Chargement… » comme du produit.
 *
 * LES CADRES (iframes : panorama, enveloppe, empreinte du parc,
 * observatoire) sont d'autres documents ; depuis qu'ils chargent
 * sentinel.i18n.js (data-sent-cadre), ils se traduisent par LA MÊME
 * mécanique que Sentinel. Leur texte est donc relevé à part (« cadres »)
 * pour être vu, ET COMPRIS DANS LE VERDICT : les tenir dehors reviendrait à
 * ne pas regarder un cinquième de ce qu'un lecteur voit.
 *
 * LES DONNÉES SAISIES NE SONT PAS DU FRANÇAIS À TRADUIRE. Le nom d'un
 * système au registre, son fournisseur, sa finalité, le nom d'un client :
 * ce sont les systèmes d'IA du client, écrits dans SA langue. La page les
 * déclare translate="no" ; le relevé les marque « donnee: », l'agrégation
 * les compte À PART et les tient HORS DU VERDICT, en disant leur volume.
 * MESURÉ AVANT CE PARTAGE : 57 255 des 70 061 mots français relevés — 82 % —
 * étaient des entrées de registre réaffichées des milliers de fois par le
 * registre, la matrice, l'empreinte, le FinOps et la qualification assistée.
 *
 * Usage :
 *   (cd <dossier> && PORT=9931 AUTH_MASTER_TOKEN=recette_locale_idf_0123456789abcdef nohup python app.py > log 2>&1 &)
 *   BASE=http://127.0.0.1:9931 node recette_sentinel_langue.js --sortie i18n/sentinel/MESURE_AVANT.json
 *   node recette_sentinel_langue.js --relire i18n/sentinel/MESURE_AVANT.json --seuil 0.05   (sans navigateur)
 *
 * Options : --seuil <0..1> (défaut 0.05) · --sortie <fichier.json> ·
 *           --pages a,b,c (quelques pages seulement) · --relire <fichier.json> ·
 *           --brut <fichier.json> (les relevés eux-mêmes, texte par texte)
 */
const fs = require('fs');
const path = require('path');
const L = require(path.join(__dirname, 'outils', 'sentinel_langue.js'));

const BASE = process.env.BASE || 'http://127.0.0.1:9931';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
const ATTENTE_PAGE = Number(process.env.ATTENTE_PAGE || 450);
/* Sous la limite du serveur (120/min), avec la marge de ce qu'une page tire
   à l'ouverture. */
const REQUETES_MAX = Number(process.env.REQUETES_MAX || 100);
const ATTRIBUTS = ['title', 'aria-label', 'placeholder'];
const SILENCE = Number(process.env.SILENCE || 62000);  /* la minute du limiteur, et un peu */

function lireOptions(argv) {
  const o = { seuil: L.SEUIL_DEFAUT, sortie: null, pages: null, relire: null, brut: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i], v = argv[i + 1];
    if (a === '--seuil') { o.seuil = Number(v); i++; }
    else if (a === '--sortie') { o.sortie = v; i++; }
    else if (a === '--pages') { o.pages = v.split(',').map(s => s.trim()).filter(Boolean); i++; }
    else if (a === '--relire') { o.relire = v; i++; }
    else if (a === '--brut') { o.brut = v; i++; }
    else throw new Error('option inconnue : ' + a);
  }
  if (!(o.seuil >= 0 && o.seuil <= 1)) throw new Error('--seuil attend un nombre entre 0 et 1, reçu : ' + o.seuil);
  return o;
}

/* LE RELEVÉ, JOUÉ DANS LA PAGE. Rend la liste des textes visibles sous
   `selecteurs`, chacun avec sa provenance. Un élément est visible s'il a
   une boîte non nulle ET que le navigateur le dit visible (checkVisibility
   couvre display, visibility, content-visibility, un <details> replié) ;
   ce qu'un ancêtre rogne par overflow n'est pas distingué — c'est la limite
   de la mesure, écrite ici. */
const RELEVER = ([selecteurs, ATTRIBUTS]) => {
  const EXCLUS = { SCRIPT: 1, STYLE: 1, NOSCRIPT: 1, TEMPLATE: 1, SVG: 1, CANVAS: 1 };
  const LETTRE = /[A-Za-zÀ-ÿ]/;
  const out = [];
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0)) return false;
    if (typeof el.checkVisibility === 'function') return el.checkVisibility({ visibilityProperty: true });
    return getComputedStyle(el).visibility !== 'hidden';
  };
  const pousser = (t, ou, prefixe) => {
    const v = String(t || '').replace(/\s+/g, ' ').trim();
    if (v && LETTRE.test(v)) out.push({ t: v, ou: prefixe + ou });
  };
  const marcher = (el, prefixe) => {
    const tag = String(el.tagName || '').toUpperCase();
    if (EXCLUS[tag]) return;
    if (!visible(el)) return;
    /* UNE DONNÉE SAISIE SE DÉCLARE translate="no", ET TOUT CE QU'ELLE
       CONTIENT EN EST UNE AUSSI — exactement la règle que le moteur de
       traduction applique (sentinel.i18n.js, sentMarcher). Le marqueur est
       posé en tête de la provenance ; l'agrégation relève ces textes à part
       et les tient hors du verdict. Les ATTRIBUTS de l'élément marqué le
       sont avec lui : le moteur ne les traduit pas non plus. */
    if (el.getAttribute && el.getAttribute('translate') === 'no' && prefixe.indexOf('donnee:') < 0) {
      prefixe = prefixe + 'donnee:';
    }
    for (const a of ATTRIBUTS) pousser(el.getAttribute(a), a, prefixe);
    if (tag === 'INPUT' && /^(submit|button|reset)$/i.test(el.getAttribute('type') || '')) pousser(el.value, 'value', prefixe);
    if (tag === 'SELECT') {
      /* SEULE L'OPTION CHOISIE SE LIT : les autres n'ont pas de boîte. */
      const opt = el.options && el.options[el.selectedIndex];
      if (opt) pousser(opt.text, 'option', prefixe);
      return;
    }
    if (tag === 'IFRAME') {
      /* UN CADRE DE MÊME ORIGINE est un autre document : relevé à part,
         sous « cadre: », parce que le dictionnaire de Sentinel ne l'atteint
         pas. Un cadre d'une autre origine ne se lit pas, et ne compte pas. */
      let doc = null;
      try { doc = el.contentDocument; } catch (e) { doc = null; }
      if (doc && doc.body) marcher(doc.body, 'cadre:');
      return;
    }
    for (const n of el.childNodes) {
      if (n.nodeType === 3) pousser(n.nodeValue, 'texte', prefixe);
      else if (n.nodeType === 1) marcher(n, prefixe);
    }
  };
  for (const s of selecteurs) document.querySelectorAll(s).forEach(el => marcher(el, ''));
  return out;
};

/* UN CADRE CHARGÉ N'EST PAS ENCORE TRADUIT : il se branche lui-même
   (sentinel.i18n.js, data-sent-cadre), puis télécharge le dictionnaire —
   après son événement `load`. On attend que chaque cadre branché en anglais
   l'ait reçu (huit secondes au plus), puis une passe. Un cadre qui ne se
   branche pas (ancien code) n'est pas attendu : il est mesuré tel quel. */
const ATTENDRE_CADRES_TRADUITS = (id) => new Promise(r => {
  const t0 = Date.now();
  (function attendre() {
    const pret = [...document.querySelectorAll('#p-' + id + ' iframe')].every(f => {
      let b = null; try { b = f.contentWindow && f.contentWindow.SENT_CADRE; } catch (e) { b = null; }
      return !b || b.langue() !== 'en' || !!b.dico;
    });
    if (pret || Date.now() - t0 > 8000) setTimeout(r, 150); else setTimeout(attendre, 50);
  })();
});

/* LES CADRES D'UNE PAGE SE CHARGENT : leur src n'est posé qu'au premier
   temps mort du navigateur (sentinel.page.js) ; on le pose si ce n'est pas
   fait, et on attend que chacun ait fini de charger. */
const CHARGER_CADRES = (id) => {
  const cadres = [...document.querySelectorAll('#p-' + id + ' iframe')];
  return Promise.all(cadres.map(f => new Promise(r => {
    if (!f.getAttribute('src') && f.getAttribute('data-src')) f.setAttribute('src', f.getAttribute('data-src'));
    let doc = null; try { doc = f.contentDocument; } catch (e) { doc = null; }
    if (doc && doc.readyState === 'complete' && doc.body && doc.body.childNodes.length) return r('déjà');
    const fin = setTimeout(() => r('délai'), 8000);
    f.addEventListener('load', () => { clearTimeout(fin); r('chargé'); }, { once: true });
  }))).then(etats => etats.length);
};

async function mesurer(options) {
  const { chromium } = require('/opt/node22/lib/node_modules/playwright');
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1500, height: 1000 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const RESSOURCE = /Failed to load resource/;
  const erreurs = [];
  pg.on('pageerror', e => erreurs.push('page : ' + String(e).slice(0, 160)));
  pg.on('console', m => { if (m.type() === 'error' && !RESSOURCE.test(m.text())) erreurs.push('console : ' + m.text().slice(0, 160)); });
  /* LA MINUTE GLISSANTE DES REQUÊTES, pour respecter le limiteur — et le
     compte des 429, qui disent que le serveur a refusé quand même. */
  const horodatages = [];
  let refus = 0;
  pg.on('request', r => { if (r.url().indexOf(BASE) === 0) horodatages.push(Date.now()); });
  pg.on('response', r => { if (r.status() === 429) refus++; });
  const recentes = () => { const t = Date.now() - 60000; while (horodatages.length && horodatages[0] < t) horodatages.shift(); return horodatages.length; };
  const pause = (ms) => new Promise(r => setTimeout(r, ms));
  let attentes = 0;
  const respirer = async () => { while (recentes() >= REQUETES_MAX) { attentes++; await pause(1000); } };
  const silence = async (pourquoi) => { process.stderr.write('  … ' + pourquoi + ' : ' + Math.round(SILENCE / 1000) + ' s de silence\n'); await pause(SILENCE); horodatages.length = 0; };

  const charger = async () => {
    await pg.waitForFunction(() => typeof sentSetLang === 'function' && typeof go === 'function', null, { timeout: 30000 });
    await pg.waitForTimeout(2500);
  };
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await charger();
  if (refus) {
    /* LE CHARGEMENT A ÉTÉ REFUSÉ EN PARTIE : une page qui a reçu des 429 à
       l'ouverture montre des « Chargement… » ou des erreurs, pas le produit. */
    await silence(refus + ' réponses 429 au chargement');
    refus = 0;
    await pg.goto(BASE + '/sentinel', { waitUntil: 'commit' });
    await charger();
  }

  const toutes = await pg.evaluate(() => Object.keys(PAGE_META));
  const pages = options.pages ? options.pages : toutes;
  const inconnues = pages.filter(p => toutes.indexOf(p) < 0);
  if (inconnues.length) throw new Error('pages absentes de PAGE_META : ' + inconnues.join(', '));

  /* ON CHOISIT EN, ET ON ATTEND LE DICTIONNAIRE — sans exiger qu'il vienne :
     un dictionnaire injoignable est un résultat, pas une panne de recette. */
  /* LE DICTIONNAIRE REÇU — tenu par le branchement de sentinel.i18n.js
     (SENT_CORPS_BRANCHE.dico) ; SENT_CORPS est son nom d'avant, lu encore
     pour mesurer un serveur qui sert l'ancien code (la colonne « avant »).
     Écrit en clair dans chaque évaluation : la CSP de Sentinel refuse eval. */
  const lireDico = () => pg.evaluate(() => {
    const d = (typeof SENT_CORPS_BRANCHE !== 'undefined' && SENT_CORPS_BRANCHE)
      ? SENT_CORPS_BRANCHE.dico : (typeof SENT_CORPS !== 'undefined' ? SENT_CORPS : null);
    return d ? { charge: true, texte: Object.keys(d.texte || {}).length, bloc: Object.keys(d.bloc || {}).length,
                 motif: Object.keys(d.motif || {}).length }
             : { charge: false, texte: 0, bloc: 0, motif: 0 };
  });
  const demanderEN = async () => {
    await respirer();
    await pg.evaluate(() => sentSetLang('en'));
    await pg.waitForFunction(() => !!((typeof SENT_CORPS_BRANCHE !== 'undefined' && SENT_CORPS_BRANCHE)
      ? SENT_CORPS_BRANCHE.dico : (typeof SENT_CORPS !== 'undefined' ? SENT_CORPS : null)),
      null, { timeout: 20000 }).catch(() => null);
    return lireDico();
  };
  let dictionnaire = await demanderEN();
  if (!dictionnaire.charge) {
    /* UN SEUL RÉESSAI, après la minute du limiteur : sentSetLang('en') une
       seconde fois relance le téléchargement, puisqu'un échec ne le laisse
       pas en attente (sentinel.i18n.js, sentBrancher → charger). */
    await silence('dictionnaire non reçu');
    dictionnaire = await demanderEN();
  }
  const langue = await pg.evaluate(() => document.documentElement.lang);
  if (langue !== 'en') throw new Error('la page n\'est pas passée en anglais (lang=' + langue + ')');

  const releves = { pages: {}, coquille: [] };
  const coquilleVue = {};
  const pages429 = [];
  const visiter = async (id) => {
    await respirer();
    await pg.evaluate(id => go(id), id);
    /* LE RENDU DIFFÉRÉ : _apresPeinture (rAF + setTimeout 0), les données
       que la page tire, les cadres, puis la passe de l'observateur (rAF). */
    await pg.waitForTimeout(ATTENTE_PAGE);
    await pg.evaluate(CHARGER_CADRES, id);
    await pg.evaluate(ATTENDRE_CADRES_TRADUITS, id);
    await pg.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
    const courante = await pg.evaluate(() => (document.querySelector('.page.on') || {}).id || null);
    if (courante !== 'p-' + id) throw new Error('go(' + id + ') n\'a pas ouvert la page : .page.on = ' + courante);
    return pg.evaluate(RELEVER, [['#p-' + id], ATTRIBUTS]);
  };
  for (let i = 0; i < pages.length; i++) {
    const id = pages[i];
    let avant = refus;
    let releve = await visiter(id);
    if (refus > avant) {
      /* LA PAGE A ÉTÉ REFUSÉE EN PARTIE : on la rouvre après la minute du
         limiteur. Si elle est refusée encore, elle est nommée. */
      await silence('page ' + id + ' : ' + (refus - avant) + ' réponses 429');
      avant = refus;
      releve = await visiter(id);
      if (refus > avant) pages429.push(id);
    }
    releves.pages[id] = releve;
    const coq = await pg.evaluate(RELEVER, [['#sb', 'header.topbar'], ATTRIBUTS]);
    for (const e of coq) {
      const k = e.ou + '\u0000' + e.t;
      if (!coquilleVue[k]) { coquilleVue[k] = true; releves.coquille.push(e); }
    }
    process.stderr.write('  ' + String(i + 1).padStart(3) + '/' + pages.length + '  ' + id + '  (' + releve.length + ' textes)\n');
  }
  await nav.close();
  if (options.brut) fs.writeFileSync(options.brut, JSON.stringify(releves, null, 1) + '\n');
  const mesure = L.agreger(releves, { base: BASE, seuil: options.seuil, dictionnaire });
  mesure.erreurs = erreurs.slice(0, 20);
  mesure.attentes_limiteur = attentes;
  mesure.reponses_429 = refus;
  mesure.pages_429 = pages429;
  return mesure;
}

function conclure(mesure, options) {
  console.log(L.resumer(mesure, options.seuil));
  if (mesure.erreurs && mesure.erreurs.length) console.log('\nerreurs de page : ' + mesure.erreurs.length + ' — ' + mesure.erreurs.slice(0, 3).join(' | '));
  if (mesure.pages_429 && mesure.pages_429.length) console.log('\nPAGES REFUSÉES PAR LE LIMITEUR (relevées sur leur « Chargement… ») : ' + mesure.pages_429.join(', '));
  return L.verdict(mesure, options.seuil);
}

async function main() {
  const options = lireOptions(process.argv.slice(2));
  if (options.relire) {
    const mesure = JSON.parse(fs.readFileSync(options.relire, 'utf8'));
    return conclure(mesure, options);
  }
  const mesure = await mesurer(options);
  if (options.sortie) {
    fs.writeFileSync(options.sortie, JSON.stringify(mesure, null, 1) + '\n');
    console.log('mesure écrite : ' + options.sortie + '\n');
  }
  return conclure(mesure, options);
}

if (require.main === module) {
  main().then(code => process.exit(code)).catch(e => { console.error(e); process.exit(2); });
} else {
  module.exports = { lireOptions, RELEVER, mesurer };
}
