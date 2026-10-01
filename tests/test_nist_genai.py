# -*- coding: utf-8 -*-
"""NIST AI 600-1 — CE QUE LE PROFIL FAIT AU TAUX, MESURÉ.

CE QUE CES RÈGLES REFUSENT DE MESURER : le branchement. Qu'une route
réponde 200 et qu'un écran affiche 211 lignes ne dit rien de ce qui compte
ici — à savoir qu'un client qui déclare son système GÉNÉRATIF et ne tient
aucune des actions suggérées voit son taux NIST descendre, et qu'il descend
de la bonne hauteur, et pour les bonnes catégories.

CHAQUE RÈGLE PART DONC D'UN SOCLE CONNU et compare le taux AVANT et APRÈS.
Une règle qui se contenterait de lire `analyse()["taux"]` mesurerait le
moteur avec lui-même.
"""
import io
import json
import os
import re

import pytest

import conformite as c
import nist_ai_rmf as N
import nist_genai as G
import parcours_normes as pn

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: LES DOUZE RISQUES, PAR LEUR NUMÉRO — dérivés, jamais réécrits.
DOUZE = [r["n"] for r in N.RISQUES_GENAI]
#: Un socle où TOUT est prouvé : le cas où le profil a le plus à dire, et
#: celui où une erreur de plafond se verrait le moins si on ne la cherchait
#: pas — un taux qui reste à 100 % ne choque personne.
TOUT_PROUVE = {x["cle"]: "prouve" for x in N.CATEGORIES}


def _taux(declaration):
    """Le taux de la carte NIST, tel que l'écran du taux l'affiche."""
    r = c.etat_des_lieux({"nist_ai_rmf": declaration})
    return [x for x in r["normes"] if x["cle"] == "nist_ai_rmf"][0]


# ══════════════════════════════════════════════════════════════════════════
#  1. LE TAUX CHANGE — ET SEULEMENT QUAND IL DOIT
# ══════════════════════════════════════════════════════════════════════════

def test_le_taux_du_cadre_TOMBE_quand_le_systeme_est_declare_generatif():
    """LA RAISON D'ÊTRE DE TOUT CE MODULE, EN UNE RÈGLE. Le même socle, la
    même déclaration de catégories : seule la qualification change."""
    avant = _taux({"etats": TOUT_PROUVE, "profil": {"genai": False}})
    apres = _taux({"etats": TOUT_PROUVE,
                   "profil": {"genai": True, "risques": DOUZE, "actions": {}}})
    assert avant["taux"] == 100, avant["taux"]
    assert apres["taux"] is not None and apres["taux"] < avant["taux"], (
        "le profil ne fait rien tomber : %r → %r"
        % (avant["taux"], apres["taux"]))
    #  ET IL TOMBE DE LA BONNE HAUTEUR : « amorcé » vaut 1 sur une échelle
    #  qui va à 3. Un plafond qui rendrait 66 % aurait rabattu sur « tenu »,
    #  ce qui laisserait croire que les actions sont partiellement tenues.
    assert apres["taux"] == 33, apres["taux"]


def test_un_systeme_NON_generatif_ne_perd_RIEN():
    """LE PROFIL NE S'APPLIQUE PAS À UN MODÈLE DE SCORING DÉTERMINISTE. Lui
    faire baisser son taux au nom de l'IA générative serait un reproche
    inventé — et celui que le client relèverait en premier."""
    nu = _taux(TOUT_PROUVE)
    non = _taux({"etats": TOUT_PROUVE,
                 "profil": {"genai": False, "risques": DOUZE, "actions": {}}})
    assert nu["taux"] == non["taux"] == 100
    assert not non["reserves"], [x["cle"] for x in non["reserves"]]


def test_toutes_les_actions_TENUES_rendent_le_taux_du_socle():
    """LE PLAFOND EST UN PLAFOND, PAS UNE PÉNALITÉ. Une maison qui tient
    tout ce que le profil demande doit retrouver son taux — sans quoi le
    travail du profil ne rapporterait jamais rien."""
    champ = G.applicables(DOUZE)
    plein = _taux({"etats": TOUT_PROUVE,
                   "profil": {"genai": True, "risques": DOUZE,
                              "actions": {k: "tenue" for k in champ}}})
    assert plein["taux"] == 100, plein["taux"]
    assert plein["ecarts"] == 0


def test_une_couverture_PARTIELLE_plafonne_a_TENU_et_pas_plus_bas():
    """UNE SEULE ACTION TENUE SUFFIT À SORTIR D'« AMORCÉ ». Le plafond a
    trois marches, pas deux : les confondre ferait rendre le même chiffre à
    une maison qui n'a rien fait et à une qui a fait la moitié."""
    une = G.PAR_CATEGORIE["GOVERN 1"][0]
    etats, mvts = G.etats_du_profil(
        TOUT_PROUVE, {"genai": True, "risques": DOUZE,
                      "actions": {une: "tenue"}})
    assert etats["GOVERN 1"] == "tenu", etats["GOVERN 1"]
    #  et les autres catégories, elles, tombent bien à « amorcé »
    assert etats["MAP 1"] == "amorce", etats["MAP 1"]
    bouge = {m["categorie"] for m in mvts}
    assert "GOVERN 1" in bouge and "MAP 1" in bouge


@pytest.mark.parametrize("socle,attendu", [
    pytest.param("absent", "absent", id="absent-reste-absent"),
    pytest.param("amorce", "amorce", id="amorce-reste-amorce"),
    pytest.param("tenu", "tenu", id="tenu-reste-tenu"),
    pytest.param("prouve", "prouve", id="prouve-reste-prouve"),
])
def test_le_plafond_ne_RELEVE_jamais_un_etat_du_socle(socle, attendu):
    """LE PROFIL SUPPOSE LE CADRE, IL NE LE REMPLACE PAS. Tenir les 211
    actions d'AI 600-1 sans avoir de gouvernance IA ne prouve pas la
    gouvernance : un plafond qui relèverait vendrait une couverture que
    personne n'a."""
    champ = G.applicables(DOUZE)
    base = {x["cle"]: socle for x in N.CATEGORIES}
    etats, mvts = G.etats_du_profil(
        base, {"genai": True, "risques": DOUZE,
               "actions": {k: "tenue" for k in champ}})
    assert set(etats.values()) == {attendu}, sorted(set(etats.values()))
    assert not mvts


def test_une_categorie_SANS_OBJET_au_socle_le_reste():
    """ÉCARTER UNE CATÉGORIE EST UNE DÉCISION DÉJÀ PRISE, et déjà
    justifiable. Le profil ne la rouvre pas — il n'a rien à dire sur une
    catégorie dont la maison a déclaré qu'elle ne s'appliquait pas."""
    base = dict(TOUT_PROUVE, **{"GOVERN 1": "sans_objet"})
    etats, _ = G.etats_du_profil(
        base, {"genai": True, "risques": DOUZE, "actions": {}})
    assert etats["GOVERN 1"] == "sans_objet"


# ══════════════════════════════════════════════════════════════════════════
#  2. LE CHAMP — CE QUE LES RISQUES DÉCLARÉS APPELLENT, ET RIEN DE PLUS
# ══════════════════════════════════════════════════════════════════════════

def test_aucun_risque_retenu_ne_plafonne_RIEN():
    """LA RÉPONSE QU'UN AUDITEUR OUVRIRA EN PREMIER. Déclarer un système
    génératif et ne retenir aucun risque revient à dire que la génération
    n'en apporte aucun. Le moteur ne l'invente pas à la place du client — il
    le NOMME, et le taux reste celui du socle."""
    t = _taux({"etats": TOUT_PROUVE,
               "profil": {"genai": True, "risques": [], "actions": {}}})
    assert t["taux"] == 100
    a = G.analyse({"genai": True, "risques": [], "actions": {}})
    assert a["tete"] == "risques_absents"
    assert "aucun" in a["dit"].lower()


def test_l_etiquette_HORS_DES_DOUZE_n_ouvre_aucune_action():
    """« Civil Rights violations » est employée une fois au §3 et n'est
    définie nulle part au §2. La retenir comme un treizième risque ferait
    entrer GV-1.4-002 dans le champ d'un client qui n'a déclaré aucun des
    douze — sur la foi d'une étiquette que le document n'assume pas."""
    assert G.applicables([0]) == []
    assert 0 in G.HORS_DOUZE
    #  ET ELLE RESTE VISIBLE : la masquer aurait fait un compte de risques
    #  qui ne retombe pas sur le document.
    assert len(G.PAR_RISQUE[0]) == 1
    assert G.ACTIONS_PAR_CODE["GV-1.4-002"]["risques"].count(0) == 1


def test_un_risque_retenu_n_appelle_QUE_ses_actions():
    """LE CHAMP SE VÉRIFIE PAR LE BAS : chaque action retenue doit porter au
    moins un des risques déclarés. Un champ trop large ferait plafonner des
    catégories sur des actions que le client n'a pas à tenir."""
    for risque in DOUZE:
        for code in G.applicables([risque]):
            assert risque in G.ACTIONS_PAR_CODE[code]["risques"], (risque, code)
    assert len(G.applicables(DOUZE)) == len(G.ACTIONS)


def test_les_23_sous_categories_sans_action_se_disent_SANS_OBJET_POUR_LE_PROFIL():
    """LA NUANCE QUI DÉCIDE D'UN CHANTIER. « Non couverte » enverrait le
    client travailler là où le NIST n'a rien demandé de particulier pour
    l'IA générative."""
    assert len(G.SOUS_CATEGORIES_SANS_ACTION) == 23
    a = G.analyse({"genai": True, "risques": DOUZE, "actions": {}})
    assert a["sous_categories_sans_action"] == list(G.SOUS_CATEGORIES_SANS_ACTION)
    #  AUCUNE D'ELLES N'EST DANS LA TABLE, et la garde du module le tient
    #  aussi — ici on mesure ce que l'écran REÇOIT.
    for k in a["sous_categories_sans_action"]:
        assert k not in G.PAR_SOUS_CATEGORIE, k


def test_une_action_ECARTEE_sort_du_denominateur_et_se_compte():
    """« SANS OBJET » EST UNE PORTE DE SORTIE, ET UNE PORTE DE SORTIE SE
    VOIT. Elle ne pénalise pas — mais le nombre d'actions écartées part avec
    le taux, parce que chacune se justifie devant un tiers."""
    champ = G.applicables([2])
    a = G.analyse({"genai": True, "risques": [2],
                   "actions": {k: "sans_objet" for k in champ}})
    assert a["couverture"]["ecartees"] == len(champ)
    assert a["couverture"]["portees"] == 0
    assert a["couverture"]["taux"] is None
    assert a["tete"] == "tout_ecarte"
    #  et aucun plafond ne tombe
    etats, mvts = G.etats_du_profil(
        TOUT_PROUVE, {"genai": True, "risques": [2],
                      "actions": {k: "sans_objet" for k in champ}})
    assert not mvts and etats == TOUT_PROUVE


def test_une_action_SANS_REPONSE_n_est_pas_tenue():
    """LE DÉFAUT LE PLUS COURANT DE CE GENRE D'ÉCRAN : un questionnaire vide
    qui rend 100 %. Ici, il rend 0 % — et dit combien de questions n'ont pas
    été ouvertes, ce qui n'est pas la même chose que de les rater."""
    champ = G.applicables([2])
    a = G.analyse({"genai": True, "risques": [2], "actions": {}})
    assert a["couverture"]["taux"] == 0
    assert a["couverture"]["sans_reponse"] == len(champ)
    assert a["couverture"]["non_tenues"] == 0


# ══════════════════════════════════════════════════════════════════════════
#  3. LE PLAN — DÉRIVÉ, ET ORDONNÉ POUR UNE RAISON QUI SE DIT
# ══════════════════════════════════════════════════════════════════════════

def test_le_plan_ne_propose_QUE_des_actions_applicables_et_non_tenues():
    """DEUX ÉTATS SORTENT DU PLAN, ET IL FALLAIT LES DEUX : « tenue »,
    évidemment — et « sans objet », parce que réclamer à un client une
    action qu'il vient d'écarter, c'est lui redemander une décision qu'il a
    déjà prise et justifiée."""
    ordre = G.applicables([2, 8])
    champ = set(ordre)
    tenues = {k: "tenue" for k in ordre[:5]}
    ecartees = {k: "sans_objet" for k in ordre[5:9]}
    refusees = {k: "non_tenue" for k in ordre[9:12]}
    reponses = dict(tenues, **dict(ecartees, **refusees))
    p = G.plan({"genai": True, "risques": [2, 8], "actions": reponses})
    codes = {e["code"] for e in p}
    assert codes <= champ
    assert not (codes & set(tenues)), "une action TENUE est au plan"
    assert not (codes & set(ecartees)), "une action ÉCARTÉE est au plan"
    assert set(refusees) <= codes, "une action refusée a disparu du plan"
    assert len(p) == len(champ) - len(tenues) - len(ecartees)
    #  ET CELLES QU'ON A DÉJÀ REGARDÉES SE SIGNALENT : « pas encore ouverte »
    #  et « regardée, pas en place » ne coûtent pas le même travail.
    vues = {e["code"] for e in p if e["deja_vue"]}
    assert vues == set(refusees), sorted(vues)[:4]


def test_le_plan_place_devant_ce_qui_traite_le_PLUS_de_risques_retenus():
    """TRIER PAR CODE AURAIT RANGÉ LE TRAVAIL PAR NUMÉRO DE PARAGRAPHE, ce
    qui n'est l'ordre de personne. À portée égale, c'est l'ordre du cadre
    qui commande : GOVERN d'abord, parce que le reste en dépend."""
    p = G.plan({"genai": True, "risques": DOUZE, "actions": {}})
    portees = [e["porte"] for e in p]
    assert portees == sorted(portees, reverse=True), portees[:12]
    rang = {f: i for i, f in enumerate(N.ORDRE)}
    for a, b in zip(p, p[1:]):
        if a["porte"] == b["porte"]:
            assert (rang[a["fonction"]], a["code"]) \
                <= (rang[b["fonction"]], b["code"]), (a["code"], b["code"])
    assert p[0]["rang"] == 1 and p[-1]["rang"] == len(p)


def test_le_plan_ne_compte_que_les_risques_RETENUS_dans_sa_portee():
    """UNE ACTION QUI TRAITE SEPT RISQUES DONT UN SEUL EST RETENU ne vaut
    pas mieux qu'une qui en traite un. Compter les sept ferait remonter en
    tête un travail que le client n'a pas à mener."""
    p = G.plan({"genai": True, "risques": [5], "actions": {}})
    assert p, "le risque 5 porte quatre actions"
    for e in p:
        assert e["porte"] == 1 and [r["n"] for r in e["risques"]] == [5]


# ══════════════════════════════════════════════════════════════════════════
#  4. LES ÉCARTS ET LA RÉSERVE — LE TAUX QUI BAISSE DIT POURQUOI
# ══════════════════════════════════════════════════════════════════════════

def test_une_categorie_plafonnee_par_le_profil_devient_un_ECART_qui_le_DIT():
    """UN TAUX QUI BAISSE SANS QU'AUCUNE ACTION NE DISE POURQUOI est le
    pire des deux mondes. L'écart existe, et il renvoie à l'écran du profil
    — pas à celui du cadre, où il n'y a rien à corriger."""
    r = c.etat_des_lieux({"nist_ai_rmf": {
        "etats": TOUT_PROUVE,
        "profil": {"genai": True, "risques": DOUZE, "actions": {}}}})
    ecarts = c.ECARTEURS["nist_ai_rmf"](
        c._ev_nist_ai_rmf({"etats": TOUT_PROUVE,
                           "profil": {"genai": True, "risques": DOUZE,
                                      "actions": {}}}, {}),
        {"etats": TOUT_PROUVE,
         "profil": {"genai": True, "risques": DOUZE, "actions": {}}})
    assert len(ecarts) == 19, len(ecarts)
    assert all("profil IA générative" in e["ou"] for e in ecarts), \
        sorted({e["ou"] for e in ecarts})
    assert r["ok"]


def test_la_RESERVE_du_profil_dit_que_le_nombre_n_est_plus_celui_du_socle():
    """UN POURCENTAGE NE PORTE PAS SON HISTOIRE. Sans cette réserve, 33 %
    se lirait « le cadre est mal tenu » alors qu'il est prouvé de bout en
    bout et plafonné par autre chose."""
    t = _taux({"etats": TOUT_PROUVE,
               "profil": {"genai": True, "risques": DOUZE, "actions": {}}})
    cles = [x["cle"] for x in t["reserves"]]
    assert "profil_genai" in cles, cles
    dite = [x for x in t["reserves"] if x["cle"] == "profil_genai"][0]
    assert "PLAFONNÉ" in dite["dit"]
    assert "amorcé" in dite["porte_sur"] and "tenu" in dite["porte_sur"]
    #  ET CE N'EST PAS UN VERROU : le plafond est déjà DANS la note, et le
    #  compter deux fois baisserait le taux d'autant.
    assert not t["verrous"]
    assert t["brut"] == t["taux"]


def test_un_code_d_action_INCONNU_fait_REFUSER_la_norme_entiere():
    """LE COMPTER « TENU » GONFLERAIT UNE COUVERTURE AVEC UNE ACTION QUI
    N'EXISTE PAS ; l'ignorer laisserait un écran remplir du vide sans le
    savoir. Le module refuse, et la carte le dit."""
    t = _taux({"etats": TOUT_PROUVE,
               "profil": {"genai": True, "risques": [2],
                          "actions": {"GV-9.9-999": "tenue"}}})
    assert t["taux"] is None
    assert "refuse" in t["dit"]
    a = G.analyse({"genai": True, "risques": [2],
                   "actions": {"GV-9.9-999": "tenue"}})
    assert a["motif"] == "actions_inconnues"


def test_un_ETAT_d_action_inconnu_est_refuse_lui_aussi():
    a = G.analyse({"genai": True, "risques": [2],
                   "actions": {G.ACTIONS[0][0]: "peut-être"}})
    assert not a["ok"] and a["motif"] == "etats_inconnus"


def test_une_categorie_que_les_risques_RETENUS_n_appellent_pas_est_SANS_OBJET():
    """DEUX CHEMINS MÈNENT À « SANS OBJET POUR LE PROFIL », et il fallait
    les deux : le NIST n'attache rien à cette catégorie pour l'IA
    générative, OU les risques retenus n'y appellent aucune action. Dans les
    deux cas le profil se tait, et se taire n'est pas reprocher."""
    a = G.analyse({"genai": True, "risques": [5], "actions": {}})
    muettes = a["sans_objet_pour_le_profil"]
    assert muettes, "le risque 5 ne porte que quatre actions : la plupart " \
                    "des catégories n'en reçoivent aucune"
    lignes = {l["cle"]: l for l in a["par_categorie"]}
    for k in muettes:
        assert lignes[k]["applicables"] == 0 and lignes[k]["plafond"] is None
    #  ET AUCUNE CATÉGORIE MUETTE N'EST PLAFONNÉE : c'est la seule chose qui
    #  compte pour le client.
    plafonnees = {m["categorie"] for m in G.etats_du_profil(
        TOUT_PROUVE, {"genai": True, "risques": [5], "actions": {}})[1]}
    assert not (plafonnees & set(muettes))


def test_l_ecran_qui_n_envoie_PAS_son_profil_verrait_son_taux_REMONTER():
    """LE DÉFAUT QUE LE TRADUCTEUR EMPÊCHE. Un socle arrivé sans son profil
    se lit « non génératif » — la seule réponse qui ne plafonne rien. Le
    client verrait son taux remonter à 100 % sans avoir touché une seule
    réponse, ce qui est le pire des deux sens."""
    ecran = {"etats": TOUT_PROUVE,
             "profil": {"genai": True, "risques": DOUZE, "actions": {}}}
    traduit = c.depuis_les_ecrans({"nist_ai_rmf": ecran})["nist_ai_rmf"]
    assert traduit["profil"] == ecran["profil"], traduit
    assert _taux(traduit)["taux"] == 33
    #  la même déclaration amputée de son profil : 100 %, et c'est faux
    assert _taux({"etats": TOUT_PROUVE})["taux"] == 100


def test_les_DEUX_formes_de_declaration_rendent_le_meme_taux():
    """LA COMPATIBILITÉ N'EST PAS UNE POLITESSE. Les dossiers enregistrés
    avant le profil portent la déclaration NIST en dictionnaire d'états nu ;
    la refuser aurait rendu muette la carte de tout client qui n'a pas
    rouvert l'écran depuis."""
    nu = _taux(TOUT_PROUVE)
    enveloppe = _taux({"etats": TOUT_PROUVE})
    assert nu["taux"] == enveloppe["taux"] == 100
    assert nu["ecarts"] == enveloppe["ecarts"] == 0


# ══════════════════════════════════════════════════════════════════════════
#  5. UN SEUL NOMBRE, DEUX CHEMINS — ILS DOIVENT S'ACCORDER
# ══════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def client():
    os.environ.setdefault("AUTH_MASTER_TOKEN",
                          "recette_locale_idf_0123456789abcdef")
    import app as _app
    _app.app.config["TESTING"] = True
    return _app.app.test_client()


def test_la_route_d_evaluation_et_le_TAUX_rendent_le_MEME_plafond(client):
    """DEUX ENDROITS QUI CALCULENT LE MÊME NOMBRE FINISSENT PAR LE CALCULER
    DIFFÉREMMENT. L'écran du cadre afficherait GOVERN 3/3 pendant que la
    carte du taux annoncerait 33 % — le même travail, deux chiffres, et le
    client entre les deux."""
    profil = {"genai": True, "risques": DOUZE, "actions": {}}
    r = client.post("/api/nist-ai-rmf/evaluer",
                    json={"etats": TOUT_PROUVE, "profil": profil})
    assert r.status_code == 200
    j = r.get_json()
    par_la_route = {p["fonction"]: p["note"] for p in j["profils"]}
    ev = c._ev_nist_ai_rmf({"etats": TOUT_PROUVE, "profil": profil}, {})
    par_le_taux = {p["fonction"]: p["note"] for p in ev["profils"]}
    assert par_la_route == par_le_taux
    assert set(par_la_route.values()) == {1.0}, par_la_route


def test_la_route_du_profil_rend_la_table_ET_le_plan(client):
    r = client.get("/api/nist-ai-rmf/profil/referentiel")
    assert r.status_code == 200
    ref = r.get_json()["referentiel"]
    assert len(ref["actions"]) == 211
    assert len(ref["sous_categories_sans_action"]) == 23
    assert ref["certifiable"] is False
    r = client.post("/api/nist-ai-rmf/profil/analyser",
                    json={"profil": {"genai": True, "risques": [5],
                                     "actions": {}},
                          "etats": TOUT_PROUVE, "limite": 2})
    assert r.status_code == 200
    j = r.get_json()
    assert j["analyse"]["champ"] == 4 and len(j["plan"]) == 2


def test_la_route_du_profil_REFUSE_une_declaration_illisible(client):
    r = client.post("/api/nist-ai-rmf/profil/analyser",
                    json={"profil": {"genai": True, "risques": [2],
                                     "actions": {"XX-0.0-000": "tenue"}}})
    assert r.status_code == 400
    assert r.get_json()["motif"] == "actions_inconnues"


# ══════════════════════════════════════════════════════════════════════════
#  6. LE RAIL — LA QUALIFICATION SE DEMANDE, ET LE SILENCE N'EST PAS « NON »
# ══════════════════════════════════════════════════════════════════════════

def test_le_bloc_du_profil_est_une_SAISIE_et_non_une_lecture():
    """IL ÉTAIT UN ÉCRAN DE LECTURE, ET C'ÉTAIT JUSTE TANT QU'IL N'Y AVAIT
    RIEN À RÉPONDRE. Le laisser en lecture aurait fait verdir le rail dès
    qu'on ouvre la page, pour un bloc qui commande le taux."""
    bloc = pn.BLOCS_PAR_NORME["nist_ai_rmf"]["genai"]
    assert bloc["nature"] == "saisie"
    assert "profil" in bloc["prerequis"], bloc["prerequis"]


@pytest.mark.parametrize("profil,attendu", [
    pytest.param(None, 1, id="sans-reponse-une-question"),
    pytest.param({"genai": False}, 0, id="non-generatif-rien-a-faire"),
    pytest.param({"genai": True, "risques": []}, 1, id="generatif-sans-risque"),
])
def test_le_rail_demande_la_QUALIFICATION_avant_tout_le_reste(profil, attendu):
    """LE SILENCE N'EST PAS « NON ». Ranger l'absence de réponse du côté de
    « non génératif » validerait le bloc sans que personne n'ait qualifié le
    système — et « non » est précisément la réponse qui ne plafonne rien."""
    d = {"etats": TOUT_PROUVE}
    if profil is not None:
        d["profil"] = profil
    manque, _, _ = pn.EVALUATEURS["nist_ai_rmf"](d)
    assert len(manque["genai"]) == attendu, manque["genai"]


def test_le_rail_nomme_les_SOUS_CATEGORIES_en_attente_et_pas_les_211_actions():
    """UN RAIL DE CENT CINQUANTE LIGNES NE SE LIT PAS. Il nomme la
    sous-catégorie et compte ses actions ouvertes : c'est là qu'on va, et
    c'est le seul travail du rail."""
    manque, _, _ = pn.EVALUATEURS["nist_ai_rmf"]({
        "etats": TOUT_PROUVE,
        "profil": {"genai": True, "risques": [2, 7], "actions": {}}})
    lignes = manque["genai"]
    champ = G.applicables([2, 7])
    attendues = {G.ACTIONS_PAR_CODE[k]["sous_categorie"] for k in champ}
    assert len(lignes) == len(attendues), (len(lignes), len(attendues))
    assert len(lignes) < len(champ)
    assert all(re.match(r"^(GOVERN|MAP|MEASURE|MANAGE) \d+\.\d+ — \d+ action",
                        l["quoi"]) for l in lignes), lignes[:2]


def test_le_rail_est_VERT_quand_chaque_action_applicable_porte_une_reponse():
    champ = G.applicables([5])
    manque, _, _ = pn.EVALUATEURS["nist_ai_rmf"]({
        "etats": TOUT_PROUVE,
        "profil": {"genai": True, "risques": [5],
                   "actions": {k: "non_tenue" for k in champ}}})
    assert manque["genai"] == []


# ══════════════════════════════════════════════════════════════════════════
#  7. LE DOCUMENT — CE QUI EST REPRIS, ET CE QUI NE L'EST PAS
# ══════════════════════════════════════════════════════════════════════════

def test_la_table_recompte_la_distribution_MESUREE_dans_le_document():
    """LE RELEVÉ EST ÉCRIT À LA MAIN DANS LE MODULE ; ici on vérifie qu'il
    n'a pas été réécrit POUR COLLER à une table modifiée. Les deux côtés
    sont donc relus depuis le document : 211 actions, et le compte par
    fonction qui retombe dessus."""
    assert len(G.ACTIONS) == 211
    assert G.COMPTES_MESURES["actions"] == 211
    assert sum(G.COMPTES_MESURES["fonctions"].values()) == 211
    assert G.COMPTES_MESURES["fonctions"] == {
        "GOVERN": 57, "MAP": 39, "MEASURE": 72, "MANAGE": 43}
    assert (G.COMPTES_MESURES["sous_categories_chargees"]
            + G.COMPTES_MESURES["sous_categories_sans_action"]) == 72
    assert len(N.SOUS_CATEGORIES) == 72


def test_les_TROIS_CONTRADICTIONS_du_document_sont_DECLAREES_et_chiffrees():
    """LES TAIRE AURAIT LAISSÉ CROIRE À UNE TABLE PLUS PROPRE QUE LE
    DOCUMENT. Un lecteur qui recompte les actions d'un risque sur le PDF
    doit retrouver le même nombre que l'écran, ou savoir pourquoi non."""
    par_risque = {r["risque"]: r for r in G.RECONCILIATIONS}
    assert set(par_risque) == {0, 5, 6}
    for n, r in par_risque.items():
        assert len(G.PAR_RISQUE[n]) == r["actions"], (n, r["actions"])
        assert r["pourquoi"] and r["au_paragraphe_3"]
    assert par_risque[0]["au_paragraphe_2"] is None
    assert G.referentiel()["reconciliations"]


def test_AUCUN_enonce_d_action_n_est_RECOPIE_dans_l_ecran():
    """LES 211 ÉNONCÉS N'EXISTENT QU'À UN SEUL ENDROIT. Recopiés dans
    l'écran, ils auraient existé en deux exemplaires — et la garde du module
    n'en garderait qu'un. C'est le même contrôle que pour prEN 18229-3,
    pour une raison différente : ici le risque n'est pas le droit d'auteur
    (le NIST se cite librement), c'est la DIVERGENCE."""
    ecran = ""
    for f in ("sentinel.page.js", "sentinel.html"):
        ecran += io.open(os.path.join(_RACINE, f), encoding="utf-8").read()
    ecran = re.sub(r"\s+", " ", ecran).lower()
    trouves = []
    for code, _sc, texte, _r in G.ACTIONS:
        mots = re.sub(r"\s+", " ", texte).lower().split(" ")
        for i in range(0, max(1, len(mots) - 7)):
            if " ".join(mots[i:i + 8]) in ecran:
                trouves.append(code)
                break
    assert not trouves, "recopiés dans l'écran : %s" % trouves[:6]


def test_la_source_dit_qu_elle_ne_se_certifie_PAS_et_qu_elle_est_un_PROFIL():
    """« CONFORME NIST AI 600-1 » NE VEUT RIEN DIRE, et le profil vaut
    encore moins seul que le cadre : citer le profil sans le cadre en
    dessous, c'est citer le profil de rien."""
    ref = G.referentiel()
    assert ref["certifiable"] is False
    assert ref["source"]["certifiable"] is False
    assert ref["source"]["profil_de"] == "NIST AI 100-1"
    assert "gouvernement des États-Unis" in ref["source"]["droits"]
    assert "AI 100-1" in ref["reserve"]
    a = G.analyse({"genai": True, "risques": DOUZE, "actions": {}})
    assert a["certifiable"] is False
    assert "suggérées" in a["reserve"]


def test_le_profil_n_ouvre_PAS_une_treizieme_norme():
    """LE DOUBLE COMPTAGE QUE CE MODULE ÉVITE. Un tiroir à part aurait fait
    monter DEUX FOIS l'indice du cabinet pour un seul chantier — et la
    moyenne consolidée aurait dilué d'autant les autres normes.

    LE NOMBRE N'EST PLUS ÉPINGLÉ ICI, ET C'EST CE QUI A DÛ CHANGER. La règle
    finissait par « == 12 » : le jour où prEN 18286 est devenue la treizième
    norme, elle est tombée alors que le profil génératif n'y était pour
    rien — elle mesurait sa propre constante. Ce qu'elle doit mesurer est
    que `nist_genai` n'est NULLE PART dans la table des normes, et que le
    nombre annoncé est bien celui de la table."""
    assert "nist_genai" not in c.NORMES_PAR_CLE
    assert "nist_genai" not in [x["cle"] for x in c.NORMES]
    assert c.NORMES_ANNONCEES == len(c.NORMES)
    assert "nist_genai" not in c.COMPOSITIONS
    #  ET IL N'AJOUTE AUCUNE PART à la norme qu'il plafonne : une part de
    #  plus aurait changé le poids de GOVERN sans que personne ne l'ait
    #  décidé.
    assert [x["cle"] for x in c.COMPOSITIONS["nist_ai_rmf"]] \
        == ["govern", "map", "measure", "manage"]


def test_les_deux_tables_de_mutations_visent_des_FICHIERS_DISJOINTS():
    """POURQUOI DEUX TABLES ET NON UNE. Une mutation qui fait LEVER
    `nist_genai` à l'import empêche pytest de COLLECTER tout fichier qui
    l'importe — la règle nommée ne s'exécute donc jamais, et la batterie
    rend « MAL VISÉE » pour huit mutations d'un coup. Le fichier de garde
    n'importe pas le module : il en fait une copie défectueuse dans un
    sous-processus. Mélanger les deux tables ferait revenir ce défaut sans
    qu'aucune règle ne le dise."""
    tables = {}
    for nom in ("nist_genai", "nist_genai_socle"):
        with io.open(os.path.join(_RACINE, "tests", "mutations_%s.json" % nom),
                     encoding="utf-8") as f:
            tables[nom] = json.load(f)
    assert tables["nist_genai"]["cibles"] == ["tests/test_nist_genai.py"]
    assert tables["nist_genai_socle"]["cibles"] == \
        ["tests/test_nist_genai_socle.py"]
    src = io.open(os.path.join(_RACINE, "tests",
                               "test_nist_genai_socle.py"),
                  encoding="utf-8").read()
    assert not re.search(r"(?m)^import nist_genai\b", src), (
        "le fichier de garde importe le module qu'il éprouve : ses règles "
        "ne pourront plus être collectées quand il lèvera")
    #  ET AUCUNE MUTATION DE LA TABLE DE COMPORTEMENT NE DOIT FAIRE LEVER LA
    #  GARDE — sinon elle serait « mal visée » elle aussi.
    ancres = {m["avant"] for m in tables["nist_genai"]["mutations"]
              if m["fichier"] == "nist_genai.py"}
    garde = io.open(os.path.join(_RACINE, "nist_genai.py"),
                    encoding="utf-8").read().split("def _verifier():")[1]
    for a in ancres:
        assert a not in garde, (
            "une mutation de comportement touche la GARDE : %r" % a[:60])
