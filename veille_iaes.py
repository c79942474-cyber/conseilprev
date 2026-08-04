# -*- coding: utf-8 -*-
"""Veille de disponibilité du site institutionnel i-aes.com, et bascule.

CE QUE CE MODULE PERMET, ET CE QU'IL NE PEUT PAS PERMETTRE

Il faut le dire avant tout le reste, parce que c'est la limite qui décide de
l'architecture : **une bascule hébergée sur i-aes.com ne peut pas s'exécuter
quand i-aes.com est hors ligne.** Si le DNS ne résout plus ou si l'hébergeur ne
répond pas, aucun script, aucune redirection, aucune règle de serveur venue de
ce domaine ne tourne — le visiteur voit la page d'erreur de son navigateur.

Trois niveaux existent, et un seul couvre le cas total :

  1. BASCULE DNS chez le registrar (enregistrement de secours, ou service de
     failover). C'est le SEUL mécanisme qui fonctionne pour un visiteur qui
     tape i-aes.com pour la première fois pendant la panne. Il ne se code pas
     ici : il se configure chez le bureau d'enregistrement.

  2. AGENT DE SERVICE (service worker) installé depuis i-aes.com lors d'une
     visite antérieure. Il survit à la panne de l'origine et peut rediriger les
     visiteurs DÉJÀ VENUS. Le fichier est fourni par ce module — voir
     `artefact_service_worker()` — mais il doit être déposé sur i-aes.com.

  3. CE QUE NOUS CONTRÔLONS VRAIMENT : nos propres pages. Elles pointent vers
     i-aes.com dans chaque pied de page et y chargent le logo. Quand le site
     institutionnel tombe, ce sont NOS pages qui affichent un lien mort et une
     image cassée. C'est ce que ce module corrige, et c'est déjà beaucoup :
     l'indisponibilité d'un tiers ne doit pas dégrader notre propre service.

CE QUE VAUT NOTRE SONDE

Une sonde depuis NOTRE serveur dit que le site est injoignable DEPUIS CHEZ
NOUS. Ce n'est pas la même chose qu'une panne mondiale : une règle de pare-feu,
un blocage géographique ou une coupure réseau intermédiaire produisent le même
verdict. L'état publié le dit, et l'historique permet de distinguer un incident
d'un aléa — un point isolé n'est pas une panne, dix points d'affilée en sont une.

DICT

  Disponibilité — la bascule, et surtout le fait que notre service ne dépende
                  plus de la disponibilité d'un tiers.
  Intégrité     — la sonde ne modifie rien : requête HEAD, jamais de GET
                  d'écriture, jamais de suivi de redirection vers un tiers
                  inconnu.
  Confidentialité — aucune donnée de visiteur ne quitte le site. La sonde part
                  du serveur, pas du navigateur du lecteur, et le relevé ne
                  contient ni adresse IP ni identifiant.
  Traçabilité   — chaque sonde est horodatée et conservée, avec son code et sa
                  latence. Une bascule sans journal est une bascule que
                  personne ne peut expliquer après coup.
"""
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

VERSION = "2026-08-a"

CIBLE = {
    "domaine": "i-aes.com",
    "url": "https://i-aes.com/",
    "role": "site institutionnel CONSEILPREV — ERSIA IA MANAGEMENT",
    "logo": "https://i-aes.com/wp-content/uploads/2026/02/LOGOv3.jpg",
}

RELAIS = {
    "url": "https://conseilprev.onrender.com/sentinel",
    "chemin": "/sentinel",
    "nom": "Sentinel — plateforme de gouvernance de l'IA",
}

# Une sonde doit être COURTE. Un délai de garde généreux transformerait une
# lenteur du site distant en lenteur de nos propres pages, ce qui reviendrait à
# importer chez nous la panne que l'on cherche à contenir.
DELAI_S = 4.0
TTL_S = 120          # on ne resonde pas plus d'une fois toutes les deux minutes
HISTORIQUE_MAX = 120  # environ quatre heures à ce rythme
SEUIL_PANNE = 3       # trois échecs consécutifs avant de parler de panne

_ETAT = {"ts": 0.0, "dernier": None}
_HISTO = []
_VERROU = threading.Lock()


def _maintenant():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sonder(url=None, delai=None):
    """Une sonde, une seule, sans cache. Renvoie le relevé brut.

    HEAD et non GET : on veut savoir si le serveur répond, pas télécharger la
    page d'accueil d'un site WordPress à chaque vérification. Les redirections
    ne sont pas suivies — un 301 est une réponse valide, et suivre une chaîne
    de redirections vers un hôte inconnu ferait sortir la sonde de son objet."""
    url = url or CIBLE["url"]
    delai = DELAI_S if delai is None else float(delai)

    class _SansRedirection(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    ouvreur = urllib.request.build_opener(_SansRedirection)
    req = urllib.request.Request(url, method="HEAD", headers={
        "User-Agent": "CONSEILPREV-veille/1.0 (+https://conseilprev.onrender.com)",
        "Accept": "*/*",
    })
    t0 = time.time()
    try:
        with ouvreur.open(req, timeout=delai) as rep:
            code = rep.status
        return {"joignable": True, "code": code, "latence_ms": int((time.time() - t0) * 1000),
                "erreur": None, "verifie_le": _maintenant(), "url": url}
    except urllib.error.HTTPError as e:
        # Un 404 ou un 500 sont des RÉPONSES : le serveur est debout. Seul un
        # 5xx durable mérite d'être compté comme indisponibilité, et c'est le
        # verdict, pas la sonde, qui en décide.
        return {"joignable": True, "code": e.code,
                "latence_ms": int((time.time() - t0) * 1000),
                "erreur": "HTTP %s" % e.code, "verifie_le": _maintenant(), "url": url}
    except Exception as e:  # noqa: BLE001
        return {"joignable": False, "code": None,
                "latence_ms": int((time.time() - t0) * 1000),
                "erreur": type(e).__name__ + (": " + str(e)[:120] if str(e) else ""),
                "verifie_le": _maintenant(), "url": url}


def _verdict(releve):
    """Debout, dégradé ou injoignable — et jamais « en panne » sur un seul point.

    Un relevé isolé ne prouve rien : un paquet perdu, une seconde de latence
    réseau, un redémarrage d'hébergeur donnent le même résultat qu'une panne.
    Il faut SEUIL_PANNE échecs consécutifs pour que le mot soit employé."""
    recents = [x for x in _HISTO[-SEUIL_PANNE:]]
    echecs = len([x for x in recents if not x.get("joignable")])
    if releve.get("joignable"):
        code = releve.get("code") or 0
        if 500 <= code < 600:
            return "degrade", ("le serveur répond mais renvoie une erreur %s : le site est "
                               "debout, son application ne l'est pas" % code)
        return "debout", "le serveur répond en %s ms" % releve.get("latence_ms")
    if echecs >= SEUIL_PANNE and len(recents) >= SEUIL_PANNE:
        return "injoignable", ("%d sondes consécutives sans réponse depuis notre serveur — "
                               "l'indisponibilité est constatée, pas supposée" % echecs)
    return "incertain", ("une sonde sans réponse ne suffit pas à conclure : il en faut %d "
                         "consécutives. Un paquet perdu produit le même relevé qu'une panne."
                         % SEUIL_PANNE)


def etat(force=False):
    """L'état courant, mis en cache. Ne bloque jamais plus que le délai de garde,
    et ne resonde pas plus d'une fois par TTL : une page qui interrogerait le
    site distant à chaque affichage lui infligerait notre propre trafic."""
    with _VERROU:
        frais = (time.time() - _ETAT["ts"]) < TTL_S
        if _ETAT["dernier"] and frais and not force:
            base = dict(_ETAT["dernier"])
            base["cache"] = True
            return base
    releve = sonder()
    with _VERROU:
        _HISTO.append(releve)
        del _HISTO[:-HISTORIQUE_MAX]
        etiquette, motif = _verdict(releve)
        out = {
            "version": VERSION,
            "cible": CIBLE,
            "relais": RELAIS,
            "releve": releve,
            "verdict": etiquette,
            "motif": motif,
            "bascule": etiquette == "injoignable",
            "sondes_conservees": len(_HISTO),
            "seuil_panne": SEUIL_PANNE,
            "cache": False,
            "portee": ("Ce verdict vaut DEPUIS NOTRE SERVEUR. Un blocage réseau "
                       "intermédiaire, une règle de pare-feu ou un filtrage géographique "
                       "produiraient le même relevé qu'une panne réelle : c'est un "
                       "indicateur d'exploitation, pas un constat opposable."),
        }
        _ETAT["ts"], _ETAT["dernier"] = time.time(), out
    return out


def historique(n=30):
    """Les n derniers relevés, du plus récent au plus ancien. C'est la seule
    façon de distinguer un incident d'un aléa après coup — une bascule sans
    journal est une bascule que personne ne peut expliquer."""
    n = max(1, min(HISTORIQUE_MAX, int(n or 30)))
    with _VERROU:
        recents = list(reversed(_HISTO[-n:]))
    joignables = len([x for x in recents if x.get("joignable")])
    return {
        "version": VERSION,
        "releves": recents,
        "total": len(recents),
        "joignables": joignables,
        "disponibilite_pct": (round(100.0 * joignables / len(recents), 1) if recents else None),
        "note": ("Taux calculé sur les sondes CONSERVÉES EN MÉMOIRE, pas depuis le début "
                 "du service : un redémarrage de l'application remet ce compteur à zéro. "
                 "Il indique une tendance récente, il ne vaut pas engagement de niveau "
                 "de service."),
    }


# ═══════════════════════════════════════════════════════════════════════════
# L'ARTEFACT À DÉPOSER SUR i-aes.com
#
# Ce module ne peut pas l'installer : il vit dans l'autre sens. Il le PRODUIT,
# pour que la mise en place ne dépende pas de la réécriture manuelle d'un
# fichier que personne ne relira.
# ═══════════════════════════════════════════════════════════════════════════

def artefact_service_worker():
    """Agent de service à déposer à la RACINE de i-aes.com.

    Il ne sert que les visiteurs DÉJÀ VENUS une fois pendant que le site
    fonctionnait : c'est sa force — il survit à la panne de son origine — et
    sa limite, qu'il faut énoncer plutôt que laisser découvrir."""
    return """/* Bascule de secours CONSEILPREV — a deposer a la RACINE de i-aes.com,
   sous le nom sw.js, et a enregistrer depuis chaque page :

     <script>
       if ('serviceWorker' in navigator) {
         navigator.serviceWorker.register('/sw.js');
       }
     </script>

   CE QU'IL FAIT. Une fois installe, cet agent survit a la panne de son propre
   site : le navigateur le garde. Quand une navigation vers i-aes.com echoue —
   serveur injoignable, erreur reseau — il repond a la place et emmene le
   visiteur sur %(relais)s.

   CE QU'IL NE FAIT PAS. Il ne sert QUE les visiteurs deja venus pendant que le
   site fonctionnait. Un visiteur qui tape i-aes.com pour la premiere fois
   pendant la panne n'a rien d'installe : son navigateur affichera sa page
   d'erreur. Seule une bascule DNS chez le bureau d'enregistrement couvre ce
   cas-la, et elle ne se code pas.

   IL NE TOUCHE A RIEN QUAND TOUT VA BIEN : aucune mise en cache, aucune
   interception des reponses valides. Il n'intervient qu'a l'echec. */
var RELAIS = '%(relais)s';

self.addEventListener('install', function (e) { self.skipWaiting(); });
self.addEventListener('activate', function (e) { e.waitUntil(self.clients.claim()); });

self.addEventListener('fetch', function (e) {
  /* Seules les NAVIGATIONS sont concernees. Rediriger une image ou une feuille
     de style vers une autre origine ne repare rien et casse la page. */
  if (e.request.mode !== 'navigate') return;
  e.respondWith(
    fetch(e.request).catch(function () {
      return Response.redirect(RELAIS + '?bascule=sw&depuis=i-aes.com', 302);
    })
  );
});
""" % {"relais": RELAIS["url"]}


def artefact_page_secours():
    """Page HTML autonome de secours, à héberger AILLEURS que sur i-aes.com —
    typiquement chez le registrar, ou sur un hébergeur statique tiers. Elle sert
    de cible à une bascule DNS : sans elle, la bascule n'aurait nulle part où
    envoyer les visiteurs."""
    return """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CONSEILPREV — service temporairement indisponible</title>
<meta name="robots" content="noindex">
<style>
  body{margin:0;font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
       background:#0A2230;color:#E9EEF2;display:grid;place-items:center;min-height:100vh;padding:24px}
  main{max-width:560px}
  h1{font-size:22px;margin:0 0 12px;color:#fff}
  p{margin:0 0 14px;color:#C7D2DA}
  a.b{display:inline-block;margin-top:8px;background:#0E6D7C;color:#fff;text-decoration:none;
      padding:11px 20px;border-radius:6px;font-weight:600}
  .n{font-size:13px;color:#8FA3AF;margin-top:20px}
</style>
</head>
<body>
<main>
  <h1>Le site institutionnel est momentan\u00e9ment indisponible</h1>
  <p>La plateforme <b>Sentinel</b> et l'ensemble des modules de conformit\u00e9 restent
  accessibles : ils sont h\u00e9berg\u00e9s s\u00e9par\u00e9ment et ne d\u00e9pendent pas de ce site.</p>
  <a class="b" href="%(relais)s?bascule=dns&amp;depuis=i-aes.com">Acc\u00e9der \u00e0 Sentinel</a>
  <p class="n">Vous \u00eates arriv\u00e9 ici parce que %(domaine)s ne r\u00e9pond pas. Cette page est
  servie par une bascule de secours, ind\u00e9pendante de l'h\u00e9bergement du site principal.
  Contact : contact@i-aes.com</p>
</main>
</body>
</html>
""" % {"relais": RELAIS["url"], "domaine": CIBLE["domaine"]}


def consignes():
    """Ce qu'il reste à faire À LA MAIN, et par qui. Un module qui prétendrait
    couvrir seul une bascule de domaine mentirait sur son propre périmètre."""
    return [
        {"niveau": 1, "porte": "bureau d'enregistrement du domaine",
         "quoi": "Bascule DNS de secours sur %s" % CIBLE["domaine"],
         "pourquoi": "C'est le SEUL mécanisme qui couvre un visiteur arrivant pendant la "
                     "panne sans être jamais venu. Aucun code hébergé sur le domaine en "
                     "panne ne peut le remplacer.",
         "comment": "Activer le failover DNS du registrar, ou pointer un enregistrement de "
                    "secours vers la page fournie par artefact_page_secours(), hébergée "
                    "hors de l'infrastructure d'i-aes.com.",
         "fait_par": "administrateur du domaine", "automatisable_ici": False},
        {"niveau": 2, "porte": "i-aes.com (WordPress)",
         "quoi": "Déposer sw.js à la racine et l'enregistrer depuis les pages",
         "pourquoi": "Couvre les visiteurs déjà venus : l'agent de service survit à la "
                     "panne de son origine.",
         "comment": "Fichier fourni par artefact_service_worker(), téléchargeable depuis "
                    "/api/veille-iaes/artefact/sw.js.",
         "fait_par": "administrateur du site institutionnel", "automatisable_ici": False},
        {"niveau": 3, "porte": "conseilprev (ce site)",
         "quoi": "Ne plus dépendre de la disponibilité d'i-aes.com",
         "pourquoi": "Quand le site institutionnel tombe, ce sont NOS pages qui affichent "
                     "un lien mort et une image cassée. L'indisponibilité d'un tiers ne "
                     "doit pas dégrader notre propre service.",
         "comment": "Fait : sonde serveur, bascule des liens du pied de page vers Sentinel, "
                    "page d'accueil de bascule, et journal des relevés.",
         "fait_par": "ce module", "automatisable_ici": True},
    ]


def sante():
    with _VERROU:
        n = len(_HISTO)
        dernier = _HISTO[-1] if _HISTO else None
    return {"module": "veille_iaes", "version": VERSION,
            "cible": CIBLE["domaine"], "relais": RELAIS["chemin"],
            "sondes_en_memoire": n, "seuil_panne": SEUIL_PANNE,
            "ttl_s": TTL_S, "delai_garde_s": DELAI_S,
            "dernier_verdict": (_verdict(dernier)[0] if dernier else "aucune sonde"),
            "horodatage": _maintenant()}
