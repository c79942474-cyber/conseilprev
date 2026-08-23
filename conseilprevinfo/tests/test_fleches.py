"""LES QUATRE FLÈCHES — et la règle qu'elles sont là pour tenir.

AUCUN BOUTON NE FAIT SILENCIEUSEMENT RIEN. C'est la seule règle de ce fichier,
et elle est moins évidente qu'elle en a l'air : le montage habituel — ← et →
câblés sur l'historique du navigateur — produit une flèche « suivant » qui ne
fait rien dans la quasi-totalité des cas, puisqu'il n'y a de page suivante que
si l'on vient de reculer. Le navigateur éteint la sienne ; une flèche dessinée
dans la page ne le peut pas, faute d'API. Elle reste allumée et morte.

C'est le même défaut que celui qu'un menu de filtre vide produisait sur ce
site — un axe qui ne donne rien mais se présente comme s'il donnait quelque
chose — et il se corrige de la même façon : en le disant.
"""
import os
import re
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)


def _lire(nom):
    return open(os.path.join(ICI, nom), encoding="utf-8").read()


def _sens():
    """Le bloc qui résout les quatre sens, isolé."""
    js = _lire("fleches.js")
    return js[js.index("function sens()"):js.index("/* ── LA POSE")]


# ── 1. Aucun bouton muet ──────────────────────────────────────────────────

def test_une_fleche_sans_emploi_est_eteinte_et_dit_pourquoi():
    """Éteinte SANS motif, elle se lit comme une panne ; avec le motif, elle
    enseigne comment s'en servir. Et jamais retirée : la croix sauterait d'une
    forme à l'autre au fil des pages, et le lecteur ne saurait plus où viser."""
    js = _lire("fleches.js")
    i = js.index("function peindre()")
    bloc = js[i:i + 700]
    assert "b.disabled = !e.faire;" in bloc, bloc
    assert "b.title = e.dit;" in bloc
    assert 'b.setAttribute("aria-label", e.dit);' in bloc
    # et le clic ne fait rien si le sens n'a pas de geste
    assert "if (b && b.__faire) b.__faire();" in js
    css = _lire("veille.css")
    assert ".fl-b-t[disabled]{" in css.replace("\n", "")


def _objet_autour(texte, i):
    """L'objet littéral qui contient la position `i`, accolades équilibrées.

    Écrit à la main plutôt qu'en expression régulière : une expression sur des
    accolades imbriquées se trompe toujours, et elle s'est effectivement
    trompée ici au premier essai — `faire: function () { … }` était lu comme un
    objet clos par l'accolade de la FONCTION, si bien que le contrôle accusait
    un sens parfaitement valide."""
    debut = texte.rindex("{", 0, i)
    n, j = 0, debut
    while j < len(texte):
        if texte[j] == "{":
            n += 1
        elif texte[j] == "}":
            n -= 1
            if n == 0:
                return texte[debut:j + 1]
        j += 1
    raise AssertionError("objet non refermé")


def test_chaque_sens_porte_toujours_un_intitule():
    """Une entrée qui rendrait `{ faire }` sans `dit` produirait exactement le
    bouton muet que ce fichier interdit."""
    bloc = _sens()
    trouves = 0
    for m in re.finditer(r"\bfaire:", bloc):
        # On remonte à l'objet littéral, pas à la fonction que `faire` porte.
        i = m.start()
        obj = _objet_autour(bloc, i + 1) if bloc[i - 1] != "{" else None
        obj = obj or _objet_autour(bloc, i)
        assert "dit:" in obj, "un sens sans intitulé : " + obj[:120]
        trouves += 1
    assert trouves >= 3, trouves
    # Et les sens éteints, eux, ne portent QUE `dit`.
    assert bloc.count("dit:") > trouves


def test_les_intitules_sont_traduits():
    """Une infobulle française sous une interface anglaise est le genre de
    reste qui fait douter du reste."""
    lg = _lire("langue.js")
    cles = set()
    for nom in ("fleches.js", "veille.js"):
        cles |= set(re.findall(r'"(fl\.[a-z.]+)"', _lire(nom)))
    assert len(cles) >= 12, cles
    manquantes = sorted(c for c in cles if '"%s":' % c not in lg)
    assert not manquantes, manquantes


# ── 2. Haut et bas ────────────────────────────────────────────────────────

def test_haut_et_bas_s_eteignent_sur_une_page_courte():
    """Sur une page qui tient à l'écran, « bas de page » emmène à un endroit
    déjà visible."""
    js = _lire("fleches.js")
    assert "var SEUIL = 1.5;" in js
    bloc = _sens()
    assert "longue ?" in bloc and 'dit: t("fl.courte")' in bloc


def test_le_defilement_respecte_la_demande_de_moins_d_animation():
    js = _lire("fleches.js")
    assert "prefers-reduced-motion" in js
    i = js.index("function aller(")
    assert 'douce() ? "smooth" : "auto"' in js[i:i + 200]


# ── 3. L'ordre de lecture ─────────────────────────────────────────────────

def test_l_ordre_est_celui_qui_est_AFFICHÉ_et_il_est_noté_une_seule_fois():
    """Le reconstruire ailleurs, même correctement, produirait tôt ou tard un
    « suivant » qui n'est pas celui de l'écran. Il est noté là où la une et le
    fil viennent d'être rendus, à partir de la même liste."""
    v = _lire("veille.js")
    assert v.count("window.FL.noter(") == 1, "l'ordre est noté à plusieurs endroits"
    i = v.index("window.FL.noter(")
    bloc = v[i:i + 300]
    assert "toutes.map(" in bloc, bloc
    # `toutes` est bien la liste servie, avant séparation une / fil
    assert "var toutes = d.fiches || [];" in v
    j = v.index("var toutes = d.fiches || [];")
    assert j < i, "l'ordre est noté avant que la liste existe"


def test_l_ordre_meurt_avec_l_onglet():
    """C'est un fil de lecture en cours, pas une trace. `localStorage` le
    garderait des mois après que le lecteur a changé de sujet."""
    js = _lire("fleches.js")
    assert 'CLE_ORDRE = "cpinfo.ordre"' in js
    assert "sessionStorage.setItem(CLE_ORDRE" in js
    assert "localStorage" not in js, "l'ordre survivrait à l'onglet"


def test_l_ordre_est_a_l_inventaire():
    """Toute clé écrite dans le navigateur figure à /confidentialite — la
    règle vaut pour celle-ci comme pour les autres."""
    assert "<code>cpinfo.ordre</code>" in _lire("confidentialite.html")


def test_l_identifiant_courant_vient_de_l_adresse():
    """Les flèches se posent avant que la fiche soit revenue du serveur : les
    lire dans le contenu rendu les ferait apparaître après le lecteur."""
    js = _lire("fleches.js")
    i = js.index("function ficheCourante()")
    bloc = js[i:i + 220]
    assert "location.pathname.match" in bloc, bloc
    assert "querySelector" not in bloc


def test_les_flèches_ne_se_posent_pas_deux_fois():
    js = _lire("fleches.js")
    assert "if (window.__FLECHES) return;" in js
    assert 'if (document.getElementById("fl")) return;' in js


def test_les_sens_sont_recalcules_quand_la_page_change():
    """La page s'allonge quand les fiches arrivent : quatre sens résolus une
    fois pour toutes diraient « la page tient à l'écran » sur un fil de
    quatre-vingt-dix-huit fiches. Et la rubrique courante change au
    défilement, donc les deux flèches latérales aussi."""
    js = _lire("fleches.js")
    bloc = js[js.index("function demarrer()"):]
    for signal in ('document.addEventListener("langue", peindre)',
                   'window.addEventListener("resize", peindre)',
                   'window.addEventListener("scroll"',
                   "MutationObserver"):
        assert signal in bloc, signal
    # Le défilement est étranglé : quatre sens recalculés à chaque événement
    # feraient tressauter la page.
    assert "requestAnimationFrame" in bloc


def test_hors_fiche_les_deux_fleches_parcourent_les_rubriques():
    """Laisser ← et → mortes sur la première page du site aurait fait de la
    moitié de la croix un ornement. La page possède bien une suite ordonnée —
    ses rubriques — et elle est LUE dans la page, comme celles de la barre."""
    bloc = _sens()
    assert "rubriques()" in bloc and "rangRubrique(" in bloc
    assert 'fl.rub.prem' in bloc and 'fl.rub.dern' in bloc
    # LA BRANCHE EST BIEN VIVANTE. Défaut du premier contrôle, trouvé en
    # mutant `if (hs.length > 1)` en `if (false)` : il vérifiait que le code
    # des rubriques EXISTE, pas qu'on y entre. Les deux flèches redevenaient
    # mortes sur la première page sans qu'un seul contrôle bouge.
    assert "if (hs.length > 1) {" in bloc, "la branche des rubriques est condamnée"
    i = bloc.index("if (hs.length > 1) {")
    assert "versRub(r - 1)" in bloc[i:] and "versRub(r + 1)" in bloc[i:]
    js = _lire("fleches.js")
    i = js.index("function rubriques()")
    assert 'querySelectorAll("main h2.rubrique[id]")' in js[i:i + 700]
    # La rubrique courante est la DERNIÈRE passée sous la marge haute :
    # prendre la plus proche du centre ferait reculer d'une rubrique au moment
    # où l'on vient d'en atteindre une.
    j = js.index("function rangRubrique(")
    assert "<= MARGE_HAUT + 1" in js[j:j + 400]


def test_les_flèches_sont_sur_toutes_les_pages():
    for nom in ("index.html", "fiche.html", "abonnement.html",
                "confronter.html", "confidentialite.html"):
        assert '<script src="/fleches.js" defer></script>' in _lire(nom), nom
