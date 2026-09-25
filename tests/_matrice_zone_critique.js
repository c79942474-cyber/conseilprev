/* LA LIGNE « ZONE CRITIQUE » DE LA MATRICE, RENDUE PAR LE VRAI CODE.

   Ce harnais DÉCOUPE sentinel.page.js — de la table des libellés jusqu'au
   `.join('')` qui ferme la carte — et l'exécute tel quel sur des systèmes
   d'essai. Rien n'est recopié : si la ligne change dans la page, elle change
   ici, et la règle mesure ce que le navigateur peindra.

   Reçoit en argument le chemin de sentinel.page.js ; écrit sur la sortie le
   HTML des lignes, un JSON {html}. */
'use strict';
const fs = require('fs');
const SRC = fs.readFileSync(process.argv[2], 'utf8');

const DEB = "  var CLASSIF_LABELS = {inacceptable:";
const FIN = "  }).join('');";
const i = SRC.indexOf(DEB);
if (i < 0) throw new Error("la table des libellés de matriceRender est introuvable");
const j = SRC.indexOf(FIN, i);
if (j < 0) throw new Error("la fin de la carte « zone critique » est introuvable");
const CORPS = SRC.slice(i, j + FIN.length);

/* LES AIDES QUE LA LIGNE EMPLOIE, PRISES DANS LA PAGE AUSSI : le marquage des
   données saisies est ce qui décide si un morceau se traduit ou non. */
const d = SRC.indexOf("function sentDonneeEch(");
const AIDES = SRC.slice(d, SRC.indexOf("window.sentDonnee = sentDonnee;", d));
const aides = new Function(AIDES + "\nreturn {sentDonnee, sentDonneeEch, SENT_ATTR_DONNEE};")();

function matriceIco() { return '🤖'; }

/* QUATRE SYSTÈMES, QUATRE COMBINAISONS — dont celles que la mesure navigateur
   a relevées en français sur la page `matrice`. */
const CRITIQUES = [
  { id: 1, nom: "Scoring credit automatise", secteur: "Finance",
    classification: "haut", statut_conformite: "a_evaluer", score_risque: 8 },
  { id: 2, nom: "Chatbot service client", secteur: "IT",
    classification: "minimal", statut_conformite: "a_evaluer", score_risque: 3 },
  { id: 3, nom: "Detection anomalies", secteur: "Industrie",
    classification: "haut", statut_conformite: "en_cours", score_risque: 7 },
  { id: 4, nom: "Prediction energetique", secteur: "Energie",
    classification: "a_evaluer", statut_conformite: "non_conforme", score_risque: 6 },
];

const c = { innerHTML: '' };
const rendre = new Function('critiques', 'c', 'matriceIco', 'sentDonnee', 'sentDonneeEch',
                            'SENT_ATTR_DONNEE', CORPS);
rendre(CRITIQUES, c, matriceIco, aides.sentDonnee, aides.sentDonneeEch, aides.SENT_ATTR_DONNEE);
process.stdout.write(JSON.stringify({ html: c.innerHTML }));
