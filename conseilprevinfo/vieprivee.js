/* CE QUE CE SITE GARDE DE VOUS — et pourquoi il n'y a pas de mur de cookies.
   ─────────────────────────────────────────────────────────────────────────
   CE SITE NE POSE AUCUN COOKIE. Pas un seul : ni de mesure d'audience, ni de
   publicité, ni de session — le serveur n'appelle `set_cookie` nulle part, et
   `test_securite` refuse que cela change sans qu'on s'en aperçoive. Ce qu'il
   garde tient dans le stockage local du navigateur, et se compte sur les
   doigts d'une main.

   D'OÙ LE REFUS D'UN BANDEAU « ACCEPTER TOUT ». Il y en aurait un ici pour la
   même raison qu'il y en a partout : parce que c'est devenu le geste attendu.
   Mais un bandeau qui demande d'accepter des cookies inexistants est un
   mensonge poli — il apprend au lecteur que ce site fait comme les autres,
   alors que sa seule promesse est de ne pas le faire. Et il vide de son sens
   le vrai consentement, celui qu'un site devrait demander pour ce qu'il pose
   RÉELLEMENT.

   CE QUI EST DEMANDÉ, ET CE QUI NE L'EST PAS. L'article 5(3) de la directive
   ePrivacy — celui qui fonde le consentement — exempte ce qui est
   « strictement nécessaire à la fourniture du service EXPRESSÉMENT DEMANDÉ
   par l'utilisateur ». Passé au crible, l'inventaire se coupe en deux :

     · `cpinfo.langue`  — vous avez cliqué sur EN. Le garder EST le service
                          demandé. Exempté.
     · `cpinfo.barre`   — vous avez replié la barre. Idem. Exempté.
     · `cpinfo.jeton`   — jeton de session, écrit à votre connexion, effacé à
                          la fermeture de l'onglet. Authentification : exempté.
     · `cpinfo.accord`  — votre réponse à la question ci-dessous. Garder un
                          REFUS est nécessaire pour l'honorer ; la CNIL le dit
                          explicitement. Exempté.
     · `cpinfo.lues`    — les fiches que vous avez ouvertes. Écrit TOUT SEUL,
                          au fil de la lecture, sans que vous l'ayez demandé.
                          CE N'EST PAS EXEMPTÉ. C'est la seule chose que ce
                          site vous demande, et il ne l'écrit pas avant.

   UN SEUL ÉLÉMENT, DONC UNE SEULE QUESTION. Refuser coûte exactement un clic,
   comme accepter, et le bouton n'est ni plus petit ni plus pâle : un
   consentement obtenu par la fatigue n'en est pas un. Ignorer le bandeau vaut
   refus — c'est le défaut, et il n'y a rien à faire pour l'obtenir.

   ET LA RÉPONSE SE CHANGE. `/confidentialite` porte l'inventaire complet et
   les deux boutons, à tout moment. Un consentement qu'on ne peut pas retirer
   aussi facilement qu'on l'a donné n'est pas valable, et c'est écrit dans le
   texte, pas seulement dans les commentaires de ce fichier. */
(function () {
  "use strict";

  var CLE = "cpinfo.accord";

  /* LES ÉLÉMENTS SOUMIS À ACCORD. Un seul aujourd'hui — et la table existe
     pour que le jour où un second apparaît, il faille l'inscrire ici plutôt
     que d'écrire un `if` de plus quelque part. */
  var SOUMIS = { memoire: true };

  function tout() {
    try {
      var v = JSON.parse(localStorage.getItem(CLE) || "{}");
      return (v && typeof v === "object") ? v : {};
    } catch (e) { return {}; }     /* navigation privée : rien n'est gardé */
  }

  function poser(cle, valeur) {
    var v = tout();
    v[cle] = valeur;
    try { localStorage.setItem(CLE, JSON.stringify(v)); }
    catch (e) { /* sans mémoire, la réponse ne vaut que pour cette page */ }
    _memo = v;
  }

  /* Gardé en mémoire de page : `accorde()` est appelé à chaque fiche rendue,
     et lire `localStorage` soixante fois par affichage n'a aucun intérêt. */
  var _memo = null;
  function etat() { if (!_memo) _memo = tout(); return _memo; }

  /* LE DÉFAUT EST LE REFUS. Une valeur absente n'est pas « pas encore
     demandé, donc on peut » : c'est « non ». */
  function accorde(cle) {
    if (!SOUMIS[cle]) return true;         /* hors périmètre : exempté */
    return etat()[cle] === "oui";
  }

  function repondu(cle) {
    var v = etat()[cle];
    return v === "oui" || v === "non";
  }

  function repondre(cle, oui) {
    poser(cle, oui ? "oui" : "non");
    /* UN REFUS EFFACE CE QUI AVAIT ÉTÉ GARDÉ. Sans cela, retirer son accord
       laisserait le fichier en place — un consentement retiré qui ne retire
       rien n'est pas un consentement retiré. */
    if (!oui && cle === "memoire" && window.LU && window.LU.oublier)
      window.LU.oublier();
    document.dispatchEvent(new CustomEvent("accord", { detail: { cle: cle, oui: !!oui } }));
    peindre();
  }

  function t(c) { return (window.L && window.L.t) ? window.L.t(c) : c; }
  function esc(x) {
    return String(x == null ? "" : x).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  /* ── LE BANDEAU ──────────────────────────────────────────────────────────
     IL NE BLOQUE RIEN. Ni voile, ni fenêtre modale, ni piège au défilement :
     le journal se lit pendant qu'il est là, et il ne réapparaît pas une fois
     répondu. Un bandeau qui empêche de lire tant qu'on n'a pas cliqué obtient
     des clics, pas des consentements. */
  function bandeau() {
    if (repondu("memoire")) return;
    /* Sans stockage — navigation privée, stockage refusé —, rien ne sera écrit
       de toute façon : demander l'autorisation d'un geste impossible n'aurait
       aucun sens, et la réponse ne pourrait pas être gardée. */
    try { localStorage.setItem("cpinfo.essai", "1"); localStorage.removeItem("cpinfo.essai"); }
    catch (e) { return; }
    if (document.getElementById("vp-b")) return;

    var d = document.createElement("div");
    d.className = "vp-b";
    d.id = "vp-b";
    d.setAttribute("role", "region");
    d.setAttribute("aria-label", t("vp.titre"));
    d.innerHTML = '<p class="vp-t">' + esc(t("vp.titre")) + "</p>"
      + "<p>" + esc(t("vp.dit")) + "</p>"
      + '<div class="vp-a">'
      + '<button type="button" class="vp-oui">' + esc(t("vp.oui")) + "</button>"
      + '<button type="button" class="vp-non">' + esc(t("vp.non")) + "</button>"
      + '<a href="/confidentialite">' + esc(t("vp.savoir")) + "</a>"
      + "</div>";
    document.body.appendChild(d);
    d.querySelector(".vp-oui").addEventListener("click", function () { repondre("memoire", true); });
    d.querySelector(".vp-non").addEventListener("click", function () { repondre("memoire", false); });
    place(d);
  }

  /* LE BOUTON DE MENU EST EN BAS À GAUCHE, LE BANDEAU EN BAS : constaté au
     navigateur, le second recouvrait entièrement le premier, et l'unique
     moyen d'ouvrir la barre latérale disparaissait tant qu'on n'avait pas
     répondu. La hauteur du bandeau est MESURÉE et non devinée — elle dépend
     de la langue, de la largeur et de la taille de caractères du lecteur, et
     une valeur écrite en dur serait fausse pour quelqu'un. */
  function place(d) {
    var poser = function () {
      document.documentElement.style.setProperty(
        "--vp-h", Math.ceil(d.getBoundingClientRect().height) + "px");
    };
    poser();
    document.documentElement.classList.add("vp-ouvert");
    try { new ResizeObserver(poser).observe(d); }
    catch (e) { window.addEventListener("resize", poser); }
  }

  function retirer() {
    var d = document.getElementById("vp-b");
    if (d) d.parentNode.removeChild(d);
    document.documentElement.classList.remove("vp-ouvert");
    document.documentElement.style.removeProperty("--vp-h");
  }

  /* ── LES BOUTONS DE LA PAGE DE CONFIDENTIALITÉ ───────────────────────────
     Le même choix, au même endroit que son explication, et à tout moment. */
  function peindre() {
    if (repondu("memoire")) retirer(); else bandeau();
    var z = document.querySelector("[data-accord]");
    if (!z) return;
    var oui = accorde("memoire");
    z.innerHTML = '<p class="vp-etat ' + (oui ? "on" : "off") + '">'
      + esc(t(oui ? "vp.etat.on" : "vp.etat.off")) + "</p>"
      + '<div class="vp-a">'
      + '<button type="button" class="vp-oui"' + (oui ? " disabled" : "") + ">"
      + esc(t("vp.oui")) + "</button>"
      + '<button type="button" class="vp-non"' + (oui ? "" : " disabled") + ">"
      + esc(t("vp.non")) + "</button></div>";
    z.querySelector(".vp-oui").addEventListener("click", function () { repondre("memoire", true); });
    z.querySelector(".vp-non").addEventListener("click", function () { repondre("memoire", false); });
  }

  function demarrer() {
    peindre();
    document.addEventListener("langue", peindre);
  }

  window.VP = {
    accorde: accorde, repondu: repondu, repondre: repondre,
    soumis: function () { return Object.keys(SOUMIS); }
  };

  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", demarrer);
  else demarrer();
})();
