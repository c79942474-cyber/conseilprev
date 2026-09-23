# -*- coding: utf-8 -*-
"""Chaque onglet de la barre porte son dessin, et chaque rubrique sa teinte.

CE QUI A ÉTÉ MESURÉ DANS UN NAVIGATEUR (recette_barre_sentinel.js) : huit
contrôles en échec. Quatre venaient de la recette, écrite avant deux
décisions prises depuis — les tiroirs repliés par défaut, et le menu rendu
entier quand le filtre ne trouve rien — ; elle les mesure désormais. Les
quatre autres étaient de vrais défauts :
  · TRENTE ET UN ONGLETS SANS DESSIN — tous ceux des tiroirs de « Votre Mise
    en Conformité Réglementaire », sauf le CRA. Leur pastille n'avait qu'un
    point de couleur : sept onglets de NIS 2, sept points identiques, et
    l'intitulé seul pour les distinguer. D'où deux échecs de plus : la
    recette cherche le dessin pour vérifier qu'il est muet et hors de la
    tabulation, et n'en trouvait pas ;
  · LA RUBRIQUE « COMPTE » SANS TEINTE : son titre prenait la terre cuite
    par défaut — la couleur qui dit « ici » — et son onglet restait gris.

CES RÈGLES LISENT LA PAGE SERVIE, et regroupent les onglets comme la barre
les montre : une suite de frères, chaque titre suivi de ses onglets.
"""
import io
import os
import re

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = io.open(os.path.join(_RACINE, "sentinel.html"), encoding="utf-8").read()


def _nav():
    i = HTML.index('class="sb-nav"')
    return HTML[i:HTML.index("</nav>", i)]


def _blocs():
    """[(rubrique, dessin du titre, [(intitulé, balise de l'onglet)])], dans
    l'ordre de la barre."""
    nav = _nav()
    rubriques = []
    for m in re.finditer(r'<div class="(sb-section|sb-item)[^"]*"[^>]*>.*?</div>', nav, re.S):
        bloc = m.group(0)
        if m.group(1) == "sb-section":
            grp = re.search(r'data-grp="([^"]+)"', bloc).group(1)
            svg = re.search(r"<svg[^>]*>(.*?)</svg>", bloc, re.S)
            rubriques.append((grp, _norme(svg.group(1)) if svg else None, []))
        elif rubriques:
            nom = re.sub(r"<[^>]+>", "", bloc).strip()
            rubriques[-1][2].append((nom, bloc))
    return rubriques


def _norme(dessin):
    return re.sub(r"\s+", "", dessin)


def _dessin(onglet):
    m = re.search(r'<span class="sb-icon"[^>]*>\s*(<svg[^>]*>)(.*?)</svg>', onglet, re.S)
    return (m.group(1), _norme(m.group(2))) if m else (None, None)


def test_la_barre_est_relevee():
    r = _blocs()
    assert len(r) >= 20 and sum(len(o) for _g, _d, o in r) >= 90, (
        "la barre n'a pas pu être relevée : %d rubriques" % len(r))


def test_CHAQUE_onglet_porte_son_dessin():
    sans = ["%s → %s" % (g, nom) for g, _d, onglets in _blocs()
            for nom, balise in onglets if _dessin(balise)[0] is None]
    assert not sans, "%d onglet(s) sans dessin : %s" % (len(sans), sans[:6])


def test_chaque_dessin_est_MUET_et_HORS_de_la_tabulation():
    """L'INTITULÉ EST ÉCRIT JUSTE À CÔTÉ : annoncer aussi l'icône le ferait
    dire deux fois, et la laisser prendre la tabulation ajouterait un arrêt
    qui ne mène nulle part."""
    fautifs = []
    for g, _d, onglets in _blocs():
        for nom, balise in onglets:
            svg, _ = _dessin(balise)
            if svg and ('aria-hidden="true"' not in svg or 'focusable="false"' not in svg):
                fautifs.append("%s → %s" % (g, nom))
    assert not fautifs, fautifs[:6]


def test_dans_une_rubrique_DEUX_onglets_ne_partagent_jamais_un_dessin():
    """C'EST LA SILHOUETTE QUI DISTINGUE, pas la couleur : dans un tiroir,
    tous les onglets portent la même couleur (WCAG 1.4.1)."""
    doublons, echos = [], []
    for g, chapeau, onglets in _blocs():
        vus = {}
        for nom, balise in onglets:
            d = _dessin(balise)[1]
            if d is None:
                continue
            if d in vus:
                doublons.append("%s : « %s » et « %s »" % (g, vus[d], nom))
            vus[d] = nom
            if chapeau and d == chapeau:
                echos.append("%s → %s" % (g, nom))
    assert not doublons, doublons
    assert not echos, "un onglet recopie le dessin de son chapeau : %s" % echos


def test_CHAQUE_rubrique_declare_sa_teinte():
    """SANS TEINTE, LE TITRE PREND LA TERRE CUITE — la couleur qui dit « ici »
    — et ses onglets le gris : la rubrique « Compte » l'a montré."""
    manquantes = [g for g, _d, _o in _blocs()
                  if not re.search(r'\.sb-nav \[data-grp="%s"\]\{--sb-ic:' % re.escape(g), HTML)]
    assert not manquantes, "rubriques sans teinte déclarée : %s" % manquantes


def test_la_rubrique_COMPTE_ne_porte_pas_la_terre_cuite():
    m = re.search(r'\.sb-nav \[data-grp="compte"\]\{--sb-ic:([^}]+)\}', HTML)
    assert m and "accent" not in m.group(1), (
        "« Compte » dirait « ici » en permanence : %r" % (m and m.group(1)))
