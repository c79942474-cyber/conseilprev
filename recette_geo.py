"""GEO — être lisible par les moteurs génératifs sans leur mentir. Sentinel.

Pourquoi une recette et pas une promesse : ce site a BLOQUÉ les robots d'IA
pendant des mois (GPTBot, CCBot, ClaudeBot, anthropic-ai — Disallow: /). La
politique s'est inversée — être cité par ChatGPT, Gemini, Perplexity et
Claude suppose d'être lu — et une inversion non contrôlée peut se réinverser
en silence au premier nettoyage de fichier. Chaque contrôle nomme le mensonge
qu'il empêche.

    BASE=http://127.0.0.1:5501 python3 recette_geo.py
"""
import json
import os
import re
import sys
import urllib.request

BASE = os.environ.get("BASE", "http://127.0.0.1:5501")
ko = 0


def ok(nom, cond, detail=""):
    global ko
    print("  %s  %s%s" % ("OK " if cond else "KO ", nom,
                          " — " + str(detail)[:120] if detail else ""))
    if not cond:
        ko += 1


def lire(chemin):
    req = urllib.request.Request(BASE + chemin, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) recette-geo"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, r.read().decode("utf-8", "replace"), r.url


print("\n══ 1. robots.txt : les moteurs génératifs sont admis, le privé fermé ══\n")
st, robots, _ = lire("/robots.txt")
ok("robots.txt répond", st == 200, "HTTP %s" % st)
for bot in ("GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot",
            "Claude-User", "Claude-SearchBot", "anthropic-ai",
            "PerplexityBot", "Perplexity-User", "Google-Extended", "CCBot"):
    m = re.search(r"User-agent: %s\n(.*?)(?:\n\n|\Z)" % re.escape(bot), robots, re.S)
    regles = m.group(1) if m else ""
    ok("%s : admis sur le public, fermé sur le privé" % bot,
       bool(m) and "Allow: /" in regles and "Disallow: /" not in regles.replace(
           "Disallow: /api/", "").replace("Disallow: /admin", "")
       .replace("Disallow: /panorama", "").replace("Disallow: /observatoire", "")
       .replace("Disallow: /enveloppe", "").replace("Disallow: /empreinte-parc", "")
       and "Disallow: /admin" in regles,
       "groupe absent" if not m else "")
ok("plus AUCUN groupe en Disallow: / intégral",
   not re.search(r"User-agent: [^\n]+\nDisallow: /\n", robots))
ok("le plan et le résumé llms.txt sont annoncés",
   "Sitemap:" in robots and "/llms.txt" in robots)

print("\n══ 2. Les pages réservées : fermées PARTOUT, dites NULLE PART ══\n")
reservees = ("/panorama", "/observatoire", "/enveloppe", "/empreinte-parc")
st, plan, _ = lire("/sitemap.xml")
ok("sitemap.xml répond", st == 200, "HTTP %s" % st)
for pth in reservees:
    ok("%s : interdit au crawl ET absent du plan" % pth,
       ("Disallow: %s" % pth) in robots and ("<loc>" not in plan
        or pth + "<" not in plan and pth + "</loc>" not in plan))

print("\n══ 3. llms.txt : rien n'est promis derrière une porte close ══\n")
st, llms, _ = lire("/llms.txt")
ok("llms.txt répond en texte", st == 200, "HTTP %s" % st)
ok("…au format llmstxt.org (titre + résumé cité)",
   llms.startswith("# ") and "\n> " in llms)
chemins = sorted({m or "/" for m in
                  re.findall(r"\]\(https://conseilprev\.onrender\.com(/[^)]*)\)", llms)})
chemins = [c.rstrip("/") or "/" for c in chemins]
ok("il décrit des pages internes", len(chemins) >= 10, "%d adresses" % len(chemins))
for pth in reservees:
    ok("…et ne promet pas %s" % pth, pth not in chemins)
tout_lisible = True
for c in chemins:
    stc, _, url_finale = lire(c)
    if stc != 200 or "/login" in url_finale or "/connexion" in url_finale:
        tout_lisible = False
        ok("  %s lisible sans compte" % c, False, "HTTP %s → %s" % (stc, url_finale))
ok("CHAQUE adresse du fichier est lisible sans compte", tout_lisible,
   "%d adresses vérifiées" % len(chemins))
ok("les études réservées sont décrites comme réservées",
   "réservées aux" in llms and "compte" in llms)

print("\n══ 4. La FAQ : le balisage DIT ce que la page MONTRE ══\n")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo  # noqa: E402
st, faq, _ = lire("/faq")
ok("/faq répond", st == 200, "HTTP %s" % st)
en_place = seo.bloc_faq_en_place(faq)
derive = seo.jsonld_faq(faq)
ok("un bloc FAQPage est servi", en_place is not None)
ok("LE BLOC EST ÉGAL À LA PAGE — dérivé, pas écrit",
   en_place == derive,
   "régénérer : python3 -c \"import seo; print(seo.bloc_faq(open('faq.html').read()))\"")
n = len(derive["mainEntity"]) if derive else 0
ok("la FAQ balisée porte ses %d questions, Sentinel compris" % n,
   n >= 36 and any("Sentinel" in q["name"] for q in derive["mainEntity"]))
stats = re.search(r'faq-stat-n">(\d+)</div><div class="faq-stat-l">Questions', faq)
ok("le compteur affiché dit le vrai compte", stats and int(stats.group(1)) == n,
   stats.group(1) + " affiché / %d réels" % n if stats else "compteur introuvable")

print("\n══ 5. L'entité reliée ══\n")
st, accueil, _ = lire("/")
m = re.search(r'<script type="application/ld\+json">(.*?)</script>', accueil, re.S)
d = json.loads(m.group(1)) if m else {}
ok("l'accueil relie le site frère (sameAs)",
   "https://conseilprevcyber.onrender.com" in d.get("sameAs", []))

print("\n" + ("%d contrôle(s) en échec" % ko if ko else "tout est vert") + "\n")
sys.exit(1 if ko else 0)
