"""Le pilotage d'un investissement data centre : formes, seuils, alertes.

CE QUE CE MODULE APPORTE, ET QUI N'EST PAS DE LA MISE EN FORME
─────────────────────────────────────────────────────────────
Trois décisions y sont CALCULÉES, là où elles se prennent d'habitude à
l'habitude ou au goût :

  1. LA FORME SUIT LA DONNÉE, ET LE MODULE REFUSE CE QUI SE LIT MAL.
     Une courbe pour une évolution dans le temps, un histogramme pour une
     comparaison entre catégories, un camembert pour des parts d'un tout —
     et un REFUS motivé quand le camembert compterait plus de six parts ou
     que ses parts seraient trop proches pour se distinguer à l'œil. Refuser
     et proposer l'histogramme vaut mieux que produire une figure dont le
     lecteur tirera une conclusion fausse : sur un camembert à huit parts
     voisines, l'ordre visuel n'est plus l'ordre des valeurs.

  2. UNE ALERTE NE SE DÉCLENCHE PAS SUR DU BRUIT.
     C'est le point que ce moteur peut tenir et qu'un tableur ne tient pas :
     il connaît l'INCERTITUDE de ses grandeurs. Une enveloppe à ±30 % qui
     dépasse sa cible de 4 % n'a rien franchi — l'écart est dans le bruit.
     Alerter quand même produit un faux positif, et au troisième plus
     personne ne regarde les couleurs. Le seuil doit donc être franchi
     AU-DELÀ de l'incertitude pour que le rouge s'allume ; entre les deux,
     le module dit « sous surveillance, l'écart n'est pas démontré ».

  3. LA TENDANCE EST MESURÉE, PAS DESSINÉE.
     La flèche vient de la série — pente sur les derniers points, comparée
     au bruit de la série elle-même. Une flèche qui monte sur trois points
     dont deux se valent est une décoration ; ici elle reste plate et le dit.

CE QU'IL NE FAIT PAS. Il n'envoie pas de notification : le module calcule
QUI doit être prévenu et à QUELLE échéance, l'envoi appartient à
l'organisation. Et il ne promet pas un pilotage que la maturité analytique
ne permet pas de tenir — voir `tenable_au_niveau`.

Aucun modèle de langage n'intervient : deux pilotages aux mêmes séries
rendent le même résultat.
"""

VERSION = "2026-08-a"

# ═══════════════════════════════════════════════════════════════════════════
#  1. LA FORME SUIT LA DONNÉE
# ═══════════════════════════════════════════════════════════════════════════

FORMES = {
    "courbe": {
        "nom": "Courbe",
        "pour": "Une évolution dans le temps : chiffre d'affaires mensuel sur "
                "douze mois, progression d'un indicateur sur plusieurs "
                "trimestres.",
        "montre": "Les tendances, les ruptures et les saisonnalités se lisent "
                  "d'un coup d'œil — c'est ce qu'aucune autre forme ne donne.",
        "eviter": "Ne l'employez pas pour comparer des catégories sans ordre "
                  "naturel : relier deux divisions par un trait suggère un "
                  "passage de l'une à l'autre qui n'existe pas.",
    },
    "histogramme": {
        "nom": "Histogramme",
        "pour": "Une comparaison entre catégories ou entre périodes : quatre "
                "divisions sur quatre trimestres, coût par lot technique.",
        "montre": "La comparaison se fait sans effort : les barres partagent "
                  "une base commune, et l'œil compare des longueurs.",
        "eviter": "Au-delà d'une quinzaine de barres, la lecture se disperse "
                  "— regrouper, ou trier par valeur.",
    },
    "camembert": {
        "nom": "Camembert",
        "pour": "Des parts d'un TOUT : répartition d'une enveloppe par lot, "
                "part de marché par segment.",
        "montre": "La part de chacun dans l'ensemble, quand il y a peu de "
                  "parts et qu'elles sont franchement différentes.",
        "eviter": "Au-delà de cinq ou six parts, ou quand les parts sont "
                  "proches, l'œil ne classe plus correctement des angles "
                  "voisins — l'histogramme trié le fait sans erreur.",
    },
}

# Les deux bornes qui déclenchent le refus de camembert. Écrites ici, servies
# à l'interface et employées par le calcul : trois valeurs identiques dans
# trois fichiers auraient divergé au premier ajustement.
CAMEMBERT_PARTS_MAX = 6
# Deux parts sont « proches » quand leur écart RELATIF est sous ce seuil :
# sur un disque, une différence de moins de dix pour cent entre deux angles
# ne se voit pas — elle se lit à l'étiquette, et alors le disque ne sert plus
# à rien.
CAMEMBERT_ECART_MIN = 0.10


def choisir_forme(nature, points, valeurs=None):
    """La forme adaptée à CETTE donnée, et le refus motivé s'il y a lieu.

    `nature` : "temps" (série datée), "categories" (comparaison), "parts"
               (composantes d'un tout).
    `points`  : nombre de points ou de catégories.
    `valeurs` : les valeurs, nécessaires pour juger si un camembert se lira.
    """
    nature = str(nature or "").strip().lower()
    n = int(points or 0)
    if nature == "temps":
        if n < 3:
            return {"forme": "histogramme", "impose": True,
                    "pourquoi": "Moins de trois points ne font pas une "
                                "tendance : une courbe à deux points affiche "
                                "une droite dont la pente n'a aucun sens. "
                                "Les barres, elles, comparent honnêtement."}
        return {"forme": "courbe", "impose": False,
                "pourquoi": "Évolution dans le temps : la courbe montre la "
                            "tendance, les ruptures et la saisonnalité."}
    if nature == "parts":
        vals = [abs(float(v)) for v in (valeurs or []) if v is not None]
        if n > CAMEMBERT_PARTS_MAX:
            return {"forme": "histogramme", "impose": True,
                    "pourquoi": "%d parts : au-delà de %d, l'œil ne classe "
                                "plus des angles voisins. L'histogramme trié "
                                "donne le même classement sans erreur de "
                                "lecture." % (n, CAMEMBERT_PARTS_MAX)}
        total = sum(vals)
        if total > 0 and len(vals) > 1:
            parts = sorted((v / total for v in vals), reverse=True)
            # Deux parts voisines dans le classement dont l'écart relatif est
            # sous le seuil : sur un disque, elles seront indiscernables.
            proches = [(parts[i], parts[i + 1]) for i in range(len(parts) - 1)
                       if parts[i] > 0
                       and (parts[i] - parts[i + 1]) / parts[i] < CAMEMBERT_ECART_MIN]
            if proches:
                return {"forme": "histogramme", "impose": True,
                        "pourquoi": "Deux parts au moins sont trop proches "
                                    "(%s %% et %s %%) : sur un disque, l'ordre "
                                    "visuel cesse d'être l'ordre des valeurs. "
                                    "L'histogramme trié les sépare."
                                    % (round(proches[0][0] * 100, 1),
                                       round(proches[0][1] * 100, 1))}
        return {"forme": "camembert", "impose": False,
                "pourquoi": "Parts d'un tout, peu nombreuses et franchement "
                            "distinctes : le disque montre le poids relatif "
                            "mieux qu'un tableau."}
    return {"forme": "histogramme", "impose": False,
            "pourquoi": "Comparaison entre catégories : les barres partagent "
                        "une base commune, l'œil compare des longueurs."}


# ═══════════════════════════════════════════════════════════════════════════
#  2. LES SEUILS DÉCISIONNELS — et l'incertitude qui les tempère
# ═══════════════════════════════════════════════════════════════════════════

ETATS = {
    "conforme": {"couleur": "vert", "signe": "●",
                 "dit": "Conforme à la cible.",
                 "action": "Rien à décider — consigner et passer."},
    "surveiller": {"couleur": "orange", "signe": "●",
                   "dit": "À surveiller.",
                   "action": "Regarder au prochain point ; pas de décision "
                             "à prendre sur ce seul écart."},
    "alerte": {"couleur": "rouge", "signe": "●",
               "dit": "Alerte — action requise.",
               "action": "Décision attendue : le seuil est franchi au-delà "
                         "de l'incertitude, ce n'est pas du bruit."},
    "indetermine": {"couleur": "gris", "signe": "○",
                    "dit": "Écart non démontré.",
                    "action": "L'écart existe mais reste dans l'incertitude "
                              "de la grandeur : resserrer la mesure avant "
                              "d'agir."},
    "non_mesure": {"couleur": "gris", "signe": "○",
                   "dit": "Non mesuré.",
                   "action": "Aucune valeur : il n'y a rien à colorer."},
}

# Le sens de l'écart : un dépassement de coût est mauvais, un dépassement de
# rendement est bon. Écrit par indicateur, jamais deviné du signe.
SENS = {"bas_bon": "une valeur BASSE est bonne (coût, délai, consommation)",
        "haut_bon": "une valeur HAUTE est bonne (rendement, taux, marge)"}


def evaluer_seuil(valeur, cible, tolerance=0.0, incertitude=0.0,
                  sens="bas_bon"):
    """L'état d'un indicateur face à sa cible — avec l'incertitude en garde.

    `tolerance`   : marge admise autour de la cible, en fraction (0,05 = 5 %).
    `incertitude` : incertitude RELATIVE de la valeur (0,30 pour ±30 %).

    LA RÈGLE QUI ÉVITE LES FAUSSES ALERTES. Un écart plus petit que
    l'incertitude de la grandeur n'est pas un écart : c'est du bruit. Le
    rouge ne s'allume donc que si le dépassement excède À LA FOIS la
    tolérance ET l'incertitude. Entre les deux, l'état est « écart non
    démontré » — ce qui appelle une mesure plus fine, pas une réunion de
    crise.
    """
    try:
        v = float(valeur)
        c = float(cible)
    except (TypeError, ValueError):
        return {"etat": "non_mesure", "ecart": None, "ecart_pct": None,
                **ETATS["non_mesure"],
                "lecture": "Valeur ou cible absente : rien à évaluer."}
    if c == 0:
        return {"etat": "non_mesure", "ecart": None, "ecart_pct": None,
                **ETATS["non_mesure"],
                "lecture": "Cible nulle : l'écart relatif n'a pas de sens."}
    tol = max(0.0, float(tolerance or 0.0))
    inc = max(0.0, float(incertitude or 0.0))
    ecart = v - c
    rel = ecart / abs(c)
    # Le dépassement DÉFAVORABLE, selon le sens de l'indicateur.
    depasse = rel if sens == "bas_bon" else -rel

    if depasse <= tol:
        etat = "conforme"
        lecture = ("Dans la cible (%s %% d'écart, tolérance %s %%)."
                   % (round(rel * 100, 1), round(tol * 100, 1)))
    elif depasse <= max(tol, inc):
        # Au-delà de la tolérance mais DANS l'incertitude : l'écart existe
        # peut-être, il n'est pas démontré. C'est la nuance que le rouge
        # écraserait.
        etat = "indetermine"
        lecture = ("Écart de %s %% au-delà de la tolérance (%s %%) — mais "
                   "l'incertitude de la grandeur est de ±%s %% : l'écart "
                   "n'est pas démontré. Resserrer la mesure avant d'alerter."
                   % (round(depasse * 100, 1), round(tol * 100, 1),
                      round(inc * 100, 1)))
    elif depasse <= max(tol, inc) * 2:
        etat = "surveiller"
        lecture = ("Écart de %s %%, au-delà de la tolérance ET de "
                   "l'incertitude (±%s %%) : réel, mais encore modéré."
                   % (round(depasse * 100, 1), round(inc * 100, 1)))
    else:
        etat = "alerte"
        lecture = ("Écart de %s %% — franchement au-delà de la tolérance et "
                   "de l'incertitude (±%s %%). Ce n'est pas du bruit."
                   % (round(depasse * 100, 1), round(inc * 100, 1)))
    return {"etat": etat, "ecart": round(ecart, 4),
            "ecart_pct": round(rel * 100, 2), **ETATS[etat],
            "lecture": lecture, "sens": sens, "sens_dit": SENS.get(sens, "")}


# ═══════════════════════════════════════════════════════════════════════════
#  3. LA TENDANCE — mesurée sur la série, comparée à son propre bruit
# ═══════════════════════════════════════════════════════════════════════════

def tendance(serie, sens="bas_bon"):
    """La flèche, calculée. Plate quand la pente ne sort pas du bruit.

    Une flèche qui monte parce que le dernier point est au-dessus du
    précédent décore ; elle ne renseigne pas. On compare donc la pente
    moyenne à la dispersion des écarts successifs : si elle n'en sort pas,
    la tendance est déclarée stable — et c'est une information.
    """
    pts = [float(x) for x in (serie or []) if x is not None]
    if len(pts) < 3:
        return {"fleche": "→", "sens": "indeterminee",
                "lecture": "Moins de trois points : aucune tendance ne peut "
                           "être établie, et une flèche en dessinerait une."}
    ecarts = [pts[i + 1] - pts[i] for i in range(len(pts) - 1)]
    pente = sum(ecarts) / len(ecarts)
    moy = sum(abs(e) for e in ecarts) / len(ecarts)
    if moy == 0 or abs(pente) < moy * 0.5:
        return {"fleche": "→", "sens": "stable", "pente": round(pente, 4),
                "lecture": "Stable : les variations se compensent, la pente "
                           "ne sort pas du bruit de la série."}
    monte = pente > 0
    bon = (monte and sens == "haut_bon") or (not monte and sens == "bas_bon")
    return {"fleche": "↗" if monte else "↘",
            "sens": "hausse" if monte else "baisse",
            "favorable": bon, "pente": round(pente, 4),
            "lecture": ("En %s sur les derniers points — %s pour cet "
                        "indicateur." % ("hausse" if monte else "baisse",
                                         "favorable" if bon else "défavorable"))}


# ═══════════════════════════════════════════════════════════════════════════
#  4. CE QUI EST TENABLE — la jonction avec la maturité analytique
# ═══════════════════════════════════════════════════════════════════════════

# Le diagnostic de maturité dit ce que l'organisation peut alimenter. Un
# tableau de bord qui promet des notifications proactives à une organisation
# incapable de dater ses données sera abandonné — et ce module refuse de le
# promettre plutôt que de le laisser croire.
TENABLE = {
    0: {"alertes": False, "notifications": False,
        "dit": "Aucune alerte automatique n'est tenable : sans donnée datée "
               "qui arrive, un seuil ne peut pas être franchi — il peut "
               "seulement être oublié. Les couleurs seraient figées au jour "
               "de la saisie."},
    1: {"alertes": True, "notifications": False,
        "dit": "Alertes visuelles à la revue périodique, oui — notifications "
               "proactives, non : elles supposent une collecte qui tourne "
               "sans intervention, et elle n'existe pas encore."},
    2: {"alertes": True, "notifications": True,
        "dit": "Alertes et notifications au franchissement sont tenables, à "
               "condition de nommer qui les reçoit et ce qu'il en fait — une "
               "alerte sans destinataire est un courriel de plus."},
    3: {"alertes": True, "notifications": True,
        "dit": "Pilotage complet : alertes, notifications, et suivi de "
               "l'écart entre la décision et son exécution."},
}


def tenable_au_niveau(niveau):
    """Ce que le pilotage peut promettre à ce niveau de maturité."""
    if niveau is None:
        return {"alertes": False, "notifications": False,
                "dit": "La maturité analytique n'a pas été diagnostiquée : on "
                       "ne sait pas ce que l'organisation peut alimenter. "
                       "Établir le diagnostic avant d'engager un tableau de "
                       "bord évite de promettre ce qui sera abandonné."}
    return TENABLE.get(int(niveau), TENABLE[0])


# ═══════════════════════════════════════════════════════════════════════════
#  5. LES INDICATEURS DE PILOTAGE D'UN INVESTISSEMENT DATA CENTRE
#
#  Chacun porte sa forme, son sens, sa tolérance et — c'est le point — son
#  INCERTITUDE par défaut, celle de la grandeur d'où il vient. Un indicateur
#  d'avant-projet ne se pilote pas avec la finesse d'un décompte de travaux,
#  et prétendre le contraire produit des alertes qui n'engagent personne.
# ═══════════════════════════════════════════════════════════════════════════

INDICATEURS = [
    {"cle": "enveloppe_kw", "nom": "Enveloppe par kW informatique",
     "unite": "€/kW IT", "nature": "categories", "sens": "bas_bon",
     "tolerance": 0.10, "incertitude": 0.30,
     "pourquoi": "Le ratio qui permet de comparer un projet à un autre et de "
                 "situer une offre. À ce stade d'étude, il porte ±30 % : "
                 "c'est la précision d'un ordre de grandeur, pas d'un devis.",
     "risque": "Un dépassement durable indique un programme qui a grossi "
               "sans arbitrage — le plus souvent par ajouts de redondance."},
    {"cle": "part_moe", "nom": "Part de la maîtrise d'œuvre",
     "unite": "% des travaux", "nature": "parts", "sens": "bas_bon",
     "tolerance": 0.15, "incertitude": 0.15,
     "pourquoi": "Une MOE trop basse ne finance pas les études : l'économie "
                 "se paie en avenants. Trop haute, elle signale un périmètre "
                 "mal défini.",
     "risque": "Sous le barème, les phases écartées reviennent en travaux "
               "supplémentaires — le poste où l'écart se voit le plus tard."},
    {"cle": "avancement_etudes", "nom": "Avancement des études par phase",
     "unite": "%", "nature": "temps", "sens": "haut_bon",
     "tolerance": 0.10, "incertitude": 0.05,
     "pourquoi": "Le seul indicateur d'avancement qui se constate sur pièces "
                 "remises, et non sur déclaration.",
     "risque": "Un retard d'études se rattrape rarement : il se transfère au "
               "chantier, où il coûte dix fois plus."},
    {"cle": "delai_raccordement", "nom": "Délai de raccordement électrique",
     "unite": "mois", "nature": "temps", "sens": "bas_bon",
     "tolerance": 0.10, "incertitude": 0.20,
     "pourquoi": "Le poste qui commande la date de mise en service, et que "
                 "l'entreprise ne maîtrise pas : il se suit, il ne se décide "
                 "pas.",
     "risque": "Un glissement ici décale toute la chaîne de recettes — et "
               "aucune accélération de chantier ne le rattrape."},
    {"cle": "pue_constate", "nom": "PUE constaté en exploitation",
     "unite": "sans unité", "nature": "temps", "sens": "bas_bon",
     "tolerance": 0.05, "incertitude": 0.08,
     "pourquoi": "L'écart entre le PUE promis et le PUE mesuré est la "
                 "première chose qu'un acheteur vérifie — et la première que "
                 "les garanties contractuelles sanctionnent.",
     "risque": "Une dérive saisonnière régulière n'est pas une panne : c'est "
               "une conception dimensionnée sur la mauvaise année météo."},
]

_CLES = [i["cle"] for i in INDICATEURS]


def _verifier():
    f = []
    if len(set(_CLES)) != len(_CLES):
        f.append("clés d'indicateurs en double")
    for i in INDICATEURS:
        if i["nature"] not in ("temps", "categories", "parts"):
            f.append("nature inconnue : " + i["cle"])
        if i["sens"] not in SENS:
            f.append("sens inconnu : " + i["cle"])
        if not i.get("risque"):
            f.append("indicateur sans risque déclaré : " + i["cle"])
        if i.get("incertitude") is None:
            f.append("indicateur sans incertitude : " + i["cle"])
    for n in (0, 1, 2, 3):
        if n not in TENABLE:
            f.append("niveau de maturité sans règle de tenabilité : %d" % n)
    return f


_f = _verifier()
if _f:
    raise AssertionError("pilotage_dc incohérent : " + " ; ".join(_f))
del _f


def piloter(mesures=None, niveau_maturite=None):
    """Le tableau de bord : état, tendance, forme et alerte par indicateur.

    `mesures` : {clé: {"valeur":…, "cible":…, "serie":[…], "incertitude":…}}
    """
    mesures = dict(mesures or {})
    tenab = tenable_au_niveau(niveau_maturite)
    cartes, alertes = [], []
    for ind in INDICATEURS:
        m = dict(mesures.get(ind["cle"]) or {})
        serie = [x for x in (m.get("serie") or []) if x is not None]
        inc = m.get("incertitude")
        inc = ind["incertitude"] if inc is None else float(inc)
        seuil = evaluer_seuil(m.get("valeur"), m.get("cible"),
                              ind["tolerance"], inc, ind["sens"])
        tend = tendance(serie, ind["sens"])
        forme = choisir_forme(ind["nature"], len(serie) or len(m.get("parts") or []),
                              m.get("parts") or serie)
        carte = {"cle": ind["cle"], "nom": ind["nom"], "unite": ind["unite"],
                 "pourquoi": ind["pourquoi"], "risque": ind["risque"],
                 "valeur": m.get("valeur"), "cible": m.get("cible"),
                 "incertitude": inc, "tolerance": ind["tolerance"],
                 "serie": serie, "seuil": seuil, "tendance": tend,
                 "forme": forme}
        # Les trois apports de l'analyse augmentée, déterministes : anomalies,
        # projection, puis le commentaire COMPOSÉ depuis tout ce qui précède.
        # L'ordre compte — l'explication cite ce que les deux premiers ont
        # constaté, elle ne peut donc rien devancer.
        carte["anomalies"] = detecter_anomalies(serie)
        carte["prediction"] = predire(serie, m.get("horizon") or 1)
        carte["explication"] = expliquer(carte)
        cartes.append(carte)
        # UNE ALERTE N'EST PAS UNE COULEUR : elle nomme qui décide et quand.
        # Et elle n'est émise que si la maturité permet de la tenir — sinon
        # elle serait promise et jamais reçue.
        if seuil["etat"] == "alerte" and tenab["alertes"]:
            alertes.append({
                "cle": ind["cle"], "nom": ind["nom"],
                "lecture": seuil["lecture"], "risque": ind["risque"],
                "notifiable": tenab["notifications"],
                "quand": ("à l'instant du franchissement" if tenab["notifications"]
                          else "à la prochaine revue de pilotage"),
            })
    n_alertes = len(alertes)
    n_indet = sum(1 for c in cartes if c["seuil"]["etat"] == "indetermine")
    if not any(c["valeur"] is not None for c in cartes):
        lecture = ("Aucune mesure saisie : ce tableau montre ce qui SERA "
                   "piloté, pas ce qui l'est. Un tableau de bord vide "
                   "présenté comme un pilotage est le premier pas vers son "
                   "abandon.")
    elif n_alertes:
        lecture = ("%d alerte%s : seuil franchi au-delà de l'incertitude — "
                   "ce n'est pas du bruit, une décision est attendue."
                   % (n_alertes, "s" if n_alertes > 1 else ""))
        if n_indet:
            lecture += (" %d écart%s non démontré%s en plus : dans "
                        "l'incertitude, à resserrer avant d'agir."
                        % (n_indet, "s" if n_indet > 1 else "",
                           "s" if n_indet > 1 else ""))
    elif n_indet:
        lecture = ("Aucune alerte démontrée. %d écart%s reste%s dans "
                   "l'incertitude de sa grandeur : la mesure ne permet pas "
                   "de trancher, et colorer en rouge serait une fausse "
                   "alerte." % (n_indet, "s" if n_indet > 1 else "",
                                "nt" if n_indet > 1 else ""))
    else:
        lecture = "Tous les indicateurs mesurés sont dans leur cible."
    return {"version": VERSION, "indicateurs": cartes, "alertes": alertes,
            "lecture": lecture, "tenable": tenab,
            "niveau_maturite": niveau_maturite,
            "reserve": "Les couleurs suivent des seuils ÉCRITS et une "
                       "incertitude déclarée : un écart plus petit que "
                       "l'incertitude de la grandeur ne déclenche pas "
                       "d'alerte. C'est ce qui évite le tableau de bord qui "
                       "crie au loup — et que plus personne ne regarde."}


# ═══════════════════════════════════════════════════════════════════════════
#  6. LES TROIS APPORTS DE L'ANALYSE AUGMENTÉE — SANS MODÈLE DE LANGAGE
#
#  Prédiction, détection d'anomalies et explication en langage naturel sont
#  les trois fonctions que les plateformes décisionnelles rangent sous « IA ».
#  Elles sont construites ici de façon DÉTERMINISTE, et c'est un choix, pas
#  une limite :
#
#   — une projection doit pouvoir être REFAITE À LA MAIN par celui qui la
#     conteste. Une régression sur cinq points se vérifie ; un modèle appris
#     ne se vérifie pas en comité d'investissement ;
#   — une anomalie signalée doit dire POURQUOI elle en est une. « Le modèle
#     l'a détectée » n'est pas une raison qu'on oppose à un exploitant qui
#     affirme que sa valeur est normale ;
#   — un commentaire généré ne doit RIEN pouvoir inventer. Composé depuis les
#     grandeurs déjà calculées, il ne peut affirmer que ce qui a été mesuré —
#     c'est la seule forme d'explication automatique qu'on annexe à un
#     dossier sans la relire ligne à ligne.
#
#  Deux exécutions sur les mêmes séries rendent le même texte, au mot près.
# ═══════════════════════════════════════════════════════════════════════════

# En dessous de ce nombre de points, on ne projette pas : une tendance tirée
# de trois relevés est une opinion avec des décimales.
PREDICTION_POINTS_MIN = 5
# Au-delà de cette fraction de l'historique, on refuse aussi : prolonger de
# douze mois une série de six est une extrapolation, pas une prévision.
PREDICTION_HORIZON_MAX = 0.5


def predire(serie, horizon=1):
    """La projection des prochains points — et le REFUS quand elle serait une
    invention.

    Régression linéaire par les moindres carrés, avec un intervalle qui
    S'ÉLARGIT avec l'horizon : projeter loin est moins sûr que projeter
    près, et un intervalle constant le cacherait. L'écart-type des résidus
    donne la largeur ; l'horizon la multiplie.
    """
    pts = [float(x) for x in (serie or []) if x is not None]
    n = len(pts)
    h = max(1, int(horizon or 1))
    if n < PREDICTION_POINTS_MIN:
        return {"possible": False,
                "motif": "%d point%s d'historique : il en faut au moins %d. "
                         "Une tendance tirée de moins de relevés est une "
                         "opinion avec des décimales — et elle se citera "
                         "comme une prévision."
                         % (n, "s" if n > 1 else "", PREDICTION_POINTS_MIN)}
    if h > max(1, int(n * PREDICTION_HORIZON_MAX)):
        return {"possible": False,
                "motif": "Horizon de %d point%s pour %d d'historique : "
                         "au-delà de la moitié de la série, ce n'est plus "
                         "une prévision mais une extrapolation. Allonger "
                         "l'historique avant d'allonger l'horizon."
                         % (h, "s" if h > 1 else "", n)}

    # Moindres carrés sur x = 0..n-1 — refaisable à la main, et c'est le point.
    xm = (n - 1) / 2.0
    ym = sum(pts) / n
    num = sum((i - xm) * (pts[i] - ym) for i in range(n))
    den = sum((i - xm) ** 2 for i in range(n)) or 1.0
    a = num / den
    b = ym - a * xm
    residus = [pts[i] - (a * i + b) for i in range(n)]
    # Écart-type des résidus : ce que le modèle N'EXPLIQUE PAS. C'est lui qui
    # donne l'honnêteté de l'intervalle.
    var = sum(r * r for r in residus) / max(1, n - 2)
    sigma = var ** 0.5

    points = []
    for k in range(1, h + 1):
        x = n - 1 + k
        v = a * x + b
        # L'intervalle s'élargit en racine de l'horizon : c'est la forme la
        # plus prudente qui reste simple à expliquer.
        marge = 1.96 * sigma * (k ** 0.5)
        points.append({"rang": k, "valeur": round(v, 4),
                       "bas": round(v - marge, 4), "haut": round(v + marge, 4),
                       "marge": round(marge, 4)})
    dernier = points[-1]
    largeur = (dernier["haut"] - dernier["bas"])
    rel = abs(largeur / dernier["valeur"]) if dernier["valeur"] else None
    lecture = ("Projection sur %d point%s : %s attendu, entre %s et %s "
               "(intervalle à 95 %%). L'intervalle s'élargit avec l'horizon "
               "— c'est ce qu'une prévision honnête montre."
               % (h, "s" if h > 1 else "", round(dernier["valeur"], 2),
                  round(dernier["bas"], 2), round(dernier["haut"], 2)))
    if rel is not None and rel > 0.5:
        lecture += (" ATTENTION : l'intervalle dépasse la moitié de la valeur "
                    "projetée. La série est trop dispersée pour que cette "
                    "projection serve à décider — elle sert à surveiller.")
    return {"possible": True, "pente": round(a, 5), "ordonnee": round(b, 4),
            "sigma_residus": round(sigma, 4), "points": points,
            "lecture": lecture,
            "methode": "Régression linéaire par moindres carrés sur "
                       "l'historique fourni ; intervalle à 1,96 σ des "
                       "résidus, élargi en racine de l'horizon. Aucun modèle "
                       "appris : le calcul se refait à la main.",
            "variables_manquantes":
                "Cette projection ne connaît QUE l'historique de "
                "l'indicateur. Les variables explicatives — carnet de "
                "commandes, saisonnalité connue, décision de marché — n'y "
                "sont pas : les intégrer relève d'un modèle multivarié, qui "
                "suppose des séries que ce moteur n'a pas."}


# Seuil de détection d'anomalie, en écarts absolus médians (MAD). 3,5 est
# l'usage courant. On emploie le MAD et non l'écart-type parce que l'écart-
# type est lui-même gonflé par l'anomalie qu'on cherche : une valeur aberrante
# élève la dispersion, donc son propre seuil, et finit par passer inaperçue.
ANOMALIE_SEUIL_MAD = 3.5
# Une rupture de tendance se constate en comparant la pente de la première
# moitié à celle de la seconde. Sous ce rapport, on ne parle pas de rupture.
RUPTURE_RAPPORT = 2.0


def detecter_anomalies(serie):
    """Les valeurs aberrantes ET les ruptures de tendance — deux choses
    distinctes, que confondre fait chercher au mauvais endroit.

    Une valeur aberrante est un point isolé : incident, erreur de saisie,
    arrêt technique. Une rupture est un changement de régime : la série
    continue, autrement. La première appelle une vérification, la seconde
    une explication — et l'action n'est pas la même.
    """
    pts = [float(x) for x in (serie or []) if x is not None]
    n = len(pts)
    if n < 4:
        return {"possible": False,
                "motif": "%d point%s : en dessous de quatre, tout écart peut "
                         "être le début d'une tendance. Signaler une anomalie "
                         "ici enverrait chercher une cause qui n'existe pas."
                         % (n, "s" if n > 1 else "")}
    tri = sorted(pts)
    med = (tri[n // 2] if n % 2 else (tri[n // 2 - 1] + tri[n // 2]) / 2.0)
    ecarts = sorted(abs(x - med) for x in pts)
    mad = (ecarts[n // 2] if n % 2
           else (ecarts[n // 2 - 1] + ecarts[n // 2]) / 2.0)
    # 0,6745 : facteur qui rend le MAD comparable à un écart-type sur une
    # distribution normale — sans lui, le seuil de 3,5 ne voudrait rien dire.
    aberrantes = []
    if mad > 0:
        for i, v in enumerate(pts):
            score = 0.6745 * abs(v - med) / mad
            if score > ANOMALIE_SEUIL_MAD:
                aberrantes.append({
                    "rang": i, "valeur": v, "score": round(score, 2),
                    "pourquoi": "Écart de %s fois la dispersion habituelle de "
                                "la série (médiane %s). Vérifier d'abord la "
                                "saisie et l'événement de la période : une "
                                "valeur aberrante isolée est plus souvent un "
                                "incident de mesure qu'un signal."
                                % (round(score, 1), round(med, 2))})
    else:
        # MAD NUL : la série est constante à la médiane près. Le cas paraît
        # théorique — il ne l'est pas : un relevé figé pendant six mois puis
        # un saut, c'est exactement le compteur qu'on avait oublié de lire.
        # Sortir ici sans rien signaler laissait passer l'anomalie la plus
        # visible de toutes, faute de pouvoir la diviser par zéro.
        for i, v in enumerate(pts):
            if v != med:
                aberrantes.append({
                    "rang": i, "valeur": v, "score": None,
                    "pourquoi": "La série est CONSTANTE à %s partout ailleurs : "
                                "la dispersion habituelle est nulle, et tout "
                                "écart y est donc anormal par construction. "
                                "Un relevé figé puis un saut signale plus "
                                "souvent une reprise de saisie qu'un "
                                "événement." % round(med, 2)})

    rupture = None
    if n >= 6:
        m = n // 2
        p1, p2 = pts[:m], pts[m:]
        def _pente(seq):
            k = len(seq)
            xm = (k - 1) / 2.0
            ym = sum(seq) / k
            d = sum((i - xm) ** 2 for i in range(k)) or 1.0
            return sum((i - xm) * (seq[i] - ym) for i in range(k)) / d
        a1, a2 = _pente(p1), _pente(p2)
        change_signe = (a1 > 0) != (a2 > 0) and abs(a1) > 0 and abs(a2) > 0
        amplifie = abs(a1) > 0 and abs(a2 / a1) > RUPTURE_RAPPORT
        if change_signe or amplifie:
            rupture = {
                "rang": m, "pente_avant": round(a1, 4), "pente_apres": round(a2, 4),
                "nature": "inversion" if change_signe else "accélération",
                "pourquoi": ("La pente passe de %s à %s au milieu de la "
                             "série : ce n'est pas un point isolé, c'est un "
                             "changement de régime. Il appelle une "
                             "explication — décision, saison, incident "
                             "durable — pas une vérification de saisie."
                             % (round(a1, 3), round(a2, 3)))}

    if not aberrantes and not rupture:
        lecture = ("Aucune anomalie : les variations restent dans la "
                   "dispersion habituelle de la série, et la pente ne change "
                   "pas de régime.")
    else:
        bouts = []
        if aberrantes:
            bouts.append("%d valeur%s aberrante%s"
                         % (len(aberrantes), "s" if len(aberrantes) > 1 else "",
                            "s" if len(aberrantes) > 1 else ""))
        if rupture:
            bouts.append("une rupture de tendance (%s)" % rupture["nature"])
        lecture = ("Détecté : " + " et ".join(bouts)
                   + ". Une valeur aberrante appelle une VÉRIFICATION ; une "
                     "rupture appelle une EXPLICATION — l'action n'est pas la "
                     "même.")
    return {"possible": True, "mediane": round(med, 4), "mad": round(mad, 4),
            "aberrantes": aberrantes, "rupture": rupture, "lecture": lecture,
            "methode": "Écart absolu médian (MAD) au seuil de %s, et "
                       "comparaison des pentes de chaque moitié de série. Le "
                       "MAD est employé plutôt que l'écart-type parce que "
                       "celui-ci est gonflé par l'anomalie qu'on cherche."
                       % ANOMALIE_SEUIL_MAD}


def expliquer(carte):
    """Le commentaire en langage naturel — COMPOSÉ, jamais généré.

    L'explication automatisée fait gagner un temps réel : elle évite de
    relire chaque figure pour retrouver ce qu'elle dit. Mais un commentaire
    produit par un modèle de langage ne peut pas être annexé à un dossier
    sans relecture, parce qu'il peut affirmer une cause qui n'a pas été
    mesurée — et c'est précisément ce qu'un lecteur pressé retiendra.

    Celui-ci est composé depuis les grandeurs DÉJÀ CALCULÉES de la carte. Il
    ne peut donc rien affirmer d'autre. Il nomme un CONSTAT et, quand une
    cause est plausible, il la pose en question — jamais en affirmation.
    """
    if not carte:
        return ""
    L = []
    nom = carte.get("nom", "Cet indicateur")
    seuil = carte.get("seuil") or {}
    tend = carte.get("tendance") or {}
    val, cible = carte.get("valeur"), carte.get("cible")

    if val is None:
        return ("%s n'est pas mesuré : il n'y a rien à commenter, et un "
                "commentaire ici décrirait un vide." % nom)

    etat = seuil.get("etat")
    if etat == "conforme":
        L.append("%s est dans sa cible (%s contre %s)." % (nom, val, cible))
    elif etat == "indetermine":
        L.append("%s s'écarte de sa cible, mais l'écart reste dans "
                 "l'incertitude de la grandeur : il n'est pas démontré."
                 % nom)
    elif etat == "surveiller":
        L.append("%s s'écarte réellement de sa cible (%s contre %s), au-delà "
                 "du bruit de mesure." % (nom, val, cible))
    elif etat == "alerte":
        L.append("%s franchit son seuil (%s contre %s), franchement au-delà "
                 "de l'incertitude : l'écart est établi." % (nom, val, cible))
    else:
        L.append("%s n'a pas de cible renseignée : son écart ne se calcule "
                 "pas." % nom)

    if tend.get("sens") == "stable":
        L.append("La série est stable — les variations se compensent.")
    elif tend.get("sens") in ("hausse", "baisse"):
        L.append("Elle est en %s, ce qui est %s ici."
                 % (tend["sens"], "favorable" if tend.get("favorable")
                    else "défavorable"))

    an = carte.get("anomalies") or {}
    if an.get("possible"):
        if an.get("rupture"):
            L.append("Une rupture de tendance (%s) apparaît au milieu de la "
                     "série : quel événement de cette période pourrait "
                     "l'expliquer ?" % an["rupture"]["nature"])
        if an.get("aberrantes"):
            L.append("%d valeur%s sort%s de la dispersion habituelle : "
                     "vérifier la saisie et l'événement de la période avant "
                     "d'y voir un signal."
                     % (len(an["aberrantes"]),
                        "s" if len(an["aberrantes"]) > 1 else "",
                        "ent" if len(an["aberrantes"]) > 1 else ""))

    pr = carte.get("prediction") or {}
    if pr.get("possible"):
        d = pr["points"][-1]
        L.append("Au rythme constaté, la projection donne %s (entre %s et "
                 "%s)." % (d["valeur"], d["bas"], d["haut"]))
    elif pr.get("motif"):
        L.append("Aucune projection : %s" % pr["motif"][:120])

    if etat in ("surveiller", "alerte") and carte.get("risque"):
        L.append("Ce que cela risque : %s" % carte["risque"])

    L.append("— Commentaire composé à partir des grandeurs calculées "
             "ci-dessus, sans modèle de langage : il ne peut affirmer que ce "
             "qui a été mesuré, et pose les causes en question.")
    return " ".join(L)


def referentiel():
    return {"version": VERSION, "formes": FORMES, "etats": ETATS,
            "sens": SENS, "indicateurs": INDICATEURS, "tenable": TENABLE,
            "camembert_parts_max": CAMEMBERT_PARTS_MAX,
            "camembert_ecart_min": CAMEMBERT_ECART_MIN,
            "prediction_points_min": PREDICTION_POINTS_MIN,
            "anomalie_seuil_mad": ANOMALIE_SEUIL_MAD}


def sante():
    return {"module": "pilotage_dc", "version": VERSION,
            "indicateurs": len(INDICATEURS), "formes": len(FORMES),
            "etats": len(ETATS), "problemes": _verifier()}
