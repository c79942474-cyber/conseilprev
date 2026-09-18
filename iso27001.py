# -*- coding: utf-8 -*-
"""ISO/IEC 27001:2022 — l'analyse de risque, et la conformité qui en découle.

═══════════════════════════════════════════════════════════════════════════
 AVERTISSEMENT DE DROIT D'AUTEUR — À LIRE AVANT DE MODIFIER CE MODULE
═══════════════════════════════════════════════════════════════════════════

ISO/IEC 27001:2022 EST PROTÉGÉE PAR LE DROIT D'AUTEUR (© ISO/IEC), exactement
comme ISO/IEC 42001:2023. Ce module cite donc, et seulement :

    · les NUMÉROS d'articles et de mesures (6.1.2, A.8.23…) ;
    · leurs TITRES, qui sont des désignations permettant de s'y référer.

TOUT LE RESTE — ce que chaque article demande, ce qu'il faut produire, ce qui
fait échouer un audit — EST RÉDIGÉ PAR LE CABINET. Aucune phrase normative
n'est reproduite. Une garde énumère les champs autorisés de la table des
mesures : y ajouter un champ pour « enrichir » une restitution empêche le
module de démarrer, avant que la contrefaçon n'atteigne une page servie.

ET LE QUESTIONNAIRE D'AUTO-ÉVALUATION QUI A SERVI DE POINT DE DÉPART EST
LUI AUSSI PROTÉGÉ : © BSI Group, réf. BSI/UK/820/SC/0316/EN/BLD. Ses
questions sont sa propriété. Aucune n'est reprise ici ; les questions de ce
module sont écrites par le cabinet, et portent sur la version en vigueur —
ce qui n'est pas le cas de celles du document d'origine.

═══════════════════════════════════════════════════════════════════════════
 LE FAIT QU'IL FAUT DIRE AVANT TOUS LES AUTRES
═══════════════════════════════════════════════════════════════════════════

    LE QUESTIONNAIRE FOURNI PORTE SUR ISO/IEC 27001:2013.
    CE N'EST PLUS LA NORME.

ISO/IEC 27001:2022 lui a succédé. Et le changement n'est pas cosmétique :
l'annexe A est passée de 114 mesures réparties en 14 chapitres (A.5 à A.18)
à 93 mesures réparties en 4 thèmes (A.5 à A.8), dont ONZE entièrement
nouvelles — renseignement sur les menaces, services en nuage, masquage des
données, prévention de la fuite de données, filtrage web, codage sécurisé…

Un organisme qui remplit aujourd'hui un questionnaire de 2016 conclut qu'il
est prêt, et découvre à l'audit qu'on lui demande onze mesures dont il n'a
jamais entendu parler, sur une numérotation qui n'existe plus.

═══════════════════════════════════════════════════════════════════════════
 LA DÉCISION QUI COMMANDE TOUTES LES AUTRES
═══════════════════════════════════════════════════════════════════════════

    QUI A ACCEPTÉ LE RISQUE RÉSIDUEL, ET QUAND L'A-T-IL ÉCRIT ?

L'article 6.1.3 e) demande l'approbation du plan de traitement ET
l'acceptation des risques résiduels PAR LES PROPRIÉTAIRES DES RISQUES. Pas
par le RSSI, pas par le consultant, pas par le comité de sécurité : par celui
qui porte l'activité exposée.

C'est la clause qui transforme un exercice technique en acte de direction, et
c'est celle qui manque le plus souvent : des registres de risques parfaits,
avec une colonne « propriétaire » remplie, et aucune trace datée d'une
acceptation. Le propriétaire est NOMMÉ, il n'a rien SIGNÉ — et l'auditeur
demande la signature, pas le nom.

    ET SON JUMEAU, À L'AUTRE BOUT : LES CRITÈRES D'ACCEPTATION SE FIXENT
    AVANT D'APPRÉCIER, pas après (art. 6.1.2 a). Les fixer après avoir vu
    les résultats donne un registre où tout est acceptable — et c'est
    invisible dans le document final, puisque seul l'ordre de rédaction
    distingue les deux.

═══════════════════════════════════════════════════════════════════════════
 CE QUE CE MODULE N'EST PAS
═══════════════════════════════════════════════════════════════════════════

CE N'EST PAS LE MÊME OBJET QUE LES QUATRE AUTRES CADRES DE SENTINEL :

    · le RGPD compte des TRAITEMENTS, qualifiés par leur finalité ;
    · l'IA Act compte des SYSTÈMES D'IA, qualifiés par leur usage ;
    · le CRA compte des PRODUITS, qualifiés par ce qu'ils SONT ;
    · NIS 2 compte des ENTITÉS, qualifiées par secteur et par taille ;
    · ISO 27001 compte des RISQUES sur des ACTIFS D'INFORMATION, à
      l'intérieur d'un PÉRIMÈTRE que l'organisme choisit lui-même.

Ce dernier point est le piège propre à 27001 : le périmètre se déclare, et
tout ce qui n'en est pas exclu par écrit sera audité. Un périmètre large
rassure le client et double la facture ; un périmètre étroit passe l'audit et
ne prouve rien à personne.

ET 27001 N'EST PAS 42001. 27001 protège l'INFORMATION ; 42001 gouverne l'IA.
La structure des articles 4 à 10 est la même — c'est la structure harmonisée
des normes de système de management —, mais les annexes A n'ont aucun
rapport : 93 mesures de sécurité d'un côté, 38 mesures de gouvernance de
l'IA de l'autre. Aucune des deux certifications n'emporte l'autre.
"""


# ═══════════════════════════════════════════════════════════════════════════
#  LES SOURCES — LA NORME, ET LE DOCUMENT QUI A SERVI DE POINT DE DÉPART
# ═══════════════════════════════════════════════════════════════════════════

SOURCE = {
    "titre": "ISO/IEC 27001:2022 — Sécurité de l'information, cybersécurité "
             "et protection de la vie privée — Systèmes de management de la "
             "sécurité de l'information — Exigences",
    "court": "ISO/IEC 27001:2022",
    "editeur": "ISO / IEC (JTC 1/SC 27)",
    "millesime": "2022-10",
    "url": "https://www.iso.org/standard/27001",
    "licence": "PROTÉGÉE PAR LE DROIT D'AUTEUR — © ISO/IEC. Aucune partie du "
               "texte normatif n'est reproduite ici : seuls les numéros et "
               "les titres d'articles et de mesures sont cités, et tout ce "
               "qui les décrit est rédigé par le cabinet.",
    "reproduction": False,
    "achat": "La mise en œuvre suppose de détenir le texte de la norme, qui "
             "s'achète auprès de l'ISO ou d'un organisme national de "
             "normalisation (AFNOR en France).",
    "certifiable": True,
    "lu_le": "2026-09-18",
}

# ── LE DOCUMENT FOURNI, ET CE QU'IL EST VRAIMENT ─────────────────────────
#
# POURQUOI IL EST DÉCLARÉ COMME UNE SOURCE À PART ENTIÈRE. Il a servi de
# point de départ, il appartient à un tiers, et il porte sur une version
# retirée. Les trois faits comptent, et aucun ne se devine à l'usage.
SOURCE_QUESTIONNAIRE = {
    "titre": "ISO/IEC 27001:2013 — Questionnaire d'auto-évaluation",
    "editeur": "BSI Group",
    "reference": "BSI/UK/820/SC/0316/EN/BLD",
    "millesime": "2016",
    "vise": "ISO/IEC 27001:2013",
    "licence": "© BSI Group. Document commercial d'un organisme de "
               "certification. Aucune de ses questions n'est reprise ici : "
               "les questions de ce module sont rédigées par le cabinet.",
    "reproduction": False,
    "reserve": "Ce questionnaire porte sur ISO/IEC 27001:2013, à laquelle "
               "ISO/IEC 27001:2022 a succédé. Le remplir aujourd'hui prépare "
               "contre une version retirée — et surtout contre une annexe A "
               "qui n'existe plus sous cette forme.",
}

# ── CE QUE LE MODULE NE SAIT PAS, ET LE DIT ──────────────────────────────
#
# LA DISCIPLINE : une date d'échéance qu'on n'a pas pu vérifier ne s'invente
# pas. Le réseau sortant de cet environnement ne joint ni iso.org, ni iaf.nu,
# ni cofrac.fr. Ce qui suit est donc annoncé comme À VÉRIFIER, et la
# restitution le répète — plutôt que de rendre une date qui se citerait en
# comité comme si elle était établie.
A_VERIFIER = (
    {"quoi": "La date de fin de la période de transition des certificats "
             "ISO/IEC 27001:2013 vers la version 2022",
     "ou": "IAF MD 26 et ses amendements, relayés par l'organisme "
           "d'accréditation national (COFRAC en France) et par l'organisme "
           "certificateur de l'organisme",
     "pourquoi": "Un certificat émis contre la version 2013 cesse d'être "
                 "valide à l'issue de cette période, quelle que soit sa date "
                 "d'expiration imprimée."},
    {"quoi": "L'état de l'amendement ISO/IEC 27001:2022/Amd 1 relatif au "
             "changement climatique (articles 4.1 et 4.2)",
     "ou": "Le texte acheté, ou le catalogue de l'organisme national de "
           "normalisation",
     "pourquoi": "Il ajoute une considération aux articles 4.1 et 4.2 sans "
                 "toucher à l'annexe A : l'ignorer est un écart d'audit "
                 "mineur, mais un écart."},
)


# ═══════════════════════════════════════════════════════════════════════════
#  LE MILLÉSIME — CE QUI A CHANGÉ ENTRE 2013 ET 2022
# ═══════════════════════════════════════════════════════════════════════════

MILLESIMES = {
    "2013": {"nom": "ISO/IEC 27001:2013", "mesures": 114, "groupes": 14,
             "libelle_groupes": "chapitres A.5 à A.18", "en_vigueur": False},
    "2022": {"nom": "ISO/IEC 27001:2022", "mesures": 93, "groupes": 4,
             "libelle_groupes": "thèmes A.5 à A.8", "en_vigueur": True},
}

# LES ONZE MESURES QUI N'EXISTAIENT PAS EN 2013. C'est le chiffre qui dit le
# reste à faire d'un organisme déjà certifié contre l'ancienne version : ni
# 93, ni 114, ni « tout » — onze.
NOUVELLES_2022 = ("A.5.7", "A.5.23", "A.5.30", "A.7.4", "A.8.9", "A.8.10",
                  "A.8.11", "A.8.12", "A.8.16", "A.8.23", "A.8.28")


# ═══════════════════════════════════════════════════════════════════════════
#  LES ARTICLES 4 À 10
# ═══════════════════════════════════════════════════════════════════════════
#
# LA MÊME STRUCTURE HARMONISÉE QUE 42001, ET C'EST TOUT L'INTÉRÊT : un
# organisme certifié sur l'une greffe l'autre sur le même socle — revue de
# direction, audit interne, non-conformités, informations documentées.
# Le champ `mutualisable` dit, article par article, ce qui se greffe.

CHAPITRES = (
    ("4", "Contexte de l'organisation", (
        ("4.1", "Compréhension de l'organisation et de son contexte",
         "Nommer ce qui, dehors et dedans, pèse sur la sécurité de "
         "l'information : marché, droit applicable, dépendances techniques, "
         "maturité interne.", True),
        ("4.2", "Compréhension des besoins et des attentes des parties "
                "intéressées",
         "Recenser qui exige quoi — clients, régulateurs, assureurs, "
         "salariés — et lesquelles de ces exigences seront traitées par le "
         "système de management.", True),
        ("4.3", "Détermination du domaine d'application du système de "
                "management de la sécurité de l'information",
         "Écrire ce qui est dedans et ce qui est dehors. C'est la décision "
         "la plus structurante de la certification : tout ce qui n'est pas "
         "exclu par écrit sera audité.", False),
        ("4.4", "Système de management de la sécurité de l'information",
         "Établir, mettre en œuvre, tenir à jour et améliorer le système — "
         "l'article qui exige que le reste existe pour de bon.", False),
    )),
    ("5", "Leadership", (
        ("5.1", "Leadership et engagement",
         "La direction s'engage, et ça se prouve : ressources allouées, "
         "arbitrages rendus, sujet porté au plus haut niveau.", True),
        ("5.2", "Politique",
         "Le document court qui fixe le cap de la sécurité de l'information "
         "et engage la direction qui le signe.", False),
        ("5.3", "Rôles, responsabilités et autorités au sein de "
                "l'organisation",
         "Qui décide, qui met en œuvre, qui contrôle — et qui rend compte à "
         "la direction de la performance du système.", True),
    )),
    ("6", "Planification", (
        ("6.1.1", "Actions à mettre en œuvre face aux risques et "
                  "opportunités — Généralités",
         "Le cadre : ce que la planification doit produire, et sur quoi elle "
         "s'appuie.", True),
        ("6.1.2", "Appréciation des risques de sécurité de l'information",
         "Définir les CRITÈRES — dont les critères d'acceptation — AVANT "
         "d'apprécier ; puis identifier, analyser et évaluer les risques "
         "pesant sur la confidentialité, l'intégrité et la disponibilité, "
         "en désignant un propriétaire pour chacun.", False),
        ("6.1.3", "Traitement des risques de sécurité de l'information",
         "Choisir les options, déterminer les mesures nécessaires, les "
         "comparer à l'annexe A pour vérifier qu'aucune n'a été omise, "
         "produire la déclaration d'applicabilité, formuler le plan de "
         "traitement — et faire APPROUVER ce plan et ACCEPTER les risques "
         "résiduels par les propriétaires des risques.", False),
        ("6.2", "Objectifs de sécurité de l'information et plans pour les "
                "atteindre",
         "Des objectifs mesurables, datés, avec un responsable — et le plan "
         "qui dit comment on y arrive.", True),
        ("6.3", "Planification des modifications",
         "Les changements du système se planifient ; ils ne se constatent "
         "pas après coup. Article ajouté par la version 2022.", True),
    )),
    ("7", "Support", (
        ("7.1", "Ressources",
         "Les moyens humains, techniques et financiers, déterminés et "
         "fournis — pas espérés.", True),
        ("7.2", "Compétences",
         "Savoir quelles compétences le système exige, vérifier qu'on les a, "
         "et combler l'écart.", True),
        ("7.3", "Sensibilisation",
         "Que les personnes concernées sachent ce qu'on attend d'elles et ce "
         "qu'un manquement produit.", True),
        ("7.4", "Communication",
         "Qui communique quoi, à qui, quand et par quel canal — en interne "
         "comme au dehors.", True),
        ("7.5.1", "Informations documentées — Généralités",
         "Ce que le système doit consigner, et ce que l'organisme juge "
         "nécessaire d'y ajouter.", True),
        ("7.5.2", "Création et mise à jour des informations documentées",
         "Identification, format, revue et approbation : la discipline "
         "documentaire ordinaire des systèmes de management.", True),
        ("7.5.3", "Maîtrise des informations documentées",
         "Disponibilité, protection, distribution, conservation, suppression "
         "— y compris pour les documents d'origine externe.", True),
    )),
    ("8", "Fonctionnement", (
        ("8.1", "Planification et maîtrise opérationnelles",
         "Faire tourner ce qui a été planifié, maîtriser les changements, et "
         "tenir les processus externalisés — la sous-traitance ne sort pas "
         "du périmètre.", True),
        ("8.2", "Appréciation des risques de sécurité de l'information",
         "L'appréciation, exécutée à intervalles planifiés ET quand quelque "
         "chose change de façon notable, avec ses résultats conservés.",
         False),
        ("8.3", "Traitement des risques de sécurité de l'information",
         "Le plan de traitement, mis en œuvre, et la preuve qu'il l'a été.",
         False),
    )),
    ("9", "Évaluation des performances", (
        ("9.1", "Surveillance, mesure, analyse et évaluation",
         "Ce qu'on mesure, comment, quand, par qui — et quand les résultats "
         "sont évalués.", True),
        ("9.2.1", "Audit interne — Généralités",
         "Le système s'audite lui-même, à intervalles planifiés.", True),
        ("9.2.2", "Programme d'audit interne",
         "Fréquence, méthodes, responsabilités, comptes rendus — et des "
         "auditeurs qui n'auditent pas leur propre travail.", True),
        ("9.3.1", "Revue de direction — Généralités",
         "La direction revoit le système à intervalles planifiés.", True),
        ("9.3.2", "Éléments d'entrée de la revue de direction",
         "Ce que la direction doit avoir sous les yeux : suites des revues "
         "précédentes, changements, performance, non-conformités, retours "
         "des parties intéressées, résultats de l'appréciation des risques.",
         True),
        ("9.3.3", "Résultats de la revue de direction",
         "Les décisions prises — et les ressources engagées pour les tenir.",
         True),
    )),
    ("10", "Amélioration", (
        ("10.1", "Amélioration continue",
         "Pertinence, adéquation et efficacité du système, améliorées en "
         "continu.", True),
        ("10.2", "Non-conformité et action corrective",
         "Réagir, en corriger les conséquences, chercher la cause, agir sur "
         "la cause, et vérifier que ça a marché.", True),
    )),
)

SOUS_CHAPITRES = {}
for _num, _titre, _sous in CHAPITRES:
    for _n, _t, _d, _mut in _sous:
        SOUS_CHAPITRES[_n] = {"chapitre": _num, "chapitre_titre": _titre,
                              "titre": _t, "dit": _d, "mutualisable": _mut}

PROPRES_A_LA_SECURITE = tuple(n for n, v in sorted(SOUS_CHAPITRES.items())
                              if not v["mutualisable"])


# ═══════════════════════════════════════════════════════════════════════════
#  L'ANNEXE A — 93 MESURES, 4 THÈMES (VERSION 2022)
# ═══════════════════════════════════════════════════════════════════════════
#
# CE QUE CETTE TABLE CONTIENT, ET RIEN D'AUTRE : un numéro, un titre, et le
# fait qu'une mesure soit nouvelle en 2022. Le texte de l'exigence n'y est
# pas et n'y sera jamais — la norme est payante et protégée.
#
# POURQUOI LES QUATRE THÈMES ET NON LES QUATORZE CHAPITRES DE 2013 : parce
# que c'est la version en vigueur. Servir l'ancienne numérotation à un
# organisme qui prépare un audit aujourd'hui lui ferait construire une
# déclaration d'applicabilité que l'auditeur ne sait pas lire.

ANNEXE_A = (
    ("A.5", "Mesures organisationnelles",
     "Ce qui se décide et s'écrit : politiques, rôles, inventaires, "
     "classification, fournisseurs, incidents, conformité.", (
         ("A.5.1", "Politiques de sécurité de l'information"),
         ("A.5.2", "Fonctions et responsabilités liées à la sécurité de "
                   "l'information"),
         ("A.5.3", "Séparation des tâches"),
         ("A.5.4", "Responsabilités de la direction"),
         ("A.5.5", "Relations avec les autorités"),
         ("A.5.6", "Relations avec des groupes d'intérêt spécifiques"),
         ("A.5.7", "Renseignement sur les menaces"),
         ("A.5.8", "Sécurité de l'information dans la gestion de projet"),
         ("A.5.9", "Inventaire des informations et autres actifs associés"),
         ("A.5.10", "Utilisation correcte des informations et autres actifs "
                    "associés"),
         ("A.5.11", "Restitution des actifs"),
         ("A.5.12", "Classification des informations"),
         ("A.5.13", "Marquage des informations"),
         ("A.5.14", "Transfert de l'information"),
         ("A.5.15", "Contrôle d'accès"),
         ("A.5.16", "Gestion des identités"),
         ("A.5.17", "Informations d'authentification"),
         ("A.5.18", "Droits d'accès"),
         ("A.5.19", "Sécurité de l'information dans les relations avec les "
                    "fournisseurs"),
         ("A.5.20", "Prise en compte de la sécurité de l'information dans "
                    "les accords conclus avec les fournisseurs"),
         ("A.5.21", "Gestion de la sécurité de l'information dans la chaîne "
                    "d'approvisionnement des produits et services TIC"),
         ("A.5.22", "Surveillance, revue et gestion des changements des "
                    "services fournisseurs"),
         ("A.5.23", "Sécurité de l'information dans l'utilisation de "
                    "services en nuage"),
         ("A.5.24", "Planification et préparation de la gestion des "
                    "incidents de sécurité de l'information"),
         ("A.5.25", "Évaluation des événements de sécurité de l'information "
                    "et prise de décision"),
         ("A.5.26", "Réponse aux incidents de sécurité de l'information"),
         ("A.5.27", "Tirer des enseignements des incidents de sécurité de "
                    "l'information"),
         ("A.5.28", "Recueil de preuves"),
         ("A.5.29", "Sécurité de l'information durant une perturbation"),
         ("A.5.30", "Préparation des TIC pour la continuité d'activité"),
         ("A.5.31", "Exigences légales, statutaires, réglementaires et "
                    "contractuelles"),
         ("A.5.32", "Droits de propriété intellectuelle"),
         ("A.5.33", "Protection des enregistrements"),
         ("A.5.34", "Protection de la vie privée et des données à caractère "
                    "personnel"),
         ("A.5.35", "Revue indépendante de la sécurité de l'information"),
         ("A.5.36", "Conformité aux politiques, règles et normes de sécurité "
                    "de l'information"),
         ("A.5.37", "Procédures d'exploitation documentées"),
     )),
    ("A.6", "Mesures liées aux personnes",
     "Ce qui se joue avant, pendant et après le contrat de travail — et qui "
     "ne se répare par aucun outil.", (
         ("A.6.1", "Sélection des candidats"),
         ("A.6.2", "Conditions générales d'embauche"),
         ("A.6.3", "Sensibilisation, apprentissage et formation à la "
                   "sécurité de l'information"),
         ("A.6.4", "Processus disciplinaire"),
         ("A.6.5", "Responsabilités après la fin ou le changement d'un "
                   "contrat de travail"),
         ("A.6.6", "Engagements de confidentialité ou de non-divulgation"),
         ("A.6.7", "Travail à distance"),
         ("A.6.8", "Déclaration des événements de sécurité de l'information"),
     )),
    ("A.7", "Mesures physiques",
     "Les murs, les portes, les câbles et le matériel — le thème qu'un "
     "organisme entièrement infogéré croit pouvoir écarter, et qui le "
     "rattrape par ses propres bureaux.", (
         ("A.7.1", "Périmètres de sécurité physique"),
         ("A.7.2", "Contrôles d'accès physique"),
         ("A.7.3", "Sécurisation des bureaux, des salles et des équipements"),
         ("A.7.4", "Surveillance de la sécurité physique"),
         ("A.7.5", "Protection contre les menaces physiques et "
                   "environnementales"),
         ("A.7.6", "Travail dans les zones sécurisées"),
         ("A.7.7", "Bureau propre et écran vide"),
         ("A.7.8", "Emplacement et protection du matériel"),
         ("A.7.9", "Sécurité des actifs hors des locaux"),
         ("A.7.10", "Supports de stockage"),
         ("A.7.11", "Services généraux"),
         ("A.7.12", "Sécurité du câblage"),
         ("A.7.13", "Maintenance du matériel"),
         ("A.7.14", "Mise au rebut ou recyclage sécurisé du matériel"),
     )),
    ("A.8", "Mesures technologiques",
     "Ce que la DSI met en œuvre : accès, journaux, réseaux, cryptographie, "
     "développement. Le thème le plus fourni, et le seul qu'on croit "
     "connaître.", (
         ("A.8.1", "Terminaux finaux des utilisateurs"),
         ("A.8.2", "Privilèges d'accès"),
         ("A.8.3", "Restriction d'accès à l'information"),
         ("A.8.4", "Accès au code source"),
         ("A.8.5", "Authentification sécurisée"),
         ("A.8.6", "Dimensionnement"),
         ("A.8.7", "Protection contre les programmes malveillants"),
         ("A.8.8", "Gestion des vulnérabilités techniques"),
         ("A.8.9", "Gestion des configurations"),
         ("A.8.10", "Suppression d'informations"),
         ("A.8.11", "Masquage des données"),
         ("A.8.12", "Prévention de la fuite de données"),
         ("A.8.13", "Sauvegarde des informations"),
         ("A.8.14", "Redondance des moyens de traitement de l'information"),
         ("A.8.15", "Journalisation"),
         ("A.8.16", "Activités de surveillance"),
         ("A.8.17", "Synchronisation des horloges"),
         ("A.8.18", "Utilisation de programmes utilitaires à privilèges"),
         ("A.8.19", "Installation de logiciels sur des systèmes en "
                    "exploitation"),
         ("A.8.20", "Sécurité des réseaux"),
         ("A.8.21", "Sécurité des services réseau"),
         ("A.8.22", "Cloisonnement des réseaux"),
         ("A.8.23", "Filtrage web"),
         ("A.8.24", "Utilisation de la cryptographie"),
         ("A.8.25", "Cycle de vie de développement sécurisé"),
         ("A.8.26", "Exigences de sécurité des applications"),
         ("A.8.27", "Principes d'ingénierie et d'architecture des systèmes "
                    "sécurisés"),
         ("A.8.28", "Codage sécurisé"),
         ("A.8.29", "Tests de sécurité dans le développement et "
                    "l'acceptation"),
         ("A.8.30", "Développement externalisé"),
         ("A.8.31", "Séparation des environnements de développement, de test "
                    "et de production"),
         ("A.8.32", "Gestion des changements"),
         ("A.8.33", "Informations de test"),
         ("A.8.34", "Protection des systèmes d'information pendant les tests "
                    "d'audit"),
     )),
)

MESURES = {}
for _th, _tt, _td, _liste in ANNEXE_A:
    for _num, _titre in _liste:
        MESURES[_num] = {"theme": _th, "theme_titre": _tt, "theme_dit": _td,
                         "titre": _titre,
                         "nouvelle_2022": _num in NOUVELLES_2022}


# ═══════════════════════════════════════════════════════════════════════════
#  L'ANALYSE DE RISQUE — ARTICLES 6.1.2 ET 6.1.3
# ═══════════════════════════════════════════════════════════════════════════
#
# CE QUE LA NORME IMPOSE, ET CE QU'ELLE LAISSE OUVERT. Elle impose d'établir
# des critères, d'identifier les risques par atteinte à la confidentialité, à
# l'intégrité ou à la disponibilité, de leur désigner un propriétaire, de les
# analyser et de les comparer aux critères. Elle n'impose AUCUNE échelle :
# celle qui suit est celle du cabinet, et le module le dit — présenter une
# échelle maison comme normative serait un faux.

ECHELLES = {
    "vraisemblance": (
        (1, "Improbable", "Aucun cas connu dans l'organisme ni dans son "
                          "secteur ; exigerait un concours de circonstances."),
        (2, "Possible", "Documenté ailleurs dans le secteur, jamais survenu "
                        "ici."),
        (3, "Probable", "Déjà survenu ici, ou survient régulièrement dans le "
                        "secteur."),
        (4, "Quasi certain", "Survient plusieurs fois par an, ou une "
                             "vulnérabilité exploitable est déjà connue."),
    ),
    "consequence": (
        (1, "Mineure", "Gêne interne, absorbée sans décision de direction."),
        (2, "Modérée", "Perturbation d'un service, coût ou délai mesurable, "
                       "pas de tiers affecté."),
        (3, "Majeure", "Service essentiel interrompu, tiers affectés, "
                       "obligation de notification possible."),
        (4, "Critique", "Atteinte durable à l'activité, aux personnes ou à "
                        "la réputation ; survie de l'organisme en question."),
    ),
}

# LES TROIS PROPRIÉTÉS — art. 6.1.2 c) 1). Un risque qui n'en atteint aucune
# n'est pas un risque de sécurité de l'information au sens de l'article : il
# peut être réel, il relève d'un autre registre.
PROPRIETES = ("confidentialite", "integrite", "disponibilite")
PROPRIETES_NOMS = {"confidentialite": "Confidentialité",
                   "integrite": "Intégrité",
                   "disponibilite": "Disponibilité"}

OPTIONS_TRAITEMENT = {
    "modifier": {"nom": "Modifier le risque", "rang": 0,
                 "dit": "Mettre en œuvre des mesures qui abaissent la "
                        "vraisemblance, la conséquence, ou les deux."},
    "partager": {"nom": "Partager le risque", "rang": 1,
                 "dit": "Assurance, sous-traitance, clause contractuelle. "
                        "Le risque reste porté par l'organisme : le partage "
                        "déplace la charge financière, pas la "
                        "responsabilité."},
    "eviter": {"nom": "Éviter le risque", "rang": 2,
               "dit": "Renoncer à l'activité qui l'engendre. C'est la seule "
                      "option qui supprime réellement le risque, et la seule "
                      "qui coûte une décision de métier."},
    "maintenir": {"nom": "Maintenir le risque", "rang": 3,
                  "dit": "L'accepter en l'état. Légitime SI le niveau "
                         "respecte les critères d'acceptation établis, et si "
                         "le propriétaire l'a écrit et daté."},
}

CRITERES_DEFAUT = {
    "seuil_acceptation": 6,
    "dit": "Au-delà de ce niveau (vraisemblance × conséquence), le risque ne "
           "peut pas être simplement maintenu : il appelle un traitement.",
}


def niveau(vraisemblance, consequence):
    """Le produit, et rien de plus savant.

    POURQUOI UN PRODUIT ET NON UNE MATRICE PONDÉRÉE. Une matrice maison
    pondérée se discute pendant trois réunions et ne change presque jamais
    l'ordre des risques. Le produit se comprend en une phrase, se refait de
    tête, et laisse la discussion là où elle est utile : sur les cotations
    elles-mêmes.
    """
    if vraisemblance not in (1, 2, 3, 4) or consequence not in (1, 2, 3, 4):
        return None
    return vraisemblance * consequence


def apprecier(risques=None, criteres=None):
    """L'appréciation des risques — et les deux défauts qu'elle refuse.

    ═══ DÉFAUT N°1 : LES CRITÈRES FIXÉS APRÈS ═══════════════════════════
    L'article 6.1.2 a) demande d'ÉTABLIR les critères, dont ceux
    d'acceptation. Les fixer après avoir vu les résultats donne un registre
    où tout est acceptable — et c'est INVISIBLE dans le document final,
    puisque seul l'ordre de rédaction distingue les deux. Le module compare
    donc les deux dates, et refuse de valider quand elles manquent ou quand
    l'ordre est inversé.

    ═══ DÉFAUT N°2 : LE PROPRIÉTAIRE NOMMÉ MAIS PAS SIGNATAIRE ══════════
    Une colonne « propriétaire » remplie ne vaut pas l'acceptation datée que
    demande l'article 6.1.3 e). L'auditeur demande la signature, pas le nom.
    """
    liste = risques or []
    if not isinstance(liste, list):
        return {"ok": False, "motif": "registre_illisible"}
    c = dict(CRITERES_DEFAUT)
    c.update(criteres or {})
    seuil = c.get("seuil_acceptation")
    if not isinstance(seuil, int) or not (1 <= seuil <= 16):
        return {"ok": False, "motif": "seuil_illisible"}

    # ── L'ORDRE DES DEUX DATES ───────────────────────────────────────────
    etabli = str(c.get("etabli_le") or "").strip()
    apprecie = str(c.get("apprecie_le") or "").strip()
    if not etabli:
        ordre = {"ok": False, "cle": "criteres_non_dates",
                 "dit": "Les critères d'acceptation ne portent aucune date. "
                        "Rien ne permet de montrer qu'ils précèdent "
                        "l'appréciation, et c'est ce que l'auditeur "
                        "demandera."}
    elif not apprecie:
        ordre = {"ok": False, "cle": "appreciation_non_datee",
                 "dit": "L'appréciation ne porte aucune date : l'antériorité "
                        "des critères ne peut pas être établie."}
    elif etabli > apprecie:
        ordre = {"ok": False, "cle": "criteres_posterieurs",
                 "dit": "Les critères d'acceptation (%s) sont POSTÉRIEURS à "
                        "l'appréciation (%s). Un registre coté puis mesuré "
                        "contre des critères écrits après rend tout "
                        "acceptable, et l'écart est un écart majeur."
                        % (etabli, apprecie)}
    else:
        ordre = {"ok": True, "cle": "conforme",
                 "dit": "Les critères (%s) précèdent l'appréciation (%s)."
                        % (etabli, apprecie)}

    lignes, defauts = [], []
    for i, r in enumerate(liste):
        r = r if isinstance(r, dict) else {}
        nom = str(r.get("nom") or "").strip()
        v, q = r.get("vraisemblance"), r.get("consequence")
        n = niveau(v, q)
        props = [p for p in PROPRIETES if r.get(p)]
        proprietaire = str(r.get("proprietaire") or "").strip()
        manques = []
        if not nom:
            manques.append("nom")
        if n is None:
            manques.append("cotation")
        if not props:
            manques.append("propriété atteinte")
        if not proprietaire:
            manques.append("propriétaire")
        if manques:
            defauts.append({"rang": i, "nom": nom or "(sans nom)",
                            "manques": manques})
        acceptable = (n is not None and n <= seuil)
        lignes.append({
            "rang": i, "nom": nom or "(sans nom)",
            "vraisemblance": v, "consequence": q, "niveau": n,
            "proprietes": props,
            "proprietes_noms": [PROPRIETES_NOMS[p] for p in props],
            "proprietaire": proprietaire or None,
            "acceptable": acceptable,
            "complet": not manques, "manques": manques,
        })

    cotes = [l for l in lignes if l["niveau"] is not None]
    inacceptables = [l for l in cotes if not l["acceptable"]]
    return {
        "ok": True,
        "criteres": dict(c, ordre=ordre),
        "lignes": lignes,
        "total": len(lignes),
        "cotes": len(cotes),
        "inacceptables": inacceptables,
        "defauts": defauts,
        "pire": (max(cotes, key=lambda l: l["niveau"]) if cotes else None),
        "echelles": ECHELLES,
        # LE REGISTRE N'EST VALIDE QUE SI LES DEUX CONDITIONS TIENNENT : des
        # critères antérieurs, et aucune ligne incomplète. Rendre « valide »
        # sur la seule cotation ferait passer un registre sans propriétaires.
        "valide": bool(ordre["ok"] and not defauts and cotes),
        "dit": _dit_appreciation(ordre, defauts, cotes, inacceptables),
        "source": SOURCE,
    }


def _dit_appreciation(ordre, defauts, cotes, inacceptables):
    if not ordre["ok"]:
        return ordre["dit"]
    if not cotes:
        return ("Aucun risque coté : l'appréciation n'a pas commencé.")
    if defauts:
        return ("%d ligne(s) incomplètes : l'article 6.1.2 c) demande, pour "
                "CHAQUE risque, la propriété atteinte et un propriétaire "
                "désigné. Une ligne sans propriétaire ne pourra être "
                "acceptée par personne." % len(defauts))
    return ("%d risque(s) au-dessus du seuil d'acceptation : ils appellent "
            "un traitement, et seul un traitement effectivement mis en "
            "œuvre — pas un plan — fait baisser le niveau résiduel."
            % len(inacceptables))


def traiter(risques=None, criteres=None):
    """Le traitement — et l'acceptation qui doit être ÉCRITE et DATÉE.

    CE QUE CETTE FONCTION REFUSE DE DIRE. Qu'un risque est « traité » parce
    qu'un plan existe. L'article 6.1.3 demande un plan formulé ET son
    approbation par les propriétaires ; l'article 8.3 demande sa MISE EN
    ŒUVRE. Un risque dont le plan est approuvé mais non exécuté reste au
    niveau initial, et le module le compte comme tel.
    """
    base = apprecier(risques, criteres)
    if not base.get("ok"):
        return base
    liste = risques or []

    lignes, sans_option, sans_acceptation, residuel_non_cote = [], [], [], []
    for l in base["lignes"]:
        r = liste[l["rang"]] if l["rang"] < len(liste) else {}
        r = r if isinstance(r, dict) else {}
        option = r.get("option") if r.get("option") in OPTIONS_TRAITEMENT else None
        mesures = [str(x).strip() for x in (r.get("mesures") or [])
                   if str(x).strip()]
        mises = bool(r.get("mesures_mises_en_oeuvre"))
        rv, rq = r.get("residuel_vraisemblance"), r.get("residuel_consequence")
        rn = niveau(rv, rq)
        accepte_par = str(r.get("accepte_par") or "").strip()
        accepte_le = str(r.get("accepte_le") or "").strip()

        # ── LE NIVEAU RETENU — ET CE QUI LE FAIT BAISSER ─────────────────
        #
        # UN PLAN N'EST PAS UNE MESURE. Tant que `mesures_mises_en_oeuvre`
        # est faux, le niveau résiduel déclaré n'est pas retenu : c'est une
        # prévision, et la servir comme un acquis est la façon la plus
        # courante de rendre un registre vert sans avoir rien fait.
        retenu = rn if (mises and rn is not None) else l["niveau"]
        acquis = bool(mises and rn is not None)

        if l["niveau"] is not None and not l["acceptable"] and not option:
            sans_option.append(l["nom"])
        if mises and rn is None:
            residuel_non_cote.append(l["nom"])

        # L'ACCEPTATION EST VALIDE SI ELLE NOMME QUELQU'UN, PORTE UNE DATE,
        # ET QUE CE QUELQU'UN EST LE PROPRIÉTAIRE DU RISQUE.
        par_le_proprietaire = bool(
            accepte_par and l["proprietaire"]
            and accepte_par.lower() == l["proprietaire"].lower())
        acceptation = {
            "par": accepte_par or None, "le": accepte_le or None,
            "par_le_proprietaire": par_le_proprietaire,
            "valide": bool(accepte_par and accepte_le and par_le_proprietaire),
        }
        besoin = (retenu is not None and retenu > base["criteres"]["seuil_acceptation"]) \
            or option == "maintenir"
        if besoin and not acceptation["valide"]:
            sans_acceptation.append(l["nom"])

        lignes.append(dict(
            l, option=(dict(OPTIONS_TRAITEMENT[option], cle=option)
                       if option else None),
            mesures=mesures, mesures_mises_en_oeuvre=mises,
            residuel_vraisemblance=rv, residuel_consequence=rq,
            residuel=rn, niveau_retenu=retenu, residuel_acquis=acquis,
            acceptation=acceptation,
            acceptation_requise=besoin,
            acceptable_retenu=(retenu is not None
                               and retenu <= base["criteres"]["seuil_acceptation"])))

    restants = [l for l in lignes
                if l["niveau_retenu"] is not None and not l["acceptable_retenu"]]
    bloquants = []
    if not base["criteres"]["ordre"]["ok"]:
        bloquants.append(base["criteres"]["ordre"]["dit"])
    if base["defauts"]:
        bloquants.append(
            "%d ligne(s) du registre sont incomplètes (art. 6.1.2 c)."
            % len(base["defauts"]))
    if sans_option:
        bloquants.append(
            "%d risque(s) au-dessus du seuil sans option de traitement "
            "choisie : %s" % (len(sans_option), ", ".join(sans_option[:6])))
    if sans_acceptation:
        bloquants.append(
            "%d risque(s) appellent une acceptation écrite et datée du "
            "PROPRIÉTAIRE, et ne l'ont pas : %s"
            % (len(sans_acceptation), ", ".join(sans_acceptation[:6])))
    if residuel_non_cote:
        bloquants.append(
            "%d risque(s) déclarent des mesures mises en œuvre sans coter le "
            "niveau résiduel : %s"
            % (len(residuel_non_cote), ", ".join(residuel_non_cote[:6])))

    return dict(base,
                lignes=lignes,
                restants=restants,
                sans_option=sans_option,
                sans_acceptation=sans_acceptation,
                residuel_non_cote=residuel_non_cote,
                options=OPTIONS_TRAITEMENT,
                recevable=not bloquants,
                bloquants=bloquants,
                dit=("Le plan de traitement tient : critères antérieurs, "
                     "registre complet, options choisies, acceptations "
                     "écrites et datées par les propriétaires."
                     if not bloquants else
                     "Le plan de traitement ne tient pas en l'état. Ce ne "
                     "sont pas des défauts techniques : ce sont des défauts "
                     "de DÉCISION, et ils se corrigent par des signatures, "
                     "pas par des outils."),
                article="art. 6.1.2 et 6.1.3")


# ═══════════════════════════════════════════════════════════════════════════
#  LA DÉCLARATION D'APPLICABILITÉ — TROIS COLONNES, PAS DEUX
# ═══════════════════════════════════════════════════════════════════════════
#
# CE QUI LA DISTINGUE DE CELLE DE 42001, ET C'EST MESURABLE. L'article
# 6.1.3 d) demande, pour chaque mesure : la décision (retenue ou écartée),
# sa JUSTIFICATION — dans les deux sens —, ET le STATUT DE MISE EN ŒUVRE.
# Trois colonnes. Celle de 42001 en demande deux ; servir le même gabarit
# aux deux normes fait perdre la troisième, et c'est celle que l'auditeur
# recoupe avec ce qu'il voit sur le terrain.

_DECISIONS = ("retenue", "ecartee")
_STATUTS = ("mise_en_oeuvre", "partielle", "planifiee", "non_mise_en_oeuvre")
_STATUTS_NOMS = {
    "mise_en_oeuvre": "Mise en œuvre",
    "partielle": "Partiellement mise en œuvre",
    "planifiee": "Planifiée",
    "non_mise_en_oeuvre": "Non mise en œuvre",
    "non_renseigne": "Statut non renseigné",
}


def _ordre(num):
    """Trier A.8.10 après A.8.9, et A.5 avant A.10 — numériquement."""
    return tuple(int(x) for x in num[2:].split(".") if x.isdigit())


def declaration_applicabilite(decisions=None):
    """Les 93 mesures, tranchées, justifiées, et dont le statut est dit.

    ═══ LES TROIS FAÇONS DE LA RATER ════════════════════════════════════
      1. une mesure ni retenue ni écartée — l'article ne prévoit pas ce cas ;
      2. une décision sans justification — exigée dans les DEUX sens ;
      3. une mesure retenue dont le statut de mise en œuvre n'est pas dit —
         la colonne propre à 27001, et la première que l'auditeur recoupe
         avec ce qu'il constate.

    UNE MESURE ÉCARTÉE N'A PAS DE STATUT, et ne doit pas en avoir : lui en
    demander un ferait compter comme un manque ce qui est une décision.
    """
    d = decisions or {}
    if not isinstance(d, dict):
        return {"ok": False, "motif": "decisions_illisibles"}

    lignes, sans_justification, sans_statut = [], [], []
    for num in sorted(MESURES, key=_ordre):
        brut = d.get(num)
        if isinstance(brut, str):
            brut = {"decision": brut}
        brut = brut if isinstance(brut, dict) else {}
        decision = brut.get("decision")
        decision = decision if decision in _DECISIONS else "non_decidee"
        justification = str(brut.get("justification") or "").strip()
        statut = brut.get("statut")
        statut = statut if statut in _STATUTS else "non_renseigne"

        manque_j = (decision in _DECISIONS and not justification)
        manque_s = (decision == "retenue" and statut == "non_renseigne")
        if manque_j:
            sans_justification.append(num)
        if manque_s:
            sans_statut.append(num)

        lignes.append(dict(
            MESURES[num], numero=num, decision=decision,
            justification=justification or None,
            statut=statut, statut_nom=_STATUTS_NOMS[statut],
            justification_manquante=manque_j, statut_manquant=manque_s))

    non_decidees = [l["numero"] for l in lignes
                    if l["decision"] == "non_decidee"]
    retenues = [l for l in lignes if l["decision"] == "retenue"]
    ecartees = [l for l in lignes if l["decision"] == "ecartee"]
    faites = [l for l in retenues if l["statut"] == "mise_en_oeuvre"]
    neuves = [l for l in lignes if l["nouvelle_2022"]]
    neuves_non_decidees = [l["numero"] for l in neuves
                           if l["decision"] == "non_decidee"]

    bloquants = []
    if non_decidees:
        bloquants.append(
            "%d mesure(s) ne sont ni retenues ni écartées : %s"
            % (len(non_decidees), ", ".join(non_decidees[:8])
               + ("…" if len(non_decidees) > 8 else "")))
    if sans_justification:
        bloquants.append(
            "%d décision(s) ne portent aucune justification : %s"
            % (len(sans_justification), ", ".join(sans_justification[:8])
               + ("…" if len(sans_justification) > 8 else "")))
    if sans_statut:
        bloquants.append(
            "%d mesure(s) retenues ne disent pas leur statut de mise en "
            "œuvre — la colonne propre à l'article 6.1.3 d) : %s"
            % (len(sans_statut), ", ".join(sans_statut[:8])
               + ("…" if len(sans_statut) > 8 else "")))

    return {
        "ok": True,
        "lignes": lignes,
        "themes": _par_theme(lignes),
        "total": len(lignes),
        "retenues": len(retenues),
        "ecartees": len(ecartees),
        "non_decidees": non_decidees,
        "sans_justification": sans_justification,
        "sans_statut": sans_statut,
        "mises_en_oeuvre": len(faites),
        "taux_mise_en_oeuvre": (round(100.0 * len(faites) / len(retenues))
                                if retenues else None),
        "taux_decision": round(100.0 * (len(lignes) - len(non_decidees))
                               / len(lignes)),
        # LES ONZE NOUVELLES, COMPTÉES À PART. C'est le reste à faire d'un
        # organisme certifié contre la version 2013 — ni 93, ni « tout ».
        "nouvelles_2022": {
            "total": len(neuves),
            "numeros": [l["numero"] for l in neuves],
            "non_decidees": neuves_non_decidees,
            "dit": "Ces %d mesures n'existaient pas dans ISO/IEC 27001:2013. "
                   "Un organisme certifié contre l'ancienne version a "
                   "celles-là devant lui, et elles seules — pas les 93."
                   % len(neuves),
        },
        "recevable": not bloquants,
        "bloquants": bloquants,
        "dit": ("La déclaration est recevable : chaque mesure est tranchée, "
                "motivée, et les mesures retenues disent où elles en sont."
                if not bloquants else
                "La déclaration n'est PAS recevable. Le défaut est "
                "documentaire, et il se corrige en écrivant, pas en "
                "développant."),
        "article": "art. 6.1.3 d)",
        "source": SOURCE,
    }


def _par_theme(lignes):
    groupes = []
    for th, tt, td, liste in ANNEXE_A:
        nums = [n for n, _t in liste]
        sous = [l for l in lignes if l["numero"] in nums]
        groupes.append({
            "numero": th, "titre": tt, "dit": td, "lignes": sous,
            "total": len(sous),
            "retenues": sum(1 for l in sous if l["decision"] == "retenue"),
            "ecartees": sum(1 for l in sous if l["decision"] == "ecartee"),
            "non_decidees": sum(1 for l in sous
                                if l["decision"] == "non_decidee"),
            "nouvelles": sum(1 for l in sous if l["nouvelle_2022"]),
        })
    return groupes


# ═══════════════════════════════════════════════════════════════════════════
#  LA MATURITÉ SUR LES ARTICLES 4 À 10
# ═══════════════════════════════════════════════════════════════════════════

def maturite(declares=None):
    """L'écart sur les articles — et ce que « sans objet » ne peut pas être.

    MÊME RÈGLE QUE POUR 42001, ET POUR LA MÊME RAISON : les mesures de
    l'annexe A s'écartent avec justification, les articles 4 à 10 non. Un
    organisme qui déclarerait « 9.2 Audit interne : sans objet » n'a pas
    écarté une mesure, il a renoncé à la certification.
    """
    d = declares or {}
    if not isinstance(d, dict):
        return {"ok": False, "motif": "declaration_illisible"}

    chapitres, refus = [], []
    for num, titre, sous in CHAPITRES:
        lignes = []
        for n, t, dit, mut in sous:
            e = d.get(n)
            if e == "sans_objet":
                refus.append(n)
                e = None
            lignes.append({
                "numero": n, "titre": t, "dit": dit, "mutualisable": mut,
                "etat": e if e in ("conforme", "partiel", "non_conforme")
                        else "non_renseigne"})
        chapitres.append({
            "numero": num, "titre": titre, "lignes": lignes,
            "conformes": sum(1 for l in lignes if l["etat"] == "conforme"),
            "total": len(lignes)})

    toutes = [l for c in chapitres for l in c["lignes"]]
    conformes = [l for l in toutes if l["etat"] == "conforme"]
    propres = [l for l in toutes if not l["mutualisable"]]
    propres_faits = [l for l in propres if l["etat"] == "conforme"]
    return {
        "ok": True,
        "chapitres": chapitres,
        "total": len(toutes),
        "conformes": len(conformes),
        "taux": round(100.0 * len(conformes) / len(toutes)),
        "non_renseigne": sum(1 for l in toutes
                             if l["etat"] == "non_renseigne"),
        "propres_a_la_securite": {
            "total": len(propres), "conformes": len(propres_faits),
            "taux": round(100.0 * len(propres_faits) / len(propres)),
            "numeros": [l["numero"] for l in propres],
            "dit": "Ces articles ne se reprennent pas d'un autre système de "
                   "management : périmètre, politique, et les deux qui "
                   "portent l'appréciation et le traitement des risques.",
        },
        "refus_sans_objet": refus,
        "dit_refus": ("Un article de 4 à 10 ne se déclare pas « sans "
                      "objet » : les exigences ne s'écartent pas, seules les "
                      "mesures de l'annexe A le peuvent (art. 6.1.3 d). "
                      "%d déclaration(s) ont été ignorées." % len(refus))
                     if refus else None,
        "source": SOURCE,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  LA CERTIFICATION, ET LA TRANSITION 2013 → 2022
# ═══════════════════════════════════════════════════════════════════════════

CERTIFICATION = {
    "nature": "Certification par un organisme tiers accrédité. Avec "
              "ISO/IEC 42001, l'une des deux seules références de cet espace "
              "qui délivre un certificat opposable — RGPD, NIS 2 et CRA sont "
              "du droit.",
    "etapes": (
        {"cle": "etape_1", "nom": "Audit d'étape 1 — revue documentaire",
         "objet": "L'auditeur vérifie que le système EXISTE sur le papier : "
                  "domaine d'application, politique, appréciation ET "
                  "traitement des risques, déclaration d'applicabilité, "
                  "plan d'audit interne.",
         "ce_qui_fait_tomber": "Une déclaration d'applicabilité amputée de "
                               "sa troisième colonne, ou un registre de "
                               "risques sans acceptation datée des "
                               "propriétaires. Deux défauts documentaires, "
                               "et ils arrêtent tout."},
        {"cle": "etape_2", "nom": "Audit d'étape 2 — mise en œuvre",
         "objet": "L'auditeur recoupe le statut déclaré de chaque mesure "
                  "retenue avec ce qu'il constate : enregistrements, "
                  "configurations, entretiens.",
         "ce_qui_fait_tomber": "Un écart entre la colonne « statut » de la "
                               "déclaration et le terrain. C'est exactement "
                               "ce que cette colonne sert à vérifier."},
        {"cle": "surveillance", "nom": "Audits de surveillance",
         "objet": "Le certificat vit sur un cycle de trois ans, avec des "
                  "audits périodiques.",
         "ce_qui_fait_tomber": "Une appréciation des risques qui n'a pas "
                               "été refaite : l'article 8.2 l'exige à "
                               "intervalles planifiés ET après tout "
                               "changement notable."},
    ),
    "prealable": "Un cycle d'audit interne (art. 9.2) et une revue de "
                 "direction (art. 9.3) doivent avoir eu lieu AVANT l'étape 2. "
                 "Ils laissent des traces datées : ils ne se fabriquent pas "
                 "la veille.",
    "transition": {
        "quoi": "Les certificats émis contre ISO/IEC 27001:2013 ont dû être "
                "migrés vers la version 2022 à l'issue d'une période de "
                "transition fixée par l'IAF.",
        "reserve": "La date exacte de fin de cette période n'a PAS pu être "
                   "vérifiée depuis cet environnement (iso.org, iaf.nu et "
                   "cofrac.fr y sont injoignables). Elle se confirme auprès "
                   "de l'organisme certificateur, qui la connaît pour chaque "
                   "certificat qu'il a émis.",
        "consequence": "Un certificat non migré cesse d'être valide à "
                       "l'issue de la transition, quelle que soit la date "
                       "d'expiration imprimée dessus.",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
#  LES PONTS — CE QUI SE RÉUTILISE, ET CE QUI NE SE SUBSTITUE PAS
# ═══════════════════════════════════════════════════════════════════════════
#
# LE PONT VERS NIS 2 EST LE PLUS DEMANDÉ ET LE PLUS MAL COMPRIS. Il est réel
# et il est large : les dix mesures de l'article 21, §2, trouvent presque
# toutes un répondant dans l'annexe A. Mais NIS 2 impose des DÉLAIS et une
# RESPONSABILITÉ PERSONNELLE que la norme ne connaît pas, et un certificat ne
# vaut pas conformité à une directive. Le rapprochement ci-dessous est la
# LECTURE DU CABINET, pas une correspondance officielle.

NIS2_VERS_ANNEXE_A = (
    ("a", "Analyse des risques et sécurité des systèmes d'information",
     ("A.5.1", "A.5.36", "A.8.8")),
    ("b", "Gestion des incidents",
     ("A.5.24", "A.5.25", "A.5.26", "A.5.27", "A.5.28", "A.6.8")),
    ("c", "Continuité des activités",
     ("A.5.29", "A.5.30", "A.8.13", "A.8.14")),
    ("d", "Sécurité de la chaîne d'approvisionnement",
     ("A.5.19", "A.5.20", "A.5.21", "A.5.22", "A.5.23")),
    ("e", "Acquisition, développement et maintenance ; vulnérabilités",
     ("A.8.8", "A.8.25", "A.8.26", "A.8.28", "A.8.29", "A.8.30")),
    ("f", "Évaluation de l'efficacité des mesures",
     ("A.5.35", "A.5.36", "A.8.16")),
    ("g", "Cyberhygiène et formation",
     ("A.6.3", "A.7.7", "A.8.7")),
    ("h", "Cryptographie et chiffrement",
     ("A.8.24",)),
    ("i", "Ressources humaines, contrôle d'accès, gestion des actifs",
     ("A.5.9", "A.5.15", "A.5.16", "A.5.18", "A.6.1", "A.6.2", "A.6.5",
      "A.8.2", "A.8.3")),
    ("j", "Authentification à plusieurs facteurs, communications sécurisées",
     ("A.5.14", "A.8.5", "A.8.20", "A.8.21")),
)

PONTS = (
    {"cle": "nis2",
     "vers": "Directive (UE) 2022/2555 (NIS 2)",
     "nature": "obligation légale",
     "reutilise": "Les dix mesures de l'article 21, §2, trouvent presque "
                  "toutes un répondant dans l'annexe A : un système de "
                  "management certifié est le socle de preuves le plus "
                  "direct qu'une entité puisse présenter.",
     # LES TROIS ARTICLES SONT NOMMÉS, ET PAS SEULEMENT DÉCRITS. « Ça ne
     # couvre pas les délais » se discute ; « ça ne couvre pas l'article 23 »
     # se vérifie, et c'est la phrase qu'on cite en réunion.
     "ne_remplace_pas": "NIS 2 impose des DÉLAIS de signalement — 24 h, "
                        "72 h, un mois (art. 23) — que la norme ne fixe "
                        "pas, une responsabilité PERSONNELLE des dirigeants "
                        "(art. 20), et un enregistrement auprès de "
                        "l'autorité (art. 3, §4). Aucun certificat ne "
                        "couvre ces trois-là.",
     "mesures_iso": tuple(sorted({m for _c, _n, ms in NIS2_VERS_ANNEXE_A
                                  for m in ms}, key=_ordre)),
     "detail": NIS2_VERS_ANNEXE_A},
    {"cle": "iso42001",
     "vers": "ISO/IEC 42001 (management de l'IA)",
     "nature": "norme volontaire",
     "reutilise": "La structure harmonisée est identique : revue de "
                  "direction, audit interne, non-conformités, informations "
                  "documentées, compétences se greffent sans être refaits.",
     "ne_remplace_pas": "Les deux annexes A n'ont AUCUN rapport : 93 mesures "
                        "de sécurité d'un côté, 38 mesures de gouvernance de "
                        "l'IA de l'autre. Et le domaine d'application du "
                        "système de management de l'IA n'est pas celui du "
                        "système de management de la sécurité — le reprendre "
                        "tel quel est l'erreur la plus courante de cette "
                        "greffe.",
     "mesures_iso": (),
     "detail": ()},
    {"cle": "rgpd",
     "vers": "Règlement (UE) 2016/679 (RGPD)",
     "nature": "obligation légale",
     "reutilise": "L'article 32 du règlement demande des mesures techniques "
                  "et organisationnelles appropriées : l'annexe A en fournit "
                  "l'inventaire, et A.5.34 vise explicitement la protection "
                  "des données à caractère personnel.",
     "ne_remplace_pas": "Le RGPD porte sur les DROITS DES PERSONNES — base "
                        "légale, information, accès, effacement, "
                        "portabilité — dont la norme ne dit rien. Un "
                        "organisme parfaitement certifié peut traiter des "
                        "données sans base légale.",
     "mesures_iso": ("A.5.31", "A.5.33", "A.5.34", "A.8.10", "A.8.11"),
     "detail": ()},
    {"cle": "cra",
     "vers": "Règlement (UE) 2024/2847 (CRA)",
     "nature": "obligation légale",
     "reutilise": "La partie II de l'annexe I du CRA — traitement et "
                  "divulgation des vulnérabilités, nomenclature logicielle — "
                  "recouvre largement A.8.8, A.8.25 et A.8.28.",
     "ne_remplace_pas": "Le CRA compte des PRODUITS et impose un marquage CE, "
                        "une documentation technique et un signalement en "
                        "24 h à l'ENISA. Un système de management certifié "
                        "ne met aucun produit en conformité.",
     "mesures_iso": ("A.8.8", "A.8.25", "A.8.28", "A.8.32"),
     "detail": ()},
)


# ═══════════════════════════════════════════════════════════════════════════
#  L'ÉVALUATION D'ENSEMBLE
# ═══════════════════════════════════════════════════════════════════════════

def evaluer(declaration=None):
    """Risque d'abord, applicabilité ensuite, maturité en dernier.

    L'ORDRE EST CELUI DE LA NORME, ET IL N'EST PAS INTERCHANGEABLE. Les
    mesures de l'annexe A se DÉDUISENT du traitement des risques
    (art. 6.1.3 b et c) : construire la déclaration d'applicabilité d'abord,
    puis chercher des risques qui la justifient, produit un document qui
    tient debout et ne protège rien. C'est l'erreur la plus fréquente, et
    elle se voit à l'étape 2.
    """
    d = declaration or {}
    if not isinstance(d, dict):
        return {"ok": False, "motif": "declaration_illisible"}
    nom = str(d.get("nom") or "").strip()
    if not nom:
        return {"ok": False, "motif": "nom_manquant"}
    perimetre = str(d.get("perimetre") or "").strip()

    risque = traiter(d.get("risques"), d.get("criteres"))
    if not risque.get("ok"):
        return risque
    soa = declaration_applicabilite(d.get("mesures"))
    if not soa.get("ok"):
        return soa
    mat = maturite(d.get("articles"))
    if not mat.get("ok"):
        return mat

    # ── L'ÉTAPE RÉELLEMENT ATTEINTE ──────────────────────────────────────
    if not perimetre:
        etape, dit = "perimetre_absent", (
            "Le domaine d'application n'est pas écrit. C'est la première "
            "décision de la certification et la plus structurante : tout ce "
            "qui n'en est pas exclu par écrit sera audité.")
    elif not risque["recevable"]:
        etape, dit = "risque_bloque", (
            "L'analyse de risque ne tient pas, et rien ne se construit "
            "dessus : les mesures de l'annexe A se DÉDUISENT du traitement "
            "des risques, pas l'inverse.")
    elif not soa["recevable"]:
        etape, dit = "etape_1_bloquee", (
            "L'analyse de risque tient ; la déclaration d'applicabilité ne "
            "passe pas l'étape 1. Aucun taux de maturité ne rattrape ce "
            "défaut : l'auditeur s'arrête au document.")
    elif mat["propres_a_la_securite"]["taux"] < 100:
        etape, dit = "etape_1_ouverte", (
            "Documents recevables. Les articles propres à la sécurité ne "
            "sont pas tous tenus (%d sur %d) — c'est là que se joue la "
            "suite." % (mat["propres_a_la_securite"]["conformes"],
                        mat["propres_a_la_securite"]["total"]))
    elif soa["taux_mise_en_oeuvre"] is not None and \
            soa["taux_mise_en_oeuvre"] < 100:
        etape, dit = "etape_2_ouverte", (
            "Articles tenus, documents recevables ; %d mesure(s) retenues "
            "sur %d sont effectivement mises en œuvre."
            % (soa["mises_en_oeuvre"], soa["retenues"]))
    else:
        etape, dit = "pret", (
            "Périmètre écrit, risques traités et acceptés, déclaration "
            "complète, mesures retenues mises en œuvre. Reste à avoir "
            "réellement conduit un audit interne et une revue de direction.")

    return {
        "ok": True,
        "nom": nom,
        "perimetre": perimetre or None,
        "risque": risque,
        "applicabilite": soa,
        "maturite": mat,
        "certification": CERTIFICATION,
        "millesimes": MILLESIMES,
        "etape": etape,
        "dit": dit,
        "ponts": PONTS,
        "a_verifier": A_VERIFIER,
        "source": SOURCE,
        "source_questionnaire": SOURCE_QUESTIONNAIRE,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  LA GARDE — CE QUE CE MODULE REFUSE DE LAISSER PASSER
# ═══════════════════════════════════════════════════════════════════════════

def _verifier():
    fautes = []

    # ── LA STRUCTURE DE LA NORME ─────────────────────────────────────────
    numeros = [c for c, _t, _s in CHAPITRES]
    if numeros != ["4", "5", "6", "7", "8", "9", "10"]:
        fautes.append("les chapitres ne sont pas 4 à 10 : %s" % numeros)
    attendu = {"4": 4, "5": 3, "6": 5, "7": 7, "8": 3, "9": 6, "10": 2}
    for num, _t, sous in CHAPITRES:
        if len(sous) != attendu[num]:
            fautes.append("le chapitre %s compte %d sous-articles au lieu de "
                          "%d" % (num, len(sous), attendu[num]))
    if len(SOUS_CHAPITRES) != sum(attendu.values()):
        fautes.append("deux sous-articles portent le même numéro")
    profonds = {}
    for n in SOUS_CHAPITRES:
        bouts = n.split(".")
        if len(bouts) == 3:
            profonds.setdefault(".".join(bouts[:2]), []).append(n)
        elif len(bouts) != 2:
            fautes.append("le sous-article « %s » n'a ni deux ni trois "
                          "niveaux" % n)
    if sorted(profonds) != ["6.1", "7.5", "9.2", "9.3"]:
        fautes.append("les articles subdivisés ne sont pas 6.1, 7.5, 9.2 et "
                      "9.3 : %s" % sorted(profonds))
    for parent, enfants in profonds.items():
        if parent in SOUS_CHAPITRES:
            fautes.append("l'article « %s » est déclaré EN PLUS de ses "
                          "enfants" % parent)
        if len(enfants) < 2:
            fautes.append("l'article « %s » n'a qu'un enfant" % parent)
    # L'ARTICLE 6.3 EST L'APPORT DE LA VERSION 2022 : le perdre ramènerait
    # la table à la structure de 2013.
    if "6.3" not in SOUS_CHAPITRES:
        fautes.append("l'article 6.3, ajouté par la version 2022, a disparu")

    # ── L'ANNEXE A ───────────────────────────────────────────────────────
    if len(ANNEXE_A) != 4:
        fautes.append("l'annexe A 2022 compte 4 thèmes, pas %d"
                      % len(ANNEXE_A))
    compte = {"A.5": 37, "A.6": 8, "A.7": 14, "A.8": 34}
    for th, _tt, _td, liste in ANNEXE_A:
        if len(liste) != compte[th]:
            fautes.append("le thème %s compte %d mesures au lieu de %d"
                          % (th, len(liste), compte[th]))
    if len(MESURES) != MILLESIMES["2022"]["mesures"]:
        fautes.append("l'annexe A ne compte pas %d mesures : %d"
                      % (MILLESIMES["2022"]["mesures"], len(MESURES)))
    for num, m in MESURES.items():
        if not num.startswith(m["theme"] + "."):
            fautes.append("la mesure « %s » est rangée sous le thème %s"
                          % (num, m["theme"]))
        if not str(m.get("titre") or "").strip():
            fautes.append("la mesure « %s » n'a pas de titre" % num)

    # ── LE DROIT D'AUTEUR, TENU DANS LA TABLE ELLE-MÊME ──────────────────
    permises = {"theme", "theme_titre", "theme_dit", "titre", "nouvelle_2022"}
    for num, m in MESURES.items():
        en_trop = set(m) - permises
        if en_trop:
            fautes.append("la mesure « %s » porte un champ non prévu (%s) : "
                          "la table ne doit contenir que des numéros, des "
                          "titres et le millésime d'apparition"
                          % (num, ", ".join(sorted(en_trop))))
    if SOURCE.get("reproduction") is not False:
        fautes.append("la source ne déclare plus la reproduction interdite")
    if "DROIT D'AUTEUR" not in SOURCE.get("licence", "").upper():
        fautes.append("la licence de la source ne nomme plus le droit d'auteur")
    if SOURCE_QUESTIONNAIRE.get("reproduction") is not False:
        fautes.append("le questionnaire BSI ne déclare plus la reproduction "
                      "interdite — ses questions sont sa propriété")
    if "BSI" not in SOURCE_QUESTIONNAIRE.get("editeur", ""):
        fautes.append("le questionnaire ne nomme plus son éditeur")

    # ── LE MILLÉSIME ─────────────────────────────────────────────────────
    if MILLESIMES["2013"]["en_vigueur"] or not MILLESIMES["2022"]["en_vigueur"]:
        fautes.append("le millésime en vigueur n'est pas 2022")
    if MILLESIMES["2013"]["mesures"] <= MILLESIMES["2022"]["mesures"]:
        fautes.append("l'annexe A 2013 devait compter PLUS de mesures que "
                      "celle de 2022 (114 contre 93)")
    if len(NOUVELLES_2022) != 11:
        fautes.append("les mesures nouvelles de 2022 ne sont pas onze : %d"
                      % len(NOUVELLES_2022))
    for n in NOUVELLES_2022:
        if n not in MESURES:
            fautes.append("la mesure nouvelle « %s » n'existe pas dans "
                          "l'annexe A" % n)
    if SOURCE_QUESTIONNAIRE.get("vise") == SOURCE.get("court"):
        fautes.append("le questionnaire est déclaré viser la version en "
                      "vigueur — c'est faux, et c'est le fait principal du "
                      "module")

    # ── L'ORDRE NUMÉRIQUE, ET NON ALPHABÉTIQUE ───────────────────────────
    tries = sorted(MESURES, key=_ordre)
    if tries[0] != "A.5.1" or tries[-1] != "A.8.34":
        fautes.append("l'ordre des mesures n'est pas numérique : de %s à %s"
                      % (tries[0], tries[-1]))
    if tries.index("A.8.9") > tries.index("A.8.10"):
        fautes.append("A.8.9 doit précéder A.8.10 — tri alphabétique détecté")

    # ── L'ÉCHELLE ET LE SEUIL ────────────────────────────────────────────
    for cle, ech in ECHELLES.items():
        rangs = [r for r, _n, _d in ech]
        if rangs != [1, 2, 3, 4]:
            fautes.append("l'échelle « %s » n'est pas graduée 1..4 : %s"
                          % (cle, rangs))
    if niveau(4, 4) != 16 or niveau(1, 1) != 1:
        fautes.append("le niveau n'est plus le produit des deux cotations")
    if niveau(0, 4) is not None or niveau(5, 1) is not None:
        fautes.append("une cotation hors échelle est acceptée")
    if len(PROPRIETES) != 3:
        fautes.append("les trois propriétés — confidentialité, intégrité, "
                      "disponibilité — ne sont plus trois")

    # ── LES QUATRE OPTIONS DE TRAITEMENT ─────────────────────────────────
    rangs = sorted(o["rang"] for o in OPTIONS_TRAITEMENT.values())
    if rangs != list(range(len(OPTIONS_TRAITEMENT))):
        fautes.append("les rangs d'option ne sont pas 0..n : %s" % rangs)
    if len(OPTIONS_TRAITEMENT) != 4:
        fautes.append("les options de traitement ne sont pas quatre")

    # ── LES DEUX REFUS QUI PORTENT LE MODULE ─────────────────────────────
    #
    # ON LES ÉPROUVE ICI, AU CHARGEMENT, plutôt que de faire confiance à la
    # lecture : ce sont les deux comportements dont tout le reste dépend.
    tardif = apprecier(
        [{"nom": "R", "vraisemblance": 4, "consequence": 4,
          "confidentialite": True, "proprietaire": "DG"}],
        {"seuil_acceptation": 6, "etabli_le": "2026-05-01",
         "apprecie_le": "2026-04-01"})
    if tardif["valide"]:
        fautes.append("des critères d'acceptation POSTÉRIEURS à "
                      "l'appréciation sont jugés valides")
    sans_proprio = apprecier(
        [{"nom": "R", "vraisemblance": 2, "consequence": 2,
          "confidentialite": True}],
        {"seuil_acceptation": 6, "etabli_le": "2026-01-01",
         "apprecie_le": "2026-02-01"})
    if sans_proprio["valide"]:
        fautes.append("un risque sans propriétaire est jugé valide")

    # ── LES PONTS ────────────────────────────────────────────────────────
    for p in PONTS:
        if not p.get("ne_remplace_pas"):
            fautes.append("le pont vers « %s » ne dit pas ce qu'il ne "
                          "remplace pas" % p["cle"])
        for n in p["mesures_iso"]:
            if n not in MESURES:
                fautes.append("le pont « %s » cite une mesure inconnue : %s"
                              % (p["cle"], n))
    cles_nis2 = [c for c, _n, _ms in NIS2_VERS_ANNEXE_A]
    if cles_nis2 != list("abcdefghij"):
        fautes.append("le rapprochement NIS 2 ne couvre pas les dix mesures "
                      "a) à j) : %s" % cles_nis2)
    for _c, _n, ms in NIS2_VERS_ANNEXE_A:
        if not ms:
            fautes.append("une mesure NIS 2 ne renvoie à aucune mesure de "
                          "l'annexe A")
        for m in ms:
            if m not in MESURES:
                fautes.append("le rapprochement NIS 2 cite une mesure "
                              "inconnue : %s" % m)

    # ── LA CERTIFICATION ─────────────────────────────────────────────────
    if len(CERTIFICATION["etapes"]) != 3:
        fautes.append("le cycle de certification n'a pas trois temps")
    for e in CERTIFICATION["etapes"]:
        if not e.get("ce_qui_fait_tomber"):
            fautes.append("l'étape « %s » ne dit pas ce qui la fait échouer"
                          % e["cle"])
    if not CERTIFICATION["transition"].get("reserve"):
        fautes.append("la transition ne porte plus sa réserve — une date non "
                      "vérifiée serait citée comme établie")
    if not A_VERIFIER:
        fautes.append("le module ne déclare plus ce qu'il n'a pas pu vérifier")

    if fautes:
        raise RuntimeError("iso27001 — table incohérente : "
                           + " ; ".join(fautes))
    return fautes


_FAUTES = _verifier()
