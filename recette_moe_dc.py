"""HONORAIRES DE MAÎTRISE D'ŒUVRE — ce que le barème doit tenir.

CE QUI EST ÉPROUVÉ, ET POURQUOI DANS CET ORDRE :

  1. L'ASSIETTE. C'est la première erreur possible, et la plus coûteuse :
     calculer les honoraires sur l'enveloppe entière au lieu des travaux gonfle
     la note d'environ un huitième sans que rien ne le signale.

  2. LES DEUX BARÈMES. Même mission, taux très différents sur le clos-couvert
     et sur le lot technique — d'un facteur huit pour l'architecte, quatre pour
     les fluides, dix pour le commissioning. Un taux unique se tromperait dans
     les deux sens à la fois.

  3. LE CHOIX DES PHASES. C'est la demande : chiffrer ce que le client confie
     réellement. Retirer une phase doit retirer sa part, et RIEN d'autre.

  4. CE QUE LE CALCULATEUR NE DOIT PAS FAIRE. Présenter une économie sans sa
     contrepartie, et présenter comme optionnelles deux missions qui relèvent
     d'obligations légales.

POUR L'EXÉCUTER :  python3 recette_moe_dc.py
"""
import sys

import finance_dc as F
import moe_dc as M

ko = 0


def ok(nom, cond, detail=""):
    global ko
    print("  %s   %s%s" % ("OK " if cond else "KO ", nom,
                           (" — " + str(detail)) if detail else ""))
    if not cond:
        ko += 1


def titre(t):
    print("\n══ %s ══\n" % t)


PARTS = {l["code"]: (l["part"][0] + l["part"][1]) / 2 for l in F.LOTS}
ENV = [800.0, 1200.0]


# ── 1. L'assiette ──────────────────────────────────────────────────────────
titre("1. L'ASSIETTE — les honoraires ne portent pas sur l'enveloppe")

A = M.assiettes(PARTS, ENV)
travaux = A["clos_couvert_meur"][1] + A["technique_meur"][1]
ok("l'assiette est plus PETITE que l'enveloppe", travaux < ENV[1],
   "%.0f M€ de travaux pour %.0f M€ d'enveloppe" % (travaux, ENV[1]))
ok("…et l'écart est dit en clair", "exclut" in A["note"], A["note"][:70])
ok("la maîtrise d'œuvre elle-même est hors assiette", "00" in M.LOTS_EXCLUS)
ok("…avec sa raison écrite", "honoraires sur des honoraires" in M.LOTS_EXCLUS["00"])
ok("la provision pour aléas aussi", "13" in M.LOTS_EXCLUS,
   M.LOTS_EXCLUS.get("13", "")[:60])
ok("aucun lot n'est à la fois compté et exclu",
   not (set(M.LOTS_EXCLUS) & (set(M.LOTS_CLOS_COUVERT) | set(M.LOTS_TECHNIQUE))))
ok("le lot technique pèse plus que le clos-couvert — c'est un centre de "
   "données", A["technique_meur"][1] > A["clos_couvert_meur"][1],
   "%.0f vs %.0f M€" % (A["technique_meur"][1], A["clos_couvert_meur"][1]))


# ── 2. Les deux barèmes ────────────────────────────────────────────────────
titre("2. DEUX ASSIETTES, DEUX BARÈMES — et l'écart est énorme")

arch = next(m for m in M.MISSIONS if m["cle"] == "architecte")
flu = next(m for m in M.MISSIONS if m["cle"] == "bet_fluides")
com = next(m for m in M.MISSIONS if m["cle"] == "commissioning")
ok("l'architecte pèse BEAUCOUP plus sur le clos-couvert",
   arch["taux_sc"] >= 6 * arch["taux_mep"],
   "%.1f %% vs %.1f %%" % (arch["taux_sc"] * 100, arch["taux_mep"] * 100))
ok("les fluides, EUX, pèsent plus sur le lot technique",
   flu["taux_mep"] >= 3 * flu["taux_sc"],
   "%.1f %% vs %.1f %%" % (flu["taux_mep"] * 100, flu["taux_sc"] * 100))
ok("le commissioning est presque tout entier sur la technique",
   com["taux_mep"] >= 8 * com["taux_sc"],
   "%.1f %% vs %.1f %%" % (com["taux_mep"] * 100, com["taux_sc"] * 100))

# Un taux unique appliqué à l'ensemble donnerait un résultat différent : c'est
# ce qui justifie la complication.
r = M.honoraires(PARTS, ENV)
plat = (arch["taux_sc"] + arch["taux_mep"]) / 2 * travaux
reel = next(l for l in r["missions"] if l["cle"] == "architecte")["montant_meur"][1]
ok("un taux moyen unique se tromperait sur l'architecte",
   abs(plat - reel) / max(reel, 1e-9) > 0.25,
   "%.1f M€ au taux moyen contre %.1f M€ au barème" % (plat, reel))


# ── 3. Le choix des phases ─────────────────────────────────────────────────
titre("3. LE CHOIX DES PHASES — c'est la demande")

tout = M.honoraires(PARTS, ENV)
concept = M.honoraires(PARTS, ENV, phases=["aps", "apd", "pro"])
ok("retirer des phases fait baisser la note",
   concept["total_meur"][1] < tout["total_meur"][1],
   "%.1f → %.1f M€" % (tout["total_meur"][1], concept["total_meur"][1]))
ok("…et les phases écartées sont nommées",
   concept["phases_ecartees"] == ["act", "exe"], concept["phases_ecartees"])

# La somme des phases retenues doit faire le total : rien ne doit se perdre.
somme = sum(tout["par_phase"][p][1] for p in M.ORDRE_PHASES)
ok("la somme des phases fait bien le total",
   abs(somme - tout["total_meur"][1]) < 0.05,
   "%.2f vs %.2f M€" % (somme, tout["total_meur"][1]))

# Et retirer une phase doit retirer EXACTEMENT sa part, ni plus ni moins.
sans_exe = M.honoraires(PARTS, ENV, phases=["aps", "apd", "pro", "act"])
attendu = tout["total_meur"][1] - tout["par_phase"]["exe"][1]
ok("retirer une phase retire exactement sa part",
   abs(sans_exe["total_meur"][1] - attendu) < 0.05,
   "%.2f attendu, %.2f obtenu" % (attendu, sans_exe["total_meur"][1]))

ok("LE CHANTIER EST LE GROS DU BARÈME — et c'est ce qui se décide en le "
   "décochant",
   tout["par_phase"]["exe"][1] > 0.5 * tout["total_meur"][1],
   "%.0f %% des honoraires en phase EXE"
   % (tout["par_phase"]["exe"][1] / tout["total_meur"][1] * 100))

# VIDE N'EST PAS ABSENT — et le contrôle a trouvé la confusion.
# `phases=[]` (rien coché) et `phases=None` (pas de filtre) donnaient le MÊME
# résultat : la mission complète. Une liste vide étant fausse en Python, tout
# décocher facturait tout.
vide = M.honoraires(PARTS, ENV, phases=[])
ok("aucune phase cochée : le module refuse plutôt que de tout facturer",
   vide["ok"] is False and "absence de mission" in vide.get("message", ""),
   vide.get("message", "") [:80] or "a rendu %s M€" % vide.get("total_meur"))
defaut = M.honoraires(PARTS, ENV, phases=None)
ok("…alors que ne PAS filtrer prend bien toutes les phases",
   defaut["ok"] and defaut["phases_retenues"] == M.ORDRE_PHASES,
   defaut["phases_retenues"])
vide_m = M.honoraires(PARTS, ENV, missions=[])
ok("même nuance sur les missions : rien coché n'est pas tout prendre",
   vide_m["ok"] and {l["cle"] for l in vide_m["missions"]} == set(M.OBLIGATOIRES),
   sorted(l["cle"] for l in vide_m["missions"]))


# ── 4. Ce que le calculateur ne doit pas faire ─────────────────────────────
titre("4. CE QU'UN CALCULATEUR D'HONORAIRES NE DOIT PAS FAIRE")

c = M.consequences(["aps", "apd", "pro"])
ok("chaque phase écartée dit ce qu'on perd", len(c) == 2, [x["cle"] for x in c])
ok("…et pas en trois mots", all(len(x["sans"]) >= 60 for x in c),
   min(len(x["sans"]) for x in c))
ok("…ni sans dire ce que la phase produisait",
   all(len(x["produit"]) >= 40 for x in c))

partiel = M.honoraires(PARTS, ENV, missions=["architecte", "bet_fluides"])
imposees = {i["cle"] for i in partiel["imposees"]}
ok("LES MISSIONS OBLIGATOIRES SONT COMPTÉES MÊME DÉCOCHÉES",
   imposees == {"sps", "controle_technique"}, sorted(imposees))
ok("…et chacune porte la référence du texte",
   all(i["obligation"].get("reference") for i in partiel["imposees"]),
   [i["obligation"]["reference"][:34] for i in partiel["imposees"]])
noms = {l["cle"] for l in partiel["missions"]}
ok("…elles figurent donc bien dans le chiffrage", {"sps"} <= noms,
   sorted(noms))
ok("…et y sont marquées comme imposées",
   next(l for l in partiel["missions"] if l["cle"] == "sps")["impose"] is True)


# ── 5. Vos offres priment sur le relevé ────────────────────────────────────
titre("5. VOS OFFRES PRIMENT SUR LE RELEVÉ")

perso = M.honoraires(PARTS, ENV, taux_perso={"architecte": {"sc": 0.02, "mep": 0.002}})
a_ref = next(l for l in tout["missions"] if l["cle"] == "architecte")["montant_meur"][1]
a_new = next(l for l in perso["missions"] if l["cle"] == "architecte")
ok("un taux saisi remplace celui du barème", a_new["montant_meur"][1] < a_ref,
   "%.1f → %.1f M€" % (a_ref, a_new["montant_meur"][1]))
ok("…et la ligne dit que le taux vient de vous", a_new["taux_saisi"] is True)
ok("les autres missions ne bougent pas",
   next(l for l in perso["missions"] if l["cle"] == "opc")["montant_meur"]
   == next(l for l in tout["missions"] if l["cle"] == "opc")["montant_meur"])


# ── 6. Le barème se tient ──────────────────────────────────────────────────
titre("6. LE BARÈME SE TIENT, ET IL DIT D'OÙ IL VIENT")

ok("treize missions", len(M.MISSIONS) == 13, len(M.MISSIONS))
ok("cinq phases", len(M.PHASES) == 5, [p["cle"] for p in M.PHASES])
for m in M.MISSIONS:
    s = sum(m["repartition"].values())
    if abs(s - 1.0) > 1e-6:
        ok("répartition de %s" % m["cle"], False, s)
ok("chaque répartition de phases somme à 1", True, "13/13")
ok("la source est nommée ET datée", "2018" in M.SOURCE["origine"],
   M.SOURCE["origine"][:60])
ok("…et sa portée est bornée : UN projet, pas un marché",
   "n'est pas un marché" in M.SOURCE["reserve"], M.SOURCE["reserve"][:60])
ok("l'anonymisation est déclarée",
   "marge" in M.SOURCE["anonymisation"] and "chiffre d'affaires" in M.SOURCE["anonymisation"],
   M.SOURCE["anonymisation"][:70])
ok("le taux effectif reste dans la plage d'un barème réel",
   3.0 <= tout["taux_effectif_pct"][1] <= 15.0,
   "%.1f %% des travaux" % tout["taux_effectif_pct"][1])


# ── 7. POURCENTAGES OU FRACTIONS — l'erreur d'unité qui vaut cent ──────────
titre("7. L'ERREUR D'UNITÉ QUI VAUT CENT")

# Le devis sert les parts en POURCENTAGE ; le barème raisonne en fractions.
# La route normalise sur la SOMME, qui vaut 1 dans un cas et 100 dans l'autre.
import app as A  # noqa: E402

# LA CLE DE SESSION EST « is_conseilprev », pas un plan d'abonnement. Mon
# premier jet posait « client_acces » : la route repondait 401 et je l'ai
# d'abord lu comme une panne de la route, alors que c'est ma session qui
# n'existait pas.
_c = A.app.test_client()
with _c.session_transaction() as _s:
    _s["is_conseilprev"] = True


def _post(charge):
    return _c.post("/api/moe-dc", json=charge,
                   headers={"Origin": "http://localhost"})


pct = {l["code"]: (l["part"][0] + l["part"][1]) / 2 * 100 for l in F.LOTS}
frac = {k: v / 100.0 for k, v in pct.items()}
r_pct = _post({"enveloppe_meur": ENV, "parts_lots": pct})
r_frac = _post({"enveloppe_meur": ENV, "parts_lots": frac})
if r_pct.status_code == 200 and r_frac.status_code == 200:
    a, b = r_pct.get_json(), r_frac.get_json()
    ok("des parts en POURCENTAGE donnent le même résultat qu'en fractions",
       a["total_meur"] == b["total_meur"],
       "%s vs %s M€" % (a["total_meur"], b["total_meur"]))
    ok("…et l'assiette ne dépasse jamais l'enveloppe",
       a["travaux_meur"][1] <= ENV[1] + 0.01,
       "%.0f M€ de travaux pour %.0f d'enveloppe"
       % (a["travaux_meur"][1], ENV[1]))
else:
    ok("la route répond", False,
       "HTTP %s / %s" % (r_pct.status_code, r_frac.status_code))

vide = _post({"enveloppe_meur": ENV, "parts_lots": pct, "phases": []})
ok("aucune phase cochée : la route refuse en 400, sans rien facturer",
   vide.status_code == 400 and vide.get_json().get("error") == "aucune_phase",
   "HTTP %s" % vide.status_code)
sans_env = _post({"parts_lots": pct})
ok("sans enveloppe, la route dit qu'il faut la calculer d'abord",
   sans_env.status_code == 400
   and "travaux" in sans_env.get_json().get("message", ""),
   sans_env.get_json().get("message", "")[:60])

print("\n" + (("%d contrôle(s) en échec" % ko) if ko else "tout est vert") + "\n")
sys.exit(1 if ko else 0)
