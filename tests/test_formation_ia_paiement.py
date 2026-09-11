# -*- coding: utf-8 -*-
"""Le paiement en ligne de la séance payante — mesuré sur ce que le SERVEUR
construit, jamais sur ce que le client affirme.

CE QUE CES RÈGLES ÉPROUVENT. Une séance payante (rang ≥ 1) ouvre une session de
paiement Stripe QUAND une clé est configurée, et le montant prélevé vient de
`formations_ia.tarif`, la même source que le prix affiché — jamais du corps que
le client a posté. Une séance gratuite ne touche JAMAIS Stripe. Sans clé, la
séance payante retombe en devis, exactement comme le catalogue existant. Et le
webhook « paiement reçu » fait passer la réservation en « payée ».

COMMENT ON MESURE SANS APPELER STRIPE. On injecte un faux module `stripe` : il
capture les arguments de `checkout.Session.create` au lieu d'ouvrir une session
réelle. La règle lit alors le `unit_amount` que le serveur a décidé, et le
confronte au tarif du module. Un taux de TVA fixe (STRIPE_TAX_RATE_ID) fait
prélever le HT, la TVA étant détaillée par Stripe — c'est le cas de production.
"""
import datetime
import json
import sys
import types

import pytest

import app as A
import formations_ia as F

SIRET_P = "900000200"


def _fake_stripe(created):
    """Un faux module stripe qui NOTE les sessions au lieu de les créer."""
    st = types.ModuleType("stripe")
    st.api_key = None
    st.max_network_retries = 0

    class _Sess:
        @staticmethod
        def create(**kw):
            created.append(kw)
            return {"id": "cs_test_1", "url": "https://checkout.stripe.test/cs_test_1"}

    class _Checkout:
        Session = _Sess

    class _TaxRate:
        @staticmethod
        def create(**kw):
            return {"id": "txr_created"}

    class _Webhook:
        @staticmethod
        def construct_event(payload, sig, secret):
            raw = payload.decode("utf-8") if isinstance(payload, (bytes, bytearray)) else payload
            return json.loads(raw)

    st.checkout = _Checkout
    st.TaxRate = _TaxRate
    st.Webhook = _Webhook
    return st


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
def client(monkeypatch):
    _purge()
    # Taux de TVA fixe : le tarif prélevé est le HT, la TVA détaillée par Stripe
    # — sans le moindre appel réseau pour créer un TaxRate.
    monkeypatch.setenv("STRIPE_TAX_RATE_ID", "txr_fixed")
    c = A.app.test_client()
    yield c
    _purge()


def _creneaux():
    return [x["date"] for x in F.creneaux(datetime.datetime.utcnow().date())]


def _resa(client, sujet, creneau, siret=SIRET_P, email="pay@ex.fr"):
    return client.post("/api/formation/inscription", json={
        "sujet": sujet, "creneau": creneau, "nom": "Payeur", "prenom": "Alex",
        "email": email, "entreprise": "PAYE SAS", "siret": siret})


def test_la_seance_gratuite_ne_touche_jamais_stripe(client, monkeypatch):
    """La première séance est offerte : aucune session de paiement ne doit
    s'ouvrir, même clé Stripe configurée."""
    created = []
    monkeypatch.setitem(sys.modules, "stripe", _fake_stripe(created))
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    cr = _creneaux()
    r = _resa(client, "gouvernance-ia", cr[-1]).get_json()
    assert r["gratuit"] is True and r["statut"] == "confirmee"
    assert created == [], "une séance offerte a pourtant ouvert un paiement"


def test_la_seance_payante_ouvre_une_session_stripe_au_bon_montant(client, monkeypatch):
    """LE CŒUR DE CE VOLET. La deuxième séance ouvre un paiement Stripe, en mode
    « payment », au tarif du MODULE (HT, la TVA étant portée par le taux)."""
    created = []
    monkeypatch.setitem(sys.modules, "stripe", _fake_stripe(created))
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    cr = _creneaux()
    assert _resa(client, "gouvernance-ia", cr[-1]).status_code == 200   # 1re offerte
    r2 = _resa(client, "securite-ia", cr[-2]).get_json()                # 2e payante
    assert r2["ok"] and r2["gratuit"] is False and r2.get("paiement") is True
    assert (r2.get("url") or "").startswith("https://checkout.stripe")
    assert len(created) == 1, "la séance payante n'a pas ouvert exactement un paiement"
    kw = created[0]
    assert kw["mode"] == "payment"
    ligne = kw["line_items"][0]["price_data"]
    assert ligne["currency"] == "eur"
    assert ligne["unit_amount"] == F.TARIF_HT_CENTS, (
        "le montant prélevé (%s) n'est pas le tarif du module (%s)"
        % (ligne["unit_amount"], F.TARIF_HT_CENTS))
    assert kw["metadata"]["type"] == "formation-ia"


def test_le_montant_stripe_ne_vient_pas_du_client(client, monkeypatch):
    """Le client a beau poster un prix, le serveur prélève le sien. C'est la
    même discipline que le reste de l'offre, poussée jusqu'à la caisse."""
    created = []
    monkeypatch.setitem(sys.modules, "stripe", _fake_stripe(created))
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    cr = _creneaux()
    assert _resa(client, "gouvernance-ia", cr[-1]).status_code == 200
    client.post("/api/formation/inscription", json={
        "sujet": "securite-ia", "creneau": cr[-2], "nom": "Payeur", "prenom": "Alex",
        "email": "pay@ex.fr", "entreprise": "PAYE SAS", "siret": SIRET_P,
        "montant_cents": 1, "ht_cents": 1, "prix": 1, "gratuit": True})
    assert created, "aucune session de paiement ouverte"
    assert created[0]["line_items"][0]["price_data"]["unit_amount"] == F.TARIF_HT_CENTS


def test_sans_cle_stripe_la_seance_payante_reste_un_devis(client, monkeypatch):
    """Pas de clé, pas de caisse en ligne : la séance payante est enregistrée en
    devis et facturée hors ligne — le repli du catalogue existant."""
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    created = []
    monkeypatch.setitem(sys.modules, "stripe", _fake_stripe(created))
    cr = _creneaux()
    assert _resa(client, "gouvernance-ia", cr[-1]).status_code == 200
    r2 = _resa(client, "securite-ia", cr[-2]).get_json()
    assert r2["gratuit"] is False and r2["statut"] == "devis"
    assert r2.get("paiement") is False
    assert created == [], "un paiement s'est ouvert alors qu'aucune clé n'est configurée"


def test_le_webhook_confirme_la_seance_payee(client, monkeypatch):
    """« checkout.session.completed » fait passer la réservation en « payée ».
    C'est le seul chemin qui encaisse : sans lui, une séance payée resterait
    « en attente » pour toujours."""
    created = []
    monkeypatch.setitem(sys.modules, "stripe", _fake_stripe(created))
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
    cr = _creneaux()
    _resa(client, "gouvernance-ia", cr[-1])          # gratuite
    _resa(client, "securite-ia", cr[-2])             # payante → en_attente_paiement

    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute("SELECT id FROM formation_ia_resa WHERE statut='en_attente_paiement' "
                "ORDER BY id DESC")
    rid = int(dict(cur.fetchone())["id"])
    # Un identifiant d'événement neuf : le webhook ignore les doublons déjà vus.
    ev = "evt_ftest_%d" % rid
    try:
        cur.execute("DELETE FROM stripe_events WHERE event_id=" +
                    ("%s" if A.REGISTRE_USE_PG else "?"), (ev,))
        conn.commit()
    except Exception:
        pass
    try: conn.close()
    except Exception: pass

    evt = {"id": ev, "type": "checkout.session.completed",
           "data": {"object": {"metadata": {"type": "formation-ia", "resa_id": str(rid)}}}}
    r = client.post("/api/stripe/webhook", data=json.dumps(evt),
                    headers={"Stripe-Signature": "t=1,v1=x", "Content-Type": "application/json"})
    assert r.status_code == 200

    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute(A.registre_sql("SELECT statut FROM formation_ia_resa WHERE id=%s",
                               "SELECT statut FROM formation_ia_resa WHERE id=?"), (rid,))
    statut = dict(cur.fetchone())["statut"]
    try: conn.close()
    except Exception: pass
    assert statut == "payee", "le webhook n'a pas confirmé la séance payée (statut=%s)" % statut
