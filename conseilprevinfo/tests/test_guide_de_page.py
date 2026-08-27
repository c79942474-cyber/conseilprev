"""LE GUIDE DE PAGE — installé partout, atteignable, et dans les deux langues.

CE QUI A DÉCLENCHÉ CE FICHIER. Les deux autres sites du cabinet ont leurs
guides ; celui-ci n'en avait aucun. C'est pourtant celui dont les conventions
sont les moins devinables : une fiche y sépare le FAIT de la LECTURE CRITIQUE,
distingue une lecture dérivée par règles d'une lecture signée, et affiche la
portée d'une incertitude. Rien de tout cela ne se déduit de la mise en page,
et un lecteur qui l'ignore lit le site de travers sans jamais s'en apercevoir.

TROIS PIÈGES CONNUS, REPRIS DES DEUX AUTRES SITES.

  · L'ANCRAGE PAR CLASSE. Sur conseilprevcyber le bouton s'ancrait sur
    `h1.page-h` ; vingt-cinq pages titraient autrement et leur guide, pourtant
    écrit, restait inatteignable — sans qu'aucune erreur ne le signale.

  · LA CLÉ RÉPÉTÉE. `GUIDES["/x"] = …` écrit deux fois écrase le premier guide
    en silence. Vingt-six guides de Sentinel avaient disparu ainsi.

  · LE GUIDE QUI NE SUIT PAS LA LANGUE. Le panneau est rendu en JavaScript :
    les attributs `data-i18n` du site ne l'atteignent pas. Un guide resté
    français sous une interface anglaise est précisément le reste qui fait
    douter de tout le reste — c'est ce que dit `langue.js` en tête, à propos
    de la date.

CE QUE CES CONTRÔLES NE PEUVENT PAS FAIRE. Juger qu'un guide décrit fidèlement
sa page : cela se vérifie en la lisant. Ni juger la qualité d'une traduction —
ils tiennent seulement qu'elle existe et qu'elle n'est pas une recopie.
"""
import io
import json
import os
import re
import subprocess

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lire(nom):
    return io.open(os.path.join(ICI, nom), encoding="utf-8").read()


JS = _lire("guide.js")
APP = _lire("app.py")

GABARITS = ["index.html", "revue.html", "confronter.html", "fiche.html",
            "abonnement.html", "confidentialite.html"]

CLES = re.findall(r'GUIDES\[\s*"([^"]+)"\s*\]\s*=', JS)


# ── LES PAGES SERVIES, D'APRÈS LES ROUTES ────────────────────────────────

def _pages():
    """Les routes qui servent un gabarit HTML. Relevées dans app.py, jamais
    recopiées : une liste écrite ici divergerait au premier ajout."""
    out = []
    for bloc in re.split(r"(?=@app\.route)", APP):
        chemins = re.findall(r'@app\.route\(\s*"([^"]+)"', bloc)
        if not chemins:
            continue
        gabarit = re.search(r'send_from_directory\([^,]+,\s*"([\w.-]+\.html)"', bloc)
        if not gabarit:
            gabarit = re.search(r'"([\w.-]+\.html)"', bloc)
        if not gabarit:
            continue
        for c in chemins:
            if c.startswith("/api/"):
                continue
            out.append((c, gabarit.group(1)))
    return out


PAGES = _pages()


def test_le_relevé_des_pages_n_est_pas_vide():
    """Si la lecture des routes cessait de fonctionner, tous les contrôles de
    couverture passeraient sur une liste vide en se déclarant verts."""
    assert len(PAGES) >= 6, "seulement %d pages relevées : %s" % (len(PAGES), PAGES)
    assert len(CLES) >= 6, "seulement %d guides relevés" % len(CLES)


def test_aucune_clé_de_guide_répétée():
    vus, doubles = set(), []
    for c in CLES:
        (doubles.append(c) if c in vus else vus.add(c))
    assert not doubles, (
        "guides écrits deux fois — le second écrase le premier en silence : %s"
        % ", ".join(sorted(set(doubles))))


@pytest.mark.parametrize("gabarit", GABARITS)
def test_chaque_gabarit_charge_le_module(gabarit):
    """Sans le script, pas de bouton — et rien ne le signale : une page qui ne
    charge pas un script n'est pas une page en erreur."""
    assert "/guide.js" in _lire(gabarit), (
        "%s ne charge pas /guide.js : la page n'aura aucun bouton d'aide" % gabarit)


def test_le_relevé_des_gabarits_couvre_ceux_que_le_serveur_sert():
    """Le relevé ci-dessus est écrit ; celui des routes est lu. S'ils
    divergeaient, la couverture porterait sur des fichiers qui ne sont plus
    servis, et laisserait de côté ceux qui le sont."""
    servis = sorted({g for _, g in PAGES})
    manquants = [g for g in servis if g not in GABARITS]
    assert not manquants, (
        "gabarits servis mais hors du contrôle de couverture : %s"
        % ", ".join(manquants))


# ── L'ANCRAGE EST UNE PROPRIÉTÉ ──────────────────────────────────────────

def _corps_ancrage():
    i = JS.index("function poserBarre(")
    return JS[i:JS.index("\n  }", i)]


def test_l_ancrage_ne_dépend_d_aucune_classe():
    corps = _corps_ancrage()
    assert 'querySelector("h1")' in corps, "l'ancrage sur le premier titre a disparu"
    for sel in re.findall(r'querySelector\("([^"]+)"\)', corps):
        assert "." not in sel and "#" not in sel, (
            "l'ancrage repose sur un nom (%s) : toute page qui titre autrement "
            "perdra son bouton, en silence" % sel)


def test_une_page_sans_titre_garde_son_bouton():
    corps = _corps_ancrage()
    assert "flottante" in corps and "document.body.insertBefore" in corps, (
        "le repli flottant a disparu : une page sans titre perdrait son bouton")


# ── LE GUIDE SUIT LA LANGUE ──────────────────────────────────────────────

def test_le_panneau_se_redessine_à_la_bascule_de_langue():
    """`langue.js` émet l'évènement `langue` ; le panneau étant rendu en
    JavaScript, il ne se retraduit pas tout seul."""
    assert 'document.addEventListener("langue", redessiner)' in JS, (
        "le guide n'écoute plus la bascule : il resterait dans la langue où il "
        "a été rendu, sous une interface passée dans l'autre")
    assert 'dispatchEvent(new CustomEvent("langue"' in _lire("langue.js"), (
        "langue.js n'émet plus l'évènement écouté ici : le nom a changé, et le "
        "guide ne se retraduira plus")


def test_le_guide_suit_l_interface_et_non_les_analyses():
    """Deux réglages distincts, et `langue.js` explique pourquoi. Le guide est
    du texte du cabinet : il suit l'interface.

    La règle porte sur ce que le module APPELLE, non sur le mot « analyses » :
    un premier essai cherchait le mot dans le fichier, et se déclenchait sur
    une phrase de guide qui EXPLIQUE au lecteur que les deux réglages sont
    distincts. Une règle qui interdit de parler d'une chose n'est pas une
    règle sur le comportement."""
    assert "L.courante" in JS, "le guide ne lit plus la langue de l'interface"
    assert not re.search(r"\bL\.analyses\s*\(", JS), (
        "le guide lit la langue des ANALYSES : c'est un réglage distinct de "
        "celui de l'interface, et les confondre retraduirait l'aide au moment "
        "où le lecteur ne l'a pas demandé")
    assert not re.search(r'addEventListener\(\s*"analyses"', JS), (
        "le guide se redessine sur la bascule des analyses, qui ne le concerne "
        "pas")


def test_les_libellés_du_bouton_existent_dans_les_deux_langues():
    i = JS.index("var LIBELLES = {")
    bloc = JS[i:JS.index("\n  };", i)]
    paires = re.findall(r'\[\s*"([^"]*)",\s*"([^"]*)"\s*\]', bloc)
    assert len(paires) >= 6, "seulement %d libellés relevés" % len(paires)
    for fr, en in paires:
        assert fr and en, "libellé incomplet : %r / %r" % (fr, en)


# ── CE QUE LE GUIDE REND VRAIMENT ────────────────────────────────────────

def _rendu(chemins, langue):
    """La résolution TELLE QUE LE NAVIGATEUR L'EXÉCUTE. Chercher un nom dans le
    fichier ne prouverait rien : renommer le repli à sa déclaration laisse le
    nom présent à son point d'usage, et une règle textuelle passerait sur un
    script cassé."""
    d = JS.index("  var GUIDES = {};")
    f = JS.index("  function langue(")
    code = (JS[d:f]
            + "\nvar lg = " + json.dumps(langue) + ";\n"
            + "var out = {};\n"
            + json.dumps(chemins) + ".forEach(function(c){\n"
            + "  var g = guidePour(c) || DEFAUT;\n"
            + "  g = g[lg] || g.fr;\n"
            + "  out[c] = {t: g.t, p: g.p, s: g.s, k: g.k, l: g.l};\n"
            + "});\n"
            + "console.log(JSON.stringify(out));\n")
    r = subprocess.run(["node", "-e", code], capture_output=True, text=True)
    assert r.returncode == 0, "guide.js n'est plus évaluable : %s" % r.stderr[-500:]
    return json.loads(r.stdout)


CHEMINS = sorted({c for c, _ in PAGES if "<" not in c}) + ["/fiche/2026-08-01-exemple"]
FR = _rendu(CHEMINS + ["/adresse-inconnue"], "fr")
EN = _rendu(CHEMINS + ["/adresse-inconnue"], "en")
REPLI_FR = FR["/adresse-inconnue"]


def test_une_adresse_inconnue_reçoit_quand_même_un_guide():
    assert REPLI_FR["t"] and len(REPLI_FR["s"] or []) >= 2
    assert EN["/adresse-inconnue"]["t"] != REPLI_FR["t"], (
        "le repli n'existe pas en anglais : il retomberait en français")


@pytest.mark.parametrize("chemin", CHEMINS)
def test_aucune_page_ne_tombe_sur_le_repli(chemin):
    assert FR[chemin]["t"] != REPLI_FR["t"], (
        "%s rend le guide générique — « %s »" % (chemin, REPLI_FR["t"]))


def test_les_fiches_partagent_un_guide_plutôt_qu_un_guide_chacune():
    """Une fiche par identifiant : écrire un guide par fiche les condamnerait à
    diverger dès la première correction. Le repli sur préfixe doit donc
    fonctionner sur une adresse quelconque."""
    a = FR["/fiche/2026-08-01-exemple"]
    b = _rendu(["/fiche/2019-01-01-autre"], "fr")["/fiche/2019-01-01-autre"]
    assert a["t"] == b["t"] and a["t"] != REPLI_FR["t"], (
        "deux fiches n'obtiennent pas le même guide, ou aucune n'en obtient")


@pytest.mark.parametrize("chemin", CHEMINS)
def test_un_guide_situe_la_page_et_dit_quoi_en_faire(chemin):
    for langue, table in (("fr", FR), ("en", EN)):
        g = table[chemin]
        assert len(g["t"].strip()) >= 5, "%s (%s) : titre trop court" % (chemin, langue)
        assert len(g["p"].strip()) >= 80, (
            "%s (%s) : chapeau de %d caractères, trop court pour situer la page"
            % (chemin, langue, len(g["p"].strip())))
        assert len(g["s"] or []) >= 2, "%s (%s) : moins de deux étapes" % (chemin, langue)
        assert len(g["k"] or []) >= 1, (
            "%s (%s) : le guide ne dit nulle part ce que la page NE fait pas"
            % (chemin, langue))


@pytest.mark.parametrize("chemin", CHEMINS)
def test_l_anglais_n_est_pas_une_recopie_du_français(chemin):
    """La règle du site : chaque phrase anglaise est ÉCRITE. Une recopie
    signale une traduction oubliée, et c'est toujours la version la moins lue
    qui reste en arrière."""
    fr, en = FR[chemin], EN[chemin]
    assert fr["t"] != en["t"], "%s : titre identique dans les deux langues" % chemin
    assert fr["p"] != en["p"], "%s : chapeau non traduit" % chemin
    for i, (a, b) in enumerate(zip(fr["s"] or [], en["s"] or [])):
        assert a != b, "%s : étape %d non traduite" % (chemin, i + 1)


@pytest.mark.parametrize("chemin", CHEMINS)
def test_les_liens_d_un_guide_mènent_quelque_part(chemin):
    connues = {c for c, _ in PAGES if "<" not in c} | {"/fiche"}

    def nu(x):
        return x.split("#")[0].rstrip("/") or "/"

    for table in (FR, EN):
        morts = [x[1] for x in (table[chemin]["l"] or []) if nu(x[1]) not in connues]
        assert not morts, "%s : liens vers des pages inexistantes — %s" % (chemin, morts)
