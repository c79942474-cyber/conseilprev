"""La page investisseurs sur un fond photographique : mesurer, pas affirmer.

LE DÉFAUT, ET IL S'EST VU AVANT D'ÊTRE MESURÉ. Le fond de page est une PHOTO.
Avec une opacité de 30 % et des panneaux transparents à 95 %, le texte était
posé sur l'image : 4,24:1 pour le corps sur les zones claires, 2,29:1 pour les
explications grises. En dessous du seuil AA, et illisible à l'œil — c'est un
lecteur qui l'a signalé, pas la suite.

POURQUOI AUCUNE RÈGLE NE L'AVAIT VU. Les contrôles de la page mesuraient ce
qu'elle DIT et ce que ses onglets FONT. Aucun ne mesurait ce qu'elle se donne à
lire. Une page peut être juste, complète, accessible au clavier — et illisible.

CE QUE CES RÈGLES FONT, ET CE QU'ELLES NE FONT PAS. Elles recalculent le
contraste à partir de trois sources : les valeurs lues DANS LA FEUILLE de la
page, les pixels lus DANS L'IMAGE, et la formule de luminance relative de
WCAG 2. Elles ne jugent pas du goût, ni du rendu d'un écran réel — cela se
constate dans un navigateur, ce qui a été fait.

LE PIÈGE QU'ELLES ÉVITENT. Une règle qui vérifierait « le panneau a un fond »
passerait sur rgba(…,.05), qui est un fond au sens de la syntaxe et un voile au
sens de l'œil. C'est le contraste COMPOSITÉ qui décide, et lui seul.
"""
import io
import os
import re

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = io.open(os.path.join(ICI, "investisseurs.html"), encoding="utf-8").read()

#: Le plancher. 4,5:1 est le seuil AA du texte courant (WCAG 2.1, critère
#: 1.4.3). On ne s'en contente pas : sur un fond dont les pixels varient, une
#: marge est ce qui empêche un contraste juste en moyenne d'être faux quelque
#: part. Le plancher retenu vaut donc 5,0:1 pour tout texte.
PLANCHER = 5.0


# ── LA MESURE ─────────────────────────────────────────────────────────────

def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _luminance(rgb):
    r, g, b = rgb
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def _contraste(a, b):
    la, lb = _luminance(a), _luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _composer(dessus, dessous, alpha):
    return tuple(dessus[i] * alpha + dessous[i] * (1 - alpha) for i in range(3))


def _hexa(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ── CE QUE LA PAGE DÉCLARE, RELU DANS LA FEUILLE ─────────────────────────

def _variable(nom):
    m = re.search(r"--%s:\s*(#[0-9a-fA-F]{3,6})" % re.escape(nom), PAGE)
    assert m, "la variable --%s n'est plus une couleur pleine" % nom
    return _hexa(m.group(1))


def _fond_rgba(selecteur):
    """Le fond d'un sélecteur : (couleur, alpha), relu dans la feuille."""
    m = re.search(r"\.%s\{[^}]*background:\s*rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)"
                  % re.escape(selecteur), PAGE)
    assert m, "le sélecteur .%s n'a pas de fond rgba() lisible" % selecteur
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))), float(m.group(4))


def _opacite_photo():
    m = re.search(r"body::before\{[^}]*opacity:\s*([\d.]+)", PAGE)
    assert m, "l'opacité du fond photographique est introuvable"
    return float(m.group(1))


def _degrade_le_plus_clair():
    """L'arrêt le plus CLAIR du dégradé du corps — celui qui décide du pire."""
    m = re.search(r"body\{[^}]*linear-gradient\(([^)]*)\)", PAGE)
    assert m, "le dégradé du corps est introuvable"
    couleurs = re.findall(r"#[0-9a-fA-F]{6}", m.group(1))
    assert len(couleurs) >= 2, couleurs
    return max((_hexa(c) for c in couleurs), key=_luminance)


def _photo_extremes():
    """La photo de fond, mesurée — jamais supposée.

    LE PIRE PIXEL DÉCIDE. Prendre la moyenne dirait « c'est lisible en général »
    d'une page qui ne l'est pas là où l'image s'éclaircit — et c'est précisément
    là que le lecteur a buté."""
    chemin = os.path.join(ICI, "hero-bg.jpg")
    if not os.path.exists(chemin):
        pytest.skip("hero-bg.jpg absent : le fond ne peut pas être mesuré")
    try:
        from PIL import Image
    except ImportError:
        pytest.skip("Pillow absent : les pixels du fond ne peuvent pas être lus")
    im = Image.open(chemin).convert("RGB")
    im.thumbnail((200, 200))
    px = list(im.getdata())
    assert px, "l'image de fond est vide"
    return max(px, key=_luminance), min(px, key=_luminance)


def _sol(dans_un_panneau):
    """Le fond RÉELLEMENT sous le texte, dans le pire cas de la photo."""
    clair, _ = _photo_extremes()
    base = _composer(clair, _degrade_le_plus_clair(), _opacite_photo())
    if not dans_un_panneau:
        return base
    couleur, alpha = _fond_rgba("bloc")
    return _composer(couleur, base, alpha)


# ═══════════════════════════════════════════════════════════════════════════
#  LE CONTRASTE, CALCULÉ
# ═══════════════════════════════════════════════════════════════════════════

def test_la_mesure_du_fond_repose_sur_une_image_REELLE():
    """LE TÉMOIN. Si l'image devenait introuvable ou uniformément noire, tous
    les contrastes ci-dessous seraient excellents et ne mesureraient rien."""
    clair, sombre = _photo_extremes()
    assert _luminance(clair) > 0.5, (
        "le pixel le plus clair du fond est à %.3f : l'image ne met plus le "
        "texte en difficulté, la mesure ne prouve plus rien" % _luminance(clair))
    assert _luminance(clair) > _luminance(sombre)


@pytest.mark.parametrize("role,variable", [
    ("corps de texte", "pp"),
    ("titres et valeurs", "wh"),
    ("gris des explications", "mu"),
    ("accent des sous-titres", "teal"),
])
def test_DANS_un_panneau_chaque_couleur_de_texte_passe_le_plancher(role, variable):
    """Le panneau doit être un SOL, pas un voile : sous une photo dont on ne
    maîtrise pas les pixels, seule son opacité tient."""
    c = _contraste(_variable(variable), _sol(True))
    assert c >= PLANCHER, (
        "%s : %.2f:1 sur la zone la plus claire de la photo — plancher %.1f:1"
        % (role, c, PLANCHER))


@pytest.mark.parametrize("role,variable", [
    ("chapeau", "pp"),
    ("titre de page", "wh"),
    ("onglet inactif", "mu"),
    ("sur-titre", "pf"),
])
def test_HORS_panneau_le_texte_passe_AUSSI_le_plancher(role, variable):
    """LE POINT QU'ON OUBLIE. Le titre, le chapeau et la rangée d'onglets ne
    sont dans aucun panneau : ils n'ont que l'opacité de la photo pour eux.
    Rendre les panneaux opaques sans faire reculer l'image les laisserait
    exactement là où ils étaient."""
    c = _contraste(_variable(variable), _sol(False))
    assert c >= PLANCHER, (
        "%s (hors panneau) : %.2f:1 — plancher %.1f:1" % (role, c, PLANCHER))


def test_le_GRIS_est_une_couleur_pleine_et_non_une_transparence():
    """UNE COULEUR À 52 % LAISSE PASSER CE QU'IL Y A DESSOUS — donc la photo.
    C'est ce qui mettait les explications à 2,29:1. Le contraste calculé sur la
    couleur nominale serait alors juste, et l'écran faux : la règle mesure donc
    la DÉCLARATION, qui est le seul endroit où la transparence se voit."""
    m = re.search(r"--mu:\s*([^;]+);", PAGE)
    assert m, "la variable --mu a disparu"
    assert "rgba" not in m.group(1), (
        "--mu est déclarée en rgba : le fond transparaît sous le texte gris "
        "(%s)" % m.group(1).strip())


def _ecart_de_contraste(fond, variable):
    """De combien le contraste du texte VARIE entre la zone la plus claire de
    la photo et la plus sombre, sous ce panneau.

    C'EST LA MESURE QUI DIT « sol ou voile ». Un seuil d'opacité est un
    constat de syntaxe : rgba(…,.05) est un fond au sens du langage et un voile
    au sens de l'œil, et rien dans le nombre ne les distingue. Ce qu'un sol
    fait, lui, se mesure : il APLATIT la variation de l'image sous le texte.
    Un voile la laisse passer, et le texte devient lisible par endroits."""
    clair, sombre = _photo_extremes()
    couleur, alpha = fond
    fond_clair = _composer(couleur, _composer(clair, _degrade_le_plus_clair(),
                                              _opacite_photo()), alpha)
    fond_sombre = _composer(couleur, _composer(sombre, _degrade_le_plus_clair(),
                                               _opacite_photo()), alpha)
    t = _variable(variable)
    return abs(_contraste(t, fond_clair) - _contraste(t, fond_sombre))


@pytest.mark.parametrize("selecteur", ["bloc", "reserve"])
def test_un_panneau_APLATIT_la_photo_au_lieu_de_la_laisser_passer(selecteur):
    """LE BLOC ET LA RÉSERVE portent tous deux du texte courant. N'en durcir
    qu'un laisserait l'autre exactement dans l'état signalé — et c'est la
    réserve, la plus dense, qui porte les points de droit.

    LE SEUIL EST UN ÉCART, PAS UNE OPACITÉ. Avant correction, le contraste du
    corps de texte passait de 8,18:1 sur les zones sombres à 4,24:1 sur les
    claires : près de quatre points d'écart, et c'est cet écart que le lecteur
    voit comme « lisible ici, pas là ». Un panneau qui fait sol le ramène sous
    un point."""
    for variable in ("pp", "mu"):
        ecart = _ecart_de_contraste(_fond_rgba(selecteur), variable)
        assert ecart <= 1.0, (
            ".%s : le contraste de --%s varie de %.2f points entre les zones "
            "claires et sombres de la photo — le panneau laisse passer l'image"
            % (selecteur, variable, ecart))


def test_le_TEMOIN_un_panneau_transparent_laisse_bien_passer_la_photo():
    """SANS CE TÉMOIN, la règle précédente passerait aussi bien sur une photo
    uniforme, où aucun panneau ne changerait rien. Elle éprouve donc qu'un
    voile PRODUIT l'écart qu'un sol supprime.

    ET IL PASSE PAR LA MÊME FONCTION, ce qui est le point. Une première version
    refaisait le calcul à la main : une mutation qui faisait rendre zéro à
    `_ecart_de_contraste` rendait la règle du panneau vacante — elle passait sur
    n'importe quoi — et le témoin, calculant de son côté, ne s'apercevait de
    rien. Un témoin qui n'emprunte pas le chemin qu'il éprouve ne l'éprouve
    pas."""
    ecart = _ecart_de_contraste(((139, 92, 246), 0.05), "pp")
    assert ecart > 1.0, (
        "un panneau à 5 %% d'opacité ne fait varier le contraste que de %.2f "
        "point : la mesure ne distingue plus un sol d'un voile" % ecart)


def test_le_pied_de_page_miniature_n_est_pas_pose_sur_la_photo():
    """Il est hors de la grille principale, et son texte emploie le gris."""
    _, alpha = _fond_rgba("ft-mini")
    assert alpha >= 0.80, alpha


def test_le_fond_photographique_a_RECULE_et_la_page_le_dit():
    """LA VALEUR SEULE NE SE RELIT PAS. Un successeur qui trouverait 16 % sans
    savoir pourquoi la remonterait au premier souci d'esthétique."""
    assert _opacite_photo() <= 0.20, _opacite_photo()
    tete = PAGE[:PAGE.index("</style>")]
    assert "LA LISIBILITÉ SUR UNE PHOTO" in tete
    for mot in ("4,24:1", "2,29:1", "photo"):
        assert mot in tete, "le motif de la correction ne cite pas %r" % mot


def test_le_mouvement_reduit_est_respecte():
    """Une page qui fige tout SAUF son fond n'a rien réglé pour qui a demandé
    du calme."""
    assert "prefers-reduced-motion" in PAGE
