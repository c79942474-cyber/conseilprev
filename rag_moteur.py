# -*- coding: utf-8 -*-
"""Moteur de la base de connaissance Sentinel — recherche, extraction, diagnostic.

POURQUOI CE MODULE
La base de connaissance vivait entièrement dans app.py. Deux conséquences :
elle n'était pas testable seule, et sa recherche restait en retrait de celle du
site industriel du cabinet. Le cœur est donc extrait ici — sans Flask, sans
connexion, sans état — pour être vérifié ligne à ligne.

CE QUI CHANGE POUR LE LECTEUR D'UNE RÉPONSE
La recherche était un ESCALIER : vectorielle d'abord, et le plein-texte
seulement si la vectorielle ne rendait rien. Un document qui répondait
lexicalement mais mal sémantiquement — un numéro d'article, un nom propre, un
sigle — était donc perdu dès que la recherche vectorielle rendait cinq résultats
médiocres. Les deux moteurs sont désormais interrogés ENSEMBLE et fusionnés.
"""
import io
import os
import re
import unicodedata

VERSION = "2026-07-a"

# ═══════════════════════════════════════════════════════════════════════════
# 1. ERREURS TYPÉES
#    Un défaut d'extraction n'est pas une panne du serveur. Distinguer les deux
#    évite de rendre un 500 opaque là où le bon message est « ce PDF est une
#    image, il n'a pas de texte à extraire ».
# ═══════════════════════════════════════════════════════════════════════════

class RagErreur(Exception):
    """Erreur portant un code lisible et le statut HTTP qui lui correspond."""

    MESSAGES = {
        "extension_refusee": "Ce format de fichier n’est pas accepté.",
        "fichier_vide": "Le fichier est vide.",
        "trop_gros": "Le fichier dépasse la taille autorisée.",
        "pdf_absent": "La lecture des PDF n’est pas disponible sur ce serveur.",
        "pdf_illisible": "Ce PDF n’a pas pu être lu — il est peut-être protégé ou endommagé.",
        "pdf_sans_texte": "Ce PDF ne contient pas de texte : c’est une image scannée. "
                          "Une reconnaissance optique serait nécessaire.",
        "docx_absent": "La lecture des documents Word n’est pas disponible sur ce serveur.",
        "docx_illisible": "Ce document Word n’a pas pu être lu.",
        "xlsx_absent": "La lecture des classeurs Excel n’est pas disponible sur ce serveur.",
        "xlsx_illisible": "Ce classeur Excel n’a pas pu être lu.",
        "texte_vide": "Aucun texte n’a pu être extrait de ce fichier.",
    }

    def __init__(self, code, statut=400, detail=None):
        self.code = code
        self.statut = statut
        self.detail = detail
        super().__init__(self.MESSAGES.get(code, code))

    def message(self):
        m = self.MESSAGES.get(self.code, self.code)
        return m + (" (" + self.detail + ")" if self.detail else "")


# ═══════════════════════════════════════════════════════════════════════════
# 2. FORMATS ACCEPTÉS
#    Élargis : un cabinet reçoit des notes en Markdown, des exports CSV, des
#    journaux et des classeurs, pas seulement des PDF et des Word.
# ═══════════════════════════════════════════════════════════════════════════

FORMATS_TEXTE = ("txt", "md", "csv", "log", "json", "yaml", "yml")
FORMATS_BINAIRES = ("pdf", "docx", "xlsx", "xlsm")
EXTENSIONS = FORMATS_TEXTE + FORMATS_BINAIRES


def extension_de(nom):
    return os.path.splitext(str(nom or ""))[1].lower().lstrip(".")


def valider_extension(nom):
    ext = extension_de(nom)
    if ext not in EXTENSIONS:
        raise RagErreur("extension_refusee", 415, ext or "sans extension")
    return ext


def formats_disponibles():
    """Ce que ce serveur sait réellement lire, ici et maintenant.

    Publié tel quel : promettre un format dont la bibliothèque est absente
    produit un échec au moment de l'envoi, quand l'utilisateur a déjà attendu."""
    dispo = {e: True for e in FORMATS_TEXTE}
    for ext, mod in (("pdf", "pypdf"), ("docx", "docx"), ("xlsx", "openpyxl")):
        try:
            __import__(mod)
            dispo[ext] = True
        except Exception:                                  # noqa: BLE001
            dispo[ext] = False
    dispo["xlsm"] = dispo["xlsx"]
    return dispo


def _decoder(donnees):
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return donnees.decode(enc)
        except UnicodeDecodeError:
            continue
    return donnees.decode("utf-8", errors="replace")


def extraire_texte(nom, donnees):
    """Texte brut d'un fichier. Lève une RagErreur explicite en cas d'échec."""
    if not donnees:
        raise RagErreur("fichier_vide", 400)
    ext = valider_extension(nom)

    if ext in FORMATS_TEXTE:
        return _decoder(donnees)

    if ext == "pdf":
        try:
            from pypdf import PdfReader
        except Exception:                                  # noqa: BLE001
            raise RagErreur("pdf_absent", 503)
        try:
            lecteur = PdfReader(io.BytesIO(donnees))
            texte = "\n\n".join((p.extract_text() or "") for p in lecteur.pages)
        except Exception as e:                             # noqa: BLE001
            raise RagErreur("pdf_illisible", 422, type(e).__name__)
        # Un PDF scanné rend une chaîne vide sans lever : sans ce contrôle, le
        # document serait accepté, indexé à zéro fragment, et introuvable —
        # un échec silencieux, le pire des trois.
        if not texte.strip():
            raise RagErreur("pdf_sans_texte", 422)
        return texte

    if ext == "docx":
        try:
            import docx
        except Exception:                                  # noqa: BLE001
            raise RagErreur("docx_absent", 503)
        try:
            d = docx.Document(io.BytesIO(donnees))
            parties = [p.text for p in d.paragraphs if p.text.strip()]
            # Les tableaux Word portent souvent l'essentiel d'une note de
            # cadrage : les ignorer revient à perdre la moitié du document.
            for t in d.tables:
                for ligne in t.rows:
                    cellules = [c.text.strip() for c in ligne.cells]
                    if any(cellules):
                        parties.append(" | ".join(cellules))
            return "\n\n".join(parties)
        except Exception as e:                             # noqa: BLE001
            raise RagErreur("docx_illisible", 422, type(e).__name__)

    if ext in ("xlsx", "xlsm"):
        try:
            import openpyxl
        except Exception:                                  # noqa: BLE001
            raise RagErreur("xlsx_absent", 503)
        try:
            cl = openpyxl.load_workbook(io.BytesIO(donnees), read_only=True, data_only=True)
            parties = []
            for feuille in cl.worksheets:
                parties.append("### " + str(feuille.title))
                for ligne in feuille.iter_rows(values_only=True):
                    vals = [str(v) for v in ligne if v is not None]
                    if vals:
                        parties.append(" | ".join(vals))
            return "\n".join(parties)
        except Exception as e:                             # noqa: BLE001
            raise RagErreur("xlsx_illisible", 422, type(e).__name__)

    raise RagErreur("extension_refusee", 415, ext)


# ═══════════════════════════════════════════════════════════════════════════
# 3. DÉCOUPAGE
#    Coupe au séparateur de phrase le plus proche plutôt qu'au caractère brut :
#    un fragment tranché en plein milieu d'un mot se retrouve mal vectorisé et
#    illisible quand il est cité en réponse.
# ═══════════════════════════════════════════════════════════════════════════

TAILLE_FRAGMENT = 900
RECOUVREMENT = 150


def decouper(texte, taille=TAILLE_FRAGMENT, recouvrement=RECOUVREMENT):
    texte = re.sub(r"[ \t]+", " ", str(texte or "")).strip()
    texte = re.sub(r"\n{3,}", "\n\n", texte)
    if not texte:
        return []
    if len(texte) <= taille:
        return [texte]

    fragments, debut = [], 0
    while debut < len(texte):
        fin = min(debut + taille, len(texte))
        if fin < len(texte):
            # On cherche une frontière propre dans le dernier quart du fragment.
            fenetre = texte[debut + int(taille * 0.75):fin]
            for sep in ("\n\n", ". ", ".\n", " ; ", "\n"):
                pos = fenetre.rfind(sep)
                if pos > 0:
                    fin = debut + int(taille * 0.75) + pos + len(sep)
                    break
        frag = texte[debut:fin].strip()
        if frag:
            fragments.append(frag)
        if fin >= len(texte):
            break
        debut = max(fin - recouvrement, debut + 1)
    return fragments


# ═══════════════════════════════════════════════════════════════════════════
# 4. REQUÊTES
#    Le plein-texte de Postgres attend une syntaxe : lui passer des mots bruts
#    joints par « | » suffit à ramener tout document contenant N'IMPORTE LEQUEL
#    des mots, y compris « le » ou « pour ». La précision s'effondre.
# ═══════════════════════════════════════════════════════════════════════════

_MOTS_VIDES = frozenset("""
au aux avec ce ces dans de des du elle en et eux il je la le les leur lui ma
mais me meme mes moi mon ne nos notre nous on ou par pas pour qu que qui sa se
ses son sur ta te tes toi ton tu un une vos votre vous c d j l a m n s t y ete
etee etees etes etant suis es est sommes etes sont serai seras sera serons
serez seront avoir etre cette cet celui celle ceux quel quelle quels quelles
plus moins tres tout tous toute toutes autre autres comme donc alors alor
""".split())

_JETON = re.compile(r"[0-9a-zàâäéèêëîïôöùûüçñ]+", re.I)


def _sans_accents(t):
    t = unicodedata.normalize("NFD", str(t or ""))
    return "".join(c for c in t if not unicodedata.combining(c)).lower()


def termes_requete(requete, mini=2):
    """Termes utiles d'une requête, mots vides écartés, doublons supprimés.

    Les termes sont réduits à des caractères alphanumériques : ils peuvent donc
    être injectés sans risque dans une `to_tsquery`, où un caractère de
    ponctuation provoquerait une erreur de syntaxe côté base."""
    vus, out = set(), []
    for brut in _JETON.findall(str(requete or "")):
        t = _sans_accents(brut)
        if len(t) < mini or t in _MOTS_VIDES or t in vus:
            continue
        vus.add(t)
        out.append(brut.lower())
    # Une requête entièrement composée de mots vides (« pour quoi et ») ne doit
    # pas rendre une liste vide : on rend alors les jetons bruts.
    if not out:
        out = [_sans_accents(t) for t in _JETON.findall(str(requete or "")) if len(t) >= mini]
    return out


# ═══════════════════════════════════════════════════════════════════════════
# 5. FUSION DE RANGS RÉCIPROQUES
#
#    Le point central de cette reprise. Deux moteurs répondent à la même
#    question par des scores qui ne sont pas comparables : une similarité
#    cosinus vaut entre 0 et 1, un `ts_rank` vaut ce qu'il veut. Les additionner
#    n'a aucun sens ; choisir l'un et jeter l'autre en perd la moitié.
#
#    La fusion de rangs réciproques ignore les scores et ne regarde que les
#    RANGS : score(d) = Σ 1/(k + rang). Un document bien placé dans les deux
#    listes passe devant un document excellent dans une seule. Méthode éprouvée
#    en recherche d'information, et indépendante de l'échelle des moteurs.
# ═══════════════════════════════════════════════════════════════════════════

K_RRF = 60


def fusionner(listes, cle=None, k=K_RRF):
    """Fusionne des listes classées en un seul classement.

    `cle` extrait l'identité d'un résultat ; par défaut le texte du fragment.
    Les listes sont passées par ordre de priorité : à égalité, la première
    rencontrée fournit l'objet conservé."""
    if cle is None:
        def cle(r):
            return r.get("texte") if isinstance(r, dict) else r[0]
    scores, garde = {}, {}
    for liste in listes:
        for rang, r in enumerate(liste or []):
            c = cle(r)
            scores[c] = scores.get(c, 0.0) + 1.0 / (k + rang + 1)
            garde.setdefault(c, r)
    ordre = sorted(scores, key=lambda c: scores[c], reverse=True)
    sortie = []
    for c in ordre:
        r = dict(garde[c]) if isinstance(garde[c], dict) else garde[c]
        if isinstance(r, dict):
            r["score_fusion"] = round(scores[c], 5)
        sortie.append(r)
    return sortie


# ═══════════════════════════════════════════════════════════════════════════
# 6. DIAGNOSTIC
#    Une base qui ne rend rien a toujours une raison. La dire économise une
#    heure de recherche : clé d'embeddings absente, extension pgvector non
#    installée, aucun document indexé, aucun terme utile dans la requête.
# ═══════════════════════════════════════════════════════════════════════════

def diagnostiquer(etat):
    """(liste de constats, capacité de recherche effective).

    `etat` : dict attendu avec les clés `base` (un magasin est joignable),
    `base_pg` (ce magasin est PostgreSQL), `pgvector`, `embeddings`,
    `documents`, `fragments`, `fragments_vectorises`.

    `base` et `base_pg` sont distincts À DESSEIN : en développement le magasin
    est un fichier SQLite. La recherche par les mots y fonctionne — la déclarer
    « indisponible » ferait chercher une panne là où il n'y en a pas."""
    constats = []
    base = etat.get("base", etat.get("base_pg"))

    if not base:
        constats.append({"niveau": "bloquant", "cle": "base",
                         "texte": "Aucune base de données joignable : la base de "
                                  "connaissance ne peut ni stocker ni retrouver de document."})
    elif not etat.get("base_pg"):
        constats.append({"niveau": "attention", "cle": "base_locale",
                         "texte": "Magasin local SQLite, et non PostgreSQL : la recherche "
                                  "par les mots reste approchée et les vecteurs ne peuvent "
                                  "pas être stockés. C’est le mode de développement."})
    if not etat.get("documents"):
        constats.append({"niveau": "attention", "cle": "vide",
                         "texte": "Aucun document versé : la recherche ne peut rien rendre. "
                                  "C’est une base vide, pas une panne."})
    elif not etat.get("fragments"):
        constats.append({"niveau": "bloquant", "cle": "non_indexe",
                         "texte": "Des documents sont présents mais aucun n’est découpé "
                                  "en fragments : l’indexation ne s’est pas terminée."})

    if not etat.get("embeddings"):
        constats.append({"niveau": "attention", "cle": "embeddings",
                         "texte": "Clé d’API d’embeddings absente : la recherche par le SENS "
                                  "est indisponible. La recherche par les MOTS fonctionne."})
    elif not etat.get("pgvector"):
        constats.append({"niveau": "attention", "cle": "pgvector",
                         "texte": "Extension pgvector non installée sur cette base : les "
                                  "vecteurs ne peuvent pas être stockés. Recherche par les "
                                  "mots uniquement."})
    elif etat.get("fragments") and not etat.get("fragments_vectorises"):
        constats.append({"niveau": "attention", "cle": "vecteurs_absents",
                         "texte": "Les fragments existent mais aucun n’est vectorisé : "
                                  "relancer l’indexation pour activer la recherche par le sens."})

    lexical = bool(base and etat.get("fragments"))
    vectoriel = bool(lexical and etat.get("base_pg") and etat.get("pgvector")
                     and etat.get("embeddings") and etat.get("fragments_vectorises"))
    if vectoriel:
        mode = "hybride"
    elif lexical:
        mode = "lexical"
    else:
        mode = "indisponible"

    if not constats:
        constats.append({"niveau": "ok", "cle": "ok",
                         "texte": "Recherche hybride opérationnelle : les mots et le sens "
                                  "sont interrogés ensemble, puis fusionnés."})
    return constats, mode


MODES = {
    "hybride": "Mots et sens interrogés ensemble, résultats fusionnés par rang réciproque",
    "lexical": "Mots seulement — la recherche par le sens est indisponible",
    "indisponible": "Aucune recherche possible en l’état",
}


def sante(etat=None):
    d = {"version": VERSION, "formats": formats_disponibles(),
         "taille_fragment": TAILLE_FRAGMENT, "recouvrement": RECOUVREMENT}
    if etat is not None:
        constats, mode = diagnostiquer(etat)
        d["mode"] = mode
        d["mode_libelle"] = MODES.get(mode, mode)
        d["constats"] = constats
    return d
