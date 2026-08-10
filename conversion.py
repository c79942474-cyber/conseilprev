# -*- coding: utf-8 -*-
"""L'appel à l'action : ce que le visiteur peut faire, sur chaque page.

CE QU'ON A TROUVÉ

Dix pages sur vingt-quatre n'offraient AUCUN chemin de conversion — ni lien
vers le formulaire, ni offre, ni rendez-vous. Parmi elles, `/tarifications` :
la page des prix. Un visiteur qui y arrive depuis une recherche lit le tarif,
décide, et n'a rien à cliquer. Le référencement l'avait amené jusque-là ; la
page le laisse repartir.

C'est le défaut le plus coûteux de tout ce travail de visibilité : attirer sans
convertir revient à payer le trajet et fermer la porte.

CE QUE CE MODULE FAIT, ET CE QU'IL NE FAIT PAS

Il pose un bandeau d'action sur les pages qui n'en ont pas, et SEULEMENT
sur celles-là. La liste est écrite en clair, page par page, plutôt que déduite
d'une heuristique : un bandeau commercial qui apparaîtrait de lui-même sur les
mentions légales ou sur la politique de confidentialité serait déplacé, et
personne ne saurait dire pourquoi il est là.

Il ne touche pas aux pages qui ont déjà un chemin. Une page soignée à la main
garde sa mise en scène — on comble un manque, on ne réécrit pas un travail.

UN SEUL VERBE

Le bandeau propose UNE action principale et une seule. La page d'accueil en
alignait neuf — « Commencer gratuitement », « Choisir Pro », « Contact »,
« Explorer les données »… — et neuf actions équivalentes n'en font aucune :
le visiteur repousse le choix, c'est-à-dire ne choisit pas.

L'action principale mène au formulaire, qui est enregistré côté serveur. Un
`mailto:` ne l'est pas : il ne laisse aucune trace, échoue silencieusement chez
tout visiteur sans client de messagerie configuré — la majorité en entreprise —
et rend toute campagne payante impossible à piloter, faute de savoir ce qu'elle
a rapporté.
"""
import re

VERSION = "2026-08-a"

# Où le bandeau doit apparaître, et POURQUOI. Une page par ligne, avec la
# phrase qui lui correspond : un appel générique sur une page de prix et sur une
# page de méthode ne dit rien à personne.
BANDEAUX = {
    "/tarifications": (
        "Ces tarifs correspondent-ils à votre périmètre ?",
        "Décrivez votre contexte : nous répondons sous 24 h ouvrées avec une "
        "proposition chiffrée, pas un catalogue."),
    "/platform": (
        "Un besoin de recrutement IA, Data ou Cyber ?",
        "Décrivez le poste et son contexte : nous revenons vers vous sous 24 h "
        "ouvrées avec une short-list argumentée."),
    "/actualites": (
        "Cette actualité concerne votre organisation ?",
        "Dites-nous où vous en êtes de votre mise en conformité : nous "
        "répondons sous 24 h ouvrées."),
    "/business-developer": (
        "Vous vous reconnaissez dans ce profil ?",
        "Présentez-vous en quelques lignes — nous répondons sous 24 h ouvrées."),
    "/empreinte": (
        "Vous devez chiffrer l'empreinte de vos systèmes ?",
        "Décrivez votre périmètre : nous répondons sous 24 h ouvrées avec la "
        "méthode applicable et ses limites."),
    "/map": (
        "Vous cherchez un partenaire dans votre région ?",
        "Dites-nous votre besoin et votre implantation : nous répondons sous "
        "24 h ouvrées."),
}

ACTION = "Décrire mon projet"
CIBLE = "/#contact"

# Le style est PORTÉ PAR LE BLOC. Ces pages n'ont pas la même feuille de style
# — certaines sont sombres, d'autres claires — et un bandeau qui hériterait de
# la leur serait illisible sur la moitié d'entre elles.
_STYLE = (
    "margin:44px auto;max-width:900px;padding:26px 28px;border-radius:14px;"
    "background:#0A2230;color:#FFFFFF;font-family:system-ui,-apple-system,"
    "'Segoe UI',Roboto,sans-serif;text-align:center;box-sizing:border-box")
_TITRE = "margin:0 0 8px;font-size:20px;line-height:1.3;font-weight:700;color:#FFFFFF"
_SOUS = ("margin:0 auto 18px;max-width:620px;font-size:14px;line-height:1.6;"
         "color:#C8D6DE")
_BTN = ("display:inline-block;padding:13px 30px;border-radius:8px;"
        "background:#0E6D7C;color:#FFFFFF;font-size:15px;font-weight:700;"
        "text-decoration:none")
_PIED = "margin:14px 0 0;font-size:12px;color:#93A8B4"

_BODY = re.compile(r"</body>", re.I)


def bandeau(route):
    """Le bloc HTML, ou "" si cette page n'en reçoit pas."""
    v = BANDEAUX.get(route)
    if not v:
        return ""
    titre, sous = v
    return (
        '<aside class="cta-bande" data-cta="%s" style="%s">'
        '<p style="%s">%s</p>'
        '<p style="%s">%s</p>'
        '<a href="%s" style="%s" data-cta-action="1">%s &rarr;</a>'
        '<p style="%s">Réponse sous 24 h ouvrées &middot; sans engagement</p>'
        '</aside>'
        % (route, _STYLE, _TITRE, titre, _SOUS, sous, CIBLE, _BTN, ACTION, _PIED))


def a_un_chemin(html):
    """La page mène-t-elle déjà quelque part ? On ne double pas un appel qui
    existe : deux bandeaux sur la même page se neutralisent."""
    h = html or ""
    return ('#contact' in h or 'cta-bande' in h
            or 'href="/demo"' in h or 'href="/formations"' in h)


def enrichir(route, html):
    """La page, avec son bandeau — si elle en mérite un et n'en a pas déjà.

    Sans `</body>`, on rend la page INCHANGÉE : coller un bloc au hasard dans
    un document casserait sa mise en page, et une page cassée ne convertit
    rien du tout.
    """
    if route not in BANDEAUX or a_un_chemin(html) or not _BODY.search(html or ""):
        return html
    return _BODY.sub(bandeau(route) + "</body>", html, count=1)


def sante(pages=None, racine="."):
    """Les pages sans chemin de conversion, une fois les bandeaux posés."""
    import os
    pages = pages or {}
    orphelines = []
    for route, fichier in pages.items():
        chemin = os.path.join(racine, fichier)
        if not os.path.exists(chemin):
            continue
        with open(chemin, encoding="utf-8", errors="replace") as f:
            html = f.read()
        if not a_un_chemin(html) and route not in BANDEAUX:
            orphelines.append(route)
    return {"module": "conversion", "version": VERSION,
            "bandeaux": len(BANDEAUX), "action": ACTION, "cible": CIBLE,
            "sans_chemin_apres_bandeau": sorted(orphelines)}
