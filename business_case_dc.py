# -*- coding: utf-8 -*-
"""Le business case : la demande, et la capacité à gagner durablement.

CE QUI MANQUAIT, ET POURQUOI C'EST LA MOITIÉ DU DOSSIER. `finance_dc` chiffre
l'enveloppe et `faisabilite_dc` en tire un avis — mais les cinq constats de cet
avis sont TOUS du côté de l'offre : le budget tient-il, le chiffrage est-il
assez complet, le réseau suivra-t-il, le calendrier est-il réaliste, le site
sera-t-il conforme. Aucun ne demande si quelqu'un louera.

Un dossier qui répond parfaitement à « pouvons-nous le construire » sans
répondre à « quelqu'un le prendra-t-il » n'est pas un business case : c'est un
devis. Et c'est le défaut caractéristique de ce marché — on est sorti de la
logique d'expérimentation pour entrer dans celle de l'investissement encadré et
planifié, où la robustesse ÉCONOMIQUE décide autant que la robustesse technique.

CE QUE CE MODULE PRODUIT.

  · HUIT TESTS DE VIABILITÉ, dans le format exact des constats de
    `faisabilite_dc` — même échelle d'états, même exigence de fondement, même
    « ce qui le renverserait ». Ils rejoignent LA MÊME synthèse : deux verdicts
    séparés pour un seul dossier se contrediraient, et c'est le plus flatteur
    qu'on retiendrait.

  · LES PROJECTIONS, sur données déclarées : revenus, coûts, marge
    d'exploitation, et surtout le TAUX DE REMPLISSAGE AU POINT MORT — le seul
    chiffre qui dise si le projet tient sans supposer qu'il se remplit.

  · LA TRAJECTOIRE D'USAGES : la montée en charge année par année, telle
    qu'elle est DÉCLARÉE, et l'année où la marge d'exploitation devient
    positive. Une trajectoire inventée serait une prévision de vente ; celle-ci
    est une hypothèse du porteur, qu'on éprouve.

CE QU'IL NE FAIT PAS, ET C'EST LA RÈGLE QUI LE TIENT.

  · IL N'INVENTE AUCUN PRIX DE MARCHÉ. Le prix au kilowatt informatique et par
    mois varie d'un facteur trois entre un marché de gros de périphérie et une
    place financière, et il se négocie contrat par contrat. Absent, la
    projection sort « indéterminée » en NOMMANT ce qui manque. Un prix par
    défaut deviendrait le prix du dossier — et personne ne conteste un
    formulaire déjà rempli.

  · IL N'INVENTE AUCUNE DEMANDE. Le taux de pré-commercialisation est déclaré
    ou il est absent ; il n'est jamais supposé. C'est précisément la donnée sur
    laquelle un porteur optimiste se trompe, et la deviner à sa place
    reviendrait à valider son optimisme.

  · IL NE NOTE PAS LES CONCURRENTS. Il compare une capacité annoncée à une
    demande déclarée. Nommer des acteurs et juger leur solidité serait une
    opinion, pas un calcul.
"""

VERSION = "2026-09-a"

# Les états sont ceux de faisabilite_dc, DÉLIBÉRÉMENT. Une seconde échelle
# — « rouge / orange / vert » — aurait obligé à traduire, et une traduction
# entre deux échelles de risque perd toujours le même bord.
ETATS = ("favorable", "vigilance", "indetermine", "bloquant")

PLAFOND = (
    "Ce module éprouve un business case ; il n'en produit pas. Les projections "
    "reposent sur des grandeurs que le porteur DÉCLARE — prix, engagements, "
    "montée en charge —, et leur qualité est celle de ces déclarations. Un "
    "point mort calculé sur un prix optimiste est un point mort optimiste, et "
    "il aura l'air d'un calcul.")


# ═══════════════════════════════════════════════════════════════════════════
#  1. LES HYPOTHÈSES DE MODÈLE — nommées, parce qu'elles décident
# ═══════════════════════════════════════════════════════════════════════════
# CELLE QUI COMPTE LE PLUS EST LA PART FIXE DE L'ÉLECTRICITÉ. Un centre à
# moitié rempli ne consomme pas la moitié : le froid, l'onduleur et la
# distribution tournent pour le volume, pas pour la charge. C'est ce qui fait
# qu'un remplissage partiel dégrade le PUE et que le point mort n'est PAS
# proportionnel. Un modèle qui ferait varier toute l'électricité avec le
# remplissage annoncerait un point mort bien plus bas qu'il n'est — l'erreur
# la plus flatteuse et la plus coûteuse de cet exercice.

HYPOTHESES = {
    "part_fixe_electricite": {
        "nom": "Part de l'électricité qui ne dépend pas du remplissage",
        "valeur": 0.35,
        "nature": "hypothese_de_modele",
        "source": "Le froid, l'onduleur, la distribution et les auxiliaires "
                  "tournent pour le VOLUME de la salle, pas pour la charge "
                  "informatique installée. Cette part correspond à l'ordre de "
                  "grandeur de la consommation non informatique d'un site "
                  "dimensionné pour sa capacité nominale.",
        "reserve": "Elle dépend fortement du mode de refroidissement et de la "
                   "capacité à mettre des tranches à l'arrêt. Un site conçu en "
                   "modules indépendants la fait baisser — c'est précisément "
                   "l'intérêt du phasage, et le test de modularité le dit.",
    },
    "postes_fixes": {
        "nom": "Postes d'exploitation indépendants du remplissage",
        "valeur": ("maintenance", "personnel", "assurance"),
        "nature": "hypothese_de_modele",
        "source": "Maintenance, astreinte et assurances se contractent sur la "
                  "capacité installée, pas sur la capacité louée. Un site "
                  "vide se maintient et se garde.",
        "reserve": "Une exploitation externalisée à la baie déplacerait une "
                   "part du personnel vers le variable — cas minoritaire.",
    },
    "mois_par_an": {
        "nom": "Mois facturés par an",
        "valeur": 12,
        "nature": "convention",
        "source": "Le prix d'hébergement se cite au kilowatt et par mois ; "
                  "l'annualiser demande cette conversion, et l'écrire ici "
                  "évite qu'elle se fasse deux fois ou pas du tout.",
        "reserve": None,
    },
}


def _h(cle):
    return HYPOTHESES[cle]["valeur"]


# ═══════════════════════════════════════════════════════════════════════════
#  2. CE QU'IL FAUT DÉCLARER — et ce que l'absence de chaque donnée empêche
# ═══════════════════════════════════════════════════════════════════════════
# LA TABLE N'EST PAS UN FORMULAIRE : c'est la liste de ce qu'un investisseur
# demandera, avec ce que son absence INTERDIT de conclure. Un champ vide ne
# rend pas le dossier incomplet en général — il rend un test précis
# impossible, et le dire est plus utile que de réclamer « toutes les données ».

ENTREES = {
    "mw_commercialises": {
        "nom": "Puissance déjà contractée ou fermement engagée (MW)",
        "empeche": "Le test de la demande. Sans lui, on ne peut pas dire si "
                   "quelqu'un louera — seulement si l'on peut construire.",
        "ou": "Contrats signés et lettres d'intention fermes, à l'exclusion "
              "des marques d'intérêt : ce sont deux choses différentes et la "
              "confusion se paie au premier comité.",
    },
    "prix_kw_mois": {
        "nom": "Prix d'hébergement au kilowatt informatique et par mois (€)",
        "empeche": "Toute projection de revenu, donc le point mort et la "
                   "marge. C'est la donnée la plus structurante du dossier.",
        "ou": "Grille tarifaire du porteur, ou prix des contrats déjà signés "
              "sur le site ou sur un site comparable du même marché.",
    },
    "annee_mise_en_service": {
        "nom": "Année de mise en service visée",
        "empeche": "Le test du calendrier contre l'accès à l'électricité — "
                   "celui qui arrête le plus de projets.",
        "ou": "Planning d'opération du porteur.",
    },
    "annee_puissance_ferme": {
        "nom": "Année de disponibilité FERME de la puissance électrique",
        "empeche": "Le même test. « Ferme » veut dire écrit par le "
                   "gestionnaire de réseau pour un point de livraison et une "
                   "puissance donnés — pas une estimation d'agence.",
        "ou": "Convention de raccordement, ou réponse écrite du gestionnaire.",
    },
    "capacite_concurrente_mw": {
        "nom": "Capacité annoncée par d'autres sur la même zone à l'horizon "
               "du projet (MW)",
        "empeche": "Le test de concurrence. Sans lui, la demande déclarée est "
                   "confrontée à rien.",
        "ou": "Annonces publiques, permis déposés, files d'attente de "
              "raccordement quand le gestionnaire les publie.",
    },
    "demande_zone_mw": {
        "nom": "Demande attendue sur la zone à l'horizon (MW)",
        "empeche": "Le test de concurrence également : c'est le dénominateur.",
        "ou": "Étude de marché du porteur, ou trajectoire publiée par une "
              "fédération professionnelle — avec son émetteur.",
    },
    "nature_projet": {
        "nom": "Nature de l'opération : greenfield ou brownfield",
        "empeche": "Le test de viabilité propre à chaque cas : ils ne "
                   "s'éprouvent pas de la même façon et n'échouent pas aux "
                   "mêmes endroits.",
        "ou": "Le programme de l'opération.",
    },
    "tranches": {
        "nom": "Découpage en tranches d'investissement (MW par tranche)",
        "empeche": "Le test de modularité et de phasage. Sans découpage "
                   "déclaré, l'engagement est réputé d'un seul tenant.",
        "ou": "Le plan de phasage du porteur.",
    },
    "densite_cible_kw_baie": {
        "nom": "Densité cible demandée par les clients (kW par baie)",
        "empeche": "Le test d'anticipation des besoins des clients finaux.",
        "ou": "Cahier des charges des clients pressentis.",
    },
    "risques_couverts": {
        "nom": "Risques financiers couverts (liste)",
        "empeche": "Le test de gestion des risques : sans déclaration, on ne "
                   "peut pas distinguer un risque assumé d'un risque oublié.",
        "ou": "Contrats : indexation, couverture de taux, de change, clause "
              "de répercussion du prix de l'électricité.",
    },
    "trajectoire_mw": {
        "nom": "Montée en charge déclarée, année par année (MW cumulés)",
        "empeche": "La trajectoire d'usages et l'année de passage en marge "
                   "positive.",
        "ou": "Le plan de commercialisation du porteur.",
    },
}

RISQUES_CONNUS = {
    "indexation": {
        "nom": "Indexation des loyers",
        "sans": "Un contrat de dix ans non indexé perd son revenu réel à "
                "l'inflation, et le porteur le découvre au cinquième exercice.",
    },
    "electricite_repercutee": {
        "nom": "Répercussion du prix de l'électricité au client",
        "sans": "C'est le poste le plus volatil du compte d'exploitation. Non "
                "répercuté, il transforme un contrat rentable en contrat "
                "déficitaire sans qu'aucune clause n'ait changé.",
    },
    "taux": {
        "nom": "Couverture du risque de taux",
        "sans": "Une dette à taux variable sur un actif à revenu fixe est un "
                "pari de marché ajouté au projet, et il n'est pas rémunéré.",
    },
    "change": {
        "nom": "Couverture du risque de change",
        "sans": "Un équipement acheté dans une devise et un revenu perçu dans "
                "une autre : l'écart se creuse entre la commande et la "
                "livraison, c'est-à-dire pendant la construction.",
    },
    "penalites_sla": {
        "nom": "Plafonnement des pénalités de disponibilité",
        "sans": "Des pénalités non plafonnées peuvent excéder la marge du "
                "contrat qu'elles garantissent.",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
#  3. LES PROJECTIONS — sur données déclarées, jamais supposées
# ═══════════════════════════════════════════════════════════════════════════

def _mi(v):
    """Le milieu d'une fourchette, ou la valeur si c'en est une.

    Les grandeurs de finance_dc voyagent en fourchettes ; le point mort, lui,
    est un nombre. Prendre le milieu est un CHOIX, et il est dit : il donne le
    cas central, pas le cas prudent. Le résultat rend aussi les deux bornes,
    parce que c'est la borne haute des coûts qui décide en comité.
    """
    if isinstance(v, (list, tuple)):
        return (float(v[0]) + float(v[-1])) / 2.0
    return float(v or 0)


def _postes_par_cle(exploitation):
    return {p.get("cle"): p for p in (exploitation or {}).get("postes") or []}


def _cout_fixe_variable(exploitation):
    """Sépare ce qui tourne quel que soit le remplissage de ce qui suit la charge.

    C'EST LA SÉPARATION QUI DÉCIDE DU POINT MORT, et la faire de travers le
    déplace de moitié. L'électricité n'est pas entièrement variable : le froid,
    l'onduleur et la distribution tournent pour le volume de la salle. Un
    modèle qui la ferait varier tout entière annoncerait un point mort bien
    plus bas qu'il n'est — l'erreur la plus flatteuse de l'exercice.
    """
    postes = _postes_par_cle(exploitation)
    if not postes:
        return None
    fixe_bas = fixe_haut = var_bas = var_haut = 0.0
    detail = []
    for cle, p in postes.items():
        m = p.get("meur_an")
        bas, haut = (float(m[0]), float(m[-1])) if isinstance(m, (list, tuple)) \
            else (float(m or 0), float(m or 0))
        if cle == "electricite":
            pf = _h("part_fixe_electricite")
            fixe_bas += bas * pf
            fixe_haut += haut * pf
            var_bas += bas * (1 - pf)
            var_haut += haut * (1 - pf)
            detail.append({"cle": cle, "nom": p.get("nom"), "nature": "mixte",
                           "part_fixe": pf,
                           "dit": "Séparée : la part non informatique tourne "
                                  "pour le volume de la salle, pas pour la "
                                  "charge installée."})
        elif cle in _h("postes_fixes"):
            fixe_bas += bas
            fixe_haut += haut
            detail.append({"cle": cle, "nom": p.get("nom"), "nature": "fixe",
                           "part_fixe": 1.0,
                           "dit": "Contracté sur la capacité installée, pas "
                                  "sur la capacité louée."})
        else:
            # Un poste que le modèle ne sait pas classer est réputé FIXE, et
            # c'est le sens prudent : le classer variable abaisserait le point
            # mort, c'est-à-dire flatterait le dossier.
            fixe_bas += bas
            fixe_haut += haut
            detail.append({"cle": cle, "nom": p.get("nom"), "nature": "fixe_par_defaut",
                           "part_fixe": 1.0,
                           "dit": "Non classé par le modèle : réputé fixe, ce "
                                  "qui est le sens prudent — le classer "
                                  "variable abaisserait le point mort."})
    return {"fixe_meur_an": [round(fixe_bas, 2), round(fixe_haut, 2)],
            "variable_meur_an": [round(var_bas, 2), round(var_haut, 2)],
            "detail": detail}


def projections(mw, exploitation=None, prix_kw_mois=None,
                mw_commercialises=None, trajectoire_mw=None):
    """Revenus, coûts, marge et taux de remplissage au point mort.

    LE POINT MORT EST LE CHIFFRE QUI DÉCIDE. Une marge calculée à cent pour
    cent de remplissage ne dit rien : tous les projets sont rentables pleins.
    Ce qui se demande en comité, c'est à partir de quel remplissage le projet
    couvre ses coûts — et si ce taux est atteignable au vu de ce qui est déjà
    contracté.

        taux de point mort = coûts fixes / (revenu à 100 % − coûts variables à 100 %)

    RIEN N'EST DEVINÉ. Sans prix déclaré, la fonction rend « indéterminé » en
    nommant ce qui manque. Un prix par défaut deviendrait le prix du dossier.
    """
    manques = []
    if not prix_kw_mois:
        manques.append("le prix d'hébergement au kilowatt et par mois")
    if not exploitation:
        manques.append("les postes d'exploitation (ils viennent du chiffrage)")
    if manques:
        return {"ok": False, "verdict": "indetermine", "manques": manques,
                "message": "Les projections ne peuvent pas être établies : il "
                           "manque " + " et ".join(manques) + ". Aucune de ces "
                           "valeurs n'est supposée ici."}

    mw = max(0.1, float(mw or 0))
    prix = float(prix_kw_mois)
    mois = _h("mois_par_an")
    # M€/an = MW × 1000 kW × €/kW/mois × 12 mois ÷ 1 000 000
    revenu_plein = mw * 1000.0 * prix * mois / 1e6
    cv = _cout_fixe_variable(exploitation)
    fixe = _mi(cv["fixe_meur_an"])
    variable = _mi(cv["variable_meur_an"])
    marge_unitaire = revenu_plein - variable

    point_mort = (fixe / marge_unitaire) if marge_unitaire > 0 else None
    # Les deux bornes, parce que c'est la borne haute des coûts qui décide.
    pm_bornes = []
    for f, v in ((cv["fixe_meur_an"][0], cv["variable_meur_an"][0]),
                 (cv["fixe_meur_an"][1], cv["variable_meur_an"][1])):
        mu = revenu_plein - v
        pm_bornes.append(round(f / mu, 4) if mu > 0 else None)

    taux_contracte = (float(mw_commercialises) / mw) if mw_commercialises else None

    return {
        "ok": True, "verdict": "etabli",
        "mw": mw, "prix_kw_mois": prix, "mois_par_an": mois,
        "revenu_plein_meur_an": round(revenu_plein, 2),
        "couts": cv,
        "cout_total_plein_meur_an": round(fixe + variable, 2),
        "marge_pleine_meur_an": round(revenu_plein - fixe - variable, 2),
        "point_mort_taux": round(point_mort, 4) if point_mort is not None else None,
        "point_mort_bornes": pm_bornes,
        "point_mort_mw": (round(point_mort * mw, 1)
                          if point_mort is not None else None),
        "taux_contracte": round(taux_contracte, 4) if taux_contracte else None,
        "marge_de_securite": (round(taux_contracte - point_mort, 4)
                              if (taux_contracte and point_mort is not None)
                              else None),
        # L'ÉQUATION S'ÉCRIT COMME LES CARTES QUI L'ENTOURENT. Elle sortait
        # « 18.52 M€/an » deux lignes sous « 33,6 M€/an » : deux graphies du
        # même genre de nombre, sur le même écran.
        "equation": ("point mort = coûts fixes %s M€/an ÷ (revenu à 100 %% "
                     "%s M€/an − coûts variables %s M€/an)"
                     % (_nb(round(fixe, 2)), _nb(round(revenu_plein, 2)),
                        _nb(round(variable, 2)))),
        "trajectoire": _trajectoire(revenu_plein, fixe, variable, mw,
                                    trajectoire_mw),
        "reserves": [
            "LE REVENU EST CELUI DE L'HÉBERGEMENT SEUL. Les services associés "
            "— interconnexion, infogérance, mains distantes — ne sont pas "
            "comptés : ils pèsent chez certains opérateurs et pas chez "
            "d'autres, et les supposer flatterait uniformément.",
            "LE POINT MORT EST UN POINT MORT D'EXPLOITATION. Il ne couvre ni "
            "le service de la dette ni la rémunération des fonds propres : un "
            "projet à l'équilibre d'exploitation peut ne pas servir son "
            "financement.",
            "LA PART FIXE DE L'ÉLECTRICITÉ EST UNE HYPOTHÈSE DE MODÈLE (%s %%), "
            "et elle décide du résultat : la faire varier tout entière avec le "
            "remplissage abaisserait le point mort d'un tiers."
            % round(_h("part_fixe_electricite") * 100),
        ],
    }


def _trajectoire(revenu_plein, fixe, variable, mw, trajectoire_mw):
    """La montée en charge DÉCLARÉE, et l'année où la marge devient positive.

    ELLE N'EST PAS PRÉVUE ICI. Une courbe de commercialisation inventée serait
    une prévision de vente déguisée en calcul. Celle-ci est l'hypothèse du
    porteur : le module la prend telle quelle et en tire les conséquences —
    c'est ce qui permet de la contester ligne par ligne.
    """
    if not trajectoire_mw:
        return {"ok": False,
                "message": "Aucune montée en charge déclarée : l'année de "
                           "passage en marge positive ne peut pas être "
                           "établie. Elle n'est pas devinée — une courbe de "
                           "commercialisation supposée serait une prévision "
                           "de vente présentée comme un calcul."}
    lignes = []
    positif = None
    for i, cumul in enumerate(trajectoire_mw, start=1):
        c = max(0.0, min(float(cumul or 0), mw))
        taux = c / mw if mw else 0.0
        rev = revenu_plein * taux
        cout = fixe + variable * taux
        marge = rev - cout
        if marge >= 0 and positif is None:
            positif = i
        lignes.append({"annee": i, "mw_cumules": round(c, 1),
                       "taux": round(taux, 4),
                       "revenu_meur": round(rev, 2),
                       "cout_meur": round(cout, 2),
                       "marge_meur": round(marge, 2)})
    return {"ok": True, "lignes": lignes, "annee_marge_positive": positif,
            "message": (None if positif else
                        "La marge d'exploitation ne devient positive sur "
                        "AUCUNE des années déclarées. Ce n'est pas "
                        "nécessairement rédhibitoire — un actif peut se "
                        "construire sur une trajectoire plus longue —, mais "
                        "la trajectoire déclarée ne le montre pas.")}


# ═══════════════════════════════════════════════════════════════════════════
#  4. LES HUIT TESTS DE VIABILITÉ
# ═══════════════════════════════════════════════════════════════════════════
# LE FORMAT EST CELUI DE `faisabilite_dc`, ET C'EST DÉLIBÉRÉ. Ces constats
# rejoignent la MÊME synthèse que ceux du chiffrage : un dossier n'a qu'un
# verdict. Deux avis séparés — l'un technique, l'autre économique — se
# contrediraient tôt ou tard, et c'est le plus flatteur qu'on présenterait.
#
# CHAQUE TEST PORTE SON FONDEMENT ET CE QUI LE RENVERSERAIT. Le second est le
# plus utile : il transforme un verdict en plan de travail. Un test qui dirait
# « insuffisant » sans dire quelle donnée le changerait n'apprend rien.

def _constat(sujet, etat, constat, fondement, renverse_si=""):
    """Le format exact des constats de faisabilite_dc.

    IL EST RECOPIÉ ICI PLUTÔT QU'IMPORTÉ, et c'est le seul sens possible :
    `faisabilite_dc` importe CE module pour lui demander ses constats.
    L'importer en retour ferait un cycle. Le format tient en cinq clés, et une
    règle vérifie qu'il ne diverge pas.
    """
    assert etat in ETATS, etat
    return {"sujet": sujet, "etat": etat, "constat": constat,
            "fondement": fondement, "renverse_si": renverse_si}


def _pct(x):
    return ("%.0f" % (float(x) * 100)).replace(".", ",")


def _test_demande(mw, mw_commercialises, proj):
    """La demande existe-t-elle ? — confrontée au POINT MORT, pas à une norme.

    C'est ce qui rend le test utile : « 45 % de pré-commercialisation » ne veut
    rien dire dans l'absolu. Le même taux est confortable sur un site dont le
    point mort est à 30 % et insuffisant sur un site dont il est à 61 %.
    """
    if mw_commercialises is None:
        return _constat(
            "Existence de la demande", "indetermine",
            "Aucune puissance contractée n'est déclarée. Le dossier dit qu'on "
            "peut construire ; il ne dit pas que quelqu'un louera.",
            "Champ « puissance déjà contractée ou fermement engagée » non "
            "renseigné.",
            "Déclarer les MW sous contrat signé ou lettre d'intention ferme — "
            "à l'exclusion des marques d'intérêt, qui n'engagent personne.")
    taux = float(mw_commercialises) / max(0.1, float(mw))
    pm = (proj or {}).get("point_mort_taux")
    if pm is None:
        return _constat(
            "Existence de la demande", "vigilance" if taux < 0.3 else "favorable",
            "%s MW contractés sur %s, soit %s %% de la capacité. Faute de "
            "projection, ce taux n'est confronté à aucun seuil."
            % (mw_commercialises, mw, _pct(taux)),
            "Puissance contractée déclarée ; point mort non calculable sans "
            "prix d'hébergement.",
            "Renseigner le prix au kilowatt et par mois : le taux contracté "
            "prend alors son sens face au point mort.")
    if taux >= pm:
        return _constat(
            "Existence de la demande", "favorable",
            "%s %% de la capacité est contractée, pour un point mort "
            "d'exploitation à %s %% : le site couvre ses coûts sur ce qui est "
            "déjà engagé." % (_pct(taux), _pct(pm)),
            "Puissance contractée déclarée, confrontée au point mort calculé "
            "sur le prix déclaré et les postes d'exploitation du chiffrage.",
            "Une perte de contrat, ou une révision du prix à la baisse, "
            "ramènerait le taux sous le point mort.")
    manque_mw = _nb(round((pm - taux) * float(mw), 1))
    return _constat(
        "Existence de la demande", "vigilance",
        "%s %% de la capacité est contractée pour un point mort à %s %% : il "
        "manque %s MW à commercialiser pour que l'exploitation s'équilibre. "
        "Le projet repose donc sur une commercialisation à venir, et c'est "
        "elle qu'il faut éprouver, pas le chiffrage."
        % (_pct(taux), _pct(pm), manque_mw),
        "Écart entre la puissance contractée déclarée et le point mort "
        "calculé.",
        "Contractualiser %s MW de plus, ou démontrer que la trajectoire de "
        "commercialisation déclarée les apporte avant l'épuisement de la "
        "trésorerie de construction." % manque_mw)


def _test_calendrier_electrique(mise_en_service, puissance_ferme):
    """Le calendrier est-il compatible avec l'accès à l'électricité ?

    C'EST LE TEST QUI ARRÊTE LE PLUS DE PROJETS, et le seul de cette liste qui
    peut être BLOQUANT à lui seul. Un bâtiment livré avant sa puissance est un
    actif qui coûte sans produire, et le délai n'est pas rattrapable : il ne
    dépend pas du porteur.
    """
    if not mise_en_service or not puissance_ferme:
        manque = []
        if not mise_en_service:
            manque.append("l'année de mise en service visée")
        if not puissance_ferme:
            manque.append("l'année de disponibilité FERME de la puissance")
        return _constat(
            "Calendrier contre accès à l'électricité", "indetermine",
            "Le test le plus décisif du dossier ne peut pas être fait : il "
            "manque " + " et ".join(manque) + ".",
            "Champs non renseignés.",
            "Obtenir du gestionnaire de réseau une date ÉCRITE pour un point "
            "de livraison et une puissance donnés. Une estimation d'agence ne "
            "vaut pas engagement, et l'écart entre les deux se compte en "
            "années.")
    ms, pf = int(mise_en_service), int(puissance_ferme)
    if pf > ms:
        return _constat(
            "Calendrier contre accès à l'électricité", "bloquant",
            "La puissance n'est ferme qu'en %d pour une mise en service visée "
            "en %d : le bâtiment serait livré %s avant d'être alimenté. "
            "Un actif achevé et non alimenté porte tous ses coûts fixes et ne "
            "produit rien." % (pf, ms, _ans(pf - ms)),
            "Comparaison de l'année de disponibilité ferme déclarée et de "
            "l'année de mise en service visée.",
            "Décaler la mise en service sur la date ferme, obtenir une date "
            "antérieure du gestionnaire, ou prévoir une alimentation "
            "transitoire — dont le coût et le régime administratif entrent "
            "alors dans l'enveloppe.")
    if pf == ms:
        return _constat(
            "Calendrier contre accès à l'électricité", "vigilance",
            "Puissance ferme et mise en service tombent la même année (%d) : "
            "il n'y a aucune marge. Tout glissement du raccordement devient "
            "un glissement de mise en service." % ms,
            "Comparaison des deux années déclarées.",
            "Obtenir une date ferme antérieure d'au moins un an, ou inscrire "
            "au plan de trésorerie le coût d'un site achevé et non alimenté.")
    return _constat(
        "Calendrier contre accès à l'électricité", "favorable",
        "La puissance est ferme en %d pour une mise en service visée en %d : "
        "%s de marge." % (pf, ms, _ans(ms - pf)),
        "Comparaison des deux années déclarées.",
        "Un report du chantier consommerait cette marge ; un décalage de la "
        "date ferme par le gestionnaire l'annulerait.")


def _ans(n):
    n = abs(int(n))
    return "un an" if n == 1 else "%d ans" % n


def _test_besoins_clients(densite_cible, devis):
    """Les besoins des clients finaux sont-ils correctement anticipés ?

    Le test porte sur la DENSITÉ, parce que c'est elle qui décide du bâtiment
    et qu'elle a été multipliée par vingt en une génération de matériel. Un
    site chiffré pour de l'hébergement classique et commercialisé auprès de
    clients qui demandent du calcul accéléré n'est pas cher : il est hors sujet.
    """
    if not densite_cible:
        return _constat(
            "Anticipation des besoins clients", "indetermine",
            "La densité demandée par les clients n'est pas déclarée. Or c'est "
            "elle qui décide du bâtiment : refroidissement, plancher, "
            "distribution électrique.",
            "Champ « densité cible » non renseigné.",
            "Relever la densité par baie au cahier des charges des clients "
            "pressentis — et non celle du site voisin.")
    d = float(densite_cible)
    # LE DRAPEAU EST SOUS `entree`, PAS À LA RACINE DU DEVIS. Lu à la racine,
    # il valait toujours faux : ce test rendait donc « bloquant » pour TOUTE
    # densité au-dessus de trente kilowatts, y compris sur un site
    # correctement chiffré en haute densité. Un verdict permanent, sur une
    # question réelle, pour une raison sans rapport avec ce qu'il prétendait
    # mesurer. Une règle l'a attrapé ; elle reste.
    ia = bool(((devis or {}).get("entree") or {}).get("densite_ia"))
    if d >= 30 and not ia:
        return _constat(
            "Anticipation des besoins clients", "bloquant",
            "Les clients demandent %s kW par baie et l'enveloppe est chiffrée "
            "hors régime haute densité. Au-delà d'une trentaine de kilowatts, "
            "l'air ne suffit plus : ce n'est pas un supplément de coût, c'est "
            "un autre bâtiment — boucle hydraulique jusqu'à la baie, plancher "
            "repris, distribution redimensionnée." % _nb(d),
            "Densité cible déclarée, confrontée au régime retenu pour le "
            "chiffrage.",
            "Rechiffrer en régime haute densité, ou établir que les clients "
            "visés se contentent de la densité que le site offre — auquel cas "
            "c'est la cible commerciale qu'il faut corriger, pas l'enveloppe.")
    if d >= 30:
        return _constat(
            "Anticipation des besoins clients", "favorable",
            "Les clients demandent %s kW par baie et l'enveloppe est chiffrée "
            "en régime haute densité : la cible commerciale et le bâtiment "
            "parlent de la même chose." % _nb(d),
            "Densité cible déclarée, confrontée au régime retenu pour le "
            "chiffrage.",
            "Une densité demandée encore supérieure rouvrirait la question du "
            "plancher, qui est la contrainte suivante.")
    return _constat(
        "Anticipation des besoins clients", "favorable" if not ia else "vigilance",
        "Les clients demandent %s kW par baie%s." % (
            _nb(d),
            ", et l'enveloppe est chiffrée en régime haute densité : le site "
            "est équipé au-delà de ce que la cible commerciale demande, et "
            "cet écart se paie en investissement" if ia else
            ", ce que l'air sait tenir en allée confinée"),
        "Densité cible déclarée, confrontée au régime retenu pour le "
        "chiffrage.",
        "Une cible commerciale révisée vers le calcul accéléré changerait "
        "cette lecture." if not ia else
        "Une cible commerciale confirmée en haute densité justifierait le "
        "surcoût du régime retenu.")


def _nb(x):
    x = float(x)
    return ("%d" % x) if abs(x - int(x)) < 1e-9 else ("%.1f" % x).replace(".", ",")


def _test_concurrence(mw, capacite_concurrente, demande_zone):
    """La capacité annoncée sur la zone contre la demande attendue.

    LE MODULE NE NOTE AUCUN ACTEUR. Nommer des concurrents et juger leur
    solidité serait une opinion ; comparer une capacité annoncée à une demande
    déclarée est un calcul. La différence tient à ce qui est opposable.
    """
    if capacite_concurrente is None or demande_zone is None:
        manque = []
        if capacite_concurrente is None:
            manque.append("la capacité annoncée par d'autres sur la zone")
        if demande_zone is None:
            manque.append("la demande attendue sur la zone")
        return _constat(
            "Concurrence sur la zone", "indetermine",
            "La position concurrentielle ne peut pas être établie : il manque "
            + " et ".join(manque) + ".",
            "Champs non renseignés.",
            "Relever les annonces publiques, les permis déposés et, quand le "
            "gestionnaire la publie, la file d'attente de raccordement de la "
            "zone.")
    offre = float(capacite_concurrente) + float(mw)
    dem = max(0.1, float(demande_zone))
    ratio = offre / dem
    part = float(mw) / offre if offre else 0.0
    if ratio > 1.5:
        etat, dit = "vigilance", (
            "L'offre annoncée sur la zone dépasse la demande attendue de "
            "moitié : %s MW pour %s MW. Dans ce cas de figure, ce n'est plus "
            "la construction qui décide mais la capacité à gagner les "
            "contrats — et le prix est la première variable qui cède."
            % (_nb(offre), _nb(dem)))
    elif ratio > 1.0:
        etat, dit = "vigilance", (
            "L'offre annoncée (%s MW) excède la demande attendue (%s MW) : le "
            "marché de la zone est servi avant que ce projet ne livre."
            % (_nb(offre), _nb(dem)))
    else:
        etat, dit = "favorable", (
            "L'offre annoncée (%s MW) reste sous la demande attendue (%s MW) : "
            "il y a de la place pour cette capacité." % (_nb(offre), _nb(dem)))
    return _constat(
        "Concurrence sur la zone", etat,
        dit + " Ce projet représenterait %s %% de l'offre annoncée." % _pct(part),
        "Capacité concurrente et demande de zone déclarées ; l'offre totale "
        "inclut ce projet.",
        "Une annonce concurrente abandonnée, ou une demande révisée, change "
        "ce rapport. C'est la donnée du dossier qui vieillit le plus vite — "
        "elle se redate à chaque comité.")


def _test_nature_projet(nature, devis):
    """Greenfield ou brownfield : ils n'échouent pas aux mêmes endroits.

    Ce test ne juge pas lequel vaut mieux — il rappelle la question qui décide
    dans chaque cas, parce qu'un dossier brownfield instruit avec la grille du
    greenfield passe à côté de la seule chose qui compte : ce que le bâtiment
    existant peut encore accepter.
    """
    n = (nature or "").strip().lower()
    if n not in ("greenfield", "brownfield"):
        return _constat(
            "Viabilité selon la nature de l'opération", "indetermine",
            "La nature de l'opération n'est pas déclarée. Greenfield et "
            "brownfield ne s'éprouvent pas de la même façon et n'échouent pas "
            "aux mêmes endroits.",
            "Champ « nature du projet » non renseigné.",
            "Déclarer s'il s'agit de partir de zéro ou de transformer "
            "l'existant.")
    if n == "brownfield":
        return _constat(
            "Viabilité selon la nature de l'opération", "vigilance",
            "Opération de transformation d'un site existant. Ce qui décide "
            "ici n'est pas le coût des travaux mais la CAPACITÉ D'ÉVOLUTION "
            "du bâti : capacité portante des planchers, hauteur disponible, "
            "puissance déjà raccordée, possibilité d'amener une boucle "
            "hydraulique jusqu'aux baies. Aucune de ces quatre données ne "
            "figure dans une enveloppe au mégawatt.",
            "Nature déclarée ; le chiffrage au mégawatt ne porte pas ces "
            "quatre contraintes.",
            "Un diagnostic de structure et un relevé de la puissance "
            "raccordée existante : ce sont les deux pièces qui font passer un "
            "brownfield de l'hypothèse au projet.")
    return _constat(
        "Viabilité selon la nature de l'opération", "vigilance",
        "Opération partant de zéro. Ce qui décide ici est la chaîne "
        "d'obtentions — maîtrise foncière, autorisation d'urbanisme, régime "
        "administratif, raccordement —, et chacune porte un délai que le "
        "porteur ne maîtrise pas.",
        "Nature déclarée.",
        "La maîtrise foncière sécurisée et l'autorisation d'urbanisme "
        "obtenue : tant qu'elles ne le sont pas, le calendrier reste une "
        "intention.")


def _test_modularite(mw, tranches, mw_commercialises, devis):
    """Modularité et phasage : chaque tranche tient-elle debout seule ?

    LE PHASAGE N'EST PAS UN CONFORT, c'est ce qui borne la perte. Un engagement
    d'un seul tenant sur une demande non contractée expose l'intégralité de
    l'enveloppe à une commercialisation qui n'a pas encore eu lieu. Découper ne
    supprime pas le risque : il le rend refusable tranche par tranche.
    """
    env = (devis or {}).get("enveloppe_meur") or [0, 0]
    haut = float(env[-1]) if env else 0.0
    if not tranches:
        return _constat(
            "Modularité et phasage", "vigilance",
            "Aucun découpage en tranches n'est déclaré : l'engagement est "
            "réputé d'un seul tenant, soit jusqu'à %s M€ exposés à une "
            "commercialisation qui n'a pas encore eu lieu. Le phasage ne "
            "supprime pas ce risque — il le rend refusable tranche par "
            "tranche." % _nb(haut),
            "Absence de découpage déclaré ; borne haute de l'enveloppe du "
            "chiffrage.",
            "Déclarer un découpage dont la PREMIÈRE tranche est couverte par "
            "la puissance déjà contractée. C'est le seul phasage qui change "
            "quelque chose au risque.")
    t = [float(x) for x in tranches if x]
    if not t:
        return _constat(
            "Modularité et phasage", "indetermine",
            "Un découpage est annoncé mais aucune tranche n'est chiffrée en "
            "mégawatts.", "Liste de tranches vide ou illisible.",
            "Déclarer la puissance de chaque tranche.")
    premiere = t[0]
    somme = sum(t)
    ecart = abs(somme - float(mw)) / max(0.1, float(mw))
    if ecart > 0.05:
        return _constat(
            "Modularité et phasage", "vigilance",
            "Les tranches déclarées totalisent %s MW pour un projet de %s MW : "
            "le découpage ne couvre pas la capacité annoncée."
            % (_nb(somme), _nb(mw)),
            "Somme des tranches déclarées, comparée à la puissance du projet.",
            "Corriger le découpage, ou la puissance annoncée — l'écart signale "
            "que l'un des deux n'est pas à jour.")
    if mw_commercialises is not None and float(mw_commercialises) >= premiere:
        return _constat(
            "Modularité et phasage", "favorable",
            "Découpage en %d tranche(s), dont la première de %s MW est "
            "entièrement couverte par les %s MW déjà contractés. Les tranches "
            "suivantes restent refusables."
            % (len(t), _nb(premiere), _nb(mw_commercialises)),
            "Découpage déclaré, confronté à la puissance contractée déclarée.",
            "Une perte de contrat ramènerait la première tranche à découvert.")
    return _constat(
        "Modularité et phasage", "vigilance",
        "Découpage en %d tranche(s), mais la première (%s MW) n'est pas "
        "couverte par ce qui est contracté%s. Un phasage dont la première "
        "tranche est déjà spéculative ne borne rien."
        % (len(t), _nb(premiere),
           " (%s MW)" % _nb(mw_commercialises)
           if mw_commercialises is not None else " — non déclaré"),
        "Découpage déclaré, confronté à la puissance contractée.",
        "Réduire la première tranche à la puissance contractée, ou "
        "contractualiser jusqu'à la couvrir.")


def _test_risques(risques_couverts):
    """Ce qui est couvert, et surtout ce qui ne l'est pas.

    LA LISTE DES RISQUES CONNUS EST FERMÉE ET DÉCLARÉE. Un risque non listé
    n'est pas signalé — c'est la limite de ce test, et il vaut mieux la dire
    que de laisser croire à une couverture exhaustive.
    """
    # UNE LISTE VIDE ET UNE ABSENCE SONT INDISTINGUABLES EN PRATIQUE : le
    # formulaire n'envoie rien quand aucune case n'est cochée. Traiter la
    # liste vide comme une déclaration « rien n'est couvert » ferait rendre un
    # verdict sur un artefact de saisie.
    if not risques_couverts:
        return _constat(
            "Gestion des risques financiers", "indetermine",
            "Aucune déclaration de couverture. On ne peut pas distinguer un "
            "risque assumé en connaissance de cause d'un risque oublié — et "
            "c'est cette distinction que cherche un investisseur.",
            "Champ « risques couverts » non renseigné.",
            "Déclarer, parmi les cinq risques du référentiel, ceux qui sont "
            "couverts par une clause ou un contrat.")
    couverts = {r for r in risques_couverts if r in RISQUES_CONNUS}
    manquants = [k for k in RISQUES_CONNUS if k not in couverts]
    if not manquants:
        return _constat(
            "Gestion des risques financiers", "favorable",
            "Les cinq risques du référentiel sont déclarés couverts. Cette "
            "liste est FERMÉE : un risque qui n'y figure pas n'est pas "
            "signalé par ce test.",
            "Déclaration du porteur, confrontée au référentiel des risques.",
            "Une clause qui expirerait avant la fin du contrat qu'elle "
            "couvre : la durée des couvertures se vérifie séparément.")
    # LE DÉFAUT DE COUVERTURE NE BLOQUE PAS, ET C'EST UN ARBITRAGE ASSUMÉ.
    # « Bloquant » veut dire, dans ce cadre, que les études suivantes
    # travailleraient sur une hypothèse déjà démentie. Un risque non couvert
    # ne remplit pas ce critère : il se couvre par une clause, au stade où les
    # contrats s'écrivent, et il n'invalide aucune étude technique. Une
    # première version le classait bloquant quand aucun des cinq n'était
    # couvert — ce qui aurait arrêté un dossier pour un formulaire non rempli.
    return _constat(
        "Gestion des risques financiers", "vigilance",
        "%d risque(s) non couvert(s) : %s. %s"
        % (len(manquants),
           ", ".join(RISQUES_CONNUS[k]["nom"].lower() for k in manquants),
           RISQUES_CONNUS[manquants[0]]["sans"]),
        "Déclaration du porteur, confrontée au référentiel des risques.",
        "Couvrir ces risques par une clause, ou déclarer qu'ils sont assumés "
        "— un risque assumé et écrit n'est pas un risque oublié.")


def _test_robustesse(proj):
    """La robustesse économique, mesurée : la marge entre ce qui est contracté
    et le point mort.

    C'est le résumé chiffré des sept autres. Il ne remplace aucun d'eux : un
    point mort confortable sur un calendrier électrique incompatible ne vaut
    rien, et l'inverse non plus.
    """
    if not proj or not proj.get("ok"):
        return _constat(
            "Robustesse économique", "indetermine",
            "Les projections n'ont pas pu être établies : " +
            (proj or {}).get("message", "données manquantes."),
            "Projections non calculables.",
            "Renseigner le prix d'hébergement : c'est la donnée qui débloque "
            "revenu, point mort et marge d'un seul coup.")
    pm = proj.get("point_mort_taux")
    marge = proj.get("marge_de_securite")
    bornes = proj.get("point_mort_bornes") or []
    haute = bornes[-1] if bornes else None
    if pm is None:
        return _constat(
            "Robustesse économique", "bloquant",
            "Le revenu à pleine charge ne couvre pas même les coûts "
            "variables : aucun taux de remplissage n'équilibre "
            "l'exploitation.",
            "Revenu à 100 %% inférieur aux coûts variables, sur le prix "
            "déclaré.",
            "Un prix d'hébergement supérieur, ou des coûts d'exploitation "
            "revus — en l'état le modèle économique ne tient pas.")
    # UN POINT MORT CENTRAL AU-DESSUS DE LA PLEINE CHARGE N'EST PAS UNE
    # VIGILANCE, ET LE CLASSER AINSI ÉTAIT UNE FAUTE. Il veut dire qu'AUCUN
    # taux de remplissage n'équilibre l'exploitation — pas même cent pour
    # cent. Ce n'est pas un point à surveiller en parallèle des études : c'est
    # un modèle économique qui ne tient pas, et poursuivre reviendrait à
    # étudier une hypothèse déjà démentie. Relevé en navigateur sur un pays
    # à électricité chère, où le calcul rendait 146 % en « vigilance ».
    if pm > 1.0:
        return _constat(
            "Robustesse économique", "bloquant",
            "Point mort à %s %% : il faudrait remplir le site au-delà de sa "
            "capacité pour équilibrer l'exploitation. Aucun taux de "
            "commercialisation n'y suffit — c'est le modèle économique qui ne "
            "tient pas, au prix déclaré et sur ce pays." % _pct(pm),
            "Point mort calculé sur le prix déclaré et les postes "
            "d'exploitation du chiffrage, qui dépendent du pays — le prix de "
            "l'électricité en est le premier terme.",
            "Un prix d'hébergement supérieur, un pays où l'électricité coûte "
            "moins, ou un PUE contractuel plus bas : les trois agissent sur "
            "le même écart.")
    if haute is not None and haute > 1.0:
        return _constat(
            "Robustesse économique", "vigilance",
            "Point mort à %s %% dans le cas central, mais la borne HAUTE des "
            "coûts d'exploitation le porte au-delà de la pleine charge : dans "
            "ce cas de figure, le site ne s'équilibre à aucun remplissage. "
            "C'est la borne haute qui se présente en comité." % _pct(pm),
            "Point mort calculé sur les deux bornes des postes "
            "d'exploitation du chiffrage.",
            "Resserrer la fourchette des coûts d'exploitation par des devis "
            "réels, ou relever le prix d'hébergement.")
    if marge is None:
        return _constat(
            "Robustesse économique", "vigilance",
            "Point mort d'exploitation à %s %% de remplissage. Faute de "
            "puissance contractée déclarée, on ne sait pas de combien on en "
            "est loin." % _pct(pm),
            "Point mort calculé ; puissance contractée non déclarée.",
            "Déclarer la puissance contractée : c'est ce qui transforme le "
            "point mort en marge de sécurité.")
    if marge >= 0:
        return _constat(
            "Robustesse économique", "favorable",
            "Point mort à %s %%, contracté à %s %% : %s points de marge de "
            "sécurité." % (_pct(pm), _pct(proj["taux_contracte"]),
                           _pct(marge)),
            "Point mort et taux contracté, calculés sur les données "
            "déclarées.",
            "Une révision du prix à la baisse, ou une hausse des coûts "
            "d'exploitation, consomme cette marge.")
    return _constat(
        "Robustesse économique", "vigilance",
        "Point mort à %s %% pour %s %% contracté : il manque %s points de "
        "remplissage, soit %s MW, pour que l'exploitation s'équilibre."
        % (_pct(pm), _pct(proj["taux_contracte"]), _pct(abs(marge)),
           _nb(round(abs(marge) * proj["mw"], 1))),
        "Écart entre le point mort et le taux contracté.",
        "Commercialiser cet écart, ou démontrer que la trajectoire déclarée "
        "l'apporte avant l'épuisement de la trésorerie de construction.")


# ═══════════════════════════════════════════════════════════════════════════
#  5. LA PORTE D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════

def constats(mw, devis=None, exploitation=None, **entrees):
    """Les huit constats, dans le format de faisabilite_dc.

    ILS SORTENT ENSEMBLE ET DANS UN ORDRE STABLE. Un ordre qui varierait d'une
    lecture à l'autre rendrait l'avis irreproductible, et un avis
    d'investissement qui change de forme entre deux comités perd toute
    autorité — quand bien même son sens ne changerait pas.
    """
    proj = projections(
        mw, exploitation=exploitation,
        prix_kw_mois=entrees.get("prix_kw_mois"),
        mw_commercialises=entrees.get("mw_commercialises"),
        trajectoire_mw=entrees.get("trajectoire_mw"))
    return [
        _test_calendrier_electrique(entrees.get("annee_mise_en_service"),
                                    entrees.get("annee_puissance_ferme")),
        _test_demande(mw, entrees.get("mw_commercialises"), proj),
        _test_robustesse(proj),
        _test_besoins_clients(entrees.get("densite_cible_kw_baie"), devis),
        _test_concurrence(mw, entrees.get("capacite_concurrente_mw"),
                          entrees.get("demande_zone_mw")),
        _test_nature_projet(entrees.get("nature_projet"), devis),
        _test_modularite(mw, entrees.get("tranches"),
                         entrees.get("mw_commercialises"), devis),
        _test_risques(entrees.get("risques_couverts")),
    ], proj


def etude(mw, devis=None, exploitation=None, **entrees):
    """Le business case complet : ses constats, ses projections, ce qui manque.

    CE QUI MANQUE EST RENDU AVEC CE QUE SON ABSENCE EMPÊCHE. Réclamer « les
    données manquantes » sans dire ce qu'elles débloquent fait remplir les
    champs faciles ; nommer le test qu'elles rendent possible fait chercher la
    bonne donnée.
    """
    liste, proj = constats(mw, devis=devis, exploitation=exploitation, **entrees)
    manquantes = [{"cle": k, "nom": v["nom"], "empeche": v["empeche"],
                   "ou": v["ou"]}
                  for k, v in ENTREES.items() if not entrees.get(k)]
    return {
        "version": VERSION,
        "plafond": PLAFOND,
        "constats": liste,
        "projections": proj,
        "manquantes": manquantes,
        "entrees_declarees": {k: v for k, v in entrees.items()
                              if v is not None and k in ENTREES},
        "hypotheses": HYPOTHESES,
        "risques_connus": RISQUES_CONNUS,
    }


def referentiel():
    return {"version": VERSION, "entrees": ENTREES,
            "risques_connus": RISQUES_CONNUS, "hypotheses": HYPOTHESES,
            "plafond": PLAFOND}


def sante():
    """Auto-contrôle. Les deux points qui comptent : le calendrier électrique
    incompatible doit BLOQUER, et un dossier vide ne doit produire que des
    indéterminations — jamais un avis favorable par défaut."""
    vide, _ = constats(20)
    dur, _ = constats(20, annee_mise_en_service=2028, annee_puissance_ferme=2031)
    return {
        "version": VERSION,
        "constats": len(vide),
        "vide_aucun_favorable": not any(c["etat"] == "favorable" for c in vide),
        "calendrier_incompatible_bloque": any(
            c["etat"] == "bloquant" and "électricité" in c["sujet"] for c in dur),
        "tous_portent_un_fondement": all(c["fondement"] for c in vide),
        "tous_portent_un_renversement": all(c["renverse_si"] for c in vide),
    }
