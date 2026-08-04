# -*- coding: utf-8 -*-
"""L'étude de faisabilité chiffrée, et l'avis qu'elle permet.

Le chiffrage existait déjà : finance_dc produit l'enveloppe, la décomposition
par lot, l'exploitation, le coût complet, le calendrier et les repères de
conformité. Ce qui manquait, c'est la SYNTHÈSE — et c'est elle qu'on demande à
un ingénieur en début de projet. Un dossier qui aligne des chiffres sans
conclure laisse l'investisseur conclure seul, avec les mêmes chiffres et moins
de méthode.

Ce module produit donc un avis. Trois règles le gouvernent, et elles comptent
plus que le verdict lui-même :

  · L'AVIS DIT SUR QUOI IL REPOSE. Chaque constat porte son fondement — d'où
    vient le chiffre, quelle est sa nature. Un avis dont on ne peut pas
    remonter la chaîne ne se défend pas en comité d'investissement.

  · L'AVIS DIT CE QUI LE RENVERSERAIT. Pour chaque constat, la donnée qui
    changerait la conclusion. C'est la partie utile : elle transforme un
    verdict en plan de travail.

  · L'AVIS NE DIT JAMAIS « INVESTISSEZ ». À ce stade, l'enveloppe est de
    classe 5 — moins cinquante, plus cent pour cent — et un tiers de son
    montant repose sur des postes que le référentiel ne sait pas chiffrer.
    Le plafond honnête d'une faisabilité, c'est « engager les études
    suivantes », jamais « engager les fonds. »
"""

import finance_dc as F

VERSION = "2026-08-a"

# Le plafond de ce que la phase autorise à dire. Écrit ici pour être affiché
# tel quel : un avis de faisabilité présenté comme une décision d'investissement
# est la faute la plus coûteuse de tout l'exercice.
PLAFOND = (
    "Une faisabilité n'autorise pas une décision d'investissement. Elle autorise "
    "— ou non — l'engagement des études suivantes. L'enveloppe est ici de classe 5 "
    "au sens de l'AACE : la fourchette réelle va de la moitié au double. Aucun "
    "avis de ce module ne dira « investissez ».")

ETATS = {
    "favorable": {"nom": "Favorable", "poids": 0,
                  "aide": "Rien dans ce qui est chiffré ne s'y oppose."},
    "vigilance": {"nom": "Vigilance", "poids": 1,
                  "aide": "Praticable, mais sous une condition qui doit être levée."},
    "indetermine": {"nom": "Indéterminé", "poids": 2,
                    "aide": "La donnée manque : ce point ne peut ni passer ni bloquer."},
    "bloquant": {"nom": "Bloquant", "poids": 3,
                 "aide": "En l'état, ce point interdit d'engager la suite."},
}

# Part de l'enveloppe non chiffrable au-delà de laquelle l'estimation ne peut
# plus soutenir une décision, si prudente soit-elle. Le seuil est un CHOIX : il
# est nommé, exporté et affiché, pour qu'on puisse le contester.
SEUIL_NON_CHIFFRE = 0.25
SEUIL_NOTE = (
    "Au-delà d'un quart de l'enveloppe reposant sur des postes que le référentiel "
    "ne chiffre pas, l'estimation ne soutient plus une décision : elle soutient "
    "une consultation. Ce seuil est un choix de méthode, pas une règle de l'art ; "
    "il est affiché pour pouvoir être discuté.")


def _pct(x, n=1):
    return round(float(x) * 100.0, n)


def _mi(v):
    """Le milieu d'une fourchette. Sert à comparer, jamais à afficher seul :
    une fourchette réduite à son milieu perd exactement ce qui la rend honnête."""
    if isinstance(v, (list, tuple)) and len(v) >= 2:
        return (float(v[0]) + float(v[1])) / 2.0
    return float(v or 0)


def _plage(v, n=0):
    """Affiche une fourchette COMME une fourchette. Passée telle quelle à un
    formateur de nombre, elle sortait en liste Python — « [36, 66] mois » dans
    un avis d'investissement."""
    def un(x):
        # À zéro décimale, on veut un ENTIER : « 0,0 à 6,0 mois » dans un avis
        # d'investissement donne une précision que le référentiel n'a pas.
        return F._fr(int(round(float(x)))) if n == 0 else F._fr(F._f(x, n))
    if isinstance(v, (list, tuple)) and len(v) >= 2:
        if abs(float(v[0]) - float(v[1])) < 1e-9:
            return un(v[0])
        return "%s à %s" % (un(v[0]), un(v[1]))
    return un(v)


def _pluriel(n, mot, suffixe="s"):
    return "%d %s%s" % (n, mot, suffixe if n > 1 else "")


# ═══════════════════════════════════════════════════════════════════════════
#  LES CONSTATS
# ═══════════════════════════════════════════════════════════════════════════

def _constat(sujet, etat, constat, fondement, renverse_si=""):
    return {"sujet": sujet, "etat": etat, "etat_nom": ETATS[etat]["nom"],
            "constat": constat, "fondement": fondement, "renverse_si": renverse_si}


def _part_non_chiffree(devis):
    """La part de l'enveloppe portée par des lots que le référentiel ne chiffre
    pas. C'est le chiffre qui décide si l'enveloppe peut soutenir un avis.

    On lit `part`, que finance_dc publie déjà en POURCENTAGE et APRÈS
    application des coefficients — et non `part_brute`, qui est la fourchette
    de la table avant modulation. Le premier jet sommait `part` comme s'il
    s'agissait d'une fraction, puis multipliait par cent : l'avis annonçait
    3 270 % d'enveloppe non chiffrée. Une unité supposée au lieu d'être lue.
    """
    lots = devis.get("lots") or []
    tot_pct = 0.0
    concernes = []
    for l in lots:
        if not l.get("arenseigner"):
            continue
        p = float(l.get("part") or 0.0)     # déjà en %
        tot_pct += p
        concernes.append({"code": l.get("code"), "nom": l.get("nom"),
                          "part_pct": round(p, 1),
                          "meur": l.get("meur"),
                          "question": l.get("question") or ""})
    return tot_pct / 100.0, concernes


def _avis_budget(devis, budget_meur):
    env = devis.get("enveloppe_meur") or [0, 0]
    if not budget_meur:
        return _constat(
            "Tenue dans le budget", "indetermine",
            "Aucun budget n'a été communiqué : l'avis ne peut rien dire du "
            "financement. L'enveloppe estimée va de %s à %s M€."
            % (F._fr(F._f(env[0], 1)), F._fr(F._f(env[1], 1))),
            "Enveloppe produite par finance_dc à partir du coût au mégawatt publié.",
            "Communiquer l'enveloppe budgétaire visée.")
    b = float(budget_meur)
    if env[1] <= b:
        return _constat(
            "Tenue dans le budget", "favorable",
            "L'enveloppe tient dans le budget sur TOUTE sa fourchette : au plus "
            "%s M€ contre %s M€ disponibles."
            % (F._fr(F._f(env[1], 1)), F._fr(F._f(b, 1))),
            "Comparaison de la borne HAUTE au budget — la seule qui engage.",
            "Une révision du coût au mégawatt, ou l'ajout de postes aujourd'hui "
            "non chiffrés.")
    if env[0] > b:
        return _constat(
            "Tenue dans le budget", "bloquant",
            "L'enveloppe dépasse le budget dès sa borne BASSE : au moins %s M€ "
            "contre %s M€ disponibles. Aucune hypothèse favorable ne le rattrape."
            % (F._fr(F._f(env[0], 1)), F._fr(F._f(b, 1))),
            "Comparaison de la borne BASSE au budget.",
            "Réduire la puissance visée, changer de gabarit, ou relever le budget. "
            "Un découpage en tranches déplace le problème sans le résoudre.")
    return _constat(
        "Tenue dans le budget", "vigilance",
        "Le budget est ENCADRÉ par l'enveloppe : il tient dans l'hypothèse basse "
        "(%s M€) et pas dans la haute (%s M€). Le projet est finançable ou non "
        "selon des paramètres qui ne sont pas encore arrêtés."
        % (F._fr(F._f(env[0], 1)), F._fr(F._f(env[1], 1))),
        "Le budget tombe à l'intérieur de la fourchette d'enveloppe.",
        "Resserrer l'enveloppe en chiffrant les postes locaux — c'est le seul "
        "moyen de trancher, et il ne coûte que des devis.")


def _avis_chiffrage(devis):
    part, concernes = _part_non_chiffree(devis)
    liste = ", ".join("%s (%s %%)" % (c["nom"], F._fr(c["part_pct"]))
                      for c in concernes) or "aucun"
    if part >= SEUIL_NON_CHIFFRE:
        return _constat(
            "Solidité du chiffrage", "vigilance",
            "%s %% de l'enveloppe repose sur des postes que le référentiel ne "
            "chiffre pas : %s. L'estimation cadre l'ordre de grandeur ; elle ne "
            "soutient pas encore un engagement." % (F._fr(_pct(part)), liste),
            "Somme des parts publiées des lots marqués « à renseigner ».",
            "Obtenir un prix de foncier, un indice local de construction et la "
            "quote-part du gestionnaire de réseau. Trois demandes, et la "
            "fourchette se resserre d'un tiers."), part, concernes
    return _constat(
        "Solidité du chiffrage", "favorable",
        "%s %% seulement de l'enveloppe repose sur des postes non chiffrés au "
        "référentiel — sous le seuil de méthode retenu (%s %%)."
        % (F._fr(_pct(part)), F._fr(_pct(SEUIL_NON_CHIFFRE))),
        "Somme des parts publiées des lots marqués « à renseigner ».",
        "L'ajout d'un poste local imprévu — fiscalité, servitude, dépollution."), part, concernes


def _avis_calendrier(traj):
    if not traj:
        return _constat("Calendrier", "indetermine",
                        "Le calendrier n'a pas pu être établi.", "—", "")
    tient = traj.get("tient_2030")
    avis = (traj.get("avis") or "").strip()
    duree = traj.get("duree_totale_mois")
    detail = ("Durée totale estimée : %s mois." % _plage(duree)) if duree else ""
    if tient is True:
        return _constat(
            "Calendrier", "favorable",
            ("La mise en service tient l'horizon retenu. " + detail).strip(),
            "Enchaînement des phases et délais de raccordement du référentiel.",
            avis or "Un allongement du délai de raccordement.")
    if tient is False:
        return _constat(
            "Calendrier", "vigilance",
            ("L'horizon retenu n'est pas tenu sur toute la fourchette. "
             + detail).strip(),
            "Enchaînement des phases et délais de raccordement du référentiel.",
            avis or "Engager le raccordement avant les études détaillées, ou "
                    "découper en tranches.")
    return _constat(
        "Calendrier", "indetermine",
        ("L'horizon n'est pas tranché par le calcul. " + detail).strip(),
        "Enchaînement des phases du référentiel.", avis)


def _avis_raccordement(devis):
    r = devis.get("raccordement") or {}
    mois = r.get("mois_sup") or [0, 0]
    sup = _mi(mois)
    sens = r.get("sens") or ""
    if sup <= 0.5:
        return _constat(
            "Raccordement électrique", "favorable",
            "Aucun surdélai de raccordement n'est constaté sur ce profil de parc "
            "— %s." % sens,
            "Référentiel de tension et de file d'attente de raccordement.",
            "L'arrivée d'un autre projet de taille comparable sur la même file.")
    # La formulation ne doit pas s'auto-contredire : dire « peu de concurrence »
    # puis « premier poste de dérive » dans la même phrase laisse le lecteur
    # choisir laquelle des deux il croit. Le constat est le SURDÉLAI ; l'état de
    # la file est le fondement, pas une atténuation.
    return _constat(
        "Raccordement électrique", "vigilance",
        "Le raccordement ajoute %s mois au calendrier. Le délai n'est pas nul, et "
        "c'est le poste qui ne se rattrape pas : aucun moyen supplémentaire ne "
        "raccourcit une file d'attente de réseau."
        % _plage(mois),
        "Référentiel de tension et de file d'attente de raccordement — %s." % sens,
        "Obtenir du gestionnaire de réseau un délai ET une quote-part OPPOSABLES. "
        "Tant qu'ils ne sont pas écrits, ce point reste ouvert.")


def _avis_conformite(conf):
    reperes = (conf or {}).get("reperes") or []
    mauvais = [r for r in reperes
               if str(r.get("verdict", "")).lower() in ("hors marché", "hors marche",
                                                        "au-dessus", "insuffisant")]
    if not reperes:
        return _constat("Conformité au marché", "indetermine",
                        "Les repères de marché n'ont pas pu être établis.", "—", "")
    if mauvais:
        return _constat(
            "Conformité au marché", "vigilance",
            "%s hors des usages du marché : %s. Un dossier qui s'en écarte doit "
            "le justifier, sinon il se fait écarter à la lecture."
            % (_pluriel(len(mauvais), "repère"),
               ", ".join(str(r.get("sujet")) for r in mauvais)),
            "Repères de marché de finance_dc, confrontés aux valeurs de conception.",
            "Revoir la conception, ou documenter la contrainte de site qui "
            "impose cet écart.")
    return _constat(
        "Conformité au marché", "favorable",
        "%s de marché %s examiné%s et tenu%s."
        % (_pluriel(len(reperes), "repère"), "sont" if len(reperes) > 1 else "est",
           "s" if len(reperes) > 1 else "", "s" if len(reperes) > 1 else ""),
        "Repères de marché de finance_dc, confrontés aux valeurs de conception.",
        "Un durcissement des attentes du marché ou de la réglementation.")


# ═══════════════════════════════════════════════════════════════════════════
#  L'AVIS D'ENSEMBLE
# ═══════════════════════════════════════════════════════════════════════════

SENS = {
    "arret": "Ne pas engager en l'état",
    "conditions": "Poursuivre sous conditions",
    "poursuivre": "Poursuivre les études",
    "incomplet": "Avis impossible en l'état",
}


def _synthese(constats, part_non_chiffree):
    """Le verdict, dérivé des constats et de rien d'autre.

    L'ordre de priorité est explicite : un bloquant l'emporte sur tout, puis
    l'indétermination sur un point structurant, puis la vigilance. Écrire la
    règle ici plutôt que de la laisser au jugement rend l'avis reproductible —
    et un avis d'investissement qui changerait d'une lecture à l'autre ne vaut
    rien.
    """
    bloquants = [c for c in constats if c["etat"] == "bloquant"]
    vigilances = [c for c in constats if c["etat"] == "vigilance"]
    indetermines = [c for c in constats if c["etat"] == "indetermine"]

    if bloquants:
        return {
            "sens": "arret", "sens_nom": SENS["arret"],
            "phrase": "Un point au moins interdit d'engager la suite en l'état : %s. "
                      "Tant qu'il n'est pas levé, les études suivantes travailleraient "
                      "sur une hypothèse déjà démentie."
                      % ", ".join(c["sujet"].lower() for c in bloquants),
            "conditions": [c["renverse_si"] for c in bloquants if c["renverse_si"]],
        }
    if vigilances:
        return {
            "sens": "conditions", "sens_nom": SENS["conditions"],
            "phrase": "Rien n'interdit d'engager les études suivantes, mais %s "
                      "%s être levé%s en parallèle et non après : %s. Les traiter "
                      "plus tard, c'est les découvrir quand la conception est figée."
                      % (_pluriel(len(vigilances), "point"),
                         "doivent" if len(vigilances) > 1 else "doit",
                         "s" if len(vigilances) > 1 else "",
                         ", ".join(c["sujet"].lower() for c in vigilances)),
            "conditions": [c["renverse_si"] for c in vigilances if c["renverse_si"]],
        }
    if indetermines:
        return {
            "sens": "incomplet", "sens_nom": SENS["incomplet"],
            "phrase": "Aucun point ne bloque, mais %s reste%s indéterminé%s faute "
                      "de donnée : %s. Un avis rendu sans eux serait un avis sur "
                      "autre chose que votre projet."
                      % (_pluriel(len(indetermines), "point"),
                         "nt" if len(indetermines) > 1 else "",
                         "s" if len(indetermines) > 1 else "",
                         ", ".join(c["sujet"].lower() for c in indetermines)),
            "conditions": [c["renverse_si"] for c in indetermines if c["renverse_si"]],
        }
    return {
        "sens": "poursuivre", "sens_nom": SENS["poursuivre"],
        "phrase": "Rien dans ce qui est chiffré ne s'oppose à l'engagement des "
                  "études suivantes. Cela ne vaut pas décision d'investissement : "
                  "l'enveloppe reste de classe 5.",
        "conditions": [],
    }


def avis(devis, budget_meur=None, exploitation=None, cout_total=None,
         trajectoire=None, conformite=None):
    """L'avis SEUL, greffé sur un chiffrage déjà produit.

    C'est la porte d'entrée pour l'application, qui a déjà calculé le devis avec
    les classes de climat et d'eau du pays, ses prix et ses perspectives. La
    faire recalculer ici produirait une SECONDE enveloppe pour le même projet —
    voisine, jamais identique — et c'est celle de l'avis qu'on retiendrait.
    """
    c_chiffrage, part, non_chiffres = _avis_chiffrage(devis)
    constats = [
        _avis_budget(devis, budget_meur),
        c_chiffrage,
        _avis_raccordement(devis),
        _avis_calendrier(trajectoire),
        _avis_conformite(conformite),
    ]
    # Le plus grave d'abord : un lecteur pressé lit la première ligne, et c'est
    # celle-là qui doit être le point dur.
    constats.sort(key=lambda c: -ETATS[c["etat"]]["poids"])
    return {
        "version": VERSION,
        "plafond": PLAFOND,
        "constats": constats,
        "non_chiffre": {"part_pct": _pct(part), "seuil_pct": _pct(SEUIL_NON_CHIFFRE),
                        "note": SEUIL_NOTE, "postes": non_chiffres},
        "avis": _synthese(constats, part),
        "etats": ETATS,
        "budget_meur": budget_meur,
        "moteur": F.VERSION,
    }


def etude(mw, pays=None, budget_meur=None, gabarit="hyperscale", scenario="neuve",
          climat_classe=None, eau_classe=None, densite_ia=False,
          parc_sites=0, pipeline_sites=0, cout_mw=None, vitesse="aucune",
          refroidissement=None, classe_ashrae=None, pue_impose=None,
          prix_mwh=None, annees=10):
    """L'étude de faisabilité chiffrée, avec son avis.

    Aucun chiffre n'est produit ici : tout vient de finance_dc. Ce module
    ASSEMBLE et CONCLUT. Recalculer une enveloppe au passage ferait exister deux
    montants pour le même projet, et c'est celui de l'avis qu'on retiendrait.
    """
    mw = max(0.1, float(mw or 0))
    devis = F.dpgf(mw, gabarit=gabarit, scenario=scenario, pays=pays,
                   climat_classe=climat_classe, eau_classe=eau_classe,
                   densite_ia=densite_ia, parc_sites=parc_sites,
                   pipeline_sites=pipeline_sites, cout_mw=cout_mw,
                   vitesse=vitesse, refroidissement=refroidissement,
                   classe_ashrae=classe_ashrae, pue_impose=pue_impose)

    pue = (devis.get("refroidissement") or {}).get("pue") or [1.2, 1.45]
    prix = prix_mwh if isinstance(prix_mwh, (list, tuple)) else None
    expl = tco = conf = traj = None
    if prix:
        try:
            expl = F.exploitation(devis["enveloppe_meur"], mw, pue, list(prix))
            tco = F.tco(devis["enveloppe_meur"], expl["total_meur_an"], annees)
        except Exception:
            expl = tco = None
    try:
        traj = F.trajectoire(devis)
    except Exception:
        traj = None
    try:
        conf = F.conformite_marche(pue, climat_classe=climat_classe)
    except Exception:
        conf = None

    # Une seule implémentation de l'avis : celle de avis(). Dupliquer la liste
    # des constats ici ferait exister deux jugements pour le même dossier.
    out = avis(devis, budget_meur=budget_meur, exploitation=expl,
               cout_total=tco, trajectoire=traj, conformite=conf)
    out.update({
        "entree": {"mw": mw, "pays": pays, "budget_meur": budget_meur,
                   "gabarit": gabarit, "scenario": scenario, "annees": annees},
        "devis": devis,
        "exploitation": expl,
        "tco": tco,
        "trajectoire": traj,
        "conformite": conf,
    })
    return out


def sante():
    """Auto-contrôle. Le point qui compte : l'avis doit être REPRODUCTIBLE et
    doit se DURCIR quand les conditions se dégradent. Un avis qui resterait
    favorable avec un budget insuffisant ne vaudrait rien."""
    a = etude(20, pays="FR", climat_classe="tempere", eau_classe="moyenne")
    b = etude(20, pays="FR", climat_classe="tempere", eau_classe="moyenne")
    petit = etude(20, pays="FR", budget_meur=10, climat_classe="tempere",
                  eau_classe="moyenne")
    large = etude(20, pays="FR", budget_meur=10000, climat_classe="tempere",
                  eau_classe="moyenne")
    return {
        "version": VERSION,
        "reproductible": a["avis"]["sens"] == b["avis"]["sens"]
                         and [c["etat"] for c in a["constats"]]
                             == [c["etat"] for c in b["constats"]],
        "sens_sans_budget": a["avis"]["sens"],
        "sens_budget_insuffisant": petit["avis"]["sens"],
        "sens_budget_large": large["avis"]["sens"],
        "budget_insuffisant_bloque": petit["avis"]["sens"] == "arret",
        "part_non_chiffree_pct": a["non_chiffre"]["part_pct"],
        "constats": len(a["constats"]),
        "aucun_avis_investir": "investissez" not in a["avis"]["phrase"].lower(),
        "moteur": F.VERSION,
    }
