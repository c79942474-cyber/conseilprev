"""CONSEILPREV INFO — veille sourcée : cyber industrielle, IA, SIA, centres de données.

CE QUE CETTE APPLICATION SERT, ET CE QU'ELLE REFUSE DE SERVIR. Elle rend des
fiches de veille dont chacune porte sa source, sa date, son statut de
vérification et une lecture critique dont la PROVENANCE est déclarée. Une
fiche qui ne remplit pas ces conditions n'est pas servie — pas « servie avec
une réserve » : refusée par `veille.publiables()`, qui est la seule porte.

LE CORPUS N'EST PAS DANS LE CODE. Il est collecté depuis les sources ouvertes
du registre, puis gardé en mémoire pour un temps borné. Un corpus figé dans un
fichier serait périmé le jour de la mise en ligne ; une collecte à chaque
requête taperait sur les serveurs des éditeurs à chaque visiteur.

DÉMARRAGE LOCAL :  python app.py
"""
import os
import re
import threading
import time
from datetime import datetime, timezone

from flask import (Flask, jsonify, make_response, request,
                   send_from_directory)

import abonnes as AB
import bulletin as BUL
import confrontation as CONF
import classeur as CL
import croisement as X
import exporter as EXP
import decision as DEC
import ingestion
import organisations as ORG
import redaction as RED
import revue as RV
import sources as SRC
import veille as V

ICI = os.path.dirname(os.path.abspath(__file__))
VERSION = "2026.08.23"

# LE CLASSEUR SE VIDE AVEC LE COMPTE. `abonnes.oublier()` promet que « rien
# n'en subsiste dans ce processus » ; cette inscription est ce qui maintient
# la phrase vraie maintenant qu'un autre module garde des données de compte.
AB.a_purger(CL.vider)

app = Flask(__name__, static_folder=None)

# LA BORNE EST POSÉE AU SERVEUR, PAS SEULEMENT DANS LE MODULE. Le contrôle de
# `confrontation.lire()` s'applique une fois le fichier REÇU EN ENTIER : sans
# cette borne-ci, un envoi de deux gigaoctets serait d'abord absorbé, puis
# refusé poliment. Flask coupe désormais la connexion avant.
# La marge sur OCTETS_MAX couvre l'enveloppe multipart, qui n'est pas du
# document mais compte dans la taille de la requête.
app.config["MAX_CONTENT_LENGTH"] = CONF.OCTETS_MAX + 512 * 1024


@app.errorhandler(413)
def _trop_gros(_e):
    """Sans ce gestionnaire, Flask rend une page HTML et le client, qui attend
    du JSON, échoue sur « Unexpected token '<' » — il afficherait donc une
    panne au lieu de la vraie raison."""
    return jsonify(ok=False, erreur="trop_volumineux",
                   message="Document trop volumineux : maximum %d Mo."
                           % (CONF.OCTETS_MAX // 1048576)), 413

# ── LE CORPUS EN MÉMOIRE ──────────────────────────────────────────────────
# Rafraîchi au plus toutes les TTL secondes, et JAMAIS pendant qu'un visiteur
# attend : la première requête après expiration sert l'ancien corpus et
# déclenche la collecte en fond. Faire attendre un lecteur le temps de
# télécharger neuf mégaoctets serait le rendre otage de la cadence des
# éditeurs.
_CORPUS = {"fiches": [], "journal": [], "quand": 0.0, "collectes": 0}
_VERROU = threading.Lock()
_EN_COURS = threading.Event()

# CINQ MINUTES, ET NON PLUS TRENTE — ce que les cadences par source rendent
# possible. Le tour de collecte ne relit plus TOUT : chaque source est relue au
# rythme auquel ELLE change (`ingestion.CADENCES`), si bien qu'un tour qui
# prenait neuf secondes et neuf mégaoctets en prend une et quelques kilo-octets
# dès que les référentiels sont à jour. Rapprocher la cadence AVANT cette
# séparation aurait retéléchargé ATT&CK et ATLAS toutes les cinq minutes — de
# la charge prise sur des sources publiques qui la supportent parce que
# personne n'en abuse.
TTL = int(os.environ.get("VEILLE_TTL", "300"))


def _collecter():
    if _EN_COURS.is_set():
        return
    _EN_COURS.set()
    try:
        r = ingestion.collecter_tout(limite_kev=int(os.environ.get("KEV_MAX", "40")))
        with _VERROU:
            # ON NE REMPLACE QUE SI LA COLLECTE A RAPPORTÉ QUELQUE CHOSE. Une
            # source momentanément injoignable ne doit pas vider le site :
            # une fiche d'hier vaut mieux qu'une page blanche, à condition que
            # sa date soit affichée — elle l'est.
            if r.get("corpus"):
                _CORPUS["fiches"] = r["corpus"]
                _CORPUS["quand"] = time.time()
                _CORPUS["collectes"] += 1
            _CORPUS["journal"] = r.get("journal", [])
    except Exception as e:  # noqa: BLE001
        app.logger.warning("collecte échouée : %s", e)
        with _VERROU:
            _CORPUS["journal"] = [{"source": "*", "ok": False,
                                   "erreur": "exception", "message": str(e)}]
    finally:
        _EN_COURS.clear()


def corpus():
    with _VERROU:
        fiches = list(_CORPUS["fiches"])
        age = time.time() - _CORPUS["quand"]
    if not fiches:
        _collecter()                      # premier appel : on attend
        with _VERROU:
            fiches = list(_CORPUS["fiches"])
    elif age > TTL:
        threading.Thread(target=_collecter, daemon=True).start()
    return fiches


def _etat_corpus():
    with _VERROU:
        return {
            "fiches": len(_CORPUS["fiches"]),
            "collectes": _CORPUS["collectes"],
            "collecte_le": (datetime.fromtimestamp(_CORPUS["quand"], timezone.utc)
                            .isoformat(timespec="seconds")
                            if _CORPUS["quand"] else None),
            "age_s": int(time.time() - _CORPUS["quand"]) if _CORPUS["quand"] else None,
            "ttl_s": TTL,
            "journal": _CORPUS["journal"],
        }


# ── PAGES ─────────────────────────────────────────────────────────────────
@app.route("/")
def accueil():
    return send_from_directory(ICI, "index.html")


@app.route("/<path:nom>.css")
def css(nom):
    return send_from_directory(ICI, nom + ".css")


@app.route("/<path:nom>.js")
def js(nom):
    return send_from_directory(ICI, nom + ".js")


@app.route("/polices/<nom>.woff2")
def police(nom):
    """LES POLICES SONT SERVIES D'ICI, ET NON DE GOOGLE. Le `<link>` vers
    `fonts.googleapis.com` envoyait à un tiers, à chaque visite et avant tout
    consentement, l'adresse IP du lecteur, sa page de provenance et la
    signature de son navigateur — pour de la typographie. Le motif complet est
    dans `polices.css` ; ici il ne reste qu'une route.

    UN AN DE CACHE, ET C'EST SANS RISQUE : le nom du fichier porte la famille
    et le sous-ensemble, jamais une version. Le jour où une police change, elle
    change de nom."""
    r = send_from_directory(os.path.join(ICI, "polices"), nom + ".woff2")
    r.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return r


@app.route("/confidentialite")
def page_confidentialite():
    return send_from_directory(ICI, "confidentialite.html")


@app.route("/revue")
def page_revue():
    return send_from_directory(ICI, "revue.html")


# ═══════════════════════════════════════════════════════════════════════════
#  LES EN-TÊTES DE SÉCURITÉ
#
#  POURQUOI ILS SONT POSÉS ICI ET NON DANS UN RÉGLAGE D'HÉBERGEUR. Un en-tête
#  configuré chez Render vaut pour Render : il disparaît au premier
#  déménagement, sans que rien ne le signale, et le site continue de se servir
#  en paraissant identique. Posé dans l'application, il voyage avec elle — et
#  `tests/test_securite.py` le vérifie sur des réponses réelles.
#
#  LA POLITIQUE DE CONTENU EST FERMÉE, sans exception à justifier : depuis que
#  les polices sont au dépôt, ce site ne charge RIEN d'un tiers. Écrire
#  `default-src 'self'` n'est donc pas une rigueur d'affichage, c'est la
#  description exacte de ce que les pages font.
# ═══════════════════════════════════════════════════════════════════════════

CSP = "; ".join([
    "default-src 'self'",
    # Aucun script en ligne, aucun `eval` : les quatre pages ne portent que des
    # `<script src>`. Sans `'unsafe-inline'`, une injection de balise dans une
    # fiche ne s'exécute pas — et c'est le seul cas où cette règle sert
    # vraiment, puisque le corpus vient de sources tierces.
    "script-src 'self'",
    # Idem pour le style : plus aucun attribut `style=` dans les pages ni dans
    # ce que le JavaScript compose. C'est ce qui permet de se passer de
    # `'unsafe-inline'` ici — la seule directive qui, laissée ouverte, vide la
    # politique de son sens.
    "style-src 'self'",
    "font-src 'self'",
    "img-src 'self' data:",
    "connect-src 'self'",
    "form-action 'self'",
    # RIEN NE PEUT ENCADRER CE SITE, ET IL N'ENCADRE RIEN. Les deux sens
    # comptent : le premier interdit le détournement de clic, le second retire
    # une surface entière.
    "frame-ancestors 'none'",
    "frame-src 'none'",
    "object-src 'none'",
    # `base-uri` est la directive qu'on oublie : sans elle, une seule balise
    # `<base>` injectée détourne toutes les adresses relatives de la page,
    # y compris celles des scripts déjà autorisés.
    "base-uri 'none'",
])

PERMISSIONS = ", ".join(
    "%s=()" % p for p in
    # CE SITE NE DEMANDE AUCUNE DE CES CAPACITÉS. Les refuser explicitement
    # coûte une ligne et retire la question : un script tiers introduit un jour
    # par erreur ne pourra pas les demander non plus.
    ("geolocation", "camera", "microphone", "payment", "usb", "magnetometer",
     "gyroscope", "accelerometer", "midi", "serial", "bluetooth",
     "display-capture", "browsing-topics", "interest-cohort")
)


@app.after_request
def _entetes(r):
    r.headers.setdefault("Content-Security-Policy", CSP)
    r.headers.setdefault("X-Content-Type-Options", "nosniff")
    r.headers.setdefault("X-Frame-Options", "DENY")
    # AUCUN RÉFÉRENT N'EST ENVOYÉ, MÊME PAS L'ORIGINE. Les fiches renvoient aux
    # sources — CISA, MITRE, la Commission —, et l'adresse d'une fiche dit ce
    # que le lecteur consultait. `strict-origin-when-cross-origin` enverrait
    # tout de même « conseilprevinfo.onrender.com » : c'est peu, mais c'est
    # gratuit à retirer et cela n'enlève rien au site.
    r.headers.setdefault("Referrer-Policy", "no-referrer")
    r.headers.setdefault("Permissions-Policy", PERMISSIONS)
    r.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
    r.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
    # HSTS N'EST POSÉ QUE SUR UNE CONNEXION DÉJÀ CHIFFRÉE. Envoyé en clair, il
    # est ignoré par les navigateurs — et en développement, sur `localhost`, il
    # verrouillerait le poste du développeur sur du HTTPS que rien n'y sert.
    # Render termine le TLS en amont : c'est `X-Forwarded-Proto` qui fait foi.
    proto = request.headers.get("X-Forwarded-Proto", request.scheme)
    if proto == "https":
        r.headers.setdefault("Strict-Transport-Security",
                             "max-age=31536000; includeSubDomains")
    return r


# ── INTERFACES ────────────────────────────────────────────────────────────
def _langue_analyses():
    """LA LANGUE DEMANDÉE POUR LES ANALYSES, et rien d'autre.

    ELLE EST SÉPARÉE DE LA LANGUE D'INTERFACE, ET C'EST LE POINT. Un lecteur
    peut vouloir l'interface en anglais et garder les analyses en français —
    c'est ce que fait un francophone qui travaille en anglais mais relit les
    textes du cabinet dans leur version d'origine —, et l'inverse est vrai
    aussi. Une seule bascule pour les deux déciderait à sa place.

    LE DÉFAUT EST LE FRANÇAIS parce que c'est la langue d'écriture de ce site :
    un paramètre absent ne doit jamais faire servir une traduction que
    personne n'a demandée."""
    return "en" if (request.args.get("analyses") or "").lower() == "en" else "fr"


@app.route("/api/veille")
def api_veille():
    """Les fiches, filtrées. Aucun paramètre ne peut faire sortir une fiche
    non publiable : `filtrer()` applique la porte avant tout le reste."""
    f = V.filtrer(
        corpus(),
        sujet=request.args.get("sujet") or None,
        pays=request.args.get("pays") or None,
        techno=request.args.get("techno") or None,
        depuis=request.args.get("depuis") or None,
        jusqua=request.args.get("jusqua") or None,
        impact=request.args.get("impact") or None,
        horizon=request.args.get("horizon") or None,
        organisation=request.args.get("organisation") or None,
        siege=request.args.get("siege") or None,
    )
    # LA TRADUCTION PRÉCÈDE LA RECHERCHE, ET NON L'INVERSE. Un lecteur qui
    # cherche « poisoning » sur une interface anglaise cherche dans ce qu'il a
    # sous les yeux ; chercher dans le français lui rendrait des fiches dont
    # aucun mot visible ne porte son terme, ce qui se lit comme une panne.
    f = [V.dans(x, _langue_analyses()) for x in f]
    q = (request.args.get("q") or "").strip()
    if q:
        f = V.chercher(f, q)
    try:
        n = max(1, min(200, int(request.args.get("n") or 60)))
    except ValueError:
        n = 60
    # UNE COUPE QUI NE SE DIT PAS SE LIT COMME UNE COUVERTURE COMPLÈTE.
    # DÉFAUT CORRIGÉ, constaté au navigateur : la page annonçait « 66 fiches
    # retenues » et en affichait 60, sans rien signaler. Le lecteur croyait
    # tenir tout le corpus filtré. La coupe est donc rendue explicitement,
    # avec de quoi la lever — ce n'est pas au client de la deviner en
    # comparant deux nombres.
    coupe = len(f) > n
    return jsonify(ok=True, version=VERSION, total=len(f), fiches=f[:n],
                   affichees=min(n, len(f)), plafond=n, tronque=coupe,
                   tronque_dit=("%d fiche(s) retenues, %d affichées. La liste "
                                "est coupée au %dᵉ rang : ce n'est pas la "
                                "fin du corpus filtré."
                                % (len(f), min(n, len(f)), n)) if coupe else "",
                   etat=_etat_corpus())


@app.route("/abonnement")
def page_abonnement():
    return send_from_directory(ICI, "abonnement.html")


@app.route("/fiche/<ident>")
def page_fiche(ident):
    """UNE ADRESSE PAR FICHE. Sans cela, rien ne se cite ni ne se transmet :
    un lecteur qui veut renvoyer un collègue à une information ne peut lui
    donner que l'adresse du site entier, à charge pour lui de la retrouver.

    LE STATUT HTTP DIT LA VÉRITÉ, PAS SEULEMENT LA PAGE. Constaté au
    navigateur : une adresse inventée rendait « 200 OK » tout en affichant
    « Fiche introuvable ». Ce n'est pas un détail d'indexation — c'est le
    site qui affirme dans son protocole le contraire de ce qu'il écrit à
    l'écran, et tout ce qui le lit sans yeux (moteur, lien archivé,
    surveillance) enregistre une page valide.
    """
    connue = any(x.get("id") == ident for x in V.publiables(corpus()))
    r = send_from_directory(ICI, "fiche.html")
    return r if connue else (r, 404)


@app.route("/api/veille/fiche/<ident>")
def api_fiche(ident):
    """La fiche seule, et ses voisines.

    Une fiche non publiable répond 404 comme si elle n'existait pas : dire
    « cette fiche existe mais vous n'y avez pas droit » renseignerait sur le
    contenu de la réserve éditoriale."""
    tout = corpus()
    f = next((x for x in V.publiables(tout) if x.get("id") == ident), None)
    if not f:
        return jsonify(ok=False, erreur="introuvable",
                       message="Aucune fiche publiée sous cet identifiant."), 404
    f = V.dans(f, _langue_analyses())
    # LES VOISINES : même sujet, jamais la fiche elle-même. Elles donnent au
    # lecteur la suite naturelle sans qu'il retourne au fil.
    # LE CROISEMENT REMPLACE « ARTICLES SIMILAIRES ». Chaque voisine porte le
    # MOTIF de son rapprochement : sans lui, le lecteur ne sait pas s'il tient
    # une coïncidence de vocabulaire ou une vraie dépendance.
    # LE VOISINAGE DE DATE EST RENDU À PART, sous son vrai nom. Mêlé aux
    # liens, il les noyait : mesuré sur le corpus, il représentait 312
    # rapprochements sur 314, tous porteurs du même motif recopié.
    # LA COMPOSITION D'ENSEMBLE ACCOMPAGNE LA FICHE. Sans elle, un lecteur qui
    # lit « aucun lien établi » croit tenir une particularité de CETTE fiche,
    # alors que c'est l'état de tout le corpus — et il en conclurait que la
    # rubrique est en panne.
    return jsonify(ok=True, fiche=f, types_de_lien=X.LIENS,
                   composition=X.mesure_liens(tout), **X.croiser(f, tout))


# LES MÊMES PARAMÈTRES QUE LE FIL, ET C'EST TOUT LE POINT. Les facettes
# décrivent LES FICHES TROUVÉES : servies sur le corpus entier, elles
# proposaient des combinaisons qui ne rendaient rien — « Systèmes d'IA » puis
# « DE (2) », alors qu'aucune fiche de cette rubrique ne porte de pays.
_FILTRES_FIL = ("sujet", "pays", "techno", "depuis", "jusqua",
                "impact", "horizon", "organisation", "siege", "q")


def _filtres_demandes():
    """Les filtres de la requête, dans une seule table lue par le fil ET par
    les facettes. Deux listes séparées auraient divergé, et les menus se
    seraient mis à décrire autre chose que ce que la page affiche."""
    return {k: (request.args.get(k) or None) for k in _FILTRES_FIL}


# ── EMPORTER UNE FICHE ────────────────────────────────────────────────────
# LA MÊME PORTE QUE LA PAGE. Une fiche non publiable répond 404 à l'export
# comme elle y répond à l'écran : un format de sortie ne doit jamais devenir
# le chemin de contournement d'une règle éditoriale.
@app.route("/fiche/<ident>.<format_>")
def emporter(ident, format_):
    if format_ not in ("pdf", "docx"):
        return (jsonify(ok=False, erreur="format_inconnu",
                        message="Formats servis : pdf, docx."), 404)
    f = next((x for x in V.publiables(corpus()) if x.get("id") == ident), None)
    if not f:
        return (jsonify(ok=False, erreur="introuvable",
                        message="Aucune fiche publiée ne porte cet "
                                "identifiant."), 404)
    langue = _langue_analyses()
    f = V.dans(f, langue)
    url = request.url_root.rstrip("/") + "/fiche/" + ident
    try:
        octets = (EXP.pdf(f, url, langue) if format_ == "pdf"
                  else EXP.docx(f, url, langue))
    except RuntimeError as e:
        # LE MOTIF EST RENDU, PAS UNE ERREUR NUE. « 500 » laisserait croire à
        # une panne du site ; ici c'est une capacité absente, et elle se dit.
        return (jsonify(ok=False, erreur="format_indisponible",
                        message=str(e)), 503)
    mime = ("application/pdf" if format_ == "pdf"
            else "application/vnd.openxmlformats-officedocument."
                 "wordprocessingml.document")
    r = make_response(octets)
    r.headers["Content-Type"] = mime
    r.headers["Content-Disposition"] = (
        'attachment; filename="%s"' % EXP._nom_fichier(f, format_))
    # RIEN N'EST MIS EN CACHE PAR UN INTERMÉDIAIRE : une fiche corrigée doit
    # ressortir corrigée, y compris pour qui a déjà téléchargé la précédente.
    r.headers["Cache-Control"] = "no-store"
    return r


@app.route("/api/veille/facettes")
def api_facettes():
    return jsonify(ok=True, **V.facettes(corpus(), **_filtres_demandes()))


@app.route("/api/veille/dossiers")
def api_dossiers():
    """Les regroupements que le corpus FORME de lui-même — jamais des
    rubriques décidées à l'avance, qui resteraient vides ou trop pleines."""
    c = corpus()
    return jsonify(ok=True,
                   par_terme=X.dossiers_par_terme(c),
                   par_entite=X.dossiers(c),
                   mesure_entites=X.mesure_entites(c),
                   tension=X.tension(c))


@app.route("/api/veille/pistes")
def api_pistes():
    """Les pistes d'instruction que le corpus permet d'ouvrir.

    LA MESURE ACCOMPAGNE TOUJOURS LES PISTES, y compris les déclencheurs
    muets : un module qui n'afficherait que ce qu'il trouve laisserait croire
    que le reste ne donne rien parce qu'il n'y a rien — alors que le plus
    souvent, la source qui le nourrirait n'est pas branchée.
    """
    c = corpus()
    return jsonify(ok=True, version=DEC.VERSION,
                   pistes=DEC.pistes(c), mesure=DEC.mesure(c),
                   solidites=DEC.SOLIDITES)


@app.route("/api/veille/referentiel")
def api_referentiel():
    """Le vocabulaire du site, servi plutôt que recopié dans la page.

    Écrit dans le HTML, il divergerait du moteur au premier ajout de statut —
    et c'est l'écran qui ferait foi pour le lecteur."""
    return jsonify(ok=True, version=VERSION,
                   sujets=V.sujets(), statuts=V.statuts(),
                   lectures=V.lectures(), impacts=V.impacts(),
                   horizons=V.horizons(),
                   # LE RÉPERTOIRE DES ORGANISATIONS, EN ENTIER — y compris
                   # celles qu'aucune fiche ne nomme aujourd'hui. Les menus,
                   # eux, ne montrent que ce qui est trouvé : cette liste-ci
                   # sert à NOMMER une clé déjà portée par une fiche, et une
                   # fiche ancienne peut nommer une entreprise absente du
                   # corpus du jour.
                   organisations=V.organisations(),
                   origine_du_siege=ORG.ORIGINE_DU_SIEGE[0],
                   origine_du_siege_en=ORG.ORIGINE_DU_SIEGE[1],
                   # CE QUE LA BASCULE FR/EN NE TRADUIT PAS, avec son compte.
                   # L'écran l'affiche au moment où la bascule sert : une
                   # interface anglaise posée sur des analyses françaises est
                   # un mensonge par omission. Le nombre vient d'ici, pas
                   # d'une phrase écrite une fois pour toutes.
                   langues=V.langues(corpus()))


@app.route("/api/revue")
def api_revue():
    """LA REVUE D'UNE PÉRIODE — hebdomadaire, ou mensuelle internationale.

    L'ANCRE PAR DÉFAUT EST LA PLUS RÉCENTE QUE LE CORPUS DOCUMENTE, et non
    aujourd'hui. Mesuré : le fait le plus récent du corpus a plusieurs
    semaines, si bien qu'ouvrir sur la semaine en cours servirait une page
    vide à chaque visite — le lecteur en conclurait une panne plutôt qu'un
    état du corpus. La page dit laquelle elle ouvre, et de combien elle est
    en arrière.

    L'ANCRE SUIT LA RÈGLE DE LA REVUE DEMANDÉE : la dernière semaine
    documentée et le dernier mois documenté SOUS LA RÈGLE INTERNATIONALE ne
    sont pas la même date."""
    genre = request.args.get("genre") or "semaine"
    if genre not in RV.GENRES:
        return (jsonify(ok=False, erreur="genre_inconnu",
                        message="Genres servis : %s." % ", ".join(RV.GENRES)), 400)
    inter = (request.args.get("international") or "") in ("1", "oui", "true")
    langue = _langue_analyses()
    c = corpus()
    ancre = request.args.get("ancre") or None
    if ancre and not re.match(r"^\d{4}-\d{2}-\d{2}$", ancre):
        # UNE ANCRE ILLISIBLE N'EST PAS FORCÉE À AUJOURD'HUI EN SILENCE : le
        # lecteur croirait avoir ouvert la période qu'il a demandée.
        return (jsonify(ok=False, erreur="ancre_illisible",
                        message="La date doit s'écrire AAAA-MM-JJ."), 400)
    if not ancre:
        ancre = RV.derniere_ancre(c, genre, international=inter)
    # LES ANALYSES SONT TRADUITES AVANT LE DÉCOUPAGE, comme sur le fil : une
    # revue anglaise composée de fiches françaises se lirait comme une panne.
    fiches = [V.dans(x, langue) for x in c]
    return jsonify(RV.revue(fiches, genre, ancre, international=inter,
                            langue=langue))


@app.route("/api/sources")
def api_sources():
    return jsonify(ok=True, version=SRC.VERSION,
                   sources=SRC.registre(request.args.get("sujet") or None),
                   natures=SRC.natures(), a_brancher=SRC.A_BRANCHER,
                   # LES NATURES D'OBSTACLE VOYAGENT AVEC LA LISTE : sans
                   # elles, la page devrait recopier les libellés, et ils
                   # divergeraient à la première correction.
                   obstacles=SRC.obstacles())


@app.route("/api/sources/sonde/<cle>")
def api_sonde(cle):
    """Va RÉELLEMENT chercher la source et dit ce qu'elle a répondu.

    Ouverte : elle ne divulgue rien qu'un lecteur ne puisse constater
    lui-même en ouvrant l'adresse, et elle rend vérifiable la promesse
    « nos sources sont atteignables »."""
    r = SRC.sonder(cle)
    return jsonify(r) if r.get("ok") else (jsonify(r), 502 if r.get("cle") else 404)


# ═══════════════════════════════════════════════════════════════════════════
#  LES ABONNÉS. Le jeton voyage dans l'en-tête `Authorization`, jamais dans
#  l'URL : une adresse se retrouve dans les journaux du serveur, dans
#  l'historique du navigateur et dans le `Referer` envoyé aux tiers.
# ═══════════════════════════════════════════════════════════════════════════

def _jeton():
    a = request.headers.get("Authorization") or ""
    return a[7:].strip() if a.lower().startswith("bearer ") else ""


@app.route("/api/abonnes/inscription", methods=["POST"])
def api_inscription():
    d = request.get_json(silent=True) or {}
    r = AB.creer(d.get("email"), d.get("motdepasse"),
                 d.get("sujets"), d.get("seuil") or "structurant")
    # LA RÉPONSE NE DIT PAS SI L'ADRESSE ÉTAIT DÉJÀ INSCRITE : ce serait
    # confirmer à un tiers qu'une personne est abonnée ici.
    r.pop("deja", None)
    return (jsonify(r), 200 if r.get("ok") else 400)


@app.route("/api/abonnes/connexion", methods=["POST"])
def api_connexion():
    d = request.get_json(silent=True) or {}
    r = AB.connecter(d.get("email"), d.get("motdepasse"))
    return (jsonify(r), 200 if r.get("ok") else 401)


@app.route("/api/abonnes/deconnexion", methods=["POST"])
def api_deconnexion():
    return jsonify(AB.deconnecter(_jeton()))


@app.route("/api/abonnes/moi")
def api_moi():
    c = AB.compte_de(_jeton())
    if not c:
        return jsonify(ok=False, erreur="non_connecte"), 401
    return jsonify(ok=True, compte=AB._public(c),
                   envoi_raccorde=bool(AB.PRESTATAIRE_COURRIEL),
                   pourquoi_pas_d_envoi=AB.POURQUOI_PAS_D_ENVOI
                   if not AB.PRESTATAIRE_COURRIEL else None)


@app.route("/api/abonnes/reglages", methods=["POST"])
def api_reglages():
    d = request.get_json(silent=True) or {}
    r = AB.regler(_jeton(), d.get("sujets"), d.get("seuil"))
    return (jsonify(r), 200 if r.get("ok")
            else (401 if r.get("erreur") == "non_connecte" else 400))


@app.route("/api/abonnes/effacer", methods=["POST"])
def api_effacer():
    r = AB.oublier(_jeton())
    return (jsonify(r), 200 if r.get("ok") else 401)


@app.route("/api/abonnes/bulletin")
def api_bulletin():
    """LE BULLETIN TEL QU'IL SERAIT ENVOYÉ — et il n'est pas envoyé.

    Montrer le courrier avant de pouvoir l'expédier n'est pas un pis-aller :
    c'est ce qui permet de le relire en entier. Un bulletin qu'on ne voit
    qu'une fois parti se corrige toujours trop tard.
    """
    c = AB.compte_de(_jeton())
    if not c:
        return jsonify(ok=False, erreur="non_connecte"), 401
    b = BUL.composer(corpus(), AB._public(c))
    b["pourquoi_pas_envoye"] = (None if AB.PRESTATAIRE_COURRIEL
                                else AB.POURQUOI_PAS_D_ENVOI)
    return jsonify(ok=True, bulletin=b, texte=BUL.texte(b))


@app.route("/confronter")
def page_confronter():
    return send_from_directory(ICI, "confronter.html")


# ═══════════════════════════════════════════════════════════════════════════
#  LE CLASSEUR — les documents d'un compte, et rien qu'à lui.
#
#  LE COMPTE EST RÉSOLU ICI, ET PASSÉ AU MODULE. `classeur.py` n'a aucune
#  fonction qui prenne un identifiant de document sans prendre aussi le
#  compte : il suffirait d'un chemin d'API oublié pour ouvrir le classeur
#  d'autrui, et cette forme-là rend l'oubli impossible.
# ═══════════════════════════════════════════════════════════════════════════

def _courriel():
    c = AB.compte_de(_jeton())
    return c["email"] if c else None


@app.route("/api/classeur")
def api_classeur():
    e = _courriel()
    if not e:
        return jsonify(ok=False, erreur="non_connecte"), 401
    return jsonify(CL.lister(e))


@app.route("/api/classeur", methods=["POST"])
def api_classeur_deposer():
    e = _courriel()
    if not e:
        return jsonify(ok=False, erreur="non_connecte"), 401
    fichier = request.files.get("document")
    if not fichier:
        return jsonify(ok=False, erreur="sans_document",
                       message="Aucun document reçu."), 400
    r = CL.deposer(e, fichier.filename, fichier.read())
    return jsonify(r), (200 if r.get("ok") else 400)


@app.route("/api/classeur/<ident>")
def api_classeur_lire(ident):
    e = _courriel()
    if not e:
        return jsonify(ok=False, erreur="non_connecte"), 401
    d = CL.contenu(e, ident)
    if not d:
        return jsonify(ok=False, erreur="introuvable"), 404
    r = make_response(d["octets_bruts"])
    r.headers["Content-Type"] = d["type"]
    # LE NOM EST CELUI DU DÉPÔT, entre guillemets échappés : un nom porteur de
    # guillemets casserait l'en-tête et ferait servir le fichier sous un autre
    # nom que celui affiché.
    r.headers["Content-Disposition"] = (
        'attachment; filename="%s"' % d["nom"].replace('"', ""))
    r.headers["Cache-Control"] = "no-store, private"
    return r


@app.route("/api/classeur/<ident>/effacer", methods=["POST"])
def api_classeur_effacer(ident):
    e = _courriel()
    if not e:
        return jsonify(ok=False, erreur="non_connecte"), 401
    r = CL.effacer(e, ident)
    return jsonify(r), (200 if r.get("ok") else 404)


@app.route("/api/confrontation", methods=["POST"])
def api_confrontation():
    """Confronte un document déposé au corpus. RÉSERVÉ AUX ABONNÉS.

    POURQUOI LA PORTE. Le document d'un industriel — politique de sécurité,
    schéma d'architecture, cahier des charges — est une donnée d'exposition :
    savoir ce qu'il contient renseigne sur son installation. Ouvrir cette
    route sans compte reviendrait à offrir un dépôt anonyme dont personne ne
    répond.

    LE DOCUMENT N'EST PAS CONSERVÉ. Il est lu en mémoire, confronté, et jeté
    avec la requête. La réponse ne contient pas le texte déposé — seulement
    des termes et des comptes.
    """
    c = AB.compte_de(_jeton())
    if not c:
        return jsonify(ok=False, erreur="non_connecte",
                       message="Cette confrontation demande un compte : le "
                               "document que vous déposez est une donnée "
                               "d'exposition."), 401
    f = request.files.get("document")
    if not f:
        return jsonify(ok=False, erreur="sans_document",
                       message="Aucun document reçu."), 400
    texte, faute = CONF.lire(f.filename or "", f.read())
    if faute:
        return jsonify(ok=False, erreur="illisible", message=faute), 400
    r = CONF.confronter(texte, corpus(), sujet=request.form.get("sujet") or None)
    # LE TEXTE EST OUBLIÉ ICI, explicitement : le laisser vivre dans la portée
    # de la fonction jusqu'au retour ne coûte rien, mais l'effacer écrit la
    # règle là où quelqu'un ajouterait un jour une journalisation.
    del texte
    return (jsonify(r), 200 if r.get("ok") else 400)


@app.route("/api/sante")
def api_sante():
    c = corpus()
    return jsonify(ok=True, version=VERSION,
                   veille=V.sante(c), sources=SRC.sante(),
                   ingestion=ingestion.sante(), croisement=X.sante(c),
                   decision=DEC.sante(c), abonnes=AB.sante(),
                   confrontation=CONF.sante(),
                   classeur=CL.sante(), export=EXP.sante(),
                   bulletin=BUL.sante(), organisations=ORG.sante(),
                   revue=RV.sante(c), redaction=RED.sante(),
                   corpus=_etat_corpus())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")),
            debug=bool(os.environ.get("DEBUG")))
