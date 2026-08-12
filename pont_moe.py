# -*- coding: utf-8 -*-
"""Le pont vers le chiffrage de maîtrise d'œuvre — et ce qu'il assume de porter.

CE QUE CE MODULE RÉSOUT

L'étude d'enveloppe répond à « combien coûte l'ouvrage ». Le bloc « Le prix de
la maîtrise d'œuvre » de conseilprevcyber répond à « combien coûte de le faire
concevoir et suivre ». Le second se calcule SUR le premier — et il fallait
jusqu'ici retaper le montant à la main, puis retaper la part du lot technique,
sans laquelle le barème retombe sur une hypothèse à 70 %.

Retaper, c'est se tromper. Et se tromper ici coûte cher : sur un centre de
données, le partage clos-couvert / technique déplace les honoraires davantage
que n'importe quel taux du barème, parce que les taux y sont inversés entre les
deux assiettes.

POURQUOI UN SECOND PONT, ET PAS UN PARAMÈTRE DE PLUS SUR LE PREMIER

`pont_dc` conduit à l'étude de durabilité et jure de ne porter AUCUN MONTANT :
c'est vrai, c'est nécessaire là-bas — un bilan carbone n'a aucun besoin du
budget — et cette promesse est écrite pour être vérifiable. Ce pont-ci porte
un montant, parce que c'est précisément ce qu'on lui demande de transporter.
Deux destinations, deux contrats : greffer les montants sur le premier
transformerait sa promesse en mensonge, et un lecteur qui a lu « aucun
montant » ne relit jamais.

CE QUE CE PONT PORTE — ET CE QUE CELA IMPLIQUE

Il porte l'ASSIETTE DE TRAVAUX, la part du lot technique et le code du pays.
Un montant dans une URL, c'est un montant qui part dans un courriel, dans un
historique de navigateur et dans les journaux des serveurs traversés. Trois
précautions, et elles ne sont pas décoratives :

  · le montant est ARRONDI À LA CENTAINE DE MILLIERS D'EUROS. Une enveloppe au
    millier près se recoupe avec un devis ; une fourchette arrondie est un
    ordre de grandeur, ce qui est exactement ce que le barème sait exploiter ;
  · RIEN DE NOMINATIF ne voyage — ni client, ni projet, ni site, ni session.
    Un montant seul ne désigne personne ; un montant avec un nom, si ;
  · LE CLIENT VOIT LE LIEN AVANT DE LE SUIVRE. Ce module fabrique l'adresse et
    dit ce qu'elle contient. Il ne l'ouvre pas, ne la raccourcit pas, ne la
    transmet à personne.

LE PAYS VOYAGE POUR ÊTRE DIT, PAS POUR ÊTRE CALCULÉ

Le barème d'honoraires ne varie pas d'un pays à l'autre : il est établi sur un
programme français et le module de destination le dit. Le code pays sert à
RAPPELER de quelle étude vient le montant — pas à moduler quoi que ce soit.
Laisser croire l'inverse ferait lire une précision qui n'existe pas.
"""

VERSION = "2026-08-a"

# La cible. En dur, comme pour l'autre pont : une adresse déduite de l'en-tête
# Host suivrait le visiteur, et un lien fabriqué en recette pointerait sur la
# recette.
BASE = "https://conseilprevcyber.onrender.com"
CHEMIN = "/ingenierie-datacenter"
ANCRE = "ig-moe"          # la section « Le prix de la maîtrise d'œuvre »

# L'arrondi du montant, en millions d'euros. 0,1 M€ = cent mille euros : assez
# fin pour que le chiffrage garde son sens, assez grossier pour qu'une URL
# partagée ne vaille pas un devis.
PAS_ARRONDI_MEUR = 0.1

# LE CONTRAT. Chaque clé est le nom d'un paramètre lu par l'AUTRE site. Écrits
# à la main dans une page, ces noms divergent au premier renommage — et le lien
# continue de fonctionner sans rien pré-remplir, ce qui est la pire des pannes :
# silencieuse. Ils sont donc tenus ici, et un test les fige.
CHAMPS = {
    "travaux_meur": {
        "nom": "Montant des travaux",
        "unite": "M€, fourchette « bas-haut »",
        "de": "l'assiette de l'étude d'enveloppe — enveloppe diminuée de la "
              "ligne de maîtrise d'œuvre et de la provision pour aléas",
        "bornes": (0.1, 100_000.0),
    },
    "part_technique": {
        "nom": "Part du lot technique",
        "unite": "% de l'assiette",
        "de": "la décomposition par lot (DPGF) de l'étude d'enveloppe",
        "bornes": (0.0, 100.0),
    },
    "pays": {
        "nom": "Pays de l'étude",
        "unite": "code à deux lettres",
        "de": "le pays retenu au classement par coût total de possession",
        "bornes": None,
    },
}

# Ce que le lien NE porte PAS. À lire avant de cliquer — c'est le sens de la
# liste, pas une formalité.
EXCLUS = [
    "Aucun nom de client, de société ou de projet.",
    "Aucun nom de site, aucune adresse, aucune coordonnée.",
    "Aucun identifiant de session : le lien n'ouvre aucun compte.",
    "Aucun détail de la décomposition : ni les quatorze lots, ni les écarts "
    "entre pays, ni le coût total de possession.",
]

# Et ce qu'il porte, dit en toutes lettres au même endroit — une liste
# d'exclusions sans sa contrepartie se lit comme « rien ne sort ».
PORTE_AVERTISSEMENT = (
    "Ce lien contient un MONTANT (l'assiette de travaux, arrondie à la "
    "centaine de milliers d'euros). Une adresse se recopie dans un courriel et "
    "s'inscrit dans les journaux des serveurs qu'elle traverse : ne la "
    "partagez qu'avec les destinataires de l'étude."
)


def _verifier():
    fautes = []
    if not BASE.startswith("https://"):
        fautes.append("la cible doit etre en https")
    if not ANCRE:
        fautes.append("ancre de section manquante")
    if PAS_ARRONDI_MEUR <= 0:
        fautes.append("le pas d'arrondi doit etre positif")
    for cle, c in CHAMPS.items():
        for k in ("nom", "unite", "de"):
            if not (c.get(k) or "").strip():
                fautes.append("champ %s : %s manquant" % (cle, k))
        b = c.get("bornes")
        if b is not None and not (isinstance(b, tuple) and len(b) == 2
                                  and b[0] < b[1]):
            fautes.append("champ %s : bornes incoherentes" % cle)
    if not EXCLUS:
        fautes.append("la liste de ce que le lien ne porte pas est vide")
    if "MONTANT" not in PORTE_AVERTISSEMENT:
        fautes.append("l'avertissement doit nommer le montant qu'il transporte")
    return fautes


_FAUTES = _verifier()
if _FAUTES:
    raise RuntimeError("pont_moe — contrat incoherent : " + " ; ".join(_FAUTES))


def _encoder(v):
    """Encodage minimal, sans dependance : les valeurs transmises sont des
    nombres, des codes pays et un tiret. Tout caractere hors de cet alphabet
    signale qu'on transmet autre chose que prevu."""
    out = []
    for ch in str(v):
        if ch.isalnum() or ch in "._-":
            out.append(ch)
        else:
            out.append("%%%02X" % ord(ch))
    return "".join(out)


def _arrondir(x):
    """Arrondi au pas, vers le pas le plus proche. Rend un float propre."""
    n = round(float(x) / PAS_ARRONDI_MEUR)
    return round(n * PAS_ARRONDI_MEUR, 6)


def lien(travaux_meur=None, part_technique=None, pays=None):
    """Construit le lien vers le chiffrage de MOE, et dit ce qu'il porte.

    `travaux_meur` : [bas, haut] ou un nombre — l'ASSIETTE, pas l'enveloppe.
    `part_technique` : fraction (0-1) ou pourcentage (>1), normalisee ici.
    `pays` : code a deux lettres.

    Rend toujours un resultat lisible. Un parametre refuse ne fait pas echouer
    le lien : il en sort ET il est nomme. Un lien qui echoue en bloc parce
    qu'une valeur sur trois est douteuse prive le client des deux autres ; un
    lien qui laisse tomber une valeur en silence le fait calculer sur un profil
    qu'il croit avoir transmis.
    """
    porte, refuses, params = [], [], {}

    if travaux_meur not in (None, "", []):
        c = CHAMPS["travaux_meur"]
        v = travaux_meur if isinstance(travaux_meur, (list, tuple)) \
            else [travaux_meur, travaux_meur]
        try:
            bas, haut = _arrondir(v[0]), _arrondir(v[-1])
        except (TypeError, ValueError, IndexError):
            bas = haut = None
            refuses.append({"champ": c["nom"], "valeur": str(travaux_meur),
                            "motif": "montant illisible"})
        if bas is not None:
            if bas > haut:
                bas, haut = haut, bas
            lo, hi = c["bornes"]
            if not (lo <= bas <= hi and lo <= haut <= hi):
                refuses.append({
                    "champ": c["nom"], "valeur": "%g – %g M€" % (bas, haut),
                    "motif": "hors des bornes transmissibles (%g a %g M€)"
                             % (lo, hi)})
            else:
                params["travaux_meur"] = ("%g" % bas if bas == haut
                                          else "%g-%g" % (bas, haut))
                porte.append({
                    "champ": c["nom"],
                    "valeur": ("%g M€" % bas if bas == haut
                               else "%g – %g M€" % (bas, haut)),
                    "de": c["de"],
                    "reserve": "arrondi à %g M€ près" % PAS_ARRONDI_MEUR})

    if part_technique not in (None, ""):
        c = CHAMPS["part_technique"]
        try:
            pt = float(part_technique)
        except (TypeError, ValueError):
            pt = None
            refuses.append({"champ": c["nom"], "valeur": str(part_technique),
                            "motif": "part illisible"})
        if pt is not None:
            # FRACTION OU POURCENTAGE : les deux circulent dans ce dépôt, et
            # les confondre multiplie l'assiette technique par cent. On
            # normalise sur la seule règle qui ne se devine pas : une part de
            # lot est au plus 1 quand elle est une fraction.
            pct = pt * 100.0 if pt <= 1.0 else pt
            lo, hi = c["bornes"]
            if not (lo <= pct <= hi):
                refuses.append({"champ": c["nom"], "valeur": str(part_technique),
                                "motif": "une part se situe entre %g et %g %%"
                                         % (lo, hi)})
            else:
                params["part_technique"] = "%.1f" % pct
                porte.append({"champ": c["nom"],
                              "valeur": "%.1f %%" % pct, "de": c["de"]})

    if pays:
        p = str(pays).strip().upper()
        if len(p) != 2 or not p.isalpha():
            refuses.append({"champ": CHAMPS["pays"]["nom"], "valeur": str(pays),
                            "motif": "un code pays s'ecrit en deux lettres"})
        else:
            params["pays"] = p
            porte.append({"champ": CHAMPS["pays"]["nom"], "valeur": p,
                          "de": CHAMPS["pays"]["de"],
                          "reserve": "pour mémoire : le barème d'honoraires ne "
                                     "varie pas d'un pays à l'autre"})

    q = "&".join("%s=%s" % (k, _encoder(v)) for k, v in sorted(params.items()))
    url = BASE + CHEMIN + (("?" + q) if q else "") + "#" + ANCRE
    return {"ok": True, "version": VERSION, "url": url,
            "porte": porte, "refuses": refuses,
            "exclus": list(EXCLUS), "avertissement": PORTE_AVERTISSEMENT,
            "vide": not params}


def referentiel():
    """Le contrat, pour qu'il soit lisible sans lire le code."""
    return {"version": VERSION, "base": BASE, "chemin": CHEMIN, "ancre": ANCRE,
            "champs": CHAMPS, "exclus": list(EXCLUS),
            "avertissement": PORTE_AVERTISSEMENT,
            "pas_arrondi_meur": PAS_ARRONDI_MEUR}
