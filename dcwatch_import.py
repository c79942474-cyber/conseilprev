# -*- coding: utf-8 -*-
"""RECUPERATION DE LA BASE DCWATCH — construire, empreindre, comparer. Sans reseau.

CE QUE CE MODULE FAIT, ET CE QU'IL NE FERA JAMAIS.

Il sait ou aller chercher la base, verifier qu'un fichier est bien celui qu'on
attend, et dire ce qu'un changement d'amont DEPLACE. Il n'ouvre aucune socket :
il n'importe aucune bibliotheque reseau, et une regle le verifie. Le
telechargement vit dans `recette_dcwatch_amont.py`, qu'on lance a la main.

C'est le patron de `peeringdb_import.py`, et il n'est pas decoratif : `app.py`
importe `dcwatch` au demarrage. Un appel reseau pose dans un module importable
ferait dependre le demarrage du service de la disponibilite de GitLab, et la
suite de tests d'une politique reseau.

POURQUOI L'EMPREINTE, ET PAS L'ETIQUETTE DE VERSION.

La base est figee sur l'etiquette 2026.04.09. Le fichier telechargé a cette
etiquette est identique, octet pour octet, a celui qui est depose. Mais le HEAD
de `main` porte deja trois enregistrements de plus — 523 contre 520, 430 France
contre 427, 341 en exploitation contre 342 — alors que le CHANGELOG amont
affiche toujours 2026.04.09.

UNE ETIQUETTE DE VERSION NE BOUGE PAS QUAND LA DONNEE BOUGE. Se fier au libelle
laisserait croire a une base a jour ; seule l'empreinte le dit. C'est pourquoi
elle vit desormais dans le code (`dcwatch.EMPREINTE`) et non dans la seule prose
d'un fichier d'attribution.

CE QUE `resume` REND, ET POURQUOI CE N'EST PAS LA BASE.

Des comptes : enregistrements, France, exploitation, projets, doublons. Jamais
une ligne, jamais un nom de site. « L'amont a bouge » n'informe personne ;
« 342 sites en exploitation deviennent 341 » se decide — et c'est une decision,
parce que ce nombre est publie et qu'une regle de lecture s'appuie dessus.
"""
import csv
import hashlib
import io

# Le projet, tel que l'API GitLab le nomme. Le chemin est echappe : le slash
# separe deux segments d'URL si on l'oublie, et l'appel part sur une autre route.
PROJET = "hubblo/datacenter-watch"
PROJET_ECHAPPE = "hubblo%2Fdatacenter-watch"
API = "https://gitlab.com/api/v4/projects"

# L'ETIQUETTE SUR LAQUELLE LA BASE EST FIGEE. Elle ne change que par decision :
# la relever deplacerait des chiffres deja publies.
TAG = "2026.04.09"
FICHIER = "export_summary.csv"


def url(tag=TAG, fichier=FICHIER):
    """L'URL du fichier a une reference donnee. Verifiable sans appel.

    `ref` accepte une etiquette, une branche ou un commit — c'est ce qui permet
    a la recette de comparer l'etiquette figee et le HEAD de `main` sans deux
    chemins de code."""
    return "%s/%s/repository/files/%s/raw?ref=%s" % (
        API, PROJET_ECHAPPE, str(fichier).replace("/", "%2F"), tag)


def url_projet():
    """La fiche du projet : visibilite, branche par defaut, derniere activite."""
    return "%s/%s" % (API, PROJET_ECHAPPE)


def empreinte(octets):
    """SHA-256 du fichier, en hexadecimal. La seule chose qui dise vraiment si
    deux exemplaires sont le meme."""
    return hashlib.sha256(octets or b"").hexdigest()


def verifier(octets, attendue):
    """Le fichier est-il celui qu'on attend ? Rend le verdict ET l'ecart : un
    booleen seul ne permet pas de dire ce qui a change."""
    obtenue = empreinte(octets)
    return {"conforme": obtenue == attendue,
            "attendue": attendue,
            "obtenue": obtenue,
            "octets": len(octets or b"")}


def _lignes(octets):
    return list(csv.DictReader(io.StringIO((octets or b"").decode("utf-8", "replace"))))


def resume(octets):
    """Des COMPTES, jamais des lignes. Ce qu'un changement d'amont deplace.

    On y compte aussi les doublons — meme nom, meme commune — parce que la base
    en porte et que tous les totaux les additionnent : le parc francais en
    exploitation ressort a 342 lignes pour 340 sites distincts. Un doublon tu se
    lit comme un site."""
    lignes = _lignes(octets)
    fr = [l for l in lignes if (l.get("country") or "").strip() == "France"]
    etat = {}
    for l in fr:
        cle = (l.get("progress_step") or "").strip() or "non renseigne"
        etat[cle] = etat.get(cle, 0) + 1
    vus, doublons = set(), 0
    for l in fr:
        cle = ((l.get("name") or "").strip().lower(),
               (l.get("city_name") or "").strip().lower())
        if cle in vus:
            doublons += 1
        vus.add(cle)
    return {
        "enregistrements": len(lignes),
        "france": len(fr),
        "exploitation": etat.get("operating", 0),
        "projets": etat.get("project", 0),
        "doublons_france": doublons,
        "octets": len(octets or b""),
    }


def comparer(local, amont):
    """Ce qui separe deux exemplaires, en clair.

    Rend les deux resumes ET les ecarts nommes. Un « les fichiers different »
    n'aide personne a decider ; « trois enregistrements de plus, un site en
    exploitation de moins » se discute."""
    a, b = resume(local), resume(amont)
    ecarts = {c: b[c] - a[c] for c in
              ("enregistrements", "france", "exploitation", "projets", "doublons_france")
              if b[c] != a[c]}
    return {"identiques": empreinte(local) == empreinte(amont),
            "depot": a, "amont": b, "ecarts": ecarts}


# ── Le tableau d'ATTRIBUTION.md, calcule depuis le fichier lui-meme ────────
# IL DECRIVAIT LA BASE DE MEMOIRE. Version, empreinte et nombre d'enregistrements
# etaient saisis a la main dans un tableau markdown : rien n'empechait le fichier
# de changer sans que le tableau bouge, et c'est le tableau qu'on aurait cru.
MARQUE_DEBUT = "<!-- table:debut -->"
MARQUE_FIN = "<!-- table:fin -->"


def table_attribution(octets, tag=TAG, le=None, fichier=FICHIER):
    """Le tableau markdown, rendu depuis le fichier. Entre les deux marqueurs."""
    r = resume(octets)
    return "\n".join([
        MARQUE_DEBUT,
        "| | |",
        "|---|---|",
        "| Version importée | `%s`, récupérée à l'étiquette du même nom |" % tag,
        "| Fichier | `%s`, repris **tel quel**, sans modification |" % fichier,
        "| Empreinte SHA-256 | `%s` |" % empreinte(octets),
        "| Enregistrements | %d |" % r["enregistrements"],
        "| Importé le | %s |" % (le or "29 août 2026"),
        MARQUE_FIN,
    ])


def remplacer_table(texte, table):
    """Substitue le tableau entre marqueurs, sans toucher au reste.

    Le raisonnement juridique qui l'entoure — articles 4.3, 4.4, 4.5, 4.8 —
    reste redige a la main. Le generer le fragiliserait : ce n'est pas de la
    donnee."""
    i = texte.find(MARQUE_DEBUT)
    j = texte.find(MARQUE_FIN)
    if i < 0 or j < 0 or j < i:
        return None
    return texte[:i] + table + texte[j + len(MARQUE_FIN):]
