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

   LE CONTOUR VERT CLIGNOTE, ET VOICI À QUELLES CONDITIONS. Ce commentaire
   disait auparavant que le clignotement permanent avait été « écarté ». Il
   avait tort sur un point : les règles d'accessibilité ne l'interdisent pas,
   elles l'encadrent, et l'encadrement est tenable.

     · WCAG 2.3.1 vise trois éclats PAR SECONDE et au-delà — le seuil du
       risque de crise pour les personnes photosensibles. Le contour bat une
       fois toutes les une seconde et demie, soit un vingtième de ce seuil, et
       ce qui varie est l'opacité d'un filet de deux pixels, pas la luminance
       d'une surface.
     · WCAG 2.2.2 exige qu'un clignotement de plus de cinq secondes puisse
       être ARRÊTÉ. Il peut l'être de deux façons, et aucune ne demande de
       chercher : le réglage `prefers-reduced-motion` du système le coupe
       d'office, et la barre latérale porte un interrupteur.
     · SEUL LE VERT BAT. Le bleu est l'état par défaut de tout le corpus :
       quatre-vingt-dix-huit contours battant ensemble rendraient la page
       inutilisable, et le mouvement ne dirait plus rien puisqu'il serait
       partout.

   CE QUI A MOTIVÉ LA RÉÉCRITURE, ce n'est pas le clignotement : c'est que le
   repère ne se VOYAIT PAS. Il tenait sur trois pixels du seul bord gauche, en
   deux teintes sombres et voisines. La mécanique marchait ; personne ne
   pouvait le constater. */
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

  /* ── L'INTERRUPTEUR DU CLIGNOTEMENT ─────────────────────────────────────
     WCAG 2.2.2 EXIGE QU'UN CLIGNOTEMENT DE PLUS DE CINQ SECONDES PUISSE ÊTRE
     ARRÊTÉ par celui qui le subit. Deux mécanismes le permettent ici, et ils
     ne servent pas la même personne :

       · `prefers-reduced-motion` le coupe d'office, sans un geste — la
         feuille de style s'en charge. C'est le seul chemin pour qui a réglé
         son système une fois pour toutes et n'a pas à le redire site par site.
       · CET INTERRUPTEUR-CI sert l'autre cas, plus fréquent : quelqu'un qui
         n'a rien réglé et que ce mouvement-ci gêne, ici, maintenant.

     IL S'ÉCRIT SANS ACCORD, ET C'EST RÉGULIER. Il n'est écrit que si vous
     cliquez, il ne dit rien de vous, et l'article 5(3) exempte ce qui est le
     service demandé — comme la langue ou le repli de la barre. Le refus de la
     MÉMOIRE DE LECTURE ne l'emporte donc pas : ce refus porte sur ce que vous
     lisez, pas sur la vitesse d'une animation. */
  var CLE_CLI = "cpinfo.clignote";

  function clignote() {
    try { return localStorage.getItem(CLE_CLI) !== "non"; }
    catch (e) { return true; }   /* stockage refusé : le défaut reste le défaut */
  }

  /* LE RÉGLAGE DU SYSTÈME EST LU, PAS DEVINÉ. La barre et le fil doivent
     pouvoir dire « votre système l'a déjà coupé » plutôt que proposer
     d'arrêter ce qui ne bouge pas — un bouton qui ne fait rien de visible
     apprend au lecteur à se méfier de tous les autres. */
  function motionReduit() {
    try {
      return !!(window.matchMedia
                && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    } catch (e) { return false; }
  }

  function poserFixe() {
    document.documentElement.classList.toggle("cp-fixe", !clignote());
  }

  function clignoter(oui) {
    try { localStorage.setItem(CLE_CLI, oui ? "oui" : "non"); } catch (e) {}
    poserFixe();
    document.dispatchEvent(new CustomEvent("clignotement",
                                           { detail: { oui: !!oui } }));
  }

  /* POSÉ AVANT LA PREMIÈRE CARTE. Les cartes sont composées par `veille.js`
     après un aller-retour réseau : la classe est en place bien avant qu'une
     seule d'entre elles existe, et personne ne voit battre un contour qu'il
     avait justement demandé d'arrêter. */
  poserFixe();

  /* LA CLASSE POSÉE SUR UNE CARTE — et le cas où il ne faut RIEN poser.
     ──────────────────────────────────────────────────────────────────
     ELLE RENDAIT « neuf » QUAND LA MÉMOIRE N'EST PAS TENUE, et c'était un
     mensonge tranquille. Sans accord, ce site ne SAIT PAS ce que vous avez
     lu ; peindre les quatre-vingt-dix-huit cartes en « à lire » affirme que
     vous n'avez rien lu, ce qui est une autre chose. Le lecteur voyait alors
     un code de couleur parfaitement uniforme et en concluait, à juste titre,
     qu'il ne distinguait rien.

     Sans accord, la carte ne porte donc AUCUNE marque, et le fil dit pourquoi
     en toutes lettres — voir `direRepere()` dans `veille.js`. Une absence
     expliquée vaut mieux qu'une affirmation fausse. */
  function classe(id) {
    if (!autorise()) return "";
    return estLue(id) ? "lu" : "neuf";
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
    /* `pulser` A ÉTÉ RETIRÉE. Elle posait trois battements sur la carte qui
       VENAIT de changer d'état. Depuis que le contour vert clignote en
       permanence, ce supplément ne dit plus rien de neuf : il ajoutait du
       mouvement là où il y en avait déjà, et deux animations sur le même
       élément se disputaient la même propriété. */
    combien: combien, classe: classe,
    /* Ce que la barre affiche à côté du compte : sans accord, « 0 à lire »
       serait faux — ce n'est pas zéro, c'est « non tenu ». */
    autorise: autorise,
    clignote: clignote, clignoter: clignoter, motionReduit: motionReduit
  };
})();
