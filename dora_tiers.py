# -*- coding: utf-8 -*-
"""
DORA — LES PRESTATAIRES TIERS DE SERVICES TIC, ET CE QUE LE CONTRAT DOIT DIRE.

═══ LE DÉFAUT QUE CE MODULE VISE ═══════════════════════════════════════
L'article 30 ne demande pas « un bon contrat ». Il énumère des clauses, et
il en énumère DEUX séries : neuf pour tout contrat de services TIC, six de
plus lorsque le service soutient une fonction critique ou importante. Un
contrat signé avant 2025 porte rarement les secondes — les droits d'audit
illimités et la stratégie de sortie sont les deux qui manquent le plus
souvent, et ce sont justement celles qu'une autorité regarde.

═══ LA SECONDE SÉRIE EST CONDITIONNELLE, ET C'EST LE VERROU ═════════════
Réclamer les quinze clauses sur un contrat de bureautique ferait perdre du
temps et du crédit. Réclamer les neuf seulement sur un contrat
d'hébergement du cœur de métier ferait manquer l'essentiel. La criticité
de la fonction soutenue commande — elle se déclare, elle ne se devine pas,
et tant qu'elle n'est pas déclarée ce module refuse de compter.

═══ LA DÉROGATION MICROENTREPRISE EST DANS LE TEXTE ═════════════════════
L'article 30, paragraphe 3, dernier alinéa, permet à une microentreprise de
convenir que les droits d'accès, d'inspection et d'audit soient délégués à
une tierce partie indépendante. La taire ferait porter à une petite
structure une exigence que le règlement lui-même aménage.

═══ ET LA CHAÎNE DE SOUS-TRAITANCE A SON PROPRE TEXTE ═══════════════════
Le règlement délégué (UE) 2025/532 précise ce qu'une entité doit
déterminer et évaluer lorsqu'elle sous-traite des services TIC soutenant
des fonctions critiques. C'est l'angle mort habituel : le contrat de
premier rang est soigné, et personne ne sait qui est au troisième.
"""

VERSION = "2026-09-a"

SOURCES = {
    "socle": "Règlement (UE) 2022/2554, articles 28 à 30",
    "politique": "Règlement délégué (UE) 2024/1773 — contenu de la politique "
                 "relative aux accords contractuels sur les services TIC "
                 "soutenant des fonctions critiques ou importantes",
    "sous_traitance": "Règlement délégué (UE) 2025/532 — éléments à "
                      "déterminer et évaluer en cas de sous-traitance de "
                      "services TIC soutenant des fonctions critiques",
}

RESERVE = (
    "Cette liste est celle de l'article 30 du règlement (UE) 2022/2554. "
    "Elle dit ce que le contrat doit COMPORTER ; elle ne juge pas la "
    "rédaction des clauses, qui relève d'un conseil juridique."
)

# ═══════════════════════════════════════════════════════════════════════
# 1. LES NEUF CLAUSES DE TOUT CONTRAT — ARTICLE 30, PARAGRAPHE 2
# ═══════════════════════════════════════════════════════════════════════

CLAUSES_COMMUNES = (
    ("a", "Description claire et exhaustive des services et fonctions "
          "fournis, et si la sous-traitance est autorisée — avec ses "
          "conditions"),
    ("b", "Lieux — régions ou pays — où les services sont fournis et où les "
          "données sont traitées et stockées, et obligation d'informer avant "
          "tout changement"),
    ("c", "Dispositions sur la disponibilité, l'authenticité, l'intégrité et "
          "la confidentialité, données à caractère personnel comprises"),
    ("d", "Garantie d'accès, de récupération et de restitution des données "
          "en cas d'insolvabilité, de résolution, de cessation d'activité ou "
          "de résiliation"),
    ("e", "Description des niveaux de service, avec leurs mises à jour et "
          "révisions"),
    ("f", "Assistance en cas d'incident lié aux TIC, sans frais "
          "supplémentaires ou à un coût déterminé à l'avance"),
    ("g", "Coopération pleine du prestataire avec les autorités compétentes "
          "et les autorités de résolution"),
    ("h", "Droits de résiliation et délais de préavis minimaux"),
    ("i", "Conditions de participation aux programmes de sensibilisation et "
          "de formation à la résilience opérationnelle numérique"),
)

# ═══════════════════════════════════════════════════════════════════════
# 2. LES SIX CLAUSES DE PLUS — ARTICLE 30, PARAGRAPHE 3
# ═══════════════════════════════════════════════════════════════════════
# Elles ne s'ajoutent QUE si le service soutient une fonction critique ou
# importante. « en plus de ceux qui figurent au paragraphe 2 » : c'est un
# cumul, pas un remplacement.

CLAUSES_CRITIQUES = (
    ("a", "Niveaux de service complets, avec des objectifs de performance "
          "quantitatifs et qualitatifs précis permettant un suivi effectif "
          "et des mesures correctives"),
    ("b", "Délais de préavis et obligations de notification, y compris de "
          "tout développement susceptible d'affecter significativement la "
          "capacité du prestataire"),
    ("c", "Mise en œuvre et test de plans d'urgence, et mesures, outils et "
          "politiques de sécurité des TIC de niveau approprié"),
    ("d", "Participation et coopération pleines au test de pénétration fondé "
          "sur la menace de l'entité financière (articles 26 et 27)"),
    ("e", "Droit de suivi permanent des performances : droits illimités "
          "d'accès, d'inspection et d'audit, niveaux d'assurance "
          "alternatifs, coopération aux inspections sur place, précisions "
          "sur leur portée et leur fréquence"),
    ("f", "Stratégie de sortie : période de transition obligatoire pendant "
          "laquelle le service continue, et qui permet de migrer ailleurs "
          "ou de réinternaliser"),
)

DEROGATION_MICRO = {
    "vise": "e",
    "article": "Article 30, paragraphe 3, dernier alinéa",
    "quoi": "Une entité financière qui est une microentreprise peut convenir "
            "que les droits d'accès, d'inspection et d'audit soient délégués "
            "à une tierce partie indépendante nommée par le prestataire, "
            "l'entité restant habilitée à lui demander en tout temps des "
            "informations et une garantie sur la performance.",
}

CLAUSES_TYPES = {
    "article": "Article 30, paragraphe 4",
    "quoi": "Les parties envisagent l'utilisation de clauses contractuelles "
            "types élaborées par les autorités publiques pour des services "
            "particuliers.",
    "portee": "C'est une incitation, pas une obligation de résultat — le "
              "texte dit « envisagent ».",
}

# ═══════════════════════════════════════════════════════════════════════
# 3. LA CHAÎNE DE SOUS-TRAITANCE — RÈGLEMENT DÉLÉGUÉ (UE) 2025/532
# ═══════════════════════════════════════════════════════════════════════

SOUS_TRAITANCE = (
    (1, "Profil de risque global et complexité"),
    (2, "Application à l'échelle d'un groupe"),
    (3, "Diligence requise et évaluation des risques en ce qui concerne le "
        "recours à des sous-traitants"),
    (4, "Conditions de sous-traitance des services TIC qui soutiennent des "
        "fonctions critiques ou importantes"),
    (5, "Changements significatifs apportés aux accords de sous-traitance"),
    (6, "Résiliation du contrat entre l'entité financière et le prestataire "
        "tiers"),
)

ETATS = {
    "absente":   {"nom": "Absente du contrat", "vaut": 0.0},
    "partielle": {"nom": "Présente mais incomplète", "vaut": 0.5},
    "presente":  {"nom": "Présente", "vaut": 1.0},
    "deleguee":  {"nom": "Déléguée à une tierce partie (dérogation "
                         "microentreprise)", "vaut": 1.0},
}


def clauses_attendues(critique, microentreprise=False):
    """Les clauses que CE contrat doit comporter — ni plus, ni moins."""
    out = [{"serie": "commune", "lettre": a, "quoi": b,
            "article": "Article 30, paragraphe 2, point %s)" % a}
           for a, b in CLAUSES_COMMUNES]
    if critique:
        for a, b in CLAUSES_CRITIQUES:
            e = {"serie": "critique", "lettre": a, "quoi": b,
                 "article": "Article 30, paragraphe 3, point %s)" % a}
            if a == DEROGATION_MICRO["vise"] and microentreprise:
                e["derogation"] = dict(DEROGATION_MICRO)
            out.append(e)
    return out


def examiner(contrat=None):
    """Ce qui manque au contrat, et sous quel article.

    LA CRITICITÉ SE DÉCLARE. Tant qu'elle ne l'est pas, ce module ne compte
    rien : il rendrait sinon un taux sur neuf clauses alors que quinze sont
    peut-être dues, et ce taux serait rassurant à tort.
    """
    c = contrat if isinstance(contrat, dict) else {}
    critique = c.get("fonction_critique")
    if critique is None:
        return {"ok": False, "motif": "criticite_non_declaree",
                "motif_texte": "La fonction soutenue est-elle critique ou "
                               "importante ? Sans cette réponse, on ne sait "
                               "pas si neuf clauses sont dues, ou quinze.",
                "reserve": RESERVE}

    micro = bool(c.get("microentreprise"))
    etats = c.get("clauses") if isinstance(c.get("clauses"), dict) else {}
    attendues = clauses_attendues(critique, micro)

    lignes, acquis = [], 0.0
    for cl in attendues:
        cle = "%s_%s" % (cl["serie"], cl["lettre"])
        e = etats.get(cle) or etats.get(cl["lettre"] if cl["serie"] == "commune"
                                        else cle)
        if e == "deleguee" and "derogation" not in cl:
            # LA DÉROGATION NE VAUT QUE POUR LA CLAUSE QU'ELLE VISE, et
            # seulement pour une microentreprise. L'accepter ailleurs ferait
            # passer une absence pour un aménagement prévu par le texte.
            e = "absente"
        vaut = ETATS[e]["vaut"] if e in ETATS else 0.0
        acquis += vaut
        lignes.append(dict(cl, etat=e if e in ETATS else "absente",
                           vaut=vaut))

    manquantes = [l for l in lignes if l["vaut"] < 1.0]
    taux = round(100.0 * acquis / len(attendues), 1) if attendues else None

    verrous = []
    critiques_absentes = [l for l in manquantes if l["serie"] == "critique"]
    if critique and critiques_absentes:
        verrous.append({
            "cle": "clauses_critiques_absentes",
            "dit": "%d clause(s) du paragraphe 3 manquent sur un contrat qui "
                   "soutient une fonction critique. Ce sont celles que "
                   "l'autorité regarde en premier : le droit d'audit "
                   "illimité et la stratégie de sortie."
                   % len(critiques_absentes)})
    if micro and not critique:
        verrous.append({
            "cle": "derogation_sans_objet",
            "dit": "La dérogation microentreprise ne vise que le point e) du "
                   "paragraphe 3, qui ne s'applique pas ici : la fonction "
                   "n'est pas déclarée critique."})

    return {
        "ok": True,
        "fonction_critique": bool(critique),
        "microentreprise": micro,
        "attendues": len(attendues),
        "taux": taux,
        "clauses": lignes,
        "manquantes": manquantes,
        "combien_manquent": len(manquantes),
        "verrous": verrous,
        "clauses_types": dict(CLAUSES_TYPES),
        "sous_traitance": {
            "quand": "Si la sous-traitance d'un service soutenant une "
                     "fonction critique est autorisée, le règlement délégué "
                     "(UE) 2025/532 s'applique.",
            "articles": [{"n": n, "titre": t} for n, t in SOUS_TRAITANCE],
            "source": SOURCES["sous_traitance"],
        } if critique else None,
        "sources": dict(SOURCES),
        "reserve": RESERVE,
    }


def referentiel():
    return {
        "version": VERSION,
        "sources": dict(SOURCES),
        "reserve": RESERVE,
        "clauses_communes": [{"lettre": a, "quoi": b} for a, b in CLAUSES_COMMUNES],
        "clauses_critiques": [{"lettre": a, "quoi": b} for a, b in CLAUSES_CRITIQUES],
        "derogation_micro": dict(DEROGATION_MICRO),
        "clauses_types": dict(CLAUSES_TYPES),
        "sous_traitance": [{"n": n, "titre": t} for n, t in SOUS_TRAITANCE],
        "etats": {k: dict(v) for k, v in ETATS.items()},
    }


def _verifier():
    assert len(CLAUSES_COMMUNES) == 9, \
        "l'article 30, paragraphe 2, compte neuf points, de a) à i)"
    assert [a for a, _ in CLAUSES_COMMUNES] == list("abcdefghi")
    assert len(CLAUSES_CRITIQUES) == 6, \
        "l'article 30, paragraphe 3, compte six points, de a) à f)"
    assert [a for a, _ in CLAUSES_CRITIQUES] == list("abcdef")
    assert DEROGATION_MICRO["vise"] in [a for a, _ in CLAUSES_CRITIQUES]
    assert len(SOUS_TRAITANCE) == 6, \
        "le règlement délégué 2025/532 compte sept articles, dont six de fond"
    assert len(clauses_attendues(False)) == 9
    assert len(clauses_attendues(True)) == 15
    for v in ETATS.values():
        assert 0.0 <= v["vaut"] <= 1.0


_verifier()
