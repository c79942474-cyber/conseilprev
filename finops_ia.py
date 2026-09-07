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
la ligne budgétaire ; et il ne porte aucun volume. Huit champs comblent cela —
et aucun d'eux n'est calculé : ils sont déclarés par celui qui lit sa console
de facturation. (Cette phrase annonçait SIX depuis l'origine ; le registre en a
reçu huit, `CHAMPS_FINOPS` en déclare huit, et une règle compare désormais le
nombre écrit ici à celui de la table — un compte de prose ne se vérifie pas
tout seul.)

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

CE QUE LA VERSION 2026-09-b AJOUTE, ET LE DÉFAUT QU'ELLE CORRIGE

Le module lisait sept champs du registre — à une exception près, exactement les
champs qui avaient été AJOUTÉS pour lui. Des vingt-trois autres colonnes que le
registre porte déjà pour la conformité, il ne lisait rien. Conséquence mesurée :
« aucun volume déclaré » sortait à l'identique pour un système encore en
CONCEPTION, où l'absence est normale, et pour un système EN PRODUCTION ET CLASSÉ
HAUT RISQUE, où elle est la première chose à traiter. Le compteur des lacunes
mélangeait le travail à faire et le travail qui n'existe pas.

Trois fonctions naissent de ce croisement, et aucune ne demande une saisie de
plus : `cout_par_classification` (le coût par niveau de risque, dans l'ordre du
règlement et non dans celui des effectifs), `lacunes` (à combler / attendues /
indéterminées, selon l'étape du cycle de vie) et `angles_morts` (ce qu'aucun des
deux modules ne voyait seul). `CHAMPS_LUS_AILLEURS` et `CHAMPS_FINOPS` disent, à
chaque manque, OÙ le champ se déclare — pour renvoyer au bon endroit au lieu de
redemander ce qui a déjà été donné.
"""
import datetime

VERSION = "2026-09-b"

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
        # ── CE QUE LES AUTRES ANALYSES DE SENTINEL ONT DÉJÀ ÉTABLI ────────
        # Ces quatre entrées ne demandent aucune saisie de plus : elles
        # relisent des champs que le registre porte pour la conformité. Elles
        # sont placées APRÈS les montants dans la structure, et le panneau les
        # montre AVANT — parce qu'un angle mort décide de la lecture d'un
        # total, comme la couverture décide de sa validité.
        "par_classification": cout_par_classification(systemes, aujourdhui),
        "lacunes": lacunes(systemes, aujourdhui),
        "angles_morts": angles_morts(systemes, aujourdhui),
        "champs_lus_ailleurs": CHAMPS_LUS_AILLEURS,
        "champs_finops": CHAMPS_FINOPS,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  CE QUE SENTINEL A DÉJÀ DEMANDÉ — ET QUE CE MODULE CESSE DE REDEMANDER
#
#  LE DÉFAUT QUE CE BLOC CORRIGE. Le module lisait SEPT champs du registre :
#  modèle, unité, les deux volumes, la source, le centre de coût, la classe de
#  tâche — c'est-à-dire, à une exception près, exactement les champs ajoutés
#  POUR LUI. Des vingt-trois autres colonnes que le registre porte déjà —
#  classification au sens du règlement, étape du cycle de vie, rôle, statut de
#  conformité, fournisseur — il ne lisait rien.
#
#  CE QUE CETTE CÉCITÉ COÛTAIT, CONCRÈTEMENT. Une ligne non instruite en sortait
#  identique à toutes les autres. Or « aucun volume déclaré » sur un système
#  ENCORE EN CONCEPTION est normal : il ne consomme rien, il n'y a rien à
#  déclarer. Le même motif sur un système EN PRODUCTION ET CLASSÉ HAUT RISQUE
#  est une lacune qu'un comité doit traiter en premier. Les deux sortaient dans
#  le même compteur, et le compteur ne permettait pas de les distinguer.
#
#  LE PRINCIPE. Un champ que Sentinel a déjà obtenu ne se redemande pas : il se
#  LIT. Un champ que Sentinel n'a jamais demandé se demande une fois, à l'endroit
#  où il a du sens, et le module dit lequel c'est.
# ═══════════════════════════════════════════════════════════════════════════

#: Les champs que le registre porte pour la CONFORMITÉ, et que le chiffrage lit
#: sans jamais les redemander. `panneau` est l'identifiant du panneau Sentinel
#: qui les recueille — il sert au renvoi affiché à côté de chaque manque.
CHAMPS_LUS_AILLEURS = {
    "classification": {
        "panneau": "simulateur",
        "recueilli_par": "Simulateur IA Act, puis le Registre IA",
        "apporte": "Le niveau de risque au sens du règlement (UE) 2024/1689. "
                   "Un euro dépensé sur un système haut risque ne se lit pas "
                   "comme un euro dépensé sur un système à risque minimal : le "
                   "premier porte des obligations qui ont, elles aussi, un coût.",
    },
    "cycle_vie": {
        "panneau": "registre",
        "recueilli_par": "Registre IA — étape du cycle de vie",
        "apporte": "Ce qui distingue une lacune ATTENDUE d'une lacune À "
                   "COMBLER. Un système en conception n'a pas de volume parce "
                   "qu'il ne consomme rien ; un système en production n'en a "
                   "pas parce que personne ne l'a relevé.",
    },
    "fournisseur": {
        "panneau": "registre",
        "recueilli_par": "Registre IA — fournisseur / éditeur",
        "apporte": "De quel éditeur relève la ligne. Quand le modèle n'est pas "
                   "déclaré, le fournisseur dit au moins CHEZ QUI le tarif est "
                   "à relever — et si cet éditeur figure ou non dans la table.",
    },
    "statut_conformite": {
        "panneau": "registre",
        "recueilli_par": "Registre IA — statut de conformité",
        "apporte": "Ce qui reste à faire porter au budget. Un système en cours "
                   "de mise en conformité a un coût de conformité à venir, "
                   "distinct de son coût d'usage.",
    },
    "service": {
        "panneau": "registre",
        "recueilli_par": "Registre IA — service utilisateur",
        "apporte": "La base d'attribution métier — déjà tenue pour la "
                   "conformité, et réemployée telle quelle ici.",
    },
    "product_owner": {
        "panneau": "registre",
        "recueilli_par": "Registre IA — Product Owner",
        "apporte": "À qui la question du volume doit être posée. Sans lui, "
                   "« relever la consommation » n'a pas de destinataire.",
    },
}

#: Les champs que le chiffrage a AJOUTÉS au registre, et qu'il faut donc bien
#: demander une fois. Chacun dit où il se saisit, pour que le panneau renvoie au
#: bon endroit au lieu de laisser l'utilisateur chercher.
CHAMPS_FINOPS = {
    "modele": {"panneau": "registre",
               "libelle": "Modèle employé",
               "ou": "Registre IA → fiche du système → « Modèle »"},
    "unite_facturation": {"panneau": "registre",
                          "libelle": "Unité de facturation",
                          "ou": "Registre IA → fiche du système → « Unité de facturation »"},
    "volume_entree_mois": {"panneau": "registre",
                           "libelle": "Volume d'entrée du mois",
                           "ou": "Registre IA → fiche du système → « Volume d'entrée »"},
    "volume_sortie_mois": {"panneau": "registre",
                           "libelle": "Volume de sortie du mois",
                           "ou": "Registre IA → fiche du système → « Volume de sortie »"},
    "volume_source": {"panneau": "registre",
                      "libelle": "Provenance du volume",
                      "ou": "Registre IA → fiche du système → « Source du volume »"},
    "centre_cout": {"panneau": "registre",
                    "libelle": "Centre de coût",
                    "ou": "Registre IA → fiche du système → « Centre de coût »"},
    "classe_tache": {"panneau": "registre",
                     "libelle": "Classe de tâche",
                     "ou": "Registre IA → fiche du système → « Classe de tâche »"},
    "leviers": {"panneau": "registre",
                "libelle": "Leviers d'optimisation posés",
                "ou": "Registre IA → fiche du système → « Leviers »"},
}


# ── LE VOCABULAIRE DU REGISTRE, REPRIS SANS ÊTRE RÉINVENTÉ ────────────────
# Ces valeurs sont celles du formulaire du Registre IA. Les recopier ici est un
# risque de dérive assumé et BORNÉ : `_verifier_vocabulaire()` échoue à l'import
# si une valeur inconnue traverse, et le test `test_finops_ia` compare cette
# table au formulaire servi. Une classification qu'on ne reconnaît pas n'est
# jamais rangée en silence dans « à évaluer » : elle ressort telle quelle.

CLASSIFICATION_IA_ACT = [
    {"cle": "inacceptable", "libelle": "Pratique interdite (art. 5)", "rang": 0,
     "lecture": "Le coût n'est pas le sujet : une pratique interdite se "
                "retire, elle ne s'optimise pas. Le montant est affiché parce "
                "que le taire ferait disparaître la ligne du tableau."},
    {"cle": "haut", "libelle": "Haut risque", "rang": 1,
     "lecture": "Le coût d'usage n'est qu'une part du coût réel : la gestion "
                "des risques, la documentation technique, la journalisation et "
                "l'évaluation de conformité en portent une autre, que ce "
                "module ne chiffre pas."},
    {"cle": "limite", "libelle": "Risque limité (transparence)", "rang": 2,
     "lecture": "S'y ajoute le coût du marquage et de l'information des "
                "personnes, hors du périmètre de ce module."},
    {"cle": "minimal", "libelle": "Risque minimal", "rang": 3,
     "lecture": "Le coût d'usage est ici l'essentiel du coût."},
    {"cle": "a_evaluer", "libelle": "À évaluer", "rang": 4,
     "lecture": "La classification n'est pas faite. Le montant se lit, le "
                "risque non — et c'est le second qui commande le premier."},
]

CYCLE_VIE = [
    {"cle": "conception", "libelle": "① Conception", "en_service": False},
    {"cle": "developpement", "libelle": "② Développement", "en_service": False},
    {"cle": "pre_production", "libelle": "③ Pré-production", "en_service": False},
    {"cle": "production", "libelle": "④ Production", "en_service": True},
    {"cle": "revue", "libelle": "⑤ Revue périodique", "en_service": True},
]

_CLASSIF = {c["cle"]: c for c in CLASSIFICATION_IA_ACT}
_CYCLE = {c["cle"]: c for c in CYCLE_VIE}


def _verifier_vocabulaire():
    """Le référentiel se contredit-il ? Contrôlé à l'import, comme ailleurs.

    C'est le seul moment où l'incohérence est encore gratuite : plus tard elle
    sort à l'écran, et à l'écran on la croit."""
    rangs = [c["rang"] for c in CLASSIFICATION_IA_ACT]
    if sorted(rangs) != list(range(len(CLASSIFICATION_IA_ACT))):
        raise ValueError("CLASSIFICATION_IA_ACT : les rangs doivent être une "
                         "suite 0..n sans trou ni doublon — ils décident de "
                         "l'ordre d'affichage, et un doublon rendrait cet "
                         "ordre dépendant du hasard du tri")
    if not any(c["en_service"] for c in CYCLE_VIE):
        raise ValueError("CYCLE_VIE : aucune étape n'est « en service » — "
                         "`lacunes()` ne pourrait alors qualifier aucune "
                         "lacune, et rendrait tout normal")
    for cle, p in CHAMPS_LUS_AILLEURS.items():
        if not p.get("panneau"):
            raise ValueError("CHAMPS_LUS_AILLEURS[%r] : sans panneau, le "
                             "renvoi affiché ne mène nulle part" % cle)


_verifier_vocabulaire()


def cout_par_classification(systemes, aujourdhui=None):
    """Le coût réparti par niveau de risque au sens du règlement.

    L'ORDRE N'EST PAS CELUI DES EFFECTIFS. `attribution()` trie par nombre de
    systèmes, ce qui est juste pour un service et faux ici : un unique système
    haut risque doit se lire AVANT quinze systèmes à risque minimal. Le tri suit
    donc le rang réglementaire, et un niveau absent du parc n'est pas affiché —
    inventer une ligne à zéro pour « inacceptable » suggérerait qu'on a cherché
    et trouvé zéro, alors qu'on n'a rien classé du tout.

    UNE VALEUR HORS VOCABULAIRE N'EST PAS RANGÉE DANS « À ÉVALUER ». Elle sort
    sous son propre nom, avec `connu: False` : la ranger silencieusement ferait
    disparaître une donnée abîmée dans un compteur d'apparence saine.
    """
    par = attribution(systemes, "classification", aujourdhui)
    groupes = []
    for g in par["groupes"]:
        ref = _CLASSIF.get(g["cle"])
        groupes.append(dict(
            g,
            connu=bool(ref),
            libelle=(ref["libelle"] if ref else g["cle"]),
            lecture=(ref["lecture"] if ref else
                     "Valeur absente du vocabulaire du registre : elle n'est "
                     "pas rangée d'office dans « à évaluer », parce qu'une "
                     "donnée abîmée doit rester visible."),
            rang=(ref["rang"] if ref else len(CLASSIFICATION_IA_ACT)),
        ))
    groupes.sort(key=lambda g: (g["rang"], g["cle"]))
    return {"champ": "classification", "groupes": groupes,
            "source": CHAMPS_LUS_AILLEURS["classification"]["recueilli_par"]}


def lacunes(systemes, aujourdhui=None):
    """Les lignes non chiffrées, SÉPARÉES selon qu'elles devaient l'être.

    LE PARTAGE QUE FAIT CETTE FONCTION EST TOUT SON OBJET. Sans lui, un parc de
    vingt systèmes dont douze sont encore en conception affiche « 8 lignes non
    instruites » comme un reproche — et le comité part relancer douze équipes
    qui n'ont rien à déclarer. Avec lui, il lit « 3 systèmes EN SERVICE dont
    personne n'a relevé la consommation », qui est le vrai travail.

    `a_combler` : en service (production ou revue), donc consommant réellement.
    `attendues`  : pas encore en service — l'absence de volume y est normale.
    `indeterminees` : étape du cycle de vie non déclarée. NI l'une NI l'autre :
        les compter avec les attendues rendrait le parc plus propre qu'il n'est,
        les compter avec les lacunes accuserait sans savoir.
    """
    a_combler, attendues, indeterminees = [], [], []
    for s in systemes:
        ligne = cout_ligne(s, aujourdhui)
        if ligne["instruit"]:
            continue
        etape = (s.get("cycle_vie") or "").strip()
        ref = _CYCLE.get(etape)
        classif = (s.get("classification") or "").strip()
        item = {
            "id": s.get("id"), "nom": s.get("nom"), "motif": ligne["motif"],
            "cycle_vie": etape or None,
            "cycle_vie_libelle": (ref["libelle"] if ref else None),
            "classification": classif or None,
            "classification_libelle": (_CLASSIF[classif]["libelle"]
                                       if classif in _CLASSIF else None),
            "fournisseur": (s.get("fournisseur") or "").strip() or None,
            "product_owner": (s.get("product_owner") or "").strip() or None,
        }
        if ref is None:
            item["pourquoi"] = ("étape du cycle de vie non déclarée : on ne "
                                "peut pas dire si ce système consomme déjà")
            indeterminees.append(item)
        elif ref["en_service"]:
            item["pourquoi"] = ("ce système est %s : il consomme, et personne "
                                "n'a encore dit combien" % ref["libelle"])
            a_combler.append(item)
        else:
            item["pourquoi"] = ("ce système est %s : l'absence de volume y est "
                                "normale, pas une lacune" % ref["libelle"])
            attendues.append(item)
    return {
        "a_combler": a_combler,
        "attendues": attendues,
        "indeterminees": indeterminees,
        "source_cycle_vie": CHAMPS_LUS_AILLEURS["cycle_vie"]["recueilli_par"],
    }


def angles_morts(systemes, aujourdhui=None):
    """Les croisements qu'un comité doit lire AVANT les totaux.

    CE NE SONT PAS DES ALERTES DE PLUS. Chacun naît du croisement de deux
    champs qui, pris séparément, ne disent rien : une ligne non chiffrée est
    banale, un système haut risque est banal — un système haut risque EN SERVICE
    et non chiffré ne l'est pas. C'est précisément ce que ni le registre seul,
    ni le chiffrage seul, ne pouvaient voir.

    AUCUN DE CES CONSTATS N'EST UN VERDICT. Ils désignent où regarder ; ce qu'il
    faut en conclure demande de connaître le contrat, l'usage réel et la qualité
    attendue — trois choses absentes d'ici.
    """
    lac = lacunes(systemes, aujourdhui)
    en_service = {str(x["id"]): x for x in lac["a_combler"]}

    haut_non_chiffre = [x for x in lac["a_combler"] + lac["indeterminees"]
                        if x["classification"] == "haut"]

    interdits = []
    for s in systemes:
        if (s.get("classification") or "").strip() == "inacceptable":
            l = cout_ligne(s, aujourdhui)
            interdits.append({"id": s.get("id"), "nom": s.get("nom"),
                              "montant": l["montant"], "devise": l["devise"],
                              "instruit": l["instruit"]})

    # Un fournisseur nommé mais pas de modèle : le tarif est relevable, il n'est
    # pas relevé. Le distinguer de « rien de déclaré » évite d'envoyer chercher
    # une information que quelqu'un a déjà donnée à moitié.
    fournisseur_sans_modele = []
    for s in systemes:
        f = (s.get("fournisseur") or "").strip()
        if f and not (s.get("modele") or "").strip():
            fournisseur_sans_modele.append({
                "id": s.get("id"), "nom": s.get("nom"), "fournisseur": f,
                "en_service": str(s.get("id")) in en_service,
            })

    return {
        "haut_risque_non_chiffre": {
            "lignes": haut_non_chiffre,
            "lecture": "Un système classé haut risque dont le coût n'est pas "
                       "connu est le pire des deux mondes : il porte les "
                       "obligations les plus lourdes du règlement, et son "
                       "budget n'est pas instruit. C'est la première ligne à "
                       "traiter, avant tout arbitrage de plafond.",
        },
        "pratiques_interdites": {
            "lignes": interdits,
            "lecture": "Une pratique interdite par l'article 5 ne s'optimise "
                       "pas : elle se retire. Le montant figure ici pour que "
                       "la ligne ne disparaisse pas du tableau, jamais pour "
                       "être arbitré.",
        },
        "fournisseur_sans_modele": {
            "lignes": fournisseur_sans_modele,
            "lecture": "Le fournisseur est déclaré, le modèle non : le tarif "
                       "est relevable chez un éditeur nommé. C'est la lacune "
                       "la moins coûteuse à combler du lot.",
        },
    }
