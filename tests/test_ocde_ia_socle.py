# -*- coding: utf-8 -*-
"""Diligence OCDE — CE QUE LE MODULE REFUSE DE CHARGER, ET POURQUOI C'EST ICI.

POURQUOI UN SECOND FICHIER. `ocde_ia` se contrôle lui-même à l'import : il
recompte ses tables ET REJOUE son arithmétique, puis lève. C'est le bon
endroit — un dépôt incohérent ne se déploie pas. Mais un module qui lève à
l'import EMPÊCHE de collecter tout fichier de règles qui l'importe : la faute
est bien attrapée, et pourtant aucune règle ne peut la NOMMER. La batterie de
mutations, elle, lit une erreur de collecte comme une survivante.

CE FICHIER N'IMPORTE DONC PAS LE MODULE. Il prend sa source, y INJECTE un
défaut précis dans une copie jetable, l'importe là, et vérifie que le refus
nomme ce défaut-là.

LES QUATRE PORTES QUI COMPTENT, ET POURQUOI CELLES-LÀ. Ce sont les quatre que
la batterie de `tests/test_ocde_ia.py` a montrées hors de sa portée, parce que
la garde les intercepte avant qu'une règle ne puisse les mesurer :
  · LES EXEMPLES QU'AUCUN GROUPE NE VISE qui cesseraient de sortir du calcul —
    un organisme du seul groupe 3 se verrait reprocher de ne pas être un
    fournisseur de calcul ;
  · LE VERROU DE L'ÉTAPE NON NÉGOCIABLE qui ne porterait plus que sur son
    étape — l'encadré 2.4 dit que la réparation est ATTENDUE dès qu'on cause,
    pas qu'elle compte un peu plus ;
  · LE PLAFOND GLOBAL qui cesserait d'être la recomposition des parts
    plafonnées — l'indice et l'écran du module afficheraient deux nombres ;
  · UN CADRE DÉCLARÉ MESURÉ qui ne l'est pas — la feuille de route dirait
    « Sentinel tient celui-là » d'un cadre que le taux ne connaît pas.
"""
import io
import os
import subprocess
import sys
import textwrap

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _refus(tmp_path, avant, apres, module="ocde_ia"):
    """Le message que le module rend quand on y injecte ce défaut, ou
    « chargé sans broncher » s'il se charge quand même.

    LA SUBSTITUTION DOIT S'APPLIQUER EXACTEMENT UNE FOIS. Si l'ancre a
    disparu du module, la règle tombe ici — c'est voulu : une porte dont on ne
    trouve plus le montant n'est plus une porte.
    """
    src = io.open(os.path.join(_RACINE, module + ".py"),
                  encoding="utf-8").read()
    assert src.count(avant) == 1, (
        "l'ancre du défaut injecté n'est plus dans %s.py (%d fois) : %r"
        % (module, src.count(avant), avant[:70]))
    d = tmp_path / "copie"
    d.mkdir()
    (d / (module + ".py")).write_text(src.replace(avant, apres),
                                      encoding="utf-8")
    #  L'ORDRE DES DEUX CHEMINS EST LE POINT : chaque insert(0) passe devant
    #  le précédent, donc la copie défectueuse s'insère EN DERNIER pour être
    #  trouvée EN PREMIER. Inversés, on importerait le vrai module et toutes
    #  les règles de ce fichier passeraient pour rien.
    code = textwrap.dedent("""
        import sys
        sys.path.insert(0, %r)
        sys.path.insert(0, %r)
        try:
            __import__(%r)
        except RuntimeError as e:
            sys.stdout.write(str(e))
        else:
            sys.stdout.write("(chargé sans broncher)")
    """) % (_RACINE, str(d), module)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True,
                       text=True, timeout=180, cwd=_RACINE)
    return (r.stdout or "") + (r.stderr or "")


# ═══════════════════════════════════════════════════════════════════════════
#  LE TÉMOIN — sans lui, toutes les règles qui suivent ne prouveraient rien
# ═══════════════════════════════════════════════════════════════════════════

def test_le_module_se_charge_SANS_defaut_injecte(tmp_path):
    """LE TÉMOIN. Un module qui lèverait TOUJOURS ferait passer chacune des
    règles suivantes sans qu'aucune mesure ait eu lieu. On injecte donc un
    changement inoffensif — un commentaire — et on exige qu'il se charge."""
    m = _refus(tmp_path,
               'NOM_DU_TAUX = "Couverture des exemples retenus"',
               'NOM_DU_TAUX = "Couverture des exemples retenus"  # inoffensif')
    assert "chargé sans broncher" in m, m


# ═══════════════════════════════════════════════════════════════════════════
#  1. LES EXEMPLES QU'AUCUN GROUPE NE VISE SORTENT, ILS NE COMPTENT PAS ZÉRO
# ═══════════════════════════════════════════════════════════════════════════

def test_le_module_REFUSE_que_les_exemples_hors_groupe_comptent_zero(tmp_path):
    """LE DÉFAUT QUI PUNIRAIT LE CLIENT POUR CE QU'IL N'EST PAS. Les 115
    exemples ne s'adressent pas tous aux mêmes entreprises : le document en
    range certains pour les fournisseurs de calcul et d'autres pour les
    déployeurs. Les compter zéro chez qui n'est ni l'un ni l'autre, ce serait
    lui reprocher son métier."""
    m = _refus(
        tmp_path,
        '    retenus = [e for e in EXEMPLES if g & set(e["groupes"])]',
        '    retenus = list(EXEMPLES)')
    assert "retenus + écartés ≠ total des exemples" in m, m


# ═══════════════════════════════════════════════════════════════════════════
#  2. LE VERROU DE L'ÉTAPE NON NÉGOCIABLE PORTE SUR TOUTES LES PARTS
# ═══════════════════════════════════════════════════════════════════════════

def test_le_module_REFUSE_un_verrou_d_etape_qui_ne_porte_que_sur_SON_etape(tmp_path):
    """L'ENCADRÉ 2.4 NE DIT PAS QUE LA RÉPARATION COMPTE UN PEU PLUS. Il dit
    qu'elle est ATTENDUE dès que l'entreprise cause ou contribue. Un organisme
    qui cause un dommage et n'a aucun dispositif de réparation ne peut pas se
    prévaloir de ses politiques : elles n'ont pas empêché le dommage, et rien
    ne le répare. Le verrou doit donc porter sur TOUTES les parts."""
    m = _refus(
        tmp_path,
        '            for autre in ETAPES:\n                _poser(autre["cle"], t)',
        '            _poser(cle_etape, t)')
    assert "plafonner le taux à 0" in m, m


# ═══════════════════════════════════════════════════════════════════════════
#  3. LE PLAFOND GLOBAL N'EST QUE LA RECOMPOSITION DES PARTS PLAFONNÉES
# ═══════════════════════════════════════════════════════════════════════════

def test_le_module_REFUSE_un_plafond_global_qui_n_est_pas_la_recomposition(tmp_path):
    """DEUX VÉRITÉS SUR LE MÊME NOMBRE. `conformite` ne lit pas le total : il
    lit les PARTS et les recompose de son côté. Si le plafond global du moteur
    cessait d'être exactement cette recomposition, l'indice et l'écran du
    module afficheraient deux chiffres pour une seule déclaration — et aucun
    des deux ne serait repérable comme le faux."""
    m = _refus(
        tmp_path,
        '        for e in etapes_plafonnees)\n    plafond = ',
        '        for e in etapes)\n    plafond = ')
    assert "recomposition des parts plafonnées" in m, m


# ═══════════════════════════════════════════════════════════════════════════
#  4. UN CADRE DÉCLARÉ MESURÉ EST UN CADRE QUE LE TAUX CONNAÎT
# ═══════════════════════════════════════════════════════════════════════════

def test_le_module_REFUSE_un_quatrieme_cadre_declare_mesure(tmp_path):
    """TROIS SUR VINGT, ET LE DIRE EST LE POINT. La feuille de route nomme
    vingt cadres ; Sentinel en mesure trois. En déclarer un quatrième ferait
    dire à l'écran « celui-là est tenu ici » d'un cadre pour lequel il n'y a
    ni questionnaire, ni taux, ni plan."""
    m = _refus(
        tmp_path,
        'CADRES_MESURES = tuple(c["cle"] for c in CADRES if c["mesure"])',
        'CADRES_MESURES = tuple(c["cle"] for c in CADRES if c["mesure"]) + ("dsa",)')
    assert "cadre(s) mesuré(s) au lieu de 3" in m, m
