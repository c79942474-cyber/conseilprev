# -*- coding: utf-8 -*-
"""ISO/IEC 42001:2023 — le système de management de l'IA, rendu pilotable.

═══════════════════════════════════════════════════════════════════════════
 AVERTISSEMENT DE DROIT D'AUTEUR — À LIRE AVANT DE MODIFIER CE MODULE
═══════════════════════════════════════════════════════════════════════════

ISO/IEC 42001:2023 EST PROTÉGÉE PAR LE DROIT D'AUTEUR. Son propre en-tête
est sans ambiguïté :

    « DOCUMENT PROTÉGÉ PAR COPYRIGHT — © ISO/IEC 2023. Tous droits réservés.
      […] aucune partie de cette publication ne peut être reproduite ni
      utilisée sous quelque forme que ce soit et par aucun procédé […] sans
      autorisation écrite préalable. »

Ce module cite donc, et seulement :

    · les NUMÉROS d'articles et de mesures (4.1, 8.4, A.6.2.3…) ;
    · leurs TITRES, qui sont des désignations permettant de s'y référer.

TOUT LE RESTE — ce que chaque article demande, ce qu'il faut produire, ce
qui fait échouer un audit — EST RÉDIGÉ PAR LE CABINET. Aucune phrase
normative de la norme n'est reproduite ici, ni dans les restitutions, ni
dans les livrables. Ce n'est pas une précaution de forme : recopier une
norme payante dans un outil vendu est une contrefaçon, et l'outil qui le
ferait serait un passif, pas un actif.

    CE QUE ÇA IMPOSE À QUI MODIFIE CE FICHIER : pour enrichir un `dit`, on
    lit la norme, on la comprend, et on l'écrit avec ses mots. On ne colle
    pas. Un `dit` qui ressemble à une phrase de norme doit être réécrit.

    ET CE QUE ÇA IMPOSE AU CLIENT : Sentinel ne remplace pas l'achat de la
    norme. Un organisme qui veut se certifier doit détenir le texte. Le
    module le dit dans chaque restitution.

═══════════════════════════════════════════════════════════════════════════
 LA DÉCISION QUI COMMANDE TOUTES LES AUTRES
═══════════════════════════════════════════════════════════════════════════

    QUELLES MESURES DE L'ANNEXE A RETENEZ-VOUS, LESQUELLES ÉCARTEZ-VOUS,
    ET POUR CHACUNE : POURQUOI ?

C'est la déclaration d'applicabilité, exigée par l'article 6.1.3 f). Elle
contient les mesures retenues ET la justification de leur inclusion COMME
de leur exclusion. Les deux. C'est le premier document que l'auditeur ouvre.

D'où le fait qui coûte le plus cher, et qu'aucun tableau de maturité ne
fait voir :

    UNE MESURE ÉCARTÉE AVEC JUSTIFICATION EST CONFORME.
    UNE MESURE LAISSÉE VIDE FAIT ÉCHOUER L'AUDIT D'ÉTAPE 1 —
    avant que quiconque ait regardé ce que l'organisme fait vraiment.

Un organisme qui aurait mis en œuvre trente-six mesures sur trente-huit et
laissé deux cases vides échoue à l'étape documentaire ; un organisme qui en
retient dix-huit et en écarte vingt, chacune motivée, passe. La conformité
ne se mesure pas en cases cochées, elle se mesure en cases DÉCIDÉES.

═══════════════════════════════════════════════════════════════════════════
 CE QUI DISTINGUE 42001 DES TROIS AUTRES CADRES DE SENTINEL
═══════════════════════════════════════════════════════════════════════════

ELLE EST CERTIFIABLE, ET ELLE EST LA SEULE.

    · RGPD, NIS 2, CRA  → du DROIT. On s'y conforme ; personne ne délivre
      d'attestation de conformité au RGPD, et le marquage CE du CRA est
      apposé par le fabricant lui-même (sauf classe II et annexe IV).
    · ISO/IEC 42001     → une NORME VOLONTAIRE, auditée par un organisme
      accrédité tiers, qui délivre un certificat opposable à un client, à
      un acheteur public, à un assureur.

C'est ce qui en fait un actif commercial et pas seulement un coût : le
certificat se montre. Et c'est pourquoi la déclaration d'applicabilité
compte autant — c'est l'objet que l'auditeur audite.

═══════════════════════════════════════════════════════════════════════════
 CE QUE CE MODULE N'EST PAS
═══════════════════════════════════════════════════════════════════════════

CE N'EST PAS LE REGISTRE DES SYSTÈMES D'IA DE L'IA ACT. 42001 compte un
SYSTÈME DE MANAGEMENT — une organisation, un périmètre, des processus. L'IA
Act compte des SYSTÈMES D'IA, qualifiés par leur usage et leur risque.
Être certifié 42001 ne rend conforme à aucune obligation de l'IA Act, et ne
dispense d'aucune ; inversement, un système d'IA à haut risque parfaitement
conforme à l'IA Act ne vaut pas un système de management certifié.

ET LES TROIS ÉVALUATIONS D'IMPACT NE SONT PAS LA MÊME. C'est la confusion
la plus coûteuse du domaine, parce que les trois portent sur le même objet :

    · 42001, art. 6.1.4 et 8.4 + annexe A.5 → impact du système d'IA sur
      les personnes, les groupes et la société — exigence NORMATIVE ;
    · IA Act, art. 27 → analyse d'impact sur les DROITS FONDAMENTAUX (AIDF),
      due par certains déployeurs de systèmes à haut risque — exigence LÉGALE ;
    · RGPD, art. 35 → analyse d'impact relative à la PROTECTION DES DONNÉES
      (AIPD), due dès qu'un traitement présente un risque élevé — exigence
      LÉGALE, et sur les seules données à caractère personnel.

Une seule des trois peut être suffisante pour les trois : aucune. Elles se
NOURRISSENT l'une l'autre — même inventaire, même cartographie des parties
affectées — et le module dit où le travail se réutilise, sans jamais
prétendre qu'un document en remplace un autre.
"""


# ═══════════════════════════════════════════════════════════════════════════
#  LA SOURCE, ET SA LICENCE
# ═══════════════════════════════════════════════════════════════════════════

SOURCE = {
    "titre": "ISO/IEC 42001:2023 — Technologies de l'information — "
             "Intelligence artificielle — Système de management",
    "court": "ISO/IEC 42001:2023",
    "editeur": "ISO / IEC (JTC 1/SC 42)",
    "millesime": "2023-12",
    "ics": "03.100.70 ; 35.020",
    "url": "https://www.iso.org/standard/81230.html",
    # LA LIGNE QUI COMMANDE TOUT LE MODULE.
    "licence": "PROTÉGÉE PAR LE DROIT D'AUTEUR — © ISO/IEC 2023, tous droits "
               "réservés. Aucune partie du texte normatif n'est reproduite "
               "ici : seuls les numéros et les titres d'articles et de "
               "mesures sont cités, et tout ce qui les décrit est rédigé par "
               "le cabinet.",
    "reproduction": False,
    "achat": "La mise en œuvre suppose de détenir le texte de la norme, qui "
             "s'achète auprès de l'ISO ou d'un organisme national de "
             "normalisation (AFNOR en France).",
    "certifiable": True,
    "lu_le": "2026-09-18",
}


# ═══════════════════════════════════════════════════════════════════════════
#  LES ARTICLES 4 À 10 — LA STRUCTURE DE HAUT NIVEAU
# ═══════════════════════════════════════════════════════════════════════════
#
# POURQUOI CETTE STRUCTURE EST LA MÊME QUE CELLE DE 9001 ET DE 27001 : c'est
# la « structure harmonisée » des normes de système de management. Ce n'est
# pas un détail d'édition — c'est ce qui permet à un organisme déjà certifié
# 27001 de greffer 42001 sur le même socle (revue de direction, audit
# interne, non-conformités) au lieu de monter un second système.
#
# CE QUE LE MODULE EN TIRE, ET QUI VAUT DE L'ARGENT : il nomme, pour chaque
# article, s'il est MUTUALISABLE avec un système de management existant.
# Un organisme déjà certifié 27001 n'a pas trente-quatre articles à monter,
# il en a une douzaine, et le reste s'étend.

CHAPITRES = (
    ("4", "Contexte de l'organisme", (
        ("4.1", "Compréhension de l'organisme et de son contexte",
         "Nommer ce qui, dehors et dedans, pèse sur la façon dont "
         "l'organisme conçoit ou utilise l'IA : marché, droit applicable, "
         "attentes sociétales, maturité interne.", True),
        ("4.2", "Compréhension des besoins et des attentes des parties "
                "intéressées",
         "Recenser qui a quelque chose à perdre ou à dire — clients, "
         "salariés, personnes soumises aux décisions du système, "
         "régulateurs — et ce que chacun attend.", True),
        ("4.3", "Détermination du périmètre du système de management de l'IA",
         "Écrire ce qui est dedans et ce qui est dehors. Un périmètre flou "
         "est la première cause de dérive de coût d'un audit : tout ce qui "
         "n'est pas exclu par écrit est audité.", False),
        ("4.4", "Système de management de l'IA",
         "Établir, mettre en œuvre, tenir à jour et améliorer le système "
         "lui-même — l'article qui dit que le reste doit exister pour de "
         "bon, pas seulement sur le papier.", False),
    )),
    ("5", "Leadership", (
        ("5.1", "Leadership et engagement",
         "La direction s'engage, et ça se prouve : ressources allouées, "
         "arbitrages rendus, sujet porté au plus haut niveau.", True),
        ("5.2", "Politique d'IA",
         "Le document court qui dit ce que l'organisme s'autorise et "
         "s'interdit en matière d'IA, et qui engage sa direction.", False),
        ("5.3", "Rôles, responsabilités et autorités au sein de l'organisme",
         "Qui décide, qui met en œuvre, qui contrôle — et qui répond quand "
         "un système se comporte mal.", True),
    )),
    ("6", "Planification", (
        ("6.1.1", "Actions à mettre en œuvre face aux risques et "
                  "opportunités — Généralités",
         "Le cadre : ce que la planification doit produire, et sur quoi "
         "elle s'appuie.", True),
        ("6.1.2", "Appréciation des risques liés à l'IA",
         "Identifier, analyser et évaluer les risques que l'IA fait courir "
         "— à l'organisme ET aux personnes. La double lecture est ce qui "
         "distingue cette appréciation d'une analyse de risque classique.",
         False),
        ("6.1.3", "Traitement des risques liés à l'IA",
         "Choisir les mesures, vérifier qu'elles couvrent les options de "
         "traitement retenues, et PRODUIRE LA DÉCLARATION D'APPLICABILITÉ "
         "avec la justification de chaque inclusion et de chaque exclusion.",
         False),
        ("6.1.4", "Évaluation de l'impact du système d'IA",
         "L'évaluation d'impact, vue depuis la planification : elle doit "
         "être prévue, cadrée et reliée à l'appréciation des risques.",
         False),
        ("6.2", "Objectifs d'IA et planification pour les atteindre",
         "Des objectifs mesurables, datés, avec un responsable — et le plan "
         "qui dit comment on y arrive.", True),
        ("6.3", "Planification des changements",
         "Les changements du système de management se planifient ; ils ne "
         "se constatent pas après coup.", True),
    )),
    ("7", "Soutien", (
        ("7.1", "Ressources",
         "Les moyens humains, techniques et financiers, déterminés et "
         "fournis — pas espérés.", True),
        ("7.2", "Compétences",
         "Savoir quelles compétences le système exige, vérifier qu'on les "
         "a, et combler l'écart.", True),
        ("7.3", "Sensibilisation",
         "Que les personnes concernées sachent ce qu'on attend d'elles et "
         "ce qu'un manquement produit.", True),
        ("7.4", "Communication",
         "Qui communique quoi, à qui, quand et par quel canal — en interne "
         "comme au dehors.", True),
        ("7.5.1", "Informations documentées — Généralités",
         "Ce que le système doit consigner, et ce que l'organisme juge "
         "nécessaire d'y ajouter.", True),
        ("7.5.2", "Création et mise à jour des informations documentées",
         "Identification, format, revue et approbation : la discipline "
         "documentaire ordinaire des systèmes de management.", True),
        ("7.5.3", "Maîtrise des informations documentées",
         "Disponibilité, protection, conservation, suppression — y compris "
         "pour les documents d'origine externe.", True),
    )),
    ("8", "Exploitation", (
        ("8.1", "Planification et maîtrise opérationnelles",
         "Faire tourner ce qui a été planifié, maîtriser les changements, "
         "et tenir les processus externalisés.", True),
        ("8.2", "Appréciation des risques liés à l'IA",
         "L'appréciation des risques, exécutée et tenue à jour — à "
         "intervalles planifiés et quand quelque chose change.", False),
        ("8.3", "Traitement des risques liés à l'IA",
         "Le plan de traitement, mis en œuvre, et la preuve qu'il l'a été.",
         False),
        ("8.4", "Évaluation de l'impact du système d'IA",
         "L'évaluation d'impact, exécutée. C'est ici que le travail fait "
         "pour l'AIDF du RGPD et pour l'AIDF de l'IA Act se réutilise — et "
         "ici qu'il ne suffit pas.", False),
    )),
    ("9", "Évaluation des performances", (
        ("9.1", "Surveillance, mesure, analyse et évaluation",
         "Ce qu'on mesure, comment, à quelle fréquence, et ce qu'on conclut "
         "des mesures.", True),
        ("9.2.1", "Audit interne — Généralités",
         "Le système s'audite lui-même, à intervalles planifiés.", True),
        ("9.2.2", "Programme d'audit interne",
         "Fréquence, méthodes, responsabilités, exigences de compte rendu "
         "— et des auditeurs qui n'auditent pas leur propre travail.", True),
        ("9.3.1", "Revue de direction — Généralités",
         "La direction revoit le système à intervalles planifiés.", True),
        ("9.3.2", "Éléments d'entrée de la revue de direction",
         "Ce que la direction doit avoir sous les yeux : suites des revues "
         "précédentes, changements, performance, non-conformités, retours "
         "des parties intéressées.", True),
        ("9.3.3", "Résultats de la revue de direction",
         "Les décisions prises — et les ressources engagées pour les tenir.",
         True),
    )),
    ("10", "Amélioration", (
        ("10.1", "Amélioration continue",
         "Pertinence, adéquation et efficacité du système, améliorées en "
         "continu.", True),
        ("10.2", "Non-conformité et action corrective",
         "Réagir, en corriger les conséquences, chercher la cause, agir sur "
         "la cause, et vérifier que ça a marché.", True),
    )),
)

SOUS_CHAPITRES = {}
for _num, _titre, _sous in CHAPITRES:
    for _n, _t, _d, _mut in _sous:
        SOUS_CHAPITRES[_n] = {"chapitre": _num, "chapitre_titre": _titre,
                              "titre": _t, "dit": _d, "mutualisable": _mut}

# LES ARTICLES QUI NE SE MUTUALISENT PAS — le vrai coût d'entrée quand on
# part d'un système déjà certifié (27001, 9001…). Ce sont eux qui portent ce
# que 42001 apporte de neuf : la politique d'IA, le périmètre, et surtout
# l'appréciation des risques et l'évaluation d'impact spécifiques à l'IA.
PROPRES_A_L_IA = tuple(n for n, v in sorted(SOUS_CHAPITRES.items())
                       if not v["mutualisable"])


# ═══════════════════════════════════════════════════════════════════════════
#  L'ANNEXE A — LES MESURES, ET CE QUE LA DÉCLARATION D'APPLICABILITÉ EN FAIT
# ═══════════════════════════════════════════════════════════════════════════
#
# LA NORME LE DIT ELLE-MÊME : les mesures de l'annexe A ne sont pas
# exhaustives, et un organisme peut en concevoir d'autres. Le module compte
# donc les trente-huit, et laisse une place aux mesures propres — sans quoi
# une déclaration d'applicabilité complète paraîtrait incomplète, ou
# l'inverse.

ANNEXE_A = (
    ("A.2", "Politiques relatives à l'IA",
     "Donner à la direction une orientation écrite et un soutien pour les "
     "systèmes d'IA.", (
         ("A.2.2", "Politique d'IA"),
         ("A.2.3", "Alignement sur les autres politiques organisationnelles"),
         ("A.2.4", "Examen de la politique d'IA"),
     )),
    ("A.3", "Organisation interne",
     "Installer la redevabilité : que quelqu'un réponde de chaque système, "
     "et qu'une préoccupation puisse remonter.", (
         ("A.3.2", "Rôles et responsabilités en matière d'IA"),
         ("A.3.3", "Signalement des préoccupations"),
     )),
    ("A.4", "Ressources pour les systèmes d'IA",
     "Recenser ce dont les systèmes dépendent — données, outils, "
     "infrastructure, humains — pour pouvoir en apprécier les risques.", (
         ("A.4.2", "Documentation des ressources"),
         ("A.4.3", "Ressources de données"),
         ("A.4.4", "Ressources d'outillage"),
         ("A.4.5", "Ressources système et informatiques"),
         ("A.4.6", "Ressources humaines"),
     )),
    ("A.5", "Évaluation des impacts des systèmes d'IA",
     "Évaluer ce que les systèmes font subir aux personnes, aux groupes et "
     "à la société — le point de couture avec l'IA Act et le RGPD.", (
         ("A.5.2", "Processus d'évaluation de l'impact du système d'IA"),
         ("A.5.3", "Documentation des évaluations de l'impact du système "
                   "d'IA"),
         ("A.5.4", "Évaluation de l'impact du système d'IA sur des personnes "
                   "ou groupes potentiels"),
         ("A.5.5", "Évaluation des impacts sociétaux des systèmes d'IA"),
     )),
    ("A.6", "Cycle de vie de système d'IA",
     "Tenir le système de bout en bout : objectifs de développement, "
     "conception, vérification, déploiement, exploitation, journalisation.",
     (
         ("A.6.1.2", "Objectifs pour un développement responsable du système "
                     "d'IA"),
         ("A.6.1.3", "Processus de conception et de développement "
                     "responsables du système d'IA"),
         ("A.6.2.2", "Exigences et spécification du système d'IA"),
         ("A.6.2.3", "Documentation de la conception et du développement du "
                     "système d'IA"),
         ("A.6.2.4", "Vérification et validation du système d'IA"),
         ("A.6.2.5", "Déploiement du système d'IA"),
         ("A.6.2.6", "Exploitation et surveillance du système d'IA"),
         ("A.6.2.7", "Documentation technique du système d'IA"),
         ("A.6.2.8", "Enregistrement des journaux d'événements du système "
                     "d'IA"),
     )),
    ("A.7", "Données pour les systèmes d'IA",
     "Savoir d'où viennent les données, ce qu'elles valent, et ce qu'on "
     "leur a fait subir avant l'entraînement.", (
         ("A.7.2", "Données pour le développement et l'amélioration du "
                   "système d'IA"),
         ("A.7.3", "Acquisition de données"),
         ("A.7.4", "Qualité des données pour les systèmes d'IA"),
         ("A.7.5", "Provenance des données"),
         ("A.7.6", "Préparation des données"),
     )),
    ("A.8", "Informations à l'attention des parties intéressées des systèmes "
            "d'IA",
     "Dire aux utilisateurs, aux clients et au public ce qu'ils doivent "
     "savoir — y compris quand ça se passe mal.", (
         ("A.8.2", "Documentation et informations du système à l'attention "
                   "des utilisateurs"),
         ("A.8.3", "Comptes rendus externes"),
         ("A.8.4", "Communication des incidents"),
         ("A.8.5", "Informations à l'attention des parties intéressées"),
     )),
    ("A.9", "Utilisation des systèmes d'IA",
     "Encadrer l'usage : pour quoi le système est prévu, et ce qu'on "
     "s'interdit d'en faire.", (
         ("A.9.2", "Processus d'utilisation responsable des systèmes d'IA"),
         ("A.9.3", "Objectifs d'utilisation responsable"),
         ("A.9.4", "Utilisation prévue du système d'IA"),
     )),
    ("A.10", "Relations avec les tiers et avec les clients",
     "Répartir les responsabilités avec les fournisseurs et les clients — "
     "et s'assurer que ce qu'on achète tient les mêmes engagements.", (
         ("A.10.2", "Répartition des responsabilités"),
         ("A.10.3", "Fournisseurs"),
         ("A.10.4", "Clients"),
     )),
)

MESURES = {}
for _og, _ot, _od, _liste in ANNEXE_A:
    for _num, _titre in _liste:
        MESURES[_num] = {"objectif": _og, "objectif_titre": _ot,
                         "objectif_dit": _od, "titre": _titre}

# LE FAIT QUE LA NORME ÉNONCE, ET QU'UN TABLEAU DE CORRESPONDANCE OUBLIE.
NON_EXHAUSTIVE = {
    "quoi": "Les mesures de l'annexe A ne sont pas exhaustives : un "
            "organisme peut en concevoir d'autres, ou s'inspirer de sources "
            "existantes, si le traitement des risques l'exige.",
    "consequence": "Une déclaration d'applicabilité qui couvre les "
                   "trente-huit mesures de l'annexe A n'est pas pour autant "
                   "complète : elle l'est si elle couvre les options de "
                   "traitement retenues, ce qui peut demander davantage.",
    "article": "art. 6.1.3 d) et NOTE 2",
}


# ═══════════════════════════════════════════════════════════════════════════
#  LA DÉCLARATION D'APPLICABILITÉ
# ═══════════════════════════════════════════════════════════════════════════

_DECISIONS = ("retenue", "ecartee")


def declaration_applicabilite(decisions=None, mesures_propres=None):
    """L'artefact que l'auditeur ouvre en premier — et ce qui le fait tomber.

    ═══ LES TROIS ÉTATS, ET POURQUOI LE TROISIÈME EST LE SEUL FATAL ═════
    Une mesure est RETENUE (et justifiée), ÉCARTÉE (et justifiée), ou
    NON DÉCIDÉE. L'article 6.1.3 f) exige une justification dans les DEUX
    premiers cas ; le troisième n'est pas prévu par la norme, et c'est
    précisément pour ça qu'il fait échouer l'étape documentaire.

    ═══ CE QUE CE COMPTE REND VISIBLE, ET QU'UN TAUX NE REND PAS ════════
    Un taux de mise en œuvre à 95 % rassure. Il ne dit pas que deux mesures
    n'ont jamais été tranchées, et que ces deux-là suffisent à renvoyer
    l'organisme à l'étape 1. Le module rend donc TROIS nombres et jamais un
    seul : décidées, non décidées, et justifications manquantes.
    """
    d = decisions or {}
    if not isinstance(d, dict):
        return {"ok": False, "motif": "decisions_illisibles"}
    propres = mesures_propres or []
    if not isinstance(propres, list):
        return {"ok": False, "motif": "mesures_propres_illisibles"}

    lignes, sans_justification = [], []
    for num in sorted(MESURES, key=_ordre):
        brut = d.get(num)
        if isinstance(brut, str):
            brut = {"decision": brut}
        brut = brut if isinstance(brut, dict) else {}
        decision = brut.get("decision")
        decision = decision if decision in _DECISIONS else "non_decidee"
        justification = str(brut.get("justification") or "").strip()
        manque = (decision in _DECISIONS and not justification)
        if manque:
            sans_justification.append(num)
        lignes.append(dict(
            MESURES[num], numero=num, decision=decision,
            justification=justification or None,
            justification_manquante=manque,
            mise_en_oeuvre=(brut.get("mise_en_oeuvre")
                            if brut.get("mise_en_oeuvre") in _ETATS
                            else "non_renseignee")))

    non_decidees = [l["numero"] for l in lignes
                    if l["decision"] == "non_decidee"]
    retenues = [l for l in lignes if l["decision"] == "retenue"]
    ecartees = [l for l in lignes if l["decision"] == "ecartee"]
    faites = [l for l in retenues if l["mise_en_oeuvre"] == "conforme"]

    # ── LE VERDICT D'ÉTAPE 1, ET IL NE PARDONNE PAS ──────────────────────
    bloquants = []
    if non_decidees:
        bloquants.append(
            "%d mesure(s) ne sont ni retenues ni écartées : %s"
            % (len(non_decidees), ", ".join(non_decidees)))
    if sans_justification:
        bloquants.append(
            "%d décision(s) ne portent aucune justification : %s"
            % (len(sans_justification), ", ".join(sans_justification)))

    return {
        "ok": True,
        "lignes": lignes,
        "objectifs": _par_objectif(lignes),
        "total": len(lignes),
        "retenues": len(retenues),
        "ecartees": len(ecartees),
        "non_decidees": non_decidees,
        "sans_justification": sans_justification,
        "mises_en_oeuvre": len(faites),
        # LE TAUX PORTE SUR LES SEULES MESURES RETENUES — écarter une mesure
        # justifiée ne doit ni pénaliser ni flatter le taux.
        "taux_mise_en_oeuvre": (round(100.0 * len(faites) / len(retenues))
                                if retenues else None),
        "taux_decision": round(100.0 * (len(lignes) - len(non_decidees))
                               / len(lignes)),
        "mesures_propres": [str(x).strip() for x in propres
                            if str(x).strip()],
        "recevable": not bloquants,
        "bloquants": bloquants,
        "dit": ("La déclaration est recevable en l'état : chaque mesure est "
                "tranchée et motivée. Reste la mise en œuvre, qui s'audite à "
                "l'étape 2." if not bloquants else
                "La déclaration n'est PAS recevable pour un audit d'étape 1. "
                "Ce n'est pas un défaut de sécurité, c'est un défaut de "
                "document — et il se corrige en écrivant, pas en "
                "développant."),
        "non_exhaustive": NON_EXHAUSTIVE,
        "article": "art. 6.1.3 f)",
        "source": SOURCE,
    }


def _ordre(num):
    """Trier A.6.2.10 après A.6.2.9, et non entre A.6.2.1 et A.6.2.2."""
    return tuple(int(x) for x in num[2:].split(".") if x.isdigit())


def _par_objectif(lignes):
    groupes = []
    for og, ot, od, liste in ANNEXE_A:
        nums = [n for n, _t in liste]
        sous = [l for l in lignes if l["numero"] in nums]
        groupes.append({
            "numero": og, "titre": ot, "dit": od, "lignes": sous,
            "retenues": sum(1 for l in sous if l["decision"] == "retenue"),
            "ecartees": sum(1 for l in sous if l["decision"] == "ecartee"),
            "non_decidees": sum(1 for l in sous
                                if l["decision"] == "non_decidee"),
        })
    return groupes


# ═══════════════════════════════════════════════════════════════════════════
#  LA MATURITÉ SUR LES ARTICLES 4 À 10
# ═══════════════════════════════════════════════════════════════════════════

_ETATS = ("conforme", "partiel", "non_conforme", "sans_objet")


def maturite(declares=None):
    """L'écart sur les articles — et ce que « sans objet » ne peut pas être.

    UNE DIFFÉRENCE AVEC L'ANNEXE A QUI COÛTE UN AUDIT : les mesures de
    l'annexe A s'écartent avec justification ; LES ARTICLES 4 À 10, NON.
    Ce sont des exigences, pas des mesures. Un organisme qui déclarerait
    « 9.2 Audit interne : sans objet » n'a pas écarté une mesure, il a
    renoncé à la certification. Le module refuse donc `sans_objet` sur un
    article, et dit pourquoi.
    """
    d = declares or {}
    if not isinstance(d, dict):
        return {"ok": False, "motif": "declaration_illisible"}

    chapitres, refus = [], []
    for num, titre, sous in CHAPITRES:
        lignes = []
        for n, t, dit, mut in sous:
            e = d.get(n)
            if e == "sans_objet":
                refus.append(n)
                e = None
            lignes.append({
                "numero": n, "titre": t, "dit": dit, "mutualisable": mut,
                "etat": e if e in ("conforme", "partiel", "non_conforme")
                        else "non_renseigne"})
        chapitres.append({
            "numero": num, "titre": titre, "lignes": lignes,
            "conformes": sum(1 for l in lignes if l["etat"] == "conforme"),
            "total": len(lignes)})

    toutes = [l for c in chapitres for l in c["lignes"]]
    conformes = [l for l in toutes if l["etat"] == "conforme"]
    propres = [l for l in toutes if not l["mutualisable"]]
    propres_faits = [l for l in propres if l["etat"] == "conforme"]
    return {
        "ok": True,
        "chapitres": chapitres,
        "total": len(toutes),
        "conformes": len(conformes),
        "taux": round(100.0 * len(conformes) / len(toutes)),
        "non_renseigne": sum(1 for l in toutes if l["etat"] == "non_renseigne"),
        # LE SECOND TAUX, QUI EST LE SEUL UTILE À QUI EST DÉJÀ CERTIFIÉ
        # AILLEURS : sur les articles que 42001 ajoute vraiment.
        "propres_a_l_ia": {
            "total": len(propres), "conformes": len(propres_faits),
            "taux": round(100.0 * len(propres_faits) / len(propres)),
            "numeros": [l["numero"] for l in propres],
            "dit": "Ces articles ne se reprennent pas d'un système de "
                   "management existant : ce sont eux qui portent ce que "
                   "42001 ajoute.",
        },
        "refus_sans_objet": refus,
        "dit_refus": ("Un article de 4 à 10 ne se déclare pas « sans "
                      "objet » : les exigences ne s'écartent pas, seules "
                      "les mesures de l'annexe A le peuvent (art. 6.1.3 f). "
                      "%d déclaration(s) ont été ignorées." % len(refus))
                     if refus else None,
        "source": SOURCE,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  LA CERTIFICATION — LES DEUX ÉTAPES, ET CE QUI SE JOUE DANS CHACUNE
# ═══════════════════════════════════════════════════════════════════════════

CERTIFICATION = {
    "nature": "Certification par un organisme tiers accrédité — la seule "
              "des quatre références de Sentinel qui délivre un certificat "
              "opposable.",
    "etapes": (
        {"cle": "etape_1", "nom": "Audit d'étape 1 — revue documentaire",
         "objet": "L'auditeur vérifie que le système EXISTE sur le papier : "
                  "périmètre, politique, appréciation des risques, "
                  "déclaration d'applicabilité, plan d'audit interne.",
         "ce_qui_fait_tomber": "Une déclaration d'applicabilité incomplète "
                               "— une mesure ni retenue ni écartée, ou une "
                               "décision sans justification. Le défaut est "
                               "documentaire, et il arrête tout avant "
                               "l'étape 2."},
        {"cle": "etape_2", "nom": "Audit d'étape 2 — mise en œuvre",
         "objet": "L'auditeur vérifie que ce qui est écrit est fait : "
                  "preuves d'exécution, enregistrements, entretiens.",
         "ce_qui_fait_tomber": "Un écart entre la déclaration "
                               "d'applicabilité et la réalité — une mesure "
                               "retenue dont rien n'atteste la mise en "
                               "œuvre."},
        {"cle": "surveillance", "nom": "Audits de surveillance",
         "objet": "Le certificat vit : des audits périodiques vérifient que "
                  "le système tient.",
         "ce_qui_fait_tomber": "Un système monté pour l'audit et abandonné "
                               "ensuite — visible au premier audit de "
                               "surveillance."},
    ),
    "prealable": "Un cycle d'audit interne (art. 9.2) et une revue de "
                 "direction (art. 9.3) doivent avoir eu lieu AVANT l'étape 2 "
                 "— ce sont des exigences, et l'organisme ne peut pas les "
                 "produire le jour de l'audit.",
}


# ═══════════════════════════════════════════════════════════════════════════
#  LES PONTS — CE QUI SE RÉUTILISE, ET CE QUI NE SE SUBSTITUE PAS
# ═══════════════════════════════════════════════════════════════════════════

PONTS = (
    {"cle": "ia_act",
     "vers": "Règlement (UE) 2024/1689 (IA Act)",
     "articles_iso": ("6.1.4", "8.4"),
     "mesures_iso": ("A.5.2", "A.5.3", "A.5.4", "A.5.5"),
     "reutilise": "L'inventaire des systèmes, la cartographie des personnes "
                  "affectées et la méthode d'évaluation d'impact servent "
                  "aussi à l'analyse d'impact sur les droits fondamentaux "
                  "(AIDF, art. 27).",
     # L'ARTICLE EST NOMMÉ DANS LA PHRASE QU'ON CITE EN RÉUNION. « Ça ne
     # remplace pas » se conteste ; « ça ne remplace pas l'article 27 » se
     # vérifie.
     "ne_remplace_pas": "L'AIDF de l'article 27 est due par certains "
                        "DÉPLOYEURS de systèmes à haut risque et suit une "
                        "liste de points imposée par le règlement. Une "
                        "évaluation 42001, même excellente, ne la constitue "
                        "pas.",
     "nature": "obligation légale"},
    {"cle": "rgpd",
     "vers": "Règlement (UE) 2016/679 (RGPD)",
     "articles_iso": ("6.1.4", "8.4"),
     "mesures_iso": ("A.5.2", "A.5.4", "A.7.3", "A.7.5"),
     "reutilise": "La provenance et la préparation des données alimentent "
                  "directement le registre des traitements et l'analyse "
                  "d'impact relative à la protection des données (AIPD, "
                  "art. 35).",
     "ne_remplace_pas": "L'AIPD de l'article 35 porte sur les seules données "
                        "à caractère personnel, et sur les droits des "
                        "personnes "
                        "concernées. Un système d'IA sans données "
                        "personnelles n'en relève pas ; un traitement sans "
                        "IA en relève quand même.",
     "nature": "obligation légale"},
    {"cle": "nis2",
     "vers": "Directive (UE) 2022/2555 (NIS 2)",
     "articles_iso": ("8.1", "10.2"),
     "mesures_iso": ("A.8.4", "A.10.3"),
     "reutilise": "La communication des incidents (A.8.4) et la maîtrise "
                  "des fournisseurs (A.10.3) recouvrent en partie les "
                  "mesures b) et d) de l'article 21, §2.",
     "ne_remplace_pas": "NIS 2 impose des DÉLAIS — 24 h, 72 h, un mois — que "
                        "la norme ne fixe pas. Un processus 42001 conforme "
                        "peut manquer entièrement l'horloge de "
                        "l'article 23.",
     "nature": "obligation légale"},
    {"cle": "iso27001",
     "vers": "ISO/IEC 27001 (sécurité de l'information)",
     "articles_iso": tuple(n for n in sorted(SOUS_CHAPITRES)
                           if SOUS_CHAPITRES[n]["mutualisable"]),
     "mesures_iso": (),
     "reutilise": "La structure harmonisée est la même : revue de "
                  "direction, audit interne, non-conformités, informations "
                  "documentées se greffent sur le système existant.",
     "ne_remplace_pas": "27001 protège l'information ; 42001 gouverne l'IA. "
                        "Les objets diffèrent, et aucune des deux "
                        "certifications n'emporte l'autre.",
     "nature": "norme volontaire"},
)


# ═══════════════════════════════════════════════════════════════════════════
#  L'ÉVALUATION D'ENSEMBLE
# ═══════════════════════════════════════════════════════════════════════════

def evaluer(declaration=None):
    """Maturité, déclaration d'applicabilité, et l'état de préparation réel.

    L'ORDRE EST DÉLIBÉRÉ : la déclaration d'applicabilité passe AVANT le
    taux de maturité dans la restitution, parce que c'est elle qui décide
    si l'audit a lieu. Un organisme à 90 % de maturité avec une déclaration
    irrecevable n'est pas « presque prêt », il est arrêté.
    """
    d = declaration or {}
    if not isinstance(d, dict):
        return {"ok": False, "motif": "declaration_illisible"}
    nom = str(d.get("nom") or "").strip()
    if not nom:
        return {"ok": False, "motif": "nom_manquant"}

    soa = declaration_applicabilite(d.get("mesures"), d.get("mesures_propres"))
    if not soa.get("ok"):
        return soa
    mat = maturite(d.get("articles"))
    if not mat.get("ok"):
        return mat

    # ── L'ÉTAT DE PRÉPARATION, QUI N'EST PAS UNE MOYENNE ─────────────────
    if not soa["recevable"]:
        etape, dit = "etape_1_bloquee", (
            "La déclaration d'applicabilité ne passe pas l'étape 1. Aucun "
            "taux de maturité ne rattrape ce défaut : l'auditeur s'arrête "
            "au document.")
    elif mat["propres_a_l_ia"]["taux"] < 100:
        etape, dit = "etape_1_ouverte", (
            "La déclaration est recevable. Les articles propres à l'IA ne "
            "sont pas tous tenus (%d sur %d) — c'est là que se joue "
            "l'étape 2." % (mat["propres_a_l_ia"]["conformes"],
                            mat["propres_a_l_ia"]["total"]))
    elif soa["taux_mise_en_oeuvre"] is not None and \
            soa["taux_mise_en_oeuvre"] < 100:
        etape, dit = "etape_2_ouverte", (
            "Les articles sont tenus ; %d mesure(s) retenue(s) sur %d "
            "restent à mettre en œuvre." % (soa["mises_en_oeuvre"],
                                            soa["retenues"]))
    else:
        etape, dit = "pret", (
            "Articles tenus, déclaration recevable, mesures retenues mises "
            "en œuvre. Reste à avoir réellement conduit un audit interne et "
            "une revue de direction avant l'étape 2.")

    return {
        "ok": True,
        "nom": nom,
        "applicabilite": soa,
        "maturite": mat,
        "certification": CERTIFICATION,
        "etape": etape,
        "dit": dit,
        "ponts": PONTS,
        "source": SOURCE,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  LA GARDE — CE QUE CE MODULE REFUSE DE LAISSER PASSER
# ═══════════════════════════════════════════════════════════════════════════

def _verifier():
    fautes = []

    # ── LA STRUCTURE DE LA NORME ─────────────────────────────────────────
    numeros = [n for n, _t, _s in CHAPITRES]
    if numeros != ["4", "5", "6", "7", "8", "9", "10"]:
        fautes.append("les chapitres ne sont pas 4 à 10 : %s" % numeros)
    # LE COMPTE PAR CHAPITRE, ET NON UN TOTAL — un total nomme un nombre,
    # un compte par chapitre nomme LEQUEL a maigri.
    attendu = {"4": 4, "5": 3, "6": 6, "7": 7, "8": 4, "9": 6, "10": 2}
    for num, _t, sous in CHAPITRES:
        if len(sous) != attendu[num]:
            fautes.append("le chapitre %s compte %d sous-articles au lieu de "
                          "%d" % (num, len(sous), attendu[num]))
    if len(SOUS_CHAPITRES) != sum(attendu.values()):
        fautes.append("deux sous-articles portent le même numéro : %d "
                      "déclarés pour %d attendus"
                      % (len(SOUS_CHAPITRES), sum(attendu.values())))

    # ── LA PROFONDEUR DE DÉCOUPE, LÀ OÙ LA NORME DÉCOUPE, ET NULLE PART
    #    AILLEURS ────────────────────────────────────────────────────────
    #
    # CE QUE CETTE RÈGLE ATTRAPE, ET QU'UN TOTAL N'ATTRAPE PAS : la norme
    # subdivise 6.1, 7.5, 9.2 et 9.3, et seulement ceux-là. Une table qui
    # garderait « 6.1 » ET ses quatre enfants compterait cinq articles là où
    # il y en a quatre ; une table qui inventerait « 8.4.1 » sans frère
    # créerait un article qui n'existe pas. Les deux passent un total ajusté.
    profonds = {}
    for n in SOUS_CHAPITRES:
        bouts = n.split(".")
        if len(bouts) == 3:
            profonds.setdefault(".".join(bouts[:2]), []).append(n)
        elif len(bouts) != 2:
            fautes.append("le sous-article « %s » n'a ni deux ni trois "
                          "niveaux" % n)
    if sorted(profonds) != ["6.1", "7.5", "9.2", "9.3"]:
        fautes.append("les articles subdivisés ne sont pas 6.1, 7.5, 9.2 et "
                      "9.3 : %s" % sorted(profonds))
    for parent, enfants in profonds.items():
        if parent in SOUS_CHAPITRES:
            fautes.append("l'article « %s » est déclaré EN PLUS de ses %d "
                          "enfants : il serait compté deux fois"
                          % (parent, len(enfants)))
        if len(enfants) < 2:
            fautes.append("l'article « %s » n'a qu'un enfant (%s) : un "
                          "niveau de découpe inventé" % (parent, enfants))
    for n, v in SOUS_CHAPITRES.items():
        if not n.startswith(v["chapitre"] + "."):
            fautes.append("le sous-article « %s » est rangé sous le "
                          "chapitre %s" % (n, v["chapitre"]))
        if not str(v.get("dit") or "").strip():
            fautes.append("le sous-article « %s » ne dit pas ce qu'il "
                          "demande" % n)

    # ── L'ANNEXE A ───────────────────────────────────────────────────────
    if len(ANNEXE_A) != 9:
        fautes.append("l'annexe A ne compte pas 9 objectifs de mesures "
                      "(A.2 à A.10) : %d" % len(ANNEXE_A))
    if len(MESURES) != 38:
        fautes.append("l'annexe A ne compte pas 38 mesures : %d"
                      % len(MESURES))
    for num, m in MESURES.items():
        if not num.startswith(m["objectif"] + "."):
            fautes.append("la mesure « %s » est rangée sous l'objectif %s"
                          % (num, m["objectif"]))
        if not str(m.get("titre") or "").strip():
            fautes.append("la mesure « %s » n'a pas de titre" % num)

    # ── LE DROIT D'AUTEUR, TENU DANS LA TABLE ELLE-MÊME ──────────────────
    #
    # CE QUE CETTE RÈGLE ATTRAPE, ET QU'AUCUNE RELECTURE NE GARANTIT : la
    # table des mesures ne porte QUE des numéros et des titres. Si un jour
    # quelqu'un ajoutait un champ contenant le texte normatif — pour
    # « enrichir » la restitution —, le module deviendrait une reproduction
    # non autorisée. Les clés autorisées sont donc énumérées, et toute clé
    # nouvelle fait tomber la garde.
    permises = {"objectif", "objectif_titre", "objectif_dit", "titre"}
    for num, m in MESURES.items():
        en_trop = set(m) - permises
        if en_trop:
            fautes.append("la mesure « %s » porte un champ non prévu (%s) : "
                          "la table ne doit contenir que des numéros et des "
                          "titres, jamais le texte normatif"
                          % (num, ", ".join(sorted(en_trop))))
    if SOURCE.get("reproduction") is not False:
        fautes.append("la source ne déclare plus que la reproduction est "
                      "interdite")
    if "DROIT D'AUTEUR" not in SOURCE.get("licence", "").upper():
        fautes.append("la licence de la source ne nomme plus le droit "
                      "d'auteur")
    if not SOURCE.get("achat"):
        fautes.append("la source ne dit plus que la norme doit être achetée")

    # ── L'ORDRE DES MESURES, QUI DOIT ÊTRE NUMÉRIQUE ET NON ALPHABÉTIQUE ─
    #
    # A.6.2.10 n'existe pas aujourd'hui, mais A.10 existe : trié comme du
    # texte, « A.10 » passe avant « A.2 ». La restitution afficherait alors
    # les relations avec les tiers entre les politiques et l'organisation.
    tries = sorted(MESURES, key=_ordre)
    if tries[0] != "A.2.2" or tries[-1] != "A.10.4":
        fautes.append("l'ordre des mesures n'est pas numérique : de %s à %s"
                      % (tries[0], tries[-1]))

    # ── LES ARTICLES PROPRES À L'IA ──────────────────────────────────────
    #
    # SI CETTE LISTE SE VIDAIT, le second taux — le seul utile à un
    # organisme déjà certifié ailleurs — vaudrait 100 % sans rien mesurer.
    if not PROPRES_A_L_IA:
        fautes.append("aucun article n'est déclaré propre à l'IA : le taux "
                      "d'effort réel ne mesurerait plus rien")
    for n in ("5.2", "6.1.2", "6.1.3", "6.1.4", "8.2", "8.3", "8.4"):
        if n not in PROPRES_A_L_IA:
            fautes.append("l'article « %s » devrait être propre à l'IA" % n)
    for n in ("9.2.1", "9.3.1", "10.2", "7.5.3"):
        if n in PROPRES_A_L_IA:
            fautes.append("l'article « %s » est mutualisable avec un système "
                          "de management existant" % n)

    # ── LA DÉCLARATION D'APPLICABILITÉ REFUSE CE QU'ELLE DOIT REFUSER ────
    vide = declaration_applicabilite({})
    if vide["recevable"]:
        fautes.append("une déclaration d'applicabilité entièrement vide est "
                      "jugée recevable")
    if len(vide["non_decidees"]) != len(MESURES):
        fautes.append("une déclaration vide ne compte pas toutes les mesures "
                      "comme non décidées")
    sans_motif = declaration_applicabilite(
        {n: {"decision": "ecartee"} for n in MESURES})
    if sans_motif["recevable"]:
        fautes.append("une déclaration où tout est écarté SANS justification "
                      "est jugée recevable — l'art. 6.1.3 f) exige la "
                      "justification de l'exclusion comme de l'inclusion")
    motivee = declaration_applicabilite(
        {n: {"decision": "ecartee", "justification": "hors périmètre"}
         for n in MESURES})
    if not motivee["recevable"]:
        fautes.append("une déclaration où tout est écarté AVEC justification "
                      "est jugée irrecevable — écarter est un droit")
    if motivee["taux_mise_en_oeuvre"] is not None:
        fautes.append("un taux de mise en œuvre est rendu alors qu'aucune "
                      "mesure n'est retenue")

    # ── LES ARTICLES NE S'ÉCARTENT PAS ───────────────────────────────────
    m = maturite({"9.2.1": "sans_objet"})
    if "9.2.1" not in m["refus_sans_objet"]:
        fautes.append("un article déclaré « sans objet » n'est pas refusé — "
                      "les exigences de 4 à 10 ne s'écartent pas")
    if [l for c in m["chapitres"] for l in c["lignes"]
            if l["numero"] == "9.2.1"][0]["etat"] != "non_renseigne":
        fautes.append("un article refusé en « sans objet » n'est pas ramené "
                      "à « non renseigné »")

    # ── LES PONTS ────────────────────────────────────────────────────────
    for p in PONTS:
        if not p.get("ne_remplace_pas"):
            fautes.append("le pont vers « %s » ne dit pas ce qu'il ne "
                          "remplace pas" % p["cle"])
        for n in p["articles_iso"]:
            if n not in SOUS_CHAPITRES:
                fautes.append("le pont « %s » cite un article inconnu : %s"
                              % (p["cle"], n))
        for n in p["mesures_iso"]:
            if n not in MESURES:
                fautes.append("le pont « %s » cite une mesure inconnue : %s"
                              % (p["cle"], n))
    # LES TROIS ÉVALUATIONS D'IMPACT SONT NOMMÉES COMME DISTINCTES.
    for cle in ("ia_act", "rgpd"):
        p = [x for x in PONTS if x["cle"] == cle]
        if not p:
            fautes.append("le pont vers « %s » a disparu" % cle)
        elif "8.4" not in p[0]["articles_iso"]:
            fautes.append("le pont vers « %s » ne passe plus par "
                          "l'article 8.4" % cle)

    # ── LES ÉTAPES DE CERTIFICATION ──────────────────────────────────────
    if len(CERTIFICATION["etapes"]) != 3:
        fautes.append("le cycle de certification n'a pas trois temps")
    for e in CERTIFICATION["etapes"]:
        if not e.get("ce_qui_fait_tomber"):
            fautes.append("l'étape « %s » ne dit pas ce qui la fait échouer"
                          % e["cle"])
    if not SOURCE.get("certifiable"):
        fautes.append("la source ne déclare plus la norme certifiable — "
                      "c'est ce qui la distingue des trois autres cadres")

    if fautes:
        raise RuntimeError("iso42001 — table incohérente : "
                           + " ; ".join(fautes))
    return fautes


_FAUTES = _verifier()
