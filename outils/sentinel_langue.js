/* ══ DANS QUELLE LANGUE EST CE TEXTE ? — l'heuristique de la mesure ═══════
 *
 * POURQUOI UNE HEURISTIQUE, ET PAS UN DICTIONNAIRE. La recette
 * recette_sentinel_langue.js relève, dans un vrai navigateur, tout ce qui
 * est VISIBLE quand EN est choisi, et doit dire de chaque texte s'il est
 * resté en français. Comparer au dictionnaire ne suffirait pas : un texte
 * que le JavaScript rend et que l'inventaire n'a pas vu n'est dans aucun
 * dictionnaire, et c'est précisément lui qu'on veut compter. Le classement
 * se fait donc SUR LE TEXTE LUI-MÊME, par des signaux explicites, chacun
 * nommé ici et éprouvé dans tests/test_sentinel_langue_mesure.py.
 *
 * LES SIGNAUX, PAR ORDRE DE FORCE :
 *   1. une chaîne sans lettre est NEUTRE (« 12 % », « — », « 2024 ») ;
 *   2. un nom propre de la liste, SEUL, est neutre (« EU AI Act »,
 *      « ISO 42001 », « Sentinel AI ») : il ne se traduit pas, il ne compte
 *      dans aucune langue ;
 *   3. chaque mot-outil de la liste française compte un point français,
 *      chaque mot-outil anglais un point anglais ;
 *   4. un mot à lettre ACCENTUÉE compte un point français : l'anglais n'en
 *      a pas, et c'est le signal le plus sûr sur un mot isolé (« Coûts ») ;
 *   5. une élision française (l', d', qu', n'…) compte un point français ;
 *      une contraction anglaise ('s, 't, 're…) un point anglais ;
 *   6. une terminaison propre à l'une des deux langues compte un point
 *      (« -ique », « -eur » ; « -ing », « -ly ») — jamais celles que les
 *      deux partagent (« -tion », « -ment »).
 * Le texte est FRANÇAIS si les points français l'emportent, ANGLAIS si les
 * points anglais l'emportent, NEUTRE à égalité — y compris zéro partout :
 * « Budget », « Score » ou « Dashboard » ne trahissent rien, et les compter
 * d'un côté serait mentir.
 *
 * CE QUE L'HEURISTIQUE CLASSE MAL, MESURÉ ET ASSUMÉ : « on » est anglais
 * pour elle (préposition) alors que c'est aussi un pronom français ; un
 * anglicisme du français (« reporting », « monitoring ») marque un point
 * anglais ; un libellé d'un ou deux mots sans mot-outil ni accent
 * (« Modules certifiants », « Dashboard ») est neutre, donc absent du
 * score. Le score d'une page — mots français / (français + anglais) — ne
 * porte que sur ce qu'elle a su décider ; les mots neutres sont comptés à
 * part, pour qu'on voie combien elle ignore.
 *
 * MÊME MODULE POUR LA RECETTE ET POUR LES RÈGLES : les tests exécutent CE
 * fichier sous node, pas une copie de ses listes. */
'use strict';

/* LES MOTS-OUTILS DE LA CONCEPTION, puis ceux que la mesure sur Sentinel a
   fait ajouter (« en », « il », « tous »…) — sans jamais un mot qui existe
   dans les deux langues : « a » (il a / a book), « an » (par an / an
   audit), « plus » (en plus / plus) sont laissés dehors. Le vocabulaire
   d'interface (« Voir », « Chargement », « Retour ») est là parce qu'un
   bouton d'un seul mot n'a ni mot-outil ni accent pour se trahir. */
var MOTS_FR = ['le', 'la', 'les', 'des', 'une', 'un', 'et', 'est', 'pour',
               'dans', 'avec', 'sur', 'par', 'pas', 'vous', 'votre', 'cette',
               'ce', 'sont', 'au', 'aux', 'du', 'être', 'ou', 'qui', 'que',
               'ne', 'se',
               'de', 'en', 'il', 'elle', 'ils', 'elles', 'nous', 'vos', 'notre',
               'nos', 'son', 'sa', 'ses', 'mes', 'leur', 'leurs', 'tout',
               'tous', 'toutes', 'sans', 'sous', 'entre', 'vers', 'comme',
               'mais', 'donc', 'chaque', 'selon', 'depuis', 'puis', 'aussi',
               'ici', 'encore', 'aucun', 'aucune', 'ni', 'cet', 'ces',
               'voir', 'chargement', 'retour', 'accueil', 'oui', 'non',
               'fermer', 'ouvrir', 'suivant', 'valider', 'annuler',
               'exporter', 'nouveau', 'lire', 'afficher', 'masquer'];
var MOTS_EN = ['the', 'and', 'of', 'to', 'is', 'for', 'with', 'on', 'in',
               'are', 'this', 'that', 'your', 'be', 'by', 'as', 'at', 'from',
               'or', 'which', 'not', 'it',
               'we', 'you', 'our', 'their', 'its', 'these', 'those', 'has',
               'have', 'was', 'were', 'will', 'can', 'all', 'if', 'when',
               'each', 'into', 'than', 'more', 'most', 'also', 'but', 'so',
               'then', 'any', 'there', 'here', 'how', 'what', 'who', 'only',
               'new', 'no', 'yes',
               'view', 'loading', 'back', 'home', 'close', 'open', 'next',
               'previous', 'save', 'cancel', 'export', 'none', 'read',
               'show', 'hide'];
/* LES NOMS PROPRES qui ne se traduisent pas et ne comptent pour aucune
   langue. Les plus longs d'abord : « EU AI Act » doit être retiré avant que
   « AI » ne le soit. */
var NOMS_PROPRES = ['EU AI Act', 'NIST AI RMF', 'OWASP LLM', 'AI Act', 'NIS 2',
                    'NIS2', 'ISO/IEC', 'DORA', 'CRA', 'ReCyF', 'ISO', 'IEC',
                    'NIST', 'OWASP', 'EBIOS', 'ANSSI', 'CNIL', 'Sentinel',
                    'CONSEILPREV', 'AI'];
/* LES TERMINAISONS PROPRES À UNE LANGUE. Pas « -tion », « -ment », « -able »,
   « -ent » : les deux langues les ont. */
var FINALES_FR = /(ique|iques|eur|eurs|euse|euses|aire|aires|elle|elles|ez|ais|ait|aient|eux|ée|ées|és)$/;
var FINALES_EN = /(ing|ings|ly|ness|ship|ships|ful|ized|ised)$/;
var ELISION_FR = /^(l|d|qu|n|s|c|j|m|t)['’]/i;
var CONTRACTION_EN = /['’](s|t|re|ve|ll|d|m)$/i;
var LETTRE = /[A-Za-zÀ-ÖØ-öø-ÿŒœ]/;
var ACCENT = /[À-ÖØ-öø-ÿŒœ]/;
var MOT = /[A-Za-zÀ-ÖØ-öø-ÿŒœ]+(?:['’][A-Za-zÀ-ÖØ-öø-ÿŒœ]+)*/g;
/* Un mot commence et finit hors lettre : « ISO » n'est pas retiré de
   « ISOLÉ », ni « CRA » de « CRAINTE ». */
var NOMS_RE = new RegExp('(^|[^A-Za-zÀ-ÿ])(' + NOMS_PROPRES.map(function (n) {
  return n.replace(/[.*+?^${}()|[\]\\\/]/g, '\\$&');
}).join('|') + ')(?![A-Za-zÀ-ÿ])', 'g');

function compterMots(texte) {
  var t = (texte === null || texte === undefined) ? '' : String(texte);
  return (t.match(MOT) || []).length;
}

/* { langue: 'fr' | 'en' | 'neutre', mots, fr, en } — `fr` et `en` sont les
   points, gardés pour que la recette puisse dire POURQUOI un texte a été
   classé comme il l'a été. `mots` ne compte pas les noms propres : « ISO »
   n'est un mot d'aucune langue, et n'a rien à faire dans un score. */
function classer(texte) {
  var t = (texte === null || texte === undefined) ? '' : String(texte);
  if (!LETTRE.test(t)) return { langue: 'neutre', mots: 0, fr: 0, en: 0 };
  var reste = t.replace(NOMS_RE, '$1 ');
  var mots = compterMots(reste);
  if (!LETTRE.test(reste)) return { langue: 'neutre', mots: 0, fr: 0, en: 0 };
  var fr = 0, en = 0;
  var jetons = reste.match(MOT) || [];
  for (var i = 0; i < jetons.length; i++) {
    var j = jetons[i], bas = j.toLowerCase();
    if (ELISION_FR.test(j)) { fr++; bas = bas.replace(ELISION_FR, ''); }
    else if (CONTRACTION_EN.test(j)) { en++; bas = bas.replace(CONTRACTION_EN, ''); }
    if (MOTS_FR.indexOf(bas) >= 0) { fr++; continue; }
    if (MOTS_EN.indexOf(bas) >= 0) { en++; continue; }
    if (ACCENT.test(bas)) { fr++; continue; }
    if (FINALES_FR.test(bas)) { fr++; continue; }
    if (FINALES_EN.test(bas)) { en++; continue; }
  }
  var langue = fr > en ? 'fr' : (en > fr ? 'en' : 'neutre');
  return { langue: langue, mots: mots, fr: fr, en: en };
}

/* ── L'AGRÉGATION : des relevés au JSON de mesure ─────────────────────────
   `releves` = { pages: { id: [ {t, ou} … ] }, coquille: [ {t, ou} … ] }
   où `t` est le texte visible et `ou` sa provenance ('texte', 'title',
   'aria-label', 'placeholder', 'value', 'option'), éventuellement préfixée
   par « cadre: » (un iframe de même origine) et par « donnee: » (un élément
   sous translate="no"). Chaque OCCURRENCE compte : un « Voir » répété vingt
   fois est vingt mots lus. La liste des restes, elle, est dédoublonnée :
   c'est une liste de travail pour qui traduit.

   DEUX LOTS SORTENT DU RANG, ET PAS DE LA MÊME MANIÈRE :

   · LES DONNÉES SAISIES (« donnee: ») — le nom d'un système au registre, son
     fournisseur, sa finalité, le nom d'un client. Elles sont relevées À PART
     et N'ENTRENT PAS dans la part française qui rend le verdict : ce sont
     les systèmes d'IA du client, écrits dans SA langue, et personne ne les
     traduit — c'est ce que déclare translate="no" dans la page. Leur volume
     est dit, pour qu'on ne croie jamais qu'elles ont disparu de la mesure.
     MESURÉ : sans cette séparation, 57 255 des 70 061 mots français relevés
     — 82 % — étaient des entrées de registre réaffichées des milliers de
     fois, et aucun seuil n'était atteignable.

   · LES CADRES (« cadre: ») — les cinq documents que Sentinel embarque en
     iframe. Ils ENTRENT DÉSORMAIS DANS LE VERDICT : depuis qu'ils chargent
     sentinel.i18n.js (data-sent-cadre), ils se traduisent par la même
     mécanique que Sentinel, et les tenir dehors reviendrait à ne pas
     regarder un cinquième de ce qu'un lecteur voit. Ils restent comptés à
     part, en plus, parce qu'une page qui régresse doit se nommer. */
var RESTES_MAX = 15;

/* LE MARQUEUR D'UNE DONNÉE SAISIE, posé par le relevé navigateur en tête de
   la provenance. Il peut suivre « cadre: » — une donnée s'affiche aussi dans
   un cadre. */
var MARQUE_DONNEE = 'donnee:';
var MARQUE_CADRE = 'cadre:';

function estDonnee(e) {
  return String((e || {}).ou || '').indexOf(MARQUE_DONNEE) >= 0;
}

function estCadre(e) {
  return String((e || {}).ou || '').indexOf(MARQUE_CADRE) === 0;
}

function mesurerLot(entrees) {
  var m = { mots_fr: 0, mots_en: 0, mots_neutres: 0, textes: 0, part_fr: null, restes: [] };
  var vus = {};
  for (var i = 0; i < (entrees || []).length; i++) {
    var e = entrees[i] || {};
    var t = (e.t === null || e.t === undefined) ? '' : String(e.t);
    var c = classer(t);
    m.textes++;
    if (c.langue === 'fr') {
      m.mots_fr += c.mots;
      var cle = (e.ou || 'texte') + '\u0000' + t;
      if (!vus[cle]) { vus[cle] = true; m.restes.push({ texte: t, mots: c.mots, ou: e.ou || 'texte' }); }
    } else if (c.langue === 'en') m.mots_en += c.mots;
    else m.mots_neutres += c.mots;
  }
  var decide = m.mots_fr + m.mots_en;
  m.part_fr = decide ? Math.round(m.mots_fr / decide * 10000) / 10000 : null;
  /* LES PLUS LONGS D'ABORD : c'est ce qui pèse dans le score, et ce qu'une
     personne qui traduit veut voir en premier. */
  m.restes.sort(function (a, b) { return b.mots - a.mots || b.texte.length - a.texte.length; });
  m.restes = m.restes.slice(0, RESTES_MAX);
  return m;
}

/* LE PARTAGE D'UN LOT DE RELEVÉS EN TROIS : ce qui rend le verdict (les
   textes de site, CADRES COMPRIS), les cadres seuls (pour les dire à part) et
   les données saisies (hors verdict). Une donnée affichée DANS un cadre est
   une donnée d'abord : elle ne se traduit pas plus là qu'ailleurs. */
function trier(entrees) {
  var out = { verdict: [], cadres: [], donnees: [] };
  for (var i = 0; i < (entrees || []).length; i++) {
    var e = entrees[i];
    if (estDonnee(e)) { out.donnees.push(e); continue; }
    out.verdict.push(e);
    if (estCadre(e)) out.cadres.push(e);
  }
  return out;
}

function vide() {
  return { mots_fr: 0, mots_en: 0, mots_neutres: 0, textes: 0, pages: 0, part_fr: null };
}

function cumuler(total, lot) {
  total.pages++;
  total.mots_fr += lot.mots_fr; total.mots_en += lot.mots_en;
  total.mots_neutres += lot.mots_neutres; total.textes += lot.textes;
}

function clore(total) {
  var decide = total.mots_fr + total.mots_en;
  total.part_fr = decide ? Math.round(total.mots_fr / decide * 10000) / 10000 : null;
  return total;
}

function agreger(releves, options) {
  options = options || {};
  var coq = trier((releves && releves.coquille) || []);
  var out = {
    _quoi: 'Ce qui reste en français, à l\'écran, quand EN est choisi — mesuré par recette_sentinel_langue.js. '
      + 'part_fr = mots français / (mots français + mots anglais) ; les mots neutres (sans lettre, nom propre, indécis) sont comptés à part. '
      + 'Les DONNÉES SAISIES (éléments translate="no" : noms de systèmes, fournisseurs, finalités, clients) sont relevées à part, '
      + 'dans « donnees », et n\'entrent PAS dans le verdict : elles sont écrites dans la langue du client et personne ne les traduit. '
      + 'Les cadres (iframes) sont comptés à part ET compris dans le verdict, depuis qu\'ils se traduisent eux-mêmes.',
    date: options.date || new Date().toISOString(),
    base: options.base || null,
    seuil: (options.seuil === undefined || options.seuil === null) ? SEUIL_DEFAUT : options.seuil,
    dictionnaire: options.dictionnaire || null,
    global: { mots_fr: 0, mots_en: 0, mots_neutres: 0, textes: 0, pages: 0, part_fr: null },
    coquille: mesurerLot(coq.verdict),
    pages: {}
  };
  if (coq.donnees.length) out.coquille.donnees = mesurerLot(coq.donnees);
  var pages = (releves && releves.pages) || {};
  var ids = Object.keys(pages);
  var cadres = vide();
  var donnees = vide();
  for (var i = 0; i < ids.length; i++) {
    var part = trier(pages[ids[i]] || []);
    var m = mesurerLot(part.verdict);
    out.pages[ids[i]] = m;
    out.global.pages++;
    /* LES CADRES : dans le verdict avec le reste de la page, ET dits à part. */
    if (part.cadres.length) {
      m.cadres = mesurerLot(part.cadres);
      cumuler(cadres, m.cadres);
    }
    /* LES DONNÉES SAISIES : hors du verdict, mais jamais tues. */
    if (part.donnees.length) {
      m.donnees = mesurerLot(part.donnees);
      cumuler(donnees, m.donnees);
    }
  }
  out.cadres = clore(cadres);
  out.donnees = clore(donnees);
  var lots = ids.map(function (id) { return out.pages[id]; }).concat([out.coquille]);
  for (var k = 0; k < lots.length; k++) {
    out.global.mots_fr += lots[k].mots_fr;
    out.global.mots_en += lots[k].mots_en;
    out.global.mots_neutres += lots[k].mots_neutres;
    out.global.textes += lots[k].textes;
  }
  var decide = out.global.mots_fr + out.global.mots_en;
  out.global.part_fr = decide ? Math.round(out.global.mots_fr / decide * 10000) / 10000 : null;
  return out;
}

/* LES PAGES LES PLUS FRANÇAISES : par part française, puis par masse de
   mots français — deux pages à 100 % se départagent par ce qu'il reste à
   traduire. Une page sans mot décidé (part nulle) vient en dernier. */
function pires(mesure, n) {
  var ids = Object.keys((mesure && mesure.pages) || {});
  ids.sort(function (a, b) {
    var pa = mesure.pages[a].part_fr, pb = mesure.pages[b].part_fr;
    if (pa === null && pb === null) return 0;
    if (pa === null) return 1;
    if (pb === null) return -1;
    return (pb - pa) || (mesure.pages[b].mots_fr - mesure.pages[a].mots_fr);
  });
  return ids.slice(0, n === undefined ? 10 : n).map(function (id) {
    var p = mesure.pages[id];
    return { page: id, part_fr: p.part_fr, mots_fr: p.mots_fr, mots_en: p.mots_en, mots_neutres: p.mots_neutres };
  });
}

var SEUIL_DEFAUT = 0.05;

/* 1 si la part française globale DÉPASSE le seuil, 0 sinon — « dépasse »,
   strictement : un seuil à 0 avec zéro mot français passe. Une mesure sans
   aucun mot décidé n'a rien à dire et passe aussi. */
function verdict(mesure, seuil) {
  var s = (seuil === undefined || seuil === null) ? SEUIL_DEFAUT : Number(seuil);
  var part = mesure && mesure.global ? mesure.global.part_fr : null;
  if (part === null || part === undefined) return 0;
  return part > s ? 1 : 0;
}

function pct(x) { return x === null || x === undefined ? '  —  ' : (x * 100).toFixed(1) + ' %'; }

function resumer(mesure, seuil) {
  var g = mesure.global;
  var s = (seuil === undefined || seuil === null) ? mesure.seuil : seuil;
  var l = [];
  l.push('SENTINEL EN ANGLAIS — ce qui reste en français à l\'écran');
  if (mesure.dictionnaire) {
    l.push('dictionnaire : ' + (mesure.dictionnaire.charge ? 'chargé' : 'NON CHARGÉ') + ' · '
      + (mesure.dictionnaire.texte || 0) + ' clés texte · ' + (mesure.dictionnaire.bloc || 0) + ' clés bloc'
      + (mesure.dictionnaire.motif ? ' · ' + mesure.dictionnaire.motif + ' motifs' : ''));
  }
  l.push('pages : ' + g.pages + ' · textes visibles : ' + g.textes);
  l.push('mots français : ' + g.mots_fr + ' · anglais : ' + g.mots_en + ' · neutres : ' + g.mots_neutres);
  l.push('PART FRANÇAISE GLOBALE : ' + pct(g.part_fr) + ' (seuil ' + pct(s) + ')');
  var c = mesure.coquille || {};
  l.push('coquille (menu + barre) : ' + pct(c.part_fr) + ' · ' + c.mots_fr + ' fr / ' + c.mots_en + ' en');
  var k = mesure.cadres;
  if (k && k.pages) {
    l.push('cadres (iframes, COMPRIS dans le verdict) : ' + pct(k.part_fr) + ' · ' + k.mots_fr + ' fr / ' + k.mots_en + ' en sur ' + k.pages + ' page(s)');
  }
  /* LE VOLUME DES DONNÉES EST DIT, TOUJOURS. Une part qui tombe parce qu'on
     a cessé de compter doit pouvoir se relire : sans cette ligne, on
     croirait ces mots disparus au lieu de les savoir mis de côté. */
  var dn = mesure.donnees;
  if (dn && dn.pages) {
    l.push('données (saisies, hors verdict) : ' + dn.mots_fr + ' mots fr / ' + dn.mots_en + ' en / '
      + dn.mots_neutres + ' neutres · ' + dn.textes + ' textes sur ' + dn.pages + ' page(s)');
  }
  l.push('');
  l.push('LES DIX PAGES LES PLUS FRANÇAISES');
  var p = pires(mesure, 10);
  for (var i = 0; i < p.length; i++) {
    l.push('  ' + pct(p[i].part_fr) + '  ' + p[i].page + '  (' + p[i].mots_fr + ' fr / ' + p[i].mots_en + ' en / ' + p[i].mots_neutres + ' neutres)');
  }
  l.push('');
  l.push(verdict(mesure, s) ? 'VERDICT : la part française dépasse le seuil — code 1'
                            : 'VERDICT : sous le seuil — code 0');
  return l.join('\n');
}

module.exports = {
  MOTS_FR: MOTS_FR, MOTS_EN: MOTS_EN, NOMS_PROPRES: NOMS_PROPRES,
  SEUIL_DEFAUT: SEUIL_DEFAUT, RESTES_MAX: RESTES_MAX,
  MARQUE_DONNEE: MARQUE_DONNEE, MARQUE_CADRE: MARQUE_CADRE,
  estDonnee: estDonnee, estCadre: estCadre, trier: trier,
  compterMots: compterMots, classer: classer, mesurerLot: mesurerLot,
  agreger: agreger, pires: pires, verdict: verdict, resumer: resumer
};
