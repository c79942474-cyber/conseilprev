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

═══ DEUX SORTES DE BLOCS — IL Y EN AVAIT TROIS ═════════════════════════
Les écrans ont été ouverts un par un dans le navigateur, et leurs champs
comptés. Sur les trente-six écrans hors DORA :

  · À REMPLIR — vingt-sept. Chaque question a une valeur « non renseigné »
    distincte des réponses : la complétude se CONSTATE, et le bloc dit, par
    leur nom, les réponses qui manquent encore.
  · À LIRE — treize. Rien à saisir : l'écran explique. Il se marque « lu »,
    et « lu » n'est PAS vert. Le vert dit « rempli » ; un écran sans champ
    ne peut pas l'être.

LES SIX QUI SE VALIDAIENT SUR UNE DÉCLARATION. L'audit IA Act, l'AIPD, la
privacy by design, la politique documentaire, la sensibilisation et
l'analyse de risque ReCyF étaient des cases à cocher, ou des listes dont la
valeur par défaut était une vraie réponse (« absent », « à planifier »,
gravité 1) : « pas coché » s'y confondait avec « pas encore regardé ». Leur
bloc passait au vert sur un clic — « liste passée en revue ». Chacune de
leurs questions porte désormais une réponse explicite, « non renseigné »
compris, et le bloc se MESURE comme les autres : il ne passe au vert que
lorsque chaque question a été répondue, et il nomme celles qui restent.

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
import en18286
import ocde_ia
import nist_ai_rmf
import nist_genai
import nist_800_53
import nist_800_82
import owasp_llm

VERSION = "2026-09-c"


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
    "validee": "Ce que ce bloc attend est renseigné. Cela ne vaut pas "
               "conformité.",
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
    #  CE PROJET N'EST PAS CITÉ AU JOURNAL OFFICIEL : rien ne s'y présume
    #  encore. Ce qui jugera, le jour venu, c'est l'évaluation de conformité
    #  de l'article 43 — pas un audit de système de management.
    "en18286": "ce projet de norme n'est pas encore cité au Journal officiel "
               "de l'Union européenne : il n'ouvre aucune présomption de "
               "conformité à l'article 17. Le jour venu, c'est l'organisme "
               "notifié de l'évaluation de conformité qui l'appréciera",
    #  CELUI-LÀ NE SE CITERA JAMAIS AU JOURNAL OFFICIEL : c'est un guide de
    #  mise en œuvre de deux recommandations, pas une norme harmonisée. La
    #  réserve ne tombera pas avec le temps.
    "ocde": "ce guide est volontaire : il met en œuvre deux recommandations "
            "de l'OCDE et n'ouvre aucune présomption de conformité, à aucune "
            "date. Aucun organisme ne délivre d'attestation contre lui",
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
    # CARTOGRAPHIER N'EST PAS UNE CONFORMITÉ, et sa réserve doit le dire
    # autrement que les autres : il n'y a ici aucune autorité à satisfaire,
    # seulement un inventaire qui est exact ou ne l'est pas. Le vert y dit
    # « déclaré », et un inventaire complet de systèmes mal classés reste un
    # inventaire complet.
    "en18229_3": "personne ne la prononce encore : le projet n'est pas cité "
                 "au Journal officiel, donc le tenir n'ouvre aucune "
                 "présomption de conformité à l'article 14 — le jour où la "
                 "référence sera citée, le même travail vaudra présomption",
    "cartographier": "personne ne la prononce : ce n'est pas une "
                     "conformité mais un inventaire, et le vert y dit que "
                     "ce qu'un écran attend est déclaré — pas que la "
                     "déclaration est juste",
}


def reserve(norme):
    return ("Le vert de ce parcours dit que ce qu'un bloc attend est "
            "renseigné. Il ne dit pas que vous êtes en conformité : %s."
            % QUI_JUGE[norme])


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
           "saisie",
           "Les quatre exigences de l'objectif 16 — gouvernance, couverture, "
           "acceptation des risques résiduels, réexamen —, chacune « oui » "
           "ou « non », et ce que chaque « oui » engage.",
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
           "Le domaine d'application du SMSI (art. 4.3), les critères "
           "d'acceptation et leurs deux dates, puis chaque risque avec sa "
           "cotation, la propriété atteinte et son propriétaire.",
           "L'appréciation des risques de l'article 6.1.2 commande la "
           "déclaration d'applicabilité qui suit — et elle se conduit DANS "
           "un périmètre écrit.",
           "Les deux dates ne sont pas décoratives : sans elles, rien ne "
           "montre que les critères précèdent l'appréciation. Et tout ce "
           "que le périmètre n'exclut pas par écrit sera audité."),
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
    #  QUATRE BLOCS, ET L'ORDRE N'EST PAS CELUI DU DOCUMENT. Le processus
    #  vient en premier parce qu'il porte la QUALIFICATION : hors du champ de
    #  l'article 17, les trois autres écrans n'ont rien à mesurer. Puis le
    #  questionnaire, puis les deux lectures qui en découlent.
    #  LE PROCESSUS EN PREMIER, ET POUR UNE RAISON PLUS FORTE QUE L'ORDRE DU
    #  DOCUMENT : il porte les GROUPES, sans lesquels le questionnaire ne sait
    #  pas lesquels des 115 exemples visent ce client, et l'IMPLICATION, qui
    #  fixe le niveau de diligence attendu aux étapes 3 et 6.
    "ocde": (
        _b("processus", "ocde-processus",
           "Processus — groupes et implication", "saisie",
           "Les trois groupes d'acteur — ils ne sont ni rigides ni exclusifs "
           "—, l'implication dans l'incidence, et la priorisation sur quatre "
           "facteurs.",
           "L'implication COMMANDE le niveau de diligence attendu : causer "
           "oblige à faire cesser ET à réparer, contribuer à cesser sa part "
           "et construire son levier, être lié à user de ce levier. C'est "
           "elle qui plafonne le taux.",
           "Se ranger en « lien direct » et ne rien faire : le document écrit "
           "qu'un lien direct devient une CONTRIBUTION si l'entreprise "
           "continue sans agir."),
        _b("questionnaire", "ocde-questionnaire",
           "Questionnaire — les six étapes", "saisie",
           "Les exemples pratiques du document, par étape et par sous-étape. "
           "Seuls ceux qu'un de vos groupes vise entrent dans le calcul.",
           "Le poids suit la charge, pas le nombre d'exemples : l'étape 3 en "
           "porte vingt-quatre pour le seul groupe 2 et l'étape 6 n'en porte "
           "que deux — or c'est l'étape 6 qui est l'attente la plus forte dès "
           "que l'entreprise cause ou contribue.",
           "Lire ce taux comme une conformité. Le document déclare ses "
           "exemples non exhaustifs : ce qui se mesure ici s'appelle "
           "couverture des exemples retenus.",
           ("processus",)),
        _b("conformite", "ocde-conformite",
           "Conformité — feuilles de route", "lecture",
           "Les quatre-vingt-onze lignes de pont que le document donne "
           "lui-même vers vingt autres cadres.",
           "Les ponts viennent du DOCUMENT, pas du cabinet : c'est l'OCDE qui "
           "rapproche ses six étapes des dispositions de l'IA Act, d'ISO/IEC "
           "42001, du cadre du NIST et de dix-sept autres.",
           "En faire une équivalence. Le document écrit que ce n'est pas un "
           "cadre d'équivalence — et sur ces vingt cadres, Sentinel en mesure "
           "trois.",
           ("questionnaire",)),
        _b("analyse", "ocde-analyse",
           "Analyse — licence et limites", "lecture",
           "La source, sa licence CC BY 4.0 et les deux mentions qu'elle "
           "impose, ce que le document s'exclut lui-même, et ce que ce module "
           "refuse de dire.",
           "Une première dans Sentinel : une source qu'on peut citer, "
           "traduire et adapter — là où les textes du CEN et de l'ISO "
           "n'existent ici que par leurs numéros et leurs titres.",
           "Croire que la licence autorise tout : le matériel de tiers en est "
           "exclu, et le logo comme l'identité visuelle de l'OCDE sont "
           "interdits.",
           ("conformite",)),
    ),
    "en18286": (
        _b("processus", "en18286-processus",
           "Processus — stratégie §4.4", "saisie",
           "La qualification, les cinq composantes de la stratégie du §4.4, "
           "et l'approche retenue pour chacune des sept exigences "
           "essentielles.",
           "C'est la pièce que ni ISO 9001 ni ISO/IEC 42001 ne donnent, et "
           "celle que l'organisme notifié ouvre en premier. L'approche "
           "retenue COMMANDE la charge de preuve : « autre norme » et "
           "« autre solution » réclament, en plus, ce qui n'est pas couvert, "
           "la justification et la preuve objective.",
           "Cocher « autre solution technique » sans ces trois pièces ne "
           "laisse pas une exigence à moitié tenue : cela plafonne le taux, "
           "parce que le §4.4.3.2.2 l'exige."),
        _b("questionnaire", "en18286-questionnaire",
           "Questionnaire — chap. 4 à 10", "saisie",
           "Les soixante-cinq paragraphes normatifs, du système de "
           "management à l'évaluation des performances.",
           "Le taux par part s'en déduit, et le poids suit la charge "
           "réglementaire : le chapitre 4 pèse trois fois le chapitre 10.",
           "Un paragraphe « sans objet » sort du calcul ; un paragraphe sans "
           "réponse compte pour zéro. L'inverse ferait monter le taux à "
           "mesure qu'on répond MOINS.",
           ("processus",)),
        _b("conformite", "en18286-conformite",
           "Conformité — annexe ZA", "lecture",
           "L'article 17 alinéa par alinéa, et le paragraphe de la norme qui "
           "le couvre.",
           "C'est la seule vue qui dise ce que le travail fait COUVRE du "
           "règlement, et non ce qu'il couvre de la norme.",
           "L'annexe ZA porte une ligne « Non couvert » — l'article 17(2). "
           "Cent pour cent ici ne veut donc pas dire article 17 tenu.",
           ("questionnaire",)),
        _b("analyse", "en18286-analyse",
           "Analyse — ponts et famille", "lecture",
           "Ce qu'un certificat ISO 9001 ou ISO/IEC 42001 apporte déjà, ce "
           "qu'il n'apporte PAS, et les autres normes harmonisées de la "
           "famille.",
           "Les deux tables de correspondance se lisent à l'envers : ce qui "
           "compte, ce sont les DEUX lignes en face du vide.",
           "prEN 18286 organise la façon de répondre aux exigences "
           "essentielles ; ce sont les AUTRES normes de la famille qui "
           "disent comment y répondre.",
           ("questionnaire",)),
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
        _b("genai", "nist-genai", "Profil IA générative", "saisie",
           "Le système est-il génératif, lesquels des douze risques "
           "s'appliquent, et lesquelles des 211 actions suggérées du §3 "
           "sont tenues.",
           "Ce bloc NE S'AJOUTE PAS au profil : il le PLAFONNE. Une "
           "catégorie « prouvée » sur le cadre ne l'est plus pour un "
           "système génératif si les actions du profil n'y sont pas "
           "tenues.",
           "Déclarer le système génératif sans retenir un seul risque "
           "revient à dire que la génération n'apporte rien — c'est la "
           "réponse qu'un auditeur ouvrira en premier.",
           ("profil",)),
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
    #  L'ORDRE N'EST PAS CELUI DE LA NORME, C'EST CELUI DU TRAVAIL : on ne
    #  répond pas au cadre d'analyse avant de savoir à quel rôle on répond, et
    #  on ne juge pas l'adéquation d'une mesure avant d'avoir posé le délai
    #  qu'elle doit tenir.
    "en18229_3": (
        _b("role", "en18229-role", "Rôle et périmètre", "saisie",
           "Fournisseur, déployeur, ou les deux — et si le système identifie "
           "des personnes à distance par la biométrie.",
           "La norme adresse ses exigences au fournisseur et transmet au "
           "déployeur par la notice : le questionnaire, les verrous et le "
           "score dépendent du rôle.",
           "Un organisme qui conçoit ET exploite porte les deux jeux "
           "d'obligations : le score retenu est celui du plus faible des "
           "deux."),
        _b("scenarios", "en18229-scenarios", "Scénarios et délais", "saisie",
           "Un scénario de risque, son délai de réaction, la catégorie de "
           "mesure retenue et la latence d'intervention mesurée.",
           "C'est la seule partie du cadre qui se CALCULE : la latence "
           "déclarée contre le délai déclaré.",
           "Un scénario dont la latence dépasse le délai sans consignation de "
           "l'impossibilité technique plafonne le score — aucune réponse au "
           "questionnaire ne lève ce verrou.",
           prerequis=("role",)),
        _b("cadre", "en18229-cadre", "Cadre d’analyse", "saisie",
           "Les questions de votre rôle, paragraphe par paragraphe.",
           "C'est ce que le score compte, et ce que le plan d'action reprend "
           "ligne par ligne.",
           "Les questions de la section RBI n'apparaissent que si vous avez "
           "déclaré un système d'identification biométrique à distance.",
           prerequis=("role",)),
        _b("score", "en18229-score", "Score et article 14", "lecture",
           "Le score, ses plafonds, la documentation exigée et la couverture "
           "de l'article 14 alinéa par alinéa.",
           "C'est la restitution : rien ne s'y saisit, tout y est dérivé de "
           "ce qui précède.",
           "Le vert ne vaut pas présomption de conformité : le projet n'est "
           "pas encore cité au Journal officiel.",
           prerequis=("cadre",)),
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
        _b("aipd", "rgpd-aipd", "AIPD (art. 35)", "saisie",
           "Pour chaque traitement : une réponse à chacun des neuf critères, "
           "puis, dès que deux sont réunis, la gravité et la vraisemblance "
           "de trois événements redoutés.",
           "Deux critères réunis rendent l'AIPD obligatoire (article 35).",
           "Un critère sans réponse n'est pas un « non » : tant qu'il en "
           "reste un, l'AIPD ne peut pas être dite « non requise ».",
           ("traitements",)),
        _b("pbd", "rgpd-pbd", "Privacy by design", "saisie",
           "Les contrôles de l'article 25 — minimisation, droits, "
           "sous-traitance, réexamen —, chacun « oui », « non » ou « sans "
           "objet ».",
           "La protection des données se conçoit avant la mise en "
           "production, pas après.",
           "« Sans objet » sort le contrôle du calcul ; « non » l'y laisse, "
           "à zéro. Les confondre flatte le taux."),
        _b("doc", "rgpd-doc", "Politique documentaire", "saisie",
           "Les documents d'accountability, chacun avec un statut choisi — "
           "« absent » compris.",
           "L'article 5, paragraphe 2, fait de la documentation la preuve "
           "de la conformité.",
           "« Absent » est une réponse, et compte au dénominateur ; un "
           "document sans statut n'a pas encore été regardé."),
        _b("sensibilisation", "rgpd-sensibilisation", "Sensibilisation",
           "saisie",
           "Le plan de sensibilisation, public par public : l'état de "
           "chaque action, choisi.",
           "Une mesure organisationnelle qui ne se forme pas ne se tient "
           "pas.",
           "« À planifier » est une réponse ; une action sans état n'a pas "
           "encore été regardée."),
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
        _b("audit", "audit-ia-act", "Audit IA Act", "saisie",
           "Les trente-quatre points de contrôle de l'audit, en huit "
           "sections, des pratiques interdites aux modèles à usage général "
           "— chacun avec une réponse.",
           "C'est l'audit que le taux de conformité de l'IA Act lit.",
           "« À réaliser » est une réponse, qui compte à zéro ; « sans "
           "objet » sort le point du calcul ; un point sans réponse n'a "
           "pas encore été regardé."),
    ),
    # ═══════════════════════════════════════════════════════════════════
    #  CARTOGRAPHIER — LE PARCOURS QUI N'EN ÉTAIT PAS UN
    # ═══════════════════════════════════════════════════════════════════
    # CE N'EST PAS UN RÉFÉRENTIEL, et il entre pourtant ici. Mesuré au
    # navigateur : les sept onglets de « Cartographier » ne portaient aucun
    # attribut de parcours — zéro puce, zéro vert, zéro étape courante,
    # aucun passage au suivant — quand les onze référentiels les avaient
    # tous. Le client ne savait donc ni où il en était, ni quoi ouvrir
    # ensuite, dans la section qui commence tout le reste.
    #
    # L'ORDRE EST CELUI DE LA BARRE, et il raconte une méthode : on
    # découvre ce qui existe déjà (Shadow AI), on classe un système
    # (Simulateur), on l'inscrit (Registre) — et le registre est la SOURCE
    # de tout ce qui suit. La qualification assistée lit ses lignes, le
    # FinOps et l'Empreinte lisent ses volumes. Ces trois-là sont donc
    # VERROUILLÉS tant que le registre n'est pas fait, et le disent : c'est
    # précisément ce qui manquait à qui ouvrait le FinOps et n'y trouvait
    # aucun chiffre. L'audit de maturité, lui, ne lit rien et n'est lu par
    # personne — il reste libre.
    "cartographier": (
        _b("shadow", "shadow-ai", "Découverte Shadow AI", "lecture",
           "Les usages d'IA déjà en place que personne n'a déclarés, cas "
           "par cas, et ce qu'il faut en faire.",
           "On ne cartographie pas ce qu'on ignore : cet écran donne la "
           "liste des endroits où regarder avant de déclarer quoi que ce "
           "soit.",
           "Rien ne s'y saisit : il se marque lu, et « lu » n'est pas vert."),
        _b("simulateur", "simulateur", "Simulateur IA Act", "saisie",
           "La classification d'un système au sens du règlement : son "
           "niveau de risque, l'article qui le fonde, et les obligations "
           "qui en découlent.",
           "C'est la classification que le registre reprend, et que le "
           "FinOps range par niveau de risque.",
           "Un système classé ne rejoint le registre que si l'on clique "
           "« Ajouter au Registre IA » : la classification seule ne "
           "déclare rien."),
        _b("registre", "registre", "Registre IA", "saisie",
           "L'inventaire des systèmes d'IA : leur finalité, leur service, "
           "leur classification, et les huit champs de coût et d'empreinte.",
           "C'EST LA SOURCE. La qualification assistée, le FinOps et "
           "l'Empreinte ne tiennent aucun inventaire à eux : ils lisent "
           "celui-ci.",
           "Un système inscrit mais incomplet compte pour un système : les "
           "dix questions essentielles décident, pas la ligne."),
        _b("qualification", "qualif-assistee", "Qualification assistée",
           "saisie",
           "Une proposition de classification par système non classé, avec "
           "ses indices, à valider ou à écarter par une personne nommée.",
           "Elle traite en lot ce que le simulateur fait un par un.",
           "Le moteur PROPOSE : rien n'est écrit au registre sans une "
           "décision et le nom de qui l'a prise.",
           prerequis=("registre",)),
        _b("finops", "finops", "FinOps IA", "saisie",
           "Ce que coûte le parc déclaré : couverture du chiffrage, "
           "montants par niveau de risque, attribution, leviers.",
           "Un montant dont on ne peut pas dire d'où vient le volume n'est "
           "pas opposable en comité.",
           "Rien ne se saisit ici : les huit champs se remplissent sur la "
           "fiche du système, au Registre. Un système sans volume déclaré "
           "ne coûte pas zéro — personne n'a encore dit ce qu'il consomme.",
           prerequis=("registre",)),
        _b("empreinte", "empreinte-ia", "Empreinte IA du parc", "saisie",
           "Ce que pèse le parc déclaré : électricité, CO₂e, eau, et la "
           "trajectoire à l'horizon retenu.",
           "Le même volume déclaré donne le coût et l'empreinte : on ne "
           "tient pas deux inventaires.",
           "Rien ne se saisit ici non plus : le volume vient de la fiche "
           "du système, au Registre.",
           prerequis=("registre",)),
        _b("maturite", "maturite", "Audit de maturité IA", "saisie",
           "Les huit piliers de la maturité IA, deux questions chacun, sur "
           "une échelle Non / Partiel / Oui.",
           "C'est le seul écran de cette section qui juge l'ORGANISATION "
           "et non les systèmes.",
           "« Pas encore répondu » n'est pas « Non » : le score porte sur "
           "les réponses reçues, et le compteur dit sur combien."),
    ),
}

# ── LES PARCOURS QUI NE SONT PAS DES RÉFÉRENTIELS DE CONFORMITÉ ───────────
# « CARTOGRAPHIER » EST UN INVENTAIRE, PAS UNE NORME. Il a un rail — sept
# écrans dans un ordre, avec des prérequis — mais pas de taux de conformité,
# pas de couleur de référentiel dans la barre, pas de traducteur vers le
# moteur de conformité, et personne ne prononce sa validité. Les gardes qui
# parcourent BLOCS pour vérifier qu'une norme est traduite, colorée, chiffrée
# et mémorisée lisent CETTE table pour savoir qui n'y est pas soumis — au lieu
# de porter chacune sa propre liste d'exceptions, qui dériveraient.
HORS_CONFORMITE = frozenset({"cartographier"})

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


def _repondu(v):
    """UNE RÉPONSE, C'EST UNE VALEUR CHOISIE. Ni `None`, ni la chaîne vide :
    ce sont les deux formes que prend « non renseigné » à l'écran."""
    return v is not None and v != ""


def _liste(d, cle):
    """Une liste de l'écran, telle qu'il l'envoie : [{cle, nom, reponse}].

    LES QUESTIONS VIENNENT DE L'ÉCRAN, qui les tient déjà et les affiche.
    Les recopier ici ferait deux listes, et la première divergence ferait
    valider un bloc sur une question que l'écran ne pose plus — ou manquer
    celle qu'il pose. Une règle de la suite exécute le collecteur et vérifie
    qu'il envoie la liste ENTIÈRE."""
    v = d.get(cle)
    return [x for x in v if isinstance(x, dict)] if isinstance(v, list) else []


def _sans_reponse(d, cle, faute):
    """Les questions d'une liste restées sans réponse, par leur nom.

    UNE LISTE ABSENTE N'EST PAS UNE LISTE COMPLÈTE : elle n'a rien à
    montrer, et le bloc le dit au lieu de passer au vert sur rien."""
    l = _liste(d, cle)
    if not l:
        return [_q(faute)]
    return [_q(str(x.get("nom") or x.get("cle") or "(question sans nom)"))
            for x in l if not _repondu(x.get("reponse"))]


#: DEUX CRITÈRES RÉUNIS RENDENT L'AIPD OBLIGATOIRE — c'est le seuil que
#: l'écran applique pour dire « AIPD requise », et une règle vérifie que
#: les deux lisent le même.
AIPD_SEUIL = 2
AIPD_NIVEAUX = (1, 2, 3, 4)


def _manque_aipd(traitements):
    """Pour chaque traitement : les neuf critères, puis — dès que le seuil
    est atteint — la gravité et la vraisemblance de chaque événement.

    UN CRITÈRE SANS RÉPONSE N'EST PAS UN « NON ». Tant qu'il en reste un,
    l'AIPD n'est ni « requise » ni « non requise » : elle n'est pas finie.
    Et les événements ne sont demandés qu'à qui doit une AIPD — les exiger
    de tous ferait coter des risques qu'aucune analyse n'a à apprécier."""
    m = []
    for t in traitements:
        nom = str(t.get("nom") or "(sans nom)")
        a = _dict(t, "aipd")
        crit = [c for c in (a.get("criteres") or []) if isinstance(c, dict)]
        if not crit:
            m.append(_q("« %s » : les critères de l'AIPD" % nom))
            continue
        vides = [c for c in crit if c.get("reponse") not in (True, False)]
        for c in vides:
            m.append(_q("« %s » : %s" % (nom, c.get("nom") or "critère")))
        if sum(1 for c in crit if c.get("reponse") is True) < AIPD_SEUIL:
            continue
        evs = [e for e in (a.get("evenements") or []) if isinstance(e, dict)]
        if not evs:
            m.append(_q("« %s » : les événements redoutés" % nom))
        for e in evs:
            if e.get("g") not in AIPD_NIVEAUX or e.get("v") not in AIPD_NIVEAUX:
                m.append(_q("« %s » : gravité et vraisemblance — %s"
                            % (nom, e.get("nom") or "événement")))
    return m


#: LES RÉPONSES QUE L'AUDIT IA ACT ACCEPTE. « none » — la valeur d'un point
#: jamais touché — n'en est pas une.
AUDIT_REPONSES = ("done", "partial", "todo", "na")


def _manque_analyse_recyf(a):
    """L'objectif 16, question par question — et ce que chaque « oui »
    engage, puisque le référentiel l'exige avec lui."""
    m = []
    entrees = _dict(a, "entrees")
    for cle, ref, titre, _dit, _piege in nis2_recyf.ANALYSE_EXIGENCES:
        v = a.get(cle)
        if v not in (True, False):
            m.append(_q("%s — %s" % (ref, titre)))
            continue
        if not v:
            continue
        if cle == "gouvernance" and a.get("moyens_alloues") not in (True, False):
            m.append(_q("%s — des moyens sont-ils alloués ?" % ref))
        if cle == "couverture":
            for c, nom in nis2_recyf.ANALYSE_ENTREES:
                if entrees.get(c) not in (True, False):
                    m.append(_q("%s — l'analyse cite-t-elle : %s ?" % (ref, nom)))
        if cle == "acceptation":
            if a.get("risques_residuels_acceptes") not in (True, False):
                m.append(_q("%s — les risques résiduels sont-ils explicitement "
                            "acceptés ?" % ref))
            if a.get("plan_date_et_responsable") not in (True, False):
                m.append(_q("%s — chaque action du plan a-t-elle une échéance "
                            "et un responsable ?" % ref))
        if cle == "reexamen" and not _nombre(a.get("dernier_reexamen_mois")):
            m.append(_q("%s — le dernier réexamen, en mois" % ref))
    return m


#: LA RÉPONSE « AUCUNE DES DEUX ANNEXES ». Sans elle, la liste des secteurs
#: n'offrait pour première option qu'un « — aucun secteur des annexes I ou
#: II — » dont la valeur était VIDE — celle-là même d'une question laissée
#: sans réponse. Le moteur de qualification lit toute clé hors des annexes
#: comme un secteur déclaré hors champ ; celle-ci en est une.
SECTEUR_HORS_ANNEXES = "hors_annexes"

NIS2_PORTES = set(nis2.HORS_TAILLE_PAR_CLE) | set(nis2.ESSENTIELLE_HORS_TAILLE)


def qualification_nis2(d):
    """Ce qui manque pour que la qualification soit PRONONCÉE, et le verdict.

    UNE QUALIFICATION VIDE REND DÉJÀ « HORS CHAMP » — mesuré sur le moteur :
    sans secteur, il répond « Aucun secteur déclaré ». Le rail ne peut donc
    pas lire le verdict pour savoir si la question a reçu une réponse ; il
    lit la DÉCLARATION.

    PUBLIQUE, PARCE QUE LE TAUX DE CONFORMITÉ LA LIT AUSSI. Deux lectures de
    « la qualification est-elle faite ? » finiraient par se contredire : le
    rail dirait le bloc vert pendant que le taux réserverait « entité non
    qualifiée », ou dirait « hors champ » sur un formulaire à moitié rempli."""
    manque = []
    portes = [c for c in NIS2_PORTES if d.get(c)]
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
    manque["qualifier"], verdict = qualification_nis2(d)

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
        manque["recyf_analyse"] = _manque_analyse_recyf(_dict(recyf, "analyse"))
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
    # LE PÉRIMÈTRE D'ABORD, parce que le moteur le lit d'abord : sans lui, son
    # évaluation s'arrête à « perimetre_absent », et le taux de conformité
    # plafonne la norme à ce seul verrou. Un bloc vert au-dessus d'un taux
    # verrouillé par ce qu'il n'a pas demandé serait la contradiction même
    # que le rail et le taux ne doivent plus se faire.
    if not str(d.get("perimetre") or "").strip():
        m.append(_q("Le domaine d'application du SMSI (art. 4.3)"))
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


def _en18286(d):
    """Ce qui manque à chacun des deux blocs de saisie.

    LE PROCESSUS SE VALIDE SUR LA QUALIFICATION ET LA STRATÉGIE, pas sur le
    questionnaire : ce sont deux blocs, et confondre leurs manques ferait
    rougir le premier pour une réponse attendue dans le second.

    HORS CHAMP, TOUT DEVIENT SANS OBJET. Un déployeur qui vient de se
    déclarer tel a RÉPONDU : lui laisser soixante-cinq questions en attente
    serait lui vendre un chantier que l'article 17 ne lui impose pas.
    """
    qual = _dict(d, "qualification")
    manque = {}
    champ = en18286.applicable({"qualification": qual})
    if champ.get("ok") is None:
        #  LES DEUX QUESTIONS SONT NOMMÉES SÉPARÉMENT, et seule celle qui
        #  manque est demandée : dire « qualifiez-vous » à qui vient de
        #  répondre à la moitié ne lui apprend pas laquelle il reste.
        attente = []
        if qual.get("fournisseur") is None:
            attente.append(_q("Êtes-vous FOURNISSEUR du système — celui qui "
                              "le met sur le marché ou en service sous son "
                              "nom ? L'article 17 ne vise que lui."))
        if qual.get("haut_risque") is None:
            attente.append(_q("Le système est-il à HAUT RISQUE au sens de "
                              "l'annexe III ou de l'article 6 ? C'est cette "
                              "qualification qui déclenche l'article 17."))
        manque["processus"] = attente
        manque["questionnaire"] = []
        return manque, {}, {}
    if champ.get("ok") is False:
        #  SANS OBJET, ET NON « À FAIRE » : la qualification déclarée écarte
        #  la norme, et le rail doit le dire plutôt que de laisser quatre
        #  blocs bleus.
        #  ET IL PART EN DEUXIÈME POSITION, PAS EN TROISIÈME. Mesuré :
        #  `avancement` lit `(manque, sans_objet, contexte)` ; rendu en
        #  troisième, ce dictionnaire atterrissait dans le CONTEXTE, que rien
        #  ne lit — et les quatre blocs d'un déployeur hors champ repassaient
        #  « validée » et « courante », c'est-à-dire du travail à faire.
        so = {b["cle"]: "L'article 17 vise le fournisseur d'un système d'IA "
                        "à haut risque : hors de cette qualification, il n'y "
                        "a rien à mesurer ici."
              for b in BLOCS["en18286"]}
        return {}, so, {}

    st = en18286.strategie(d)
    attente = [_q("Stratégie de conformité : « %s »" % c["nom"])
               for c in st["composantes"] if not c["declaree"]]
    for ligne in st["lignes"]:
        if ligne["etat"] == "sans_approche":
            attente.append(_q("Exigence essentielle « %s » (%s) : aucune "
                              "approche retenue"
                              % (ligne["nom"], ligne["article"])))
        elif ligne["etat"] == "a_prouver":
            attente.append(_q("Exigence essentielle « %s » : l'approche "
                              "retenue réclame encore %d pièce(s) du "
                              "§4.4.3.2.2"
                              % (ligne["nom"], len(ligne["manque"]))))
    manque["processus"] = attente

    reponses = _dict(d, "reponses")
    manque["questionnaire"] = [
        _q("%s %s" % (p["num"], p["titre"]))
        for p in en18286.PARAGRAPHES
        if reponses.get(p["num"]) not in en18286.ETATS]
    return manque, {}, {}


def _ocde(d):
    """Ce qui manque aux deux blocs de saisie de la diligence OCDE.

    IL N'Y A PAS DE HORS-CHAMP ICI, et c'est une différence de fond avec les
    treize autres : ce guide n'écarte personne. Toute entreprise de la chaîne
    de valeur de l'IA est attendue sur la diligence, les PME comprises — le
    document le dit, et ajoute seulement que la mesure se proportionne. Le
    rail ne rend donc JAMAIS « sans objet » pour cette norme.

    LE PROCESSUS SE VALIDE SUR LES GROUPES, L'IMPLICATION ET LA PRIORISATION,
    pas sur le questionnaire. Confondre les deux ferait rougir le premier pour
    une réponse attendue dans le second.
    """
    qual = _dict(d, "qualification")
    groupes = ocde_ia.groupes_declares({"qualification": qual})
    attente = []
    if not groupes:
        attente.append(_q("Quel ou quels GROUPES d'acteur votre organisme "
                          "occupe-t-il dans la chaîne de valeur de l'IA ? Ils "
                          "ne sont ni rigides ni exclusifs : déclarez-en "
                          "autant que nécessaire."))
    if ocde_ia.implication_declaree({"qualification": qual}) is None:
        attente.append(_q("Votre IMPLICATION dans l'incidence : la causez-vous, "
                          "y contribuez-vous, ou y êtes-vous lié par une "
                          "relation d'affaires ? C'est elle qui fixe le niveau "
                          "de diligence attendu."))
    pr = ocde_ia.priorisation(d)
    if not pr["renseignee"]:
        attente.append(_q("La PRIORISATION de l'étape 2.4 : coter les risques "
                          "sur l'échelle, la portée, l'irrémédiabilité et la "
                          "probabilité."))
    else:
        for cle in pr["incompletes"]:
            attente.append(_q("Risque « %s » : un facteur au moins n'est pas "
                              "coté — trois sur quatre ne font pas une "
                              "priorisation" % cle))
        for cle in pr["sans_justification"]:
            attente.append(_q("Risque « %s » : coté sans justification écrite, "
                              "et le document exige un processus crédible"
                              % cle))
    manque = {"processus": attente}

    #  LE QUESTIONNAIRE NE RÉCLAME QUE LES EXEMPLES RETENUS, et il ne les
    #  liste pas un à un : cent quinze lignes rendraient le rail illisible.
    #  Il réclame par ÉTAPE, comme le profil du NIST réclame par
    #  sous-catégorie.
    reponses = _dict(d, "reponses")
    retenus, _ = ocde_ia.exemples_retenus(groupes)
    reste = []
    for et in ocde_ia.ETAPES:
        n = len([e for e in retenus
                 if ocde_ia.UNITES_PAR_CLE[e["unite"]]["etape"] == et["num"]
                 and reponses.get(e["cle"]) not in ocde_ia.ETATS])
        if n:
            reste.append(_q("Étape %d « %s » : %d exemple(s) sans réponse"
                            % (et["num"], et["nom"], n)))
    manque["questionnaire"] = reste
    return manque, {}, {}


def _nist_ai_rmf(d):
    """Deux blocs de saisie : le cadre, puis le profil qui le plafonne.

    LE PROFIL NE RÉCLAME PAS 211 RÉPONSES, ET IL NE LE POURRAIT PAS. Il
    réclame la qualification, les risques retenus, puis — par SOUS-CATÉGORIE
    et non par action — celles où il reste une action sans réponse. Lister
    les actions une à une aurait rendu un rail de cent cinquante lignes que
    personne ne lit ; nommer la sous-catégorie dit où aller, ce qui est le
    seul travail du rail.
    """
    etats = _dict(d, "etats")
    manque = {"profil": [_q("%s — %s" % (c["cle"], c["nom"]))
                         for c in nist_ai_rmf.CATEGORIES
                         if etats.get(c["cle"]) not in nist_ai_rmf.ETATS]}

    profil = _dict(d, "profil")
    genai = profil.get("genai")
    if genai is not True and genai is not False:
        # NI « OUI » NI « NON » : la question n'a pas été posée. La ranger du
        # côté de « non » aurait validé le bloc sans que personne n'ait
        # qualifié le système — et « non » est précisément la réponse qui ne
        # plafonne rien.
        manque["genai"] = [_q("Le système est-il génératif ? AI 600-1 ne "
                              "s'applique qu'à l'IA générative.")]
        return manque, {}, {}
    if not genai:
        manque["genai"] = []
        return manque, {}, {}

    retenus = nist_genai.risques_declares(profil.get("risques"))
    if not retenus:
        manque["genai"] = [_q("Au moins un des douze risques du profil — ou "
                              "la décision assumée qu'aucun ne s'applique à "
                              "ce système génératif.")]
        return manque, {}, {}

    actions = profil.get("actions") if isinstance(profil.get("actions"), dict) \
        else {}
    attente = []
    for sc in (a["sous_categorie"] for a in
               (nist_genai.ACTIONS_PAR_CODE[c]
                for c in nist_genai.applicables(retenus))):
        if sc not in attente:
            attente.append(sc)
    reste = []
    for sc in attente:
        ouvertes = [c for c in nist_genai.PAR_SOUS_CATEGORIE[sc]
                    if c in set(nist_genai.applicables(retenus))
                    and actions.get(c) not in nist_genai.ETATS_ACTION]
        if ouvertes:
            reste.append(_q("%s — %d action(s) du profil sans réponse"
                            % (sc, len(ouvertes))))
    manque["genai"] = reste
    return manque, {}, {}


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
    return {"traitements": m,
            "aipd": _manque_aipd([t if isinstance(t, dict) else {}
                                  for t in traitements]),
            "pbd": _sans_reponse(d, "pbd", "La liste des contrôles de la "
                                 "privacy by design n'a pas été transmise"),
            "doc": _sans_reponse(d, "doc", "La liste des documents n'a pas "
                                 "été transmise"),
            "sensibilisation": _sans_reponse(
                d, "sensibilisation", "Le plan de sensibilisation n'a pas "
                "été transmis")}, {}, {}


def _ia_act(d):
    """Les trente-quatre points, chacun avec une réponse.

    LA LISTE VIENT DE L'ÉCRAN — la même règle que pour les listes RGPD ; les
    réponses viennent de l'audit, tel que l'écran le garde."""
    points = _liste(d, "points")
    if not points:
        return {"audit": [_q("La liste des points de l'audit n'a pas été "
                             "transmise")]}, {}, {}
    audit = _dict(d, "audit")
    return {"audit": [_q(str(p.get("titre") or p.get("cle")))
                      for p in points
                      if audit.get(p.get("cle")) not in AUDIT_REPONSES]}, {}, {}


def _cartographier(d):
    """CE QUE CHAQUE ÉCRAN DE « CARTOGRAPHIER » ATTEND, ET CE QUI LUI MANQUE.

    AUCUN DE CES SEUILS N'EST INVENTÉ ICI : chacun est celui que l'écran
    applique déjà. Les dix questions essentielles sont celles du registre
    (Hub France IA) ; la couverture du chiffrage est celle du moteur FinOps ;
    la couverture des volumes est celle du moteur d'empreinte ; le lot à
    qualifier est celui que le serveur constitue — « les systèmes non
    classés ». Un seuil réinventé ici et l'écran dirait une chose, le rail
    une autre.
    """
    manque, sans_objet = {}, {}

    # ── LE SIMULATEUR : une classification, pas un formulaire commencé ──
    sim = _dict(d, "simulateur")
    if not _repondu(sim.get("nom")):
        manque.setdefault("simulateur", []).append(
            _q("Nommez le système, puis déroulez les quatre étapes"))
    for cle, quoi in (("secteur", "Choisissez le secteur d'usage"),
                      ("type", "Choisissez le type de système")):
        if not _repondu(sim.get(cle)):
            manque.setdefault("simulateur", []).append(_q(quoi))
    if not _repondu(sim.get("niveau")):
        manque.setdefault("simulateur", []).append(
            _q("Terminez les quatre étapes : la classification n'est pas "
               "encore rendue"))

    # ── LE REGISTRE : au moins un système, et chacun complet ──
    reg = _dict(d, "registre")
    systemes = reg.get("systemes")
    systemes = systemes if isinstance(systemes, list) else []
    if not systemes:
        manque.setdefault("registre", []).append(
            _q("Aucun système déclaré — le FinOps, l'Empreinte et la "
               "qualification assistée lisent tous ce registre"))
    else:
        for x in systemes:
            if not isinstance(x, dict):
                continue
            if not _nombre(x.get("completude")) or x.get("completude") < 100:
                manque.setdefault("registre", []).append(
                    _q("« %s » : les dix questions essentielles ne sont pas "
                       "toutes renseignées" % (x.get("nom") or "(sans nom)")))

    # ── LA QUALIFICATION ASSISTÉE : plus rien à classer ──
    qual = _dict(d, "qualification")
    restants = qual.get("a_qualifier")
    if not isinstance(restants, int):
        manque.setdefault("qualification", []).append(
            _q("Ouvrez l'écran : le lot à qualifier n'a pas encore été "
               "demandé au moteur"))
    elif restants > 0:
        manque.setdefault("qualification", []).append(
            _q("%d système(s) du registre n'ont pas de classification — "
               "proposez, puis décidez" % restants))

    # ── LE FINOPS ET L'EMPREINTE : ils ne se remplissent pas chez eux ──
    # LEUR « MANQUE » NOMME LES SYSTÈMES ET L'ÉCRAN OÙ LES REMPLIR. Dire
    # « la couverture est à 0 % » sans dire où saisir laisse exactement la
    # question qui a été posée : on ne sait pas quelles données choisir.
    fo = _dict(_dict(d, "finops"), "couverture")
    fo_total, fo_ok = fo.get("total"), fo.get("instruites")
    if not _nombre(fo_total):
        manque.setdefault("finops", []).append(
            _q("Ouvrez l'écran : le chiffrage n'a pas encore été demandé"))
    elif fo_total and fo_ok != fo_total:
        for nom in (fo.get("non_chiffres") or [])[:12]:
            manque.setdefault("finops", []).append(
                _q("« %s » : renseignez le modèle, l'unité de facturation, "
                   "les volumes du mois et leur source — Registre IA → "
                   "fiche du système" % nom))
        if not manque.get("finops"):
            manque["finops"] = [_q(
                "%s ligne(s) sur %s ne sont pas chiffrées — les huit champs "
                "se saisissent au Registre, sur la fiche du système"
                % (int(fo_total) - int(fo_ok or 0), int(fo_total)))]

    emp = _dict(_dict(d, "empreinte"), "couverture")
    emp_total, emp_ok = emp.get("systemes"), emp.get("chiffrable")
    if not _nombre(emp_total):
        manque.setdefault("empreinte", []).append(
            _q("Ouvrez l'écran : l'empreinte n'a pas encore été demandée"))
    elif emp_total and emp_ok != emp_total:
        for nom in (emp.get("volume_manquant") or [])[:12]:
            manque.setdefault("empreinte", []).append(
                _q("« %s » : renseignez le volume de sortie du mois — "
                   "Registre IA → fiche du système" % nom))
        if not manque.get("empreinte"):
            manque["empreinte"] = [_q(
                "%s système(s) sur %s sans volume déclaré — il se saisit au "
                "Registre" % (int(emp_total) - int(emp_ok or 0), int(emp_total)))]

    # ── L'AUDIT DE MATURITÉ : les seize questions ──
    mat = _dict(d, "maturite")
    rep, tot = mat.get("repondues"), mat.get("total")
    if not _nombre(tot) or not tot:
        manque.setdefault("maturite", []).append(
            _q("Ouvrez l'écran : les huit piliers n'ont pas encore été "
               "présentés"))
    elif rep != tot:
        manque.setdefault("maturite", []).append(
            _q("%s question(s) sur %s sans réponse — « pas encore répondu » "
               "n'est pas « Non »" % (int(tot) - int(rep or 0), int(tot))))

    return manque, sans_objet, {}


def _en18229_3(d):
    """CE QUE CHAQUE ÉCRAN DE prEN 18229-3 ATTEND, ET CE QUI LUI MANQUE.

    AUCUN SEUIL N'EST RÉINVENTÉ ICI : le rail lit le moteur. Le rôle vient de
    la déclaration, l'adéquation des scénarios du calcul du moteur, et
    l'avancement du cadre du compte de ses propres exigences applicables.
    """
    import en18229_3 as _en
    manque, sans_objet = {}, {}

    # ── LE RÔLE : il commande le reste, donc il vient en premier ──────────
    roles = [r for r in ("fournisseur", "deployeur")
             if isinstance(d.get(r), dict) and d[r]]
    if not roles:
        manque.setdefault("role", []).append(
            _q("Choisissez votre rôle — fournisseur, déployeur, ou les deux — "
               "et répondez à son questionnaire"))
    if d.get("rbi") is None:
        manque.setdefault("role", []).append(
            _q("Dites si le système identifie des personnes à distance par la "
               "biométrie : neuf exigences en dépendent"))

    # ── LES SCÉNARIOS : au moins un, et chacun doit tenir son délai ───────
    scs = [x for x in (d.get("scenarios") or []) if isinstance(x, dict)]
    if not scs:
        manque.setdefault("scenarios", []).append(
            _q("Déclarez au moins un scénario de risque avec son délai de "
               "réaction : c'est lui qui commande le choix des mesures"))
    else:
        for x in scs:
            r = _en.scenario(x)
            if r["etat"] in ("tient", "impossible_consignee"):
                continue
            for m in (r["manque"] or []):
                manque.setdefault("scenarios", []).append(
                    _q("« %s » : %s" % (r["nom"] or "sans nom", m)))

    # ── LE CADRE : les exigences applicables du rôle, sans réponse ────────
    rbi = bool(d.get("rbi"))
    notif = d.get("notifications_fournisseur")
    notif = True if notif is None else bool(notif)
    for role in (roles or []):
        rep = d.get(role) or {}
        for ex in _en.applicables(role, rbi, notif):
            if _en._valeur(rep.get(ex["cle"])) is None:
                manque.setdefault("cadre", []).append(
                    _q("%s %s (%s) — sans réponse"
                       % (ex["clause"], ex["titre"],
                          _en.ROLES[role]["nom"].lower())))

    # ── LE SCORE : un écran de lecture, qui a besoin du reste ─────────────
    if not roles or not scs:
        sans_objet["score"] = ("Le score se calcule sur un rôle et au moins "
                               "un scénario de risque.")

    #  LE CONTEXTE QUE LE BANDEAU AFFICHE : le rôle qui commande, et ce que
    #  le score vaut. Un rail qui ne dirait pas le rôle laisserait croire que
    #  les questions manquantes sont les mêmes pour tous.
    contexte = {}
    if roles:
        contexte["role"] = " et ".join(_en.ROLES[r]["nom"] for r in roles)
    if rbi:
        contexte["rbi"] = ("Identification biométrique à distance : neuf "
                           "exigences de plus, et l'alinéa 14(5) à tenir.")
    return manque, sans_objet, contexte


EVALUATEURS = {
    "en18229_3": _en18229_3,
    "cartographier": _cartographier,
    "nis2": _nis2, "iso27001": _iso27001, "iso42001": _iso42001,
    "cra": _cra, "en18286": _en18286, "ocde": _ocde,
    "nist_ai_rmf": _nist_ai_rmf, "owasp_llm": _owasp_llm,
    "nist_800_53": _nist_800_53, "nist_800_82": _nist_800_82,
    "rgpd": _rgpd, "ia_act": _ia_act,
}


# ═══════════════════════════════════════════════════════════════════════
# 5. L'AVANCEMENT — UN SEUL ENDROIT LE CALCULE
# ═══════════════════════════════════════════════════════════════════════

def _declares(d, cle, norme):
    """Les panneaux déclarés lus — ceux de CE parcours.

    UN CLIC NE VALIDE RIEN QUI SE REMPLIT. Un bloc à remplir ne consulte pas
    « lus » — sans quoi un clic validerait ce qu'il demande de renseigner.
    Une règle de la suite le vérifie ; une autre, que l'ancienne
    déclaration « passé en revue » ne valide plus rien."""
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
    return ("Les %d blocs du parcours sont faits. Ce n'est pas une "
            "conformité : %s." % (len(ouvrables), QUI_JUGE[norme]))


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
for _hc in HORS_CONFORMITE:
    if _hc not in BLOCS:
        _FAUTES.append("hors conformité : %s n'est pas un parcours" % _hc)

assert not _FAUTES, "parcours_normes.py se contredit : %s" % _FAUTES
