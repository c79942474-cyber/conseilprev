# -*- coding: utf-8 -*-
"""Suisse, Norvège, Royaume-Uni : présents sur les cartes, jamais naturalisés.

CE QU'ON PROTÈGE.

1. LE FAUX ZÉRO. Les neuf sites suisses ne portent ni capacité annoncée ni
   gabarit : aucune empreinte n'en est dérivable. La somme de rien valait
   « 0 t de CO2e », affichée en face de « 9 centres » — un pays sans calcul
   passait pour le plus propre du tableau, et remontait en tête d'un tri
   croissant. Un zéro qui n'est pas une mesure doit se dire « non estimée ».

2. LE FAUX PRIX. Un pays absent du référentiel des prix recevait en silence
   une fourchette de secours de 100-150 €/MWh, puis un coût total de possession
   complet, au même format et avec la même autorité qu'un pays sourcé. Le repli
   reste — sinon il n'y a pas de dossier — mais il se déclare.

3. LA FAUSSE APPARTENANCE. Ces trois pays ne sont PAS des États membres, et
   le règlement IA ne s'y applique pas de la même façon : pas du tout en Suisse
   et au Royaume-Uni, par reprise EEE en Norvège. Les colorer sur la carte sans
   le dire les naturaliserait. Chacun porte `ue: False`, un régime écrit, et le
   suffixe « (hors UE) » derrière son nom.

4. LA DÉRIVE DE LA GRAINE. La page embarque une copie du référentiel pour
   fonctionner sans serveur. Elle était figée à vingt-sept pays et ne suivait
   PAS l'API : `UE` étant capturé une seule fois au chargement, tout ajout
   servi par le serveur n'atteignait jamais les cartes. Le défaut ne se voyait
   que le jour où les deux cessaient de dire la même chose — c'est-à-dire
   aujourd'hui.
"""
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


import implantation as I                                       # noqa: E402
import datacentres as D                                        # noqa: E402
import empreinte_sites as E                                    # noqa: E402
import panorama_ia as P                                        # noqa: E402

TIERS = ("CH", "NO", "GB")
impl = I.assemble(D.SITES, E.INTENSITE)
pp = {x["pays"]: x for x in impl["pays"]}
emp = E.assemble(sites=D.assemble()["sites"], cas=[])
ep = {x["pays"]: x for x in emp["par_pays"]}

print("\n══ 1. Les trois sont là, et ne sont pas confondus avec des membres ══\n")

ok("les Vingt-Sept restent vingt-sept", len(P.PAYS_UE) == 27, len(P.PAYS_UE))
ok("trois pays tiers s'y ajoutent pour les cartes", len(P.PAYS_TIERS) == 3,
   sorted(P.PAYS_TIERS))
ok("…soit trente pays servis", len(P.PAYS_CARTE) == 30, len(P.PAYS_CARTE))
ok("aucun pays tiers ne s'est glissé chez les membres",
   not (set(P.PAYS_UE) & set(P.PAYS_TIERS)), set(P.PAYS_UE) & set(P.PAYS_TIERS))
for c in TIERS:
    x = P.PAYS_CARTE[c]
    ok("%s se déclare hors Union" % c, x.get("ue") is False, x.get("ue"))
    ok("…et porte un régime écrit, pas un silence", bool(x.get("regime")),
       (x.get("regime") or "")[:52])
    ok("…avec son autorité de cybersécurité et sa CNIL nationale",
       bool(x.get("cyber")) and bool(x.get("dpa")), "%s · %s" % (x.get("cyber"), x.get("dpa")))
ok("un État membre, lui, ne porte AUCUN drapeau `ue`",
   P.PAYS_CARTE["FR"].get("ue") is None)
# LE point de droit : l'AI Act ne s'applique pas de la meme facon aux trois, et
# les fondre serait une faute lourde. Chaque regime doit etre DISTINCT.
ok("la Suisse dit que le règlement IA ne s'y applique PAS",
   "ne s'applique PAS" in P.PAYS_CARTE["CH"]["regime"])
ok("…tout en rappelant l'article 2 : un fournisseur suisse y est soumis sur le "
   "marché de l'Union", "art. 2" in P.PAYS_CARTE["CH"]["regime"])
ok("la Norvège dit l'EEE et la reprise à venir",
   "EEE" in P.PAYS_CARTE["NO"]["regime"] and "repris" in P.PAYS_CARTE["NO"]["regime"])
ok("le Royaume-Uni dit qu'aucun équivalent n'est en vigueur",
   "aucun équivalent" in P.PAYS_CARTE["GB"]["regime"])
ok("les trois régimes sont bel et bien différents",
   len({P.PAYS_CARTE[c]["regime"] for c in TIERS}) == 3)
ok("la santé compte les deux populations séparément",
   P.sante()["n_pays_ue"] == 27 and P.sante()["n_pays_tiers"] == 3
   and P.sante()["n_pays_carte"] == 30)

print("\n══ 2. La graine embarquée ne dérive plus du module ══\n")

pan = io.open(DEPOT + "/panorama.html", encoding="utf-8").read()
i = pan.find("var DATA = ")
graine = json.loads(pan[i + len("var DATA = "):pan.find("\n", i)].rstrip().rstrip(";"))
gp = graine.get("pays_ue") or {}
ok("la graine porte les trente pays", len(gp) == 30, len(gp))
ok("…exactement les mêmes que le module, pas un de plus ni de moins",
   set(gp) == set(P.PAYS_CARTE), set(gp) ^ set(P.PAYS_CARTE))
# Comparer les seuls NOMS laissait passer toute correction de fond restée dans
# le module : autorité renommée, coquille corrigée, régime précisé. La graine
# est une COPIE, et une copie se vérifie entière.
ecarts = [c for c in gp if gp[c] != P.PAYS_CARTE[c]]
ok("…et chaque fiche est identique, jusqu'au dernier caractère", not ecarts, ecarts)
ok("…drapeaux d'appartenance compris",
   all(gp[c].get("ue") == P.PAYS_CARTE[c].get("ue") for c in gp))
ok("la graine nomme aussi les trois tiers", graine.get("pays_tiers") == sorted(TIERS),
   graine.get("pays_tiers"))
# LE défaut structurel : `UE` était capturé une seule fois. Sans ce relais,
# tout ce qui précède serait vrai côté serveur et faux à l'écran.
ok("la page RELIE `UE` quand l'API répond",
   "UE=DATA.pays_ue||UE" in pan.replace(" ", ""))
ok("…et sait distinguer un membre d'un pays tiers", "function estUE(" in pan)
ok("le suffixe « (hors UE) » survit à l'entrée dans la table",
   'p.ue === false ? p.nom + " (hors UE)"' in pan)

print("\n══ 3. La Suisse entre au comparateur — sur des sources, pas des défauts ══\n")

for nom, d in (("eau", I.EAU), ("mix", I.MIX), ("prix", I.PRIX), ("avis", I.AVIS)):
    ok("la Suisse a désormais son %s" % nom, "CH" in d)
ok("24 pays classés au lieu de 23",
   sum(1 for x in impl["pays"] if x["avis"]) == 24,
   sum(1 for x in impl["pays"] if x["avis"]))
ch = pp["CH"]
ok("son mix est celui de 2024 : ~30 % nucléaire, le reste hydraulique",
   I.MIX["CH"] == {"nucleaire": 30, "renouvelables": 70, "fossile": 0}, I.MIX["CH"])
ok("son eau est classée faible", I.EAU["CH"][0] == "faible")
ok("…mais l'incertitude de l'AEE sur le WEI+ suisse est DITE",
   "incertitude ÉLEVÉE" in I.EAU["CH"][2], I.EAU["CH"][2][-60:])
ok("son prix est bas, entre 70 et 110 €/MWh",
   I.PRIX["CH"] == ("bas", (70, 110)), I.PRIX["CH"])
# Le libelle de la source ne doit pas attribuer a Eurostat un chiffre qui n'en
# vient pas : ni la Suisse ni le Royaume-Uni n'y figurent.
ok("…et la source avoue que deux pays ne viennent PAS d'Eurostat",
   "NE VIENNENT PAS" in I.SOURCE_PRIX["note"]
   and "Royaume-Uni" in I.SOURCE_PRIX["note"]
   and "ElCom" in I.SOURCE_PRIX["note"])
ok("l'avis suisse nomme la sortie du nucléaire",
   any("sortie du nucléaire" in x for x in ch["avis"]["contre"]))
ok("…et croise le risque de crue du critère XDI",
   any("TROISIÈME MONDIALE" in x for x in ch["avis"]["contre"]))
ok("…ce que le critère climatique confirme, à 33 %",
   ch["climat_physique"]["haut_risque_pct"] == 33
   and ch["climat_physique"]["rang_mondial"] == 3)
ok("le commentaire nomme le paradoxe : kWh propre, sol exposé",
   "paradoxe" in ch["avis"]["comm"])
ok("la Suisse porte une perspective datée et sourcée",
   any(x["pays"] == "CH" and x.get("source") and x.get("date")
       for x in I.PERSPECTIVES))
ok("…l'accord électricité signé le 2 mars 2026, non ratifié",
   any(x["pays"] == "CH" and "ratification" in x["resume"] for x in I.PERSPECTIVES))
ok("la santé du module reste verte", I.sante()["ok"], I.sante()["problemes"])

print("\n══ 4. L'analyse d'investissement ne fabrique plus de prix en silence ══\n")

import app as APP                                              # noqa: E402
APP.app.config["TESTING"] = True
NAV = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
       "Accept-Language": "fr-FR,fr;q=0.9", "Accept-Encoding": "gzip, deflate"}
with APP.app.test_client() as c:
    with c.session_transaction() as sess:
        sess["is_conseilprev"] = True
    r = c.post("/api/finance-dc/devis", headers=NAV,
               json={"pays": ["CH", "NO", "GB", "FR", "LI"], "mw": 20,
                     "gabarit": "hyperscale", "annees": 10})
    j = r.get_json() or {}
ok("le comparateur d'investissement répond", r.status_code == 200 and j.get("ok"),
   r.status_code)
dos = {x["pays"]: x for x in (j.get("dossiers") or [])}
ok("les trois pays tiers y sont chiffrables",
   all(k in dos for k in TIERS), sorted(dos))
for c2 in TIERS:
    o = dos[c2]["contexte"]["prix_origine"]
    ok("%s : son prix vient du RÉFÉRENTIEL, pas d'un défaut" % c2,
       o["nature"] == "referentiel", o["nature"])
ok("le libellé n'attribue plus tous les prix à Eurostat",
   "sources nationales pour la Suisse" in dos["CH"]["contexte"]["prix_origine"]["libelle"])
# DISCRIMINATION : un pays SANS prix doit encore recevoir un dossier — sinon on
# aurait remplace une valeur inventee par un refus — mais il doit le DIRE.
li = dos.get("LI", {}).get("contexte", {}).get("prix_origine") or {}
ok("un pays sans prix national reçoit toujours un dossier", bool(li), li.get("nature"))
ok("…mais il déclare son repli au lieu de l'appliquer en silence",
   li.get("nature") == "defaut" and "AUCUN prix national" in li.get("libelle", ""))
ok("…et prévient que le coût qui en découle est un ordre de grandeur",
   "ordre de" in li.get("libelle", ""))
ok("le prix réellement employé voyage avec le dossier",
   dos["CH"]["contexte"]["prix_eur_mwh"] == [70, 110],
   dos["CH"]["contexte"]["prix_eur_mwh"])
# Le prix suisse sourcé est plus bas que le repli : le coût total DEVAIT bouger.
ok("la Suisse coûte désormais moins que le pays resté sur le repli",
   dos["CH"]["tco"]["total_meur"][0] < dos["LI"]["tco"]["total_meur"][0],
   "%s contre %s" % (dos["CH"]["tco"]["total_meur"], dos["LI"]["tco"]["total_meur"]))

print("\n══ 5. L'empreinte : « non estimée » n'est pas « zéro » ══\n")

for c3 in TIERS:
    ok("%s figure au tableau d'empreinte" % c3, c3 in ep, sorted(ep)[:5])
ok("la Norvège et le Royaume-Uni ont, eux, une empreinte dérivée",
   ep["NO"]["estimable"] and ep["GB"]["estimable"])
ok("…et elle n'est pas nulle",
   ep["GB"]["total_t"][1] > 0 and ep["NO"]["total_t"][1] > 0)
ok("la Suisse porte 9 centres et AUCUN chiffrable",
   ep["CH"]["n_dc"] == 9 and ep["CH"]["dc_estimes"] == 0,
   "%d / %d" % (ep["CH"]["dc_estimes"], ep["CH"]["n_dc"]))
ok("…elle est donc déclarée non estimable", ep["CH"]["estimable"] is False)
ok("…avec le motif en toutes lettres",
   "ni capacité annoncée ni gabarit" in (ep["CH"]["motif_non_estimable"] or ""))
ok("…qui nie explicitement la lecture « parc propre »",
   "pas une absence d'émissions" in (ep["CH"]["motif_non_estimable"] or ""))
# DISCRIMINATION : sans ce drapeau, un tri croissant sacrait la Suisse premiere
# du classement d'empreinte, devant des pays reellement mesures.
tries = sorted(emp["par_pays"], key=lambda x: x["total_t"][1])
ok("un tri croissant placerait la Suisse en tête — le drapeau l'en empêche",
   tries[0]["pays"] in ("CH", "LI") and tries[0]["estimable"] is False,
   tries[0]["pays"])
ok("chaque pays sait combien de ses centres ont été chiffrés",
   all("dc_estimes" in x and "dc_non_estimes" in x for x in emp["par_pays"]))
ok("…et la somme des deux fait bien le parc",
   all(x["dc_estimes"] + x["dc_non_estimes"] == x["n_dc"] for x in emp["par_pays"]))
ok("les pays mesurés ne sont pas touchés par le drapeau",
   all(x["estimable"] for x in emp["par_pays"] if x["total_t"][1] > 0))
ok("la page écrit « non estimée » plutôt qu'un zéro",
   pan.count('"non estimée"') >= 3, pan.count('"non estimée"'))

print("\n══ 6. Ce que l'ouverture ne devait PAS déplacer ══\n")

ok("le référentiel des sites est intact", len(D.SITES) == 249, len(D.SITES))
ok("les 28 pays du parc sont inchangés",
   len({s["pays"] for s in D.SITES}) == 28)
ok("les dix critères de socle du comparateur sont intacts",
   [c["cle"] for c in impl["criteres"] if c["famille"] == "socle"]
   == ["carbone", "mix", "eau", "climat", "prix", "parc", "climat_physique",
       "feux", "inondations", "pipeline"],
   [c["cle"] for c in impl["criteres"] if c["famille"] == "socle"])
ok("…et six critères d'aléas s'y ajoutent",
   sum(1 for c in impl["criteres"] if c["famille"] == "aleas") == 6,
   len(impl["criteres"]))
ok("la France n'a pas bougé d'une note",
   pp["FR"]["notes"]["climat"] == 65 and pp["FR"]["notes"]["climat_physique"] == 21)
ok("les feux et inondations restent hors champ pour les trois",
   all(pp[c]["notes"]["feux"] is None and pp[c]["notes"]["inondations"] is None
       for c in TIERS))
ok("…et disent toujours que c'est un défaut de couverture, pas un bon score",
   all("hors du champ" in pp[c]["inondations_absence"] for c in TIERS))
ok("le panel de cas d'IA reste celui de l'Union",
   all(x["pays"] in P.PAYS_UE for x in P.CAS), P.sante()["n_cas"])
ok("aucun cas n'a été inventé pour les pays tiers",
   not [x for x in P.CAS if x["pays"] in TIERS])

print("\n══ 7. Discrimination : rien de tout cela n'existait avant ══\n")


def _avant(marqueur, fichier):
    hs = subprocess.check_output(
        ["git", "-C", DEPOT, "log", "-S", marqueur, "--format=%H", "--", fichier],
        text=True).split()
    ref = ("%s^" % hs[-1]) if hs else "HEAD"
    return subprocess.check_output(
        ["git", "-C", DEPOT, "show", "%s:%s" % (ref, fichier)], text=True)


av_ia = _avant("PAYS_TIERS", "panorama_ia.py")
ok("avant, aucun pays tiers n'existait au référentiel", "PAYS_TIERS" not in av_ia)
ok("…et la table des pays s'arrêtait aux Vingt-Sept", "PAYS_CARTE" not in av_ia)
av_i = _avant('"CH": ("bas", (70, 110))', "implantation.py")
ok("avant, la Suisse n'avait pas de prix", '"CH": ("bas"' not in av_i)
av_a = _avant("prix_origine", "app.py")
ok("avant, le prix de repli s'appliquait sans se nommer", "prix_origine" not in av_a)
ok("…alors que le repli lui-même existait déjà", "or [100, 150]" in av_a)
av_e = _avant("dc_estimes", "empreinte_sites.py")
# Le module SAVAIT deja qu'un site sans gabarit n'est pas estimable : la fiche
# de site le disait mot pour mot. C'est l'AGREGAT PAYS qui jetait ce verdict et
# additionnait des riens en un zero. Le contrôle porte donc sur la remontee, pas
# sur la connaissance — c'est la ou etait le defaut.
ok("avant, le site savait déjà qu'il n'était pas estimable",
   "non estimable" in av_e)
ok("…mais le pays ne comptait pas ses centres chiffrés",
   "dc_estimes" not in av_e)
ok("…et ne portait donc ni drapeau, ni motif",
   '"estimable"' not in av_e and "motif_non_estimable" not in av_e)
av_p = _avant("function estUE(", "panorama.html")
ok("avant, la page ne savait pas ce qu'était un pays tiers",
   "function estUE(" not in av_p)
ok("…et ne reliait pas `UE` au rafraîchissement de l'API",
   "UE=DATA.pays_ue||UE" not in av_p.replace(" ", ""))

print("")
print("%d contrôle(s) en échec\n" % ko if ko else "tout est vert\n")
sys.exit(1 if ko else 0)
