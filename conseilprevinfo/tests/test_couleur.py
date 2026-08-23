"""LA PALETTE — ce qu'une couleur a le droit d'affirmer, et à quel contraste.

CE SITE SE SERT DE LA COULEUR COMME D'UN VOCABULAIRE : le rouge dit qu'une
information rompt, le bleu classe le sujet, le vert qu'une source a été
confrontée, l'ambre qu'il y a une réserve. Un lecteur qui apprend ces quatre
codes lit la page sans lire les mots. C'est un gain réel, et c'est aussi une
dette : une teinte qui devient illisible ne se contente pas d'être laide, elle
retire une information au lecteur qui en dépend le plus.

DEUX DÉFAUTS D'ANCIENNETÉ ONT ÉTÉ TROUVÉS EN ÉCRIVANT CE FICHIER, et c'est
pour cela qu'il existe. Sur l'ancien fond crème, `--sourd2` donnait 3,37 de
contraste et `--ocre` 3,59 — la norme AA en demande 4,5 pour du texte. Le
premier peint « SIGNAL FAIBLE », le second « STRUCTURANT ». Ces deux pastilles
s'affichent des dizaines de fois par page, et personne ne l'avait vu parce que
personne ne l'avait mesuré. Les valeurs sont maintenant à 5,05 et 5,66.

CE QUI EST MESURÉ EST LA FEUILLE DE STYLE ELLE-MÊME, pas une table recopiée
ici : les valeurs sont lues dans `:root`. Un contrôle qui porterait sa propre
copie de la palette passerait le jour où quelqu'un changerait la vraie.
"""
import os
import re
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

CSS = open(os.path.join(ICI, "veille.css"), encoding="utf-8").read()


def _sans_commentaires(texte):
    """LES COMMENTAIRES PARLENT DES RÈGLES INTERDITES — c'est leur travail :
    ils disent pourquoi `background-attachment:fixed` a été écarté et pourquoi
    l'attribut `style` de conseilprevcyber ne peut pas être repris ici. Les
    compter comme des règles est une faute de contrôle, et elle a été commise
    au premier essai : trois contrôles accusaient le code de faire exactement
    ce que le commentaire d'à côté expliquait avoir évité."""
    return re.sub(r"/\*.*?\*/", "", texte, flags=re.S)


CODE_CSS = _sans_commentaires(CSS)

#: Le seuil AA pour du texte de taille courante. Les pastilles sont petites —
#: 9,5 px —, donc AA « grand texte » (3:1) ne s'applique en aucun cas.
AA = 4.5


def _palette():
    """Les variables de `:root`, lues dans la feuille."""
    bloc = CSS[CSS.index(":root{"):CSS.index("\n}", CSS.index(":root{"))]
    return {m.group(1): m.group(2)
            for m in re.finditer(r"--([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6})\s*;", bloc)}


P = _palette()

#: Les quatre familles du code éditorial, plus l'ocre qui en est une nuance.
CODE = ("rouge", "bleu", "vert", "ambre", "ocre")
#: Les gris de texte. `sourd2` en fait partie : il compose des étiquettes.
TEXTE = ("encre", "encre2", "sourd", "sourd2")
#: Les deux fonds sur lesquels tout ce qui précède peut se trouver.
FONDS = ("papier", "papier2")
#: Les teintes du menu — hors du code, et le contrôle ci-dessous l'exige.
NAV = ("nav-graphite", "nav-ardoise", "nav-prune", "nav-sable")


def _lum(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contraste(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def _melange(teinte, fond, part):
    """`color-mix(in srgb, teinte part%, transparent)` posé sur `fond`."""
    t = [int(teinte.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    f = [int(fond.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#%02X%02X%02X" % tuple(
        round(t[i] * part + f[i] * (1 - part)) for i in range(3))


def _saturation(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    hi, lo = max(c), min(c)
    if hi == lo:
        return 0.0
    l = (hi + lo) / 2
    return (hi - lo) / (2 - hi - lo) if l > 0.5 else (hi - lo) / (hi + lo)


# ── 1. Le contraste, sur les deux papiers ─────────────────────────────────

def test_la_palette_est_bien_lue_dans_la_feuille():
    """Sans cela, tout ce fichier vérifierait sa propre copie."""
    manquantes = [c for c in CODE + TEXTE + FONDS + NAV if c not in P]
    assert not manquantes, manquantes


def test_chaque_teinte_du_code_est_lisible_sur_les_deux_papiers():
    """Une teinte sous le seuil ne se contente pas d'être laide : elle retire
    une information au lecteur qui en dépend le plus."""
    faibles = []
    for nom in CODE + TEXTE:
        for fond in FONDS:
            r = contraste(P[nom], P[fond])
            if r < AA:
                faibles.append("%s sur %s : %.2f" % (nom, fond, r))
    assert not faibles, faibles


def test_chaque_pastille_est_lisible_sur_SON_PROPRE_fond():
    """Le fond d'une pastille est un voile de sa propre couleur : il éclaircit
    à peine, mais il éclaircit. Mesurer la teinte sur le papier nu passerait à
    côté du seul fond sur lequel elle se trouve réellement."""
    faibles = []
    for nom, part in (("rouge", .07), ("ocre", .08), ("sourd", .07),
                      ("bleu", .07), ("ambre", .07)):
        for fond in FONDS:
            f = _melange(P[nom], P[fond], part)
            r = contraste(P[nom], f)
            if r < AA:
                faibles.append("%s sur son voile (%s) : %.2f" % (nom, f, r))
    assert not faibles, faibles


def test_l_oreille_reste_lisible():
    """C'est la seule surface sombre du site : le papier y devient le texte."""
    assert contraste(P["papier"], P["encre"]) >= 7.0


def test_les_deux_defauts_corriges_ne_reviennent_pas():
    """`--sourd2` à #93866F et `--ocre` à #A9701F donnaient 3,37 et 3,59 sur
    l'ancien fond. Ce contrôle les nomme pour qu'une « restauration de la
    palette d'origine » ne les ramène pas sans qu'on s'en aperçoive."""
    assert P["sourd2"].upper() != "#93866F"
    assert P["ocre"].upper() != "#A9701F"
    for nom in ("sourd2", "ocre"):
        assert contraste(P[nom], P["papier2"]) >= AA


# ── 2. Les teintes du menu ne parlent pas le code ─────────────────────────

def test_les_teintes_du_menu_ne_sont_aucune_teinte_du_code():
    """Un menu peint en rouge et en vert apprendrait au lecteur un second
    vocabulaire de couleurs en face du premier."""
    codes = {P[c].upper() for c in CODE}
    for n in NAV:
        assert P[n].upper() not in codes, n


def test_les_teintes_du_menu_sont_desaturees_et_le_code_ne_l_est_pas():
    """La distinction ne tient pas qu'à la valeur exacte : deux rouges voisins
    seraient lus comme le même rouge. Les teintes du menu sont franchement
    plus sourdes que celles du code — c'est ce qui les empêche d'être prises
    pour lui, avec la forme (silhouette au trait contre étiquette pleine).
    Mesuré : la plus vive du menu est à 0,39, la plus sourde du code à 0,55."""
    plus_sourde = max(_saturation(P[n]) for n in NAV)
    plus_vive = min(_saturation(P[c]) for c in CODE)
    assert plus_sourde < plus_vive, (plus_sourde, plus_vive)
    assert plus_sourde < 0.40, plus_sourde


def test_les_icones_du_menu_restent_perceptibles():
    """Un pictogramme est un élément non textuel : WCAG 1.4.11 demande 3:1.

    LE SEUIL EST APPLIQUÉ À PLEINE INTENSITÉ, ET C'EST LE BON CRITÈRE — pas un
    seuil déplacé pour passer. Le critère 1.4.11 vise ce qui est NÉCESSAIRE à
    la compréhension ; une image purement décorative en est exemptée. Ici
    l'intitulé est écrit à côté de chaque icône, et
    `test_la_silhouette_n_est_jamais_seule_a_porter_l_information` est ce qui
    l'exige. Les icônes d'entrée, atténuées, sont donc décoratives au sens
    strict du texte — mais les icônes de GROUPE et les filets teintés portent
    l'identité du groupe à pleine intensité, et eux doivent tenir le seuil.

    La tentation était l'inverse : imposer 3:1 à l'opacité réduite. Essayé,
    mesuré — il ne restait que des teintes à 0,10 de saturation, c'est-à-dire
    quatre gris. Un contrôle trop strict au mauvais endroit avait supprimé la
    distinction qu'il était censé protéger."""
    for n in NAV:
        for fond in FONDS:
            r = contraste(P[n], P[fond])
            assert r >= 3.0, "%s sur %s : %.2f" % (n, fond, r)


# ── 3. Une couleur ne s'écrit qu'une fois ─────────────────────────────────

def test_aucune_teinte_de_la_palette_n_est_recopiee_en_rgba():
    """DÉFAUT TROUVÉ EN CHANGEANT DE PAPIER. Les fonds de pastille étaient
    écrits `rgba(158,31,20,.07)` — les composantes de l'ancien rouge. Le texte
    suivait la variable, le fond non : après la retouche, chaque pastille
    portait un texte d'une teinte sur un voile d'une autre. À sept pour cent
    d'opacité personne ne l'aurait vu, ce qui est exactement le problème."""
    interdits = []
    for nom in CODE + TEXTE + FONDS + NAV:
        h = P[nom].lstrip("#")
        rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
        motif = re.compile(r"rgba?\(\s*%d\s*,\s*%d\s*,\s*%d\s*[,)]" % rgb)
        # Les ombres sont grises et dérivent de l'encre : elles ont le droit.
        for m in motif.finditer(CSS):
            ligne = CSS[:m.start()].count("\n") + 1
            contexte = CSS[max(0, m.start() - 120):m.start()]
            if "box-shadow" in contexte or "--ombre" in contexte:
                continue
            interdits.append("%s recopié ligne %d" % (nom, ligne))
    assert not interdits, interdits


def test_les_voiles_de_pastille_derivent_de_leur_variable():
    """La règle précédente dit ce qui est interdit ; celle-ci dit ce qui a
    remplacé la copie, pour qu'un retour en arrière soit visible."""
    for nom in ("rouge", "ocre", "sourd", "bleu"):
        assert "color-mix(in srgb,var(--%s)" % nom in CSS.replace("\n", ""), nom


# ── 4. Le papier couché : ce qui le distingue d'un crème refroidi ─────────

def test_la_feuille_porte_son_reflet():
    """Sans le reflet, il ne reste qu'un crème refroidi. C'est lui qui fait la
    différence entre un mat et un couché à l'œil nu, et il est la raison même
    du changement de papier — le retirer viderait la décision de son objet."""
    serre = CSS.replace(" ", "").replace("\n", "")
    assert "body::before{" in serre
    i = serre.index("body::before{")
    bloc = serre[i:i + 420]
    assert "position:fixed" in bloc and "z-index:-1" in bloc
    assert "radial-gradient" in bloc and "linear-gradient" in bloc
    # Il ne doit pas capter le clic ni le défilement.
    assert "pointer-events:none" in bloc


def test_le_reflet_n_est_pas_un_fond_attache():
    """`background-attachment:fixed` fait le même effet et hache le
    défilement sur téléphone : le navigateur recompose la peinture de fond à
    chaque image. Une couche fixe, elle, n'est peinte qu'une fois."""
    assert "background-attachment:fixed" not in CODE_CSS.replace(" ", "")


def test_la_carte_porte_le_lustre_et_une_ombre_presque_absente():
    """Une ombre qu'on remarque fait une interface à cartes flottantes, ce que
    ce site n'est pas ; une ombre qu'on ne remarque pas fait du papier."""
    serre = CSS.replace(" ", "").replace("\n", "")
    assert "--lustre:linear-gradient(180deg,#FFFFFF0%,var(--papier)100%)" in serre
    # LA RÈGLE PRINCIPALE, pas la première trouvée : `.fiche{` apparaît aussi
    # sous une requête de média, où elle ne redéfinit qu'un espacement. Premier
    # essai tombé là-dessus — un contrôle qui prend la première occurrence d'un
    # sélecteur lit souvent une autre règle que celle qu'il croit lire.
    regles = [serre[m.end():serre.index("}", m.end())]
              for m in re.finditer(r"(?<![a-z0-9.-])\.fiche\{", serre)]
    assert any("background:var(--lustre)" in r for r in regles), regles[:2]
    # L'ombre au repos reste sous 10 % d'opacité : au-delà, ce sont des cartes.
    for m in re.finditer(r"--ombre:([^;]+);", CODE_CSS):
        for a in re.findall(r"rgba\([^)]*,\s*\.(\d+)\)", m.group(1)):
            assert int(a) <= 10, m.group(1)


# ── 5. Le menu emploie les caractères du journal ──────────────────────────

def test_le_menu_nomme_dans_la_fonte_du_journal():
    """Il composait les intitulés en Inter — la fonte des libellés d'interface.
    « Le fil » dans la colonne et « Le fil » en tête de rubrique, à trente
    centimètres l'un de l'autre, n'avaient pas le même dessin : la colonne
    semblait appartenir à un autre site que la page."""
    serre = CSS.replace(" ", "").replace("\n", "")
    for regle in (".bl-lab{", ".bl-sa{"):
        i = serre.index(regle)
        assert "font-family:var(--serif)" in serre[i:i + 220], regle
    # Les libellés de groupe et les compteurs restent en monospace : ils
    # étiquettent et mesurent, ils ne nomment pas.
    i = serre.index(".bl-t{")
    assert "font-family:var(--fix)" in serre[i:i + 260]
    i = serre.index(".bl-sai{")
    assert "font-family:var(--fix)" in serre[i:i + 200]
    # Et aucune quatrième fonte n'est introduite.
    familles = set(re.findall(r"font-family:\s*var\(--([a-z]+)\)", CSS))
    assert familles <= {"serif", "sans", "fix"}, familles


def test_chaque_groupe_du_menu_porte_sa_teinte_par_une_classe():
    """conseilprevcyber l'écrit en attribut `style` sur chaque section. Ici la
    politique de sécurité de contenu se ferme sur `style-src 'self'` : un
    attribut `style` serait refusé par le navigateur lui-même, et les icônes
    sortiraient toutes grises sans qu'une erreur ne s'affiche nulle part."""
    b = open(os.path.join(ICI, "barre.js"), encoding="utf-8").read()
    assert "--nav-ic" not in _sans_commentaires(b), \
        "la teinte est posée en attribut style"
    assert "'<section class=\"bl-g g-' + cle + '\">'" in b
    serre = CSS.replace(" ", "").replace("\n", "")
    for g in ("corpus", "site", "sections", "legende"):
        assert ".bl-g.g-%s{--nav-ic:" % g in serre, g
