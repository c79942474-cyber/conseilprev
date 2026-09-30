# -*- coding: utf-8 -*-
"""prEN 18229-3 — CE QUE LE MODULE REFUSE DE CHARGER, ET POURQUOI C'EST ICI.

POURQUOI UN SECOND FICHIER. `en18229_3` et `conformite` se contrôlent
eux-mêmes à l'import et lèvent sur une table incohérente. C'est le bon
endroit : un dépôt cassé ne se déploie pas. Mais un module qui lève à
l'import EMPÊCHE de collecter tout fichier de règles qui l'importe — la
faute est bien attrapée, et pourtant aucune règle ne peut la NOMMER.

CE FICHIER N'IMPORTE DONC NI L'UN NI L'AUTRE. Il prend leur source, y
INJECTE un défaut précis dans une copie jetable, l'importe là, et vérifie
que le refus nomme ce défaut-là. Chaque règle mesure donc une porte, une
seule, et le dit — au lieu de constater qu'« un fichier n'a pas collecté ».
"""
import io
import os
import subprocess
import sys
import textwrap

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _refus(tmp_path, module, avant, apres):
    """Le message que `module` rend quand on y injecte ce défaut, ou None
    s'il se charge quand même.

    LA SUBSTITUTION DOIT S'APPLIQUER EXACTEMENT UNE FOIS. Si l'ancre a
    disparu du module, la règle tombe ici — c'est voulu : une porte dont on
    ne trouve plus le montant n'est plus une porte.
    """
    src = io.open(os.path.join(_RACINE, module + ".py"), encoding="utf-8").read()
    assert src.count(avant) == 1, (
        "l'ancre du défaut injecté n'est plus dans %s.py (%d fois) : %r"
        % (module, src.count(avant), avant[:70]))
    d = tmp_path / "copie"
    d.mkdir()
    #  LE MODULE A DES VOISINS : on le charge depuis la racine, en ne
    #  remplaçant QUE le fichier muté par la copie défectueuse.
    (d / (module + ".py")).write_text(src.replace(avant, apres),
                                      encoding="utf-8")
    #  L'ORDRE DES DEUX CHEMINS EST LE POINT : chaque insert(0) passe
    #  devant le précédent, donc la copie défectueuse s'insère EN DERNIER
    #  pour être trouvée EN PREMIER. Inversés, on importerait le vrai
    #  module et toutes les règles de ce fichier passeraient pour rien.
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
                       text=True, timeout=120, cwd=_RACINE)
    return (r.stdout or "") + (r.stderr or "")


def test_le_module_se_charge_SANS_defaut_injecte(tmp_path):
    """LE TÉMOIN. Sans cette règle, toutes les suivantes passeraient aussi
    bien si le module levait toujours."""
    m = _refus(tmp_path, "en18229_3",
               '    "presomption": False,', '    "presomption": False,  # ok')
    assert "chargé sans broncher" in m, m


def test_le_module_REFUSE_une_presomption_de_conformite_declaree(tmp_path):
    """LE MENSONGE LE PLUS COÛTEUX DU MODULE. Annoncer une présomption que la
    citation au Journal officiel n'a pas ouverte vendrait une couverture
    juridique inexistante."""
    m = _refus(tmp_path, "en18229_3",
               '    "presomption": False,', '    "presomption": True,')
    assert "présomption de conformité" in m, m
    assert "Journal officiel" in m, m


def test_le_module_REFUSE_une_licence_qui_ne_nomme_pas_le_droit_d_auteur(tmp_path):
    """LA LICENCE COMMANDE LA FORME DU MODULE : c'est elle qui dit pourquoi
    aucune phrase normative n'est recopiée. La perdre déferait la doctrine
    sans que rien ne casse."""
    m = _refus(tmp_path, "en18229_3",
               '    "licence": "PROTÉGÉE PAR LE DROIT D\'AUTEUR',
               '    "licence": "Publiée par le CEN')
    assert "droit d'auteur" in m, m


def test_le_module_REFUSE_un_verrou_dont_le_plafond_ne_se_LIT_PAS(tmp_path):
    """DEUX CHAMPS DÉRIVENT, UN TEXTE NON. Si le plafond cessait d'être lu
    dans la phrase que le client lit, l'écran pourrait annoncer 25 % pendant
    que le calcul en laisse passer 100."""
    m = _refus(tmp_path, "en18229_3",
               "    return int(m.group(1)) if m else 100", "    return 100")
    assert "plafond" in m, m


def test_le_module_REFUSE_un_plan_qui_ne_commence_PAS_par_les_verrous(tmp_path):
    """ON NE CONÇOIT PAS UNE INTERFACE AVANT DE SAVOIR QUEL DÉLAI ELLE DOIT
    TENIR. Un plan qui commencerait ailleurs ferait travailler un client sur
    des points que le plafond rend sans effet."""
    m = _refus(tmp_path, "en18229_3",
               'ETAPES_PLAN = (\n    ("verrous", "Lever les verrous",',
               'ETAPES_PLAN = (\n    ("zverrous", "Lever les verrous",')
    assert "plan" in m, m


def test_le_module_REFUSE_une_exigence_SANS_etape_de_plan(tmp_path):
    """UN `.get(cle, "mesures")` QUI SERT VRAIMENT range un point de
    calibration dans « concevoir les mesures », et le plan devient faux sans
    que rien ne lève."""
    m = _refus(tmp_path, "en18229_3",
               '    "scenarios": "calibrer",', '    "zscenarios": "calibrer",')
    assert "étape dans le plan" in m or "n'est pas une exigence" in m, m


def test_le_module_REFUSE_un_alinea_de_l_annexe_ZA_que_personne_ne_MESURE(tmp_path):
    """LE DÉFAUT QUE CE CONTRÔLE A TROUVÉ À L'ÉCRITURE : cinq paragraphes de
    l'annexe n'avaient aucune question. L'alinéa se serait affiché
    « couvert » en ne mesurant rien."""
    #  LE PARAGRAPHE CHOISI EST PORTÉ PAR UNE SEULE QUESTION : le déplacer
    #  laisse vraiment l'alinéa 14(4)(e) sans rien qui le mesure. Un
    #  paragraphe porté par deux questions ne prouverait rien.
    m = _refus(tmp_path, "en18229_3",
               '_e("etat_sur", "5.7.5"', '_e("etat_sur", "5.7.9"')
    assert "5.7.5" in m, m
    assert "aucune question du cadre ne couvre" in m, m


def test_le_module_REFUSE_une_ARITHMETIQUE_de_scenario_qui_ne_tient_plus(tmp_path):
    """LA PARTIE CALCULABLE SE CONTRÔLE ELLE-MÊME, SUR TROIS CAS ÉCRITS DANS
    LE MODULE : une revue rétrospective qui dépasse 200 ms doit être
    signalée, la même consignée au titre du 5.2.4 doit être reconnue, et la
    même sur deux heures doit tenir. Inverser la comparaison casse les
    trois."""
    m = _refus(tmp_path, "en18229_3", "    if latence <= delai:",
               "    if latence >= delai:")
    assert "qui tient un délai de deux heures est refusée" in m, m


def test_le_module_REFUSE_de_ne_plus_reconnaitre_la_consignation_du_5_2_4(tmp_path):
    """LE SEUL AVEU RECEVABLE DE LA NORME. Ne plus le reconnaître ferait
    plafonner le score d'un client qui a fait exactement ce que le texte
    demande — consigner l'impossibilité technique au dossier de risque."""
    m = _refus(tmp_path, "en18229_3", "    if consignee:", "    if not consignee:")
    assert "l'impossibilité technique consignée n'est plus reconnue" in m, m


def test_le_module_REFUSE_un_verrou_que_le_score_DEPASSE(tmp_path):
    """LE CONTRÔLE QUI ÉPROUVE LE PLAFOND EN LE JOUANT. Chaque verrou est
    rejoué sur un questionnaire où tout SAUF lui est tenu : si le score monte
    au-dessus du plafond annoncé, la phrase que le client lit est fausse, et
    le module refuse de démarrer plutôt que de l'afficher."""
    m = _refus(tmp_path, "en18229_3",
               '    return {"brut": brut, "taux": min(brut, plafond), "plafond": plafond,',
               '    return {"brut": brut, "taux": brut, "plafond": plafond,')
    assert "annonce 25 % mais le score monte à" in m, m


def test_conformite_REFUSE_un_compte_de_normes_qui_NE_SUIT_PAS_la_table(tmp_path):
    """LE TITRE CODÉ EN DUR QUI DIT SEPT QUAND LA GRILLE EN MONTRE NEUF est un
    défaut déjà rencontré sur ce site, et corrigé une fois. La garde le tient
    maintenant des deux côtés."""
    m = _refus(tmp_path, "conformite", "NORMES_ANNONCEES = 12",
               "NORMES_ANNONCEES = 11")
    assert "annonce" in m or "normes" in m, m
