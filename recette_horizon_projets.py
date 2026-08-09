# -*- coding: utf-8 -*-
"""Le curseur 2025→2030 doit montrer les constructions à venir, pas rien.

CE QU'ON PROTÈGE, ET C'EST PRÉCIS.

1. LE DÉFAUT SIGNALÉ. La carte portait un curseur d'année et un test d'estompe
   qui comparait `annee_service`. Or AUCUN des vingt projets du référentiel ne
   portait d'année de mise en service : le test était donc faux pour tous, à
   toutes les années, et glisser le curseur de 2025 à 2030 ne changeait rien à
   l'écran. Un contrôle qui ne rejouerait pas ce calcul sur le référentiel
   d'AVANT laisserait croire qu'il vérifie quelque chose.

2. UNE INTENTION N'EST PAS UN FAIT. `horizon_annonce` est un calendrier
   d'opérateur ; `annee_service` atteste une mise en service constatée. Les
   confondre — ranger un horizon dans le champ des mises en service — ferait
   dire à la carte qu'un site existe alors qu'il est annoncé. Aucun site ne doit
   porter les deux, et aucun site en service ne doit porter un horizon.

3. L'ABSENCE N'EST PAS UNE DATE. Douze projets n'ont aucun calendrier public.
   Leur prêter 2030 les ferait disparaître du parc jusqu'au bout du curseur ;
   leur prêter 2025 les y ferait entrer d'office. Ils sont montrés à toutes les
   années, dans un état qui leur est propre, et comptés à part.

4. LA PROSE VIEILLIT PLUS VITE QUE LA DONNÉE. Corriger deux statuts a changé le
   nombre de projets sans date, et la limite écrite en toutes lettres disait
   encore « quatorze » sur un référentiel qui n'en portait plus que douze. Le
   module rapproche désormais la phrase du dénombrement ; on vérifie que ce
   rapprochement DISCRIMINE.
"""
import io
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


import datacentres as D                                         # noqa: E402

d = D.assemble()
SITES = d["sites"]
PIPE = d["agregats"]["pipeline"]
PROJ = [s for s in SITES if s["statut"] in D.PROJET]


def par_nom(fragment):
    t = [s for s in SITES if fragment.lower() in (s["nom_site"] or "").lower()]
    return t[0] if len(t) == 1 else None


print("\n══ 1. Six calendriers publics, recopiés un par un ══\n")

ATTENDUS = (("Bedburg", "DE", 2027, "annonce"),
            ("Bergheim", "DE", 2027, "annonce"),
            ("Espoo", "FI", 2027, "construction"),
            ("Narvik", "NO", 2027, "construction"),
            ("Start Campus Sines", "PT", 2027, "construction"),
            ("Fos", "FR", 2028, "annonce"))
for frag, pays, an, statut in ATTENDUS:
    s = par_nom(frag)
    ok("%s (%s) : horizon annoncé %d, statut « %s »" % (frag, pays, an, statut),
       bool(s) and s["pays"] == pays and s.get("horizon_annonce") == an
       and s["statut"] == statut,
       s and (s["pays"], s.get("horizon_annonce"), s["statut"]))
    # Une date sans provenance est une date inventée : la note doit porter
    # l'année ET le mot qui dit que c'est un CALENDRIER, pas un constat.
    note = (s.get("note") or "") if s else ""
    mots = [m for m in ("horizon", "calendrier", "attendue", "visee")
            if m in note.lower()]
    ok("…et sa note dit d'où vient cette date, et que c'est un calendrier",
       str(an) in note and bool(mots), mots or note[-60:])

ok("six horizons, pas un de plus", PIPE["avec_horizon"] == 6, PIPE["avec_horizon"])
ok("…répartis 2027 puis 2028, sans date inventée avant ni après",
   PIPE["par_annee"] == {"2027": 5, "2028": 1}, PIPE["par_annee"])

print("\n══ 2. Une intention n'est jamais rangée avec un fait ══\n")

ok("le champ existe sur les 249 lignes, jamais indéfini côté page",
   all("horizon_annonce" in s for s in SITES),
   sum(1 for s in SITES if "horizon_annonce" not in s))
ok("aucun site ne porte à la fois un horizon et une mise en service",
   not [s["nom_site"] for s in SITES
        if s.get("horizon_annonce") and s.get("annee_service")])
ok("aucun site EN SERVICE ne porte d'horizon annoncé",
   not [s["nom_site"] for s in SITES
        if s["statut"] == "service" and s.get("horizon_annonce")])
ok("aucun ABANDON n'en porte non plus — un projet mort n'a pas d'échéance",
   not [s["nom_site"] for s in SITES
        if s["statut"] == "abandonne" and s.get("horizon_annonce")])
ok("les six horizons portent tous sur un projet",
   all(s["statut"] in D.PROJET for s in SITES if s.get("horizon_annonce")))
ok("aucun horizon n'est antérieur au relevé — ce serait un retard, pas un plan",
   all(s["horizon_annonce"] >= 2027 for s in SITES if s.get("horizon_annonce")))

print("\n══ 3. Deux statuts vérifiés, deux statuts CORRIGÉS ══\n")

for frag, an, motif in (("Waltham Cross", 2025, "16 septembre 2025"),
                        ("Eclairion", 2026, "2026")):
    s = par_nom(frag)
    ok("%s est désormais en service (%d)" % (frag, an),
       bool(s) and s["statut"] == "service" and s.get("annee_service") == an,
       s and (s["statut"], s.get("annee_service")))
    ok("…et la note porte la date d'ouverture, pas une supposition",
       bool(s) and motif in (s.get("note") or ""), motif)
# DISCRIMINATION : la correction doit avoir DÉPLACÉ le compte, sinon elle n'a
# corrigé que du texte.
ok("le parc en service a gagné ces deux sites",
   PIPE["en_service"] == 227 and PIPE["projets"] == 18,
   (PIPE["en_service"], PIPE["projets"]))
ok("…et le total de lignes n'a pas bougé : c'est un reclassement, pas un ajout",
   len(SITES) == 249, len(SITES))
ok("le millésime marque le passage", d["version"] == "2026-08-d", d["version"])

print("\n══ 4. L'absence de calendrier reste une absence ══\n")

sans = [s for s in PROJ if not s.get("horizon_annonce")]
ok("douze projets sans date publiée", len(sans) == 12 == PIPE["sans_horizon"],
   len(sans))
ok("…et leur champ vaut None, pas une année de complaisance",
   all(s["horizon_annonce"] is None for s in sans))
ok("…aucun n'a reçu 2030 en douce — ils seraient absents tout du long",
   not [s for s in sans if s.get("horizon_annonce") == 2030])
ok("…ni 2025, qui les ferait entrer au parc d'office",
   not [s for s in sans if s.get("horizon_annonce") == 2025])
ok("les trois nombres se recomposent sans trou",
   PIPE["avec_horizon"] + PIPE["sans_horizon"] == PIPE["projets"] == 18)
ok("…et le référentiel entier se recompose aussi",
   PIPE["projets"] + PIPE["en_service"]
   + d["agregats"]["par_statut"]["abandonne"] == 249)

print("\n══ 5. La prose ne peut plus mentir sur le dénombrement ══\n")

s = D.sante()
ok("la santé du module est verte", not s["problemes"], s["problemes"])
ok("…et elle publie le pipeline plutôt que de le laisser deviner",
   s["pipeline"]["sans_horizon"] == 12)
lim = " ".join(D.LIMITES)
ok("la limite de temporalité NOMME les deux corrections",
   "Waltham Cross" in lim and "Eclairion" in lim
   and "CORRIG" in lim.upper())
ok("…et compte douze projets sans date, pas quatorze",
   "Les douze autres projets" in lim and "quatorze autres" not in lim)
ok("…et rappelle que la carte les montre en permanence",
   "montre en permanence" in lim)
# DISCRIMINATION : le garde-fou doit RÉAGIR. On rejoue la phrase fausse qui a
# survécu à la correction des deux statuts.
vraies = D.LIMITES[:]
try:
    D.LIMITES[:] = [x.replace("Les douze autres projets",
                              "Les quatorze autres projets") for x in vraies]
    faux = D._limite_temporalite(PIPE)
finally:
    D.LIMITES[:] = vraies
ok("…et la phrase d'hier serait bien refusée aujourd'hui",
   bool(faux) and "douze autres projets" in faux[0], faux)
ok("le contrôle est revenu à l'état initial", not D.sante()["problemes"])

print("\n══ 6. La fraîcheur annoncée à l'écran suit le référentiel ══\n")

sent = io.open(DEPOT + "/sentinel.html", encoding="utf-8").read()
mil = [l for l in sent.splitlines() if l.startswith("var DC_MILLESIME")]
ok("le millésime est déclaré UNE fois dans l'interface", len(mil) == 1, mil)
ok("…et il vaut celui du module", ('"%s"' % D.VERSION) in (mil[0] if mil else ""),
   mil[0] if mil else "")
# LE contrôle : c'est cette recopie qui avait vieilli. Corriger deux statuts de
# chantier a fait passer le module en 2026-08-d pendant que six listes de
# sources annonçaient encore 2026-08-b — une fraîcheur de données fausse.
restes = [l.strip()[:70] for l in sent.splitlines()
          if "centres de données" in l and "version 2026-08" in l]
ok("plus aucune liste de sources ne recopie un millésime de centres",
   not restes, restes[:2])
ok("…mais six d'entre elles le CITENT bien, par la constante",
   sent.count("+ DC_MILLESIME") == 6, sent.count("+ DC_MILLESIME"))
ok("le millésime du référentiel des systèmes d'IA, lui, n'a pas bougé",
   "2026-07-b" in sent)

print("\n══ 7. Discrimination : le curseur ne pouvait RIEN montrer avant ══\n")


def _avant(marqueur, fichier):
    """Le fichier juste AVANT l'arrivée du marqueur.

    Si un commit l'a introduit, on lit son parent ; sinon la modification n'est
    pas encore livrée et la référence est HEAD. Rendre une chaîne vide rendrait
    le contrôle CREUX."""
    hs = subprocess.check_output(
        ["git", "-C", DEPOT, "log", "-S", marqueur, "--format=%H", "--", fichier],
        text=True).split()
    ref = ("%s^" % hs[-1]) if hs else "HEAD"
    return subprocess.check_output(
        ["git", "-C", DEPOT, "show", "%s:%s" % (ref, fichier)], text=True)


av = _avant("horizon_annonce", "datacentres.py")
ok("avant, le référentiel ignorait la notion d'horizon annoncé",
   "horizon_annonce" not in av)

espace = {}
exec(compile(av, "datacentres_avant", "exec"), espace)
sites_av = espace["SITES"]
proj_av = [x for x in sites_av if x["statut"] in ("annonce", "autorise", "construction")]
ok("…et comptait vingt projets", len(proj_av) == 20, len(proj_av))
# LE contrôle central : on rejoue le test d'estompe de la page d'alors, année
# par année. Il rendait faux pour TOUS les projets, à TOUTES les années.
bouges = {an: sum(1 for x in proj_av
                  if x.get("annee_service") and x["annee_service"] > an)
          for an in range(2024, 2031)}
ok("…dont AUCUN ne portait d'année de mise en service",
   not [x for x in proj_av if x.get("annee_service")])
ok("…si bien que le test d'estompe d'alors était faux à chacune des 7 années",
   set(bouges.values()) == {0}, bouges)
ok("…et que déplacer le curseur de 2024 à 2030 ne pouvait rien changer",
   len(set(bouges.values())) == 1)
# Contre-épreuve : aujourd'hui, le même parcours d'années fait bouger le parc.
etats = {}
for an in range(2024, 2031):
    n = sum(1 for x in SITES
            if x["statut"] == "service"
            and not (x.get("annee_service") and x["annee_service"] > an))
    n += sum(1 for x in PROJ if x.get("horizon_annonce")
             and x["horizon_annonce"] <= an)
    etats[an] = n
ok("aujourd'hui le parc CROÎT le long du curseur",
   sorted(etats.values()) == list(etats.values())
   and len(set(etats.values())) > 1, etats)
ok("…de 225 en 2024 à 233 en 2030", etats[2024] == 225 and etats[2030] == 233,
   (etats[2024], etats[2030]))
ok("…et le saut a bien lieu en 2027, quand cinq horizons échoient",
   etats[2027] - etats[2026] == 5, etats[2027] - etats[2026])

pan = _avant("function etatDC", "panorama.html")
ok("avant, la page n'avait pas d'état à l'année", "function etatDC" not in pan)
ok("…et son estompe reposait sur le champ que les projets ne portaient pas",
   "annee_service && s.annee_service > DC_HORIZON" in pan)
ok("…tandis que le curseur d'aujourd'hui redessine la couche",
   "renderDC(true)" in io.open(DEPOT + "/panorama.html", encoding="utf-8").read())
ok("…sans reconstruire la barre sous le doigt",
   "sansHabillage" in io.open(DEPOT + "/panorama.html", encoding="utf-8").read())

print("\n══ 8. Ce que cette correction ne devait PAS déplacer ══\n")

ok("le référentiel garde ses 249 lignes", d["n_sites"] == 249, d["n_sites"])
ok("les quatre abandons sont intacts",
   d["agregats"]["par_statut"]["abandonne"] == 4)
ok("les cinq statuts existent toujours", len(D.STATUTS) == 5, sorted(D.STATUTS))
ok("aucune capacité n'a été inventée au passage",
   d["agregats"]["capacite_mw_cumulee"] == 0,
   d["agregats"]["capacite_mw_cumulee"])
ok("les deux origines restent séparées",
   len([x for x in SITES if x.get("provenance") == "registre"]) == 139,
   len([x for x in SITES if x.get("provenance") == "registre"]))
ok("les listes de retirés et réintégrés n'ont pas bougé",
   len(D.RETIRES) == 3 and len(D.REINTEGRES) == 5)

print("")
print("%d contrôle(s) en échec\n" % ko if ko else "tout est vert\n")
sys.exit(1 if ko else 0)
