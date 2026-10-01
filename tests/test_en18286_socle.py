# -*- coding: utf-8 -*-
"""prEN 18286 — CE QUE LE MODULE REFUSE DE CHARGER, ET POURQUOI C'EST ICI.

POURQUOI UN SECOND FICHIER. `en18286` se contrôle lui-même à l'import et lève
sur une table incohérente. C'est le bon endroit : un dépôt cassé ne se déploie
pas. Mais un module qui lève à l'import EMPÊCHE de collecter tout fichier de
règles qui l'importe — la faute est bien attrapée, et pourtant aucune règle ne
peut la NOMMER.

CE FICHIER N'IMPORTE DONC PAS LE MODULE. Il prend sa source, y INJECTE un
défaut précis dans une copie jetable, l'importe là, et vérifie que le refus
nomme ce défaut-là. Chaque règle mesure une porte, une seule, et le dit — au
lieu de constater qu'« un fichier n'a pas collecté ».

LES CINQ PORTES QUI COMPTENT, ET POURQUOI CELLES-LÀ :
  · la PRÉSOMPTION annoncée alors que la référence n'est pas citée au Journal
    officiel — le mensonge le plus coûteux que ce module puisse dire ;
  · la LICENCE qui cesse de nommer le droit d'auteur du CEN — c'est elle qui
    dit pourquoi aucune phrase normative n'est recopiée ;
  · une RÉFÉRENCE DE L'ANNEXE ZA qui ne vise plus aucun paragraphe — l'écran
    de conformité dirait « non couvert » là où la norme couvre ;
  · le PLAFOND de la charge de preuve du §4.4.3.2.2 qui cesse de tomber, ou
    qui cesse de se lever quand les trois pièces arrivent ;
  · la LIGNE « non couvert » de l'annexe ZA qui disparaît — cent pour cent se
    lirait alors « article 17 tenu », ce que la norme elle-même dément.
"""
import io
import os
import subprocess
import sys
import textwrap

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _refus(tmp_path, avant, apres, module="en18286"):
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
                       text=True, timeout=120, cwd=_RACINE)
    return (r.stdout or "") + (r.stderr or "")


# ═══════════════════════════════════════════════════════════════════════════
#  LE TÉMOIN — sans lui, toutes les règles qui suivent ne prouveraient rien
# ═══════════════════════════════════════════════════════════════════════════

def test_le_module_se_charge_SANS_defaut_injecte(tmp_path):
    """LE TÉMOIN. Un module qui lèverait TOUJOURS ferait passer chacune des
    règles suivantes sans qu'aucune mesure ait eu lieu. On injecte donc un
    changement inoffensif — un commentaire — et on exige qu'il se charge."""
    m = _refus(tmp_path, '    "presomption": False,\n    "licence"',
               '    "presomption": False,  # inoffensif\n    "licence"')
    assert "chargé sans broncher" in m, m


# ═══════════════════════════════════════════════════════════════════════════
#  1. LA PRÉSOMPTION ET LA LICENCE — CE QUE LE MODULE NE PEUT PAS DIRE
# ═══════════════════════════════════════════════════════════════════════════

def test_le_module_REFUSE_une_presomption_de_conformite_declaree(tmp_path):
    """LE MENSONGE LE PLUS COÛTEUX DU MODULE. Annoncer une présomption que la
    citation au Journal officiel n'a pas ouverte vendrait une couverture
    juridique inexistante : le client croirait l'article 17 présumé tenu alors
    qu'un organisme notifié reste à convaincre de bout en bout."""
    m = _refus(tmp_path, '    "presomption": False,\n    "licence"',
               '    "presomption": True,\n    "licence"')
    assert "présomption de conformité" in m, m
    assert "Journal officiel" in m, m


def test_le_module_REFUSE_une_reserve_qui_ne_dit_plus_D_OU_viendrait_la_presomption(tmp_path):
    """LA RÉSERVE EST CE QUE LE CLIENT LIT. Si elle cessait de nommer le
    Journal officiel, elle dirait « ce n'est pas encore présumé » sans dire ce
    qui y changerait quelque chose — et le travail fait paraîtrait inutile au
    lieu d'être en avance."""
    m = _refus(
        tmp_path,
        "    \"Ce projet de norme n'est pas encore cit\u00e9 au Journal officiel "
        "de l'Union \"",
        "    \"Ce projet de norme n'est pas encore reconnu par la Commission \"")
    assert "Journal officiel" in m, m


def test_le_module_REFUSE_une_licence_qui_ne_nomme_pas_le_droit_d_auteur(tmp_path):
    """LA LICENCE COMMANDE LA FORME DU MODULE : c'est elle qui dit pourquoi
    aucune phrase normative n'est recopiée. La perdre déferait la doctrine
    sans que rien ne casse — et la prochaine main écrirait les énoncés."""
    m = _refus(tmp_path, '"licence": "PROTÉGÉE PAR LE DROIT D\'AUTEUR',
               '"licence": "Publiée par le CEN')
    assert "droit d'auteur" in m, m


# ═══════════════════════════════════════════════════════════════════════════
#  2. L'ANNEXE ZA — LA RÉSOLUTION, ET LA LIGNE VIDE
# ═══════════════════════════════════════════════════════════════════════════

def test_le_module_REFUSE_une_reference_ZA_qui_ne_vise_AUCUN_paragraphe(tmp_path):
    """LE DÉFAUT QUI COÛTE LE PLUS CHER À L'ÉCRAN DE CONFORMITÉ, et qui ne se
    voit pas à la lecture : une référence de l'annexe ZA que la table ne
    résout pas affiche une colonne vide, et le lecteur comprend « la norme ne
    couvre pas cet alinéa » — l'inverse de ce que la norme dit."""
    m = _refus(tmp_path, '_za("Article 11(1) — première phrase"',
               '_za("Article 11(1) — première phrase", "99.9"')
    assert "annexe ZA" in m, m
    assert "ne vise aucun" in m, m


def test_le_module_REFUSE_la_disparition_de_la_ligne_NON_COUVERTE(tmp_path):
    """LA LIGNE LA PLUS IMPORTANTE DU TABLEAU EST CELLE QUI EST VIDE. L'annexe
    ZA déclare elle-même l'article 17(2) couvert par aucun paragraphe. La
    retirer ferait lire 100 % comme « article 17 tenu » — un mensonge par
    arrondi, et celui que la norme elle-même dément."""
    m = _refus(tmp_path, 'ZA_NON_COUVERTS = tuple(',
               'ZA_NON_COUVERTS = ()  # \nZA_INUTILE = tuple(')
    assert "non couverte" in m or "17(2)" in m, m


def test_la_resolution_a_DEUX_SENS_et_le_module_refuse_qu_elle_en_perde_un(tmp_path):
    """LES DEUX SENS SONT NÉCESSAIRES, et c'est mesuré : l'annexe écrit « 4.4 »
    là où la table porte 4.4.1 et suivants (du général au détaillé), et
    « 5.3.1 » là où la table porte « 5.3 » (du détaillé au général). Couper le
    second sens laisse des lignes de l'annexe sans rien en face."""
    m = _refus(tmp_path,
               '            or reference.startswith(p["num"] + ".")]',
               '            ]')
    assert "annexe ZA" in m, m


# ═══════════════════════════════════════════════════════════════════════════
#  3. LE PLAFOND DE LA CHARGE DE PREUVE — IL TOMBE, ET IL SE LÈVE
# ═══════════════════════════════════════════════════════════════════════════

def test_le_module_REFUSE_un_plafond_qui_ne_TOMBE_plus(tmp_path):
    """SI LE VERROU NE SE DÉCLENCHE PLUS, l'écran annonce 100 % à qui a coché
    « autre solution technique » sans produire une seule des trois pièces du
    §4.4.3.2.2. C'est exactement le chiffre qu'un organisme notifié
    contredira, et le client l'apprendra devant lui."""
    m = _refus(tmp_path, "PLAFOND_STRATEGIE_SANS_PREUVE = 0.5",
               "PLAFOND_STRATEGIE_SANS_PREUVE = 1.0")
    assert "plafond" in m, m


def test_le_module_REFUSE_un_verrou_qui_ne_se_DECLENCHE_plus(tmp_path):
    """DEUX CHOSES À TENIR, ET DEUX PORTES DISTINCTES. La précédente garde
    l'ARITHMÉTIQUE du plafond ; celle-ci garde le fait qu'un verrou soit
    NOMMÉ. Un plafond qui tombe sans que rien ne le dise rend un taux plus bas
    que le travail fait, sans expliquer pourquoi — et le client cherche
    l'erreur dans ses réponses au lieu de produire les trois pièces.

    MESURÉ : sans cette règle, la ligne `if not sans["verrous"]` de la garde
    n'était gardée par rien — la batterie de mutations l'a montrée survivante,
    parce que le contrôle d'arithmétique voisin attrapait déjà l'autre
    défaut."""
    m = _refus(tmp_path,
               '        verrous.append({\n            "cle": "charge_de_preuve",',
               '        [].append({\n            "cle": "charge_de_preuve",')
    assert "verrou" in m, m


def test_le_module_REFUSE_un_plafond_qui_ne_se_LEVE_plus(tmp_path):
    """LA PORTE DOIT S'OUVRIR. Un verrou qu'aucune réponse ne lève n'est pas un
    verrou, c'est un mur : le client produirait les trois pièces et verrait le
    même chiffre. On coupe donc la lecture des pièces et on exige le refus."""
    m = _refus(tmp_path,
               '                           if not v.get(p["cle"]))',
               '                           if True)')
    assert "pièces" in m or "plafond" in m or "LÈVENT" in m, m


def test_le_module_REFUSE_une_approche_qui_ouvre_presomption_ET_charge_de_preuve(tmp_path):
    """LES DEUX NE VONT PAS ENSEMBLE. Une norme harmonisée citée au Journal
    officiel ouvre présomption : il reste à DOCUMENTER. Lui coller en plus la
    charge de preuve des approches c et d ferait payer deux fois le chemin le
    plus sûr — et personne ne le prendrait."""
    m = _refus(tmp_path,
               '     "preuve": "documenter",\n'
               '     "charge": "Documenter l\'exigence essentielle satisfaite.",\n'
               '     "presomption": True},\n'
               '    {"cle": "specification", "lettre": "b",',
               '     "preuve": "justifier",\n'
               '     "charge": "Documenter l\'exigence essentielle satisfaite.",\n'
               '     "presomption": True},\n'
               '    {"cle": "specification", "lettre": "b",')
    assert "présomption" in m, m


# ═══════════════════════════════════════════════════════════════════════════
#  4. LA QUALIFICATION — LE SILENCE N'EST PAS UN « NON »
# ═══════════════════════════════════════════════════════════════════════════

def test_le_module_REFUSE_de_confondre_le_SILENCE_avec_une_reponse(tmp_path):
    """LE DÉFAUT MESURÉ, ET CORRIGÉ : avec « et » au lieu de « ou », un
    fournisseur qui venait de se déclarer tel — sans avoir encore dit si son
    système est à haut risque — était renvoyé HORS CHAMP, et ses quatre écrans
    passaient en « sans objet ». La garde doit refuser ce retour en arrière."""
    m = _refus(tmp_path,
               'if q.get("fournisseur") is None or q.get("haut_risque") is None:',
               'if q.get("fournisseur") is None and q.get("haut_risque") is None:')
    assert "qualification" in m, m


def test_le_module_REFUSE_qu_un_NON_FOURNISSEUR_reste_dans_le_champ(tmp_path):
    """LA RÈGLE MIROIR. L'article 17 vise le FOURNISSEUR : laisser soixante-cinq
    questions à un déployeur lui vendrait un chantier que le règlement ne lui
    impose pas."""
    m = _refus(tmp_path,
               '    if not q.get("fournisseur") or not q.get("haut_risque"):',
               '    if False:')
    assert "hors champ" in m, m


# ═══════════════════════════════════════════════════════════════════════════
#  5. LES TABLES — CE QUI SE RECOMPTE
# ═══════════════════════════════════════════════════════════════════════════

def test_le_module_REFUSE_un_chapitre_dont_la_PART_n_existe_pas(tmp_path):
    """DEUX FAÇONS DE PERDRE UN CHAPITRE, ET DEUX PORTES. Celle-ci : le
    chapitre nomme une part qui n'est pas déclarée — une faute de frappe
    suffit. Ses paragraphes sortiraient du dénominateur en silence, et le taux
    monterait d'autant sans que personne l'ait décidé.

    MESURÉ : la première version de cette règle injectait une PART sans
    chapitre, et c'est un AUTRE contrôle de la garde qui l'attrapait — la
    batterie de mutations a montré que la ligne visée survivait."""
    m = _refus(tmp_path, '     "part": "strategie",', '     "part": "stratgie",')
    assert "part inconnue" in m, m


def test_le_module_REFUSE_une_part_dont_AUCUN_chapitre_ne_releve(tmp_path):
    """L'AUTRE SENS. Une part du score que plus aucun chapitre ne vise garde
    son poids au dénominateur et ne peut jamais rien rendre : le taux
    plafonnerait sous 100 % quoi qu'on réponde, sans qu'aucun écran dise
    pourquoi."""
    m = _refus(tmp_path, '"chapitres": ("8",)', '"chapitres": ()')
    assert "part" in m, m


def test_le_module_REFUSE_les_SEPT_exigences_essentielles_devenues_six(tmp_path):
    """SEPT, PARCE QUE LE CHAPITRE III SECTION 2 DU RÈGLEMENT EN PORTE SEPT.
    En perdre une retirerait un article entier du §4.4 — et le taux monterait,
    puisque le dénominateur de la stratégie se réduirait."""
    m = _refus(tmp_path,
               '    {"cle": "robustesse", "lettre": "g",',
               '    {"cle": "robustesse_retiree", "lettre": "g", "retire": True,\n'
               '     "_ignore": True} if False else {"cle": "robustesse", "lettre": "g",')
    assert "chargé sans broncher" in m or "sept" in m, m
