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
    # Et aucune fonte hors des CINQ déclarées n'est introduite. Elles étaient
    # trois ; deux caractères de presse s'y sont ajoutés, chacun avec un rôle
    # écrit — voir le contrôle suivant, qui garde ces rôles plutôt que de se
    # contenter de compter.
    familles = set(re.findall(r"font-family:\s*var\(--([a-z]+)\)", CSS))
    assert familles <= {"serif", "sans", "fix", "titre", "gothique"}, familles


def _taille_mini(corps):
    """La plus petite taille qu'une règle puisse rendre. `clamp(a,b,c)` en
    rend `a` : c'est cette borne-là qui décide si un dessin tient."""
    m = re.search(r"font-size:\s*clamp\(\s*([\d.]+)px", corps)
    if m:
        return float(m.group(1))
    m = re.search(r"font-size:\s*([\d.]+)px", corps)
    return float(m.group(1)) if m else None


def test_le_caractere_de_titre_ne_descend_pas_sous_dix_huit_pixels():
    """CE N'EST PAS UNE PRÉFÉRENCE, C'EST UNE RÈGLE DE COMPOSITION. Playfair a
    des déliés très fins : à douze pixels sur un écran ordinaire, ils
    disparaissent purement et simplement, et le mot se met à clignoter d'un
    pixel à l'autre selon l'arrondi. Le caractère de texte fait exactement
    l'inverse — Newsreader est dessiné pour tenir en petit corps.

    Un titre de carte à vingt-et-un pixels le porte donc ; une glose à douze ne
    doit jamais le porter. Ce contrôle tombe le jour où quelqu'un l'appliquera
    à un libellé « pour l'harmonie »."""
    fautes = []
    for m in re.finditer(r"(?m)^([^{}\n][^{\n]*)\{([^}]*)\}", CODE_CSS):
        sel, corps = m.group(1).strip(), m.group(2)
        if "var(--titre)" not in corps:
            continue
        t = _taille_mini(corps)
        # UNE RÈGLE SANS TAILLE HÉRITE DE LA SIENNE : elle n'est pas jugée ici,
        # mais elle doit être rare et volontaire.
        if t is not None and t < 18:
            fautes.append("%s : %spx" % (sel, t))
    assert not fautes, fautes


def test_la_gothique_ne_compose_que_le_bandeau_de_titre():
    """LE FICHIER EST SOUS-ENSEMBLÉ AUX LETTRES, et c'est ce qui rend cette
    règle nécessaire plutôt que décorative : il ne porte NI CHIFFRE, NI
    PONCTUATION au-delà de l'espace, du tiret et de l'esperluette. Composer
    « 98 fiches » dedans ferait tomber les chiffres dans une fonte de secours
    au milieu du mot — un défaut qui ne se voit qu'à l'écran, et seulement là
    où il y a un chiffre.

    ELLE NE COMPOSE DONC QU'UN SEUL SÉLECTEUR, et c'est le nom du site."""
    porteurs = []
    for m in re.finditer(r"(?m)^([^{}\n][^{\n]*)\{([^}]*)\}", CODE_CSS):
        if "var(--gothique)" in m.group(2):
            porteurs.append(m.group(1).strip())
    assert porteurs == [".titre-journal"], porteurs
    # ET LA PLAGE DÉCLARÉE CORRESPOND AU FICHIER : annoncer des chiffres que
    # le fichier ne porte pas ferait chercher au navigateur un glyphe absent.
    pol = open(os.path.join(ICI, "polices.css"), encoding="utf-8").read()
    i = pol.index("font-family: 'Gothique'")
    plage = pol[i:i + 420]
    for chiffre in ("U+0030", "0030-0039"):
        assert chiffre not in plage, "la plage annonce des chiffres"
    assert "U+0041-005A" in plage and "U+0061-007A" in plage


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


# ── 6. LE PANNEAU LATÉRAL — deux états, sept valeurs, et rien d'autre ─────

def _bloc_sombre():
    """Le contenu de `@media (prefers-color-scheme: dark)`."""
    i = CODE_CSS.index("@media (prefers-color-scheme: dark)")
    j = CODE_CSS.index("\n}\n", CODE_CSS.index(":root{", i))
    return CODE_CSS[i:j]


def _palette_sombre():
    """La palette telle qu'elle est EN MODE SOMBRE : celle de `:root`, avec
    les valeurs que la requête de média redéfinit."""
    p = dict(P)
    for m in re.finditer(r"--([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6})", _bloc_sombre()):
        p[m.group(1)] = m.group(2)
    return p


PANNEAU = ("bl-fond", "bl-fond2", "bl-encre", "bl-encre2", "bl-sourd",
           "bl-sourd2", "bl-filet", "bl-filet2", "bl-actif", "bl-lien")
#: Les encres du panneau, celles qui composent du texte.
PANNEAU_ENCRES = ("bl-encre", "bl-encre2", "bl-sourd", "bl-sourd2",
                  "bl-actif", "bl-lien")


def test_le_panneau_a_ses_propres_jetons():
    """Sans jetons à part, chaque règle du menu porterait `var(--encre)` et il
    faudrait la redéclarer une par une sous la requête de média — une
    trentaine de règles, dont on en oublierait trois, et ces trois-là seraient
    du texte noir sur ardoise."""
    manquants = [c for c in PANNEAU if c not in P]
    assert not manquants, manquants


def test_les_deux_etats_du_panneau_sont_lisibles():
    """Le jour comme la nuit, sur SES DEUX fonds — celui des entrées et celui
    des cadres internes, qui n'est pas le même."""
    faibles = []
    for etat, pal in (("clair", P), ("sombre", _palette_sombre())):
        for encre in PANNEAU_ENCRES:
            for fond in ("bl-fond", "bl-fond2"):
                r = contraste(pal[encre], pal[fond])
                if r < AA:
                    faibles.append("%s : %s sur %s = %.2f"
                                   % (etat, encre, fond, r))
    assert not faibles, faibles


def test_les_teintes_de_navigation_basculent_avec_le_panneau():
    """`--nav-graphite` à #4A5568 sur une ardoise à #262C34 donne 1,4 de
    contraste, c'est-à-dire une icône invisible. Chacune doit avoir son jumeau
    clair, et le contrôle vaut sur les deux fonds du panneau."""
    sombre = _palette_sombre()
    # Elles changent RÉELLEMENT de valeur : garder les mêmes passerait le
    # contrôle du dictionnaire tout en laissant les icônes dans le noir.
    for n in NAV:
        assert sombre[n] != P[n], n
    faibles = []
    for etat, pal in (("clair", P), ("sombre", sombre)):
        for n in NAV:
            for fond in ("bl-fond", "bl-fond2"):
                r = contraste(pal[n], pal[fond])
                if r < 3.0:
                    faibles.append("%s : %s sur %s = %.2f" % (etat, n, fond, r))
    assert not faibles, faibles


def test_le_panneau_se_detache_de_la_feuille():
    """C'est la demande : « plus contrasté que la feuille principale ». Le
    panneau clair s'en écarte franchement sans inverser ; le sombre l'oppose."""
    assert contraste(P["bl-fond"], P["papier"]) >= 1.2
    assert contraste(_palette_sombre()["bl-fond"], P["papier"]) >= 7.0


def test_la_feuille_ne_bascule_pas_avec_le_panneau():
    """Ce site est un journal : il se lit sur du papier, et un papier ne
    devient pas noir la nuit. Le menu, lui, est du mobilier — il peut
    s'assombrir sans que la page change de nature. Basculer la feuille
    demanderait de mesurer un thème sombre sur les quatre-vingt-dix-huit
    fiches, ce qui n'a pas été fait et ne doit pas être prétendu."""
    sombre = _palette_sombre()
    for c in ("papier", "papier2", "papier3", "encre", "encre2") + CODE:
        assert sombre[c] == P[c], c


def test_la_requete_sombre_ne_redefinit_que_des_jetons():
    """UNE RÈGLE DE COMPOSANT POSÉE LÀ s'appliquerait la nuit et pas le jour :
    c'est le défaut classique du mode sombre, et il ne se voit que sur l'un des
    deux écrans. La requête ne contient qu'un `:root`."""
    bloc = _bloc_sombre()
    # Un seul sélecteur, et c'est `:root`.
    # `:root` commence par deux-points : la classe de caractères doit
    # l'admettre, sinon le contrôle ne trouve RIEN et se croit satisfait.
    selecteurs = [x.strip() for x in
                  re.findall(r"(?m)^\s*([:.#a-zA-Z][^{\n]*)\{", bloc)]
    assert selecteurs == [":root"], selecteurs


def test_aucune_regle_du_menu_ne_peint_avec_la_palette_de_la_page():
    """Une seule oubliée devient du texte noir sur ardoise — et elle ne se voit
    que sur l'écran d'un lecteur en mode sombre, c'est-à-dire jamais ici.

    LA LÉGENDE EST L'EXCEPTION, ET ELLE EST NOMMÉE. Elle reste sur un carton de
    la couleur de la feuille parce que c'est son travail : une pastille
    « RUPTURE » recolorée pour tenir sur l'ardoise ne serait plus celle des
    cartes, or la légende sert à montrer ce qu'on VERRA sur une carte."""
    # On isole les règles dont le sélecteur appartient au menu.
    fautives = []
    for m in re.finditer(r"(?m)^([^{}\n][^{\n]*)\{([^}]*)\}", CODE_CSS):
        sel, corps = m.group(1).strip(), m.group(2)
        if not re.search(r"(^|[\s,])\.(bl|an)[-\s.:\[]", " " + sel):
            continue
        if ".bl-lg" in sel:          # la légende, exception nommée ci-dessus
            continue
        for jeton in re.findall(r"var\(--([a-z0-9-]+)\)", corps):
            if jeton in ("papier", "papier2", "papier3", "encre", "encre2",
                         "sourd", "sourd2", "filet", "filet2", "rouge", "bleu"):
                fautives.append("%s : var(--%s)" % (sel, jeton))
    assert not fautives, fautives


def test_le_bandeau_de_titre_ne_melange_pas_deux_registres():
    """DÉFAUT SIGNALÉ PAR LE LECTEUR, ET IL AVAIT L'ŒIL. Le mot-titre était
    passé à la gothique ; la ligne dessous était restée en Inter — un
    sans-serif d'interface posé sous un logotype de 1850, soit deux siècles
    d'écart en dix-huit pixels. Le bandeau était à moitié converti.

    LE CHAPEAU D'UNE PREMIÈRE PAGE EST COMPOSÉ DANS LE CARACTÈRE DE LA
    COLONNE : c'est ce qui le rattache au journal plutôt qu'à sa barre
    d'outils. Ailleurs, la même classe sert de sous-titre de page et garde le
    sans, qui y est à sa place — la règle porte donc sur `.tete .devise`, pas
    sur `.devise`.

    ET LES DEUX MOTS DU LOGOTYPE SONT DU MÊME POIDS. Le second était à 700 :
    dans une gothique, cela ne se lit pas comme une emphase mais comme un
    AUTRE caractère, les pleins s'épaississant au point de changer le
    dessin."""
    serre = CODE_CSS.replace(" ", "").replace("\n", "")
    i = serre.index(".tete.devise{")
    bloc = serre[i:i + 260]
    assert "font-family:var(--serif)" in bloc, bloc
    assert "var(--sans)" not in bloc, bloc
    j = serre.index(".titre-journalspan{")
    assert "font-weight:400" in serre[j:j + 90], serre[j:j + 90]


def test_le_bandeau_de_genre_ne_recopie_pas_ce_qu_il_annonce():
    """LA BANDE PORTE L'ÉNUMÉRATION DES SUJETS, et elle la porte UNE fois. Le
    paragraphe du dessous la portait aussi : les fondre était le défaut, les
    dupliquer en serait un pire — deux listes de sujets à trente pixels l'une
    de l'autre divergeraient au premier sujet ajouté, et c'est toujours celle
    qu'on regarde le moins qui reste en arrière.

    Elles viennent donc de DEUX clés distinctes du dictionnaire, et le
    paragraphe ne porte plus la première."""
    h = open(os.path.join(ICI, "index.html"), encoding="utf-8").read()
    i = h.index('<p class="genre"')
    assert 'data-i18n="ac.devise"' in h[i:i + 200], h[i:i + 200]
    j = h.index('<p class="devise">')
    bloc = h[j:h.index("</p>", j)]
    assert 'data-i18n="ac.devise"' not in bloc, "l'énumération est écrite deux fois"
    assert 'data-i18n="ac.devise.b"' in bloc and 'data-i18n="ac.devise.fin"' in bloc
    # ET LA BANDE EST COMPOSÉE COMME UNE BANDE : capitales espacées, entre
    # deux filets. Sans les filets, ce n'est qu'une ligne de petites capitales.
    serre = CODE_CSS.replace(" ", "").replace("\n", "")
    k = serre.index(".genre{")
    g = serre[k:k + 320]
    assert "text-transform:uppercase" in g and "letter-spacing:" in g
    assert "border-top:1pxsolidvar(--encre)" in g and "border-bottom:1pxsolidvar(--encre)" in g
