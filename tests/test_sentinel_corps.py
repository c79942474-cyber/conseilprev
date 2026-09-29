# -*- coding: utf-8 -*-
"""LE CORPS DE SENTINEL SE TRADUIT PAR CONTENU — sentinel.i18n.js, la route
/sentinel.en.json et leur branchement dans sentinel.page.js.

CE QUI EXISTAIT, ET CE QUI MANQUAIT. Le moteur bilingue (test_sentinel_bilingue)
traduit la COQUILLE : 213 clés posées par `data-i18n` sur le menu, le fil
d'Ariane et l'identité des pages. Le CORPS — 25 900 mots dans le HTML, 4 000
chaînes rendues par le JavaScript — restait en français, et c'était écrit
comme un choix. La demande est désormais : tout Sentinel en anglais.

LA CONCEPTION QUE CES RÈGLES GARDENT. On ne marque pas 4 300 éléments dans un
fichier de 890 Ko : le corps se traduit PAR CONTENU, à l'exécution, la clé
étant le texte français NORMALISÉ. Deux régimes décidés par la forme de
l'élément — BLOC (mise en forme nue, innerHTML) et TEXTE (nœud par nœud,
nodeValue, un lien survit) — des exclusions nettes, des attributs traduits,
l'original gardé dans une WeakMap et restitué, un observateur pour ce que le
JavaScript rend après coup, un dictionnaire téléchargé une fois et servi
fusionné par Flask.

CES RÈGLES EXÉCUTENT LE CODE. Le VRAI sentinel.i18n.js tourne sous node sur
un DOM réduit à ce qu'il touche (tests/_dom_sentinel_corps.js) ; le VRAI bloc
de sentinel.page.js tourne avec un faux observateur, un faux fetch et une
image différée maîtrisée ; la VRAIE route Flask est appelée sur des dossiers
d'essai. Deux règles seulement lisent le code : celle qui interdit innerHTML
hors du régime bloc — le piège de l'accueil, payé deux fois — et celle qui
garde le module en ES5. La recette navigateur
(recette_sentinel_langue_moteur.js) mesure le reste : la vraie sérialisation,
le vrai observateur, le vrai réseau.
"""
import functools
import html as _html
import io
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RACINE)
os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
os.environ.setdefault('FLASK_SECRET_KEY', 'recette-sentinel-corps')

import sentinel_i18n  # noqa: E402

NODE = shutil.which("node")
MODULE = os.path.join(_RACINE, "sentinel.i18n.js")
HARNAIS = os.path.join(_RACINE, "tests", "_dom_sentinel_corps.js")


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


SRC_MODULE = _lire("sentinel.i18n.js")
PAGE_JS = _lire("sentinel.page.js")
SENTINEL = _lire("sentinel.html")
APP_PY = _lire("app.py")

NBSP, FINE, ESPACE_FINE, BOM = chr(0xA0), chr(0x202F), chr(0x2009), chr(0xFEFF)
E_ACCENT_COMBINE = "e" + chr(0x0301)


def _ids(cas):
    """Les identifiants des cas, en ASCII sans espace : le banc de mutations
    lit le nom d'une règle tombée jusqu'à la première espace, et pytest
    échappe les accents dans les identifiants."""
    import unicodedata
    out = []
    for c in cas:
        s = unicodedata.normalize("NFKD", c[0]).encode("ascii", "ignore").decode()
        out.append(re.sub(r"-+", "-", re.sub(r"[^A-Za-z0-9]+", "-", s)).strip("-"))
    return out


def _code(src):
    """Le CODE sans ses commentaires : un commentaire peut citer `innerHTML`
    pour dire pourquoi on ne l'écrit pas."""
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", "", src)


CODE_MODULE = _code(SRC_MODULE)


# ══════════════════════════════════════════════════════════════════════════
#  LE HARNAIS — le vrai module, un DOM minuscule
# ══════════════════════════════════════════════════════════════════════════

@functools.lru_cache(maxsize=None)
def _jouer_json(programme):
    if not NODE:
        pytest.skip("node absent : le module ne peut pas être exécuté")
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "prog.json")
        io.open(p, "w", encoding="utf-8").write(programme)
        r = subprocess.run([NODE, HARNAIS, MODULE, p],
                           capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail("le module n'a pas tourné :\n%s" % (r.stderr or "")[-2500:])
    return r.stdout


def _jouer(html, ops, dico=None):
    """Joue `ops` sur le fragment `html` avec le dictionnaire `dico` ; rend la
    liste des résultats, un par opération."""
    out = json.loads(_jouer_json(json.dumps(
        {"html": html, "dico": dico or {"texte": {}, "bloc": {}}, "ops": ops},
        ensure_ascii=False, sort_keys=True)))
    for i, r in enumerate(out):
        assert not (isinstance(r, dict) and "erreur" in r), (
            "l'opération %d (%s) a levé : %s" % (i, ops[i]["op"], r["erreur"][:600]))
    return out


# ══════════════════════════════════════════════════════════════════════════
#  1. LA NORMALISATION — la même, en JavaScript et en Python
# ══════════════════════════════════════════════════════════════════════════

CAS_NORMALISATION = [
    ("insécables et fine", "  46" + NBSP + "juridictions" + FINE + "— 2,5 %  ",
     "# juridictions — # %"),
    ("décimales", "2024.1 puis 1,5 et 3", "# puis # et #"),
    ("NFC", E_ACCENT_COMBINE + "t" + E_ACCENT_COMBINE + " 2026", "été #"),
    ("BOM et espace fine", BOM + "x" + ESPACE_FINE + "y  ", "x y"),
    ("tabulations et retours", "a\n\t b\r\n c", "a b c"),
    ("nombre collé à une lettre", "Art. 5 et art5bis", "Art. # et art#bis"),
    ("vide", "   ", ""),
]


@pytest.mark.parametrize("nom,entree,attendu", CAS_NORMALISATION, ids=_ids(CAS_NORMALISATION))
def test_la_normalisation_est_la_MEME_en_JavaScript_et_en_Python(nom, entree, attendu):
    """UNE CLÉ CALCULÉE PAR L'INVENTAIRE (Python) ET CHERCHÉE PAR LE
    NAVIGATEUR (JavaScript) doit être la même chaîne, au caractère près :
    un blanc que l'un réduit et pas l'autre, et rien ne se traduit — sans
    erreur, sans trace."""
    js = _jouer("", [{"op": "normaliser", "valeur": entree}])[0]
    py = sentinel_i18n.normaliser(entree)
    assert js == attendu, "JavaScript : %r" % js
    assert py == attendu, "Python : %r" % py


# ══════════════════════════════════════════════════════════════════════════
#  2. LE CLASSEMENT — bloc, texte, exclu
# ══════════════════════════════════════════════════════════════════════════

CAS_CLASSEMENT = [
    ("gras nu → bloc", '<p id="t">Bonjour <b>le monde</b> !</p>', "bloc"),
    ("gras imbriqué et br → bloc", '<p id="t">Voir <b>x <i>y</i></b><br>z</p>', "bloc"),
    ("lien → texte", '<p id="t">Voir <a href="#">x</a></p>', "texte"),
    ("span à classe → texte", '<p id="t">Voir <span class="k">x</span></p>', "texte"),
    ("gras à id → texte", '<p id="t">Voir <b id="g">x</b></p>', "texte"),
    ("gras à gestionnaire → texte", '<p id="t">Voir <b onclick="x()">x</b></p>', "texte"),
    ("bouton → texte", '<p id="t">Voir <button>x</button></p>', "texte"),
    ("icône svg → texte", '<p id="t">Voir <svg></svg></p>', "texte"),
    ("texte seul → texte", '<p id="t">Bonjour</p>', "texte"),
    ("code → exclu", '<code id="t">x</code>', "exclu"),
    ("pre → exclu", '<pre id="t">x</pre>', "exclu"),
    ("input → exclu", '<input id="t" placeholder="x">', "exclu"),
    ("data-i18n → exclu", '<p id="t" data-i18n="k">x</p>', "exclu"),
    ("data-i18n-bloc → exclu", '<p id="t" data-i18n-bloc="k">x <b>y</b></p>', "exclu"),
    ("translate=no → exclu", '<p id="t" translate="no">x</p>', "exclu"),
    ("ancêtre translate=no → exclu", '<div translate="no"><p id="t">x <b>y</b></p></div>', "exclu"),
    ("dans un pre → exclu", '<pre><span id="t">x</span></pre>', "exclu"),
]


@pytest.mark.parametrize("nom,html,attendu", CAS_CLASSEMENT, ids=_ids(CAS_CLASSEMENT))
def test_le_classement_decide_bloc_texte_ou_exclu(nom, html, attendu):
    """LE RÉGIME EST DÉCIDÉ PAR LA FORME. Un bloc ne contient que de la mise
    en forme SANS attribut : c'est la seule condition sous laquelle réécrire
    l'innerHTML ne perd rien. Un lien, un identifiant, un gestionnaire, une
    classe — tout ce qui porte un comportement — fait retomber en TEXTE, où
    chaque nœud est écrit seul et rien n'est réécrit autour."""
    assert _jouer(html, [{"op": "classer", "sel": "#t"}])[0] == attendu


# ══════════════════════════════════════════════════════════════════════════
#  3. LES CHIFFRES — réinjectés dans l'ordre, ou rien
# ══════════════════════════════════════════════════════════════════════════

CAS_CHIFFRES = [
    ("un compteur", "All (#)", "Toutes (15)", "All (15)"),
    ("deux nombres dans l'ordre", "# of #", "3 sur 12", "3 of 12"),
    ("décimales gardées telles quelles", "# then #", "2,5 % et 2024.1", "2,5 then 2024.1"),
    ("trop de # → rien", "#", "aucun", None),
    ("pas assez de # → rien", "none", "3", None),
    ("une entité HTML n'est pas un emplacement", "&#39;s #", "a 7", "&#39;s 7"),
]


@pytest.mark.parametrize("nom,en,fr,attendu", CAS_CHIFFRES, ids=_ids(CAS_CHIFFRES))
def test_les_chiffres_du_francais_reviennent_dans_l_anglais(nom, en, fr, attendu):
    """« 46 juridictions » n'est pas quarante-six clés. Le nombre devient « # »
    dans la clé et REVIENT dans la valeur — dans l'ordre. Si les comptes ne
    concordent pas, la traduction ne s'affiche PAS : un chiffre déplacé est
    un mensonge, le français vaut mieux."""
    assert _jouer("", [{"op": "digits", "en": en, "fr": fr}])[0] == attendu


# ══════════════════════════════════════════════════════════════════════════
#  4. LA TRADUCTION — et ce qu'elle laisse intact
# ══════════════════════════════════════════════════════════════════════════

FRAGMENT = (
    '<div class="page" id="p-x">'
    '<p id="a">Bonjour <b>le monde</b> !</p>'
    '<p id="b">Voir le <a href="#" onclick="go(\'r\')">Rapport</a>.</p>'
    '<span id="c" title="Fermer la fenêtre">Toutes (15)</span>'
    '<p id="d" translate="no">Bonjour <b>le monde</b> !</p>'
    '<code id="e">Bonjour</code>'
    '<span id="f" data-i18n="k">Bonjour</span>'
    '<input id="g" type="submit" value="Envoyer" placeholder="Bonjour">'
    '<p id="h">' + NBSP + 'Bonjour ' + '<i class="ic"></i>' + '</p>'
    '</div>'
)
DICO = {
    "texte": {"Voir le": "See the", "Rapport": "Report", "Toutes (#)": "All (#)",
              "Fermer la fenêtre": "Close the window", "Bonjour": "Hello",
              "Envoyer": "Send"},
    "bloc": {"Bonjour le monde !": "Hello <b>world</b>!"},
}


def test_le_regime_TEXTE_traduit_autour_du_lien_et_le_lien_SURVIT():
    """LE PIÈGE DE L'ACCUEIL. `el.innerHTML = <traduction>` effaçait un lien
    écrit dans l'élément traduit, sans erreur et sans trace — deux fois dans
    ce dépôt. Ici, le texte autour du lien est écrit nœud par nœud : le lien
    garde son href, son gestionnaire, et son propre texte est traduit seul."""
    html = _jouer(FRAGMENT, [{"op": "traduire", "langue": "en"}, {"op": "html", "sel": "#b"}], DICO)[1]
    assert html == 'See the <a href="#" onclick="go(\'r\')">Report</a>.', html


def test_le_regime_BLOC_traduit_d_un_tenant_et_garde_le_gras():
    html = _jouer(FRAGMENT, [{"op": "traduire", "langue": "en"}, {"op": "html", "sel": "#a"}], DICO)[1]
    assert html == "Hello <b>world</b>!", html


def test_les_attributs_sont_traduits_title_placeholder_et_value_d_un_bouton():
    """UN `title` EST LU, UN `placeholder` EST LU, LA VALEUR D'UN BOUTON EST
    SON LIBELLÉ. Un `input` est exclu du parcours de son contenu — il n'en a
    pas — mais pas de celui de ses attributs."""
    r = _jouer(FRAGMENT, [{"op": "traduire", "langue": "en"},
                          {"op": "attr", "sel": "#c", "nom": "title"},
                          {"op": "attr", "sel": "#g", "nom": "placeholder"},
                          {"op": "attr", "sel": "#g", "nom": "value"}], DICO)
    assert r[1:] == ["Close the window", "Hello", "Send"], r[1:]


def test_une_entree_a_chiffres_garde_ses_chiffres_a_l_ecran():
    r = _jouer(FRAGMENT, [{"op": "traduire", "langue": "en"}, {"op": "texte", "sel": "#c"}], DICO)
    assert r[1] == "All (15)", r[1]


def test_les_blancs_de_tete_et_de_queue_du_noeud_sont_CONSERVES():
    """« consultez le <a>Reporting</a> » : l'espace avant le lien est dans le
    nœud texte. La clé est trimée, le nœud ne l'est pas — sinon deux mots se
    collent, et l'insécable qui empêchait une césure disparaît."""
    r = _jouer(FRAGMENT, [{"op": "traduire", "langue": "en"},
                          {"op": "texte", "sel": "#b", "enfant": 0},
                          {"op": "texte", "sel": "#h", "enfant": 0}], DICO)
    assert r[1] == "See the ", repr(r[1])
    assert r[2] == NBSP + "Hello ", repr(r[2])


@pytest.mark.parametrize("sel,pourquoi", [
    ("#d", "translate=\"no\""), ("#e", "un <code>"), ("#f", "data-i18n, l'ancien régime")],
    ids=["translate-no", "code", "data-i18n"])
def test_ce_qui_est_EXCLU_reste_en_francais(sel, pourquoi):
    """translate="no" est ce que le HTML prévoit pour cela ; un <code> est du
    code ; un porteur de data-i18n appartient à l'ancien régime, qui l'écrit
    lui-même — deux moteurs sur le même élément s'écraseraient l'un l'autre."""
    r = _jouer(FRAGMENT, [{"op": "html", "sel": sel}, {"op": "traduire", "langue": "en"},
                          {"op": "html", "sel": sel}], DICO)
    assert r[2] == r[0], "%s (%s) a été touché : %r" % (sel, pourquoi, r[2])


def test_une_cle_absente_du_dictionnaire_laisse_le_francais():
    r = _jouer('<p id="t">Introuvable ici</p>',
               [{"op": "traduire", "langue": "en"}, {"op": "html", "sel": "#t"}], DICO)
    assert r == [0, "Introuvable ici"], r


# ══════════════════════════════════════════════════════════════════════════
#  5. LA RESTITUTION — octet pour octet, et la mémoire se vide
# ══════════════════════════════════════════════════════════════════════════

def test_le_retour_en_francais_restitue_OCTET_POUR_OCTET():
    """RIEN N'EST JAMAIS PERDU. L'original de chaque nœud et de chaque
    attribut touché est gardé ; le retour au français le remet — et le
    document entier est comparé, pas seulement ce qu'on croit avoir touché."""
    r = _jouer(FRAGMENT, [{"op": "html"}, {"op": "traduire", "langue": "en"}, {"op": "html"},
                          {"op": "traduire", "langue": "fr"}, {"op": "html"}], DICO)
    assert r[2] != r[0], "la traduction n'a rien changé"
    assert r[4] == r[0], "après retour :\n%s\navant :\n%s" % (r[4], r[0])


def test_la_memoire_des_originaux_est_VIDEE_au_retour():
    """UNE WEAKMAP QUI GARDE UN ORIGINAL APRÈS RESTITUTION restituerait, à
    la bascule suivante, un français d'AVANT ce que le JavaScript a pu
    réécrire entre-temps. L'entrée est retirée dès que l'original est remis."""
    r = _jouer(FRAGMENT, [{"op": "traduire", "langue": "en"},
                          {"op": "memorise", "sel": "#a"}, {"op": "memorise", "sel": "#c"},
                          {"op": "memorise", "sel": "#b", "enfant": 0},
                          {"op": "traduire", "langue": "fr"},
                          {"op": "memorise", "sel": "#a"}, {"op": "memorise", "sel": "#c"},
                          {"op": "memorise", "sel": "#b", "enfant": 0}], DICO)
    assert r[1:4] == [True, True, True], "rien n'est mémorisé en anglais : %s" % r[1:4]
    assert r[5:8] == [False, False, False], "la mémoire n'est pas vidée : %s" % r[5:8]


def test_ce_que_le_JavaScript_a_reecrit_apres_la_traduction_n_est_pas_ecrase():
    """LE JAVASCRIPT PEINT PAR-DESSUS. Un compteur rafraîchi après la bascule
    porte une valeur plus récente que l'original mémorisé : la restitution
    ne remet l'original que si le nœud porte ENCORE sa traduction."""
    r = _jouer('<p id="t">Bonjour</p>',
               [{"op": "traduire", "langue": "en"}, {"op": "texte", "sel": "#t"},
                {"op": "setTexte", "sel": "#t", "enfant": 0, "valeur": "Nouveau texte"},
                {"op": "traduire", "langue": "fr"}, {"op": "texte", "sel": "#t"}], DICO)
    assert r[1] == "Hello"
    assert r[4] == "Nouveau texte", r[4]


# ══════════════════════════════════════════════════════════════════════════
#  6. PAS DE BOUCLE, ET CE QUI ARRIVE APRÈS COUP EST TRADUIT
# ══════════════════════════════════════════════════════════════════════════

CHAINE = {"texte": {"Un": "Deux", "Deux": "Trois"}, "bloc": {}}


def test_un_noeud_deja_traduit_est_SAUTE_meme_si_sa_traduction_est_une_cle():
    """L'OBSERVATEUR REPASSE SUR CE QU'IL A ÉCRIT. Si « Deux » est aussi une
    clé, une seconde passe naïve écrirait « Trois », puis la suivante autre
    chose : un nœud dont la valeur courante est sa traduction est sauté, et
    la seconde passe n'écrit RIEN."""
    r = _jouer('<p id="t">Un</p>',
               [{"op": "traduire", "langue": "en"}, {"op": "traduire", "langue": "en"},
                {"op": "texte", "sel": "#t"}], CHAINE)
    assert r[0] == 1 and r[1] == 0, "écritures par passe : %s" % r[:2]
    assert r[2] == "Deux", r[2]


def test_un_noeud_insere_apres_coup_est_traduit_depuis_sa_racine():
    """CE QUE LE JAVASCRIPT REND APRÈS LA BASCULE passe par le même chemin,
    depuis le sous-arbre touché : l'observateur de sentinel.page.js appelle
    sentTraduireCorps sur la cible de la mutation."""
    r = _jouer('<div id="z"><p id="t">Un</p></div>',
               [{"op": "traduire", "langue": "en"},
                {"op": "append", "sel": "#z", "html": '<p id="n">Un</p>'},
                {"op": "traduire", "sel": "#n", "langue": "en"},
                {"op": "texte", "sel": "#n"}, {"op": "texte", "sel": "#t"}], CHAINE)
    assert r[3] == "Deux", r[3]
    assert r[4] == "Deux", "le premier nœud a été retraduit : %r" % r[4]


def test_un_noeud_reecrit_en_francais_par_le_JavaScript_est_retraduit():
    """Un rendu qui réécrit un texte déjà traduit avec une NOUVELLE valeur
    française est traduit à son tour — la mémoire suit la valeur courante."""
    r = _jouer('<p id="t">Un</p>',
               [{"op": "traduire", "langue": "en"},
                {"op": "setTexte", "sel": "#t", "enfant": 0, "valeur": "Un"},
                {"op": "traduire", "sel": "#t", "langue": "en"}, {"op": "texte", "sel": "#t"},
                {"op": "traduire", "langue": "fr"}, {"op": "texte", "sel": "#t"}], CHAINE)
    assert r[3] == "Deux", r[3]
    assert r[5] == "Un", r[5]


# ══════════════════════════════════════════════════════════════════════════
#  7. L'INVENTAIRE APPLIQUE EXACTEMENT LES RÈGLES DE LA TRADUCTION
# ══════════════════════════════════════════════════════════════════════════

def test_l_inventaire_releve_les_trois_regimes_et_la_page():
    inv = _jouer(FRAGMENT, [{"op": "inventaire"}])[0]
    assert inv["bloc"]["Bonjour le monde !"] == {
        "fr": "Bonjour le monde !", "html": "Bonjour <b>le monde</b> !", "pages": ["x"]}, inv["bloc"]
    assert inv["texte"]["Toutes (#)"] == "Toutes (15)", inv["texte"]
    assert inv["texte"]["Voir le"] == "Voir le" and inv["texte"]["Rapport"] == "Rapport"
    assert inv["attr"] == {"Fermer la fenêtre": "Fermer la fenêtre", "Bonjour": "Bonjour",
                           "Envoyer": "Envoyer"}, inv["attr"]
    #  CE QUI EST EXCLU N'EST PAS RELEVÉ NON PLUS : le traduire serait du
    #  travail perdu, puisque la traduction ne l'atteint pas.
    assert "Bonjour le monde !" not in inv["texte"]
    assert list(inv["bloc"]) == ["Bonjour le monde !"]


def test_TOUT_ce_que_l_inventaire_releve_la_traduction_l_atteint_et_rien_d_autre():
    """LA PREUVE QUE LES DEUX SUIVENT LES MÊMES RÈGLES : un dictionnaire
    fabriqué depuis l'inventaire (« EN » + clé) traduit CHAQUE entrée
    relevée — et l'inventaire d'après ne voit plus que de l'anglais."""
    inv = _jouer(FRAGMENT, [{"op": "inventaire"}])[0]
    #  LE BLOC ANGLAIS GARDE LES BALISES DU FRANÇAIS (c'est la règle du
    #  régime), avec ses chiffres remplacés par « # » comme dans une clé.
    dico = {"texte": {k: "EN " + k for k in list(inv["texte"]) + list(inv["attr"])},
            "bloc": {k: "EN " + re.sub(r"[0-9]+(?:[.,][0-9]+)*", "#", v["html"])
                     for k, v in inv["bloc"].items()}}
    apres = _jouer(FRAGMENT, [{"op": "traduire", "langue": "en"}, {"op": "inventaire"}], dico)[1]
    for regime in ("texte", "bloc", "attr"):
        restes = [k for k in apres[regime] if not k.startswith("EN ")]
        assert not restes, "%s relevé(s) mais non traduit(s) : %s" % (regime, restes)
    assert len(apres["texte"]) == len(inv["texte"]) and len(apres["bloc"]) == len(inv["bloc"])


# ══════════════════════════════════════════════════════════════════════════
#  8. CE QUE LE CODE DU MODULE N'A PAS LE DROIT DE FAIRE
# ══════════════════════════════════════════════════════════════════════════

def _fonctions(code):
    """{nom: corps} des fonctions de premier niveau du module."""
    out = {}
    for m in re.finditer(r"(?m)^function (\w+)\s*\([^)]*\)\s*\{", code):
        i, prof = m.end(), 1
        while i < len(code) and prof:
            prof += {"{": 1, "}": -1}.get(code[i], 0)
            i += 1
        out[m.group(1)] = code[m.start():i]
    return out


def test_innerHTML_ne_s_ecrit_QUE_dans_le_regime_bloc():
    """LA DIFFÉRENCE QUI SÉPARE CE MOTEUR DE CELUI DE L'ACCUEIL, et la raison
    des deux régimes. Écrire innerHTML efface tout ce qui portait un
    comportement ; ce geste n'est permis que sur un élément que sentToutInline
    a reconnu comme de la mise en forme nue, dans deux fonctions nommées."""
    fns = _fonctions(CODE_MODULE)
    assert {"sentBlocAppliquer", "sentBlocRestituer", "sentTexteAppliquer",
            "sentAttrsAppliquer"} <= set(fns), sorted(fns)
    ecrivent = sorted(n for n, c in fns.items() if re.search(r"\.innerHTML\s*=[^=]", c))
    assert ecrivent == ["sentBlocAppliquer", "sentBlocRestituer"], (
        "innerHTML s'écrit hors du régime bloc, dans : %s — tout lien, bouton ou "
        "identifiant sous l'élément traduit sera effacé sans erreur" % ecrivent)
    for n in ("sentTexteAppliquer", "sentAttrsAppliquer", "sentMarcher"):
        assert "innerHTML" not in fns[n], "%s touche innerHTML" % n
    assert "nodeValue = " in fns["sentTexteAppliquer"], "le régime texte n'écrit plus nodeValue"


def test_le_module_reste_en_ES5_et_s_exporte_pour_node():
    """LE RESTE DE SENTINEL EST EN `var`/`function`, et le module est lu par
    des navigateurs qu'on ne choisit pas. Et il s'exporte : les règles et
    l'outil d'inventaire exécutent CE fichier, pas une copie."""
    for motif in (r"\blet\s", r"\bconst\s", r"=>", r"\bclass\s", "`"):
        assert not re.search(motif, CODE_MODULE), "syntaxe hors ES5 : %s" % motif
    assert "module.exports = {" in CODE_MODULE
    for nom in ("sentNormaliser", "SENT_INLINE", "sentClasser", "sentInventaire",
                "sentTraduireCorps", "sentDigits"):
        assert re.search(r"\b%s: %s\b" % (nom, nom), CODE_MODULE), "%s n'est pas exporté" % nom
    assert "if (typeof module !== 'undefined'" in CODE_MODULE


def test_la_liste_blanche_du_bloc_est_celle_de_la_conception():
    i = CODE_MODULE.index("var SENT_INLINE = [")
    liste = set(re.findall(r"'([a-z]+)'", CODE_MODULE[i:CODE_MODULE.index("];", i)]))
    assert liste == {"b", "strong", "i", "em", "u", "s", "sup", "sub", "small", "mark",
                     "code", "kbd", "abbr", "br", "wbr", "span"}, sorted(liste)


# ══════════════════════════════════════════════════════════════════════════
#  9. LE BRANCHEMENT DANS sentinel.page.js — exécuté
# ══════════════════════════════════════════════════════════════════════════

def _bloc_corps():
    i = PAGE_JS.index("/* ══ LE CORPS DES PAGES, TRADUIT PAR CONTENU")
    return PAGE_JS[i:PAGE_JS.index("window.sentSetLang = function", i)]


#  LE VRAI MODULE PASSE DEVANT : la mécanique (téléchargement, observateur,
#  passe différée) vit dans sentinel.i18n.js (sentBrancher), partagée avec les
#  pages embarquées en cadre ; sentinel.page.js la branche sur SON document.
#  Le prélude redéclare sentTraduireCorps APRÈS le module : dans un même
#  script, la dernière déclaration gagne, et sentBrancher appelle le témoin.
_PRELUDE = r"""
var opts = JSON.parse(process.argv[2]);
var SENT_LANG = opts.lang;
var appels = [], observateurs = [], images = [], fetchs = 0;
function sentTraduireCorps(r, d, l) { appels.push([r.id || '?', !!d, l]); return 0; }
function MutationObserver(cb) {
  this.cb = cb; this.deconnecte = false; this.pris = 0;
  this.observe = function (t, o) { this.cible = t.id; this.options = o; observateurs.push(this); };
  this.disconnect = function () { this.deconnecte = true; };
  this.takeRecords = function () { this.pris++; return []; };
}
function requestAnimationFrame(fn) { images.push(fn); }
var body = { id: 'body', nodeType: 1, contains: function () { return true; } };
var document = { body: body };
function fetch() {
  fetchs++;
  if (opts.fetch === 'ok') return Promise.resolve({ ok: true, json: function () { return Promise.resolve(opts.dico); } });
  if (opts.fetch === '500') return Promise.resolve({ ok: false, status: 500 });
  return Promise.reject(new Error('reseau'));
}
"""

_EPILOGUE = r"""
(async function () {
  var faits = {};
  if (opts.scenario === 'observateur') {
    sentCorpsBranche().dico = opts.dico;
    sentCorpsAppliquer();
    faits.premierAppel = appels[0];
    faits.options = observateurs.length === 1 ? observateurs[0].options : null;
    faits.cible = observateurs.length === 1 ? observateurs[0].cible : null;
    var texte = { nodeType: 3, parentNode: { id: 'parent', nodeType: 1, contains: function () { return false; } } };
    observateurs[0].cb([{ target: { id: 'nouveau', nodeType: 1, contains: function () { return false; } } },
                        { target: texte }]);
    observateurs[0].cb([{ target: { id: 'autre', nodeType: 1, contains: function () { return false; } } }]);
    faits.imagesProgrammees = images.length;
    images[0]();
    faits.apresMutation = appels.slice(1);
    faits.recordsPris = observateurs[0].pris;
    SENT_LANG = 'fr';
    sentCorpsAppliquer();
    faits.deconnecte = observateurs[0].deconnecte;
    faits.obsNul = sentCorpsBranche().obs === null;
    faits.dernierAppel = appels[appels.length - 1];
    var avant = appels.length;
    observateurs[0].cb([{ target: { id: 'tard', nodeType: 1, contains: function () { return false; } } }]);
    images.slice(1).forEach(function (f) { f(); });
    faits.appelsApresArret = appels.length - avant;
  } else {
    sentCorpsAppliquer();
    sentCorpsAppliquer();
    faits.fetchsSync = fetchs;
    faits.appelsSync = appels.length;
    if (opts.basculeAvantReponse) SENT_LANG = 'fr';
    await new Promise(function (r) { setTimeout(r, 5); });
    faits.appels = appels.slice();
    faits.corps = sentCorpsBranche().dico;
    faits.attenteNulle = sentCorpsBranche().attente === null;
    faits.observateurs = observateurs.length;
    sentCorpsAppliquer();
    await new Promise(function (r) { setTimeout(r, 5); });
    faits.fetchsApresRelance = fetchs;
    faits.appelsApresRelance = appels.slice(faits.appels.length);
  }
  process.stdout.write(JSON.stringify(faits));
})().catch(function (e) { process.stdout.write(JSON.stringify({ erreur: String(e && e.stack || e) })); });
"""


@functools.lru_cache(maxsize=None)
def _page(opts_json):
    if not NODE:
        pytest.skip("node absent")
    with tempfile.TemporaryDirectory() as d:
        h = os.path.join(d, "h.js")
        io.open(h, "w", encoding="utf-8").write(SRC_MODULE + _PRELUDE + _bloc_corps() + _EPILOGUE)
        r = subprocess.run([NODE, h, opts_json], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail("le bloc de sentinel.page.js n'a pas tourné :\n%s" % (r.stderr or "")[-2500:])
    out = json.loads(r.stdout)
    assert "erreur" not in out, out.get("erreur", "")[:800]
    return out


def _faits(**opts):
    return _page(json.dumps(dict({"lang": "en", "fetch": "ok", "dico": {"texte": {"a": "b"}, "bloc": {}},
                                  "scenario": "chargement"}, **opts), sort_keys=True))


def test_sentAppliquer_appelle_le_corps_APRES_la_coquille():
    """LE CORPS SUIT LA COQUILLE, dans la même fonction, après les deux
    boucles data-i18n : les éléments marqués sont déjà écrits quand le corps
    les rencontre — et il les saute."""
    i = PAGE_JS.index("function sentAppliquer()")
    corps = PAGE_JS[i:PAGE_JS.index("\n}", i)]
    assert "sentCorpsAppliquer()" in corps, "sentAppliquer n'appelle plus le corps"
    assert corps.index("[data-i18n-bloc]") < corps.index("sentCorpsAppliquer()")


def test_l_observateur_est_demarre_en_anglais_avec_les_trois_types_de_mutation():
    """childList pour ce qu'un rendu insère, subtree parce que ça arrive
    n'importe où, characterData pour un compteur réécrit sur place. En
    manquer un, c'est une famille de rendus qui reste en français."""
    f = _faits(scenario="observateur")
    assert f["premierAppel"] == ["body", True, "en"], f["premierAppel"]
    assert f["cible"] == "body"
    assert f["options"] == {"childList": True, "subtree": True, "characterData": True}, f["options"]


def test_une_mutation_est_traduite_a_l_image_suivante_sur_sa_cible_et_les_records_sont_repris():
    """UNE PASSE PAR IMAGE, sur les sous-arbres touchés seulement, et
    takeRecords après : nos propres écritures ne sont pas des mutations à
    retraduire — c'est ce qui empêche la boucle."""
    f = _faits(scenario="observateur")
    assert f["imagesProgrammees"] == 1, "deux lots de mutations → %d passe(s)" % f["imagesProgrammees"]
    assert f["apresMutation"] == [["nouveau", True, "en"], ["parent", True, "en"], ["autre", True, "en"]], f["apresMutation"]
    assert f["recordsPris"] == 1, "takeRecords non appelé après la passe"


def test_l_observateur_est_ARRETE_au_retour_en_francais_et_le_corps_restitue():
    f = _faits(scenario="observateur")
    assert f["deconnecte"] is True, "l'observateur tourne encore en français"
    assert f["obsNul"] is True
    assert f["dernierAppel"] == ["body", False, "fr"], f["dernierAppel"]
    assert f["appelsApresArret"] == 0, "une mutation tardive a encore traduit en français"


def test_le_dictionnaire_est_telecharge_UNE_fois_puis_applique():
    """PARESSEUX : rien avant la première demande d'anglais, un seul fetch
    même si l'anglais est demandé deux fois pendant le téléchargement."""
    f = _faits()
    assert f["fetchsSync"] == 1, "%d fetch pour deux demandes" % f["fetchsSync"]
    assert f["appelsSync"] == 0, "le corps a été appliqué sans dictionnaire"
    #  UNE SEULE APPLICATION à l'arrivée, même demandée deux fois pendant le
    #  téléchargement : parcourir 4 300 éléments deux fois pour le même
    #  résultat est du travail perdu.
    assert f["appels"] == [["body", True, "en"]], f["appels"]
    assert f["corps"] == {"texte": {"a": "b"}, "bloc": {}, "motif": {}}, f["corps"]
    assert f["observateurs"] == 1
    assert f["fetchsApresRelance"] == 1, "le dictionnaire a été retéléchargé"
    assert f["appelsApresRelance"] == [["body", True, "en"]], "une demande explicite n'applique plus"


@pytest.mark.parametrize("panne", ["500", "reseau"])
def test_un_dictionnaire_injoignable_ne_casse_rien_et_se_redemande(panne):
    """LA COQUILLE RESTE TRADUITE, le corps reste en français, aucune
    exception — et la prochaine demande d'anglais réessaie : une panne
    réseau n'est pas définitive."""
    f = _faits(fetch=panne)
    assert f["appels"] == [], "le corps a été appliqué sans dictionnaire : %s" % f["appels"]
    assert f["corps"] is None and f["attenteNulle"] is True
    assert f["observateurs"] == 0
    assert f["fetchsApresRelance"] == 2, "pas de nouvel essai après la panne"


def test_un_retour_en_francais_pendant_le_telechargement_n_ecrit_pas_d_anglais():
    f = _faits(basculeAvantReponse=True)
    assert [a for a in f["appels"] if a[2] == "en"] == [], f["appels"]


def test_le_code_de_page_ne_telecharge_le_dictionnaire_qu_a_un_seul_endroit():
    """UN SEUL TÉLÉCHARGEMENT, DANS LE MODULE : sentinel.page.js et les
    cadres passent par sentBrancher ; une seconde copie du fetch dans la page
    serait une seconde mécanique à tenir d'accord avec la première."""
    code = _code(PAGE_JS)
    assert "sentinel.en.json'" not in code, "sentinel.page.js télécharge encore le dictionnaire lui-même"
    assert "sentBrancher(document" in _bloc_corps()
    assert CODE_MODULE.count("fetch(") == 1, CODE_MODULE.count("fetch(")
    assert "var SENT_DICO_URL = '/sentinel.en.json';" in CODE_MODULE
    assert "credentials: 'same-origin'" in CODE_MODULE


# ══════════════════════════════════════════════════════════════════════════
#  10. sentinel.html — l'ordre des scripts
# ══════════════════════════════════════════════════════════════════════════

def test_le_module_est_charge_AVANT_sentinel_page_js_et_en_differe():
    """sentinel.page.js appelle sentTraduireCorps dès son chargement si la
    langue mémorisée est l'anglais : le module doit être là avant. Deux
    scripts `defer` s'exécutent dans l'ordre du document."""
    i = SENTINEL.find('<script src="/sentinel.i18n.js" defer></script>')
    j = SENTINEL.find('<script src="/sentinel.page.js" defer></script>')
    assert i >= 0, "sentinel.i18n.js n'est pas chargé par sentinel.html"
    assert j >= 0
    assert i < j, "sentinel.i18n.js est chargé APRÈS sentinel.page.js"
    assert SENTINEL.count("sentinel.i18n.js") == 1


def test_sentinel_html_n_est_pas_marque_element_par_element():
    """LA CONCEPTION : le corps se traduit par contenu. Aucune nouvelle
    marque data-i18n n'a été semée dans le corps pour ce lot — les 213 clés
    de la coquille restent la seule chose que le HTML porte."""
    assert SENTINEL.count("data-i18n=") <= 130, SENTINEL.count("data-i18n=")
    assert SENTINEL.count("data-i18n-bloc=") <= 100


# ══════════════════════════════════════════════════════════════════════════
#  11. LA ROUTE /sentinel.en.json
# ══════════════════════════════════════════════════════════════════════════

NAVIGATEUR = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Firefox/130.0',
              'Accept-Language': 'fr', 'Accept-Encoding': 'identity'}


@pytest.fixture
def dossier(tmp_path, monkeypatch):
    """Un dossier de dictionnaires d'essai, vu par le module ET par la
    route — le cache du module est vidé pour ne pas servir le vrai."""
    d = tmp_path / "i18n"
    d.mkdir()
    monkeypatch.setattr(sentinel_i18n, "DOSSIER", str(d))
    sentinel_i18n._CACHE.clear()
    yield d
    sentinel_i18n._CACHE.clear()


def _ecrire(d, nom, contenu):
    (d / nom).write_text(json.dumps(contenu, ensure_ascii=False), encoding="utf-8")


def _client():
    import app as A
    return A.app.test_client()


def _get(chemin="/sentinel.en.json", **h):
    e = dict(NAVIGATEUR)
    e.update(h)
    return _client().get(chemin, headers=e)


def test_la_route_est_inseree_juste_apres_donnees_structurees():
    i = APP_PY.index("@app.route('/donnees-structurees.json')")
    j = APP_PY.index("@app.route('/sentinel.en.json')")
    assert i < j
    entre = APP_PY[i:j]
    assert entre.count("@app.route(") == 1, "d'autres routes se sont glissées entre les deux"
    assert APP_PY.count("/sentinel.en.json'") == 1


def test_la_route_fusionne_deux_fichiers(dossier):
    _ecrire(dossier, "a.json", {"_lot": "a", "texte": {"Un": "One"}, "bloc": {"Un <b>x</b>": "One <b>x</b>"}})
    _ecrire(dossier, "b.json", {"_lot": "b", "texte": {"Deux": "Two"}})
    r = _get()
    assert r.status_code == 200 and r.mimetype == "application/json", (r.status_code, r.mimetype)
    d = r.get_json()
    assert d == {"texte": {"Un": "One", "Deux": "Two"}, "bloc": {"Un <b>x</b>": "One <b>x</b>"}}, d
    assert "_lot" not in json.dumps(d)


def test_un_conflit_est_JOURNALISE_et_la_premiere_valeur_gagne(dossier, caplog):
    """DEUX TRADUCTIONS POUR LA MÊME CLÉ ne doivent pas se remplacer au
    hasard d'un ordre de lecture : la première (ordre des fichiers) gagne,
    et le journal nomme le fichier, le régime et la clé."""
    _ecrire(dossier, "a.json", {"texte": {"Un": "One"}})
    _ecrire(dossier, "b.json", {"texte": {"Un": "Uno", "Deux": "Two"}})
    _ecrire(dossier, "c.json", {"texte": {"Deux": "Two"}})  # identique : pas un conflit
    with caplog.at_level(logging.ERROR):
        d = _get().get_json()
    assert d["texte"] == {"Un": "One", "Deux": "Two"}, d
    conflits = [m for m in caplog.messages if "SENTINEL_I18N_CONFLIT" in m]
    assert len(conflits) == 1, caplog.messages
    assert "b.json" in conflits[0] and "Un" in conflits[0] and "a.json" in conflits[0], conflits[0]


def test_la_route_porte_Cache_Control_public_une_heure_et_un_ETag(dossier):
    _ecrire(dossier, "a.json", {"texte": {"Un": "One"}})
    r = _get()
    assert r.headers.get("Cache-Control") == "public, max-age=3600", r.headers.get("Cache-Control")
    etag = r.headers.get("ETag")
    assert etag and etag.startswith('"'), etag
    r2 = _get(**{"If-None-Match": etag})
    assert r2.status_code == 304, r2.status_code
    assert r2.headers.get("ETag") == etag
    assert not r2.data


def test_un_dossier_vide_ou_absent_rend_un_dictionnaire_VIDE_et_pas_une_erreur(dossier):
    """LE NAVIGATEUR QUI REÇOIT {} garde la coquille traduite et le corps en
    français — l'état d'avant ce module. Un 404 ou un 500 serait une erreur
    console à chaque bascule, pour un dossier qu'on n'a pas encore rempli."""
    r = _get()
    assert r.status_code == 200 and r.get_json() == {"texte": {}, "bloc": {}}, (r.status_code, r.data[:80])
    shutil.rmtree(str(dossier))
    sentinel_i18n._CACHE.clear()
    r = _get()
    assert r.status_code == 200 and r.get_json() == {"texte": {}, "bloc": {}}, (r.status_code, r.data[:80])


def test_un_fichier_modifie_est_RELU_et_l_ETag_change(dossier):
    _ecrire(dossier, "a.json", {"texte": {"Un": "One"}})
    r1 = _get()
    _ecrire(dossier, "a.json", {"texte": {"Un": "One", "Deux": "Two"}})
    r2 = _get()
    assert r2.get_json()["texte"] == {"Un": "One", "Deux": "Two"}, r2.get_json()
    assert r1.headers["ETag"] != r2.headers["ETag"]


def test_un_fichier_illisible_est_nomme_et_les_autres_sont_servis(dossier, caplog):
    _ecrire(dossier, "a.json", {"texte": {"Un": "One"}})
    (dossier / "b.json").write_text("{pas du json", encoding="utf-8")
    with caplog.at_level(logging.ERROR):
        r = _get()
    assert r.status_code == 200 and r.get_json()["texte"] == {"Un": "One"}
    assert any("b.json" in m and "illisible" in m for m in caplog.messages), caplog.messages


# ══════════════════════════════════════════════════════════════════════════
#  12. LE DICTIONNAIRE D'EXEMPLE — la mécanique se voit de bout en bout
# ══════════════════════════════════════════════════════════════════════════

def _texte_de_sentinel():
    """Le texte visible de sentinel.html, normalisé comme le navigateur le
    ferait : balises retirées, entités décodées, blancs réduits."""
    corps = re.sub(r"<(script|style)\b.*?</\1>", " ", SENTINEL, flags=re.S | re.I)
    corps = re.sub(r"<!--.*?-->", " ", corps, flags=re.S)
    #  LES ATTRIBUTS LUS SONT DU TEXTE AUSSI : un `title` ou un `placeholder`
    #  est traduit (SENT_ATTRIBUTS) et les lots en portent. Retirer les balises
    #  les effaçait, et une clé prise d'un `title` passait pour inventée.
    attrs = " \n ".join(m.group(2) for m in re.finditer(
        r'\s(title|aria-label|placeholder|alt)="([^"]*)"', corps))
    return sentinel_i18n.normaliser(_html.unescape(re.sub(r"<[^>]+>", " \n ", corps) + " \n " + attrs))


def test_le_dossier_reel_se_fusionne_sans_faute_et_chaque_cle_est_sa_propre_normalisation():
    """UNE CLÉ QUI N'EST PAS DÉJÀ NORMALISÉE ne sera jamais cherchée : le
    navigateur normalise le texte de la page, pas les clés. Et chaque valeur
    porte autant de « # » que sa clé, sinon les chiffres ne reviennent pas."""
    dico, fautes = sentinel_i18n.fusionner()
    assert not fautes, fautes
    assert dico["texte"] and dico["bloc"], "le dossier d'exemple est vide"
    for regime in ("texte", "bloc"):
        for cle, val in dico[regime].items():
            assert sentinel_i18n.normaliser(cle) == cle, "%s : clé non normalisée %r" % (regime, cle[:60])
            assert cle.count("#") == val.count("#"), "%s : « # » différents entre %r et %r" % (regime, cle[:40], val[:40])
    for cle in dico["bloc"]:
        assert not re.search(r"<\w+\s", dico["bloc"][cle]), "un bloc anglais porte un attribut"


def test_les_entrees_de_l_exemple_prises_dans_le_HTML_s_y_trouvent_bien():
    """Le dictionnaire d'exemple ne vaut que s'il vise du VRAI texte de
    Sentinel : une clé que la page ne contient pas ne prouve rien.

    L'EXEMPLE SEUL, PAS LE DOSSIER ENTIER. Les lots de traduction venus
    depuis relèvent aussi des textes RECOMPOSÉS à l'écran par une
    concaténation (« Aucune actualite » + « a analyser pour le moment. ») :
    ils sont vrais à l'écran et introuvables d'un seul tenant dans le code.
    Leur justesse se mesure au navigateur (recette_sentinel_langue.js), pas
    par une recherche de sous-chaîne — c'est l'exemple que cette règle garde."""
    with io.open(os.path.join(sentinel_i18n.DOSSIER, "_exemple.json"), encoding="utf-8") as f:
        ex = json.load(f)
    dico = {"texte": ex.get("texte") or {}, "bloc": ex.get("bloc") or {}}
    texte = _texte_de_sentinel()
    cles = list(dico["texte"]) + list(dico["bloc"])
    dans_html = [k for k in cles if k in texte]
    assert len(dans_html) >= 4, "trop peu de clés prises dans le HTML : %s" % dans_html
    #  LES AUTRES VISENT CE QUE LE JAVASCRIPT REND (les cartes de formation,
    #  peintes par go('training')) : leur texte est dans sentinel.page.js,
    #  qui écrit ses accents échappés (u00e9 derrière une barre oblique
    #  inverse) — la clé est cherchée sous cette forme, et coupée avant ses
    #  « # » et ses parenthèses, qui sont des chiffres et de la concaténation
    #  dans le code.
    for cle in cles:
        if cle in dans_html:
            continue
        morceau = json.dumps(re.split(r"[#(]", cle)[0].strip(), ensure_ascii=True)[1:-1]
        assert morceau and morceau in PAGE_JS, (
            "clé absente de sentinel.html ET de sentinel.page.js : %r" % cle[:80])


def test_la_recette_navigateur_est_dans_le_depot_et_lit_le_dictionnaire_d_exemple():
    r = _lire("recette_sentinel_langue_moteur.js")
    assert "_exemple.json" in r and "sentSetLang('en')" in r and "sentSetLang('fr')" in r
    assert "innerHTML" in r and "status: 500" in r, "la recette ne mesure plus la restitution ou la panne"
