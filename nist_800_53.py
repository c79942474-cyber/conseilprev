# -*- coding: utf-8 -*-
"""NIST SP 800-53 Rev. 4 — LE CATALOGUE DE MESURES, ET CE QU'IL DEMANDE D'ABORD.

═══ CE QUE C'EST ════════════════════════════════════════════════════════
« Security and Privacy Controls for Federal Information Systems and
Organizations », révision 4. Dix-huit familles de mesures, désignées par
deux lettres, plus un catalogue de mesures de vie privée en annexe J.
Trois socles — Low, Moderate, High — disent lesquelles s'appliquent.

═══ POURQUOI LA RÉVISION 4, ET NON LA 5 ═════════════════════════════════
PARCE QUE C'EST CELLE QUE LA SURCHARGE INDUSTRIELLE VISE. NIST SP 800-82
Rev. 2 le dit à l'ouverture de son annexe G : « The ICS overlay is a
partial tailoring of the controls and control baselines in SP 800-53,
Revision 4 ». Bâtir ce module sur la révision 5 aurait produit un pont
faux : deux familles de la révision 5 — PT et SR — n'existent pas en
révision 4, et la famille CA n'y porte pas le même intitulé. Un pont entre
deux millésimes qui ne se recouvrent pas est pire qu'un pont absent, parce
qu'il a l'air de tenir.

CE QUE CELA COÛTE, ET IL FAUT LE DIRE : la révision 5 est la version
courante du catalogue. Ce module mesure donc la préparation d'un système
industriel contre le référentiel que sa surcharge OT utilise, pas contre
le dernier état du catalogue. La réserve est portée à l'écran, pas ici
seulement.

═══ À QUELLE MAILLE CE MODULE MESURE, ET POURQUOI ═══════════════════════
IL MESURE PAR FAMILLE. Le catalogue complet de la révision 4 n'est pas
disponible dans cet environnement : la répartition exacte des mesures par
socle ne s'invente pas, et un pourcentage dont le dénominateur serait
supposé vaudrait moins que son absence. Les dix-huit familles, elles, sont
énumérées par le document lui-même, au §6.2, avec leur définition.

Ce que le module ne rend donc pas : « tant de mesures tenues sur tant
d'applicables ». Il le dit, plutôt que de le laisser croire.

═══ LE SOCLE N'EST PAS UN CHOIX DE CONFORT ══════════════════════════════
Il DÉCOULE de la catégorisation du système. Annoncer « High » sans avoir
conduit l'appréciation du risque, c'est donner un résultat sans sa
méthode : la famille RA est précisément celle qui le produit. C'est un
verrou, et il est calculé.

═══ ET L'AVAL NE PEUT PAS DEVANCER L'AMONT ══════════════════════════════
RA, PL, CA et PM ne sont pas quatre familles parmi dix-huit : elles
décident de ce que les quatorze autres doivent faire. Une maison qui
chiffre fort sur les mesures techniques et faiblement sur ce socle n'a pas
un programme de sécurité — elle a un inventaire d'outils. Le module le dit
au lieu de le moyenner.

═══ DROITS ══════════════════════════════════════════════════════════════
Les publications de la série SP du NIST sont des œuvres du gouvernement
des États-Unis : elles se citent et se reprennent librement. Les intitulés
de famille et leurs définitions figurent ici dans leur libellé d'origine,
en anglais, tel qu'il est au document — un intitulé traduit ne se retrouve
plus dans le catalogue quand un auditeur demande où il est écrit. Ce qui
est en français est le travail du cabinet.
"""

SOURCES = (
    {"cle": "sp80053r4",
     "titre": "NIST SP 800-53 Rev. 4 — Security and Privacy Controls for "
              "Federal Information Systems and Organizations",
     "date": "2013-04",
     "doi": "https://doi.org/10.6028/NIST.SP.800-53r4",
     "droits": "Œuvre du gouvernement des États-Unis — libre de citation.",
     "certifiable": False},
    {"cle": "sp80082r2",
     "titre": "NIST SP 800-82 Rev. 2 — Guide to Industrial Control Systems "
              "(ICS) Security",
     "date": "2015-05",
     "doi": "https://doi.org/10.6028/NIST.SP.800-82r2",
     "droits": "Œuvre du gouvernement des États-Unis — libre de citation.",
     "role": "source des dix-huit familles énumérées ici (§6.2) et de la "
             "surcharge industrielle",
     "certifiable": False},
)

#: LE MILLÉSIME, DIT UNE FOIS ET PORTÉ PARTOUT. Le dépôt a déjà payé un
#: questionnaire qui visait ISO 27001:2013 quand la norme était de 2022 :
#: un référentiel sans millésime affiché finit par être pris pour le dernier.
REVISION = "Rev. 4 (avril 2013)"
REVISION_COURANTE = "Rev. 5"
RESERVE_MILLESIME = (
    "Ce module vise la révision 4 du catalogue, parce que c'est celle que "
    "la surcharge industrielle SP 800-82 Rev. 2 adapte. La révision 5 est "
    "la version courante : elle ajoute les familles PT et SR, et renomme "
    "CA. Un système déjà aligné sur la révision 5 doit le savoir avant de "
    "lire ce taux."
)


# ══════════════════════════════════════════════════════════════════════════
#  LES DIX-HUIT FAMILLES
# ══════════════════════════════════════════════════════════════════════════
#
# L'ordre et les définitions anglaises sont ceux du §6.2 de SP 800-82 Rev. 2,
# qui les énumère pour les besoins de sa surcharge. La dernière colonne — ce
# que la famille demande, en une phrase utilisable en comité — est le travail
# du cabinet, pas une traduction.

FAMILLES = (
    ("AC", "Access Control",
     "the process of granting or denying specific requests for obtaining "
     "and using information and related information processing services",
     "qui peut faire quoi, et la révocation le jour où le rôle change"),
    ("AT", "Awareness and Training",
     "policies and procedures to ensure that all information system users "
     "are given appropriate security training",
     "ce que les gens savent faire, pas ce qu'ils ont signé"),
    ("AU", "Audit and Accountability",
     "independent review and examination of records and activities to "
     "assess the adequacy of system controls",
     "les traces, leur intégrité, et quelqu'un qui les lit"),
    ("CA", "Security Assessment and Authorization",
     "assurance that the specified controls are implemented correctly, "
     "operating as intended, and producing the desired outcome",
     "qui a autorisé la mise en service, sur quelles preuves, pour combien "
     "de temps"),
    ("CP", "Contingency Planning",
     "policies and procedures designed to maintain or restore business "
     "operations in the event of emergencies, system failures, or disaster",
     "le retour en service, éprouvé — pas le plan qui le décrit"),
    ("CM", "Configuration Management",
     "policies and procedures for controlling modifications to hardware, "
     "firmware, software, and documentation",
     "l'état de référence, et ce qui se passe quand il dérive"),
    ("IA", "Identification and Authentication",
     "the process of verifying the identity of a user, process, or device "
     "as a prerequisite for granting access to resources",
     "prouver qui l'on est, y compris pour les comptes de service"),
    ("IR", "Incident Response",
     "policies and procedures pertaining to incident response training, "
     "testing, handling, monitoring, reporting, and support services",
     "détecter, qualifier, contenir, et rendre compte dans les délais dus"),
    ("MA", "Maintenance",
     "policies and procedures to manage all maintenance aspects of an "
     "information system",
     "l'intervention, sur site et à distance, et qui la conduit"),
    ("MP", "Media Protection",
     "policies and procedures to ensure secure handling of media: access, "
     "labeling, storage, transport, sanitization, destruction, and disposal",
     "les supports, jusqu'à leur effacement ou leur destruction"),
    ("PE", "Physical and Environmental Protection",
     "policies and procedures addressing physical, transmission, and "
     "display access control as well as environmental controls",
     "l'accès physique, l'énergie, le refroidissement, l'eau"),
    ("PL", "Planning",
     "development and maintenance of a plan to address information system "
     "security",
     "le plan de sécurité du système : ce qu'il est, ce qu'il protège"),
    ("PS", "Personnel Security",
     "policies and procedures for personnel position categorization, "
     "screening, transfer, penalty, and termination",
     "l'entrée, la mobilité et le départ des personnes"),
    ("RA", "Risk Assessment",
     "the process of identifying risks to operations, assets, or "
     "individuals by determining the probability of occurrence and impact",
     "la catégorisation du système, et le socle qui en découle"),
    ("SA", "System and Services Acquisition",
     "allocation of resources for information system security throughout "
     "the systems life cycle, and acquisition policies based on risk",
     "ce qu'on exige de ses fournisseurs avant de signer"),
    ("SC", "System and Communications Protection",
     "mechanisms for protecting both system and data transmission "
     "components",
     "le cloisonnement, le chiffrement, les frontières"),
    ("SI", "System and Information Integrity",
     "policies and procedures to protect information systems and their "
     "data from design flaws and data modification",
     "les correctifs, la détection, l'intégrité de ce qui tourne"),
    ("PM", "Program Management",
     "provides security controls at the organizational rather than the "
     "information-system level",
     "le programme à l'échelle de la maison, au-dessus de chaque système"),
)
FAMILLES_PAR_CLE = {f[0]: f for f in FAMILLES}
ORDRE_FAMILLES = [f[0] for f in FAMILLES]


# ══════════════════════════════════════════════════════════════════════════
#  LES CINQ GROUPES, ET POURQUOI LE PREMIER COMMANDE LES AUTRES
# ══════════════════════════════════════════════════════════════════════════

GROUPES = (
    {"cle": "pilotage", "nom": "Pilotage et autorisation",
     "familles": ("RA", "PL", "CA", "PM"), "poids": 3,
     "pourquoi": "ces quatre familles produisent le socle, le plan et "
                 "l'autorisation : elles commandent le périmètre des "
                 "quatorze autres"},
    {"cle": "maitrise", "nom": "Maîtrise du système et de sa chaîne",
     "familles": ("CM", "SA", "MA"), "poids": 2,
     "pourquoi": "ce qui tourne, d'où cela vient, et qui y intervient"},
    {"cle": "acces", "nom": "Accès, personnes et lieux",
     "familles": ("AC", "IA", "AT", "PS", "PE"), "poids": 2,
     "pourquoi": "le chemin le plus emprunté vers un système reste un accès "
                 "légitime mal tenu"},
    {"cle": "exploitation", "nom": "Exploitation, détection et reprise",
     "familles": ("AU", "SI", "IR", "CP"), "poids": 2,
     "pourquoi": "ce qui se passe une fois le système en service, y compris "
                 "le jour où il tombe"},
    {"cle": "donnees", "nom": "Protection des données et des échanges",
     "familles": ("SC", "MP"), "poids": 2,
     "pourquoi": "la donnée elle-même, en transit et sur support"},
)
GROUPES_PAR_CLE = {g["cle"]: g for g in GROUPES}
#: Le groupe dont les autres dépendent. Nommé ici une fois, utilisé partout.
SOCLE_COMMANDANT = "pilotage"


# ══════════════════════════════════════════════════════════════════════════
#  LES TROIS SOCLES
# ══════════════════════════════════════════════════════════════════════════

SOCLES = {
    "low": {"nom": "Low", "rang": 1,
            "dit": "Une perte aurait un effet LIMITÉ sur les missions, les "
                   "actifs ou les personnes."},
    "moderate": {"nom": "Moderate", "rang": 2,
                 "dit": "Une perte aurait un effet SÉRIEUX — dégradation "
                        "notable, préjudice financier ou humain sans danger "
                        "vital."},
    "high": {"nom": "High", "rang": 3,
             "dit": "Une perte aurait un effet GRAVE ou CATASTROPHIQUE, y "
                    "compris des atteintes graves aux personnes."},
}
ORDRE_SOCLES = ["low", "moderate", "high"]


# ══════════════════════════════════════════════════════════════════════════
#  L'ÉCHELLE
# ══════════════════════════════════════════════════════════════════════════
#
# LA MÊME QUE CELLE DU CADRE IA DE CE CABINET, et ce n'est pas une
# coquetterie : un lecteur qui tient deux référentiels NIST ne doit pas
# apprendre deux échelles. « prouvé » n'est pas « tenu » avec de la
# conviction en plus — c'est « tenu », plus une pièce qu'on pose sur la table.

ETATS = {
    "absent":     {"note": 0.0, "nom": "Absent",
                   "dit": "Rien en place, ou rien qu'on puisse montrer."},
    "amorce":     {"note": 1.0, "nom": "Amorcé",
                   "dit": "Des pratiques existent, sans constance ni "
                          "responsable désigné."},
    "tenu":       {"note": 2.0, "nom": "Tenu",
                   "dit": "Défini, appliqué, porté par quelqu'un de nommé."},
    "prouve":     {"note": 3.0, "nom": "Prouvé",
                   "dit": "Tenu, ET démontrable devant un tiers sans "
                          "préparation."},
    "sans_objet": {"note": None, "nom": "Sans objet",
                   "dit": "Hors périmètre, avec une justification écrite — "
                          "le catalogue l'autorise, il ne l'offre pas."},
}
ORDRE_ETATS = ["absent", "amorce", "tenu", "prouve", "sans_objet"]
NOTE_MAX = 3.0

#: AU-DELÀ, LE PÉRIMÈTRE EST VIDÉ PLUTÔT QUE TAILLÉ. Écarter une famille est
#: permis ; en écarter le quart revient à redessiner le système pour qu'il
#: passe. Le seuil est le quart des dix-huit, arrondi au plus proche.
PLAFOND_SANS_OBJET = 4


def _pc(x, sur):
    return round(100.0 * x / sur, 1) if sur else None


def _groupe(etats, groupe):
    """La note d'un groupe, étalée sur TOUTES ses familles.

    POURQUOI « ÉTALÉE », ET NON « MOYENNE DES RENSEIGNÉES ». Une moyenne des
    seules familles déclarées fait qu'une maison qui n'en ouvre qu'une, et la
    déclare prouvée, affiche 100 %. Le défaut a été mesuré sur le cadre IA de
    ce cabinet avant d'être corrigé ; on ne le réintroduit pas ici. Une
    famille muette compte comme absente, ce qu'elle est.

    UNE FAMILLE « SANS OBJET » SORT DU DÉNOMINATEUR, elle. Ce n'est pas la
    même chose : elle a été regardée, puis écartée avec un motif.
    """
    cles = groupe["familles"]
    retenues = [c for c in cles if etats.get(c) != "sans_objet"]
    renseignees = [c for c in cles
                   if c in etats and etats.get(c) != "sans_objet"]
    acquis = sum(ETATS[etats[c]]["note"] for c in renseignees)
    return {
        "groupe": groupe["cle"], "nom": groupe["nom"], "poids": groupe["poids"],
        "pourquoi": groupe["pourquoi"],
        "familles": len(cles), "retenues": len(retenues),
        "renseignees": len(renseignees),
        "ecartees": len(cles) - len(retenues),
        "note": round(acquis / len(renseignees), 2) if renseignees else None,
        "sur": NOTE_MAX,
        "taux": _pc(acquis, NOTE_MAX * len(retenues)) if retenues else None,
        "detail": [{"famille": c,
                    "titre": FAMILLES_PAR_CLE[c][1],
                    "definition": FAMILLES_PAR_CLE[c][2],
                    "demande": FAMILLES_PAR_CLE[c][3],
                    "etat": etats.get(c),
                    "etat_nom": ETATS[etats[c]]["nom"] if c in etats else None}
                   for c in cles],
    }


def evaluer(socle=None, etats=None):
    """Le profil par groupe, le socle annoncé, et ce qui plafonne les deux.

    CE QUE CETTE FONCTION REFUSE DE RENDRE : un nombre de mesures tenues sur
    un nombre de mesures applicables. Le module travaille à la maille de la
    famille, et le dire vaut mieux qu'un ratio au dénominateur supposé.
    """
    etats = etats if isinstance(etats, dict) else {}
    inconnues = [k for k in etats if k not in FAMILLES_PAR_CLE]
    mauvais = [k for k, v in etats.items() if v not in ETATS]
    if inconnues:
        return {"ok": False, "motif": "familles_inconnues",
                "detail": sorted(inconnues)[:8]}
    if mauvais:
        return {"ok": False, "motif": "etats_inconnus",
                "detail": sorted(mauvais)[:8]}
    if socle is not None and socle not in SOCLES:
        return {"ok": False, "motif": "socle_inconnu", "detail": socle}

    profils = [_groupe(etats, g) for g in GROUPES]
    par_cle = {p["groupe"]: p for p in profils}
    renseignees = sum(p["renseignees"] for p in profils)
    ecartees = sum(p["ecartees"] for p in profils)

    verrous = []

    # 1. LE SOCLE ANNONCÉ SANS LA MÉTHODE QUI LE PRODUIT.
    if socle and SOCLES[socle]["rang"] >= 2 and etats.get("RA") in (None, "absent"):
        verrous.append({
            "cle": "socle_sans_appreciation",
            "dit": "Le socle %s est annoncé alors que l'appréciation du "
                   "risque (RA) est absente. Le socle DÉCOULE de la "
                   "catégorisation : sans elle, il est affirmé, pas établi."
                   % SOCLES[socle]["nom"]})

    # 2. RA ÉCARTÉE. On peut écarter des familles ; pas celle qui décide de
    #    ce qu'on écarte.
    if etats.get("RA") == "sans_objet":
        verrous.append({
            "cle": "risque_ecarte",
            "dit": "L'appréciation du risque est déclarée sans objet. C'est "
                   "elle qui justifie les exclusions : s'en passer rend "
                   "toutes les autres injustifiables."})

    # 3. L'AVAL DEVANCE L'AMONT — le défaut le plus fréquent, et celui qu'une
    #    note globale unique aurait entièrement masqué.
    amont = par_cle[SOCLE_COMMANDANT]
    aval = [p for p in profils if p["groupe"] != SOCLE_COMMANDANT
            and p["note"] is not None]
    devancent = [p["nom"] for p in aval
                 if amont["note"] is None or p["note"] > amont["note"] + 0.5]
    if devancent and renseignees >= 4:
        verrous.append({
            "cle": "socle_devance",
            "dit": "Les mesures avancent plus vite que ce qui les commande : "
                   "%s %s au-dessus du pilotage. Des mesures appliquées sans "
                   "socle autorisé ne se défendent pas en audit."
                   % (", ".join(devancent),
                      "sont" if len(devancent) > 1 else "est")})

    # 4. LE PÉRIMÈTRE VIDÉ.
    if ecartees > PLAFOND_SANS_OBJET:
        verrous.append({
            "cle": "perimetre_vide",
            "dit": "%d familles sur %d sont déclarées sans objet. Au-delà de "
                   "%d, le périmètre n'est plus taillé : il est vidé."
                   % (ecartees, len(FAMILLES), PLAFOND_SANS_OBJET)})

    return {
        "ok": True,
        "revision": REVISION,
        "socle": socle,
        "socle_nom": SOCLES[socle]["nom"] if socle else None,
        "socle_dit": SOCLES[socle]["dit"] if socle else None,
        "familles": len(FAMILLES),
        "renseignees": renseignees,
        "ecartees": ecartees,
        "profils": profils,
        "verrous": verrous,
        "certifiable": False,
        "reserve": "SP 800-53 ne se certifie pas. Aucun organisme ne délivre "
                   "d'attestation contre ce catalogue : ce taux dit une "
                   "couverture déclarée, pas une conformité reconnue.",
        "reserve_millesime": RESERVE_MILLESIME,
        "maille": "Le module travaille par FAMILLE, pas par mesure : la "
                  "répartition des mesures par socle n'est pas reprise ici, "
                  "et un ratio au dénominateur supposé vaudrait moins que "
                  "son absence.",
    }


def referentiel():
    """Ce que l'écran a besoin de savoir pour poser les questions."""
    return {
        "sources": [dict(s) for s in SOURCES],
        "revision": REVISION,
        "revision_courante": REVISION_COURANTE,
        "reserve_millesime": RESERVE_MILLESIME,
        "socles": [dict(SOCLES[c], cle=c) for c in ORDRE_SOCLES],
        "etats": [dict(ETATS[c], cle=c) for c in ORDRE_ETATS],
        "groupes": [{"cle": g["cle"], "nom": g["nom"], "poids": g["poids"],
                     "pourquoi": g["pourquoi"],
                     "familles": [{"cle": c,
                                   "titre": FAMILLES_PAR_CLE[c][1],
                                   "definition": FAMILLES_PAR_CLE[c][2],
                                   "demande": FAMILLES_PAR_CLE[c][3]}
                                  for c in g["familles"]]}
                    for g in GROUPES],
        "socle_commandant": SOCLE_COMMANDANT,
        "certifiable": False,
    }


# ══════════════════════════════════════════════════════════════════════════
#  LA GARDE — elle recompte à chaque chargement
# ══════════════════════════════════════════════════════════════════════════

def _verifier():
    assert len(FAMILLES) == 18, len(FAMILLES)
    assert len(FAMILLES_PAR_CLE) == 18, "deux familles portent le même code"
    # LES GROUPES PARTITIONNENT LES FAMILLES : aucune oubliée, aucune comptée
    # deux fois. Sans cette garde, une famille perdue dans un regroupement
    # sortirait du taux sans que rien ne le dise.
    groupees = [c for g in GROUPES for c in g["familles"]]
    assert len(groupees) == 18, len(groupees)
    assert sorted(groupees) == sorted(ORDRE_FAMILLES), (
        sorted(set(ORDRE_FAMILLES) ^ set(groupees)))
    assert SOCLE_COMMANDANT in GROUPES_PAR_CLE
    assert "RA" in GROUPES_PAR_CLE[SOCLE_COMMANDANT]["familles"], (
        "le groupe qui commande ne contient plus l'appréciation du risque, "
        "dont découle le socle")
    # LA RÉVISION 5 N'EST PAS ICI, ET C'EST VOULU : ses deux familles propres
    # feraient croire à un pont avec une surcharge qui ne les connaît pas.
    assert "PT" not in FAMILLES_PAR_CLE and "SR" not in FAMILLES_PAR_CLE, (
        "PT et SR appartiennent à la révision 5 : la surcharge industrielle "
        "vise la révision 4 et ne les tailla jamais")
    assert set(ORDRE_ETATS) == set(ETATS)
    assert set(ORDRE_SOCLES) == set(SOCLES)


_verifier()
