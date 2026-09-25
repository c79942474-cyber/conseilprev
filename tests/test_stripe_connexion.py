# -*- coding: utf-8 -*-
"""Un paiement ENCAISSÉ confirme ; un paiement NON encaissé ne confirme pas.

Ce que ces règles mesurent, sur le fil et sans réseau : la VRAIE bibliothèque
`stripe` parle à un faux serveur local (fixture `faux_stripe`), le VRAI
transport Brevo à un autre (`faux_brevo`), et les notifications sont signées
comme Stripe les signe, puis lues par le VRAI `Webhook.construct_event`.

LE DÉFAUT MESURÉ, avant correction (rapport du 24/09/2026) :
  · le webhook activait une offre ou confirmait une séance sur un
    `checkout.session.completed` à `payment_status=unpaid` ;
  · un échec de traitement répondait 200 et marquait l'événement vu — le
    paiement était perdu, Stripe ne réessayait jamais ;
  · `client_reference_id` d'une formation (un n° d'inscription) était pris
    pour un n° de compte, et le client Stripe d'un acheteur de formation
    était écrit sur ce compte ;
  · aucune page de retour ne vérifiait la session : « Paiement reçu » était
    affiché sans condition ;
  · la facturation RaaS créait une facture VIDE puis répondait « échec » ;
  · une résiliation refusée par Stripe effaçait quand même le lien local.

Trois familles :
  · le CONTRAT : ce que le site envoie et accepte — vert avant comme après ;
  · un DÉFAUT par règle — rouge sur le code de base, vert une fois corrigé ;
  · chaque assertion dit ce qui a été OBSERVÉ.
"""
import datetime
import io
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time

import pytest
import stripe

import app as A
import formations_ia as F
from conftest import SECRET_WEBHOOK_RECETTE
from faux_services import evenement_stripe, signer_stripe

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = shutil.which("node")
UA_STRIPE = "Stripe/1.0 (+https://stripe.com/docs/webhooks)"
NAVIGATEUR = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Firefox/130.0",
              "Accept": "application/json", "Accept-Language": "fr-FR"}
AUJOURD_HUI = datetime.datetime.utcnow().date().isoformat()


# ══════════════════════════════════════════════════════════════════════════
#  LA BASE : clients, réservations, factures — nettoyée avant et après
# ══════════════════════════════════════════════════════════════════════════
def _q(sql, args=()):
    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute(sql, args)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def _exec(sql, args=()):
    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute(sql, args)
    conn.commit()
    conn.close()


def purger():
    conn = A.registre_get_db(); cur = conn.cursor()
    A._formation_ia_table(cur, conn)
    A._form_tables(cur, conn)
    cur.execute("CREATE TABLE IF NOT EXISTS stripe_events (event_id TEXT PRIMARY KEY, processed_at TEXT)")
    for sql in ("DELETE FROM formation_ia_resa", "DELETE FROM form_inscriptions",
                "DELETE FROM stripe_events",
                "DELETE FROM raas_invoices WHERE numero LIKE 'F-RECETTE-%'",
                "DELETE FROM client_relances WHERE related_ref LIKE 'F-RECETTE-%'",
                "DELETE FROM client_relances WHERE related_ref='sub_impaye'",
                "DELETE FROM form_sessions WHERE lieu LIKE 'RECETTE %'",
                "DELETE FROM clients WHERE email LIKE '%@recette.test'",
                "DELETE FROM clients WHERE email LIKE 'efface-%@anonyme.invalid'"):
        try:
            cur.execute(sql); conn.commit()
        except Exception:
            conn.rollback()
    conn.close()
    A._FORM_TAX_RATE_CACHE["id"] = None


@pytest.fixture
def base():
    purger()
    yield
    purger()


@pytest.fixture
def client(base):
    return A.app.test_client()


def creer_client(email, plan="gratuit", sub=None, cust=None):
    _exec("INSERT INTO clients (nom_entreprise, email, mot_de_passe_hash, actif, date_creation, "
          "plan, stripe_subscription_id, stripe_customer_id, generation_session) "
          "VALUES (?,?,?,?,?,?,?,?,0)",
          ("RECETTE " + email, email, "x", 1, datetime.datetime.utcnow().isoformat(),
           plan, sub, cust))
    return _q("SELECT id FROM clients WHERE email=?", (email,))[0]["id"]


def client_row(cid):
    return _q("SELECT * FROM clients WHERE id=?", (cid,))[0]


def connecter(c, cid):
    with c.session_transaction() as s:
        s["client_id"] = cid
        s["sgen"] = 0


def admin(c):
    with c.session_transaction() as s:
        s["is_conseilprev"] = True


def vu(event_id):
    return bool(_q("SELECT 1 AS x FROM stripe_events WHERE event_id=?", (event_id,)))


def creneaux():
    return [x["date"] for x in F.creneaux(datetime.datetime.utcnow().date())]


def panier(c, n=2, siret="900000777", email="payeur@recette.test", dates=None):
    """n séances : la première offerte, les suivantes payantes."""
    cr = dates or creneaux()
    cles = [s["cle"] for s in F.SUJETS][:n]
    r = c.post("/api/formation/inscription", json={
        "seances": [{"sujet": k, "creneau": cr[i]} for i, k in enumerate(cles)],
        "nom": "Payeur", "prenom": "Alex", "email": email,
        "entreprise": "RECETTE SAS", "siret": siret,
        "telephone": "+33 6 12 34 56 78", "lieu": "9 av. du Test, 75000 Paris"})
    assert r.status_code == 200, r.get_json()
    return r.get_json()


def statuts(commande):
    return [x["statut"] for x in _q(
        "SELECT statut FROM formation_ia_resa WHERE commande=? AND gratuit=0 ORDER BY id",
        (commande,))]


def session_payee(commande, **extra):
    o = {"id": "cs_test_recette", "object": "checkout.session", "mode": "payment",
         "status": "complete", "payment_status": "paid", "amount_total": 96000,
         "currency": "eur", "client_reference_id": commande, "customer": None,
         "subscription": None,
         "metadata": {"type": "formation-ia", "commande": commande}}
    o.update(extra)
    return o


def poster(c, objet, type_="checkout.session.completed", evt=None, sig=None, charge=None):
    """Une notification signée comme Stripe la signe. Rend (réponse, id)."""
    evt, charge_ = evenement_stripe(objet, type_, evt)
    charge = charge if charge is not None else charge_
    h = {"User-Agent": UA_STRIPE, "Content-Type": "application/json; charset=utf-8"}
    if sig is not False:
        h["Stripe-Signature"] = sig or signer_stripe(charge, SECRET_WEBHOOK_RECETTE)
    return c.post("/api/stripe/webhook", data=charge, headers=h), evt


def destinataires(fb):
    return [x.json["to"][0]["email"] for x in fb.recues("POST", "/v3/smtp/email")]


def sujets(fb):
    return [x.json["subject"] for x in fb.recues("POST", "/v3/smtp/email")]


def session_catalogue_future():
    """Une session du catalogue encore réservable (le refus des sessions
    passées fait partie de ce qui est mesuré ici)."""
    rows = _q("SELECT id FROM form_sessions WHERE actif=1 AND date_session > ? "
              "ORDER BY date_session LIMIT 1", (AUJOURD_HUI,))
    assert rows, "aucune session future dans le calendrier amorcé"
    return rows[0]["id"]


def inscrire_catalogue(c, sid, email="catalogue@recette.test", participants=1):
    return c.post("/api/formations/inscription", json={
        "session_id": sid, "participants": participants,
        "nom": "N", "prenom": "P", "email": email}, headers=NAVIGATEUR).get_json()


def facture_raas(cid, numero, montant=1000, statut_echeance="envoyee"):
    due = [{"echeance": 1, "montant": montant, "due": "2026-01-01", "status": statut_echeance}]
    _exec("INSERT INTO raas_invoices (client_id, numero, amount_eur, status, due_json, issued_at) "
          "VALUES (?,?,?,?,?,?)", (cid, numero, montant, "emise", json.dumps(due), "2026-01-01"))


def facture_row(numero):
    r = _q("SELECT status, due_json FROM raas_invoices WHERE numero=?", (numero,))[0]
    return r["status"], json.loads(r["due_json"])[0]


def _node(harnais):
    if not NODE:
        pytest.skip("node absent : le code de la page ne peut pas être exécuté")
    with tempfile.TemporaryDirectory() as d:
        h = os.path.join(d, "h.js")
        io.open(h, "w", encoding="utf-8").write(harnais)
        r = subprocess.run([NODE, h], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail("le scénario n'a pas tourné :\n%s" % (r.stderr or "")[-1500:])
    return json.loads(r.stdout)


def _tranche(src, debut, fin):
    i = src.find(debut)
    assert i >= 0, "%r est introuvable" % debut
    j = src.find(fin, i)
    assert j > i, "fin de %r introuvable" % debut
    return src[i:j + len(fin)]


# ══════════════════════════════════════════════════════════════════════════
#  A. LE CONTRAT — ce que le site envoie et accepte
# ══════════════════════════════════════════════════════════════════════════
def test_la_caisse_formation_ia_recoit_le_contrat_attendu(client, faux_stripe, faux_brevo):
    j = panier(client, n=2)
    assert j["paiement"] is True and j["url"].startswith(faux_stripe.url), j
    envois = faux_stripe.recues("POST", "/v1/checkout/sessions")
    assert len(envois) == 1, "sessions ouvertes : %d" % len(envois)
    r = envois[0]
    assert r.entetes["authorization"] == "Bearer sk_test_recette_locale"
    assert r.entetes["content-type"] == "application/x-www-form-urlencoded"
    assert r.entetes["stripe-version"] == stripe.api_version
    f = r.form
    assert f["mode"] == "payment"
    assert f["line_items[0][price_data][currency]"] == "eur"
    assert f["line_items[0][price_data][unit_amount]"] == str(F.TARIF_HT_CENTS)
    assert f["line_items[0][tax_rates][0]"] == "txr_recette"
    assert "line_items[1][quantity]" not in f, "la séance offerte est facturée"
    assert f["metadata[type]"] == "formation-ia"
    assert f["metadata[commande]"] == j["commande"] == f["client_reference_id"]
    assert "/formation?paiement=ok" in f["success_url"], f["success_url"]


def test_une_panne_stripe_remet_la_commande_en_devis(client, faux_stripe, faux_brevo):
    faux_stripe.pannes["POST /v1/checkout/sessions"] = (
        500, {"error": {"type": "api_error", "message": "panne simulée"}})
    j = panier(client, n=2)
    assert j["paiement"] is False
    assert statuts(j["commande"]) == ["devis"], statuts(j["commande"])


def test_le_remboursement_porte_la_cle_du_jeton_et_ne_part_qu_une_fois(base, faux_stripe):
    r = {"stripe_session_id": "cs_test_42"}
    for _ in range(2):          # un second appel = réseau coupé puis rejoué
        A._formation_ia_rembourser(r, 48000, "JETONrecette")
    rb = faux_stripe.recues("POST", "/v1/refunds")
    assert len(rb) == 2, "remboursements envoyés : %d" % len(rb)
    assert {x.entetes["idempotency-key"] for x in rb} == {"formation-ia-rb-JETONrecette"}
    assert rb[0].form == {"payment_intent": "pi_test_cs_test_42", "amount": "48000"}
    assert len(faux_stripe.remboursements) == 1, "Stripe a créé %d remboursement(s)" % len(faux_stripe.remboursements)


def test_une_notification_signee_confirme_la_commande(client, faux_stripe, faux_brevo):
    j = panier(client, n=2)
    r, evt = poster(client, session_payee(j["commande"]))
    assert r.status_code == 200, r.get_json()
    assert statuts(j["commande"]) == ["payee"], statuts(j["commande"])
    assert vu(evt), "événement traité mais non retenu comme vu"


def test_une_notification_signee_active_l_offre(client, faux_stripe, faux_brevo):
    cid = creer_client("abonne@recette.test")
    r, _ = poster(client, {"id": "cs_ab", "object": "checkout.session", "mode": "subscription",
                           "payment_status": "paid", "client_reference_id": str(cid),
                           "customer": "cus_ab", "subscription": "sub_ab",
                           "metadata": {"client_id": str(cid), "plan": "pro"}})
    row = client_row(cid)
    assert r.status_code == 200, r.get_data(as_text=True)
    assert (row["plan"], row["stripe_customer_id"], row["stripe_subscription_id"]) == ("pro", "cus_ab", "sub_ab"), row
    assert "abonne@recette.test" in destinataires(faux_brevo), destinataires(faux_brevo)


@pytest.mark.parametrize("cas", ["alteree", "autre_secret", "perimee", "essais_actuels", "absente"])
def test_une_signature_invalide_est_refusee_et_ne_change_rien(client, faux_stripe, faux_brevo, cas):
    j = panier(client, n=2)
    _, charge = evenement_stripe(session_payee(j["commande"]))
    sig = {"alteree": signer_stripe(charge, SECRET_WEBHOOK_RECETTE),
           "autre_secret": signer_stripe(charge, "whsec_autre"),
           "perimee": signer_stripe(charge, SECRET_WEBHOOK_RECETTE, t=time.time() - 301),
           "essais_actuels": "t=1,v1=x",
           "absente": False}[cas]
    if cas == "alteree":
        charge = charge.replace(b'"paid"', b'"PAID"')
    r, _ = poster(client, None, sig=sig, charge=charge)
    assert r.status_code == 400, (r.status_code, r.get_json())
    assert statuts(j["commande"]) == ["en_attente_paiement"], statuts(j["commande"])


def test_l_evenement_d_un_autre_site_du_compte_est_acquitte_sans_effet(client, faux_stripe, faux_brevo):
    """conseilprevcyber vend sur le MÊME compte : son checkout.session.completed
    (client_reference_id = une adresse, aucune métadonnée) arrive aussi ici."""
    j = panier(client, n=2)
    avant = len(faux_brevo.requetes)
    r, _ = poster(client, {"id": "cs_test_cyber", "object": "checkout.session",
                           "mode": "payment", "payment_status": "paid",
                           "client_reference_id": "acheteur@exemple.test",
                           "customer": "cus_cyber", "metadata": {}})
    assert r.status_code == 200, r.get_json()
    assert statuts(j["commande"]) == ["en_attente_paiement"]
    assert len(faux_brevo.requetes) == avant, "courriels partis : %d" % (len(faux_brevo.requetes) - avant)


def test_le_rejeu_d_un_evenement_deja_traite_ne_renvoie_aucun_courriel(client, faux_stripe, faux_brevo):
    j = panier(client, n=2)
    r1, evt = poster(client, session_payee(j["commande"]))
    assert r1.status_code == 200
    n = len(faux_brevo.requetes)
    r2, _ = poster(client, session_payee(j["commande"]), evt=evt)
    assert r2.get_json().get("duplicate") is True, r2.get_json()
    assert len(faux_brevo.requetes) == n, "%d courriel(s) de plus au rejeu" % (len(faux_brevo.requetes) - n)


def test_le_webhook_sans_secret_rend_501(client, faux_stripe, monkeypatch):
    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET")
    r, _ = poster(client, {"id": "in_x", "object": "invoice", "metadata": {}}, "invoice.paid")
    assert r.status_code == 501, r.status_code      # non 2xx : Stripe réessaie


def test_routage_invoice_paid_et_payment_failed(client, faux_stripe, faux_brevo):
    cid = creer_client("raas@recette.test", cust="cus_raas")
    facture_raas(cid, "F-RECETTE-1"); facture_raas(cid, "F-RECETTE-2")
    for num, t in (("F-RECETTE-1", "invoice.paid"), ("F-RECETTE-2", "invoice.payment_failed")):
        r, _ = poster(client, {"id": "in_x", "object": "invoice", "amount_paid": 120000,
                               "metadata": {"numero": num, "echeance": "1", "client_id": str(cid)}}, t)
        assert r.status_code == 200, (t, r.get_json())
    lu = {num: (facture_row(num)[0], facture_row(num)[1]["status"]) for num in ("F-RECETTE-1", "F-RECETTE-2")}
    assert lu == {"F-RECETTE-1": ("payee", "payee"), "F-RECETTE-2": ("emise", "echec")}, lu


def test_la_caisse_d_abonnement_recoit_le_contrat_attendu(client, faux_stripe, monkeypatch):
    monkeypatch.setenv("STRIPE_PRICE_PRO", "price_pro_recette")
    cid = creer_client("caisse@recette.test")
    connecter(client, cid)
    r = client.post("/api/sentinel/checkout", json={"plan": "pro"}, headers=NAVIGATEUR)
    assert r.status_code == 200 and r.get_json()["url"].startswith(faux_stripe.url), r.get_json()
    f = faux_stripe.recues("POST", "/v1/checkout/sessions")[0].form
    assert f["mode"] == "subscription" and f["line_items[0][price]"] == "price_pro_recette", f
    assert f["metadata[client_id]"] == str(cid) and f["metadata[plan]"] == "pro"
    assert f["customer_email"] == "caisse@recette.test"


def test_la_caisse_du_catalogue_et_son_webhook(client, faux_stripe, faux_brevo):
    cid = creer_client("catalogue@recette.test")
    connecter(client, cid)
    sid = session_catalogue_future()
    j = inscrire_catalogue(client, sid, participants=2)
    assert j["ok"] and j["paiement"] is True, j
    f = faux_stripe.recues("POST", "/v1/checkout/sessions")[0].form
    assert f["mode"] == "payment" and f["line_items[0][quantity]"] == "2", f
    assert f["line_items[0][tax_rates][0]"] == "txr_recette"
    ins = _q("SELECT id, statut FROM form_inscriptions WHERE email='catalogue@recette.test'")[0]
    assert f["metadata[inscription_id]"] == str(ins["id"])
    r, _ = poster(client, {"id": "cs_cat", "object": "checkout.session", "payment_status": "paid",
                           "metadata": {"type": "formation", "inscription_id": str(ins["id"])}})
    assert r.status_code == 200
    assert _q("SELECT statut FROM form_inscriptions WHERE id=?", (ins["id"],))[0]["statut"] == "payee"


def test_une_caisse_expiree_laisse_l_inscription_catalogue_en_attente(client, faux_stripe, faux_brevo):
    """Le catalogue est facturable hors ligne : CONSEILPREV rappelle. Seule la
    formation IA, dont le paiement retient la place, libère son créneau."""
    cid = creer_client("catalogue2@recette.test")
    connecter(client, cid)
    j = inscrire_catalogue(client, session_catalogue_future(), email="catalogue2@recette.test")
    r, _ = poster(client, {"id": "cs_cat2", "object": "checkout.session", "payment_status": "unpaid",
                           "status": "expired",
                           "metadata": {"type": "formation", "inscription_id": str(j["inscription_id"])}},
                  "checkout.session.expired")
    assert r.status_code == 200
    st = _q("SELECT statut FROM form_inscriptions WHERE id=?", (j["inscription_id"],))[0]["statut"]
    assert st == "en_attente_paiement", st


# ══════════════════════════════════════════════════════════════════════════
#  1a. UN ÉCHEC DE TRAITEMENT N'EST PAS ACQUITTÉ
# ══════════════════════════════════════════════════════════════════════════
def test_un_echec_de_traitement_n_est_pas_acquitte_et_le_reessai_confirme(
        client, faux_stripe, faux_brevo, monkeypatch, caplog):
    j = panier(client, n=2)
    vrai = A._formation_ia_confirmer_paiement

    def panne(**kw):
        raise RuntimeError("base momentanément injoignable")
    monkeypatch.setattr(A, "_formation_ia_confirmer_paiement", panne)
    with caplog.at_level(logging.ERROR, logger="conseilprev"):
        r1, evt = poster(client, session_payee(j["commande"]))
    marque = vu(evt)
    monkeypatch.setattr(A, "_formation_ia_confirmer_paiement", vrai)
    r2, _ = poster(client, session_payee(j["commande"]), evt=evt)     # le réessai de Stripe
    etat = {"1re_livraison": r1.status_code, "marque_vu_apres_echec": marque,
            "reessai": r2.get_json(), "statut_final": statuts(j["commande"])}
    assert r1.status_code >= 500 and not marque and statuts(j["commande"]) == ["payee"], etat
    journal = [m.getMessage() for m in caplog.records if "formation-ia" in m.getMessage() and evt in m.getMessage()]
    assert journal, "aucune ligne de journal ne nomme l'étape et l'événement : %s" % [m.getMessage() for m in caplog.records]


def test_une_base_muette_a_la_reclamation_rend_503_sans_rien_acquitter(client, faux_stripe, monkeypatch):
    """Stripe réessaie pendant trois jours sur un non-2xx. Une base injoignable
    doit donc répondre 503, jamais 200."""
    def muette():
        raise RuntimeError("base injoignable (simulée)")
    monkeypatch.setattr(A, "registre_get_db", muette)
    r, _ = poster(client, {"id": "in_x", "object": "invoice", "metadata": {}}, "invoice.paid")
    assert r.status_code == 503, "base injoignable : HTTP %s %s" % (r.status_code, r.get_json())


def test_deux_livraisons_simultanees_ne_traitent_qu_une_fois(client, faux_stripe, faux_brevo, monkeypatch):
    j = panier(client, n=2)
    vrai = A._formation_ia_confirmer_paiement
    appels = []

    def lent(**kw):
        appels.append(kw)
        time.sleep(0.4)
        return vrai(**kw)
    monkeypatch.setattr(A, "_formation_ia_confirmer_paiement", lent)
    _, charge = evenement_stripe(session_payee(j["commande"]))
    n0 = len(faux_brevo.requetes)
    fils = [threading.Thread(target=poster, args=(A.app.test_client(), None),
                             kwargs={"charge": charge}) for _ in range(2)]
    [f.start() for f in fils]; [f.join() for f in fils]
    assert len(appels) == 1, "%d traitements, %d courriels pour une seule notification" % (
        len(appels), len(faux_brevo.requetes) - n0)


# ══════════════════════════════════════════════════════════════════════════
#  1b. SEUL UN PAIEMENT ENCAISSÉ CONFIRME
# ══════════════════════════════════════════════════════════════════════════
def test_un_paiement_non_encaisse_ne_confirme_pas_la_formation_ia(client, faux_stripe, faux_brevo):
    """checkout.session.completed arrive avec payment_status='unpaid' pour les
    moyens différés (prélèvement SEPA…) : l'argent n'est pas là."""
    j = panier(client, n=2)
    r, _ = poster(client, session_payee(j["commande"], payment_status="unpaid"))
    assert r.status_code == 200
    assert statuts(j["commande"]) == ["en_attente_paiement"], statuts(j["commande"])


def test_un_paiement_non_encaisse_n_active_pas_l_offre(client, faux_stripe, faux_brevo):
    cid = creer_client("impaye@recette.test")
    poster(client, {"id": "cs_i", "object": "checkout.session", "payment_status": "unpaid",
                    "status": "complete", "client_reference_id": str(cid),
                    "metadata": {"client_id": str(cid), "plan": "entreprise"}})
    assert client_row(cid)["plan"] == "gratuit", "offre %r activée sur payment_status=unpaid" % client_row(cid)["plan"]


def test_un_paiement_non_encaisse_ne_confirme_pas_le_catalogue(client, faux_stripe, faux_brevo):
    cid = creer_client("catalogue3@recette.test")
    connecter(client, cid)
    j = inscrire_catalogue(client, session_catalogue_future(), email="catalogue3@recette.test")
    poster(client, {"id": "cs_c3", "object": "checkout.session", "payment_status": "unpaid",
                    "metadata": {"type": "formation", "inscription_id": str(j["inscription_id"])}})
    st = _q("SELECT statut FROM form_inscriptions WHERE id=?", (j["inscription_id"],))[0]["statut"]
    assert st == "en_attente_paiement", st


def test_le_paiement_differe_abouti_confirme(client, faux_stripe, faux_brevo):
    j = panier(client, n=2)
    r, _ = poster(client, session_payee(j["commande"]), "checkout.session.async_payment_succeeded")
    assert r.status_code == 200
    assert statuts(j["commande"]) == ["payee"], statuts(j["commande"])


@pytest.mark.parametrize("type_", ["checkout.session.expired", "checkout.session.async_payment_failed"])
def test_une_caisse_sans_paiement_libere_le_creneau(client, faux_stripe, faux_brevo, type_):
    """Le paiement retient la place. Une caisse expirée ou un prélèvement
    refusé, c'est un paiement qui n'a pas eu lieu : le créneau redevient
    libre pour un autre client, sans attendre la fin de la retenue."""
    cr = creneaux()
    jx = panier(client, n=2, dates=cr)
    offerte = _q("SELECT id, statut FROM formation_ia_resa WHERE commande=? AND gratuit=1",
                 (jx["commande"],))
    r, _ = poster(client, session_payee(jx["commande"], payment_status="unpaid", status="expired"), type_)
    assert r.status_code == 200, r.get_json()
    st = statuts(jx["commande"])
    assert st == ["annulee"], "la séance payante est %s après %s" % (st, type_)
    # LA SÉANCE OFFERTE DU MÊME PANIER N'EST PAS TOUCHÉE. Elle est confirmée
    # d'emblée et n'a rien coûté : la libération d'une caisse abandonnée ne
    # doit pas la faire perdre au client, c'est ce que la docstring promet.
    apres = _q("SELECT id, statut FROM formation_ia_resa WHERE commande=? AND gratuit=1",
               (jx["commande"],))
    assert apres == offerte, "la séance offerte est passée de %s à %s après %s" % (offerte, apres, type_)
    # Le créneau payant de X (cr[1]) est repris par Y : accepté, pas 409.
    ry = client.post("/api/formation/inscription", json={
        "seances": [{"sujet": F.SUJETS[2]["cle"], "creneau": cr[1]}],
        "nom": "Repreneur", "prenom": "Yann", "email": "repreneur@recette.test",
        "entreprise": "AUTRE SAS", "siret": "900000888",
        "telephone": "+33 6 98 76 54 32", "lieu": "1 rue du Test, 75000 Paris"})
    assert ry.status_code == 200, "le créneau libéré est refusé : HTTP %s %s" % (ry.status_code, ry.get_json())


# ══════════════════════════════════════════════════════════════════════════
#  1c. LE COMPTE VIENT DES MÉTADONNÉES, JAMAIS DE client_reference_id
# ══════════════════════════════════════════════════════════════════════════
def test_une_session_de_formation_ne_relie_pas_un_client_stripe_a_un_compte(client, faux_stripe, faux_brevo):
    """client_reference_id porte un N° D'INSCRIPTION pour une formation du
    catalogue, une COMMANDE pour la formation IA, un N° DE COMPTE pour Sentinel."""
    victime = creer_client("victime@recette.test", cust="cus_victime", sub="sub_victime")
    r, _ = poster(client, {"id": "cs_form", "object": "checkout.session", "mode": "payment",
                           "payment_status": "paid", "client_reference_id": str(victime),
                           "customer": "cus_acheteur_formation", "subscription": None,
                           "metadata": {"type": "formation", "inscription_id": "999999"}})
    assert r.status_code == 200
    row = client_row(victime)
    assert row["stripe_customer_id"] == "cus_victime", (
        "le compte Sentinel n°%d est désormais prélevé sur le client Stripe %r d'un acheteur de formation"
        % (victime, row["stripe_customer_id"]))


# ══════════════════════════════════════════════════════════════════════════
#  1d. UNE FACTURE À ZÉRO NE SOLDE RIEN
# ══════════════════════════════════════════════════════════════════════════
def test_une_facture_a_zero_ne_solde_pas_l_echeance(client, faux_stripe, faux_brevo):
    cid = creer_client("zero@recette.test", cust="cus_zero")
    facture_raas(cid, "F-RECETTE-0")
    poster(client, {"id": "in_zero", "object": "invoice", "amount_paid": 0, "total": 0,
                    "metadata": {"numero": "F-RECETTE-0", "echeance": "1", "client_id": str(cid)}},
           "invoice.paid")
    assert facture_row("F-RECETTE-0")[0] != "payee", "échéance de 1 000 EUR soldée par une facture de 0 EUR"


def test_un_ecart_entre_montant_paye_et_attendu_est_journalise(client, faux_stripe, faux_brevo, caplog):
    cid = creer_client("ecart@recette.test", cust="cus_ecart")
    facture_raas(cid, "F-RECETTE-E", montant=1000)
    with caplog.at_level(logging.WARNING, logger="conseilprev"):
        poster(client, {"id": "in_ecart", "object": "invoice", "amount_paid": 50000,
                        "metadata": {"numero": "F-RECETTE-E", "echeance": "1", "client_id": str(cid)}},
               "invoice.paid")
    lignes = [m.getMessage() for m in caplog.records if "F-RECETTE-E" in m.getMessage()]
    assert any("50000" in l and "100000" in l for l in lignes), (
        "50 000 c encaissés pour 100 000 c attendus, et le journal dit : %s" % lignes)


# ══════════════════════════════════════════════════════════════════════════
#  1e. LE CYCLE DE VIE DE L'ABONNEMENT
# ══════════════════════════════════════════════════════════════════════════
def test_un_abonnement_resilie_chez_stripe_repasse_le_client_en_gratuit(client, faux_stripe, faux_brevo):
    cid = creer_client("resilie@recette.test", plan="pro", sub="sub_resilie", cust="cus_resilie")
    r, _ = poster(client, {"id": "sub_resilie", "object": "subscription", "customer": "cus_resilie",
                           "status": "canceled", "metadata": {}}, "customer.subscription.deleted")
    row = client_row(cid)
    assert (row["plan"], row["stripe_subscription_id"]) == ("gratuit", None), (
        r.status_code, row["plan"], row["stripe_subscription_id"])


@pytest.mark.parametrize("forme", ["dahlia", "ancienne"])
def test_une_facture_d_abonnement_impayee_previent_le_client_et_conseilprev(
        client, faux_stripe, faux_brevo, forme):
    cid = creer_client("impaye2@recette.test", plan="pro", sub="sub_impaye", cust="cus_impaye")
    obj = {"id": "in_impaye", "object": "invoice", "customer": "cus_impaye",
           "billing_reason": "subscription_cycle", "metadata": {}}
    if forme == "dahlia":
        obj["parent"] = {"type": "subscription_details",
                         "subscription_details": {"subscription": "sub_impaye", "metadata": {}}}
    else:
        obj["subscription"] = "sub_impaye"
    r, _ = poster(client, obj, "invoice.payment_failed")
    dest = destinataires(faux_brevo)
    assert r.status_code == 200
    assert "impaye2@recette.test" in dest and A.CONSEILPREV_NOTIFY_EMAIL in dest, (
        "impayé d'abonnement : courriels partis vers %s" % dest)
    # LA RELANCE EST EN BASE, PAS SEULEMENT DANS LES COURRIELS. C'est elle que
    # CONSEILPREV voit dans la gestion des clients, et le courriel interne
    # l'annonce (« une relance est planifiée »). Sans cette mesure, l'écriture
    # pouvait être annulée sans que rien ne tombe : la promesse restait dans le
    # texte du message, et nulle part ailleurs.
    rel = _q("SELECT type, status, related_ref FROM client_relances WHERE client_id=?", (cid,))
    assert rel == [{"type": "paiement", "status": "planifiee", "related_ref": "sub_impaye"}], (
        "relance écrite en base : %s" % rel)


# ══════════════════════════════════════════════════════════════════════════
#  1f. LES ÉVÉNEMENTS QUE LE SITE TRAITE SONT DÉCLARÉS (pour le diagnostic)
# ══════════════════════════════════════════════════════════════════════════
def test_les_evenements_requis_sont_declares_pour_le_diagnostic():
    requis = getattr(A, "STRIPE_EVENEMENTS_REQUIS", None)
    assert isinstance(requis, tuple), "STRIPE_EVENEMENTS_REQUIS : %r" % (requis,)
    attendus = {"checkout.session.completed", "checkout.session.async_payment_succeeded",
                "checkout.session.async_payment_failed", "checkout.session.expired",
                "invoice.paid", "invoice.payment_failed", "customer.subscription.deleted"}
    assert attendus <= set(requis), "manquent : %s" % sorted(attendus - set(requis))


# ══════════════════════════════════════════════════════════════════════════
#  2. LA CAISSE D'ABONNEMENT
# ══════════════════════════════════════════════════════════════════════════
def test_la_caisse_d_abonnement_pose_les_metadonnees_sur_l_abonnement(client, faux_stripe, monkeypatch):
    """Les événements customer.subscription.* et invoice.* portent les
    métadonnées de l'ABONNEMENT, pas celles de la session de caisse."""
    monkeypatch.setenv("STRIPE_PRICE_PRO", "price_pro_recette")
    cid = creer_client("meta@recette.test")
    connecter(client, cid)
    client.post("/api/sentinel/checkout", json={"plan": "pro"}, headers=NAVIGATEUR)
    f = faux_stripe.recues("POST", "/v1/checkout/sessions")[0].form
    attendu = {"subscription_data[metadata][client_id]": str(cid),
               "subscription_data[metadata][plan]": "pro",
               "subscription_data[metadata][site]": "conseilprev"}
    assert {k: f.get(k) for k in attendu} == attendu, sorted(f)


def test_un_client_deja_abonne_change_de_prix_au_lieu_d_ouvrir_une_seconde_caisse(
        client, faux_stripe, monkeypatch):
    monkeypatch.setenv("STRIPE_PRICE_ENTREPRISE", "price_ent_recette")
    cid = creer_client("montee@recette.test", plan="pro", sub="sub_montee", cust="cus_montee")
    connecter(client, cid)
    r = client.post("/api/sentinel/checkout", json={"plan": "entreprise"}, headers=NAVIGATEUR)
    j = r.get_json()
    caisses = len(faux_stripe.recues("POST", "/v1/checkout/sessions"))
    modifs = [x.form for x in faux_stripe.recues("POST", "/v1/subscriptions/sub_montee")]
    etat = {"http": r.status_code, "reponse": j, "caisses_ouvertes": caisses, "modifications": modifs}
    assert r.status_code == 200 and j.get("ok") is True and j.get("modifie") is True, etat
    assert caisses == 0 and len(modifs) == 1, etat
    assert modifs[0].get("items[0][price]") == "price_ent_recette", modifs[0]
    assert modifs[0].get("items[0][id]") == "si_sub_montee", modifs[0]
    assert modifs[0].get("proration_behavior") == "create_prorations", modifs[0]
    assert client_row(cid)["plan"] == "entreprise", client_row(cid)["plan"]


def test_les_trois_caisses_reviennent_avec_l_identifiant_de_session(client, faux_stripe, faux_brevo, monkeypatch):
    """Sans {CHECKOUT_SESSION_ID} dans success_url, la page de retour n'a
    aucun moyen de relire la session : c'est le filet quand la notification
    n'arrive pas (un mois sans webhook vient d'être constaté)."""
    monkeypatch.setenv("STRIPE_PRICE_PRO", "price_pro_recette")
    cid = creer_client("retour@recette.test")
    connecter(client, cid)
    client.post("/api/sentinel/checkout", json={"plan": "pro"}, headers=NAVIGATEUR)
    inscrire_catalogue(client, session_catalogue_future(), email="retour@recette.test")
    panier(A.app.test_client(), n=2)
    urls = [x.form["success_url"] for x in faux_stripe.recues("POST", "/v1/checkout/sessions")]
    assert len(urls) == 3 and all("session_id={CHECKOUT_SESSION_ID}" in u for u in urls), urls


def test_la_page_recharge_quand_l_abonnement_est_modifie():
    """EXÉCUTÉ : `sentinelCheckout` avec une réponse {ok, modifie} recharge la
    page au lieu de partir vers /tarifications."""
    src = io.open(os.path.join(_RACINE, "sentinel.page.js"), encoding="utf-8").read()
    code = _tranche(src, "window.sentinelCheckout = function(plan){", "\n};")
    o = _node("""
      const etat = { recharges: 0, href: '/sentinel' };
      global.window = global;
      global.location = { get href(){ return etat.href; }, set href(v){ etat.href = v; },
                          reload: () => { etat.recharges++; } };
      global.document = { createElement: () => ({ style: {}, innerHTML: '', parentNode: null }),
                          body: { appendChild: () => {} } };
      global.fetch = () => Promise.resolve({ json: () => Promise.resolve({ ok: true, modifie: true }) });
    """ + code + """
      window.sentinelCheckout('entreprise');
      setTimeout(() => process.stdout.write(JSON.stringify(etat)), 30);
    """)
    assert o["recharges"] == 1 and o["href"] == "/sentinel", "après « modifié » : %s" % o


# ══════════════════════════════════════════════════════════════════════════
#  3. LE RETOUR DE CAISSE — le filet quand la notification n'arrive pas
# ══════════════════════════════════════════════════════════════════════════
def test_le_retour_de_caisse_confirme_une_formation_ia_encaissee(client, faux_stripe, faux_brevo):
    j = panier(client, n=2)
    sid = _q("SELECT stripe_session_id FROM formation_ia_resa WHERE commande=? AND gratuit=0",
             (j["commande"],))[0]["stripe_session_id"]
    faux_stripe.payer(sid, amount_total=96000)
    r = client.get("/api/stripe/retour?session_id=" + sid, headers=NAVIGATEUR)
    assert r.status_code == 200 and r.get_json() == {"statut": "paye"}, (r.status_code, r.get_json())
    assert statuts(j["commande"]) == ["payee"], statuts(j["commande"])
    assert "Réservation confirmée — 1 séance(s)" in sujets(faux_brevo), sujets(faux_brevo)


def test_le_retour_de_caisse_active_une_offre_encaissee_une_seule_fois(client, faux_stripe, faux_brevo, monkeypatch):
    """Le retour confirme ; la notification qui suit ne réactive ni ne
    renvoie le courriel d'activation : les confirmateurs sont idempotents."""
    monkeypatch.setenv("STRIPE_PRICE_PRO", "price_pro_recette")
    cid = creer_client("retour2@recette.test")
    connecter(client, cid)
    client.post("/api/sentinel/checkout", json={"plan": "pro"}, headers=NAVIGATEUR)
    sid = list(faux_stripe.sessions)[0]
    faux_stripe.payer(sid, customer="cus_r2", subscription="sub_r2")
    r = A.app.test_client().get("/api/stripe/retour?session_id=" + sid, headers=NAVIGATEUR)
    assert r.get_json() == {"statut": "paye"}, (r.status_code, r.get_json())
    row = client_row(cid)
    assert (row["plan"], row["stripe_customer_id"], row["stripe_subscription_id"]) == ("pro", "cus_r2", "sub_r2"), row
    n = len(faux_brevo.requetes)
    poster(client, dict(faux_stripe.sessions[sid]))
    assert len(faux_brevo.requetes) == n, "%d courriel(s) de plus à la notification" % (len(faux_brevo.requetes) - n)


def test_le_retour_de_caisse_confirme_une_inscription_catalogue_encaissee(client, faux_stripe, faux_brevo):
    cid = creer_client("retour3@recette.test")
    connecter(client, cid)
    j = inscrire_catalogue(client, session_catalogue_future(), email="retour3@recette.test")
    sid = list(faux_stripe.sessions)[0]
    faux_stripe.payer(sid)
    r = client.get("/api/stripe/retour?session_id=" + sid, headers=NAVIGATEUR)
    assert r.get_json() == {"statut": "paye"}, (r.status_code, r.get_json())
    st = _q("SELECT statut FROM form_inscriptions WHERE id=?", (j["inscription_id"],))[0]["statut"]
    assert st == "payee", st


def test_le_retour_de_caisse_ne_confirme_pas_une_session_non_payee(client, faux_stripe, faux_brevo):
    j = panier(client, n=2)
    sid = list(faux_stripe.sessions)[0]
    r = client.get("/api/stripe/retour?session_id=" + sid, headers=NAVIGATEUR)
    assert r.get_json() == {"statut": "en_attente"}, (r.status_code, r.get_json())
    assert statuts(j["commande"]) == ["en_attente_paiement"], statuts(j["commande"])


def test_le_retour_de_caisse_d_une_session_inconnue_ne_dit_rien_d_autre(client, faux_stripe):
    faux_stripe.route("GET", "/v1/checkout/sessions/cs_inconnue",
                      lambda r: (404, {"error": {"type": "invalid_request_error", "code": "resource_missing",
                                                 "message": "No such checkout.session"}}))
    r = client.get("/api/stripe/retour?session_id=cs_inconnue", headers=NAVIGATEUR)
    assert r.get_json() == {"statut": "inconnu"}, (r.status_code, r.get_json())
    r2 = client.get("/api/stripe/retour", headers=NAVIGATEUR)
    assert r2.status_code == 400 and set(r2.get_json()) == {"statut"}, (r2.status_code, r2.get_json())


def test_le_retour_de_caisse_est_limite_en_debit(client, faux_stripe):
    codes = [client.get("/api/stripe/retour?session_id=cs_x%d" % i, headers=NAVIGATEUR).status_code
             for i in range(40)]
    assert 429 in codes and codes[0] == 200, "40 appels d'une même adresse : %s" % sorted(set(codes))


@pytest.mark.parametrize("statut,attendu,proscrit", [
    pytest.param("paye", "Paiement reçu", "en cours de confirmation", id="paye"),
    pytest.param("en_attente", "en cours de confirmation", "Paiement reçu", id="en_attente"),
])
def test_la_page_formation_n_annonce_le_paiement_recu_qu_apres_confirmation(statut, attendu, proscrit):
    """EXÉCUTÉ : le bandeau de retour de formation.html demande au serveur
    avant d'annoncer quoi que ce soit."""
    src = io.open(os.path.join(_RACINE, "formation.html"), encoding="utf-8").read()
    code = _tranche(src, "(function retourPaiement(){", "\n  })();")
    o = _node("""
      const el = { hidden: true, className: '', innerHTML: '', textContent: '' };
      const appels = [];
      global.window = global;
      global.location = { search: '?paiement=ok&session_id=cs_test_page' };
      global.document = { getElementById: (id) => id === 'retour-paiement' ? el : null };
      global.fetch = (u) => { appels.push(String(u));
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ statut: '%s' }) }); };
    """ % statut + code + """
      setTimeout(() => process.stdout.write(JSON.stringify({ el, appels })), 30);
    """)
    texte = o["el"]["innerHTML"] + o["el"]["textContent"]
    assert any("/api/stripe/retour" in a and "cs_test_page" in a for a in o["appels"]), (
        "la page n'a rien demandé au serveur ; appels : %s ; bandeau : %r" % (o["appels"], texte))
    assert attendu in texte and proscrit not in texte and not o["el"]["hidden"], (
        "serveur : %s ; page : %r" % (statut, texte))


@pytest.mark.parametrize("statut,attendu,proscrit", [
    pytest.param("paye", "activée", "en cours de confirmation", id="paye"),
    pytest.param("en_attente", "en cours de confirmation", "activée", id="en_attente"),
])
def test_la_page_sentinel_n_annonce_l_offre_activee_qu_apres_confirmation(statut, attendu, proscrit):
    src = io.open(os.path.join(_RACINE, "sentinel.page.js"), encoding="utf-8").read()
    code = _tranche(src, "window.sentinelActivationToast = function(){", "\n};")
    o = _node("""
      const poses = [], appels = [];
      global.window = global;
      global.location = { search: '?activation=ok&session_id=cs_test_page' };
      global.document = { createElement: () => ({ style: {}, textContent: '', innerHTML: '', parentNode: null }),
                          body: { appendChild: (t) => { poses.push(t); t.parentNode = global.document.body; },
                                  removeChild: () => {} } };
      global.fetch = (u) => { appels.push(String(u));
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ statut: '%s' }) }); };
      global.setTimeout = (f, ms) => (ms >= 1000 ? 0 : require('timers').setTimeout(f, ms));
    """ % statut + code + """
      window.sentinelActivationToast();
      require('timers').setTimeout(() => process.stdout.write(JSON.stringify({
        textes: poses.map(t => t.textContent + t.innerHTML), appels })), 30);
    """)
    texte = " ".join(o["textes"])
    assert any("/api/stripe/retour" in a and "cs_test_page" in a for a in o["appels"]), (
        "la page n'a rien demandé au serveur ; appels : %s ; message : %r" % (o["appels"], texte))
    assert attendu in texte and proscrit not in texte, "serveur : %s ; page : %r" % (statut, texte)


# ══════════════════════════════════════════════════════════════════════════
#  4. FORMATION IA : caisse bornée, montant réel, accusé au client
# ══════════════════════════════════════════════════════════════════════════
def test_la_caisse_ferme_quand_la_retenue_du_creneau_expire(client, faux_stripe, faux_brevo):
    """La place n'est tenue que RETENUE_MINUTES ; une caisse Stripe vit 24 h
    par défaut. Payer à H+2 règle une place peut-être déjà reprise.

    LA RETENUE COURT DEPUIS L'ÉCRITURE DE LA LIGNE, pas depuis l'ouverture de
    la caisse : entre les deux, deux courriels synchrones et la lecture du taux
    de TVA. Avec un Brevo lent, la caisse survivait à la retenue d'autant — X
    pouvait encore payer un créneau déjà rendu à Y. Brevo est donc ralenti ici,
    sans quoi la mesure ne verrait rien."""
    faux_brevo.lenteurs["POST /v3/smtp/email"] = 1.5
    avant = time.time()
    j = panier(client, n=2)
    f = faux_stripe.recues("POST", "/v1/checkout/sessions")[0].form
    assert "expires_at" in f, "aucun expires_at : la caisse reste ouverte 24 h"
    borne = max(30, F.RETENUE_MINUTES) * 60
    cree = _q("SELECT created_at FROM formation_ia_resa WHERE commande=? AND gratuit=0",
              (j["commande"],))[0]["created_at"]
    cree = (datetime.datetime.fromisoformat(cree)
            - datetime.datetime(1970, 1, 1)).total_seconds()
    fin_retenue = cree + F.RETENUE_MINUTES * 60
    # Stripe refuse une caisse qui fermerait à moins de 30 minutes : c'est ce
    # plancher, et non la retenue, qui s'applique si la retenue est plus courte.
    assert avant + borne - 5 <= int(f["expires_at"]) <= max(fin_retenue, avant + 31 * 60 + 5), (
        "la caisse ferme %d s après la fin de la retenue du créneau"
        % (int(f["expires_at"]) - fin_retenue))


def test_le_montant_encaisse_est_celui_de_l_evenement(client, faux_stripe, faux_brevo):
    j = panier(client, n=2)
    # Taux réel porté par STRIPE_TAX_RATE_ID = 5,5 % : Stripe encaisse 84 400 c.
    poster(client, session_payee(j["commande"], amount_total=84400))
    r = _q("SELECT paye_ttc_cents FROM formation_ia_resa WHERE commande=? AND gratuit=0", (j["commande"],))[0]
    assert r["paye_ttc_cents"] == 84400, (
        "paye_ttc_cents recalculé (%s) au lieu du montant encaissé (84400) : base du remboursement fausse"
        % r["paye_ttc_cents"])


def test_le_montant_encaisse_se_repartit_sur_les_seances_payantes(client, faux_stripe, faux_brevo):
    j = panier(client, n=3)
    poster(client, session_payee(j["commande"], amount_total=168801))
    lus = [x["paye_ttc_cents"] for x in _q(
        "SELECT paye_ttc_cents FROM formation_ia_resa WHERE commande=? AND gratuit=0 ORDER BY id", (j["commande"],))]
    assert sum(lus) == 168801 and max(lus) - min(lus) <= 1, lus


def test_un_evenement_sans_montant_retombe_sur_le_recalcul(client, faux_stripe, faux_brevo):
    j = panier(client, n=2)
    poster(client, session_payee(j["commande"], amount_total=None))
    r = _q("SELECT paye_ttc_cents FROM formation_ia_resa WHERE commande=? AND gratuit=0", (j["commande"],))[0]
    assert r["paye_ttc_cents"] == F._ttc(F.TARIF_HT_CENTS), r


@pytest.mark.parametrize("n", [1, 2])
def test_le_client_recoit_l_accuse_de_reservation(client, faux_stripe, faux_brevo, n):
    """n=1 : séance offerte seule ; n=2 : une offerte + une payante. L'accusé
    porte les liens d'annulation : c'est le seul courriel du parcours gratuit."""
    panier(client, n=n, email="accuse%d@recette.test" % n)
    a = destinataires(faux_brevo)
    assert "accuse%d@recette.test" % n in a, "courriels partis : %s" % a


def test_un_accuse_qui_echoue_est_journalise(client, faux_stripe, faux_brevo, monkeypatch, caplog):
    def casse(*a, **k):
        raise RuntimeError("relais indisponible (simulé)")
    monkeypatch.setattr(A, "send_email_smart", casse)
    with caplog.at_level(logging.ERROR, logger="conseilprev"):
        panier(client, n=2, email="journal@recette.test")
    lignes = [m.getMessage() for m in caplog.records if "journal@recette.test" in m.getMessage()]
    assert lignes, "l'accusé n'est pas parti et rien ne le dit : %s" % [m.getMessage() for m in caplog.records]


# ══════════════════════════════════════════════════════════════════════════
#  5. CATALOGUE : identifiant sûr, sessions passées ou complètes refusées
# ══════════════════════════════════════════════════════════════════════════
def test_l_identifiant_d_inscription_est_celui_de_la_ligne_ecrite(client, faux_stripe, faux_brevo, monkeypatch):
    """Entrelacement forcé : une autre inscription est écrite ENTRE notre
    COMMIT et la relecture. MAX(id) rendrait la sienne."""
    cid = creer_client("concurrence@recette.test")
    connecter(client, cid)
    sid = session_catalogue_future()
    vrai = A.registre_get_db

    def concurrent():
        k = vrai(); cu = k.cursor()
        cu.execute("INSERT INTO form_inscriptions (session_id, client_id, nom, prenom, email, participants, "
                   "montant_cents, statut, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                   (sid, 0, "Autre", "Personne", "autre@recette.test", 1, 95000,
                    "en_attente_paiement", datetime.datetime.utcnow().isoformat()))
        k.commit(); k.close()

    class Cur(object):
        def __init__(s, cur, p): s._c, s._p = cur, p
        def execute(s, sql, *a):
            if isinstance(sql, str) and sql.lstrip().upper().startswith("INSERT INTO FORM_INSCRIPTIONS"):
                s._p.vu = True
            return s._c.execute(sql, *a)
        def __getattr__(s, k): return getattr(s._c, k)

    class Conn(object):
        def __init__(s, conn): s._c, s.vu = conn, False
        def cursor(s): return Cur(s._c.cursor(), s)
        def commit(s):
            r = s._c.commit()
            if s.vu:
                s.vu = False; concurrent()
            return r
        def __getattr__(s, k): return getattr(s._c, k)

    monkeypatch.setattr(A, "registre_get_db", lambda: Conn(vrai()))
    j = inscrire_catalogue(client, sid, email="concurrence@recette.test")
    monkeypatch.setattr(A, "registre_get_db", vrai)
    meta = faux_stripe.recues("POST", "/v1/checkout/sessions")[0].form["metadata[inscription_id]"]
    mien = _q("SELECT id FROM form_inscriptions WHERE email='concurrence@recette.test'")[0]["id"]
    assert meta == str(mien) == str(j.get("inscription_id")), (
        "la caisse porte l'inscription %s, la réponse %s, la mienne est %s" % (meta, j.get("inscription_id"), mien))


def test_une_session_passee_est_refusee(client, faux_stripe, faux_brevo):
    cid = creer_client("passe@recette.test")
    connecter(client, cid)
    _exec("INSERT INTO form_sessions (formation_id, date_session, date_fin, lieu, prix_cents, places, actif) "
          "VALUES (?,?,?,?,?,?,1)", (15, "2026-09-07", "2026-09-07", "RECETTE passee", 95000, 12))
    sid = _q("SELECT id FROM form_sessions WHERE lieu='RECETTE passee'")[0]["id"]
    r = client.post("/api/formations/inscription", json={"session_id": sid, "participants": 1,
                    "nom": "N", "prenom": "P", "email": "passe@recette.test"}, headers=NAVIGATEUR)
    assert r.status_code == 400 and not r.get_json().get("paiement"), (
        "session du 2026-09-07 encaissable le %s : HTTP %s %s" % (AUJOURD_HUI, r.status_code, r.get_json()))
    assert "pass" in (r.get_json().get("error") or "").lower(), r.get_json()
    assert not faux_stripe.recues("POST", "/v1/checkout/sessions"), "une caisse a été ouverte"


def test_une_session_complete_est_refusee(client, faux_stripe, faux_brevo):
    """LA DATE EST CALCULÉE, JAMAIS ÉCRITE EN DUR. Le refus « session passée »
    est testé AVANT le refus « session complète » : une date fixe finit par
    passer, et la règle tombe alors sur du code juste en annonçant un défaut
    qui n'existe pas. Mesuré : la même règle datée d'hier échoue en disant
    « cette session est passee », sans un mot sur le remplissage."""
    cid = creer_client("complet@recette.test")
    connecter(client, cid)
    futur = (datetime.datetime.utcnow().date() + datetime.timedelta(days=60)).isoformat()
    _exec("INSERT INTO form_sessions (formation_id, date_session, date_fin, lieu, prix_cents, places, actif) "
          "VALUES (?,?,?,?,?,?,1)", (15, futur, futur, "RECETTE complete", 95000, 2))
    sid = _q("SELECT id FROM form_sessions WHERE lieu='RECETTE complete'")[0]["id"]
    _exec("INSERT INTO form_inscriptions (session_id, client_id, nom, prenom, email, participants, "
          "montant_cents, statut, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
          (sid, 0, "Deja", "Inscrit", "deja@recette.test", 2, 190000, "payee", "2026-09-01"))
    r = client.post("/api/formations/inscription", json={"session_id": sid, "participants": 1,
                    "nom": "N", "prenom": "P", "email": "complet@recette.test"}, headers=NAVIGATEUR)
    assert r.status_code == 400 and not r.get_json().get("paiement"), (
        "session complète (2 places, 2 payées), caisse ouverte quand même : HTTP %s %s" % (r.status_code, r.get_json()))
    assert "compl" in (r.get_json().get("error") or "").lower(), r.get_json()


# ══════════════════════════════════════════════════════════════════════════
#  6. FACTURATION RAAS ET ABONNEMENTS (administration)
# ══════════════════════════════════════════════════════════════════════════
def _facturer(c, cid):
    admin(c)
    return c.post("/api/clients/billing-run", json={"mode": "execute", "confirm": True, "client_id": cid},
                  headers=NAVIGATEUR).get_json()


def test_la_facture_raas_contient_sa_ligne_et_l_echeance_est_notee(client, faux_stripe):
    """Avant : ligne créée SANS facture, facture créée sans la ligne (défaut
    Stripe : exclude), puis `inv.get('id')` levait AttributeError."""
    cid = creer_client("raas2@recette.test", cust="cus_raas2")
    facture_raas(cid, "F-RECETTE-R", montant=1000, statut_echeance="a_venir")
    j = _facturer(client, cid)
    lignes = faux_stripe.recues("POST", "/v1/invoiceitems")
    factures = faux_stripe.recues("POST", "/v1/invoices", exact=True)
    finalisees = [x for x in faux_stripe.recues("POST", "/v1/invoices/") if x.chemin.endswith("/finalize")]
    etat = {"reponse": j.get("processed"), "lignes": [x.form for x in lignes],
            "factures": [x.form for x in factures], "finalisations": len(finalisees),
            "echeance": facture_row("F-RECETTE-R")[1]}
    assert j["processed"][0]["ok"] is True, etat
    assert len(factures) == 1 and factures[0].form.get("pending_invoice_items_behavior") == "exclude", etat
    assert len(lignes) == 1 and lignes[0].form.get("invoice", "").startswith("in_test_"), etat
    assert len(finalisees) == 1, etat
    assert facture_row("F-RECETTE-R")[1]["status"] == "envoyee", etat
    assert factures[0].entetes["idempotency-key"] == "raas-F-RECETTE-R-e1-inv2", factures[0].entetes["idempotency-key"]
    assert lignes[0].entetes["idempotency-key"] == "raas-F-RECETTE-R-e1-item2", lignes[0].entetes["idempotency-key"]


def test_une_echeance_n_est_notee_envoyee_qu_apres_finalisation(client, faux_stripe):
    cid = creer_client("raas3@recette.test", cust="cus_raas3")
    facture_raas(cid, "F-RECETTE-F", montant=1000, statut_echeance="a_venir")
    faux_stripe.route("POST", "/v1/invoices/", lambda r: (500, {"error": {"type": "api_error", "message": "panne"}})
                      if r.chemin.endswith("/finalize") else (200, {"id": "in_x", "object": "invoice"}),
                      prefixe=True)
    j = _facturer(client, cid)
    st = facture_row("F-RECETTE-F")[1]["status"]
    assert not j["processed"][0]["ok"] and st == "a_venir", (j["processed"], st)


def test_une_resiliation_refusee_par_stripe_garde_le_lien_local(base, faux_stripe):
    cid = creer_client("lie@recette.test", plan="pro", sub="sub_lie", cust="cus_lie")
    faux_stripe.pannes["DELETE /v1/subscriptions/sub_lie"] = (
        500, {"error": {"type": "api_error", "message": "panne simulée"}})
    ok = A._billing_cancel_subscription(cid)
    essais = len(faux_stripe.recues("DELETE", "/v1/subscriptions/sub_lie"))
    assert ok is False and client_row(cid)["stripe_subscription_id"] == "sub_lie", (
        "%d résiliation(s) refusée(s) par Stripe, résultat %r, lien local %r : l'abonnement continue "
        "d'être prélevé sans que le site le sache" % (essais, ok, client_row(cid)["stripe_subscription_id"]))


def test_un_abonnement_deja_disparu_chez_stripe_est_oublie(base, faux_stripe):
    cid = creer_client("disparu@recette.test", plan="pro", sub="sub_disparu")
    faux_stripe.pannes["DELETE /v1/subscriptions/sub_disparu"] = (
        404, {"error": {"type": "invalid_request_error", "code": "resource_missing",
                        "message": "No such subscription"}})
    assert A._billing_cancel_subscription(cid) is True
    assert client_row(cid)["stripe_subscription_id"] is None


def test_le_billing_run_n_emet_pas_de_facture_si_la_resiliation_echoue(client, faux_stripe):
    """Le cumul abonnement + facturation par résultats est ce que la
    docstring interdit : une résiliation refusée bloque l'échéance."""
    cid = creer_client("cumul@recette.test", plan="pro", sub="sub_cumul", cust="cus_cumul")
    facture_raas(cid, "F-RECETTE-C", montant=1000, statut_echeance="a_venir")
    faux_stripe.pannes["DELETE /v1/subscriptions/sub_cumul"] = (
        500, {"error": {"type": "api_error", "message": "panne simulée"}})
    j = _facturer(client, cid)
    assert not j["processed"][0]["ok"], j["processed"]
    assert not faux_stripe.recues("POST", "/v1/invoices", exact=True), "une facture est partie malgré l'abonnement actif"
    assert client_row(cid)["stripe_subscription_id"] == "sub_cumul"


def test_changer_d_offre_met_a_jour_l_abonnement_stripe(client, faux_stripe, monkeypatch):
    monkeypatch.setenv("STRIPE_PRICE_ENTREPRISE", "price_ent_recette")
    cid = creer_client("offre@recette.test", plan="pro", sub="sub_offre")
    admin(client)
    j = client.post("/api/clients/set-plan", json={"client_id": cid, "plan": "entreprise"},
                    headers=NAVIGATEUR).get_json()
    modifs = [x.form for x in faux_stripe.recues("POST", "/v1/subscriptions/sub_offre")]
    assert j["stripe_sync"] == "tarif_mis_a_jour" and modifs, (j, modifs)
    assert modifs[0].get("items[0][id]") == "si_sub_offre" and modifs[0].get("items[0][price]") == "price_ent_recette", modifs


def test_passer_en_gratuit_n_annonce_pas_une_resiliation_refusee(client, faux_stripe):
    cid = creer_client("gratuit@recette.test", plan="pro", sub="sub_gratuit")
    faux_stripe.pannes["DELETE /v1/subscriptions/sub_gratuit"] = (
        500, {"error": {"type": "api_error", "message": "panne simulée"}})
    admin(client)
    r = client.post("/api/clients/set-plan", json={"client_id": cid, "plan": "gratuit"}, headers=NAVIGATEUR)
    j = r.get_json(); row = client_row(cid)
    assert j.get("stripe_sync") != "abonnement_resilie" and not j.get("ok", True) is True, (r.status_code, j)
    assert row["stripe_subscription_id"] == "sub_gratuit" and row["plan"] == "pro", row


def test_passer_en_gratuit_resilie_puis_oublie_l_abonnement(client, faux_stripe):
    cid = creer_client("gratuit2@recette.test", plan="pro", sub="sub_gratuit2")
    admin(client)
    j = client.post("/api/clients/set-plan", json={"client_id": cid, "plan": "gratuit"}, headers=NAVIGATEUR).get_json()
    row = client_row(cid)
    assert j["ok"] and j["stripe_sync"] == "abonnement_resilie", j
    assert (row["plan"], row["stripe_subscription_id"]) == ("gratuit", None), row


def test_le_detail_d_abonnement_lit_la_fin_de_periode_sur_l_article(client, faux_stripe):
    cid = creer_client("detail@recette.test", plan="pro", sub="sub_detail")
    admin(client)
    j = client.get("/api/clients/subscription?client_id=%d&live=1" % cid, headers=NAVIGATEUR).get_json()
    attendu = faux_stripe.abonnements["sub_detail"]["items"]["data"][0]["current_period_end"]
    assert j.get("has_sub") is True and j.get("current_period_end") == attendu, j


def _abonnements_par_email(faux, prix):
    faux.route("GET", "/v1/customers", lambda r: (200, {
        "object": "list", "url": "/v1/customers", "has_more": False,
        "data": [{"id": "cus_meme_email", "object": "customer"}]}))
    faux.route("GET", "/v1/subscriptions", lambda r: (200, {
        "object": "list", "url": "/v1/subscriptions", "has_more": False,
        "data": [{"id": "sub_trouve", "object": "subscription", "status": "active", "metadata": {},
                  "items": {"object": "list", "data": [
                      {"id": "si_x", "object": "subscription_item",
                       "price": {"id": prix, "object": "price", "unit_amount": 1500,
                                 "currency": "eur", "recurring": {"interval": "month"}}}]}}]}))


def test_le_rattachement_par_email_ignore_un_abonnement_d_un_autre_produit(client, faux_stripe, monkeypatch):
    """Le compte Stripe est PARTAGÉ : un abonnement d'un autre site porte le
    même e-mail. Rattaché ici, un set-plan « gratuit » le RÉSILIERAIT."""
    monkeypatch.setenv("STRIPE_PRICE_PRO", "price_pro_recette")
    _abonnements_par_email(faux_stripe, "price_autre_produit")
    cid = creer_client("partage@recette.test", plan="pro")
    admin(client)
    j = client.get("/api/clients/subscription?client_id=%d&live=1" % cid, headers=NAVIGATEUR).get_json()
    row = client_row(cid)
    assert row["stripe_subscription_id"] is None and j.get("has_sub") is False, (
        "abonnement %r (prix price_autre_produit) rattaché au client ; réponse %s" % (row["stripe_subscription_id"], j))


def test_le_rattachement_par_email_retient_un_abonnement_du_site(client, faux_stripe, monkeypatch):
    monkeypatch.setenv("STRIPE_PRICE_PRO", "price_pro_recette")
    _abonnements_par_email(faux_stripe, "price_pro_recette")
    cid = creer_client("partage2@recette.test", plan="pro")
    admin(client)
    j = client.get("/api/clients/subscription?client_id=%d&live=1" % cid, headers=NAVIGATEUR).get_json()
    row = client_row(cid)
    assert j.get("has_sub") is True and (row["stripe_subscription_id"], row["stripe_customer_id"]) == ("sub_trouve", "cus_meme_email"), (j, row)


# ══════════════════════════════════════════════════════════════════════════
#  7. EFFACEMENT RGPD : résilier avant d'oublier
# ══════════════════════════════════════════════════════════════════════════
def test_l_effacement_rgpd_resilie_l_abonnement_avant_de_l_oublier(client, faux_stripe):
    cid = creer_client("rgpd@recette.test", plan="pro", sub="sub_rgpd", cust="cus_rgpd")
    for t in ("client_entites", "client_connecteurs", "client_formations"):
        _exec("CREATE TABLE IF NOT EXISTS %s (id INTEGER PRIMARY KEY, client_id INTEGER)" % t)
    admin(client)
    j = client.post("/api/rgpd/effacement", json={"email": "rgpd@recette.test"}, headers=NAVIGATEUR).get_json()
    row = client_row(cid)
    assert row["email"] != "rgpd@recette.test", "l'anonymisation n'a pas eu lieu : %s" % j
    resil = faux_stripe.recues("DELETE", "/v1/subscriptions/sub_rgpd")
    assert len(resil) == 1 and row["stripe_subscription_id"] is None, (
        "identifiant d'abonnement effacé (%r) avec %d résiliation(s) chez Stripe : le compte effacé "
        "continuerait d'être prélevé, et plus rien ne permettrait de l'arrêter" % (row["stripe_subscription_id"], len(resil)))


# ══════════════════════════════════════════════════════════════════════════
#  8. UNE TVA DÉCIMALE NE BLOQUE PLUS LE DÉMARRAGE
# ══════════════════════════════════════════════════════════════════════════
def test_une_tva_ecrite_en_decimal_ne_bloque_plus_le_demarrage():
    """« 20.0 » : le même taux, écrit en décimal — `int()` le refusait et
    l'application ne démarrait plus. Un AUTRE taux (5.5) est arrêté plus
    loin par la garde volontaire du tarif annoncé (960 € TTC), qui n'est pas
    ce qui est mesuré ici."""
    env = dict(os.environ, FORMATION_TVA_PCT="20.0", AUTO_MAJ="0", PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run([sys.executable, "-c",
                        "import formations_ia, app; print(formations_ia.TVA_PCT, app.FORM_TVA_PCT)"],
                       cwd=_RACINE, env=env, capture_output=True, text=True, timeout=120)
    assert p.returncode == 0, (p.stderr.strip().splitlines() or ["?"])[-1]
    assert p.stdout.split() == ["20", "20"], "les deux lectures de la TVA : %r" % p.stdout


@pytest.mark.parametrize("brut,attendu", [("20", 20), ("20.0", 20), ("5.5", 5.5), ("5,5", 5.5), ("", 20), ("abc", 20)])
def test_la_tva_est_lue_en_nombre_a_un_seul_endroit(brut, attendu):
    lu = F._lire_tva(brut)
    assert lu == attendu and type(lu) is type(attendu), "%r lu comme %r (%s)" % (brut, lu, type(lu).__name__)
    assert A.FORM_TVA_PCT == F.TVA_PCT, (A.FORM_TVA_PCT, F.TVA_PCT)


# ══════════════════════════════════════════════════════════════════════════
#  9. UNE RÉCLAMATION INTERROMPUE N'EST PAS UN PAIEMENT PERDU
# ══════════════════════════════════════════════════════════════════════════
def test_une_reclamation_interrompue_est_reprise_au_reessai_de_stripe(
        client, faux_stripe, faux_brevo, monkeypatch):
    """Le fil peut mourir ENTRE la réclamation et la fin du traitement : délai
    gunicorn de 120 s sur un envoi qui traîne, SIGKILL d'un déploiement, OOM.
    Ni `_faire` ni l'except extérieur n'attrapent SystemExit.

    MESURÉ AVANT CORRECTION : l'événement restait « vu » pour toujours, Stripe
    le relivrait et recevait 200 « duplicate », puis cessait de réessayer. Les
    séances restaient « en_attente_paiement » et leur créneau était libéré au
    bout de la retenue — alors que l'argent était encaissé."""
    j = panier(client, n=2)
    vrai = A._formation_ia_confirmer_paiement

    def tue(**kw):
        raise SystemExit(1)
    monkeypatch.setattr(A, "_formation_ia_confirmer_paiement", tue)
    _, charge = evenement_stripe(session_payee(j["commande"]))
    try:
        poster(A.app.test_client(), None, charge=charge)
    except SystemExit:
        pass                       # le worker gthread meurt exactement ainsi
    monkeypatch.setattr(A, "_formation_ia_confirmer_paiement", vrai)
    # LE RÉESSAI IMMÉDIAT : la réclamation date de quelques millisecondes.
    # Stripe doit repartir avec un non-2xx, jamais avec un acquittement.
    r1, _ = poster(A.app.test_client(), None, charge=charge)
    assert r1.status_code >= 400 and not (r1.get_json() or {}).get("duplicate"), (
        "réessai immédiat : HTTP %s %s — Stripe s'arrête sur un 2xx et le "
        "paiement est perdu" % (r1.status_code, r1.get_json()))
    assert statuts(j["commande"]) == ["en_attente_paiement"], statuts(j["commande"])
    # LES RÉCLAMATIONS VIEILLISSENT — celle de l'événement comme celle de la
    # caisse, toutes deux abandonnées par le même fil mort. Le réessai suivant
    # de Stripe les reprend.
    _exec("UPDATE stripe_events SET processed_at=?",
          ((datetime.datetime.utcnow() - datetime.timedelta(minutes=30)).isoformat(),))
    r2, _ = poster(A.app.test_client(), None, charge=charge)
    assert r2.status_code == 200 and statuts(j["commande"]) == ["payee"], (
        "réclamation abandonnée depuis 30 min, réessai : HTTP %s %s, séances %s"
        % (r2.status_code, r2.get_json(), statuts(j["commande"])))


# ══════════════════════════════════════════════════════════════════════════
#  10. LE RETOUR DE CAISSE NE REJOUE PAS — une session ne se confirme qu'une fois
# ══════════════════════════════════════════════════════════════════════════
def test_le_retour_ne_rejoue_pas_une_session_de_caisse_ancienne(client, faux_stripe, faux_brevo, monkeypatch):
    """La page /sentinel?activation=ok&session_id=cs_… rappelle le retour à
    CHAQUE chargement, et la route est publique.

    MESURÉ AVANT CORRECTION : après une résiliation, un simple rechargement
    remettait plan='entreprise' ET l'identifiant d'un abonnement mort — l'offre
    payante était acquise pour toujours sans le moindre prélèvement, et
    billing-run résiliait ensuite un abonnement qui n'existait plus."""
    monkeypatch.setenv("STRIPE_PRICE_ENTREPRISE", "price_ent_recette")
    cid = creer_client("rejeu@recette.test")
    connecter(client, cid)
    client.post("/api/sentinel/checkout", json={"plan": "entreprise"}, headers=NAVIGATEUR)
    sid = list(faux_stripe.sessions)[0]
    faux_stripe.payer(sid, customer="cus_rejeu", subscription="sub_rejeu")
    assert client.get("/api/stripe/retour?session_id=" + sid,
                      headers=NAVIGATEUR).get_json() == {"statut": "paye"}
    assert client_row(cid)["plan"] == "entreprise", client_row(cid)
    # L'abonnement est résilié chez Stripe : le compte repasse en gratuit.
    poster(client, {"id": "sub_rejeu", "object": "subscription", "status": "canceled",
                    "metadata": {"client_id": str(cid), "site": "conseilprev"}},
           "customer.subscription.deleted")
    assert client_row(cid)["plan"] == "gratuit", client_row(cid)
    # LA VIEILLE PAGE EST RECHARGÉE : la session est toujours « paid » chez Stripe.
    r = A.app.test_client().get("/api/stripe/retour?session_id=" + sid, headers=NAVIGATEUR)
    row = client_row(cid)
    assert (row["plan"], row["stripe_subscription_id"]) == ("gratuit", None), (
        "rechargement de /sentinel?activation=ok&session_id=%s : offre %r et abonnement %r rendus "
        "sans aucun prélèvement (réponse %s)" % (sid, row["plan"], row["stripe_subscription_id"], r.get_json()))


@pytest.mark.parametrize("statut", ["canceled", "unpaid", "incomplete_expired"])
def test_aucune_offre_n_est_activee_si_l_abonnement_n_est_plus_actif_chez_stripe(
        client, faux_stripe, faux_brevo, statut):
    """L'ARGENT EST-IL ENCORE LÀ ? Une session de caisse reste « paid » pour
    toujours ; l'abonnement qu'elle a ouvert, non. L'offre se lit sur
    l'abonnement, pas sur une caisse fermée il y a six mois."""
    cid = creer_client("mortvivant@recette.test")
    faux_stripe._abonnement("sub_mortvivant")["status"] = statut
    r, _ = poster(client, {"id": "cs_mv", "object": "checkout.session", "mode": "subscription",
                           "payment_status": "paid", "customer": "cus_mv",
                           "subscription": "sub_mortvivant",
                           "metadata": {"client_id": str(cid), "plan": "entreprise"}})
    row = client_row(cid)
    assert r.status_code == 200, r.get_json()
    assert (row["plan"], row["stripe_subscription_id"]) == ("gratuit", None), (
        "abonnement %s chez Stripe : offre %r activée et abonnement %r mémorisé"
        % (statut, row["plan"], row["stripe_subscription_id"]))


def test_le_retour_et_la_notification_simultanes_ne_confirment_qu_une_fois(
        client, faux_stripe, faux_brevo, monkeypatch):
    """Stripe livre checkout.session.completed AU MOMENT où il renvoie le
    navigateur : les deux requêtes arrivent ensemble sur 2 workers × 8 fils.

    MESURÉ AVANT CORRECTION : deux confirmations de la même caisse, donc deux
    « Réservation confirmée » au client et deux notifications internes — quatre
    crédits pris sur les 300 envois quotidiens du compte Brevo."""
    j = panier(client, n=2)
    sid = _q("SELECT stripe_session_id FROM formation_ia_resa WHERE commande=? AND gratuit=0",
             (j["commande"],))[0]["stripe_session_id"]
    faux_stripe.payer(sid, amount_total=96000)
    vrai = A._formation_ia_confirmer_paiement
    appels = []

    def lent(**kw):
        appels.append(kw)
        time.sleep(0.4)
        return vrai(**kw)
    monkeypatch.setattr(A, "_formation_ia_confirmer_paiement", lent)
    obj = dict(faux_stripe.sessions[sid])
    fils = [threading.Thread(target=poster, args=(A.app.test_client(), obj)),
            threading.Thread(target=A.app.test_client().get,
                             args=("/api/stripe/retour?session_id=" + sid,),
                             kwargs={"headers": NAVIGATEUR})]
    [f.start() for f in fils]; [f.join() for f in fils]
    assert len(appels) == 1, "%d confirmations pour un seul paiement ; sujets : %s" % (
        len(appels), sujets(faux_brevo))
    assert sujets(faux_brevo).count("Réservation confirmée — 1 séance(s)") == 1, sujets(faux_brevo)


def test_un_retour_encaisse_dont_la_confirmation_echoue_dit_en_attente_et_rend_la_main(
        client, faux_stripe, faux_brevo, monkeypatch, caplog):
    """Encaissé chez Stripe, mais la base est momentanément injoignable : la
    page ne doit pas annoncer « Paiement reçu » pour des séances restées en
    attente — et la réclamation prise par le retour doit être RENDUE, sinon la
    notification que Stripe réessaie trouverait la caisse « déjà traitée » et
    le paiement serait perdu pour de bon."""
    j = panier(client, n=2)
    sid = _q("SELECT stripe_session_id FROM formation_ia_resa WHERE commande=? AND gratuit=0",
             (j["commande"],))[0]["stripe_session_id"]
    faux_stripe.payer(sid, amount_total=96000)
    vrai = A._formation_ia_confirmer_paiement

    def panne(**kw):
        raise RuntimeError("base momentanément injoignable")
    monkeypatch.setattr(A, "_formation_ia_confirmer_paiement", panne)
    with caplog.at_level(logging.ERROR, logger="conseilprev"):
        r = client.get("/api/stripe/retour?session_id=" + sid, headers=NAVIGATEUR)
    assert r.get_json() == {"statut": "en_attente"}, (r.status_code, r.get_json())
    assert statuts(j["commande"]) == ["en_attente_paiement"], statuts(j["commande"])
    assert any("STRIPE_RETOUR_ECHEC" in m.getMessage() for m in caplog.records), (
        [m.getMessage() for m in caplog.records])
    monkeypatch.setattr(A, "_formation_ia_confirmer_paiement", vrai)
    r2, _ = poster(client, dict(faux_stripe.sessions[sid]))
    assert r2.status_code == 200 and statuts(j["commande"]) == ["payee"], (
        "la notification qui suit un retour en échec ne confirme plus rien : %s %s"
        % (r2.get_json(), statuts(j["commande"])))


@pytest.mark.parametrize("page", ["formation", "sentinel"])
def test_la_page_de_retour_efface_l_identifiant_de_session_de_la_barre_d_adresse(page):
    """EXÉCUTÉ : sans cela, l'adresse de retour reste dans la barre et chaque
    F5 — ou le rechargement que `sentinelCheckout` fait après un changement
    d'offre — redemande la confirmation de la MÊME caisse."""
    if page == "formation":
        src = io.open(os.path.join(_RACINE, "formation.html"), encoding="utf-8").read()
        code = _tranche(src, "(function retourPaiement(){", "\n  })();")
        depart = "?paiement=ok&session_id=cs_test_page"
        amorce = """
          const el = { hidden: true, className: '', innerHTML: '', textContent: '' };
          global.document = { getElementById: (id) => id === 'retour-paiement' ? el : null };
        """
        lancer = ""
    else:
        src = io.open(os.path.join(_RACINE, "sentinel.page.js"), encoding="utf-8").read()
        code = _tranche(src, "window.sentinelActivationToast = function(){", "\n};")
        depart = "?activation=ok&session_id=cs_test_page"
        amorce = """
          global.document = { createElement: () => ({ style: {}, textContent: '', innerHTML: '', parentNode: null }),
                              body: { appendChild: (t) => { t.parentNode = global.document.body; },
                                      removeChild: () => {} } };
          global.setTimeout = (f, ms) => (ms >= 1000 ? 0 : require('timers').setTimeout(f, ms));
        """
        lancer = "window.sentinelActivationToast();"
    o = _node("""
      const etat = { search: '%s', remplacements: [], appels: [] };
      global.window = global;
      global.location = { pathname: '/page', get search(){ return etat.search; } };
      global.history = { replaceState: (a, b, u) => { etat.remplacements.push(String(u));
                          etat.search = String(u).indexOf('?') > -1 ? String(u).slice(String(u).indexOf('?')) : ''; } };
      global.fetch = (u) => { etat.appels.push(String(u));
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ statut: 'paye' }) }); };
    """ % depart + amorce + code + lancer + """
      require('timers').setTimeout(() => process.stdout.write(JSON.stringify(etat)), 40);
    """)
    assert any("cs_test_page" in a for a in o["appels"]), (
        "la page n'a rien demandé au serveur : %s" % o["appels"])
    assert o["remplacements"], (
        "l'adresse de retour reste dans la barre : un rechargement rejouerait la caisse")
    assert all("session_id" not in u and "=ok" not in u for u in o["remplacements"]), o["remplacements"]


# ══════════════════════════════════════════════════════════════════════════
#  11. UNE OFFRE SUPÉRIEURE NE S'ACCORDE PAS SUR UN ABONNEMENT QUI NE PAIE PAS
# ══════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("statut", ["past_due", "unpaid", "incomplete", "paused"])
def test_un_abonnement_impaye_n_obtient_pas_l_offre_superieure(client, faux_stripe, monkeypatch, statut):
    """MESURÉ AVANT CORRECTION : `Subscription.modify` avec
    `create_prorations` ne facture RIEN tout de suite — il ajoute la
    différence à une facture que ce client ne paie déjà pas — et l'offre la
    plus chère était posée dans la foulée. CGV 3.4 : un impayé suspend."""
    monkeypatch.setenv("STRIPE_PRICE_ENTREPRISE", "price_ent_recette")
    cid = creer_client("impaye3@recette.test", plan="pro", sub="sub_impaye3", cust="cus_impaye3")
    faux_stripe._abonnement("sub_impaye3")["status"] = statut
    connecter(client, cid)
    r = client.post("/api/sentinel/checkout", json={"plan": "entreprise"}, headers=NAVIGATEUR)
    modifs = [x.form for x in faux_stripe.recues("POST", "/v1/subscriptions/sub_impaye3")]
    etat = {"http": r.status_code, "reponse": r.get_json(),
            "plan": client_row(cid)["plan"], "modifications": modifs}
    assert client_row(cid)["plan"] == "pro", (
        "abonnement %s : l'offre %r est accordée sans encaissement — %s" % (statut, etat["plan"], etat))
    assert r.status_code == 402 and not modifs, etat
    assert not faux_stripe.recues("POST", "/v1/checkout/sessions"), (
        "une seconde caisse est ouverte alors que la première n'est pas réglée")


@pytest.mark.parametrize("cas", ["canceled", "resource_missing"])
def test_un_abonnement_mort_chez_stripe_rouvre_une_caisse(client, faux_stripe, monkeypatch, cas):
    """C'est l'état de la production : un abonnement résilié chez Stripe laisse
    son identifiant en base. Le client qui revient à la caisse doit pouvoir se
    réabonner — pas recevoir un 502 parce qu'on a tenté de modifier un mort."""
    monkeypatch.setenv("STRIPE_PRICE_ENTREPRISE", "price_ent_recette")
    cid = creer_client("mort@recette.test", plan="pro", sub="sub_mort")
    if cas == "canceled":
        faux_stripe._abonnement("sub_mort")["status"] = "canceled"
    else:
        faux_stripe.pannes["GET /v1/subscriptions/sub_mort"] = (
            404, {"error": {"type": "invalid_request_error", "code": "resource_missing",
                            "message": "No such subscription"}})
    connecter(client, cid)
    r = client.post("/api/sentinel/checkout", json={"plan": "entreprise"}, headers=NAVIGATEUR)
    j = r.get_json()
    caisses = faux_stripe.recues("POST", "/v1/checkout/sessions")
    assert r.status_code == 200 and j.get("ok") is True and j.get("url"), (cas, r.status_code, j)
    assert len(caisses) == 1, "%s : %d caisse(s) ouverte(s)" % (cas, len(caisses))
    assert not faux_stripe.recues("POST", "/v1/subscriptions/sub_mort"), (
        "%s : l'abonnement mort a été modifié" % cas)


def test_l_activation_memorise_l_abonnement_meme_quand_l_offre_est_deja_posee(
        client, faux_stripe, faux_brevo):
    """Un client passé « pro » à la main par CONSEILPREV, sans abonnement, paie
    ensuite l'offre Pro. Si l'activation se croit déjà faite, l'abonnement et le
    client Stripe ne sont jamais mémorisés : un passage en « gratuit » ne
    résilierait rien, et Stripe continuerait de prélever."""
    cid = creer_client("deja@recette.test", plan="pro")
    r, _ = poster(client, {"id": "cs_deja", "object": "checkout.session", "mode": "subscription",
                           "payment_status": "paid", "customer": "cus_deja",
                           "subscription": "sub_deja",
                           "metadata": {"client_id": str(cid), "plan": "pro"}})
    row = client_row(cid)
    assert r.status_code == 200, r.get_json()
    assert (row["plan"], row["stripe_subscription_id"], row["stripe_customer_id"]) \
        == ("pro", "sub_deja", "cus_deja"), row


# ══════════════════════════════════════════════════════════════════════════
#  12. LA RÉSILIATION QUE LE SITE A DEMANDÉE NE RÉTROGRADE PERSONNE
# ══════════════════════════════════════════════════════════════════════════
def test_la_resiliation_demandee_par_le_site_est_marquee_chez_stripe(base, faux_stripe):
    """Sans marque, le `customer.subscription.deleted` qui revient est
    indiscernable d'une résiliation subie."""
    cid = creer_client("marque@recette.test", plan="entreprise", sub="sub_marque", cust="cus_marque")
    assert A._billing_cancel_subscription(cid) is True
    envois = faux_stripe.recues("DELETE", "/v1/subscriptions/sub_marque")
    assert len(envois) == 1, "%d résiliation(s) envoyée(s)" % len(envois)
    # Les paramètres d'un DELETE voyagent dans l'URL, pas dans un corps.
    marque = (envois[0].requete.get("cancellation_details[comment]") or [""])[0]
    assert marque.startswith(A.STRIPE_RESILIATION_MARQUE), (
        "la résiliation demandée par le site n'est pas marquée : %s" % envois[0].requete)


def test_le_client_passe_en_facturation_par_resultats_ne_retombe_pas_en_gratuit(
        client, faux_stripe, faux_brevo):
    """billing-run résilie l'abonnement, puis Stripe notifie la résiliation que
    le site vient lui-même de demander.

    MESURÉ AVANT CORRECTION : ce retour rétrogradait en « gratuit » un client
    désormais facturé au résultat — il perdait tous ses modules. Les deux ordres
    d'arrivée sont mesurés : la notification AVANT et APRÈS l'oubli du lien."""
    marque = A.STRIPE_RESILIATION_MARQUE + "raas"
    # (a) La notification arrive AVANT que le lien local soit oublié.
    ca = creer_client("raas_a@recette.test", plan="entreprise", sub="sub_raas_a", cust="cus_raas_a")
    poster(client, {"id": "sub_raas_a", "object": "subscription", "status": "canceled",
                    "cancellation_details": {"comment": marque}, "metadata": {}},
           "customer.subscription.deleted")
    ra = client_row(ca)
    assert (ra["plan"], ra["stripe_subscription_id"]) == ("entreprise", "sub_raas_a"), (
        "notification reçue avant l'oubli du lien : %s" % ra)
    # (b) Et APRÈS : le lien est déjà NULL, seul metadata.client_id reste.
    cb = creer_client("raas_b@recette.test", plan="entreprise", sub="sub_raas_b", cust="cus_raas_b")
    assert A._billing_cancel_subscription(cb) is True
    poster(client, {"id": "sub_raas_b", "object": "subscription", "status": "canceled",
                    "cancellation_details": {"comment": marque},
                    "metadata": {"client_id": str(cb), "site": "conseilprev"}},
           "customer.subscription.deleted")
    assert client_row(cb)["plan"] == "entreprise", (
        "notification reçue après l'oubli du lien : offre %r" % client_row(cb)["plan"])


def test_un_abonnement_inconnu_ici_ne_retrograde_aucun_client(client, faux_stripe, faux_brevo):
    """Le compte Stripe est PARTAGÉ avec conseilprevcyber. Un
    customer.subscription.deleted d'un abonnement inconnu de ce site, portant un
    metadata.client_id, faisait passer en « gratuit » le client de CE site qui
    porte ce numéro — une offre posée à la main disparaissait sans raison."""
    cid = creer_client("autresite@recette.test", plan="pro")        # offre posée par set-plan
    r, _ = poster(client, {"id": "sub_de_conseilprevcyber", "object": "subscription",
                           "status": "canceled", "metadata": {"client_id": str(cid)}},
                  "customer.subscription.deleted")
    assert r.status_code == 200, r.get_json()
    assert client_row(cid)["plan"] == "pro", (
        "un abonnement d'un autre site du compte a rétrogradé ce client en %r"
        % client_row(cid)["plan"])


# ══════════════════════════════════════════════════════════════════════════
#  13. UNE SÉANCE ANNULÉE NE REVIENT PAS À LA VIE
# ══════════════════════════════════════════════════════════════════════════
def test_une_seance_annulee_et_remboursee_ne_repasse_pas_payee(client, faux_stripe, faux_brevo):
    """MESURÉ AVANT CORRECTION : le confirmateur retenait toute ligne « != payee »,
    donc AUSSI les annulées. Une séance annulée et remboursée redevenait
    « payée » — avec le montant de TOUTE la commande, puisque le prorata ne se
    répartissait plus que sur elle. Le second remboursement, calculé sur ce
    montant gonflé, vidait le paiement."""
    j = panier(client, n=3)                    # 1 offerte + 2 payantes
    faux_stripe.payer(list(faux_stripe.sessions)[0], amount_total=192000)
    A._formation_ia_confirmer_paiement(commande=j["commande"], montant_ttc_cents=192000)
    av = _q("SELECT id, jeton, statut, paye_ttc_cents FROM formation_ia_resa "
            "WHERE commande=? AND gratuit=0 ORDER BY id", (j["commande"],))
    assert [x["statut"] for x in av] == ["payee", "payee"], av
    assert [x["paye_ttc_cents"] for x in av] == [96000, 96000], av
    ra = client.post("/api/formation/annulation", json={"jeton": av[0]["jeton"]}, headers=NAVIGATEUR)
    assert ra.status_code == 200 and ra.get_json().get("ok"), ra.get_json()
    # LA PAGE DE RETOUR EST ROUVERTE (historique, F5) : le confirmateur repasse.
    A._formation_ia_confirmer_paiement(commande=j["commande"], montant_ttc_cents=192000)
    ap = _q("SELECT id, statut, paye_ttc_cents FROM formation_ia_resa "
            "WHERE commande=? AND gratuit=0 ORDER BY id", (j["commande"],))
    montants = [int(x.form["amount"]) for x in faux_stripe.recues("POST", "/v1/refunds")]
    assert ap[0]["statut"] == "annulee", (
        "la séance annulée et remboursée est repassée %r ; remboursements : %s"
        % (ap[0]["statut"], montants))
    assert ap[0]["paye_ttc_cents"] == 96000, (
        "le montant réglé sur la séance annulée est passé à %s c : le remboursement "
        "suivant serait calculé dessus" % ap[0]["paye_ttc_cents"])
    assert montants == [48000], "remboursements envoyés : %s" % montants


def test_le_montant_encaisse_se_repartit_sur_toute_la_commande_pas_sur_le_reliquat(
        client, faux_stripe, faux_brevo):
    """La caisse a été ouverte pour DEUX séances payantes, soit 1 920 € TTC. Le
    client en annule une avant de payer, puis règle. La séance qui reste ne
    porte que SA part : lui attribuer tout `amount_total` ferait rembourser
    960 € pour une séance qui en a coûté 480."""
    j = panier(client, n=3)
    lig = _q("SELECT id, jeton FROM formation_ia_resa WHERE commande=? AND gratuit=0 ORDER BY id",
             (j["commande"],))
    assert client.post("/api/formation/annulation", json={"jeton": lig[0]["jeton"]},
                       headers=NAVIGATEUR).status_code == 200
    A._formation_ia_confirmer_paiement(commande=j["commande"], montant_ttc_cents=192000)
    ap = _q("SELECT id, statut, paye_ttc_cents FROM formation_ia_resa "
            "WHERE commande=? AND gratuit=0 ORDER BY id", (j["commande"],))
    assert [x["statut"] for x in ap] == ["annulee", "payee"], ap
    assert ap[1]["paye_ttc_cents"] == 96000, (
        "la séance réglée porte %s c au lieu de 96 000 : c'est là-dessus que se "
        "calculera son remboursement" % ap[1]["paye_ttc_cents"])


def test_une_seance_annulee_avant_paiement_puis_reprise_n_est_pas_confirmee(
        client, faux_stripe, faux_brevo):
    """X réserve, annule AVANT de payer (le créneau est libéré), Y le reprend,
    puis X termine son paiement — sa session Stripe reste ouverte une heure.

    MESURÉ AVANT CORRECTION : la ligne annulée de X repassait « payée ». Deux
    séances actives sur une date qui n'en porte qu'une, alors que le formateur
    ne se dédouble pas."""
    cr = creneaux()
    jx = panier(client, n=2, dates=cr)
    lig = _q("SELECT id, jeton FROM formation_ia_resa WHERE commande=? AND gratuit=0",
             (jx["commande"],))[0]
    assert client.post("/api/formation/annulation", json={"jeton": lig["jeton"]},
                       headers=NAVIGATEUR).status_code == 200
    ry = client.post("/api/formation/inscription", json={
        "seances": [{"sujet": F.SUJETS[2]["cle"], "creneau": cr[1]}],
        "nom": "Repreneur", "prenom": "Yann", "email": "repreneur2@recette.test",
        "entreprise": "AUTRE SAS", "siret": "900000999",
        "telephone": "+33 6 98 76 54 32", "lieu": "1 rue du Test, 75000 Paris"})
    assert ry.status_code == 200, (ry.status_code, ry.get_json())
    A._formation_ia_confirmer_paiement(commande=jx["commande"], montant_ttc_cents=96000)
    st = _q("SELECT statut FROM formation_ia_resa WHERE id=?", (lig["id"],))[0]["statut"]
    assert st == "annulee", (
        "la séance annulée de X est repassée %r : deux clients tiennent le %s" % (st, cr[1]))


def test_un_paiement_sans_seance_a_confirmer_est_signale_a_conseilprev(
        client, faux_stripe, faux_brevo):
    """L'argent est encaissé et plus aucune séance n'est confirmable : ni
    silence, ni remboursement automatique — CONSEILPREV décide, donc CONSEILPREV
    est prévenu."""
    cr = creneaux()
    jx = panier(client, n=2, dates=cr)
    lig = _q("SELECT jeton FROM formation_ia_resa WHERE commande=? AND gratuit=0",
             (jx["commande"],))[0]
    client.post("/api/formation/annulation", json={"jeton": lig["jeton"]}, headers=NAVIGATEUR)
    avant = len(faux_brevo.recues("POST", "/v3/smtp/email"))
    A._formation_ia_confirmer_paiement(commande=jx["commande"], montant_ttc_cents=96000)
    envois = [x.json for x in faux_brevo.recues("POST", "/v3/smtp/email")][avant:]
    dest = [x["to"][0]["email"] for x in envois]
    assert A.CONSEILPREV_NOTIFY_EMAIL in dest, (
        "encaissement sans séance à confirmer : personne n'est prévenu (%s)" % dest)
    assert jx["commande"] in " ".join(x["htmlContent"] for x in envois), envois


# ══════════════════════════════════════════════════════════════════════════
#  14. EFFACEMENT RGPD : ne pas perdre le seul moyen d'arrêter un prélèvement
# ══════════════════════════════════════════════════════════════════════════
def test_l_effacement_rgpd_garde_le_lien_quand_stripe_refuse_la_resiliation(client, faux_stripe):
    """Stripe refuse le DELETE : l'abonnement reste « active » et continue de
    prélever une personne qui a demandé l'effacement. Effacer quand même son
    identifiant, c'est perdre le seul moyen de l'arrêter — l'art. 17.3.b couvre
    la conservation de ces identifiants techniques, le temps de résilier."""
    cid = creer_client("rgpd2@recette.test", plan="pro", sub="sub_rgpd2", cust="cus_rgpd2")
    for t in ("client_entites", "client_connecteurs", "client_formations"):
        _exec("CREATE TABLE IF NOT EXISTS %s (id INTEGER PRIMARY KEY, client_id INTEGER)" % t)
    faux_stripe.pannes["DELETE /v1/subscriptions/sub_rgpd2"] = (
        500, {"error": {"type": "api_error", "message": "panne simulée"}})
    admin(client)
    j = client.post("/api/rgpd/effacement", json={"email": "rgpd2@recette.test"},
                    headers=NAVIGATEUR).get_json()
    row = client_row(cid)
    bilan = j.get("bilan") or {}
    assert bilan.get("abonnement") == "non_resilie", j
    assert row["email"] != "rgpd2@recette.test", "l'effacement doit avoir lieu malgré tout : %s" % j
    assert row["stripe_subscription_id"] == "sub_rgpd2", (
        "identifiant d'abonnement effacé alors que Stripe a refusé la résiliation : "
        "le compte anonymisé continue d'être prélevé et plus rien ne permet de l'arrêter")
    assert bilan.get("abonnement_a_resilier") == "sub_rgpd2", (
        "le bilan rendu à l'administrateur ne nomme pas l'abonnement à résilier : %s" % bilan)
