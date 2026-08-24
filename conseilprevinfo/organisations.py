# -*- coding: utf-8 -*-
"""LES ORGANISATIONS QUE LES SOURCES NOMMENT — et rien de plus.

CE QUE CE MODULE FAIT, EN UNE PHRASE : il reconnaît, dans les champs où une
source ÉCRIT le nom d'une entité, les organisations d'un répertoire tenu à la
main — et il n'en reconnaît aucune ailleurs.

════════════════════════════════════════════════════════════════════════════
POURQUOI UN RÉPERTOIRE ÉCRIT À LA MAIN, ET PAS UNE EXTRACTION
════════════════════════════════════════════════════════════════════════════
La tentation est de lire le champ `target` d'ATLAS et d'en tirer l'entreprise.
Mesuré sur les cinquante-sept études de cas, ce champ contient :

    « OpenAI ChatGPT »                      → une entreprise et son produit
    « Microsoft 365 Copilot »               → une entreprise et son produit
    « Cloud-Based LLM Services »            → AUCUNE entreprise
    « 10 web-scale datasets »               → aucune entreprise
    « Ukraine's security and defense sector » → un secteur d'un État
    « California Employment Development Department » → une administration

Une extraction automatique produirait donc des « entreprises » nommées
« Cloud-Based LLM Services » et « Multiple systems ». Ce serait une invention,
c'est-à-dire précisément ce que ce site refuse. Le répertoire ci-dessous est
un JUGEMENT DE CE CABINET, écrit, versionné, et relisible ligne à ligne — au
même titre que `EDITEURS_INDUSTRIELS` dans `ingestion.py`, qui porte la même
mention depuis l'origine.

CE QUI NE FIGURE PAS AU RÉPERTOIRE N'EST PAS RATTACHÉ. « Ukraine's security
and defense sector » ne donne aucune organisation, et c'est le bon résultat :
un axe qui ne trouve rien doit le dire, pas combler.

════════════════════════════════════════════════════════════════════════════
OÙ LE NOM EST CHERCHÉ — ET OÙ IL NE L'EST JAMAIS
════════════════════════════════════════════════════════════════════════════
Uniquement dans les champs où la SOURCE désigne une entité :

    ATLAS      → `target`                       (la cible de l'incident)
    CISA KEV   → `vendorProject`, `product`     (l'éditeur et son produit)

JAMAIS dans la lecture critique, la portée, l'incertitude ni le chapeau. Ces
textes sont de ce site : y chercher un nom d'entreprise reviendrait à
rattacher une fiche à Microsoft parce que NOUS avons écrit « Microsoft » dans
une phrase d'analyse. Le filtre annoncerait alors « les fiches qui concernent
Microsoft » en servant « les fiches où nous avons tapé Microsoft ».

════════════════════════════════════════════════════════════════════════════
LA CORRESPONDANCE SE FAIT SUR DES MOTS ENTIERS, ET LA PLUS LONGUE GAGNE
════════════════════════════════════════════════════════════════════════════
Deux défauts que ces deux règles empêchent, et qui sont tous deux arrivés
ailleurs dans ce code :

  · MOTS ENTIERS. `ingestion.py` porte déjà la cicatrice : « Intel Ethernet
    DIAGNOSTICS Driver » ressortait industriel parce que « diagnostics »
    contient « ics ». Une sous-chaîne nue rattacherait « Delta Electronics »
    à toute fiche portant le mot « delta ».
  · LA PLUS LONGUE GAGNE, et elle CONSOMME le passage. Sans cela,
    « Rockwell Automation » rattacherait à la fois Rockwell et — si un jour
    une entrée « Automation » existait — cette entrée-là. Surtout,
    « Hitachi Energy » (siège en Suisse) serait compté comme Hitachi (siège
    au Japon) : le filtre par pays dirait alors le Japon d'un fait suisse.

════════════════════════════════════════════════════════════════════════════
LE PAYS DU SIÈGE EST UN APPORT DE CE CABINET, ET IL EST MARQUÉ COMME TEL
════════════════════════════════════════════════════════════════════════════
AUCUNE des sources lues ne porte le siège d'une entreprise. Le pays écrit ici
ne dérive donc de rien : il est renseigné à la main, et l'écran le dit là où
il sert — le menu porte sa mention, l'interface la répète.

IL N'EST PAS LE PAYS DE LA FICHE, et les deux ne doivent jamais se confondre.
Le champ `pays` d'une fiche dit où le FAIT se situe (une zone électrique, un
réseau national) ; le siège dit d'où vient l'ENTREPRISE NOMMÉE. Un incident
ATLAS contre un produit Microsoft n'est pas un fait américain. Les deux axes
sont donc servis séparément, sous deux intitulés distincts, dans le même menu
déroulant mais dans deux groupes nommés.

QUAND LE SIÈGE EST DISPUTÉ, IL EST LAISSÉ VIDE. VirusTotal est né à Málaga et
appartient à Google ; Johnson Controls a son siège social en Irlande et sa
direction à Milwaukee. Écrire un pays dans ces cas-là serait trancher une
question dont ce site n'a pas à connaître. L'entrée existe, elle est
filtrable par son nom, et elle ne pèse dans aucun compte par pays.
"""

import re

LANGUES = ("fr", "en")

#: Ce que le pays du siège EST, et ce qu'il n'est pas. Servi avec la facette.
ORIGINE_DU_SIEGE = (
    "Le pays du siège est renseigné à la main par ce cabinet : aucune des "
    "sources lues ne le porte. Il dit d'où vient l'entreprise nommée, jamais "
    "où se situe le fait.",
    "The head-office country is entered by hand by this firm: none of the "
    "sources read carries it. It says where the named company comes from, "
    "never where the fact takes place.",
)

#: Ce qu'une organisation EST — la nature n'est pas une décoration : une
#: administration et une fondation ne se lisent pas comme une entreprise.
NATURES = {
    "entreprise":     ("Entreprise", "Company"),
    "fondation":      ("Fondation", "Foundation"),
    "administration": ("Administration", "Public body"),
}

#: LE RÉPERTOIRE. `cle` est l'identifiant stable ; `appellations` est la liste
#: des formes SOUS LESQUELLES LES SOURCES ÉCRIVENT ce nom — pas des synonymes
#: choisis par nous, mais ce qui a été lu dans leurs champs. `pays` est le
#: siège, ou `None` quand il est disputé, avec le motif écrit.
ORGANISATIONS = (
    # ── Éditeurs de systèmes industriels, tels que CISA KEV les nomme ──────
    {"cle": "siemens", "nom": "Siemens", "pays": "DE", "nature": "entreprise",
     "appellations": ("siemens",)},
    {"cle": "schneider", "nom": "Schneider Electric", "pays": "FR",
     "nature": "entreprise", "appellations": ("schneider electric", "schneider")},
    {"cle": "rockwell", "nom": "Rockwell Automation", "pays": "US",
     "nature": "entreprise", "appellations": ("rockwell automation", "rockwell")},
    {"cle": "abb", "nom": "ABB", "pays": "CH", "nature": "entreprise",
     "appellations": ("abb",)},
    {"cle": "honeywell", "nom": "Honeywell", "pays": "US",
     "nature": "entreprise", "appellations": ("honeywell",)},
    {"cle": "emerson", "nom": "Emerson Electric", "pays": "US",
     "nature": "entreprise", "appellations": ("emerson",)},
    {"cle": "yokogawa", "nom": "Yokogawa Electric", "pays": "JP",
     "nature": "entreprise", "appellations": ("yokogawa",)},
    {"cle": "mitsubishi", "nom": "Mitsubishi Electric", "pays": "JP",
     "nature": "entreprise", "appellations": ("mitsubishi electric", "mitsubishi")},
    {"cle": "omron", "nom": "Omron", "pays": "JP", "nature": "entreprise",
     "appellations": ("omron",)},
    # LES DEUX HITACHI SONT DEUX ENTRÉES, et c'est le cas d'école de la règle
    # « la plus longue gagne » : Hitachi Energy a son siège à Zurich, Hitachi
    # à Tokyo. Une seule entrée ferait dire au filtre par pays le Japon d'un
    # fait suisse — ou l'inverse.
    {"cle": "hitachi_energy", "nom": "Hitachi Energy", "pays": "CH",
     "nature": "entreprise", "appellations": ("hitachi energy",)},
    {"cle": "hitachi", "nom": "Hitachi", "pays": "JP", "nature": "entreprise",
     "appellations": ("hitachi",)},
    {"cle": "general_electric", "nom": "General Electric", "pays": "US",
     "nature": "entreprise", "appellations": ("general electric",)},
    {"cle": "moxa", "nom": "Moxa", "pays": "TW", "nature": "entreprise",
     "appellations": ("moxa",)},
    {"cle": "advantech", "nom": "Advantech", "pays": "TW",
     "nature": "entreprise", "appellations": ("advantech",)},
    {"cle": "phoenix_contact", "nom": "Phoenix Contact", "pays": "DE",
     "nature": "entreprise", "appellations": ("phoenix contact",)},
    {"cle": "wago", "nom": "WAGO", "pays": "DE", "nature": "entreprise",
     "appellations": ("wago",)},
    {"cle": "beckhoff", "nom": "Beckhoff", "pays": "DE",
     "nature": "entreprise", "appellations": ("beckhoff",)},
    {"cle": "delta", "nom": "Delta Electronics", "pays": "TW",
     "nature": "entreprise", "appellations": ("delta electronics",)},
    {"cle": "unitronics", "nom": "Unitronics", "pays": "IL",
     "nature": "entreprise", "appellations": ("unitronics",)},
    {"cle": "trihedral", "nom": "Trihedral Engineering", "pays": "CA",
     "nature": "entreprise", "appellations": ("trihedral", "vtscada")},
    {"cle": "aveva", "nom": "AVEVA", "pays": "GB", "nature": "entreprise",
     "appellations": ("aveva",)},
    {"cle": "codesys", "nom": "CODESYS", "pays": "DE", "nature": "entreprise",
     "appellations": ("codesys", "3s-smart software solutions")},
    {"cle": "festo", "nom": "Festo", "pays": "DE", "nature": "entreprise",
     "appellations": ("festo",)},
    {"cle": "pilz", "nom": "Pilz", "pays": "DE", "nature": "entreprise",
     "appellations": ("pilz",)},
    {"cle": "sick", "nom": "SICK", "pays": "DE", "nature": "entreprise",
     "appellations": ("sick ag",)},
    {"cle": "wibu", "nom": "WIBU-SYSTEMS", "pays": "DE",
     "nature": "entreprise", "appellations": ("wibu-systems", "wibu")},
    {"cle": "red_lion", "nom": "Red Lion Controls", "pays": "US",
     "nature": "entreprise", "appellations": ("red lion",)},
    {"cle": "opto22", "nom": "Opto 22", "pays": "US", "nature": "entreprise",
     "appellations": ("opto 22",)},
    {"cle": "inductive", "nom": "Inductive Automation", "pays": "US",
     "nature": "entreprise", "appellations": ("inductive automation",)},
    {"cle": "iconics", "nom": "ICONICS", "pays": "US", "nature": "entreprise",
     "appellations": ("iconics",)},
    # SIÈGE DISPUTÉ — société de droit irlandais, direction à Milwaukee.
    {"cle": "johnson_controls", "nom": "Johnson Controls", "pays": None,
     "nature": "entreprise", "appellations": ("johnson controls",),
     "pays_motif": ("Société de droit irlandais dont la direction opère depuis "
                    "les États-Unis : trancher serait un jugement de plus.",
                    "An Irish-registered company run from the United States: "
                    "picking one would be one judgement too many.")},

    # ── Entités nommées par les études de cas MITRE ATLAS ─────────────────
    {"cle": "openai", "nom": "OpenAI", "pays": "US", "nature": "entreprise",
     "appellations": ("openai", "chatgpt")},
    {"cle": "anthropic", "nom": "Anthropic", "pays": "US",
     "nature": "entreprise", "appellations": ("anthropic", "claude")},
    {"cle": "google", "nom": "Google", "pays": "US", "nature": "entreprise",
     "appellations": ("google", "bard", "gemini")},
    {"cle": "microsoft", "nom": "Microsoft", "pays": "US",
     "nature": "entreprise",
     "appellations": ("microsoft", "azure", "bing", "copilot studio")},
    {"cle": "github", "nom": "GitHub", "pays": "US", "nature": "entreprise",
     "appellations": ("github",)},
    {"cle": "hugging_face", "nom": "Hugging Face", "pays": "US",
     "nature": "entreprise", "appellations": ("hugging face", "huggingface")},
    {"cle": "palo_alto", "nom": "Palo Alto Networks", "pays": "US",
     "nature": "entreprise", "appellations": ("palo alto networks",)},
    {"cle": "kaspersky", "nom": "Kaspersky", "pays": "RU",
     "nature": "entreprise", "appellations": ("kaspersky",)},
    {"cle": "proofpoint", "nom": "Proofpoint", "pays": "US",
     "nature": "entreprise", "appellations": ("proofpoint",)},
    {"cle": "clearview", "nom": "Clearview AI", "pays": "US",
     "nature": "entreprise", "appellations": ("clearview ai", "clearview")},
    {"cle": "slack", "nom": "Slack", "pays": "US", "nature": "entreprise",
     "appellations": ("slack",)},
    {"cle": "atlassian", "nom": "Atlassian", "pays": "AU",
     "nature": "entreprise", "appellations": ("atlassian", "jira")},
    {"cle": "amazon", "nom": "Amazon", "pays": "US", "nature": "entreprise",
     "appellations": ("amazon",)},
    {"cle": "anysphere", "nom": "Anysphere (Cursor)", "pays": "US",
     "nature": "entreprise", "appellations": ("cursor",)},
    {"cle": "systran", "nom": "SYSTRAN", "pays": "FR", "nature": "entreprise",
     "appellations": ("systran",)},
    {"cle": "postmark", "nom": "Postmark", "pays": "US",
     "nature": "entreprise", "appellations": ("postmark",)},
    {"cle": "pytorch", "nom": "PyTorch Foundation", "pays": "US",
     "nature": "fondation", "appellations": ("pytorch",)},
    # SIÈGE DISPUTÉ — né à Málaga, filiale de Google depuis 2012.
    {"cle": "virustotal", "nom": "VirusTotal", "pays": None,
     "nature": "entreprise", "appellations": ("virustotal",),
     "pays_motif": ("Fondée en Espagne, filiale d'un groupe américain depuis "
                    "2012 : les deux réponses se défendent.",
                    "Founded in Spain, a subsidiary of an American group since "
                    "2012: both answers hold.")},
    {"cle": "edd_californie",
     "nom": "Employment Development Department (Californie)",
     "nom_en": "Employment Development Department (California)",
     "pays": "US", "nature": "administration",
     "appellations": ("employment development department",)},
)


def _verifier():
    """CE QUE LE RÉPERTOIRE NE DOIT PAS DEVENIR, contrôlé au chargement.

    Une faute ici ne se voit pas à l'écran : elle se voit dans un filtre qui
    rattache des fiches à la mauvaise entreprise, ce qui est pire qu'un filtre
    absent. Le module refuse donc de se charger plutôt que de servir un
    répertoire douteux."""
    vues, appels = set(), {}
    for o in ORGANISATIONS:
        for champ in ("cle", "nom", "nature", "appellations"):
            if not o.get(champ):
                raise ValueError("organisation sans %s : %r" % (champ, o))
        if o["cle"] in vues:
            raise ValueError("clé en double : %s" % o["cle"])
        vues.add(o["cle"])
        if o["nature"] not in NATURES:
            raise ValueError("nature inconnue : %s" % o["nature"])
        # UN SIÈGE VIDE DOIT DIRE POURQUOI. Sans cette règle, un pays oublié
        # se lirait comme un siège disputé, et le lecteur croirait à une
        # réserve là où il n'y a qu'un trou.
        if o.get("pays") is None and not o.get("pays_motif"):
            raise ValueError("siège absent sans motif : %s" % o["cle"])
        if o.get("pays") and not re.match(r"^[A-Z]{2}$", o["pays"]):
            raise ValueError("pays hors ISO 3166-1 alpha-2 : %s" % o["cle"])
        for a in o["appellations"]:
            if a != a.lower():
                raise ValueError("appellation non minuscule : %r" % a)
            # DEUX LETTRES SE CACHENT DANS TROP DE MOTS. La leçon est déjà
            # payée dans `ingestion.py` avec « ics » trouvé dans
            # « diagnostics » : trois caractères est le plancher, et encore
            # est-ce le mot entier qui est cherché.
            if len(a) < 3:
                raise ValueError("appellation trop courte : %r" % a)
            if a in appels and appels[a] != o["cle"]:
                raise ValueError("appellation « %s » partagée par %s et %s"
                                 % (a, appels[a], o["cle"]))
            appels[a] = o["cle"]


_verifier()

#: Les appellations, LA PLUS LONGUE D'ABORD. L'ordre est ce qui fait la règle :
#: il est calculé une fois, et non à chaque fiche.
_APPELS = sorted(((a, o["cle"]) for o in ORGANISATIONS for a in o["appellations"]),
                 key=lambda x: (-len(x[0]), x[0]))

_PAR_CLE = {o["cle"]: o for o in ORGANISATIONS}


def _motif(appellation):
    """Mot entier, insensible à la casse. Le passage trouvé sera consommé."""
    return re.compile(r"(?<![a-z0-9])%s(?![a-z0-9])" % re.escape(appellation))


_MOTIFS = [(_motif(a), cle) for a, cle in _APPELS]


def reconnaitre(*textes):
    """Les organisations que LA SOURCE nomme dans ces textes-là.

    L'ordre du résultat est celui du répertoire, pas celui de la rencontre :
    deux fiches nommant les mêmes entreprises doivent porter la même liste,
    sans quoi le lecteur croirait à un classement.

    LE PASSAGE TROUVÉ EST CONSOMMÉ — remplacé par un blanc — pour que
    « Hitachi Energy » ne donne pas aussi « Hitachi ». C'est la règle « la
    plus longue gagne », et elle est appliquée ici, pas supposée ailleurs.
    """
    reste = " ".join(str(t or "") for t in textes).lower()
    trouvees = set()
    for motif, cle in _MOTIFS:
        neuf, n = motif.subn(" ", reste)
        if n:
            trouvees.add(cle)
            reste = neuf
    return [o["cle"] for o in ORGANISATIONS if o["cle"] in trouvees]


def nom(cle, langue="fr"):
    o = _PAR_CLE.get(cle)
    if not o:
        return cle
    return o.get("nom_en") or o["nom"] if langue == "en" else o["nom"]


def siege(cle):
    """Le pays du siège, ou None quand il est disputé — jamais deviné."""
    o = _PAR_CLE.get(cle)
    return o.get("pays") if o else None


def referentiel():
    """Ce que l'écran a besoin de savoir pour NOMMER une organisation. Les
    comptes ne sont pas ici : ils dépendent des filtres en cours, et c'est
    `veille.facettes` qui les tient.

    LES DEUX COLONNES SONT SERVIES, ET L'ÉCRAN CHOISIT. C'est la règle du site
    depuis les pays et les sujets : traduire côté serveur obligerait à savoir
    ici quelle langue le lecteur lit, alors que ce choix vit dans son
    navigateur — et une page déjà chargée devrait redemander tout le
    répertoire pour changer un intitulé."""
    return [{
        "cle": o["cle"],
        "nom": o["nom"],
        "nom_en": o.get("nom_en") or o["nom"],
        "pays": o.get("pays"),
        "nature": o["nature"],
        "nature_nom": NATURES[o["nature"]][0],
        "nature_nom_en": NATURES[o["nature"]][1],
        "pays_motif": (o.get("pays_motif") or ("", ""))[0] or None,
        "pays_motif_en": (o.get("pays_motif") or ("", ""))[1] or None,
    } for o in ORGANISATIONS]


def sante():
    """CE QUE LE RÉPERTOIRE COUVRE, ET CE QU'IL NE COUVRE PAS — mesuré, pas
    annoncé. Un répertoire tenu à la main vieillit ; ce compte est ce qui le
    dira."""
    sans_siege = [o["cle"] for o in ORGANISATIONS if not o.get("pays")]
    return {
        "module": "organisations",
        "version": "2026.08.24",
        "portee": "Reconnaît, dans les seuls champs où une source nomme une "
                  "entité, les organisations d'un répertoire écrit à la main. "
                  "N'extrait aucun nom et n'en devine aucun.",
        "organisations": len(ORGANISATIONS),
        "appellations": len(_APPELS),
        "pays_distincts": len({o["pays"] for o in ORGANISATIONS if o.get("pays")}),
        "siege_dispute": sans_siege,
        "origine_du_siege": ORIGINE_DU_SIEGE[0],
        "modeles_de_langage": 0,
    }
