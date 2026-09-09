# -*- coding: utf-8 -*-
"""LA COHÉRENCE DES PARCOURS — mesurée sur l'ORDRE, pas sur la présence.

CE QUE LES RÈGLES EXISTANTES GARDENT DÉJÀ, ET CE QU'ELLES NE VOIENT PAS.
`test_parcours_par_role.py` vérifie qu'un parcours existe, que ses étapes
mènent quelque part, qu'elles disent quoi faire et ce qu'elles apportent.
`test_parcours_couverture.py` vérifie que tout panneau est atteint par au
moins un chemin. Les deux sont vertes depuis des semaines. Aucune ne voyait
qu'un parcours pouvait mener au FinOps ou à l'Empreinte IA SANS PASSER PAR LE
REGISTRE — alors que ces deux panneaux LISENT ce registre et n'ont rien à
afficher sans lui.

LE DÉFAUT QUE CE FICHIER A ATTRAPÉ, ET IL ÉTAIT RÉCENT. `dc_reporting` menait
à « Empreinte IA du parc » sans que le parcours passe par le Registre. Le
lecteur y arrivait sur une couverture de 0 / 0, sans erreur, sans message, et
sans savoir que c'est à lui de déclarer l'inventaire. Une étape morte se voit ;
une étape qui mène à un tableau vide, non.

CE QUE CES RÈGLES GARDENT

  — L'ORDRE DE LECTURE. Le Registre précède ce qui le lit. Un total avant son
    inventaire n'est pas une avance de temps, c'est un chiffre sans base.

  — LE LECTEUR DONT C'EST LE MÉTIER. Un FinOps que le contrôle de gestion ne
    rencontre jamais n'a pas trouvé son lecteur, même s'il est « couvert ».

  — LES CHEMINS NE SE CONFONDENT PAS. Trois parcours qui partagent presque
    toutes leurs étapes n'apprennent rien de plus qu'un seul.
"""
import io
import os
import re

import pytest

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = io.open(os.path.join(RACINE, "sentinel.html"), encoding="utf-8").read()
SRC = io.open(os.path.join(RACINE, "sentinel.page.js"), encoding="utf-8").read()

PANNEAUX = set(re.findall(r'id="p-([a-z0-9-]+)"', PAGE))


def _catalogue():
    """Les parcours, lus dans le VRAI fichier — jamais recopiés ici."""
    d = SRC.index("var GUIDED_PATHS = [")
    f = SRC.index("\n];", d)
    cat = []
    for m in re.split(r"\n  \{\n?\s*id:\s*'", SRC[d:f])[1:]:
        cat.append((m[:m.index("'")], re.findall(r"\{id:\s*'([a-z0-9-]+)'", m)))
    return cat


CATALOGUE = _catalogue()
PAR_ID = dict(CATALOGUE)


def test_le_releve_lit_bien_le_catalogue():
    """Garde-fou : une lecture cassée rendrait tout ce qui suit vert en ne
    mesurant rien — le défaut que ce dépôt a déjà commis ailleurs."""
    assert len(CATALOGUE) >= 22, "parcours relevés : %d" % len(CATALOGUE)
    assert all(e for _, e in CATALOGUE), "un parcours est relevé sans étape"
    assert "registre" in PANNEAUX and "finops" in PANNEAUX


# ══════════════════════════════════════════════════════════════════════════
#  1. LE REGISTRE PRÉCÈDE CE QUI LE LIT
# ══════════════════════════════════════════════════════════════════════════

#: Les panneaux qui n'ont RIEN à afficher tant que le registre est vide, et
#: qui ne le disent qu'une fois qu'on y est. Relevés sur le comportement des
#: panneaux, pas sur une intention : tous deux lisent `systemes_ia`.
LISENT_LE_REGISTRE = ("finops", "empreinte-ia")


@pytest.mark.parametrize("lecteur", LISENT_LE_REGISTRE)
def test_le_REGISTRE_precede_tout_panneau_qui_le_lit(lecteur):
    """LA RÈGLE QUI A ATTRAPÉ `dc_reporting`. Elle mesure une POSITION, pas une
    présence : un parcours qui contient le registre APRÈS le panneau qui le lit
    échoue aussi, parce que le lecteur aura déjà vu le tableau vide.

    Ce n'est pas une préférence de mise en page. Ces deux panneaux calculent
    sur un inventaire déclaré ; sans lui, la couverture vaut zéro et aucun
    chiffre ne s'affiche. Le parcours doit conduire à la déclaration AVANT le
    calcul, sans quoi il conduit à une impasse silencieuse."""
    fautifs = []
    for pid, etapes in CATALOGUE:
        if lecteur not in etapes:
            continue
        i = etapes.index(lecteur)
        avant = etapes[:i]
        if "registre" not in avant:
            fautifs.append("%s (registre %s)" % (
                pid, "absent" if "registre" not in etapes else "placé après"))
    assert not fautifs, (
        "parcours menant à « %s » sans passer d'abord par le Registre : %s.\n"
        "Ce panneau LIT le registre : le lecteur y arrivera sur une couverture "
        "nulle, sans erreur et sans savoir que l'inventaire lui revient."
        % (lecteur, ", ".join(fautifs)))


def test_la_regle_ci_dessus_sait_distinguer_l_ordre_de_la_presence():
    """TÉMOIN NÉGATIF. Sans lui, la règle précédente pourrait se contenter de
    « le registre figure quelque part » et rester verte sur un parcours qui le
    place en dernier. On vérifie ici, sur un catalogue fabriqué, qu'elle
    distingue bien les deux — sinon elle mesurerait autre chose que son nom."""
    def _viole(etapes):
        i = etapes.index("finops")
        return "registre" not in etapes[:i]
    assert _viole(["finops", "registre"]), "l'ordre inverse n'est pas détecté"
    assert _viole(["matrice", "finops"]), "l'absence n'est pas détectée"
    assert not _viole(["registre", "finops"]), "l'ordre correct est refusé"


# ══════════════════════════════════════════════════════════════════════════
#  2. CHAQUE MODULE RENCONTRE LE MÉTIER DONT C'EST LE TRAVAIL
# ══════════════════════════════════════════════════════════════════════════
# CE QUE CETTE TABLE AJOUTE À LA COUVERTURE. Un panneau « couvert » peut ne
# jamais croiser celui dont c'est le métier : avant ce lot, le FinOps n'était
# atteint que par le CDO et le CAIO — ni l'un ni l'autre ne vote le budget.
LECTEUR_ATTENDU = {
    "finops": ["daf_cout_ia", "ceo"],
    "empreinte-ia": ["rse_empreinte_ia", "dc_reporting"],
    "maturite": ["dsi_socle_ia", "risk_manager", "grc_senior"],
}


@pytest.mark.parametrize("panneau,parcours", sorted(LECTEUR_ATTENDU.items()))
def test_le_module_rencontre_le_metier_dont_c_est_le_travail(panneau, parcours):
    manquants = [p for p in parcours if panneau not in PAR_ID.get(p, [])]
    assert not manquants, (
        "le panneau « %s » n'est plus atteint par %s. Soit l'étape a été "
        "retirée, soit le rattachement a changé — et il se redéclare ici."
        % (panneau, ", ".join(manquants)))


# ══════════════════════════════════════════════════════════════════════════
#  3. LES TROIS PARCOURS NEUFS NE SE CONFONDENT PAS
# ══════════════════════════════════════════════════════════════════════════

NEUFS = ("daf_cout_ia", "rse_empreinte_ia", "dsi_socle_ia")


@pytest.mark.parametrize("pid", NEUFS)
def test_le_parcours_neuf_existe_et_est_un_chemin(pid):
    assert pid in PAR_ID, "le parcours %s a disparu du catalogue" % pid
    assert len(PAR_ID[pid]) >= 4, (
        "%s ne compte que %d étape(s)" % (pid, len(PAR_ID[pid])))


def test_les_trois_parcours_neufs_ne_se_recouvrent_pas():
    """S'ils portaient presque les mêmes étapes, les distinguer n'apprendrait
    rien et il aurait fallu en écrire un seul. Ils partagent le Registre —
    c'est justement ce qui en fait une famille — mais chacun doit porter au
    moins deux étapes que les deux autres n'ont pas."""
    for pid in NEUFS:
        autres = set()
        for x in NEUFS:
            if x != pid:
                autres |= set(PAR_ID[x])
        propres = set(PAR_ID[pid]) - autres
        assert len(propres) >= 2, (
            "%s n'a que %d étape(s) qui lui soi(en)t propre(s) : %s — il se "
            "confond avec les deux autres" % (pid, len(propres), sorted(propres)))


def test_chaque_parcours_neuf_porte_LE_module_dont_il_part():
    """Un parcours « ce que l'IA coûte » qui ne mène pas au FinOps porte un
    titre que son contenu ne tient pas."""
    attendu = {"daf_cout_ia": "finops",
               "rse_empreinte_ia": "empreinte-ia",
               "dsi_socle_ia": "maturite"}
    for pid, panneau in attendu.items():
        assert panneau in PAR_ID[pid], (
            "%s ne mène pas à « %s », qui est pourtant son sujet" % (pid, panneau))


def test_le_socle_est_le_POINT_DE_DEPART_du_parcours_DSI():
    """Ce parcours existe parce que la maturité était traversée quatre fois et
    jamais en tête. « Est-on capable de tenir cela » se demande AVANT
    d'inventorier et de chiffrer, sinon on chiffre ce qu'on ne sait pas tenir."""
    assert PAR_ID["dsi_socle_ia"][0] == "maturite", (
        "le parcours DSI ne commence plus par l'audit de maturité mais par "
        "« %s » : il perd ce qui le distingue du CDO et du CAIO"
        % PAR_ID["dsi_socle_ia"][0])


# ══════════════════════════════════════════════════════════════════════════
#  4. LES TROIS SONT RANGÉS, ET LEUR FAMILLE DIT CE QUI LES RÉUNIT
# ══════════════════════════════════════════════════════════════════════════

def test_les_trois_parcours_neufs_sont_dans_UNE_SEULE_famille_declaree():
    """Un parcours absent des familles retombe dans « Autres parcours » : il
    existe, il fonctionne, et personne ne le trouve."""
    d = SRC.index("var GP_FAMILLES = [")
    f = SRC.index("\n];", d)
    bloc = SRC[d:f]
    familles = re.findall(r"titre:\s*'((?:[^'\\]|\\.)*)'[^}]*?ids:\s*\[([^\]]*)\]",
                          bloc, re.S)
    ou = {}
    for titre, ids in familles:
        for i in re.findall(r"'([a-z_0-9]+)'", ids):
            ou.setdefault(i, []).append(titre)
    for pid in NEUFS:
        assert pid in ou, (
            "%s n'est dans aucune famille : il tombera dans « Autres "
            "parcours », où on ne le cherchera pas" % pid)
        assert len(ou[pid]) == 1, (
            "%s est rangé dans %d familles : %s" % (pid, len(ou[pid]), ou[pid]))
    assert len({ou[p][0] for p in NEUFS}) == 1, (
        "les trois parcours neufs sont dispersés dans %s — ils lisent le même "
        "inventaire, c'est ce qui en fait une famille"
        % {ou[p][0] for p in NEUFS})
