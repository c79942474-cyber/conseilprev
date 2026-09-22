/* Les infobulles s'ouvrent aussi au DOIGT et au CLAVIER.
   ═══════════════════════════════════════════════════════════════════════

   LE DÉFAUT, MESURÉ AU NAVIGATEUR EN CONTEXTE TACTILE (Pixel 7, hasTouch,
   `(hover:none)` vrai) : sur la page d'accueil, l'opacité de la bulle reste
   à 0 AVANT et APRÈS un appui du doigt. Les trente-deux infobulles du site
   public ne s'ouvrent jamais sur un téléphone. Elles ne s'ouvrent pas
   davantage au clavier : les cartes sont des <div> sans tabindex, et
   `element.focus()` n'y prend même pas — le focus reste sur le <body>.

   POURQUOI. L'ouverture est écrite `:hover::after` et rien d'autre. Il n'y a
   pas de survol sur un écran tactile, et un <div> n'est pas focusable.

   CE QUE CE FICHIER FAIT, ET CE QU'IL NE FAIT PAS

   Il ne dessine AUCUNE bulle. Chaque page a déjà la sienne — position,
   couleurs, flèche, largeur — réglée au pixel près, parfois contre un
   `overflow:hidden` qui lui a coûté une recette entière. Une seconde bulle
   dessinée ici s'afficherait EN PLUS de celle du survol sur un poste fixe :
   deux bulles pour une infobulle. Ce script ne fait donc qu'une chose :
   poser une classe, et publier une règle qui ouvre la bulle EXISTANTE quand
   cette classe est là. Le réglage reste où il est.

   POURQUOI LA RÈGLE EST INJECTÉE ICI ET NON ÉCRITE DANS LES PAGES. Vingt
   pages portent la feuille des infobulles. Vingt copies d'une même règle
   divergent — ce dépôt a déjà payé ce défaut-là. Une seule déclaration, au
   même endroit que le comportement qu'elle sert.

   LE LECTEUR D'ÉCRAN. Le texte vit dans un attribut, invisible aux
   technologies d'assistance. À l'ouverture, il est déposé dans une région
   `aria-live` unique pour toute la page : une seule balise en plus, et le
   texte est annoncé au moment où quelqu'un le demande. */
(function () {
  "use strict";

  /* LES DEUX CONVENTIONS DU DÉPÔT, ET RIEN D'AUTRE. `data-tooltip` sur le
     site public, `data-tip` dans Sentinel. Un `title` natif n'est PAS
     ramassé : il appartient au navigateur, sert aussi aux champs de
     formulaire, et le détourner produirait deux infobulles sur un poste
     fixe — celle du navigateur et la nôtre. */
  var ATTRS = ["data-tooltip", "data-tip"];
  var SELECTEUR = "[data-tooltip],[data-tip]";
  var OUVERTE = "bulle-ouverte";
  var REGION = "bulle-annonce";
  /* « LIRE D'ABORD, AGIR ENSUITE » — ET SEULEMENT LÀ OÙ C'EST DEMANDÉ.
     ═══════════════════════════════════════════════════════════════════
     LE DÉFAUT MESURÉ. Sur le rail DORA, chaque bloc est un <bouton> qui
     mène à son panneau. Au doigt, l'appui ouvrait bien la bulle — puis
     déclenchait la navigation, qui repeint le rail et DÉTRUIT le bouton
     qui la portait. Relevé au navigateur : opacité 0. L'infobulle était
     donc illisible au doigt, exactement comme avec le `title` natif
     qu'elle venait remplacer.

     CE QU'ON FAIT : sur ces éléments-là, le premier appui OUVRE et retient
     le clic ; le second laisse passer. C'est la convention mobile
     ordinaire pour un contrôle qui porte une explication, et c'est
     précisément ce que ce rail demande — savoir ce qu'un bloc fait AVANT
     d'y aller.

     POURQUOI UN ATTRIBUT, ET NON POUR TOUT LE MONDE. Retenir le premier
     clic partout changerait le comportement de chaque lien du site au
     doigt. L'élément qui le veut le déclare. */
  var AVANT_CLIC = "data-bulle-avant-clic";

  function texte(el) {
    for (var i = 0; i < ATTRS.length; i++) {
      var v = el.getAttribute(ATTRS[i]);
      if (v) return v;
    }
    return "";
  }

  /* L'ÉTAT OUVERT EST DÉRIVÉ DU SURVOL DÉJÀ ÉCRIT, JAMAIS REDÉCLARÉ.
     ═══════════════════════════════════════════════════════════════════
     LE PIÈGE ÉVITÉ. Une règle générique du genre « à l'ouverture,
     opacité 1 » a l'air de suffire. Elle ne suffit pas : le survol ne fait
     pas qu'allumer la bulle, il annule aussi son décalage d'entrée — et ce
     décalage n'est pas le même partout (4 px sur la bulle générique, 6 px
     sur les cartes de l'accueil, avec ou sans centrage `translateX(-50%)`).
     Une valeur devinée ici laisserait la bulle deux pixels plus bas au
     doigt qu'à la souris, et se déréglerait au premier changement de page.

     CE QU'ON FAIT À LA PLACE : on lit les feuilles de la page, on retient
     les règles qui ouvrent une infobulle au survol, et on en republie une
     JUMELLE où `:hover` devient notre classe. Tout ce que le survol fait,
     l'appui du doigt le fait — sans qu'aucune valeur soit recopiée.

     LE FILTRE EST ÉTROIT, ET IL EST DÉRIVÉ LUI AUSSI. Sans lui,
     `.diff-card:hover{transform:scale(1.10)}` serait jumelée : la carte
     grossirait à chaque appui, ce qui n'a rien à voir avec une infobulle.

     MAIS IL NE PEUT PAS ÊTRE UNE LISTE DE NOMS DE CLASSES. Le dépôt en
     compte déjà trois — `.ent-tip` dans Sentinel, `.ttip` sur le panorama,
     `[data-tooltip]` sur le site public — et une quatrième arriverait sans
     que personne ne pense à ce fichier. C'est d'ailleurs une règle de la
     suite qui a trouvé les deux pages oubliées, pas une relecture.

     ON RECONNAÎT DONC UNE INFOBULLE À CE QU'ELLE FAIT : une règle qui REND
     l'attribut, c'est-à-dire qui porte `content:attr(data-tip…)`. Le
     sélecteur de cette règle, privé de ses pseudo-éléments, donne la
     « base » de la famille — `.ttip`, `.ent-tip`, `[data-tooltip]`. On
     jumelle ensuite tout ce qui survole cette base, et rien d'autre.

     LE REPLI. Une feuille d'une autre origine lève une erreur à la lecture
     de ses règles — le navigateur l'interdit. On garde alors la règle
     générique : la bulle s'ouvre, au décalage près. */
  function _toutesLesRegles() {
    var out = [];
    var feuilles = document.styleSheets;
    for (var i = 0; i < feuilles.length; i++) {
      var regles;
      try { regles = feuilles[i].cssRules; } catch (e) { continue; }
      if (!regles) continue;
      for (var j = 0; j < regles.length; j++) {
        if (regles[j].selectorText) out.push(regles[j]);
      }
    }
    return out;
  }

  function _base(sel) {
    return sel.split("::")[0].split(":hover")[0].trim();
  }

  function jumelles() {
    var regles = _toutesLesRegles(), bases = {}, out = [], i;
    /* Premier passage : QUI REND UN ATTRIBUT D'INFOBULLE. */
    for (i = 0; i < regles.length; i++) {
      var css = regles[i].style.cssText || "";
      var sel = regles[i].selectorText;
      if (css.indexOf("attr(data-tooltip") >= 0
          || css.indexOf("attr(data-tip") >= 0
          || sel.indexOf("[data-tooltip]") >= 0
          || sel.indexOf("[data-tip]") >= 0) {
        var b = _base(sel);
        if (b) bases[b] = true;
      }
    }
    /* Second passage : tout ce qui survole une de ces bases. */
    for (i = 0; i < regles.length; i++) {
      var s2 = regles[i].selectorText;
      if (s2.indexOf(":hover") < 0) continue;
      if (!bases[_base(s2)]) continue;
      out.push(s2.split(":hover").join("." + OUVERTE) + "{"
               + regles[i].style.cssText + "}");
    }
    return out;
  }

  function publierLaRegle() {
    if (document.getElementById("css-bulle-ouverte")) return;
    var s = document.createElement("style");
    s.id = "css-bulle-ouverte";
    s.textContent = jumelles().join("")
      /* LE SOCLE, qui tient même si aucune jumelle n'a pu être lue.
         `!important` n'est pas un confort : cette feuille passe après celle
         de la page, dont certaines rouvrent `[data-tooltip]::after` avec
         leurs propres `!important` de thème. Elle ne touche QUE l'ouverture,
         jamais la couleur, la position ni la largeur. */
      + "." + OUVERTE + "::after{opacity:1 !important;pointer-events:none}"
      + "." + OUVERTE + "::before{opacity:1 !important}"
      /* Ce que le doigt révèle, le clavier doit le révéler aussi. */
      + SELECTEUR + ":focus-visible::after{opacity:1 !important}"
      + SELECTEUR + ":focus-visible::before{opacity:1 !important}"
      + SELECTEUR + ":focus-visible{outline:2px solid currentColor;"
      + "outline-offset:2px}"
      /* La région d'annonce est lue, jamais vue. `clip-path` plutôt que
         `display:none`, qui la retirerait de l'arbre d'accessibilité. */
      + "#" + REGION + "{position:absolute;width:1px;height:1px;overflow:hidden;"
      + "clip-path:inset(50%);white-space:nowrap}";
    (document.head || document.documentElement).appendChild(s);
  }

  function region() {
    var r = document.getElementById(REGION);
    if (!r) {
      r = document.createElement("div");
      r.id = REGION;
      r.setAttribute("aria-live", "polite");
      r.setAttribute("aria-atomic", "true");
      (document.body || document.documentElement).appendChild(r);
    }
    return r;
  }

  var ouvert = null;
  /* L'élément dont le PROCHAIN clic doit être retenu. Il est posé à
     l'appui et consommé par le clic qui suit — jamais conservé au-delà. */
  var aRetenir = null;

  function fermer() {
    if (!ouvert) return;
    ouvert.classList.remove(OUVERTE);
    ouvert = null;
    try { region().textContent = ""; } catch (e) { /* rien à annoncer */ }
  }

  function ouvrir(el) {
    if (ouvert === el) return fermer();   /* un second appui referme */
    fermer();
    el.classList.add(OUVERTE);
    ouvert = el;
    try { region().textContent = texte(el); } catch (e) { /* idem */ }
  }

  /* CE QUI REND LA CIBLE ATTEIGNABLE AU CLAVIER. Un <div> n'est pas
     focusable ; un <button> ou un <a> l'est déjà, et lui poser un tabindex
     ne ferait que dupliquer son rang de tabulation. */
  function preparer(el) {
    if (el.hasAttribute("data-bulle-prete")) return;
    el.setAttribute("data-bulle-prete", "1");
    var focusable = /^(A|BUTTON|INPUT|SELECT|TEXTAREA)$/.test(el.tagName)
                    || el.hasAttribute("tabindex");
    if (!focusable) el.setAttribute("tabindex", "0");
  }

  function balayer() {
    var n = document.querySelectorAll(SELECTEUR);
    for (var i = 0; i < n.length; i++) preparer(n[i]);
    return n.length;
  }

  function demarrer() {
    publierLaRegle();
    balayer();

    /* L'APPUI. `pointerdown` couvre le doigt, le stylet et la souris ; on ne
       retient que ce qui n'est PAS une souris, pour ne pas voler le survol
       à un poste fixe. Un clic de souris sur une carte doit continuer de
       suivre son lien, pas d'ouvrir une bulle. */
    document.addEventListener("pointerdown", function (ev) {
      if (ev.pointerType === "mouse") return;
      var el = ev.target && ev.target.closest && ev.target.closest(SELECTEUR);
      if (!el) return fermer();
      /* UN APPUI SUR UN LIEN OU UN BOUTON DOIT RESTER UN APPUI SUR CE
         LIEN. On ouvre la bulle SANS empêcher l'action : l'infobulle
         explique, elle ne remplace pas la navigation. */
      preparer(el);
      var etaitOuvert = (ouvert === el);
      ouvrir(el);
      /* Le premier appui sur un élément qui l'a demandé retient son clic.
         Le second — celui qui referme, ou celui qui suit une lecture —
         le laisse passer. */
      aRetenir = (!etaitOuvert && el.hasAttribute(AVANT_CLIC)) ? el : null;
    }, true);

    /* LE CLIC EST RETENU ICI, ET NON À L'APPUI. `preventDefault` sur
       `pointerdown` ne supprime pas partout le clic que le navigateur
       synthétise après un appui : on attend donc ce clic-là et on l'arrête
       au vol, en capture, avant que le gestionnaire du bouton ne le voie. */
    document.addEventListener("click", function (ev) {
      if (!aRetenir) return;
      var el = ev.target && ev.target.closest && ev.target.closest(SELECTEUR);
      if (el !== aRetenir) { aRetenir = null; return; }
      aRetenir = null;
      ev.preventDefault();
      ev.stopPropagation();
    }, true);

    /* La tabulation ouvre par `:focus-visible` (règle CSS ci-dessus) ; il
       reste à annoncer le texte, ce que le CSS ne sait pas faire. */
    document.addEventListener("focusin", function (ev) {
      var el = ev.target && ev.target.closest && ev.target.closest(SELECTEUR);
      if (el) { try { region().textContent = texte(el); } catch (e) {} }
    });
    document.addEventListener("focusout", function (ev) {
      if (ouvert !== ev.target) { try { region().textContent = ""; } catch (e) {} }
    });

    /* LES SORTIES, parce qu'une bulle ouverte qu'on ne sait pas fermer masque
       le contenu qu'elle devait éclairer : un second appui, un appui
       ailleurs (plus haut), et la touche d'échappement.

       ═══ ET PAS AU DÉFILEMENT — C'EST UN DÉFAUT MESURÉ, PAS UNE OPINION ═══
       Une première version fermait aussi au défilement. Mesure au
       navigateur, contexte tactile : la classe était POSÉE puis RETIRÉE
       dans la foulée, et la bulle ne s'ouvrait jamais. La page défile en
       `scroll-behavior:smooth` — amener une carte à l'écran émet des
       dizaines d'événements de défilement APRÈS l'appui. Sur un vrai
       téléphone, c'est le cas ordinaire : on tape une carte à demi visible,
       le navigateur l'amène à l'écran, et la bulle se referme avant d'avoir
       été lue. Fermer au défilement ne servait à rien par ailleurs : la
       bulle est positionnée par rapport à sa cible et voyage avec elle.

       LE REDIMENSIONNEMENT NE COMPTE QUE S'IL CHANGE LA LARGEUR. Sur un
       téléphone, la barre d'adresse qui se rétracte pendant un défilement
       émet un `resize` — de hauteur seulement. Le prendre pour un
       changement de mise en page ramènerait le défaut qu'on vient de
       corriger, par une autre porte. */
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" || ev.key === "Esc") fermer();
    });
    var largeur = window.innerWidth;
    window.addEventListener("resize", function () {
      if (window.innerWidth === largeur) return;
      largeur = window.innerWidth;
      fermer();
    });
    window.addEventListener("orientationchange", fermer);

    /* Les pages de Sentinel réécrivent des panneaux entiers : les cibles
       arrivées après coup doivent devenir atteignables sans rechargement. */
    try {
      new MutationObserver(balayer).observe(document.documentElement,
        { childList: true, subtree: true });
    } catch (e) { /* pas d'observateur : le balayage initial tient */ }
  }

  window.infobulles = { ouvrir: ouvrir, fermer: fermer, balayer: balayer,
                        selecteur: SELECTEUR, classe: OUVERTE };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", demarrer);
  } else {
    demarrer();
  }
})();
