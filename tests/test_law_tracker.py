# -*- coding: utf-8 -*-
"""Le bandeau du suivi législatif européen, sur la page Réglementations.

POURQUOI IL EXISTE. La page « Réglementations » part du Règlement (UE)
2024/1689 — c'est-à-dire d'un texte ADOPTÉ. Ce qui est encore en procédure n'y
figure nulle part, et c'est exactement l'angle mort qu'un suivi législatif
comble. Le bandeau est donc EN TÊTE : le placer en bas reviendrait à le
proposer à qui a déjà fini de lire.

CE QUE CES RÈGLES REFUSENT DE LAISSER PASSER. Ce module n'a pas pu joindre
law-tracker.europa.eu — le proxy de sortie le bloque — et ne peut donc pas
vérifier ce que le site annonce de lui-même. Le bandeau ne dit par conséquent
que ce qui est vérifiable : le nom de l'outil et son domaine. Une règle
interdit d'y ajouter une description de périmètre, parce que décrire un
service sur la foi de son nom, dans une page dont tout le propos est de
renvoyer aux textes officiels, serait exactement la faute que cette page
combat.

LE CONTRASTE EST CALCULÉ, PAS CONSTATÉ. Un bandeau en tête de page qui ne se
lit pas ne sert à rien, et « une couleur est déclarée » ne mesure pas qu'elle
se voit.
"""
import io
import os
import re

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "https://law-tracker.europa.eu/homepage?lang=fr"


@pytest.fixture(scope="module")
def page():
    return io.open(os.path.join(ICI, "sentinel.html"), encoding="utf-8").read()


def _bloc(page, ancre, taille=2200):
    i = page.index(ancre)
    return page[i:i + taille]


# ── 1. IL EST LÀ, ET IL EST EN TÊTE ────────────────────────────────────────

def test_le_bandeau_est_sur_la_page_reglementations():
    """Pas ailleurs : c'est la page des textes, c'est là que le manque se voit."""
    p = io.open(os.path.join(ICI, "sentinel.html"), encoding="utf-8").read()
    assert p.count(URL) == 1, (
        "le lien figure %d fois ; une seule est voulue" % p.count(URL))
    debut = p.index('id="p-regs"')
    fin = p.index('<div class="page" id="p-', debut + 10)
    assert debut < p.index(URL) < fin, (
        "le bandeau n'est pas dans le panneau des Réglementations")


def test_le_bandeau_precede_la_veille_et_les_onglets():
    """EN HAUT veut dire AVANT ce qui prend l'écran.

    Mesuré par les positions, pas par une impression : placé après la veille
    et les onglets, il serait sous la ligne de flottaison sur la plupart des
    écrans — et le demandeur a dit « en haut ».
    """
    p = io.open(os.path.join(ICI, "sentinel.html"), encoding="utf-8").read()
    debut = p.index('id="p-regs"')
    lien = p.index(URL)
    veille = p.index('id="veille-regs"', debut)
    onglets = p.index('class="regs-tabbar"', debut)
    assert lien < veille, "le bandeau passe après le bloc de veille"
    assert lien < onglets, "le bandeau passe après la barre d'onglets"


def test_le_lien_s_ouvre_ailleurs_sans_donner_la_main_a_la_cible(page):
    """`target="_blank"` sans `rel` laisse la page ouverte manipuler celle-ci.

    Ce n'est pas une précaution de principe ici : la page d'où l'on part porte
    une session d'administration.
    """
    bloc = _bloc(page, 'class="lawtrack"')
    assert 'target="_blank"' in bloc, bloc[:300]
    assert "noopener" in bloc, bloc[:300]
    assert "noreferrer" in bloc, bloc[:300]


# ── 2. IL NE DIT QUE CE QU'ON A PU VÉRIFIER ────────────────────────────────

def test_le_bandeau_nomme_l_outil_et_son_domaine(page):
    """Les deux seules choses vérifiables sans joindre le site."""
    bloc = _bloc(page, 'class="lawtrack"')
    assert "EU Law Tracker" in bloc, bloc[:400]
    assert "law-tracker.europa.eu" in bloc, bloc[:400]


def test_le_bandeau_n_affirme_rien_du_contenu_du_site(page):
    """LA RÈGLE QUI TIENT L'HONNÊTETÉ DE CE BANDEAU.

    Le site n'a pas pu être joint. Lui prêter un éditeur, un périmètre ou une
    exhaustivité serait une affirmation invérifiable — dans une page dont tout
    le propos est de renvoyer aux textes officiels. Ces formulations sont donc
    interdites ici tant que personne n'est allé voir.
    """
    bloc = _bloc(page, 'class="lawtrack"')
    interdits = [
        "publié par", "édité par", "Commission européenne", "Parlement européen",
        "officiel de l", "toutes les procédures", "l'ensemble des textes",
        "exhaustif", "mis à jour quotidiennement", "en temps réel",
    ]
    trouves = [x for x in interdits if x.lower() in bloc.lower()]
    assert not trouves, (
        "le bandeau affirme ce qui n'a pas pu être vérifié : %r" % trouves)


def test_le_bandeau_dit_pourquoi_il_est_la(page):
    """Un lien nu se lit comme une publicité. Celui-ci dit ce qu'il comble :
    cette page traite d'un texte ADOPTÉ, le reste est en procédure."""
    bloc = _bloc(page, 'class="lawtrack"')
    assert "2024/1689" in bloc, bloc[:600]
    assert "procédure" in bloc, bloc[:600]


# ── 3. IL SE VOIT ET IL SE LIT — MESURÉ ────────────────────────────────────

def _lum(hexa):
    h = hexa.lstrip("#")
    def c(i):
        v = int(h[i:i + 2], 16) / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return .2126 * c(0) + .7152 * c(2) + .0722 * c(4)


def _contraste(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def _composer(rgb, alpha, fond):
    f = fond.lstrip("#")
    return "#%02X%02X%02X" % tuple(
        int(round(rgb[k] * alpha + int(f[k * 2:k * 2 + 2], 16) * (1 - alpha)))
        for k in (0, 1, 2))


def _token(page, nom):
    m = re.search(r"--%s\s*:\s*(#[0-9A-Fa-f]{6})" % re.escape(nom), page)
    assert m, "le jeton --%s n'est plus déclaré" % nom
    return m.group(1)


def test_le_bandeau_se_lit_sur_son_propre_fond(page):
    """Le fond est un voile d'accent sur blanc : on le COMPOSE et on mesure.

    Les trois encres du bandeau — le titre en --ink, le corps en --muted, le
    domaine en --accent — doivent toutes tenir le plancher AA sur ce fond.
    Vérifier que « une couleur est déclarée » ne dirait rien de cela.
    """
    m = re.search(r"\.lawtrack\{[^}]*background:\s*rgba\((\d+),\s*(\d+),\s*"
                  r"(\d+),\s*\.?(\d+)\)", page)
    assert m, "le fond du bandeau n'est plus lisible dans la feuille"
    rgb = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    fond = _composer(rgb, float("0." + m.group(4)), "#FFFFFF")
    for jeton, plancher in (("ink", 4.5), ("muted", 4.5), ("accent", 4.5)):
        c = _contraste(_token(page, jeton), fond)
        assert c >= plancher, (
            "--%s tient %.2f:1 sur le fond du bandeau" % (jeton, c))


def test_la_pastille_pleine_porte_un_texte_lisible(page):
    """Blanc sur --accent : l'inverse du reste du bandeau, donc à mesurer à part."""
    m = re.search(r"\.lawtrack-tag\{[^}]*background:\s*var\(--accent\)[^}]*"
                  r"color:\s*(#[0-9A-Fa-f]{3,6})", page)
    assert m, "la pastille n'est plus lisible dans la feuille"
    encre = m.group(1)
    if len(encre) == 4:
        encre = "#" + "".join(ch * 2 for ch in encre[1:])
    c = _contraste(encre, _token(page, "accent"))
    assert c >= 4.5, "la pastille tient %.2f:1" % c


def test_le_bandeau_reste_atteignable_au_clavier(page):
    """Un bandeau qui est un lien entier doit montrer son focus : sans cela il
    devient invisible pour qui navigue à la tabulation."""
    assert ".lawtrack:focus-visible{" in page, (
        "aucun état de focus : le bandeau disparaît au clavier")
    bloc = _bloc(page, ".lawtrack:focus-visible{", 160)
    assert "outline" in bloc, bloc
