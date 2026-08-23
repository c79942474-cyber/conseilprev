/* CE QUE VOUS AVEZ DÉJÀ LU — et où cela reste.
   ────────────────────────────────────────────
   POURQUOI CETTE MÉMOIRE EXISTE. Le fil sert quatre-vingt-dix-huit fiches et
   s'allonge à chaque collecte. Sans repère, un lecteur qui revient chaque
   semaine relit les mêmes têtes de liste et manque ce qui est arrivé entre
   deux visites — le contraire de ce qu'une veille doit produire.

   ELLE NE QUITTE PAS VOTRE NAVIGATEUR. Les identifiants lus sont écrits dans
   `localStorage`, jamais envoyés au serveur, jamais rattachés à un compte.
   Ce site ne veut pas savoir ce que vous lisez : il n'en a aucun usage
   légitime, et en garder trace côté serveur créerait exactement le fichier
   qu'un industriel redoute en consultant une veille sur ses propres
   vulnérabilités. La page le dit à l'écran, elle ne se contente pas de le
   faire.

   LE CLIGNOTEMENT PERMANENT A ÉTÉ ÉCARTÉ, ET C'EST UN REFUS ARGUMENTÉ. Les
   règles d'accessibilité l'interdisent : au-delà de cinq secondes, tout
   clignotement doit pouvoir être arrêté (WCAG 2.2.2), et rien ne doit
   dépasser trois éclats par seconde (WCAG 2.3.1) — au-delà, c'est un risque
   de crise pour les personnes photosensibles. Une soixantaine de cartes
   clignotant en continu rendrait par ailleurs la page illisible pour tout le
   monde. La pulsation joue donc TROIS FOIS puis s'arrête, et seulement sur
   les fiches dont l'état vient de changer — c'est là qu'un signal sert. */
(function () {
  "use strict";

  var CLE = "cpinfo.lues";
  var MAXI = 600;      /* au-delà, les plus anciennes sortent */

  function lire() {
    try {
      var v = JSON.parse(localStorage.getItem(CLE) || "[]");
      return Array.isArray(v) ? v : [];
    } catch (e) { return []; }   /* navigation privée, stockage refusé */
  }

  function ecrire(l) {
    try { localStorage.setItem(CLE, JSON.stringify(l.slice(-MAXI))); }
    catch (e) { /* le site reste utilisable sans mémoire de lecture */ }
  }

  var _lues = null;
  function ensemble() {
    if (!_lues) {
      _lues = {};
      lire().forEach(function (id) { _lues[id] = true; });
    }
    return _lues;
  }

  function estLue(id) { return !!ensemble()[id]; }

  /* Rend `true` si l'état vient de CHANGER — c'est ce qui déclenche la
     pulsation. Marquer une fiche déjà lue ne doit rien faire clignoter. */
  function marquer(id) {
    if (!id || estLue(id)) return false;
    ensemble()[id] = true;
    var l = lire();
    l.push(id);
    ecrire(l);
    return true;
  }

  function oublier() {
    _lues = {};
    try { localStorage.removeItem(CLE); } catch (e) {}
    document.dispatchEvent(new CustomEvent("lecture-effacee"));
  }

  function combien() { return Object.keys(ensemble()).length; }

  /* LA CLASSE POSÉE SUR UNE CARTE. `lu` ou `neuf` — jamais rien : une carte
     sans marque laisserait croire que la mémoire est en panne. */
  function classe(id) { return estLue(id) ? "lu" : "neuf"; }

  /* LA PULSATION, BORNÉE. Elle est retirée à la fin de l'animation pour que
     rien ne reste en mouvement, et elle n'est pas posée du tout si le lecteur
     a demandé moins d'animation. */
  function pulser(el) {
    if (!el) return;
    try {
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    } catch (e) { /* navigateur ancien : on pulse */ }
    el.classList.add("pulse");
    setTimeout(function () { el.classList.remove("pulse"); }, 2400);
  }

  window.LU = {
    estLue: estLue, marquer: marquer, oublier: oublier,
    combien: combien, classe: classe, pulser: pulser
  };
})();
