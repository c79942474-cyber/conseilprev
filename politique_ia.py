# -*- coding: utf-8 -*-
"""La politique de gouvernance de l'IA : celle de CONSEILPREV, et un modèle vierge.

DEUX DOCUMENTS, UNE SEULE SOURCE. Le premier est la politique de CONSEILPREV,
remplie de ses données réelles. Le second est le même document vidé, que le
cabinet remet à un client pour qu'il écrive la sienne. Les tenir dans deux
fichiers aurait garanti qu'ils divergent : on corrige une section d'un côté,
on oublie l'autre, et le modèle remis au client finit par ne plus ressembler à
ce que le cabinet applique à lui-même.

CE QUI CHANGE ENTRE LES DEUX, ET RIEN D'AUTRE : les valeurs (nom, rôles,
outils, dates) et le cadre juridique. Le corps du texte est identique, et une
règle le mesure.

── TROIS ARBITRAGES, ÉCRITS ICI PARCE QU'ILS NE SE DEVINENT PAS ─────────────

1. LE GABARIT D'ORIGINE ÉTAIT QUÉBÉCOIS. Il citait la Loi 25, la Commission
   d'accès à l'information et l'article 12.1. CONSEILPREV est une SARL de
   droit français : lui appliquer la Loi 25 aurait produit une politique qui
   se réclame d'un texte qui ne la régit pas — la faute exacte qu'une
   politique de conformité est censée empêcher. La version CONSEILPREV renvoie
   donc au RGPD, à la CNIL et au règlement sur l'IA. LE MODÈLE VIERGE, LUI,
   NE TRANCHE PAS : son cadre juridique est un champ à remplir, avec les deux
   jeux de références côte à côte, parce que le cabinet ne sait pas d'avance
   où son client est établi.

2. CONSEILPREV EST UNE TRÈS PETITE STRUCTURE, ET LA POLITIQUE LE DIT. Le
   gabarit répartit cinq rôles sur cinq personnes. Ici ils se cumulent sur le
   gérant. Écrire cinq noms différents aurait décrit une séparation des
   fonctions qui n'existe pas — et une politique qui décrit une organisation
   imaginaire ne protège personne. Le cumul est déclaré, avec ce qu'il coûte :
   personne ne contrôle celui qui décide, et le contrôle vient donc de
   l'extérieur (client, expert-comptable, auditeur).

3. L'INVENTAIRE NOMME AUSSI CE QUI N'EST PAS DE L'IA. Sur-déclarer est une
   faute au même titre que sous-déclarer : une politique qui rangerait les
   moteurs de calcul du site parmi les systèmes d'IA ferait porter à des
   formules déterministes des obligations de transparence et de surveillance
   qui ne les visent pas, et diluerait l'attention sur celui qui, lui, génère
   vraiment du texte. Chaque ligne de l'inventaire porte donc `ia` vrai ou
   faux, et le motif.
"""
import datetime as _dt

VERSION = "2026-09-a"

#: Durée maximale entre deux révisions, en mois. Le gabarit dit « maximum 12 » ;
#: on ne l'assouplit pas, et la date de prochaine révision en est DÉDUITE — une
#: date recopiée à la main finit par dire douze mois quand il s'en est écoulé
#: dix-huit.
REVISION_MOIS = 12


# ── LES DONNÉES DE CONSEILPREV ─────────────────────────────────────────────
# LE SIRET N'Y EST PAS, ET C'EST DÉLIBÉRÉ. Deux valeurs circulent dans la base
# documentaire du cabinet — l'une sur les états financiers, l'autre sur une
# fiche d'identité qui se déclare elle-même « à compléter » — et elles ne
# concordent pas. Une politique de gouvernance n'a besoin d'aucun SIRET pour
# être valable ; y porter le mauvais des deux aurait introduit une erreur
# gratuite dans un document signé. Le SIREN, lui, est certain.
ORGANISME = {
    "nom": "CONSEILPREV",
    "forme": "SARL",
    "capital": "8 000 €",
    "siren": "494 530 157",
    "tva": "FR 24 494 530 157",
    "adresse": "19 rue Auguste Chabrières, 75015 Paris",
    "representant": "Christophe Cerf",
    "qualite": "Gérant",
    "courriel": "christophe.cerf@i-aes.com",
    "telephone": "+33 6 60 69 21 45",
    "activite": "Conseil en gouvernance de l'intelligence artificielle et "
                "cybersécurité industrielle",
}


# ── LE CADRE JURIDIQUE, SELON OÙ L'ORGANISME EST ÉTABLI ────────────────────
CADRES = {
    "ue": {
        "nom": "France / Union européenne",
        "protection": "le règlement (UE) 2016/679 (RGPD) et la loi "
                      "« Informatique et Libertés » du 6 janvier 1978 modifiée",
        "autorite": "la Commission nationale de l'informatique et des libertés "
                    "(CNIL)",
        "decision_auto": "l'article 22 du RGPD",
        "analyse_impact": "une analyse d'impact relative à la protection des "
                          "données (AIPD, article 35 du RGPD)",
        "sous_traitant": "l'article 28 du RGPD, qui impose un contrat écrit "
                         "avec le sous-traitant",
        "transfert": "un transfert hors Union européenne suppose un mécanisme "
                     "du chapitre V du RGPD (décision d'adéquation, clauses "
                     "contractuelles types) et une analyse des risques",
        "violation": "une violation de données se notifie à la CNIL dans les "
                     "72 heures lorsqu'elle présente un risque, et aux "
                     "personnes concernées en cas de risque élevé "
                     "(articles 33 et 34 du RGPD)",
        "ia": "le règlement (UE) 2024/1689 sur l'intelligence artificielle",
    },
    "qc": {
        "nom": "Québec",
        "protection": "la Loi sur la protection des renseignements personnels "
                      "dans le secteur privé, telle que modifiée par la Loi 25",
        "autorite": "la Commission d'accès à l'information (CAI)",
        "decision_auto": "l'article 12.1 de cette loi",
        "analyse_impact": "une évaluation des facteurs relatifs à la vie "
                          "privée (EFVP)",
        "sous_traitant": "l'obligation d'un écrit prévoyant les mesures de "
                         "protection applicables",
        "transfert": "une communication de renseignements personnels à "
                     "l'extérieur du Québec exige une évaluation préalable",
        "violation": "un incident de confidentialité présentant un risque de "
                     "préjudice sérieux se déclare à la CAI et aux personnes "
                     "concernées",
        "ia": "le cas échéant, le règlement européen sur l'IA pour les "
              "activités visant le marché de l'Union",
    },
}


# ── L'INVENTAIRE RÉEL DES SYSTÈMES ─────────────────────────────────────────
# RELEVÉ DANS LE CODE EN SERVICE, PAS IMAGINÉ. Chaque ligne dit si le système
# repose sur un modèle génératif — et, quand ce n'est pas le cas, POURQUOI. La
# colonne existe précisément pour que l'inventaire reste lisible quand il
# grandira : sans elle, tout ce qui touche au mot « IA » y entre.
SYSTEMES = [
    {"nom": "Assistant conversationnel du site",
     "fournisseur": "Anthropic (API Claude)",
     "usage": "Répondre aux questions des visiteurs sur la conformité IA, "
              "appuyé sur la base de connaissance du cabinet.",
     "donnees": "Question posée par le visiteur ; extraits de la base de "
                "connaissance. Aucune saisie de renseignement personnel n'est "
                "demandée.",
     "ia": True,
     "risque": "moyen",
     "motif": "Génère du texte librement ; une réponse erronée sur une "
              "obligation réglementaire peut être reprise telle quelle par un "
              "visiteur.",
     "mesure": "Réponses ancrées sur la base documentaire ; mention visible "
               "que l'interlocuteur est un système d'IA ; aucun engagement "
               "contractuel ne se prend par ce canal."},
    {"nom": "Recherche dans la base de connaissance (vectorisation)",
     "fournisseur": "Service d'embeddings du fournisseur de modèles",
     "usage": "Retrouver les passages pertinents d'un document déposé pour "
              "les servir à l'assistant.",
     "donnees": "Texte des documents déposés par le cabinet.",
     "ia": True,
     "risque": "faible",
     "motif": "Transforme du texte en vecteurs ; ne génère rien, mais "
              "détermine ce que l'assistant voit — donc ce qu'il peut dire.",
     "mesure": "Documents déposés par le cabinet seulement ; le passage "
               "retenu est rendu avec la réponse pour être vérifié."},
    {"nom": "Rédaction assistée de livrables",
     "fournisseur": "Anthropic (API Claude)",
     "usage": "Produire des BROUILLONS de notes et de rapports, relus avant "
              "remise.",
     "donnees": "Éléments du dossier client fournis dans la demande.",
     "ia": True,
     "risque": "élevé",
     "motif": "Le modèle génère librement un texte destiné au client. Une "
              "référence inventée dans une note de conformité engage le "
              "cabinet, et rien dans la forme du texte ne la distingue d'une "
              "vraie.",
     "mesure": "Vérification en source primaire avant remise (section 8.4) ; "
               "marquage lisible par machine apposé sur le fichier ; mention "
               "visible portée sur le document."},
    # ── CE QUI N'EST PAS DE L'IA, ET QUI EST NOMMÉ POUR QUE PERSONNE NE
    #    L'Y RANGE PAR PRUDENCE MAL PLACÉE ─────────────────────────────────
    {"nom": "Moteurs de calcul (empreinte, FinOps, faisabilité, enveloppe)",
     "fournisseur": "CONSEILPREV — code interne",
     "usage": "Calculer à partir de référentiels versionnés et sourcés.",
     "donnees": "Valeurs saisies par l'utilisateur ; facteurs publiés.",
     "ia": False,
     "risque": "faible",
     "motif": "Formules déterministes : la même entrée rend toujours la même "
              "sortie, et chaque résultat porte son équation et sa source.",
     "mesure": "Équation et source affichées avec chaque valeur ; les "
               "documents produits déclarent « calcul déterministe, sans "
               "génération par IA »."},
    {"nom": "Relevé des pièces de marchés publics",
     "fournisseur": "CONSEILPREV — code interne",
     "usage": "Repérer dans un dossier de consultation l'acheteur, l'objet, "
              "les délais et les critères, avec la citation.",
     "donnees": "Texte des pièces déposées par le cabinet pour ses propres "
                "candidatures.",
     "ia": False,
     "risque": "faible",
     "motif": "Motifs d'expression régulière. Aucun modèle n'intervient ; ce "
              "qui n'est pas trouvé est déclaré « non relevé », jamais deviné.",
     "mesure": "Chaque valeur est rendue avec le passage exact d'où elle "
               "vient, pour être vérifiée sur la pièce."},
    {"nom": "Veille réglementaire",
     "fournisseur": "CONSEILPREV — code interne",
     "usage": "Collecter les publications officielles et les présenter.",
     "donnees": "Flux publics.",
     "ia": False,
     "risque": "faible",
     "motif": "Collecte et filtrage par mots-clés déclarés. Aucun résumé "
              "n'est généré : les titres sont ceux de la source.",
     "mesure": "Lien vers la source primaire sur chaque élément."},
]


def _prochaine_revision(entree, mois=REVISION_MOIS):
    """La date de révision, DÉDUITE de l'entrée en vigueur.

    Elle n'est pas saisie : une date recopiée à la main finit par annoncer
    douze mois quand il s'en est écoulé dix-huit, et c'est précisément le
    genre d'écart qu'un auditeur relève en premier.
    """
    a, m = entree.year + (entree.month - 1 + mois) // 12, \
        (entree.month - 1 + mois) % 12 + 1
    j = min(entree.day, [31, 29 if a % 4 == 0 and (a % 100 or a % 400 == 0)
                         else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return _dt.date(a, m, j)


#: L'ENCADRÉ DE FIN, REPRIS MOT POUR MOT. Il vient du cabinet, pas de ce
#: module : le recomposer, même mieux tourné, ferait dire au document autre
#: chose que ce que son auteur a voulu. Une règle mesure qu'il est intact.
ENCADRE_UE = (
    "Si vous vendez à des clients européens, deux dates ont changé cet été. "
    "Le règlement omnibus numérique de l'Union européenne est entré en vigueur "
    "le 27 juillet 2026 et reporte au 2 décembre 2027 l'essentiel des "
    "obligations sur les systèmes à haut risque, qui devaient s'appliquer le "
    "2 août 2026. Par contre, les obligations de transparence, comme divulguer "
    "qu'une personne interagit avec une IA et étiqueter un contenu généré, "
    "s'appliquent depuis le 2 août 2026. L'obligation de literacy en IA a été "
    "assouplie : elle demande maintenant de prendre des mesures pour soutenir "
    "la compétence de vos équipes, sans garantir un niveau précis."
)


# ═══════════════════════════════════════════════════════════════════════════
#  LE CORPS DE LA POLITIQUE
# ═══════════════════════════════════════════════════════════════════════════
# UN SEUL TEXTE POUR LES DEUX DOCUMENTS. Ce qui varie passe par `v`, le
# vocabulaire : le nom de l'organisme, les rôles, les outils. Dans la version
# vierge, ces mêmes entrées valent « [à compléter] ». Écrire deux fois le
# texte aurait garanti la divergence — et c'est le modèle remis au client qui
# aurait vieilli en silence, puisque personne ne le relit.

def _vocabulaire(variante, entree, cadre):
    """Les valeurs qui changent d'un document à l'autre. Rien d'autre."""
    c = CADRES[cadre]
    if variante == "conseilprev":
        o = ORGANISME
        return {
            "org": o["nom"],
            "identite": "%s, %s au capital de %s, SIREN %s, %s" % (
                o["nom"], o["forme"], o["capital"], o["siren"], o["adresse"]),
            "responsable": "%s, %s" % (o["representant"], o["qualite"]),
            "inventaire_resp": "%s, %s" % (o["representant"], o["qualite"]),
            "dpo": "%s, %s" % (o["representant"], o["qualite"]),
            "instance": "l'associé unique, en assemblée annuelle",
            "contact": o["courriel"],
            "entree": entree.strftime("%d/%m/%Y"),
            "revision": _prochaine_revision(entree).strftime("%d/%m/%Y"),
            "annee": str(entree.year),
            "cadence_inventaire": "trimestriellement",
            "part_formee": "100 %",
            "date_formation": "31/12/%s" % entree.year,
            "retention_doc": "cinq ans",
            "cadre": c,
            "vierge": False,
        }
    return {
        "org": "[Nom de l'entreprise]",
        "identite": "[Nom de l'entreprise], [forme juridique], "
                    "[numéro d'identification], [adresse]",
        "responsable": "[nom, titre]",
        "inventaire_resp": "[nom, titre]",
        "dpo": "[nom, titre — responsable de la protection des données]",
        "instance": "[conseil d'administration ou comité de gestion]",
        "contact": "[adresse courriel]",
        "entree": "[date]",
        "revision": "[date, au plus tard 12 mois après l'entrée en vigueur]",
        "annee": "[année]",
        "cadence_inventaire": "[trimestriellement]",
        "part_formee": "[100 %]",
        "date_formation": "[date]",
        "retention_doc": "[durée]",
        "cadre": c,
        "vierge": True,
    }


def _tableau_systemes(v):
    """L'inventaire. Rempli pour le cabinet, à trois lignes vides pour le modèle."""
    lignes = ["| Système | Fournisseur | Usage | Modèle génératif | Risque |",
              "|---|---|---|---|---|"]
    if v["vierge"]:
        for _ in range(3):
            lignes.append("| [outil] | [fournisseur] | [usage prévu] | "
                          "[oui / non] | [faible / moyen / élevé] |")
        return "\n".join(lignes)
    for s in SYSTEMES:
        lignes.append("| %s | %s | %s | %s | %s |" % (
            s["nom"], s["fournisseur"], s["usage"],
            "Oui" if s["ia"] else "Non", s["risque"]))
    return "\n".join(lignes)


def _detail_systemes(v):
    """Ce que le tableau ne peut pas tenir : pourquoi ce risque, quelle mesure.

    UN TABLEAU À CINQ COLONNES NE PORTE PAS UN RAISONNEMENT. « moyen » sans le
    motif ne se conteste pas, donc ne se révise pas : au bout d'un an personne
    ne sait plus pourquoi le niveau avait été mis là.
    """
    if v["vierge"]:
        return ("Pour chaque système inscrit, consignez ici le motif du niveau "
                "de risque retenu et les mesures qui l'encadrent. Un niveau "
                "sans motif ne se conteste pas, donc ne se révise jamais.")
    out = []
    for s in SYSTEMES:
        out.append("**%s** — %s *Données traitées :* %s *Pourquoi ce niveau :* "
                   "%s *Mesures :* %s" % (
                       s["nom"],
                       "" if s["ia"] else "Ce système ne repose sur aucun "
                                          "modèle génératif. ",
                       s["donnees"], s["motif"], s["mesure"]))
    return "\n\n".join(out)


def _corps(v):
    """Les seize sections, dans l'ordre du gabarit."""
    c = v["cadre"]
    s = []
    a = s.append

    a("# Politique de gouvernance de l'intelligence artificielle")
    a("**Organisation :** %s  " % v["identite"])
    a("**Version :** 1.0 — **Entrée en vigueur :** %s — "
      "**Approuvée par :** %s — **Prochaine révision :** %s "
      "(au plus tard %d mois)" % (v["entree"], v["responsable"],
                                  v["revision"], REVISION_MOIS))
    a("**Cadre juridique applicable :** %s." % c["nom"]
      + ("" if not v["vierge"] else
         " *Ce document propose les références du droit français et européen ; "
         "si votre organisation est établie au Québec, remplacez-les par "
         "celles de la Loi 25 — la correspondance est donnée en annexe.*"))

    a("## 1. Objet")
    a("Cette politique établit comment %s encadre l'acquisition, "
      "l'utilisation, la surveillance et le retrait des systèmes "
      "d'intelligence artificielle. Elle vise à permettre l'usage de ces "
      "outils tout en protégeant les données personnelles, les informations "
      "confidentielles, la qualité du travail livré aux clients et les "
      "personnes touchées par les décisions prises." % v["org"])

    a("## 2. Portée")
    a("Cette politique s'applique à toute personne agissant pour %s — "
      "salariés, prestataires, stagiaires, mandataires sociaux — sans "
      "exception, direction comprise." % v["org"])
    a("Elle vise tout système qui génère du contenu, analyse de "
      "l'information, produit une recommandation ou exécute des tâches à "
      "partir d'un modèle d'intelligence artificielle, qu'il soit acheté, "
      "infonuagique, intégré dans un logiciel existant ou développé en "
      "interne : assistants conversationnels, fonctions d'IA intégrées dans "
      "un logiciel déjà utilisé, extensions de navigateur, outils de "
      "transcription et de résumé de réunion, traducteurs en ligne, agents "
      "autonomes.")
    a("Si vous n'êtes pas certain qu'un outil est visé, présumez qu'il l'est "
      "et posez la question au responsable désigné à la section 4.")

    a("## 3. Définitions")
    a("- **Système d'IA** — logiciel qui, à partir de données, produit du "
      "contenu, des prédictions, des recommandations ou des décisions.\n"
      "- **IA générative** — système qui produit du texte, des images, du "
      "code, de l'audio ou de la vidéo.\n"
      "- **Agent** — système d'IA qui exécute des actions de façon autonome "
      "dans un autre logiciel ou service.\n"
      "- **Décision automatisée** — décision concernant une personne, prise à "
      "partir d'un traitement automatisé, sans intervention humaine.\n"
      "- **Hallucination** — résultat inventé par un système d'IA, présenté "
      "avec la même assurance qu'un résultat exact.")

    a("## 4. Rôles et responsabilités")
    if v["vierge"]:
        a("- %s est responsable de la gouvernance de l'IA : approuve cette "
          "politique, arbitre les exceptions, rend compte à %s au moins une "
          "fois par an.\n"
          "- %s tient l'inventaire, approuve toute nouvelle utilisation et "
          "conserve les évaluations de risque.\n"
          "- %s est consulté avant tout usage impliquant des données "
          "personnelles.\n"
          "- Chaque responsable d'équipe s'assure que les membres de son "
          "équipe ont lu cette politique et l'ont attestée.\n"
          "- Chaque personne demeure responsable du travail qu'elle produit, "
          "quel que soit l'outil utilisé."
          % (v["responsable"], v["instance"], v["inventaire_resp"], v["dpo"]))
        a("*Si votre structure est petite, ces rôles peuvent se cumuler sur "
          "une même personne. Dans ce cas, écrivez-le ici plutôt que "
          "d'inscrire des noms différents : une politique qui décrit une "
          "séparation des fonctions qui n'existe pas ne protège personne, et "
          "c'est le premier écart qu'un auditeur relève.*")
    else:
        # LE CUMUL EST DÉCLARÉ, ET CE QU'IL COÛTE AVEC LUI. C'est le point où
        # une politique de petite structure ment le plus souvent.
        a("%s exerce l'ensemble des rôles prévus par cette politique : "
          "responsable de la gouvernance de l'IA, tenue de l'inventaire, "
          "approbation des nouveaux usages, protection des données "
          "personnelles." % v["responsable"])
        a("**Ce cumul est assumé et ses limites sont déclarées.** %s est une "
          "structure à effectif très réduit : la séparation des fonctions n'y "
          "est pas praticable, et prétendre le contraire serait faux. En "
          "conséquence, personne en interne ne contrôle celui qui décide. Le "
          "contre-pouvoir est donc externe et nommé : la relecture "
          "contradictoire par le client sur les livrables qui l'engagent, "
          "l'expert-comptable sur les données financières, et tout auditeur "
          "mandaté par un client. Le jour où un premier salarié est recruté, "
          "cette section est la première à réviser." % v["org"])
        a("Toute personne agissant pour %s demeure responsable du travail "
          "qu'elle produit, quel que soit l'outil utilisé." % v["org"])

    a("## 5. Objectifs")
    a("Objectifs fixés pour %s :" % v["annee"])
    a("- Maintenir un inventaire à jour de tous les systèmes d'IA utilisés, "
      "révisé au moins %s\n"
      "- Former %s des personnes concernées avant le %s\n"
      "- Évaluer le risque de tout nouveau système avant sa mise en service, "
      "sans exception\n"
      "- Consigner et traiter 100 %% des incidents liés à l'IA signalés"
      % (v["cadence_inventaire"], v["part_formee"], v["date_formation"]))
    a("Ces objectifs sont revus chaque année en même temps que la politique.")

    a("## 6. Inventaire des systèmes d'IA")
    a("%s tient un inventaire écrit de tous les systèmes en service. Aucun "
      "système ne peut être mis en service sans y être inscrit. L'inventaire "
      "est révisé au moins %s." % (v["org"], v["cadence_inventaire"]))
    a("**L'inventaire nomme aussi ce qui n'est PAS de l'IA.** Ranger un "
      "moteur de calcul déterministe parmi les systèmes d'IA lui ferait "
      "porter des obligations qui ne le visent pas, et diluerait l'attention "
      "sur ceux qui génèrent réellement du contenu. La colonne « modèle "
      "génératif » tranche, et le motif est consigné à la section 7.")
    a(_tableau_systemes(v))

    a("## 7. Évaluation des risques et des répercussions")
    a("Avant la mise en service d'un système, %s évalue et consigne : la "
      "nature des données traitées, les conséquences possibles d'un résultat "
      "erroné, les personnes qui pourraient être touchées, le risque de "
      "traitement discriminatoire et le degré d'autonomie accordé au système. "
      "Chaque système reçoit un niveau : faible, moyen ou élevé."
      % v["inventaire_resp"])
    a("Un système est **automatiquement classé à risque interne élevé** s'il "
      "touche l'embauche, la rémunération, la discipline, l'accès à un "
      "service, l'octroi de crédit, la santé ou la sécurité d'une personne. "
      "Cette classification est interne : elle ne détermine pas la "
      "qualification juridique du système au sens de %s." % c["ia"])
    a("Un système à risque interne élevé exige une approbation écrite de %s "
      "avant sa mise en service. S'il traite des données personnelles, %s est "
      "réalisée avant la mise en service lorsque la loi applicable ou les "
      "règles internes l'exigent. L'évaluation est refaite si l'usage change, "
      "et au moins une fois par an pour les systèmes à risque élevé."
      % (v["responsable"], c["analyse_impact"]))
    a(_detail_systemes(v))

    a("## 8. Règles d'usage acceptable")
    a("Cette section est remise à chaque personne concernée et fait l'objet "
      "de l'attestation prévue à la section 16.")

    a("### 8.1 Outils autorisés")
    if v["vierge"]:
        a("Seuls les outils suivants sont approuvés pour un usage "
          "professionnel, et uniquement depuis le compte d'entreprise "
          "fourni :")
        a("- [Outil 1 — compte d'entreprise]\n- [Outil 2]\n- [Outil 3]")
    else:
        a("Seuls les outils inscrits à l'inventaire de la section 6 sont "
          "approuvés pour un usage professionnel, et uniquement depuis le "
          "compte d'entreprise.")
    a("**L'utilisation d'un compte personnel gratuit pour du travail de "
      "l'entreprise est interdite**, même s'il s'agit du même produit. Les "
      "protections contractuelles qui nous protègent sont attachées au compte "
      "d'entreprise, pas au logo affiché à l'écran.")
    a("Pour demander l'ajout d'un outil, écrivez à %s. N'installez rien avant "
      "d'avoir reçu une réponse." % v["contact"])

    a("### 8.2 Données : ce qui peut être saisi, et où")
    a("| Type d'information | Outil public, compte personnel | "
      "Outil approuvé, compte d'entreprise |\n|---|---|---|\n"
      "| Information déjà publique | Permis | Permis |\n"
      "| Document interne non sensible | Interdit | Permis |\n"
      "| Donnée personnelle (client, salarié, candidat) | Interdit | "
      "Permis seulement si autorisé par écrit par " + v["dpo"] + " et "
      "compatible avec nos obligations légales et contractuelles |\n"
      "| Secret d'affaires, code source, contrat client | Interdit | "
      "Permis seulement si autorisé par écrit par " + v["responsable"] + " |\n"
      "| Donnée de santé, financière ou judiciaire | Interdit | "
      "Interdit sans autorisation écrite de " + v["responsable"] + " |")
    a("**Une autorisation interne ne suffit pas à elle seule.** Plusieurs "
      "contrats clients interdisent de transmettre leur information à un "
      "tiers, y compris à un fournisseur d'IA, sans leur accord. Vérifiez le "
      "contrat avant de demander l'autorisation.")
    a("Dans le doute, posez-vous cette question avant de coller quoi que ce "
      "soit : cette information identifie-t-elle une personne, révèle-t-elle "
      "un avantage concurrentiel, appartient-elle à un client, ou "
      "pourrait-elle causer un préjudice si elle sortait ? Si oui, arrêtez et "
      "demandez.")

    a("### 8.3 Usages interdits")
    a("- Contourner une mesure de sécurité, un contrôle d'accès ou une règle "
      "de confidentialité de l'entreprise ou d'un client\n"
      "- Produire du contenu discriminatoire, harcelant, diffamatoire ou "
      "illégal\n"
      "- Générer du contenu qui imite une personne réelle, sa voix ou son "
      "image, sans son consentement écrit\n"
      "- Utiliser un outil d'IA pour prendre seul une décision qui touche "
      "l'emploi, l'embauche, la rémunération, la discipline ou l'accès à un "
      "service d'une personne\n"
      "- Téléverser un document client dans un outil non approuvé, y compris "
      "pour le traduire ou le résumer\n"
      "- Présenter un contenu généré par IA comme provenant d'une source "
      "vérifiée sans avoir fait la vérification décrite à la section 8.4")

    a("### 8.4 Vérification obligatoire avant utilisation")
    a("Cette règle vise le contenu produit par un outil d'IA à la demande "
      "d'une personne. Les actions exécutées par un agent approuvé selon la "
      "section 8.6 suivent les limites définies lors de son approbation.")
    a("**Un contenu produit par un outil d'IA est un brouillon. Il ne devient "
      "un livrable qu'après vérification humaine.**")
    a("Avant d'envoyer à un client, de publier, de déposer dans un dossier "
      "officiel, de transmettre à un tiers ou d'appuyer une décision "
      "importante sur un contenu produit avec l'aide de l'IA, vous devez :")
    a("1. Vérifier chaque fait, chiffre, citation, référence, article de loi "
      "ou nom cité **dans une source primaire**, pas dans l'outil qui l'a "
      "généré\n"
      "2. Confirmer que le contenu correspond réellement à la demande et au "
      "contexte du dossier\n"
      "3. Corriger ou retirer tout élément que vous ne pouvez pas confirmer")
    a("Un outil d'IA peut inventer une référence qui a toutes les apparences "
      "d'une vraie. Cette vérification n'est pas une suggestion.")

    a("### 8.5 Supervision humaine")
    a("Aucune décision produisant un effet juridique ou un effet important "
      "sur une personne ne peut être prise uniquement à partir d'un "
      "traitement automatisé. Une personne identifiée doit réviser la "
      "décision et l'assumer.")
    a("Quand un système d'IA est utilisé dans un processus qui touche une "
      "personne, %s doit être avisé avant le déploiement, pour évaluer les "
      "obligations d'information et de révision prévues par %s."
      % (v["dpo"], c["decision_auto"]))

    a("### 8.6 Agents et automatisation")
    a("Un agent qui exécute des actions de façon autonome — envoyer un "
      "courriel, modifier un fichier, créer un enregistrement, déclencher un "
      "paiement — doit être approuvé par %s avant sa mise en service."
      % v["responsable"])
    a("Chaque agent a un propriétaire nommé, une liste documentée des "
      "systèmes auxquels il accède, et une limite claire des actions qu'il "
      "peut exécuter sans validation humaine.")

    a("## 9. Cycle de vie des systèmes développés en interne")
    if v["vierge"]:
        a("*Cette section s'applique si votre organisation conçoit, entraîne, "
          "affine ou intègre ses propres systèmes d'IA. Si ce n'est pas le "
          "cas, écrivez-le ici plutôt que de supprimer la section : un "
          "auditeur doit pouvoir constater que la question a été posée.*")
    else:
        a("%s n'entraîne ni n'affine aucun modèle. Elle INTÈGRE des modèles "
          "de tiers dans ses outils, ce qui relève de la section 11. Cette "
          "section est conservée et reste sans objet tant que cette situation "
          "dure ; elle est réactivée au premier système conçu en interne."
          % v["org"])
    a("Pour chaque système développé, sont documentés : l'objectif visé et "
      "les usages exclus, les données d'entraînement et leur provenance, les "
      "tests effectués avant mise en service (exactitude, comportement sur "
      "une entrée inattendue, tentatives d'injection d'instructions), les "
      "personnes ayant approuvé la mise en production, et les critères de "
      "retrait. Cette documentation est conservée pendant toute la vie du "
      "système et %s après son retrait." % v["retention_doc"])

    a("## 10. Données")
    a("Les données utilisées pour alimenter ou entraîner un système d'IA "
      "doivent avoir une provenance connue et un droit d'utilisation vérifié.")
    a("Aucune donnée personnelle n'est utilisée pour entraîner un modèle sans "
      "base légale documentée et autorisation écrite de %s. La durée de "
      "conservation des données transmises à un fournisseur d'IA est connue "
      "et consignée dans l'inventaire." % v["dpo"])

    a("## 11. Fournisseurs et tiers")
    a("Avant de contracter avec un fournisseur d'IA, %s vérifie et conserve "
      "la preuve des éléments suivants : le contrat exclut-il l'utilisation "
      "de nos données pour entraîner les modèles du fournisseur ; où les "
      "données sont-elles hébergées et combien de temps sont-elles "
      "conservées ; quelles sont les obligations de notification en cas "
      "d'incident ; les mesures contractuelles, organisationnelles et "
      "techniques du fournisseur sont-elles compatibles avec les obligations "
      "qui nous incombent." % v["responsable"])
    a("Le recours à un fournisseur qui traite des données personnelles pour "
      "notre compte fait l'objet d'un écrit, comme l'exige %s. %s : ce point "
      "est validé par %s ou par un conseil juridique."
      % (c["sous_traitant"], c["transfert"].capitalize(), v["dpo"]))

    a("## 12. Transparence envers les personnes")
    a("Quand une personne pourrait raisonnablement croire qu'elle échange "
      "avec un humain alors qu'elle échange avec un système d'IA, elle en est "
      "informée clairement.")
    a("Quand une décision la concernant est fondée sur un traitement "
      "automatisé, elle en est informée, peut obtenir les principaux facteurs "
      "ayant mené à la décision, et peut demander une révision par une "
      "personne.")
    a("Le contenu généré par IA publié au nom de %s est vérifié selon la "
      "section 8.4 avant publication%s." % (
          v["org"],
          "" if v["vierge"] else ", et porte un marquage lisible par machine "
          "dans les propriétés du fichier ainsi qu'une mention visible sur le "
          "document. Les documents issus d'un calcul déterministe portent au "
          "contraire la mention « calcul déterministe, sans génération par "
          "IA » : un marquage apposé partout ne signale plus rien"))

    a("## 13. Compétence et formation")
    a("Chaque personne concernée suit une formation à l'usage de l'IA avant "
      "d'utiliser un outil approuvé, puis une mise à jour annuelle. La "
      "formation couvre la reconnaissance d'une donnée personnelle, les "
      "hallucinations, et la procédure de vérification de la section 8.4. La "
      "participation et la compréhension sont consignées.")

    a("## 14. Incidents liés à l'IA")
    a("Signalez immédiatement à %s toute situation où :" % v["contact"])
    a("- Une information confidentielle ou une donnée personnelle a été "
      "saisie dans un outil non approuvé\n"
      "- Un contenu généré par IA contenant une erreur a été transmis à un "
      "client ou publié\n"
      "- Un système d'IA a produit un résultat discriminatoire ou "
      "inapproprié\n"
      "- Un agent a exécuté une action non prévue")
    a("**Signaler rapidement n'entraîne aucune sanction. Ne pas signaler, "
      "oui.**")
    a("Chaque signalement est consigné au registre des incidents liés à l'IA "
      "avec la date, la description, les mesures prises et la correction "
      "apportée. Chaque incident touchant des données personnelles est évalué "
      "et consigné : %s." % c["violation"])

    a("## 15. Surveillance et amélioration")
    a("%s présente à %s, au moins une fois par an, un bilan couvrant l'état "
      "de l'inventaire, les incidents survenus et leur traitement, l'atteinte "
      "des objectifs de la section 5, les écarts constatés et les correctifs "
      "prévus avec un responsable et une échéance."
      % (v["responsable"], v["instance"]))
    a("Cette politique est révisée au moins une fois par an, ou plus tôt si "
      "un changement réglementaire, un incident ou l'arrivée d'un nouveau "
      "système le justifie.")
    a("Le non-respect de cette politique peut donner lieu à des mesures "
      "disciplinaires, selon la gravité et les conséquences pour "
      "l'organisation ou ses clients.")

    a("## 16. Attestation")
    a("J'ai lu et compris les règles d'usage acceptable de l'intelligence "
      "artificielle de %s. Je m'engage à les respecter et à signaler tout "
      "incident visé à la section 14." % v["org"])
    a("Nom : ______________________________")
    a("Signature : ________________________")
    a("Date : _____________________________")

    if v["vierge"]:
        a("## Annexe — correspondance des références juridiques")
        a("Ce modèle emploie les références du droit français et européen. "
          "Si votre organisation est établie au Québec, remplacez-les par la "
          "colonne de droite.")
        a("| Dans ce document | Équivalent au Québec |\n|---|---|\n"
          "| " + CADRES["ue"]["protection"] + " | "
          + CADRES["qc"]["protection"] + " |\n"
          "| " + CADRES["ue"]["autorite"] + " | "
          + CADRES["qc"]["autorite"] + " |\n"
          "| " + CADRES["ue"]["decision_auto"] + " | "
          + CADRES["qc"]["decision_auto"] + " |\n"
          "| " + CADRES["ue"]["analyse_impact"] + " | "
          + CADRES["qc"]["analyse_impact"] + " |")

    # ── L'ENCADRÉ DE FIN, EN DERNIER ET SUR LES DEUX DOCUMENTS ────────────
    # L'ENCADRÉ TIENT D'UN SEUL TENANT. Mesuré sur le PDF produit : sans ce
    # marquage il se coupait entre deux pages — trois lignes en bas de
    # l'avant-dernière, la fin en haut de la dernière. Un avertissement scindé
    # perd la moitié de sa force.
    a("---")
    a(":::ensemble")
    a("### À noter — calendrier européen")
    a(ENCADRE_UE)
    a(":::")
    return s


def politique(variante="conseilprev", entree=None, cadre=None):
    """Le document, en Markdown, avec les métadonnées d'export.

    `entree` est PASSÉE, jamais lue de l'horloge : deux appels le même jour
    doivent rendre le même document, et une règle qui dépendrait de `today()`
    changerait de verdict à minuit.
    """
    if variante not in ("conseilprev", "modele"):
        raise ValueError("variante inconnue : %r" % (variante,))
    entree = entree or _dt.date.today()
    cadre = cadre or "ue"
    v = _vocabulaire(variante, entree, cadre)
    label = ("Politique de gouvernance de l'IA — CONSEILPREV"
             if variante == "conseilprev"
             else "Politique de gouvernance de l'IA — modèle à compléter")
    return {
        "variante": variante,
        "markdown": "\n\n".join(_corps(v)),
        "label": label,
        "fichier": ("politique-gouvernance-ia-conseilprev"
                    if variante == "conseilprev"
                    else "politique-gouvernance-ia-modele"),
        # LE DOCUMENT N'EST PAS ÉCRIT PAR UN MODÈLE, ET SES PROPRIÉTÉS LE
        # DISENT. Apposer un marquage « produit avec l'assistance d'une IA »
        # sur la politique qui ORGANISE cet usage serait faux, et se
        # remarquerait.
        "meta": {"label": label, "ia": False,
                 "referentiel": "politique_ia " + VERSION,
                 "suffixe": "Gouvernance IA"},
    }


def _verifier():
    """Ce qui doit être vrai au chargement, sinon le module refuse de servir."""
    pb = []
    for cle in ("ue", "qc"):
        manques = [k for k in CADRES["ue"] if k not in CADRES[cle]]
        if manques:
            pb.append("le cadre %s ne porte pas %s" % (cle, ", ".join(manques)))
    for s in SYSTEMES:
        for k in ("nom", "fournisseur", "usage", "donnees", "ia", "risque",
                  "motif", "mesure"):
            if k not in s:
                pb.append("le système %r ne porte pas %s" % (s.get("nom"), k))
        if s.get("risque") not in ("faible", "moyen", "élevé"):
            pb.append("niveau de risque inconnu : %r" % (s.get("risque"),))
    if not any(s["ia"] for s in SYSTEMES):
        pb.append("aucun système génératif : l'inventaire ne décrit plus rien")
    if all(s["ia"] for s in SYSTEMES):
        pb.append("tous les systèmes sont déclarés génératifs : la distinction "
                  "que l'inventaire prétend porter a disparu")
    if pb:
        raise RuntimeError("politique_ia : " + " ; ".join(pb))


_verifier()
