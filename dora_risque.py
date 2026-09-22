# -*- coding: utf-8 -*-
"""
DORA — L'ANALYSE DE RISQUE LIÉ AUX TIC, DANS LE RÉGIME QUI EST LE VÔTRE.

═══ CE QUI SE MESURE ICI ════════════════════════════════════════════════
Le règlement délégué (UE) 2024/1774 détaille ce que les articles 15 et 16
de DORA demandent. Il compte quarante-deux articles, répartis en quatre
titres, et — c'est tout le sujet — DEUX RÉGIMES QUI NE SE RECOUVRENT PAS :

  · TITRE II — vingt-six articles, cinq chapitres, pour les entités du
    cadre complet ;
  · TITRE III — quatorze articles, quatre chapitres, pour les entités du
    cadre simplifié de l'article 16, paragraphe 1, de DORA.

L'article premier (profil de risque global et complexité) est un principe
qui commande la proportionnalité ; l'article 42 est l'entrée en vigueur.
Ni l'un ni l'autre ne s'évalue : les compter parmi les exigences gonflerait
le dénominateur de deux, et ferait baisser tous les taux sans raison.

═══ LE RÉGIME COMMANDE, ET C'EST LE VERROU DU MODULE ════════════════════
Évaluer une entité du cadre simplifié contre les vingt-six articles du
titre II serait la faute la plus coûteuse possible : le client paierait un
programme dont la moitié ne le vise pas, et découvrirait au premier
contrôle qu'on lui a vendu le mauvais référentiel. Le module refuse donc
d'évaluer sans régime déclaré — il ne choisit pas « par défaut ».

═══ LE TAUX EST PAR CHAPITRE, ET LE PLUS FAIBLE SE VOIT ═════════════════
Un taux global de 80 % obtenu avec un chapitre à 20 % décrit mal la
situation : le chapitre faible est précisément celui qui se verra en
inspection. La restitution donne donc le taux par chapitre ET nomme le plus
bas, au lieu de le noyer dans une moyenne.
"""

VERSION = "2026-09-a"

SOURCE = ("Règlement délégué (UE) 2024/1774 de la Commission du 13 mars 2024 "
          "complétant le règlement (UE) 2022/2554 par des normes techniques "
          "de réglementation précisant les outils, méthodes, processus et "
          "politiques de gestion du risque lié aux TIC et le cadre simplifié "
          "de gestion du risque lié aux TIC")

LIEN = "https://eur-lex.europa.eu/eli/reg_del/2024/1774/oj"

RESERVE = (
    "Ce module mesure une déclaration, pas une conformité. Les intitulés "
    "d'articles sont ceux du texte publié au Journal officiel de l'Union ; "
    "ce que chacun exige est résumé par le cabinet et ne remplace pas la "
    "lecture de l'article. Aucune certification ne s'obtient contre ce "
    "texte : DORA est une obligation, pas un référentiel certifiable."
)

ARTICLES_1774 = (
    (1, 'Profil de risque global et complexité', 'I', None, None),
    (2, 'Éléments généraux des politiques, procédures, protocoles et outils de sécurité des TIC', 'II', 'I', 'Politiques, procédures, protocoles et outils de sécurité des TIC'),
    (3, 'Gestion du risque lié aux TIC', 'II', 'I', 'Politiques, procédures, protocoles et outils de sécurité des TIC'),
    (4, 'Politique de gestion des actifs de TIC', 'II', 'I', 'Politiques, procédures, protocoles et outils de sécurité des TIC'),
    (5, 'Procédure de gestion des actifs de TIC', 'II', 'I', 'Politiques, procédures, protocoles et outils de sécurité des TIC'),
    (6, 'Chiffrement et contrôles cryptographiques', 'II', 'I', 'Politiques, procédures, protocoles et outils de sécurité des TIC'),
    (7, 'Gestion des clés cryptographiques', 'II', 'I', 'Politiques, procédures, protocoles et outils de sécurité des TIC'),
    (8, 'Politiques et procédures pour les opérations de TIC', 'II', 'I', 'Politiques, procédures, protocoles et outils de sécurité des TIC'),
    (9, 'Gestion des capacités et des performances', 'II', 'I', 'Politiques, procédures, protocoles et outils de sécurité des TIC'),
    (10, 'Gestion des vulnérabilités et des correctifs', 'II', 'I', 'Politiques, procédures, protocoles et outils de sécurité des TIC'),
    (11, 'Sécurité des données et des systèmes', 'II', 'I', 'Politiques, procédures, protocoles et outils de sécurité des TIC'),
    (12, 'Journalisation', 'II', 'I', 'Politiques, procédures, protocoles et outils de sécurité des TIC'),
    (13, 'Gestion de la sécurité des réseaux', 'II', 'I', 'Politiques, procédures, protocoles et outils de sécurité des TIC'),
    (14, 'Sécurisation des informations en transit', 'II', 'I', 'Politiques, procédures, protocoles et outils de sécurité des TIC'),
    (15, 'Gestion des projets de TIC', 'II', 'I', 'Politiques, procédures, protocoles et outils de sécurité des TIC'),
    (16, 'Acquisition, développement et maintenance des systèmes de TIC', 'II', 'I', 'Politiques, procédures, protocoles et outils de sécurité des TIC'),
    (17, 'Gestion des changements dans les TIC', 'II', 'I', 'Politiques, procédures, protocoles et outils de sécurité des TIC'),
    (18, 'Sécurité physique et environnementale', 'II', 'I', 'Politiques, procédures, protocoles et outils de sécurité des TIC'),
    (19, 'Politique des ressources humaines', 'II', 'II', 'Politique des ressources humaines et contrôle d’accès'),
    (20, 'Gestion de l’identité', 'II', 'II', 'Politique des ressources humaines et contrôle d’accès'),
    (21, 'Contrôle d’accès', 'II', 'II', 'Politique des ressources humaines et contrôle d’accès'),
    (22, 'Politique de gestion des incidents liés aux TIC', 'II', 'III', 'Détection des incidents liés aux TIC et réponse à ces incidents'),
    (23, 'Détection des activités anormales et critères pour la détection '
     'des incidents liés aux TIC et la réponse à ces incidents', 'II', 'III', 'Détection des incidents liés aux TIC et réponse à ces incidents'),
    (24, 'Composantes de la politique de continuité des activités de TIC', 'II', 'IV', 'Gestion de la continuité des activités de TIC'),
    (25, 'Tests des plans de continuité des activités de TIC', 'II', 'IV', 'Gestion de la continuité des activités de TIC'),
    (26, 'Plans de réponse et de rétablissement des TIC', 'II', 'IV', 'Gestion de la continuité des activités de TIC'),
    (27, 'Format et contenu du rapport sur le réexamen du cadre de gestion du risque lié aux TIC', 'II', 'V', 'Rapport sur le réexamen du cadre de gestion du risque lié aux TIC'),
    (28, 'Gouvernance et organisation', 'III', 'I', 'Cadre simplifié de gestion du risque lié aux TIC'),
    (29, 'Politique et mesures en matière de sécurité de l’information', 'III', 'I', 'Cadre simplifié de gestion du risque lié aux TIC'),
    (30, 'Classification des actifs informationnels et des actifs de TIC', 'III', 'I', 'Cadre simplifié de gestion du risque lié aux TIC'),
    (31, 'Gestion du risque lié aux TIC', 'III', 'I', 'Cadre simplifié de gestion du risque lié aux TIC'),
    (32, 'Sécurité physique et environnementale', 'III', 'I', 'Cadre simplifié de gestion du risque lié aux TIC'),
    (33, 'Contrôle d’accès', 'III', 'II', 'Autres éléments des systèmes, protocoles et outils visant à réduire au minimum l’incidence du risque lié aux TIC'),
    (34, 'Sécurité des opérations de TIC', 'III', 'II', 'Autres éléments des systèmes, protocoles et outils visant à réduire au minimum l’incidence du risque lié aux TIC'),
    (35, 'Sécurité des données, des systèmes et des réseaux', 'III', 'II', 'Autres éléments des systèmes, protocoles et outils visant à réduire au minimum l’incidence du risque lié aux TIC'),
    (36, 'Tests de sécurité des TIC', 'III', 'II', 'Autres éléments des systèmes, protocoles et outils visant à réduire au minimum l’incidence du risque lié aux TIC'),
    (37, 'Acquisition, développement et maintenance des systèmes de TIC', 'III', 'II', 'Autres éléments des systèmes, protocoles et outils visant à réduire au minimum l’incidence du risque lié aux TIC'),
    (38, 'Gestion des projets de TIC et des changements dans les TIC', 'III', 'II', 'Autres éléments des systèmes, protocoles et outils visant à réduire au minimum l’incidence du risque lié aux TIC'),
    (39, 'Composantes du plan de continuité des activités de TIC', 'III', 'III', 'Gestion de la continuité des activités de TIC'),
    (40, 'Tests des plans de continuité des activités', 'III', 'III', 'Gestion de la continuité des activités de TIC'),
    (41, 'Format et contenu du rapport sur le réexamen du cadre simplifié de gestion du risque lié aux TIC', 'III', 'IV', 'Rapport sur le réexamen du cadre simplifié de gestion du risque lié aux TIC'),
    (42, 'Entrée en vigueur', 'IV', None, None),
)

# Les deux articles qui ne s'évaluent pas, et pourquoi.
HORS_EVALUATION = {
    1: "Principe de proportionnalité : il commande la lecture de tous les "
       "autres, il ne se déclare pas lui-même.",
    42: "Entrée en vigueur.",
}

REGIMES = {
    "complet": {
        "nom": "Cadre complet",
        "titre": "II",
        "renvoi": "Articles 5 à 15 du règlement (UE) 2022/2554",
        "pourquoi": "Aucune des cinq catégories de l'article 16, "
                    "paragraphe 1, n'est déclarée.",
    },
    "simplifie": {
        "nom": "Cadre simplifié",
        "titre": "III",
        "renvoi": "Article 16 du règlement (UE) 2022/2554",
        "pourquoi": "L'entité relève de l'une des cinq catégories de "
                    "l'article 16, paragraphe 1.",
    },
}

# ═══════════════════════════════════════════════════════════════════════
# LES ÉTATS DE DÉCLARATION
# ═══════════════════════════════════════════════════════════════════════
# « SANS OBJET » N'EST PAS « FAIT ». Il sort du dénominateur au lieu d'y
# entrer comme un succès — sans quoi il suffirait de tout déclarer sans
# objet pour afficher cent pour cent. Et il est PLAFONNÉ : au-delà, ce
# n'est plus une exception, c'est un périmètre mal posé.

ETATS = {
    "absent":     {"nom": "Rien en place", "note": 0.0},
    "amorce":     {"nom": "Amorcé", "note": 1.0},
    "tenu":       {"nom": "En place", "note": 2.0},
    "prouve":     {"nom": "En place et démontrable", "note": 3.0},
    "sans_objet": {"nom": "Sans objet", "note": None},
}

NOTE_MAX = 3.0
PLAFOND_SANS_OBJET = 5


def articles(regime):
    """Les articles à évaluer pour ce régime — et rien d'autre."""
    r = REGIMES.get(regime)
    if not r:
        return []
    return [a for a in ARTICLES_1774
            if a[2] == r["titre"] and a[0] not in HORS_EVALUATION]


def chapitres(regime):
    """Les chapitres du régime, dans l'ordre du texte."""
    vus, out = set(), []
    for n, titre, ti, cn, ct in articles(regime):
        if cn not in vus:
            vus.add(cn)
            out.append({"cle": cn, "nom": ct,
                        "articles": [a[0] for a in articles(regime)
                                     if a[3] == cn]})
    return out


def evaluer(regime, etats=None):
    """Le taux par chapitre, et le chapitre le plus faible nommé.

    LE MODULE REFUSE D'ÉVALUER SANS RÉGIME. Choisir « complet » par défaut
    ferait porter vingt-six articles à une entité qui n'en doit que
    quatorze ; choisir « simplifié » ferait l'inverse, et masquerait douze
    exigences. Aucune des deux erreurs n'est rattrapable par un avertissement.
    """
    if regime not in REGIMES:
        return {"ok": False, "motif": "regime_absent",
                "motif_texte": "Le régime n'est pas déclaré. Qualifiez "
                               "d'abord l'entité — le cadre complet et le "
                               "cadre simplifié ne portent pas les mêmes "
                               "articles, et il n'y a pas de défaut "
                               "raisonnable.",
                "reserve": RESERVE}

    etats = etats if isinstance(etats, dict) else {}
    liste = articles(regime)
    attendus = {a[0] for a in liste}
    intrus = sorted(k for k in etats
                    if isinstance(k, int) and k not in attendus)

    profils, sans_objet = [], 0
    for cn in [c["cle"] for c in chapitres(regime)]:
        dedans = [a for a in liste if a[3] == cn]
        somme, compte, so = 0.0, 0, 0
        details = []
        for n, titre, _, _, _ in dedans:
            e = etats.get(n)
            if e == "sans_objet":
                so += 1
                details.append({"article": n, "titre": titre,
                                "etat": "sans_objet", "note": None})
                continue
            note = ETATS[e]["note"] if e in ETATS and ETATS[e]["note"] is not None else 0.0
            # UN ARTICLE NON DÉCLARÉ COMPTE POUR ZÉRO, et reste au
            # dénominateur : le silence n'allège pas l'exigence.
            somme += note
            compte += 1
            details.append({"article": n, "titre": titre,
                            "etat": e if e in ETATS else "absent",
                            "note": note})
        sans_objet += so
        taux = round(100.0 * somme / (compte * NOTE_MAX), 1) if compte else None
        profils.append({
            "cle": cn,
            "nom": next(c["nom"] for c in chapitres(regime) if c["cle"] == cn),
            "articles": len(dedans), "evalues": compte, "sans_objet": so,
            "taux": taux, "details": details,
        })

    evalues = sum(p["evalues"] for p in profils)
    somme = sum((p["taux"] or 0) * p["evalues"] for p in profils)
    global_ = round(somme / evalues, 1) if evalues else None

    avec_taux = [p for p in profils if p["taux"] is not None]
    plus_faible = min(avec_taux, key=lambda p: p["taux"]) if avec_taux else None

    verrous = []
    if sans_objet > PLAFOND_SANS_OBJET:
        verrous.append({
            "cle": "trop_de_sans_objet",
            "dit": "%d articles sont déclarés sans objet, au-delà du plafond "
                   "de %d. Au-delà, ce n'est plus une exception : c'est un "
                   "périmètre mal posé, et le taux ne veut plus dire "
                   "grand-chose." % (sans_objet, PLAFOND_SANS_OBJET)})
    if intrus:
        verrous.append({
            "cle": "articles_hors_regime",
            "dit": "Des articles déclarés ne relèvent pas du régime %s : %s. "
                   "Ils sont ignorés — les évaluer gonflerait un taux avec "
                   "des exigences qui ne s'appliquent pas."
                   % (REGIMES[regime]["nom"].lower(),
                      ", ".join("art. %d" % i for i in intrus))})
    if plus_faible and global_ is not None and plus_faible["taux"] < global_ - 25:
        verrous.append({
            "cle": "chapitre_decroche",
            "dit": "Le chapitre « %s » est à %.1f %% quand l'ensemble est à "
                   "%.1f %%. C'est lui qui se verra en inspection, pas la "
                   "moyenne." % (plus_faible["nom"], plus_faible["taux"],
                                 global_)})

    return {
        "ok": True,
        "regime": dict(REGIMES[regime], cle=regime),
        "taux": global_,
        "articles_du_regime": len(liste),
        "evalues": evalues,
        "sans_objet": sans_objet,
        "profils": profils,
        "plus_faible": {"cle": plus_faible["cle"], "nom": plus_faible["nom"],
                        "taux": plus_faible["taux"]} if plus_faible else None,
        "verrous": verrous,
        "source": SOURCE,
        "lien": LIEN,
        "reserve": RESERVE,
    }


def ecarts(regime, etats=None):
    """Ce qui n'est pas en place, chapitre par chapitre, du plus bas au
    plus haut. LE PLAN SORT DES ÉCARTS, il ne se compose pas à côté."""
    r = evaluer(regime, etats)
    if not r.get("ok"):
        return r
    out = []
    for p in sorted(r["profils"], key=lambda x: (x["taux"] is None, x["taux"])):
        for d in p["details"]:
            if d["etat"] in ("absent", "amorce"):
                out.append({
                    "article": d["article"], "titre": d["titre"],
                    "chapitre": p["nom"], "etat": d["etat"],
                    "rang": 1 if d["etat"] == "absent" else 2,
                })
    return {"ok": True, "regime": r["regime"], "ecarts": out,
            "combien": len(out), "reserve": RESERVE}


def referentiel(regime=None):
    return {
        "version": VERSION,
        "source": SOURCE,
        "lien": LIEN,
        "reserve": RESERVE,
        "regimes": {k: dict(v) for k, v in REGIMES.items()},
        "etats": {k: dict(v) for k, v in ETATS.items()},
        "note_max": NOTE_MAX,
        "plafond_sans_objet": PLAFOND_SANS_OBJET,
        "hors_evaluation": dict(HORS_EVALUATION),
        "chapitres": {k: chapitres(k) for k in REGIMES},
        "articles": {k: [{"n": a[0], "titre": a[1], "chapitre": a[3]}
                         for a in articles(k)] for k in REGIMES},
    }


def _verifier():
    assert len(ARTICLES_1774) == 42, \
        "le règlement délégué 2024/1774 compte quarante-deux articles"
    numeros = [a[0] for a in ARTICLES_1774]
    assert numeros == list(range(1, 43)), "les numéros ne se suivent pas"
    for a in ARTICLES_1774:
        assert a[1].strip(), "l'article %d n'a pas d'intitulé" % a[0]

    complet, simplifie = articles("complet"), articles("simplifie")
    assert len(complet) == 26, len(complet)
    assert len(simplifie) == 14, len(simplifie)
    assert len(complet) + len(simplifie) + len(HORS_EVALUATION) == 42

    # LES DEUX RÉGIMES NE SE RECOUVRENT PAS. S'ils partageaient un article,
    # le total ci-dessus tiendrait quand même — et le partage passerait.
    assert not ({a[0] for a in complet} & {a[0] for a in simplifie})

    assert [c["cle"] for c in chapitres("complet")] == ["I", "II", "III", "IV", "V"]
    assert [c["cle"] for c in chapitres("simplifie")] == ["I", "II", "III", "IV"]
    for regime in REGIMES:
        for c in chapitres(regime):
            assert c["nom"].strip(), (regime, c["cle"])
            assert c["articles"], (regime, c["cle"])

    assert ETATS["sans_objet"]["note"] is None, \
        "« sans objet » ne porte pas de note : il sort du dénominateur"
    assert max(v["note"] for v in ETATS.values()
               if v["note"] is not None) == NOTE_MAX


_verifier()
