# -*- coding: utf-8 -*-
"""CE QUE LES DEUX RÈGLEMENTS SERVENT VRAIMENT — DGA et Data Act, mesurés
sur la CHARGE DES ROUTES et non sur les constantes des modules.

POURQUOI PAS LES CONSTANTES. dga.py et data_act.py portent chacun un
`_verifier()` qui refuse l'import si leurs tables dérivent : quinze
conditions à l'article 12, trois cadres assujettis sur quatre, les deux
nombres de l'article 83 §5 du RGPD. Ces gardes sont bonnes, et elles ne
mesurent qu'une chose : le MODULE. Entre le module et le lecteur il y a une
route, un sérialiseur et un écran — et c'est là que les défauts de ce dépôt
se sont logés. Ces règles lisent donc ce que `/api/dga/referentiel` et
`/api/data-act/referentiel` RENDENT, et ce que `/api/…/evaluer` RÉPOND.

CE QU'ELLES MESURENT, ET QUI N'EST MESURÉ NULLE PART AILLEURS :
  · la qualification commande tout, et « aucune » est une réponse COMPLÈTE
    (HTTP 200, pas 400 : hors champ n'est pas une erreur du client) ;
  · les obligations servies sont celles des qualités déclarées, et d'elles
    seules — servir les 42 du DGA à qui n'en relève d'aucune inventerait un
    chantier ;
  · l'arithmétique de l'article 40 §4, qui EMPRUNTE celle de l'article 83 §5
    du RGPD : le PLUS ÉLEVÉ de 20 000 000 EUR et de 4 % du chiffre d'affaires
    mondial, et AUCUNE réduction pour les PME — l'inverse de l'article 99 §6
    de l'IA Act, et c'est le piège que ce module existe pour désamorcer ;
  · un chapitre que l'article 40 §4 NE DÉSIGNE PAS n'a pas de plafond
    européen : il faut lire « régime national », pas « 20 000 000 EUR » ;
  · le DGA ne prête aucun plafond : son article 34 renvoie au droit national,
    et la charge doit le DIRE au lieu de se taire ;
  · un point non renseigné compte ZÉRO et le dit — un questionnaire vide
    n'est pas une conformité à zéro.
"""
import json
import os
import sys

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RACINE not in sys.path:
    sys.path.insert(0, _RACINE)


@pytest.fixture(scope="module")
def client():
    import app
    app.app.config["TESTING"] = True
    return app.app.test_client()


def _ref(client, route):
    r = client.get(route)
    assert r.status_code == 200, (route, r.status_code)
    j = json.loads(r.data.decode("utf-8"))
    assert j.get("ok") is True, j
    return j["referentiel"]


def _ev(client, route, charge):
    r = client.post(route, json=charge)
    #  HORS CHAMP N'EST PAS UNE ERREUR DU CLIENT. Répondre 400 à « je ne
    #  relève d'aucun cadre » dirait que la question est mal posée, alors que
    #  c'est la réponse la plus fréquente et la plus utile du module.
    assert r.status_code == 200, (route, r.status_code, r.data[:200])
    return json.loads(r.data.decode("utf-8"))


# ══════════════════════════════════════════════════════════════════════════
#  1. LE DGA — CE QUE LA ROUTE REND
# ══════════════════════════════════════════════════════════════════════════

def test_la_charge_du_DGA_porte_les_quatre_cadres_dont_TROIS_assujettissent(client):
    """LA QUALIFICATION COMMANDE TOUT : quatre cadres à l'article 1er §1, et
    trois seulement créent des obligations. Un quatrième assujetti ferait
    proposer un chantier au comité européen de l'innovation."""
    ref = _ref(client, "/api/dga/referentiel")
    cadres = ref["cadres"]
    assert len(cadres) == 4, [c["cle"] for c in cadres]
    assujettis = [c["cle"] for c in cadres if c["assujetti"]]
    assert len(assujettis) == 3, assujettis
    #  CELUI QUI N'ASSUJETTIT PERSONNE LE DIT, dans la charge et pas
    #  seulement dans le module : un écran muet là-dessus laisserait croire
    #  que le comité impose quelque chose à une entreprise.
    #  LA PHRASE EST DANS `quoi`, PAS DANS `qui` : `qui` nomme la personne
    #  visée (« Organe de l'Union »), `quoi` dit ce que le cadre fait — et
    #  c'est là que le comité doit déclarer qu'il n'oblige personne.
    muet = [c["cle"] for c in cadres
            if not c["assujetti"]
            and "obligation" not in (c.get("quoi") or "").lower()]
    assert not muet, muet
    for c in cadres:
        assert c.get("article", "").startswith("art. 1er §1"), c


def test_la_charge_du_DGA_porte_les_quinze_conditions_lettrees_a_a_o(client):
    """LES QUINZE CONDITIONS DE L'ARTICLE 12, et leurs lettres. Une condition
    perdue en route, c'est un point qu'aucun écran ne demandera jamais."""
    ref = _ref(client, "/api/dga/referentiel")
    cond = ref["conditions_art12"]
    assert len(cond) == 15, len(cond)
    lettres = [c["lettre"] for c in cond]
    assert lettres == list("abcdefghijklmno"), lettres
    assert all((c.get("quoi") or "").strip() for c in cond), lettres


def test_la_charge_du_DGA_DIT_qu_elle_ne_chiffre_aucune_amende(client):
    """L'ARTICLE 34 RENVOIE AU DROIT NATIONAL, et la charge doit le DIRE.
    Un écran muet sur l'exposition laisserait croire qu'elle est nulle —
    c'est l'inverse : elle est seulement ailleurs."""
    s = _ref(client, "/api/dga/referentiel")["sanctions"]
    assert s["article"].startswith("art. 34"), s["article"]
    assert s["plafond_ue"] is None, s["plafond_ue"]
    pourquoi = s.get("pourquoi_pas_de_plafond") or ""
    assert len(pourquoi) > 80, pourquoi
    assert "national" in pourquoi.lower(), pourquoi


def test_la_charge_du_DGA_porte_les_cinq_points_du_pont_RGPD(client):
    """CINQ DISPOSITIONS, CHACUNE AVEC SON ARTICLE. Le pont doit être LU
    dans le texte, pas supposé : c'est pour cela que chaque point porte
    l'article qui le dit et la conséquence qui en découle."""
    pont = _ref(client, "/api/dga/referentiel")["pont_rgpd"]
    assert len(pont) == 5, [p["cle"] for p in pont]
    for p in pont:
        assert p.get("article", "").startswith("art. "), p
        assert (p.get("dit") or "").strip(), p
        assert (p.get("consequence") or "").strip(), p
    #  LE RÈGLEMENT NE CRÉE AUCUNE BASE LÉGALE, et c'est le point qui évite
    #  qu'un client cherche sa base dans le mauvais texte.
    assert any("base" in (p.get("dit") or "").lower() for p in pont), pont


def test_HORS_CHAMP_est_une_reponse_complete_et_ne_sert_AUCUNE_obligation(client):
    """« AUCUNE DE CES QUALITÉS » EST LA RÉPONSE DE LA PLUPART DES CLIENTS.
    Elle vaut 200, elle le dit en clair, et elle ne sert aucune des 42
    obligations : en servir une seule proposerait un chantier sans objet."""
    j = _ev(client, "/api/dga/evaluer", {"qualites": ["aucune"]})
    assert j["applicable"]["ok"] is False, j["applicable"]
    assert j["applicable"]["cadres"] == [], j["applicable"]["cadres"]
    assert "HORS CHAMP" in j["applicable"]["dit"], j["applicable"]["dit"]
    #  CE QUE « NE SERT AUCUNE OBLIGATION » VEUT DIRE DANS LA CHARGE SERVIE.
    #  `evaluer` ne rend PAS la liste des obligations — l'écran la lit sur
    #  `/referentiel` — mais il rend le DÉNOMINATEUR, et c'est lui qui dit
    #  combien de points le client va se voir demander. Un hors-champ qui
    #  en annoncerait un seul proposerait un chantier sans objet.
    assert j["score"]["attendus"] == 0, j["score"]
    #  ET AUCUN TAUX : « rien à faire » n'est pas « 0 % fait ».
    assert j["score"]["total"] is None, j["score"]
    #  LE NOMBRE SERVI SOUS `obligations` EST CELUI DU RÈGLEMENT ENTIER, et
    #  il ne bouge pas avec la qualification : le confondre avec « ce qu'on
    #  vous demande » est précisément l'erreur que le dénominateur évite.
    assert j["obligations"] == len(_ref(client, "/api/dga/referentiel")["obligations"])


def test_le_DENOMINATEUR_est_celui_de_la_qualite_declaree_et_D_ELLE_SEULE(client):
    """CE QU'ON VOUS DEMANDE EST CE QUE VOTRE QUALITÉ PORTE. Le DGA range
    ses 42 obligations entre quatre qualités ; les attendre toutes d'un
    prestataire d'intermédiation lui ferait répondre pour une organisation
    altruiste qu'il n'est pas, et son taux serait celui d'un métier qui
    n'est pas le sien.

    MESURÉ SUR LE DÉNOMINATEUR ET NON SUR UNE LISTE, parce que c'est le
    dénominateur que la route sert : `evaluer` rend `score.attendus`, et
    l'écran lit la liste des points sur `/referentiel`. Les deux doivent
    donner le même compte, sinon l'écran demande des points qui ne pèsent
    rien, ou en pèse qu'il ne demande pas."""
    ref = _ref(client, "/api/dga/referentiel")
    tout = len(ref["obligations"])
    siennes = [o["cle"] for o in ref["obligations"]
               if o["qualite"] == "intermediaire"]
    j = _ev(client, "/api/dga/evaluer", {"qualites": ["intermediaire"]})
    assert j["score"]["attendus"] == len(siennes), (j["score"], len(siennes))
    assert 0 < len(siennes) < tout, (len(siennes), tout)
    #  ET DEUX QUALITÉS CUMULÉES ADDITIONNENT LEURS POINTS, sans recouvrement :
    #  un organisme public qui est aussi réutilisateur doit voir les deux
    #  séries, et chacune une seule fois.
    autres = [o["cle"] for o in ref["obligations"]
              if o["qualite"] == "organisme_public"]
    j2 = _ev(client, "/api/dga/evaluer",
             {"qualites": ["intermediaire", "organisme_public"]})
    assert j2["score"]["attendus"] == len(set(siennes) | set(autres)), \
        (j2["score"], len(siennes), len(autres))


# ══════════════════════════════════════════════════════════════════════════
#  2. LE DATA ACT — L'ARITHMÉTIQUE EMPRUNTÉE AU RGPD
# ══════════════════════════════════════════════════════════════════════════

def test_la_charge_du_Data_Act_expose_EXACTEMENT_les_chapitres_II_III_et_V(client):
    """L'ARTICLE 40 §4 NE DÉSIGNE QUE TROIS CHAPITRES. En exposer un
    quatrième ferait annoncer un plafond européen là où le régime est
    national ; en retirer un en cacherait un vrai."""
    ref = _ref(client, "/api/data-act/referentiel")
    assert len(ref["chapitres"]) == 6, [c["cle"] for c in ref["chapitres"]]
    exposes = [c["cle"] for c in ref["chapitres"] if c.get("rgpd_art83")]
    assert exposes == ["II", "III", "V"], exposes
    assert ref["sanctions"]["chapitres_exposes"] == ["II", "III", "V"], ref["sanctions"]


def test_la_charge_du_Data_Act_porte_les_DEUX_nombres_de_l_article_83_5(client):
    """20 000 000 EUR, 4 %, LE PLUS ÉLEVÉ, ET AUCUNE RÉDUCTION PME.
    Retenir le plus bas est l'erreur que le calculateur de l'article 99
    avait faite ; accorder une réduction PME serait la même erreur à
    l'envers, et elle rendrait une PME moins exposée qu'elle ne l'est."""
    s = _ref(client, "/api/data-act/referentiel")["sanctions"]
    assert s["fixe"] == 20000000, s["fixe"]
    assert s["part"] == 0.04, s["part"]
    assert s["plus_eleve"] is True, s["plus_eleve"]
    assert s["reduction_pme"] is False, s["reduction_pme"]
    assert "83" in s.get("emprunt", ""), s.get("emprunt")


def test_une_PME_est_PLUS_exposee_ici_que_sous_l_IA_Act(client):
    """LE PIÈGE QUE CE MODULE EXISTE POUR DÉSAMORCER, mesuré sur la charge.
    À 8 M€ de chiffre d'affaires, 4 % font 320 000 EUR : l'article 83 §5
    retient le PLUS ÉLEVÉ, donc 20 000 000 EUR. À 2 Md€, 4 % font
    80 000 000 EUR, et c'est eux qu'on retient."""
    pme = _ev(client, "/api/data-act/evaluer",
              {"qualites": ["fabricant"], "chiffre_affaires": 8000000})["exposition"]
    assert pme["plafond"] == 20000000, pme
    assert pme["motif"] == "art83_5", pme
    grand = _ev(client, "/api/data-act/evaluer",
                {"qualites": ["fabricant"], "chiffre_affaires": 2000000000})["exposition"]
    assert grand["plafond"] == 80000000, grand
    #  ET LA PHRASE LE DIT, parce qu'un chiffre sans sa raison ne se
    #  défend pas en comité.
    assert "aucune réduction" in (pme.get("dit") or "").lower(), pme.get("dit")


def test_un_chapitre_NON_DESIGNE_par_l_article_40_4_n_a_PAS_de_plafond_europeen(client):
    """LE DÉFAUT MESURÉ ICI, ET IL ÉTAIT DANS LA CHARGE SERVIE. Un
    fournisseur de cloud n'ouvre que les chapitres VI et VII — aucun des
    deux n'est désigné par l'article 40 §4. La route annonçait pourtant
    20 000 000 EUR, parce qu'elle passait `chapitre=None` au calcul dès
    qu'aucun chapitre exposé n'était ouvert, et que `None` veut dire « on
    ne sait pas » et non « aucun ». Le lecteur lisait donc le plafond du
    RGPD là où le régime est national — exactement le contresens que
    l'écran du module met en garde contre."""
    j = _ev(client, "/api/data-act/evaluer",
            {"qualites": ["cloud"], "chiffre_affaires": 5000000})
    assert j["chapitres"] and all(c in ("VI", "VII") for c in j["chapitres"]), j["chapitres"]
    expo = j["exposition"]
    assert expo["plafond"] is None, expo
    assert expo["motif"] == "regime_national", expo
    #  ET LA CHARGE DIT POURQUOI, en nommant l'article qui renvoie à l'État
    #  membre : « pas de plafond » sans la raison se lirait « pas de risque ».
    dit = expo.get("dit") or ""
    assert "art. 40" in dit, dit
    assert "aucun plafond europ" in dit.lower(), dit
    assert expo.get("chapitre") in j["chapitres"], expo


def test_la_charge_du_Data_Act_porte_les_dix_clauses_dont_TROIS_sont_abusives(client):
    """ARTICLE 13 : trois clauses abusives au §4, sept PRÉSUMÉES abusives au
    §5. La nuance est juridique et elle décide de la charge de la preuve :
    compter dix clauses « abusives » durcirait le texte."""
    cl = _ref(client, "/api/data-act/referentiel")["clauses_art13"]
    assert len(cl) == 10, len(cl)
    dures = [c["cle"] for c in cl if c["nature"] == "abusive"]
    assert len(dures) == 3, dures
    presumees = [c["cle"] for c in cl if c["nature"] == "presumee"]
    assert len(presumees) == 7, presumees


def test_la_charge_du_Data_Act_situe_chaque_echeance_par_rapport_a_AUJOURD_HUI(client):
    """UNE ÉCHÉANCE QUI NE SE SITUE PAS NE SERT À RIEN. La charge rend le
    jour qu'elle a pris pour référence et, pour chaque échéance, si elle est
    échue — sans quoi un écran dirait « à venir » pour une date passée."""
    j = _ev(client, "/api/data-act/evaluer", {"qualites": ["fabricant"]})
    assert j.get("aujourdhui"), j.keys()
    ech = j["echeances"]
    assert len(ech) == 5, [e["cle"] for e in ech]
    for e in ech:
        assert isinstance(e.get("echue"), bool), e
        assert isinstance(e.get("jours"), int), e
    #  L'APPLICATION DU RÈGLEMENT EST PASSÉE : le 12 septembre 2025 est
    #  derrière nous, et un module qui l'annoncerait « à venir » ferait
    #  planifier ce qui est déjà exigible.
    appli = next(e for e in ech if e["cle"] == "application")
    assert appli["echue"] is True, appli
    #  ET LA DERNIÈRE NE L'EST PAS : les frais de changement ne tombent
    #  qu'au 12 janvier 2027.
    assert any(not e["echue"] for e in ech), ech


# ══════════════════════════════════════════════════════════════════════════
#  3. LES DEUX, ET LA RÈGLE DU TAUX
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("route,qualite", [
    ("/api/dga/evaluer", "intermediaire"),
    ("/api/data-act/evaluer", "fabricant"),
])
def test_un_questionnaire_VIDE_ne_rend_AUCUN_chiffre(client, route, qualite):
    """UN QUESTIONNAIRE VIDE N'EST PAS UNE CONFORMITÉ À ZÉRO : c'est une
    conformité qu'on n'a pas regardée. Rendre 0 % ferait croire à un
    constat là où il n'y a qu'une absence de mesure, et l'indice des seize
    référentiels afficherait ce zéro.

    CETTE RÈGLE PASSAIT POUR RIEN. Elle lisait `score["taux"]`, une clé que
    la charge ne porte pas : `.get` rendait `None`, l'assertion était vraie
    quoi qu'il arrive, et deux mutations qui faisaient rendre 0 % à un
    questionnaire vide y ont survécu. Le nombre servi s'appelle `total`, et
    c'est lui que l'indice lit."""
    j = _ev(client, route, {"qualites": [qualite]})
    assert j["score"]["renseignes"] == 0, j["score"]
    assert j["tete"] == "vide", j["tete"]
    assert j["score"]["total"] is None, j["score"]
    #  ET AUCUNE PART NON PLUS : `conformite` RECOMPOSE le taux de la norme à
    #  partir des parts. Un plafond ou un zéro posé sur le seul total ne lui
    #  parviendrait pas, et l'indice afficherait un autre chiffre que l'écran.
    assert set(j["score"]["parts"]) == {qualite}, j["score"]["parts"]
    assert all(v is None for v in j["score"]["parts"].values()), j["score"]["parts"]
    #  ET LA TÊTE LE DIT EN CLAIR, parce qu'un « — » sans phrase se lit comme
    #  une panne de l'écran.
    assert "pas regard" in j["dit"], j["dit"]


@pytest.mark.parametrize("route,ref_route,qualite", [
    ("/api/dga/evaluer", "/api/dga/referentiel", "intermediaire"),
    ("/api/data-act/evaluer", "/api/data-act/referentiel", "fabricant"),
])
def test_un_point_NON_RENSEIGNE_compte_ZERO_et_le_denominateur_ne_bouge_pas(
        client, route, ref_route, qualite):
    """LE DÉFAUT MESURÉ ICI, ET IL ÉTAIT DANS LES DEUX MOTEURS.

    `_part` ne gardait que les réponses CONNUES et divisait par leur
    nombre. Un prestataire d'intermédiation qui déclarait tenir UN des
    dix-neuf points de sa qualité lisait donc 100 %, et
    `conformite._lire_dga` servait ce 100 % à l'indice des seize
    référentiels : le DGA s'y affichait maîtrisé sur un dix-neuvième de son
    contenu. Les deux moteurs plus anciens nomment ce réglage dans leur
    propre code — `ocde_ia`, puis `en18286` : « sortir du dénominateur ce
    qu'on n'a pas regardé ferait monter le taux à mesure qu'on répond
    MOINS : le pire réglage possible ». Ces deux-ci le faisaient, et le
    commentaire de `dga._part` citait pourtant `ocde_ia` comme autorité.

    CE QUE LA RÈGLE FIXE : un point tenu sur N attendus vaut 100/N, le
    dénominateur ne bouge pas quand on répond, et il ne descend que sur un
    « sans objet » — le seul état qui retire un point du périmètre."""
    ref = _ref(client, ref_route)
    cles = [o["cle"] for o in ref["obligations"] if o["qualite"] == qualite]
    assert len(cles) >= 3, cles

    j0 = _ev(client, route, {"qualites": [qualite]})
    attendus = j0["score"]["attendus"]
    assert attendus == len(cles), (attendus, len(cles))

    j1 = _ev(client, route, {"qualites": [qualite], "reponses": {cles[0]: "tenu"}})
    sc = j1["score"]
    assert sc["renseignes"] == 1, sc
    #  LE DÉNOMINATEUR N'A PAS BOUGÉ…
    assert sc["attendus"] == attendus, (sc, attendus)
    #  …ET LE TAUX EST CELUI D'UN POINT SUR LE PÉRIMÈTRE ENTIER.
    assert sc["total"] == round(100.0 / attendus), (sc, attendus)
    assert sc["total"] < 100, sc

    #  LE SEUL ÉTAT QUI RETIRE UN POINT DU DÉNOMINATEUR EST « SANS OBJET » :
    #  un point que la qualité ne vise pas n'est pas un manquement.
    j2 = _ev(client, route, {"qualites": [qualite],
                             "reponses": {cles[0]: "tenu",
                                          cles[1]: "sans_objet"}})
    assert j2["score"]["attendus"] == attendus - 1, (j2["score"], attendus)
    assert j2["score"]["total"] == round(100.0 / (attendus - 1)), j2["score"]

    #  ET TOUT TENIR FAIT 100 % — le plafond reste atteignable, sinon la
    #  règle ci-dessus se contenterait d'un taux qui ne monte jamais.
    j3 = _ev(client, route, {"qualites": [qualite],
                             "reponses": {c: "tenu" for c in cles}})
    assert j3["score"]["total"] == 100, j3["score"]
    assert j3["score"]["renseignes"] == len(cles), j3["score"]


@pytest.mark.parametrize("route", ["/api/dga/referentiel", "/api/data-act/referentiel"])
def test_AUCUN_des_deux_reglements_ne_promet_de_presomption(client, route):
    """NI CERTIFICATION NI MARQUAGE. Un taux élevé ne vaut aucune
    présomption de conformité, et la charge le dit — c'est la condition
    pour qu'un module de conformité ne se fasse pas passer pour un
    organisme certificateur."""
    ref = _ref(client, route)
    assert ref["presomption"] is False, ref["presomption"]
