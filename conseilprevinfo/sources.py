"""LE REGISTRE DES SOURCES — ce dont ce site a le droit de parler.

POURQUOI CE FICHIER EXISTE, ET POURQUOI IL EST LE PREMIER. Un site de veille
se juge sur une seule chose : peut-on remonter à l'origine de ce qu'il
affiche. Tout le reste — la mise en page, les filtres, la fraîcheur — ne vaut
rien si le lecteur ne peut pas vérifier. Ce module tient donc la liste des
sources ADMISES, et le moteur refuse de servir une fiche qui n'en cite aucune.

CE QU'IL N'EST PAS. Ce n'est pas une bibliographie décorative. Chaque entrée
porte son ACCÈS RÉEL — l'adresse exacte d'où la donnée se télécharge, sa
licence, sa cadence de mise à jour et ce qu'elle couvre. Une source qu'on ne
sait pas atteindre n'est pas une source : c'est une intention.

L'ÉTAT `atteignable` EST MESURÉ, PAS DÉCLARÉ. Il est renseigné par
`sonder()`, qui va réellement chercher l'adresse. Écrit à la main, il
deviendrait faux le jour où un éditeur déplace un fichier — et personne ne le
verrait, parce qu'une liste de sources a l'air vraie tant qu'on ne la teste
pas.

UNE RÉSERVE HONNÊTE SUR L'ENVIRONNEMENT DE DÉVELOPPEMENT. La machine qui a
servi à écrire ce module n'a pas d'accès sortant libre : les API publiques
(data.europa.eu, data.gouv.fr, Ember, AIE) y sont refusées par la politique
réseau. Les sources ci-dessous marquées `verifie_le` ONT été atteintes et
lues depuis cet environnement ; les autres sont déclarées `a_sonder` et le
resteront jusqu'à ce qu'une exécution en production les confronte. Aucune
n'est présumée bonne.
"""
import json
import os
import ssl
import urllib.error
import urllib.request
from datetime import date, datetime, timezone

VERSION = "2026.08.22"

# ── Ce qu'une source PEUT être ────────────────────────────────────────────
# La nature commande la façon dont une fiche qui s'y appuie sera lue. Un
# catalogue d'autorité et un billet d'éditeur ne se citent pas de la même
# manière, et les confondre est la faute qui coûte le plus cher à un site de
# veille : elle ne se voit pas, et elle décrédibilise tout le reste d'un coup.
NATURES = {
    "autorite_publique": {
        "nom": "Autorité publique",
        "poids": "Fait autorité dans son périmètre. Une entrée à ce catalogue "
                 "engage l'organisme qui le publie et se cite telle quelle.",
        "rang": 1,
    },
    "referentiel_communautaire": {
        "nom": "Référentiel communautaire",
        "poids": "Base tenue par une communauté ouverte, versionnée et "
                 "révisable. Solide et traçable, mais ce n'est pas un acte "
                 "officiel : la version employée se cite avec la donnée.",
        "rang": 2,
    },
    "donnee_ouverte_scientifique": {
        "nom": "Donnée ouverte scientifique",
        "poids": "Série publiée par un organisme de recherche, avec sa "
                 "méthode. Les séries sont comparables entre pays, mais leur "
                 "millésime et leur périmètre décident du résultat.",
        "rang": 2,
    },
    "norme": {
        "nom": "Norme",
        "poids": "Texte normatif. Souvent payant : ce site en cite la "
                 "RÉFÉRENCE et la portée, jamais le contenu reproduit.",
        "rang": 1,
    },
    "reglementation": {
        "nom": "Réglementation",
        "poids": "Texte contraignant, avec sa date d'application. Ce qui "
                 "oblige et ce qui n'oblige pas ne se confondent pas.",
        "rang": 1,
    },
    "publication_editeur": {
        "nom": "Publication d'éditeur",
        "poids": "Utile pour l'état de l'art, mais l'intérêt de son auteur "
                 "n'est pas neutre. Ne fonde jamais un chiffre à elle seule.",
        "rang": 4,
    },
}

ORDRE_NATURES = ["autorite_publique", "reglementation", "norme",
                 "referentiel_communautaire", "donnee_ouverte_scientifique",
                 "publication_editeur"]

# ── Les sources admises ───────────────────────────────────────────────────
# `verifie_le` : date à laquelle l'adresse a réellement répondu depuis cet
# environnement, avec ce qui en a été lu. C'est le seul champ qui autorise à
# écrire « source vérifiée » sur une fiche.
SOURCES = {
    "cisa_kev": {
        "nom": "CISA — Known Exploited Vulnerabilities Catalog",
        "editeur": "Cybersecurity and Infrastructure Security Agency (États-Unis)",
        "nature": "autorite_publique",
        "sujets": ["cyber_industriel"],
        "url_humaine": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        "url_donnee": "https://raw.githubusercontent.com/cisagov/kev-data/develop/"
                      "known_exploited_vulnerabilities.json",
        "format": "json",
        "licence": "Domaine public (œuvre du gouvernement fédéral américain)",
        "licence_en": "Public domain (work of the US federal government)",
        "cadence": "quotidienne",
        "couvre": "Vulnérabilités dont l'exploitation en conditions réelles est "
                  "AVÉRÉE — pas une liste de failles théoriques. Porte l'éditeur, "
                  "le produit, la date d'inscription, l'échéance de remédiation "
                  "imposée aux agences fédérales, et l'usage connu par rançongiciel.",
        "ne_couvre_pas": "Ni la criticité pour VOTRE installation, ni les "
                         "systèmes industriels non référencés par un éditeur "
                         "américain. Une absence au catalogue ne vaut pas absence "
                         "de risque.",
        "verifie_le": "2026-08-22",
        "verifie_quoi": "Catalogue 2026.08.21, 1 674 vulnérabilités, 190 inscrites "
                        "en 2026.",
    },
    "mitre_attack_ics": {
        "nom": "MITRE ATT&CK for ICS",
        "editeur": "The MITRE Corporation",
        "nature": "referentiel_communautaire",
        "sujets": ["cyber_industriel"],
        "url_humaine": "https://attack.mitre.org/matrices/ics/",
        "url_donnee": "https://raw.githubusercontent.com/mitre-attack/"
                      "attack-stix-data/master/ics-attack/ics-attack.json",
        "format": "stix",
        "licence": "MITRE ATT&CK Terms of Use — réutilisation libre avec citation",
        "licence_en": "MITRE ATT&CK Terms of Use — free reuse with attribution",
        "cadence": "quelques versions par an",
        "couvre": "Les techniques d'attaque OBSERVÉES sur systèmes industriels, "
                  "les groupes d'attaquants qui les emploient, les logiciels "
                  "malveillants documentés et les types d'actifs visés.",
        "ne_couvre_pas": "Ce n'est ni une liste de vulnérabilités, ni une mesure "
                         "de probabilité. Une technique décrite n'est pas une "
                         "technique employée contre vous.",
        "verifie_le": "2026-08-22",
        "verifie_quoi": "ICS ATT&CK v19.2 — 97 techniques actives, 14 groupes "
                        "(dont Sandworm Team, Dragonfly, TEMP.Veles), 30 "
                        "logiciels (dont Stuxnet, Industroyer, EKANS), 18 types "
                        "d'actifs.",
    },
    "cve_list": {
        "nom": "CVE Program — liste officielle (cvelistV5)",
        "editeur": "CVE Program / MITRE",
        "nature": "autorite_publique",
        "sujets": ["cyber_industriel", "ia"],
        "url_humaine": "https://www.cve.org/",
        "url_donnee": "https://raw.githubusercontent.com/CVEProject/cvelistV5/"
                      "main/cves/delta.json",
        "format": "json",
        "licence": "CVE Program Terms of Use — redistribution libre",
        "licence_en": "CVE Program Terms of Use — free redistribution",
        "cadence": "continue",
        "couvre": "L'enregistrement officiel des vulnérabilités publiées, avec "
                  "leur descriptif et l'autorité qui les a attribuées.",
        "ne_couvre_pas": "Ni l'exploitation réelle — c'est le rôle du catalogue "
                         "KEV — ni la présence de la faille chez vous.",
        "verifie_le": "2026-08-22",
        "verifie_quoi": "Fichier delta accessible ; sert au suivi incrémental.",
    },
    "owid_energie": {
        "nom": "Our World in Data — Energy Data",
        "editeur": "Global Change Data Lab / University of Oxford",
        "nature": "donnee_ouverte_scientifique",
        "sujets": ["datacenter"],
        "url_humaine": "https://ourworldindata.org/energy",
        "url_donnee": "https://raw.githubusercontent.com/owid/energy-data/"
                      "master/owid-energy-data.csv",
        "format": "csv",
        "licence": "CC BY 4.0",
        "licence_en": "CC BY 4.0",
        "cadence": "annuelle, avec révisions",
        "couvre": "Production, consommation et mix électrique par pays et par "
                  "année — le substrat de tout calcul d'intensité carbone et "
                  "d'implantation.",
        "ne_couvre_pas": "Aucune donnée propre aux centres de données. Le passage "
                         "du mix national à l'empreinte d'un site demande des "
                         "hypothèses qui doivent être écrites.",
        "verifie_le": "2026-08-22",
        "verifie_quoi": "CSV de 9,2 Mo servi intégralement.",
    },
    "owid_co2": {
        "nom": "Our World in Data — CO₂ and Greenhouse Gas Emissions",
        "editeur": "Global Change Data Lab / University of Oxford",
        "nature": "donnee_ouverte_scientifique",
        "sujets": ["datacenter"],
        "url_humaine": "https://ourworldindata.org/co2-emissions",
        "url_donnee": "https://raw.githubusercontent.com/owid/co2-data/"
                      "master/owid-co2-data.csv",
        "format": "csv",
        "licence": "CC BY 4.0",
        "licence_en": "CC BY 4.0",
        "cadence": "annuelle",
        "couvre": "Émissions par pays, par secteur et par habitant, sur série "
                  "longue.",
        "ne_couvre_pas": "L'intensité carbone HORAIRE d'un réseau, qui décide "
                         "pourtant du placement d'une charge de calcul.",
        "verifie_le": "2026-08-22",
        "verifie_quoi": "CSV de 14,4 Mo servi intégralement.",
    },
    "electricity_maps": {
        "nom": "Electricity Maps — configuration des zones",
        "editeur": "Electricity Maps (contributions ouvertes)",
        "nature": "referentiel_communautaire",
        "sujets": ["datacenter"],
        "url_humaine": "https://github.com/electricitymaps/electricitymaps-contrib",
        "url_donnee": "https://raw.githubusercontent.com/electricitymaps/"
                      "electricitymaps-contrib/master/config/zones/FR.yaml",
        "format": "yaml",
        "licence": "Dépôt sous licence libre ; les données temps réel, elles, "
                   "relèvent d'un service commercial",
        "licence_en": "Repository under an open licence; the real-time data, however, falls under a commercial service",
        "cadence": "continue",
        "couvre": "Le paramétrage par zone électrique : facteurs d'émission "
                  "retenus, capacités, sources déclarées.",
        "ne_couvre_pas": "Les séries temps réel ne sont PAS dans ce dépôt libre. "
                         "Les annoncer comme gratuites serait faux.",
        "verifie_le": "2026-08-22",
        "verifie_quoi": "Fichier de zone FR lu (29 ko).",
    },
    "mitre_atlas": {
        "nom": "MITRE ATLAS — Adversarial Threat Landscape for AI Systems",
        "editeur": "The MITRE Corporation",
        "nature": "referentiel_communautaire",
        "sujets": ["ia", "sia", "cyber_industriel"],
        "url_humaine": "https://atlas.mitre.org/",
        "url_donnee": "https://raw.githubusercontent.com/mitre-atlas/atlas-data/"
                      "main/dist/ATLAS.yaml",
        "format": "yaml",
        "licence": "MITRE ATLAS Terms of Use — réutilisation libre avec citation",
        "licence_en": "MITRE ATLAS Terms of Use — free reuse with attribution",
        "cadence": "quelques versions par an",
        "couvre": "Les attaques OBSERVÉES contre des systèmes d'intelligence "
                  "artificielle en production : études de cas datées avec leur "
                  "cible et le déroulé, techniques d'attaque, tactiques et "
                  "mesures d'atténuation. C'est l'équivalent d'ATT&CK pour "
                  "l'IA, et la seule base publique qui documente des "
                  "incidents réels plutôt que des scénarios de laboratoire.",
        "ne_couvre_pas": "Ni la fréquence de ces attaques, ni leur coût, ni "
                         "aucune obligation réglementaire. Une technique "
                         "documentée n'est pas une technique employée contre "
                         "vous, et l'absence d'un cas ne vaut pas absence "
                         "d'incident — seulement absence d'incident PUBLIÉ.",
        "verifie_le": "2026-08-22",
        "verifie_quoi": "ATLAS v5.6.0 — 57 études de cas datées, 170 "
                        "techniques, 16 tactiques, 35 atténuations.",
    },
    # ── AJOUTÉE APRÈS MESURE ──────────────────────────────────────────────
    # La rubrique IA ne portait que huit fiches, toutes issues d'ATLAS,
    # c'est-à-dire toutes de la même nature : des INCIDENTS OBSERVÉS. Une
    # veille qui ne connaît d'un domaine que ses incidents n'en donne qu'une
    # face — celle qui s'est déjà produite. OWASP apporte l'autre : le
    # CONSENSUS d'une communauté de praticiens sur ce qui menace un système à
    # base de modèle de langage, indépendamment de ce qui a été observé.
    #
    # Deux natures différentes sur le même terrain : c'est ce qui permet à un
    # lecteur de distinguer « c'est arrivé » de « c'est reconnu comme un
    # risque », deux énoncés qu'un agrégateur confondrait.
    "owasp_llm": {
        "nom": "OWASP Top 10 pour les applications à modèle de langage (2025)",
        "editeur": "OWASP Foundation",
        "nature": "referentiel_communautaire",
        "sujets": ["ia", "sia"],
        "url_humaine": "https://genai.owasp.org/llm-top-10/",
        "url_donnee": ("https://raw.githubusercontent.com/OWASP/"
                       "www-project-top-10-for-large-language-model-"
                       "applications/main/2_0_vulns/LLM01_PromptInjection.md"),
        "format": "markdown",
        "licence": "Creative Commons BY-SA 4.0 — réutilisation libre avec "
                   "citation et partage à l'identique",
        "licence_en": "Creative Commons BY-SA 4.0 — free reuse with attribution and share-alike",
        "cadence": "une édition majeure environ tous les dix-huit mois",
        "couvre": "Les dix familles de risques que la communauté OWASP retient "
                  "pour une application bâtie sur un modèle de langage : "
                  "injection d'invite, fuite d'information sensible, chaîne "
                  "d'approvisionnement, empoisonnement des données et du "
                  "modèle, traitement fautif des sorties, agentivité "
                  "excessive, fuite d'invite système, faiblesses des index "
                  "vectoriels, désinformation, consommation non bornée. "
                  "Chaque entrée porte sa description, des exemples de "
                  "risques, des mesures de prévention et des scénarios "
                  "d'attaque, avec ses références.",
        "ne_couvre_pas": "Ni la fréquence de ces risques, ni leur coût, ni "
                         "aucune obligation réglementaire — c'est un consensus "
                         "de praticiens, pas une norme opposable. La liste ne "
                         "dit pas non plus si un risque s'est RÉALISÉ : elle "
                         "recense ce qui est reconnu comme menaçant, quand "
                         "ATLAS recense ce qui a été observé. Confondre les "
                         "deux ferait passer un risque théorique pour un "
                         "incident.",
        "verifie_le": "2026-08-22",
        "verifie_quoi": "Les dix entrées de l'édition 2025 ont été atteintes "
                        "et lues une à une depuis cet environnement.",
    },
    "helm_stanford": {
        "nom": "Stanford CRFM — HELM",
        "editeur": "Center for Research on Foundation Models, Stanford",
        "nature": "donnee_ouverte_scientifique",
        "sujets": ["ia", "sia"],
        "url_humaine": "https://crfm.stanford.edu/helm/",
        "url_donnee": "https://raw.githubusercontent.com/stanford-crfm/helm/"
                      "main/README.md",
        "format": "texte",
        "licence": "Apache 2.0 (code) ; résultats publiés",
        "licence_en": "Apache 2.0 (code); published results",
        "cadence": "continue",
        "couvre": "L'évaluation reproductible de modèles de fondation sur des "
                  "tâches déclarées, avec le protocole.",
        "ne_couvre_pas": "Aucune mesure de conformité réglementaire. Un bon score "
                         "d'évaluation ne dit RIEN de la conformité AI Act d'un "
                         "système qui l'emploie.",
        "verifie_le": "2026-08-22",
        "verifie_quoi": "Dépôt accessible.",
    },
    "mlcommons": {
        "nom": "MLCommons — MLPerf Inference",
        "editeur": "MLCommons",
        "nature": "referentiel_communautaire",
        "sujets": ["ia", "datacenter"],
        "url_humaine": "https://mlcommons.org/benchmarks/",
        "url_donnee": "https://raw.githubusercontent.com/mlcommons/inference/"
                      "master/README.md",
        "format": "texte",
        "licence": "Apache 2.0",
        "licence_en": "Apache 2.0",
        "cadence": "deux campagnes par an",
        "couvre": "Les performances d'inférence mesurées selon un protocole "
                  "commun — le seul terrain où des matériels se comparent sans "
                  "que chacun choisisse son épreuve.",
        "ne_couvre_pas": "La consommation en exploitation réelle. Une mesure de "
                         "banc n'est pas une charge de production.",
        "verifie_le": "2026-08-22",
        "verifie_quoi": "Dépôt accessible.",
    },
}

# ── Sources visées mais NON atteintes depuis l'environnement de conception ──
# Elles sont écrites ici plutôt que tues : le jour où le réseau s'ouvre, la
# liste de ce qu'il reste à brancher est déjà faite. Aucune ne doit être
# citée par une fiche tant que `sonder()` ne l'a pas confirmée.
#: LES DEUX NATURES D'OBSTACLE — et pourquoi les distinguer.
#:
#: Elles se lisaient pareil, et ce n'est pas pareil du tout. « Refusé par la
#: politique réseau de l'environnement de conception » veut dire : cela
#: marchera en production, il suffit de déployer. « Licence commerciale
#: requise » veut dire : cela ne marchera JAMAIS sans contrat, quel que soit
#: l'hébergement, et aucune quantité de code n'y changera rien. Un lecteur —
#: ou le cabinet lui-même dans six mois — doit pouvoir trier d'un coup d'œil
#: ce qui est un chantier de ce qui est une dépense.
NATURES_OBSTACLE = {
    "environnement": {
        "nom": "Bloqué ici, pas ailleurs",
        "nom_en": "Blocked here, not elsewhere",
        "dit": "La politique réseau de l'environnement de conception refuse "
               "cet hôte. Rien à décider : la source se branche au "
               "déploiement, et le bouton « Sonder » du registre le confirme "
               "en un clic.",
        "dit_en": "The design environment's network policy refuses this host. "
                  "Nothing to decide: the source connects on deployment, and "
                  "the register's “Probe” button confirms it in one click."},
    "licence": {
        "nom": "Contrat commercial requis",
        "nom_en": "Commercial contract required",
        "dit": "Le contenu existe et se lit, mais sa redistribution demande "
               "une licence payante. Ce site cite la licence de chaque source "
               "sous chaque fiche : publier sans licence reviendrait à écrire "
               "une mention fausse à l'endroit précis où il promet de dire "
               "vrai. C'est une décision du cabinet, pas un travail de "
               "développement.",
        "dit_en": "The content exists and can be read, but redistributing it "
                  "requires a paid licence. This site cites each source's "
                  "licence under every entry: publishing without one would "
                  "mean writing a false notice at the exact place where it "
                  "promises to tell the truth. That is a decision for the "
                  "firm, not a development task."},
    "format": {
        "nom": "Rien de lisible par machine",
        "nom_en": "Nothing machine-readable",
        "dit": "La source ne publie ni flux, ni interface, ni fichier stable. "
               "La lire supposerait de découper des pages HTML, ce qui casse "
               "à la première refonte et sans prévenir.",
        "dit_en": "The source publishes no feed, no interface and no stable "
                  "file. Reading it would mean scraping HTML pages, which "
                  "breaks at the first redesign and without warning."},
}
ORDRE_OBSTACLES = ["environnement", "licence", "format"]

A_BRANCHER = [
    # ── CE QUI TIENT À UNE LICENCE, ET NON À DU CODE ──────────────────────
    # Le cabinet a demandé de brancher les dépêches AFP et Reuters. Les deux
    # sont ici, avec ce qu'il faudrait — et ce n'est pas du développement.
    {"cle": "afp", "nom": "AFP — dépêches",
     "nature_obstacle": "licence",
     "pourquoi": "L'agence couvre les quatre thèmes de ce site, et elle date "
                 "ses dépêches à la minute — ce qu'aucune source publique ne "
                 "fait sur la cyber industrielle.",
     "obstacle": "AFP ne publie aucun flux libre. L'accès passe par AFP Forum "
                 "ou l'API AFP, sous contrat commercial, avec un régime de "
                 "citation et une durée de conservation contractuels. Sans ce "
                 "contrat, republier une dépêche est une contrefaçon — et "
                 "afficher « licence : libre » sous la fiche serait un "
                 "mensonge à l'endroit exact où ce site promet de dire vrai.",
     "ce_qu_il_faudrait": "Un contrat AFP, une clé d'API, et la mention "
                          "contractuelle portée par chaque fiche. Le "
                          "collecteur, lui, est du travail ordinaire."},
    {"cle": "reuters", "nom": "Reuters — dépêches",
     "nature_obstacle": "licence",
     "pourquoi": "Même couverture, et une antériorité utile sur les "
                 "incidents industriels signalés hors d'Europe.",
     "obstacle": "Reuters a retiré ses flux RSS publics ; il ne reste que "
                 "Reuters Connect, sous contrat. La page « rssfeed » citée "
                 "un peu partout ne répond plus. Comme pour l'AFP, republier "
                 "sans licence reviendrait à écrire une mention fausse.",
     "ce_qu_il_faudrait": "Un contrat Reuters Connect et ses identifiants. "
                          "Aucune quantité de code n'y supplée."},

    # ── CE QUI TIENT À CET ENVIRONNEMENT, ET SE BRANCHE AU DÉPLOIEMENT ────
    {"cle": "data_europa", "nom": "data.europa.eu — portail européen",
     "nature_obstacle": "environnement",
     "pourquoi": "Le point d'entrée des jeux publics de l'Union.",
     "obstacle": "Refusé (403) par la politique réseau de l'environnement de "
                 "conception. À rebrancher en production."},
    {"cle": "data_gouv_fr", "nature_obstacle": "environnement", "nom": "data.gouv.fr",
     "pourquoi": "Jeux publics français, dont l'énergie et les réseaux.",
     "obstacle": "Refusé (403) dans cet environnement."},
    {"cle": "ember", "nature_obstacle": "environnement", "nom": "Ember — Electricity Data",
     "pourquoi": "Intensité carbone de l'électricité, séries mensuelles.",
     "obstacle": "API refusée (403) dans cet environnement."},
    {"cle": "enisa", "nature_obstacle": "environnement", "nom": "ENISA — Threat Landscape",
     "pourquoi": "Panorama européen des menaces, annuel.",
     "obstacle": "Non sondé : lecture de page bloquée dans cet environnement."},
    {"cle": "cert_fr", "nature_obstacle": "environnement", "nom": "CERT-FR (ANSSI) — avis et alertes",
     "pourquoi": "Les avis qui engagent l'autorité française.",
     "obstacle": "Non sondé : lecture de page bloquée dans cet environnement."},
    {"cle": "eur_lex", "nature_obstacle": "environnement", "nom": "EUR-Lex",
     "pourquoi": "Le texte faisant foi des règlements cités (AI Act, NIS2, EED).",
     "obstacle": "Non sondé : lecture de page bloquée dans cet environnement."},
]


def _f(x):
    return round(float(x), 3)


def natures():
    return [dict(NATURES[c], cle=c) for c in ORDRE_NATURES]


# ── ADMISE N'EST PAS LUE ───────────────────────────────────────────────────
# DÉFAUT CORRIGÉ. Le registre annonçait neuf sources — chacune avec son bouton
# « Sonder » prouvant qu'elle répond — alors que quatre seulement nourrissaient
# le corpus. Un lecteur en concluait que le site s'appuie sur neuf sources.
# L'écart ne se voyait de nulle part : ni le registre ni les fiches ne
# distinguaient « admise » de « lue ».
#
# Chaque source non lue porte donc SA RAISON. Une liste d'admises sans motif
# finit par accueillir n'importe quoi : c'est le motif écrit qui rend une
# admission coûteuse, donc réfléchie.
POURQUOI_PAS_LUE = {
    "cve_list": "Son adresse de données est `delta.json`, un flux des "
                "CHANGEMENTS des dernières minutes — deux entrées à l'instant "
                "de l'écriture. Ce n'est pas un catalogue : deux collectes "
                "successives rendraient deux corpus sans rapport, et aucune "
                "ne serait reproductible. La source reste admise parce qu'une "
                "fiche PEUT la citer ; elle n'alimente pas la collecte.",
    "owid_co2": "Elle porte les émissions de l'économie entière, par pays et "
                "par secteur. La rubrique « centres de données » de ce site "
                "raisonne sur le MIX ÉLECTRIQUE, que `owid_energie` sert déjà : "
                "verser des totaux nationaux ajouterait du contexte sans "
                "changer un arbitrage d'implantation. Admise pour un usage à "
                "venir, pas lue aujourd'hui.",
    "helm_stanford": "Son adresse publique est un README : elle documente un "
                     "PROTOCOLE d'évaluation, elle ne publie pas de résultats "
                     "structurés à cette adresse. En tirer des fiches "
                     "reviendrait à paraphraser une page de présentation. "
                     "Admise comme référence de méthode, pas comme flux.",
    "mlcommons": "Même situation : le README décrit la suite MLPerf et son "
                 "protocole, sans servir les résultats. Une fiche « MLPerf "
                 "existe » n'apprendrait rien à personne.",
}


def _lues():
    """Les clés que les collecteurs lisent réellement.

    L'import est TARDIF et protégé : `sources` ne doit pas dépendre
    d'`ingestion`, qui dépend de lui. Si la lecture échoue, on ne prétend rien
    — `collectee` vaut None, et l'écran dit « indéterminé » plutôt que de
    trancher au hasard.
    """
    try:
        import ingestion
        return ingestion.sources_collectees()
    except Exception:  # noqa: BLE001
        return None


def registre(sujet=None):
    """Les sources admises, éventuellement restreintes à un sujet.

    Chaque entrée dit si elle est LUE par un collecteur — dérivé de la table
    des collecteurs, jamais recopié — et, sinon, pourquoi.
    """
    lues = _lues()
    out = []
    for cle, s in SOURCES.items():
        if sujet and sujet not in s["sujets"]:
            continue
        out.append(dict(s, cle=cle, nature_nom=NATURES[s["nature"]]["nom"],
                        nature_poids=NATURES[s["nature"]]["poids"],
                        collectee=(None if lues is None else cle in lues),
                        pourquoi_pas_lue=POURQUOI_PAS_LUE.get(cle, "")))
    out.sort(key=lambda s: (ORDRE_NATURES.index(s["nature"]), s["nom"]))
    return out


def sonder(cle, delai=25):
    """Va RÉELLEMENT chercher l'adresse et rend ce qu'elle a répondu.

    C'est ce qui distingue un registre d'une bibliographie : l'état
    d'atteignabilité est mesuré au moment où on le demande, jamais recopié.
    Un échec n'est pas une erreur du programme — c'est une information sur
    la source, et elle est rendue telle quelle.
    """
    s = SOURCES.get(cle)
    if not s:
        return {"ok": False, "erreur": "source_inconnue",
                "message": "Source inconnue : %r." % cle}
    debut = datetime.now(timezone.utc)
    req = urllib.request.Request(
        s["url_donnee"],
        headers={"User-Agent": "conseilprevinfo/%s (veille sourcée)" % VERSION})
    try:
        with urllib.request.urlopen(req, timeout=delai) as r:
            octets = 0
            # On ne charge pas tout en mémoire : on veut savoir que ça répond
            # et que ça sert du volume, pas rapatrier neuf mégaoctets.
            for _ in range(64):
                bloc = r.read(65536)
                if not bloc:
                    break
                octets += len(bloc)
            return {
                "ok": True, "cle": cle, "code": r.status,
                "octets_lus": octets,
                "ms": int((datetime.now(timezone.utc) - debut).total_seconds() * 1000),
                "quand": debut.isoformat(timespec="seconds"),
            }
    except urllib.error.HTTPError as e:
        return {"ok": False, "cle": cle, "code": e.code, "erreur": "http",
                "message": "L'éditeur a répondu %s." % e.code}
    except (urllib.error.URLError, ssl.SSLError, TimeoutError, OSError) as e:
        return {"ok": False, "cle": cle, "erreur": "injoignable",
                "message": "Adresse injoignable depuis cet environnement : %s. "
                           "Ce n'est pas une panne du site — c'est l'état du "
                           "réseau, et il se dit." % e}


def sante():
    verifiees = [c for c, s in SOURCES.items() if s.get("verifie_le")]
    return {
        "module": "sources", "version": VERSION,
        "sources": len(SOURCES),
        "verifiees": len(verifiees),
        "a_brancher": len(A_BRANCHER),
        # LE DÉTAIL COMPTE PLUS QUE LE TOTAL : « huit sources à brancher » ne
        # dit pas si c'est un après-midi de travail ou deux contrats à signer.
        "a_brancher_par_obstacle": {
            n: sum(1 for x in A_BRANCHER if x.get("nature_obstacle") == n)
            for n in ORDRE_OBSTACLES},
        "par_nature": {n: sum(1 for s in SOURCES.values() if s["nature"] == n)
                       for n in ORDRE_NATURES},
        "par_sujet": {s: sum(1 for x in SOURCES.values() if s in x["sujets"])
                      for s in sorted({s for x in SOURCES.values()
                                       for s in x["sujets"]})},
        "portee": "Registre des sources admises. Une fiche qui n'en cite "
                  "aucune n'est pas publiable — le moteur la refuse.",
    }


def obstacles():
    """Les natures d'obstacle, servies comme le reste du vocabulaire."""
    return [dict(NATURES_OBSTACLE[c], cle=c) for c in ORDRE_OBSTACLES]


def _verifier():
    """Le contrôle au chargement.

    Mieux vaut un service qui ne démarre pas qu'un registre qui promet une
    source sans dire où la prendre : la fiche qui s'y appuie deviendrait
    invérifiable sans que rien ne le signale.
    """
    for cle, s in SOURCES.items():
        for champ in ("nom", "editeur", "nature", "url_humaine", "url_donnee",
                      "licence", "couvre", "ne_couvre_pas", "cadence"):
            if not str(s.get(champ, "")).strip():
                raise RuntimeError("sources : %s sans %s" % (cle, champ))
        if s["nature"] not in NATURES:
            raise RuntimeError("sources : nature inconnue sur %s : %r"
                               % (cle, s["nature"]))
        if not s["sujets"]:
            raise RuntimeError("sources : %s ne couvre aucun sujet" % cle)
        for u in (s["url_humaine"], s["url_donnee"]):
            if not u.startswith("https://"):
                raise RuntimeError(
                    "sources : %s porte une adresse non chiffrée : %r" % (cle, u))
        # CE QUE CETTE SOURCE NE COUVRE PAS EST OBLIGATOIRE, et c'est le
        # contrôle qui compte : une source dont on ne dit que les forces
        # finit citée hors de son périmètre.
        if len(s["ne_couvre_pas"]) < 40:
            raise RuntimeError(
                "sources : %s ne dit pas assez ce qu'elle NE couvre PAS — une "
                "source sans limite écrite sera citée hors de son domaine" % cle)
    for x in A_BRANCHER:
        # UNE ENTRÉE SANS NATURE D'OBSTACLE EST LA PORTE OUVERTE au retour de
        # l'indistinction : « bloqué ici » et « contrat requis » se liraient à
        # nouveau pareil, et la liste redeviendrait un fourre-tout.
        if x.get("nature_obstacle") not in NATURES_OBSTACLE:
            raise RuntimeError("sources : %s n'a pas de nature d'obstacle"
                               % x.get("cle"))
        if x["nature_obstacle"] == "licence" and not x.get("ce_qu_il_faudrait"):
            raise RuntimeError("sources : %s est bloquée par une licence sans "
                               "dire ce qu'il faudrait" % x["cle"])

    if set(ORDRE_NATURES) != set(NATURES):
        raise RuntimeError("sources : l'ordre des natures ne les couvre pas")
    rangs = {NATURES[n]["rang"] for n in NATURES}
    if not rangs <= {1, 2, 3, 4}:
        raise RuntimeError("sources : rang de nature hors barème")

    for a in A_BRANCHER:
        for champ in ("cle", "nom", "pourquoi", "obstacle"):
            if not str(a.get(champ, "")).strip():
                raise RuntimeError("sources : source à brancher sans %s" % champ)
        if a["cle"] in SOURCES:
            raise RuntimeError(
                "sources : %s figure à la fois comme admise et à brancher"
                % a["cle"])


_verifier()
