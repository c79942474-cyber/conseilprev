# -*- coding: utf-8 -*-
"""
DORA — QUI EST DANS LE CHAMP, ET SOUS QUEL RÉGIME.

═══ CE QUE CE MODULE DÉCIDE, ET CE QU'IL REFUSE DE DÉCIDER ═══════════════
Il dit si une entité relève du règlement (UE) 2022/2554, par quel point de
l'article 2 elle y entre, et — c'est le point qui commande tout le reste —
si elle relève du cadre COMPLET ou du cadre SIMPLIFIÉ de l'article 16.

IL NE REND PAS D'AVIS JURIDIQUE. La qualification réelle est prononcée par
l'autorité compétente — l'ACPR ou l'AMF en France, les autorités
européennes de surveillance au niveau de l'Union. Ce module prépare la
discussion ; il ne la ferme pas.

═══ POURQUOI LE RÉGIME, ET NON LE STATUT ════════════════════════════════
NIS 2 se joue sur « essentielle ou importante » : deux statuts, deux
régimes de supervision. DORA ne fonctionne pas ainsi. Les vingt types
d'entités financières de l'article 2, paragraphe 1, points a) à t), sont
TOUS dans le champ, sans gradation. Ce qui varie, c'est l'épaisseur des
obligations, et elle se décide à l'article 16 : cinq catégories d'entités
échappent aux articles 5 à 15 et relèvent d'un cadre allégé.

C'EST DONC LE RÉGIME QU'IL FAUT ANNONCER, PAS LE STATUT. Annoncer les
vingt-sept articles du titre II du règlement délégué (UE) 2024/1774 à une
petite institution de retraite professionnelle serait faux, et coûteux :
le client paierait un programme dont la moitié ne le vise pas.

═══ LA TAILLE N'EST PAS LE RÉGIME, ET LES CONFONDRE SERAIT UNE FAUTE ════
L'article 3 définit microentreprise, petite et moyenne entreprise. Ces
définitions servent ailleurs — notamment pour écarter la règle des
incidents récurrents. Elles ne décident PAS du cadre simplifié, qui repose
sur des catégories nommées à l'article 16, paragraphe 1, et non sur des
seuils d'effectif. Une microentreprise qui n'est dans aucune des cinq
catégories relève du cadre complet.
"""

VERSION = "2026-09-a"

REGLEMENT = ("Règlement (UE) 2022/2554 du Parlement européen et du Conseil "
             "du 14 décembre 2022 sur la résilience opérationnelle numérique "
             "du secteur financier")

RESERVE = (
    "Ce module prépare une qualification ; il ne la prononce pas. La "
    "qualification réelle relève de l'autorité compétente — ACPR ou AMF en "
    "France, autorités européennes de surveillance au niveau de l'Union."
)

# ═══════════════════════════════════════════════════════════════════════
# 1. LES TEXTES DU CORPUS — ET CE QUE CHACUN PERMET
# ═══════════════════════════════════════════════════════════════════════
# UNE SOURCE SANS ADRESSE EST UNE INTENTION, PAS UNE SOURCE. Les textes de
# l'Union sont réutilisables avec attribution : on cite les numéros et les
# intitulés d'articles, et ce que chacun exige est écrit par le cabinet.

SOURCES = (
    {"cle": "dora", "celex": "32022R2554",
     "titre": "Règlement (UE) 2022/2554 (DORA)",
     "lien": "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554",
     "apporte": "Le socle : champ d'application, gestion du risque lié aux "
                "TIC, incidents, tests, prestataires tiers. 64 articles."},
    {"cle": "directive", "celex": "32022L2556",
     "titre": "Directive (UE) 2022/2556",
     "lien": "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022L2556",
     "apporte": "Aligne huit directives sectorielles financières sur la "
                "résilience opérationnelle numérique."},
    {"cle": "rts_1772", "celex": "32024R1772",
     "titre": "Règlement délégué (UE) 2024/1772",
     "lien": "https://eur-lex.europa.eu/eli/reg_del/2024/1772/oj",
     "apporte": "Classification des incidents liés aux TIC et des "
                "cybermenaces, et seuils d'importance significative."},
    {"cle": "rts_1773", "celex": "32024R1773",
     "titre": "Règlement délégué (UE) 2024/1773",
     "lien": "https://eur-lex.europa.eu/eli/reg_del/2024/1773/oj",
     "apporte": "Contenu de la politique relative aux accords contractuels "
                "sur les services TIC soutenant des fonctions critiques."},
    {"cle": "rts_1774", "celex": "32024R1774",
     "titre": "Règlement délégué (UE) 2024/1774",
     "lien": "https://eur-lex.europa.eu/eli/reg_del/2024/1774/oj",
     "apporte": "Outils, méthodes, processus et politiques de gestion du "
                "risque lié aux TIC, et cadre simplifié. 42 articles."},
    {"cle": "rts_532", "celex": "32025R0532",
     "titre": "Règlement délégué (UE) 2025/532",
     "lien": "https://eur-lex.europa.eu/eli/reg_del/2025/532/oj",
     "apporte": "Ce qu'une entité doit déterminer et évaluer lorsqu'elle "
                "sous-traite des services TIC soutenant des fonctions "
                "critiques ou importantes."},
)

# CE QUE LE CORPUS NE PORTE PAS, ET QU'ON N'INVENTERA DONC PAS.
# L'article 19, paragraphe 4, renvoie les DÉLAIS de déclaration à l'acte
# d'exécution visé à l'article 20, premier alinéa, point a) ii). Cet acte
# n'est pas au corpus. Les valeurs qui circulent — quatre heures, soixante-
# douze heures, un mois — ne se lisent nulle part dans ce qui est chargé
# ici, et un module qui les afficherait les présenterait comme sourcées.
LACUNES = (
    {"cle": "delais_declaration",
     "quoi": "Les délais de la notification initiale, du rapport "
             "intermédiaire et du rapport final.",
     "ou": "Article 19, paragraphe 4, qui renvoie à l'acte d'exécution de "
           "l'article 20, premier alinéa, point a) ii).",
     "pourquoi": "L'acte d'exécution n'est pas au corpus. Ce module "
                 "n'affiche donc aucun délai chiffré : le faire "
                 "présenterait comme sourcé un chiffre qui ne l'est pas."},
    {"cle": "tlpt",
     "quoi": "Les modalités des tests de pénétration fondés sur la menace.",
     "ou": "Articles 26 et 27, qui renvoient à des normes techniques.",
     "pourquoi": "Les normes visées ne sont pas au corpus."},
    {"cle": "tiers_critiques",
     "quoi": "La liste des prestataires tiers de services TIC désignés "
             "critiques.",
     "ou": "Article 31.",
     "pourquoi": "Elle est tenue par les autorités européennes de "
                 "surveillance, et n'est pas dans le texte."},
)


# ═══════════════════════════════════════════════════════════════════════
# 2. LE CHAMP D'APPLICATION — ARTICLE 2, PARAGRAPHE 1
# ═══════════════════════════════════════════════════════════════════════
# Vingt et une entrées, de a) à u). Les vingt premières sont collectivement
# les « entités financières » (art. 2, §2) ; la vingt et unième, les
# prestataires tiers de services TIC, est dans le champ à un autre titre —
# elle ne porte pas les obligations des chapitres II à IV, elle est la
# CONTREPARTIE des obligations du chapitre V.

ENTITES = (
    ("etablissement_credit", "a", "Établissement de crédit", True),
    ("etablissement_paiement", "b", "Établissement de paiement, y compris "
     "exempté au titre de la directive (UE) 2015/2366", True),
    ("information_comptes", "c", "Prestataire de services d'information sur "
     "les comptes", True),
    ("monnaie_electronique", "d", "Établissement de monnaie électronique, y "
     "compris exempté au titre de la directive 2009/110/CE", True),
    ("entreprise_investissement", "e", "Entreprise d'investissement", True),
    ("crypto_actifs", "f", "Prestataire de services sur crypto-actifs agréé, "
     "et émetteur de jetons se référant à un ou des actifs", True),
    ("depositaire_central", "g", "Dépositaire central de titres", True),
    ("contrepartie_centrale", "h", "Contrepartie centrale", True),
    ("plateforme_negociation", "i", "Plate-forme de négociation", True),
    ("referentiel_central", "j", "Référentiel central", True),
    ("gestionnaire_fia", "k", "Gestionnaire de fonds d'investissement "
     "alternatifs", True),
    ("societe_gestion", "l", "Société de gestion", True),
    ("communication_donnees", "m", "Prestataire de services de communication "
     "de données", True),
    ("assurance", "n", "Entreprise d'assurance ou de réassurance", True),
    ("intermediaire_assurance", "o", "Intermédiaire d'assurance, de "
     "réassurance ou d'assurance à titre accessoire", True),
    ("retraite_professionnelle", "p", "Institution de retraite "
     "professionnelle", True),
    ("notation_credit", "q", "Agence de notation de crédit", True),
    ("indices_reference", "r", "Administrateur d'indices de référence "
     "d'importance critique", True),
    ("financement_participatif", "s", "Prestataire de services de financement "
     "participatif", True),
    ("referentiel_titrisations", "t", "Référentiel des titrisations", True),
    ("prestataire_tic", "u", "Prestataire tiers de services TIC", False),
)

ENTITES_PAR_CLE = {e[0]: e for e in ENTITES}

# Les vingt premières, collectivement « entités financières » — art. 2, §2.
FINANCIERES = tuple(e[0] for e in ENTITES if e[3])


# ═══════════════════════════════════════════════════════════════════════
# 3. LES EXCLUSIONS — ARTICLE 2, PARAGRAPHE 3
# ═══════════════════════════════════════════════════════════════════════
# UNE EXCLUSION N'EST PAS UNE DISPENSE PARTIELLE : le règlement ne
# s'applique pas. Les confondre avec le cadre simplifié — qui, lui,
# s'applique — serait l'erreur la plus coûteuse de ce module.

EXCLUSIONS = (
    {"cle": "fia_article_3_2", "lettre": "a",
     "quoi": "Gestionnaire de fonds d'investissement alternatifs visé à "
             "l'article 3, paragraphe 2, de la directive 2011/61/UE",
     "vise": ("gestionnaire_fia",)},
    {"cle": "assurance_article_4", "lettre": "b",
     "quoi": "Entreprise d'assurance ou de réassurance visée à l'article 4 "
             "de la directive 2009/138/CE",
     "vise": ("assurance",)},
    {"cle": "irp_quinze_affilies", "lettre": "c",
     "quoi": "Institution de retraite professionnelle dont les régimes ne "
             "comptent pas plus de quinze affiliés au total",
     "vise": ("retraite_professionnelle",)},
    {"cle": "mifid_articles_2_3", "lettre": "d",
     "quoi": "Personne physique ou morale exemptée au titre des articles 2 "
             "et 3 de la directive 2014/65/UE",
     "vise": ("entreprise_investissement",)},
    {"cle": "intermediaire_pme", "lettre": "e",
     "quoi": "Intermédiaire d'assurance, de réassurance ou d'assurance à "
             "titre accessoire qui est une microentreprise ou une petite ou "
             "moyenne entreprise",
     "vise": ("intermediaire_assurance",)},
    {"cle": "cheques_postaux", "lettre": "f",
     "quoi": "Office des chèques postaux visé à l'article 2, paragraphe 5, "
             "point 3), de la directive 2013/36/UE",
     "vise": ("etablissement_credit",)},
)

EXCLUSIONS_PAR_CLE = {x["cle"]: x for x in EXCLUSIONS}

OPTION_ETAT_MEMBRE = {
    "article": "Article 2, paragraphe 4",
    "quoi": "Un État membre peut exclure de son territoire les entités "
            "visées à l'article 2, paragraphe 5, points 4) à 23), de la "
            "directive 2013/36/UE.",
    "consequence": "L'option est propre à chaque État membre et doit être "
                   "vérifiée auprès de l'autorité nationale. Elle n'est pas "
                   "présumée exercée.",
}


# ═══════════════════════════════════════════════════════════════════════
# 4. LE RÉGIME — ARTICLE 16, PARAGRAPHE 1
# ═══════════════════════════════════════════════════════════════════════

REGIMES = {
    "complet": {
        "nom": "Cadre complet",
        "quoi": "Les articles 5 à 15 s'appliquent, précisés par le titre II "
                "du règlement délégué (UE) 2024/1774 — vingt-sept articles.",
        "articles": "Articles 5 à 15",
        "rts": "Règlement délégué (UE) 2024/1774, titre II",
    },
    "simplifie": {
        "nom": "Cadre simplifié",
        "quoi": "Les articles 5 à 15 ne s'appliquent pas. L'article 16, "
                "paragraphe 1, deuxième alinéa, leur substitue huit "
                "obligations, précisées par le titre III du règlement "
                "délégué (UE) 2024/1774 — quatorze articles.",
        "articles": "Article 16",
        "rts": "Règlement délégué (UE) 2024/1774, titre III",
    },
    "hors_champ": {
        "nom": "Hors du champ du règlement",
        "quoi": "Le règlement ne s'applique pas.",
        "articles": "Article 2, paragraphe 3",
        "rts": None,
    },
}

# Les cinq catégories de l'article 16, paragraphe 1, premier alinéa.
SIMPLIFIE = (
    {"cle": "petite_investissement_non_interconnectee",
     "quoi": "Petite entreprise d'investissement non interconnectée",
     "vise": ("entreprise_investissement",)},
    {"cle": "paiement_exempte",
     "quoi": "Établissement de paiement exempté au titre de la directive "
             "(UE) 2015/2366",
     "vise": ("etablissement_paiement",)},
    {"cle": "credit_exempte_sans_option",
     "quoi": "Établissement exempté au titre de la directive 2013/36/UE pour "
             "lequel l'État membre a décidé de ne PAS appliquer l'option de "
             "l'article 2, paragraphe 4",
     "vise": ("etablissement_credit",)},
    {"cle": "monnaie_electronique_exempte",
     "quoi": "Établissement de monnaie électronique exempté au titre de la "
             "directive 2009/110/CE",
     "vise": ("monnaie_electronique",)},
    {"cle": "petite_irp",
     "quoi": "Petite institution de retraite professionnelle",
     "vise": ("retraite_professionnelle",)},
)

SIMPLIFIE_PAR_CLE = {s["cle"]: s for s in SIMPLIFIE}

# Article 16, paragraphe 1, deuxième alinéa — les huit obligations qui
# remplacent les articles 5 à 15.
OBLIGATIONS_SIMPLIFIE = (
    ("a", "Cadre de gestion du risque lié aux TIC solide et documenté, "
          "protection des composantes et infrastructures physiques comprise"),
    ("b", "Surveillance permanente de la sécurité et du fonctionnement de "
          "tous les systèmes de TIC"),
    ("c", "Réduction au minimum de l'incidence du risque, par des systèmes, "
          "protocoles et outils solides, résilients et actualisés"),
    ("d", "Identification et détection rapides des sources de risque et des "
          "anomalies, et traitement rapide des incidents"),
    ("e", "Recensement des principales dépendances vis-à-vis des "
          "prestataires tiers de services TIC"),
    ("f", "Continuité des fonctions critiques ou importantes, par des plans "
          "de continuité et des mesures de sauvegarde et de restauration"),
    ("g", "Tests réguliers de ces plans et de l'efficacité des contrôles"),
    ("h", "Mise en œuvre des conclusions des tests et de l'analyse "
          "post-incident, et programmes de sensibilisation et de formation"),
)


# ═══════════════════════════════════════════════════════════════════════
# 5. LES TAILLES — ARTICLE 3, POINTS 60 À 64
# ═══════════════════════════════════════════════════════════════════════
# ELLES NE DÉCIDENT PAS DU RÉGIME. Elles servent ailleurs : la règle des
# incidents récurrents ne vise pas les microentreprises. Les faire décider
# du cadre simplifié serait une lecture fausse, et elle est tentante.

TAILLES = {
    "micro": {
        "nom": "Microentreprise",
        "quoi": "Moins de dix personnes employées, et chiffre d'affaires "
                "annuel ou total du bilan n'excédant pas 2 millions d'euros.",
        "exclut": ("plateforme_negociation", "contrepartie_centrale",
                   "referentiel_central", "depositaire_central"),
    },
    "petite": {
        "nom": "Petite entreprise",
        "quoi": "Dix personnes ou plus et moins de cinquante, et chiffre "
                "d'affaires annuel ou total du bilan supérieur à 2 millions "
                "d'euros sans excéder 10 millions.",
        "exclut": (),
    },
    "moyenne": {
        "nom": "Moyenne entreprise",
        "quoi": "Au-delà de la petite entreprise et en deçà des seuils de la "
                "grande entreprise, au sens de l'article 3.",
        "exclut": (),
    },
    "grande": {
        "nom": "Grande entreprise",
        "quoi": "Au-delà des seuils de la moyenne entreprise.",
        "exclut": (),
    },
    "indetermine": {
        "nom": "Taille non déclarée",
        "quoi": "La taille n'est pas renseignée.",
        "exclut": (),
    },
}


def taille(effectif=None, ca_eur=None, bilan_eur=None, entite=None):
    """La taille au sens de l'article 3 — ou « indéterminé », qui se dit.

    LE « OU » DE L'ARTICLE EST UN VRAI « OU ». « dont le chiffre d'affaires
    annuel et/ou le total du bilan annuel n'excède pas 2 millions d'euros » :
    un seul des deux suffit. Lire « et » resterait sans effet sur la plupart
    des dossiers et se tromperait sur ceux qui comptent.
    """
    if effectif is None:
        return dict(TAILLES["indetermine"], cle="indetermine")
    try:
        n = int(effectif)
    except (TypeError, ValueError):
        return dict(TAILLES["indetermine"], cle="indetermine")

    montants = [m for m in (ca_eur, bilan_eur) if m is not None]
    petit_montant = any(float(m) <= 2_000_000 for m in montants) if montants else None

    if n < 10:
        # UNE MICROENTREPRISE EST AUSSI DÉFINIE PAR CE QU'ELLE N'EST PAS :
        # quatre types d'entités ne peuvent jamais l'être, quelle que soit
        # leur taille.
        if entite in TAILLES["micro"]["exclut"]:
            return dict(TAILLES["petite"], cle="petite",
                        note="Moins de dix personnes, mais ce type d'entité "
                             "ne peut pas être une microentreprise au sens "
                             "de l'article 3.")
        if petit_montant is None:
            return dict(TAILLES["indetermine"], cle="indetermine",
                        note="L'effectif est sous dix personnes, mais ni le "
                             "chiffre d'affaires ni le bilan ne sont "
                             "déclarés : la microentreprise ne peut pas être "
                             "établie.")
        if petit_montant:
            return dict(TAILLES["micro"], cle="micro")
        return dict(TAILLES["petite"], cle="petite")
    if n < 50:
        return dict(TAILLES["petite"], cle="petite")
    if n < 250:
        return dict(TAILLES["moyenne"], cle="moyenne")
    return dict(TAILLES["grande"], cle="grande")


# ═══════════════════════════════════════════════════════════════════════
# 6. LA QUALIFICATION
# ═══════════════════════════════════════════════════════════════════════

def qualifier(declaration=None):
    """Dans le champ ou non, et sous quel régime — et POURQUOI.

    LE « POURQUOI » EST LE LIVRABLE. Un régime annoncé sans le fait qui l'a
    décidé ferme la discussion ; le fait l'ouvre — et s'il s'agit d'une
    exemption sectorielle, la question devient « cette exemption tient-elle
    encore », qui a une réponse vérifiable.
    """
    d = declaration or {}
    if not isinstance(d, dict):
        return {"ok": False, "motif": "declaration_illisible"}

    cle = (d.get("entite") or "").strip()
    if cle not in ENTITES_PAR_CLE:
        return {
            "ok": True, "dans_le_champ": None, "regime": None,
            "entite": None, "a_completer": True,
            "motif": "Aucun type d'entité déclaré, ou type inconnu de "
                     "l'article 2, paragraphe 1.",
            "article": "Article 2, paragraphe 1",
            "reserve": RESERVE,
        }

    e = ENTITES_PAR_CLE[cle]
    t = taille(d.get("effectif"), d.get("ca_eur"), d.get("bilan_eur"), cle)

    # ── LES EXCLUSIONS D'ABORD : hors champ, il n'y a pas de régime ──────
    declarees = [x for x in EXCLUSIONS
                 if d.get(x["cle"]) and cle in x["vise"]]
    if declarees:
        return {
            "ok": True, "dans_le_champ": False, "regime": "hors_champ",
            "entite": {"cle": cle, "lettre": e[1], "nom": e[2],
                       "financiere": e[3]},
            "taille": t,
            "exclusions": [dict(x) for x in declarees],
            "motif": declarees[0]["quoi"],
            "article": "Article 2, paragraphe 3, point %s"
                       % declarees[0]["lettre"],
            "a_completer": False,
            "option_etat_membre": dict(OPTION_ETAT_MEMBRE),
            "reserve": RESERVE,
        }

    # ── LE PRESTATAIRE TIERS N'EST PAS UNE ENTITÉ FINANCIÈRE ────────────
    # Il est dans le champ, mais pas au même titre : il ne porte pas les
    # obligations des chapitres II à IV. Lui annoncer un « régime » de
    # gestion du risque lié aux TIC serait lui prêter des devoirs qui
    # appartiennent à son client.
    if not e[3]:
        return {
            "ok": True, "dans_le_champ": True, "regime": None,
            "entite": {"cle": cle, "lettre": e[1], "nom": e[2],
                       "financiere": False},
            "taille": t,
            "exclusions": [],
            "motif": "Prestataire tiers de services TIC : dans le champ du "
                     "règlement au titre du chapitre V, comme contrepartie "
                     "des obligations de l'entité financière cliente. Les "
                     "chapitres II à IV ne lui sont pas opposables.",
            "article": "Article 2, paragraphe 1, point u)",
            "a_completer": False,
            "designation_critique": {
                "quoi": "Un prestataire peut être désigné critique au titre "
                        "de l'article 31, et relève alors d'un cadre de "
                        "supervision européen.",
                "reserve": "La liste des prestataires désignés est tenue par "
                           "les autorités européennes de surveillance ; elle "
                           "n'est pas dans le texte et n'est pas reproduite "
                           "ici.",
            },
            "reserve": RESERVE,
        }

    # ── LE RÉGIME ───────────────────────────────────────────────────────
    portes = [s for s in SIMPLIFIE if d.get(s["cle"]) and cle in s["vise"]]
    if portes:
        return {
            "ok": True, "dans_le_champ": True, "regime": "simplifie",
            "entite": {"cle": cle, "lettre": e[1], "nom": e[2],
                       "financiere": True},
            "taille": t,
            "exclusions": [],
            "porte": dict(portes[0]),
            "motif": portes[0]["quoi"],
            "article": "Article 16, paragraphe 1",
            "obligations": [{"lettre": a, "quoi": b}
                            for a, b in OBLIGATIONS_SIMPLIFIE],
            "a_completer": False,
            "reserve": RESERVE,
        }

    return {
        "ok": True, "dans_le_champ": True, "regime": "complet",
        "entite": {"cle": cle, "lettre": e[1], "nom": e[2],
                   "financiere": True},
        "taille": t,
        "exclusions": [],
        "porte": None,
        "motif": "Aucune des cinq catégories de l'article 16, paragraphe 1, "
                 "n'est déclarée : les articles 5 à 15 s'appliquent.",
        "article": "Articles 5 à 15",
        "a_completer": False,
        "reserve": RESERVE,
    }


def evaluer(declaration=None):
    """L'ÉVALUATION D'ENSEMBLE — qualifier, puis mesurer, dans cet ordre.

    L'ORDRE N'EST PAS UN CONFORT DE PRÉSENTATION, C'EST LA LOGIQUE DU
    RÈGLEMENT. Le régime de l'article 16 décide de quels articles du
    règlement délégué (UE) 2024/1774 sont opposables ; mesurer avant de
    qualifier revient à choisir le référentiel au hasard. Les moteurs en
    aval refusent d'ailleurs de travailler sans régime, et ce refus
    remonte ici tel quel plutôt que d'être masqué par un taux.

    Les imports sont locaux : `dora_ponts` importe ce module, et un import
    en tête de fichier fermerait le cercle.
    """
    import dora_risque as _risque
    import dora_tiers as _tiers
    import dora_ponts as _ponts

    d = declaration if isinstance(declaration, dict) else {}
    q = qualifier(d)
    if not q.get("ok"):
        return {"ok": False, "motif": q.get("motif", "declaration_illisible")}

    regime = q.get("regime")
    mesurable = regime in _risque.REGIMES

    contrats = d.get("contrats")
    contrats = contrats if isinstance(contrats, list) else []
    examens = [_tiers.examiner(c) for c in contrats]
    recevables = [x for x in examens if x.get("ok")]

    return {
        "ok": True,
        "version": VERSION,
        "qualification": q,
        "regime": regime,
        # « MESURABLE » EST LE MOT JUSTE, ET IL N'EST PAS « CONFORME ». Une
        # entité hors champ ou un prestataire tiers n'a pas de régime : il
        # n'y a rien à mesurer, ce qui ne dit rien de son état.
        "mesurable": mesurable,
        "articulation": _ponts.articulation(q, d.get("identifiee_nis2")),
        "risque": _risque.evaluer(regime, d.get("etats")) if mesurable
                  else None,
        "ecarts_risque": _risque.ecarts(regime, d.get("etats")) if mesurable
                         else None,
        "apport_iso27001": _ponts.apport(regime, d.get("mesures_iso"))
                           if mesurable else None,
        "contrats": examens,
        # LE TAUX DES CONTRATS EST CELUI DU PIRE, PAS LA MOYENNE. Un parc de
        # dix contrats dont neuf sont complets et un vide n'est pas « à
        # 90 % » : c'est le contrat vide que l'autorité ouvrira, et une
        # moyenne le ferait disparaître.
        "taux_contrats": (min(x["taux"] for x in recevables)
                          if recevables else None),
        "contrats_irrecevables": len(examens) - len(recevables),
        "reserve": RESERVE,
    }


def referentiel():
    return {
        "version": VERSION,
        "reglement": REGLEMENT,
        "reserve": RESERVE,
        "sources": [dict(s) for s in SOURCES],
        "lacunes": [dict(l) for l in LACUNES],
        "entites": [{"cle": a, "lettre": b, "nom": c, "financiere": d}
                    for a, b, c, d in ENTITES],
        "exclusions": [dict(x) for x in EXCLUSIONS],
        "option_etat_membre": dict(OPTION_ETAT_MEMBRE),
        "regimes": {k: dict(v) for k, v in REGIMES.items()},
        "simplifie": [dict(s) for s in SIMPLIFIE],
        "obligations_simplifie": [{"lettre": a, "quoi": b}
                                  for a, b in OBLIGATIONS_SIMPLIFIE],
        "tailles": {k: dict(v) for k, v in TAILLES.items()},
    }


# ═══════════════════════════════════════════════════════════════════════
# 7. LE RÉFÉRENTIEL SE CONTREDIT-IL ? CONTRÔLÉ À L'IMPORT
# ═══════════════════════════════════════════════════════════════════════

def _verifier():
    assert len(ENTITES) == 21, \
        "l'article 2, paragraphe 1, compte vingt et une entrées, de a) à u)"
    lettres = [e[1] for e in ENTITES]
    assert lettres == list("abcdefghijklmnopqrstu"), lettres
    assert len(FINANCIERES) == 20, \
        "vingt entités financières — les points a) à t)"
    assert ENTITES[-1][0] == "prestataire_tic" and not ENTITES[-1][3]

    assert len(EXCLUSIONS) == 6, \
        "l'article 2, paragraphe 3, compte six exclusions"
    for x in EXCLUSIONS:
        for v in x["vise"]:
            assert v in ENTITES_PAR_CLE, \
                "l'exclusion %s vise un type inconnu : %s" % (x["cle"], v)

    assert len(SIMPLIFIE) == 5, \
        "l'article 16, paragraphe 1, nomme cinq catégories"
    for s in SIMPLIFIE:
        for v in s["vise"]:
            assert v in ENTITES_PAR_CLE, s["cle"]

    assert len(OBLIGATIONS_SIMPLIFIE) == 8, \
        "l'article 16, paragraphe 1, deuxième alinéa, compte huit points"
    assert [a for a, _ in OBLIGATIONS_SIMPLIFIE] == list("abcdefgh")

    assert set(REGIMES) == {"complet", "simplifie", "hors_champ"}
    cles_sources = [s["cle"] for s in SOURCES]
    assert len(cles_sources) == len(set(cles_sources))
    for s in SOURCES:
        assert s["lien"].startswith("https://"), s["cle"]
    for l in LACUNES:
        assert l["ou"].strip() and l["pourquoi"].strip(), l["cle"]


_verifier()
