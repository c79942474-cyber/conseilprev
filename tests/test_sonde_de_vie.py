"""LA SONDE DE VIE ET LE DÉPLOIEMENT — deux déclarations qui doivent se tenir.

LA FAUTE, ET CE QU'ELLE COÛTAIT. Une fonction `health()` était déclarée sur
`/api/health`, adresse déjà prise quelques milliers de lignes plus haut par
`health_check`, le diagnostic complet. Flask accepte deux règles pour une même
URL quand leurs points d'entrée diffèrent, et sert la PREMIÈRE enregistrée :
cette fonction n'a donc jamais répondu. Aucune erreur ne le signalait, aucun
contrôle ne la joignait, et elle annonçait au passage une version « 8.0 »
écrite à la main — une déclaration qui ne peut que vieillir.

CE QUE CES CONTRÔLES GARDENT :

  1. Le chemin déclaré dans `render.yaml` doit correspondre à une route qui
     RÉPOND. Une sonde de vie pointant dans le vide ferait redémarrer le
     service en boucle, et l'erreur ne serait visible que sur Render.
  2. La sonde doit rester LÉGÈRE. Render l'interroge toutes les quelques
     secondes : y brancher le diagnostic d'exploitant, qui va sonder SMTP et
     les clés d'API, ferait déclarer le service en panne pour une clé absente
     alors qu'il sert parfaitement les pages.
  3. Aucune URL ne doit porter deux routes. C'est la forme exacte du défaut
     d'origine, et elle ne se voit pas à la lecture.
  4. La région doit être déclarée. Absente, Render place le service en Oregon,
     à environ 150 ms de plus par aller-retour pour un public européen — c'est
     l'écart mesuré entre les deux domaines du cabinet.
"""
import collections
import os
import re
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
os.environ.setdefault('FLASK_SECRET_KEY', 'recette-sonde')

import app as application  # noqa: E402

YAML = open(os.path.join(ICI, 'render.yaml'), encoding='utf-8').read()


def _chemin_declare():
    """Le chemin de sonde tel que `render.yaml` le déclare — pas une copie."""
    m = re.search(r'^\s*healthCheckPath:\s*(\S+)', YAML, re.M)
    return m.group(1) if m else None


def _get(chemin):
    return application.app.test_client().get(
        chemin, headers={'X-Forwarded-For': '203.0.113.201'})


def test_le_deploiement_declare_un_chemin_de_sonde():
    assert _chemin_declare(), (
        "render.yaml ne déclare aucun healthCheckPath : Render ne saura pas "
        "distinguer un service vivant d'un service en boucle de démarrage")


def test_le_chemin_declare_repond_vraiment():
    """LE CONTRÔLE QUI AURAIT VU LA ROUTE MORTE. Il ne lit pas le code : il
    interroge l'adresse que le déploiement désigne."""
    chemin = _chemin_declare()
    r = _get(chemin)
    assert r.status_code == 200, '%s répond %s' % (chemin, r.status_code)
    assert (r.get_json() or {}).get('status') == 'ok', r.data[:120]


def test_la_sonde_reste_legere():
    """Interrogée toutes les quelques secondes, elle ne doit pas rendre une
    page. Le diagnostic d'exploitant, lui, en rend une de 3,6 Ko."""
    r = _get(_chemin_declare())
    assert r.mimetype == 'application/json', r.mimetype
    assert len(r.data) < 200, '%d octets pour une sonde de vie' % len(r.data)


def test_la_sonde_nest_pas_le_diagnostic_dexploitant():
    """Les deux existent et ne font pas le même métier. Les confondre ferait
    déclarer le service en panne pour une clé SMTP absente."""
    diag = _get('/api/health')
    assert diag.status_code == 200
    assert 'html' in (diag.mimetype or ''), (
        "/api/health ne rend plus le diagnostic : les deux rôles ont fusionné")
    assert _chemin_declare() != '/api/health'


def test_aucune_url_ne_porte_deux_routes():
    """LA FORME EXACTE DU DÉFAUT D'ORIGINE. Flask accepte deux règles sur une
    même URL quand leurs points d'entrée diffèrent, sert la première, et ne
    dit rien de la seconde."""
    par_url = collections.defaultdict(list)
    for r in application.app.url_map.iter_rules():
        # Les méthodes distinguent légitimement deux routes de même adresse
        # (un GET et un POST, par exemple) : on ne compare que ce qui se
        # recouvre vraiment.
        for m in (r.methods or set()) - {'HEAD', 'OPTIONS'}:
            par_url[(str(r), m)].append(r.endpoint)
    doublons = {k: v for k, v in par_url.items() if len(v) > 1}
    assert not doublons, (
        'des adresses portent plusieurs routes, dont une qui ne répondra '
        'jamais : %s' % doublons)


def test_la_region_est_declaree_et_europeenne():
    """Absente, Render place le service en Oregon. Le public de ce cabinet est
    européen, et l'écart se paie à chaque aller-retour."""
    m = re.search(r'^\s*region:\s*(\S+)', YAML, re.M)
    assert m, ("render.yaml ne déclare aucune région : Render retombe sur "
               "Oregon, à environ 150 ms de plus par aller-retour")
    assert m.group(1) in ('frankfurt', 'eu-central'), m.group(1)


def test_le_fichier_dit_ce_que_la_region_ne_fait_pas():
    """Une région déclarée ne DÉPLACE pas un service existant : Render la fixe
    à la création. Un fichier qui laisserait croire l'inverse ferait attendre
    un effet qui ne viendra pas.

    UNE SEULE PHRASE EST ACCEPTÉE, ET C'EST VOULU. Une première version en
    admettait deux, reliées par « ou » : la seconde parlait en réalité de la
    BASE de données, pas du service. Retirer l'avertissement sur le service
    laissait donc le contrôle vert, l'autre phrase tenant lieu de preuve pour
    une affirmation qu'elle ne faisait pas. Ce contrôle porte sur une
    formulation précise ; la reformuler doit obliger à revenir ici."""
    assert 'ne déplace pas un service existant' in YAML, (
        "render.yaml déclare une région sans dire qu'elle ne prend effet qu'à "
        "la recréation du service")
