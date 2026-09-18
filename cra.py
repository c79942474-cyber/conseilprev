# -*- coding: utf-8 -*-
"""LE CYBER RESILIENCE ACT — règlement (UE) 2024/2847, rendu calculable.

═══════════════════════════════════════════════════════════════════════════
 CE QUE CE MODULE CALCULE, ET POURQUOI C'EST CELA QU'IL FAUT CALCULER
═══════════════════════════════════════════════════════════════════════════

Un règlement se résume facilement ; ce qui se résume mal, c'est la DÉCISION
qu'il impose. Pour le CRA, il y en a une qui commande toutes les autres :

    PAR QUELLE PROCÉDURE CE PRODUIT DÉMONTRE-T-IL SA CONFORMITÉ ?

Parce que la réponse sépare deux mondes. D'un côté le contrôle interne
(module A) : le fabricant évalue, signe, appose le marquage — quelques
semaines. De l'autre l'examen UE de type ou l'assurance qualité complète
(modules B+C ou H) : un ORGANISME NOTIFIÉ intervient — un budget, un délai de
plusieurs mois, et une file d'attente qui n'existe pas encore puisque le
chapitre IV n'est applicable que depuis le 11 juin 2026.

ET CETTE RÉPONSE TIENT À UN SEUL FAIT, POUR TOUTE UNE CLASSE DE PRODUITS.
Un produit important de classe I (annexe III) reste auto-évaluable À CONDITION
que le fabricant applique INTÉGRALEMENT les normes harmonisées, spécifications
communes ou schémas de certification pertinents (art. 32, §2). Ne les
appliquer qu'en partie — ou qu'elles n'existent pas encore — bascule le
produit chez l'organisme notifié. C'est la bascule la plus coûteuse du
règlement, elle se joue sur une case à cocher, et c'est précisément ce qu'un
tableau de correspondance ne dit pas.

═══════════════════════════════════════════════════════════════════════════
 CE QUE CE MODULE NE FAIT PAS
═══════════════════════════════════════════════════════════════════════════

IL NE REND PAS D'AVIS JURIDIQUE, et la restitution le dit. La qualification
d'un produit au regard d'une exclusion sectorielle (dispositif médical,
aviation, véhicule, équipement marin) est une question de droit qui se
tranche sur le produit réel, pas sur une case cochée par celui qui le vend.
Le module CONSTATE ce qui est déclaré et nomme ce qui reste à vérifier.

IL NE RECOPIE PAS LE RÈGLEMENT. Les libellés des annexes III et IV sont des
désignations de catégories — des faits, repris pour pouvoir y ranger un
produit —, et le texte du JO est réutilisable au titre de la décision
2011/833/UE moyennant attribution. Tout ce qui est rédigé ici (le « dit »,
les constats, les réserves) est du cabinet, et ne prétend pas à l'autorité du
texte : la référence d'article accompagne chaque règle pour qu'on puisse
toujours remonter à la source.

═══════════════════════════════════════════════════════════════════════════
 CE QUE CE MODULE N'EST PAS
═══════════════════════════════════════════════════════════════════════════

Ce n'est NI le registre des systèmes d'IA, NI le registre des traitements.
Les trois cadres de Sentinel comptent trois unités d'analyse différentes, et
les confondre est la faute de fond que ce module évite :

    · l'IA Act compte des SYSTÈMES D'IA, qualifiés par leur usage ;
    · le RGPD compte des TRAITEMENTS, qualifiés par leur finalité ;
    · le CRA compte des PRODUITS, qualifiés par ce qu'ils SONT.

Un même objet peut être les trois — une caméra intelligente est un produit
comportant des éléments numériques, elle embarque un système d'IA, et elle
opère un traitement de données. Trois qualifications, trois registres, trois
jeux d'obligations, et trois rôles qui ne se recouvrent pas : fabricant n'est
pas fournisseur, qui n'est pas responsable de traitement.
"""

import datetime


# ═══════════════════════════════════════════════════════════════════════════
#  LA SOURCE
# ═══════════════════════════════════════════════════════════════════════════

SOURCE = {
    "titre": "Règlement (UE) 2024/2847 du Parlement européen et du Conseil "
             "du 23 octobre 2024 concernant des exigences de cybersécurité "
             "horizontales pour les produits comportant des éléments "
             "numériques (règlement sur la cyberrésilience)",
    "court": "Cyber Resilience Act (CRA)",
    "jo": "JO L du 20.11.2024",
    "eli": "http://data.europa.eu/eli/reg/2024/2847/oj",
    "licence": "Réutilisation autorisée — décision 2011/833/UE, avec "
               "attribution. Seul le texte publié au Journal officiel fait foi.",
    "lu_le": "2026-09-18",
}


# ═══════════════════════════════════════════════════════════════════════════
#  LE CALENDRIER — ET CE QUI EST DÉJÀ EN VIGUEUR
# ═══════════════════════════════════════════════════════════════════════════
#
# POURQUOI CE BLOC EST EN TÊTE DU MODULE ET EN TÊTE DE LA RESTITUTION. Tout
# le discours public sur le CRA parle de « l'échéance de décembre 2027 », et
# cette phrase est fausse deux fois :
#
#   · le chapitre IV — organismes notifiés — est applicable DEPUIS LE
#     11 JUIN 2026 ; c'est le tuyau par lequel devra passer tout produit
#     important de classe II, et il se remplit maintenant ;
#   · l'ARTICLE 14 — signalement des vulnérabilités activement exploitées et
#     des incidents graves — est applicable DEPUIS LE 11 SEPTEMBRE 2026.
#
# Un fabricant qui « attend 2027 » et qui découvre aujourd'hui qu'une de ses
# vulnérabilités est exploitée a VINGT-QUATRE HEURES pour alerter, et il ne le
# sait pas. C'est le seul endroit du règlement où le retard se compte déjà.

ECHEANCES = [
    {"cle": "ch4", "date": "2026-06-11",
     "objet": "Chapitre IV (art. 35 à 51) — notification des organismes "
              "d'évaluation de la conformité",
     "pourquoi": "C'est le tuyau : un produit important de classe II ne peut "
                 "être évalué que par un organisme notifié, et ces organismes "
                 "ne sont désignés que depuis cette date.",
     "article": "art. 71, §2"},
    {"cle": "art14", "date": "2026-09-11",
     "objet": "Article 14 — signalement des vulnérabilités activement "
              "exploitées et des incidents graves",
     "pourquoi": "La seule obligation dont le retard se compte DÉJÀ : 24 h "
                 "pour l'alerte précoce, 72 h pour la notification.",
     "article": "art. 71, §2"},
    {"cle": "general", "date": "2027-12-11",
     "objet": "Application générale du règlement",
     "pourquoi": "Marquage CE, déclaration UE de conformité, documentation "
                 "technique, exigences essentielles de l'annexe I.",
     "article": "art. 71, §2"},
]


def _jour(s):
    a, m, j = (int(x) for x in s.split("-"))
    return datetime.date(a, m, j)


def calendrier(aujourdhui=None):
    """Les échéances, et lesquelles sont DÉJÀ passées.

    `aujourdhui` est injecté — sans quoi ce module serait intestable : une
    règle qui vérifie « l'article 14 est en vigueur » passerait pour la seule
    raison que l'horloge de la machine est après le 11 septembre 2026, et
    aurait échoué la veille sans que rien n'ait changé dans le code.
    """
    d = aujourdhui or datetime.date.today()
    if isinstance(d, str):
        d = _jour(d)
    out = []
    for e in ECHEANCES:
        quand = _jour(e["date"])
        out.append(dict(e, applicable=quand <= d,
                        jours=(d - quand).days if quand <= d
                        else -(quand - d).days))
    return {"date": d.isoformat(), "echeances": out,
            "en_vigueur": [e for e in out if e["applicable"]],
            "a_venir": [e for e in out if not e["applicable"]]}


# ═══════════════════════════════════════════════════════════════════════════
#  LE PÉRIMÈTRE — ET CE QUI EN SORT
# ═══════════════════════════════════════════════════════════════════════════
#
# LE CRITÈRE TERRITORIAL N'EST PAS LE LIEU D'ÉTABLISSEMENT. Le règlement
# s'applique dès que le produit est mis à disposition sur le marché de
# l'Union, à titre onéreux OU GRATUIT. Un fabricant hors Union y est soumis si
# son produit est destiné au marché européen ; un fabricant français ne l'est
# pas pour un produit qu'il ne vend qu'ailleurs. C'est le produit qui décide,
# pas le siège.

EXCLUSIONS = [
    {"cle": "medical", "nom": "Dispositif médical / diagnostic in vitro",
     "renvoi": "règlements (UE) 2017/745 et 2017/746", "article": "art. 2, §2"},
    {"cle": "aviation", "nom": "Produit certifié en aviation civile",
     "renvoi": "règlement (UE) 2018/1139", "article": "art. 2, §3"},
    {"cle": "vehicule", "nom": "Produit destiné aux véhicules à moteur et "
                               "à leurs remorques",
     "renvoi": "règlement (UE) 2019/2144", "article": "art. 2, §4"},
    {"cle": "marin", "nom": "Équipement marin",
     "renvoi": "directive 2014/90/UE", "article": "art. 2, §5"},
    {"cle": "rechange", "nom": "Pièce de rechange fabriquée aux mêmes "
                               "spécifications que le composant remplacé",
     "renvoi": "—", "article": "art. 2, §6"},
    {"cle": "defense", "nom": "Produit développé ou modifié exclusivement à "
                              "des fins de sécurité nationale ou de défense",
     "renvoi": "—", "article": "art. 2, §7"},
    {"cle": "classifie", "nom": "Produit conçu pour traiter des informations "
                                "classifiées",
     "renvoi": "—", "article": "art. 2, §7"},
]

#: LA CLAUSE GÉNÉRALE, TENUE À PART DES SEPT AUTRES — ET CE N'EST PAS UN
#: DÉTAIL DE RANGEMENT. Les sept exclusions ci-dessus se constatent : on
#: regarde le produit, on sait. Celle-ci s'APPRÉCIE — « d'autres règles de
#: l'Union couvrent tout ou partie des mêmes risques, à un niveau de
#: protection identique ou supérieur ». Personne ne peut cocher cela depuis un
#: écran. La mêler aux autres aurait laissé croire qu'un produit sort du CRA
#: parce qu'un utilisateur a coché une case.
CLAUSE_GENERALE = {
    "cle": "autre_droit_union",
    "nom": "Autres règles de l'Union couvrant les mêmes risques à un niveau "
           "au moins équivalent",
    "article": "art. 2, §8",
    "dit": "Cette exclusion ne se coche pas : elle s'établit texte contre "
           "texte, risque par risque, au regard des exigences essentielles de "
           "l'annexe I. Elle appelle une analyse juridique, pas une "
           "déclaration.",
}


# ═══════════════════════════════════════════════════════════════════════════
#  LES CLASSES — ANNEXES III ET IV
# ═══════════════════════════════════════════════════════════════════════════
#
# LES LIBELLÉS SONT CEUX DU RÈGLEMENT, et c'est voulu : un client doit pouvoir
# retrouver sa catégorie dans le texte, mot pour mot, quand il la conteste.
# Ce qui est du cabinet, c'est le classement en quatre niveaux et tout ce que
# le module en DÉDUIT.

ANNEXE_III_I = (
    "Systèmes de gestion des identités, logiciels et dispositifs de gestion "
    "des accès privilégiés (dont lecteurs d'authentification, de contrôle "
    "d'accès et biométriques)",
    "Navigateurs autonomes et intégrés",
    "Gestionnaires de mots de passe",
    "Logiciels qui recherchent, suppriment ou mettent en quarantaine des "
    "logiciels malveillants",
    "Produits avec fonction de réseau privé virtuel (VPN)",
    "Systèmes de gestion de la qualité",
    "Systèmes de gestion des informations et des événements de sécurité (SIEM)",
    "Gestionnaires de démarrage",
    "Infrastructure à clé publique et logiciels d'émission de certificats "
    "numériques",
    "Interfaces réseau physiques et virtuelles",
    "Systèmes d'exploitation",
    "Routeurs, modems destinés à la connexion à l'internet et commutateurs",
    "Microprocesseurs dotés de fonctionnalités liées à la sécurité",
    "Microcontrôleurs dotés de fonctionnalités liées à la sécurité",
    "Circuits intégrés spécifiques (ASIC) et réseaux de portes programmables "
    "(FPGA) dotés de fonctionnalités liées à la sécurité",
    "Assistants virtuels polyvalents pour maison intelligente",
    "Produits domestiques intelligents dotés de fonctionnalités de sécurité "
    "(serrures, caméras, surveillance pour bébé, alarmes)",
    "Jouets connectés à caractéristiques sociales interactives ou à fonctions "
    "de localisation",
    "Produits portables personnels de surveillance de la santé hors "
    "règlements (UE) 2017/745 et 2017/746, ou destinés aux enfants",
)

ANNEXE_III_II = (
    "Hyperviseurs et systèmes d'exécution de conteneurs",
    "Pare-feu, systèmes de détection et de prévention des intrusions",
    "Microprocesseurs résistants aux manipulations",
    "Microcontrôleurs résistants aux manipulations",
)

ANNEXE_IV = (
    "Dispositifs matériels avec boîtier de sécurité",
    "Passerelles pour compteur intelligent au sein des systèmes intelligents "
    "de mesure, et autres dispositifs à des fins de sécurité avancées",
    "Cartes à puce ou dispositifs similaires, y compris éléments sécurisés",
)

CLASSES = {
    "ordinaire": {
        "rang": 0, "nom": "Produit comportant des éléments numériques",
        "dit": "Ni important ni critique : le fabricant démontre lui-même sa "
               "conformité.",
        "article": "art. 32, §1",
    },
    "important_i": {
        "rang": 1, "nom": "Produit important — classe I (annexe III)",
        "dit": "Auto-évaluable SI le fabricant applique intégralement les "
               "normes harmonisées, spécifications communes ou schémas de "
               "certification pertinents. Sinon, organisme notifié.",
        "article": "art. 7, §1 · annexe III · art. 32, §2",
    },
    "important_ii": {
        "rang": 2, "nom": "Produit important — classe II (annexe III)",
        "dit": "Organisme notifié dans tous les cas : le contrôle interne "
               "seul n'est jamais ouvert.",
        "article": "art. 7, §1 · annexe III · art. 32, §3",
    },
    "critique": {
        "rang": 3, "nom": "Produit critique (annexe IV)",
        "dit": "Le niveau le plus exigeant du règlement, adossé à un schéma "
               "européen de certification de cybersécurité.",
        "article": "art. 8 · annexe IV · art. 32, §4",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
#  LES PROCÉDURES — ANNEXE VIII, APPELÉES PAR L'ARTICLE 32
# ═══════════════════════════════════════════════════════════════════════════

PROCEDURES = {
    "A": {"nom": "Contrôle interne (module A)",
          "organisme_notifie": False,
          "dit": "Le fabricant évalue, établit la documentation technique, "
                 "signe la déclaration UE de conformité et appose le "
                 "marquage CE. Aucun tiers n'intervient.",
          "article": "annexe VIII, partie I"},
    "B+C": {"nom": "Examen UE de type (module B) + conformité au type sur "
                   "contrôle interne de la production (module C)",
            "organisme_notifie": True,
            "dit": "Un organisme notifié examine le type, puis le fabricant "
                   "garantit la conformité de la production à ce type.",
            "article": "annexe VIII, parties II et III"},
    "H": {"nom": "Assurance complète de la qualité (module H)",
          "organisme_notifie": True,
          "dit": "Un organisme notifié approuve et surveille le système "
                 "qualité couvrant conception, fabrication et contrôle.",
          "article": "annexe VIII, partie IV"},
    "CERT": {"nom": "Schéma européen de certification de cybersécurité "
                    "(niveau d'assurance au moins « substantiel »)",
             "organisme_notifie": True,
             "dit": "Certification au titre du règlement (UE) 2019/881, "
                    "lorsqu'un schéma est disponible et pertinent.",
             "article": "art. 27, §9 · art. 32"},
}


def procedures_ouvertes(classe, normes_harmonisees=False):
    """LES PROCÉDURES OUVERTES À CE PRODUIT — le calcul qui commande le budget.

    `normes_harmonisees` : le fabricant applique-t-il INTÉGRALEMENT les normes
    harmonisées, spécifications communes ou schémas de certification
    pertinents ? La question ne se pose QUE pour la classe I, et c'est là que
    se joue la bascule la plus coûteuse du règlement.

    ═══ POURQUOI « INTÉGRALEMENT » ET PAS « EN PARTIE » ══════════════════
    L'article 32, §2 vise trois cas d'une seule voix : le fabricant n'a pas
    appliqué les normes, ne les a appliquées QU'EN PARTIE, ou ces normes
    N'EXISTENT PAS. Les trois basculent le produit chez l'organisme notifié.
    Un module qui accepterait « partiellement » comme une réponse suffisante
    laisserait un fabricant de classe I croire qu'il s'auto-évalue, jusqu'au
    jour où une autorité de surveillance lui demande sur quelle norme il
    s'appuie.
    """
    if classe == "critique":
        return ["CERT"]
    if classe == "important_ii":
        return ["B+C", "H", "CERT"]
    if classe == "important_i":
        return ["A"] if normes_harmonisees else ["B+C", "H"]
    return ["A"]


# ═══════════════════════════════════════════════════════════════════════════
#  LES RÔLES DE LA CHAÎNE DE VALEUR
# ═══════════════════════════════════════════════════════════════════════════
#
# UN MÊME ACTEUR PEUT CHANGER DE RÔLE SANS CHANGER DE MÉTIER, et c'est le
# piège que ce tableau existe pour montrer. Un distributeur qui appose sa
# marque sur un produit, ou qui le modifie substantiellement, DEVIENT
# fabricant — avec toutes les obligations qui vont avec, y compris le
# signalement en 24 heures. Beaucoup d'intégrateurs et de revendeurs sous
# marque propre ignorent qu'ils sont dans ce cas.

ROLES = {
    "fabricant": {
        "nom": "Fabricant",
        "rang": 0,
        "dit": "Conçoit ou fait concevoir le produit et le met sur le marché "
               "sous son nom ou sa marque.",
        "porte": ["exigences essentielles (annexe I)",
                  "évaluation des risques de cybersécurité",
                  "documentation technique (annexe VII)",
                  "déclaration UE de conformité (annexe V)",
                  "marquage CE",
                  "signalement art. 14 (24 h / 72 h)",
                  "période d'assistance et mises à jour de sécurité"],
        "article": "art. 13 · art. 14",
        "palier": "lourd",
    },
    "importateur": {
        "nom": "Importateur",
        "rang": 1,
        "dit": "Établi dans l'Union, met sur le marché un produit d'un "
               "fabricant établi hors de l'Union.",
        # CE QUE L'IMPORTATEUR DOIT VÉRIFIER AVANT DE METTRE SUR LE MARCHÉ,
        # point par point du texte — et non « vérifier que le fabricant a fait
        # ce qu'il devait », qui ne dit pas quoi regarder.
        "porte": ["la procédure d'évaluation de la conformité a bien été menée "
                  "à bien par le fabricant (art. 32)",
                  "le fabricant a établi la documentation technique",
                  "le marquage CE est apposé, la déclaration UE de conformité "
                  "et les instructions de l'annexe II accompagnent le produit",
                  "ces informations sont RÉDIGÉES DANS UNE LANGUE aisément "
                  "compréhensible par les utilisateurs ET par les autorités "
                  "de surveillance",
                  "être EN MESURE DE FOURNIR les documents qui le prouvent",
                  "informer le fabricant et les autorités d'un risque "
                  "important, y compris tiré de facteurs NON TECHNIQUES"],
        "article": "art. 19",
        "palier": "moyen",
    },
    "distributeur": {
        "nom": "Distributeur",
        "rang": 2,
        "dit": "Met un produit à disposition sur le marché sans être ni "
               "fabricant ni importateur.",
        "porte": ["agir avec la diligence requise",
                  "vérifier que le marquage CE est apposé",
                  "vérifier que le fabricant ET l'importateur se sont conformés "
                  "à leurs obligations, et que tous les documents nécessaires "
                  "lui ont été COMMUNIQUÉS",
                  "ne pas mettre à disposition tant qu'un produit qu'il croit "
                  "non conforme n'a pas été mis en conformité",
                  "informer sans retard injustifié en cas de risque important",
                  "faire prendre les mesures correctives, ou faire retirer"],
        "article": "art. 20",
        "palier": "moyen",
    },
    "requalifie": {
        "nom": "Requalifié fabricant (art. 21)",
        "rang": 3,
        "dit": "Un importateur ou un distributeur qui met le produit sur le "
               "marché sous SON propre nom ou SA propre marque, ou qui y "
               "apporte une modification substantielle, EST un fabricant au "
               "sens du règlement.",
        "porte": ["toutes les obligations des articles 13 et 14",
                  "y compris le signalement en 24 h, déjà applicable"],
        "article": "art. 21",
        "palier": "lourd",
    },
    # ═══ L'ACTEUR QUE LA PREMIÈRE VERSION DE CETTE TABLE N'AVAIT PAS ═══
    #
    # L'article 22 ne vise NI le fabricant, NI l'importateur, NI le
    # distributeur : il vise « une personne physique ou morale, autre que »
    # ceux-là, qui apporte une modification substantielle et met le produit à
    # disposition. C'est l'intégrateur, l'infogéreur, le maître d'œuvre qui
    # livre une solution assemblée — et c'est le rôle le plus fréquemment
    # ignoré, parce que celui qui l'exerce ne se pense pas « fabricant ».
    #
    # ET SA PORTÉE N'EST PAS CELLE DES AUTRES. Il répond pour LA PARTIE
    # modifiée — ou pour LE PRODUIT ENTIER si la modification a des
    # répercussions sur la cybersécurité de l'ensemble. Cette nuance-là décide
    # de l'étendue de la documentation technique à produire, donc du coût.
    "integrateur": {
        "nom": "Intégrateur — modification substantielle (art. 22)",
        "rang": 4,
        "dit": "Toute personne, autre que le fabricant, l'importateur ou le "
               "distributeur, qui apporte une modification substantielle à un "
               "produit déjà sur le marché et le met à disposition.",
        "porte": ["les obligations des articles 13 et 14 SUR LA PARTIE "
                  "modifiée",
                  "ou SUR LE PRODUIT ENTIER si la modification a des "
                  "répercussions sur sa cybersécurité d'ensemble"],
        "article": "art. 22",
        "palier": "lourd",
    },
}

#: CE QUE TOUS PORTENT, QUEL QUE SOIT LE RÔLE — et qui n'est dans aucune
#: fiche ci-dessus parce que le rattacher à l'une d'elles laisserait croire
#: que les autres en sont dispensées.
TRACABILITE = {
    "nom": "Identification des opérateurs économiques",
    "dit": "Sur demande des autorités de surveillance : le nom et l'adresse "
           "de qui vous a fourni le produit, et de qui vous l'avez fourni. "
           "Cela suppose de le savoir — donc de l'avoir consigné au moment de "
           "la transaction, pas au moment de la demande.",
    "article": "art. 23",
}


def qualifier_role(declaration=None):
    """QUEL RÔLE LE RÈGLEMENT VOUS DONNE — et non celui que vous croyez avoir.

    ═══ POURQUOI CETTE FONCTION EXISTE ═══════════════════════════════════
    Le CRA ne demande pas comment vous vous appelez : il regarde ce que vous
    FAITES du produit. Deux gestes ordinaires du commerce changent le rôle
    sans changer le métier :

      · apposer SON nom ou SA marque sur un produit qu'on revend ;
      · apporter une MODIFICATION SUBSTANTIELLE à un produit déjà sur le
        marché.

    L'un et l'autre font de vous un fabricant — avec la documentation
    technique, la déclaration UE de conformité, et le signalement en
    vingt-quatre heures qui est déjà applicable. Un revendeur sous marque
    propre, un infogéreur qui durcit un équipement, un intégrateur qui livre
    une solution assemblée sont dans ce cas et l'ignorent le plus souvent.

    ═══ CE QU'ELLE REND, ET POURQUOI PAS SEULEMENT UN RÔLE ═══════════════
    Elle rend le rôle ET le chemin qui y mène, question par question. Un
    verdict sans son chemin ne se conteste pas — or celui-ci doit pouvoir
    l'être : c'est une qualification juridique, et elle se vérifie sur les
    faits réels, pas sur des cases.
    """
    d = declaration or {}
    trace = []

    def noter(question, reponse, effet):
        trace.append({"question": question, "reponse": bool(reponse),
                      "effet": effet})
        return bool(reponse)

    marque = noter("Mettez-vous le produit sur le marché sous VOTRE nom ou "
                   "VOTRE marque ?", d.get("sous_ma_marque"),
                   "art. 21 — vous êtes fabricant")
    modif = noter("Apportez-vous une MODIFICATION SUBSTANTIELLE à un produit "
                  "déjà mis sur le marché ?", d.get("modification_substantielle"),
                  "art. 21 ou 22 — vous êtes fabricant pour ce que vous modifiez")
    concoit = noter("Concevez-vous ou faites-vous concevoir ce produit ?",
                    d.get("je_concois"), "art. 3 — vous êtes fabricant d'origine")
    importe = noter("Le fabricant est-il établi HORS de l'Union, et "
                    "mettez-vous vous-même le produit sur le marché de "
                    "l'Union ?", d.get("fabricant_hors_union"),
                    "art. 19 — vous êtes importateur")

    # ═══ L'ORDRE DE CES TESTS EST CELUI DU RÈGLEMENT, PAS LE PLUS COMMODE.
    # La requalification PRIME : un importateur qui appose sa marque n'est
    # pas « importateur ET un peu fabricant », il EST fabricant. Tester
    # l'import d'abord aurait rendu « importateur » et masqué la seule
    # réponse qui change quelque chose.
    if concoit and not modif:
        cle, pourquoi = "fabricant", "Vous concevez le produit et le mettez " \
            "sur le marché : vous êtes fabricant d'origine."
    elif marque or (modif and (importe or d.get("je_distribue"))):
        cle, pourquoi = "requalifie", "Vous apposez votre marque ou vous " \
            "modifiez substantiellement un produit que vous revendez : le " \
            "règlement vous tient pour fabricant."
    elif modif:
        cle, pourquoi = "integrateur", "Vous n'êtes ni le fabricant, ni " \
            "l'importateur, ni le distributeur, et vous modifiez " \
            "substantiellement : l'article 22 vous tient pour fabricant."
    elif importe:
        cle, pourquoi = "importateur", "Vous mettez sur le marché de l'Union " \
            "un produit d'un fabricant établi hors de l'Union."
    else:
        cle, pourquoi = "distributeur", "Vous mettez le produit à disposition " \
            "sans le concevoir, l'importer, le marquer ni le modifier."

    etendue = None
    if cle in ("integrateur", "requalifie") and modif:
        # LA NUANCE QUI DÉCIDE DU COÛT. L'article 22, §2 borne l'obligation à
        # la PARTIE modifiée — sauf si la modification a des répercussions sur
        # la cybersécurité du produit dans son ensemble, auquel cas elle porte
        # sur le produit entier. Entre les deux, l'étendue de la documentation
        # technique à produire n'est pas du même ordre.
        ensemble = bool(d.get("modification_affecte_ensemble"))
        etendue = {
            "ensemble": ensemble,
            "dit": ("La modification a des répercussions sur la cybersécurité "
                    "de l'ensemble : vos obligations portent sur LE PRODUIT "
                    "ENTIER." if ensemble else
                    "Vos obligations portent sur LA PARTIE modifiée — à "
                    "condition que la modification n'ait pas de répercussions "
                    "sur la cybersécurité de l'ensemble du produit."),
            "article": "art. 22, §2",
        }
    return {"ok": True, "role": dict(ROLES[cle], cle=cle), "pourquoi": pourquoi,
            "etendue": etendue, "trace": trace, "tracabilite": TRACABILITE,
            "reserve": "Cette qualification suit ce qui est déclaré. Elle "
                       "s'établit en droit sur les faits réels — notamment la "
                       "notion de « modification substantielle », qui "
                       "s'apprécie au regard de la cybersécurité du produit "
                       "et non de l'ampleur technique du changement.",
            "source": SOURCE}


# ═══════════════════════════════════════════════════════════════════════════
#  L'ARTICLE 64 — CE QUE LE RÈGLEMENT CHIFFRE LUI-MÊME
# ═══════════════════════════════════════════════════════════════════════════
#
# POURQUOI CE MODULE NE CHIFFRE QUE CELA. On lui a demandé un « parcours
# chiffré », et il y a deux façons de le faire. La première consiste à
# estimer un coût de mise en conformité — tant de jours-homme, tant pour un
# organisme notifié. Aucun de ces chiffres n'est dans le règlement, aucun
# n'est public de façon fiable, et les inventer donnerait un document qui a
# l'air d'un devis sans en être un : c'est la pire des deux erreurs, parce
# qu'il serait cité en comité.
#
# LA SECONDE CONSISTE À CHIFFRER CE QUE LE TEXTE CHIFFRE. L'article 64 pose
# trois paliers d'amende, en euros et en pourcentage du chiffre d'affaires
# mondial, « le montant le plus élevé étant retenu ». C'est exact, c'est
# opposable, et cela se calcule à partir d'une seule donnée que le client
# possède : son chiffre d'affaires. Le reste — nombre de produits chez
# l'organisme notifié, jours restants, exigences non couvertes — sort déjà
# des autres écrans.
#
# LE SEUIL QUE PRESQUE TOUS LES RÉSUMÉS OUBLIENT. « 15 millions OU 2,5 % »
# n'est pas un choix de l'autorité : c'est le plus élevé des deux. Il existe
# donc un chiffre d'affaires en dessous duquel le montant fixe commande
# TOUJOURS, et au-dessus duquel le pourcentage prend le relais. Pour le
# palier lourd, ce basculement se fait à 600 millions d'euros. Une PME qui
# lit « 2,5 % de mon chiffre d'affaires » se rassure à tort : c'est
# 15 millions qui s'appliquent à elle.

SANCTIONS = {
    "lourd": {
        "rang": 0,
        "nom": "Exigences essentielles et obligations du fabricant",
        "vise": "Le non-respect des exigences essentielles de cybersécurité "
                "de l'annexe I et des obligations des articles 13 et 14.",
        "plafond_eur": 15000000,
        "part_ca": 0.025,
        "article": "art. 64, §2",
    },
    "moyen": {
        "rang": 1,
        "nom": "Obligations des autres opérateurs et de la procédure",
        "vise": "Le non-respect des obligations des articles 18 à 23, 28, "
                "30 §1-4, 31 §1-4, 32 §1-2-3, 33 §5, 39, 41, 47, 49 et 53.",
        "plafond_eur": 10000000,
        "part_ca": 0.02,
        "article": "art. 64, §3",
    },
    "leger": {
        "rang": 2,
        "nom": "Informations inexactes aux organismes notifiés et aux autorités",
        "vise": "La fourniture d'informations inexactes, incomplètes ou "
                "trompeuses aux organismes notifiés et aux autorités de "
                "surveillance du marché, en réponse à une demande.",
        "plafond_eur": 5000000,
        "part_ca": 0.01,
        "article": "art. 64, §4",
    },
}

#: CE QUE L'AUTORITÉ PREND EN COMPTE POUR FIXER LE MONTANT — et qui interdit
#: de présenter le plafond comme une prévision. Repris de l'article 64, §5.
MODULATION = (
    "la nature, la gravité et la durée de l'infraction et de ses conséquences",
    "l'existence d'amendes déjà infligées au même opérateur pour une "
    "infraction similaire",
    "la taille de l'entreprise, en particulier s'il s'agit d'une micro, "
    "petite ou moyenne entreprise, y compris une jeune entreprise",
)


def seuil_de_bascule(palier):
    """LE CHIFFRE D'AFFAIRES À PARTIR DUQUEL LE POURCENTAGE COMMANDE.

    En dessous, le montant fixe s'applique toujours ; au-dessus, le
    pourcentage. C'est la seule façon de répondre honnêtement à « combien
    est-ce que je risque » — une PME à qui l'on cite « 2,5 % du chiffre
    d'affaires » entend un chiffre dix fois trop bas.
    """
    p = SANCTIONS[palier]
    return int(round(p["plafond_eur"] / p["part_ca"]))


def exposition(chiffre_affaires=None, paliers=None):
    """L'exposition maximale, palier par palier, pour un chiffre d'affaires.

    `paliers` restreint aux paliers réellement en cause ; sans lui, les trois
    sont rendus — parce qu'un opérateur qui ne sait pas encore lesquels le
    concernent doit voir les trois avant de choisir.

    ═══ CE QUE CETTE FONCTION REFUSE DE FAIRE ════════════════════════════
    Elle ne rend JAMAIS un montant unique. L'article 64, §5 impose de tenir
    compte de la nature de l'infraction, de sa durée, des antécédents et de
    la taille de l'entreprise : un plafond n'est pas une prévision, et
    l'afficher seul le ferait lire comme tel. Chaque ligne porte donc le
    plafond ET ce qui le module.

    SANS CHIFFRE D'AFFAIRES, ELLE REND LE MONTANT FIXE ET LE DIT. Elle ne
    suppose pas zéro : un chiffre d'affaires inconnu traité comme nul
    donnerait l'exposition d'une entreprise sans activité.
    """
    ca = None
    if chiffre_affaires is not None:
        try:
            ca = float(chiffre_affaires)
        except (TypeError, ValueError):
            ca = None
        if ca is not None and ca < 0:
            ca = None
    cles = [c for c in (paliers or SANCTIONS) if c in SANCTIONS]
    cles.sort(key=lambda c: SANCTIONS[c]["rang"])
    lignes = []
    for c in cles:
        p = SANCTIONS[c]
        part = None if ca is None else ca * p["part_ca"]
        retenu = p["plafond_eur"] if part is None else max(p["plafond_eur"], part)
        lignes.append({
            "cle": c, "nom": p["nom"], "vise": p["vise"],
            "article": p["article"],
            "plafond_eur": p["plafond_eur"], "part_ca": p["part_ca"],
            "montant_part": part,
            "retenu_eur": retenu,
            # CE QUI COMMANDE, NOMMÉ. « Le montant le plus élevé étant
            # retenu » est la phrase du texte ; dire LEQUEL commande pour CE
            # chiffre d'affaires est ce qui la rend utilisable.
            "commande": ("montant_fixe" if part is None or p["plafond_eur"] >= part
                         else "pourcentage"),
            "seuil_bascule_eur": seuil_de_bascule(c),
        })
    return {
        "ok": True,
        "chiffre_affaires": ca,
        "ca_declare": ca is not None,
        "lignes": lignes,
        "modulation": MODULATION,
        "reserve": "Ces montants sont des PLAFONDS, pas des prévisions. "
                   "L'article 64, §5 impose de tenir compte de la nature, de "
                   "la gravité et de la durée de l'infraction, des "
                   "antécédents de l'opérateur et de sa taille. Le régime de "
                   "sanctions lui-même est fixé par chaque État membre.",
        "article": "art. 64",
        "source": SOURCE,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  L'ARTICLE 14 — LE SEUL COMPTE À REBOURS DÉJÀ EN MARCHE
# ═══════════════════════════════════════════════════════════════════════════
#
# DEUX FAITS DÉCLENCHEURS, TROIS ÉCHÉANCES CHACUN, ET LE MÊME DOUBLE
# DESTINATAIRE. Ce qui se retient mal et coûte cher : la notification part
# SIMULTANÉMENT au CSIRT désigné coordinateur ET à l'ENISA, par la
# plateforme unique de signalement de l'article 16. Prévenir l'un puis
# l'autre, ou l'un seulement, n'est pas ce que le texte demande.

SIGNALEMENT = {
    "vulnerabilite": {
        "nom": "Vulnérabilité activement exploitée",
        "declencheur": "Le fabricant prend connaissance d'une vulnérabilité "
                       "de son produit qui est activement exploitée.",
        "etapes": [
            {"cle": "alerte", "delai_h": 24,
             "nom": "Alerte précoce",
             "contenu": "Signalement sans retard injustifié, en indiquant le "
                        "cas échéant les États membres où le produit a été "
                        "mis à disposition."},
            {"cle": "notification", "delai_h": 72,
             "nom": "Notification de vulnérabilité",
             "contenu": "Informations générales sur le produit, nature de "
                        "l'exploitation et de la vulnérabilité, mesures "
                        "correctives prises et celles que les utilisateurs "
                        "peuvent prendre."},
            {"cle": "final", "delai_h": 14 * 24,
             "depuis": "la mise à disposition d'une mesure de correction ou "
                       "d'atténuation",
             "nom": "Rapport final",
             "contenu": "Description de la vulnérabilité, gravité et "
                        "répercussions, acteur malveillant le cas échéant, "
                        "précisions sur le correctif."},
        ],
        "article": "art. 14, §1 et §2",
    },
    "incident": {
        "nom": "Incident grave ayant des répercussions sur la sécurité du "
               "produit",
        "declencheur": "Le fabricant prend connaissance d'un incident grave "
                       "affectant la sécurité du produit.",
        "etapes": [
            {"cle": "alerte", "delai_h": 24,
             "nom": "Alerte précoce",
             "contenu": "Indiquant au minimum si l'incident pourrait avoir "
                        "été causé par des actes illicites ou malveillants."},
            {"cle": "notification", "delai_h": 72,
             "nom": "Notification d'incident",
             "contenu": "Nature de l'incident, évaluation initiale, mesures "
                        "correctives prises et celles que les utilisateurs "
                        "peuvent prendre."},
            {"cle": "final", "delai_h": 30 * 24,
             "depuis": "la notification d'incident",
             "nom": "Rapport final",
             "contenu": "Description détaillée, gravité et répercussions, "
                        "type de menace ou cause profonde, mesures "
                        "d'atténuation appliquées et en cours."},
        ],
        "article": "art. 14, §3 et §4",
    },
}

DESTINATAIRES = {
    "dit": "Le CSIRT désigné comme coordinateur ET l'ENISA, SIMULTANÉMENT, "
           "par la plateforme unique de signalement.",
    "article": "art. 14, §1 et §3 · art. 16",
}


# ═══════════════════════════════════════════════════════════════════════════
#  LES EXIGENCES ESSENTIELLES — ANNEXE I, LES DEUX PARTIES
# ═══════════════════════════════════════════════════════════════════════════
#
# DEUX PARTIES QUI NE SE COTENT PAS DE LA MÊME FAÇON, et les confondre
# vaudrait une analyse d'écart fausse. La partie I porte sur les PROPRIÉTÉS
# du produit — elle se vérifie sur une version donnée. La partie II porte sur
# des PROCESSUS du fabricant — elle se vérifie sur une organisation, et elle
# vaut pendant toute la période d'assistance, pas au moment de la mise sur le
# marché. Un produit peut être conforme partie I et l'entreprise défaillante
# partie II : c'est même le cas le plus courant.

ANNEXE_I_I = (
    ("ei-01", "Niveau de cybersécurité approprié aux risques",
     "Conception, développement et fabrication garantissant un niveau "
     "approprié en fonction des risques."),
    ("ei-02", "Aucune vulnérabilité exploitable connue à la mise sur le marché",
     "Le produit est mis à disposition sans vulnérabilité exploitable connue."),
    ("ei-03", "Configuration de sécurité par défaut",
     "État sûr à la livraison, avec possibilité de réinitialisation à l'état "
     "d'origine ; dérogation possible pour un produit sur mesure."),
    ("ei-04", "Correction par mises à jour de sécurité",
     "Vulnérabilités corrigeables par mise à jour, y compris automatique et "
     "activée par défaut mais désactivable."),
    ("ei-05", "Protection contre l'accès non autorisé",
     "Mécanismes de contrôle d'accès et d'authentification appropriés."),
    ("ei-06", "Confidentialité des données",
     "Protection des données au repos, en transit et en traitement, par "
     "chiffrement ou autre moyen adapté."),
    ("ei-07", "Intégrité des données, commandes et configuration",
     "Protection contre la manipulation ou la modification non autorisée."),
    ("ei-08", "Minimisation des données",
     "Traitement limité aux données adéquates, pertinentes et nécessaires à "
     "l'utilisation prévue."),
    ("ei-09", "Disponibilité des fonctions essentielles",
     "Résilience et atténuation des effets des attaques par déni de service."),
    ("ei-10", "Limitation des surfaces d'attaque",
     "Réduction des interfaces exposées, y compris externes."),
    ("ei-11", "Réduction de l'impact d'un incident",
     "Techniques et mesures d'atténuation limitant la portée d'une "
     "compromission."),
    ("ei-12", "Enregistrement et surveillance de l'activité",
     "Journalisation des accès et modifications pertinents pour la sécurité, "
     "avec possibilité de désactivation."),
    ("ei-13", "Suppression sécurisée des données et paramètres",
     "Possibilité pour l'utilisateur d'effacer données et configuration de "
     "façon sûre et facile, et de les transférer."),
)

ANNEXE_I_II = (
    ("gv-01", "Nomenclature des logiciels (SBOM)",
     "Recensement et documentation des vulnérabilités et des composants, par "
     "une nomenclature lisible par machine couvrant au moins les dépendances "
     "de niveau supérieur."),
    ("gv-02", "Correction sans retard",
     "Gestion et correction des vulnérabilités sans retard, par mises à jour "
     "de sécurité fournies séparément des mises à jour de fonctionnalité "
     "quand c'est techniquement possible."),
    ("gv-03", "Tests et examens de sécurité réguliers",
     "Le produit est soumis régulièrement à des tests et examens efficaces."),
    ("gv-04", "Communication sur les vulnérabilités corrigées",
     "À la publication d'une mise à jour : description, identification du "
     "produit, conséquences, gravité, et aide à la remédiation."),
    ("gv-05", "Politique de divulgation coordonnée",
     "Une politique de divulgation coordonnée des vulnérabilités est établie "
     "et appliquée."),
    ("gv-06", "Adresse de contact pour le signalement",
     "Point de contact permettant à un tiers de signaler une vulnérabilité "
     "découverte, et partage d'informations sur les composants tiers."),
    ("gv-07", "Distribution sécurisée des mises à jour",
     "Mécanismes garantissant que les correctifs parviennent aux produits de "
     "façon sûre et rapide."),
    ("gv-08", "Diffusion gratuite et sans délai des correctifs",
     "Les mises à jour correctives sont diffusées sans délai et à titre "
     "gratuit, accompagnées d'un avis informant les utilisateurs."),
)


# ═══════════════════════════════════════════════════════════════════════════
#  L'ÉVALUATION D'UN PRODUIT
# ═══════════════════════════════════════════════════════════════════════════

_ETATS = ("conforme", "partiel", "absent", "sans_objet")


def evaluer_produit(produit=None, aujourdhui=None):
    """Un produit déclaré → son périmètre, sa classe, sa route, ses écarts.

    `produit` attend :
      nom, marche_ue (bool), exclusions (list[cle]), classe (cle de CLASSES),
      role (cle de ROLES), normes_harmonisees (bool),
      ecarts : {cle d'exigence: état}

    ═══ CE QUE CETTE FONCTION REFUSE DE DÉDUIRE ══════════════════════════
    Elle ne devine PAS la classe à partir du nom du produit. Un moteur qui
    rangerait « notre passerelle » en classe I sur la foi d'un mot rendrait
    un verdict que personne ne pourrait contester — et la classe commande la
    procédure, donc le budget. La classe est DÉCLARÉE, l'annexe est affichée
    à côté pour qu'on la choisisse en connaissance de cause, et la
    restitution rappelle qui l'a choisie.
    """
    p = produit or {}
    nom = str(p.get("nom") or "").strip()
    if not nom:
        return {"ok": False, "motif": "produit_sans_nom"}

    # ── LE PÉRIMÈTRE ─────────────────────────────────────────────────────
    sur_le_marche = bool(p.get("marche_ue"))
    exclus = [e for e in EXCLUSIONS
              if e["cle"] in set(p.get("exclusions") or ())]
    if not sur_le_marche:
        perimetre = {"dans": False, "motif": "hors_marche_ue",
                     "dit": "Le produit n'est pas déclaré mis à disposition "
                            "sur le marché de l'Union. Le règlement ne "
                            "s'applique pas — et c'est le PRODUIT qui décide, "
                            "pas le lieu d'établissement : la réponse change "
                            "le jour où il y est vendu, fût-ce gratuitement.",
                     "exclusions": []}
    elif exclus:
        perimetre = {"dans": False, "motif": "exclusion_sectorielle",
                     "dit": "Un cadre sectoriel déclaré prend le pas. Cette "
                            "qualification est une question de droit : elle "
                            "se vérifie sur le produit réel, pas sur une case "
                            "cochée.",
                     "exclusions": exclus}
    else:
        perimetre = {"dans": True, "motif": "", "dit": "", "exclusions": []}

    # ── LA CLASSE ET LA ROUTE ────────────────────────────────────────────
    classe = p.get("classe") if p.get("classe") in CLASSES else "ordinaire"
    harmonisees = bool(p.get("normes_harmonisees"))
    routes = procedures_ouvertes(classe, harmonisees)
    organisme = all(PROCEDURES[r]["organisme_notifie"] for r in routes)

    # ── LA BASCULE, NOMMÉE QUAND ELLE EXISTE ─────────────────────────────
    #
    # CE QU'ELLE APPORTE, ET QU'UN SIMPLE RÉSULTAT N'APPORTE PAS. Dire « votre
    # produit passe par un organisme notifié » ferme la discussion. Dire
    # « il y passe PARCE QUE les normes harmonisées ne sont pas intégralement
    # appliquées, et il n'y passerait pas sinon » ouvre un chantier chiffrable.
    bascule = None
    if classe == "important_i":
        bascule = {
            "fait": "application intégrale des normes harmonisées, "
                    "spécifications communes ou schémas de certification "
                    "pertinents",
            "etat": bool(harmonisees),
            "si_oui": ["A"], "si_non": ["B+C", "H"],
            "dit": ("Le contrôle interne reste ouvert tant que ces normes "
                    "sont INTÉGRALEMENT appliquées." if harmonisees else
                    "Ne pas les appliquer, ne les appliquer qu'en partie, ou "
                    "qu'elles n'existent pas encore : les trois cas mènent au "
                    "même endroit — l'organisme notifié."),
            "article": "art. 32, §2",
        }

    # ── LE RÔLE ──────────────────────────────────────────────────────────
    role = p.get("role") if p.get("role") in ROLES else "fabricant"

    # ── LES ÉCARTS ───────────────────────────────────────────────────────
    ecarts = _ecarts(p.get("ecarts") or {})

    return {
        "ok": True,
        "nom": nom,
        "perimetre": perimetre,
        "classe": dict(CLASSES[classe], cle=classe),
        "routes": [dict(PROCEDURES[r], cle=r) for r in routes],
        "organisme_notifie": organisme,
        "bascule": bascule,
        "role": dict(ROLES[role], cle=role),
        "ecarts": ecarts,
        "calendrier": calendrier(aujourdhui),
        "signalement": SIGNALEMENT if perimetre["dans"] else None,
        "source": SOURCE,
    }


def _ecarts(declares):
    """L'analyse d'écart sur les deux parties de l'annexe I.

    UNE EXIGENCE NON RENSEIGNÉE N'EST PAS UNE EXIGENCE CONFORME, et c'est la
    seule règle qui compte ici. Un tableau d'écarts qui compte les cases
    vides comme vertes rend un taux de conformité flatteur et faux — celui
    qu'on montre en comité, et qui se défait au premier audit.
    """
    parties = []
    for cle_p, titre, table, quoi in (
            ("I", "Propriétés du produit (annexe I, partie I)", ANNEXE_I_I,
             "se vérifie sur une version du produit"),
            ("II", "Gestion des vulnérabilités (annexe I, partie II)",
             ANNEXE_I_II, "se vérifie sur l'organisation du fabricant, et "
                          "vaut pendant toute la période d'assistance")):
        lignes = []
        for cle, nom, dit in table:
            e = declares.get(cle)
            lignes.append({"cle": cle, "nom": nom, "dit": dit,
                           "etat": e if e in _ETATS else "non_renseigne"})
        parties.append({
            "partie": cle_p, "titre": titre, "quoi": quoi, "lignes": lignes,
            "compte": {e: sum(1 for l in lignes if l["etat"] == e)
                       for e in _ETATS + ("non_renseigne",)},
        })
    total = sum(len(x["lignes"]) for x in parties)
    conformes = sum(x["compte"]["conforme"] for x in parties)
    retenus = total - sum(x["compte"]["sans_objet"] for x in parties)
    return {
        "parties": parties,
        "total": total,
        "conformes": conformes,
        "retenus": retenus,
        # LE TAUX EST RENDU, MAIS JAMAIS SEUL : `non_renseigne` l'accompagne
        # toujours, parce qu'un taux de 100 % sur trois exigences renseignées
        # ne dit rien de vingt et une.
        "taux": (round(100.0 * conformes / retenus) if retenus else None),
        "non_renseigne": sum(x["compte"]["non_renseigne"] for x in parties),
    }


def evaluer_parc(produits=None, aujourdhui=None):
    """Le portefeuille de produits — et ce qui COMMANDE l'effort.

    ═══ CE QUI COMMANDE N'EST PAS LA MOYENNE ════════════════════════════
    Un fabricant de quarante produits dont un seul relève de la classe II
    n'a pas « 2,5 % de son parc chez l'organisme notifié » : il a un
    calendrier et un budget d'organisme notifié, point. La classe la plus
    haute du parc décide de l'organisation à monter ; la moyenne ne décrit
    aucun produit réel et rassure à tort.
    """
    liste = produits or []
    if not isinstance(liste, list):
        return {"ok": False, "motif": "parc_illisible"}
    noms = [str((p or {}).get("nom") or "").strip() for p in liste]
    if len(set(n for n in noms if n)) != len([n for n in noms if n]):
        return {"ok": False, "motif": "noms_en_double"}

    cotes, hors = [], []
    for p in liste:
        r = evaluer_produit(p, aujourdhui)
        if not r.get("ok"):
            continue
        (cotes if r["perimetre"]["dans"] else hors).append(r)
    if not cotes:
        return {"ok": True, "cotes": 0, "hors_perimetre": hors,
                "commande": None, "dit": "Aucun produit déclaré dans le "
                                         "périmètre du règlement."}
    pire = max(cotes, key=lambda r: r["classe"]["rang"])
    notifies = [r for r in cotes if r["organisme_notifie"]]
    return {
        "ok": True,
        "cotes": len(cotes),
        "produits": cotes,
        "hors_perimetre": hors,
        "commande": {"nom": pire["nom"], "classe": pire["classe"]},
        "organisme_notifie": len(notifies),
        "noms_organisme_notifie": [r["nom"] for r in notifies],
        "calendrier": calendrier(aujourdhui),
        "dit": ("%d produit(s) sur %d passent par un organisme notifié. "
                "C'est ce chiffre, et non le taux de conformité, qui fixe le "
                "calendrier : la désignation de ces organismes n'a commencé "
                "qu'en juin 2026."
                % (len(notifies), len(cotes))),
        "source": SOURCE,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  LA GARDE — CE QUE CE MODULE REFUSE DE LAISSER PASSER
# ═══════════════════════════════════════════════════════════════════════════

def _verifier():
    fautes = []
    if [c for c in CLASSES.values() if "rang" not in c]:
        fautes.append("une classe sans rang")
    rangs = sorted(c["rang"] for c in CLASSES.values())
    if rangs != list(range(len(CLASSES))):
        fautes.append("les rangs de classe ne sont pas 0..n : %s" % rangs)
    for cle, c in CLASSES.items():
        if not str(c.get("article") or "").strip():
            fautes.append("la classe « %s » ne cite aucun article" % cle)
    for cle, p in PROCEDURES.items():
        if "organisme_notifie" not in p:
            fautes.append("la procédure « %s » ne dit pas si un organisme "
                          "notifié intervient" % cle)
    # CHAQUE CLASSE MÈNE QUELQUE PART, DANS LES DEUX SENS DE LA BASCULE.
    for cle in CLASSES:
        for h in (True, False):
            r = procedures_ouvertes(cle, h)
            if not r:
                fautes.append("la classe « %s » n'ouvre aucune procédure "
                              "(normes=%s)" % (cle, h))
            for x in r:
                if x not in PROCEDURES:
                    fautes.append("procédure inconnue : %s" % x)
    # LES EXIGENCES PORTENT DES CLÉS UNIQUES — sinon l'analyse d'écart
    # écraserait silencieusement une ligne par une autre.
    cles = [c for c, _n, _d in ANNEXE_I_I] + [c for c, _n, _d in ANNEXE_I_II]
    if len(set(cles)) != len(cles):
        fautes.append("deux exigences portent la même clé")
    # LES DEUX FAITS DÉCLENCHEURS ONT LEURS TROIS ÉTAPES, ET LES DÉLAIS
    # COURTS SONT LES MÊMES DES DEUX CÔTÉS (24 h puis 72 h).
    for cle, s in SIGNALEMENT.items():
        d = [e["delai_h"] for e in s["etapes"]]
        if d[:2] != [24, 72]:
            fautes.append("« %s » : les deux premiers délais ne sont pas "
                          "24 h puis 72 h (%s)" % (cle, d))
        if len(s["etapes"]) != 3:
            fautes.append("« %s » n'a pas trois étapes" % cle)
    if not SOURCE.get("licence"):
        fautes.append("la source ne dit pas sous quelle licence elle est reprise")
    # ── LES RÔLES ────────────────────────────────────────────────────────
    rangs = sorted(r["rang"] for r in ROLES.values())
    if rangs != list(range(len(ROLES))):
        fautes.append("les rangs de rôle ne sont pas 0..n : %s" % rangs)
    for cle, r in ROLES.items():
        if r.get("palier") not in SANCTIONS:
            fautes.append("le rôle « %s » ne dit pas à quel palier de sanction "
                          "il expose" % cle)
        if not r.get("porte"):
            fautes.append("le rôle « %s » ne porte aucune obligation" % cle)
    # ── LES PALIERS ──────────────────────────────────────────────────────
    r2 = sorted(p["rang"] for p in SANCTIONS.values())
    if r2 != list(range(len(SANCTIONS))):
        fautes.append("les rangs de palier ne sont pas 0..n : %s" % r2)
    for cle, p in SANCTIONS.items():
        if not (p.get("plafond_eur") and p.get("part_ca")):
            fautes.append("le palier « %s » n'a pas ses DEUX bornes — un "
                          "palier qui n'en aurait qu'une ferait disparaître "
                          "le « montant le plus élevé étant retenu »" % cle)
    # LE PALIER LE PLUS LOURD EST BIEN LE PLUS LOURD, sur les deux bornes.
    ordre = sorted(SANCTIONS, key=lambda c: SANCTIONS[c]["rang"])
    for a, b in zip(ordre, ordre[1:]):
        if not (SANCTIONS[a]["plafond_eur"] > SANCTIONS[b]["plafond_eur"]
                and SANCTIONS[a]["part_ca"] > SANCTIONS[b]["part_ca"]):
            fautes.append("le palier « %s » n'est pas plus lourd que « %s » "
                          "sur les deux bornes" % (a, b))
    # CHAQUE ARBRE DE QUALIFICATION MÈNE À UN RÔLE DE LA TABLE.
    for d in ({}, {"sous_ma_marque": True}, {"je_concois": True},
              {"fabricant_hors_union": True},
              {"modification_substantielle": True},
              {"modification_substantielle": True, "fabricant_hors_union": True}):
        q = qualifier_role(d)
        if q["role"]["cle"] not in ROLES:
            fautes.append("l'arbre de qualification rend un rôle inconnu : %s"
                          % q["role"]["cle"])
    if fautes:
        raise RuntimeError("cra — table incohérente : " + " ; ".join(fautes))
    return fautes


_FAUTES = _verifier()
