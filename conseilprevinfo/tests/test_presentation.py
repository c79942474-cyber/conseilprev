"""LA MISE EN PAGE — ce qu'elle a le droit de dire, et ce qu'elle ajouterait.

UNE MISE EN PAGE PEUT MENTIR AUSSI SÛREMENT QU'UN TEXTE. Donner à une fiche
plus de place, c'est affirmer qu'elle compte davantage ; le faire sur un
critère que le moteur ne porte pas reviendrait à noter l'information — ce que
ce site refuse partout ailleurs.

D'OÙ LA RÈGLE : la présentation REND LISIBLE l'ordre du moteur, elle n'en
invente aucun. La tête de première page est la première fiche du tri déjà
publié — « le plus important d'abord, puis le plus récent ». Le jour où ce tri
change, la tête change avec lui, sans qu'une ligne de mise en page soit
touchée.

ET ELLE NE DOIT PAS DEVENIR UN OBSTACLE. Une barre d'outils qui prend
quarante-quatre pour cent d'un écran de téléphone a cessé d'être un outil.
"""
import os
import re
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)


def _lire(nom):
    return open(os.path.join(ICI, nom), encoding="utf-8").read()


# ── 1. La tête de une n'ajoute aucun jugement ─────────────────────────────

def test_la_tete_est_la_premiere_du_tri_publie():
    """Elle n'est pas choisie : elle est la première de la liste que le moteur
    a déjà classée. Un critère de mise en page — « la plus longue », « celle
    qui a une image » — ferait de la page une seconde autorité en face du
    moteur."""
    js = _lire("veille.js")
    i = js.index('$("une").innerHTML')
    bloc = js[i:i + 400]
    assert 'i === 0 ? "tete"' in bloc, bloc[:200]
    # aucune autre condition ne décide de la tête
    for interdit in ("length >", "sort(", "Math.max", "score"):
        assert interdit not in bloc, interdit


def test_la_une_ne_retient_que_ce_qui_rompt():
    """La composition ne change pas ce qui y entre : la une reste la seule
    portée « rupture », et ne se remplit pas des fiches suivantes."""
    js = _lire("veille.js")
    assert 'f.impact === "rupture"' in js
    i = js.index('var une = toutes.filter')
    assert "slice(" not in js[i:i + 200], "la une est coupée à un nombre arbitraire"


def test_le_tri_du_moteur_est_bien_celui_qu_on_rend_lisible():
    """Le commentaire de `filtrer()` annonce « le plus important d'abord, puis
    le plus récent ». Si ce tri disparaissait, la tête cesserait de vouloir
    dire quelque chose — et rien à l'écran ne le signalerait."""
    py = _lire("veille.py")
    i = py.index("def filtrer(")
    bloc = py[i:i + 2600]
    assert "out.sort(" in bloc
    assert 'IMPACTS.get(f.get("impact"), {}).get("rang"' in bloc


# ── 2. La barre recopie, elle ne recalcule pas ────────────────────────────

def test_l_etat_de_la_barre_vient_du_meme_calcul_que_le_bandeau():
    """Un second calcul, même juste, finirait par afficher un autre nombre que
    celui d'à côté. La barre est remplie DANS `rendreEtat`, à partir des mêmes
    variables — elle ne refait aucune addition."""
    js = _lire("veille.js")
    i = js.index("function rendreEtat")
    fin = js.index("\n  /* LE NUMÉRO DE DEMANDE", i)
    bloc = js[i:fin]
    assert '$("bl-etat")' in bloc, "la barre est remplie ailleurs que dans rendreEtat"
    assert "et.fiches" in bloc and "mauvaises.length" in bloc


def test_la_barre_ne_sait_pas_compter_des_fiches():
    """Elle réserve la place, le moteur écrit dedans. Si `barre.js` se mettait
    à interroger l'API, la barre deviendrait une seconde source de vérité."""
    b = _lire("barre.js")
    assert 'id="bl-etat"' in b
    assert "/api/" not in b, "la barre latérale interroge le serveur"


# ── 3. Le repli des filtres ───────────────────────────────────────────────

def test_le_compte_de_filtres_actifs_vient_de_la_table_unique():
    """Un compte tenu à part finirait par annoncer « 2 actifs » sur une page
    qui n'en applique qu'un. Il se calcule sur `FILTRES`, la même table qui
    sert à interroger le serveur et à écrire l'adresse."""
    js = _lire("veille.js")
    i = js.index("function compterActifs")
    bloc = js[i:i + 400]
    assert "FILTRES.filter(" in bloc, bloc[:200]


def test_le_repli_ne_vaut_que_sur_petit_ecran():
    """Au-dessus de 900 px la barre tient sur deux lignes : la replier serait
    une gêne pour rien, et cacher des filtres qu'on voyait est une perte."""
    css = _lire("veille.css")
    assert ".f-plier{display:none}" in css.replace(" ", "")
    i = css.index("@media (max-width:899px)")
    bloc = css[i:i + 1400]
    assert ".f-plier{" in bloc.replace(" ", "").replace("\n", "")
    assert ".filtres .in{display:none}" in bloc


def test_le_bouton_de_repli_declare_ce_qu_il_commande():
    """`aria-expanded` et `aria-controls` ne sont pas décoratifs : sans eux,
    un lecteur d'écran annonce un bouton sans dire s'il ouvre ou ferme, ni
    quoi."""
    h = _lire("index.html")
    i = h.index('id="f-plier"')
    bloc = h[i - 200:i + 300]
    assert 'aria-expanded="false"' in bloc
    assert 'aria-controls="f-champs"' in bloc
    js = _lire("veille.js")
    assert 'plier.setAttribute("aria-expanded"' in js


def test_la_mesure_qui_a_motive_le_repli_est_ecrite():
    """« 44 % de l'écran » n'est pas une impression : c'est une mesure prise au
    navigateur, et elle est écrite là où quelqu'un serait tenté de défaire le
    repli en le trouvant inutile."""
    css = _lire("veille.css")
    assert "373 px" in css and "QUARANTE-QUATRE POUR" in css
