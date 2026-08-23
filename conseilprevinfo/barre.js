/* LA BARRE LATÉRALE — et pourquoi elle ne peut pas mentir.
   ────────────────────────────────────────────────────────
   LES SECTIONS NE SONT PAS ÉCRITES ICI, ELLES SONT LUES DANS LA PAGE. Une
   liste tenue à la main dans ce fichier promettrait « Pistes d'instruction »
   le jour où la rubrique serait retirée, et le lecteur cliquerait dans le
   vide. Toute `h2.rubrique` portant un identifiant devient une entrée ; aucune
   autre n'en devient une. La barre ne peut donc pas diverger de la page — de
   la même façon que le registre des sources dérive de la table qui collecte.

   LES COMPTES VIENNENT DES MÊMES ÉLÉMENTS QUE LES TITRES. Chaque rubrique
   porte déjà son compteur (`<span id="c-fil">98</span>`) que le moteur
   remplit ; la barre le recopie et le suit. Un second calcul, même juste,
   finirait par afficher un autre nombre que celui d'à côté.

   ELLE NE S'IMPOSE PAS SUR UN TÉLÉPHONE. Sous 1100 px elle se replie derrière
   un bouton : une colonne fixe de 230 px sur un écran de 390 px prend la
   moitié de la largeur pour de la navigation, c'est-à-dire pour rien. */
(function () {
  "use strict";

  function $(i) { return document.getElementById(i); }
  function esc(x) {
    return String(x == null ? "" : x).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function t(c) { return (window.L && window.L.t) ? window.L.t(c) : c; }

  /* Les pages du site. Elles sont peu nombreuses et stables ; les découvrir
     demanderait un index que ce site n'a pas, et l'inventer serait pire. */
  var PAGES = [
    { href: "/", cle: "bl.fil", dit: "bl.fil.dit" },
    { href: "/confronter", cle: "bl.conf", dit: "bl.conf.dit" },
    { href: "/abonnement", cle: "bl.abo", dit: "bl.abo.dit" }
  ];

  function ici(href) {
    var p = location.pathname;
    return href === "/" ? (p === "/" || p === "") : p.indexOf(href) === 0;
  }

  function sections() {
    return Array.prototype.slice.call(
      document.querySelectorAll("main h2.rubrique[id]")
    ).map(function (h) {
      /* LE TITRE EST LE PREMIER SPAN SANS IDENTIFIANT ; LE COMPTEUR EST
         CELUI QUI EN PORTE UN.

         DÉFAUT CONSTATÉ AU NAVIGATEUR. Premier essai : retirer TOUS les spans
         et garder le reste — ce qui marchait tant que le titre était du texte
         nu. Depuis qu'il est lui-même dans un span, pour être traduisible,
         cette règle le supprimait : la barre affichait « 53 fiche(s) » sans
         jamais dire de quoi. Le compteur, lui, reste suivi à part — le
         recopier dans le libellé le figerait à la valeur du chargement. */
      var c = h.querySelector("span[id]");
      var premier = h.querySelector("span:not([id])");
      var brut = premier ? premier.textContent
        : (c ? h.textContent.replace(c.textContent, "") : h.textContent);
      /* LE TITRE DE LA BARRE S'ARRÊTE AU TIRET. Les rubriques de ce site
         s'intitulent « nom court — ce que c'est » : « Le fil — tout le corpus
         filtré ». La glose est utile en tête de section, elle ne l'est pas
         dans une colonne de 236 px, où elle repousse le compteur hors du
         cadre et fait de chaque entrée trois lignes. Le nom court suffit :
         c'est celui que le lecteur cherche. */
      var titre = brut.replace(/\s+/g, " ").trim();
      var i = titre.indexOf(" — ");
      return {
        id: h.id,
        titre: i > 0 ? titre.slice(0, i) : titre,
        compteur: c ? c.id : null
      };
    });
  }

  function rendre() {
    var hote = document.querySelector("[data-barre]");
    if (!hote) return;
    var secs = sections();
    var h = '<nav class="bl-nav" aria-label="' + esc(t("bl.pages")) + '">';

    h += '<p class="bl-t">' + esc(t("bl.pages")) + "</p><ul class=\"bl-l\">";
    PAGES.forEach(function (p) {
      h += '<li><a href="' + p.href + '"' + (ici(p.href) ? ' aria-current="page"' : "")
        + '><b>' + esc(t(p.cle)) + "</b><span>" + esc(t(p.dit)) + "</span></a></li>";
    });
    h += "</ul>";

    if (secs.length) {
      h += '<p class="bl-t">' + esc(t("bl.sections")) + "</p><ul class=\"bl-l bl-s\">";
      secs.forEach(function (s) {
        h += '<li><a href="#' + esc(s.id) + '" data-va="' + esc(s.id) + '">'
          + esc(s.titre)
          + (s.compteur ? '<i data-de="' + esc(s.compteur) + '"></i>' : "")
          + "</a></li>";
      });
      h += "</ul>";
    }
    h += "</nav>";
    hote.innerHTML = h;
    suivreCompteurs();
    suivreLecture(secs);
  }

  /* LE COMPTE DE LA BARRE EST CELUI DE LA RUBRIQUE, recopié à chaque fois
     qu'il change. Deux nombres différents pour la même chose sur le même
     écran valent moins qu'aucun nombre. */
  function suivreCompteurs() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-de]"), function (cible) {
      var src = $(cible.getAttribute("data-de"));
      if (!src) return;
      var copier = function () {
        var v = (src.textContent || "").replace(/\s+/g, " ").trim();
        cible.textContent = v;
        cible.hidden = !v;
      };
      copier();
      try { new MutationObserver(copier).observe(src, { childList: true, characterData: true, subtree: true }); }
      catch (e) { /* sans observateur, le compte reste celui du chargement */ }
    });
  }

  /* LA SECTION EN COURS DE LECTURE EST MARQUÉE. Sans cela, une barre de
     navigation sur une page longue dit où l'on peut aller sans jamais dire
     où l'on est. */
  function suivreLecture(secs) {
    var titres = secs.map(function (s) { return $(s.id); }).filter(Boolean);
    if (!titres.length || typeof IntersectionObserver === "undefined") return;
    var vus = {};
    var obs = new IntersectionObserver(function (entrees) {
      entrees.forEach(function (e) { vus[e.target.id] = e.isIntersecting; });
      var courant = null;
      titres.forEach(function (h) { if (vus[h.id] && !courant) courant = h.id; });
      Array.prototype.forEach.call(document.querySelectorAll("[data-va]"), function (a) {
        a.classList.toggle("bl-ici", a.getAttribute("data-va") === courant);
      });
    }, { rootMargin: "-70px 0px -70% 0px" });
    titres.forEach(function (h) { obs.observe(h); });
  }

  function replier() {
    var b = $("bl-bouton"), c = document.querySelector("[data-barre]");
    if (!b || !c) return;
    /* UNE BARRE REPLIÉE N'EST PAS SEULEMENT INVISIBLE : elle doit sortir du
       parcours. Déplacée par `transform`, elle reste dans l'ordre de
       tabulation et dans l'arbre d'accessibilité — un lecteur au clavier
       traverse donc huit liens hors écran avant d'atteindre la page, et un
       lecteur d'écran les annonce tous. `inert` l'en retire, et `aria-hidden`
       le dit aux navigateurs qui ne le connaissent pas encore. */
    var ouvrir = function (o) {
      c.classList.toggle("bl-ouverte", o);
      b.setAttribute("aria-expanded", o ? "true" : "false");
      b.setAttribute("aria-label", t(o ? "bl.fermer" : "bl.ouvrir"));
      var replie = o ? false : window.matchMedia("(max-width:1099px)").matches;
      if (replie) { c.setAttribute("inert", ""); c.setAttribute("aria-hidden", "true"); }
      else { c.removeAttribute("inert"); c.removeAttribute("aria-hidden"); }
    };
    /* Au passage en grand écran, la barre redevient une colonne : la laisser
       inerte la rendrait muette pour rien. */
    try {
      window.matchMedia("(max-width:1099px)").addEventListener("change", function () {
        ouvrir(false);
      });
    } catch (e) { /* navigateur ancien : l'état du chargement fait foi */ }
    b.addEventListener("click", function () {
      ouvrir(!c.classList.contains("bl-ouverte"));
    });
    /* Un clic sur un lien referme : sur un téléphone, la barre couvre la page
       qu'on vient de demander. */
    c.addEventListener("click", function (e) {
      if (e.target.closest("a")) ouvrir(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") ouvrir(false);
    });
    ouvrir(false);
  }

  function demarrer() {
    rendre();
    replier();
    /* La barre est réécrite à la bascule de langue : ses libellés viennent du
       dictionnaire, et les titres de section viennent de la page — qui vient
       elle aussi d'être retraduite. L'ordre importe, d'où l'écoute. */
    document.addEventListener("langue", rendre);
  }

  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", demarrer);
  else demarrer();
})();
