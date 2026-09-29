# -*- coding: utf-8 -*-
"""La carte mondiale des régulations IA — sa bibliothèque et son fond de carte.

Le défaut mesuré : la carte ne tenait qu'à deux domaines tiers. Leaflet venait
d'unpkg.com, les tuiles de CARTO. Mesure au navigateur, unpkg injoignable :
`leafletCharge: false`, le repli « la carte n'a pas pu se charger » à la place
de la carte, le compteur à « carte indisponible », **0 marqueur** — alors
qu'aucune donnée ne manquait. Et si seules les TUILES tombaient, les 46
marqueurs restaient posés sur du vide, sans un mot d'explication.

Ce que ces règles mesurent, après correction :
  · la bibliothèque est servie par ce site, et la page ne nomme plus unpkg ;
  · Flask sert réellement le fichier, sa feuille et ses images de marqueurs ;
  · le fond de carte a un suppléant, et la bascule se décide sur des FAITS —
    on exécute le vrai `fondPoser` de `map.page.js` contre un Leaflet simulé.

Mesure navigateur qui a validé la correction (serveur local, /sentinel → carto,
les deux fournisseurs de tuiles injoignables) :
    leafletCharge true · repli visible false · badge « 46 juridictions »
    marqueurs 46 · fondAbsent true
    note : « Fond de carte indisponible — les juridictions et leurs données
            restent affichées et cliquables. »
"""
import json
import os
import re
import shutil
import subprocess

import pytest

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = shutil.which('node')


def _lire(nom):
    with open(os.path.join(RACINE, nom), encoding='utf-8') as f:
        return f.read()


MAP_HTML = _lire('map.html')
MAP_JS = _lire('map.page.js')


# ── 1. LA BIBLIOTHÈQUE VIENT DE CE SITE ──────────────────────────────────────

def test_la_page_de_la_carte_ne_va_plus_chercher_sa_bibliotheque_chez_un_tiers():
    """On mesure ce que la page CHARGE, pas ce qu'elle raconte : le commentaire
    qui explique d'où l'on vient a le droit de nommer unpkg, la balise non."""
    sans_commentaires = re.sub(r'<!--.*?-->', '', MAP_HTML, flags=re.S)
    charges = re.findall(r'(?:src|href)="([^"]+)"', sans_commentaires)
    fautifs = [u for u in charges if 'unpkg.com' in u]
    assert not fautifs, (
        'map.html charge encore depuis unpkg : %s — la carte retombe sous la panne '
        "d'un tiers" % fautifs)


@pytest.mark.parametrize('href', ['/vendor/leaflet/leaflet.js', '/vendor/leaflet/leaflet.css'])
def test_la_page_de_la_carte_charge_la_bibliotheque_de_la_meme_origine(href):
    assert href in MAP_HTML, 'map.html ne charge pas %s' % href


@pytest.mark.parametrize('fichier', [
    'vendor/leaflet/leaflet.js',
    'vendor/leaflet/leaflet.css',
    'vendor/leaflet/LICENSE',
    'vendor/leaflet/images/marker-icon.png',
    'vendor/leaflet/images/marker-icon-2x.png',
    'vendor/leaflet/images/marker-shadow.png',
    'vendor/leaflet/images/layers.png',
    'vendor/leaflet/images/layers-2x.png',
])
def test_le_fichier_de_la_bibliotheque_est_bien_dans_le_depot(fichier):
    chemin = os.path.join(RACINE, fichier)
    assert os.path.isfile(chemin), '%s manque : la page chargerait du vide' % fichier
    assert os.path.getsize(chemin) > 0, '%s est vide' % fichier


def test_la_bibliotheque_copiee_porte_sa_version_et_sa_licence():
    """Une bibliothèque recopiée sans sa licence est une dette juridique, et
    sans sa version on ne sait plus ce qu'on sert."""
    js = _lire('vendor/leaflet/leaflet.js')[:400]
    assert 'Leaflet 1.9.4' in js, "l'en-tête ne dit pas quelle version est servie"
    licence = _lire('vendor/leaflet/LICENSE')
    assert 'BSD 2-Clause' in licence
    assert 'Vladimir Agafonkin' in js or 'Volodymyr Agafonkin' in licence


@pytest.mark.parametrize('chemin,type_attendu', [
    ('/vendor/leaflet/leaflet.js', 'javascript'),
    ('/vendor/leaflet/leaflet.css', 'css'),
    ('/vendor/leaflet/images/marker-icon.png', 'image/png'),
])
def test_le_serveur_sert_reellement_la_bibliotheque(chemin, type_attendu):
    """Le fichier est dans le dépôt, mais c'est Flask qui décide s'il sort."""
    import app as application
    client = application.app.test_client()
    r = client.get(chemin)
    assert r.status_code == 200, '%s rend %s' % (chemin, r.status_code)
    assert type_attendu in (r.headers.get('Content-Type') or '').lower()
    assert len(r.get_data()) > 0


# ── 2. LE FOND DE CARTE A UN SUPPLÉANT ───────────────────────────────────────

#: LES SERVICES DE TUILES QUI EXIGENT UNE CLÉ. CARTO a fermé son service
#: libre : ses serveurs répondent 200, et l'image porte « API KEY REQUIRED »
#: en filigrane. Une panne qui répond 200 n'est pas une panne pour le
#: navigateur — aucun « tileerror » ne se déclenche, donc AUCUN suppléant ne
#: peut la rattraper. La seule parade est de ne pas en dépendre, et c'est
#: cette liste qui le fait tenir.
SERVICES_A_CLE = ['cartocdn.com', 'basemaps.carto', 'api.mapbox.com',
                  'tiles.stadiamaps.com', 'maptiler.com', 'thunderforest.com',
                  'api.os.uk', 'here.com']
MARQUEURS_DE_CLE = ['{apikey}', 'apikey=', 'api_key=', 'access_token=', 'key=']


def _fonds_declares():
    return re.findall(r"url:'(https://[^']+)'", MAP_JS)


def test_aucun_fond_de_carte_n_exige_de_cle_d_api():
    """Le défaut vu à l'écran : 46 pastilles posées sur un damier de filigranes
    « API KEY REQUIRED », sans aucune géographie."""
    fautifs = [u for u in _fonds_declares()
               if any(h in u.lower() for h in SERVICES_A_CLE)
               or any(m in u.lower() for m in MARQUEURS_DE_CLE)]
    assert not fautifs, (
        'fond(s) de carte servis par un service qui exige une clé : %s — les '
        'tuiles reviendront en 200 avec un filigrane, et aucun suppléant ne '
        'se déclenchera' % fautifs)


def test_le_calque_des_tuiles_est_desature_pour_laisser_la_couleur_aux_pastilles():
    """Les tuiles libres sont en couleurs, et la carte se LIT par la couleur
    des pastilles. Le filtre porte sur le calque des tuiles seul."""
    import re as _re
    m = _re.search(r'\.leaflet-tile-pane\s*\{([^}]*)\}', MAP_HTML)
    assert m, 'aucun filtre sur le calque des tuiles : le fond concurrence les pastilles'
    regle = m.group(1)
    assert 'grayscale' in regle, regle
    assert 'filter' in regle, regle


def test_le_fond_de_carte_declare_au_moins_deux_fournisseurs():
    urls = re.findall(r"url:'(https://[^']+)'", MAP_JS)
    assert len(urls) >= 2, 'un seul fond déclaré : une panne du fournisseur vide la carte'
    hotes = {u.split('/')[2].split('.', 1)[-1] for u in urls}
    assert len(hotes) >= 2, 'les fonds déclarés viennent du même hôte : %s' % sorted(hotes)


def _fond(evenements, rappels=0):
    """Exécute le VRAI `fondPoser` de map.page.js contre un Leaflet simulé, et
    rend ce qui s'est passé : les fonds posés, et la note de repli éventuelle.

    `evenements` donne, fond par fond, la suite d'événements de tuiles à jouer
    (« o » = une tuile est arrivée, « k » = une tuile a été refusée).
    `rappels` redemande la note de repli autant de fois, pour mesurer qu'elle
    n'est écrite qu'une fois même si on la redemande."""
    if not NODE:
        pytest.skip('node absent : le fond de carte ne peut pas être exécuté')
    debut = MAP_JS.index('var FONDS = [')
    fin = MAP_JS.index('fondPoser(0);') + len('fondPoser(0);')
    moteur = MAP_JS[debut:fin]
    prog = """
var poses = [], notes = [], couches = [];
var map = { removeLayer: function(){}, };
var L = { tileLayer: function(url, opts){
  var h = {};
  var c = { _url: url, _opts: opts,
    on: function(n, f){ (h[n] = h[n] || []).push(f); return c; },
    off: function(){ h = {}; return c; },
    addTo: function(){ poses.push(url); couches.push({c:c, h:h}); return c; },
    feu: function(n){ (h[n] || []).forEach(function(f){ f(); }); } };
  return c;
} };
var document = {
  getElementById: function(id){ return id === 'map' ? racine : (racine.enfants[id] || null); },
  createElement: function(){ return { id:'', setAttribute:function(){}, textContent:'' }; } };
var racine = { enfants:{}, appendChild: function(n){ racine.enfants[n.id] = n; notes.push(n.textContent); } };
%s
var SCENES = %s;
SCENES.forEach(function(scene, i){
  var u = couches[i]; if (!u) return;
  scene.split('').forEach(function(ch){ u.c.feu(ch === 'o' ? 'tileload' : 'tileerror'); });
});
for (var r = 0; r < %d; r++) fondAbsent();
console.log(JSON.stringify({ poses: poses, notes: notes }));
""" % (moteur, json.dumps(evenements), rappels)
    r = subprocess.run([NODE, '-e', prog], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail("le fond de carte ne s'exécute pas :\n%s" % (r.stderr or '')[-1500:])
    return json.loads(r.stdout.strip())


def test_le_premier_fond_est_pose_sans_rien_attendre():
    r = _fond([''])
    assert len(r['poses']) == 1, 'aucun fond posé au démarrage : %s' % r
    assert r['poses'][0] == _fonds_declares()[0]
    assert r['notes'] == [], 'une note de repli s’affiche alors que rien n’a échoué'


def test_quatre_tuiles_refusees_sans_une_seule_arrivee_font_passer_au_suppleant():
    r = _fond(['kkkk'])
    assert len(r['poses']) == 2, 'le suppléant n’a pas pris le relais : %s' % r['poses']
    assert r['poses'][1] == _fonds_declares()[1]
    assert r['poses'][1] != r['poses'][0]


def test_trois_refus_ne_suffisent_pas_a_quitter_un_fournisseur():
    """Le réseau du visiteur hoquette : ce n'est pas une panne du fournisseur."""
    r = _fond(['kkk'])
    assert len(r['poses']) == 1, 'on a changé de fond pour trois tuiles : %s' % r['poses']
    assert r['notes'] == []


def test_un_fournisseur_qui_a_deja_servi_une_tuile_n_est_plus_quitte():
    """Une tuile arrivée prouve le fournisseur : les refus qui suivent sont du
    ressort du réseau, et basculer ferait repartir tout le fond à zéro."""
    r = _fond(['okkkkkkkk'])
    assert len(r['poses']) == 1, 'on a quitté un fond qui servait : %s' % r['poses']


def test_quand_aucun_fond_ne_repond_la_carte_le_dit_au_lieu_de_se_taire():
    r = _fond(['kkkk', 'kkkk'])
    assert len(r['poses']) == 2
    assert len(r['notes']) == 1, 'aucune note alors que les deux fonds ont échoué : %s' % r
    note = r['notes'][0]
    assert 'Fond de carte indisponible' in note
    assert 'restent affich' in note, (
        'la note ne dit pas que les données, elles, sont toujours là : %r' % note)


def test_la_note_de_repli_n_est_ecrite_qu_une_fois_meme_si_on_la_redemande():
    """Le garde n'est pas décoratif : un redimensionnement, un changement de vue
    ou une seconde pose des fonds redemandera la note. Elle doit rester unique,
    sinon les mentions s'empilent les unes sur les autres au coin de la carte."""
    r = _fond(['kkkk', 'kkkk'], rappels=3)
    assert len(r['notes']) == 1, 'la note est empilée plusieurs fois : %s' % r['notes']


# ── 3. LE REPLI QUAND LA BIBLIOTHÈQUE ELLE-MÊME MANQUE ───────────────────────

def test_le_repli_sans_bibliotheque_n_accuse_plus_un_domaine_qui_n_est_plus_utilise():
    """Le message nommait unpkg.com. La bibliothèque vient désormais d'ici :
    envoyer le visiteur vérifier son accès à unpkg serait une fausse piste."""
    avant = MAP_JS[:MAP_JS.index('var map = L.map(')]
    assert 'unpkg' not in avant, 'le repli nomme encore unpkg : %s' % avant[-400:]
    assert "pas pu se charger" in avant
    assert '/panorama#s-carte' in avant, 'le repli ne propose plus de porte de sortie'
