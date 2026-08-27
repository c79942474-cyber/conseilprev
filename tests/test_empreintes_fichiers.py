"""VINGT-NEUF ALLERS-RETOURS POUR DEMANDER LA PERMISSION DE NE RIEN FAIRE.

CE QUI A DÉCLENCHÉ CE FICHIER. Une session Sentinel ordinaire, mesurée dans le
journal d'accès de gunicorn — première visite, seconde visite, puis ouverture
des quatre modules cartographiques :

    10×  /fleches.js
     8×  /figures_export.js
     8×  /drapeaux.js
     6×  /factcheck.js
     2×  /sentinel.page.js
    ───
    34 requêtes, dont 29 réponses « 304 — rien n'a changé »

Le navigateur avait ces fichiers. Il a quand même demandé au serveur, vingt-neuf
fois, s'il pouvait s'en servir. `Cache-Control: no-cache` n'interdit pas de
GARDER une réponse, il interdit de la SERVIR sans demander : le corps ne repart
pas, mais l'aller-retour est payé plein tarif — quarante millisecondes depuis
un navigateur français vers Francfort.

CE QU'ON NE POUVAIT PAS FAIRE : allonger le cache. Un `max-age` long sur
`/sentinel.page.js` rendrait toute mise en ligne invisible pendant sa durée.
La raison pour laquelle le cache était court était bonne.

CE QU'ON A FAIT À LA PLACE. La question « ce fichier a-t-il changé ? » est
déplacée dans l'ADRESSE : `/sentinel.page.js?v=c666d434d6`. Une adresse qui
porte sa version se garde un an sans risque, parce qu'elle ne désignera jamais
un autre contenu. Après : 5 requêtes, aucun 304.

CE QUE CES CONTRÔLES NE PEUVENT PAS FAIRE. Rejouer la session : il n'y a pas de
navigateur ici. Ils vérifient les trois propriétés dont tout le reste dépend —
qu'une empreinte SUIT le fichier, qu'une adresse au long cours porte la BONNE
empreinte, et que les pages HTML, elles, continuent de revalider. Si l'une des
trois cède, le raccourci d'un an devient un fichier figé chez le visiteur.
"""
import io
import os
import re
import sys
import time

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
os.environ.setdefault('FLASK_SECRET_KEY', 'recette-empreintes')

import empreintes  # noqa: E402
import app as application  # noqa: E402

SOURCE = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()

_IP = [40]


def _get(chemin, connecte=False):
    _IP[0] += 1
    c = application.app.test_client()
    if connecte:
        # Sentinel est derriere un verrou : sans session, la page repond une
        # redirection vers /login, et un controle qui lirait CETTE reponse
        # passerait sans jamais regarder la page visee.
        with c.session_transaction() as s:
            s['is_conseilprev'] = True
    return c.get(
        chemin,
        headers={'X-Forwarded-For': '198.51.100.%d' % (_IP[0] % 250 + 1),
                 'User-Agent': 'Mozilla/5.0 (recette)',
                 'Accept-Encoding': 'gzip'})


def _html(r):
    corps = r.get_data()
    if r.headers.get('Content-Encoding') == 'gzip':
        import gzip
        corps = gzip.decompress(corps)
    return corps.decode('utf-8', 'replace')


# ── L'EMPREINTE SUIT LE FICHIER ──────────────────────────────────────────

def test_une_empreinte_change_quand_le_fichier_change(tmp_path):
    """LA PROPRIÉTÉ SUR LAQUELLE TOUT REPOSE. Si l'empreinte ne bougeait pas,
    une mise en ligne resterait invisible un an chez chaque visiteur."""
    f = tmp_path / 'essai.js'
    f.write_text('un')
    piste = os.path.join(ICI, 'essai_empreinte_recette.js')
    try:
        io.open(piste, 'w').write('un')
        v1 = empreintes.version('/essai_empreinte_recette.js')
        assert v1
        time.sleep(0.01)
        io.open(piste, 'w').write('deux — contenu different')
        v2 = empreintes.version('/essai_empreinte_recette.js')
        assert v2 and v2 != v1, (
            "le fichier a changé, l'empreinte non : la mise en ligne serait "
            "invisible pendant un an")
    finally:
        if os.path.exists(piste):
            os.remove(piste)


def test_les_deux_criteres_comptent(tmp_path):
    """L'HORODATAGE SEUL NE SUFFIT PAS, ET LA TAILLE SEULE NON PLUS.

    Le contrôle précédent réécrit le fichier : l'horodatage change en même
    temps que la taille, et il passerait donc même si l'empreinte ignorait
    l'une des deux — une mutation l'a montré. On isole ici chaque critère.

    POURQUOI GARDER LES DEUX. La granularité de l'horodatage dépend du système
    de fichiers, et une mise en ligne qui restaure les dates (rsync, copie
    d'archive) laisserait deux contenus différents avec la même date. La
    taille seule ne voit pas une correction d'un caractère par un autre."""
    piste = os.path.join(ICI, 'essai_criteres_recette.js')
    try:
        io.open(piste, 'w').write('abcdefghij')
        st = os.stat(piste)
        v_ref = empreintes.version('/essai_criteres_recette.js')

        # Même horodatage, taille différente.
        io.open(piste, 'w').write('abcdefghij + plus long')
        os.utime(piste, ns=(st.st_atime_ns, st.st_mtime_ns))
        assert empreintes.version('/essai_criteres_recette.js') != v_ref, (
            "l'empreinte ignore la taille : deux contenus de dates identiques "
            "partageraient la même adresse")

        # Même taille, horodatage différent.
        io.open(piste, 'w').write('abcdefghij')
        os.utime(piste, ns=(st.st_atime_ns, st.st_mtime_ns + 10 ** 9))
        assert empreintes.version('/essai_criteres_recette.js') != v_ref, (
            "l'empreinte ignore l'horodatage")
    finally:
        if os.path.exists(piste):
            os.remove(piste)


def test_une_empreinte_ne_change_pas_toute_seule():
    """L'inverse est aussi coûteux : une empreinte instable annulerait tout le
    bénéfice, chaque page annonçant une adresse jamais vue."""
    a = empreintes.version('/sentinel.page.js')
    b = empreintes.version('/sentinel.page.js')
    assert a == b and a


def test_aucune_empreinte_nest_inventee():
    """Un fichier absent du disque garde son adresse telle quelle : mieux vaut
    l'ancien comportement qu'une adresse fabriquée."""
    assert empreintes.version('/ce-fichier-nexiste-pas.js') is None
    assert empreintes.version('') is None


def test_une_adresse_ne_peut_pas_sortir_du_dossier():
    """`?v=` se calcule à partir d'un chemin venu de la requête. Un chemin qui
    remonte l'arborescence n'a rien à faire ici.

    L'ÉCHANTILLON EST CHOISI POUR QUE LA RÈGLE MORDE. `/../app.py` retombe sur
    `/home/user/app.py`, qui n'existe pas : le contrôle passerait tout seul,
    par accident, même sans garde-fou — une mutation l'a montré. Le chemin
    ci-dessous, lui, REMONTE PUIS REDESCEND et désigne un fichier bien réel."""
    dossier = os.path.basename(ICI)
    assert empreintes.version('/../%s/app.py' % dossier) is None, (
        "un chemin qui remonte l'arborescence est accepté")
    assert empreintes.version('/../../etc/passwd') is None


# ── LE MARQUAGE NE TOUCHE QUE CE QUI EST À NOUS ──────────────────────────

def test_les_scripts_locaux_sont_marques():
    html = '<script src="/sentinel.page.js" defer></script>'
    sorti = empreintes.marquer(html)
    assert re.search(r'/sentinel\.page\.js\?v=[0-9a-f]{10}"', sorti), sorti


@pytest.mark.parametrize('html', [
    # CELUI-CI EST LE SEUL QUI METTE LA RÈGLE À L'ÉPREUVE : il se TERMINE par
    # « .css ». L'adresse Google Fonts, elle, finit par « wght@400 » et ne peut
    # de toute façon pas correspondre — un contrôle qui ne montrerait qu'elle
    # passerait même sans garde-fou. Une mutation l'a démasqué.
    '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">',
    '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>',
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400">',
])
def test_une_adresse_externe_nest_pas_touchee(html):
    """Marquer une feuille distante casserait son adresse — et prétendrait
    connaître la version d'un fichier qui n'est pas chez nous."""
    assert empreintes.marquer(html) == html


def test_une_adresse_relative_nest_pas_touchee():
    """On ne sait pas à quoi elle se résout : l'empreinte serait fausse une
    fois sur deux."""
    for html in ('<script src="./relatif.js"></script>',
                 '<script src="sous/dossier.js"></script>'):
        assert empreintes.marquer(html) == html


def test_un_fichier_absent_garde_son_adresse():
    html = '<script src="/pas-la.js"></script>'
    assert empreintes.marquer(html) == html


def test_les_images_ne_sont_pas_marquees():
    """On s'en tient au JavaScript et aux feuilles de style : ce sont eux que
    la mesure a montrés revalidés en boucle, et eux dont une version périmée
    casse la page. Élargir sans mesurer serait deviner.

    L'IMAGE CITÉE EXISTE SUR LE DISQUE, et c'est le point : avec un fichier
    absent, l'adresse resterait intacte de toute façon, faute d'empreinte à
    calculer — le contrôle passerait sans rien vérifier."""
    assert os.path.exists(os.path.join(ICI, 'hero-bg.jpg'))
    html = '<img src="/hero-bg.jpg">'
    assert empreintes.marquer(html) == html


# ── CE QUE LE SERVEUR RÉPOND ─────────────────────────────────────────────

@pytest.mark.parametrize('chemin,script,connecte', [
    ('/sentinel', 'sentinel.page.js', True),
    ('/', 'index.page.js', False),
])
def test_la_page_annonce_bien_des_adresses_versionnees(chemin, script, connecte):
    """Bout en bout : c'est le HTML servi, pas la fonction isolée, qui décide
    de ce que le navigateur demande. Une page publique et une page derrière le
    verrou : elles ne passent pas par le même chemin de service."""
    r = _get(chemin, connecte=connecte)
    assert r.status_code == 200, "%s a répondu %d" % (chemin, r.status_code)
    assert script + '?v=' in _html(r), (
        "%s appelle encore %s sans empreinte : chaque visite repaiera un "
        "aller-retour de revalidation" % (chemin, script))


def test_une_adresse_avec_la_bonne_empreinte_se_garde_un_an():
    v = empreintes.version('/sentinel.page.js')
    r = _get('/sentinel.page.js?v=' + v)
    assert r.status_code == 200
    assert r.headers.get('Cache-Control') == empreintes.IMMUABLE, (
        "reçu « %s »" % r.headers.get('Cache-Control'))


def test_une_empreinte_perimee_ne_fige_rien():
    """LE CONTRÔLE QUI ÉVITE LE PIRE. Servir un an une adresse dont l'empreinte
    ne correspond plus figerait un contenu périmé chez le visiteur, sans aucun
    moyen de le rattraper."""
    r = _get('/sentinel.page.js?v=0000000000')
    assert r.headers.get('Cache-Control') != empreintes.IMMUABLE


def test_une_adresse_sans_empreinte_garde_le_comportement_davant():
    """Une page très ancienne gardée par un intermédiaire, une adresse
    recopiée à la main : elles doivent continuer de fonctionner comme avant."""
    r = _get('/sentinel.page.js')
    assert r.status_code == 200
    assert r.headers.get('Cache-Control') != empreintes.IMMUABLE


def test_les_pages_html_revalident_toujours():
    """C'EST LA CONDITION DU RACCOURCI. Le cache d'un an n'est sans risque que
    parce que la page qui NOMME l'adresse, elle, est revalidée à chaque visite :
    c'est là que la nouvelle version est annoncée."""
    r = _get('/sentinel', connecte=True)
    assert r.status_code == 200
    cc = r.headers.get('Cache-Control') or ''
    assert 'no-cache' in cc, (
        "la page Sentinel ne revalide plus (« %s ») : une mise en ligne "
        "resterait invisible" % cc)
    assert empreintes.IMMUABLE not in cc


def test_le_marquage_est_pose_dans_le_cache_de_pages():
    """Une fois par version de fichier, jamais par visite : posé ailleurs, ce
    serait une expression régulière sur 693 Ko à chaque requête."""
    i = SOURCE.index('def _page_cache_entry(')
    corps = SOURCE[i:SOURCE.index('\ndef _serve_page_fast', i)]
    assert 'empreintes.marquer(' in corps


def test_seules_les_lectures_beneficient_du_raccourci():
    """Un POST vers la même adresse ne doit pas hériter d'un cache d'un an."""
    i = SOURCE.index('empreintes.immuable(request.path')
    fenetre = SOURCE[max(0, i - 260):i]
    assert "request.method in ('GET', 'HEAD')" in fenetre
    assert 'response.status_code == 200' in fenetre


@pytest.mark.parametrize('duree', [31536000])
def test_le_raccourci_dure_un_an_et_le_dit(duree):
    assert 'max-age=%d' % duree in empreintes.IMMUABLE
    assert 'immutable' in empreintes.IMMUABLE
    assert 'public' in empreintes.IMMUABLE
