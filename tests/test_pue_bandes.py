"""LES BANDES DE PUE — accordées entre modules, et l'écart PUBLIÉ.

DEUX CHOSES DIFFÉRENTES SONT GARDÉES ICI, ET AUCUNE N'ÉTAIT GARDÉE AVANT.

  1. TROIS MODULES PORTENT DES BANDES DE PUE PAR FAMILLE DE REFROIDISSEMENT.
     `finance_dc.REFROIDISSEMENT` en décrit quatre, `datacentres.PUE` six ;
     deux familles sont communes — `free_cooling` et `adiabatique` — et elles
     s'accordent aujourd'hui au centième. Mesuré : accord exact sur les deux.
     Mais rien ne l'imposait : l'accord tenait par discipline, pas par
     garantie. Une bande retouchée d'un côté et pas de l'autre aurait fait
     coexister deux vérités pour la même famille, dans le même cabinet, sans
     qu'aucune ligne ne le dise. C'est exactement le genre d'écart que ce
     dépôt a déjà mesuré entre ses deux sites sur les facteurs d'électricité.

  2. UN PUE IMPOSÉ N'ÉTAIT PLUS CONFRONTÉ À RIEN. Le chemin `pue_impose` de
     `pue_de()` bornait la valeur à [1,02 ; 2,5] et la retournait. Un PUE de
     1,05 annoncé sur des aéroréfrigérants secs — dont la bande commence à
     1,25 — passait sans une ligne. Or c'est LE dossier qu'un maître d'ouvrage
     apporte : une promesse de contrat, et c'est ce qu'une étude sert à
     instruire.

     Le module ne le REJETTE pas, et c'est voulu : un cahier des charges peut
     imposer ce que la famille ne porte pas d'ordinaire. Il le PUBLIE — même
     geste que l'écart d'arrondi du tableau d'honoraires, qui est écrit sous
     le total plutôt que dissous dans une ligne au hasard.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import finance_dc as F
import datacentres as D


def test_LE_POINT_QUI_DECIDE_les_familles_communes_portent_la_meme_bande():
    """Deux modules, une famille, un seul chiffre — ou bien lequel croire ?"""
    communes = set(F.REFROIDISSEMENT) & set(D.PUE)
    assert len(communes) >= 2, (
        "moins de deux familles communes : ce contrôle ne garderait plus rien — %s"
        % sorted(communes))
    for f in sorted(communes):
        a = tuple(F.REFROIDISSEMENT[f]["pue"])
        b = tuple(D.PUE[f])
        assert a == b, (
            "la famille « %s » vaut %s dans finance_dc et %s dans datacentres : "
            "deux vérités pour un même mode de refroidissement" % (f, a, b))


def test_les_familles_propres_a_chaque_module_sont_ASSUMEES_et_non_oubliees():
    """Les deux vocabulaires ne couvrent pas le même ensemble, et c'est
    légitime : `finance_dc` décrit les familles qu'un PROJET peut retenir,
    `datacentres` celles que le PARC cartographié présente. Ce contrôle
    n'exige pas qu'ils fusionnent — il exige qu'on sache lesquelles diffèrent,
    pour qu'un ajout futur soit un choix et non un oubli."""
    seules_projet = set(F.REFROIDISSEMENT) - set(D.PUE)
    seules_parc = set(D.PUE) - set(F.REFROIDISSEMENT)
    assert seules_projet == {"liquide", "sec"}, seules_projet
    assert seules_parc == {"air", "eau", "inconnu", "recuperation_chaleur"}, seules_parc


def test_toute_bande_est_ordonnee_et_physiquement_tenable():
    """Un PUE inférieur à 1 signifierait qu'un centre rend plus d'énergie qu'il
    n'en consomme. Une borne haute sous la borne basse rendrait une fourchette
    vide, et le code qui la lit choisirait silencieusement l'une des deux."""
    for nom, table in (("finance_dc", {k: v["pue"] for k, v in F.REFROIDISSEMENT.items()}),
                       ("datacentres", D.PUE)):
        for f, bande in table.items():
            bas, haut = float(bande[0]), float(bande[1])
            assert bas > 1.0, "%s/%s : borne basse %s ≤ 1" % (nom, f, bas)
            assert bas <= haut, "%s/%s : bande inversée %s" % (nom, f, bande)
            assert haut < 3.0, "%s/%s : borne haute %s invraisemblable" % (nom, f, haut)


# ═══════════════════════════════════════════════════════════════════════════
#  LE PUE IMPOSÉ — retenu, mais confronté
# ═══════════════════════════════════════════════════════════════════════════

def test_LE_POINT_QUI_DECIDE_un_PUE_impose_hors_bande_est_DIT():
    """LE DÉFAUT MESURÉ. 1,05 sur des aéroréfrigérants secs (bande 1,25-1,50)
    était accepté en silence. Il l'est toujours — un cahier des charges peut
    l'imposer — mais il ne passe plus sans être signalé."""
    bande = F.REFROIDISSEMENT["sec"]["pue"]
    valeur, nature, note = F.pue_de("sec", None, 1.05)
    assert valeur == [1.05, 1.05], valeur
    assert nature == "saisi_hors_bande", nature
    # …ET LA NOTE PORTE LES DEUX NOMBRES QUI PERMETTENT DE RECOMPTER.
    assert "1,05" in note
    assert "1,25" in note and "1,5" in note, note
    assert "en deçà" in note, note
    # …et elle dit ce que cela ENGAGE, sinon la réserve ne pèse rien.
    assert "ENGAGEMENT" in note, note


def test_un_PUE_impose_hors_bande_PAR_LE_HAUT_est_dit_aussi():
    """La borne haute compte autant : un PUE médiocre imposé engage le coût
    d'exploitation sur toute la vie de l'ouvrage."""
    valeur, nature, note = F.pue_de("sec", None, 1.60)
    assert nature == "saisi_hors_bande", nature
    assert "au-delà" in note, note
    assert "1,6" in note


def test_un_PUE_impose_DANS_la_bande_ne_declenche_aucune_reserve():
    """Une réserve qui paraît sans raison use celle qui en a une."""
    valeur, nature, note = F.pue_de("sec", None, 1.30)
    assert nature == "saisi", nature
    assert "ENGAGEMENT" not in note
    assert "ne le contredit pas" in note, note


def test_SANS_LA_CONFRONTATION_le_controle_precedent_ne_prouverait_rien():
    """Ce contrôle-ci existe pour que les précédents ne puissent pas passer à
    vide : il vérifie que les trois valeurs employées tombent bien de part et
    d'autre de la bande, sinon « hors bande » et « dans la bande » ne
    testeraient pas deux situations différentes."""
    bas, haut = F.REFROIDISSEMENT["sec"]["pue"]
    assert 1.05 < bas, "1,05 n'est plus sous la bande : le cas hors-bande bas a disparu"
    assert bas <= 1.30 <= haut, "1,30 n'est plus dans la bande"
    assert 1.60 > haut, "1,60 n'est plus au-dessus de la bande"


def test_le_bornage_a_deux_et_demi_reste_en_place():
    """La borne dure protège d'une saisie aberrante — 25 au lieu de 2,5. Elle
    n'a jamais été une vérification, et le nouveau texte ne la remplace pas."""
    valeur, nature, note = F.pue_de("sec", None, 25.0)
    assert valeur == [2.5, 2.5], valeur
    assert nature == "saisi_hors_bande", nature


def test_le_chemin_sans_PUE_impose_est_INCHANGE():
    """Une correction qui déplacerait le comportement par défaut changerait
    tous les chiffrages en cours sans que personne ne l'ait demandé."""
    valeur, nature, note = F.pue_de("sec", None, None)
    assert nature == "hypothese", nature
    assert valeur == list(F.REFROIDISSEMENT["sec"]["pue"]), valeur
