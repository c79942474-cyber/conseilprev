/* ══ SENTINEL SE TRADUIT PAR CONTENU — le module partagé ═══════════════════
 *
 * CE QUI EXISTAIT. Le moteur bilingue de sentinel.page.js traduit la COQUILLE
 * (menu, fil d'Ariane, surtitre, titre, chapeau) par des attributs data-i18n :
 * 213 clés, posées une à une dans le HTML. Le corps des 118 pages — 25 900
 * mots — et les 4 000 chaînes que le JavaScript rend après coup restaient en
 * français. Marquer 4 300 éléments dans un fichier de 890 Ko aurait été
 * fragile, et n'aurait de toute façon rien fait pour ce que le JavaScript
 * peint : une carte de formation, un compteur, un message d'état.
 *
 * LE CORPS SE TRADUIT DONC PAR CONTENU, \u00c0 L'EXÉCUTION. La clé d'une
 * traduction est le texte français lui-même, NORMALISÉ (§ sentNormaliser) :
 * on parcourt le document, on retrouve chaque texte dans le dictionnaire, on
 * l'écrit. Ce que le JavaScript rend ensuite passe par le même chemin, porté
 * par un observateur (sentinel.page.js).
 *
 * DEUX RÉGIMES, DÉCIDÉS PAR LA FORME DE L'ÉLÉMENT (§ sentClasser) :
 *   · BLOC — l'élément ne contient que de la mise en forme (gras, italique,
 *     exposant…) SANS AUCUN attribut : il est traduit d'un seul tenant, par
 *     innerHTML, pour que « le <b>Cyber Resilience Act</b> pour » ne devienne
 *     pas trois fragments recousus mot à mot. C'est le seul endroit où
 *     innerHTML s'écrit, et il est ENCADRÉ : un lien, un bouton, un
 *     identifiant, un gestionnaire, une icône, un span à classe — tout ce qui
 *     porte un comportement — retire l'élément de ce régime.
 *   · TEXTE — sinon, chaque nœud texte est traduit SEUL, par nodeValue, et
 *     les enfants sont parcourus. Un lien au milieu d'un paragraphe survit
 *     parce que rien ne le réécrit. C'est le piège de l'accueil, payé deux
 *     fois dans ce dépôt (`el.innerHTML = <traduction>` effaçait les liens),
 *     et la raison de ce partage en deux régimes.
 *
 * RÉVERSIBLE. L'original de chaque nœud et de chaque attribut touché est
 * gardé dans une WeakMap ; le retour au français le restitue octet pour
 * octet, et rien n'est jamais perdu. Un nœud dont la valeur courante est
 * déjà sa traduction est sauté : l'observateur peut repasser sans boucler.
 *
 * SANS DÉPENDANCE, EN ES5 (var, function) comme le reste de Sentinel, et
 * chargeable par node : les règles (tests/test_sentinel_corps.py) et l'outil
 * d'inventaire exécutent CE fichier, pas une copie. */

var SENT_INLINE = ['b', 'strong', 'i', 'em', 'u', 's', 'sup', 'sub', 'small',
                   'mark', 'code', 'kbd', 'abbr', 'br', 'wbr', 'span'];
/* CE QU'ON NE PARCOURT PAS : du code, des données, ce que l'utilisateur
   saisit, ce qu'un moteur dessine. Leurs ATTRIBUTS (title, placeholder…)
   restent traduits ; leur contenu, non. */
var SENT_EXCLUS = ['script', 'style', 'textarea', 'input', 'select', 'option',
                   'code', 'pre', 'svg', 'canvas', 'iframe'];
/* Et ceux dont on ne touche RIEN, pas même les attributs : un `title` de
   script n'existe pas, et les attributs d'un SVG ne sont pas du texte. */
var SENT_MUETS = ['script', 'style', 'svg', 'canvas'];
var SENT_ATTRIBUTS = ['title', 'aria-label', 'placeholder', 'alt'];

/* LA MÊME LISTE QUE sentinel_i18n.py, \u00c0 LA LETTRE. `\s` couvre l'insécable
   et la fine en JavaScript mais pas la marque d'ordre des octets en Python :
   chaque caractère est donc nommé, des deux côtés. */
var SENT_BLANCS = /[\s\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000\ufeff]+/g;
var SENT_CHIFFRES = /[0-9]+(?:[.,][0-9]+)*/g;
var SENT_LETTRE = /[A-Za-z\u00c0-\u024f]/;

/* NFC, chaque blanc devient une espace, les suites se réduisent, trim. */
function sentAplanir(s) {
  s = (s === null || s === undefined) ? '' : String(s);
  if (s.normalize) s = s.normalize('NFC');
  s = s.replace(SENT_BLANCS, ' ');
  if (s.charAt(0) === ' ') s = s.slice(1);
  if (s.charAt(s.length - 1) === ' ') s = s.slice(0, -1);
  return s;
}

/* LA CLÉ D'UN TEXTE FRANÇAIS : aplani, puis chaque nombre devient « # ».
   « 46 juridictions selon 12 critères » est UNE phrase, pas quarante-six :
   un compteur que le JavaScript fait varier ne doit pas rendre la clé
   introuvable. Les chiffres d'origine reviennent par sentDigits. */
function sentNormaliser(s) {
  return sentAplanir(s).replace(SENT_CHIFFRES, '#');
}

/* LES CHIFFRES D'ORIGINE, RÉINJECTÉS DANS L'ORDRE dans la valeur anglaise.
   Rend null si les comptes ne concordent pas : une traduction qui n'a pas le
   même nombre de « # » que le français n'a pas le droit de s'afficher avec
   des chiffres déplacés — le français reste. Un « # » précédé de « & » est
   une entité HTML (&#39;), pas un emplacement. */
function sentDigits(cle_en, texte_fr) {
  var s = (cle_en === null || cle_en === undefined) ? '' : String(cle_en);
  var fr = (texte_fr === null || texte_fr === undefined) ? '' : String(texte_fr);
  var nombres = fr.match(SENT_CHIFFRES) || [];
  var sortie = '', n = 0;
  for (var k = 0; k < s.length; k++) {
    var c = s.charAt(k);
    if (c === '#' && (k === 0 || s.charAt(k - 1) !== '&')) {
      if (n >= nombres.length) return null;
      sortie += nombres[n++];
    } else {
      sortie += c;
    }
  }
  return n === nombres.length ? sortie : null;
}

function sentTagDe(el) {
  return String(el.tagName || el.nodeName || '').toLowerCase();
}

/* CE QUI RETIRE UN ÉLÉMENT — ET TOUT CE QU'IL CONTIENT — DU CORPS TRADUIT :
   une balise exclue, l'ancien régime (data-i18n reste maître chez lui), ou
   translate="no", que le HTML prévoit précisément pour cela. */
function sentPorteExclusion(el) {
  if (SENT_EXCLUS.indexOf(sentTagDe(el)) >= 0) return true;
  if (el.hasAttribute('data-i18n') || el.hasAttribute('data-i18n-bloc')) return true;
  if (el.getAttribute('translate') === 'no') return true;
  return false;
}

function sentAncetreExclu(el) {
  for (var p = el.parentNode; p && p.nodeType === 1; p = p.parentNode) {
    if (sentPorteExclusion(p)) return true;
  }
  return false;
}

/* TOUS LES DESCENDANTS SONT DE LA MISE EN FORME NUE — ou pas. On s'arrête au
   premier qui ne l'est pas : un conteneur avec un <div> se classe à son
   premier enfant, sans parcourir ses centaines de descendants. */
function sentToutInline(el) {
  var enfants = el.childNodes, vus = 0;
  for (var i = 0; i < enfants.length; i++) {
    var e = enfants[i];
    if (e.nodeType !== 1) continue;
    vus++;
    if (SENT_INLINE.indexOf(sentTagDe(e)) < 0) return false;
    if (e.attributes && e.attributes.length) return false;
    if (sentToutInline(e) === false) return false;
  }
  return vus > 0 ? true : null;
}

/* Le régime d'un élément SEUL, ses ancêtres étant déjà admis. */
function sentClasserIci(el) {
  if (sentPorteExclusion(el)) return 'exclu';
  return sentToutInline(el) === true ? 'bloc' : 'texte';
}

/* 'bloc' | 'texte' | 'exclu' — la règle commune à la traduction ET à
   l'inventaire, qui DOIVENT classer pareil : une clé relevée sous un régime
   et cherchée sous l'autre ne se retrouverait jamais. */
function sentClasser(el) {
  if (!el || el.nodeType !== 1) return 'exclu';
  if (sentAncetreExclu(el)) return 'exclu';
  return sentClasserIci(el);
}

/* LES ATTRIBUTS QUI PORTENT DU TEXTE LU : title, aria-label, placeholder,
   alt — et la valeur d'un bouton de formulaire, qui est son libellé. */
function sentAttributsDe(el) {
  var liste = SENT_ATTRIBUTS.slice();
  if (sentTagDe(el) === 'input') {
    var type = String(el.getAttribute('type') || '').toLowerCase();
    if (type === 'submit' || type === 'button' || type === 'reset') liste.push('value');
  }
  return liste;
}

function sentPageDe(el, courante) {
  var id = el.getAttribute('id') || '';
  var classes = ' ' + (el.getAttribute('class') || '') + ' ';
  if (id.indexOf('p-') === 0 && classes.indexOf(' page ') >= 0) return id.slice(2);
  return courante;
}

/* LE PARCOURS, UNIQUE, que la traduction et l'inventaire empruntent avec des
   gestes différents (`ctx`). C'est la garantie que les deux appliquent
   exactement les mêmes règles. */
function sentMarcher(el, ctx, page) {
  if (!el || el.nodeType !== 1) return;
  var tag = sentTagDe(el);
  if (SENT_MUETS.indexOf(tag) >= 0) return;
  if (el.hasAttribute('data-i18n') || el.hasAttribute('data-i18n-bloc')) return;
  if (el.getAttribute('translate') === 'no') return;
  page = sentPageDe(el, page);
  ctx.attrs(el, page);
  if (SENT_EXCLUS.indexOf(tag) >= 0) return;
  if (sentToutInline(el) === true) { ctx.bloc(el, page); return; }
  var enfants = el.childNodes;
  /* LA LISTE EST COPIÉE : traduire un bloc ou un texte ne change pas la
     liste des enfants, mais un gestionnaire de mutation tiers pourrait. */
  var copie = [];
  for (var i = 0; i < enfants.length; i++) copie.push(enfants[i]);
  for (var k = 0; k < copie.length; k++) {
    var n = copie[k];
    if (n.nodeType === 3) ctx.texte(n, el, page);
    else if (n.nodeType === 1) sentMarcher(n, ctx, page);
  }
}

/* ── L'INVENTAIRE ──────────────────────────────────────────────────────
   { bloc: {clé: {fr, html, pages: […]}}, texte: {clé: fr}, attr: {clé: fr} }
   — ce que l'outil du lot de traduction relève, avec EXACTEMENT les règles
   de la traduction, puisque c'est le même parcours. */
function sentInventaire(racine) {
  var inv = { bloc: {}, texte: {}, attr: {} };
  var ctx = {
    attrs: function (el) {
      var liste = sentAttributsDe(el);
      for (var i = 0; i < liste.length; i++) {
        var v = el.getAttribute(liste[i]);
        if (!v || !SENT_LETTRE.test(v)) continue;
        var cle = sentNormaliser(v);
        if (!(cle in inv.attr)) inv.attr[cle] = sentAplanir(v);
      }
    },
    bloc: function (el, page) {
      var tc = el.textContent;
      if (!SENT_LETTRE.test(tc)) return;
      var cle = sentNormaliser(tc);
      var ent = inv.bloc[cle];
      if (!ent) ent = inv.bloc[cle] = { fr: sentAplanir(tc), html: sentAplanir(el.innerHTML), pages: [] };
      if (page && ent.pages.indexOf(page) < 0) ent.pages.push(page);
    },
    texte: function (n) {
      var v = n.nodeValue;
      if (!v || !SENT_LETTRE.test(v)) return;
      var cle = sentNormaliser(v);
      if (!(cle in inv.texte)) inv.texte[cle] = sentAplanir(v);
    }
  };
  if (racine && racine.nodeType === 9) racine = racine.body || racine.documentElement;
  sentMarcher(racine, ctx, '');
  return inv;
}

/* ── LA MÉMOIRE DES ORIGINAUX ──────────────────────────────────────────
   nœud → { t: {fr, en} | h: {fr, en} | a: {nom: {fr, en}} }. Une WeakMap :
   un nœud que la page retire est oublié avec elle, rien ne fuit. */
var SENT_ORIG = (typeof WeakMap === 'function') ? new WeakMap() : {
  get: function (n) { return n.__sentOrig; },
  set: function (n, v) { n.__sentOrig = v; },
  'delete': function (n) { delete n.__sentOrig; }
};

function sentMemoire(n) {
  var rec = SENT_ORIG.get(n);
  if (!rec) { rec = {}; SENT_ORIG.set(n, rec); }
  return rec;
}

/* ── LES MOTIFS : les libellés composés ────────────────────────────────
   CE QU'UNE CLÉ EXACTE NE PEUT PAS COUVRIR. « Supprimer Chatbot service
   client du registre » est une phrase d'interface qui ENCADRE une donnée :
   il y a autant de clés que de systèmes au registre. La section « motif »
   du dictionnaire écrit la phrase une fois, la donnée en « {} » :
     "Supprimer {} du registre": "Delete {} from the register"
   « {} » capture un morceau quelconque, NON VIDE, recopié dans la
   traduction à la place du « {} » de même rang ; les « # » restent les
   chiffres et reviennent par sentDigits, dans l'ordre.

   LE MORCEAU CAPTURÉ EST RECOPIÉ TEL QUEL — SAUF s'il est lui-même une clé
   exacte du régime texte : « Bloc 1 sur 2 · Vue d'ensemble IA Act — … »
   encadre le NOM d'un bloc, qui est une phrase d'interface déjà traduite,
   et le recopier en français laisserait la moitié du libellé dans l'autre
   langue. Le nom d'un système saisi par l'utilisateur n'est pas une clé :
   il passe intact.

   UN MOTIF N'EST ESSAYÉ QUE SI LA CLÉ EXACTE MANQUE, et seulement dans le
   régime TEXTE et sur les attributs : un bloc est du HTML, et y recopier
   un morceau de texte brut le rendrait comme balisage.

   COMPILÉS UNE FOIS par dictionnaire reçu, essayés du PLUS LONG au plus
   court (à longueur égale, par ordre des clés) : l'ordre est déterministe,
   et le motif le plus précis gagne — « Étape # — {} · vous y êtes » passe
   avant « Étape # — {} · {} ». Un motif sans aucun caractère hors de ses
   « {} » attraperait tout : il est écarté (sentinel_i18n.py le refuse
   aussi, et le nomme). */
var SENT_TROU = '{}';
var SENT_MOTIFS_VUS = { source: null, liste: [] };

function sentEchapperRe(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function sentMotifsCompiler(motifs) {
  if (!motifs || typeof motifs !== 'object') return [];
  if (SENT_MOTIFS_VUS.source === motifs) return SENT_MOTIFS_VUS.liste;
  var cles = [];
  for (var k in motifs) {
    if (Object.prototype.hasOwnProperty.call(motifs, k) && typeof motifs[k] === 'string') cles.push(k);
  }
  cles.sort(function (a, b) {
    if (a.length !== b.length) return b.length - a.length;
    return a < b ? -1 : (a > b ? 1 : 0);
  });
  var liste = [];
  for (var i = 0; i < cles.length; i++) {
    var morceaux = cles[i].split(SENT_TROU);
    if (!/\S/.test(morceaux.join(''))) continue;
    if (motifs[cles[i]].split(SENT_TROU).length !== morceaux.length) continue;
    /* L'INDICE : le plus long morceau fixe, cherché par indexOf avant
       toute expression — un texte qui ne le contient pas ne coûte rien. */
    var indice = '';
    for (var j = 0; j < morceaux.length; j++) if (morceaux[j].length > indice.length) indice = morceaux[j];
    var re = [];
    for (var m = 0; m < morceaux.length; m++) re.push(sentEchapperRe(morceaux[m]));
    liste.push({ cle: cles[i], en: motifs[cles[i]], indice: indice,
                 re: new RegExp('^' + re.join('(.+?)') + '$') });
  }
  SENT_MOTIFS_VUS = { source: motifs, liste: liste };
  return liste;
}

/* LA VALEUR ANGLAISE D'UNE CLÉ PAR LES MOTIFS — encore avec ses « # » —,
   ou null si aucun ne s'applique. */
function sentMotifTraduire(cle, d) {
  var liste = d.motifs || [];
  for (var i = 0; i < liste.length; i++) {
    var m = liste[i];
    if (cle.indexOf(m.indice) < 0) continue;
    var r = m.re.exec(cle);
    if (!r) continue;
    var morceaux = m.en.split(SENT_TROU), sortie = morceaux[0];
    for (var k = 1; k < morceaux.length; k++) {
      var capte = r[k];
      var t = Object.prototype.hasOwnProperty.call(d.texte, capte) ? d.texte[capte] : null;
      sortie += (typeof t === 'string' ? t : capte) + morceaux[k];
    }
    return sortie;
  }
  return null;
}

/* LA TRADUCTION D'UNE CLÉ DU RÉGIME TEXTE : l'entrée exacte d'abord, les
   motifs ensuite. */
function sentChercherTexte(cle, d) {
  var t = d.texte[cle];
  if (t !== undefined && t !== null) return t;
  return sentMotifTraduire(cle, d);
}

function sentAttrsAppliquer(el, dico) {
  var liste = sentAttributsDe(el), compte = 0;
  for (var i = 0; i < liste.length; i++) {
    var nom = liste[i], v = el.getAttribute(nom);
    if (!v || !SENT_LETTRE.test(v)) continue;
    var rec = SENT_ORIG.get(el);
    if (rec && rec.a && rec.a[nom] && rec.a[nom].en === v) continue;  /* déjà traduit */
    var t = sentChercherTexte(sentNormaliser(v), dico);
    if (t === undefined || t === null) continue;
    var val = sentDigits(t, v);
    if (val === null || val === v) continue;
    el.setAttribute(nom, val);
    rec = sentMemoire(el);
    if (!rec.a) rec.a = {};
    rec.a[nom] = { fr: v, en: val };
    compte++;
  }
  return compte;
}

/* LE SEUL ENDROIT QUI ÉCRIT innerHTML — sur un élément que sentToutInline a
   reconnu comme de la mise en forme nue, et rien d'autre. */
function sentBlocAppliquer(el, dico) {
  var courant = el.innerHTML;
  var rec = SENT_ORIG.get(el);
  if (rec && rec.h && rec.h.en === courant) return 0;  /* déjà traduit */
  var tc = el.textContent;
  if (!SENT_LETTRE.test(tc)) return 0;
  var t = dico.bloc[sentNormaliser(tc)];
  if (t === undefined || t === null) return 0;
  var val = sentDigits(t, tc);
  if (val === null || val === courant) return 0;
  el.innerHTML = val;
  rec = sentMemoire(el);
  /* CE QUE LE NAVIGATEUR A GARDÉ, pas ce qu'on lui a donné : la
     sérialisation peut différer de la chaîne écrite (entités, guillemets),
     et c'est à ELLE que la passe suivante comparera. */
  rec.h = { fr: courant, en: el.innerHTML };
  return 1;
}

function sentTexteAppliquer(n, dico) {
  var v = n.nodeValue;
  if (!v || !SENT_LETTRE.test(v)) return 0;
  var rec = SENT_ORIG.get(n);
  if (rec && rec.t && rec.t.en === v) return 0;  /* déjà traduit */
  var t = sentChercherTexte(sentNormaliser(v), dico);
  if (t === undefined || t === null) return 0;
  var val = sentDigits(t, v);
  if (val === null) return 0;
  /* LES BLANCS DE TÊTE ET DE QUEUE SONT CONSERVÉS : « consultez le <a> »
     perd son espace avant le lien si on l'oublie, et deux mots se collent. */
  var m = v.match(/^([\s\u00a0\ufeff]*)([\s\S]*?)([\s\u00a0\ufeff]*)$/);
  val = m[1] + val + m[3];
  if (val === v) return 0;
  n.nodeValue = val;
  rec = sentMemoire(n);
  rec.t = { fr: v, en: val };
  return 1;
}

/* LA RESTITUTION parcourt TOUT, sans exclusion : elle ne cherche que ce que
   la traduction a mémorisé, et ne restitue que si la valeur courante est
   encore la traduction — ce que le JavaScript a réécrit entre-temps est
   plus récent, et reste. */
function sentBlocRestituer(el, rec) {
  if (el.innerHTML === rec.h.en) { el.innerHTML = rec.h.fr; return 1; }
  return 0;
}

function sentRestituer(n) {
  var compte = 0;
  if (n.nodeType === 3) {
    var rt = SENT_ORIG.get(n);
    if (rt && rt.t) {
      if (n.nodeValue === rt.t.en) { n.nodeValue = rt.t.fr; compte++; }
      SENT_ORIG['delete'](n);
    }
    return compte;
  }
  if (n.nodeType !== 1) return 0;
  var rec = SENT_ORIG.get(n);
  if (rec) {
    if (rec.a) {
      for (var nom in rec.a) {
        if (rec.a.hasOwnProperty(nom) && n.getAttribute(nom) === rec.a[nom].en) {
          n.setAttribute(nom, rec.a[nom].fr); compte++;
        }
      }
    }
    if (rec.h) compte += sentBlocRestituer(n, rec);
    SENT_ORIG['delete'](n);
  }
  var enfants = n.childNodes, copie = [];
  for (var i = 0; i < enfants.length; i++) copie.push(enfants[i]);
  for (var k = 0; k < copie.length; k++) compte += sentRestituer(copie[k]);
  return compte;
}

/* APPLIQUE (langue 'en', avec `dico` = {texte, bloc, motif}) OU RESTITUE (toute
   autre langue) sous `racine` — un élément, un document, ou un nœud texte
   (on remonte alors à son parent, parce que le régime est celui du parent).
   Rend le nombre de nœuds et d'attributs écrits. */
function sentTraduireCorps(racine, dico, langue) {
  if (!racine) return 0;
  if (racine.nodeType === 3) racine = racine.parentNode;
  if (racine && racine.nodeType === 9) racine = racine.body || racine.documentElement;
  if (!racine || racine.nodeType !== 1) return 0;
  if (langue !== 'en') return sentRestituer(racine);
  if (!dico) return 0;
  var d = { texte: dico.texte || {}, bloc: dico.bloc || {},
            motifs: sentMotifsCompiler(dico.motif) };
  if (sentAncetreExclu(racine)) return 0;
  var compte = 0;
  sentMarcher(racine, {
    attrs: function (el) { compte += sentAttrsAppliquer(el, d); },
    bloc: function (el) { compte += sentBlocAppliquer(el, d); },
    texte: function (n) { compte += sentTexteAppliquer(n, d); }
  }, '');
  return compte;
}

/* ══ LE BRANCHEMENT D'UN DOCUMENT ═════════════════════════════════════════
 *
 * CE QUI VIVAIT DANS sentinel.page.js, ET POURQUOI IL EST ICI. Le
 * téléchargement paresseux du dictionnaire, l'application au corps et
 * l'observateur des rendus différés étaient écrits pour LE document de
 * Sentinel. Mesuré au navigateur (i18n/sentinel/MESURE_APRES.json) : les
 * cinq pages que Sentinel embarque en cadre — la carte, le panorama,
 * l'enveloppe, l'empreinte du parc, l'observatoire — restaient à 98 % en
 * français en anglais, parce que ce sont d'AUTRES documents et que rien de
 * tout cela n'y était chargé. Recopier le bloc dans chacun aurait fait six
 * exemplaires de la même mécanique, dont un finit toujours par diverger ;
 * il est donc ici, une fois, et Sentinel comme ses cadres le branchent.
 *
 * sentBrancher(doc, { langue: function () → 'fr' | 'en', url }) rend un
 * branchement : appliquer() suit la langue que `langue()` dit AU MOMENT DE
 * L'APPEL — et encore à l'arrivée du dictionnaire, qui peut avoir changé
 * entre-temps. Le reste est l'ancienne mécanique de sentinel.page.js, à
 * l'identique :
 *   · PARESSEUX — le dictionnaire n'est téléchargé qu'à la première
 *     demande d'anglais ; un lecteur français ne paie rien ; un échec n'est
 *     pas définitif, la demande suivante réessaie ;
 *   · VIVANT — un MutationObserver, actif en anglais SEULEMENT, traduit ce
 *     que le JavaScript rend après coup : une passe par image, sur les seuls
 *     sous-arbres touchés, nos propres écritures retirées de la file
 *     (takeRecords) — pas de boucle. */
var SENT_DICO_URL = '/sentinel.en.json';
var SENT_LANGUE_CLE = 'cp-sentinel-langue-v1';
var SENT_MESSAGE = 'cp-sentinel-langue';

function sentBrancher(doc, options) {
  options = options || {};
  var b = {
    doc: doc,
    url: options.url || SENT_DICO_URL,
    langue: (typeof options.langue === 'function') ? options.langue : function () { return 'fr'; },
    dico: null,       /* le dictionnaire {texte, bloc, motif}, une fois reçu */
    attente: null,    /* le téléchargement en cours, pour ne pas le doubler */
    obs: null,        /* l'observateur, non nul en anglais seulement */
    prevu: false,     /* une passe différée est déjà programmée */
    cibles: []        /* les sous-arbres touchés depuis la dernière passe */
  };

  b.charger = function () {
    if (b.dico) return Promise.resolve(b.dico);
    if (b.attente) return b.attente;
    if (typeof fetch !== 'function') return Promise.resolve(null);
    b.attente = fetch(b.url, { credentials: 'same-origin' })
      .then(function (r) {
        if (!r.ok) throw new Error('sentinel.en.json : HTTP ' + r.status);
        return r.json();
      })
      .then(function (d) {
        b.dico = { texte: (d && d.texte) || {}, bloc: (d && d.bloc) || {},
                   motif: (d && d.motif) || {} };
        return b.dico;
      })
      ['catch'](function () {
        /* UN ÉCHEC N'EST PAS DÉFINITIF : la prochaine demande d'anglais
           réessaiera. D'ici là, le corps reste en français — l'état d'avant
           ce module, pas une page cassée. */
        b.attente = null;
        return null;
      });
    return b.attente;
  };

  /* OUBLIER le dictionnaire reçu : la prochaine demande d'anglais le
     retélécharge. C'est le chemin du réessai, et celui de la recette. */
  b.oublier = function () { b.dico = null; b.attente = null; };

  b.appliquer = function () {
    if (!b.doc || !b.doc.body) return;
    if (b.langue() === 'en') {
      if (!b.dico) {
        /* UN TÉLÉCHARGEMENT DÉJÀ EN COURS SUFFIT : il appliquera le corps en
           arrivant. Lui accrocher une seconde suite ferait parcourir le
           document deux fois pour le même résultat. */
        if (b.attente) return;
        b.charger().then(function (d) {
          /* LA LANGUE A PU CHANGER PENDANT LE TÉLÉCHARGEMENT : on n'écrit de
             l'anglais que si l'anglais est encore demandé. */
          if (d && b.langue() === 'en') b.appliquer();
        });
        return;
      }
      sentTraduireCorps(b.doc.body, b.dico, 'en');
      b.observer(true);
      return;
    }
    b.observer(false);
    sentTraduireCorps(b.doc.body, null, 'fr');
  };

  b.passe = function () {
    b.prevu = false;
    var lot = b.cibles;
    b.cibles = [];
    if (b.langue() !== 'en' || !b.dico || !b.obs) return;
    for (var k = 0; k < lot.length; k++) {
      var cible = lot[k];
      if (!b.doc.body.contains(cible)) continue;
      /* UN SOUS-ARBRE CONTENU DANS UN AUTRE DU MÊME LOT est parcouru avec
         lui : une passe, pas deux. */
      var couvert = false;
      for (var j = 0; j < lot.length; j++) {
        if (j !== k && lot[j] !== cible && lot[j].contains(cible)) { couvert = true; break; }
      }
      if (!couvert) sentTraduireCorps(cible, b.dico, 'en');
    }
    /* NOS PROPRES ÉCRITURES NE SONT PAS DES MUTATIONS À TRADUIRE. */
    b.obs.takeRecords();
  };

  b.observer = function (actif) {
    if (typeof MutationObserver !== 'function') return;
    if (!actif) {
      if (b.obs) { b.obs.disconnect(); b.obs = null; }
      b.cibles = [];
      return;
    }
    if (b.obs) return;
    b.obs = new MutationObserver(function (records) {
      for (var i = 0; i < records.length; i++) {
        var t = records[i].target;
        if (t && t.nodeType === 3) t = t.parentNode;
        if (t && b.cibles.indexOf(t) < 0) b.cibles.push(t);
      }
      if (b.prevu) return;
      b.prevu = true;
      if (typeof requestAnimationFrame === 'function') requestAnimationFrame(b.passe);
      else setTimeout(b.passe, 16);
    });
    b.obs.observe(b.doc.body, { childList: true, subtree: true, characterData: true });
  };

  return b;
}

/* ── LES CADRES ───────────────────────────────────────────────────────────
 * SENTINEL PRÉVIENT SES CADRES quand la langue change : un message à chaque
 * <iframe> du document, adressé à SA PROPRE origine — un cadre d'une autre
 * origine ne le reçoit pas. Le cadre écoute aussi l'événement `storage`
 * (la langue est mémorisée sous la même clé) : l'un suffit, l'autre couvre
 * un stockage bloqué ou une page ouverte seule dans un autre onglet. */
function sentPrevenirCadres(doc, langue) {
  var cadres = doc.getElementsByTagName('iframe'), n = 0;
  var origine = doc.location && doc.location.origin;
  for (var i = 0; i < cadres.length; i++) {
    try {
      cadres[i].contentWindow.postMessage({ type: SENT_MESSAGE, langue: langue }, origine);
      n++;
    } catch (e) { /* un cadre pas encore né, ou d'une autre origine */ }
  }
  return n;
}

/* UN DOCUMENT EMBARQUÉ SE BRANCHE LUI-MÊME. Chargé par
 *   <script src="/sentinel.i18n.js" data-sent-cadre defer></script>
 * il lit la langue — celle de Sentinel s'il est dans son cadre, sinon la
 * langue mémorisée — et traduit son corps si c'est l'anglais. EN FRANÇAIS,
 * RIEN NE CHANGE : pas de téléchargement, pas d'observateur, pas une
 * écriture dans le document ; seuls deux écouteurs attendent qu'on leur
 * dise autre chose. */
function sentCadreLangue(win) {
  /* LE PARENT FAIT FOI QUAND IL EST SENTINEL ET QU'IL A DÉJÀ DÉCIDÉ :
     sa variable SENT_LANG est la langue affichée. Avant l'exécution de son
     script (le cadre peut charger plus tôt), elle n'existe pas encore, et
     la langue mémorisée — que Sentinel lit aussi — prend le relais. */
  try {
    if (win.parent && win.parent !== win) {
      var l = win.parent.SENT_LANG;
      if (l === 'en' || l === 'fr') return l;
    }
  } catch (e) { /* parent d'une autre origine : il ne dit rien */ }
  try {
    return win.localStorage.getItem(SENT_LANGUE_CLE) === 'en' ? 'en' : 'fr';
  } catch (e2) {
    return 'fr';
  }
}

function sentCadreDemarrer(win) {
  var doc = win.document, courante = 'fr';
  var langOrigine = doc.documentElement.getAttribute('lang');
  var b = sentBrancher(doc, { langue: function () { return courante; } });
  var poser = function (l) {
    l = (l === 'en') ? 'en' : 'fr';
    if (l === courante) return;
    courante = l;
    if (l === 'en') doc.documentElement.setAttribute('lang', 'en');
    else if (langOrigine === null) doc.documentElement.removeAttribute('lang');
    else doc.documentElement.setAttribute('lang', langOrigine);
    b.appliquer();
  };
  win.addEventListener('storage', function (e) {
    if (e.key === SENT_LANGUE_CLE || e.key === null) poser(sentCadreLangue(win));
  });
  win.addEventListener('message', function (e) {
    if (e.source !== win.parent || e.origin !== win.location.origin) return;
    var d = e.data;
    if (d && d.type === SENT_MESSAGE) poser(d.langue);
  });
  poser(sentCadreLangue(win));
  win.SENT_CADRE = b;
  return b;
}

if (typeof document !== 'undefined' && document.currentScript
    && document.currentScript.hasAttribute('data-sent-cadre')) {
  sentCadreDemarrer(window);
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    SENT_INLINE: SENT_INLINE, SENT_EXCLUS: SENT_EXCLUS, SENT_ATTRIBUTS: SENT_ATTRIBUTS,
    sentAplanir: sentAplanir, sentNormaliser: sentNormaliser, sentDigits: sentDigits,
    sentClasser: sentClasser, sentInventaire: sentInventaire,
    sentTraduireCorps: sentTraduireCorps, SENT_ORIG: SENT_ORIG,
    sentMotifsCompiler: sentMotifsCompiler, sentBrancher: sentBrancher,
    sentPrevenirCadres: sentPrevenirCadres, sentCadreLangue: sentCadreLangue,
    sentCadreDemarrer: sentCadreDemarrer, SENT_LANGUE_CLE: SENT_LANGUE_CLE
  };
}
