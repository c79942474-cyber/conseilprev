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

  3. UN TAUX SUR UNE NORME QU'ON NE MESURE PAS EST UN MENSONGE POLI. Une norme
     dont l'écran ne porte aucune réponse rend None, jamais 0 ; une norme que
     la qualification déclarée écarte rend « sans objet ». Zéro voudrait dire
     « rien de fait » ; None veut dire « nous ne le mesurons pas », et c'est
     la vérité.

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

VERSION = "2026-09-b"

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
    {"cle": "en18229_3", "nom": "prEN 18229-3", "nature": "cadre",
     "texte": "prEN 18229-3:2026 (CEN/CLC JTC 21)",
     "panneau": "en18229-role",
     "mesure": "la supervision humaine de l'article 14 : les scénarios de "
               "risque, leur délai de réaction, et les mesures qui doivent "
               "le tenir"},
    {"cle": "nist_800_82", "nom": "NIST SP 800-82", "nature": "cadre",
     "texte": "NIST SP 800-82 Rev. 2 (2015)",
     "panneau": "nist82-ot",
     "mesure": "les dix axes de la surcharge industrielle, plafonnés par le "
               "socle 800-53 qu'ils taillent"},
    #  LA TREIZIÈME, ET LA SECONDE DU CEN/CLC JTC 21 : le système de
    #  management de la qualité que l'article 17 impose au fournisseur d'un
    #  système d'IA à haut risque. Comme prEN 18229-3, elle est au stade de
    #  l'Enquête CEN — donc « cadre » et non « certifiable » : rien ne s'y
    #  certifie tant que la référence n'est pas citée au Journal officiel.
    {"cle": "en18286", "nom": "prEN 18286", "nature": "cadre",
     "texte": "prEN 18286:2025 (CEN/CLC JTC 21)",
     "panneau": "en18286-processus",
     "mesure": "le système de management de la qualité de l'article 17 : la "
               "stratégie de conformité réglementaire, et la charge de "
               "preuve que l'approche retenue ouvre"},
    #  LA QUATORZIÈME, ET LA PREMIÈRE QUI NE SOIT NI UNE OBLIGATION NI UNE
    #  NORME : un GUIDE DE MISE EN ŒUVRE de deux recommandations de l'OCDE.
    #  « cadre », donc, comme le NIST — mais pour une raison plus forte que
    #  les deux prEN : celles-là vaudront présomption le jour de leur
    #  citation au Journal officiel, celui-ci jamais. Et ce qu'il mesure
    #  n'est pas ce que les treize autres mesurent : elles demandent si LE
    #  SYSTÈME est conforme, celui-ci demande si L'ENTREPRISE a fait ce
    #  qu'il fallait pour savoir — relations d'affaires, amont et aval
    #  compris.
    {"cle": "ocde", "nom": "Diligence OCDE", "nature": "cadre",
     "texte": "OECD Due Diligence Guidance for Responsible AI (2026)",
     "panneau": "ocde-processus",
     "mesure": "les six étapes de la diligence, l'implication dans "
               "l'incidence — causer, contribuer, être lié — et les quatre "
               "facteurs de priorisation"},
]
NORMES_PAR_CLE = {n["cle"]: n for n in NORMES}


# ══════════════════════════════════════════════════════════════════════════
#  UNE COULEUR PAR RÉFÉRENTIEL — DÉCLARÉE ICI, DÉRIVÉE PARTOUT
# ══════════════════════════════════════════════════════════════════════════
#
# POURQUOI ELLE EST DANS CE FICHIER. C'est lui qui tient la liste des douze
# normes. Une seconde liste de couleurs, dans la feuille de style, se
# séparerait de celle-ci au premier référentiel ajouté : la treizième norme
# arriverait sans couleur, ou hériterait de celle d'une autre — et rien ne
# le dirait. La barre latérale et le rail lisent CELLE-CI.
#
# CE QUE LA COULEUR DIT, ET CE QU'ELLE NE DIT PAS. Elle dit « cet écran
# appartient à ce référentiel-là », et rien d'autre. Elle ne classe pas, ne
# hiérarchise pas, ne signale aucun état.
#
# ELLE N'EST JAMAIS SEULE À PORTER L'INFORMATION. Chaque entrée de la barre
# garde son nom écrit. Douze teintes ne peuvent pas être TOUTES séparables
# deux à deux : mesurées toutes paires confondues, la plus proche tombe à
# ΔE 12,2 en vision normale (sarcelle et ciel) et à 3,6 en protanopie
# (violet et bleu) — le pétrole de la douzième n'a rapproché ni l'une ni
# l'autre, il est à ΔE 28,8 de son plus proche voisin de tiroir. C'est le nom, pas la couleur, qui identifie ; la
# couleur fait retrouver d'un coup d'œil ce que le nom a déjà dit.
#
# L'ORDRE EST CELUI DE LA BARRE LATÉRALE, ET C'EST LE POINT. Deux couleurs
# ne se comparent à l'œil que si elles se touchent : ce sont les tiroirs
# VOISINS qui doivent se séparer. `ORDRE_BARRE` fixe l'ordre réel des
# tiroirs, une règle le confronte à la page, et c'est dans CET ordre que la
# palette a été validée — pire voisinage ΔE 20,8 en vision normale (plancher
# 15, sur bleu/sarcelle) et 18,8 en vision déficiente (cible 8, même paire).
# Les deux NIST, qui partagent un tiroir, sont voisins et comptent comme
# tels. LE PÉTROLE S'EST GLISSÉ ENTRE SARCELLE ET VIOLET, et cela a DÉFAIT
# le pire voisinage déficient d'avant — sarcelle/violet à 17,4 — qui n'est
# plus une adjacence : les deux ne se touchent plus.
#
# TROIS COULEURS DISENT DÉJÀ AUTRE CHOSE DANS SENTINEL, ET AUCUNE DES DOUZE
# NE LES IMITE. La terre cuite dit « ici » — elle prend l'icône au survol et
# remplit la pastille de l'onglet ouvert ; le vert dit « bloc validé », le
# bleu « bloc attendu », l'ambre « bloc verrouillé ». Aucune des douze n'est
# à moins de ΔE 8 de l'une d'elles : ce n'est jamais le même pas de
# couleur. ET LE VERT EST TENU À L'ÉCART TOUT ENTIER, pas seulement son pas
# exact : c'est la couleur que le parcours donne à un bloc rempli, dans ces
# douze modules mêmes. Un référentiel vert dans la barre se lirait « acquis ».
# D'où l'absence d'un rouge franc, d'un orange et d'un vert : les deux
# premiers tomberaient sur la terre cuite ou sur l'ambre, le troisième sur
# le sens que le rail lui donne.
#
# MESURÉ AVANT D'ÊTRE ÉCRIT, avec le validateur de palettes, dans l'ordre
# de la barre : bande de clarté, plancher de chroma, séparation en vision
# normale et déficiente, contraste. Tout passe ; le contraste de l'icône sur
# sa propre pastille teintée ne descend pas sous 3:1 (WCAG 1.4.11).

COULEURS = {
    "rgpd":        "#C50759",   # cramoisi
    "iso27001":    "#355CD4",   # bleu
    "iso42001":    "#0A8D83",   # sarcelle
    "dora":        "#9650E8",   # violet
    "nis2":        "#8F7515",   # ocre
    "cra":         "#9B0D9F",   # magenta
    "nist_ai_rmf": "#804810",   # bronze
    "owasp_llm":   "#D35D94",   # rose
    "nist_800_53": "#7F2E55",   # prune
    "nist_800_82": "#138BCF",   # ciel
    "en18229_3":   "#00323C",   # pétrole
    #  AUBERGINE, ET NON LE VERT QU'ON AURAIT CHOISI D'INSTINCT. Mesuré :
    #  un vert de qualité (#1F6F3F) tombait à ΔE 3,7 du vert qui dit
    #  « bloc validé » dans le rail — un référentiel vert dans la barre se
    #  lirait « acquis » avant d'avoir répondu à une seule question. Tout
    #  l'arc du vert et du sarcelle est d'ailleurs fermé ici : le vert de
    #  validation d'un côté, ISO 42001 et prEN 18229-3 de l'autre.
    #  CETTE TEINTE EST LA PLUS ÉCARTÉE QUE LA PLACE PERMETTE. prEN 18286
    #  est VOISINE de prEN 18229-3 (pétrole très sombre) et de DORA
    #  (violet clair) dans la barre. Relevé : ΔE 18,7 du pétrole et 26,0 du
    #  violet en vision normale ; 10,4 et 24,7 en vision déficiente. Les
    #  planchers sont 15 et 8 : la paire la plus serrée passe à ×1,25,
    #  quand les autres paires de la barre tiennent à ×1,4 ou mieux. C'est
    #  le maximum atteignable entre ces deux voisines-là, et c'est une
    #  contrainte de place, pas un relâchement du contrôle.
    "en18286":     "#500078",   # aubergine
    # L'IA ACT N'EST PAS DANS LES TIROIRS DE CONFORMITÉ : son écran d'entrée
    # vit sous « Pilotage », parmi des onglets en terre cuite. Sa couleur ne
    # voisine donc aucune des onze autres, et n'entre pas dans le contrôle
    # d'adjacence ; elle reste loin de la terre cuite qui l'entoure.
    "ia_act":      "#5F24B7",   # indigo
    #  LE SANG-DE-BŒUF, ET LE BLEU DE L'OCDE ÉCARTÉ PAR SA PROPRE LICENCE :
    #  CC BY interdit d'employer son identité visuelle ou de suggérer qu'elle
    #  adosse cet usage. Relevé : ΔE 15,7 de la teinte de norme la plus
    #  proche, 24,1 de la couleur d'état la plus proche, 11,4:1 de contraste
    #  sur sa propre pastille. Dans la barre, sa seule voisine est NIST
    #  800-82 (bleu vif), à ΔE 40,0 en vision normale et 35,3 en vision
    #  déficiente — la paire la plus large de la barre.
    "ocde":        "#550707",   # sang-de-bœuf
}

#: L'ORDRE OÙ LES RÉFÉRENTIELS SE SUIVENT DANS LA BARRE LATÉRALE. Il ne se
#: devine pas de `NORMES`, dont l'ordre est celui de la page d'accueil.
#:
#: LES DEUX NORMES DE L'IA VOISINENT, ET C'EST UN CHOIX : prEN 18229-3 sert
#: l'article 14 de l'IA Act comme ISO/IEC 42001 sert son système de
#: management. Un client qui ouvre l'une trouve l'autre à côté. La règle
#: d'adjacence des couleurs est mesurée sur cet ordre, pas sur un autre.
ORDRE_BARRE = ("rgpd", "iso27001", "iso42001", "en18229_3", "en18286",
               "dora", "nis2",
               "cra", "nist_ai_rmf", "owasp_llm", "nist_800_53",
               "nist_800_82", "ocde")


def couleur(cle):
    """La couleur d'un référentiel, ou None s'il n'en a pas.

    ON NE REND PAS UNE COULEUR PAR DÉFAUT. Une teinte de repli ferait
    passer un référentiel oublié pour un référentiel gris — et personne ne
    verrait qu'il manque."""
    return COULEURS.get(cle)

#: CE QUE LA PAGE D'ACCUEIL ANNONCE. Un seul endroit le décide ; la
#: garde en bas de fichier le confronte à la table ci-dessus, et une
#: règle de la suite le confronte au titre et à la grille de l'accueil.
NORMES_ANNONCEES = 14


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
    ("a5_1", "art5", "Inventaire des pratiques potentiellement interdites", "Art. 5(1)(a) à (e), (ba), (bb)", "p1"),
    ("a5_2", "art5", "Absence d'identification biométrique à distance non autorisée", "Art. 5(1)(h)", "p1"),
    ("a5_3", "art5", "Vérification du périmètre émotionnel et de catégorisation", "Art. 5(1)(f)(g)", "p1"),
    ("a5_4", "art5", "Culture de l'IA des équipes (Art. 4)", "Art. 4", "p2"),
    ("a6_1", "art6", "Cartographie complète des systèmes IA", "Art. 6, Art. 51", "p1"),
    ("a6_2", "art6", "Classification selon l'Annexe III (8 domaines) et l'Annexe I", "Art. 6(1)(2), Annexe I et III", "p1"),
    ("a6_3", "art6", "Documentation de la décision de classification", "Art. 6(4)", "p2"),
    ("a6_4", "art6", "Procédure de reclassification continue", "Art. 6, Art. 9", "p2"),
    ("a9_1", "art9_10", "Système de gestion des risques documenté et opérationnel", "Art. 9(1)(2)", "p1"),
    ("a9_2", "art9_10", "Tests avant mise sur le marché", "Art. 9(5)(6)", "p1"),
    ("a9_3", "art9_10", "Gouvernance des données d'entraînement", "Art. 10(2)", "p1"),
    ("a9_4", "art9_10", "Qualité des données de validation et de test", "Art. 10(3)(4)", "p1"),
    ("a9_5", "art9_10", "Données personnelles dans l'entraînement", "Art. 10, Art. 4a, RGPD", "p2"),
    ("a11_1", "art11_12", "Dossier technique complet (Annexe IV)", "Art. 11, Annexe IV", "p1"),
    ("a11_2", "art11_12", "Mise à jour continue du dossier technique", "Art. 11(2)", "p2"),
    ("a12_1", "art11_12", "Journalisation automatique des décisions", "Art. 12(1)(2)", "p1"),
    ("a12_2", "art11_12", "Conservation des journaux", "Art. 12(3)", "p2"),
    ("a18_1", "art11_12", "Conservation de la documentation technique (10 ans)", "Art. 18", "p2"),
    ("a13_1", "art13_14", "Notice d'utilisation conforme Art. 13", "Art. 13(3)", "p1"),
    ("a13_2", "art13_14", "Transparence envers les utilisateurs finaux (Art. 50)", "Art. 50(1) à (4)", "p1"),
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
    #  LES SIX ÉTAPES DE LA DILIGENCE, AVEC LES POIDS DU MOTEUR. Les
    #  recopier ici est un doublon assumé et surveillé : une règle confronte
    #  ces poids à `ocde_ia.ETAPES`, parce que deux jeux de poids rendraient
    #  deux taux pour la même déclaration.
    "ocde": [
        {"cle": "ancrer", "nom": "Ancrer dans les politiques", "poids": 1,
         "pourquoi": "le socle, et celui qu'un système de management déjà en "
                     "place apporte le plus souvent tel quel"},
        {"cle": "identifier", "nom": "Identifier et évaluer", "poids": 3,
         "pourquoi": "l'étape qui commande toutes les autres : sans "
                     "incidences identifiées, qualifiées et priorisées, les "
                     "étapes 3 à 6 n'ont pas d'objet"},
        {"cle": "traiter", "nom": "Faire cesser, prévenir, atténuer",
         "poids": 3,
         "pourquoi": "le seul endroit où quelque chose change pour les "
                     "personnes"},
        {"cle": "suivre", "nom": "Suivre la mise en œuvre", "poids": 1,
         "pourquoi": "ce qui empêche la diligence d'être un exercice annuel"},
        {"cle": "communiquer", "nom": "Rendre compte", "poids": 1,
         "pourquoi": "la part que les parties prenantes peuvent vérifier"},
        {"cle": "reparer", "nom": "Réparer ou y coopérer", "poids": 2,
         "pourquoi": "l'attente la plus forte du cadre dès que l'entreprise "
                     "cause ou contribue"},
    ],
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
    #  LA SUPERVISION HUMAINE SE COMPOSE DE TROIS PARTS, ET LA PREMIÈRE
    #  COMMANDE LES DEUX AUTRES : sans scénario de risque ni délai de
    #  réaction, une interface de revue ne se justifie par rien et une
    #  vérification ne sait pas contre quoi conclure.
    #  CINQ PARTS, ET LE POIDS SUIT LA CHARGE RÉGLEMENTAIRE, pas le nombre
    #  de paragraphes. La stratégie du §4.4 pèse le plus parce qu'elle n'a
    #  d'équivalent ni dans ISO 9001 ni dans ISO/IEC 42001 : c'est ce que le
    #  règlement AJOUTE, et ce qu'un SMQ déjà certifié ne porte pas.
    "en18286": [
        {"cle": "strategie", "nom": "Stratégie et documentation", "poids": 3,
         "pourquoi": "le §4.4 est la pièce propre au règlement, et celle que "
                     "l'organisme notifié ouvre en premier"},
        {"cle": "direction", "nom": "Direction, planification, support",
         "poids": 1,
         "pourquoi": "le socle de management, celui qu'un SMQ déjà certifié "
                     "apporte le plus souvent tel quel"},
        {"cle": "produit", "nom": "Élaboration du produit", "poids": 2,
         "pourquoi": "de la destination à la documentation technique : ce "
                     "que l'évaluation de conformité examine"},
        {"cle": "exploitation", "nom": "Exploitation et contrôle", "poids": 2,
         "pourquoi": "surveillance après commercialisation et incidents "
                     "graves — les deux obligations dont une autorité se "
                     "saisit sans attendre un audit"},
        {"cle": "performance", "nom": "Évaluation des performances",
         "poids": 1,
         "pourquoi": "la revue de direction ne produit rien par elle-même : "
                     "elle décide de ce que le reste produit"},
    ],
    "en18229_3": [
        {"cle": "calibration", "nom": "Scénarios, délais et sélection",
         "poids": 3,
         "pourquoi": "le délai de réaction décide quelle catégorie de mesure "
                     "peut tenir un scénario ; tout le reste s'y réfère"},
        {"cle": "mesures", "nom": "Mesures et fonctions d'intervention",
         "poids": 2,
         "pourquoi": "les interfaces, les notifications et les quatre "
                     "fonctions — ce que la personne désignée voit et ce "
                     "qu'elle peut faire"},
        {"cle": "preuves", "nom": "Vérification et documentation", "poids": 2,
         "pourquoi": "ce qui sépare une conception d'une mesure qui "
                     "fonctionne, et ce qui la rend démontrable"},
    ],
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
    #  LE SEUL VERROU DU SITE QUI NE VIENT PAS D'UNE CASE MAIS D'UN CALCUL.
    #  Un scénario dont la latence d'intervention dépasse son délai de
    #  réaction, sans que l'impossibilité technique soit consignée, est le cas
    #  que la norme refuse nommément. Tant qu'il tient, on ne peut pas
    #  prétendre que les mesures ni leurs preuves valent quelque chose : elles
    #  sont calibrées sur un délai qu'elles ne tiennent pas.
    "en18229_3": [
        {"cle": "scenario_sans_intervention",
         "dit": "Au moins un scénario de risque a une latence d'intervention "
                "supérieure à son délai de réaction, sans consignation de "
                "l'impossibilité technique au dossier de gestion des "
                "risques. La supervision humaine n'y est pas une mesure de "
                "gestion des risques.",
         "bloque": ["mesures", "preuves"],
         "ou": "en18229 · scénarios de risque",
         "fonde_sur": "arithmetique",
         "calcul": "la latence d'intervention déclarée du scénario (5.7.1) "
                   "comparée à son délai de réaction déterminé (5.2.2) — deux "
                   "nombres que le client déclare, aucun seuil inventé ici"},
    ],
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
    #  AUCUNE DE CES TROIS NE SE LÈVE PAR LE TRAVAIL. La première est la
    #  nature de l'instrument, la deuxième l'aveu du document sur ses propres
    #  exemples, la troisième son refus d'équivalence.
    "ocde": [
        {"cle": "volontaire",
         "dit": "Ce guide est VOLONTAIRE : c'est la mise en œuvre de deux "
                "recommandations de l'OCDE, pas une norme harmonisée. Il "
                "n'ouvre aucune présomption de conformité, et aucune date ne "
                "changera cela.",
         "porte_sur": "Le taux dit la diligence déclarée. Aucun organisme ne "
                      "délivre d'attestation contre ce guide — à la "
                      "différence de prEN 18286, qui vaudra présomption le "
                      "jour de sa citation au Journal officiel.",
         "ou": "ocde · analyse"},
        {"cle": "non_exhaustif",
         "dit": "Le document déclare lui-même que ses exemples pratiques ne "
                "constituent pas une liste de contrôle exhaustive.",
         "porte_sur": "Ce que ce taux mesure s'appelle « couverture des "
                      "exemples retenus », jamais conformité : un organisme "
                      "peut les tenir tous et rester en défaut sur un risque "
                      "qu'aucun d'eux ne nomme.",
         "ou": "ocde · questionnaire"},
        {"cle": "pas_equivalence",
         "dit": "Les six feuilles de route rapprochent les étapes de l'OCDE "
                "des dispositions de vingt autres cadres. Le document écrit "
                "que ce n'est PAS un cadre d'équivalence.",
         "porte_sur": "Tenir ISO/IEC 42001 ou le cadre du NIST ne vaut pas "
                      "diligence OCDE, et l'inverse est vrai aussi. Sur ces "
                      "vingt cadres, Sentinel en mesure trois.",
         "ou": "ocde · conformité"},
    ],
    "en18286": [
        {"cle": "charge_de_preuve",
         "dit": "Une ou plusieurs exigences essentielles sont traitées par "
                "« autre norme » ou « autre solution technique » sans la "
                "justification et la preuve objective que le §4.4.3.2.2 "
                "réclame.",
         "porte_sur": "La part « stratégie » n'est comptée qu'à moitié : le "
                      "travail de documentation est réel, c'est la "
                      "DÉMONSTRATION qui manque. Le détail est sur l'écran "
                      "« Processus ».",
         "ou": "en18286 · processus"},
        {"cle": "presomption",
         "dit": "Ce projet de norme n'est pas encore cité au Journal "
                "officiel de l'Union européenne au titre du Règlement (UE) "
                "2024/1689 : le tenir n'ouvre aucune présomption de "
                "conformité à l'article 17.",
         "porte_sur": "Le taux dit ce que le système de management déclaré "
                      "couvre du tableau ZA.1. Il ne dit ni qu'un organisme "
                      "notifié l'a vu, ni que la norme est citée.",
         "ou": "en18286 · conformité"},
        #  LA LACUNE EST DÉCLARÉE PAR LA NORME, PAS PAR NOUS. L'annexe ZA
        #  porte une ligne « Non couvert » : la taire ferait lire 100 % comme
        #  « article 17 tenu », ce que la norme elle-même dément.
        {"cle": "za_incomplete",
         "dit": "L'annexe ZA de cette norme déclare l'article 17(2) NON "
                "COUVERT — les fournisseurs soumis à la législation de "
                "l'Union sur les services financiers.",
         "porte_sur": "Cent pour cent ici ne veut pas dire article 17 tenu : "
                      "c'est la norme qui annonce sa propre limite.",
         "ou": "en18286 · conformité"},
        {"cle": "article_17_2",
         "dit": "Votre régime relève de l'article 17(2) : les obligations de "
                "gouvernance interne de la législation sur les services "
                "financiers valent exécution de l'article 17.",
         "porte_sur": "Le travail fait ici reste utile, mais il ne se "
                      "substitue pas à ce que votre autorité de tutelle "
                      "attend — et la norme ne couvre pas ce cas.",
         "ou": "en18286 · conformité"},
    ],
    "en18229_3": [
        {"cle": "presomption",
         "dit": "Ce projet de norme n'est pas encore cité au Journal officiel "
                "de l'Union européenne au titre du Règlement (UE) 2024/1689 : "
                "le tenir n'ouvre aucune présomption de conformité à "
                "l'article 14.",
         "porte_sur": "Le taux dit la supervision humaine déclarée au regard "
                      "d'un projet à l'Enquête CEN. Le jour où la référence "
                      "sera citée, le même travail vaudra présomption — dans "
                      "les limites du domaine d'application de la norme.",
         "ou": "en18229 · cadre d'analyse"},
    ],
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
        {"cle": "profil_genai",
         "dit": "Le système est déclaré génératif : le taux est celui du "
                "cadre PLAFONNÉ par le profil AI 600-1.",
         "porte_sur": "Une catégorie dont les actions du profil ne sont pas "
                      "tenues ne peut pas dépasser « amorcé » ; "
                      "partiellement tenues, elle ne dépasse pas « tenu ». "
                      "Le travail fait sur le cadre n'est pas retiré — c'est "
                      "ce qu'on peut en dire pour un système génératif qui "
                      "est borné.",
         "ou": "nist · profil IA générative"},
        {"cle": "socle_devance",
         "dit": "Une ou plusieurs fonctions devancent GOVERN.",
         "porte_sur": "Le cadre place GOVERN au-dessus des trois autres. Le "
                      "travail de MEASURE et de MANAGE est réel, mais "
                      "personne ne le reprend : c'est une couverture sans "
                      "gouvernance, pas une couverture moindre.",
         "ou": "nist · profil"},
    ],
}

# ── QUAND LA NORME NE S'APPLIQUE PAS : NI TAUX, NI ZÉRO ────────────────────
#
# CE N'EST NI UN VERROU NI UNE RÉSERVE. Un verrou plafonne un taux, une
# réserve le met en doute ; ici, il n'y a pas de taux du tout, parce que la
# qualification DÉCLARÉE écarte la norme. Mesuré avant cette table : une
# entité hors du champ de NIS 2 recevait « 0 % », dix écarts et dix actions
# au plan — le chantier que le module NIS 2 refuse justement de vendre à
# une entreprise hors champ —, pendant que le rail de son écran passait
# tous les blocs en « sans objet ».
SANS_OBJET = {
    "en18286": {
        "cle": "hors_champ",
        "dit": "L'article 17 vise le FOURNISSEUR d'un système d'IA à haut "
               "risque. Hors de cette qualification, il n'y a pas de taux à "
               "mesurer, et ce n'est pas un zéro. La qualification se revoit : "
               "un déployeur qui modifie substantiellement un système, ou qui "
               "y appose son nom, DEVIENT fournisseur au sens du règlement.",
        "ou": "en18286 · processus",
    },
    "nis2": {
        "cle": "hors_champ",
        "dit": "Hors du champ de la directive, selon la qualification "
               "déclarée : il n'y a pas de taux à mesurer, et ce n'est pas un "
               "zéro. La qualification se revoit le jour où le secteur ou la "
               "taille change.",
        "ou": "nis2 · qualification",
    },
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
    # LA QUALIFICATION SE LIT SUR LA DÉCLARATION, AVEC LA FONCTION DU RAIL.
    # `qualifier` rend toujours un statut — et « hors champ » sur un
    # formulaire VIDE. Le lire ici aurait fait dire au taux « hors champ » à
    # qui n'a pas encore choisi son secteur, pendant que le rail lui disait
    # « il manque le secteur ». Une seule lecture, donc : celle du rail.
    import parcours_normes as _pn
    manque, verdict = _pn.qualification_nis2(dec or {})
    statut = ((verdict or {}).get("statut") or {}).get("cle")
    # HORS CHAMP, IL N'Y A PAS DE TAUX — ET CE N'EST PAS UN ZÉRO. Mesuré :
    # une entité hors du champ recevait « 0 % » et dix actions au plan,
    # pendant que le rail passait tous ses blocs en « sans objet ».
    if not manque and statut == "hors_champ":
        return None, ["hors_champ"]
    parts = {
        "mesures": (ev.get("mesures") or {}).get("taux"),
        "gouvernance": (ev.get("gouvernance") or {}).get("taux"),
    }
    # LA RÉSERVE TOMBE QUAND LA QUALIFICATION N'EST PAS PRONONÇABLE : il
    # manque le secteur, ou la taille d'un secteur des annexes. On ne sait
    # alors pas quel régime s'applique, donc pas à quel niveau d'exigence
    # les dix mesures doivent être tenues.
    q = ev.get("qualification") or {}
    verrous = ["non_qualifie"] if (manque or q.get("indetermine")
                                   or not statut) else []
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


def _nist_declaration(dec):
    """Les états du cadre et la déclaration de profil, d'où qu'ils viennent.

    DEUX FORMES ARRIVENT ICI, ET C'EST VOULU. Avant le profil AI 600-1, la
    déclaration NIST ÉTAIT le dictionnaire des états — « GOVERN 1 » →
    « tenu ». Les dossiers déjà enregistrés la portent ainsi, et les refuser
    aurait effacé le taux de tout client qui n'a pas rouvert l'écran depuis.
    La forme neuve les emboîte sous « etats » et ajoute « profil ».

    ELLES SE DISTINGUENT SANS AMBIGUÏTÉ : aucune catégorie du cadre ne
    s'appelle « etats » ni « profil ».
    """
    d = dec if isinstance(dec, dict) else {}
    if "etats" in d or "profil" in d:
        etats = d.get("etats") if isinstance(d.get("etats"), dict) else {}
        profil = d.get("profil") if isinstance(d.get("profil"), dict) else {}
        return etats, profil
    return d, {}


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
    signaux = ["socle_devance"] if ev.get("devancent_le_socle") else []
    # LE PROFIL A DÉJÀ AGI SUR LES NOTES CI-DESSUS — il plafonne l'état de
    # chaque catégorie qu'il charge. La réserve ne rabaisse donc rien de
    # plus : elle DIT que le nombre affiché n'est pas celui du socle, ce que
    # l'écran ne pourrait pas deviner d'un pourcentage.
    if ev.get("plafonds_du_profil"):
        signaux.append("profil_genai")
    return parts, signaux


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


#: À quelle part de la composition appartient chaque paragraphe du cadre.
#: LA TABLE EST EXPLICITE, parce qu'une règle déduite du numéro se tromperait :
#: 5.4.1 est une exigence de documentation pour le fournisseur et une exigence
#: de mise en œuvre pour le déployeur.
PARTS_EN18229 = {
    "calibration": ("scenarios", "delai", "selection", "impossibilite",
                    "surcharge", "categories", "deploy_conditions"),
    "mesures": ("retro_interface", "retro_parametres", "alerte_conception",
                "alerte_exigences", "continue_generales", "continue_ihm",
                "continue_fonctionnalite", "biais_conception",
                "biais_deployeur", "interpretation", "competences_deployeur",
                "fonctions", "negligence", "ecrasement", "retour", "etat_sur",
                "rbi_prevention", "rbi_statuts", "rbi_informations",
                "rbi_interface", "rbi_entrees", "rbi_independance",
                "rbi_deployeur", "deploy_mise_en_oeuvre"),
    "preuves": ("revue_affectations", "retro_verif", "continue_verif",
                "biais_tests", "comportement_apres", "entrainement",
                "deploy_specification", "deploy_residuel",
                "deploy_notifications", "deploy_verification",
                "rbi_documentation", "rbi_competences", "notice",
                "doc_technique", "notice_recue"),
}


def _lire_en18229_3(ev, dec=None):
    """Les trois parts de la supervision humaine, lues sur le rôle qui commande.

    LE RÔLE QUI COMMANDE EST LE PLUS FAIBLE DES DEUX, et c'est lui qu'on lit :
    agréger les deux questionnaires ferait remonter le côté tenu par-dessus le
    côté défaillant, exactement le mensonge que le moteur refuse.

    LA RÉSERVE EST PERMANENTE : ce projet de norme n'est pas encore cité au
    Journal officiel, donc aucune réponse ne peut ouvrir une présomption de
    conformité."""
    if not ev or not ev.get("ok"):
        return None, []
    import en18229_3 as _en
    role = ev.get("role_commande") or "fournisseur"
    reponses = ((dec or {}).get(role)
                if isinstance((dec or {}).get(role), dict) else {})
    exs = {e["cle"]: e for e in _en.applicables(
        role, bool(ev.get("rbi")),
        (dec or {}).get("notifications_fournisseur", True) is not False)}
    parts = {}
    for part, cles in PARTS_EN18229.items():
        retenues = [exs[c] for c in cles if c in exs]
        if not retenues:
            parts[part] = None
            continue
        poids = sum(x["poids"] for x in retenues)
        acquis = sum((_en._valeur(reponses.get(x["cle"])) or 0.0) * x["poids"]
                     for x in retenues)
        parts[part] = _pc(acquis, poids)
    #  LE SIGNAL DU VERROU SE CALCULE, IL NE SE DÉCLARE PAS. C'est le moteur
    #  qui dit si un scénario ne tient pas son délai : la carte du taux ne
    #  recompte rien, elle lit.
    signaux = ["presomption"]
    if (ev.get("scenarios_casses") or 0) > 0:
        signaux.append("scenario_sans_intervention")
    return parts, signaux


def _lire_en18286(ev, dec=None):
    """Les cinq parts du SMQ de l'article 17, telles que le moteur les rend.

    ON NE RECALCULE RIEN ICI. Le moteur a déjà appliqué le plafond de la
    charge de preuve du 4.4.3.2.2 ; le recomposer ferait DEUX vérités sur le
    même nombre, et c'est le défaut que ce fichier existe pour éviter.

    HORS CHAMP, IL N'Y A PAS DE TAUX. Le signal part, et `taux_norme` rend
    « — » avec sa raison plutôt qu'un zéro qui se lirait comme un constat.
    """
    if not ev or not ev.get("ok"):
        return None, []
    champ = ev.get("applicable") or {}
    if champ.get("ok") is False:
        return None, ["hors_champ"]
    signaux = [r["cle"] for r in (ev.get("reserves") or [])]
    #  LE PLAFOND EST DÉJÀ DANS LES PARTS. Le moteur rend `parts` plafonnées
    #  et `parts_brutes` à côté ; on lit les premières, et on ne rejoue pas
    #  le verrou ici — `conformite` le compterait une seconde fois, et son
    #  arithmétique de verrou (qui RETIRE une part entière) ne rendrait pas
    #  le même nombre que le moteur (qui la DEMI-COMPTE).
    if (ev.get("score") or {}).get("verrous"):
        signaux.append("charge_de_preuve")
    return dict(ev.get("parts") or {}), signaux


def _lire_ocde(ev, dec=None):
    """Les six parts de la diligence, telles que le moteur les rend.

    ON NE RECALCULE RIEN ICI. Le moteur a déjà posé ses trois plafonds SUR
    LES PARTS — et c'est pour cette raison qu'il les y a posés : un plafond
    laissé sur le seul total ne serait jamais arrivé jusqu'ici, et l'indice
    afficherait un chiffre plus haut que l'écran du module.

    IL N'Y A PAS DE HORS-CHAMP. Ce guide n'écarte personne : toute entreprise
    de la chaîne de valeur de l'IA est attendue sur la diligence, les PME
    comprises. Tant que les groupes ne sont pas déclarés, il n'y a pas de
    taux — mais ce n'est pas un « sans objet », c'est une question sans
    réponse, et `taux_norme` rend « — ».
    """
    if not ev or not ev.get("ok"):
        return None, []
    if (ev.get("applicable") or {}).get("ok") is not True:
        return None, []
    signaux = [r["cle"] for r in (ev.get("reserves") or [])]
    return dict(ev.get("parts") or {}), signaux


LECTEURS = {
    "ocde": _lire_ocde,
    "en18286": _lire_en18286,
    "iso42001": _lire_iso42001, "iso27001": _lire_iso27001,
    "nis2": _lire_nis2, "cra": _lire_cra, "nist_ai_rmf": _lire_nist,
    "owasp_llm": _lire_owasp, "ia_act": _lire_ia_act, "rgpd": _lire_rgpd,
    "nist_800_53": _lire_nist_800_53, "nist_800_82": _lire_nist_800_82,
    "dora": _lire_dora, "en18229_3": _lire_en18229_3,
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

    so = SANS_OBJET.get(cle)
    if parts is None and so and so["cle"] in signaux:
        # RENSEIGNÉE, ET SANS TAUX. La qualification a été faite — c'est elle
        # qui écarte la norme. « — » y dirait « pas encore regardé », ce qui
        # serait faux ; « 0 % » dirait « rien de fait », ce qui l'est aussi.
        return {"ok": True, "cle": cle, "nom": norme["nom"],
                "texte": norme["texte"],
                "nature": norme["nature"], "nature_nom": nature["nom"],
                "taux": None, "brut": None, "plafond": None,
                "composants": [dict(c, taux=None, renseigne=False)
                               for c in composition],
                "verrous": [], "reserves": [], "renseigne": True,
                "sans_objet": True,
                "mesure": norme["mesure"], "panneau": norme["panneau"],
                "taux_dit": nature["taux_dit"], "dit": so["dit"]}

    if parts is None:
        # UN REFUS N'EST PAS UN SILENCE. Quand le module refuse d'évaluer ce
        # que l'écran lui a transmis, dire « rien n'a été évalué » ferait
        # croire à qui vient de remplir trois écrans que rien n'est parti.
        motif = ((evaluation or {}).get("motif")
                 if isinstance(evaluation, dict) and not evaluation.get("ok")
                 else None)
        return {"ok": True, "cle": cle, "nom": norme["nom"],
                "nature": norme["nature"], "nature_nom": nature["nom"],
                "taux": None, "brut": None, "plafond": None,
                "composants": [dict(c, taux=None, renseigne=False)
                               for c in composition],
                "verrous": [], "reserves": [], "renseigne": False,
                "mesure": norme["mesure"], "panneau": norme["panneau"],
                "taux_dit": nature["taux_dit"],
                "dit": ("Le module refuse d'évaluer la déclaration de son "
                        "écran (%s) : le rail de cet écran nomme ce qui "
                        "manque." % motif) if motif else
                       "Rien n'a encore été évalué sur cette norme."}

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
    # LES ÉTATS LUS ICI SONT CEUX QUE LE PROFIL A PLAFONNÉS, quand il y en
    # a. Relire la déclaration brute aurait fait disparaître du plan
    # exactement les catégories que le profil vient de faire tomber : le
    # taux aurait baissé sans qu'aucune action ne dise pourquoi.
    plafonnes = ev.get("etats_plafonnes")
    etats = plafonnes if isinstance(plafonnes, dict) else _nist_declaration(dec)[0]
    par_le_profil = {m["categorie"] for m in (ev.get("plafonds_du_profil") or ())}
    out = []
    for cat in _k.CATEGORIES:
        e = etats.get(cat["cle"])
        if e in ("prouve", "sans_objet"):
            continue
        out.append(_ec((cat["fonction"] or "").lower(), cat["cle"],
                       cat.get("nom"),
                       "nist · profil IA générative"
                       if cat["cle"] in par_le_profil
                       else "nist · " + cat["fonction"],
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


def _ecarts_en18229_3(ev, dec=None):
    """Un paragraphe non tenu est un écart — et un SCÉNARIO dont la mesure ne
    tient pas le délai en est un autre, d'une nature différente.

    LES DEUX SE DISTINGUENT AU PLAN, et c'est ce qui le rend utilisable :
    combler le premier se fait sur l'écran du cadre ; combler le second
    demande de relever la catégorie de mesure ou de consigner l'impossibilité
    technique au dossier de gestion des risques. Les confondre ferait écrire
    « répondez à la question » là où il faut refaire une analyse de risque."""
    if not ev or not ev.get("ok"):
        return []
    import en18229_3 as _en
    role = ev.get("role_commande") or "fournisseur"
    reponses = ((dec or {}).get(role)
                if isinstance((dec or {}).get(role), dict) else {})
    out = []
    #  LE SCÉNARIO CASSÉ PASSE DEVANT : c'est le défaut que la norme refuse
    #  nommément, et il plafonne le taux.
    for sc in (dec or {}).get("scenarios") or []:
        if not isinstance(sc, dict):
            continue
        r = _en.scenario(sc)
        if r["etat"] in ("tient", "impossible_consignee"):
            continue
        out.append(_ec("calibration", "scenario",
                       "Scénario « %s » — %s"
                       % (r["nom"] or "sans nom",
                          _en.ETATS_SCENARIO[r["etat"]]["nom"]),
                       "en18229 · scénarios de risque", "5.2.2"))
    part_de = {c: part for part, cles in PARTS_EN18229.items() for c in cles}
    for ex in _en.applicables(role, bool(ev.get("rbi")),
                              (dec or {}).get("notifications_fournisseur",
                                              True) is not False):
        if _en._valeur(reponses.get(ex["cle"])) == 1.0:
            continue
        out.append(_ec(part_de.get(ex["cle"], "mesures"), ex["cle"],
                       "%s — %s" % (ex["clause"], ex["titre"]),
                       "en18229 · %s" % _en.ROLES[role]["nom"].lower(),
                       ex["clause"]))
    return out


def _ecarts_en18286(ev, dec=None):
    """Ce que le plan du module nomme déjà — repris tel quel.

    LE PLAN DU MOTEUR EST DÉJÀ ORDONNÉ, et il met en tête ce qui PLAFONNE :
    une exigence essentielle traitée par « autre solution » sans sa preuve
    objective. Le réordonner ici ferait remonter un paragraphe du chapitre 10
    devant le verrou qui l'empêche de compter.
    """
    if not ev or not ev.get("ok"):
        return []
    import en18286 as _en
    if (ev.get("applicable") or {}).get("ok") is False:
        return []
    out = []
    for e in _en.plan(dec or {}):
        comp = e.get("part") or "strategie"
        out.append(_ec(comp, e["cle"], e["quoi"], e["ou"], e.get("article")))
    return out


#: OÙ TOMBE CHAQUE ACTION DU PLAN DE L'OCDE. Les trois premières portent sur
#: la qualification, qui vit dans l'étape 2 : c'est là que le document range
#: l'implication (2.3) et la priorisation (2.4).
_OCDE_COMPOSANT = {"groupes": "identifier", "implication": "identifier",
                   "priorisation": "identifier",
                   "justifier_priorisation": "identifier"}


def _ecarts_ocde(ev, dec=None):
    """Ce que le plan du module nomme déjà — repris tel quel, dans son ordre.

    LE PLAN DU MOTEUR EST DÉJÀ ORDONNÉ, et il met en tête ce qui DÉBLOQUE :
    les groupes, puis l'implication, puis ce que l'implication rend non
    négociable. Le réordonner ici ferait remonter l'étape 5 devant la
    question qui empêche tout le reste de compter.
    """
    if not ev or not ev.get("ok"):
        return []
    import ocde_ia as _o
    if (ev.get("applicable") or {}).get("ok") is not True:
        return []
    out = []
    for e in _o.plan(dec or {}, limite=24)["actions"]:
        comp = _OCDE_COMPOSANT.get(e["cle"])
        if comp is None and e["cle"].startswith("etape_"):
            comp = e["cle"][len("etape_"):]
        out.append(_ec(comp or "identifier", e["cle"], e["quoi"], e["ou"]))
    return out


ECARTEURS = {
    "ocde": _ecarts_ocde,
    "en18286": _ecarts_en18286,
    "dora": _ecarts_dora,
    "iso42001": _ecarts_iso42001, "iso27001": _ecarts_iso27001,
    "nis2": _ecarts_nis2, "cra": _ecarts_cra, "nist_ai_rmf": _ecarts_nist,
    "owasp_llm": _ecarts_owasp, "ia_act": _ecarts_ia_act, "rgpd": _ecarts_rgpd,
    "nist_800_53": _ecarts_nist_800_53, "nist_800_82": _ecarts_nist_800_82,
    "en18229_3": _ecarts_en18229_3,
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
#  ÉVALUER CHAQUE NORME — UNE TABLE, POUR QUE LA GARDE PUISSE LA COMPTER
# ══════════════════════════════════════════════════════════════════════════
#
# MESURÉ AVANT CETTE TABLE : les deux référentiels NIST de sécurité des
# systèmes industriels avaient un lecteur, un extracteur d'écarts, une
# composition — et AUCUNE évaluation. Leurs cartes restaient « — » quoi que
# l'on déclare. Le défaut ne se voyait pas parce que les évaluations
# étaient écrites en dur dans le corps de la fonction ; en table, la garde
# de ce module vérifie que chaque norme de la grille en a une.
#
# Les imports restent locaux : ces modules importent beaucoup, et le taux
# n'en a besoin qu'au moment d'évaluer.

def _ev_ia_act(dec, d):
    return evaluer_audit_ia_act(dec)


def _ev_cra(dec, d):
    import cra as _cra
    return _cra.evaluer_produit(dec)


def _ev_iso42001(dec, d):
    import iso42001 as _i42
    return _i42.evaluer(dec)


def _ev_iso27001(dec, d):
    import iso27001 as _i27
    return _i27.evaluer(dec)


def _ev_dora(dec, d):
    import dora as _dora
    return _dora.evaluer(dec)


def _ev_nis2(dec, d):
    import nis2 as _n2
    return _n2.evaluer(dec)


def _ev_rgpd(dec, d):
    return dict(dec, ok=True)


def _ev_nist_ai_rmf(dec, d):
    """Le cadre, puis le profil qui le plafonne — dans cet ordre.

    LE PROFIL EST ÉVALUÉ AVANT D'ÊTRE APPLIQUÉ. S'il refuse la déclaration —
    un code d'action qui n'existe pas, un état inconnu —, on ne plafonne
    rien et on rend le refus : plafonner sur une saisie que le module
    n'accepte pas reviendrait à baisser un taux sur la foi de données dont
    on vient de dire qu'on ne les comprend pas.
    """
    import nist_ai_rmf as _nist
    import nist_genai as _profil
    etats, prof = _nist_declaration(dec)
    lu = _profil.analyse(prof, etats)
    if not lu.get("ok"):
        return {"ok": False, "motif": "profil_genai_illisible",
                "detail": lu.get("detail"), "profil_motif": lu.get("motif")}
    plafonnes, mouvements = _profil.etats_du_profil(etats, prof)
    ev = _nist.evaluer(plafonnes)
    if not ev.get("ok"):
        return ev
    ev["profil_genai"] = lu
    ev["etats_plafonnes"] = plafonnes
    ev["plafonds_du_profil"] = mouvements
    return ev


def _ev_owasp_llm(dec, d):
    import owasp_llm as _ow
    return _ow.evaluer(dec)


def _ev_nist_800_53(dec, d):
    import nist_800_53 as _n53
    return _n53.evaluer(dec.get("socle"), dec.get("etats"))


def _ev_nist_800_82(dec, d):
    # LA SURCHARGE SE MESURE CONTRE SON SOCLE, qui voyage avec elle : le
    # moteur ramène chaque axe à la plus faible des familles 800-53 qu'il
    # taille, et sans elles il ne saurait pas sur quoi l'axe repose.
    import nist_800_82 as _n82
    return _n82.evaluer(dec.get("etats"), dec.get("etats_800_53"))


def _ev_en18229_3(dec, d):
    # LES DEUX RÔLES VOYAGENT ENSEMBLE, et le moteur retient le plus faible :
    # un organisme qui conçoit ET exploite porte deux jeux d'obligations, et
    # moyenner les deux cacherait le côté défaillant.
    import en18229_3 as _en
    return _en.evaluer(dec)


def _ev_en18286(dec, d):
    import en18286 as _en
    return _en.evaluer(dec)


def _ev_ocde(dec, d):
    import ocde_ia as _o
    return _o.evaluer(dec)


EVALUATEURS = {
    "ocde": _ev_ocde,
    "en18286": _ev_en18286,
    "ia_act": _ev_ia_act, "cra": _ev_cra, "iso42001": _ev_iso42001,
    "iso27001": _ev_iso27001, "dora": _ev_dora, "nis2": _ev_nis2,
    "rgpd": _ev_rgpd, "nist_ai_rmf": _ev_nist_ai_rmf,
    "owasp_llm": _ev_owasp_llm, "nist_800_53": _ev_nist_800_53,
    "nist_800_82": _ev_nist_800_82, "en18229_3": _ev_en18229_3,
}


def _evaluer(cle, dec, d):
    """L'évaluation d'une norme, ou None si rien n'est déclaré.

    UNE DÉCLARATION ABSENTE NE S'ÉVALUE PAS. Plusieurs moteurs rendent
    ok=True sur rien — l'audit IA Act, le NIST AI RMF, le Top 10 OWASP — et
    certains rendent 0 % : c'est la DÉCLARATION qui dit si le sujet a été
    ouvert, pas le résultat.

    UNE DÉCLARATION ILLISIBLE NE FAIT PAS TOMBER LES DIX AUTRES. Mesuré :
    l'enveloppe `{"etats": …}` d'un écran, passée telle quelle au moteur
    NIST AI RMF, levait une TypeError — et l'écran du taux perdait ses onze
    cartes pour une seule déclaration de travers. Elle rend désormais un
    refus, que la carte de CETTE norme affiche."""
    if not dec or not isinstance(dec, dict):
        return None
    f = EVALUATEURS.get(cle)
    if not f:
        return None
    try:
        return f(dec, d)
    except (TypeError, ValueError, AttributeError, KeyError):
        return {"ok": False, "motif": "declaration_illisible"}


# ══════════════════════════════════════════════════════════════════════════
#  CE QUE LES ÉCRANS TIENNENT → CE QUE CHAQUE MOTEUR ATTEND
# ══════════════════════════════════════════════════════════════════════════
#
# LE DÉFAUT QUI A FAIT ÉCRIRE CETTE SECTION, MESURÉ DANS UN NAVIGATEUR. Le
# taux lisait `window.CONF_DECL`, que quatre modules sur onze n'écrivaient
# jamais ; deux autres l'écrivaient sans qu'il soit lu, et DORA n'y figurait
# pas. Qui remplissait NIS 2 jusqu'à voir trois blocs verts dans le rail
# trouvait, sur l'écran du taux, « — ». Le rail et le taux lisaient deux
# collectes différentes : ils ne pouvaient que se contredire.
#
# DÉSORMAIS UNE SEULE COLLECTE. L'écran envoie au taux ce qu'il envoie au
# rail — les mêmes objets, rassemblés par les mêmes fonctions —, et la
# traduction vers le format de chaque moteur se fait ICI, une fois, en
# Python, là où des règles peuvent la mesurer.
#
# UN ÉCRAN SANS AUCUNE RÉPONSE NE DEVIENT PAS UNE DÉCLARATION. Les moteurs
# rendent 0 % sur un questionnaire vide, et le moteur NIS 2 rend même
# « hors champ » sur un formulaire vierge : traduire un écran vide, ce
# serait afficher un zéro — ou un verdict — que personne n'a déclaré.

#: LE NOM QUE QUATRE MOTEURS EXIGENT, ET QU'AUCUN TAUX NE LIT. ISO 27001,
#: ISO 42001, NIS 2 et le CRA refusent d'évaluer sans nom, parce que leur
#: restitution complète est un document nommé. Le taux n'en affiche rien, et
#: une règle vérifie que deux noms différents rendent les mêmes taux.
NOM_INERTE = "Déclaration des écrans Sentinel"

#: LE VOCABULAIRE DE L'ÉCRAN D'AUDIT IA ACT, et celui du moteur.
#: « À réaliser » est une RÉPONSE : le point est déclaré non tenu. Un point
#: jamais touché (« none ») n'en est pas une : il n'est pas traduit, et le
#: moteur le compte « non renseigné » — non tenu lui aussi, mais nommé comme
#: tel. Les deux se confondaient ; l'écran demande désormais une réponse.
AUDIT_ECRAN = {"done": "tenu", "partial": "partiel", "na": "sans_objet",
               "todo": "absent"}


def _rempli(v):
    """Une RÉPONSE, et pas l'état initial d'un écran : un texte non blanc, un
    nombre, un vrai, une collection non vide."""
    if v is None or v is False:
        return False
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, (dict, list, tuple)):
        return bool(v)
    return True


def _dict_de(v, cle):
    x = v.get(cle)
    return dict(x) if isinstance(x, dict) else {}


def _de_iso27001(v, e):
    criteres = _dict_de(v, "criteres")
    # LE SEUIL N'EST PAS UNE RÉPONSE : l'écran l'initialise à 6. Les deux
    # dates, elles, ne se remplissent que si quelqu'un les écrit.
    if not any(_rempli(x) for x in (
            v.get("perimetre"), criteres.get("etabli_le"),
            criteres.get("apprecie_le"), v.get("risques"), v.get("mesures"),
            v.get("articles"))):
        return None
    risques = v.get("risques") if isinstance(v.get("risques"), list) else []
    return {"nom": NOM_INERTE, "perimetre": v.get("perimetre") or "",
            "criteres": criteres, "risques": risques,
            "mesures": _dict_de(v, "mesures"),
            "articles": _dict_de(v, "articles")}


def _de_iso42001(v, e):
    if not (_rempli(v.get("mesures")) or _rempli(v.get("articles"))):
        return None
    return {"nom": NOM_INERTE, "mesures": _dict_de(v, "mesures"),
            "articles": _dict_de(v, "articles")}


#: CE QUE L'ÉCRAN NIS 2 TIENT DE LA QUALIFICATION. Le chiffre d'affaires de
#: l'exposition et les vingt objectifs du calque de l'ANSSI n'y sont pas : le
#: premier chiffre une sanction, les seconds ont leur propre taux — de
#: PRÉPARATION, séparé. La traduction ne recopie donc que ce qui suit, les
#: portes de l'article 2, les mesures et la gouvernance.
NIS2_QUALIFICATION = ("secteur", "effectif", "ca_eur", "bilan_eur")


def _de_nis2(v, e):
    import parcours_normes as _pn
    portes = {k: True for k in _pn.NIS2_PORTES if v.get(k)}
    if not (any(_rempli(v.get(k)) for k in NIS2_QUALIFICATION) or portes
            or _rempli(v.get("mesures")) or _rempli(v.get("gouvernance"))):
        return None
    d = {k: v.get(k) for k in NIS2_QUALIFICATION}
    d.update(portes)
    d.update(nom=NOM_INERTE, mesures=_dict_de(v, "mesures"),
             gouvernance=_dict_de(v, "gouvernance"))
    return d


def _de_cra(v, e):
    """L'analyse d'écart de l'écran, et le rôle QU'IL A QUALIFIÉ.

    LE RÔLE SE LIT SUR LES RÉPONSES, COMME DANS LE RAIL. Sans réponse, le
    moteur de qualification rend « distributeur » par défaut — et le taux
    du produit, lui, suppose « fabricant ». Transmettre l'un ou l'autre
    ferait disparaître la réserve qui dit que le rôle n'est pas qualifié."""
    import cra as _cra
    import parcours_normes as _pn
    role = _dict_de(v, "role")
    repondu = any(role.get(k) for k in _pn.CRA_ROLE_CLES)
    nommes = [p for p in (v.get("produits") or [])
              if isinstance(p, dict) and str(p.get("nom") or "").strip()]
    ecarts = _dict_de(v, "ecarts")
    if not (repondu or nommes or ecarts):
        return None
    return {"nom": NOM_INERTE, "ecarts": ecarts,
            "role": (_cra.qualifier_role(role)["role"]["cle"]
                     if repondu else None)}


def _de_dora(v, e):
    """La déclaration que le module DORA assemble lui-même, telle quelle.

    SON ÉCRAN L'A DÉJÀ AU FORMAT DU MOTEUR : `doraDeclaration()` recolle les
    six écrans en un seul objet, pour son propre rail. Le taux lit ce
    même objet."""
    contrats = [c for c in (v.get("contrats") or []) if isinstance(c, dict)]
    if not (_rempli(v.get("entite")) or _rempli(v.get("etats"))
            or any(_rempli(c.get("clauses"))
                   or c.get("fonction_critique") is not None
                   for c in contrats)):
        return None
    return dict(v)


def _de_etats(v, e):
    etats = _dict_de(v, "etats")
    return etats or None


def _de_nist_ai_rmf(v, e):
    """Les états du cadre ET la déclaration de profil, en une seule pièce.

    LES DEUX VOYAGENT ENSEMBLE PARCE QUE LE SECOND COMMANDE LE PREMIER. Les
    séparer aurait laissé arriver un socle sans son profil — et un socle
    sans profil se lit « non génératif », c'est-à-dire la réponse qui ne
    plafonne rien.
    """
    etats = _dict_de(v, "etats")
    profil = v.get("profil") if isinstance(v.get("profil"), dict) else None
    if not (etats or profil):
        return None
    return {"etats": etats or {}, "profil": profil or {}}


def _de_nist_800_53(v, e):
    etats = _dict_de(v, "etats")
    socle = v.get("socle") or None
    if not (socle or etats):
        return None
    return {"socle": socle, "etats": etats}


def _de_nist_800_82(v, e):
    etats = _dict_de(v, "etats")
    if not etats:
        return None
    socle53 = e.get("nist_800_53") if isinstance(e.get("nist_800_53"), dict) \
        else {}
    return {"etats": etats, "etats_800_53": _dict_de(socle53, "etats")}


def _pourcentage(x):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return 0
    return max(0, min(100, int(round(x))))


def _de_rgpd(v, e):
    """Les quatre briques, telles que le tableau de bord RGPD les calcule.

    LE REGISTRE N'EST PAS RECALCULÉ ICI. L'écran « Conformité RGPD » en
    affiche déjà le pourcentage ; le refaire en Python donnerait deux
    arrondis pour le même nombre. Ce qui se décide ici, c'est seulement si
    le sujet a été ouvert : un registre sans traitement et trois briques à
    zéro ne sont pas un RGPD « à 0 % », ils sont un RGPD pas encore regardé.
    """
    traitements = [t for t in (v.get("traitements") or [])
                   if isinstance(t, dict)]
    b = _dict_de(v, "briques")
    briques = {c["cle"]: _pourcentage(b.get(c["cle"]))
               for c in COMPOSITIONS["rgpd"]}
    if not traitements and not any(briques.values()):
        return None
    return {"briques": briques}


def _de_ia_act(v, e):
    audit = _dict_de(v, "audit")
    reponses = {k: AUDIT_ECRAN[x] for k, x in audit.items() if x in AUDIT_ECRAN}
    return reponses or None


def _de_en18229_3(v, e):
    """L'écran de la supervision humaine → ce que son moteur attend.

    UN ÉCRAN SANS RÔLE DÉCLARÉ N'EST PAS UNE DÉCLARATION. Le moteur rendrait
    « aucun rôle déclaré », et la carte du taux afficherait un refus là où
    « — » est la vérité : le sujet n'a pas été ouvert."""
    roles = {r: _dict_de(v, r) for r in ("fournisseur", "deployeur")}
    if not any(roles.values()):
        return None
    out = {"rbi": bool(v.get("rbi")),
           "scenarios": v.get("scenarios") if isinstance(v.get("scenarios"), list)
           else []}
    if v.get("notifications_fournisseur") is not None:
        out["notifications_fournisseur"] = bool(v.get("notifications_fournisseur"))
    for r, rep in roles.items():
        if rep:
            out[r] = rep
    return out


def _de_en18286(v, e):
    """L'écran du SMQ de l'article 17 → ce que son moteur attend.

    LA QUALIFICATION SUFFIT À FAIRE UNE DÉCLARATION, et c'est voulu : un
    fournisseur qui vient de se déclarer hors champ a RÉPONDU. Sa carte doit
    dire « sans objet », pas « — ». À l'inverse, un écran où rien n'est
    touché reste absent, et le taux rend « — ».
    """
    qual = _dict_de(v, "qualification")
    reponses = _dict_de(v, "reponses")
    strat = v.get("strategie") if isinstance(v.get("strategie"), dict) else {}
    certifie = _dict_de(v, "certifie")
    if not (qual or reponses or strat or certifie):
        return None
    return {"qualification": qual, "reponses": reponses,
            "strategie": strat, "certifie": certifie}


def _de_ocde(v, e):
    """L'écran de la diligence OCDE → ce que son moteur attend.

    LA QUALIFICATION SUFFIT À FAIRE UNE DÉCLARATION : un organisme qui vient
    de déclarer ses groupes et son implication a RÉPONDU, même sans une seule
    réponse au questionnaire — et sa carte doit le montrer. À l'inverse, un
    écran où rien n'est touché reste absent, et le taux rend « — ».
    """
    qual = _dict_de(v, "qualification")
    reponses = _dict_de(v, "reponses")
    prio = v.get("priorisation") if isinstance(v.get("priorisation"), list) \
        else []
    if not (qual or reponses or prio):
        return None
    return {"qualification": qual, "reponses": reponses,
            "priorisation": prio}


TRADUCTEURS = {
    "ocde": _de_ocde,
    "en18286": _de_en18286,
    "ia_act": _de_ia_act, "cra": _de_cra, "iso42001": _de_iso42001,
    "iso27001": _de_iso27001, "dora": _de_dora, "nis2": _de_nis2,
    "rgpd": _de_rgpd, "nist_ai_rmf": _de_nist_ai_rmf, "owasp_llm": _de_etats,
    "nist_800_53": _de_nist_800_53, "nist_800_82": _de_nist_800_82,
    "en18229_3": _de_en18229_3,
}


def depuis_les_ecrans(ecrans):
    """Les déclarations des écrans → celles que `etat_des_lieux` attend.

    `ecrans` porte, par clé de norme, l'objet que l'écran envoie aussi au
    rail. Une norme dont l'écran ne porte aucune réponse est ABSENTE du
    résultat : son taux sera « — », jamais 0."""
    e = ecrans if isinstance(ecrans, dict) else {}
    out = {}
    for cle, traduire in TRADUCTEURS.items():
        v = e.get(cle)
        if not isinstance(v, dict):
            continue
        t = traduire(v, e)
        if t is not None:
            out[cle] = t
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

    etats, ecarts = [], {}
    for norme in NORMES:
        cle = norme["cle"]
        dec = d.get(cle)
        ev = _evaluer(cle, dec, d)
        et = taux_norme(cle, ev, dec)
        extracteur = ECARTEURS.get(cle)
        # UNE NORME SANS OBJET N'A PAS D'ÉCARTS : le plan ne vend pas un
        # chantier à qui la qualification déclarée l'a épargné.
        liste = (extracteur(ev, dec)
                 if (extracteur and ev and not et.get("sans_objet")) else [])
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

def _verifier_couleurs():
    """LA PALETTE SE GARDE COMME LE RESTE — par recomptage, pas par confiance.

    TROIS CHOSES PEUVENT SE DÉFAIRE EN SILENCE : une norme ajoutée sans
    couleur, deux normes qui finissent par partager la même teinte, et un
    ordre de barre qui cite une clé disparue. Les trois se voient à l'écran
    comme un détail ; aucune ne se voit dans le code."""
    f = []
    for n in NORMES:
        if n["cle"] not in COULEURS:
            f.append("la norme %s n'a pas de couleur" % n["cle"])
    for cle in COULEURS:
        if cle not in NORMES_PAR_CLE:
            f.append("la couleur %s ne vise aucune norme" % cle)
    vues = {}
    for cle, coul in COULEURS.items():
        c = coul.upper()
        if c in vues:
            f.append("%s et %s partagent la couleur %s" % (vues[c], cle, c))
        vues[c] = cle
        if len(c) != 7 or not c.startswith("#"):
            f.append("la couleur de %s n'est pas un hexadécimal à six "
                     "chiffres : %r" % (cle, coul))
    for cle in ORDRE_BARRE:
        if cle not in COULEURS:
            f.append("l'ordre de barre cite %s, qui n'a pas de couleur" % cle)
    return tuple(f)


def _verifier():
    fautes = list(_verifier_couleurs())

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
        # LES DEUX MAILLONS QUI MANQUAIENT, ET QUI NE SE VOYAIENT PAS : un
        # lecteur sans évaluation lit toujours None, et une évaluation sans
        # traducteur n'est jamais appelée depuis l'écran. Sept cartes sur
        # onze restaient « — » quoi que l'on remplisse.
        if n["cle"] not in EVALUATEURS:
            fautes.append("%s : aucune évaluation — sa carte resterait "
                          "« — » quoi que l'on déclare" % n["cle"])
        if n["cle"] not in TRADUCTEURS:
            fautes.append("%s : aucun traducteur d'écran — le taux ne "
                          "verrait jamais ce que son écran déclare"
                          % n["cle"])
        if not n.get("panneau"):
            fautes.append("%s : aucun panneau Sentinel. Un taux qui ne mène "
                          "pas à l'écran où on le corrige est un reproche, "
                          "pas un outil." % n["cle"])
        if not n.get("mesure"):
            fautes.append("%s : ne dit pas ce qu'il mesure" % n["cle"])

    for cle, so in SANS_OBJET.items():
        if cle not in COMPOSITIONS:
            fautes.append("« sans objet » sur %s, qui n'a pas de composition"
                          % cle)
        deja = ({v["cle"] for v in VERROUS.get(cle, ())}
                | {r["cle"] for r in RESERVES.get(cle, ())})
        if so["cle"] in deja:
            fautes.append("%s : %s est à la fois « sans objet » et verrou ou "
                          "réserve — une norme écartée n'a pas de taux à "
                          "plafonner ni à mettre en doute" % (cle, so["cle"]))
        if not so.get("dit") or not so.get("ou"):
            fautes.append("%s : « sans objet » sans dire pourquoi ni où cela "
                          "se revoit" % cle)

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
        # UN VERROU N'EXISTE QUE LÀ OÙ UN TIERS REFUSE D'ALLER PLUS LOIN —
        # OU LÀ OÙ L'ARITHMÉTIQUE DU MODULE PROUVE QUE LA PRÉTENTION EST
        # FAUSSE. C'est la ligne qui le sépare d'une réserve, et elle est
        # vérifiable de deux façons : les normes certifiables ont un auditeur
        # qui peut s'arrêter à la porte ; ailleurs, un plafond n'est légitime
        # que si un CALCUL le fonde, et le verrou doit alors le déclarer.
        #
        # LE CAS QUI A FAIT ÉCRIRE CETTE SECONDE PORTE : prEN 18229-3 n'a pas
        # d'auditeur — le projet n'est même pas cité au Journal officiel — mais
        # un scénario dont la latence d'intervention dépasse son délai de
        # réaction ne peut PAS être supervisé, et aucune réponse ne rend cela
        # faux. Laisser un taux monter dessus serait le mensonge que la norme
        # refuse nommément. Ce qui reste interdit : plafonner « parce que c'est
        # grave ». La sévérité inventée se déclare dans RESERVES.
        if NORMES_PAR_CLE.get(cle, {}).get("nature") != "certifiable":
            sans_calcul = [v["cle"] for v in verrous
                           if v.get("fonde_sur") != "arithmetique"]
            if sans_calcul:
                fautes.append(
                    "%s porte un verrou sans être certifiable et sans qu'un "
                    "calcul le fonde (%s). Un verrou plafonne un taux parce "
                    "qu'un tiers refuse de poursuivre, ou parce que "
                    "l'arithmétique du module prouve la prétention fausse — et "
                    "il doit alors porter fonde_sur=\"arithmetique\" et dire "
                    "quel calcul. Sinon ce n'est pas un verrou mais une "
                    "réserve, et elle se déclare dans RESERVES."
                    % (cle, ", ".join(sans_calcul)))
            for v in verrous:
                if v.get("fonde_sur") == "arithmetique" and not v.get("calcul"):
                    fautes.append(
                        "le verrou %s de %s se dit fondé sur un calcul sans "
                        "dire lequel" % (v["cle"], cle))
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
