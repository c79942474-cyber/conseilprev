# -*- coding: utf-8 -*-
"""Visibilité et conversion — ce qui doit être vrai sur chaque page servie.

CE QU'ON PROTÈGE, ET C'EST PRÉCIS.

1. DEUX CONSIGNES CONTRAIRES SONT PIRES QU'UNE SEULE. `robots.txt` interdit
   `/panorama` et `/observatoire` ; un plan du site qui les annoncerait quand
   même laisserait le moteur choisir laquelle des deux consignes suivre. Le
   contrôle croise les deux listes.

2. ON N'INVENTE PAS L'IDENTITÉ D'UNE PAGE. Le titre et la description servis
   aux moteurs sont ceux que la page porte déjà. Une page sans titre ne reçoit
   RIEN — plutôt qu'un titre générique qui la ferait indexer sous un nom qui
   n'est pas le sien. Et on n'écrase jamais une balise posée à la main.

3. UN PRIX AFFICHÉ À GOOGLE EST UN PRIX ENGAGÉ. Les données structurées des
   formations passent par la MÊME fonction que la facturation. Deux chemins de
   prix qui divergeraient ne seraient pas un défaut de balise : ce serait une
   publicité trompeuse.

4. ATTIRER SANS CONVERTIR, C'EST PAYER LE TRAJET ET FERMER LA PORTE. Dix pages
   n'offraient aucun chemin — dont celle des tarifs. Le bandeau ne se pose que
   là où il manque, et jamais sur une page qui a déjà le sien.
"""
import io
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

DEPOT = "/home/user/conseilprev"
sys.path.insert(0, DEPOT)
os.chdir(DEPOT)

ko = 0


def ok(nom, cond, detail=""):
    global ko
    print("  %s   %s%s" % ("OK " if cond else "KO ", nom,
                           (" — " + str(detail)) if detail else ""))
    if not cond:
        ko += 1


import conversion as C                                          # noqa: E402
import seo as S                                                 # noqa: E402

PAGES = {
    '/': 'index.html', '/support': 'support.html',
    '/mentions-legales': 'mentions-legales.html',
    '/protection-donnees': 'protection-donnees.html', '/cgv': 'cgv.html',
    '/confidentialite': 'confidentialite.html', '/actualites': 'actualites.html',
    '/formations': 'formations.html', '/empreinte': 'empreinte.html',
    '/tarifications': 'tarifications.html', '/dsa': 'dsa.html',
    '/team': 'team.html', '/careers': 'careers.html',
    '/ressources': 'ressources.html', '/sourcing': 'sourcing.html',
    '/business-developer': 'business-developer.html', '/platform': 'platform.html',
    '/donnees': 'donnees.html', '/aies': 'aies.html', '/demo': 'demo.html',
    '/faq': 'faq.html', '/livre-blanc': 'livre-blanc.html',
    '/accessibility': 'accessibility.html', '/map': 'map.html',
}

print("\n══ 1. Le plan du site existe, et il dit vrai ══\n")

xml = S.plan(PAGES, racine=DEPOT)
racine = ET.fromstring(xml)
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
urls = [u.find(NS + "loc").text for u in racine.findall(NS + "url")]
ok("le XML est bien formé et porte le bon espace de noms",
   racine.tag == NS + "urlset", racine.tag)
ok("il annonce les vingt-quatre pages servies", len(urls) == len(PAGES),
   "%d adresses pour %d pages" % (len(urls), len(PAGES)))
ok("…toutes absolues", all(u.startswith("https://") for u in urls))
ok("…et toutes distinctes", len(set(urls)) == len(urls))
ok("la racine porte sa barre finale, comme sa canonique",
   S.BASE + "/" in urls, [u for u in urls if u.rstrip("/") == S.BASE][:1])

# LE contrôle : ce que robots.txt interdit ne doit PAS figurer au plan.
robots = io.open(DEPOT + "/app.py", encoding="utf-8").read()
bloc = robots[robots.find("Disallow: /api/"):]
bloc = bloc[:bloc.find("Sitemap:")]
interdits = re.findall(r"Disallow:\s*(\S+)", bloc)
ok("robots interdit bien quatre chemins", len(interdits) == 4, interdits)
fautes = [u for u in urls for i in interdits
          if i != "/" and u.startswith(S.BASE + i)]
ok("aucune adresse interdite ne figure au plan", not fautes, fautes[:3])
ok("…et les deux modules réservés en font partie",
   S.exclue("/panorama") and S.exclue("/observatoire"))
ok("un dossier interdit couvre aussi ses enfants", S.exclue("/api/export-dc"))

dates = [u.find(NS + "lastmod").text for u in racine.findall(NS + "url")]
ok("chaque adresse porte une date au format ISO",
   all(re.match(r"^\d{4}-\d{2}-\d{2}$", d) for d in dates))
# DISCRIMINATION : une date figée au jour de la génération ne dit rien. Elles
# doivent VENIR des fichiers, donc différer entre elles.
ok("…et ces dates viennent des fichiers, elles ne sont pas toutes identiques",
   len(set(dates)) > 1, "%d dates distinctes" % len(set(dates)))
prios = [float(u.find(NS + "priority").text) for u in racine.findall(NS + "url")]
ok("la page d'accueil est la plus prioritaire", max(prios) == 1.0)
ok("…et les mentions légales les moins", min(prios) <= 0.2)
ok("une page inconnue de la table reçoit une valeur par défaut, pas zéro",
   S.PRIORITES.get("/inexistante", S.DEFAUT) == S.DEFAUT and S.DEFAUT[0] > 0)
ok("une adresse au plan dont le fichier manque est écartée",
   len(S.plan({"/fantome": "nexiste-pas.html"}, racine=DEPOT).split("<loc>")) == 1)

# ── UN PLAN QUE PERSONNE NE PEUT LIRE NE SERT À RIEN ──────────────────────
# Le controle d'en-tetes destine aux scripts anonymes s'appliquait AUSSI aux
# moteurs declares, et repondait 404 : le message qui fait desindexer. On
# rejoue ici la decision du middleware, sans reseau.
_MID = io.open(DEPOT + "/app.py", encoding="utf-8").read()
_ALLOWED = re.search(r"ALLOWED_BOTS = \[(.*?)\]", _MID, re.S).group(1)
_ALLOWED = re.findall(r"'([^']+)'", _ALLOWED)


def _passe(ua, chemin, lang="", enc=""):
    """La reponse du filtre d'en-tetes : True = la page est servie."""
    machines = ('/robots.txt', '/sitemap.xml', '/donnees-structurees.json')
    if chemin in machines or any(b in ua.lower() for b in _ALLOWED):
        return True
    return not (ua and len(ua) > 10 and not lang and not enc)


GBOT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
BING = "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
LKIN = "LinkedInBot/1.0 (compatible; Mozilla/5.0; Apache-HttpClient)"
ok("les moteurs sont bien dix dans la liste d'autorisation", len(_ALLOWED) == 10,
   _ALLOWED)
ok("un moteur déclaré atteint une page de contenu sans en-tête de navigateur",
   _passe(GBOT, "/formations") and _passe(BING, "/tarifications"))
ok("…et l'aperçu LinkedIn aussi, qui est le canal du conseil B2B",
   _passe(LKIN, "/livre-blanc"))
ok("le plan du site et robots.txt ne sont jamais soumis à ce test",
   _passe("n-importe-quoi-de-long", "/sitemap.xml")
   and _passe("n-importe-quoi-de-long", "/robots.txt"))
# CE QUI DOIT RESTER FERMÉ : le filtre garde son objet.
ok("un script anonyme qui usurpe un navigateur reste refusé",
   not _passe("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
              "/formations"))
ok("…et un vrai navigateur passe, lui", _passe(
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36", "/formations",
    lang="fr-FR", enc="gzip"))
ok("l'exemption est bien celle du code servi, pas une copie de la recette",
   "_moteur_declare" in _MID and "path not in _machines" in _MID)

print("\n══ 2. On n'invente pas l'identité d'une page ══\n")

page = '<html><head><title>Un titre</title><meta name="description" content="Une description."></head><body>x</body></html>'
b = S.balises("/essai", page)
ok("une page complète reçoit sa canonique", 'rel="canonical"' in b)
ok("…son adresse absolue", S.BASE + "/essai" in b)
ok("…ses balises de partage", 'property="og:title"' in b and 'og:image' in b)
ok("…et sa carte Twitter", 'name="twitter:card"' in b)
ok("le titre servi est celui de la page, jamais un autre",
   'content="Un titre"' in b)
# LE contrôle : sans titre, on ne donne RIEN.
ok("une page SANS titre ne reçoit rien du tout",
   S.balises("/x", "<html><head></head><body></body></html>") == "")
ok("…et elle est rendue inchangée",
   S.enrichir("/x", "<html><head></head></html>") == "<html><head></head></html>")
# On ne double jamais ce qui existe : la page d'accueil a été soignée à la main.
dejala = ('<html><head><title>T</title><link rel="canonical" href="https://x/">'
          '<meta property="og:title" content="T"><meta name="twitter:card" content="summary">'
          '</head><body></body></html>')
ok("une canonique posée à la main n'est pas doublée",
   'rel="canonical"' not in S.balises("/y", dejala))
ok("…ni les balises de partage", 'property="og:' not in S.balises("/y", dejala))
ok("…si bien que la page reste identique", S.enrichir("/y", dejala) == dejala)
ok("sans </head>, la page est rendue INCHANGÉE plutôt que cassée",
   S.enrichir("/z", "<html><title>T</title></html>") == "<html><title>T</title></html>")
ok("l'insertion se fait AVANT la fermeture de l'en-tête",
   S.enrichir("/essai", page).index("canonical") < S.enrichir("/essai", page).index("</head>"))
ok("un guillemet dans un titre ne casse pas la balise",
   "&quot;" in S.balises("/q", '<html><head><title>Le "grand" titre</title></head></html>'))

# ── L'APOSTROPHE. Une description française en contient presque toujours une.
# Si la citation fermante n'est pas la MÊME que l'ouvrante, la lecture s'arrête
# au premier « ' » du texte : /team partait avec og:description="L".
apos = ('<html><head><title>T</title>'
        '<meta name="description" content="L’equipe et l\'outil de CONSEILPREV.">'
        '</head></html>')
ok("une apostrophe n'interrompt pas la lecture de la description",
   S.lire(apos)[1] == "L’equipe et l'outil de CONSEILPREV.",
   repr(S.lire(apos)[1]))
ok("…et la description servie est complète, pas sa première lettre",
   'content="L’equipe et l\'outil de CONSEILPREV."' in S.balises("/a", apos))
ok("une description en simples quotes est lue de la même façon",
   S.lire('<html><head><title>T</title>'
          "<meta name='description' content='Un \"cas\" limite.'>"
          '</head></html>')[1] == "Un &quot;cas&quot; limite.")

# Sur les VRAIES pages : la description servie est celle du fichier, entière.
_REEL = re.compile(r'<meta\s+name=["\']description["\']\s+content=(["\'])(.*?)\1',
                   re.S | re.I)
_courtes = []
for _r, _f in sorted(PAGES.items()):
    _p = os.path.join(DEPOT, _f)
    if not os.path.exists(_p):
        continue
    with open(_p, encoding="utf-8", errors="replace") as _fh:
        _h = _fh.read()
    _m = _REEL.search(_h)
    if _m and len(S.lire(_h)[1]) < len(re.sub(r"\s+", " ", _m.group(2)).strip()) - 6:
        _courtes.append((_r, len(S.lire(_h)[1])))
ok("aucune des vingt-quatre descriptions n'est tronquée à la lecture",
   not _courtes, _courtes)

sante = S.sante(PAGES, racine=DEPOT)
ok("plus aucune page sans titre", not sante["sans_titre"], sante["sans_titre"])
ok("…ni sans description", not sante["sans_description"], sante["sans_description"])
ok("l'adresse de base est une VARIABLE d'environnement",
   "SITE_BASE_URL" in io.open(DEPOT + "/seo.py", encoding="utf-8").read())

print("\n══ 3. Un prix affiché à Google est un prix engagé ══\n")

CAT = [{"id": 1, "titre": "Formation A", "jours": 2, "prix_cents": 175000},
       {"id": 2, "titre": "Formation B", "jours": 10, "prix_cents": 600000},
       {"id": 3, "titre": "Sans prix", "jours": 1}]
j = S.jsonld_formations(CAT, prix_de=lambda c: c.get("prix_cents"))
items = [e["item"] for e in j["itemListElement"]]
ok("chaque formation devient un Course", len(items) == 3
   and all(i["@type"] == "Course" for i in items))
ok("la durée est en jours, au format ISO", items[1]["timeRequired"] == "P10D",
   items[1]["timeRequired"])
ok("le prix est en euros, pas en centimes",
   items[0]["offers"]["price"] == "1750.00", items[0]["offers"]["price"])
ok("…et le programme de dix jours à 6 000 €",
   items[1]["offers"]["price"] == "6000.00", items[1]["offers"]["price"])
# DISCRIMINATION : un prix absent ne devient pas zéro. « 0,00 € » affiché dans
# un résultat de recherche est une offre, et une offre engage.
ok("une formation sans prix part SANS offre, jamais à zéro",
   "offers" not in items[2], items[2].get("offers"))
ok("le fournisseur est nommé sur chaque cours",
   all(i["provider"]["name"] == "CONSEILPREV" for i in items))
ok("une entrée sans titre est écartée",
   len(S.jsonld_formations([{"jours": 1}])["itemListElement"]) == 0)
# Le prix vient de la fonction qui FACTURE, pas d'une seconde table.
app_src = io.open(DEPOT + "/app.py", encoding="utf-8").read()
ok("la route branche le prix sur la fonction de facturation",
   "seo.jsonld_formations(FORM_CATALOGUE, prix_de=form_prix_cents)" in app_src)

print("\n══ 4. Attirer sans convertir, c'est fermer la porte ══\n")

ok("six pages reçoivent un bandeau", len(C.BANDEAUX) == 6, sorted(C.BANDEAUX))
ok("…dont celle des tarifs", "/tarifications" in C.BANDEAUX)
ok("chaque bandeau a SA phrase, aucune n'est recopiée",
   len({t for t, _ in C.BANDEAUX.values()}) == len(C.BANDEAUX))
ok("…et chacune est une question ou une adresse directe au lecteur",
   all(t.endswith("?") or t.startswith("Vous") for t, _ in C.BANDEAUX.values()),
   [t for t, _ in C.BANDEAUX.values() if not (t.endswith("?") or t.startswith("Vous"))])
h = C.bandeau("/tarifications")
ok("le bandeau porte UNE seule action", h.count("data-cta-action") == 1)
ok("…qui mène au formulaire, enregistré côté serveur", C.CIBLE == "/#contact"
   and 'href="/#contact"' in h)
# Un mailto ne laisse aucune trace, échoue chez qui n'a pas de client de
# messagerie, et rend toute campagne payante impossible à piloter.
ok("…et surtout PAS à un mailto", "mailto:" not in h)
ok("il annonce le délai de réponse", "24 h ouvrées" in h)
ok("le style est porté par le bloc, pas hérité de la page",
   h.count("style=") >= 5)
ok("le bandeau ne se pose pas sur une page qui a déjà un chemin",
   C.enrichir("/tarifications", "<html><body><a href='/#contact'>x</a></body></html>")
   .count("cta-bande") == 0)
ok("…ni deux fois sur la même page",
   C.enrichir("/tarifications", C.enrichir("/tarifications",
              "<html><body>x</body></html>")).count("cta-bande") == 1)
ok("…ni sur une page non déclarée", "cta-bande" not in
   C.enrichir("/cgv", "<html><body>x</body></html>"))
ok("sans </body>, la page est rendue INCHANGÉE",
   C.enrichir("/tarifications", "<html>x</html>") == "<html>x</html>")
ok("il se pose juste avant la fermeture du corps",
   C.enrichir("/tarifications", "<html><body>x</body></html>")
   .endswith("</aside></body></html>"))
sc = C.sante(PAGES, racine=DEPOT)
ok("plus aucune page de contenu n'est un cul-de-sac",
   not [r for r in sc["sans_chemin_apres_bandeau"]
        if r not in ("/cgv", "/mentions-legales", "/dsa", "/accessibility")],
   sc["sans_chemin_apres_bandeau"])

print("\n══ 5. Discrimination : rien de tout cela n'était vrai ══\n")


def _avant(marqueur, fichier):
    hs = subprocess.check_output(
        ["git", "-C", DEPOT, "log", "-S", marqueur, "--format=%H", "--", fichier],
        text=True).split()
    ref = ("%s^" % hs[-1]) if hs else "HEAD"
    try:
        return subprocess.check_output(
            ["git", "-C", DEPOT, "show", "%s:%s" % (ref, fichier)], text=True)
    except subprocess.CalledProcessError:
        return ""


av = _avant("def sitemap_xml", "app.py")
ok("avant, robots.txt annonçait un plan du site…", "Sitemap: https://" in av)
# LE défaut : l'adresse annoncée rendait 404.
ok("…qui n'existait pas : aucune route ne le servait",
   "sitemap_xml" not in av and "/sitemap.xml'" not in av)
ok("les deux modules n'existaient pas",
   _avant("def balises", "seo.py") == ""
   and _avant("BANDEAUX", "conversion.py") == "")


def _compte(html_dir, motif):
    n = 0
    for f in PAGES.values():
        p = os.path.join(html_dir, f)
        if os.path.exists(p):
            with open(p, encoding="utf-8", errors="replace") as fh:
                if motif in fh.read():
                    n += 1
    return n


ok("vingt-trois pages sur vingt-quatre n'avaient pas de canonique",
   _compte(DEPOT, 'rel="canonical"') == 1,
   "%d fichier(s) en portent une en dur" % _compte(DEPOT, 'rel="canonical"'))
ok("…et vingt et une pas de carte de partage",
   _compte(DEPOT, 'property="og:') == 3,
   "%d fichier(s) en portent" % _compte(DEPOT, 'property="og:'))
ok("elles sont désormais POSÉES au service, pas dans les fichiers",
   "seo.enrichir(_route" in app_src and "conversion.enrichir(_route" in app_src)
avmap = _avant("Carte des acteurs IA", "map.html")
ok("avant, /map n'avait ni titre, ni langue déclarée",
   "<title>" not in avmap and 'lang="fr"' not in avmap)
ok("…elle a l'un et l'autre aujourd'hui",
   "<title>" in io.open(DEPOT + "/map.html", encoding="utf-8").read())

print("\n══ 6. Ce que cette mise en visibilité ne devait PAS déplacer ══\n")

ok("les vingt-quatre pages publiques sont toujours servies", len(PAGES) == 24)
ok("les deux modules réservés le restent",
   "PAGES_RESERVEES" in app_src and "reserve_abonne_page" in app_src)
# CE CONTRÔLE LISAIT UNE LIGNE, PAS UNE PROPRIÉTÉ. Il exigeait le texte exact
# « raw = conversion.enrichir(_route, _html).encode('utf-8') ». Le jour où une
# troisième injection s'est ajoutée (l'empreinte des fichiers statiques), la
# ligne est devenue deux — et le contrôle a viré au rouge alors que ce qu'il
# gardait n'avait pas bougé d'un pouce. On regarde donc OÙ se fait l'injection,
# ce qui est la question posée, et non comment elle s'écrit.
def _corps(nom, fin):
    i = app_src.index("def %s(" % nom)
    return app_src[i:app_src.index(fin, i)]


_construction = _corps("_page_cache_entry", "\ndef _serve_page_fast")
_service = _corps("_serve_page_fast", "\n_CACHE_PAGES")
ok("l'injection se fait à la construction du cache, pas à chaque visite",
   all(q in _construction for q in ("seo.enrichir(", "conversion.enrichir(",
                                    "empreintes.marquer("))
   and not any(q in _service for q in ("seo.enrichir(", "conversion.enrichir(",
                                       "empreintes.marquer(")),
   "une injection a migré vers le chemin de service : elle serait alors "
   "refaite à chaque visite, sur 693 Ko de HTML")
ok("…et une erreur d'injection est journalisée, pas avalée",
   "SEO_ENRICH_ERR" in app_src)
ok("le plan du site est mis en cache une heure",
   "public, max-age=3600" in app_src)
ok("les robots d'IA restent traités à part dans robots.txt",
   "GPTBot" in app_src and "ClaudeBot" in app_src)

# La première version de `_DESC` s'arrêtait à la première apostrophe. Le défaut
# n'était pas théorique : on le rejoue ici sur les vraies pages.
_VIEUX = re.compile(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
                    re.S | re.I)
_perdues = 0
for _r, _f in PAGES.items():
    _p = os.path.join(DEPOT, _f)
    if not os.path.exists(_p):
        continue
    with open(_p, encoding="utf-8", errors="replace") as _fh:
        _h = _fh.read()
    _v, _n = _VIEUX.search(_h), _REEL.search(_h)
    if _v and _n and len(_v.group(1)) < len(_n.group(2)) - 6:
        _perdues += 1
ok("l'expression d'origine coupait dix descriptions sur vingt-quatre",
   _perdues == 10, "%d page(s) touchées" % _perdues)

# Le filtre d'en-tetes, tel qu'il etait : aucune exemption.
_avant_mid = _avant("_moteur_declare", "app.py")


def _passe_avant(ua, chemin, lang="", enc=""):
    return not (ua and len(ua) > 10 and not lang and not enc)


ok("avant, le filtre d'en-têtes existait déjà", "HEADERS_INCOHERENTS" in _avant_mid)
ok("…mais sans exemption : ni pour les moteurs, ni pour le plan du site",
   "_moteur_declare" not in _avant_mid and "_machines" not in _avant_mid)
ok("…si bien qu'un moteur sans Accept-Encoding recevait 404 sur tout le site",
   not _passe_avant(GBOT, "/formations") and not _passe_avant(GBOT, "/sitemap.xml"))
ok("…alors qu'il est servi aujourd'hui",
   _passe(GBOT, "/formations") and _passe(GBOT, "/sitemap.xml"))

print("")
print("%d contrôle(s) en échec\n" % ko if ko else "tout est vert\n")
sys.exit(1 if ko else 0)
