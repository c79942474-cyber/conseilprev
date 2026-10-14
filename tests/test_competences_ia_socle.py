# -*- coding: utf-8 -*-
"""RÉFÉRENTIEL DE COMPÉTENCES IA — CE QUE LE MODULE REFUSE DE CHARGER.

POURQUOI UN SECOND FICHIER. `competences_ia` se contrôle à l'import : il
relit ses tables — clés de familles, niveaux dans l'échelle, sections connues
de la nomenclature, plafonds de rôle, formations — puis lève. C'est le bon
endroit : un dépôt où la cible d'une famille est écrite « proteger » dans une
table et « protéger » dans l'autre ne doit pas se déployer. Mais un module
qui lève à l'import EMPÊCHE de collecter tout fichier de règles qui
l'importe : la faute est attrapée, et pourtant aucune règle ne peut la
NOMMER. La batterie de mutations, elle, lit une erreur de collecte comme une
survivante.

CE FICHIER N'IMPORTE DONC PAS LE MODULE. Il prend sa source, y injecte un
défaut précis dans une copie jetable, l'importe là, et vérifie que le refus
nomme ce défaut-là.

LES SIX PORTES QUI COMPTENT, ET POURQUOI CELLES-LÀ :
  · UNE CLÉ DE FAMILLE MAL ORTHOGRAPHIÉE dans une cible — elle serait
    simplement ignorée, et la cible sortirait un cran trop bas sans que rien
    ne le dise ;
  · UN NIVEAU HORS ÉCHELLE — le nom du niveau serait introuvable et l'écran
    afficherait une cible sans nom ;
  · UNE SECTION QUI N'EXISTE PAS dans `secteurs_nace` — son exigence ne
    s'appliquerait jamais, et personne ne le verrait ;
  · UNE EXIGENCE SECTORIELLE SANS RAISON ÉCRITE — elle ne se discuterait
    pas ;
  · UN PLAFOND DE RÔLE ABSENT ou QUI CONTREDIT le rôle — la fonction et le
    secteur passeraient sans borne, ou le rôle serait rabattu sous lui-même ;
  · DEUX SENSIBILISATIONS, OU AUCUNE — la porte d'entrée de qui part de zéro
    serait ambiguë ou fermée.
"""
import io
import os
import subprocess
import sys
import textwrap

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _refus(tmp_path, avant, apres, module="competences_ia"):
    """Le message que le module rend quand on y injecte ce défaut, ou
    « chargé sans broncher » s'il se charge quand même.

    L'ANCRE DOIT ÊTRE UNIQUE : une porte dont on ne trouve plus le montant
    n'est plus une porte, et la règle tombe ici — c'est voulu."""
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
    #  trouvée EN PREMIER. Inversés, on importerait le vrai module.
    code = textwrap.dedent("""
        import sys
        sys.path.insert(0, %r)
        sys.path.insert(0, %r)
        try:
            __import__(%r)
        except RuntimeError as e:
            sys.stdout.write(str(e))
        else:
            sys.stdout.write("(charge sans broncher)")
    """) % (_RACINE, str(d), module)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True,
                       text=True, timeout=180, cwd=_RACINE)
    return (r.stdout or "") + (r.stderr or "")


# ═══════════════════════════════════════════════════════════════════════════
#  LE TÉMOIN — sans lui, aucune règle de ce fichier ne prouverait rien
# ═══════════════════════════════════════════════════════════════════════════

def test_le_module_se_charge_SANS_defaut_injecte(tmp_path):
    """UN MODULE QUI LÈVERAIT TOUJOURS ferait passer chacune des règles
    ci-dessous pour la mauvaise raison."""
    sortie = _refus(tmp_path, '"dirigeant":        {"comprendre": 2',
                    '"dirigeant":        {"comprendre": 2')
    assert "charge sans broncher" in sortie, sortie[:400]


# ═══════════════════════════════════════════════════════════════════════════
#  LES SIX PORTES
# ═══════════════════════════════════════════════════════════════════════════

def test_une_cle_de_famille_MAL_ORTHOGRAPHIEE_est_refusee(tmp_path):
    sortie = _refus(tmp_path, '"dirigeant":        {"comprendre": 2',
                    '"dirigeant":        {"comprandre": 2')
    assert "famille inconnue" in sortie, sortie[:400]
    assert "comprandre" in sortie


def test_un_niveau_HORS_ECHELLE_dans_une_table_est_refuse(tmp_path):
    sortie = _refus(tmp_path, '"juridique":   {"evaluer": 4,',
                    '"juridique":   {"evaluer": 9,')
    assert "hors échelle" in sortie, sortie[:400]
    assert "CIBLE_FONCTION" in sortie


def test_une_section_INCONNUE_de_la_nomenclature_est_refusee(tmp_path):
    sortie = _refus(tmp_path, '    "P": ({"evaluer": 3, "proteger": 3},',
                    '    "ZZ": ({"evaluer": 3, "proteger": 3},')
    assert "n'existe pas dans secteurs_nace" in sortie, sortie[:400]


def test_une_exigence_SECTORIELLE_sans_raison_ecrite_est_refusee(tmp_path):
    sortie = _refus(
        tmp_path,
        '          "Enseignement : production de contenus destinés à des '
        'apprenants, "\n          "dont l\'exactitude engage l\'établissement.")',
        '          "")')
    assert "aucune raison écrite" in sortie, sortie[:400]


def test_un_PLAFOND_de_role_qui_contredit_le_role_est_refuse(tmp_path):
    """LE PLAFOND NE PEUT PAS DESCENDRE SOUS CE QUE LA POPULATION EXIGE
    D'ELLE-MÊME : la population porte le rôle. Un plafond à 2 sur l'expert
    technique, qui exige 5 sur « protéger », rabattrait le rôle sous
    lui-même — et personne ne serait plus jamais visé au niveau 5."""
    sortie = _refus(tmp_path, '"expert_conformite": 5, "expert_technique": 5,',
                    '"expert_conformite": 5, "expert_technique": 2,')
    assert "le plafond contredit le rôle" in sortie, sortie[:400]


def test_un_PLAFOND_de_role_ABSENT_est_refuse(tmp_path):
    """SANS PLAFOND, la fonction et le secteur passeraient sans borne : un
    collaborateur des systèmes d'information ressortirait à « Concevoir ou
    expertiser »."""
    sortie = _refus(tmp_path, '    "collaborateur": 3,\n',
                    '')
    assert "n'a pas de plafond de rôle" in sortie, sortie[:400]
    assert "collaborateur" in sortie


def test_DEUX_sensibilisations_sont_refusees(tmp_path):
    """LA PORTE D'ENTRÉE DE QUI PART DE ZÉRO EST UNIQUE : deux
    sensibilisations laisseraient choisir, et le module n'a aucun élément
    pour trancher."""
    sortie = _refus(
        tmp_path,
        '{"n": 13, "titre_attendu": "Repenser mon processus en IA-first",\n'
        '     "porte": {"appliquer": 3, "interagir": 2}},',
        '{"n": 13, "titre_attendu": "Repenser mon processus en IA-first",\n'
        '     "porte": {"appliquer": 3, "interagir": 2},\n'
        '     "sensibilisation": True},')
    assert "EXACTEMENT une" in sortie, sortie[:400]


def test_AUCUNE_sensibilisation_est_refusee(tmp_path):
    """ZÉRO LAISSERAIT SANS PORTE celui qui part de rien : la nature
    « sensibilisation » serait rendue, et aucune formation ne la servirait."""
    sortie = _refus(tmp_path, '     "sensibilisation": True},',
                    '     },')
    assert "EXACTEMENT une" in sortie, sortie[:400]


def test_une_formation_SANS_titre_attendu_est_refusee(tmp_path):
    """SANS TITRE ATTENDU, aucune règle ne pourrait refuser la dérive du
    catalogue : l'écran proposerait un numéro dont le titre a changé."""
    sortie = _refus(
        tmp_path,
        '{"n": 12, "titre_attendu": "Littératie IA pour les métiers",',
        '{"n": 12, "titre_attendu": "",')
    assert "n'a pas de titre attendu" in sortie, sortie[:400]
