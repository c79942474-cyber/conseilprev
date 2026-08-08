# -*- coding: utf-8 -*-
"""Panorama des systèmes d'IA (SIA) déployés en entreprise dans l'UE — module autonome.

OBJET. Un référentiel EXPERT et SOURCÉ des déploiements d'IA en entreprise dans
l'Union (POC, pilotes, production, mise à l'échelle) sur la période mi-2023 →
mi-2026, croisé avec : la classification de risque du Règlement (UE) 2024/1689
(AI Act), un profil de vulnérabilités cyber par type de SIA, la couche
réglementaire nationale des 27 États membres, et un score d'exposition
réglementaire calculé — le tout destiné aux décideurs comme base de travail.

TROIS RÈGLES D'HONNÊTETÉ, non négociables :

1. PANEL REPRÉSENTATIF, PAS EXHAUSTIF. Un inventaire exhaustif des SIA en
   production dans l'UE n'existe nulle part publiquement — la base européenne
   des systèmes à haut risque (art. 71 AI Act) ne se remplira qu'à partir des
   échéances de 2026-2027. Prétendre à l'exhaustivité serait un mensonge de
   méthode. Ce panel couvre les cas PUBLIQUEMENT DOCUMENTÉS, sélectionnés pour
   représenter la diversité des secteurs, des pays, des stades et des classes
   de risque. Chaque agrégat affiché porte cette limite.

2. EXPOSITION ≠ CONFORMITÉ. Le score calculé mesure l'EXPOSITION RÉGLEMENTAIRE
   DU CAS D'USAGE (classe de risque, stade, données, population touchée,
   dépendance GPAI, signaux publics) — il n'est PAS un audit de conformité de
   l'entreprise : personne ne peut auditer de l'extérieur ce qui se joue dans
   la documentation technique et la gouvernance interne. Les seuls jugements
   portés sur une entreprise nommée sont des FAITS PUBLICS SOURCÉS (sanction,
   enquête, décision de justice, engagement public).

3. CERTAIN / DÉDUIT / INTERPRÉTÉ. Les cas et signaux sont des données sourcées
   et datées, avec un niveau de preuve explicite (décision publique >
   communication d'entreprise > presse spécialisée). La classification AI Act
   et le score sont DÉTERMINISTES : mêmes entrées, même sortie, règles lisibles
   ci-dessous — aucun modèle de langage n'intervient dans ce module. Aucune
   donnée personnelle n'y transite : rien à minimiser, rien à déclarer au
   registre des traitements.
"""
import copy
import json
import os
import re
import threading
import time
import unicodedata
from datetime import datetime

VERSION = "2026-07-b"
FENETRE = "juin 2023 → juillet 2026"

# ═══════════════════════════════════════════════════════════════════════════
# 1. RÉFÉRENTIELS FERMÉS — classes de risque, échéances, niveaux de preuve
# ═══════════════════════════════════════════════════════════════════════════

CLASSES = {
    "interdit":     {"nom": "Pratique interdite (art. 5)", "rang": 4, "couleur": "#7A1B12",
                     "echeance": "2 février 2025 (en vigueur)"},
    "haut_risque":  {"nom": "Haut risque (annexe III / annexe I)", "rang": 3, "couleur": "#B83222",
                     "echeance": "2 août 2026 (annexe III) · 2 août 2027 (annexe I)"},
    "transparence": {"nom": "Risque de transparence (art. 50)", "rang": 2, "couleur": "#C47C1A",
                     "echeance": "2 août 2026"},
    "minimal":      {"nom": "Risque minimal", "rang": 1, "couleur": "#2D7A47",
                     "echeance": "codes de conduite volontaires"},
}

PREUVE = {
    "decision":     "décision publique (sanction, jugement, mesure d'autorité)",
    "officiel":     "communication officielle de l'entreprise ou de l'institution",
    "presse":       "presse économique ou spécialisée",
}

# ═══════════════════════════════════════════════════════════════════════════
# 2. TYPES DE SIA ET PROFILS DE VULNÉRABILITÉ CYBER
#    Croisement OWASP LLM Top 10 (2025), MITRE ATLAS, recommandations ANSSI
#    (« Recommandations de sécurité pour un système d'IA générative », 2024),
#    ENISA (paysage des menaces IA), BSI. L'article 15 de l'AI Act (exactitude,
#    robustesse, cybersécurité) rend ces vecteurs OPPOSABLES pour le haut risque.
# ═══════════════════════════════════════════════════════════════════════════

TYPES_SIA = {
    "assistant_llm": {
        "nom": "Assistant génératif interne (LLM/RAG)",
        "vulnerabilites": [
            {"v": "Injection de prompt directe et indirecte", "ref": "OWASP LLM01 · ATLAS AML.T0051"},
            {"v": "Fuite d'informations sensibles via le contexte RAG", "ref": "OWASP LLM02/LLM06 · ANSSI R11-R14"},
            {"v": "Empoisonnement du corpus documentaire interne", "ref": "OWASP LLM03 · ATLAS AML.T0020"},
            {"v": "Dépendance chaîne d'approvisionnement modèle/API", "ref": "OWASP LLM05 · ANSSI R3"},
        ],
        "referentiels": ["ANSSI GenAI 2024", "OWASP LLM Top 10 v2025", "ISO/IEC 42001", "art. 15 AI Act"],
    },
    "chatbot_client": {
        "nom": "Agent conversationnel face client",
        "vulnerabilites": [
            {"v": "Injection de prompt par l'utilisateur final", "ref": "OWASP LLM01"},
            {"v": "Réponses erronées engageant la responsabilité", "ref": "OWASP LLM09 (surconfiance)"},
            {"v": "Exfiltration de données clients par détournement", "ref": "OWASP LLM02 · ENISA"},
            {"v": "Absence de marquage IA (art. 50)", "ref": "AI Act art. 50 §1"},
        ],
        "referentiels": ["OWASP LLM Top 10 v2025", "ANSSI GenAI 2024", "art. 50 AI Act"],
    },
    "scoring_ml": {
        "nom": "Scoring / décision assistée (crédit, tarification, priorisation)",
        "vulnerabilites": [
            {"v": "Empoisonnement des données d'entraînement", "ref": "ATLAS AML.T0020 · ENISA"},
            {"v": "Attaques par inférence d'appartenance (fuite RGPD)", "ref": "ATLAS AML.T0024"},
            {"v": "Dérive du modèle non détectée (art. 15)", "ref": "art. 15 §4 AI Act"},
            {"v": "Extraction du modèle par requêtes massives", "ref": "ATLAS AML.T0044"},
        ],
        "referentiels": ["MITRE ATLAS", "ENISA", "art. 9-15 AI Act", "EBA/EIOPA (secteur financier)"],
    },
    "rh_recrutement": {
        "nom": "Tri de candidatures / évaluation RH",
        "vulnerabilites": [
            {"v": "Biais discriminatoires (opposables art. 10)", "ref": "art. 10 AI Act · jurisprudences DPA"},
            {"v": "Manipulation adverse des CV (keyword stuffing)", "ref": "ATLAS AML.T0043"},
            {"v": "Traçabilité des décisions insuffisante (art. 12)", "ref": "art. 12 AI Act"},
        ],
        "referentiels": ["annexe III 4 AI Act", "RGPD art. 22", "lignes directrices AI HLEG/ALTAI"],
    },
    "vision_industrielle": {
        "nom": "Vision industrielle (qualité, sécurité, maintenance)",
        "vulnerabilites": [
            {"v": "Exemples adversariaux physiques (leurres)", "ref": "ATLAS AML.T0015"},
            {"v": "Dérive capteurs / conditions hors distribution", "ref": "art. 15 AI Act"},
            {"v": "Intégrité de la chaîne de télémétrie OT", "ref": "IEC 62443 · NIS 2"},
        ],
        "referentiels": ["MITRE ATLAS", "IEC 62443", "NIS 2", "règlement Machines 2023/1230"],
    },
    "biometrie": {
        "nom": "Biométrie / analyse comportementale",
        "vulnerabilites": [
            {"v": "Attaques par présentation (spoofing)", "ref": "ISO/IEC 30107 · ENISA"},
            {"v": "Base de référence : cible de haute valeur", "ref": "RGPD art. 9 · ENISA"},
            {"v": "Frontière art. 5 (catégorisation, émotions)", "ref": "art. 5 §1 f-g AI Act"},
        ],
        "referentiels": ["art. 5 et annexe III 1 AI Act", "RGPD art. 9", "lignes directrices Commission fév. 2025"],
    },
    "agent_autonome": {
        "nom": "Agent autonome (outils, workflows)",
        "vulnerabilites": [
            {"v": "Abus d'outils par injection indirecte", "ref": "OWASP LLM01/LLM07 (agentic)"},
            {"v": "Escalade de privilèges via connecteurs", "ref": "ANSSI GenAI R16 · ENISA"},
            {"v": "Actions irréversibles sans validation humaine", "ref": "art. 14 AI Act (contrôle humain)"},
        ],
        "referentiels": ["OWASP LLM Top 10 v2025 (agentic)", "ANSSI GenAI 2024", "art. 14 AI Act"],
    },
    "optimisation_predictive": {
        "nom": "Prévision / optimisation (demande, tournées, énergie)",
        "vulnerabilites": [
            {"v": "Empoisonnement des séries temporelles amont", "ref": "ATLAS AML.T0020"},
            {"v": "Effet systémique d'une dérive silencieuse", "ref": "art. 15 AI Act · NIS 2"},
        ],
        "referentiels": ["MITRE ATLAS", "NIS 2 (secteurs essentiels)"],
    },
    "surveillance_salaries": {
        "nom": "Suivi algorithmique des travailleurs",
        "vulnerabilites": [
            {"v": "Détournement de finalité (RGPD)", "ref": "RGPD art. 5 · sanctions CNIL"},
            {"v": "Décisions automatisées sans recours (art. 22 RGPD)", "ref": "RGPD art. 22 · annexe III 4 b"},
            {"v": "Frontière émotions au travail = interdit", "ref": "art. 5 §1 f AI Act"},
        ],
        "referentiels": ["annexe III 4 AI Act", "RGPD", "droit du travail national"],
    },
    "sante_dm": {
        "nom": "IA dispositif médical / aide au diagnostic",
        "vulnerabilites": [
            {"v": "Attaques adversariales sur l'imagerie", "ref": "ATLAS · littérature MICCAI"},
            {"v": "Dérive de population (généralisation clinique)", "ref": "MDR + art. 15 AI Act"},
            {"v": "Chaîne logicielle certifiée (mise à jour = requalification)", "ref": "MDR 2017/745 · annexe I AI Act"},
        ],
        "referentiels": ["MDR 2017/745", "annexe I AI Act (2027)", "MDCG", "ISO 14971"],
    },
    "observation_terre": {
        "nom": "Observation de la Terre assistée par IA (télédétection)",
        "vulnerabilites": [
            {"v": "Leurre du signal amont (usurpation AIS, brouillage GNSS)",
             "ref": "ATLAS AML.T0015 · EMSA/EUSPA"},
            {"v": "Dérive saisonnière et couverture nuageuse : conditions hors distribution",
             "ref": "art. 15 §4 AI Act"},
            {"v": "Dépendance à une chaîne de données ouverte tierce — la disponibilité "
                  "du service Copernicus devient une dépendance opérationnelle",
             "ref": "NIS 2 · art. 15 AI Act"},
            {"v": "Erreur de géoréférencement portée directement dans la décision "
                  "(parcelle voisine, navire voisin)",
             "ref": "art. 14 AI Act (contrôle humain)"},
            {"v": "Empoisonnement des jeux d'annotation ouverts réutilisés",
             "ref": "ATLAS AML.T0020"},
        ],
        "referentiels": ["règlement délégué (UE) 1159/2013 (politique de données Copernicus)",
                         "art. 14-15 AI Act", "NIS 2", "MITRE ATLAS"],
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# 3. CLASSIFICATION AI ACT — DÉTERMINISTE
#    Chaque cas porte des DRAPEAUX factuels ; les règles ci-dessous en déduisent
#    la classe et citent leur fondement. Ordre d'examen : interdit > haut risque
#    > transparence > minimal (la classe la plus contraignante l'emporte).
# ═══════════════════════════════════════════════════════════════════════════

def classer_cas(cas):
    """Renvoie (classe, [règles déclenchées avec fondement])."""
    d = cas.get("drapeaux", {})
    regles = []
    classe = "minimal"

    if d.get("emotion_travail"):
        regles.append("Reconnaissance des émotions sur le lieu de travail → INTERDIT, art. 5 §1 f (depuis le 2 févr. 2025)")
        classe = "interdit"
    if d.get("scraping_facial"):
        regles.append("Constitution de bases faciales par moissonnage indiscriminé → INTERDIT, art. 5 §1 e")
        classe = "interdit"
    if classe != "interdit":
        hr = []
        if d.get("rh"):
            hr.append("Emploi : recrutement, évaluation, gestion des travailleurs → annexe III 4")
        if d.get("credit"):
            hr.append("Évaluation de la solvabilité / score de crédit → annexe III 5 b")
        if d.get("assurance_vie_sante"):
            hr.append("Tarification vie et santé → annexe III 5 c")
        if d.get("infrastructure_critique"):
            hr.append("Composant de sécurité d'une infrastructure critique → annexe III 2")
        if d.get("dispositif_medical"):
            hr.append("Composant de sécurité d'un produit réglementé (MDR) → art. 6 §1 + annexe I")
        if d.get("biometrie_id"):
            hr.append("Identification / catégorisation biométrique → annexe III 1")
        if d.get("triage_urgence"):
            hr.append("Triage d'appels ou de patients en urgence → annexe III 5 d")
        if d.get("education"):
            hr.append("Éducation : admission, évaluation → annexe III 3")
        if d.get("prestations_publiques"):
            hr.append("Accès aux prestations et services publics essentiels : "
                      "octroi, réduction, suppression → annexe III 5 a")
        if d.get("migration_frontieres"):
            hr.append("Migration, asile, contrôle aux frontières → annexe III 7")
        if hr:
            regles.extend(hr)
            classe = "haut_risque"
        elif d.get("chatbot") or d.get("generation_contenu"):
            regles.append("Interaction directe avec des personnes / contenu généré → obligations de transparence, art. 50")
            classe = "transparence"
        else:
            regles.append("Hors annexe III, hors art. 5, hors art. 50 → risque minimal (codes de conduite volontaires, art. 95)")
    if d.get("gpai"):
        regles.append("SIA fondé sur un modèle à usage général : diligence chaîne d'approvisionnement (chap. V, applicable depuis le 2 août 2025)")
    if d.get("exclusion_defense"):
        regles.append("Finalité défense/sécurité nationale → hors champ AI Act (art. 2 §3) ; encadrement national")
    return classe, regles


# ═══════════════════════════════════════════════════════════════════════════
# 4. SCORE D'EXPOSITION RÉGLEMENTAIRE — DÉTERMINISTE, 0-100
#    Mesure la PRIORITÉ D'EXAMEN du cas d'usage, jamais la conformité de
#    l'entreprise. Chaque terme est lisible et sourcé dans le détail du calcul.
# ═══════════════════════════════════════════════════════════════════════════

_BASE = {"interdit": 92, "haut_risque": 68, "transparence": 40, "minimal": 14}
_STADE = {"production": 15, "echelle": 15, "pilote": 8, "poc": 3, "abandonne": 0}

def scorer_cas(cas, classe):
    d = cas.get("drapeaux", {})
    detail = []
    s = _BASE[classe]
    detail.append(("classe %s" % CLASSES[classe]["nom"], _BASE[classe]))
    st = _STADE.get(cas.get("stade", "poc"), 3)
    detail.append(("stade « %s »" % cas.get("stade", "poc"), st)); s += st
    if d.get("donnees_sensibles"):
        detail.append(("données sensibles (art. 9 RGPD)", 8)); s += 8
    elif d.get("donnees_perso"):
        detail.append(("données personnelles", 5)); s += 5
    pop = cas.get("population", "")
    if pop in ("salaries", "candidats"):
        detail.append(("population : travailleurs/candidats", 5)); s += 5
    elif pop == "grand_public":
        detail.append(("population : grand public", 6)); s += 6
    if d.get("gpai"):
        detail.append(("dépendance modèle tiers (GPAI)", 4)); s += 4
    for sig in cas.get("signaux", []):
        if sig.get("sens") == "-":
            detail.append(("signal public défavorable : %s" % sig["titre"][:60], 10)); s += 10
        elif sig.get("sens") == "+":
            detail.append(("mesure publique de maîtrise : %s" % sig["titre"][:60], -8)); s -= 8
    s = max(0, min(100, s))
    if s >= 80: tiers = "critique"
    elif s >= 60: tiers = "élevé"
    elif s >= 40: tiers = "à surveiller"
    else: tiers = "maîtrisable"
    return s, tiers, detail


# ═══════════════════════════════════════════════════════════════════════════
# 5. LE PANEL — cas publiquement documentés, mi-2023 → mi-2026
#    Champs : entreprise, pays (ISO-2), secteur, cas, type (clé TYPES_SIA),
#    stade, annee, population, drapeaux, signaux [{titre, sens, preuve, date}],
#    sources [{editeur, titre, date, preuve}]. Les liens profonds ne sont PAS
#    stockés (invérifiables d'ici) : éditeur + titre + date suffisent à retrouver
#    la pièce, sans risquer l'URL inventée.
# ═══════════════════════════════════════════════════════════════════════════

CAS = [
 # ── FINANCE / ASSURANCE ────────────────────────────────────────────────────
 {"entreprise": "BNP Paribas", "pays": "FR", "secteur": "Banque",
  "cas": "Assistants génératifs internes (conseillers, conformité) fondés sur les modèles Mistral AI",
  "type": "assistant_llm", "stade": "production", "annee": 2024, "population": "salaries",
  "drapeaux": {"gpai": True, "donnees_perso": True},
  "sources": [{"editeur": "BNP Paribas / Mistral AI", "titre": "Partenariat pluriannuel (communiqué)", "date": "2024-07", "preuve": "officiel"}]},
 {"entreprise": "AXA", "pays": "FR", "secteur": "Assurance",
  "cas": "AXA Secure GPT déployé à l'échelle du groupe (~140 000 collaborateurs)",
  "type": "assistant_llm", "stade": "echelle", "annee": 2023, "population": "salaries",
  "drapeaux": {"gpai": True, "donnees_perso": True},
  "sources": [{"editeur": "AXA", "titre": "Lancement d'AXA Secure GPT (communiqué)", "date": "2023-07", "preuve": "officiel"}]},
 {"entreprise": "AXA", "pays": "FR", "secteur": "Assurance",
  "cas": "Tarification et sélection des risques santé/prévoyance assistées par ML",
  "type": "scoring_ml", "stade": "production", "annee": 2024, "population": "grand_public",
  "drapeaux": {"assurance_vie_sante": True, "donnees_sensibles": True},
  "sources": [{"editeur": "presse assurance (L'Argus)", "titre": "IA et tarification : pratiques du marché", "date": "2024", "preuve": "presse"}]},
 {"entreprise": "BBVA", "pays": "ES", "secteur": "Banque",
  "cas": "Déploiement ChatGPT Enterprise (milliers de licences) pour les fonctions internes",
  "type": "assistant_llm", "stade": "production", "annee": 2024, "population": "salaries",
  "drapeaux": {"gpai": True, "donnees_perso": True},
  "sources": [{"editeur": "BBVA / OpenAI", "titre": "Accord ChatGPT Enterprise (communiqué)", "date": "2024-05", "preuve": "officiel"}]},
 {"entreprise": "Santander", "pays": "ES", "secteur": "Banque",
  "cas": "Scoring de crédit ML consommateurs (Openbank et réseaux)",
  "type": "scoring_ml", "stade": "production", "annee": 2024, "population": "grand_public",
  "drapeaux": {"credit": True, "donnees_perso": True},
  "sources": [{"editeur": "presse financière", "titre": "IA et octroi de crédit dans la banque de détail", "date": "2024", "preuve": "presse"}]},
 {"entreprise": "ING", "pays": "NL", "secteur": "Banque",
  "cas": "Chatbot génératif de service client (premier grand déploiement bancaire génAI face client en Europe)",
  "type": "chatbot_client", "stade": "production", "annee": 2024, "population": "grand_public",
  "drapeaux": {"chatbot": True, "gpai": True, "donnees_perso": True},
  "sources": [{"editeur": "ING / McKinsey", "titre": "Étude de cas assistant génératif client", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Klarna", "pays": "SE", "secteur": "Fintech",
  "cas": "Assistant client OpenAI traitant l'équivalent de ~700 agents (2/3 des conversations)",
  "type": "chatbot_client", "stade": "echelle", "annee": 2024, "population": "grand_public",
  "drapeaux": {"chatbot": True, "gpai": True, "donnees_perso": True},
  "signaux": [{"titre": "Réintroduction d'agents humains annoncée (limites qualité)", "sens": "+", "preuve": "officiel", "date": "2025"}],
  "sources": [{"editeur": "Klarna", "titre": "AI assistant handles two-thirds of chats (communiqué)", "date": "2024-02", "preuve": "officiel"}]},
 {"entreprise": "Allianz", "pays": "DE", "secteur": "Assurance",
  "cas": "Assistance génératives à la gestion des sinistres et à la souscription",
  "type": "assistant_llm", "stade": "pilote", "annee": 2024, "population": "salaries",
  "drapeaux": {"gpai": True, "donnees_perso": True},
  "sources": [{"editeur": "Allianz", "titre": "Programme génAI groupe (rapports/presse)", "date": "2024", "preuve": "presse"}]},
 {"entreprise": "Munich Re", "pays": "DE", "secteur": "Assurance",
  "cas": "Souscription augmentée et couverture des risques de modèles IA (aiSure)",
  "type": "scoring_ml", "stade": "production", "annee": 2024, "population": "b2b",
  "drapeaux": {"donnees_perso": False},
  "sources": [{"editeur": "Munich Re", "titre": "aiSure — assurance de performance des modèles", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Intesa Sanpaolo", "pays": "IT", "secteur": "Banque",
  "cas": "Programme d'assistants génératifs internes (déploiement progressif)",
  "type": "assistant_llm", "stade": "pilote", "annee": 2024, "population": "salaries",
  "drapeaux": {"gpai": True, "donnees_perso": True},
  "sources": [{"editeur": "presse financière italienne", "titre": "Plan IA d'Intesa Sanpaolo", "date": "2024", "preuve": "presse"}]},
 {"entreprise": "Revolut", "pays": "LT", "secteur": "Fintech",
  "cas": "Détection de fraude paiement en temps réel par ML",
  "type": "scoring_ml", "stade": "echelle", "annee": 2024, "population": "grand_public",
  "drapeaux": {"donnees_perso": True},
  "sources": [{"editeur": "Revolut", "titre": "Dispositif anti-fraude (communication produit)", "date": "2024", "preuve": "officiel"}]},

 # ── RH / EMPLOI ────────────────────────────────────────────────────────────
 {"entreprise": "Randstad", "pays": "NL", "secteur": "Services RH",
  "cas": "Appariement algorithmique candidats-missions à l'échelle européenne",
  "type": "rh_recrutement", "stade": "production", "annee": 2024, "population": "candidats",
  "drapeaux": {"rh": True, "donnees_perso": True},
  "sources": [{"editeur": "Randstad", "titre": "Plateformes de matching (communication)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Siemens", "pays": "DE", "secteur": "Industrie",
  "cas": "Aide au tri de candidatures et mobilité interne assistée",
  "type": "rh_recrutement", "stade": "pilote", "annee": 2024, "population": "candidats",
  "drapeaux": {"rh": True, "donnees_perso": True},
  "sources": [{"editeur": "presse RH", "titre": "IA de recrutement dans l'industrie allemande", "date": "2024", "preuve": "presse"}]},
 {"entreprise": "Amazon France Logistique", "alias": ["Amazon"], "pays": "FR", "secteur": "Logistique",
  "cas": "Suivi algorithmique de la productivité des salariés en entrepôt (scanners)",
  "type": "surveillance_salaries", "stade": "production", "annee": 2023, "population": "salaries",
  "drapeaux": {"rh": True, "donnees_perso": True},
  "signaux": [{"titre": "Sanction CNIL 32 M€ (surveillance excessive)", "sens": "-", "preuve": "decision", "date": "2024-01"}],
  "sources": [{"editeur": "CNIL", "titre": "Délibération SAN-2023-021 (publiée janv. 2024)", "date": "2024-01", "preuve": "decision"}]},
 {"entreprise": "Secteur centres d'appels (plusieurs opérateurs)", "alias": [], "pays": "PL", "secteur": "Services",
  "cas": "Pilotes d'analyse des émotions des téléconseillers en temps réel — abandonnés à l'entrée en vigueur de l'art. 5",
  "type": "biometrie", "stade": "abandonne", "annee": 2024, "population": "salaries",
  "drapeaux": {"emotion_travail": True, "donnees_sensibles": True},
  "sources": [{"editeur": "presse spécialisée / lignes directrices Commission", "titre": "Practices interdites : reconnaissance d'émotions au travail", "date": "2025-02", "preuve": "presse"}]},

 # ── SANTÉ ──────────────────────────────────────────────────────────────────
 {"entreprise": "Doctolib", "pays": "FR", "secteur": "Santé numérique",
  "cas": "Assistant de consultation (transcription et synthèse) pour les praticiens",
  "type": "assistant_llm", "stade": "production", "annee": 2024, "population": "grand_public",
  "drapeaux": {"gpai": True, "donnees_sensibles": True},
  "sources": [{"editeur": "Doctolib", "titre": "Lancement de l'assistant de consultation", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Philips", "pays": "NL", "secteur": "Dispositifs médicaux",
  "cas": "Reconstruction et lecture d'imagerie accélérées par IA (gamme SmartSpeed)",
  "type": "sante_dm", "stade": "echelle", "annee": 2024, "population": "grand_public",
  "drapeaux": {"dispositif_medical": True, "donnees_sensibles": True},
  "sources": [{"editeur": "Philips", "titre": "Portefeuille IA d'imagerie (marquage CE MDR)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Siemens Healthineers", "pays": "DE", "secteur": "Dispositifs médicaux",
  "cas": "AI-Rad Companion : aide à la lecture radiologique multi-organes",
  "type": "sante_dm", "stade": "echelle", "annee": 2024, "population": "grand_public",
  "drapeaux": {"dispositif_medical": True, "donnees_sensibles": True},
  "sources": [{"editeur": "Siemens Healthineers", "titre": "AI-Rad Companion (CE MDR)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Owkin", "pays": "FR", "secteur": "Biotech",
  "cas": "Diagnostics et biomarqueurs IA en oncologie (produits marqués CE)",
  "type": "sante_dm", "stade": "production", "annee": 2024, "population": "grand_public",
  "drapeaux": {"dispositif_medical": True, "donnees_sensibles": True},
  "sources": [{"editeur": "Owkin", "titre": "Produits de diagnostic (communication réglementaire)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Kry / Livi", "alias": ["Kry", "Livi"], "pays": "SE", "secteur": "Santé numérique",
  "cas": "Pré-tri des symptômes et orientation des patients en télémédecine",
  "type": "scoring_ml", "stade": "production", "annee": 2024, "population": "grand_public",
  "drapeaux": {"triage_urgence": True, "donnees_sensibles": True},
  "sources": [{"editeur": "Kry", "titre": "Parcours de triage numérique", "date": "2024", "preuve": "officiel"}]},

 # ── INDUSTRIE / AUTOMOBILE / AÉRO ─────────────────────────────────────────
 {"entreprise": "Airbus", "pays": "FR", "secteur": "Aéronautique",
  "cas": "Vision qualité en ligne d'assemblage et génAI d'ingénierie interne",
  "type": "vision_industrielle", "stade": "production", "annee": 2024, "population": "salaries",
  "drapeaux": {},
  "sources": [{"editeur": "Airbus", "titre": "Programmes IA industriels (communication)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Thales", "pays": "FR", "secteur": "Défense & sécurité",
  "cas": "cortAIx : accélérateur IA (100+ chercheurs) pour systèmes critiques et défense",
  "type": "agent_autonome", "stade": "pilote", "annee": 2024, "population": "b2b",
  "drapeaux": {"exclusion_defense": True},
  "sources": [{"editeur": "Thales", "titre": "Lancement de cortAIx (communiqué)", "date": "2024-03", "preuve": "officiel"}]},
 {"entreprise": "Renault Group", "alias": ["Renault"], "pays": "FR", "secteur": "Automobile",
  "cas": "Inspection qualité par vision et optimisation d'usine (plateforme avec Google Cloud)",
  "type": "vision_industrielle", "stade": "echelle", "annee": 2024, "population": "salaries",
  "drapeaux": {},
  "sources": [{"editeur": "Renault Group / Google", "titre": "Industrie 4.0 (communiqués)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Stellantis", "pays": "NL", "secteur": "Automobile",
  "cas": "Partenariat Mistral AI : assistant d'ingénierie et IA embarquée conversationnelle",
  "type": "assistant_llm", "stade": "pilote", "annee": 2025, "population": "salaries",
  "drapeaux": {"gpai": True},
  "sources": [{"editeur": "Stellantis / Mistral AI", "titre": "Partenariat stratégique (communiqué)", "date": "2025-02", "preuve": "officiel"}]},
 {"entreprise": "Volkswagen", "pays": "DE", "secteur": "Automobile",
  "cas": "ChatGPT intégré à l'assistant vocal IDA (via Cerence) sur véhicules européens",
  "type": "chatbot_client", "stade": "production", "annee": 2024, "population": "grand_public",
  "drapeaux": {"chatbot": True, "gpai": True, "donnees_perso": True},
  "sources": [{"editeur": "Volkswagen / Cerence", "titre": "Intégration ChatGPT dans IDA (CES 2024)", "date": "2024-01", "preuve": "officiel"}]},
 {"entreprise": "BMW", "pays": "DE", "secteur": "Automobile",
  "cas": "Vision qualité en production (Regensburg) et IA d'usine",
  "type": "vision_industrielle", "stade": "production", "annee": 2024, "population": "salaries",
  "drapeaux": {},
  "sources": [{"editeur": "BMW Group", "titre": "AI in production (communication)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Bosch", "pays": "DE", "secteur": "Équipementier",
  "cas": "Inspection optique IA et offre AIShield (sécurité des modèles) — fournisseur et utilisateur",
  "type": "vision_industrielle", "stade": "echelle", "annee": 2024, "population": "b2b",
  "drapeaux": {},
  "sources": [{"editeur": "Bosch", "titre": "AI in manufacturing / AIShield", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Siemens", "pays": "DE", "secteur": "Industrie",
  "cas": "Industrial Copilot (avec Microsoft) : génAI pour l'ingénierie d'automatisation",
  "type": "assistant_llm", "stade": "production", "annee": 2024, "population": "b2b",
  "drapeaux": {"gpai": True},
  "signaux": [{"titre": "Cas d'usage limité à l'assistance hors fonction de sécurité machine", "sens": "+", "preuve": "officiel", "date": "2024"}],
  "sources": [{"editeur": "Siemens / Microsoft", "titre": "Industrial Copilot (communiqués, clients pilotes)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "ASML", "pays": "NL", "secteur": "Semi-conducteurs",
  "cas": "ML de métrologie et de contrôle de procédé lithographique",
  "type": "optimisation_predictive", "stade": "echelle", "annee": 2024, "population": "b2b",
  "drapeaux": {},
  "sources": [{"editeur": "ASML", "titre": "Computational lithography (communication)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Schneider Electric", "pays": "FR", "secteur": "Équipements électriques",
  "cas": "Copilotes génAI (Resource Advisor) et optimisation énergétique client",
  "type": "assistant_llm", "stade": "production", "annee": 2024, "population": "b2b",
  "drapeaux": {"gpai": True},
  "sources": [{"editeur": "Schneider Electric", "titre": "Resource Advisor Copilot (communiqué)", "date": "2024", "preuve": "officiel"}]},

 # ── ÉNERGIE / UTILITIES ────────────────────────────────────────────────────
 {"entreprise": "Enel", "pays": "IT", "secteur": "Énergie",
  "cas": "Maintenance prédictive du réseau de distribution et inspection par drones+vision",
  "type": "optimisation_predictive", "stade": "echelle", "annee": 2024, "population": "b2b",
  "drapeaux": {"infrastructure_critique": True},
  "sources": [{"editeur": "Enel", "titre": "Grid digitalisation (rapports)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Iberdrola", "pays": "ES", "secteur": "Énergie",
  "cas": "Prévision de production renouvelable et maintenance prédictive éolienne",
  "type": "optimisation_predictive", "stade": "echelle", "annee": 2024, "population": "b2b",
  "drapeaux": {"infrastructure_critique": True},
  "sources": [{"editeur": "Iberdrola", "titre": "IA et réseaux intelligents (communication)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "TotalEnergies", "pays": "FR", "secteur": "Énergie",
  "cas": "Assistants génAI internes et optimisation d'actifs industriels",
  "type": "assistant_llm", "stade": "production", "annee": 2024, "population": "salaries",
  "drapeaux": {"gpai": True},
  "sources": [{"editeur": "TotalEnergies", "titre": "Programme digital & IA (communication)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Vattenfall", "pays": "SE", "secteur": "Énergie",
  "cas": "Prévision de demande et d'équilibrage par apprentissage automatique",
  "type": "optimisation_predictive", "stade": "production", "annee": 2024, "population": "b2b",
  "drapeaux": {"infrastructure_critique": True},
  "sources": [{"editeur": "Vattenfall", "titre": "IA pour l'équilibrage réseau", "date": "2024", "preuve": "officiel"}]},

 # ── TRANSPORT / LOGISTIQUE ─────────────────────────────────────────────────
 {"entreprise": "SNCF", "pays": "FR", "secteur": "Transport ferroviaire",
  "cas": "Maintenance prédictive du matériel roulant et surveillance d'infrastructures",
  "type": "optimisation_predictive", "stade": "echelle", "annee": 2024, "population": "b2b",
  "drapeaux": {"infrastructure_critique": True},
  "sources": [{"editeur": "SNCF", "titre": "Programmes IA maintenance (communication)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "DHL Group", "alias": ["DHL"], "pays": "DE", "secteur": "Logistique",
  "cas": "Optimisation de tournées et vision de tri colis à l'échelle du réseau",
  "type": "optimisation_predictive", "stade": "echelle", "annee": 2024, "population": "b2b",
  "drapeaux": {},
  "sources": [{"editeur": "DHL", "titre": "AI in logistics (rapports)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Maersk", "pays": "DK", "secteur": "Logistique maritime",
  "cas": "Optimisation du positionnement conteneurs et de la consommation",
  "type": "optimisation_predictive", "stade": "production", "annee": 2024, "population": "b2b",
  "drapeaux": {},
  "sources": [{"editeur": "Maersk", "titre": "IA d'optimisation flotte (communication)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Lufthansa Group", "alias": ["Lufthansa"], "pays": "DE", "secteur": "Transport aérien",
  "cas": "GénAI service client et optimisation des opérations (retards, affectations)",
  "type": "chatbot_client", "stade": "pilote", "annee": 2024, "population": "grand_public",
  "drapeaux": {"chatbot": True, "gpai": True, "donnees_perso": True},
  "sources": [{"editeur": "Lufthansa", "titre": "Programme IA (communication)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Plateformes VTC / livraison (Uber, Bolt, Glovo…)", "alias": ["Uber", "Glovo", "Deliveroo"], "pays": "NL", "secteur": "Plateformes",
  "cas": "Gestion algorithmique des chauffeurs/livreurs (affectation, suspension de comptes)",
  "type": "surveillance_salaries", "stade": "echelle", "annee": 2024, "population": "salaries",
  "drapeaux": {"rh": True, "donnees_perso": True},
  "signaux": [{"titre": "Décisions AP/justice NL sur « robo-firing » et transparence ; directive travail de plateforme 2024/2831", "sens": "-", "preuve": "decision", "date": "2023-2024"}],
  "sources": [{"editeur": "Autoriteit Persoonsgegevens / cours néerlandaises", "titre": "Contentieux gestion algorithmique", "date": "2023-2024", "preuve": "decision"}]},

 # ── COMMERCE / DISTRIBUTION ────────────────────────────────────────────────
 {"entreprise": "Zalando", "pays": "DE", "secteur": "E-commerce",
  "cas": "Assistant mode fondé sur ChatGPT et recommandation de taille",
  "type": "chatbot_client", "stade": "production", "annee": 2023, "population": "grand_public",
  "drapeaux": {"chatbot": True, "gpai": True, "donnees_perso": True},
  "sources": [{"editeur": "Zalando", "titre": "Fashion Assistant (communiqué)", "date": "2023-04", "preuve": "officiel"}]},
 {"entreprise": "Carrefour", "pays": "FR", "secteur": "Grande distribution",
  "cas": "Chatbot d'achat « Hopla » (OpenAI) et génAI pour fiches produits et achats",
  "type": "chatbot_client", "stade": "production", "annee": 2023, "population": "grand_public",
  "drapeaux": {"chatbot": True, "gpai": True, "donnees_perso": True},
  "sources": [{"editeur": "Carrefour", "titre": "Lancement Hopla (communiqué)", "date": "2023-06", "preuve": "officiel"}]},
 {"entreprise": "IKEA (Ingka)", "alias": ["IKEA"], "pays": "SE", "secteur": "Distribution",
  "cas": "Assistant génAI de conception et service client (Billie) ; requalification des salariés du centre d'appel",
  "type": "chatbot_client", "stade": "production", "annee": 2024, "population": "grand_public",
  "drapeaux": {"chatbot": True, "gpai": True, "donnees_perso": True},
  "signaux": [{"titre": "Programme public de requalification des téléconseillers", "sens": "+", "preuve": "officiel", "date": "2024"}],
  "sources": [{"editeur": "Ingka Group", "titre": "IA générative et emploi (communication)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Otto Group", "alias": ["Otto Group"], "pays": "DE", "secteur": "E-commerce",
  "cas": "Génération de descriptions produits et traduction à l'échelle du catalogue",
  "type": "assistant_llm", "stade": "production", "annee": 2024, "population": "b2b",
  "drapeaux": {"gpai": True, "generation_contenu": True},
  "sources": [{"editeur": "Otto Group", "titre": "GenAI dans le e-commerce (communication)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Decathlon", "pays": "FR", "secteur": "Distribution",
  "cas": "Prévision de demande et chatbot d'assistance client",
  "type": "optimisation_predictive", "stade": "production", "annee": 2024, "population": "grand_public",
  "drapeaux": {"chatbot": True, "donnees_perso": True},
  "sources": [{"editeur": "Decathlon", "titre": "IA supply & relation client", "date": "2024", "preuve": "presse"}]},

 # ── TÉLÉCOMS / TECH / MÉDIAS ───────────────────────────────────────────────
 {"entreprise": "Deutsche Telekom", "pays": "DE", "secteur": "Télécoms",
  "cas": "Assistants génAI internes (askT) et service client augmenté",
  "type": "assistant_llm", "stade": "production", "annee": 2024, "population": "salaries",
  "drapeaux": {"gpai": True, "donnees_perso": True},
  "sources": [{"editeur": "Deutsche Telekom", "titre": "askT / AI program (communication)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Orange", "pays": "FR", "secteur": "Télécoms",
  "cas": "GénAI relation client et réseau ; accords avec fournisseurs de modèles européens",
  "type": "chatbot_client", "stade": "pilote", "annee": 2024, "population": "grand_public",
  "drapeaux": {"chatbot": True, "gpai": True, "donnees_perso": True},
  "sources": [{"editeur": "Orange", "titre": "Stratégie IA (communiqués)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Telefónica", "pays": "ES", "secteur": "Télécoms",
  "cas": "Plateforme interne « Kernel » et génAI multi-métiers ; signataire du Pacte IA",
  "type": "assistant_llm", "stade": "production", "annee": 2024, "population": "salaries",
  "drapeaux": {"gpai": True, "donnees_perso": True},
  "signaux": [{"titre": "Signataire du Pacte sur l'IA de la Commission (engagements anticipés)", "sens": "+", "preuve": "officiel", "date": "2024-09"}],
  "sources": [{"editeur": "Commission européenne", "titre": "Liste des signataires du Pacte sur l'IA", "date": "2024-09", "preuve": "officiel"}]},
 {"entreprise": "SAP", "pays": "DE", "secteur": "Éditeur logiciel",
  "cas": "Copilote Joule intégré aux suites (fournisseur de SIA à des milliers d'entreprises UE) ; signataire du Pacte IA",
  "type": "assistant_llm", "stade": "echelle", "annee": 2024, "population": "b2b",
  "drapeaux": {"gpai": True},
  "signaux": [{"titre": "Signataire du Pacte sur l'IA de la Commission", "sens": "+", "preuve": "officiel", "date": "2024-09"}],
  "sources": [{"editeur": "SAP / Commission européenne", "titre": "Joule ; liste des signataires du Pacte IA", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Spotify", "pays": "SE", "secteur": "Médias",
  "cas": "Recommandation à l'échelle et DJ vocal génératif (voix clonée marquée)",
  "type": "chatbot_client", "stade": "echelle", "annee": 2024, "population": "grand_public",
  "drapeaux": {"generation_contenu": True, "gpai": True, "donnees_perso": True},
  "sources": [{"editeur": "Spotify", "titre": "AI DJ (communication produit)", "date": "2024", "preuve": "officiel"}]},

 # ── ÉLARGISSEMENT GÉOGRAPHIQUE — autres États membres ─────────────────────
 {"entreprise": "KBC", "pays": "BE", "secteur": "Banque",
  "cas": "Assistante numérique « Kate » : parcours client et actes bancaires automatisés",
  "type": "chatbot_client", "stade": "echelle", "annee": 2024, "population": "grand_public",
  "drapeaux": {"chatbot": True, "donnees_perso": True, "gpai": True},
  "sources": [{"editeur": "KBC", "titre": "Kate — résultats d'adoption (communications)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Ryanair", "pays": "IE", "secteur": "Transport aérien",
  "cas": "Tarification dynamique et assistance client automatisée",
  "type": "optimisation_predictive", "stade": "production", "annee": 2024, "population": "grand_public",
  "drapeaux": {"chatbot": True, "donnees_perso": True},
  "sources": [{"editeur": "presse économique", "titre": "Pricing algorithmique du transport aérien", "date": "2024", "preuve": "presse"}]},
 {"entreprise": "EDP", "pays": "PT", "secteur": "Énergie",
  "cas": "Maintenance prédictive des parcs éoliens et solaires",
  "type": "optimisation_predictive", "stade": "production", "annee": 2024, "population": "b2b",
  "drapeaux": {"infrastructure_critique": True},
  "sources": [{"editeur": "EDP", "titre": "IA pour les renouvelables (communication)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Erste Group", "alias": ["Erste Group", "Erste Bank"], "pays": "AT", "secteur": "Banque",
  "cas": "Conseiller numérique George : recommandations financières personnalisées et génAI",
  "type": "chatbot_client", "stade": "production", "annee": 2024, "population": "grand_public",
  "drapeaux": {"chatbot": True, "gpai": True, "donnees_perso": True},
  "sources": [{"editeur": "Erste Group", "titre": "George — assistants financiers (communication)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Nokia", "pays": "FI", "secteur": "Équipementier télécom",
  "cas": "Réseaux autonomes : détection d'anomalies et optimisation par ML (offre et usage interne)",
  "type": "optimisation_predictive", "stade": "echelle", "annee": 2024, "population": "b2b",
  "drapeaux": {"infrastructure_critique": True},
  "sources": [{"editeur": "Nokia", "titre": "Autonomous networks / AVA (communication)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Bolt", "pays": "EE", "secteur": "Plateformes",
  "cas": "Affectation algorithmique des courses et détection de fraude conducteurs",
  "type": "surveillance_salaries", "stade": "echelle", "annee": 2024, "population": "salaries",
  "drapeaux": {"rh": True, "donnees_perso": True},
  "sources": [{"editeur": "presse tech", "titre": "Gestion algorithmique des plateformes baltes", "date": "2024", "preuve": "presse"}]},
 {"entreprise": "Żabka", "pays": "PL", "secteur": "Distribution",
  "cas": "Magasins autonomes Nano : vision par ordinateur pour l'encaissement sans caisse",
  "type": "vision_industrielle", "stade": "echelle", "annee": 2024, "population": "grand_public",
  "drapeaux": {"donnees_perso": True},
  "sources": [{"editeur": "Żabka Group", "titre": "Réseau Nano (communications)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Škoda Auto", "pays": "CZ", "secteur": "Automobile",
  "cas": "Contrôle qualité par vision en ligne de production (Magic Eye)",
  "type": "vision_industrielle", "stade": "production", "annee": 2024, "population": "salaries",
  "drapeaux": {},
  "sources": [{"editeur": "Škoda Auto", "titre": "IA en production (communication)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Novo Nordisk", "pays": "DK", "secteur": "Pharmaceutique",
  "cas": "Découverte de molécules assistée par IA (partenariats calcul intensif)",
  "type": "optimisation_predictive", "stade": "pilote", "annee": 2024, "population": "b2b",
  "drapeaux": {},
  "signaux": [{"titre": "Usage R&D scientifique : exemption partielle art. 2 §6 documentée", "sens": "+", "preuve": "officiel", "date": "2024"}],
  "sources": [{"editeur": "Novo Nordisk", "titre": "IA en découverte de médicaments (communication)", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "OTP Bank", "pays": "HU", "secteur": "Banque",
  "cas": "Chatbot client et scoring interne (déploiement régional CEE)",
  "type": "chatbot_client", "stade": "production", "annee": 2024, "population": "grand_public",
  "drapeaux": {"chatbot": True, "donnees_perso": True},
  "sources": [{"editeur": "presse bancaire CEE", "titre": "Digitalisation OTP", "date": "2024", "preuve": "presse"}]},
 {"entreprise": "eMAG", "pays": "RO", "secteur": "E-commerce",
  "cas": "Recommandation produits et génération de contenu catalogue",
  "type": "assistant_llm", "stade": "production", "annee": 2024, "population": "grand_public",
  "drapeaux": {"generation_contenu": True, "gpai": True, "donnees_perso": True},
  "sources": [{"editeur": "presse tech roumaine", "titre": "IA chez eMAG", "date": "2024", "preuve": "presse"}]},

 # ── SIGNAUX RÉGLEMENTAIRES STRUCTURANTS (fournisseurs et pratiques) ────────
 {"entreprise": "OpenAI (fournisseur, effets UE)", "pays": "IT", "secteur": "Fournisseur GPAI",
  "cas": "ChatGPT : traitement des données des utilisateurs européens",
  "type": "assistant_llm", "stade": "echelle", "annee": 2024, "population": "grand_public",
  "drapeaux": {"gpai": True, "donnees_perso": True},
  "signaux": [{"titre": "Sanction Garante 15 M€ (base légale, information, mineurs)", "sens": "-", "preuve": "decision", "date": "2024-12"}],
  "sources": [{"editeur": "Garante per la protezione dei dati personali", "titre": "Provvedimento ChatGPT (communiqué)", "date": "2024-12", "preuve": "decision"}]},
 {"entreprise": "Clearview AI (fournisseur, effets UE)", "pays": "FR", "secteur": "Fournisseur biométrie",
  "cas": "Base de reconnaissance faciale constituée par moissonnage d'images en ligne",
  "type": "biometrie", "stade": "echelle", "annee": 2023, "population": "grand_public",
  "drapeaux": {"scraping_facial": True, "donnees_sensibles": True},
  "signaux": [{"titre": "Astreinte CNIL 5,2 M€ (après sanction 20 M€) ; sanctions homologues NL/IT/GR", "sens": "-", "preuve": "decision", "date": "2023-05"}],
  "sources": [{"editeur": "CNIL", "titre": "Liquidation d'astreinte Clearview AI", "date": "2023-05", "preuve": "decision"}]},
 {"entreprise": "Worldcoin / World (Tools for Humanity)", "alias": ["Worldcoin"], "pays": "DE", "secteur": "Fournisseur biométrie",
  "cas": "Collecte d'iris contre jetons (orbs) auprès du grand public européen",
  "type": "biometrie", "stade": "echelle", "annee": 2024, "population": "grand_public",
  "drapeaux": {"biometrie_id": True, "donnees_sensibles": True},
  "signaux": [{"titre": "Injonctions BayLDA (DE) ; suspensions ES/PT par les autorités", "sens": "-", "preuve": "decision", "date": "2024"}],
  "sources": [{"editeur": "BayLDA / AEPD / CNPD", "titre": "Mesures d'urgence biométrie Worldcoin", "date": "2024", "preuve": "decision"}]},
 {"entreprise": "Replika (Luka Inc., effets UE)", "pays": "IT", "secteur": "Fournisseur IA affective",
  "cas": "Compagnon conversationnel affectif accessible aux mineurs",
  "type": "chatbot_client", "stade": "echelle", "annee": 2023, "population": "grand_public",
  "drapeaux": {"chatbot": True, "gpai": True, "donnees_sensibles": True},
  "signaux": [{"titre": "Blocage Garante (2023) puis sanction 5 M€ (2025)", "sens": "-", "preuve": "decision", "date": "2023/2025"}],
  "sources": [{"editeur": "Garante", "titre": "Mesures Replika", "date": "2023-02", "preuve": "decision"}]},
 {"entreprise": "Mistral AI (fournisseur UE)", "pays": "FR", "secteur": "Fournisseur GPAI",
  "cas": "Modèles à usage général fournis aux entreprises européennes (Le Chat Enterprise, API)",
  "type": "assistant_llm", "stade": "echelle", "annee": 2024, "population": "b2b",
  "drapeaux": {"gpai": True},
  "signaux": [{"titre": "Adhésion au code de bonnes pratiques GPAI (juill. 2025)", "sens": "+", "preuve": "officiel", "date": "2025-07"}],
  "sources": [{"editeur": "Commission européenne / Mistral AI", "titre": "Code of Practice GPAI — signataires", "date": "2025-07", "preuve": "officiel"}]},

 # ── OBSERVATION DE LA TERRE — SIA bâtis sur des DONNÉES OUVERTES ───────────
 # Ces cas ont une particularité : leur matière première est publique et
 # gratuite (Copernicus, NASA, data.gouv.fr). Le lecteur peut donc, seul,
 # retrouver les images qui alimentent le système — ce qui n'est vrai d'aucun
 # autre cas du panel. Le champ `donnees_ouvertes` le rend explicite.
 {"entreprise": "ASP — Agence de services et de paiement", "pays": "FR", "secteur": "Administration / Agriculture",
  "cas": "Contrôles PAC par surveillance : séries Sentinel-1 et Sentinel-2 classées automatiquement pour vérifier les cultures déclarées sur chaque parcelle",
  "type": "observation_terre", "stade": "production", "annee": 2023, "population": "grand_public",
  "drapeaux": {"prestations_publiques": True, "donnees_perso": True},
  "donnees_ouvertes": ["copernicus"],
  "sources": [{"editeur": "Union européenne", "titre": "Règlement d'exécution (UE) 2022/1173 — système de suivi des surfaces par monitoring", "date": "2022-07", "preuve": "officiel"},
              {"editeur": "Commission européenne / JRC", "titre": "Area monitoring system — mise en œuvre par les organismes payeurs", "date": "2023", "preuve": "officiel"}]},
 {"entreprise": "FEGA — Fondo Español de Garantía Agraria", "pays": "ES", "secteur": "Administration / Agriculture",
  "cas": "Même dispositif de suivi des surfaces agricoles par imagerie Sentinel, appliqué aux aides espagnoles",
  "type": "observation_terre", "stade": "production", "annee": 2023, "population": "grand_public",
  "drapeaux": {"prestations_publiques": True, "donnees_perso": True},
  "donnees_ouvertes": ["copernicus"],
  "sources": [{"editeur": "Union européenne", "titre": "Règlement d'exécution (UE) 2022/1173 — obligation applicable à tous les organismes payeurs", "date": "2022-07", "preuve": "officiel"}]},
 {"entreprise": "Frontex", "pays": "PL", "secteur": "Sécurité / Frontières",
  "cas": "Services de fusion EUROSUR : détection d'embarcations et suivi d'activité par imagerie satellitaire aux frontières extérieures",
  "type": "observation_terre", "stade": "production", "annee": 2023, "population": "grand_public",
  "drapeaux": {"migration_frontieres": True, "donnees_perso": True},
  "donnees_ouvertes": ["copernicus"],
  "sources": [{"editeur": "Union européenne", "titre": "Règlement (UE) 2019/1896 — garde-frontières et garde-côtes, services de fusion EUROSUR", "date": "2019-11", "preuve": "officiel"},
              {"editeur": "Frontex", "titre": "EUROSUR Fusion Services — description des services d'observation", "date": "2023", "preuve": "officiel"}]},
 {"entreprise": "Commission européenne — service Copernicus de gestion des urgences (CEMS)", "pays": "BE", "secteur": "Sécurité civile",
  "cas": "Cartographie rapide de crise : délimitation assistée des zones inondées et brûlées à partir de Sentinel-1 et Sentinel-2",
  "type": "observation_terre", "stade": "production", "annee": 2023, "population": "b2b",
  "drapeaux": {},
  "donnees_ouvertes": ["copernicus"],
  "sources": [{"editeur": "Commission européenne / JRC", "titre": "Copernicus EMS — Rapid Mapping, portail public des activations", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "EMSA — Agence européenne pour la sécurité maritime", "pays": "PT", "secteur": "Maritime / Environnement",
  "cas": "CleanSeaNet : détection automatisée des nappes d'hydrocarbures sur imagerie radar Sentinel-1, alertes transmises aux États membres",
  "type": "observation_terre", "stade": "production", "annee": 2023, "population": "b2b",
  "drapeaux": {},
  "donnees_ouvertes": ["copernicus"],
  "sources": [{"editeur": "EMSA", "titre": "CleanSeaNet — service européen de détection des pollutions par imagerie satellitaire", "date": "2024", "preuve": "officiel"}]},
 {"entreprise": "Kayrros", "pays": "FR", "secteur": "Environnement / Analytique",
  "cas": "Détection des super-émetteurs de méthane par analyse des colonnes Sentinel-5P, exploitée par des acteurs publics et privés",
  "type": "observation_terre", "stade": "production", "annee": 2023, "population": "b2b",
  "drapeaux": {},
  "donnees_ouvertes": ["copernicus"],
  "sources": [{"editeur": "presse spécialisée (énergie, climat)", "titre": "Détection satellitaire des fuites de méthane à partir des données Copernicus", "date": "2023/2024", "preuve": "presse"}]},
 {"entreprise": "ECMWF (organisation intergouvernementale, calcul à Bologne)", "pays": "IT", "secteur": "Météorologie",
  "cas": "AIFS : modèle de prévision météorologique appris sur la réanalyse ERA5 du service Copernicus climat, passé en exploitation",
  "type": "observation_terre", "stade": "production", "annee": 2025, "population": "b2b",
  "drapeaux": {},
  "donnees_ouvertes": ["copernicus"],
  "sources": [{"editeur": "ECMWF", "titre": "Artificial Intelligence Forecasting System — passage en exploitation", "date": "2025-02", "preuve": "officiel"}]},
]

# ═══════════════════════════════════════════════════════════════════════════
# 6. COUCHE PAYS — autorités, stratégie, cyber, état AI Act (UE-27)
#    `precision` marque ce qui reste mouvant (désignations art. 70 en cours
#    d'ici aux échéances) : mieux vaut un champ daté qu'une certitude fausse.
# ═══════════════════════════════════════════════════════════════════════════

PAYS_UE = {
 "FR": {"nom": "France", "cyber": "ANSSI", "dpa": "CNIL",
        "autorite_ia": "coordination DGE ; CNIL positionnée sur les SIA traitant des données personnelles",
        "strategie": "Stratégie nationale IA (2018, actualisée — France 2030)",
        "notes": "ANSSI : recommandations sécurité génAI (2024). Bac à sable : dispositifs sectoriels CNIL.",
        "precision": "désignation art. 70 à confirmer"},
 "DE": {"nom": "Allemagne", "cyber": "BSI", "dpa": "BfDI + Länder",
        "autorite_ia": "Bundesnetzagentur pressentie (surveillance du marché)",
        "strategie": "KI-Strategie (2018, act. 2020)",
        "notes": "BSI : publications sécurité IA ; BayLDA actif sur la biométrie.",
        "precision": "désignation art. 70 à confirmer"},
 "IT": {"nom": "Italie", "cyber": "ACN", "dpa": "Garante",
        "autorite_ia": "ACN + AgID désignées par la loi IA nationale (2025)",
        "strategie": "Strategia italiana IA (2024)",
        "notes": "Garante très actif (ChatGPT, Replika) ; première loi IA nationale d'un État membre.",
        "precision": "documenté (loi 2025)"},
 "ES": {"nom": "Espagne", "cyber": "CCN / INCIBE", "dpa": "AEPD",
        "autorite_ia": "AESIA (première agence IA dédiée de l'UE, 2023)",
        "strategie": "ENIA (2020) + bac à sable réglementaire pionnier (2023-2024)",
        "notes": "Bac à sable AI Act pilote pour la Commission.",
        "precision": "documenté"},
 "NL": {"nom": "Pays-Bas", "cyber": "NCSC-NL", "dpa": "Autoriteit Persoonsgegevens",
        "autorite_ia": "AP (coordination algorithmes) + RDI",
        "strategie": "Strategisch Actieplan AI (2019)",
        "notes": "AP publie un rapport semestriel sur les risques algorithmiques.",
        "precision": "documenté"},
 "BE": {"nom": "Belgique", "cyber": "CCB", "dpa": "APD/GBA",
        "autorite_ia": "SPF Économie pressenti", "strategie": "Plan national IA (2022)",
        "notes": "", "precision": "désignation à confirmer"},
 "SE": {"nom": "Suède", "cyber": "MSB / NCSC-SE", "dpa": "IMY",
        "autorite_ia": "IMY + agences sectorielles", "strategie": "Nationell inriktning AI (2018)",
        "notes": "", "precision": "désignation à confirmer"},
 "DK": {"nom": "Danemark", "cyber": "CFCS", "dpa": "Datatilsynet",
        "autorite_ia": "Digitaliseringsstyrelsen", "strategie": "Stratégie IA (2019)",
        "notes": "Premier pays à adopter la loi d'application AI Act (2024).", "precision": "documenté"},
 "FI": {"nom": "Finlande", "cyber": "Traficom/NCSC-FI", "dpa": "Tietosuojavaltuutettu",
        "autorite_ia": "Traficom pressentie", "strategie": "AI 4.0", "notes": "", "precision": "à confirmer"},
 "PL": {"nom": "Pologne", "cyber": "NASK / CERT.PL", "dpa": "UODO",
        "autorite_ia": "Commission IA (projet de loi 2024-2025)", "strategie": "Polityka AI (2020)",
        "notes": "", "precision": "projet en cours"},
 "PT": {"nom": "Portugal", "cyber": "CNCS", "dpa": "CNPD",
        "autorite_ia": "ANACOM pressentie", "strategie": "AI Portugal 2030", "notes": "", "precision": "à confirmer"},
 "IE": {"nom": "Irlande", "cyber": "NCSC-IE", "dpa": "DPC",
        "autorite_ia": "répartition multi-régulateurs annoncée (2024)", "strategie": "AI - Here for Good (2021)",
        "notes": "DPC : interlocuteur des grands fournisseurs (sièges UE).", "precision": "documenté"},
 "AT": {"nom": "Autriche", "cyber": "GovCERT/DSB", "dpa": "DSB",
        "autorite_ia": "RTR (KI-Servicestelle, 2024)", "strategie": "AIM AT 2030",
        "notes": "Point de contact IA opérationnel dès 2024.", "precision": "documenté"},
 "CZ": {"nom": "Tchéquie", "cyber": "NÚKIB", "dpa": "ÚOOÚ",
        "autorite_ia": "à désigner", "strategie": "NAIS (2019)", "notes": "", "precision": "à confirmer"},
 "RO": {"nom": "Roumanie", "cyber": "DNSC", "dpa": "ANSPDCP",
        "autorite_ia": "à désigner", "strategie": "Stratégie IA (2024)", "notes": "", "precision": "à confirmer"},
 "GR": {"nom": "Grèce", "cyber": "NCSA", "dpa": "HDPA", "autorite_ia": "à désigner",
        "strategie": "Stratégie IA (2024)", "notes": "", "precision": "à confirmer"},
 "HU": {"nom": "Hongrie", "cyber": "NKI", "dpa": "NAIH", "autorite_ia": "à désigner",
        "strategie": "MI Stratégia (2020)", "notes": "", "precision": "à confirmer"},
 "SK": {"nom": "Slovaquie", "cyber": "NBU", "dpa": "ÚOOÚ SR", "autorite_ia": "à désigner",
        "strategie": "2019", "notes": "", "precision": "à confirmer"},
 "SI": {"nom": "Slovénie", "cyber": "SI-CERT", "dpa": "IP-RS", "autorite_ia": "à désigner",
        "strategie": "NpUI (2021)", "notes": "", "precision": "à confirmer"},
 "HR": {"nom": "Croatie", "cyber": "SOA/ZSIS", "dpa": "AZOP", "autorite_ia": "à désigner",
        "strategie": "2025 (plan)", "notes": "", "precision": "à confirmer"},
 "BG": {"nom": "Bulgarie", "cyber": "CERT Bulgaria", "dpa": "CPDP", "autorite_ia": "à désigner",
        "strategie": "2020", "notes": "", "precision": "à confirmer"},
 "LT": {"nom": "Lituanie", "cyber": "NKSC", "dpa": "VDAI", "autorite_ia": "Inovacijų agentūra pressentie",
        "strategie": "2019", "notes": "Écosystème fintech dense (Revolut UAB).", "precision": "à confirmer"},
 "LV": {"nom": "Lettonie", "cyber": "CERT.LV", "dpa": "DVI", "autorite_ia": "à désigner",
        "strategie": "2020", "notes": "", "precision": "à confirmer"},
 "EE": {"nom": "Estonie", "cyber": "RIA", "dpa": "AKI", "autorite_ia": "MKM / RIA",
        "strategie": "Kratid (2019, act.)", "notes": "Administration numérique pionnière.", "precision": "à confirmer"},
 "LU": {"nom": "Luxembourg", "cyber": "NC3/CIRCL", "dpa": "CNPD", "autorite_ia": "à désigner",
        "strategie": "AI4Gov (2019)", "notes": "", "precision": "à confirmer"},
 "MT": {"nom": "Malte", "cyber": "CSA Malta", "dpa": "IDPC", "autorite_ia": "MDIA",
        "strategie": "Malta AI (2019)", "notes": "MDIA : certification volontaire IA dès 2019.", "precision": "documenté"},
 "CY": {"nom": "Chypre", "cyber": "DSA/CSIRT-CY", "dpa": "Commissioner",
        "autorite_ia": "à désigner", "strategie": "2020", "notes": "", "precision": "à confirmer"},
}

# ═══════════════════════════════════════════════════════════════════════════
# 6 bis. LES TROIS PAYS TIERS DU PARC — Suisse, Norvège, Royaume-Uni
#
#    POURQUOI ILS ENTRENT ICI. Le référentiel des centres de données y recense
#    quarante-trois sites — neuf en Suisse, huit en Norvège, vingt-six au
#    Royaume-Uni. Les laisser en gris sur les cartes revenait à les traiter
#    comme des taches blanches alors qu'ils portent une part réelle du parc,
#    et à rendre leurs tuiles d'empreinte cliquables sur une fiche vide.
#
#    POURQUOI ILS RESTENT À PART. Ce ne sont PAS des États membres, et
#    l'écrire à leur place serait une faute lourde : le règlement IA ne
#    s'applique pas de la même façon dans les trois, et pas du tout dans deux
#    d'entre eux. Chacun porte donc `ue: False` et un champ `regime` qui dit
#    quel droit s'applique — la carte les colore, elle ne les naturalise pas.
#
#    CE QUE ZÉRO CAS SIGNIFIE POUR EUX. Le panel ne recense que des systèmes
#    déployés dans l'Union : un compte nul chez eux ne veut pas dire qu'il n'y
#    a pas d'IA, il veut dire qu'ils sont hors du champ d'observation. C'est
#    une nuance que l'interface doit porter, sans quoi la carte publierait une
#    absence pour un fait.
# ═══════════════════════════════════════════════════════════════════════════

PAYS_TIERS = {
 "CH": {"nom": "Suisse", "ue": False, "cyber": "OFCS (Office fédéral de la cybersécurité)",
        "dpa": "PFPDT (Préposé fédéral à la protection des données et à la transparence)",
        "autorite_ia": "aucune autorité transversale — approche sectorielle assumée",
        "strategie": "Le Conseil fédéral a décidé le 12 février 2025 de ratifier la "
                     "Convention-cadre du Conseil de l'Europe sur l'IA et a chargé le "
                     "DFJP d'un avant-projet de loi mis en consultation d'ici fin 2026.",
        "regime": "Hors UE ET hors EEE : le règlement IA ne s'applique PAS en Suisse. "
                  "Il s'impose en revanche à tout fournisseur suisse qui met un système "
                  "sur le marché de l'Union ou dont la sortie y est utilisée (art. 2). "
                  "Le socle actuel est la LPD révisée, en vigueur depuis le 1er septembre 2023.",
        "notes": "Un hébergement en Suisse place les données hors de la juridiction de "
                 "l'Union — c'est un argument commercial, et une contrainte de transfert.",
        "precision": "documenté (décision du Conseil fédéral, 12 février 2025)"},
 "NO": {"nom": "Norvège", "ue": False, "cyber": "NSM / NorCERT",
        "dpa": "Datatilsynet",
        "autorite_ia": "Nkom (autorité des communications) désignée autorité "
                       "coordinatrice de surveillance du marché ; Datatilsynet exploite "
                       "un bac à sable IA",
        "strategie": "Nasjonal strategi for kunstig intelligens (2020)",
        "regime": "Membre de l'EEE : le règlement IA est réputé pertinent pour l'EEE et "
                  "sera repris en droit norvégien. La loi nationale (KI-loven) a été mise "
                  "en consultation en juin 2025 pour une entrée en vigueur visée à l'été "
                  "2026 ; le calendrier a glissé, les adaptations EEE restant en "
                  "négociation. Le RGPD, lui, s'applique déjà par l'EEE.",
        "notes": "Le seul des trois qui convergera vers le régime de l'Union.",
        "precision": "documenté (consultation publique, juin 2025)"},
 "GB": {"nom": "Royaume-Uni", "ue": False, "cyber": "NCSC",
        "dpa": "ICO",
        "autorite_ia": "aucune autorité transversale — régulateurs sectoriels (ICO, FCA, "
                       "Ofcom, CMA, MHRA) ; l'AI Security Institute évalue les modèles "
                       "de frontière mais n'est pas un régulateur de marché",
        "strategie": "Livre blanc « A pro-innovation approach to AI regulation » (2023), "
                     "réaffirmé en février 2025 : réguler à l'usage, par les régulateurs "
                     "sectoriels existants, plutôt que par une loi transversale.",
        "regime": "Pays tiers depuis le retrait de l'Union : aucun équivalent du "
                  "règlement IA n'est en vigueur. L'ICO est tenu de produire un code de "
                  "pratique contraignant sur l'IA et les décisions automatisées.",
        "notes": "Premier marché européen de colocation, et le seul du panel où aucune "
                 "loi transversale sur l'IA n'est annoncée à échéance certaine.",
        "precision": "documenté (livre blanc 2023, position gouvernementale février 2025)"},
}

# Ce que les cartes et les fiches consomment : les trente pays, chacun sachant
# s'il est membre. Les deux dictionnaires restent séparés à la source pour que
# `PAYS_UE` continue de vouloir dire « les Vingt-Sept », et rien d'autre.
PAYS_CARTE = dict(PAYS_UE, **PAYS_TIERS)

# ═══════════════════════════════════════════════════════════════════════════
# 7. ASSEMBLAGE — enrichissement, agrégats, sortie API
# ═══════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════
# 5 bis. LOCALISATION DES ORGANISATIONS
#
#    CE QUE LE POINT DIT : où se trouve l'organisation qui déploie le système
#    — son siège ou son site principal.
#    CE QU'IL NE DIT PAS : où le système tourne. Un modèle entraîné à Paris
#    peut s'exécuter dans un centre de données irlandais et servir vingt pays.
#    Confondre les deux serait une erreur de lecture, et la carte le dit.
#
#    Quatre niveaux de précision, jamais mélangés :
#      siege      siège social ou site principal de l'organisation
#      site       site précisément documenté par le cas lui-même
#      national   dispositif sans point unique (contrôles nationaux, secteur
#                 entier) — rattaché au centre du pays, pas à une ville
#      sans_site  fournisseur hors UE dont seuls les EFFETS sont dans l'Union :
#                 le rattachement au pays est celui de l'autorité qui a agi,
#                 il n'y a aucun site à pointer
#
#    La table est tenue à part du panel : reprendre 72 fiches à la main pour
#    y glisser deux champs serait une source d'erreurs silencieuses.
# ═══════════════════════════════════════════════════════════════════════════

VILLES = {
    "Paris": [48.857, 2.352], "Toulouse": [43.604, 1.444], "Lille": [50.629, 3.057],
    "Madrid": [40.417, -3.704], "Santander": [43.462, -3.810], "Bilbao": [43.263, -2.935],
    "Amsterdam": [52.374, 4.892], "Veldhoven": [51.418, 5.404],
    "Munich": [48.137, 11.575], "Erlangen": [49.598, 11.004], "Wolfsburg": [52.423, 10.787],
    "Stuttgart": [48.776, 9.183], "Bonn": [50.735, 7.100], "Cologne": [50.937, 6.960],
    "Berlin": [52.520, 13.405], "Hambourg": [53.551, 9.994], "Walldorf": [49.305, 8.643],
    "Stockholm": [59.329, 18.069], "Älmhult": [56.551, 14.140],
    "Turin": [45.070, 7.687], "Rome": [41.903, 12.496], "Bologne": [44.494, 11.343],
    "Vilnius": [54.687, 25.280], "Varsovie": [52.230, 21.012], "Lisbonne": [38.722, -9.139],
    "Bruxelles": [50.851, 4.352], "Dublin": [53.350, -6.260], "Vienne": [48.208, 16.373],
    "Espoo": [60.205, 24.656], "Tallinn": [59.437, 24.754], "Copenhague": [55.676, 12.568],
    "Mladá Boleslav": [50.412, 14.904], "Budapest": [47.498, 19.040], "Bucarest": [44.427, 26.103],
}

# entreprise → (ville, précision). `None` en ville = pas de point de ville.
SITES = {
    "BNP Paribas": ("Paris", "siege"),
    "AXA": ("Paris", "siege"),
    "BBVA": ("Madrid", "siege"),
    "Santander": ("Santander", "siege"),
    "ING": ("Amsterdam", "siege"),
    "Klarna": ("Stockholm", "siege"),
    "Allianz": ("Munich", "siege"),
    "Munich Re": ("Munich", "siege"),
    "Intesa Sanpaolo": ("Turin", "siege"),
    "Revolut": ("Vilnius", "siege"),
    "Randstad": ("Amsterdam", "siege"),
    "Siemens": ("Munich", "siege"),
    "Amazon France Logistique": (None, "national"),
    "Secteur centres d'appels (plusieurs opérateurs)": (None, "national"),
    "Doctolib": ("Paris", "siege"),
    "Philips": ("Amsterdam", "siege"),
    "Siemens Healthineers": ("Erlangen", "siege"),
    "Owkin": ("Paris", "siege"),
    "Kry / Livi": ("Stockholm", "siege"),
    "Airbus": ("Toulouse", "site"),
    "Thales": ("Paris", "siege"),
    "Renault Group": ("Paris", "siege"),
    "Stellantis": ("Amsterdam", "siege"),
    "Volkswagen": ("Wolfsburg", "site"),
    "BMW": ("Munich", "siege"),
    "Bosch": ("Stuttgart", "siege"),
    "ASML": ("Veldhoven", "site"),
    "Schneider Electric": ("Paris", "siege"),
    "Enel": ("Rome", "siege"),
    "Iberdrola": ("Bilbao", "siege"),
    "TotalEnergies": ("Paris", "siege"),
    "Vattenfall": ("Stockholm", "siege"),
    "SNCF": ("Paris", "siege"),
    "DHL Group": ("Bonn", "siege"),
    "Maersk": ("Copenhague", "siege"),
    "Lufthansa Group": ("Cologne", "siege"),
    "Plateformes VTC / livraison (Uber, Bolt, Glovo…)": (None, "national"),
    "Zalando": ("Berlin", "siege"),
    "Carrefour": ("Paris", "siege"),
    "IKEA (Ingka)": ("Älmhult", "site"),
    "Otto Group": ("Hambourg", "siege"),
    "Decathlon": ("Lille", "siege"),
    "Deutsche Telekom": ("Bonn", "siege"),
    "Orange": ("Paris", "siege"),
    "Telefónica": ("Madrid", "siege"),
    "SAP": ("Walldorf", "siege"),
    "Spotify": ("Stockholm", "siege"),
    "KBC": ("Bruxelles", "siege"),
    "Ryanair": ("Dublin", "siege"),
    "EDP": ("Lisbonne", "siege"),
    "Erste Group": ("Vienne", "siege"),
    "Nokia": ("Espoo", "siege"),
    "Bolt": ("Tallinn", "siege"),
    "Żabka": ("Varsovie", "siege"),
    "Škoda Auto": ("Mladá Boleslav", "site"),
    "Novo Nordisk": ("Copenhague", "siege"),
    "OTP Bank": ("Budapest", "siege"),
    "eMAG": ("Bucarest", "siege"),
    "OpenAI (fournisseur, effets UE)": (None, "sans_site"),
    "Clearview AI (fournisseur, effets UE)": (None, "sans_site"),
    "Worldcoin / World (Tools for Humanity)": (None, "sans_site"),
    "Replika (Luka Inc., effets UE)": (None, "sans_site"),
    "Mistral AI (fournisseur UE)": ("Paris", "siege"),
    "ASP — Agence de services et de paiement": (None, "national"),
    "FEGA — Fondo Español de Garantía Agraria": (None, "national"),
    "Frontex": ("Varsovie", "siege"),
    "Commission européenne — service Copernicus de gestion des urgences (CEMS)": ("Bruxelles", "siege"),
    "EMSA — Agence européenne pour la sécurité maritime": ("Lisbonne", "siege"),
    "Kayrros": ("Paris", "siege"),
    "ECMWF (organisation intergouvernementale, calcul à Bologne)": ("Bologne", "site"),
}

GEO_LIBELLE = {
    "siege": "siège ou site principal de l'organisation",
    "site": "site documenté par le cas",
    "national": "dispositif national ou sectoriel — aucun point unique",
    "sans_site": "fournisseur hors UE : rattachement à l'autorité qui a agi, aucun site à pointer",
}


def localiser(entreprise):
    """(ville, lat, lon, précision) pour une organisation du panel.

    Une organisation absente de la table est traitée comme « national » plutôt
    que placée au hasard : mieux vaut un point assumé au centre du pays qu'une
    coordonnée inventée que rien ne signale."""
    ville, prec = SITES.get(entreprise, (None, "national"))
    if ville and ville in VILLES:
        lat, lon = VILLES[ville]
        return ville, lat, lon, prec
    return None, None, None, prec if prec in GEO_LIBELLE else "national"


def _enrichir():
    """Classe et score chaque cas ; renvoie la liste enrichie (sans muter CAS)."""
    out = []
    for i, brut in enumerate(CAS):
        cas = copy.deepcopy(brut)
        classe, regles = classer_cas(cas)
        score, tiers, detail = scorer_cas(cas, classe)
        cas.update({
            "id": "sia-%03d" % (i + 1),
            "classe": classe,
            "classe_nom": CLASSES[classe]["nom"],
            "classe_rang": CLASSES[classe]["rang"],
            "echeance": CLASSES[classe]["echeance"],
            "regles": regles,
            "exposition": score,
            "exposition_tiers": tiers,
            "exposition_detail": [{"terme": t, "points": p} for t, p in detail],
            "type_nom": TYPES_SIA[cas["type"]]["nom"],
            "vulnerabilites": TYPES_SIA[cas["type"]]["vulnerabilites"],
            "referentiels_securite": TYPES_SIA[cas["type"]]["referentiels"],
            "pays_nom": PAYS_UE.get(cas["pays"], {}).get("nom", cas["pays"]),
        })
        ville, lat, lon, prec = localiser(cas["entreprise"])
        cas.update({"ville": ville, "lat": lat, "lon": lon,
                    "geo": prec, "geo_libelle": GEO_LIBELLE[prec]})
        cas.setdefault("signaux", [])
        out.append(cas)
    return out


def _agreger(cas_enrichis):
    par_pays, par_secteur, par_classe, par_stade, par_annee = {}, {}, {}, {}, {}
    # Cas dont la matière première est publique et gratuite : les seuls que le
    # lecteur peut remonter jusqu'à la donnée d'entrée sans rien demander.
    par_socle = {}
    for c in cas_enrichis:
        for s in (c.get("donnees_ouvertes") or []):
            par_socle[s] = par_socle.get(s, 0) + 1
    for c in cas_enrichis:
        p = par_pays.setdefault(c["pays"], {"pays": c["pays"], "nom": c["pays_nom"], "n": 0,
                                            "exposition_moy": 0.0, "haut_risque": 0, "interdit": 0})
        p["n"] += 1
        p["exposition_moy"] += c["exposition"]
        if c["classe"] == "haut_risque": p["haut_risque"] += 1
        if c["classe"] == "interdit": p["interdit"] += 1
        s = par_secteur.setdefault(c["secteur"], {"secteur": c["secteur"], "n": 0, "exposition_moy": 0.0,
                                                  "classes": {}})
        s["n"] += 1; s["exposition_moy"] += c["exposition"]
        s["classes"][c["classe"]] = s["classes"].get(c["classe"], 0) + 1
        par_classe[c["classe"]] = par_classe.get(c["classe"], 0) + 1
        par_stade[c["stade"]] = par_stade.get(c["stade"], 0) + 1
        par_annee[str(c["annee"])] = par_annee.get(str(c["annee"]), 0) + 1
    for p in par_pays.values():
        p["exposition_moy"] = round(p["exposition_moy"] / p["n"], 1)
    for s in par_secteur.values():
        s["exposition_moy"] = round(s["exposition_moy"] / s["n"], 1)
    return {
        "par_pays": sorted(par_pays.values(), key=lambda x: -x["n"]),
        "par_secteur": sorted(par_secteur.values(), key=lambda x: -x["n"]),
        "par_classe": par_classe,
        "par_stade": par_stade,
        "par_annee": dict(sorted(par_annee.items())),
        "par_socle_ouvert": par_socle,
        "n_socle_ouvert": sum(1 for c in cas_enrichis if c.get("donnees_ouvertes")),
    }


METHODOLOGIE = {
    "fenetre": FENETRE,
    "criteres_inclusion": [
        "cas identifiable (entreprise + usage + stade) documenté par une source publique nommée et datée",
        "déploiement, pilote, POC ou abandon situé dans l'UE ou à effets directs dans l'UE",
        "diversité recherchée : secteurs, pays, classes de risque, stades — le panel vaut par sa représentativité, pas par son volume",
    ],
    "limites": [
        "PANEL, PAS RECENSEMENT : les déploiements non communiqués (majoritaires) n'y figurent pas — biais de publication assumé et signalé",
        "le score mesure l'EXPOSITION RÉGLEMENTAIRE du cas d'usage, jamais la conformité de l'entreprise (inauditables de l'extérieur)",
        "les classifications reposent sur les usages DÉCLARÉS ; un même outil peut changer de classe selon sa fonction exacte",
        "les désignations d'autorités nationales (art. 70) évoluent d'ici août 2026 : champ `precision` par pays",
    ],
    "referentiels": [
        "Règlement (UE) 2024/1689 (AI Act) — art. 5, 6, 50, annexes I et III ; échéances 2025-2027",
        "OWASP LLM Top 10 (2025) · MITRE ATLAS · ANSSI (recommandations génAI, 2024) · ENISA · BSI",
        "NIS 2, DORA, MDR, règlement Machines : sur-couches sectorielles citées par cas",
    ],
    "evolutions_prevues": [
        "raccordement à la base UE des systèmes à haut risque (art. 71) dès son ouverture",
        "flux autorités (CNIL, Garante, AP, AEPD, BSI…) et bases d'incidents (OCDE AIM, AIAAIC) en veille automatisée",
        "rapprochement avec le Registre IA de Sentinel : situer VOS systèmes dans le panel",
    ],
}

CREDITS = [
    "Décisions citées : CNIL, Garante, AEPD, BayLDA, Autoriteit Persoonsgegevens (sources primaires publiques)",
    "Communiqués et rapports des entreprises citées (sources officielles)",
    "Commission européenne : Pacte sur l'IA, code de bonnes pratiques GPAI, lignes directrices art. 5",
    "Référentiels sécurité : OWASP, MITRE ATLAS, ANSSI, ENISA, BSI",
]


# ═══════════════════════════════════════════════════════════════════════════
# 8. SIGNAUX EN CONTINU — flux d'autorités et d'institutions, rapprochés du panel
#
#    RÈGLE ABSOLUE : un titre de flux N'ALTÈRE JAMAIS un score. Les scores ne
#    reposent que sur des faits qualifiés à la main dans le référentiel. Le flux
#    alimente une file « à qualifier » : il signale, l'expert tranche, la version
#    suivante du référentiel intègre. Automatiser la détection sans automatiser
#    le jugement — c'est ce qui garde le module opposable.
#
#    Les quatre flux sont EXACTEMENT ceux que la veille de Sentinel interroge
#    déjà avec succès en production : aucun canal nouveau à fiabiliser.
# ═══════════════════════════════════════════════════════════════════════════

FLUX_SOURCES = [
    {"nom": "CNIL",        "url": "https://www.cnil.fr/fr/rss.xml"},
    {"nom": "ANSSI",       "url": "https://cyber.gouv.fr/feed"},
    {"nom": "EU AI Act",   "url": "https://artificialintelligenceact.eu/feed/"},
    {"nom": "Commission (stratégie numérique)", "url": "https://digital-strategy.ec.europa.eu/en/rss.xml"},
]

# Filtre thématique : CNIL et ANSSI publient bien au-delà de l'IA — on ne garde
# que ce qui la concerne. Liste volontairement large : un faux positif se lit
# en une seconde, un faux négatif est invisible.
_MOTS_IA = ["intelligence artificielle", "artificial intelligence", " ia ", "l'ia",
            " ai ", "ai act", "règlement ia", "algorith", "chatgpt", "openai",
            "modèle de langage", "llm", "généra", "generative", "gpai", "chatbot",
            "biométr", "biometric", "reconnaissance faciale", "facial recognition",
            "deepfake", "machine learning", "apprentissage automatique",
            # Centres de donnees : la couche infrastructure de /panorama se met
            # a jour par versions ; entre deux versions, les annonces passent
            # par la meme file « a qualifier » que les signaux IA.
            "data center", "data centre", "datacenter", "centre de données",
            "centres de données"]

_FLUX_TTL = 1800          # 30 min : le rythme des autorités, pas celui d'un ticker
_FLUX_RETRY = 300
_FLUX_CACHE = {"ts": 0.0, "ts_ok": 0.0, "data": None, "erreur": None}
_FLUX_LOCK = threading.Lock()


def _hors_ligne():
    return (os.environ.get("PAN_OFFLINE") or os.environ.get("OBS_OFFLINE") or "") in ("1", "true", "yes")


def _normaliser(t):
    t = unicodedata.normalize("NFD", str(t or ""))
    return "".join(c for c in t if not unicodedata.combining(c)).lower()


def _alias_panel():
    """[(alias_normalisé, alias_brut, id_cas, sensible_casse)] pour le rapprochement.

    Dérivé du nom d'entreprise (partie avant la parenthèse) sauf alias explicite.
    Les sigles courts (≤ 4 lettres : AXA, SAP, ING, KBC…) ne s'apparient qu'en
    respectant la casse : « ING » dans un titre, jamais « building »."""
    out = []
    for i, c in enumerate(CAS):
        cid = "sia-%03d" % (i + 1)
        aliases = c.get("alias")
        if aliases is None:
            nom = c["entreprise"].split(" (")[0].strip()
            aliases = [] if ("/" in nom or "plusieurs" in nom.lower() or "secteur" in nom.lower()) else [nom]
        for a in aliases:
            if len(a) < 3:
                continue
            out.append((_normaliser(a), a, cid, len(a) <= 4))
    return out


def _rapprocher(titre, alias):
    """Ids des cas dont un alias apparaît dans le titre (bordures de mots)."""
    trouves = []
    t_norm = _normaliser(titre)
    for a_norm, a_brut, cid, strict in alias:
        if strict:
            if re.search(r"\b" + re.escape(a_brut) + r"\b", titre):
                trouves.append(cid)
        elif re.search(r"\b" + re.escape(a_norm) + r"\b", t_norm):
            trouves.append(cid)
    return sorted(set(trouves))


def _lire_flux():
    """(items, None) ou (None, erreur). Réseau uniquement ici — jamais bloquant
    au-delà des délais courts, plafonds stricts, aucun identifiant."""
    import requests
    import feedparser
    alias = _alias_panel()
    items, erreurs = [], []
    for src in FLUX_SOURCES:
        try:
            r = requests.get(src["url"], headers={"User-Agent": "Sentinel-Panorama/1.0"}, timeout=6)
            if r.status_code != 200:
                erreurs.append("%s: HTTP %d" % (src["nom"], r.status_code))
                continue
            flux = feedparser.parse(r.content[:1_500_000])
            for e in (flux.entries or [])[:15]:
                titre = (e.get("title") or "").strip()
                if not titre:
                    continue
                texte = _normaliser(titre + " " + (e.get("summary") or "")[:300])
                if not any(m in " " + texte + " " for m in _MOTS_IA):
                    continue
                lien = e.get("link") or ""
                date = ""
                for k in ("published", "updated"):
                    if e.get(k):
                        date = str(e[k])[:16]
                        break
                items.append({"titre": titre[:200], "lien": lien[:300], "source": src["nom"],
                              "date": date, "cas_lies": _rapprocher(titre, alias)})
        except Exception as ex:
            erreurs.append("%s: %s" % (src["nom"], type(ex).__name__))
    if not items:
        return None, ("aucun flux exploitable — " + " ; ".join(erreurs))[:300] if erreurs else "flux vides"
    items = items[:40]
    return items, None


def _obtenir_flux():
    c = _FLUX_CACHE
    now = time.time()
    if c["data"] is not None and (now - c["ts_ok"] < _FLUX_TTL):
        return c
    if c["erreur"] is not None and (now - c["ts"] < _FLUX_RETRY):
        return c
    if not _FLUX_LOCK.acquire(blocking=False):
        return c        # une autre requête rafraîchit : on sert l'état courant
    try:
        now = time.time()
        if c["data"] is not None and (now - c["ts_ok"] < _FLUX_TTL):
            return c
        try:
            data, erreur = _lire_flux()
        except Exception as ex:
            data, erreur = None, type(ex).__name__
        c["ts"] = time.time()
        if erreur is None and data is not None:
            c["data"], c["ts_ok"], c["erreur"] = data, c["ts"], None
        else:
            c["erreur"] = erreur or "réponse vide"   # l'ancienne donnée est conservée
    finally:
        _FLUX_LOCK.release()
    return c


def rearmer():
    """Force le prochain accès à retenter les flux (?refresh=1). Ne vide pas la
    donnée déjà obtenue : forcer un essai ne doit jamais appauvrir l'affichage."""
    _FLUX_CACHE["ts_ok"] = 0.0
    _FLUX_CACHE["ts"] = 0.0
    _FLUX_CACHE["erreur"] = None


def _iso(ts):
    if not ts:
        return None
    return datetime.utcfromtimestamp(ts).isoformat() + "Z"


def assemble():
    cas = _enrichir()
    # Signaux en continu : cache paresseux, seed pur en mode hors-ligne.
    if _hors_ligne():
        fc = {"ts": 0.0, "ts_ok": 0.0, "data": None, "erreur": None}
    else:
        fc = _obtenir_flux()
    if fc["data"]:
        par_cas = {}
        for it in fc["data"]:
            for cid in it.get("cas_lies", []):
                par_cas.setdefault(cid, []).append(
                    {"titre": it["titre"], "lien": it["lien"], "source": it["source"], "date": it["date"]})
        flux = {"mode": "live", "count": len(fc["data"]), "items": fc["data"], "par_cas": par_cas,
                "note": "Titres bruts des flux d'autorités et d'institutions — À QUALIFIER : "
                        "aucun n'entre dans les scores tant qu'il n'est pas vérifié et versé au référentiel."}
    else:
        flux = {"mode": "seed", "count": 0, "items": [], "par_cas": {},
                "note": "Signaux non chargés (hors-ligne, premier accès ou flux injoignables) — voir `etat`."}
    etat_flux = {"ok": fc["erreur"] is None and fc["data"] is not None,
                 "derniere_maj": _iso(fc["ts_ok"]), "derniere_erreur": fc["erreur"],
                 "sources": [s["nom"] for s in FLUX_SOURCES], "ttl_s": _FLUX_TTL}
    return {
        "signaux_flux": flux,
        "etat": {"flux": etat_flux},
        "maj": datetime.utcnow().isoformat() + "Z",
        "version": VERSION,
        "titre": "Panorama des systèmes d'IA en entreprise — UE",
        "fenetre": FENETRE,
        "n_cas": len(cas),
        "n_pays": len({c["pays"] for c in cas}),
        "n_secteurs": len({c["secteur"] for c in cas}),
        "cas": cas,
        "agregats": _agreger(cas),
        "classes": CLASSES,
        "types": {k: {"nom": v["nom"]} for k, v in TYPES_SIA.items()},
        # Les cartes reçoivent les trente : vingt-sept membres et trois pays
        # tiers qui portent des sites. Chacun sait ce qu'il est — `ue: False`
        # pour les trois — et l'interface ne les confond jamais.
        "pays_ue": PAYS_CARTE,
        "pays_tiers": sorted(PAYS_TIERS),
        "methodologie": METHODOLOGIE,
        "credits": CREDITS,
    }


def sante():
    """Bloc 'panorama' pour /api/health : référentiel + fraîcheur des signaux."""
    now = time.time()
    return {"version": VERSION, "n_cas": len(CAS), "n_pays_ue": len(PAYS_UE),
            "n_pays_tiers": len(PAYS_TIERS), "n_pays_carte": len(PAYS_CARTE),
            "flux": {"ok": _FLUX_CACHE["erreur"] is None and _FLUX_CACHE["data"] is not None,
                     "items": len(_FLUX_CACHE["data"] or []),
                     "age_s": int(now - _FLUX_CACHE["ts_ok"]) if _FLUX_CACHE["ts_ok"] else None,
                     "ttl_s": _FLUX_TTL}}
