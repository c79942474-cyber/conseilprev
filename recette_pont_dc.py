# -*- coding: utf-8 -*-
"""Le pont vers l'etude de durabilite — le contrat, et ce qui ne doit pas voyager.

CE QUE CE PONT FAIT. Une etude d'implantation se termine sur deux reponses :
quel pays, et combien. La suite — bilan energie / eau / carbone et trajectoire
de decarbonation — se mene sur l'autre site du cabinet. Le lien y porte le
profil technique pour qu'il ne soit pas ressaisi.

CE QUE CETTE RECETTE PROTEGE, ET LE DEUXIEME POINT EST LE VRAI SUJET :

  1. LE CONTRAT NE PEUT PAS DERIVER EN SILENCE. Les noms des parametres
     appartiennent au formulaire de l'AUTRE site. S'ils changent ici sans
     changer la-bas, le lien continue de FONCTIONNER et ne pre-remplit plus
     rien : le visiteur arrive sur un formulaire vide et croit que le lien
     n'etait qu'un raccourci de navigation. Les noms sont donc figes ici, avec
     la conversion appliquee.

  2. RIEN DE NOMINATIF NE VOYAGE. Une URL se copie, se colle dans un courriel,
     s'enregistre dans un historique et se journalise sur les serveurs qu'elle
     traverse : ce qu'on y met devient public au premier partage. On verifie
     donc qu'un lien construit depuis une reponse COMPLETE de l'enveloppe
     d'investissement — qui contient des montants, des ecarts entre pays et des
     dossiers entiers — n'en laisse rien passer.

  3. UN REFUS NE FAIT PAS ECHOUER LE LIEN, ET IL SE DIT. Un lien qui echoue en
     bloc parce qu'une valeur sur trois est douteuse prive le client des deux
     autres ; un lien qui laisse tomber une valeur en silence le fait calculer
     sur un profil qu'il croit avoir transmis.

  POUR L'EXECUTER :  python3 recette_pont_dc.py
"""
import sys

import pont_dc as P

ko = 0


def ok(nom, cond, detail=""):
    global ko
    print("  " + ("OK " if cond else "KO ") + "  " + nom + (" — " + str(detail) if detail else ""))
    if not cond:
        ko += 1


def titre(t):
    print("\n== " + t + " ==\n")


# ── 1. Le contrat ──────────────────────────────────────────────────────────
titre("1. Le contrat avec l'autre site")

ok("le module se charge sans probleme", P.sante()["problemes"] == [],
   P.sante()["problemes"])
ok("la cible est en https", P.BASE.startswith("https://"), P.BASE)

# LES NOMS SONT FIGES. Ce sont les identifiants des champs du formulaire de
# destination : les changer ici sans les changer la-bas casse le pre-remplissage
# SANS casser le lien. Si cette liste doit evoluer, elle evolue des deux cotes.
ATTENDUS = {"puissance_it_kw", "pays", "refroidissement"}
ok("les noms de parametres sont exactement ceux du formulaire cible",
   set(P.CHAMPS) == ATTENDUS, sorted(P.CHAMPS))
ok("chaque champ dit son unite et d'ou il vient",
   all(c["nom"] and c["unite"] and c["de"] for c in P.CHAMPS.values()))
ok("la conversion MW vers kW est declaree",
   P.CHAMPS["puissance_it_kw"]["facteur"] == 1000.0,
   P.CHAMPS["puissance_it_kw"]["facteur"])

r = P.lien(mw=45, pays="FR")
ok("le lien porte l'ancre attendue par la page cible",
   r["url"].startswith(P.BASE + "/datacenter#voie="), r["url"])
ok("…et la puissance convertie en kilowatts",
   "puissance_it_kw=45000" in r["url"], r["url"])
ok("…et le pays en deux lettres majuscules", "pays=FR" in r["url"])

# ── 2. Rien de nominatif ne voyage ─────────────────────────────────────────
titre("2. Ce que le lien ne porte pas")

# Une reponse de l'enveloppe TELLE QUE L'API LA REND : montants, ecarts,
# dossiers. Si le pont laissait fuir quoi que ce soit, c'est ici qu'on le voit.
REPONSE = {
    "entree": {"mw": 45, "gabarit": "hyperscale", "scenario": "neuve",
               "pays": ["FR", "SE", "DE"]},
    "classement": [{"pays": "SE", "tco_meur": [910, 1180], "tco_milieu": 1045},
                   {"pays": "FR", "tco_meur": [980, 1240], "tco_milieu": 1110}],
    "dossiers": [{"pays": "SE", "devis": {"enveloppe_meur": [360, 450]},
                  "client": "GROUPE EXEMPLE SA",
                  "site": "Zone industrielle de Norrland, parcelle 14"}],
    "avertissement": "…",
}
u = P.depuis_devis(REPONSE)["url"]
ok("le lien tire d'une reponse complete retient le pays du classement",
   "pays=SE" in u, u)
ok("…et la puissance de l'entree", "puissance_it_kw=45000" in u)
# LE CONTROLE STRUCTUREL PLUTOT QUE LA CHASSE AUX SOUS-CHAINES. Chercher
# « 450 » dans l'URL le trouvait dans « 45000 » : une alerte sur une fuite qui
# n'existait pas. On enumere donc les parametres REELLEMENT presents et on
# exige qu'ils appartiennent au contrat — un parametre ajoute un jour sans etre
# declare tombe ici, quel que soit son contenu.
frag = u.split("#", 1)[1]
noms = [x.split("=")[0] for x in frag.split("&")]
ok("le lien ne porte que des parametres du contrat",
   set(noms) <= (ATTENDUS | {"voie"}), noms)
ok("…et rien d'autre : ni montant, ni gabarit, ni scenario",
   not (set(noms) - (ATTENDUS | {"voie"})), noms)

# Les chaines, elles, ne peuvent pas se cacher dans un nombre : la recherche
# litterale garde tout son sens pour un nom de client ou de site.
for interdit, quoi in [("EXEMPLE", "un nom de client"),
                       ("Norrland", "un nom de site"),
                       ("hyperscale", "un gabarit de projet"),
                       ("neuve", "un scenario")]:
    ok("le lien ne porte PAS " + quoi, interdit not in u, u)

# Et les VALEURS transmises sont exactement les deux attendues.
valeurs = dict(x.split("=", 1) for x in frag.split("&"))
ok("la seule puissance transmise est celle de l'entree, convertie",
   valeurs.get("puissance_it_kw") == "45000", valeurs)
ok("le seul pays transmis est le premier du classement",
   valeurs.get("pays") == "SE", valeurs)

ok("la liste de ce qui ne voyage pas est servie avec le lien",
   len(P.lien(mw=1)["exclus"]) >= 4)
ok("…et elle nomme les donnees nominatives",
   any("client" in x.lower() for x in P.EXCLUS))

# ── 3. Les refus ───────────────────────────────────────────────────────────
titre("3. Un refus ne fait pas echouer le lien, et il se dit")

r = P.lien(mw=45, pays="FRANCE")
ok("un code pays mal ecrit est refuse",
   any("pays" in x["champ"].lower() for x in r["refuses"]), r["refuses"])
ok("…mais la puissance passe quand meme", "puissance_it_kw=45000" in r["url"])
ok("…et le lien reste utilisable", r["url"].startswith("https://"))

r = P.lien(mw=0.001, pays="FR")
ok("une puissance hors bornes est refusee",
   any("borne" in x["motif"] for x in r["refuses"]), r["refuses"])
ok("…et elle ne figure pas dans le lien", "puissance_it_kw" not in r["url"], r["url"])

r = P.lien(mw=45, pays="FR", voie="inventée")
ok("une voie inconnue est refusee et remplacee par le defaut",
   any(x["champ"] == "voie" for x in r["refuses"])
   and ("voie=" + P.VOIE_DEFAUT) in r["url"], r["url"])

r = P.lien(mw="beaucoup", pays="FR")
ok("une puissance illisible est refusee sans lever",
   any("illisible" in x["motif"] for x in r["refuses"]), r["refuses"])

r = P.lien(mw=45, pays="FR", refroidissement="tour; DROP TABLE")
ok("une cle de famille inattendue est refusee",
   any("famille" in x["champ"].lower() for x in r["refuses"]), r["refuses"])
ok("…et rien d'etranger ne se retrouve dans l'URL",
   " " not in r["url"] and ";" not in r["url"], r["url"])

# ── 4. Ce que le module refuse de faire ────────────────────────────────────
titre("4. Ce que le module refuse de faire")

src = open(__file__.replace("recette_pont_dc.py", "pont_dc.py"), encoding="utf-8").read()
ok("il ne valide PAS les familles de refroidissement contre une liste tenue ici",
   "REFROIDISSEMENT" not in src,
   "une liste recopiee divergerait du moteur de destination")
ok("il n'ouvre ni ne suit aucun lien",
   "urlopen" not in src and "requests" not in src and "webbrowser" not in src)
ok("la cible n'est pas deduite de l'en-tete Host",
   "request." not in src, "un lien fabrique derriere un proxy pointerait ailleurs")

# ── 5. Le lien construit est celui que la page cible sait lire ─────────────
titre("5. La forme exacte attendue par la page cible")

r = P.lien(mw=20, pays="se", refroidissement="tour_evaporative", voie="trajectoire")
attendu = (P.BASE + "/datacenter#voie=trajectoire&pays=SE"
           "&puissance_it_kw=20000&refroidissement=tour_evaporative")
ok("l'URL est exactement celle qu'attend la page de destination",
   r["url"] == attendu, r["url"])

print("\n" + (str(ko) + " controle(s) en echec" if ko else "tout est vert") + "\n")
sys.exit(1 if ko else 0)
