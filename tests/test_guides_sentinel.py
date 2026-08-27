"""LE GUIDE DE PAGE DE SENTINEL — ATTEIGNABLE, UNIQUE, ET DIT DE QUOI IL PARLE.

CE QUI A DÉCLENCHÉ CE FICHIER. Une demande simple : « les guides en début de
page à installer sur toutes les pages, et à mettre à jour pour les autres ».
En vérifiant dans un vrai navigateur, trois défauts sont apparus — et AUCUN
des trois ne produisait la moindre erreur. C'est ce qui les rendait durables.

PREMIER DÉFAUT : VINGT-SIX GUIDES ÉCRASÉS PAR HOMONYMIE. `PAGE_GUIDES` est un
littéral d'objet JavaScript. Une clé répétée n'y est pas une erreur : la
DERNIÈRE gagne, en silence. Vingt-six entrées ajoutées en tête de table étaient
donc mortes à la naissance, recouvertes par des entrées homonymes situées plus
bas. Le panneau ouvrait bien un guide — l'ancien — et rien ne distinguait ce
cas d'un ajout réussi.

DEUXIÈME DÉFAUT : VINGT-CINQ GUIDES SANS BOUTON POUR LES OUVRIR. L'injecteur
cherchait `h1.page-h`. Les vingt-quatre fiches pays titrent en `h1.fiche-h`,
la cartographie des cas d'usage en `h1.page-title`. Sur ces vingt-cinq
panneaux, `querySelector` rendait `null`, la fonction sortait, et le bouton
n'existait pas. Un guide écrit mais inatteignable coûte le prix de l'écriture
sans en rendre la valeur.

TROISIÈME DÉFAUT, LE PLUS DISCRET : LE COMPTAGE. La table contenait des clés
citées avec apostrophes et d'autres sans. Un relevé qui ne voit qu'une des
deux formes annonce une couverture fausse — dans les deux sens : il croit
manquer ce qui existe, et il croit couvrir ce qui manque.

CE QUE CES CONTRÔLES NE PEUVENT PAS FAIRE. Juger la JUSTESSE d'un guide. Qu'un
texte décrive fidèlement son panneau ne se prouve pas ici ; cela s'établit en
lisant le panneau, et c'est ce qui a été fait. Ce fichier tient les propriétés
STRUCTURELLES dont l'atteinte a montré qu'elles manquaient : une clé par
panneau, un panneau par clé, un bouton sur chaque panneau, et de la substance
derrière chaque titre de section.
"""
import io
import os
import re

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JS = io.open(os.path.join(ICI, 'sentinel.page.js'), encoding='utf-8').read()
HTML = io.open(os.path.join(ICI, 'sentinel.html'), encoding='utf-8').read()


def _bloc(nom):
    """Le corps du littéral `nom = { … }`, borné par son exposition sur
    `window` — pas par une accolade comptée à la main."""
    d = JS.index('var %s = {' % nom)
    f = JS.index('window.%s' % nom, d)
    return JS[d:f]


BLOC_GUIDES = _bloc('PAGE_GUIDES')

# Les deux écritures d'une clé JavaScript. Ne relever qu'une des deux est
# exactement le troisième défaut décrit en tête de fichier.
CLE = re.compile(r"^\s{2}(?P<q>['\"]?)(?P<cle>[A-Za-z_][\w-]*)(?P=q)\s*:\s*\{", re.M)


def _entrees():
    """(clé, corps) pour chaque guide, dans l'ordre du fichier."""
    bornes = [(m.group('cle'), m.start()) for m in CLE.finditer(BLOC_GUIDES)]
    out = []
    for n, (cle, i) in enumerate(bornes):
        j = bornes[n + 1][1] if n + 1 < len(bornes) else len(BLOC_GUIDES)
        out.append((cle, BLOC_GUIDES[i:j]))
    return out


ENTREES = _entrees()
CLES = [c for c, _ in ENTREES]

PANNEAUX = re.compile(r'<div class="page[^"]*" id="p-(?P<id>[A-Za-z0-9_-]+)"')


def _panneaux():
    """(id, corps) pour chaque panneau de sentinel.html."""
    bornes = [(m.group('id'), m.start()) for m in PANNEAUX.finditer(HTML)]
    out = []
    for n, (pid, i) in enumerate(bornes):
        j = bornes[n + 1][1] if n + 1 < len(bornes) else len(HTML)
        out.append((pid, HTML[i:j]))
    return out


PANS = _panneaux()
IDS = [p for p, _ in PANS]


def _resolu(pid):
    """La règle de `guidePour()`, rejouée : clé exacte, sinon repli des fiches
    pays sur leur guide commun."""
    return pid in CLES or (pid.startswith('fiche-') and 'fiche-pays' in CLES)


# ── UNE CLÉ, UN GUIDE ────────────────────────────────────────────────────

def test_aucune_cle_repetee():
    """Le premier défaut. Une clé répétée ne lève rien en JavaScript : elle
    supprime silencieusement le guide écrit en premier."""
    vus, doubles = set(), []
    for cle in CLES:
        (doubles.append(cle) if cle in vus else vus.add(cle))
    assert not doubles, (
        "clés répétées dans PAGE_GUIDES — la dernière écrase les précédentes "
        "sans erreur : %s" % ', '.join(sorted(set(doubles))))


def test_le_relevé_voit_les_deux_écritures_de_clé():
    """Le troisième défaut. Si ce contrôle ne trouvait qu'une des deux formes,
    tous les autres compteraient faux — y compris celui de la couverture."""
    avec = [c for c in CLES if ("'%s'" % c) in BLOC_GUIDES]
    sans = [c for c in CLES if re.search(r'^\s{2}%s\s*:\s*\{' % re.escape(c),
                                         BLOC_GUIDES, re.M)]
    assert avec and sans, (
        "la table ne contient plus qu'une seule écriture de clé (%d avec "
        "apostrophes, %d sans) : ce contrôle ne prouve plus rien et doit être "
        "revu, pas supprimé" % (len(avec), len(sans)))


# ── UN PANNEAU, UN GUIDE ─────────────────────────────────────────────────

def test_chaque_panneau_a_un_guide():
    orphelins = sorted(p for p in IDS if not _resolu(p))
    assert not orphelins, (
        "panneaux sans guide, qui tombent sur « Guide non encore disponible » "
        ": %s" % ', '.join(orphelins))


def test_aucun_guide_sans_panneau():
    """L'inverse compte autant : un guide dont le panneau a disparu ne se voit
    jamais, et sa présence fait croire à une couverture qu'il ne rend pas."""
    fantomes = sorted(c for c in CLES if c not in IDS and c != 'fiche-pays')
    assert not fantomes, (
        "guides sans panneau correspondant dans sentinel.html : %s"
        % ', '.join(fantomes))


def test_le_guide_commun_des_fiches_pays_existe():
    """Vingt-quatre fiches partagent un guide. Le repli n'a de sens que si sa
    cible existe."""
    fiches = [p for p in IDS if p.startswith('fiche-')]
    assert len(fiches) >= 20, "les fiches pays ont disparu du relevé"
    assert 'fiche-pays' in CLES
    assert not [f for f in fiches if f in CLES], (
        "une fiche pays a désormais son propre guide : le repli commun n'est "
        "plus la règle, ce contrôle doit être revu")


# ── LE BOUTON EXISTE SUR CHAQUE PANNEAU ──────────────────────────────────

def _ancrage_du_bouton():
    i = JS.index('function guideInjectButton(')
    return JS[i:JS.index('\n}', i)]


def test_le_bouton_s_ancre_sur_un_titre_et_non_sur_une_classe():
    """Le deuxième défaut. `h1.page-h` laissait vingt-cinq panneaux sans
    bouton. La propriété qui vaut est « le premier titre de niveau un du
    panneau », indépendante du nom de classe."""
    corps = _ancrage_du_bouton()
    assert 'querySelector("h1")' in corps, (
        "l'injecteur ancre de nouveau le bouton sur une classe de titre : "
        "tout panneau titrant autrement perdra son bouton, en silence")


def test_tous_les_panneaux_portent_un_titre_de_niveau_un():
    """Sans `h1`, l'injecteur sort et le bouton n'existe pas. C'est la
    condition que le code exige réellement."""
    sans = sorted(p for p, corps in PANS if not re.search(r'<h1[\s>]', corps))
    assert not sans, (
        "panneaux sans <h1> : leur guide restera inatteignable — %s"
        % ', '.join(sans))


def test_les_titres_de_panneau_ne_partagent_pas_une_seule_classe():
    """Si un jour tous les panneaux titraient pareil, l'ancrage par classe
    redeviendrait suffisant — et ce contrôle-ci, trompeur. Il dit alors qu'il
    ne prouve plus rien."""
    classes = set()
    for _, corps in PANS:
        m = re.search(r'<h1[^>]*class="([^"]*)"', corps)
        if m:
            classes.add(m.group(1).strip())
    assert len(classes) > 1, (
        "tous les titres portent la même classe (%s) : l'ancrage générique "
        "n'est plus une exigence, ce fichier doit être relu" % classes)


def test_le_bouton_se_pose_apres_le_conteneur_du_titre():
    """Sur les fiches pays le titre vit dans une rangée flex ; y insérer le
    bouton le rangerait dans la rangée, à côté du badge de risque."""
    corps = _ancrage_du_bouton()
    assert 'h1.parentNode !== activePage' in corps, (
        "le bouton se pose de nouveau juste après le titre : sur les fiches "
        "pays il atterrira dans la rangée du code pays et du badge")


def test_le_bouton_est_reinjecte_a_chaque_navigation():
    i = JS.index('/* Re-injecter le bouton a chaque navigation */')
    corps = JS[i:i + 900]
    assert 'guideInjectButton()' in corps and 'window.go' in corps, (
        "la ré-injection du bouton après `go()` a disparu : le bouton "
        "resterait celui du panneau quitté")


# ── LE GUIDE DIT QUELQUE CHOSE ───────────────────────────────────────────

SECTION = re.compile(r'\{h:"([^"]*)",\s*t:"([^"]*)"\}')


@pytest.mark.parametrize('cle,corps', ENTREES, ids=[c for c, _ in ENTREES])
def test_un_guide_a_un_titre_et_au_moins_deux_sections(cle, corps):
    titre = re.search(r'title:\s*"([^"]*)"', corps)
    assert titre and len(titre.group(1).strip()) >= 8, (
        "guide %s sans titre lisible" % cle)
    sections = SECTION.findall(corps)
    assert len(sections) >= 2, (
        "guide %s : %d section(s). Deux au minimum — à quoi sert la page, et "
        "comment s'en servir." % (cle, len(sections)))


@pytest.mark.parametrize('cle,corps', ENTREES, ids=[c for c, _ in ENTREES])
def test_aucune_section_ne_se_reduit_a_son_titre(cle, corps):
    """Un intitulé sans texte derrière remplit la fenêtre sans rien apprendre.
    Le seuil est celui de la section la plus courte réellement écrite (87
    caractères), arrondi en dessous."""
    for h, t in SECTION.findall(corps):
        assert len(h.strip()) >= 5, "guide %s : intitulé vide" % cle
        assert len(t.strip()) >= 80, (
            "guide %s, section « %s » : %d caractères. Trop court pour "
            "apprendre quoi que ce soit." % (cle, h, len(t.strip())))


@pytest.mark.parametrize('cle,corps', ENTREES, ids=[c for c, _ in ENTREES])
def test_les_intitulés_d_un_guide_sont_distincts(cle, corps):
    intitules = [h.strip().lower() for h, _ in SECTION.findall(corps)]
    assert len(set(intitules)) == len(intitules), (
        "guide %s : deux sections portent le même intitulé — l'une des deux "
        "est probablement un doublon d'écriture" % cle)


def test_le_repli_reste_écrit_mais_inatteignable():
    """Le message « Guide non encore disponible » doit continuer d'exister —
    un panneau ajouté demain le rencontrera. Aucun panneau d'aujourd'hui ne
    doit y tomber : c'est ce que garantit le contrôle de couverture."""
    assert 'Guide non encore disponible' in JS
    assert not [p for p in IDS if not _resolu(p)]


# ── LE MENU MÈNE À DES PANNEAUX QUI EXISTENT ─────────────────────────────

def test_chaque_entrée_de_menu_ouvre_un_panneau_guidé():
    cibles = set(re.findall(r"go\('([A-Za-z0-9_-]+)'", HTML))
    assert len(cibles) >= 40, "le relevé des entrées de menu est retombé à %d" % len(cibles)
    muets = sorted(c for c in cibles if c in IDS and not _resolu(c))
    assert not muets, "entrées de menu menant à un panneau sans guide : %s" % ', '.join(muets)
    inconnues = sorted(c for c in cibles if c not in IDS)
    assert not inconnues, (
        "le menu appelle des panneaux qui n'existent pas : %s" % ', '.join(inconnues))
