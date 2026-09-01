"""La récupération de DCWatch : figée sur l'étiquette, et qui dit quand l'amont bouge.

CE QUI A DÉCLENCHÉ CE FICHIER. La base était déposée à la main, sans aucun
chemin de retour vers sa source, et son empreinte ne vivait que dans la prose
d'un fichier d'attribution. GitLab est désormais joignable : la récupération est
branchée — mais la manière compte plus que le branchement.

CE QUE CES RÈGLES PROTÈGENT :

  1. UNE ÉTIQUETTE DE VERSION NE BOUGE PAS QUAND LA DONNÉE BOUGE. Le fichier
     déposé est identique, octet pour octet, à celui de l'étiquette amont
     2026.04.09 — et pourtant le HEAD de `main` porte trois enregistrements de
     plus, un site en exploitation de MOINS, et un doublon de plus, sous le
     même numéro de version. Se fier au libellé laisserait croire à une base à
     jour. L'empreinte entre donc dans le code, et une règle la vérifie.

  2. AUCUN MODULE IMPORTABLE N'OUVRE DE SOCKET. `app.py` importe `dcwatch` au
     démarrage : un appel réseau posé là ferait dépendre le démarrage du
     service de la disponibilité de GitLab, et la suite de tests d'une
     politique réseau. Le contrôle porte sur l'ARBRE des imports, et il
     manquait à `peeringdb_import.py`, qui tenait la règle sans la garder.

  3. LE TABLEAU D'ATTRIBUTION DÉCRIVAIT LA BASE DE MÉMOIRE. Version, empreinte
     et nombre d'enregistrements étaient saisis à la main : rien n'empêchait le
     fichier de changer sans que le tableau bouge — et c'est le tableau qu'on
     aurait cru.

  4. UNE RECETTE MUETTE SE LIT COMME UN CONTRÔLE VERT. Réseau refusé, base
     absente : elle doit le dire et sortir en échec.

  5. UN RAFRAÎCHISSEMENT SILENCIEUX. « Environ trois cent cinquante » se lit
     aujourd'hui sur 342 lignes en exploitation ; l'amont en porte 341. La
     recette compare, elle ne dépose pas.
"""
import ast
import io
import os
import subprocess
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import dcwatch  # noqa: E402
import dcwatch_import as I  # noqa: E402

DOSSIER = os.path.join(ICI, 'dcwatch')

pytestmark = pytest.mark.skipif(not dcwatch.disponible(),
                                reason="base DCWatch non déposée")


def _octets():
    with open(os.path.join(DOSSIER, I.FICHIER), 'rb') as f:
        return f.read()


# ── 1. Ce qu'on demande, et où ─────────────────────────────────────────────

def test_l_url_nomme_l_etiquette_et_echappe_le_projet():
    """Le chemin du projet contient un slash : non échappé, il coupe l'URL en
    deux segments et l'appel part sur une autre route de l'API."""
    u = I.url('2026.04.09')
    assert u.startswith('https://gitlab.com/api/v4/projects/')
    assert 'hubblo%2Fdatacenter-watch' in u
    assert 'hubblo/datacenter-watch' not in u
    assert u.endswith('/export_summary.csv/raw?ref=2026.04.09')


def test_l_url_sert_aussi_bien_une_branche_qu_une_etiquette():
    """C'est ce qui permet de comparer l'étiquette figée et le HEAD de main
    sans deux chemins de code — et deux chemins divergeraient."""
    assert I.url('main').endswith('ref=main')
    assert I.url('2026.03.26').endswith('ref=2026.03.26')


# ── 2. L'empreinte, dans le code ───────────────────────────────────────────

def test_le_depot_a_l_empreinte_inscrite_dans_le_code():
    v = I.verifier(_octets(), dcwatch.EMPREINTE)
    assert v['conforme'], (
        "le fichier déposé ne correspond plus à dcwatch.EMPREINTE : la base a "
        "été remplacée, tronquée, ou rafraîchie sans décision (%s attendu, %s obtenu)"
        % (v['attendue'][:16], v['obtenue'][:16]))


def test_l_attribution_enonce_la_meme_empreinte_que_le_code():
    """Deux copies d'une même valeur dérivent ; ce contrôle est le seul lien
    entre le tableau markdown et la constante du module."""
    texte = io.open(os.path.join(DOSSIER, 'ATTRIBUTION.md'), encoding='utf-8').read()
    assert dcwatch.EMPREINTE in texte


def test_l_etat_signale_un_depot_qui_a_change(monkeypatch):
    """La discrimination : sans elle, `etat()` dirait « conforme » quoi qu'il
    arrive et ne mesurerait rien."""
    assert dcwatch.etat()['empreinte_conforme'] is True
    monkeypatch.setattr(dcwatch, 'EMPREINTE', 'f' * 64)
    e = dcwatch.etat()
    assert e['empreinte_conforme'] is False
    assert 'A CHANGE' in e['dit']


def test_le_drapeau_sort_avec_les_chiffres_servis(monkeypatch):
    """Un dépôt remplacé doit se voir LÀ OÙ LES CHIFFRES SONT SERVIS, pas
    seulement dans une fonction que personne n'appelle.

    ET IL DOIT SUIVRE L'ÉTAT, PAS ÊTRE VRAI. Une première version se contentait
    d'`assert ... is True` : câbler le drapeau à `True` dans `couverture()` la
    laissait verte. Une règle qui vérifie une valeur au lieu d'une propriété ne
    garde rien — c'est la mutation qui l'a montré."""
    assert dcwatch.couverture()['empreinte_conforme'] is True
    monkeypatch.setattr(dcwatch, 'EMPREINTE', 'f' * 64)
    assert dcwatch.couverture()['empreinte_conforme'] is False, (
        "le drapeau ne suit pas l'état du dépôt : il est câblé")


# ── 3. Le résumé compare des conséquences, pas des octets ──────────────────

def test_le_resume_compte_ce_qui_est_publie():
    r = I.resume(_octets())
    assert r['enregistrements'] == 520
    assert r['france'] == 427
    assert r['exploitation'] == 342
    assert r['doublons_france'] == 2, (
        "les doublons ne sont plus comptés : le parc français ressortirait à "
        "342 sites au lieu de 340")


def test_le_resume_ne_rend_aucune_ligne():
    """La règle de fond du module ODbL vaut pour le nouveau : des comptes, pas
    des enregistrements."""
    r = I.resume(_octets())
    for cle, v in r.items():
        assert isinstance(v, int), "%s rend autre chose qu'un compte" % cle


def test_la_comparaison_discrimine():
    """Un résumé identique sur deux fichiers différents ne mesurerait rien."""
    octets = _octets()
    lignes = octets.split(b'\n')
    ampute = b'\n'.join(lignes[:-40])
    c = I.comparer(octets, ampute)
    assert c['identiques'] is False
    assert c['ecarts'], "aucun écart relevé entre deux fichiers différents"
    assert c['ecarts']['enregistrements'] < 0


def test_deux_exemplaires_identiques_ne_montrent_aucun_ecart():
    c = I.comparer(_octets(), _octets())
    assert c['identiques'] is True
    assert c['ecarts'] == {}


# ── 4. Le tableau d'attribution est calculé, pas saisi ─────────────────────

def test_le_tableau_regenere_est_celui_du_fichier():
    """S'il ne l'était pas, il décrirait une base qui n'est plus là — et c'est
    le tableau qu'on croirait."""
    texte = io.open(os.path.join(DOSSIER, 'ATTRIBUTION.md'), encoding='utf-8').read()
    i, j = texte.find(I.MARQUE_DEBUT), texte.find(I.MARQUE_FIN)
    assert i >= 0 and j > i, "les marqueurs du tableau ont disparu"
    actuel = texte[i:j + len(I.MARQUE_FIN)]
    assert actuel == I.table_attribution(_octets()), (
        "le tableau d'attribution ne décrit plus le fichier déposé")


def test_le_remplacement_ne_touche_pas_a_la_prose():
    """Le raisonnement sur les articles 4.3 à 4.8 est écrit à la main : le
    générer le fragiliserait."""
    texte = io.open(os.path.join(DOSSIER, 'ATTRIBUTION.md'), encoding='utf-8').read()
    neuf = I.remplacer_table(texte, I.table_attribution(_octets()))
    assert neuf == texte, "la régénération n'est pas idempotente"
    for phrase in ('Section 4.4', 'Produced Work', 'ODbL'):
        assert phrase in neuf, "la régénération a emporté la prose : « %s »" % phrase


def test_l_attribution_dit_ce_qui_est_entre_au_referentiel():
    """LA PHRASE QUI ÉTAIT DEVENUE FAUSSE. Elle affirmait que le référentiel
    servi ne portait aucune valeur venue d'ici, après que cinq points y furent
    entrés. Une mention qui décrit autre chose que la réalité vaut moins que
    pas de mention."""
    texte = io.open(os.path.join(DOSSIER, 'ATTRIBUTION.md'), encoding='utf-8').read()
    assert 'ne porte\naucune valeur venue d\'ici' not in texte
    assert 'point_source' in texte, "l'emprunt n'est pas dit là où on le cherche"
    for commune in ('Val-de-Reuil', 'Prévessin-Moëns', 'Bruges'):
        assert commune in texte


# ── 5. Aucun module importable n'ouvre de socket ───────────────────────────

RESEAU = ('requests', 'urllib', 'urllib3', 'http', 'httpx', 'socket', 'aiohttp',
          'ftplib', 'telnetlib')


@pytest.mark.parametrize('module', ['dcwatch.py', 'dcwatch_import.py', 'parc_fr.py',
                                    'peeringdb_import.py'])
def test_aucun_module_importable_n_ouvre_de_socket(module):
    """`app.py` importe `dcwatch` au démarrage. Un appel réseau posé dans un
    module importable ferait dépendre le démarrage du service de GitLab, et la
    suite de tests d'une politique réseau.

    LA RÈGLE MANQUAIT À `peeringdb_import.py`, qui tenait la discipline dans son
    en-tête sans que rien ne la garde : elle y est étendue."""
    arbre = ast.parse(io.open(os.path.join(ICI, module), encoding='utf-8').read())
    fautifs = []
    for n in ast.walk(arbre):
        noms = []
        if isinstance(n, ast.Import):
            noms = [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom):
            noms = [n.module or '']
        for nom in noms:
            if nom.split('.')[0] in RESEAU:
                fautifs.append(nom)
    assert not fautifs, (
        "%s importe %s : la lecture réseau doit rester dans une recette lancée "
        "à la main" % (module, ', '.join(fautifs)))


def test_l_appel_reseau_est_confine_dans_une_seule_fonction():
    """Un `urlopen` dispersé dans le corps du script rendrait les contrôles
    dépendants de l'ordre d'exécution, et la gestion du refus impossible à
    tenir en un seul endroit."""
    arbre = ast.parse(io.open(os.path.join(ICI, 'recette_dcwatch_amont.py'),
                              encoding='utf-8').read())
    porteuses = set()
    for f in ast.walk(arbre):
        if not isinstance(f, ast.FunctionDef):
            continue
        for n in ast.walk(f):
            if isinstance(n, ast.Attribute) and n.attr == 'urlopen':
                porteuses.add(f.name)
    assert porteuses == {'telecharger'}, (
        "l'appel réseau sort de `telecharger` : %s" % (porteuses or 'introuvable'))


# ── 6. La recette compare, elle ne dépose pas ──────────────────────────────

def test_la_recette_ne_depose_rien_sans_qu_on_le_demande():
    """Un rafraîchissement silencieux déplacerait des chiffres déjà publiés :
    342 sites en exploitation deviendraient 341."""
    arbre = ast.parse(io.open(os.path.join(ICI, 'recette_dcwatch_amont.py'),
                              encoding='utf-8').read())
    appels = [n for n in ast.walk(arbre)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
              and n.func.id == 'deposer']
    assert len(appels) == 1, "deposer() est appelée %d fois" % len(appels)
    # ET L'APPEL DOIT ÊTRE SOUS LA CONDITION, pas ailleurs dans le fichier :
    # une version qui appellerait `deposer` en dehors du `if` satisferait un
    # simple comptage tout en déposant à chaque exécution.
    sous_condition = [
        n for n in ast.walk(arbre) if isinstance(n, ast.If)
        and '--deposer' in ast.unparse(n.test)
        and any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                and c.func.id == 'deposer' for c in ast.walk(n))]
    assert sous_condition, (
        "l'appel à deposer() n'est pas sous la condition `--deposer` : la "
        "recette écraserait la base à chaque exécution")


def test_la_recette_refuse_de_se_taire_sans_base(tmp_path):
    """ÉPROUVÉE POUR DE VRAI, pas lue. Une première version de cette règle
    acceptait « 0 ou 1 » comme code de sortie : elle ne vérifiait rien. La
    recette est ici lancée sur un dossier VIDE — elle doit sortir en échec et
    dire qu'elle n'a rien pu comparer."""
    faux = tmp_path / 'depot-vide'
    faux.mkdir()
    r = subprocess.run([sys.executable, os.path.join(ICI, 'recette_dcwatch_amont.py')],
                       capture_output=True, text=True, timeout=180,
                       env=dict(os.environ, DCWATCH_DOSSIER=str(faux)))
    assert r.returncode == 1, (
        "sans base, la recette sort en succès : un contrôle muet se lit comme "
        "un contrôle vert\n%s" % r.stdout[-600:])
    assert 'rien a comparer' in r.stdout
    assert 'vert' not in r.stdout.split('rien a comparer')[0].replace('KO', '')


@pytest.mark.skipif(os.environ.get('RECETTE_RESEAU') != '1',
                    reason="appel réseau : RECETTE_RESEAU=1 pour l'exécuter")
def test_la_recette_passe_de_bout_en_bout_quand_le_reseau_repond():
    """LA SUITE RESTE HERMÉTIQUE, ET C'EST DÉLIBÉRÉ. Tout le reste de ce fichier
    tourne sans réseau ; cette règle-ci sort du poste, donc elle ne s'exécute
    que sur demande — `RECETTE_RESEAU=1 python3 -m pytest tests`. Une suite qui
    interroge GitLab à chaque passage se met à échouer pour des raisons qui ne
    la regardent pas, et on finit par ne plus la croire."""
    r = subprocess.run([sys.executable, os.path.join(ICI, 'recette_dcwatch_amont.py')],
                       capture_output=True, text=True, timeout=240)
    assert r.returncode == 0, r.stdout[-900:]
    assert 'tout est vert' in r.stdout
    assert 'ODbL' in r.stdout
    assert 'Aucun depot' in r.stdout, "la recette a déposé sans qu'on le demande"
