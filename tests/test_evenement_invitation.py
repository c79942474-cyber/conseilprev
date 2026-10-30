# -*- coding: utf-8 -*-
"""L'INVITATION ET SA SOURCE NE DOIVENT PAS DIVERGER.

CE QUE CES RÈGLES GARDENT. L'après-midi de formation du 9 novembre 2026 est
servie par la page `/formation-ia`, celle qu'on partage, et `evenement.py` en
est la source. Un horaire corrigé d'un côté et pas de l'autre ne se
signalerait par rien : ces règles refusent que la page s'en écarte — la date,
les bornes horaires, le lieu, les neuf étapes, les conditions, l'adresse
d'inscription, le lien du PDF.

LE BANDEAU DE L'ACCUEIL, SECONDE COPIE, A ÉTÉ RETIRÉ — remplacé par
l'animation « Security Advisor — Banque » (tests/test_hero_video.py). Les
règles qui le comparaient à la page sont parties avec lui ; une seule reste,
et elle refuse qu'un bandeau à moitié retiré survive en tête de l'accueil.
"""
import html as _html
import io
import json
import os
import re
import subprocess
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import evenement as ev  # noqa: E402


def _lire(nom):
    return io.open(os.path.join(ICI, nom), encoding='utf-8').read()


PAGE = _lire('formation-ia.html')
ACCUEIL = _lire('index.html')
ACCUEIL_JS = _lire('index.page.js')
EV_JS = _lire('evenement.js')
APP = _lire('app.py')
GUIDE = _lire('guide.js')


def _texte(src):
    """Le texte visible : balises retirées, entités rendues, espaces réduits.

    ON LIT CE QUE LE VISITEUR VOIT, pas la source. Un fait présent dans un
    commentaire HTML ou coupé en deux par une balise ne compte pas."""
    sans_script = re.sub(r'<(script|style)\b.*?</\1>', ' ', src, flags=re.S | re.I)
    sans_commentaire = re.sub(r'<!--.*?-->', ' ', sans_script, flags=re.S)
    return re.sub(r'\s+', ' ', _html.unescape(re.sub(r'<[^>]+>', ' ', sans_commentaire)))


TEXTE_PAGE = _texte(PAGE)



# ══════════════════════════════════════════════════════════════════════════
#  1. LA PAGE EST ENGENDRÉE, ET ELLE N'A PAS VIEILLI
# ══════════════════════════════════════════════════════════════════════════

def test_la_page_engendree_est_a_jour():
    """LE PRIX DU CHOIX D'UNE PAGE ÉCRITE SUR DISQUE. La page est servie en
    HTML statique pour qu'elle s'affiche sans JavaScript et qu'un moteur la
    lise. En échange, elle peut vieillir pendant que `evenement.py` change :
    c'est l'outil qui le dit, et cette règle qui l'exige."""
    r = subprocess.run([sys.executable, 'outils/engendrer_invitation.py',
                        '--verifier'], cwd=ICI, capture_output=True, text=True)
    assert r.returncode == 0, (
        "la page ou le script partagé a dérivé de evenement.py — rejouez "
        "« python3 outils/engendrer_invitation.py » :\n" + r.stdout + r.stderr)


def test_les_fichiers_engendres_disent_qu_ils_le_sont():
    """Un fichier engendré qui ne le dit pas sera corrigé à la main, et la
    correction sera perdue au passage suivant — sans que personne ne sache
    pourquoi."""
    for nom, src in (('formation-ia.html', PAGE), ('evenement.js', EV_JS)):
        assert 'engendr' in src.lower().replace('é', 'e'), nom
        assert 'evenement.py' in src, "%s ne nomme pas sa source" % nom
        assert 'outils/engendrer_invitation.py' in src, \
            "%s ne nomme pas l'outil qui le refait" % nom


# ══════════════════════════════════════════════════════════════════════════
#  2. LES FAITS, DES DEUX CÔTÉS
# ══════════════════════════════════════════════════════════════════════════

FAITS = [
    pytest.param(lambda: ev.TITRE, id='titre'),
    pytest.param(lambda: ev.PUBLIC, id='public'),
    pytest.param(lambda: ev.DATE_LISIBLE, id='date'),
    pytest.param(lambda: ev.LIEU, id='lieu'),
    pytest.param(lambda: ev.ADRESSE, id='adresse'),
    pytest.param(lambda: ev.VILLE, id='ville'),
    pytest.param(lambda: ev.ACCES, id='acces'),
    pytest.param(lambda: ev.GRATUITE, id='gratuite'),
    pytest.param(lambda: ev.CONDITIONS[0], id='condition-report'),
    pytest.param(lambda: ev.CONDITIONS[1], id='condition-autre-novotel'),
    pytest.param(lambda: ev.ANIMATEUR, id='animateur'),
]


@pytest.mark.parametrize('fait', FAITS)
def test_la_page_porte_le_fait(fait):
    v = fait()
    assert v in TEXTE_PAGE, (
        "/formation-ia ne dit pas « %s » — la page a dérivé de evenement.py"
        % v[:70])


#  L'IDENTIFIANT DE CHAQUE CAS EST L'HEURE, et rien d'autre : pytest
#  fabriquerait sinon un nom à partir des quatre champs, intitulé et
#  détail compris — illisible dans un rapport, et instable dès qu'on
#  corrige une virgule.
@pytest.mark.parametrize('heure,titre,detail,module', ev.PROGRAMME,
                         ids=[h for h, _, _, _ in ev.PROGRAMME])
def test_la_page_porte_chaque_etape(heure, titre, detail, module):
    """LES NEUF ÉTAPES, HEURE PAR HEURE. C'est le contenu le plus long, donc
    celui qu'on corrige d'un seul côté."""
    assert heure in TEXTE_PAGE, '/formation-ia : %s absent' % heure
    assert titre in TEXTE_PAGE, '/formation-ia : « %s » absent' % titre
    if detail:
        assert detail in TEXTE_PAGE, '/formation-ia : le détail de %s est absent' % heure


def test_la_page_n_ajoute_aucune_etape():
    """Une étape de plus est une divergence autant qu'une de moins, et elle ne
    se verrait pas en cherchant ce que le module déclare."""
    attendues = len(ev.PROGRAMME)
    assert PAGE.count('<li class="iv-mod">') + PAGE.count('<li class="iv-pause">') \
        + PAGE.count('<li><time') == attendues, \
        '/formation-ia ne porte pas %d étapes' % attendues


def test_l_accueil_ne_garde_AUCUN_reste_du_bandeau():
    """UN BANDEAU À MOITIÉ RETIRÉ EST PIRE QU'UN BANDEAU. Le retrait touchait
    le HTML, sa feuille de style, son script, ses cinquante-six clés de
    traduction et le chargement de /evenement.js : un morceau oublié laisse
    une invitation fantôme — un bouton d'agenda sans bandeau, un libellé
    traduit que plus rien n'affiche, un script chargé pour rien."""
    for reste in ('id="inv-bandeau"', 'class="inv-billet"', '.inv-billet{',
                  '/evenement.js', 'datetime="2026-11-09'):
        assert reste not in ACCUEIL, "l'accueil garde « %s » du bandeau" % reste
    for reste in ("getElementById('inv-bandeau')", '"inv.titre"', 'CPEvenement'):
        assert reste not in ACCUEIL_JS, "index.page.js garde « %s » du bandeau" % reste


# ══════════════════════════════════════════════════════════════════════════
#  3. LA PAGE EST SERVIE
# ══════════════════════════════════════════════════════════════════════════

def test_la_page_est_publiee_par_le_serveur():
    """Un lien vers une adresse que le serveur ne publie pas rend 404, et le
    bandeau l'annoncerait quand même."""
    assert ("'%s':" % ev.PAGE) in APP, \
        "%s n'est pas dans la table PAGES d'app.py" % ev.PAGE
    assert "'formation-ia.html'" in APP


def test_la_page_a_son_guide():
    """La règle du dépôt l'exige pour toute adresse publiée ; on nomme ici
    l'adresse pour que l'échec dise de quelle page il s'agit."""
    assert ('GUIDES["%s"]' % ev.PAGE) in GUIDE, \
        "%s tomberait sur le guide générique" % ev.PAGE


# ══════════════════════════════════════════════════════════════════════════
#  4. CE QUE LA PAGE AJOUTE, ET QUI DOIT RESTER VRAI
# ══════════════════════════════════════════════════════════════════════════

def test_le_pitch_et_les_acquis_sont_sur_la_page():
    """LE PITCH EST CE QU'ON LIT EN PREMIER. Il vit dans `evenement.py` parce
    que c'est aussi le texte qu'on recopie dans un courriel."""
    for p in ev.PITCH.split('\n'):
        if p.strip():
            assert p.strip() in TEXTE_PAGE, \
                "le pitch a dérivé : « %s »" % p.strip()[:60]
    for titre, detail in ev.ACQUIS:
        assert titre in TEXTE_PAGE, "acquis absent : %s" % titre
        assert detail in TEXTE_PAGE, "détail d'acquis absent : %s" % titre


def test_l_inscription_mene_au_lien_du_pdf_des_deux_cotes():
    """LE LIEN D'INSCRIPTION EST CELUI DE L'INVITATION D'ORIGINE, octet pour
    octet : même destinataire, même objet, même corps pré-rempli. Deux objets
    différents, et les inscriptions ne se classent plus ensemble."""
    attendu = _html.escape(ev.MAILTO, quote=True)
    #  TOUS LES LIENS, PAS « AU MOINS UN ». Mesuré par la mutation M7 : la
    #  page porte trois fois l'adresse d'inscription, et n'en changer qu'une
    #  laissait passer une règle qui se contentait d'une occurrence.
    for nom, src in (('/formation-ia', PAGE),):
        liens = re.findall(r'href="(mailto:[^"]*%s[^"]*)"'
                           % re.escape(ev.INSCRIPTION), src)
        assert liens, "%s n'offre plus aucun lien d'inscription" % nom
        divergents = [l for l in liens if l != attendu]
        assert not divergents, (
            "%s porte %d lien(s) d'inscription qui ne sont pas celui de "
            "l'invitation PDF : %s" % (nom, len(divergents), divergents[0][:90]))


def test_le_pdf_de_l_invitation_est_sur_le_disque_et_lie():
    chemin = os.path.join(ICI, ev.PDF.lstrip('/'))
    assert os.path.exists(chemin), "le PDF de l'invitation a disparu : %s" % ev.PDF
    assert io.open(chemin, 'rb').read(5) == b'%PDF-', "ce n'est pas un PDF"
    assert ev.PDF in PAGE


def test_les_donnees_structurees_disent_les_memes_bornes():
    """UN LIEN PARTAGÉ EST D'ABORD UN APERÇU. Des bornes fausses dans le
    JSON-LD donneraient à un moteur une date que la page contredit."""
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', PAGE, re.S)
    assert m, "la page a perdu ses données structurées"
    d = json.loads(m.group(1))
    assert d['@type'] == 'EducationEvent'
    assert d['startDate'].startswith('2026-11-09T13:00')
    assert d['endDate'].startswith('2026-11-09T17:00')
    assert d['name'] == ev.TITRE
    assert d['location']['name'] == ev.LIEU
    assert d['offers']['url'] == ev.MAILTO


# ══════════════════════════════════════════════════════════════════════════
#  5. UN SEUL FABRICANT DE FICHIER D'AGENDA
# ══════════════════════════════════════════════════════════════════════════

def test_l_accueil_ne_fabrique_aucun_ics():
    """LE DÉFAUT QUE CETTE RÈGLE EMPÊCHE DE REVENIR. Le bandeau de l'accueil
    fabriquait son .ics lui-même, à côté de celui de la page : deux fabricants
    finissent par poser deux séances différentes. Le bandeau est parti ; la
    règle reste, parce qu'un retour de l'invitation sur l'accueil se ferait
    d'abord en recopiant un fabricant."""
    for marqueur in ('BEGIN:VCALENDAR', 'function plier', 'DTSTART:'):
        assert marqueur not in ACCUEIL_JS, (
            "index.page.js refabrique un .ics (« %s ») : il doit passer par "
            "/evenement.js" % marqueur)


def test_la_page_charge_le_script_partage():
    """La page s'en sert pour son bouton d'agenda : sans lui, le repli
    existe, mais il ne doit jamais servir."""
    assert '<script src="/evenement.js" defer></script>' in PAGE, \
        "formation-ia.html ne charge pas /evenement.js"


def test_le_script_partage_porte_les_bornes_du_module():
    """Les deux bornes, et le fuseau : 14 h – 18 h à Paris valent 13 h – 17 h
    UTC en heure d'hiver. Une erreur d'une heure ici ne se voit qu'au moment
    où la salle est vide."""
    assert 'Date.UTC(2026, 10, 9, 13, 0, 0)' in EV_JS
    assert 'Date.UTC(2026, 10, 9, 17, 0, 0)' in EV_JS
    for c in ev.CONDITIONS:
        assert c in EV_JS, "le .ics ne porte pas la condition « %s »" % c[:50]
