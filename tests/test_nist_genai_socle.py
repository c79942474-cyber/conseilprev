# -*- coding: utf-8 -*-
"""NIST AI 600-1 — CE QUE LE MODULE REFUSE DE CHARGER, ET POURQUOI C'EST ICI.

MÊME RAISON QUE POUR prEN 18229-3, ET C'EST LA SEULE. `nist_genai` se
contrôle lui-même à l'import et lève sur une table incohérente — c'est le
bon endroit, un dépôt cassé ne se déploie pas. Mais un module qui lève à
l'import EMPÊCHE de collecter tout fichier de règles qui l'importe : la
faute est bien attrapée, et pourtant aucune règle ne peut la NOMMER.

CE FICHIER N'IMPORTE DONC PAS `nist_genai`. Il prend sa source, y INJECTE
un défaut précis dans une copie jetable, l'importe là, et vérifie que le
refus nomme ce défaut-là.

ET LA GARDE DE CE MODULE FAIT PLUS QUE COMPTER. Elle REJOUE le plafond sur
quatre cas écrits dans le fichier : c'est ce plafond qui fait bouger le taux
affiché au client, et une garde qui ne vérifierait que des nombres
laisserait passer une inversion de comparaison.
"""
import io
import os
import subprocess
import sys
import textwrap

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _refus(tmp_path, avant, apres, module="nist_genai"):
    """Le message que `module` rend quand on y injecte ce défaut, ou
    « chargé sans broncher » s'il se charge quand même."""
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


def test_le_module_se_charge_SANS_defaut_injecte(tmp_path):
    """LE TÉMOIN. Sans cette règle, toutes les suivantes passeraient aussi
    bien si le module levait toujours.

    ET IL SERT UNE SECONDE FOIS, POUR LES DÉFAUTS QUE LA GARDE ATTRAPE DE
    TROP LOIN. Compter une action sans réponse comme TENUE, par exemple, ne
    fait tomber aucune porte nommée : la garde refuse alors le module sur
    trois de ses contrôles à la fois, et c'est le témoin — pas eux — qui dit
    ce qui s'est passé. « Le module ne se charge plus du tout » est le
    constat juste, et le seul qui ne prétende pas viser un défaut précis."""
    m = _refus(tmp_path, '    "actions": 211,', '    "actions": 211,  # ok')
    assert "chargé sans broncher" in m, m


def test_le_module_REFUSE_un_COMPTE_D_ACTIONS_qui_ne_suit_pas_le_document(tmp_path):
    """211 A ÉTÉ COMPTÉ DANS LE DOCUMENT, PAS DÉRIVÉ DE LA TABLE. GV-1.1-002
    n'existe pas — il n'apparaît qu'au guide de lecture du §3, comme exemple
    de codification. Une table qui rendrait 212 aurait donc repris cet
    exemple pour une action."""
    m = _refus(tmp_path, '    "actions": 211,', '    "actions": 212,')
    assert "actions" in m and "document" in m, m


def test_le_module_REFUSE_une_DISTRIBUTION_par_risque_qui_ne_retombe_pas(tmp_path):
    """LE RELEVÉ EST LE SEUL CONTRE-POIDS D'UNE TABLE DE 211 LIGNES. Sans
    lui, déplacer une action d'un risque à l'autre — par confort de
    relecture, sur un libellé — passerait inaperçu, et le champ d'un client
    changerait sans que rien ne le dise."""
    m = _refus(tmp_path, "8: 71, 9: 50", "8: 70, 9: 51")
    assert "risque" in m and "relevé" in m, m


def test_le_module_REFUSE_un_compte_par_FONCTION_qui_ne_retombe_pas(tmp_path):
    m = _refus(tmp_path, '"MEASURE": 72, "MANAGE": 43', '"MEASURE": 73, "MANAGE": 42')
    assert "MEASURE" in m or "MANAGE" in m, m


def test_le_module_REFUSE_un_PLAFOND_qui_ne_tombe_plus_a_zero_action(tmp_path):
    """LE DÉFAUT QUI COÛTERAIT LE PLUS CHER AU CLIENT : une catégorie
    « prouvée » sur le cadre resterait prouvée pour un système génératif
    dont aucune action du profil n'est tenue. Le taux ne bougerait pas, et
    l'écran vendrait une couverture qui n'existe pas."""
    m = _refus(tmp_path, '    if taux <= 0:\n        return "amorce"',
               '    if taux <= 0:\n        return None')
    assert "catégories tombent" in m, m


def test_le_module_REFUSE_un_plafond_qui_RELEVE_un_etat_du_socle(tmp_path):
    """LE PROFIL SUPPOSE LE CADRE, IL NE LE REMPLACE PAS. Un plafond qui
    relèverait ferait passer une maison sans gouvernance IA pour une maison
    qui en a, au seul motif qu'elle tient les actions d'AI 600-1."""
    m = _refus(tmp_path,
               "    return plafond if _RANG[plafond] < _RANG[etat] else etat",
               "    return plafond if _RANG[plafond] != _RANG[etat] else etat")
    assert "RELEVÉ" in m, m


def test_le_module_REFUSE_un_plafond_qui_frappe_un_systeme_NON_generatif(tmp_path):
    """AI 600-1 NE S'APPLIQUE QU'À L'IA GÉNÉRATIVE. Un plafond qui
    s'appliquerait quand même ferait baisser le taux d'un modèle de scoring
    déterministe au nom d'un profil qui ne le vise pas."""
    m = _refus(tmp_path, '    if not d.get("genai"):\n        return base, []',
               '    if False:\n        return base, []')
    assert "NON génératif" in m, m


def test_le_module_REFUSE_que_l_etiquette_HORS_LISTE_ouvre_des_actions(tmp_path):
    """« Civil Rights violations » n'est pas un treizième risque : le
    document l'emploie une fois sans l'avoir définie. La retenir ferait
    entrer une action dans le champ d'un client qui n'a déclaré aucun des
    douze."""
    m = _refus(tmp_path,
               "        if n in _rmf.RISQUES_PAR_N:\n            out.add(n)",
               "        if n in _rmf.RISQUES_PAR_N or n in HORS_DOUZE:\n"
               "            out.add(n)")
    assert "hors des douze" in m, m


def test_le_module_REFUSE_une_action_rattachee_HORS_du_cadre(tmp_path):
    """UNE ACTION QUI POINTE SUR UNE SOUS-CATÉGORIE INEXISTANTE ne
    plafonnerait jamais rien : elle serait dans la table, applicable, et
    sans effet — le pire des cas, parce qu'elle compterait au dénominateur
    de la couverture."""
    m = _refus(tmp_path, '("GV-1.1-001", "GOVERN 1.1",',
               '("GV-1.1-001", "GOVERN 1.9",')
    assert "n'est pas au cadre" in m or "se range sous" in m, m


def test_le_module_REFUSE_un_code_qui_CONTREDIT_sa_sous_categorie(tmp_path):
    """DEUX PORTES, ET IL FALLAIT LES DEUX. La précédente attrape une
    sous-catégorie qui n'existe PAS au cadre ; celle-ci attrape une
    sous-catégorie qui existe et qui n'est pas celle que le code annonce.
    Mesuré : avec la seule première, désarmer ce contrôle-ci ne faisait
    tomber aucune règle — GV-1.1-001 rangé sous GOVERN 1.2 se chargeait
    sans un mot, et son action plafonnait la mauvaise catégorie."""
    m = _refus(tmp_path, '("GV-1.1-001", "GOVERN 1.1",',
               '("GV-1.1-001", "GOVERN 1.2",')
    assert "se range sous" in m, m


def test_le_module_REFUSE_une_RECONCILIATION_dont_le_nombre_est_faux(tmp_path):
    """LES TROIS CONTRADICTIONS DU DOCUMENT SE DISENT AVEC LEURS NOMBRES, et
    un lecteur qui recompte sur le PDF doit retrouver les mêmes. Un nombre
    laissé derrière une table qui a bougé est pire qu'aucun nombre."""
    m = _refus(tmp_path, '"risque": 6, "actions": 57,',
               '"risque": 6, "actions": 58,')
    assert "réconciliation" in m, m


def test_le_module_REFUSE_un_compte_de_SOUS_CATEGORIES_SANS_ACTION_faux(tmp_path):
    """23 SUR 72 — et c'est la nuance qui décide d'un chantier : elles sont
    sans objet POUR LE PROFIL, jamais « non couvertes »."""
    m = _refus(tmp_path, '    "sous_categories_sans_action": 23,',
               '    "sous_categories_sans_action": 22,')
    assert "sans action" in m, m
