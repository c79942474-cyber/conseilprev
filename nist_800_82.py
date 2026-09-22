# -*- coding: utf-8 -*-
"""NIST SP 800-82 Rev. 2 — LA SURCHARGE INDUSTRIELLE, QUI NE REFAIT PAS 800-53.

═══ CE QUE C'EST, ET CE QUE CE N'EST PAS ════════════════════════════════
« Guide to Industrial Control Systems (ICS) Security », révision 2, mai
2015. Son annexe G n'est PAS un second catalogue : c'est une surcharge —
un *overlay* — de SP 800-53 Rev. 4. Le document le dit lui-même :

    « The ICS overlay is a partial tailoring of the controls and control
      baselines in SP 800-53, Revision 4, and adds supplementary guidance
      specific to ICS. »

CE QUE CELA COMMANDE ICI. Poser deux questionnaires indépendants aurait
fait répondre deux fois aux mêmes questions, puis additionné les deux
réponses en un taux flatteur. Ce module ne redemande donc RIEN de ce que
le module 800-53 demande déjà : il mesure ce que l'industriel AJOUTE, et
il LIT la déclaration 800-53 pour savoir si cet ajout repose sur quelque
chose.

═══ LE VERROU QUI FAIT TOUT LE SÉRIEUX DE CE MODULE ═════════════════════
UNE MESURE TAILLÉE NE PEUT PAS ÊTRE PLUS SOLIDE QUE CELLE QU'ELLE TAILLE.
Déclarer « prouvé » la segmentation OT quand la famille SC est absente du
socle 800-53, c'est prétendre avoir adapté une mesure qu'on n'a pas. Le
module calcule ce plafond axe par axe, au lieu de faire confiance.

═══ CE QUI EST COMPTÉ, ET PAR QUELLE MÉTHODE ════════════════════════════
Les chiffres de ce module ne sont pas repris d'un commentaire : ils ont
été comptés dans l'annexe G du document. La méthode, pour qu'on puisse la
refaire : on repère les en-têtes de mesure de la forme « XX-n Titre », et
l'on compte celles sous lesquelles figure une « ICS Supplemental
Guidance ». Résultat : CENT QUATRE-VINGT-CINQ mesures distinctes réparties
sur les DIX-HUIT familles. La garde en bas de fichier recompte le total et
la répartition à chaque chargement.

Ce nombre sert de POIDS, pas de dénominateur : une famille que la surcharge
retouche vingt-deux fois (SC) ne demande pas le même travail industriel
qu'une famille qu'elle retouche quatre fois (AT, RA).

═══ CE QUE LE MODULE NE PRÉTEND PAS ═════════════════════════════════════
Ce n'est pas une certification : rien ne se certifie contre 800-82. Et ce
n'est pas IEC 62443, qui est un autre référentiel, payant, et dont ce
cabinet ne recopie pas le contenu — la surcharge y renvoie d'ailleurs,
ainsi qu'au guide SCADA de l'EPRI, comme sources de sa propre doctrine.

═══ DROITS ══════════════════════════════════════════════════════════════
Œuvre du gouvernement des États-Unis, libre de citation. Les intitulés de
section et les passages cités sont en anglais, tels qu'au document. Le
français est le travail du cabinet.
"""

import nist_800_53 as socle53

# CHAQUE SOURCE DIT CE QU'ELLE A APPORTÉ — voir la raison en tête du
# registre de `nist_800_53`, où deux publications listées à l'identique
# laissaient croire que les deux avaient été lues.
SOURCES = (
    {"cle": "sp80082r2",
     "titre": "NIST SP 800-82 Rev. 2 — Guide to Industrial Control Systems "
              "(ICS) Security",
     "date": "2015-05",
     "doi": "https://doi.org/10.6028/NIST.SP.800-82r2",
     "droits": "Œuvre du gouvernement des États-Unis — libre de citation.",
     "lue": True,
     "apporte": "L'annexe G — les mesures que la surcharge industrielle "
                "retouche, famille par famille — et les raisons qu'elle "
                "donne de les retoucher.",
     "certifiable": False},
)

REVISION = "Rev. 2 (mai 2015)"
VISE = "NIST SP 800-53 Rev. 4"
RESERVE = (
    "SP 800-82 Rev. 2 surcharge la révision 4 du catalogue 800-53. Elle a "
    "été remplacée en 2023 par la révision 3, qui parle d'OT plutôt que "
    "d'ICS et se rattache à la révision 5. Ce module mesure ce que la "
    "révision 2 demande, parce que c'est elle qui est ici : un lecteur qui "
    "travaille sur la révision 3 doit le savoir avant de lire ce taux."
)


# ══════════════════════════════════════════════════════════════════════════
#  CE QUE LA SURCHARGE RETOUCHE, FAMILLE PAR FAMILLE
# ══════════════════════════════════════════════════════════════════════════
#
# Compté dans l'annexe G — voir la méthode en tête de fichier. Total : 185.

RETOUCHES = {
    "AC": 18, "AT": 4,  "AU": 12, "CA": 8,  "CP": 10, "CM": 11,
    "IA": 8,  "IR": 8,  "MA": 6,  "MP": 7,  "PE": 17, "PL": 5,
    "PS": 8,  "RA": 4,  "SA": 13, "SC": 22, "SI": 14, "PM": 10,
}
RETOUCHES_TOTAL = 185


# ══════════════════════════════════════════════════════════════════════════
#  LES DIX AXES INDUSTRIELS
# ══════════════════════════════════════════════════════════════════════════
#
# CHACUN PORTE LA SECTION DU DOCUMENT D'OÙ IL VIENT, et les familles 800-53
# qu'il surcharge. Ce rattachement n'est pas décoratif : c'est lui qui rend
# le plafond calculable — un axe ne peut pas dépasser ce que portent les
# familles qu'il taille.

AXES = (
    {"cle": "surete", "nom": "La sûreté commande la sécurité",
     "section": "§2.4 — Risk Management Requirements",
     "cite": "For an ICS, human safety and fault tolerance to prevent loss "
             "of life or endangerment of public health or confidence [...] "
             "are the primary concerns.",
     "familles": ("RA", "PL"), "poids": 3,
     "demande": "l'analyse de sûreté existe, et le programme de "
                "cybersécurité lui est subordonné — une mesure de sécurité "
                "qui peut déclencher un arrêt de procédé est un événement "
                "de sûreté avant d'être un incident informatique"},
    {"cle": "disponibilite", "nom": "Disponibilité et fenêtres d'arrêt",
     "section": "§2.4 — Availability Requirements",
     "cite": "Unexpected outages of systems that control industrial "
             "processes are not acceptable. Outages often must be planned "
             "and scheduled days or weeks in advance.",
     "familles": ("CP", "MA", "SI"), "poids": 3,
     "demande": "les fenêtres d'intervention sont négociées et tenues, et "
                "les correctifs suivent la validation du constructeur — pas "
                "le calendrier de la DSI"},
    {"cle": "segmentation", "nom": "Segmentation et protection de frontière",
     "section": "§5.1 à §5.6 — Network Segmentation and Segregation",
     "cite": "Recommended Defense-in-Depth Architecture",
     "familles": ("SC", "AC"), "poids": 3,
     "demande": "le réseau de conduite est séparé du réseau de gestion, et "
                "la frontière est tenue par un dispositif qu'on sait "
                "configurer et relire"},
    {"cle": "flux", "nom": "Règles de filtrage et flux unidirectionnels",
     "section": "§5.7 à §5.11 — Firewall policies, Unidirectional Gateways",
     "cite": "Specific ICS Firewall Issues · Unidirectional Gateways",
     "familles": ("SC",), "poids": 2,
     "demande": "les règles de filtrage sont écrites service par service, "
                "et les flux qui n'ont pas à remonter ne remontent pas"},
    {"cle": "redondance", "nom": "Points uniques de défaillance et redondance",
     "section": "§5.12 et §5.13 — Single Points of Failure, Redundancy",
     "cite": "Redundancy and Fault Tolerance",
     "familles": ("CP", "PE"), "poids": 2,
     "demande": "les points uniques sont identifiés, et la redondance est "
                "éprouvée plutôt que déclarée"},
    {"cle": "authentification", "nom": "Authentification en conduite",
     "section": "§5.14 et §5.15 — Preventing MITM, Authentication and "
                "Authorization",
     "cite": "Authentication and Authorization",
     "familles": ("IA", "AC"), "poids": 2,
     "demande": "les comptes de conduite sont nominatifs là où c'est "
                "possible, et les comptes partagés qui subsistent sont "
                "recensés avec leur motif"},
    {"cle": "surveillance", "nom": "Surveiller sans perturber",
     "section": "§5.16 — Monitoring, Logging, and Auditing",
     "cite": "Monitoring, Logging, and Auditing",
     "familles": ("AU", "SI"), "poids": 2,
     "demande": "la surveillance est passive sur les segments sensibles — "
                "un balayage actif renverse des équipements qui n'ont "
                "jamais été écrits pour y répondre"},
    {"cle": "reprise", "nom": "Détection, réponse et repli",
     "section": "§5.17 — Incident Detection, Response, and System Recovery",
     "cite": "Incident Detection, Response, and System Recovery",
     "familles": ("IR", "CP"), "poids": 3,
     "demande": "le procédé sait tourner en mode dégradé ou manuel, et "
                "quelqu'un l'a déjà fait pour de bon"},
    {"cle": "contraintes", "nom": "Ressources contraintes et systèmes hérités",
     "section": "§2.4 — Resource Constraints",
     "cite": "Indiscriminate use of IT security practices in ICS may cause "
             "availability [issues].",
     "familles": ("CM", "SA"), "poids": 2,
     "demande": "les équipements qui ne supportent ni chiffrement ni "
                "journalisation sont inventoriés, et portent des mesures "
                "compensatoires écrites"},
    {"cle": "metier", "nom": "Ceux qui tiennent le réseau de conduite",
     "section": "§2.4 — System Operation",
     "cite": "Control networks are typically managed by control engineers, "
             "not IT personnel.",
     "familles": ("AT", "PS"), "poids": 2,
     "demande": "automaticiens et informaticiens travaillent sur le même "
                "plan, et les habilitations suivent les deux métiers"},
)
AXES_PAR_CLE = {a["cle"]: a for a in AXES}
ORDRE_AXES = [a["cle"] for a in AXES]

#: La même échelle que le socle : un lecteur ne doit pas en apprendre deux.
ETATS = socle53.ETATS
ORDRE_ETATS = socle53.ORDRE_ETATS
NOTE_MAX = socle53.NOTE_MAX


def _pc(x, sur):
    return round(100.0 * x / sur, 1) if sur else None


def _plafond_axe(axe, etats53):
    """Ce que le socle 800-53 laisse atteindre à un axe industriel.

    LA RÈGLE, ET ELLE TIENT EN UNE PHRASE : une mesure taillée ne peut pas
    être plus solide que celle qu'elle taille. On prend donc la PLUS FAIBLE
    des familles surchargées — pas leur moyenne. Une segmentation OT qui
    s'appuie sur SC prouvée et AC absente vaut ce que vaut AC : le chemin le
    plus faible est celui qu'un attaquant prend.
    """
    notes = []
    for f in axe["familles"]:
        etat = etats53.get(f)
        if etat == "sans_objet":
            continue
        notes.append(ETATS[etat]["note"] if etat in ETATS else 0.0)
    if not notes:
        return None
    return min(notes)


def evaluer(etats_ot=None, etats_800_53=None):
    """Le profil industriel, et ce que le socle 800-53 lui permet.

    DEUX DÉCLARATIONS ENTRENT ICI, ET CE N'EST PAS UNE COMMODITÉ : sans la
    première, le module ne saurait pas ce que l'industriel ajoute ; sans la
    seconde, il ne saurait pas si cet ajout repose sur quelque chose.
    """
    etats_ot = etats_ot if isinstance(etats_ot, dict) else {}
    etats53 = etats_800_53 if isinstance(etats_800_53, dict) else {}

    inconnus = [k for k in etats_ot if k not in AXES_PAR_CLE]
    mauvais = [k for k, v in etats_ot.items() if v not in ETATS]
    if inconnus:
        return {"ok": False, "motif": "axes_inconnus", "detail": sorted(inconnus)[:8]}
    if mauvais:
        return {"ok": False, "motif": "etats_inconnus", "detail": sorted(mauvais)[:8]}
    hors53 = [k for k in etats53 if k not in socle53.FAMILLES_PAR_CLE]
    if hors53:
        return {"ok": False, "motif": "familles_800_53_inconnues",
                "detail": sorted(hors53)[:8]}

    profils, depassements = [], []
    for axe in AXES:
        etat = etats_ot.get(axe["cle"])
        note = ETATS[etat]["note"] if etat in ETATS else None
        plafond = _plafond_axe(axe, etats53)
        retenu = etat != "sans_objet"
        # LE DÉPASSEMENT EST RELEVÉ, PAS CORRIGÉ EN SILENCE. Rabattre la note
        # sans le dire ferait disparaître le défaut de l'écran : c'est
        # précisément ce qu'il faut montrer.
        depasse = (retenu and note is not None and plafond is not None
                   and note > plafond)
        if depasse:
            depassements.append(axe)
        profils.append({
            "axe": axe["cle"], "nom": axe["nom"], "poids": axe["poids"],
            "section": axe["section"], "cite": axe["cite"],
            "demande": axe["demande"],
            "familles": [{"cle": f,
                          "titre": socle53.FAMILLES_PAR_CLE[f][1],
                          "retouches": RETOUCHES.get(f),
                          "etat_800_53": etats53.get(f)}
                         for f in axe["familles"]],
            "retouches": sum(RETOUCHES.get(f, 0) for f in axe["familles"]),
            "etat": etat,
            "etat_nom": ETATS[etat]["nom"] if etat in ETATS else None,
            "note": note, "sur": NOTE_MAX,
            "plafond": plafond,
            "note_retenue": (min(note, plafond)
                             if (note is not None and plafond is not None)
                             else note),
            "depasse_le_socle": depasse,
        })

    retenus = [p for p in profils if p["etat"] != "sans_objet"]
    renseignes = [p for p in retenus if p["note"] is not None]
    acquis = sum(p["note_retenue"] for p in renseignes)
    taux = _pc(acquis, NOTE_MAX * len(retenus)) if retenus else None

    verrous = []

    # 1. LA SURCHARGE SANS SON SOCLE. Mesurer l'adaptation industrielle d'un
    #    catalogue qu'on n'a pas déclaré revient à noter une traduction sans
    #    l'original.
    if not etats53:
        verrous.append({
            "cle": "surcharge_sans_socle",
            "dit": "Aucune famille SP 800-53 n'est déclarée. La surcharge "
                   "industrielle adapte ce catalogue : sans lui, ce taux "
                   "mesure une adaptation de rien."})

    # 2. LES AXES QUI DÉPASSENT CE QU'ILS TAILLENT.
    if depassements:
        verrous.append({
            "cle": "axes_au_dessus_du_socle",
            "dit": "%s au-dessus de la famille 800-53 qu'%s : %s. Une "
                   "mesure taillée ne peut pas être plus solide que celle "
                   "qu'elle taille."
                   % ("%d axes industriels sont déclarés" % len(depassements)
                      if len(depassements) > 1
                      else "Un axe industriel est déclaré",
                      "ils taillent" if len(depassements) > 1
                      else "il taille",
                      ", ".join(a["nom"] for a in depassements))})

    # 3. LA SÛRETÉ ÉCARTÉE. Tout peut se tailler en OT, sauf cela.
    if etats_ot.get("surete") == "sans_objet":
        verrous.append({
            "cle": "surete_ecartee",
            "dit": "La sûreté est déclarée sans objet. Dans un système "
                   "industriel, elle prime sur la sécurité : l'écarter "
                   "retire au taux le seul axe dont dépendent les autres."})

    return {
        "ok": True,
        "revision": REVISION,
        "vise": VISE,
        "axes": len(AXES),
        "renseignes": len(renseignes),
        "ecartes": len(profils) - len(retenus),
        "profils": profils,
        "taux": taux,
        "retouches_total": RETOUCHES_TOTAL,
        "familles_surchargees": len(RETOUCHES),
        "verrous": verrous,
        "certifiable": False,
        "reserve": RESERVE,
        "reserve_socle": "Rien ne se certifie contre SP 800-82 : ce taux dit "
                         "l'adaptation industrielle déclarée d'un catalogue "
                         "volontaire, pas une conformité reconnue.",
    }


def referentiel():
    return {
        "sources": [dict(s) for s in SOURCES],
        "revision": REVISION, "vise": VISE, "reserve": RESERVE,
        "etats": [dict(ETATS[c], cle=c) for c in ORDRE_ETATS],
        "retouches": dict(RETOUCHES),
        "retouches_total": RETOUCHES_TOTAL,
        "axes": [{"cle": a["cle"], "nom": a["nom"], "poids": a["poids"],
                  "section": a["section"], "cite": a["cite"],
                  "demande": a["demande"],
                  "familles": [{"cle": f,
                                "titre": socle53.FAMILLES_PAR_CLE[f][1],
                                "retouches": RETOUCHES.get(f)}
                               for f in a["familles"]]}
                 for a in AXES],
        "certifiable": False,
    }


# ══════════════════════════════════════════════════════════════════════════
#  LA GARDE — elle recompte à chaque chargement
# ══════════════════════════════════════════════════════════════════════════

def _verifier():
    # LE TOTAL EST RECOMPTÉ, PAS RECOPIÉ. Un chiffre annoncé en tête de
    # fichier et démenti par la table serait le défaut exact que ce cabinet
    # traque ailleurs.
    assert sum(RETOUCHES.values()) == RETOUCHES_TOTAL, sum(RETOUCHES.values())
    assert len(RETOUCHES) == 18, len(RETOUCHES)
    # LA SURCHARGE NE RETOUCHE QUE DES FAMILLES QUI EXISTENT DANS LA RÉVISION
    # VISÉE. Une famille de la révision 5 glissée ici passerait pour taillée
    # alors que le document ne l'a jamais vue.
    inconnues = sorted(set(RETOUCHES) - set(socle53.FAMILLES_PAR_CLE))
    assert not inconnues, inconnues
    manquantes = sorted(set(socle53.FAMILLES_PAR_CLE) - set(RETOUCHES))
    assert not manquantes, (
        "familles 800-53 sans compte de retouches : %s" % manquantes)
    # CHAQUE AXE EST RATTACHÉ À DES FAMILLES RÉELLES — sans quoi son plafond
    # ne se calculerait sur rien, et le verrou du socle serait décoratif.
    for a in AXES:
        assert a["familles"], a["cle"]
        for f in a["familles"]:
            assert f in socle53.FAMILLES_PAR_CLE, (a["cle"], f)
    assert len(AXES_PAR_CLE) == len(AXES), "deux axes portent la même clé"
    assert "surete" in AXES_PAR_CLE


_verifier()
