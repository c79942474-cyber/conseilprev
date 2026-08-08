# -*- coding: utf-8 -*-
"""L'import PeeringDB, éprouvé sans réseau.

CE QU'ON PROTÈGE. Un import de masse peut apporter six cents lignes et
détruire ce qui fait la valeur des cent dix premières : il suffit qu'il
écrase une fiche vérifiée par un enregistrement déclaratif, qu'il laisse
passer un point non géocodé — le défaut exact qui avait fait retirer NTT
Francfort — ou qu'il annonce « 612 retenus » sans dire qu'il en a écarté 300.

Le jeu d'essai est donc construit pour PIÉGER : il contient un site hors
d'Europe, un sans coordonnées, un non géocodé, un doublon d'une ligne déjà
vérifiée, un doublon interne, une fiche supprimée, une sans exploitant, et
un point au milieu de l'Atlantique. Un import qui les accepte tous rendrait
un chiffre flatteur et faux.
"""
import io
import json
import os
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


import datacentres as D                                      # noqa: E402
import peeringdb_import as P                                 # noqa: E402


def fiche(**kw):
    """Une fiche PeeringDB minimale et valide, que chaque cas vient dégrader.
    Partir d'un gabarit valide isole le défaut testé : sinon un refus pourrait
    venir de n'importe quel champ manquant."""
    base = {"id": 1, "org_name": "Exemple SA", "name": "EX1", "city": "Hambourg",
            "country": "DE", "latitude": 53.55, "longitude": 9.99, "status": "ok",
            "geocode_status": True, "address1": "Musterstrasse 1", "zipcode": "20095",
            "net_count": 12, "ix_count": 2, "carrier_count": 3, "updated": "2026-05-14T10:00:00Z"}
    base.update(kw)
    return base


# Marcoussis : une ligne DÉJÀ vérifiée du référentiel (Data4). Un import qui
# la réintroduit ferait deux points sur le même campus.
MARCOUSSIS = [s for s in D.SITES if s["ville"] == "Marcoussis"][0]

JEU = [
    fiche(id=101),                                                    # retenu
    fiche(id=102, city="Milan", country="IT", latitude=45.51, longitude=9.21),
    fiche(id=103, city="Ashburn", country="US", latitude=39.04, longitude=-77.49),
    fiche(id=104, latitude=None, longitude=None),
    fiche(id=105, geocode_status=False, city="Gand", latitude=51.05, longitude=3.72),
    fiche(id=106, status="deleted", city="Lyon", country="FR", latitude=45.76, longitude=4.84),
    fiche(id=107, org_name="  ", city="Porto", country="PT", latitude=41.15, longitude=-8.61),
    fiche(id=108, city="Marcoussis", country="FR",
          latitude=MARCOUSSIS["lat"], longitude=MARCOUSSIS["lon"]),      # doublon référentiel
    fiche(id=109),                                                    # doublon interne de 101
    fiche(id=110, city="Milieu de l'Atlantique", country="PT", latitude=40.0, longitude=-40.0),
]

print("\n══ 1. Les pièges sont tous détectés, et nommés ══\n")

r = P.importer(JEU, existants=D.SITES)
rap = r["rapport"]
ok("dix fiches reçues", rap["recus"] == 10, rap["recus"])
ok("deux retenues", rap["retenus"] == 2, rap["retenus"])
for motif, attendu in (("hors_europe", 1), ("statut_non_actif", 1),
                       ("sans_coordonnees", 1), ("non_geocode", 1),
                       ("sans_exploitant", 1), ("doublon_referentiel", 1),
                       ("doublon_interne", 1), ("hors_fenetre", 1)):
    ok("%s : %d" % (motif.replace("_", " "), attendu),
       rap[motif] == attendu, rap[motif])
ok("le compte des écartés boucle",
   rap["ecartes"] == rap["recus"] - rap["retenus"] == 8, rap["ecartes"])
ok("aucune perte silencieuse : la somme des motifs égale les écartés",
   sum(rap[m] for m in P.MOTIFS) == rap["ecartes"],
   "%d vs %d" % (sum(rap[m] for m in P.MOTIFS), rap["ecartes"]))
ok("le résumé nomme les motifs, il ne les tait pas",
   "hors europe" in P.resume(rap) and "doublon" in P.resume(rap),
   P.resume(rap))

print("\n══ 2. Ce qui entre respecte le schéma du référentiel ══\n")

s = r["sites"][0]
ok("toutes les clés du référentiel sont présentes",
   set(P.CLES) - set(s) == set(), sorted(set(P.CLES) - set(s)))
ok("aucune clé étrangère au schéma, hors provenance",
   set(s) - set(P.CLES) == set(), sorted(set(s) - set(P.CLES)))
ok("l'exploitant vient de l'organisation déclarante", s["operateur"] == "Exemple SA")
ok("la source dit d'où elle vient et qui l'a inscrite",
   "PeeringDB" in s["source_libelle"] and "Exemple SA" in s["source_libelle"])
ok("le type de source est « registre », déjà libellé par la carte",
   s["source_type"] == "registre")

print("\n══ 3. Rien n'est deviné : ni puissance, ni gabarit, ni stade ══\n")

ok("aucune capacité", s["capacite_mw"] is None)
ok("aucun gabarit — donc aucune dérivation d'ordre de grandeur",
   s["gabarit"] is None)
est = D.estimer(s)
ok("le moteur répond « aucune dérivation possible », pas un chiffre",
   est["nature"] == "indisponible" and est["electricite"] is None, est["nature"])
ok("la note explique pourquoi le gabarit est absent",
   "aucune derivation possible" in s["note"])
ok("…et que la densité d'interconnexion n'est pas une taille",
   "PAS de sa taille" in s["note"])
ok("…et que le registre ignore les stades d'avancement",
   "ne distingue aucun stade" in s["note"])
ok("le statut est « service », faute de mieux, et c'est dit",
   s["statut"] == "service")

print("\n══ 4. Les deux origines restent distinctes ══\n")

ok("un site importé se déclare « registre »", s["provenance"] == "registre")
d = D.assemble()
# Le référentiel PORTE désormais les deux origines — c'est le but. Ce qui doit
# tenir, c'est qu'elles restent séparables, et que la part vérifiée n'ait pas
# bougé d'une ligne : un import qui rognerait sur elle serait une perte
# déguisée en enrichissement.
from collections import Counter as _C                          # noqa: E402
prov = _C(x["provenance"] for x in d["sites"])
ok("les deux origines cohabitent et se comptent",
   set(prov) == {"referentiel", "registre"}, dict(prov))
ok("la part établie une par une est intacte : 110",
   prov["referentiel"] == 110, prov["referentiel"])
ok("aucune ligne ne porte une provenance inconnue",
   all(x["provenance"] in ("referentiel", "registre") for x in d["sites"]))
# DISCRIMINATION : sans le marqueur, les deux seraient indiscernables.
ok("le marqueur est la SEULE chose qui les sépare dans la donnée",
   len({(x["operateur"], x["ville"]) for x in d["sites"]}) > 0
   and all(set(x) == set(d["sites"][0]) for x in d["sites"]))

print("\n══ 5. La coordonnée géocodée est le point de bascule ══\n")

sans = P.importer([fiche(id=201, geocode_status=False)], existants=[])
ok("géocodage exigé par défaut : la fiche est refusée",
   sans["rapport"]["retenus"] == 0 and sans["rapport"]["non_geocode"] == 1)
avec = P.importer([fiche(id=201, geocode_status=False)], existants=[],
                  exiger_geocodage=False)
ok("…et l'exigence est levable, explicitement",
   avec["rapport"]["retenus"] == 1)
ok("quatre décimales, parce qu'ici elles sont méritées",
   len(str(s["lat"]).split(".")[-1]) <= 4)

print("\n══ 6. Le seuil de doublon sépare deux bâtiments, pas deux adresses ══\n")

proche = P.importer([fiche(id=301, latitude=53.55, longitude=9.99),
                     fiche(id=302, latitude=53.5545, longitude=9.9955)], existants=[])
ok("à ~600 m, c'est le même site", proche["rapport"]["retenus"] == 1,
   proche["rapport"]["retenus"])
loin = P.importer([fiche(id=303, latitude=53.55, longitude=9.99),
                   fiche(id=304, latitude=53.60, longitude=10.05)], existants=[])
ok("à ~7 km, ce sont deux sites", loin["rapport"]["retenus"] == 2,
   loin["rapport"]["retenus"])
ok("la distance est calculée, pas approchée à plat",
   abs(P.distance_km(53.55, 9.99, 53.60, 10.05) - 6.9) < 1.2,
   round(P.distance_km(53.55, 9.99, 53.60, 10.05), 2))
ok("…et elle tient aux hautes latitudes, où le référentiel a de vrais sites",
   abs(P.distance_km(65.58, 22.15, 65.58, 22.30) - 6.9) < 1.0,
   round(P.distance_km(65.58, 22.15, 65.58, 22.30), 2))

print("\n══ 7. Le fichier déposé peut avoir plusieurs formes ══\n")

tmp = "/tmp/claude-0/-home-user-conseilprev/e6d7dc5d-fcdb-52f0-a89f-586f900c30d5/scratchpad"
for nom, contenu in (("liste.json", [fiche(id=401)]),
                     ("enveloppe.json", {"data": [fiche(id=402)]}),
                     ("pages.json", [{"data": [fiche(id=403)]},
                                     {"data": [fiche(id=404, latitude=48.85,
                                                     longitude=2.35, city="Paris",
                                                     country="FR")]}])):
    chemin = os.path.join(tmp, nom)
    io.open(chemin, "w", encoding="utf-8").write(json.dumps(contenu))
    n = P.importer(chemin, existants=[])["rapport"]["retenus"]
    ok("%s → %d site(s)" % (nom, 1 if nom != "pages.json" else 2),
       n == (2 if nom == "pages.json" else 1), n)

# LE DUMP COMPLET. C'est une autre forme que la réponse d'API : un objet par
# TYPE d'objet. Un lecteur qui n'attend que l'une des deux rend « aucun site
# trouvé » sur un fichier parfaitement valide — et ne dit pas laquelle il
# attendait, ce qui est le pire des deux mondes.
for nom, obj in (("dump-fac.json", {"fac": {"data": [fiche(id=501)]},
                                    "net": {"data": [{"asn": 64500}]}}),
                 ("dump-facility.json", {"facility": {"data": [fiche(id=502)]}}),
                 ("dump-cle-inconnue.json", {"installations": {"data": [fiche(id=503)]}}),
                 ("dump-net-avant.json", {"net": {"data": [{"asn": 64501, "name": "R"}]},
                                          "fac": {"data": [fiche(id=504)]}})):
    chemin = os.path.join(tmp, nom)
    io.open(chemin, "w", encoding="utf-8").write(json.dumps(obj))
    lu = P.charger(chemin)
    ok("%s → 1 installation" % nom, len(lu) == 1, len(lu))
    ok("…et c'est bien une installation, pas un réseau",
       bool(lu) and "latitude" in lu[0], sorted(lu[0])[:3] if lu else "-")

print("\n══ 8. La sortie s'insère telle quelle dans le référentiel ══\n")

txt = P.lignes_python(r["sites"])
ok("une ligne par site", txt.count("\n") + 1 == len(r["sites"]))
ok("le format est celui du fichier — dict indenté, virgule finale",
   txt.startswith(" {'operateur':") and txt.rstrip().endswith("},"))
# La vraie preuve : ce texte doit se relire comme du Python et redonner
# exactement les mêmes sites.
relu = eval("[" + txt + "]")                                  # noqa: S307
ok("le texte produit se relit et redonne les mêmes sites",
   relu == r["sites"], "%d relus" % len(relu))
ok("les clés y sont dans l'ordre du référentiel",
   list(relu[0].keys()) == P.CLES)

print("\n══ 9. L'URL de l'API est construite juste, sans être appelée ══\n")

u = P.fetch_api()
ok("la première page cible l'Europe et les fiches actives",
   "region_continent=Europe" in u[0] and "status=ok" in u[0], u[0])
ok("la pagination avance", "skip=0" in u[0] and "skip=250" in u[1])
ok("un filtre par pays remplace le filtre continent",
   "country=DE" in P.fetch_api(pays="DE")[0]
   and "region_continent" not in P.fetch_api(pays="DE")[0])
ok("le module n'exige aucun réseau pour fonctionner",
   P.sante()["reseau_requis"] is False)

print("\n══ 10. L'import RÉEL est en place, et reste distinguable ══\n")

from collections import Counter                               # noqa: E402
prov = Counter(x["provenance"] for x in d["sites"])
ok("249 sites au total", d["n_sites"] == 249, d["n_sites"])
ok("110 vérifiés, 139 importés", prov["referentiel"] == 110 and prov["registre"] == 139,
   dict(prov))
ok("28 pays", len({x["pays"] for x in d["sites"]}) == 28,
   len({x["pays"] for x in d["sites"]}))
ok("le cumul de puissance reste nul — le registre n'en publie pas",
   d["agregats"]["capacite_mw_cumulee"] == 0.0)
reg = [x for x in d["sites"] if x["provenance"] == "registre"]
ok("aucun site importé ne porte de gabarit",
   all(not x.get("gabarit") for x in reg))
ok("…donc aucun ne reçoit d'estimation d'électricité",
   all(x["estimation"]["nature"] == "indisponible" for x in reg))
ok("tous portent une source PeeringDB nommée",
   all("PeeringDB" in (x["source_libelle"] or "") for x in reg))
ok("tous avouent le niveau de preuve dans leur note",
   all("Preuve moyenne" in (x["note"] or "") for x in reg))
ok("aucun site fermé n'est passé",
   not [x for x in reg if "closed" in (x["nom_site"] or "").lower()],
   [x["nom_site"] for x in reg if "closed" in (x["nom_site"] or "").lower()][:2])
ok("ni la Russie ni l'Ukraine, hors périmètre déclaré",
   not [x for x in reg if x["pays"] in ("RU", "UA")])

print("\n══ 11. Les limites disent la cohabitation, la carte la montre ══\n")

lim = " ".join(d["limites"])
ok("les limites nomment les deux origines",
   "DEUX ORIGINES" in lim and "DISQUE CREUX" in lim and "DRAPEAU" in lim)
ok("…et disent que le registre n'apporte ni puissance ni stade",
   "ne distingue AUCUN stade" in lim)
ok("…et que trois fiches se déclaraient fermées en restant actives",
   "restant actives au registre" in lim)
ok("…et que c'est un annuaire d'interconnexion, donc biaisé",
   "annuaire d'INTERCONNEXION" in lim)
ok("le compte des limites suit le référentiel",
   "sur les 249 sites" in lim and "110 sites" not in lim)
pan = io.open(DEPOT + "/panorama.html", encoding="utf-8").read()
ok("la carte dessine un disque pour un enregistrement",
   'class="dc-reg"' in pan and 's.provenance === "registre"' in pan)
ok("…et la légende explique la différence",
   "inscrit par l" in pan and "source nommée (" in pan)
ok("le disque est creux, jamais plein", ".dc-reg{ fill:none" in pan)

import datacentres_idf as I                                   # noqa: E402
# L'import fait entrer neuf installations franciliennes dans le référentiel
# européen : la couche régionale en hérite mécaniquement, et c'est correct.
# Ce qui ne le serait pas, c'est de servir un total qui ne dise plus lequel
# de ces points a été vérifié.
a = I.assemble()
ok("la couche hérite désormais de 14 franciliens", a["n_herites"] == 14, a["n_herites"])
ok("…dont 5 établis un par un", a["n_herites_verifies"] == 5, a["n_herites_verifies"])
ok("…et 9 venus du registre", a["n_herites_registre"] == 9, a["n_herites_registre"])
ok("le manque annoncé se réduit d'autant",
   a["n_manquants"] == a["n_annonces"] - a["n_affiches"], a["n_manquants"])
ok("la santé publie aussi la part vérifiée",
   I.sante().get("n_herites_verifies") == 5)

print("")
print("%d contrôle(s) en échec\n" % ko if ko else "tout est vert\n")
sys.exit(1 if ko else 0)
