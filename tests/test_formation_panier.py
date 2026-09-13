# -*- coding: utf-8 -*-
"""Réserver de une à quatre formations d'un geste, et choisir laquelle est offerte.

CE QUI A CHANGÉ, ET POURQUOI CE N'EST PAS UN CONFORT. La gratuité tombait sur la
PREMIÈRE séance réservée, quelle qu'elle soit : un client qui voulait la
gouvernance agentique offerte devait la réserver EN PREMIER — et l'apprendre
après coup. Le panier rend ce choix explicite, et ces règles le mesurent : la
séance à zéro doit être CELLE QU'ON A DÉSIGNÉE, pas la première de la liste.

LE POINT DE SÉCURITÉ, ET IL EST LE PLUS IMPORTANT DE CE FICHIER. Le client
envoie désormais une clé « gratuit ». Elle désigne un SUJET, jamais un prix —
mais la frontière ne tient que si le serveur la garde : une règle poste donc la
demande de gratuité pour un client qui a DÉJÀ consommé la sienne, et exige que
tout soit facturé. Sans ce témoin, la relaxation de la règle « aucune clé de
prix dans le corps posté » serait une porte ouverte plutôt qu'une précision.

LES SEPT JOURS SE MESURENT À LA BORNE, PAS AU MILIEU. « Moins de sept jours
avant » est ce qui est dû : à exactement sept jours l'annulation passe encore,
à six elle est refusée. Une règle qui n'éprouverait que J-30 et J-1 serait verte
sur un délai de trois jours comme sur un délai de trente.

CE QUE L'ANNULATION NE FAIT PAS, ET C'EST DÉLIBÉRÉ. Elle n'est pas atteignable
en GET. Le lien part par courriel : un anti-virus qui inspecte les liens, un
client de messagerie qui précharge, un moteur qui indexe — tous le visitent sans
que personne n'ait cliqué. Une annulation déclenchée par une simple visite est
un piège posé à son propre client.
"""
import datetime
import io
import os
import re
import unicodedata

import pytest

import app as A
import formations_ia as F


RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = io.open(os.path.join(RACINE, "formation.html"), encoding="utf-8").read()

SIRET_A = "910000000"
SIRET_B = "910000001"
TOUS = [s["cle"] for s in F.SUJETS]


def _purge():
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


def _creneaux():
    return [c["date"] for c in F.creneaux(datetime.datetime.utcnow().date())]


def _poster(client, paires, gratuit=None, siret=SIRET_A, **kw):
    corps = {
        "seances": [{"sujet": s, "creneau": d} for s, d in paires],
        "nom": "Durand", "prenom": "Alex", "email": kw.get("email", "a@ex.fr"),
        "entreprise": "ESSAI SAS", "siret": siret,
        "telephone": "+33 6 12 34 56 78", "lieu": "12 rue d'Essai, Paris",
    }
    if gratuit:
        corps["gratuit"] = gratuit
    corps.update({k: v for k, v in kw.items() if k != "email"})
    return client.post("/api/formation/inscription", json=corps)


def _sans_accent(t):
    """Pour les règles qui mesurent le SENS d'une phrase et non sa graphie."""
    return "".join(c for c in unicodedata.normalize("NFD", t or "")
                   if unicodedata.category(c) != "Mn")


def _lignes():
    conn = A.registre_get_db(); cur = conn.cursor()
    A._formation_ia_table(cur, conn)
    cur.execute("SELECT * FROM formation_ia_resa ORDER BY id ASC")
    out = [dict(r) for r in cur.fetchall()]
    try: conn.close()
    except Exception: pass
    return out


# ══════════════════════════════════════════════════════════════════════════
#  LE DEVIS — le moteur, hors ligne
# ══════════════════════════════════════════════════════════════════════════
def test_de_une_a_quatre_formations_en_un_seul_devis():
    for n in (1, 2, 3, 4):
        d = F.devis(TOUS[:n])
        assert d["ok"], d
        assert d["nb"] == n and len(d["lignes"]) == n


def test_une_cinquieme_formation_est_refusee_et_le_DIT():
    """Le refus muet ferait chercher une panne. Et le plafond n'est pas un
    nombre rond : c'est le nombre de sujets."""
    d = F.devis(TOUS + ["gouvernance-ia"])
    assert not d["ok"] and d["error"] == "trop_de_seances"
    assert "quatre" in d["message"].lower()
    assert F.MAX_SEANCES == F.NB_SUJETS


def test_la_gratuite_porte_sur_la_seance_CHOISIE_et_non_sur_la_PREMIERE():
    """LE CŒUR DE CE FICHIER. Avant, la première réservée était offerte : cette
    règle serait verte par accident si l'on désignait la première. On désigne
    donc la TROISIÈME, et l'on exige que ce soit ELLE qui soit à zéro."""
    d = F.devis(TOUS[:3], gratuit=TOUS[2])
    offertes = [l["cle"] for l in d["lignes"] if l["gratuit"]]
    assert offertes == [TOUS[2]], offertes
    assert d["lignes"][0]["ht_cents"] == F.TARIF_HT_CENTS
    assert d["ht_cents"] == 2 * F.TARIF_HT_CENTS


def test_sans_choix_la_PREMIERE_est_offerte_et_jamais_AUCUNE():
    """Laisser la gratuité tomber faute d'avoir coché ferait payer une séance
    annoncée offerte — le contraire de la règle publiée."""
    d = F.devis(TOUS[:3])
    assert d["gratuite"] == TOUS[0]
    assert sum(1 for l in d["lignes"] if l["gratuit"]) == 1
    assert d["message"] and "offerte" in d["message"]


def test_une_gratuite_HORS_panier_est_refusee():
    """Une remise sur une séance qu'on ne réserve pas serait introuvable à
    l'écran — et le total, inexplicable."""
    d = F.devis(["gouvernance-ia"], gratuit="securite-ia")
    assert not d["ok"] and d["error"] == "gratuite_hors_panier"


def test_un_client_qui_a_DEJA_consomme_sa_gratuite_paie_tout():
    d = F.devis(TOUS[:2], gratuit=TOUS[1], gratuite_disponible=False)
    assert d["ok"] and d["gratuite"] is None
    assert all(not l["gratuit"] for l in d["lignes"])
    assert d["ht_cents"] == 2 * F.TARIF_HT_CENTS
    assert "déjà" in (d["message"] or "")


def test_le_meme_sujet_deux_fois_est_refuse():
    d = F.devis(["securite-ia", "securite-ia"])
    assert not d["ok"] and d["error"] == "sujet_en_double"


def test_le_total_est_la_SOMME_des_lignes_et_non_un_calcul_a_part():
    """Deux calculs du même montant divergent le jour où l'un des deux change ;
    c'est celui qui est affiché qui a tort, et on ne le sait qu'à la facture."""
    for gr in (None, TOUS[1], TOUS[3]):
        d = F.devis(TOUS, gratuit=gr)
        assert d["ht_cents"] == sum(l["ht_cents"] for l in d["lignes"]), d
        assert d["nb_payantes"] == sum(1 for l in d["lignes"] if not l["gratuit"])


# ══════════════════════════════════════════════════════════════════════════
#  LES SEPT JOURS — mesurés à la borne
# ══════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("reste,rendu", [
    (30, 48000), (8, 48000), (7, 48000), (6, 0), (1, 0), (0, 0),
])
def test_le_remboursement_est_de_MOITIE_a_sept_jours_et_NUL_a_six(reste, rendu):
    """LA BORNE DU BARÈME, MESURÉE DES DEUX CÔTÉS. « Moins de sept jours » est
    ce qui n'est pas rendu : à SEPT exactement, la moitié l'est. Une règle qui
    n'éprouverait que J-30 et J-1 serait verte sur un délai de trois jours
    comme sur un délai de trente.

    480 € SUR 960 € : ce sont les montants annoncés au client, et ils se
    DÉRIVENT du tarif et du taux de TVA. Les écrire ici les fige à côté du
    calcul ; le garde du module vérifie qu'ils coïncident encore, et refuse de
    charger sinon.
    """
    rb = F.remboursement(96000, reste)
    assert rb["cents"] == rendu, (reste, rb)
    assert rb["du"] is bool(rendu)
    assert str(F.ANNULATION_JOURS) in rb["motif"]


@pytest.mark.parametrize("reste", [30, 8, 7, 6, 1, 0])
def test_annuler_reste_POSSIBLE_des_deux_cotes_du_delai(reste):
    """CE QUI A CHANGÉ, ET POURQUOI. Tant que la séance se réglait après coup,
    refuser l'annulation tardive évitait de transformer un clic en huit cents
    euros d'engagement. Le paiement étant encaissé à la réservation, annuler
    tard ne crée plus de dette : cela renonce au remboursement. Refuser
    garderait un créneau bloqué sur une séance que personne ne viendrait
    suivre."""
    jour = datetime.date(2026, 10, 20)
    ok, motif = F.annulable(jour, jour - datetime.timedelta(days=reste))
    assert ok, (reste, motif)
    assert str(F.ANNULATION_JOURS) in motif


def test_une_seance_OFFERTE_ne_donne_lieu_a_aucun_remboursement():
    rb = F.remboursement(0, 30)
    assert rb["cents"] == 0 and rb["du"] is False
    assert "rien à rendre" in rb["motif"]


def test_le_barème_ne_RECALCULE_pas_le_tarif_mais_lit_ce_qui_a_ete_REGLE():
    """Un client qui a payé 960 € doit récupérer 480 €, même si le tarif a
    changé depuis. Le barème prend donc le montant RÉGLÉ en argument — il ne
    va pas le chercher dans le catalogue du jour."""
    assert F.remboursement(50000, 30)["cents"] == 25000
    assert F.remboursement(96000, 30)["cents"] == 48000


def test_l_arrondi_du_remboursement_ne_PENCHE_pas_toujours_du_meme_cote():
    """Tronquer ferait rendre un centime de moins à chaque fois, toujours au
    détriment du client, et toujours en faveur de la même partie."""
    assert F.remboursement(1, 30)["cents"] == 1        # 0,5 c → 1 c, pas 0
    assert F.remboursement(3, 30)["cents"] == 2        # 1,5 c → 2 c


def test_une_seance_PASSEE_ne_s_annule_pas():
    ok, motif = F.annulable("2026-01-01", "2026-02-01")
    assert not ok and "eu lieu" in motif


def test_la_regle_d_annulation_DIT_son_delai_ET_son_bareme():
    """Sept jours écrits dans le code et « une semaine » dans le texte
    finissent par diverger — et c'est le texte que le client a lu qui engage.
    Le taux et les montants suivent la même discipline."""
    r = F.regle_annulation()
    assert r["jours"] == F.ANNULATION_JOURS
    assert r["pct"] == F.REMBOURSEMENT_PCT
    for champ in ("avant", "apres", "infobulle"):
        assert str(F.ANNULATION_JOURS) in r[champ], champ
    assert str(F.REMBOURSEMENT_PCT) in r["infobulle"]
    # Les montants annoncés sont ceux que le calcul rendra, pas un texte à côté.
    assert r["ttc_cents"] == 96000 and r["rendu_cents"] == 48000
    assert "480" in r["avant"] and "960" in r["avant"]
    assert "aucun remboursement" in r["apres"].lower()
    # Le paiement immédiat est dit : c'est lui qui retient la place.
    assert "réservation" in r["paiement"]


def test_le_TTC_annonce_et_sa_MOITIE_sont_derives_du_tarif():
    """960 € et 480 € sont les montants publiés. Ils se dérivent du tarif HT et
    du taux de TVA : si le taux changeait, ils cesseraient de valoir ce qui a
    été annoncé — et le module refuse alors de charger plutôt que de rembourser
    un autre montant sous le même libellé."""
    assert F._ttc(F.TARIF_HT_CENTS) == 96000
    assert F.remboursement(96000, F.ANNULATION_JOURS)["cents"] == 48000
    assert F.sante()["problemes"] == []


# ══════════════════════════════════════════════════════════════════════════
#  LA ROUTE — ce que la base garde vraiment
# ══════════════════════════════════════════════════════════════════════════
def test_trois_seances_en_un_envoi_font_TROIS_reservations(client):
    cre = _creneaux()[:3]
    r = _poster(client, list(zip(TOUS[:3], cre)), gratuit=TOUS[2])
    assert r.status_code == 200 and r.get_json()["ok"], r.get_json()
    lg = _lignes()
    assert len(lg) == 3
    assert len({x["commande"] for x in lg}) == 1, "les trois lignes ne sont pas groupées"
    assert sorted(x["date_creneau"] for x in lg) == sorted(cre)


def test_la_gratuite_CHOISIE_est_celle_qui_vaut_zero_EN_BASE(client):
    """L'écran peut afficher ce qu'il veut : ce qui compte est la ligne écrite."""
    cre = _creneaux()[:3]
    _poster(client, list(zip(TOUS[:3], cre)), gratuit=TOUS[2])
    zero = [x["sujet"] for x in _lignes() if int(x["montant_cents"] or 0) == 0]
    assert zero == [TOUS[2]], zero


def test_un_client_DEJA_VENU_ne_retrouve_pas_sa_gratuite_en_la_DEMANDANT(client):
    """LE TÉMOIN DE SÉCURITÉ. Le client envoie « gratuit » : si le serveur le
    croyait, il suffirait de repasser commande pour ne jamais payer."""
    cre = _creneaux()
    _poster(client, [(TOUS[0], cre[0])], gratuit=TOUS[0])
    r = _poster(client, [(TOUS[1], cre[1])], gratuit=TOUS[1])
    assert r.status_code == 200, r.get_json()
    j = r.get_json()
    assert j["devis"]["nb_payantes"] == 1, j["devis"]
    assert j["devis"]["ht_cents"] == F.TARIF_HT_CENTS
    seconde = [x for x in _lignes() if x["sujet"] == TOUS[1]][0]
    assert int(seconde["montant_cents"]) == F.TARIF_HT_CENTS
    assert int(seconde["gratuit"] or 0) == 0


def test_deux_formations_a_la_MEME_date_sont_refusees(client):
    cre = _creneaux()[0]
    r = _poster(client, [(TOUS[0], cre), (TOUS[1], cre)])
    assert r.status_code == 400
    assert "même date" in r.get_json()["error"] or "meme date" in r.get_json()["error"]
    assert _lignes() == [], "un panier refusé a quand même écrit"


def test_une_date_hors_calendrier_est_refusee(client):
    r = _poster(client, [(TOUS[0], "2019-01-01")])
    assert r.status_code == 400 and not _lignes()


def test_un_panier_dont_UNE_date_est_prise_n_ecrit_RIEN(client):
    """L'ATOMICITÉ. Écrire deux séances puis refuser la troisième laisserait un
    panier à moitié réservé — et le client ne saurait pas laquelle est prise."""
    cre = _creneaux()[:3]
    _poster(client, [(TOUS[0], cre[0])], siret=SIRET_B, email="b@ex.fr")
    avant = len(_lignes())
    r = _poster(client, [(TOUS[1], cre[1]), (TOUS[2], cre[0])])
    assert r.status_code == 409, r.get_json()
    assert len(_lignes()) == avant, "le panier refusé a écrit une ligne quand même"


def test_l_ANCIEN_envoi_un_sujet_un_creneau_marche_encore(client):
    """La route promet d'accepter l'ancien envoi ; lui rendre une réponse
    amputée le casserait quand même."""
    r = client.post("/api/formation/inscription", json={
        "sujet": TOUS[0], "creneau": _creneaux()[0], "nom": "Durand",
        "prenom": "Alex", "email": "a@ex.fr", "entreprise": "ESSAI SAS",
        "siret": SIRET_A, "telephone": "+33 6 12 34 56 78",
        "lieu": "12 rue d'Essai, Paris"})
    assert r.status_code == 200
    j = r.get_json()
    for ancienne in ("gratuit", "montant_cents", "ttc_cents", "sujet", "creneau"):
        assert ancienne in j, "la clé « %s » a disparu de la réponse" % ancienne
    assert j["gratuit"] is True and j["montant_cents"] == 0
    assert len(_lignes()) == 1


def test_chaque_reservation_porte_un_jeton_UNIQUE_et_long(client):
    """Le jeton est la SEULE preuve qu'un client sans compte possède sur sa
    réservation. Court ou prévisible, il se teste en quelques minutes."""
    cre = _creneaux()[:3]
    _poster(client, list(zip(TOUS[:3], cre)))
    jetons = [x["jeton"] for x in _lignes()]
    assert all(j and len(j) >= 24 for j in jetons), jetons
    assert len(set(jetons)) == 3, "deux séances partagent un jeton"


# ══════════════════════════════════════════════════════════════════════════
#  L'ANNULATION
# ══════════════════════════════════════════════════════════════════════════
def _jeton_de(sujet):
    return [x["jeton"] for x in _lignes() if x["sujet"] == sujet][0]


def test_annuler_a_plus_de_sept_jours_LIBERE_le_creneau(client):
    cre = _creneaux()[0]
    _poster(client, [(TOUS[0], cre)])
    pris = [c for c in client.get("/api/formation/referentiel").get_json()["creneaux"]
            if c["date"] == cre][0]
    assert not pris["libre"], "le créneau n'a jamais été pris"
    r = client.post("/api/formation/annulation", json={"jeton": _jeton_de(TOUS[0])})
    assert r.status_code == 200 and r.get_json()["ok"], r.get_json()
    apres = [c for c in client.get("/api/formation/referentiel").get_json()["creneaux"]
             if c["date"] == cre][0]
    assert apres["libre"], "le créneau annulé reste bloqué"


def _poser_a(client, jours, payee=True):
    """Une réservation posée à `jours` de la séance, réglée ou non.

    ON NE PEUT PAS RÉSERVER À MOINS DE SEPT JOURS — le calendrier ne le propose
    pas. La ligne est donc déplacée en base, comme une réservation prise il y a
    trois semaines pour après-demain.
    """
    _poster(client, [(TOUS[0], _creneaux()[0])])
    quand = (datetime.datetime.utcnow().date()
             + datetime.timedelta(days=jours)).isoformat()
    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute(A.registre_sql(
        "UPDATE formation_ia_resa SET date_creneau=%s, gratuit=0, "
        "montant_cents=80000, paye_ttc_cents=96000, statut=%s",
        "UPDATE formation_ia_resa SET date_creneau=?, gratuit=0, "
        "montant_cents=80000, paye_ttc_cents=96000, statut=?"),
        (quand, "payee" if payee else "devis"))
    conn.commit()
    try: conn.close()
    except Exception: pass
    return _jeton_de(TOUS[0])


def test_annuler_a_MOINS_de_sept_jours_REUSSIT_mais_ne_rembourse_RIEN(client):
    """LE PAIEMENT ÉTANT ENCAISSÉ D'AVANCE, annuler tard ne crée plus de dette :
    cela renonce au remboursement. Refuser garderait un créneau bloqué sur une
    séance que personne ne viendrait suivre."""
    jet = _poser_a(client, 3)
    r = client.post("/api/formation/annulation", json={"jeton": jet})
    assert r.status_code == 200 and r.get_json()["ok"], r.get_json()
    j = r.get_json()
    assert j["remboursement"]["attendu_cents"] == 0, j["remboursement"]
    assert j["remboursement"]["rembourse_cents"] == 0
    assert "aucun remboursement" in j["message"].lower()
    lg = _lignes()[0]
    assert lg["statut"] == "annulee"
    assert int(lg["rembourse_cents"] or 0) == 0
    assert int(lg["remboursement_du"] or 0) == 0, (
        "un remboursement est noté dû alors que le délai est dépassé")


def test_annuler_a_PLUS_de_sept_jours_doit_la_MOITIE_du_montant_regle(client):
    """480 € sur 960 €. Sans clé Stripe le virement ne peut pas partir — mais
    la somme est alors notée DUE, et l'écran ne prétend jamais qu'elle est
    partie."""
    jet = _poser_a(client, 20)
    r = client.post("/api/formation/annulation", json={"jeton": jet})
    assert r.status_code == 200 and r.get_json()["ok"], r.get_json()
    rb = r.get_json()["remboursement"]
    assert rb["attendu_cents"] == 48000 and rb["pct"] == F.REMBOURSEMENT_PCT
    lg = _lignes()[0]
    # Sans Stripe : rien n'est parti, tout est dû — et les deux se totalisent.
    assert (int(lg["rembourse_cents"] or 0)
            + int(lg["remboursement_du"] or 0)) == 48000, dict(lg)


def test_l_ecran_ne_dit_JAMAIS_rembourse_quand_rien_n_est_parti(client):
    """Annoncer un virement qui n'a pas eu lieu se découvre au relevé bancaire,
    quinze jours plus tard — et c'est alors CONSEILPREV qui a menti."""
    jet = _poser_a(client, 20)
    j = client.post("/api/formation/annulation", json={"jeton": jet}).get_json()
    if j["remboursement"]["rembourse_cents"] == 0:
        assert "vous est du" in j["message"] or "vous est dû" in j["message"], j["message"]
        assert "emis" not in j["message"].lower().replace("émis", "emis") \
            or "n'a PAS pu" in j["message"], j["message"]


def test_une_seance_NON_REGLEE_annulee_ne_donne_lieu_a_aucun_remboursement(client):
    """Il n'y a rien à rendre sur ce qui n'a pas été encaissé — et le dire
    évite qu'on l'attende."""
    jet = _poser_a(client, 20, payee=False)
    j = client.post("/api/formation/annulation", json={"jeton": jet}).get_json()
    assert j["remboursement"]["rembourse_cents"] == 0
    assert j["remboursement"]["du_cents"] == 0
    # LA GRAPHIE N'EST PAS L'OBJET DE CETTE RÈGLE : elle mesure ce que la phrase
    # DIT, pas comment elle l'écrit. Les accents ont leur propre règle.
    m = _sans_accent(j["message"])
    assert "pas ete reglee" in m or "rien a rendre" in m, j["message"]


def test_une_seance_DEJA_TENUE_ne_s_annule_plus(client):
    """Seule une date passée arrête l'annulation : le délai, lui, ne décide
    plus que du remboursement."""
    jet = _poser_a(client, -3)
    r = client.post("/api/formation/annulation", json={"jeton": jet})
    assert r.status_code == 409
    assert "eu lieu" in r.get_json()["error"]
    assert _lignes()[0]["statut"] != "annulee"


def test_le_jeton_d_un_AUTRE_n_annule_pas_ma_seance(client):
    cre = _creneaux()[:2]
    _poster(client, [(TOUS[0], cre[0])])
    _poster(client, [(TOUS[1], cre[1])], siret=SIRET_B, email="b@ex.fr")
    r = client.post("/api/formation/annulation", json={"jeton": _jeton_de(TOUS[1])})
    assert r.status_code == 200
    etats = {x["sujet"]: x["statut"] for x in _lignes()}
    assert etats[TOUS[1]] == "annulee"
    assert etats[TOUS[0]] != "annulee", "l'annulation a débordé sur l'autre client"


def test_un_jeton_inconnu_ne_dit_PAS_s_il_a_existe(client):
    """Distinguer « inconnu » de « déjà servi » donnerait à qui essaie des
    jetons au hasard un signal sur ceux qui existent."""
    r = client.post("/api/formation/annulation", json={"jeton": "z" * 40})
    assert r.status_code == 404
    assert "deja" not in r.get_json()["error"].lower()


def test_recliquer_sur_le_lien_ne_ressemble_pas_a_une_panne(client):
    _poster(client, [(TOUS[0], _creneaux()[0])])
    jet = _jeton_de(TOUS[0])
    client.post("/api/formation/annulation", json={"jeton": jet})
    r = client.post("/api/formation/annulation", json={"jeton": jet})
    assert r.status_code == 200 and r.get_json()["ok"] and r.get_json()["deja"]


def test_l_annulation_n_est_PAS_atteignable_en_GET(client):
    """LE PIÈGE DU LIEN DE COURRIEL. Un anti-virus qui inspecte les liens, un
    client de messagerie qui précharge : tous visitent l'adresse sans que
    personne n'ait cliqué. Une annulation déclenchée par une visite est un
    piège posé à son propre client."""
    _poster(client, [(TOUS[0], _creneaux()[0])])
    jet = _jeton_de(TOUS[0])
    # LA MESURE PORTE SUR L'EFFET, PAS SUR LE CODE DE RETOUR. Un 404 et un 405
    # disent tous deux « pas par ici » ; ce qui compte est que la séance soit
    # toujours là après la visite.
    r = client.get("/api/formation/annulation?jeton=" + jet)
    assert r.status_code in (404, 405), r.status_code
    assert _lignes()[0]["statut"] != "annulee", (
        "une simple visite de l'adresse a annulé la séance")
    # Et le lien du courriel mène à la PAGE, pas à l'écriture. La page est
    # servie avec un en-tête de navigateur : le garde anti-robot du site refuse
    # un client sans agent utilisateur, et mesurer SON refus ne dirait rien de
    # ce qu'on veut ici.
    NAVIGATEUR = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                                " (KHTML, like Gecko) Chrome/120 Safari/537.36",
                  "Accept": "text/html,application/xhtml+xml",
                  "Accept-Language": "fr-FR"}
    assert client.get("/formation?annuler=" + jet,
                      headers=NAVIGATEUR).status_code == 200
    assert _lignes()[0]["statut"] != "annulee", (
        "ouvrir la page d'annulation annule sans qu'on ait cliqué")


# ══════════════════════════════════════════════════════════════════════════
#  LA PAGE
# ══════════════════════════════════════════════════════════════════════════
def test_la_page_envoie_les_SEANCES_avec_leur_date():
    i = PAGE.index("/api/formation/inscription")
    corps = PAGE[i:i + 1400]
    assert "seances:" in corps
    assert "sujet:k" in corps.replace(" ", "") or "sujet: k" in corps
    assert "creneau:" in corps


def test_la_page_ne_CALCULE_pas_le_total_elle_meme():
    """Elle ne sait pas si ce client a déjà consommé sa séance offerte — cela
    se lit en base. Un total calculé ici afficherait 1 600 € à qui en doit
    2 400, et l'écart se découvrirait à la caisse."""
    i = PAGE.index("function majRecap(")
    corps = PAGE[i:PAGE.index("\n  }", i)]
    assert "state.devis" in corps, "le récapitulatif n'affiche pas le devis du serveur"
    for ecrit in ("80000", "* 800", "TARIF_HT"):
        assert ecrit not in corps, "le total est recomposé dans la page (« %s »)" % ecrit
    assert "/api/formation/devis" in PAGE, "la page ne demande aucun devis au serveur"


def test_l_infobulle_des_sept_jours_est_LUE_et_non_recopiee():
    """Sept jours écrits dans la page et sept dans le module finissent par
    diverger — et c'est le texte affiché qui engage."""
    i = PAGE.index("function rendreAnnulation(")
    corps = PAGE[i:PAGE.index("\n  }", i)]
    assert "a.infobulle" in corps, "l'infobulle n'est pas lue du référentiel"
    assert "data-tip" in corps
    # Le délai n'est écrit NULLE PART en dur dans la page.
    assert not re.search(r"moins de (sept|7) jours", PAGE), (
        "le délai d'annulation est recopié dans la page au lieu d'être lu")


def test_le_lien_d_annulation_ne_declenche_RIEN_en_s_ouvrant():
    i = PAGE.index("function annulation(")
    corps = PAGE[i:PAGE.index("\n  })();", i)]
    assert "annul-go" in corps and "addEventListener('click'" in corps, (
        "l'annulation ne passe pas par un bouton")
    # L'appel réseau est DANS le gestionnaire de clic, jamais au chargement.
    av = corps[:corps.index("addEventListener('click'")]
    assert "/api/formation/annulation" not in av, (
        "la page appelle l'annulation avant tout clic : le premier anti-virus "
        "qui ouvre le lien annulerait la séance")


def test_sans_limite_de_participants_est_DIT():
    """Le code n'a jamais posé de plafond ; ne pas le dire laissait le client
    supposer le contraire — et n'inviter que trois personnes."""
    assert "limite de participants" in F.SUPPORT["participants"].lower()
    assert 'id="sup-part"' in PAGE


def test_le_support_dit_ce_qui_est_PERSONNALISE_et_ce_qui_ne_l_est_pas():
    """« Support personnalisé » sans dire ce qui l'est est la promesse la plus
    facile à démentir le jour de la séance."""
    natures = {e["nature"] for e in F.SUPPORT["elements"]}
    assert natures == {"standard", "personnalise"}, natures
    i = PAGE.index("function rendreSupport(")
    corps = PAGE[i:PAGE.index("\n  }", i)]
    assert "personnalise" in corps and "standard" in corps
    assert "e.nature" in corps, "la page décide seule de ce qui est personnalisé"


def test_les_etudes_de_cas_suivent_le_TYPE_de_client():
    a = F.etudes_de_cas("exploitant")
    b = F.etudes_de_cas("editeur")
    assert a["choisi"] and b["choisi"] and a["cas"] != b["cas"]
    inconnu = F.etudes_de_cas("zzz")
    assert not inconnu["choisi"] and inconnu["cas"], (
        "un profil inconnu rend une liste vide : on croirait qu'aucun cas "
        "n'est présenté")
    assert 'id="fo-profil"' in PAGE


# ══════════════════════════════════════════════════════════════════════════
#  LE PAIEMENT IMMÉDIAT — ce qu'il confirme, et ce qu'il retient
# ══════════════════════════════════════════════════════════════════════════
def _en_attente(client, n=3):
    """Un panier de n séances payantes, laissé « en attente de paiement »."""
    cre = _creneaux()[:n + 1]
    _poster(client, list(zip(TOUS[:n + 1], cre)))
    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute("UPDATE formation_ia_resa SET statut='en_attente_paiement', "
                "gratuit=0, montant_cents=80000")
    conn.commit()
    try: conn.close()
    except Exception: pass
    return _lignes()[0]["commande"]


def test_une_session_stripe_confirme_TOUTES_les_seances_du_panier(client):
    """LE DÉFAUT QUE CETTE RÈGLE TIENT. Une session Stripe règle jusqu'à QUATRE
    séances. Ne confirmer que la première laissait les trois autres « en
    attente de paiement » alors qu'elles étaient réglées — et, le jour d'une
    annulation, sans remboursement, parce qu'on les croyait impayées.

    C'est un défaut qui ne se voit pas : la première séance est confirmée,
    l'écran de retour dit « paiement reçu », et l'argent est bien encaissé. Ce
    qui manque n'apparaît qu'à l'annulation, des semaines plus tard.
    """
    cmd = _en_attente(client, 3)
    A._formation_ia_confirmer_paiement(commande=cmd)
    etats = [x["statut"] for x in _lignes()]
    assert etats == ["payee"] * 4, etats


def test_le_montant_REGLE_est_note_AU_PAIEMENT_et_non_recalcule_apres(client):
    """Un client qui a payé 960 € doit récupérer 480 €, même si le tarif a
    changé entre-temps. Ce qui a été encaissé est donc noté le jour du
    paiement."""
    cmd = _en_attente(client, 1)
    A._formation_ia_confirmer_paiement(commande=cmd)
    for x in _lignes():
        assert int(x["paye_ttc_cents"] or 0) == 96000, dict(x)
        assert x["paye_le"], "la date de paiement n'est pas notée"


def test_une_seance_OFFERTE_n_est_jamais_marquee_payee(client):
    """La marquer ainsi ferait croire à un remboursement possible sur une
    séance qui n'a rien coûté."""
    cre = _creneaux()[:2]
    _poster(client, list(zip(TOUS[:2], cre)), gratuit=TOUS[0])
    cmd = _lignes()[0]["commande"]
    A._formation_ia_confirmer_paiement(commande=cmd)
    par = {x["sujet"]: x for x in _lignes()}
    assert par[TOUS[0]]["statut"] != "payee", "la séance offerte est dite payée"
    assert int(par[TOUS[0]]["paye_ttc_cents"] or 0) == 0


def test_confirmer_DEUX_FOIS_le_meme_paiement_ne_change_rien(client):
    """Une notification Stripe peut arriver deux fois."""
    cmd = _en_attente(client, 1)
    A._formation_ia_confirmer_paiement(commande=cmd)
    avant = [(x["statut"], x["paye_le"]) for x in _lignes()]
    A._formation_ia_confirmer_paiement(commande=cmd)
    assert [(x["statut"], x["paye_le"]) for x in _lignes()] == avant


def test_une_place_NON_REGLEE_cesse_de_tenir_le_creneau(client):
    """C'EST LA CONSÉQUENCE DIRECTE DU PAIEMENT IMMÉDIAT. Le client part vers la
    caisse ; s'il n'y va pas, le créneau doit redevenir libre. Sans ce délai, un
    panier abandonné bloquerait une date jusqu'à la fin de la campagne — et
    l'écran la montrerait simplement « prise », sans que personne sache
    pourquoi ni puisse la rendre."""
    cre = _creneaux()[0]
    _poster(client, [(TOUS[0], cre)])
    vieux = (datetime.datetime.utcnow()
             - datetime.timedelta(minutes=F.RETENUE_MINUTES + 5)).isoformat()
    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute(A.registre_sql(
        "UPDATE formation_ia_resa SET statut='en_attente_paiement', created_at=%s",
        "UPDATE formation_ia_resa SET statut='en_attente_paiement', created_at=?"),
        (vieux,))
    conn.commit()
    try: conn.close()
    except Exception: pass
    libre = [c for c in client.get("/api/formation/referentiel").get_json()["creneaux"]
             if c["date"] == cre][0]["libre"]
    assert libre, "une place jamais réglée bloque encore le créneau"
    # Et elle est REPRENABLE : le calendrier ne ment pas sur ce qu'il propose.
    r = _poster(client, [(TOUS[1], cre)], siret=SIRET_B, email="b@ex.fr")
    assert r.status_code == 200, r.get_json()


def test_une_place_REGLEE_tient_le_creneau_QUEL_QUE_SOIT_son_age(client):
    """LE TÉMOIN NÉGATIF. Sans lui, la règle précédente serait verte sur un
    délai qui libère TOUT, y compris les séances payées."""
    cre = _creneaux()[0]
    _poster(client, [(TOUS[0], cre)])
    vieux = (datetime.datetime.utcnow() - datetime.timedelta(days=90)).isoformat()
    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute(A.registre_sql(
        "UPDATE formation_ia_resa SET statut='payee', created_at=%s",
        "UPDATE formation_ia_resa SET statut='payee', created_at=?"), (vieux,))
    conn.commit()
    try: conn.close()
    except Exception: pass
    libre = [c for c in client.get("/api/formation/referentiel").get_json()["creneaux"]
             if c["date"] == cre][0]["libre"]
    assert not libre, "une séance PAYÉE a cessé de tenir son créneau"


def test_le_calendrier_et_la_RESERVATION_lisent_la_MEME_condition():
    """Deux conditions écrites séparément divergent : le calendrier annoncerait
    libre un créneau que la réservation refuserait, ou l'inverse — et le client
    verrait une date se dérober au dernier geste."""
    src = io.open(os.path.join(RACINE, "app.py"), encoding="utf-8").read()
    assert src.count("_formation_ia_tient_le_creneau()") >= 3, (
        "la condition « tient le créneau » n'est pas partagée")
    # Et elle n'est écrite qu'UNE fois.
    assert src.count("statut = 'en_attente_paiement' \"") == 1, (
        "la condition d'expiration est écrite à plusieurs endroits")


def test_le_remboursement_ne_part_pas_DEUX_fois(client):
    """DEUX GARDES QUI SE COUVRENT, ET UNE DÉPENDANCE COMMUNE. Le second clic
    est arrêté deux fois : par la relecture du statut avant toute écriture, et
    par l'écriture conditionnelle (`WHERE statut != 'annulee'`). Supprimer l'un
    des deux ne change rien séquentiellement — l'autre arrête encore, et cette
    règle ne voit aucune différence. C'est une bonne propriété du code, pas un
    trou dans la mesure : la course n'existe qu'en production, et le second
    garde est là pour elle.

    CE QUE LA RÈGLE ATTRAPE QUAND MÊME, mesuré par mutation : les deux gardes
    relisent la MÊME valeur, `'annulee'`. Si l'écriture note autre chose — une
    faute de frappe, un statut renommé d'un seul côté — les deux tombent
    ensemble, le second clic rembourse une seconde fois, et le compteur
    d'appels ci-dessous le dit. Une seule substitution suffit à le prouver.

    ON COMPTE LES APPELS, PAS LE TOTAL EN BASE. Mesuré aussi : un second
    passage réécrit les mêmes montants, si bien que le total ne bouge pas — une
    règle qui ne regarde que lui reste verte pendant que l'ordre de
    remboursement part une seconde fois chez Stripe."""
    jet = _poser_a(client, 20)
    vrai = A._formation_ia_rembourser
    appels = []

    def _mouchard(r, cents, jeton):
        appels.append(cents)
        return vrai(r, cents, jeton)

    A._formation_ia_rembourser = _mouchard
    try:
        client.post("/api/formation/annulation", json={"jeton": jet})
        r2 = client.post("/api/formation/annulation", json={"jeton": jet})
    finally:
        A._formation_ia_rembourser = vrai
    assert r2.get_json().get("deja") is True
    assert appels == [48000], (
        "l'ordre de remboursement est parti %d fois : %s" % (len(appels), appels))
    lg = _lignes()[0]
    assert (int(lg["rembourse_cents"] or 0)
            + int(lg["remboursement_du"] or 0)) == 48000, dict(lg)


def test_une_seance_ANNULEE_par_la_route_ne_recoit_plus_de_RELANCE(client):
    """LA COUTURE ENTRE DEUX SOUS-SYSTÈMES, MESURÉE DE BOUT EN BOUT. Le balayage
    des relances lit `statut IN ('confirmee','payee')` ; la route d'annulation
    ÉCRIT `'annulee'`. Les deux listes vivent à deux endroits et rien ne les
    relie : si elles divergent, le client qui vient d'annuler reçoit « votre
    formation a lieu dans une semaine ».

    CE QU'ELLE APPORTE, SANS L'EXAGÉRER. Les deux bouts sont déjà tenus chacun
    de son côté — le balayage par une règle qui insère directement une ligne
    annulée, l'écriture par les règles d'annulation qui relisent le statut en
    base. Aucune mutation d'un seul côté ne fait donc tomber celle-ci SEULE :
    les voisines tombent avec. Elle n'est pas là pour attraper ce qu'elles
    attrapent, mais pour que le RACCORD soit écrit quelque part — la question
    « un client qui annule est-il encore relancé ? » a ici une réponse mesurée,
    au lieu d'être déduite en lisant deux fichiers.

    LE TÉMOIN POSITIF N'EST PAS DÉCORATIF : sans lui, une relance qui ne
    partirait JAMAIS — fenêtre fausse, colonne absente — rendrait cette règle
    verte pour une raison sans rapport avec ce qu'elle prétend."""
    jet = _poser_a(client, 5)                     # dans la fenêtre J-7 (0 < 5 <= 7)
    ref = datetime.datetime.utcnow().date()
    assert A._formation_ia_relances(ref, envoyer=False), (
        "témoin : sans annulation, la relance J-7 est bien due")
    assert client.post("/api/formation/annulation", json={"jeton": jet}
                       ).get_json()["ok"]
    assert A._formation_ia_relances(ref, envoyer=False) == [], (
        "une séance annulée est encore relancée")


# ══════════════════════════════════════════════════════════════════════════
#  LE FRANÇAIS DU PARCOURS — mesuré sur les textes RÉELLEMENT ÉMIS
# ══════════════════════════════════════════════════════════════════════════
# Ces mots n'existent pas en français sans leur accent : les rencontrer dans un
# texte adressé au client, c'est une faute, jamais un choix de graphie. « règle »
# et « accuse » en sont volontairement absents — ils ont un homographe valide, et
# une règle qui se trompe sur eux serait plus nuisible que le défaut qu'elle
# chasse.
_SANS_ACCENT = re.compile(
    r"(?<![\w-])(seances?|creneaux?|annulees?|reglees?|payees?|confirmees?"
    r"|reservations?|reservees?|recues?|recu|liberees?|libere|remboursees?"
    r"|deja|etait|ete|apres|journees?|equipe|etes|meme|posees?|securise"
    r"|enregistree|redirigee)(?![\w-])", re.I)


def _corpus_client(client, monkeypatch):
    """TOUT ce qui part vers un lecteur humain sur un parcours complet — client
    ET CONSEILPREV : réponses de l'API et corps de courriel, sujets compris."""
    vus = []
    monkeypatch.setattr(A, "send_email_smart",
                        lambda to, nom, sujet, corps, **k: vus.append(
                            (sujet or "") + " " + (corps or "")))

    def _dire(rep):
        j = rep.get_json() or {}
        for k in ("message", "error"):
            if j.get(k):
                vus.append(j[k])
        for x in (j.get("seances") or []):
            vus.append(str(x.get("libelle") or ""))

    cre = _creneaux()
    _dire(_poster(client, [(TOUS[0], cre[0]), (TOUS[1], cre[1])], gratuit=TOUS[1]))
    # LES REFUS AUSSI : ce sont les phrases qu'un client lit le plus souvent.
    _dire(_poster(client, [(TOUS[2], cre[0]), (TOUS[3], cre[0])], email="b@ex.fr"))
    _dire(_poster(client, [(TOUS[2], "2000-01-01")], email="c@ex.fr"))
    _dire(_poster(client, [(TOUS[0], cre[2])]))
    # LE PAIEMENT, PUIS LE RAPPEL, PUIS L'ANNULATION.
    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute("SELECT commande FROM formation_ia_resa WHERE gratuit=0 LIMIT 1")
    cmd = dict(cur.fetchone())["commande"]
    conn.close()
    A._formation_ia_confirmer_paiement(commande=cmd)
    jet = _poser_a(client, 9, payee=True)
    A._formation_ia_relances(datetime.datetime.utcnow().date()
                             + datetime.timedelta(days=2), envoyer=True)
    _dire(client.post("/api/formation/annulation", json={"jeton": jet}))
    _dire(client.post("/api/formation/annulation", json={"jeton": jet}))
    _dire(client.post("/api/formation/annulation", json={"jeton": "x" * 40}))
    return vus


def test_aucun_texte_envoye_a_un_HUMAIN_ne_perd_ses_accents(client, monkeypatch):
    """POURQUOI CETTE RÈGLE EXISTE, ET CE QU'ELLE A ATTRAPÉ. Les phrases écrites
    dans app.py l'étaient sans accents ; celles qui viennent de formations_ia les
    portent. Les deux se rejoignent dans la MÊME phrase à l'écran :

        « Seance annulee. Annulation à moins de 7 jours : aucun remboursement
          n'est prévu. Le creneau est libere. »

    Aucune règle ne pouvait le voir : chaque moitié était juste de son côté, et
    le défaut n'apparaît qu'une fois la phrase assemblée. Celle-ci mesure donc
    les textes TELS QU'ILS PARTENT — réponses d'API et corps de courriel —, sur
    un parcours complet : réservation, refus, paiement, rappel, annulation.

    LE TÉMOIN POSITIF N'EST PAS UN ORNEMENT : sans lui, un parcours qui
    n'émettrait plus rien du tout rendrait la règle verte."""
    vus = _corpus_client(client, monkeypatch)
    assert len(vus) >= 14, "le parcours n'a presque rien émis : %d textes" % len(vus)
    accentues = [t for t in vus if re.search(r"[éèêàçùîôûœÉÈÀ]", t)]
    assert len(accentues) >= 10, (
        "témoin : seuls %d textes sur %d portent un accent — le parcours ne "
        "produit sans doute plus les phrases attendues" % (len(accentues), len(vus)))
    fautes = sorted({m.group(0) for t in vus for m in _SANS_ACCENT.finditer(t)})
    assert not fautes, (
        "mots privés de leur accent dans un texte envoyé à un humain : %s\n"
        "→ %s" % (fautes, [t[:160] for t in vus
                           if _SANS_ACCENT.search(t)][:4]))


# ══════════════════════════════════════════════════════════════════════════
#  LA PAGE DIT LE MODÈLE — sans le recopier
# ══════════════════════════════════════════════════════════════════════════
def test_la_page_dit_que_le_PAIEMENT_retient_la_place():
    """LA MESURE PORTE SUR LE BON ÉLÉMENT. « a.paiement » figure deux fois dans
    cette fonction — au bloc tarif et à la règle d'annulation. Chercher la
    chaîne dans la fonction entière rendait la règle verte alors que le bloc
    tarif avait été vidé : mesuré par mutation."""
    i = PAGE.index("function rendreAnnulation(")
    corps = PAGE[i:PAGE.index("\n  }", i)]
    assert 'id="of-paiement"' in PAGE, "le bloc tarif n'a pas de place pour le dire"
    m = re.search(r"of-paiement'\);\s*\n?\s*if\(op\)\s*op\.textContent\s*=\s*([^;]+);",
                  corps)
    assert m, "le bloc tarif ne reçoit rien : %s" % corps[:300]
    assert "a.paiement" in m.group(1), (
        "le bloc tarif affiche « %s » au lieu de la règle du serveur"
        % m.group(1).strip())


def test_la_page_annonce_le_bareme_SANS_le_recopier():
    """480 € et 960 € se dérivent du tarif. Les écrire dans la page les ferait
    vivre longtemps après un changement de taux — et c'est le texte affiché qui
    engage."""
    i = PAGE.index("function rendreAnnulation(")
    corps = PAGE[i:PAGE.index("\n  }", i)]
    assert "a.avant" in corps and "a.apres" in corps
    # LA FEUILLE DE STYLE EST HORS SUJET : « border-radius:50% » n'engage
    # personne. On ne regarde que ce que le client LIT — le balisage et le
    # script — sans quoi la règle tombe sur une bordure arrondie.
    sans_css = re.sub(r"<style[^>]*>.*?</style>", "", PAGE, flags=re.S)
    for chiffre in ("480", "960", "50 %"):
        assert chiffre not in sans_css, (
            "le barème est recopié dans la page (« %s ») au lieu d'être lu"
            % chiffre)
