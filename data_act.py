# -*- coding: utf-8 -*-
"""LE RÈGLEMENT SUR LES DONNÉES — ET L'EXPOSITION QU'IL EMPRUNTE AU RGPD.
   ═══════════════════════════════════════════════════════════════════════

   Règlement (UE) 2023/2854 du 13 décembre 2023, applicable depuis le
   12 septembre 2025. Cité par numéro et par intitulé d'article ; son texte
   n'est pas recopié — la règle de la maison.

   CE QUE CE MODULE APPORTE QUE LES QUINZE AUTRES N'APPORTAIENT PAS.
   Sentinel mesurait l'IA, la cybersécurité, la résilience et les données
   PERSONNELLES. Il ne mesurait rien sur les données NON personnelles que
   l'entreprise produit, détient, vend ou héberge. Le Data Act est ce
   chaînon : il porte sur les données d'un produit connecté, sur ce qu'un
   détenteur doit mettre à disposition, sur les clauses qu'il ne peut plus
   imposer, et sur la liberté de quitter son fournisseur de cloud.

   L'EXPOSITION FINANCIÈRE EST EMPRUNTÉE AU RGPD, ET C'EST LE FAIT LE PLUS
   LOURD DU RÈGLEMENT. L'article 40 §4 dit que, pour les manquements aux
   chapitres II, III et V, les autorités de contrôle du RGPD peuvent
   infliger des amendes administratives au titre de l'article 83 du RGPD,
   « jusqu'à concurrence du montant visé à l'article 83, paragraphe 5 ».
   Ce montant est de 20 000 000 EUR ou, pour une entreprise, 4 % du chiffre
   d'affaires annuel mondial total de l'exercice précédent, LE PLUS ÉLEVÉ
   étant retenu. Deux conséquences que les clients découvrent trop tard :

     · c'est la CNIL — l'autorité RGPD — qui sanctionne, pas une autorité
       nouvelle. Le Data Act n'ouvre pas un second guichet : il élargit la
       compétence de celui qui existe ;
     · l'article 83 §5 ne connaît AUCUNE réduction pour les PME. Là où
       l'IA Act, à son article 99 §6, retient le plafond le PLUS BAS pour
       une PME, le RGPD retient toujours le plus élevé. Une PME exposée au
       titre du Data Act l'est donc plus durement qu'au titre de l'IA Act.

   ET IL Y A UNE ÉCHÉANCE DÉJÀ ÉCHUE, LA PREMIÈRE CHOSE À DIRE À UN
   FABRICANT. L'obligation d'accessibilité dès la conception de l'article 3
   §1 s'applique aux produits connectés et services connexes mis sur le
   marché APRÈS le 12 septembre 2026. Cette date est passée. Un produit mis
   sur le marché depuis lors doit être conçu pour rendre ses données
   accessibles ; ce n'est plus un projet, c'est un état exigible.

   CE QUE LE MODULE REFUSE DE DIRE
     · qu'il crée une base juridique. L'article 4 §12 dit le contraire en
       propres termes : quand l'utilisateur n'est pas la personne concernée,
       les données personnelles ne lui sont mises à disposition QUE s'il
       existe un fondement juridique valable au titre de l'article 6 du
       RGPD. L'accès Data Act ne fabrique pas de base légale ;
     · que l'accès de son chapitre II remplace les articles 15 et 20 du
       RGPD. L'article 1er §5 dit qu'il les COMPLÈTE. Deux droits, deux
       régimes, deux délais — et un client qui croirait les avoir fusionnés
       répondrait mal aux deux ;
     · qu'une PME est hors champ. L'article 7 exempte les micro et petites
       entreprises du chapitre II, SOUS CONDITIONS, et les moyennes
       seulement pour un temps. Les autres chapitres ne connaissent pas
       cette exemption.
"""
import datetime


#  ══════════════════════════════════════════════════════════════════════════
#  LA SOURCE
#  ══════════════════════════════════════════════════════════════════════════

SOURCE = {
    "cle": "data_act",
    "nom": "Règlement sur les données",
    "sigle": "Data Act",
    "reference": "Règlement (UE) 2023/2854",
    "titre_long": ("Règlement (UE) 2023/2854 du Parlement européen et du "
                   "Conseil du 13 décembre 2023 concernant des règles "
                   "harmonisées portant sur l'équité de l'accès aux données "
                   "et de l'utilisation des données et modifiant le "
                   "règlement (UE) 2017/2394 et la directive (UE) 2020/1828 "
                   "(règlement sur les données)"),
    "adopte": "2023-12-13",
    "jo": "JO L du 22.12.2023",
    "url": ("https://eur-lex.europa.eu/legal-content/FR/TXT/"
            "?uri=CELEX:32023R2854"),
}


#  ══════════════════════════════════════════════════════════════════════════
#  LES DATES DE L'ARTICLE 50 — RELEVÉES AU TEXTE, PAS DE MÉMOIRE
#  ══════════════════════════════════════════════════════════════════════════

ENTREE_EN_VIGUEUR = "2024-01-11"
APPLICABLE_DEPUIS = "2025-09-12"

ECHEANCES = (
    {"cle": "application", "date": APPLICABLE_DEPUIS, "article": "art. 50",
     "quoi": "Le règlement est applicable.",
     "qui": "tous"},
    {"cle": "art3_produits", "date": "2026-09-12", "article": "art. 50, al. 3",
     "quoi": ("L'obligation de l'article 3 §1 — accessibilité des données "
              "dès la conception — s'applique aux produits connectés et aux "
              "services connexes mis sur le marché après cette date."),
     "qui": "fabricant"},
    {"cle": "chap4_nouveaux", "date": APPLICABLE_DEPUIS,
     "article": "art. 50, al. 5",
     "quoi": ("Le chapitre IV — clauses contractuelles abusives — "
              "s'applique aux contrats conclus après cette date."),
     "qui": "detenteur"},
    {"cle": "art29_frais_nuls", "date": "2027-01-12", "article": "art. 29 §1",
     "quoi": ("Plus aucun frais de changement de fournisseur ne peut être "
              "imposé au client. Jusque-là, des frais RÉDUITS sont "
              "admis, plafonnés aux coûts directement liés (art. 29 §2 "
              "et §3)."),
     "qui": "cloud"},
    {"cle": "chap4_anciens", "date": "2027-09-12", "article": "art. 50, al. 6",
     "quoi": ("Le chapitre IV s'applique aussi aux contrats conclus le "
              "12 septembre 2025 ou avant, s'ils sont à durée indéterminée "
              "ou viennent à échéance au moins dix ans à compter du "
              "11 janvier 2024."),
     "qui": "detenteur"},
)


#  ══════════════════════════════════════════════════════════════════════════
#  LES CHAPITRES, ET LEQUEL EMPRUNTE LE PLAFOND DU RGPD
#  ══════════════════════════════════════════════════════════════════════════
#
# `rgpd_art83` est la clé de l'exposition : l'article 40 §4 ne désigne que
# les chapitres II, III et V. Pour les autres, le régime est national et
# aucun plafond européen ne s'applique.

CHAPITRES = (
    {"cle": "II", "articles": "art. 3 à 7",
     "nom": "Partage de données entre entreprises et consommateurs, et "
            "entre entreprises",
     "quoi": ("Les données, hors contenu, relatives à la performance, à "
              "l'utilisation et à l'environnement des produits connectés "
              "et des services connexes."),
     "rgpd_art83": True},
    {"cle": "III", "articles": "art. 8 à 12",
     "nom": "Obligations des détenteurs tenus de mettre des données à "
            "disposition en vertu du droit de l'Union",
     "quoi": ("Les données du secteur privé soumises à une obligation "
              "légale de partage : conditions équitables, compensation, "
              "règlement des litiges."),
     "rgpd_art83": True},
    {"cle": "IV", "articles": "art. 13",
     "nom": "Clauses contractuelles abusives imposées unilatéralement",
     "quoi": ("Les données du secteur privé auxquelles il est accédé sur "
              "la base d'un contrat entre entreprises."),
     "rgpd_art83": False},
    {"cle": "V", "articles": "art. 14 à 22",
     "nom": "Mise à disposition au profit d'organismes du secteur public "
            "en cas de besoin exceptionnel",
     "quoi": ("Les données du secteur privé, en particulier non "
              "personnelles, réclamées pour une mission d'intérêt "
              "public."),
     "rgpd_art83": True},
    {"cle": "VI", "articles": "art. 23 à 31",
     "nom": "Changement de fournisseur de services de traitement de données",
     "quoi": ("Les données et les services traités par les fournisseurs de "
              "services de traitement de données — le cloud."),
     "rgpd_art83": False},
    {"cle": "VII", "articles": "art. 32",
     "nom": "Accès international illicite aux données non personnelles",
     "quoi": ("Les données non personnelles détenues dans l'Union par des "
              "fournisseurs de services de traitement de données."),
     "rgpd_art83": False},
)
CHAPITRES_PAR_CLE = {c["cle"]: c for c in CHAPITRES}


#  ══════════════════════════════════════════════════════════════════════════
#  LES SEPT QUALITÉS DE L'ARTICLE 1er §3 — ET ELLES SONT EXTRATERRITORIALES
#  ══════════════════════════════════════════════════════════════════════════
#
# Le texte répète « quel que soit le lieu d'établissement » pour le
# fabricant, le détenteur et le fournisseur de cloud. Une société établie
# hors de l'Union qui met un produit connecté sur le marché de l'Union, ou
# qui sert des clients dans l'Union, est tenue. C'est dit à l'écran, parce
# que c'est le contresens le plus fréquent.

QUALITES = (
    {"cle": "fabricant", "lettre": "a", "chapitres": ("II",),
     "nom": "Fabricant d'un produit connecté, ou fournisseur d'un service "
            "connexe",
     "extraterritorial": True,
     "aide": ("Le produit est mis sur le marché de l'Union, quel que soit "
              "votre lieu d'établissement. Les assistants virtuels en font "
              "partie dès qu'ils interagissent avec un produit ou un "
              "service connecté (art. 1er §4).")},
    {"cle": "utilisateur", "lettre": "b", "chapitres": ("II",),
     "nom": "Utilisateur, dans l'Union, d'un produit connecté ou d'un "
            "service connexe",
     "extraterritorial": False,
     "aide": ("Vous exploitez des machines, des véhicules, des équipements "
              "industriels ou médicaux connectés. C'est la qualité qui "
              "donne des DROITS plutôt que des obligations — mais elle en "
              "porte aussi : articles 4 §10, §11 et 6.")},
    {"cle": "detenteur", "lettre": "c", "chapitres": ("II", "III", "IV"),
     "nom": "Détenteur de données mettant des données à disposition de "
            "destinataires dans l'Union",
     "extraterritorial": True,
     "aide": ("Vous détenez les données d'un produit ou d'un service et "
              "les mettez à disposition — sur demande de l'utilisateur, ou "
              "au titre d'une obligation légale.")},
    {"cle": "destinataire", "lettre": "d", "chapitres": ("II", "III"),
     "nom": "Destinataire de données dans l'Union",
     "extraterritorial": False,
     "aide": ("Des données vous sont mises à disposition à la demande d'un "
              "utilisateur. L'article 6 encadre strictement ce que vous "
              "pouvez en faire.")},
    {"cle": "secteur_public", "lettre": "e", "chapitres": ("V",),
     "nom": "Organisme du secteur public demandant des données pour un "
            "besoin exceptionnel",
     "extraterritorial": False,
     "aide": ("Vous invoquez un besoin exceptionnel au titre des "
              "articles 14 à 22 pour exécuter une mission d'intérêt "
              "public.")},
    {"cle": "cloud", "lettre": "f", "chapitres": ("VI", "VII"),
     "nom": "Fournisseur de services de traitement de données",
     "extraterritorial": True,
     "aide": ("Infrastructure, plateforme ou logiciel en tant que service, "
              "fourni à des clients dans l'Union, quel que soit votre lieu "
              "d'établissement.")},
    {"cle": "espace_donnees", "lettre": "g", "chapitres": ("VIII",),
     "nom": "Participant à un espace de données, ou vendeur d'applications "
            "à contrats intelligents",
     "extraterritorial": False,
     "aide": ("Vous participez à un espace de données, ou vous déployez "
              "des contrats intelligents pour des tiers dans l'exécution "
              "d'un accord de partage de données.")},
    {"cle": "aucune", "lettre": None, "chapitres": (),
     "nom": "Aucune de ces qualités",
     "extraterritorial": False,
     "aide": ("Le règlement ne vous saisit alors pas. C'est rare : dès "
              "qu'une entreprise consomme du cloud, elle est cliente d'un "
              "fournisseur et bénéficie du chapitre VI — mais en "
              "bénéficier n'est pas y être assujetti.")},
)
QUALITES_PAR_CLE = {q["cle"]: q for q in QUALITES}


#  ══════════════════════════════════════════════════════════════════════════
#  L'ARTICLE 7 — L'EXEMPTION QUI NE VAUT QUE POUR LE CHAPITRE II
#  ══════════════════════════════════════════════════════════════════════════

EXEMPTION_ART7 = {
    "article": "art. 7 §1",
    "chapitre": "II",
    "qui": ("Les microentreprises et les petites entreprises, au sens de "
            "la recommandation 2003/361/CE."),
    "conditions": (
        ("partenaire", "Ne pas avoir d'entreprise partenaire ou liée, au "
                       "sens de l'article 3 de l'annexe de la "
                       "recommandation 2003/361/CE, qui ne soit pas elle "
                       "aussi micro ou petite."),
        ("sous_traitance", "Ne pas travailler en sous-traitance pour "
                           "fabriquer ou concevoir un produit connecté, ni "
                           "pour fournir un service connexe."),
    ),
    "moyenne": ("Une entreprise moyenne est exemptée tant qu'elle l'est "
                "depuis moins d'un an, et ses produits le sont pendant un "
                "an après leur mise sur le marché."),
    "ce_qu_elle_ne_couvre_pas": (
        "L'exemption ne vaut QUE pour le chapitre II. Les clauses abusives "
        "du chapitre IV, le changement de fournisseur du chapitre VI et "
        "l'accès international du chapitre VII ne la connaissent pas."),
    "non_contournable": ("Article 7 §2 : toute clause qui exclut les "
                         "droits de l'utilisateur du chapitre II, y "
                         "déroge ou en modifie les effets au détriment de "
                         "l'utilisateur NE LE LIE PAS."),
}


#  ══════════════════════════════════════════════════════════════════════════
#  L'ARTICLE 13 — TROIS CLAUSES ABUSIVES, SEPT PRÉSUMÉES
#  ══════════════════════════════════════════════════════════════════════════
#
# LA DISTINCTION EST TOUT L'ARTICLE. Le §4 énumère ce qui EST abusif ; le §5,
# ce qui est PRÉSUMÉ abusif — donc discutable, charge de preuve renversée. Un
# écran qui les mélangerait ferait croire à dix interdictions fermes, et
# ferait renégocier des contrats qui n'avaient pas à l'être.

CLAUSES_ART13 = (
    ("4a", "abusive", "art. 13 §4 a)",
     "Exclure ou limiter la responsabilité de celui qui a imposé la clause "
     "en cas d'acte intentionnel ou de négligence grave"),
    ("4b", "abusive", "art. 13 §4 b)",
     "Exclure les voies de recours de la partie à qui la clause est "
     "imposée, ou la responsabilité de celui qui l'impose"),
    ("4c", "abusive", "art. 13 §4 c)",
     "Donner à celui qui impose la clause le droit exclusif de dire si les "
     "données sont conformes au contrat, ou d'interpréter une clause"),
    ("5a", "presumee", "art. 13 §5 a)",
     "Limiter de manière inappropriée les voies de recours, ou étendre la "
     "responsabilité de la partie à qui la clause est imposée"),
    ("5b", "presumee", "art. 13 §5 b)",
     "Permettre d'accéder aux données de l'autre partie et de les utiliser "
     "au détriment grave de ses intérêts légitimes — données "
     "commercialement sensibles, secrets d'affaires, propriété "
     "intellectuelle"),
    ("5c", "presumee", "art. 13 §5 c)",
     "Empêcher la partie à qui la clause est imposée d'utiliser les "
     "données qu'elle a fournies ou générées pendant le contrat"),
    ("5d", "presumee", "art. 13 §5 d)",
     "L'empêcher de résilier l'accord dans un délai raisonnable"),
    ("5e", "presumee", "art. 13 §5 e)",
     "L'empêcher d'obtenir une copie des données qu'elle a fournies ou "
     "générées, pendant le contrat ou dans un délai raisonnable après"),
    ("5f", "presumee", "art. 13 §5 f)",
     "Permettre une résiliation dans un délai excessivement court au "
     "regard des alternatives disponibles, sauf motifs sérieux"),
    ("5g", "presumee", "art. 13 §5 g)",
     "Permettre de modifier substantiellement le prix ou une condition de "
     "fond sans motif valable ni droit de résiliation"),
)


#  ══════════════════════════════════════════════════════════════════════════
#  LES OBLIGATIONS, PAR QUALITÉ
#  ══════════════════════════════════════════════════════════════════════════

OBLIGATIONS_BRUTES = (
    #  ── FABRICANT / FOURNISSEUR DE SERVICE CONNEXE — CHAPITRE II ─────────
    ("fab_conception", "fabricant", "II", "art. 3 §1",
     "Le produit est conçu et fabriqué, le service conçu et fourni, de "
     "sorte que les données et leurs métadonnées soient accessibles à "
     "l'utilisateur par défaut : aisément, en sécurité, SANS FRAIS, dans un "
     "format complet, structuré, couramment utilisé et lisible par machine"),
    ("fab_info_achat", "fabricant", "II", "art. 3 §2",
     "Avant la vente, la location ou le crédit-bail, l'utilisateur reçoit "
     "les quatre informations du §2 : type, format et volume estimé ; "
     "génération en continu et en temps réel ; stockage et durée ; moyens "
     "d'accès, d'extraction et d'effacement"),
    ("fab_info_service", "fabricant", "II", "art. 3 §3",
     "Avant la fourniture d'un service connexe, l'utilisateur reçoit les "
     "neuf informations du §3, dont l'identité du détenteur de données, le "
     "droit de réclamation et l'existence de secrets d'affaires"),
    #  ── DÉTENTEUR DE DONNÉES — CHAPITRES II ET III ───────────────────────
    ("det_acces", "detenteur", "II", "art. 4 §1",
     "Quand l'utilisateur ne peut pas accéder directement aux données, "
     "elles sont rendues facilement accessibles sans retard injustifié, à "
     "qualité égale à celle dont bénéficie le détenteur, sans frais, sur "
     "simple demande électronique"),
    ("det_neutralite", "detenteur", "II", "art. 4 §4",
     "Aucune interface ne rend indûment difficile l'exercice des droits : "
     "pas de choix non neutre, pas d'atteinte à l'autonomie de décision"),
    ("det_minimisation", "detenteur", "II", "art. 4 §5",
     "La vérification de la qualité d'utilisateur n'exige que les "
     "informations nécessaires, et aucune donnée de connexion n'est "
     "conservée au-delà du nécessaire"),
    ("det_secrets", "detenteur", "II", "art. 4 §6 à §8",
     "Les secrets d'affaires sont recensés, des mesures proportionnées "
     "sont convenues avec l'utilisateur, et tout refus, blocage ou "
     "suspension est motivé par écrit ET notifié à l'autorité compétente"),
    ("det_base_rgpd", "detenteur", "II", "art. 4 §12",
     "Quand l'utilisateur n'est pas la personne concernée, les données "
     "personnelles ne sont mises à disposition que s'il existe une base "
     "juridique valable au titre de l'article 6 du RGPD — et, le cas "
     "échéant, les conditions de l'article 9 du RGPD et de l'article 5 §3 "
     "de la directive 2002/58/CE"),
    ("det_contrat_usage", "detenteur", "II", "art. 4 §13 et §14",
     "Le détenteur n'utilise les données non personnelles facilement "
     "accessibles que sur la base d'un contrat avec l'utilisateur, n'en "
     "tire pas d'informations sur sa position commerciale, et ne les "
     "transmet à aucun tiers hors exécution de ce contrat"),
    ("det_partage_tiers", "detenteur", "II", "art. 5",
     "Sur demande de l'utilisateur, les données sont mises à la "
     "disposition d'un tiers, dans les mêmes conditions de qualité et de "
     "délai"),
    ("det_frand", "detenteur", "III", "art. 8",
     "Les données sont mises à disposition à des conditions équitables, "
     "raisonnables et non discriminatoires, et de manière transparente ; "
     "aucune exclusivité hors demande de l'utilisateur"),
    ("det_compensation", "detenteur", "III", "art. 9",
     "La compensation convenue est non discriminatoire et raisonnable ; "
     "face à une PME ou à une organisation à but non lucratif de "
     "recherche, elle ne dépasse pas les coûts directement liés"),
    ("det_litiges", "detenteur", "III", "art. 10",
     "Un organe de règlement des litiges certifié est accessible, et ses "
     "décisions sont traitées de bonne foi"),
    ("det_protection", "detenteur", "III", "art. 11",
     "Les mesures techniques de protection sont proportionnées et "
     "n'entravent pas l'exercice des droits ; un usage non autorisé "
     "déclenche les recours de l'article 11"),
    ("det_clauses", "detenteur", "IV", "art. 13",
     "Aucune clause abusive au sens de l'article 13 n'est imposée "
     "unilatéralement à une autre entreprise"),
    #  ── DESTINATAIRE — CHAPITRE II ───────────────────────────────────────
    ("dst_finalite", "destinataire", "II", "art. 6 §1",
     "Les données ne sont traitées qu'aux fins et dans les conditions "
     "convenues avec l'utilisateur, et effacées quand elles ne sont plus "
     "nécessaires"),
    ("dst_interdits", "destinataire", "II", "art. 6 §2",
     "Aucune des pratiques interdites par le §2 : interface non neutre, "
     "profilage non convenu, transmission à un autre tiers, usage pour "
     "développer un produit concurrent, détournement contre la position "
     "commerciale de l'utilisateur"),
    #  ── UTILISATEUR — CHAPITRE II ────────────────────────────────────────
    ("uti_concurrence", "utilisateur", "II", "art. 4 §10",
     "Les données obtenues ne servent pas à développer un produit "
     "concurrent de celui dont elles proviennent, ni à obtenir des "
     "informations sur la situation économique du fabricant"),
    ("uti_loyaute", "utilisateur", "II", "art. 4 §11",
     "Aucun recours à des moyens coercitifs ni exploitation de lacunes de "
     "l'infrastructure technique du détenteur pour obtenir l'accès"),
    #  ── SECTEUR PUBLIC — CHAPITRE V ──────────────────────────────────────
    ("pub_besoin", "secteur_public", "V", "art. 15",
     "Le besoin exceptionnel est caractérisé selon l'article 15, et la "
     "demande n'est pas un substitut à une obligation de partage existante "
     "(art. 16)"),
    ("pub_demande", "secteur_public", "V", "art. 17",
     "La demande est motivée, proportionnée, précise sur les données, la "
     "finalité et la durée, et publiée en ligne sans retard"),
    ("pub_usage", "secteur_public", "V", "art. 19",
     "Les données ne servent que la finalité déclarée, sont détruites dès "
     "qu'elles ne sont plus nécessaires, et leur sécurité est assurée"),
    ("pub_compensation", "secteur_public", "V", "art. 20",
     "La compensation due au détenteur est versée selon l'article 20, et "
     "la gratuité n'est invoquée que dans les cas qu'il prévoit"),
    #  ── FOURNISSEUR DE CLOUD — CHAPITRES VI ET VII ───────────────────────
    ("cld_obstacles", "cloud", "VI", "art. 23",
     "Aucun obstacle précommercial, commercial, technique, contractuel ou "
     "organisationnel n'empêche le client de changer de fournisseur, "
     "d'atteindre l'équivalence fonctionnelle, ou de résilier"),
    ("cld_clauses", "cloud", "VI", "art. 25",
     "Le contrat porte les clauses de changement de fournisseur : délai de "
     "transition maximal de trente jours, préavis de résiliation de deux "
     "mois au plus, assistance, et énumération des données et actifs "
     "numériques portables"),
    ("cld_information", "cloud", "VI", "art. 26",
     "Le client reçoit l'information sur les procédures de changement, les "
     "formats, les outils d'exportation et les restrictions connues"),
    ("cld_bonne_foi", "cloud", "VI", "art. 27",
     "Toutes les parties coopèrent de bonne foi pour rendre le changement "
     "effectif, dans les délais et en préservant la continuité"),
    ("cld_transparence_intl", "cloud", "VI", "art. 28",
     "Le contrat est transparent sur la juridiction où les données sont "
     "hébergées et sur les mesures techniques, organisationnelles et "
     "juridiques prises contre un accès international non conforme"),
    ("cld_frais", "cloud", "VI", "art. 29",
     "Les frais de changement de fournisseur sont supprimés au "
     "12 janvier 2027 ; d'ici là ils sont réduits et plafonnés aux coûts "
     "directement liés, et l'information précontractuelle du §4 est "
     "fournie"),
    ("cld_technique", "cloud", "VI", "art. 30",
     "Les obligations techniques du changement sont tenues selon la "
     "catégorie de service, l'équivalence fonctionnelle comprise là où "
     "l'article l'exige"),
    ("cld_acces_intl", "cloud", "VII", "art. 32",
     "Aucun transfert ni accès gouvernemental de pays tiers à des données "
     "non personnelles détenues dans l'Union n'est accordé hors des "
     "conditions de l'article 32 ; le client est informé"),
    #  ── ESPACE DE DONNÉES ET CONTRATS INTELLIGENTS — CHAPITRE VIII ───────
    ("esp_interop", "espace_donnees", "VIII", "art. 33",
     "Les exigences essentielles d'interopérabilité sont tenues : "
     "description du jeu de données, structures, formats, vocabulaires, "
     "moyens techniques d'accès"),
    ("esp_contrats", "espace_donnees", "VIII", "art. 36",
     "Les contrats intelligents respectent les exigences essentielles : "
     "robustesse, interruption sûre, archivage, contrôle d'accès, et "
     "cohérence avec l'accord de partage"),
)

OBLIGATIONS = tuple(
    {"cle": c, "qualite": q, "chapitre": ch, "article": a, "quoi": quoi}
    for c, q, ch, a, quoi in OBLIGATIONS_BRUTES)
OBLIGATIONS_PAR_CLE = {o["cle"]: o for o in OBLIGATIONS}

OBLIGATIONS_PAR_QUALITE = {}
for _o in OBLIGATIONS:
    OBLIGATIONS_PAR_QUALITE.setdefault(_o["qualite"], []).append(_o["cle"])
OBLIGATIONS_PAR_QUALITE = {k: tuple(v)
                           for k, v in OBLIGATIONS_PAR_QUALITE.items()}


#  ══════════════════════════════════════════════════════════════════════════
#  LE PONT AVEC LE RGPD — QUATRE DISPOSITIONS, TOUTES DANS LE TEXTE
#  ══════════════════════════════════════════════════════════════════════════

PONT_RGPD = (
    {"cle": "complete", "article": "art. 1er §5, 2e phrase",
     "dit": ("Dans la mesure où les utilisateurs sont les personnes "
             "concernées, les droits du chapitre II COMPLÈTENT les droits "
             "d'accès et de portabilité des articles 15 et 20 du RGPD."),
     "consequence": ("Deux droits, deux régimes. Répondre au titre du Data "
                     "Act ne purge pas une demande d'accès RGPD, et "
                     "l'inverse est vrai aussi."),
     "ou": "rgpd-traitements"},
    {"cle": "prevaut", "article": "art. 1er §5, 3e phrase",
     "dit": ("En cas de conflit entre le règlement et le droit de la "
             "protection des données à caractère personnel ou de la vie "
             "privée, ce dernier PRÉVAUT."),
     "consequence": ("Un jeu de données mixte — personnel et non "
                     "personnel inextricablement liés — reste arbitré par "
                     "le RGPD."),
     "ou": "rgpd-hub"},
    {"cle": "base_legale", "article": "art. 4 §12",
     "dit": ("Quand l'utilisateur n'est pas la personne concernée, les "
             "données personnelles ne lui sont mises à disposition que "
             "s'il existe un fondement juridique valable au titre de "
             "l'article 6 du RGPD, et le cas échéant si les conditions de "
             "l'article 9 du RGPD et de l'article 5 §3 de la directive "
             "2002/58/CE sont remplies."),
     "consequence": ("Le droit d'accès du Data Act NE FABRIQUE PAS de base "
                     "légale. Sans article 6, la demande se refuse."),
     "ou": "rgpd-traitements"},
    {"cle": "sanction", "article": "art. 40 §4",
     "dit": ("Pour les manquements aux chapitres II, III et V, les "
             "autorités de contrôle du RGPD peuvent infliger des amendes "
             "administratives au titre de l'article 83 du RGPD, jusqu'à "
             "concurrence du montant de son paragraphe 5."),
     "consequence": ("C'est la CNIL qui sanctionne, avec le plafond le "
                     "plus élevé du RGPD — et l'article 83 §5 ne prévoit "
                     "AUCUNE réduction pour les PME."),
     "ou": "rgpd-conformite"},
)


#  ══════════════════════════════════════════════════════════════════════════
#  L'ARTICLE 40 — L'EXPOSITION, ET SON ARITHMÉTIQUE
#  ══════════════════════════════════════════════════════════════════════════
#
# LES DEUX NOMBRES VIENNENT DE L'ARTICLE 83 §5 DU RGPD, relevé à sa source :
# 20 000 000 EUR ou 4 % du chiffre d'affaires annuel mondial total de
# l'exercice précédent, LE PLUS ÉLEVÉ étant retenu. Ils ne sont pas dans le
# Data Act : il les emprunte.

RGPD_ART83_5_FIXE = 20_000_000
RGPD_ART83_5_PART = 0.04
RGPD_ART83_5_PLUS_ELEVE = True
RGPD_ART83_5_REDUCTION_PME = False

SANCTIONS = {
    "article": "art. 40",
    "emprunt": "RGPD, art. 83 §5",
    "chapitres_exposes": tuple(c["cle"] for c in CHAPITRES
                               if c["rgpd_art83"]),
    "autorite": ("Les autorités de contrôle chargées de surveiller "
                 "l'application du RGPD — en France, la CNIL — dans les "
                 "limites de leur compétence (art. 40 §4)."),
    "edps": ("Pour les manquements au chapitre V, le Contrôleur européen "
             "de la protection des données peut sanctionner les "
             "institutions de l'Union sur le fondement de l'article 66 du "
             "règlement (UE) 2018/1725 (art. 40 §5). Cette voie ne vise "
             "pas les entreprises."),
    "national": ("Pour les chapitres IV, VI et VIII, le régime est celui "
                 "que l'État membre détermine (art. 40 §1) : aucun plafond "
                 "européen ne s'y applique."),
    "criteres": (
        ("a", "Nature, gravité, ampleur et durée de l'infraction"),
        ("b", "Mesures prises pour atténuer ou réparer le préjudice"),
        ("c", "Infractions antérieures"),
        ("d", "Avantages financiers obtenus ou pertes évitées, s'ils sont "
              "établis de manière fiable"),
        ("e", "Toute autre circonstance aggravante ou atténuante"),
        ("f", "Le chiffre d'affaires annuel réalisé dans l'Union au cours "
              "de l'exercice précédent"),
    ),
}


def exposition(chiffre_affaires=None, chapitre=None):
    """Le plafond encouru, et POURQUOI il vaut ce qu'il vaut.

    L'ARITHMÉTIQUE EST CELLE DE L'ARTICLE 83 §5 DU RGPD, PAS CELLE DE
    L'ARTICLE 99 DE L'IA ACT. La différence est le piège : l'article 99 §6
    retient le plafond le PLUS BAS pour une PME, l'article 83 §5 retient
    toujours le PLUS ÉLEVÉ. Une PME est donc plus exposée ici que sous
    l'IA Act, et c'est l'inverse de ce qu'on attend.

    `None` n'est pas zéro : un chapitre hors de la liste de l'article 40 §4
    n'a pas de plafond européen, et rendre 0 ferait croire à l'impunité.
    """
    if chapitre is not None:
        ch = CHAPITRES_PAR_CLE.get(chapitre)
        if ch is None:
            return {"plafond": None, "motif": "chapitre_inconnu",
                    "chapitre": chapitre}
        if not ch["rgpd_art83"]:
            return {"plafond": None, "motif": "regime_national",
                    "chapitre": chapitre,
                    "dit": SANCTIONS["national"]}
    if chiffre_affaires is None:
        return {"plafond": RGPD_ART83_5_FIXE, "part": None,
                "motif": "ca_inconnu", "chapitre": chapitre,
                "dit": ("Sans chiffre d'affaires, seul le montant fixe de "
                        "l'article 83 §5 est connu. Le plafond réel est le "
                        "PLUS ÉLEVÉ des deux, donc au moins celui-ci.")}
    try:
        ca = float(chiffre_affaires)
    except (TypeError, ValueError):
        return {"plafond": None, "motif": "ca_invalide",
                "chapitre": chapitre}
    if ca < 0:
        return {"plafond": None, "motif": "ca_negatif", "chapitre": chapitre}
    sur_ca = round(ca * RGPD_ART83_5_PART)
    plafond = max(RGPD_ART83_5_FIXE, sur_ca)
    return {
        "plafond": plafond,
        "fixe": RGPD_ART83_5_FIXE,
        "part": RGPD_ART83_5_PART,
        "sur_ca": sur_ca,
        "retenu": ("part_du_ca" if sur_ca > RGPD_ART83_5_FIXE else "fixe"),
        "motif": "art83_5",
        "chapitre": chapitre,
        "reduction_pme": RGPD_ART83_5_REDUCTION_PME,
        "dit": ("Article 40 §4 du Data Act, par renvoi à l'article 83 §5 du "
                "RGPD : le plus élevé de %s EUR et de 4 %% du chiffre "
                "d'affaires annuel mondial total, soit %s EUR. L'article 83 "
                "§5 ne prévoit aucune réduction pour les PME."
                % ("{:,}".format(RGPD_ART83_5_FIXE).replace(",", " "),
                   "{:,}".format(plafond).replace(",", " "))),
    }


#  ══════════════════════════════════════════════════════════════════════════
#  LES RÉSERVES
#  ══════════════════════════════════════════════════════════════════════════

RESERVES = (
    {"cle": "plafond_pas_amende",
     "dit": ("Les montants de l'article 83 §5 sont des PLAFONDS. L'amende "
             "se fixe en dessous, au regard des critères de l'article 40 "
             "§3 et de l'article 83 §2 du RGPD.")},
    {"cle": "pas_de_base_legale",
     "dit": ("Le règlement ne crée aucune base juridique de traitement. "
             "L'article 4 §12 exige l'article 6 du RGPD, et ce module ne "
             "le remplace pas.")},
    {"cle": "pme_pas_hors_champ",
     "dit": ("L'exemption de l'article 7 ne couvre que le chapitre II, et "
             "sous conditions. Une PME reste tenue par les chapitres IV, "
             "VI et VII.")},
    {"cle": "pas_de_certification",
     "dit": ("Le Data Act ne prévoit ni certification ni marquage. Un taux "
             "élevé ici ne vaut aucune présomption de conformité.")},
)

NOM_DU_TAUX = "Couverture des obligations de la qualité déclarée"

ETATS = {"tenu": 1.0, "partiel": 0.5, "non_tenu": 0.0, "sans_objet": None}


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
#  LA QUALIFICATION, LE TAUX, LES ÉCHÉANCES
#  ══════════════════════════════════════════════════════════════════════════

def qualites_declarees(declaration=None):
    d = declaration if isinstance(declaration, dict) else {}
    brut = d.get("qualites")
    if isinstance(brut, str):
        brut = [brut]
    if not isinstance(brut, (list, tuple)):
        return ()
    return tuple(q for q in brut if q in QUALITES_PAR_CLE)


def exempte_art7(declaration=None):
    """L'exemption du chapitre II — et les deux conditions qui la retiennent.

    Elle ne se déduit PAS de la taille seule : l'article 7 §1 la refuse à
    qui a une entreprise partenaire ou liée plus grande, et à qui travaille
    en sous-traitance. Déclarer « petite entreprise » ne suffit donc pas, et
    le module ne l'accorde pas sans les deux réponses.
    """
    d = declaration if isinstance(declaration, dict) else {}
    taille = d.get("taille")
    if taille not in ("micro", "petite"):
        return {"ok": False, "motif": "taille",
                "dit": ("L'exemption de l'article 7 ne vise que les micro "
                        "et petites entreprises.")}
    if d.get("sans_partenaire_plus_grand") is not True:
        return {"ok": False, "motif": "partenaire",
                "dit": ("L'article 7 §1 refuse l'exemption si une "
                        "entreprise partenaire ou liée n'est pas elle aussi "
                        "micro ou petite.")}
    if d.get("hors_sous_traitance") is not True:
        return {"ok": False, "motif": "sous_traitance",
                "dit": ("L'article 7 §1 refuse l'exemption à qui travaille "
                        "en sous-traitance pour fabriquer ou concevoir un "
                        "produit connecté, ou fournir un service "
                        "connexe.")}
    return {"ok": True, "motif": "art7",
            "dit": ("Le chapitre II ne s'applique pas. Les chapitres IV, VI "
                    "et VII, eux, ne connaissent pas cette exemption.")}


def applicable(declaration=None):
    qs = qualites_declarees(declaration)
    if not qs:
        return {"ok": None, "qualites": (), "chapitres": (), "exemption": None,
                "dit": ("Aucune qualité n'est déclarée. L'article 1er §3 en "
                        "énumère sept : sans savoir laquelle est la vôtre, "
                        "il n'y a rien à mesurer.")}
    if "aucune" in qs and len(qs) == 1:
        return {"ok": False, "qualites": qs, "chapitres": (),
                "exemption": None,
                "dit": ("HORS CHAMP. Aucune des sept qualités de "
                        "l'article 1er §3 n'est la vôtre. Attention "
                        "toutefois : l'extraterritorialité du règlement "
                        "saisit un fabricant ou un fournisseur de cloud où "
                        "qu'il soit établi, dès qu'il touche le marché de "
                        "l'Union.")}
    utiles = tuple(q for q in qs if q != "aucune")
    exemption = exempte_art7(declaration) if any(
        "II" in QUALITES_PAR_CLE[q]["chapitres"] for q in utiles) else None
    chapitres = []
    for q in utiles:
        for ch in QUALITES_PAR_CLE[q]["chapitres"]:
            if ch not in chapitres:
                chapitres.append(ch)
    if exemption and exemption["ok"] and "II" in chapitres:
        chapitres.remove("II")
    return {"ok": True, "qualites": utiles, "chapitres": tuple(chapitres),
            "exemption": exemption,
            "dit": ("Vous relevez de %d chapitre(s) du règlement. Les "
                    "obligations affichées sont celles de vos qualités, et "
                    "d'elles seules." % len(chapitres))}


def score(declaration=None):
    d = declaration if isinstance(declaration, dict) else {}
    rep = d.get("reponses") if isinstance(d.get("reponses"), dict) else {}
    champ = applicable(d)
    retenus_ch = set(champ["chapitres"])
    parts, renseignes, attendus = {}, 0, 0
    for q in champ["qualites"]:
        cles = tuple(c for c in OBLIGATIONS_PAR_QUALITE.get(q, ())
                     if OBLIGATIONS_PAR_CLE[c]["chapitre"] in retenus_ch)
        if not cles:
            continue
        taux, n, total = _part(cles, rep)
        parts[q] = taux
        renseignes += n
        attendus += total
    gardes = [v for v in parts.values() if v is not None]
    return {"parts": parts,
            "total": (round(sum(gardes) / len(gardes)) if gardes else None),
            "renseignes": renseignes, "attendus": attendus}


def echeances(declaration=None, aujourdhui=None):
    """Les échéances de l'article 50 et de l'article 29, situées dans le temps.

    `echue` se mesure, elle ne se suppose pas : au 5 octobre 2026, celle de
    l'article 3 §1 est passée de vingt-trois jours, et celle des frais de
    changement de fournisseur tombe dans quatre-vingt-dix-neuf. Les deux
    sont actionnables, et pas du tout de la même façon.
    """
    jour = aujourdhui or datetime.date.today().isoformat()
    qs = set(qualites_declarees(declaration))
    sortie = []
    for e in ECHEANCES:
        vise = (e["qui"] == "tous" or e["qui"] in qs or not qs)
        reste = (datetime.date.fromisoformat(e["date"])
                 - datetime.date.fromisoformat(jour)).days
        sortie.append({"cle": e["cle"], "date": e["date"],
                       "article": e["article"], "quoi": e["quoi"],
                       "qui": e["qui"], "vous_vise": vise,
                       "echue": e["date"] <= jour, "jours": reste})
    return sortie


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
    ech = echeances(d, aujourdhui)
    # LE CHAPITRE PASSÉ AU CALCUL D'EXPOSITION, ET POURQUOI CE N'EST PLUS
    # `None` QUAND AUCUN CHAPITRE OUVERT N'EST EXPOSÉ.
    #
    # CE QUI A ÉTÉ MESURÉ : un fournisseur de services de traitement de
    # données n'ouvre que les chapitres VI et VII, dont aucun n'est désigné
    # par l'article 40 §4. Cette ligne cherchait le premier chapitre exposé
    # et rendait `None` quand elle n'en trouvait aucun — or `exposition()`
    # lit `None` comme « on ne sait pas lequel », pas comme « aucun », et
    # retombait sur l'arithmétique de l'article 83 §5. La route annonçait
    # donc 20 000 000 EUR de plafond européen à qui n'en encourt aucun :
    # exactement le contresens contre lequel l'écran du module met en garde
    # (« Croire que ce chapitre expose au plafond du RGPD »).
    #
    # ON NOMME DONC UN CHAPITRE OUVERT, exposé si l'un l'est, le premier
    # ouvert sinon : le calcul rend alors « regime_national » et renvoie à
    # ce que dit la sanction nationale. `None` ne reste réservé qu'au cas où
    # AUCUN chapitre n'est ouvert — hors champ, non qualifié, exempté —, où
    # il n'y a pas de chapitre à nommer.
    exposes = [c for c in champ["chapitres"]
               if CHAPITRES_PAR_CLE[c]["rgpd_art83"]]
    expo = exposition(d.get("chiffre_affaires"),
                      chapitre=(exposes or champ["chapitres"] or [None])[0])
    echues = [e for e in ech if e["echue"] and e["vous_vise"]
              and e["cle"] != "application"]

    if champ["ok"] is None:
        tete, dit = "non_qualifie", champ["dit"]
    elif champ["ok"] is False:
        tete, dit = "hors_champ", champ["dit"]
    elif not champ["chapitres"]:
        tete, dit = "exempte", (
            (champ["exemption"] or {}).get("dit")
            or "Aucun chapitre ne vous saisit au vu de vos déclarations.")
    elif not sc["renseignes"]:
        tete, dit = "vide", (
            "La qualification est faite, rien n'est renseigné. Le module ne "
            "rend aucun chiffre par défaut : un questionnaire vide n'est pas "
            "une conformité à zéro, c'est une conformité qu'on n'a pas "
            "regardée.")
    elif echues:
        tete, dit = "echeance_passee", (
            "%d échéance(s) qui vous visent sont passées, dont %s (%s). Ce "
            "n'est plus un calendrier : c'est un état exigible."
            % (len(echues), echues[0]["article"], echues[0]["date"]))
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
        "chapitres": list(champ["chapitres"]),
        "exemption_art7": champ["exemption"],
        "parts": dict(sc["parts"]),
        "score": sc,
        "echeances": ech,
        "exposition": expo,
        "applicable_depuis": APPLICABLE_DEPUIS,
        "obligations": len(OBLIGATIONS),
        "renseignes": sc["renseignes"],
        "pont_rgpd": [dict(p) for p in PONT_RGPD],
        "reserves": [dict(r) for r in RESERVES],
        "tete": tete, "dit": dit,
        "presomption": False,
        "nom_du_taux": NOM_DU_TAUX,
    }


def referentiel():
    return {
        "source": dict(SOURCE),
        "entree_en_vigueur": ENTREE_EN_VIGUEUR,
        "applicable_depuis": APPLICABLE_DEPUIS,
        "echeances": [dict(e) for e in ECHEANCES],
        "chapitres": [dict(c) for c in CHAPITRES],
        "qualites": [dict(q) for q in QUALITES],
        "exemption_art7": {
            "article": EXEMPTION_ART7["article"],
            "chapitre": EXEMPTION_ART7["chapitre"],
            "qui": EXEMPTION_ART7["qui"],
            "conditions": [{"cle": c, "quoi": q}
                           for c, q in EXEMPTION_ART7["conditions"]],
            "moyenne": EXEMPTION_ART7["moyenne"],
            "ce_qu_elle_ne_couvre_pas":
                EXEMPTION_ART7["ce_qu_elle_ne_couvre_pas"],
            "non_contournable": EXEMPTION_ART7["non_contournable"],
        },
        "clauses_art13": [{"cle": c, "nature": n, "article": a, "quoi": q}
                          for c, n, a, q in CLAUSES_ART13],
        "obligations": [dict(o) for o in OBLIGATIONS],
        "pont_rgpd": [dict(p) for p in PONT_RGPD],
        "sanctions": {
            "article": SANCTIONS["article"],
            "emprunt": SANCTIONS["emprunt"],
            "chapitres_exposes": list(SANCTIONS["chapitres_exposes"]),
            "autorite": SANCTIONS["autorite"],
            "edps": SANCTIONS["edps"],
            "national": SANCTIONS["national"],
            "fixe": RGPD_ART83_5_FIXE,
            "part": RGPD_ART83_5_PART,
            "plus_eleve": RGPD_ART83_5_PLUS_ELEVE,
            "reduction_pme": RGPD_ART83_5_REDUCTION_PME,
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

    LE PREMIER RANG EST LA QUALIFICATION, le deuxième LES ÉCHÉANCES DÉJÀ
    PASSÉES. Une obligation dont la date est échue ne se planifie pas, elle
    se répare : au 5 octobre 2026, l'article 3 §1 est exigible depuis
    vingt-trois jours pour tout produit mis sur le marché depuis le
    12 septembre 2026.
    """
    d = declaration if isinstance(declaration, dict) else {}
    rep = d.get("reponses") if isinstance(d.get("reponses"), dict) else {}
    champ = applicable(d)
    actions = []
    if champ["ok"] is None:
        actions.append({"cle": "qualifier", "quoi": (
            "Déclarer vos qualités au titre de l'article 1er §3 — fabricant, "
            "utilisateur, détenteur, destinataire, organisme du secteur "
            "public, fournisseur de services de traitement de données, "
            "participant à un espace de données. Elles s'appliquent QUEL QUE "
            "SOIT votre lieu d'établissement."),
            "ou": "data-act · qualification"})
        return {"actions": actions[:limite]}
    if champ["ok"] is False or not champ["chapitres"]:
        return {"actions": []}
    for e in echeances(d):
        if e["echue"] and e["vous_vise"] and e["cle"] != "application":
            actions.append({"cle": "echeance_%s" % e["cle"], "quoi": (
                "Échéance passée le %s (%s) : %s" % (e["date"], e["article"],
                                                     e["quoi"])),
                "ou": "data-act · obligations"})
    for q in champ["qualites"]:
        for c in OBLIGATIONS_PAR_QUALITE.get(q, ()):
            if OBLIGATIONS_PAR_CLE[c]["chapitre"] not in champ["chapitres"]:
                continue
            etat = rep.get(c)
            if etat in ("tenu", "sans_objet"):
                continue
            o = OBLIGATIONS_PAR_CLE[c]
            verbe = ("Compléter" if etat == "partiel"
                     else "Tenir" if etat == "non_tenu" else "Renseigner")
            actions.append({"cle": c,
                            "quoi": "%s — %s : %s" % (verbe, o["article"],
                                                      o["quoi"]),
                            "ou": "data-act · obligations"})
    return {"actions": actions[:limite]}

#  ══════════════════════════════════════════════════════════════════════════
#  LE GARDIEN
#  ══════════════════════════════════════════════════════════════════════════

def _verifier():
    if len(QUALITES) - 1 != 7:
        raise RuntimeError(
            "data_act : l'article 1er §3 enumere sept qualites, a) a g), "
            "plus « aucune » ; la table en declare %d." % (len(QUALITES) - 1))
    lettres = [q["lettre"] for q in QUALITES if q["lettre"]]
    if lettres != list('abcdefg'):
        raise RuntimeError(
            "data_act : les lettres de l'article 1er §3 doivent aller de a a "
            "g, dans l'ordre ; la table dit %r." % (lettres,))
    if len(CHAPITRES) != 6:
        raise RuntimeError(
            "data_act : l'article 1er §2 situe six chapitres, II a VII ; la "
            "table en declare %d." % len(CHAPITRES))
    exposes = tuple(c["cle"] for c in CHAPITRES if c["rgpd_art83"])
    if exposes != ("II", "III", "V"):
        raise RuntimeError(
            "data_act : l'article 40 §4 ne designe QUE les chapitres II, III "
            "et V ; la table expose %r. Elargir cette liste inventerait une "
            "exposition, la reduire en cacherait une." % (exposes,))
    #  L'ARITHMETIQUE EMPRUNTEE — les deux nombres de l'article 83 §5 du RGPD.
    if RGPD_ART83_5_FIXE != 20_000_000:
        raise RuntimeError(
            "data_act : l'article 83 §5 du RGPD dit 20 000 000 EUR ; la "
            "table dit %r." % (RGPD_ART83_5_FIXE,))
    if RGPD_ART83_5_PART != 0.04:
        raise RuntimeError(
            "data_act : l'article 83 §5 du RGPD dit 4 %% du chiffre "
            "d'affaires annuel mondial total ; la table dit %r."
            % (RGPD_ART83_5_PART,))
    if RGPD_ART83_5_PLUS_ELEVE is not True:
        raise RuntimeError(
            "data_act : l'article 83 §5 retient le montant le PLUS ELEVE. "
            "Retenir le plus bas est l'erreur que le calculateur de "
            "l'article 99 avait faite, et elle divisait le plafond par dix.")
    if RGPD_ART83_5_REDUCTION_PME is not False:
        raise RuntimeError(
            "data_act : l'article 83 §5 du RGPD ne prevoit AUCUNE reduction "
            "pour les PME, contrairement a l'article 99 §6 de l'IA Act.")
    #  L'ordre des echeances, et le fait qu'aucune ne precede l'application.
    for e in ECHEANCES:
        if e["date"] < APPLICABLE_DEPUIS:
            raise RuntimeError(
                "data_act : l'echeance %r (%s) precede l'entree en "
                "application (%s)." % (e["cle"], e["date"],
                                       APPLICABLE_DEPUIS))
        if e["qui"] != "tous" and e["qui"] not in QUALITES_PAR_CLE:
            raise RuntimeError(
                "data_act : l'echeance %r vise la qualite inconnue %r."
                % (e["cle"], e["qui"]))
    if len(CLAUSES_ART13) != 10:
        raise RuntimeError(
            "data_act : l'article 13 porte trois clauses abusives (§4 a-c) "
            "et sept presumees abusives (§5 a-g), soit dix ; la table en "
            "declare %d." % len(CLAUSES_ART13))
    dures = sum(1 for _, n, _, _ in CLAUSES_ART13 if n == "abusive")
    if dures != 3:
        raise RuntimeError(
            "data_act : le §4 enumere TROIS clauses qui SONT abusives ; la "
            "table en marque %d. Confondre le §4 et le §5 ferait "
            "renegocier des clauses seulement presumees." % dures)
    if len(PONT_RGPD) != 4:
        raise RuntimeError(
            "data_act : le pont avec le RGPD repose sur quatre dispositions "
            "du texte ; la table en declare %d." % len(PONT_RGPD))
    for p in PONT_RGPD:
        if not p.get("article") or not p.get("dit") or not p.get("ou"):
            raise RuntimeError(
                "data_act : chaque point du pont RGPD porte son article, ce "
                "qu'il dit et ou il mene ; %r en manque." % (p.get("cle"),))
    #  Chaque qualite assujettie porte des obligations, et chaque obligation
    #  tombe dans un chapitre que sa qualite connait.
    for q in QUALITES:
        if q["cle"] == "aucune":
            continue
        cles = OBLIGATIONS_PAR_QUALITE.get(q["cle"])
        if not cles:
            raise RuntimeError(
                "data_act : la qualite %r ne porte aucune obligation ; un "
                "ecran de qualification qui mene au vide est pire qu'une "
                "qualite absente." % q["cle"])
        for c in cles:
            ch = OBLIGATIONS_PAR_CLE[c]["chapitre"]
            if ch not in q["chapitres"]:
                raise RuntimeError(
                    "data_act : l'obligation %r releve du chapitre %s, que "
                    "la qualite %r ne declare pas." % (c, ch, q["cle"]))


_verifier()
