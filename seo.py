# -*- coding: utf-8 -*-
"""Référencement : ce qui doit être vrai sur CHAQUE page servie.

POURQUOI CE MODULE EXISTE

Le référencement d'un site de conseil ne se joue pas sur des mots-clés glissés
dans un texte. Il se joue sur trois choses ennuyeuses, qu'aucune page ne porte
spontanément et qu'aucune relecture humaine ne rattrape à l'échelle :

  1. L'ADRESSE CANONIQUE. Sans elle, la même page atteignable par plusieurs
     chemins — avec ou sans « www », en http, avec un paramètre de campagne —
     devient plusieurs pages aux yeux d'un moteur, qui répartit alors entre
     elles la confiance qu'il aurait accordée à une seule.

  2. LA CARTE DE PARTAGE. Un lien collé dans LinkedIn ou dans un courriel
     n'affiche que ce que la page déclare en Open Graph. Sans ces balises, un
     dirigeant à qui l'on transmet une analyse voit une URL nue — au moment
     précis où la crédibilité se joue. C'est le canal principal du conseil B2B,
     et il était vide sur vingt et une pages sur vingt-quatre.

  3. LE PLAN DU SITE. `robots.txt` en annonçait un depuis le début. Il n'a
     jamais existé : l'adresse rendait 404. Un moteur qui suit cette
     déclaration reçoit une porte fermée.

CE QUE CE MODULE NE FAIT PAS

Il n'invente aucun texte. Le titre et la description sont ceux que la page
porte déjà : les recopier ailleurs créerait deux vérités qui divergeraient au
premier changement. Il les LIT et les décline. Une page sans titre ne reçoit
donc rien — et la recette le signale, plutôt que de lui coller un titre
générique qui la ferait indexer sous un nom qui n'est pas le sien.

L'ADRESSE DE BASE EST UNE VARIABLE

`SITE_BASE_URL` est lue dans l'environnement. Le jour où le site quitte
`conseilprev.onrender.com` pour un nom de domaine propre, aucune ligne de code
ne change — et rien ne reste en arrière avec l'ancienne adresse en dur, ce qui
serait le pire des deux mondes : des canoniques qui pointent vers un site qu'on
a quitté.
"""
import os
import re
from datetime import datetime, timezone

VERSION = "2026-08-a"

BASE_PAR_DEFAUT = "https://conseilprev.onrender.com"


def _normaliser(u):
    """UNE ADRESSE SANS SCHEMA EST UN PIEGE SILENCIEUX. `SITE_BASE_URL` se
    saisit a la main dans un tableau de bord ; ecrire « i-aes.eu » plutot que
    « https://i-aes.eu » est l'erreur naturelle. Toutes les canoniques du site
    deviendraient alors « i-aes.eu/ », une adresse relative que les moteurs
    rejettent — sans qu'aucune page ne cesse de s'afficher, donc sans que rien
    ne le signale. On complete le schema plutot que de servir cela."""
    u = (u or "").strip().rstrip("/")
    if u and not u.startswith(("http://", "https://")):
        u = "https://" + u
    return u


def _hote(u):
    """L'hote seul, tel qu'il s'ecrit dans un pied de page."""
    return re.sub(r"^https?://", "", u).rstrip("/")


BASE = _normaliser(os.environ.get("SITE_BASE_URL")) or BASE_PAR_DEFAUT

# NOS ADRESSES : la courante, et celle d'où l'on vient. Le recalage ne touche
# QU'À CELLES-LÀ. Une canonique qui désigne un AUTRE site est un choix
# éditorial — du contenu syndiqué, par exemple — et ce module ne défait pas
# le travail fait à la main : c'est son principe depuis le début.
NOS_ADRESSES = tuple({BASE, BASE_PAR_DEFAUT.rstrip("/")})

SITE_NOM = "CONSEILPREV"
LOCALE = "fr_FR"
IMAGE_PARTAGE = "/emblem.png"

_TITRE = re.compile(r"<title>(.*?)</title>", re.S | re.I)
# La citation fermante doit etre LA MEME que l'ouvrante — d'ou la reference
# arriere `\1`. Sans elle, `["\']` s'arrete a la premiere apostrophe francaise
# rencontree DANS le texte : la description de /team devenait « L », celle de
# /support « Contactez l ». Dix pages sur vingt-quatre partaient ainsi avec une
# carte de partage vide, ce que ce module existe precisement pour eviter.
_DESC = re.compile(r'<meta\s+name=["\']description["\']\s+content=(["\'])(.*?)\1',
                   re.S | re.I)
_HEAD = re.compile(r"</head>", re.I)


def _texte(s):
    """Une balise ne peut porter ni retour à la ligne ni guillemet double."""
    return re.sub(r"\s+", " ", (s or "")).replace('"', "&quot;").strip()


def lire(html):
    """Le titre et la description que la page porte DÉJÀ. Jamais inventés."""
    t = _TITRE.search(html or "")
    d = _DESC.search(html or "")
    return (_texte(t.group(1)) if t else "",
            _texte(d.group(2)) if d else "")


def url(route):
    """L'adresse absolue. La racine garde sa barre finale : c'est la forme que
    la page d'accueil declare deja en canonique, et deux formes de la meme
    adresse sont deux pages pour un moteur."""
    r = "/" if route in ("", "/") else "/" + str(route).lstrip("/")
    return BASE + r


def balises(route, html):
    """Les balises manquantes de cette page, prêtes à être insérées.

    On n'écrase JAMAIS ce qui est déjà là : une page qui a été soignée à la
    main garde sa version. On ne comble que les trous.
    """
    titre, desc = lire(html)
    if not titre:
        return ""                    # sans identité, on n'invente pas la sienne
    u = url(route)
    out = []
    if 'rel="canonical"' not in html and "rel='canonical'" not in html:
        out.append('<link rel="canonical" href="%s">' % u)
    if 'property="og:' not in html:
        out += ['<meta property="og:type" content="website">',
                '<meta property="og:site_name" content="%s">' % SITE_NOM,
                '<meta property="og:locale" content="%s">' % LOCALE,
                '<meta property="og:title" content="%s">' % titre,
                '<meta property="og:url" content="%s">' % u,
                '<meta property="og:image" content="%s">' % (BASE + IMAGE_PARTAGE)]
        if desc:
            out.append('<meta property="og:description" content="%s">' % desc)
    if 'name="twitter:card"' not in html:
        out += ['<meta name="twitter:card" content="summary_large_image">',
                '<meta name="twitter:title" content="%s">' % titre]
        if desc:
            out.append('<meta name="twitter:description" content="%s">' % desc)
        out.append('<meta name="twitter:image" content="%s">' % (BASE + IMAGE_PARTAGE))
    return "".join(out)


# SEULES LES ADRESSES DE *CETTE PAGE* SONT RECALEES EN ENTIER.
#
# `canonical` et `og:url` designent la page elle-meme : leur valeur juste est
# `url(route)`, chemin compris, et une page servie a /x qui declarerait /y se
# trompe d'adresse.
#
# `og:image` ET `twitter:image` N'Y SONT PLUS, ET C'EST UNE CORRECTION. Une
# premiere version les forcait sur IMAGE_PARTAGE — or les pages declarent
# « /og-image.png », qui n'est pas « /emblem.png ». Le recalage remplacait donc
# silencieusement l'image de partage choisie par une autre : ce qu'on voit sur
# LinkedIn quand on partage la page changeait, sans que personne l'ait demande.
# Le CHEMIN d'une image est un choix editorial ; seul son HOTE est une
# coordonnee, et le remplacement global s'en charge deja.
_ADRESSES_A_RECALER = (
    # (motif de la balise, nom de l'attribut qui porte l'adresse)
    (re.compile(r'<link\b[^>]*\brel=["\']canonical["\'][^>]*>', re.I), "href"),
    (re.compile(r'<meta\b[^>]*\bproperty=["\']og:url["\'][^>]*>', re.I), "content"),
)


def _recaler(html, motif, attribut, valeur):
    """Réécrit l'adresse d'une balise DÉJÀ présente — mais seulement si elle
    désigne une de NOS adresses. Une canonique pointant ailleurs est laissée
    intacte : c'est une décision, pas une coordonnée périmée."""
    def _sub(m):
        def _attr(a):
            ancienne = a.group(2)
            if not ancienne.startswith(NOS_ADRESSES):
                return a.group(0)          # adresse étrangère : on n'y touche pas
            return a.group(1) + valeur + a.group(3)
        return re.sub(r'(\b%s=["\'])([^"\']*)(["\'])' % attribut,
                      _attr, m.group(0), count=1)
    return motif.sub(_sub, html, count=1)


def recaler_adresses(route, html):
    """LES ADRESSES ABSOLUES DE LA PAGE, RAMENÉES SUR `SITE_BASE_URL`.

    CE QUE CE MODULE PROMETTAIT, ET NE TENAIT PAS. Son en-tête annonce que
    changer d'adresse ne demande « aucune ligne de code » et que « rien ne
    reste en arrière avec l'ancienne adresse en dur, ce qui serait le pire des
    deux mondes : des canoniques qui pointent vers un site qu'on a quitté ».

    C'était pourtant exactement ce qui se passait. `balises()` ne comble QUE
    les trous — « on n'écrase jamais ce qui est déjà là » —, et seize pages
    portent leur canonique écrite à la main. `SITE_BASE_URL` n'avait donc
    aucun effet sur elles : mesuré, vingt-six occurrences de l'ancien hôte
    survivaient dans les pages servies, dont neuf sur la seule page d'accueil.
    Le module décrivait le défaut qu'il causait.

    LA DISTINCTION QUE `balises()` GARDE, ET QUI RESTE JUSTE : un titre ou une
    description écrits à la main sont un travail éditorial, et on n'y touche
    pas. Une adresse absolue n'est pas de l'écriture — c'est une coordonnée,
    et elle doit suivre le site."""
    u = url(route)
    # 1. LES COORDONNEES NOMMEES prennent la valeur exacte de CETTE page.
    for motif, attribut in _ADRESSES_A_RECALER:
        html = _recaler(html, motif, attribut, u)

    # 2. TOUTE AUTRE MENTION DE NOS ADRESSES. Elles ne sont pas toutes dans
    #    des balises : seize pieds de page affichent l'adresse EN TOUTES
    #    LETTRES (« <a href="/">conseilprev.onrender.com</a> »), une donnee
    #    structurée JSON-LD declare l'url de l'organisation — c'est ce que
    #    Google lit pour l'identifier — et une chaine de script signe les
    #    messages de contact « Envoye depuis … ». Aucune n'etait recalee.
    #
    #    UN REMPLACEMENT DE CHAINE, PAS UNE ANALYSE DE BALISES. C'est
    #    volontaire : deux tentatives d'analyse par expression reguliere se
    #    sont trompees aujourd'hui meme sur ce depot. Remplacer un nom d'hote
    #    connu par un autre ne demande aucune comprehension de la structure,
    #    et ne peut donc pas se tromper sur elle.
    #
    #    L'ORDRE COMPTE : la forme avec schema d'abord, la forme nue ensuite.
    #    L'inverse produirait « https://i-aes.eu » puis un second passage sur
    #    un hote deja remplace.
    for ancienne in NOS_ADRESSES:
        if ancienne == BASE:
            continue
        html = html.replace(ancienne, BASE)
        html = html.replace(_hote(ancienne), _hote(BASE))
    return html


def enrichir(route, html):
    """La page, complétée. Sans `</head>`, on rend la page INCHANGÉE plutôt que
    de coller des balises n'importe où : un fragment mal placé casse le rendu,
    et un site cassé ne se référence pas."""
    if not html:
        return html
    html = recaler_adresses(route, html)
    b = balises(route, html)
    if not b or not _HEAD.search(html):
        return html
    return _HEAD.sub(b + "</head>", html, count=1)


# ═══════════════════════════════════════════════════════════════════════════
# LE PLAN DU SITE
# ═══════════════════════════════════════════════════════════════════════════

# La priorité n'est pas un classement : c'est ce qu'on demande au moteur de
# revisiter en premier. Les pages de conversion et les pages de fond passent
# avant les mentions légales, qui ne changent jamais.
PRIORITES = {
    "/": (1.0, "weekly"),
    "/aies": (0.9, "monthly"),
    "/platform": (0.9, "monthly"),
    "/formations": (0.9, "monthly"),
    "/demo": (0.8, "monthly"),
    "/livre-blanc": (0.8, "monthly"),
    "/donnees": (0.8, "weekly"),
    "/faq": (0.8, "monthly"),
    "/ressources": (0.7, "weekly"),
    "/actualites": (0.7, "weekly"),
    "/tarifications": (0.7, "monthly"),
    "/empreinte": (0.6, "monthly"),
    "/sourcing": (0.6, "monthly"),
    "/business-developer": (0.6, "monthly"),
    "/team": (0.5, "monthly"),
    "/careers": (0.5, "monthly"),
    "/support": (0.5, "monthly"),
    "/map": (0.4, "monthly"),
    "/dsa": (0.3, "yearly"),
    "/accessibility": (0.3, "yearly"),
    "/mentions-legales": (0.2, "yearly"),
    "/cgv": (0.2, "yearly"),
    "/confidentialite": (0.2, "yearly"),
    "/protection-donnees": (0.2, "yearly"),
}

DEFAUT = (0.5, "monthly")

# Ce que `robots.txt` interdit ne doit PAS figurer au plan. Annoncer à un
# moteur une adresse qu'on lui interdit par ailleurs, c'est lui envoyer deux
# consignes contraires — et c'est lui qui choisit laquelle suivre.
# /enveloppe et /empreinte-parc MANQUAIENT : réservées aux abonnés depuis
# leur création, elles restaient annoncées au plan du site — un moteur y
# envoyait ses visiteurs trouver une porte close sous un titre prometteur.
INTERDITES = ("/api/", "/admin", "/panorama", "/observatoire",
              "/enveloppe", "/empreinte-parc")


def exclue(route):
    return any(route == i or route.startswith(i) for i in INTERDITES)


def _iso(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d")


def plan(pages, racine="."):
    """Le sitemap XML, à partir des pages RÉELLEMENT servies.

    `lastmod` vient de la date du fichier : une date inventée ou figée au jour
    de la génération apprend au moteur à ne plus la croire.
    """
    lignes = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for route in sorted(pages):
        if exclue(route):
            continue
        fichier = pages[route]
        chemin = os.path.join(racine, fichier)
        if not os.path.exists(chemin):
            continue                 # une adresse au plan doit exister
        pri, freq = PRIORITES.get(route, DEFAUT)
        lignes += ["  <url>",
                   "    <loc>%s</loc>" % url(route),
                   "    <lastmod>%s</lastmod>" % _iso(os.path.getmtime(chemin)),
                   "    <changefreq>%s</changefreq>" % freq,
                   "    <priority>%.1f</priority>" % pri,
                   "  </url>"]
    lignes.append("</urlset>")
    return "\n".join(lignes) + "\n"


# ═══════════════════════════════════════════════════════════════════════════
# DONNÉES STRUCTURÉES
# ═══════════════════════════════════════════════════════════════════════════

def jsonld_site():
    """Le site lui-même. Complète la fiche Organization déjà présente en page
    d'accueil : l'une décrit l'entreprise, l'autre le site."""
    return {"@context": "https://schema.org", "@type": "WebSite",
            "name": SITE_NOM, "url": BASE + "/", "inLanguage": "fr-FR",
            "publisher": {"@type": "Organization", "name": SITE_NOM,
                          "url": BASE + "/"}}


def jsonld_formations(catalogue, prix_de=None):
    """Le catalogue de formation, en `Course`.

    C'est le seul contenu du site éligible à un résultat enrichi qui ait un
    sens ici : une formation a une durée, un prix et un organisme. Un prix
    absent n'est PAS remplacé par zéro — l'offre part sans prix plutôt qu'avec
    un prix faux, qui serait opposable.
    """
    org = {"@type": "Organization", "name": SITE_NOM, "url": BASE + "/"}
    cours = []
    for c in (catalogue or []):
        titre = (c.get("titre") or "").strip()
        if not titre:
            continue
        cents = prix_de(c) if prix_de else c.get("prix_cents")
        item = {"@type": "Course", "name": titre,
                "description": (c.get("resume") or c.get("objectif") or titre)[:300],
                "provider": org,
                "url": BASE + "/formations"}
        jours = c.get("jours")
        if jours:
            item["timeRequired"] = "P%dD" % int(jours)
        if cents:
            item["offers"] = {"@type": "Offer", "price": "%.2f" % (cents / 100.0),
                              "priceCurrency": "EUR",
                              "category": "Formation professionnelle",
                              "url": BASE + "/formations"}
        cours.append(item)
    return {"@context": "https://schema.org", "@type": "ItemList",
            "name": "Catalogue de formations CONSEILPREV",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": c}
                                for i, c in enumerate(cours)]}


def sante(pages=None, racine="."):
    """Ce qui manque encore, page par page. Un audit qui rend une liste vide
    quand tout va bien, et des noms quand ça ne va pas."""
    pages = pages or {}
    sans_titre, sans_desc, longues = [], [], []
    for route, fichier in pages.items():
        chemin = os.path.join(racine, fichier)
        if not os.path.exists(chemin):
            continue
        with open(chemin, encoding="utf-8", errors="replace") as f:
            html = f.read()
        t, d = lire(html)
        if not t:
            sans_titre.append(route)
        if not d:
            sans_desc.append(route)
        elif len(d) > 170:
            longues.append((route, len(d)))
    return {"module": "seo", "version": VERSION, "base": BASE,
            "pages": len(pages),
            "sans_titre": sorted(sans_titre),
            "sans_description": sorted(sans_desc),
            "descriptions_trop_longues": sorted(longues),
            "problemes": (["%d page(s) sans titre" % len(sans_titre)] if sans_titre else [])
                         + (["%d page(s) sans description" % len(sans_desc)]
                            if sans_desc else [])}


# ═══════════════════════════════════════════════════════════════════════════
# GEO — LE BALISAGE FAQ, DÉRIVÉ DE LA PAGE
#
# Les moteurs génératifs (ChatGPT, Gemini, Perplexity, Claude) s'appuient sur
# le FAQPage pour citer des réponses. La règle absolue : le bloc DIT ce que la
# page MONTRE. Il est donc dérivé du HTML par le même extracteur qui le
# contrôle en recette — une seule implémentation, aucun écart possible.
#
# Régénérer après modification de la FAQ :
#     python3 -c "import seo; print(seo.bloc_faq(open('faq.html').read()))"
# ═══════════════════════════════════════════════════════════════════════════

import html as _html
import json as _json

_FAQ_Q = re.compile(r'<button class="faq-q".*?>(.*?)</button>', re.S)
_FAQ_R = re.compile(r'<div class="faq-a-inner">(.*?)</div>', re.S)
_FAQ_FLECHE = re.compile(r'<span class="faq-arrow"[^>]*>.*?</span>', re.S)
_FAQ_BLOC = re.compile(
    r'<script type="application/ld\+json" data-geo="faq">(.*?)</script>', re.S)
_TOUTE_BALISE = re.compile(r"<[^>]+>")


def _texte_nu(fragment):
    t = _FAQ_FLECHE.sub(" ", fragment or "")
    t = _TOUTE_BALISE.sub(" ", t)
    t = _html.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def extraire_faq(page_html):
    """Les paires question/réponse RÉELLEMENT affichées par la page."""
    qs = [_texte_nu(m) for m in _FAQ_Q.findall(page_html or "")]
    rs = [_texte_nu(m) for m in _FAQ_R.findall(page_html or "")]
    if len(qs) != len(rs):
        raise ValueError("FAQ déséquilibrée : %d questions, %d réponses"
                         % (len(qs), len(rs)))
    return list(zip(qs, rs))


def jsonld_faq(page_html):
    paires = extraire_faq(page_html)
    if not paires:
        return None
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "inLanguage": "fr",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": r}}
                           for q, r in paires]}


def bloc_faq(page_html):
    d = jsonld_faq(page_html)
    if d is None:
        return ""
    return ('<script type="application/ld+json" data-geo="faq">'
            + _json.dumps(d, ensure_ascii=False) + "</script>")


def bloc_faq_en_place(page_html):
    m = _FAQ_BLOC.search(page_html or "")
    if not m:
        return None
    try:
        return _json.loads(m.group(1))
    except ValueError:
        return None
