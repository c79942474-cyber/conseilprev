# -*- coding: utf-8 -*-
"""LES SIX INFOBULLES DE « CE QUI NOUS DISTINGUE ».

CE QUI A DÉCLENCHÉ CE FICHIER. Une demande : « mettre des infobulles sur les
6 cartes de CE QUI NOUS DISTINGUE ».

CE QUE LA MESURE A TROUVÉ AVANT D'ÉCRIRE UNE LIGNE, et qui rendait la pose
naïve de l'attribut parfaitement inutile :

  1. `.diff-card` porte `overflow:hidden`. La convention maison range la bulle
     AU-DESSUS de l'élément (`bottom:calc(100% + 10px)`) : posée telle quelle,
     elle tombe hors de la boîte et le rognage l'efface. Rien ne prévient —
     l'attribut est là, la règle CSS est là, et l'écran ne montre rien.
     Ce rognage n'est pas décoratif : le `::before` de la carte est un blob en
     `inset:-60%` qui, sans lui, déborderait sur toute la grille. On ne pouvait
     donc pas l'ouvrir ; il fallait rentrer la bulle.

  2. Le `::before` de la carte est DÉJÀ ce blob. La flèche de la convention ne
     peut pas s'y loger, et deux de ses déclarations fuiraient dessus : un
     `border-top-color` qui peindrait un arc de 5 px sur un disque flouté, et
     un `translateX(-50%)` qui le décalerait d'une demi-largeur.

  3. `applyLang` ne traite que `[data-i18n]` et `[data-i18n-ph]`. Un
     `data-tooltip` serait resté français en anglais et en allemand.

LA MESURE QUI A TRANCHÉ. Deux captures du même survol, prises dans un
navigateur : avec la règle cadrée, la bulle s'affiche en entier dans la carte ;
avec le réglage de la convention, la carte se survole, s'agrandit, éclaire ses
voisines — et n'affiche AUCUNE bulle. C'est ce que ces règles gardent.

CE QUE CES RÈGLES NE PEUVENT PAS FAIRE. Ouvrir un navigateur. Elles gardent la
chaîne — attribut, dictionnaire, boucle de traduction, géométrie CSS — et
l'ancrage des chiffres ; elles ne regardent pas l'écran. La recette
`recette_infobulles_distinction.js` s'en charge.
"""
import io
import json
import os
import re
import unicodedata
from html import unescape

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = io.open(os.path.join(_RACINE, "index.html"), encoding="utf-8").read()
INDEXJS = io.open(os.path.join(_RACINE, "index.page.js"), encoding="utf-8").read()
SENTINEL = io.open(os.path.join(_RACINE, "sentinel.html"), encoding="utf-8").read()
SENTINELJS = io.open(os.path.join(_RACINE, "sentinel.page.js"), encoding="utf-8").read()

#: LES SIX CARTES, DANS L'ORDRE OÙ LA PAGE LES POSE. Écrite ici une seule
#: fois : plusieurs règles la parcourent, et la tenir à deux endroits aurait
#: garanti qu'une septième carte soit contrôlée par l'une et ignorée par l'autre.
CARTES = ("df.ai", "df.ind", "df.eco", "df.exp", "df.jur", "df.intl")

LANGUES = ("fr", "en", "de")

#: LES NOMBRES ÉCRITS EN TOUTES LETTRES. Une infobulle qui annonce « douze
#: secteurs » doit pouvoir être confrontée au nombre de cartes que la page
#: montre vraiment : sans cette table, l'annonce ne serait comparable à rien.
EN_LETTRES = {
    8:  {"fr": "huit",  "en": "eight",  "de": "acht"},
    9:  {"fr": "neuf",  "en": "nine",   "de": "neun"},
    10: {"fr": "dix",   "en": "ten",    "de": "zehn"},
    11: {"fr": "onze",  "en": "eleven", "de": "elf"},
    12: {"fr": "douze", "en": "twelve", "de": "zwölf"},
}


# ══════════════════════════════════════════════════════════════════════════
#  LECTURE
# ══════════════════════════════════════════════════════════════════════════

def _section(identifiant):
    """La section demandée, coupée à la section suivante."""
    debut = INDEX.find('id="%s"' % identifiant)
    assert debut > 0, "section %s introuvable" % identifiant
    suite = INDEX.find("<section", debut)
    return INDEX[debut:suite if suite > 0 else len(INDEX)]


BLOC = _section("differenciateurs")


def _gabarit(texte):
    """Ce que le littéral gabarit rend à JSON.parse.

    LE FICHIER PASSE PAR DEUX COUCHES : le gabarit ` ` consomme un niveau
    d'échappement, JSON.parse consomme le second. `\\\\u0027` écrit dans le
    fichier vaut donc `\\u0027` pour JSON — une apostrophe ; et `\\u00A0` écrit
    avec un seul contre-oblique est déjà l'espace insécable quand JSON le lit.
    Comparer le fichier brut au texte affiché, sans rejouer cette première
    couche, compare la page à un texte que personne ne voit jamais."""
    def rendu(m):
        if m.group(1):
            return chr(int(m.group(1), 16))
        return {"n": "\n", "t": "\t", "r": "\r"}.get(m.group(2), m.group(2))
    return re.sub(r"\\(?:u([0-9a-fA-F]{4})|(.))", rendu, texte)


def _dico(lg):
    m = re.search(r"\n\s*%s:JSON\.parse\(`(.*?)`\)" % lg, INDEXJS, re.S)
    assert m, "dictionnaire %s introuvable" % lg
    return json.loads(_gabarit(m.group(1)))


def _feuille():
    """Le CSS de la page, commentaires retirés.

    SANS CE NETTOYAGE, CES RÈGLES SE MENTIRAIENT À ELLES-MÊMES. Le commentaire
    qui explique le réglage de l'infobulle CITE, pour les expliquer, les cinq
    déclarations que ces règles traquent — `overflow:hidden`, `inset:-60%`,
    `bottom:calc(100% + 10px)`, `border-top-color`, `translateX(-50%)`.
    Un analyseur qui lirait le fichier brut recollerait la prose et le code en
    règles qui n'existent pas, et trouverait tout ce qu'il cherche."""
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", INDEX, re.S))
    return re.sub(r"/\*.*?\*/", " ", css, flags=re.S)


def _regles():
    return [(sel.strip(), corps)
            for sel, corps in re.findall(r"([^{}@]+)\{([^{}]*)\}", _feuille())
            if sel.strip()]


def _declaration(selecteur, propriete):
    """La DERNIÈRE valeur déclarée pour `propriete` dans la règle exactement
    nommée `selecteur` — la dernière, parce que c'est celle que la cascade
    retient quand un sélecteur est écrit deux fois."""
    trouve = None
    for sel, corps in _regles():
        if sel != selecteur:
            continue
        m = re.search(r"(?:^|;)\s*%s\s*:\s*([^;]+)" % re.escape(propriete), corps)
        if m:
            trouve = m.group(1).strip()
    return trouve


def _porte(selecteur, propriete):
    """Vrai si UNE règle dont le sélecteur contient `selecteur` déclare la
    propriété — la carte est visée par des sélecteurs groupés de vingt noms,
    la chercher par égalité ne trouverait rien."""
    for sel, corps in _regles():
        if selecteur not in sel:
            continue
        if re.search(r"(?:^|;)\s*%s\s*:" % re.escape(propriete), corps):
            return corps
    return None


def _infobulles_html():
    """Les triplets (clé du titre, texte de l'infobulle, clé de traduction)
    posés sur la page, une entrée par carte.

    LE DÉCOUPAGE SE FAIT SUR L'OUVERTURE DE LA CARTE, PAS SUR SA FERMETURE.
    Une première version cherchait `</div></div>` pour clore chaque carte :
    cette suite n'apparaît qu'à la DERNIÈRE, refermée juste avant la grille.
    La lecture rendait une seule entrée contenant les six, et les règles qui
    s'en servent tombaient — pour un défaut de la mesure, pas de la page."""
    triplets = []
    for carte in BLOC.split('<div class="diff-card"')[1:]:
        ouverture = carte[:carte.find(">") + 1]
        titre = re.search(r'<h3 class="diff-title" data-i18n="([^"]+)"', carte)
        bulle = re.search(r'\sdata-tooltip="([^"]*)"', ouverture)
        cle = re.search(r'\sdata-i18n-tip="([^"]*)"', ouverture)
        triplets.append((titre.group(1) if titre else None,
                         unescape(bulle.group(1)) if bulle else None,
                         cle.group(1) if cle else None))
    return triplets


def _mots(texte):
    sans = "".join(c for c in unicodedata.normalize("NFD", texte.lower())
                   if unicodedata.category(c) != "Mn")
    return [m for m in re.findall(r"[a-z0-9]+", sans) if len(m) > 2]


# ══════════════════════════════════════════════════════════════════════════
#  1. LE GARDE-FOU : SANS LUI, TOUT CE QUI SUIT COMPARE DES VIDES
# ══════════════════════════════════════════════════════════════════════════

def test_la_lecture_de_la_section_n_est_pas_vide():
    """C'EST ARRIVÉ UNE FOIS DANS CE DÉPÔT, ET LA RECETTE EST RESTÉE VERTE :
    une lecture qui rend zéro carte fait passer toutes les comparaisons qui
    suivent pour des comparaisons de vides."""
    assert len(BLOC) > 1500, len(BLOC)
    assert BLOC.count('class="diff-card"') == 6, (
        "la section n'expose plus six cartes : %d"
        % BLOC.count('class="diff-card"'))
    assert len(_infobulles_html()) == 6, _infobulles_html()


def test_la_classe_diff_card_SERT_AUSSI_AILLEURS():
    """POURQUOI TOUTES CES RÈGLES SONT CADRÉES SUR LA SECTION. `.diff-card`
    habille aussi les six cartes de services : une règle écrite sur la classe
    seule croirait mesurer six cartes et en mesurerait douze — et un réglage
    CSS posé sur la classe seule toucherait une section que personne n'a
    demandé de changer."""
    total = INDEX.count('class="diff-card"')
    assert total > 6, (
        "`.diff-card` ne sert plus qu'ici (%d) : le cadrage sur "
        "#differenciateurs n'a plus de raison d'être, mais il ne nuit pas — "
        "c'est ce commentaire qu'il faut corriger." % total)


# ══════════════════════════════════════════════════════════════════════════
#  2. CHAQUE CARTE PORTE SON INFOBULLE, ET LA BONNE
# ══════════════════════════════════════════════════════════════════════════

def test_CHACUNE_des_six_cartes_porte_son_infobulle():
    """CINQ CARTES SUR SIX, C'EST UNE SECTION QUI PARAÎT MUETTE. Le visiteur
    qui survole la sixième et ne voit rien conclut que la page ne fait pas
    d'infobulles, pas que celle-ci manque."""
    manquantes = [t for t, bulle, _ in _infobulles_html() if not bulle]
    assert not manquantes, "cartes sans infobulle : %s" % manquantes


def test_l_infobulle_est_APPARIEE_a_la_carte_qu_elle_explique():
    """UNE INFOBULLE JUSTE SUR LA MAUVAISE CARTE EST PIRE QUE PAS D'INFOBULLE :
    elle affirme quelque chose de faux avec l'autorité d'un texte écrit."""
    vus = [(t, cle) for t, _, cle in _infobulles_html()]
    assert vus == [(c + ".t", "tip." + c) for c in CARTES], vus


def test_l_infobulle_ECRITE_dans_la_page_est_celle_du_dictionnaire_francais():
    """LES DEUX TEXTES SONT DEUX SOURCES POUR LA MÊME PHRASE : celui de
    l'attribut s'affiche avant que JavaScript ne tourne, celui du dictionnaire
    le remplace ensuite. Les laisser diverger fait clignoter la page d'une
    version à l'autre, et personne ne sait laquelle fait foi."""
    fr = _dico("fr")
    for (_, bulle, _ref), cle in zip(_infobulles_html(), CARTES):
        attendu = fr.get("tip." + cle)
        assert attendu, "tip.%s absente du dictionnaire français" % cle
        assert bulle == attendu, (
            "tip.%s : la page dit\n  %r\nle dictionnaire dit\n  %r"
            % (cle, bulle, attendu))


# ══════════════════════════════════════════════════════════════════════════
#  3. LES TROIS LANGUES — ET LA BOUCLE QUI LES ÉCRIT
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("lg", LANGUES)
def test_les_six_infobulles_existent_dans_la_langue(lg):
    """UNE CLÉ ABSENTE NE TOMBE PAS : `ii()` rend une valeur vide, la boucle
    passe son tour, et l'infobulle reste dans la langue précédente. Le lecteur
    allemand lit du français sans que rien ne signale l'accident."""
    dico = _dico(lg)
    manquantes = [c for c in CARTES if not (dico.get("tip." + c) or "").strip()]
    assert not manquantes, "tip.* absentes du dictionnaire %s : %s" % (lg, manquantes)


@pytest.mark.parametrize("cle", CARTES)
def test_les_trois_langues_disent_des_choses_DIFFERENTES(cle):
    """RECOPIER LE FRANÇAIS SOUS L'ÉTIQUETTE « en » FAIT PASSER LA RÈGLE
    PRÉCÉDENTE : la clé existe, elle n'est pas vide, et la traduction n'a pas
    eu lieu. C'est le défaut que cette règle-ci mesure."""
    textes = {lg: _dico(lg)["tip." + cle] for lg in LANGUES}
    for a, b in (("fr", "en"), ("fr", "de"), ("en", "de")):
        assert textes[a] != textes[b], (
            "tip.%s : %s et %s portent le même texte — %r"
            % (cle, a, b, textes[a][:70]))


def test_applyLang_ECRIT_l_attribut_et_pas_seulement_du_texte():
    """LE DÉFAUT MESURÉ AVANT D'ÉCRIRE : `applyLang` ne connaissait que
    `data-i18n` (du texte) et `data-i18n-ph` (un attribut de formulaire).
    Une infobulle est un ATTRIBUT DE CONTENU : sans une boucle qui l'écrit,
    les dictionnaires anglais et allemand existent et ne servent à rien.

    LE GARDE-FOU. La boucle `[data-i18n-ph]`, sur laquelle celle-ci est
    calquée, doit toujours être là : si elle disparaissait, la comparaison
    n'aurait plus de modèle et cette règle passerait sur une fonction vide."""
    corps = re.search(r"function applyLang\(\)\{(.*?)\n\}", INDEXJS, re.S)
    assert corps, "applyLang introuvable"
    corps = corps.group(1)
    assert "[data-i18n-ph]" in corps and "placeholder=" in corps, (
        "le modèle d'attribut traduit a disparu d'applyLang")
    assert "[data-i18n-tip]" in corps, (
        "applyLang ne parcourt pas [data-i18n-tip] : l'infobulle restera "
        "française en anglais et en allemand")
    assert re.search(r"i18nTip\)", corps), (
        "applyLang ne LIT pas la clé data-i18n-tip")
    assert re.search(r"setAttribute\(\s*'data-tooltip'", corps), (
        "applyLang ne réécrit pas data-tooltip : la clé est lue et jetée")


# ══════════════════════════════════════════════════════════════════════════
#  4. LE RENDU — LE PIÈGE DU ROGNAGE, MESURÉ DES DEUX CÔTÉS
# ══════════════════════════════════════════════════════════════════════════

def test_la_carte_ROGNE_toujours_ce_qui_deborde_de_sa_boite():
    """LE GARDE-FOU DE LA RÈGLE SUIVANTE. Celle-ci exige que la bulle soit
    rentrée DANS la carte. Cette exigence n'a de sens que tant que la carte
    rogne : si `overflow:hidden` disparaissait, la contrainte deviendrait une
    superstition qu'on traînerait sans savoir pourquoi.

    ET LE ROGNAGE N'EST PAS NÉGOCIABLE : le `::before` de la carte déborde de
    soixante pour cent de chaque côté. L'ouvrir pour laisser sortir la bulle
    répandrait ce blob sur toute la grille."""
    assert _porte(".diff-card", "overflow"), (
        "aucune règle ne déclare plus overflow sur .diff-card")
    corps = _porte(".diff-card", "overflow")
    assert "hidden" in corps, corps
    blob = _porte(".diff-card::before", "inset")
    assert blob and "-60%" in blob, (
        "le blob ne déborde plus : le rognage n'est peut-être plus nécessaire, "
        "et le réglage de l'infobulle mérite d'être rouvert — %r" % blob)


def test_l_infobulle_est_reglee_DANS_la_boite_de_la_carte():
    """LE DÉFAUT QU'UNE CAPTURE A MONTRÉ. La convention maison range la bulle
    au-dessus de l'élément. Posée telle quelle sur une carte qui rogne, elle
    est INVISIBLE — et rien ne le dit : l'attribut est là, la règle est là.

    CE QUE CETTE RÈGLE EXIGE : un `bottom` compté depuis le bas de la carte
    vers l'intérieur, en longueurs ABSOLUES, et un `top:auto` qui annule
    l'ancrage hérité. Un `bottom:calc(100% + …)` recommence le défaut.

    POURQUOI « ABSOLUES » ET NON « UNE SEULE LONGUEUR ». Une première version
    exigeait un nombre nu ; l'arrivée de l'appel sous la bulle a rendu ce
    décalage une somme — le fond de la carte, la hauteur de l'appel, l'écart.
    La règle tombait alors sur la FORME de l'expression, pas sur ce qu'elle
    voulait dire. Ce qui rejette la bulle hors de la carte, c'est une unité
    qui se résout sur la taille de la carte ou de la fenêtre ; c'est cela
    qu'on interdit."""
    apres = ".diff-card[data-tooltip]::after"
    bas = _declaration(apres, "bottom")
    assert bas is not None, "%s ne déclare pas bottom" % apres
    interdites = re.findall(r"\d+\s*(%|v[hw]|svh|dvh|lvh)", bas)
    assert not interdites, (
        "bottom:%s se résout sur la taille de la carte ou de la fenêtre — la "
        "bulle repasserait hors de la boîte, qui la rogne" % bas)
    assert re.search(r"\d+(\.\d+)?px", bas), (
        "bottom:%s ne porte aucune longueur absolue" % bas)
    assert _declaration(apres, "top") == "auto", (
        "sans top:auto, l'ancrage haut hérité de la convention subsiste")
    for cote in ("left", "right"):
        v = _declaration(apres, cote)
        assert v and re.match(r"^\d+(\.\d+)?px$", v), (
            "%s:%s — la bulle doit tenir entre les deux bords de la carte"
            % (cote, v))


def test_la_convention_pose_toujours_sa_bulle_AU_DESSUS():
    """LE SECOND GARDE-FOU. La règle précédente corrige un réglage hérité ;
    si la convention elle-même changeait d'ancrage, la correction n'aurait
    plus d'objet et il faudrait la retirer, pas la garder."""
    bas = _declaration("[data-tooltip]::after", "bottom")
    assert bas and "calc(100%" in bas.replace(" ", ""), (
        "la convention [data-tooltip] ne range plus sa bulle au-dessus "
        "(bottom:%s) : le cadrage de .diff-card est peut-être devenu inutile"
        % bas)


def test_la_fleche_de_la_convention_ne_FUIT_pas_sur_le_blob():
    """LE ::before DE LA CARTE EST DÉJÀ PRIS. Le blob le remplit ; la flèche
    de la convention ne peut pas s'y loger. Mais deux de ses déclarations ne
    sont PAS réécrites par la règle du blob, et fuiraient donc dessus : un
    contour de 5 px dont le haut est teinté — un arc violet sur un disque
    flouté — et une translation d'une demi-largeur vers la gauche.

    LE GARDE-FOU, DES DEUX CÔTÉS : on vérifie d'abord que la fuite existe
    vraiment, sans quoi la neutralisation ne neutraliserait rien."""
    fleche = None
    for sel, corps in _regles():
        if sel == "[data-tooltip]::before":
            fleche = corps
    assert fleche, "la flèche de la convention a disparu"
    assert "border-top-color" in fleche and "translateX(-50%)" in fleche.replace(" ", ""), (
        "la flèche ne porte plus les deux déclarations qui fuient : %r" % fleche)

    avant = ".diff-card[data-tooltip]::before"
    assert _declaration(avant, "border") == "0", (
        "le contour de la flèche n'est pas annulé : il peindrait un arc sur le blob")
    assert _declaration(avant, "transform") == "none", (
        "la translation de la flèche n'est pas annulée : elle décalerait le blob")


# ══════════════════════════════════════════════════════════════════════════
#  5. L'ANCRAGE DES CHIFFRES — CE QUE LA PAGE PEUT PROUVER
# ══════════════════════════════════════════════════════════════════════════
#  Une infobulle est du texte affirmatif, court, et lu au moment où le
#  visiteur hésite. Un chiffre inventé y est plus coûteux qu'ailleurs.
#  Ces règles ne vérifient pas que les chiffres sont beaux : elles les
#  DÉRIVENT de ce que le site montre, et comparent.

def test_les_secteurs_ANNONCES_sont_ceux_QUE_LA_PAGE_MONTRE():
    """LE DÉFAUT MESURÉ. La carte elle-même annonce « plus de 20 secteurs
    industriels » ; la page en affiche douze. L'infobulle ne reprend pas ce
    chiffre : elle renvoie à la grille, qu'on peut compter."""
    secteurs = _section("secteurs").count('class="sector-card')
    assert secteurs > 0, "la grille des secteurs est vide"
    mot = EN_LETTRES.get(secteurs)
    assert mot, (
        "la page montre %d secteurs — ajouter ce nombre à EN_LETTRES, puis "
        "réécrire les trois infobulles tip.df.ind" % secteurs)
    for lg in LANGUES:
        texte = _dico(lg)["tip.df.ind"]
        assert re.search(r"\b%s\b" % mot[lg], texte, re.I), (
            "tip.df.ind (%s) n'annonce pas les %d secteurs que la page "
            "montre : %r" % (lg, secteurs, texte))


def test_les_referentiels_et_leurs_modules_sont_COMPTES_sur_la_page():
    """LE CHIFFRE ET SON EXCEPTION. La grille des normes porte neuf
    référentiels, dont huit mènent à un module Sentinel — DORA n'a que son
    texte. L'infobulle annonce les deux nombres : si l'un des deux bouge, la
    phrase devient fausse sans que rien d'autre ne tombe."""
    normes = _section("normes")
    total = len(re.findall(r'<div class="nc [^"]*"', normes))
    avec_module = len(re.findall(r'class="nc-go" href="/sentinel\?goto=', normes))
    assert total > 0 and avec_module > 0, (total, avec_module)
    assert avec_module < total, (
        "chaque norme a désormais son module : l'exception que l'infobulle "
        "nomme n'existe plus")
    for nombre in (total, avec_module):
        assert nombre in EN_LETTRES, (
            "%d n'est pas dans EN_LETTRES — l'ajouter, puis réécrire les "
            "trois infobulles tip.df.jur" % nombre)
    for lg in LANGUES:
        texte = _dico(lg)["tip.df.jur"]
        for nombre in (total, avec_module):
            assert re.search(r"\b%s\b" % EN_LETTRES[nombre][lg], texte, re.I), (
                "tip.df.jur (%s) n'annonce pas %d : %r" % (lg, nombre, texte))


def test_les_juridictions_et_les_criteres_ANNONCES_existent_dans_sentinel():
    """UN CHIFFRE QUI NE RENVOIE À RIEN. L'infobulle promet une carte mondiale
    de 46 juridictions sur 12 critères ; le module doit la tenir, sinon elle
    envoie le visiteur chercher ce qui n'est pas là."""
    for lg in LANGUES:
        texte = _dico(lg)["tip.df.intl"]
        nombres = re.findall(r"\b(\d+)\b", texte)
        assert len(nombres) == 2, (
            "tip.df.intl (%s) : %d nombre(s), on en attend deux — %r"
            % (lg, len(nombres), texte))
        for n in nombres:
            assert re.search(r"\b%s\s+(juridictions|crit)" % n, SENTINELJS), (
                "tip.df.intl annonce %s, que le module Sentinel ne dit nulle "
                "part" % n)


def test_le_module_NOMME_par_l_infobulle_des_couts_existe():
    """L'INFOBULLE NOMME UN MODULE ET DÉCRIT CE QU'IL FAIT D'ABORD : afficher
    la couverture du chiffrage avant le moindre montant. Si le panneau
    disparaissait, ou si la couverture cessait de précéder les montants, la
    promesse deviendrait creuse."""
    assert '<div class="page" id="p-finops">' in SENTINEL, (
        "le panneau FinOps a disparu de Sentinel")
    panneau = SENTINEL[SENTINEL.find('<div class="page" id="p-finops">"'.rstrip('"')):]
    panneau = panneau[:panneau.find('<div class="page" id="p-', 10)]
    couverture = panneau.find('id="fo-couverture"')
    montants = panneau.find('id="fo-montants"')
    assert couverture > 0 and montants > 0, (couverture, montants)
    assert couverture < montants, (
        "les montants précèdent désormais la couverture : l'infobulle "
        "tip.df.eco affirme le contraire")
    for lg in LANGUES:
        assert re.search(r"finops", _dico(lg)["tip.df.eco"], re.I), (
            "tip.df.eco (%s) ne nomme plus le module qu'elle décrit" % lg)


@pytest.mark.parametrize("cle", CARTES)
def test_l_infobulle_AJOUTE_quelque_chose_a_la_carte(cle):
    """UNE INFOBULLE QUI REDIT LA DESCRIPTION COÛTE UN SURVOL POUR RIEN, et
    masque le texte qu'elle recopie — car elle s'affiche par-dessus.
    On mesure la plus longue suite de mots commune aux deux."""
    fr = _dico("fr")
    bulle, desc = _mots(fr["tip." + cle]), _mots(fr[cle + ".d"])
    plus_longue, n = 0, len(desc)
    for i in range(len(bulle)):
        for j in range(n):
            k = 0
            while i + k < len(bulle) and j + k < n and bulle[i + k] == desc[j + k]:
                k += 1
            plus_longue = max(plus_longue, k)
    assert plus_longue < 5, (
        "tip.%s reprend %d mots de suite de sa propre description"
        % (cle, plus_longue))


# ══════════════════════════════════════════════════════════════════════════
#  6. L'APPEL — CHAQUE CARTE MÈNE OÙ SON INFOBULLE PROMET
# ══════════════════════════════════════════════════════════════════════════
#  LA DEMANDE : « connecter la carte 32 ans vers i-aes.com, la carte
#  juridique vers la grille neuf référentiels huit modules, carte
#  international vers module 46 juridictions, carte coûts vers page finops,
#  agent industrie vers grille 12 secteurs, assistants IA vers modules
#  OWASP ».
#
#  LE CHOIX DE FORME, ET IL VIENT D'UNE CONSIGNE ANTÉRIEURE. Deux fois déjà,
#  sur les cartes de risque puis sur celles des services : « seul le cliquage
#  sur ouvrir le module doit rediriger ». La carte entière n'est donc PAS un
#  lien ; c'est un appel nommé, posé au bas de chaque carte.

#: OÙ MÈNE CHAQUE CARTE. Une seule table, parcourue par plusieurs règles.
DESTINATIONS = {
    "df.ai":   "/sentinel?goto=owasp-dix",
    "df.ind":  "#secteurs",
    "df.eco":  "/sentinel?goto=finops",
    "df.exp":  "https://i-aes.com",
    "df.jur":  "#normes",
    "df.intl": "/sentinel?goto=carto",
}

FLECHES = {"interne": "→", "externe": "↗"}


def _appels():
    """Les appels des six cartes : (clé du titre, href, attributs, libellé)."""
    out = []
    for carte in BLOC.split('<div class="diff-card"')[1:]:
        titre = re.search(r'<h3 class="diff-title" data-i18n="([^"]+)\.t"', carte)
        lien = re.search(r'<a class="diff-go" href="([^"]*)"([^>]*)>(.*?)</a>',
                         carte, re.S)
        out.append((titre.group(1) if titre else None,
                    unescape(lien.group(1)) if lien else None,
                    lien.group(2) if lien else None,
                    lien.group(3) if lien else None))
    return out


def test_CHACUNE_des_six_cartes_porte_son_appel():
    """CINQ CARTES CONNECTÉES SUR SIX, C'EST UNE SECTION QUI PARAÎT INERTE :
    le visiteur qui tombe d'abord sur la sixième conclut que ces cartes ne
    mènent nulle part, et ne réessaie pas sur les autres."""
    vus = _appels()
    assert len(vus) == 6, vus
    manquants = [t for t, href, _, _ in vus if not href]
    assert not manquants, "cartes sans appel : %s" % manquants


def test_l_appel_mène_là_où_la_DEMANDE_l_a_envoyé():
    """UN APPEL JUSTE SUR LA MAUVAISE CARTE ENVOIE LE VISITEUR AILLEURS avec
    l'assurance d'un lien nommé — le pire des deux mondes."""
    vus = [(t, href) for t, href, _, _ in _appels()]
    assert vus == [(c, DESTINATIONS[c]) for c in CARTES], vus


def test_les_destinations_SENTINEL_existent_comme_panneau_ET_comme_onglet():
    """UNE DESTINATION INCONNUE N'AFFICHE AUCUNE ERREUR DANS SENTINEL : la
    page s'ouvre sur le sommaire, et le visiteur croit avoir mal cliqué.
    `hubGo` retrouve l'onglet par son `onclick` : chaque cible doit donc
    exister DEUX fois — comme panneau, et comme entrée de menu."""
    vises = [re.search(r"goto=([a-z0-9-]+)", h).group(1)
             for _, h, _, _ in _appels() if h.startswith("/sentinel")]
    assert len(vises) == 3, vises
    for cible in vises:
        assert '<div class="page" id="p-%s">' % cible in SENTINEL, (
            "aucun panneau p-%s dans Sentinel" % cible)
        assert "go('%s',this," % cible in SENTINEL, (
            "aucun onglet ne mène à %s : le lien ouvrira le sommaire" % cible)


def test_les_liens_vers_Sentinel_gardent_la_page_d_accueil():
    """CES APPELS PARTENT D'UNE PAGE PUBLIQUE VERS UN PRODUIT DERRIÈRE
    AUTHENTIFICATION : ils s'adressent par construction à quelqu'un qui n'est
    pas connecté. Dans l'onglet courant, un clic remplacerait l'accueil par un
    formulaire de connexion — le lien marche, la destination est juste, et la
    visite s'arrête là. Mesuré au navigateur une fois déjà, sur d'autres
    liens de cette même page."""
    for titre, href, attrs, _ in _appels():
        if not href.startswith(("/sentinel", "http")):
            continue
        assert 'target="_blank"' in attrs, (
            "%s reste dans l'onglet courant" % titre)
        assert "noopener" in attrs, (
            "%s ouvre un onglet sans noopener : la page ouverte garde la main "
            "sur celle qui l'a ouverte" % titre)


def test_les_ANCRES_restent_dans_l_onglet_courant():
    """OUVRIR UN NOUVEL ONGLET POUR DESCENDRE DE DEUX SECTIONS SUR LA PAGE
    QU'ON LIT DÉJÀ est une perte sèche : le visiteur se retrouve avec deux
    copies de l'accueil et perd sa position dans la première."""
    for titre, href, attrs, _ in _appels():
        if not href.startswith("#"):
            continue
        assert "target=" not in attrs, (
            "%s ouvre un onglet pour une ancre de la même page" % titre)


def test_les_deux_grilles_VISEES_existent_sur_cette_page():
    vises = [h[1:] for _, h, _, _ in _appels() if h.startswith("#")]
    assert len(vises) == 2, vises
    for cible in vises:
        assert 'id="%s"' % cible in INDEX, "aucune section #%s" % cible


def test_les_grilles_visees_se_DEGAGENT_de_l_en_tete_fixe():
    """LE DÉFAUT MESURÉ AU NAVIGATEUR AVANT D'Y TOUCHER. L'en-tête fixe occupe
    les 108 premiers pixels ; une ancre dépose la section à zéro. Le surtitre
    et le haut du titre passaient DESSOUS — pour les liens du menu comme pour
    les appels neufs. Les deux sections visées réservent désormais la hauteur
    de l'en-tête ; mesuré après : le surtitre tombe à 196, l'en-tête finit à
    108."""
    vises = sorted(h[1:] for _, h, _, _ in _appels() if h.startswith("#"))
    marge = None
    for sel, corps in _regles():
        if all(("#" + c) in sel for c in vises):
            m = re.search(r"scroll-margin-top\s*:\s*(\d+)px", corps)
            if m:
                marge = int(m.group(1))
    assert marge is not None, (
        "les sections %s ne réservent plus la hauteur de l'en-tête fixe"
        % vises)
    assert marge >= 108, (
        "scroll-margin-top:%dpx — l'en-tête fixe descend à 108px, le surtitre "
        "repasserait dessous" % marge)


def test_le_module_46_juridictions_VISE_est_bien_celui_qui_les_PORTE():
    """L'INFOBULLE PROMET UNE CARTE MONDIALE DE 46 JURIDICTIONS SUR 12
    CRITÈRES, ET L'APPEL OUVRE UN PANNEAU. Les deux doivent désigner la même
    chose : on relève les nombres dans l'infobulle, on suit l'appel jusqu'au
    panneau, et on exige que le panneau les porte. Une promesse et une porte
    qui ne mènent pas au même endroit, c'est la forme la plus coûteuse de
    lien mort — celle qui a l'air de marcher."""
    href = dict((t, h) for t, h, _, _ in _appels())["df.intl"]
    cible = re.search(r"goto=([a-z0-9-]+)", href).group(1)
    debut = SENTINEL.find('<div class="page" id="p-%s">' % cible)
    assert debut > 0, cible
    suite = SENTINEL.find('<div class="page" id="p-', debut + 10)
    panneau = SENTINEL[debut:suite if suite > 0 else debut + 6000]
    for nombre in re.findall(r"\b(\d+)\b", _dico("fr")["tip.df.intl"]):
        assert re.search(r"\b%s\b" % nombre, panneau), (
            "l'infobulle annonce %s, le panneau p-%s ne le dit pas"
            % (nombre, cible))


def test_le_module_OWASP_VISE_est_celui_que_l_infobulle_NOMME():
    href = dict((t, h) for t, h, _, _ in _appels())["df.ai"]
    assert "owasp" in href, href
    assert re.search(r"owasp", _dico("fr")["tip.df.ai"], re.I), (
        "l'infobulle de la carte ne nomme plus ce que l'appel ouvre")


def test_le_module_FinOps_VISE_est_celui_que_l_infobulle_NOMME():
    href = dict((t, h) for t, h, _, _ in _appels())["df.eco"]
    assert "finops" in href, href
    assert re.search(r"finops", _dico("fr")["tip.df.eco"], re.I), (
        "l'infobulle de la carte ne nomme plus ce que l'appel ouvre")


# ── LE LIBELLÉ DE L'APPEL, DANS LES TROIS LANGUES ────────────────────────

def _cles_appel():
    return ["dg." + c.split(".")[1] for c in CARTES]


def test_le_libelle_de_l_appel_est_celui_du_dictionnaire_francais():
    fr = _dico("fr")
    for (_, _, _, dedans), cle in zip(_appels(), _cles_appel()):
        m = re.search(r'<span data-i18n="%s">(.*?)</span>' % re.escape(cle),
                      dedans, re.S)
        assert m, "l'appel ne porte pas le libellé traduisible %s" % cle
        assert unescape(m.group(1)) == fr[cle], (
            "%s : la page dit %r, le dictionnaire %r"
            % (cle, unescape(m.group(1)), fr[cle]))


@pytest.mark.parametrize("lg", LANGUES)
def test_les_six_libelles_existent_dans_la_langue(lg):
    dico = _dico(lg)
    manquants = [c for c in _cles_appel() if not (dico.get(c) or "").strip()]
    assert not manquants, "libellés absents du dictionnaire %s : %s" % (lg, manquants)


@pytest.mark.parametrize("cle", ["dg." + c.split(".")[1] for c in CARTES])
def test_les_trois_langues_donnent_des_libelles_DIFFERENTS(cle):
    textes = {lg: _dico(lg)[cle] for lg in LANGUES}
    for a, b in (("fr", "en"), ("fr", "de"), ("en", "de")):
        assert textes[a] != textes[b], (
            "%s : %s et %s portent le même libellé — %r"
            % (cle, a, b, textes[a]))


def test_la_FLECHE_reste_hors_du_texte_traduit():
    """LE PIÈGE QUI A COÛTÉ DEUX FOIS À CE DÉPÔT. `applyLang` remplace
    l'innerHTML de tout porteur de `data-i18n` : ce qui vit DEDANS disparaît
    au premier changement de langue, sans erreur et sans trace. La flèche
    reste donc à côté du span, jamais dedans.

    LE GARDE-FOU : on vérifie d'abord qu'il y a bien une flèche à préserver."""
    for titre, href, _, dedans in _appels():
        m = re.search(r'<span data-i18n="dg\.[a-z]+">(.*?)</span>(.*)$',
                      dedans, re.S)
        assert m, "l'appel de %s n'a pas la forme span + flèche" % titre
        dans, apres = m.group(1), m.group(2)
        fleche = FLECHES["externe"] if href.startswith("http") else FLECHES["interne"]
        assert fleche in apres, (
            "%s : la flèche %s manque après le span (reste : %r)"
            % (titre, fleche, apres))
        for f in FLECHES.values():
            assert f not in dans, (
                "%s : la flèche est DANS le texte traduit — le premier "
                "changement de langue l'effacera" % titre)


def test_le_libelle_du_lien_i_aes_ne_NOMME_pas_le_domaine():
    """LA COLLISION MESURÉE AVEC LA BASCULE DU SITE INSTITUTIONNEL.

    `bascule.js` réécrit les liens vers i-aes.com quand le site ne répond pas
    — un pare-feu d'entreprise suffit — et relabellise ceux dont le TEXTE
    nomme le domaine, par `textContent`. Ce geste efface tout le balisage de
    l'élément. Or cet appel est le PREMIER lien i-aes.com du site à porter du
    balisage : son `<span data-i18n>` et sa flèche disparaîtraient, et le
    libellé cesserait d'être traduit — silencieusement.

    Un libellé qui ne cite pas le domaine n'a pas à être relabellisé : la
    bascule fait quand même son travail sur l'adresse et sur l'infobulle
    native, et la traduction survit. Mesuré au navigateur dans l'état dégradé,
    que ce bac à sable reproduit naturellement.

    LES DEUX GARDE-FOUS : sans eux, cette règle interdirait un mot sans
    raison. On vérifie que la bascule existe, qu'elle relabellise toujours par
    `textContent`, et qu'elle ne le fait QUE sur les libellés qui citent le
    domaine."""
    bascule = io.open(os.path.join(_RACINE, "bascule.js"), encoding="utf-8").read()
    assert 'var CIBLE = "i-aes.com"' in bascule, (
        "la bascule ne vise plus i-aes.com : cette règle n'a plus d'objet")
    assert re.search(r"el\.textContent\s*=\s*t\.replace\(CIBLE", bascule), (
        "la bascule ne relabellise plus par textContent : le balisage ne "
        "risque plus rien, et cette contrainte peut être levée")
    assert "t.indexOf(CIBLE) >= 0" in bascule, (
        "la bascule relabellise désormais sans regarder le texte : éviter le "
        "domaine ne protège plus rien")

    href = dict((t, h) for t, h, _, _ in _appels())["df.exp"]
    assert "i-aes.com" in href, href
    for lg in LANGUES:
        libelle = _dico(lg)["dg.exp"]
        assert "i-aes.com" not in libelle, (
            "le libellé %s cite le domaine (%r) : la bascule effacerait le "
            "span traduit et la flèche" % (lg, libelle))


# ── LA BULLE ET L'APPEL SE PARTAGENT LE BAS DE LA CARTE ──────────────────

def test_UN_SEUL_nombre_commande_la_boite_de_l_appel_ET_son_degagement():
    """LA BULLE ÉTAIT RÉGLÉE EXACTEMENT LÀ OÙ L'APPEL EST ARRIVÉ. Deux nombres
    tenus séparément — la hauteur du lien d'un côté, le dégagement de l'autre
    — auraient fini par diverger, et la bulle aurait recouvert le lien qu'elle
    est censée laisser cliquable. Une seule déclaration les commande."""
    var = "--diff-appel"
    declare = _declaration(".diff-card[data-tooltip]", var)
    assert declare and re.match(r"^\d+px$", declare), (
        "%s n'est pas déclarée sur la carte : %r" % (var, declare))
    hauteur = _declaration(".diff-go", "height")
    assert hauteur and var in hauteur, (
        "la boîte de l'appel ne suit pas %s : height:%s" % (var, hauteur))
    degagement = _declaration(".diff-card[data-tooltip]::after", "bottom")
    assert degagement and var in degagement, (
        "le dégagement de la bulle ne suit pas %s : bottom:%s"
        % (var, degagement))


def test_l_appel_est_COLLE_en_bas_de_la_carte():
    """POURQUOI LE DÉGAGEMENT NE SUFFIT PAS SEUL. Les cartes d'une même rangée
    s'étirent à la plus haute, mais leur contenu reste calé en haut : l'appel
    d'une carte au texte court remonte, et un dégagement compté depuis le bas
    ne le protège plus. Collé au bas, sa position ne dépend plus de la
    longueur du texte."""
    assert _declaration(".diff-card[data-tooltip]", "display") == "flex", (
        "la carte n'est plus une colonne flexible")
    assert _declaration(".diff-card[data-tooltip]", "flex-direction") == "column"
    assert _declaration(".diff-go", "margin-top") == "auto", (
        "l'appel n'est plus collé au bas : le dégagement de la bulle devient "
        "une supposition sur la longueur du texte")


# ══════════════════════════════════════════════════════════════════════════
#  7. CE QUI EXIGE UN COMPTE LE DIT AVANT LE CLIC
# ══════════════════════════════════════════════════════════════════════════
#  LE DÉFAUT SIGNALÉ, PUIS MESURÉ. « Un clic tombe sur une page de
#  connexion ». Trois des six appels mènent à /sentinel, gardé par
#  `sentinel_login_required` : un visiteur non connecté qui clique
#  « Ouvrir le module OWASP » reçoit un champ mot de passe. Le lien
#  fonctionne, la destination est juste, et la visite s'arrête là.
#
#  ON NE RETIRE PAS LES LIENS : le module est bien là, derrière un compte
#  gratuit. On le DIT avant le clic, ce qui coûte une ligne et rend la
#  décision au visiteur.

APP = io.open(os.path.join(_RACINE, "app.py"), encoding="utf-8").read()
BASCULE = io.open(os.path.join(_RACINE, "bascule.js"), encoding="utf-8").read()


def _routes_gardees():
    """Les adresses que `sentinel_login_required` protège, lues dans app.py.

    ON NE TIENT PAS DE LISTE À LA MAIN. Une liste recopiée ici vieillirait
    en silence : le jour où un module s'ouvrirait au public, la mention
    « connexion requise » resterait, et personne ne la démentirait."""
    gardees = set()
    for m in re.finditer(r"@app\.route\((['\"])([^'\"]+)\1[^)]*\)\s*\n"
                         r"(?:@[^\n]+\n)*?@sentinel_login_required", APP):
        gardees.add(m.group(2))
    return gardees


def _mentions():
    """Par carte : (clé du titre, href de l'appel, texte de la mention|None)."""
    out = []
    for carte in BLOC.split('<div class="diff-card"')[1:]:
        titre = re.search(r'<h3 class="diff-title" data-i18n="([^"]+)\.t"', carte)
        lien = re.search(r'<a class="diff-go" href="([^"]*)"', carte)
        note = re.search(r'<span class="diff-cnx">(.*?)</span>\s*</span>',
                         carte, re.S)
        out.append((titre.group(1) if titre else None,
                    unescape(lien.group(1)) if lien else None,
                    note.group(1) if note else None))
    return out


def test_la_page_SENTINEL_exige_toujours_un_compte():
    """LE GARDE-FOU DE TOUTE CETTE SECTION. La mention n'est vraie que tant
    que /sentinel est gardé. Si le produit s'ouvrait au public, elle
    deviendrait un mensonge affiché en toutes lettres — et rien d'autre ne
    le signalerait."""
    gardees = _routes_gardees()
    assert "/sentinel" in gardees, (
        "/sentinel n'est plus derrière `sentinel_login_required` : la mention "
        "« connexion requise » des trois appels est à retirer. Routes gardées "
        "relevées : %s" % sorted(gardees))


def test_la_mention_est_sur_les_appels_GARDES_et_sur_EUX_SEULS():
    """DES DEUX CÔTÉS, ET C'EST LE POINT. Un appel gardé sans mention envoie
    le visiteur sur un formulaire sans prévenir ; une mention sur un appel
    LIBRE décourage un clic qui n'aurait rien coûté. Les deux se mesurent
    ici, contre ce que `app.py` garde réellement."""
    gardees = _routes_gardees()
    attendu, vu = [], []
    for titre, href, note in _mentions():
        chemin = href.split("?")[0]
        attendu.append((titre, chemin in gardees))
        vu.append((titre, note is not None))
    assert vu == attendu, (
        "mention et garde ne coïncident pas.\n  attendu : %s\n  vu      : %s"
        % (attendu, vu))
    assert sum(1 for _, g in attendu if g) == 3, attendu


def test_la_mention_est_TRADUITE_dans_les_trois_langues():
    for lg in LANGUES:
        assert (_dico(lg).get("dg.cnx") or "").strip(), (
            "dg.cnx absente du dictionnaire %s" % lg)
    textes = {lg: _dico(lg)["dg.cnx"] for lg in LANGUES}
    for a, b in (("fr", "en"), ("fr", "de"), ("en", "de")):
        assert textes[a] != textes[b], (
            "dg.cnx : %s et %s portent le même texte — %r" % (a, b, textes[a]))


def test_le_CADENAS_reste_hors_du_texte_traduit():
    """MÊME PIÈGE QUE LA FLÈCHE. `applyLang` remplace l'innerHTML du porteur
    de `data-i18n` : un cadenas écrit dedans disparaîtrait au premier
    changement de langue. Il est donc frère du span, jamais dedans."""
    fr = _dico("fr")["dg.cnx"]
    assert "🔒" not in fr, (
        "le cadenas est DANS le texte traduit : le premier changement de "
        "langue l'effacera")
    for titre, _, note in _mentions():
        if note is None:
            continue
        m = re.search(r'^(.*?)<span data-i18n="dg\.cnx">', note, re.S)
        assert m and "🔒" in m.group(1), (
            "%s : la mention n'affiche pas le cadenas avant son texte — %r"
            % (titre, note[:60]))


def test_le_degagement_de_la_bulle_COMPTE_la_mention():
    """LA BULLE EST RÉGLÉE EN BAS DE LA CARTE, ET LA MENTION S'Y AJOUTE SOUS
    L'APPEL. Sans réservation, la bulle recouvrirait la phrase qu'on vient
    d'écrire pour prévenir le visiteur — le contraire du but.

    UN SEUL NOMBRE COMMANDE LES DEUX, comme pour l'appel : `--diff-cnx-h`
    dessine la boîte de la mention, et `:has` le reporte en réservation.
    C'est la PRÉSENCE de la mention qui décide, pas un attribut parallèle
    qu'il faudrait tenir en accord avec elle."""
    var = "--diff-cnx-h"
    hauteur = _declaration(".diff-card[data-tooltip]", var)
    assert hauteur and re.match(r"^\d+px$", hauteur), (
        "%s n'est pas déclarée sur la carte : %r" % (var, hauteur))
    assert _declaration(".diff-cnx", "height") and \
        var in _declaration(".diff-cnx", "height"), (
        "la boîte de la mention ne suit pas %s" % var)
    reserve = _declaration(".diff-card[data-tooltip]:has(.diff-cnx)", "--diff-cnx")
    assert reserve and var in reserve, (
        "la réservation ne suit pas %s : %r" % (var, reserve))
    degagement = _declaration(".diff-card[data-tooltip]::after", "bottom")
    assert degagement and "--diff-cnx" in degagement, (
        "le dégagement de la bulle ignore la mention : bottom:%s" % degagement)


# ── LE LIEN INSTITUTIONNEL N'EST PLUS DÉTOURNÉ ───────────────────────────

def test_le_relais_de_la_bascule_est_LUI_MEME_garde():
    """POURQUOI L'APPEL INSTITUTIONNEL SORT DU RELAIS — le garde-fou de la
    règle suivante. `bascule.js` réécrit les liens i-aes.com vers /sentinel,
    qui exige un compte : pour un visiteur non connecté, le relais change
    « le site ne répond pas » en « créez un compte ». Mesuré au navigateur :
    un clic anonyme aboutissait à « Connexion — Sentinel AI ».

    Si le relais cessait d'être gardé, l'exception n'aurait plus d'objet et
    il faudrait la retirer, pas la conserver par habitude."""
    m = re.search(r'var RELAIS\s*=\s*"([^"]+)"', BASCULE)
    assert m, "le relais de la bascule est introuvable"
    assert m.group(1) in _routes_gardees(), (
        "le relais %s n'exige plus de compte : l'exception posée sur l'appel "
        "institutionnel peut être levée" % m.group(1))


def test_l_appel_institutionnel_REFUSE_le_relais():
    """UNE CARTE QUI PROMET LE SITE INSTITUTIONNEL DOIT Y MENER. Tomber sur
    une page en panne se comprend ; tomber sur un formulaire de connexion,
    non — c'est ce qui a été signalé.

    LES DEUX GARDE-FOUS. Sans eux, cet attribut serait un ornement : on
    vérifie que la bascule détourne toujours les liens i-aes.com, et qu'elle
    HONORE l'exception au lieu de l'ignorer."""
    assert 'a[href*="' in BASCULE and 'var CIBLE = "i-aes.com"' in BASCULE, (
        "la bascule ne ramasse plus les liens i-aes.com : l'exception ne "
        "protège plus de rien")
    assert re.search(r'hasAttribute\("data-bascule-jamais"\)\s*\)\s*continue',
                     BASCULE), (
        "la bascule n'honore pas `data-bascule-jamais` : l'attribut posé sur "
        "l'appel ne fait rien")

    href, attrs = None, None
    for carte in BLOC.split('<div class="diff-card"')[1:]:
        m = re.search(r'<a class="diff-go" href="(https://i-aes\.com[^"]*)"([^>]*)>',
                      carte)
        if m:
            href, attrs = m.group(1), m.group(2)
    assert href, "aucun appel ne mène au site institutionnel"
    assert "data-bascule-jamais" in attrs, (
        "l'appel institutionnel est encore détournable : un visiteur dont le "
        "réseau bloque i-aes.com recevrait un formulaire de connexion")


def test_les_AUTRES_liens_institutionnels_gardent_le_relais():
    """L'EXCEPTION RESTE UNE EXCEPTION. Le logo, l'icône et la mention du
    pied de page ne promettent pas une destination précise : le relais y
    garde son intérêt. Si l'attribut se répandait, la bascule cesserait de
    servir sans que personne ne l'ait décidé."""
    liens = re.findall(r'<a [^>]*href="https://i-aes\.com[^"]*"[^>]*>', INDEX)
    assert len(liens) >= 3, (
        "%d lien(s) vers i-aes.com relevés : la lecture a changé de forme"
        % len(liens))
    exemptes = [l for l in liens if "data-bascule-jamais" in l]
    assert len(exemptes) == 1, (
        "%d liens sortent du relais, on en attend un seul (l'appel de la "
        "carte) : %s" % (len(exemptes), exemptes))


# ══════════════════════════════════════════════════════════════════════════
#  8. LA BATTERIE DE MUTATIONS NE SE PÉRIME PLUS EN SILENCE
# ══════════════════════════════════════════════════════════════════════════

def test_chaque_ancre_de_la_batterie_de_mutations_EXISTE_ENCORE():
    """CE QUI S'EST PASSÉ TROIS FOIS, ET QUI A MOTIVÉ CETTE RÈGLE.

    La batterie vit dans un fichier de chaînes littérales. Chaque fois que le
    code qu'elle mute a changé — le réglage de la bulle, puis l'arrivée de
    l'appel, puis celle de la mention — des ancres ont cessé de correspondre.
    Une ancre périmée ne mute RIEN : la mutation ne tombe pas, la règle
    qu'elle devait éprouver n'est plus éprouvée, et personne ne le sait
    jusqu'à la prochaine exécution manuelle de la batterie.

    Une batterie qu'on croit complète et qui ne couvre plus ce qu'elle
    prétend est exactement le défaut que ce dépôt traque partout ailleurs.
    Elle est donc vérifiée par la suite, à chaque passage.

    CE QUE CETTE RÈGLE NE FAIT PAS : exécuter les mutations. Elle garde
    l'outil, pas le résultat — la batterie se lance à part."""
    chemin = os.path.join(_RACINE, "tests", "mutations_distinction.json")
    table = json.loads(io.open(chemin, encoding="utf-8").read())
    muts = table["mutations"]
    assert len(muts) >= 50, (
        "%d mutations seulement : la batterie a maigri sans qu'on le dise"
        % len(muts))

    fichiers, perimees, sans_effet = {}, [], []
    for m in muts:
        f = m["fichier"]
        if f not in fichiers:
            fichiers[f] = io.open(os.path.join(_RACINE, f), encoding="utf-8").read()
        n = fichiers[f].count(m["avant"])
        if n != 1:
            perimees.append("%s — %s : %d occurrence(s)" % (f, m["nom"], n))
        if m["avant"] == m["apres"]:
            sans_effet.append(m["nom"])
    assert not perimees, (
        "%d ancre(s) périmée(s) : ces mutations ne modifient plus rien et "
        "les règles qu'elles éprouvent ne sont plus éprouvées.\n  %s"
        % (len(perimees), "\n  ".join(perimees)))
    assert not sans_effet, "mutations sans effet : %s" % sans_effet

    nommees = {m["regle"].split("[")[0] for m in muts}
    source = io.open(os.path.abspath(__file__), encoding="utf-8").read()
    voisin = io.open(os.path.join(_RACINE, "tests",
                                  "test_offres_services.py"), encoding="utf-8").read()
    absentes = [r for r in nommees
                if ("def %s(" % r) not in source and ("def %s(" % r) not in voisin]
    assert not absentes, (
        "la batterie vise des règles qui n'existent plus : %s" % absentes)
