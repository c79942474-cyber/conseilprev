"""LE CLASSEUR — vos documents, et ce que ce site en fait exactement.

CE MODULE ROMPT UNE PROMESSE, ET C'EST POURQUOI IL LA REMPLACE PAR UNE AUTRE.
La page de confrontation écrit, en toutes lettres : « Ce que devient votre
document. Rien. Il est lu en mémoire, confronté, puis jeté avec la requête.
Aucune copie n'est écrite sur disque. » Cette phrase reste vraie de la
CONFRONTATION — et elle le reste parce qu'elle a été amendée le jour où ce
classeur est apparu, au lieu d'être laissée à mentir par omission.

Ranger un document est un ACTE DÉLIBÉRÉ, distinct de le confronter. Il faut
donc dire, à l'endroit où on le pose, ce qu'il devient — et le dire avec la
même précision qu'ailleurs.

CE QUE LE CLASSEUR CONSERVE, ET OÙ.

  · EN MÉMOIRE DU SERVEUR, comme les comptes eux-mêmes (`abonnes.py` tient
    `_COMPTES` dans un dictionnaire). Rien n'est écrit sur disque, rien n'est
    envoyé ailleurs, aucun tiers n'y accède.
  · DONC : UN REDÉMARRAGE EFFACE TOUT. C'est vrai des comptes depuis le
    premier jour ; ce l'est du classeur pour la même raison. L'hébergement
    actuel redémarre à chaque mise en ligne et après une période sans visite.
    CE N'EST PAS UN COFFRE. Un espace qui perdrait des documents en silence
    serait pire que pas d'espace du tout : la page le dit avant le dépôt, pas
    après.
  · CLOISONNÉ PAR COMPTE. Un document n'est lisible que par le jeton de
    session du compte qui l'a déposé. Aucune fonction de ce module ne prend un
    identifiant de document sans prendre aussi le compte.

CE QU'IL NE FAIT PAS. Il n'ouvre pas vos documents, ne les indexe pas, ne les
lit pas — sauf si vous demandez explicitement une confrontation, qui reste
l'opération décrite sur sa propre page. Il ne les partage pas, ne produit
aucun aperçu, et ne déduit rien de leurs noms.

POURQUOI DES PLAFONDS. Sans eux, un seul dépôt suffirait à épuiser la mémoire
d'un serveur partagé et à faire tomber le site pour tout le monde — un
refus poli vaut mieux qu'une panne générale.
"""
import hashlib
import re
import secrets
import threading
from datetime import datetime, timezone

VERSION = "2026.08.23"

# ── LES PLAFONDS, ET CE QU'ILS PROTÈGENT ─────────────────────────────────
# Ils sont écrits ici, servis à l'écran, et vérifiés par les contrôles : un
# plafond qu'on découvre au refus est une mauvaise surprise, un plafond
# annoncé est une contrainte.
OCTETS_PAR_DOCUMENT = 8 * 1024 * 1024      # 8 Mio
OCTETS_PAR_COMPTE = 40 * 1024 * 1024       # 40 Mio
DOCUMENTS_PAR_COMPTE = 30
# LE PLAFOND GLOBAL EXISTE PARCE QUE LA MÉMOIRE EST PARTAGÉE. L'instance
# gratuite dispose d'un demi-gigaoctet pour TOUT le site, corpus compris ;
# sans cette borne, trois comptes suffiraient à la faire tomber.
OCTETS_AU_TOTAL = 120 * 1024 * 1024        # 120 Mio

# Les formats acceptés. La liste est courte À DESSEIN : ce classeur range des
# documents de travail, il n'est pas un hébergement de fichiers. Accepter tout
# et n'importe quoi transformerait un service du cabinet en dépôt anonyme.
FORMATS = {
    ".txt": "text/plain", ".md": "text/markdown", ".csv": "text/csv",
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument."
             "wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument."
             "spreadsheetml.sheet",
    ".pptx": "application/vnd.openxmlformats-officedocument."
             "presentationml.presentation",
    ".odt": "application/vnd.oasis.opendocument.text",
}

_VERROU = threading.Lock()
# {courriel: [ {id, nom, ext, octets, empreinte, depose_le, octets_bruts}, … ]}
_RANGES = {}


def _maintenant():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _extension(nom):
    m = re.search(r"(\.[A-Za-z0-9]{1,5})$", str(nom or ""))
    return (m.group(1).lower() if m else "")


def _nom_propre(nom):
    """Le nom d'origine, débarrassé de ce qui n'a rien à faire dans un nom.

    UN NOM DE FICHIER EST UNE ENTRÉE D'UTILISATEUR, et il est réaffiché : sans
    nettoyage il porterait des chemins (`..\\..\\`), des retours à la ligne qui
    cassent l'affichage, ou du balisage. Le nom est conservé pour que le
    déposant retrouve son document — pas pour être exécuté.
    """
    n = str(nom or "document")
    n = n.replace("\\", "/").split("/")[-1]        # jamais de chemin
    n = re.sub(r"[\x00-\x1f\x7f]", "", n)          # jamais de caractère de contrôle
    n = n.strip() or "document"
    return n[:120]


def _total_global():
    return sum(d["octets"] for l in _RANGES.values() for d in l)


def deposer(courriel, nom, octets):
    """Range un document. Rend `{ok, document}` ou `{ok: False, …}`.

    CHAQUE REFUS DIT SA RAISON ET SON PLAFOND. « Dépôt impossible » oblige à
    deviner, et l'on devine toujours mal : on réessaie avec le même fichier.
    """
    if not courriel:
        return {"ok": False, "erreur": "hors_compte",
                "message": "Le classeur n'existe que pour un compte : ce que "
                           "vous rangez n'est lisible que par lui."}
    nom = _nom_propre(nom)
    ext = _extension(nom)
    if ext not in FORMATS:
        return {"ok": False, "erreur": "format_refuse",
                "message": "Format non rangé : %s. Ce classeur accepte %s — "
                           "c'est un classeur de documents de travail, pas un "
                           "hébergement de fichiers."
                           % (ext or "aucune extension",
                              ", ".join(sorted(FORMATS)))}
    if not octets:
        return {"ok": False, "erreur": "vide",
                "message": "Ce fichier est vide."}
    if len(octets) > OCTETS_PAR_DOCUMENT:
        return {"ok": False, "erreur": "trop_gros",
                "message": "Ce document pèse %.1f Mio ; le plafond est de "
                           "%d Mio par document."
                           % (len(octets) / 1048576.0,
                              OCTETS_PAR_DOCUMENT // 1048576)}

    with _VERROU:
        siens = _RANGES.setdefault(courriel, [])
        if len(siens) >= DOCUMENTS_PAR_COMPTE:
            return {"ok": False, "erreur": "trop_nombreux",
                    "message": "Votre classeur contient déjà %d documents, "
                               "c'est le plafond. Effacez-en un pour en "
                               "ranger un autre."
                               % DOCUMENTS_PAR_COMPTE}
        deja = sum(d["octets"] for d in siens)
        if deja + len(octets) > OCTETS_PAR_COMPTE:
            return {"ok": False, "erreur": "compte_plein",
                    "message": "Votre classeur atteindrait %.1f Mio ; le "
                               "plafond est de %d Mio par compte."
                               % ((deja + len(octets)) / 1048576.0,
                                  OCTETS_PAR_COMPTE // 1048576)}
        if _total_global() + len(octets) > OCTETS_AU_TOTAL:
            # LE REFUS NOMME LA VRAIE CAUSE. « Réessayez plus tard » ferait
            # croire à une panne passagère alors que c'est une limite du
            # serveur, et le déposant réessaierait en boucle.
            return {"ok": False, "erreur": "serveur_plein",
                    "message": "La mémoire partagée du serveur est pleine "
                               "(%d Mio au total, tous comptes confondus). "
                               "Ce n'est pas une panne : c'est la borne qui "
                               "empêche un dépôt de faire tomber le site."
                               % (OCTETS_AU_TOTAL // 1048576)}

        # L'EMPREINTE SERT AU DÉPOSANT, PAS AU SITE. Elle lui permet de
        # vérifier que le fichier récupéré est bien celui qu'il a déposé —
        # utile précisément parce que cet espace n'est pas durable.
        d = {
            "id": secrets.token_urlsafe(12),
            "nom": nom, "ext": ext, "type": FORMATS[ext],
            "octets": len(octets),
            "empreinte": hashlib.sha256(octets).hexdigest()[:16],
            "depose_le": _maintenant(),
            "_octets": octets,
        }
        siens.append(d)
    return {"ok": True, "document": _public(d)}


def _public(d):
    """Ce qui sort de ce module. LES OCTETS N'EN SORTENT JAMAIS PAR ICI :
    seule `contenu()` les rend, et elle exige le compte."""
    return {k: v for k, v in d.items() if not k.startswith("_")}


def lister(courriel):
    if not courriel:
        return {"ok": False, "erreur": "hors_compte", "documents": []}
    with _VERROU:
        siens = list(_RANGES.get(courriel) or [])
    octets = sum(d["octets"] for d in siens)
    return {
        "ok": True,
        "documents": [_public(d) for d in
                      sorted(siens, key=lambda x: x["depose_le"], reverse=True)],
        "n": len(siens),
        "octets": octets,
        # LES PLAFONDS SONT SERVIS AVEC LA LISTE, pas seulement au refus. Un
        # plafond qu'on découvre en le heurtant est une mauvaise surprise.
        "plafond_documents": DOCUMENTS_PAR_COMPTE,
        "plafond_octets": OCTETS_PAR_COMPTE,
        "plafond_par_document": OCTETS_PAR_DOCUMENT,
        "formats": sorted(FORMATS),
        "durable": False,
        "dit": ("Ces documents vivent EN MÉMOIRE DU SERVEUR, comme votre "
                "compte : rien n'est écrit sur disque, rien n'est envoyé "
                "ailleurs, et un redémarrage du site les efface. Ce n'est pas "
                "un coffre — gardez l'original chez vous."),
        "dit_en": ("These documents live IN THE SERVER'S MEMORY, like your "
                   "account: nothing is written to disk, nothing is sent "
                   "anywhere, and a restart of the site erases them. This is "
                   "not a vault — keep your own copy."),
    }


def contenu(courriel, ident):
    """Les octets d'un document — et seulement pour le compte qui l'a rangé.

    LE COMPTE EST UN ARGUMENT, PAS UN CONTRÔLE FAIT AILLEURS. Une fonction qui
    prendrait le seul identifiant laisserait la porte à l'appelant, et il
    suffirait d'un chemin d'API oublié pour ouvrir le classeur d'autrui.
    """
    if not courriel:
        return None
    with _VERROU:
        for d in (_RANGES.get(courriel) or []):
            if d["id"] == ident:
                return dict(_public(d), octets_bruts=d["_octets"])
    return None


def effacer(courriel, ident):
    if not courriel:
        return {"ok": False, "erreur": "hors_compte"}
    with _VERROU:
        siens = _RANGES.get(courriel) or []
        for i, d in enumerate(siens):
            if d["id"] == ident:
                siens.pop(i)
                # L'EFFACEMENT EST RÉEL : l'entrée sort de la liste, les
                # octets ne sont plus référencés. Rien n'est marqué
                # « supprimé » tout en restant lisible.
                return {"ok": True, "efface": ident}
    return {"ok": False, "erreur": "introuvable",
            "message": "Aucun document de votre classeur ne porte cet "
                       "identifiant."}


def vider(courriel):
    """Appelé quand un compte est effacé. SANS CELA, LES DOCUMENTS D'UN COMPTE
    SUPPRIMÉ RESTERAIENT EN MÉMOIRE — un compte « effacé » dont les fichiers
    survivent n'est pas effacé."""
    with _VERROU:
        n = len(_RANGES.pop(courriel, []))
    return n


def sante():
    with _VERROU:
        comptes = len(_RANGES)
        docs = sum(len(l) for l in _RANGES.values())
        octets = _total_global()
    return {
        "module": "classeur", "version": VERSION,
        "comptes_avec_documents": comptes,
        "documents": docs, "octets": octets,
        "durable": False,
        "plafond_global_octets": OCTETS_AU_TOTAL,
        "portee": "Range les documents d'un compte EN MÉMOIRE, cloisonnés par "
                  "compte. Rien n'est écrit sur disque : un redémarrage "
                  "efface tout, comme il efface les comptes. Ce n'est pas un "
                  "coffre, et la page le dit avant le dépôt.",
    }
