# -*- coding: utf-8 -*-
"""Gouvernance IA opérationnelle — comité, circuit de validation, indicateurs.

CE QUE CE MODULE AJOUTE, ET CE QU'IL N'AJOUTE PAS
Sentinel porte déjà une matrice RACI complète (18 rôles, 16 processus, variantes
sectorielles) dans « Parties prenantes ». Ce module ne la duplique pas : il la
prolonge là où elle s'arrête. Une matrice dit QUI ferait quoi ; elle ne dit ni
quand le comité se réunit, ni ce qu'il a le droit de trancher, ni par quel
chemin passe un nouvel usage avant d'exister.

Trois objets, donc :
  LE COMITÉ      — composition type, décisions qui lui sont réservées, cadence.
                   Un comité sans décisions réservées ne gouverne pas, il informe.
  LE CIRCUIT     — le chemin d'un nouvel usage, de la demande à la mise en
                   production, avec la QUALIFICATION AI ACT AU POINT D'ENTRÉE :
                   c'est elle qui détermine la lourdeur du reste. Qualifier à la
                   fin, c'est découvrir après coup qu'on a construit un système
                   à haut risque sans les obligations qui vont avec.
  LES INDICATEURS— ce que le comité regarde. Chacun porte sa cible, son seuil
                   d'alerte, sa source et son SENS DE LECTURE — un indicateur
                   dont on ignore s'il doit monter ou descendre ne sert à rien.

LA DISCIPLINE DE CE FICHIER
La qualification rendue ici est une qualification PRÉSUMÉE, calculée depuis des
réponses déclaratives. Elle oriente le circuit ; elle ne remplace pas l'analyse
juridique, et le module le dit à l'utilisateur plutôt que de le laisser croire
le contraire.
"""
from datetime import datetime, timezone

VERSION = "2026-07-a"

# ═══════════════════════════════════════════════════════════════════════════
# 1. LE COMITÉ DE GOUVERNANCE IA
# ═══════════════════════════════════════════════════════════════════════════

COMITE = {
    "mandat": (
        "Le comité de gouvernance IA arbitre les usages de l'intelligence "
        "artificielle dans l'organisation : il autorise ou refuse un nouvel "
        "usage, tranche les arbitrages entre valeur métier et exposition, et "
        "suspend un système dont le suivi révèle une dérive."),
    "cadence": "trimestrielle, avec séance extraordinaire sur demande motivée",
    "quorum": (
        "Direction, Conformité/Risque et Métiers doivent être représentés. "
        "Sans l'un des trois, la séance informe mais ne décide pas."),
    "membres": [
        {"fonction": "Direction générale", "voix": "décisionnaire",
         "role": "Orientation stratégique IA, arbitrage final"},
        {"fonction": "Métiers", "voix": "décisionnaire",
         "role": "Validation de la valeur d'usage et de l'appropriation"},
        {"fonction": "IT / Architecture", "voix": "décisionnaire",
         "role": "Faisabilité, architecture, sécurité technique"},
        {"fonction": "Conformité / Risque", "voix": "décisionnaire",
         "role": "Contrôle réglementaire et éthique, veto motivé"},
        {"fonction": "Juridique", "voix": "consultative",
         "role": "Qualification réglementaire, contrats, responsabilité"},
        {"fonction": "DPO", "voix": "consultative",
         "role": "Protection des données, nécessité d'une AIPD"},
        {"fonction": "Cybersécurité", "voix": "consultative",
         "role": "Exposition, sécurité des données et du modèle"},
        {"fonction": "Représentation des utilisateurs", "voix": "consultative",
         "role": "Conditions réelles d'usage, contournements observés"},
    ],
    # Ce qui distingue un comité qui gouverne d'un comité qui assiste.
    "decisions_reservees": [
        "autoriser la mise en production d'un système d'IA à haut risque",
        "autoriser un usage traitant des données personnelles sensibles",
        "valider la politique interne d'usage de l'IA et ses révisions",
        "arbitrer un désaccord entre valeur métier et exposition réglementaire",
        "suspendre ou retirer un système en exploitation",
        "accepter formellement un risque résiduel, avec sa justification écrite",
        "autoriser un usage porté par un tiers sur les données de l'organisation",
    ],
    "hors_perimetre": [
        "le choix technique d'un modèle ou d'un fournisseur (IT, sur cahier des charges)",
        "l'opportunité métier d'un cas d'usage (métiers, avant saisine)",
        "les décisions de sûreté ou de sécurité des personnes (instances dédiées)",
    ],
}

# ═══════════════════════════════════════════════════════════════════════════
# 2. LE CIRCUIT DE VALIDATION D'UN NOUVEL USAGE
#    Chaque étape porte QUI décide et ce qui ne peut pas être sauté.
# ═══════════════════════════════════════════════════════════════════════════

CIRCUIT = [
    {"cle": "demande", "nom": "Demande & description de l'usage",
     "qui": "Métier demandeur",
     "quoi": "Finalité, population concernée, données envisagées, gain attendu. "
             "Une demande sans finalité écrite n'est pas instruite.",
     "sortie": "fiche d'usage"},
    {"cle": "qualification", "nom": "Qualification réglementaire",
     "qui": "Conformité / Juridique",
     "quoi": "Classe AI Act présumée, nécessité d'une AIPD ou d'une FRIA, "
             "obligations de transparence (art. 50). C'est ICI que se décide la "
             "lourdeur de tout le reste — jamais à la fin.",
     "sortie": "classe présumée & obligations"},
    {"cle": "instruction", "nom": "Instruction technique & sécurité",
     "qui": "IT, Cybersécurité, DPO",
     "quoi": "Données réellement nécessaires, hébergement, exposition, "
             "supervision humaine prévue, journalisation.",
     "sortie": "avis technique motivé"},
    {"cle": "decision", "nom": "Décision",
     "qui": "Comité de gouvernance IA (ou délégation selon la classe)",
     "quoi": "Autorisation, autorisation sous conditions, ajournement ou refus. "
             "Toute décision est motivée et tracée, y compris le refus.",
     "sortie": "décision tracée"},
    {"cle": "mise_en_prod", "nom": "Mise en production encadrée",
     "qui": "IT & métier",
     "quoi": "Conditions de la décision mises en œuvre, inscription au registre "
             "des systèmes IA, information des utilisateurs.",
     "sortie": "inscription au registre"},
    {"cle": "suivi", "nom": "Suivi & revue",
     "qui": "Responsable de l'usage",
     "quoi": "Indicateurs de performance et de dérive, incidents, revue "
             "périodique dont la fréquence dépend de la classe.",
     "sortie": "revue périodique"},
]

# Voies allégées : tout ne mérite pas le circuit complet, et prétendre le
# contraire fait naître le contournement — c'est-à-dire le shadow AI.
VOIES = {
    "complete": {"nom": "Circuit complet", "etapes": [c["cle"] for c in CIRCUIT],
                 "decideur": "Comité de gouvernance IA",
                 "quand": "haut risque présumé, données sensibles, ou usage porté par un tiers"},
    "allegee": {"nom": "Voie allégée", "etapes": ["demande", "qualification", "instruction", "decision", "suivi"],
                "decideur": "Conformité + métier, comité informé",
                "quand": "risque limité, données non sensibles, périmètre restreint"},
    "declaration": {"nom": "Simple déclaration", "etapes": ["demande", "qualification"],
                    "decideur": "Responsable IA, enregistrement au registre",
                    "quand": "usage bureautique d'un outil déjà autorisé, sans donnée sensible"},
}

# ═══════════════════════════════════════════════════════════════════════════
# 3. QUALIFICATION PRÉSUMÉE AU POINT D'ENTRÉE
#    Sept questions fermées. Le résultat ORIENTE le circuit ; il ne conclut pas
#    en droit, et la sortie le dit explicitement.
# ═══════════════════════════════════════════════════════════════════════════

QUESTIONS = [
    {"cle": "interdit", "texte": "L'usage relève-t-il d'une pratique interdite (notation sociale, "
                                 "manipulation, reconnaissance des émotions au travail, police prédictive) ?",
     "poids": "bloquant"},
    {"cle": "annexe3", "texte": "L'usage touche-t-il un domaine de l'annexe III (emploi, éducation, "
                                "crédit, services essentiels, migration, justice, biométrie, infrastructures critiques) ?",
     "poids": "haut"},
    {"cle": "decision_personne", "texte": "Le système produit-il une décision ou une évaluation "
                                          "concernant une personne ?", "poids": "haut"},
    {"cle": "sensibles", "texte": "Traite-t-il des données personnelles sensibles (santé, biométrie, "
                                  "opinions, appartenance syndicale) ?", "poids": "haut"},
    {"cle": "interaction", "texte": "Interagit-il directement avec des personnes, ou génère-t-il du "
                                    "contenu diffusé ?", "poids": "transparence"},
    {"cle": "tiers", "texte": "L'usage est-il opéré par un tiers, ou repose-t-il sur un modèle "
                              "fourni par un tiers ?", "poids": "tiers"},
    {"cle": "personnelles", "texte": "Traite-t-il des données personnelles (même non sensibles) ?",
     "poids": "rgpd"},
]

CLASSES = {
    "interdit": {"nom": "Pratique interdite (présumée)", "rang": 1, "couleur": "#B83222",
                 "sens": "L'usage ne peut pas être autorisé en l'état — arrêt immédiat de l'instruction."},
    "haut": {"nom": "Haut risque (présumé)", "rang": 2, "couleur": "#C4501A",
             "sens": "Obligations lourdes : gestion des risques, qualité des données, documentation "
                     "technique, journalisation, supervision humaine, information des utilisateurs."},
    "limite": {"nom": "Risque limité — transparence (présumé)", "rang": 3, "couleur": "#C47C1A",
               "sens": "Obligation d'informer les personnes qu'elles interagissent avec une IA et de "
                       "marquer les contenus générés (art. 50)."},
    "minimal": {"nom": "Risque minimal (présumé)", "rang": 4, "couleur": "#2D7A47",
                "sens": "Pas d'obligation spécifique au titre de l'AI Act ; le RGPD et la sécurité "
                        "s'appliquent si des données personnelles sont traitées."},
}


def qualifier(reponses):
    """Qualification PRÉSUMÉE depuis les réponses déclaratives.

    `reponses` : dict clé -> bool. Rend la classe, la voie applicable, les
    obligations déclenchées et les réserves — toujours les réserves."""
    r = {q["cle"]: bool(reponses.get(q["cle"])) for q in QUESTIONS}

    if r["interdit"]:
        classe = "interdit"
    elif r["annexe3"] or (r["decision_personne"] and r["sensibles"]):
        classe = "haut"
    elif r["interaction"]:
        classe = "limite"
    else:
        classe = "minimal"

    if classe in ("interdit", "haut") or r["sensibles"] or r["tiers"]:
        voie = "complete"
    elif classe == "limite" or r["personnelles"]:
        voie = "allegee"
    else:
        voie = "declaration"

    obligations = []
    if classe == "haut":
        obligations += [
            "système de gestion des risques (art. 9)",
            "gouvernance des données d'entraînement et de test (art. 10)",
            "documentation technique & journalisation (art. 11-12)",
            "supervision humaine effective (art. 14)",
            "information des utilisateurs & notice d'emploi (art. 13)",
            "inscription au registre des systèmes IA",
        ]
    if r["interaction"]:
        obligations.append("transparence : informer qu'il s'agit d'une IA, marquer les contenus (art. 50)")
    if r["personnelles"] or r["sensibles"]:
        obligations.append("base légale, minimisation, information et droits des personnes (RGPD)")
    if r["sensibles"] or classe == "haut":
        obligations.append("analyse d'impact (AIPD, et FRIA si l'organisme y est soumis)")
    if r["tiers"]:
        obligations.append("encadrement contractuel du tiers : responsabilités, données, réversibilité")
    if classe == "interdit":
        obligations = ["aucune : l'usage relève d'une pratique prohibée — ne pas poursuivre en l'état"]

    return {
        "classe": classe,
        "classe_nom": CLASSES[classe]["nom"],
        "classe_sens": CLASSES[classe]["sens"],
        "couleur": CLASSES[classe]["couleur"],
        "voie": voie,
        "voie_nom": VOIES[voie]["nom"],
        "decideur": VOIES[voie]["decideur"],
        "etapes": VOIES[voie]["etapes"],
        "obligations": obligations,
        "reserve": (
            "Qualification PRÉSUMÉE, calculée depuis des réponses déclaratives. Elle "
            "oriente le circuit et ne vaut pas analyse juridique : la classification "
            "définitive relève du juriste, sur le système réel et sa documentation."),
    }


# ═══════════════════════════════════════════════════════════════════════════
# 4. LES INDICATEURS DE GOUVERNANCE
#    Chacun porte son sens de lecture : sans lui, un chiffre n'informe pas.
# ═══════════════════════════════════════════════════════════════════════════

INDICATEURS = [
    {"cle": "usages_declares", "nom": "Usages déclarés au registre",
     "famille": "Couverture", "sens": "hausse", "cible": "100 % des usages connus",
     "lecture": "Un registre incomplet rend toutes les autres mesures fausses.",
     "source": "Registre des systèmes IA"},
    {"cle": "part_qualifies", "nom": "Part des usages qualifiés AI Act",
     "famille": "Couverture", "sens": "hausse", "cible": "100 %",
     "lecture": "Un usage non qualifié est un usage dont on ignore les obligations.",
     "source": "Circuit de validation"},
    {"cle": "delai_decision", "nom": "Délai moyen de décision (jours)",
     "famille": "Fluidité", "sens": "baisse", "cible": "< 30 jours",
     "lecture": "Un circuit lent se contourne. Ce chiffre mesure le risque de shadow AI "
                "autant que l'efficacité du comité.",
     "source": "Circuit de validation"},
    {"cle": "en_attente", "nom": "Demandes en attente de décision",
     "famille": "Fluidité", "sens": "baisse", "cible": "aucune au-delà d'un trimestre",
     "lecture": "Une file qui s'allonge annonce des mises en production hors circuit.",
     "source": "Circuit de validation"},
    {"cle": "haut_risque", "nom": "Systèmes à haut risque en exploitation",
     "famille": "Exposition", "sens": "surveiller", "cible": "connu et documenté",
     "lecture": "Le nombre importe moins que la certitude de les avoir tous identifiés.",
     "source": "Registre + qualification"},
    {"cle": "refus", "nom": "Demandes refusées ou ajournées",
     "famille": "Exposition", "sens": "surveiller", "cible": "non nul",
     "lecture": "Un comité qui n'a jamais rien refusé ne décide pas : il enregistre.",
     "source": "Circuit de validation"},
    {"cle": "revues_a_jour", "nom": "Revues périodiques à jour",
     "famille": "Exploitation", "sens": "hausse", "cible": "100 %",
     "lecture": "Une revue en retard sur un système à haut risque est un écart de conformité.",
     "source": "Suivi des systèmes"},
    {"cle": "sensibilisation", "nom": "Collaborateurs sensibilisés",
     "famille": "Humain", "sens": "hausse", "cible": "> 90 % des populations exposées",
     "lecture": "La politique d'usage ne produit d'effet que si elle est connue.",
     "source": "Formation"},
]

STATUTS_DEMANDE = {
    "brouillon": {"nom": "Brouillon", "rang": 1, "couleur": "#8892A0"},
    "qualifie": {"nom": "Qualifié", "rang": 2, "couleur": "#1C5CAB"},
    "instruction": {"nom": "En instruction", "rang": 3, "couleur": "#C47C1A"},
    "autorise": {"nom": "Autorisé", "rang": 4, "couleur": "#2D7A47"},
    "conditions": {"nom": "Autorisé sous conditions", "rang": 5, "couleur": "#2D7A47"},
    "ajourne": {"nom": "Ajourné", "rang": 6, "couleur": "#C4501A"},
    "refuse": {"nom": "Refusé", "rang": 7, "couleur": "#B83222"},
}


def tableau_bord(demandes):
    """Calcule les indicateurs depuis la file réelle des demandes.

    Ne rend JAMAIS un indicateur qu'on ne sait pas calculer : une case vide est
    honnête, une valeur inventée ne l'est pas."""
    d = list(demandes or [])
    n = len(d)
    decidees = [x for x in d if x.get("statut") in ("autorise", "conditions", "refuse")]
    attente = [x for x in d if x.get("statut") in ("brouillon", "qualifie", "instruction")]
    qualifiees = [x for x in d if x.get("classe")]
    refus = [x for x in d if x.get("statut") in ("refuse", "ajourne")]
    haut = [x for x in d if x.get("classe") == "haut"
            and x.get("statut") in ("autorise", "conditions")]

    delais = []
    for x in decidees:
        try:
            a = datetime.fromisoformat(str(x.get("cree_le"))[:19])
            b = datetime.fromisoformat(str(x.get("decide_le"))[:19])
            delais.append((b - a).days)
        except Exception:                                      # noqa: BLE001
            continue

    valeurs = {
        "usages_declares": {"valeur": n, "unite": "demande(s)"},
        "part_qualifies": {"valeur": (round(100.0 * len(qualifiees) / n) if n else None),
                           "unite": "%"},
        "delai_decision": {"valeur": (round(sum(delais) / len(delais)) if delais else None),
                           "unite": "jours"},
        "en_attente": {"valeur": len(attente), "unite": "demande(s)"},
        "haut_risque": {"valeur": len(haut), "unite": "système(s)"},
        "refus": {"valeur": len(refus), "unite": "demande(s)"},
        "revues_a_jour": {"valeur": None, "unite": "%"},
        "sensibilisation": {"valeur": None, "unite": "%"},
    }
    lignes = []
    for ind in INDICATEURS:
        v = valeurs.get(ind["cle"], {})
        lignes.append(dict(ind, valeur=v.get("valeur"), unite=v.get("unite"),
                           mesure=(v.get("valeur") is not None)))
    return {
        "indicateurs": lignes,
        "total": n,
        "note": ("Les indicateurs sans valeur ne sont pas à zéro : ils ne sont pas "
                 "encore mesurés. Les revues et la sensibilisation se renseignent "
                 "hors de ce module."),
    }


def referentiel():
    """Tout ce dont l'interface a besoin, en une réponse."""
    return {
        "version": VERSION,
        "genere": datetime.now(timezone.utc).isoformat(),
        "comite": COMITE,
        "circuit": CIRCUIT,
        "voies": VOIES,
        "questions": QUESTIONS,
        "classes": CLASSES,
        "indicateurs": INDICATEURS,
        "statuts": STATUTS_DEMANDE,
        "raci_ailleurs": (
            "La matrice RACI détaillée — 18 rôles, 16 processus, variantes "
            "sectorielles — est portée par le module « Parties prenantes ». Ce "
            "module ne la duplique pas : il en applique les rôles au comité et au "
            "circuit."),
    }


def sante():
    pb = []
    cles_circuit = {c["cle"] for c in CIRCUIT}
    for v, spec in VOIES.items():
        for e in spec["etapes"]:
            if e not in cles_circuit:
                pb.append("voie %s : étape inconnue %s" % (v, e))
    for q in QUESTIONS:
        if not q.get("texte") or not q.get("cle"):
            pb.append("question incomplète")
    for i in INDICATEURS:
        if i["sens"] not in ("hausse", "baisse", "surveiller"):
            pb.append("indicateur %s : sens inconnu" % i["cle"])
        if not i.get("lecture"):
            pb.append("indicateur %s : sens de lecture manquant" % i["cle"])
    # Une qualification doit rendre une classe connue pour toute combinaison.
    import itertools
    for combo in itertools.product([False, True], repeat=len(QUESTIONS)):
        rep = {q["cle"]: c for q, c in zip(QUESTIONS, combo)}
        out = qualifier(rep)
        if out["classe"] not in CLASSES or out["voie"] not in VOIES:
            pb.append("qualification incohérente pour %s" % rep)
            break
    return {"ok": not pb, "problemes": pb, "version": VERSION,
            "membres": len(COMITE["membres"]),
            "decisions_reservees": len(COMITE["decisions_reservees"]),
            "etapes": len(CIRCUIT), "voies": len(VOIES),
            "questions": len(QUESTIONS), "indicateurs": len(INDICATEURS)}
