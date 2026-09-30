# -*- coding: utf-8 -*-
"""LE PROFIL IA GÉNÉRATIVE DU CADRE NIST — 211 ACTIONS, ET CE QU'ELLES FONT
AU TAUX DÉJÀ AFFICHÉ.

═══ CE MODULE N'EST PAS UNE TREIZIÈME NORME ═════════════════════════════
NIST AI 600-1 est un PROFIL de NIST AI 100-1, pas un second cadre. Ses 211
actions suggérées ne flottent pas : chacune se rattache à une sous-catégorie
du cadre, et le document ne se lit pas sans lui. Lui ouvrir un tiroir à part
dans « votre conformité réglementaire » aurait compté DEUX FOIS le même
cadre dans le taux global du cabinet — une maison qui travaille son AI RMF
aurait vu son indice monter deux fois pour un seul chantier.

Il se branche donc SOUS la norme qui existe déjà, et il n'ajoute aucune
part : il agit sur celles qui sont là.

═══ CE QU'IL FAIT AU TAUX, ET POURQUOI C'EST UN PLAFOND ═════════════════
Le cadre AI 100-1 se note par catégorie, de « absent » à « prouvé ». Ces
états ont été posés sur un système quelconque. Dès lors que le système est
GÉNÉRATIF, le profil attache à ces mêmes catégories des actions que le cadre
seul ne demandait pas — et une catégorie « prouvée » sans ces actions-là
n'est plus prouvée POUR CE SYSTÈME.

LE PROFIL NE RETIRE DONC RIEN AU TRAVAIL FAIT : IL PLAFONNE CE QU'ON PEUT
EN DIRE. C'est la même mécanique que les verrous de `conformite` — `brut`
reste, `taux` est le plus petit des deux. Concrètement, par catégorie :

    aucune action tenue          → l'état ne peut pas dépasser « amorcé »
    une partie des actions       → l'état ne peut pas dépasser « tenu »
    toutes les actions tenues    → l'état déclaré tient

Soustraire des points aurait été plus simple et plus faux : un plafond dit
« vous ne pouvez pas vous en prévaloir au-delà », une soustraction dit
« votre travail vaut moins », ce qui n'est pas vrai.

ET LE PLAFOND NE MONTE JAMAIS UN ÉTAT. Une catégorie « absente » au socle
reste absente, quand bien même les actions du profil seraient toutes
tenues : le profil suppose le cadre, il ne le remplace pas.

═══ CE QUE LE PROFIL NE DIT PAS DE 23 SOUS-CATÉGORIES ═══════════════════
49 des 72 sous-catégories portent au moins une action. LES 23 AUTRES N'EN
PORTENT AUCUNE, et cela se dit « sans objet POUR LE PROFIL » — jamais « non
couvertes ». La nuance décide d'un chantier : le NIST n'a rien de
particulier à ajouter là pour l'IA générative, ce n'est pas un trou.

═══ LES TROIS CONTRADICTIONS DU DOCUMENT, DÉCLARÉES ET NON MASQUÉES ═════
Le §3 d'AI 600-1 ne nomme pas toujours ses risques comme le §2 qui les
définit. Trois écarts ont été relevés à l'extraction ; les taire aurait
laissé croire à une table plus propre que le document :

  · « Harmful Bias AND Homogenization » au §3, « OR » au §2 — 57 actions
    en dépendaient, plus du quart de la table ;
  · « Environmental » au §3, « Environmental Impacts » au §2 — sans
    réconciliation, le cinquième risque paraissait orphelin ;
  · « Civil Rights violations », porté par GV-1.4-002, ne figure PAS parmi
    les douze. Il est conservé tel quel, hors liste, avec le numéro 0.

ET GV-1.1-002 N'EXISTE PAS. Il n'apparaît que dans le guide de lecture du
§3, comme exemple de codification. Le compte réel est 211, pas 212.

═══ DROITS ══════════════════════════════════════════════════════════════
AI 600-1 est une œuvre du gouvernement des États-Unis : elle se cite
librement. Les 211 actions sont donc reprises EN ANGLAIS, mot pour mot,
comme le sont déjà les 72 énoncés de sous-catégories — c'est le libellé
qu'un auditeur cherchera, et le traduire l'aurait rendu introuvable. Ce qui
est en français est le travail du cabinet : le plafond, le plan, et ce que
tout cela coûte.
"""
import nist_ai_rmf as _rmf


SOURCE = {
    "cle": "genai",
    "titre": "NIST AI 600-1 — AI RMF: Generative Artificial Intelligence "
             "Profile",
    "date": "2024-07",
    "doi": "https://doi.org/10.6028/NIST.AI.600-1",
    "droits": "Œuvre du gouvernement des États-Unis — libre de citation.",
    "lue": True,
    "apporte": "Les 211 actions suggérées du §3, chacune rattachée à une "
               "sous-catégorie du cadre AI 100-1 et aux risques qu'elle "
               "traite. Les douze risques eux-mêmes sont déjà dans "
               "`nist_ai_rmf` : ce module ne les redéclare pas.",
    "certifiable": False,
    "profil_de": "NIST AI 100-1",
}


# ═══════════════════════════════════════════════════════════════════════════
#  LES RÉCONCILIATIONS — CE QUE L'EXTRACTION A DÛ TRANCHER
# ═══════════════════════════════════════════════════════════════════════════
#
# ELLES VOYAGENT AVEC LE RÉFÉRENTIEL, pas en note de bas de fichier. Un
# lecteur qui recompte les actions d'un risque sur le PDF doit pouvoir
# retrouver le même nombre que l'écran, ou savoir pourquoi il diffère.

RECONCILIATIONS = (
    {"au_paragraphe_3": "Harmful Bias and Homogenization",
     "au_paragraphe_2": "Harmful Bias or Homogenization",
     "risque": 6, "actions": 57,
     "pourquoi": "Le §2 définit le risque avec « or ». C'est l'étiquette "
                 "la plus portée de la table : sans cette réconciliation, "
                 "aucune des douze ne reconnaissait 57 rattachements, et "
                 "l'extraction rendait des actions sans risque du tout."},
    {"au_paragraphe_3": "Environmental",
     "au_paragraphe_2": "Environmental Impacts",
     "risque": 5, "actions": 4,
     "pourquoi": "Le cinquième risque paraissait n'avoir aucune action, "
                 "alors qu'il en a quatre. Un risque orphelin à l'écran se "
                 "lit « rien à faire », ce qui est l'inverse."},
    {"au_paragraphe_3": "Civil Rights violations",
     "au_paragraphe_2": None,
     "risque": 0, "actions": 1,
     "pourquoi": "Cette étiquette ne figure pas parmi les douze risques du "
                 "§2. Elle est portée par la seule action GV-1.4-002 et "
                 "conservée telle quelle, hors liste : la réécrire en l'un "
                 "des douze aurait inventé un rattachement que le document "
                 "ne fait pas."},
)

# LE RISQUE ZÉRO N'EST PAS UN TREIZIÈME RISQUE — c'est une étiquette que le
# document emploie une fois sans l'avoir définie. Elle ne rend donc AUCUNE
# action applicable à elle seule : GV-1.4-002 entre dans le champ par les
# trois autres risques qu'elle porte, jamais par celle-ci.
HORS_DOUZE = {
    0: {"n": 0, "cle": "Civil Rights violations",
        "nom": "Atteintes aux droits civiques",
        "dit": "Étiquette employée au §3 d'AI 600-1 et absente des douze "
               "risques du §2. Affichée telle quelle, elle ne déclenche "
               "rien par elle-même."},
}


# ═══════════════════════════════════════════════════════════════════════════
#  LES 211 ACTIONS SUGGÉRÉES (AI 600-1, §3)
# ═══════════════════════════════════════════════════════════════════════════
#
# (code, sous-catégorie du cadre, énoncé d'origine, risques traités)
#
# LES RISQUES SONT DES NUMÉROS, ET C'EST VOULU. Écrits en toutes lettres,
# 211 fois, ils auraient pesé 18 Ko de chaînes qu'aucune garde ne peut
# éprouver autrement que par égalité de texte. En numéros, la garde les
# confronte aux douze de `nist_ai_rmf` ET recompte la distribution mesurée
# dans le document — une seule action déplacée fait tomber le module.
#
#   1 CBRN · 2 Confabulation · 3 Contenus dangereux · 4 Vie privée
#   5 Impacts environnementaux · 6 Biais et homogénéisation
#   7 Configuration humain-IA · 8 Intégrité de l'information
#   9 Sécurité de l'information · 10 Propriété intellectuelle
#   11 Contenus obscènes · 12 Chaîne de valeur  ·  0 hors des douze

ACTIONS = (

    # ── GOVERN 1.1 ──────────────────────────────────────────────────────
    ("GV-1.1-001", "GOVERN 1.1",
     "Align GAI development and use with applicable laws and "
     "regulations, including those related to data privacy, copyright "
     "and intellectual property law.",
     (4, 6, 10)),

    # ── GOVERN 1.2 ──────────────────────────────────────────────────────
    ("GV-1.2-001", "GOVERN 1.2",
     "Establish transparency policies and processes for documenting the "
     "origin and history of training data and generated data for GAI "
     "applications to advance digital content transparency, while "
     "balancing the proprietary nature of training approaches.",
     (4, 8, 10)),
    ("GV-1.2-002", "GOVERN 1.2",
     "Establish policies to evaluate risk-relevant capabilities of GAI "
     "and robustness of safety measures, both prior to deployment and on "
     "an ongoing basis, through internal and external evaluations.",
     (1, 9)),

    # ── GOVERN 1.3 ──────────────────────────────────────────────────────
    ("GV-1.3-001", "GOVERN 1.3",
     "Consider the following factors when updating or defining risk "
     "tiers for GAI: Abuses and impacts to information integrity; "
     "Dependencies between GAI and other IT or data systems; Harm to "
     "fundamental rights or public safety; Presentation of obscene, "
     "objectionable, offensive, discriminatory, invalid or untruthful "
     "output; Psychological impacts to humans (e.g., "
     "anthropomorphization, algorithmic aversion, emotional "
     "entanglement); Possibility for malicious use; Whether the system "
     "introduces significant new security vulnerabilities; Anticipated "
     "system impact on some groups compared to others; Unreliable "
     "decision making capabilities, validity, adaptability, and "
     "variability of GAI system performance over time.",
     (1, 3, 6, 8, 11, 12)),
    ("GV-1.3-002", "GOVERN 1.3",
     "Establish minimum thresholds for performance or assurance criteria "
     "and review as part of deployment approval (“go/”no-go”) policies, "
     "procedures, and processes, with reviewed processes and approval "
     "thresholds reflecting measurement of GAI capabilities and risks.",
     (1, 2, 3)),
    ("GV-1.3-003", "GOVERN 1.3",
     "Establish a test plan and response policy, before developing "
     "highly capable models, to periodically evaluate whether the model "
     "may misuse CBRN information or capabilities and/or offensive cyber "
     "capabilities.",
     (1, 9)),
    ("GV-1.3-004", "GOVERN 1.3",
     "Obtain input from stakeholder communities to identify unacceptable "
     "use, in accordance with activities in the AI RMF Map function.",
     (1, 3, 6, 11)),
    ("GV-1.3-005", "GOVERN 1.3",
     "Maintain an updated hierarchy of identified and expected GAI risks "
     "connected to contexts of GAI model advancement and use, "
     "potentially including specialized risk levels for GAI systems that "
     "address issues such as model collapse and algorithmic monoculture.",
     (6,)),
    ("GV-1.3-006", "GOVERN 1.3",
     "Reevaluate organizational risk tolerances to account for "
     "unacceptable negative risk (such as where significant negative "
     "impacts are imminent, severe harms are actually occurring, or "
     "large-scale risks could occur); and broad GAI negative risks, "
     "including: Immature safety or risk cultures related to AI and GAI "
     "design, development and deployment, public information integrity "
     "risks, including impacts on democratic processes, unknown "
     "long-term performance characteristics of GAI.",
     (1, 3, 8)),
    ("GV-1.3-007", "GOVERN 1.3",
     "Devise a plan to halt development or deployment of a GAI system "
     "that poses unacceptable negative risk. CBRN Information and "
     "Capability;",
     (8, 9)),

    # ── GOVERN 1.4 ──────────────────────────────────────────────────────
    ("GV-1.4-001", "GOVERN 1.4",
     "Establish policies and mechanisms to prevent GAI systems from "
     "generating CSAM, NCII or content that violates the law.",
     (3, 6, 11)),
    ("GV-1.4-002", "GOVERN 1.4",
     "Establish transparent acceptable use policies for GAI that address "
     "illegal use or applications of GAI.",
     (0, 1, 4, 11)),

    # ── GOVERN 1.5 ──────────────────────────────────────────────────────
    ("GV-1.5-001", "GOVERN 1.5",
     "Define organizational responsibilities for periodic review of "
     "content provenance and incident monitoring for GAI systems.",
     (8,)),
    ("GV-1.5-002", "GOVERN 1.5",
     "Establish organizational policies and procedures for after action "
     "reviews of GAI system incident response and incident disclosures, "
     "to identify gaps; Update incident response and incident disclosure "
     "processes as required.",
     (7, 9)),
    ("GV-1.5-003", "GOVERN 1.5",
     "Maintain a document retention policy to keep history for test, "
     "evaluation, validation, and verification (TEVV), and digital "
     "content transparency methods for GAI.",
     (8, 10)),

    # ── GOVERN 1.6 ──────────────────────────────────────────────────────
    ("GV-1.6-001", "GOVERN 1.6",
     "Enumerate organizational GAI systems for incorporation into AI "
     "system inventory and adjust AI system inventory requirements to "
     "account for GAI risks.",
     (9,)),
    ("GV-1.6-002", "GOVERN 1.6",
     "Define any inventory exemptions in organizational policies for GAI "
     "systems embedded into application software.",
     (12,)),
    ("GV-1.6-003", "GOVERN 1.6",
     "In addition to general model, governance, and risk information, "
     "consider the following items in GAI system inventory entries: Data "
     "provenance information (e.g., source, signatures, versioning, "
     "watermarks); Known issues reported from internal bug tracking or "
     "external information sharing resources (e.g., AI incident "
     "database, AVID, CVE, NVD, or OECD AI incident monitor); Human "
     "oversight roles and responsibilities; Special rights and "
     "considerations for intellectual property, licensed works, or "
     "personal, privileged, proprietary or sensitive data; Underlying "
     "foundation models, versions of underlying models, and access "
     "modes.",
     (4, 7, 8, 10, 12)),

    # ── GOVERN 1.7 ──────────────────────────────────────────────────────
    ("GV-1.7-001", "GOVERN 1.7",
     "Protocols are put in place to ensure GAI systems are able to be "
     "deactivated when necessary.",
     (9, 12)),
    ("GV-1.7-002", "GOVERN 1.7",
     "Consider the following factors when decommissioning GAI systems: "
     "Data retention requirements; Data security, e.g., containment, "
     "protocols, Data leakage after decommissioning; Dependencies "
     "between upstream, downstream, or other data, internet of things "
     "(IOT) or AI systems; Use of open-source data or models; Users’ "
     "emotional entanglement with GAI functions.",
     (7, 9, 12)),

    # ── GOVERN 2.1 ──────────────────────────────────────────────────────
    ("GV-2.1-001", "GOVERN 2.1",
     "Establish organizational roles, policies, and procedures for "
     "communicating GAI incidents and performance to AI Actors and "
     "downstream stakeholders (including those potentially impacted), "
     "via community or official resources (e.g., AI incident database, "
     "AVID, CVE, NVD, or OECD AI incident monitor).",
     (7, 12)),
    ("GV-2.1-002", "GOVERN 2.1",
     "Establish procedures to engage teams for GAI system incident "
     "response with diverse composition and responsibilities based on "
     "the particular incident type.",
     (6,)),
    ("GV-2.1-003", "GOVERN 2.1",
     "Establish processes to verify the AI Actors conducting GAI "
     "incident response tasks demonstrate and maintain the appropriate "
     "skills and training.",
     (7,)),
    ("GV-2.1-004", "GOVERN 2.1",
     "When systems may raise national security risks, involve national "
     "security professionals in mapping, measuring, and managing those "
     "risks.",
     (1, 3, 9)),
    ("GV-2.1-005", "GOVERN 2.1",
     "Create mechanisms to provide protections for whistleblowers who "
     "report, based on reasonable belief, when the organization violates "
     "relevant laws or poses a specific and empirically "
     "well-substantiated negative risk to public safety (or has already "
     "caused harm).",
     (1, 3)),

    # ── GOVERN 3.2 ──────────────────────────────────────────────────────
    ("GV-3.2-001", "GOVERN 3.2",
     "Policies are in place to bolster oversight of GAI systems with "
     "independent evaluations or assessments of GAI models or systems "
     "where the type and robustness of evaluations are proportional to "
     "the identified risks.",
     (1, 6)),
    ("GV-3.2-002", "GOVERN 3.2",
     "Consider adjustment of organizational roles and components across "
     "lifecycle stages of large or complex GAI systems, including: Test "
     "and evaluation, validation, and red-teaming of GAI systems; GAI "
     "content moderation; GAI system development and engineering; "
     "Increased accessibility of GAI tools, interfaces, and systems, "
     "Incident response and containment.",
     (6, 7, 9)),
    ("GV-3.2-003", "GOVERN 3.2",
     "Define acceptable use policies for GAI interfaces, modalities, and "
     "human-AI configurations (i.e., for chatbots and decision-making "
     "tasks), including criteria for the kinds of queries GAI "
     "applications should refuse to respond to.",
     (7,)),
    ("GV-3.2-004", "GOVERN 3.2",
     "Establish policies for user feedback mechanisms for GAI systems "
     "which include thorough instructions and any mechanisms for "
     "recourse.",
     (7,)),
    ("GV-3.2-005", "GOVERN 3.2",
     "Engage in threat modeling to anticipate potential risks from GAI "
     "systems.",
     (1, 9)),

    # ── GOVERN 4.1 ──────────────────────────────────────────────────────
    ("GV-4.1-001", "GOVERN 4.1",
     "Establish policies and procedures that address continual "
     "improvement processes for GAI risk measurement. Address general "
     "risks associated with a lack of explainability and transparency in "
     "GAI systems by using ample documentation and techniques such as: "
     "application of gradient-based attributions, occlusion/term "
     "reduction, counterfactual prompts and prompt engineering, and "
     "analysis of embeddings; Assess and update risk measurement "
     "approaches at regular cadences.",
     (2,)),
    ("GV-4.1-002", "GOVERN 4.1",
     "Establish policies, procedures, and processes detailing risk "
     "measurement in context of use with standardized measurement "
     "protocols and structured public feedback exercises such as AI "
     "red-teaming or independent external evaluations. CBRN Information "
     "and Capability;",
     (12,)),
    ("GV-4.1-003", "GOVERN 4.1",
     "Establish policies, procedures, and processes for oversight "
     "functions (e.g., senior leadership, legal, compliance, including "
     "internal evaluation) across the GAI lifecycle, from problem "
     "formulation and supply chains to system decommission.",
     (12,)),

    # ── GOVERN 4.2 ──────────────────────────────────────────────────────
    ("GV-4.2-001", "GOVERN 4.2",
     "Establish terms of use and terms of service for GAI systems.",
     (3, 10, 11)),
    ("GV-4.2-002", "GOVERN 4.2",
     "Include relevant AI Actors in the GAI system risk identification "
     "process.",
     (7,)),
    ("GV-4.2-003", "GOVERN 4.2",
     "Verify that downstream GAI system impacts (such as the use of "
     "third-party plugins) are included in the impact documentation "
     "process.",
     (12,)),

    # ── GOVERN 4.3 ──────────────────────────────────────────────────────
    ("GV-4.3-002", "GOVERN 4.3",
     "Establish organizational practices to identify the minimum set of "
     "criteria necessary for GAI system incident reporting such as: "
     "System ID (auto-generated most likely), Title, Reporter, "
     "System/Source, Data Reported, Date of Incident, Description, "
     "Impact(s), Stakeholder(s) Impacted.",
     (9,)),
    ("GV-4.3-003", "GOVERN 4.3",
     "Verify information sharing and feedback mechanisms among "
     "individuals and organizations regarding any negative impact from "
     "GAI systems.",
     (4, 8)),

    # ── GOVERN 5.1 ──────────────────────────────────────────────────────
    ("GV-5.1-001", "GOVERN 5.1",
     "Allocate time and resources for outreach, feedback, and recourse "
     "processes in GAI system development.",
     (6, 7)),
    ("GV-5.1-002", "GOVERN 5.1",
     "Document interactions with GAI systems to users prior to "
     "interactive activities, particularly in contexts involving more "
     "significant risks.",
     (2, 7)),

    # ── GOVERN 6.1 ──────────────────────────────────────────────────────
    ("GV-6.1-001", "GOVERN 6.1",
     "Categorize different types of GAI content with associated "
     "third-party rights (e.g., copyright, intellectual property, data "
     "privacy).",
     (4, 10, 12)),
    ("GV-6.1-002", "GOVERN 6.1",
     "Conduct joint educational activities and events in collaboration "
     "with third parties to promote best practices for managing GAI "
     "risks.",
     (12,)),
    ("GV-6.1-003", "GOVERN 6.1",
     "Develop and validate approaches for measuring the success of "
     "content provenance management efforts with third parties (e.g., "
     "incidents detected and response times).",
     (8, 12)),
    ("GV-6.1-004", "GOVERN 6.1",
     "Draft and maintain well-defined contracts and service level "
     "agreements (SLAs) that specify content ownership, usage rights, "
     "quality standards, security requirements, and content provenance "
     "expectations for GAI systems.",
     (8, 9, 10)),
    ("GV-6.1-005", "GOVERN 6.1",
     "Implement a use-cased based supplier risk assessment framework to "
     "evaluate and monitor third-party entities’ performance and "
     "adherence to content provenance standards and technologies to "
     "detect anomalies and unauthorized changes; services acquisition "
     "and value chain risk management; and legal compliance.",
     (4, 8, 9, 10, 12)),
    ("GV-6.1-006", "GOVERN 6.1",
     "Include clauses in contracts which allow an organization to "
     "evaluate third-party GAI processes and standards.",
     (8,)),
    ("GV-6.1-007", "GOVERN 6.1",
     "Inventory all third-party entities with access to organizational "
     "content and establish approved GAI technology and service provider "
     "lists.",
     (12,)),
    ("GV-6.1-008", "GOVERN 6.1",
     "Maintain records of changes to content made by third parties to "
     "promote content provenance, including sources, timestamps, "
     "metadata.",
     (8, 10, 12)),
    ("GV-6.1-009", "GOVERN 6.1",
     "Update and integrate due diligence processes for GAI acquisition "
     "and procurement vendor assessments to include intellectual "
     "property, data privacy, security, and other risks. For example, "
     "update processes to: Address solutions that may rely on embedded "
     "GAI technologies; Address ongoing monitoring, assessments, and "
     "alerting, dynamic risk assessments, and real-time reporting tools "
     "for monitoring third-party GAI risks; Consider policy adjustments "
     "across GAI modeling libraries, tools and APIs, fine-tuned models, "
     "and embedded tools; Assess GAI vendors, open-source or proprietary "
     "GAI tools, or GAI service providers against incident or "
     "vulnerability databases.",
     (4, 6, 7, 9, 10, 12)),
    ("GV-6.1-010", "GOVERN 6.1",
     "Update GAI acceptable use policies to address proprietary and "
     "open-source GAI technologies and data, and contractors, "
     "consultants, and other third-party personnel.",
     (10, 12)),

    # ── GOVERN 6.2 ──────────────────────────────────────────────────────
    ("GV-6.2-001", "GOVERN 6.2",
     "Document GAI risks associated with system value chain to identify "
     "over-reliance on third-party data and to identify fallbacks.",
     (12,)),
    ("GV-6.2-002", "GOVERN 6.2",
     "Document incidents involving third-party GAI data and systems, "
     "including opendata and open-source software.",
     (10, 12)),
    ("GV-6.2-003", "GOVERN 6.2",
     "Establish incident response plans for third-party GAI "
     "technologies: Align incident response plans with impacts "
     "enumerated in MAP 5.1; Communicate third-party GAI incident "
     "response plans to all relevant AI Actors; Define ownership of GAI "
     "incident response functions; Rehearse third-party GAI incident "
     "response plans at a regular cadence; Improve incident response "
     "plans based on retrospective learning; Review incident response "
     "plans for alignment with relevant breach reporting, data "
     "protection, data privacy, or other laws.",
     (4, 6, 7, 9, 12)),
    ("GV-6.2-004", "GOVERN 6.2",
     "Establish policies and procedures for continuous monitoring of "
     "third-party GAI systems in deployment.",
     (12,)),
    ("GV-6.2-005", "GOVERN 6.2",
     "Establish policies and procedures that address GAI data "
     "redundancy, including model weights and other system artifacts.",
     (6,)),
    ("GV-6.2-006", "GOVERN 6.2",
     "Establish policies and procedures to test and manage risks related "
     "to rollover and fallback technologies for GAI systems, "
     "acknowledging that rollover and fallback may include manual "
     "processing.",
     (8,)),
    ("GV-6.2-007", "GOVERN 6.2",
     "Review vendor contracts and avoid arbitrary or capricious "
     "termination of critical GAI technologies or vendor services and "
     "non-standard terms that may amplify or defer liability in "
     "unexpected ways and/or contribute to unauthorized data collection "
     "by vendors or third-parties (e.g., secondary data use). Consider: "
     "Clear assignment of liability and responsibility for incidents, "
     "GAI system changes over time (e.g., fine-tuning, drift, decay); "
     "Request: Notification and disclosure for serious incidents arising "
     "from third-party data and systems; Service Level Agreements (SLAs) "
     "in vendor contracts that address incident response, response "
     "times, and availability of critical support.",
     (7, 9, 12)),

    # ── MAP 1.1 ─────────────────────────────────────────────────────────
    ("MP-1.1-001", "MAP 1.1",
     "When identifying intended purposes, consider factors such as "
     "internal vs. external use, narrow vs. broad application scope, "
     "fine-tuning, and varieties of data sources (e.g., grounding, "
     "retrieval-augmented generation).",
     (4, 10)),
    ("MP-1.1-002", "MAP 1.1",
     "Determine and document the expected and acceptable GAI system "
     "context of use in collaboration with socio-cultural and other "
     "domain experts, by assessing: Assumptions and limitations; Direct "
     "value to the organization; Intended operational environment and "
     "observed usage patterns; Potential positive and negative impacts "
     "to individuals, public safety, groups, communities, organizations, "
     "democratic institutions, and the physical environment; Social "
     "norms and expectations.",
     (6,)),
    ("MP-1.1-003", "MAP 1.1",
     "Document risk measurement plans to address identified risks. Plans "
     "may include, as applicable: Individual and group cognitive biases "
     "(e.g., confirmation bias, funding bias, groupthink) for AI Actors "
     "involved in the design, implementation, and use of GAI systems; "
     "Known past GAI system incidents and failure modes; In-context use "
     "and foreseeable misuse, abuse, and off-label use; Over reliance on "
     "quantitative metrics and methodologies without sufficient "
     "awareness of their limitations in the context(s) of use; Standard "
     "measurement and structured human feedback approaches; Anticipated "
     "human-AI configurations.",
     (3, 6, 7)),
    ("MP-1.1-004", "MAP 1.1",
     "Identify and document foreseeable illegal uses or applications of "
     "the GAI system that surpass organizational risk tolerances.",
     (1, 3, 11)),

    # ── MAP 1.2 ─────────────────────────────────────────────────────────
    ("MP-1.2-001", "MAP 1.2",
     "Establish and empower interdisciplinary teams that reflect a wide "
     "range of capabilities, competencies, demographic groups, domain "
     "expertise, educational backgrounds, lived experiences, "
     "professions, and skills across the enterprise to inform and "
     "conduct risk measurement and management functions.",
     (6, 7)),
    ("MP-1.2-002", "MAP 1.2",
     "Verify that data or benchmarks used in risk measurement, and "
     "users, participants, or subjects involved in structured GAI public "
     "feedback exercises are representative of diverse in-context user "
     "populations.",
     (6, 7)),

    # ── MAP 2.1 ─────────────────────────────────────────────────────────
    ("MP-2.1-001", "MAP 2.1",
     "Establish known assumptions and practices for determining data "
     "origin and content lineage, for documentation and evaluation "
     "purposes.",
     (8,)),
    ("MP-2.1-002", "MAP 2.1",
     "Institute test and evaluation for data and content flows within "
     "the GAI system, including but not limited to, original data "
     "sources, data transformations, and decision-making criteria.",
     (4, 10)),

    # ── MAP 2.2 ─────────────────────────────────────────────────────────
    ("MP-2.2-001", "MAP 2.2",
     "Identify and document how the system relies on upstream data "
     "sources, including for content provenance, and if it serves as an "
     "upstream dependency for other systems.",
     (8, 12)),
    ("MP-2.2-002", "MAP 2.2",
     "Observe and analyze how the GAI system interacts with external "
     "networks, and identify any potential for negative externalities, "
     "particularly where content provenance might be compromised.",
     (8,)),

    # ── MAP 2.3 ─────────────────────────────────────────────────────────
    ("MP-2.3-001", "MAP 2.3",
     "Assess the accuracy, quality, reliability, and authenticity of GAI "
     "output by comparing it to a set of known ground truth data and by "
     "using a variety of evaluation methods (e.g., human oversight and "
     "automated evaluation, proven cryptographic techniques, review of "
     "content inputs).",
     (8,)),
    ("MP-2.3-002", "MAP 2.3",
     "Review and document accuracy, representativeness, relevance, "
     "suitability of data used at different stages of AI life cycle.",
     (6, 10)),
    ("MP-2.3-003", "MAP 2.3",
     "Deploy and document fact-checking techniques to verify the "
     "accuracy and veracity of information generated by GAI systems, "
     "especially when the information comes from multiple (or unknown) "
     "sources.",
     (8,)),
    ("MP-2.3-004", "MAP 2.3",
     "Develop and implement testing techniques to identify GAI produced "
     "content (e.g., synthetic media) that might be indistinguishable "
     "from human-generated content.",
     (8,)),
    ("MP-2.3-005", "MAP 2.3",
     "Implement plans for GAI systems to undergo regular adversarial "
     "testing to identify vulnerabilities and potential manipulation or "
     "misuse.",
     (9,)),

    # ── MAP 3.4 ─────────────────────────────────────────────────────────
    ("MP-3.4-001", "MAP 3.4",
     "Evaluate whether GAI operators and end-users can accurately "
     "understand content lineage and origin.",
     (7, 8)),
    ("MP-3.4-002", "MAP 3.4",
     "Adapt existing training programs to include modules on digital "
     "content transparency.",
     (8,)),
    ("MP-3.4-003", "MAP 3.4",
     "Develop certification programs that test proficiency in managing "
     "GAI risks and interpreting content provenance, relevant to "
     "specific industry and context.",
     (8,)),
    ("MP-3.4-004", "MAP 3.4",
     "Delineate human proficiency tests from tests of GAI capabilities.",
     (7,)),
    ("MP-3.4-005", "MAP 3.4",
     "Implement systems to continually monitor and track the outcomes of "
     "human-GAI configurations for future refinement and improvements.",
     (7, 8)),
    ("MP-3.4-006", "MAP 3.4",
     "Involve the end-users, practitioners, and operators in GAI system "
     "in prototyping and testing activities. Make sure these tests cover "
     "various scenarios, such as crisis situations or ethically "
     "sensitive contexts.",
     (3, 6, 7, 8)),

    # ── MAP 4.1 ─────────────────────────────────────────────────────────
    ("MP-4.1-001", "MAP 4.1",
     "Conduct periodic monitoring of AI-generated content for privacy "
     "risks; address any possible instances of PII or sensitive data "
     "exposure.",
     (4,)),
    ("MP-4.1-002", "MAP 4.1",
     "Implement processes for responding to potential intellectual "
     "property infringement claims or other rights.",
     (10,)),
    ("MP-4.1-003", "MAP 4.1",
     "Connect new GAI policies, procedures, and processes to existing "
     "model, data, software development, and IT governance and to legal, "
     "compliance, and risk management activities.",
     (4, 9)),
    ("MP-4.1-004", "MAP 4.1",
     "Document training data curation policies, to the extent possible "
     "and according to applicable laws and policies.",
     (4, 10, 11)),
    ("MP-4.1-005", "MAP 4.1",
     "Establish policies for collection, retention, and minimum quality "
     "of data, in consideration of the following risks: Disclosure of "
     "inappropriate CBRN information; Use of Illegal or dangerous "
     "content; Offensive cyber capabilities; Training data imbalances "
     "that could give rise to harmful biases; Leak of personally "
     "identifiable information, including facial likenesses of "
     "individuals.",
     (1, 3, 4, 6, 9, 10)),
    ("MP-4.1-006", "MAP 4.1",
     "Implement policies and practices defining how third-party "
     "intellectual property and training data will be used, stored, and "
     "protected.",
     (10, 12)),
    ("MP-4.1-007", "MAP 4.1",
     "Re-evaluate models that were fine-tuned or enhanced on top of "
     "third-party models.",
     (12,)),
    ("MP-4.1-008", "MAP 4.1",
     "Re-evaluate risks when adapting GAI models to new domains. "
     "Additionally, establish warning systems to determine if a GAI "
     "system is being used in a new domain where previous assumptions "
     "(relating to context of use or mapped risks such as security, and "
     "safety) may no longer hold.",
     (1, 3, 4, 6, 10)),
    ("MP-4.1-009", "MAP 4.1",
     "Leverage approaches to detect the presence of PII or sensitive "
     "data in generated output text, image, video, or audio.",
     (4,)),
    ("MP-4.1-010", "MAP 4.1",
     "Conduct appropriate diligence on training data use to assess "
     "intellectual property, and privacy, risks, including to examine "
     "whether use of proprietary or sensitive training data is "
     "consistent with applicable laws.",
     (4, 10)),

    # ── MAP 5.1 ─────────────────────────────────────────────────────────
    ("MP-5.1-001", "MAP 5.1",
     "Apply TEVV practices for content provenance (e.g., probing a "
     "system's synthetic data generation capabilities for potential "
     "misuse or vulnerabilities.",
     (8, 9)),
    ("MP-5.1-002", "MAP 5.1",
     "Identify potential content provenance harms of GAI, such as "
     "misinformation or disinformation, deepfakes, including NCII, or "
     "tampered content. Enumerate and rank risks based on their "
     "likelihood and potential impact, and determine how well provenance "
     "solutions address specific risks and/or harms.",
     (3, 8, 11)),
    ("MP-5.1-003", "MAP 5.1",
     "Consider disclosing use of GAI to end users in relevant contexts, "
     "while considering the objective of disclosure, the context of use, "
     "the likelihood and magnitude of the risk posed, the audience of "
     "the disclosure, as well as the frequency of the disclosures.",
     (7,)),
    ("MP-5.1-004", "MAP 5.1",
     "Prioritize GAI structured public feedback processes based on risk "
     "assessment estimates.",
     (1, 3, 6, 8)),
    ("MP-5.1-005", "MAP 5.1",
     "Conduct adversarial role-playing exercises, GAI red-teaming, or "
     "chaos testing to identify anomalous or unforeseen failure modes.",
     (9,)),
    ("MP-5.1-006", "MAP 5.1",
     "Profile threats and negative impacts arising from GAI systems "
     "interacting with, manipulating, or generating content, and "
     "outlining known and potential vulnerabilities and the likelihood "
     "of their occurrence.",
     (9,)),

    # ── MAP 5.2 ─────────────────────────────────────────────────────────
    ("MP-5.2-001", "MAP 5.2",
     "Determine context-based measures to identify if new impacts are "
     "present due to the GAI system, including regular engagements with "
     "downstream AI Actors to identify and quantify new contexts of "
     "unanticipated impacts of GAI systems.",
     (7, 12)),
    ("MP-5.2-002", "MAP 5.2",
     "Plan regular engagements with AI Actors responsible for inputs to "
     "GAI systems, including third-party data and algorithms, to review "
     "and evaluate unanticipated impacts.",
     (7, 12)),

    # ── MEASURE 1.1 ─────────────────────────────────────────────────────
    ("MS-1.1-001", "MEASURE 1.1",
     "Employ methods to trace the origin and modifications of digital "
     "content.",
     (8,)),
    ("MS-1.1-002", "MEASURE 1.1",
     "Integrate tools designed to analyze content provenance and detect "
     "data anomalies, verify the authenticity of digital signatures, and "
     "identify patterns associated with misinformation or manipulation.",
     (8,)),
    ("MS-1.1-003", "MEASURE 1.1",
     "Disaggregate evaluation metrics by demographic factors to identify "
     "any discrepancies in how content provenance mechanisms work across "
     "diverse populations.",
     (6, 8)),
    ("MS-1.1-004", "MEASURE 1.1",
     "Develop a suite of metrics to evaluate structured public feedback "
     "exercises informed by representative AI Actors.",
     (1, 6, 7)),
    ("MS-1.1-005", "MEASURE 1.1",
     "Evaluate novel methods and technologies for the measurement of "
     "GAI-related risks including in content provenance, offensive "
     "cyber, and CBRN, while maintaining the models’ ability to produce "
     "valid, reliable, and factually accurate outputs.",
     (1, 8, 11)),
    ("MS-1.1-006", "MEASURE 1.1",
     "Implement continuous monitoring of GAI system impacts to identify "
     "whether GAI outputs are equitable across various sub-populations. "
     "Seek active and direct feedback from affected communities via "
     "structured feedback mechanisms or redteaming to monitor and "
     "improve outputs.",
     (6,)),
    ("MS-1.1-007", "MEASURE 1.1",
     "Evaluate the quality and integrity of data used in training and "
     "the provenance of AI-generated content, for example by employing "
     "techniques like chaos engineering and seeking stakeholder "
     "feedback.",
     (8,)),
    ("MS-1.1-008", "MEASURE 1.1",
     "Define use cases, contexts of use, capabilities, and negative "
     "impacts where structured human feedback exercises, e.g., GAI "
     "red-teaming, would be most beneficial for GAI risk measurement and "
     "management based on the context of use.",
     (1, 6)),
    ("MS-1.1-009", "MEASURE 1.1",
     "Track and document risks or opportunities related to all GAI risks "
     "that cannot be measured quantitatively, including explanations as "
     "to why some risks cannot be measured (e.g., due to technological "
     "limitations, resource constraints, or trustworthy considerations). "
     "Include unmeasured risks in marginal risks.",
     (8,)),

    # ── MEASURE 1.3 ─────────────────────────────────────────────────────
    ("MS-1.3-001", "MEASURE 1.3",
     "Define relevant groups of interest (e.g., demographic groups, "
     "subject matter experts, experience with GAI technology) within the "
     "context of use as part of plans for gathering structured public "
     "feedback.",
     (1, 6, 7)),
    ("MS-1.3-002", "MEASURE 1.3",
     "Engage in internal and external evaluations, GAI red-teaming, "
     "impact assessments, or other structured human feedback exercises "
     "in consultation with representative AI Actors with expertise and "
     "familiarity in the context of use, and/or who are representative "
     "of the populations associated with the context of use.",
     (1, 6, 7)),
    ("MS-1.3-003", "MEASURE 1.3",
     "Verify those conducting structured human feedback exercises are "
     "not directly involved in system development tasks for the same GAI "
     "model.",
     (4, 7)),

    # ── MEASURE 2.2 ─────────────────────────────────────────────────────
    ("MS-2.2-001", "MEASURE 2.2",
     "Assess and manage statistical biases related to GAI content "
     "provenance through techniques such as re-sampling, re-weighting, "
     "or adversarial training.",
     (6, 8, 9)),
    ("MS-2.2-002", "MEASURE 2.2",
     "Document how content provenance data is tracked and how that data "
     "interacts with privacy and security. Consider: Anonymizing data to "
     "protect the privacy of human subjects; Leveraging privacy output "
     "filters; Removing any personally identifiable information (PII) to "
     "prevent potential harm or misuse. Data Privacy; Human AI "
     "Configuration; Information Integrity; Information Security;",
     (3,)),
    ("MS-2.2-003", "MEASURE 2.2",
     "Provide human subjects with options to withdraw participation or "
     "revoke their consent for present or future use of their data in "
     "GAI applications.",
     (4, 7, 8)),
    ("MS-2.2-004", "MEASURE 2.2",
     "Use techniques such as anonymization, differential privacy or "
     "other privacyenhancing technologies to minimize the risks "
     "associated with linking AI-generated content back to individual "
     "human subjects.",
     (4, 7)),

    # ── MEASURE 2.3 ─────────────────────────────────────────────────────
    ("MS-2.3-001", "MEASURE 2.3",
     "Consider baseline model performance on suites of benchmarks when "
     "selecting a model for fine tuning or enhancement with "
     "retrieval-augmented generation.",
     (2, 9)),
    ("MS-2.3-002", "MEASURE 2.3",
     "Evaluate claims of model capabilities using empirically validated "
     "methods.",
     (2, 9)),
    ("MS-2.3-003", "MEASURE 2.3",
     "Share results of pre-deployment testing with relevant GAI Actors, "
     "such as those with system release approval authority.",
     (7,)),
    ("MS-2.3-004", "MEASURE 2.3",
     "Utilize a purpose-built testing environment such as NIST Dioptra "
     "to empirically evaluate GAI trustworthy characteristics.",
     (1, 2, 3, 4, 6, 8, 9)),

    # ── MEASURE 2.5 ─────────────────────────────────────────────────────
    ("MS-2.5-001", "MEASURE 2.5",
     "Avoid extrapolating GAI system performance or capabilities from "
     "narrow, nonsystematic, and anecdotal assessments.",
     (2, 7)),
    ("MS-2.5-002", "MEASURE 2.5",
     "Document the extent to which human domain knowledge is employed to "
     "improve GAI system performance, via, e.g., RLHF, fine-tuning, "
     "retrievalaugmented generation, content moderation, business rules.",
     (7,)),
    ("MS-2.5-003", "MEASURE 2.5",
     "Review and verify sources and citations in GAI system outputs "
     "during predeployment risk measurement and ongoing monitoring "
     "activities.",
     (2,)),
    ("MS-2.5-004", "MEASURE 2.5",
     "Track and document instances of anthropomorphization (e.g., human "
     "images, mentions of human feelings, cyborg imagery or motifs) in "
     "GAI system interfaces.",
     (7,)),
    ("MS-2.5-005", "MEASURE 2.5",
     "Verify GAI system training data and TEVV data provenance, and that "
     "fine-tuning or retrieval-augmented generation data is grounded.",
     (8,)),
    ("MS-2.5-006", "MEASURE 2.5",
     "Regularly review security and safety guardrails, especially if the "
     "GAI system is being operated in novel circumstances. This includes "
     "reviewing reasons why the GAI system was initially assessed as "
     "being safe to deploy.",
     (3, 9)),

    # ── MEASURE 2.6 ─────────────────────────────────────────────────────
    ("MS-2.6-001", "MEASURE 2.6",
     "Assess adverse impacts, including health and wellbeing impacts for "
     "value chain or other AI Actors that are exposed to sexually "
     "explicit, offensive, or violent information during GAI training "
     "and maintenance.",
     (3, 7, 11, 12)),
    ("MS-2.6-002", "MEASURE 2.6",
     "Assess existence or levels of harmful bias, intellectual property "
     "infringement, data privacy violations, obscenity, extremism, "
     "violence, or CBRN information in system training data.",
     (1, 3, 4, 6, 10, 11)),
    ("MS-2.6-003", "MEASURE 2.6",
     "Re-evaluate safety features of fine-tuned models when the negative "
     "risk exceeds organizational risk tolerance.",
     (3,)),
    ("MS-2.6-004", "MEASURE 2.6",
     "Review GAI system outputs for validity and safety: Review "
     "generated code to assess risks that may arise from unreliable "
     "downstream decision-making.",
     (3, 12)),
    ("MS-2.6-005", "MEASURE 2.6",
     "Verify that GAI system architecture can monitor outputs and "
     "performance, and handle, recover from, and repair errors when "
     "security anomalies, threats and impacts are detected.",
     (2, 8, 9)),
    ("MS-2.6-006", "MEASURE 2.6",
     "Verify that systems properly handle queries that may give rise to "
     "inappropriate, malicious, or illegal usage, including facilitating "
     "manipulation, extortion, targeted impersonation, cyber-attacks, "
     "and weapons creation.",
     (1, 9)),
    ("MS-2.6-007", "MEASURE 2.6",
     "Regularly evaluate GAI system vulnerabilities to possible "
     "circumvention of safety measures.",
     (1, 9)),

    # ── MEASURE 2.7 ─────────────────────────────────────────────────────
    ("MS-2.7-001", "MEASURE 2.7",
     "Apply established security measures to: Assess likelihood and "
     "magnitude of vulnerabilities and threats such as backdoors, "
     "compromised dependencies, data breaches, eavesdropping, "
     "man-in-the-middle attacks, reverse engineering, autonomous agents, "
     "model theft or exposure of model weights, AI inference, bypass, "
     "extraction, and other baseline security concerns.",
     (4, 8, 9, 12)),
    ("MS-2.7-002", "MEASURE 2.7",
     "Benchmark GAI system security and resilience related to content "
     "provenance against industry standards and best practices. Compare "
     "GAI system security features and content provenance methods "
     "against industry state-of-the-art.",
     (8, 9)),
    ("MS-2.7-003", "MEASURE 2.7",
     "Conduct user surveys to gather user satisfaction with the "
     "AI-generated content and user perceptions of content authenticity. "
     "Analyze user feedback to identify concerns and/or current literacy "
     "levels related to content provenance and understanding of labels "
     "on content.",
     (7, 8)),
    ("MS-2.7-004", "MEASURE 2.7",
     "Identify metrics that reflect the effectiveness of security "
     "measures, such as data provenance, the number of unauthorized "
     "access attempts, inference, bypass, extraction, penetrations, or "
     "provenance verification.",
     (8, 9)),
    ("MS-2.7-005", "MEASURE 2.7",
     "Measure reliability of content authentication methods, such as "
     "watermarking, cryptographic signatures, digital fingerprints, as "
     "well as access controls, conformity assessment, and model "
     "integrity verification, which can help support the effective "
     "implementation of content provenance techniques. Evaluate the rate "
     "of false positives and false negatives in content provenance, as "
     "well as true positives and true negatives for verification.",
     (8,)),
    ("MS-2.7-006", "MEASURE 2.7",
     "Measure the rate at which recommendations from security checks and "
     "incidents are implemented. Assess how quickly the AI system can "
     "adapt and improve based on lessons learned from security incidents "
     "and feedback.",
     (8, 9)),
    ("MS-2.7-007", "MEASURE 2.7",
     "Perform AI red-teaming to assess resilience against: Abuse to "
     "facilitate attacks on other systems (e.g., malicious code "
     "generation, enhanced phishing content), GAI attacks (e.g., prompt "
     "injection), ML attacks (e.g., adversarial examples/prompts, data "
     "poisoning, membership inference, model extraction, sponge "
     "examples).",
     (3, 6, 9)),
    ("MS-2.7-008", "MEASURE 2.7",
     "Verify fine-tuning does not compromise safety and security "
     "controls.",
     (3, 8, 9)),
    ("MS-2.7-009", "MEASURE 2.7",
     "Regularly assess and verify that security measures remain "
     "effective and have not been compromised.",
     (9,)),

    # ── MEASURE 2.8 ─────────────────────────────────────────────────────
    ("MS-2.8-001", "MEASURE 2.8",
     "Compile statistics on actual policy violations, take-down "
     "requests, and intellectual property infringement for "
     "organizational GAI systems: Analyze transparency reports across "
     "demographic groups, languages groups.",
     (6, 10)),
    ("MS-2.8-002", "MEASURE 2.8",
     "Document the instructions given to data annotators or AI "
     "red-teamers.",
     (7,)),
    ("MS-2.8-003", "MEASURE 2.8",
     "Use digital content transparency solutions to enable the "
     "documentation of each instance where content is generated, "
     "modified, or shared to provide a tamperproof history of the "
     "content, promote transparency, and enable traceability. Robust "
     "version control systems can also be applied to track changes "
     "across the AI lifecycle over time.",
     (8,)),
    ("MS-2.8-004", "MEASURE 2.8",
     "Verify adequacy of GAI system user instructions through user "
     "testing.",
     (7,)),

    # ── MEASURE 2.9 ─────────────────────────────────────────────────────
    ("MS-2.9-001", "MEASURE 2.9",
     "Apply and document ML explanation results such as: Analysis of "
     "embeddings, Counterfactual prompts, Gradient-based attributions, "
     "Model compression/surrogate models, Occlusion/term reduction.",
     (2,)),
    ("MS-2.9-002", "MEASURE 2.9",
     "Document GAI model details including: Proposed use and "
     "organizational value; Assumptions and limitations, Data collection "
     "methodologies; Data provenance; Data quality; Model architecture "
     "(e.g., convolutional neural network, transformers, etc.); "
     "Optimization objectives; Training algorithms; RLHF approaches; "
     "Fine-tuning or retrieval-augmented generation approaches; "
     "Evaluation data; Ethical considerations; Legal and regulatory "
     "requirements.",
     (6, 8)),

    # ── MEASURE 2.10 ────────────────────────────────────────────────────
    ("MS-2.10-001", "MEASURE 2.10",
     "Conduct AI red-teaming to assess issues such as: Outputting of "
     "training data samples, and subsequent reverse engineering, model "
     "extraction, and membership inference risks; Revealing biometric, "
     "confidential, copyrighted, licensed, patented, personal, "
     "proprietary, sensitive, or trade-marked information; Tracking or "
     "revealing location information of users or members of training "
     "datasets.",
     (7, 8, 10)),
    ("MS-2.10-002", "MEASURE 2.10",
     "Engage directly with end-users and other stakeholders to "
     "understand their expectations and concerns regarding content "
     "provenance. Use this feedback to guide the design of provenance "
     "data-tracking techniques.",
     (7, 8)),
    ("MS-2.10-003", "MEASURE 2.10",
     "Verify deduplication of GAI training data samples, particularly "
     "regarding synthetic data.",
     (6,)),

    # ── MEASURE 2.11 ────────────────────────────────────────────────────
    ("MS-2.11-001", "MEASURE 2.11",
     "Apply use-case appropriate benchmarks (e.g., Bias Benchmark "
     "Questions, Real Hateful or Harmful Prompts, Winogender Schemas15) "
     "to quantify systemic bias, stereotyping, denigration, and hateful "
     "content in GAI system outputs; Document assumptions and "
     "limitations of benchmarks, including any actual or possible "
     "training/test data cross contamination, relative to in-context "
     "deployment environment.",
     (6,)),
    ("MS-2.11-002", "MEASURE 2.11",
     "Conduct fairness assessments to measure systemic bias. Measure GAI "
     "system performance across demographic groups and subgroups, "
     "addressing both quality of service and any allocation of services "
     "and resources. Quantify harms using: field testing with sub-group "
     "populations to determine likelihood of exposure to generated "
     "content exhibiting harmful bias, AI red-teaming with "
     "counterfactual and low-context (e.g., “leader,” “bad guys”) "
     "prompts. For ML pipelines or business processes with categorical "
     "or numeric outcomes that rely on GAI, apply general fairness "
     "metrics (e.g., demographic parity, equalized odds, equal "
     "opportunity, statistical hypothesis tests), to the pipeline or "
     "business outcome where appropriate; Custom, context-specific "
     "metrics developed in collaboration with domain experts and "
     "affected communities; Measurements of the prevalence of "
     "denigration in generated content in deployment (e.g., subsampling "
     "a fraction of traffic and manually annotating denigrating "
     "content).",
     (3, 6)),
    ("MS-2.11-003", "MEASURE 2.11",
     "Identify the classes of individuals, groups, or environmental "
     "ecosystems which might be impacted by GAI systems through direct "
     "engagement with potentially impacted communities.",
     (5, 6)),
    ("MS-2.11-004", "MEASURE 2.11",
     "Review, document, and measure sources of bias in GAI training and "
     "TEVV data: Differences in distributions of outcomes across and "
     "within groups, including intersecting groups; Completeness, "
     "representativeness, and balance of data sources; demographic group "
     "and subgroup coverage in GAI system training data; Forms of latent "
     "systemic bias in images, text, audio, embeddings, or other complex "
     "or unstructured data; Input data features that may serve as "
     "proxies for demographic group membership (i.e., image metadata, "
     "language dialect) or otherwise give rise to emergent bias within "
     "GAI systems; The extent to which the digital divide may negatively "
     "impact representativeness in GAI system training and TEVV data; "
     "Filtering of hate speech or content in GAI system training data; "
     "Prevalence of GAI-generated data in GAI system training data.",
     (6,)),
    ("MS-2.11-005", "MEASURE 2.11",
     "Assess the proportion of synthetic to non-synthetic training data "
     "and verify training data is not overly homogenous or GAI-produced "
     "to mitigate concerns of model collapse.",
     (6,)),

    # ── MEASURE 2.12 ────────────────────────────────────────────────────
    ("MS-2.12-001", "MEASURE 2.12",
     "Assess safety to physical environments when deploying GAI systems.",
     (3,)),
    ("MS-2.12-002", "MEASURE 2.12",
     "Document anticipated environmental impacts of model development, "
     "maintenance, and deployment in product design decisions.",
     (5,)),
    ("MS-2.12-003", "MEASURE 2.12",
     "Measure or estimate environmental impacts (e.g., energy and water "
     "consumption) for training, fine tuning, and deploying models: "
     "Verify tradeoffs between resources used at inference time versus "
     "additional resources required at training time.",
     (5,)),
    ("MS-2.12-004", "MEASURE 2.12",
     "Verify effectiveness of carbon capture or offset programs for GAI "
     "training and applications, and address green-washing concerns.",
     (5,)),

    # ── MEASURE 2.13 ────────────────────────────────────────────────────
    ("MS-2.13-001", "MEASURE 2.13",
     "Create measurement error models for pre-deployment metrics to "
     "demonstrate construct validity for each metric (i.e., does the "
     "metric effectively operationalize the desired concept): Measure or "
     "estimate, and document, biases or statistical variance in applied "
     "metrics or structured human feedback processes; Leverage domain "
     "expertise when modeling complex societal constructs such as "
     "hateful content.",
     (2, 6, 8)),

    # ── MEASURE 3.2 ─────────────────────────────────────────────────────
    ("MS-3.2-001", "MEASURE 3.2",
     "Establish processes for identifying emergent GAI system risks "
     "including consulting with external AI Actors.",
     (2, 7)),

    # ── MEASURE 3.3 ─────────────────────────────────────────────────────
    ("MS-3.3-001", "MEASURE 3.3",
     "Conduct impact assessments on how AI-generated content might "
     "affect different social, economic, and cultural groups.",
     (6,)),
    ("MS-3.3-002", "MEASURE 3.3",
     "Conduct studies to understand how end users perceive and interact "
     "with GAI content and accompanying content provenance within "
     "context of use. Assess whether the content aligns with their "
     "expectations and how they may act upon the information presented.",
     (7, 8)),
    ("MS-3.3-003", "MEASURE 3.3",
     "Evaluate potential biases and stereotypes that could emerge from "
     "the AIgenerated content using appropriate methodologies including "
     "computational testing methods as well as evaluating structured "
     "feedback input.",
     (6,)),
    ("MS-3.3-004", "MEASURE 3.3",
     "Provide input for training materials about the capabilities and "
     "limitations of GAI systems related to digital content transparency "
     "for AI Actors, other professionals, and the public about the "
     "societal impacts of AI and the role of diverse and inclusive "
     "content generation.",
     (6, 7, 8)),
    ("MS-3.3-005", "MEASURE 3.3",
     "Record and integrate structured feedback about content provenance "
     "from operators, users, and potentially impacted communities "
     "through the use of methods such as user research studies, focus "
     "groups, or community forums. Actively seek feedback on generated "
     "content quality and potential biases. Assess the general awareness "
     "among end users and impacted communities about the availability of "
     "these feedback channels.",
     (6, 7, 8)),

    # ── MEASURE 4.2 ─────────────────────────────────────────────────────
    ("MS-4.2-001", "MEASURE 4.2",
     "Conduct adversarial testing at a regular cadence to map and "
     "measure GAI risks, including tests to address attempts to deceive "
     "or manipulate the application of provenance techniques or other "
     "misuses. Identify vulnerabilities and understand potential misuse "
     "scenarios and unintended outputs.",
     (8, 9)),
    ("MS-4.2-002", "MEASURE 4.2",
     "Evaluate GAI system performance in real-world scenarios to observe "
     "its behavior in practical environments and reveal issues that "
     "might not surface in controlled and optimized testing "
     "environments.",
     (2, 7, 9)),
    ("MS-4.2-003", "MEASURE 4.2",
     "Implement interpretability and explainability methods to evaluate "
     "GAI system decisions and verify alignment with intended purpose.",
     (6, 8)),
    ("MS-4.2-004", "MEASURE 4.2",
     "Monitor and document instances where human operators or other "
     "systems override the GAI's decisions. Evaluate these cases to "
     "understand if the overrides are linked to issues related to "
     "content provenance.",
     (8,)),
    ("MS-4.2-005", "MEASURE 4.2",
     "Verify and document the incorporation of results of structured "
     "public feedback exercises into design, implementation, deployment "
     "approval (“go”/“no-go” decisions), monitoring, and decommission "
     "decisions.",
     (7, 9)),

    # ── MANAGE 1.3 ──────────────────────────────────────────────────────
    ("MG-1.3-001", "MANAGE 1.3",
     "Document trade-offs, decision processes, and relevant measurement "
     "and feedback results for risks that do not surpass organizational "
     "risk tolerance, for example, in the context of model release: "
     "Consider different approaches for model release, for example, "
     "leveraging a staged release approach. Consider release approaches "
     "in the context of the model and its projected use cases. Mitigate, "
     "transfer, or avoid risks that surpass organizational risk "
     "tolerances.",
     (9,)),
    ("MG-1.3-002", "MANAGE 1.3",
     "Monitor the robustness and effectiveness of risk controls and "
     "mitigation plans (e.g., via red-teaming, field testing, "
     "participatory engagements, performance assessments, user feedback "
     "mechanisms).",
     (7,)),

    # ── MANAGE 2.2 ──────────────────────────────────────────────────────
    ("MG-2.2-001", "MANAGE 2.2",
     "Compare GAI system outputs against pre-defined organization risk "
     "tolerance, guidelines, and principles, and review and test "
     "AI-generated content against these guidelines.",
     (1, 3, 6, 11)),
    ("MG-2.2-002", "MANAGE 2.2",
     "Document training data sources to trace the origin and provenance "
     "of AIgenerated content.",
     (8,)),
    ("MG-2.2-003", "MANAGE 2.2",
     "Evaluate feedback loops between GAI system content provenance and "
     "human reviewers, and update where needed. Implement real-time "
     "monitoring systems to affirm that content provenance protocols "
     "remain effective.",
     (8,)),
    ("MG-2.2-004", "MANAGE 2.2",
     "Evaluate GAI content and data for representational biases and "
     "employ techniques such as re-sampling, re-ranking, or adversarial "
     "training to mitigate biases in the generated content.",
     (6, 9)),
    ("MG-2.2-005", "MANAGE 2.2",
     "Engage in due diligence to analyze GAI output for harmful content, "
     "potential misinformation, and CBRN-related or NCII content.",
     (1, 3, 6, 11)),
    ("MG-2.2-006", "MANAGE 2.2",
     "Use feedback from internal and external AI Actors, users, "
     "individuals, and communities, to assess impact of AI-generated "
     "content.",
     (7,)),
    ("MG-2.2-007", "MANAGE 2.2",
     "Use real-time auditing tools where they can be demonstrated to aid "
     "in the tracking and validation of the lineage and authenticity of "
     "AI-generated data.",
     (8,)),
    ("MG-2.2-008", "MANAGE 2.2",
     "Use structured feedback mechanisms to solicit and capture user "
     "input about AIgenerated content to detect subtle shifts in quality "
     "or alignment with community and societal values.",
     (6, 7)),
    ("MG-2.2-009", "MANAGE 2.2",
     "Consider opportunities to responsibly use synthetic data and other "
     "privacy enhancing techniques in GAI development, where appropriate "
     "and applicable, match the statistical properties of real-world "
     "data without disclosing personally identifiable information or "
     "contributing to homogenization.",
     (2, 4, 6, 8, 10)),

    # ── MANAGE 2.3 ──────────────────────────────────────────────────────
    ("MG-2.3-001", "MANAGE 2.3",
     "Develop and update GAI system incident response and recovery plans "
     "and procedures to address the following: Review and maintenance of "
     "policies and procedures to account for newly encountered uses; "
     "Review and maintenance of policies and procedures for detection of "
     "unanticipated uses; Verify response and recovery plans account for "
     "the GAI system value chain; Verify response and recovery plans are "
     "updated for and include necessary details to communicate with "
     "downstream GAI system Actors: Points-of-Contact (POC), Contact "
     "information, notification format.",
     (12,)),

    # ── MANAGE 2.4 ──────────────────────────────────────────────────────
    ("MG-2.4-001", "MANAGE 2.4",
     "Establish and maintain communication plans to inform AI "
     "stakeholders as part of the deactivation or disengagement process "
     "of a specific GAI system (including for open-source models) or "
     "context of use, including reasons, workarounds, user access "
     "removal, alternative processes, contact information, etc.",
     (7,)),
    ("MG-2.4-002", "MANAGE 2.4",
     "Establish and maintain procedures for escalating GAI system "
     "incidents to the organizational risk management authority when "
     "specific criteria for deactivation or disengagement is met for a "
     "particular context of use or for the GAI system as a whole.",
     (9,)),
    ("MG-2.4-003", "MANAGE 2.4",
     "Establish and maintain procedures for the remediation of issues "
     "which trigger incident response processes for the use of a GAI "
     "system, and provide stakeholders timelines associated with the "
     "remediation plan.",
     (9,)),
    ("MG-2.4-004", "MANAGE 2.4",
     "Establish and regularly review specific criteria that warrants the "
     "deactivation of GAI systems in accordance with set risk tolerances "
     "and appetites.",
     (9,)),

    # ── MANAGE 3.1 ──────────────────────────────────────────────────────
    ("MG-3.1-001", "MANAGE 3.1",
     "Apply organizational risk tolerances and controls (e.g., "
     "acquisition and procurement processes; assessing personnel "
     "credentials and qualifications, performing background checks; "
     "filtering GAI input and outputs, grounding, fine tuning, "
     "retrieval-augmented generation) to third-party GAI resources: "
     "Apply organizational risk tolerance to the utilization of "
     "third-party datasets and other GAI resources; Apply organizational "
     "risk tolerances to fine-tuned third-party models; Apply "
     "organizational risk tolerance to existing third-party models "
     "adapted to a new domain; Reassess risk measurements after "
     "fine-tuning thirdparty GAI models.",
     (10, 12)),
    ("MG-3.1-002", "MANAGE 3.1",
     "Test GAI system value chain risks (e.g., data poisoning, malware, "
     "other software and hardware vulnerabilities; labor practices; data "
     "privacy and localization compliance; geopolitical alignment).",
     (4, 6, 9, 12)),
    ("MG-3.1-003", "MANAGE 3.1",
     "Re-assess model risks after fine-tuning or retrieval-augmented "
     "generation implementation and for any third-party GAI models "
     "deployed for applications and/or use cases that were not evaluated "
     "in initial testing.",
     (12,)),
    ("MG-3.1-004", "MANAGE 3.1",
     "Take reasonable measures to review training data for CBRN "
     "information, and intellectual property, and where appropriate, "
     "remove it. Implement reasonable measures to prevent, flag, or take "
     "other action in response to outputs that reproduce particular "
     "training data (e.g., plagiarized, trademarked, patented, licensed "
     "content or trade secret material).",
     (1, 10)),
    ("MG-3.1-005", "MANAGE 3.1",
     "Review various transparency artifacts (e.g., system cards and "
     "model cards) for third-party models.",
     (8, 9, 12)),

    # ── MANAGE 3.2 ──────────────────────────────────────────────────────
    ("MG-3.2-001", "MANAGE 3.2",
     "Apply explainable AI (XAI) techniques (e.g., analysis of "
     "embeddings, model compression/distillation, gradient-based "
     "attributions, occlusion/term reduction, counterfactual prompts, "
     "word clouds) as part of ongoing continuous improvement processes "
     "to mitigate risks related to unexplainable GAI systems.",
     (6,)),
    ("MG-3.2-002", "MANAGE 3.2",
     "Document how pre-trained models have been adapted (e.g., "
     "fine-tuned, or retrieval-augmented generation) for the specific "
     "generative task, including any data augmentations, parameter "
     "adjustments, or other modifications. Access to un-tuned (baseline) "
     "models supports debugging the relative influence of the pretrained "
     "weights compared to the fine-tuned model weights or other system "
     "updates.",
     (4, 8)),
    ("MG-3.2-003", "MANAGE 3.2",
     "Document sources and types of training data and their origins, "
     "potential biases present in the data related to the GAI "
     "application and its content provenance, architecture, training "
     "process of the pre-trained model including information on "
     "hyperparameters, training duration, and any fine-tuning or "
     "retrieval-augmented generation processes applied.",
     (6, 8, 10)),
    ("MG-3.2-004", "MANAGE 3.2",
     "Evaluate user reported problematic content and integrate feedback "
     "into system updates. Human-AI Configuration,",
     (3,)),
    ("MG-3.2-005", "MANAGE 3.2",
     "Implement content filters to prevent the generation of "
     "inappropriate, harmful, false, illegal, or violent content related "
     "to the GAI application, including for CSAM and NCII. These filters "
     "can be rule-based or leverage additional machine learning models "
     "to flag problematic inputs and outputs.",
     (3, 6, 8, 11)),
    ("MG-3.2-006", "MANAGE 3.2",
     "Implement real-time monitoring processes for analyzing generated "
     "content performance and trustworthiness characteristics related to "
     "content provenance to identify deviations from the desired "
     "standards and trigger alerts for human intervention.",
     (8,)),
    ("MG-3.2-007", "MANAGE 3.2",
     "Leverage feedback and recommendations from organizational boards "
     "or committees related to the deployment of GAI applications and "
     "content provenance when using third-party pre-trained models.",
     (8, 12)),
    ("MG-3.2-008", "MANAGE 3.2",
     "Use human moderation systems where appropriate to review generated "
     "content in accordance with human-AI configuration policies "
     "established in the Govern function, aligned with socio-cultural "
     "norms in the context of use, and for settings where AI models are "
     "demonstrated to perform poorly.",
     (7,)),
    ("MG-3.2-009", "MANAGE 3.2",
     "Use organizational risk tolerance to evaluate acceptable risks and "
     "performance metrics and decommission or retrain pre-trained models "
     "that perform outside of defined limits.",
     (1, 2)),

    # ── MANAGE 4.1 ──────────────────────────────────────────────────────
    ("MG-4.1-001", "MANAGE 4.1",
     "Collaborate with external researchers, industry experts, and "
     "community representatives to maintain awareness of emerging best "
     "practices and technologies in measuring and managing identified "
     "risks.",
     (6, 8)),
    ("MG-4.1-002", "MANAGE 4.1",
     "Establish, maintain, and evaluate effectiveness of organizational "
     "processes and procedures for post-deployment monitoring of GAI "
     "systems, particularly for potential confabulation, CBRN, or cyber "
     "risks.",
     (1, 2, 9)),
    ("MG-4.1-003", "MANAGE 4.1",
     "Evaluate the use of sentiment analysis to gauge user sentiment "
     "regarding GAI content performance and impact, and work in "
     "collaboration with AI Actors experienced in user research and "
     "experience.",
     (7,)),
    ("MG-4.1-004", "MANAGE 4.1",
     "Implement active learning techniques to identify instances where "
     "the model fails or produces unexpected outputs.",
     (2,)),
    ("MG-4.1-005", "MANAGE 4.1",
     "Share transparency reports with internal and external stakeholders "
     "that detail steps taken to update the GAI system to enhance "
     "transparency and accountability.",
     (6, 7)),
    ("MG-4.1-006", "MANAGE 4.1",
     "Track dataset modifications for provenance by monitoring data "
     "deletions, rectification requests, and other changes that may "
     "impact the verifiability of content origins.",
     (8,)),
    ("MG-4.1-007", "MANAGE 4.1",
     "Verify that AI Actors responsible for monitoring reported issues "
     "can effectively evaluate GAI system performance including the "
     "application of content provenance data tracking techniques, and "
     "promptly escalate issues for response.",
     (7, 8)),

    # ── MANAGE 4.2 ──────────────────────────────────────────────────────
    ("MG-4.2-001", "MANAGE 4.2",
     "Conduct regular monitoring of GAI systems and publish reports "
     "detailing the performance, feedback received, and improvements "
     "made.",
     (6,)),
    ("MG-4.2-002", "MANAGE 4.2",
     "Practice and follow incident response plans for addressing the "
     "generation of inappropriate or harmful content and adapt processes "
     "based on findings to prevent future occurrences. Conduct "
     "post-mortem analyses of incidents with relevant AI Actors, to "
     "understand the root causes and implement preventive measures.",
     (3, 7)),
    ("MG-4.2-003", "MANAGE 4.2",
     "Use visualizations or other methods to represent GAI model "
     "behavior to ease non-technical stakeholders understanding of GAI "
     "system functionality.",
     (7,)),

    # ── MANAGE 4.3 ──────────────────────────────────────────────────────
    ("MG-4.3-001", "MANAGE 4.3",
     "Conduct after-action assessments for GAI system incidents to "
     "verify incident response and recovery processes are followed and "
     "effective, including to follow procedures for communicating "
     "incidents to relevant AI Actors and where applicable, relevant "
     "legal and regulatory bodies.",
     (9,)),
    ("MG-4.3-002", "MANAGE 4.3",
     "Establish and maintain policies and procedures to record and track "
     "GAI system reported errors, near-misses, and negative impacts.",
     (2, 8)),
    ("MG-4.3-003", "MANAGE 4.3",
     "Report GAI incidents in compliance with legal and regulatory "
     "requirements (e.g., HIPAA breach reporting, e.g., OCR (2023) or "
     "NHTSA (2022) autonomous vehicle crash reporting requirements.",
     (4, 9)),
)


# ═══════════════════════════════════════════════════════════════════════════
#  LES INDEX — DÉRIVÉS, JAMAIS SAISIS
# ═══════════════════════════════════════════════════════════════════════════

PREFIXES = {"GV": "GOVERN", "MP": "MAP", "MS": "MEASURE", "MG": "MANAGE"}

ACTIONS_PAR_CODE = {}
PAR_SOUS_CATEGORIE = {}
PAR_CATEGORIE = {}
PAR_RISQUE = {}
for _code, _sc, _txt, _ris in ACTIONS:
    _cat = _sc.rsplit(".", 1)[0]
    _a = {"code": _code, "sous_categorie": _sc, "categorie": _cat,
          "fonction": _sc.split(" ", 1)[0], "texte": _txt,
          "risques": tuple(_ris)}
    ACTIONS_PAR_CODE[_code] = _a
    PAR_SOUS_CATEGORIE.setdefault(_sc, []).append(_code)
    PAR_CATEGORIE.setdefault(_cat, []).append(_code)
    for _n in _ris:
        PAR_RISQUE.setdefault(_n, []).append(_code)

# LES 23 SOUS-CATÉGORIES QUE LE PROFIL NE CHARGE PAS. Elles se calculent, et
# la garde vérifie qu'elles sont bien 23 — le nombre a été compté dans le
# document avant d'être écrit ici.
SOUS_CATEGORIES_SANS_ACTION = tuple(
    cle for cle, _ in _rmf.SOUS_CATEGORIES if cle not in PAR_SOUS_CATEGORIE)


# LA DISTRIBUTION MESURÉE DANS LE DOCUMENT, ÉCRITE À LA MAIN ────────────────
#
# ELLE N'EST PAS DÉRIVÉE DE LA TABLE, SANS QUOI ELLE NE GARDERAIT RIEN. C'est
# le relevé fait sur le PDF ; la garde le confronte à ce que la table rend.
# Déplacer une seule action d'un risque à un autre fait tomber le module au
# chargement — et c'est la seule façon d'empêcher qu'une retouche « de
# confort » sur un libellé emporte un rattachement avec elle.
COMPTES_MESURES = {
    "actions": 211,
    "risques": {1: 29, 2: 18, 3: 31, 4: 28, 5: 4, 6: 57,
                7: 56, 8: 71, 9: 50, 10: 28, 11: 14, 12: 36, 0: 1},
    "fonctions": {"GOVERN": 57, "MAP": 39, "MEASURE": 72, "MANAGE": 43},
    "sous_categories_chargees": 49,
    "sous_categories_sans_action": 23,
}


# ═══════════════════════════════════════════════════════════════════════════
#  CE QUE LE CLIENT DÉCLARE SUR UNE ACTION
# ═══════════════════════════════════════════════════════════════════════════
#
# TROIS ÉTATS, ET « SANS RÉPONSE » N'EN EST PAS UN. Une action jamais ouverte
# n'est pas tenue : la compter autrement ferait rendre 100 % à un
# questionnaire vide, ce qui est le défaut le plus courant de ce genre
# d'écran. Elle est comptée à part, pour que l'écran puisse dire « vous n'en
# avez pas encore regardé 40 » plutôt que « vous en ratez 40 ».

ETATS_ACTION = {
    "tenue": {"nom": "Tenue", "note": 1,
              "dit": "L'action est en place pour ce système."},
    "non_tenue": {"nom": "Non tenue", "note": 0,
                  "dit": "Regardée, et pas en place."},
    "sans_objet": {"nom": "Sans objet", "note": None,
                   "dit": "L'action ne s'applique pas à ce système — et il "
                          "faut pouvoir dire pourquoi."},
}

# L'ÉCHELLE DU CADRE, REPRISE TELLE QUELLE. On ne la redéfinit pas : elle est
# dans `nist_ai_rmf`, et un plafond qui ne parlerait pas la même langue que
# l'état qu'il plafonne ne plafonnerait rien.
_RANG = {cle: e["note"] for cle, e in _rmf.ETATS.items()
         if e["note"] is not None}


def plafond_de(taux):
    """L'état le plus haut qu'une catégorie peut porter à cette couverture.

    AUCUNE ACTION APPLICABLE → AUCUN PLAFOND, et c'est le point délicat. Le
    profil n'a rien à dire là ; lui faire dire « zéro tenu » transformerait
    un silence du NIST en reproche au client.
    """
    if taux is None:
        return None
    if taux <= 0:
        return "amorce"
    if taux < 100:
        return "tenu"
    return None


def plafonner(etat, plafond):
    """Le plafond ne descend un état que s'il est plus bas. IL NE MONTE
    JAMAIS RIEN : une catégorie absente au socle reste absente, quand bien
    même toutes les actions du profil seraient tenues. Le profil suppose le
    cadre, il ne le remplace pas."""
    if plafond is None or etat not in _RANG or plafond not in _RANG:
        return etat
    return plafond if _RANG[plafond] < _RANG[etat] else etat


# ═══════════════════════════════════════════════════════════════════════════
#  LE CHAMP : QUELLES ACTIONS LES RISQUES DÉCLARÉS APPELLENT
# ═══════════════════════════════════════════════════════════════════════════

def risques_declares(risques=None):
    """Les numéros retenus parmi les douze, triés et dédoublonnés.

    UN SEUL ENDROIT LIT CE CHAMP. Le plan et l'analyse le lisaient chacun à
    leur façon, et deux lectures d'une même saisie finissent toujours par
    diverger sur un cas — ici, la chaîne « 06 » ou le nombre flottant.
    """
    out = set()
    for n in (risques or ()):
        try:
            n = int(n)
        except (TypeError, ValueError):
            continue
        if n in _rmf.RISQUES_PAR_N:
            out.add(n)
    return sorted(out)


def applicables(risques=None):
    """Les codes que les risques déclarés rendent applicables, dans l'ordre
    de la table.

    LE RISQUE 0 N'EN APPELLE AUCUN. « Civil Rights violations » n'est pas un
    des douze : le retenir ici ferait entrer GV-1.4-002 dans le champ d'un
    client qui n'a déclaré aucun des douze risques, sur la foi d'une
    étiquette que le document n'a pas définie.
    """
    voulus = set(risques_declares(risques))
    if not voulus:
        return []
    return [a[0] for a in ACTIONS if voulus.intersection(a[3])]


def couverture(portee, actions=None):
    """Ce que la déclaration rend sur une portée d'actions données."""
    dec = actions if isinstance(actions, dict) else {}
    tenues, ecartees, sans_reponse, refusees = [], [], [], []
    for c in portee:
        e = dec.get(c)
        if e == "tenue":
            tenues.append(c)
        elif e == "sans_objet":
            ecartees.append(c)
        elif e == "non_tenue":
            refusees.append(c)
        else:
            sans_reponse.append(c)
    portees = len(portee) - len(ecartees)
    return {
        "applicables": len(portee), "tenues": len(tenues),
        "ecartees": len(ecartees), "non_tenues": len(refusees),
        "sans_reponse": len(sans_reponse), "portees": portees,
        "taux": (None if not portees
                 else int(round(100.0 * len(tenues) / portees))),
        "codes_tenues": tenues, "codes_manquantes": refusees + sans_reponse,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  LE PLAFOND PAR CATÉGORIE — CE QUI FAIT BOUGER LE TAUX DÉJÀ AFFICHÉ
# ═══════════════════════════════════════════════════════════════════════════

def par_categorie(declaration=None):
    """Pour chacune des 19 catégories du cadre : ce que le profil y attache,
    ce qui en est tenu, et le plafond qui en découle."""
    d = declaration if isinstance(declaration, dict) else {}
    champ = set(applicables(d.get("risques")))
    actions = d.get("actions") if isinstance(d.get("actions"), dict) else {}
    out = []
    for cat in _rmf.CATEGORIES:
        portee = [c for c in PAR_CATEGORIE.get(cat["cle"], ()) if c in champ]
        cv = couverture(portee, actions)
        # « SANS OBJET POUR LE PROFIL » N'EST PAS « NON COUVERTE ». Deux
        # chemins y mènent : le NIST n'attache rien à cette catégorie pour
        # l'IA générative, ou les risques déclarés n'en appellent aucune.
        sans_objet_profil = not portee
        out.append({
            "cle": cat["cle"], "nom": cat["nom"], "fonction": cat["fonction"],
            "attachees": len(PAR_CATEGORIE.get(cat["cle"], ())),
            "applicables": cv["applicables"], "tenues": cv["tenues"],
            "ecartees": cv["ecartees"], "non_tenues": cv["non_tenues"],
            "sans_reponse": cv["sans_reponse"], "portees": cv["portees"],
            "taux": cv["taux"],
            "plafond": plafond_de(cv["taux"]),
            "sans_objet_pour_le_profil": sans_objet_profil,
            # TOUTES ÉCARTÉES N'EST PAS SANS OBJET : là, le client a dit non
            # à chaque action que le NIST attache. Aucun plafond ne tombe —
            # mais l'écran le nomme, parce que c'est une porte de sortie et
            # qu'une porte de sortie se voit.
            "ecartee_en_entier": bool(portee) and cv["portees"] == 0,
        })
    return out


def etats_du_profil(etats=None, declaration=None):
    """Les états du cadre, plafonnés par le profil. Rend (états, mouvements).

    HORS SYSTÈME GÉNÉRATIF, RIEN NE BOUGE — et le dire est la moitié de
    l'intérêt : le profil ne s'applique pas à un modèle de scoring
    déterministe, et lui faire baisser son taux au nom de l'IA générative
    serait un reproche inventé.
    """
    base = dict(etats) if isinstance(etats, dict) else {}
    d = declaration if isinstance(declaration, dict) else {}
    if not d.get("genai"):
        return base, []
    mouvements = []
    for ligne in par_categorie(d):
        avant = base.get(ligne["cle"])
        apres = plafonner(avant, ligne["plafond"])
        if apres != avant:
            base[ligne["cle"]] = apres
            mouvements.append({
                "categorie": ligne["cle"], "nom": ligne["nom"],
                "fonction": ligne["fonction"], "de": avant, "vers": apres,
                "taux": ligne["taux"], "applicables": ligne["applicables"],
                "tenues": ligne["tenues"],
            })
    return base, mouvements


# ═══════════════════════════════════════════════════════════════════════════
#  LE PLAN — DÉRIVÉ DES RISQUES DÉCLARÉS, PAS D'UNE LISTE DE SOUHAITS
# ═══════════════════════════════════════════════════════════════════════════

def plan(declaration=None, limite=None):
    """Les actions applicables qui ne sont pas tenues, les plus portantes
    d'abord.

    L'ORDRE EST CALCULÉ, ET IL SE JUSTIFIE EN DEUX PHRASES : une action qui
    traite QUATRE des risques déclarés vaut mieux qu'une qui en traite un, et
    à portée égale l'ordre du cadre commande — GOVERN d'abord, parce que le
    reste en dépend. Trier par code aurait rangé le travail par numéro de
    paragraphe, ce qui n'est l'ordre de personne.
    """
    d = declaration if isinstance(declaration, dict) else {}
    voulus = set(risques_declares(d.get("risques")))
    actions = d.get("actions") if isinstance(d.get("actions"), dict) else {}
    rang_f = {f: i for i, f in enumerate(_rmf.ORDRE)}
    out = []
    for code in applicables(d.get("risques")):
        if actions.get(code) in ("tenue", "sans_objet"):
            continue
        a = ACTIONS_PAR_CODE[code]
        portes = sorted(voulus.intersection(a["risques"]))
        out.append({
            "code": code, "sous_categorie": a["sous_categorie"],
            "categorie": a["categorie"], "fonction": a["fonction"],
            "texte": a["texte"],
            "risques": [{"n": n, "nom": _rmf.RISQUES_PAR_N[n]["nom"]}
                        for n in portes],
            "porte": len(portes),
            "deja_vue": actions.get(code) == "non_tenue",
        })
    out.sort(key=lambda x: (-x["porte"], rang_f.get(x["fonction"], 9),
                            x["code"]))
    for i, e in enumerate(out, 1):
        e["rang"] = i
    return out[:limite] if limite else out


# ═══════════════════════════════════════════════════════════════════════════
#  L'ANALYSE
# ═══════════════════════════════════════════════════════════════════════════

def analyse(declaration=None, etats=None):
    """Le profil tel qu'il se lit à l'écran : le champ, la couverture, les
    plafonds tombés, et ce qui reste à tenir."""
    d = declaration if isinstance(declaration, dict) else {}
    genai = bool(d.get("genai"))
    actions = d.get("actions") if isinstance(d.get("actions"), dict) else {}
    inconnues = sorted(c for c in actions if c not in ACTIONS_PAR_CODE)
    if inconnues:
        # UN CODE QU'ON NE CONNAÎT PAS NE SE RANGE PAS EN SILENCE. Le compter
        # « tenu » gonflerait une couverture avec une action qui n'existe
        # pas ; l'ignorer laisserait un écran remplir du vide sans le savoir.
        return {"ok": False, "motif": "actions_inconnues",
                "detail": inconnues[:8]}
    mauvais = sorted(c for c, e in actions.items() if e not in ETATS_ACTION)
    if mauvais:
        return {"ok": False, "motif": "etats_inconnus", "detail": mauvais[:8]}

    declares = risques_declares(d.get("risques"))
    champ = applicables(declares)
    dans_le_champ = set(champ)
    cv = couverture(champ, actions)
    lignes = par_categorie(d)
    _, mouvements = etats_du_profil(etats, d)

    if not genai:
        tete, dit = "hors_profil", (
            "Le système n'est pas déclaré génératif. Le profil AI 600-1 ne "
            "s'applique pas, et le taux du cadre reste celui du socle. Ce "
            "n'est pas une dispense : c'est une qualification, et elle se "
            "revoit le jour où un modèle de langage entre dans la chaîne.")
    elif not declares:
        tete, dit = "risques_absents", (
            "Le système est déclaré génératif, mais aucun des douze risques "
            "n'est retenu. Aucune action n'est donc applicable et aucun "
            "plafond ne tombe — ce qui revient à dire que la génération "
            "n'apporte aucun risque. C'est la seule réponse du questionnaire "
            "qu'un auditeur ouvrira en premier.")
    elif cv["taux"] is None:
        tete, dit = "tout_ecarte", (
            "Les %d actions applicables sont toutes écartées. Le profil ne "
            "plafonne donc rien — mais chaque « sans objet » se justifie "
            "devant un tiers, et ils sont ici au complet."
            % cv["applicables"])
    elif cv["taux"] >= 100:
        tete, dit = "couvert", (
            "Les %d actions applicables sont tenues. Le profil ne plafonne "
            "aucune catégorie : le taux du cadre est celui du socle, et il "
            "vaut pour un système génératif." % cv["portees"])
    elif not cv["tenues"]:
        tete, dit = "aucune_tenue", (
            "Aucune des %d actions applicables n'est tenue. Les %d "
            "catégories que le profil charge ne peuvent pas dépasser "
            "« amorcé », quel que soit l'état déclaré au socle."
            % (cv["portees"], sum(1 for l in lignes if l["applicables"])))
    else:
        tete, dit = "partiel", (
            "%d des %d actions applicables sont tenues. Les catégories "
            "incomplètes ne peuvent pas dépasser « tenu » : « prouvé » "
            "suppose que rien ne manque, et il manque quelque chose."
            % (cv["tenues"], cv["portees"]))

    return {
        "ok": True,
        "genai": genai,
        "risques": [dict(_rmf.RISQUES_PAR_N[n],
                         actions=len([c for c in PAR_RISQUE.get(n, ())
                                      if c in dans_le_champ]))
                    for n in declares],
        "risques_declares": declares,
        "champ": len(champ),
        "couverture": cv,
        "taux": cv["taux"] if genai else None,
        "par_categorie": lignes,
        "mouvements": mouvements,
        "categories_plafonnees": len([l for l in lignes if l["plafond"]])
                                 if genai else 0,
        "sans_objet_pour_le_profil": [l["cle"] for l in lignes
                                      if l["sans_objet_pour_le_profil"]],
        "ecartees_en_entier": [l["cle"] for l in lignes
                               if l["ecartee_en_entier"]],
        "sous_categories_sans_action": list(SOUS_CATEGORIES_SANS_ACTION),
        "tete": tete, "dit": dit,
        "certifiable": False,
        "reserve":
            "AI 600-1 est un PROFIL d'AI 100-1, et il ne se certifie pas "
            "davantage que lui. Ces 211 actions sont « suggérées » — le "
            "document le dit ainsi, et il ne prétend ni être exhaustif ni "
            "convenir à tous les systèmes. Elles ne valent donc pas une "
            "liste de contrôle opposable : elles disent ce qu'un tiers "
            "s'attendra à trouver, et ce qu'il faudra savoir justifier "
            "quand il ne le trouvera pas.",
    }


def referentiel():
    """La table, telle que l'écran la demande — sans jamais la recopier."""
    return {
        "source": dict(SOURCE),
        "profil_de": "NIST AI 100-1",
        "reconciliations": [dict(r) for r in RECONCILIATIONS],
        "hors_douze": [dict(v) for v in HORS_DOUZE.values()],
        "actions": [dict(ACTIONS_PAR_CODE[a[0]],
                         risques=list(ACTIONS_PAR_CODE[a[0]]["risques"]))
                    for a in ACTIONS],
        "par_sous_categorie": {k: list(v)
                               for k, v in PAR_SOUS_CATEGORIE.items()},
        "sous_categories_sans_action": list(SOUS_CATEGORIES_SANS_ACTION),
        "risques": [dict(r, actions=len(PAR_RISQUE.get(r["n"], ())))
                    for r in _rmf.RISQUES_GENAI],
        "etats_action": ETATS_ACTION,
        "comptes": COMPTES_MESURES,
        "certifiable": False,
        "reserve":
            "NIST AI 600-1 est une œuvre du gouvernement des États-Unis : "
            "les 211 énoncés sont repris mot pour mot, en anglais, parce que "
            "c'est le libellé qu'un auditeur cherchera. Le profil ne se "
            "certifie pas, et il ne vaut rien sans le cadre AI 100-1 "
            "en dessous.",
    }


# ═══════════════════════════════════════════════════════════════════════════
#  LA GARDE — ELLE REJOUE LE PLAFOND, ELLE NE LE RELIT PAS
# ═══════════════════════════════════════════════════════════════════════════

_SOUS_DU_CADRE = frozenset(cle for cle, _ in _rmf.SOUS_CATEGORIES)


def _verifier():
    fautes = []

    # ── LA TABLE SE RECOMPTE ────────────────────────────────────────────
    if len(ACTIONS) != COMPTES_MESURES["actions"]:
        fautes.append("la table porte %d actions, le document en a %d"
                      % (len(ACTIONS), COMPTES_MESURES["actions"]))
    if len(ACTIONS_PAR_CODE) != len(ACTIONS):
        fautes.append("deux actions portent le même code")

    for code, sc, txt, ris in ACTIONS:
        tete = code.split("-", 1)[0]
        if tete not in PREFIXES:
            fautes.append("%s : préfixe inconnu" % code)
            continue
        numero = code.split("-")[1]
        attendu = "%s %s" % (PREFIXES[tete], numero)
        if attendu != sc:
            fautes.append("%s dit « %s » et se range sous « %s »"
                          % (code, attendu, sc))
        if sc not in _SOUS_DU_CADRE:
            fautes.append("%s : la sous-catégorie %s n'est pas au cadre"
                          % (code, sc))
        if not txt.strip():
            fautes.append("%s : énoncé vide" % code)
        if not ris:
            fautes.append("%s : aucun risque" % code)
        inconnus = [n for n in ris
                    if n not in _rmf.RISQUES_PAR_N and n not in HORS_DOUZE]
        if inconnus:
            fautes.append("%s : risque(s) %s hors des douze et hors liste"
                          % (code, inconnus))
        # UNE ACTION QUE SEULE L'ÉTIQUETTE HORS LISTE PORTERAIT n'entrerait
        # jamais dans aucun champ : elle serait dans la table sans pouvoir en
        # sortir. Aucune n'est dans ce cas, et la garde le tient.
        if ris and not [n for n in ris if n in _rmf.RISQUES_PAR_N]:
            fautes.append("%s : aucun des douze risques — inatteignable"
                          % code)

    # ── LA DISTRIBUTION MESURÉE ─────────────────────────────────────────
    for n, attendu in sorted(COMPTES_MESURES["risques"].items()):
        eu = len(PAR_RISQUE.get(n, ()))
        if eu != attendu:
            fautes.append("le risque %s porte %d actions, le relevé en "
                          "compte %d" % (n, eu, attendu))
    if set(PAR_RISQUE) - set(COMPTES_MESURES["risques"]):
        fautes.append("un risque de la table n'est pas au relevé : %s"
                      % sorted(set(PAR_RISQUE)
                               - set(COMPTES_MESURES["risques"])))
    for f, attendu in sorted(COMPTES_MESURES["fonctions"].items()):
        eu = len([a for a in ACTIONS if a[1].split(" ", 1)[0] == f])
        if eu != attendu:
            fautes.append("%s porte %d actions, le relevé en compte %d"
                          % (f, eu, attendu))
    if len(PAR_SOUS_CATEGORIE) != COMPTES_MESURES["sous_categories_chargees"]:
        fautes.append("%d sous-catégories chargées, le relevé en compte %d"
                      % (len(PAR_SOUS_CATEGORIE),
                         COMPTES_MESURES["sous_categories_chargees"]))
    if len(SOUS_CATEGORIES_SANS_ACTION) \
            != COMPTES_MESURES["sous_categories_sans_action"]:
        fautes.append("%d sous-catégories sans action, le relevé en compte %d"
                      % (len(SOUS_CATEGORIES_SANS_ACTION),
                         COMPTES_MESURES["sous_categories_sans_action"]))

    # ── LES RÉCONCILIATIONS DISENT DES NOMBRES : ILS SE VÉRIFIENT ───────
    for r in RECONCILIATIONS:
        eu = len(PAR_RISQUE.get(r["risque"], ()))
        if eu != r["actions"]:
            fautes.append("la réconciliation « %s » annonce %d actions, la "
                          "table en porte %d"
                          % (r["au_paragraphe_3"], r["actions"], eu))

    # ── LE PLAFOND SE REJOUE, SUR QUATRE CAS ÉCRITS ICI ─────────────────
    #
    # SANS CETTE PARTIE, LA GARDE NE GARDERAIT QUE DES NOMBRES. C'est le
    # plafond qui change le taux affiché au client : il doit tomber quand il
    # doit tomber, et JAMAIS monter un état.
    douze = [r["n"] for r in _rmf.RISQUES_GENAI]
    tout_prouve = {c["cle"]: "prouve" for c in _rmf.CATEGORIES}
    tout_absent = {c["cle"]: "absent" for c in _rmf.CATEGORIES}
    champ = applicables(douze)

    # 1. non génératif : rien ne bouge, quelle que soit la couverture.
    inchange, mvts = etats_du_profil(
        tout_prouve, {"genai": False, "risques": douze, "actions": {}})
    if inchange != tout_prouve or mvts:
        fautes.append("un système NON génératif voit son socle plafonné")

    # 2. génératif, rien de tenu : toutes les catégories chargées tombent à
    #    « amorcé », et aucune autre ne bouge.
    bas, mvts = etats_du_profil(
        tout_prouve, {"genai": True, "risques": douze, "actions": {}})
    charge = [c["cle"] for c in _rmf.CATEGORIES if PAR_CATEGORIE.get(c["cle"])]
    tombees = [k for k, v in bas.items() if v == "amorce"]
    if sorted(tombees) != sorted(charge):
        fautes.append("à zéro action tenue, %d catégories tombent sur %d "
                      "chargées" % (len(tombees), len(charge)))
    if len(mvts) != len(charge):
        fautes.append("le nombre de mouvements ne suit pas les catégories "
                      "plafonnées")

    # 3. génératif, tout tenu : rien ne bouge — le travail déclaré tient.
    plein = {c: "tenue" for c in champ}
    haut, mvts = etats_du_profil(
        tout_prouve, {"genai": True, "risques": douze, "actions": plein})
    if haut != tout_prouve or mvts:
        fautes.append("toutes les actions tenues, et le socle est quand "
                      "même plafonné")

    # 4. LE PLAFOND NE MONTE JAMAIS : socle absent, profil À MOITIÉ tenu.
    #
    #    LA COUVERTURE DOIT ÊTRE PARTIELLE, ET CE DÉTAIL EST TOUT LE
    #    CONTRÔLE. Une première version jouait ce cas à 100 % : il n'y a
    #    alors AUCUN plafond, `plafonner` sort avant la comparaison, et la
    #    garde ne gardait rien — inverser le sens de la comparaison passait
    #    au travers. À moitié, les deux plafonds existent (« amorcé » là où
    #    rien n'est tenu, « tenu » là où une partie l'est) et doivent tous
    #    deux laisser « absent » où il est.
    moitie = {code: "tenue" for code in champ[:len(champ) // 2]}
    reste, _ = etats_du_profil(
        tout_absent, {"genai": True, "risques": douze, "actions": moitie})
    if reste != tout_absent:
        fautes.append("le plafond du profil a RELEVÉ un état du socle : %s"
                      % sorted(k for k, v in reste.items() if v != "absent")[:4])
    plafonds_joues = {plafond_de(l["taux"]) for l in par_categorie(
        {"genai": True, "risques": douze, "actions": moitie})}
    if not {"amorce", "tenu"} <= plafonds_joues:
        fautes.append("le cas « le plafond ne monte pas » ne joue pas les "
                      "deux plafonds : %s" % sorted(
                          str(x) for x in plafonds_joues))

    # 5. UNE COUVERTURE PARTIELLE PLAFONNE À « TENU », PAS PLUS BAS. Une
    #    seule action tenue dans une catégorie suffit à sortir d'« amorcé ».
    une = next(iter(PAR_CATEGORIE["GOVERN 1"]))
    partiel, _ = etats_du_profil(
        tout_prouve, {"genai": True, "risques": douze, "actions": {une: "tenue"}})
    if partiel.get("GOVERN 1") != "tenu":
        fautes.append("une catégorie partiellement couverte ne plafonne pas "
                      "à « tenu » mais à « %s »" % partiel.get("GOVERN 1"))

    # 6. LE CHAMP SUIT LES RISQUES DÉCLARÉS, et l'étiquette hors liste
    #    n'ouvre rien à elle seule.
    if applicables([0]):
        fautes.append("l'étiquette hors des douze rend des actions "
                      "applicables à elle seule")
    if len(champ) != len(ACTIONS):
        fautes.append("les douze risques n'appellent pas toute la table : "
                      "%d sur %d" % (len(champ), len(ACTIONS)))

    if fautes:
        raise RuntimeError(
            "nist_genai : la table du profil AI 600-1 est incohérente — "
            + " ; ".join(fautes[:8]))
    return fautes


_FAUTES = _verifier()
