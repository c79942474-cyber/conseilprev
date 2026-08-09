# -*- coding: utf-8 -*-
"""Reprise de la base documentaire de conseilprevcyber dans Sentinel.

POURQUOI CE MODULE
Les deux plateformes du cabinet tiennent chacune une base de connaissance, avec
des schemas differents : conseilprevcyber classe ses documents par THEME —
domaines normatifs, familles techniques, et noms d'ENTREPRISES — quand Sentinel
les rattache a des PAGES (audit, registre, FRIA…). Transferer sans traduire
perdrait le classement, qui est l'essentiel du travail accumule.

Ce module fait la traduction, et rien d'autre : il ne touche ni au reseau ni a
la base. Il prend une sauvegarde conseilprevcyber et rend des documents prets a
inserer, avec leur theme d'origine CONSERVE TEL QUEL, sa famille, et les pages
Sentinel deduites. Il est donc verifiable seul.

CE QUI EST CONSERVE, ET POURQUOI
Le theme d'origine est garde mot pour mot, meme s'il ne veut rien dire pour
Sentinel. Un document classe « IEC 62443 » ou « EDF » chez conseilprevcyber doit
rester retrouvable sous ce nom : c'est ainsi que son proprietaire le cherchera.
Les pages Sentinel sont AJOUTEES, elles ne remplacent pas.
"""
import base64
import os
import re
import unicodedata

VERSION = "2026-07-a"

# ═══════════════════════════════════════════════════════════════════════════
# 1. LE VOCABULAIRE D'ORIGINE
#    Copie du referentiel de conseilprevcyber (rag_store.THEME_FAMILLES) au
#    30 juillet 2026. Copie et non import : les deux depots sont separes, et
#    une dependance croisee ferait qu'aucun des deux ne pourrait etre deploye
#    seul. Un theme absent de cette liste n'est pas perdu pour autant — il
#    tombe dans « Autres », avec son libelle intact.
# ═══════════════════════════════════════════════════════════════════════════

FAMILLES = [
    ('Normes & réglementations', [
        'Normes IEC',
        'IEC 62443',
        'ISO 27001 / 27002',
        'ISO Standards',
        'Normes',
        'NIST CSF / SP 800-82',
        'NIS2',
        'DORA',
        'RGPD',
        'AI Act',
        'Cyber Resilience Act',
        'Sûreté fonctionnelle (IEC 61508/61511)',
    ]),
    ('ANSSI', [
        'ANSSI',
        'ANSSI / Guides & recommandations',
        'ANSSI / Référentiels & qualification',
        'ANSSI / Méthodes (EBIOS RM)',
        'Guides ANSSI',
    ]),
    ('Architecture & technique OT/IT', [
        'Architecture & segmentation',
        'Inventaire & cartographie',
        'Analyse de risques',
        'Durcissement & configuration',
        'Gestion des correctifs',
        'Gestion des accès & identités',
        'Accès distant & télémaintenance',
        'Sécurité réseau & pare-feu',
        'Automates, SCADA & DCS',
        'SCADA',
        'IIoT & objets connectés',
        'Automotive',
        'Cryptographie & PKI',
        'Supervision & détection',
        'Réponse à incident',
        'Continuité & résilience (PRA/PCA)',
    ]),
    ('Gouvernance & organisation', [
        'Gouvernance & CSMS',
        'Sensibilisation & formation',
        'Gestion des prestataires',
        'Conformité & audit',
    ]),
    ('Juridique & contrats', [
        'Juridique / Textes & réglementation',
        'Juridique / Doctrine & lignes directrices',
        'Juridique / Contrats & clausiers',
        'Juridique / Contrats fournisseurs',
        'Juridique / Notes & consultations',
        'Juridique / Jurisprudence & sanctions',
        'Juridique / IA Act',
        'Juridique / NIS 2 & DORA',
        'Juridique / RGPD & données',
        "Juridique / Marchés & appels d'offres",
    ]),
    # Centres de données — miroir de la famille ajoutee dans rag_store.py de
    # conseilprevcyber. Les deux listes sont des copies volontaires (voir
    # l'en-tete) : un theme present d'un cote et absent de l'autre rendrait les
    # memes documents classables ici et introuvables la-bas.
    ('Centres de données', [
        'Data center',
        'Data center / Conception & architecture',
        'Data center / Thermique & refroidissement',
        'Data center / Refroidissement liquide & immersion',
        'Data center / Eau & stress hydrique',
        'Data center / Énergie & électricité',
        'Data center / Chaleur fatale & réseaux de chaleur',
        'Data center / Carbone & analyse de cycle de vie',
        'Data center / Efficacité & indicateurs (PUE, WUE, CUE, ERE)',
        'Data center / Normes (EN 50600, ISO/IEC 30134, ASHRAE)',
        'Data center / Réglementation UE (EED, taxonomie, CSRD)',
        "Data center / Appels d'offres & CCTP",
        'Data center / Études de site & implantation',
        'Data center / Recherche & état de l\'art',
        'Data center / Retours d\'exploitation & mesures',
        'Data center / Fournisseurs & fiches techniques',

        # Deux sous-dossiers de MANAGEMENT, distincts des seize precedents qui
        # sont techniques. Un plan de gestion environnementale et un plan de
        # sécurité ne se cherchent pas au meme moment que la note thermique.
        'Data center / Green Management',
        'Data center / Green Management / Politique & objectifs',
        'Data center / Green Management / Indicateurs & reporting',
        'Data center / Green Management / Certifications & labels',
        'Data center / Safety Management',
        'Data center / Safety Management / Analyse de risques & HAZOP',
        'Data center / Safety Management / Incendie & détection',
        'Data center / Safety Management / Consignation & travaux',
        'Data center / Safety Management / Plans d\'urgence & exercices',
    ]),

    ('Métier & livrables', [
        'AMOA SI Industriel',
        'Cahier des charges & CCTP',
        'Plan de remédiation',
        'Études de cas',
    ]),
    ('Engineering', [
        'Engineering',
        'Engineering / Projet OWFarm',
        'Engineering / Projet OWFarm / BSH2 Package',
        'Engineering / Projet OWFarm / Safety',
        'Engineering / Projet OWFarm / Fire fighting',
        'Engineering / Projet OWFarm / Fire fighting / Watermist',
        'Engineering / Projet OWFarm / Rules',
        'Engineering / Projet OWFarm / Rules / DNV',
        'Engineering / Projet OWFarm / Rules / NFPA',
        'Engineering / Oil & Gas',
        'Engineering / Oil & Gas / GNL',
        'Engineering / Oil & Gas / GNL / LNG Guidance Projects',
        'Engineering / Oil & Gas / GNL / Rules',
        'Engineering / Oil & Gas / Safety',
        'Engineering / Oil & Gas / Rules',
    ]),
    ('Entreprises & références', [
        'Alstom',
        'Atos',
        'EDF',
        'GRDF',
        'Renault',
        'SGP',
        'Technip',
    ]),
    ('Divers', [
        'Veille',
        'Général',
    ]),
]

# Normalisation partagée : deux sections l'emploient — la déduction des pages
# et l'appartenance à un périmètre. Elle est posée AVANT elles, plutôt qu'entre
# les deux comme auparavant : Python s'en accommodait, pas le lecteur.
def _sans_accents(t):
    t = unicodedata.normalize("NFD", str(t or ""))
    return "".join(c for c in t if not unicodedata.combining(c)).lower()


FAMILLE_ENTREPRISES = "Entreprises & références"

_INDEX_FAMILLE = {}
for _nom, _themes in FAMILLES:
    for _t in _themes:
        _INDEX_FAMILLE[_t] = _nom


def famille_de(theme):
    """Famille d'un thème. Les sous-dossiers héritent de leur parent : un thème
    « Engineering / Projet OWFarm / Safety » absent du vocabulaire doit tomber
    dans « Engineering », pas dans « Autres »."""
    t = (theme or "").strip()
    if not t:
        return "Divers"
    if t in _INDEX_FAMILLE:
        return _INDEX_FAMILLE[t]
    racine = t.split(" / ")[0].strip()
    return _INDEX_FAMILLE.get(racine, "Autres")


def est_entreprise(theme):
    """Vrai si le thème désigne une entreprise ou une référence client."""
    return famille_de(theme) == FAMILLE_ENTREPRISES


# ═══════════════════════════════════════════════════════════════════════════
# 1 bis. PÉRIMÈTRES DE RÉDACTION — une dimension à part, et il le fallait
#
#    LE PROBLÈME. Sentinel range ses documents par PAGE : audit, registre,
#    fria, maturité, veille, raci, général. Ces sept pages parlent toutes IA
#    Act et RGPD. Aucune ne parle Safety, incendie, DNV ou CCTP — si bien que
#    tout ce qui vient d'Engineering atterrit dans « général », faute de
#    mieux, et devient indistinguable du reste.
#
#    LA FAUSSE BONNE IDÉE, qu'on écarte. On pourrait forcer ces documents vers
#    « audit » ou « registre » pour qu'ils cessent d'être orphelins. Ce serait
#    poser une règle NFPA devant quelqu'un qui instruit un registre de systèmes
#    d'IA : du bruit, pas de l'aide. Les pages restent ce qu'elles sont.
#
#    CE QU'ON FAIT. Un PÉRIMÈTRE est une seconde dimension, bâtie sur le thème
#    d'origine — celui que l'import conserve déjà — et orthogonale aux pages.
#    Elle sert à DISCRIMINER une rédaction : « je rédige une pièce d'incendie »
#    n'est pas « je rédige un registre IA », et les deux puisent pourtant dans
#    la même réserve.
#
#    ELLE PRIORISE, ELLE NE FILTRE PAS. Le périmètre fait remonter ce qui lui
#    appartient ; il ne cache jamais le reste. Un document utile rangé ailleurs
#    doit rester atteignable, sinon l'absence de résultat ne dirait plus si la
#    pièce n'existe pas ou si elle est hors périmètre.
# ═══════════════════════════════════════════════════════════════════════════

#  cle, libellé, familles rattachées, mots reconnus dans le thème ou le nom
PERIMETRES = (
    ("engineering", "Engineering", ("Engineering",),
     ("engineering", "owfarm", "oil & gas", "oil and gas", "gnl", "lng", "offshore",
      "package")),
    ("moe", "Maîtrise d'œuvre & pièces de marché", ("Métier & livrables",),
     ("maitrise d'oeuvre", "maitrise d oeuvre", "cctp", "cahier des charges",
      "appel d'offres", "appels d'offres", "amoa", "dce", "marche de travaux",
      "bordereau", "dpgf")),
    ("safety", "Safety & analyse de risques", (),
     ("safety", "hazop", "hazid", "atex", "analyse de risques", "consignation",
      "plan d'urgence", "securite des personnes")),
    ("fire", "Incendie & fire fighting", (),
     ("fire", "incendie", "watermist", "brouillard d'eau", "sprinkler", "extinction",
      "desenfumage", "detection incendie")),
    ("rules", "Règles, normes & codes", (),
     ("rules", "dnv", "nfpa", "en 50600", "ashrae", "iso/iec", "iec 6", "norme",
      "reglement", "code de construction")),
    ("datacenter", "Centres de données", ("Centres de données",),
     ("data center", "datacenter", "pue", "wue", "refroidissement", "free cooling")),
)

_INDEX_PERIMETRE = {p[0]: p for p in PERIMETRES}


def perimetres():
    """Les périmètres proposés au rédacteur, prêts à afficher."""
    return [{"cle": c, "nom": n, "familles": list(f), "mots": len(m)}
            for c, n, f, m in PERIMETRES]


def perimetre_valide(cle):
    return (cle or "") in _INDEX_PERIMETRE


def dans_perimetre(cle, theme="", famille="", nom_fichier=""):
    """Ce document appartient-il au périmètre demandé ?

    Trois voies, et la troisième n'est pas un luxe : un document déposé
    directement sur Sentinel n'a NI thème NI famille — l'import est le seul à
    en poser. Sans le repli sur le nom de fichier, la moitié de la réserve
    serait hors de tout périmètre, et le partage annoncé n'aurait pas lieu."""
    p = _INDEX_PERIMETRE.get(cle or "")
    if not p:
        return False
    _c, _nom, familles, mots = p
    fam = (famille or "").strip() or famille_de(theme)
    if familles and fam in familles:
        return True
    n = _sans_accents(theme) + " " + _sans_accents(nom_fichier)
    return any(m in n for m in mots)


# ═══════════════════════════════════════════════════════════════════════════
# 2. DU THÈME AUX PAGES SENTINEL
#    Sentinel rattache un document a des pages, pas a un domaine. La deduction
#    est par MOTS-CLES et volontairement large : mieux vaut un document propose
#    a une page de trop que rendu introuvable. « general » est toujours ajoute,
#    afin qu'aucun document ne devienne invisible si la deduction se trompe.
# ═══════════════════════════════════════════════════════════════════════════

PAGES_PAR_MOT = (
    ("audit", ("audit", "conformite", "62443", "iso 27001", "nist", "nis2", "dora",
               "cyber resilience", "evaluation", "maturite")),
    ("registre", ("ai act", "rgpd", "registre", "donnees personnelles", "traitement")),
    ("fria", ("droits fondamentaux", "fria", "impact", "ai act", "biometrie")),
    ("maturite", ("maturite", "gouvernance", "csms", "organisation", "sensibilisation",
                  "formation", "plan de remediation", "feuille de route")),
    ("veille", ("veille", "cert", "bulletin", "actualite", "avis")),
    ("raci", ("prestataire", "partie prenante", "raci", "responsabilite", "contrat",
              "clausier", "fournisseur", "juridique")),
)


def pages_pour(theme, titre=""):
    """Pages Sentinel déduites d'un thème et d'un titre. Toujours au moins
    « general » : un document mal déduit doit rester atteignable."""
    n = _sans_accents(theme) + " " + _sans_accents(titre)
    pages = [p for p, mots in PAGES_PAR_MOT if any(m in n for m in mots)]
    if "general" not in pages:
        pages.append("general")
    return pages


# ═══════════════════════════════════════════════════════════════════════════
# 3. LECTURE D'UNE SAUVEGARDE
# ═══════════════════════════════════════════════════════════════════════════

class ImportErreur(Exception):
    """Erreur de lecture d'une sauvegarde, avec son statut HTTP."""

    def __init__(self, message, statut=400, code="sauvegarde_invalide"):
        self.statut = statut
        self.code = code
        super().__init__(message)


def _extension(nom):
    return os.path.splitext(str(nom or ""))[1].lower().lstrip(".")


_MIME = {"pdf": "application/pdf", "txt": "text/plain", "csv": "text/csv",
         "md": "text/markdown", "json": "application/json", "log": "text/plain",
         "yaml": "application/yaml", "yml": "application/yaml",
         "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
         "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         "xlsm": "application/vnd.ms-excel.sheet.macroEnabled.12"}


def verifier_sauvegarde(obj):
    """Contrôle la forme d'une sauvegarde avant d'en tirer quoi que ce soit."""
    if not isinstance(obj, dict):
        raise ImportErreur("Le fichier n’est pas une sauvegarde JSON.")
    if obj.get("app") and obj["app"] != "conseilprevcyber-rag":
        raise ImportErreur("Cette sauvegarde vient de « %s », pas de conseilprevcyber."
                           % obj["app"], 422, "mauvaise_origine")
    docs = obj.get("documents")
    if not isinstance(docs, list):
        raise ImportErreur("La sauvegarde ne contient aucune liste de documents.",
                           422, "sans_documents")
    return docs


def lire_document(d):
    """Normalise UN document de la sauvegarde. Rend None si inexploitable —
    l'appelant compte les rejets et dit pourquoi, plutôt que d'interrompre un
    transfert de trois cents pièces pour une seule illisible."""
    if not isinstance(d, dict):
        return None, "entrée non conforme"
    b64 = d.get("content_b64") or ""
    if not b64:
        return None, "aucun contenu"
    try:
        donnees = base64.b64decode(b64, validate=False)
    except Exception:                                          # noqa: BLE001
        return None, "contenu illisible (base64)"
    if not donnees:
        return None, "contenu vide"

    nom = (d.get("filename") or "").strip()
    titre = (d.get("title") or "").strip()
    if not nom:
        nom = (titre or "document") + ".txt"
    ext = _extension(nom)
    theme = (d.get("theme") or "").strip()
    return {
        "nom_fichier": nom,
        "titre": titre or os.path.splitext(nom)[0],
        "extension": "." + ext if ext else "",
        "type_mime": _MIME.get(ext, "application/octet-stream"),
        "theme": theme,
        "famille": famille_de(theme),
        "entreprise": theme if est_entreprise(theme) else "",
        "visibilite": (d.get("visibility") or "public").strip() or "public",
        "pages": pages_pour(theme, titre),
        "donnees": donnees,
        "octets": len(donnees),
    }, None


def inventaire(obj):
    """Ce que contient une sauvegarde, AVANT de rien transférer : combien de
    documents, quel poids, quels domaines, quelles entreprises.

    On ne lance pas un transfert de plusieurs centaines de mégaoctets sans
    savoir ce qu'il contient — et l'inventaire est le seul moyen de vérifier
    ensuite que rien n'a été perdu en route."""
    docs = verifier_sauvegarde(obj)
    par_theme, par_famille, entreprises = {}, {}, {}
    total = octets = rejets = 0
    for d in docs:
        n, _motif = lire_document(d)
        if not n:
            rejets += 1
            continue
        total += 1
        octets += n["octets"]
        par_theme[n["theme"] or "(sans thème)"] = par_theme.get(n["theme"] or "(sans thème)", 0) + 1
        par_famille[n["famille"]] = par_famille.get(n["famille"], 0) + 1
        if n["entreprise"]:
            entreprises[n["entreprise"]] = entreprises.get(n["entreprise"], 0) + 1
    return {
        "documents": total, "rejets": rejets, "octets": octets,
        "themes": dict(sorted(par_theme.items(), key=lambda kv: (-kv[1], kv[0]))),
        "familles": dict(sorted(par_famille.items(), key=lambda kv: (-kv[1], kv[0]))),
        "entreprises": dict(sorted(entreprises.items(), key=lambda kv: (-kv[1], kv[0]))),
        "cree_le": obj.get("created_at"),
        "annonce": obj.get("count"),
    }
