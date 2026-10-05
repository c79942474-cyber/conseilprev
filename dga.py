# -*- coding: utf-8 -*-
"""LE RÈGLEMENT SUR LA GOUVERNANCE DES DONNÉES — ET LA QUESTION QUI DÉCIDE DE TOUT.
   ═══════════════════════════════════════════════════════════════════════════

   Règlement (UE) 2022/868 du 30 mai 2022, applicable depuis le 24 septembre
   2023. Il est cité par numéro et par intitulé d'article ; son texte n'est
   pas recopié ici — la règle de la maison, écrite au-dessus du fonds
   documentaire, vaut pour un règlement comme pour une norme.

   CE MODULE COMMENCE PAR DIRE « VOUS N'ÊTES PAS CONCERNÉ », ET C'EST SON
   PREMIER SERVICE. Les treize autres référentiels de Sentinel demandent à
   quel point vous êtes conforme. Celui-ci demande d'abord si le règlement
   vous saisit, parce que la réponse est NON pour la très grande majorité
   des entreprises. L'article 1er §1 n'établit que quatre cadres :

     a) la réutilisation de certaines catégories de données protégées
        détenues par des ORGANISMES DU SECTEUR PUBLIC (chapitre II) ;
     b) la notification et la surveillance des SERVICES D'INTERMÉDIATION DE
        DONNÉES (chapitre III) ;
     c) l'enregistrement volontaire des ORGANISATIONS ALTRUISTES EN MATIÈRE
        DE DONNÉES (chapitre IV) ;
     d) le comité européen de l'innovation dans le domaine des données.

   Une entreprise qui n'est ni un organisme du secteur public, ni un
   intermédiaire de données, ni une organisation altruiste reconnue, et qui
   ne réutilise pas de données du secteur public, n'a AUCUNE obligation au
   titre de ce règlement. Un outil de conformité qui lui inventerait un taux
   lui ferait acheter un chantier qui n'existe pas. Le hors-champ est donc
   une réponse à part entière, et il est affiché comme telle.

   CE QUE LE MODULE REFUSE DE DIRE
     · qu'un taux élevé vaut présomption de quoi que ce soit : le DGA ne
       prévoit ni certification, ni marquage, ni présomption de conformité.
       Le seul signe extérieur qu'il crée est le LABEL de l'article 11 §9,
       « prestataire de services d'intermédiation de données reconnu dans
       l'Union », et il s'obtient d'une autorité, pas d'un questionnaire ;
     · une exposition chiffrée. L'article 34 renvoie aux États membres le
       régime des sanctions, sans plafond européen, là où l'IA Act, NIS 2,
       DORA et le Data Act en portent un. Annoncer un montant ici serait
       l'inventer — et le module le dit à l'écran au lieu de se taire ;
     · qu'il crée une base juridique pour traiter des données personnelles.
       L'article 1er §3 l'écrit en propres termes, et c'est le pont avec le
       RGPD : voir PONT_RGPD, lu par l'écran du pont et par une règle.

   L'ARTICLE 37 EST DÉJÀ ÉCHU, ET C'EST LE PREMIER FAIT À DIRE À UN
   INTERMÉDIAIRE. Les entités qui fournissaient des services d'intermédiation
   de données au 23 juin 2022 devaient se conformer au chapitre III au plus
   tard le 24 septembre 2025. Cette date est passée. Un intermédiaire
   antérieur qui n'a pas notifié n'est pas « en retard sur un calendrier » :
   il est en infraction, et le module le qualifie ainsi.
"""
import datetime


#  ══════════════════════════════════════════════════════════════════════════
#  LA SOURCE
#  ══════════════════════════════════════════════════════════════════════════

SOURCE = {
    "cle": "dga",
    "nom": "Règlement sur la gouvernance des données",
    "sigle": "DGA",
    "reference": "Règlement (UE) 2022/868",
    "titre_long": ("Règlement (UE) 2022/868 du Parlement européen et du "
                   "Conseil du 30 mai 2022 portant sur la gouvernance "
                   "européenne des données et modifiant le règlement (UE) "
                   "2018/1724 (règlement sur la gouvernance des données)"),
    "adopte": "2022-05-30",
    "jo": "JO L 152 du 3.6.2022",
    "url": ("https://eur-lex.europa.eu/legal-content/FR/TXT/"
            "?uri=CELEX:32022R0868"),
}

#  Les dates sont celles des articles 37 et 38, relevées au texte.
APPLICABLE_DEPUIS = "2023-09-24"          # art. 38, al. 2
TRANSITOIRE_ART37 = "2025-09-24"          # art. 37
REFERENCE_ART37 = "2022-06-23"            # art. 37 : les entités « au »


#  ══════════════════════════════════════════════════════════════════════════
#  LES QUATRE CADRES DE L'ARTICLE 1er §1 — ET CELUI QUI NE CONCERNE PERSONNE
#  ══════════════════════════════════════════════════════════════════════════
#
# `assujetti` dit si le cadre crée des obligations pour un CLIENT. Le comité
# européen de l'innovation dans le domaine des données en est un organe de
# l'Union : il est dans le règlement, il n'est dans le périmètre de personne.

CADRES = (
    {"cle": "reutilisation", "article": "art. 1er §1 a) · chapitre II",
     "nom": "Réutilisation de données protégées du secteur public",
     "qui": "Organisme du secteur public détenteur, et réutilisateur",
     "assujetti": True,
     "quoi": ("Les conditions auxquelles certaines catégories de données "
              "protégées détenues par un organisme du secteur public "
              "peuvent être réutilisées.")},
    {"cle": "intermediation", "article": "art. 1er §1 b) · chapitre III",
     "nom": "Services d'intermédiation de données",
     "qui": "Prestataire de services d'intermédiation de données",
     "assujetti": True,
     "quoi": ("La notification préalable de l'article 11 et les quinze "
              "conditions de l'article 12, sous la surveillance d'une "
              "autorité compétente.")},
    {"cle": "altruisme", "article": "art. 1er §1 c) · chapitre IV",
     "nom": "Altruisme en matière de données",
     "qui": "Organisation altruiste en matière de données reconnue",
     "assujetti": True,
     "quoi": ("Un enregistrement VOLONTAIRE qui, une fois obtenu, rend "
              "contraignants les articles 18, 20, 21 et 22.")},
    {"cle": "comite", "article": "art. 1er §1 d) · chapitre VI",
     "nom": "Comité européen de l'innovation dans le domaine des données",
     "qui": "Organe de l'Union",
     "assujetti": False,
     "quoi": ("Un organe consultatif institué par le règlement. Il ne crée "
              "d'obligation pour aucune entreprise.")},
)

#  ── LES QUALITÉS QU'UN CLIENT PEUT DÉCLARER ──────────────────────────────
#
# Elles sont la porte du module. `aucune` n'est pas une absence de réponse :
# c'est une réponse, et elle ferme le règlement.

QUALITES = (
    {"cle": "organisme_public", "cadre": "reutilisation",
     "nom": "Organisme du secteur public détenant des données protégées",
     "aide": ("Au sens de l'article 2 : l'État, les autorités régionales ou "
              "locales, les organismes de droit public, et leurs "
              "associations. Une entreprise publique n'en est pas un pour "
              "ce chapitre — l'article 3 §2 a) l'exclut.")},
    {"cle": "reutilisateur", "cadre": "reutilisation",
     "nom": "Réutilisateur de données du secteur public",
     "aide": ("Vous demandez à un organisme public la réutilisation de "
              "données protégées par un secret commercial, un secret "
              "statistique, un droit de propriété intellectuelle de tiers "
              "ou la protection des données personnelles.")},
    {"cle": "intermediaire", "cadre": "intermediation",
     "nom": "Prestataire de services d'intermédiation de données",
     "aide": ("Vous exploitez une place de marché de données, un espace de "
              "données, une plateforme d'échange, ou une coopérative de "
              "données — les trois catégories de l'article 10.")},
    {"cle": "altruiste", "cadre": "altruisme",
     "nom": "Organisation altruiste en matière de données reconnue",
     "aide": ("Vous êtes inscrit, ou vous demandez l'inscription, au "
              "registre public national des organisations altruistes. "
              "L'enregistrement est volontaire ; ses obligations, non.")},
    {"cle": "aucune", "cadre": None,
     "nom": "Aucune de ces qualités",
     "aide": ("C'est le cas de la très grande majorité des entreprises. Le "
              "règlement ne vous impose alors rien, et le module s'arrête "
              "là plutôt que de vous proposer un chantier sans objet.")},
)
QUALITES_PAR_CLE = {q["cle"]: q for q in QUALITES}


#  ══════════════════════════════════════════════════════════════════════════
#  ARTICLE 3 — CE QUI EST DANS LE CHAPITRE II, ET CE QUI N'Y EST PAS
#  ══════════════════════════════════════════════════════════════════════════

CATEGORIES_ART3 = (
    ("a", "Confidentialité commerciale, y compris le secret d'affaires, le "
          "secret professionnel et le secret d'entreprise"),
    ("b", "Secret statistique"),
    ("c", "Droits de propriété intellectuelle de tiers"),
    ("d", "Protection des données à caractère personnel, dans la mesure où "
          "ces données ne relèvent pas de la directive (UE) 2019/1024"),
)

EXCLUSIONS_ART3 = (
    ("a", "Données détenues par des entreprises publiques"),
    ("b", "Données détenues par des radiodiffuseurs de service public, "
          "leurs filiales et les organismes accomplissant une mission de "
          "radiodiffusion de service public"),
    ("c", "Données détenues par des établissements culturels et "
          "d'enseignement"),
    ("d", "Données protégées pour des raisons de sécurité publique, de "
          "défense ou de sécurité nationale"),
    ("e", "Données dont la fourniture ne relève pas de la mission de "
          "service public de l'organisme concerné"),
)


#  ══════════════════════════════════════════════════════════════════════════
#  ARTICLE 10 — LES TROIS CATÉGORIES DE SERVICES D'INTERMÉDIATION
#  ══════════════════════════════════════════════════════════════════════════
#
# LA CATÉGORIE b) EST UN PONT AVEC LE RGPD, DANS LE TEXTE MÊME : ces services
# existent « notamment pour permettre l'exercice des droits des personnes
# concernées prévus par le règlement (UE) 2016/679 ». Un intermédiaire de
# cette catégorie ne choisit pas d'être aussi un sujet du RGPD : il l'est par
# construction.

SERVICES_ART10 = (
    {"cle": "b2b", "lettre": "a",
     "nom": "Intermédiation entre détenteurs et utilisateurs de données",
     "rgpd": False,
     "quoi": ("Échanges bilatéraux ou multilatéraux, plateformes, bases de "
              "données partagées, infrastructure d'interconnexion.")},
    {"cle": "personnes", "lettre": "b",
     "nom": "Intermédiation au profit des personnes concernées",
     "rgpd": True,
     "quoi": ("Entre les personnes concernées — ou les personnes physiques "
              "mettant à disposition des données non personnelles — et les "
              "utilisateurs potentiels, notamment pour permettre "
              "l'exercice des droits prévus par le RGPD.")},
    {"cle": "cooperative", "lettre": "c",
     "nom": "Services de coopératives de données",
     "rgpd": False,
     "quoi": "Les coopératives de données, nommées comme telles."},
)


#  ══════════════════════════════════════════════════════════════════════════
#  ARTICLE 12 — LES QUINZE CONDITIONS, a) À o)
#  ══════════════════════════════════════════════════════════════════════════
#
# Ce sont les quinze points qu'un intermédiaire doit tenir, et c'est le cœur
# mesurable du module. Chacun est reformulé — pas recopié — avec sa lettre,
# pour qu'un auditeur retrouve l'alinéa.

CONDITIONS_ART12 = (
    ("a", "Finalité et personne morale distincte",
     "Les données ne servent qu'à être mises à disposition des "
     "utilisateurs, et le service est fourni par une personne morale "
     "distincte."),
    ("b", "Pas de subordination à d'autres services",
     "Les modalités commerciales, tarification comprise, ne dépendent pas "
     "de l'usage d'autres services du même prestataire ou d'une entité "
     "liée."),
    ("c", "Les métadonnées d'usage ne servent qu'au service",
     "Date, heure, géolocalisation, durée et connexions établies ne "
     "servent qu'au développement du service — fraude et cybersécurité "
     "comprises — et sont communiquées au détenteur sur demande."),
    ("d", "Format reçu, conversion encadrée, non-participation",
     "L'échange se fait au format reçu ; toute conversion est justifiée et "
     "ouvre une possibilité de non-participation, sauf si le droit de "
     "l'Union l'exige."),
    ("e", "Outils supplémentaires sur demande expresse",
     "Stockage temporaire, organisation, conversion, anonymisation, "
     "pseudonymisation : seulement sur demande ou approbation expresse, et "
     "les outils de tiers ne servent à rien d'autre."),
    ("f", "Accès équitable, transparent et non discriminatoire",
     "Y compris sur les prix et les conditions de service, à l'égard des "
     "personnes concernées, des détenteurs et des utilisateurs."),
    ("g", "Procédures contre la fraude et l'abus",
     "Des procédures pour prévenir les pratiques frauduleuses ou abusives "
     "de parties cherchant à obtenir un accès."),
    ("h", "Continuité en cas d'insolvabilité",
     "Une continuité raisonnable du service, des mécanismes d'accès, de "
     "transfert et d'extraction des données stockées, et l'exercice des "
     "droits des personnes concernées."),
    ("i", "Interopérabilité avec les autres intermédiaires",
     "Par des normes ouvertes communément utilisées dans le secteur."),
    ("j", "Empêcher le transfert ou l'accès illicites",
     "Des mesures techniques, juridiques et organisationnelles contre le "
     "transfert ou l'accès illicites aux données non personnelles."),
    ("k", "Informer sans retard en cas d'accès non autorisé",
     "Le détenteur est informé sans retard de tout transfert, accès ou "
     "usage non autorisé portant sur les données non personnelles "
     "partagées."),
    ("l", "Sécurité du stockage, du traitement et de la transmission",
     "Un niveau approprié pour les données non personnelles, et le niveau "
     "le PLUS ÉLEVÉ pour les informations sensibles sous l'angle de la "
     "concurrence."),
    ("m", "Agir au mieux de l'intérêt des personnes concernées",
     "Les informer et, le cas échéant, les conseiller de manière concise, "
     "transparente et accessible sur les utilisations prévues AVANT "
     "qu'elles ne consentent."),
    ("n", "Juridiction des pays tiers, et outils de retrait",
     "Préciser la juridiction du pays tiers où l'usage est prévu, et "
     "fournir des outils pour donner ET retirer le consentement ou "
     "l'autorisation."),
    ("o", "Journal de l'activité d'intermédiation",
     "Le prestataire tient un journal de son activité d'intermédiation."),
)


#  ══════════════════════════════════════════════════════════════════════════
#  LES OBLIGATIONS DE L'ALTRUISME — ARTICLES 18, 20, 21 ET 22
#  ══════════════════════════════════════════════════════════════════════════
#
# POURQUOI CES QUATRE ET PAS LES AUTRES : ce sont exactement les articles que
# l'article 34 §1 désigne comme sanctionnables pour une organisation
# altruiste. Le reste du chapitre IV organise le registre et les autorités.

ALTRUISME = (
    ("18a", "art. 18 a)", "Mener des activités altruistes en matière de "
     "données"),
    ("18b", "art. 18 b)", "Être une personne morale constituée pour "
     "poursuivre des objectifs d'intérêt général"),
    ("18c", "art. 18 c)", "Agir sans but lucratif et être juridiquement "
     "indépendante de toute entité lucrative"),
    ("18d", "art. 18 d)", "Mener ces activités par une structure "
     "fonctionnellement distincte des autres"),
    ("18e", "art. 18 e)", "Se conformer au recueil de règles de "
     "l'article 22 §1, au plus tard dix-huit mois après l'entrée en "
     "vigueur des actes délégués"),
    ("20r", "art. 20 §1", "Tenir des registres complets et exacts : qui "
     "traite, quand et combien de temps, pour quelle finalité déclarée, "
     "contre quelles redevances"),
    ("20a", "art. 20 §2", "Établir et transmettre un rapport annuel "
     "d'activité à l'autorité compétente, avec ses cinq éléments"),
    ("21i", "art. 21 §1", "Informer préalablement, clairement et "
     "intelligiblement, des objectifs d'intérêt général et de la "
     "localisation d'un traitement en pays tiers"),
    ("21f", "art. 21 §2", "N'utiliser les données que pour les objectifs "
     "autorisés, et ne pas recourir à des pratiques commerciales "
     "trompeuses pour les solliciter"),
    ("21c", "art. 21 §3", "Fournir des outils pour obtenir le "
     "consentement ou l'autorisation, ET pour les retirer facilement"),
    ("21s", "art. 21 §4", "Assurer un niveau de sécurité approprié pour "
     "le stockage et le traitement des données non personnelles "
     "collectées"),
    ("21n", "art. 21 §5", "Informer sans retard les détenteurs de tout "
     "transfert, accès ou usage non autorisé"),
    ("21j", "art. 21 §6", "Préciser la juridiction du pays tiers lorsque "
     "le traitement est facilité pour un tiers"),
    ("22", "art. 22", "Appliquer le recueil de règles adopté par acte "
     "délégué : information, exigences techniques et de sécurité, "
     "communication, interopérabilité"),
)


#  ══════════════════════════════════════════════════════════════════════════
#  L'ARTICLE 11 — LA NOTIFICATION, ET SES DÉLAIS CHIFFRÉS
#  ══════════════════════════════════════════════════════════════════════════

NOTIFICATION = {
    "article": "art. 11",
    "obligatoire": True,
    "quand": ("Avant de fournir le service. L'activité peut commencer dès "
              "la notification soumise (§4), sous réserve des conditions "
              "du chapitre III."),
    "renseignements": (
        ("a", "Nom du prestataire"),
        ("b", "Statut juridique, forme, structure de propriété, filiales "
              "pertinentes et numéro d'enregistrement"),
        ("c", "Adresse de l'établissement principal dans l'Union, des "
              "succursales, ou du représentant légal"),
        ("d", "Un site internet public, complet et à jour"),
        ("e", "Personnes de contact et coordonnées"),
        ("f", "Description du service, et la catégorie de l'article 10 "
              "dont il relève"),
        ("g", "Date estimée de lancement, si elle diffère de la "
              "notification"),
    ),
    "delais": (
        ("declaration", 7, "jours",
         "Déclaration standardisée délivrée sur demande, dans un délai "
         "d'une semaine à compter de la notification dûment complétée "
         "(§8)."),
        ("modification", 14, "jours",
         "Toute modification des renseignements du §6 est notifiée dans "
         "les quatorze jours (§12)."),
        ("cessation", 15, "jours",
         "La cessation d'activité est notifiée dans les quinze jours "
         "(§13)."),
    ),
    "representant_legal": ("Un prestataire non établi dans l'Union qui y "
                           "propose ses services désigne un représentant "
                           "légal dans un État membre (§3)."),
    "label": ("« Prestataire de services d'intermédiation de données "
              "reconnu dans l'Union » — article 11 §9. Il s'obtient de "
              "l'autorité compétente, sur confirmation du respect des "
              "articles 11 et 12, et s'accompagne d'un logo commun que la "
              "Commission conçoit."),
    "registre": ("La Commission tient un registre public de tous les "
                 "prestataires proposant leurs services dans l'Union "
                 "(§10)."),
    "redevance": ("L'autorité peut percevoir une redevance proportionnée. "
                  "Pour les PME et les jeunes pousses, elle peut la "
                  "réduire ou y renoncer (§11)."),
}


#  ══════════════════════════════════════════════════════════════════════════
#  LE PONT AVEC LE RGPD — ARTICLE 1er §3, DANS LE TEXTE
#  ══════════════════════════════════════════════════════════════════════════
#
# C'EST LE LIEN QUE CE MODULE DOIT AU DISPOSITIF RGPD DÉJÀ EN PLACE, et il
# est TEXTUEL : chaque point ci-dessous porte l'article qui le dit. Un pont
# qui ne serait qu'une affirmation d'ergonomie n'aurait rien à faire ici.

PONT_RGPD = (
    {"cle": "applique", "article": "art. 1er §3, 1re phrase",
     "dit": ("Le droit de l'Union et le droit national en matière de "
             "protection des données à caractère personnel s'appliquent à "
             "TOUTES les données à caractère personnel traitées en lien "
             "avec le règlement."),
     "consequence": ("Votre registre des traitements et vos AIPD ne sont "
                     "pas suspendus parce qu'une opération relève du DGA."),
     "ou": "rgpd-traitements"},
    {"cle": "prevaut", "article": "art. 1er §3, 3e phrase",
     "dit": ("En cas de conflit entre le règlement et le droit de la "
             "protection des données à caractère personnel, ce dernier "
             "PRÉVAUT."),
     "consequence": ("Aucune obligation du DGA ne s'invoque contre le "
                     "RGPD : l'arbitrage est écrit d'avance."),
     "ou": "rgpd-hub"},
    {"cle": "pas_de_base", "article": "art. 1er §3, 4e phrase",
     "dit": ("Le règlement NE CRÉE PAS de base juridique pour le "
             "traitement de données à caractère personnel, et ne modifie "
             "pas les droits et obligations du RGPD."),
     "consequence": ("Relever du DGA ne dispense pas de l'article 6 du "
                     "RGPD. La base légale reste à trouver ailleurs."),
     "ou": "rgpd-traitements"},
    {"cle": "autorites", "article": "art. 1er §3, 2e phrase",
     "dit": ("Le règlement est sans préjudice des règlements (UE) 2016/679 "
             "et (UE) 2018/1725 et des directives 2002/58/CE et (UE) "
             "2016/680, y compris en ce qui concerne les pouvoirs et "
             "compétences des autorités de contrôle."),
     "consequence": ("La CNIL garde ses pouvoirs sur les traitements de "
                     "données personnelles d'un intermédiaire ou d'une "
                     "organisation altruiste."),
     "ou": "rgpd-hub"},
    {"cle": "droits", "article": "art. 10 b)",
     "dit": ("Les services d'intermédiation au profit des personnes "
             "concernées existent notamment pour PERMETTRE L'EXERCICE des "
             "droits que le RGPD leur confère."),
     "consequence": ("Un intermédiaire de cette catégorie est un sujet du "
                     "RGPD par construction, pas par accident."),
     "ou": "rgpd-pbd"},
)


#  ══════════════════════════════════════════════════════════════════════════
#  ARTICLE 34 — LES SANCTIONS, ET LE PLAFOND QUI N'EXISTE PAS
#  ══════════════════════════════════════════════════════════════════════════
#
# LE CONTRASTE AVEC LE DATA ACT EST LE FAIT LE PLUS UTILE DE CET ARTICLE.
# Le Data Act, à son article 40 §4, emprunte le plafond de l'article 83 §5
# du RGPD. Le DGA n'emprunte rien : il renvoie aux États membres, sans
# montant. Le module l'affiche, parce qu'un écran muet sur l'exposition
# laisse croire qu'elle est nulle.

SANCTIONS = {
    "article": "art. 34",
    "plafond_ue": None,
    "pourquoi_pas_de_plafond": (
        "L'article 34 §1 charge les États membres de déterminer le régime "
        "des sanctions et n'énonce aucun montant, ni en euros ni en part "
        "du chiffre d'affaires. Contrairement au Data Act, qui emprunte à "
        "l'article 83 §5 du RGPD, le DGA ne prête aucun plafond européen : "
        "l'exposition se lit dans le droit national."),
    "exigences": ("Effectives, proportionnées et dissuasives, en tenant "
                  "compte des recommandations du comité européen de "
                  "l'innovation dans le domaine des données."),
    "manquements": (
        ("art. 5 §14 et art. 31", "Transferts de données à caractère non "
         "personnel vers des pays tiers"),
        ("art. 11", "Obligation de notification du prestataire "
         "d'intermédiation"),
        ("art. 12", "Les quinze conditions de fourniture du service "
         "d'intermédiation"),
        ("art. 18, 20, 21 et 22", "Conditions d'enregistrement comme "
         "organisation altruiste reconnue"),
    ),
    "criteres": (
        ("a", "Nature, gravité, ampleur et durée de l'infraction"),
        ("b", "Mesures prises pour atténuer ou réparer le préjudice"),
        ("c", "Infractions antérieures"),
        ("d", "Avantages financiers obtenus ou pertes évitées, s'ils sont "
              "établis de manière fiable"),
        ("e", "Toute autre circonstance aggravante ou atténuante"),
    ),
}


#  ══════════════════════════════════════════════════════════════════════════
#  CE QUE LE MODULE NE PEUT PAS FAIRE, ÉCRIT AVANT QU'ON LE LUI DEMANDE
#  ══════════════════════════════════════════════════════════════════════════

RESERVES = (
    {"cle": "pas_de_certification",
     "dit": ("Le DGA ne prévoit ni certification ni marquage. Un taux élevé "
             "ici ne vaut aucune présomption de conformité.")},
    {"cle": "label_non_auto_declare",
     "dit": ("Le label de l'article 11 §9 s'obtient de l'autorité "
             "compétente sur confirmation, jamais d'un questionnaire. Ce "
             "module prépare le dossier ; il ne délivre pas le label.")},
    {"cle": "exposition_nationale",
     "dit": ("L'exposition financière n'est pas chiffrable ici : "
             "l'article 34 la renvoie au droit national, sans plafond "
             "européen.")},
    {"cle": "recueil_de_regles",
     "dit": ("Le recueil de règles de l'article 22 est un acte délégué de "
             "la Commission. Ce que l'article 18 e) rend exigible dépend de "
             "son entrée en vigueur, et le module ne la devine pas.")},
)

NOM_DU_TAUX = "Couverture des obligations de la qualité déclarée"


#  ══════════════════════════════════════════════════════════════════════════
#  LES ÉTATS D'UNE RÉPONSE — LES MÊMES QUE PARTOUT DANS SENTINEL
#  ══════════════════════════════════════════════════════════════════════════

ETATS = {
    "tenu": 1.0,
    "partiel": 0.5,
    "non_tenu": 0.0,
    "sans_objet": None,
}


def _part(cles, reponses):
    """La part d'une famille d'obligations : les « sans objet » SORTENT du
    dénominateur, les points SANS RÉPONSE comptent ZÉRO et Y RESTENT.

    POURQUOI LES « SANS OBJET » SORTENT. Un point que la qualité déclarée ne
    vise pas n'est pas un manquement : le compter contre le client lui
    reprocherait son métier. C'est la règle qu'`ocde_ia` avait posée la
    première, et elle vaut ici pour la même raison.

    POURQUOI LES SANS-RÉPONSE N'EN SORTENT PAS, ET CE QUI A ÉTÉ MESURÉ. Cette
    fonction les sortait aussi — elle ne gardait que les valeurs connues et
    divisait par leur nombre. Mesuré : un prestataire d'intermédiation qui
    déclarait tenir UN des dix-neuf points de sa qualité lisait 100 %, et
    `conformite._lire_dga` servait ce 100 % à l'indice des seize
    référentiels, qui affichait donc le DGA maîtrisé sur un dix-neuvième de
    son contenu. C'est exactement ce que `ocde_ia` et `en18286` nomment « le
    pire réglage possible » : sortir du dénominateur ce qu'on n'a pas
    regardé fait monter le taux à mesure qu'on répond MOINS. Le
    dénominateur est donc celui des obligations de la qualité, moins les
    seuls « sans objet ».

    LES TROIS NOMBRES RENDUS : le taux, le nombre de points RENSEIGNÉS — qui
    dit combien du questionnaire a été regardé, et que l'écran affiche à
    côté du taux pour qu'un taux bas se lise « pas encore répondu » et non
    « non tenu » —, et le nombre de points ATTENDUS, qui est celui sur
    lequel le taux porte.
    """
    cles = tuple(cles)
    portes, acquis, renseignes = 0, 0.0, 0
    for c in cles:
        brut = reponses.get(c)
        if brut == "sans_objet":
            continue
        portes += 1
        v = ETATS.get(brut)
        if v is not None:
            renseignes += 1
            acquis += v
    #  UN QUESTIONNAIRE VIDE NE REND PAS 0 %, IL NE REND RIEN. Compter zéro
    #  dès qu'une qualité est déclarée dirait « vous ne tenez aucun de vos
    #  dix-neuf points » à qui n'a simplement pas encore ouvert l'écran, et
    #  l'indice des seize référentiels l'afficherait. L'absence de réponse
    #  pèse zéro DANS un taux, elle ne fabrique pas un taux à elle seule —
    #  c'est aussi ce que dit la tête « vide » de l'évaluation.
    if not portes or not renseignes:
        return None, renseignes, portes
    return round(100.0 * acquis / portes), renseignes, portes


#  ══════════════════════════════════════════════════════════════════════════
#  LES OBLIGATIONS, RANGÉES PAR QUALITÉ
#  ══════════════════════════════════════════════════════════════════════════

OBLIGATIONS_PAR_QUALITE = {
    "intermediaire": tuple("art12_%s" % l for l, _, _ in CONDITIONS_ART12)
                     + ("art11_notification", "art11_site",
                        "art11_modification", "art11_cessation"),
    "altruiste": tuple("alt_%s" % c for c, _, _ in ALTRUISME),
    "organisme_public": ("art5_conditions", "art5_securite", "art6_redevances",
                         "art4_exclusivite", "art8_point_unique",
                         "art9_delai", "art31_transfert"),
    "reutilisateur": ("art5_respect", "art5_reidentification",
                      "art31_transfert"),
}

#  Les libellés des obligations qui ne viennent pas d'une table déjà écrite.
LIBELLES = {
    "art11_notification": ("art. 11 §1", "La notification a été soumise à "
                           "l'autorité compétente avant la fourniture du "
                           "service"),
    "art11_site": ("art. 11 §6 d)", "Un site internet public porte des "
                   "informations complètes et à jour sur le prestataire et "
                   "son activité"),
    "art11_modification": ("art. 11 §12", "Les modifications des "
                           "renseignements notifiés sont transmises dans "
                           "les quatorze jours"),
    "art11_cessation": ("art. 11 §13", "Une procédure existe pour notifier "
                        "la cessation d'activité dans les quinze jours"),
    "art4_exclusivite": ("art. 4", "Aucun accord d'exclusivité ne restreint "
                         "la réutilisation des données, hors les cas et "
                         "durées que l'article autorise"),
    "art5_conditions": ("art. 5", "Les conditions de réutilisation sont non "
                        "discriminatoires, proportionnées et "
                        "objectivement justifiées"),
    "art5_securite": ("art. 5 §3 et §4", "L'accès se fait dans un "
                      "environnement sécurisé de traitement, ou sur des "
                      "données anonymisées, modifiées ou agrégées"),
    "art5_respect": ("art. 5", "Les conditions posées par l'organisme "
                     "détenteur sont respectées, y compris celles qui "
                     "protègent les droits de tiers"),
    "art5_reidentification": ("art. 5 §5", "Aucune tentative de "
                              "réidentification, et notification à "
                              "l'organisme de toute réidentification "
                              "survenue"),
    "art6_redevances": ("art. 6", "Les redevances sont transparentes, non "
                        "discriminatoires, proportionnées et justifiées "
                        "par les coûts ; publiées en ligne"),
    "art8_point_unique": ("art. 8", "Les demandes passent par le point "
                          "d'information unique, ou lui sont transmises"),
    "art9_delai": ("art. 9", "Les demandes de réutilisation sont traitées "
                   "dans le délai que le droit national fixe, et un refus "
                   "est motivé"),
    "art31_transfert": ("art. 31", "Les transferts de données à caractère "
                        "non personnel vers un pays tiers sont encadrés, et "
                        "le réutilisateur est informé des conditions"),
}


def obligations():
    """Toutes les obligations du module, avec leur article et leur qualité.

    UNE SEULE SOURCE. Les écrans, le taux, les écarts et les règles lisent
    cette liste ; aucun d'eux ne redéclare un libellé.
    """
    sortie = []
    for lettre, titre, quoi in CONDITIONS_ART12:
        sortie.append({"cle": "art12_%s" % lettre, "qualite": "intermediaire",
                       "article": "art. 12 %s)" % lettre,
                       "nom": titre, "quoi": quoi})
    for cle, article, quoi in ALTRUISME:
        sortie.append({"cle": "alt_%s" % cle, "qualite": "altruiste",
                       "article": article, "nom": quoi, "quoi": quoi})
    for qualite, cles in OBLIGATIONS_PAR_QUALITE.items():
        for c in cles:
            if c in LIBELLES and not any(s["cle"] == c for s in sortie):
                article, quoi = LIBELLES[c]
                sortie.append({"cle": c, "qualite": qualite,
                               "article": article, "nom": quoi,
                               "quoi": quoi})
    return sortie


OBLIGATIONS = tuple(obligations())
OBLIGATIONS_PAR_CLE = {o["cle"]: o for o in OBLIGATIONS}


#  ══════════════════════════════════════════════════════════════════════════
#  LA QUALIFICATION, PUIS LE TAUX
#  ══════════════════════════════════════════════════════════════════════════

def qualites_declarees(declaration=None):
    d = declaration if isinstance(declaration, dict) else {}
    brut = d.get("qualites")
    if isinstance(brut, str):
        brut = [brut]
    if not isinstance(brut, (list, tuple)):
        return ()
    return tuple(q for q in brut if q in QUALITES_PAR_CLE)


def applicable(declaration=None):
    """Le règlement vous saisit-il ? Trois réponses, pas deux.

    `ok is None` n'est pas « non » : c'est « la question n'a pas été
    posée ». Les confondre ferait afficher « hors champ » à qui n'a rien
    déclaré, et c'est le plus sûr moyen de rater une obligation.
    """
    qs = qualites_declarees(declaration)
    if not qs:
        return {"ok": None, "qualites": (), "cadres": (),
                "dit": ("Aucune qualité n'est déclarée. Le règlement "
                        "n'établit que quatre cadres : sans savoir si vous "
                        "relevez de l'un d'eux, il n'y a rien à mesurer — "
                        "et ce n'est pas la même chose qu'un hors-champ.")}
    if "aucune" in qs and len(qs) == 1:
        return {"ok": False, "qualites": qs, "cadres": (),
                "dit": ("HORS CHAMP. Vous n'êtes ni un organisme du secteur "
                        "public détenant des données protégées, ni un "
                        "réutilisateur, ni un prestataire de services "
                        "d'intermédiation de données, ni une organisation "
                        "altruiste reconnue. Le règlement (UE) 2022/868 ne "
                        "vous impose alors aucune obligation. C'est le cas "
                        "de la très grande majorité des entreprises, et le "
                        "dire vaut mieux que de vous proposer un chantier "
                        "sans objet.")}
    utiles = tuple(q for q in qs if q != "aucune")
    cadres = tuple(sorted({QUALITES_PAR_CLE[q]["cadre"] for q in utiles}))
    return {"ok": True, "qualites": utiles, "cadres": cadres,
            "dit": ("Vous relevez de %d des quatre cadres du règlement. Les "
                    "obligations affichées sont celles de vos qualités, et "
                    "d'elles seules." % len(cadres))}


def score(declaration=None):
    d = declaration if isinstance(declaration, dict) else {}
    rep = d.get("reponses") if isinstance(d.get("reponses"), dict) else {}
    champ = applicable(d)
    parts, renseignes, attendus = {}, 0, 0
    for q in champ["qualites"]:
        cles = OBLIGATIONS_PAR_QUALITE.get(q, ())
        taux, n, total = _part(cles, rep)
        parts[q] = taux
        renseignes += n
        attendus += total
    retenus = [v for v in parts.values() if v is not None]
    return {
        "parts": parts,
        "total": (round(sum(retenus) / len(retenus)) if retenus else None),
        "renseignes": renseignes,
        "attendus": attendus,
    }


def retard_art37(declaration=None, aujourdhui=None):
    """L'article 37 est échu — pour qui fournissait déjà le service.

    CE QUE CETTE FONCTION REFUSE DE FAIRE : qualifier d'« en retard » un
    intermédiaire né après le 23 juin 2022. L'article 37 ne vise QUE les
    entités qui fournissaient le service à cette date ; les autres sont
    tenues par l'article 11 dès qu'elles commencent, et c'est un autre
    manquement.
    """
    d = declaration if isinstance(declaration, dict) else {}
    jour = aujourdhui or datetime.date.today().isoformat()
    if "intermediaire" not in qualites_declarees(d):
        return None
    if d.get("anterieur_2022") is not True:
        return None
    echu = jour > TRANSITOIRE_ART37
    notifie = (d.get("reponses") or {}).get("art11_notification") == "tenu"
    return {
        "article": "art. 37",
        "reference": REFERENCE_ART37,
        "echeance": TRANSITOIRE_ART37,
        "echue": echu,
        "notifie": notifie,
        "dit": (("L'échéance de l'article 37 est passée depuis le %s. Un "
                 "prestataire qui fournissait déjà le service au %s et qui "
                 "n'a pas notifié n'est pas en retard sur un calendrier : "
                 "il est en infraction." % (TRANSITOIRE_ART37,
                                            REFERENCE_ART37))
                if echu and not notifie else
                ("L'échéance de l'article 37 est passée depuis le %s, et la "
                 "notification est déclarée faite."
                 % TRANSITOIRE_ART37) if echu else
                ("L'échéance de l'article 37 tombe le %s."
                 % TRANSITOIRE_ART37)),
    }


def evaluer(declaration=None, aujourdhui=None):
    d = declaration if isinstance(declaration, dict) else {}
    rep = d.get("reponses") if isinstance(d.get("reponses"), dict) else {}
    inconnus = sorted(k for k in rep if k not in OBLIGATIONS_PAR_CLE)
    if inconnus:
        return {"ok": False, "motif": "obligations_inconnues",
                "detail": inconnus[:8]}
    mauvais = sorted(k for k, v in rep.items() if v not in ETATS)
    if mauvais:
        return {"ok": False, "motif": "etats_inconnus", "detail": mauvais[:8]}

    champ = applicable(d)
    sc = score(d)
    art37 = retard_art37(d, aujourdhui)

    if champ["ok"] is None:
        tete, dit = "non_qualifie", champ["dit"]
    elif champ["ok"] is False:
        tete, dit = "hors_champ", champ["dit"]
    elif not sc["renseignes"]:
        tete, dit = "vide", (
            "La qualification est faite, rien n'est renseigné. Le module ne "
            "rend aucun chiffre par défaut : un questionnaire vide n'est "
            "pas une conformité à zéro, c'est une conformité qu'on n'a pas "
            "regardée.")
    elif art37 and art37["echue"] and not art37["notifie"]:
        tete, dit = "art37_echu", art37["dit"]
    else:
        tete, dit = "mesure", (
            "%d %% des obligations attendues de vos qualités sont "
            "déclarées tenues, sur %d points attendus dont %d "
            "renseigné(s). Un point qu'on n'a pas regardé compte zéro : "
            "le taux monte quand on répond, jamais quand on s'abstient."
            % (sc["total"] or 0, sc["attendus"], sc["renseignes"]))

    return {
        "ok": True,
        "aujourdhui": (aujourdhui or datetime.date.today().isoformat()),
        "applicable": champ,
        "qualites": list(champ["qualites"]),
        "cadres": list(champ["cadres"]),
        "parts": dict(sc["parts"]),
        "score": sc,
        "art37": art37,
        "applicable_depuis": APPLICABLE_DEPUIS,
        "obligations": len(OBLIGATIONS),
        "renseignes": sc["renseignes"],
        "pont_rgpd": [dict(p) for p in PONT_RGPD],
        "sanctions": {"plafond_ue": None,
                      "pourquoi": SANCTIONS["pourquoi_pas_de_plafond"]},
        "reserves": [dict(r) for r in RESERVES],
        "tete": tete, "dit": dit,
        "presomption": False,
        "nom_du_taux": NOM_DU_TAUX,
    }


def referentiel():
    """La table, telle que l'écran la demande.

    LE PONT RGPD EST DANS LA CHARGE, pas dans le gabarit : une règle le
    vérifie ici, parce que c'est le lien que la demande exigeait et qu'un
    lien écrit dans le HTML se perdrait à la première refonte.
    """
    return {
        "source": dict(SOURCE),
        "applicable_depuis": APPLICABLE_DEPUIS,
        "transitoire_art37": TRANSITOIRE_ART37,
        "reference_art37": REFERENCE_ART37,
        "cadres": [dict(c) for c in CADRES],
        "qualites": [dict(q) for q in QUALITES],
        "categories_art3": [{"lettre": l, "quoi": q}
                            for l, q in CATEGORIES_ART3],
        "exclusions_art3": [{"lettre": l, "quoi": q}
                            for l, q in EXCLUSIONS_ART3],
        "services_art10": [dict(s) for s in SERVICES_ART10],
        "conditions_art12": [{"lettre": l, "nom": n, "quoi": q}
                             for l, n, q in CONDITIONS_ART12],
        "altruisme": [{"cle": c, "article": a, "quoi": q}
                      for c, a, q in ALTRUISME],
        "notification": {
            "article": NOTIFICATION["article"],
            "quand": NOTIFICATION["quand"],
            "renseignements": [{"lettre": l, "quoi": q}
                               for l, q in NOTIFICATION["renseignements"]],
            "delais": [{"cle": c, "valeur": v, "unite": u, "quoi": q}
                       for c, v, u, q in NOTIFICATION["delais"]],
            "representant_legal": NOTIFICATION["representant_legal"],
            "label": NOTIFICATION["label"],
            "registre": NOTIFICATION["registre"],
            "redevance": NOTIFICATION["redevance"],
        },
        "obligations": [dict(o) for o in OBLIGATIONS],
        "pont_rgpd": [dict(p) for p in PONT_RGPD],
        "sanctions": {
            "article": SANCTIONS["article"],
            "plafond_ue": SANCTIONS["plafond_ue"],
            "pourquoi_pas_de_plafond": SANCTIONS["pourquoi_pas_de_plafond"],
            "exigences": SANCTIONS["exigences"],
            "manquements": [{"article": a, "quoi": q}
                            for a, q in SANCTIONS["manquements"]],
            "criteres": [{"lettre": l, "quoi": q}
                         for l, q in SANCTIONS["criteres"]],
        },
        "etats": sorted(ETATS),
        "reserves": [dict(r) for r in RESERVES],
        "nom_du_taux": NOM_DU_TAUX,
        "presomption": False,
    }



def plan(declaration=None, limite=24):
    """CE QU'IL RESTE À FAIRE, DANS L'ORDRE OÙ ÇA DÉBLOQUE.

    LE PREMIER RANG N'EST PAS UNE OBLIGATION, C'EST LA QUALIFICATION. Tant
    qu'aucune qualité n'est déclarée, aucune action n'a de sens : proposer
    « tenir les quinze conditions de l'article 12 » à qui n'est pas
    intermédiaire de données serait vendre un chantier inexistant.

    LE DEUXIÈME RANG EST L'ARTICLE 37 QUAND IL EST ÉCHU, parce qu'il ne se
    rattrape pas : la notification manquante d'un intermédiaire antérieur au
    23 juin 2022 est un manquement constitué, pas un retard.
    """
    d = declaration if isinstance(declaration, dict) else {}
    rep = d.get("reponses") if isinstance(d.get("reponses"), dict) else {}
    champ = applicable(d)
    actions = []
    if champ["ok"] is None:
        actions.append({"cle": "qualifier", "quoi": (
            "Déclarer votre qualité au titre du règlement : organisme du "
            "secteur public, réutilisateur, prestataire de services "
            "d'intermédiation de données, organisation altruiste — ou "
            "aucune des quatre."), "ou": "dga · qualification"})
        return {"actions": actions[:limite]}
    if champ["ok"] is False:
        return {"actions": []}
    art37 = retard_art37(d)
    if art37 and art37["echue"] and not art37["notifie"]:
        actions.append({"cle": "art37", "quoi": (
            "Notifier sans délai l'autorité compétente : l'échéance de "
            "l'article 37 est passée depuis le %s pour un prestataire qui "
            "fournissait déjà le service au %s."
            % (TRANSITOIRE_ART37, REFERENCE_ART37)),
            "ou": "dga · obligations"})
    for q in champ["qualites"]:
        for c in OBLIGATIONS_PAR_QUALITE.get(q, ()):
            etat = rep.get(c)
            if etat in ("tenu", "sans_objet"):
                continue
            o = OBLIGATIONS_PAR_CLE[c]
            verbe = ("Compléter" if etat == "partiel"
                     else "Tenir" if etat == "non_tenu" else "Renseigner")
            actions.append({"cle": c,
                            "quoi": "%s — %s : %s" % (verbe, o["article"],
                                                      o["quoi"]),
                            "ou": "dga · obligations"})
    return {"actions": actions[:limite]}

#  ══════════════════════════════════════════════════════════════════════════
#  LE GARDIEN — IL LÈVE RuntimeError, PAS AssertionError
#  ══════════════════════════════════════════════════════════════════════════
#
# `python -O` retire les assertions. Un gardien écrit avec `assert` ne garde
# donc rien en production, là où il sert le plus.

def _verifier():
    if len(CONDITIONS_ART12) != 15:
        raise RuntimeError(
            "dga : l'article 12 porte quinze conditions, a) a o) ; la table "
            "en declare %d." % len(CONDITIONS_ART12))
    lettres = [l for l, _, _ in CONDITIONS_ART12]
    if lettres != list('abcdefghijklmno'):
        raise RuntimeError(
            "dga : les lettres de l'article 12 doivent aller de a a o, dans "
            "l'ordre ; la table dit %r." % (lettres,))
    if len(CATEGORIES_ART3) != 4:
        raise RuntimeError(
            "dga : l'article 3 §1 porte quatre categories de donnees "
            "protegees ; la table en declare %d." % len(CATEGORIES_ART3))
    if len(EXCLUSIONS_ART3) != 5:
        raise RuntimeError(
            "dga : l'article 3 §2 porte cinq exclusions ; la table en "
            "declare %d." % len(EXCLUSIONS_ART3))
    if len(SERVICES_ART10) != 3:
        raise RuntimeError(
            "dga : l'article 10 porte trois categories de services, a) a "
            "c) ; la table en declare %d." % len(SERVICES_ART10))
    if sum(1 for s in SERVICES_ART10 if s["rgpd"]) != 1:
        raise RuntimeError(
            "dga : une seule categorie de l'article 10 — la b) — nomme les "
            "droits du RGPD ; la table en marque %d."
            % sum(1 for s in SERVICES_ART10 if s["rgpd"]))
    if len(tuple(c for c in CADRES if c["assujetti"])) != 3:
        raise RuntimeError(
            "dga : l'article 1er §1 etablit quatre cadres, dont TROIS "
            "creent des obligations pour un client ; la table en marque %d."
            % len(tuple(c for c in CADRES if c["assujetti"])))
    if SANCTIONS["plafond_ue"] is not None:
        raise RuntimeError(
            "dga : l'article 34 n'enonce AUCUN plafond europeen — il renvoie "
            "aux Etats membres. Un montant pose ici serait invente.")
    if APPLICABLE_DEPUIS >= TRANSITOIRE_ART37:
        raise RuntimeError(
            "dga : l'echeance transitoire de l'article 37 (%s) est "
            "posterieure a l'entree en application (%s) ; la table dit le "
            "contraire." % (TRANSITOIRE_ART37, APPLICABLE_DEPUIS))
    #  LE PONT RGPD : cinq provisions, chacune avec son article.
    if len(PONT_RGPD) != 5:
        raise RuntimeError(
            "dga : le pont avec le RGPD repose sur cinq dispositions du "
            "texte ; la table en declare %d." % len(PONT_RGPD))
    for p in PONT_RGPD:
        if not p.get("article") or not p.get("dit") or not p.get("ou"):
            raise RuntimeError(
                "dga : chaque point du pont RGPD porte son article, ce "
                "qu'il dit et ou il mene ; %r en manque." % (p.get("cle"),))
    #  Une qualite sans obligations declarees serait un ecran vide.
    for q in QUALITES:
        if q["cle"] == "aucune":
            continue
        if not OBLIGATIONS_PAR_QUALITE.get(q["cle"]):
            raise RuntimeError(
                "dga : la qualite %r ne porte aucune obligation ; un ecran "
                "de qualification qui mene au vide est pire qu'une qualite "
                "absente." % q["cle"])
    #  Chaque obligation doit etre rattachee a une qualite connue.
    for o in OBLIGATIONS:
        if o["qualite"] not in QUALITES_PAR_CLE:
            raise RuntimeError(
                "dga : l'obligation %r est rattachee a la qualite inconnue "
                "%r." % (o["cle"], o["qualite"]))


_verifier()
