# -*- coding: utf-8 -*-
"""LES DOCUMENTS EMBARQUÉS SE TRADUISENT AUSSI — mesuré sur leur texte propre.

LE DÉFAUT MESURÉ (mesure navigateur du 25 septembre 2026). Sentinel embarque
cinq documents en <iframe>. Depuis qu'ils chargent sentinel.i18n.js, ils se
traduisent par la même mécanique que Sentinel — et ils entrent dans le
verdict. Mais LEUR TEXTE PROPRE n'avait jamais été inventorié : le catalogue
portait quelques centaines d'entrées pour les vues qui les hébergent, aucune
pour le contenu du document lui-même. Mesuré, moteur et dictionnaire réels
sur `panorama.html` : 89 textes traduits, 247 encore français, dont les
QUARANTE blocs de méthode — l'avertissement de lecture, la note sur le coût
au mégawatt, la définition NeurIPS. Soit, à l'écran, 1 996 mots français sur
la vue « enveloppe », 1 954 sur « pan-sia », 656 sur « empreinte-parc » et
250 sur « obs-rd » : le cinquième de tout le français resté visible.

CE QUE CES RÈGLES MESURENT. Elles ne lisent pas les dictionnaires — elles
FONT TRADUIRE le document par le vrai moteur (sentinel.i18n.js) avec le VRAI
dictionnaire du dépôt (i18n/sentinel/), puis font juger ce qui reste par le
VRAI classeur de la mesure navigateur (outils/sentinel_langue.js).

CE QUI EST SORTI DU JUGEMENT, ET POURQUOI :
  · <script> et <style> — ce n'est pas du texte lu, et les commentaires du
    code y sont en français par choix ;
  · <option> — le moteur ne parcourt PAS les listes déroulantes
    (SENT_EXCLUS), parce qu'une option peut porter une donnée saisie. Les
    libellés d'option restent donc en français, c'est une limite CONNUE et
    nommée ici : 44 libellés, 124 mots, comptés dans la mesure navigateur ;
  · CE QUE LE DICTIONNAIRE A DÉLIBÉRÉMENT GARDÉ EN FRANÇAIS. Le crédit
    « Carto n°89, 2025 © Areion/Capri — « Recherche et développement dans le
    domaine de l'IA » » est le TITRE PUBLIÉ d'une source tierce : la licence
    ne permet pas d'en faire une œuvre dérivée, donc la traduction retenue
    reprend le titre tel quel et ajoute sa glose entre crochets. Un texte qui
    est EXACTEMENT une valeur du dictionnaire a été traduit — cette règle
    mesure ce qui ne l'a PAS été. Un refus « identique au français » n'entre
    jamais au dictionnaire : rien ne peut se cacher derrière cette porte.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RACINE)

import sentinel_i18n  # noqa: E402

NODE = shutil.which("node")
HARNAIS = os.path.join(_RACINE, "tests", "_dom_sentinel_corps.js")
MODULE = os.path.join(_RACINE, "sentinel.i18n.js")
CLASSEUR = os.path.join(_RACINE, "outils", "sentinel_langue.js")

#: LES DOCUMENTS QUE SENTINEL EMBARQUE, et la vue qui les héberge. `/map` est
#: une carte sans texte propre ; `panorama.html` sert TROIS vues (le document
#: choisit sa vue d'après l'adresse, voir app.py).
CADRES = [("panorama.html", "pan-sia · enveloppe · empreinte-parc"),
          ("observatoire.html", "obs-rd")]


def _node(args):
    if not NODE:
        pytest.skip("node absent")
    r = subprocess.run([NODE] + args, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, (r.stderr or "")[-2000:]
    return r.stdout


def _corps(nom):
    html = io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()
    m = re.search(r"<body[^>]*>(.*)</body>", html, re.S)
    return m.group(1) if m else html


def _traduire(html):
    dico = sentinel_i18n.fusionner()[0]
    prog = {"html": html, "dico": dico,
            "ops": [{"op": "traduire", "langue": "en"}, {"op": "html"}]}
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "prog.json")
        io.open(p, "w", encoding="utf-8").write(
            json.dumps(prog, ensure_ascii=False, sort_keys=True))
        out = json.loads(_node([HARNAIS, MODULE, p]))
    assert not (isinstance(out[0], dict) and "erreur" in out[0]), out[0]
    return out[0], out[1]


def _valeurs_du_dictionnaire():
    """Les traductions RETENUES, normalisées — ce que le dépôt a décidé."""
    #  SEULEMENT CE QUI A VRAIMENT CHANGÉ. Une valeur identique à sa clé
    #  n'est pas une décision, c'est une traduction absente : l'admettre
    #  ouvrirait une porte par laquelle n'importe quel défaut passerait
    #  (mesuré : la mutation « la valeur redevient le français » survivait).
    dico = sentinel_i18n.fusionner()[0]
    out = set()
    for regime in ("texte", "bloc", "motif"):
        for cle, v in (dico.get(regime) or {}).items():
            if not isinstance(v, str):
                continue
            nu = sentinel_i18n.normaliser(re.sub(r"<[^>]+>", " ", v))
            if nu != sentinel_i18n.normaliser(re.sub(r"<[^>]+>", " ", cle)):
                out.add(nu)
    return out


def _textes_lus(html):
    """Ce qu'un lecteur voit : sans le code, sans les listes déroulantes."""
    for balise in ("script", "style", "option"):
        html = re.sub(r"<%s\b.*?</%s>" % (balise, balise), " ", html, flags=re.S | re.I)
    return [t.strip() for t in re.split(r"<[^>]+>", html) if len(t.strip()) >= 12]


def _classer(textes):
    with tempfile.TemporaryDirectory() as d:
        q = os.path.join(d, "lot.json")
        io.open(q, "w", encoding="utf-8").write(json.dumps(textes, ensure_ascii=False))
        prog = ("const fs=require('fs');const L=require(%s);"
                "const t=JSON.parse(fs.readFileSync(%s,'utf8'));"
                "process.stdout.write(JSON.stringify(t.map(x=>L.classer(x))));"
                % (json.dumps(CLASSEUR), json.dumps(q)))
        return json.loads(_node(["-e", prog]))


@pytest.mark.parametrize("nom,vues", CADRES, ids=[c[0][:-5] for c in CADRES])
def test_le_document_embarque_ne_garde_aucun_texte_francais(nom, vues):
    """LA MESURE, DE BOUT EN BOUT : le vrai moteur, le vrai dictionnaire, le
    vrai classeur — sur le document que Sentinel embarque vraiment."""
    _, apres = _traduire(_corps(nom))
    textes = _textes_lus(apres)
    verdicts = _classer(textes)
    retenues = _valeurs_du_dictionnaire()
    restes = [(v["fr"], t) for t, v in zip(textes, verdicts)
              if v["langue"] == "fr" and sentinel_i18n.normaliser(t) not in retenues]
    restes.sort(reverse=True)
    assert not restes, (
        "%s (vues %s) : %d texte(s) encore en français, %d mots — le premier : %r"
        % (nom, vues, len(restes), sum(n for n, _ in restes), restes[0][1][:200]))


@pytest.mark.parametrize("nom,vues", CADRES, ids=[c[0][:-5] for c in CADRES])
def test_le_document_embarque_est_vraiment_traduit_et_pas_seulement_vide(nom, vues):
    """UNE PAGE VIDE PASSERAIT LA RÈGLE PRÉCÉDENTE. Celle-ci mesure le
    TRAVAIL : le moteur écrit des dizaines de textes, et l'anglais est
    majoritaire à l'écran."""
    ecrits, apres = _traduire(_corps(nom))
    assert ecrits >= 50, "%s : seulement %d écritures du moteur" % (nom, ecrits)
    verdicts = _classer(_textes_lus(apres))
    anglais = sum(1 for v in verdicts if v["langue"] == "en")
    assert anglais >= 20, "%s : %d textes anglais à l'écran" % (nom, anglais)


def test_les_blocs_de_methode_des_cadres_sont_tous_au_dictionnaire():
    """CE QUI MANQUAIT, NOMMÉ : le régime BLOC des documents embarqués. Un
    bloc est traduit d'un seul tenant, clé = le texte ENTIER de l'élément ;
    les lots écrits depuis les « restes » de la mesure, qui sont des NŒUDS,
    ne pouvaient pas les porter."""
    dico = sentinel_i18n.fusionner()[0]
    manquants = []
    for nom, _ in CADRES:
        prog = {"html": _corps(nom), "dico": {"texte": {}, "bloc": {}},
                "ops": [{"op": "inventaire"}]}
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "prog.json")
            io.open(p, "w", encoding="utf-8").write(
                json.dumps(prog, ensure_ascii=False, sort_keys=True))
            inv = json.loads(_node([HARNAIS, MODULE, p]))[0]
        for cle in (inv.get("bloc") or {}):
            if re.search(r"[A-Za-zÀ-ÿ]{3}", cle) and cle not in dico["bloc"]:
                manquants.append((nom, cle[:90]))
    assert not manquants, "%d bloc(s) sans traduction : %s" % (len(manquants), manquants[:3])
