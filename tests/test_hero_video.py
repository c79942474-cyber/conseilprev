# -*- coding: utf-8 -*-
"""LE BANDEAU « SECURITY ADVISOR — BANQUE » EN TÊTE DE L'ACCUEIL.

CE QUI A ÉTÉ DEMANDÉ, EN DEUX TEMPS : remplacer le bandeau « Gouverner et
sécuriser l'IA — invitation gratuite du 9 novembre » par l'animation fournie,
EN SUPPRIMANT LA RÉFÉRENCE BANCAIRE de 600 k€ ; puis la mettre au FORMAT D'UN
BANDEAU LINKEDIN, cliquable, menant au profil LinkedIn de Christophe Cerf.

CE QUI A ÉTÉ FAIT, ET CE QUE CES RÈGLES MESURENT :

  1. L'ANIMATION EST RECOMPOSÉE, PAS RECADRÉE. L'original était en portrait
     (4:5), titres et cartes empilés ; un bandeau LinkedIn fait 4:1. Un
     recadrage aurait coupé les textes. Les scènes, leurs textes et leurs
     couleurs sont repris dans `outils/bandeau_security_advisor/bandeau.html`,
     disposés en largeur, et `engendrer.js` en tire la vidéo image par image.

  2. LA RÉFÉRENCE BANCAIRE N'EXISTE PAS DANS LA SOURCE. La carte de l'original
     portait trois montants — 600 k€, « signé 480 k€ (+ 110 k€ optionnel) » —
     et désignait le client. La règle relit la source et refuse chacun de ces
     marqueurs. LA VIDÉO PUBLIÉE EST BIEN CELLE DE LA SOURCE : sa durée et son
     nombre d'images sont ceux que la chronologie de la source fixe.
     (La version précédente, coupée dans l'original, gardait une signature
     d'image de la carte pour la reconnaître. Comparée à des images 4:1, elle
     ne mesurerait plus rien : elle a été retirée plutôt que laissée verte.)

  3. L'ORIGINAL N'EST PAS AU DÉPÔT : le serveur publie tout fichier de la
     racine (`static_folder='.'`), et l'original porte encore la scène.

  4. LA VIDÉO EST SERVIE COMME UN FICHIER, pas par une route bridée : un
     lecteur envoie plusieurs requêtes par plage d'octets.

  5. LE BANDEAU ENTIER EST LE LIEN, le bouton de pause vit À CÔTÉ (un bouton
     dans un lien est du HTML invalide, et la pause ouvrirait LinkedIn). Le
     lien s'ouvre dans un nouvel onglet, sans transmettre `window.opener`.

  6. IL S'ARRÊTE QUAND ON LE DEMANDE (WCAG 2.2.2), ne démarre pas seul sous
     `prefers-reduced-motion`, et ce qu'il montre est écrit en toutes lettres
     dans les trois langues de l'accueil.
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
SOURCE = os.path.join('outils', 'bandeau_security_advisor', 'bandeau.html')
PROFIL = 'https://www.linkedin.com/in/cerfchristophe'


def _lire(nom):
    return io.open(os.path.join(ICI, nom), encoding='utf-8').read()


ACCUEIL = _lire('index.html')
ACCUEIL_JS = _lire('index.page.js')
APP = _lire('app.py')
SRC = _lire(SOURCE)

_FFPROBE = shutil.which('ffprobe')
_sans_ffprobe = pytest.mark.skipif(not _FFPROBE, reason="ffprobe absent : la vidéo ne peut pas être lue ici")


def _sonder():
    r = subprocess.run([_FFPROBE, '-v', 'error', '-count_frames', '-show_entries',
                        'stream=codec_name,pix_fmt,width,height,nb_read_frames,r_frame_rate:format=duration',
                        '-of', 'json', os.path.join(ICI, VIDEO)],
                       capture_output=True, text=True, check=True, timeout=120)
    return json.loads(r.stdout)


# ══════════════════════════════════════════════════════════════════════════
#  1. LA SOURCE ET LA VIDÉO
# ══════════════════════════════════════════════════════════════════════════

#: CE QUE LA SCÈNE RETIRÉE PORTAIT. Chaque marqueur est cherché tel quel, et
#: aussi sans espace (« 600k€ ») ni insécable.
_MARQUEURS_BANQUE = ('600 k', '480 k', '110 k', 'référence bancaire',
                     "appel d'offres", 'appel d’offres', 'triennal', 'remporté par')


def test_la_source_ne_porte_AUCUNE_trace_de_la_reference_bancaire():
    """CE QUI EST MONTRÉ, pas ce qui est commenté : le commentaire de tête
    de la source NOMME la scène pour dire qu'elle est absente, et c'est sa
    place. Tout le reste — balisage, styles, script — est lu."""
    montre = re.sub(r'<!--.*?-->', ' ', SRC, flags=re.S)
    texte = re.sub(r'[\s\u00a0\u202f]+', ' ', montre).lower()
    compact = texte.replace(' ', '')
    for m in _MARQUEURS_BANQUE:
        assert m.lower() not in texte and m.lower().replace(' ', '') not in compact, (
            "la source du bandeau porte « %s » : la référence bancaire revient" % m)


def _chronologie():
    m = re.search(r'var DUREES = \[([^\]]+)\];', SRC)
    return [float(x) for x in m.group(1).split(',')]


@_sans_ffprobe
def test_la_video_publiee_est_CELLE_de_la_source():
    """Durée et nombre d'images fixés par la chronologie de la source, à
    30 images par seconde. Une vidéo remplacée à la main — l'original, une
    autre version — aurait une autre durée ou un autre format."""
    d = _sonder()
    v = d['streams'][0]
    total = sum(_chronologie())
    assert len(_chronologie()) == SRC.count('<section class="scene'), \
        "la chronologie et les scènes ne se correspondent plus"
    assert v['r_frame_rate'] == '30/1', v['r_frame_rate']
    assert int(v['nb_read_frames']) == round(total * 30), (v['nb_read_frames'], total)
    assert abs(float(d['format']['duration']) - total) < 0.05


@_sans_ffprobe
def test_la_video_est_un_BANDEAU_LINKEDIN_lisible_par_tout_navigateur():
    """1584 × 396 — le format d'un bandeau LinkedIn — en H.264 4:2:0, sans
    piste son, l'index en tête (`faststart`) : sans lui, le navigateur
    télécharge tout le fichier avant la première image."""
    d = _sonder()
    assert len(d['streams']) == 1, "la vidéo porte une piste de plus qu'elle n'en montre"
    v = d['streams'][0]
    assert (v['width'], v['height']) == (1584, 396), v
    assert v['codec_name'] == 'h264' and v['pix_fmt'] == 'yuv420p', v
    tete = io.open(os.path.join(ICI, VIDEO), 'rb').read(4096)
    assert tete.find(b'moov') >= 0 and (tete.find(b'mdat') < 0 or tete.find(b'moov') < tete.find(b'mdat')), \
        "l'index (moov) n'est pas en tête du fichier"


def test_la_video_et_son_affiche_sont_au_depot_et_LEGERES():
    v = os.path.join(ICI, VIDEO)
    a = os.path.join(ICI, AFFICHE)
    assert os.path.isfile(v) and os.path.isfile(a)
    assert os.path.getsize(v) < 2.5 * 1024 * 1024, os.path.getsize(v)
    assert io.open(a, 'rb').read(3) == b'\xff\xd8\xff', "l'affiche n'est pas un JPEG"


def test_l_ORIGINAL_n_est_pas_au_depot():
    suspects = []
    for racine, dossiers, fichiers in os.walk(ICI):
        dossiers[:] = [d for d in dossiers if not d.startswith('.') and d != 'node_modules']
        for f in fichiers:
            if (f.lower().endswith(('.mp4', '.mov', '.webm', '.m4v'))
                    and ('advisor' in f.lower() or 'security' in f.lower()) and f != VIDEO):
                suspects.append(os.path.relpath(os.path.join(racine, f), ICI))
    assert not suspects, "vidéos de la série au dépôt, donc publiées : %s" % suspects


def test_la_video_est_servie_comme_un_FICHIER_et_non_par_une_route_bridee():
    i = APP.index('static_exts = (')
    assert "'.mp4'" in APP[i:i + 200], "les .mp4 ne passent plus par la liste blanche"
    assert "@app.route('/%s')" % VIDEO not in APP, (
        "une route dédiée sert la vidéo : bornée comme /demo.mp4, elle couperait "
        "les requêtes par plage du lecteur")


# ══════════════════════════════════════════════════════════════════════════
#  2. L'ACCUEIL
# ══════════════════════════════════════════════════════════════════════════

def _figure():
    i = ACCUEIL.index('<figure class="hero-video" id="hero-video">')
    return ACCUEIL[i:ACCUEIL.index('</figure>', i)]


def test_le_bandeau_tient_la_place_de_l_invitation_en_tete_du_heros():
    h = ACCUEIL.index('<div class="hero-content">')
    f = ACCUEIL.index('<figure class="hero-video"')
    t = ACCUEIL.index('<h1 class="hero-main-title">')
    assert h < f < t, "le bandeau n'est plus en tête du héros, au-dessus du titre"


def test_le_bandeau_ENTIER_mene_au_profil_LinkedIn_dans_un_nouvel_onglet():
    f = _figure()
    m = re.search(r'<a class="hero-video-lien"[^>]*>(.*?)</a>', f, re.S)
    assert m, "le bandeau n'est plus un lien"
    ouvrante = f[f.index('<a class="hero-video-lien"'):f.index('>', f.index('<a class="hero-video-lien"')) + 1]
    assert 'href="%s"' % PROFIL in ouvrante, ouvrante
    assert 'target="_blank"' in ouvrante and 'rel="noopener"' in ouvrante, (
        "un nouvel onglet sans rel=noopener laisse LinkedIn piloter la page d'origine")
    dedans = m.group(1)
    assert '<video' in dedans, "la vidéo n'est pas dans le lien : seul un coin serait cliquable"
    assert 'data-i18n="hero.video.lien"' in dedans, "le lien n'a pas de nom lisible"
    assert '<button' not in dedans, "le bouton de pause est DANS le lien : un clic ouvrirait LinkedIn"
    assert 'id="hero-video-btn"' in f[f.index('</a>'):], "le bouton de pause a quitté le bandeau"


def test_la_video_est_muette_en_boucle_inline_et_reserve_sa_hauteur():
    f = _figure()
    for attr in ('autoplay', 'muted', 'loop', 'playsinline', 'preload="metadata"'):
        assert re.search(r'<video[^>]*\s%s(?=[\s>])' % re.escape(attr), f), "attribut manquant : %s" % attr
    assert 'poster="/%s"' % AFFICHE in f
    assert '<source src="/%s" type="video/mp4">' % VIDEO in f
    assert 'width="1584" height="396"' in f
    assert '.hero-video-v{display:block;width:100%;height:auto;aspect-ratio:4/1' in ACCUEIL


def test_il_se_met_en_PAUSE_et_respecte_le_mouvement_reduit():
    f = _figure()
    assert 'id="hero-video-btn"' in f and 'data-i18n="hero.video.pause"' in f
    i = ACCUEIL_JS.index("getElementById('hero-video-lecteur')")
    bloc = ACCUEIL_JS[i:ACCUEIL_JS.index('})();', i)]
    assert "prefers-reduced-motion: reduce" in bloc and "v.pause()" in bloc
    assert "removeAttribute('autoplay')" in bloc
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
def test_ce_que_montre_le_bandeau_est_ECRIT_dans_les_trois_langues(langue):
    d = _dictionnaire(langue)
    for cle in ('hero.video.desc', 'hero.video.pause', 'hero.video.lire', 'hero.video.lien'):
        assert d.get(cle, '').strip(), "%s : pas de texte pour %s" % (langue, cle)
    assert '600' not in d['hero.video.desc'] and '480' not in d['hero.video.desc'], \
        "le texte de remplacement redit le montant coupé"
    assert 'LinkedIn' in d['hero.video.lien']
    f = _figure()
    assert 'aria-describedby="hero-video-desc"' in f
    assert 'id="hero-video-desc" data-i18n="hero.video.desc"' in f
