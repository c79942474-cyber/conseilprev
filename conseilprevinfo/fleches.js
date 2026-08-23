/* LES QUATRE FLÈCHES — et la règle qui les empêche d'être décoratives.
   ───────────────────────────────────────────────────────────────────
   LA RÈGLE, D'ABORD : AUCUN BOUTON NE FAIT SILENCIEUSEMENT RIEN. Chaque
   flèche voit son sens RÉSOLU au moment où elle est posée ; ce sens devient
   son intitulé, et une flèche qui n'en a pas est rendue ÉTEINTE, avec le
   motif écrit dans son infobulle. C'est la même règle que partout ailleurs
   sur ce site — un axe qui ne donne rien le dit — appliquée à un ornement
   d'interface, parce qu'un ornement qui trompe trompe autant qu'un texte.

   Ce n'est pas une précaution théorique. Le montage habituel — ← et → câblés
   sur l'historique du navigateur — donne une flèche « suivant » qui ne fait
   RIEN dans la quasi-totalité des cas : il n'y a de page suivante que si l'on
   vient de reculer. Le navigateur, lui, éteint la sienne ; une flèche dessinée
   dans la page ne le peut pas, faute d'API. Elle reste donc allumée et morte.

   D'OÙ LE SENS DONNÉ À GAUCHE ET DROITE : la fiche PRÉCÉDENTE et la fiche
   SUIVANTE, dans l'ordre du fil que vous lisiez. C'est le geste du journal —
   article précédent, article suivant — et c'est ici le seul qui soit
   VÉRIFIABLE : l'ordre est connu, sa longueur aussi, et le rang s'affiche.
   L'ordre suit vos filtres : si vous parcouriez « Systèmes d'IA », les
   voisines sont celles de cette rubrique, pas celles du corpus entier.

   L'ORDRE VIT DANS `sessionStorage`, ET IL Y MEURT. Il disparaît à la
   fermeture de l'onglet, comme le jeton de session : c'est un fil de lecture
   en cours, pas une trace. Il est inscrit à l'inventaire de
   /confidentialite, comme tout le reste — et un contrôle le vérifie.

   HAUT ET BAS NE S'AFFICHENT PAS SUR UNE PAGE COURTE. Sous une page et demie
   d'écran, un bouton « bas de page » emmène à un endroit déjà visible.

   PAS DE DOUBLON. Ces flèches n'apparaissent pas là où la barre latérale sert
   déjà de navigateur de sections… si, justement : la barre navigue ENTRE les
   rubriques, les flèches parcourent la page et le fil. Mais elles ne se
   posent pas deux fois, et le garde ci-dessous en répond. */
(function () {
  "use strict";

  if (window.__FLECHES) return;
  window.__FLECHES = true;

  var CLE_ORDRE = "cpinfo.ordre";
  /* Sous une page et demie d'écran à faire défiler, « haut » et « bas »
     désignent des endroits déjà visibles. Mesure reprise de `fleches.js` des
     autres sites du cabinet, pour que les trois se comportent pareil. */
  var SEUIL = 1.5;

  function t(c) { return (window.L && window.L.t) ? window.L.t(c) : c; }
  function esc(x) {
    return String(x == null ? "" : x).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  /* ── L'ORDRE DE LECTURE ──────────────────────────────────────────────── */

  function noter(ids, dit) {
    if (!ids || !ids.length) return;
    try {
      sessionStorage.setItem(CLE_ORDRE, JSON.stringify(
        { ids: ids, dit: dit || "", quand: Date.now() }));
    } catch (e) { /* sans stockage, les flèches diront qu'elles ne savent pas */ }
  }

  function ordre() {
    try {
      var v = JSON.parse(sessionStorage.getItem(CLE_ORDRE) || "null");
      return (v && Array.isArray(v.ids) && v.ids.length) ? v : null;
    } catch (e) { return null; }
  }

  /* L'identifiant de la fiche affichée vient de l'ADRESSE, jamais du contenu
     rendu : les flèches se posent avant que la fiche soit revenue du serveur,
     et une flèche qui n'apparaîtrait qu'après le chargement arriverait après
     le lecteur. */
  function ficheCourante() {
    var m = location.pathname.match(/^\/fiche\/([^/.]+)$/);
    return m ? decodeURIComponent(m[1]) : null;
  }

  /* ── LE DÉFILEMENT ───────────────────────────────────────────────────── */

  function douce() {
    try { return !window.matchMedia("(prefers-reduced-motion: reduce)").matches; }
    catch (e) { return true; }
  }

  function hauteurDefilable() {
    var d = document.documentElement;
    return Math.max(0, d.scrollHeight - window.innerHeight);
  }

  function assezLongue() {
    return hauteurDefilable() > window.innerHeight * (SEUIL - 1);
  }

  function aller(y) {
    window.scrollTo({ top: y, behavior: douce() ? "smooth" : "auto" });
  }

  /* ── LA RÉSOLUTION DES QUATRE SENS ───────────────────────────────────────
     Chaque entrée rend { faire, dit } — ou { dit } seul, et la flèche est
     alors éteinte avec ce motif pour infobulle. AUCUNE ne rend une fonction
     sans intitulé : c'est ce qui interdit le bouton muet. */

  /* LES RUBRIQUES DE LA PAGE — LUES DANS LA PAGE, comme celles de la barre
     latérale. Sur une page qui n'est pas une fiche, c'est ce que ← et →
     parcourent : il y a bien une suite ordonnée, et sauter de rubrique en
     rubrique sur un fil de quatre-vingt-dix-huit fiches est le geste qu'on
     fait vraiment. Une liste écrite ici promettrait une rubrique retirée. */
  var MARGE_HAUT = 90;   /* la barre de filtres est collante */

  function rubriques() {
    /* MASQUÉE, UNE RUBRIQUE N'EST PAS UNE ÉTAPE. Sur la page d'abonnement,
       les rubriques du panneau caché avaient un rectangle de hauteur nulle en
       haut de page : la flèche « rubrique suivante » se croyait donc arrivée
       à la dernière, et s'éteignait alors qu'il restait tout à parcourir. */
    return Array.prototype.slice.call(
      document.querySelectorAll("main h2.rubrique[id]"))
      .filter(function (h) { return h.getClientRects().length > 0; });
  }

  function titreDe(h) {
    var c = h.querySelector("span[id]");
    var premier = h.querySelector("span:not([id])");
    var brut = premier ? premier.textContent
      : (c ? h.textContent.replace(c.textContent, "") : h.textContent);
    var s = brut.replace(/\s+/g, " ").trim();
    var i = s.indexOf(" — ");
    return i > 0 ? s.slice(0, i) : s;
  }

  function rangRubrique(hs) {
    /* CELLE OÙ L'ON EST : la dernière dont le titre est passé sous la marge
       haute. Prendre la plus proche du centre ferait reculer d'une rubrique
       au moment où l'on vient d'en atteindre une. */
    var r = -1;
    hs.forEach(function (h, i) {
      if (h.getBoundingClientRect().top <= MARGE_HAUT + 1) r = i;
    });
    return r;
  }

  function sens() {
    var o = ordre(), id = ficheCourante();
    var rang = (o && id) ? o.ids.indexOf(id) : -1;
    var n = o ? o.ids.length : 0;

    function versFiche(i) {
      var suite = o.ids[i];
      return {
        faire: function () { location.href = "/fiche/" + encodeURIComponent(suite); },
        dit: t(i < rang ? "fl.prec" : "fl.suiv") + " — "
             + t("fl.rang").replace("{r}", i + 1).replace("{n}", n)
             + (o.dit ? " · " + o.dit : "")
      };
    }

    function eteinte(cle) {
      /* UNE FLÈCHE SANS EMPLOI S'ÉTEINT EN DISANT POURQUOI. Un bouton éteint
         qui explique vaut mieux qu'un bouton allumé qui ne fait rien, et mieux
         qu'un bouton absent dont on se demande s'il a disparu. */
      return { dit: t(cle) };
    }

    var g, d;
    if (rang > 0) g = versFiche(rang - 1);
    else if (rang === 0) g = eteinte("fl.prem");

    if (rang >= 0 && rang < n - 1) d = versFiche(rang + 1);
    else if (rang === n - 1 && n) d = eteinte("fl.dern");

    /* HORS FICHE — ou sur une fiche ouverte par un lien direct —, ← et →
       parcourent les RUBRIQUES de la page. C'est la seule suite ordonnée que
       cette page-là possède, et elle en possède une : laisser les deux flèches
       mortes sur la première page du site aurait fait de la moitié de la croix
       un ornement. */
    if (!g || !d) {
      var hs = rubriques();
      if (hs.length > 1) {
        var r = rangRubrique(hs);
        var versRub = function (i) {
          return {
            faire: function () {
              window.scrollTo({
                top: Math.max(0, hs[i].getBoundingClientRect().top
                                 + window.pageYOffset - MARGE_HAUT),
                behavior: douce() ? "smooth" : "auto"
              });
            },
            dit: t(i < r ? "fl.rub.prec" : "fl.rub.suiv") + " — " + titreDe(hs[i])
          };
        };
        if (!g) g = r > 0 ? versRub(r - 1) : eteinte("fl.rub.prem");
        if (!d) d = r < hs.length - 1 ? versRub(r + 1) : eteinte("fl.rub.dern");
      } else {
        if (!g) g = eteinte(id ? "fl.sansfil" : "fl.horsfiche");
        if (!d) d = eteinte(id ? "fl.sansfil" : "fl.horsfiche");
      }
    }

    var longue = assezLongue();
    return {
      haut: longue ? { faire: function () { aller(0); }, dit: t("fl.haut") }
                   : { dit: t("fl.courte") },
      bas: longue ? { faire: function () { aller(hauteurDefilable()); }, dit: t("fl.bas") }
                  : { dit: t("fl.courte") },
      gauche: g,
      droite: d
    };
  }

  /* ── LA POSE ─────────────────────────────────────────────────────────── */

  var CASES = [
    ["haut", "↑", "fl-h"], ["gauche", "←", "fl-g"],
    ["droite", "→", "fl-d"], ["bas", "↓", "fl-b"]
  ];

  function peindre() {
    var boite = document.getElementById("fl");
    if (!boite) return;
    var s = sens();
    boite.setAttribute("aria-label", t("fl.titre"));
    CASES.forEach(function (c) {
      var b = boite.querySelector("." + c[2]);
      if (!b) return;
      var e = s[c[0]];
      b.disabled = !e.faire;
      b.title = e.dit;
      b.setAttribute("aria-label", e.dit);
      b.__faire = e.faire || null;
    });
  }

  function poser() {
    if (document.getElementById("fl")) return;
    var boite = document.createElement("div");
    boite.className = "fl";
    boite.id = "fl";
    boite.setAttribute("role", "group");
    var h = "";
    CASES.forEach(function (c) {
      h += '<button type="button" class="fl-b-t ' + c[2] + '">'
        + esc(c[1]) + "</button>";
    });
    boite.innerHTML = h;
    document.body.appendChild(boite);
    boite.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (b && b.__faire) b.__faire();
    });
    peindre();
  }

  function demarrer() {
    poser();
    /* La page s'allonge quand les fiches arrivent, et la fiche ouverte change
       de rang quand le lecteur revient au fil : les quatre sens sont donc
       recalculés à chaque événement qui peut les changer, jamais une fois
       pour toutes. */
    document.addEventListener("langue", peindre);
    window.addEventListener("resize", peindre);
    /* LA RUBRIQUE COURANTE CHANGE AU DÉFILEMENT, donc les deux flèches
       latérales aussi. Étranglé par `requestAnimationFrame` : recalculer
       quatre sens à chaque événement de défilement ferait tressauter une page
       de quatre-vingt-dix-huit fiches. */
    var enAttente = false;
    window.addEventListener("scroll", function () {
      if (enAttente) return;
      enAttente = true;
      requestAnimationFrame(function () { enAttente = false; peindre(); });
    }, { passive: true });
    var m = document.querySelector("main");
    if (m && typeof MutationObserver !== "undefined") {
      var attente = null;
      new MutationObserver(function () {
        if (attente) return;
        attente = setTimeout(function () { attente = null; peindre(); }, 120);
      }).observe(m, { childList: true, subtree: true,
                      attributes: true, attributeFilter: ["hidden", "class"] });
    }
  }

  window.FL = { noter: noter, ordre: ordre };

  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", demarrer);
  else demarrer();
})();
