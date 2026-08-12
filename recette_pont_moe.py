# -*- coding: utf-8 -*-
"""Le pont vers le chiffrage de MOE — ce qu'il porte, et ce qu'il n'a pas le
droit de porter en silence.

CE PONT EST DIFFERENT DE L'AUTRE, ET C'EST TOUT LE SUJET. Le lien vers l'etude
de durabilite jure de ne porter AUCUN MONTANT ; celui-ci porte une assiette de
travaux, parce que c'est ce qu'on lui demande de transporter. Un module qui
transporterait un montant sans le dire serait le vrai defaut — pas le montant
lui-meme.

CE QUE CETTE RECETTE PROTEGE :

  1. LE CONTRAT NE PEUT PAS DERIVER EN SILENCE. Les noms des parametres
     appartiennent au formulaire de l'AUTRE site. Changes ici sans l'etre
     la-bas, le lien continue de FONCTIONNER et ne pre-remplit plus rien : le
     visiteur arrive sur un formulaire vide et croit a un simple raccourci.

  2. LE MONTANT EST ANNONCE ET ARRONDI. Annonce, parce qu'une URL se colle
     dans un courriel. Arrondi, parce qu'une enveloppe au millier pres se
     recoupe avec un devis.

  3. RIEN DE NOMINATIF NE VOYAGE, meme construit depuis une reponse COMPLETE
     de l'enveloppe — qui contient des dossiers entiers, des ecarts entre pays
     et des noms de lots.

  4. FRACTION OU POURCENTAGE NE SE CONFONDENT PAS. Les deux circulent dans ce
     depot ; les melanger multiplie l'assiette technique par cent.

  5. UN REFUS NE FAIT PAS ECHOUER LE LIEN, ET IL SE DIT.

  POUR L'EXECUTER :  python3 recette_pont_moe.py
"""
import sys

import pont_moe as P

ko = 0


def ok(nom, cond, detail=""):
    global ko
    print("  " + ("OK " if cond else "KO ") + "   " + nom
          + (" — " + str(detail) if detail else ""))
    if not cond:
        ko += 1


def titre(t):
    print("\n== " + t + " ==\n")


titre("1. Le contrat, fige — il appartient a l'autre site")

ok("la cible est le bloc de MOE de l'ingenierie de projet",
   P.BASE == "https://conseilprevcyber.onrender.com"
   and P.CHEMIN == "/ingenierie-datacenter" and P.ANCRE == "ig-moe",
   P.BASE + P.CHEMIN + "#" + P.ANCRE)
ok("les trois parametres portent les noms attendus la-bas",
   sorted(P.CHAMPS) == ["part_technique", "pays", "travaux_meur"],
   sorted(P.CHAMPS))
ok("chacun dit son unite et sa provenance",
   all((c.get("unite") or "").strip() and (c.get("de") or "").strip()
       for c in P.CHAMPS.values()))

titre("2. LE POINT QUI DECIDE : le montant est annonce, pas glisse")

r = P.lien(travaux_meur=[612.437, 761.281], part_technique=0.6238, pays="fr")
ok("l'avertissement nomme le montant transporte",
   "MONTANT" in r["avertissement"], r["avertissement"][:64] + "...")
ok("...et dit ou une URL se retrouve",
   "courriel" in r["avertissement"] and "journ" in r["avertissement"])
ok("le montant est ARRONDI a la centaine de milliers d'euros",
   "612.4-761.3" in r["url"], r["url"].split("?")[1].split("#")[0])
ok("...et l'arrondi est dit au lecteur",
   any("arrondi" in (x.get("reserve") or "") for x in r["porte"]))

titre("3. Ce qui voyage, et ce qui ne voyage pas")

champs = {x["champ"] for x in r["porte"]}
ok("les trois grandeurs demandees sont portees", len(champs) == 3, champs)
ok("le pays est porte POUR MEMOIRE, et le bareme ne s'en sert pas",
   any(x["champ"].startswith("Pays") and "ne varie pas" in (x.get("reserve") or "")
       for x in r["porte"]))
ok("la liste de ce qui ne voyage pas est servie avec", len(r["exclus"]) >= 4)
ok("...et elle exclut le nominatif",
   any("client" in e.lower() for e in r["exclus"])
   and any("session" in e.lower() for e in r["exclus"]))

titre("4. Rien de nominatif, meme depuis une reponse COMPLETE d'enveloppe")

# Une reponse d'enveloppe telle que l'API la rend : dossiers entiers, ecarts,
# noms de lots. On ne construit le lien qu'a partir des trois valeurs prevues.
REPONSE = {
    "entree": {"mw": 100, "pays": ["FR", "SE"]},
    "classement": [{"pays": "FR", "tco_meur": [1268.9, 2135.5]}],
    "dossiers": [{"pays": "FR", "devis": {
        "enveloppe_meur": [736.0, 920.0],
        "lots": [{"code": "01", "nom": "Gros oeuvre — site de Meudon", "part": 22.1},
                 {"code": "05", "nom": "Groupes froid Carrier", "part": 18.4},
                 {"code": "00", "nom": "Maitrise d'oeuvre", "part": 8.0},
                 {"code": "13", "nom": "Provision pour aleas", "part": 5.0}]}}],
    "ecarts": [{"a": {"pays": "FR"}, "b": {"pays": "SE"}, "note": "confidentiel"}],
}
d = REPONSE["dossiers"][0]
parts = {l["code"]: l["part"] / 100 for l in d["devis"]["lots"]}
assiette = sum(v for k, v in parts.items() if k not in ("00", "13"))
env = d["devis"]["enveloppe_meur"]
lien = P.lien(travaux_meur=[env[0] * assiette, env[1] * assiette],
              part_technique=parts.get("05", 0),
              pays=REPONSE["classement"][0]["pays"])
url = lien["url"]
# ON FOUILLE LA REQUETE, PAS L'ADRESSE ENTIERE. Ma premiere version cherchait
# « SE » dans toute l'URL et le trouvait dans « conSEilprevcyber » : un
# controle qui accuse le nom de domaine ne prouve rien et se fait ignorer.
requete = url.split("?", 1)[1].split("#", 1)[0] if "?" in url else ""
valeurs = [p.split("=", 1)[1] for p in requete.split("&") if "=" in p]
interdits = ["Meudon", "Carrier", "gros", "oeuvre", "aleas", "2135"]
fuites = [m for m in interdits
          if any(m.lower() in v.lower() for v in valeurs)]
ok("AUCUN NOM DE SITE NI DE FOURNISSEUR NE PASSE", not fuites, fuites)
ok("...et le pays COMPARE ne part pas — seul celui retenu",
   "SE" not in valeurs, valeurs)
ok("...et le coût total de possession non plus",
   not any("1268" in v for v in valeurs))
ok("le lien porte bien l'assiette, pas l'enveloppe brute",
   "736" not in url and "920" not in url, url.split("?")[1])

titre("5. Fraction et pourcentage ne se confondent pas")

a = P.lien(part_technique=0.624)["url"]
b = P.lien(part_technique=62.4)["url"]
ok("0,624 et 62,4 donnent la MEME part transmise", a == b,
   a.split("?")[1] + " / " + b.split("?")[1])
ok("une part impossible est refusee, pas transmise",
   P.lien(part_technique=180)["refuses"], P.lien(part_technique=180)["refuses"])

titre("6. Un refus ne fait pas echouer le lien, et il se dit")

r2 = P.lien(travaux_meur=650, part_technique=0.6, pays="france")
ok("le pays douteux est refuse", any(x["champ"].startswith("Pays")
                                     for x in r2["refuses"]))
ok("...mais le montant et la part passent quand meme", len(r2["porte"]) == 2,
   [x["champ"] for x in r2["porte"]])
ok("...et le lien reste utilisable", r2["url"].endswith("#" + P.ANCRE))

r3 = P.lien(travaux_meur="beaucoup")
ok("un montant illisible est nomme, pas devine", r3["refuses"])
ok("...et le lien sans rien a porter le dit", P.lien()["vide"])

r4 = P.lien(travaux_meur=10_000_000)
ok("un montant hors bornes ne part pas", r4["refuses"] and not r4["porte"],
   r4["refuses"])

titre("7. L'AUTRE pont ne ment plus sur les montants")

import pont_dc

ok("pont_dc qualifie sa promesse « aucun montant »",
   any("CE lien" in e for e in pont_dc.EXCLUS),
   [e[:52] for e in pont_dc.EXCLUS if "montant" in e])
ok("...et renvoie vers celui qui, lui, porte l'assiette",
   any("maîtrise d'œuvre" in e for e in pont_dc.EXCLUS))
ok("pont_dc ne porte toujours aucun montant, lui",
   "meur" not in str(pont_dc.CHAMPS).lower()
   and "montant" not in str(sorted(pont_dc.CHAMPS)).lower(),
   sorted(pont_dc.CHAMPS))

print("\n" + (str(ko) + " controle(s) en echec" if ko else "tout est vert") + "\n")
sys.exit(1 if ko else 0)
