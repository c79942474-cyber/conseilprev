# -*- coding: utf-8 -*-
"""UN LIBELLÉ COMPOSÉ DE PLUSIEURS ÉTIQUETTES SE TRADUIT — chacune la sienne.

LE DÉFAUT MESURÉ (mesure navigateur du 25 septembre 2026, page `matrice` :
7 828 mots français sur 7 851, part_fr 0,997 — 36 % de tout le français
resté à l'écran dans Sentinel). La carte « zone critique » écrivait

    <div class="eval-d">Haut risque · À évaluer · <span translate="no">…</span></div>

c'est-à-dire UN SEUL nœud texte « Haut risque · À évaluer · ». La clé de la
traduction étant le texte du nœud, il fallait une entrée de dictionnaire par
COMBINAISON : cinq classifications × quatre statuts, vingt clés, dont aucune
n'a jamais été relevée. Les deux étiquettes existaient pourtant, traduites,
depuis les lots 08 et 14 (« Haut risque » → « High risk », « À évaluer » →
« To be assessed ») : elles ne se retrouvaient simplement pas.

CE QUE CETTE RÈGLE MESURE, ET COMMENT. Elle ne lit pas le texte du code —
elle FAIT RENDRE la ligne par le code de sentinel.page.js lui-même
(tests/_matrice_zone_critique.js découpe la page, n'en recopie rien), puis
elle FAIT TRADUIRE le résultat par le vrai moteur (sentinel.i18n.js) avec le
VRAI dictionnaire du dépôt (i18n/sentinel/). Ce qui reste à l'écran est
ensuite classé par le VRAI classeur de la mesure navigateur
(outils/sentinel_langue.js) : la règle tombe si un mot français subsiste
ailleurs que dans une donnée saisie.

Elle est rouge sur le code d'avant : la clé composée n'est dans aucun
dictionnaire, et « Haut risque · À évaluer · » reste tel quel.
"""
import io
import json
import os
import shutil
import subprocess
import sys

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RACINE)

import sentinel_i18n  # noqa: E402

NODE = shutil.which("node")
RENDU = os.path.join(_RACINE, "tests", "_matrice_zone_critique.js")
PAGE_JS = os.path.join(_RACINE, "sentinel.page.js")
CLASSEUR = os.path.join(_RACINE, "outils", "sentinel_langue.js")
HARNAIS = os.path.join(_RACINE, "tests", "_dom_sentinel_corps.js")
MODULE = os.path.join(_RACINE, "sentinel.i18n.js")

#: LES DONNÉES SAISIES du jeu d'essai — noms de systèmes et secteurs. Elles
#: sont déclarées translate="no" par la page et n'ont pas à être traduites :
#: la règle les retire avant de classer ce qui reste.
DONNEES = ("Scoring credit automatise", "Chatbot service client",
           "Detection anomalies", "Prediction energetique",
           "Finance", "IT", "Industrie", "Energie")


def _node(args):
    if not NODE:
        pytest.skip("node absent")
    r = subprocess.run([NODE] + args, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, (r.stderr or "")[-2000:]
    return r.stdout


def _rendu():
    """Le HTML que matriceRender peint vraiment pour la zone critique."""
    return json.loads(_node([RENDU, PAGE_JS]))["html"]


def _traduire(html):
    """Le même HTML, passé au vrai moteur avec le vrai dictionnaire."""
    dico = sentinel_i18n.fusionner()[0]
    prog = {"html": html, "dico": dico,
            "ops": [{"op": "traduire", "langue": "en"}, {"op": "html"}]}
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "prog.json")
        io.open(p, "w", encoding="utf-8").write(
            json.dumps(prog, ensure_ascii=False, sort_keys=True))
        out = json.loads(_node([HARNAIS, MODULE, p]))
    assert not (isinstance(out[0], dict) and "erreur" in out[0]), out[0]
    return out[1]


def _classer(texte):
    prog = ("const L=require(%s);"
            "process.stdout.write(JSON.stringify(L.classer(%s)));"
            % (json.dumps(CLASSEUR), json.dumps(texte)))
    return json.loads(_node(["-e", prog]))


def _visible_hors_donnees(html):
    """Le texte lu à l'écran, une fois les données saisies retirées."""
    import re
    texte = re.sub(r"<[^>]+>", " ", html)
    for d in DONNEES:
        texte = texte.replace(d, " ")
    return re.sub(r"\s+", " ", texte).strip()


def test_la_zone_critique_de_la_matrice_ne_garde_aucun_mot_francais():
    """LA MESURE, DE BOUT EN BOUT : la page rend, le moteur traduit, le
    classeur de la mesure navigateur juge."""
    apres = _traduire(_rendu())
    reste = _visible_hors_donnees(apres)
    verdict = _classer(reste)
    assert verdict["langue"] != "fr", (
        "la ligne « zone critique » reste en français (%s mots) : %r"
        % (verdict["fr"], reste[:300]))
    assert verdict["fr"] == 0, (
        "%d mot(s) français à l'écran : %r" % (verdict["fr"], reste[:300]))


@pytest.mark.parametrize("francais,anglais", [
    ("Haut risque", "High risk"),
    ("Risque minimal", "Minimal risk"),
    ("À évaluer", "To be assessed"),
    ("En cours", "In progress"),
    ("Non conforme", "Not compliant"),
])
def test_chaque_etiquette_de_la_zone_critique_est_traduite_pour_elle_meme(francais, anglais):
    """CHACUNE SA CLÉ. C'est la promesse du découpage : une étiquette
    traduite ailleurs dans Sentinel l'est ici aussi, sans qu'une entrée de
    dictionnaire soit écrite pour chaque combinaison."""
    apres = _traduire(_rendu())
    assert anglais in apres, (
        "« %s » n'est pas devenu « %s » : %r" % (francais, anglais, apres[:400]))
    assert francais not in _visible_hors_donnees(apres), (
        "« %s » est resté à l'écran" % francais)


def test_les_donnees_saisies_de_la_ligne_restent_intactes():
    """CE QUI EST AU CLIENT NE SE TRADUIT PAS : le nom du système et son
    secteur passent entiers, et gardent leur déclaration."""
    apres = _traduire(_rendu())
    for d in ("Scoring credit automatise", "Finance"):
        assert d in apres, "la donnée %r a été touchée : %r" % (d, apres[:400])
    assert apres.count('translate="no"') >= 8, (
        "les données ne sont plus déclarées : %r" % apres[:400])
