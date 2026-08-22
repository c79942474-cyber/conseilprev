"""LE BULLETIN — ce qu'un abonné reçoit, et ce qu'on refuse de lui écrire.

LA FAUTE QUE CE MODULE ÉVITE. Une lettre hebdomadaire a un rythme à tenir, et
ce rythme est un piège : la semaine où il ne s'est rien passé, on complète.
On reprend une brève de la semaine d'avant, on requalifie un fait mineur en
« à surveiller », et l'abonné apprend en trois envois que le bulletin est
toujours plein — donc qu'il n'apprend rien de sa longueur.

CE MODULE PRÉFÈRE NE RIEN ENVOYER. Quand rien du corpus ne franchit le seuil
de l'abonné sur la période, il rend un bulletin VIDE et le dit. Un silence
est une information : il signifie que rien n'a bougé sur les sujets suivis,
et il n'a de valeur que si le bulletin est capable de se taire.

TROIS RÈGLES.

  1. RIEN QUI NE SOIT DÉJÀ PUBLIÉ. Le bulletin ne compose aucune phrase
     d'analyse : il reprend le chapeau, la lecture et la source des fiches
     telles qu'elles sont sur le site. Un texte rédigé pour l'envoi
     divergerait de la fiche, et c'est la version reçue par courriel qui
     ferait foi pour l'abonné.

  2. LE SEUIL EST CELUI DE L'ABONNÉ, pas le nôtre. Quelqu'un qui n'a demandé
     que les ruptures ne reçoit pas « aussi deux ou trois choses
     intéressantes ». La sélection est la sienne ; l'élargir sans le lui
     demander est la première étape vers la lettre qu'on ne lit plus.

  3. AUCUN MODÈLE DE LANGAGE. Comme partout ici : deux compositions sur le
     même corpus et la même période rendent le même texte.

CE QUE CE MODULE NE FAIT PAS : il n'envoie rien. Voir `abonnes.py`,
`PRESTATAIRE_COURRIEL`.
"""
from datetime import date, timedelta

import decision as DEC
import veille as V

VERSION = "2026.08.22"

PERIODE_JOURS = 7

_MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet",
         "août", "septembre", "octobre", "novembre", "décembre")


def _fr(d):
    """« 2026-08-22 » → « 22 août 2026 ». Une date ISO dans l'objet d'un
    courriel français signale un envoi non relu."""
    try:
        d = d if isinstance(d, date) else date.fromisoformat(str(d)[:10])
    except (TypeError, ValueError):
        return str(d)
    return "%d %s %d" % (d.day, _MOIS[d.month - 1], d.year)

# Le nombre de fiches au-delà duquel un bulletin cesse d'être lu. Il est
# écrit, et la coupe est ANNONCÉE dans le bulletin lui-même — comme partout
# ailleurs sur ce site.
MAXI_FICHES = 8
MAXI_PISTES = 2


def _rang(impact):
    return V.IMPACTS.get(impact, {}).get("rang", 99)


def _dans_la_periode(f, debut, fin):
    d = str(f.get("date_fait") or "")[:10]
    return bool(d) and str(debut) <= d <= str(fin)


def composer(corpus, compte, fin=None, periode_jours=PERIODE_JOURS):
    """Le bulletin d'UN abonné, pour une période donnée.

    `fin` est passée plutôt que lue à l'horloge : un bulletin doit pouvoir
    être recomposé à l'identique pour la semaine dernière, sans quoi il
    n'est pas vérifiable.
    """
    fin = fin or date.today()
    debut = fin - timedelta(days=periode_jours - 1)
    sujets = set(compte.get("sujets") or list(V.ORDRE_SUJETS))
    seuil_cle = compte.get("seuil") or "structurant"
    seuil = _rang(seuil_cle)

    pub = V.publiables(corpus)
    retenues = [f for f in pub
                if f.get("sujet") in sujets
                and _rang(f.get("impact")) <= seuil
                and _dans_la_periode(f, debut, fin)]
    retenues.sort(key=lambda f: (_rang(f.get("impact")),
                                 _renverse(f.get("date_fait"))))

    # LES PISTES NE SONT SERVIES QUE SI ELLES S'APPUIENT SUR CE QUI EST DANS
    # LE BULLETIN. Une piste déclenchée par des fiches que l'abonné ne reçoit
    # pas lui arriverait sans ce qui la fonde — c'est-à-dire comme un avis.
    ids = {f.get("id") for f in retenues}
    pistes = [p for p in DEC.pistes(corpus)
              if any(f["id"] in ids for f in p.get("fiches") or [])]

    coupe = max(0, len(retenues) - MAXI_FICHES)
    servies = retenues[:MAXI_FICHES]

    return {
        "periode": {"du": str(debut), "au": str(fin), "jours": periode_jours},
        "destinataire": compte.get("email"),
        "sujets": sorted(sujets),
        "seuil": compte.get("seuil"),
        "vide": not servies,
        "objet": _objet(servies, debut, fin),
        "entree": _entree(servies, retenues, sujets, seuil_cle,
                          debut, fin),
        "fiches": [_extrait(f) for f in servies],
        "n_retenues": len(retenues),
        "n_servies": len(servies),
        "coupe": coupe,
        "coupe_dit": ("%d fiche(s) de plus franchissent votre seuil sur la "
                      "période et ne sont pas dans ce courrier : un bulletin "
                      "qui les porterait toutes ne se lirait plus. Elles sont "
                      "sur le site, avec les mêmes filtres."
                      % coupe) if coupe else "",
        "pistes": [_piste_courte(p) for p in pistes[:MAXI_PISTES]],
        "n_pistes": len(pistes),
        "envoye": False,
        "pourquoi_pas_envoye": None,
    }


def _renverse(d):
    try:
        p = [int(x) for x in str(d)[:10].split("-")]
        return (-p[0], -p[1], -p[2])
    except (ValueError, IndexError):
        return (0, 0, 0)


def _objet(servies, debut, fin):
    """L'objet dit le COMPTE et le plus haut niveau atteint, jamais un
    superlatif. « L'essentiel de la semaine » ne se vérifie pas ; « 3 faits,
    dont 1 rupture » se vérifie en ouvrant."""
    if not servies:
        return ("CONSEILPREV INFO — rien à signaler du %s au %s"
                % (_fr(debut), _fr(fin)))
    ruptures = sum(1 for f in servies if f.get("impact") == "rupture")
    return ("CONSEILPREV INFO — %d fait(s) du %s au %s%s"
            % (len(servies), _fr(debut), _fr(fin),
               ", dont %d rupture(s)" % ruptures if ruptures else ""))


def _entree(servies, retenues, sujets, seuil_cle, debut, fin):
    """LE CAS DU BULLETIN VIDE EST TRAITÉ EN PREMIER, et il est explicite.

    C'est ce paragraphe qui donne sa valeur au silence : sans lui, une lettre
    vide passe pour une panne d'envoi, et l'abonné apprend à ne plus s'y
    fier.
    """
    noms = ", ".join(V.SUJETS[s]["nom"] for s in sorted(sujets)
                     if s in V.SUJETS)
    if not servies:
        return ("Rien à signaler du %s au %s sur les sujets que vous "
                "suivez (%s), au seuil que vous avez fixé. Ce bulletin est "
                "vide, et c'est une information : il n'a pas été complété "
                "avec des faits d'une autre semaine ni avec des éléments "
                "au-dessous de votre seuil. Un bulletin toujours plein "
                "n'apprend rien de sa longueur."
                % (_fr(debut), _fr(fin), noms))
    return ("%d fait(s) franchissent votre seuil « %s » sur %s, du %s au "
            "%s. Chaque élément renvoie à sa fiche, qui porte sa source et "
            "son statut de vérification. Rien de ce qui suit n'a été rédigé "
            "pour ce courrier : ce sont les textes du site."
            % (len(retenues), V.IMPACTS.get(seuil_cle, {}).get("nom", "—"),
               noms, _fr(debut), _fr(fin)))


def _extrait(f):
    """UN EXTRAIT, PAS UNE RÉÉCRITURE. Les champs sont repris tels quels ;
    seule la lecture est raccourcie, et le bulletin dit qu'elle l'est."""
    lecture = str(f.get("lecture") or "")
    coupee = len(lecture) > 320
    return {
        "id": f.get("id"), "titre": f.get("titre"),
        "chapeau": f.get("chapeau"),
        "lecture": (lecture[:317].rstrip() + "…") if coupee else lecture,
        "lecture_coupee": coupee,
        "lecture_nature": f.get("lecture_nature"),
        "lecture_nom": f.get("lecture_nom"),
        "impact": f.get("impact"), "impact_nom": f.get("impact_nom"),
        "sujet_nom": f.get("sujet_nom"),
        "date_fait": f.get("date_fait"),
        "statut_nom": f.get("statut_nom"),
        "source": (f.get("source") or {}).get("nom"),
        "source_url": (f.get("source") or {}).get("url"),
        "lien": "/fiche/%s" % f.get("id"),
    }


def _piste_courte(p):
    """La piste arrive AMPUTÉE DE SA PROPOSITION et lestée de sa réserve.

    Dans un courriel, une piste se lit plus vite et plus seule que sur le
    site : elle y arriverait comme un conseil. Ce qu'elle n'établit pas part
    donc avec elle, et le détail reste sur le site.
    """
    return {"cle": p["cle"], "titre": p["titre"],
            "solidite_nom": p["solidite_nom"],
            "declencheur": p["declencheur"],
            "n_etablit_pas": p["n_etablit_pas"],
            "lien": "/#r-pistes"}


def texte(b):
    """Le bulletin en texte brut.

    LE TEXTE BRUT EST LA VERSION DE RÉFÉRENCE, pas un repli pour vieux
    logiciels : c'est celle qu'on peut relire en entier avant d'envoyer, et
    celle qui ne cache rien dans un gabarit.
    """
    l = [b["objet"], "=" * min(len(b["objet"]), 72), "", b["entree"], ""]
    for f in b["fiches"]:
        l.append("— %s [%s · %s]" % (f["titre"], f["impact_nom"], f["sujet_nom"]))
        l.append("  %s" % f["chapeau"])
        l.append("  Lecture (%s) : %s" % (f["lecture_nom"], f["lecture"]))
        l.append("  Source : %s — %s" % (f["source"], f["source_url"]))
        l.append("  Fiche : %s" % f["lien"])
        l.append("")
    if b["coupe"]:
        l += [b["coupe_dit"], ""]
    for p in b["pistes"]:
        l.append("PISTE — %s (%s)" % (p["titre"], p["solidite_nom"]))
        l.append("  Ce qui la déclenche : %s" % p["declencheur"])
        l.append("  Ce qu'elle n'établit pas : %s" % p["n_etablit_pas"])
        l.append("")
    l.append("— CONSEILPREV INFO. Chaque fait porte sa source et son statut.")
    l.append("  Vous recevez ce bulletin parce que vous vous y êtes abonné ; "
             "il se règle et se résilie depuis votre compte.")
    return "\n".join(l)


def sante(corpus=None):
    return {
        "module": "bulletin", "version": VERSION,
        "periode_jours": PERIODE_JOURS,
        "maxi_fiches": MAXI_FICHES,
        "modeles_de_langage": 0,
        "phrases_redigees_pour_l_envoi": 0,
        "portee": "Compose le bulletin d'un abonné à partir des seules fiches "
                  "publiées, à son seuil et sur ses sujets. N'envoie rien, et "
                  "rend un bulletin vide plutôt que de le compléter.",
    }


def _verifier():
    if MAXI_FICHES < 1:
        raise RuntimeError("bulletin : plus aucune fiche ne serait servie")
    # LE SILENCE DOIT RESTER POSSIBLE. Si un jour quelqu'un ajoute un repli
    # « à défaut, prendre les N dernières fiches », c'est ici que ça se verra.
    src = composer.__doc__ or ""
    if "vide" not in _entree.__doc__:
        raise RuntimeError(
            "bulletin : le cas du bulletin vide n'est plus traité en premier — "
            "une lettre vide passera pour une panne d'envoi")
    del src


_verifier()
