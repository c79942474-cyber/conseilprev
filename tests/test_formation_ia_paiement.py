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
        "email": email, "entreprise": "PAYE SAS", "siret": siret,
        "telephone": "+33 6 12 34 56 78", "lieu": "9 av. du Test, 75000 Paris"})


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
        "telephone": "+33 6 12 34 56 78", "lieu": "9 av. du Test, 75000 Paris",
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
           "data": {"object": {"payment_status": "paid",
                               "metadata": {"type": "formation-ia", "resa_id": str(rid)}}}}
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


# ══════════════════════════════════════════════════════════════════════════
#  CE QUI PART RÉELLEMENT À LA CAISSE, pour un panier de PLUSIEURS séances
# ══════════════════════════════════════════════════════════════════════════
#  RIEN NE LE MESURAIT. Les règles ci-dessus éprouvent une séance à la fois,
#  posée par l'ancien envoi. Depuis que le panier accepte jusqu'à quatre
#  formations en un geste, c'est le NOMBRE de lignes envoyées à Stripe et leur
#  somme qui décident de ce qui est prélevé — et personne ne les regardait.
def _panier(client, n, siret, email, gratuit=None):
    cr = _creneaux()
    cles = [s["cle"] for s in F.SUJETS][:n]
    return client.post("/api/formation/inscription", json={
        "seances": [{"sujet": c, "creneau": cr[i]} for i, c in enumerate(cles)],
        "gratuit": gratuit or "",
        "nom": "Payeur", "prenom": "Alex", "email": email,
        "entreprise": "PAYE SAS", "siret": siret,
        "telephone": "+33 6 12 34 56 78", "lieu": "9 av. du Test, 75000 Paris"})


def _lignes_stripe(created):
    assert len(created) == 1, "il faut UNE session pour la commande : %d" % len(created)
    return created[0]["line_items"]


@pytest.mark.parametrize("n,attendu", [(1, 0), (2, 1), (3, 2), (4, 3)])
def test_la_caisse_reçoit_UNE_ligne_par_seance_PAYANTE_et_pas_une_de_plus(
        client, monkeypatch, n, attendu):
    """LA RÈGLE QUE LE CABINET A DEMANDÉE, MESURÉE LÀ OÙ L'ARGENT PASSE : la
    première formation choisie est offerte, les suivantes sont au tarif. Une
    seule séance n'ouvre donc aucun paiement ; quatre en ouvrent un de trois
    lignes.

    ON LIT LES LIGNES ENVOYÉES À STRIPE, pas le devis. Le devis peut être juste
    pendant que la caisse facture autre chose — c'est exactement le genre
    d'écart qui ne se découvre qu'au relevé bancaire."""
    created = []
    monkeypatch.setitem(sys.modules, "stripe", _fake_stripe(created))
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    j = _panier(client, n, "9000002%02d" % n, "p%d@ex.fr" % n).get_json()
    assert j["ok"], j
    if not attendu:
        assert created == [], "une commande sans séance payante a ouvert un paiement"
        return
    items = _lignes_stripe(created)
    assert len(items) == attendu, (
        "%d séance(s) choisie(s) : %d ligne(s) facturée(s) au lieu de %d — %s"
        % (n, len(items), attendu,
           [x["price_data"]["product_data"]["name"] for x in items]))
    # ET CHAQUE LIGNE EST AU TARIF DU MODULE, jamais à un montant recopié.
    for it in items:
        assert it["price_data"]["unit_amount"] == F.TARIF_HT_CENTS, it
        assert it["quantity"] == 1, it


def test_la_seance_OFFERTE_n_apparait_JAMAIS_dans_les_lignes_facturees(
        client, monkeypatch):
    """La désigner autrement que par son prix : on prend la TROISIÈME comme
    offerte, et on vérifie qu'elle est absente de la caisse. Une règle qui
    n'éprouverait que la première serait verte sur un code qui saute
    systématiquement la ligne 1."""
    created = []
    monkeypatch.setitem(sys.modules, "stripe", _fake_stripe(created))
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    cles = [s["cle"] for s in F.SUJETS]
    j = _panier(client, 4, "900000299", "p99@ex.fr", gratuit=cles[2]).get_json()
    assert j["ok"] and j["devis"]["gratuite"] == cles[2], j["devis"]
    noms = [x["price_data"]["product_data"]["name"] for x in _lignes_stripe(created)]
    offert = F.sujet(cles[2])["titre"]
    assert len(noms) == 3, noms
    assert not any(offert in x for x in noms), (
        "la séance offerte « %s » est facturée : %s" % (offert, noms))
    # Et les trois autres y sont bien, chacune une fois.
    for k in (0, 1, 3):
        t = F.sujet(cles[k])["titre"]
        assert sum(1 for x in noms if t in x) == 1, (t, noms)


def test_la_somme_facturee_est_CELLE_du_devis_et_non_une_autre(client, monkeypatch):
    """DEUX CALCULS DU MÊME MONTANT DIVERGENT le jour où l'un des deux change ;
    c'est celui qui est prélevé qui a raison, et on ne le sait qu'après. On
    additionne donc ce que Stripe reçoit et on le confronte au devis rendu au
    client — le même objet que la page affiche."""
    created = []
    monkeypatch.setitem(sys.modules, "stripe", _fake_stripe(created))
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    j = _panier(client, 4, "900000288", "p88@ex.fr").get_json()
    total = sum(x["price_data"]["unit_amount"] * x["quantity"]
                for x in _lignes_stripe(created))
    assert total == j["devis"]["ht_cents"], (
        "la caisse prélève %d c, le devis annonce %d c"
        % (total, j["devis"]["ht_cents"]))
    assert total == 3 * F.TARIF_HT_CENTS, total
