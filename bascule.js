/* Bascule i-aes.com → Sentinel, côté navigateur.

   POURQUOI CE FICHIER EXISTE

   Chaque page de ce site porte, dans son pied de page, un lien vers le site
   institutionnel i-aes.com — et la page d'accueil y charge en plus le logo.
   Quand ce site tombe, ce sont NOS pages qui affichent un lien mort et une
   image cassée. L'indisponibilité d'un tiers ne doit pas dégrader notre propre
   service : c'est la seule partie de la bascule que nous contrôlons vraiment,
   et c'est celle-ci.

   DEUX SIGNAUX, ET ILS NE DISENT PAS LA MÊME CHOSE

   1. NOTRE SERVEUR sonde i-aes.com et publie son verdict sur /api/veille-iaes.
      Il est fiable — vraie requête HTTP, code de réponse lisible — mais il
      répond à la question « le site répond-il DEPUIS NOTRE HÉBERGEUR ».

   2. LE NAVIGATEUR DU VISITEUR charge une image connue d'i-aes.com. Une image
      se charge sans CORS : `onload` prouve que l'origine répond, `onerror`
      qu'elle ne répond pas — pour CE visiteur, sur SON réseau. C'est la seule
      autorité sur ce que ce visiteur-là peut atteindre.

   Les deux peuvent diverger, et c'est précisément l'intérêt d'avoir les deux :
   un visiteur derrière un pare-feu d'entreprise qui bloque i-aes.com doit
   basculer même si notre serveur, lui, voit le site debout.

   CE QU'ON NE FAIT PAS

   On ne teste pas avec `fetch()`. Une requête inter-origines qui échoue ne
   permet pas de distinguer « site injoignable » de « site debout mais sans
   en-tête CORS » : les deux lèvent la même erreur réseau, sans code. Un test
   qui confond une panne avec une politique de sécurité déclencherait des
   bascules pour rien.

   On ne redirige jamais le visiteur de force. On réécrit un lien et on dit
   pourquoi. Une redirection automatique depuis une page qui fonctionne
   arracherait le lecteur à ce qu'il était en train de lire, sur la foi d'une
   sonde qui peut se tromper. */
(function () {
  "use strict";

  var CIBLE = "i-aes.com";
  /* LE RELAIS EST PUBLIC, ET C'EST LA CONDITION DE TOUT LE RESTE.
     Il a d'abord été /sentinel. Mesuré au navigateur : un visiteur NON
     CONNECTÉ qui cliquait « i-aes.com » dans le pied de page atterrissait sur
     « Connexion — Sentinel AI ». La bascule transformait alors « le site
     institutionnel ne répond pas » en « créez un compte » — pire que le lien
     mort qu'elle devait éviter. Un seul lien y avait échappé, par exception ;
     les trois autres tombaient tous sur le formulaire.
     /relais-iaes ne garde rien, dit quel signal a déclenché la bascule, et
     REDONNE l'adresse d'origine pour que le visiteur réessaie lui-même. */
  var RELAIS = "/relais-iaes";
  /* Écrit une seule fois : l'ajout du marqueur et le contrôle « déjà posé »
     doivent viser exactement la même chaîne, sinon une seconde bascule
     l'empilerait. */
  var ETAT = " (indisponible)";
  var BALISE = "https://i-aes.com/wp-content/uploads/2026/02/LOGOv3.jpg";
  var DELAI_BALISE = 6000;

  function liens() {
    var out = [];
    var a = document.querySelectorAll('a[href*="' + CIBLE + '"]');
    for (var i = 0; i < a.length; i++) {
      /* Les liens « mailto: » portent le même domaine et ne tombent pas avec
         le site web : basculer une adresse de contact vers une page n'aurait
         aucun sens, et priverait le visiteur du seul moyen de nous écrire. */
      if (/^mailto:/i.test(a[i].getAttribute("href") || "")) continue;
      /* UN LIEN PEUT REFUSER LE RELAIS — ET PLUS AUCUN LIEN DU SITE NE LE
         FAIT. L'exception avait été posée sur l'appel « Découvrir le site
         institutionnel » quand le relais menait à /sentinel : mieux valait
         une page en panne, qui se comprend, qu'un formulaire de connexion,
         qui ne se comprend pas. Le relais est désormais public et rend
         l'adresse d'origine : l'exception coûterait au visiteur ce qu'elle
         devait lui épargner — un message d'erreur du navigateur, hors de
         notre site, sans explication ni retour.
         L'ATTRIBUT RESTE HONORÉ, et il sert : la page de relais elle-même
         porte un lien « Réessayer i-aes.com », qu'une bascule chargée là
         réécrirait vers la page déjà affichée. */
      if (a[i].hasAttribute("data-bascule-jamais")) continue;
      out.push(a[i]);
    }
    return out;
  }

  function basculer(motif) {
    var L = liens();
    if (!L.length) return 0;
    for (var i = 0; i < L.length; i++) {
      var el = L[i];
      if (el.getAttribute("data-bascule")) continue;
      el.setAttribute("data-bascule", motif);
      el.setAttribute("data-href-origine", el.getAttribute("href"));
      el.setAttribute("href", RELAIS + "?bascule=" + encodeURIComponent(motif)
        + "&depuis=" + encodeURIComponent(CIBLE));
      el.removeAttribute("target");
      /* L'INTITULÉ DISAIT « Sentinel », ET C'EST DEVENU FAUX. Tant que le
         relais menait à /sentinel, remplacer « i-aes.com » par « Sentinel »
         était la seule façon de ne pas mentir sur la destination. Le relais
         mène maintenant à une page qui PARLE d'i-aes.com et en redonne
         l'adresse : effacer le domaine de l'intitulé effacerait justement le
         sujet du lien.
         ON AJOUTE DONC UN ÉTAT, AU LIEU DE CHANGER DE SUJET — et on l'ajoute
         DANS LE TEXTE, pas seulement dans le `title` : un title ne s'ouvre
         pas au doigt, et le visiteur au téléphone ne le lirait jamais. */
      var t = (el.textContent || "").trim();
      if (t && t.indexOf(CIBLE) >= 0 && t.indexOf(ETAT) < 0) el.textContent = t + ETAT;
      var dit = "Le site " + CIBLE + " ne répond pas — ce lien explique pourquoi "
        + "et redonne l'adresse.";
      el.setAttribute("title", dit);
      /* Le logo et l'icône n'ont pas de texte : sans libellé accessible, leur
         changement d'état ne serait annoncé à personne. */
      if (!t) el.setAttribute("aria-label", dit);
    }
    document.documentElement.setAttribute("data-iaes", "injoignable");
    try {
      window.dispatchEvent(new CustomEvent("bascule-iaes", { detail: { motif: motif, n: L.length } }));
    } catch (e) { /* CustomEvent absent : la bascule reste faite, seul l'événement manque */ }
    return L.length;
  }

  /* Signal 2 : le navigateur du visiteur. Une image se charge sans CORS, ce qui
     en fait le seul test inter-origines dont le résultat soit interprétable. */
  function baliseImage(apres) {
    var fini = false;
    var img = new Image();
    var minuteur = setTimeout(function () {
      if (fini) return;
      fini = true;
      img.src = "";
      apres(false, "delai");
    }, DELAI_BALISE);
    img.onload = function () {
      if (fini) return;
      fini = true; clearTimeout(minuteur); apres(true, "image chargée");
    };
    img.onerror = function () {
      if (fini) return;
      fini = true; clearTimeout(minuteur); apres(false, "image en échec");
    };
    /* Horodatage en paramètre : sans lui, une image déjà en cache répondrait
       « disponible » alors que l'origine est tombée depuis. */
    img.src = BALISE + (BALISE.indexOf("?") >= 0 ? "&" : "?") + "_v=" + Date.now();
  }

  function demarrer() {
    if (!liens().length) return;

    /* Signal 1, sans bloquer : une page ne doit jamais attendre le verdict
       d'une sonde pour s'afficher. */
    try {
      fetch("/api/veille-iaes", { credentials: "same-origin" })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          if (j && j.ok && j.bascule) basculer("serveur");
        })
        .catch(function () { /* la veille est indisponible : on garde les liens */ });
    } catch (e) { /* pas de fetch : le signal 2 reste */ }

    /* Signal 2 : ce que CE visiteur peut atteindre. Il prime, parce qu'il
       décrit sa situation à lui — pas celle de notre hébergeur. */
    baliseImage(function (joignable, detail) {
      if (!joignable) basculer("navigateur:" + detail);
      try {
        window.__iaesBalise = { joignable: joignable, detail: detail, le: new Date().toISOString() };
      } catch (e) { /* rien à signaler */ }
    });
  }

  /* Exposé pour la recette et pour les pages qui veulent afficher l'état. */
  window.basculeIaes = { basculer: basculer, liens: liens, cible: CIBLE, relais: RELAIS };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", demarrer);
  } else {
    demarrer();
  }
})();
