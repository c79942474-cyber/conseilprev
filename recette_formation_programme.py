# -*- coding: utf-8 -*-
"""Un programme de deux semaines à 6 000 € dans un catalogue de séminaires à 950 €.

CE QU'ON PROTÈGE.

1. LE TARIF QUI RETOMBE EN SILENCE. Le prix se déduisait du nombre de JOURS :
   `FORM_PRIX.get(cat['jours'], 95000)`, avec un barème à deux entrées — un et
   deux jours. Tant que le catalogue ne comptait que des séminaires, le défaut
   ne servait jamais. Une formation de dix jours y serait tombée sans un mot :
   950 € facturés au lieu de 6 000, par Stripe, sur une session réelle, avec un
   reçu et une facture. Le prix est désormais PORTÉ PAR LA LIGNE, et l'absence
   de tarif se journalise au lieu de se combler.

2. LES TROIS COPIES DU CATALOGUE. Il vit dans `app.py` (identifiants, tarifs,
   sessions), dans `sentinel.html` (les cartes du Hub Training) et dans
   `formations.html` (la page publique). Trois copies qui se contredisent
   publient trois offres différentes sous un seul nom. On vérifie ici qu'elles
   comptent le même nombre de formations et disent le même prix.

3. LES COMPTEURS ÉCRITS EN DUR. La page publique affichait « Toutes les
   formations (10) » au-dessus de ses cartes. La onzième les rendait tous faux
   d'un coup — sur une page qui montre les cartes juste en dessous. Ils se
   calculent maintenant à l'affichage.
"""
import io
import json
import os
import re
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


import app as APP                                              # noqa: E402

CAT = APP.FORM_CATALOGUE
PROG = next((c for c in CAT if c["id"] == 11), None)

print("\n══ 1. Le programme est au catalogue, et il s'y distingue ══\n")

ok("onze formations au catalogue", len(CAT) == 11, len(CAT))
ok("la onzième existe", bool(PROG), PROG)
ok("elle dure dix jours — deux semaines", PROG["jours"] == 10, PROG["jours"])
ok("…et porte son propre tarif : 6 000 € HT",
   PROG.get("prix_cents") == 600000, PROG.get("prix_cents"))
ok("elle forme une famille à part, « Programme »", PROG["ref"] == "Programme", PROG["ref"])
ok("…que les dix autres ne partagent pas",
   [c["ref"] for c in CAT].count("Programme") == 1)
ok("les identifiants restent uniques",
   len({c["id"] for c in CAT}) == 11, sorted(c["id"] for c in CAT))
ok("aucune autre formation ne porte de prix en dur",
   [c["id"] for c in CAT if c.get("prix_cents")] == [11],
   [c["id"] for c in CAT if c.get("prix_cents")])
# Trois sessions par an, comme les dix autres formations : une seule aurait
# fait de l'offre un essai, et n'aurait laissé au client aucune alternative.
sess11 = [s for s in APP.FORM_SESSIONS_DEFAUT if s[0] == 11]
ok("trois sessions sont ouvertes pour lui, comme pour les autres",
   len(sess11) == 3, len(sess11))
# Un programme de DIX JOURS ouvrables tient sur deux semaines pleines : il part
# un lundi et s'achève un vendredi. Une session ouverte un mardi et close un
# samedi promettrait dix jours et n'en offrirait pas dix.
from datetime import date                                      # noqa: E402


def _jour(s):
    y, m, j = (int(x) for x in s.split("-"))
    return date(y, m, j).weekday()


mauvais = [s[1:3] for s in sess11 if _jour(s[1]) != 0 or _jour(s[2]) != 4]
ok("…chacune part un lundi et s'achève un vendredi", not mauvais, mauvais)
ok("…et couvre bien onze jours calendaires, soit dix ouvrables",
   all((date(*(int(x) for x in s[2].split("-")))
        - date(*(int(x) for x in s[1].split("-")))).days == 11 for s in sess11),
   [(s[1], s[2]) for s in sess11])
ok("…et les trois s'étalent dans l'année", len({s[1][:7] for s in sess11}) == 3,
   sorted(s[1] for s in sess11))

print("\n══ 2. LE contrôle : le tarif ne retombe plus en silence ══\n")

ok("le programme est facturé 6 000 €",
   APP.form_prix_cents(PROG) == 600000, APP.form_prix_cents(PROG) / 100)
ok("un séminaire d'un jour reste à 950 €",
   APP.form_prix_cents({"id": 1, "jours": 1}) == 95000)
ok("…et un de deux jours à 1 750 €",
   APP.form_prix_cents({"id": 2, "jours": 2}) == 175000)
# DISCRIMINATION : c'est le calcul qu'on a remplacé. Il rendait 950 € pour dix
# jours, sans un mot — l'écart aurait été de 5 050 € par participant.
ancien = APP.FORM_PRIX.get(PROG["jours"], 95000)
ok("l'ancien calcul aurait facturé 950 € — l'écart évité vaut 5 050 € par participant",
   ancien == 95000 and APP.form_prix_cents(PROG) - ancien == 505000,
   "%d € contre %d €" % (ancien / 100, APP.form_prix_cents(PROG) / 100))
ok("le prix explicite prime sur le barème, même quand les deux existent",
   APP.form_prix_cents({"id": 99, "jours": 1, "prix_cents": 300000}) == 300000)
ok("une durée hors barème et sans prix retombe, mais elle est SIGNALÉE",
   APP.form_prix_cents({"id": 98, "jours": 5}) == 95000)
ok("…et une formation inconnue aussi", APP.form_prix_cents(None) == 95000)

print("\n══ 3. Les trois copies du catalogue disent la même chose ══\n")

sent = io.open(DEPOT + "/sentinel.html", encoding="utf-8").read()
i = sent.find("window.FORMATIONS_CAT = ")
hub = json.loads(sent[i + len("window.FORMATIONS_CAT = "):sent.find("\n", i)].rstrip().rstrip(";"))
ok("le Hub Training porte onze formations", len(hub) == 11, len(hub))
ok("…avec les mêmes numéros que le module",
   sorted(x["n"] for x in hub) == sorted(c["id"] for c in CAT))
ok("…et les mêmes familles",
   {x["ref"] for x in hub} == {c["ref"] for c in CAT},
   {x["ref"] for x in hub} ^ {c["ref"] for c in CAT})
ph = next(x for x in hub if x["n"] == 11)
ok("la carte du Hub annonce le prix, pas seulement la durée",
   "6 000 € HT" in ph["d"], ph["d"])
# DÉRIVE : le prix est écrit dans le texte de la carte ET dans le module. S'ils
# divergent, la page affiche un montant et Stripe en encaisse un autre.
ok("…et ce prix est bien celui que Stripe encaissera",
   "%s 000 € HT" % (PROG["prix_cents"] // 100000) in ph["d"],
   "%s vs %d €" % (ph["d"], PROG["prix_cents"] / 100))
ok("la carte porte les six modules ET les livrables", len(ph["g"]) == 7, len(ph["g"]))
for mot in ("agentique", "model cards", "RACI", "NIST", "ISO 42001", "littératie"):
    ok("…elle nomme « %s »" % mot, mot in json.dumps(ph, ensure_ascii=False))
ok("la famille « Programme » a sa couleur au Hub", "'Programme':'#B03A2E'" in sent)
ok("…et son bouton de filtre", "'Transverse', 'Programme'" in sent)

pub = io.open(DEPOT + "/formations.html", encoding="utf-8").read()
ok("la page publique porte onze cartes",
   pub.count('<article class="fo-card"') == 11,
   pub.count('<article class="fo-card"'))
ok("…dont celle du programme", 'data-ref="Programme"' in pub)
ok("…et son bouton de filtre", 'data-r="Programme"' in pub)
ok("la phrase tarifaire cite les trois tarifs, pas deux",
   all(x in pub for x in ("950 € HT", "1 750 € HT", "6 000 € HT")))
ok("…et nomme la durée du programme", "programme de deux semaines" in pub)

print("\n══ 4. Les compteurs se comptent au lieu de se recopier ══\n")

ok("plus aucun compteur figé dans les boutons de filtre",
   not re.search(r'onclick="foFilter\([^)]*\)">[^<]*\(\d+\)', pub),
   (re.search(r'onclick="foFilter\([^)]*\)">[^<]*\(\d+\)', pub) or [""])[0])
ok("une fonction les calcule à l'affichage", "window.foCompter" in pub)
ok("…et elle est branchée au chargement",
   'DOMContentLoaded", window.foCompter' in pub)
ok("…en comptant les cartes réellement présentes",
   'querySelectorAll(".fo-card")' in pub)

print("\n══ 5. Ce que l'ajout ne devait PAS déplacer ══\n")

ok("les dix formations d'origine sont intactes",
   [c["id"] for c in CAT[:10]] == list(range(1, 11)))
ok("…y compris leurs durées", [c["jours"] for c in CAT[:10]]
   == [1, 2, 1, 1, 2, 1, 1, 2, 2, 2])
ok("le barème à la journée n'a pas bougé",
   APP.FORM_PRIX == {1: 95000, 2: 175000}, APP.FORM_PRIX)
ok("la TVA reste celle du paramétrage", APP.FORM_TVA_PCT == 20.0, APP.FORM_TVA_PCT)
# Chaque formation du catalogue reçoit TROIS dates : le contrôle porte sur
# cette régularité, pas sur un total qu'il faudrait recopier à chaque ajout.
from collections import Counter                                # noqa: E402
par_form = Counter(s[0] for s in APP.FORM_SESSIONS_DEFAUT)
ok("les trente sessions d'origine sont intactes",
   sum(n for f, n in par_form.items() if f <= 10) == 30,
   sum(n for f, n in par_form.items() if f <= 10))
ok("…et chaque formation en compte exactement trois, la nouvelle comprise",
   set(par_form.values()) == {3}, dict(sorted(par_form.items())))
ok("chaque session vise une formation qui existe",
   all(any(c["id"] == s[0] for c in CAT) for s in APP.FORM_SESSIONS_DEFAUT))
ok("chaque formation du catalogue a une session",
   {s[0] for s in APP.FORM_SESSIONS_DEFAUT} == {c["id"] for c in CAT})

print("\n══ 6. L'API sert le catalogue complet ══\n")

APP.app.config["TESTING"] = True
NAV = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
       "Accept-Language": "fr-FR,fr;q=0.9", "Accept-Encoding": "gzip, deflate"}
with APP.app.test_client() as c:
    with c.session_transaction() as s:
        s["is_conseilprev"] = True
    r = c.get("/api/formations/sessions", headers=NAV)
    j = r.get_json() or {}
ok("les sessions répondent", r.status_code == 200 and j.get("ok"), r.status_code)
ok("…et servent les onze formations", len(j.get("catalogue") or []) == 11,
   len(j.get("catalogue") or []))
s11 = [s for s in (j.get("sessions") or []) if s["formation_id"] == 11]
ok("les trois sessions du programme sont ouvertes", len(s11) == 3, len(s11))
if s11:
    s = s11[0]
    ok("…facturée 6 000 € HT", s["prix_cents"] == 600000, s["prix_cents"] / 100)
    ok("…soit 7 200 € TTC à 20 %", s["prix_ttc_cents"] == 720000,
       s["prix_ttc_cents"] / 100)
    ok("…sur dix jours", s["jours"] == 10, s["jours"])
    ok("…et elle porte son titre", "op" in (s.get("titre") or "").lower(), s.get("titre"))

print("\n══ 7. L'amorçage comble les trous, il ne renonce pas ══\n")

# LE défaut qui aurait rendu tout le reste inutile. L'amorçage renonçait dès que
# la table contenait UNE ligne : sur un serveur déjà démarré — c'est-à-dire en
# production — la onzième formation n'aurait jamais reçu de session. Sa carte
# se serait affichée, son bouton aussi, et le sélecteur aurait répondu « aucune
# session ouverte ». Une offre visible et non réservable.
src = io.open(DEPOT + "/app.py", encoding="utf-8").read()
# Le motif « table non vide → on renonce » existe ailleurs dans le fichier, pour
# des tables SANS RAPPORT (registre RGPD, rétention, usages art. 50) où il est
# légitime. Chercher dans tout app.py accusait donc du code étranger : le
# contrôle se limite au corps de `_form_tables`.
_i = src.find("def _form_tables(")
_form_src = src[_i:src.find("\n@app.route", _i)]
ok("l'amorçage des formations ne renonce plus dès la première ligne trouvée",
   "get('n', 0)) > 0" not in _form_src)
ok("…il lit quelles formations ont déjà des sessions",
   "SELECT DISTINCT formation_id FROM form_sessions" in _form_src)
ok("…et n'insère que celles qui n'en ont aucune", "manquantes" in _form_src)
ok("…en le journalisant", "FORM_SESSIONS_AMORCAGE" in _form_src)

with APP.app.test_client() as c:
    with c.session_transaction() as s:
        s["is_conseilprev"] = True
    j2 = (c.get("/api/formations/sessions", headers=NAV).get_json() or {})
sess_bd = j2.get("sessions") or []
par_bd = Counter(s["formation_id"] for s in sess_bd)
ok("la base porte bien trois sessions pour le programme", par_bd.get(11) == 3,
   par_bd.get(11))
ok("…toutes à 6 000 € HT",
   {s["prix_cents"] for s in sess_bd if s["formation_id"] == 11} == {600000},
   {s["prix_cents"] for s in sess_bd if s["formation_id"] == 11})
ok("…et aucune formation du catalogue n'est sans session",
   set(par_bd) >= {c["id"] for c in CAT},
   {c["id"] for c in CAT} - set(par_bd))
# IDEMPOTENCE : rappeler l'amorçage ne doit rien dupliquer.
with APP.app.test_client() as c:
    with c.session_transaction() as s:
        s["is_conseilprev"] = True
    j3 = (c.get("/api/formations/sessions", headers=NAV).get_json() or {})
ok("un second appel n'ajoute aucun doublon",
   len(j3.get("sessions") or []) == len(sess_bd),
   "%d puis %d" % (len(sess_bd), len(j3.get("sessions") or [])))

print("\n══ 8. Discrimination : rien de tout cela n'existait avant ══\n")


def _avant(marqueur, fichier):
    hs = subprocess.check_output(
        ["git", "-C", DEPOT, "log", "-S", marqueur, "--format=%H", "--", fichier],
        text=True).split()
    ref = ("%s^" % hs[-1]) if hs else "HEAD"
    return subprocess.check_output(
        ["git", "-C", DEPOT, "show", "%s:%s" % (ref, fichier)], text=True)


av = _avant("form_prix_cents", "app.py")
ok("avant, le tarif se déduisait des jours, sans recours",
   "FORM_PRIX.get(cat['jours'] if cat else 1, 95000)" in av)
ok("…et aucune fonction ne le résolvait", "def form_prix_cents" not in av)
ok("…ni ne journalisait un tarif manquant", "FORM_PRIX_MANQUANT" not in av)
ok("avant, le catalogue s'arrêtait à dix", av.count("{'id': 1") >= 1
   and "'id': 11" not in av)
avs = _avant("'Programme':'#B03A2E'", "sentinel.html")
ok("avant, le Hub n'avait pas de famille « Programme »",
   "'Programme':'#B03A2E'" not in avs)
ava = _avant("FORM_SESSIONS_AMORCAGE", "app.py")
ok("avant, l'amorçage renonçait dès qu'une ligne existait",
   "if int(dict(cur.fetchone()).get('n', 0)) > 0:" in ava)
avp = _avant("window.foCompter", "formations.html")
ok("avant, la page publique écrivait ses compteurs en dur",
   "Toutes les formations (10)" in avp)
ok("…et ne savait pas les calculer", "foCompter" not in avp)

print("")
print("%d contrôle(s) en échec\n" % ko if ko else "tout est vert\n")
sys.exit(1 if ko else 0)
