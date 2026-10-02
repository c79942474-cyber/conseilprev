# -*- coding: utf-8 -*-
"""OCDE — Guide sur le devoir de diligence pour une IA responsable (2026).

CE QUE CE DOCUMENT EST. C'est le guide de mise en œuvre que l'OCDE a écrit
pour deux de ses instruments à la fois : les Principes de l'OCDE sur l'IA
(Recommandation révisée en mai 2024) et le Guide OCDE à l'intention des
entreprises multinationales sur la conduite responsable des entreprises
(révisé en 2023). Il est bâti sur le Guide OCDE sur le devoir de diligence
pour une conduite responsable des entreprises (2018), et il reprend sa
charpente : six étapes. Approuvé et déclassifié par le Comité de la politique
de l'économie numérique et le Comité de l'investissement le 26 janvier 2026 ;
version révisée de mai 2026.

═══ IL EST VOLONTAIRE, ET ÇA NE CHANGERA PAS ════════════════════════════
Aucune certification, aucun organisme notifié, aucune présomption de
conformité — et, contrairement à prEN 18286, ce n'est pas une question de
calendrier. prEN 18286 n'ouvre pas encore de présomption mais en ouvrira le
jour de sa citation au Journal officiel. Celui-ci, jamais : un guide de mise
en œuvre de deux recommandations n'est pas une norme harmonisée. La parenté
la plus proche dans Sentinel est le cadre du NIST, pas NIS 2.

═══ LA LICENCE CHANGE LA FORME DU MODULE ════════════════════════════════
CC BY 4.0 — une première dans ce dépôt. Les textes du CEN et de l'ISO sont
protégés : les modules prEN 18229-3, prEN 18286, ISO/IEC 42001 et ISO/IEC
27001 n'en citent que les numéros et les intitulés. Ici, la reproduction, la
traduction et l'adaptation sont permises, sous trois conditions que la
licence formule elle-même et que ce module honore :

  · citer l'œuvre            → SOURCE["citation"], affichée sur les quatre
                               écrans ;
  · pour une TRADUCTION      → identifier les modifications et porter
                               MENTION_TRADUCTION ;
  · pour une ADAPTATION      → porter MENTION_ADAPTATION.

Les deux mentions sont dues, et pour deux raisons différentes : les intitulés
des étapes sont TRADUITS, et le découpage du questionnaire est une
ADAPTATION du cadre. Le module les porte toutes les deux, mot pour mot.

DEUX LIMITES, ET ELLES TOMBENT SUR LE CONTENU LE PLUS UTILE :
  · LE MATÉRIEL DE TIERS EST EXCLU de la licence. Les six feuilles de route
    citent les clauses d'ISO/IEC 42001, 23894, 38507, 42005, d'ISO 31000, de
    l'IEEE 7000 et d'AI Verify. Ces lignes-là restent sous leur licence
    d'origine : le module les rend comme il rend déjà l'ISO — NUMÉRO ET
    INTITULÉ, rien d'autre.
  · LE LOGO, L'IDENTITÉ VISUELLE ET L'IMAGE DE COUVERTURE DE L'OCDE SONT
    INTERDITS, et il est interdit de suggérer que l'OCDE adosse cet usage.
    Conséquence concrète et non décorative : la couleur du tiroir dans la
    barre latérale de Sentinel n'est pas le bleu de l'OCDE.

═══ POURQUOI LES EXEMPLES PRATIQUES RESTENT EN ANGLAIS ══════════════════
La licence permettrait de les traduire. Ils ne le sont pas, pour la même
raison que les 212 actions du profil IA générative du NIST : c'est le libellé
qu'un auditeur cherchera, et une traduction obligerait à porter la mention
d'adaptation sur chacune des 115 lignes. Le module écrit le FRANÇAIS du
cabinet autour d'elles — ce que chaque sous-étape demande, et ce qu'elle
engage — et laisse l'énoncé de l'OCDE intact.

═══ CE QUE CE MODULE CALCULE, ET QU'UNE LISTE À COCHER NE CALCULE PAS ════
L'IMPLICATION PLAFONNE LE TAUX. Le document consacre une sous-étape entière
(2.3) à une question à trois réponses : l'entreprise CAUSE l'impact, elle y
CONTRIBUE, ou elle y est seulement LIÉE par une relation d'affaires. Et il
dit ce que chacune commande :

    cause       → cesser, prévenir, et RÉPARER le dommage causé
    contribue   → cesser sa contribution, réparer SA PART, et construire son
                  levier sur la relation d'affaires
    lien direct → user de son levier, et le construire si besoin

Le plafond en découle sans qu'on l'invente : le taux global ne peut pas
dépasser celui de l'étape que l'implication déclarée rend NON NÉGOCIABLE. Un
client qui déclare « je cause » et laisse l'étape 6 à zéro n'a pas une étape
à moitié tenue — il a l'attente la plus forte du cadre non tenue.

ET L'IMPLICATION N'EST PAS FIGÉE : le document écrit qu'un lien direct
devient une contribution si l'entreprise continue sans rien faire. Le module
le répète à l'écran plutôt que de laisser croire à un classement acquis.

LA PRIORISATION EXIGE SA JUSTIFICATION. L'étape 2.4 se cote sur quatre
facteurs — échelle, portée, irrémédiabilité, probabilité — et le document
demande un processus CRÉDIBLE, dont la logique est rendue publique. Une
cotation sans justification écrite n'est donc pas une priorisation : c'est un
chiffre. Le module plafonne la part « identifier » tant qu'une ligne cotée
n'a pas sa justification.

LES TROIS GROUPES NE SONT PAS EXCLUSIFS. Le document le dit expressément.
Un même client peut fournir des intrants ET exploiter un système : le module
accepte plusieurs groupes, et les 115 exemples qui ne visent aucun des
groupes déclarés sortent du calcul au lieu de compter zéro.

═══ CE QUE CE MODULE REFUSE DE DIRE ═════════════════════════════════════
QU'IL Y A UN TAUX DE CONFORMITÉ. Le document déclare ses exemples pratiques
non exhaustifs — « not meant to represent an exhaustive check list ». Un
score plein sur une liste que sa propre source dit incomplète serait un
mensonge par arrondi. Ce que le module rend s'appelle COUVERTURE DES
EXEMPLES RETENUS, et jamais conformité.

QUE TENIR ISO/IEC 42001 OU LE CADRE DU NIST VAUT DILIGENCE OCDE. Les six
feuilles de route montrent où les cadres se recoupent ; le document interdit
d'en faire une équivalence — « this table is not an equivalency framework,
as the scope and nature of the expectations in the other frameworks may
vary ». Le module affiche l'avertissement sur l'écran qui porte les ponts.

QU'IL PORTE UN CATALOGUE DE RISQUES. Le document se déclare « risk-agnostic
to remain evergreen » : il ne liste pas les risques de l'IA, et ce module
n'en invente pas.

QU'IL COUVRE LA CHAÎNE DU MATÉRIEL. Le document s'en exclut lui-même et
renvoie au guide OCDE sur les minerais.
"""
import datetime


# ═══════════════════════════════════════════════════════════════════════════
#  1. LA SOURCE, ET SA LICENCE
# ═══════════════════════════════════════════════════════════════════════════

SOURCE = {
    "titre": "OCDE — Guide sur le devoir de diligence pour une intelligence "
             "artificielle responsable",
    "court": "Diligence OCDE · IA responsable",
    "en": "OECD Due Diligence Guidance for Responsible AI",
    "editeur": "OCDE — Comité de la politique de l'économie numérique (CPEN, "
               "par son Groupe de travail sur la gouvernance de l'IA) et "
               "Comité de l'investissement (par son Groupe de travail sur la "
               "conduite responsable des entreprises)",
    "millesime": "2026-05 (version révisée)",
    "approuve": "Approuvé et déclassifié le 26 janvier 2026",
    "doi": "https://doi.org/10.1787/41671712-en",
    "isbn": "978-92-64-31822-9 (PDF)",
    "citation": "OECD (2026), OECD Due Diligence Guidance for Responsible AI, "
                "OECD Publishing, Paris, "
                "https://doi.org/10.1787/41671712-en.",
    "met_en_oeuvre": "Les Principes de l'OCDE sur l'IA (Recommandation du "
                     "Conseil sur l'intelligence artificielle, révisée en "
                     "mai 2024) et le Guide OCDE à l'intention des "
                     "entreprises multinationales sur la conduite "
                     "responsable des entreprises (2023)",
    "socle": "Guide OCDE sur le devoir de diligence pour une conduite "
             "responsable des entreprises (2018)",
    #  LA PRÉSOMPTION EST LE SEUL CHAMP QUI VAILLE DE L'ARGENT. Elle est
    #  fausse ici, et elle ne deviendra pas vraie : la garde du module
    #  refuse qu'on écrive l'inverse.
    "presomption": False,
    "volontaire": True,
    "licence": "Creative Commons Attribution 4.0 International (CC BY 4.0) — "
               "© OCDE 2026. La reproduction, la traduction et l'adaptation "
               "sont permises, à charge de citer l'œuvre, d'identifier les "
               "modifications et de porter les mentions que la licence "
               "impose. Le matériel de tiers en est exclu.",
}

#: LA MENTION QUE LA LICENCE IMPOSE À UNE TRADUCTION, mot pour mot. Les
#: intitulés des six étapes sont traduits en français : elle est due.
MENTION_TRADUCTION = (
    "In the event of any discrepancy between the original work and the "
    "translation, only the text of the original work should be considered "
    "valid."
)

#: LA MENTION QUE LA LICENCE IMPOSE À UNE ADAPTATION, mot pour mot. Le
#: découpage du questionnaire, les poids et les plafonds sont une adaptation
#: du cadre : elle est due aussi.
MENTION_ADAPTATION = (
    "This is an adaptation of an original work by the OECD. The opinions "
    "expressed and arguments employed in this adaptation should not be "
    "reported as representing the official views of the OECD or of its "
    "Member countries."
)

#: CE QUE LA LICENCE INTERDIT, et qui commande une décision de maquette.
INTERDITS = (
    {"cle": "logo",
     "dit": "Le logo, l'identité visuelle et l'image de couverture de l'OCDE "
            "ne peuvent pas être employés sans autorisation expresse.",
     "fait": "La couleur du tiroir de ce module dans la barre latérale n'est "
             "pas le bleu de l'OCDE, et aucune marque de l'OCDE n'est "
             "reproduite."},
    {"cle": "adossement",
     "dit": "Il est interdit de suggérer que l'OCDE adosse cet usage de "
            "l'œuvre.",
     "fait": "Les deux mentions de licence voyagent avec le référentiel, et "
             "l'écran dit que les poids, les plafonds et le découpage du "
             "questionnaire sont du cabinet."},
    {"cle": "tiers",
     "dit": "La licence ne couvre pas le matériel de tiers présent dans "
            "l'œuvre.",
     "fait": "Les feuilles de route citent les clauses d'ISO, de l'IEEE et "
             "d'AI Verify par NUMÉRO ET INTITULÉ seulement, comme un index."},
)

RESERVE_VOLONTAIRE = (
    "Cet instrument est VOLONTAIRE : c'est le guide de mise en œuvre de deux "
    "recommandations de l'OCDE, pas une norme harmonisée. Il n'ouvre aucune "
    "présomption de conformité, aucun organisme ne délivre d'attestation "
    "contre lui, et aucune date ne changera cela — à la différence de prEN "
    "18286, qui vaudra présomption le jour de sa citation au Journal "
    "officiel. Le travail fait ici sert la diligence de l'entreprise et les "
    "cadres que les feuilles de route nomment ; il ne tient lieu d'aucun."
)

#: LE PÉRIMÈTRE QUE LE DOCUMENT S'EXCLUT LUI-MÊME, déclaré plutôt que tu.
HORS_PERIMETRE = (
    {"cle": "materiel",
     "quoi": "Les chaînes d'approvisionnement des intrants matériels — "
             "extraction des matières premières, fabrication des composants.",
     "dit": "Le document s'en exclut expressément et renvoie à un autre "
            "guide de diligence de l'OCDE."},
    {"cle": "catalogue_de_risques",
     "quoi": "Une liste des risques propres à l'IA.",
     "dit": "Le document se déclare « risk-agnostic » pour rester valable "
            "dans le temps : il nomme des cadres qui listent des risques, il "
            "n'en dresse pas la liste. Ce module ne lui en prête pas une."},
    {"cle": "equivalence",
     "quoi": "Une table d'équivalence entre les cadres.",
     "dit": "Les six feuilles de route montrent où les exigences se "
            "ressemblent. Le document écrit qu'elles ne constituent PAS un "
            "cadre d'équivalence, « as the scope and nature of the "
            "expectations in the other frameworks may vary »."},
)

#: L'AVERTISSEMENT DU DOCUMENT SUR SES PROPRES EXEMPLES, repris verbatim : il
#: interdit de lire la couverture comme un taux de conformité.
AVERTISSEMENT_EXEMPLES = (
    "The practical examples are not meant to represent an exhaustive check "
    "list."
)

#: ET CELUI QUI PORTE SUR LES FEUILLES DE ROUTE.
AVERTISSEMENT_FEUILLES = (
    "Although the provisions are related to implementation of the RBC due "
    "diligence framework, this table is not an equivalency framework, as the "
    "scope and nature of the expectations in the other frameworks may vary."
)


# ═══════════════════════════════════════════════════════════════════════════
#  2. LES TROIS GROUPES D'ACTEURS — ET ILS NE SONT PAS EXCLUSIFS
# ═══════════════════════════════════════════════════════════════════════════
#
# LE DOCUMENT LE DIT EXPRESSÉMENT : les groupes « are not rigid nor
# exclusive ». Un éditeur qui entraîne un modèle sur ses propres données et
# l'exploite pour ses clients est dans le groupe 1 ET dans le groupe 2. Les
# autres modules de Sentinel font choisir UN rôle ; celui-ci accepte
# plusieurs groupes, parce que sa source l'exige.

GROUPES = (
    {"cle": "intrants", "num": 1,
     "nom": "Fournisseur d'intrants d'IA",
     "en": "Suppliers of AI inputs",
     "amont": True,
     "dit": "Vous fournissez ce avec quoi un système d'IA se construit : "
            "données, annotation, création et conservation de jeux de "
            "données, code mis à disposition de tiers — contributions à des "
            "bibliothèques ouvertes comprises —, métriques et mesures "
            "d'évaluation. Ou les intrants qui le portent : capital, "
            "infrastructure numérique et services administratifs (calcul, "
            "nuage, plateformes de paiement, plateformes de travail "
            "numériques, systèmes d'exploitation, magasins d'applications, "
            "éditeurs de sécurité et de logiciels d'entreprise), matériel "
            "(semi-conducteurs, équipements réseau).",
     "exemples": ("données et annotation", "jeux de données",
                  "code pour des tiers", "métriques d'évaluation",
                  "capital", "calcul et nuage", "matériel")},
    {"cle": "cycle_vie", "num": 2,
     "nom": "Acteur du cycle de vie du système",
     "en": "Enterprises actively involved in the design, development, "
           "deployment, and operation of AI systems",
     "amont": None,
     "dit": "Vous êtes dans le cycle de vie du système : planification et "
            "conception, construction du modèle ou adaptation d'un modèle "
            "existant, test, évaluation, vérification et validation, "
            "déploiement quel qu'en soit le canal — y compris la "
            "distribution de logiciel ouvert —, exploitation pour des "
            "clients et surveillance. Un organisme qui modifie et "
            "redéploie un modèle existant pour son propre usage en fait "
            "partie.",
     "exemples": ("conception", "construction ou adaptation du modèle",
                  "test et validation", "déploiement",
                  "exploitation et surveillance")},
    {"cle": "utilisateur", "num": 3,
     "nom": "Utilisateur du système d'IA",
     "en": "Users of the AI system",
     "amont": False,
     "dit": "Vous utilisez des systèmes d'IA dans vos opérations, vos "
            "produits ou vos services — établissements financiers et "
            "entreprises de l'économie réelle comprises, y compris celles "
            "dont le métier n'a rien à voir avec l'IA. Le document attend de "
            "vous que la diligence sur ces systèmes entre dans votre "
            "diligence d'ensemble : si le système ne porte pas de risque "
            "significatif, d'autres sujets passent devant.",
     "exemples": ("usage dans les opérations", "usage dans les produits",
                  "usage dans les services")},
)

GROUPES_PAR_CLE = {g["cle"]: g for g in GROUPES}

NON_EXCLUSIFS = (
    "Les trois groupes ne sont ni rigides ni exclusifs — le document le dit "
    "lui-même. Déclarez-en autant que votre organisme en occupe : le "
    "questionnaire montre alors les exemples de chacun, et ceux qu'aucun de "
    "vos groupes ne vise sortent du calcul au lieu de compter zéro."
)

#: CE QUE LE DOCUMENT DIT DES PME, et qui ne les exonère de rien.
PME = (
    "Les PME sont tenues à la diligence comme les autres. Le document "
    "reconnaît qu'elles n'en ont pas la même capacité — moyens limités, "
    "levier plus faible sur les relations d'affaires, coût de la prévention "
    "— et que la mesure se proportionne à leur situation. Elle ne disparaît "
    "pas."
)


# ═══════════════════════════════════════════════════════════════════════════
#  3. LES SIX ÉTAPES, ET LES DOUZE UNITÉS QUI SE RENSEIGNENT
# ═══════════════════════════════════════════════════════════════════════════
#
# LE FRANÇAIS EST DU CABINET, L'ANGLAIS EST DU DOCUMENT. Les intitulés
# anglais sont repris tels quels ; « nom » est une traduction et « demande »
# une reformulation — c'est à ce titre que MENTION_TRADUCTION et
# MENTION_ADAPTATION voyagent avec le référentiel.
#
# LE POIDS SUIT LA CHARGE, PAS LE NOMBRE D'EXEMPLES. L'étape 3 porte
# vingt-quatre exemples pour le seul groupe 2 et l'étape 6 n'en porte que
# deux : compter les exemples ferait de l'étape 6 un détail, alors que c'est
# l'attente la plus forte du cadre dès que l'entreprise cause ou contribue.

ETAPES = (
    {"num": 1, "cle": "ancrer",
     "nom": "Ancrer la conduite responsable dans les politiques et les "
            "systèmes de management",
     "poids": 1,
     "pourquoi": "Le socle, et celui qu'un système de management déjà en "
                 "place — ISO/IEC 42001, ISO 9001, un dispositif RSE — "
                 "apporte le plus souvent tel quel."},
    {"num": 2, "cle": "identifier",
     "nom": "Identifier et évaluer les incidences négatives réelles et "
            "potentielles",
     "poids": 3,
     "pourquoi": "L'étape qui commande toutes les autres : sans incidences "
                 "identifiées, qualifiées par l'implication et priorisées, "
                 "les étapes 3 à 6 n'ont pas d'objet."},
    {"num": 3, "cle": "traiter",
     "nom": "Faire cesser, prévenir et atténuer les incidences négatives",
     "poids": 3,
     "pourquoi": "Le seul endroit où quelque chose change pour les "
                 "personnes. Tout le reste documente ; celle-ci agit."},
    {"num": 4, "cle": "suivre",
     "nom": "Suivre la mise en œuvre et les résultats de la diligence",
     "poids": 1,
     "pourquoi": "Ce qui empêche la diligence d'être un exercice annuel : "
                 "le document demande de chercher ce que les passes "
                 "précédentes ont manqué."},
    {"num": 5, "cle": "communiquer",
     "nom": "Rendre compte des actions menées",
     "poids": 1,
     "pourquoi": "La part que les parties prenantes peuvent vérifier. Elle "
                 "ne crée rien par elle-même et rend le reste opposable."},
    {"num": 6, "cle": "reparer",
     "nom": "Assurer la réparation ou y coopérer, lorsqu'il y a lieu",
     "poids": 2,
     "pourquoi": "Deux exemples pratiques seulement, et l'attente la plus "
                 "forte du cadre : dès que l'entreprise cause ou contribue, "
                 "elle est attendue sur la réparation du dommage, pas "
                 "seulement sur sa prévention."},
)

ETAPES_PAR_NUM = {e["num"]: e for e in ETAPES}
ETAPES_PAR_CLE = {e["cle"]: e for e in ETAPES}

#: LES DOUZE UNITÉS QUI SE RENSEIGNENT. Neuf sous-étapes des étapes 1 à 3, et
#: les étapes 4, 5 et 6 que le document ne subdivise pas. Deux d'entre elles
#: — 2.3 et 2.4 — se renseignent AUSSI sur l'écran « processus », parce
#: qu'elles portent une structure et pas seulement un état : c'est là que le
#: plafond se calcule.
UNITES = (
    {"cle": "1.1", "etape": 1, "nom": "Politiques de conduite responsable",
     "demande": "Des politiques écrites, adoptées et diffusées, qui "
                "énoncent l'engagement de l'organisme sur les Principes de "
                "l'OCDE sur l'IA et le Guide EM — et qui portent le plan de "
                "mise en œuvre de la diligence, pour les opérations propres "
                "comme pour les relations d'affaires.",
     "piege": "Une politique IA écrite par la conformité et jamais lue par "
              "ceux qui construisent. Elle existe, elle est datée, et elle "
              "ne change aucune décision d'architecture."},
    {"cle": "1.2", "etape": 1, "nom": "Systèmes de management internes",
     "demande": "L'ancrage dans les organes, les structures, les processus "
                "et les équipes, de sorte que la diligence se fasse dans le "
                "cours normal du travail — en tenant compte de "
                "l'indépendance et de l'autonomie que le droit national "
                "reconnaît à certains de ces organes.",
     "piege": "Une responsabilité attribuée à une fonction qui n'a ni le "
              "budget ni l'autorité d'arrêter une mise en service. Elle "
              "signera ce qu'on lui présentera."},
    {"cle": "1.3", "etape": 1,
     "nom": "Attentes vis-à-vis des relations d'affaires",
     "demande": "Les attentes et les politiques portées dans la relation "
                "elle-même : fournisseurs d'intrants, partenaires de "
                "vente, clients et utilisateurs.",
     "piege": "Des attentes communiquées une fois à la signature, jamais "
              "reprises ensuite. Le document demande des canaux qui "
              "durent."},
    {"cle": "2.1", "etape": 2, "nom": "Cadrage initial des risques",
     "demande": "Un exercice de cadrage qui dit OÙ les risques peuvent se "
                "trouver et où ils peuvent être les plus significatifs — "
                "avant toute évaluation approfondie.",
     "piege": "Un cadrage qui s'arrête aux systèmes que la DSI a achetés. "
              "Les usages arrivés par une carte bancaire d'équipe n'y "
              "figurent pas, et ce sont ceux qui posent problème."},
    {"cle": "2.2", "etape": 2,
     "nom": "Évaluation approfondie des risques les plus significatifs",
     "demande": "Des évaluations itératives et de plus en plus fines, sur "
                "DEUX périmètres que le document sépare : les activités "
                "propres de l'organisme, et ses relations d'affaires.",
     "piege": "Une évaluation faite une fois, à la mise en service, sur la "
              "version d'alors. Le fournisseur a changé le modèle depuis."},
    {"cle": "2.3", "etape": 2,
     "nom": "Apprécier son implication dans l'incidence",
     "demande": "Causer, contribuer, ou être lié : la question à trois "
                "réponses qui décide du niveau de diligence attendu. Elle "
                "se renseigne sur l'écran « processus », et c'est elle qui "
                "plafonne le taux.",
     "piege": "Se ranger en « lien direct » et ne rien faire. Le document "
              "écrit que le lien direct devient une CONTRIBUTION si "
              "l'entreprise continue sans agir."},
    {"cle": "2.4", "etape": 2,
     "nom": "Prioriser les risques les plus saillants",
     "demande": "La priorisation sur la gravité et la probabilité, quand il "
                "n'est pas possible de tout traiter en même temps. Les "
                "quatre facteurs se cotent sur l'écran « processus », et "
                "chacun demande sa justification écrite.",
     "piege": "Une cotation sans justification. Le document demande un "
              "processus CRÉDIBLE dont la logique est rendue publique : un "
              "chiffre sans raison n'en est pas un."},
    {"cle": "3.1", "etape": 3,
     "nom": "Traiter les risques que l'organisme cause ou auxquels il "
            "contribue",
     "demande": "Faire cesser ce qui cause ou contribue, et bâtir les plans "
                "qui préviennent et atténuent les incidences futures.",
     "piege": "Un registre de risques tenu à jour et jamais arbitré. Tout y "
              "est noté, rien n'y est refusé, et le système part quand "
              "même."},
    {"cle": "3.2", "etape": 3,
     "nom": "Traiter les risques auxquels l'organisme est lié par une "
            "relation d'affaires",
     "demande": "User de son levier sur la relation d'affaires — et le "
                "construire s'il manque. Le document nomme trois réponses "
                "possibles : poursuivre la relation pendant l'atténuation, "
                "la suspendre temporairement, ou s'en désengager.",
     "piege": "Un désengagement présenté comme la seule réponse "
              "responsable. Partir peut aggraver l'incidence pour les "
              "personnes et supprime le levier qui restait."},
    {"cle": "4", "etape": 4,
     "nom": "Suivre la mise en œuvre et les résultats",
     "demande": "Chercher ce que les passes précédentes ont manqué, "
                "vérifier que des risques évalués ne sont pas devenus "
                "inacceptables, et mesurer l'efficacité de l'association "
                "des parties prenantes elle-même.",
     "piege": "Un suivi qui mesure l'activité — nombre de revues, nombre "
              "de formations — et jamais le résultat pour les personnes."},
    {"cle": "5", "etape": 5,
     "nom": "Rendre compte des actions menées",
     "demande": "Communiquer à l'extérieur les politiques, les processus, "
                "les incidences identifiées et priorisées, les critères de "
                "priorisation, les mesures prises et leurs résultats — avec "
                "les égards dus au secret des affaires et au droit de la "
                "concurrence.",
     "piege": "Un rapport qui publie les politiques et jamais les "
              "incidences. Le document demande les deux, et nomme les "
              "capacités, limites et usages inappropriés du système."},
    {"cle": "6", "etape": 6,
     "nom": "Assurer la réparation ou y coopérer",
     "demande": "Lorsque l'organisme a causé une incidence réelle ou y a "
                "contribué, rétablir les personnes dans la situation qui "
                "serait la leur si elle ne s'était pas produite, autant que "
                "possible, et à la mesure de l'incidence.",
     "piege": "Un dispositif de réclamation qui existe sans être "
              "accessible. Le document attend un mécanisme légitime par "
              "lequel les parties prenantes peuvent réellement saisir "
              "l'entreprise."},
)

UNITES_PAR_CLE = {u["cle"]: u for u in UNITES}
UNITES_DE_L_ETAPE = {}
for _u in UNITES:
    UNITES_DE_L_ETAPE.setdefault(_u["etape"], []).append(_u["cle"])


# ═══════════════════════════════════════════════════════════════════════════
#  4. L'IMPLICATION — CAUSER, CONTRIBUER, ÊTRE LIÉ
# ═══════════════════════════════════════════════════════════════════════════
#
# C'EST LA PIÈCE PROPRE AU CADRE DE L'OCDE, et celle qu'aucun des treize
# autres référentiels de Sentinel ne porte. L'IA Act demande ce que le
# système est ; celui-ci demande ce que l'entreprise a FAIT dans l'incidence.
# Et la réponse commande des attentes différentes — c'est pourquoi elle
# plafonne le taux au lieu d'ajouter une case.

IMPLICATIONS = (
    {"cle": "cause", "num": 1, "nom": "L'organisme CAUSE l'incidence",
     "en": "Causing the impact",
     "attendu": "Faire cesser l'activité qui cause, prévenir les incidences "
                "potentielles, et RÉPARER le dommage déjà causé.",
     #  LES ÉTAPES QUE CETTE IMPLICATION REND NON NÉGOCIABLES : le taux
     #  global ne pourra pas les dépasser.
     "commande": ("traiter", "reparer"),
     "dit": "Votre activité produit l'incidence par elle-même. Le document "
            "attend la cessation ET la réparation : prévenir ne suffit "
            "plus, le dommage existe."},
    {"cle": "contribue", "num": 2, "nom": "L'organisme CONTRIBUE à l'incidence",
     "en": "Contributing to the impact",
     "attendu": "Faire cesser sa contribution, prévenir celle à venir, "
                "réparer SA PART du dommage, et construire son levier sur "
                "les relations d'affaires pour prévenir le reste.",
     "commande": ("traiter", "reparer"),
     "dit": "Votre activité, combinée à celle d'autres, produit "
            "l'incidence ; ou elle cause, facilite ou encourage un autre à "
            "la produire. Le document exige que la contribution soit "
            "SUBSTANTIELLE : elle n'inclut pas les contributions mineures "
            "ou négligeables."},
    {"cle": "lien_direct", "num": 3,
     "nom": "L'organisme est LIÉ à l'incidence par une relation d'affaires",
     "en": "Directly linked to the impact",
     "attendu": "User de son levier sur la ou les relations d'affaires pour "
                "qu'elles préviennent ou atténuent — et construire ce "
                "levier s'il manque.",
     "commande": ("traiter",),
     "dit": "L'incidence est rattachée à vos opérations, produits ou "
            "services par une relation d'affaires. Le document note que la "
            "contribution ou le lien direct, une fois le système déployé, "
            "vendu ou revendu, va souvent avec un risque non atténué à la "
            "conception ou un utilisateur final à haut risque."},
)

IMPLICATIONS_PAR_CLE = {i["cle"]: i for i in IMPLICATIONS}
ORDRE_IMPLICATIONS = tuple(i["cle"] for i in IMPLICATIONS)

#: ELLE N'EST PAS FIGÉE, et le module le répète plutôt que de laisser croire
#: à un classement acquis. Le document l'écrit deux fois.
IMPLICATION_NON_FIGEE = (
    "La relation d'un organisme à une incidence n'est pas statique. Elle "
    "change avec la situation, et avec ce que la diligence fait baisser. Le "
    "document le dit dans l'autre sens aussi : un organisme qui reste lié à "
    "une incidence et ne prend aucune mesure pour l'atténuer voit son lien "
    "direct devenir une CONTRIBUTION avec le temps."
)

#: LES OPTIONS DE RÉPARATION QUE LE DOCUMENT NOMME, pour que l'écran ne
#: réduise pas « réparer » à « indemniser ».
REPARATIONS = (
    {"cle": "restitution", "nom": "Restitution",
     "dit": "Rétablir la personne ou le groupe dans la position qui serait "
            "la sienne si le dommage ne s'était pas produit."},
    {"cle": "compensation", "nom": "Compensation",
     "dit": "Une compensation financière pour le dommage économiquement "
            "appréciable — atteinte physique ou morale, perte de revenus."},
    {"cle": "autres", "nom": "Les autres formes",
     "dit": "Le document note que plusieurs options peuvent se combiner "
            "selon l'ampleur et le contexte du dommage, et que la "
            "réparation effective dépend du contexte."},
)


# ═══════════════════════════════════════════════════════════════════════════
#  5. LA PRIORISATION — QUATRE FACTEURS, ET LA JUSTIFICATION QUI LES REND
#     CRÉDIBLES
# ═══════════════════════════════════════════════════════════════════════════
#
# LE DOCUMENT DONNE LES FACTEURS, PAS LE BARÈME. Il n'y a pas de formule dans
# le tableau 2.3 : il nomme quatre facteurs et demande un processus
# CRÉDIBLE, dont la logique est rendue publique. Le module code donc ce que
# la conduite responsable tient de longue date — la GRAVITÉ se lit sur
# l'échelle, la portée et l'irrémédiabilité, et la SAILLANCE combine la
# gravité avec la probabilité — et il nomme ce choix comme un choix du
# cabinet, pas comme une prescription de l'OCDE.

FACTEURS = (
    {"cle": "echelle", "nom": "Échelle", "en": "Scale",
     "gravite": True,
     "dit": "La gravité de l'incidence.",
     "exemple": "Un système d'IA employé pour déterminer la durée des "
                "peines dans des affaires pénales."},
    {"cle": "portee", "nom": "Portée", "en": "Scope",
     "gravite": True,
     "dit": "L'étendue de l'incidence — combien de personnes, quel "
            "territoire.",
     "exemple": "Des recommandations biaisées dans un service public d'aide "
                "sociale, qui aboutissent à la suppression de l'aide pour "
                "des milliers de familles."},
    {"cle": "irremediabilite", "nom": "Irrémédiabilité", "en": "Irremediability",
     "gravite": True,
     "dit": "La mesure dans laquelle l'incidence peut être réparée — les "
            "limites à la possibilité de rétablir les personnes ou "
            "l'environnement dans leur situation antérieure.",
     "exemple": "Une incidence dont le dommage ne peut pas être défait, "
                "quelle que soit la somme engagée ensuite."},
    {"cle": "probabilite", "nom": "Probabilité", "en": "Likelihood",
     "gravite": False,
     "dit": "L'estimation de la probabilité que l'incidence se produise.",
     "exemple": "Un risque dont la réalisation est déjà documentée dans un "
                "déploiement comparable."},
)

FACTEURS_PAR_CLE = {f["cle"]: f for f in FACTEURS}
FACTEURS_DE_GRAVITE = tuple(f["cle"] for f in FACTEURS if f["gravite"])

#: LES TROIS NIVEAUX, ET LEUR VALEUR. Trois et pas cinq : le document ne
#: gradue rien, et une échelle plus fine prêterait à sa source une précision
#: qu'elle n'a pas.
NIVEAUX = {
    "faible": {"nom": "Faible", "valeur": 1},
    "moyen": {"nom": "Moyen", "valeur": 2},
    "eleve": {"nom": "Élevé", "valeur": 3},
}
ORDRE_NIVEAUX = ("faible", "moyen", "eleve")

#: LA SAILLANCE : trois paliers, nommés par le produit de la gravité et de la
#: probabilité. Les bornes sont du cabinet.
PALIERS_SAILLANCE = (
    {"cle": "a_suivre", "nom": "À suivre", "min": 1,
     "dit": "Reste au registre et se revoit ; ne commande pas d'action "
            "immédiate."},
    {"cle": "a_traiter", "nom": "À traiter", "min": 5,
     "dit": "Entre dans le plan de l'étape 3, après les risques saillants."},
    {"cle": "saillant", "nom": "Saillant", "min": 7,
     "dit": "Le document attend qu'il passe devant : c'est un des risques "
            "les plus significatifs, et l'étape 3 commence par lui."},
)


# ═══════════════════════════════════════════════════════════════════════════
#  6. LES CADRES QUE LES FEUILLES DE ROUTE NOMMENT — ET CEUX QUE SENTINEL
#     MESURE VRAIMENT
# ═══════════════════════════════════════════════════════════════════════════
#
# CE QUE CE MODULE APPORTE ET QU'AUCUN AUTRE N'APPORTE : les ponts, c'est le
# DOCUMENT qui les donne, pas le cabinet. Six tableaux, un par étape,
# quatre-vingt-onze lignes, vingt cadres nationaux et internationaux.
#
# ET LE CHIFFRE HONNÊTE QUI VA AVEC : sur ces vingt cadres, Sentinel en
# MESURE TROIS. Les dix-sept autres sont nommés par l'OCDE et non tenus par
# le cabinet. L'écran l'affiche, comme l'annexe ZA de prEN 18286 affiche
# « non couvert » en face de l'article 17(2) : un pont vers un cadre qu'on ne
# mesure pas reste un renseignement utile, pas une couverture.

CADRES = (
    {"cle": "asean", "nom": "ASEAN — Guide on AI Governance and Ethics",
     "mesure": None},
    {"cle": "australie",
     "nom": "Australie — Guidance for AI Adoption (Implementation Practices)",
     "mesure": None},
    {"cle": "canada",
     "nom": "Canada — Voluntary Code of Conduct on the Responsible "
            "Development and Management of Advanced Generative AI Systems",
     "mesure": None},
    {"cle": "coe",
     "nom": "Conseil de l'Europe — Convention-cadre sur l'IA et "
            "méthodologie HUDERIA",
     "mesure": None},
    {"cle": "ia_act", "nom": "Règlement (UE) 2024/1689 — IA Act",
     "mesure": "ia_act"},
    {"cle": "dsa", "nom": "Règlement (UE) 2022/2065 — DSA",
     "mesure": None,
     "note": "Le site porte une page /dsa qui expose le règlement ; aucun "
             "module ne le mesure."},
    {"cle": "csddd",
     "nom": "Directive (UE) 2024/1760 — devoir de vigilance des entreprises "
            "en matière de durabilité (CSDDD)",
     "mesure": None},
    {"cle": "hiroshima",
     "nom": "Processus d'Hiroshima — Code de conduite international pour les "
            "systèmes d'IA avancés",
     "mesure": None},
    {"cle": "ieee7000", "nom": "IEEE 7000-2021", "mesure": None,
     "tiers": True},
    {"cle": "iso31000", "nom": "ISO 31000 et ISO/IEC 23894", "mesure": None,
     "tiers": True},
    {"cle": "iso23894", "nom": "ISO/IEC 23894 — management du risque de l'IA",
     "mesure": None, "tiers": True},
    {"cle": "iso38507",
     "nom": "ISO/IEC 38507:2022 — gouvernance de l'usage de l'IA",
     "mesure": None, "tiers": True},
    {"cle": "iso42001",
     "nom": "ISO/IEC 42001 — système de management de l'IA",
     "mesure": "iso42001", "tiers": True},
    {"cle": "iso42005", "nom": "ISO/IEC 42005 — évaluation d'impact d'un SIA",
     "mesure": None, "tiers": True},
    {"cle": "japon", "nom": "Japon — AI Guidelines for Business v1.1",
     "mesure": None},
    {"cle": "coree", "nom": "Corée — AI Basic Act", "mesure": None},
    {"cle": "singapour", "nom": "Singapour — AI Verify Testing Framework",
     "mesure": None, "tiers": True},
    {"cle": "uk", "nom": "Royaume-Uni — DSIT, Introduction to AI Assurance",
     "mesure": None},
    {"cle": "ungp",
     "nom": "ONU — Principes directeurs relatifs aux entreprises et aux "
            "droits de l'homme",
     "mesure": None},
    {"cle": "nist", "nom": "États-Unis — NIST AI Risk Management Framework",
     "mesure": "nist_ai_rmf"},
)

CADRES_PAR_CLE = {c["cle"]: c for c in CADRES}

#: LES CADRES QUE SENTINEL MESURE, nommés une seule fois. Une règle les
#: confronte à conformite.NORMES : un pont qui désignerait une norme que le
#: taux de conformité ne connaît pas serait une promesse en l'air.
CADRES_MESURES = tuple(c["cle"] for c in CADRES if c["mesure"])

#: LES CADRES DONT LE DOCUMENT CITE DES CLAUSES SOUS DROIT D'AUTEUR DE TIERS.
#: La licence CC BY de l'OCDE ne les couvre pas : numéro et intitulé, rien
#: d'autre, comme pour les modules ISO de ce dépôt.
CADRES_TIERS = tuple(c["cle"] for c in CADRES if c.get("tiers"))


# ═══════════════════════════════════════════════════════════════════════════
#  7. CE QUE LE DOCUMENT ÉCRIT — INTITULÉS, EXEMPLES, FEUILLES DE ROUTE
# ═══════════════════════════════════════════════════════════════════════════
#
# LE SEUL BLOC DE CE MODULE QUI SOIT REPRIS DU DOCUMENT. Il est extrait du
# PDF plutôt que recopié à la main, et la garde recompte ce qu'il porte : 115
# exemples pratiques, 12 unités, 91 lignes de pont sur 6 feuilles de route.
#: LES SIX ETAPES, dans leur intitule anglais du document. Le nom
#: francais, lui, est du cabinet : c'est une TRADUCTION, et la licence
#: impose de le dire (voir MENTION_ADAPTATION).
ETAPES_EN = {
    1: u"Embed RBC into policies and management systems",
    2: u"Identify and assess actual and potential adverse impacts",
    3: u"Cease, prevent and mitigate adverse impacts",
    4: u"Track implementation and results of due diligence activities",
    5: u"Communicate actions to address impacts",
    6: u"Provide for or co-operate in remediation when appropriate",
}

#: LES SOUS-ETAPES, meme regime : numero et intitule anglais du document.
SOUS_ETAPES_EN = (
    ("1.1", 1, u"RBC policies"),
    ("1.2", 1, u"Internal management systems"),
    ("1.3", 1, u"Expectations on business relationships"),
    ("2.1", 2, u"Initial scoping of risks"),
    ("2.2", 2, u"In-depth assessment of most significant risks"),
    ("2.3", 2, u"Assess involvement with the actual or potential impact (cause, contribute,"),
    ("2.4", 2, u"Prioritise the most significant (i.e., most salient) risks"),
    ("3.1", 3, u"Addressing risks that the enterprise causes or contributes to"),
    ("3.2", 3, u"Addressing risks directly linked to the enterprise throughout the AI value chain."),
)

#: LES EXEMPLES PRATIQUES DU DOCUMENT, repris VERBATIM EN ANGLAIS.
#: Pourquoi en anglais : meme raison que pour le profil du NIST, c'est
#: le libelle qu'un auditeur cherchera, et la licence autorise la
#: reproduction avec attribution sans obliger a la mention d'adaptation
#: que porterait une traduction. « volet » est le sous-titre que le
#: document donne a un bloc quand il en donne deux pour la meme
#: sous-etape.
EXEMPLES = (
    {"cle": "1.1-1", "unite": "1.1",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"In addition to commitments to relevant RBC principles and "
           u"standards, commit to implement the OECD AI Principles, as relevant, "
           u"through the design, development, deployment, operation and use of "
           u"AI systems (i.e., human -centred, fair, transparent, explainable, "
           u"robust, secure, safe, and accountable)."},
    {"cle": "1.1-2", "unite": "1.1",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Develop or review and update existing RBC policies, including risk "
           u"management policies, with the active participation of stakeholders, "
           u"including workers, workers’ representatives and trade unions, to "
           u"align with principles from relevant international, regional and "
           u"national frameworks."},
    {"cle": "1.1-3", "unite": "1.1",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Build on findings from the risk assessment (see Step 2) in order to "
           u"update or more clearly define the enterprise’s approach to "
           u"addressing the most significant risks identified ( see Step 3)."},
    {"cle": "1.1-4", "unite": "1.1",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Set risk-tolerance thresholds to help determine low, medium, high "
           u"severity and likelihood of risks and guide appropriate responses or "
           u"trigger deeper due diligence."},
    {"cle": "1.1-5", "unite": "1.1",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Make risk management policies publicly available as appropriate, "
           u"(e.g., on the enterprise’s website, and when relevant, in the local "
           u"languages of areas where the enterprise operates or maintains "
           u"business relationships). In some cases, enterprises may wish to "
           u"make more detailed policies and risk management information "
           u"available to specific stakeholders and business relationships ( see "
           u"Step 5) or take specific commitments on certain risks and issues.  "
           u"21"},
    {"cle": "1.1-6", "unite": "1.1",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Consider policies that are sufficiently flexible and technology "
           u"neutral to allow a margin for future developments while also being "
           u"precise enough to provide guidance to operational teams."},
    {"cle": "1.1-7", "unite": "1.1",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Consider aligning policies with relevant national strategies to "
           u"ensure coherence between RBC commitments and the host country's "
           u"priorities."},
    {"cle": "1.2-8", "unite": "1.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Assign oversight and responsibility for AI due diligence to "
           u"relevant senior management and assign responsibilities to the board "
           u"of directors for AI RBC more broadly."},
    {"cle": "1.2-9", "unite": "1.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Assign responsibility for implementing aspects of the policies "
           u"across relevant departments with particular attention to those "
           u"staff whose actions and decisions are most likely to increase or "
           u"decrease risks of adverse impacts (e.g., development teams, staff "
           u"involved in data gathering, data annotation and c ontent "
           u"moderation, system design, and/or service or product procurement, "
           u"systems designed to make decisions of consequence). It is important "
           u"that roles and responsibilities and lines of communication related "
           u"to risk management are documented and communicat ed to individuals "
           u"and teams throughout the enterprise."},
    {"cle": "1.2-10", "unite": "1.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Develop or adapt existing information and record-keeping systems to "
           u"collect information on AI risk management processes for adverse "
           u"impacts (e.g., processes for relevant teams to inventory AI "
           u"systems, and document and communicate risks of the AI systems they "
           u"design, develop, deploy, evaluate and use); such as to: units "
           u"within the enterprise – external to the team that developed or "
           u"deployed the AI system – regarding potential risks (e.g., "
           u"procurement, sales, compliance, export control, marketing, and "
           u"human resources). incorporate external and internal feedback on "
           u"risks into system design and implementation. and externally, the "
           u"risks presented by AI systems across all business relationships."},
    {"cle": "1.2-11", "unite": "1.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Establish channels of communication, or utilise existing channels "
           u"of communication, between relevant senior management and "
           u"implementing departments for sharing and documenting risk and risk "
           u"management decision-making."},
    {"cle": "1.2-12", "unite": "1.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Communicate the policies to the organisation’s relevant staff "
           u"(e.g., during staff orientation or training, during the design "
           u"review process, for customer relationship management staff, as a "
           u"standing item of board meetings, etc)."},
    {"cle": "1.2-13", "unite": "1.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Develop policies, procedures, and training to ensure that staff are "
           u"familiar with their duties related to risk management and the "
           u"organisation’s risk management practices."},
    {"cle": "1.2-14", "unite": "1.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Encourage alignment across teams and business units on relevant "
           u"aspects of the enterprise’s RBC policies for AI. This could be done "
           u"for example by creating cross -functional groups or committees to "
           u"share information and decision-making about risks, and including "
           u"business units that can impact adoption of the RBC policies for AI "
           u"in decision-making. 22  responsibilities related to the "
           u"implementation of AI due diligence. Consider appointing independent "
           u"external expertise to the committee as part of broader stakeholder "
           u"engagement efforts. policies for AI (e .g., including objectives or "
           u"metrics in employee evaluations linked to implementation of RBC "
           u"policies, such as energy consumption, conducting stakeholder "
           u"engagement activities, and adopting RBC policies; and rewards "
           u"-based challenges or hackathons linked to developing solutions to "
           u"RBC challenges)."},
    {"cle": "1.2-15", "unite": "1.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Review existing processes across IT, security, procurement, "
           u"software development lifecycle (SDLC), etc., to identify how these "
           u"will interoperate with policies and processes put in place in "
           u"relation to AI due diligence."},
    {"cle": "1.2-16", "unite": "1.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Promote broad decision-making related to AI risk management (e.g., "
           u"relevant staff or stakeholders are made up from a diversity of "
           u"disciplines, experience, expertise, and backgrounds)."},
    {"cle": "1.2-17", "unite": "1.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Develop incident monitoring and response systems."},
    {"cle": "1.2-18", "unite": "1.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Develop, draw from or adapt existing complaint or whistleblower "
           u"procedures for staff to raise issues or complaints related to RBC "
           u"issues, in compliance with domestic regulations."},
    {"cle": "1.2-19", "unite": "1.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Develop policies and practices to foster critical thinking mindset "
           u"in the design, development, deployment and use of AI systems."},
    {"cle": "1.2-20", "unite": "1.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Develop processes for upgrading, decommissioning and phasing out AI "
           u"systems safely and in a manner that does not increase risks, create "
           u"new risks or decrease the enterprise’s trustworthiness."},
    {"cle": "1.2-21", "unite": "1.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Develop contingency plans to handle failures, incidents or adverse "
           u"impacts linked to AI systems."},
    {"cle": "1.2-22", "unite": "1.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Develop a stakeholder engagement plan to allow stakeholders to "
           u"assess and monitor the implementation of relevant RBC processes "
           u"across the enterprise, ensuring regular participation of "
           u"stakeholders in RBC processes, including workers, workers’ "
           u"representatives and trade unions."},
    {"cle": "1.2-23", "unite": "1.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Establish or join collaborative initiatives to develop, advance, "
           u"and adopt, where appropriate, shared standards, tools, mechanisms, "
           u"and best practices for ensuring the safety, security, and "
           u"trustworthiness of advanced AI systems, such as the OECD Catalogue "
           u"of Tools for Trustworthy AI."},
    {"cle": "1.3-24", "unite": "1.3",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Communicate key aspects of the RBC policies for AI to relevant "
           u"business relationships, including suppliers of inputs, sales "
           u"partners and users of AI systems."},
    {"cle": "1.3-25", "unite": "1.3",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Where enterprises rely on sales partners – business relationships "
           u"who buy, distribute, integrate, and resell products and services to "
           u"end customers – develop channels of communication across the sales "
           u"channel and with relevant external stakeholders to ensure ongoing "
           u"due diligence."},
    {"cle": "1.3-26", "unite": "1.3",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Develop and implement pre -qualification processes for suppliers or "
           u"customers that takes into account due diligence on relevant RBC "
           u"issues, where feasible, adapting such processes to the specific "
           u"risk and context to focus on RBC issues that have been identi fied "
           u"as relevant for the business relationships and their activities or "
           u"area(s) of operation."},
    {"cle": "1.3-27", "unite": "1.3",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Where relevant, and particularly with regards to business "
           u"relationships with SMEs, consider providing adequate resources to "
           u"suppliers, customers, end-users and other business relationships "
           u"for them to understand and apply the relevant RBC policies and impl "
           u"ement due diligence (e.g.,  23 participating in targeted awareness "
           u"raising, training, or capacity building with relevant business "
           u"relationships and workers). Ideally and where appropriate, "
           u"resources and additional guidance provided to customers and end "
           u"users should be as specific and targeted as possible."},
    {"cle": "1.3-28", "unite": "1.3",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Seek to understand and address barriers arising from the "
           u"enterprise’s way of doing business that may impede the ability of "
           u"suppliers, users and other business relationships to implement RBC "
           u"polices, such as the enterprise’s purchasing practices when "
           u"acquiring algorithms, datasets, software or hardware."},
    {"cle": "2.1-29", "unite": "2.1",
     "groupes": ("intrants",),
     "en": u"Identify business relationships that are actively involved in the "
           u"development of AI systems (i.e., business relationships in Group "
           u"2)."},
    {"cle": "2.1-30", "unite": "2.1",
     "groupes": ("intrants",),
     "en": u"Develop an initial understanding of the types of AI systems being "
           u"developed by business relationships, including the risk information "
           u"related to AI systems described in Step 2.1."},
    {"cle": "2.1-31", "unite": "2.1",
     "groupes": ("cycle_vie",),
     "en": u"Develop an understanding of the enterprise’s role in the AI system "
           u"lifecycle and maintain an up-to- date registry of AI systems linked "
           u"to the enterprise."},
    {"cle": "2.1-32", "unite": "2.1",
     "groupes": ("cycle_vie",),
     "en": u"Develop an understanding of the risks of potential adverse impacts "
           u"related to the development and/or use of the AI system(s). This can "
           u"be done through desk research and consultation on which risks might "
           u"be associated with the AI system and gathering and reviewing "
           u"reporting on risks about the AI system or t he enterprise that "
           u"developed or modified the system. Internal sources of risk "
           u"information include incident monitoring mechanisms, oversight "
           u"bodies, and communication channels described in Step 1.2. Externa l "
           u"sources of risk information include reports from national human "
           u"rights institutions, national AI observatories, regulatory "
           u"agencies, sector-specific ministries, international and regional "
           u"human rights accountability mechanisms, civil society organisations "
           u"and workers, workers’ representatives, trade unions, public "
           u"incident data bases ,11 court cases, grievance mechanisms, and "
           u"engagement with affected and at -risk communities. The OECD "
           u"Framework for the Classification of AI Systems also provides a "
           u"foundation that can be built upon to understand risks related to AI "
           u"systems (see OECD Framework for the Classification of AI Systems "
           u"(OECD, 2022[13]))."},
    {"cle": "2.1-33", "unite": "2.1",
     "groupes": ("cycle_vie",),
     "en": u"Risk information can be related to: to cause harm can increase if "
           u"deployed in a manner that they can interact without guardrails in "
           u"place. recognition technology, predictive policing, surveillance "
           u"technology, marketing technology) companies, healthcare providers, "
           u"judiciary bodies, law enforcement, intelligence agencies, "
           u"individuals) system (e.g., labour risks during data annotation and "
           u"content moderation, sourcing private data or intellectual property "
           u"(IP)) with high levels of corruption, human rights and labour "
           u"rights abuses, and conflict zones) inadequately performing "
           u"important tasks)  25 accordance with its intended purpose, or "
           u"under conditions of reasonably foreseeable improper use or misuse, "
           u"which may give rise to adverse impacts (see Box 2.1) for indicators "
           u"of uses of AI systems that potentially pose higher risks of adverse "
           u"impacts)."},
    {"cle": "2.1-34", "unite": "2.1",
     "groupes": ("cycle_vie",),
     "en": u"Where it is not feasible or practical to conduct in-depth "
           u"assessments of all AI systems, consider an escalation system (e.g., "
           u"having a questionnaire for all new AI systems to assess the "
           u"baseline risk level and anything with indicators of high risk is "
           u"then escalated for further in-depth due diligence)."},
    {"cle": "2.1-35", "unite": "2.1",
     "groupes": ("cycle_vie",),
     "en": u"Review the findings of the scoping exercise on a regular basis and "
           u"when significant changes occur (e.g., operating in a new country, "
           u"development of a new AI system or product, restructuring, engaging "
           u"with new business relationships, when relevant laws undergo "
           u"significant changes)."},
    {"cle": "2.1-36", "unite": "2.1",
     "groupes": ("cycle_vie",),
     "en": u"Consider relevant laws, regulations, and standards in areas such as "
           u"consumer protection or sector specific laws, regulations and "
           u"standards (e.g., in healthcare, manufacturing, aviation, etc.) to "
           u"help enterprises understand risks and define high-risk uses of AI "
           u"systems."},
    {"cle": "2.1-37", "unite": "2.1",
     "groupes": ("utilisateur",),
     "en": u"Develop an initial understanding of all uses of AI systems within "
           u"the enterprise including the risk information related to AI systems "
           u"described in Step 2.1, paragraph 54(b), (e.g., human resources, "
           u"marketing, sales, customer service, procurement, due diligence, "
           u"etc.) and consider which uses call for deeper due diligence. In "
           u"cases of low risk, further in -depth due diligence activity may not "
           u"be warranted."},
    {"cle": "2.1-38", "unite": "2.1",
     "groupes": ("utilisateur",),
     "en": u"Identify business relationships that develop and deploy AI systems "
           u"used in operations, products and services."},
    {"cle": "2.2-39", "unite": "2.2",
     "groupes": ("cycle_vie",),
     "volet": u"identifying risks in own operations",
     "en": u"Catalogue the specific legal requirements and "
           u"national/international/industry standards applicable to the AI "
           u"system or AI actor being assessed, including relevant national and "
           u"international RBC and labour standards."},
    {"cle": "2.2-40", "unite": "2.2",
     "groupes": ("cycle_vie",),
     "volet": u"identifying risks in own operations",
     "en": u"Review TEVV information (Test and Evaluation, Verification and "
           u"Validation), including those related to experimental design, data "
           u"collection and selection (e.g., availability, accuracy, "
           u"representativeness, suitability), system trustworthiness, and "
           u"construct validation. Make efforts to ensure that tools or metrics "
           u"that are used to measure, test, or mitigate AI system risk are "
           u"themselves be tested, have proven, quantifiable utility and have "
           u"quality assurance testing across all measures."},
    {"cle": "2.2-41", "unite": "2.2",
     "groupes": ("cycle_vie",),
     "volet": u"identifying risks in own operations",
     "en": u"Where relevant to the risk, review evaluations of the AI system "
           u"involving human subjects."},
    {"cle": "2.2-42", "unite": "2.2",
     "groupes": ("cycle_vie",),
     "volet": u"identifying risks in own operations",
     "en": u"Review how system output is expected to be utilised and overseen by "
           u"humans."},
    {"cle": "2.2-43", "unite": "2.2",
     "groupes": ("cycle_vie",),
     "volet": u"identifying risks in own operations",
     "en": u"Consult domain experts, users, and enterprises external to the team "
           u"that developed or deployed the AI system."},
    {"cle": "2.2-44", "unite": "2.2",
     "groupes": ("cycle_vie",),
     "volet": u"identifying risks in own operations",
     "en": u"Consult and engage stakeholders, including workers, workers’ "
           u"representatives and trade unions, impacted and potentially impacted "
           u"communities, independent experts, and civil society groups to "
           u"gather information on significant risks, taking into account "
           u"potential barriers to effective stakeholder engagement. Where "
           u"directly consulting with stakeholders is not possible, consider "
           u"reasonable alternatives such as consulting independent expert "
           u"resources, including human rights defenders, trade unions and civil "
           u"society groups. may affect them. tests), with due regard for "
           u"business confidentiality and IP rights."},
    {"cle": "2.2-45", "unite": "2.2",
     "groupes": ("cycle_vie",),
     "volet": u"identifying risks in own operations",
     "en": u"Consider risks of adverse impacts at the pre-deployment stage and "
           u"development stage (e.g., model theft, and misuse from internal "
           u"use)."},
    {"cle": "2.2-46", "unite": "2.2",
     "groupes": ("cycle_vie",),
     "volet": u"identifying risks in own operations",
     "en": u"Identify risks to robustness and security of AI systems, for "
           u"example through mathematical guarantees or adversarial robustness "
           u"testing."},
    {"cle": "2.2-47", "unite": "2.2",
     "groupes": ("cycle_vie",),
     "volet": u"identifying risks in own operations",
     "en": u"Identify risks to privacy and data governance at the data and model "
           u"levels (see Box 2.3)."},
    {"cle": "2.2-48", "unite": "2.2",
     "groupes": ("cycle_vie",),
     "volet": u"identifying risks in own operations",
     "en": u"Identify risks of the AI system facilitating or advocating for "
           u"outcomes that result in adverse impacts on human rights and harms "
           u"to society and the public interest."},
    {"cle": "2.2-49", "unite": "2.2",
     "groupes": ("cycle_vie",),
     "volet": u"identifying risks related to business relationships using AI "
              u"systems",
     "en": u"Map the organisation’s relevant operations or business "
           u"relationships relevant to the prioritised risk."},
    {"cle": "2.2-50", "unite": "2.2",
     "groupes": ("cycle_vie",),
     "volet": u"identifying risks related to business relationships using AI "
              u"systems",
     "en": u"Review whether relevant high-risk business relationships have due "
           u"diligence policies and internal management systems in place (per "
           u"Step 1)."},
    {"cle": "2.2-51", "unite": "2.2",
     "groupes": ("cycle_vie",),
     "volet": u"identifying risks related to business relationships using AI "
              u"systems",
     "en": u"For assessments of business relationships, notably data enrichment "
           u"services, where available, use information from the organisation’s "
           u"own, or third parties’ impact assessments, legal reviews, "
           u"compliance management systems, financial audits, occupational, "
           u"health and safety inspections; worker’s organisation, trade union, "
           u"and/or ci vil society reporting; and any other relevant assessments "
           u"carried out by the organisation or by industry and multi "
           u"-stakeholder initiatives and “know your customer” (KYC) processes."},
    {"cle": "2.2-52", "unite": "2.2",
     "groupes": ("cycle_vie",),
     "volet": u"identifying risks related to business relationships using AI "
              u"systems",
     "en": u"Consider an escalation system to flag potentially high - risk sales "
           u"without unnecessarily encumbering low-risk sales. In some contexts, "
           u"this process might be related to or can be integrated with existing "
           u"compliance processes for export control and sanctions. This could "
           u"include: flagged sales • At the model level: The security of an AI "
           u"model can be assessed based on:"},
    {"cle": "2.2-53", "unite": "2.2",
     "groupes": ("cycle_vie",),
     "volet": u"identifying risks related to business relationships using AI "
              u"systems",
     "en": u"the access level a malicious actor might have, from “black box” "
           u"(e.g., no knowledge about the model) to “full transparency” (e.g., "
           u"full information about the model and its training data)"},
    {"cle": "2.2-54", "unite": "2.2",
     "groupes": ("cycle_vie",),
     "volet": u"identifying risks related to business relationships using AI "
              u"systems",
     "en": u"the phases in which an attack might happen (e.g., during training "
           u"or inference)"},
    {"cle": "2.2-55", "unite": "2.2",
     "groupes": ("cycle_vie",),
     "volet": u"identifying risks related to business relationships using AI "
              u"systems",
     "en": u"whether passive (e.g., “honest but curious”) or active (e.g., fully "
           u"malicious) attacks are likely given the threat profile"},
    {"cle": "2.2-56", "unite": "2.2",
     "groupes": ("cycle_vie",),
     "volet": u"identifying risks related to business relationships using AI "
              u"systems",
     "en": u"whether the model relies on cross -border transfers of data (e.g., "
           u"if the developer is a multinational enterprise and data is "
           u"collected from multiple jurisdictions, or if some of the "
           u"development of the model is outsourced to other entities). • At the "
           u"intersection of data and model levels: Risks include making "
           u"inferences about certain members of the training dataset through "
           u"its interactions with the model . Techniques to assess "
           u"vulnerability levels include statistical disclosure, model "
           u"inversion, inferring class representatives, and membership and "
           u"property inference. • At the human-AI interaction: Training, "
           u"checklists and verification processes could help identify risks "
           u"arising from the interaction between the human and the system "
           u"(e.g., unintentional actions – or lack of action – by developers or "
           u"users that compromise the privacy or data governance of an AI "
           u"system). The OECD Privacy Guidelines, adopted in 1980 and revised "
           u"in 2013 (OECD, 2015 [16]), are the cornerstone of the OECD’s work "
           u"on privacy and are recognised as the global minimum standard for "
           u"privacy and data protection . Additionally, the Implementation "
           u"Guidance for the OECD Privacy Guidelines: Chapter on Accountability "
           u"can assist stakeholders in better understanding and implementing "
           u"the accountability principle outlined in the Privacy Guidelines "
           u"through privacy management programmes. Such programs, with their "
           u"risk -based approach, offer organisations a valuable tool to "
           u"address evolving risks and challenges, such as those posed by "
           u"emerging technologies."},
    {"cle": "2.2-57", "unite": "2.2",
     "groupes": ("intrants", "utilisateur",),
     "en": u"When engaging with enterprises involved in Group 2 activities that "
           u"are flagged by due diligence processes as being high -risk, "
           u"enterprises should engage directly with business relationships to "
           u"better understand their due diligence efforts, and where "
           u"appropriate, encourage them to take further steps to address actual "
           u"and potential adverse impacts. Specific due diligence information "
           u"to gather from business relationships includes: responsible AI "
           u"(e.g., the Hiroshima Process Code of Conduct, the EU AI Pact, "
           u"relevant Codes of Conduct arising out of the EU AIA and/or DSA) "
           u"timelines and benchmarks for improvement and their outcomes (see "
           u"Step 3)"},
    {"cle": "2.2-58", "unite": "2.2",
     "groupes": ("intrants", "utilisateur",),
     "en": u"Where due diligence information is not available or if business "
           u"relationships do not provide sufficient detail to inform an "
           u"enterprise’s risk assessment, enterprises can refer to existing "
           u"assessments – such as assessments shared through a collaborative "
           u"ind ustry-led or multi - stakeholder initiatives, academic studies, "
           u"or AI safety ratings service providers, and NGO reports or other "
           u"market research services – while continuing to engage with the "
           u"business relationship to make the disclosures available."},
    {"cle": "3.1-59", "unite": "3.1",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Assign responsibility to relevant senior staff for ensuring that "
           u"activities that cause or contribute to adverse impacts cease, and "
           u"for preventing activities that may cause or contribute to adverse "
           u"impacts in the future. Depending on the context of the risk, this "
           u"might include staff from different business units who have the "
           u"means to take the necessary action to address risks (e.g., research "
           u"and product development, procurement, customer relationship "
           u"management, sales, or legal)."},
    {"cle": "3.1-60", "unite": "3.1",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"In the case of complex activities that may be difficult to cease "
           u"due to operational, contractual or legal issues (e.g., provision of "
           u"government services, long -term contracts, reliance on a business "
           u"relationship), create a roadmap for how to cease the activities "
           u"causing or contributing to adverse impacts. Enterprises may benefit "
           u"from publicly explaining the complexity of the situation and "
           u"efforts made to progressively stop activities over time."},
    {"cle": "3.1-61", "unite": "3.1",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Consult and engage with impacted and potentially impacted "
           u"stakeholders and their representatives to devise appropriate "
           u"actions and implement the plan (see Chapter 1, Meaningful "
           u"stakeholder engagement)."},
    {"cle": "3.1-62", "unite": "3.1",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Draw from the findings of the risk assessment to update and "
           u"strengthen management systems to better track information and flag "
           u"risks before adverse impacts occur."},
    {"cle": "3.1-63", "unite": "3.1",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Update the enterprise’s policies with active engagement of "
           u"stakeholders to provide guidance on how to avoid and address the "
           u"adverse impacts in the future and ensure their implementation."},
    {"cle": "3.1-64", "unite": "3.1",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"When deciding which mitigation action to take, consider weighing "
           u"this action against other possible risks that might occur as well "
           u"as the benefits of deploying or using the AI system, where relevant "
           u"."},
    {"cle": "3.1-65", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Conduct data quality reviews to identify and address issues such as "
           u"incorrect labels and representativeness."},
    {"cle": "3.1-66", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Implement privacy preserving and responsible data governance "
           u"approaches to collecting data and training AI systems such as data "
           u"cleaning, on -device processing, and federated learning. Monitor "
           u"pre-trained models used for development as part of regular AI "
           u"system monitoring and maintenance, including through data quality "
           u"reviews."},
    {"cle": "3.1-67", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"If the enterprise is not confident it can train a safe model at the "
           u"scale it initially had planned, they could consider incremental "
           u"scaling (i.e., training a smaller or otherwise weaker model)."},
    {"cle": "3.1-68", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Apply state -of-the-art alignment and safety techniques such as "
           u"inverse reinforcement learning (Centre for the Governance of AI, "
           u"2023[19])."},
    {"cle": "3.1-69", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Take steps to prevent or mitigate risks linked to data collection "
           u"and processing."},
    {"cle": "3.1-70", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Risks related to data quality and sourcing might also be linked to "
           u"data enrichment services. Transparency, explainability and "
           u"traceability"},
    {"cle": "3.1-71", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Seek to enable transparency , explainability and traceability, in "
           u"relation to sourcing data from subcontractors, datasets, processes, "
           u"relevant decisions made during system development , including on "
           u"human review of significant decisions as well as appeal processes "
           u"(see Box 2.8). 36 "},
    {"cle": "3.1-72", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Seek to enable ways to generate and provide interpretations and "
           u"explanations of an AI system’s output by including the below "
           u"information in model explanations, if relevant:"},
    {"cle": "3.1-73", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Enterprises should implement mechanisms to provide clear, "
           u"accessible, and meaningful explanations of automated decision "
           u"-making processes, especially when such decisions may significantly "
           u"affect individuals. These explanations should include the logic, "
           u"main parameters, and potential outcomes of the algorithmic process, "
           u"tailored to the average user’s understanding."},
    {"cle": "3.1-74", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Develop and deploy reliable content authentication and provenance "
           u"mechanisms, where technically feasible (see Box 2.9)."},
    {"cle": "3.1-75", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Consider contributing to the advancement and standardisation of AI "
           u"measurement science to fully understand the long-term benefits and "
           u"risks of AI systems."},
    {"cle": "3.1-76", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Consider developing a guide for external stakeholders that provides "
           u"resources to help stakeholders better understand the AI system. "
           u"This could take the form of responsible AI documentation, offering "
           u"stakeholders a single repository for information on intended use "
           u"cases and limitations, responsible AI design choices, and best "
           u"practices for deployment and performance optimisation. Such a guide "
           u"could address issues related to the OECD AI Principles . This would "
           u"be a constantly evolving document as the AI system and related "
           u"risks are better understood."},
    {"cle": "3.1-77", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Make the information in disclosures sufficiently clear and "
           u"understandable to enable deployers and users as appropriate and "
           u"relevant to interpret the model/system’s output and to enable users "
           u"to use it appropriately, and that disclosures should be supported "
           u"and informed by robust documentation processes. Security, safety "
           u"and robustness"},
    {"cle": "3.1-78", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Develop approaches to support robustness, security and safety "
           u"throughout the AI system lifecycle, for example: from users and "
           u"other relevant AI organisations, appeal and override, "
           u"decommissioning, incident response, recovery, and change "
           u"management. supersede, disengage, or deactivate AI systems that "
           u"demonstrate performance or outcomes inconsistent with intended use. "
           u"Responsible deployment"},
    {"cle": "3.1-79", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Engage with stakeholders for input on system requirements and "
           u"design decisions (e.g., “the system shall respect the privacy of "
           u"its users”) pre-deployment (see Box 2.10)."},
    {"cle": "3.1-80", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Consider measures to gradually deploy the AI system as evidence "
           u"about risks emerges. Research has identified a ‘gradient system of "
           u"access’ when deploying generative AI models, ranging from fully "
           u"closed and gradual/staged release at one end of the gradient to "
           u"downloadable and fully open at the other end (Solaiman, 2023 [26]). "
           u"Each level of access comes with risks and trade -offs that should "
           u"be taken into account when considering how to prevent and mitigate "
           u"risks linked to the AI system (see Box 2.11)."},
    {"cle": "3.1-81", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Consider monitoring and controlling model or system usage (e.g., by "
           u"collecting know -your- customer (KYC) information and restricting "
           u"access to the system or some capabilities of the system). This can "
           u"be done through a risk -based gating and escalation approa ch (see "
           u"(BSR, 2022[27])). 40 "},
    {"cle": "3.1-82", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Develop adequate assessments and monitoring measures internally and "
           u"support external researchers who have the resources and "
           u"understanding to support post-deployment assessment."},
    {"cle": "3.1-83", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Establish and integrate feedback processes for end users and "
           u"relevant stakeholders to report problems and appeal system "
           u"outcomes."},
    {"cle": "3.1-84", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Update and fine -tune the AI system post -deployment based on on "
           u"-going monitoring and post - deployment assessment. Methods for "
           u"fine -tuning include reinforcement learning with human feedback or "
           u"making adjustments to datasets."},
    {"cle": "3.1-85", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Where significant adverse impacts are imminent or severe harms are "
           u"actually occurring – it is important to cease development and "
           u"deployment of the AI system in a responsible manner until risks can "
           u"be sufficiently managed."},
    {"cle": "3.1-86", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Assess whether legal requirements on AI development and use may "
           u"cause impacts (see Box 2.12)."},
    {"cle": "3.1-87", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Examples of actions that could be used by enterprises to mitigate "
           u"risks of misuse of AI systems include the following: risk of misuse "
           u"is significant)"},
    {"cle": "3.1-88", "unite": "3.1",
     "groupes": ("cycle_vie",),
     "en": u"Take steps to ensure that business relationships deploying the "
           u"enterprise’s AI systems are also meaningfully engaging with "
           u"stakeholders before deployment, particularly in the workplace. See"},
    {"cle": "3.2-89", "unite": "3.2",
     "groupes": ("utilisateur",),
     "en": u"In the context of using AI systems for operational decision-making, "
           u"enterprise may need to engage with workers, workers’ "
           u"representatives and trade unions to mitigate risks. Engagement with "
           u"workers can include: the collection and analysis of data that "
           u"concerns them"},
    {"cle": "3.2-90", "unite": "3.2",
     "groupes": ("utilisateur",),
     "en": u"When using AI systems in products and services, enterprises could "
           u"conduct independent tests where technically feasible (e.g., red "
           u"teaming or other types of testing exercises) to verify the quality "
           u"of the output s and test vulnerabilities. Enterprises should also "
           u"consider disclosing when outputs are generated or informed by AI "
           u"systems and to what extent (see Box 2.8)."},
    {"cle": "3.2-91", "unite": "3.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Assign responsibility for developing, implementing and monitoring "
           u"plans to prevent or mitigate actual or potential adverse impacts "
           u"directly linked to the enterprise by business relationships ."},
    {"cle": "3.2-92", "unite": "3.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Support or collaborate with the relevant business relationship(s) "
           u"in developing fit-for-purpose plans for them to prevent or mitigate "
           u"adverse impacts identified within reasonable and clearly defined 42 "
           u" timelines, using qualitative and quantitative indicators for "
           u"defining and measuring improvement (sometimes referred to as "
           u"“corrective action plans”)."},
    {"cle": "3.2-93", "unite": "3.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Use leverage, to the extent possible and in line with competition "
           u"law obligations , to prompt the business relationship(s) to prevent "
           u"or mitigate adverse impacts or risks. Once a product or service has "
           u"been sold or re -sold, consider ways to exercise leverage through "
           u"restricting the provision of essential services that the AI system "
           u"relies on to run (e.g., customer support, updates, running servers, "
           u"etc.). Using leverage may include: through direct communications "
           u"with staff responsible for addressing risks at the operational, "
           u"senior management and/or board level to express views on RBC issues "
           u"– with performance on RBC wrongful practices of the entity causing "
           u"the harm RBC are not respected."},
    {"cle": "3.2-94", "unite": "3.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"If the enterprise does not have sufficient leverage to encourage a "
           u"business relationship to prevent or mitigate an adverse impact , "
           u"consider ways to build additional leverage with the business "
           u"relationship in line with competition law , including for example "
           u"through outreach from senior management and through support and "
           u"incentives as relevant."},
    {"cle": "3.2-95", "unite": "3.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"To the extent possible, in line with competition law , cooperate "
           u"with other enterprises or stakeholders to build and exert leverage "
           u"to encourage the prevention and mitigation of adverse impacts, for "
           u"example through collaborative approaches in industry associations, "
           u"or through engagement with governments."},
    {"cle": "3.2-96", "unite": "3.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"To prevent potential (future) adverse impacts and address actual "
           u"impacts, seek to build leverage into new and existing business "
           u"relationships (e.g., through policies or codes of conduct, "
           u"contracts, or written agreements) (see Box 2.14).  43"},
    {"cle": "3.2-97", "unite": "3.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Include conditions and expectations on RBC issues in supplier, "
           u"sales partner and/or user contracts or other forms of written "
           u"agreements (e.g., the development of “responsible use guides” or "
           u"“acceptable use policies” for users)."},
    {"cle": "3.2-98", "unite": "3.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Encourage business relationships causing or contributing to adverse "
           u"impacts to consult and engage with impacted or potentially impacted "
           u"stakeholders or their representatives in developing and "
           u"implementing corrective action plans."},
    {"cle": "3.2-99", "unite": "3.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Support relevant business relationships in the prevention or "
           u"mitigation of adverse impacts or risks (e.g., through training or "
           u"strengthening of their management systems, striving for continuous "
           u"improvement through measurable, time-bound targets)."},
    {"cle": "3.2-100", "unite": "3.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Encourage relevant authorities in the country where the adverse "
           u"impact is occurring to act, (e.g., through inspections, enforcement "
           u"and application of existing laws and regulations )."},
    {"cle": "3.2-101", "unite": "3.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Engage with other enterprises and stakeholders to cease adverse "
           u"impacts and/or prevent them from recurring or to prevent risks from "
           u"materialising (e.g., through participating in industry initiatives "
           u"and engagement with governments)."},
    {"cle": "3.2-102", "unite": "3.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Where a business relationship’s due diligence information is not "
           u"publicly available, seek to engage with business relationships to "
           u"increase transparency or to demonstrate due diligence through "
           u"confidential bilateral or multilateral arrangements (e.g., "
           u"disclosure to trusted industry or multi - stakeholder initiatives "
           u"or non-disclosure agreements)."},
    {"cle": "3.2-103", "unite": "3.2",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"As a last resort, consider disengaging from the business "
           u"relationship (see Box 2.15). 44 "},
    {"cle": "4-104", "unite": "4",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Identify adverse impacts or risks that may have been overlooked in "
           u"past due diligence processes and include these in the future."},
    {"cle": "4-105", "unite": "4",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Assess whether previously undetected risks exist or previously "
           u"assessed risks are no longer acceptable."},
    {"cle": "4-106", "unite": "4",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Assess effectiveness of stakeholder engagement efforts (e.g., "
           u"looking at whether engagement is timely, accessible, and "
           u"appropriate and safe for stakeholders)."},
    {"cle": "4-107", "unite": "4",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Include feedback of lessons learned into the enterprise’s due "
           u"diligence in order to improve the process and outcomes in the "
           u"future."},
    {"cle": "4-108", "unite": "4",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Monitor and track AI system performance or assurance criteria "
           u"qualitatively or quantitatively for conditions similar to "
           u"deployment setting(s), for example, by: Verification and Validation "
           u"(TEVV). consultations with relevant AI actors and other "
           u"stakeholders , including affected communities, and field data about "
           u"context relevant risks and trustworthiness characteristics . "
           u"communities, governments, workers, workers’ representatives and "
           u"trade unions , civil society, and academia . This should be done "
           u"with a view to advancing safety, security and trustworthiness of "
           u"advanced AI systems.  47 deployment context(s) and across the AI "
           u"system lifecycle with domain experts and relevant AI actors and "
           u"stakeholders to validate whether the system is performing "
           u"consistently as intended."},
    {"cle": "4-109", "unite": "4",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Monitor and track implementation and effectiveness of the "
           u"organisation’s own internal commitments, activities and goals on "
           u"due diligence (e.g., by carrying out periodic internal or third - "
           u"party reviews or audits of the outcomes achieved and communicating "
           u"results at relevant levels within the organisation)."},
    {"cle": "4-110", "unite": "4",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Carry out periodic assessments of business relationships, to verify "
           u"that risk mitigation measures are being pursued or to validate that "
           u"adverse impacts have actually been prevented or mitigated."},
    {"cle": "5-111", "unite": "5",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Publicly communicate all relevant information on due diligence "
           u"processes, with due regard for commercial confidentiality, "
           u"competition law, and other competitive or security concerns .12 "
           u"Include information on the following: 48  relevant voluntary "
           u"initiatives. impacts or other notable risks that the enterprise "
           u"causes or contributes to, communicate with impacted or potentially "
           u"impacted stakeholders in a timely, culturally sensitive and "
           u"accessible manner, all information that is relevant to them, in "
           u"particular when relevant concerns are raised by them or on their "
           u"behalf. timelines and benchmarks for improvement and their outcomes "
           u", such as details of the evaluations (including red-teaming) "
           u"conducted for risks of adverse impacts diligence processes "
           u"circumvent safeguards, in particular incidents related to general- "
           u"purpose AI systems."},
    {"cle": "5-112", "unite": "5",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Disclose the above information in a way that is user friendly, "
           u"regular, timely, reliable, clear, complete, accurate and with "
           u"sufficient detail (see MNE Guidelines Chapter III: Disclosure for "
           u"more detail)."},
    {"cle": "5-113", "unite": "5",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"Ensure information is presented appropriately for different target "
           u"audiences and may take special steps to make information available "
           u"to vulnerable stakeholders (e.g., workers)."},
    {"cle": "6-114", "unite": "6",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"When appropriate (i.e., in instances where the adverse impact is "
           u"caused or contributed to by the enterprise), provide for or "
           u"cooperate with legitimate remediation mechanisms through which "
           u"impacted stakeholders can raise complaints and seek to have them "
           u"addressed with the enterprise (see Box 2.17)."},
    {"cle": "6-115", "unite": "6",
     "groupes": ("intrants", "cycle_vie", "utilisateur",),
     "en": u"For adverse impacts directly linked to business relationships, "
           u"enterprises are expected to apply leverage on the business "
           u"relationship, in line with competition law, to provide for or "
           u"cooperate with remediation mechanisms."},
)

#: LES SIX FEUILLES DE ROUTE, telles que le document les donne : une par
#: etape, chacune nommant les dispositions voisines d'autres cadres. Les
#: references a ISO, a l'IEEE et a AI Verify sont du MATERIEL DE TIERS,
#: que la licence CC BY de l'OCDE ne couvre pas : elles sont citees par
#: NUMERO ET INTITULE, comme un index, et rien de plus.
FEUILLES = {
    1: (
        ("asean",
         u"Section C.1: 1. Internal governance structures and measures and "
         u"Annex A: 2 Internal governance structures and measures"),
        ("australie",
         u"Implementation Practice 1, 2, and 4"),
        ("canada",
         u"Accountability"),
        ("coe",
         u"HUDERIA Workflow"),
        ("ia_act",
         u"Art. 9.1-3: Risk Management System, Art. 17.1 Quality "
         u"Management System"),
        ("dsa",
         u"Art. 14: Terms and Conditions and Art. 45: Code of Conduct"),
        ("csddd",
         u"Art. 7: Integrate due diligence into policies and risk "
         u"management systems"),
        ("hiroshima",
         u"Principle 4 (paragraph 2) and Principle 5 (paragraphs 1,3, and "
         u"4) and Principle 7"),
        ("ieee7000",
         u"6: Key roles; 7: Concept of Operations (ConOps) and Context "
         u"Exploration Process"),
        ("iso23894",
         u"5.1: General; 5.2: Leadership and Commitment; 5.3: Integration; "
         u"5.4: Design"),
        ("iso38507",
         u"4: Governance implications of the organizational use of AI "
         u"(includes governance and accountability considerations); 6: "
         u"Policies to address use of AI (includes oversight, decision- "
         u"making, data use, compliance, and culture and values)."),
        ("iso42001",
         u"Broadly covered in: 4: Context; 5: Leadership; 6: Planning; 7: "
         u"Support; 8: Operation; 9: Performance evaluation; 10: "
         u"Improvement. Implement organizational and technical measures as "
         u"necessary to address identified risks. Covered in detail in "
         u"Annex: A.2 (AI policies) and sub-controls A.2.2–A.2.4 and Annex "
         u"A.5.2 (AI impact assessment) for risk management"),
        ("japon",
         u"Part 2 E. Building AI governance, Part 3, 4, 5; Appendix 2. "
         u"“Section 2. E. Building AI Governance”, and Appendix 3, 4, 5."),
        ("coree",
         u"Art. 34"),
        ("singapour",
         u"1.1.1 – 9.6.3"),
        ("uk",
         u"3.2: AI assurance and governance; 6.1: Steps to build AI "
         u"assurance"),
        ("ungp",
         u"Operational Principles 15 and 16: Policy Commitment"),
        ("nist",
         u"Govern"),
    ),
    2: (
        ("asean",
         u"Section C.2: Determining the level of human involvement in AI- "
         u"augmented decision-making; C.3. Operations Management; and "
         u"Annex A: 3: Determining the level of human involvement in AI- "
         u"augmented decision-making"),
        ("australie",
         u"Implementation Practice 2 and 3.2"),
        ("canada",
         u"Safety Measure 1"),
        ("coe",
         u"Context-based risk analysis (COBRA), Impact Assessment (IA)"),
        ("ia_act",
         u"Art. 9(2): Identify, analyse and evaluate known and foreseeable "
         u"risks, Art. 55(1): Obligations for general purpose AI models "
         u"with systemic risk"),
        ("dsa",
         u"Art. 34: Risk assessment"),
        ("csddd",
         u"Arts. 8 and 9: Identify and assess actual or potential adverse "
         u"impacts, and, where necessary, prioritise potential and actual "
         u"adverse impacts"),
        ("hiroshima",
         u"Principles 1, 2, 6 and 7"),
        ("ieee7000",
         u"8. Ethical Values Elicitation and Prioritization Process; 9. "
         u"Ethical Requirements Definition Process"),
        ("iso31000",
         u"6.3: Scope, context, criteria – 6.4: Risk Assessment"),
        ("iso42001",
         u"6: Planning (6.1.1, 6.1.2, 6.1.4); 8: Operation (8.2, 8.4); "
         u"Annex A.5 (Assessing AI system impacts); sub-controls "
         u"A.5.2–A.5.5"),
        ("iso42005",
         u"5.8 Actual and potential impacts"),
        ("japon",
         u"Appendix 1.B. AI’s benefits and risks; Appendix 2.A. Building "
         u"of AI governance and monitoring by management"),
        ("coree",
         u"Arts. 32, 33, and 35"),
        ("singapour",
         u"Safety 4.1.1 – 4.3.1"),
        ("uk",
         u"4.1.1: Measure; 4.1.2: Evaluate, 5.4: Risk Assessment, .5; "
         u"Impact assessment; 5.6: Bias audit"),
        ("ungp",
         u"Operational Principles 17, 18"),
        ("nist",
         u"Govern 1, 4, Map 1-5"),
    ),
    3: (
        ("asean",
         u"Section C.2: Determining the level of human involvement in AI- "
         u"augmented decision-making; C.3. Operations Management; and "
         u"Annex A: 3: Determining the level of human involvement in AI- "
         u"augmented decision-making"),
        ("australie",
         u"Implementation Practices 1, 2, 3, 4, 5"),
        ("canada",
         u"Safety Measures 2 & 3; Fairness and Equity; Transparency; Human "
         u"Oversight and Monitoring; Validity and Robustness"),
        ("coe",
         u"Impact Mitigation Plan (IMP) and Access to Remedies"),
        ("ia_act",
         u"Recital 115, Art. 9(2a), Art. 9(2)(d), Art. 9(4)-(5), Art. 50 "
         u"(transparency obligations), Art. 55(1)(b)"),
        ("dsa",
         u"Art. 35: Mitigation of risks"),
        ("csddd",
         u"Arts. 10 and 11: Prevent and (where not possible or immediately "
         u"possible) mitigate potential adverse impacts; and bring actual "
         u"adverse impacts to an end and minimise their extent"),
        ("hiroshima",
         u"Principles 1, 2, 6-7, and 11"),
        ("ieee7000",
         u"10. Ethical Risk-Based Design Process"),
        ("iso31000",
         u"6.5: Risk treatment"),
        ("iso42001",
         u"6.1.3 AI risk treatment; 8.3 AI risk treatment; Annex A A.5 and "
         u"sub-controls A.5.2–A.5.5 for risk management; A.7 (Data for AI "
         u"systems) and sub-controls A.7.2–A.7.6 to cover data quality and "
         u"management"),
        ("japon",
         u"Part 2C. Common Guiding Principles, Part 3, 4, 5; Appendix 3, "
         u"4, 5."),
        ("coree",
         u"Arts. 31, 32, and 34"),
        ("singapour",
         u"Testing Framework Safety 4.1.1 – 4.6.1 Security 5.1.1 – 5.7.1 "
         u"Robustness 6.1.1 – 6.5.3"),
        ("ungp",
         u"Operational Principle 19"),
        ("uk",
         u"4.2: AI assurance mechanisms; 5.2: AI assurance spectrum; 5.3: "
         u"Assuring data, models, systems, and governance in practice; "
         u"6.1: Steps to build AI assurance"),
        ("nist",
         u"Map 1, Manage 1-4"),
    ),
    4: (
        ("asean",
         u"Section C.3 and Annex A:3"),
        ("australie",
         u"Implementation Practices 1, 2, 3, 4, 5"),
        ("canada",
         u"Human Oversight and Monitoring"),
        ("coe",
         u"Iterative requirements"),
        ("ia_act",
         u"Recital 114, Art. 9(5)-(8): Testing, Art. 55(1)(c): Incident "
         u"reporting for general purpose AI models, Art. 60: Testing of "
         u"High-Risk AI Systems in Real World Conditions Outside AI "
         u"Regulatory Sandboxes, Art. 72: Post market monitoring"),
        ("dsa",
         u"Art. 37: Independent audit"),
        ("csddd",
         u"Art. 14: Establish and maintain a notification mechanism and "
         u"complaints procedure: Art. 15: Monitor the effectiveness of due "
         u"diligence policy and measures Principles 4"),
        ("iso31000",
         u"6.6: Monitor and review"),
        ("iso42001",
         u"8.1: Operational planning and control; 9: Performance "
         u"evaluation; 10: Improvement ; Annex A.6.2.6 and A.6.2.8 "
         u"(monitoring and logging); Annex A.8.4 (incident communication)"),
        ("coree",
         u"Arts. 32 and 34"),
        ("singapour",
         u"Safety 4.1.1 – 4.6.1; Security 5.1.1 – 5.7.1; Robustness 6.1.1 "
         u"– 6.5.3"),
        ("ungp",
         u"Operational Principle 20"),
        ("uk",
         u"5.7: Compliance audit; 6.1.3: Review internal governance and "
         u"risk management"),
        ("nist",
         u"Measure 1, 4"),
    ),
    5: (
        ("asean",
         u"Section C.4. Stakeholder interaction and communication and "
         u"Annex A:5"),
        ("australie",
         u"Implementation Practices 1, 2, 3, 4"),
        ("canada",
         u"Transparency"),
        ("coe",
         u"Stakeholder Engagement Process (SEP)"),
        ("ia_act",
         u"Art. 13: Transparency and provision of information to "
         u"deployers, Art. 53(1)(a) and (d), Art. 55(1)(c)"),
        ("dsa",
         u"Art. 42: Transparency reporting obligations"),
        ("csddd",
         u"Art. 16: Publicly communicate on due diligence"),
        ("hiroshima",
         u"Principles 4 and 5"),
        ("ieee7000",
         u"11: Transparency management process"),
        ("iso31000",
         u"6.7: Recording and reporting"),
        ("iso42001",
         u"7.4 Communication; Annex A.6.2.7, A.8.2, A.8.4, A.8.5."),
        ("japon",
         u"Part 2C. Common Guiding Principles 6, 7; Appendix 3, 4, 5, B. "
         u"Descriptions of “Common guiding principles” in Part 2. 6, 7"),
        ("coree",
         u"Arts. 28 and 31"),
        ("singapour",
         u"Transparency 1.1.1 – 1.5.1"),
        ("ungp",
         u"Operational Principle 21"),
        ("uk",
         u"4.1.3: Communicate"),
        ("nist",
         u"Manage 4"),
    ),
    6: (
        ("asean",
         u"Section C.4: 4. Stakeholder interaction and communication"),
        ("australie",
         u"Implementation Practices 1 and 2"),
        ("dsa",
         u"Art. 14: Terms and conditions"),
        ("csddd",
         u"Art. 12: Provide remediation for actual adverse impacts"),
        ("singapour",
         u"Transparency 1.4.1 – 1.5.1"),
        ("ungp",
         u"Operational Principles 22, 29, 30, 31"),
        ("uk",
         u"5.3: Assuring data, models, systems, and governance in practice "
         u" 49"),
    ),
}


#: CE QUE L'EXTRACTION DU PDF A LAISSÉ DE TRAVERS, DÉCLARÉ PLUTÔT QUE TU.
#: Le bloc ci-dessus est extrait du document, pas recopié à la main — et une
#: extraction a ses coutures. Deux ont été mesurées et traitées, une subsiste.
#:
#: TRAITÉE : seize exemples sur cent quinze avaient avalé l'encadré, le
#: tableau ou la ligne de source qui les suivait dans la page — l'un faisait
#: 5 881 caractères contre 215 de médiane. L'extracteur coupe désormais l'item
#: à l'encadré, et le maximum est retombé à 1 537.
#:
#: SUBSISTE : quatre items du §2.2 sont les éléments d'une liste IMBRIQUÉE que
#: le document numérote comme une liste de premier rang. Ils se lisent donc en
#: minuscule, comme la suite d'une phrase qui n'est pas là. Les fusionner
#: produirait un exemple de quatre mille caractères ; les réécrire inventerait
#: une phrase que le document ne porte pas. Ils sont nommés ici, et l'écran
#: peut le dire.
COUTURES_DE_L_EXTRACTION = (
    {"cle": "liste_imbriquee",
     "quoi": "Quatre exemples du §2.2 commencent en minuscule.",
     "pourquoi": "Ce sont les éléments d'une liste imbriquée que le document "
                 "numérote comme une liste de premier rang : chacun est un "
                 "facteur à considérer, et la phrase qui les introduit est "
                 "dans l'exemple précédent.",
     "fait": "Ils sont conservés tels quels. Les fusionner produirait un "
             "exemple de quatre mille caractères ; les réécrire inventerait "
             "une phrase que le document ne porte pas.",
     "exemples": ("2.2-53", "2.2-54", "2.2-55", "2.2-56")},
)


# ═══════════════════════════════════════════════════════════════════════════
#  8. CE QUE LE CLIENT DÉCLARE
# ═══════════════════════════════════════════════════════════════════════════

ETATS = {
    "tenu": {"nom": "Tenu", "valeur": 1.0,
             "dit": "En place, appliqué, et montrable sur pièce."},
    "partiel": {"nom": "Partiellement tenu", "valeur": 0.5,
                "dit": "Commencé, pas achevé."},
    "absent": {"nom": "Absent", "valeur": 0.0, "dit": "Rien en place."},
    "sans_objet": {"nom": "Sans objet", "valeur": None,
                   "dit": "L'exemple ne s'applique pas à votre organisme — "
                          "et il faut pouvoir dire pourquoi. Les exemples "
                          "qu'aucun de vos groupes ne vise sortent déjà du "
                          "calcul sans que vous ayez à le dire."},
}

ORDRE_ETATS = ("absent", "partiel", "tenu", "sans_objet")

#: CE QUE LE TAUX S'APPELLE. Il ne s'appelle PAS « conformité », et la garde
#: du module refuse qu'on le renomme : le document déclare ses exemples non
#: exhaustifs, et un taux de conformité sur une liste incomplète serait un
#: mensonge par arrondi.
NOM_DU_TAUX = "Couverture des exemples retenus"

CE_QUE_LE_TAUX_N_EST_PAS = (
    "Ce taux dit la part des exemples pratiques retenus par vos groupes que "
    "vous déclarez tenus. Ce n'est PAS un taux de conformité : le document "
    "écrit lui-même que ses exemples ne constituent pas une liste de "
    "contrôle exhaustive, et aucun organisme ne délivre d'attestation contre "
    "ce guide. Un organisme peut avoir tenu les 115 exemples et rester en "
    "défaut de diligence sur un risque qu'aucun d'eux ne nomme."
)


# ═══════════════════════════════════════════════════════════════════════════
#  9. LA QUALIFICATION — LES GROUPES, PUIS L'IMPLICATION
# ═══════════════════════════════════════════════════════════════════════════

def groupes_declares(declaration=None):
    """Les clés de groupe que la déclaration porte, dans l'ordre du document.

    PLUSIEURS GROUPES SONT NORMAUX, et c'est le document qui l'impose : ils
    « are not rigid nor exclusive ». Une clé inconnue est ignorée plutôt que
    de faire tomber le calcul — l'écran, lui, ne propose que les trois.
    """
    d = declaration if isinstance(declaration, dict) else {}
    q = d.get("qualification") if isinstance(d.get("qualification"), dict) \
        else {}
    brut = q.get("groupes")
    if isinstance(brut, str):
        brut = [brut]
    if not isinstance(brut, (list, tuple, set)):
        brut = ()
    return tuple(g["cle"] for g in GROUPES if g["cle"] in set(brut))


def implication_declaree(declaration=None):
    """La clé d'implication déclarée, ou None."""
    d = declaration if isinstance(declaration, dict) else {}
    q = d.get("qualification") if isinstance(d.get("qualification"), dict) \
        else {}
    c = q.get("implication")
    return c if c in IMPLICATIONS_PAR_CLE else None


def applicable(declaration=None):
    """Ce que la qualification permet de mesurer.

    TROIS SORTIES, ET PAS DEUX : « ok » quand les groupes sont déclarés,
    None quand ils ne le sont pas — et jamais False. Ce guide ne met
    personne hors champ : toute entreprise de la chaîne de valeur de l'IA
    est attendue sur la diligence, les PME comprises. Les autres modules de
    Sentinel ont un hors-champ ; celui-ci n'en a pas, et le dire est une
    information.
    """
    g = groupes_declares(declaration)
    if not g:
        return {"ok": None, "groupes": (), "implication": None,
                "dit": "Aucun groupe d'acteur n'est déclaré. Le "
                       "questionnaire ne sait pas lesquels des 115 exemples "
                       "vous visent, et le module ne rend aucun chiffre : "
                       "un taux calculé sur des exemples adressés à "
                       "quelqu'un d'autre ne voudrait rien dire."}
    noms = ", ".join(GROUPES_PAR_CLE[c]["nom"] for c in g)
    return {"ok": True, "groupes": g,
            "implication": implication_declaree(declaration),
            "dit": "Groupe(s) déclaré(s) : %s. Aucune entreprise de la "
                   "chaîne de valeur de l'IA n'est hors du champ de ce "
                   "guide : il n'a pas de seuil d'effectif ni de liste "
                   "sectorielle." % noms}


def exemples_retenus(groupes):
    """Les exemples que ces groupes retiennent, et ceux qu'ils écartent.

    UN EXEMPLE QU'AUCUN GROUPE DÉCLARÉ NE VISE SORT DU CALCUL. Il ne compte
    pas zéro : le document l'adresse à quelqu'un d'autre, et le compter
    contre ce client reviendrait à lui reprocher de ne pas être un
    fournisseur de calcul.
    """
    g = set(groupes)
    retenus = [e for e in EXEMPLES if g & set(e["groupes"])]
    ecartes = [e for e in EXEMPLES if not (g & set(e["groupes"]))]
    return retenus, ecartes


# ═══════════════════════════════════════════════════════════════════════════
#  10. LA PRIORISATION, CALCULÉE — ET LA JUSTIFICATION QUI LA REND CRÉDIBLE
# ═══════════════════════════════════════════════════════════════════════════

#: Ce qu'une priorisation sans justification écrite laisse revendiquer de la
#: part « identifier ». LA MOITIÉ, et pas zéro : les risques sont bien
#: identifiés et cotés, c'est le CARACTÈRE CRÉDIBLE du processus qui manque.
PLAFOND_PRIORISATION_SANS_JUSTIFICATION = 0.5

#: Ce qu'une déclaration SANS IMPLICATION laisse revendiquer, toutes étapes
#: confondues. LA MOITIÉ : le questionnaire peut être rempli entièrement et
#: sincèrement, mais l'encadré 2.4 fait dépendre le niveau de diligence
#: attendu d'une question à laquelle personne n'a répondu.
PLAFOND_SANS_IMPLICATION = 0.5


def _niveau(v):
    n = NIVEAUX.get(v)
    return n["valeur"] if n else None


def _palier(saillance):
    choisi = PALIERS_SAILLANCE[0]
    for p in PALIERS_SAILLANCE:
        if saillance >= p["min"]:
            choisi = p
    return choisi


def priorisation(declaration=None):
    """Les risques cotés, leur gravité, leur saillance, et ce qui manque.

    CE QUE CETTE FONCTION REFUSE DE FAIRE : rendre une saillance pour une
    ligne dont un facteur n'est pas coté. Trois facteurs sur quatre ne font
    pas une priorisation : ils font une opinion partiellement chiffrée, et
    l'afficher comme un classement tromperait sur ce qui a été fait.
    """
    d = declaration if isinstance(declaration, dict) else {}
    brut = d.get("priorisation")
    if not isinstance(brut, (list, tuple)):
        brut = ()

    lignes, sans_justification, incompletes = [], [], []
    for i, r in enumerate(brut):
        if not isinstance(r, dict):
            continue
        cle = str(r.get("cle") or ("risque-%d" % (i + 1)))
        nom = (r.get("nom") or "").strip()
        notes = {}
        for f in FACTEURS:
            notes[f["cle"]] = _niveau(r.get(f["cle"]))
        manquants = [c for c, v in notes.items() if v is None]
        just = (r.get("justification") or "").strip()
        ligne = {"cle": cle, "nom": nom, "notes": notes,
                 "facteurs_manquants": sorted(manquants),
                 "justification": bool(just)}
        if manquants:
            ligne.update(gravite=None, saillance=None, palier=None)
            incompletes.append(cle)
        else:
            gravite = max(notes[c] for c in FACTEURS_DE_GRAVITE)
            saillance = gravite * notes["probabilite"]
            ligne.update(gravite=gravite, saillance=saillance,
                         palier=_palier(saillance)["cle"])
            #  UNE LIGNE COTÉE SANS JUSTIFICATION ÉCRITE : c'est elle qui
            #  plafonne. Une ligne INCOMPLÈTE ne plafonne pas — elle n'est
            #  pas encore une priorisation, elle est en cours.
            if not just:
                sans_justification.append(cle)
        lignes.append(ligne)

    cotees = [l for l in lignes if l["saillance"] is not None]
    saillants = [l["cle"] for l in cotees if l["palier"] == "saillant"]
    return {
        "lignes": lignes,
        "cotees": len(cotees),
        "incompletes": sorted(incompletes),
        "sans_justification": sorted(sans_justification),
        "saillants": saillants,
        #  CRÉDIBLE : au moins une ligne entièrement cotée, et aucune cotée
        #  sans sa justification. Le document ne demande pas un nombre de
        #  lignes ; il demande que le processus se démontre.
        "credible": bool(cotees) and not sans_justification,
        "renseignee": bool(lignes),
    }


# ═══════════════════════════════════════════════════════════════════════════
#  11. LE SCORE — ET LE PLAFOND QUE L'IMPLICATION IMPOSE
# ═══════════════════════════════════════════════════════════════════════════

def _valeur(etat):
    e = ETATS.get(etat)
    return e["valeur"] if e else None


def score(declaration=None):
    """La couverture par étape, le brut, le plafond, et le taux qui en sort.

    TROIS NOMBRES, ET LES TROIS SONT NÉCESSAIRES — c'est la doctrine du reste
    du site : `brut` dit ce que vaut le travail déclaré, `plafond` ce que la
    qualification laisse revendiquer, `taux` le plus petit des deux.

    LE PLAFOND NE VIENT PAS D'UNE CASE. Il se calcule sur l'implication
    déclarée : le taux global ne peut pas dépasser celui de l'étape que cette
    implication rend NON NÉGOCIABLE. C'est l'encadré 2.4 du document, pas une
    règle du cabinet — « enterprises causing adverse impacts are expected to
    cease or prevent potential impacts and remediate harm caused ».
    """
    d = declaration if isinstance(declaration, dict) else {}
    rep = d.get("reponses") if isinstance(d.get("reponses"), dict) else {}
    groupes = groupes_declares(d)
    retenus, ecartes = exemples_retenus(groupes)
    retenus_par_cle = {e["cle"] for e in retenus}

    etapes, poids_total, acquis_total = [], 0, 0.0
    for et in ETAPES:
        exs = [e for e in retenus
               if UNITES_PAR_CLE[e["unite"]]["etape"] == et["num"]]
        portes, acquis, sans_reponse = 0, 0.0, []
        for e in exs:
            if rep.get(e["cle"]) == "sans_objet":
                continue
            v = _valeur(rep.get(e["cle"]))
            if v is None:
                sans_reponse.append(e["cle"])
            #  UN EXEMPLE SANS RÉPONSE COMPTE POUR ZÉRO, ET PAS POUR RIEN.
            #  Le sortir du dénominateur ferait monter le taux à mesure
            #  qu'on répond MOINS.
            portes += 1
            acquis += v or 0.0
        t = (None if not portes else int(round(100.0 * acquis / portes)))
        etapes.append(dict(et, exemples=len(exs), portes=portes,
                           sans_reponse=len(sans_reponse), taux=t))
        poids_total += et["poids"]
        acquis_total += et["poids"] * (0.0 if t is None else t / 100.0)

    brut = int(round(100.0 * acquis_total / poids_total)) if poids_total else 0
    par_cle = {e["cle"]: e for e in etapes}

    # ── LES VERROUS, ET AUCUN NE VIENT D'UNE CASE ───────────────────────
    #
    # TOUT PLAFOND S'ÉCRIT SUR LES PARTS, JAMAIS SUR LE SEUL TOTAL. C'est la
    # leçon de `conformite` : ce fichier-là RECOMPOSE le taux d'une norme à
    # partir des parts que le moteur lui rend. Un plafond posé sur le total
    # seul ne lui parviendrait pas, et l'indice afficherait un chiffre plus
    # haut que cet écran — deux vérités sur le même nombre, et le client
    # entre les deux.
    verrous = []
    pr = priorisation(d)
    impl = implication_declaree(d)
    plafonds = {}       # clé d'étape → plafond en points ; le plus bas gagne

    def _poser(cle_etape, valeur):
        if cle_etape in plafonds:
            plafonds[cle_etape] = min(plafonds[cle_etape], valeur)
        else:
            plafonds[cle_etape] = valeur

    #  PREMIER VERROU : LA PRIORISATION COTÉE SANS JUSTIFICATION ÉCRITE.
    #  Il ne porte que sur l'étape 2 : les risques sont identifiés et cotés,
    #  c'est le caractère CRÉDIBLE du processus qui manque — et le document
    #  demande que la logique de priorisation soit rendue publique.
    if pr["sans_justification"]:
        _poser("identifier",
               int(round(100 * PLAFOND_PRIORISATION_SANS_JUSTIFICATION)))
        verrous.append({
            "cle": "priorisation_sans_justification",
            "dit": "%d risque(s) coté(s) sans justification écrite."
                   % len(pr["sans_justification"]),
            "porte_sur": "Le document demande un processus de priorisation "
                         "CRÉDIBLE, dont la logique est rendue publique. La "
                         "part « identifier » ne peut pas être revendiquée "
                         "au-delà de la moitié.",
            "risques": list(pr["sans_justification"]),
            "etapes": ["identifier"],
            "ou": "ocde · processus"})

    #  SECOND VERROU : L'IMPLICATION MANQUANTE. Il ne porte que sur les deux
    #  étapes dont l'encadré 2.4 fait dépendre le NIVEAU attendu — faire
    #  cesser, et réparer. Les quatre autres se tiennent sans elle.
    if groupes and impl is None:
        cap = int(round(100 * PLAFOND_SANS_IMPLICATION))
        for c in ("traiter", "reparer"):
            _poser(c, cap)
        verrous.append({
            "cle": "implication_non_declaree",
            "dit": "L'implication dans l'incidence — causer, contribuer, "
                   "être lié — n'est pas déclarée.",
            "porte_sur": "L'encadré 2.4 fait dépendre de cette réponse le "
                         "niveau de diligence attendu. Sans elle, ni « faire "
                         "cesser » ni « réparer » ne sont calibrés sur quoi "
                         "que ce soit : ces deux parts ne peuvent pas être "
                         "revendiquées au-delà de %d %%." % cap,
            "etapes": ["traiter", "reparer"],
            "ou": "ocde · processus"})

    #  TROISIÈME VERROU : L'ÉTAPE QUE L'IMPLICATION REND NON NÉGOCIABLE.
    #  Celui-là porte sur TOUTES les parts, et c'est le seul du module qui le
    #  fasse. L'encadré 2.4 ne dit pas que la réparation compte un peu plus,
    #  il dit qu'elle est ATTENDUE dès que l'entreprise cause ou contribue :
    #  un organisme qui cause un dommage et n'a aucun dispositif de
    #  réparation ne peut pas se prévaloir de ses politiques — elles n'ont
    #  pas empêché le dommage, et rien ne le répare. Les parts BRUTES restent
    #  à côté, et l'écran montre les deux.
    if impl:
        for cle_etape in IMPLICATIONS_PAR_CLE[impl]["commande"]:
            e = par_cle.get(cle_etape)
            t = None if e is None else e["taux"]
            if t is None or t >= 100:
                continue
            for autre in ETAPES:
                _poser(autre["cle"], t)
            verrous.append({
                "cle": "etape_non_negociable",
                "dit": "Vous déclarez « %s ». Le cadre rend alors l'étape "
                       "« %s » non négociable, et elle est renseignée à "
                       "%d %%."
                       % (IMPLICATIONS_PAR_CLE[impl]["nom"],
                          ETAPES_PAR_CLE[cle_etape]["nom"], t),
                "porte_sur": "Aucune part ne peut être revendiquée au-delà "
                             "de celle-là : %s"
                             % IMPLICATIONS_PAR_CLE[impl]["attendu"],
                "etape": cle_etape,
                "etapes": [x["cle"] for x in ETAPES],
                "ou": "ocde · questionnaire"})

    #  LES PARTS PLAFONNÉES SONT CELLES QUE LE TAUX DE CONFORMITÉ LIRA, et le
    #  plafond global n'est QUE leur recomposition : une seule arithmétique,
    #  décidée ici, lue partout.
    etapes_plafonnees = []
    for e in etapes:
        t = e["taux"]
        cap = plafonds.get(e["cle"])
        if t is not None and cap is not None:
            t = min(t, cap)
        etapes_plafonnees.append(dict(e, taux=t))

    acquis_plafonne = sum(
        e["poids"] * (0.0 if e["taux"] is None else e["taux"] / 100.0)
        for e in etapes_plafonnees)
    plafond = (int(round(100.0 * acquis_plafonne / poids_total))
               if poids_total else 0)


    return {"brut": brut, "plafond": plafond, "taux": min(brut, plafond),
            "etapes": etapes, "etapes_plafonnees": etapes_plafonnees,
            "verrous": verrous, "plafonne": min(brut, plafond) < brut,
            "exemples_retenus": len(retenus), "exemples_ecartes": len(ecartes),
            "renseignes": len([c for c in rep if c in retenus_par_cle
                               and rep[c] in ETATS]),
            "nom_du_taux": NOM_DU_TAUX}


# ═══════════════════════════════════════════════════════════════════════════
#  12. LES FEUILLES DE ROUTE, LUES — ET CE QU'ELLES NE DISENT PAS
# ═══════════════════════════════════════════════════════════════════════════

def feuilles_calculees():
    """Les six feuilles de route, avec pour chaque ligne ce que Sentinel en
    sait — et l'avertissement du document au-dessus.

    CE QUE CETTE FONCTION REFUSE DE FAIRE : présenter un pont comme une
    couverture. Une ligne dit « ce cadre-là porte une exigence voisine » ;
    elle ne dit ni qu'elle est équivalente, ni que le cabinet la mesure. Les
    deux colonnes sont donc séparées, et comptées.
    """
    out = []
    for et in ETAPES:
        lignes = []
        for cle, disposition in FEUILLES[et["num"]]:
            c = CADRES_PAR_CLE[cle]
            lignes.append({
                "cadre": cle, "nom": c["nom"],
                "disposition": disposition,
                "mesure": c["mesure"],
                "tiers": bool(c.get("tiers")),
                "note": c.get("note"),
            })
        out.append({
            "etape": et["num"], "cle": et["cle"], "nom": et["nom"],
            "lignes": lignes,
            "cadres": len(lignes),
            "mesures": len([l for l in lignes if l["mesure"]]),
        })
    return {
        "etapes": out,
        "cadres": len(CADRES),
        "lignes": sum(len(e["lignes"]) for e in out),
        "cadres_mesures": list(CADRES_MESURES),
        "cadres_non_mesures": [c["cle"] for c in CADRES if not c["mesure"]],
        "cadres_tiers": list(CADRES_TIERS),
        "avertissement": AVERTISSEMENT_FEUILLES,
        #  LA PHRASE QUI EMPÊCHE DE LIRE CE TABLEAU COMME UNE ÉQUIVALENCE,
        #  en français et à l'écran, au-dessus des lignes et non en note.
        "dit": "Ces lignes sont celles du document : c'est l'OCDE qui "
               "rapproche ses six étapes des dispositions de %d autres "
               "cadres, en %d lignes. Le document écrit que ce n'est PAS un "
               "cadre d'équivalence — la portée et la nature des attentes "
               "varient d'un cadre à l'autre. Et sur ces %d cadres, Sentinel "
               "en mesure %d : les %d autres sont nommés ici et non tenus "
               "par le cabinet."
               % (len(CADRES), sum(len(e["lignes"]) for e in out),
                  len(CADRES), len(CADRES_MESURES),
                  len(CADRES) - len(CADRES_MESURES)),
    }


# ═══════════════════════════════════════════════════════════════════════════
#  13. LE PLAN — DÉRIVÉ, ET ORDONNÉ PAR CE QUE LE CADRE EXIGE D'ABORD
# ═══════════════════════════════════════════════════════════════════════════
#
# L'ORDRE N'EST PAS CELUI DES ÉTAPES. Un plan qui commencerait par l'étape 1
# ferait écrire une politique à un organisme qui ne sait pas encore s'il
# cause ou s'il est lié — et la politique serait à réécrire. L'ordre suit ce
# qui DÉBLOQUE le reste : la qualification d'abord, puis ce que l'implication
# rend non négociable, puis le travail de fond.

def plan(declaration=None, limite=12):
    d = declaration if isinstance(declaration, dict) else {}
    rep = d.get("reponses") if isinstance(d.get("reponses"), dict) else {}
    groupes = groupes_declares(d)
    impl = implication_declaree(d)
    pr = priorisation(d)
    sc = score(d)
    actions = []

    if not groupes:
        actions.append({
            "rang": 1, "cle": "groupes",
            "quoi": "Déclarer le ou les groupes d'acteur que votre organisme "
                    "occupe dans la chaîne de valeur de l'IA.",
            "pourquoi": "Rien ne se mesure avant : le questionnaire ne sait "
                        "pas lesquels des %d exemples vous visent." % len(EXEMPLES),
            "ou": "ocde · processus"})
        return {"actions": actions, "total": 1, "tronque": False}

    if impl is None:
        actions.append({
            "rang": 1, "cle": "implication",
            "quoi": "Apprécier votre implication dans les incidences "
                    "identifiées : causer, contribuer, ou être lié par une "
                    "relation d'affaires.",
            "pourquoi": "C'est la sous-étape 2.3, et elle commande le niveau "
                        "de diligence attendu aux étapes 3 et 6. Tant "
                        "qu'elle manque, le taux est plafonné à %d %%."
                        % int(round(100 * PLAFOND_SANS_IMPLICATION)),
            "ou": "ocde · processus"})

    if not pr["renseignee"]:
        actions.append({
            "rang": 2, "cle": "priorisation",
            "quoi": "Coter les risques identifiés sur les quatre facteurs du "
                    "document : échelle, portée, irrémédiabilité, "
                    "probabilité.",
            "pourquoi": "L'étape 2.4 commande l'ordre de l'étape 3. Sans "
                        "elle, « traiter » n'a pas de file d'attente.",
            "ou": "ocde · processus"})
    elif pr["sans_justification"]:
        actions.append({
            "rang": 2, "cle": "justifier_priorisation",
            "quoi": "Écrire la justification des %d risque(s) coté(s) qui "
                    "n'en portent pas." % len(pr["sans_justification"]),
            "pourquoi": "Le document demande un processus de priorisation "
                        "crédible, dont la logique est rendue publique. La "
                        "part « identifier » est plafonnée à la moitié tant "
                        "qu'une cotation reste sans raison écrite.",
            "ou": "ocde · processus"})

    #  CE QUE L'IMPLICATION REND NON NÉGOCIABLE PASSE DEVANT LE RESTE.
    non_negociables = (IMPLICATIONS_PAR_CLE[impl]["commande"] if impl else ())
    par_cle = {e["cle"]: e for e in sc["etapes"]}
    rang = 3
    for cle_etape in non_negociables:
        e = par_cle.get(cle_etape)
        if e and e["taux"] is not None and e["taux"] < 100:
            actions.append({
                "rang": rang, "cle": "etape_%s" % cle_etape,
                "quoi": "Compléter l'étape « %s » — %d exemple(s) retenu(s), "
                        "%d sans réponse."
                        % (e["nom"], e["exemples"], e["sans_reponse"]),
                "pourquoi": "Votre implication déclarée la rend non "
                            "négociable : le taux global ne peut pas la "
                            "dépasser.",
                "ou": "ocde · questionnaire"})
            rang += 1

    #  PUIS LE RESTE, PAR POIDS DÉCROISSANT PUIS PAR NUMÉRO D'ÉTAPE.
    reste = [e for e in sc["etapes"]
             if e["cle"] not in non_negociables and e["sans_reponse"]]
    for e in sorted(reste, key=lambda x: (-x["poids"], x["num"])):
        actions.append({
            "rang": rang, "cle": "etape_%s" % e["cle"],
            "quoi": "Renseigner l'étape %d « %s » — %d exemple(s) sans "
                    "réponse sur %d retenu(s)."
                    % (e["num"], e["nom"], e["sans_reponse"], e["exemples"]),
            "pourquoi": e["pourquoi"],
            "ou": "ocde · questionnaire"})
        rang += 1

    total = len(actions)
    return {"actions": actions[:limite], "total": total,
            "tronque": total > limite}


# ═══════════════════════════════════════════════════════════════════════════
#  14. L'ÉVALUATION — CE QUE L'ÉCRAN ET LE TAUX DE CONFORMITÉ LISENT
# ═══════════════════════════════════════════════════════════════════════════

#: LES RÉSERVES QUI VOYAGENT AVEC LE RÉSULTAT, quoi qu'il vaille. Aucune ne
#: se lève par le travail : la première est la nature de l'instrument, la
#: deuxième l'aveu du document sur ses propres exemples, la troisième le
#: refus d'équivalence, et la quatrième la licence.
RESERVES = (
    {"cle": "volontaire", "nom": "Aucune présomption, à aucune date",
     "dit": RESERVE_VOLONTAIRE},
    {"cle": "non_exhaustif", "nom": "Les exemples ne sont pas exhaustifs",
     "dit": CE_QUE_LE_TAUX_N_EST_PAS},
    {"cle": "pas_equivalence", "nom": "Les ponts ne valent pas équivalence",
     "dit": "Les six feuilles de route rapprochent les étapes de l'OCDE des "
            "dispositions d'autres cadres. Le document écrit que ce n'est "
            "pas un cadre d'équivalence : tenir ISO/IEC 42001 ou le cadre du "
            "NIST ne vaut pas diligence OCDE, et l'inverse est vrai aussi."},
    {"cle": "licence", "nom": "Ce qui est de l'OCDE, et ce qui est du cabinet",
     "dit": "Les intitulés et les 115 exemples pratiques viennent du "
            "document, sous licence CC BY 4.0. Le découpage du "
            "questionnaire, les poids, les plafonds et tout le français "
            "autour sont du cabinet — les deux mentions que la licence "
            "impose sont portées à l'écran, mot pour mot."},
)

RESERVES_PAR_CLE = {r["cle"]: r for r in RESERVES}


def evaluer(declaration=None, aujourdhui=None):
    d = declaration if isinstance(declaration, dict) else {}
    rep = d.get("reponses") if isinstance(d.get("reponses"), dict) else {}
    connus = {e["cle"] for e in EXEMPLES}
    inconnus = sorted(k for k in rep if k not in connus)
    if inconnus:
        return {"ok": False, "motif": "exemples_inconnus",
                "detail": inconnus[:8]}
    mauvais = sorted(k for k, v in rep.items() if v not in ETATS)
    if mauvais:
        return {"ok": False, "motif": "etats_inconnus", "detail": mauvais[:8]}

    champ = applicable(d)
    sc = score(d)
    pr = priorisation(d)
    impl = implication_declaree(d)

    if champ["ok"] is None:
        tete, dit = "non_qualifie", champ["dit"]
    elif not sc["renseignes"]:
        tete, dit = "vide", (
            "Rien n'est renseigné. Le module ne rend aucun chiffre par "
            "défaut : un questionnaire vide n'est pas une diligence à zéro, "
            "c'est une diligence qu'on n'a pas regardée.")
    elif impl is None:
        tete, dit = "implication_manquante", (
            "%d %% des exemples retenus sont déclarés tenus ; sans "
            "l'appréciation de votre implication, le cadre ne permet pas "
            "d'aller au-delà de %d %%. Ce n'est pas le travail qui manque, "
            "c'est la question qui le calibre."
            % (sc["brut"], sc["plafond"]))
    elif sc["verrous"]:
        tete, dit = "plafonne", (
            "%d %% des exemples retenus sont déclarés tenus ; ce que votre "
            "qualification laisse revendiquer s'arrête à %d %%. Les verrous "
            "disent lesquels, et où les lever."
            % (sc["brut"], sc["plafond"]))
    elif not pr["credible"]:
        tete, dit = "priorisation_absente", (
            "La priorisation de l'étape 2.4 n'est pas renseignée. Le "
            "questionnaire peut être complet sans elle ; l'étape 3 n'a alors "
            "pas de file d'attente, et le document demande un processus de "
            "priorisation crédible.")
    else:
        tete, dit = "coherent", (
            "Les groupes sont déclarés, l'implication est appréciée, la "
            "priorisation est justifiée. Reste ce que le questionnaire "
            "laisse ouvert — et les réserves, qui ne se lèvent pas par le "
            "travail.")

    return {
        "ok": True,
        "aujourdhui": (aujourdhui or datetime.date.today().isoformat()),
        "applicable": champ,
        "groupes": list(champ["groupes"]),
        "implication": impl,
        "implication_non_figee": IMPLICATION_NON_FIGEE,
        #  LE TAUX DE CONFORMITÉ LIT CELLES-CI, DÉJÀ PLAFONNÉES.
        "parts": {e["cle"]: e["taux"] for e in sc["etapes_plafonnees"]},
        "parts_brutes": {e["cle"]: e["taux"] for e in sc["etapes"]},
        "score": sc,
        "priorisation": pr,
        "exemples": len(EXEMPLES),
        "renseignes": sc["renseignes"],
        "plan": plan(d),
        "reserves": [dict(r) for r in RESERVES],
        "tete": tete, "dit": dit,
        "presomption": False,
        "nom_du_taux": NOM_DU_TAUX,
        "reserve": RESERVE_VOLONTAIRE,
    }


def referentiel():
    """La table, telle que l'écran la demande.

    LES DEUX MENTIONS DE LICENCE SONT DANS LA CHARGE, pas dans un pied de
    page du gabarit : une règle vérifie qu'elles y sont, parce que c'est la
    condition à laquelle ce module a le droit d'exister.
    """
    return {
        "source": dict(SOURCE),
        "citation": SOURCE["citation"],
        "mention_traduction": MENTION_TRADUCTION,
        "mention_adaptation": MENTION_ADAPTATION,
        "interdits": [dict(i) for i in INTERDITS],
        "reserve": RESERVE_VOLONTAIRE,
        "hors_perimetre": [dict(h) for h in HORS_PERIMETRE],
        "avertissement_exemples": AVERTISSEMENT_EXEMPLES,
        "avertissement_feuilles": AVERTISSEMENT_FEUILLES,
        "groupes": [dict(g, exemples=list(g["exemples"])) for g in GROUPES],
        "non_exclusifs": NON_EXCLUSIFS,
        "pme": PME,
        "etapes": [dict(e) for e in ETAPES],
        "etapes_en": dict(ETAPES_EN),
        "sous_etapes_en": [{"num": n, "etape": e, "en": t}
                           for n, e, t in SOUS_ETAPES_EN],
        "unites": [dict(u) for u in UNITES],
        "exemples": [dict(e, groupes=list(e["groupes"])) for e in EXEMPLES],
        "implications": [dict(i, commande=list(i["commande"]))
                         for i in IMPLICATIONS],
        "ordre_implications": list(ORDRE_IMPLICATIONS),
        "implication_non_figee": IMPLICATION_NON_FIGEE,
        "reparations": [dict(r) for r in REPARATIONS],
        "facteurs": [dict(f) for f in FACTEURS],
        "niveaux": NIVEAUX, "ordre_niveaux": list(ORDRE_NIVEAUX),
        "paliers": [dict(p) for p in PALIERS_SAILLANCE],
        "etats": ETATS, "ordre_etats": list(ORDRE_ETATS),
        "nom_du_taux": NOM_DU_TAUX,
        "ce_que_le_taux_n_est_pas": CE_QUE_LE_TAUX_N_EST_PAS,
        "feuilles": feuilles_calculees(),
        "coutures": [dict(c, exemples=list(c["exemples"]))
                      for c in COUTURES_DE_L_EXTRACTION],
        "cadres": [dict(c) for c in CADRES],
        "reserves": [dict(r) for r in RESERVES],
        "presomption": False,
        "volontaire": True,
        "exhaustif": False,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  15. LA GARDE — ELLE REJOUE L'ARITHMÉTIQUE, ELLE NE LA RELIT PAS
# ═══════════════════════════════════════════════════════════════════════════

def _verifier():
    fautes = []

    if SOURCE["presomption"] is not False or SOURCE["volontaire"] is not True:
        fautes.append("SOURCE ne dit plus que l'instrument est volontaire et "
                      "sans présomption")

    #  LES DEUX MENTIONS QUE LA LICENCE IMPOSE, MOT POUR MOT. Les tronquer
    #  ou les paraphraser ferait sortir ce module des conditions de la
    #  licence : c'est la seule faute de ce fichier qui soit juridique.
    if "only the text of the original work should be considered valid" \
            not in MENTION_TRADUCTION:
        fautes.append("MENTION_TRADUCTION n'est plus celle de la licence")
    if "This is an adaptation of an original work by the OECD" \
            not in MENTION_ADAPTATION:
        fautes.append("MENTION_ADAPTATION n'est plus celle de la licence")
    if "doi.org/10.1787/41671712-en" not in SOURCE["citation"]:
        fautes.append("SOURCE['citation'] ne porte plus le DOI de l'œuvre")

    if "conformité" in NOM_DU_TAUX.lower():
        fautes.append("le taux s'appelle « conformité » : le document "
                      "déclare ses exemples non exhaustifs")

    if len(GROUPES) != 3:
        fautes.append("%d groupes au lieu de 3" % len(GROUPES))
    if len(ETAPES) != 6:
        fautes.append("%d étapes au lieu de 6" % len(ETAPES))
    if len(UNITES) != 12:
        fautes.append("%d unités au lieu de 12" % len(UNITES))
    if len(EXEMPLES) != 115:
        fautes.append("%d exemples au lieu de 115" % len(EXEMPLES))
    if len(CADRES) != 20:
        fautes.append("%d cadres au lieu de 20" % len(CADRES))
    if len(FEUILLES) != 6:
        fautes.append("%d feuilles de route au lieu de 6" % len(FEUILLES))
    n_lignes = sum(len(v) for v in FEUILLES.values())
    if n_lignes != 91:
        fautes.append("%d lignes de pont au lieu de 91" % n_lignes)
    if len(CADRES_MESURES) != 3:
        fautes.append("%d cadre(s) mesuré(s) au lieu de 3"
                      % len(CADRES_MESURES))

    #  CHAQUE EXEMPLE VISE UNE UNITÉ CONNUE ET AU MOINS UN GROUPE CONNU.
    for e in EXEMPLES:
        if e["unite"] not in UNITES_PAR_CLE:
            fautes.append("exemple %s : unité inconnue %s"
                          % (e["cle"], e["unite"]))
        for g in e["groupes"]:
            if g not in GROUPES_PAR_CLE:
                fautes.append("exemple %s : groupe inconnu %s"
                              % (e["cle"], g))
        if not e.get("en", "").strip():
            fautes.append("exemple %s : énoncé vide" % e["cle"])
    if len({e["cle"] for e in EXEMPLES}) != len(EXEMPLES):
        fautes.append("deux exemples portent la même clé")

    #  CHAQUE UNITÉ APPARTIENT À UNE ÉTAPE CONNUE, ET CHAQUE ÉTAPE PORTE AU
    #  MOINS UNE UNITÉ : une étape sans unité serait une étape invisible.
    for u in UNITES:
        if u["etape"] not in ETAPES_PAR_NUM:
            fautes.append("unité %s : étape inconnue %r"
                          % (u["cle"], u["etape"]))
    for et in ETAPES:
        if not UNITES_DE_L_ETAPE.get(et["num"]):
            fautes.append("étape %d sans unité" % et["num"])
        if not [e for e in EXEMPLES
                if UNITES_PAR_CLE[e["unite"]]["etape"] == et["num"]]:
            fautes.append("étape %d sans exemple" % et["num"])

    #  CHAQUE LIGNE DE PONT DÉSIGNE UN CADRE CONNU ET PORTE UNE DISPOSITION.
    for num, lignes in FEUILLES.items():
        if num not in ETAPES_PAR_NUM:
            fautes.append("feuille de route pour l'étape inconnue %r" % num)
        for cle, disposition in lignes:
            if cle not in CADRES_PAR_CLE:
                fautes.append("étape %s : cadre inconnu %s" % (num, cle))
            if not (disposition or "").strip():
                fautes.append("étape %s, cadre %s : disposition vide"
                              % (num, cle))

    #  CHAQUE IMPLICATION COMMANDE AU MOINS UNE ÉTAPE EXISTANTE — sans quoi
    #  le plafond ne porterait sur rien et la doctrine serait décorative.
    for i in IMPLICATIONS:
        if not i["commande"]:
            fautes.append("implication %s ne commande aucune étape" % i["cle"])
        for c in i["commande"]:
            if c not in ETAPES_PAR_CLE:
                fautes.append("implication %s commande l'étape inconnue %s"
                              % (i["cle"], c))

    #  LES COUTURES DÉCLARÉES SONT CELLES QU'ON MESURE, ET RIEN D'AUTRE. Une
    #  couture nommée qui ne correspondrait plus serait pire que pas de
    #  déclaration : elle ferait croire le défaut connu et borné.
    minuscules = tuple(sorted(e["cle"] for e in EXEMPLES
                              if e["en"][:1].islower()
                              or e["en"][:1] in u"\u2022\u2013-"))
    declarees = tuple(sorted(c
                             for x in COUTURES_DE_L_EXTRACTION
                             for c in x["exemples"]))
    if minuscules != declarees:
        fautes.append("les exemples qui commencent en minuscule (%s) ne sont "
                      "plus ceux que COUTURES_DE_L_EXTRACTION déclare (%s)"
                      % (list(minuscules), list(declarees)))

    #  L'ARITHMÉTIQUE, REJOUÉE. Un organisme du groupe 2 qui déclare tout
    #  tenu, cause l'incidence, et laisse l'étape 6 vide : le brut est haut,
    #  le plafond est celui de l'étape 6, et le taux suit le plafond.
    exs = [e for e in EXEMPLES if "cycle_vie" in e["groupes"]]
    reponses = {e["cle"]: "tenu" for e in exs
                if UNITES_PAR_CLE[e["unite"]]["etape"] != 6}
    d = {"qualification": {"groupes": ["cycle_vie"], "implication": "cause"},
         "reponses": reponses,
         "priorisation": [{"cle": "r1", "nom": "essai", "echelle": "eleve",
                           "portee": "moyen", "irremediabilite": "faible",
                           "probabilite": "moyen",
                           "justification": "écrite"}]}
    sc = score(d)
    if sc["taux"] != 0:
        fautes.append("l'étape 6 vide sous « cause » devrait plafonner le "
                      "taux à 0, et il vaut %r" % sc["taux"])
    if sc["brut"] <= sc["taux"]:
        fautes.append("le brut devrait dépasser le taux plafonné (%r vs %r)"
                      % (sc["brut"], sc["taux"]))
    if not [v for v in sc["verrous"] if v["cle"] == "etape_non_negociable"]:
        fautes.append("aucun verrou « etape_non_negociable » alors que "
                      "l'implication « cause » rend « reparer » non "
                      "négociable")

    #  ET LE MÊME ORGANISME SANS IMPLICATION DÉCLARÉE : les deux parts dont
    #  l'encadré 2.4 fait dépendre le niveau attendu sont plafonnées à la
    #  moitié, et les quatre autres ne bougent pas. On vérifie les PARTS,
    #  parce que c'est par elles que le plafond atteint `conformite`.
    d2 = {"qualification": {"groupes": ["cycle_vie"]},
          "reponses": {e["cle"]: "tenu" for e in exs},
          "priorisation": d["priorisation"]}
    sc2 = score(d2)
    attendu = int(round(100 * PLAFOND_SANS_IMPLICATION))
    parts2 = {e["cle"]: e["taux"] for e in sc2["etapes_plafonnees"]}
    brutes2 = {e["cle"]: e["taux"] for e in sc2["etapes"]}
    for c in ("traiter", "reparer"):
        if parts2.get(c) != attendu:
            fautes.append("sans implication, la part « %s » devrait être "
                          "plafonnée à %d %% et vaut %r"
                          % (c, attendu, parts2.get(c)))
    for c in ("ancrer", "identifier", "suivre", "communiquer"):
        if parts2.get(c) != brutes2.get(c):
            fautes.append("sans implication, la part « %s » ne devrait pas "
                          "bouger (%r vs %r)"
                          % (c, parts2.get(c), brutes2.get(c)))
    if sc2["plafond"] >= sc2["brut"]:
        fautes.append("sans implication, le plafond devrait rester sous le "
                      "brut (%r vs %r)" % (sc2["plafond"], sc2["brut"]))

    #  LE PLAFOND GLOBAL N'EST QUE LA RECOMPOSITION DES PARTS PLAFONNÉES.
    #  C'est ce que `conformite` refera de son côté : si les deux calculs
    #  divergeaient, l'indice et cet écran afficheraient deux nombres.
    poids_t = sum(e["poids"] for e in ETAPES)
    recompose = int(round(sum(
        ETAPES_PAR_CLE[e["cle"]]["poids"] * (e["taux"] or 0)
        for e in sc2["etapes_plafonnees"]) / float(poids_t)))
    if recompose != sc2["plafond"]:
        fautes.append("le plafond global (%r) n'est pas la recomposition des "
                      "parts plafonnées (%r)" % (sc2["plafond"], recompose))

    #  LES EXEMPLES QU'AUCUN GROUPE DÉCLARÉ NE VISE SORTENT DU CALCUL.
    retenus, ecartes = exemples_retenus(("utilisateur",))
    if not ecartes:
        fautes.append("un organisme du seul groupe 3 devrait voir des "
                      "exemples écartés")
    if len(retenus) + len(ecartes) != len(EXEMPLES):
        fautes.append("retenus + écartés ≠ total des exemples")

    #  UNE PRIORISATION COTÉE SANS JUSTIFICATION PLAFONNE « identifier ».
    d3 = dict(d, priorisation=[{"cle": "r1", "echelle": "eleve",
                                "portee": "eleve",
                                "irremediabilite": "eleve",
                                "probabilite": "eleve"}])
    sc3 = score(d3)
    if not [v for v in sc3["verrous"]
            if v["cle"] == "priorisation_sans_justification"]:
        fautes.append("une cotation sans justification ne verrouille pas")
    ident = {e["cle"]: e["taux"] for e in sc3["etapes_plafonnees"]}
    if ident.get("identifier") is not None \
            and ident["identifier"] > int(round(
                100 * PLAFOND_PRIORISATION_SANS_JUSTIFICATION)):
        fautes.append("la part « identifier » n'est pas plafonnée alors "
                      "qu'une cotation n'a pas sa justification")

    return fautes


_FAUTES = _verifier()
if _FAUTES:
    #  RuntimeError, ET PAS AssertionError : une assertion disparaît sous
    #  `python -O`, et la garde avec elle. C'est le choix d'en18286, pour la
    #  même raison — un dépôt incohérent ne doit pas pouvoir se déployer.
    raise RuntimeError("ocde_ia : " + " | ".join(_FAUTES))
