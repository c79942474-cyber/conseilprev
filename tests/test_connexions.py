# -*- coding: utf-8 -*-
"""Stripe et Brevo sont-ils VRAIMENT branchés sur CE service ? — mesuré contre
de faux comptes réglés comme les vrais.

LE DÉFAUT QUI A FAIT ÉCRIRE CES RÈGLES. Pendant un mois, le seul point de
réception Stripe du compte visait `https://conseilprev.onrender.com/api/stripe/
webhook`, un hôte sans service, alors que le site vit sur
`conseilprevia.onrender.com`. Les paiements partaient, aucune confirmation
n'arrivait, et rien dans le code ne le mesurait : le défaut n'est pas dans le
code, il est dans l'écart entre la configuration du service et les comptes.
Côté Brevo, l'expéditeur par défaut n'est pas vérifié et six envois sur treize
visaient une adresse non routable.

CE QUE CES RÈGLES ÉPROUVENT. Les faux serveurs (tests/faux_services.py) sont
d'abord réglés COMME LE VRAI COMPTE avant correction : chaque alerte attendue
doit sortir, avec son code et sa gravité. Puis réglés juste : aucune alerte.
Puis, contrôle par contrôle, un seul réglage est cassé et c'est l'alerte de CE
contrôle qui doit tomber. La route est réservée à l'administrateur, ne recopie
aucune clé, répond 200 quand un service est en panne, et ne fait que LIRE.
L'outil de l'exploitant partage cette logique et n'importe pas l'application.
"""
import ast
import datetime
import importlib.util
import io
import json
import os
import secrets
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time

import pytest
import requests
import stripe

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RACINE)

import app as A                                                     # noqa: E402
import connexions                                                   # noqa: E402

ICI_SITE = "https://conseilprevia.onrender.com"
ATTENDU = ICI_SITE + connexions.CHEMIN_WEBHOOK
ANCIEN = "https://conseilprev.onrender.com/api/stripe/webhook"
VERSION_DU_POINT_REEL = "2026-05-27.dahlia"
EVENEMENTS_REELS = ("checkout.session.completed", "invoice.paid", "invoice.payment_failed")
#: Les secrets de recette posés par les fixtures : aucun ne doit jamais
#: apparaître dans une réponse, un rapport ou une sortie d'outil.
SECRETS = ("sk_test_recette_locale", "xkeysib-recette-locale", "whsec_recette_locale")
NODE = shutil.which("node")
OUTIL = os.path.join(_RACINE, "outils", "verifier_connexions.py")


# ══════════════════════════════════════════════════════════════════════════
#  RÉGLAGES DES FAUX COMPTES
# ══════════════════════════════════════════════════════════════════════════

def _point(url, evenements, version, statut="enabled"):
    return {"id": "we_recette", "object": "webhook_endpoint",
            "status": statut, "url": url, "api_version": version,
            "enabled_events": list(evenements)}


def _prix(pid, actif=True, recurrent=True):
    return {"id": pid, "object": "price", "active": actif, "unit_amount": 4900,
            "currency": "eur", "recurring": {"interval": "month"} if recurrent else None}


def compte_reel(faux_stripe, faux_brevo):
    """Le compte TEL QU'IL ÉTAIT le 24/09/2026 : un seul point de réception,
    vers l'hôte sans service, trois événements, une version d'API en retard ;
    l'expéditeur vérifié n'est pas celui du code. Rend le MAIL_FROM du code."""
    faux_stripe.points.append(_point(ANCIEN, EVENEMENTS_REELS, VERSION_DU_POINT_REEL))
    faux_stripe.compte["livemode"] = True
    faux_stripe.prix["price_pro"] = _prix("price_pro")
    faux_stripe.prix["price_entreprise"] = _prix("price_entreprise")
    return connexions.MAIL_FROM_PAR_DEFAUT


def compte_juste(faux_stripe, faux_brevo):
    """Le compte réglé comme il doit l'être. Rend le MAIL_FROM vérifié."""
    faux_stripe.points.append(_point(ATTENDU, EVENEMENTS_REELS, stripe.api_version))
    faux_stripe.compte["livemode"] = True
    faux_stripe.prix["price_pro"] = _prix("price_pro")
    faux_stripe.prix["price_entreprise"] = _prix("price_entreprise")
    return faux_brevo.expediteurs[0]["email"]


def _config(faux_brevo, mail_from, **extra):
    c = {"site_base_url": ICI_SITE, "stripe_webhook_secret_present": True,
         "stripe_evenements_requis": connexions.EVENEMENTS_TRAITES,
         "stripe_prix": {"pro": "price_pro", "entreprise": "price_entreprise"},
         "brevo_api_key": "xkeysib-recette-locale", "brevo_api_base": faux_brevo.url,
         "mail_from": mail_from}
    c.update(extra)
    return c


def _stripe_pret():
    """Le module réglé comme la route le règle."""
    return A._stripe_pret(os.environ["STRIPE_SECRET_KEY"])


def _il_y_a(heures):
    return (datetime.datetime.utcnow() - datetime.timedelta(hours=heures)).isoformat()


def _base(evenements=(), envois=()):
    """Une base en mémoire avec les deux tables telles qu'app.py les crée.
    `envois` : (destinataire, succes, raison_echec, date_envoi)."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE stripe_events (event_id TEXT PRIMARY KEY, processed_at TEXT)")
    conn.execute("CREATE TABLE email_log (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                 "destinataire TEXT NOT NULL, sujet TEXT, methode TEXT, "
                 "succes INTEGER NOT NULL, raison_echec TEXT, date_envoi TEXT NOT NULL)")
    for i, quand in enumerate(evenements):
        conn.execute("INSERT INTO stripe_events VALUES (?, ?)", ("evt_%d" % i, quand))
    for dest, succes, raison, quand in envois:
        conn.execute("INSERT INTO email_log (destinataire, sujet, methode, succes, "
                     "raison_echec, date_envoi) VALUES (?,?,?,?,?,?)",
                     (dest, "sujet", "brevo_api", succes, raison, quand))
    conn.commit()

    def lire(sql, params=()):
        return [dict(r) for r in conn.execute(sql, tuple(params)).fetchall()]
    return lire


def _journal_reel():
    """Treize envois, six vers l'adresse non routable (contexte du 24/09)."""
    envois = [("client%d@exemple.test" % i, 1, None, _il_y_a(i)) for i in range(7)]
    envois += [("conseilprev@internal.system", 1, None, _il_y_a(i)) for i in range(6)]
    return _base(evenements=[_il_y_a(24 * 29)], envois=envois)


def _diag(faux_brevo, mail_from, base=None, stripe_pret=True, **extra):
    return connexions.diagnostic(stripe=_stripe_pret() if stripe_pret else None,
                                 session=requests.Session(),
                                 config=_config(faux_brevo, mail_from, **extra), base=base)


def _codes(diag):
    return {a["code"]: a for a in diag["alertes"]}


def _gravites(diag):
    return {a["code"]: a["gravite"] for a in diag["alertes"]}


# ══════════════════════════════════════════════════════════════════════════
#  1. LE COMPTE TEL QU'IL ÉTAIT, PUIS RÉGLÉ JUSTE
# ══════════════════════════════════════════════════════════════════════════

def test_le_compte_tel_qu_il_etait_declenche_exactement_les_alertes_documentees(
        faux_stripe, faux_brevo):
    """Point vers l'hôte sans service, expéditeur non vérifié, envois non
    routables : les trois défauts du rapport, chacun avec sa gravité — et
    l'ancien point est cité, pour qu'on voie OÙ partaient les notifications."""
    mail_from = compte_reel(faux_stripe, faux_brevo)
    d = _diag(faux_brevo, mail_from, base=_journal_reel())
    assert _gravites(d) == {
        "stripe_webhook_absent": "bloquant",
        "stripe_webhook_autres_points": "info",
        "brevo_expediteur_non_verifie": "bloquant",
        "brevo_envois_non_routables": "important",
    }, d["alertes"]
    m = _codes(d)["stripe_webhook_absent"]["message"]
    assert ATTENDU in m and ANCIEN in m, "le message ne dit pas d'où vers où : %s" % m
    assert "6 envoi" in _codes(d)["brevo_envois_non_routables"]["message"]
    assert d["brevo"]["envois_non_routables"] == 6
    assert d["stripe"]["point_actif"] is False
    assert d["stripe"]["autres_points"] == [ANCIEN]


def test_le_compte_regle_juste_ne_donne_aucune_alerte(faux_stripe, faux_brevo):
    mail_from = compte_juste(faux_stripe, faux_brevo)
    d = _diag(faux_brevo, mail_from,
              base=_base(evenements=[_il_y_a(2)], envois=[("c@exemple.test", 1, None, _il_y_a(1))]))
    assert d["alertes"] == [], d["alertes"]
    s, b = d["stripe"], d["brevo"]
    assert s["point_actif"] is True and s["evenements_manquants"] == []
    assert s["compte"] == {"id": "acct_recette", "livemode": True, "charges_enabled": True}
    assert s["prix"]["pro"] == {"id": "price_pro", "actif": True, "recurrent": True}
    assert 1.9 <= s["dernier_evenement"]["age_heures"] <= 2.2, s["dernier_evenement"]
    assert b["expediteur_verifie"] is True and b["compte"]["credits"] == 300
    assert b["journal_24h"] == {"disponible": True, "ok": 1, "echecs": 0, "derniere_erreur": None}
    assert b["envois_non_routables"] == 0
    assert d["verifie_le"][:4] == str(datetime.datetime.utcnow().year)


# ══════════════════════════════════════════════════════════════════════════
#  2. UN CONTRÔLE, UNE ALERTE — chaque réglage cassé seul
# ══════════════════════════════════════════════════════════════════════════

def test_un_point_de_reception_vers_un_autre_hote_est_bloquant(faux_stripe, faux_brevo):
    mail_from = compte_juste(faux_stripe, faux_brevo)
    faux_stripe.points[0]["url"] = ANCIEN
    d = _diag(faux_brevo, mail_from)
    assert _gravites(d).get("stripe_webhook_absent") == "bloquant", d["alertes"]


def test_un_point_desactive_ne_compte_pas(faux_stripe, faux_brevo):
    """Un point vers la bonne adresse mais DÉSACTIVÉ chez Stripe ne reçoit
    rien : c'est le même défaut qu'un point absent."""
    mail_from = compte_juste(faux_stripe, faux_brevo)
    faux_stripe.points[0]["status"] = "disabled"
    d = _diag(faux_brevo, mail_from)
    assert "stripe_webhook_absent" in _codes(d), d["alertes"]
    assert "disabled" in _codes(d)["stripe_webhook_absent"]["message"]


def test_les_evenements_manquants_sont_signales_et_nommes(faux_stripe, faux_brevo):
    mail_from = compte_juste(faux_stripe, faux_brevo)
    requis = EVENEMENTS_REELS + ("checkout.session.async_payment_succeeded",
                                 "customer.subscription.deleted")
    d = _diag(faux_brevo, mail_from, stripe_evenements_requis=requis)
    a = _codes(d).get("stripe_webhook_evenements_manquants")
    assert a and a["gravite"] == "important", d["alertes"]
    assert "checkout.session.async_payment_succeeded" in a["message"]
    assert "customer.subscription.deleted" in a["message"]
    assert "checkout.session.completed" not in a["message"], "un événement couvert est dit manquant"
    assert d["stripe"]["evenements_manquants"] == list(requis[3:])


def test_un_point_abonne_a_tout_couvre_tout(faux_stripe, faux_brevo):
    mail_from = compte_juste(faux_stripe, faux_brevo)
    faux_stripe.points[0]["enabled_events"] = ["*"]
    d = _diag(faux_brevo, mail_from, stripe_evenements_requis=EVENEMENTS_REELS + ("charge.refunded",))
    assert "stripe_webhook_evenements_manquants" not in _codes(d), d["alertes"]


def test_une_version_d_api_differente_est_une_info(faux_stripe, faux_brevo):
    mail_from = compte_juste(faux_stripe, faux_brevo)
    faux_stripe.points[0]["api_version"] = VERSION_DU_POINT_REEL
    d = _diag(faux_brevo, mail_from)
    a = _codes(d).get("stripe_webhook_version_api")
    assert a and a["gravite"] == "info", d["alertes"]
    assert VERSION_DU_POINT_REEL in a["message"] and stripe.api_version in a["message"]


def test_le_secret_de_signature_absent_est_bloquant(faux_stripe, faux_brevo):
    mail_from = compte_juste(faux_stripe, faux_brevo)
    d = _diag(faux_brevo, mail_from, stripe_webhook_secret_present=False)
    assert _gravites(d).get("stripe_secret_webhook_absent") == "bloquant", d["alertes"]
    assert d["stripe"]["secret_webhook_present"] is False


@pytest.mark.parametrize("cas,code", [
    ("inactif", "stripe_prix_inactif"),
    ("ponctuel", "stripe_prix_non_recurrent"),
    ("absent", "stripe_prix_absent"),
    ("inconnu", "stripe_prix_illisible"),
])
def test_un_prix_d_abonnement_inutilisable_est_signale(faux_stripe, faux_brevo, cas, code):
    mail_from = compte_juste(faux_stripe, faux_brevo)
    prix = {"pro": "price_pro", "entreprise": "price_entreprise"}
    if cas == "inactif":
        faux_stripe.prix["price_entreprise"] = _prix("price_entreprise", actif=False)
    elif cas == "ponctuel":
        faux_stripe.prix["price_entreprise"] = _prix("price_entreprise", recurrent=False)
    elif cas == "absent":
        prix["entreprise"] = ""
    else:
        faux_stripe.pannes["GET /v1/prices/price_entreprise"] = (
            404, {"error": {"type": "invalid_request_error", "message": "No such price"}})
    d = _diag(faux_brevo, mail_from, stripe_prix=prix)
    assert _gravites(d).get(code) == "important", d["alertes"]
    assert "entreprise" in _codes(d)[code]["message"]
    assert {c for c in _codes(d) if c.startswith("stripe_prix_")} == {code}, d["alertes"]


def test_un_compte_qui_ne_peut_pas_encaisser_est_bloquant(faux_stripe, faux_brevo):
    mail_from = compte_juste(faux_stripe, faux_brevo)
    faux_stripe.compte["charges_enabled"] = False
    d = _diag(faux_brevo, mail_from)
    assert _gravites(d).get("stripe_encaissement_desactive") == "bloquant", d["alertes"]


def test_une_cle_de_test_est_une_info(faux_stripe, faux_brevo):
    mail_from = compte_juste(faux_stripe, faux_brevo)
    faux_stripe.compte["livemode"] = False
    d = _diag(faux_brevo, mail_from)
    assert _gravites(d).get("stripe_mode_test") == "info", d["alertes"]


@pytest.mark.parametrize("credits,attendu", [(49, "important"), (50, None), (0, "important")])
def test_des_credits_brevo_sous_le_seuil_sont_signales(faux_stripe, faux_brevo, credits, attendu):
    mail_from = compte_juste(faux_stripe, faux_brevo)
    faux_brevo.credits = credits
    d = _diag(faux_brevo, mail_from)
    assert _gravites(d).get("brevo_credits_faibles") == attendu, d["alertes"]
    assert d["brevo"]["compte"]["credits"] == credits


def test_un_expediteur_non_verifie_est_bloquant_et_les_actifs_sont_cites(faux_stripe, faux_brevo):
    compte_juste(faux_stripe, faux_brevo)
    verifie = faux_brevo.expediteurs[0]["email"]
    d = _diag(faux_brevo, connexions.MAIL_FROM_PAR_DEFAUT)
    a = _codes(d).get("brevo_expediteur_non_verifie")
    assert a and a["gravite"] == "bloquant", d["alertes"]
    assert connexions.MAIL_FROM_PAR_DEFAUT in a["message"] and verifie in a["message"]


def test_un_expediteur_verifie_mais_inactif_ne_compte_pas(faux_stripe, faux_brevo):
    mail_from = compte_juste(faux_stripe, faux_brevo)
    faux_brevo.expediteurs[0]["active"] = False
    d = _diag(faux_brevo, mail_from)
    assert "brevo_expediteur_non_verifie" in _codes(d), d["alertes"]
    assert d["brevo"]["expediteurs_actifs"] == []


def test_la_casse_de_l_expediteur_ne_compte_pas(faux_stripe, faux_brevo):
    mail_from = compte_juste(faux_stripe, faux_brevo)
    d = _diag(faux_brevo, mail_from.upper())
    assert "brevo_expediteur_non_verifie" not in _codes(d), d["alertes"]


def test_des_envois_vers_une_adresse_non_routable_sont_signales(faux_stripe, faux_brevo):
    mail_from = compte_juste(faux_stripe, faux_brevo)
    base = _base(envois=[("conseilprev@internal.system", 1, None, _il_y_a(24 * 10)),
                         ("conseilprev@internal.system", 1, None, _il_y_a(1)),
                         ("client@exemple.test", 1, None, _il_y_a(1))])
    d = _diag(faux_brevo, mail_from, base=base)
    a = _codes(d).get("brevo_envois_non_routables")
    assert a and a["gravite"] == "important" and a["message"].startswith("2 envoi"), d["alertes"]
    assert d["brevo"]["envois_non_routables"] == 2


def test_le_journal_des_24_h_est_resume_avec_la_derniere_erreur(faux_stripe, faux_brevo):
    mail_from = compte_juste(faux_stripe, faux_brevo)
    base = _base(envois=[("a@exemple.test", 1, None, _il_y_a(1)),
                         ("b@exemple.test", 1, None, _il_y_a(2)),
                         ("c@exemple.test", 0, "http_402", _il_y_a(3)),
                         ("d@exemple.test", 0, "http_500", _il_y_a(5)),
                         ("e@exemple.test", 0, "vieux", _il_y_a(30))])
    j = _diag(faux_brevo, mail_from, base=base)["brevo"]["journal_24h"]
    assert (j["ok"], j["echecs"]) == (2, 2), j
    assert j["derniere_erreur"]["raison"] == "http_402", j


# ══════════════════════════════════════════════════════════════════════════
#  3. PANNES, LENTEURS, BASE ABSENTE : DES ALERTES, JAMAIS D'EXCEPTION
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("service,panne,code", [
    ("stripe", "GET /v1/account", "stripe_compte_illisible"),
    ("stripe", "GET /v1/webhook_endpoints", "stripe_webhooks_illisibles"),
    ("brevo", "GET /v3/account", "brevo_compte_illisible"),
    ("brevo", "GET /v3/senders", "brevo_expediteurs_illisibles"),
], ids=["stripe_compte", "stripe_webhooks", "brevo_compte", "brevo_expediteurs"])
def test_une_panne_du_service_donne_une_alerte_pas_une_exception(
        faux_stripe, faux_brevo, service, panne, code):
    mail_from = compte_juste(faux_stripe, faux_brevo)
    faux = faux_stripe if service == "stripe" else faux_brevo
    faux.pannes[panne] = (500, {"error": {"type": "api_error", "message": "panne simulée"}})
    d = _diag(faux_brevo, mail_from)
    assert _gravites(d).get(code) == "bloquant", d["alertes"]
    assert "500" in _codes(d)[code]["message"] or "panne" in _codes(d)[code]["message"]


@pytest.mark.parametrize("service", ["stripe", "brevo"])
def test_un_service_injoignable_donne_une_alerte_pas_une_exception(
        faux_stripe, faux_brevo, reseau_ferme, service):
    """La garde réseau REFUSE la connexion : c'est exactement ce que fait un
    hôte éteint ou une politique réseau."""
    mail_from = compte_juste(faux_stripe, faux_brevo)
    extra = {}
    if service == "brevo":
        extra["brevo_api_base"] = "http://127.0.0.1:9"
    else:
        stripe.api_base = "http://127.0.0.1:9"
    d = _diag(faux_brevo, mail_from, **extra)
    code = "stripe_compte_illisible" if service == "stripe" else "brevo_compte_illisible"
    assert _gravites(d).get(code) == "bloquant", d["alertes"]


@pytest.mark.parametrize("service,lent", [("stripe", "GET /v1/account"), ("brevo", "GET /v3/account")],
                         ids=["stripe", "brevo"])
def test_un_service_lent_est_abandonne_dans_le_delai(faux_stripe, faux_brevo, service, lent):
    """1,5 s de réponse, 0,3 s de délai : l'alerte sort en moins de 1,2 s.
    Sans délai, le diagnostic attendrait la réponse — et 80 s chez Stripe."""
    mail_from = compte_juste(faux_stripe, faux_brevo)
    (faux_stripe if service == "stripe" else faux_brevo).lenteurs[lent] = 1.5
    t = time.time()
    d = _diag(faux_brevo, mail_from, delai=0.3)
    duree = time.time() - t
    code = "stripe_compte_illisible" if service == "stripe" else "brevo_compte_illisible"
    assert code in _codes(d), "aucune alerte après %.2f s : %s" % (duree, d["alertes"])
    assert duree < 1.2, "le délai de 0,3 s n'a pas été appliqué : %.2f s" % duree


def test_le_delai_par_defaut_ne_depasse_pas_huit_secondes(faux_stripe, faux_brevo, monkeypatch):
    """Ce que reçoivent RÉELLEMENT le client HTTP de Stripe et `session.get`
    quand la configuration ne dit rien : un délai, et jamais plus de 8 s."""
    mail_from = compte_juste(faux_stripe, faux_brevo)
    pret = _stripe_pret()          # le client de CAISSE (15 s) est créé ici, pas mesuré
    delais = []

    class Espion(stripe.RequestsClient):
        def __init__(self, timeout=80, **kw):
            delais.append(("stripe", timeout))
            super(Espion, self).__init__(timeout=timeout, **kw)

    class Session(requests.Session):
        def get(self, url, **kw):
            delais.append(("brevo", kw.get("timeout")))
            return super(Session, self).get(url, **kw)
    monkeypatch.setattr(stripe, "RequestsClient", Espion)
    connexions.diagnostic(stripe=pret, session=Session(),
                          config=_config(faux_brevo, mail_from))
    assert connexions.DELAI <= 8
    assert {s for s, _ in delais} == {"stripe", "brevo"}, delais
    assert all(t is not None and 0 < t <= 8 for _, t in delais), delais


@pytest.mark.parametrize("base", ["absente", "sans_tables"])
def test_une_base_absente_ou_sans_journal_est_toleree(faux_stripe, faux_brevo, base):
    mail_from = compte_juste(faux_stripe, faux_brevo)

    def sans_table(sql, params=()):
        raise sqlite3.OperationalError("no such table")
    d = _diag(faux_brevo, mail_from, base=None if base == "absente" else sans_table)
    assert d["alertes"] == [], d["alertes"]
    assert d["stripe"]["dernier_evenement"]["disponible"] is False
    assert d["brevo"]["journal_24h"]["disponible"] is False
    assert d["brevo"]["envois_non_routables"] is None


def test_sans_module_stripe_le_diagnostic_le_dit_et_ne_l_appelle_pas(faux_stripe, faux_brevo):
    mail_from = compte_juste(faux_stripe, faux_brevo)
    d = _diag(faux_brevo, mail_from, stripe_pret=False)
    assert _gravites(d).get("stripe_non_configure") == "bloquant", d["alertes"]
    assert d["stripe"]["cle_presente"] is False
    assert faux_stripe.recues() == [], "Stripe a été appelé sans clé : %s" % faux_stripe.recues()


@pytest.mark.parametrize("envoi,racine", [
    ("https://api.brevo.com/v3/smtp/email", "https://api.brevo.com"),
    ("http://127.0.0.1:9/v3/smtp/email", "http://127.0.0.1:9"),
    ("https://api.brevo.com/v3/", "https://api.brevo.com"),
    ("https://api.brevo.com", "https://api.brevo.com"),
    ("", "https://api.brevo.com"),
], ids=["envoi", "faux_serveur", "v3", "racine", "vide"])
def test_la_racine_de_l_api_brevo_est_derivee_de_l_adresse_d_envoi(envoi, racine):
    """app.py ne connaît que l'adresse d'ENVOI ; la lecture du compte doit la
    suivre — jusqu'au faux serveur de recette — sans recopier une adresse."""
    assert connexions.base_brevo(envoi) == racine


def test_sans_cle_brevo_le_diagnostic_le_dit_et_ne_l_appelle_pas(faux_stripe, faux_brevo):
    mail_from = compte_juste(faux_stripe, faux_brevo)
    d = _diag(faux_brevo, mail_from, brevo_api_key="")
    assert _gravites(d).get("brevo_non_configure") == "bloquant", d["alertes"]
    assert d["brevo"]["cle_presente"] is False
    assert faux_brevo.recues() == [], faux_brevo.recues()


# ══════════════════════════════════════════════════════════════════════════
#  4. AUCUN SECRET NE SORT
# ══════════════════════════════════════════════════════════════════════════

def test_aucune_cle_ne_figure_dans_le_rapport(faux_stripe, faux_brevo):
    mail_from = compte_reel(faux_stripe, faux_brevo)
    texte = json.dumps(_diag(faux_brevo, mail_from, base=_journal_reel()), ensure_ascii=False)
    for s in SECRETS:
        assert s not in texte, "un secret est dans le rapport : %s" % s
    d = json.loads(texte)
    assert d["stripe"]["cle_presente"] is True and d["brevo"]["cle_presente"] is True


def test_une_cle_mal_copiee_n_est_pas_recopiee_dans_l_alerte(faux_stripe, faux_brevo):
    """Une clé collée avec un retour à la ligne (le piège classique d'une
    variable Render) : `requests` refuse l'en-tête et CITE sa valeur dans
    l'exception. L'alerte doit la masquer."""
    mail_from = compte_juste(faux_stripe, faux_brevo)
    d = _diag(faux_brevo, mail_from, brevo_api_key="xkeysib-recette-locale\n")
    assert "brevo_compte_illisible" in _codes(d), d["alertes"]
    texte = json.dumps(d, ensure_ascii=False)
    assert "xkeysib-recette-locale" not in texte, texte


# ══════════════════════════════════════════════════════════════════════════
#  5. LA ROUTE D'ADMINISTRATION
# ══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def admin():
    c = A.app.test_client()
    with c.session_transaction() as s:
        s["is_conseilprev"] = True
    return c


@pytest.fixture
def service_regle(monkeypatch, faux_stripe, faux_brevo):
    """La configuration du service telle que la route la lit : adresse du site
    (la source des liens des courriers), prix, expéditeur."""
    monkeypatch.setattr(A.seo, "BASE", ICI_SITE)
    monkeypatch.setenv("STRIPE_PRICE_PRO", "price_pro")
    monkeypatch.setenv("STRIPE_PRICE_ENTREPRISE", "price_entreprise")
    monkeypatch.delattr(A, "STRIPE_EVENEMENTS_REQUIS", raising=False)

    def regler(mail_from):
        monkeypatch.setattr(A, "MAIL_FROM", mail_from)
    return regler


def test_un_anonyme_recoit_403_sans_qu_aucun_compte_soit_interroge(faux_stripe, faux_brevo):
    r = A.app.test_client().get("/api/admin/connexions")
    assert r.status_code == 403, (r.status_code, r.get_data(as_text=True)[:200])
    assert faux_stripe.recues() == [] and faux_brevo.recues() == []


@pytest.fixture
def client_ordinaire():
    """UN COMPTE SENTINEL QUI EXISTE VRAIMENT, connecté et NON administrateur.

    CE QUE CETTE RÈGLE MESURAIT EN CROYANT MESURER AUTRE CHOSE. Elle posait
    `client_id = 987654321`, un numéro qu'aucune ligne de `clients` ne porte :
    `sentauth_current_client` ne trouvait personne et rendait None. La règle
    remesurait donc le cas ANONYME, déjà couvert par sa voisine, sous le nom
    du cas « connecté mais pas CONSEILPREV » — celui qui n'était pas mesuré.

    Mutation jouée sur le code corrigé : `admin_session_conseilprev` réduite à
    `if client:`. Elle survivait, et le diagnostic des connexions — adresses
    des points de réception, expéditeurs, état des comptes Stripe et Brevo —
    s'ouvrait à tout compte gratuit connecté.

    Le nom d'entreprise ne doit pas être « CONSEILPREV » : `sentauth_current_
    client` reconnaît l'administrateur à ce nom autant qu'à son adresse."""
    email = "ordinaire_%s@recette.test" % secrets.token_hex(4)
    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO clients (nom_entreprise, email, mot_de_passe_hash, actif, "
                "date_creation, plan, generation_session) VALUES (?,?,?,?,?,?,0)",
                ("RECETTE Compte gratuit", email, "x", 1,
                 datetime.datetime.utcnow().isoformat(), "gratuit"))
    conn.commit()
    cur.execute("SELECT id FROM clients WHERE email=?", (email,))
    cid = dict(cur.fetchone())["id"]
    conn.close()
    c = A.app.test_client()
    with c.session_transaction() as s:
        s["client_id"] = cid
        s["sgen"] = 0
    yield c
    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute("DELETE FROM clients WHERE id=?", (cid,))
    conn.commit(); conn.close()


def test_un_client_connecte_mais_pas_conseilprev_recoit_403(client_ordinaire, faux_stripe, faux_brevo):
    r = client_ordinaire.get("/api/admin/connexions")
    assert r.status_code == 403, (r.status_code, r.get_data(as_text=True)[:200])
    assert faux_stripe.recues() == [] and faux_brevo.recues() == [], (
        "les comptes Stripe et Brevo ont été interrogés pour un compte gratuit")


def test_l_administrateur_voit_le_compte_tel_qu_il_etait(admin, service_regle, faux_stripe, faux_brevo):
    service_regle(compte_reel(faux_stripe, faux_brevo))
    r = admin.get("/api/admin/connexions")
    assert r.status_code == 200, r.get_data(as_text=True)[:300]
    d = r.get_json()
    codes = _gravites(d)
    assert codes.get("stripe_webhook_absent") == "bloquant", d["alertes"]
    assert codes.get("brevo_expediteur_non_verifie") == "bloquant", d["alertes"]
    assert d["stripe"]["point_attendu"] == ATTENDU
    assert d["brevo"]["expediteur"] == connexions.MAIL_FROM_PAR_DEFAUT
    assert d["stripe"]["secret_webhook_present"] is True


def test_aucune_cle_ne_figure_dans_la_reponse(admin, service_regle, faux_stripe, faux_brevo):
    service_regle(compte_reel(faux_stripe, faux_brevo))
    texte = admin.get("/api/admin/connexions").get_data(as_text=True)
    for s in SECRETS:
        assert s not in texte, "un secret est dans la réponse : %s" % s


def _journal_partage_propre():
    """Le journal RÉEL de la base de recette : la table existe, aucune ligne
    vers l'adresse non routable, un événement Stripe reçu à l'instant."""
    A.email_log_init_db()
    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute("DELETE FROM email_log WHERE destinataire LIKE '%@internal.system'")
    cur.execute("CREATE TABLE IF NOT EXISTS stripe_events (event_id TEXT PRIMARY KEY, processed_at TEXT)")
    cur.execute("DELETE FROM stripe_events WHERE event_id='evt_recette_connexions'")
    cur.execute("INSERT INTO stripe_events (event_id, processed_at) VALUES (?, ?)",
                ("evt_recette_connexions", datetime.datetime.utcnow().isoformat()))
    conn.commit(); conn.close()


def test_l_administrateur_voit_tout_branche_quand_le_compte_est_juste(
        admin, service_regle, faux_stripe, faux_brevo):
    service_regle(compte_juste(faux_stripe, faux_brevo))
    _journal_partage_propre()
    try:
        r = admin.get("/api/admin/connexions")
        assert r.status_code == 200
        d = r.get_json()
        assert d["alertes"] == [], d["alertes"]
        assert d["stripe"]["point_actif"] is True
        assert d["stripe"]["dernier_evenement"]["disponible"] is True
        assert 0 <= d["stripe"]["dernier_evenement"]["age_heures"] < 0.1
        assert d["brevo"]["journal_24h"]["disponible"] is True
    finally:
        conn = A.registre_get_db()
        conn.cursor().execute("DELETE FROM stripe_events WHERE event_id='evt_recette_connexions'")
        conn.commit(); conn.close()


def test_sans_cle_stripe_la_route_repond_200_avec_l_alerte(
        admin, service_regle, faux_stripe, faux_brevo, monkeypatch):
    service_regle(compte_juste(faux_stripe, faux_brevo))
    monkeypatch.delenv("STRIPE_SECRET_KEY")
    r = admin.get("/api/admin/connexions")
    assert r.status_code == 200
    assert _gravites(r.get_json()).get("stripe_non_configure") == "bloquant", r.get_json()["alertes"]
    assert faux_stripe.recues() == []


def test_sans_secret_de_signature_la_route_le_dit(
        admin, service_regle, faux_stripe, faux_brevo, monkeypatch):
    """Sans STRIPE_WEBHOOK_SECRET, le point de réception répond 501 à Stripe :
    c'est ce que la route doit lire dans l'environnement, pas supposer."""
    service_regle(compte_juste(faux_stripe, faux_brevo))
    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET")
    d = admin.get("/api/admin/connexions").get_json()
    assert _gravites(d).get("stripe_secret_webhook_absent") == "bloquant", d["alertes"]
    assert d["stripe"]["secret_webhook_present"] is False


def test_un_compte_en_panne_donne_200_et_une_alerte(admin, service_regle, faux_stripe, faux_brevo):
    service_regle(compte_juste(faux_stripe, faux_brevo))
    faux_stripe.pannes["GET /v1/webhook_endpoints"] = (503, {"error": {"message": "maintenance"}})
    faux_brevo.pannes["GET /v3/senders"] = (429, {"code": "too_many_requests"})
    r = admin.get("/api/admin/connexions")
    assert r.status_code == 200, r.get_data(as_text=True)[:300]
    codes = _codes(r.get_json())
    assert {"stripe_webhooks_illisibles", "brevo_expediteurs_illisibles"} <= set(codes), codes


@pytest.mark.parametrize("publie", [True, False])
def test_la_route_lit_les_evenements_requis_publies_par_l_application(
        admin, service_regle, faux_stripe, faux_brevo, monkeypatch, publie):
    """Si un autre lot publie STRIPE_EVENEMENTS_REQUIS, c'est lui qui fait
    foi ; sinon, les trois types traités aujourd'hui."""
    service_regle(compte_juste(faux_stripe, faux_brevo))
    if publie:
        monkeypatch.setattr(A, "STRIPE_EVENEMENTS_REQUIS",
                            EVENEMENTS_REELS + ("checkout.session.async_payment_succeeded",),
                            raising=False)
    d = admin.get("/api/admin/connexions").get_json()
    present = "stripe_webhook_evenements_manquants" in _codes(d)
    assert present is publie, d["alertes"]
    assert d["stripe"]["evenements_requis"][:3] == list(EVENEMENTS_REELS)


def test_une_base_sans_journal_ne_fait_pas_tomber_la_route(
        admin, service_regle, faux_stripe, faux_brevo, monkeypatch):
    service_regle(compte_juste(faux_stripe, faux_brevo))
    # Un premier passage AVANT de remplacer la base : les fils de fond que
    # la première requête du processus démarre ne doivent pas hériter d'une
    # base vide en mémoire.
    assert admin.get("/api/admin/connexions").status_code == 200

    def base_vide():
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        return conn
    monkeypatch.setattr(A, "registre_get_db", base_vide)
    r = admin.get("/api/admin/connexions")
    assert r.status_code == 200, r.get_data(as_text=True)[:300]
    d = r.get_json()
    assert d["brevo"]["journal_24h"]["disponible"] is False
    assert d["stripe"]["dernier_evenement"]["disponible"] is False
    assert d["alertes"] == [], d["alertes"]


def test_la_route_ne_fait_que_lire(admin, service_regle, faux_stripe, faux_brevo):
    service_regle(compte_reel(faux_stripe, faux_brevo))
    admin.get("/api/admin/connexions")
    methodes = {r.methode for r in faux_stripe.recues()} | {r.methode for r in faux_brevo.recues()}
    assert methodes == {"GET"}, methodes
    assert {r.chemin for r in faux_stripe.recues()} == {
        "/v1/account", "/v1/webhook_endpoints", "/v1/prices/price_pro", "/v1/prices/price_entreprise"}
    assert {r.chemin for r in faux_brevo.recues()} == {"/v3/account", "/v3/senders"}


def test_la_route_suit_immediatement_la_sante_email():
    """La fusion avec les autres lots doit rester triviale : la route est
    insérée juste après `email_health`, et nulle part ailleurs."""
    src = io.open(os.path.join(_RACINE, "app.py"), encoding="utf-8").read()
    i = src.index("def email_health(")
    j = src.index("@app.route('/api/admin/connexions'")
    assert i < j, "la route est avant la santé email"
    assert src.count("@app.route(", i, j) == 0, "une autre route sépare les deux"
    assert src.count("/api/admin/connexions") == 1


# ══════════════════════════════════════════════════════════════════════════
#  6. L'OUTIL DE L'EXPLOITANT
# ══════════════════════════════════════════════════════════════════════════

def _outil():
    spec = importlib.util.spec_from_file_location("verifier_connexions", OUTIL)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _environ(faux_brevo, mail_from, **extra):
    env = {"STRIPE_SECRET_KEY": "sk_test_recette_locale",
           "STRIPE_WEBHOOK_SECRET": "whsec_recette_locale",
           "STRIPE_PRICE_PRO": "price_pro", "STRIPE_PRICE_ENTREPRISE": "price_entreprise",
           "SITE_BASE_URL": ICI_SITE, "BREVO_API_KEY": "xkeysib-recette-locale",
           "BREVO_API_BASE": faux_brevo.url, "MAIL_FROM": mail_from}
    env.update(extra)
    return env


def test_l_outil_n_importe_pas_l_application():
    """Importer app.py, c'est démarrer l'application : base, fils de fond,
    référentiels. Un outil de diagnostic ne le fait pas."""
    arbre = ast.parse(io.open(OUTIL, encoding="utf-8").read())
    importes = set()
    for n in ast.walk(arbre):
        if isinstance(n, ast.Import):
            importes |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom):
            importes.add((n.module or "").split(".")[0])
    assert "app" not in importes, importes
    assert "connexions" in importes, "l'outil ne partage pas la logique du module"


def test_l_outil_dit_ce_qui_manque_et_sort_en_1(faux_stripe, faux_brevo):
    mail_from = compte_reel(faux_stripe, faux_brevo)
    lignes = []
    code = _outil().principal(_environ(faux_brevo, mail_from), lignes.append)
    texte = "\n".join(lignes)
    assert code == 1, texte
    assert "✗ Stripe : point de réception actif vers %s" % ATTENDU in texte, texte
    assert "✗ Brevo : expéditeur %s vérifié" % mail_from in texte, texte
    assert "[BLOQUANT] stripe_webhook_absent" in texte, texte
    assert "[BLOQUANT] brevo_expediteur_non_verifie" in texte, texte
    assert "Tout est branché" not in texte


def test_l_outil_dit_tout_est_branche_et_sort_en_0(faux_stripe, faux_brevo):
    mail_from = compte_juste(faux_stripe, faux_brevo)
    lignes = []
    code = _outil().principal(_environ(faux_brevo, mail_from), lignes.append)
    texte = "\n".join(lignes)
    assert code == 0, texte
    assert "✗" not in texte, texte
    assert "✓ Tout est branché." in texte, texte
    assert "– base : DATABASE_URL absente" in texte, "l'outil ne dit pas que la base n'est pas lue"
    assert sum(1 for l in lignes if l[:1] in "✓✗–") >= 10, texte


def test_l_outil_n_imprime_aucune_cle(faux_stripe, faux_brevo):
    mail_from = compte_reel(faux_stripe, faux_brevo)
    lignes = []
    _outil().principal(_environ(faux_brevo, mail_from), lignes.append)
    texte = "\n".join(lignes)
    for s in SECRETS:
        assert s not in texte, "un secret est imprimé : %s" % s
    assert "✓ Stripe : clé présente" in texte and "✓ Brevo : clé présente" in texte


def test_l_outil_ne_fait_que_lire(faux_stripe, faux_brevo):
    mail_from = compte_reel(faux_stripe, faux_brevo)
    _outil().principal(_environ(faux_brevo, mail_from), lambda t: None)
    assert {r.methode for r in faux_stripe.recues() + faux_brevo.recues()} == {"GET"}


def test_l_outil_sans_aucune_variable_ne_leve_pas_et_sort_en_1(reseau_ferme):
    """Lancé à vide : deux alertes bloquantes de configuration, aucun appel
    réseau (la garde le refuserait), code 1."""
    lignes = []
    code = _outil().principal({}, lignes.append)
    texte = "\n".join(lignes)
    assert code == 1
    assert "stripe_non_configure" in texte and "brevo_non_configure" in texte, texte


# ══════════════════════════════════════════════════════════════════════════
#  7. L'ÉCRAN
# ══════════════════════════════════════════════════════════════════════════

def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


def _tranche(debut, src):
    i = src.find(debut)
    assert i >= 0, "%r est introuvable" % debut
    j = src.find("\n};", i) + 3
    return src[i:j]


def _node(harnais):
    if not NODE:
        pytest.skip("node absent : le code de l'écran ne peut pas être exécuté")
    with tempfile.TemporaryDirectory() as d:
        h = os.path.join(d, "h.js")
        io.open(h, "w", encoding="utf-8").write(harnais)
        r = subprocess.run([NODE, h], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail("le scénario n'a pas tourné :\n%s" % (r.stderr or "")[-1500:])
    return json.loads(r.stdout)


def test_l_ecran_a_un_bloc_connexions_a_cote_de_la_sante_email():
    html = _lire("sentinel.html")
    i = html.index('id="email-health-widget"')
    j = html.index('id="connexions-widget"')
    assert 0 < j - i < 600, "le bloc est loin de la santé email (%d caractères)" % (j - i)
    assert "Connexions Stripe et Brevo" in html[i:j + 200]


@pytest.mark.parametrize("cas", ["vide", "alertes", "refus"])
def test_l_ecran_liste_les_alertes_et_dit_tout_est_branche_quand_il_n_y_en_a_pas(cas):
    donnees = {
        "vide": {"status": 200, "data": {"alertes": [], "verifie_le": "2026-09-24T10:00:00+00:00",
                                         "stripe": {"dernier_evenement": {"disponible": True,
                                                                          "recu_le": "2026-09-24T08:00:00+00:00",
                                                                          "age_heures": 2.0}}}},
        "alertes": {"status": 200, "data": {"alertes": [
            {"code": "stripe_webhook_absent", "gravite": "bloquant", "message": "vers <b>x</b>"},
            {"code": "brevo_credits_faibles", "gravite": "important", "message": "49 crédits"},
            {"code": "stripe_webhook_version_api", "gravite": "info", "message": "version"}],
            "verifie_le": "2026-09-24T10:00:00+00:00",
            "stripe": {"dernier_evenement": {"disponible": True, "recu_le": None}}}},
        "refus": {"status": 403, "data": {"error": "Acces reserve"}},
    }[cas]
    o = _node("""
      global.window = global;
      var requetes = [], zones = { 'connexions-widget': { innerHTML: '' } };
      global.document = { getElementById: function(id){ return zones[id] || null; } };
      global.fetch = function(u){ requetes.push(String(u)); return Promise.resolve({
        status: %d, json: function(){ return Promise.resolve(%s); } }); };
    """ % (donnees["status"], json.dumps(donnees["data"])) + _tranche(
        "window.connexionsRender = function(){", _lire("sentinel.page.js")) + """
      window.connexionsRender();
      setTimeout(function(){ process.stdout.write(JSON.stringify({
        requetes: requetes, html: zones['connexions-widget'].innerHTML })); }, 30);
    """)
    assert o["requetes"] == ["/api/admin/connexions"], o
    html = o["html"]
    if cas == "vide":
        assert "Tout est branché" in html and "radar-registre-ok" in html, html
        assert "il y a 2 h" in html, html
    elif cas == "alertes":
        assert "Tout est branché" not in html, html
        assert "stripe_webhook_absent" in html and "brevo_credits_faibles" in html, html
        assert "radar-registre-warn" in html, "l'alerte importante n'a pas la classe existante"
        assert "&lt;b&gt;x&lt;/b&gt;" in html and "<b>x</b>" not in html, "message non échappé"
        assert "jamais" in html, "le dernier événement absent n'est pas dit"
    else:
        assert "Erreur serveur" in html and "Tout est branché" not in html, html


def test_l_ecran_charge_le_diagnostic_avec_la_sante_email():
    o = _node("""
      global.window = global;
      var appels = [];
      global.sentAuthMoi = function(){ return Promise.resolve({authenticated: true, is_conseilprev: true}); };
      global.document = { getElementById: function(){ return { style: {} }; } };
      window.clientsRenderList = function(){ appels.push('clientsRenderList'); };
      window.emailHealthRender = function(){ appels.push('emailHealthRender'); };
      window.connexionsRender = function(){ appels.push('connexionsRender'); };
      window.infraStatusRender = function(){ appels.push('infraStatusRender'); };
    """ + _tranche("window.clientsInitPage = function(){", _lire("sentinel.page.js")) + """
      window.clientsInitPage();
      setTimeout(function(){ process.stdout.write(JSON.stringify(appels)); }, 30);
    """)
    assert "connexionsRender" in o, o
    assert o.index("connexionsRender") == o.index("emailHealthRender") + 1, o
