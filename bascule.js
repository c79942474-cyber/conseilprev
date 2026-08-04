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
  var RELAIS = "/sentinel";
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
      /* Le lien change de destination : il doit changer d'intitulé, sinon le
         visiteur clique sur « i-aes.com » et atterrit ailleurs sans le savoir.
         On ne touche pas aux liens dont le contenu est une image ou une icône :
         leur libellé est le title, qu'on met à jour. */
      var t = (el.textContent || "").trim();
      if (t && t.indexOf(CIBLE) >= 0) el.textContent = t.replace(CIBLE, "Sentinel");
      el.setAttribute("title", "Le site " + CIBLE + " ne répond pas — ce lien conduit à "
        + "Sentinel, hébergé séparément.");
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
