"""Observatoire R&D IA — données sourcées sur la recherche et le développement en IA.

Module AUTONOME (aucun import Flask) consommé par app.py pour la page /observatoire
et l'API /api/observatoire. Il ne dépend que de la bibliothèque standard, de
`requests` et de `feedparser` — déjà présents dans requirements.txt.

── Philosophie (même découpage que juridique.py) ──────────────────────────────
  1. CE QUI EST CERTAIN — le SEED : données recomposées depuis les sources
     primaires publiques (Epoch AI, MacroPolo/NeurIPS, AI Index/CSET, Eurostat,
     textes officiels UE). Chaque série porte sa source, sa licence, sa date et
     sa PRÉCISION ("exact", "classe", "lecture graphique (±)") : un chiffre dont
     on ne sait pas dire d'où il vient et à quel près n'a pas sa place ici.
  2. CE QUI SE DÉDUIT — les fetcheurs et agrégations : cumul de modèles par
     pays depuis le CSV Epoch, dernière année Eurostat, tri des flux. Calculs
     déterministes, reproductibles, sans IA.
  3. CE QUI S'INTERPRÈTE — rien : ce module ne fait AUCUN appel à un modèle de
     langage. Les seules « lectures stratégiques » affichées sont des phrases
     figées dans le SEED, rattachées à leurs chiffres sources.

── Droit d'auteur ─────────────────────────────────────────────────────────────
La carte « Recherche et développement dans le domaine de l'IA » (Carto n°89,
2025 © Areion/Capri) a inspiré le choix des volets : elle n'est PAS reproduite.
Chaque vue est recomposée depuis les sources primaires publiques, avec les
crédits obligatoires en clair (SEED['credits']) et la mention d'inspiration.

── RGPD ───────────────────────────────────────────────────────────────────────
Aucune donnée personnelle ne transite par ce module : les fetcheurs consultent
des sources statistiques et des flux publics, sans identifiant, sans cookie,
sans saisie utilisateur transmise. Rien à déclarer au registre des traitements ;
la minimisation (_minimiser d'app.py) est sans objet ici.

── Intégration app.py (pour mémoire) ──────────────────────────────────────────
  - page   : ajouter '/observatoire': 'observatoire.html' dans PAGES (la boucle
    add_url_rule crée la route avec rate-limit, cache mémoire et gzip) ;
  - API    : @app.route('/api/observatoire') + @rate_limit(60/60) qui renvoie
    jsonify(observatoire_ia.assemble()) — le cache est DANS ce module ;
  - santé  : bloc data['observatoire'] = observatoire_ia.sante() dans /api/health.

Mode hors-ligne : OBS_OFFLINE=1 → aucun réseau, seed pur (tests, premier rendu).
"""

import csv
import html as _html
import io
import json
import os
import threading
import time
from datetime import datetime

import requests
import feedparser

# Version du seed : à incrémenter à chaque mise à jour des données figées.
VERSION_SEED = "2026.07"

# ── Réseau : règles communes à tous les fetcheurs ──
# Jamais d'identifiant, jamais de cookie, User-Agent explicite, timeout court.
UA = {"User-Agent": "Sentinel-Observatoire/1.0"}
TIMEOUT_FLUX = 6        # flux RSS (aligné sur la veille)
TIMEOUT_API = 10        # API Eurostat
TIMEOUT_CSV = 15        # CSV Epoch (quelques Mo)
EPOCH_MAX_OCTETS = 15 * 1024 * 1024  # plafond de téléchargement du CSV (15 Mo)

# ── Cadence de rafraîchissement (TTL, en secondes) ──
# Epoch et Eurostat évoluent à la semaine ; les flux à la demi-heure (VEILLE_TTL).
OBS_TTL = {
    "epoch": 7 * 86400,
    "eurostat": 7 * 86400,
    "flux": 1800,
}
OBS_RETRY = 300  # après un échec, pas de nouvel essai avant 5 min (anti-martèlement)


# ═══════════════════════════════════════════════════════════════════════════
# 1. CRÉDITS OBLIGATOIRES — licences des sources, affichés en clair
# ═══════════════════════════════════════════════════════════════════════════

CREDIT_EPOCH = "Epoch AI, “Data on Notable AI Models”, epoch.ai — CC BY 4.0"
CREDIT_EUROSTAT = "Source : Eurostat (isoc_eb_ai) — CC BY 4.0"
CREDIT_MACROPOLO = ("MacroPolo, The Global AI Talent Tracker 2.0, Paulson Institute — "
                    "analyse des auteurs NeurIPS 2022")
CREDIT_AI_INDEX = ("AI Index Report 2025, AI Index Steering Committee, Institute for "
                   "Human-Centered AI (HAI), Stanford University — données brevets : "
                   "CSET, Georgetown University")
CREDIT_UE = "© Union européenne — réutilisation : Décision 2011/833/UE"
CREDIT_CARTO = ("inspiration : Carto n°89, 2025 © Areion/Capri — aucune reproduction "
                "de la carte, vues recomposées depuis les sources primaires")


# ═══════════════════════════════════════════════════════════════════════════
# 2. SEED — données figées, sourcées, datées ; jamais générées
# ═══════════════════════════════════════════════════════════════════════════
#
# Chaque volet porte : source, licence, date, precision, credit.
# Valeurs de `precision` :
#   "exact"                    — chiffre publié tel quel par la source
#   "classe"                   — intervalle publié (légende de carte)
#   "classe (lecture de carte)"— intervalle déduit de la lecture de la carte
#   "lecture graphique (±…)"   — valeur relevée sur un graphique, marge indiquée
SEED = {

    # ── Modèles d'IA remarquables créés 2003–été 2024, cumul par pays ──────
    # Le seed stocke les CLASSES ; en production le fetcher Epoch les remplace
    # par les comptes exacts (mode "live", precision "exact").
    "modeles": {
        "titre": "Modèles d'IA remarquables — cumul par pays",
        "source": "Epoch AI — Notable AI Models",
        "licence": "CC BY 4.0",
        "date": "2003 – été 2024",
        "precision": "classe",
        "credit": CREDIT_EPOCH,
        "classes": ["1-10", "11-20", "21-60", "61-100", "101-560"],
        "pays": {
            # Classes publiées dans la légende (précision "classe")
            "États-Unis":  {"classe": "101-560", "precision": "classe"},
            "Chine":       {"classe": "101-560", "precision": "classe"},
            "Canada":      {"classe": "61-100",  "precision": "classe"},
            "Royaume-Uni": {"classe": "21-60",   "precision": "classe"},
            "Allemagne":   {"classe": "21-60",   "precision": "classe"},
            "France":      {"classe": "21-60",   "precision": "classe"},
            # Classes déduites de la lecture de la carte
            "Russie":       {"classe": "11-20", "precision": "classe (lecture de carte)"},
            "Japon":        {"classe": "11-20", "precision": "classe (lecture de carte)"},
            "Corée du Sud": {"classe": "11-20", "precision": "classe (lecture de carte)"},
            "Israël":       {"classe": "11-20", "precision": "classe (lecture de carte)"},
            "Inde":         {"classe": "11-20", "precision": "classe (lecture de carte)"},
            "Suède":        {"classe": "1-10", "precision": "classe (lecture de carte)"},
            "Norvège":      {"classe": "1-10", "precision": "classe (lecture de carte)"},
            "Finlande":     {"classe": "1-10", "precision": "classe (lecture de carte)"},
            "Pays-Bas":     {"classe": "1-10", "precision": "classe (lecture de carte)"},
            "Belgique":     {"classe": "1-10", "precision": "classe (lecture de carte)"},
            "Irlande":      {"classe": "1-10", "precision": "classe (lecture de carte)"},
            "Espagne":      {"classe": "1-10", "precision": "classe (lecture de carte)"},
            "Suisse":       {"classe": "1-10", "precision": "classe (lecture de carte)"},
            "Italie":       {"classe": "1-10", "precision": "classe (lecture de carte)"},
            "Pologne":      {"classe": "1-10", "precision": "classe (lecture de carte)"},
            "Rép. tchèque": {"classe": "1-10", "precision": "classe (lecture de carte)"},
            "Autriche":     {"classe": "1-10", "precision": "classe (lecture de carte)"},
            "Iran":         {"classe": "1-10", "precision": "classe (lecture de carte)"},
            "Arabie saoudite":      {"classe": "1-10", "precision": "classe (lecture de carte)"},
            "Émirats arabes unis":  {"classe": "1-10", "precision": "classe (lecture de carte)"},
            "Australie":    {"classe": "1-10", "precision": "classe (lecture de carte)"},
            "Argentine":    {"classe": "1-10", "precision": "classe (lecture de carte)"},
        },
        "note": "Classes de la carte Carto n°89 ; remplacées par les comptes exacts "
                "du CSV Epoch AI dès que le fetcher a répondu (mode live).",
    },

    # ── Chercheurs d'élite en IA, 2022 (MacroPolo / NeurIPS) ───────────────
    "talents": {
        "titre": "Chercheurs d'élite en IA (2022)",
        "definition": "Auteurs d'articles retenus pour présentation ORALE à NeurIPS 2022 "
                      "(~top 2 % des publications) — N.B. de la carte.",
        "source": "MacroPolo — Global AI Talent Tracker 2.0, d'après NeurIPS 2022",
        "licence": "© MacroPolo / Paulson Institute — citation avec crédit exact",
        "date": "2022",
        "precision": "exact (pourcentages publiés) ; lieu de travail hors États-Unis/Chine : "
                     "lecture graphique",
        "credit": CREDIT_MACROPOLO,
        # ARCHIVÉ sciemment : think tank dissous en 2024, site à risque de disparition.
        "origine_pct": {
            "États-Unis": 28, "Chine": 26, "Autres": 28, "Inde": 7,
            "France": 5, "Allemagne": 4, "Canada": 2,
        },  # somme = 100
        "lieu_travail_pct": {"États-Unis": 57, "Chine": 12, "Autres": 31},
        "note_lieu_travail": "La carte montre aussi Royaume-Uni, Allemagne, France et "
                             "Canada entre 2 et 4 % chacun (lecture graphique) — valeurs "
                             "précises non publiées, comptées dans « Autres ».",
        "lecture": "Les États-Unis forment 28 % des chercheurs d'élite mais en emploient "
                   "57 % — attraction nette ; la Chine en forme 26 % et n'en emploie que "
                   "12 % — exportatrice nette de talents.",
    },

    # ── Brevets d'IA accordés — part du total mondial (%) ──────────────────
    "brevets": {
        "titre": "Brevets d'IA accordés — part du total mondial (%)",
        "source": "AI Index (Stanford HAI) — données CSET, Georgetown University",
        "licence": "CC BY-ND 4.0 (rapport) — citation avec crédit exact",
        "date": "2010-2023",
        "precision": "points 2023 exacts ; séries 2010-2023 : lecture graphique (±3 pts)",
        "credit": CREDIT_AI_INDEX,
        # Points 2023 affichés sur la carte : EXACTS.
        "points_2023": {"Chine": 69.7, "États-Unis": 14.2, "Europe": 2.8},
        "parts_pct": {
            "Chine":      {"2010": 13, "2012": 15, "2014": 18, "2016": 30,
                           "2018": 42, "2020": 55, "2022": 64, "2023": 69.7},
            "États-Unis": {"2010": 40, "2012": 38, "2014": 37, "2016": 33,
                           "2018": 27, "2020": 21, "2022": 16, "2023": 14.2},
            "Europe":     {"2010": 8, "2012": 7, "2014": 6, "2016": 5,
                           "2018": 4.5, "2020": 3.8, "2022": 3.1, "2023": 2.8},
        },
        "precision_parts": "lecture graphique (±3 pts), sauf points 2023 (exacts)",
        "volume_mondial_milliers": {
            "2010": 2, "2012": 3, "2014": 5, "2016": 8, "2018": 15,
            "2020": 40, "2021": 62, "2022": 95, "2023": 122,
        },
        "precision_volume": "lecture graphique",
    },

    # ── Adoption de l'IA par les entreprises UE (Eurostat) ─────────────────
    # Seed MINIMAL : le fetcher Eurostat fournit le détail par pays en production.
    "adoption_ue": {
        "titre": "Adoption de l'IA par les entreprises (UE)",
        "source": "Eurostat — isoc_eb_ai (enquête TIC entreprises)",
        "licence": "CC BY 4.0",
        "date": "2024",
        "precision": "≈, à confirmer par le flux",
        "credit": CREDIT_EUROSTAT,
        "annee": "2024",
        "valeurs": {"UE-27": 13.5},  # % d'entreprises utilisant l'IA
        "note": "Seed minimal ; remplacé par le détail par pays de l'API Eurostat "
                "dès que le fetcher a répondu (mode live).",
    },

    # ── Gouvernance & stratégie UE — référentiel fermé, vérifié ────────────
    "gouvernance": {
        "titre": "Gouvernance & stratégie IA de l'Union européenne",
        "source": "Textes et pages officiels (EUR-Lex, Commission européenne)",
        "licence": CREDIT_UE,
        "date": "2018-2024",
        "precision": "exact",
        "credit": CREDIT_UE,
        "entrees": [
            {
                "titre": "Règlement (UE) 2024/1689 (AI Act) et Bureau de l'IA (AI Office)",
                "annee": "2024",
                "lien": "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32024R1689",
                "liens_annexes": ["https://digital-strategy.ec.europa.eu/en/policies/ai-office"],
                "usage": "Point d'entrée réglementaire : classifier chaque système d'IA par "
                         "niveau de risque et caler la mise en conformité sur le calendrier "
                         "2025-2027 ; le Bureau de l'IA supervise les modèles à usage général.",
            },
            {
                "titre": "AI HLEG — Lignes directrices en matière d'éthique pour une IA "
                         "digne de confiance (2019) et liste d'évaluation ALTAI (2020)",
                "annee": "2019 / 2020",
                "lien": "https://digital-strategy.ec.europa.eu/en/library/ethics-guidelines-trustworthy-ai",
                "liens_annexes": ["https://digital-strategy.ec.europa.eu/en/library/"
                                  "assessment-list-trustworthy-artificial-intelligence-altai-self-assessment"],
                "usage": "Grille d'auto-évaluation éthique antérieure à l'AI Act : les sept "
                         "exigences et la liste ALTAI structurent un audit interne avant "
                         "d'engager la mise en conformité réglementaire.",
            },
            {
                "titre": "Alliance européenne pour l'IA (plateforme Futurium de la Commission)",
                "annee": "2018",
                "lien": "https://futurium.ec.europa.eu/en/european-ai-alliance",
                "usage": "Canal de consultation de la Commission : suivre les appels à "
                         "contributions pour anticiper actes d'exécution et codes de bonne "
                         "pratique avant leur adoption.",
            },
            {
                "titre": "Plan coordonné dans le domaine de l'IA (2018, révisé 2021)",
                "annee": "2018, révisé 2021",
                "lien": "https://digital-strategy.ec.europa.eu/en/policies/plan-ai",
                "usage": "Cadre des financements et priorités des États membres : situe les "
                         "dispositifs mobilisables par un client (GenAI4EU, pôles européens "
                         "d'innovation numérique).",
            },
            {
                "titre": "AI Watch (JRC) — suivi de l'IA par la Commission",
                "annee": "2018",
                "lien": "https://ai-watch.ec.europa.eu/",
                "usage": "Indicateurs de référence UE (adoption, investissements, talents) "
                         "pour objectiver un dossier de conformité ou un comparatif sectoriel.",
            },
        ],
    },

    # ── Crédits obligatoires, affichés en clair sur la page ────────────────
    "credits": [
        CREDIT_EPOCH,
        CREDIT_EUROSTAT,
        CREDIT_MACROPOLO,
        CREDIT_AI_INDEX,
        CREDIT_UE,
        CREDIT_CARTO,
    ],
}


# ═══════════════════════════════════════════════════════════════════════════
# 3. CATALOGUE DES SOURCES — ce qui alimente (ou alimentera) l'observatoire
# ═══════════════════════════════════════════════════════════════════════════
# `automatisable` = consommable par un fetcher en production ; les autres sont
# des références à revue manuelle (cadence indiquée). Champ `role` : à quoi
# sert la source dans l'observatoire.
SOURCES = [
    {"nom": "Epoch AI — Notable AI Models",
     "url": "https://epoch.ai/data/notable_ai_models.csv",
     "licence": "CC BY 4.0", "credit": CREDIT_EPOCH,
     "cadence": "hebdomadaire", "automatisable": True,
     "role": "Source primaire du volet « modèles remarquables » (organisation, pays, compute, date)."},
    {"nom": "Eurostat — isoc_eb_ai (adoption IA entreprises)",
     "url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/isoc_eb_ai",
     "licence": "CC BY 4.0", "credit": CREDIT_EUROSTAT,
     "cadence": "trimestrielle (dataset annuel)", "automatisable": True,
     "role": "Volet adoption de l'IA par les entreprises (UE-27 / France / taille d'entreprise)."},
    {"nom": "data.europa.eu — API hub-search",
     "url": "https://data.europa.eu/api/hub/search/",
     "licence": "CC BY 4.0 (métadonnées)", "credit": CREDIT_UE,
     "cadence": "à la demande / mensuel", "automatisable": True,
     "role": "Secondaire — découverte de jeux de données IA complémentaires (JRC, Eurostat, CORDIS)."},
    {"nom": "CORDIS — RSS recherche projets UE",
     "url": "https://cordis.europa.eu/search/rss?q=%27artificial%20intelligence%27",
     "licence": "Décision 2011/833/UE", "credit": "© Union européenne, CORDIS, cordis.europa.eu",
     "cadence": "hebdomadaire", "automatisable": True,
     "role": "Volet projets de recherche IA financés par l'UE (Horizon Europe, coordinateurs, pays)."},
    {"nom": "Commission — Stratégie numérique (RSS)",
     "url": "https://digital-strategy.ec.europa.eu/en/rss.xml",
     "licence": "Décision 2011/833/UE / CC BY 4.0", "credit": "© Union européenne — Commission européenne",
     "cadence": "toutes les 6 h", "automatisable": True,
     "role": "Actualités politiques numériques/IA de la Commission (AI Act, GenAI4EU…)."},
    {"nom": "AI Act — artificialintelligenceact.eu (feed)",
     "url": "https://artificialintelligenceact.eu/feed/",
     "licence": "Future of Life Institute — citation + lien source",
     "credit": "artificialintelligenceact.eu (Future of Life Institute)",
     "cadence": "toutes les 6 h", "automatisable": True,
     "role": "Volet réglementation UE — actualité de mise en œuvre de l'AI Act."},
    {"nom": "EPO OPS — Open Patent Services",
     "url": "https://ops.epo.org/",
     "licence": "Conditions OPS de l'OEB (gratuit avec attribution)",
     "credit": "Données brevets : OEB, Open Patent Services",
     "cadence": "mensuelle", "automatisable": True,
     "role": "Volet brevets IA (dépôts par pays/déposant) une fois la clé OAuth2 en variable "
             "d'environnement Render ; AI Index/CSET en attendant."},
    {"nom": "Futurium — Alliance européenne pour l'IA",
     "url": "https://futurium.ec.europa.eu/en/european-ai-alliance",
     "licence": "© Union européenne (2011/833/UE)", "credit": CREDIT_UE,
     "cadence": "revue manuelle mensuelle", "automatisable": False,
     "role": "Lien de référence communauté/consultations du volet politiques UE "
             "(à requalifier en automatisable si le /rss.xml répond 200 en production)."},
    {"nom": "AI Watch (JRC)",
     "url": "https://ai-watch.ec.europa.eu/",
     "licence": "© UE / CC BY 4.0 (publications JRC)",
     "credit": "AI Watch — JRC, Commission européenne",
     "cadence": "revue manuelle semestrielle", "automatisable": False,
     "role": "Cadrage/indicateurs de référence UE (investissements, adoption, talents) — pas d'API dédiée."},
    {"nom": "OECD.AI — Policy Observatory",
     "url": "https://oecd.ai/",
     "licence": "OCDE — CC BY 4.0 par défaut (vérifier par dashboard)",
     "credit": "OECD.AI Policy Observatory, oecd.ai",
     "cadence": "revue manuelle trimestrielle", "automatisable": False,
     "role": "Volet politiques IA hors UE (60+ pays) — lien + capture manuelle, pas de scraping."},
    {"nom": "MacroPolo — Global AI Talent Tracker",
     "url": "https://macropolo.org/digital-projects/the-global-ai-talent-tracker/",
     "licence": "© MacroPolo / Paulson Institute", "credit": CREDIT_MACROPOLO,
     "cadence": "~triennale — catalogage manuel, chiffres ARCHIVÉS dans le seed "
                "(think tank dissous en 2024, site à risque)", "automatisable": False,
     "role": "Source du volet « chercheurs d'élite » NeurIPS (origine/formation/affiliation)."},
    {"nom": "Stanford AI Index (brevets : CSET)",
     "url": "https://aiindex.stanford.edu/report/",
     "licence": "CC BY-ND 4.0", "credit": CREDIT_AI_INDEX,
     "cadence": "annuelle (parution avril) — intégration manuelle", "automatisable": False,
     "role": "Volet brevets (tant qu'EPO OPS n'est pas branché) et cadrage macro annuel."},
]


# ═══════════════════════════════════════════════════════════════════════════
# 4. FETCHEURS TEMPS RÉEL — calculs déterministes sur sources publiques
# ═══════════════════════════════════════════════════════════════════════════
# Contrat commun : renvoyer (donnees, None) en cas de succès, (None, "erreur")
# sinon. Jamais d'exception propagée, jamais d'identifiant transmis.

def _assainir_erreur(ex):
    """Message d'erreur assaini : une ligne, tronqué, sans dump interne."""
    txt = " ".join(str(ex).split())
    nom = type(ex).__name__ if isinstance(ex, BaseException) else "Erreur"
    return (nom + ": " + txt)[:180] if txt else nom


# Noms de pays Epoch (anglais) → libellés français du seed. Déterministe :
# un pays absent de la table garde son libellé d'origine.
_PAYS_FR = {
    "united states of america": "États-Unis", "united states": "États-Unis", "usa": "États-Unis",
    "china": "Chine", "united kingdom": "Royaume-Uni", "germany": "Allemagne",
    "france": "France", "canada": "Canada", "russia": "Russie", "japan": "Japon",
    "south korea": "Corée du Sud", "korea (republic of)": "Corée du Sud",
    "israel": "Israël", "india": "Inde", "sweden": "Suède", "norway": "Norvège",
    "finland": "Finlande", "netherlands": "Pays-Bas", "belgium": "Belgique",
    "ireland": "Irlande", "spain": "Espagne", "switzerland": "Suisse", "italy": "Italie",
    "poland": "Pologne", "czech republic": "Rép. tchèque", "czechia": "Rép. tchèque",
    "austria": "Autriche", "iran": "Iran", "saudi arabia": "Arabie saoudite",
    "united arab emirates": "Émirats arabes unis", "australia": "Australie",
    "argentina": "Argentine", "singapore": "Singapour", "taiwan": "Taïwan",
    "hong kong": "Hong Kong", "multinational": "Multinational",
}

# Candidats de nom de colonne pays du CSV Epoch (le schéma a déjà été renommé).
_EPOCH_COL_PAYS = ["Country (from Organization)", "Country (of organization)",
                   "Organization country", "Country"]
# epoch.ai = domaine actuel ; epochai.org = ancien domaine (redirigé), en repli.
_EPOCH_URLS = ["https://epoch.ai/data/notable_ai_models.csv",
               "https://epochai.org/data/notable_ai_models.csv"]


def _telecharger_plafonne(url, timeout, plafond):
    """Télécharge une URL en flux, borné à `plafond` octets. Renvoie les octets
    ou lève ValueError si la réponse dépasse le plafond (protection mémoire)."""
    resp = requests.get(url, headers=UA, timeout=timeout, stream=True)
    try:
        if resp.status_code != 200:
            raise ValueError("HTTP %s" % resp.status_code)
        decl = resp.headers.get("Content-Length")
        if decl and decl.isdigit() and int(decl) > plafond:
            raise ValueError("réponse annoncée > %d Mo" % (plafond // (1024 * 1024)))
        morceaux, total = [], 0
        for chunk in resp.iter_content(chunk_size=65536):
            if not chunk:
                continue
            total += len(chunk)
            if total > plafond:
                raise ValueError("réponse > %d Mo, téléchargement interrompu"
                                 % (plafond // (1024 * 1024)))
            morceaux.append(chunk)
        return b"".join(morceaux)
    finally:
        try:
            resp.close()
        except Exception:
            pass


def epoch_modeles():
    """CSV « notable AI models » d'Epoch AI → cumul de modèles par pays.

    La colonne pays peut lister PLUSIEURS pays séparés par des virgules
    (organisations multi-pays) : chaque pays cité compte pour un.
    Renvoie ({pays: count}, None) ou (None, "erreur")."""
    derniere = "aucune URL essayée"
    for url in _EPOCH_URLS:
        try:
            brut = _telecharger_plafonne(url, TIMEOUT_CSV, EPOCH_MAX_OCTETS)
            texte = brut.decode("utf-8", errors="replace")
            lecteur = csv.DictReader(io.StringIO(texte))
            entetes = lecteur.fieldnames or []
            # Colonne pays : candidats connus d'abord, sinon 1re colonne
            # contenant "country" (tolérance aux renommages du schéma Epoch).
            col = next((c for c in _EPOCH_COL_PAYS if c in entetes), None)
            if col is None:
                col = next((c for c in entetes if c and "country" in c.lower()), None)
            if col is None:
                derniere = "colonne pays introuvable (en-têtes : %s)" % ", ".join(entetes[:8])
                continue
            comptes = {}
            for ligne in lecteur:
                cellule = (ligne.get(col) or "").strip()
                if not cellule:
                    continue
                for pays in cellule.split(","):
                    pays = pays.strip()
                    if not pays:
                        continue
                    libelle = _PAYS_FR.get(pays.lower(), pays)
                    comptes[libelle] = comptes.get(libelle, 0) + 1
            if not comptes:
                derniere = "CSV lu mais aucun pays compté"
                continue
            # Tri décroissant : lisible tel quel côté front.
            return dict(sorted(comptes.items(), key=lambda kv: -kv[1])), None
        except Exception as ex:
            derniere = _assainir_erreur(ex)
    return None, "Epoch AI injoignable — " + derniere


_EUROSTAT_URL = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/"
                 "data/isoc_eb_ai")
# Filtres préférés : entreprises (10 salariés et plus, hors secteur financier)
# utilisant au moins une technologie d'IA, en % des entreprises. Si les codes
# changent côté Eurostat, on retombe sur la requête sans filtre (1re catégorie
# de chaque dimension annexe).
_EUROSTAT_FILTRES = "?format=JSON&lang=fr&indic_is=E_AI&unit=PC_ENT&sizen_r2=10_C10_S951_XK"
_EUROSTAT_SANS_FILTRE = "?format=JSON&lang=fr"


def _jsonstat_positions(categorie):
    """category.index d'un JSON-stat : dict code→position ou liste ordonnée."""
    idx = (categorie or {}).get("index")
    if isinstance(idx, dict):
        return dict(idx)
    if isinstance(idx, list):
        return {code: i for i, code in enumerate(idx)}
    # Dimension à catégorie unique sans index explicite.
    labels = (categorie or {}).get("label") or {}
    return {code: i for i, code in enumerate(labels)}


def eurostat_adoption():
    """API Eurostat isoc_eb_ai → % d'entreprises utilisant l'IA, dernière année.

    Parsing JSON-stat 2.0 minimal, sans dépendance nouvelle : ids/sizes,
    index linéaire en ordre ligne (strides), valeurs par position.
    Renvoie ({"annee": "2024", "valeurs": {pays: %}}, None) ou (None, "erreur")."""
    donnees, derniere = None, "aucune requête aboutie"
    for suffixe in (_EUROSTAT_FILTRES, _EUROSTAT_SANS_FILTRE):
        try:
            resp = requests.get(_EUROSTAT_URL + suffixe, headers=UA, timeout=TIMEOUT_API)
            if resp.status_code != 200:
                derniere = "HTTP %s" % resp.status_code
                continue
            donnees = json.loads(resp.content.decode("utf-8"))
            break
        except Exception as ex:
            derniere = _assainir_erreur(ex)
    if donnees is None:
        return None, "Eurostat injoignable — " + derniere
    try:
        dims = donnees.get("dimension") or {}
        ids = donnees.get("id") or dims.get("id") or []
        tailles = donnees.get("size") or dims.get("size") or []
        if not ids or len(ids) != len(tailles):
            return None, "JSON-stat inattendu (id/size absents)"
        if "geo" not in ids or "time" not in ids:
            return None, "JSON-stat sans dimension geo/time"
        # Strides en ordre ligne : stride[i] = produit des tailles suivantes.
        strides, s = [1] * len(tailles), 1
        for i in range(len(tailles) - 1, -1, -1):
            strides[i] = s
            s *= tailles[i]
        valeurs = donnees.get("value") or {}
        if isinstance(valeurs, list):
            valeurs = {str(i): v for i, v in enumerate(valeurs)}

        def _cat(dim):
            return (dims.get(dim) or {}).get("category") or {}

        pos_geo = _jsonstat_positions(_cat("geo"))
        pos_time = _jsonstat_positions(_cat("time"))
        labels_geo = _cat("geo").get("label") or {}
        # Position 0 pour toute dimension annexe (avec filtres : catégorie unique).
        base = {dim: 0 for dim in ids}
        i_geo, i_time = ids.index("geo"), ids.index("time")

        def _lire(pg, pt):
            base[ids[i_geo]], base[ids[i_time]] = pg, pt
            lineaire = sum(base[dim] * strides[i] for i, dim in enumerate(ids))
            return valeurs.get(str(lineaire))

        # Dernière année disposant d'au moins une valeur non nulle.
        for annee, pt in sorted(pos_time.items(), key=lambda kv: kv[0], reverse=True):
            releve = {}
            for code, pg in pos_geo.items():
                v = _lire(pg, pt)
                if v is not None:
                    releve[labels_geo.get(code, code)] = v
            if releve:
                return {"annee": str(annee), "valeurs": releve}, None
        return None, "JSON-stat sans valeur exploitable"
    except Exception as ex:
        return None, "parsing Eurostat — " + _assainir_erreur(ex)


# Flux du volet « stratégie & réglementation ». Le RSS Futurium (Alliance
# européenne pour l'IA) n'est PAS intégré : /rss.xml non documenté et injoignable
# au sondage — Futurium reste un lien de référence (SOURCES) ; à requalifier en
# flux si le RSS répond 200 en production.
OBS_FLUX = [
    {"url": "https://digital-strategy.ec.europa.eu/en/rss.xml",
     "source": "Commission européenne — Stratégie numérique"},
    {"url": "https://artificialintelligenceact.eu/feed/",
     "source": "AI Act (artificialintelligenceact.eu)"},
]
OBS_FLUX_MAX_PAR_SOURCE = 8


def flux_strategie():
    """Agrège les flux RSS stratégie/réglementation IA — titre, lien, date
    seulement (pas de résumé : la veille générale s'en charge déjà).
    Renvoie (items, None) si au moins un flux répond, (None, "erreur") sinon."""
    items, erreurs = [], []
    for flux in OBS_FLUX:
        try:
            resp = requests.get(flux["url"], headers=UA, timeout=TIMEOUT_FLUX)
            if resp.status_code != 200:
                erreurs.append("%s : HTTP %s" % (flux["source"], resp.status_code))
                continue
            analyse = feedparser.parse(resp.content)
            if not analyse.entries:
                erreurs.append("%s : aucun item" % flux["source"])
                continue
            for e in analyse.entries[:OBS_FLUX_MAX_PAR_SOURCE]:
                titre = _html.unescape((e.get("title") or "").strip())
                if not titre:
                    continue
                iso, ts = None, 0.0
                for attr in ("published_parsed", "updated_parsed"):
                    dp = e.get(attr)
                    if dp:
                        try:
                            ts = time.mktime(dp)
                            iso = datetime(dp[0], dp[1], dp[2], dp[3], dp[4], dp[5]).isoformat() + "Z"
                        except Exception:
                            pass
                        break
                items.append({"titre": titre[:200], "lien": e.get("link") or "",
                              "date": iso, "source": flux["source"], "_ts": ts})
        except Exception as ex:
            erreurs.append("%s : %s" % (flux["source"], _assainir_erreur(ex)))
    if not items:
        return None, ("aucun flux joignable — " + " ; ".join(erreurs))[:300]
    items.sort(key=lambda it: it.get("_ts") or 0.0, reverse=True)
    for it in items:
        it.pop("_ts", None)
    return items, None


# ═══════════════════════════════════════════════════════════════════════════
# 5. CACHE PARESSEUX — motif _VEILLE_CACHE d'app.py, un état par source
# ═══════════════════════════════════════════════════════════════════════════
# Rafraîchissement à l'accès quand le TTL est écoulé ; le verrou est pris en
# NON bloquant : une seule requête paie le rafraîchissement, les autres servent
# l'état précédent. Un échec conserve l'ancienne donnée et n'est pas retenté
# avant OBS_RETRY secondes.

_FETCHEURS = {"epoch": epoch_modeles, "eurostat": eurostat_adoption, "flux": flux_strategie}

_OBS_CACHE = {src: {"ts": 0.0, "ts_ok": 0.0, "data": None, "erreur": None}
              for src in _FETCHEURS}
_OBS_LOCKS = {src: threading.Lock() for src in _FETCHEURS}


def _hors_ligne():
    """Vrai si OBS_OFFLINE impose le seed pur (tests, premier rendu instantané)."""
    return (os.environ.get("OBS_OFFLINE") or "") in ("1", "true", "yes")


def _obtenir(source):
    """État de cache d'une source, rafraîchi si nécessaire (jamais bloquant
    pour plus d'une requête). Renvoie l'entrée de cache, pas une copie."""
    c = _OBS_CACHE[source]
    now = time.time()
    fraiche = c["data"] is not None and (now - c["ts_ok"] < OBS_TTL[source])
    echec_recent = c["erreur"] is not None and (now - c["ts"] < OBS_RETRY)
    if fraiche or echec_recent:
        return c
    verrou = _OBS_LOCKS[source]
    if not verrou.acquire(blocking=False):
        return c  # une autre requête rafraîchit déjà : on sert l'état courant
    try:
        # Revérification sous verrou : le rafraîchissement a pu aboutir entre-temps.
        now = time.time()
        if c["data"] is not None and (now - c["ts_ok"] < OBS_TTL[source]):
            return c
        try:
            data, erreur = _FETCHEURS[source]()
        except Exception as ex:  # un fetcheur ne doit jamais faire tomber l'API
            data, erreur = None, _assainir_erreur(ex)
        c["ts"] = time.time()
        if erreur is None and data is not None:
            c["data"], c["ts_ok"], c["erreur"] = data, c["ts"], None
        else:
            c["erreur"] = erreur or "réponse vide"  # donnée précédente conservée
    finally:
        verrou.release()
    return c


def _iso(ts):
    return datetime.utcfromtimestamp(ts).isoformat() + "Z" if ts else None


# ═══════════════════════════════════════════════════════════════════════════
# 6. ASSEMBLAGE — le dict complet servi par /api/observatoire
# ═══════════════════════════════════════════════════════════════════════════

def _copie(volet):
    """Copie profonde d'un volet du SEED (les appelants ne mutent pas le seed)."""
    return json.loads(json.dumps(SEED[volet]))


def rearmer():
    """Rend les caches de source à nouveau rafraîchissables au prochain accès.

    Sert le « forcer un essai » de l'API (?refresh=1). On ne VIDE pas la donnée
    déjà obtenue : si le rafraîchissement échoue, l'observatoire continue de
    servir la dernière valeur connue plutôt que de retomber au référentiel —
    forcer un essai ne doit jamais pouvoir appauvrir l'affichage."""
    for src in _FETCHEURS:
        c = _OBS_CACHE[src]
        c["ts_ok"] = 0.0      # TTL considéré comme écoulé
        c["ts"] = 0.0         # lève aussi la temporisation après échec
        c["erreur"] = None


def assemble(force=False):
    """Assemble l'état complet de l'observatoire.

    Chaque volet indique son mode : "seed" (données figées sourcées) ou "live"
    (fetcheur ayant répondu, servi depuis le cache). `etat` donne le diagnostic
    par source ; `hors_ligne` signale le mode OBS_OFFLINE=1 (aucun réseau).

    `force` réarme les caches avant l'assemblage (bouton de rafraîchissement)."""
    offline = _hors_ligne()
    if force and not offline:
        rearmer()
    if offline:
        caches = {src: {"ts": 0.0, "ts_ok": 0.0, "data": None, "erreur": None}
                  for src in _FETCHEURS}
    else:
        caches = {src: _obtenir(src) for src in _FETCHEURS}

    # ── Volet modèles : classes du seed, remplacées par les comptes Epoch ──
    modeles = _copie("modeles")
    c = caches["epoch"]
    if c["data"]:
        modeles.update({
            "mode": "live", "precision": "exact",
            "date": "2003 → aujourd'hui (CSV Epoch AI, cache serveur)",
            "cumul_pays": c["data"],
            "note": "Comptes exacts agrégés du CSV Epoch AI (chaque pays cité d'une "
                    "organisation multi-pays compte pour un).",
        })
        modeles.pop("pays", None)     # les classes cèdent la place aux comptes
        modeles.pop("classes", None)
    else:
        modeles["mode"] = "seed"

    # ── Volets figés : talents, brevets, gouvernance (seed par nature) ─────
    talents = _copie("talents")
    talents["mode"] = "seed"
    brevets = _copie("brevets")
    brevets["mode"] = "seed"
    gouvernance = _copie("gouvernance")
    gouvernance["mode"] = "seed"

    # ── Volet adoption UE : seed minimal, détail Eurostat si disponible ────
    adoption = _copie("adoption_ue")
    c = caches["eurostat"]
    if c["data"]:
        adoption.update({
            "mode": "live", "precision": "exact (API Eurostat)",
            "annee": c["data"].get("annee"),
            "date": c["data"].get("annee"),
            "valeurs": c["data"].get("valeurs") or {},
            "note": "Détail par pays servi par l'API Eurostat (cache serveur).",
        })
    else:
        adoption["mode"] = "seed"

    # ── Volet flux : uniquement live (le seed n'embarque pas d'actualité) ──
    c = caches["flux"]
    if c["data"]:
        flux = {"mode": "live", "count": len(c["data"]), "items": c["data"],
                "credit": "© sources citées par item (Commission européenne, "
                          "Future of Life Institute)"}
    else:
        flux = {"mode": "seed", "count": 0, "items": [],
                "note": "Flux non chargés (hors-ligne, premier accès ou sources "
                        "injoignables) — voir `etat`."}

    # ── Diagnostic par source ──────────────────────────────────────────────
    etat = {}
    for src, cc in caches.items():
        etat[src] = {
            "ok": cc["erreur"] is None and cc["data"] is not None,
            "derniere_maj": _iso(cc["ts_ok"]),
            "derniere_erreur": cc["erreur"],
        }

    return {
        "maj": datetime.utcnow().isoformat() + "Z",
        "version_seed": VERSION_SEED,
        "hors_ligne": offline,
        "modeles": modeles,
        "talents": talents,
        "brevets": brevets,
        "adoption_ue": adoption,
        "gouvernance": gouvernance,
        "flux": flux,
        "sources": {"catalogue": SOURCES, "credits": list(SEED["credits"])},
        "etat": etat,
    }


def sante():
    """Bloc 'observatoire' pour /api/health : volumétrie et âge du cache."""
    now = time.time()
    detail, ages = {}, []
    for src, c in _OBS_CACHE.items():
        d = c["data"]
        n = len(d) if hasattr(d, "__len__") else (1 if d is not None else 0)
        age = round(now - c["ts_ok"], 1) if c["ts_ok"] else None
        if age is not None:
            ages.append(age)
        detail[src] = {"cache_items": n, "cache_age_s": age, "ttl_s": OBS_TTL[src]}
    return {
        "cache_items": sum(v["cache_items"] for v in detail.values()),
        "cache_age_s": max(ages) if ages else None,
        "ttl_s": dict(OBS_TTL),
        "detail": detail,
    }


if __name__ == "__main__":  # aperçu rapide en local : OBS_OFFLINE=1 python3 observatoire_ia.py
    print(json.dumps(assemble(), ensure_ascii=False, indent=2)[:4000])
