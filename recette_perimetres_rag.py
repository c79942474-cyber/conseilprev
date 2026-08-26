# -*- coding: utf-8 -*-
"""Une seule réserve, deux provenances, et un périmètre qui discrimine sans cacher.

CE QU'ON PROTÈGE.

1. LA RÉSERVE EST DÉJÀ COMMUNE — ET ON NE DOIT PAS LA CLOISONNER. Documents et
   documents Engineering vivent dans la MÊME table depuis l'import, qui
   conserve `theme`, `famille`, `entreprise` et `origine`. Le travail ne
   consistait pas à les réunir, mais à rendre exploitable ce qui l'était déjà.

2. LE MUR. Sentinel range ses documents par PAGE, et ses sept pages parlent
   toutes IA Act ou RGPD : audit, registre, fria, maturité, veille, raci,
   général. Aucune ne parle Safety, incendie, DNV ou CCTP. Tout ce qui vient
   d'Engineering atterrissait donc dans « général », indistinguable du reste.

3. LA FAUSSE BONNE IDÉE ÉCARTÉE. Forcer ces documents vers « audit » ou
   « registre » les aurait sortis du fourre-tout — au prix d'une règle NFPA
   posée devant quelqu'un qui instruit un registre de systèmes d'IA. Les pages
   restent ce qu'elles sont ; le PÉRIMÈTRE est une dimension à part, bâtie sur
   le thème d'origine.

4. IL PRIORISE, IL NE FILTRE PAS. C'est le choix explicite : la recherche voit
   toute la réserve, et le périmètre fait remonter ce qui lui appartient. Un
   contrôle entier y est consacré, parce qu'un filtre serait passé pour une
   priorité tant qu'on ne cherche pas hors périmètre.
"""
import copy
import gzip
import io
import json
import os
import subprocess
import sys

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


import rag_import as R                                         # noqa: E402
import app as APP                                              # noqa: E402

print("\n══ 1. Le vocabulaire des périmètres tient debout ══\n")

P = R.perimetres()
ok("six périmètres proposés", len(P) == 6, len(P))
ok("…dont Engineering et maîtrise d'œuvre, les deux nommés par la demande",
   {"engineering", "moe"} <= {x["cle"] for x in P},
   [x["cle"] for x in P])
ok("…et les trois thèmes cités : safety, fire, rules",
   {"safety", "fire", "rules"} <= {x["cle"] for x in P})
ok("chacun porte un libellé lisible, pas sa clé",
   all(x["nom"] and x["nom"] != x["cle"] for x in P),
   [x["nom"] for x in P][:3])
ok("chacun sait reconnaître quelque chose",
   all(x["mots"] or x["familles"] for x in P))
ok("un périmètre inventé n'est pas valide", not R.perimetre_valide("nimportequoi"))
ok("…et l'absence de périmètre non plus", not R.perimetre_valide(""))

print("\n══ 2. Les deux réserves se croisent vraiment ══\n")

# LE contrôle de la demande : une pièce d'incendie doit puiser DANS LES DEUX.
CAS = [
    ("Engineering / Projet OWFarm / Safety", "", {"engineering", "safety"}),
    ("Engineering / Projet OWFarm / Fire fighting / Watermist", "",
     {"engineering", "fire"}),
    ("Engineering / Projet OWFarm / Rules / DNV", "", {"engineering", "rules"}),
    ("Engineering / Oil & Gas / GNL / Rules", "", {"engineering", "rules"}),
    # Celui-ci vient de l'autre base — « Documents », famille Centres de données.
    ("Data center / Safety Management / Incendie & détection", "",
     {"safety", "fire", "datacenter"}),
    ("Cahier des charges & CCTP", "", {"moe"}),
]
for theme, nom, attendu in CAS:
    trouves = {x["cle"] for x in P if R.dans_perimetre(x["cle"], theme, "", nom)}
    ok("%s" % theme[:54], trouves == attendu, "%s" % sorted(trouves))
ok("un document d'incendie EXISTE des deux côtés — c'est le partage demandé",
   R.dans_perimetre("fire", "Engineering / Projet OWFarm / Fire fighting / Watermist")
   and R.dans_perimetre("fire", "Data center / Safety Management / Incendie & détection"))
# Un document depose directement sur Sentinel n'a NI theme NI famille : sans le
# repli sur le nom de fichier, la moitie de la reserve serait hors perimetre.
ok("un document sans thème est rattrapé par son nom de fichier",
   R.dans_perimetre("fire", "", "", "NFPA-750-watermist-2023.pdf")
   and R.dans_perimetre("rules", "", "", "NFPA-750-watermist-2023.pdf"))
ok("…mais un document étranger n'est rattaché à rien",
   not any(R.dans_perimetre(x["cle"], "", "", "politique-IA-interne.docx") for x in P))
ok("la famille suffit, même sans mot reconnu",
   R.dans_perimetre("engineering", "Engineering / Projet inconnu", "Engineering"))
ok("…et elle se déduit du thème quand elle n'est pas fournie",
   R.dans_perimetre("engineering", "Engineering / Projet inconnu", ""))

print("\n══ 3. LE contrôle : le périmètre PRIORISE, il ne filtre jamais ══\n")

LOT = [
    {"document": "politique-IA.docx", "theme": "", "famille": "", "texte": "a"},
    {"document": "NFPA-750-watermist.pdf", "theme": "", "famille": "", "texte": "b"},
    {"document": "note-safety.pdf", "theme": "Engineering / Projet OWFarm / Safety",
     "famille": "Engineering", "texte": "c"},
    {"document": "veille.pdf", "theme": "Veille", "famille": "Divers", "texte": "d"},
]
sans = APP.rag_prioriser(copy.deepcopy(LOT), "")
ok("sans périmètre, l'ordre du moteur est intact",
   [x["document"] for x in sans] == [x["document"] for x in LOT])
ok("…et aucun document ne se voit attribuer d'appartenance",
   all(x["dans_perimetre"] is None for x in sans))

feu = APP.rag_prioriser(copy.deepcopy(LOT), "fire")
ok("avec « fire », le document d'incendie passe en tête",
   feu[0]["document"] == "NFPA-750-watermist.pdf", feu[0]["document"])
# CE contrôle est celui qui distingue une PRIORITÉ d'un FILTRE. Un filtre
# aurait rendu une liste d'UN élément et passerait tout ce qui précède.
ok("…et RIEN n'a disparu : les quatre sont toujours là",
   len(feu) == 4, "%d au lieu de %d" % (len(feu), len(LOT)))
ok("…les documents hors périmètre gardent leur ordre relatif",
   [x["document"] for x in feu if not x["dans_perimetre"]]
   == ["politique-IA.docx", "note-safety.pdf", "veille.pdf"],
   [x["document"] for x in feu if not x["dans_perimetre"]])
ok("…et chacun DIT s'il vient du périmètre ou d'ailleurs",
   [x["dans_perimetre"] for x in feu] == [True, False, False, False])

ing = APP.rag_prioriser(copy.deepcopy(LOT), "engineering")
ok("avec « engineering », c'est un autre document qui remonte",
   ing[0]["document"] == "note-safety.pdf", ing[0]["document"])
ok("…preuve que la priorité suit le périmètre, et non un ordre figé",
   ing[0]["document"] != feu[0]["document"])
vide = APP.rag_prioriser([], "fire")
ok("une liste vide reste une liste vide, sans incident", vide == [])

print("\n══ 4. L'API sert le périmètre, et avoue quand elle l'ignore ══\n")

APP.app.config["TESTING"] = True
NAV = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
       "Accept-Language": "fr-FR,fr;q=0.9", "Accept-Encoding": "gzip, deflate"}


def _json(r):
    """Ce que fait un navigateur, et que le client de test ne fait pas.

    Ces contrôles envoient de VRAIS en-têtes de navigateur, `Accept-Encoding`
    compris. L'application compresse aussi ses réponses JSON : le corps arrive
    gzippé, et un navigateur — comme `fetch` ou `requests` — le décompresse
    tout seul. Le client de test de Werkzeug est le seul à ne pas le faire.
    Retirer `Accept-Encoding` des en-têtes ferait passer le contrôle en
    cessant de ressembler à un navigateur : c'est l'inverse de ce qu'on veut."""
    if r.headers.get("Content-Encoding") == "gzip":
        return json.loads(gzip.decompress(r.data).decode("utf-8"))
    return r.get_json()


with APP.app.test_client() as c:
    with c.session_transaction() as s:
        s["is_conseilprev"] = True
    rp = c.get("/api/rag/perimetres", headers=NAV)
    jp = _json(rp) or {}
    r1 = c.post("/api/rag/search", headers=NAV,
                json={"query": "protection incendie brouillard d'eau", "perimetre": "fire"})
    j1 = _json(r1) or {}
    r2 = c.post("/api/rag/search", headers=NAV,
                json={"query": "incendie", "perimetre": "perimetre-invente"})
    j2 = _json(r2) or {}
    r3 = c.post("/api/rag/search", headers=NAV, json={"query": "incendie"})
    j3 = _json(r3) or {}
ok("les périmètres sont servis par l'API", rp.status_code == 200
   and len(jp.get("perimetres") or []) == 6, rp.status_code)
ok("…par le module qui détient la taxonomie, pas par une copie",
   [x["cle"] for x in jp["perimetres"]] == [x["cle"] for x in P])
ok("une recherche avec périmètre répond", r1.status_code == 200, r1.status_code)
ok("…et rend le périmètre appliqué", j1.get("perimetre") == "fire", j1.get("perimetre"))
ok("…avec le compte de ce qui en vient", "n_perimetre" in j1)
# Appliquer un perimetre inconnu EN SILENCE ferait croire a une priorisation
# qui n'a pas eu lieu — c'est le meme defaut que le prix de repli muet.
ok("un périmètre inconnu n'est PAS appliqué en silence",
   j2.get("perimetre_inconnu") is True and j2.get("perimetre") == "",
   "%s / %r" % (j2.get("perimetre_inconnu"), j2.get("perimetre")))
ok("…et une recherche sans périmètre ne crie pas à l'inconnu",
   j3.get("perimetre_inconnu") is False and j3.get("perimetre") == "")

print("\n══ 5. Les pages Sentinel n'ont PAS été détournées ══\n")

ok("les sept pages sont inchangées",
   APP.RAG_PAGES_VALIDES == ["audit", "registre", "fria", "maturite", "veille",
                             "raci", "general"], APP.RAG_PAGES_VALIDES)
# On a REFUSE de reclasser l'ingenierie vers les pages IA Act : une regle NFPA
# devant un registre de systemes d'IA serait du bruit, pas de l'aide.
for theme in ("Engineering / Projet OWFarm / Safety",
              "Engineering / Projet OWFarm / Rules / DNV",
              "Engineering / Oil & Gas / GNL / Rules"):
    ok("« %s » ne s'invite pas dans les pages IA Act" % theme.split(" / ")[-1],
       R.pages_pour(theme) == ["general"], R.pages_pour(theme))
ok("…et les déductions IA Act d'origine fonctionnent toujours",
   R.pages_pour("IEC 62443 audit") == ["audit", "general"]
   and "fria" in R.pages_pour("Droits fondamentaux — FRIA"),
   R.pages_pour("IEC 62443 audit"))
ok("le périmètre, lui, les rend adressables sans les déplacer",
   R.dans_perimetre("rules", "Engineering / Projet OWFarm / Rules / DNV"))

print("\n══ 6. Ce que le partage ne devait PAS déplacer ══\n")

# Compter les familles ne dit rien de leur contenu : on vérifie les NOMS,
# et que les deux qui portent le partage — Engineering et Centres de
# données — n'ont pas perdu de sous-dossier au passage.
noms = [n for n, _ in R.FAMILLES]
ok("les dix familles de thèmes sont intactes", len(R.FAMILLES) == 10, len(R.FAMILLES))
ok("…dont Engineering et Centres de données, les deux que le partage relie",
   "Engineering" in noms and "Centres de données" in noms, noms)
th = dict(R.FAMILLES)
ok("…avec leurs sous-dossiers au complet",
   len(th["Engineering"]) == 15 and len(th["Centres de données"]) == 25,
   "%d / %d" % (len(th["Engineering"]), len(th["Centres de données"])))
ok("…familles et sous-dossiers compris",
   R.famille_de("Engineering / Projet OWFarm / Safety") == "Engineering"
   and R.famille_de("Data center / Eau & stress hydrique") == "Centres de données")
ok("…et la reconnaissance des entreprises aussi", R.est_entreprise("EDF"))
ok("la normalisation partagée est définie AVANT ses usages",
   io.open(DEPOT + "/rag_import.py", encoding="utf-8").read().find("def _sans_accents(")
   < io.open(DEPOT + "/rag_import.py", encoding="utf-8").read().find("def dans_perimetre("))
def _page(nom):
    """Le HTML d'une page ET le JavaScript qu'elle exécute.

    Le JavaScript en ligne a été sorti des pages vers des fichiers `.page.js`
    servis à côté : ce qui s'exécutait DANS `sentinel.html` s'exécute
    désormais dans `sentinel.page.js`. Ces contrôles cherchent des marqueurs
    dans « ce que la page fait » — ils doivent donc lire les deux fichiers.
    Ne lire que le HTML déclarerait absent un code simplement déplacé, et
    c'est ce qui s'est produit : trois recettes vertes sont tombées le jour de
    l'extraction, sans qu'aucune page ait cessé de fonctionner."""
    s = io.open(os.path.join(DEPOT, nom), encoding="utf-8").read()
    js = os.path.join(DEPOT, nom.replace(".html", ".page.js"))
    if os.path.exists(js):
        s += "\n" + io.open(js, encoding="utf-8").read()
    return s


sent = _page("sentinel.html")
ok("l'interface charge les périmètres depuis le serveur",
   "/api/rag/perimetres" in sent)
ok("…une seule fois, et les garde", "window.__ragPerimetres" in sent)
ok("…et affiche le thème d'origine de chaque extrait", "r.theme" in sent)
ok("…en marquant ceux qui viennent du périmètre", "r.dans_perimetre" in sent)
ok("…tout en écrivant que rien n'est restreint",
   "ne restreint rien" in sent)

print("\n══ 7. Discrimination : rien de tout cela n'existait avant ══\n")


def _avant(marqueur, fichier):
    hs = subprocess.check_output(
        ["git", "-C", DEPOT, "log", "-S", marqueur, "--format=%H", "--", fichier],
        text=True).split()
    ref = ("%s^" % hs[-1]) if hs else "HEAD"
    return subprocess.check_output(
        ["git", "-C", DEPOT, "show", "%s:%s" % (ref, fichier)], text=True)


avr = _avant("PERIMETRES", "rag_import.py")
ok("avant, aucun périmètre n'existait", "PERIMETRES" not in avr)
ok("…et rien ne savait dire si un document en relevait",
   "def dans_perimetre" not in avr)
ava = _avant("rag_prioriser", "app.py")
ok("avant, la recherche ne connaissait que la page",
   "def rag_recherche(cur, query, limite=5, page='')" in ava)
ok("…et ne rapportait ni thème ni famille",
   "d.theme, d.famille" not in ava)
ok("…ni ne savait prioriser quoi que ce soit", "rag_prioriser" not in ava)
avs = _avant("__ragPerimetres", "sentinel.html")
ok("avant, la consultation n'offrait aucun choix de réserve",
   "__ragPerimetres" not in avs)

print("")
print("%d contrôle(s) en échec\n" % ko if ko else "tout est vert\n")
sys.exit(1 if ko else 0)
