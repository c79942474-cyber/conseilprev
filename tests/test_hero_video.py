# -*- coding: utf-8 -*-
"""L'ANIMATION « SECURITY ADVISOR — BANQUE » EN TÊTE DE L'ACCUEIL.

CE QUI A ÉTÉ DEMANDÉ : remplacer le bandeau « Gouverner et sécuriser l'IA —
invitation gratuite du 9 novembre » par l'animation fournie, EN SUPPRIMANT LA
RÉFÉRENCE BANCAIRE de 600 k€.

CE QUI A ÉTÉ FAIT, ET CE QUE CES RÈGLES MESURENT :

  1. LA SCÈNE EST COUPÉE, PAS MASQUÉE. La carte « référence bancaire » porte
     trois montants — 600 k€, « signé 480 k€ (+ 110 k€ optionnel) » — et le
     client désigné. Masquer le seul chiffre aurait laissé les deux autres.
     Les images 367 à 486 de l'original (4 s) ont été retirées ; la jonction
     se fait entre deux images vides du fondu.
     LA RÈGLE NE GARDE PAS LA SCÈNE POUR LA RECONNAÎTRE : elle garde une
     signature de 16 × 20 niveaux de gris de la carte pleine, illisible, et
     refuse toute image de la vidéo publiée qui s'en approche. Mesuré à
     l'écriture : la carte pleine reste à 2,55 au plus de sa signature, toute
     autre image de l'original ou de la vidéo publiée à 12,5 au moins.

  2. L'ORIGINAL N'EST PAS AU DÉPÔT. Le serveur publie tout fichier de la
     racine (`static_folder='.'`) : l'original y serait téléchargeable, et il
     porte encore la scène.

  3. LA VIDÉO EST SERVIE COMME UN FICHIER, PAS PAR UNE ROUTE BRIDÉE. Un
     lecteur vidéo envoie plusieurs requêtes par plage d'octets ; la route
     de /demo.mp4, bornée à cinq requêtes par minute, l'aurait coupé.

  4. ELLE S'ARRÊTE QUAND ON LE DEMANDE. Muette, en boucle, au-delà de cinq
     secondes : un bouton de pause est exigé (WCAG 2.2.2), et sous
     `prefers-reduced-motion` elle ne démarre pas d'elle-même. Ce qu'elle
     montre est écrit en toutes lettres, dans les trois langues de l'accueil.
"""
import io
import json
import os
import re
import shutil
import subprocess

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO = 'hero-security-advisor.mp4'
AFFICHE = 'hero-security-advisor.jpg'


def _lire(nom):
    return io.open(os.path.join(ICI, nom), encoding='utf-8').read()


ACCUEIL = _lire('index.html')
ACCUEIL_JS = _lire('index.page.js')
APP = _lire('app.py')

#: LA SIGNATURE DE LA CARTE « RÉFÉRENCE BANCAIRE », PLEINEMENT AFFICHÉE
#: (image 455 de l'original), réduite à 16 × 20 niveaux de gris.
_TEMOIN_BANQUE = [
    246, 236, 237, 236, 236, 236, 236, 236, 240, 241, 238, 235, 231, 230, 229, 232,
    243, 220, 219, 220, 223, 226, 246, 246, 246, 240, 234, 230, 228, 226, 225, 228,
    246, 246, 246, 246, 246, 246, 246, 246, 240, 240, 238, 232, 224, 224, 223, 224,
    242, 242, 242, 242, 242, 242, 242, 243, 240, 240, 238, 232, 225, 223, 223, 224,
    240, 245, 245, 245, 245, 245, 245, 245, 244, 244, 242, 240, 237, 236, 235, 227,
    239, 249, 248, 247, 247, 236, 239, 238, 239, 239, 237, 248, 247, 248, 249, 229,
    238, 249, 249, 179, 198, 180, 199, 191, 195, 218, 233, 236, 182, 246, 249, 231,
    238, 249, 244, 126, 151, 160, 154, 156, 159, 196, 141, 170, 192, 249, 249, 233,
    236, 249, 249, 172, 190, 171, 190, 183, 187, 215, 183, 224, 179, 246, 249, 236,
    232, 249, 249, 233, 232, 236, 231, 238, 245, 244, 246, 247, 247, 249, 249, 237,
    231, 249, 249, 228, 216, 232, 230, 235, 242, 235, 234, 234, 237, 249, 249, 233,
    229, 249, 231, 168, 165, 189, 174, 174, 162, 191, 156, 165, 165, 240, 249, 232,
    224, 249, 164, 159, 179, 174, 172, 167, 201, 192, 186, 195, 189, 205, 249, 232,
    224, 249, 249, 249, 233, 217, 221, 218, 224, 233, 229, 236, 249, 249, 249, 232,
    224, 249, 249, 233, 214, 214, 211, 217, 216, 214, 216, 212, 232, 249, 249, 229,
    224, 246, 247, 247, 247, 248, 248, 248, 248, 247, 248, 247, 247, 247, 246, 225,
    230, 225, 223, 224, 224, 225, 225, 225, 224, 224, 221, 219, 216, 214, 215, 224,
    232, 232, 232, 232, 232, 232, 232, 232, 232, 229, 228, 224, 221, 215, 216, 222,
    235, 237, 237, 237, 237, 236, 235, 234, 234, 232, 230, 228, 226, 227, 230, 232,
    230, 229, 228, 227, 228, 219, 221, 222, 221, 221, 221, 228, 226, 224, 224, 225,
]
_W, _H = 16, 20
#: LE SEUIL, ENTRE LES DEUX MESURES : 2,55 au plus pour la carte, 12,5 au
#: moins pour tout le reste.
_SEUIL = 6.0

_FFMPEG = shutil.which('ffmpeg')
_sans_ffmpeg = pytest.mark.skipif(not _FFMPEG, reason="ffmpeg absent : la vidéo ne peut pas être décodée ici")


def signatures(chemin):
    """Une signature 16 × 20 en niveaux de gris par image."""
    r = subprocess.run([_FFMPEG, '-v', 'error', '-i', chemin, '-vf',
                        'scale=%d:%d:flags=area,format=gray' % (_W, _H),
                        '-f', 'rawvideo', '-'], capture_output=True, check=True, timeout=120)
    n = _W * _H
    return [r.stdout[i:i + n] for i in range(0, len(r.stdout) - n + 1, n)]


def proches_de_la_banque(chemin):
    """Les numéros des images qui ressemblent à la carte bancaire."""
    out = []
    for k, s in enumerate(signatures(chemin)):
        d = sum(abs(a - b) for a, b in zip(s, _TEMOIN_BANQUE)) / float(len(s))
        if d < _SEUIL:
            out.append(k)
    return out


# ══════════════════════════════════════════════════════════════════════════
#  1. LA VIDÉO PUBLIÉE
# ══════════════════════════════════════════════════════════════════════════

@_sans_ffmpeg
def test_la_scene_REFERENCE_BANCAIRE_n_est_dans_AUCUNE_image_publiee():
    proches = proches_de_la_banque(os.path.join(ICI, VIDEO))
    assert not proches, ("%d image(s) de la vidéo publiée ressemblent à la carte "
                         "« référence bancaire » (600 k€), dont la n°%d"
                         % (len(proches), proches[0]))


@_sans_ffmpeg
def test_la_video_est_lisible_par_tout_navigateur():
    """H.264 en 4:2:0, et l'index en tête (`faststart`) : sans lui, le
    navigateur télécharge tout le fichier avant la première image."""
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                        'stream=codec_name,pix_fmt,width,height:format=duration',
                        '-of', 'json', os.path.join(ICI, VIDEO)],
                       capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    v = [s for s in d['streams'] if s.get('codec_name')][0]
    assert v['codec_name'] == 'h264' and v['pix_fmt'] == 'yuv420p', v
    assert v['width'] * 5 == v['height'] * 4, "le format n'est plus 4:5 : %s" % v
    assert len(d['streams']) == 1, "la vidéo porte une piste de plus qu'elle n'en montre"
    tete = io.open(os.path.join(ICI, VIDEO), 'rb').read(4096)
    assert tete.find(b'moov') >= 0 and (tete.find(b'mdat') < 0 or tete.find(b'moov') < tete.find(b'mdat')), \
        "l'index (moov) n'est pas en tête du fichier"


def test_la_video_et_son_affiche_sont_au_depot_et_LEGERES():
    """L'ACCUEIL EST LA PAGE LA PLUS VUE. L'original pesait 5,4 Mo ; la vidéo
    publiée, ramenée à 720 × 900, doit rester sous 2,5 Mo."""
    v = os.path.join(ICI, VIDEO)
    a = os.path.join(ICI, AFFICHE)
    assert os.path.isfile(v) and os.path.isfile(a)
    assert os.path.getsize(v) < 2.5 * 1024 * 1024, os.path.getsize(v)
    assert io.open(a, 'rb').read(3) == b'\xff\xd8\xff', "l'affiche n'est pas un JPEG"


def test_l_ORIGINAL_n_est_pas_au_depot():
    """Une seule vidéo de l'animation à la racine, la publiée. Tout autre
    fichier vidéo du même nom de série serait servi tel quel."""
    suspects = [f for f in os.listdir(ICI)
                if f.lower().endswith(('.mp4', '.mov', '.webm', '.m4v'))
                and ('advisor' in f.lower() or 'security' in f.lower())
                and f != VIDEO]
    assert not suspects, "vidéos de la série à la racine, donc publiées : %s" % suspects


def test_la_video_est_servie_comme_un_FICHIER_et_non_par_une_route_bridee():
    assert "'.mp4'" in APP[APP.index('static_exts = ('):APP.index('static_exts = (') + 200], \
        "les .mp4 ne passent plus par la liste blanche des fichiers statiques"
    assert "@app.route('/%s')" % VIDEO not in APP, (
        "une route dédiée sert la vidéo : bornée comme /demo.mp4, elle couperait "
        "les requêtes par plage du lecteur")


# ══════════════════════════════════════════════════════════════════════════
#  2. L'ACCUEIL
# ══════════════════════════════════════════════════════════════════════════

def _figure():
    i = ACCUEIL.index('<figure class="hero-video" id="hero-video">')
    return ACCUEIL[i:ACCUEIL.index('</figure>', i)]


def test_l_animation_tient_la_place_du_bandeau_en_tete_du_heros():
    h = ACCUEIL.index('<div class="hero-content">')
    f = ACCUEIL.index('<figure class="hero-video"')
    t = ACCUEIL.index('<h1 class="hero-main-title">')
    assert h < f < t, "l'animation n'est plus en tête du héros, au-dessus du titre"


def test_la_video_est_muette_en_boucle_inline_et_cite_des_fichiers_qui_existent():
    f = _figure()
    for attr in ('autoplay', 'muted', 'loop', 'playsinline', 'preload="metadata"'):
        assert re.search(r'<video[^>]*\s%s(?=[\s>])' % re.escape(attr), f), "attribut manquant : %s" % attr
    assert 'poster="/%s"' % AFFICHE in f
    assert '<source src="/%s" type="video/mp4">' % VIDEO in f
    #  LA HAUTEUR EST RÉSERVÉE avant le chargement : sans elle, le titre
    #  sauterait à l'arrivée de la première image.
    assert 'width="720" height="900"' in f


def test_elle_se_met_en_PAUSE_et_respecte_le_mouvement_reduit():
    f = _figure()
    assert 'id="hero-video-btn"' in f and 'data-i18n="hero.video.pause"' in f
    i = ACCUEIL_JS.index("getElementById('hero-video-lecteur')")
    bloc = ACCUEIL_JS[i:ACCUEIL_JS.index('})();', i)]
    assert "prefers-reduced-motion: reduce" in bloc and "v.pause()" in bloc
    assert "removeAttribute('autoplay')" in bloc
    #  LA PAUSE DEMANDÉE GAGNE SUR LE RETOUR À L'ÉCRAN.
    assert "if(!voulue) return;" in bloc
    assert "'hero.video.lire'" in bloc and "'hero.video.pause'" in bloc


def _dictionnaire(langue):
    def gabarit(t):
        return re.sub(r'\\(?:u([0-9a-fA-F]{4})|(.))',
                      lambda m: (chr(int(m.group(1), 16)) if m.group(1)
                                 else {'n': '\n', 't': '\t', 'r': '\r'}.get(m.group(2), m.group(2))), t)
    m = re.search(r'\n  %s:JSON\.parse\(`(.*?)`\)' % langue, ACCUEIL_JS, re.S)
    return json.loads(gabarit(m.group(1)))


@pytest.mark.parametrize('langue', ['fr', 'en', 'de'])
def test_ce_que_montre_l_animation_est_ECRIT_dans_les_trois_langues(langue):
    d = _dictionnaire(langue)
    for cle in ('hero.video.desc', 'hero.video.pause', 'hero.video.lire'):
        assert d.get(cle, '').strip(), "%s : pas de texte pour %s" % (langue, cle)
    assert '600' not in d['hero.video.desc'] and '480' not in d['hero.video.desc'], \
        "le texte de remplacement redit le montant coupé"
    f = _figure()
    assert 'aria-describedby="hero-video-desc"' in f
    assert 'id="hero-video-desc" data-i18n="hero.video.desc"' in f
