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

    CE QUE CETTE RÈGLE EXIGE : un `bottom` en longueur simple, qui compte
    depuis le bas de la carte vers l'intérieur, et un `top:auto` qui annule
    l'ancrage hérité. Un `bottom:calc(100% + …)` recommence le défaut."""
    apres = ".diff-card[data-tooltip]::after"
    bas = _declaration(apres, "bottom")
    assert bas is not None, "%s ne déclare pas bottom" % apres
    assert "%" not in bas, (
        "bottom:%s remet la bulle HORS de la carte, qui la rognera" % bas)
    assert re.match(r"^\d+(\.\d+)?px$", bas), (
        "bottom:%s n'est pas une longueur simple" % bas)
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
