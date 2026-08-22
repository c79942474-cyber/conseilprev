"""CE QUE LE SITE RÉPOND — pas seulement ce qu'il affiche.

Deux défauts constatés au navigateur ont motivé ce fichier, et tous deux
avaient la même forme : la page écrivait une chose, le protocole en disait
une autre. Un lecteur humain voyait le bon texte ; tout ce qui lit sans yeux
— moteur d'indexation, lien archivé, surveillance, autre programme —
enregistrait le contraire.

  1. UNE LISTE COUPÉE DOIT LE DIRE. Annoncer « 66 fiches retenues » en en
     servant 60, sans rien signaler, apprend au lecteur qu'il tient tout le
     corpus filtré.
  2. UNE ADRESSE QUI N'EXISTE PAS DOIT RÉPONDRE 404. Elle rendait « 200 OK »
     tout en affichant « Fiche introuvable ».
"""
import os
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import pytest  # noqa: E402

import app as A  # noqa: E402
import veille as V  # noqa: E402


@pytest.fixture()
def client():
    A.app.config["TESTING"] = True
    with A.app.test_client() as c:
        yield c


def _un_id_publie():
    pub = V.publiables(A.corpus())
    if not pub:
        pytest.skip("corpus vide : rien à interroger")
    return pub[0]["id"]


# ── 1. Une liste coupée le dit ────────────────────────────────────────────

def test_une_liste_coupee_l_annonce():
    """La coupe vient du SERVEUR, qui la déclare — le client ne la déduit pas
    de deux nombres, sans quoi la règle vivrait à deux endroits et l'un des
    deux finirait faux."""
    A.app.config["TESTING"] = True
    with A.app.test_client() as c:
        d = c.get("/api/veille?n=3").get_json()
    assert d["ok"] and d["tronque"] is True
    assert len(d["fiches"]) == 3 and d["affichees"] == 3
    assert d["total"] > 3
    assert str(d["total"]) in d["tronque_dit"]
    assert "coupée" in d["tronque_dit"]


def test_une_liste_entiere_n_annonce_aucune_coupe(client):
    d = client.get("/api/veille?n=200").get_json()
    assert d["tronque"] is False and d["tronque_dit"] == ""
    assert d["affichees"] == d["total"] == len(d["fiches"])


def test_le_plafond_ne_depasse_jamais_ce_qui_est_demande(client):
    for n in (1, 5, 60):
        d = client.get("/api/veille?n=%d" % n).get_json()
        assert len(d["fiches"]) <= n, n


def test_un_plafond_absurde_ne_fait_pas_tomber_la_veille(client):
    for mauvais in ("zero", "-4", "0", "99999", ""):
        r = client.get("/api/veille?n=%s" % mauvais)
        assert r.status_code == 200, mauvais
        assert r.get_json()["ok"] is True, mauvais


# ── 2. Une adresse qui n'existe pas répond 404 ────────────────────────────

def test_une_fiche_inventee_repond_404_et_pas_seulement_a_l_ecran():
    A.app.config["TESTING"] = True
    with A.app.test_client() as c:
        assert c.get("/fiche/cette-fiche-n-existe-pas").status_code == 404
        assert c.get("/api/veille/fiche/cette-fiche-n-existe-pas").status_code == 404


def test_une_fiche_publiee_repond_200(client):
    ident = _un_id_publie()
    assert client.get("/fiche/%s" % ident).status_code == 200
    assert client.get("/api/veille/fiche/%s" % ident).status_code == 200


def test_une_fiche_en_reserve_est_introuvable_comme_si_elle_n_existait_pas(
        client, monkeypatch):
    """Répondre « elle existe mais vous n'y avez pas droit » renseignerait sur
    le contenu de la réserve éditoriale."""
    cachee = dict(V.publiables(A.corpus())[0], id="essai-reserve",
                  statut="redigee_par_ia", lecture_nature="modele")
    monkeypatch.setattr(A, "corpus", lambda: [cachee])
    assert client.get("/fiche/essai-reserve").status_code == 404
    r = client.get("/api/veille/fiche/essai-reserve")
    assert r.status_code == 404
    assert "droit" not in (r.get_json().get("message") or "")


# ── 3. Le croisement servi sépare le lien du voisinage ────────────────────

def test_l_api_rend_le_voisinage_a_part_des_liens(client):
    d = client.get("/api/veille/fiche/%s" % _un_id_publie()).get_json()
    assert "liens" in d and "voisinage" in d
    assert all(v["lien"] != "meme_periode" for v in d["liens"]), d["liens"]
    assert all(v["lien"] == "meme_periode" for v in d["voisinage"])


def test_aucun_voisin_servi_n_est_une_fiche_en_reserve(client):
    """Même porte que le fil : une fonctionnalité annexe ne la contourne pas."""
    for ident in [f["id"] for f in V.publiables(A.corpus())[:8]]:
        d = client.get("/api/veille/fiche/%s" % ident).get_json()
        publies = {f["id"] for f in V.publiables(A.corpus())}
        for v in d["liens"] + d["voisinage"]:
            assert v["id"] in publies, v["id"]


# ── 4. Les axes qui ne donnent rien le disent ─────────────────────────────

def test_l_api_pistes_sert_la_mesure_avec_les_pistes(client):
    """Servir les pistes sans la mesure laisserait croire que les
    déclencheurs muets ne trouvent rien parce qu'il n'y a rien à trouver."""
    d = client.get("/api/veille/pistes").get_json()
    assert d["ok"] and "mesure" in d and "solidites" in d
    assert d["mesure"]["total"] == len(d["pistes"])
    for p in d["pistes"]:
        assert p["fiches"] and "acheteur" in p["n_etablit_pas"]
        assert p["solidite"] in {int(k) for k in d["solidites"]}


def test_aucune_piste_servie_ne_pointe_une_fiche_en_reserve(client):
    """Une piste qui citerait une fiche non publiée en divulguerait le titre —
    et la porte éditoriale serait contournée par la bande."""
    publies = {f["id"] for f in V.publiables(A.corpus())}
    for p in client.get("/api/veille/pistes").get_json()["pistes"]:
        for f in p["fiches"]:
            assert f["id"] in publies, f["id"]


def test_l_api_dossiers_dit_ce_que_l_axe_par_entite_a_mesure(client):
    d = client.get("/api/veille/dossiers").get_json()
    m = d["mesure_entites"]
    assert m["dit"] and m["fiches"] == len(V.publiables(A.corpus()))
    assert d["tension"]["dit"]


def test_les_filtres_de_l_ecran_sont_ceux_que_l_api_lit():
    """LE CONTRAT ENTRE L'ÉCRAN ET LE MOTEUR. La page écrit désormais ses
    filtres dans l'adresse, pour qu'une vue se transmette — ce site répète
    partout que sans lien, rien ne se cite. Une adresse partagée qui nomme un
    filtre que l'API ignore rendrait une AUTRE vue que celle qu'on croyait
    envoyer, sans un mot : c'est la panne la plus trompeuse possible, puisque
    la page s'affiche normalement.

    Le contrôle lit la table unique de veille.js, celle qui sert à la fois à
    interroger, à écrire l'adresse et à la relire."""
    import re as _re
    js = open(os.path.join(ICI, "veille.js"), encoding="utf-8").read()
    bloc = js[js.index("var FILTRES = ["):js.index("function parametres")]
    noms = _re.findall(r'\["(\w+)",\s*"f-[\w-]+"\]', bloc)
    assert len(noms) >= 7, noms
    src = open(os.path.join(ICI, "app.py"), encoding="utf-8").read()
    api = src[src.index("def api_veille"):src.index("def page_abonnement")]
    for n in noms:
        assert 'request.args.get("%s")' % n in api, n
