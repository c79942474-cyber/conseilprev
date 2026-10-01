# -*- coding: utf-8 -*-
"""prEN 18286:2025 — le système de management de la qualité de l'article 17.

CE QUE CETTE NORME EST. C'est la norme harmonisée du CEN/CLC JTC 21 écrite
sur mandat de la Commission (M/613 — C(2023) 3215) pour donner un moyen
VOLONTAIRE de se conformer à l'article 17 du Règlement (UE) 2024/1689 : le
système de management de la qualité qu'un FOURNISSEUR de système d'IA à haut
risque doit tenir. Son annexe ZA dit lesquels de ses paragraphes couvrent
lesquels alinéas de l'article 17.

ELLE EST AU STADE DE L'ENQUÊTE CEN. Elle n'est donc PAS citée au Journal
officiel, et ne confère AUCUNE présomption de conformité — le texte le dit
lui-même : « Une fois la présente norme citée au Journal officiel… ». Le
module le répète à l'écran, parce qu'un client qui l'ignore croirait acheter
une couverture juridique qui n'existe pas encore.

═══ LE DROIT D'AUTEUR COMMANDE LA FORME DU MODULE ═══════════════════════
Le texte est la propriété du CEN et de ses membres nationaux. Aucune phrase
normative n'est reproduite : seuls les NUMÉROS et les TITRES de paragraphes
sont cités — ce qu'un index bibliographique fait — et tout ce qui les décrit,
toutes les questions du cadre d'analyse, sont rédigés par le cabinet. La même
doctrine que pour prEN 18229-3, pour la même raison.

═══ CE QUE CE MODULE CALCULE, ET QU'UNE LISTE À COCHER NE CALCULE PAS ════
LE §4.4 EST UN PROCESSUS, PAS UNE CASE. Pour chacune des sept exigences
essentielles, le fournisseur CHOISIT une approche — norme harmonisée,
spécification commune, autre norme, autre solution technique — et ce choix
COMMANDE une charge de preuve différente :

    norme harmonisée ou spécification commune  → documenter l'exigence
    autre norme ou autre solution technique    → documenter CE QUI N'EST PAS
                                                 couvert, JUSTIFIER la mesure,
                                                 et produire la preuve objective

Un fournisseur qui coche « autre solution » sans la justification et la
preuve objective n'a pas une exigence à moitié tenue : il a une exigence que
l'organisme notifié rouvrira. Le moteur plafonne donc le score sur ce que la
norme exige elle-même au §4.4.3.2.2, au lieu de compter des cases.

═══ CE QUE CE MODULE REFUSE DE DIRE ═════════════════════════════════════
QUE L'ARTICLE 17 SERAIT COUVERT EN ENTIER. L'annexe ZA porte une ligne
« Non couvert » en face de l'article 17(2) — les fournisseurs qui sont des
institutions financières soumises à la législation sur les services
financiers. Ce module l'affiche plutôt que de l'omettre : un taux de 100 %
sur une norme qui déclare elle-même une lacune serait un mensonge par
arrondi.

ET QUE TENIR ISO 9001 OU ISO/IEC 42001 SUFFIRAIT. Les deux tables de
correspondance de la norme laissent DEUX paragraphes sans équivalent : le
§4.4, la stratégie de conformité réglementaire, et le §9, l'exploitation et
le contrôle. Ce sont précisément les deux que le règlement ajoute.
"""
import datetime


# ═══════════════════════════════════════════════════════════════════════════
#  1. LA SOURCE, ET SA LICENCE
# ═══════════════════════════════════════════════════════════════════════════

SOURCE = {
    "titre": "prEN 18286:2025 — Intelligence artificielle — Système de "
             "management de la qualité pour le règlement européen sur l'IA",
    "court": "prEN 18286:2025",
    "en": "Artificial intelligence — Quality management system for EU AI Act "
          "regulatory purposes",
    "editeur": "CEN/CLC JTC 21 « Intelligence artificielle » "
               "(secrétariat : DS)",
    "millesime": "2025-10",
    "ics": "03.100.70 ; 35.240.01",
    "stade": "Enquête CEN",
    "mandat": "Demande de normalisation M/613 — C(2023) 3215 de la "
              "Commission européenne",
    "vise": "Règlement (UE) 2024/1689, article 17 — système de management "
            "de la qualité du fournisseur de système d'IA à haut risque",
    #  LA PRÉSOMPTION EST LE SEUL CHAMP QUI VAILLE DE L'ARGENT, et c'est
    #  celui qu'on serait tenté d'arrondir. La norme n'est pas citée au
    #  Journal officiel : elle ne confère rien. La garde du module refuse
    #  qu'on écrive l'inverse.
    "presomption": False,
    "licence": "PROTÉGÉE PAR LE DROIT D'AUTEUR du CEN et de ses membres "
               "nationaux. Ce module ne reproduit AUCUNE phrase normative : "
               "il cite les numéros et les titres de paragraphes, comme un "
               "index, et tout le reste est rédigé par le cabinet.",
}

RESERVE_PRESOMPTION = (
    "Ce projet de norme n'est pas encore cité au Journal officiel de l'Union "
    "européenne au titre du Règlement (UE) 2024/1689 : le tenir n'ouvre "
    "aucune présomption de conformité à l'article 17. Le jour où la "
    "référence sera citée, le même travail vaudra présomption — dans les "
    "limites du tableau ZA.1, et sans l'article 17(2) que la norme déclare "
    "elle-même non couvert."
)

# ── LES CONTRADICTIONS DU DOCUMENT, DÉCLARÉES ───────────────────────────
#
# ELLES VOYAGENT AVEC LE RÉFÉRENTIEL. Un lecteur qui recompte sur le PDF doit
# retrouver ce que l'écran affiche, ou savoir pourquoi il en diffère. Les
# taire ferait croire à une table plus propre que le document.

CONTRADICTIONS = (
    {"ou": "8.3.2.1 et 8.3.2.3",
     "quoi": "Deux paragraphes portent le MÊME titre, « Exigences relatives "
             "au système d'IA », à trois numéros d'écart.",
     "fait": "Les deux sont conservés, distingués par leur numéro. Les "
             "fusionner aurait fait disparaître un paragraphe que l'annexe "
             "ZA peut viser ; les renommer aurait inventé un titre que le "
             "document ne porte pas."},
    {"ou": "Annexe B, tableau B.1",
     "quoi": "La ligne de prEN 18229-2 est intitulée « Crédibilité Partie 1 » "
             "— le même libellé que la ligne précédente, qui est bien la "
             "partie 1.",
     "fait": "La partie est rétablie d'après la référence elle-même "
             "(prEN 18229-2) et d'après l'article visé (15). Le libellé "
             "d'origine est rappelé à l'écran."},
    {"ou": "Annexe B, tableau B.1",
     "quoi": "Le tableau ne liste PAS prEN 18229-3 (supervision humaine). "
             "Il range les articles 12 à 14 sous prEN 18229-1.",
     "fait": "Le module ne l'ajoute pas au tableau : il le signale comme "
             "une norme de la famille que ce site traite déjà, en disant "
             "que le rattachement vient du site et non de l'annexe B."},
)


# ═══════════════════════════════════════════════════════════════════════════
#  2. LES SEPT CHAPITRES NORMATIFS
# ═══════════════════════════════════════════════════════════════════════════
#
# LA NORME SUIT L'ANNEXE SL, ET C'EST UNE BONNE NOUVELLE MAL COMPRISE. Un
# fournisseur qui tient déjà ISO 9001 ou ISO/IEC 42001 reconnaîtra six de ces
# sept chapitres. Il en conclura trop vite qu'il tient la norme — alors que
# les deux tables de correspondance du document laissent justement le §4.4 et
# le chapitre 9 SANS équivalent. Ce sont les deux que le règlement ajoute.

CHAPITRES = (
    {"num": "4", "nom": "Système de management de la qualité",
     "quoi": "Quelles exigences réglementaires s'appliquent, sur quel "
             "périmètre, selon quelle stratégie — et ce qu'on en documente.",
     "part": "strategie",
     "ce_qui_le_fait_tomber":
         "Un périmètre écrit pour le certificat et non pour le produit : il "
         "nomme l'entreprise, pas les systèmes d'IA à haut risque qu'elle "
         "met sur le marché. L'organisme notifié ouvre alors un dossier qui "
         "ne recouvre pas le système qu'il doit évaluer."},
    {"num": "5", "nom": "Responsabilité de la direction",
     "quoi": "La politique qualité, les rôles, et qui répond de quoi.",
     "part": "direction",
     "ce_qui_le_fait_tomber":
         "Une responsabilité réglementaire attribuée à une fonction qui n'a "
         "ni le budget ni l'autorité d'arrêter une mise sur le marché. Elle "
         "signera ce qu'on lui présentera."},
    {"num": "6", "nom": "Planification",
     "quoi": "Les risques pesant sur le fonctionnement du système de "
             "management lui-même, et les objectifs qualité.",
     "part": "direction",
     "ce_qui_le_fait_tomber":
         "Confondre les risques DU système d'IA, qui relèvent de "
         "l'article 9, avec les risques pesant sur le système de "
         "MANAGEMENT, qui sont ceux de ce chapitre. Le second reste alors "
         "vide, et personne ne le voit."},
    {"num": "7", "nom": "Support",
     "quoi": "Les ressources, les compétences, et la communication — dont "
             "celle qui se fait à des fins réglementaires.",
     "part": "direction",
     "ce_qui_le_fait_tomber":
         "Une matrice de compétences tenue pour les auditeurs et jamais "
         "pour les recrutements. Le jour où l'équipe qui sait change, "
         "personne ne s'en aperçoit."},
    {"num": "8", "nom": "Élaboration du produit",
     "quoi": "Du cycle de vie à la documentation technique : conception, "
             "développement, vérification, validation, données.",
     "part": "produit",
     "ce_qui_le_fait_tomber":
         "Une vérification qui rejoue le jeu d'essai de l'entraînement. "
         "Elle prouve que le modèle a appris, pas qu'il tient ses exigences."},
    {"num": "9", "nom": "Exploitation et contrôle",
     "quoi": "Déploiement, chaîne d'approvisionnement, changements, "
             "surveillance après commercialisation, incidents graves, "
             "non-conformités.",
     "part": "exploitation",
     "ce_qui_le_fait_tomber":
         "Une surveillance après commercialisation qui attend la "
         "réclamation. Le règlement demande une approche ACTIVE, et c'est "
         "le chapitre qu'aucune des deux normes ISO ne couvre."},
    {"num": "10", "nom": "Évaluation des performances",
     "quoi": "La revue de direction, l'amélioration, et la planification "
             "des changements du système de management.",
     "part": "performance",
     "ce_qui_le_fait_tomber":
         "Une revue de direction annuelle sur un système qui change tous "
         "les mois. Elle arrive après les décisions qu'elle devait éclairer."},
)

CHAPITRES_PAR_NUM = {c["num"]: c for c in CHAPITRES}


# ═══════════════════════════════════════════════════════════════════════════
#  3. LES SOIXANTE-CINQ PARAGRAPHES — NUMÉRO ET TITRE, RIEN D'AUTRE
# ═══════════════════════════════════════════════════════════════════════════
#
# LE TITRE EST CITÉ, L'ÉNONCÉ NE L'EST PAS. `demande` est la question que le
# cabinet pose ; elle dit ce qu'il faut montrer, dans les mots du cabinet.
# `piege` dit ce qui fait tomber ce paragraphe-là en revue.
#
# L'ORDRE EST CELUI DU DOCUMENT. Le réordonner par importance supposerait une
# hiérarchie que la norme ne pose pas.

def _p(num, titre, demande, piege=None):
    return {"num": num, "chapitre": num.split(".")[0], "titre": titre,
            "demande": demande, "piege": piege}


PARAGRAPHES = (
    # ── 4. SYSTÈME DE MANAGEMENT DE LA QUALITÉ ──────────────────────────
    _p("4.1", "Généralités",
       "Votre SMQ est-il établi par écrit, tenu à jour, et son efficacité "
       "entretenue dans le temps ?"),
    _p("4.2", "Identifier les exigences réglementaires applicables",
       "Avez-vous établi, par écrit, quelles exigences réglementaires "
       "s'appliquent à chacun de vos systèmes d'IA ?",
       "Une liste faite une fois à la conception. Un système requalifié à "
       "haut risque en cours de vie ne déclenche rien."),
    _p("4.3", "Détermination du domaine d'application du système de "
              "management de la qualité",
       "Le périmètre nomme-t-il les systèmes d'IA couverts — et dit-il ce "
       "qui en est exclu, et pourquoi ?",
       "Un périmètre qui nomme des entités juridiques plutôt que des "
       "produits : il ne permet pas de dire si LE système évalué est dedans."),
    _p("4.4.1", "Détermination de la stratégie",
       "La stratégie de conformité réglementaire est-elle déterminée et "
       "documentée, avec ses cinq composantes ?",
       "C'est la pièce qui n'a d'équivalent ni dans ISO 9001 ni dans "
       "ISO/IEC 42001 : un SMQ repris tel quel d'un certificat existant ne "
       "la porte pas."),
    _p("4.4.2", "Exigences essentielles",
       "Les sept exigences essentielles applicables à vos systèmes sont-"
       "elles identifiées une à une ?"),
    _p("4.4.3.1", "Sélection des approches",
       "Pour chaque exigence essentielle, l'approche retenue est-elle "
       "choisie et écrite — norme harmonisée, spécification commune, autre "
       "norme, ou autre solution technique ?",
       "Le choix n'est pas neutre : les deux dernières approches ouvrent "
       "une charge de preuve que les deux premières n'ont pas."),
    _p("4.4.3.2", "Sélection des mesures",
       "Les mesures retenues sont-elles documentées — et, pour les "
       "approches « autre norme » ou « autre solution », ce qui n'est pas "
       "couvert est-il écrit, justifié et prouvé ?",
       "C'est l'arithmétique du module : une approche « autre » sans "
       "justification ni preuve objective plafonne le score, parce que la "
       "norme elle-même l'exige au 4.4.3.2.2."),
    _p("4.5.1", "Documentation du système de management de la qualité",
       "La documentation du SMQ existe-t-elle, et couvre-t-elle ce que la "
       "norme attend ?"),
    _p("4.5.2", "Documentation opérationnelle",
       "La documentation opérationnelle — celle qui sert à faire, pas à "
       "prouver — est-elle tenue ?"),
    _p("4.5.3", "Mise à jour des informations documentées",
       "Les informations documentées sont-elles mises à jour quand le "
       "système, le périmètre ou la réglementation changent ?"),
    _p("4.5.4", "Maîtrise des informations documentées",
       "Une procédure documentée définit-elle approbation, diffusion, "
       "version, conservation et retrait des documents ?",
       "Cinq exigences dans un seul paragraphe : c'est celui où « on a une "
       "GED » passe pour une réponse."),

    # ── 5. RESPONSABILITÉ DE LA DIRECTION ───────────────────────────────
    _p("5.1", "Généralités",
       "La direction démontre-t-elle son engagement par des actes "
       "constatables, et non par une déclaration de politique ?"),
    _p("5.2.1", "Établissement de la politique qualité",
       "Une politique qualité est-elle établie, et dit-elle quelque chose "
       "de vos systèmes d'IA en particulier ?",
       "Une politique qualité générique recopiée d'ISO 9001 : elle passe "
       "l'audit du SMQ et ne dit rien du règlement."),
    _p("5.3", "Rôles, responsabilité et autorités",
       "Les rôles et autorités sont-ils attribués, et la personne chargée "
       "de la conformité réglementaire a-t-elle l'autorité d'arrêter une "
       "mise sur le marché ?",
       "L'alinéa (m) de l'article 17(1) ne demande pas un nom : il demande "
       "une responsabilité qui porte."),

    # ── 6. PLANIFICATION ────────────────────────────────────────────────
    _p("6.1", "Actions pour traiter les risques liés au fonctionnement du "
              "système de management",
       "Les risques pesant sur le fonctionnement du SMQ lui-même sont-ils "
       "identifiés et traités ?",
       "Ce ne sont PAS les risques du système d'IA — ceux-là relèvent de "
       "l'article 9 et du §8.1."),
    _p("6.2.1", "Objectifs qualité",
       "Des objectifs qualité mesurables sont-ils fixés ?"),
    _p("6.2.2", "Planification de la réalisation des objectifs qualité",
       "Le chemin pour les atteindre est-il planifié — qui, quoi, quand, "
       "avec quelles ressources ?"),

    # ── 7. SUPPORT ──────────────────────────────────────────────────────
    _p("7.1", "Ressources",
       "Les ressources nécessaires au SMQ sont-elles déterminées et "
       "fournies ?"),
    _p("7.2", "Compétences",
       "Les compétences requises sont-elles déterminées, et leur présence "
       "entretenue et prouvée ?"),
    _p("7.3.1", "Communication — généralités",
       "Les communications internes et externes nécessaires au SMQ sont-"
       "elles déterminées ?"),
    _p("7.3.2", "Sensibilisation",
       "Les personnes concernées savent-elles ce que le SMQ attend d'elles "
       "et ce que leur travail engage ?"),
    _p("7.3.3", "Communication à des fins réglementaires",
       "La communication avec les autorités, les organismes notifiés et "
       "les déployeurs est-elle organisée et tenue ?",
       "C'est l'alinéa (j) de l'article 17(1). Le jour d'un incident "
       "grave, c'est le seul chemin qui compte."),

    # ── 8. ÉLABORATION DU PRODUIT ───────────────────────────────────────
    _p("8.1", "Actions de traitement des risques",
       "Le système de gestion des risques de l'article 9 est-il en place, "
       "et ses actions reprises dans l'élaboration du produit ?",
       "L'annexe ZA le dit sous réserve : l'alinéa (g) n'est couvert que "
       "SI le système de gestion des risques est conforme à l'article 9."),
    _p("8.2", "Détermination des étapes du cycle de vie",
       "Les étapes du cycle de vie sont-elles déterminées, avec leurs "
       "processus et procédures ?"),
    _p("8.3.1", "Initialisation",
       "La destination du système d'IA est-elle déterminée et écrite ?",
       "La destination commande la qualification à haut risque, donc tout "
       "le reste. L'écrire après la conception, c'est la déduire du "
       "produit au lieu de l'avoir choisie."),
    _p("8.3.2.1", "Exigences relatives au système d'IA",
       "Les exigences du système d'IA sont-elles établies, et tracent-"
       "elles jusqu'aux exigences essentielles ?"),
    _p("8.3.2.2", "Passage en revue des exigences relatives au système d'IA",
       "Ces exigences sont-elles passées en revue avant d'engager la "
       "conception ?"),
    _p("8.3.2.3", "Exigences relatives au système d'IA",
       "Les exigences sont-elles tenues à jour quand la conception ou la "
       "destination évoluent ?",
       "Le document porte deux paragraphes du même titre, 8.3.2.1 et "
       "8.3.2.3 : les deux sont conservés, distingués par leur numéro."),
    _p("8.3.2.4", "Contrôles de la conception et du développement",
       "Des contrôles de conception et de développement sont-ils définis "
       "et appliqués ?"),
    _p("8.4.1", "Vérification du système d'IA",
       "La vérification démontre-t-elle que le système satisfait ses "
       "exigences ?",
       "Vérifier sur le jeu d'essai de l'entraînement prouve "
       "l'apprentissage, pas la tenue des exigences."),
    _p("8.4.2", "Validation du système d'IA",
       "La validation démontre-t-elle que le système tient sa destination "
       "dans les conditions réelles d'usage ?"),
    _p("8.5", "Gestion des données",
       "La stratégie de gestion des données est-elle établie et tenue ?",
       "C'est l'alinéa (f) de l'article 17(1), et il renvoie à "
       "l'article 10 : l'ensemble de la gouvernance des jeux de données."),
    _p("8.6", "Durabilité environnementale",
       "La durabilité environnementale est-elle prise en compte dans "
       "l'élaboration ?"),
    _p("8.7.1", "Documentation technique",
       "Une documentation technique est-elle établie et tenue à jour pour "
       "CHAQUE système d'IA ?",
       "L'annexe ZA la rattache à l'article 11(1) : c'est la pièce qu'un "
       "organisme notifié demande en premier, et par système, pas par "
       "entreprise."),
    _p("8.7.2", "Instructions d'utilisation",
       "La notice d'utilisation est-elle produite, et porte-t-elle ce que "
       "le déployeur doit savoir pour tenir ses propres obligations ?"),

    # ── 9. EXPLOITATION ET CONTRÔLE ─────────────────────────────────────
    _p("9.1.1", "Déploiement",
       "Le déploiement est-il maîtrisé, et la version déployée liée à sa "
       "documentation ?"),
    _p("9.1.2", "Exploitation et surveillance",
       "L'exploitation et la surveillance du système en service sont-elles "
       "organisées ?"),
    _p("9.2.1", "Chaîne d'approvisionnement — généralités",
       "La chaîne d'approvisionnement du système d'IA est-elle maîtrisée ?",
       "C'est l'alinéa (l) de l'article 17(1). Un modèle de fondation "
       "acheté sur étagère en fait partie."),
    _p("9.2.2", "Évaluation et sélection",
       "Les fournisseurs et composants sont-ils évalués avant d'être "
       "retenus ?"),
    _p("9.2.3", "Surveillance et ré-évaluation",
       "Sont-ils surveillés et ré-évalués en cours de vie ?",
       "Un fournisseur de modèle change de version sans préavis : la "
       "ré-évaluation est le seul endroit où cela se voit."),
    _p("9.2.4", "Exigences et spécifications",
       "Les exigences imposées aux fournisseurs sont-elles écrites et "
       "contractualisées ?"),
    _p("9.2.5", "Étendue du contrôle",
       "L'étendue du contrôle exercé sur chaque maillon est-elle "
       "déterminée en fonction de ce qu'il porte ?"),
    _p("9.3.1", "Changements — planification",
       "Les changements apportés aux systèmes d'IA sont-ils planifiés ?"),
    _p("9.3.2", "Passage en revue des changements",
       "Chaque changement est-il passé en revue avant d'être appliqué ?"),
    _p("9.3.3", "Changements déclenchant une action",
       "Sait-on quels changements déclenchent une action réglementaire — "
       "nouvelle évaluation, nouvelle documentation, notification ?"),
    _p("9.3.4", "Changements prédéterminés",
       "Les changements prédéterminés sont-ils décrits dans la "
       "documentation technique avant d'être mis en œuvre ?",
       "C'est ce qui sépare une évolution prévue d'une modification "
       "substantielle qui rouvre l'évaluation de conformité."),
    _p("9.4.1", "Surveillance après commercialisation — généralités",
       "Un système de surveillance après commercialisation est-il établi ?",
       "L'alinéa (h) de l'article 17(1), et l'article 72. C'est le "
       "chapitre qu'aucune des deux normes ISO ne couvre."),
    _p("9.4.2", "Domaine d'application de la surveillance",
       "Son périmètre est-il déterminé ?"),
    _p("9.4.3", "Approche de surveillance",
       "L'approche est-elle ACTIVE — collecte organisée, et non attente "
       "de la réclamation ?"),
    _p("9.4.4", "Informations fournies",
       "Les informations collectées sont-elles définies, et effectivement "
       "collectées ?"),
    _p("9.4.5", "Risques nouveaux et émergents",
       "Les risques nouveaux ou émergents détectés en service sont-ils "
       "traités et renvoyés au système de gestion des risques ?"),
    _p("9.4.6", "Interaction avec les déployeurs",
       "Les déployeurs ont-ils un canal, et ce qu'ils remontent "
       "arrive-t-il quelque part ?"),
    _p("9.4.7", "Non-conformités identifiées par la surveillance après "
                "commercialisation",
       "Les non-conformités trouvées par la surveillance rejoignent-elles "
       "le traitement des non-conformités ?"),
    _p("9.5.1", "Signalement d'incidents graves — généralités",
       "Des procédures de signalement des incidents graves sont-elles "
       "documentées, mises en œuvre et tenues à jour ?",
       "L'alinéa (i) de l'article 17(1). Sept exigences dans ce seul "
       "paragraphe — c'est le plus chargé de la norme."),
    _p("9.5.2", "Procédures de signalement",
       "Les procédures disent-elles qui signale, à qui, dans quel délai, "
       "et avec quelles pièces ?"),
    _p("9.6.1", "Non-conformité et action corrective",
       "Les non-conformités sont-elles traitées, et les actions "
       "correctives suivies jusqu'à leur efficacité ?"),
    _p("9.6.2", "Documentation",
       "Le traitement des non-conformités est-il documenté ?"),

    # ── 10. ÉVALUATION DES PERFORMANCES ─────────────────────────────────
    _p("10.1", "Généralités",
       "Ce qu'il faut surveiller et mesurer est-il déterminé, et mesuré ?"),
    _p("10.2.1", "Revue — généralités",
       "Une revue du système de management est-elle conduite à intervalles "
       "planifiés ?"),
    _p("10.2.2", "Éléments d'entrée de la revue de direction",
       "La revue reçoit-elle ce qu'il lui faut pour décider — surveillance, "
       "incidents, non-conformités, changements, retours des déployeurs ?"),
    _p("10.2.3", "Éléments de sortie de la revue",
       "La revue produit-elle des décisions tracées, et pas seulement un "
       "compte rendu ?"),
    _p("10.3", "Amélioration",
       "Le système de management est-il amélioré sur la base de ce que la "
       "revue et la surveillance rendent ?"),
    _p("10.4.1", "Planification des changements — généralités",
       "Les changements du système de management sont-ils planifiés ?"),
    _p("10.4.2", "Changements apportés au domaine d'application",
       "Un changement de périmètre est-il traité comme tel — et ses effets "
       "sur la stratégie de conformité repris ?"),
    _p("10.4.3", "Changements apportés au processus",
       "Un changement de processus est-il revu avant d'être appliqué ?"),
)

PARAGRAPHES_PAR_NUM = {p["num"]: p for p in PARAGRAPHES}
PAR_CHAPITRE = {}
for _p_ in PARAGRAPHES:
    PAR_CHAPITRE.setdefault(_p_["chapitre"], []).append(_p_)


# ═══════════════════════════════════════════════════════════════════════════
#  4. LE PROCESSUS DU §4.4 — LA STRATÉGIE DE CONFORMITÉ RÉGLEMENTAIRE
# ═══════════════════════════════════════════════════════════════════════════
#
# C'EST LA PIÈCE PROPRE À CE RÈGLEMENT, et la seule que ni ISO 9001 ni
# ISO/IEC 42001 ne portent — les deux tables de correspondance de la norme la
# laissent en face du vide. Un fournisseur qui arrive avec un SMQ certifié
# croit tenir le chapitre 4 ; il lui manque exactement ce paragraphe-là.

ELEMENTS_STRATEGIE = (
    {"cle": "smq", "nom": "La conformité du système de management lui-même",
     "dit": "Le SMQ est conforme aux exigences réglementaires, telles que "
            "ce document les décline.",
     "ou": "le présent document"},
    {"cle": "essentielles", "nom": "La conformité aux exigences essentielles",
     "dit": "Les sept exigences du Chapitre III, Section 2 du règlement — "
            "une à une, avec l'approche retenue pour chacune.",
     "ou": "4.4.2 et 4.4.3"},
    {"cle": "surveillance",
     "nom": "La surveillance après commercialisation",
     "dit": "Ce qu'on surveille une fois le système en service, et comment.",
     "ou": "9.4"},
    {"cle": "incidents", "nom": "Les incidents graves",
     "dit": "Qui signale, à qui, dans quel délai, avec quelles pièces.",
     "ou": "9.5"},
    {"cle": "donnees", "nom": "La stratégie de gestion des données",
     "dit": "Ce qu'on fait des jeux de données, de leur gouvernance à leur "
            "conservation.",
     "ou": "8.5"},
)

# ── LES SEPT EXIGENCES ESSENTIELLES ────────────────────────────────────
#
# ELLES SONT CELLES DU CHAPITRE III, SECTION 2 DU RÈGLEMENT, et le §4.4.2 les
# énumère. L'article visé est rappelé parce que c'est lui qui commande : la
# norme n'invente pas ces exigences, elle organise la façon d'y répondre.

EXIGENCES_ESSENTIELLES = (
    {"cle": "risques", "lettre": "a", "nom": "Système de gestion des risques",
     "article": "Article 9", "norme": "prEN 18228"},
    {"cle": "donnees", "lettre": "b",
     "nom": "Données et gouvernance des données",
     "article": "Article 10", "norme": "prEN 18284"},
    {"cle": "documentation", "lettre": "c", "nom": "Documentation technique",
     "article": "Article 11", "norme": None},
    {"cle": "conservation", "lettre": "d", "nom": "Conservation",
     "article": "Article 12", "norme": "prEN 18229-1"},
    {"cle": "transparence", "lettre": "e",
     "nom": "Transparence et fourniture d'informations aux déployeurs",
     "article": "Article 13", "norme": "prEN 18229-1"},
    {"cle": "supervision", "lettre": "f", "nom": "Supervision humaine",
     "article": "Article 14", "norme": "prEN 18229-1"},
    {"cle": "robustesse", "lettre": "g",
     "nom": "Exactitude, robustesse et cybersécurité",
     "article": "Article 15", "norme": "prEN 18229-2 / prEN 18282"},
)

# ── LES QUATRE APPROCHES, ET CE QUE CHACUNE COÛTE EN PREUVE ────────────
#
# C'EST LE CŒUR CALCULABLE DU MODULE. Le §4.4.3.2 ne met pas les quatre
# approches sur le même plan : les deux premières se documentent, les deux
# dernières se documentent ET se justifient ET se prouvent. Un écran qui les
# afficherait comme quatre cases équivalentes ferait croire que le choix est
# libre. Il l'est — mais il n'est pas gratuit.

APPROCHES = (
    {"cle": "harmonisee", "lettre": "a", "nom": "Norme harmonisée",
     "dit": "Une norme européenne harmonisée, citée au Journal officiel au "
            "titre du règlement.",
     "preuve": "documenter",
     "charge": "Documenter l'exigence essentielle satisfaite.",
     "presomption": True},
    {"cle": "specification", "lettre": "b",
     "nom": "Spécification commune",
     "dit": "Une spécification commune adoptée par un acte d'exécution de "
            "la Commission.",
     "preuve": "documenter",
     "charge": "Documenter l'exigence essentielle satisfaite.",
     "presomption": True},
    {"cle": "autre_norme", "lettre": "c", "nom": "Autre norme",
     "dit": "Une norme qui n'est ni harmonisée ni spécification commune — "
            "une norme internationale, sectorielle ou nationale.",
     "preuve": "justifier",
     "charge": "Documenter ce qui n'est PAS entièrement couvert, justifier "
               "les mesures retenues, et produire la preuve objective que "
               "l'exigence est satisfaite.",
     "presomption": False},
    {"cle": "autre_solution", "lettre": "d",
     "nom": "Autre spécification ou solution technique",
     "dit": "Une solution que vous avez construite vous-même, ou que "
            "votre profession recommande.",
     "preuve": "justifier",
     "charge": "Documenter ce qui n'est PAS entièrement couvert, justifier "
               "les mesures retenues, et produire la preuve objective que "
               "l'exigence est satisfaite.",
     "presomption": False},
)

APPROCHES_PAR_CLE = {a["cle"]: a for a in APPROCHES}
#: Les approches qui ouvrent la charge de preuve du 4.4.3.2.2.
APPROCHES_A_JUSTIFIER = tuple(a["cle"] for a in APPROCHES
                              if a["preuve"] == "justifier")


# ═══════════════════════════════════════════════════════════════════════════
#  5. L'ANNEXE ZA — CE QUE LA NORME COUVRE DE L'ARTICLE 17, ET CE QU'ELLE NE
#     COUVRE PAS
# ═══════════════════════════════════════════════════════════════════════════
#
# LA LIGNE « NON COUVERT » EST LA PLUS IMPORTANTE DU TABLEAU, et c'est celle
# qu'on serait tenté de ne pas afficher. L'article 17(2) — les fournisseurs
# soumis à la législation de l'Union sur les services financiers — n'est
# couvert par aucun paragraphe. Un taux de 100 % sur une norme qui déclare
# elle-même une lacune serait un mensonge par arrondi.

def _za(article, paras, dit, remarque=None):
    return {"article": article, "paragraphes": tuple(paras), "dit": dit,
            "remarque": remarque, "couvert": bool(paras)}


ANNEXE_ZA = (
    _za("Article 11(1) — première phrase", ("8.7.1",),
        "La documentation technique, établie avant la mise sur le marché et "
        "tenue à jour."),
    _za("Article 17(1) — première phrase",
        ("4.1", "4.2", "4.3", "4.4", "5.1", "5.3.1", "5.3.2", "5.3.3"),
        "L'obligation même de tenir un système de management de la qualité.",
        "Couvert dans la mesure où les obligations sont couvertes par "
        "l'article 17."),
    _za("Article 17(1)(a)", ("4.4", "9.3.1", "9.3.2", "9.3.3"),
        "La stratégie de respect de la réglementation, y compris pour les "
        "modifications."),
    _za("Article 17(1)(b)", ("8.3.1", "8.3.2"),
        "Les techniques et procédures de conception et de contrôle de la "
        "conception."),
    _za("Article 17(1)(c)", ("8.4",),
        "Les techniques et procédures de développement, de contrôle et "
        "d'assurance qualité."),
    _za("Article 17(1)(d)", ("8.4",),
        "Les procédures d'examen, d'essai et de validation."),
    _za("Article 17(1)(e)", ("4.4",),
        "Les spécifications techniques, dont les normes appliquées — et, "
        "quand elles ne le sont pas entièrement, les moyens employés."),
    _za("Article 17(1)(f)", ("8.5",),
        "Les systèmes et procédures de gestion des données."),
    _za("Article 17(1)(g)", ("8.1",),
        "Le système de gestion des risques de l'article 9.",
        "Sous réserve de l'utilisation d'un système de gestion des risques "
        "conforme à l'article 9."),
    _za("Article 17(1)(h)", ("9.4",),
        "Le système de surveillance après commercialisation."),
    _za("Article 17(1)(i)", ("9.5",),
        "Les procédures de signalement d'un incident grave."),
    _za("Article 17(1)(j)", ("7.3",),
        "La communication avec les autorités, les organismes notifiés, les "
        "autres opérateurs, les clients et les parties intéressées."),
    _za("Article 17(1)(k)", ("4.5", "8.7"),
        "Les systèmes et procédures d'archivage de la documentation et des "
        "informations."),
    _za("Article 17(1)(l)", ("7.1", "9.2"),
        "La gestion des ressources, y compris la sécurité de "
        "l'approvisionnement."),
    _za("Article 17(1)(m)", ("5.3.1", "5.3.2", "5.3.3"),
        "Le cadre de responsabilité de la direction et du personnel."),
    #  LA LACUNE DÉCLARÉE PAR LA NORME ELLE-MÊME.
    _za("Article 17(2)", (),
        "Les fournisseurs soumis à la législation de l'Union sur les "
        "services financiers, dont les obligations de gouvernance interne "
        "valent exécution de l'article 17.",
        "Non couvert."),
    _za("Article 72", ("9.4",),
        "La surveillance après commercialisation par les fournisseurs, et "
        "le plan qui l'accompagne."),
)

#: La seule ligne non couverte — nommée, pour qu'une règle puisse la tenir.
ZA_NON_COUVERTS = tuple(z["article"] for z in ANNEXE_ZA if not z["couvert"])


# ═══════════════════════════════════════════════════════════════════════════
#  6. LES PONTS — CE QU'UN CERTIFICAT EXISTANT DONNE, ET CE QU'IL NE DONNE PAS
# ═══════════════════════════════════════════════════════════════════════════
#
# LES DEUX TABLES DE CORRESPONDANCE DE LA NORME SE LISENT À L'ENVERS, et c'est
# la seule lecture utile. Tout le monde regarde ce qui correspond ; ce qui
# compte, ce sont les DEUX LIGNES EN FACE DU VIDE. Le §4.4 — la stratégie de
# conformité réglementaire — et le chapitre 9 — exploitation et contrôle —
# n'ont d'équivalent ni dans ISO 9001:2015 ni dans ISO/IEC 42001:2023. Ce sont
# exactement les deux que le règlement ajoute.

def _c(ici, la_bas):
    return {"ici": ici, "la_bas": la_bas, "couvert": la_bas is not None}


PONTS = (
    {"cle": "iso9001", "norme": "ISO 9001:2015",
     "nom": "Systèmes de management de la qualité — Exigences",
     "dans_le_site": False,
     "lignes": (
         _c("1 Domaine d'application", "1 Domaine d'application"),
         _c("4.1 à 4.3 Système de management de la qualité",
            "4 Contexte de l'organisme (4.1 à 4.4)"),
         _c("4.4 Stratégie de conformité réglementaire", None),
         _c("4.5 Informations documentées", "7.5 Informations documentées"),
         _c("5 Responsabilité de la direction", "5 Leadership"),
         _c("6 Planification", "6 Planification"),
         _c("7.1 Support — ressources", "7.1 Ressources"),
         _c("7.2 Compétences", "7.2 Compétences"),
         _c("7.3 Communication", "8.2.1 Communication avec les clients"),
         _c("8 Élaboration du produit", "8 Réalisation"),
         _c("9 Exploitation et contrôle", None),
         _c("10 Évaluation des performances", "9 Évaluation des performances"),
         _c("10.3 Amélioration", "10 Amélioration"),
     )},
    {"cle": "iso42001", "norme": "ISO/IEC 42001:2023",
     "nom": "Système de management de l'intelligence artificielle",
     #  CELUI-LÀ EST DÉJÀ DANS LE SITE, et c'est ce qui rend le pont
     #  calculable plutôt que descriptif : le client a déjà répondu.
     "dans_le_site": True,
     "lignes": (
         _c("1 Domaine d'application", "1 Domaine d'application"),
         _c("4.1 à 4.3 Système de management de la qualité",
            "4 Contexte de l'organisme (4.1 à 4.4)"),
         _c("4.4 Stratégie de conformité réglementaire", None),
         _c("4.5 Informations documentées", "7.5 Informations documentées"),
         _c("5 Responsabilité de la direction", "5 Leadership"),
         _c("6 Planification", "6 Planification"),
         _c("7 Support", "7 Soutien"),
         _c("8 Élaboration du produit", "8 Réalisation"),
         _c("9 Exploitation et contrôle", None),
         _c("10 Évaluation des performances", "9 Évaluation des performances"),
         _c("10.3 Amélioration", "10 Amélioration"),
     )},
)

PONTS_PAR_CLE = {p["cle"]: p for p in PONTS}

#: Ce qu'AUCUN des deux certificats ne donne. Calculé, pas recopié : une
#: ligne qui passerait « couverte » dans une table et pas dans l'autre ne
#: devrait plus y figurer.
SANS_EQUIVALENT = tuple(sorted(
    {l["ici"] for p in PONTS for l in p["lignes"] if not l["couvert"]}))


# ── LA FAMILLE DES NORMES HARMONISÉES (ANNEXE B) ───────────────────────
#
# ELLE DIT CE QUE CETTE NORME-CI NE FAIT PAS. prEN 18286 organise la façon de
# répondre aux exigences essentielles ; ce sont les AUTRES qui disent comment
# y répondre. Un fournisseur qui achète « la norme du SMQ » et croit avoir
# traité l'article 10 se trompe de document.

FAMILLE = (
    {"ref": "prEN 18228", "aspect": "Gestion des risques",
     "sujet": "Exigences relatives au système de gestion des risques",
     "articles": "Article 9", "dans_le_site": False},
    {"ref": "prEN 18284", "aspect": "Qualité des données",
     "sujet": "Qualité et gouvernance des jeux de données dans l'IA",
     "articles": "Article 10", "dans_le_site": False},
    {"ref": "prEN 18229-1", "aspect": "Crédibilité — partie 1",
     "sujet": "Cadre pour la crédibilité des systèmes d'IA",
     "articles": "Articles 12 à 14", "dans_le_site": False},
    {"ref": "prEN 18229-2", "aspect": "Crédibilité — partie 2",
     "sujet": "Cadre pour la crédibilité des systèmes d'IA",
     "articles": "Article 15", "dans_le_site": False,
     "note": "Le tableau B.1 intitule cette ligne « Crédibilité Partie 1 », "
             "comme la précédente. La partie est rétablie d'après la "
             "référence et l'article visé."},
    {"ref": "prEN 18282", "aspect": "Cybersécurité",
     "sujet": "Spécifications de cybersécurité pour les systèmes d'IA",
     "articles": "Article 15", "dans_le_site": False},
    {"ref": "prEN 18229-3", "aspect": "Supervision humaine",
     "sujet": "Cadre pour la crédibilité des systèmes d'IA — partie 3",
     "articles": "Article 14", "dans_le_site": True,
     "note": "ABSENTE du tableau B.1, qui range les articles 12 à 14 sous "
             "prEN 18229-1. Elle figure ici parce que ce site la traite "
             "déjà — le rattachement vient du site, pas de l'annexe B."},
)


# ═══════════════════════════════════════════════════════════════════════════
#  7. CE QUE LE CLIENT DÉCLARE
# ═══════════════════════════════════════════════════════════════════════════

ETATS = {
    "tenu": {"nom": "Tenu", "valeur": 1.0,
             "dit": "En place, appliqué, et montrable sur pièce."},
    "partiel": {"nom": "Partiellement tenu", "valeur": 0.5,
                "dit": "Commencé, pas achevé."},
    "absent": {"nom": "Absent", "valeur": 0.0, "dit": "Rien en place."},
    "sans_objet": {"nom": "Sans objet", "valeur": None,
                   "dit": "Le paragraphe ne s'applique pas — et il faut "
                          "pouvoir dire pourquoi."},
}

ORDRE_ETATS = ("absent", "partiel", "tenu", "sans_objet")

# ── LES PARTS DU SCORE, ET POURQUOI CELLES-LÀ ──────────────────────────
#
# LE POIDS SUIT LA CHARGE RÉGLEMENTAIRE, PAS LE NOMBRE DE PARAGRAPHES. Le
# chapitre 4 pèse le plus parce qu'il porte le §4.4, que ni ISO 9001 ni
# ISO/IEC 42001 ne donnent. Le chapitre 9 pèse autant que le 8 parce qu'il
# porte la surveillance après commercialisation et le signalement d'incidents
# graves — les deux obligations dont une autorité se saisit sans attendre un
# audit, et le second chapitre sans équivalent ISO.

PARTS = (
    {"cle": "strategie", "nom": "Stratégie et documentation", "chapitres": ("4",),
     "poids": 3,
     "pourquoi": "Le §4.4 n'a d'équivalent dans aucune des deux normes ISO : "
                 "c'est la pièce propre au règlement, et celle que "
                 "l'organisme notifié ouvre en premier."},
    {"cle": "direction", "nom": "Direction, planification, support",
     "chapitres": ("5", "6", "7"), "poids": 1,
     "pourquoi": "Le socle de management, celui qu'un SMQ déjà certifié "
                 "apporte le plus souvent tel quel."},
    {"cle": "produit", "nom": "Élaboration du produit", "chapitres": ("8",),
     "poids": 2,
     "pourquoi": "De la destination à la documentation technique : ce que "
                 "l'évaluation de conformité examine."},
    {"cle": "exploitation", "nom": "Exploitation et contrôle",
     "chapitres": ("9",), "poids": 2,
     "pourquoi": "Surveillance après commercialisation et incidents graves — "
                 "les deux obligations dont une autorité se saisit sans "
                 "attendre un audit, et le second chapitre sans équivalent "
                 "ISO."},
    {"cle": "performance", "nom": "Évaluation des performances",
     "chapitres": ("10",), "poids": 1,
     "pourquoi": "La revue de direction : elle ne produit rien par "
                 "elle-même, elle décide de ce que le reste produit."},
)

PARTS_PAR_CLE = {p["cle"]: p for p in PARTS}
PART_DU_CHAPITRE = {c: p["cle"] for p in PARTS for c in p["chapitres"]}


# ═══════════════════════════════════════════════════════════════════════════
#  8. LE PROCESSUS, CALCULÉ — §4.4 ET SA CHARGE DE PREUVE
# ═══════════════════════════════════════════════════════════════════════════

ETATS_EXIGENCE = {
    "tenue": {"nom": "Tenue", "dit": "L'approche est choisie et sa charge "
                                     "de preuve est honorée."},
    "a_prouver": {"nom": "À prouver",
                  "dit": "L'approche choisie ouvre la charge du 4.4.3.2.2, "
                         "et il manque au moins une des trois pièces."},
    "sans_approche": {"nom": "Sans approche",
                      "dit": "Aucune approche n'est retenue pour cette "
                             "exigence essentielle."},
    "sans_objet": {"nom": "Sans objet",
                   "dit": "L'exigence ne s'applique pas à ce système — et "
                          "il faut pouvoir dire pourquoi."},
}

#: Les trois pièces que le 4.4.3.2.2 réclame quand l'approche est « autre ».
PIECES_A_JUSTIFIER = (
    {"cle": "couverture_ecrite",
     "nom": "Ce qui n'est PAS entièrement couvert, écrit"},
    {"cle": "justification", "nom": "La justification des mesures retenues"},
    {"cle": "preuve_objective",
     "nom": "La preuve objective que l'exigence est satisfaite"},
)


def strategie(declaration=None):
    """Le §4.4, exigence essentielle par exigence essentielle.

    CE QUE CETTE FONCTION REFUSE DE FAIRE : traiter les quatre approches
    comme quatre cases équivalentes. Le choix est libre, il n'est pas
    gratuit — et c'est la norme elle-même qui le dit au 4.4.3.2.2.
    """
    d = declaration if isinstance(declaration, dict) else {}
    s = d.get("strategie") if isinstance(d.get("strategie"), dict) else {}
    elements = s.get("elements") if isinstance(s.get("elements"), dict) else {}
    saisies = s.get("exigences") if isinstance(s.get("exigences"), dict) else {}

    lignes = []
    for ex in EXIGENCES_ESSENTIELLES:
        v = saisies.get(ex["cle"]) if isinstance(saisies.get(ex["cle"]), dict) \
            else {}
        if v.get("sans_objet"):
            lignes.append(dict(ex, etat="sans_objet", approche=None,
                               manque=(), charge=None))
            continue
        a = APPROCHES_PAR_CLE.get(v.get("approche"))
        if not a:
            lignes.append(dict(ex, etat="sans_approche", approche=None,
                               manque=(), charge=None))
            continue
        manque = ()
        if a["cle"] in APPROCHES_A_JUSTIFIER:
            manque = tuple(p["cle"] for p in PIECES_A_JUSTIFIER
                           if not v.get(p["cle"]))
        lignes.append(dict(ex, etat=("a_prouver" if manque else "tenue"),
                           approche=a["cle"], approche_nom=a["nom"],
                           presomption=a["presomption"],
                           charge=a["charge"], manque=manque))

    portees = [l for l in lignes if l["etat"] != "sans_objet"]
    trous = [l for l in lignes if l["etat"] == "a_prouver"]
    muettes = [l for l in lignes if l["etat"] == "sans_approche"]
    composantes = [dict(e, declaree=bool(elements.get(e["cle"])))
                   for e in ELEMENTS_STRATEGIE]
    manquantes = [c for c in composantes if not c["declaree"]]

    return {
        "lignes": lignes,
        "composantes": composantes,
        "composantes_manquantes": [c["cle"] for c in manquantes],
        "portees": len(portees),
        "tenues": len([l for l in lignes if l["etat"] == "tenue"]),
        "a_prouver": [l["cle"] for l in trous],
        "sans_approche": [l["cle"] for l in muettes],
        "sans_objet": [l["cle"] for l in lignes if l["etat"] == "sans_objet"],
        #  LA STRATÉGIE EST COMPLÈTE quand ses cinq composantes sont
        #  déclarées ET que chaque exigence portée a son approche honorée.
        "complete": not manquantes and not trous and not muettes,
        "taux": (None if not portees
                 else int(round(100.0 * len([l for l in lignes
                                             if l["etat"] == "tenue"])
                                / len(portees)))),
    }


# ═══════════════════════════════════════════════════════════════════════════
#  9. LE SCORE — ET LE PLAFOND QUE LA NORME S'IMPOSE À ELLE-MÊME
# ═══════════════════════════════════════════════════════════════════════════

#: Ce qu'une stratégie dont la charge de preuve n'est pas honorée laisse
#: revendiquer de la part « stratégie ». LA MOITIÉ, et pas zéro : le travail
#: de documentation est réel, c'est la DÉMONSTRATION qui manque.
PLAFOND_STRATEGIE_SANS_PREUVE = 0.5


def _valeur(etat):
    e = ETATS.get(etat)
    return e["valeur"] if e else None


def score(declaration=None):
    """Le score par part, le brut, le plafond, et le taux qui en sort.

    TROIS NOMBRES, ET LES TROIS SONT NÉCESSAIRES — c'est la doctrine du
    reste du site : `brut` dit ce que vaut le travail fait, `plafond` ce que
    la charge de preuve laisse revendiquer, `taux` le plus petit des deux.
    """
    d = declaration if isinstance(declaration, dict) else {}
    rep = d.get("reponses") if isinstance(d.get("reponses"), dict) else {}

    parts, poids_total, acquis_total = [], 0, 0.0
    for part in PARTS:
        paras = [p for p in PARAGRAPHES if p["chapitre"] in part["chapitres"]]
        retenus, acquis = 0, 0.0
        sans_reponse = []
        for p in paras:
            v = _valeur(rep.get(p["num"]))
            if rep.get(p["num"]) == "sans_objet":
                continue
            if v is None:
                sans_reponse.append(p["num"])
            #  UN PARAGRAPHE SANS RÉPONSE COMPTE POUR ZÉRO, ET PAS POUR
            #  RIEN. Le sortir du dénominateur ferait monter le taux à
            #  mesure qu'on répond MOINS : le pire réglage possible.
            retenus += 1
            acquis += v or 0.0
        t = (None if not retenus else int(round(100.0 * acquis / retenus)))
        parts.append(dict(part, paragraphes=len(paras), portes=retenus,
                          sans_reponse=len(sans_reponse), taux=t))
        poids_total += part["poids"]
        acquis_total += part["poids"] * (0.0 if t is None else t / 100.0)

    brut = int(round(100.0 * acquis_total / poids_total)) if poids_total else 0

    # ── LE VERROU, ET IL NE VIENT PAS D'UNE CASE ────────────────────────
    #
    # IL SE CALCULE SUR LA STRATÉGIE. Une exigence essentielle traitée par
    # « autre norme » ou « autre solution » sans sa justification et sa
    # preuve objective n'est pas à moitié tenue : c'est une exigence que
    # l'organisme notifié rouvrira, et le §4.4 ne peut pas s'en prévaloir.
    st = strategie(d)
    verrous = []
    cap = 1.0
    if st["a_prouver"]:
        cap = PLAFOND_STRATEGIE_SANS_PREUVE
        verrous.append({
            "cle": "charge_de_preuve",
            "dit": "%d exigence(s) essentielle(s) traitée(s) par « autre "
                   "norme » ou « autre solution technique » sans la "
                   "justification et la preuve objective que le 4.4.3.2.2 "
                   "réclame." % len(st["a_prouver"]),
            "porte_sur": "La part « stratégie » ne peut pas être revendiquée "
                         "au-delà de la moitié : le travail de documentation "
                         "est réel, c'est la DÉMONSTRATION qui manque.",
            "exigences": list(st["a_prouver"]),
            "ou": "en18286 · processus"})

    poids_strat = PARTS_PAR_CLE["strategie"]["poids"]
    plafond = int(round(100.0 * ((poids_total - poids_strat)
                                 + poids_strat * cap) / poids_total)) \
        if poids_total else 0

    #  LES PARTS PLAFONNÉES SONT CELLES QUE LE TAUX DE CONFORMITÉ LIRA, et
    #  c'est le point : ce module décide l'arithmétique une fois. Si
    #  `conformite` recomposait son taux sur les parts BRUTES, il
    #  afficherait 100 % là où ce module affiche 83 % — deux vérités sur le
    #  même nombre, et le client entre les deux. Mesuré avant cette
    #  correction, exactement comme l'audit IA Act l'avait été avant elles.
    parts_plafonnees = []
    for part in parts:
        t = part["taux"]
        if part["cle"] == "strategie" and t is not None:
            t = min(t, int(round(100 * cap)))
        parts_plafonnees.append(dict(part, taux=t))
    return {"brut": brut, "plafond": plafond, "taux": min(brut, plafond),
            "parts": parts, "parts_plafonnees": parts_plafonnees,
            "verrous": verrous, "plafonne": min(brut, plafond) < brut}


# ═══════════════════════════════════════════════════════════════════════════
#  10. LA COUVERTURE DE L'ARTICLE 17, LIGNE PAR LIGNE
# ═══════════════════════════════════════════════════════════════════════════

def _resout(reference):
    """Les paragraphes du module que vise une référence de l'annexe ZA.

    LA RÉSOLUTION VA DANS LES DEUX SENS, et il le faut : l'annexe ZA vise
    tantôt plus large que la table (« 4.4 » pour 4.4.1, 4.4.2, 4.4.3.1 et
    4.4.3.2), tantôt plus fin (« 5.3.1 » quand la table porte « 5.3 »).
    Une résolution à sens unique laisserait des lignes de l'annexe sans
    rien en face, et l'écran dirait « non couvert » là où la norme couvre.
    """
    return [p for p in PARAGRAPHES
            if p["num"] == reference
            or p["num"].startswith(reference + ".")
            or reference.startswith(p["num"] + ".")]


def couverture_za(declaration=None):
    """L'article 17 tel que la déclaration le rend — et la ligne que la
    norme déclare elle-même non couverte."""
    d = declaration if isinstance(declaration, dict) else {}
    rep = d.get("reponses") if isinstance(d.get("reponses"), dict) else {}
    lignes = []
    for z in ANNEXE_ZA:
        vises = []
        for r in z["paragraphes"]:
            for p in _resout(r):
                if p["num"] not in [v["num"] for v in vises]:
                    vises.append(p)
        valeurs = [(_valeur(rep.get(p["num"])), rep.get(p["num"]))
                   for p in vises]
        portes = [v for v, e in valeurs if e != "sans_objet"]
        acquis = sum(v or 0.0 for v in portes)
        lignes.append({
            "article": z["article"], "dit": z["dit"],
            "remarque": z["remarque"],
            "couvert_par_la_norme": z["couvert"],
            "paragraphes": list(z["paragraphes"]),
            "vises": [p["num"] for p in vises],
            "taux": (None if not z["couvert"] or not portes
                     else int(round(100.0 * acquis / len(portes)))),
            "sans_reponse": len([v for v in portes if v is None]),
        })
    return lignes


def ponts_calcules(declaration=None):
    """Ce qu'un certificat déjà tenu apporte — et les deux paragraphes qu'il
    n'apporte pas."""
    d = declaration if isinstance(declaration, dict) else {}
    tenus = d.get("certifie") if isinstance(d.get("certifie"), dict) else {}
    out = []
    for p in PONTS:
        couvertes = [l for l in p["lignes"] if l["couvert"]]
        out.append(dict(p, tenu=bool(tenus.get(p["cle"])),
                        correspondances=len(couvertes),
                        total=len(p["lignes"]),
                        sans_equivalent=[l["ici"] for l in p["lignes"]
                                         if not l["couvert"]]))
    return out


# ═══════════════════════════════════════════════════════════════════════════
#  11. LA QUALIFICATION — ELLE COMMANDE TOUT LE RESTE
# ═══════════════════════════════════════════════════════════════════════════
#
# L'ARTICLE 17 S'ADRESSE AU FOURNISSEUR D'UN SYSTÈME D'IA À HAUT RISQUE, et à
# lui seul. Noter un déployeur sur un système de management de la qualité
# qu'il n'a pas à tenir produirait un taux accablant et faux. On le déclare
# hors champ, et on dit pourquoi — comme NIS 2 le fait déjà pour une entité
# que son secteur et sa taille placent dehors.

HORS_CHAMP = {
    "cle": "hors_champ",
    "dit": "Cette norme vise le FOURNISSEUR d'un système d'IA à haut risque "
           "— celui qui le met sur le marché ou en service sous son nom. "
           "Hors de cette qualification, l'article 17 ne s'applique pas, et "
           "ce module ne rend aucun taux.",
    "porte_sur": "Ce n'est pas une dispense : la qualification se revoit. Un "
                 "déployeur qui modifie substantiellement un système, ou qui "
                 "y appose son nom, DEVIENT fournisseur au sens du "
                 "règlement.",
}

RESERVES = (
    {"cle": "presomption", "dit": RESERVE_PRESOMPTION,
     "ou": "en18286 · conformité",
     "porte_sur": "Le taux dit ce que le système de management déclaré "
                  "couvre du tableau ZA.1. Il ne dit pas qu'un organisme "
                  "notifié l'a vu, ni que la norme est citée au JOUE.",
     "toujours": True},
    {"cle": "article_17_2",
     "dit": "Votre régime relève de l'article 17(2) : les obligations de "
            "gouvernance interne de la législation de l'Union sur les "
            "services financiers valent exécution de l'article 17.",
     "ou": "en18286 · conformité",
     "porte_sur": "L'annexe ZA de cette norme déclare l'article 17(2) NON "
                  "COUVERT. Le travail fait ici reste utile — il ne se "
                  "substitue pas à ce que votre autorité de tutelle "
                  "attend, et il n'en découle aucune présomption.",
     "toujours": False},
    {"cle": "za_incomplete",
     "dit": "L'annexe ZA porte une ligne sans aucun paragraphe en face.",
     "ou": "en18286 · conformité",
     "porte_sur": "Cent pour cent sur cette norme ne veut pas dire "
                  "article 17 tenu : la norme elle-même déclare une lacune.",
     "toujours": True},
)

RESERVES_PAR_CLE = {r["cle"]: r for r in RESERVES}


def applicable(declaration=None):
    """La norme s'applique-t-elle, et pourquoi.

    IL FAUT LES DEUX RÉPONSES, PAS UNE. Mesuré : avec « et » au lieu de
    « ou » ci-dessous, un fournisseur qui venait de se déclarer tel — et qui
    n'avait pas encore dit si son système est à haut risque — était renvoyé
    HORS CHAMP, et ses quatre écrans passaient en « sans objet ». Le silence
    sur UNE des deux questions ne se range pas du côté du « non » : il se dit
    « pas encore qualifié », et l'écran reste à remplir.
    """
    d = declaration if isinstance(declaration, dict) else {}
    q = d.get("qualification") if isinstance(d.get("qualification"), dict) \
        else {}
    if q.get("fournisseur") is None or q.get("haut_risque") is None:
        return {"ok": None, "motif": "non_qualifie",
                "dit": "La qualification n'est pas faite : on ne sait pas "
                       "si l'article 17 vous vise."}
    if not q.get("fournisseur") or not q.get("haut_risque"):
        return {"ok": False, "motif": "hors_champ", "dit": HORS_CHAMP["dit"]}
    return {"ok": True, "motif": "fournisseur_haut_risque",
            "dit": "Vous mettez sur le marché un système d'IA à haut risque "
                   "sous votre nom : l'article 17 vous impose un système de "
                   "management de la qualité."}


# ═══════════════════════════════════════════════════════════════════════════
#  12. LE PLAN — DÉRIVÉ, ET ORDONNÉ POUR UNE RAISON QUI SE DIT
# ═══════════════════════════════════════════════════════════════════════════

def plan(declaration=None, limite=None):
    """Par quoi commencer.

    L'ORDRE N'EST PAS CELUI DU DOCUMENT, ET C'EST VOULU. Ce qui PLAFONNE
    passe devant : tant que la charge de preuve du 4.4.3.2.2 n'est pas
    honorée, le reste bute sur le même plafond. Puis les composantes
    manquantes de la stratégie, puis les paragraphes — par poids de part,
    parce que refermer un écart du chapitre 4 rapporte trois fois ce que
    rapporte le même écart au chapitre 10.
    """
    d = declaration if isinstance(declaration, dict) else {}
    rep = d.get("reponses") if isinstance(d.get("reponses"), dict) else {}
    st = strategie(d)
    out = []

    for ligne in st["lignes"]:
        if ligne["etat"] != "a_prouver":
            continue
        out.append({
            "rang_famille": 0, "cle": "preuve:" + ligne["cle"],
            "quoi": "Exigence essentielle « %s » : l'approche « %s » ouvre "
                    "la charge du 4.4.3.2.2." % (ligne["nom"],
                                                 ligne["approche_nom"]),
            "manque": [p["nom"] for p in PIECES_A_JUSTIFIER
                       if p["cle"] in ligne["manque"]],
            "ou": "en18286 · processus", "article": ligne["article"]})

    for c in st["composantes"]:
        if c["declaree"]:
            continue
        out.append({"rang_famille": 1, "cle": "strategie:" + c["cle"],
                    "quoi": "Stratégie de conformité : « %s » n'est pas "
                            "déclarée." % c["nom"],
                    "manque": [], "ou": "en18286 · processus",
                    "article": c["ou"]})

    poids = {p["cle"]: p["poids"] for p in PARTS}
    manquants = []
    for p in PARAGRAPHES:
        e = rep.get(p["num"])
        if e in ("tenu", "sans_objet"):
            continue
        part = PART_DU_CHAPITRE[p["chapitre"]]
        manquants.append((-poids[part], _ordre_num(p["num"]), p, part, e))
    manquants.sort(key=lambda x: (x[0], x[1]))
    for _, _, p, part, e in manquants:
        out.append({"rang_famille": 2, "cle": p["num"],
                    "quoi": "%s %s" % (p["num"], p["titre"]),
                    "manque": [], "ou": "en18286 · questionnaire",
                    "article": p["num"], "part": part,
                    "deja_vu": e == "partiel"})

    for i, e in enumerate(out, 1):
        e["rang"] = i
    return out[:limite] if limite else out


def _ordre_num(num):
    """« 10.2 » vient après « 9.6 », et « 4.5.4 » après « 4.5.1 ». Un tri de
    chaînes rendrait l'inverse sur les deux."""
    return tuple(int(x) for x in num.split("."))


# ═══════════════════════════════════════════════════════════════════════════
#  13. L'ÉVALUATION — CE QUE L'ÉCRAN ET LE TAUX DE CONFORMITÉ LISENT
# ═══════════════════════════════════════════════════════════════════════════

def evaluer(declaration=None, aujourdhui=None):
    d = declaration if isinstance(declaration, dict) else {}
    rep = d.get("reponses") if isinstance(d.get("reponses"), dict) else {}
    inconnus = sorted(k for k in rep if k not in PARAGRAPHES_PAR_NUM)
    if inconnus:
        return {"ok": False, "motif": "paragraphes_inconnus",
                "detail": inconnus[:8]}
    mauvais = sorted(k for k, v in rep.items() if v not in ETATS)
    if mauvais:
        return {"ok": False, "motif": "etats_inconnus", "detail": mauvais[:8]}

    champ = applicable(d)
    st = strategie(d)
    sc = score(d)
    za = couverture_za(d)
    q = d.get("qualification") if isinstance(d.get("qualification"), dict) \
        else {}

    signaux = ["presomption", "za_incomplete"]
    if q.get("services_financiers"):
        signaux.append("article_17_2")
    reserves = [dict(RESERVES_PAR_CLE[c]) for c in signaux]

    renseignes = len([k for k in rep if rep[k] in ETATS])
    if champ["ok"] is False:
        tete, dit = "hors_champ", HORS_CHAMP["dit"]
    elif champ["ok"] is None:
        tete, dit = "non_qualifie", champ["dit"]
    elif not renseignes:
        tete, dit = "vide", (
            "Rien n'est renseigné. Le module ne rend aucun chiffre par "
            "défaut : un questionnaire vide n'est pas un système de "
            "management à zéro.")
    elif sc["verrous"]:
        tete, dit = "charge_de_preuve", (
            "%d %% du travail est déclaré ; la charge de preuve du 4.4.3.2.2 "
            "interdit d'aller au-delà de %d %%. Ce n'est pas le travail qui "
            "manque, c'est la démonstration."
            % (sc["brut"], sc["plafond"]))
    elif not st["complete"]:
        tete, dit = "strategie_incomplete", (
            "La stratégie de conformité réglementaire du §4.4 n'est pas "
            "complète. C'est la pièce que ni ISO 9001 ni ISO/IEC 42001 ne "
            "donnent, et celle que l'organisme notifié ouvre en premier.")
    else:
        tete, dit = "coherent", (
            "La stratégie est complète et sa charge de preuve honorée. "
            "Reste ce que le questionnaire laisse ouvert — et la réserve de "
            "présomption, qui ne se lève pas par le travail.")

    return {
        "ok": True,
        "aujourdhui": (aujourdhui or datetime.date.today().isoformat()),
        "applicable": champ,
        #  LE TAUX DE CONFORMITÉ LIT CELLES-CI, DÉJÀ PLAFONNÉES.
        "parts": {p["cle"]: p["taux"] for p in sc["parts_plafonnees"]},
        "parts_brutes": {p["cle"]: p["taux"] for p in sc["parts"]},
        "score": sc,
        "strategie": st,
        "annexe_za": za,
        "za_non_couverts": list(ZA_NON_COUVERTS),
        "ponts": ponts_calcules(d),
        "sans_equivalent": list(SANS_EQUIVALENT),
        "paragraphes": len(PARAGRAPHES),
        "renseignes": renseignes,
        "reserves": reserves,
        "tete": tete, "dit": dit,
        "presomption": False,
        "reserve": RESERVE_PRESOMPTION,
    }


def referentiel():
    """La table, telle que l'écran la demande — sans jamais la recopier."""
    return {
        "source": dict(SOURCE),
        "reserve": RESERVE_PRESOMPTION,
        "contradictions": [dict(c) for c in CONTRADICTIONS],
        "chapitres": [dict(c) for c in CHAPITRES],
        "paragraphes": [dict(p) for p in PARAGRAPHES],
        "parts": [dict(p, chapitres=list(p["chapitres"])) for p in PARTS],
        "etats": ETATS, "ordre_etats": list(ORDRE_ETATS),
        "elements_strategie": [dict(e) for e in ELEMENTS_STRATEGIE],
        "exigences_essentielles": [dict(e) for e in EXIGENCES_ESSENTIELLES],
        "approches": [dict(a) for a in APPROCHES],
        "pieces_a_justifier": [dict(p) for p in PIECES_A_JUSTIFIER],
        "etats_exigence": ETATS_EXIGENCE,
        "annexe_za": [dict(z, paragraphes=list(z["paragraphes"]))
                      for z in ANNEXE_ZA],
        "za_non_couverts": list(ZA_NON_COUVERTS),
        "ponts": [dict(p, lignes=[dict(l) for l in p["lignes"]])
                  for p in PONTS],
        "sans_equivalent": list(SANS_EQUIVALENT),
        "famille": [dict(f) for f in FAMILLE],
        "hors_champ": dict(HORS_CHAMP),
        "presomption": False,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  14. LA GARDE — ELLE REJOUE L'ARITHMÉTIQUE, ELLE NE LA RELIT PAS
# ═══════════════════════════════════════════════════════════════════════════

def _verifier():
    fautes = []

    # ── LA TABLE SE RECOMPTE ────────────────────────────────────────────
    if len(PARAGRAPHES_PAR_NUM) != len(PARAGRAPHES):
        fautes.append("deux paragraphes portent le même numéro")
    for p in PARAGRAPHES:
        if p["chapitre"] not in CHAPITRES_PAR_NUM:
            fautes.append("%s : le chapitre %s n'est pas déclaré"
                          % (p["num"], p["chapitre"]))
        if p["chapitre"] not in PART_DU_CHAPITRE:
            fautes.append("%s : son chapitre n'appartient à aucune part du "
                          "score" % p["num"])
        if not p["titre"] or not p["demande"]:
            fautes.append("%s : titre ou question manquant" % p["num"])
    for c in CHAPITRES:
        if not PAR_CHAPITRE.get(c["num"]):
            fautes.append("le chapitre %s ne porte aucun paragraphe"
                          % c["num"])
        if c["part"] not in PARTS_PAR_CLE:
            fautes.append("le chapitre %s renvoie à une part inconnue (%s)"
                          % (c["num"], c["part"]))

    # ── L'ANNEXE ZA SE RÉSOUT, OU LE MODULE NE DÉMARRE PAS ──────────────
    #
    # UNE RÉFÉRENCE ZA SANS PARAGRAPHE EN FACE ferait afficher « non
    # couvert » là où la norme couvre. C'est le défaut qui coûte le plus
    # cher à l'écran de conformité, et il ne se voit pas à la lecture.
    for z in ANNEXE_ZA:
        if not z["couvert"]:
            continue
        for r in z["paragraphes"]:
            if not _resout(r):
                fautes.append("annexe ZA, %s : la référence %s ne vise aucun "
                              "paragraphe de la table" % (z["article"], r))
    if len(ZA_NON_COUVERTS) != 1 or ZA_NON_COUVERTS[0] != "Article 17(2)":
        fautes.append("la ligne non couverte de l'annexe ZA n'est plus "
                      "l'article 17(2) : %s" % list(ZA_NON_COUVERTS))

    # ── LE PROCESSUS DU §4.4 ────────────────────────────────────────────
    if len(EXIGENCES_ESSENTIELLES) != 7:
        fautes.append("les exigences essentielles ne sont plus sept : %d"
                      % len(EXIGENCES_ESSENTIELLES))
    if len(ELEMENTS_STRATEGIE) != 5:
        fautes.append("la stratégie du 4.4.1 ne porte plus cinq composantes")
    if len(APPROCHES) != 4:
        fautes.append("les approches du 4.4.3.1 ne sont plus quatre")
    if len(APPROCHES_A_JUSTIFIER) != 2:
        fautes.append("la charge de preuve du 4.4.3.2.2 ne pèse plus sur "
                      "DEUX approches : %s" % list(APPROCHES_A_JUSTIFIER))
    for a in APPROCHES:
        if a["presomption"] and a["preuve"] != "documenter":
            fautes.append("l'approche %s ouvre une présomption ET une charge "
                          "de preuve : les deux ne vont pas ensemble"
                          % a["cle"])
    if len(PIECES_A_JUSTIFIER) != 3:
        fautes.append("le 4.4.3.2.2 ne réclame plus trois pièces")

    # ── LA LICENCE ET LA PRÉSOMPTION ────────────────────────────────────
    if SOURCE.get("presomption") is not False:
        fautes.append("la source annonce une présomption de conformité que "
                      "la citation au Journal officiel n'a pas ouverte")
    if "Journal officiel" not in RESERVE_PRESOMPTION:
        fautes.append("la réserve ne dit plus d'où viendrait la présomption "
                      "— le Journal officiel")
    if "DROIT D'AUTEUR" not in SOURCE.get("licence", ""):
        fautes.append("la licence ne nomme plus le droit d'auteur : c'est "
                      "elle qui dit pourquoi aucune phrase normative n'est "
                      "recopiée")

    # ── LES PONTS : CE QU'ILS NE DONNENT PAS EST LE POINT ───────────────
    if not SANS_EQUIVALENT:
        fautes.append("les deux tables de correspondance ne laissent plus "
                      "rien sans équivalent : le pont ne dirait plus ce "
                      "qu'un certificat ISO ne donne PAS")
    for attendu in ("4.4", "9 "):
        if not any(s.startswith(attendu) for s in SANS_EQUIVALENT):
            fautes.append("le paragraphe « %s » a disparu des lignes sans "
                          "équivalent ISO" % attendu.strip())

    # ── L'ARITHMÉTIQUE SE REJOUE, SUR QUATRE CAS ÉCRITS ICI ─────────────
    #
    # SANS CETTE PARTIE, LA GARDE NE GARDERAIT QUE DES NOMBRES. C'est le
    # plafond de la charge de preuve qui change le taux affiché au client :
    # il doit tomber quand il doit tomber, et se lever quand les trois
    # pièces arrivent.
    q = {"fournisseur": True, "haut_risque": True}
    tout = {p["num"]: "tenu" for p in PARAGRAPHES}
    elements = {e["cle"]: True for e in ELEMENTS_STRATEGIE}

    def _d(approche, pieces=False):
        ex = {}
        for e in EXIGENCES_ESSENTIELLES:
            v = {"approche": approche}
            if pieces:
                v.update({p["cle"]: True for p in PIECES_A_JUSTIFIER})
            ex[e["cle"]] = v
        return {"qualification": q, "reponses": tout,
                "strategie": {"elements": elements, "exigences": ex}}

    plein = score(_d("harmonisee"))
    if plein["taux"] != 100 or plein["verrous"]:
        fautes.append("tout tenu par normes harmonisées ne rend pas 100 %% : "
                      "%r" % plein["taux"])
    sans = score(_d("autre_solution"))
    if not sans["verrous"]:
        fautes.append("une approche « autre solution » sans preuve ne "
                      "déclenche aucun verrou")
    if sans["taux"] >= plein["taux"] or sans["taux"] != sans["plafond"]:
        fautes.append("le plafond de la charge de preuve ne tient pas : "
                      "brut %s, plafond %s, taux %s"
                      % (sans["brut"], sans["plafond"], sans["taux"]))
    leve = score(_d("autre_solution", pieces=True))
    if leve["taux"] != 100 or leve["verrous"]:
        fautes.append("les trois pièces du 4.4.3.2.2 ne LÈVENT pas le "
                      "plafond : %r" % leve["taux"])
    #  LES DEUX CHEMINS DOIVENT S'ACCORDER : le taux du module et celui
    #  qu'on recompose sur les parts plafonnées, pondérées comme ici.
    poids = {x["cle"]: x["poids"] for x in PARTS}
    total = sum(poids.values())
    for cas in (_d("harmonisee"), _d("autre_solution"),
                _d("autre_solution", pieces=True)):
        sc = score(cas)
        recompose = int(round(sum(
            poids[x["cle"]] * (x["taux"] or 0) for x in sc["parts_plafonnees"])
            / float(total)))
        if abs(recompose - sc["taux"]) > 1:
            fautes.append("le taux du module (%s) et celui qu'on recompose "
                          "sur ses parts plafonnées (%s) divergent"
                          % (sc["taux"], recompose))
    vide = score({"qualification": q})
    if vide["taux"] != 0:
        fautes.append("un questionnaire vide ne rend pas 0 %% : %r"
                      % vide["taux"])

    # ── LE PLAN FAIT PASSER DEVANT CE QUI PLAFONNE ──────────────────────
    p_sans = plan(_d("autre_solution"))
    if not p_sans or p_sans[0]["rang_famille"] != 0:
        fautes.append("le plan ne met pas en tête ce qui PLAFONNE le score")
    if _ordre_num("10.1") <= _ordre_num("9.6"):
        fautes.append("le tri des numéros range 10.1 avant 9.6 : c'est un "
                      "tri de chaînes, pas de paragraphes")

    # ── LE HORS-CHAMP ───────────────────────────────────────────────────
    if applicable({"qualification": {"fournisseur": False,
                                     "haut_risque": True}}).get("ok") is not False:
        fautes.append("un non-fournisseur n'est pas déclaré hors champ")
    if applicable({}).get("ok") is not None:
        fautes.append("une qualification absente est confondue avec une "
                      "réponse")
    #  ET LE SILENCE SUR UNE SEULE DES DEUX QUESTIONS, qui est le cas que la
    #  garde laissait passer. MESURÉ : un fournisseur déclaré, la question du
    #  haut risque encore ouverte, et le module le renvoyait HORS CHAMP — ses
    #  quatre écrans passaient « sans objet » sans qu'il ait rien dit.
    for moitie in ({"fournisseur": True}, {"haut_risque": True}):
        if applicable({"qualification": moitie}).get("ok") is not None:
            fautes.append("une qualification À MOITIÉ faite (%s) est "
                          "confondue avec une réponse : le silence sur "
                          "l'autre question ne vaut pas « non »"
                          % ", ".join(sorted(moitie)))

    if fautes:
        raise RuntimeError(
            "en18286 : la table de prEN 18286 est incohérente — "
            + " ; ".join(fautes[:8]))
    return fautes


_FAUTES = _verifier()
