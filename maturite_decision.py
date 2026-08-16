"""La maturité analytique décisionnelle, appliquée à l'investissement data centre en UE.

CE QUE CE MODULE EST, ET CE QU'IL N'EST PAS
───────────────────────────────────────────
Il ne dit PAS si un investissement est bon. L'enveloppe, les KPI de création
de valeur et le prix de maîtrise d'œuvre s'en chargent, chacun avec sa
méthode et ses réserves.

Il dit si l'organisation peut INSTRUIRE la décision — ce qui est une autre
question, et la seule qui se pose avant de commander un tableau de bord. Un
comité qui reçoit une enveloppe à ±30 % et n'a ni série historique, ni
donnée datée, ni grille de lecture ne décidera pas mieux avec un graphique de
plus : il décidera à l'intuition, avec un chiffre pour se rassurer.

POURQUOI CE DIAGNOSTIC PRÉCÈDE LE TABLEAU DE BORD
Promettre un pilotage que l'organisation ne peut pas alimenter produit
toujours la même chose : un outil abandonné au troisième mois, et une
défiance durable envers le suivant. Le diagnostic évite d'engager ce qui ne
peut pas être absorbé — et permet une feuille de route ancrée dans les
capacités réelles.

LA RÈGLE DE CALCUL QUI COMMANDE TOUT : LE MAILLON FAIBLE
La maturité globale n'est PAS la moyenne des axes. Une organisation dotée
d'une excellente grille d'analyse mais dont les données ne portent pas de
date ne décide pas mieux qu'une organisation sans date : la grille s'applique
à des données inutilisables. Une moyenne aurait affiché « intermédiaire » et
envoyé travailler la grille — c'est-à-dire renforcer ce qui tient déjà.
Le minimum, lui, désigne ce qui bloque. C'est moins flatteur, et c'est le
seul chiffre actionnable.

Aucun modèle de langage n'intervient ici : deux diagnostics aux mêmes
réponses rendent le même résultat, au point près.
"""

VERSION = "2026-08-a"

# ═══════════════════════════════════════════════════════════════════════════
#  L'ÉCHELLE — quatre niveaux, chacun constatable
#
#  Une échelle dont les niveaux se décrivent par des adjectifs (« bon »,
#  « avancé ») se remplit au moral du jour. Chaque niveau porte donc ici ce
#  qui se CONSTATE : une trace, une fréquence, un responsable nommé.
# ═══════════════════════════════════════════════════════════════════════════

NIVEAUX = [
    {"n": 0, "nom": "absent",
     "constat": "Rien n'existe sur ce point, ou rien qui survive au départ "
                "de la personne qui le porte.",
     "decision": "La décision se prend sans cet appui — elle peut être juste, "
                 "elle n'est pas instruite."},
    {"n": 1, "nom": "initial",
     "constat": "Cela existe au coup par coup, à la demande, sans forme "
                "arrêtée ni responsable désigné.",
     "decision": "Utilisable pour éclairer un arbitrage ponctuel ; pas pour "
                 "engager un capital sur plusieurs années."},
    {"n": 2, "nom": "structuré",
     "constat": "Une méthode écrite existe et un responsable est nommé ; "
                "l'application reste partielle ou irrégulière.",
     "decision": "Suffisant pour instruire une décision d'investissement "
                 "documentée, à condition de nommer les zones non couvertes."},
    {"n": 3, "nom": "piloté",
     "constat": "La méthode est appliquée à intervalle défini, ses résultats "
                "sont mesurés, et les écarts déclenchent une action tracée.",
     "decision": "L'organisation peut suivre l'exécution de sa décision et "
                 "corriger sur des faits — la condition d'un comité utile."},
]
NIVEAU_MAX = max(n["n"] for n in NIVEAUX)


def _niveau(n):
    for x in NIVEAUX:
        if x["n"] == n:
            return x
    return NIVEAUX[0]


# ═══════════════════════════════════════════════════════════════════════════
#  LES QUATRE AXES ET LEURS CRITÈRES
#
#  Chaque critère est une question à laquelle on répond par un CONSTAT, pas
#  par une appréciation : « les jeux de données portent-ils une date de
#  production ? » se vérifie en ouvrant un fichier ; « la donnée est-elle de
#  qualité ? » ne se vérifie pas.
# ═══════════════════════════════════════════════════════════════════════════

AXES = [
    {
        "cle": "cible",
        "nom": "Définir la maturité cible",
        "resume": "Critères objectifs de maturité, KPI de pilotage, maintien "
                  "dans la durée.",
        "pourquoi": "Sans cap écrit, l'écart ne se mesure pas — et tout "
                    "tableau de bord devient une collection d'indicateurs "
                    "dont personne ne sait lequel devrait bouger.",
        "criteres": [
            {"cle": "criteres_ecrits",
             "question": "Les critères de maturité attendus sont-ils écrits, "
                         "avec un seuil chiffré par critère ?",
             "preuve": "Le document qui les porte, daté et diffusé."},
            {"cle": "kpi_pilotage",
             "question": "Les KPI de pilotage sont-ils arrêtés, chacun avec "
                         "son propriétaire et sa fréquence de revue ?",
             "preuve": "La liste des KPI avec, en regard, un nom et un rythme."},
            {"cle": "maintien",
             "question": "Le maintien dans la durée est-il organisé — qui "
                         "réévalue, quand, et que déclenche un écart ?",
             "preuve": "Le compte rendu de la dernière réévaluation."},
        ],
    },
    {
        "cle": "collecte",
        "nom": "Collecte de données",
        "resume": "Cibler les sources, outiller la collecte, qualifier la "
                  "donnée, la temporaliser.",
        "pourquoi": "Une donnée non datée ou non traçable est inutilisable en "
                    "contexte décisionnel : elle ne se compare à rien, et "
                    "personne ne peut dire si elle vaut encore.",
        "criteres": [
            {"cle": "sources_ciblees",
             "question": "Les sources nécessaires à chaque KPI sont-elles "
                         "identifiées nommément, y compris les sources "
                         "externes (marché, énergie, foncier) ?",
             "preuve": "La cartographie source → indicateur."},
            {"cle": "collecte_outillee",
             "question": "La collecte est-elle outillée — automatisée ou, à "
                         "défaut, décrite par une procédure reproductible ?",
             "preuve": "Le flux ou la procédure, et son dernier passage."},
            {"cle": "donnee_qualifiee",
             "question": "La donnée est-elle qualifiée : périmètre, unité, "
                         "mode de calcul, incertitude connue ?",
             "preuve": "Le dictionnaire de données, ou les fiches "
                       "d'indicateur."},
            {"cle": "donnee_datee",
             "question": "Chaque donnée porte-t-elle sa date de production ET "
                         "sa période de validité ?",
             "preuve": "Un extrait quelconque : la date doit y être, sans "
                       "avoir à la demander à quelqu'un."},
        ],
    },
    {
        "cle": "analyse",
        "nom": "Traitement et analyse",
        "resume": "Grille analytique, méthodes qualitative ET quantitative.",
        "pourquoi": "Des données brutes ne deviennent des éléments de "
                    "décision que par une grille — et une grille purement "
                    "quantitative rate ce qui décide vraiment d'un site : "
                    "l'acceptabilité locale, le délai de raccordement, la "
                    "disponibilité des compétences.",
        "criteres": [
            {"cle": "grille",
             "question": "Une grille de lecture existe-t-elle, disant quel "
                         "écart appelle quelle question ?",
             "preuve": "La grille, appliquée à un cas réel."},
            {"cle": "quanti",
             "question": "Les méthodes quantitatives sont-elles tenues — "
                         "séries, écarts, sensibilité aux hypothèses ?",
             "preuve": "Une analyse de sensibilité déjà produite."},
            {"cle": "quali",
             "question": "Le qualitatif est-il instruit avec la même rigueur "
                         "— entretiens, avis d'exploitants, retours "
                         "d'incidents — et tracé ?",
             "preuve": "Les comptes rendus, et ce qu'ils ont changé."},
        ],
    },
    {
        "cle": "amelioration",
        "nom": "Axe d'amélioration",
        "resume": "Déclinaison des actions et priorisation.",
        "pourquoi": "La maturité analytique n'est jamais un état figé : sans "
                    "actions hiérarchisées ni jalon de réévaluation, le "
                    "diagnostic devient un constat qu'on relit un an plus "
                    "tard, inchangé.",
        "criteres": [
            {"cle": "actions",
             "question": "Les actions d'amélioration sont-elles identifiées, "
                         "chacune avec un porteur et une échéance ?",
             "preuve": "Le plan d'actions, avec ses dates."},
            {"cle": "priorisation",
             "question": "Sont-elles hiérarchisées selon leur effet sur la "
                         "maturité — et non selon leur facilité ?",
             "preuve": "Le critère de priorisation écrit, et son application."},
            {"cle": "jalons",
             "question": "Des jalons de réévaluation sont-ils posés au "
                         "calendrier ?",
             "preuve": "La date de la prochaine, déjà inscrite."},
        ],
    },
]

_CLES_AXES = [a["cle"] for a in AXES]


# ═══════════════════════════════════════════════════════════════════════════
#  LES TROIS FAMILLES DE DÉCISION, ET CE QUE CETTE ÉTUDE LEUR APPORTE
#
#  Le point de jonction avec l'enveloppe. Chaque famille dit :
#   — ce qu'elle exige pour être instruite ;
#   — ce que l'étude d'enveloppe COUVRE déjà (constaté sur le calcul, pas
#     promis) ;
#   — ce qu'elle ne couvre pas, et qui doit venir de l'organisation.
#
#  `couvert_par` nomme les blocs de l'étude ; `exige_axes` dit quels axes de
#  maturité conditionnent cette famille — car une décision de positionnement
#  concurrentiel repose sur des données EXTERNES, donc sur la collecte, bien
#  plus que sur la grille d'analyse.
# ═══════════════════════════════════════════════════════════════════════════

DECISIONS = [
    {
        "cle": "investissement",
        "nom": "Décision d'investissement",
        "porte_sur": "Acquisition d'un site, ouverture d'un centre, extension "
                     "de capacité, nouveau produit d'hébergement.",
        "exige": [
            "des projections financières sur trois à cinq ans",
            "une analyse de rentabilité assise sur des hypothèses écrites",
            "des scénarios de risque, dont au moins un défavorable",
        ],
        "couvert_par": [
            {"bloc": "enveloppe",
             "apporte": "L'ordre de grandeur d'investissement par lots "
                        "techniques, avec sa fourchette assumée — la base de "
                        "toute projection."},
            {"bloc": "kpi",
             "apporte": "Les indicateurs de création de valeur (EVA, ROCE, "
                        "flux de trésorerie disponible) et leur provenance."},
            {"bloc": "moe",
             "apporte": "Le prix de la maîtrise d'œuvre par phases — une "
                        "ligne que les projections oublient régulièrement."},
        ],
        "hors_perimetre": [
            "le coût du capital propre à l'entreprise et sa structure de "
            "financement",
            "les hypothèses de remplissage et de prix de vente sur la durée",
            "le calendrier réel de raccordement électrique, qui commande "
            "souvent la date de mise en service",
        ],
        "exige_axes": ["cible", "collecte", "analyse"],
    },
    {
        "cle": "positionnement",
        "nom": "Décision de positionnement concurrentiel",
        "porte_sur": "Où s'implanter face aux acteurs en place, sur quel "
                     "segment, avec quelle promesse de service.",
        "exige": [
            "des données de marché datées et comparables",
            "des parts de marché par zone et par segment",
            "des indicateurs de satisfaction client comparés aux concurrents",
        ],
        "couvert_par": [
            {"bloc": "pays",
             "apporte": "La comparaison entre pays d'implantation sur les "
                        "facteurs physiques et réglementaires — coût de "
                        "l'énergie, eau, mix, contraintes."},
        ],
        "hors_perimetre": [
            "les parts de marché des opérateurs, qui ne sont pas publiques "
            "à la maille utile",
            "la satisfaction client comparée, qui suppose une enquête propre "
            "ou un panel acheté",
            "les intentions d'investissement des concurrents",
        ],
        "exige_axes": ["collecte", "analyse"],
    },
    {
        "cle": "allocation",
        "nom": "Décision d'allocation de ressources",
        "porte_sur": "Répartir les ressources humaines, budgétaires et "
                     "techniques entre sites, projets et priorités.",
        "exige": [
            "un tableau de bord croisant performance par entité, capacité "
            "disponible et priorités stratégiques",
            "une mesure de capacité qui ne soit pas déclarative",
            "des priorités arbitrées et écrites",
        ],
        "couvert_par": [
            {"bloc": "moe",
             "apporte": "La charge de maîtrise d'œuvre par phase — une entrée "
                        "directe du plan de charge."},
            {"bloc": "enveloppe",
             "apporte": "La ventilation par lots, qui donne la maille "
                        "budgétaire de l'arbitrage."},
        ],
        "hors_perimetre": [
            "la capacité réelle des équipes, qui se mesure dans "
            "l'organisation, pas dans une étude",
            "les priorités stratégiques, qui s'arbitrent en comité",
            "la performance par entité, qui suppose un contrôle de gestion "
            "en place",
        ],
        "exige_axes": ["cible", "collecte", "amelioration"],
    },
]

_CLES_DECISIONS = [d["cle"] for d in DECISIONS]

# Les blocs de l'étude d'enveloppe auxquels `couvert_par` peut renvoyer. Une
# clé inventée ferait promettre au diagnostic un apport que la page ne rend
# pas — contrôlé au chargement.
BLOCS_ETUDE = {
    "enveloppe": "Enveloppe d'investissement et DPGF",
    "kpi": "Création de valeur (EVA, ROCE, flux disponible)",
    "moe": "Prix de la maîtrise d'œuvre",
    "pays": "Comparaison des pays d'implantation",
}


def _verifier():
    """Le référentiel se contredit-il ? Contrôlé à l'import — c'est le seul
    moment où l'incohérence est encore gratuite."""
    f = []
    if len(set(_CLES_AXES)) != len(_CLES_AXES):
        f.append("clés d'axes en double")
    for a in AXES:
        if not a["criteres"]:
            f.append("axe sans critère : " + a["cle"])
        for c in a["criteres"]:
            for champ in ("question", "preuve"):
                if not str(c.get(champ, "")).strip():
                    f.append("critère incomplet : %s.%s" % (a["cle"], c["cle"]))
    for d in DECISIONS:
        for ax in d["exige_axes"]:
            if ax not in _CLES_AXES:
                f.append("décision %s : axe inconnu %s" % (d["cle"], ax))
        for c in d["couvert_par"]:
            if c["bloc"] not in BLOCS_ETUDE:
                f.append("décision %s : bloc d'étude inconnu %s"
                         % (d["cle"], c["bloc"]))
        if not d["hors_perimetre"]:
            f.append("décision %s : aucun hors-périmètre déclaré — une "
                     "famille qui ne dit pas ce qu'elle ne couvre pas se lit "
                     "comme un quitus" % d["cle"])
    return f


_f = _verifier()
if _f:
    raise AssertionError("maturite_decision incohérent : " + " ; ".join(_f))
del _f


# ═══════════════════════════════════════════════════════════════════════════
#  LE DIAGNOSTIC
# ═══════════════════════════════════════════════════════════════════════════

def _lire_reponse(v):
    """Une réponse est un niveau 0-3, ou rien. Une valeur illisible n'est PAS
    ramenée à zéro : elle reste non répondue, et le diagnostic dit combien de
    critères n'ont pas été instruits. Un zéro inventé abaisserait la maturité
    d'une organisation qui a simplement sauté une question."""
    if v is None or v == "":
        return None
    try:
        n = int(v)
    except (TypeError, ValueError):
        return None
    return n if 0 <= n <= NIVEAU_MAX else None


def diagnostic(reponses=None, etude=None):
    """La maturité analytique de l'organisation, axe par axe, et ce qu'elle
    permet de décider.

    `reponses` : {clé_axe: {clé_critère: 0..3}} — les constats.
    `etude`    : {"enveloppe": bool, "kpi": bool, "moe": bool, "pays": bool}
                 ce que la page a RÉELLEMENT calculé au moment du diagnostic.
                 Non fourni, aucun bloc n'est réputé disponible : on ne
                 promet pas un apport qu'on n'a pas constaté.
    """
    reponses = dict(reponses or {})
    dispo = {k: bool((etude or {}).get(k)) for k in BLOCS_ETUDE}

    axes = []
    for a in AXES:
        rep = dict(reponses.get(a["cle"]) or {})
        notes, manquants = [], []
        criteres = []
        for c in a["criteres"]:
            n = _lire_reponse(rep.get(c["cle"]))
            if n is None:
                manquants.append(c["cle"])
            else:
                notes.append(n)
            criteres.append({"cle": c["cle"], "question": c["question"],
                             "preuve": c["preuve"], "niveau": n})
        # Le niveau de l'axe est celui de son critère le plus faible — même
        # raison qu'au global : un axe ne vaut pas la moyenne de ses parties
        # quand l'une d'elles bloque l'usage des autres.
        niveau = min(notes) if notes else None
        axes.append({
            "cle": a["cle"], "nom": a["nom"], "resume": a["resume"],
            "pourquoi": a["pourquoi"], "criteres": criteres,
            "niveau": niveau,
            "niveau_nom": _niveau(niveau)["nom"] if niveau is not None else "non instruit",
            "instruit": len(notes), "total": len(a["criteres"]),
            "manquants": manquants,
            "faible": None if niveau is None else
                      [c["cle"] for c in criteres if c["niveau"] == niveau],
        })

    instruits = [a for a in axes if a["niveau"] is not None]
    complet = all(not a["manquants"] for a in axes)
    if not instruits:
        global_n = None
        lecture = ("Aucun critère n'a été instruit : il n'y a pas de "
                   "diagnostic, seulement un questionnaire. Répondre aux "
                   "treize constats prend une heure et remplace une "
                   "discussion d'opinion par un écart mesuré.")
    else:
        # LE MAILLON FAIBLE, PAS LA MOYENNE. Voir l'en-tête du module.
        global_n = min(a["niveau"] for a in instruits)
        bloquants = [a["nom"] for a in instruits if a["niveau"] == global_n]
        lecture = ("Maturité globale : %s (niveau %d sur %d) — c'est le "
                   "niveau de l'axe le plus faible, pas une moyenne. "
                   "Ce qui commande aujourd'hui : %s. Renforcer un autre axe "
                   "ne déplacera pas ce chiffre."
                   % (_niveau(global_n)["nom"], global_n, NIVEAU_MAX,
                      ", ".join(bloquants)))
        if not complet:
            reste = sum(len(a["manquants"]) for a in axes)
            lecture += (" %d critère%s non instruit%s : le résultat peut "
                        "encore baisser, jamais monter."
                        % (reste, "s" if reste > 1 else "",
                           "s" if reste > 1 else ""))

    # ── Ce que chaque famille de décision peut être instruite ────────────
    decisions = []
    for d in DECISIONS:
        niveaux = [a["niveau"] for a in axes
                   if a["cle"] in d["exige_axes"] and a["niveau"] is not None]
        n = min(niveaux) if niveaux else None
        couvert = [{"bloc": c["bloc"], "nom": BLOCS_ETUDE[c["bloc"]],
                    "apporte": c["apporte"], "disponible": dispo[c["bloc"]]}
                   for c in d["couvert_par"]]
        prets = [c for c in couvert if c["disponible"]]
        if n is None:
            verdict, dit = "non_instruit", (
                "Les axes qui conditionnent cette décision n'ont pas été "
                "renseignés.")
        elif n <= 0:
            verdict, dit = "non_instruisable", (
                "En l'état, cette décision se prendra sans appui analytique. "
                "L'étude apporte des chiffres ; il manque de quoi les "
                "confronter à la réalité de l'entreprise.")
        elif n == 1:
            verdict, dit = "fragile", (
                "Instruisable pour éclairer, pas pour engager : les éléments "
                "existent au coup par coup et ne se rejoueront pas à "
                "l'identique dans six mois.")
        elif n == 2:
            verdict, dit = "instruisable", (
                "Instruisable, à condition de nommer explicitement les zones "
                "non couvertes ci-dessous dans la note de décision.")
        else:
            verdict, dit = "pilotable", (
                "Instruisable ET suivable : l'organisation pourra constater "
                "l'écart entre la décision et son exécution.")
        decisions.append({
            "cle": d["cle"], "nom": d["nom"], "porte_sur": d["porte_sur"],
            "exige": d["exige"], "couvert_par": couvert,
            "apports_disponibles": len(prets), "apports_total": len(couvert),
            "hors_perimetre": d["hors_perimetre"],
            "axes_conditionnants": d["exige_axes"],
            "niveau": n, "verdict": verdict, "lecture": dit,
        })

    return {
        "version": VERSION,
        "axes": axes,
        "niveau_global": global_n,
        "niveau_global_nom": (_niveau(global_n)["nom"] if global_n is not None
                              else "non instruit"),
        "complet": complet,
        "lecture": lecture,
        "decisions": decisions,
        "actions": actions(axes),
        "reserve": "Ce diagnostic ne dit pas si l'investissement est bon : il "
                   "dit si l'organisation peut l'instruire. Les deux "
                   "questions sont distinctes, et confondre la seconde avec "
                   "la première est la façon la plus courante de valider un "
                   "mauvais dossier bien présenté.",
    }


def actions(axes):
    """Les actions prioritaires — hiérarchisées par EFFET sur la maturité
    globale, jamais par facilité.

    L'ordre est calculé, pas choisi : puisque le global est le minimum, seule
    la remontée du ou des axes les plus faibles le déplace. Une action sur un
    axe déjà au-dessus ne changera rien au chiffre — et le dire évite le
    plan d'actions qui améliore ce qui allait bien.
    """
    instruits = [a for a in axes if a["niveau"] is not None]
    out = []
    # D'abord, instruire ce qui ne l'est pas : sans constat, pas de priorité.
    for a in axes:
        if a["manquants"]:
            out.append({
                "axe": a["cle"], "axe_nom": a["nom"], "rang": 0,
                "quoi": "Instruire les %d critère%s non renseigné%s de cet axe."
                        % (len(a["manquants"]), "s" if len(a["manquants"]) > 1 else "",
                           "s" if len(a["manquants"]) > 1 else ""),
                "pourquoi": "Un axe non instruit ne peut ni être priorisé ni "
                            "être écarté : il laisse le diagnostic ouvert.",
                "effet": "aucun sur le chiffre — il le rend fiable",
            })
    if instruits:
        mini = min(a["niveau"] for a in instruits)
        for a in instruits:
            if a["niveau"] == mini:
                out.append({
                    "axe": a["cle"], "axe_nom": a["nom"], "rang": 1,
                    "quoi": "Porter cet axe au niveau %d (« %s ») : %s"
                            % (min(mini + 1, NIVEAU_MAX),
                               _niveau(min(mini + 1, NIVEAU_MAX))["nom"],
                               _niveau(min(mini + 1, NIVEAU_MAX))["constat"]),
                    "pourquoi": a["pourquoi"],
                    "effet": "DÉPLACE la maturité globale — c'est le maillon "
                             "faible",
                })
        for a in instruits:
            if a["niveau"] > mini:
                out.append({
                    "axe": a["cle"], "axe_nom": a["nom"], "rang": 2,
                    "quoi": "Maintenir — ne pas y investir avant que le "
                            "maillon faible ait remonté.",
                    "pourquoi": "Renforcer un axe déjà au-dessus du minimum "
                                "n'améliore pas la capacité à décider : le "
                                "goulet est ailleurs.",
                    "effet": "aucun sur le chiffre tant que le minimum n'a "
                             "pas bougé",
                })
    out.sort(key=lambda x: x["rang"])
    return out


# ═══════════════════════════════════════════════════════════════════════════
#  LA RESTITUTION AUX SPONSORS — dès le départ, surtout si elle déçoit
#
#  LA RÈGLE QUI COMMANDE CE BLOC. Un diagnostic décevant se présente AU
#  DÉBUT, pas quand le tableau de bord est livré. Recalibrer une ambition en
#  ouverture de projet est une conversation d'une heure ; expliquer six mois
#  plus tard pourquoi l'outil n'est pas utilisé est une conversation qu'on ne
#  gagne pas — et qui coûte la confiance sur les missions suivantes.
#
#  Le verdict passe donc EN TÊTE de la note, jamais en annexe, et il n'est
#  pas adouci : la fonction ne sait pas produire une version ménagée. C'est
#  délibéré — une restitution qui existe en deux versions finit toujours par
#  circuler dans la mauvaise.
# ═══════════════════════════════════════════════════════════════════════════

# Ce qu'on peut livrer À CHAQUE NIVEAU sans promettre l'impossible. C'est le
# cœur du recalibrage : à niveau 0, un tableau de bord temps réel sera
# abandonné au troisième mois — non par mauvaise volonté, mais parce que
# personne ne peut l'alimenter.
PROMETTABLE = {
    0: {"livrable": "Un état des lieux et un plan de collecte — pas de "
                    "tableau de bord.",
        "pourquoi": "Un outil de pilotage suppose une donnée qui arrive. "
                    "Ici, elle n'arrive pas encore : l'outil serait vide au "
                    "premier rafraîchissement, et c'est ainsi qu'on perd un "
                    "sponsor.",
        "eviter": "Promettre un tableau de bord temps réel, des alertes "
                  "automatiques ou un suivi mensuel."},
    1: {"livrable": "Un tableau de bord à MAIN LEVÉE, trimestriel, sur trois "
                    "à cinq indicateurs, alimenté par une procédure écrite.",
        "pourquoi": "Les éléments existent au coup par coup : on peut les "
                    "rassembler à cadence lente, à condition que quelqu'un "
                    "soit nommé pour le faire.",
        "eviter": "Promettre l'automatisation, le temps réel, ou un "
                  "périmètre large — chaque indicateur ajouté est une "
                  "collecte manuelle de plus."},
    2: {"livrable": "Un tableau de bord mensuel outillé, avec ses fiches "
                    "d'indicateur et ses seuils d'alerte.",
        "pourquoi": "La méthode existe et un responsable est nommé ; "
                    "l'irrégularité résiduelle se traite par le rythme et "
                    "les rappels.",
        "eviter": "Promettre un pilotage prédictif ou des comparaisons "
                  "externes que la collecte ne couvre pas."},
    3: {"livrable": "Un pilotage complet : suivi d'écart, analyse de "
                    "sensibilité, revue périodique et boucle de correction.",
        "pourquoi": "La donnée arrive, elle est datée et qualifiée, la "
                    "grille existe : l'organisation peut être tenue à ses "
                    "propres chiffres.",
        "eviter": "Croire que l'outil dispense de la revue : c'est elle qui "
                  "fait vivre le pilotage, pas l'inverse."},
}


def restitution_sponsors(diag, projet=""):
    """La note de restitution, à présenter aux sponsors AVANT d'engager.

    Elle porte le verdict en tête — y compris et surtout quand il déçoit —,
    dit ce qui est promettable à ce niveau, ce qui ne l'est pas encore, et à
    quelle condition précise l'ambition supérieure devient tenable.
    """
    if not diag:
        return ""
    n = diag.get("niveau_global")
    L = []
    A = L.append
    titre = "Diagnostic de maturité analytique — capacité à décider"
    A("# " + titre + (" · " + projet if projet else ""))
    A("")

    # ── 1. LE VERDICT, EN TÊTE ────────────────────────────────────────────
    A("## Ce que ce diagnostic conclut")
    A("")
    A(diag["lecture"])
    A("")
    if n is not None and n <= 1:
        A("**Cette conclusion est décevante, et c'est la raison de la "
          "présenter maintenant.** Recalibrer l'ambition en ouverture coûte "
          "une réunion ; livrer dans six mois un tableau de bord que "
          "personne n'alimente coûte le projet, et la confiance qui allait "
          "avec. Ce qui suit n'est pas un renoncement : c'est le périmètre "
          "sur lequel l'engagement peut être tenu.")
        A("")

    # ── 2. LE RECALIBRAGE ─────────────────────────────────────────────────
    if n is not None:
        p = PROMETTABLE[n]
        A("## Ce qui est promettable à ce niveau — et ce qui ne l'est pas")
        A("")
        A("**Livrable tenable aujourd'hui.** %s" % p["livrable"])
        A("")
        A("*Pourquoi celui-là.* %s" % p["pourquoi"])
        A("")
        A("**À NE PAS promettre en l'état.** %s" % p["eviter"])
        A("")
        if n < NIVEAU_MAX:
            suite = PROMETTABLE[n + 1]
            bloquants = [a["nom"] for a in diag["axes"]
                         if a["niveau"] == n]
            A("**Ce qui débloque le palier suivant.** Porter %s au niveau "
              "%d ouvre : %s"
              % (" et ".join(bloquants) or "l'axe le plus faible",
                 n + 1, suite["livrable"]))
            A("")

    # ── 3. AXE PAR AXE, SANS MOYENNE ──────────────────────────────────────
    A("## Où en est l'organisation, axe par axe")
    A("")
    A("| Axe | Niveau | Instruit | Ce qui bloque |")
    A("|---|---|---|---|")
    for a in diag["axes"]:
        bloque = ", ".join(a["faible"] or []) if a["niveau"] is not None else "—"
        A("| %s | %s | %d/%d | %s |"
          % (a["nom"],
             "non instruit" if a["niveau"] is None
             else "%d — %s" % (a["niveau"], a["niveau_nom"]),
             a["instruit"], a["total"], bloque))
    A("")
    A("*Le niveau global est le MINIMUM des axes, pas leur moyenne : on ne "
      "décide pas mieux que sa donnée la plus faible. Une moyenne aurait "
      "affiché un résultat plus flatteur et envoyé travailler ce qui tient "
      "déjà.*")
    A("")

    # ── 4. CE QUE CHAQUE DÉCISION PEUT ÊTRE INSTRUITE ─────────────────────
    A("## Ce que l'entreprise peut décider aujourd'hui")
    A("")
    for d in diag["decisions"]:
        A("### %s" % d["nom"])
        A("")
        A("*%s*" % d["porte_sur"])
        A("")
        A("**Verdict.** %s" % d["lecture"])
        A("")
        dispo = [c for c in d["couvert_par"] if c["disponible"]]
        if dispo:
            A("Ce que l'étude apporte déjà :")
            A("")
            for c in dispo:
                A("- **%s** — %s" % (c["nom"], c["apporte"]))
            A("")
        manquants = [c for c in d["couvert_par"] if not c["disponible"]]
        if manquants:
            A("Ce que l'étude apporterait, une fois calculé : %s."
              % ", ".join(c["nom"] for c in manquants))
            A("")
        A("Ce qui restera à instruire hors de cette étude :")
        A("")
        for h in d["hors_perimetre"]:
            A("- " + h)
        A("")

    # ── 5. LE PLAN, HIÉRARCHISÉ PAR EFFET ─────────────────────────────────
    A("## Le plan d'amélioration, hiérarchisé par effet")
    A("")
    for act in diag["actions"]:
        A("- **%s** — %s *(%s)*" % (act["axe_nom"], act["quoi"], act["effet"]))
    A("")
    A("*Les actions sont classées par EFFET sur la maturité globale, non par "
      "facilité : puisque le global est le minimum, seule la remontée du "
      "maillon faible le déplace.*")
    A("")

    A("---")
    A("")
    A("*%s Diagnostic déterministe — deux évaluations aux mêmes constats "
      "rendent le même résultat. maturite_decision v%s.*"
      % (diag["reserve"], diag["version"]))
    return "\n".join(L)


def referentiel():
    """Le cadre servi à l'interface — questions, échelle, familles."""
    return {"version": VERSION, "niveaux": NIVEAUX, "axes": AXES,
            "decisions": DECISIONS, "blocs_etude": BLOCS_ETUDE}


def sante():
    return {"module": "maturite_decision", "version": VERSION,
            "axes": len(AXES),
            "criteres": sum(len(a["criteres"]) for a in AXES),
            "decisions": len(DECISIONS),
            "problemes": _verifier()}
