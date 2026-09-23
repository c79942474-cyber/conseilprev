# -*- coding: utf-8 -*-
"""
LE RAIL DES DIX AUTRES RÉFÉRENTIELS — LA GRAMMAIRE DE DORA, ÉTENDUE.

═══ CE QUI A ÉTÉ DEMANDÉ ════════════════════════════════════════════════
« Dans chaque module de "Votre mise en conformité" : lorsque chaque bloc
de référentiel est rempli, l'afficher en vert et passer automatiquement au
bloc suivant — par exemple, dans NIS 2, quand "Suis-je concerné ?" est
rempli, passer à "Mesures art. 21 §2" —, et ainsi de suite jusqu'à la fin,
avec des infobulles à chaque fois et une flèche vers le bas. Pour les onze
normes présentes dans Sentinel. »

DORA avait déjà ce rail (`dora_parcours`). Ce module le donne aux dix
autres, avec les mêmes états, les mêmes couleurs, et la même règle : le
vert dit ce qu'il MESURE, jamais une conformité.

═══ TROIS SORTES DE BLOCS, ET POURQUOI IL EN FAUT TROIS ════════════════
Les écrans ont été ouverts un par un dans le navigateur, et leurs champs
comptés. Sur les trente-six écrans hors DORA :

  · À REMPLIR — vingt et un. Chaque champ a une valeur « non renseigné »
    distincte des réponses : la complétude se CONSTATE, et le bloc dit, par
    leur nom, les réponses qui manquent encore.
  · À PASSER EN REVUE — six. Des cases à cocher, ou des listes dont la
    valeur par défaut est une vraie réponse (« absent », « à planifier »,
    gravité 1). « Pas coché » s'y confond avec « pas encore regardé » :
    AUCUN calcul ne peut dire que la liste a été lue. Le bloc se valide donc
    sur une DÉCLARATION — « liste passée en revue » —, et son infobulle le
    dit en ces termes. Prétendre le mesurer serait inventer une donnée.
  · À LIRE — treize. Rien à saisir : l'écran explique. Il se marque « lu »,
    et « lu » n'est PAS vert. Le vert dit « rempli » ; un écran sans champ
    ne peut pas l'être.

═══ L'ORDRE EST CELUI DE LA BARRE LATÉRALE ═════════════════════════════
La flèche vers le bas relie deux onglets VOISINS : si l'ordre du rail
n'était pas celui de la barre, elle sauterait par-dessus des onglets. Une
règle de la suite confronte les deux, onglet par onglet.
"""

import iso27001
import iso42001
import cra
import nis2
import nis2_recyf
import nist_ai_rmf
import nist_800_53
import nist_800_82
import owasp_llm

VERSION = "2026-09-b"


# ═══════════════════════════════════════════════════════════════════════
# 1. LES ÉTATS — CEUX DE DORA, PLUS UN
# ═══════════════════════════════════════════════════════════════════════
# LES CINQ PREMIERS SONT CEUX DE DORA — clés, couleurs, puces, animation —,
# et ils en DÉRIVENT : un même vert ne peut pas vouloir dire deux choses
# d'un tiroir à l'autre. Leurs phrases, elles, ne nomment pas l'autorité —
# elle change d'un référentiel à l'autre, et chaque référentiel la nomme
# dans sa réserve.

import dora_parcours

#: CE QUE CHAQUE ÉTAT DIT ICI. La couleur, la puce et l'animation viennent
#: de DORA — une première version les recopiait, et la recopie divergeait
#: déjà : 🔒 ici, ⚠ dans DORA pour le même état.
_DITS = {
    "validee": "Ce que ce bloc attend est renseigné — ou, pour une liste à "
               "cases, déclaré passé en revue. Cela ne vaut pas conformité.",
    "courante": "Le bloc que le parcours attend. La flèche y mène, et le "
                "bandeau de l'écran nomme ce qui lui manque.",
    "attente": "Viendra à son tour. Rien n'empêche de l'ouvrir dès "
               "maintenant.",
    "verrouillee": "Dépend d'un bloc précédent : ce qu'il demanderait ne se "
                   "détermine pas sans lui.",
    "sans_objet": "Ce bloc ne s'ouvre pas pour vous, et le motif est dit.",
}
ETATS = {k: dict(v, dit=_DITS[k]) for k, v in dora_parcours.ETATS.items()}
# ── LE SIXIÈME, PROPRE À CE MODULE. Il n'est PAS vert, et c'est le point :
#    un écran sans champ n'a pas été « rempli ».
ETATS["lue"] = {
    "nom": "Lu",
    "couleur": "neutre",
    "puce": "✓",
    "anime": False,
    "dit": "Rien à remplir sur cet écran : il explique. Il est marqué lu "
           "parce que vous l'avez déclaré — ce n'est pas un bloc validé.",
}
ANIMES = tuple(k for k, v in ETATS.items() if v["anime"])

NATURES = {
    "saisie": {
        "nom": "À remplir",
        "dit": "Chaque champ a une valeur « non renseigné » : le vert dit que "
               "tous ceux que le bloc attend portent une réponse.",
    },
    "revue": {
        "nom": "À passer en revue",
        "dit": "Des cases dont la valeur par défaut est aussi une réponse : "
               "« pas coché » ne se distingue pas de « pas encore regardé ». "
               "Le vert dit que vous avez DÉCLARÉ la liste passée en revue — "
               "pas qu'un calcul l'a constaté.",
    },
    "lecture": {
        "nom": "À lire",
        "dit": "Rien à saisir : l'écran explique. Il se marque « lu », et "
               "« lu » n'est pas vert.",
    },
}


# ═══════════════════════════════════════════════════════════════════════
# 2. QUI JUGE — CE QUE LE VERT NE DIT PAS, RÉFÉRENTIEL PAR RÉFÉRENTIEL
# ═══════════════════════════════════════════════════════════════════════

QUI_JUGE = {
    "rgpd": "la CNIL apprécie, et l'article 5, paragraphe 2, met la preuve "
            "de la conformité à la charge du responsable de traitement",
    "iso27001": "seul un organisme de certification accrédité la prononce, "
                "au terme d'un audit en deux étapes",
    "iso42001": "seul un organisme de certification accrédité la prononce, "
                "au terme d'un audit en deux étapes",
    "nis2": "l'autorité nationale compétente l'apprécie — l'ANSSI selon le "
            "projet de loi de transposition —, sur pièces et par audit",
    "cra": "elle se démontre par la procédure d'évaluation de la conformité "
           "que la classe du produit impose, avant le marquage CE",
    "nist_ai_rmf": "ce cadre est volontaire et ne se certifie pas : il n'y a "
                   "pas de conformité à prononcer",
    "owasp_llm": "cette liste est un classement de risques, pas une norme : "
                 "il n'y a pas de conformité à prononcer",
    "nist_800_53": "ce catalogue ne se certifie pas hors du cadre fédéral "
                   "américain : il n'y a pas de conformité à prononcer",
    "nist_800_82": "ce guide ne se certifie pas : il n'y a pas de conformité "
                   "à prononcer",
    "ia_act": "l'autorité de surveillance du marché l'apprécie, et les "
              "systèmes à haut risque passent par une évaluation de la "
              "conformité",
}


def reserve(norme):
    return ("Le vert de ce parcours dit que ce qu'un bloc attend est "
            "renseigné — ou déclaré passé en revue. Il ne dit pas que vous "
            "êtes en conformité : %s." % QUI_JUGE[norme])


# ═══════════════════════════════════════════════════════════════════════
# 3. LES BLOCS, DANS L'ORDRE DE LA BARRE
# ═══════════════════════════════════════════════════════════════════════
# `nom` EST LE LIBELLÉ DE L'ONGLET, À LA LETTRE — une règle le vérifie :
# l'infobulle et la barre ne peuvent pas désigner le même écran par deux
# noms différents.

def _b(cle, panneau, nom, nature, quoi, pourquoi, piege, prerequis=()):
    return {"cle": cle, "panneau": panneau, "nom": nom, "nature": nature,
            "quoi": quoi, "pourquoi": pourquoi, "piege": piege,
            "prerequis": tuple(prerequis)}


BLOCS = {
    "nis2": (
        _b("qualifier", "nis2-qualifier", "Suis-je concerné ?", "saisie",
           "Le secteur, la taille, et les portes de l'article 2 qui ignorent "
           "la taille.",
           "Il commande tout le reste : hors champ, rien ne s'applique ; "
           "essentielle ou importante, la supervision et le plafond "
           "d'amende changent.",
           "« Aucun secteur choisi » n'est pas « aucune des deux annexes ». "
           "Le premier est une question sans réponse ; seul le second "
           "prononce un hors champ."),
        _b("mesures", "nis2", "Mesures art. 21 §2", "saisie",
           "Les dix mesures « tous risques » de l'article 21, paragraphe 2.",
           "C'est le socle que l'autorité contrôle, quel que soit le statut.",
           "Une mesure non renseignée n'est pas une mesure conforme : elle "
           "reste au dénominateur.",
           ("qualifier",)),
        _b("gouvernance", "nis2-gouvernance", "Gouvernance art. 20",
           "saisie",
           "Les quatre obligations des organes de direction : approuver, "
           "superviser, répondre, se former.",
           "C'est le seul article qui expose personnellement les dirigeants.",
           "La formation du personnel est un encouragement : elle s'affiche, "
           "mais le bloc se valide sans elle.",
           ("qualifier",)),
        _b("signalement", "nis2-signalement", "Signalement art. 23",
           "lecture",
           "La chaîne de notification : alerte précoce, notification, "
           "rapport final.",
           "Les délais courent en heures, et la chaîne se répète à blanc "
           "avant l'incident.",
           "L'horloge part de la PRISE DE CONNAISSANCE de l'incident "
           "important, pas de sa résolution.",
           ("qualifier",)),
        _b("recyf_objectifs", "recyf-objectifs", "ReCyF · 20 objectifs",
           "saisie",
           "Les objectifs du référentiel ReCyF que votre statut rend "
           "applicables — vingt pour une entité essentielle, quinze pour une "
           "importante.",
           "C'est la forme que la transposition française prépare. Le taux "
           "qui en sort est un taux de PRÉPARATION, séparé de tout autre.",
           "Le texte n'est pas en vigueur : le vert dit « déclaré », pas "
           "« exigé aujourd'hui ».",
           ("qualifier",)),
        _b("recyf_analyse", "recyf-analyse", "ReCyF · Analyse de risque",
           "revue",
           "Les quatre exigences de l'objectif 16 : gouvernance, couverture, "
           "acceptation des risques résiduels, réexamen.",
           "L'analyse de risque y cesse d'être une case sur dix et devient "
           "quatre exigences vérifiables.",
           "Réservé aux entités essentielles : pour une importante, le bloc "
           "est sans objet, pas à zéro.",
           ("qualifier",)),
        _b("chiffre", "nis2-chiffre", "Exposition chiffrée", "saisie",
           "Le chiffre d'affaires annuel mondial, et le plancher du plafond "
           "d'amende qu'il fixe.",
           "Le chiffre qui part en comité doit porter sa réserve dans le même "
           "bloc.",
           "C'est un PLANCHER du plafond que la loi nationale doit prévoir, "
           "pas un plafond européen.",
           ("qualifier",)),
    ),
    "iso27001": (
        _b("risques", "iso27001-risques", "Analyse de risque", "saisie",
           "Les critères d'acceptation et leurs deux dates, puis chaque "
           "risque avec sa cotation, la propriété atteinte et son "
           "propriétaire.",
           "L'appréciation des risques de l'article 6.1.2 commande la "
           "déclaration d'applicabilité qui suit.",
           "Les deux dates ne sont pas décoratives : sans elles, rien ne "
           "montre que les critères précèdent l'appréciation."),
        _b("soa", "iso27001-soa", "Déclaration d’applicabilité", "saisie",
           "Les 93 mesures de l'annexe A 2022 : retenue ou écartée, justifiée "
           "dans les deux cas, et le statut de mise en œuvre des retenues.",
           "C'est l'artefact que l'auditeur ouvre en premier.",
           "Une mesure ni retenue ni écartée suffit à rendre la déclaration "
           "irrecevable."),
        _b("articles", "iso27001", "Articles 4 à 10", "saisie",
           "Les trente sous-articles du corps de la norme.",
           "Les exigences du corps ne s'écartent pas : seules les mesures de "
           "l'annexe A le peuvent.",
           "« Sans objet » n'y est pas une réponse : il est refusé et le "
           "sous-article reste à renseigner."),
        _b("millesime", "iso27001-millesime",
           "2013 → 2022 : ce qui a changé", "lecture",
           "Ce qui distingue la version 2022 de la version 2013 : 93 mesures "
           "en 4 thèmes au lieu de 114 en 14 chapitres.",
           "Un organisme certifié en 2013 a onze mesures nouvelles devant "
           "lui — pas 93.",
           "Un questionnaire encore écrit contre 2013 ne vise plus la norme "
           "en vigueur."),
    ),
    "iso42001": (
        _b("articles", "iso42001", "Articles 4 à 10", "saisie",
           "Les trente-deux sous-articles du corps de la norme.",
           "Les exigences du corps ne s'écartent pas, et certaines sont "
           "propres à l'IA.",
           "« Sans objet » n'y est pas une réponse : il est refusé et le "
           "sous-article reste à renseigner."),
        _b("soa", "iso42001-soa", "Déclaration d’applicabilité", "saisie",
           "Les 38 mesures de l'annexe A : retenue ou écartée, et justifiée "
           "dans les deux cas.",
           "C'est l'artefact que l'auditeur ouvre en premier.",
           "Une seule mesure non décidée renvoie l'organisme à l'étape "
           "documentaire."),
        _b("certif", "iso42001-certif", "Chemin de certification",
           "lecture",
           "Les deux étapes de l'audit, et ce qui fait échouer la première.",
           "Savoir ce que l'auditeur ouvre en premier évite de préparer "
           "l'étape 2 avant l'étape 1.",
           "La certification porte sur le système de management, pas sur "
           "chaque système d'IA."),
        _b("ponts", "iso42001-ponts", "Ponts IA Act / RGPD / NIS 2",
           "lecture",
           "Ce qui se réutilise d'un cadre à l'autre, et ce qui ne se "
           "réutilise pas.",
           "Ne pas documenter deux fois ce qu'un seul dossier prouve.",
           "Un pont n'est pas une équivalence : il réutilise une preuve, il "
           "ne transfère pas une obligation."),
    ),
    "cra": (
        _b("role", "cra-role", "Qualifier mon rôle", "saisie",
           "Ce que vous faites du produit : concevoir, importer, distribuer, "
           "le vendre sous votre marque, le modifier.",
           "Le règlement regarde vos GESTES, pas votre métier : le rôle "
           "commande les obligations.",
           "Vendre sous sa marque ou modifier substantiellement un produit "
           "fait de vous un fabricant."),
        _b("produits", "cra", "Produits & classification", "saisie",
           "Le registre des produits comportant des éléments numériques, et "
           "la classe déclarée de chacun.",
           "La classe commande la procédure d'évaluation, donc le budget.",
           "La classe est DÉCLARÉE, jamais devinée du nom du produit.",
           ("role",)),
        _b("ecarts", "cra-ecarts", "Analyse d’écart", "saisie",
           "Les vingt et une exigences essentielles de l'annexe I, parties I "
           "et II.",
           "C'est le cœur du règlement, et ce que la documentation technique "
           "devra démontrer.",
           "« Partiel » n'est pas « conforme » : il compte pour une moitié.",
           ("role",)),
        _b("chiffre", "cra-chiffre", "Exposition chiffrée", "saisie",
           "Le chiffre d'affaires annuel mondial, et les trois paliers "
           "d'amende de l'article 64.",
           "Le chiffre qui part en comité doit porter sa réserve dans le même "
           "bloc.",
           "Le plafond retenu est le plus élevé des deux montants.",
           ("role",)),
        _b("signalement", "cra-signalement", "Signalement art. 14",
           "lecture",
           "Vulnérabilité activement exploitée et incident grave : les "
           "échéances de vingt-quatre heures, soixante-douze heures, puis le "
           "rapport final.",
           "C'est l'obligation du règlement qui s'applique la première.",
           "Elle vise aussi les produits déjà sur le marché.",
           ("role",)),
    ),
    "nist_ai_rmf": (
        _b("profil", "nist-profil", "Profil par fonction", "saisie",
           "Les dix-neuf catégories des quatre fonctions — Govern, Map, "
           "Measure, Manage —, chacune avec son état.",
           "Le cadre se lit en profil, jamais en note globale.",
           "Une catégorie muette compte comme absente : le profil s'étale "
           "sur toutes."),
        _b("cadre", "nist-cadre", "Le cadre, catégorie par catégorie",
           "lecture",
           "Ce que chaque catégorie demande, sous-catégorie par "
           "sous-catégorie.",
           "Coter une catégorie suppose de savoir ce qu'elle recouvre.",
           "Le cadre est volontaire : il décrit des résultats, pas des "
           "contrôles imposés."),
        _b("genai", "nist-genai", "Profil IA générative", "lecture",
           "Les douze risques propres à l'IA générative (NIST AI 600-1).",
           "Ils s'ajoutent au profil, ils ne le remplacent pas.",
           "Un risque propre à l'IA générative se traite dans les "
           "catégories existantes du cadre."),
    ),
    "owasp_llm": (
        _b("dix", "owasp-dix", "Les dix risques", "saisie",
           "Le millésime 2025 du Top 10 des applications à base de LLM, "
           "risque par risque.",
           "Chaque risque se déclare traité, partiellement, ou non.",
           "Ce n'est pas une note sur dix : c'est un profil et des angles "
           "morts."),
        _b("pont", "owasp-pont", "Ce qu’ISO 42001 ne couvre pas", "lecture",
           "Les risques qu'aucune mesure de l'annexe A d'ISO/IEC 42001 ne "
           "vise directement.",
           "Une certification 42001 ne dispense pas de les traiter.",
           "Le pont dit où la norme s'arrête, pas qu'elle est insuffisante."),
    ),
    "nist_800_53": (
        _b("socle", "nist53-socle", "Socle et dix-huit familles", "saisie",
           "Le socle retenu — Low, Moderate ou High —, puis l'état de chacune "
           "des dix-huit familles de mesures.",
           "Le socle décide de ce que chaque famille doit contenir.",
           "Révision 4 : ce n'est plus le dernier millésime du catalogue."),
    ),
    "nist_800_82": (
        _b("ot", "nist82-ot", "Surcharge industrielle (OT)", "saisie",
           "Les dix axes que l'industriel ajoute au socle 800-53.",
           "Un axe est plafonné par la plus faible des familles 800-53 qu'il "
           "taille.",
           "Sans le socle 800-53 renseigné, chaque axe est plafonné à zéro : "
           "remplissez d'abord l'écran du catalogue."),
    ),
    "rgpd": (
        _b("hub", "rgpd-hub", "Vue d’ensemble", "lecture",
           "Le point d'entrée du dispositif RGPD, et ce que chaque écran "
           "couvre.",
           "Savoir où l'on va avant de remplir le registre.",
           "La vue d'ensemble ne mesure rien : elle oriente."),
        _b("traitements", "rgpd-traitements", "Registre des traitements",
           "saisie",
           "Chaque traitement, avec les six champs de l'article 30 que le "
           "module suit : finalités, base légale, catégories de personnes et "
           "de données, durée de conservation, mesures de sécurité.",
           "Le registre est la pièce que la CNIL demande en premier, et il "
           "alimente l'AIPD et la cartographie.",
           "Un traitement déclaré sans sa base légale n'est pas un "
           "traitement renseigné."),
        _b("cartographie", "rgpd-cartographie",
           "Cartographie des traitements", "lecture",
           "Le registre vu d'ensemble : flux, catégories, destinataires.",
           "Ce qui ne se voit pas ligne à ligne se voit en carte.",
           "Elle ne montre que ce que le registre contient.",
           ("traitements",)),
        _b("aipd", "rgpd-aipd", "AIPD (art. 35)", "revue",
           "Pour chaque traitement : les neuf critères, puis la gravité et "
           "la vraisemblance de trois événements redoutés.",
           "Deux critères réunis rendent l'AIPD obligatoire (article 35).",
           "Gravité et vraisemblance valent 1 par défaut : une AIPD jamais "
           "ouverte ressemble à une AIPD qui conclut au risque minimal.",
           ("traitements",)),
        _b("pbd", "rgpd-pbd", "Privacy by design", "revue",
           "Les contrôles de l'article 25 : minimisation, droits, "
           "sous-traitance, réexamen.",
           "La protection des données se conçoit avant la mise en "
           "production, pas après.",
           "Une case non cochée dit « pas en place » ou « pas encore "
           "regardé » — la liste ne permet pas de les distinguer."),
        _b("doc", "rgpd-doc", "Politique documentaire", "revue",
           "Les documents d'accountability, avec leur statut, leur "
           "responsable et leur date de revue.",
           "L'article 5, paragraphe 2, fait de la documentation la preuve "
           "de la conformité.",
           "« Absent » est la valeur par défaut : un document jamais "
           "regardé s'affiche comme absent."),
        _b("sensibilisation", "rgpd-sensibilisation", "Sensibilisation",
           "revue",
           "Le plan de sensibilisation, public par public, avec sa "
           "fréquence.",
           "Une mesure organisationnelle qui ne se forme pas ne se tient "
           "pas.",
           "« À planifier » est la valeur par défaut : une action jamais "
           "regardée s'affiche comme à planifier."),
        _b("conformite", "rgpd-conformite", "Conformité RGPD", "lecture",
           "Le tableau de bord qui consolide le registre, l'AIPD, la privacy "
           "by design, la documentation et la sensibilisation.",
           "Il se lit à la fin : il ne dit que ce que les écrans précédents "
           "contiennent.",
           "L'indice consolidé est une moyenne d'axes : il ne remplace pas "
           "la lecture axe par axe."),
    ),
    "ia_act": (
        _b("hub", "ia-act-hub", "Vue d’ensemble IA Act", "lecture",
           "Le point d'entrée du dispositif IA Act : cartographier, classer, "
           "évaluer, documenter, prouver.",
           "Savoir quels systèmes sont concernés avant d'auditer.",
           "La vue d'ensemble ne mesure rien : elle oriente."),
        _b("audit", "audit-ia-act", "Audit IA Act", "revue",
           "Les trente-quatre points de contrôle de l'audit, en huit "
           "sections, des pratiques interdites aux modèles à usage général.",
           "C'est l'audit que le taux de conformité de l'IA Act lit.",
           "Un point non coché dit « pas fait » ou « pas encore regardé » : "
           "la bascule ne permet pas de les distinguer."),
    ),
}

BLOCS_PAR_NORME = {n: {b["cle"]: b for b in bs} for n, bs in BLOCS.items()}
for _n, _bs in BLOCS.items():
    for _i, _bloc in enumerate(_bs, 1):
        _bloc["rang"] = _i


# ═══════════════════════════════════════════════════════════════════════
# 4. CE QUI MANQUE — NOMMÉ PAR LES MOTEURS DES MODULES, JAMAIS RECOPIÉ
# ═══════════════════════════════════════════════════════════════════════
# CHAQUE LISTE VIENT DU MODULE QUI TIENT LE RÉFÉRENTIEL. Les dix mesures
# viennent de `nis2`, les 93 mesures de `iso27001`, les vingt et une
# exigences de `cra`. Une seconde liste écrite ici se séparerait de la
# première au premier millésime.

def _q(texte):
    return {"quoi": texte}


def _dict(d, cle):
    v = d.get(cle)
    return v if isinstance(v, dict) else {}


def _nombre(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0


#: LA RÉPONSE « AUCUNE DES DEUX ANNEXES ». Sans elle, la liste des secteurs
#: n'offrait pour première option qu'un « — aucun secteur des annexes I ou
#: II — » dont la valeur était VIDE — celle-là même d'une question laissée
#: sans réponse. Le moteur de qualification lit toute clé hors des annexes
#: comme un secteur déclaré hors champ ; celle-ci en est une.
SECTEUR_HORS_ANNEXES = "hors_annexes"

_NIS2_PORTES = set(nis2.HORS_TAILLE_PAR_CLE) | set(nis2.ESSENTIELLE_HORS_TAILLE)


def _nis2_qualification(d):
    """Ce qui manque pour que la qualification soit PRONONCÉE, et le verdict.

    UNE QUALIFICATION VIDE REND DÉJÀ « HORS CHAMP » — mesuré sur le moteur :
    sans secteur, il répond « Aucun secteur déclaré ». Le rail ne peut donc
    pas lire le verdict pour savoir si la question a reçu une réponse ; il
    lit la DÉCLARATION."""
    manque = []
    portes = [c for c in _NIS2_PORTES if d.get(c)]
    directes = [c for c in nis2.ESSENTIELLE_HORS_TAILLE if d.get(c)]
    if not directes:
        secteur = d.get("secteur")
        if not secteur:
            manque.append(_q("Le secteur d'activité — ou « aucune des deux "
                             "annexes »"))
        elif secteur in nis2.SECTEURS and not portes:
            t = nis2.taille(d.get("effectif"), d.get("ca_eur"),
                            d.get("bilan_eur"))
            for x in t.get("manquants") or ():
                manque.append(_q("La taille : " + x))
    verdict = None
    if not manque:
        charge = {k: d.get(k) for k in ("secteur", "effectif", "ca_eur",
                                         "bilan_eur")}
        charge.update({c: True for c in portes})
        verdict = nis2.qualifier(charge)
    return manque, verdict


def _nis2(d):
    manque, sans_objet = {}, {}
    manque["qualifier"], verdict = _nis2_qualification(d)

    mesures = _dict(d, "mesures")
    manque["mesures"] = [
        _q("Mesure %s) — %s" % (cle, nom)) for cle, nom, _dit in nis2.MESURES
        if mesures.get(cle) not in nis2._ETATS]

    gouv = _dict(d, "gouvernance")
    manque["gouvernance"] = [
        _q("%s (%s)" % (g["quoi"], g["article"])) for g in nis2.GOUVERNANCE
        if g["cle"] in nis2.GOUVERNANCE_OBLIGATOIRE
        and gouv.get(g["cle"]) not in ("conforme", "partiel", "non_conforme")]

    recyf = _dict(d, "recyf")
    statut = recyf.get("statut")
    if statut not in ("essentielle", "importante"):
        manque["recyf_objectifs"] = [
            _q("Votre statut au sens du référentiel : entité essentielle ou "
               "importante")]
        manque["recyf_analyse"] = [
            _q("Votre statut, choisi sur l'écran des vingt objectifs")]
    else:
        etats = _dict(recyf, "etats")
        manque["recyf_objectifs"] = [
            _q("Objectif %d — %s" % (o["numero"], o["titre"]))
            for o in nis2_recyf.attendus(statut)["objectifs"]
            if o["dans_le_champ"]
            and etats.get(str(o["numero"]),
                          etats.get(o["numero"])) not in nis2_recyf.ETATS]
        if statut == "importante":
            sans_objet["recyf_analyse"] = (
                "L'objectif 16 est réservé aux entités essentielles par "
                "proportionnalité : pour une entité importante, ce bloc est "
                "sans objet — pas à zéro.")

    manque["chiffre"] = ([] if _nombre(d.get("chiffre_affaires")) else
                         [_q("Le chiffre d'affaires annuel mondial de "
                             "l'exercice précédent")])

    # ── HORS CHAMP : LE PARCOURS S'ARRÊTE AU PREMIER BLOC, ET C'EST LE BON
    #    RÉSULTAT. Seulement quand le verdict vient d'une qualification
    #    RENSEIGNÉE : un formulaire vide rend lui aussi « hors champ ».
    if verdict and verdict.get("ok") and verdict["statut"]["cle"] == "hors_champ":
        motif = ("Hors du champ de la directive : %s (%s)."
                 % (verdict["motif"].rstrip("."), verdict["article"]))
        for b in BLOCS["nis2"][1:]:
            sans_objet[b["cle"]] = motif
    return manque, sans_objet, {"verdict": verdict}


def _iso27001(d):
    manque = {}
    c = _dict(d, "criteres")
    m = []
    if not str(c.get("etabli_le") or "").strip():
        m.append(_q("La date à laquelle les critères d'acceptation ont été "
                    "établis"))
    if not str(c.get("apprecie_le") or "").strip():
        m.append(_q("La date de l'appréciation des risques"))
    risques = d.get("risques") if isinstance(d.get("risques"), list) else []
    if not risques:
        m.append(_q("Au moins un risque porté au registre"))
    else:
        a = iso27001.apprecier(risques, {k: v for k, v in c.items()
                                         if k == "seuil_acceptation"})
        if not a.get("ok"):
            m.append(_q("Le seuil d'acceptation, entre 1 et 16"))
        else:
            for df in a["defauts"]:
                m.append(_q("Risque « %s » : %s" % (df["nom"],
                                                    ", ".join(df["manques"]))))
    manque["risques"] = m

    s = iso27001.declaration_applicabilite(_dict(d, "mesures"))
    titre = lambda n: iso27001.MESURES[n]["titre"]
    manque["soa"] = (
        [_q("%s %s — retenue ou écartée" % (n, titre(n)))
         for n in s["non_decidees"]]
        + [_q("%s %s — justification" % (n, titre(n)))
           for n in s["sans_justification"]]
        + [_q("%s %s — statut de mise en œuvre" % (n, titre(n)))
           for n in s["sans_statut"]])

    mat = iso27001.maturite(_dict(d, "articles"))
    manque["articles"] = [
        _q("%s %s" % (l["numero"], l["titre"]))
        for ch in mat["chapitres"] for l in ch["lignes"]
        if l["etat"] == "non_renseigne"]
    return manque, {}, {}


def _iso42001(d):
    manque = {}
    mat = iso42001.maturite(_dict(d, "articles"))
    manque["articles"] = [
        _q("%s %s" % (l["numero"], l["titre"]))
        for ch in mat["chapitres"] for l in ch["lignes"]
        if l["etat"] == "non_renseigne"]
    s = iso42001.declaration_applicabilite(_dict(d, "mesures"))
    titre = lambda n: iso42001.MESURES[n]["titre"]
    manque["soa"] = (
        [_q("%s %s — retenue ou écartée" % (n, titre(n)))
         for n in s["non_decidees"]]
        + [_q("%s %s — justification" % (n, titre(n)))
           for n in s["sans_justification"]])
    return manque, {}, {}


#: LES QUESTIONS DE RÔLE QUE L'ÉCRAN POSE, sauf la sous-question qui ne
#: précise qu'une modification. MÊME PIÈGE QUE LE SECTEUR NIS 2 : sans
#: aucune réponse, le moteur rend déjà un rôle — « distributeur ». Le rail ne
#: lit donc pas le verdict, il lit la déclaration. Et « je distribue », que
#: le moteur n'a pas besoin de lire pour conclure, est ce qui fait de ce
#: verdict par défaut une RÉPONSE.
CRA_ROLE_CLES = ("je_concois", "fabricant_hors_union", "je_distribue",
                 "sous_ma_marque", "modification_substantielle")


def _cra(d):
    manque = {}
    role = _dict(d, "role")
    manque["role"] = ([] if any(role.get(k) for k in CRA_ROLE_CLES) else
                      [_q("Au moins une réponse sur ce que vous faites du "
                          "produit")])
    produits = d.get("produits") if isinstance(d.get("produits"), list) else []
    nommes = [p for p in produits
              if isinstance(p, dict) and str(p.get("nom") or "").strip()]
    manque["produits"] = ([] if nommes else
                          [_q("Au moins un produit comportant des éléments "
                              "numériques, avec son nom et sa classe")])
    ecarts = _dict(d, "ecarts")
    manque["ecarts"] = [
        _q("%s — %s" % (cle, titre))
        for cle, titre, _dit in cra.ANNEXE_I_I + cra.ANNEXE_I_II
        if ecarts.get(cle) not in cra._ETATS]
    manque["chiffre"] = ([] if _nombre(d.get("chiffre_affaires")) else
                         [_q("Le chiffre d'affaires annuel mondial de "
                             "l'exercice précédent")])
    return manque, {}, {}


def _nist_ai_rmf(d):
    etats = _dict(d, "etats")
    return ({"profil": [_q("%s — %s" % (c["cle"], c["nom"]))
                        for c in nist_ai_rmf.CATEGORIES
                        if etats.get(c["cle"]) not in nist_ai_rmf.ETATS]},
            {}, {})


def _owasp_llm(d):
    etats = _dict(d, "etats")
    return ({"dix": [_q("%s — %s" % (r["cle"], r["nom"]))
                     for r in owasp_llm.RISQUES
                     if etats.get(r["cle"]) not in owasp_llm.ETATS]},
            {}, {})


def _nist_800_53(d):
    etats = _dict(d, "etats")
    m = ([] if d.get("socle") in nist_800_53.SOCLES else
         [_q("Le socle retenu : Low, Moderate ou High")])
    m += [_q("%s — %s" % (f[0], f[1])) for f in nist_800_53.FAMILLES
          if etats.get(f[0]) not in nist_800_53.ETATS]
    return {"socle": m}, {}, {}


def _nist_800_82(d):
    etats = _dict(d, "etats")
    return ({"ot": [_q(a["nom"]) for a in nist_800_82.AXES
                    if etats.get(a["cle"]) not in nist_800_82.ETATS]},
            {}, {})


#: LES SIX CHAMPS DE L'ARTICLE 30 QUE LE MODULE SUIT DÉJÀ — ceux que son
#: tableau de bord compte. Le rail ne s'en invente pas d'autres.
RGPD_CHAMPS_ART30 = (
    ("finalites", "finalités"),
    ("base_legale", "base légale"),
    ("categories_personnes", "catégories de personnes"),
    ("categories_donnees", "catégories de données"),
    ("duree_conservation", "durée de conservation"),
    ("mesures_securite", "mesures de sécurité"),
)


def _rgpd(d):
    traitements = (d.get("traitements")
                   if isinstance(d.get("traitements"), list) else [])
    m = []
    if not traitements:
        m.append(_q("Au moins un traitement au registre"))
    for t in traitements:
        t = t if isinstance(t, dict) else {}
        champs = _dict(t, "champs")
        vides = [nom for cle, nom in RGPD_CHAMPS_ART30 if not champs.get(cle)]
        if vides:
            m.append(_q("« %s » : %s" % (str(t.get("nom") or "(sans nom)"),
                                          ", ".join(vides))))
    return {"traitements": m}, {}, {}


def _ia_act(d):
    return {}, {}, {}


EVALUATEURS = {
    "nis2": _nis2, "iso27001": _iso27001, "iso42001": _iso42001,
    "cra": _cra, "nist_ai_rmf": _nist_ai_rmf, "owasp_llm": _owasp_llm,
    "nist_800_53": _nist_800_53, "nist_800_82": _nist_800_82,
    "rgpd": _rgpd, "ia_act": _ia_act,
}


# ═══════════════════════════════════════════════════════════════════════
# 5. L'AVANCEMENT — UN SEUL ENDROIT LE CALCULE
# ═══════════════════════════════════════════════════════════════════════

def _declares(d, cle, norme):
    """Les panneaux déclarés lus, ou passés en revue — ceux de CE parcours.

    UNE DÉCLARATION NE VALIDE QUE CE QUI SE VALIDE PAR DÉCLARATION, et ce
    n'est pas ce filtre qui le garantit : c'est que chaque branche de
    `avancement` ne lit que la sienne. Un bloc à remplir ne consulte ni
    « lus » ni « revus » — sans quoi un clic validerait ce qu'il demande de
    renseigner. Une règle de la suite le vérifie."""
    brut = d.get(cle)
    brut = brut if isinstance(brut, (list, tuple)) else ()
    admis = {b["panneau"] for b in BLOCS[norme]}
    return {p for p in brut if isinstance(p, str) and p in admis}


def avancement(norme, declaration=None):
    """L'état des blocs d'un référentiel, ce qui manque à chacun, et lequel
    bat.

    UN SEUL BLOC EST COURANT : le premier ni validé, ni lu, ni sans objet,
    dont les prérequis tiennent. Pas le suivant du dernier rempli — qui a
    rempli 1 et 3 est ramené à 2."""
    if norme not in BLOCS:
        return {"ok": False, "motif": "norme_inconnue",
                "normes": sorted(BLOCS)}
    d = declaration if isinstance(declaration, dict) else {}
    manque, sans_objet, contexte = EVALUATEURS[norme](d)
    lus = _declares(d, "lus", norme)
    revus = _declares(d, "revus", norme)

    lignes, valides = [], set()
    for b in BLOCS[norme]:
        l = dict(b, prerequis=list(b["prerequis"]), etat=None, motif=None,
                 manque=[], prerequis_manquants=[])
        if b["cle"] in sans_objet:
            l.update(etat="sans_objet", motif=sans_objet[b["cle"]])
            lignes.append(l)
            continue
        absents = [p for p in b["prerequis"] if p not in valides]
        if b["nature"] == "lecture":
            if b["panneau"] in lus and not absents:
                valides.add(b["cle"])
                l["etat"] = "lue"
            elif b["panneau"] not in lus:
                l["manque"].append(_q("Lisez l'écran, puis marquez-le lu — "
                                      "le bouton est au bas de l'écran"))
        elif b["nature"] == "revue":
            l["manque"] = list(manque.get(b["cle"]) or [])
            if b["panneau"] in revus and not absents and not l["manque"]:
                valides.add(b["cle"])
                l["etat"] = "validee"
            elif b["panneau"] not in revus:
                l["manque"].append(_q("Déclarez la liste passée en revue — "
                                      "le bouton est au bas de l'écran"))
        else:
            l["manque"] = list(manque.get(b["cle"]) or [])
            if not l["manque"] and not absents:
                valides.add(b["cle"])
                l["etat"] = "validee"
        l["prerequis_manquants"] = absents
        lignes.append(l)

    noms = {b["cle"]: b["nom"] for b in BLOCS[norme]}
    courante = None
    for l in lignes:
        if l["etat"] is not None:
            continue
        if l["prerequis_manquants"]:
            l["etat"] = "verrouillee"
            l["motif"] = ("Ce bloc dépend de : %s. Complétez-le d'abord."
                          % ", ".join(noms[p] for p in l["prerequis_manquants"]))
            continue
        if courante is None:
            courante = l["cle"]
            l["etat"] = "courante"
        else:
            l["etat"] = "attente"

    # ── LE SUIVANT EST CALCULÉ ICI, PAS DEVINÉ PAR L'ÉCRAN : c'est lui qui
    #    porte le passage automatique. Même leçon que DORA : un bloc
    #    VERROUILLÉ reste un suivant légitime, puisque valider le bloc
    #    courant peut précisément le déverrouiller.
    suivant = None
    if courante:
        rang = BLOCS_PAR_NORME[norme][courante]["rang"]
        reste = [l for l in lignes if l["rang"] > rang
                 and l["etat"] != "sans_objet"]
        suivant = reste[0]["cle"] if reste else None

    ouvrables = [l for l in lignes if l["etat"] != "sans_objet"]
    faits = [l for l in ouvrables if l["etat"] in ("validee", "lue")]
    return {
        "ok": True,
        "version": VERSION,
        "norme": norme,
        "blocs": lignes,
        "courante": courante,
        "suivant": suivant,
        "total": len(ouvrables),
        "faits": len(faits),
        "valides": sum(1 for l in ouvrables if l["etat"] == "validee"),
        "part": (round(100.0 * len(faits) / len(ouvrables), 1)
                 if ouvrables else 0.0),
        "fini": bool(ouvrables) and len(faits) == len(ouvrables),
        "conclusion": _conclusion(norme, lignes, ouvrables, faits, contexte),
        "sans_objet": [{"cle": l["cle"], "nom": l["nom"], "motif": l["motif"]}
                       for l in lignes if l["etat"] == "sans_objet"],
        "etats": {k: dict(v) for k, v in ETATS.items()},
        "natures": {k: dict(v) for k, v in NATURES.items()},
        "reserve": reserve(norme),
    }


def _conclusion(norme, lignes, ouvrables, faits, contexte):
    """Ce que la fin du parcours signifie — et ce qu'elle ne signifie pas."""
    if not ouvrables or len(faits) != len(ouvrables):
        return None
    v = (contexte or {}).get("verdict")
    if norme == "nis2" and v and v.get("statut", {}).get("cle") == "hors_champ":
        return ("Le parcours s'arrête au premier bloc, et c'est le bon "
                "résultat : l'entité est hors du champ de la directive. Cent "
                "pour cent ne dit pas que le travail est fait — il dit qu'il "
                "n'y en a pas.")
    revues = sum(1 for l in ouvrables
                 if l["nature"] == "revue" and l["etat"] == "validee")
    return ("Les %d blocs du parcours sont faits%s. Ce n'est pas une "
            "conformité : %s."
            % (len(ouvrables),
               (" — dont %d par une revue que vous avez déclarée" % revues
                if revues else ""),
               QUI_JUGE[norme]))


def referentiel():
    return {
        "version": VERSION,
        "etats": {k: dict(v) for k, v in ETATS.items()},
        "natures": {k: dict(v) for k, v in NATURES.items()},
        "secteur_hors_annexes": SECTEUR_HORS_ANNEXES,
        # LES CHAMPS QUE L'ÉCRAN DOIT DIRE REMPLIS OU NON, pour chaque
        # traitement : relus ici par le collecteur, jamais recopiés en
        # JavaScript.
        "rgpd_champs": [cle for cle, _nom in RGPD_CHAMPS_ART30],
        "normes": {n: {"reserve": reserve(n),
                       "blocs": [dict(b, prerequis=list(b["prerequis"]))
                                 for b in bs]}
                   for n, bs in BLOCS.items()},
    }


# ═══════════════════════════════════════════════════════════════════════
# 6. LE RÉFÉRENTIEL SE CONTREDIT-IL ? CONTRÔLÉ À L'IMPORT
# ═══════════════════════════════════════════════════════════════════════

def _verifier():
    fautes = []
    if len(ANIMES) != 1 or ANIMES[0] != "courante":
        fautes.append("l'animation doit être réservée au seul état "
                      "« courante » : %s" % list(ANIMES))
    if ETATS["lue"]["couleur"] == ETATS["validee"]["couleur"]:
        fautes.append("« lu » ne peut pas porter le vert de « validé » : un "
                      "écran sans champ n'a pas été rempli")
    for k, v in ETATS.items():
        if not (v.get("nom") and v.get("dit") and v.get("puce")):
            fautes.append("état %s : incomplet" % k)
    panneaux = {}
    for n, bs in BLOCS.items():
        if n not in EVALUATEURS:
            fautes.append("%s : aucun évaluateur" % n)
        if n not in QUI_JUGE:
            fautes.append("%s : sa réserve ne dit pas qui juge" % n)
        if bs and bs[0]["prerequis"]:
            fautes.append("%s : le premier bloc porte un prérequis — le "
                          "parcours ne pourrait pas commencer" % n)
        vus = set()
        for b in bs:
            if b["nature"] not in NATURES:
                fautes.append("%s/%s : nature inconnue %r"
                              % (n, b["cle"], b["nature"]))
            for champ in ("nom", "quoi", "pourquoi", "piege", "panneau"):
                if not b.get(champ):
                    fautes.append("%s/%s : %s manquant" % (n, b["cle"], champ))
            if b["cle"] in vus:
                fautes.append("%s : bloc %s déclaré deux fois" % (n, b["cle"]))
            vus.add(b["cle"])
            # ── UN PRÉREQUIS VIENT TOUJOURS AVANT, sans quoi le bloc
            #    serait verrouillé pour toujours.
            for p in b["prerequis"]:
                if p not in BLOCS_PAR_NORME[n]:
                    fautes.append("%s/%s : prérequis inconnu %r"
                                  % (n, b["cle"], p))
                elif BLOCS_PAR_NORME[n][p]["rang"] >= b["rang"]:
                    fautes.append("%s/%s dépend de %s, qui vient APRÈS lui"
                                  % (n, b["cle"], p))
            if b["panneau"] in panneaux:
                fautes.append("le panneau %s appartient à deux parcours : %s "
                              "et %s" % (b["panneau"], panneaux[b["panneau"]], n))
            panneaux[b["panneau"]] = n
    return fautes


_FAUTES = _verifier()
assert not _FAUTES, "parcours_normes.py se contredit : %s" % _FAUTES
