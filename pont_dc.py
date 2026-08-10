# -*- coding: utf-8 -*-
"""Le pont vers l'étude de durabilité — un lien, et le contrat qui le tient.

CE QUE CE MODULE RÉSOUT

Une étude d'implantation se termine sur deux réponses : QUEL PAYS, et COMBIEN.
Le comparateur pondéré donne le premier, l'enveloppe d'investissement le second.
L'étape suivante — le bilan énergie / eau / carbone et la trajectoire de
décarbonation — se mène sur l'autre site du cabinet, et jusqu'ici il fallait
retaper le profil à la main. Retaper, c'est se tromper : la puissance saisie ici
en mégawatts se ressaisit là-bas en kilowatts, et l'écart d'un facteur mille ne
se voit qu'au résultat.

LE VRAI RISQUE N'EST PAS L'URL, C'EST LE CONTRAT

Les noms des paramètres appartiennent à l'AUTRE site : ce sont les
identifiants de ses champs de formulaire. Écrits à la main dans une page, ils
divergent au premier renommage — et le lien continue de fonctionner, sans rien
pré-remplir. Une panne silencieuse : le visiteur arrive sur un formulaire vide
et croit que le lien n'était qu'un raccourci de navigation.

Ce module tient donc le contrat en un seul endroit, avec ce qu'il faut pour le
vérifier : le nom de chaque champ, son unité, la conversion appliquée, et les
bornes. Un test le fige ; s'il change, il change ici.

CE QUE LE LIEN NE PORTE PAS, ET C'EST DÉLIBÉRÉ

Aucun nom de client, aucun nom de projet, aucun montant, aucun élément qui
désigne une personne ou une affaire. Le profil TECHNIQUE seul — puissance,
pays, famille de refroidissement. Une URL se copie, se colle dans un courriel,
s'enregistre dans un historique de navigateur et se journalise sur les serveurs
qu'elle traverse : ce qu'on y met devient public au premier partage.

C'EST LE CLIENT QUI DÉCIDE. Ce module fabrique le lien ; il ne le suit pas, ne
le raccourcit pas et n'ouvre rien. La page l'affiche, dit ce qu'il porte, et
laisse la main.
"""

VERSION = "2026-08-a"

# La cible. En dur et non déduite : une adresse construite depuis l'en-tête
# Host suivrait le visiteur, et un lien fabriqué derrière un proxy ou un
# environnement de recette pointerait vers cet environnement-là.
BASE = "https://conseilprevcyber.onrender.com"
CHEMIN = "/datacenter"

# LE CONTRAT. Chaque clé est l'identifiant d'un champ du formulaire de l'autre
# site — pas un nom choisi ici. `de` dit d'où vient la valeur dans NOTRE étude,
# `facteur` la conversion à appliquer, `bornes` ce qu'on refuse de transmettre.
CHAMPS = {
    "puissance_it_kw": {
        "nom": "Puissance informatique installée",
        "unite": "kW",
        "de": "la puissance en MW de l'enveloppe d'investissement",
        "facteur": 1000.0,          # MW → kW
        "bornes": (100.0, 2_000_000.0),
    },
    "pays": {
        "nom": "Pays d'implantation",
        "unite": "code à deux lettres",
        "de": "le pays retenu au comparateur pondéré, ou le premier du "
              "classement par coût total de possession",
        "facteur": None,
        "bornes": None,
    },
    "refroidissement": {
        "nom": "Famille de refroidissement",
        "unite": "clé de famille",
        "de": "le mode de refroidissement retenu à la conception",
        "facteur": None,
        "bornes": None,
    },
}

# Les voies de l'autre site. Le lien en désigne une : arriver sur la page sans
# voie choisie oblige le lecteur à deviner par où commencer, et il commence
# rarement par la bonne.
VOIES = {
    "inventaire": "Compter et déclarer — périmètre, année de référence, "
                  "inventaire, indicateurs, déclaration européenne, vérification",
    "trajectoire": "Réduire — éviter, réduire, substituer, puis le résiduel",
}
VOIE_DEFAUT = "inventaire"

# Ce que le lien NE porte PAS. Écrit noir sur blanc parce que c'est ce que le
# client doit pouvoir vérifier avant de cliquer.
EXCLUS = [
    "Aucun nom de client, de société ou de projet.",
    "Aucun montant : ni enveloppe, ni coût total de possession, ni écart entre "
    "pays.",
    "Aucun site nommé, aucune adresse, aucune coordonnée.",
    "Aucun identifiant de session : le lien n'ouvre aucun compte et n'en "
    "réclame aucun.",
]


def _verifier():
    fautes = []
    if not BASE.startswith("https://"):
        fautes.append("la cible doit etre en https")
    for cle, c in CHAMPS.items():
        for k in ("nom", "unite", "de"):
            if not (c.get(k) or "").strip():
                fautes.append("champ %s : %s manquant" % (cle, k))
        b = c.get("bornes")
        if b and not (isinstance(b, tuple) and len(b) == 2 and b[0] < b[1]):
            fautes.append("champ %s : bornes incoherentes" % cle)
        if c.get("facteur") is not None and c["facteur"] <= 0:
            fautes.append("champ %s : facteur nul ou negatif" % cle)
    if VOIE_DEFAUT not in VOIES:
        fautes.append("voie par defaut inconnue")
    if not EXCLUS:
        fautes.append("la liste de ce que le lien ne porte pas est vide")
    return fautes


_FAUTES = _verifier()
if _FAUTES:
    raise RuntimeError("pont_dc — contrat incoherent : " + " ; ".join(_FAUTES))


def _encoder(v):
    """Encodage minimal, sans dependance. Les valeurs transmises sont des
    codes pays, des cles de famille et des nombres : tout caractere hors de cet
    alphabet est le signe qu'on transmet autre chose que prevu, et il est
    refuse plus haut."""
    out = []
    for ch in str(v):
        if ch.isalnum() or ch in "._-":
            out.append(ch)
        else:
            out.append("%%%02X" % ord(ch))
    return "".join(out)


def lien(mw=None, pays=None, refroidissement=None, voie=VOIE_DEFAUT):
    """Construit le lien, et dit ce qu'il porte — ou pourquoi il ne le porte pas.

    Rend toujours un resultat lisible : un parametre refuse ne fait pas echouer
    le lien, il en sort ET il est nomme. Un lien qui echoue en bloc parce qu'une
    valeur sur trois est douteuse prive le client des deux autres.
    """
    porte, refuses = [], []

    if voie not in VOIES:
        refuses.append({"champ": "voie", "valeur": str(voie),
                        "motif": "voie inconnue — « %s » retenue" % VOIE_DEFAUT})
        voie = VOIE_DEFAUT

    params = {}

    if mw not in (None, ""):
        c = CHAMPS["puissance_it_kw"]
        try:
            kw = float(mw) * c["facteur"]
        except (TypeError, ValueError):
            refuses.append({"champ": c["nom"], "valeur": str(mw),
                            "motif": "puissance illisible"})
            kw = None
        if kw is not None:
            bas, haut = c["bornes"]
            if not (bas <= kw <= haut):
                refuses.append({
                    "champ": c["nom"], "valeur": "%s MW" % mw,
                    "motif": "hors des bornes transmissibles (%g a %g kW)"
                             % (bas, haut)})
            else:
                # Entier : une puissance informatique au dixieme de kilowatt
                # donnerait une precision que l'etude d'implantation n'a pas.
                params["puissance_it_kw"] = str(int(round(kw)))
                porte.append({"champ": c["nom"], "valeur": "%s kW"
                              % params["puissance_it_kw"],
                              "de": c["de"]})

    if pays:
        p = str(pays).strip().upper()
        if len(p) != 2 or not p.isalpha():
            refuses.append({"champ": CHAMPS["pays"]["nom"], "valeur": str(pays),
                            "motif": "un code pays s'ecrit en deux lettres"})
        else:
            params["pays"] = p
            porte.append({"champ": CHAMPS["pays"]["nom"], "valeur": p,
                          "de": CHAMPS["pays"]["de"]})

    if refroidissement:
        # Volontairement NON valide contre une liste tenue ici : la liste des
        # familles appartient au moteur de l'autre site, et la recopier
        # garantirait une divergence. C'est LUI qui refusera une cle inconnue,
        # et il le dira au visiteur.
        f = str(refroidissement).strip()
        if not f.replace("_", "").isalnum():
            refuses.append({"champ": CHAMPS["refroidissement"]["nom"],
                            "valeur": f, "motif": "cle de famille inattendue"})
        else:
            params["refroidissement"] = f
            porte.append({"champ": CHAMPS["refroidissement"]["nom"],
                          "valeur": f, "de": CHAMPS["refroidissement"]["de"],
                          "reserve": "La liste des familles appartient au "
                                     "moteur de destination : s'il ne connait "
                                     "pas cette cle, il le dira et laissera le "
                                     "champ tel quel."})

    # L'ancre plutot que la chaine de requete : elle n'est pas transmise au
    # serveur, donc ni journalisee dans ses acces ni envoyee au referent. Pour
    # un profil technique cela change peu ; le principe, lui, se tient.
    frag = "voie=" + _encoder(voie)
    for cle in ("pays", "puissance_it_kw", "refroidissement"):
        if cle in params:
            frag += "&" + cle + "=" + _encoder(params[cle])

    return {
        "url": BASE + CHEMIN + "#" + frag,
        "voie": voie,
        "voie_texte": VOIES[voie],
        "porte": porte,
        "refuses": refuses,
        "exclus": EXCLUS,
        "version": VERSION,
        "note": "Ce lien ouvre l'etude de durabilite sur l'autre site du "
                "cabinet, avec ce profil deja saisi. Il n'ouvre aucun compte "
                "et ne transmet aucune donnee nominative. Le site de "
                "destination affichera ce qu'il a repris, et vous demandera de "
                "le verifier avant de calculer.",
    }


def depuis_devis(reponse, voie=VOIE_DEFAUT, pays=None):
    """Le lien, tire directement d'une reponse de l'enveloppe d'investissement.

    Le pays retenu est, par defaut, le PREMIER DU CLASSEMENT par cout total de
    possession — le seul chiffre qui departage les pays, l'enveloppe
    d'investissement etant identique par construction. Le client peut en
    designer un autre : c'est son arbitrage, pas celui du classement.
    """
    reponse = reponse or {}
    entree = reponse.get("entree") or {}
    classement = reponse.get("classement") or []
    if not pays and classement:
        pays = classement[0].get("pays")
    return lien(mw=entree.get("mw"), pays=pays, voie=voie)


def referentiel():
    """Le contrat, servi tel quel : de quoi montrer au client ce qui voyagera."""
    return {
        "version": VERSION,
        "cible": BASE + CHEMIN,
        "champs": CHAMPS,
        "voies": VOIES,
        "voie_defaut": VOIE_DEFAUT,
        "exclus": EXCLUS,
    }


def sante():
    return {"module": "pont_dc", "version": VERSION,
            "cible": BASE + CHEMIN,
            "champs": len(CHAMPS), "voies": len(VOIES),
            "problemes": _verifier()}
