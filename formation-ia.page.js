/* LA PAGE D'INVITATION — CE QUE LE JAVASCRIPT AJOUTE, ET RIEN D'AUTRE.
   ══════════════════════════════════════════════════════════════════════

   LA PAGE SE LIT SANS CE FICHIER, ET C'EST LA RÈGLE QUI A DÉCIDÉ DE SA
   FORME. C'est l'adresse qu'on partage : la date, le lieu, le programme,
   les conditions et le lien d'inscription sont dans le HTML servi. Un
   visiteur dont le script ne se charge pas — réseau coupé en pleine page,
   extension zélée, lecteur de courriel qui ouvre un aperçu — doit quand
   même pouvoir lire l'invitation et s'inscrire.

   CE FICHIER N'AJOUTE DONC QUE DEUX CHOSES : le téléchargement du fichier
   d'agenda (il se fabrique dans le navigateur, sans aller-retour) et la
   phrase qui dit quoi faire quand un clic sur « mailto: » n'ouvre rien —
   sur un poste sans client de courrier, ce clic ne produit AUCUN signal
   visible, et le visiteur croit que la page est cassée.

   LES FAITS VIENNENT DE /evenement.js, PARTAGÉ AVEC LE BANDEAU DE
   L'ACCUEIL. Deux fabricants de .ics finiraient par poser deux séances
   différentes. */
(function () {
  "use strict";

  var statut = document.getElementById('iv-statut');
  var agenda = document.getElementById('iv-agenda');
  var inscrire = document.getElementById('iv-inscrire');
  var minuterie = null;

  function dire(t) {
    if (!statut) return;
    statut.textContent = t;
    clearTimeout(minuterie);
    minuterie = setTimeout(function () { statut.textContent = ''; }, 12000);
  }

  /* LE BOUTON D'AGENDA N'EXISTE QUE SI LE SCRIPT PARTAGÉ EST LÀ. Sans lui,
     il resterait affiché et ne ferait rien : un bouton mort est pire qu'un
     bouton absent, parce qu'il se présente comme une promesse. */
  if (agenda) {
    if (!window.CPEvenement) {
      agenda.hidden = true;
    } else {
      agenda.addEventListener('click', function () {
        window.CPEvenement.telechargerIcs();
        dire("Fichier agenda téléchargé : ouvrez-le pour ajouter la "
             + "formation à votre calendrier (rappel la veille).");
      });
    }
  }

  if (inscrire) {
    inscrire.addEventListener('click', function () {
      dire("Votre messagerie s'ouvre avec l'e-mail d'inscription pré-rempli. "
           + "Si rien ne s'ouvre, écrivez à "
           + ((window.CPEvenement && window.CPEvenement.inscription)
              || 'christophe.cerf@outlook.com') + ".");
    });
  }
})();
