# -*- coding: utf-8 -*-
"""Un sommaire de page légale n'est pas la barre de navigation du site.

LE DÉFAUT, ET C'EST UN LECTEUR QUI L'A VU, PAS LA SUITE. Sur /cgv, le bloc
« Sommaire » se posait par-dessus le texte : ses dix liens, tassés dans une
barre de 56 px de haut, débordaient sur « 1. Objet ». Même chose sur
/confidentialite et /protection-donnees.

LA CAUSE, ET ELLE TIENT EN UN CARACTÈRE MANQUANT.

    nav{position:sticky;top:0;z-index:100;display:flex;…}

Un sélecteur d'ÉLÉMENT NU désigne TOUS les <nav> de la page. Le sommaire est
marqué `<nav class="toc" aria-label="Sommaire">` — c'est l'élément juste pour
une table des matières, et c'est ce qui l'a perdu : il recevait, sans que rien
ne le dise, la position collante de la barre du site, son z-index de 100, sa
disposition en ligne et sa hauteur fixe. Huit sélecteurs `nav` nus par page,
dont cinq en `!important`, qui écrasaient jusqu'au fond du bloc.

CE QUE MESURENT CES RÈGLES : LA PORTÉE DES SÉLECTEURS, pas la présence d'un
correctif. Pour chaque page qui imbrique un <nav> dans son contenu, on
reconstruit la chaîne d'ancêtres de ce <nav>, puis on évalue contre elle CHAQUE
sélecteur de la feuille. Un sélecteur qui l'atteint et qui déclare une
propriété de mise en page est le défaut, quel que soit son libellé.

LE PIÈGE QU'ELLES ÉVITENT. Une règle qui chercherait « body > nav » dans le
texte de la feuille serait verte sur une page où un neuvième `nav{…}` aurait
été ajouté sans ancrage : le motif attendu s'y trouve, et le défaut aussi.
C'est la portée qui décide, jamais la présence d'un motif.

L'ÉVALUATEUR NE DEVINE PAS. Il couvre le type, `*`, la classe, l'identifiant,
`:not(simple)`, les pseudo-classes, les pseudo-éléments et les combinateurs
descendant et enfant. Devant toute autre grammaire — un sélecteur d'attribut,
un `+`, un `~` — il LÈVE plutôt que de répondre « non ». Une règle qui ne sait
pas juger doit le dire ; c'est ce qui l'empêche de passer pour rien.

CE QU'ELLES NE FONT PAS. Elles ne rendent pas la page. Que le sommaire cesse
EFFECTIVEMENT de chevaucher le texte se mesure dans un navigateur, et c'est
`outils/recette_mise_en_page.js` qui le fait.
"""
import io
import os
import re

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Les pages qui portent un SOMMAIRE : un <nav class="toc"> imbriqué dans le
#: contenu. La liste est DÉCLARÉE et confrontée à ce que les fichiers portent :
#: une page qui en gagne ou en perd un fait rougir la règle, et c'est voulu.
#:
#: DEUX AUTRES PAGES IMBRIQUENT UN <nav> ET N'ENTRENT PAS ICI, parce que leur
#: <nav> imbriqué EST une barre de navigation, voulue comme telle :
#: `sentinel.html` (nav.sb-nav, la colonne latérale — que la feuille exempte
#: déjà nommément par `:not(.sb-nav)`) et `panorama.html` (nav.pnav, la bande
#: de navigation du panorama). Elles ne sont pas hors de portée pour autant :
#: `outils/recette_mise_en_page.js` mesure le rendu de TOUTES les pages.
PAGES_A_SOMMAIRE = {"cgv.html", "confidentialite.html", "protection-donnees.html"}

#: Les propriétés par lesquelles la barre de navigation abîmait le sommaire.
#: `position`, `top` et `z-index` le décollaient du flux et le posaient sur le
#: texte ; `display` et `height` l'écrasaient sur une ligne de 56 px ; les
#: autres lui prenaient son apparence.
MISE_EN_PAGE = {
    "position", "top", "z-index", "display", "height", "min-height", "max-height",
    "padding", "padding-top", "padding-bottom", "padding-left", "padding-right",
    "background", "background-color", "background-image", "border-bottom",
    "box-shadow", "backdrop-filter", "-webkit-backdrop-filter",
    "align-items", "gap", "flex-wrap",
}


# ── LECTURE DES FEUILLES ──────────────────────────────────────────────────

def _sans_commentaires(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def _fin_de_bloc(css, i):
    """Indice qui suit l'accolade fermante appariée à `css[i] == '{'`."""
    assert css[i] == "{"
    p = 0
    while i < len(css):
        if css[i] == "{":
            p += 1
        elif css[i] == "}":
            p -= 1
            if p == 0:
                return i + 1
        i += 1
    return len(css)


#: Les at-règles dont le corps contient d'autres règles : on entre. Les autres
#: (`@keyframes`, `@font-face`) ont un corps qui n'est pas fait de sélecteurs
#: d'éléments — on le saute en entier plutôt que d'y lire « 0% » comme un type.
AT_TRANSPARENTES = ("@media", "@supports", "@layer", "@container", "@scope")


def _regles(css, traverser_les_at=True, _profondeur=0):
    """Rend (sélecteur, déclarations) pour chaque règle, at-règles traversées.

    `traverser_les_at=False` ne sert qu'à une chose : prouver, en comparant les
    deux comptes, que la traversée RAPPORTE quelque chose. Sans cette preuve,
    un lecteur qui n'entrerait plus dans les @media resterait vert.
    """
    css = _sans_commentaires(css) if _profondeur == 0 else css
    out, i, debut = [], 0, 0
    while i < len(css):
        c = css[i]
        if c == "{":
            prelude = css[debut:i].strip()
            fin = _fin_de_bloc(css, i)
            corps = css[i + 1:fin - 1]
            if prelude.startswith("@"):
                if traverser_les_at and prelude.split()[0].lower() in AT_TRANSPARENTES:
                    out.extend(_regles(corps, traverser_les_at, _profondeur + 1))
            elif prelude:
                out.append((prelude, corps))
            i = debut = fin
            continue
        if c == ";":
            # At-règle sans corps (@import, @charset) : rien à retenir.
            debut = i + 1
        i += 1
    return out


def _proprietes(declarations):
    """Les noms de propriétés déclarés dans un bloc, en minuscules."""
    noms = set()
    for morceau in declarations.split(";"):
        if ":" not in morceau:
            continue
        nom = morceau.split(":", 1)[0].strip().lower()
        if nom and re.match(r"^-?[a-z][\w-]*$", nom):
            noms.add(nom)
    return noms


# ── L'ARBRE DU DOCUMENT ───────────────────────────────────────────────────

_VIDES = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
          "meta", "param", "source", "track", "wbr"}


class _Noeud(object):
    def __init__(self, tag, attrs):
        d = dict(attrs)
        self.tag = tag
        self.classes = set((d.get("class") or "").split())
        self.ident = d.get("id") or ""

    def __repr__(self):
        return self.tag + "".join("." + c for c in sorted(self.classes))


def _chaines_des_nav(html):
    """Les chaînes d'ancêtres de chaque <nav>, de la racine au <nav> inclus."""
    from html.parser import HTMLParser

    trouve = []

    class P(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self, convert_charrefs=True)
            self.pile = []

        def handle_starttag(self, tag, attrs):
            if tag in _VIDES:
                return
            n = _Noeud(tag, attrs)
            self.pile.append(n)
            if tag == "nav":
                trouve.append(list(self.pile))

        def handle_startendtag(self, tag, attrs):
            pass

        def handle_endtag(self, tag):
            for k in range(len(self.pile) - 1, -1, -1):
                if self.pile[k].tag == tag:
                    del self.pile[k:]
                    return

    P().feed(html)
    return trouve


# ── L'ÉVALUATEUR DE SÉLECTEURS ────────────────────────────────────────────

class GrammaireNonCouverte(Exception):
    """Le sélecteur emploie une construction que l'évaluateur ne sait pas juger.

    Il LÈVE au lieu de répondre « n'atteint pas » : une règle qui ne sait pas
    juger et se tait est une règle qui passe pour rien.
    """


_JETON = re.compile(r"""
      (?P<type>\*|[A-Za-z][\w-]*)
    | (?P<classe>\.[\w-]+)
    | (?P<ident>\#[\w-]+)
    | (?P<pseudo>::?[\w-]+(?:\([^()]*\))?)
    | (?P<attr>\[[^\]]*\])
""", re.X)


def _compose(compound, noeud):
    """Le compound désigne-t-il ce nœud ? (indépendamment de son contexte)

    L'ORDRE DE LA DÉCISION EST LE POINT. On tranche d'abord sur tout ce qui est
    décidable ; on ne lève QUE si le jeton non couvert est celui qui reste à
    trancher. La première version levait dès qu'elle croisait un sélecteur
    d'attribut n'importe où dans la feuille — `[data-tooltip]::after` suffisait
    à interrompre la mesure de la page entière, alors qu'un pseudo-élément ne
    désigne jamais la boîte de l'élément et que la réponse était « non ».
    """
    i, vu_type, indecis = 0, False, []
    while i < len(compound):
        m = _JETON.match(compound, i)
        if not m or m.start() != i:
            raise GrammaireNonCouverte(compound)
        i = m.end()
        if m.group("attr"):
            indecis.append(m.group("attr"))
        elif m.group("type"):
            if vu_type:                       # « div p » sans combinateur : impossible
                raise GrammaireNonCouverte(compound)
            vu_type = True
            t = m.group("type")
            if t != "*" and t.lower() != noeud.tag:
                return False
        elif m.group("classe"):
            if m.group("classe")[1:] not in noeud.classes:
                return False
        elif m.group("ident"):
            if m.group("ident")[1:] != noeud.ident:
                return False
        else:
            p = m.group("pseudo")
            if p.startswith("::"):
                return False                  # habille un pseudo-élément, pas la boîte
            nom = p[1:].split("(")[0].lower()
            if nom == "not":
                interne = p[p.index("(") + 1:-1].strip()
                if "," in interne:
                    raise GrammaireNonCouverte(compound)
                if _compose(interne, noeud):
                    return False
            # Les autres pseudo-classes (:hover, :first-child…) peuvent
            # s'appliquer : on ne s'en sert pas pour exclure.
    if i != len(compound):
        raise GrammaireNonCouverte(compound)
    if indecis:
        # Tout le reste dit « oui » : c'est l'attribut qui tranche, et on ne
        # sait pas le lire. Se taire ici serait répondre « non » par ignorance.
        raise GrammaireNonCouverte(compound)
    return True


def _decouper(selecteur):
    """[(combinateur, compound), …] de gauche à droite ; le premier a None."""
    parts, tampon, comb, prof = [], "", None, 0
    i = 0
    while i < len(selecteur):
        c = selecteur[i]
        if c == "(":
            prof += 1
        elif c == ")":
            prof -= 1
        if prof == 0 and c in " >+~\t\n":
            if tampon:
                parts.append((comb, tampon))
                tampon, comb = "", " "
            if c in ">+~":
                comb = c
        else:
            tampon += c
        i += 1
    if tampon:
        parts.append((comb, tampon))
    if not parts:
        raise GrammaireNonCouverte(selecteur)
    return parts


def _atteint(selecteur, chaine):
    """Ce sélecteur (une seule alternative, sans virgule) désigne-t-il chaine[-1] ?"""
    parts = _decouper(selecteur.strip())

    def rec(i, j):
        comb, comp = parts[i]
        if j < 0 or not _compose(comp, chaine[j]):
            return False
        if i == 0:
            return True
        lien = parts[i][0]
        if lien == ">":
            return rec(i - 1, j - 1)
        if lien == " ":
            return any(rec(i - 1, k) for k in range(j - 1, -1, -1))
        raise GrammaireNonCouverte(selecteur)

    return rec(len(parts) - 1, len(chaine) - 1)


def _atteint_liste(selecteur, chaine):
    """Une liste de sélecteurs séparés par des virgules de premier niveau."""
    for alt in _virgules(selecteur):
        if _atteint(alt, chaine):
            return True
    return False


def _virgules(selecteur):
    out, tampon, prof = [], "", 0
    for c in selecteur:
        if c == "(":
            prof += 1
        elif c == ")":
            prof -= 1
        if c == "," and prof == 0:
            if tampon.strip():
                out.append(tampon.strip())
            tampon = ""
        else:
            tampon += c
    if tampon.strip():
        out.append(tampon.strip())
    return out


# ── CE QU'ON MESURE, PAGE PAR PAGE ────────────────────────────────────────

def _page(nom):
    return io.open(os.path.join(ICI, nom), encoding="utf-8").read()


def _feuille(html):
    return "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, flags=re.S | re.I))


def _sommaire_et_barre(nom):
    """(chaîne du <nav class="toc"> imbriqué, chaîne du <nav> fils de <body>)."""
    chaines = _chaines_des_nav(_page(nom))
    imbrique = [c for c in chaines if c[-2].tag != "body" and "toc" in c[-1].classes]
    barre = [c for c in chaines if c[-2].tag == "body"]
    return (imbrique[0] if imbrique else None), (barre[0] if barre else None)


def _regles_qui_atteignent(nom, chaine):
    """Les (sélecteur, propriétés) de mise en page qui atteignent cette chaîne.

    DEUX EXCEPTIONS, et elles se lisent sur la FORME du sujet, jamais sur son
    texte :

     1. Un sujet qui nomme `.toc` est l'habillage PROPRE du sommaire. Il est
        fait pour lui ; il n'est pas le défaut.
     2. Un sujet réduit à `*` est la remise à zéro du document
        (`*{margin:0;padding:0}`). Elle atteint le sommaire comme elle atteint
        tout le reste — et la barre au même titre : ce n'est pas « habiller le
        sommaire comme la barre », c'est le socle de la page.

    Tout le reste passe, y compris ce qui n'a pas été prévu ici.
    """
    out = []
    for selecteur, decls in _regles(_feuille(_page(nom))):
        props = _proprietes(decls) & MISE_EN_PAGE
        if not props:
            continue
        for alt in _virgules(selecteur):
            sujet = _decouper(alt)[-1][1]
            if ".toc" in sujet or sujet.strip() == "*":
                continue
            if _atteint(alt, chaine):
                out.append((alt, sorted(props)))
    return out


# ── LES RÈGLES ────────────────────────────────────────────────────────────

def test_les_pages_a_sommaire_sont_bien_celles_qui_sont_declarees():
    """Anti-vacuité : sans sommaire imbriqué, tout le reste passerait à vide."""
    trouvees = set()
    for nom in sorted(os.listdir(ICI)):
        if not nom.endswith(".html"):
            continue
        for chaine in _chaines_des_nav(_page(nom)):
            if chaine[-2].tag != "body" and "toc" in chaine[-1].classes:
                trouvees.add(nom)
    assert trouvees == PAGES_A_SOMMAIRE, (
        "les pages qui portent un sommaire ont changé : %s trouvées, %s "
        "déclarées. Mettre PAGES_A_SOMMAIRE à jour est une décision — l'y "
        "porter fait entrer la page sous la règle."
        % (sorted(trouvees), sorted(PAGES_A_SOMMAIRE)))


@pytest.mark.parametrize("nom", sorted(PAGES_A_SOMMAIRE))
def test_le_sommaire_est_bien_imbrique_dans_le_contenu(nom):
    """La chaîne mesurée est celle d'un sommaire, pas celle de la barre."""
    sommaire, barre = _sommaire_et_barre(nom)
    assert sommaire is not None, "%s : aucun <nav> imbriqué" % nom
    assert barre is not None, "%s : aucune barre <nav> fille de <body>" % nom
    assert sommaire[-1].tag == "nav" and "toc" in sommaire[-1].classes
    assert [n.tag for n in sommaire[:2]] == ["html", "body"], [str(n) for n in sommaire]
    assert sommaire[-2].tag != "body", "le sommaire serait la barre"
    # L'enveloppe du contenu n'a pas le même nom partout (`.con` sur /cgv et
    # /confidentialite, `.page-wrap` sur /protection-donnees) : ce qui compte
    # est que le sommaire soit DANS le contenu, à distance de <body>.
    assert len(sommaire) >= 4, [str(n) for n in sommaire]
    assert barre[-2].tag == "body", [str(n) for n in barre]


@pytest.mark.parametrize("nom", sorted(PAGES_A_SOMMAIRE))
def test_aucun_selecteur_de_mise_en_page_n_atteint_le_sommaire(nom):
    """LE DÉFAUT MESURÉ. Avant correction : 8 sélecteurs par page, dont
    `nav{position:sticky;…}` et `nav:not(.sb-nav){flex-wrap:wrap}`."""
    sommaire, _ = _sommaire_et_barre(nom)
    fautifs = _regles_qui_atteignent(nom, sommaire)
    assert not fautifs, (
        "%s : %d sélecteur(s) habillent le sommaire comme la barre — %s"
        % (nom, len(fautifs), fautifs[:6]))


@pytest.mark.parametrize("nom", sorted(PAGES_A_SOMMAIRE))
def test_la_barre_garde_sa_position_sa_hauteur_et_son_fond(nom):
    """Anti-dégât collatéral : ancrer les sélecteurs ne devait pas les éteindre."""
    _, barre = _sommaire_et_barre(nom)
    portees = set()
    for sel, props in _regles_qui_atteignent(nom, barre):
        portees.update(props)
    for attendue in ("position", "z-index", "height", "background", "display"):
        assert attendue in portees, (
            "%s : plus aucun sélecteur ne déclare « %s » sur la barre — "
            "l'ancrage l'a débranchée. Portées : %s"
            % (nom, attendue, sorted(portees)))


@pytest.mark.parametrize("nom", sorted(PAGES_A_SOMMAIRE))
def test_le_sommaire_garde_un_habillage_qui_lui_est_propre(nom):
    """Le sommaire n'est pas nu : `.toc` lui donne fond, bordure et marges."""
    sommaire, _ = _sommaire_et_barre(nom)
    propres = set()
    for selecteur, decls in _regles(_feuille(_page(nom))):
        for alt in _virgules(selecteur):
            if ".toc" in _decouper(alt)[-1][1] and _atteint(alt, sommaire):
                propres.update(_proprietes(decls))
    for attendue in ("background", "padding"):
        assert attendue in propres, (
            "%s : le sommaire n'a plus de « %s » à lui — %s"
            % (nom, attendue, sorted(propres)))


# ── LES TÉMOINS : LA RÈGLE SAIT-ELLE ÉCHOUER ? ────────────────────────────
#
# Sans eux, `test_aucun_selecteur…` serait vert le jour où l'évaluateur
# répondrait « non » à tout — un défaut de mesure, pas d'absence de défaut.

def test_l_evaluateur_atteint_le_sommaire_par_un_selecteur_nu():
    """Le sélecteur d'AVANT correction doit être vu comme atteignant."""
    sommaire, _ = _sommaire_et_barre("cgv.html")
    assert _atteint("nav", sommaire) is True
    assert _atteint("nav:not(.sb-nav)", sommaire) is True
    assert _atteint(".toc", sommaire) is True


def test_l_evaluateur_n_atteint_pas_le_sommaire_par_le_selecteur_ancre():
    """Le sélecteur d'APRÈS correction ne doit désigner que la barre."""
    sommaire, barre = _sommaire_et_barre("cgv.html")
    assert _atteint("body > nav", sommaire) is False
    assert _atteint("body > nav", barre) is True
    assert _atteint("body > nav:not(.sb-nav)", barre) is True


def test_l_evaluateur_leve_sur_une_grammaire_qu_il_ne_sait_pas_juger():
    """Il ne répond jamais « non » par ignorance."""
    sommaire, _ = _sommaire_et_barre("cgv.html")
    for inconnu in ('nav[aria-label]', 'h1 + nav', 'div ~ nav'):
        with pytest.raises(GrammaireNonCouverte):
            _atteint(inconnu, sommaire)


def test_le_lecteur_de_feuille_lit_bien_ce_qu_il_y_a_dedans():
    """Le découpage en règles n'avale ni ne fabrique rien.

    Sans cette preuve, un lecteur qui rendrait zéro règle rendrait aussi zéro
    fautif — et la règle principale serait verte sur une page cassée.
    """
    feuille = _feuille(_page("cgv.html"))
    regles = _regles(feuille)
    # 291 règles relevées sur cgv.html le 09/09/2026. Le plancher n'est pas ce
    # nombre — la feuille bouge — mais l'ordre de grandeur : un lecteur cassé
    # en rend zéro ou trois, et c'est cela qu'on attrape. La première version
    # de cette règle exigeait « plus de 400 » : un chiffre inventé, qui a fait
    # rougir la mesure au lieu du défaut.
    assert len(regles) > 150, len(regles)
    selecteurs = [s for s, _ in regles]
    assert any(s.strip() == ".toc" for s in selecteurs), "la règle .toc a disparu"
    assert any("toc-list" in s for s in selecteurs)
    # Les images-clés ne sont pas des sélecteurs d'éléments : « 0% » ne doit
    # jamais entrer dans la liste.
    assert not [s for s in selecteurs if re.match(r"^\d+%", s.strip())]
    # Les at-règles à corps transparent sont TRAVERSÉES, et la traversée
    # RAPPORTE : la feuille porte des @media, et les règles qu'ils contiennent
    # doivent sortir du lecteur. On le mesure par différence plutôt que de
    # l'affirmer — c'est dans un @media que vivait `nav:not(.sb-nav)`.
    assert "@media" in feuille
    assert not [s for s in selecteurs if s.strip().startswith("@")]
    sans_at = _regles(feuille, traverser_les_at=False)
    # 291 règles au total, 277 hors @media, soit 14 de plus par la traversée
    # (cgv.html, 09/09/2026). Le seuil retenu est 5, pas 14 : un lecteur qui
    # n'entre plus dans les @media en rapporte ZÉRO de plus, et c'est ce
    # basculement-là qu'on attrape — pas la valeur du jour.
    assert len(regles) > len(sans_at) + 5, (len(regles), len(sans_at))
