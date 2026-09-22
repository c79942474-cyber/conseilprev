# -*- coding: utf-8 -*-
"""
DORA — LE CADRE DE SUPERVISION DES PRESTATAIRES TIERS CRITIQUES.

═══ LA LACUNE QUE CE MODULE FERME ══════════════════════════════════════
`dora.py` disait, pour un prestataire tiers de services TIC : « un
prestataire peut être désigné critique au titre de l'article 31, et relève
alors d'un cadre de supervision européen », puis renvoyait à une liste
qu'il ne connaissait pas. C'était honnête et c'était peu. Les deux normes
techniques de 2025 — les règlements délégués (UE) 2025/295 et 2025/420 —
disent enfin ce qu'« être désigné critique » entraîne concrètement, et
c'est ce que ce module rend lisible.

═══ CE QUE LE MODULE REFUSE DE FAIRE, ET C'EST L'ESSENTIEL ═════════════
IL NE PRÉDIT PAS LA DÉSIGNATION. Les autorités européennes de surveillance
désignent, par l'intermédiaire du comité mixte et sur recommandation du
forum de supervision (article 31, paragraphe 1, point a)). Les quatre
critères du paragraphe 2 sont des critères d'APPRÉCIATION — effet
systémique, importance des entités dépendantes, dépendance sur fonctions
critiques, substituabilité — et aucun n'est chiffré par le texte. Rendre
un « vous serez désigné » sur des critères non chiffrés serait inventer un
seuil que le législateur n'a pas écrit.

CE QUI SE CALCULE, EN REVANCHE : les quatre EXCLUSIONS du paragraphe 8.
Elles ne s'apprécient pas, elles se constatent — et c'est la seule réponse
ferme que le texte permette. Un prestataire intragroupe, ou qui ne sert
que des entités actives dans un seul État membre, ne PEUT PAS être désigné,
quelle que soit sa part de marché.

═══ POURQUOI UNE ENTITÉ FINANCIÈRE LIT CET ÉCRAN ═══════════════════════
Parce que la supervision de son prestataire lui revient dessus. Le
prestataire notifie à ses clients sa désignation (article 31,
paragraphe 5) ; le superviseur principal publie les cas de refus de suivre
ses recommandations, en NOMMANT le prestataire (article 42,
paragraphe 2) ; et l'autorité compétente apprécie, chez l'entité
financière, l'incidence des mesures prises par le prestataire (règlement
délégué (UE) 2025/295, article 6). Le client est évalué sur ce que son
fournisseur a fait.
"""

VERSION = "2026-09-a"

RESERVE = (
    "Ce module décrit une procédure ; il ne prononce aucune désignation. "
    "Les autorités européennes de surveillance désignent, et elles seules. "
    "La liste des prestataires désignés est publiée et mise à jour chaque "
    "année par le comité mixte (article 31, paragraphe 9) ; elle n'est pas "
    "reproduite ici, parce qu'une liste recopiée vieillit sans prévenir."
)


# ═══════════════════════════════════════════════════════════════════════
# 1. LES SOURCES
# ═══════════════════════════════════════════════════════════════════════

# CHAQUE SOURCE DIT AUSSI SI ELLE A ÉTÉ LUE.
# `apporte` dit ce qu'on en a tiré ; `lue` dit si le texte lui-même était à
# disposition. Les deux ne se déduisent pas l'un de l'autre : on peut tirer
# beaucoup d'un texte qu'on cite sans l'avoir ouvert — et c'est précisément
# ce qui s'est passé pour SP 800-53 Rev. 4, dont le registre laissait croire
# le contraire. Voir la raison, en toutes lettres, en tête du registre de
# `nist_800_53`.
SOURCES = (
    {"cle": "dora", "lue": True, "titre": "Règlement (UE) 2022/2554 (DORA)",
     "celex": "32022R2554",
     "lien": "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri="
             "CELEX:32022R2554",
     "apporte": "Les articles 31 à 44 : la désignation, le superviseur "
                "principal, les pouvoirs, et le suivi par les autorités "
                "compétentes."},
    {"cle": "rd_295", "lue": True, "titre": "Règlement délégué (UE) 2025/295",
     "celex": "32025R0295",
     "lien": "https://eur-lex.europa.eu/eli/reg_del/2025/295/oj",
     "apporte": "Ce que le prestataire désigné doit fournir, sous quelle "
                "forme, et ce que l'autorité compétente apprécie ensuite "
                "chez l'entité financière cliente."},
    {"cle": "rd_420", "lue": True, "titre": "Règlement délégué (UE) 2025/420",
     "celex": "32025R0420",
     "lien": "https://eur-lex.europa.eu/eli/reg_del/2025/420/oj",
     "apporte": "L'équipe d'examen conjoint : qui supervise réellement, "
                "avec quelles tâches et sous quelle coordination."},
    # LES DEUX ACTES DE L'ARTICLE 31, §6, ET DE L'ARTICLE 43, §2. Ce sont
    # les textes ADOPTÉS par la Commission le 22 février 2024 ; ce corpus
    # porte leur version C(2024), et non leur numérotation au Journal
    # officiel. On cite donc ce qu'on tient, et la lacune le dit.
    {"cle": "criteres", "lue": True, "titre": "Acte délégué C(2024) 896 de la "
                                  "Commission du 22 février 2024",
     "celex": None,
     "lien": None,
     "apporte": "LES CRITÈRES DE DÉSIGNATION, CHIFFRÉS : deux étapes, "
                "quatre sous-critères de seuil, et la barre des 10 %."},
    {"cle": "redevances", "lue": True, "titre": "Acte délégué C(2024) 902 de la "
                                    "Commission du 22 février 2024",
     "celex": None,
     "lien": None,
     "apporte": "Le montant des redevances de supervision, leur assiette, "
                "leur plancher et leur échéance de paiement."},
)

LACUNES = (
    "Les deux actes délégués du 22 février 2024 figurent au corpus dans "
    "leur version adoptée par la Commission — C(2024) 896 et C(2024) 902. "
    "Leur numérotation définitive au Journal officiel n'y figure pas : les "
    "articles sont cités tels qu'adoptés, et c'est le texte publié qui "
    "fait foi.",
    "L'acte délégué C(2024) 896 ne dit pas expressément si les deux parts "
    "du sous-critère 4.1 et du sous-critère 4.2 doivent être atteintes "
    "dans LA MÊME catégorie d'entités financières, comme l'article 2, "
    "paragraphe 4, l'impose pour les sous-critères 1.1 et 1.2. Le module "
    "calcule les DEUX lectures et signale quand elles divergent, plutôt "
    "que d'en choisir une en silence.",
    "La liste des prestataires désignés critiques n'est pas reproduite. "
    "Elle est publiée par le comité mixte et mise à jour chaque année ; la "
    "recopier ici garantirait qu'elle soit fausse un jour sans que rien ne "
    "le signale.",
)


# ═══════════════════════════════════════════════════════════════════════
# 2. CE QUI S'APPRÉCIE — LES QUATRE CRITÈRES DE L'ARTICLE 31, §2
# ═══════════════════════════════════════════════════════════════════════
# ILS SONT ÉNONCÉS, PAS PONDÉRÉS. Leur donner un poids ici reviendrait à
# fabriquer un seuil que le texte ne porte pas, et le client bâtirait un
# raisonnement sur un chiffre inventé par un écran.

CRITERES = (
    {"cle": "effet_systemique", "lettre": "a",
     "quoi": "L'effet systémique sur la stabilité, la continuité ou la "
             "qualité de la fourniture de services financiers si le "
             "prestataire subissait une défaillance opérationnelle à grande "
             "échelle.",
     "apprecie_sur": "Le nombre d'entités financières servies et la valeur "
                     "totale de leurs actifs."},
    {"cle": "importance_clients", "lettre": "b",
     "quoi": "Le caractère ou l'importance systémique des entités "
             "financières qui dépendent du prestataire.",
     "apprecie_sur": "Le nombre d'établissements d'importance systémique "
                     "mondiale ou autres qui en dépendent, et leur "
                     "interdépendance avec d'autres entités financières."},
    {"cle": "fonctions_critiques", "lettre": "c",
     "quoi": "La dépendance des entités financières aux services du "
             "prestataire pour leurs fonctions critiques ou importantes.",
     "apprecie_sur": "La dépendance directe ET indirecte — la "
                     "sous-traitance est comptée, ce qui fait apparaître "
                     "des dépendances qu'aucun contrat ne montre."},
    {"cle": "substituabilite", "lettre": "d",
     "quoi": "Le degré de substituabilité du prestataire.",
     "apprecie_sur": "L'absence de solutions de substitution réelles — "
                     "nombre limité d'acteurs, part de marché, technologie "
                     "propriétaire — et la difficulté de migrer données et "
                     "charges de travail ailleurs, en coût, en délai et en "
                     "risque ajouté."},
)

# ─── LA MÉTHODE : DEUX ÉTAPES, ET LA PREMIÈRE EST UN FILTRE ──────────────
# L'ACTE DÉLÉGUÉ C(2024) 896 CHIFFRE CE QUE L'ARTICLE 31, §2, ÉNONCE.
# Étape 1 : des sous-critères de SEUIL, qui se calculent. Étape 2 : des
# sous-critères d'APPRÉCIATION, qui ne se calculent pas — et le module
# refuse de les simuler, parce qu'un « vous serez désigné » fondé sur une
# appréciation inventée est pire qu'un silence.
#
# LE CRITÈRE c) N'A PAS D'ÉTAPE 1. L'article premier, paragraphe 1, second
# alinéa, le dit : pour le critère c), la première étape est couverte par
# l'évaluation des critères a), b) et d). Lui en fabriquer une ferait un
# filtre de plus, et écarterait des prestataires que le texte n'écarte pas.

METHODE = {
    "source": "Acte délégué C(2024) 896, article premier",
    "etape_1": "Les AES évaluent si le prestataire remplit TOUS les "
               "sous-critères « étape 1 ». Ils se calculent.",
    "etape_2": "Les prestataires qui franchissent l'étape 1 sont soumis "
               "aux sous-critères « étape 2 ». Ils s'apprécient.",
    "designation": "Est désigné le prestataire qui remplit tous les "
                   "sous-critères « étape 1 » ET dont l'évaluation « étape "
                   "2 » est positive — par les AES, via le comité mixte, "
                   "sur recommandation du forum de supervision, après "
                   "expiration du délai de déclaration motivée.",
    "critere_c_sans_etape_1": "Pour le critère c), la première étape est "
                              "couverte par l'évaluation des critères a), "
                              "b) et d).",
}

#: LE SEUIL, ÉCRIT UNE SEULE FOIS. Dix pour cent, et il vaut pour les
#: quatre sous-critères de part de l'acte délégué — 1.1, 1.2, 4.1 et 4.2.
SEUIL_PART = 10.0

SOUS_CRITERES = (
    {"cle": "1.1", "critere": "effet_systemique", "etape": 1,
     "article": "Acte délégué C(2024) 896, article 2, §§1 a) et 2",
     "quoi": "Part, sur le nombre d'entités financières d'une catégorie de "
             "l'article 2, paragraphe 1, de celles à qui le prestataire "
             "fournit des services TIC soutenant des fonctions critiques "
             "ou importantes.",
     "seuil": SEUIL_PART},
    {"cle": "1.2", "critere": "effet_systemique", "etape": 1,
     "article": "Acte délégué C(2024) 896, article 2, §§1 b) et 3",
     "quoi": "Part, sur la valeur totale des actifs des entités "
             "financières de cette même catégorie dans l'Union, de la "
             "valeur des actifs de celles servies pour des fonctions "
             "critiques ou importantes.",
     "seuil": SEUIL_PART},
    {"cle": "1.3", "critere": "effet_systemique", "etape": 2,
     "article": "Acte délégué C(2024) 896, article 2, §5 a)",
     "quoi": "L'intensité de l'incidence d'une interruption des services "
             "du prestataire sur les activités des entités financières "
             "retenues à l'étape 1, et le nombre d'entités concernées.",
     "seuil": None},
    {"cle": "1.4", "critere": "effet_systemique", "etape": 2,
     "article": "Acte délégué C(2024) 896, article 2, §5 b)",
     "quoi": "La dépendance du prestataire à l'égard des MÊMES "
             "sous-traitants pour des services soutenant des fonctions "
             "critiques ou importantes.",
     "seuil": None,
     "applique_plus_tard": "Le superviseur principal applique ce "
                           "sous-critère à compter de vingt-quatre mois "
                           "après l'entrée en vigueur de DORA (article 7 "
                           "de l'acte délégué)."},
    {"cle": "2.1", "critere": "importance_clients", "etape": 1,
     "article": "Acte délégué C(2024) 896, article 3, §§1 a) et 2",
     "quoi": "Établissements de crédit d'importance systémique servis "
             "pour des fonctions critiques ou importantes. Rempli si au "
             "moins un EISm, OU au moins trois autres EIS, OU au moins un "
             "autre EIS dont le score d'importance systémique calculé "
             "selon l'article 131, paragraphe 3, de la directive "
             "2013/36/UE dépasse 3 000.",
     "seuil": None},
    {"cle": "2.2", "critere": "importance_clients", "etape": 1,
     "article": "Acte délégué C(2024) 896, article 3, §§1 b) et 3",
     "quoi": "Autres entités financières identifiées comme systémiques "
             "par les autorités compétentes. Rempli si au moins une "
             "entité des points g), h), i) ou j) de l'article 2, "
             "paragraphe 1, OU au moins trois autres entités systémiques.",
     "seuil": None},
    {"cle": "2.3", "critere": "importance_clients", "etape": 2,
     "article": "Acte délégué C(2024) 896, article 3, §4",
     "quoi": "L'interdépendance entre les EISm ou autres EIS et les autres "
             "entités financières retenues à l'étape 1, notamment lorsque "
             "ces établissements fournissent des services d'infrastructure "
             "financière à d'autres entités financières.",
     "seuil": None},
    {"cle": "3.1", "critere": "fonctions_critiques", "etape": 2,
     "article": "Acte délégué C(2024) 896, article 4, §1",
     "quoi": "Le service TIC fourni en définitive à l'appui de fonctions "
             "critiques ou importantes est de nature critique pour les "
             "activités de ces entités.",
     "seuil": None},
    {"cle": "4.1", "critere": "substituabilite", "etape": 1,
     "article": "Acte délégué C(2024) 896, article 5, §§1 a), 2 et 4 a)",
     "quoi": "Part, sur le nombre total d'entités financières d'une "
             "catégorie, de celles pour lesquelles il n'existe AUCUN autre "
             "prestataire capable de fournir le même service à l'appui de "
             "leurs fonctions critiques ou importantes.",
     "seuil": SEUIL_PART},
    {"cle": "4.2", "critere": "substituabilite", "etape": 1,
     "article": "Acte délégué C(2024) 896, article 5, §§1 b), 3 et 4 b)",
     "quoi": "Part, sur le nombre total d'entités financières d'une "
             "catégorie, de celles pour lesquelles il est extrêmement "
             "difficile de se tourner vers un autre prestataire.",
     "seuil": SEUIL_PART},
    {"cle": "4.3", "critere": "substituabilite", "etape": 2,
     "article": "Acte délégué C(2024) 896, article 5, §5, renvoyant à "
                "l'article 31, paragraphe 2, point d) i), de DORA",
     "quoi": "L'absence de solutions de substitution réelles, même "
             "partielles — nombre limité d'acteurs, part de marché, "
             "complexité technique, technologie propriétaire, "
             "caractéristiques propres de l'organisation.",
     "seuil": None},
)

SOUS_CRITERES_PAR_CLE = {s["cle"]: s for s in SOUS_CRITERES}

#: ARTICLE 6 DE L'ACTE DÉLÉGUÉ — ET C'EST LA BOUCLE QUI SE FERME. Les AES
#: évaluent les sous-critères À PARTIR DES REGISTRES D'INFORMATIONS que
#: les entités financières tiennent au titre de l'article 28, §3. Le
#: registre qu'une banque remplit sert à désigner son fournisseur.
SOURCES_DONNEES = {
    "article": "Acte délégué C(2024) 896, article 6",
    "quoi": "Les AES évaluent les sous-critères à partir des données des "
            "registres d'informations de l'article 28, paragraphe 3, de "
            "DORA, et peuvent y ajouter toute autre source dont elles "
            "disposent.",
    "millesime": "Les données les plus récentes de l'année d'évaluation, "
                 "ou celles disponibles au plus tard le 31 décembre de "
                 "l'année précédente.",
    "ce_que_cela_change": "Le registre d'informations n'est pas une "
                          "formalité déclarative : c'est la matière "
                          "première de la désignation. Un registre "
                          "incomplet fausse l'appréciation portée sur vos "
                          "fournisseurs.",
}


#: ARTICLE 31, §3 — LE GROUPE EST L'UNITÉ D'APPRÉCIATION.
PERIMETRE_GROUPE = {
    "article": "Article 31, paragraphe 3",
    "quoi": "Lorsque le prestataire appartient à un groupe, les quatre "
            "critères s'apprécient sur les services TIC fournis par "
            "L'ENSEMBLE DU GROUPE.",
    "consequence": "Découper une activité en filiales ne fait pas baisser "
                   "l'appréciation : elle est consolidée.",
}

#: ARTICLE 31, §4 — ET LE GROUPE DÉSIGNE UN POINT DE CONTACT.
POINT_COORDINATION = {
    "article": "Article 31, paragraphe 4",
    "quoi": "Un prestataire critique qui fait partie d'un groupe désigne "
            "une personne morale comme point de coordination, pour la "
            "représentation et la communication avec le superviseur "
            "principal.",
}


# ═══════════════════════════════════════════════════════════════════════
# 3. CE QUI SE CONSTATE — LES QUATRE EXCLUSIONS DE L'ARTICLE 31, §8
# ═══════════════════════════════════════════════════════════════════════
# LA SEULE RÉPONSE FERME QUE LE TEXTE PERMET. Une exclusion ne s'apprécie
# pas : elle tient ou elle ne tient pas. C'est donc la seule chose que ce
# module calcule.

EXCLUSIONS = (
    {"cle": "entite_financiere", "point": "i",
     "quoi": "Entité financière qui fournit des services TIC à d'autres "
             "entités financières.",
     "pourquoi": "Elle est déjà dans le champ du règlement à son propre "
                 "titre, et supervisée comme entité financière."},
    {"cle": "cadre_sebc", "point": "ii",
     "quoi": "Prestataire soumis à des cadres de supervision établis pour "
             "soutenir les missions de l'article 127, paragraphe 2, du "
             "traité sur le fonctionnement de l'Union européenne.",
     "pourquoi": "Les missions du Système européen de banques centrales "
                 "ont leur propre cadre de surveillance."},
    {"cle": "intragroupe", "point": "iii",
     "quoi": "Prestataire tiers de services TIC intragroupe.",
     "pourquoi": "Le risque reste à l'intérieur du groupe, où il est déjà "
                 "saisi par les obligations de l'entité financière "
                 "elle-même."},
    {"cle": "un_seul_etat", "point": "iv",
     "quoi": "Prestataire qui fournit des services TIC dans un seul État "
             "membre, à des entités financières qui ne sont actives que "
             "dans cet État membre.",
     "pourquoi": "Sans dimension transfrontalière, la supervision relève "
                 "de l'autorité nationale, pas du cadre de l'Union."},
)

EXCLUSIONS_PAR_CLE = {x["cle"]: x for x in EXCLUSIONS}


# ═══════════════════════════════════════════════════════════════════════
# 4. LA PROCÉDURE, ET SES DÉLAIS — ARTICLE 31, §5
# ═══════════════════════════════════════════════════════════════════════
# CHAQUE ÉTAPE PORTE SON DÉLAI, PARCE QUE C'EST LE DÉLAI QUI SE RATE. Six
# semaines pour contester une évaluation, ce n'est pas long quand il faut
# réunir une part de marché consolidée sur un groupe.

PROCEDURE = (
    {"rang": 1, "cle": "notification_evaluation",
     "quoi": "Le superviseur principal notifie au prestataire le résultat "
             "de l'évaluation menée en vue de la désignation.",
     "delai": None, "article": "Article 31, paragraphe 5"},
    {"rang": 2, "cle": "declaration_motivee",
     "quoi": "Le prestataire peut adresser une déclaration motivée "
             "contenant toute information pertinente pour l'évaluation.",
     "delai": "Six semaines à compter de la notification",
     "article": "Article 31, paragraphe 5"},
    {"rang": 3, "cle": "complement",
     "quoi": "Le superviseur principal tient compte de la déclaration et "
             "peut demander des informations complémentaires.",
     "delai": "Trente jours civils à compter de la réception de la "
              "déclaration",
     "article": "Article 31, paragraphe 5"},
    {"rang": 4, "cle": "designation",
     "quoi": "Les AES, par l'intermédiaire du comité mixte, notifient la "
             "désignation et la date à partir de laquelle le prestataire "
             "fera effectivement l'objet d'activités de supervision.",
     "delai": "Cette date est fixée au plus tard un mois après la "
              "notification",
     "article": "Article 31, paragraphe 5"},
    {"rang": 5, "cle": "information_clients",
     "quoi": "Le prestataire notifie sa désignation aux entités "
             "financières auxquelles il fournit des services.",
     "delai": None, "article": "Article 31, paragraphe 5"},
)

#: ARTICLE 31, §11 — ON PEUT DEMANDER À ÊTRE DÉSIGNÉ. Contre-intuitif, et
#: pourtant rationnel : la désignation vaut label de supervision
#: européenne, et un prestataire qui la brigue s'épargne d'avoir à
#: convaincre chaque client, un par un, de sa solidité.
VOLONTAIRE = {
    "article": "Article 31, paragraphe 11 ; règlement délégué (UE) "
               "2025/295, article premier",
    "quoi": "Un prestataire qui ne figure pas sur la liste publiée peut "
            "demander à être désigné critique.",
    "perimetre_groupe": "Lorsque le prestataire appartient à un groupe, "
                        "les informations s'apprécient sur les services "
                        "TIC fournis par l'ensemble du groupe (article "
                        "premier, paragraphe 2).",
    "informations": (
        ("a", "Nom de la personne morale"),
        ("b", "Code d'identification de l'entité juridique"),
        ("c", "Nom et coordonnées de la personne de contact"),
        ("d", "Pays du siège statutaire"),
        ("e", "Structure d'entreprise — société mère et entreprises liées "
              "fournissant des services TIC à des entités financières de "
              "l'Union"),
        ("f", "Estimation de la part de marché dans le secteur financier "
              "de l'Union, et par type d'entité financière, pour l'année "
              "de la demande et l'année précédente"),
        ("g", "Description de chaque service TIC fourni, des fonctions "
              "qu'il soutient, et s'il soutient des fonctions critiques "
              "ou importantes"),
        ("h", "Liste des entités financières clientes, avec pour chacune "
              "son type et la localisation géographique depuis laquelle "
              "elle est servie"),
        ("i", "Liste des prestataires DÉJÀ désignés critiques qui "
              "s'appuient sur les services du demandeur"),
        ("j", "Autoévaluation de la substituabilité de chaque service, et "
              "connaissance des autres prestataires capables de le rendre"),
        ("k", "Stratégie commerciale future — changements de groupe ou de "
              "gestion, nouveaux marchés, nouvelles activités"),
        ("l", "Identification des sous-traitants qui sont eux-mêmes "
              "désignés prestataires tiers critiques"),
        ("m", "Tout autre motif pertinent"),
    ),
}


# ═══════════════════════════════════════════════════════════════════════
# 5. CE QUE LE PRESTATAIRE DÉSIGNÉ DOIT — RD (UE) 2025/295
# ═══════════════════════════════════════════════════════════════════════

OBLIGATIONS = (
    {"cle": "informations", "article": "RD (UE) 2025/295, article 2",
     "quoi": "Fournir au superviseur principal, à sa demande, toute "
             "information nécessaire à ses missions — y compris les "
             "accords et les COPIES DES DOCUMENTS CONTRACTUELS conclus "
             "avec les entités financières.",
     "ce_qui_surprend": "Les contrats eux-mêmes sont communicables. Une "
                        "clause de confidentialité négociée avec un client "
                        "ne fait pas obstacle à la supervision."},
    {"cle": "plan_correctif", "article": "RD (UE) 2025/295, article 3",
     "quoi": "Après les recommandations de l'article 35, paragraphe 1, "
             "point d), remettre un rapport contenant un PLAN DE MESURES "
             "CORRECTIVES, conforme au calendrier fixé par le superviseur "
             "principal pour chaque recommandation, puis rendre compte de "
             "sa mise en œuvre.",
     "ce_qui_surprend": "Le calendrier n'est pas négocié : il est fixé "
                        "recommandation par recommandation."},
    {"cle": "canal", "article": "RD (UE) 2025/295, article 4",
     "quoi": "Transmettre par les canaux électroniques sécurisés dédiés "
             "indiqués par le superviseur principal, dans la forme et "
             "selon la structure qu'il définit, en localisant clairement "
             "chaque élément demandé.",
     "ce_qui_surprend": "La forme est imposée. Un envoi complet mais mal "
                        "structuré est un envoi à refaire."},
    {"cle": "sous_traitance", "article": "RD (UE) 2025/295, article 5 et "
                                          "annexe",
     "quoi": "Fournir les informations sur les accords de sous-traitance "
             "selon le MODÈLE figurant en annexe du règlement délégué.",
     "ce_qui_surprend": "Le modèle est normatif : la chaîne de "
                        "sous-traitance se déclare dans un format unique, "
                        "comparable d'un prestataire à l'autre."},
)


# ═══════════════════════════════════════════════════════════════════════
# 6. CE QUI REVIENT SUR L'ENTITÉ FINANCIÈRE CLIENTE
# ═══════════════════════════════════════════════════════════════════════
# LA PARTIE QUE PERSONNE NE LIT, ET QUI DÉCIDE DES CONTRATS. Un client
# n'est pas spectateur de la supervision de son fournisseur : il en porte
# les conséquences, et son autorité compétente l'interroge dessus.

RETOMBEES_CLIENT = (
    {"cle": "notification_designation",
     "article": "DORA, article 31, paragraphe 5, dernier alinéa",
     "quoi": "Le prestataire vous notifie sa désignation comme critique.",
     "quoi_faire": "Inscrire la date au registre d'informations de "
                   "l'article 28, paragraphe 3 : elle change le régime de "
                   "surveillance de ce contrat."},
    {"cle": "intention_suivre",
     "article": "DORA, article 42, paragraphe 1",
     "quoi": "Dans les soixante jours civils suivant les recommandations "
             "du superviseur principal, le prestataire notifie son "
             "intention de les suivre, ou explique de façon circonstanciée "
             "pourquoi il ne les suivra pas. Le superviseur principal "
             "transmet immédiatement l'information aux autorités "
             "compétentes des entités financières concernées.",
     "quoi_faire": "Demander cette réponse au prestataire : votre autorité "
                   "l'aura, et vous interrogera dessus."},
    {"cle": "divulgation_publique",
     "article": "DORA, article 42, paragraphe 2",
     "quoi": "Le superviseur principal rend PUBLIC le cas où un "
             "prestataire ne répond pas, ou répond insuffisamment — en "
             "révélant son identité, le type et la nature du manquement.",
     "quoi_faire": "Prévoir, dans la stratégie de sortie de l'article 30, "
                   "paragraphe 3, point f), ce que déclenche une telle "
                   "publication."},
    {"cle": "appreciation_autorite",
     "article": "RD (UE) 2025/295, article 6",
     "quoi": "Votre autorité compétente apprécie, chez vous, l'incidence "
             "des mesures prises par le prestataire sur la base des "
             "recommandations — notamment l'adéquation et la cohérence des "
             "mesures correctives que VOUS avez mises en œuvre pour "
             "atténuer les risques recensés.",
     "quoi_faire": "Documenter votre propre réaction aux recommandations "
                   "faites à votre prestataire. C'est de cela qu'on vous "
                   "demandera compte, et non du comportement du "
                   "prestataire."},
)


# ═══════════════════════════════════════════════════════════════════════
# 7. QUI SUPERVISE RÉELLEMENT — RD (UE) 2025/420
# ═══════════════════════════════════════════════════════════════════════

EQUIPE_EXAMEN = {
    "source": "Règlement délégué (UE) 2025/420",
    "quoi": "L'équipe d'examen conjoint exerce les activités de "
            "supervision, sous la coordination du coordonnateur du "
            "superviseur principal.",
    "mise_en_place": {
        "article": "Article 2",
        "quoi": "Mise en place après la PREMIÈRE désignation d'un "
                "prestataire comme critique, par le superviseur principal "
                "en accord avec le réseau de supervision commun de "
                "l'article 34, paragraphe 1, de DORA. Elle peut être mise "
                "à jour en cas de changement significatif de la situation "
                "du prestataire.",
    },
    "composition": {
        "article": "Article 3",
        "quoi": "Le superviseur principal détermine le nombre de membres "
                "et la composition, en accord avec le réseau de "
                "supervision commun et en concertation avec le forum de "
                "supervision de l'article 32, paragraphe 1.",
    },
    "revision": {
        "article": "Article 4",
        "quoi": "Périodiquement, en cas de changement de superviseur "
                "principal ou de changement significatif, les résultats "
                "des membres sont évalués et la composition peut être "
                "modifiée.",
    },
    "taches": (
        ("a", "Assister le superviseur principal dans la préparation du "
              "plan de supervision individuel annuel (DORA, article 33, "
              "paragraphe 4)"),
        ("b", "Assister le superviseur principal dans l'évaluation prévue "
              "à l'article 33, paragraphe 2, de DORA"),
    ),
    "modalites": {
        "article": "Article 5",
        "quoi": "Les membres exécutent leurs tâches avec compétence, soin "
                "et diligence, SANS AUCUN BIAIS, selon les instructions du "
                "coordonnateur du superviseur principal (DORA, article 40, "
                "paragraphe 2) et les procédures élaborées conjointement "
                "par les autorités européennes de surveillance.",
    },
}

#: ARTICLE 31, §9 — LA LISTE EST PUBLIQUE, ET ELLE EST ANNUELLE.
LISTE = {
    "article": "Article 31, paragraphe 9",
    "quoi": "Les AES, par l'intermédiaire du comité mixte, établissent, "
            "publient et mettent à jour CHAQUE ANNÉE la liste des "
            "prestataires tiers critiques de services TIC au niveau de "
            "l'Union.",
    "pourquoi_pas_ici": "Une liste recopiée dans un écran vieillit sans "
                        "prévenir. Celle-ci se consulte à sa source.",
}


# ═══════════════════════════════════════════════════════════════════════
# 8. LE CALCUL — CE QUI SE CONSTATE, ET RIEN D'AUTRE
# ═══════════════════════════════════════════════════════════════════════

ISSUES = {
    "exclu": {
        "nom": "Ne peut pas être désigné critique",
        "quoi": "Au moins une des quatre exclusions de l'article 31, "
                "paragraphe 8, s'applique. La désignation est fermée, "
                "quelle que soit la part de marché.",
    },
    "etape_1_non_franchie": {
        "nom": "L'étape 1 n'est pas franchie",
        "quoi": "Au moins un sous-critère de seuil n'est pas atteint. "
                "L'acte délégué C(2024) 896 exige qu'ils le soient TOUS "
                "pour passer à l'étape 2 : la désignation ne peut pas "
                "aboutir en l'état.",
    },
    "etape_1_franchie": {
        "nom": "L'étape 1 est franchie — l'étape 2 s'apprécie",
        "quoi": "Tous les sous-critères de seuil sont atteints. Les AES "
                "procèdent alors à l'évaluation « étape 2 », qui ne se "
                "calcule pas : ce module l'énonce et ne la simule pas.",
    },
    "lecture_incertaine": {
        "nom": "L'étape 1 dépend d'une lecture que le texte ne tranche pas",
        "quoi": "Les deux parts de substituabilité atteignent le seuil, "
                "mais dans des catégories différentes. Selon que la même "
                "catégorie est exigée ou non, l'étape 1 est franchie ou "
                "non — et l'acte délégué ne le dit pas expressément.",
    },
    "a_completer": {
        "nom": "Déclaration incomplète",
        "quoi": "Les quatre exclusions n'ont pas toutes reçu de réponse. "
                "Une exclusion non déclarée n'est pas une exclusion "
                "écartée.",
    },
}


def eligibilite(declaration=None):
    """Le prestataire PEUT-IL être désigné critique — et rien de plus.

    LES QUATRE EXCLUSIONS SE DÉCLARENT TOUTES, OU LA RÉPONSE N'EN EST PAS
    UNE. Traiter une exclusion muette comme « non applicable » rendrait
    « éligible » à un prestataire intragroupe qui n'aurait simplement pas
    répondu — et c'est le sens inverse de la vérité.
    """
    d = declaration if isinstance(declaration, dict) else {}

    declarees = [x for x in EXCLUSIONS if d.get(x["cle"]) is True]
    muettes = [x["cle"] for x in EXCLUSIONS if d.get(x["cle"]) is None]

    # ── L'EXCLUSION PREMIÈRE, ET ELLE FERME TOUT. Calculer des seuils
    #    pour un prestataire intragroupe serait un travail exact sur une
    #    question qui ne se pose pas.
    etape = etape_1(d)
    if declarees:
        issue = "exclu"
    elif muettes:
        issue = "a_completer"
    elif etape["verdict"] == "a_completer":
        issue = "a_completer"
    elif etape["verdict"] == "non_franchie":
        issue = "etape_1_non_franchie"
    elif etape["verdict"] == "lecture_incertaine":
        issue = "lecture_incertaine"
    else:
        issue = "etape_1_franchie"

    return {
        "ok": True,
        "issue": issue,
        "methode": dict(METHODE),
        "etape_1": etape,
        "etape_2": [dict(s) for s in SOUS_CRITERES if s["etape"] == 2],
        "sources_donnees": dict(SOURCES_DONNEES),
        "redevances": {
            "plancher_eur": REDEVANCE_PLANCHER_EUR,
            "plancher_dit": REDEVANCES["calcul"]["plancher_dit"],
        },
        "nom": ISSUES[issue]["nom"],
        "quoi": ISSUES[issue]["quoi"],
        "exclusions_retenues": [dict(x) for x in declarees],
        "exclusions_non_declarees": muettes,
        "criteres": [dict(c) for c in CRITERES],
        "perimetre_groupe": dict(PERIMETRE_GROUPE),
        # CE QUE LE MODULE NE CALCULE PAS, DIT AVEC LE RESTE. L'étape 1
        # se chiffre depuis que l'acte délégué C(2024) 896 est au corpus ;
        # l'étape 2 ne se chiffre pas, et ne se chiffrera pas.
        "l_etape_2_ne_se_calcule_pas":
            "Les sous-critères « étape 2 » — intensité de l'incidence "
            "d'une interruption, dépendance aux mêmes sous-traitants, "
            "interdépendance des établissements systémiques, criticité "
            "réelle du service, absence de substitut — sont des "
            "appréciations. Aucun seuil ne les décide, et franchir "
            "l'étape 1 ne vaut pas désignation.",
        "procedure": [dict(p) for p in PROCEDURE],
        "volontaire": {"article": VOLONTAIRE["article"],
                       "quoi": VOLONTAIRE["quoi"],
                       "perimetre_groupe": VOLONTAIRE["perimetre_groupe"],
                       "informations": [{"lettre": a, "quoi": b}
                                        for a, b in
                                        VOLONTAIRE["informations"]]},
        "liste": dict(LISTE),
        "reserve": RESERVE,
    }


# ═══════════════════════════════════════════════════════════════════════
# 8 bis. L'ÉTAPE 1 SE CALCULE — ET SEULEMENT ELLE
# ═══════════════════════════════════════════════════════════════════════

def _part(v):
    """Une part en pourcentage, ou None si elle n'est pas déclarée."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _seuil_par_categorie(categories, champ_a, champ_b):
    """Les deux parts atteignent-elles 10 %, et dans quelle catégorie ?

    DEUX LECTURES, ET LE MODULE LES REND TOUTES LES DEUX. L'article 2,
    paragraphe 4, exige les deux parts dans LA MÊME catégorie ; l'article 5,
    paragraphe 4, ne le dit pas expressément. Trancher en silence ferait
    dire au module une chose que le texte ne dit pas — et dans un sens qui
    change le verdict. Il rend donc les deux, et signale la divergence.
    """
    memes, separees_a, separees_b, lues = [], False, False, 0
    for c in categories or ():
        if not isinstance(c, dict):
            continue
        a, b = _part(c.get(champ_a)), _part(c.get(champ_b))
        if a is None or b is None:
            continue
        lues += 1
        if a >= SEUIL_PART:
            separees_a = True
        if b >= SEUIL_PART:
            separees_b = True
        if a >= SEUIL_PART and b >= SEUIL_PART:
            memes.append({"categorie": c.get("categorie"), "part_a": a,
                          "part_b": b})
    return {
        "categories_lues": lues,
        "meme_categorie": bool(memes),
        "categories_franchies": memes,
        "categories_separees": bool(separees_a and separees_b),
        "diverge": bool(separees_a and separees_b) and not memes,
    }


def etape_1(declaration=None):
    """Les six sous-critères de seuil, et ce qu'ils donnent.

    UN SOUS-CRITÈRE NON DÉCLARÉ N'EST PAS UN SOUS-CRITÈRE NON REMPLI. Le
    traiter comme tel rendrait « ne sera pas désigné » à un prestataire qui
    n'a simplement pas répondu — la plus rassurante des erreurs, et la pire.
    """
    d = declaration if isinstance(declaration, dict) else {}

    effet = _seuil_par_categorie(d.get("categories_servies"),
                                 "part_nombre", "part_actifs")
    subst = _seuil_par_categorie(d.get("categories_substituabilite"),
                                 "part_sans_alternative",
                                 "part_bascule_difficile")

    def _n(cle):
        v = d.get(cle)
        return v if isinstance(v, int) and v >= 0 else None

    gsii, osii = _n("eism"), _n("autres_eis")
    osii_haut = _n("autres_eis_score_sup_3000")
    sys_ghij, sys_autres = _n("systemiques_ghij"), _n("systemiques_autres")

    lignes = []

    def _ligne(cle, etat, dit):
        s = SOUS_CRITERES_PAR_CLE[cle]
        lignes.append({"cle": cle, "critere": s["critere"],
                       "article": s["article"], "quoi": s["quoi"],
                       "seuil": s["seuil"], "etat": etat, "dit": dit})

    # ── CRITÈRE a) — LES DEUX PARTS, DANS LA MÊME CATÉGORIE ────────────
    if not effet["categories_lues"]:
        etat_a, dit_a = "non_declare", "Aucune catégorie d'entités "             "financières servies n'est renseignée."
    elif effet["meme_categorie"]:
        etat_a, dit_a = "rempli", (
            "Les deux parts atteignent %.0f %% dans %d catégorie(s)."
            % (SEUIL_PART, len(effet["categories_franchies"])))
    else:
        etat_a, dit_a = "non_rempli", (
            "Aucune catégorie où les deux parts atteignent %.0f %%."
            % SEUIL_PART)
    _ligne("1.1", etat_a, dit_a)
    _ligne("1.2", etat_a, dit_a)

    # ── CRITÈRE b) — DEUX SOUS-CRITÈRES, CHACUN À TROIS PORTES ─────────
    if gsii is None or osii is None or osii_haut is None:
        etat_21, dit_21 = "non_declare", "Le nombre d'EISm et d'autres "             "EIS servis n'est pas renseigné."
    elif gsii >= 1 or osii >= 3 or osii_haut >= 1:
        etat_21, dit_21 = "rempli", (
            "%d EISm, %d autres EIS, dont %d au score supérieur à 3 000."
            % (gsii, osii, osii_haut))
    else:
        etat_21, dit_21 = "non_rempli", (
            "Ni un EISm, ni trois autres EIS, ni un autre EIS au score "
            "supérieur à 3 000.")
    _ligne("2.1", etat_21, dit_21)

    if sys_ghij is None or sys_autres is None:
        etat_22, dit_22 = "non_declare", "Le nombre d'entités identifiées "             "systémiques n'est pas renseigné."
    elif sys_ghij >= 1 or sys_autres >= 3:
        etat_22, dit_22 = "rempli", (
            "%d entité(s) des points g) à j) et %d autre(s) entité(s) "
            "identifiées systémiques." % (sys_ghij, sys_autres))
    else:
        etat_22, dit_22 = "non_rempli", (
            "Ni une entité des points g) à j), ni trois autres entités "
            "identifiées systémiques.")
    _ligne("2.2", etat_22, dit_22)

    # ── CRITÈRE d) — LES DEUX PARTS DE SUBSTITUABILITÉ ─────────────────
    if not subst["categories_lues"]:
        etat_d, dit_d = "non_declare", "Aucune catégorie n'est renseignée "             "pour la substituabilité."
    elif subst["meme_categorie"]:
        etat_d, dit_d = "rempli", (
            "Les deux parts atteignent %.0f %% dans %d catégorie(s)."
            % (SEUIL_PART, len(subst["categories_franchies"])))
    elif subst["diverge"]:
        etat_d, dit_d = "lecture_incertaine", (
            "Les deux parts atteignent %.0f %%, mais dans des catégories "
            "DIFFÉRENTES. L'acte délégué ne dit pas expressément si la "
            "même catégorie est exigée ici, comme elle l'est à "
            "l'article 2, paragraphe 4." % SEUIL_PART)
    else:
        etat_d, dit_d = "non_rempli", (
            "Aucune catégorie où les deux parts atteignent %.0f %%."
            % SEUIL_PART)
    _ligne("4.1", etat_d, dit_d)
    _ligne("4.2", etat_d, dit_d)

    etats = {l["etat"] for l in lignes}
    if "non_declare" in etats:
        verdict = "a_completer"
    elif "non_rempli" in etats:
        verdict = "non_franchie"
    elif "lecture_incertaine" in etats:
        verdict = "lecture_incertaine"
    else:
        verdict = "franchie"

    return {"verdict": verdict, "lignes": lignes,
            "effet_systemique": effet, "substituabilite": subst}


# ═══════════════════════════════════════════════════════════════════════
# 8 ter. CE QUE COÛTE LA SUPERVISION — ACTE DÉLÉGUÉ C(2024) 902
# ═══════════════════════════════════════════════════════════════════════
# LE CHIFFRE QUE PERSONNE N'ANNONCE, ET QUI DÉCIDE PARFOIS D'UNE
# STRATÉGIE. Un prestataire qui envisage la désignation volontaire de
# l'article 31, §11, doit savoir qu'elle se paie, et combien au minimum.

REDEVANCE_PLANCHER_EUR = 50000.0

REDEVANCES = {
    "source": "Acte délégué C(2024) 902 de la Commission du 22 février "
              "2024",
    "assiette": {
        "article": "Article 2",
        "quoi": "Le chiffre d'affaires retenu est celui réalisé DANS "
                "L'UNION en fournissant aux entités financières de "
                "l'article 2, paragraphe 1, de DORA les services TIC "
                "énumérés par les normes techniques d'exécution de "
                "l'article 28, paragraphe 9.",
        "declaration": "Des chiffres annuels AUDITÉS pour l'année n−2, "
                       "remis au superviseur principal au plus tard le "
                       "31 décembre de l'année n−1.",
        "defaut": "À défaut de chiffres audités correctement délimités, le "
                  "superviseur principal retient le chiffre d'affaires "
                  "généré dans l'Union.",
    },
    "calcul": {
        "article": "Article 3",
        "quoi": "Redevance annuelle = coûts annuels totaux estimés des "
                "superviseurs, multipliés par un coefficient de chiffre "
                "d'affaires : le chiffre d'affaires applicable du "
                "prestataire pour n−2, rapporté à celui de TOUS les "
                "prestataires critiques pour n−2.",
        "plancher_eur": REDEVANCE_PLANCHER_EUR,
        "plancher_dit": "Aucun prestataire critique ne paie moins de "
                        "50 000 EUR par an, quel que soit son chiffre "
                        "d'affaires.",
    },
    "premiere_annee": {
        "article": "Article 4",
        "quoi": "Pour la PREMIÈRE liste publiée, les redevances sont "
                "réparties à PARTS ÉGALES entre les prestataires désignés. "
                "Pour la première année d'une désignation ultérieure, le "
                "prestataire acquitte un forfait égal à ce montant, au "
                "prorata des jours civils de supervision si l'année est "
                "incomplète.",
    },
    "paiement": {
        "article": "Article 5",
        "quoi": "Annuel, en euros, en une seule tranche. Les notes de "
                "débit laissent au moins trente jours.",
        "echeances": (
            "Supervisé depuis le 1er janvier : au plus tard le 30 avril de "
            "la même année.",
            "Désigné en cours d'année : au plus tard le 31 décembre de "
            "cette année.",
        ),
        "retard": "Intérêts de retard de l'article 99 du règlement "
                  "(UE, Euratom) 2018/1046.",
    },
    "couts_couverts": (
        ("a", "Désignation des prestataires comme critiques"),
        ("b", "Désignation du superviseur principal"),
        ("c", "Supervision effective — travaux de l'équipe d'examen "
              "conjoint et conseils des experts indépendants"),
        ("d", "Suivi des recommandations de l'article 35, paragraphe 1, "
              "point d)"),
        ("e", "Gouvernance du cadre de supervision"),
    ),
    "electronique": {
        "article": "Article 6",
        "quoi": "Toute communication entre les AES et les prestataires "
                "critiques se fait par voie électronique.",
    },
}


def redevance(couts_totaux_eur=None, ca_prestataire_eur=None,
              ca_tous_prestataires_eur=None, nombre_prestataires=None,
              premiere_liste=False, jours_supervises=None):
    """La redevance annuelle, et le plancher qui la relève.

    LE PLANCHER EST LA PARTIE QUI SURPREND, et c'est celle qu'on annonce
    en premier : un petit prestataire désigné critique paie 50 000 EUR
    même si son coefficient de chiffre d'affaires en donnerait cinq cents.
    """
    if not isinstance(couts_totaux_eur, (int, float)) or couts_totaux_eur <= 0:
        return {"ok": False, "motif": "couts_absents",
                "motif_texte": "Le montant total estimé des coûts annuels "
                               "des superviseurs n'est pas connu : il est "
                               "estimé chaque année et n'est pas dans le "
                               "texte.",
                "plancher_eur": REDEVANCE_PLANCHER_EUR,
                "reserve": RESERVE}

    # ── PREMIÈRE LISTE : PARTS ÉGALES, ET LE COEFFICIENT NE JOUE PAS ───
    if premiere_liste:
        if not isinstance(nombre_prestataires, int) or nombre_prestataires < 1:
            return {"ok": False, "motif": "nombre_absent",
                    "motif_texte": "La répartition à parts égales suppose "
                                   "de connaître le nombre de "
                                   "prestataires désignés.",
                    "reserve": RESERVE}
        brut = couts_totaux_eur / float(nombre_prestataires)
        base = "Article 4 — parts égales sur la première liste publiée."
        coefficient = None
    else:
        if not all(isinstance(x, (int, float)) and x > 0
                   for x in (ca_prestataire_eur, ca_tous_prestataires_eur)):
            return {"ok": False, "motif": "chiffre_affaires_absent",
                    "motif_texte": "Le coefficient suppose le chiffre "
                                   "d'affaires applicable du prestataire "
                                   "ET celui de tous les prestataires "
                                   "critiques, pour l'année n−2.",
                    "reserve": RESERVE}
        coefficient = ca_prestataire_eur / float(ca_tous_prestataires_eur)
        brut = couts_totaux_eur * coefficient
        base = "Article 3 — coûts annuels estimés × coefficient de "                "chiffre d'affaires."

    # ── LE PRORATA D'UNE ANNÉE INCOMPLÈTE, ET IL S'APPLIQUE AVANT ──────
    prorata = None
    if isinstance(jours_supervises, int) and 0 < jours_supervises < 365:
        prorata = jours_supervises / 365.0
        brut *= prorata

    due = max(brut, REDEVANCE_PLANCHER_EUR)
    return {
        "ok": True,
        "base": base,
        "coefficient": coefficient,
        "prorata": prorata,
        "brut_eur": round(brut, 2),
        "plancher_eur": REDEVANCE_PLANCHER_EUR,
        "due_eur": round(due, 2),
        "releve_par_le_plancher": due > brut,
        "dit": ("Le calcul donne %.2f EUR ; le plancher de l'article 3, "
                "paragraphe 3, porte la redevance à %.2f EUR."
                % (brut, due)) if due > brut else
               ("Le calcul donne %.2f EUR, au-dessus du plancher de "
                "%.0f EUR." % (brut, REDEVANCE_PLANCHER_EUR)),
        "echeances": list(REDEVANCES["paiement"]["echeances"]),
        "reserve": RESERVE,
    }


def referentiel():
    return {
        "version": VERSION,
        "reserve": RESERVE,
        "sources": [dict(s) for s in SOURCES],
        "lacunes": list(LACUNES),
        "criteres": [dict(c) for c in CRITERES],
        "methode": dict(METHODE),
        "seuil_part": SEUIL_PART,
        "sous_criteres": [dict(s) for s in SOUS_CRITERES],
        "sources_donnees": dict(SOURCES_DONNEES),
        "redevances": {
            "source": REDEVANCES["source"],
            "assiette": dict(REDEVANCES["assiette"]),
            "calcul": dict(REDEVANCES["calcul"]),
            "premiere_annee": dict(REDEVANCES["premiere_annee"]),
            "paiement": dict(REDEVANCES["paiement"],
                             echeances=list(
                                 REDEVANCES["paiement"]["echeances"])),
            "couts_couverts": [{"lettre": a, "quoi": b}
                               for a, b in REDEVANCES["couts_couverts"]],
            "electronique": dict(REDEVANCES["electronique"]),
        },
        "perimetre_groupe": dict(PERIMETRE_GROUPE),
        "point_coordination": dict(POINT_COORDINATION),
        "exclusions": [dict(x) for x in EXCLUSIONS],
        "procedure": [dict(p) for p in PROCEDURE],
        "volontaire": {"article": VOLONTAIRE["article"],
                       "quoi": VOLONTAIRE["quoi"],
                       "perimetre_groupe": VOLONTAIRE["perimetre_groupe"],
                       "informations": [{"lettre": a, "quoi": b}
                                        for a, b in
                                        VOLONTAIRE["informations"]]},
        "obligations": [dict(o) for o in OBLIGATIONS],
        "retombees_client": [dict(r) for r in RETOMBEES_CLIENT],
        "equipe_examen": {
            "source": EQUIPE_EXAMEN["source"],
            "quoi": EQUIPE_EXAMEN["quoi"],
            "mise_en_place": dict(EQUIPE_EXAMEN["mise_en_place"]),
            "composition": dict(EQUIPE_EXAMEN["composition"]),
            "revision": dict(EQUIPE_EXAMEN["revision"]),
            "modalites": dict(EQUIPE_EXAMEN["modalites"]),
            "taches": [{"lettre": a, "quoi": b}
                       for a, b in EQUIPE_EXAMEN["taches"]],
        },
        "liste": dict(LISTE),
        "issues": {k: dict(v) for k, v in ISSUES.items()},
    }


# ═══════════════════════════════════════════════════════════════════════
# 9. LE RÉFÉRENTIEL SE CONTREDIT-IL ? CONTRÔLÉ À L'IMPORT
# ═══════════════════════════════════════════════════════════════════════

def _verifier():
    fautes = []

    if len(EXCLUSIONS) != 4:
        fautes.append("l'article 31, paragraphe 8, compte quatre "
                      "exclusions, la table en porte %d" % len(EXCLUSIONS))
    if [x["point"] for x in EXCLUSIONS] != ["i", "ii", "iii", "iv"]:
        fautes.append("les exclusions ne suivent pas les points i à iv")
    if len(CRITERES) != 4:
        fautes.append("l'article 31, paragraphe 2, compte quatre critères, "
                      "la table en porte %d" % len(CRITERES))
    if [c["lettre"] for c in CRITERES] != ["a", "b", "c", "d"]:
        fautes.append("les critères ne suivent pas les points a) à d)")

    # ── CHAQUE EXCLUSION DIT POURQUOI ELLE EXISTE. Une exclusion sans
    #    motif se lit comme une faveur ; avec son motif, elle se discute.
    for x in EXCLUSIONS:
        if not x.get("pourquoi"):
            fautes.append("exclusion %s : aucun motif" % x["cle"])

    # ── LES SEUILS VIVENT SUR LES SOUS-CRITÈRES, JAMAIS SUR LES
    #    CRITÈRES. L'article 31, paragraphe 2, énonce ; l'acte délégué
    #    chiffre. Poser un seuil sur un critère effacerait cette
    #    distinction, et ferait croire que le règlement lui-même chiffre.
    for c in CRITERES:
        for interdit in ("poids", "seuil", "note", "taux"):
            if interdit in c:
                fautes.append(
                    "critère %s porte un %r : l'article 31, paragraphe 2, "
                    "énonce et ne chiffre pas — les seuils appartiennent "
                    "aux sous-critères de l'acte délégué" % (c["cle"],
                                                              interdit))

    # ── CHAQUE SOUS-CRITÈRE SE RATTACHE À UN CRITÈRE EXISTANT, PORTE SON
    #    ARTICLE, ET N'A DE SEUIL QU'À L'ÉTAPE 1.
    connus = {c["cle"] for c in CRITERES}
    for s in SOUS_CRITERES:
        if s["critere"] not in connus:
            fautes.append("sous-critère %s : critère inconnu %r"
                          % (s["cle"], s["critere"]))
        if s["etape"] not in (1, 2):
            fautes.append("sous-critère %s : étape %r" % (s["cle"],
                                                          s["etape"]))
        if not s.get("article"):
            fautes.append("sous-critère %s : aucun article" % s["cle"])
        if s["etape"] == 2 and s.get("seuil") is not None:
            fautes.append(
                "sous-critère %s est à l'étape 2 et porte un seuil : "
                "l'étape 2 s'APPRÉCIE, et lui donner un seuil ferait "
                "calculer une désignation que les AES prononcent"
                % s["cle"])

    # ── LE CRITÈRE c) N'A AUCUN SOUS-CRITÈRE D'ÉTAPE 1. L'article
    #    premier, §1, second alinéa, le dit expressément ; lui en ajouter
    #    un fabriquerait un filtre que le texte ne pose pas.
    c_etape1 = [s["cle"] for s in SOUS_CRITERES
                if s["critere"] == "fonctions_critiques" and s["etape"] == 1]
    if c_etape1:
        fautes.append(
            "le critère c) reçoit un sous-critère d'étape 1 (%s) alors que "
            "l'acte délégué dit sa première étape couverte par les "
            "critères a), b) et d)" % c_etape1)

    # ── LES QUATRE SOUS-CRITÈRES DE PART PORTENT LE MÊME SEUIL, ÉCRIT
    #    UNE SEULE FOIS. Deux seuils divergents sur la même barre des
    #    10 % seraient invisibles à la relecture.
    parts = [s for s in SOUS_CRITERES if s.get("seuil") is not None]
    if len(parts) != 4:
        fautes.append("quatre sous-critères portent une part de 10 %%, la "
                      "table en compte %d" % len(parts))
    if any(s["seuil"] != SEUIL_PART for s in parts):
        fautes.append("un sous-critère de part s'écarte du seuil unique")

    # ── LE PLANCHER DE REDEVANCE EST UN PLANCHER, PAS UN MONTANT.
    if REDEVANCE_PLANCHER_EUR != 50000.0:
        fautes.append("le plancher de redevance de l'article 3, "
                      "paragraphe 3, vaut 50 000 EUR, la table dit %r"
                      % REDEVANCE_PLANCHER_EUR)
    if REDEVANCES["calcul"]["plancher_eur"] != REDEVANCE_PLANCHER_EUR:
        fautes.append("le plancher est écrit deux fois et diverge")

    # ── LA PROCÉDURE EST ORDONNÉE, ET SANS TROU.
    if [p["rang"] for p in PROCEDURE] != list(range(1, len(PROCEDURE) + 1)):
        fautes.append("les rangs de la procédure ne se suivent pas")
    for p in PROCEDURE:
        if not p.get("article"):
            fautes.append("étape %s : aucun article" % p["cle"])

    # ── LES TREIZE INFORMATIONS DE LA DEMANDE VOLONTAIRE, DE a) À m).
    lettres = [a for a, _b in VOLONTAIRE["informations"]]
    attendu = [chr(c) for c in range(ord("a"), ord("m") + 1)]
    if lettres != attendu:
        fautes.append("la demande volontaire ne porte pas les points a) à "
                      "m) : %s" % lettres)

    # ── CHAQUE RETOMBÉE DIT QUOI FAIRE. Une conséquence sans geste est
    #    une inquiétude, pas un conseil.
    for r in RETOMBEES_CLIENT:
        if not r.get("quoi_faire") or not r.get("article"):
            fautes.append("retombée %s : sans article ou sans geste"
                          % r["cle"])
    for o in OBLIGATIONS:
        if not o.get("article") or not o.get("ce_qui_surprend"):
            fautes.append("obligation %s : incomplète" % o["cle"])

    return fautes


_FAUTES = _verifier()
assert not _FAUTES, "dora_supervision.py se contredit : %s" % _FAUTES
