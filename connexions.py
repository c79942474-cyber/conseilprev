# -*- coding: utf-8 -*-
"""Stripe et Brevo sont-ils VRAIMENT branchés sur CE service ? Mesuré, pas supposé.

CE QUI S'EST PASSÉ, ET QUE RIEN NE MESURAIT. Pendant un mois, le seul point de
réception Stripe du compte visait `https://conseilprev.onrender.com/api/stripe/
webhook` — un hôte sans service, le site vivant sur `conseilprevia.onrender.com`.
Chaque paiement partait, chaque notification tombait dans le vide, et aucune
page ne cessait de s'afficher. Côté Brevo, l'expéditeur par défaut du code
(`noreply@conseilprev.onrender.com`) n'est pas un expéditeur vérifié du compte,
et six envois sur treize visaient `conseilprev@internal.system`, une adresse
qui n'existe pas : le crédit est décompté, le message rebondit.

Aucun de ces défauts n'est dans le code : ils sont dans l'ÉCART entre le code
et les comptes. C'est cet écart que ce module mesure, en interrogeant les deux
comptes avec ce que le service a réellement en configuration.

CE QUE CE MODULE REFUSE.
  · Aucune clé, aucun fragment de clé dans le résultat : des booléens
    (`cle_presente`, `secret_webhook_present`), et les messages d'erreur sont
    passés au masque avant d'être rendus.
  · Aucune exception qui remonte : un service en panne, lent ou mal configuré
    est une ALERTE, pas un 500. Chaque appel sortant porte un délai, `DELAI`
    secondes au plus.
  · Aucune écriture : que des GET, chez Stripe comme chez Brevo, et des SELECT
    dans la base. L'outil `outils/verifier_connexions.py` peut donc être lancé
    par l'exploitant sur un compte en production sans rien y changer.

CE MODULE N'IMPORTE PAS `app` : il reçoit le module `stripe` déjà réglé, une
`requests.Session`, une configuration en clair et, s'il y en a une, une
fonction de lecture de la base. C'est ce qui le rend appelable depuis la route
d'administration comme depuis un outil en ligne de commande qui ne doit pas
démarrer l'application.
"""
import datetime
import re

#: Délai par appel sortant, en secondes. Quatre appels Stripe et deux Brevo
#: au plus : un diagnostic ne doit jamais tenir une requête de navigateur
#: au-delà de ce que l'exploitant accepte d'attendre.
DELAI = 8

#: Le chemin du point de réception Stripe de ce service, tel que la route
#: `/api/stripe/webhook` d'app.py l'expose.
CHEMIN_WEBHOOK = "/api/stripe/webhook"

#: Les types d'événements que le point de réception TRAITE aujourd'hui
#: (app.py, branches de `stripe_webhook`). Repli si l'application ne publie
#: pas `STRIPE_EVENEMENTS_REQUIS`.
EVENEMENTS_TRAITES = ("checkout.session.completed", "invoice.paid",
                      "invoice.payment_failed")

#: Sous ce nombre de crédits Brevo restants, une journée de relances suffit à
#: couper les courriels de confirmation d'inscription.
CREDITS_BREVO_MINIMUM = 50

#: L'expéditeur par défaut d'app.py quand `MAIL_FROM` n'est pas défini. Il
#: n'est vérifié chez Brevo ni ne le sera : c'est un nom d'hôte Render.
MAIL_FROM_PAR_DEFAUT = "noreply@conseilprev.onrender.com"

#: Le domaine de l'adresse interne non routable (app.py,
#: CONSEILPREV_INTERNAL_EMAIL). Un envoi vers lui coûte un crédit et rebondit.
DOMAINE_NON_ROUTABLE = "@internal.system"

#: Adresse d'API Brevo par défaut, pour l'outil qui n'importe pas app.py.
BREVO_API_BASE_PAR_DEFAUT = "https://api.brevo.com"

GRAVITES = ("bloquant", "important", "info")


def base_brevo(url):
    """L'adresse racine de l'API Brevo, DÉRIVÉE de l'adresse d'envoi.

    app.py ne connaît que `BREVO_API_URL` = `https://api.brevo.com/v3/smtp/
    email`. On en retire le suffixe d'envoi, puis `/v3`, pour obtenir la
    racine sur laquelle `/v3/account` et `/v3/senders` se greffent. Dériver
    plutôt que recopier `https://api.brevo.com` : en recette, l'adresse
    d'envoi est redirigée vers un faux serveur local, et les lectures de
    compte doivent le suivre.
    """
    u = str(url or "").strip().rstrip("/")
    for suffixe in ("/smtp/email", "/v3"):
        if u.endswith(suffixe):
            u = u[:-len(suffixe)]
    return u or BREVO_API_BASE_PAR_DEFAUT


def _champ(objet, nom, defaut=None):
    """Un champ d'un `StripeObject` ou d'un dict. En 15.x, `StripeObject`
    n'est PAS un dict et n'a pas de `.get()` : on lit par index."""
    try:
        v = objet[nom]
    except (KeyError, TypeError, AttributeError, IndexError):
        try:
            v = getattr(objet, nom)
        except AttributeError:
            return defaut
    return defaut if v is None else v


def _maintenant():
    return datetime.datetime.now(datetime.timezone.utc)


def _lire_horodatage(texte):
    """Un horodatage ISO écrit par app.py (`datetime.utcnow().isoformat()`,
    donc naïf et en UTC), ou None si illisible."""
    if not texte:
        return None
    try:
        d = datetime.datetime.fromisoformat(str(texte).replace("Z", "+00:00"))
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=datetime.timezone.utc)
    return d


class _Rapport(object):
    """Les alertes, et le masque qui interdit à un secret d'y entrer."""

    def __init__(self, secrets):
        self.alertes = []
        # Le secret tel quel ET débarrassé de ses blancs : une clé collée avec
        # un retour à la ligne est refusée par la couche HTTP, qui la CITE
        # dans son message — sous forme échappée, où le retour à la ligne
        # n'est plus un retour à la ligne.
        self.secrets = sorted({v for s in secrets if isinstance(s, str)
                               for v in (s, s.strip()) if len(v) >= 8},
                              key=len, reverse=True)

    def masquer(self, texte):
        t = str(texte)
        for s in self.secrets:
            t = t.replace(s, "***")
        return t

    def erreur(self, exc):
        """« NomDeLException : message », sur une ligne, borné, masqué. Les
        messages de la bibliothèque Stripe font plusieurs lignes et invitent
        à écrire au support : on garde l'essentiel."""
        message = re.sub(r"\s+", " ", str(exc)).strip()
        return self.masquer("%s : %s" % (type(exc).__name__, message[:160]))

    def alerte(self, code, gravite, message):
        assert gravite in GRAVITES, gravite
        self.alertes.append({"code": code, "gravite": gravite,
                             "message": self.masquer(message)})


# ══════════════════════════════════════════════════════════════════════════
#  STRIPE
# ══════════════════════════════════════════════════════════════════════════

def _client_stripe(stripe, delai):
    """Un client Stripe PROPRE AU DIAGNOSTIC : même clé, même adresse d'API
    que le module reçu, mais son propre transport.

    POURQUOI NE PAS APPELER `stripe.Account.retrieve()` DIRECTEMENT. Le
    transport du module est réglé par `_stripe_pret()` d'app.py pour les
    caisses : quinze secondes et deux réessais, ce qui est juste pour un
    paiement. Un diagnostic, lui, MESURE : il ne réessaie pas, et il ne doit
    pas tenir une requête de navigateur seize secondes par contrôle. On ne
    touche pas aux réglages partagés du module — c'était précisément le
    défaut des cinq `max_network_retries = 0` — on construit un client à
    côté.
    """
    return stripe.StripeClient(
        stripe.api_key,
        base_addresses={"api": stripe.api_base},
        http_client=stripe.RequestsClient(timeout=delai),
        max_network_retries=0)


def _diagnostic_stripe(stripe, config, base, rapport, delai):
    attendu = str(config.get("site_base_url") or "").rstrip("/") + CHEMIN_WEBHOOK
    requis = tuple(config.get("stripe_evenements_requis") or EVENEMENTS_TRAITES)
    res = {
        "cle_presente": bool(stripe is not None and getattr(stripe, "api_key", None)),
        "secret_webhook_present": bool(config.get("stripe_webhook_secret_present")),
        "version_api_bibliotheque": getattr(stripe, "api_version", None),
        "compte": None,
        "point_attendu": attendu,
        "points": [],
        "point_actif": False,
        "evenements_requis": list(requis),
        "evenements_manquants": [],
        "autres_points": [],
        "dernier_evenement": {"disponible": False, "recu_le": None, "age_heures": None},
        "prix": {},
    }
    if not res["secret_webhook_present"]:
        rapport.alerte("stripe_secret_webhook_absent", "bloquant",
                       "STRIPE_WEBHOOK_SECRET absente : le point de réception "
                       "répond 501 à toute notification, aucun paiement ne peut "
                       "être confirmé.")
    _dernier_evenement_stripe(base, res)
    if not res["cle_presente"]:
        rapport.alerte("stripe_non_configure", "bloquant",
                       "STRIPE_SECRET_KEY absente : aucune caisse ne peut ouvrir "
                       "et le compte ne peut pas être vérifié.")
        return res
    try:
        client = _client_stripe(stripe, delai)
    except Exception as e:                                    # noqa: BLE001
        rapport.alerte("stripe_compte_illisible", "bloquant",
                       "Client Stripe impossible à construire : " + rapport.erreur(e))
        return res
    _compte_stripe(client, res, rapport)
    _points_de_reception(client, res, rapport, attendu, requis,
                         res["version_api_bibliotheque"])
    _prix_stripe(client, config, res, rapport)
    return res


def _compte_stripe(client, res, rapport):
    try:
        compte = client.v1.accounts.retrieve_current()
    except Exception as e:                                    # noqa: BLE001
        rapport.alerte("stripe_compte_illisible", "bloquant",
                       "Le compte Stripe ne répond pas : " + rapport.erreur(e))
        return
    livemode = bool(_champ(compte, "livemode", False))
    encaisse = bool(_champ(compte, "charges_enabled", False))
    res["compte"] = {"id": _champ(compte, "id"), "livemode": livemode,
                     "charges_enabled": encaisse}
    if not encaisse:
        rapport.alerte("stripe_encaissement_desactive", "bloquant",
                       "Le compte Stripe %s ne peut pas encaisser "
                       "(charges_enabled=false) : activation ou vérification "
                       "à terminer dans le tableau de bord Stripe."
                       % _champ(compte, "id", "?"))
    if not livemode:
        rapport.alerte("stripe_mode_test", "info",
                       "La clé Stripe est une clé de TEST (livemode=false) : "
                       "aucun paiement réel ne sera encaissé.")


def _points_de_reception(client, res, rapport, attendu, requis, version_bibliotheque):
    """LE CONTRÔLE QUI MANQUAIT PENDANT UN MOIS : existe-t-il, chez Stripe, un
    point de réception ACTIF dont l'adresse est EXACTEMENT celle de ce
    service ? Un point vers un autre hôte est listé — c'est ce qui permet de
    voir, dans le message, où partaient les notifications."""
    try:
        points = list(client.v1.webhook_endpoints.list({"limit": 100}).data)
    except Exception as e:                                    # noqa: BLE001
        rapport.alerte("stripe_webhooks_illisibles", "bloquant",
                       "Les points de réception Stripe ne peuvent pas être lus : "
                       + rapport.erreur(e))
        return
    lus = []
    for p in points:
        lus.append({"id": _champ(p, "id"), "url": _champ(p, "url", ""),
                    "status": _champ(p, "status", ""),
                    "enabled_events": list(_champ(p, "enabled_events", []) or []),
                    "api_version": _champ(p, "api_version")})
    res["points"] = lus
    notres = [p for p in lus if p["url"] == attendu]
    actifs = [p for p in notres if p["status"] == "enabled"]
    res["autres_points"] = [p["url"] for p in lus if p["url"] != attendu]
    if not actifs:
        trouvees = ", ".join(
            "%s (%s)" % (p["url"], p["status"] or "?") for p in lus) or "aucun"
        rapport.alerte("stripe_webhook_absent", "bloquant",
                       "Aucun point de réception Stripe ACTIF vers %s : les "
                       "paiements partent, aucune confirmation n'arrive. Points "
                       "du compte : %s." % (attendu, trouvees))
    else:
        res["point_actif"] = True
        point = actifs[0]
        couverts = set(point["enabled_events"])
        manquants = [] if "*" in couverts else [e for e in requis if e not in couverts]
        res["evenements_manquants"] = manquants
        if manquants:
            rapport.alerte("stripe_webhook_evenements_manquants", "important",
                           "Le point de réception %s n'est pas abonné à : %s. "
                           "Ces événements ne seront jamais reçus."
                           % (attendu, ", ".join(manquants)))
        if (point["api_version"] and version_bibliotheque
                and point["api_version"] != version_bibliotheque):
            rapport.alerte("stripe_webhook_version_api", "info",
                           "Le point de réception envoie des événements en version "
                           "%s, la bibliothèque du service parle en %s."
                           % (point["api_version"], version_bibliotheque))
    if res["autres_points"]:
        rapport.alerte("stripe_webhook_autres_points", "info",
                       "Autres points de réception sur le même compte Stripe : %s."
                       % ", ".join(res["autres_points"]))


def _prix_stripe(client, config, res, rapport):
    """STRIPE_PRICE_PRO et STRIPE_PRICE_ENTREPRISE ouvrent la caisse
    d'abonnement (`mode=subscription`) : un prix inactif ou ponctuel y fait
    échouer toute souscription, en 502, sans message pour le client."""
    prix = config.get("stripe_prix") or {}
    for nom in ("pro", "entreprise"):
        pid = str(prix.get(nom) or "").strip()
        etat = {"id": pid or None, "actif": None, "recurrent": None}
        res["prix"][nom] = etat
        if not pid:
            rapport.alerte("stripe_prix_absent", "important",
                           "STRIPE_PRICE_%s absente : l'offre %s ne peut pas "
                           "être souscrite (la caisse répond 501)."
                           % (nom.upper(), nom))
            continue
        try:
            p = client.v1.prices.retrieve(pid)
        except Exception as e:                                # noqa: BLE001
            rapport.alerte("stripe_prix_illisible", "important",
                           "Le prix %s (%s) ne peut pas être lu : %s"
                           % (pid, nom, rapport.erreur(e)))
            continue
        etat["actif"] = bool(_champ(p, "active", False))
        etat["recurrent"] = _champ(p, "recurring") is not None
        if not etat["actif"]:
            rapport.alerte("stripe_prix_inactif", "important",
                           "Le prix %s de l'offre %s est archivé (active=false) : "
                           "Stripe refusera la souscription." % (pid, nom))
        if not etat["recurrent"]:
            rapport.alerte("stripe_prix_non_recurrent", "important",
                           "Le prix %s de l'offre %s est ponctuel, pas récurrent : "
                           "une caisse en mode abonnement le refuse." % (pid, nom))


def _dernier_evenement_stripe(base, res):
    """Quand la dernière notification Stripe est-elle arrivée ? C'est la
    mesure directe de « le point de réception vise ce service ». Table
    absente, base injoignable : `disponible` reste faux, sans alerte — ce
    n'est pas un défaut de branchement."""
    if base is None:
        return
    try:
        lignes = base("SELECT MAX(processed_at) AS dernier FROM stripe_events")
    except Exception:                                         # noqa: BLE001
        return
    res["dernier_evenement"]["disponible"] = True
    dernier = lignes[0]["dernier"] if lignes else None
    d = _lire_horodatage(dernier)
    if d is not None:
        res["dernier_evenement"]["recu_le"] = d.isoformat()
        res["dernier_evenement"]["age_heures"] = round(
            (_maintenant() - d).total_seconds() / 3600.0, 1)


# ══════════════════════════════════════════════════════════════════════════
#  BREVO
# ══════════════════════════════════════════════════════════════════════════

def _diagnostic_brevo(session, config, base, rapport, delai):
    cle = str(config.get("brevo_api_key") or "")
    racine = base_brevo(config.get("brevo_api_base") or BREVO_API_BASE_PAR_DEFAUT)
    mail_from = str(config.get("mail_from") or MAIL_FROM_PAR_DEFAUT).strip()
    res = {
        "cle_presente": bool(cle),
        "base_api": racine,
        "expediteur": mail_from,
        "compte": None,
        "expediteurs_actifs": [],
        "expediteur_verifie": False,
        "journal_24h": {"disponible": False, "ok": None, "echecs": None,
                        "derniere_erreur": None},
        "envois_non_routables": None,
    }
    _journal_brevo(base, res, rapport)
    if not cle:
        rapport.alerte("brevo_non_configure", "bloquant",
                       "BREVO_API_KEY absente : aucun courriel ne part par l'API, "
                       "et le compte ne peut pas être vérifié.")
        return res
    if session is None:
        rapport.alerte("brevo_compte_illisible", "bloquant",
                       "Aucune session HTTP fournie : le compte Brevo n'a pas "
                       "été interrogé.")
        return res
    entetes = {"api-key": cle, "Accept": "application/json"}
    _compte_brevo(session, racine, entetes, res, rapport, delai)
    _expediteurs_brevo(session, racine, entetes, res, rapport, delai, mail_from)
    return res


def _get_brevo(session, url, entetes, delai):
    """Un GET, un délai, et une réponse JSON — ou une exception à capturer.
    Le corps d'une réponse en erreur n'est JAMAIS recopié dans une alerte :
    seul le statut l'est."""
    r = session.get(url, headers=entetes, timeout=delai)
    if r.status_code != 200:
        raise RuntimeError("HTTP %d sur %s" % (r.status_code, url))
    return r.json()


def _compte_brevo(session, racine, entetes, res, rapport, delai):
    try:
        compte = _get_brevo(session, racine + "/v3/account", entetes, delai)
    except Exception as e:                                    # noqa: BLE001
        rapport.alerte("brevo_compte_illisible", "bloquant",
                       "Le compte Brevo ne répond pas : " + rapport.erreur(e))
        return
    plans = compte.get("plan") or [] if isinstance(compte, dict) else []
    credits = None
    types = []
    for p in plans:
        if not isinstance(p, dict):
            continue
        types.append(str(p.get("type") or "?"))
        if p.get("creditsType") == "sendLimit" and isinstance(p.get("credits"), (int, float)):
            credits = int(p["credits"])
    res["compte"] = {"plan": types, "credits": credits}
    if credits is not None and credits < CREDITS_BREVO_MINIMUM:
        rapport.alerte("brevo_credits_faibles", "important",
                       "Il reste %d crédits d'envoi Brevo (seuil : %d) : les "
                       "confirmations d'inscription vont bientôt tomber."
                       % (credits, CREDITS_BREVO_MINIMUM))


def _expediteurs_brevo(session, racine, entetes, res, rapport, delai, mail_from):
    """LE CONTRÔLE QUE LA GARDE D'app.py NE FAIT PAS : MAIL_FROM est-il un
    expéditeur VÉRIFIÉ du compte ? Sinon Brevo refuse chaque envoi (« sender
    not valid ») et le courriel finit en fichier de repli sur le disque."""
    try:
        reponse = _get_brevo(session, racine + "/v3/senders", entetes, delai)
    except Exception as e:                                    # noqa: BLE001
        rapport.alerte("brevo_expediteurs_illisibles", "bloquant",
                       "Les expéditeurs Brevo ne peuvent pas être lus : "
                       + rapport.erreur(e))
        return
    expediteurs = reponse.get("senders") or [] if isinstance(reponse, dict) else []
    actifs = [str(s.get("email") or "") for s in expediteurs
              if isinstance(s, dict) and s.get("active") and s.get("email")]
    res["expediteurs_actifs"] = actifs
    res["expediteur_verifie"] = mail_from.lower() in {a.lower() for a in actifs}
    if not res["expediteur_verifie"]:
        rapport.alerte("brevo_expediteur_non_verifie", "bloquant",
                       "MAIL_FROM = %s n'est pas un expéditeur vérifié du compte "
                       "Brevo : chaque envoi sera refusé. Expéditeurs actifs : %s."
                       % (mail_from, ", ".join(actifs) or "aucun"))


def _journal_brevo(base, res, rapport):
    """Ce que le journal `email_log` dit des 24 dernières heures, et le
    nombre d'envois vers l'adresse non routable. Table absente ou base
    injoignable : `disponible` reste faux, sans alerte."""
    if base is None:
        return
    depuis = (datetime.datetime.utcnow() - datetime.timedelta(hours=24)).isoformat()
    try:
        comptes = base("SELECT succes, COUNT(*) AS n FROM email_log "
                       "WHERE date_envoi > ? GROUP BY succes", (depuis,))
        derniere = base("SELECT raison_echec, methode, date_envoi FROM email_log "
                        "WHERE NOT succes AND date_envoi > ? "
                        "ORDER BY date_envoi DESC LIMIT 1", (depuis,))
        non_routables = base("SELECT COUNT(*) AS n FROM email_log "
                             "WHERE destinataire LIKE ?", ("%" + DOMAINE_NON_ROUTABLE,))
    except Exception:                                         # noqa: BLE001
        return
    ok = echecs = 0
    for ligne in comptes:
        if ligne["succes"] in (True, 1):
            ok += int(ligne["n"])
        else:
            echecs += int(ligne["n"])
    journal = res["journal_24h"]
    journal.update({"disponible": True, "ok": ok, "echecs": echecs})
    if derniere:
        d = derniere[0]
        journal["derniere_erreur"] = {"raison": d["raison_echec"], "methode": d["methode"],
                                      "date": d["date_envoi"]}
    n = int(non_routables[0]["n"]) if non_routables else 0
    res["envois_non_routables"] = n
    if n > 0:
        rapport.alerte("brevo_envois_non_routables", "important",
                       "%d envoi(s) du journal visent une adresse %s : le crédit "
                       "est décompté et le message rebondit, personne ne le lit."
                       % (n, DOMAINE_NON_ROUTABLE))


# ══════════════════════════════════════════════════════════════════════════
#  LE DIAGNOSTIC
# ══════════════════════════════════════════════════════════════════════════

def diagnostic(stripe=None, session=None, config=None, base=None):
    """Le rapport : {"stripe", "brevo", "alertes", "verifie_le"}.

    `stripe`  : le module `stripe` déjà réglé (clé posée), ou None si la clé
                manque — l'alerte `stripe_non_configure` le dit.
    `session` : une `requests.Session` pour Brevo.
    `config`  : site_base_url, stripe_webhook_secret_present,
                stripe_evenements_requis, stripe_prix {pro, entreprise},
                brevo_api_key, brevo_api_base, mail_from, delai.
    `base`    : `base(sql, params=()) -> [dict]`, placeholders `?`, lecture
                seule ; None si aucune base n'est accessible.

    Ne lève JAMAIS : chaque défaillance devient une alerte, avec son code,
    sa gravité (bloquant, important, info) et un message sans secret.
    """
    config = dict(config or {})
    delai = float(config.get("delai") or DELAI)
    rapport = _Rapport([config.get("brevo_api_key"),
                        getattr(stripe, "api_key", None) if stripe is not None else None])
    resultat = {"stripe": {}, "brevo": {}, "alertes": rapport.alertes,
                "verifie_le": _maintenant().replace(microsecond=0).isoformat()}
    try:
        resultat["stripe"] = _diagnostic_stripe(stripe, config, base, rapport, delai)
    except Exception as e:                                    # noqa: BLE001
        rapport.alerte("stripe_diagnostic_interrompu", "bloquant",
                       "Le diagnostic Stripe s'est interrompu : " + rapport.erreur(e))
    try:
        resultat["brevo"] = _diagnostic_brevo(session, config, base, rapport, delai)
    except Exception as e:                                    # noqa: BLE001
        rapport.alerte("brevo_diagnostic_interrompu", "bloquant",
                       "Le diagnostic Brevo s'est interrompu : " + rapport.erreur(e))
    return resultat


def bloquant(resultat):
    """Y a-t-il au moins une alerte bloquante ? C'est le code de sortie de
    l'outil en ligne de commande."""
    return any(a.get("gravite") == "bloquant" for a in resultat.get("alertes", []))
