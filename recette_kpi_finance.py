"""EVA, ROCE, FCF — ce que le moteur doit refuser autant que ce qu'il calcule.

CE QUI EST ÉPROUVÉ ICI, ET DANS QUEL ORDRE :

  1. LES REFUS. Un module financier se juge d'abord sur ce qu'il refuse de
     dire. Sans revenu, sans coût du capital, sans taux d'impôt, les trois
     indicateurs ne valent pas zéro — ils ne sont pas instruits, et un zéro
     affiché à leur place se lirait « ce projet ne crée pas de valeur ».

  2. LES CALCULS, contre des cas dont la réponse se vérifie à la main.

  3. LES DEUX PIÈGES que ces indicateurs tendent à leur lecteur :
     · le ROCE monte tout seul avec l'amortissement ;
     · une fourchette d'enveloppe qui traverse zéro rend l'avis impossible,
       et c'est cette impossibilité qu'il faut dire.

  4. CE QUE LE MODULE N'INVENTE PAS : aucune référence sectorielle, aucun taux
     par défaut sur les grandeurs qui décident.

POUR L'EXÉCUTER :  python3 recette_kpi_finance.py
"""
import sys

import kpi_finance as K

ko = 0


def ok(nom, cond, detail=""):
    global ko
    print("  %s   %s%s" % ("OK " if cond else "KO ", nom,
                           (" — " + str(detail)) if detail else ""))
    if not cond:
        ko += 1


def titre(t):
    print("\n══ %s ══\n" % t)


CAPEX = [800.0, 1200.0]
OPEX = [60.0, 95.0]
COMPLET = {"revenu_meur_an": 210, "wacc": 8, "is_taux": 25, "montee_ans": 1}


# ── 1. Les refus ───────────────────────────────────────────────────────────
titre("1. CE QUE LE MOTEUR REFUSE DE DIRE")

vide = K.serie(CAPEX, OPEX, 10, {})
ok("sans hypothèses, rien n'est instruit", vide["instruit"] is False)
ok("…et aucune année n'est fabriquée", vide["annees"] == [], vide["annees"])
ok("…le message distingue « non instruit » de « zéro »",
   "pas zéro" in vide["message"] or "ne valent pas zéro" in vide["message"],
   vide["message"][:80])

trous = {m["cle"] for m in vide["manquantes"]}
ok("les trois hypothèses obligatoires sont nommées",
   trous == {"revenu_meur_an", "wacc", "is_taux"}, sorted(trous))
ok("…chacune porte une QUESTION, pas un nom de champ",
   all(m["question"].endswith("?") for m in vide["manquantes"]),
   [m["question"][:40] for m in vide["manquantes"]])

for cle in ("revenu_meur_an", "wacc", "is_taux"):
    partiel = dict(COMPLET)
    del partiel[cle]
    s = K.serie(CAPEX, OPEX, 10, partiel)
    ok("retirer %s suffit à tout bloquer" % cle, s["instruit"] is False)

ok("une chaîne vide ne devient pas zéro en chemin",
   K.serie(CAPEX, OPEX, 10, dict(COMPLET, wacc=""))["instruit"] is False)
ok("…un texte illisible non plus",
   K.serie(CAPEX, OPEX, 10, dict(COMPLET, is_taux="n/a"))["instruit"] is False)

lec_vide = K.lecture(vide)
ok("la lecture d'une série non instruite ne conclut rien",
   lec_vide["instruit"] is False and "indicateurs" not in lec_vide)


# ── 2. Les calculs ─────────────────────────────────────────────────────────
titre("2. LES CALCULS, vérifiés à la main")

# Cas net : CAPEX 1000 pile, OPEX 50 pile, revenu 200, amort 20 ans, IS 25 %,
# CMPC 8 %, pas de BFR, montée immédiate.
#   dotation = 1000/20 = 50 ; EBIT = 200 − 50 − 50 = 100
#   NOPAT = 75 ; capitaux employés an 1 = 1000
#   EVA = 75 − 80 = −5 ; ROCE = 100/1000 = 10 %
#   FCF = 75 + 50 − 10 (1 % de maintien) − 0 = 115
s = K.serie([1000, 1000], [50, 50], 10,
            {"revenu_meur_an": 200, "wacc": 8, "is_taux": 25, "montee_ans": 1,
             "amort_ans": 20, "maintien_part": 1, "bfr_meur": 0})
a1 = s["annees"][0]
ok("EBIT = revenu − OPEX − dotation", a1["ebit_meur"] == [100.0, 100.0],
   a1["ebit_meur"])
ok("capitaux employés an 1 = CAPEX (rien encore amorti)",
   a1["capitaux_employes_meur"] == [1000.0, 1000.0], a1["capitaux_employes_meur"])
ok("EVA = NOPAT − capitaux × CMPC = 75 − 80 = −5",
   a1["eva_meur"] == [-5.0, -5.0], a1["eva_meur"])
ok("ROCE = EBIT ÷ capitaux = 10 %", a1["roce_pct"] == [10.0, 10.0], a1["roce_pct"])
ok("FCF = NOPAT + dotation − maintien = 75 + 50 − 10 = 115",
   a1["fcf_meur"] == [115.0, 115.0], a1["fcf_meur"])

a2 = s["annees"][1]
ok("l'an 2, les capitaux employés ont baissé d'une dotation",
   a2["capitaux_employes_meur"] == [950.0, 950.0], a2["capitaux_employes_meur"])

# Le BFR entre bien dans les capitaux employés — l'oublier flatte ROCE et EVA.
sb = K.serie([1000, 1000], [50, 50], 3,
             {"revenu_meur_an": 200, "wacc": 8, "is_taux": 25, "montee_ans": 1,
              "amort_ans": 20, "bfr_meur": 100})
ok("le BFR entre dans les capitaux employés",
   sb["annees"][0]["capitaux_employes_meur"] == [1100.0, 1100.0],
   sb["annees"][0]["capitaux_employes_meur"])
ok("…et il dégrade donc l'EVA", sb["annees"][0]["eva_meur"][0] < -5.0,
   sb["annees"][0]["eva_meur"])

# La montée en charge s'applique au revenu, pas aux charges.
sm = K.serie([1000, 1000], [50, 50], 4,
             {"revenu_meur_an": 200, "wacc": 8, "is_taux": 25, "montee_ans": 4})
ok("la montée en charge fait croître le revenu",
   [l["revenu_meur"] for l in sm["annees"]] == [50.0, 100.0, 150.0, 200.0],
   [l["revenu_meur"] for l in sm["annees"]])
ok("…et la première année est donc la plus mauvaise",
   sm["annees"][0]["eva_meur"][1] < sm["annees"][-1]["eva_meur"][1])

# La fourchette est propagée, et dans le bon sens.
sf = K.serie(CAPEX, OPEX, 5, COMPLET)
l = sf["annees"][0]
ok("le cas BAS combine bien les charges hautes",
   l["eva_meur"][0] < l["eva_meur"][1] and l["ebit_meur"][0] < l["ebit_meur"][1],
   "%s / %s" % (l["ebit_meur"], l["eva_meur"]))
ok("…et les capitaux employés hauts viennent du CAPEX haut",
   l["capitaux_employes_meur"] == [800.0, 1200.0], l["capitaux_employes_meur"])


# ── 3. Les deux pièges ─────────────────────────────────────────────────────
titre("3. LES DEUX PIÈGES QUE CES INDICATEURS TENDENT")

# Piège 1 — le ROCE monte tout seul. Revenu constant : toute hausse est
# mécanique, et le moteur doit le dire.
sp = K.serie([1000, 1000], [50, 50], 10,
             {"revenu_meur_an": 200, "wacc": 8, "is_taux": 25, "montee_ans": 1,
              "amort_ans": 20})
roce = [i for i in K.lecture(sp)["indicateurs"] if i["cle"] == "roce"][0]
ok("à revenu CONSTANT, le ROCE net monte quand même",
   sp["annees"][-1]["roce_pct"][0] > sp["annees"][0]["roce_pct"][0],
   "%s → %s" % (sp["annees"][0]["roce_pct"][0], sp["annees"][-1]["roce_pct"][0]))
ok("…le ROCE à capitaux BRUTS, lui, ne bouge pas",
   sp["annees"][-1]["roce_brut_pct"] == sp["annees"][0]["roce_brut_pct"],
   sp["annees"][-1]["roce_brut_pct"])
ok("LE MOTEUR DIT QUE LA HAUSSE EST MÉCANIQUE", "alerte" in roce,
   roce.get("alerte", "aucune alerte — le lecteur croira à un progrès")[:90])

# Et l'inverse : une vraie amélioration ne doit PAS être signalée comme fausse.
sv = K.serie([1000, 1000], [50, 50], 10,
             {"revenu_meur_an": 200, "wacc": 8, "is_taux": 25, "montee_ans": 6,
              "amort_ans": 20})
roce_v = [i for i in K.lecture(sv)["indicateurs"] if i["cle"] == "roce"][0]
ok("une hausse RÉELLE n'est pas dénoncée comme mécanique",
   "alerte" not in roce_v,
   "brute : " + roce_v.get("tendance_brute", "?"))

# Piège 2 — la fourchette traverse le seuil : aucun avis possible.
eva_t = [i for i in K.lecture(K.serie(CAPEX, OPEX, 10, COMPLET))["indicateurs"]
         if i["cle"] == "eva"][0]
ok("une fourchette qui traverse zéro rend l'EVA INDÉCIDABLE",
   eva_t["verdict"] == "indecidable", "%s %s" % (eva_t["verdict"], eva_t["fourchette"]))
ok("…et le moteur dit ce qu'il faudrait resserrer",
   "devis" in eva_t["dit"], eva_t["dit"][-90:])

# Fourchette entièrement au-dessus : là, il tranche.
eva_p = [i for i in K.lecture(K.serie([700, 750], [50, 55], 10, COMPLET))["indicateurs"]
         if i["cle"] == "eva"][0]
ok("une fourchette entièrement positive donne un avis franc",
   eva_p["verdict"] == "favorable", "%s %s" % (eva_p["verdict"], eva_p["fourchette"]))
eva_n = [i for i in K.lecture(K.serie([1800, 2000], [140, 160], 10, COMPLET))["indicateurs"]
         if i["cle"] == "eva"][0]
ok("…et une fourchette entièrement négative aussi",
   eva_n["verdict"] == "defavorable", "%s %s" % (eva_n["verdict"], eva_n["fourchette"]))


# ── 4. Un point ne décide rien ─────────────────────────────────────────────
titre("4. UN POINT NE DÉCIDE RIEN, ET LE MOTEUR LE DIT")

un = K.lecture(K.serie(CAPEX, OPEX, 1, COMPLET))
ok("sur un seul exercice, une réserve explicite est posée",
   any("un point" in r or "évolution" in r for r in un["reserves"]),
   un["reserves"][0][:90])
plusieurs = K.lecture(K.serie(CAPEX, OPEX, 10, COMPLET))
ok("…et elle disparaît dès qu'il y a une trajectoire",
   not any("Un seul exercice" in r for r in plusieurs["reserves"]))
ok("chaque indicateur porte sa tendance",
   all("tendance" in i for i in plusieurs["indicateurs"]),
   [i["tendance"] for i in plusieurs["indicateurs"]])


# ── 5. Ce que le module n'invente pas ──────────────────────────────────────
titre("5. CE QUE LE MODULE N'INVENTE PAS")

lec = K.lecture(K.serie(CAPEX, OPEX, 10, COMPLET))
sans = [i for i in lec["indicateurs"] if i.get("atteint") == "non_compare"]
ok("sans objectif, aucun indicateur n'est déclaré atteint",
   len(sans) == len(lec["indicateurs"]), len(sans))
ok("…et le module DIT qu'il n'invente pas de référence sectorielle",
   all("inventée" in i["sans_cible"] for i in sans),
   sans[0]["sans_cible"][:90] if sans else "")

avec = K.lecture(K.serie(CAPEX, OPEX, 10, COMPLET), cibles={"roce": 12})
roce_c = [i for i in avec["indicateurs"] if i["cle"] == "roce"][0]
ok("un objectif fourni est repris et comparé",
   roce_c.get("cible") == 12 and roce_c["atteint"] in ("oui", "non", "incertain"),
   "%s → %s" % (roce_c.get("cible"), roce_c.get("atteint")))
ok("…et l'écart est chiffré", "ecart_cible" in roce_c, roce_c.get("ecart_cible"))

ok("aucun taux par défaut sur les grandeurs qui décident",
   not (set(K.DEFAUTS) & {"revenu_meur_an", "wacc", "is_taux"}),
   sorted(K.DEFAUTS))
ok("les trois pièges sont écrits et substantiels",
   all(len(m["piege"]) >= 80 for m in K.INDICATEURS.values()),
   {k: len(m["piege"]) for k, m in K.INDICATEURS.items()})
ok("ce qui reste à faire est écrit, avec ce qui manque pour le faire",
   len(K.SUITE) >= 4 and all(s["manque"] for s in K.SUITE),
   [s["quoi"] for s in K.SUITE])


# ── 6. Le contrat servi à la page ──────────────────────────────────────────
titre("6. LE CONTRAT SERVI À LA PAGE")

r = K.referentiel()
ok("l'ordre est servi comme LISTE, pas comme dictionnaire",
   isinstance(r["ordre"], list) and r["ordre"] == ["eva", "roce", "fcf"],
   r["ordre"])
ok("…et l'EVA ouvre la lecture", r["ordre"][0] == "eva")
ok("chaque entrée porte sa question et son motif",
   all(e["question"] and e["pourquoi"] for e in r["entrees"]))
ok("la portée du module est déclarée", "sectorielle" in K.sante()["portee"],
   K.sante()["portee"][:70])

print("\n" + (("%d contrôle(s) en échec" % ko) if ko else "tout est vert") + "\n")
sys.exit(1 if ko else 0)
