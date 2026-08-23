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

  /* ── RIEN N'EST ÉCRIT SANS ACCORD ────────────────────────────────────────
     CETTE MÉMOIRE EST LA SEULE CHOSE DE CE SITE QUI S'ÉCRIVE TOUTE SEULE. La
     langue, le repli de la barre, le jeton de session sont écrits parce que
     vous avez cliqué : ils sont le service demandé, et l'article 5(3) de la
     directive ePrivacy les exempte. Celle-ci s'écrit AU FIL DE LA LECTURE,
     sans geste de votre part — elle n'est donc pas exemptée, et elle attend.

     LE DÉFAUT EST LE REFUS, y compris si `vieprivee.js` manque : sans lui,
     `window.VP` est absent, et une porte absente doit se lire fermée. Une
     mémoire qui s'écrirait « en attendant que le module de consentement
     charge » serait exactement le contournement que ce contrôle interdit. */
  function autorise() {
    return !!(window.VP && window.VP.accorde && window.VP.accorde("memoire"));
  }

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
      if (autorise()) lire().forEach(function (id) { _lues[id] = true; });
    }
    return _lues;
  }

  function estLue(id) { return autorise() && !!ensemble()[id]; }

  /* Rend `true` si l'état vient de CHANGER — c'est ce qui déclenche la
     pulsation. Marquer une fiche déjà lue ne doit rien faire clignoter. */
  function marquer(id) {
    if (!autorise() || !id || estLue(id)) return false;
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

  /* L'ACCORD PEUT ARRIVER APRÈS LA PAGE. Le lecteur répond au bandeau alors
     que soixante cartes sont déjà à l'écran, marquées « non lue » parce que
     rien n'était lisible à ce moment-là. L'ensemble est donc reconstruit, et
     `lecture-effacee` fait repeindre les cartes — le même signal que
     l'effacement, parce que c'est le même besoin : l'état affiché a changé. */
  document.addEventListener("accord", function (e) {
    if (!e.detail || e.detail.cle !== "memoire") return;
    _lues = null;
    document.dispatchEvent(new CustomEvent("lecture-effacee"));
  });

  window.LU = {
    estLue: estLue, marquer: marquer, oublier: oublier,
    combien: combien, classe: classe, pulser: pulser,
    /* Ce que la barre affiche à côté du compte : sans accord, « 0 à lire »
       serait faux — ce n'est pas zéro, c'est « non tenu ». */
    autorise: autorise
  };
})();
