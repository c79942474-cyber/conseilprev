"""LA COMPRESSION DES RÉPONSES — mesurée sur ce qui voyage, pas sur l'intention.

CE QUI PARTAIT EN CLAIR. Ni Flask ni Render ne compressent quoi que ce soit
par défaut. Ce site sert 354 Ko de feuilles de style et de scripts —
`veille.css` fait 91 Ko à lui seul, `langue.js` 73 Ko — et les envoyait tels
quels à chaque première visite. Le défaut ne casse rien : il coûte, et il ne
se voit qu'en regardant les en-têtes réellement servis.

LE PIÈGE, ET POURQUOI CE FICHIER EXISTE. Sur le site voisin, une première
version du même crochet écartait les réponses `is_streamed`. Or une réponse de
`send_from_directory` a pour corps un `FileWrapper`, objet sans longueur, que
Werkzeug déclare précisément `is_streamed` : le crochet écartait EXACTEMENT ce
qu'il devait comprimer. Il s'exécutait, ne servait à rien, et rien ne le
disait. Ces contrôles sont écrits pour que ce silence-là soit impossible ici.

CE QUI EST VÉRIFIÉ EST LE CORPS, PAS L'EN-TÊTE. Une réponse annoncée
`Content-Encoding: gzip` est décompressée et comparée octet pour octet au
fichier sur disque. Un en-tête peut mentir ; des octets qui se décompressent
en l'original, non.

ET LA LISTE DES FICHIERS N'EST PAS ÉCRITE ICI : elle est relue du dépôt. Une
liste tenue à part dériverait, et ces contrôles ne protégeraient plus que
d'elle-même.
"""
import glob
import gzip
import os
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import app as A  # noqa: E402

from flask import Response  # noqa: E402


# DEUX ROUTES DE RECETTE, POSÉES AVANT LA PREMIÈRE REQUÊTE — Flask refuse de
# les enregistrer après coup, et c'est heureux. Elles éprouvent deux cas que le
# dépôt n'offre pas : une réponse trop courte pour valoir une compression, et
# un VRAI flux, celui que le crochet doit laisser passer alors que
# `is_streamed` le confond avec un fichier. Elles passent par le crochet réel.
@A.app.route("/_recette_compression_court")
def _recette_compression_court():
    return Response("court" * 20, mimetype="text/plain")


@A.app.route("/_recette_compression_flux")
def _recette_compression_flux():
    def gen():
        for _ in range(400):
            yield "du texte assez long pour dépasser le seuil, " * 3
    return Response(gen(), mimetype="text/plain")


def _get(chemin, gzip_accepte=True, **entetes):
    h = {"Accept-Encoding": "gzip, deflate" if gzip_accepte else "identity"}
    h.update(entetes)
    return A.app.test_client().get(chemin, headers=h)


def _statiques():
    """Les scripts et feuilles de style réellement présents, du plus gros au
    plus petit, au-dessus du seuil de compression."""
    f = [p for p in glob.glob(os.path.join(ICI, "*.js"))
         + glob.glob(os.path.join(ICI, "*.css"))
         if os.path.getsize(p) > A._GZIP_MIN]
    return sorted(f, key=os.path.getsize, reverse=True)


# ── LE DÉFAUT LUI-MÊME ────────────────────────────────────────────────────

def test_les_scripts_et_les_styles_arrivent_compresses():
    """LE CONTRÔLE QUI RENDRAIT UN CROCHET MUET IMPOSSIBLE. C'est le cas exact
    qu'un filtre sur `is_streamed` écarterait : une réponse de
    `send_from_directory`, en passe-plat, corps `FileWrapper`."""
    fichiers = _statiques()
    assert fichiers, "aucun .js ni .css dans le dépôt : le contrôle ne mesure rien"
    clairs = []
    for chemin in fichiers:
        nom = os.path.basename(chemin)
        r = _get("/" + nom)
        assert r.status_code == 200, nom
        if r.headers.get("Content-Encoding") != "gzip":
            clairs.append(nom)
    assert not clairs, "servis en clair : %s" % clairs


def test_le_corps_compresse_redonne_le_fichier_octet_pour_octet():
    """Un en-tête peut mentir. Les octets, non."""
    for chemin in _statiques()[:6]:
        nom = os.path.basename(chemin)
        r = _get("/" + nom)
        assert gzip.decompress(r.data) == open(chemin, "rb").read(), nom


def test_la_longueur_annoncee_est_celle_du_corps_compresse():
    """Une longueur restée sur la taille d'origine tronquerait la réponse ou
    la ferait attendre indéfiniment."""
    r = _get("/" + os.path.basename(_statiques()[0]))
    assert int(r.headers["Content-Length"]) == len(r.data)


def test_le_gain_est_reel_et_mesure_sur_le_depot():
    """Une compression qui ne gagne rien ne vaut pas son coût. Le chiffre
    n'est pas écrit : il est mesuré."""
    clair = compresse = 0
    for chemin in _statiques():
        r = _get("/" + os.path.basename(chemin))
        clair += os.path.getsize(chemin)
        compresse += len(r.data)
    assert compresse < clair * 0.45, (
        "les fichiers statiques ne gagnent que %d %%"
        % (100 - 100 * compresse // clair))


def test_les_pages_html_arrivent_compressees():
    for chemin, _ in (("/", "index"), ("/revue", "revue"),
                      ("/confidentialite", "confidentialité")):
        r = _get(chemin)
        if r.status_code != 200:
            continue
        assert r.headers.get("Content-Encoding") == "gzip", chemin
        assert b"<!" in gzip.decompress(r.data)[:400].lower()


# ── CE QUE LE CROCHET DOIT LAISSER TRANQUILLE ─────────────────────────────

def test_une_police_deja_compressee_nest_meme_pas_soumise_au_compresseur(
        compressions):
    """Le format `woff2` embarque sa propre compression : la repasser au gzip
    coûte du processeur et rend des octets EN PLUS.

    ET C'EST L'ESSAI QU'ON MESURE, PAS SON RÉSULTAT. Le crochet garde une
    sécurité de dernier ressort — si la version compressée est plus grosse,
    elle est jetée — de sorte qu'une police recomprimée par erreur arriverait
    quand même intacte au lecteur, en-tête absent. Une mutation supprimant le
    filtre par type de contenu a effectivement survécu à un contrôle qui ne
    regardait que l'en-tête : le gâchis était réel, invisible et gratuit à
    laisser passer. On compte donc les appels au compresseur."""
    polices = glob.glob(os.path.join(ICI, "polices", "*.woff2"))
    if not polices:
        pytest.skip("aucune police servie depuis le dépôt")
    nom = os.path.basename(polices[0])[:-len(".woff2")]
    r = _get("/polices/%s.woff2" % nom)
    assert r.status_code == 200, nom
    assert not r.headers.get("Content-Encoding")
    assert compressions["n"] == 0, (
        "une police déjà compressée est passée au compresseur pour rien")


def test_la_revisite_recoit_un_304_sans_corps():
    """L'étiquette ETag n'est pas touchée par la compression, et c'est voulu :
    Flask évalue If-None-Match AVANT le crochet. Y ajouter un suffixe
    casserait le 304 — c'est-à-dire le gain le plus important des deux, celui
    qui épargne le corps entier à chaque revisite."""
    nom = os.path.basename(_statiques()[0])
    r1 = _get("/" + nom)
    etag = r1.headers.get("ETag")
    assert etag, "%s est servi sans ETag : chaque revisite retélécharge tout" % nom
    r2 = _get("/" + nom, **{"If-None-Match": etag})
    assert r2.status_code == 304
    assert r2.data == b""


def test_un_lecteur_qui_ne_sait_pas_lire_gzip_recoit_le_fichier_en_clair():
    chemin = _statiques()[0]
    r = _get("/" + os.path.basename(chemin), gzip_accepte=False)
    assert not r.headers.get("Content-Encoding")
    assert r.data == open(chemin, "rb").read()


def test_vary_previent_les_caches_intermediaires():
    """Sans `Vary: Accept-Encoding`, un cache intermédiaire servirait la
    version compressée à un lecteur qui ne sait pas la lire."""
    r = _get("/" + os.path.basename(_statiques()[0]))
    assert "accept-encoding" in (r.headers.get("Vary") or "").lower()


def test_une_reponse_trop_courte_nest_pas_compressee():
    r = _get("/_recette_compression_court")
    assert r.status_code == 200
    assert not r.headers.get("Content-Encoding")


def test_un_vrai_flux_nest_pas_rassemble_en_memoire():
    """`is_streamed` recouvre deux choses : un fichier sur disque (borné,
    lisible) et un générateur, qu'on ne bufferise pas — le lire jusqu'au bout
    annulerait sa raison d'être. Le crochet ne doit toucher qu'au premier."""
    r = _get("/_recette_compression_flux")
    assert r.status_code == 200
    assert len(r.data) > A._GZIP_MIN, (
        "le flux de recette est trop court : il serait écarté par le seuil, "
        "et ce contrôle ne mesurerait plus rien")
    assert not r.headers.get("Content-Encoding")


# ── LA MÉMOIRE DE COMPRESSION ─────────────────────────────────────────────

class _EspionGzip:
    """Le module `gzip`, à ceci près qu'il compte ses compressions.

    COMPTER LES APPELS, PAS LE CONTENU DU CACHE : un code qui ÉCRIT dans le
    cache sans jamais le RELIRE laisse exactement une entrée et recomprime à
    chaque fois. La taille du cache ne mesure donc pas ce qu'elle prétend."""

    def __init__(self, compteur):
        self._c = compteur

    def __getattr__(self, nom):
        return getattr(gzip, nom)

    def compress(self, data, *a, **kw):
        self._c["n"] += 1
        return gzip.compress(data, *a, **kw)


@pytest.fixture
def compressions(monkeypatch):
    c = {"n": 0}
    monkeypatch.setattr(A, "gzip", _EspionGzip(c))
    return c


def test_un_fichier_stable_nest_compresse_quune_fois(compressions):
    nom = os.path.basename(_statiques()[0])
    A._GZIP_CACHE.clear()
    a = _get("/" + nom)
    assert a.headers.get("Content-Encoding") == "gzip"
    assert compressions["n"] == 1, "le fichier n'a pas été compressé"
    b = _get("/" + nom)
    assert compressions["n"] == 1, (
        "le fichier a été recomprimé alors qu'il n'a pas changé")
    assert a.data == b.data


def test_un_fichier_qui_change_est_recompresse():
    """La signature est prise sur Last-Modified et la longueur : un fichier
    remplacé doit repartir au compresseur, sinon un déploiement servirait
    l'ancienne version."""
    A._GZIP_CACHE.clear()
    d1 = A._gz_memo(("/x.js", "lun, 01 jan 2024", 5000), b"AAAA" * 2000)
    d2 = A._gz_memo(("/x.js", "mar, 02 jan 2024", 5000), b"BBBB" * 2000)
    assert d1 != d2
    assert gzip.decompress(d2) == b"BBBB" * 2000


def test_le_corpus_calcule_a_la_volee_nencombre_pas_la_memoire():
    """Le corpus change à chaque collecte : garder sa compression ferait
    grossir la mémoire sans jamais servir."""
    A._GZIP_CACHE.clear()
    A._gz_memo(None, b"CCCC" * 2000)
    assert A._GZIP_CACHE == {}


def test_la_memoire_est_bornee():
    A._GZIP_CACHE.clear()
    for i in range(A._GZIP_CACHE_MAX + 3):
        A._gz_memo(("/f%d.js" % i, "lun", 4000), b"D" * 4000)
    assert len(A._GZIP_CACHE) <= A._GZIP_CACHE_MAX


# ── LE CROCHET EST-IL SEULEMENT BRANCHÉ ? ─────────────────────────────────

def test_le_crochet_est_enregistre_sur_lapplication():
    """Un contrôle qui prouve que la règle fonctionne ne prouve pas qu'elle
    s'exécute. Celui-ci lit la liste des crochets de Flask."""
    noms = [f.__name__ for f in A.app.after_request_funcs.get(None, [])]
    assert "_comprimer" in noms


def test_les_entetes_de_securite_survivent_a_la_compression():
    """Les deux crochets se suivent. Comprimer ne doit pas emporter la
    politique de sécurité, ni l'inverse."""
    r = _get("/" + os.path.basename(_statiques()[0]))
    assert r.headers.get("Content-Encoding") == "gzip"
    assert r.headers.get("Content-Security-Policy")
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
