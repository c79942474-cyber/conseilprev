# -*- coding: utf-8 -*-
"""NIS 2 — directive (UE) 2022/2555, rendue calculable.

═══════════════════════════════════════════════════════════════════════════
 LA DÉCISION QUI COMMANDE TOUTES LES AUTRES
═══════════════════════════════════════════════════════════════════════════

    SUIS-JE UNE ENTITÉ ESSENTIELLE, OU UNE ENTITÉ IMPORTANTE ?

La question a l'air d'un classement d'honneur ; c'est un régime de contrôle.

    · ESSENTIELLE  → supervision EX ANTE (art. 32) : inspections sur place,
      contrôles aléatoires, audits de sécurité RÉGULIERS, scans. L'autorité
      n'a besoin d'aucun incident, d'aucun soupçon, pour venir.
    · IMPORTANTE   → supervision EX POST (art. 33) : l'autorité agit « au vu
      d'éléments de preuve, d'indications ou d'informations » de manquement.

Et l'écart ne s'arrête pas là. L'article 32, §5, réservé aux SEULES entités
essentielles, permet de suspendre une certification ou une autorisation, et
d'INTERDIRE TEMPORAIREMENT au directeur général ou au représentant légal
d'exercer ses fonctions dirigeantes. Aucun équivalent à l'article 33.

═══════════════════════════════════════════════════════════════════════════
 CE QUI FAIT BASCULER — ET QUI N'EST PAS LE NIVEAU DE SÉCURITÉ
═══════════════════════════════════════════════════════════════════════════

La bascule ne récompense ni ne punit une posture de sécurité : elle se
calcule sur DEUX FAITS, le secteur (annexe I ou II) et la taille (seuils de
la recommandation 2003/361/CE). Une entreprise de l'annexe I qui recrute et
passe de 240 à 260 personnes devient essentielle sans avoir rien changé à
son risque — et hérite au passage des audits réguliers, et d'un palier de
sanction supérieur de 43 % (10 M€ contre 7 M€).

C'est un effet de seuil, il se franchit par la croissance, et personne ne
l'annonce : à la différence d'une certification, LA QUALIFICATION NE SE
DEMANDE PAS. L'État dresse la liste (art. 3, §3) et l'entité doit s'y
déclarer elle-même (art. 3, §4) — au plus tard le 17 avril 2025. Cette date
est passée. Une entité non enregistrée n'est pas « pas encore concernée » :
elle est en manquement sur une obligation dont l'échéance est derrière elle.

═══════════════════════════════════════════════════════════════════════════
 CE QUE CE MODULE NE FAIT PAS
═══════════════════════════════════════════════════════════════════════════

IL NE REND PAS D'AVIS JURIDIQUE. La qualification réelle est prononcée par
l'autorité nationale compétente, sur l'entité réelle ; le module CONSTATE ce
qui est déclaré, nomme l'article qui s'applique, et dit ce qui reste à faire
trancher.

IL NE CONFOND PAS UNE DIRECTIVE AVEC UN RÈGLEMENT, et c'est la réserve la
plus importante de tout le module. NIS 2 n'est pas d'application directe :
ce qui oblige une entreprise, c'est LA LOI DE TRANSPOSITION de chaque État
membre où elle fournit ses services. Les montants de l'article 34 sont
introduits par « au moins » — ce sont des PLANCHERS imposés aux États, pas
des plafonds offerts aux entreprises. Un État peut aller au-delà, et le
module ne prétendra jamais chiffrer une amende maximale : il chiffre le
PLANCHER EUROPÉEN, en disant que c'est un plancher.

    Le CRA, lui, est un règlement : ses montants sont les montants.
    Les deux modules de Sentinel disent cette différence, chacun pour sa
    source, parce que confondre les deux régimes fausse toute estimation.

IL NE RECOPIE PAS LA DIRECTIVE. Les libellés d'annexes et de mesures sont
des désignations — des faits, repris pour pouvoir s'y ranger —, et le texte
du Journal officiel est réutilisable au titre de la décision 2011/833/UE
moyennant attribution. Tout ce qui est rédigé ici est du cabinet.

═══════════════════════════════════════════════════════════════════════════
 CE QUE CE MODULE N'EST PAS
═══════════════════════════════════════════════════════════════════════════

NIS 2 compte des ENTITÉS, qualifiées par leur secteur et leur taille.
Ni des systèmes d'IA (IA Act), ni des traitements (RGPD), ni des produits
(CRA). Une même entreprise peut relever des quatre : quatre unités de
compte, quatre registres, quatre jeux d'obligations qui ne se recouvrent pas.
"""

import datetime


# ═══════════════════════════════════════════════════════════════════════════
#  LA SOURCE
# ═══════════════════════════════════════════════════════════════════════════

SOURCE = {
    "titre": "Directive (UE) 2022/2555 du Parlement européen et du Conseil "
             "du 14 décembre 2022 concernant des mesures destinées à assurer "
             "un niveau élevé commun de cybersécurité dans l'ensemble de "
             "l'Union, modifiant le règlement (UE) n° 910/2014 et la "
             "directive (UE) 2018/1972, et abrogeant la directive (UE) "
             "2016/1148 (directive SRI 2)",
    "court": "NIS 2",
    "jo": "JO L 333 du 27.12.2022, p. 80",
    "eli": "http://data.europa.eu/eli/dir/2022/2555/oj",
    "licence": "Réutilisation autorisée — décision 2011/833/UE, avec "
               "attribution. Seul le texte publié au Journal officiel fait foi.",
    "lu_le": "2026-09-18",
    # LA RÉSERVE QUI CHANGE LA LECTURE DE TOUT LE RESTE.
    "nature": "directive",
    "reserve": "Une directive n'est pas d'application directe : ce qui oblige "
               "une entité, c'est la loi de transposition de chaque État "
               "membre où elle fournit ses services. Les montants et délais "
               "repris ici sont ceux de la directive — des MINIMA imposés aux "
               "États. Une transposition nationale peut être plus exigeante, "
               "jamais moins.",
}


# ═══════════════════════════════════════════════════════════════════════════
#  ET POUR LA FRANCE, LA TRANSPOSITION A UNE AUTRE FORME
# ═══════════════════════════════════════════════════════════════════════════
#
# LA RÉSERVE CI-DESSUS ÉTAIT EXACTE ET S'ARRÊTAIT TROP TÔT. Elle disait que
# c'est la loi de transposition qui oblige — sans dire ce que celle-ci
# prépare. Un client français mesurait donc dix mesures quand l'ANSSI le
# contrôlera sur vingt objectifs.
#
# CE RENVOI N'IMPORTE RIEN. `nis2_recyf` lit ce module ; un import en tête de
# fichier fermerait le cercle. Il nomme le calque, il ne l'appelle pas.

TRANSPOSITION_FR = {
    "existe": True,
    "module": "nis2_recyf",
    "panneau": "recyf-objectifs",
    "quoi": "Le projet de loi relatif à la résilience des infrastructures "
            "critiques et au renforcement de la cybersécurité remplace, à "
            "son article 14, les dix mesures de l'article 21 §2 par quatre "
            "familles, et renvoie au ReCyF — vingt objectifs de sécurité, "
            "152 moyens de conformité pour une entité essentielle, 76 pour "
            "une entité importante.",
    "ce_qui_change_le_plus": "La distinction essentielle / importante cesse "
                             "d'être une affaire de supervision et de "
                             "plafond d'amende : elle retire cinq objectifs "
                             "sur vingt à une entité importante.",
    "en_vigueur": False,
    "reserve": "Ni le projet de loi ni le référentiel ne sont en vigueur. Ce "
               "que le calque français rend est un taux de PRÉPARATION, qui "
               "ne se confond avec aucun taux de conformité.",
}


# ═══════════════════════════════════════════════════════════════════════════
#  LE CALENDRIER — ET CE QUI EST DÉJÀ DERRIÈRE NOUS
# ═══════════════════════════════════════════════════════════════════════════
#
# POURQUOI LA DATE EST INJECTÉE, ET JAMAIS LUE DE L'HORLOGE : une échéance
# calculée sur `datetime.date.today()` rend un test qui passe aujourd'hui et
# tombe demain. La date entre par la porte, et les règles la fixent.

ECHEANCES = (
    {"cle": "transposition",
     "date": "2024-10-17",
     "quoi": "Les États membres adoptent et publient leur loi de transposition",
     "article": "art. 41, §1"},
    {"cle": "application",
     "date": "2024-10-18",
     "quoi": "Les dispositions nationales de transposition s'appliquent",
     "article": "art. 41, §1"},
    {"cle": "enregistrement",
     "date": "2025-04-17",
     "quoi": "Les États établissent la liste des entités essentielles et "
             "importantes ; les entités concernées communiquent à l'autorité "
             "compétente leur nom, leurs coordonnées, leur secteur et les "
             "États membres où elles opèrent",
     "article": "art. 3, §§3 et 4"},
)


def calendrier(aujourdhui=None):
    """Ce qui est applicable, et depuis quand — la date entrant par la porte."""
    jour = aujourdhui or datetime.date.today()
    if isinstance(jour, str):
        jour = datetime.date(*(int(x) for x in jour.split("-")))
    lignes = []
    for e in ECHEANCES:
        d = datetime.date(*(int(x) for x in e["date"].split("-")))
        jours = (d - jour).days
        lignes.append(dict(e, applicable=(jours <= 0), jours=jours))
    return {
        "aujourdhui": jour.isoformat(),
        "echeances": lignes,
        "en_vigueur": [l for l in lignes if l["applicable"]],
        "a_venir": [l for l in lignes if not l["applicable"]],
    }


# ═══════════════════════════════════════════════════════════════════════════
#  LE SECTEUR — ANNEXES I ET II
# ═══════════════════════════════════════════════════════════════════════════
#
# CE QUE L'ANNEXE DÉCIDE : elle ne décide PAS à elle seule du statut. Elle
# décide de QUEL statut est ATTEIGNABLE. L'annexe I ouvre la porte au statut
# d'entité essentielle si la taille suit ; l'annexe II plafonne à
# « importante », quelle que soit la taille. Un géant de la gestion des
# déchets reste une entité importante ; un opérateur d'eau potable de 260
# personnes est une entité essentielle.

ANNEXE_I = (
    ("energie", "Énergie",
     ("Électricité", "Réseaux de chaleur et de froid", "Pétrole", "Gaz",
      "Hydrogène")),
    ("transports", "Transports",
     ("Transports aériens", "Transports ferroviaires", "Transports par eau",
      "Transports routiers")),
    ("banque", "Secteur bancaire", ()),
    ("marches_financiers", "Infrastructures des marchés financiers", ()),
    ("sante", "Santé", ()),
    ("eau_potable", "Eau potable", ()),
    ("eaux_usees", "Eaux usées", ()),
    ("infrastructure_numerique", "Infrastructure numérique",
     ("Points d'échange internet", "Fournisseurs de services DNS",
      "Registres de noms de domaine de premier niveau",
      "Fournisseurs de services d'informatique en nuage",
      "Fournisseurs de services de centres de données",
      "Réseaux de diffusion de contenu",
      "Prestataires de services de confiance",
      "Fournisseurs de réseaux de communications électroniques publics",
      "Fournisseurs de services de communications électroniques "
      "accessibles au public")),
    ("services_tic", "Gestion des services TIC (interentreprises)",
     ("Fournisseurs de services gérés",
      "Fournisseurs de services de sécurité gérés")),
    ("administration_publique", "Administration publique", ()),
    ("espace", "Espace", ()),
)

ANNEXE_II = (
    ("postal", "Services postaux et d'expédition", ()),
    ("dechets", "Gestion des déchets", ()),
    ("chimie", "Fabrication, production et distribution de produits chimiques",
     ()),
    ("alimentaire",
     "Production, transformation et distribution des denrées alimentaires",
     ()),
    ("fabrication", "Fabrication",
     ("Dispositifs médicaux et dispositifs médicaux de diagnostic in vitro",
      "Produits informatiques, électroniques et optiques",
      "Équipements électriques", "Machines et équipements",
      "Véhicules automobiles, remorques et semi-remorques",
      "Autres matériels de transport")),
    ("numerique", "Fournisseurs numériques",
     ("Places de marché en ligne", "Moteurs de recherche en ligne",
      "Plateformes de services de réseaux sociaux")),
    ("recherche", "Recherche", ()),
)

SECTEURS = {}
for _cle, _nom, _sous in ANNEXE_I:
    SECTEURS[_cle] = {"nom": _nom, "annexe": "I", "sous_secteurs": _sous,
                      "plafond": "essentielle"}
for _cle, _nom, _sous in ANNEXE_II:
    SECTEURS[_cle] = {"nom": _nom, "annexe": "II", "sous_secteurs": _sous,
                      "plafond": "importante"}


# ═══════════════════════════════════════════════════════════════════════════
#  LA TAILLE — RECOMMANDATION 2003/361/CE, ANNEXE, ARTICLE 2
# ═══════════════════════════════════════════════════════════════════════════
#
# L'ARITHMÉTIQUE EXACTE, PARCE QUE C'EST ELLE QUI FAIT BASCULER :
#
#   PME (§1)      : effectif < 250 ET (CA ≤ 50 M€ OU bilan ≤ 43 M€)
#   petite (§2)   : effectif < 50  ET (CA ≤ 10 M€ OU bilan ≤ 10 M€)
#   micro (§3)    : effectif < 10  ET (CA ≤  2 M€ OU bilan ≤  2 M€)
#   moyenne       : PME qui n'est ni petite ni micro
#   grande        : la négation de PME —
#                   effectif ≥ 250 OU (CA > 50 M€ ET bilan > 43 M€)
#
# LE « OU » DU SECOND MEMBRE EST LA PIÈGE : il suffit de rester sous L'UN des
# deux plafonds financiers pour rester PME. Une entreprise à 60 M€ de chiffre
# d'affaires et 20 M€ de bilan est encore une moyenne entreprise. Le lire
# comme un « ET » surqualifie, et c'est l'erreur la plus fréquente.
#
# ET UNE PARTICULARITÉ DE NIS 2 : l'article 2, §1, second alinéa, ÉCARTE
# l'article 3, §4, de l'annexe à la recommandation — la règle qui prive du
# statut de PME une entreprise détenue à 25 % ou plus par un organisme
# public. Sous NIS 2, une entreprise publique se mesure comme les autres.

SEUILS = {
    "pme": {"effectif": 250, "ca_eur": 50000000, "bilan_eur": 43000000,
            "article": "recommandation 2003/361/CE, annexe, art. 2, §1"},
    "petite": {"effectif": 50, "ca_eur": 10000000, "bilan_eur": 10000000,
               "article": "recommandation 2003/361/CE, annexe, art. 2, §2"},
    "micro": {"effectif": 10, "ca_eur": 2000000, "bilan_eur": 2000000,
              "article": "recommandation 2003/361/CE, annexe, art. 2, §3"},
}

ECART_RECOMMANDATION = {
    "quoi": "L'article 3, §4, de l'annexe à la recommandation 2003/361/CE "
            "— qui exclut du statut de PME une entreprise détenue à 25 % ou "
            "plus par un organisme public — ne s'applique pas aux fins de "
            "NIS 2.",
    "consequence": "Une entreprise publique ou à capitaux publics se mesure "
                   "sur son effectif et ses comptes, comme les autres.",
    "article": "art. 2, §1, second alinéa",
}

TAILLES = {
    "micro": {"nom": "Microentreprise", "rang": 0},
    "petite": {"nom": "Petite entreprise", "rang": 1},
    "moyenne": {"nom": "Moyenne entreprise", "rang": 2},
    "grande": {"nom": "Au-delà des plafonds PME", "rang": 3},
}


def _sous(valeur, plafond):
    """Un plafond qu'on ne renseigne pas n'est pas un plafond respecté."""
    return valeur is not None and valeur <= plafond


def taille(effectif=None, ca_eur=None, bilan_eur=None):
    """La catégorie de taille, et le fait qui l'a décidée.

    UNE DONNÉE MANQUANTE NE VAUT PAS UNE DONNÉE FAVORABLE. Si l'effectif
    n'est pas renseigné, aucune catégorie n'est prononcée : le module rend
    `indetermine` et dit ce qui manque. Deviner « petite » par défaut
    sortirait du champ une entité qui y est, et ce serait le seul défaut
    vraiment coûteux de tout le module.
    """
    manquants = []
    if effectif is None:
        manquants.append("effectif")
    if ca_eur is None and bilan_eur is None:
        manquants.append("chiffre d'affaires ou total du bilan")
    if manquants:
        return {"cle": "indetermine", "nom": "Indéterminée",
                "manquants": manquants,
                "dit": "La catégorie de taille ne se prononce pas sans %s."
                       % " ni ".join(manquants)}

    def financier(plafond):
        return _sous(ca_eur, plafond) or _sous(bilan_eur, plafond)

    s = SEUILS
    est_pme = effectif < s["pme"]["effectif"] and (
        _sous(ca_eur, s["pme"]["ca_eur"]) or
        _sous(bilan_eur, s["pme"]["bilan_eur"]))
    if not est_pme:
        motif = ("l'effectif atteint ou dépasse 250 personnes"
                 if effectif >= s["pme"]["effectif"] else
                 "le chiffre d'affaires dépasse 50 M€ ET le total du bilan "
                 "dépasse 43 M€")
        return dict(TAILLES["grande"], cle="grande", pourquoi=motif,
                    article=s["pme"]["article"])
    if effectif < s["micro"]["effectif"] and financier(s["micro"]["ca_eur"]):
        return dict(TAILLES["micro"], cle="micro",
                    pourquoi="moins de 10 personnes et 2 M€",
                    article=s["micro"]["article"])
    if effectif < s["petite"]["effectif"] and financier(s["petite"]["ca_eur"]):
        return dict(TAILLES["petite"], cle="petite",
                    pourquoi="moins de 50 personnes et 10 M€",
                    article=s["petite"]["article"])
    return dict(TAILLES["moyenne"], cle="moyenne",
                pourquoi="PME sans être une petite entreprise",
                article=s["pme"]["article"])


# ═══════════════════════════════════════════════════════════════════════════
#  LES CAS OÙ LA TAILLE NE COMPTE PAS — ARTICLE 2, §§2 À 4
# ═══════════════════════════════════════════════════════════════════════════
#
# CE QUE CETTE TABLE ÉVITE : un dirigeant de PME lit « moins de 50 salariés »
# et referme le dossier. Or huit portes d'entrée ignorent totalement la
# taille — et deux d'entre elles (prestataire de confiance, service DNS)
# mènent directement au statut d'entité ESSENTIELLE.

HORS_TAILLE = (
    {"cle": "communications_electroniques",
     "quoi": "Fournisseur de réseaux de communications électroniques publics "
             "ou de services de communications électroniques accessibles au "
             "public",
     "article": "art. 2, §2, a) i)", "statut": None},
    {"cle": "confiance",
     "quoi": "Prestataire de services de confiance",
     "article": "art. 2, §2, a) ii)", "statut": None},
    {"cle": "dns_tld",
     "quoi": "Registre de noms de domaine de premier niveau ou fournisseur de "
             "services DNS",
     "article": "art. 2, §2, a) iii)", "statut": "essentielle"},
    {"cle": "seul_prestataire",
     "quoi": "Seul prestataire, dans un État membre, d'un service essentiel "
             "au maintien d'activités sociétales ou économiques critiques",
     "article": "art. 2, §2, b)", "statut": None},
    {"cle": "securite_publique",
     "quoi": "Une perturbation du service pourrait avoir un impact important "
             "sur la sécurité publique, la sûreté publique ou la santé publique",
     "article": "art. 2, §2, c)", "statut": None},
    {"cle": "risque_systemique",
     "quoi": "Une perturbation pourrait induire un risque systémique "
             "important, en particulier avec un impact transfrontière",
     "article": "art. 2, §2, d)", "statut": None},
    {"cle": "importance_nationale",
     "quoi": "Entité critique en raison de son importance spécifique au "
             "niveau national ou régional",
     "article": "art. 2, §2, e)", "statut": None},
    {"cle": "administration_centrale",
     "quoi": "Entité de l'administration publique des pouvoirs publics "
             "centraux",
     "article": "art. 2, §2, f) i)", "statut": "essentielle"},
    {"cle": "administration_regionale",
     "quoi": "Entité de l'administration publique au niveau régional dont la "
             "perturbation pourrait avoir un impact important",
     "article": "art. 2, §2, f) ii)", "statut": None},
    {"cle": "entite_critique_2557",
     "quoi": "Entité recensée comme entité critique au titre de la directive "
             "(UE) 2022/2557 (résilience des entités critiques)",
     "article": "art. 2, §3", "statut": "essentielle"},
    {"cle": "enregistrement_noms_domaine",
     "quoi": "Entité fournissant des services d'enregistrement de noms de "
             "domaine",
     "article": "art. 2, §4", "statut": None},
)

HORS_TAILLE_PAR_CLE = {h["cle"]: h for h in HORS_TAILLE}

# LES PORTES QUI MÈNENT DIRECTEMENT AU STATUT D'ENTITÉ ESSENTIELLE, quelle
# que soit la taille — article 3, §1, b), d) et f).
ESSENTIELLE_HORS_TAILLE = {
    "confiance_qualifie": {
        "quoi": "Prestataire de services de confiance QUALIFIÉ",
        "article": "art. 3, §1, b)"},
    "dns_tld": {
        "quoi": "Registre de noms de domaine de premier niveau ou fournisseur "
                "de services DNS",
        "article": "art. 3, §1, b)"},
    "administration_centrale": {
        "quoi": "Entité de l'administration publique des pouvoirs publics "
                "centraux",
        "article": "art. 3, §1, d)"},
    "entite_critique_2557": {
        "quoi": "Entité critique au titre de la directive (UE) 2022/2557",
        "article": "art. 3, §1, f)"},
    "ose_2016_1148": {
        "quoi": "Opérateur de services essentiels identifié avant le "
                "16 janvier 2023 au titre de la directive (UE) 2016/1148, "
                "si l'État membre en dispose ainsi",
        "article": "art. 3, §1, g)"},
}

# LE CAS QUI SE LIT À L'ENVERS DE TOUS LES AUTRES — article 3, §1, c) : pour
# les communications électroniques accessibles au public, être une MOYENNE
# entreprise suffit à être essentielle. Partout ailleurs, moyenne = importante.
MOYENNE_SUFFIT = {
    "cle": "communications_electroniques",
    "quoi": "Fournisseur de réseaux de communications électroniques publics "
            "ou de services de communications électroniques accessibles au "
            "public constituant une moyenne entreprise",
    "article": "art. 3, §1, c)",
}


# ═══════════════════════════════════════════════════════════════════════════
#  LA QUALIFICATION
# ═══════════════════════════════════════════════════════════════════════════

STATUTS = {
    "essentielle": {
        "nom": "Entité essentielle", "rang": 2,
        "supervision": "ex_ante", "palier": "essentielle",
        "article": "art. 3, §1"},
    "importante": {
        "nom": "Entité importante", "rang": 1,
        "supervision": "ex_post", "palier": "importante",
        "article": "art. 3, §2"},
    "hors_champ": {
        "nom": "Hors du champ de la directive", "rang": 0,
        "supervision": None, "palier": None,
        "article": "art. 2, §1"},
}


def qualifier(declaration=None):
    """Essentielle, importante, ou hors champ — et POURQUOI.

    LE « POURQUOI » EST LE LIVRABLE, pas le statut. Un statut seul ferme la
    discussion ; le fait qui l'a décidé ouvre un chantier : si c'est un
    effet de seuil sur l'effectif, la question devient « à combien suis-je
    du seuil », et elle a une réponse chiffrée.
    """
    d = declaration or {}
    if not isinstance(d, dict):
        return {"ok": False, "motif": "declaration_illisible"}

    secteur_cle = d.get("secteur")
    secteur = SECTEURS.get(secteur_cle)
    t = taille(d.get("effectif"), d.get("ca_eur"), d.get("bilan_eur"))

    # ── LES PORTES QUI IGNORENT LA TAILLE ────────────────────────────────
    portes = [HORS_TAILLE_PAR_CLE[c] for c in HORS_TAILLE_PAR_CLE
              if d.get(c)]
    portes.sort(key=lambda h: [x["cle"] for x in HORS_TAILLE].index(h["cle"]))

    # ── LES PORTES QUI MÈNENT DIRECTEMENT À « ESSENTIELLE » ──────────────
    directes = [dict(ESSENTIELLE_HORS_TAILLE[c], cle=c)
                for c in sorted(ESSENTIELLE_HORS_TAILLE) if d.get(c)]

    if directes:
        return _verdict("essentielle", secteur, t, portes,
                        motif=directes[0]["quoi"],
                        article=directes[0]["article"],
                        seuil_franchi=False, directes=directes)

    # ── HORS DE TOUTE ANNEXE : la directive ne s'applique pas ────────────
    if secteur is None:
        return _verdict(
            "hors_champ", None, t, portes,
            motif="Le secteur déclaré ne figure ni à l'annexe I ni à "
                  "l'annexe II." if secteur_cle else
                  "Aucun secteur déclaré.",
            article="art. 2, §1", seuil_franchi=False, directes=[])

    # ── LA TAILLE, QUAND AUCUNE PORTE NE L'IGNORE ────────────────────────
    if t["cle"] == "indetermine" and not portes:
        return _verdict("hors_champ", secteur, t, portes,
                        motif="La taille n'est pas renseignée : la "
                              "qualification ne peut pas être prononcée.",
                        article="art. 2, §1", seuil_franchi=False,
                        directes=[], indetermine=True)

    petite = t["cle"] in ("micro", "petite")
    if petite and not portes:
        return _verdict(
            "hors_champ", secteur, t, portes,
            motif="Sous les seuils de la moyenne entreprise, et aucune des "
                  "portes de l'article 2, §§2 à 4, n'est déclarée.",
            article="art. 2, §1", seuil_franchi=False, directes=[])

    # Article 3, §1, c) — le cas qui se lit à l'envers.
    if (t["cle"] == "moyenne" and d.get("communications_electroniques")):
        return _verdict("essentielle", secteur, t, portes,
                        motif=MOYENNE_SUFFIT["quoi"],
                        article=MOYENNE_SUFFIT["article"],
                        seuil_franchi=False, directes=[])

    if secteur["annexe"] == "I" and t["cle"] == "grande":
        return _verdict(
            "essentielle", secteur, t, portes,
            motif="Secteur de l'annexe I, au-delà des plafonds de la moyenne "
                  "entreprise.",
            article="art. 3, §1, a)", seuil_franchi=True, directes=[])

    motif = ("Secteur de l'annexe II : le statut d'entité essentielle n'est "
             "pas atteignable par la taille."
             if secteur["annexe"] == "II" else
             "Secteur de l'annexe I, mais sous les plafonds de la moyenne "
             "entreprise." if t["cle"] == "moyenne" else
             "Une des portes de l'article 2, §§2 à 4, fait entrer l'entité "
             "dans le champ sans condition de taille.")
    return _verdict("importante", secteur, t, portes, motif=motif,
                    article="art. 3, §2",
                    seuil_franchi=(secteur["annexe"] == "I" and
                                   t["cle"] == "moyenne"),
                    directes=[])


def _verdict(statut, secteur, t, portes, motif, article, seuil_franchi,
             directes, indetermine=False):
    s = dict(STATUTS[statut], cle=statut)
    sortie = {
        "ok": True,
        "statut": s,
        "secteur": (dict(secteur, cle=[c for c, v in SECTEURS.items()
                                       if v is secteur][0])
                    if secteur else None),
        "taille": t,
        "motif": motif,
        "article": article,
        "portes_hors_taille": portes,
        "portes_essentielles": directes,
        "indetermine": indetermine,
        "ecart_recommandation": ECART_RECOMMANDATION,
        "source": SOURCE,
    }
    # ── L'EFFET DE SEUIL, CHIFFRÉ QUAND IL EST À PORTÉE ──────────────────
    #
    # CE QUE ÇA APPORTE : une entité importante de l'annexe I à 240 personnes
    # n'est pas « conforme », elle est à dix embauches du régime d'audits
    # réguliers. Le dire maintenant coûte une ligne ; le découvrir plus tard
    # coûte un budget d'audit non provisionné.
    #
    # CE QUE CE `statut == "importante"` ÉVITE : annoncer une bascule à qui
    # l'a déjà franchie. Un opérateur télécom moyenne entreprise est DÉJÀ
    # essentiel par l'article 3, §1, c) ; lui dire qu'il pourrait le devenir
    # en grandissant est faux, et lui ferait provisionner deux fois.
    sortie["bascule"] = None
    if (statut == "importante" and secteur and secteur["annexe"] == "I"
            and t.get("cle") == "moyenne"):
        sortie["bascule"] = {
            "vers": "essentielle",
            "fait": "franchir les plafonds de la moyenne entreprise — "
                    "250 personnes, ou 50 M€ de chiffre d'affaires ET 43 M€ "
                    "de total de bilan",
            "consequence": "supervision ex ante (art. 32) au lieu d'ex post "
                           "(art. 33), et palier de sanction porté de 7 M€ "
                           "à 10 M€ de plancher",
            "article": "art. 3, §1, a)",
        }
    sortie["seuil_franchi"] = seuil_franchi
    return sortie


# ═══════════════════════════════════════════════════════════════════════════
#  LE RÉGIME DE SUPERVISION — ARTICLES 32 ET 33
# ═══════════════════════════════════════════════════════════════════════════

REGIMES = {
    "ex_ante": {
        "nom": "Supervision ex ante",
        "article": "art. 32",
        "declencheur": "Aucun. L'autorité exerce ses pouvoirs de supervision "
                       "sans avoir à établir un manquement préalable.",
        "pouvoirs": (
            "Inspections sur place et contrôles à distance, y compris des "
            "contrôles aléatoires",
            "Audits de sécurité réguliers ET ciblés, par un organisme "
            "indépendant ou l'autorité",
            "Audits ad hoc, notamment après un incident important",
            "Scans de sécurité fondés sur des critères d'évaluation des "
            "risques",
            "Demandes d'informations nécessaires à l'évaluation des "
            "mesures de gestion des risques, y compris les politiques "
            "consignées par écrit",
            "Demandes d'accès aux données, aux documents et à toutes "
            "informations nécessaires",
            "Demandes de preuves de mise en œuvre des politiques de "
            "cybersécurité",
        ),
        "escalade": {
            "quoi": "Si les mesures d'exécution restent inefficaces, "
                    "l'autorité peut faire suspendre une certification ou "
                    "une autorisation, et faire INTERDIRE TEMPORAIREMENT au "
                    "directeur général ou au représentant légal d'exercer "
                    "des responsabilités dirigeantes dans l'entité.",
            "article": "art. 32, §5",
        },
    },
    "ex_post": {
        "nom": "Supervision ex post",
        "article": "art. 33",
        "declencheur": "Des éléments de preuve, des indications ou des "
                       "informations selon lesquels l'entité ne respecterait "
                       "pas la directive.",
        "pouvoirs": (
            "Inspections sur place et contrôles à distance ex post",
            "Audits de sécurité ciblés, par un organisme indépendant ou "
            "l'autorité",
            "Scans de sécurité fondés sur des critères d'évaluation des "
            "risques",
            "Demandes d'informations pour une évaluation ex post",
            "Demandes d'accès aux données et aux documents",
            "Demandes de preuves de mise en œuvre des politiques de "
            "cybersécurité",
        ),
        # LA DIFFÉRENCE QUI SE VOIT ICI ET NULLE PART AILLEURS : pas
        # d'escalade sur la personne du dirigeant pour une entité importante.
        "escalade": None,
    },
}


# ═══════════════════════════════════════════════════════════════════════════
#  LES DIX MESURES — ARTICLE 21, §2
# ═══════════════════════════════════════════════════════════════════════════
#
# « AU MOINS » : l'article dit que les mesures COMPRENNENT AU MOINS ces dix.
# Ce n'est pas une liste de contrôle qu'on épuise, c'est un socle en dessous
# duquel on ne descend pas. Le module compte les dix ; il ne prétend pas que
# les dix suffisent, et le dit.

MESURES = (
    ("a", "Analyse des risques et sécurité des systèmes d'information",
     "Les politiques qui disent comment le risque est apprécié, et comment "
     "la sécurité des systèmes en découle."),
    ("b", "Gestion des incidents",
     "Détecter, qualifier, traiter, clore — et savoir à quel moment "
     "l'horloge des 24 heures de l'article 23 démarre."),
    ("c", "Continuité des activités",
     "Sauvegardes, reprise d'activité et gestion de crise : ce qui permet de "
     "continuer à servir quand le système principal ne répond plus."),
    ("d", "Sécurité de la chaîne d'approvisionnement",
     "Les relations avec les fournisseurs et prestataires DIRECTS, en tenant "
     "compte des vulnérabilités propres à chacun et de la qualité de leurs "
     "pratiques (art. 21, §3)."),
    ("e", "Sécurité de l'acquisition, du développement et de la maintenance",
     "Y compris le traitement et la divulgation des vulnérabilités — le point "
     "de couture avec le CRA, qui impose la même chose côté produit."),
    ("f", "Politiques et procédures d'évaluation de l'efficacité des mesures",
     "Mesurer ce que les mesures produisent, pas seulement qu'elles existent."),
    ("g", "Cyberhygiène de base et formation à la cybersécurité",
     "Les pratiques élémentaires, et la formation — à distinguer de la "
     "formation des dirigeants, qui relève de l'article 20, §2."),
    ("h", "Cryptographie et, le cas échéant, chiffrement",
     "Les politiques et procédures qui disent quoi chiffrer, avec quoi, et "
     "qui détient les clés."),
    ("i", "Sécurité des ressources humaines, contrôle d'accès, gestion des "
     "actifs",
     "Les trois se tiennent : un inventaire d'actifs sans gestion des "
     "arrivées et des départs ne protège rien."),
    ("j", "Authentification à plusieurs facteurs ou continue, communications "
     "sécurisées",
     "Voix, vidéo et texte sécurisés, et des systèmes sécurisés de "
     "communication d'urgence au sein de l'entité, selon les besoins."),
)

MESURES_CLAUSE = {
    "socle": "Les mesures « comprennent au moins » ces dix éléments : c'est "
             "un plancher, pas une liste à épuiser.",
    "approche": "Approche « tous risques » — protéger les réseaux et les "
                "systèmes d'information ET leur environnement physique.",
    "proportionnalite": "La proportionnalité tient compte du degré "
                        "d'exposition, de la taille de l'entité, et de la "
                        "probabilité et de la gravité des incidents.",
    "correction": "Une entité qui constate qu'elle ne se conforme pas prend "
                  "sans retard injustifié les mesures correctives "
                  "nécessaires (art. 21, §4).",
    "article": "art. 21, §§1 à 4",
}

_ETATS = ("conforme", "partiel", "non_conforme", "sans_objet")


# ═══════════════════════════════════════════════════════════════════════════
#  LA GOUVERNANCE — ARTICLE 20
# ═══════════════════════════════════════════════════════════════════════════
#
# CE QUE CET ARTICLE FAIT, ET QU'AUCUN AUTRE TEXTE CYBER NE FAISAIT : il
# nomme une personne. Les organes de direction APPROUVENT les mesures,
# SUPERVISENT leur mise en œuvre, et PEUVENT ÊTRE TENUS RESPONSABLES de la
# violation de l'article 21. Ce n'est plus la DSI qui porte le sujet.

GOUVERNANCE = (
    {"cle": "approbation",
     "quoi": "L'organe de direction approuve les mesures de gestion des "
             "risques en matière de cybersécurité",
     "preuve": "Une délibération datée, nommant les mesures approuvées.",
     "article": "art. 20, §1"},
    {"cle": "supervision",
     "quoi": "L'organe de direction supervise la mise en œuvre de ces mesures",
     "preuve": "Un point récurrent à l'ordre du jour, avec des indicateurs "
               "et des décisions tracées.",
     "article": "art. 20, §1"},
    {"cle": "responsabilite",
     "quoi": "Les membres de l'organe de direction peuvent être tenus "
             "responsables de la violation de l'article 21 par l'entité",
     "preuve": "La chaîne de délégation écrite, et ce qu'elle ne délègue pas.",
     "article": "art. 20, §1"},
    {"cle": "formation_dirigeants",
     "quoi": "Les membres de l'organe de direction SONT TENUS de suivre une "
             "formation",
     "preuve": "Les attestations nominatives et datées des dirigeants "
               "eux-mêmes — pas celles des équipes.",
     "article": "art. 20, §2"},
    {"cle": "formation_personnel",
     "quoi": "L'entité est encouragée à offrir régulièrement une formation "
             "similaire à son personnel",
     "preuve": "Le plan de formation et son taux de réalisation.",
     "article": "art. 20, §2"},
)

# CE QUI SÉPARE LES DEUX FORMATIONS, et qu'un plan de formation unique
# confond : celle des dirigeants est une OBLIGATION (« sont tenus de »),
# celle du personnel est un ENCOURAGEMENT (« encouragent »). Une entreprise
# qui forme tout le monde sauf son conseil d'administration a manqué la
# seule des deux qui soit obligatoire.
GOUVERNANCE_OBLIGATOIRE = ("approbation", "supervision", "responsabilite",
                           "formation_dirigeants")


# ═══════════════════════════════════════════════════════════════════════════
#  LE SIGNALEMENT — ARTICLE 23
# ═══════════════════════════════════════════════════════════════════════════
#
# L'HORLOGE DÉMARRE À LA CONNAISSANCE, PAS À LA SURVENANCE. « Après avoir eu
# connaissance de l'incident important » — ce qui déplace la question de la
# détection vers la QUALIFICATION : le jour où quelqu'un, dans l'entreprise,
# a compris que c'était important, les 24 heures ont commencé.

SIGNALEMENT = {
    "destinataire": "Le CSIRT ou, selon le cas, l'autorité compétente",
    "depart": "La CONNAISSANCE de l'incident important — pas sa survenance, "
              "pas sa détection technique.",
    "article": "art. 23, §§1 et 4",
    "etapes": (
        {"cle": "alerte_precoce", "delai": "24 heures", "delai_h": 24,
         "quoi": "Alerte précoce",
         "contenu": "Indique, le cas échéant, si l'incident est suspecté "
                    "d'avoir été causé par des actes illicites ou "
                    "malveillants, et s'il pourrait avoir un impact "
                    "transfrontière.",
         "article": "art. 23, §4, a)"},
        {"cle": "notification", "delai": "72 heures", "delai_h": 72,
         "quoi": "Notification d'incident",
         "contenu": "Met à jour l'alerte précoce, fournit une évaluation "
                    "initiale — gravité, impact — et les indicateurs de "
                    "compromission lorsqu'ils sont disponibles.",
         "article": "art. 23, §4, b)"},
        {"cle": "intermediaire", "delai": "à la demande du CSIRT",
         "delai_h": None,
         "quoi": "Rapport intermédiaire",
         "contenu": "Les mises à jour pertinentes de la situation.",
         "article": "art. 23, §4, c)"},
        {"cle": "final", "delai": "1 mois après la notification",
         "delai_h": 720,
         "quoi": "Rapport final",
         "contenu": "Description détaillée de l'incident, type de menace ou "
                    "cause profonde, mesures d'atténuation appliquées et en "
                    "cours, et impact transfrontière le cas échéant.",
         "article": "art. 23, §4, d)"},
    ),
    "incident_en_cours": {
        "quoi": "Si l'incident est toujours en cours à la date du rapport "
                "final, l'entité fournit à cette date un RAPPORT "
                "D'AVANCEMENT, puis un rapport final dans un délai d'un mois "
                "à compter du traitement de l'incident.",
        "article": "art. 23, §4, e)",
    },
    # ═══ LA SECONDE NOTIFICATION, CELLE QU'ON OUBLIE ═══════════════════
    #
    # L'ARTICLE 23 EN IMPOSE DEUX, PAS UNE. Tout le monde retient le CSIRT ;
    # le même paragraphe 1 impose aussi de notifier LES DESTINATAIRES DES
    # SERVICES des incidents susceptibles de nuire à la fourniture de ces
    # services. Et le paragraphe 2 ajoute, en cas de cybermenace importante,
    # la communication aux destinataires potentiellement affectés des mesures
    # ou corrections qu'ILS peuvent appliquer.
    #
    # CE QUE ÇA CHANGE EN CELLULE DE CRISE : la liste des destinataires à
    # prévenir n'existe jamais le jour J. Elle se construit à froid, ou elle
    # ne se construit pas.
    "destinataires": {
        "incident": {
            "quoi": "Notifier aux destinataires des services les incidents "
                    "importants susceptibles de nuire à la fourniture de ces "
                    "services.",
            "quand": "Sans retard injustifié — aucun délai chiffré, ce qui "
                     "n'en fait pas une obligation molle : « sans retard "
                     "injustifié » se juge après coup, sur ce qu'on aurait "
                     "pu faire.",
            "article": "art. 23, §1"},
        "menace": {
            "quoi": "Communiquer aux destinataires potentiellement affectés "
                    "par une cybermenace importante les mesures ou "
                    "corrections qu'ils peuvent appliquer eux-mêmes.",
            "quand": "Sans retard injustifié.",
            "article": "art. 23, §2"},
        "dit": "Ces deux communications sont DISTINCTES de la notification au "
               "CSIRT et ne s'y substituent pas. La liste des destinataires à "
               "prévenir ne se fabrique pas le jour de l'incident.",
    },
    "sans_aveu": {
        "quoi": "Le simple fait de notifier un incident n'accroît pas la "
                "responsabilité de l'entité qui est à l'origine de la "
                "notification.",
        "consequence": "L'argument « ne notifions pas, ça nous incriminerait » "
                       "est écarté par le texte lui-même.",
        "article": "art. 23, §1",
    },
    "derogation_confiance": {
        "quoi": "Un prestataire de services de confiance notifie les "
                "incidents importants affectant la fourniture de ses "
                "services de confiance dans les 24 heures — et non 72.",
        "delai_h": 24,
        "article": "art. 23, §4, second alinéa",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
#  LES SANCTIONS — ARTICLE 34
# ═══════════════════════════════════════════════════════════════════════════
#
# LE MOT QUI CHANGE TOUT : « AU MOINS ». L'article 34, §§4 et 5, impose aux
# États membres des amendes d'un maximum d'AU MOINS ces montants. Le chiffre
# n'est donc pas ce que l'entreprise risque au maximum ; c'est le minimum
# que l'État doit rendre possible. Une transposition nationale peut prévoir
# davantage — et le module ne dira jamais « votre exposition maximale est de
# X », seulement « le plancher européen du plafond est de X ».

SANCTIONS = {
    "essentielle": {
        "nom": "Entités essentielles", "rang": 1,
        "plancher_eur": 10000000, "part_ca": 2.0,
        "retenu": "le montant le plus élevé",
        "article": "art. 34, §4"},
    "importante": {
        "nom": "Entités importantes", "rang": 0,
        "plancher_eur": 7000000, "part_ca": 1.4,
        "retenu": "le montant le plus élevé",
        "article": "art. 34, §5"},
}

NATURE_PLANCHER = {
    "quoi": "Les montants de l'article 34 sont des PLANCHERS imposés aux "
            "États membres (« un maximum d'au moins »), pas des plafonds "
            "opposables à l'administration.",
    "consequence": "L'exposition réelle se lit dans la loi de transposition "
                   "de chaque État membre où l'entité fournit ses services. "
                   "Le chiffre ci-dessous est un minimum européen.",
    "difference_cra": "Le règlement (UE) 2024/2847 (CRA), lui, est "
                      "d'application directe : ses montants sont les "
                      "montants. Traiter NIS 2 comme le CRA sous-estime "
                      "l'exposition.",
    "article": "art. 34, §§4 et 5",
}


def seuil_de_bascule(palier):
    """Le chiffre d'affaires à partir duquel le pourcentage passe devant.

    LE FAIT QUE CETTE FONCTION REND VISIBLE, ET QU'AUCUNE LECTURE DE
    L'ARTICLE 34 NE DONNE : les deux paliers pivotent au MÊME chiffre
    d'affaires — 500 M€. 10 M€ / 2 % = 500 M€ ; 7 M€ / 1,4 % = 500 M€.

    Ce n'est pas une coïncidence de calcul, c'est le rapport 10/7 = 2/1,4
    tenu par le législateur : au-dessus de 500 M€, la qualification
    essentielle/importante ne change plus le RÉGIME de calcul — les deux
    paliers sont proportionnels — mais elle continue d'écarter les montants
    de 43 %. En dessous, les deux planchers forfaitaires commandent, et
    l'écart est le même 43 %. La qualification pèse donc partout autant :
    il n'existe aucune taille où être « importante » plutôt
    qu'« essentielle » cesserait d'alléger la sanction.
    """
    if palier not in SANCTIONS:
        return None
    s = SANCTIONS[palier]
    return s["plancher_eur"] / (s["part_ca"] / 100.0)


def exposition(chiffre_affaires=None, statut=None):
    """Le plancher européen du plafond, pour un chiffre d'affaires donné.

    LE CHIFFRE D'AFFAIRES EST CELUI DU GROUPE, ET MONDIAL, comme pour le
    RGPD : « du chiffre d'affaires annuel mondial total de l'entreprise à
    laquelle l'entité essentielle appartient ». Lire le chiffre d'affaires
    de la seule filiale concernée divise l'exposition par l'écart entre la
    filiale et le groupe, et c'est le plus gros facteur d'erreur possible.
    """
    ca = chiffre_affaires
    if ca is not None and (not isinstance(ca, (int, float)) or ca < 0):
        return {"ok": False, "motif": "chiffre_affaires_illisible"}
    cles = ([statut] if statut in SANCTIONS else sorted(
        SANCTIONS, key=lambda c: -SANCTIONS[c]["rang"]))
    lignes = []
    for cle in cles:
        s = SANCTIONS[cle]
        part = (ca * s["part_ca"] / 100.0) if ca is not None else None
        lignes.append({
            "cle": cle, "nom": s["nom"], "article": s["article"],
            "plancher_eur": s["plancher_eur"], "part_ca": s["part_ca"],
            "part_eur": part,
            "retenu_eur": (max(s["plancher_eur"], part)
                           if part is not None else None),
            "borne_retenue": (None if part is None else
                              ("part_ca" if part > s["plancher_eur"]
                               else "plancher")),
            "pivot_eur": seuil_de_bascule(cle),
        })
    return {
        "ok": True,
        "chiffre_affaires": ca,
        "assiette": "Chiffre d'affaires annuel mondial total de l'entreprise "
                    "à laquelle l'entité appartient — pas celui de la seule "
                    "entité concernée.",
        "lignes": lignes,
        "pivot_commun_eur": seuil_de_bascule("essentielle"),
        "dit_pivot": "Les deux paliers pivotent au même chiffre d'affaires — "
                     "500 M€ : en dessous, ce sont les planchers "
                     "forfaitaires qui commandent ; au-dessus, les "
                     "pourcentages. L'écart entre les deux qualifications "
                     "reste de 43 % de part et d'autre.",
        "nature": NATURE_PLANCHER,
        "source": SOURCE,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  L'ÉVALUATION
# ═══════════════════════════════════════════════════════════════════════════

def evaluer(declaration=None, aujourdhui=None):
    """Qualifier, puis mesurer l'écart — dans cet ordre, jamais l'inverse.

    POURQUOI CET ORDRE : l'écart sur les dix mesures ne veut rien dire tant
    qu'on ne sait pas si l'entité est dans le champ. Un tableau d'écarts
    servi à une entreprise hors champ lui vend un chantier qu'elle ne doit
    pas mener ; servi à une entité essentielle sans dire que ses audits
    seront réguliers et non déclenchés, il sous-estime l'échéance.
    """
    d = declaration or {}
    if not isinstance(d, dict):
        return {"ok": False, "motif": "declaration_illisible"}
    nom = str(d.get("nom") or "").strip()
    if not nom:
        return {"ok": False, "motif": "nom_manquant"}

    q = qualifier(d)
    if not q.get("ok"):
        return q

    statut = q["statut"]["cle"]
    regime = (REGIMES[q["statut"]["supervision"]]
              if q["statut"]["supervision"] else None)

    return {
        "ok": True,
        "nom": nom,
        "qualification": q,
        "regime": regime,
        "mesures": _ecarts_mesures(d.get("mesures") or {}),
        "gouvernance": _ecarts_gouvernance(d.get("gouvernance") or {}),
        "signalement": SIGNALEMENT if statut != "hors_champ" else None,
        "derogation_confiance": (
            SIGNALEMENT["derogation_confiance"] if d.get("confiance") or
            d.get("confiance_qualifie") else None),
        "enregistrement": _enregistrement(d, aujourdhui),
        "calendrier": calendrier(aujourdhui),
        "sanctions": (dict(SANCTIONS[q["statut"]["palier"]],
                           cle=q["statut"]["palier"])
                      if q["statut"]["palier"] else None),
        "nature_plancher": NATURE_PLANCHER,
        "source": SOURCE,
    }


def _ecarts_mesures(declares):
    """Les dix mesures — une case vide n'est pas une case verte."""
    lignes = []
    for cle, nom, dit in MESURES:
        e = declares.get(cle)
        lignes.append({"cle": cle, "nom": nom, "dit": dit,
                       "etat": e if e in _ETATS else "non_renseigne"})
    compte = {e: sum(1 for l in lignes if l["etat"] == e)
              for e in _ETATS + ("non_renseigne",)}
    retenus = len(lignes) - compte["sans_objet"]
    return {
        "lignes": lignes,
        "total": len(lignes),
        "compte": compte,
        "retenus": retenus,
        "conformes": compte["conforme"],
        # LE TAUX NE VOYAGE JAMAIS SEUL : `non_renseigne` l'accompagne,
        # parce qu'un 100 % sur deux mesures renseignées ne dit rien des huit.
        "taux": (round(100.0 * compte["conforme"] / retenus)
                 if retenus else None),
        "non_renseigne": compte["non_renseigne"],
        "clause": MESURES_CLAUSE,
    }


def _ecarts_gouvernance(declares):
    """L'article 20 — et la ligne qui n'est pas facultative.

    LE PIÈGE QUE CETTE FONCTION REND VISIBLE : `formation_personnel` est un
    encouragement, les quatre autres sont des obligations. Compter les cinq
    au même titre rend un taux de 80 % à une entreprise qui a manqué la
    formation de ses dirigeants — le seul manquement des cinq qui expose
    personnellement quelqu'un.
    """
    lignes = []
    for g in GOUVERNANCE:
        e = declares.get(g["cle"])
        lignes.append(dict(
            g, etat=e if e in _ETATS else "non_renseigne",
            obligatoire=(g["cle"] in GOUVERNANCE_OBLIGATOIRE)))
    obligatoires = [l for l in lignes if l["obligatoire"]]
    tenus = [l for l in obligatoires if l["etat"] == "conforme"]
    manques = [l for l in obligatoires if l["etat"] != "conforme"]
    return {
        "lignes": lignes,
        "obligatoires": len(obligatoires),
        "tenus": len(tenus),
        "manques": [l["cle"] for l in manques],
        "taux": round(100.0 * len(tenus) / len(obligatoires)),
        "dit": ("Les cinq lignes ne pèsent pas pareil : quatre sont des "
                "obligations, la formation du personnel est un "
                "encouragement. Le taux ci-dessus ne compte que les quatre."),
    }


def _enregistrement(d, aujourdhui=None):
    """L'obligation dont l'échéance est DERRIÈRE nous.

    CE QUE ÇA CHANGE : toutes les autres lignes du module décrivent un
    chantier à mener. Celle-ci décrit un retard déjà constitué, si l'entité
    est dans le champ et ne s'est pas déclarée. C'est la seule ligne qui se
    règle en une semaine, et la seule qu'on ne voit pas venir.
    """
    cal = calendrier(aujourdhui)
    ligne = [l for l in cal["echeances"] if l["cle"] == "enregistrement"][0]
    fait = bool(d.get("enregistre"))
    return {
        "echeance": ligne,
        "fait": fait,
        "en_retard": (ligne["applicable"] and not fait),
        "informations": (
            "Nom de l'entité",
            "Adresse et coordonnées actualisées, y compris adresses "
            "électroniques, plages d'IP et numéros de téléphone",
            "Secteur et sous-secteur des annexes I ou II",
            "Liste des États membres où l'entité fournit des services "
            "relevant du champ de la directive",
        ),
        "mise_a_jour": "Toute modification est notifiée sans tarder, et en "
                       "tout état de cause dans un délai de deux semaines.",
        "article": "art. 3, §4",
    }


def evaluer_groupe(entites=None, aujourdhui=None):
    """Plusieurs entités — et ce qui COMMANDE l'organisation à monter.

    ═══ CE QUI COMMANDE N'EST PAS LA MOYENNE ════════════════════════════
    Un groupe de douze filiales dont une seule est essentielle n'a pas
    « 8 % de supervision ex ante » : il a des audits réguliers à subir, un
    dirigeant exposé à une interdiction d'exercer, et un palier de sanction
    à 10 M€. La filiale la plus haute décide de l'organisation ; la moyenne
    ne décrit aucune filiale réelle et rassure à tort.

    ET LE SECOND FAIT QUE SEUL UN GROUPE RÉVÈLE : une entité qui opère dans
    plusieurs États membres relève de plusieurs transpositions. Le module
    compte ces États, parce que c'est le multiplicateur de la charge
    déclarative, et qu'aucune lecture entité par entité ne le fait voir.
    """
    liste = entites or []
    if not isinstance(liste, list):
        return {"ok": False, "motif": "groupe_illisible"}
    noms = [str((e or {}).get("nom") or "").strip() for e in liste]
    retenus = [n for n in noms if n]
    if len(set(retenus)) != len(retenus):
        return {"ok": False, "motif": "noms_en_double"}

    cotes, hors = [], []
    etats = set()
    for e in liste:
        r = evaluer(e, aujourdhui)
        if not r.get("ok"):
            continue
        for x in (e.get("etats_membres") or []):
            if str(x).strip():
                etats.add(str(x).strip())
        if r["qualification"]["statut"]["cle"] == "hors_champ":
            hors.append(r)
        else:
            cotes.append(r)

    if not cotes:
        return {"ok": True, "cotes": 0, "hors_champ": hors, "commande": None,
                "etats_membres": sorted(etats),
                "dit": "Aucune entité déclarée dans le champ de la directive.",
                "source": SOURCE}

    pire = max(cotes, key=lambda r: r["qualification"]["statut"]["rang"])
    essentielles = [r for r in cotes
                    if r["qualification"]["statut"]["cle"] == "essentielle"]
    retards = [r["nom"] for r in cotes if r["enregistrement"]["en_retard"]]
    return {
        "ok": True,
        "cotes": len(cotes),
        "entites": cotes,
        "hors_champ": hors,
        "commande": {"nom": pire["nom"], "statut": pire["qualification"]["statut"]},
        "essentielles": len(essentielles),
        "noms_essentielles": [r["nom"] for r in essentielles],
        "etats_membres": sorted(etats),
        "retards_enregistrement": retards,
        "calendrier": calendrier(aujourdhui),
        "dit": ("%d entité(s) sur %d relèvent de la supervision ex ante "
                "(art. 32). C'est ce chiffre — et non un taux de conformité "
                "— qui fixe la charge : ces entités subissent des audits "
                "réguliers sans qu'aucun incident ne soit nécessaire."
                % (len(essentielles), len(cotes))),
        "dit_transposition": (
            "Le groupe opère dans %d État(s) membre(s) déclaré(s) : autant "
            "de lois de transposition, autant d'autorités compétentes, et "
            "autant de régimes de sanction possiblement plus sévères que le "
            "plancher européen." % len(etats)) if etats else (
            "Aucun État membre déclaré : la charge déclarative de "
            "l'article 3, §4, ne peut pas être estimée."),
        "source": SOURCE,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  LA GARDE — CE QUE CE MODULE REFUSE DE LAISSER PASSER
# ═══════════════════════════════════════════════════════════════════════════

def _verifier():
    fautes = []

    # ── LES SECTEURS ─────────────────────────────────────────────────────
    if len(ANNEXE_I) != 11:
        fautes.append("l'annexe I ne compte pas 11 secteurs : %d"
                      % len(ANNEXE_I))
    if len(ANNEXE_II) != 7:
        fautes.append("l'annexe II ne compte pas 7 secteurs : %d"
                      % len(ANNEXE_II))
    if len(SECTEURS) != len(ANNEXE_I) + len(ANNEXE_II):
        fautes.append("deux secteurs portent la même clé entre les annexes")
    for cle, s in SECTEURS.items():
        if s["plafond"] not in STATUTS:
            fautes.append("le secteur « %s » plafonne à un statut inconnu"
                          % cle)
    # L'ANNEXE II NE MÈNE JAMAIS À « ESSENTIELLE » PAR LA TAILLE — c'est le
    # fait qui distingue les deux annexes, et il doit tenir dans la table.
    for cle, _n, _s in ANNEXE_II:
        if SECTEURS[cle]["plafond"] != "importante":
            fautes.append("le secteur d'annexe II « %s » prétend atteindre "
                          "le statut d'entité essentielle" % cle)

    # ── LES STATUTS ──────────────────────────────────────────────────────
    rangs = sorted(s["rang"] for s in STATUTS.values())
    if rangs != list(range(len(STATUTS))):
        fautes.append("les rangs de statut ne sont pas 0..n : %s" % rangs)
    for cle, s in STATUTS.items():
        if cle == "hors_champ":
            continue
        if s["supervision"] not in REGIMES:
            fautes.append("le statut « %s » ne renvoie à aucun régime de "
                          "supervision" % cle)
        if s["palier"] not in SANCTIONS:
            fautes.append("le statut « %s » ne dit pas à quel palier de "
                          "sanction il expose" % cle)

    # ── LE RÉGIME EX ANTE EST BIEN LE PLUS LOURD ─────────────────────────
    #
    # ET SURTOUT : l'escalade sur la personne du dirigeant n'existe QUE pour
    # les entités essentielles. Une table qui la donnerait aux deux effacerait
    # la conséquence la plus lourde de la qualification.
    if REGIMES["ex_ante"].get("escalade") is None:
        fautes.append("le régime ex ante a perdu l'escalade de l'art. 32, §5")
    if REGIMES["ex_post"].get("escalade") is not None:
        fautes.append("le régime ex post s'est vu attribuer une escalade que "
                      "l'article 33 ne prévoit pas")
    if len(REGIMES["ex_ante"]["pouvoirs"]) <= len(REGIMES["ex_post"]["pouvoirs"]):
        fautes.append("le régime ex ante n'est pas plus étendu que l'ex post")

    # ── LES DIX MESURES ──────────────────────────────────────────────────
    if len(MESURES) != 10:
        fautes.append("l'article 21, §2, ne compte pas 10 mesures : %d"
                      % len(MESURES))
    cles = [c for c, _n, _d in MESURES]
    if cles != list("abcdefghij"):
        fautes.append("les mesures ne sont pas étiquetées a..j : %s" % cles)

    # ── LA GOUVERNANCE ───────────────────────────────────────────────────
    cles_g = [g["cle"] for g in GOUVERNANCE]
    if len(set(cles_g)) != len(cles_g):
        fautes.append("deux lignes de gouvernance portent la même clé")
    for c in GOUVERNANCE_OBLIGATOIRE:
        if c not in cles_g:
            fautes.append("l'obligation « %s » ne figure dans aucune ligne "
                          "de gouvernance" % c)
    # LA LIGNE QUI N'EST PAS OBLIGATOIRE DOIT RESTER NON OBLIGATOIRE : si
    # elle rejoignait le tuple, le taux de l'article 20 compterait un
    # encouragement comme une obligation.
    if "formation_personnel" in GOUVERNANCE_OBLIGATOIRE:
        fautes.append("la formation du personnel — un encouragement — est "
                      "comptée comme une obligation")
    for g in GOUVERNANCE:
        if not str(g.get("article") or "").strip():
            fautes.append("la ligne de gouvernance « %s » ne cite aucun "
                          "article" % g["cle"])

    # ── LE SIGNALEMENT ───────────────────────────────────────────────────
    delais = [e["delai_h"] for e in SIGNALEMENT["etapes"]]
    if delais[:2] != [24, 72]:
        fautes.append("les deux premiers délais de signalement ne sont pas "
                      "24 h puis 72 h : %s" % delais)
    if len(SIGNALEMENT["etapes"]) != 4:
        fautes.append("la chaîne de signalement n'a pas quatre étapes")
    if SIGNALEMENT["derogation_confiance"]["delai_h"] != 24:
        fautes.append("la dérogation « prestataire de confiance » ne ramène "
                      "pas la notification à 24 h")
    # LES DEUX NOTIFICATIONS DE L'ARTICLE 23, ET PAS SEULEMENT CELLE DU
    # CSIRT. Perdre le volet « destinataires » ferait rendre une chaîne de
    # signalement qui a l'air complète et qui laisse une obligation dehors.
    dest = SIGNALEMENT.get("destinataires") or {}
    for cle in ("incident", "menace"):
        if not (dest.get(cle) or {}).get("article"):
            fautes.append("la notification aux destinataires — volet « %s » — "
                          "a disparu de l'article 23" % cle)
    if not SIGNALEMENT.get("sans_aveu"):
        fautes.append("la clause « notifier n'accroît pas la responsabilité » "
                      "a disparu — c'est elle qui désamorce le conseil de ne "
                      "pas notifier")
    if not SIGNALEMENT.get("incident_en_cours"):
        fautes.append("l'article 23, §4, e) — le rapport d'avancement quand "
                      "l'incident est toujours en cours — a disparu")

    # ── LES SANCTIONS ────────────────────────────────────────────────────
    r2 = sorted(s["rang"] for s in SANCTIONS.values())
    if r2 != list(range(len(SANCTIONS))):
        fautes.append("les rangs de palier ne sont pas 0..n : %s" % r2)
    for cle, s in SANCTIONS.items():
        if not (s.get("plancher_eur") and s.get("part_ca")):
            fautes.append("le palier « %s » n'a pas ses DEUX bornes — un "
                          "palier qui n'en aurait qu'une ferait disparaître "
                          "le « montant le plus élevé étant retenu »" % cle)
    ordre = sorted(SANCTIONS, key=lambda c: -SANCTIONS[c]["rang"])
    for a, b in zip(ordre, ordre[1:]):
        if not (SANCTIONS[a]["plancher_eur"] > SANCTIONS[b]["plancher_eur"]
                and SANCTIONS[a]["part_ca"] > SANCTIONS[b]["part_ca"]):
            fautes.append("le palier « %s » n'est pas plus lourd que « %s » "
                          "sur les deux bornes" % (a, b))
    # LE MOT QUI TIENT TOUT LE CHIFFRAGE. Si « plancher » disparaissait des
    # noms de champ, la restitution présenterait un minimum comme un maximum.
    for cle, s in SANCTIONS.items():
        if "plancher_eur" not in s:
            fautes.append("le palier « %s » ne nomme plus son montant comme "
                          "un plancher" % cle)
    # LES DEUX PALIERS PIVOTENT AU MÊME CHIFFRE D'AFFAIRES — c'est le
    # rapport 10/7 = 2/1,4 tenu par le législateur. Si un montant bougeait
    # sans l'autre, la restitution annoncerait un pivot commun qui n'existe
    # plus, et le conseil « au-dessus de 500 M€ » deviendrait faux pour un
    # des deux paliers.
    pivots = [seuil_de_bascule(c) for c in SANCTIONS]
    if max(pivots) - min(pivots) > 1.0:
        fautes.append("les deux paliers ne pivotent plus au même chiffre "
                      "d'affaires : %s" % [round(x) for x in pivots])
    if round(pivots[0]) != 500000000:
        fautes.append("le pivot commun n'est plus 500 M€ : %d"
                      % round(pivots[0]))
    if SOURCE.get("nature") != "directive":
        fautes.append("la source ne se déclare plus comme une directive — "
                      "le chiffrage présenterait des planchers comme des "
                      "plafonds")
    if not SOURCE.get("licence"):
        fautes.append("la source ne dit pas sous quelle licence elle est "
                      "reprise")
    if not SOURCE.get("reserve"):
        fautes.append("la source ne porte plus la réserve de transposition")

    # ── LES PORTES HORS TAILLE ───────────────────────────────────────────
    cles_h = [h["cle"] for h in HORS_TAILLE]
    if len(set(cles_h)) != len(cles_h):
        fautes.append("deux portes hors taille portent la même clé")
    for h in HORS_TAILLE:
        if h["statut"] is not None and h["statut"] not in STATUTS:
            fautes.append("la porte « %s » mène à un statut inconnu"
                          % h["cle"])
        if not str(h.get("article") or "").strip():
            fautes.append("la porte « %s » ne cite aucun article" % h["cle"])

    # ── L'ARITHMÉTIQUE DES SEUILS, VÉRIFIÉE SUR SES BORNES ───────────────
    #
    # CE QUE CES CAS ATTRAPENT, ET QU'UNE RELECTURE N'ATTRAPE PAS : le « OU »
    # du second membre de la définition PME. 60 M€ de chiffre d'affaires avec
    # 20 M€ de bilan reste une moyenne entreprise ; le lire comme un « ET »
    # la ferait passer « grande », et l'entité deviendrait essentielle à tort.
    cas = (
        ({"effectif": 260, "ca_eur": 1000000}, "grande"),
        ({"effectif": 249, "ca_eur": 60000000, "bilan_eur": 50000000},
         "grande"),
        ({"effectif": 249, "ca_eur": 60000000, "bilan_eur": 20000000},
         "moyenne"),
        ({"effectif": 100, "ca_eur": 30000000}, "moyenne"),
        ({"effectif": 49, "ca_eur": 9000000}, "petite"),
        ({"effectif": 9, "ca_eur": 1000000}, "micro"),
        ({"effectif": 9}, "indetermine"),
        ({"ca_eur": 1000000}, "indetermine"),
    )
    for entree, attendu in cas:
        rendu = taille(**entree)["cle"]
        if rendu != attendu:
            fautes.append("taille(%s) rend « %s » au lieu de « %s »"
                          % (entree, rendu, attendu))

    # ── CHAQUE CHEMIN DE QUALIFICATION MÈNE À UN STATUT DE LA TABLE ──────
    chemins = (
        {},
        {"secteur": "energie", "effectif": 300, "ca_eur": 80000000},
        {"secteur": "energie", "effectif": 100, "ca_eur": 30000000},
        {"secteur": "dechets", "effectif": 5000, "ca_eur": 900000000},
        {"secteur": "sante", "effectif": 20, "ca_eur": 3000000},
        {"secteur": "sante", "effectif": 20, "ca_eur": 3000000,
         "seul_prestataire": True},
        {"secteur": "infrastructure_numerique", "effectif": 3,
         "ca_eur": 400000, "dns_tld": True},
        {"secteur": "infrastructure_numerique", "effectif": 100,
         "ca_eur": 30000000, "communications_electroniques": True},
        {"secteur": "administration_publique", "administration_centrale": True},
    )
    for c in chemins:
        q = qualifier(c)
        if not q.get("ok") or q["statut"]["cle"] not in STATUTS:
            fautes.append("la qualification rend un statut inconnu pour %s"
                          % c)

    if fautes:
        raise RuntimeError("nis2 — table incohérente : " + " ; ".join(fautes))
    return fautes


_FAUTES = _verifier()
