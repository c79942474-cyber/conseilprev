# -*- coding: utf-8 -*-
"""L'EMPREINTE DU PARC — la couture entre le registre et le moteur.

CE FICHIER N'EST PAS UN JUMEAU, et c'est délibéré : il garde ce qui n'existe
que dans Sentinel — la colonne du registre, le normalisateur qui la remplit, et
la route qui la lit. Le moteur, lui, est gardé par `tests/test_empreinte_ia.py`,
qui est copié à l'identique dans les deux dépôts.

CE QUE CES RÈGLES GARDENT

  — LA DÉCLARATION N'EST PAS COMPLÉTÉE. Un ajustement fin partiel reste
    partiel : le boucher avec des valeurs par défaut ferait disparaître le
    manque du relevé de couverture, et un parc à moitié déclaré paraîtrait
    complet.

  — LES DEUX CHEMINS D'ÉCRITURE FILTRENT PAREIL. Création et mise à jour
    passent par le même normalisateur. Deux filtres différents, c'est un
    registre dont le contenu dépend de la façon dont il a été rempli.

  — LA ROUTE EST AUSSI FERMÉE QUE LE REGISTRE QU'ELLE LIT. La laisser plus
    ouverte ouvrirait par la bande ce que l'autre ferme.
"""
import io
import json
import os
import re
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import empreinte_ia as E                                            # noqa: E402

SOURCE = io.open(os.path.join(ICI, "app.py"), encoding="utf-8").read()


def _app():
    import app
    return app


# ═══════════════════════════════════════════════════════════════════════════
#  1. LA COLONNE
# ═══════════════════════════════════════════════════════════════════════════

def test_la_colonne_est_ajoutee_par_un_appel_LITTERAL():
    """LA RAISON EST ÉCRITE DANS app.py, six lignes plus haut : la recette
    reconstruit la table en lisant les appels à `registre_ajouter_colonne` avec
    un nom de colonne littéral. Une colonne ajoutée par une variable n'existe
    pas pour elle, et l'INSERT tombe."""
    assert re.search(r"registre_ajouter_colonne\(cur, 'systemes_ia', "
                     r"'ajustement_fin', \"TEXT\"\)", SOURCE)


def test_UNE_colonne_et_pas_cinq():
    """Cinq colonnes auraient multiplié par cinq les points de couture — INSERT,
    UPDATE, sérialisation, recette —, chacun dédoublé entre PostgreSQL et
    SQLite, pour une valeur qui se lit et s'écrit toujours d'un bloc."""
    for champ in E.A_DECLARER_FIN:
        assert not re.search(r"registre_ajouter_colonne\(cur, 'systemes_ia', "
                             r"'%s'" % champ, SOURCE), champ


def test_la_colonne_est_rendue_en_DICTIONNAIRE_jamais_en_chaine():
    """Le moteur attend un objet ; une chaîne y passerait pour une déclaration
    vide, et la campagne d'entraînement disparaîtrait du bilan sans bruit."""
    app = _app()
    for brut in ('{"pue": 1.2}', "", None, "pas du json", "[1,2]"):
        d = app.registre_row_to_dict({
            "id": 1, "nom": "x", "finalite": "", "secteur": "", "type_systeme": "",
            "donnees_utilisees": "", "classification": "", "justification": "",
            "statut_conformite": "", "score_risque": 0, "responsable": "",
            "fournisseur": "", "date_creation": "", "date_maj": "",
            "ajustement_fin": brut})
        assert isinstance(d["ajustement_fin"], dict), brut


# ═══════════════════════════════════════════════════════════════════════════
#  2. LE NORMALISATEUR
# ═══════════════════════════════════════════════════════════════════════════

COMPLET = {"heures_accelerateur": 512, "nombre_accelerateurs": 8,
           "puissance_w": 700, "pue": 1.2, "amorti_mois": 24}


def test_seuls_les_champs_DECLARES_par_le_moteur_entrent_en_base():
    """Accepter des clés arbitraires ferait entrer dans le registre — donc dans
    un livrable — des données que personne n'a spécifiées et qu'aucune règle ne
    mesure."""
    app = _app()
    # LES INTRUS SONT DES NOMBRES, ET C'EST TOUT L'INTÉRÊT. La première version
    # passait « mot_de_passe: secret » : la conversion en flottant l'écartait
    # d'elle-même, et la règle était verte sans que la liste blanche serve à
    # rien — une mutation qui la supprimait a survécu. Un intrus numérique,
    # lui, franchit la conversion et n'est arrêté QUE par la liste.
    lu = json.loads(app._registre_ajustement_fin(
        dict(COMPLET, budget_mensuel=4200, latence_ms=120, score=3.5,
             mot_de_passe="secret")))
    assert set(lu) == set(E.A_DECLARER_FIN), (
        "des clés non déclarées sont entrées : %s"
        % sorted(set(lu) - set(E.A_DECLARER_FIN)))
    for intrus in ("budget_mensuel", "latence_ms", "score", "mot_de_passe"):
        assert intrus not in lu, intrus


def test_une_declaration_partielle_RESTE_partielle():
    """La boucher ici ferait disparaître le manque du relevé de couverture."""
    app = _app()
    lu = json.loads(app._registre_ajustement_fin({"heures_accelerateur": 512}))
    assert lu == {"heures_accelerateur": 512.0}
    assert E.ajustement_fin(lu, 60.0)["nature"] == "incomplet"


@pytest.mark.parametrize("brut", ["512 heures", None, [], 42, {"pue": "beaucoup"}])
def test_une_declaration_illisible_ne_fait_pas_tomber_la_route(brut):
    app = _app()
    assert app._registre_ajustement_fin(brut) == "" or json.loads(
        app._registre_ajustement_fin(brut)) != {"pue": "beaucoup"}


def test_les_DEUX_chemins_d_ecriture_passent_par_le_MEME_normalisateur():
    """Deux filtres différents, c'est un registre dont le contenu dépend de la
    façon dont il a été rempli — et l'un des deux qu'on oublie de corriger."""
    creation = re.search(r"def registre_create.*?\ndef _registre_ajustement_fin",
                         SOURCE, re.S)
    maj = re.search(r"def registre_update.*?\n@app\.route", SOURCE, re.S)
    assert creation and maj
    # ON MESURE QUE C'EST BIEN LA CHARGE ENTRANTE QUI EST NORMALISÉE. La
    # première version cherchait le nom de la fonction n'importe où dans le
    # bloc de mise à jour — et il y figure aussi pour relire l'existant. Une
    # mutation qui remplaçait la normalisation de l'entrée par un json.dumps
    # brut a donc survécu.
    entrant = "_registre_ajustement_fin(data.get('ajustement_fin'))"
    assert entrant in creation.group(0), (
        "la création ne normalise pas la déclaration reçue")
    assert entrant in maj.group(0), (
        "la mise à jour ne normalise pas la déclaration reçue")


def test_la_mise_a_jour_CONSERVE_une_declaration_non_fournie():
    """Un client qui met à jour le nom d'un système ne doit pas perdre sa
    déclaration d'entraînement au passage."""
    maj = re.search(r"def registre_update.*?\n@app\.route", SOURCE, re.S).group(0)
    assert "if data.get('ajustement_fin') is not None else None" in maj
    assert "fin_final = (fin_json if fin_json is not None" in maj


# ═══════════════════════════════════════════════════════════════════════════
#  3. LA ROUTE
# ═══════════════════════════════════════════════════════════════════════════

def test_la_route_est_reservee_comme_le_registre_qu_elle_lit():
    bloc = re.search(r"@app\.route\('/api/empreinte/parc'.*?\ndef empreinte_parc",
                     SOURCE, re.S)
    assert bloc, "la route /api/empreinte/parc est introuvable"
    assert "@require_paid_plan" in bloc.group(0)
    assert "@rate_limit" in bloc.group(0)


def test_la_route_PASSE_les_intensites_au_lieu_de_les_faire_relever():
    """Un moteur de calcul qui interroge RTE au milieu de son arithmétique ne se
    teste pas, il se moque. Le relevé — avec son cache et sa tâche de fond —
    reste ici ; le module reçoit des nombres."""
    corps = re.search(r"def empreinte_parc\(\):.*?\n@app\.route", SOURCE, re.S).group(0)
    assert "_emp_intensite(" in corps and "_emp_intensite_hebergement()" in corps
    assert "empreinte_ia.parc(systemes, intensite, int_heb" in corps


def test_la_route_rend_la_couverture_et_ce_qui_manque_AVANT_les_totaux():
    corps = re.search(r"def empreinte_parc\(\):.*?\n@app\.route", SOURCE, re.S).group(0)
    assert "empreinte_ia.parc(" in corps
    r = E.parc([{"nom": "A", "modele": "claude", "volume_sortie_mois": "1000"},
                {"nom": "B", "modele": "claude"}], 60.0, 380.0)
    assert list(r)[0] == "couverture"
    assert r["couverture"]["volume_manquant"] == ["B"]


def test_la_route_sert_les_facteurs_AVEC_leur_source():
    """Un total sans ses facteurs n'est pas auditable : le lecteur ne peut pas
    savoir d'où vient le nombre qu'on lui montre."""
    corps = re.search(r"def empreinte_parc\(\):.*?\n@app\.route", SOURCE, re.S).group(0)
    assert "'facteurs': empreinte_ia.FACTEURS" in corps
    assert "'scenarios_source': empreinte_ia.SCENARIOS_SOURCE" in corps
    assert "'etat_module': empreinte_ia.etat()" in corps
    for f in E.FACTEURS.values():
        assert f["source"] and f["nature"]


#: Chaque constante d'app.py, et l'expression du module dont elle DOIT venir.
LUES_DU_MODULE = [
    ("EMP_WH_1K", "empreinte_ia.WH_1K_JETONS"),
    ("EMP_MODELES", "empreinte_ia.PROFILS_MODELE"),
    ("EMP_FABRICATION_PCT", "empreinte_ia.FACTEURS['fabrication_pct']['valeur']"),
    ("EMP_HEBERGEMENT_WH_REQ",
     "empreinte_ia.FACTEURS['hebergement_wh_req']['valeur']"),
    ("EMP_RESEAU_KWH_GO", "empreinte_ia.FACTEURS['reseau_kwh_go']['valeur']"),
]


def test_les_facteurs_d_app_py_sont_LUS_dans_le_module_et_non_redeclares():
    """LE DOUBLON QUE CETTE RÈGLE FERME. Ces constantes vivaient ici : un PUE
    par modèle, une intensité par pays, une majoration de fabrication, un
    kWh/Go — invisibles du site cyber qui publie les siennes avec leur source,
    et intestables sans importer une application Flask complète.

    ELLE MESURE LA LIAISON, PAS L'IDENTITÉ D'OBJET. La première version
    comparait `app.EMP_WH_1K is E.WH_1K_JETONS`. C'était juste lancée seule et
    faux dans la suite : `tests/test_empreinte_ia.py` recharge le module pour
    éprouver la garde d'import, et un rechargement relie le nom à un NOUVEAU
    dictionnaire pendant qu'app.py tient encore l'ancien. La règle dépendait
    donc de l'ordre des fichiers, pas de ce qu'elle prétend. Lire la liaison
    dans la source la rend indépendante de l'ordre ET reste ce qui fait tomber
    la recopie : une valeur recollée serait égale, jamais lue du module."""
    app = _app()
    for nom, expression in LUES_DU_MODULE:
        assert re.search(r"^%s = %s$" % (re.escape(nom), re.escape(expression)),
                         SOURCE, re.M), (
            "app.py ne lit plus %s dans le module : la valeur y est redéclarée,\n"
            "et elle redeviendra muette quand celle du module changera" % nom)
        assert hasattr(app, nom), nom
    # La liaison dite, le contenu vérifié : une expression juste qui pointerait
    # sur autre chose passerait la mesure de source.
    assert app.EMP_FABRICATION_PCT == E.FACTEURS["fabrication_pct"]["valeur"]
    assert app.EMP_HEBERGEMENT_WH_REQ == E.FACTEURS["hebergement_wh_req"]["valeur"]
    assert app.EMP_RESEAU_KWH_GO == E.FACTEURS["reseau_kwh_go"]["valeur"]
    assert app.EMP_WH_1K == E.WH_1K_JETONS
    assert app.EMP_MODELES == E.PROFILS_MODELE


def test_le_calcul_d_une_requete_DELEGUE_au_module_sans_changer_un_chiffre():
    """Le déplacement était un refactoring : il ne devait pas bouger un nombre.
    On recalcule ici ce que le module rend, et on exige l'égalité."""
    app = _app()
    r = app._emp_calc("claude", 5000, 800)
    attendu = E.inference("claude", 5000, r["intensite"],
                          app._emp_intensite_hebergement()[0],
                          intensite_fixe=app.EMP_INTENSITE_DEFAUT["US"])
    for cle in ("wh_a", "wh_b", "wh_c", "g_a", "g_b", "g_c", "g_c_min", "g_c_max"):
        assert r[cle] == pytest.approx(attendu[cle]), cle
    assert r["source_intensite"], "la source de l'intensité ne remonte plus"
