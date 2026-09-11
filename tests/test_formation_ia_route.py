# -*- coding: utf-8 -*-
"""La réservation « Formations conformité IA » par la voie HTTP — mesurée.

CE QUE CES RÈGLES ÉPROUVENT, ET QU'AUCUN APPEL DIRECT NE MESURE : que la route
publique décide bien du tarif elle-même (rang → gratuit puis 800 € HT), qu'elle
ne réserve qu'UNE séance par créneau et qu'un sujet une seule fois par client,
et qu'elle refuse à la source un sujet inconnu, un créneau hors calendrier ou
une origine étrangère. Le prix n'est JAMAIS cru sur parole du client : la règle
poste des inscriptions et lit ce que le serveur a décidé.

Les lignes de test portent une clé cliente reconnaissable et sont effacées à la
fin — la base partagée ne doit rien garder de ces essais.
"""
import datetime

import pytest

import app as A
import formations_ia as F

# Une clé cliente d'essai, effacée en fin de test ; des créneaux pris dans le
# FOND du calendrier (mars 2027), pour ne heurter aucune vraie réservation.
SIRET_TEST = "900000000"          # 9 chiffres → clé 'siret:900000000'
SIRET_TEST2 = "900000001"


def _creneaux():
    return [c["date"] for c in F.creneaux(datetime.datetime.utcnow().date())]


def _purge():
    """Ardoise nette AVANT et APRÈS chaque test. La table des réservations de
    formation n'appartient qu'à cette fonctionnalité et n'est peuplée par aucun
    autre test : la vider rend ces règles indépendantes de l'ordre de la suite
    et de tout dépôt résiduel — sans quoi un créneau déjà pris par un test
    voisin ferait échouer « la première est gratuite » sur un 409."""
    conn = A.registre_get_db(); cur = conn.cursor()
    try:
        A._formation_ia_table(cur, conn)
        cur.execute("DELETE FROM formation_ia_resa")
        conn.commit()
    except Exception:
        pass
    try: conn.close()
    except Exception: pass


@pytest.fixture
def client():
    _purge()
    c = A.app.test_client()
    yield c
    _purge()


def _resa(client, sujet, creneau, siret=SIRET_TEST, email="essai@ex.fr",
          entreprise="ESSAI SAS"):
    return client.post("/api/formation/inscription", json={
        "sujet": sujet, "creneau": creneau, "nom": "Durand", "prenom": "Alex",
        "email": email, "entreprise": entreprise, "siret": siret})


def test_le_referentiel_est_public_et_complet(client):
    """Sans compte, on obtient l'offre, les quatre sujets, le calendrier (avec
    l'état libre de chaque créneau) et le tarif — le tarif venant du serveur."""
    r = client.get("/api/formation/referentiel")
    assert r.status_code == 200
    j = r.get_json()
    assert j["ok"] and len(j["sujets"]) == 4
    assert j["creneaux"] and all("libre" in c for c in j["creneaux"])
    assert j["tarif"]["ht_cents"] == 80000


def test_la_premiere_est_gratuite_la_deuxieme_a_800(client):
    """LE CŒUR DE L'OFFRE, PAR LA ROUTE. La première séance d'un client (même
    SIRET) est confirmée et gratuite ; la deuxième, sur un autre sujet, est à
    800 € HT. Le rang et le prix sont décidés côté serveur."""
    cr = _creneaux()
    r1 = _resa(client, "gouvernance-ia", cr[-1]).get_json()
    assert r1["ok"] and r1["gratuit"] is True and r1["montant_cents"] == 0
    assert r1["statut"] == "confirmee"
    r2 = _resa(client, "securite-ia", cr[-2]).get_json()
    assert r2["ok"] and r2["gratuit"] is False and r2["montant_cents"] == 80000


def test_un_meme_sujet_ne_se_reserve_pas_deux_fois(client):
    cr = _creneaux()
    assert _resa(client, "gouvernance-ia", cr[-1]).status_code == 200
    r = _resa(client, "gouvernance-ia", cr[-3])
    assert r.status_code == 409


def test_un_creneau_ne_porte_qu_une_seance(client):
    """Le formateur ne se dédouble pas : un créneau déjà pris est refusé, même
    à un autre client."""
    cr = _creneaux()
    assert _resa(client, "gouvernance-ia", cr[-1]).status_code == 200
    r = _resa(client, "securite-ia", cr[-1], siret=SIRET_TEST2,
              email="autre@ex.fr", entreprise="AUTRE SARL")
    assert r.status_code == 409


def test_la_route_refuse_a_la_source_sujet_creneau_et_champs(client):
    """Un sujet inconnu, un créneau hors calendrier, ou des champs requis
    absents sont refusés AVANT toute écriture — le client ne fixe rien."""
    cr = _creneaux()
    assert _resa(client, "sujet-bidon", cr[-1]).status_code == 400
    assert _resa(client, "gouvernance-ia", "2020-01-01").status_code == 400
    r = client.post("/api/formation/inscription", json={
        "sujet": "gouvernance-ia", "creneau": cr[-1], "nom": "", "prenom": "",
        "email": "", "entreprise": ""})
    assert r.status_code == 400


def test_une_origine_etrangere_est_refusee(client):
    cr = _creneaux()
    r = client.post("/api/formation/inscription",
                    json={"sujet": "gouvernance-ia", "creneau": cr[-1],
                          "nom": "X", "prenom": "Y", "email": "z@ex.fr",
                          "entreprise": "E"},
                    headers={"Origin": "https://evil.example"})
    assert r.status_code == 403


def test_la_cle_client_prefere_le_SIRET_puis_le_courriel():
    """La gratuité se compte par entreprise : le SIRET (≥ 9 chiffres) fait la
    clé ; sans SIRET valable, le courriel. Deux inscriptions du même SIRET ne
    rejouent pas la première séance gratuite, quel que soit le courriel."""
    assert A._formation_ia_cle_client("900 000 000", "a@ex.fr") == "siret:900000000"
    assert A._formation_ia_cle_client("12345", "A@Ex.FR") == "email:a@ex.fr"
    assert A._formation_ia_cle_client("", "  Jean@Ex.fr ") == "email:jean@ex.fr"
