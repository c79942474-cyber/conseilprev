"""L'indice de coût de construction : ce que l'enveloppe ne savait pas du pays.

CE QUE CES TESTS PROTÈGENT, ET LA FAUTE QU'ILS EMPÊCHENT.

Le coût unitaire de ce module est une hypothèse de FILIÈRE, en M€ par MW
informatique : elle ne connaît pas le pays. Trois pays comparés rendaient donc
trois enveloppes rigoureusement identiques — 736 à 920 M€ pour l'Irlande, la
Suède et la France — et rien ne le disait. Comparer deux pays sur une enveloppe
commune, c'est les comparer au même prix de main-d'œuvre.

  1. LE MÉCANISME EXISTE, ET IL SE PROPAGE. L'indice s'applique au coût
     unitaire, donc à TOUT ce qui en découle : chaque lot de la DPGF,
     l'échéancier, le coût total. L'appliquer plus loin laisserait des
     grandeurs incohérentes entre elles — une enveloppe ajustée au-dessus de
     lots qui ne le seraient pas.

  2. LE MODULE NE FABRIQUE PAS LE COEFFICIENT. Ces indices existent chez
     Eurostat, ils sont publics et ils changent chaque année ; les recopier de
     mémoire en ferait des chiffres sans millésime que personne ne pourrait
     vérifier. Le test vérifie qu'aucune table par pays n'est apparue.

  3. SANS INDICE, LE MODULE LE DIT. C'est le point qui compte le plus : un
     silence laisserait conclure que construire coûte la même chose partout
     dans l'Union.

  4. UN INDICE ABERRANT EST REFUSÉ, PAS CORRIGÉ EN SILENCE. À 900, l'enveloppe
     serait absurde et aucune alerte en aval ne la rattraperait.
"""
import os
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import finance_dc as f  # noqa: E402


def test_sans_indice_le_module_le_dit_au_lieu_de_se_taire():
    d = f.dpgf(100, pays="FR")
    i = d["indice_construction"]
    assert i["applique"] is False
    assert i["valeur"] is None
    assert i["nature"] == "absent"
    # LA PHRASE QUI ÉVITE LE CONTRESENS : elle doit dire que l'enveloppe est la
    # MÊME pour tous les pays, pas seulement qu'un indice manque.
    assert "MEME pour tous les pays" in i["dit"] or "MÊME pour tous les pays" in i["dit"]
    assert "PAS pris en compte" in i["dit"]


def test_deux_pays_sans_indice_rendent_la_meme_enveloppe():
    """LE CONSTAT QUI JUSTIFIE TOUT LE RESTE. Si un jour le coût unitaire
    devenait country-aware par un autre chemin, ce test tomberait — et il
    faudrait alors revoir le message ci-dessus, qui deviendrait faux."""
    a = f.dpgf(100, pays="IE")
    b = f.dpgf(100, pays="PL")
    assert a["enveloppe_meur"] == b["enveloppe_meur"], (
        "le coût unitaire est devenu dépendant du pays : le message "
        "« l'enveloppe ne dépend pas du pays » est désormais faux")


def test_l_indice_deplace_l_enveloppe_exactement_du_bon_facteur():
    base = f.dpgf(100, pays="FR")["enveloppe_meur"]
    for indice in (70.0, 100.0, 130.0):
        d = f.dpgf(100, pays="FR", indice_construction=indice)
        k = indice / 100.0
        for j in (0, 1):
            assert abs(d["enveloppe_meur"][j] - base[j] * k) < 0.15, (indice, j)
        assert d["indice_construction"]["applique"] is True
        assert abs(d["indice_construction"]["valeur"] - indice) < 0.01


def test_l_ajustement_se_propage_a_CHAQUE_lot():
    """UNE ENVELOPPE AJUSTÉE AU-DESSUS DE LOTS QUI NE LE SERAIENT PAS ne
    s'additionnerait plus : c'est le défaut que ce test empêche."""
    a = f.dpgf(100, pays="FR")
    b = f.dpgf(100, pays="FR", indice_construction=130)
    la = {x["code"]: x["meur"] for x in a["lots"]}
    lb = {x["code"]: x["meur"] for x in b["lots"]}
    assert set(la) == set(lb)
    bouge = 0
    for code in la:
        for j in (0, 1):
            if la[code][j] == 0:
                continue
            assert abs(lb[code][j] / la[code][j] - 1.30) < 0.02, code
            bouge += 1
    assert bouge >= 10, "trop peu de lots vérifiés : %d" % bouge
    # ET LE TOTAL DES LOTS SUIT L'ENVELOPPE : les deux ne doivent pas diverger.
    assert abs(sum(x["meur"][1] for x in b["lots"])
               / sum(x["meur"][1] for x in a["lots"]) - 1.30) < 0.02


def test_un_indice_aberrant_est_refuse_pas_corrige():
    for mauvais in (900.0, 5.0, -20.0):
        d = f.dpgf(100, pays="FR", indice_construction=mauvais)
        assert d.get("ok") is False, mauvais
        assert d["erreur"] == "indice_hors_bornes"
        assert "UE27 = 100" in d["message"]
    # AUX BORNES EXACTES, ON ACCEPTE : refuser 40 ou 200 rejetterait des pays
    # réels de l'Union.
    for bon in (f.INDICE_CONSTRUCTION["min"], f.INDICE_CONSTRUCTION["max"]):
        assert f.dpgf(100, pays="FR", indice_construction=bon).get("ok") is not False


def test_une_saisie_illisible_ne_fait_pas_tomber_le_calcul():
    """Un champ vide ou une virgule mal placée ne doit pas casser l'étude :
    l'indice est optionnel, et son absence a déjà un sens défini."""
    for illisible in ("", None, "abc", []):
        d = f.dpgf(100, pays="FR", indice_construction=illisible)
        assert d.get("ok") is not False, repr(illisible)
        assert d["indice_construction"]["applique"] is False


def test_le_module_ne_fabrique_AUCUNE_valeur_par_pays():
    """LA LIGNE À NE PAS FRANCHIR. Le jour où quelqu'un ajoutera une table
    « FR: 110, IE: 120 » de mémoire, ce test tombera — et c'est le but. Ces
    indices se publient avec un millésime ; sans lui, ils ne se vérifient pas."""
    I = f.INDICE_CONSTRUCTION
    assert "refus" in I and "AUCUNE VALEUR PAR PAYS" in I["refus"]
    assert "Eurostat" in I["source"]
    # Aucune clé de deux lettres majuscules — c'est-à-dire aucun code pays.
    codes = [k for k in I if len(k) == 2 and k.isupper()]
    assert codes == [], "des codes pays sont apparus dans le référentiel : %s" % codes
    # Et le mécanisme reste neutre par défaut.
    assert I["reference"] == 100.0


def test_l_indice_est_declare_dans_le_dossier_rendu():
    """Un ajustement silencieux serait pire que pas d'ajustement : le lecteur
    verrait une enveloppe bouger sans pouvoir refaire le calcul."""
    d = f.dpgf(100, pays="FR", indice_construction=115)
    i = d["indice_construction"]
    assert i["nature"] == "saisi"
    assert "Eurostat" in i["source"]
    assert "15" in i["dit"]
