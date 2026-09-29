#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stripe et Brevo sont-ils branchés sur CE service ? — l'outil de l'exploitant.

À LANCER SUR SA MACHINE OU DANS UN SHELL RENDER, avec les variables
d'environnement du service :

    python3 outils/verifier_connexions.py

Il lit STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, STRIPE_PRICE_PRO,
STRIPE_PRICE_ENTREPRISE, SITE_BASE_URL (ou BASE_URL), BREVO_API_KEY, MAIL_FROM,
BREVO_API_BASE (facultative) et DATABASE_URL (facultative : sans elle, le
journal et le dernier événement reçu ne sont pas lus). Il interroge les DEUX
comptes en LECTURE SEULE — des GET chez Stripe et Brevo, des SELECT en base —,
imprime une ligne par contrôle (✓ ou ✗, « – » quand rien n'a pu être lu), puis
les alertes, et sort avec le code 1 s'il y en a une bloquante. Il n'imprime
AUCUNE clé.

POURQUOI IL N'IMPORTE PAS app.py. Importer l'application, c'est la démarrer :
ouvrir la base, lancer les fils de fond, lire tous les référentiels. Un outil
de diagnostic qui met vingt secondes à commencer et laisse des fils derrière
lui n'est pas un outil qu'on lance. La logique est dans `connexions.py`, qui
n'importe rien de l'application ; c'est lui qui est éprouvé par la recette
avec de faux serveurs — cet outil-ci n'ajoute que la lecture de
l'environnement et la mise en forme.
"""
import io
import os
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)
import connexions                                                   # noqa: E402

COCHE, CROIX, TIRET = "✓", "✗", "–"


def configuration(environ):
    """(secret Stripe, config du diagnostic) depuis l'environnement — sans
    jamais recopier un secret ailleurs que dans la config qui l'appelle."""
    lire = lambda nom: str(environ.get(nom) or "").strip()             # noqa: E731
    site = (lire("SITE_BASE_URL") or lire("BASE_URL")
            or "https://conseilprev.onrender.com")
    if "://" not in site:
        site = "https://" + site
    config = {
        "site_base_url": site,
        "stripe_webhook_secret_present": bool(lire("STRIPE_WEBHOOK_SECRET")),
        "stripe_evenements_requis": connexions.EVENEMENTS_TRAITES,
        "stripe_prix": {"pro": lire("STRIPE_PRICE_PRO"),
                        "entreprise": lire("STRIPE_PRICE_ENTREPRISE")},
        "brevo_api_key": lire("BREVO_API_KEY"),
        "brevo_api_base": lire("BREVO_API_BASE") or connexions.BREVO_API_BASE_PAR_DEFAUT,
        "mail_from": lire("MAIL_FROM") or connexions.MAIL_FROM_PAR_DEFAUT,
    }
    return lire("STRIPE_SECRET_KEY"), config


def module_stripe(secret):
    """Le module `stripe`, clé posée — ou None sans clé (l'alerte le dira)."""
    if not secret:
        return None
    import stripe
    stripe.api_key = secret
    return stripe


def base_de_donnees(environ, ecrire):
    """Une lecture de la base de production, si DATABASE_URL est là et que
    psycopg est installé ; sinon None, et l'outil le dit. Chaque requête ouvre
    et ferme sa connexion : rien ne reste derrière l'outil."""
    url = str(environ.get("DATABASE_URL") or "").strip()
    if not url:
        ecrire("%s base : DATABASE_URL absente, journal et dernier événement "
               "non lus" % TIRET)
        return None
    try:
        import psycopg
        import psycopg.rows
    except Exception:                                                  # noqa: BLE001
        ecrire("%s base : psycopg absent, journal et dernier événement non lus"
               % TIRET)
        return None

    def lire(sql, params=()):
        with psycopg.connect(url, row_factory=psycopg.rows.dict_row,
                             connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute(sql.replace("?", "%s"), tuple(params))
                return [dict(r) for r in cur.fetchall()]
    return lire


def _sans(codes, alertes):
    return not any(a["code"] in codes for a in alertes)


def lignes(diag):
    """Une ligne par contrôle : (état, texte). État : True (✓), False (✗) ou
    None (– : non vérifié)."""
    s, b, alertes = diag.get("stripe", {}), diag.get("brevo", {}), diag.get("alertes", [])
    out = []

    def ligne(etat, texte):
        out.append((etat, texte))

    ligne(bool(s.get("cle_presente")), "Stripe : clé présente")
    compte = s.get("compte")
    if compte:
        ligne(_sans({"stripe_encaissement_desactive"}, alertes),
              "Stripe : compte %s lisible, mode %s, encaissement %s"
              % (compte.get("id"), "réel" if compte.get("livemode") else "TEST",
                 "activé" if compte.get("charges_enabled") else "DÉSACTIVÉ"))
    else:
        ligne(None if not s.get("cle_presente") else False, "Stripe : compte non lu")
    ligne(bool(s.get("point_actif")),
          "Stripe : point de réception actif vers %s" % s.get("point_attendu"))
    if s.get("point_actif"):
        manquants = s.get("evenements_manquants") or []
        ligne(not manquants, "Stripe : événements requis couverts"
              + ("" if not manquants else " — manquent : " + ", ".join(manquants)))
        ligne(_sans({"stripe_webhook_version_api"}, alertes),
              "Stripe : version d'API du point = bibliothèque (%s)"
              % s.get("version_api_bibliotheque"))
    ligne(bool(s.get("secret_webhook_present")), "Stripe : secret de signature présent")
    de = s.get("dernier_evenement") or {}
    if not de.get("disponible"):
        ligne(None, "Stripe : dernier événement reçu — base non lue")
    elif de.get("recu_le") is None:
        ligne(False, "Stripe : aucun événement jamais reçu")
    else:
        ligne(True, "Stripe : dernier événement reçu le %s (il y a %s h)"
              % (de["recu_le"], de.get("age_heures")))
    for nom, etat in sorted((s.get("prix") or {}).items()):
        ligne(bool(etat.get("actif") and etat.get("recurrent")),
              "Stripe : prix %s %s" % (nom, "actif et récurrent"
                                        if etat.get("actif") and etat.get("recurrent")
                                        else ("absent" if not etat.get("id")
                                              else "inactif ou ponctuel")))
    autres = s.get("autres_points") or []
    if autres:
        ligne(None, "Stripe : autres points de réception du compte : " + ", ".join(autres))

    ligne(bool(b.get("cle_presente")), "Brevo : clé présente")
    compte = b.get("compte")
    if compte:
        ligne(_sans({"brevo_credits_faibles"}, alertes),
              "Brevo : compte lisible, offre %s, crédits restants %s"
              % ("/".join(compte.get("plan") or []) or "?", compte.get("credits")))
    else:
        ligne(None if not b.get("cle_presente") else False, "Brevo : compte non lu")
    ligne(bool(b.get("expediteur_verifie")),
          "Brevo : expéditeur %s vérifié" % b.get("expediteur"))
    j = b.get("journal_24h") or {}
    if j.get("disponible"):
        derniere = j.get("derniere_erreur") or {}
        ligne(True, "Brevo : journal 24 h — %s ok, %s échec(s)%s"
              % (j.get("ok"), j.get("echecs"),
                 (", dernière erreur : %s" % derniere.get("raison")) if derniere else ""))
        ligne((b.get("envois_non_routables") or 0) == 0,
              "Brevo : envois vers %s dans le journal : %s"
              % (connexions.DOMAINE_NON_ROUTABLE, b.get("envois_non_routables")))
    else:
        ligne(None, "Brevo : journal non lu")
    return out


def imprimer(diag, ecrire):
    for etat, texte in lignes(diag):
        ecrire("%s %s" % (COCHE if etat else (TIRET if etat is None else CROIX), texte))
    alertes = diag.get("alertes", [])
    ecrire("")
    if not alertes:
        ecrire("%s Tout est branché." % COCHE)
    for a in alertes:
        ecrire("[%s] %s — %s" % (a["gravite"].upper(), a["code"], a["message"]))
    ecrire("vérifié le %s" % diag.get("verifie_le"))


def principal(environ=None, ecrire=None):
    """Le code de sortie : 1 si une alerte est bloquante, 0 sinon."""
    environ = os.environ if environ is None else environ
    ecrire = ecrire or (lambda t: sys.stdout.write(t + "\n"))
    secret, config = configuration(environ)
    import requests
    diag = connexions.diagnostic(stripe=module_stripe(secret), session=requests.Session(),
                                 config=config, base=base_de_donnees(environ, ecrire))
    imprimer(diag, ecrire)
    return 1 if connexions.bloquant(diag) else 0


if __name__ == "__main__":
    # La sortie standard de Render n'est pas toujours en UTF-8 : on force,
    # sinon la coche fait tomber l'outil sur un UnicodeEncodeError.
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception:                                                  # noqa: BLE001
        pass
    sys.exit(principal())
