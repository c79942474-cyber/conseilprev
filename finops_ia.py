# -*- coding: utf-8 -*-
"""FinOps de l'IA — le coût d'un système, lu sur un volume DÉCLARÉ.

CE QUE CE MODULE AJOUTE AU REGISTRE, ET CE QU'IL REFUSE D'INVENTER

Le registre des systèmes d'IA existe pour la conformité : il dit qui est
responsable de quoi, pour quelle finalité, dans quel service, sous quel rôle au
sens du règlement (UE) 2024/1689. C'est exactement la base d'attribution que le
FinOps réclame, et c'est la moitié la plus coûteuse de la démarche — celle qui
demande de parler à des gens. Elle est faite.

CE QUI MANQUAIT N'ÉTAIT PAS DE L'ORGANISATION, C'ÉTAIT DE LA MESURE. Le
registre nomme le FOURNISSEUR, jamais le MODÈLE ; il nomme le SERVICE, jamais
la ligne budgétaire ; et il ne porte aucun volume. Six champs comblent cela —
et aucun d'eux n'est calculé : ils sont déclarés par celui qui lit sa console
de facturation.

LA RÈGLE QUI TIENT TOUT LE MODULE

  UN VOLUME ABSENT NE VAUT PAS ZÉRO EURO.

C'est le même piège que `kpi_finance` décrit pour l'EVA : « un EVA nul faute de
revenu se lirait "ce projet ne crée pas de valeur" ; c'est faux, il se lit
"personne n'a encore dit ce qu'il rapporte" ». Ici la conséquence est pire, car
un total de zéro rassure. Un parc de vingt systèmes dont trois seulement sont
instruits afficherait un coût mensuel crédible, et le comité qui le lit
conclurait que l'IA coûte peu. C'EST LA COUVERTURE QUI DÉCIDE DE LA LECTURE DU
TOTAL, pas le total. Toute sortie de ce module la porte, et `cout_parc()` refuse
de rendre un montant sans elle.

LES TARIFS SONT DES PRIX CATALOGUE, DATÉS, ET CE N'EST PAS LA MÊME CHOSE QU'UNE
FACTURE. Un contrat entreprise, une remise au volume, un cache de contexte, un
traitement différé ou un modèle auto-hébergé donnent un coût réel différent —
souvent d'un ordre de grandeur. Le module calcule donc un ORDRE DE GRANDEUR
CATALOGUE, le dit à chaque appel, et n'a aucun moyen de connaître votre facture.
La seule façon de la connaître est de la lire.

CE QUI N'EST PAS ICI, ET POURQUOI

  · AUCUNE CONVERSION DE DEVISE. Les tarifs publics sont libellés en dollars.
    Convertir demanderait un taux, c'est-à-dire une valeur datée de plus, et un
    taux inventé ferait un montant faux d'apparence précise. Les montants
    sortent dans la devise du tarif ; la conversion est une décision, pas un
    détail d'affichage.
  · AUCUN TARIF QUE JE NE PEUX PAS SOURCER. La table ne porte que des modèles
    dont le prix catalogue est relevé, avec sa date et son émetteur. Les autres
    éditeurs ne sont pas absents par oubli : ils sont absents parce qu'inventer
    leur prix serait une invention habillée en référentiel — la faute que
    `finance_dc` refuse déjà pour le coût au mégawatt.
  · AUCUNE MESURE. Ce module ne compte aucun jeton. Il ne peut pas : il ne
    tourne pas dans vos applications.
"""
import datetime

VERSION = "2026-09-a"

# ── LES TARIFS CATALOGUE ───────────────────────────────────────────────────
# Prix PUBLIÉS, par million de jetons, dans la devise de l'éditeur. Chaque
# entrée porte sa source et la date de son relevé : un tarif sans date est une
# rumeur, et un tarif de plus d'un an décrit un marché qui a bougé.
#
# POURQUOI SI PEU DE LIGNES. Il n'y en a que ce que je peux sourcer. Ajouter un
# éditeur dont je ne tiens pas le tarif relevé donnerait une table plus large et
# moins vraie — et c'est la ligne inventée qu'on ne saurait plus distinguer des
# autres. `A_RENSEIGNER` dit ce qu'il faut y mettre.
TARIFS = {
    "claude-opus-5":    {"entree": 5.0,  "sortie": 25.0, "devise": "USD"},
    "claude-opus-4-8":  {"entree": 5.0,  "sortie": 25.0, "devise": "USD"},
    "claude-sonnet-5":  {"entree": 3.0,  "sortie": 15.0, "devise": "USD"},
    "claude-sonnet-4-6": {"entree": 3.0, "sortie": 15.0, "devise": "USD"},
    "claude-haiku-4-5": {"entree": 1.0,  "sortie": 5.0,  "devise": "USD"},
    "claude-fable-5":   {"entree": 10.0, "sortie": 50.0, "devise": "USD"},
}

TARIFS_SOURCE = ("Tarifs catalogue Anthropic, par million de jetons, "
                 "relevés le 24 juin 2026")
TARIFS_RELEVE_LE = "2026-06-24"

# Au-delà de quel âge un tarif cesse d'être un ordre de grandeur défendable.
# DOUZE MOIS N'EST PAS UN CHIFFRE ROND CHOISI POUR FAIRE JOLI : c'est l'ordre
# de grandeur observé entre deux révisions tarifaires chez les éditeurs de
# modèles, et un prix plus vieux que cela a des chances d'avoir été remplacé
# sans que personne ici l'ait vu.
TARIF_PEREMPTION_JOURS = 365

A_RENSEIGNER = {
    "tarifs_autres_editeurs":
        "Les tarifs d'OpenAI, Google, Mistral, Meta et des hébergeurs de "
        "modèles ouverts ne figurent pas dans la table : ils ne sont pas "
        "relevés ici. Les ajouter demande de reporter le prix publié, sa "
        "devise, sa date de relevé et son adresse — pas de l'estimer.",
    "taux_de_change":
        "Aucun taux n'est appliqué. Les montants sortent en dollars quand le "
        "tarif l'est. Convertir suppose un taux daté, et un taux inventé "
        "produirait un montant faux d'apparence précise.",
    "remises_et_contrats":
        "Un contrat entreprise, une remise au volume, un cache de contexte ou "
        "un traitement différé changent le coût réel, parfois d'un ordre de "
        "grandeur. Le module ne les connaît pas et ne les devine pas.",
    "coûts_hors_modèle":
        "Stockage vectoriel, orchestration, supervision, temps humain de "
        "relecture : ces postes sont réels et absents ici. Un coût de modèle "
        "n'est pas un coût de cas d'usage.",
}

# ── LES UNITÉS DE FACTURATION ──────────────────────────────────────────────
# Le jeton n'est pas la seule. Un système facturé au siège ou à l'heure de GPU
# ne se chiffre pas avec une table de prix par million de jetons, et prétendre
# le contraire donnerait un montant sans rapport. Les unités autres que le jeton
# sont donc RECONNUES et NON CHIFFRÉES : c'est une lacune déclarée, pas un zéro.
UNITES = {
    "jetons": "facturé au jeton consommé (entrée + sortie)",
    "requetes": "facturé à la requête, quel que soit sa taille",
    "heures_gpu": "facturé au temps de calcul réservé",
    "sieges": "facturé par utilisateur et par mois",
    "forfait": "montant fixe, indépendant de l'usage",
}
UNITES_CHIFFRABLES = ("jetons",)

# ── LES CLASSES DE TÂCHE, ET LE SURDIMENSIONNEMENT ────────────────────────
# « Un modèle de grande taille pour une tâche simple constitue un gaspillage
# courant. » Encore faut-il pouvoir dire qu'une tâche est simple — sans quoi le
# constat reste une maxime. La classe est DÉCLARÉE par celui qui connaît le cas
# d'usage ; le module ne la devine pas depuis la finalité, qui est du texte
# libre et dirait n'importe quoi.
CLASSES_TACHE = {
    "extraction": {
        "libelle": "Extraction ou classification sur texte court",
        "rang": 1,
        "note": "Étiquetage, tri, extraction de champs : la tâche a une "
                "réponse vérifiable et courte.",
    },
    "redaction": {
        "libelle": "Rédaction ou reformulation guidée",
        "rang": 2,
        "note": "Résumé, réécriture, réponse sur un contexte fourni.",
    },
    "analyse": {
        "libelle": "Analyse sur documents longs",
        "rang": 3,
        "note": "Synthèse multi-documents, comparaison, recherche de "
                "contradictions.",
    },
    "raisonnement": {
        "libelle": "Raisonnement long ou agentique",
        "rang": 4,
        "note": "Enchaînement d'outils, planification, code, décisions "
                "successives.",
    },
}

# Le RANG DU MODÈLE : sa place dans la gamme de son éditeur, pas sa qualité.
# Comparer un rang de modèle à un rang de tâche est une HEURISTIQUE, et elle
# est nommée comme telle partout où elle sort. Elle ne dit jamais « ce modèle
# est trop gros » : elle dit « l'écart mérite d'être regardé ».
RANG_MODELE = {
    "claude-haiku-4-5": 1,
    "claude-sonnet-4-6": 2,
    "claude-sonnet-5": 2,
    "claude-opus-4-8": 3,
    "claude-opus-5": 3,
    "claude-fable-5": 3,
}

# ── LES LEVIERS ────────────────────────────────────────────────────────────
# Déclarés, jamais mesurés : le module ne peut pas savoir si un cache est
# réellement branché. Ce qu'il apporte est la QUESTION posée à chaque ligne du
# registre — et une case non cochée sur vingt lignes se voit, là où l'absence
# de la question ne se voit pas.
LEVIERS = {
    "cache": "Les réponses répétitives sont mises en cache",
    "differe": "Les traitements non urgents partent en lot différé",
    "requete_bornee": "La taille des requêtes est bornée (contexte élagué)",
    "modele_par_etape": "Un modèle plus petit traite les étapes simples",
}


def _aujourdhui():
    return datetime.date.today()


def tarif_age_jours(aujourdhui=None):
    """L'âge du relevé tarifaire, en jours. Ce qui vieillit n'est pas le code."""
    ref = datetime.date.fromisoformat(TARIFS_RELEVE_LE)
    return ((aujourdhui or _aujourdhui()) - ref).days


def tarif_perime(aujourdhui=None):
    return tarif_age_jours(aujourdhui) > TARIF_PEREMPTION_JOURS


# ── LE COÛT D'UNE LIGNE ────────────────────────────────────────────────────

def _nombre(valeur):
    """Rend un flottant, ou None. Une chaîne vide n'est pas un zéro.

    LA NUANCE DÉCIDE DE TOUT CE MODULE. `float("") -> erreur`, mais
    `float(0) -> 0.0` : sans cette fonction, un champ laissé vide au formulaire
    et un volume réellement nul se ressembleraient au premier `try/except` venu,
    et le premier deviendrait silencieusement le second.
    """
    if valeur is None:
        return None
    if isinstance(valeur, bool):
        return None
    if isinstance(valeur, (int, float)):
        return float(valeur)
    texte = str(valeur).strip().replace(" ", "").replace(" ", "")
    texte = texte.replace(",", ".")
    if not texte:
        return None
    try:
        return float(texte)
    except ValueError:
        return None


def cout_ligne(systeme, aujourdhui=None):
    """Ce que coûte UN système par mois — ou pourquoi on ne peut pas le dire.

    Rend toujours un dictionnaire portant `instruit` (booléen) et `motif`
    (None quand instruit). JAMAIS un montant seul : un appelant qui ne lit que
    le montant doit tomber sur None, pas sur 0.

    `systeme` est une ligne du registre, telle que `/api/registre` la rend.
    """
    modele = (systeme.get("modele") or "").strip()
    unite = (systeme.get("unite_facturation") or "").strip()
    entree = _nombre(systeme.get("volume_entree_mois"))
    sortie = _nombre(systeme.get("volume_sortie_mois"))
    source = (systeme.get("volume_source") or "").strip()

    base = {
        "id": systeme.get("id"),
        "nom": systeme.get("nom"),
        "modele": modele or None,
        "unite": unite or None,
        "instruit": False,
        "montant": None,
        "devise": None,
        "motif": None,
        "source_volume": source or None,
        "tarif_source": TARIFS_SOURCE,
        "tarif_perime": tarif_perime(aujourdhui),
    }

    if not unite:
        base["motif"] = "unité de facturation non déclarée"
        return base
    if unite not in UNITES:
        base["motif"] = "unité de facturation inconnue : %s" % unite
        return base
    if unite not in UNITES_CHIFFRABLES:
        # RECONNU ET NON CHIFFRÉ. Un système facturé au siège a un coût, et ce
        # module ne sait pas le calculer. Le dire vaut mieux que de le compter
        # pour zéro dans un total qui se voudra complet.
        base["motif"] = ("facturation « %s » : réelle, mais hors de portée "
                         "d'une table de prix au jeton" % unite)
        return base
    if not modele:
        base["motif"] = "modèle non déclaré"
        return base
    if modele not in TARIFS:
        base["motif"] = ("aucun tarif relevé pour « %s » — voir "
                         "A_RENSEIGNER['tarifs_autres_editeurs']" % modele)
        return base
    if entree is None and sortie is None:
        # LE CŒUR DE LA RÈGLE. Pas de volume, pas de montant — surtout pas zéro.
        base["motif"] = "aucun volume déclaré pour ce mois"
        return base
    if not source:
        # UNE CONSOMMATION SANS PROVENANCE N'EST PAS UNE MESURE. Le chiffre peut
        # venir d'une console de facturation, d'un export, ou de la mémoire de
        # quelqu'un — et ces trois-là ne se valent pas devant un comité.
        base["motif"] = "volume déclaré sans source : d'où vient le chiffre ?"
        return base

    t = TARIFS[modele]
    entree = entree or 0.0
    sortie = sortie or 0.0
    montant = (entree / 1e6) * t["entree"] + (sortie / 1e6) * t["sortie"]
    base.update({
        "instruit": True,
        "montant": round(montant, 2),
        "devise": t["devise"],
        "volume_entree_mois": entree,
        "volume_sortie_mois": sortie,
        "formule": ("(%s jetons d'entrée / 1e6 × %s) + (%s jetons de sortie "
                    "/ 1e6 × %s) %s"
                    % (int(entree), t["entree"], int(sortie), t["sortie"],
                       t["devise"])),
    })
    return base


def dimensionnement(systeme):
    """Le modèle est-il proportionné à la tâche déclarée ? — une QUESTION.

    ELLE NE REND JAMAIS UN VERDICT. « Ce modèle est trop gros » suppose de
    connaître la qualité attendue, le taux d'erreur toléré et ce qu'une erreur
    coûte — trois choses qu'aucun registre ne porte. Ce qui est rendu est un
    ÉCART DE RANG, avec ce qu'il faudrait vérifier. Un écart de deux rangs sur
    un parc de trente systèmes désigne où regarder ; il ne décide rien.
    """
    modele = (systeme.get("modele") or "").strip()
    classe = (systeme.get("classe_tache") or "").strip()
    sortie = {"id": systeme.get("id"), "nom": systeme.get("nom"),
              "modele": modele or None, "classe_tache": classe or None,
              "instruit": False, "ecart": None, "motif": None,
              "heuristique": True}
    if not modele:
        sortie["motif"] = "modèle non déclaré"
        return sortie
    if modele not in RANG_MODELE:
        sortie["motif"] = "rang inconnu pour « %s »" % modele
        return sortie
    if classe not in CLASSES_TACHE:
        sortie["motif"] = ("classe de tâche non déclarée — elle ne se devine "
                           "pas depuis la finalité, qui est du texte libre")
        return sortie
    ecart = RANG_MODELE[modele] - CLASSES_TACHE[classe]["rang"]
    sortie.update({
        "instruit": True,
        "ecart": ecart,
        "rang_modele": RANG_MODELE[modele],
        "rang_tache": CLASSES_TACHE[classe]["rang"],
        "a_regarder": ecart >= 2,
        "note": ("le modèle est de deux rangs au-dessus de la tâche déclarée : "
                 "un modèle plus petit mérite d'être essayé, et mesuré"
                 if ecart >= 2 else
                 "le modèle est en dessous de la tâche déclarée : la qualité "
                 "est le sujet, pas le coût" if ecart < 0 else
                 "rang cohérent avec la tâche déclarée"),
    })
    return sortie


def leviers_manquants(systeme):
    """Les leviers d'optimisation NON déclarés sur cette ligne.

    Déclarés, jamais mesurés — le module ne peut pas savoir si un cache est
    réellement branché. Ce qu'il apporte est la question posée à chaque ligne :
    une case jamais cochée sur vingt lignes se voit, l'absence de la question
    ne se voit pas.
    """
    poses = systeme.get("leviers") or []
    if isinstance(poses, str):
        poses = [p.strip() for p in poses.split(",") if p.strip()]
    return sorted(set(LEVIERS) - set(poses))


# ── LE PARC ────────────────────────────────────────────────────────────────

def couverture(systemes, aujourdhui=None):
    """Combien de lignes du registre sont chiffrables, et pourquoi les autres.

    ELLE EST RENDUE AVANT LE TOTAL, ET LE TOTAL NE SORT PAS SANS ELLE. Un parc
    de vingt systèmes dont trois sont instruits produit un montant crédible et
    faux de quatre-vingt-cinq pour cent — et personne ne le voit, parce qu'un
    total ne dit pas ce qu'il ignore.
    """
    lignes = [cout_ligne(s, aujourdhui) for s in systemes]
    instruites = [l for l in lignes if l["instruit"]]
    motifs = {}
    for l in lignes:
        if not l["instruit"]:
            motifs[l["motif"]] = motifs.get(l["motif"], 0) + 1
    total = len(lignes)
    return {
        "total": total,
        "instruites": len(instruites),
        "non_instruites": total - len(instruites),
        "part_instruite": (round(len(instruites) / total, 3) if total else None),
        "motifs": dict(sorted(motifs.items(), key=lambda kv: -kv[1])),
        "lignes": lignes,
    }


def cout_parc(systemes, aujourdhui=None):
    """Le coût mensuel catalogue du parc — et ce qu'il laisse dehors.

    LE MONTANT N'EST JAMAIS RENDU SEUL. Il est accompagné de la couverture qui
    en décide la lecture, et d'un `lisible` qui vaut faux tant qu'aucune ligne
    n'est instruite : un parc entier non instruit rend `None`, jamais `0.0`.

    LES DEVISES NE SONT PAS ADDITIONNÉES ENTRE ELLES. Additionner des dollars
    et des euros pour rendre un nombre unique serait faux d'une manière que
    personne ne verrait — le total est donc rendu PAR DEVISE.
    """
    couv = couverture(systemes, aujourdhui)
    par_devise = {}
    for l in couv["lignes"]:
        if l["instruit"]:
            par_devise[l["devise"]] = round(
                par_devise.get(l["devise"], 0.0) + l["montant"], 2)
    return {
        "version": VERSION,
        "couverture": couv,
        "lisible": bool(par_devise),
        "mensuel_par_devise": par_devise or None,
        "annuel_par_devise": ({d: round(m * 12, 2) for d, m in par_devise.items()}
                              if par_devise else None),
        "tarif_source": TARIFS_SOURCE,
        "tarif_age_jours": tarif_age_jours(aujourdhui),
        "tarif_perime": tarif_perime(aujourdhui),
        "avertissement": (
            "Ordre de grandeur CATALOGUE. Un contrat entreprise, une remise au "
            "volume, un cache de contexte ou un traitement différé donnent un "
            "coût réel différent, parfois d'un ordre de grandeur. Ce montant "
            "ne remplace pas la lecture de votre facture."),
    }


def attribution(systemes, champ, aujourdhui=None):
    """Le coût réparti par service, centre de coût, modèle ou propriétaire.

    LES LIGNES NON INSTRUITES SONT COMPTÉES DANS CHAQUE GROUPE, et c'est le
    point : un service dont aucune ligne n'est chiffrée doit apparaître avec un
    montant vide et un compteur, pas disparaître du tableau. Un groupe absent se
    lit « ce service ne consomme rien » ; un groupe à zéro instruit se lit
    « personne n'a encore dit ce qu'il consomme ». La première lecture est
    fausse et rassurante.

    `champ` : 'service', 'centre_cout', 'modele', 'product_owner', 'famille'…
    """
    groupes = {}
    for s in systemes:
        cle = (s.get(champ) or "").strip() or "— non renseigné —"
        l = cout_ligne(s, aujourdhui)
        g = groupes.setdefault(cle, {
            "cle": cle, "systemes": 0, "instruites": 0,
            "mensuel_par_devise": {}, "motifs": {},
        })
        g["systemes"] += 1
        if l["instruit"]:
            g["instruites"] += 1
            g["mensuel_par_devise"][l["devise"]] = round(
                g["mensuel_par_devise"].get(l["devise"], 0.0) + l["montant"], 2)
        else:
            g["motifs"][l["motif"]] = g["motifs"].get(l["motif"], 0) + 1
    for g in groupes.values():
        g["lisible"] = bool(g["mensuel_par_devise"])
        if not g["lisible"]:
            g["mensuel_par_devise"] = None
    return {"champ": champ,
            "groupes": sorted(groupes.values(),
                              key=lambda g: (-g["systemes"], g["cle"]))}


def depassements(systemes, seuils, aujourdhui=None):
    """Quels groupes dépassent leur plafond mensuel — et lesquels ne se savent pas.

    `seuils` : {clé de groupe: {'plafond': montant, 'devise': 'USD'}}.

    DEUX SORTIES, PAS UNE. Un plafond posé sur un groupe dont aucune ligne
    n'est instruite ne peut être ni respecté ni dépassé : le déclarer « sous le
    plafond » serait un vert par ignorance. Ces groupes-là sortent dans
    `non_verifiables`, et c'est la liste qu'un comité doit lire en premier.
    """
    par_service = attribution(systemes, "centre_cout", aujourdhui)
    atteints, non_verifiables = [], []
    for g in par_service["groupes"]:
        seuil = seuils.get(g["cle"])
        if not seuil:
            continue
        devise = seuil.get("devise", "USD")
        if not g["lisible"] or devise not in (g["mensuel_par_devise"] or {}):
            non_verifiables.append({
                "cle": g["cle"], "plafond": seuil.get("plafond"),
                "devise": devise, "systemes": g["systemes"],
                "instruites": g["instruites"],
                "motif": "aucun montant instruit dans cette devise — le "
                         "plafond ne peut être ni respecté ni dépassé",
            })
            continue
        montant = g["mensuel_par_devise"][devise]
        plafond = seuil.get("plafond")
        atteints.append({
            "cle": g["cle"], "montant": montant, "plafond": plafond,
            "devise": devise,
            "part": (round(montant / plafond, 3) if plafond else None),
            "depasse": bool(plafond) and montant > plafond,
            "partiel": g["instruites"] < g["systemes"],
        })
    return {"atteints": sorted(atteints, key=lambda a: -(a["part"] or 0)),
            "non_verifiables": non_verifiables}


def etat(systemes, seuils=None, aujourdhui=None):
    """Tout ce que le panneau doit montrer, dans l'ordre où il doit le montrer.

    LA COUVERTURE VIENT EN PREMIER dans la structure comme à l'écran. Ce n'est
    pas une commodité de mise en page : c'est la seule information qui décide
    si les suivantes se lisent.
    """
    couts = cout_parc(systemes, aujourdhui)
    return {
        "version": VERSION,
        "couverture": couts["couverture"],
        "couts": couts,
        "par_service": attribution(systemes, "service", aujourdhui),
        "par_centre_cout": attribution(systemes, "centre_cout", aujourdhui),
        "par_modele": attribution(systemes, "modele", aujourdhui),
        "dimensionnement": [dimensionnement(s) for s in systemes],
        "leviers_manquants": {str(s.get("id")): leviers_manquants(s)
                              for s in systemes},
        "depassements": depassements(systemes, seuils or {}, aujourdhui),
        "a_renseigner": A_RENSEIGNER,
    }
