# -*- coding: utf-8 -*-
"""LE CADRE NIST DE GESTION DES RISQUES DE L'IA — ET CE QU'IL N'EST PAS.

═══ CE QU'IL EST ════════════════════════════════════════════════════════
NIST AI 100-1, « Artificial Intelligence Risk Management Framework (AI RMF
1.0) », janvier 2023. Quatre fonctions — GOVERN, MAP, MEASURE, MANAGE —
déclinées en 19 catégories et 72 sous-catégories. Les nombres ci-dessus ne
sont pas repris d'un commentaire : ils ont été comptés dans le document
lui-même, et la garde en bas de fichier les recompte à chaque chargement.

S'y ajoute NIST AI 600-1, « Generative Artificial Intelligence Profile »,
juillet 2024 : douze risques propres à l'IA générative.

═══ CE QU'IL N'EST PAS, ET C'EST LE PLUS UTILE À SAVOIR ═════════════════
IL NE SE CERTIFIE PAS. Le cadre est volontaire : il n'y a pas d'organisme
d'accréditation, pas d'auditeur habilité, pas de certificat. « Conforme NIST
AI RMF » ne veut rien dire — au mieux, cela signifie « nous nous en sommes
servis ». C'est exactement la réserve qui vaut déjà pour ISO/IEC 27090 dans
ce cabinet, et elle se dit avant le premier écran, pas après.

ET AI 600-1 EST UN PROFIL, PAS UN SECOND CADRE. Ses actions suggérées se
rattachent aux sous-catégories du RMF : le citer sans le cadre en dessous,
c'est citer le profil de rien.

═══ CE QUE CE MODULE MESURE, ET POURQUOI CELA ═══════════════════════════
LES QUATRE FONCTIONS NE SONT PAS QUATRE COLONNES INDÉPENDANTES. MAP, MEASURE
et MANAGE supposent GOVERN : sans décision, sans rôle nommé, sans politique,
on cartographie des risques que personne ne s'est engagé à traiter et on
mesure des écarts que personne n'arbitrera. Une maison qui note bien sur
MANAGE et mal sur GOVERN ne « gère » rien — elle éteint des feux.

LE MODULE REND DONC DEUX CHOSES QU'UN SIMPLE POURCENTAGE NE REND PAS : la
note par fonction, et l'AVERTISSEMENT DE SOCLE quand l'aval dépasse l'amont.
Un score global unique aurait masqué exactement ce défaut-là, qui est le plus
fréquent.

═══ DROITS ══════════════════════════════════════════════════════════════
Les publications de la série technique du NIST sont des œuvres du
gouvernement des États-Unis. Elles se citent et se reprennent ; chaque
élément porte son identifiant et l'énoncé d'origine, en anglais, tel qu'il
figure au document. Ce qui est en français — ce qu'il faut montrer, ce qui
fait tomber une fonction — est le travail du cabinet, pas une traduction.
"""
import datetime


SOURCES = (
    {"cle": "rmf",
     "titre": "NIST AI 100-1 — AI Risk Management Framework (AI RMF 1.0)",
     "date": "2023-01", "doi": "https://doi.org/10.6028/NIST.AI.100-1",
     "droits": "Œuvre du gouvernement des États-Unis — libre de citation.",
     "certifiable": False},
    {"cle": "genai",
     "titre": "NIST AI 600-1 — AI RMF: Generative Artificial Intelligence Profile",
     "date": "2024-07", "doi": "https://doi.org/10.6028/NIST.AI.600-1",
     "droits": "Œuvre du gouvernement des États-Unis — libre de citation.",
     "certifiable": False},
)

# ═══════════════════════════════════════════════════════════════════════════
#  LES SEPT CARACTÉRISTIQUES D'UNE IA DIGNE DE CONFIANCE (AI 100-1, §3)
# ═══════════════════════════════════════════════════════════════════════════
#
# ELLES NE S'ADDITIONNENT PAS, ET LE DOCUMENT LE DIT : elles s'arbitrent.
# Rendre un système plus explicable peut le rendre moins sûr ; le rendre plus
# robuste peut coûter en équité. Une maison qui les présente comme sept cases
# à cocher n'a pas encore rencontré le premier arbitrage.

CARACTERISTIQUES = (
    ("Valid and Reliable", "Valide et fiable",
     "La seule qui soit un préalable : un système qui ne marche pas n'a pas "
     "besoin d'être équitable."),
    ("Safe", "Sûr",
     "L'atteinte aux personnes et aux biens, distincte de la sécurité "
     "informatique."),
    ("Secure and Resilient", "Sécurisé et résilient",
     "Celle que la cyber revendique — et la seule des sept qu'elle couvre."),
    ("Accountable and Transparent", "Redevable et transparent",
     "Quelqu'un répond, et on peut savoir de quoi."),
    ("Explainable and Interpretable", "Explicable et interprétable",
     "Deux choses distinctes : le mécanisme, et le sens pour celui qui subit "
     "la décision."),
    ("Privacy-Enhanced", "Respectueux de la vie privée",
     "Là où le RGPD et le cadre se rejoignent sans se recouvrir."),
    ("Fair – with Harmful Bias Managed", "Équitable, biais nuisibles maîtrisés",
     "Le document dit MAÎTRISÉS, pas absents : un biais nul n'existe pas, et "
     "promettre son absence est la faute la plus commune."),
)

# ═══════════════════════════════════════════════════════════════════════════
#  LES QUATRE FONCTIONS ET LEURS DIX-NEUF CATÉGORIES
# ═══════════════════════════════════════════════════════════════════════════

FONCTIONS = (
    {"cle": "GOVERN", "nom": "Gouverner", "rang": 0,
     "quoi": "La culture, les rôles, les politiques et les processus qui "
             "décident de ce qu'on fait de l'IA — et de qui en répond.",
     "socle": True,
     "ce_qui_la_fait_tomber":
         "Une politique IA écrite par la conformité, jamais lue par ceux qui "
         "construisent. Elle existe, elle est datée, et elle n'a aucun effet "
         "sur une seule décision d'architecture."},
    {"cle": "MAP", "nom": "Cartographier", "rang": 1,
     "quoi": "Établir le contexte : à quoi sert le système, sur quelles "
             "données, pour qui, avec quels tiers, et quels effets sur les "
             "personnes.",
     "socle": False,
     "ce_qui_la_fait_tomber":
         "Un inventaire des systèmes qui s'arrête à ceux que la DSI a "
         "achetés. Les usages arrivés par une carte bancaire d'équipe n'y "
         "figurent pas, et ce sont ceux qui posent problème."},
    {"cle": "MEASURE", "nom": "Mesurer", "rang": 2,
     "quoi": "Éprouver le système sur les caractéristiques de confiance, "
             "avec des méthodes et des métriques nommées, et suivre les "
             "risques dans le temps.",
     "socle": False,
     "ce_qui_la_fait_tomber":
         "Une évaluation faite une fois, à la mise en service, sur la "
         "version d'alors. Le fournisseur a changé le modèle depuis, et "
         "l'évaluation porte sur un système qui n'existe plus."},
    {"cle": "MANAGE", "nom": "Gérer", "rang": 3,
     "quoi": "Traiter, arbitrer, surveiller : affecter les ressources, "
             "décider ce qu'on accepte, préparer la réponse et la reprise.",
     "socle": False,
     "ce_qui_la_fait_tomber":
         "Un registre de risques tenu à jour et jamais arbitré. Tout y est "
         "noté, rien n'y est refusé, et le système part quand même."},
)

FONCTIONS_PAR_CLE = {f["cle"]: f for f in FONCTIONS}
ORDRE = [f["cle"] for f in FONCTIONS]


CATEGORIES = (
    {"cle": "GOVERN 1", "fonction": "GOVERN", "rang": 1,
     "nom": "Politiques, processus et pratiques",
     "dit": "Ce qui est écrit, et ce qui s'applique.",
     "enonce": "Policies, processes, procedures, and practices across the organization related to the mapping, measuring, and managing of AI risks are in place, transparent, and implemented effectively."},
    {"cle": "GOVERN 2", "fonction": "GOVERN", "rang": 2,
     "nom": "Redevabilité et rôles nommés",
     "dit": "Qui répond, et de quoi exactement.",
     "enonce": "Accountability structures are in place so that the appropriate teams and individuals are empowered, responsible, and trained for mapping, measuring, and managing AI risks."},
    {"cle": "GOVERN 3", "fonction": "GOVERN", "rang": 3,
     "nom": "Compétences et diversité des équipes",
     "dit": "Qui regarde le système, et avec quels angles morts.",
     "enonce": "Workforce diversity, equity, inclusion, and accessibility processes are prioritized in the mapping, measuring, and managing of AI risks throughout the lifecycle."},
    {"cle": "GOVERN 4", "fonction": "GOVERN", "rang": 4,
     "nom": "Culture du risque",
     "dit": "Ce qu'il en coûte, dans cette maison, de dire non.",
     "enonce": "Organizational teams are committed to a culture"},
    {"cle": "GOVERN 5", "fonction": "GOVERN", "rang": 5,
     "nom": "Engagement des parties prenantes",
     "dit": "Ceux qui subissent la décision ont-ils un canal.",
     "enonce": "Processes are in place for robust engagement with relevant AI actors."},
    {"cle": "GOVERN 6", "fonction": "GOVERN", "rang": 6,
     "nom": "Risques des tiers",
     "dit": "Le fournisseur de modèle est un tiers comme un autre — sauf qu'il change de version sans préavis.",
     "enonce": "Policies and procedures are in place to address AI risks and benefits arising from third-party software and data and other supply chain issues."},
    {"cle": "MAP 1", "fonction": "MAP", "rang": 1,
     "nom": "Le contexte est établi",
     "dit": "À quoi sert le système, et pour qui.",
     "enonce": "Context is established and understood."},
    {"cle": "MAP 2", "fonction": "MAP", "rang": 2,
     "nom": "Le système est catégorisé",
     "dit": "Ce qu'il fait, et ce qu'il ne sait pas faire.",
     "enonce": "Categorization of the AI system is performed."},
    {"cle": "MAP 3", "fonction": "MAP", "rang": 3,
     "nom": "Bénéfices et coûts attendus",
     "dit": "Y compris les coûts non monétaires.",
     "enonce": "AI capabilities, targeted usage, goals, and expected benefits and costs compared with appropriate benchmarks are understood."},
    {"cle": "MAP 4", "fonction": "MAP", "rang": 4,
     "nom": "Risques des composants, tiers compris",
     "dit": "La chaîne d'approvisionnement du modèle.",
     "enonce": "Risks and benefits are mapped for all components of the AI system including third-party software and data."},
    {"cle": "MAP 5", "fonction": "MAP", "rang": 5,
     "nom": "Effets sur les personnes et la société",
     "dit": "Ce que le système fait à ceux qui ne l'ont pas choisi.",
     "enonce": "Impacts to individuals, groups, communities, organizations, and society are characterized."},
    {"cle": "MEASURE 1", "fonction": "MEASURE", "rang": 1,
     "nom": "Méthodes et métriques",
     "dit": "Ce qu'on mesure, comment, et ce qu'on a renoncé à mesurer.",
     "enonce": "Appropriate methods and metrics are identified and applied."},
    {"cle": "MEASURE 2", "fonction": "MEASURE", "rang": 2,
     "nom": "Évaluation des caractéristiques de confiance",
     "dit": "Les sept, éprouvées — pas déclarées.",
     "enonce": "AI systems are evaluated for trustworthy characteristics."},
    {"cle": "MEASURE 3", "fonction": "MEASURE", "rang": 3,
     "nom": "Suivi des risques dans le temps",
     "dit": "Le système bouge ; la mesure d'hier ne vaut plus.",
     "enonce": "Mechanisms for tracking identified AI risks over time are in place."},
    {"cle": "MEASURE 4", "fonction": "MEASURE", "rang": 4,
     "nom": "Retour sur l'efficacité de la mesure",
     "dit": "Mesure-t-on ce qui compte, ou ce qui se mesure facilement.",
     "enonce": "Feedback about efficacy of measurement is gathered and assessed."},
    {"cle": "MANAGE 1", "fonction": "MANAGE", "rang": 1,
     "nom": "Priorisation et traitement",
     "dit": "Ce qu'on traite, et ce qu'on accepte par écrit.",
     "enonce": "AI risks based on assessments and other analytical output from the MAP and MEASURE functions are prioritized, responded to, and managed."},
    {"cle": "MANAGE 2", "fonction": "MANAGE", "rang": 2,
     "nom": "Stratégies de maximisation et de réduction",
     "dit": "Les ressources vont quelque part : où.",
     "enonce": "Strategies to maximize AI benefits and minimize negative impacts are planned, prepared, implemented, documented, and informed by input from relevant AI actors."},
    {"cle": "MANAGE 3", "fonction": "MANAGE", "rang": 3,
     "nom": "Risques des tiers, gérés",
     "dit": "Le contrat, la sortie, et ce qu'on fait si le tiers s'arrête.",
     "enonce": "AI risks and benefits from third-party entities are managed."},
    {"cle": "MANAGE 4", "fonction": "MANAGE", "rang": 4,
     "nom": "Réponse, reprise et communication",
     "dit": "Le jour où ça casse, qui fait quoi.",
     "enonce": "Risk treatments, including response and recovery, and communication plans for the identified and measured AI risks are documented and monitored regularly."},
)

CATEGORIES_PAR_CLE = {c["cle"]: c for c in CATEGORIES}

# ═══════════════════════════════════════════════════════════════════════════
#  LES SOIXANTE-DOUZE SOUS-CATÉGORIES
# ═══════════════════════════════════════════════════════════════════════════
#
# ELLES SONT REPRISES DU DOCUMENT, EN ANGLAIS ET VERBATIM. Deux raisons, et
# aucune n'est la paresse. La première : ce sont des œuvres du gouvernement
# des États-Unis, elles se citent. La seconde tient à l'usage — une
# sous-catégorie sert de PIÈCE dans une revue, et une pièce qu'on a traduite
# ne se retrouve plus dans le document quand l'auditeur demande où elle est
# écrite.
#
# ELLES NE SERVENT PAS DE QUESTIONNAIRE. Poser soixante-douze questions à un
# comité produit soixante-douze réponses de façade. L'évaluation se fait au
# niveau des dix-neuf catégories — la longueur d'un vrai atelier — et les
# sous-catégories sont la liste de preuves sous chacune.

SOUS_CATEGORIES = (
    ("GOVERN 1.1", "Legal and regulatory requirements involving AI are understood, managed, and documented."),
    ("GOVERN 1.2", "The characteristics of trustworthy AI are integrated into organizational policies, processes, procedures, and practices."),
    ("GOVERN 1.3", "Processes, procedures, and practices are in place to determine the needed level of risk management activities based on the organization’s risk tolerance."),
    ("GOVERN 1.4", "The risk management process and its outcomes are established through transparent policies, procedures, and other controls based on organizational risk priorities. Categories Subcategories Continued on next page Page 22 NIST AI…"),
    ("GOVERN 1.5", "Ongoing monitoring and periodic review of the risk management process and its outcomes are planned and organizational roles and responsibilities clearly defined, including determining the frequency of periodic review."),
    ("GOVERN 1.6", "Mechanisms are in place to inventory AI systems and are resourced according to organizational risk priorities."),
    ("GOVERN 1.7", "Processes and procedures are in place for decommissioning and phasing out AI systems safely and in a manner that does not increase risks or decrease the organization’s trustworthiness."),
    ("GOVERN 2.1", "Roles and responsibilities and lines of communication related to mapping, measuring, and managing AI risks are documented and are clear to individuals and teams throughout the organization."),
    ("GOVERN 2.2", "The organization’s personnel and partners receive AI risk management training to enable them to perform their duties and responsibilities consistent with related policies, procedures, and agreements."),
    ("GOVERN 2.3", "Executive leadership of the organization takes responsibility for decisions about risks associated with AI system development and deployment."),
    ("GOVERN 3.1", "Decision-making related to mapping, measuring, and managing AI risks throughout the lifecycle is informed by a diverse team (e.g., diversity of demographics, disciplines, experience, expertise, and backgrounds)."),
    ("GOVERN 3.2", "Policies and procedures are in place to define and differentiate roles and responsibilities for human-AI configurations and oversight of AI systems."),
    ("GOVERN 4.1", "Organizational policies and practices are in place to foster a critical thinking and safety-first mindset in the design, development, deployment, and uses of AI systems to minimize potential negative impacts. Categories…"),
    ("GOVERN 4.2", "Organizational teams document the risks and potential impacts of the AI technology they design, develop, deploy, evaluate, and use, and they communicate about the impacts more broadly."),
    ("GOVERN 4.3", "Organizational practices are in place to enable AI testing, identification of incidents, and information sharing."),
    ("GOVERN 5.1", "Organizational policies and practices are in place to collect, consider, prioritize, and integrate feedback from those external to the team that developed or deployed the AI system regarding the potential individual and…"),
    ("GOVERN 5.2", "Mechanisms are established to enable the team that developed or deployed AI systems to regularly incorporate adjudicated feedback from relevant AI actors into system design and implementation."),
    ("GOVERN 6.1", "Policies and procedures are in place that address AI risks associated with third-party entities, including risks of infringement of a third-party’s intellectual property or other rights."),
    ("GOVERN 6.2", "Contingency processes are in place to handle failures or incidents in third-party data or AI systems deemed to be high-risk. Categories Subcategories 5.2 Map The MAP function establishes the context to frame risks related to…"),
    ("MAP 1.1", "Intended purposes, potentially beneficial uses, contextspecific laws, norms and expectations, and prospective settings in which the AI system will be deployed are understood and documented. Considerations include: the specific…"),
    ("MAP 1.2", "Interdisciplinary AI actors, competencies, skills, and capacities for establishing context reflect demographic diversity and broad domain and user experience expertise, and their participation is documented. Opportunities for…"),
    ("MAP 1.3", "The organization’s mission and relevant goals for AI technology are understood and documented."),
    ("MAP 1.4", "The business value or context of business use has been clearly defined or – in the case of assessing existing AI systems – re-evaluated."),
    ("MAP 1.5", "Organizational risk tolerances are determined and documented."),
    ("MAP 1.6", "System requirements (e.g., “the system shall respect the privacy of its users”) are elicited from and understood by relevant AI actors. Design decisions take socio-technical implications into account to address AI risks."),
    ("MAP 2.1", "The specific tasks and methods used to implement the tasks that the AI system will support are defined (e.g., classifiers, generative models, recommenders)."),
    ("MAP 2.2", "Information about the AI system’s knowledge limits and how system output may be utilized and overseen by humans is documented. Documentation provides sufficient information to assist relevant AI actors when making decisions…"),
    ("MAP 2.3", "Scientific integrity and TEVV considerations are identified and documented, including those related to experimental design, data collection and selection (e.g., availability, representativeness, suitability), system…"),
    ("MAP 3.1", "Potential benefits of intended AI system functionality and performance are examined and documented."),
    ("MAP 3.2", "Potential costs, including non-monetary costs, which result from expected or realized AI errors or system functionality and trustworthiness – as connected to organizational risk tolerance – are examined and documented."),
    ("MAP 3.3", "Targeted application scope is specified and documented based on the system’s capability, established context, and AI system categorization."),
    ("MAP 3.4", "Processes for operator and practitioner proficiency with AI system performance and trustworthiness – and relevant technical standards and certifications – are defined, assessed, and documented."),
    ("MAP 3.5", "Processes for human oversight are defined, assessed, and documented in accordance with organizational policies from the GOVERN function."),
    ("MAP 4.1", "Approaches for mapping AI technology and legal risks of its components – including the use of third-party data or software – are in place, followed, and documented, as are risks of infringement of a third party’s intellectual…"),
    ("MAP 4.2", "Internal risk controls for components of the AI system, including third-party AI technologies, are identified and documented."),
    ("MAP 5.1", "Likelihood and magnitude of each identified impact (both potentially beneficial and harmful) based on expected use, past uses of AI systems in similar contexts, public incident reports, feedback from those external to the team…"),
    ("MAP 5.2", "Practices and personnel for supporting regular engagement with relevant AI actors and integrating feedback about positive, negative, and unanticipated impacts are in place and documented. Categories Subcategories 5.3 Measure…"),
    ("MEASURE 1.1", "Approaches and metrics for measurement of AI risks enumerated during the MAP function are selected for implementation starting with the most significant AI risks. The risks or trustworthiness characteristics that will not – or…"),
    ("MEASURE 1.2", "Appropriateness of AI metrics and effectiveness of existing controls are regularly assessed and updated, including reports of errors and potential impacts on affected communities."),
    ("MEASURE 1.3", "Internal experts who did not serve as front-line developers for the system and/or independent assessors are involved in regular assessments and updates. Domain experts, users, AI actors external to the team that developed or…"),
    ("MEASURE 2.1", "Test sets, metrics, and details about the tools used during TEVV are documented."),
    ("MEASURE 2.2", "Evaluations involving human subjects meet applicable requirements (including human subject protection) and are representative of the relevant population."),
    ("MEASURE 2.3", "AI system performance or assurance criteria are measured qualitatively or quantitatively and demonstrated for conditions similar to deployment setting(s). Measures are documented."),
    ("MEASURE 2.4", "The functionality and behavior of the AI system and its components – as identified in the MAP function – are monitored when in production."),
    ("MEASURE 2.5", "The AI system to be deployed is demonstrated to be valid and reliable. Limitations of the generalizability beyond the conditions under which the technology was developed are documented. Categories Subcategories Continued on…"),
    ("MEASURE 2.6", "The AI system is evaluated regularly for safety risks – as identified in theMAP function. The AI system to be deployed is demonstrated to be safe, its residual negative risk does not exceed the risk tolerance, and it can fail…"),
    ("MEASURE 2.7", "AI system security and resilience – as identified in the MAP function – are evaluated and documented."),
    ("MEASURE 2.8", "Risks associated with transparency and accountability – as identified in the MAP function – are examined and documented."),
    ("MEASURE 2.9", "The AI model is explained, validated, and documented, and AI system output is interpreted within its context – as identified in the MAP function – to inform responsible use and governance."),
    ("MEASURE 2.10", "Privacy risk of the AI system – as identified in the MAP function – is examined and documented."),
    ("MEASURE 2.11", "Fairness and bias – as identified in the MAP function – are evaluated and results are documented."),
    ("MEASURE 2.12", "Environmental impact and sustainability of AI model training and management activities – as identified in the MAP function – are assessed and documented."),
    ("MEASURE 2.13", "Effectiveness of the employed TEVV metrics and processes in the MEASURE function are evaluated and documented."),
    ("MEASURE 3.1", "Approaches, personnel, and documentation are in place to regularly identify and track existing, unanticipated, and emergent AI risks based on factors such as intended and actual performance in deployed contexts."),
    ("MEASURE 3.2", "Risk tracking approaches are considered for settings where AI risks are difficult to assess using currently available measurement techniques or where metrics are not yet available. Categories Subcategories Continued on next…"),
    ("MEASURE 3.3", "Feedback processes for end users and impacted communities to report problems and appeal system outcomes are established and integrated into AI system evaluation metrics."),
    ("MEASURE 4.1", "Measurement approaches for identifying AI risks are connected to deployment context(s) and informed through consultation with domain experts and other end users. Approaches are documented."),
    ("MEASURE 4.2", "Measurement results regarding AI system trustworthiness in deployment context(s) and across the AI lifecycle are informed by input from domain experts and relevant AI actors to validate whether the system is performing…"),
    ("MEASURE 4.3", "Measurable performance improvements or declines based on consultations with relevant AI actors, including affected communities, and field data about contextrelevant risks and trustworthiness characteristics are identified and…"),
    ("MANAGE 1.1", "A determination is made as to whether the AI system achieves its intended purposes and stated objectives and whether its development or deployment should proceed."),
    ("MANAGE 1.2", "Treatment of documented AI risks is prioritized based on impact, likelihood, and available resources or methods."),
    ("MANAGE 1.3", "Responses to the AI risks deemed high priority, as identified by the MAP function, are developed, planned, and documented. Risk response options can include mitigating, transferring, avoiding, or accepting."),
    ("MANAGE 1.4", "Negative residual risks (defined as the sum of all unmitigated risks) to both downstream acquirers of AI systems and end users are documented."),
    ("MANAGE 2.1", "Resources required to manage AI risks are taken into account – along with viable non-AI alternative systems, approaches, or methods – to reduce the magnitude or likelihood of potential impacts."),
    ("MANAGE 2.2", "Mechanisms are in place and applied to sustain the value of deployed AI systems."),
    ("MANAGE 2.3", "Procedures are followed to respond to and recover from a previously unknown risk when it is identified."),
    ("MANAGE 2.4", "Mechanisms are in place and applied, and responsibilities are assigned and understood, to supersede, disengage, or deactivate AI systems that demonstrate performance or outcomes inconsistent with intended use."),
    ("MANAGE 3.1", "AI risks and benefits from third-party resources are regularly monitored, and risk controls are applied and documented."),
    ("MANAGE 3.2", "Pre-trained models which are used for development are monitored as part of AI system regular monitoring and maintenance. Categories Subcategories Continued on next page Page 32 NIST AI 100-1 AI RMF 1.0 Table 4: Categories and…"),
    ("MANAGE 4.1", "Post-deployment AI system monitoring plans are implemented, including mechanisms for capturing and evaluating input from users and other relevant AI actors, appeal and override, decommissioning, incident response, recovery,…"),
    ("MANAGE 4.2", "Measurable activities for continual improvements are integrated into AI system updates and include regular engagement with interested parties, including relevant AI actors."),
    ("MANAGE 4.3", "Incidents and errors are communicated to relevant AI actors, including affected communities. Processes for tracking, responding to, and recovering from incidents and errors are followed and documented. Categories Subcategories…"),)

SOUS_PAR_CATEGORIE = {}
for _cle, _txt in SOUS_CATEGORIES:
    _cat = _cle.rsplit(".", 1)[0]
    SOUS_PAR_CATEGORIE.setdefault(_cat, []).append({"cle": _cle, "enonce": _txt})


# ═══════════════════════════════════════════════════════════════════════════
#  LES DOUZE RISQUES DU PROFIL IA GÉNÉRATIVE (NIST AI 600-1)
# ═══════════════════════════════════════════════════════════════════════════
#
# LEUR ORDRE EST ALPHABÉTIQUE DANS LE DOCUMENT, ET CE N'EST PAS UN CLASSEMENT
# DE GRAVITÉ. Le reprendre tel quel évite d'inventer une hiérarchie que le
# NIST s'est abstenu de poser — et la tentation est réelle, parce qu'un
# lecteur pressé lit le premier comme le pire.
#
# LA MOITIÉ D'ENTRE EUX NE RELÈVENT PAS DE LA CYBER — six sur douze, et la
# garde en bas de fichier le recompte plutôt que de s'en remettre à cette
# phrase. Le dire est utile : un RSSI à qui l'on confie « les risques de l'IA
# générative selon le NIST » se retrouve à répondre de l'empreinte
# environnementale, des biais et de la propriété intellectuelle, qu'il ne
# tient pas et sur lesquels il n'a aucun moyen d'action.

RISQUES_GENAI = (
    {"n": 1, "cle": "CBRN Information or Capabilities", "nom": "Informations NRBC",
     "cyber": False, "qui_le_tient": "Direction des risques, affaires publiques"},
    {"n": 2, "cle": "Confabulation", "nom": "Confabulation",
     "cyber": True, "qui_le_tient": "Métier et sécurité IA",
     "note": "Le document emploie « confabulation » plutôt qu'« hallucination » : "
             "le second terme prête au système une expérience qu'il n'a pas."},
    {"n": 3, "cle": "Dangerous, Violent, or Hateful Content",
     "nom": "Contenus dangereux, violents ou haineux",
     "cyber": False, "qui_le_tient": "Conformité, modération"},
    {"n": 4, "cle": "Data Privacy", "nom": "Vie privée",
     "cyber": True, "qui_le_tient": "Délégué à la protection des données"},
    {"n": 5, "cle": "Environmental Impacts", "nom": "Impacts environnementaux",
     "cyber": False, "qui_le_tient": "Direction immobilière et RSE"},
    {"n": 6, "cle": "Harmful Bias or Homogenization",
     "nom": "Biais nuisibles et homogénéisation",
     "cyber": False, "qui_le_tient": "Métier, validation des modèles"},
    {"n": 7, "cle": "Human-AI Configuration", "nom": "Configuration humain-IA",
     "cyber": True, "qui_le_tient": "Conception, sécurité IA",
     "note": "Le risque le plus sous-estimé du lot : il couvre la confiance "
             "excessive, la confusion sur qui décide, et l'anthropomorphisme."},
    {"n": 8, "cle": "Information Integrity", "nom": "Intégrité de l'information",
     "cyber": True, "qui_le_tient": "Cyberdéfense, communication"},
    {"n": 9, "cle": "Information Security", "nom": "Sécurité de l'information",
     "cyber": True, "qui_le_tient": "Cyberdéfense",
     "note": "Le seul des douze que la cyber couvre de bout en bout — et "
             "celui dont on déduit à tort qu'elle couvre les onze autres."},
    {"n": 10, "cle": "Intellectual Property", "nom": "Propriété intellectuelle",
     "cyber": False, "qui_le_tient": "Direction juridique"},
    {"n": 11, "cle": "Obscene, Degrading, and/or Abusive Content",
     "nom": "Contenus obscènes, dégradants ou abusifs",
     "cyber": False, "qui_le_tient": "Conformité, modération"},
    {"n": 12, "cle": "Value Chain and Component Integration",
     "nom": "Chaîne de valeur et intégration des composants",
     "cyber": True, "qui_le_tient": "Achats et sécurité des projets"},
)

RISQUES_PAR_N = {r["n"]: r for r in RISQUES_GENAI}


# ═══════════════════════════════════════════════════════════════════════════
#  L'ÉVALUATION — QUATRE NOTES, ET UN AVERTISSEMENT DE SOCLE
# ═══════════════════════════════════════════════════════════════════════════

ETATS = {
    "absent": {"note": 0, "nom": "Absent", "dit": "Rien en place."},
    "amorce": {"note": 1, "nom": "Amorcé",
               "dit": "Des travaux existent, sans être tenus."},
    "tenu": {"note": 2, "nom": "Tenu",
             "dit": "En place et appliqué, sans preuve systématique."},
    "prouve": {"note": 3, "nom": "Prouvé",
               "dit": "En place, appliqué, et démontrable sur pièce."},
    "sans_objet": {"note": None, "nom": "Sans objet",
                   "dit": "La catégorie ne s'applique pas — et il faut "
                          "pouvoir dire pourquoi."},
}

_NOTE_MAX = 3


def _profil_fonction(etats, fonction):
    """La note d'une fonction : la MOYENNE de ses catégories renseignées.

    POURQUOI UNE MOYENNE ICI, ALORS QUE LA CHAÎNE D'AUTONOMIE L'INTERDIT.
    Les deux mesurent des choses différentes. Une chaîne vaut son maillon le
    plus faible parce qu'une attaque passe par un seul maillon. Une fonction
    du cadre n'est pas une chaîne : GOVERN 3 faible ne rend pas GOVERN 1
    inutile. Ce qui ne se moyenne pas ici, c'est l'ENSEMBLE des quatre
    fonctions — et c'est précisément ce que ce module refuse de rendre.
    """
    cats = [c for c in CATEGORIES if c["fonction"] == fonction]
    notes = []
    sans_objet = []
    for c in cats:
        e = etats.get(c["cle"])
        if e == "sans_objet":
            sans_objet.append(c["cle"])
            continue
        if e in ETATS and ETATS[e]["note"] is not None:
            notes.append(ETATS[e]["note"])
    return {
        "fonction": fonction,
        "nom": FONCTIONS_PAR_CLE[fonction]["nom"],
        "categories": len(cats),
        "renseignees": len(notes),
        "sans_objet": sans_objet,
        "note": (round(sum(notes) / float(len(notes)), 2) if notes else None),
        "sur": _NOTE_MAX,
    }


def evaluer(etats=None, aujourdhui=None):
    """Le profil par fonction, et ce qui le commande.

    ═══ CE QUE CETTE FONCTION REFUSE DE RENDRE ══════════════════════════
    UNE NOTE GLOBALE. Additionner les quatre fonctions produit un chiffre qui
    monte quand on cartographie beaucoup et qu'on ne décide rien — c'est-à-dire
    exactement le profil le plus répandu, et celui que le cadre est écrit pour
    corriger. Une maison à 2,5/3 sur MAP et 0,5/3 sur GOVERN a un score moyen
    honorable et aucune gouvernance.

    ET UN TAUX DE CONFORMITÉ. Le cadre ne se certifie pas : il n'y a rien à
    quoi être conforme. Un pourcentage laisserait croire le contraire, et
    c'est la première chose qu'un lecteur reprendrait en comité.
    """
    etats = etats if isinstance(etats, dict) else {}
    inconnues = [k for k in etats if k not in CATEGORIES_PAR_CLE]
    mauvais = [k for k, v in etats.items() if v not in ETATS]
    if inconnues:
        return {"ok": False, "motif": "categories_inconnues",
                "detail": sorted(inconnues)[:8]}
    if mauvais:
        return {"ok": False, "motif": "etats_inconnus",
                "detail": sorted(mauvais)[:8]}

    profils = [_profil_fonction(etats, f) for f in ORDRE]
    par_cle = {p["fonction"]: p for p in profils}
    renseignees = sum(p["renseignees"] for p in profils)

    # ── L'AVERTISSEMENT DE SOCLE ─────────────────────────────────────────
    #
    # MAP, MEASURE ET MANAGE SUPPOSENT GOVERN. Quand l'aval dépasse l'amont
    # d'un point entier, la maison traite des risques que personne n'a
    # décidé d'assumer. Le seuil d'un point n'est pas cosmétique : en dessous,
    # l'écart tient au bruit d'une évaluation déclarative.
    socle = par_cle["GOVERN"]["note"]
    devant = []
    if socle is not None:
        for f in ORDRE[1:]:
            n = par_cle[f]["note"]
            if n is not None and n - socle >= 1.0:
                devant.append({"fonction": f, "nom": par_cle[f]["nom"],
                               "note": n, "socle": socle,
                               "ecart": round(n - socle, 2)})

    if not renseignees:
        tete, dit = "vide", (
            "Rien n'est renseigné. Le cadre ne rend aucun chiffre par défaut : "
            "un profil vide n'est pas un profil à zéro.")
    elif socle is None:
        tete, dit = "socle_absent", (
            "La fonction GOVERN n'est pas renseignée. C'est elle qui décide de "
            "ce qu'on fait de l'IA et de qui en répond ; sans elle, les trois "
            "autres notes portent sur des travaux que personne n'a commandés.")
    elif devant:
        tete, dit = "aval_devant_socle", (
            "%d fonction(s) devancent la gouvernance d'au moins un point. "
            "Ce n'est pas une bonne nouvelle : on cartographie, on mesure ou "
            "on traite des risques que personne ne s'est engagé à assumer. "
            "L'écart se résorbe par le haut, pas en ralentissant l'aval."
            % len(devant))
    else:
        tete, dit = "coherent", (
            "Le profil est cohérent : la gouvernance ne se fait pas devancer. "
            "Reste à savoir ce qu'on en prouve — l'état « tenu » et l'état "
            "« prouvé » se ressemblent en atelier et se séparent en revue.")

    return {
        "ok": True,
        "aujourdhui": (aujourdhui or datetime.date.today().isoformat()),
        "profils": profils,
        "categories": len(CATEGORIES),
        "renseignees": renseignees,
        "socle": socle,
        "devancent_le_socle": devant,
        "tete": tete,
        "dit": dit,
        "certifiable": False,
        "reserve":
            "Le cadre NIST AI RMF ne se certifie pas : aucun organisme "
            "n'accrédite, aucun auditeur n'habilite, aucun certificat "
            "n'existe. « Conforme NIST AI RMF » ne veut rien dire. Ce profil "
            "dit où vous en êtes de VOTRE usage du cadre, et rien d'autre.",
    }


def preuves(categorie):
    """Les sous-catégories qui servent de pièces sous une catégorie."""
    return list(SOUS_PAR_CATEGORIE.get(categorie, ()))


def referentiel():
    return {
        "sources": list(SOURCES),
        "caracteristiques": [{"en": a, "fr": b, "dit": c}
                             for a, b, c in CARACTERISTIQUES],
        "fonctions": list(FONCTIONS),
        "categories": list(CATEGORIES),
        "sous_categories": [{"cle": a, "enonce": b}
                            for a, b in SOUS_CATEGORIES],
        "risques_genai": list(RISQUES_GENAI),
        "etats": ETATS,
        "certifiable": False,
        "reserve":
            "NIST AI 100-1 et AI 600-1 sont des œuvres du gouvernement des "
            "États-Unis : elles se citent librement. Elles ne se certifient "
            "pas, et AI 600-1 est un PROFIL du cadre — le citer sans le cadre "
            "en dessous, c'est citer le profil de rien.",
    }


# ═══════════════════════════════════════════════════════════════════════════
#  LA GARDE
# ═══════════════════════════════════════════════════════════════════════════

def _verifier():
    fautes = []
    # ── LES COMPTES SONT CEUX DU DOCUMENT, ET ILS SE RECOMPTENT ─────────
    if len(FONCTIONS) != 4:
        fautes.append("le cadre ne compte pas quatre fonctions : %d" % len(FONCTIONS))
    if len(CATEGORIES) != 19:
        fautes.append("le cadre ne compte pas 19 catégories : %d" % len(CATEGORIES))
    if len(SOUS_CATEGORIES) != 72:
        fautes.append("le cadre ne compte pas 72 sous-catégories : %d"
                      % len(SOUS_CATEGORIES))
    if len(CARACTERISTIQUES) != 7:
        fautes.append("les caractéristiques de confiance ne sont pas sept : %d"
                      % len(CARACTERISTIQUES))
    if len(RISQUES_GENAI) != 12:
        fautes.append("le profil IA générative ne compte pas douze risques : %d"
                      % len(RISQUES_GENAI))
    if sorted(r["n"] for r in RISQUES_GENAI) != list(range(1, 13)):
        fautes.append("les douze risques ne sont pas numérotés de 1 à 12")

    # ── CHAQUE CATÉGORIE APPARTIENT À UNE FONCTION CONNUE ────────────────
    for c in CATEGORIES:
        if c["fonction"] not in FONCTIONS_PAR_CLE:
            fautes.append("la catégorie « %s » relève d'une fonction inconnue"
                          % c["cle"])
        if not str(c.get("enonce") or "").strip():
            fautes.append("la catégorie « %s » ne porte pas son énoncé d'origine"
                          % c["cle"])

    # ── CHAQUE SOUS-CATÉGORIE SE RATTACHE À UNE CATÉGORIE DÉCLARÉE ───────
    #
    # SANS CETTE VÉRIFICATION, une sous-catégorie orpheline resterait dans la
    # table sans jamais s'afficher : elle compterait dans les 72 et ne
    # servirait de pièce à personne.
    for cat, liste in SOUS_PAR_CATEGORIE.items():
        if cat not in CATEGORIES_PAR_CLE:
            fautes.append("les sous-catégories de « %s » ne se rattachent à "
                          "aucune catégorie déclarée" % cat)
    orphelines = [c["cle"] for c in CATEGORIES
                  if not SOUS_PAR_CATEGORIE.get(c["cle"])]
    if orphelines:
        fautes.append("catégorie(s) sans aucune sous-catégorie : %s"
                      % ", ".join(orphelines))

    # ── UN SEUL SOCLE, ET C'EST GOVERN ──────────────────────────────────
    socles = [f["cle"] for f in FONCTIONS if f.get("socle")]
    if socles != ["GOVERN"]:
        fautes.append("le socle déclaré n'est pas GOVERN seul : %s" % socles)

    # ── LE CADRE NE SE CERTIFIE PAS, ET ÇA NE SE PERD PAS EN CHEMIN ─────
    if any(s.get("certifiable") for s in SOURCES):
        fautes.append("une source est déclarée certifiable : ni AI 100-1 ni "
                      "AI 600-1 ne le sont")

    if fautes:
        raise RuntimeError("nist_ai_rmf — table incohérente : "
                           + " ; ".join(fautes))
    return []


_FAUTES = _verifier()
