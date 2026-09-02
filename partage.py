# -*- coding: utf-8 -*-
"""Partager un communiqué sur LinkedIn — et ce que LinkedIn accepte réellement.

LA CONTRAINTE QUI COMMANDE TOUT LE MODULE, et qu'il vaut mieux connaître avant
d'ajouter un bouton : **LinkedIn ne prend qu'une URL.** Le point d'entrée
`share-offsite` a cessé, en 2021, d'honorer les paramètres `title`, `summary` et
`mini` ; ils sont ignorés en silence. La carte affichée dans le fil est
construite par le robot de LinkedIn, qui va LIRE la page visée et y chercher ses
balises OpenGraph.

CONSÉQUENCE, ET C'EST ELLE QUI FAIT LE TRAVAIL. Un bouton « partager » qui
pointe vers `/actualites` fait que les quatre communiqués produisent la MÊME
carte : même titre, même résumé, même lien. Le lecteur qui en partage deux publie
deux fois la même chose. Le bouton n'aurait donc aucune valeur sans ce qui vient
avec lui : une ADRESSE PAR COMMUNIQUÉ, qui porte ses propres balises.

Et le robot de LinkedIn n'exécute pas de JavaScript. Ce qu'il lit est le HTML
SERVI — pas ce que la page devient une fois la langue choisie. Les titres et les
résumés sont donc extraits du HTML statique, celui qu'un robot voit, et non des
objets `NA`, `NA2`… qui vivent dans le script.

CE QUE CE MODULE NE FAIT PAS : il n'écrit aucun texte. Titre, date et résumé sont
LUS dans `actualites.html`. Recopier un titre ici en produirait un second
exemplaire, et c'est celui qu'on oublie de corriger qui partirait sur LinkedIn.

QUAND LA LECTURE ÉCHOUE, ON NE REND RIEN. Une page dont la structure a changé
rend une liste vide, et l'appelant n'affiche aucun bouton — un bouton qui
partagerait la mauvaise adresse vaut moins qu'un bouton absent.
"""
import html as _html
import os
import re
import unicodedata

VERSION = "2026-09-a"

ICI = os.path.dirname(os.path.abspath(__file__))
PAGE = "actualites.html"
CHEMIN_LISTE = "/actualites"

# Le point d'entrée de partage. AUCUN AUTRE PARAMÈTRE N'EST AJOUTÉ : `title`,
# `summary` et `mini` traînent encore dans beaucoup d'exemples en ligne, ils sont
# ignorés depuis 2021. Les poser donnerait une URL plus longue et pas un mot de
# plus dans la publication — et laisserait croire que le texte est maîtrisé ici.
LINKEDIN = "https://www.linkedin.com/sharing/share-offsite/?url="

# Longueur au-delà de laquelle LinkedIn tronque le résumé de la carte. La valeur
# n'est pas contractuelle et l'affichage varie selon le support ; on coupe donc
# sur une frontière de phrase AVANT ce seuil plutôt que d'espérer y tomber juste.
RESUME_MAX = 200

_ARTICLE = re.compile(
    r'<article class="na-article"[^>]*data-theme="([^"]*)"[^>]*>(.*?)</article>',
    re.S)
_ID = re.compile(r'id="(na\d*)-title"')
_TITRE = re.compile(r'id="na\d*-title"[^>]*>(.*?)</h2>', re.S)
_DATE = re.compile(r'id="na\d*-date"[^>]*>(.*?)</div>', re.S)
_CORPS = re.compile(r'id="na\d*-body"[^>]*>(.*?)</div>\s*$', re.S)


def _texte(fragment):
    """Le texte lisible d'un fragment HTML — balises ôtées, entités résolues."""
    sans = re.sub(r"<[^>]+>", " ", fragment or "")
    return re.sub(r"\s+", " ", _html.unescape(sans)).strip()


def creneau(titre):
    """Le fragment d'adresse tiré du titre : accents ôtés, minuscules, tirets.

    IL N'EST PAS L'IDENTIFIANT. C'est le préfixe — `na4` — qui identifie le
    communiqué, et le créneau ne sert qu'à rendre l'adresse lisible. Un titre
    corrigé change donc le créneau SANS casser les liens déjà partagés : la
    route ne regarde que ce qui précède le premier tiret.
    """
    plat = unicodedata.normalize("NFD", titre or "")
    plat = "".join(c for c in plat if unicodedata.category(c) != "Mn").lower()
    plat = re.sub(r"[^a-z0-9]+", "-", plat).strip("-")
    return "-".join(plat.split("-")[:9])


def resume(corps_html, maximum=RESUME_MAX):
    """Le début du communiqué, coupé sur une frontière de phrase.

    COUPER AU MILIEU D'UN MOT DONNE UNE CARTE QUI A L'AIR CASSÉE, et une carte
    qui a l'air cassée est ce que le lecteur retient de la publication. On
    remonte donc au dernier point avant le seuil ; s'il n'y en a pas, au dernier
    espace, et l'on pose une ellipse.
    """
    plein = _texte(corps_html)
    if len(plein) <= maximum:
        return plein
    tronque = plein[:maximum]
    point = max(tronque.rfind(". "), tronque.rfind("… "), tronque.rfind("! "))
    if point > maximum * 0.5:
        return tronque[:point + 1].strip()
    espace = tronque.rfind(" ")
    return (tronque[:espace] if espace > 0 else tronque).strip() + "…"


def communiques(source=None):
    """Les communiqués de la page, dans leur ordre d'affichage.

    Chacun porte son identifiant, son créneau, son titre, sa date, son résumé,
    ses thèmes et son chemin permanent. Rien n'est écrit ici : tout est lu.
    """
    if source is None:
        try:
            with open(os.path.join(ICI, PAGE), encoding="utf-8") as fh:
                source = fh.read()
        except OSError:                                        # pragma: no cover
            return []
    sortie = []
    for themes, bloc in _ARTICLE.findall(source):
        ident = _ID.search(bloc)
        titre = _TITRE.search(bloc)
        if not (ident and titre):
            # UNE ENTRÉE INCOMPLÈTE EST ÉCARTÉE, PAS DEVINÉE. Un communiqué sans
            # titre lisible produirait une carte vide sur LinkedIn.
            continue
        date = _DATE.search(bloc)
        corps = _CORPS.search(bloc)
        titre_txt = _texte(titre.group(1))
        cle = creneau(titre_txt)
        sortie.append({
            "id": ident.group(1),
            "creneau": ("%s-%s" % (ident.group(1), cle)) if cle else ident.group(1),
            "titre": titre_txt,
            "date": _texte(date.group(1)) if date else None,
            "resume": resume(corps.group(1)) if corps else None,
            "themes": [t.strip() for t in themes.split(",") if t.strip()],
            "chemin": "%s/%s" % (CHEMIN_LISTE,
                                 ("%s-%s" % (ident.group(1), cle)) if cle
                                 else ident.group(1)),
        })
    return sortie


def par_identifiant(creneau_demande, source=None):
    """Le communiqué désigné par un créneau. None s'il n'existe pas.

    ON NE COMPARE QUE LE PRÉFIXE. Un lien partagé il y a six mois porte le
    créneau d'alors ; le titre a pu être corrigé depuis. Faire dépendre la
    résolution du titre entier casserait ce lien — et un lien mort publié sous
    votre nom coûte davantage qu'une adresse un peu vieillie.
    """
    tete = (creneau_demande or "").split("-")[0].lower()
    for c in communiques(source):
        if c["id"] == tete:
            return c
    return None


def url_linkedin(permalien):
    """L'adresse de partage. Le permalien doit être ABSOLU.

    Un chemin relatif produirait un partage vers une page introuvable — LinkedIn
    ne connaît pas le domaine d'origine du clic.
    """
    from urllib.parse import quote
    if not permalien or not permalien.startswith("http"):
        return None
    return LINKEDIN + quote(permalien, safe="")
