# -*- coding: utf-8 -*-
"""Le rail et le taux de conformité lisent les MÊMES déclarations.

LA DEMANDE : « brancher le taux de conformité sur les mêmes déclarations que
le rail, pour que les deux ne se contredisent plus ».

CE QUI A ÉTÉ MESURÉ AVANT D'ÉCRIRE UNE LIGNE — dans un navigateur, puis sur
le serveur :

  · NIS 2 rempli par ses vrais contrôles jusqu'à trois blocs verts dans le
    rail : la carte NIS 2 du taux affichait « — » ;
  · sept cartes sur onze ne pouvaient RIEN afficher, quoi que l'on remplisse.
    Le taux lisait `window.CONF_DECL`, que quatre modules n'écrivaient
    jamais ; 800-53 et 800-82 l'écrivaient sans être lus ni évalués, et DORA
    n'y figurait pas ;
  · une fois ouvert, le taux ne se recalculait plus de la session : son
    cache vivait dans une fermeture, et la remise à zéro visait une AUTRE
    variable, globale, du même nom ;
  · RGPD « 0 % » sans la moindre déclaration ;
  · les déclarations du rail, données telles quelles au calcul du taux :
    huit refus, et une TypeError qui faisait tomber les onze cartes ;
  · ISO 27001 : un verrou « périmètre absent » que l'écran n'offrait aucun
    moyen de lever — pas même un champ ;
  · NIS 2 hors champ : « 0 % » et dix actions au plan, pendant que le rail
    passait tous ses blocs en « sans objet ».

CE QUE « NE PLUS SE CONTREDIRE » VEUT DIRE, ET CE QUE ÇA NE VEUT PAS DIRE. Le
rail dit « rempli » ; le taux dit « tenu ». Un module entièrement rempli de
réponses défavorables est tout vert au rail et bas au taux, et c'est juste.
Ce qui est une contradiction, et que ces règles attrapent :
  · un bloc vert au rail, et une carte « — » au taux ;
  · un bloc vert au rail, et au taux un verrou ou une réserve qui porte sur
    CE QUE CE BLOC VIENT DE REMPLIR ;
  · « sans objet » d'un côté, un taux de l'autre.
"""
import io
import json
import os
import re
import sys

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RACINE)

import conformite as c  # noqa: E402
import parcours_normes as pn  # noqa: E402
import cra  # noqa: E402
import iso27001  # noqa: E402
import iso42001  # noqa: E402
import nis2  # noqa: E402
import nis2_recyf  # noqa: E402
import nist_ai_rmf  # noqa: E402
import nist_800_53  # noqa: E402
import nist_800_82  # noqa: E402
import owasp_llm  # noqa: E402


def _lire(nom):
    with io.open(os.path.join(_RACINE, nom), encoding="utf-8") as f:
        return f.read()


PAGEJS = _lire("sentinel.page.js")


def _code(src):
    """Le JavaScript sans ses commentaires."""
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", "", src)


CODE = _code(PAGEJS)


# ══════════════════════════════════════════════════════════════════════════
#  LES ÉCRANS — TELS QUE LA PAGE LES TIENT
# ══════════════════════════════════════════════════════════════════════════
#
# LES ÉTATS INITIAUX RECOPIENT CEUX DE LA PAGE, et c'est voulu : une règle ne
# peut pas lancer le navigateur. La recette `recette_taux_rail.js` le lance,
# et vérifie sur l'écran réel qu'avant toute réponse les onze cartes disent
# « — ».

def _vierges():
    return {
        "iso27001": {"perimetre": "",
                     "criteres": {"seuil_acceptation": 6, "etabli_le": "",
                                  "apprecie_le": ""},
                     "risques": [], "mesures": {}, "articles": {}},
        "iso42001": {"mesures": {}, "articles": {}},
        "nis2": {"secteur": None, "effectif": None, "ca_eur": None,
                 "bilan_eur": None, "mesures": {}, "gouvernance": {},
                 "chiffre_affaires": None,
                 "recyf": {"statut": None, "etats": {}}},
        "cra": {"role": {}, "produits": [], "ecarts": {},
                "chiffre_affaires": None},
        "nist_ai_rmf": {"etats": {}},
        "owasp_llm": {"etats": {}},
        "nist_800_53": {"socle": None, "etats": {}},
        "nist_800_82": {"etats": {}},
        "rgpd": {"traitements": [],
                 "briques": {"registre": 0, "pbd": 0, "doc": 0,
                             "sensibilisation": 0}},
        "ia_act": {"audit": {}},
        "dora": {"entite": "", "identifiee_nis2": None, "etats": {},
                 "contrats": [{"fonction_critique": None,
                               "microentreprise": False, "clauses": {}}],
                 "services_critiques": None, "iso27001_certifie": None,
                 "mesures_iso": None},
    }


def _risque():
    return {"nom": "Rançongiciel", "vraisemblance": 3, "consequence": 4,
            "confidentialite": True, "proprietaire": "DSI"}


def _alterne(cles, etats):
    """Des réponses qui ALTERNENT : ni toutes favorables, ni toutes
    défavorables."""
    return {k: etats[i % len(etats)] for i, k in enumerate(cles)}


def _articles(module):
    return _alterne([l["numero"] for ch in module.maturite({})["chapitres"]
                     for l in ch["lignes"]],
                    ("conforme", "partiel", "non_conforme"))


def _liste_repondue(prefixe, reponses, n=6):
    """Une liste d'écran dont CHAQUE question a une réponse — telle que le
    collecteur l'envoie : [{cle, nom, reponse}]."""
    return [{"cle": "%s-%d" % (prefixe, i), "nom": "Question %d" % i,
             "reponse": reponses[i % len(reponses)]} for i in range(n)]


def _aipd_repondue():
    """Neuf critères répondus, dont deux « oui » : l'AIPD est requise, et
    ses trois événements sont cotés."""
    return {"criteres": [{"nom": "Critère %d" % i, "reponse": i < 2}
                         for i in range(9)],
            "evenements": [{"nom": n, "g": 2, "v": 3}
                           for n in ("Accès", "Modification", "Disparition")]}


def _remplis():
    """Chaque écran rempli jusqu'au dernier bloc à remplir — avec des
    réponses MOYENNES, ni toutes favorables ni toutes défavorables : un
    banc où tout est « conforme » ne distingue pas un taux lu d'un taux
    plafonné à cent."""
    return {
        "iso27001": {"perimetre": "SI de production",
                     "criteres": {"seuil_acceptation": 6,
                                  "etabli_le": "2026-01-10",
                                  "apprecie_le": "2026-02-01"},
                     "risques": [_risque()],
                     "mesures": {n: {"decision": "retenue",
                                     "statut": "mise_en_oeuvre",
                                     "justification": "risque R1"}
                                 for n in iso27001.MESURES},
                     "articles": _articles(iso27001)},
        "iso42001": {"mesures": {n: {"decision": "retenue",
                                     "justification": "SoA",
                                     "mise_en_oeuvre": etat}
                                 for n, etat in _alterne(
                                     sorted(iso42001.MESURES),
                                     ("conforme", "partiel")).items()},
                     "articles": _articles(iso42001)},
        "nis2": {"secteur": "energie", "effectif": 300, "ca_eur": 60e6,
                 "bilan_eur": None,
                 "mesures": _alterne([cle for cle, _n, _d in nis2.MESURES],
                                     ("conforme", "partiel")),
                 "gouvernance": {k: "conforme"
                                 for k in nis2.GOUVERNANCE_OBLIGATOIRE},
                 "chiffre_affaires": 60e6,
                 "recyf": {"statut": "essentielle",
                           "etats": {str(o[0]): "engage"
                                     for o in nis2_recyf.OBJECTIFS},
                           "analyse": {"gouvernance": True,
                                       "moyens_alloues": True,
                                       "couverture": False,
                                       "acceptation": True,
                                       "risques_residuels_acceptes": True,
                                       "plan_date_et_responsable": False,
                                       "reexamen": True,
                                       "dernier_reexamen_mois": 12}}},
        "cra": {"role": {"je_concois": True},
                "produits": [{"nom": "Boîtier", "marche_ue": True,
                              "classe": "ordinaire"}],
                "ecarts": _alterne([k for k, _t, _d
                                    in cra.ANNEXE_I_I + cra.ANNEXE_I_II],
                                   ("conforme", "partiel", "absent")),
                "chiffre_affaires": 5e7},
        "nist_ai_rmf": {"etats": _alterne(
            [x["cle"] for x in nist_ai_rmf.CATEGORIES],
            ("prouve", "tenu", "amorce", "absent"))},
        "owasp_llm": {"etats": _alterne([r["cle"] for r in owasp_llm.RISQUES],
                                        ("oui", "partiel", "non"))},
        "nist_800_53": {"socle": "moderate",
                        "etats": _alterne([f[0] for f in nist_800_53.FAMILLES],
                                          ("prouve", "tenu", "amorce"))},
        "nist_800_82": {"etats": _alterne([a["cle"] for a in nist_800_82.AXES],
                                          ("prouve", "tenu", "amorce"))},
        "rgpd": {"traitements": [{"nom": "Paie",
                                  "champs": {k: True for k, _l
                                             in pn.RGPD_CHAMPS_ART30},
                                  "aipd": _aipd_repondue()}],
                 "pbd": _liste_repondue("pbd", ("oui", "non", "sans_objet")),
                 "doc": _liste_repondue("doc", ("en_place", "absent")),
                 "sensibilisation": _liste_repondue(
                     "sens", ("realise", "a_planifier")),
                 "briques": {"registre": 100, "pbd": 40, "doc": 20,
                             "sensibilisation": 0}},
        "ia_act": {"audit": _alterne([p[0] for p in c.AUDIT_IA_ACT],
                                     ("done", "partial", "todo", "na")),
                   "points": [{"cle": p[0], "titre": p[2]}
                              for p in c.AUDIT_IA_ACT]},
        "dora": {"entite": "etablissement_credit", "identifiee_nis2": True,
                 "etats": {"2": "prouve", "3": "amorce"},
                 "contrats": [{"fonction_critique": False,
                               "microentreprise": False,
                               "clauses": {"commune_a": "presente"}}]},
    }


def _taux(ecrans):
    r = c.etat_des_lieux(c.depuis_les_ecrans(json.loads(json.dumps(ecrans))),
                         plafond_actions=999)
    assert r["ok"], r
    return r


def _carte(r, cle):
    return [n for n in r["normes"] if n["cle"] == cle][0]


def _etats_rail(norme, d):
    av = pn.avancement(norme, d)
    return {b["cle"]: b["etat"] for b in av["blocs"]}


# ══════════════════════════════════════════════════════════════════════════
#  1. UN ÉCRAN VIERGE N'EST PAS UNE DÉCLARATION — NI UN ZÉRO
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("norme", sorted(_vierges()))
def test_un_ecran_VIERGE_ne_devient_pas_une_declaration(norme):
    """LES MOTEURS RENDENT 0 % SUR UN QUESTIONNAIRE VIDE, et le moteur NIS 2
    rend même « hors champ » sur un formulaire vierge. Traduire un écran que
    personne n'a touché afficherait un zéro — ou un verdict — que personne
    n'a déclaré. MESURÉ : RGPD « 0 % » avant toute réponse."""
    ecrans = {norme: _vierges()[norme]}
    assert c.depuis_les_ecrans(ecrans) == {}, (
        "l'écran vierge de %s devient une déclaration" % norme)
    carte = _carte(_taux(ecrans), norme)
    assert carte["taux"] is None and not carte["renseigne"], (
        "%s affiche %r avant toute réponse" % (norme, carte["taux"]))


def test_les_ONZE_ecrans_vierges_ensemble_rendent_onze_tirets():
    r = _taux(_vierges())
    assert [n["cle"] for n in r["normes"] if n["taux"] is not None
            or n["renseigne"]] == []
    assert r["plan"] and not r["plan"].get("actions"), (
        "le plan propose des actions sur des écrans que personne n'a ouverts")


# ══════════════════════════════════════════════════════════════════════════
#  2. CE QUE LE RAIL DIT REMPLI, LE TAUX LE VOIT
# ══════════════════════════════════════════════════════════════════════════

RAIL = sorted(pn.BLOCS_PAR_NORME)


def test_les_normes_du_rail_sont_TOUTES_traduites():
    """LE DÉFAUT MESURÉ ÉTAIT UN OUBLI, PAS UN CALCUL. Sept cartes restaient
    « — » parce qu'aucun chemin ne menait de leur écran au taux."""
    assert set(RAIL) | {"dora"} == set(c.TRADUCTEURS) == set(c.EVALUATEURS) \
        == set(c.NORMES_PAR_CLE)


@pytest.mark.parametrize("norme", RAIL + ["dora"])
def test_un_ecran_REMPLI_a_un_taux(norme):
    """LE POINT QUI DÉCIDE. MESURÉ : NIS 2 rempli jusqu'à trois blocs verts,
    et la carte restait « — ». Tout écran que le rail tient pour rempli
    rend désormais une carte chiffrée."""
    ecrans = _remplis()
    d = ecrans[norme]
    if norme != "dora":
        etats = _etats_rail(norme, d)
        saisies = [b["cle"] for b in pn.BLOCS[norme] if b["nature"] == "saisie"]
        pas_vertes = [k for k in saisies if etats[k] != "validee"]
        assert not pas_vertes, (
            "le banc n'est plus complet pour le rail (%s) : cette règle ne "
            "mesurerait plus rien" % pas_vertes)
    carte = _carte(_taux(ecrans), norme)
    assert carte["renseigne"] and carte["taux"] is not None, (
        "%s : le rail est vert, et la carte du taux dit %r — « %s »"
        % (norme, carte["taux"], carte["dit"]))


def test_un_TAUX_LU_n_est_pas_un_taux_plafonne_a_cent():
    """Les réponses du banc sont moyennes : si une traduction perdait les
    réponses et ne gardait que « quelque chose a été dit », les taux
    sortiraient tous à 0 ou tous à 100. Ils sont entre les deux."""
    r = _taux(_remplis())
    for cle in ("iso42001", "nis2", "cra", "nist_ai_rmf", "owasp_llm",
                "nist_800_53", "nist_800_82", "rgpd"):
        t = _carte(r, cle)["taux"]
        assert t is not None and 0 < t < 100, (cle, t)


# ══════════════════════════════════════════════════════════════════════════
#  3. UN BLOC VERT NE LAISSE PAS DE VERROU SUR CE QU'IL A REMPLI
# ══════════════════════════════════════════════════════════════════════════

def test_ISO27001_le_perimetre_du_bloc_vert_leve_le_VERROU():
    """MESURÉ : le moteur s'arrête à « perimetre_absent », le taux en fait
    un verrou qui plafonne la norme à 40 %, et l'écran n'avait AUCUN champ
    pour l'écrire. Le rail le demande désormais, et les deux basculent
    ensemble."""
    e = _remplis()
    e["iso27001"]["perimetre"] = ""
    assert _etats_rail("iso27001", e["iso27001"])["risques"] != "validee"
    carte = _carte(_taux(e), "iso27001")
    assert "perimetre_absent" in {v["cle"] for v in carte["verrous"]}
    e["iso27001"]["perimetre"] = "SI de production"
    assert _etats_rail("iso27001", e["iso27001"])["risques"] == "validee"
    carte = _carte(_taux(e), "iso27001")
    assert "perimetre_absent" not in {v["cle"] for v in carte["verrous"]}, (
        "le bloc est vert, et le taux verrouille encore le périmètre")


@pytest.mark.parametrize("norme", ["iso27001", "iso42001"])
def test_la_declaration_d_applicabilite_VERTE_n_est_jamais_IRRECEVABLE(norme):
    e = _remplis()
    assert _etats_rail(norme, e[norme])["soa"] == "validee"
    verrous = {v["cle"] for v in _carte(_taux(e), norme)["verrous"]}
    assert "soa_irrecevable" not in verrous
    # UNE MESURE SANS JUSTIFICATION : les deux basculent ensemble.
    premiere = sorted(e[norme]["mesures"])[0]
    e[norme]["mesures"][premiere]["justification"] = ""
    assert _etats_rail(norme, e[norme])["soa"] != "validee"
    verrous = {v["cle"] for v in _carte(_taux(e), norme)["verrous"]}
    assert "soa_irrecevable" in verrous


def test_le_role_CRA_se_lit_sur_les_MEMES_reponses():
    """SANS RÉPONSE, le moteur de qualification dit « distributeur » et le
    taux du produit suppose « fabricant ». La réserve « rôle non qualifié »
    doit tomber exactement quand le bloc du rail passe au vert."""
    e = _remplis()
    assert _etats_rail("cra", e["cra"])["role"] == "validee"
    assert not _carte(_taux(e), "cra")["reserves"]
    e["cra"]["role"] = {}
    assert _etats_rail("cra", e["cra"])["role"] != "validee"
    assert "role_absent" in {x["cle"] for x in _carte(_taux(e), "cra")["reserves"]}


# ══════════════════════════════════════════════════════════════════════════
#  4. NIS 2 — LA QUALIFICATION SE LIT UNE FOIS, ET « HORS CHAMP » N'EST
#     PAS UN ZÉRO
# ══════════════════════════════════════════════════════════════════════════

def _nis2(**qualification):
    e = _remplis()
    for k in ("secteur", "effectif", "ca_eur", "bilan_eur"):
        e["nis2"][k] = None
    e["nis2"].update(qualification)
    return e


@pytest.mark.parametrize("qualification", [
    pytest.param({}, id="aucun-secteur"),
    pytest.param({"secteur": "energie"}, id="secteur-sans-taille"),
])
def test_une_qualification_INCOMPLETE_est_une_reserve_pas_un_hors_champ(qualification):
    """LE PIÈGE MESURÉ SUR LE MOTEUR : sans secteur, il répond « hors champ ».
    Le lire aurait fait dire au taux « sans objet » à qui a répondu aux dix
    mesures sans avoir encore choisi son secteur — pendant que le rail lui
    dit qu'il manque le secteur."""
    e = _nis2(**qualification)
    assert _etats_rail("nis2", e["nis2"])["qualifier"] != "validee"
    carte = _carte(_taux(e), "nis2")
    assert not carte.get("sans_objet"), "un formulaire incomplet passe hors champ"
    assert carte["taux"] is not None
    assert "non_qualifie" in {x["cle"] for x in carte["reserves"]}


def test_une_qualification_COMPLETE_leve_la_reserve():
    e = _nis2(secteur="energie", effectif=300, ca_eur=60e6)
    assert _etats_rail("nis2", e["nis2"])["qualifier"] == "validee"
    assert not _carte(_taux(e), "nis2")["reserves"]


@pytest.mark.parametrize("qualification", [
    pytest.param({"secteur": pn.SECTEUR_HORS_ANNEXES}, id="aucune-annexe"),
    pytest.param({"secteur": "energie", "effectif": 10, "ca_eur": 1e6,
                  "bilan_eur": 1e6}, id="petite-entreprise"),
])
def test_HORS_CHAMP_au_rail_c_est_SANS_OBJET_au_taux(qualification):
    """MESURÉ : « 0 % », dix écarts et dix actions au plan pour une entité
    que la directive ne vise pas — le chantier que le module NIS 2 refuse
    justement de vendre à une entreprise hors champ."""
    e = _nis2(**qualification)
    etats = _etats_rail("nis2", e["nis2"])
    assert etats["qualifier"] == "validee"
    assert etats["mesures"] == "sans_objet", etats
    r = _taux(e)
    carte = _carte(r, "nis2")
    assert carte.get("sans_objet") and carte["taux"] is None, carte
    assert carte["renseigne"], "« sans objet » se lirait « pas encore regardé »"
    assert carte["ecarts"] == 0
    actions = [a for a in r["plan"]["actions"] if "nis2" in a["normes"]]
    assert not actions, "le plan vend encore un chantier NIS 2 : %s" % actions


# ══════════════════════════════════════════════════════════════════════════
#  5. CE QUE LA TRADUCTION PORTE — ET CE QU'ELLE N'INVENTE PAS
# ══════════════════════════════════════════════════════════════════════════

def test_le_NOM_exige_par_les_moteurs_n_entre_dans_AUCUN_taux(monkeypatch):
    """Quatre moteurs refusent d'évaluer sans nom ; le taux n'en affiche
    rien. S'il en dépendait, ce serait une donnée inventée qui compte."""
    avant = {n["cle"]: (n["taux"], n["brut"]) for n in _taux(_remplis())["normes"]}
    monkeypatch.setattr(c, "NOM_INERTE", "Tout autre nom")
    apres = {n["cle"]: (n["taux"], n["brut"]) for n in _taux(_remplis())["normes"]}
    assert avant == apres


def test_la_surcharge_800_82_se_mesure_CONTRE_son_socle_800_53():
    """LA TRADUCTION PORTE LE SOCLE AVEC LA SURCHARGE. Un axe industriel
    déclaré prouvé au-dessus de familles 800-53 absentes est ramené à elles
    par le moteur ; si le socle se perdait en route, le taux 800-82
    monterait exactement là où le module signale un défaut."""
    e = {"nist_800_82": {"etats": {a["cle"]: "prouve"
                                   for a in nist_800_82.AXES}}}
    seul = _carte(_taux(e), "nist_800_82")["taux"]
    e["nist_800_53"] = {"socle": "moderate",
                        "etats": {f[0]: "prouve" for f in nist_800_53.FAMILLES}}
    soutenu = _carte(_taux(e), "nist_800_82")["taux"]
    assert seul is not None and soutenu is not None
    assert seul < soutenu, (
        "le taux 800-82 ne dépend pas du socle 800-53 (%r, %r) : la "
        "traduction ne le transmet plus" % (seul, soutenu))


def test_le_vocabulaire_de_l_AUDIT_IA_ACT():
    points = [p[0] for p in c.AUDIT_IA_ACT[:6]]
    d = c.depuis_les_ecrans({"ia_act": {"audit": dict(zip(
        points, ["done", "partial", "na", "todo", "none", "conforme"]))}})
    # « none » — un point jamais touché dans l'ancien écran — et une valeur
    # inconnue ne sont PAS des réponses : elles ne se traduisent pas, et le
    # moteur compte ces points « non renseignés ».
    assert d["ia_act"] == dict(zip(points, ["tenu", "partiel", "sans_objet",
                                            "absent"]))


@pytest.mark.parametrize("ecran,ouvert", [
    pytest.param({"traitements": [], "briques": {"pbd": 0}}, False, id="rien"),
    pytest.param({"traitements": [{"nom": "Paie", "champs": {}}],
                  "briques": {}}, True, id="un-traitement"),
    pytest.param({"traitements": [], "briques": {"doc": 20}}, True, id="une-brique"),
    pytest.param({"traitements": [], "briques": {"doc": True}}, False,
                 id="un-booleen-n-est-pas-un-pourcentage"),
])
def test_RGPD_ouvert_ou_pas_regarde(ecran, ouvert):
    """UN REGISTRE SANS TRAITEMENT ET TROIS BRIQUES À ZÉRO ne sont pas un
    RGPD « à 0 % », mais un RGPD pas encore regardé. MESURÉ : la carte
    affichait « 0 % » avant la moindre réponse."""
    assert ("rgpd" in c.depuis_les_ecrans({"rgpd": ecran})) is ouvert


def test_une_brique_RGPD_reste_un_POURCENTAGE():
    d = c.depuis_les_ecrans({"rgpd": {"traitements": [{"nom": "x"}],
                                      "briques": {"registre": 150,
                                                  "pbd": -3, "doc": "40"}}})
    assert d["rgpd"]["briques"] == {"registre": 100, "pbd": 0, "doc": 0,
                                    "sensibilisation": 0}


def test_une_declaration_ILLISIBLE_ne_fait_pas_tomber_les_dix_autres():
    """MESURÉ : l'enveloppe `{"etats": …}` d'un écran, donnée telle quelle au
    moteur NIST AI RMF, levait une TypeError, et l'écran du taux perdait
    ses onze cartes. La carte fautive dit maintenant qu'elle est refusée."""
    r = c.etat_des_lieux({"nist_ai_rmf": {"etats": {"GOVERN 1": "tenu"}},
                          "owasp_llm": {"LLM01": "oui"}})
    assert r["ok"]
    assert _carte(r, "owasp_llm")["taux"] is not None
    fautive = _carte(r, "nist_ai_rmf")
    assert fautive["taux"] is None and "refuse" in fautive["dit"], fautive["dit"]


# ══════════════════════════════════════════════════════════════════════════
#  6. LA GARDE — LE DÉFAUT NE PEUT PAS REVENIR EN SILENCE
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("table,faute", [
    pytest.param("EVALUATEURS", "aucune évaluation", id="evaluateurs"),
    pytest.param("TRADUCTEURS", "aucun traducteur d'écran", id="traducteurs"),
])
def test_la_GARDE_refuse_une_norme_que_le_taux_ne_peut_pas_voir(monkeypatch, table, faute):
    amputee = dict(getattr(c, table))
    amputee.pop("nist_800_53")
    monkeypatch.setattr(c, table, amputee)
    with pytest.raises(RuntimeError) as e:
        c._verifier()
    assert "nist_800_53" in str(e.value) and faute in str(e.value)


def test_la_garde_LAISSE_passer_le_module_intact():
    c._verifier()


# ══════════════════════════════════════════════════════════════════════════
#  7. LA ROUTE ACCEPTE LES ÉCRANS
# ══════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def client():
    os.environ.setdefault("AUTH_MASTER_TOKEN", "recette_locale_idf_0123456789abcdef")
    import app as _app
    _app.app.config["TESTING"] = True
    return _app.app.test_client()


def test_la_route_traduit_les_ECRANS_que_la_page_envoie(client):
    r = client.post("/api/conformite/etat-des-lieux",
                    json={"ecrans": {"nis2": _remplis()["nis2"]}})
    assert r.status_code == 200
    carte = _carte(r.get_json(), "nis2")
    assert carte["renseigne"] and carte["taux"] is not None, carte


def test_la_route_garde_le_format_des_MOTEURS(client):
    r = client.post("/api/conformite/etat-des-lieux",
                    json={"declarations": {"owasp_llm": {"LLM01": "oui"}}})
    assert r.status_code == 200
    assert _carte(r.get_json(), "owasp_llm")["taux"] is not None


# ══════════════════════════════════════════════════════════════════════════
#  8. L'ÉCRAN — UNE COLLECTE, UN CACHE QUI SUIT LES RÉPONSES
# ══════════════════════════════════════════════════════════════════════════

def _fonction(nom):
    i = CODE.index("function %s(" % nom)
    j = CODE.index("\n}", i)
    return CODE[i:j]


def test_le_taux_envoie_la_COLLECTE_DU_RAIL_et_rien_d_autre():
    """UNE SEULE COLLECTE, DEUX LECTEURS. Deux collectes pour les mêmes
    réponses, c'était la garantie que le rail et le taux se contredisent."""
    init = _fonction("confInit")
    assert "window.declarationsDesEcrans()" in init
    assert "JSON.stringify({ecrans: ecrans})" in init
    assert "declarations:" not in init
    assert "CONF_DECL" not in CODE
    collecte = _fonction("declarationsDesEcrans")
    assert "Object.keys(RAIL_DECL)" in collecte, (
        "le taux ne lit plus les collecteurs du rail")
    assert "doraDeclaration()" in collecte, (
        "DORA, qui garde son propre rail, n'est plus transmis au taux")


def _collecteur(norme):
    """Le corps du collecteur du rail pour cette norme, et lui seul."""
    c = CODE[CODE.index("  %s: function () {" % norme):]
    return c[:c.index("\n  },")]


def test_les_collecteurs_du_rail_portent_ce_que_le_taux_lit():
    # DANS LE COLLECTEUR, PAS AILLEURS. La même chaîne figure aussi dans la
    # mémoire des écrans, qui garde le périmètre : chercher dans tout le
    # fichier laissait survivre le collecteur qui l'aurait perdu (M33).
    assert "perimetre: ISO27_ETAT.perimetre" in _collecteur("iso27001")
    rgpd = CODE[CODE.index("  rgpd: function () {"):]
    rgpd = rgpd[:rgpd.index("\n  },")]
    for f in ("confRegPct", "confPbdPct", "confDocPct", "confSensPct"):
        assert "window.%s" % f in rgpd, "la brique %s ne part plus" % f
    ia = CODE[CODE.index("  ia_act: function () {"):]
    ia = ia[:ia.index("\n  }")]
    assert "audit: window.AUDIT_STATE || {}" in ia, "l'audit IA Act ne part plus"
    assert "window.auditPoints()" in ia, (
        "la liste des points ne part plus : le rail ne peut plus nommer ceux "
        "qui attendent une réponse")


def test_le_perimetre_ISO27001_a_ENFIN_un_champ():
    crit = _fonction("iso27RemplirCriteres")
    assert 'id="iso27-perimetre"' in crit
    assert "onchange=\"iso27Perimetre(this.value)\"" in crit
    assert re.search(r"window\.iso27Perimetre = function \(valeur\) \{\s*"
                     r"ISO27_ETAT\.perimetre = ", CODE)
    assert re.search(r"var ISO27_ETAT = \{\s*perimetre: ''", CODE)


def test_le_cache_du_taux_suit_la_VERSION_des_declarations():
    """MESURÉ : une fois ouvert, le taux ne se recalculait plus. Son cache
    vivait dans une fermeture ; la remise à zéro, écrite ailleurs, visait
    une AUTRE variable du même nom."""
    init = _fonction("confInit")
    assert re.search(r"if\(CONF_ETAT && CONF_VERSION === version\)", init)
    assert "var version = window.DECL_VERSION || 0;" in init
    # AUCUNE AFFECTATION DE CONF_ETAT HORS DE LA FERMETURE QUI LE DÉCLARE.
    lignes = PAGEJS.split("\n")
    decl = [i for i, l in enumerate(lignes) if l.startswith("var CONF_ETAT")]
    assert len(decl) == 1
    debut = max(i for i in range(decl[0]) if lignes[i].startswith("(function"))
    fin = min(i for i in range(decl[0], len(lignes))
              if lignes[i].startswith("})();"))
    code_lignes = _code(PAGEJS).split("\n")
    hors = [i + 1 for i, l in enumerate(code_lignes)
            if re.search(r"\bCONF_ETAT\s*=[^=]", l) and not debut < i < fin]
    assert not hors, (
        "CONF_ETAT est affecté hors de sa fermeture (lignes %s) : c'est une "
        "autre variable, et le cache du taux n'en saura rien" % hors)


def test_TOUTE_reponse_change_la_version_DORA_compris():
    sur = _fonction("_railSurReponse")
    assert "declarationsChangees();" in sur
    assert sur.index("declarationsChangees();") < sur.index("n !== 'dora'"), (
        "les réponses DORA, que le rail laisse à son moteur, ne changent "
        "plus la version : le taux DORA resterait figé")
    assert "declarationsChangees()" in _fonction("declPublier")


def test_le_taux_attend_le_REFERENTIEL_et_le_REGISTRE_comme_le_rail():
    init = _fonction("confInit")
    assert "window.railPrealables(calculer," in init
    pre = _fonction("railPrealables")
    assert "!RAIL_REF" in pre and "!window.TRAIT_DATA" in pre
    # UN ÉCHEC NE SE RELANCE PAS EN BOUCLE.
    assert "if (ok) railPrealables(apres, echec); else if (echec) echec();" in pre
    ini = _fonction("railInit")
    assert ini.count("attentes.forEach(function (f) { try { f(false); }") == 2, (
        "un échec du référentiel laisse le taux attendre sans fin")


def test_le_registre_du_tableau_de_bord_compte_les_MEMES_champs_que_le_rail():
    """LE VERT DU BLOC « REGISTRE » ET LA BRIQUE « REGISTRE » DU TAUX doivent
    compter les mêmes champs de l'article 30 : sinon le bloc est vert à
    côté d'une brique à 83 %."""
    m = re.search(r"window\.confRegPct = function\(\)\{.*?var champs=\[([^\]]*)\]",
                  CODE, flags=re.S)
    assert m
    js = re.findall(r'"([a-z_]+)"', m.group(1))
    assert js == [k for k, _l in pn.RGPD_CHAMPS_ART30]


def test_la_carte_DIT_sans_objet():
    assert re.search(r"n\.sans_objet \? 'sans objet' :", CODE)


def test_les_reponses_NIST_et_OWASP_d_hier_sont_lues_au_CHARGEMENT():
    """Lues à l'ouverture de leur écran seulement, elles restaient
    invisibles au rail et au taux tant qu'on n'y retournait pas."""
    for decl, cle in (("NIST_DECL", "NIST_CLE_STOCK"),
                      ("OWASP_DECL", "OWASP_CLE_STOCK")):
        i = CODE.index("var %s = _declLire(%s);" % (decl, cle))
        assert CODE.index("var %s = '" % cle) < i


def test_PARTIR_voir_son_taux_annule_le_decompte_des_DEUX_rails():
    """MESURÉ DANS LE NAVIGATEUR : un bloc validé lance quatre secondes de
    décompte vers le bloc suivant ; qui partait voir son taux de conformité
    pendant ce temps y était ramené de force — le rail DORA faisait de même.
    C'est précisément le geste « je remplis, puis je regarde mon taux »."""
    apres = _fonction("railApresGo")
    retour = apres.index("if (!n || n === 'dora') return;")
    assert re.search(r"railAutoAnnuler\(\);", apres[:retour]), (
        "le décompte ne s'annule qu'en allant sur un écran de référentiel")
    assert re.search(r"doraAutoAnnuler\(\);", apres[:retour]), (
        "le décompte DORA survit à la navigation")
    assert "window.__railAutoDepuis = _ecranCourant();" in _fonction("railAutoLancer")
    assert "window.__doraAutoDepuis = " in _fonction("doraAutoLancer")


def test_une_reponse_ANCIENNE_ne_repeint_pas_le_taux():
    """DEUX CALCULS PEUVENT SE CROISER — une réponse donnée pendant qu'un
    calcul est en route —, et le plus ancien peut revenir le dernier. Il
    repeindrait alors des taux que les réponses ont déjà dépassés : la
    contradiction même que ce branchement supprime. La course a été MESURÉE
    sur l'écran ReCyF, bâti de la même façon."""
    init = _fonction("confInit")
    assert "var demande = ++CONF_DEMANDE;" in init
    assert init.count("if(demande !== CONF_DEMANDE) return;") == 2, (
        "une réponse ancienne — ou son échec — repeint encore l'écran")
