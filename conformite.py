# -*- coding: utf-8 -*-
"""Le taux de conformité des neuf normes, et le plan qui le fait monter.

LA DEMANDE : un taux entre 0 et 100 % pour chacune des neuf normes de
Sentinel, tiré des analyses de risque et des réponses aux questionnaires, puis
un plan d'action et de remédiation pour s'approcher de 100 %.

CE QUI REND L'EXERCICE DANGEREUX, ET QUE CE MODULE REFUSE DE FAIRE.

  1. NEUF POURCENTAGES ALIGNÉS SE LISENT COMME NEUF FOIS LA MÊME CHOSE.
     Ils ne le sont pas. « 80 % » sur l'ISO 42001 veut dire « prêt aux quatre
     cinquièmes pour un audit de certification » ; « 80 % » sur le NIST AI RMF
     ne veut rien dire de tel, puisque ce cadre N'EST PAS CERTIFIABLE — il n'y
     a pas d'auditeur au bout. Chaque norme porte donc sa NATURE, et la nature
     dit en toutes lettres ce que 100 % signifie ET ce qu'il ne signifie pas.

  2. UNE MOYENNE PLATE CACHE LE DÉFAUT QUI ARRÊTE TOUT. Le module ISO 42001 de
     ce dépôt l'écrit déjà : « un organisme à 90 % de maturité avec une
     déclaration irrecevable n'est pas presque prêt, il est arrêté ». Le taux
     est donc COMPOSÉ de parts déclarées, puis PLAFONNÉ par ses verrous : un
     verrou n'annule pas le travail fait, il interdit de le compter au-delà de
     ce qu'il laisse passer. Le maillon le plus faible commande — la même
     règle que securite_ia applique à la chaîne d'autonomie.

  3. UN TAUX SUR UNE NORME QU'ON NE MESURE PAS EST UN MENSONGE POLI. DORA n'a
     pas de module ici : son taux est None, jamais 0. Zéro voudrait dire « rien
     de fait » ; None veut dire « nous ne le mesurons pas », et c'est la
     vérité.

  4. UNE MOYENNE DES NEUF SERAIT LE PIRE DES DEUX MONDES. On rend donc ce qui
     COMMANDE — le plus bas des taux mesurés — et la moyenne à côté, nommée
     comme telle, parce qu'un comité la calculera de toute façon et qu'il vaut
     mieux qu'elle soit posée avec son avertissement que reconstituée sans.

D'OÙ VIENNENT LES CHIFFRES. De nulle part ailleurs que des modules déjà en
place : iso42001, iso27001, nis2, cra, nist_ai_rmf, owasp_llm évaluent chacun
une déclaration et nomment leurs écarts. Ce module ne réévalue rien — il
COMPOSE. S'il inventait sa propre notation, il y aurait deux vérités sur la
même norme, et c'est exactement le défaut qu'on a trouvé dans l'indice à trois
cadres de l'écran (voir plus bas, RECALAGE).
"""
import copy

VERSION = "2026-09-a"

# ══════════════════════════════════════════════════════════════════════════
#  LES NATURES — CE QUE 100 % VEUT DIRE, ET CE QU'IL NE VEUT PAS DIRE
# ══════════════════════════════════════════════════════════════════════════
#
# LA COLONNE QUI COMPTE EST LA DERNIÈRE. Un écran qui affiche « 100 % » sans
# dire de quoi laisse le lecteur conclure « nous sommes conformes », ce qu'un
# taux ne peut jamais établir : sur une obligation, c'est une autorité qui
# tranche ; sur une norme certifiable, un auditeur ; sur un cadre volontaire,
# personne. Le taux mesure le TRAVAIL FAIT, et rien d'autre.

NATURES = {
    "certifiable": {
        "nom": "Norme certifiable",
        "taux_dit": "préparation à l'audit de certification",
        "cent_veut_dire": "Les articles sont tenus, la déclaration "
                          "d'applicabilité est recevable et les mesures "
                          "retenues sont mises en œuvre.",
        "cent_ne_veut_pas_dire": "Que vous êtes certifié. Un organisme "
                                 "accrédité conduit l'audit, et lui seul "
                                 "délivre le certificat.",
    },
    "obligation": {
        "nom": "Obligation légale",
        "taux_dit": "écarts mesurés refermés",
        "cent_veut_dire": "Aucun des écarts que ce module sait mesurer ne "
                          "reste ouvert.",
        "cent_ne_veut_pas_dire": "Que vous êtes en conformité. L'autorité de "
                                 "contrôle apprécie, sur pièces, et son "
                                 "périmètre déborde ce qu'un questionnaire "
                                 "couvre.",
    },
    "cadre": {
        "nom": "Cadre volontaire",
        "taux_dit": "couverture du cadre",
        "cent_veut_dire": "Chaque point du cadre porte un état déclaré et "
                          "démontrable.",
        "cent_ne_veut_pas_dire": "Une conformité. Ce cadre n'est pas "
                                 "certifiable : il n'existe aucun auditeur "
                                 "au bout, et personne ne peut délivrer "
                                 "d'attestation contre lui.",
    },
    "risques": {
        "nom": "Liste de risques",
        "taux_dit": "risques traités",
        "cent_veut_dire": "Chacun des risques de la liste est traité, ou "
                          "écarté avec son motif.",
        "cent_ne_veut_pas_dire": "Une immunité, ni une conformité. Une liste "
                                 "de risques n'est pas un référentiel "
                                 "d'exigences, et traiter les dix n'épuise "
                                 "pas les risques d'une application.",
    },
    "sans_instrument": {
        "nom": "Sans instrument de mesure ici",
        "taux_dit": None,
        "cent_veut_dire": None,
        "cent_ne_veut_pas_dire": "Un taux de 0 %. L'absence de mesure n'est "
                                 "pas une absence de conformité — c'est une "
                                 "absence de mesure, et les deux ne se "
                                 "confondent pas.",
    },
}


# ══════════════════════════════════════════════════════════════════════════
#  LES ONZE NORMES, DANS L'ORDRE DE LA PAGE D'ACCUEIL
# ══════════════════════════════════════════════════════════════════════════
#
# `panneau` est la destination Sentinel : un taux qui ne mène pas à l'écran
# où on le corrige est un reproche, pas un outil.

NORMES = [
    {"cle": "ia_act", "nom": "IA Act", "nature": "obligation",
     "texte": "Règlement (UE) 2024/1689",
     "panneau": "ia-act-hub",
     "mesure": "les trente-quatre points de l'audit, article par article"},
    {"cle": "cra", "nom": "CRA", "nature": "obligation",
     "texte": "Règlement (UE) 2024/2847",
     "panneau": "cra-role",
     "mesure": "les exigences de l'annexe I, parties I et II"},
    {"cle": "iso42001", "nom": "ISO/IEC 42001", "nature": "certifiable",
     "texte": "ISO/IEC 42001:2023",
     "panneau": "iso42001",
     "mesure": "les articles 4 à 10 et la déclaration d'applicabilité"},
    {"cle": "iso27001", "nom": "ISO/IEC 27001", "nature": "certifiable",
     "texte": "ISO/IEC 27001:2022",
     "panneau": "iso27001-risques",
     "mesure": "l'appréciation du risque, les articles et la déclaration "
               "d'applicabilité"},
    {"cle": "dora", "nom": "DORA", "nature": "obligation",
     "texte": "Règlement (UE) 2022/2554",
     "panneau": "dora-qualifier",
     "mesure": "les articles du règlement délégué (UE) 2024/1774 du régime "
               "qui est le vôtre, et les quinze clauses de l'article 30"},
    {"cle": "nis2", "nom": "NIS 2", "nature": "obligation",
     "texte": "Directive (UE) 2022/2555",
     "panneau": "nis2-qualifier",
     "mesure": "les dix mesures de l'article 21 §2 et la gouvernance de "
               "l'article 20"},
    {"cle": "rgpd", "nom": "RGPD", "nature": "obligation",
     "texte": "Règlement (UE) 2016/679",
     "panneau": "rgpd-hub",
     "mesure": "la complétude du dispositif documentaire"},
    {"cle": "nist_ai_rmf", "nom": "NIST AI RMF", "nature": "cadre",
     "texte": "NIST AI 100-1 (2023)",
     "panneau": "nist-profil",
     "mesure": "les soixante-douze sous-catégories des quatre fonctions"},
    {"cle": "owasp_llm", "nom": "OWASP Top 10 LLM", "nature": "risques",
     "texte": "OWASP Top 10 for LLM Applications, 2025",
     "panneau": "owasp-dix",
     "mesure": "les dix risques de la liste"},
    {"cle": "nist_800_53", "nom": "NIST SP 800-53", "nature": "cadre",
     "texte": "NIST SP 800-53 Rev. 4 (2013)",
     "panneau": "nist53-socle",
     "mesure": "les dix-huit familles de mesures, et le socle qu'elles "
               "supposent"},
    {"cle": "nist_800_82", "nom": "NIST SP 800-82", "nature": "cadre",
     "texte": "NIST SP 800-82 Rev. 2 (2015)",
     "panneau": "nist82-ot",
     "mesure": "les dix axes de la surcharge industrielle, plafonnés par le "
               "socle 800-53 qu'ils taillent"},
]
NORMES_PAR_CLE = {n["cle"]: n for n in NORMES}

#: CE QUE LA PAGE D'ACCUEIL ANNONCE. Un seul endroit le décide ; la
#: garde en bas de fichier le confronte à la table ci-dessus, et une
#: règle de la suite le confronte au titre et à la grille de l'accueil.
NORMES_ANNONCEES = 11


# ══════════════════════════════════════════════════════════════════════════
#  L'AUDIT IA ACT — LE RÉFÉRENTIEL, ET POURQUOI IL EST ÉCRIT DEUX FOIS
# ══════════════════════════════════════════════════════════════════════════
#
# LES HUIT SECTIONS ET LES TRENTE-QUATRE POINTS DE L'AUDIT VIVENT AUSSI DANS
# `sentinel.page.js`, sous le nom `AUDIT_SECTIONS`. C'est une duplication, et
# ce dépôt en refuse d'ordinaire — le titre des « neuf normes maîtrisées »
# vient d'être corrigé pour cette raison exacte.
#
# CE QUI LA REND ACCEPTABLE ICI, ET RIEN D'AUTRE : une règle compare les deux
# listes point par point — identifiants, section, priorité — et refuse la
# moindre divergence. La duplication qui nuit est celle que personne ne
# vérifie ; celle-ci ne peut pas dériver d'un cran sans que la recette tombe.
#
# POURQUOI NE PAS AVOIR SUPPRIMÉ L'UNE DES DEUX. L'écran tient l'état de
# l'audit dans le navigateur, indexé par ces identifiants, et des évaluations
# enregistrées les portent déjà. Faire lire la liste depuis l'API changerait
# l'ordre d'initialisation d'un écran en service, pour un gain qui est
# précisément celui que la règle apporte sans risque. Le sens de la
# duplication est posé : le PYTHON est normatif, le JavaScript en est la copie
# à remplacer le jour où cet écran sera repris.

AUDIT_IA_ACT_SECTIONS = (
    ("art5", "Pratiques interdites", "Art. 5"),
    ("art6", "Classification haut risque", "Art. 6 + Annexe III"),
    ("art9_10", "Gestion des risques & Gouvernance des données", "Art. 9-10"),
    ("art11_12", "Documentation technique & Journalisation", "Art. 11-12"),
    ("art13_14", "Transparence & Supervision humaine", "Art. 13-14"),
    ("art15_17", "Robustesse, Exactitude & Qualité", "Art. 15-17"),
    ("art49_51", "Évaluation de conformité & Enregistrement", "Art. 43-49, 51"),
    ("gpai", "Modèles GPAI", "Art. 51-55"),
)

# (identifiant, section, intitulé, article, priorité)
AUDIT_IA_ACT = (
    ("a5_1", "art5", "Inventaire des pratiques potentiellement interdites", "Art. 5(1)(a)(b)(c)", "p1"),
    ("a5_2", "art5", "Absence d'identification biométrique à distance non autorisée", "Art. 5(1)(h)", "p1"),
    ("a5_3", "art5", "Vérification du périmètre émotionnel et de catégorisation", "Art. 5(1)(f)(g)", "p1"),
    ("a5_4", "art5", "Formation littératie IA (Art. 4)", "Art. 4", "p2"),
    ("a6_1", "art6", "Cartographie complète des systèmes IA", "Art. 6, Art. 51", "p1"),
    ("a6_2", "art6", "Classification selon l'Annexe III (8 domaines)", "Art. 6(2), Annexe III", "p1"),
    ("a6_3", "art6", "Documentation de la décision de classification", "Art. 6(4)", "p2"),
    ("a6_4", "art6", "Procédure de reclassification continue", "Art. 6, Art. 9", "p2"),
    ("a9_1", "art9_10", "Système de gestion des risques documenté et opérationnel", "Art. 9(1)(2)", "p1"),
    ("a9_2", "art9_10", "Tests avant mise sur le marché", "Art. 9(5)(6)", "p1"),
    ("a9_3", "art9_10", "Gouvernance des données d'entraînement", "Art. 10(2)", "p1"),
    ("a9_4", "art9_10", "Qualité des données de validation et de test", "Art. 10(3)(4)", "p1"),
    ("a9_5", "art9_10", "Données personnelles dans l'entraînement", "Art. 10(5), RGPD", "p2"),
    ("a11_1", "art11_12", "Dossier technique complet (Annexe IV)", "Art. 11, Annexe IV", "p1"),
    ("a11_2", "art11_12", "Mise à jour continue du dossier technique", "Art. 11(2)", "p2"),
    ("a12_1", "art11_12", "Journalisation automatique des décisions", "Art. 12(1)(2)", "p1"),
    ("a12_2", "art11_12", "Conservation des journaux", "Art. 12(3)", "p2"),
    ("a18_1", "art11_12", "Conservation de la documentation technique (10 ans)", "Art. 18", "p2"),
    ("a13_1", "art13_14", "Notice d'utilisation conforme Art. 13", "Art. 13(3)", "p1"),
    ("a13_2", "art13_14", "Transparence envers les utilisateurs finaux (Art. 50)", "Art. 50(1)(2)", "p1"),
    ("a14_1", "art13_14", "Mécanismes de supervision humaine fonctionnels", "Art. 14(1)(3)", "p1"),
    ("a14_2", "art13_14", "Désignation et formation des superviseurs", "Art. 14(4)", "p2"),
    ("a15_1", "art15_17", "Niveaux d'exactitude définis et mesurés", "Art. 15(1)(3)", "p1"),
    ("a15_2", "art15_17", "Robustesse aux erreurs et aux manipulations", "Art. 15(4)(5)", "p2"),
    ("a17_1", "art15_17", "Système de gestion de la qualité (Art. 17)", "Art. 17", "p1"),
    ("a17_2", "art15_17", "Surveillance post-commercialisation", "Art. 17(1)(k), Art. 72", "p2"),
    ("a43_1", "art49_51", "Évaluation de conformité réalisée", "Art. 43, 44, Annexe VI", "p1"),
    ("a47_1", "art49_51", "Déclaration UE de conformité", "Art. 47", "p1"),
    ("a48_1", "art49_51", "Marquage CE apposé", "Art. 48", "p2"),
    ("a51_1", "art49_51", "Enregistrement dans la base de données EU", "Art. 71, Art. 49", "p1"),
    ("g53_1", "gpai", "Documentation GPAI (Art. 53)", "Art. 53(1)", "p1"),
    ("g53_2", "gpai", "Politique de droits d'auteur et droit d'opposition", "Art. 53(1)(c)", "p1"),
    ("g55_1", "gpai", "Évaluation adversariale (modèles systémiques)", "Art. 55(1)(a)(b)", "p1"),
    ("g55_2", "gpai", "Signalement des incidents (GPAI systémiques)", "Art. 55(1)(d)", "p1"),
)

# LES DEUX PRIORITÉS, ET CE QUI LES SÉPARE.
PRIORITES_IA_ACT = {
    "p1": {"nom": "Priorité 1",
           "dit": "Pratiques interdites, classification, documentation : un "
                  "écart s'y solde par un retrait du marché, pas par une "
                  "observation."},
    "p2": {"nom": "Priorité 2",
           "dit": "Le reste de l'audit — nécessaire, mais qui ne ferme pas "
                  "l'accès au marché à lui seul."},
}

_ETATS_AUDIT = ("tenu", "partiel", "absent", "sans_objet")


def evaluer_audit_ia_act(reponses=None):
    """L'audit IA Act, évalué ici faute d'un module qui le fasse ailleurs.

    UN POINT NON RENSEIGNÉ N'EST PAS UN POINT TENU — la même règle que le
    module CRA pose en tête de son analyse d'écart, pour la même raison : un
    tableau qui compte les cases vides comme vertes rend un taux flatteur et
    faux, celui qu'on montre en comité et qui se défait au premier contrôle.
    """
    r = reponses or {}
    if not isinstance(r, dict):
        return {"ok": False, "motif": "reponses_illisibles"}
    points = []
    for cle, section, titre, article, prio in AUDIT_IA_ACT:
        e = r.get(cle)
        points.append({"cle": cle, "section": section, "titre": titre,
                       "article": article, "prio": prio,
                       "etat": e if e in _ETATS_AUDIT else "non_renseigne"})
    return {"ok": True, "points": points,
            "sections": [{"cle": c, "titre": t, "article": a}
                         for c, t, a in AUDIT_IA_ACT_SECTIONS],
            "priorites": PRIORITES_IA_ACT,
            "total": len(points),
            "renseignes": sum(1 for p in points
                              if p["etat"] != "non_renseigne")}


# ══════════════════════════════════════════════════════════════════════════
#  LA COMPOSITION D'UN TAUX
# ══════════════════════════════════════════════════════════════════════════
#
# POURQUOI DES POIDS, ET POURQUOI ILS SONT ÉCRITS ICI. Une moyenne plate des
# parts d'une norme suppose qu'elles pèsent pareil. Elles ne pèsent pas
# pareil : sur l'ISO 27001, l'appréciation du risque commande tout le reste —
# sans elle la déclaration d'applicabilité n'a rien à justifier. Les poids
# sont donc DÉCLARÉS, avec leur motif, et une règle vérifie qu'aucun n'est nul
# (un composant de poids zéro est un composant qu'on ferait mieux de retirer).
#
# LES VERROUS. Un verrou nomme un défaut qui ARRÊTE la démarche, et les parts
# qu'il rend inatteignables. Le plafond qu'il impose est la somme des poids
# NON bloqués : le travail déjà fait reste compté, mais on ne peut plus
# prétendre au-delà. C'est la différence entre « vous avez fait 70 % du
# chemin » et « vous êtes à 70 % de la conformité » — la première est vraie,
# la seconde est fausse tant que la porte est fermée.

COMPOSITIONS = {
    "iso42001": [
        {"cle": "articles", "nom": "Articles 4 à 10 tenus", "poids": 2,
         "pourquoi": "le système de management lui-même ; sans lui il n'y a "
                     "rien à certifier"},
        {"cle": "propres_ia", "nom": "Articles propres à l'IA", "poids": 2,
         "pourquoi": "ce qui distingue cette norme d'un SMSI générique — "
                     "c'est là que se joue l'étape 2"},
        {"cle": "mesures", "nom": "Mesures retenues mises en œuvre", "poids": 1,
         "pourquoi": "l'annexe A se choisit ; ce qui compte est que le choix "
                     "soit appliqué, pas qu'il soit large"},
    ],
    "iso27001": [
        {"cle": "risque", "nom": "Appréciation du risque conduite", "poids": 2,
         "pourquoi": "elle commande la déclaration d'applicabilité : sans "
                     "elle, aucune exclusion ne se justifie"},
        {"cle": "articles", "nom": "Articles 4 à 10 tenus", "poids": 2,
         "pourquoi": "le SMSI lui-même"},
        {"cle": "mesures", "nom": "Mesures retenues mises en œuvre", "poids": 1,
         "pourquoi": "les 93 mesures de l'annexe A se retiennent ou "
                     "s'écartent ; seule la mise en œuvre du retenu compte"},
    ],
    "nis2": [
        {"cle": "mesures", "nom": "Les dix mesures de l'article 21 §2",
         "poids": 3,
         "pourquoi": "la directive dit « comprennent au moins » : c'est un "
                     "plancher, et un plancher se tient entièrement"},
        {"cle": "gouvernance", "nom": "Gouvernance de l'article 20", "poids": 2,
         "pourquoi": "la seule partie dont les dirigeants répondent "
                     "personnellement"},
    ],
    "cra": [
        {"cle": "produit", "nom": "Exigences de l'annexe I, partie I",
         "poids": 2,
         "pourquoi": "les propriétés du produit — elles se vérifient sur une "
                     "version livrable"},
        {"cle": "vulnerabilites", "nom": "Annexe I, partie II — "
                                          "vulnérabilités", "poids": 2,
         "pourquoi": "le traitement des vulnérabilités court sur toute la "
                     "durée de support, bien après la mise sur le marché"},
    ],
    "nist_ai_rmf": [
        {"cle": "govern", "nom": "GOVERN", "poids": 2,
         "pourquoi": "le socle : le cadre lui-même place cette fonction "
                     "au-dessus des trois autres"},
        {"cle": "map", "nom": "MAP", "poids": 1, "pourquoi": "une fonction"},
        {"cle": "measure", "nom": "MEASURE", "poids": 1,
         "pourquoi": "une fonction"},
        {"cle": "manage", "nom": "MANAGE", "poids": 1,
         "pourquoi": "une fonction"},
    ],
    "owasp_llm": [
        {"cle": "risques", "nom": "Les dix risques", "poids": 1,
         "pourquoi": "la liste n'est pas ordonnée par gravité : rien ne "
                     "justifierait d'y pondérer un risque plus qu'un autre"},
    ],
    "ia_act": [
        {"cle": "p1", "nom": "Points de priorité 1", "poids": 2,
         "pourquoi": "les pratiques interdites et la classification : un "
                     "écart s'y solde par un retrait, pas par une amende"},
        {"cle": "p2", "nom": "Points de priorité 2", "poids": 1,
         "pourquoi": "le reste de l'audit"},
    ],
    "rgpd": [
        {"cle": "registre", "nom": "Registre des traitements", "poids": 2,
         "pourquoi": "article 30 : la pièce qu'une autorité demande en "
                     "premier, et celle dont l'absence est constatable "
                     "immédiatement"},
        {"cle": "pbd", "nom": "Privacy by design", "poids": 1,
         "pourquoi": "article 25"},
        {"cle": "doc", "nom": "Documentation", "poids": 1,
         "pourquoi": "l'accountability de l'article 5 §2"},
        {"cle": "sensibilisation", "nom": "Sensibilisation", "poids": 1,
         "pourquoi": "article 39 : ce qui décide si le reste est appliqué"},
    ],
    # DEUX PARTS, ET PAS TROIS. La chaîne de notification des incidents se
    # mesure sur un incident réel, pas sur un questionnaire : lui donner une
    # part reviendrait à noter une intention. Elle est donc dite en réserve,
    # là où elle ne gonfle aucun taux.
    "dora": [
        {"cle": "cadre", "nom": "Cadre de gestion du risque lié aux TIC",
         "poids": 3,
         "pourquoi": "l'objet même du règlement : les articles du règlement "
                     "délégué (UE) 2024/1774 que votre régime rend "
                     "opposables, et ce que l'autorité ouvre en premier"},
        {"cle": "tiers", "nom": "Clauses contractuelles de l'article 30",
         "poids": 2,
         "pourquoi": "une clause absente ne se rattrape pas après la "
                     "signature — il faut rouvrir le contrat, et le "
                     "prestataire n'y a aucun intérêt"},
    ],
    # LES CINQ GROUPES DU CATALOGUE, ET LE PREMIER PÈSE PLUS QUE LES AUTRES.
    # Ce n'est pas une préférence : RA, PL, CA et PM produisent le socle, le
    # plan et l'autorisation. Les quatorze familles restantes exécutent ce
    # que ces quatre-là ont décidé.
    "nist_800_53": [
        {"cle": "pilotage", "nom": "Pilotage et autorisation", "poids": 3,
         "pourquoi": "le socle, le plan et l'autorisation : sans eux, les "
                     "autres familles s'appliquent sans mandat"},
        {"cle": "maitrise", "nom": "Maîtrise du système et de sa chaîne",
         "poids": 2,
         "pourquoi": "ce qui tourne, d'où cela vient, et qui y intervient"},
        {"cle": "acces", "nom": "Accès, personnes et lieux", "poids": 2,
         "pourquoi": "le chemin le plus emprunté reste un accès légitime "
                     "mal tenu"},
        {"cle": "exploitation", "nom": "Exploitation, détection et reprise",
         "poids": 2,
         "pourquoi": "ce qui se passe une fois en service, y compris le "
                     "jour où le système tombe"},
        {"cle": "donnees", "nom": "Protection des données et des échanges",
         "poids": 2,
         "pourquoi": "la donnée elle-même, en transit et sur support"},
    ],
    # LA SURCHARGE INDUSTRIELLE EN TROIS PARTS, ET LA PREMIÈRE COMMANDE.
    # Dans un système industriel, la sûreté prime sur la sécurité : une
    # mesure qui peut arrêter un procédé est un événement de sûreté avant
    # d'être un incident informatique.
    "nist_800_82": [
        {"cle": "socle_ot", "nom": "Sûreté, disponibilité et reprise",
         "poids": 3,
         "pourquoi": "les trois axes dont dépend la vie du procédé — et, "
                     "dans cet ordre, des personnes"},
        {"cle": "architecture", "nom": "Architecture et flux", "poids": 2,
         "pourquoi": "segmentation, filtrage, redondance : ce qui décide "
                     "jusqu'où une intrusion se propage"},
        {"cle": "conduite", "nom": "Conduite au quotidien", "poids": 2,
         "pourquoi": "authentification, surveillance, équipements hérités et "
                     "les métiers qui tiennent le réseau"},
    ],
}

VERROUS = {
    "iso42001": [
        {"cle": "soa_irrecevable",
         "dit": "La déclaration d'applicabilité ne passe pas l'étape 1. "
                "L'auditeur s'arrête au document : aucun taux de maturité ne "
                "rattrape ce défaut.",
         "bloque": ["mesures"],
         "ou": "iso42001 · déclaration d'applicabilité"},
    ],
    "iso27001": [
        {"cle": "perimetre_absent",
         "dit": "Le périmètre du SMSI n'est pas écrit. Tout ce qui n'est pas "
                "exclu par écrit est audité — un périmètre flou est la "
                "première cause de dérive du coût d'audit.",
         "bloque": ["articles", "mesures"],
         "ou": "iso27001 · périmètre"},
        {"cle": "soa_irrecevable",
         "dit": "La déclaration d'applicabilité ne passe pas l'étape 1.",
         "bloque": ["mesures"],
         "ou": "iso27001 · déclaration d'applicabilité"},
    ],
}

# ── LES RÉSERVES : CE QUI N'EST PAS UN VERROU ───────────────────────────────
#
# TROIS « VERROUS » ONT ÉTÉ ÉCRITS ICI AVANT D'ÊTRE RECONNUS POUR AUTRE CHOSE,
# et c'est la garde de ce module qui l'a dit : ils bloquaient TOUS les
# composants de leur norme, donc imposaient un plafond de zéro. Un taux
# toujours nul n'est pas un plafond, c'est un effacement — il jette le travail
# fait au lieu d'en limiter la portée.
#
# LA LIGNE QUI LES SÉPARE, ET ELLE EST VÉRIFIABLE : un VERROU existe là où un
# TIERS REFUSE D'ALLER PLUS LOIN. L'auditeur qui s'arrête sur une déclaration
# d'applicabilité irrecevable est une porte fermée, et une porte fermée se
# chiffre. Ne pas savoir si l'on est entité essentielle ou importante n'est
# pas une porte fermée : les dix mesures de l'article 21 §2 sont le même
# plancher dans les deux régimes, et le travail fait vaut ce qu'il vaut.
#
# Ce qui manque alors n'est pas de la conformité, c'est une CERTITUDE sur ce
# contre quoi on se mesure. On le dit, on en fait une action de premier rang —
# elle coûte peu et change le sens de tout le reste — et on ne touche pas au
# taux. La garde vérifie qu'aucun verrou ne vit hors d'une norme certifiable,
# parce que c'est là, et seulement là, qu'il y a une porte.

RESERVES = {
    "nis2": [
        {"cle": "non_qualifie",
         "dit": "L'entité n'est pas qualifiée : on ne sait pas si le régime "
                "est celui des entités essentielles ou importantes.",
         "porte_sur": "Le taux vaut pour les dix mesures, qui sont le même "
                      "plancher dans les deux régimes. Ce qui change avec la "
                      "qualification, c'est la supervision — a priori ou a "
                      "posteriori — et le plafond des sanctions.",
         "ou": "nis2 · qualification"},
    ],
    "nist_800_53": [
        {"cle": "millesime",
         "dit": "Ce module vise la révision 4 du catalogue, parce que c'est "
                "celle que la surcharge industrielle SP 800-82 Rev. 2 "
                "adapte. La révision 5 est la version courante.",
         "porte_sur": "La révision 5 ajoute les familles PT et SR et renomme "
                      "CA. Un système déjà aligné sur la révision 5 lit ce "
                      "taux contre un millésime antérieur au sien.",
         "ou": "nist53 · millésime"},
        {"cle": "non_certifiable",
         "dit": "SP 800-53 ne se certifie pas : aucun organisme ne délivre "
                "d'attestation contre ce catalogue.",
         "porte_sur": "Le taux dit une couverture déclarée, pas une "
                      "conformité reconnue. « Conforme 800-53 » ne veut rien "
                      "dire hors du périmètre fédéral américain.",
         "ou": "nist53 · portée"},
    ],
    "nist_800_82": [
        {"cle": "surcharge",
         "dit": "Ce taux mesure ce que l'industriel AJOUTE au catalogue "
                "800-53, et il est plafonné par ce que ce catalogue porte "
                "déjà.",
         "porte_sur": "Une mesure taillée ne peut pas être plus solide que "
                      "celle qu'elle taille : un axe déclaré au-dessus de "
                      "sa famille 800-53 est ramené à elle, et le "
                      "dépassement est signalé plutôt qu'effacé.",
         "ou": "nist82 · surcharge"},
        {"cle": "millesime",
         "dit": "La révision 2 (2015) parle d'ICS et surcharge 800-53 Rev. 4. "
                "La révision 3 (2023) parle d'OT et vise la révision 5.",
         "porte_sur": "Les deux révisions ne recouvrent pas le même "
                      "catalogue. Mesurer contre l'une en croyant tenir "
                      "l'autre est le défaut que ce module refuse.",
         "ou": "nist82 · millésime"},
    ],
    "cra": [
        {"cle": "role_absent",
         "dit": "Le rôle n'est pas qualifié ; le taux est calculé comme si "
                "vous étiez fabricant.",
         "porte_sur": "Fabricant, importateur et distributeur ne portent pas "
                      "les mêmes obligations. Si vous n'êtes pas fabricant, "
                      "une partie des exigences mesurées ici ne vous incombe "
                      "pas — et d'autres, qui ne sont pas mesurées, vous "
                      "incombent.",
         "ou": "cra · rôle"},
    ],
    "dora": [
        {"cle": "regime_absent",
         "dit": "Le régime n'est pas déterminé : on ne sait pas si le cadre "
                "complet ou le cadre simplifié de l'article 16 s'applique.",
         "porte_sur": "Les deux cadres ne portent pas les mêmes articles — "
                      "vingt-six d'un côté, quatorze de l'autre — et ils ne "
                      "se recouvrent pas. Tant que la qualification n'est "
                      "pas faite, la part « cadre » ne peut pas être "
                      "mesurée, et compte donc pour zéro.",
         "ou": "dora · qualification"},
        {"cle": "hors_taux",
         "dit": "Ce taux porte sur le cadre de gestion du risque et sur les "
                "contrats. Il ne porte sur rien d'autre.",
         "porte_sur": "La chaîne de notification et ses délais en heures, "
                      "les tests de pénétration fondés sur la menace, et le "
                      "registre d'informations de l'article 28, "
                      "paragraphe 3, ne sont pas dans ce nombre. Cent pour "
                      "cent ici ne veut pas dire DORA tenu.",
         "ou": "dora · portée du taux"},
    ],
    "nist_ai_rmf": [
        {"cle": "socle_devance",
         "dit": "Une ou plusieurs fonctions devancent GOVERN.",
         "porte_sur": "Le cadre place GOVERN au-dessus des trois autres. Le "
                      "travail de MEASURE et de MANAGE est réel, mais "
                      "personne ne le reprend : c'est une couverture sans "
                      "gouvernance, pas une couverture moindre.",
         "ou": "nist · profil"},
    ],
}


# ══════════════════════════════════════════════════════════════════════════
#  LIRE CE QUE CHAQUE MODULE REND DÉJÀ
# ══════════════════════════════════════════════════════════════════════════
#
# CE MODULE NE RÉÉVALUE RIEN. Chaque `_lire_*` prend l'évaluation rendue par
# le module de la norme et en tire deux choses : le taux de chacune de ses
# parts, et les verrous engagés. Rien d'autre. Si on recalculait ici, il y
# aurait DEUX vérités sur la même norme — et c'est très exactement le défaut
# mesuré sur l'écran (voir RECALAGE en fin de fichier) : l'audit IA Act y
# affichait deux pourcentages différents selon la vue qui le regardait.

def _pc(numerateur, denominateur):
    """Un pourcentage entier, ou None quand il n'y a rien à diviser.

    ZÉRO SUR ZÉRO N'EST PAS ZÉRO POUR CENT. Un référentiel dont aucune ligne
    ne s'applique n'est pas « à 0 % » : il est sans objet, et la distinction
    décide de l'affichage comme du plan."""
    if not denominateur:
        return None
    return int(round(100.0 * numerateur / denominateur))


def _lire_iso42001(ev, dec=None):
    if not ev or not ev.get("ok"):
        return None, []
    mat, soa = ev.get("maturite") or {}, ev.get("applicabilite") or {}
    parts = {
        "articles": mat.get("taux"),
        "propres_ia": (mat.get("propres_a_l_ia") or {}).get("taux"),
        "mesures": soa.get("taux_mise_en_oeuvre"),
    }
    verrous = [] if soa.get("recevable") else ["soa_irrecevable"]
    return parts, verrous


def _lire_iso27001(ev, dec=None):
    if not ev or not ev.get("ok"):
        return None, []
    mat, soa = ev.get("maturite") or {}, ev.get("applicabilite") or {}
    risque = ev.get("risque") or {}
    # L'APPRÉCIATION DU RISQUE SE MESURE PAR CE QU'ELLE A COTÉ, pas par le
    # fait qu'elle ait tourné : `apprecier` rend ok=True sur zéro risque, et
    # un SMSI sans risque coté n'a rien sur quoi s'appuyer. On compte donc les
    # risques RÉELLEMENT cotés sur ceux qui ont été portés.
    parts = {
        "risque": _pc(risque.get("cotes") or 0, risque.get("total") or 0),
        "articles": mat.get("taux"),
        "mesures": soa.get("taux_mise_en_oeuvre"),
    }
    verrous = []
    if ev.get("etape") == "perimetre_absent":
        verrous.append("perimetre_absent")
    if not soa.get("recevable"):
        verrous.append("soa_irrecevable")
    return parts, verrous


def _lire_nis2(ev, dec=None):
    if not ev or not ev.get("ok"):
        return None, []
    parts = {
        "mesures": (ev.get("mesures") or {}).get("taux"),
        "gouvernance": (ev.get("gouvernance") or {}).get("taux"),
    }
    # LE VERROU NE TOMBE PAS SUR « PAS DE STATUT » MAIS SUR UN STATUT QUI NE
    # DIT RIEN. `qualifier` rend toujours un statut ; celui qui bloque est
    # « indetermine » — on ne sait pas quel régime s'applique, donc on ne sait
    # pas à quel niveau d'exigence les dix mesures doivent être tenues.
    q = ev.get("qualification") or {}
    statut = q.get("statut") or {}
    verrous = ["non_qualifie"] if (q.get("indetermine")
                                   or not statut.get("cle")) else []
    return parts, verrous


def _lire_cra(ev, dec=None):
    if not ev or not ev.get("ok"):
        return None, []
    parts = {}
    for p in (ev.get("ecarts") or {}).get("parties") or []:
        lignes = p.get("lignes") or []
        # UNE EXIGENCE PARTIELLE N'EST PAS UNE EXIGENCE TENUE, et elle n'est
        # pas rien non plus : elle vaut une moitié, comme l'audit IA Act
        # compte les siennes. Compter « partiel » pour zéro découragerait de
        # le déclarer ; le compter pour un serait le mensonge que le module
        # CRA refuse déjà en tête de son analyse d'écart.
        tenues = sum(1.0 if l.get("etat") == "conforme"
                     else 0.5 if l.get("etat") == "partiel" else 0.0
                     for l in lignes)
        retenues = [l for l in lignes if l.get("etat") != "sans_objet"]
        cle = "produit" if p.get("partie") == "I" else "vulnerabilites"
        parts[cle] = _pc(tenues, len(retenues))
    # LE MODULE CRA SUPPOSE « FABRICANT » QUAND RIEN N'EST DIT, et c'est le
    # bon défaut — c'est le rôle le plus chargé, donc celui qui ne fait rien
    # manquer. Mais son évaluation porte alors une hypothèse qu'elle ne
    # signale pas : on la lit sur la DÉCLARATION, pas sur le résultat. Une
    # première version regardait `role.cle`, toujours rempli : la réserve
    # n'est jamais tombée, et l'écran promettait un taux sans dire contre
    # quoi il était calculé.
    signaux = [] if (dec or {}).get("role") else ["role_absent"]
    return parts, signaux


def _lire_nist(ev, dec=None):
    if not ev or not ev.get("ok"):
        return None, []
    # LE TAUX D'UNE FONCTION EST SA NOTE SUR L'ÉCHELLE DU CADRE, ramenée en
    # pourcentage : `prouve` vaut 3, et c'est le haut de l'échelle. Compter
    # « renseigné / total » ferait passer une fonction entièrement ABSENTE
    # pour une fonction à 100 %, dès lors qu'on a pris la peine de déclarer
    # qu'elle était absente.
    parts = {}
    for p in ev.get("profils") or []:
        cle = (p.get("fonction") or "").lower()
        note, sur = p.get("note"), p.get("sur")
        total = p.get("categories") or 0
        # LA NOTE DU MODULE EST UNE MOYENNE SUR LES SEULES CATÉGORIES
        # RENSEIGNÉES, et c'est juste pour ce qu'elle mesure : le niveau de ce
        # qu'on a regardé. Ce n'est PAS une couverture. Mesuré, une seule
        # catégorie sur six déclarée « prouvé » rendait 100 % — le cadre était
        # réputé couvert à 100 % alors que cinq sixièmes n'avaient jamais été
        # ouverts. Or la nature déclarée de cette norme dit que 100 % veut
        # dire « CHAQUE point porte un état ». On étale donc la note sur
        # TOUTES les catégories : une catégorie muette compte comme absente,
        # ce qu'elle est.
        renseignees = p.get("renseignees") or 0
        sans_objet = len(p.get("sans_objet") or ())
        portees = total - sans_objet
        parts[cle] = (None if note is None or not sur or not portees
                      else int(round(100.0 * note * renseignees / (sur * portees))))
    verrous = ["socle_devance"] if ev.get("devancent_le_socle") else []
    return parts, verrous


def _lire_owasp(ev, dec=None):
    if not ev or not ev.get("ok"):
        return None, []
    lignes = ev.get("lignes") or []
    retenus = [l for l in lignes if l.get("traite") is not None]
    traites = [l for l in retenus if l.get("traite")]
    return {"risques": _pc(len(traites), len(retenus))}, []


def _lire_ia_act(ev, dec=None):
    """L'audit IA Act, compté comme l'écran le compte : un point partiel vaut
    une moitié. La règle qui garde ce demi-point est écrite plus bas."""
    if not ev or not ev.get("ok"):
        return None, []
    parts = {}
    for prio in ("p1", "p2"):
        pts = [p for p in (ev.get("points") or []) if p.get("prio") == prio]
        retenus = [p for p in pts if p.get("etat") != "sans_objet"]
        acquis = sum(1.0 if p.get("etat") == "tenu"
                     else 0.5 if p.get("etat") == "partiel" else 0.0
                     for p in retenus)
        parts[prio] = _pc(acquis, len(retenus))
    return parts, []


def _lire_rgpd(ev, dec=None):
    if not ev or not ev.get("ok"):
        return None, []
    return {c["cle"]: (ev.get("briques") or {}).get(c["cle"])
            for c in COMPOSITIONS["rgpd"]}, []


def _lire_dora(ev, dec=None):
    """Le cadre et les contrats, tels que les quatre moteurs les rendent.

    LE TAUX DES CONTRATS EST CELUI DU PIRE, ET IL VIENT DÉJÀ COMME TEL. Le
    recomposer en moyenne ici ferait disparaître le contrat vide qui est
    précisément celui que l'autorité ouvrira.
    """
    if not ev or not ev.get("ok"):
        return None, []
    # PERMANENTE : ce taux ne couvre ni la chaîne de notification, ni les
    # tests, ni le registre d'informations. Le dire toujours, parce que le
    # nombre, lui, s'affiche toujours.
    signaux = ["hors_taux"]
    if not ev.get("mesurable"):
        signaux.append("regime_absent")
    r = ev.get("risque") or {}
    cadre = r.get("taux") if r.get("ok") else None
    contrats = ev.get("taux_contrats")
    return ({"cadre": int(round(cadre)) if cadre is not None else None,
             "tiers": int(round(contrats)) if contrats is not None else None},
            signaux)


def _lire_nist_800_53(ev, dec=None):
    """Les cinq groupes du catalogue, déjà étalés par le moteur.

    ON NE RECALCULE RIEN ICI. Le moteur étale chaque groupe sur TOUTES ses
    familles — une famille muette compte comme absente — et retire du
    dénominateur les seules familles écartées avec un motif. Refaire ce
    calcul ici, c'est garantir qu'un jour les deux divergeront."""
    if not ev or not ev.get("ok"):
        return None, []
    # LES DEUX RÉSERVES SONT PERMANENTES, PAS CONDITIONNELLES. Le millésime
    # et l'absence de certification ne dépendent pas des réponses : elles
    # valent pour toute lecture de ce taux, et se disent donc toujours.
    return ({p["groupe"]: p.get("taux") for p in ev.get("profils") or []},
            ["millesime", "non_certifiable"])


def _lire_nist_800_82(ev, dec=None):
    """Les dix axes industriels, regroupés en trois parts.

    LA NOTE RETENUE, PAS LA NOTE DÉCLARÉE. Le moteur plafonne chaque axe par
    la plus faible des familles 800-53 qu'il taille : c'est `note_retenue`
    qu'on agrège, sans quoi un axe déclaré au-dessus de son socle gonflerait
    le taux exactement là où le module vient de signaler un défaut."""
    if not ev or not ev.get("ok"):
        return None, []
    import nist_800_82 as _ot
    parts = {}
    for part, axes in PARTS_800_82.items():
        retenus = [p for p in ev.get("profils") or []
                   if p["axe"] in axes and p.get("etat") != "sans_objet"]
        if not retenus:
            parts[part] = None
            continue
        acquis = sum(p.get("note_retenue") or 0.0 for p in retenus)
        parts[part] = _pc(acquis, _ot.NOTE_MAX * len(retenus))
    # PERMANENTES ELLES AUSSI : ce taux mesure une surcharge plafonnée par
    # son socle, contre un millésime qui n'est plus le dernier. Les deux
    # changent le sens du nombre, quelles que soient les réponses.
    return parts, ["surcharge", "millesime"]


#: QUEL AXE COMPTE DANS QUELLE PART. Écrit ici une seule fois ; la garde
#: vérifie que les dix axes du moteur y figurent, et une seule fois chacun.
PARTS_800_82 = {
    "socle_ot":     ("surete", "disponibilite", "reprise"),
    "architecture": ("segmentation", "flux", "redondance"),
    "conduite":     ("authentification", "surveillance", "contraintes",
                     "metier"),
}


LECTEURS = {
    "iso42001": _lire_iso42001, "iso27001": _lire_iso27001,
    "nis2": _lire_nis2, "cra": _lire_cra, "nist_ai_rmf": _lire_nist,
    "owasp_llm": _lire_owasp, "ia_act": _lire_ia_act, "rgpd": _lire_rgpd,
    "nist_800_53": _lire_nist_800_53, "nist_800_82": _lire_nist_800_82,
    "dora": _lire_dora,
}


# ══════════════════════════════════════════════════════════════════════════
#  LE TAUX : COMPOSER, PUIS PLAFONNER
# ══════════════════════════════════════════════════════════════════════════

def taux_norme(cle, evaluation, declaration=None):
    """Le taux d'une norme, ses parts, et ce qui le plafonne.

    TROIS NOMBRES SORTENT D'ICI, ET LES TROIS SONT NÉCESSAIRES :
      `brut`    — ce que vaut le travail fait, parts pondérées ;
      `plafond` — ce que les verrous laissent atteindre ;
      `taux`    — le plus petit des deux, parce qu'un verrou n'efface pas le
                  travail mais interdit de s'en prévaloir au-delà.

    N'en montrer qu'un serait faux dans les deux sens : le brut seul fait
    croire la porte ouverte, le plafond seul efface ce qui est fait.
    """
    norme = NORMES_PAR_CLE.get(cle)
    if not norme:
        return {"ok": False, "motif": "norme_inconnue"}
    nature = NATURES[norme["nature"]]

    if norme["nature"] == "sans_instrument":
        return {"ok": True, "cle": cle, "nom": norme["nom"],
                "nature": norme["nature"], "nature_nom": nature["nom"],
                "taux": None, "brut": None, "plafond": None,
                "composants": [], "verrous": [], "reserves": [],
                "renseigne": False,
                "mesure": norme["mesure"], "panneau": norme["panneau"],
                "taux_dit": nature["taux_dit"],
                "dit": "Aucun instrument de mesure ici. Le taux est absent, "
                       "pas nul — et l'absence de mesure ne dit rien de "
                       "l'état réel."}

    lire = LECTEURS.get(cle)
    parts, signaux = (lire(evaluation, declaration) if lire else (None, []))
    composition = COMPOSITIONS[cle]

    if parts is None:
        return {"ok": True, "cle": cle, "nom": norme["nom"],
                "nature": norme["nature"], "nature_nom": nature["nom"],
                "taux": None, "brut": None, "plafond": None,
                "composants": [dict(c, taux=None, renseigne=False)
                               for c in composition],
                "verrous": [], "reserves": [], "renseigne": False,
                "mesure": norme["mesure"], "panneau": norme["panneau"],
                "taux_dit": nature["taux_dit"],
                "dit": "Rien n'a encore été évalué sur cette norme."}

    composants, poids_total, acquis = [], 0, 0.0
    for c in composition:
        t = parts.get(c["cle"])
        composants.append(dict(c, taux=t, renseigne=t is not None))
        # UNE PART NON RENSEIGNÉE COMPTE POUR ZÉRO, ET PAS POUR RIEN. La
        # sortir du dénominateur ferait monter le taux à mesure qu'on
        # renseigne MOINS de choses : le pire réglage possible, puisqu'il
        # récompense l'ignorance.
        poids_total += c["poids"]
        acquis += c["poids"] * (t or 0)
    brut = int(round(acquis / poids_total)) if poids_total else None

    verrous, reserves, plafond = [], [], 100
    for r in RESERVES.get(cle, []):
        if r["cle"] in signaux:
            reserves.append(dict(r))
    if signaux:
        bloques = set()
        for v in VERROUS.get(cle, []):
            if v["cle"] not in signaux:
                continue
            verrous.append(dict(v))
            bloques |= set(v["bloque"])
        libres = sum(c["poids"] for c in composition
                     if c["cle"] not in bloques)
        plafond = int(round(100.0 * libres / poids_total)) if poids_total else 0

    taux = min(brut, plafond) if brut is not None else None
    renseigne = any(c["renseigne"] for c in composants)

    if not renseigne:
        dit = "Rien n'a encore été évalué sur cette norme."
    elif verrous:
        dit = ("%d %% du travail est fait ; les verrous ci-dessous "
               "interdisent d'aller au-delà de %d %%." % (brut, plafond))
    elif taux == 100:
        dit = nature["cent_veut_dire"]
    else:
        dit = "Aucun verrou. Le taux monte en refermant les écarts."

    return {"ok": True, "cle": cle, "nom": norme["nom"], "texte": norme["texte"],
            "nature": norme["nature"], "nature_nom": nature["nom"],
            "taux": taux, "brut": brut, "plafond": plafond,
            "plafonne": taux is not None and brut is not None and taux < brut,
            "composants": composants, "verrous": verrous,
            "reserves": reserves,
            "renseigne": renseigne, "mesure": norme["mesure"],
            "panneau": norme["panneau"], "taux_dit": nature["taux_dit"],
            "cent_veut_dire": nature["cent_veut_dire"],
            "cent_ne_veut_pas_dire": nature["cent_ne_veut_pas_dire"],
            "dit": dit}


def consolide(taux_par_norme):
    """CE QUI COMMANDE, ET LA MOYENNE — dans cet ordre, et jamais l'inverse.

    L'écran de ce dépôt portait déjà un indice à trois cadres, et son propre
    texte d'aide disait : « traitez d'abord la composante la plus basse, c'est
    elle qui tire l'indice vers le bas ». C'était faux de l'indice affiché :
    une MOYENNE ne se laisse pas tirer vers le bas par sa composante la plus
    basse, elle la dilue. Deux cadres à 90 % et un à 30 % rendaient 70 %, et
    le 30 % disparaissait de la vue.

    Ce qui commande est donc le MINIMUM des taux mesurés, et il est nommé
    comme tel. La moyenne reste rendue, parce qu'un comité la calculera de
    toute façon, et qu'il vaut mieux la poser avec son avertissement que la
    laisser reconstituer sans.
    """
    mesures = [t for t in taux_par_norme
               if t.get("taux") is not None and t.get("renseigne")]
    if not mesures:
        return {"commande": None, "moyenne": None, "qui": None,
                "mesurees": 0, "sur": len(taux_par_norme),
                "dit": "Aucune norme n'a encore été évaluée."}
    pire = min(mesures, key=lambda t: t["taux"])
    moyenne = int(round(sum(t["taux"] for t in mesures) / float(len(mesures))))
    return {
        "commande": pire["taux"], "qui": pire["cle"], "qui_nom": pire["nom"],
        "moyenne": moyenne, "mesurees": len(mesures), "sur": len(taux_par_norme),
        "dit": "%d %% est le taux de %s, le plus bas des %d normes évaluées — "
               "c'est lui qui commande. La moyenne (%d %%) ne remplace pas "
               "cette lecture : elle dilue précisément ce qu'il faut traiter "
               "en premier." % (pire["taux"], pire["nom"], len(mesures), moyenne),
        # LE COMPTE SE DÉRIVE DE LA TABLE, IL NE SE RÉÉCRIT PAS. Cette
        # phrase disait « Neuf normes » alors que la grille en portait onze —
        # exactement le défaut que le titre de l'accueil avait déjà eu.
        "avertissement": "%d normes de natures différentes ne s'additionnent "
                         "pas. Une moyenne entre une obligation légale, une "
                         "norme certifiable et un cadre volontaire produit un "
                         "nombre qu'aucun auditeur, aucune autorité et aucun "
                         "assureur ne reconnaîtra." % NORMES_ANNONCEES,
    }


# ══════════════════════════════════════════════════════════════════════════
#  LES ÉCARTS — CE QUE CHAQUE MODULE NOMME DÉJÀ
# ══════════════════════════════════════════════════════════════════════════
#
# Un écart porte TOUJOURS le composant auquel il appartient : sans lui, on ne
# saurait pas ce que le refermer rapporte, et le plan annoncerait des gains
# qu'il ne peut pas tenir.

def _ec(composant, cle, nom, ou, article=None):
    return {"composant": composant, "cle": cle, "nom": nom, "ou": ou,
            "article": article}


def _ecarts_iso42001(ev, dec=None):
    if not ev or not ev.get("ok"):
        return []
    out = []
    mat = ev.get("maturite") or {}
    propres = set((mat.get("propres_a_l_ia") or {}).get("numeros") or ())
    for ch in mat.get("chapitres") or []:
        for ligne in ch.get("lignes") or []:
            if ligne.get("etat") in ("conforme", "sans_objet"):
                continue
            num = ligne.get("numero")
            comp = "propres_ia" if num in propres else "articles"
            out.append(_ec(comp, num, ligne.get("titre"),
                           "iso42001 · articles", "art. " + str(num)))
    for ligne in (ev.get("applicabilite") or {}).get("lignes") or []:
        if ligne.get("decision") != "retenue":
            continue
        # L'ÉTAT QUI COMPTE EST « conforme », PAS « oui ». Une première
        # version cherchait « oui » : aucune mesure réellement mise en œuvre
        # n'était reconnue, et le plan réclamait un travail déjà fait. Le
        # défaut ne s'est pas vu tant que le dossier d'essai n'a porté AUCUNE
        # mesure en œuvre — les deux côtés du calcul étaient faux de la même
        # façon, donc d'accord entre eux.
        if ligne.get("mise_en_oeuvre") in ("conforme", "sans_objet"):
            continue
        out.append(_ec("mesures", ligne.get("numero"), ligne.get("titre"),
                       "iso42001 · déclaration d'applicabilité",
                       ligne.get("numero")))
    return out


def _ecarts_iso27001(ev, dec=None):
    if not ev or not ev.get("ok"):
        return []
    out = []
    for ch in (ev.get("maturite") or {}).get("chapitres") or []:
        for ligne in ch.get("lignes") or []:
            if ligne.get("etat") in ("conforme", "sans_objet"):
                continue
            num = ligne.get("numero")
            out.append(_ec("articles", num, ligne.get("titre"),
                           "iso27001 · articles", "art. " + str(num)))
    for ligne in (ev.get("applicabilite") or {}).get("lignes") or []:
        if ligne.get("decision") != "retenue":
            continue
        # L'ÉTAT QUI COMPTE EST « conforme », PAS « oui ». Une première
        # version cherchait « oui » : aucune mesure réellement mise en œuvre
        # n'était reconnue, et le plan réclamait un travail déjà fait. Le
        # défaut ne s'est pas vu tant que le dossier d'essai n'a porté AUCUNE
        # mesure en œuvre — les deux côtés du calcul étaient faux de la même
        # façon, donc d'accord entre eux.
        if ligne.get("mise_en_oeuvre") in ("conforme", "sans_objet"):
            continue
        out.append(_ec("mesures", ligne.get("numero"), ligne.get("titre"),
                       "iso27001 · déclaration d'applicabilité",
                       ligne.get("numero")))
    return out


def _ecarts_nis2(ev, dec=None):
    if not ev or not ev.get("ok"):
        return []
    import nis2 as _n
    out = []
    for ligne in (ev.get("mesures") or {}).get("lignes") or []:
        if ligne.get("etat") in ("conforme", "sans_objet"):
            continue
        out.append(_ec("mesures", ligne.get("cle"), ligne.get("nom"),
                       "nis2 · mesures",
                       "art. 21 §2 (%s)" % ligne.get("cle")))
    manques = set((ev.get("gouvernance") or {}).get("manques") or ())
    for g in _n.GOUVERNANCE:
        if g["cle"] in manques:
            out.append(_ec("gouvernance", g["cle"], g["quoi"],
                           "nis2 · gouvernance", g["article"]))
    return out


def _ecarts_cra(ev, dec=None):
    if not ev or not ev.get("ok"):
        return []
    out = []
    for p in (ev.get("ecarts") or {}).get("parties") or []:
        comp = "produit" if p.get("partie") == "I" else "vulnerabilites"
        for ligne in p.get("lignes") or []:
            if ligne.get("etat") in ("conforme", "sans_objet"):
                continue
            out.append(_ec(comp, ligne.get("cle"), ligne.get("nom"),
                           "cra · annexe I partie %s" % p.get("partie"),
                           "annexe I, partie %s" % p.get("partie")))
    return out


def _ecarts_nist(ev, dec=None):
    """LE MODULE NIST NE REND QUE DES AGRÉGATS PAR FONCTION — note, nombre de
    catégories renseignées — et aucun détail par catégorie. Les écarts se
    lisent donc sur la DÉCLARATION elle-même, confrontée au référentiel. C'est
    la seule norme des neuf dans ce cas, et la seule raison pour laquelle ces
    fonctions reçoivent la déclaration en plus de l'évaluation."""
    if not ev or not ev.get("ok"):
        return []
    import nist_ai_rmf as _k
    etats = dec or {}
    out = []
    for cat in _k.CATEGORIES:
        e = etats.get(cat["cle"])
        if e in ("prouve", "sans_objet"):
            continue
        out.append(_ec((cat["fonction"] or "").lower(), cat["cle"],
                       cat.get("nom"), "nist · " + cat["fonction"],
                       cat["cle"]))
    return out


def _ecarts_owasp(ev, dec=None):
    if not ev or not ev.get("ok"):
        return []
    return [_ec("risques", l.get("cle"), l.get("nom"), "owasp · top 10",
                l.get("cle"))
            for l in ev.get("lignes") or []
            if l.get("traite") is not True and l.get("etat") != "sans_objet"]


def _ecarts_ia_act(ev, dec=None):
    if not ev or not ev.get("ok"):
        return []
    return [_ec(p["prio"], p["cle"], p["titre"],
                "ia act · audit — %s" % p["section"], p["article"])
            for p in ev.get("points") or []
            if p.get("etat") not in ("tenu", "sans_objet")]


def _ecarts_rgpd(ev, dec=None):
    """LE RGPD NE NOMME PAS SES LIGNES ICI — l'écran rend quatre pourcentages
    et rien de plus fin. On ne fabrique donc pas d'écarts imaginaires : une
    brique incomplète devient UNE action, qui renvoie à l'écran où elle se
    remplit. Inventer un détail qu'on n'a pas serait pire que de renvoyer."""
    if not ev or not ev.get("ok"):
        return []
    briques = ev.get("briques") or {}
    return [_ec(c["cle"], c["cle"], c["nom"], "rgpd · " + c["nom"], None)
            for c in COMPOSITIONS["rgpd"]
            if (briques.get(c["cle"]) or 0) < 100]


def _ecarts_nist_800_53(ev, dec=None):
    """Une famille qui n'est ni prouvée ni écartée est un écart.

    L'ÉCART SE LIT SUR L'ÉVALUATION, PAS SUR LA DÉCLARATION. Le moteur rend
    le détail famille par famille avec son état : le plan n'a donc pas
    besoin de la déclaration brute, et ne risque pas de diverger d'elle."""
    if not ev or not ev.get("ok"):
        return []
    out = []
    for prof in ev.get("profils") or []:
        for f in prof.get("detail") or []:
            if f.get("etat") in ("prouve", "sans_objet"):
                continue
            out.append(_ec(prof["groupe"], f["famille"],
                           "%s — %s" % (f["famille"], f["titre"]),
                           "nist53 · " + prof["nom"], f["famille"]))
    return out


def _ecarts_nist_800_82(ev, dec=None):
    """Un axe non prouvé est un écart — et un axe qui DÉPASSE son socle en
    est un autre, d'une nature différente.

    LES DEUX SE DISTINGUENT AU PLAN, et c'est ce qui rend le plan
    utilisable : combler le premier se fait dans l'atelier industriel ;
    combler le second demande d'abord de reprendre la famille 800-53 qui
    manque en dessous. Les confondre ferait écrire une action impossible."""
    if not ev or not ev.get("ok"):
        return []
    out = []
    for p in ev.get("profils") or []:
        if p.get("etat") == "sans_objet":
            continue
        if p.get("depasse_le_socle"):
            manquantes = [f["cle"] for f in p.get("familles") or []
                          if f.get("etat_800_53") in (None, "absent")]
            out.append(_ec("socle_manquant", p["axe"],
                           "%s — reprendre d'abord %s dans 800-53"
                           % (p["nom"], ", ".join(manquantes) or "le socle"),
                           "nist82 · socle", p["axe"]))
            continue
        if p.get("etat") != "prouve":
            out.append(_ec(_part_de_l_axe(p["axe"]), p["axe"], p["nom"],
                           "nist82 · surcharge", p["axe"]))
    return out


def _ecarts_dora(ev, dec=None):
    """Les articles du régime qui ne sont pas tenus, et les clauses absentes.

    CHAQUE CONTRAT PORTE SON RANG, parce que deux contrats n'ont pas le même
    poids : une clause manquante sur un contrat qui soutient une fonction
    critique se règle avant la même clause sur un contrat ordinaire.
    """
    if not ev or not ev.get("ok"):
        return []
    out = []
    er = ev.get("ecarts_risque") or {}
    if er.get("ok"):
        for x in er.get("ecarts") or []:
            out.append(_ec("cadre", "art_%d" % x["article"], x["titre"],
                           "dora · cadre de gestion du risque",
                           "RD (UE) 2024/1774, art. %d" % x["article"]))
    for rang, examen in enumerate(ev.get("contrats") or [], start=1):
        if not examen.get("ok"):
            continue
        critique = examen.get("fonction_critique")
        for cl in examen.get("manquantes") or []:
            out.append(_ec(
                "tiers",
                "contrat%d_%s_%s" % (rang, cl["serie"], cl["lettre"]),
                "Contrat %d%s — %s" % (rang,
                                       " (fonction critique)" if critique
                                       else "", cl["quoi"]),
                "dora · contrats de prestation TIC",
                cl["article"]))
    return out


def _part_de_l_axe(axe):
    for part, axes in PARTS_800_82.items():
        if axe in axes:
            return part
    return "conduite"


ECARTEURS = {
    "dora": _ecarts_dora,
    "iso42001": _ecarts_iso42001, "iso27001": _ecarts_iso27001,
    "nis2": _ecarts_nis2, "cra": _ecarts_cra, "nist_ai_rmf": _ecarts_nist,
    "owasp_llm": _ecarts_owasp, "ia_act": _ecarts_ia_act, "rgpd": _ecarts_rgpd,
    "nist_800_53": _ecarts_nist_800_53, "nist_800_82": _ecarts_nist_800_82,
}


# ══════════════════════════════════════════════════════════════════════════
#  LE PLAN — TROIS RANGS, ET UN GAIN QUI SE VÉRIFIE
# ══════════════════════════════════════════════════════════════════════════
#
# RANG 1, LES VERROUS. Ils plafonnent : tant qu'ils tiennent, tout le travail
# des autres rangs bute sur le même plafond. Les traiter en premier n'est pas
# une préférence de méthode, c'est de l'arithmétique.
#
# RANG 2, CE QUI SERT PLUSIEURS NORMES. C'est le seul vrai bénéfice à tenir
# neuf référentiels au même endroit : la mesure A.5.1 de l'annexe A sert la
# 27001 ET la mesure (a) de l'article 21 §2 de NIS 2. Ces rapprochements ne
# sont pas inventés ici — ils sont DÉCLARÉS dans les modules concernés
# (`iso27001.NIS2_VERS_ANNEXE_A`, `owasp_llm.pont_42001`), et une règle vérifie
# qu'aucune action n'en invente un.
#
# RANG 3, LE PROPRE À CHAQUE NORME. Le reste, groupé par norme et par
# composant, pour que le plan reste lisible au lieu de lister trois cents
# lignes.
#
# LE GAIN EST MESURÉ, PAS ANNONCÉ. Chaque action rejoue le calcul du taux
# comme si ses écarts étaient refermés, et rend la différence. Une règle
# applique ensuite TOUTES les actions du plan et vérifie qu'on atteint bien le
# total promis : un plan dont les gains ne s'additionnent pas jusqu'au bout
# est un plan qui ment sur sa destination.

def _recomposer(etat, ecarts_fermes):
    """Le taux qu'aurait cette norme si ces écarts-là étaient refermés.

    On ne touche NI à la pondération NI au plafond : refermer un écart ne
    lève pas un verrou (c'est le rang 1 qui s'en charge), et le plafond reste
    donc celui d'aujourd'hui. Compter autrement ferait miroiter des gains que
    la porte fermée interdit d'encaisser.
    """
    if not etat.get("ok") or etat.get("taux") is None:
        return etat.get("taux")
    par_comp = {}
    for e in ecarts_fermes:
        par_comp.setdefault(e["composant"], 0)
        par_comp[e["composant"]] += 1
    total_par_comp = etat.get("_ecarts_par_composant") or {}
    poids_total, acquis = 0, 0.0
    for c in etat["composants"]:
        t = c["taux"] or 0
        n_total = total_par_comp.get(c["cle"], 0)
        n_ferme = par_comp.get(c["cle"], 0)
        if n_total and n_ferme:
            # CHAQUE ÉCART D'UN COMPOSANT VAUT LA MÊME PART DE CE QUI MANQUE :
            # refermer la moitié des écarts ramène la moitié du chemin.
            t = t + (100 - t) * (min(n_ferme, n_total) / float(n_total))
        poids_total += c["poids"]
        acquis += c["poids"] * t
    brut = int(round(acquis / poids_total)) if poids_total else None
    return min(brut, etat.get("plafond", 100)) if brut is not None else None


def _action(rang, cle, quoi, pourquoi, ou, normes, gains, ecarts, **extra):
    a = {"rang": rang, "cle": cle, "quoi": quoi, "pourquoi": pourquoi,
         "ou": ou, "normes": normes, "gains": gains,
         "gain_total": sum(g["gain"] for g in gains),
         "ecarts": [e["cle"] for e in ecarts], "combien": len(ecarts)}
    a.update(extra)
    return a


def _ponts_multi_normes(etats, ecarts):
    """Les rapprochements DÉCLARÉS, et eux seuls.

    Deux ponts existent dans ce dépôt et sont déjà gardés par leurs propres
    recettes :
      `iso27001.NIS2_VERS_ANNEXE_A` — chacune des dix mesures de l'article 21
      §2 de NIS 2 vers les mesures de l'annexe A 27001 qui la servent ;
      `owasp_llm.pont_42001()`      — chacun des dix risques LLM vers les
      mesures de l'annexe A 42001 qui le rencontrent.

    On n'en invente aucun autre. Un pont inventé ici serait une promesse que
    ni l'auditeur 27001 ni l'autorité NIS 2 ne reconnaîtraient.
    """
    import iso27001 as _i27
    import owasp_llm as _ow
    liens = []
    for cle_nis, nom_nis, mesures in _i27.NIS2_VERS_ANNEXE_A:
        liens.append({"cle": "nis2_" + cle_nis,
                      "de": ("nis2", cle_nis, nom_nis),
                      "vers": ("iso27001", list(mesures)),
                      "quoi": "Mettre en place %s" % ", ".join(mesures),
                      "pourquoi": "Ces mesures de l'annexe A 27001 servent la "
                                  "mesure « %s » de l'article 21 §2. Un SMSI "
                                  "certifié est le socle de preuves le plus "
                                  "direct devant une autorité NIS 2."
                                  % nom_nis,
                      "ou": "iso27001-soa"})
    pont = _ow.pont_42001()
    for cle_llm, mesures in (pont.get("rencontres") or {}).items():
        if not mesures:
            continue
        liens.append({"cle": "owasp_" + cle_llm,
                      "de": ("owasp_llm", cle_llm, cle_llm),
                      "vers": ("iso42001", list(mesures)),
                      "quoi": "Mettre en place %s" % ", ".join(mesures),
                      "pourquoi": "Ces mesures de l'annexe A 42001 "
                                  "rencontrent le risque %s du Top 10 LLM."
                                  % cle_llm,
                      "ou": "iso42001-soa"})
    return liens


def plan(etats, ecarts_par_norme, plafond_actions=24):
    """Le plan d'action, en trois rangs, gains mesurés CUMULATIVEMENT.

    POURQUOI LES GAINS SE CALCULENT DANS L'ORDRE, ET PAS CHACUN DANS SON COIN.
    Ils ne sont pas indépendants : deux actions qui touchent le même composant
    se partagent le même chemin restant. Mesuré sur un dossier réel, des gains
    calculés séparément puis additionnés menaient le Top 10 OWASP à 102 % — le
    plan promettait plus qu'il n'existe. On les calcule donc À LA SUITE, sur
    l'état laissé par les actions précédentes : la somme se télescope alors
    exactement jusqu'au plafond, et l'arrondi ne s'accumule plus.
    """
    par_cle = {e["cle"]: e for e in etats}
    brouillons = []

    # ── RANG 1 : LEVER LES VERROUS ──────────────────────────────────────
    for e in etats:
        for v in e.get("verrous") or []:
            immediat = ((e["brut"] - e["taux"])
                        if (e.get("brut") is not None
                            and e.get("taux") is not None) else 0)
            plafond_gagne = 100 - (e.get("plafond") or 100)
            brouillons.append({
                "rang": 1, "cle": "%s:%s" % (e["cle"], v["cle"]),
                "quoi": v["dit"].split(".")[0] + ".",
                "pourquoi": "Ce verrou plafonne %s à %d %%. Tant qu'il tient, "
                            "tout autre travail sur cette norme bute sur le "
                            "même plafond — et %s"
                            % (e["nom"], e["plafond"],
                               v["dit"][0].lower() + v["dit"][1:]),
                "ou": v["ou"], "normes": [e["cle"]], "ferme": {},
                "leve_un_verrou": True, "verrou": v["cle"],
                "plafond_gagne": plafond_gagne, "immediat": immediat,
                "tri": -plafond_gagne})

    # ── RANG 1 bis : LEVER LES RÉSERVES ─────────────────────────────────
    #
    # ELLES NE RAPPORTENT AUCUN POINT, ET ELLES SONT AU PREMIER RANG. Une
    # réserve ne plafonne rien : elle dit que le taux est calculé contre une
    # hypothèse non confirmée. Confirmer l'hypothèse coûte une demi-journée
    # et décide de ce que TOUT le reste veut dire — c'est le meilleur rapport
    # du plan, et il ne se voit pas sur un classement par points.
    for e in etats:
        for r in e.get("reserves") or []:
            brouillons.append({
                "rang": 1, "cle": "%s:%s" % (e["cle"], r["cle"]),
                "quoi": r["dit"],
                "pourquoi": r["porte_sur"] + " Lever cette réserve ne change "
                            "aucun point : elle décide de ce que les points "
                            "veulent dire.",
                "ou": r["ou"], "normes": [e["cle"]], "ferme": {},
                "leve_une_reserve": True, "reserve": r["cle"],
                "tri": 0})

    # ── RANG 2 : CE QUI SERT PLUSIEURS NORMES ───────────────────────────
    for lien in _ponts_multi_normes(etats, ecarts_par_norme):
        norme_de, cle_de, nom_de = lien["de"]
        norme_vers, mesures = lien["vers"]
        ferme = {}
        ouverts_de = [x for x in ecarts_par_norme.get(norme_de, [])
                      if x["cle"] == cle_de]
        ouverts_vers = [x for x in ecarts_par_norme.get(norme_vers, [])
                        if x["cle"] in mesures]
        if ouverts_de:
            ferme[norme_de] = ouverts_de
        if ouverts_vers:
            ferme[norme_vers] = ouverts_vers
        if not ferme:
            continue
        # LE TRI DU RANG 2 SE FAIT SUR UNE ESTIMATION INDÉPENDANTE — on n'a
        # pas encore l'ordre, donc pas encore les gains cumulés. L'estimation
        # ne sert qu'à ordonner ; les gains affichés, eux, seront les vrais.
        estime = 0
        for norme, fermes in ferme.items():
            et = par_cle.get(norme)
            if et and et.get("taux") is not None:
                estime += (_recomposer(et, fermes) or 0) - et["taux"]
        brouillons.append({
            "rang": 2, "cle": lien["cle"], "quoi": lien["quoi"],
            "pourquoi": lien["pourquoi"], "ou": lien["ou"],
            "normes": sorted(ferme), "ferme": ferme, "pont": True,
            "tri": -estime})

    # ── RANG 3 : LE PROPRE À CHAQUE NORME, GROUPÉ PAR COMPOSANT ─────────
    deja = {x["cle"] for b in brouillons for lst in b["ferme"].values()
            for x in lst}
    for e in etats:
        if e.get("taux") is None:
            continue
        restants = [x for x in ecarts_par_norme.get(e["cle"], [])
                    if x["cle"] not in deja]
        par_comp = {}
        for x in restants:
            par_comp.setdefault(x["composant"], []).append(x)
        for comp in e["composants"]:
            groupe = par_comp.get(comp["cle"])
            if not groupe:
                continue
            estime = (_recomposer(e, groupe) or 0) - e["taux"]
            brouillons.append({
                "rang": 3, "cle": "%s:%s" % (e["cle"], comp["cle"]),
                "quoi": "Refermer les %d écart(s) de « %s »"
                        % (len(groupe), comp["nom"]),
                "pourquoi": comp["pourquoi"][0].upper()
                            + comp["pourquoi"][1:] + ".",
                "ou": e["panneau"], "normes": [e["cle"]],
                "ferme": {e["cle"]: groupe}, "composant": comp["cle"],
                "detail": [{"cle": x["cle"], "nom": x["nom"],
                            "article": x["article"]} for x in groupe[:8]],
                "detail_tronque": max(0, len(groupe) - 8),
                "tri": -estime})

    # L'ORDRE : le rang d'abord, l'apport ensuite. Un plan trié par le seul
    # apport ferait remonter une action de rang 3 devant un verrou, et le
    # lecteur commencerait par ce qui ne peut pas encore rapporter.
    brouillons.sort(key=lambda b: (b["rang"], b["tri"], b["cle"]))

    # ── LES GAINS, DANS CET ORDRE ET PAS UN AUTRE ───────────────────────
    cumul = {e["cle"]: [] for e in etats}
    courant = {e["cle"]: e.get("taux") for e in etats}
    actions = []
    for b in brouillons:
        gains = []
        if b.get("leve_une_reserve"):
            e = par_cle[b["normes"][0]]
            gains.append({"norme": e["cle"], "nom": e["nom"], "gain": 0,
                          "de": e["taux"], "a": e["taux"],
                          "dit": "Aucun point : lever une réserve ne déplace "
                                 "pas le taux, elle en fixe le sens."})
        elif b.get("leve_un_verrou"):
            e = par_cle[b["normes"][0]]
            gains.append({
                "norme": e["cle"], "nom": e["nom"], "gain": b["immediat"],
                "de": e["taux"], "a": e["brut"],
                "plafond_de": e.get("plafond"), "plafond_a": 100,
                "dit": ("Débloque %d point(s) de plafond ; %s"
                        % (b["plafond_gagne"],
                           "rien d'immédiat tant que les écarts restent "
                           "ouverts." if not b["immediat"]
                           else "et %d point(s) tout de suite."
                                % b["immediat"]))})
        else:
            for norme, fermes in sorted(b["ferme"].items()):
                et = par_cle.get(norme)
                if not et or et.get("taux") is None:
                    continue
                cumul[norme] = cumul[norme] + fermes
                apres = _recomposer(et, cumul[norme])
                g = (apres or 0) - (courant[norme] or 0)
                gains.append({"norme": norme, "nom": et["nom"], "gain": g,
                              "de": courant[norme], "a": apres,
                              "confisque": bool(not g and et.get("plafonne"))})
                courant[norme] = apres
        a = {k: v for k, v in b.items() if k not in ("ferme", "tri",
                                                      "immediat")}
        a["gains"] = gains
        a["gain_total"] = sum(g["gain"] for g in gains)
        a["ecarts"] = [x["cle"] for lst in b["ferme"].values() for x in lst]
        a["combien"] = len(a["ecarts"])
        actions.append(a)

    tronque = max(0, len(actions) - plafond_actions)
    return {"actions": actions[:plafond_actions], "tronquees": tronque,
            "total": len(actions),
            "atteint": {c: courant[c] for c in courant
                        if courant[c] is not None},
            "dit": ("%d action(s), du verrou au détail."
                    % len(actions)) + (
                       " Les %d dernières ne sont pas affichées : elles "
                       "rapportent le moins, et rien tant que les "
                       "précédentes tiennent." % tronque if tronque else "")}



# ══════════════════════════════════════════════════════════════════════════
#  CE QUE LE PLAN NE PEUT PAS FAIRE
# ══════════════════════════════════════════════════════════════════════════
#
# LA MOITIÉ QU'ON NE MONTRE JAMAIS, et celle qui fait la différence en comité.
# Un plan qui promet 100 % sur les onze normes ment sur plusieurs points, et
# ces points sont connus d'avance. Les taire n'aide personne : ils se
# découvrent au pire moment, c'est-à-dire devant l'auditeur.

def limites(etats):
    import owasp_llm as _ow
    out = []
    # DORA A DÉSORMAIS UN TAUX — CE QUI DÉPLACE LA LIMITE, SANS LA SUPPRIMER.
    # Tant qu'il n'était pas mesuré, la limite était l'absence de mesure.
    # Maintenant qu'il l'est, la limite est la PORTÉE de ce qui est mesuré :
    # un nombre affiché est lu comme s'il couvrait tout le règlement, et il
    # n'en couvre que deux chapitres.
    dora = [e for e in etats if e["cle"] == "dora" and e.get("renseigne")]
    if dora:
        out.append({
            "cle": "dora_hors_taux",
            "quoi": "Le taux DORA porte sur le cadre de gestion du risque et "
                    "sur les contrats. Trois obligations lourdes en sont "
                    "absentes.",
            "pourquoi": "La chaîne de notification et ses délais en heures "
                        "(article 19 ; règlement délégué (UE) 2025/301, "
                        "article 5), les tests de pénétration fondés sur la "
                        "menace (articles 26 et 27) et le registre "
                        "d'informations (article 28, paragraphe 3) ne "
                        "s'évaluent pas par un questionnaire. Cent pour cent "
                        "ici ne veut pas dire DORA tenu.",
            "quoi_faire": "Traiter ces trois-là comme des chantiers propres, "
                          "hors de ce taux — la classification d'un incident "
                          "se répète à blanc, elle ne se coche pas.",
        })
        out.append({
            "cle": "dora_tlpt_autorites",
            "quoi": "Ce n'est pas vous qui décidez si vous devez conduire un "
                    "test de pénétration fondé sur la menace.",
            "pourquoi": "L'article 2 du règlement délégué (UE) 2025/1190 "
                        "confie cette détermination aux autorités désignées, "
                        "sur six facteurs d'incidence et neuf facteurs de "
                        "risque. Aucun questionnaire ne s'y substitue, et "
                        "s'en dispenser parce qu'on ne s'est pas désigné "
                        "soi-même est un contresens.",
            "quoi_faire": "Demander à l'autorité compétente si l'entité "
                          "figure parmi celles qu'elle a retenues.",
        })
        out.append({
            "cle": "dora_nis2_ne_se_presume_pas",
            "quoi": "La mise à l'écart de NIS 2 ne se présume pas, et elle "
                    "n'est jamais totale.",
            "pourquoi": "L'article 1er, paragraphe 2, ne vise que les "
                        "entités FINANCIÈRES identifiées essentielles ou "
                        "importantes — pas les prestataires tiers de "
                        "services TIC. Et même lorsqu'il joue, "
                        "l'identification et l'enregistrement de "
                        "l'article 3, paragraphes 3 et 4, de la directive "
                        "restent dus.",
            "quoi_faire": "Ouvrir le panneau « DORA · qualification » : "
                          "l'articulation s'y calcule, article par article.",
        })
    nist = [e for e in etats if e["cle"] == "nist_ai_rmf"]
    if nist:
        out.append({
            "cle": "nist_non_certifiable",
            "quoi": "100 % sur le NIST AI RMF n'est pas une conformité.",
            "pourquoi": "Ce cadre n'est pas certifiable : aucun organisme ne "
                        "délivre d'attestation contre lui. Le taux mesure la "
                        "couverture que vous déclarez, et rien de plus — "
                        "l'annoncer comme une conformité serait une faute "
                        "devant un client comme devant un assureur.",
            "quoi_faire": "L'annoncer pour ce qu'il est : une couverture "
                          "volontaire, utile en appui d'une démarche 42001.",
        })
    hors = (_ow.pont_42001() or {}).get("hors_portee") or []
    if hors:
        out.append({
            "cle": "owasp_hors_annexe_a",
            "quoi": "%s ne rencontrent aucune mesure de l'annexe A 42001."
                    % ", ".join(hors),
            "pourquoi": "Ces risques-là ne se referment par aucun travail de "
                        "certification : ils se traitent dans l'architecture "
                        "et l'exploitation. Une organisation certifiée 42001 "
                        "les garde entiers.",
            "quoi_faire": "Les traiter comme des risques techniques, hors du "
                          "plan de certification.",
        })
    certifiables = [e for e in etats
                    if e.get("nature") == "certifiable" and e.get("taux") == 100]
    if certifiables:
        out.append({
            "cle": "audit_reel",
            "quoi": "Un taux de 100 %% sur %s ne vaut pas certificat."
                    % ", ".join(e["nom"] for e in certifiables),
            "pourquoi": "Il reste à avoir réellement conduit un audit interne "
                        "et une revue de direction, puis à faire venir un "
                        "organisme accrédité. Aucune case cochée ici ne "
                        "remplace ces trois-là.",
            "quoi_faire": "Planifier l'audit interne, la revue de direction, "
                          "puis l'étape 1 avec l'organisme.",
        })
    return out


# ══════════════════════════════════════════════════════════════════════════
#  L'ENTRÉE
# ══════════════════════════════════════════════════════════════════════════

def etat_des_lieux(declarations=None, plafond_actions=24):
    """Les onze taux, ce qui commande, le plan, et ce que le plan ne peut pas.

    `declarations` porte, par clé de norme, la déclaration que le module de
    cette norme attend — la même, exactement. On ne redéfinit aucun format :
    un second vocabulaire pour dire la même chose est un second endroit à
    tenir d'accord.
    """
    d = declarations or {}
    if not isinstance(d, dict):
        return {"ok": False, "motif": "declarations_illisibles"}

    import iso42001 as _i42
    import iso27001 as _i27
    import nis2 as _n2
    import cra as _cra
    import nist_ai_rmf as _nist
    import owasp_llm as _ow
    import dora as _dora

    evaluations = {
        "ia_act": evaluer_audit_ia_act(d.get("ia_act")),
        "cra": _cra.evaluer_produit(d.get("cra")) if d.get("cra") else None,
        "iso42001": _i42.evaluer(d.get("iso42001")) if d.get("iso42001") else None,
        "iso27001": _i27.evaluer(d.get("iso27001")) if d.get("iso27001") else None,
        "dora": _dora.evaluer(d.get("dora")) if d.get("dora") else None,
        "nis2": _n2.evaluer(d.get("nis2")) if d.get("nis2") else None,
        "rgpd": (dict(d["rgpd"], ok=True) if isinstance(d.get("rgpd"), dict)
                 else None),
        "nist_ai_rmf": _nist.evaluer(d.get("nist_ai_rmf") or {}),
        "owasp_llm": _ow.evaluer(d.get("owasp_llm") or {}),
    }
    # L'AUDIT IA ACT ET LES DEUX DERNIERS NE SE DISTINGUENT PAS D'UNE
    # DÉCLARATION VIDE PAR LEUR ÉVALUATION : ils rendent ok=True sur rien.
    # C'est la DÉCLARATION qui dit si le sujet a été ouvert.
    for cle in ("ia_act", "nist_ai_rmf", "owasp_llm"):
        if not d.get(cle):
            evaluations[cle] = None

    etats, ecarts = [], {}
    for norme in NORMES:
        cle = norme["cle"]
        ev = evaluations.get(cle)
        dec = d.get(cle)
        et = taux_norme(cle, ev, dec)
        extracteur = ECARTEURS.get(cle)
        liste = extracteur(ev, dec) if (extracteur and ev) else []
        ecarts[cle] = liste
        par_comp = {}
        for x in liste:
            par_comp[x["composant"]] = par_comp.get(x["composant"], 0) + 1
        et["_ecarts_par_composant"] = par_comp
        et["ecarts"] = len(liste)
        etats.append(et)

    p = plan(etats, ecarts, plafond_actions=plafond_actions)
    for et in etats:
        et.pop("_ecarts_par_composant", None)
    return {
        "ok": True, "version": VERSION,
        "normes": etats,
        "consolide": consolide(etats),
        "plan": p,
        "limites": limites(etats),
        "natures": NATURES,
        "reserve": "Les taux mesurent le travail déclaré, jamais un jugement "
                   "de conformité. Sur une obligation, c'est une autorité qui "
                   "tranche ; sur une norme certifiable, un organisme "
                   "accrédité ; sur un cadre volontaire, personne.",
    }


# ══════════════════════════════════════════════════════════════════════════
#  LA GARDE — CE QUE CE MODULE REFUSE DE LAISSER PASSER
# ══════════════════════════════════════════════════════════════════════════

def _verifier():
    fautes = []

    # LE COMPTE EST ÉCRIT ICI, ET LA PAGE D'ACCUEIL DOIT S'Y TENIR. Il a
    # valu neuf ; il vaut onze depuis que les deux référentiels NIST de
    # sécurité des systèmes industriels ont rejoint la grille. Une règle de
    # la suite confronte ce nombre au titre et à la grille de l'accueil :
    # c'est le seul endroit où il se décide.
    if len(NORMES) != NORMES_ANNONCEES:
        fautes.append("le site annonce %d normes, ce module en déclare %d"
                      % (NORMES_ANNONCEES, len(NORMES)))
    if len(NORMES_PAR_CLE) != len(NORMES):
        fautes.append("deux normes partagent une clé")

    # PLUS AUCUNE NORME DE LA GRILLE N'EST SANS INSTRUMENT. DORA fut la
    # dernière, et il ne l'est plus depuis que les quatre moteurs
    # `dora*.py` le mesurent. La règle ne disparaît pas pour autant : elle
    # change de sens et devient plus exigeante — une norme affichée sur
    # l'accueil sans moyen de la mesurer est désormais un défaut, pas une
    # exception à documenter.
    sans = [n["cle"] for n in NORMES if n["nature"] == "sans_instrument"]
    if sans:
        fautes.append(
            "%s figure(nt) dans la grille sans instrument de mesure. Depuis "
            "que DORA a ses moteurs, aucune norme annoncée n'est sans "
            "module : en afficher une reviendrait à promettre une maîtrise "
            "qu'aucun écran ne soutient." % sans)

    for n in NORMES:
        if n["nature"] not in NATURES:
            fautes.append("%s : nature inconnue %r" % (n["cle"], n["nature"]))
            continue
        nat = NATURES[n["nature"]]
        if not nat.get("cent_ne_veut_pas_dire"):
            fautes.append("la nature %r ne dit pas ce que 100 %% NE veut pas "
                          "dire — c'est la seule phrase qui empêche de lire "
                          "un taux comme une attestation" % n["nature"])
        if n["nature"] == "sans_instrument":
            if n["cle"] in COMPOSITIONS:
                fautes.append("%s n'a pas de taux mais porte une composition"
                              % n["cle"])
            continue
        if n["cle"] not in COMPOSITIONS:
            fautes.append("%s : aucune composition" % n["cle"])
        if n["cle"] not in LECTEURS:
            fautes.append("%s : aucun lecteur" % n["cle"])
        if n["cle"] not in ECARTEURS:
            fautes.append("%s : aucun extracteur d'écarts — son taux "
                          "monterait sans qu'aucune action ne le dise"
                          % n["cle"])
        if not n.get("panneau"):
            fautes.append("%s : aucun panneau Sentinel. Un taux qui ne mène "
                          "pas à l'écran où on le corrige est un reproche, "
                          "pas un outil." % n["cle"])
        if not n.get("mesure"):
            fautes.append("%s : ne dit pas ce qu'il mesure" % n["cle"])

    for cle, reserves in RESERVES.items():
        if cle not in COMPOSITIONS:
            fautes.append("réserve sur %s, qui n'a pas de composition" % cle)
        for r in reserves:
            if not r.get("porte_sur"):
                fautes.append(
                    "%s/%s ne dit pas SUR QUOI elle porte. Une réserve qui ne "
                    "délimite pas ce qu'elle met en doute laisse le lecteur "
                    "douter de tout le taux — ou de rien."
                    % (cle, r["cle"]))
            if not r.get("ou"):
                fautes.append("%s/%s ne dit pas où se lève" % (cle, r["cle"]))
        croises = set(v["cle"] for v in VERROUS.get(cle, ())) & \
            set(r["cle"] for r in reserves)
        if croises:
            fautes.append("%s : %s est à la fois verrou et réserve"
                          % (cle, sorted(croises)))

    for cle, comp in COMPOSITIONS.items():
        if cle not in NORMES_PAR_CLE:
            fautes.append("composition orpheline : %s" % cle)
        if not comp:
            fautes.append("%s : composition vide" % cle)
        vus = set()
        for c in comp:
            if c["poids"] <= 0:
                fautes.append("%s/%s : poids %r — un composant qui ne pèse "
                              "rien ne devrait pas figurer"
                              % (cle, c["cle"], c["poids"]))
            if not c.get("pourquoi"):
                fautes.append("%s/%s : poids sans motif écrit"
                              % (cle, c["cle"]))
            if c["cle"] in vus:
                fautes.append("%s : composant %s déclaré deux fois"
                              % (cle, c["cle"]))
            vus.add(c["cle"])

    for cle, verrous in VERROUS.items():
        if cle not in COMPOSITIONS:
            fautes.append("verrou sur %s, qui n'a pas de composition" % cle)
            continue
        # UN VERROU N'EXISTE QUE LÀ OÙ UN TIERS REFUSE D'ALLER PLUS LOIN.
        # C'est la ligne qui le sépare d'une réserve, et elle est vérifiable :
        # seules les normes certifiables ont un auditeur qui peut s'arrêter à
        # la porte. Ailleurs, un plafond serait une sévérité inventée.
        if NORMES_PAR_CLE.get(cle, {}).get("nature") != "certifiable":
            fautes.append(
                "%s porte un verrou sans être certifiable. Un verrou plafonne "
                "un taux parce qu'un tiers refuse de poursuivre ; sans "
                "auditeur au bout, ce n'est pas un verrou mais une réserve, "
                "et elle se déclare dans RESERVES." % cle)
        connus = {c["cle"] for c in COMPOSITIONS[cle]}
        poids_total = sum(c["poids"] for c in COMPOSITIONS[cle])
        for v in verrous:
            inconnus = sorted(set(v["bloque"]) - connus)
            if inconnus:
                fautes.append("%s/%s bloque des composants qui n'existent "
                              "pas : %s" % (cle, v["cle"], inconnus))
            if not v["bloque"]:
                fautes.append("%s/%s ne bloque rien : il ne plafonne donc "
                              "rien, et n'est pas un verrou"
                              % (cle, v["cle"]))
            bloque = sum(c["poids"] for c in COMPOSITIONS[cle]
                         if c["cle"] in set(v["bloque"]))
            if bloque >= poids_total:
                fautes.append(
                    "%s/%s bloque TOUT : le taux serait toujours nul, ce qui "
                    "effacerait le travail fait au lieu de le plafonner"
                    % (cle, v["cle"]))
            if not v.get("ou"):
                fautes.append("%s/%s ne dit pas où se lève" % (cle, v["cle"]))

    # LES DEUX PRIORITÉS DE L'AUDIT IA ACT DOIVENT ÊTRE CELLES DES POINTS.
    prios_declarees = {p[4] for p in AUDIT_IA_ACT}
    if prios_declarees != set(PRIORITES_IA_ACT):
        fautes.append("l'audit IA Act porte les priorités %s, la table en "
                      "déclare %s" % (sorted(prios_declarees),
                                      sorted(PRIORITES_IA_ACT)))
    composants_ia = {c["cle"] for c in COMPOSITIONS["ia_act"]}
    if composants_ia != prios_declarees:
        fautes.append("la composition IA Act pondère %s alors que l'audit "
                      "porte %s" % (sorted(composants_ia),
                                    sorted(prios_declarees)))
    if len({p[0] for p in AUDIT_IA_ACT}) != len(AUDIT_IA_ACT):
        fautes.append("deux points de l'audit IA Act partagent un identifiant")
    sections = {s[0] for s in AUDIT_IA_ACT_SECTIONS}
    orphelins = sorted({p[1] for p in AUDIT_IA_ACT} - sections)
    if orphelins:
        fautes.append("des points de l'audit visent des sections absentes : %s"
                      % orphelins)

    if fautes:
        raise RuntimeError(
            "conformite.py — incohérences :\n  - " + "\n  - ".join(fautes))


_verifier()
