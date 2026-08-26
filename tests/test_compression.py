"""LA COMPRESSION DES RÉPONSES — et le silence qu'elle a d'abord gardé.

LA FAUTE, ET CE QU'ELLE COÛTAIT. Le JavaScript des pages a été sorti des
fichiers HTML vers des fichiers `.js` séparés. Le HTML, lui, est compressé
depuis longtemps par `_serve_page_fast` : la page d'accueil part en 58 Ko au
lieu de 269 Ko, soit -78 %. Les fichiers `.js`, servis par
`send_from_directory`, partaient EN CLAIR. L'extraction gagnait donc sur les
visites de retour et PERDAIT sur la première : 171 Ko qui coûtaient environ
40 Ko compressés en coûtaient désormais 176.

LA PREMIÈRE CORRECTION N'A RIEN CORRIGÉ, ET NE L'A PAS DIT. Le crochet
`compresser_texte` écartait les réponses `is_streamed`. Or une réponse de
`send_from_directory` a pour corps un `FileWrapper`, objet sans longueur, que
Werkzeug déclare précisément `is_streamed` : le crochet écartait EXACTEMENT
les fichiers qu'il devait comprimer. Il s'exécutait, ne servait à rien, et
aucune erreur ne le signalait. Seule une mesure de l'en-tête réellement servi
l'a révélé.

CE QUE CES CONTRÔLES MESURENT. Pas la présence d'un en-tête : le CORPS. Une
réponse annoncée `Content-Encoding: gzip` est décompressée et comparée octet
pour octet au fichier sur disque. Un en-tête peut mentir ; des octets qui se
décompressent en l'original, non.

CE QU'ILS REFUSENT DE MESURER À LA PLACE. La liste des fichiers `.js` n'est
pas écrite ici : elle est relue du dépôt. Une liste tenue à part dériverait
du dépôt réel, et ces contrôles ne protégeraient plus que d'elle-même.
"""
import glob
import gzip
import os
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
os.environ.setdefault('FLASK_SECRET_KEY', 'recette-compression')

import app as application  # noqa: E402


# DEUX ROUTES DE RECETTE, POSÉES AVANT LA PREMIÈRE REQUÊTE. Flask refuse
# d'enregistrer une route après coup, et c'est heureux. Elles servent à
# éprouver deux cas que le dépôt n'offre pas : une réponse trop courte pour
# valoir une compression, et un VRAI flux — un générateur, celui que le
# crochet doit laisser passer alors que `is_streamed` le confond avec un
# fichier. Elles passent par le crochet réel, pas par une imitation.
@application.app.route('/_recette_compression_court')
def _recette_compression_court():
    return application.Response('court' * 20, mimetype='text/plain')


@application.app.route('/_recette_compression_flux')
def _recette_compression_flux():
    def gen():
        for _ in range(400):
            yield 'du texte assez long pour dépasser le seuil, ' * 3
    return application.Response(gen(), mimetype='text/plain')


# Chaque page est sondée depuis une adresse distincte : le limiteur de débit
# de l'application compte 120 requêtes par minute et par IP, et un 429 se
# lirait comme une compression absente.
_IP = [0]


def _client():
    return application.app.test_client()


def _get(chemin, gzip_accepte=True, **entetes):
    _IP[0] += 1
    h = {'X-Forwarded-For': '203.0.113.%d' % (_IP[0] % 250 + 1)}
    if gzip_accepte:
        h['Accept-Encoding'] = 'gzip, deflate'
    else:
        h['Accept-Encoding'] = 'identity'
    h.update(entetes)
    return _client().get(chemin, headers=h)


def _js_du_depot():
    """Les fichiers `.js` réellement présents, du plus gros au plus petit."""
    f = [p for p in glob.glob(os.path.join(ICI, '*.js'))
         if os.path.getsize(p) > application._GZIP_MIN]
    return sorted(f, key=os.path.getsize, reverse=True)


# ──────────────────────────────────────────────────────────────────────
# LE DÉFAUT LUI-MÊME : un fichier statique doit arriver compressé
# ──────────────────────────────────────────────────────────────────────

def test_un_fichier_js_arrive_compresse():
    """LE CONTRÔLE QUI AURAIT VU LA PREMIÈRE VERSION MUETTE.

    C'est le cas exact que `is_streamed` écartait : une réponse de
    `send_from_directory`, en passe-plat, corps `FileWrapper`."""
    js = _js_du_depot()
    assert js, 'aucun fichier .js dans le dépôt : le contrôle ne mesure rien'
    nom = os.path.basename(js[0])
    r = _get('/' + nom)
    assert r.status_code == 200, nom
    assert r.headers.get('Content-Encoding') == 'gzip', (
        '%s est servi en clair — le crochet de compression ne le voit pas' % nom)


def test_le_corps_compresse_redonne_le_fichier_octet_pour_octet():
    """Un en-tête peut mentir. Les octets, non."""
    for chemin in _js_du_depot()[:5]:
        nom = os.path.basename(chemin)
        r = _get('/' + nom)
        assert r.headers.get('Content-Encoding') == 'gzip', nom
        assert gzip.decompress(r.data) == open(chemin, 'rb').read(), nom


def test_la_longueur_annoncee_est_celle_du_corps_compresse():
    """Un Content-Length resté sur la taille d'origine tronquerait la
    réponse ou la ferait attendre indéfiniment."""
    nom = os.path.basename(_js_du_depot()[0])
    r = _get('/' + nom)
    assert int(r.headers['Content-Length']) == len(r.data)


def test_la_compression_gagne_vraiment_sur_le_javascript():
    """Une compression qui ne gagne rien ne vaut pas son coût processeur.
    Le chiffre n'est pas écrit : il est mesuré sur le dépôt réel."""
    total_clair = total_gz = 0
    for chemin in _js_du_depot()[:8]:
        r = _get('/' + os.path.basename(chemin))
        total_clair += os.path.getsize(chemin)
        total_gz += len(r.data)
    assert total_gz < total_clair * 0.55, (
        'le JavaScript ne gagne que %d %% à la compression'
        % (100 - 100 * total_gz // total_clair))


# ──────────────────────────────────────────────────────────────────────
# CE QUE LE CROCHET DOIT LAISSER TRANQUILLE
# ──────────────────────────────────────────────────────────────────────

def test_un_client_qui_ne_sait_pas_lire_gzip_recoit_le_fichier_en_clair():
    chemin = _js_du_depot()[0]
    r = _get('/' + os.path.basename(chemin), gzip_accepte=False)
    assert not r.headers.get('Content-Encoding')
    assert r.data == open(chemin, 'rb').read()


def test_vary_previent_les_caches_intermediaires():
    """Sans `Vary: Accept-Encoding`, un cache intermédiaire servirait la
    version compressée à un client qui ne sait pas la lire."""
    r = _get('/' + os.path.basename(_js_du_depot()[0]))
    assert 'accept-encoding' in (r.headers.get('Vary') or '').lower()


def test_une_reponse_trop_courte_nest_pas_compressee():
    """En dessous d'un paquet réseau, l'en-tête gzip coûte plus qu'il ne
    rend. On monte une route réelle et on la sert par le vrai crochet."""
    r = _get('/_recette_compression_court')
    assert r.status_code == 200
    assert not r.headers.get('Content-Encoding')


def test_un_vrai_flux_nest_pas_rassemble_en_memoire():
    """`is_streamed` recouvre deux choses : un fichier sur disque (borné,
    lisible) et un générateur (qu'on ne bufferise pas — le lire jusqu'au bout
    annulerait sa raison d'être). Le crochet ne doit toucher qu'au premier."""
    r = _get('/_recette_compression_flux')
    assert r.status_code == 200
    assert len(r.data) > application._GZIP_MIN, (
        'le flux de recette est trop court : il serait écarté par le seuil, '
        'et ce contrôle ne mesurerait plus rien')
    assert not r.headers.get('Content-Encoding'), (
        'un flux a été rassemblé en mémoire pour être compressé')


def test_une_image_nest_pas_compressee():
    """Un JPEG est déjà compressé : le repasser au gzip coûte du processeur
    et rend des octets en plus."""
    r = _get('/hero-bg.jpg')
    if r.status_code != 200:
        pytest.skip('hero-bg.jpg absent du dépôt')
    assert not r.headers.get('Content-Encoding')


# ──────────────────────────────────────────────────────────────────────
# CE QUE LA COMPRESSION NE DOIT PAS CASSER
# ──────────────────────────────────────────────────────────────────────

def test_la_revisite_recoit_toujours_un_304_sans_corps():
    """L'étiquette ETag n'est pas touchée, et c'est voulu : Flask évalue
    If-None-Match avant le crochet. Y ajouter un suffixe casserait le 304 —
    c'est-à-dire le gain le plus important des deux."""
    nom = os.path.basename(_js_du_depot()[0])
    r1 = _get('/' + nom)
    etag = r1.headers.get('ETag')
    assert etag, '%s est servi sans ETag : chaque revisite retélécharge tout' % nom
    r2 = _get('/' + nom, **{'If-None-Match': etag})
    assert r2.status_code == 304
    assert r2.data == b''


def test_une_reponse_dapi_calculee_arrive_compressee():
    """Le JavaScript n'est pas seul à voyager : les réponses JSON aussi, et
    elles ne viennent d'aucun fichier — elles empruntent l'autre chemin du
    crochet, celui qui ne garde rien en mémoire."""
    cl = _client()
    with cl.session_transaction() as s:
        s['is_conseilprev'] = True
    _IP[0] += 1
    r = cl.get('/api/datacentres',
               headers={'Accept-Encoding': 'gzip',
                        'X-Forwarded-For': '203.0.113.%d' % (_IP[0] % 250 + 1)})
    if r.status_code != 200:
        pytest.skip('/api/datacentres indisponible (%s)' % r.status_code)
    assert r.headers.get('Content-Encoding') == 'gzip'
    clair = gzip.decompress(r.data)
    assert len(clair) > len(r.data) * 2, 'le JSON gagne moins de moitié'
    import json
    assert isinstance(json.loads(clair), (dict, list))


def test_les_pages_html_restent_compressees():
    """`_serve_page_fast` compressait déjà le HTML. Le nouveau crochet ne
    doit pas le doubler ni le défaire."""
    r = _get('/')
    assert r.status_code == 200
    assert r.headers.get('Content-Encoding') == 'gzip'
    assert gzip.decompress(r.data)[:200].lower().count(b'<!doctype') == 1


# ──────────────────────────────────────────────────────────────────────
# LA MÉMOIRE DE COMPRESSION
# ──────────────────────────────────────────────────────────────────────

class _EspionGzip:
    """Le module `gzip`, à ceci près qu'il compte ses compressions.

    COMPTER LES APPELS, PAS LE CONTENU DU CACHE. Une première version de ce
    contrôle vérifiait que le cache contenait une entrée après deux requêtes.
    Une mutation y a survécu : un code qui ÉCRIT dans le cache sans jamais le
    RELIRE laisse exactement une entrée et recomprime à chaque fois. La taille
    du cache ne mesurait donc pas ce qu'elle prétendait."""

    def __init__(self, compteur):
        self._c = compteur

    def __getattr__(self, nom):          # tout le reste du module, inchangé
        return getattr(gzip, nom)

    def compress(self, data, *a, **kw):
        self._c['n'] += 1
        return gzip.compress(data, *a, **kw)


@pytest.fixture
def compressions(monkeypatch):
    c = {'n': 0}
    monkeypatch.setattr(application, 'gzip', _EspionGzip(c))
    return c


def test_un_fichier_stable_nest_compresse_quune_fois(compressions):
    """Comprimer sentinel.page.js coûte 36 ms au niveau 5. Le refaire à
    chaque requête pour un fichier qui ne change qu'au déploiement serait du
    processeur brûlé."""
    nom = os.path.basename(_js_du_depot()[0])
    application._GZIP_CACHE.clear()
    a = _get('/' + nom)
    assert a.headers.get('Content-Encoding') == 'gzip'
    assert compressions['n'] == 1, 'le fichier n\'a pas été compressé'
    b = _get('/' + nom)
    assert compressions['n'] == 1, (
        'le fichier a été recomprimé alors qu\'il n\'a pas changé')
    assert a.data == b.data


def test_un_fichier_qui_change_est_recompresse():
    """La signature est prise sur Last-Modified et la longueur : un fichier
    remplacé doit repartir au compresseur, sinon un déploiement servirait
    l'ancienne version."""
    application._GZIP_CACHE.clear()
    d1 = _gz_par_signature(('/x.js', 'lun, 01 jan 2024', 5000), b'AAAA' * 2000)
    d2 = _gz_par_signature(('/x.js', 'mar, 02 jan 2024', 5000), b'BBBB' * 2000)
    assert d1 != d2
    assert gzip.decompress(d2) == b'BBBB' * 2000


def test_une_reponse_calculee_a_la_volee_nencombre_pas_la_memoire():
    """Une réponse d'API change à chaque appel : la garder ferait grossir la
    mémoire sans jamais servir."""
    application._GZIP_CACHE.clear()
    _gz_par_signature(None, b'CCCC' * 2000)
    assert application._GZIP_CACHE == {}


def test_la_memoire_est_bornee():
    """Un dépôt qui grandirait sans fin ne doit pas emporter le processus."""
    application._GZIP_CACHE.clear()
    for i in range(application._GZIP_CACHE_MAX + 3):
        _gz_par_signature(('/f%d.js' % i, 'lun', 4000), b'D' * 4000)
    assert len(application._GZIP_CACHE) <= application._GZIP_CACHE_MAX


def _gz_par_signature(cle, data):
    return application._gz_memo(cle, data)


# ──────────────────────────────────────────────────────────────────────
# LE CROCHET EST-IL SEULEMENT BRANCHÉ ?
# ──────────────────────────────────────────────────────────────────────

def test_le_crochet_est_enregistre_sur_lapplication():
    """Un contrôle qui prouve que la règle fonctionne ne prouve pas qu'elle
    s'exécute. Celui-ci lit la liste des crochets de Flask."""
    noms = [f.__name__ for f in
            application.app.after_request_funcs.get(None, [])]
    assert 'compresser_texte' in noms
