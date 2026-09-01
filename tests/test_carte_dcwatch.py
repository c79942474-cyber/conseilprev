"""La carte publiée, rejouée sur la base que nous détenons.

CE QUI A DÉCLENCHÉ CE FICHIER. « Les Echos » a publié une carte des centres de
données français en citant Hubblo-DCWatch. Le référentiel recopiait « environ
trois cent cinquante » avec sa source — un nombre rond, exact peut-être, mais
invérifiable en l'état. Or la base DCWatch est DÉPOSÉE dans ce dépôt, sous
ODbL : la carte était donc vérifiable, et ne l'avait jamais été.

CE QUE CES RÈGLES PROTÈGENT, ET LES FAUTES QU'ELLES EMPÊCHENT :

  1. COMPARER SUR LE MAUVAIS TOTAL. « 350 » ne se retrouve pas en comptant les
     lignes françaises de la base — il y en a 427. C'est le compte des lignes
     EN EXPLOITATION. Sans cette règle écrite, l'écart de 77 lignes se lirait
     comme une lacune de la base, alors que ce sont des projets.

  2. ADDITIONNER DEUX STADES. Deux gigawatts tournent, sept sont annoncés,
     quinze sont réservés au réseau. Additionner deux de ces trois chiffres
     donne un total qui n'existe à aucune date.

  3. COMPTER UN DOUBLON POUR UN SITE. La base répète deux bâtiments OVH : le
     parc en exploitation ressort à 342 lignes pour 340 sites distincts. C'est
     l'écart exact que la vérification a fait sortir sur Roubaix — le seul des
     onze sites nommés qui ne concorde pas.

  4. RÉPARER LA BASE PLUTÔT QUE LA LECTURE. L'export échappe les apostrophes
     en « \\, », et « Provence-Alpes-Côte d\\,Azur » ressortait tel quel dans les
     ventilations servies. La réparation se fait à la LECTURE : le fichier porte
     une empreinte vérifiée, et le corriger le rendrait dérivé au sens de l'ODbL.

  5. FRANCHIR LA LIGNE DE L'ODbL. Concorder avec la carte ne justifie pas de
     verser ces estimations dans le référentiel servi : `capacite_mw` reste nul
     partout, et une puissance de bâtiment n'est pas une charge informatique.
"""
import os
import subprocess
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import datacentres as D  # noqa: E402
import dcwatch  # noqa: E402
import parc_fr as P  # noqa: E402

pytestmark = pytest.mark.skipif(not dcwatch.disponible(),
                                reason="base DCWatch non déposée")


def _fr():
    return dcwatch.agregats("France")


# ── 1. La règle de lecture de la carte ─────────────────────────────────────

def test_la_regle_de_lecture_est_ecrite_et_pas_seulement_connue():
    """Une règle de lecture qui vit dans la tête de celui qui l'a trouvée est
    perdue au premier rafraîchissement."""
    fr = D.COUVERTURE_NATIONALE["FR"]
    assert "lecture" in fr, "la règle de lecture de la carte n'est pas écrite"
    assert "EXPLOITATION" in fr["lecture"]
    assert fr.get("verifie_par"), "rien ne dit comment refaire la vérification"
    assert os.path.exists(os.path.join(ICI, fr["verifie_par"])), (
        "la recette nommée n'existe pas : une vérification qu'on ne peut pas "
        "relancer est une affirmation")


def test_le_compte_publie_se_retrouve_sur_les_sites_en_exploitation():
    """Et PAS sur le total des lignes. Les deux moitiés comptent : une règle
    qui vérifierait seulement la première resterait verte si la base doublait
    de taille en projets."""
    a = _fr()
    publie = D.COUVERTURE_NATIONALE["FR"]["recense"]
    exploitation = a["repartition_etat"]["operating"]
    assert abs(exploitation - publie) <= 10, (
        "le compte publié (%d) ne se retrouve plus sur les sites en "
        "exploitation (%d)" % (publie, exploitation))
    assert abs(a["sites"] - publie) > 25, (
        "le total des lignes (%d) est devenu comparable au compte publié : la "
        "règle de lecture ne distingue plus rien" % a["sites"])


# ── 2. Les trois stades, et l'addition impossible ──────────────────────────

def test_la_puissance_est_ventilee_par_stade():
    """Un total de mégawatts qui mêle l'exploitation et les projets ne décrit
    aucune date : ni aujourd'hui, ni demain."""
    a = _fr()
    mw = a["puissance_par_etat_mw"]
    assert "operating" in mw and "project" in mw, mw
    assert mw["project"] > mw["operating"], (
        "les projets ne pèsent plus davantage que l'exploitation : vérifier "
        "que la ventilation porte bien sur la base et non sur un sous-ensemble")
    assert abs(sum(mw.values()) - a["puissance_totale_mw"]) < 1.0, (
        "la ventilation ne se recompose pas en son total")


def test_le_rapprochement_vit_hors_du_referentiel_servi():
    """LA CONTRAINTE QUI A DÉPLACÉ CE CODE. `datacentres.py` ne doit pas
    importer DCWatch — le référentiel servi deviendrait une base dérivée. Le
    rapprochement vit donc dans un troisième module, qui est un travail
    produit ; et ce module ne descend jamais à la ligne."""
    import ast
    src = open(os.path.join(ICI, 'parc_fr.py'), encoding='utf-8').read()
    assert '_lire' not in src, (
        "parc_fr lit la base par site : ce que dcwatch s'interdit précisément "
        "de servir")
    appels = {n.func.attr for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
              and isinstance(n.func.value, ast.Name) and n.func.value.id == 'dcwatch'}
    assert appels <= {'agregats', 'disponible'}, (
        "parc_fr appelle autre chose que les agrégats de dcwatch : %s" % appels)


def test_les_echelles_sont_derivees_et_jamais_recopiees():
    e = P.echelles()
    assert e["disponible"] is True
    par_cle = {x["cle"]: x for x in e["echelles"]}
    assert set(par_cle) >= {"exploitation", "projets", "raccordement_reserve"}
    a = _fr()
    # Dérivé, donc égal au dixième de GW près à ce que rend l'agrégat.
    assert abs(par_cle["exploitation"]["valeur"]
               - a["puissance_par_etat_mw"]["operating"] / 1000.0) < 0.01
    assert par_cle["exploitation"]["sites"] == a["repartition_etat"]["operating"]
    for x in e["echelles"]:
        assert len(x.get("reserve") or "") > 50, (
            "%s : un ordre de grandeur sans réserve se lit comme une mesure" % x["cle"])
        assert x.get("source"), "%s : sans source" % x["cle"]
    assert "ODbL" in e["mention"], "la mention exigée par l'article 4.3 a disparu"


def test_les_echelles_se_taisent_quand_la_base_manque(monkeypatch):
    """Une absence de base ne doit pas produire des zéros : zéro gigawatt en
    exploitation serait un chiffre, et un chiffre faux."""
    monkeypatch.setattr(dcwatch, 'disponible', lambda: False)
    e = P.echelles()
    assert e["disponible"] is False
    assert "echelles" not in e
    assert len(e["pourquoi"]) > 40


# ── 3. Les doublons de la base ─────────────────────────────────────────────

def test_les_doublons_sont_comptes_et_rendus():
    """Les taire ferait passer un doublon pour un site — et c'est exactement
    l'écart que la carte a fait sortir sur Roubaix."""
    a = _fr()
    assert "doublons" in a, "l'agrégat ne dit plus si la base se répète"
    assert a["doublons"] >= 1, (
        "plus aucun doublon détecté : ou la base a été nettoyée, ou la "
        "détection ne détecte plus rien")


def test_le_compte_de_doublons_ne_rend_aucun_nom():
    """La ligne de l'ODbL : un COMPTE est un agrégat, une LISTE serait la base."""
    a = _fr()
    assert isinstance(a["doublons"], int)


def test_la_detection_de_doublons_discrimine():
    lignes = [{'name': 'A', 'city_name': 'X'}, {'name': 'B', 'city_name': 'X'}]
    assert dcwatch._doublons(lignes) == 0
    assert dcwatch._doublons(lignes + [{'name': 'A', 'city_name': 'X'}]) == 1
    # Même nom, autre commune : deux bâtiments, pas un doublon.
    assert dcwatch._doublons(lignes + [{'name': 'A', 'city_name': 'Y'}]) == 0


# ── 4. La base est réparée à la lecture, jamais dans le fichier ────────────

def test_l_apostrophe_echappee_est_reparee_a_la_lecture():
    regions = _fr()["repartition_region"]
    abimes = [r for r in regions if '\\' in r]
    assert not abimes, "libellé(s) encore abîmé(s) dans ce qui est servi : %s" % abimes
    assert any("Côte d'Azur" in r for r in regions), (
        "la réparation a emporté le libellé au lieu de le réparer")


def test_le_fichier_de_la_base_n_est_pas_modifie():
    """Le corriger le rendrait DÉRIVÉ au sens de l'ODbL, et invaliderait
    l'empreinte que porte ATTRIBUTION.md."""
    with open(dcwatch.FICHIER, encoding='utf-8') as f:
        brut = f.read()
    assert '\\,' in brut, (
        "le défaut a disparu du fichier source : la base a été modifiée au lieu "
        "d'être réparée à la lecture")


def test_la_reparation_ne_touche_que_l_echappement():
    assert dcwatch._reparer("Côte d\\,Azur") == "Côte d'Azur"
    assert dcwatch._reparer("Roubaix") == "Roubaix"
    assert dcwatch._reparer(None) is None


# ── 5. La ligne que la concordance ne justifie pas de franchir ─────────────

def test_concorder_avec_la_carte_n_ouvre_aucune_puissance_par_site():
    """LA RÈGLE DE FOND. La carte est en mégawatts, notre référentiel n'en
    porte aucun — et la concordance ne change rien : ces mégawatts sont
    estimés par mesure de BÂTIMENT sur imagerie satellite, pas mesurés en
    charge informatique."""
    for nom, lot in (("SITES", D.SITES), ("assemble()", D.assemble()["sites"])):
        avec = [s for s in lot if s.get("capacite_mw")]
        assert not avec, (
            "%d site(s) de %s portent une capacite_mw : la concordance avec la "
            "carte a servi de prétexte à lever l'interdit" % (len(avec), nom))


def test_la_recette_de_carte_passe_de_bout_en_bout():
    """Elle s'exécute vraiment. Une recette qu'on ne lance jamais est une
    intention, pas un contrôle."""
    r = subprocess.run([sys.executable, os.path.join(ICI, 'recette_carte_dcwatch.py')],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-800:]
    assert 'tout est vert' in r.stdout
    assert 'ODbL' in r.stdout, "la mention de provenance ne suit pas les chiffres produits"
