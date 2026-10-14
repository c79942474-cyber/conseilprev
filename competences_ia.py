# -*- coding: utf-8 -*-
"""RÉFÉRENTIEL DE COMPÉTENCES IA — ce qu'une personne doit maîtriser, et jusqu'où.

CE QUE CE MODULE EST. Un référentiel de compétences traduit un objectif
général — « maîtriser l'IA générative » — en capacités précises, observables,
attendues à un NIVEAU qui dépend de la personne. Ce module prend quatre
déclarations (le type de personne, le secteur de l'entreprise, la fonction
métier, le niveau de connaissances actuel) et rend trois choses : la cible par
famille de compétences, l'écart avec le niveau déclaré, et la réponse de
formation ou de sensibilisation qui comble cet écart.

CE QU'IL N'EST PAS, et c'est la première phrase du cadrage retenu : ni un
catalogue de formations, ni une liste d'outils, ni une bibliothèque de prompts.
Les six familles ci-dessous restent vraies quand ChatGPT, Copilot, Gemini ou
Claude changent de version ou de nom. Savoir vérifier une production, protéger
une information confidentielle ou contextualiser une demande ne se périme pas
avec l'outil.

═══ LA CIBLE EST UN MAXIMUM, JAMAIS UNE SOMME ═════════════════════════════
Trois entrées contribuent à la cible d'une même famille : la population, la
fonction et le secteur. Les ADDITIONNER fabriquerait des experts : un manager
(encadrer 4) en juridique (protéger 4) dans la santé (protéger 4) sortirait
au-delà de l'échelle, et la sortie recommanderait un cursus de deux semaines
à quelqu'un qui a besoin d'une journée. On retient donc le MAXIMUM des trois,
et la sortie dit laquelle des trois commande — parce que c'est cette raison-là
qui se discute en comité, pas le chiffre.

═══ L'ÉCART COMMANDE LA PROPOSITION, ET RIEN D'AUTRE ══════════════════════
Une formation n'est proposée que si elle porte une famille où un écart existe,
et seulement jusqu'à la cible. Proposer au-delà coûte des jours à l'entreprise
et de la crédibilité au plan : un collaborateur à qui on propose un cursus de
gouvernance avancée comprend que personne n'a regardé son besoin. Les
formations écartées pour cette raison sont DITES écartées, avec leur motif —
une absence silencieuse se lit comme un oubli.

═══ LE NIVEAU DÉCLARÉ N'EST PAS UN NIVEAU MESURÉ ══════════════════════════
L'entrée est une déclaration. Et une déclaration GLOBALE ne peut pas dire ce
qui compte le plus : deux personnes qui emploient le même outil chaque jour
peuvent être fortes en « interagir » et faibles en « évaluer » — l'une obtient
vite un résultat pertinent et ne le vérifie pas, l'autre se méfie de tout et
n'en tire rien. Le module ne corrige pas cette asymétrie en silence : il la
NOMME dans ses réserves, et dit ce qu'il faudrait pour la lever (une
déclaration par famille, un exercice, une mise en situation).

═══ CE QUE LE MODULE NE PEUT PAS FAIRE, ÉCRIT ICI ET SERVI À L'ÉCRAN ══════
  · Il ne mesure pas. Il calcule un écart entre une cible et une déclaration.
  · Il ne propose que ce que le catalogue du cabinet contient. Un besoin que
    le catalogue ne couvre pas est RENDU comme non couvert, avec la famille et
    le niveau manquants — jamais remplacé par la formation la plus proche.
  · L'échelle et les cibles sont la position du cabinet, pas une obligation.
    L'article 4 du règlement (UE) 2024/1689 impose aux fournisseurs et aux
    déployeurs de prendre des mesures pour que les personnes qui utilisent
    leurs systèmes atteignent un niveau suffisant de maîtrise de l'IA, en
    tenant compte de leurs connaissances, de leur formation et du contexte
    d'usage. Il n'écrit aucune échelle, et n'en impose aucune. Le plancher de
    niveau 1 sur « comprendre » et « protéger » en découle ; le reste est une
    doctrine, et le dire est la condition pour qu'on puisse en discuter.
"""
import secteurs_nace

VERSION = "2026-10-a"

# ═══════════════════════════════════════════════════════════════════════════
#  1. LES SIX FAMILLES, DANS L'ORDRE OÙ ELLES S'ACQUIÈRENT
# ═══════════════════════════════════════════════════════════════════════════
#
# L'ORDRE N'EST PAS DÉCORATIF. On ne contrôle pas une production qu'on ne sait
# pas obtenir, et on n'encadre pas un usage qu'on n'a pas pratiqué. Il sert à
# l'affichage ET au tri de la proposition : à écart égal, la famille la plus
# amont passe d'abord.

FAMILLES = (
    {"cle": "comprendre", "nom": "Comprendre",
     "dit": "Connaître ce qu'une IA peut produire et les limites auxquelles "
            "elle reste confrontée : un résultat vraisemblable n'est pas un "
            "résultat exact.",
     "observable": "La personne sait expliquer pourquoi une réponse générée "
                   "demande une vérification."},
    {"cle": "interagir", "nom": "Interagir",
     "dit": "Formuler une demande qui obtient une production exploitable, et "
            "la faire évoluer : objectif, contexte, contraintes, format.",
     "observable": "La personne précise l'objectif, le contexte, les "
                   "contraintes et le résultat attendu."},
    {"cle": "evaluer", "nom": "Évaluer",
     "dit": "Contrôler la qualité d'une production avant de s'en servir : "
            "exactitude, complétude, respect des contraintes posées.",
     "observable": "La personne vérifie les faits, la cohérence, et ce qui "
                   "exige une source."},
    {"cle": "proteger", "nom": "Protéger",
     "dit": "Savoir quelles informations peuvent être communiquées à l'outil, "
            "et lesquelles ne peuvent pas l'être.",
     "observable": "La personne identifie une situation sensible et sait "
                   "quelle règle appliquer ou qui solliciter."},
    {"cle": "appliquer", "nom": "Appliquer",
     "dit": "Déterminer quand l'IA apporte réellement de la valeur dans "
            "l'activité, et quelle place garder à l'expertise humaine.",
     "observable": "La personne sait dire la valeur apportée, et garde le "
                   "contrôle du résultat."},
    {"cle": "encadrer", "nom": "Encadrer",
     "dit": "Piloter les usages et les responsabilités : règles, niveaux de "
            "contrôle, arbitrages, accompagnement des utilisateurs.",
     "observable": "La personne formalise les usages autorisés, les contrôles "
                   "et les responsabilités."},
)
_CLES_FAMILLES = tuple(f["cle"] for f in FAMILLES)
_RANG_FAMILLE = {f["cle"]: i for i, f in enumerate(FAMILLES)}


# ═══════════════════════════════════════════════════════════════════════════
#  2. L'ÉCHELLE — DES COMPORTEMENTS, PAS DES ADJECTIFS
# ═══════════════════════════════════════════════════════════════════════════
#
# « Débutant », « intermédiaire », « avancé » ne décrivent rien d'observable et
# ne se négocient pas : deux managers appelleront « intermédiaire » deux choses
# différentes. Chaque niveau dit donc ce que la personne est capable de FAIRE.
#
# LE NIVEAU 0 N'EST PAS DANS LE CADRAGE D'ORIGINE, ET IL EST NÉCESSAIRE.
# L'échelle retenue commence à « Comprendre ». Quelqu'un qui n'a jamais ouvert
# un outil génératif est EN DESSOUS : le placer au niveau 1 lui prêterait des
# repères qu'il n'a pas, et l'écart calculé serait faux d'un cran sur les six
# familles à la fois.

NIVEAUX = (
    {"n": 0, "nom": "Aucun repère",
     "dit": "La personne n'a pas de repère sur ce qu'un système génératif "
            "produit, ni sur les règles qui s'appliquent."},
    {"n": 1, "nom": "Comprendre",
     "dit": "Elle connaît les principes essentiels, les possibilités, les "
            "limites et les règles applicables, et sait quand demander de "
            "l'aide."},
    {"n": 2, "nom": "Utiliser avec accompagnement",
     "dit": "Elle met en œuvre les bonnes pratiques dans des situations "
            "simples ou encadrées, avec un référent ou une procédure."},
    {"n": 3, "nom": "Utiliser en autonomie",
     "dit": "Elle choisit une approche pertinente, contextualise, évalue les "
            "réponses et gère les risques courants sans accompagnement "
            "systématique."},
    {"n": 4, "nom": "Piloter et transmettre",
     "dit": "Elle accompagne d'autres utilisateurs, définit des pratiques, "
            "challenge les usages et participe aux règles communes."},
    {"n": 5, "nom": "Concevoir ou expertiser",
     "dit": "Elle intervient sur des situations complexes : conception, "
            "architecture, intégration, sécurisation, gouvernance avancée."},
)
NIVEAU_MIN = 0
NIVEAU_MAX = 5
_NIVEAUX_PAR_N = {x["n"]: x for x in NIVEAUX}

#: LE PLANCHER, ET IL A UN FONDEMENT. L'article 4 du règlement (UE) 2024/1689
#: vise les personnes qui utilisent les systèmes pour le compte du déployeur :
#: aucune population n'est donc à zéro sur « comprendre » et « protéger ». Les
#: quatre autres familles n'ont pas de plancher — un collaborateur qui n'emploie
#: pas d'IA dans son activité n'a aucune raison d'être noté sur « appliquer ».
PLANCHER_ART4 = ("comprendre", "proteger")
PLANCHER_ART4_NIVEAU = 1
PLANCHER_SOURCE = ("Règlement (UE) 2024/1689, article 4 — maîtrise de l'IA. "
                   "L'obligation est de prendre des mesures ; le niveau 1 est "
                   "la lecture du cabinet, pas une exigence du texte.")


# ═══════════════════════════════════════════════════════════════════════════
#  3. LES QUATRE ENTRÉES
# ═══════════════════════════════════════════════════════════════════════════
#
# POPULATION ET FONCTION SE RECOUVRENT, ET C'EST VOULU. Un DPO est une
# fonction support ET un expert de conformité ; un DSI encadre ET conçoit. Le
# recouvrement est sans danger puisque la cible retient le maximum : la
# personne reçoit la plus haute des deux exigences, ce qui est exactement ce
# qu'on veut. Les séparer en une seule liste aurait obligé à écrire une entrée
# par combinaison.

POPULATIONS = (
    {"cle": "dirigeant", "nom": "Dirigeant, membre du comité de direction",
     "dit": "Arbitre les usages, engage l'organisation, répond du dispositif."},
    {"cle": "manager", "nom": "Manager, encadrant d'équipe",
     "dit": "Observe les pratiques réelles, autorise ou refuse un usage dans "
            "son périmètre."},
    {"cle": "referent_ia", "nom": "Référent ou ambassadeur IA",
     "dit": "Relais désigné auprès des utilisateurs, entre deux formations."},
    {"cle": "collaborateur", "nom": "Collaborateur sans encadrement",
     "dit": "Emploie l'IA dans son activité, sans responsabilité d'arbitrage."},
    {"cle": "expert_conformite",
     "nom": "Conformité, juridique, DPO, qualité, audit",
     "dit": "Écrit les règles, instruit les analyses d'impact, contrôle."},
    {"cle": "expert_technique", "nom": "DSI, données, sécurité, développement",
     "dit": "Intègre, sécurise et exploite les solutions."},
)
_CLES_POPULATIONS = tuple(p["cle"] for p in POPULATIONS)

FONCTIONS = (
    {"cle": "direction", "nom": "Direction générale, stratégie"},
    {"cle": "rh", "nom": "Ressources humaines, formation"},
    {"cle": "juridique", "nom": "Juridique, conformité, protection des données"},
    {"cle": "finance", "nom": "Finance, gestion, contrôle"},
    {"cle": "marketing", "nom": "Marketing, communication, création"},
    {"cle": "commercial", "nom": "Commercial, relation client"},
    {"cle": "operations", "nom": "Production, exploitation, logistique"},
    {"cle": "si_data", "nom": "Systèmes d'information, données, sécurité"},
    {"cle": "qualite_hse", "nom": "Qualité, HSE, risques"},
    {"cle": "rd", "nom": "Recherche, développement, ingénierie"},
)
_CLES_FONCTIONS = tuple(f["cle"] for f in FONCTIONS)


def secteurs():
    """LES SECTEURS NE SONT PAS RECOPIÉS ICI. Ce sont les vingt-deux sections
    de la nomenclature, lues dans `secteurs_nace` — le module qui les porte
    déjà, avec leur intitulé officiel. Les retaper aurait créé une seconde
    liste de secteurs dans le dépôt, et deux listes de secteurs divergent."""
    return [{"code": s["code"], "nom": s["intitule"],
             "officiel": s["intitule_officiel"]}
            for s in secteurs_nace.SECTIONS]


_CODES_SECTEURS = tuple(s["code"] for s in secteurs_nace.SECTIONS)


# ═══════════════════════════════════════════════════════════════════════════
#  4. CE QUE CHAQUE ENTRÉE EXIGE
# ═══════════════════════════════════════════════════════════════════════════
#
# Une famille absente d'une table vaut ZÉRO pour cette entrée — pas « non
# renseigné ». Écrire un zéro partout aurait rendu les tables illisibles sans
# rien ajouter : ce qui se lit, c'est ce qu'une entrée EXIGE.

CIBLE_POPULATION = {
    "dirigeant":        {"comprendre": 2, "evaluer": 2, "proteger": 2,
                         "appliquer": 2, "encadrer": 4},
    "manager":          {"comprendre": 2, "interagir": 2, "evaluer": 3,
                         "proteger": 3, "appliquer": 3, "encadrer": 4},
    "referent_ia":      {"comprendre": 3, "interagir": 3, "evaluer": 3,
                         "proteger": 3, "appliquer": 4, "encadrer": 4},
    "collaborateur":    {"comprendre": 1, "interagir": 2, "evaluer": 2,
                         "proteger": 2, "appliquer": 2},
    "expert_conformite": {"comprendre": 3, "evaluer": 4, "proteger": 4,
                          "encadrer": 4},
    "expert_technique": {"comprendre": 4, "interagir": 3, "evaluer": 3,
                         "proteger": 5, "appliquer": 4, "encadrer": 5},
}

CIBLE_FONCTION = {
    "direction":   {"encadrer": 4},
    "rh":          {"proteger": 3, "encadrer": 4,
                    # LES RH PORTENT LE RÉFÉRENTIEL LUI-MÊME : sans « piloter
                    # et transmettre », personne ne tient la trajectoire.
                    "appliquer": 3},
    "juridique":   {"evaluer": 4, "proteger": 4, "encadrer": 4},
    "finance":     {"evaluer": 3, "proteger": 3},
    # LE MARKETING PORTE L'ARTICLE 50. Marquage, étiquetage et preuve des
    # contenus de synthèse tombent sur ceux qui publient : « évaluer » et
    # « protéger » y montent, et ce n'est pas une préférence de métier.
    "marketing":   {"evaluer": 3, "proteger": 3, "appliquer": 3},
    "commercial":  {"evaluer": 3, "proteger": 3},
    "operations":  {"appliquer": 3},
    "si_data":     {"comprendre": 4, "proteger": 5, "appliquer": 4,
                    "encadrer": 5},
    "qualite_hse": {"evaluer": 4, "encadrer": 4},
    "rd":          {"comprendre": 4, "interagir": 3, "evaluer": 3,
                    "appliquer": 4},
}

# ── LE SECTEUR N'EXIGE QUELQUE CHOSE QUE LÀ OÙ UN RÉGIME LE JUSTIFIE ───────
#
# CE QU'ON N'A PAS FAIT, ET POURQUOI. Mettre une exigence sur les vingt-deux
# sections aurait demandé d'inventer dix-sept positions sans fondement, et
# aurait fait monter la cible de tout le monde d'un cran — c'est-à-dire rien.
# Cinq groupes de sections portent un régime qui PÈSE sur la manipulation de
# données ou sur la responsabilité de l'usage ; les autres sont neutres, et
# leur neutralité est une réponse, pas un trou.
CIBLE_SECTEUR = {
    "Q": ({"proteger": 4, "evaluer": 4},
          "Santé et action sociale : données de santé, et une production "
          "générée qui touche une personne se vérifie avant d'être employée."),
    "K": ({"proteger": 4, "encadrer": 4},
          "Finance et assurance : secteur sous régime de résilience "
          "opérationnelle, où l'usage d'un outil externe s'encadre."),
    "O": ({"proteger": 4, "evaluer": 4},
          "Administration publique : décisions qui engagent des droits, et "
          "transparence due aux personnes."),
    "P": ({"evaluer": 3, "proteger": 3},
          "Enseignement : production de contenus destinés à des apprenants, "
          "dont l'exactitude engage l'établissement."),
    "J": ({"comprendre": 3, "proteger": 3},
          "Information et communication : secteur qui FOURNIT souvent les "
          "systèmes, en plus de les employer."),
}
# ── LE PLAFOND DE RÔLE : UN SECTEUR NE CONFÈRE PAS UN RÔLE ────────────────
#
# CE QUE LE MAXIMUM SEUL PRODUISAIT, ET POURQUOI C'ÉTAIT FAUX. Un
# collaborateur du secteur de la santé ressortait à « Piloter et
# transmettre » sur « évaluer » et « protéger », et un collaborateur de la
# direction des systèmes d'information à « Concevoir ou expertiser » sur
# « protéger ». Or les niveaux 4 et 5 de l'échelle ne décrivent pas une
# vigilance plus haute : ils décrivent un RÔLE — transmettre à d'autres,
# concevoir ou expertiser. Un secteur sensible et une direction technique
# élèvent l'exigence portée sur la personne ; ils ne lui donnent pas ce rôle.
#
# Donc : la POPULATION porte le rôle, et son exigence passe entière. La
# FONCTION et le SECTEUR portent la demande du domaine, et leur exigence est
# RABATTUE au plafond du rôle. La sortie montre les deux nombres — l'exigence
# brute et ce qui a été retenu — pour qu'un comité voie le rabattement au
# lieu de le deviner.
PLAFOND_ROLE = {
    #  Seul le collaborateur est plafonné, et c'est la seule population qui
    #  n'occupe aucun rôle : « sans encadrement » est écrit dans son intitulé.
    "collaborateur": 3,
    "dirigeant": 5, "manager": 5, "referent_ia": 5,
    "expert_conformite": 5, "expert_technique": 5,
}
PLAFOND_ROLE_DIT = (
    "Le niveau 3 est le plus haut niveau d'USAGE de l'échelle ; les niveaux 4 "
    "et 5 décrivent un rôle — transmettre, concevoir. La fonction et le "
    "secteur sont rabattus à ce plafond : ils élèvent l'exigence, ils ne "
    "confèrent pas le rôle. L'exigence de la population, elle, passe entière, "
    "puisque c'est elle qui porte le rôle."
)

_SECTEURS_NEUTRES_DIT = (
    "Aucune exigence sectorielle n'est posée : ce secteur ne porte pas, en "
    "lui-même, de régime qui déplace la cible. La population et la fonction "
    "la commandent entièrement."
)


# ═══════════════════════════════════════════════════════════════════════════
#  5. LE CATALOGUE DU CABINET, CITÉ PAR NUMÉRO
# ═══════════════════════════════════════════════════════════════════════════
#
# LES FORMATIONS NE SONT PAS RECOPIÉES ICI NON PLUS, et pour une raison plus
# forte que pour les secteurs : le catalogue est servi à l'écran du Hub
# Training depuis `FORMATIONS_CAT`. Une seconde copie du titre, de la durée ou
# du public aurait divergé au premier ajustement, et l'écran aurait proposé une
# formation sous un intitulé que le catalogue n'emploie plus.
#
# CE QUI EST DÉCLARÉ ICI, ET QUE LE CATALOGUE NE DIT PAS : quelles familles
# chaque formation porte, et JUSQU'À QUEL NIVEAU. C'est le seul lien entre un
# référentiel de compétences et une offre de formation, et il n'existe nulle
# part ailleurs. `titre_attendu` est là pour qu'une règle puisse refuser la
# dérive : si le catalogue renomme ou renumérote, la règle tombe et nomme la
# ligne.

APPORTS = (
    {"n": 1, "titre_attendu": "Fondamentaux du règlement européen sur l'IA",
     "porte": {"comprendre": 2, "encadrer": 2}},
    {"n": 2, "titre_attendu": "Systèmes à haut risque : obligations et mise en conformité",
     "porte": {"comprendre": 3, "proteger": 3, "encadrer": 3}},
    {"n": 3, "titre_attendu": "Transparence (article 50) : marquage, étiquetage et preuve",
     "porte": {"evaluer": 3, "proteger": 3}},
    {"n": 4, "titre_attendu": "Analyse d'impact sur les droits fondamentaux (FRIA)",
     "porte": {"evaluer": 4, "proteger": 4}},
    {"n": 5, "titre_attendu": "RGPD pour les projets d'intelligence artificielle",
     "porte": {"proteger": 4}},
    {"n": 6, "titre_attendu": "Analyse d'impact relative à la protection des données (art. 35)",
     "porte": {"proteger": 4}},
    {"n": 7, "titre_attendu": "Preuve du consentement, rétention et droits des personnes",
     "porte": {"proteger": 4}},
    {"n": 8, "titre_attendu": "ISO/IEC 42001 : construire un système de management de l'IA",
     "porte": {"encadrer": 4}},
    {"n": 9, "titre_attendu": "Auditer un système de management de l'IA",
     "porte": {"evaluer": 4, "encadrer": 5}},
    {"n": 10, "titre_attendu": "Gouvernance de l'IA : IA Act, RGPD et ISO 42001 en un dispositif unique",
     "porte": {"comprendre": 3, "proteger": 4, "encadrer": 4}},
    {"n": 11, "titre_attendu": "Rendre la gouvernance de l'IA opérationnelle",
     "porte": {"encadrer": 5, "proteger": 4, "appliquer": 4}},
    # LA SEULE PORTE D'ENTRÉE, ET LA SEULE SENSIBILISATION. Une demi-journée,
    # sans prérequis, qui porte quatre familles au premier palier : c'est elle
    # que reçoit quiconque part de zéro, et elle seule.
    {"n": 12, "titre_attendu": "Littératie IA pour les métiers",
     "porte": {"comprendre": 2, "interagir": 2, "evaluer": 2, "proteger": 2},
     "sensibilisation": True},
    {"n": 13, "titre_attendu": "Repenser mon processus en IA-first",
     "porte": {"appliquer": 3, "interagir": 2}},
    {"n": 14, "titre_attendu": "Animer un atelier d'adoption — former les formateurs",
     "porte": {"appliquer": 4, "encadrer": 4}},
    {"n": 15, "titre_attendu": "Constituer un réseau d'ambassadeurs",
     "porte": {"encadrer": 4}},
)
_NUMEROS_APPORTS = tuple(a["n"] for a in APPORTS)
CATALOGUE_SOURCE = ("Catalogue « Formations conformité IA » du Hub Training "
                    "(FORMATIONS_CAT). Les titres, durées et publics viennent "
                    "de là ; ce module n'ajoute que la correspondance entre "
                    "une formation et les familles qu'elle porte.")


def _verifier():
    """LES TABLES SE CONTREDISENT OU ELLES NE SERVENT À RIEN. Une clé de
    famille mal orthographiée dans une cible ne lèverait nulle part : elle
    serait simplement ignorée, et la cible sortirait un cran trop bas sans que
    rien ne le dise."""
    fautes = []
    for nom, table in (("CIBLE_POPULATION", CIBLE_POPULATION),
                       ("CIBLE_FONCTION", CIBLE_FONCTION)):
        for cle, exig in table.items():
            for fam, niv in exig.items():
                if fam not in _CLES_FAMILLES:
                    fautes.append("%s[%s] : famille inconnue %r" % (nom, cle, fam))
                if not (NIVEAU_MIN <= niv <= NIVEAU_MAX):
                    fautes.append("%s[%s][%s] : niveau %r hors échelle"
                                  % (nom, cle, fam, niv))
    for code, (exig, dit) in CIBLE_SECTEUR.items():
        if code not in _CODES_SECTEURS:
            fautes.append("CIBLE_SECTEUR : la section %r n'existe pas dans "
                          "secteurs_nace" % code)
        if not dit:
            fautes.append("CIBLE_SECTEUR[%s] : aucune raison écrite. Une "
                          "exigence sectorielle sans motif ne se discute pas."
                          % code)
        for fam, niv in exig.items():
            if fam not in _CLES_FAMILLES:
                fautes.append("CIBLE_SECTEUR[%s] : famille inconnue %r"
                              % (code, fam))
            if not (NIVEAU_MIN <= niv <= NIVEAU_MAX):
                fautes.append("CIBLE_SECTEUR[%s][%s] : niveau %r hors échelle"
                              % (code, fam, niv))
    for cle in _CLES_POPULATIONS:
        if cle not in CIBLE_POPULATION:
            fautes.append("la population %r n'a aucune cible : elle sortirait "
                          "au plancher, ce qui est faux pour toutes" % cle)
    for cle in _CLES_FONCTIONS:
        if cle not in CIBLE_FONCTION:
            fautes.append("la fonction %r n'a aucune cible" % cle)
    for cle in _CLES_POPULATIONS:
        if cle not in PLAFOND_ROLE:
            fautes.append("la population %r n'a pas de plafond de rôle : la "
                          "fonction et le secteur passeraient sans borne"
                          % cle)
            continue
        plaf = PLAFOND_ROLE[cle]
        if not (1 <= plaf <= NIVEAU_MAX):
            fautes.append("PLAFOND_ROLE[%s] = %r, hors échelle" % (cle, plaf))
        #  Un plafond sous ce que la population exige d'elle-même serait un
        #  plafond qui se contredit : la population porte le rôle.
        sien = max((CIBLE_POPULATION.get(cle) or {}).values() or [0])
        if sien > plaf:
            fautes.append("PLAFOND_ROLE[%s] = %d, mais la population exige "
                          "%d d'elle-même : le plafond contredit le rôle"
                          % (cle, plaf, sien))
    if not PLAFOND_ROLE_DIT:
        fautes.append("PLAFOND_ROLE n'a aucune raison écrite : un rabattement "
                      "muet se lit comme une erreur de calcul")
    for cle in PLAFOND_ROLE:
        if cle not in _CLES_POPULATIONS:
            fautes.append("PLAFOND_ROLE : population inconnue %r" % cle)
    vus = set()
    for a in APPORTS:
        if a["n"] in vus:
            fautes.append("la formation n°%d est déclarée deux fois" % a["n"])
        vus.add(a["n"])
        if not a.get("titre_attendu"):
            fautes.append("la formation n°%d n'a pas de titre attendu : une "
                          "règle ne pourrait pas refuser la dérive du "
                          "catalogue" % a["n"])
        if not a.get("porte"):
            fautes.append("la formation n°%d ne porte aucune famille : elle ne "
                          "serait jamais proposée" % a["n"])
        for fam, niv in (a.get("porte") or {}).items():
            if fam not in _CLES_FAMILLES:
                fautes.append("formation n°%d : famille inconnue %r"
                              % (a["n"], fam))
            if not (1 <= niv <= NIVEAU_MAX):
                fautes.append("formation n°%d : porte au niveau %r, hors "
                              "échelle utile" % (a["n"], niv))
    sensib = [a["n"] for a in APPORTS if a.get("sensibilisation")]
    if len(sensib) != 1:
        fautes.append("%d formation(s) marquée(s) sensibilisation : il en faut "
                      "EXACTEMENT une, c'est la porte d'entrée de qui part de "
                      "zéro — %s" % (len(sensib), sensib))
    if fautes:
        raise RuntimeError("competences_ia : " + " | ".join(fautes))


_verifier()


# ═══════════════════════════════════════════════════════════════════════════
#  6. LA CIBLE, FAMILLE PAR FAMILLE
# ═══════════════════════════════════════════════════════════════════════════

def _entree(valeur, permises):
    return valeur if valeur in permises else None


def composer(exig_pop, exig_fon, exig_sec, plafond, famille):
    """LA COMPOSITION D'UNE SEULE FAMILLE : (niveau, retenus, commande).

    POURQUOI ELLE EST SORTIE DE `cible()`, ET C'EST UNE BATTERIE DE MUTATIONS
    QUI L'A IMPOSÉ. Deux propriétés de cette arithmétique ne changent AUCUNE
    sortie sur les 1 320 triplets du dépôt :

      · LE PLANCHER DE L'ARTICLE 4 ne mord sur aucun triplet, parce que les
        six populations exigent déjà au moins 1 sur « comprendre » et sur
        « protéger ». Il garde l'avenir, pas le présent ;
      · LE NON-RABATTEMENT DE LA POPULATION ne se voit pas non plus : la
        seule population plafonnée (le collaborateur, à 3) n'exige que 2
        d'elle-même, et la garde d'import REFUSE une table où une population
        exigerait plus que son plafond.

    Les deux mutations correspondantes SURVIVAIENT donc à toutes les règles
    écrites sur `cible()` — non parce que les règles étaient faibles, mais
    parce que ces propriétés ne sont pas observables depuis la sortie du
    dépôt. Sortie ici, la composition s'éprouve sur des exigences qui
    n'existent pas dans les tables, et les deux propriétés se mesurent."""
    #  Troisième membre : le plafond de rôle s'applique-t-il à cette entrée ?
    #  La population porte le rôle, son exigence passe ENTIÈRE ; la fonction
    #  et le secteur portent la demande du domaine, et sont RABATTUES.
    parts = [("population", exig_pop, False),
             ("fonction", exig_fon, True),
             ("secteur", exig_sec, True)]
    plancher = PLANCHER_ART4_NIVEAU if famille in PLANCHER_ART4 else 0
    retenus = [(nom, min(v, plafond) if rab else v, v)
               for nom, v, rab in parts]
    niv = max([r[1] for r in retenus] + [plancher])
    #  CE QUI COMMANDE : la ou les entrées qui atteignent le maximum APRÈS
    #  rabattement — citer une entrée dont l'exigence a été rabattue sous la
    #  cible dirait qu'elle commande alors qu'elle a été bornée. S'il n'y en a
    #  aucune, c'est le plancher, et il est nommé comme tel.
    commande = [r[0] for r in retenus if r[1] == niv and niv > 0]
    if not commande:
        commande = ["article 4"] if niv else []
    return niv, retenus, commande


def cible(population, fonction, secteur):
    """La cible par famille, et CE QUI LA COMMANDE.

    Le maximum des trois contributions, plancher de l'article 4 compris, et
    l'exigence de la fonction comme celle du secteur RABATTUES au plafond du
    rôle (voir PLAFOND_ROLE). La sortie porte, pour chaque famille, laquelle
    des trois a décidé et ce qui a été rabattu : sans cela, un comité qui
    trouve une cible trop haute — ou trop basse — ne sait pas quel argument
    discuter."""
    pop = _entree(population, _CLES_POPULATIONS)
    fon = _entree(fonction, _CLES_FONCTIONS)
    sec = _entree(secteur, _CODES_SECTEURS)
    if not pop or not fon or not sec:
        manque = [n for n, v in (("population", pop), ("fonction", fon),
                                 ("secteur", sec)) if not v]
        return {"ok": False,
                "dit": "Entrée(s) non reconnue(s) : %s. Le module ne devine "
                       "pas une cible à partir d'une entrée vide."
                       % ", ".join(manque),
                "manque": manque}

    exig_sec, raison_sec = CIBLE_SECTEUR.get(sec, ({}, _SECTEURS_NEUTRES_DIT))
    plafond = PLAFOND_ROLE[pop]
    out = []
    for f in FAMILLES:
        c = f["cle"]
        niv, retenus, commande = composer(
            CIBLE_POPULATION[pop].get(c, 0), CIBLE_FONCTION[fon].get(c, 0),
            exig_sec.get(c, 0), plafond, c)
        out.append({
            "famille": c, "nom": f["nom"], "dit": f["dit"],
            "observable": f["observable"], "cible": niv,
            "cible_nom": _NIVEAUX_PAR_N[niv]["nom"],
            "commande": commande,
            "parts": [{"entree": r[0], "exige": r[2], "retenu": r[1],
                       "plafonne": r[2] > r[1]} for r in retenus],
        })
    return {"ok": True, "familles": out,
            "population": pop, "fonction": fon, "secteur": sec,
            "raison_secteur": raison_sec,
            "secteur_neutre": sec not in CIBLE_SECTEUR,
            "plafond_role": plafond,
            "plafond_role_dit": PLAFOND_ROLE_DIT,
            "plafond_mord": any(q["plafonne"] for f in out
                                for q in f["parts"])}


# ═══════════════════════════════════════════════════════════════════════════
#  7. L'ÉCART, PUIS LA PROPOSITION
# ═══════════════════════════════════════════════════════════════════════════

NATURES = {
    "atteint": "Aucune action de formation : la cible est atteinte au niveau "
               "déclaré, sur les six familles.",
    "sensibilisation": "Une sensibilisation suffit : les écarts sont d'un "
                       "palier, au premier niveau.",
    "formation": "Une ou deux formations ciblées sur les familles en écart.",
    "cursus": "Un parcours : l'écart dépasse deux paliers sur au moins une "
              "famille, et aucune séance isolée ne le comble.",
}


def _ecarts(familles, niveau_actuel):
    out = []
    for f in familles:
        e = max(0, f["cible"] - niveau_actuel)
        out.append(dict(f, actuel=niveau_actuel,
                        actuel_nom=_NIVEAUX_PAR_N[niveau_actuel]["nom"],
                        ecart=e))
    return out


def _nature(ecarts, niveau_actuel):
    pire = max([e["ecart"] for e in ecarts] or [0])
    if pire <= 0:
        return "atteint", pire
    if pire >= 3:
        return "cursus", pire
    if pire == 1 and niveau_actuel <= 1:
        return "sensibilisation", pire
    return "formation", pire


def proposer(population, fonction, secteur, niveau_actuel):
    """La réponse pour UNE personne : niveau de départ, cible, écarts,
    formations retenues — et celles qui sont écartées, avec leur motif.

    CE QUE LA SORTIE REFUSE DE FAIRE. Elle ne propose pas une formation qui
    porte une famille au-delà de la cible : une personne dont la cible est 3
    n'a pas besoin du niveau 5, et le lui proposer coûte des jours et de la
    crédibilité. Les formations écartées pour cette raison sont rendues avec
    leur motif, parce qu'une absence silencieuse se lit comme un oubli."""
    #  `True` EST UN ENTIER EN PYTHON, et `NIVEAU_MIN <= True <= NIVEAU_MAX`
    #  est vrai : un `true` JSON passait donc pour le niveau 1, et la personne
    #  recevait une trajectoire qu'elle n'a pas demandée. Mesuré par une
    #  règle, pas deviné.
    if isinstance(niveau_actuel, bool) \
            or not isinstance(niveau_actuel, int) \
            or not (NIVEAU_MIN <= niveau_actuel <= NIVEAU_MAX):
        return {"ok": False,
                "dit": "Le niveau déclaré doit être un entier de %d à %d."
                       % (NIVEAU_MIN, NIVEAU_MAX)}
    c = cible(population, fonction, secteur)
    if not c.get("ok"):
        return c

    ecarts = _ecarts(c["familles"], niveau_actuel)
    nature, pire = _nature(ecarts, niveau_actuel)
    en_ecart = {e["famille"]: e for e in ecarts if e["ecart"] > 0}
    cibles = {e["famille"]: e["cible"] for e in ecarts}

    #  DEUX LECTURES DE LA MÊME FORMATION, ET ELLES NE SE CONFONDENT PAS.
    #  « utiles » sert à CHOISIR : une formation n'entre que si elle répond à
    #  un besoin sans dépasser la cible — on ne retient jamais une formation
    #  POUR dépasser. « credits » sert à COMPTER ce qu'elle apporte une fois
    #  retenue, plafonné à la cible : une sensibilisation qui mène au niveau 2
    #  comble bien un besoin de niveau 1, et le refuser laissait la famille
    #  « comprendre » d'un collaborateur en écart sans que rien ne le dise.
    retenues, ecartees = [], []
    for a in APPORTS:
        utiles, au_dela, credits = [], [], []
        for fam, porte in a["porte"].items():
            if fam not in en_ecart:
                continue
            if porte <= niveau_actuel:
                continue           # rien à apporter : déjà acquis
            credits.append({"famille": fam,
                            "porte_a": min(porte, cibles[fam])})
            if porte > cibles[fam]:
                au_dela.append(fam)
                continue
            utiles.append({"famille": fam, "porte_a": porte,
                            "gagne": min(porte, cibles[fam]) - niveau_actuel})
        if utiles:
            #  LE RANG DE LA FAMILLE LA PLUS AMONT DÉCIDE DE L'ORDRE : on ne
            #  contrôle pas une production qu'on ne sait pas obtenir.
            amont = min(_RANG_FAMILLE[u["famille"]] for u in utiles)
            retenues.append({
                "n": a["n"], "titre_attendu": a["titre_attendu"],
                "sensibilisation": bool(a.get("sensibilisation")),
                "porte": sorted(utiles,
                                key=lambda u: _RANG_FAMILLE[u["famille"]]),
                "gain_total": sum(u["gagne"] for u in utiles),
                "credits": sorted(credits,
                                  key=lambda u: _RANG_FAMILLE[u["famille"]]),
                "_tri": (-sum(u["gagne"] for u in utiles), amont, a["n"]),
            })
        elif au_dela:
            ecartees.append({
                "n": a["n"], "titre_attendu": a["titre_attendu"],
                "motif": "porte %s au-delà de la cible de cette personne"
                         % ", ".join(sorted(au_dela)),
            })
    retenues.sort(key=lambda r: r.pop("_tri"))

    #  LA COUVERTURE, ET CE QUI N'AJOUTE RIEN. Rendre les quinze formations
    #  qui « apportent quelque chose » rend le catalogue, pas une proposition :
    #  un manager parti du niveau 1 les voyait TOUTES retenues. On garde donc
    #  une formation seulement si elle élève le palier atteint sur au moins une
    #  famille en écart, au-delà de ce que les formations déjà gardées
    #  atteignent. Les autres sont rendues REDONDANTES avec leur motif — la
    #  réduction est mesurée sur la couverture, ce n'est pas un plafond
    #  arbitraire sur le nombre de lignes.
    couvert = dict((fam, niveau_actuel) for fam in en_ecart)
    gardees, redondantes = [], []
    for r in retenues:
        gagne = [u for u in r.pop("credits")
                 if u["porte_a"] > couvert[u["famille"]]]
        if not gagne:
            redondantes.append({
                "n": r["n"], "titre_attendu": r["titre_attendu"],
                "motif": "n'ajoute aucun palier que les formations retenues "
                         "n'atteignent déjà",
            })
            continue
        for u in gagne:
            couvert[u["famille"]] = u["porte_a"]
        r["ajoute"] = [{"famille": u["famille"], "porte_a": u["porte_a"]}
                       for u in gagne]
        gardees.append(r)
    retenues = gardees

    #  CE QUE LE CATALOGUE NE COUVRE PAS — DÉRIVÉ DE LA COUVERTURE OBTENUE,
    #  JAMAIS ÉCRIT. On ne regarde pas le plafond du catalogue en théorie : on
    #  regarde ce que les formations RETENUES atteignent réellement. Là où
    #  elles n'atteignent pas la cible, le besoin reste ouvert, et il est
    #  rendu — c'est une information pour le cabinet, pas un défaut à masquer.
    non_couvert = []
    for fam, e in sorted(en_ecart.items(),
                         key=lambda kv: _RANG_FAMILLE[kv[0]]):
        if couvert[fam] >= e["cible"]:
            continue
        plafond = max([a["porte"].get(fam, 0) for a in APPORTS] or [0])
        non_couvert.append({
            "famille": fam, "nom": e["nom"], "cible": e["cible"],
            "atteint": couvert[fam],
            "plafond_catalogue": plafond,
            "dit": ("Le catalogue porte « %s » au niveau %d au mieux ; la "
                    "cible est %d. Aucune formation existante ne comble cet "
                    "écart." % (e["nom"], plafond, e["cible"]))
                   if plafond < e["cible"] else
                   ("Les formations retenues portent « %s » au niveau %d ; la "
                    "cible est %d. Le catalogue va plus haut (%d), mais pas "
                    "par une formation qui réponde d'abord à un autre besoin "
                    "de cette personne." % (e["nom"], couvert[fam],
                                            e["cible"], plafond)),
        })

    #  L'ARRIVÉE NE DESCEND PAS SOUS LE DÉPART. Une personne qui se déclare
    #  au niveau 5 et dont la cible la plus haute est 4 ne « va » pas au
    #  niveau 4 : elle est déjà au-delà, et l'écrire autrement donnerait une
    #  trajectoire descendante qui n'a aucun sens.
    haute = max([e["cible"] for e in ecarts] or [0])
    au_dela = niveau_actuel > haute
    vise = max(haute, niveau_actuel)
    return {
        "ok": True, "version": VERSION,
        "population": c["population"], "fonction": c["fonction"],
        "secteur": c["secteur"], "raison_secteur": c["raison_secteur"],
        "secteur_neutre": c["secteur_neutre"],
        "plafond_role": c["plafond_role"],
        "plafond_role_dit": c["plafond_role_dit"],
        "plafond_mord": c["plafond_mord"],
        "depart": {"niveau": niveau_actuel,
                   "nom": _NIVEAUX_PAR_N[niveau_actuel]["nom"],
                   "dit": _NIVEAUX_PAR_N[niveau_actuel]["dit"]},
        "arrivee": {"niveau": vise, "nom": _NIVEAUX_PAR_N[vise]["nom"],
                    "au_dela_de_la_cible": au_dela,
                    "cible_la_plus_haute": haute,
                    "dit": ("Le niveau déclaré dépasse déjà la plus haute des "
                            "six cibles (%d) : la trajectoire ne descend pas, "
                            "elle s'arrête." % haute) if au_dela else
                           ("Niveau visé : le plus haut des six cibles. Les "
                            "familles dont la cible est plus basse n'ont pas "
                            "à l'atteindre.")},
        "familles": ecarts,
        "nature": nature, "nature_dit": NATURES[nature], "pire_ecart": pire,
        "formations": retenues, "ecartees": ecartees,
        "redondantes": redondantes,
        "non_couvert": non_couvert,
        "catalogue_source": CATALOGUE_SOURCE,
        "reserves": reserves(niveau_actuel),
        "plancher_source": PLANCHER_SOURCE,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  8. LES RÉSERVES — CE QUE LA SORTIE NE PEUT PAS GARANTIR
# ═══════════════════════════════════════════════════════════════════════════

def reserves(niveau_actuel):
    """Elles partent AVEC le résultat, jamais en bas d'écran. Une réserve
    reléguée s'applique à un chiffre qu'on ne regarde plus."""
    out = [
        {"quoi": "Le niveau de départ est déclaré, pas mesuré",
         "pourquoi": "Le module calcule un écart entre une cible et une "
                     "déclaration. Il ne constate aucune compétence.",
         "quoi_faire": "Confirmer par une mise en situation, un exercice "
                       "pratique ou un entretien avec le manager."},
        {"quoi": "Un niveau GLOBAL masque l'asymétrie qui compte",
         "pourquoi": "Deux personnes au même niveau déclaré peuvent être "
                     "fortes en « interagir » et faibles en « évaluer » : "
                     "l'une obtient vite un résultat et ne le vérifie pas, "
                     "l'autre se méfie et n'en tire rien. Le module ne corrige "
                     "pas cet écart en silence.",
         "quoi_faire": "Déclarer un niveau PAR FAMILLE, ou observer les "
                       "productions réelles de la personne."},
        {"quoi": "L'échelle et les cibles sont la position du cabinet",
         "pourquoi": "L'article 4 du règlement (UE) 2024/1689 impose de "
                     "prendre des mesures pour un niveau suffisant de "
                     "maîtrise de l'IA, en tenant compte des connaissances et "
                     "du contexte. Il n'écrit aucune échelle.",
         "quoi_faire": "Faire valider les cibles par les métiers, les "
                       "managers et la DSI avant d'en faire un attendu RH."},
    ]
    if niveau_actuel >= 3:
        out.append({
            "quoi": "Un niveau déclaré élevé est le plus fragile",
            "pourquoi": "C'est à partir de l'autonomie que l'écart entre "
                        "l'aisance ressentie et le contrôle réellement exercé "
                        "se creuse — et la déclaration ne le voit pas.",
            "quoi_faire": "Contrôler « évaluer » et « protéger » sur deux "
                          "productions réelles avant de retenir ce niveau."})
    return out


# ═══════════════════════════════════════════════════════════════════════════
#  9. LE RÉFÉRENTIEL SERVI À L'ÉCRAN, ET LA SANTÉ DU MODULE
# ═══════════════════════════════════════════════════════════════════════════

def referentiel():
    """Tout ce dont le formulaire a besoin, en un appel : les quatre listes
    déroulantes, les six familles et l'échelle."""
    return {
        "version": VERSION,
        "familles": [dict(f) for f in FAMILLES],
        "niveaux": [dict(n) for n in NIVEAUX],
        "populations": [dict(p) for p in POPULATIONS],
        "fonctions": [dict(f) for f in FONCTIONS],
        "secteurs": secteurs(),
        "plancher": {"familles": list(PLANCHER_ART4),
                     "niveau": PLANCHER_ART4_NIVEAU,
                     "source": PLANCHER_SOURCE},
        "catalogue_source": CATALOGUE_SOURCE,
        "natures": dict(NATURES),
    }


def sante():
    """Ce que le module sait de lui-même, pour la page d'état."""
    return {
        "version": VERSION,
        "familles": len(FAMILLES),
        "niveaux": len(NIVEAUX),
        "populations": len(POPULATIONS),
        "fonctions": len(FONCTIONS),
        "secteurs": len(_CODES_SECTEURS),
        "secteurs_avec_exigence": len(CIBLE_SECTEUR),
        "formations_rattachees": len(APPORTS),
        "combinaisons": (len(POPULATIONS) * len(FONCTIONS)
                         * len(_CODES_SECTEURS) * len(NIVEAUX)),
    }
