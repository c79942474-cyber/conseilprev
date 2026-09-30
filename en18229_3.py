# -*- coding: utf-8 -*-
"""prEN 18229-3:2026 — la supervision humaine des systèmes d'IA, mesurée.

CE QUE CETTE NORME EST, ET CE QU'ELLE N'EST PAS. C'est la partie 3 du cadre
de fiabilité de l'IA du CEN/CENELEC JTC 21, écrite sur mandat de la
Commission (C(2023)3215 — M/613) pour donner un moyen VOLONTAIRE de se
conformer à l'article 14 du Règlement (UE) 2024/1689. Son annexe ZA dit
lesquels de ses paragraphes couvrent lesquels alinéas de l'article 14. Elle
est au stade de l'Enquête CEN : elle n'est PAS encore citée au Journal
officiel, donc elle ne confère PAS encore de présomption de conformité. Le
module le dit à l'écran, parce qu'un client qui l'ignore croirait acheter
une présomption qui n'existe pas encore.

LE DROIT D'AUTEUR COMMANDE LA FORME DU MODULE. Le texte est la propriété du
CEN et de ses membres nationaux. Aucune phrase normative n'est reproduite
ici : seuls les NUMÉROS et les TITRES de paragraphes sont cités — ce qu'un
index bibliographique fait — et tout ce qui les décrit, toutes les questions
du cadre d'analyse, sont rédigés par le cabinet.

CE QUE CELA INTERDIT, ET CE QUE CELA PERMET, MESURÉ. Aucune suite de huit
mots de la prose du module ne se retrouve dans le texte de la norme, hors
deux cas : les TITRES de paragraphes, cités comme un index les cite, et les
DÉSIGNATIONS d'un élément documentaire — on ne peut pas dire « la
documentation technique doit porter ceci » sans nommer ce « ceci ». Toute
autre coïncidence de huit mots est un défaut à corriger, et se vérifie en
comparant le module au texte que le cabinet détient.

LA DISTINCTION QUI COMMANDE TOUT LE RESTE : FOURNISSEUR ou DÉPLOYEUR. La
norme adresse ses exigences au FOURNISSEUR, pour la conception et le
développement du système. Ce qui dépend du contexte de déploiement ne
disparaît pas : il est TRANSMIS au déployeur par la notice d'utilisation.
Un déployeur n'est donc pas noté sur la conception d'une interface qu'il n'a
pas conçue — il est noté sur ce qu'il met en œuvre et sur ce qu'il EXIGE de
son fournisseur. Poser les mêmes questions aux deux rôles donnerait un score
faux dans les deux sens : accablant pour le déployeur, indulgent pour le
fournisseur.

CE QUE CE MODULE CALCULE, ET QU'UNE LISTE À COCHER NE CALCULE PAS. Le cœur
de la norme est une chaîne arithmétique, pas une case :

    scénario de risque (5.2.1)
        → délai de réaction (5.2.2)
            → catégorie de mesure de supervision (5.3)
                → latence d'intervention mesurée (5.7.1)

Le 5.7.1 exige que la latence d'intervention soit spécifiée, MESURÉE et
vérifiée comme compatible avec le délai de réaction. Le moteur compare donc
DEUX NOMBRES QUE LE CLIENT DÉCLARE — il n'invente aucun seuil, puisque la
norme n'en donne aucun. Quand la latence dépasse le délai, la mesure ne
tient pas le scénario : soit on relève la catégorie, soit le 5.2.4 s'applique
et l'impossibilité technique de l'intervention humaine en temps réel doit
être consignée au dossier de gestion des risques. Un rail qui dirait « case
cochée » sur un délai de 200 ms tenu par une revue rétrospective mentirait.

LE VERT NE VAUT PAS PRÉSOMPTION. Le score que rend ce module dit que ce que
la norme attend est déclaré et que l'arithmétique tient. Il ne dit pas qu'un
organisme notifié l'a vu, ni que la norme est citée au JOUE.
"""


# ═══════════════════════════════════════════════════════════════════════════
#  1. LA SOURCE, ET SA LICENCE
# ═══════════════════════════════════════════════════════════════════════════

SOURCE = {
    "titre": "prEN 18229-3:2026 — Cadre de fiabilité de l'IA — "
             "Partie 3 : Supervision humaine",
    "court": "prEN 18229-3:2026",
    "editeur": "CEN/CENELEC JTC 21 « Intelligence artificielle » "
               "(secrétariat : DS)",
    "millesime": "2026-07",
    "ics": "35.240.01",
    "stade": "Enquête CEN",
    "mandat": "Demande de normalisation C(2023)3215 — M/613 de la "
              "Commission européenne",
    # LA LIGNE QUI COMMANDE TOUTE LA FORME DU MODULE.
    "licence": "PROTÉGÉE PAR LE DROIT D'AUTEUR — © CEN et ses membres "
               "nationaux, tous droits réservés. Aucune partie du texte "
               "normatif n'est reproduite ici : seuls les numéros et les "
               "titres de paragraphes sont cités, et tout ce qui les décrit "
               "— y compris chaque question du cadre d'analyse — est rédigé "
               "par le cabinet.",
    "reproduction": False,
    "achat": "La mise en œuvre suppose de détenir le projet de norme, qui "
             "s'obtient auprès d'un membre national du CEN (AFNOR en "
             "France) ; au stade de l'Enquête, il est diffusé pour "
             "commentaires.",
    # CE QUI N'EST PAS ENCORE VRAI, ET QUI SE DIT AVANT LE RESTE.
    "presomption": False,
    "presomption_dit": "La présomption de conformité à l'article 14 ne "
                       "naîtra que le jour où la référence de la norme sera "
                       "citée au Journal officiel de l'Union européenne au "
                       "titre du Règlement (UE) 2024/1689. Ce n'est pas le "
                       "cas à ce jour : le projet est à l'Enquête CEN.",
    "certifiable": False,
    "lu_le": "2026-09-30",
}

#: Les documents que la norme appelle, et ce que chacun porte. UN MODULE QUI
#: TAIRAIT CETTE FAMILLE ferait croire que la supervision humaine se traite
#: seule : elle est calibrée par la gestion des risques et journalisée
#: ailleurs.
FAMILLE = (
    ("prEN 18228", "Gestion des risques liés à l'IA",
     "Article 9 — c'est là que les scénarios de risque sont identifiés, "
     "estimés et évalués, et que vit le dossier de gestion des risques sur "
     "lequel les mesures de supervision sont calibrées.", True),
    ("prEN 18229-1", "Conservation des documents",
     "Article 12 — la journalisation sur laquelle s'appuie toute revue de "
     "supervision, y compris l'enregistrement des interventions.", True),
    ("prEN 18229-2", "Transparence et fourniture d'informations aux "
                     "déployeurs",
     "Article 13 — la notice d'utilisation, c'est-à-dire le véhicule par "
     "lequel les obligations qui dépendent du déploiement passent du "
     "fournisseur au déployeur.", True),
    ("prEN 18229-4", "Exactitude",
     "Article 15, volet exactitude.", False),
    ("prEN 18229-5", "Robustesse",
     "Article 15 hors cybersécurité.", False),
    ("EN 18286:2026", "Système de management de la qualité pour le "
                      "règlement européen sur l'IA",
     "Article 17 — la conception, la vérification et la modification des "
     "mesures de supervision, et la surveillance de leur efficacité après "
     "la mise sur le marché, relèvent de ce système.", True),
)


# ═══════════════════════════════════════════════════════════════════════════
#  2. LES DEUX RÔLES DE L'ARTICLE 14, ET CE QUI PASSE DE L'UN À L'AUTRE
# ═══════════════════════════════════════════════════════════════════════════
#
# POURQUOI DEUX QUESTIONNAIRES ET NON UN SEUL AVEC DES CASES « SANS OBJET » :
# un questionnaire unique donne un score unique, et un score unique sur des
# exigences qui ne s'adressent pas à vous est un chiffre faux. Le déployeur
# qui répondrait « non » à « avez-vous conçu l'interface de revue » serait
# noté mauvais pour une chose qu'il n'a pas le droit de faire ; le
# fournisseur qui répondrait « sans objet » à la même question s'exonérerait
# de son obligation principale.

ROLES = {
    "fournisseur": {
        "nom": "Fournisseur",
        "dit": "Vous développez le système d'IA, ou vous le faites "
               "développer, et vous le mettez sur le marché ou en service "
               "sous votre nom ou votre marque.",
        "porte": "La norme vous adresse ses exigences. Elles portent sur la "
                 "conception et le développement : les mesures de "
                 "supervision elles-mêmes, leur vérification, et les "
                 "informations que vous transmettez au déployeur.",
        "transmet": "Ce qui dépend du contexte de déploiement, vous ne "
                    "pouvez pas le mettre en œuvre à la place du "
                    "déployeur : vous le SPÉCIFIEZ dans la notice "
                    "d'utilisation, avec ses critères de performance, les "
                    "compétences requises et les méthodes de vérification.",
    },
    "deployeur": {
        "nom": "Déployeur",
        "dit": "Vous utilisez le système d'IA sous votre propre autorité, "
               "hors activité personnelle non professionnelle.",
        "porte": "La norme ne vous adresse pas directement ses exigences : "
                 "elle les adresse à votre fournisseur. Ce qui vous revient "
                 "arrive par la notice d'utilisation — et c'est précisément "
                 "ce que ce cadre vous sert à EXIGER d'un fournisseur, puis "
                 "à mettre en œuvre.",
        "transmet": "Ce que vous mettez en œuvre reste sous votre "
                    "responsabilité : affecter des personnes désignées "
                    "compétentes, tenir les conditions d'utilisation, et "
                    "vérifier que la mesure fonctionne chez vous.",
    },
}

#: Ce qu'un rôle ne peut pas être. UNE PERSONNE QUI EST LES DEUX à la fois
#: (elle développe et elle exploite son propre système) répond aux deux
#: questionnaires : le module ne fusionne pas les deux scores, il les rend
#: tous les deux, parce que les deux obligations existent séparément.
ROLES_CUMULABLES = True


# ═══════════════════════════════════════════════════════════════════════════
#  3. LES TROIS CATÉGORIES DE MESURE DE SUPERVISION (5.3)
# ═══════════════════════════════════════════════════════════════════════════
#
# CE QUI LES DISTINGUE N'EST PAS LEUR RICHESSE, C'EST LE MOMENT OÙ ELLES
# INTERVIENNENT par rapport à la sortie du système. C'est ce moment qui
# décide si la catégorie peut tenir un délai de réaction — et c'est pour ça
# que le module les ordonne. Elles ne sont PAS exclusives : un même système
# peut porter des configurations différentes selon le scénario, et un même
# scénario peut en combiner plusieurs.
#
# L'ORDRE EST CELUI DE LA LATENCE ATTEIGNABLE, pas celui du texte. Une revue
# rétrospective regarde après ; une alerte appelle quelqu'un qui n'était pas
# là ; une surveillance continue parle à quelqu'un qui regardait déjà. Trois
# latences croissantes vers le haut, décroissantes vers le bas.

CATEGORIES = (
    ("continue", "Mesures de surveillance continue", "5.3.4",
     "La personne désignée a un accès continu et en temps réel à l'état du "
     "système, à ses sorties, à ses alertes et à la disponibilité des "
     "fonctions d'intervention.",
     "C'est la seule catégorie qui n'a pas à réveiller quelqu'un : la "
     "personne regardait déjà. C'est donc la plus courte latence "
     "atteignable — et la plus chère, parce qu'elle occupe quelqu'un.",
     "Une surveillance continue sans essai d'aptitude à l'utilisation "
     "(5.3.4.5) est une hypothèse : rien ne dit que la personne verra ce "
     "que l'écran montre, ni dans quel délai.",
     3),
    ("alerte", "Mesures d'intervention déclenchées par alerte", "5.3.3",
     "Le système notifie la personne désignée lorsqu'il entre dans un état "
     "qui demande une attention ou une intervention humaine ; la personne "
     "perçoit, évalue, puis intervient.",
     "Elle n'occupe personne à plein temps, mais elle ajoute à la latence "
     "le temps de percevoir l'alerte et de reprendre le contexte.",
     "Le taux de fausses alertes est le vrai sujet : une alerte qui crie "
     "trop souvent n'est plus perçue, et la latence réelle s'allonge sans "
     "que rien dans la conception ait changé.",
     2),
    ("retrospective", "Mesures de revue rétrospective", "5.3.2",
     "Les sorties sont examinées APRÈS avoir été produites, sur une "
     "interface qui porte le journal des sorties, leurs entrées, les scores "
     "de confiance, les alertes associées et la version du système.",
     "C'est la catégorie qui permet de corriger, d'escalader et de "
     "documenter — pas d'empêcher. Elle convient aux délais de réaction "
     "longs.",
     "Choisie seule sur un délai de réaction court, elle ne tient pas le "
     "scénario : la sortie est déjà partie. Le 5.2.4 existe pour ce cas, et "
     "il demande de le CONSIGNER, pas de l'ignorer.",
     1),
)

CATEGORIES_PAR_CLE = {c[0]: {"cle": c[0], "nom": c[1], "clause": c[2],
                             "quoi": c[3], "pourquoi": c[4], "piege": c[5],
                             "rang": c[6]}
                      for c in CATEGORIES}

#: Le rang le plus haut atteint par un jeu de catégories. C'EST LE MEILLEUR
#: DES CHOIX QUI COMMANDE, pas leur nombre : ajouter une revue rétrospective
#: à une surveillance continue n'abaisse pas la latence de l'ensemble.
def rang_categories(categories):
    """Le rang de latence du meilleur choix, ou 0 si aucun n'est déclaré."""
    rangs = [CATEGORIES_PAR_CLE[c]["rang"] for c in (categories or [])
             if c in CATEGORIES_PAR_CLE]
    return max(rangs) if rangs else 0


# ═══════════════════════════════════════════════════════════════════════════
#  4. LES QUATRE FONCTIONS D'INTERVENTION (5.7)
# ═══════════════════════════════════════════════════════════════════════════
#
# LA RÈGLE DE COMPOSITION EST EXPLICITE DANS LA NORME, et le module la tient
# telle quelle : au moins UNE des trois premières, PLUS un arrêt ou un mode
# opératoire sécurisé. Les trois premières agissent sur une sortie ; la
# quatrième agit sur le système. Ce ne sont pas quatre variantes d'une même
# chose : refuser une sortie n'arrête pas un système qui continue d'en
# produire.

FONCTIONS = (
    ("negligence", "Négligence", "5.7.2", "sortie",
     "La personne désignée rejette explicitement une sortie AVANT son "
     "exécution ; le système ne l'exécute pas et ne la rejoue pas.",
     "C'est la fonction minimale : elle suppose que la sortie passe par une "
     "porte avant d'agir."),
    ("ecrasement", "Écrasement", "5.7.3", "sortie",
     "La personne désignée bloque la sortie du système et lui substitue une "
     "alternative qu'elle fournit ; le chemin automatique est interrompu.",
     "Les deux sorties — celle du système et celle de la personne — "
     "s'enregistrent : sans les deux, on ne peut pas mesurer plus tard qui "
     "avait raison."),
    ("retour", "Retour", "5.7.4", "sortie",
     "La personne désignée annule une action DÉJÀ EXÉCUTÉE et ramène le "
     "processus à un état antérieur ou sécurisé.",
     "Elle oblige à écrire ce qui est réversible et ce qui ne l'est pas : "
     "un virement parti et un courriel envoyé ne se rattrapent pas."),
    ("etat_sur", "Transition en état sécurisé", "5.7.5", "systeme",
     "La personne désignée déclenche un état sécurisé prédéfini — ou un "
     "arrêt, lorsque l'arrêt est lui-même un état sécurisé — par un "
     "déclencheur accessible indépendamment de l'état du système.",
     "C'est la fonction que la norme rend OBLIGATOIRE en plus des autres. "
     "Un déclencheur qui dépend du système qu'il doit arrêter n'en est pas "
     "un."),
)

FONCTIONS_PAR_CLE = {f[0]: {"cle": f[0], "nom": f[1], "clause": f[2],
                            "porte_sur": f[3], "quoi": f[4], "pourquoi": f[5]}
                     for f in FONCTIONS}

#: Les trois fonctions qui portent sur une sortie : au moins une est exigée.
FONCTIONS_SUR_SORTIE = tuple(f[0] for f in FONCTIONS if f[3] == "sortie")
#: Celle qui porte sur le système, et qui s'ajoute aux autres.
FONCTION_SYSTEME = "etat_sur"


# ═══════════════════════════════════════════════════════════════════════════
#  5. LE SCÉNARIO DE RISQUE — LÀ OÙ LA NORME DEVIENT ARITHMÉTIQUE
# ═══════════════════════════════════════════════════════════════════════════
#
# LES DEUX NOMBRES SONT DÉCLARÉS PAR LE CLIENT, ET AUCUN N'EST INVENTÉ ICI.
# La norme ne donne aucun seuil chiffré — elle dit que le délai de réaction
# est déterminé par le fournisseur à partir du scénario (5.2.2), et que la
# latence d'intervention doit être spécifiée, MESURÉE et vérifiée comme
# compatible avec ce délai (5.7.1). Le moteur compare donc ce que le client
# déclare, et il nomme ce qu'il ne peut pas comparer. Un module qui poserait
# « moins de 500 ms = surveillance continue » substituerait son chiffre à
# celui d'un dossier de gestion des risques : ce serait faux, et opposable
# à personne.
#
# LES UNITÉS SE RAMÈNENT À LA MILLISECONDE. Un délai s'exprime en
# millisecondes pour certains systèmes et en jours pour d'autres : demander
# un nombre sans unité produirait des comparaisons entre des heures et des
# secondes.

UNITES = {
    "ms": ("milliseconde", 1),
    "s": ("seconde", 1000),
    "min": ("minute", 60 * 1000),
    "h": ("heure", 3600 * 1000),
    "j": ("jour", 24 * 3600 * 1000),
}

#: Les états d'un scénario, et ce que chacun veut dire. LE VERT NE DIT PAS
#: « SÛR », il dit « la latence déclarée tient le délai déclaré ».
ETATS_SCENARIO = {
    "tient": {
        "nom": "La mesure tient le délai",
        "dit": "La latence d'intervention déclarée est inférieure ou égale "
               "au délai de réaction déterminé pour ce scénario.",
        "couleur": "vert",
    },
    "ne_tient_pas": {
        "nom": "La mesure ne tient pas le délai",
        "dit": "La latence d'intervention déclarée dépasse le délai de "
               "réaction. La supervision humaine n'est pas, pour ce "
               "scénario, une mesure de gestion des risques : relevez la "
               "catégorie de mesure, ou appliquez le 5.2.4.",
        "couleur": "rouge",
    },
    "impossible_consignee": {
        "nom": "Impossibilité technique consignée (5.2.4)",
        "dit": "Aucune intervention humaine ne rentre dans ce délai, et "
               "l'impossibilité est consignée au dossier de gestion des "
               "risques. La supervision ne porte pas ce risque : d'autres "
               "mesures doivent le porter.",
        "couleur": "orange",
    },
    "impossible_non_consignee": {
        "nom": "Impossibilité technique NON consignée",
        "dit": "La latence dépasse le délai et aucune consignation au titre "
               "du 5.2.4 n'est déclarée. C'est le cas que la norme refuse : "
               "une affectation de supervision sans capacité d'intervention "
               "n'est pas une mesure.",
        "couleur": "rouge",
    },
    "sans_latence": {
        "nom": "Latence d'intervention non déclarée",
        "dit": "Le 5.7.1 exige que la latence d'intervention soit "
               "spécifiée, mesurée et vérifiée. Sans elle, rien ne dit que "
               "la mesure choisie tient le délai — le moteur ne suppose pas.",
        "couleur": "gris",
    },
    "sans_delai": {
        "nom": "Délai de réaction non déterminé",
        "dit": "Le 5.2.2 exige un délai de réaction PAR scénario. C'est lui "
               "qui commande le choix des catégories de mesure : sans lui, "
               "aucun choix n'est justifiable.",
        "couleur": "gris",
    },
    "sans_mesure": {
        "nom": "Aucune mesure de supervision sélectionnée",
        "dit": "Le 5.2.3 exige au moins une mesure par scénario. Un "
               "scénario sans mesure est un risque identifié que rien ne "
               "supervise.",
        "couleur": "rouge",
    },
}


def _nombre(v):
    """Un nombre, ou None. UNE CHAÎNE VIDE N'EST PAS ZÉRO : un délai non
    renseigné et un délai nul ne disent pas la même chose."""
    if v is None or v is True or v is False:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", ".").replace(" ", "").replace(" ", "")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def en_ms(valeur, unite):
    """Une durée déclarée, ramenée en millisecondes, ou None."""
    n = _nombre(valeur)
    if n is None or n < 0:
        return None
    f = UNITES.get(str(unite or "").strip())
    if not f:
        return None
    return n * f[1]


def duree_lisible(ms):
    """Une durée en millisecondes, rendue dans l'unité qui la lit le mieux."""
    if ms is None:
        return "—"
    for cle in ("j", "h", "min", "s"):
        seuil = UNITES[cle][1]
        if ms >= seuil:
            v = ms / seuil
            #  LA VIRGULE DÉCIMALE EST FRANÇAISE. « 1.7 heure » dans un
            #  rapport remis à un comité se lit comme une coquille.
            texte = ("%.0f" % v) if abs(v - round(v)) < 0.05 \
                else ("%.1f" % v).replace(".", ",")
            return "%s %s%s" % (texte, UNITES[cle][0],
                                "s" if v >= 2 else "")
    return "%.0f milliseconde%s" % (ms, "s" if ms >= 2 else "")


def scenario(d):
    """L'analyse d'UN scénario de risque : son délai, sa latence, ses
    catégories, et si l'ensemble tient.

    Ce que la fonction rend n'est jamais « conforme » ou « non conforme » :
    c'est l'un des sept états de ETATS_SCENARIO, chacun avec ce qui manque
    pour en sortir. Un moteur qui rendrait un booléen ferait disparaître la
    différence entre « ça ne tient pas » et « on ne sait pas encore ».
    """
    d = d if isinstance(d, dict) else {}
    nom = (str(d.get("nom") or "").strip() or None)
    delai = en_ms(d.get("delai"), d.get("delai_unite"))
    latence = en_ms(d.get("latence"), d.get("latence_unite"))
    cats = [c for c in (d.get("categories") or []) if c in CATEGORIES_PAR_CLE]
    consignee = bool(d.get("impossibilite_consignee"))

    r = {"nom": nom, "delai_ms": delai, "latence_ms": latence,
         "delai_dit": duree_lisible(delai), "latence_dit": duree_lisible(latence),
         "categories": cats, "rang": rang_categories(cats),
         "impossibilite_consignee": consignee, "manque": []}

    # L'ORDRE DES GARDES EST CELUI DE LA NORME : on ne juge pas l'adéquation
    # d'une mesure avant de savoir à quoi elle doit être adéquate.
    if delai is None:
        r["etat"] = "sans_delai"
        r["manque"].append("Déterminez le délai de réaction de ce scénario "
                           "(5.2.2) — c'est lui qui commande le choix des "
                           "catégories de mesure.")
        return r
    if not cats:
        r["etat"] = "sans_mesure"
        r["manque"].append("Sélectionnez au moins une catégorie de mesure de "
                           "supervision pour ce scénario (5.2.3).")
        return r
    if latence is None:
        r["etat"] = "sans_latence"
        r["manque"].append("Mesurez la latence d'intervention des mesures "
                           "choisies et déclarez-la (5.7.1) : sans elle, "
                           "l'adéquation au délai n'est pas vérifiée.")
        return r

    if latence <= delai:
        r["etat"] = "tient"
        r["marge_ms"] = delai - latence
        r["marge_dit"] = duree_lisible(delai - latence)
        return r

    # LA LATENCE DÉPASSE LE DÉLAI. Deux sorties, et une seule est un aveu
    # recevable : consigner l'impossibilité technique au titre du 5.2.4.
    r["depassement_ms"] = latence - delai
    r["depassement_dit"] = duree_lisible(latence - delai)
    if consignee:
        r["etat"] = "impossible_consignee"
        r["manque"].append("La supervision humaine ne porte pas ce risque : "
                           "vérifiez que d'autres mesures de gestion des "
                           "risques le portent (prEN 18228), et que la "
                           "consignation nomme le temps minimal "
                           "d'intervention retenu.")
        return r
    # LE CONSEIL EST CHIFFRÉ, PAS GÉNÉRAL : si une catégorie plus rapide
    # existe encore, c'est la première chose à essayer.
    r["etat"] = "impossible_non_consignee"
    if r["rang"] < 3:
        plus_rapide = [c["nom"] for c in CATEGORIES_PAR_CLE.values()
                       if c["rang"] > r["rang"]]
        r["manque"].append("La latence dépasse le délai de %s. Relevez la "
                           "catégorie de mesure — %s restent disponibles — "
                           "et mesurez la nouvelle latence."
                           % (r["depassement_dit"],
                              " ou ".join(sorted(plus_rapide))))
    else:
        r["manque"].append("La latence dépasse le délai de %s alors que la "
                           "catégorie la plus rapide est déjà retenue : le "
                           "5.2.4 s'applique. Consignez l'impossibilité "
                           "technique de l'intervention humaine en temps "
                           "réel au dossier de gestion des risques."
                           % r["depassement_dit"])
    return r


# ═══════════════════════════════════════════════════════════════════════════
#  6. LES EXIGENCES, PAR PARAGRAPHE ET PAR RÔLE
# ═══════════════════════════════════════════════════════════════════════════
#
# CE QUE CHAQUE ENTRÉE PORTE, ET POURQUOI CHAQUE CHAMP EXISTE :
#
#   cle       identifiant stable — une règle de test le nomme, pas son rang
#   clause    le NUMÉRO du paragraphe de la norme, cité comme un index
#   titre     le TITRE du paragraphe, cité comme un index
#   role      « fournisseur », « deployeur », ou les deux : c'est ce champ
#             qui fait qu'un déployeur n'est pas noté sur la conception
#   question  RÉDIGÉE PAR LE CABINET — aucune phrase normative recopiée
#   pourquoi  ce que la question sert à éviter, en clair
#   piege     le défaut que le cabinet voit en mission sur ce point
#   poids     ce que la réponse pèse dans le score (1 à 3)
#   verrou    si renseigné : ce point PLAFONNE le score tant qu'il n'est pas
#             tenu, et le texte dit pourquoi
#   si        condition d'applicabilité : None, « rbi », ou
#             « pas_de_notification_fournisseur »
#
# LES POIDS NE SONT PAS DÉCORATIFS. Un point qui commande d'autres points
# pèse davantage : sans scénario de risque, rien en aval n'est calibré.

def _e(cle, clause, titre, role, question, pourquoi, piege, poids,
       verrou=None, si=None):
    return {"cle": cle, "clause": clause, "titre": titre, "role": role,
            "question": question, "pourquoi": pourquoi, "piege": piege,
            "poids": poids, "verrou": verrou, "si": si}


EXIGENCES = (
    # ── 5.2 L'INTÉGRATION DE LA GESTION DES RISQUES ──────────────────────
    _e("scenarios", "5.2.1", "Identification des scénarios de risque",
       ("fournisseur",),
       "Avez-vous identifié, au niveau logique ou fonctionnel, les scénarios "
       "où une sortie du système peut conduire à un dommage et où la "
       "supervision humaine est nécessaire pour l'empêcher ou l'atténuer ?",
       "C'est la racine de tout le reste : le délai de réaction, le choix "
       "des catégories de mesure et la vérification sont tous calibrés "
       "scénario par scénario.",
       "Les scénarios s'écrivent par TYPE de sortie et par chaîne de cause "
       "à effet, pas par instance de déploiement : une liste de clients "
       "n'est pas une liste de scénarios.",
       3,
       verrou="Sans scénario de risque identifié, aucune mesure de "
              "supervision n'est calibrée sur quoi que ce soit : le score "
              "ne peut pas dépasser 25 %."),
    _e("delai", "5.2.2", "Délai de réaction", ("fournisseur",),
       "Avez-vous déterminé, pour CHAQUE scénario, le délai de réaction, en "
       "tenant compte de vos critères d'acceptabilité du risque ?",
       "C'est le critère qui décide quelle catégorie de mesure peut tenir "
       "le scénario. Un délai en millisecondes et un délai en jours "
       "n'appellent pas la même supervision.",
       "Un délai unique pour tout le système est presque toujours faux : il "
       "est déterminé par le scénario, donc il varie d'un scénario à "
       "l'autre.",
       3,
       verrou="Sans délai de réaction, le choix des catégories de mesure "
              "n'est justifiable par rien : le score ne peut pas dépasser "
              "40 %."),
    _e("selection", "5.2.3", "Sélection et documentation des mesures",
       ("fournisseur",),
       "Avez-vous sélectionné au moins une mesure par scénario, vérifié "
       "qu'elles sont COLLECTIVEMENT suffisantes pour permettre "
       "l'intervention dans le délai, et documenté ce choix au dossier de "
       "gestion des risques ?",
       "Une mesure par scénario est le plancher ; l'adéquation au délai est "
       "le critère. Quand aucune catégorie seule n'y suffit, il faut les "
       "combiner.",
       "« Nous avons une interface de revue » n'est pas une sélection : la "
       "sélection se justifie scénario par scénario, contre un délai.",
       3),
    _e("impossibilite", "5.2.4",
       "Impossibilité technique de l'intervention humaine en temps réel",
       ("fournisseur",),
       "Lorsqu'un délai de réaction ne laisse matériellement pas le temps "
       "d'une intervention humaine en conditions réelles, l'avez-vous "
       "consigné au dossier de gestion des risques, avec le temps minimal "
       "d'intervention que vous retenez ?",
       "C'est l'aveu recevable. Confier une responsabilité de supervision à "
       "quelqu'un qui n'a pas matériellement le temps d'intervenir n'est "
       "pas une mesure de gestion des risques — et le prétendre expose.",
       "Ce n'est pas une dispense : le risque reste, et d'autres mesures "
       "doivent le porter. La consignation dit seulement que la supervision "
       "humaine ne le portera pas.",
       2),
    _e("surcharge", "5.2.5", "Surcharge et conflit", ("fournisseur",),
       "Lorsqu'une seule personne désignée supervise plusieurs scénarios, "
       "avez-vous démontré et justifié dans la documentation technique "
       "qu'elle le peut sans surcharge cognitive ni conflit ?",
       "La supervision se dégrade par la fatigue, la baisse de vigilance et "
       "le conflit d'attention bien avant de se dégrader par une faute de "
       "conception.",
       "La démonstration se fait sur la charge RÉELLE attendue, pas sur un "
       "poste théorique : c'est le nombre de scénarios simultanés qui "
       "compte, pas le nombre d'écrans.",
       2),
    _e("revue_affectations", "5.2.6", "Revue des affectations de supervision",
       ("fournisseur",),
       "Revoyez-vous les scénarios, les délais et les mesures lors de la "
       "surveillance après commercialisation et à chaque modification de "
       "conception, et mettez-vous à jour le dossier en conséquence ?",
       "Un système d'IA change ; ses scénarios de risque changent avec lui. "
       "Une supervision calibrée une fois vieillit sans que rien ne le "
       "signale.",
       "Cette revue relève du système de management de la qualité "
       "(EN 18286:2026) : si vous n'en avez pas, elle n'aura pas de "
       "déclencheur.",
       2),

    # ── 5.3 LES CATÉGORIES DE MESURE ──────────────────────────────────────
    _e("categories", "5.3.1", "Généralités (catégories de mesure)",
       ("fournisseur",),
       "Les mesures que vous avez sélectionnées appartiennent-elles aux trois "
       "catégories de la norme — revue rétrospective, intervention "
       "déclenchée par alerte, surveillance continue — ou sont-elles conçues "
       "pour satisfaire les critères de ces catégories ?",
       "Ce qui sépare les trois catégories, c'est QUAND l'humain entre en "
       "scène : après la sortie, appelé par une alerte, ou déjà présent. "
       "C'est ce « quand » qui décide si la mesure tient le délai.",
       "Ce ne sont pas des classifications exclusives auxquelles le système "
       "entier serait affecté : un même système porte des configurations "
       "différentes selon le scénario, et un scénario peut en combiner "
       "plusieurs.",
       2),
    _e("retro_interface", "5.3.2.1", "Exigences d'interface (revue "
       "rétrospective)", ("fournisseur",),
       "Votre interface de revue porte-t-elle, pour chaque sortie, son "
       "journal horodaté, ses données d'entrée, ses scores de confiance, "
       "les alertes associées, la version du système — et permet-elle à la "
       "personne désignée d'y AJOUTER ses propres observations ?",
       "Une revue sans les entrées ni la version du système ne permet pas "
       "de dire si le comportement était dans les limites attendues : elle "
       "constate sans pouvoir conclure.",
       "L'ajout d'observations par la personne désignée est régulièrement "
       "oublié : ce qu'elle savait de l'environnement au moment de la "
       "sortie n'est dans aucun journal machine.",
       2),
    _e("retro_parametres", "5.3.2.2", "Paramètres de conception (revue "
       "rétrospective)", ("fournisseur",),
       "Avez-vous déterminé la durée de conservation, les capacités de "
       "filtrage et d'agrégation, les mécanismes de signalement, les "
       "fonctions de revue et la traçabilité entre chaque sortie, son "
       "entrée, sa revue et l'action corrective ?",
       "La durée de conservation se règle sur le temps nécessaire pour "
       "identifier et imputer un dommage — pas sur une politique d'archivage "
       "générique.",
       "Sans filtrage par scénario, type de sortie et score de confiance, "
       "une revue rétrospective sur un gros volume devient une navigation "
       "au hasard.",
       2),
    _e("retro_verif", "5.3.2.3.1", "Vérification (revue rétrospective)",
       ("fournisseur",),
       "Avez-vous vérifié que les personnes désignées repèrent les sorties "
       "incorrectes ou dangereuses et agissent DANS le délai de réaction, "
       "défini des critères d'acceptation, traité les écarts avant la mise "
       "sur le marché, et prévu comment la revue se poursuit si l'interface "
       "principale ou la journalisation tombe ?",
       "La vérification est ce qui sépare une interface conçue d'une "
       "interface qui fonctionne. Les critères d'acceptation et les "
       "résultats entrent dans la documentation technique.",
       "Les procédures de repli s'oublient : quand l'interface de revue "
       "tombe, la capacité de revue tombe avec elle et personne ne l'avait "
       "prévu.",
       2),
    _e("alerte_conception", "5.3.3.1", "Conception des fonctions de "
       "notification", ("fournisseur",),
       "Vos seuils d'alerte viennent-ils des dangers prévisibles, de la "
       "cotation du risque et du temps dont la personne dispose — et "
       "l'alerte part-elle d'elle-même dès que le système atteint un état "
       "qui appelle quelqu'un ?",
       "Une alerte dont le seuil ne vient pas du dossier de gestion des "
       "risques est un réglage d'ingénieur, pas une mesure.",
       "Les alertes de TRANSPARENCE (comprendre une sortie) et les "
       "notifications de SUPERVISION (déclencher une intervention) sont "
       "deux objets différents : la prEN 18229-2 traite les premières.",
       2),
    _e("alerte_exigences", "5.3.3.2", "Exigences des fonctions de "
       "notification", ("fournisseur",),
       "Vos notifications sont-elles perceptibles et interprétables dans "
       "les conditions réelles d'exploitation, distinguées par urgence, "
       "présentées sur une modalité testée, et leur logique d'escalade "
       "est-elle validée comme émettant assez tôt pour permettre une action "
       "efficace ?",
       "Le taux de fausses alertes et la latence de réponse sont les deux "
       "mesures qui décident si une alerte sert encore à quelque chose.",
       "Une modalité unique — le visuel — échoue dès que la personne "
       "désignée regarde ailleurs, ce qui est le cas normal d'un poste qui "
       "fait autre chose.",
       2),
    _e("continue_generales", "5.3.4.1", "Exigences générales (surveillance "
       "continue)", ("fournisseur",),
       "La personne désignée a-t-elle un accès continu et en temps réel au "
       "fonctionnement courant du système et à ses notifications — et "
       "sait-elle à tout instant si elle peut encore écraser une sortie, "
       "couper le système ou le remettre à zéro ?",
       "Le statut des fonctions d'intervention fait partie de "
       "l'information de supervision : savoir qu'on peut arrêter est une "
       "condition pour arrêter.",
       "L'état du système ne se résume pas à « en marche » : actif, "
       "inactif, dégradé et sécurisé ne demandent pas la même réaction.",
       2),
    _e("continue_ihm", "5.3.4.2", "Conception de l'interface homme-machine",
       ("fournisseur",),
       "Peut-on lire sur l'interface, sans se tromper, où en est le système et "
       "s'il sort de ses bornes — et la commande qui déclenche une "
       "atténuation résiste-t-elle à un geste involontaire quand le "
       "scénario le demande ?",
       "Une commande d'arrêt trop facile à heurter crée un danger de plus ; "
       "une commande trop difficile à atteindre annule la mesure.",
       "La présentation des sorties et des indicateurs de confiance relève "
       "de la prEN 18229-2 : ce paragraphe ne traite que les fonctions de "
       "supervision.",
       2),
    _e("continue_fonctionnalite", "5.3.4.3", "Fonctionnalité de l'interface",
       ("fournisseur",),
       "L'écran dit-il ce que le système sait et ne sait pas faire, et "
       "rapporte-t-il ce qu'il fait AUX scénarios de risque que vous avez "
       "identifiés — pas à des courbes générales ?",
       "Une surveillance détachée des scénarios n'est qu'un mur d'écrans : "
       "c'est l'écart au seuil de risque qui appelle un geste.",
       "Les indicateurs qui mettent en évidence les écarts automatiquement "
       "font la différence entre une surveillance et une veille passive.",
       1),
    _e("continue_verif", "5.3.4.4", "Vérification (surveillance continue)",
       ("fournisseur",),
       "Avez-vous vérifié que les personnes désignées accomplissent les "
       "tâches de supervision clés DANS le délai de réaction, avec des "
       "critères d'acceptation définis et des résultats consignés dans la "
       "documentation technique ?",
       "C'est la même logique que pour la revue rétrospective : une "
       "interface non vérifiée est une hypothèse sur le comportement humain.",
       "Les essais d'aptitude à l'utilisation (5.3.4.5) sont la méthode "
       "recommandée, avec des personnes désignées représentatives — pas "
       "l'équipe qui a conçu l'écran.",
       2),

    # ── 5.4 CE QUE LE DÉPLOYEUR MET EN ŒUVRE ──────────────────────────────
    _e("deploy_specification", "5.4.1", "Conditions relatives aux mesures et "
       "à la documentation mises en œuvre par le déployeur",
       ("fournisseur",),
       "Pour chaque mesure que le déployeur doit mettre en œuvre, la notice "
       "d'utilisation nomme-t-elle le risque visé, ce qu'il faut mettre en "
       "œuvre (technique, procédural, organisationnel), les critères de "
       "performance mesurables, les compétences requises et les méthodes de "
       "vérification recommandées ?",
       "C'est le véhicule de la responsabilité : ce que la notice ne dit "
       "pas, le déployeur ne le mettra pas en œuvre, et le risque restera "
       "sans porteur.",
       "« Le déployeur veillera à » n'est pas une spécification : sans "
       "critère de performance mesurable, la mesure n'est pas vérifiable "
       "chez le déployeur.",
       3),
    _e("deploy_residuel", "5.4.2", "Limitations du risque résiduel",
       ("fournisseur",),
       "La notice d'utilisation dit-elle quels risques résiduels subsistent "
       "même si les mesures du déployeur sont correctement mises en œuvre, "
       "et à quelles conditions ou limitations l'usage est soumis si elles "
       "ne le sont pas ?",
       "Un déployeur qui ne connaît pas le risque résiduel ne peut pas "
       "l'accepter — et c'est lui qui l'accepte.",
       "La seconde moitié s'oublie : ce qui se passe si la mesure N'EST PAS "
       "mise en œuvre doit être écrit, sinon le système est utilisé hors de "
       "sa destination sans que personne le sache.",
       2),
    _e("deploy_notifications", "5.4.3", "Spécifications relatives aux "
       "notifications mises en œuvre par le déployeur", ("fournisseur",),
       "Puisque vous ne mettez pas en œuvre les notifications en temps réel, "
       "la notice donne-t-elle les seuils, ce que l'alerte doit dire, sur "
       "quel canal, et par quelle prise technique le déployeur s'y "
       "branche — assez pour qu'il implémente ET TESTE sans vous "
       "rappeler ?",
       "Une spécification incomplète transforme une obligation transmise en "
       "obligation impossible : le déployeur ne peut pas tester ce dont il "
       "n'a pas l'interface.",
       "La justification de votre impossibilité à implémenter ces "
       "notifications doit figurer dans la documentation technique, en "
       "renvoyant au délai de réaction.",
       2, si="pas_de_notification_fournisseur"),
    _e("deploy_mise_en_oeuvre", "5.4.1", "Mise en œuvre par le déployeur des "
       "mesures spécifiées", ("deployeur",),
       "Avez-vous mis en œuvre CHAQUE mesure de supervision que la notice "
       "d'utilisation vous attribue, avec les moyens techniques, les "
       "procédures et l'organisation qu'elle spécifie ?",
       "C'est votre part du dispositif. La conception du fournisseur ne "
       "supervise rien tant que vous n'avez pas affecté quelqu'un et "
       "branché la mesure sur votre exploitation.",
       "Une mesure « prévue » n'est pas une mesure mise en œuvre : ce qui "
       "compte est la procédure écrite, la personne nommée et la preuve "
       "qu'elle l'applique.",
       3,
       verrou="Sans mise en œuvre des mesures que la notice vous attribue, "
              "la supervision humaine du système que vous exploitez n'existe "
              "pas : le score ne peut pas dépasser 30 %."),
    _e("deploy_verification", "5.4.1", "Vérification par le déployeur de ses "
       "propres mesures", ("deployeur",),
       "Avez-vous vérifié, par les méthodes que la notice recommande, que "
       "chaque mesure tourne bien chez vous ET qu'elle produit l'effet "
       "attendu, au regard des critères de performance qu'elle donne ?",
       "Les critères de performance sont dans la notice pour être mesurés. "
       "Sans mesure, vous avez une procédure, pas une preuve.",
       "L'efficacité se mesure dans VOS conditions : le même seuil d'alerte "
       "ne produit pas la même charge chez deux déployeurs.",
       2),
    _e("deploy_conditions", "5.4.2", "Respect des conditions et du risque "
       "résiduel", ("deployeur",),
       "Avez-vous lu les risques résiduels et les conditions d'utilisation "
       "de la notice, et les tenez-vous — ou avez-vous formellement accepté "
       "les risques que vous ne couvrez pas ?",
       "Utiliser le système hors des conditions de sa destination vous fait "
       "sortir du cadre où le fournisseur a démontré quoi que ce soit.",
       "L'acceptation d'un risque résiduel se décide au niveau qui a le "
       "pouvoir de l'accepter, et se trace : sinon elle n'a pas eu lieu.",
       2),

    # ── 5.5 BIAIS D'AUTOMATISATION ────────────────────────────────────────
    _e("biais_conception", "5.5.1", "Sensibilisation au biais "
       "d'automatisation", ("fournisseur",),
       "Votre conception oblige-t-elle la personne désignée à examiner vraiment "
       "une sortie avant de la retenir, au lieu de la laisser valider par "
       "habitude ?",
       "C'est l'alinéa 14(4)(b) du règlement. Une personne qui valide tout "
       "par habitude n'est pas une mesure de gestion des risques, même si "
       "elle clique.",
       "Les dispositifs d'engagement coûtent de l'attention : mal dosés, "
       "ils créent la surcharge qu'ils devaient éviter.",
       2),
    _e("biais_tests", "5.5.2", "Tests de biais d'automatisation",
       ("fournisseur",),
       "Avez-vous testé si vos mesures maintiennent l'acceptation passive "
       "dans des limites acceptables — par exemple en présentant à des "
       "personnes représentatives un mélange de sorties correctes et "
       "volontairement erronées, et en mesurant ce qui passe ?",
       "C'est le seul moyen de savoir si la conception fonctionne : le "
       "biais d'automatisation ne se déclare pas, il se mesure.",
       "Comparer AVEC et SANS les dispositifs d'atténuation est ce qui "
       "donne un résultat interprétable ; un taux seul ne dit rien.",
       1),
    _e("biais_deployeur", "5.5.1", "Sensibilisation des personnes désignées "
       "au biais d'automatisation", ("deployeur",),
       "Vos personnes désignées sont-elles averties du biais "
       "d'automatisation, et votre organisation du travail leur laisse-t-elle "
       "le temps d'examiner réellement les sorties ?",
       "Le dispositif du fournisseur suppose une personne disponible. Une "
       "cadence qui ne laisse pas le temps d'examiner produit l'acceptation "
       "passive quelle que soit la conception.",
       "Un objectif de volume horaire sur un poste de supervision est "
       "l'antidote exact de la supervision.",
       2),

    # ── 5.6 INTERPRÉTATION DES SORTIES ────────────────────────────────────
    _e("interpretation", "5.6.1", "Support d'interprétation de sortie pour "
       "les personnes désignées", ("fournisseur",),
       "Le système, sa documentation et le matériel d'entraînement "
       "obligatoire permettent-ils aux personnes désignées de comprendre le "
       "fonctionnement, les capacités et les limites du système, et les "
       "compétences que vous supposez sont-elles DÉCLARÉES dans la notice ?",
       "C'est l'alinéa 14(4)(c). Un score de confiance qu'on ne sait pas "
       "lire n'aide personne, et des compétences supposées mais non "
       "déclarées ne seront pas recrutées.",
       "Les compétences supposées doivent être celles de la notice, pas "
       "celles de l'équipe qui a conçu le système.",
       2),
    _e("entrainement", "5.6.2", "Matériel d'entraînement destiné aux "
       "personnes désignées", ("fournisseur",),
       "Le matériel d'entraînement couvre-t-il les limites et mises en "
       "garde, la façon dont la base de calcul des sorties peut produire "
       "des sorties exceptionnelles, et — pour un système qui continue "
       "d'apprendre — si les actions de supervision influencent ou non "
       "l'apprentissage ?",
       "Une personne désignée qui ignore que son écrasement nourrit le "
       "modèle ne peut pas mesurer la portée de son geste.",
       "C'est une recommandation dans la norme, pas une exigence : elle "
       "pèse donc moins, mais son absence se voit en audit d'usage.",
       1),
    _e("competences_deployeur", "5.6.1", "Affectation de personnes désignées "
       "compétentes", ("deployeur",),
       "Les personnes que vous affectez à la supervision ont-elles les "
       "compétences que la notice d'utilisation déclare, et ont-elles suivi "
       "le matériel d'entraînement fourni ?",
       "Le fournisseur a démontré sa supervision pour un profil donné. Une "
       "personne moins qualifiée que ce profil invalide la démonstration.",
       "L'écart le plus fréquent : la supervision est confiée au poste "
       "disponible, pas au profil déclaré.",
       3),

    # ── 5.7 LES FONCTIONS D'INTERVENTION ──────────────────────────────────
    _e("fonctions", "5.7.1", "Généralités (fonctions d'intervention)",
       ("fournisseur",),
       "Le système met-il en œuvre au moins une fonction parmi négligence, "
       "écrasement et retour, PLUS de quoi couper le système ou le "
       "basculer en marche dégradée sûre — et la latence est-elle "
       "spécifiée, mesurée et vérifiée comme compatible avec le délai de "
       "réaction ?",
       "C'est l'alinéa 14(4)(d) et (e). Sans fonction d'intervention, la "
       "supervision se réduit à regarder.",
       "L'abstention est une intervention : la personne désignée doit "
       "pouvoir écarter une sortie sans s'en servir, et ce "
       "refus s'enregistre comme un événement de supervision.",
       3,
       verrou="Sans fonction d'intervention, la supervision humaine ne peut "
              "rien empêcher : le score ne peut pas dépasser 35 %."),
    _e("negligence", "5.7.2", "Négligence", ("fournisseur",),
       "Lorsque la personne désignée rejette une sortie avant son exécution, "
       "le système s'abstient-il de l'exécuter, l'enregistre-t-il, et reste-"
       "t-il stable sans la rejouer ?",
       "Rejeter une sortie que le système rejoue une seconde plus tard n'est "
       "pas un rejet. La stabilité après rejet est la moitié de la fonction.",
       "L'enregistrement du rejet relève de la prEN 18229-1 : sans lui, on ne "
       "peut pas démontrer plus tard que la sortie n'a pas agi.",
       2),
    _e("ecrasement", "5.7.3", "Écrasement", ("fournisseur",),
       "Lorsque la personne désignée substitue sa propre sortie, le chemin "
       "d'exécution automatique est-il interrompu, l'alternative humaine "
       "intégrée, et LES DEUX sorties — celle du système et la vôtre — "
       "enregistrées ?",
       "Enregistrer les deux est ce qui permet, six mois plus tard, de "
       "mesurer qui avait raison et d'ajuster le système ou la formation.",
       "N'enregistrer que la sortie retenue efface la trace du désaccord, "
       "c'est-à-dire l'information la plus utile du dispositif.",
       2),
    _e("retour", "5.7.4", "Retour", ("fournisseur",),
       "La personne désignée peut-elle annuler une action DÉJÀ exécutée et "
       "ramener le processus à un état antérieur ou sécurisé, les processus "
       "dépendants reçoivent-ils l'ordre de revenir eux aussi, et la notice "
       "dit-elle ce qui est réversible et ce qui ne l'est pas ?",
       "Un retour qui ne prévient pas les processus en aval laisse le système "
       "dans un état incohérent : une moitié est revenue, l'autre non.",
       "La liste des conditions NON réversibles est la partie qui compte : un "
       "virement exécuté et un courriel envoyé ne se rattrapent pas, et la "
       "personne désignée doit le savoir avant d'agir.",
       2),
    _e("etat_sur", "5.7.5", "Transition en état sécurisé", ("fournisseur",),
       "La personne désignée dispose-t-elle d'une commande de mise en "
       "sécurité — bouton matériel ou commande logicielle — atteignable "
       "INDÉPENDAMMENT du système, et la bascule est-elle validée sur le "
       "temps, "
       "la stabilité, la complétude de l'atténuation et la récupération ?",
       "Un déclencheur qui passe par le système qu'il doit arrêter tombe "
       "avec lui. C'est le cas d'école, et il se produit.",
       "Pendant l'état sécurisé, seules les fonctions documentées comme "
       "restant actives doivent l'être : tout le reste est inerte, et cela "
       "se teste.",
       2),
    _e("comportement_apres", "5.7.1", "Prévisibilité du comportement après "
       "intervention", ("fournisseur",),
       "Le comportement du système après une intervention est-il "
       "prévisible, et les écarts constatés sont-ils documentés et analysés "
       "dans la documentation technique ?",
       "Une personne désignée qui ne sait pas ce que fait le système après "
       "son geste n'intervient plus qu'à contrecœur.",
       "Les écarts se documentent : c'est l'un des sept éléments que la "
       "documentation technique doit porter.",
       1),

    # ── 5.8 IDENTIFICATION BIOMÉTRIQUE À DISTANCE (RBI) ───────────────────
    _e("rbi_prevention", "5.8.1", "Prévention technique des sorties "
       "d'identification non revues", ("fournisseur",),
       "Le système empêche-t-il TECHNIQUEMENT une sortie d'identification "
       "de déclencher une action, une décision automatisée ou une "
       "transmission avant que les revues de deux personnes physiques "
       "distinctes soient enregistrées ?",
       "C'est l'alinéa 14(5) du règlement : la vérification séparée par au "
       "moins deux personnes. « Techniquement » veut dire que la "
       "procédure ne suffit pas.",
       "La sortie doit rester isolée pendant la revue : si elle est "
       "consultable par les systèmes en aval « pour information », elle "
       "n'est pas isolée.",
       3, si="rbi",
       verrou="Sans prévention technique des sorties non revues, l'alinéa "
              "14(5) n'est pas tenu sur un système d'identification "
              "biométrique à distance : le score ne peut pas dépasser 30 %."),
    _e("rbi_statuts", "5.8.2.1", "Généralités (processus de revue)",
       ("fournisseur",),
       "Le système distingue-t-il au minimum les états « revue requise », "
       "« revue complétée » et « rejeté », et l'accès à l'interface de "
       "revue est-il limité à des comptes authentifiés ?",
       "Les trois états sont ce qui rend la prévention technique "
       "vérifiable : sans état, on ne peut pas prouver qu'une sortie non "
       "revue n'a rien déclenché.",
       "Une sortie rejetée doit être exclue de toute action opérationnelle, "
       "pas seulement marquée.",
       2, si="rbi"),
    _e("rbi_informations", "5.8.2.2", "Fourniture d'informations à des fins "
       "de revue", ("fournisseur",),
       "Chaque réviseur dispose-t-il des quatre éléments sans lesquels la "
       "revue est formelle : l'échantillon capté, l'identification "
       "proposée, les indicateurs de qualité, et le contexte — horodatage "
       "et alertes comprises ?",
       "Une revue sans indicateur de qualité ne peut pas distinguer une "
       "identification douteuse d'une image médiocre.",
       "Les métadonnées contextuelles sont ce qui permet de reconstituer la "
       "scène plus tard, en cas de contestation.",
       2, si="rbi"),
    _e("rbi_interface", "5.8.2.3", "Exigences relatives à la conception de "
       "l'interface de revue", ("fournisseur",),
       "L'interface permet-elle une inspection détaillée — zoom, vue "
       "panoramique, affichage côte à côte ou à bascule de la sonde et de "
       "la référence — et signale-t-elle la faible qualité d'image et les "
       "scores sous les seuils déclarés dans la notice ?",
       "La comparaison visuelle est l'acte de revue. Une résolution "
       "insuffisante rend la revue formelle.",
       "Les seuils sous lesquels un score déclenche une alerte doivent "
       "figurer dans la notice d'utilisation : c'est l'un des sept éléments "
       "exigés.",
       2, si="rbi"),
    _e("rbi_entrees", "5.8.2.4", "Exigences relatives aux entrées de revue",
       ("fournisseur",),
       "La décision de revue exige-t-elle une action explicite — aucune "
       "action passive ne valant décision — le système permet-il "
       "d'enregistrer des observations, et consigne-t-il décision, notes et "
       "horodatage ?",
       "Un délai qui expire et vaut validation détruit la garantie de "
       "l'alinéa 14(5).",
       "La politique qui tranche un désaccord entre réviseurs relève du "
       "propriétaire du système : elle doit être définie et documentée, pas "
       "improvisée.",
       2, si="rbi"),
    _e("rbi_independance", "5.8.3", "Mécanismes d'indépendance du réviseur "
       "manuel", ("fournisseur",),
       "Le système authentifie-t-il chaque réviseur par des justificatifs "
       "individuels, empêche-t-il un même compte de réviser deux fois la "
       "même sortie, masque-t-il en revue séquentielle la décision du "
       "premier réviseur au second, et enregistre-t-il chaque action "
       "séparément ?",
       "Deux revues du même compte ou une seconde revue qui voit la "
       "première ne font pas deux vérifications indépendantes : elles en "
       "font une, et l'alinéa 14(5) n'est pas tenu.",
       "Le masquage en revue séquentielle est le point le plus souvent "
       "absent : techniquement simple, il est presque toujours oublié.",
       3, si="rbi"),
    _e("rbi_documentation", "5.8.4", "Exigences relatives à la documentation "
       "(RBI)", ("fournisseur",),
       "La documentation technique porte-t-elle les mécanismes "
       "d'indépendance mis en œuvre, les résultats d'essai qui démontrent "
       "qu'ils fonctionnent, et les options de configuration offertes aux "
       "déployeurs pour la gestion du flux de revue ?",
       "Les options de configuration sont le point de bascule : une option "
       "qui permet au déployeur de ramener la revue à une personne annule "
       "la garantie.",
       "Les résultats d'essai, pas la description : une architecture "
       "décrite n'est pas une architecture validée.",
       2, si="rbi"),
    _e("rbi_competences", "5.8.5", "Exigences relatives aux compétences du "
       "réviseur manuel", ("fournisseur",),
       "La notice d'utilisation définit-elle les compétences et la "
       "formation minimales des réviseurs — savoir se servir de "
       "l'interface, savoir lire un score de confiance et un indicateur "
       "de qualité, être averti du biais d'automatisation — et "
       "recommande-t-elle un contenu de formation ?",
       "Deux réviseurs mal formés ne valent pas mieux qu'un réviseur formé, "
       "et l'alinéa 14(5) exige les deux.",
       "La sensibilisation au biais d'automatisation est explicitement "
       "citée parmi les compétences : sur un flux de milliers "
       "d'identifications, c'est le risque premier.",
       2, si="rbi"),
    _e("rbi_deployeur", "5.8.5", "Affectation de deux réviseurs "
       "indépendants", ("deployeur",),
       "Affectez-vous effectivement deux personnes physiques distinctes, "
       "avec les compétences déclarées dans la notice, à la revue de chaque "
       "sortie d'identification — et votre configuration du système ne "
       "ramène-t-elle pas la revue à une seule personne ?",
       "La prévention est technique chez le fournisseur ; l'affectation est "
       "organisationnelle chez vous. Les deux sont nécessaires.",
       "Les options de configuration de la revue sont documentées "
       "précisément pour que vous sachiez laquelle vous exposerait.",
       3, si="rbi",
       verrou="Sans deux réviseurs indépendants effectivement affectés, "
              "l'alinéa 14(5) n'est pas tenu chez vous : le score ne peut "
              "pas dépasser 30 %."),

    # ── 6 LA DOCUMENTATION ────────────────────────────────────────────────
    _e("notice", "6.1", "Notice d'utilisation", ("fournisseur",),
       "La notice d'utilisation porte-t-elle les sept informations de "
       "supervision que la norme y renvoie (voir le tableau de la "
       "documentation, dérivé de vos réponses) ?",
       "La notice est le seul véhicule par lequel les obligations "
       "dépendantes du déploiement passent au déployeur. Ce qu'elle ne dit "
       "pas reste sans porteur.",
       "Deux des sept éléments ne s'appliquent qu'aux systèmes "
       "d'identification biométrique à distance, et un seul quand vous "
       "n'implémentez pas les notifications : le tableau les affiche selon "
       "vos réponses.",
       2),
    _e("doc_technique", "6.2", "Documentation technique", ("fournisseur",),
       "La documentation technique porte-t-elle les sept éléments que la "
       "norme y renvoie (voir le tableau de la documentation, dérivé de vos "
       "réponses) ?",
       "C'est là que vivent les preuves : critères d'acceptation, résultats "
       "de vérification, démonstration de non-surcharge, justifications.",
       "Les déterminations de risque restent au dossier tenu au titre de "
       "prEN 18228 : c'est lui qui les porte. La documentation technique, "
       "elle, porte les preuves de conception et de vérification.",
       2),
    _e("notice_recue", "6.1", "Lecture de la notice d'utilisation reçue",
       ("deployeur",),
       "Avez-vous reçu de votre fournisseur une notice d'utilisation qui "
       "porte ces informations de supervision — et, si elle est muette sur "
       "l'un des points, l'avez-vous réclamé par écrit ?",
       "C'est votre levier. Une notice muette sur la supervision humaine "
       "est un écart du fournisseur à l'article 13, et vous êtes la seule "
       "partie qui puisse le constater avant l'autorité.",
       "Réclamer par écrit sert deux fois : à obtenir l'information, et à "
       "montrer plus tard que vous l'avez demandée.",
       3),
)

EXIGENCES_PAR_CLE = {e["cle"]: e for e in EXIGENCES}


# ═══════════════════════════════════════════════════════════════════════════
#  7. LA DOCUMENTATION, DÉRIVÉE — JAMAIS UNE LISTE FIXE
# ═══════════════════════════════════════════════════════════════════════════
#
# POURQUOI DÉRIVER PLUTÔT QUE LISTER : la norme renvoie sept éléments à la
# notice d'utilisation et sept à la documentation technique, mais TROIS de
# ces quatorze ne s'appliquent que sous condition — deux aux systèmes
# d'identification biométrique à distance, un lorsque le fournisseur
# n'implémente pas les notifications en temps réel. Une liste fixe de
# quatorze lignes ferait travailler un client sur des pièces qu'il n'a pas à
# produire ; une liste dérivée dit exactement ce qui lui est demandé.

#: (cle, où, ce qu'il faut y mettre, le paragraphe d'où ça vient, condition)
DOCUMENTATION = (
    ("mesures_deployeur", "notice",
     "Les mesures de supervision que le déployeur met en œuvre, et la "
     "documentation exigée pour chacune", "5.4.1", None),
    ("limites_residuel", "notice",
     "Les limites de ces mesures et le risque résiduel qui subsiste",
     "5.4.2", None),
    ("spec_notifications", "notice",
     "Les spécifications des notifications que le déployeur doit "
     "implémenter, puisque vous ne les implémentez pas", "5.4.3",
     "pas_de_notification_fournisseur"),
    ("competences_supposees", "notice",
     "Les compétences supposées des personnes désignées pour interpréter "
     "les sorties", "5.6.1", None),
    ("reversible", "notice",
     "Ce qui peut être annulé après exécution, et ce qui ne peut pas "
     "l'être", "5.7.4", None),
    ("seuils_confiance", "notice",
     "Les seuils sous lesquels un score de confiance déclenche une alerte",
     "5.8.2.3", "rbi"),
    ("competences_reviseurs", "notice",
     "Les compétences et la formation minimales des personnes chargées de "
     "la revue", "5.8.5", "rbi"),

    ("justif_notifications", "technique",
     "La justification de votre impossibilité à implémenter les "
     "notifications en temps réel, en renvoyant au délai de réaction",
     "6.2 a)", "pas_de_notification_fournisseur"),
    ("procedures_repli", "technique",
     "Comment la revue continue quand l'interface principale ou la "
     "journalisation tombe", "5.3.2.3", None),
    ("architecture_rbi", "technique",
     "L'architecture qui isole une sortie non revue, la preuve qu'elle "
     "fonctionne, ce qui rend les deux réviseurs indépendants, les essais "
     "correspondants, et ce que le déployeur peut configurer",
     "5.8.1 et 5.8.4", "rbi"),
    ("demo_surcharge", "technique",
     "La démonstration de non-surcharge lorsqu'une personne désignée "
     "supervise plusieurs scénarios", "5.2.5", None),
    ("critres_retro", "technique",
     "Ce que vous exigiez de la revue rétrospective pour l'accepter, et ce "
     "que la vérification a donné", "5.3.2.3.1", None),
    ("criteres_continue", "technique",
     "Ce que vous exigiez de la surveillance continue pour l'accepter, et "
     "ce que la vérification a donné", "5.3.4.4", None),
    ("ecarts_intervention", "technique",
     "La documentation des écarts de comportement du système après "
     "intervention", "5.7.1", None),
)


def documentation(rbi=False, notifications_fournisseur=True):
    """Ce que la notice d'utilisation et la documentation technique doivent
    porter, POUR CE SYSTÈME — pas pour un système en général."""
    out = {"notice": [], "technique": []}
    for cle, ou, quoi, clause, si in DOCUMENTATION:
        if si == "rbi" and not rbi:
            continue
        if si == "pas_de_notification_fournisseur" and notifications_fournisseur:
            continue
        out[ou].append({"cle": cle, "quoi": quoi, "clause": clause,
                        "conditionnel": si})
    return out


# ═══════════════════════════════════════════════════════════════════════════
#  8. L'ANNEXE ZA — CE QUE LA NORME COUVRE DE L'ARTICLE 14
# ═══════════════════════════════════════════════════════════════════════════
#
# C'EST LA SEULE PARTIE DU DOCUMENT QUI DIT CE QU'IL VAUT JURIDIQUEMENT, et
# c'est une annexe INFORMATIVE. Le module la reproduit comme une table de
# correspondance — des numéros d'articles en face de numéros de paragraphes,
# ce qu'un index fait — et il rappelle à chaque fois que la présomption
# n'existera qu'à la citation au Journal officiel.

ANNEXE_ZA = (
    ("14(1)", "Conception permettant une supervision humaine effective",
     ("5.2.1", "5.2.2", "5.2.3", "5.2.4", "5.2.5", "5.2.6", "5.3.1")),
    ("14(2)", "Prévention ou réduction des risques pour la santé, la "
              "sécurité et les droits fondamentaux",
     ("5.2.1", "5.2.2", "5.2.3", "5.2.4", "5.3.1")),
    ("14(3)(a)", "Mesures intégrées par le fournisseur avant la mise sur le "
                 "marché",
     ("5.3.2.1", "5.3.2.2", "5.3.2.3.1", "5.3.3.1", "5.3.3.2", "5.3.4.1",
      "5.3.4.2", "5.3.4.3", "5.3.4.4")),
    ("14(3)(b)", "Mesures identifiées par le fournisseur et mises en œuvre "
                 "par le déployeur",
     ("5.4.1", "5.4.2", "5.4.3")),
    ("14(4)(a)", "Comprendre les capacités et les limites, et surveiller le "
                 "fonctionnement",
     ("5.3.3.1", "5.3.3.2", "5.3.4.1", "5.3.4.2", "5.3.4.3", "5.3.4.4",
      "5.6.1")),
    ("14(4)(b)", "Rester conscient du biais d'automatisation", ("5.5.1",)),
    ("14(4)(c)", "Interpréter correctement les sorties", ("5.6.1",)),
    ("14(4)(d)", "Décider de ne pas utiliser le système, ou ignorer, "
                 "outrepasser ou inverser une sortie",
     ("5.7.1", "5.7.2", "5.7.3", "5.7.4")),
    ("14(4)(e)", "Interrompre le système ou l'arrêter",
     ("5.7.1", "5.7.5")),
    ("14(5)", "Vérification séparée par au moins deux personnes physiques "
              "(identification biométrique à distance)",
     ("5.8.1", "5.8.2.1", "5.8.2.2", "5.8.2.3", "5.8.2.4", "5.8.3", "5.8.4",
      "5.8.5")),
)

#: Les alinéas qui ne concernent QUE l'identification biométrique à distance.
ZA_RBI = ("14(5)",)


def couverture_article_14(reponses, rbi=False):
    """Pour chaque alinéa de l'article 14, l'état de ce qui le couvre.

    LA GRANULARITÉ EST CELLE DE L'ANNEXE ZA, PAS CELLE DU QUESTIONNAIRE : un
    alinéa est couvert quand TOUS les paragraphes que l'annexe lui associe
    sont tenus. Dire « 80 % de l'article 14 » n'aurait aucun sens — un
    alinéa n'est pas tenu à 80 %.
    """
    reponses = reponses if isinstance(reponses, dict) else {}
    # Le paragraphe est tenu si TOUTES les exigences qui le citent le sont.
    par_clause = {}
    for ex in EXIGENCES:
        par_clause.setdefault(ex["clause"], []).append(ex)
    out = []
    for alinea, titre, clauses in ANNEXE_ZA:
        if alinea in ZA_RBI and not rbi:
            out.append({"alinea": alinea, "titre": titre, "clauses": clauses,
                        "etat": "sans_objet",
                        "dit": "Ne concerne que les systèmes "
                               "d'identification biométrique à distance."})
            continue
        tenues, manquantes, inconnues = [], [], []
        for c in clauses:
            exs = par_clause.get(c) or []
            if not exs:
                inconnues.append(c)
                continue
            for ex in exs:
                if ex["si"] == "rbi" and not rbi:
                    continue
                r = reponses.get(ex["cle"])
                if r is True:
                    tenues.append(ex["cle"])
                elif r is False:
                    manquantes.append(ex["cle"])
                else:
                    inconnues.append(ex["cle"])
        if manquantes:
            etat, dit = "non_couvert", ("%d exigence(s) du questionnaire qui "
                                        "portent cet alinéa sont déclarées "
                                        "non tenues." % len(manquantes))
        elif inconnues:
            etat, dit = "sans_reponse", ("%d exigence(s) qui portent cet "
                                         "alinéa n'ont pas de réponse."
                                         % len(inconnues))
        elif tenues:
            etat, dit = "couvert", ("Les %d exigences qui portent cet alinéa "
                                    "sont déclarées tenues." % len(tenues))
        else:
            etat, dit = "sans_reponse", "Aucune exigence applicable trouvée."
        out.append({"alinea": alinea, "titre": titre, "clauses": clauses,
                    "etat": etat, "dit": dit, "tenues": len(tenues),
                    "manquantes": len(manquantes),
                    "sans_reponse": len(inconnues)})
    return out


# ═══════════════════════════════════════════════════════════════════════════
#  9. LE SCORE — COMPOSÉ, PUIS PLAFONNÉ PAR SES VERROUS
# ═══════════════════════════════════════════════════════════════════════════
#
# LA MÊME DOCTRINE QUE LE TAUX DE CONFORMITÉ DU SITE, POUR LA MÊME RAISON :
# une moyenne pondérée seule permet d'afficher 85 % en ayant manqué le point
# qui fait tenir tous les autres. Un verrou ne retire pas des points, il
# POSE UN PLAFOND : tant qu'il n'est pas levé, le score ne monte pas au-delà,
# quel que soit le reste. Et le plafond se NOMME, avec la raison.
#
# LE SCORE NE COMPTE QUE CE QUI EST APPLICABLE : une exigence sans objet
# (RBI sur un système qui n'en est pas) ne pèse ni au numérateur ni au
# dénominateur. La compter au dénominateur ferait baisser le score de qui
# n'a rien à faire.

#: Ce qu'une réponse peut valoir. LE « PARTIEL » EXISTE PARCE QUE LE TERRAIN
#: l'impose : une interface de revue qui porte quatre des cinq éléments
#: attendus n'est ni tenue ni absente.
VALEURS = {True: 1.0, "partiel": 0.5, False: 0.0}


def applicables(role, rbi=False, notifications_fournisseur=True):
    """Les exigences qui s'adressent à CE rôle pour CE système."""
    role = role if role in ROLES else "fournisseur"
    out = []
    for ex in EXIGENCES:
        if role not in ex["role"]:
            continue
        if ex["si"] == "rbi" and not rbi:
            continue
        if ex["si"] == "pas_de_notification_fournisseur" \
                and notifications_fournisseur:
            continue
        out.append(ex)
    return tuple(out)


def _valeur(r):
    """La valeur d'une réponse, ou None si elle n'a pas été donnée.

    « PAS ENCORE RÉPONDU » N'EST PAS « NON » : c'est la leçon du module de
    maturité. Une réponse absente ne compte pas comme un échec, elle compte
    comme une question ouverte — et le score dit sur combien de questions il
    porte.
    """
    if r is True or r is False:
        return VALEURS[r]
    if isinstance(r, str) and r.strip().lower() in ("partiel", "partiellement"):
        return VALEURS["partiel"]
    return None


def score(role, reponses, rbi=False, notifications_fournisseur=True,
          scenarios=None):
    """Le score de conformité de CE rôle, et les plafonds qui le tiennent."""
    reponses = reponses if isinstance(reponses, dict) else {}
    exs = applicables(role, rbi, notifications_fournisseur)
    poids_total = sum(e["poids"] for e in exs)
    acquis, repondues, sans_reponse = 0.0, 0, []
    for ex in exs:
        v = _valeur(reponses.get(ex["cle"]))
        if v is None:
            sans_reponse.append(ex["cle"])
            continue
        repondues += 1
        acquis += v * ex["poids"]
    brut = int(round(100.0 * acquis / poids_total)) if poids_total else 0

    # ── LES VERROUS, ET LEUR PLAFOND ─────────────────────────────────────
    verrous = []
    for ex in exs:
        if not ex["verrou"]:
            continue
        v = _valeur(reponses.get(ex["cle"]))
        if v == 1.0:
            continue
        plafond = _plafond_du_texte(ex["verrou"])
        verrous.append({"cle": ex["cle"], "clause": ex["clause"],
                        "titre": ex["titre"], "plafond": plafond,
                        "dit": ex["verrou"],
                        "repondu": v is not None})

    # ── LE VERROU QUI NE VIENT PAS D'UNE CASE, MAIS DE L'ARITHMÉTIQUE ────
    #
    # UN SCÉNARIO DONT LA MESURE NE TIENT PAS LE DÉLAI, ET DONT
    # L'IMPOSSIBILITÉ N'EST PAS CONSIGNÉE, est le défaut que la norme refuse
    # nommément. Il ne se voit dans aucune réponse par oui ou non : il se
    # calcule. C'est le seul verrou du module qu'une case ne peut pas lever.
    if role == "fournisseur":
        casses = [s for s in (scenarios or [])
                  if s.get("etat") == "impossible_non_consignee"]
        if casses:
            noms = [s.get("nom") or "(sans nom)" for s in casses[:4]]
            verrous.append({
                "cle": "scenario_sans_intervention_possible",
                "clause": "5.2.3 et 5.2.4", "titre": "Adéquation des mesures "
                "au délai de réaction", "plafond": 50,
                #  L'ACCORD SUIT LE NOMBRE, y compris au singulier : « 1
                #  scénario ont une latence » se lit dans un rapport remis.
                "dit": "%d scénario%s — %s — %s une latence d'intervention "
                       "supérieure à %s délai de réaction sans que "
                       "l'impossibilité technique soit consignée. La norme "
                       "refuse ce cas nommément : le score ne peut pas "
                       "dépasser 50 %%."
                       % (len(casses), "s" if len(casses) > 1 else "",
                          ", ".join("« %s »" % n for n in noms),
                          "ont" if len(casses) > 1 else "a",
                          "leur" if len(casses) > 1 else "son"),
                "repondu": True})

    plafond = min([v["plafond"] for v in verrous], default=100)
    return {"brut": brut, "taux": min(brut, plafond), "plafond": plafond,
            "verrous": verrous, "poids_total": poids_total,
            "acquis": round(acquis, 2), "applicables": len(exs),
            "repondues": repondues, "sans_reponse": sans_reponse,
            "complet": not sans_reponse}


def _plafond_du_texte(texte):
    """Le plafond que le verrou annonce, lu DANS son propre texte.

    POURQUOI LIRE LE TEXTE PLUTÔT QUE PORTER UN SECOND CHAMP : deux champs
    dérivent. Un verrou qui annoncerait « 25 % » à l'écran en plafonnant à
    40 % dans le calcul serait un mensonge invisible — et c'est exactement le
    genre de défaut qu'une relecture ne voit pas.
    """
    import re
    m = re.search(r"(\d{1,3})\s*%", texte or "")
    return int(m.group(1)) if m else 100


# ═══════════════════════════════════════════════════════════════════════════
#  10. L'ANALYSE COMPLÈTE, ET LE PLAN QUI EN DÉCOULE
# ═══════════════════════════════════════════════════════════════════════════

#: L'ordre dans lequel un plan d'action se tient. CE N'EST PAS L'ORDRE DES
#: PARAGRAPHES : on ne conçoit pas une interface avant de savoir quel délai
#: elle doit tenir. Les verrous d'abord, puis la calibration, puis les
#: mesures, puis leur vérification, puis la documentation.
ETAPES_PLAN = (
    ("verrous", "Lever les verrous",
     "Ces points plafonnent le score : rien d'autre ne le fera monter tant "
     "qu'ils tiennent."),
    ("calibrer", "Calibrer sur les risques",
     "Les scénarios, les délais de réaction et la sélection des mesures — "
     "tout le reste se justifie par rapport à eux."),
    ("mesures", "Concevoir les mesures",
     "Les interfaces, les notifications et les fonctions d'intervention."),
    ("verifier", "Vérifier",
     "Ce qui sépare une conception d'une mesure qui fonctionne : critères "
     "d'acceptation, essais, résultats."),
    ("documenter", "Documenter",
     "Les deux pièces remises — notice d'utilisation, documentation "
     "technique : c'est là que "
     "la conformité devient démontrable."),
)

#: À quelle étape appartient chaque paragraphe. LA TABLE EST EXPLICITE parce
#: qu'une règle déduite du numéro se tromperait : 5.4.1 est une exigence de
#: documentation pour le fournisseur et une exigence de mise en œuvre pour le
#: déployeur.
_ETAPE_DE = {
    "scenarios": "calibrer", "delai": "calibrer", "selection": "calibrer",
    "impossibilite": "calibrer", "surcharge": "calibrer",
    "revue_affectations": "verifier",
    "retro_interface": "mesures", "retro_parametres": "mesures",
    "retro_verif": "verifier",
    "alerte_conception": "mesures", "alerte_exigences": "mesures",
    "continue_generales": "mesures", "continue_ihm": "mesures",
    "continue_fonctionnalite": "mesures", "continue_verif": "verifier",
    "deploy_specification": "documenter", "deploy_residuel": "documenter",
    "deploy_notifications": "documenter",
    "deploy_mise_en_oeuvre": "mesures", "deploy_verification": "verifier",
    "deploy_conditions": "calibrer",
    "biais_conception": "mesures", "biais_tests": "verifier",
    "biais_deployeur": "mesures",
    "interpretation": "mesures", "entrainement": "documenter",
    "competences_deployeur": "mesures",
    "categories": "calibrer",
    "fonctions": "mesures", "etat_sur": "mesures",
    "negligence": "mesures", "ecrasement": "mesures", "retour": "mesures",
    "comportement_apres": "verifier",
    "rbi_prevention": "mesures", "rbi_statuts": "mesures",
    "rbi_informations": "mesures", "rbi_interface": "mesures",
    "rbi_entrees": "mesures", "rbi_independance": "mesures",
    "rbi_documentation": "documenter", "rbi_competences": "documenter",
    "rbi_deployeur": "mesures",
    "notice": "documenter", "doc_technique": "documenter",
    "notice_recue": "documenter",
}


def plan(role, reponses, rbi=False, notifications_fournisseur=True,
         scenarios=None):
    """Le plan d'action, DÉRIVÉ des écarts — jamais une liste générique.

    Ce que le plan porte et qu'une liste de paragraphes ne porte pas : les
    verrous en tête, avec leur plafond chiffré, puis les écarts par étape,
    chacun avec le paragraphe qui le fonde et le piège du terrain.
    """
    reponses = reponses if isinstance(reponses, dict) else {}
    s = score(role, reponses, rbi, notifications_fournisseur, scenarios)
    par_etape = {c: [] for c, _n, _d in ETAPES_PLAN}
    cles_verrouillees = {v["cle"] for v in s["verrous"]}

    for v in s["verrous"]:
        par_etape["verrous"].append({
            "cle": v["cle"], "clause": v["clause"], "titre": v["titre"],
            "quoi": v["dit"], "plafond": v["plafond"], "poids": 3})

    for ex in applicables(role, rbi, notifications_fournisseur):
        if ex["cle"] in cles_verrouillees:
            continue
        v = _valeur(reponses.get(ex["cle"]))
        if v == 1.0:
            continue
        etape = _ETAPE_DE.get(ex["cle"], "mesures")
        par_etape[etape].append({
            "cle": ex["cle"], "clause": ex["clause"], "titre": ex["titre"],
            "quoi": ex["question"], "piege": ex["piege"],
            "poids": ex["poids"],
            "etat": "partiel" if v == 0.5
                    else ("absent" if v == 0.0 else "sans_reponse")})

    # Les scénarios cassés entrent dans l'étape « calibrer » avec leur
    # arithmétique : c'est là qu'ils se réparent.
    for sc in (scenarios or []):
        if sc.get("etat") in ("tient", "impossible_consignee"):
            continue
        for m in (sc.get("manque") or []):
            par_etape["calibrer"].append({
                "cle": "scenario", "clause": "5.2.2 et 5.2.3",
                "titre": "Scénario « %s »" % (sc.get("nom") or "sans nom"),
                "quoi": m, "piege": None, "poids": 3, "etat": sc["etat"]})

    etapes = []
    for cle, nom, dit in ETAPES_PLAN:
        lignes = sorted(par_etape[cle], key=lambda x: -x["poids"])
        if lignes:
            etapes.append({"cle": cle, "nom": nom, "dit": dit,
                           "lignes": lignes})
    return {"etapes": etapes,
            "total": sum(len(e["lignes"]) for e in etapes)}


def analyse(d):
    """Le cadre d'analyse complet, pour un système et un rôle.

    Ce que la fonction rend tient en six parties : le rôle et ce qu'il porte,
    les scénarios de risque avec leur arithmétique, le questionnaire avec ses
    réponses, le score et ses plafonds, la documentation dérivée, et la
    couverture de l'article 14 alinéa par alinéa.
    """
    d = d if isinstance(d, dict) else {}
    role = d.get("role") if d.get("role") in ROLES else "fournisseur"
    rbi = bool(d.get("rbi"))
    notif = d.get("notifications_fournisseur")
    notif = True if notif is None else bool(notif)
    reponses = d.get("reponses") if isinstance(d.get("reponses"), dict) else {}

    scs = [scenario(x) for x in (d.get("scenarios") or [])
           if isinstance(x, dict)]
    s = score(role, reponses, rbi, notif, scs)

    # LE COMPTE DES SCÉNARIOS PAR ÉTAT, parce qu'un total ne dit pas lequel.
    par_etat = {}
    for sc in scs:
        par_etat[sc["etat"]] = par_etat.get(sc["etat"], 0) + 1

    return {
        "ok": True,
        "source": SOURCE,
        "role": dict(ROLES[role], cle=role),
        "rbi": rbi,
        "notifications_fournisseur": notif,
        "scenarios": scs,
        "scenarios_par_etat": par_etat,
        "exigences": [
            dict(ex, reponse=reponses.get(ex["cle"]),
                 valeur=_valeur(reponses.get(ex["cle"])))
            for ex in applicables(role, rbi, notif)],
        "score": s,
        "documentation": documentation(rbi, notif),
        "article_14": couverture_article_14(reponses, rbi),
        "plan": plan(role, reponses, rbi, notif, scs),
        # LA RÉSERVE SE DIT À CHAQUE RÉPONSE, pas une fois dans un coin.
        "reserve": "Ce score dit que ce que la norme attend est déclaré et "
                   "que l'arithmétique du délai de réaction tient. Il ne "
                   "vaut pas présomption de conformité : %s"
                   % SOURCE["presomption_dit"],
    }


def evaluer(declaration):
    """Le taux de ce référentiel, dans le format que le taux de conformité
    du site attend.

    LES DEUX RÔLES NE SE MOYENNENT PAS. Un organisme qui est fournisseur ET
    déployeur porte deux jeux d'obligations distincts ; le taux affiché est
    celui du PLUS FAIBLE des deux, parce qu'un score global calculé sur la
    réunion des deux questionnaires cacherait le côté défaillant derrière le
    côté tenu. La carte nomme le rôle qui commande.
    """
    d = declaration if isinstance(declaration, dict) else {}
    rbi = bool(d.get("rbi"))
    notif = d.get("notifications_fournisseur")
    notif = True if notif is None else bool(notif)
    scs = [scenario(x) for x in (d.get("scenarios") or [])
           if isinstance(x, dict)]

    #  LES RÔLES DÉCLARÉS, ET RIEN D'AUTRE. Un rôle qu'on n'a pas endossé ne
    #  se note pas : il n'entre ni au numérateur ni au dénominateur.
    roles = [r for r in ("fournisseur", "deployeur")
             if isinstance(d.get(r), dict) and d[r]]
    if not roles:
        return {"ok": False, "motif": "aucun_role_declare",
                "dit": "Choisissez votre rôle — fournisseur, déployeur, ou "
                       "les deux — et répondez à son questionnaire."}

    par_role = {}
    for r in roles:
        par_role[r] = score(r, d[r], rbi, notif, scs if r == "fournisseur"
                            else None)
    commande = min(roles, key=lambda r: par_role[r]["taux"])

    verrous = []
    for r in roles:
        for v in par_role[r]["verrous"]:
            verrous.append(dict(v, role=ROLES[r]["nom"]))

    return {
        "ok": True,
        "taux": par_role[commande]["taux"],
        "roles": {r: par_role[r] for r in roles},
        "role_commande": commande,
        "role_commande_nom": ROLES[commande]["nom"],
        "rbi": rbi,
        "scenarios": len(scs),
        "scenarios_casses": len([x for x in scs if x["etat"]
                                 == "impossible_non_consignee"]),
        "verrous": verrous,
        "certifiable": False,
        "article_14": couverture_article_14(d.get(commande) or {}, rbi),
        "reserve": "Rien ne se certifie contre prEN 18229-3 : ce taux dit la "
                   "supervision humaine déclarée au regard d'un projet de "
                   "norme. %s" % SOURCE["presomption_dit"],
    }


def referentiel():
    """Ce que l'écran a besoin de savoir avant la première réponse."""
    return {
        "source": SOURCE,
        "famille": [{"norme": n, "titre": t, "porte": p, "socle": s}
                    for n, t, p, s in FAMILLE],
        "roles": {c: dict(v, cle=c) for c, v in ROLES.items()},
        "categories": [CATEGORIES_PAR_CLE[c[0]] for c in CATEGORIES],
        "fonctions": [FONCTIONS_PAR_CLE[f[0]] for f in FONCTIONS],
        "unites": {c: {"nom": n, "ms": m} for c, (n, m) in UNITES.items()},
        "etats_scenario": ETATS_SCENARIO,
        "exigences": [dict(e) for e in EXIGENCES],
        "documentation": [{"cle": c, "ou": o, "quoi": q, "clause": cl,
                           "conditionnel": si}
                          for c, o, q, cl, si in DOCUMENTATION],
        "annexe_za": [{"alinea": a, "titre": t, "clauses": cl}
                      for a, t, cl in ANNEXE_ZA],
        "etapes_plan": [{"cle": c, "nom": n, "dit": d}
                        for c, n, d in ETAPES_PLAN],
    }


# ═══════════════════════════════════════════════════════════════════════════
#  11. LE CONTRÔLE DU MODULE — IL ÉCHOUE À L'IMPORT, PAS EN PRODUCTION
# ═══════════════════════════════════════════════════════════════════════════

def _verifier():
    fautes = []

    # ── LA LICENCE, QUI COMMANDE LA FORME DU MODULE ───────────────────────
    if "DROIT D'AUTEUR" not in SOURCE.get("licence", "").upper():
        fautes.append("la licence de la source ne nomme plus le droit "
                      "d'auteur du CEN")
    if SOURCE.get("reproduction") is not False:
        fautes.append("la source déclare reproduire le texte normatif")
    if SOURCE.get("presomption") is not False:
        fautes.append("la source annonce une présomption de conformité que "
                      "la citation au Journal officiel n'a pas encore "
                      "ouverte")

    # ── LES TROIS CATÉGORIES, ET LEUR ORDRE DE LATENCE ────────────────────
    if len(CATEGORIES) != 3:
        fautes.append("les catégories de mesure ne sont plus trois : %d"
                      % len(CATEGORIES))
    rangs = [c[6] for c in CATEGORIES]
    if sorted(rangs, reverse=True) != rangs or len(set(rangs)) != len(rangs):
        fautes.append("les catégories ne sont plus rangées par latence "
                      "décroissante, ou deux partagent un rang : %s" % rangs)
    # CE QUE CETTE RÈGLE ATTRAPE : une revue rétrospective qui passerait
    # devant la surveillance continue rendrait le conseil du moteur faux —
    # il proposerait de « relever » vers une catégorie plus lente.
    if CATEGORIES_PAR_CLE["retrospective"]["rang"] \
            >= CATEGORIES_PAR_CLE["continue"]["rang"]:
        fautes.append("la revue rétrospective est rangée aussi vite que la "
                      "surveillance continue")

    # ── LES QUATRE FONCTIONS, ET LA RÈGLE DE COMPOSITION ──────────────────
    if len(FONCTIONS) != 4:
        fautes.append("les fonctions d'intervention ne sont plus quatre : %d"
                      % len(FONCTIONS))
    if len(FONCTIONS_SUR_SORTIE) != 3:
        fautes.append("les fonctions qui portent sur une sortie ne sont plus "
                      "trois : %s" % (FONCTIONS_SUR_SORTIE,))
    if FONCTIONS_PAR_CLE.get(FONCTION_SYSTEME, {}).get("porte_sur") != "systeme":
        fautes.append("la fonction qui porte sur le système n'est plus "
                      "l'état sécurisé")

    # ── LES EXIGENCES ─────────────────────────────────────────────────────
    if len(EXIGENCES_PAR_CLE) != len(EXIGENCES):
        fautes.append("deux exigences portent la même clé : %d clés pour %d "
                      "entrées" % (len(EXIGENCES_PAR_CLE), len(EXIGENCES)))
    for ex in EXIGENCES:
        if not ex["clause"] or not ex["clause"][0].isdigit():
            fautes.append("%s ne cite pas un numéro de paragraphe : %r"
                          % (ex["cle"], ex["clause"]))
        if not ex["titre"]:
            fautes.append("%s ne cite pas le titre de son paragraphe"
                          % ex["cle"])
        if not set(ex["role"]) <= set(ROLES):
            fautes.append("%s s'adresse à un rôle inconnu : %s"
                          % (ex["cle"], ex["role"]))
        if not ex["role"]:
            fautes.append("%s ne s'adresse à personne" % ex["cle"])
        if ex["poids"] not in (1, 2, 3):
            fautes.append("%s a un poids hors de 1 à 3 : %r"
                          % (ex["cle"], ex["poids"]))
        if ex["si"] not in (None, "rbi", "pas_de_notification_fournisseur"):
            fautes.append("%s porte une condition inconnue : %r"
                          % (ex["cle"], ex["si"]))
        # LA QUESTION EST UNE QUESTION. Une affirmation dans un questionnaire
        # se répond par « oui » sans que personne ait vérifié quoi.
        if not ex["question"].rstrip().endswith("?"):
            fautes.append("%s n'est pas posée comme une question" % ex["cle"])
        if ex["verrou"] and "%" not in ex["verrou"]:
            fautes.append("le verrou de %s n'annonce pas son plafond"
                          % ex["cle"])
        if ex["cle"] not in _ETAPE_DE:
            fautes.append("%s n'a pas d'étape dans le plan" % ex["cle"])

    # LES DEUX RÔLES ONT CHACUN DE QUOI RÉPONDRE. Un rôle sans exigence
    # rendrait un score de 0 sur 0, c'est-à-dire un écran vide.
    for role in ROLES:
        if not applicables(role):
            fautes.append("le rôle %s n'a aucune exigence applicable" % role)
        if not [e for e in EXIGENCES if role in e["role"] and e["verrou"]]:
            fautes.append("le rôle %s n'a aucun verrou : son score ne serait "
                          "jamais plafonné" % role)

    # ── LES ÉTAPES DU PLAN ────────────────────────────────────────────────
    connues = {c for c, _n, _d in ETAPES_PLAN}
    for cle, etape in _ETAPE_DE.items():
        if etape not in connues:
            fautes.append("%s pointe une étape de plan inconnue : %r"
                          % (cle, etape))
        if cle not in EXIGENCES_PAR_CLE:
            fautes.append("la table des étapes nomme %s, qui n'est pas une "
                          "exigence" % cle)
    if ETAPES_PLAN[0][0] != "verrous":
        fautes.append("le plan ne commence plus par les verrous")

    # ── L'ANNEXE ZA, ET SES DIX ALINÉAS ───────────────────────────────────
    if len(ANNEXE_ZA) != 10:
        fautes.append("l'annexe ZA ne compte plus dix alinéas : %d"
                      % len(ANNEXE_ZA))
    clauses_du_questionnaire = {ex["clause"] for ex in EXIGENCES}
    for alinea, _t, clauses in ANNEXE_ZA:
        if not clauses:
            fautes.append("l'alinéa %s ne renvoie à aucun paragraphe"
                          % alinea)
        # CE QUE CETTE RÈGLE ATTRAPE, ET QU'UN COMPTE N'ATTRAPE PAS : un
        # alinéa de l'article 14 qui renverrait à un paragraphe qu'aucune
        # question du cadre ne couvre serait déclaré « couvert » par un
        # questionnaire qui ne le mesure pas.
        orphelines = [c for c in clauses if c not in clauses_du_questionnaire]
        if orphelines:
            fautes.append("l'alinéa %s renvoie à %s, qu'aucune question du "
                          "cadre ne couvre" % (alinea, orphelines))
    if "14(5)" not in ZA_RBI:
        fautes.append("l'alinéa 14(5) n'est plus réservé aux systèmes "
                      "d'identification biométrique à distance")

    # ── LA DOCUMENTATION ──────────────────────────────────────────────────
    cles_doc = [c for c, _o, _q, _cl, _si in DOCUMENTATION]
    if len(set(cles_doc)) != len(cles_doc):
        fautes.append("deux éléments de documentation portent la même clé")
    for ou, attendu in (("notice", 7), ("technique", 7)):
        n = len([1 for _c, o, _q, _cl, _si in DOCUMENTATION if o == ou])
        if n != attendu:
            fautes.append("la %s porte %d éléments au lieu de %d"
                          % (ou, n, attendu))
    for _c, ou, _q, _cl, si in DOCUMENTATION:
        if ou not in ("notice", "technique"):
            fautes.append("un élément de documentation va dans %r" % ou)
        if si not in (None, "rbi", "pas_de_notification_fournisseur"):
            fautes.append("un élément de documentation porte une condition "
                          "inconnue : %r" % si)
    # LA DOCUMENTATION SE DÉRIVE VRAIMENT : un système sans RBI et dont le
    # fournisseur implémente ses notifications doit en porter MOINS.
    court = documentation(False, True)
    long_ = documentation(True, False)
    if len(court["notice"]) >= len(long_["notice"]) \
            or len(court["technique"]) >= len(long_["technique"]):
        fautes.append("la documentation ne se dérive plus des conditions : "
                      "le cas court porte autant que le cas complet")

    # ── LES UNITÉS, ET LEUR CONVERSION ────────────────────────────────────
    if en_ms(1, "s") != 1000 or en_ms(1, "min") != 60000 \
            or en_ms(1, "h") != 3600000 or en_ms(1, "j") != 86400000:
        fautes.append("la conversion des unités de durée est fausse")
    if en_ms("", "s") is not None or en_ms(1, "semaine") is not None:
        fautes.append("une durée vide ou une unité inconnue ne rend plus None")

    # ── L'ARITHMÉTIQUE QUI PORTE LE MODULE ────────────────────────────────
    #
    # LE MODULE SE MESURE LUI-MÊME SUR LE CAS QUI LE JUSTIFIE : un délai
    # court tenu par une revue rétrospective doit tomber, et le même cas
    # consigné au titre du 5.2.4 doit être reconnu.
    court_delai = {"nom": "contrôle", "delai": 200, "delai_unite": "ms",
                   "latence": 4, "latence_unite": "s",
                   "categories": ["retrospective"]}
    if scenario(court_delai)["etat"] != "impossible_non_consignee":
        fautes.append("une revue rétrospective qui dépasse un délai de 200 ms "
                      "n'est plus signalée")
    if scenario(dict(court_delai, impossibilite_consignee=True))["etat"] \
            != "impossible_consignee":
        fautes.append("l'impossibilité technique consignée n'est plus "
                      "reconnue")
    long_delai = dict(court_delai, delai=2, delai_unite="h", latence=20,
                      latence_unite="min")
    if scenario(long_delai)["etat"] != "tient":
        fautes.append("une revue rétrospective qui tient un délai de deux "
                      "heures est refusée")

    # LE PLAFOND ANNONCÉ EST LE PLAFOND APPLIQUÉ. Deux chiffres qui dérivent
    # sont un mensonge invisible : l'écran dirait 25 %, le calcul 40 %.
    for ex in EXIGENCES:
        if not ex["verrou"]:
            continue
        p = _plafond_du_texte(ex["verrou"])
        if not 1 <= p <= 99:
            fautes.append("le verrou de %s annonce un plafond hors de 1 à "
                          "99 %% : %d" % (ex["cle"], p))
        tout = {e["cle"]: True for e in EXIGENCES if e["cle"] != ex["cle"]}
        role = "fournisseur" if "fournisseur" in ex["role"] else "deployeur"
        s = score(role, tout, rbi=True, notifications_fournisseur=False)
        if s["taux"] > p:
            fautes.append("le verrou de %s annonce %d %% mais le score monte "
                          "à %d %%" % (ex["cle"], p, s["taux"]))

    if fautes:
        raise RuntimeError("en18229_3 — table incohérente : "
                           + " ; ".join(fautes))
    return fautes


_FAUTES = _verifier()
