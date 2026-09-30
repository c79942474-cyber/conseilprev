# -*- coding: utf-8 -*-
"""Le pont Simulateur → Registre franchissable, et l'état du simulateur atteignable.

LE DÉFAUT MESURÉ. `SIM_DATA` et `simClassify` vivent dans une fonction anonyme
(le bloc du simulateur). Deux boutons situés PLUS LOIN dans le fichier les
nommaient directement : « Ajouter au Registre IA » et « Enregistrer dans
l'historique ». Hors de cette portée, `SIM_DATA` n'existe pas.

Mesuré au navigateur, simulateur REMPLI (nom, secteur, type, étape franchie) :

    typeof SIM_DATA (portée globale) → "undefined"
    window.SIM_DATA                  → "undefined"
    window.simAddToRegistre          → "function"
    clic sur « ajouter au registre » → « Aucune simulation a enregistrer.
                                         Completez d abord le simulateur. »

La garde `typeof SIM_DATA === "undefined"` était donc TOUJOURS vraie : le
pont entre deux modules de la cartographie ne pouvait pas être franchi, et
l'écran accusait l'utilisateur de ne pas avoir rempli ce qu'il venait de
remplir.

APRÈS, même parcours mesuré au navigateur :

    la porte rend  {"donnees":"Pont simulateur …","classe":"haut"}
    au clic        « Système ajouté au Registre IA. Voulez-vous l'ouvrir… »
    registre       5 systèmes → 6 · trouvé · classification « haut »
                   · secteur « Emploi / RH »

UNE PORTE, PAS UNE COPIE : `window.SIM_DATA = SIM_DATA` aurait figé la
référence, que `simReset` réaffecte au premier « Recommencer ».
"""
import io
import json
import os
import re
import shutil
import subprocess

import pytest

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = shutil.which("node")


def _lire(nom):
    with io.open(os.path.join(RACINE, nom), encoding="utf-8") as f:
        return f.read()


ECRAN = _lire("sentinel.page.js")


def _bloc(depuis, jusqu_a):
    i = ECRAN.index(depuis)
    return ECRAN[i:ECRAN.index(jusqu_a, i)]


# ── 1. L'ÉTAT DU SIMULATEUR A UNE PORTE, ET ELLE REND L'ÉTAT COURANT ─────

def test_le_simulateur_offre_une_porte_sur_son_etat_et_sur_sa_classification():
    assert "window.simDonnees = function()" in ECRAN, (
        "l'état du simulateur n'est atteignable par personne")
    assert "window.simClassifier = function()" in ECRAN, (
        "la classification du simulateur n'est atteignable par personne")


def test_la_porte_rend_l_etat_courant_et_pas_une_copie_figee():
    """`simReset` réaffecte l'objet : une copie posée une fois sur `window`
    aurait vieilli au premier « Recommencer », et le bouton aurait enregistré
    la simulation précédente."""
    if not NODE:
        pytest.skip("node absent")
    prog = """
      var SIM_DATA = { name: 'premier' };
      var window = {};
      window.simDonnees = function(){ return SIM_DATA; };
      var avant = window.simDonnees().name;
      SIM_DATA = { name: 'second' };          /* ce que fait simReset */
      console.log(JSON.stringify([avant, window.simDonnees().name]));
    """
    r = subprocess.run([NODE, "-e", prog], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-600:]
    assert json.loads(r.stdout.strip()) == ["premier", "second"], r.stdout


def test_la_porte_est_posee_avant_que_quiconque_s_en_serve():
    """Les deux appelants sont plus loin dans le fichier que le simulateur :
    la porte doit être posée avant eux, sinon elle n'existe pas au moment du
    clic."""
    porte = ECRAN.index("window.simDonnees = function()")
    for appelant in ("window.simAddToRegistre = function()",
                     "window.histoSaveSimulateur"):
        assert ECRAN.index(appelant) > porte, appelant


# ── 2. PLUS PERSONNE NE NOMME L'ÉTAT HORS DE SA PORTÉE ───────────────────

#: Les deux boutons qui vivent HORS du bloc du simulateur, et qui nommaient
#: son état comme s'ils étaient dedans.
APPELANTS = {
    "simAddToRegistre": ("window.simAddToRegistre = function(){", "\n})();"),
    "histoSaveSimulateur": ("window.histoSaveSimulateur = function(){", "\n};"),
}


@pytest.mark.parametrize("appelant", sorted(APPELANTS))
def test_aucun_appelant_ne_nomme_l_etat_hors_de_sa_portee(appelant):
    """LE DÉFAUT D'ORIGINE. Ces deux fonctions sont écrites plus loin que le
    bloc du simulateur : elles n'y ont pas accès. Nommer `SIM_DATA` là vaut
    « undefined » quoi qu'ait saisi l'utilisateur, et leur garde était donc
    toujours vraie."""
    debut, fin = APPELANTS[appelant]
    corps = _bloc(debut, fin)
    assert "SIM_DATA" not in corps, (
        "« %s » nomme encore SIM_DATA hors de sa portée : la garde sera "
        "toujours vraie et le bouton refusera toujours" % appelant)


@pytest.mark.parametrize("appelant", sorted(APPELANTS))
def test_aucun_appelant_n_appelle_la_classification_hors_de_sa_portee(appelant):
    debut, fin = APPELANTS[appelant]
    corps = _bloc(debut, fin)
    assert not re.search(r"(?<![.\w])simClassify\(\)", corps), (
        "« %s » appelle simClassify hors de sa portée" % appelant)


# ── 3. LE BOUTON ENREGISTRE VRAIMENT — LE VRAI CODE, EXÉCUTÉ ─────────────

def _jouer(donnees):
    """Exécute le VRAI `simAddToRegistre` contre un environnement simulé, et
    rend ce qui s'est passé : l'alerte éventuelle, et ce qui serait envoyé."""
    if not NODE:
        pytest.skip("node absent")
    #  ON EXÉCUTE LE VRAI CORPS, coupé juste avant le `fetch` : la règle
    #  mesure ce qui PART au registre, pas le réseau. La fonction est
    #  rouverte sous un autre nom et refermée ici, puis appelée.
    corps = _bloc("var SECTEUR_LABELS = {", "\n  var btn = document.getElementById")
    corps = corps.replace("window.simAddToRegistre = function(){",
                          "function jouer(){", 1)
    prog = """
      var alertes = [], envoye = null;
      var window = {};
      function alert(m){ alertes.push(m); }
      window.simDonnees = function(){ return %s; };
      window.simClassifier = function(){
        return { level: 'haut', score: 7.4, article: 'Art. 6(2) — Annexe III' }; };
      %s
        envoye = payload;
      }
      jouer();
      console.log(JSON.stringify({ alertes: alertes, envoye: envoye }));
    """ % (json.dumps(donnees) if donnees is not None else "null", corps)
    r = subprocess.run([NODE, "-e", prog], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail("le bouton ne s'exécute pas :\n%s" % (r.stderr or "")[-1500:])
    return json.loads(r.stdout.strip())


def test_un_simulateur_rempli_n_est_plus_refuse():
    """C'EST LE DÉFAUT, EXÉCUTÉ. Avant, cette alerte tombait toujours."""
    r = _jouer({"name": "Assistant de tri", "secteur": "emploi",
                "type": "scoring", "desc": "Tri des candidatures"})
    assert r["alertes"] == [], (
        "le bouton refuse une simulation remplie : %s" % r["alertes"])
    assert r["envoye"]["nom"] == "Assistant de tri", r["envoye"]


def test_un_simulateur_vide_est_toujours_refuse():
    """La garde garde encore : on a réparé la portée, pas supprimé le
    contrôle."""
    for vide in (None, {}, {"name": ""}):
        r = _jouer(vide)
        assert len(r["alertes"]) == 1, (vide, r)
        assert "Completez d abord le simulateur" in r["alertes"][0], r["alertes"]


def test_le_systeme_part_au_registre_avec_sa_classification_et_son_secteur():
    """Le pont ne sert à rien s'il perd ce que le simulateur a établi."""
    r = _jouer({"name": "Assistant de tri", "secteur": "emploi",
                "type": "scoring", "desc": "Tri des candidatures"})
    p = r["envoye"]
    assert p["classification"] == "haut", p
    assert p["secteur"] == "Emploi / RH", p
    assert p["type_systeme"] == "scoring", p
    assert p["finalite"] == "Tri des candidatures", p
    assert p["justification"] == "Art. 6(2) — Annexe III", p
    assert p["score_risque"] == 7, p


@pytest.mark.parametrize("niveau,attendu", [
    ("interdit", "inacceptable"), ("haut", "haut"),
    ("limite", "limite"), ("minimal", "minimal"),
])
def test_chaque_niveau_du_simulateur_arrive_au_registre_dans_son_vocabulaire(niveau, attendu):
    """Le simulateur dit « interdit », le registre dit « inacceptable » : la
    traduction doit tenir pour les quatre niveaux, sans quoi un système part
    « à évaluer » alors qu'il est classé."""
    if not NODE:
        pytest.skip("node absent")
    corps = _bloc("var LEVEL_TO_CLASSIF = {", "\nwindow.simAddToRegistre")
    prog = ("%s\nconsole.log(JSON.stringify(LEVEL_TO_CLASSIF[%s] || 'a_evaluer'));"
            % (corps, json.dumps(niveau)))
    r = subprocess.run([NODE, "-e", prog], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-600:]
    assert json.loads(r.stdout.strip()) == attendu, r.stdout
