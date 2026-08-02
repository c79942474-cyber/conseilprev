/* ══════════════════════════════════════════════════════════════════════════
   DRAPEAUX NATIONAUX — fond de carte et vignettes de tableau

   Deux usages, deux niveaux de fidélité, et c'est délibéré.

   DANS LES TABLEAUX, le drapeau est un IDENTIFIANT : l'œil le lit à côté du
   nom pour retrouver une ligne. Il est donc dessiné aussi fidèlement qu'une
   vignette de 20 × 14 px le permet — bandes exactes, croix nordiques
   véritablement en croix, proportions respectées.

   SUR LA CARTE, le drapeau est un REMPLISSAGE : un pays y prend la forme de
   son territoire, pas celle d'un rectangle, et aucune vignette n'y est
   reconnaissable. On y pose les COULEURS PRINCIPALES du drapeau, en bandes,
   par un dégradé à seuils francs. C'est une évocation, pas une reproduction —
   et la légende le dit, parce qu'un lecteur qui croirait voir un drapeau exact
   se tromperait sur les armoiries, les croix et les emblèmes qui n'y sont pas.

   Ce que ce fichier ne fait PAS : remplacer les fonds de carte qui portent une
   donnée. Colorier les pays par leur drapeau efface le nombre de cas ou de
   modèles qu'ils portaient. Les drapeaux sont donc UN FOND DE PLUS, au choix
   du lecteur, jamais une substitution silencieuse.
   ══════════════════════════════════════════════════════════════════════════ */
(function(global){
"use strict";

/* type :
     v      bandes verticales, de gauche à droite
     h      bandes horizontales, de haut en bas
     croix  croix nordique — b[0] fond, b[1] croix, b[2] liseré éventuel
     croixc croix CENTRÉE — Suisse, Géorgie. Une croix suisse dessinée comme
            une croix nordique n'est plus la croix suisse : le décalage vers
            le guindant est précisément ce qui distingue les deux familles.
     cercle champ uni b[0] + douze marques b[1] en couronne (drapeau européen)
   approx : ce que la vignette NE reproduit pas — un GROUPE NOMINAL, toujours,
            parce qu'il s'insère dans « vignette simplifiée, sans … ». Cette
            tournure est la seule qui accepte le singulier comme le pluriel
            sans accord à gérer.
   note   : une PHRASE, quand l'écart ne se dit pas par un nom (une proportion
            fausse, un format carré rendu en 10:7).
   Ni l'un ni l'autre n'est décoratif : ils alimentent l'infobulle et la note
   de la carte. Taire une approximation, c'est la faire passer pour une
   exactitude. */
var D = {
  /* L'Union n'est pas un pays, mais elle figure en tête de colonne dans les
     tableaux qui l'agrègent (brevets « Europe »). Sans vignette, cette colonne
     serait la seule sans repère visuel de sa ligne. */
  EU: { t: "cercle", b: ["#003399", "#FFCC00"], n: "Union européenne",
        note: "les douze étoiles sont figurées par des points" },

  /* ── Union européenne — 27 ── */
  AT: { t: "h", b: ["#ED2939", "#FFFFFF", "#ED2939"], n: "Autriche" },
  BE: { t: "v", b: ["#000000", "#FDDA24", "#EF3340"], n: "Belgique" },
  BG: { t: "h", b: ["#FFFFFF", "#00966E", "#D62612"], n: "Bulgarie" },
  CY: { t: "h", b: ["#FFFFFF", "#FFFFFF", "#FFFFFF"], n: "Chypre",
        approx: "l’île en cuivre et les rameaux d’olivier" },
  CZ: { t: "h", b: ["#FFFFFF", "#D7141A"], n: "Tchéquie",
        approx: "le triangle bleu du guindant" },
  DE: { t: "h", b: ["#000000", "#DD0000", "#FFCE00"], n: "Allemagne" },
  DK: { t: "croix", b: ["#C8102E", "#FFFFFF"], n: "Danemark" },
  EE: { t: "h", b: ["#0072CE", "#000000", "#FFFFFF"], n: "Estonie" },
  ES: { t: "h", b: ["#AA151B", "#F1BF00", "#AA151B"], n: "Espagne",
        approx: "les armoiries" },
  FI: { t: "croix", b: ["#FFFFFF", "#002F6C"], n: "Finlande" },
  FR: { t: "v", b: ["#002654", "#FFFFFF", "#ED2939"], n: "France" },
  GR: { t: "h", b: ["#0D5EAF", "#FFFFFF", "#0D5EAF", "#FFFFFF", "#0D5EAF"],
        n: "Grèce", approx: "la croix du canton" },
  HR: { t: "h", b: ["#FF0000", "#FFFFFF", "#171796"], n: "Croatie",
        approx: "l’échiquier des armoiries" },
  HU: { t: "h", b: ["#CD2A3E", "#FFFFFF", "#436F4D"], n: "Hongrie" },
  IE: { t: "v", b: ["#169B62", "#FFFFFF", "#FF883E"], n: "Irlande" },
  IT: { t: "v", b: ["#008C45", "#F4F5F0", "#CD212A"], n: "Italie" },
  LT: { t: "h", b: ["#FDB913", "#006A44", "#C1272D"], n: "Lituanie" },
  LU: { t: "h", b: ["#ED2939", "#FFFFFF", "#00A1DE"], n: "Luxembourg" },
  LV: { t: "h", b: ["#9E3039", "#FFFFFF", "#9E3039"], n: "Lettonie",
        note: "la bande blanche est plus étroite en réalité (2:1:2)" },
  MT: { t: "v", b: ["#FFFFFF", "#CF142B"], n: "Malte",
        approx: "la croix de George" },
  NL: { t: "h", b: ["#AE1C28", "#FFFFFF", "#21468B"], n: "Pays-Bas" },
  PL: { t: "h", b: ["#FFFFFF", "#DC143C"], n: "Pologne" },
  PT: { t: "v", b: ["#006600", "#FF0000"], n: "Portugal",
        approx: "la sphère armillaire et les armoiries" },
  RO: { t: "v", b: ["#002B7F", "#FCD116", "#CE1126"], n: "Roumanie" },
  SE: { t: "croix", b: ["#005293", "#FECB00"], n: "Suède" },
  SI: { t: "h", b: ["#FFFFFF", "#0000FF", "#FF0000"], n: "Slovénie",
        approx: "les armoiries au Triglav" },
  SK: { t: "h", b: ["#FFFFFF", "#0B4EA2", "#EE1C25"], n: "Slovaquie",
        approx: "les armoiries à la double croix" },

  /* ── Europe hors UE, présents dans les jeux de données ── */
  GB: { t: "h", b: ["#012169", "#FFFFFF", "#C8102E", "#FFFFFF", "#012169"],
        n: "Royaume-Uni", approx: "les croix superposées de l’Union Jack" },
  NO: { t: "croix", b: ["#BA0C2F", "#FFFFFF", "#00205B"], n: "Norvège" },
  CH: { t: "croixc", b: ["#DA291C", "#FFFFFF"], n: "Suisse",
        note: "le drapeau suisse est carré ; la vignette est au format 10:7" },
  IS: { t: "croix", b: ["#02529C", "#FFFFFF", "#DC1E35"], n: "Islande" },
  UA: { t: "h", b: ["#0057B7", "#FFD700"], n: "Ukraine" },
  RS: { t: "h", b: ["#C6363C", "#0C4076", "#FFFFFF"], n: "Serbie",
        approx: "les armoiries" },
  AL: { t: "h", b: ["#E41E20", "#E41E20"], n: "Albanie",
        approx: "l’aigle bicéphale" },
  BA: { t: "h", b: ["#002F6C", "#002F6C"], n: "Bosnie-Herzégovine",
        approx: "le triangle jaune et les étoiles" },
  MK: { t: "h", b: ["#D20000", "#D20000"], n: "Macédoine du Nord",
        approx: "le soleil à huit rayons" },
  ME: { t: "h", b: ["#C40308", "#C40308"], n: "Monténégro",
        approx: "l’aigle et le liseré doré" },
  MD: { t: "v", b: ["#0046AE", "#FFD200", "#CC092F"], n: "Moldavie",
        approx: "les armoiries" },
  BY: { t: "h", b: ["#D22730", "#009A49"], n: "Biélorussie",
        approx: "le motif décoratif du guindant" },
  TR: { t: "h", b: ["#E30A17", "#E30A17"], n: "Turquie",
        approx: "le croissant et l’étoile" },

  /* ── Voisinage et territoires dessinés par la carte du Panorama ──
     Ces pays n'ont pas de donnée dans le Panorama, mais la carte trace leur
     contour. Sans drapeau, ils resteraient gris dans la vue « drapeaux » —
     et le gris y voudrait dire « pas de donnée », ce qui serait faux : la
     donnée n'existe pas, mais le drapeau, lui, existe. */
  AD: { t: "v", b: ["#10069F", "#FEDD00", "#D0103A"], n: "Andorre",
        approx: "les armoiries" },
  AM: { t: "h", b: ["#D90012", "#0033A0", "#F2A800"], n: "Arménie" },
  AZ: { t: "h", b: ["#0092BC", "#E4002B", "#00AF66"], n: "Azerbaïdjan",
        approx: "le croissant et l’étoile" },
  DZ: { t: "v", b: ["#006233", "#FFFFFF"], n: "Algérie",
        approx: "le croissant et l’étoile rouges" },
  GE: { t: "croixc", b: ["#FFFFFF", "#FF0000"], n: "Géorgie",
        approx: "les quatre croisettes de Bolnisi" },
  IQ: { t: "h", b: ["#CE1126", "#FFFFFF", "#000000"], n: "Irak",
        approx: "l’inscription verte" },
  LB: { t: "h", b: ["#EE161F", "#FFFFFF", "#EE161F"], n: "Liban",
        approx: "le cèdre vert", note: "les bandes réelles sont 1:2:1" },
  LI: { t: "h", b: ["#002B7F", "#CE1126"], n: "Liechtenstein",
        approx: "la couronne d’or" },
  MA: { t: "h", b: ["#C1272D", "#C1272D"], n: "Maroc",
        approx: "l’étoile verte" },
  MC: { t: "h", b: ["#CE1126", "#FFFFFF"], n: "Monaco" },
  SM: { t: "h", b: ["#FFFFFF", "#5EB6E4"], n: "Saint-Marin",
        approx: "les armoiries" },
  SY: { t: "h", b: ["#CE1126", "#FFFFFF", "#000000"], n: "Syrie",
        approx: "les deux étoiles vertes" },
  TN: { t: "h", b: ["#E70013", "#E70013"], n: "Tunisie",
        approx: "le disque blanc, le croissant et l’étoile" },
  VA: { t: "v", b: ["#FFE000", "#FFFFFF"], n: "Vatican",
        approx: "les clés et la tiare" },
  GL: { t: "h", b: ["#FFFFFF", "#D00C33"], n: "Groenland",
        approx: "le disque bicolore" },
  FO: { t: "croix", b: ["#FFFFFF", "#ED2939", "#0065BD"], n: "Îles Féroé" },
  AX: { t: "croix", b: ["#0053A5", "#DA020E", "#FFD100"], n: "Åland" },
  GG: { t: "croixc", b: ["#FFFFFF", "#E8112D"], n: "Guernesey",
        approx: "la croix d’or superposée" },
  JE: { t: "h", b: ["#FFFFFF", "#FFFFFF"], n: "Jersey",
        approx: "le sautoir rouge et les armoiries" },
  IM: { t: "h", b: ["#CF142B", "#CF142B"], n: "Île de Man",
        approx: "le triskèle" },
  GI: { t: "h", b: ["#FFFFFF", "#FFFFFF", "#DA000C"], n: "Gibraltar",
        approx: "le château et la clé" },

  /* ── Hors Europe — pays porteurs de données de l’Observatoire ── */
  US: { t: "h", b: ["#B31942", "#FFFFFF", "#B31942", "#FFFFFF", "#B31942"],
        n: "États-Unis", approx: "le canton bleu et les cinquante étoiles" },
  CN: { t: "h", b: ["#EE1C25", "#EE1C25"], n: "Chine",
        approx: "les cinq étoiles jaunes" },
  CA: { t: "v", b: ["#FF0000", "#FFFFFF", "#FF0000"], n: "Canada",
        approx: "la feuille d’érable" },
  JP: { t: "h", b: ["#FFFFFF", "#FFFFFF"], n: "Japon",
        approx: "le disque rouge" },
  KR: { t: "h", b: ["#FFFFFF", "#FFFFFF"], n: "Corée du Sud",
        approx: "le taegeuk et les trigrammes" },
  IN: { t: "h", b: ["#FF9933", "#FFFFFF", "#138808"], n: "Inde",
        approx: "la roue d’Ashoka" },
  IL: { t: "h", b: ["#FFFFFF", "#0038B8", "#FFFFFF"], n: "Israël",
        approx: "l’étoile de David" },
  RU: { t: "h", b: ["#FFFFFF", "#0039A6", "#D52B1E"], n: "Russie" },
  AU: { t: "h", b: ["#00008B", "#00008B"], n: "Australie",
        approx: "l’Union Jack et la Croix du Sud" },
  AR: { t: "h", b: ["#74ACDF", "#FFFFFF", "#74ACDF"], n: "Argentine",
        approx: "le soleil de Mai" },
  IR: { t: "h", b: ["#239F40", "#FFFFFF", "#DA0000"], n: "Iran",
        approx: "l’emblème et les inscriptions" },
  SA: { t: "h", b: ["#165D31", "#165D31"], n: "Arabie saoudite",
        approx: "la chahada et le sabre" },
  AE: { t: "h", b: ["#00732F", "#FFFFFF", "#000000"], n: "Émirats arabes unis",
        approx: "la bande rouge verticale du guindant" },
  BR: { t: "h", b: ["#009B3A", "#009B3A"], n: "Brésil",
        approx: "le losange jaune et la sphère céleste" },
  MX: { t: "v", b: ["#006847", "#FFFFFF", "#CE1126"], n: "Mexique",
        approx: "les armoiries" },
  SG: { t: "h", b: ["#EF3340", "#FFFFFF"], n: "Singapour",
        approx: "le croissant et les cinq étoiles" },
  TW: { t: "h", b: ["#FE0000", "#FE0000"], n: "Taïwan",
        approx: "le canton bleu au soleil blanc" }
};

function esc(s){
  return String(s == null ? "" : s).replace(/[&<>"']/g, function(c){
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
  });
}

/* Un même pays apparaît plusieurs fois par page — tableau, infobulle, fiche.
   Un identifiant de découpe constant produirait autant d'éléments id="drc-FR" :
   le rendu resterait juste (les découpes sont identiques), mais la page
   deviendrait invalide et tout audit d'accessibilité le signalerait. Un
   compteur suffit. */
var UID = 0;

/* Eurostat n'écrit pas la Grèce EL par erreur : c'est sa nomenclature. Le
   Royaume-Uni y reste UK. Refuser ces codes afficherait un cadre vide à côté
   de deux pays parfaitement connus — on les traduit plutôt en ISO. */
var ALIAS = { EL: "GR", UK: "GB" };

function res(code){
  var c = String(code == null ? "" : code).toUpperCase();
  return ALIAS[c] || c;
}

function connu(code){ return !!D[res(code)]; }
function nom(code){ return (D[res(code)] || {}).n || code; }
/* L'écart déclaré, sous forme lisible — les deux champs réunis, parce qu'un
   appelant qui demande « en quoi cette vignette est-elle approximative ? »
   veut la réponse entière, pas la moitié qui se dit par un nom. */
function approx(code){
  var f = D[res(code)] || {};
  return [f.approx, f.note].filter(Boolean).join(" ; ");
}

/* Les couleurs principales, dans l'ordre du drapeau. Sert au dégradé de carte
   et à toute lecture programmatique — jamais de couleur écrite en dur ailleurs. */
function couleurs(code){
  var f = D[res(code)];
  if(!f) return [];
  if(f.t === "croix" || f.t === "croixc" || f.t === "cercle") return [f.b[0], f.b[1]];
  return f.b.slice();
}

/* ── LA VIGNETTE DE TABLEAU ────────────────────────────────────────────────
   20 × 14 par défaut, ratio 10:7 — celui de la plupart des drapeaux européens.
   Un liseré gris entoure la vignette : sans lui, un drapeau à bande blanche
   extérieure (Pologne, Finlande) se fondrait dans la page et paraîtrait
   tronqué. */
function icone(code, opts){
  opts = opts || {};
  var w = opts.w || 20, h = opts.h || 14;
  code = res(code);
  var f = D[code];
  var titre = f ? f.n : (opts.nom || code);
  var aria = opts.decoratif ? ' aria-hidden="true"'
                            : ' role="img" aria-label="' + esc("Drapeau — " + titre) + '"';
  if(!f){
    /* Pays sans drapeau au référentiel : on montre un cadre vide plutôt que
       rien. Une case absente désaligne la colonne et se lit comme un oubli. */
    return '<svg class="dr" width="' + w + '" height="' + h + '" viewBox="0 0 20 14"'
      + aria + '><rect width="20" height="14" rx="1.5" fill="#F0EEEA" stroke="#C9C6C0"'
      + ' stroke-width="1"/><line x1="4" y1="7" x2="16" y2="7" stroke="#C9C6C0"'
      + ' stroke-width="1.2"/><title>' + esc(titre) + ' — drapeau non répertorié</title></svg>';
  }
  var corps = "";
  if(f.t === "cercle"){
    /* Douze marques en couronne. À 20 × 14 px, une étoile à cinq branches se
       réduit à une tache : le point la remplace, et l'infobulle le dit. Le
       compte, lui, est exact — c'est ce que douze étoiles signifient. */
    corps = '<rect width="20" height="14" fill="' + f.b[0] + '"/>';
    for(var s = 0; s < 12; s++){
      var a = (s / 12) * Math.PI * 2 - Math.PI / 2;
      corps += '<circle cx="' + (10 + Math.cos(a) * 4.2).toFixed(2)
             + '" cy="' + (7 + Math.sin(a) * 4.2).toFixed(2)
             + '" r="0.95" fill="' + f.b[1] + '"/>';
    }
  } else if(f.t === "croixc"){
    corps = '<rect width="20" height="14" fill="' + f.b[0] + '"/>'
          + '<rect x="0" y="5.4" width="20" height="3.2" fill="' + f.b[1] + '"/>'
          + '<rect x="8.4" y="0" width="3.2" height="14" fill="' + f.b[1] + '"/>';
  } else if(f.t === "croix"){
    /* Croix nordique : hampe décalée vers le guindant, proportions usuelles. */
    var fond = f.b[0], croix = f.b[1], liseré = f.b[2];
    corps = '<rect width="20" height="14" fill="' + fond + '"/>';
    if(liseré){
      corps += '<rect x="0" y="4.6" width="20" height="4.8" fill="' + liseré + '"/>'
             + '<rect x="5.4" y="0" width="4.8" height="14" fill="' + liseré + '"/>';
    }
    corps += '<rect x="0" y="5.6" width="20" height="2.8" fill="' + croix + '"/>'
           + '<rect x="6.4" y="0" width="2.8" height="14" fill="' + croix + '"/>';
  } else {
    var n = f.b.length, pas = (f.t === "v" ? 20 : 14) / n;
    corps = f.b.map(function(c, i){
      return f.t === "v"
        ? '<rect x="' + (i * pas).toFixed(2) + '" y="0" width="' + (pas + 0.02).toFixed(2)
          + '" height="14" fill="' + c + '"/>'
        : '<rect x="0" y="' + (i * pas).toFixed(2) + '" width="20" height="'
          + (pas + 0.02).toFixed(2) + '" fill="' + c + '"/>';
    }).join("");
  }
  var tt = f.n;
  if(f.approx) tt += " — vignette simplifiée, sans " + f.approx;
  if(f.note) tt += (f.approx ? " ; " : " — vignette simplifiée : ") + f.note;
  var cid = "drc-" + code + "-" + (++UID);
  return '<svg class="dr" width="' + w + '" height="' + h + '" viewBox="0 0 20 14"' + aria
    + '><clipPath id="' + cid + '"><rect width="20" height="14" rx="1.5"/></clipPath>'
    + '<g clip-path="url(#' + cid + ')">' + corps + "</g>"
    + '<rect width="20" height="14" rx="1.5" fill="none" stroke="rgba(28,28,28,.28)"'
    + ' stroke-width="1"/><title>' + esc(tt) + "</title></svg>";
}

/* ── LE FOND DE CARTE ──────────────────────────────────────────────────────
   Un dégradé par pays, à seuils francs : les bandes du drapeau, appliquées à
   la boîte englobante du tracé du pays. La forme reste celle du territoire —
   c'est bien une évocation, jamais une reproduction. */
function defs(codes){
  var out = "", vus = {};
  (codes || Object.keys(D)).forEach(function(brut){
    var code = res(brut);
    /* Deux codes peuvent désigner le même drapeau (EL et GR). Un second
       dégradé de même identifiant serait ignoré par le navigateur, mais
       alourdirait le document pour rien. */
    if(vus[code]) return;
    vus[code] = true;
    var f = D[code];
    /* Le drapeau européen ne se réduit pas à des bandes : une couronne
       d'étoiles rendue en dégradé donnerait un damier bleu-or qui ne
       ressemble à rien. Il n'a pas de contour de carte de toute façon —
       on n'en fabrique donc pas de fond du tout. */
    if(!f || f.t === "cercle") return;
    var bandes = (f.t === "croix" || f.t === "croixc")
      /* Une croix ne se rend pas en dégradé. On pose les deux couleurs du
         drapeau, la couleur de croix au centre — l'identité chromatique est
         conservée, le dessin ne l'est pas, et la légende l'annonce. */
      ? [f.b[0], f.b[1], f.b[0]]
      : f.b;
    var vert = (f.t === "v");
    var st = "", n = bandes.length;
    bandes.forEach(function(c, i){
      st += '<stop offset="' + (i / n * 100).toFixed(3) + '%" stop-color="' + c + '"/>'
          + '<stop offset="' + ((i + 1) / n * 100).toFixed(3) + '%" stop-color="' + c + '"/>';
    });
    out += '<linearGradient id="dr-' + code + '" x1="0" y1="0" x2="' + (vert ? 1 : 0)
      + '" y2="' + (vert ? 0 : 1) + '">' + st + "</linearGradient>";
  });
  return "<defs>" + out + "</defs>";
}

/* La référence de remplissage d'un pays, ou null s'il n'est pas répertorié —
   l'appelant garde alors son gris « pas de donnée » plutôt qu'une couleur
   inventée. */
function fond(code){
  code = res(code);
  return (D[code] && D[code].t !== "cercle") ? "url(#dr-" + code + ")" : null;
}

/* Combien de drapeaux sont simplifiés, et lesquels. La légende s'en sert pour
   annoncer la limite au lieu de la laisser découvrir. */
function simplifies(codes){
  var vus = {};
  return (codes || Object.keys(D)).map(res).filter(function(c){
    if(vus[c] || !D[c]) return false;
    vus[c] = true;
    return !!(D[c].approx || D[c].note);
  });
}

global.DRAPEAUX = { icone: icone, defs: defs, fond: fond, couleurs: couleurs,
                    nom: nom, approx: approx, connu: connu,
                    simplifies: simplifies, table: D };
})(window);
