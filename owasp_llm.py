# -*- coding: utf-8 -*-
"""LE TOP 10 OWASP POUR LES APPLICATIONS LLM — ET CE QU'AUCUNE NORME NE COUVRE.

═══ CE QUE C'EST, ET CE QUE CE N'EST PAS ════════════════════════════════
Une liste de dix risques, tenue par l'OWASP, millésime 2025. Ce n'est ni une
norme, ni un référentiel certifiable, ni une méthode d'analyse de risque :
c'est un inventaire de ce qui casse le plus souvent, classé par fréquence
constatée. On ne s'y conforme pas — on s'en sert pour vérifier qu'on n'a rien
oublié d'évident.

ELLE SE PÉRIME VITE, ET C'EST SA QUALITÉ. Le millésime 2023 ne portait ni la
fuite d'invite système, ni les faiblesses des bases vectorielles, ni la
consommation non bornée. Citer « le Top 10 OWASP LLM » sans son millésime,
c'est citer une liste qu'on n'a pas relue.

═══ LE PONT QUI DONNE SA VALEUR AU MODULE ═══════════════════════════════
CHAQUE RISQUE EST RATTACHÉ AUX MESURES DE L'ANNEXE A D'ISO/IEC 42001 QUI LE
TOUCHENT — par NUMÉRO, jamais par recopie : la norme est sous droits, et ce
cabinet cite les numéros et les titres sans reproduire les exigences.

ET LE RÉSULTAT INTÉRESSANT EST L'INVERSE DU PONT. Ce qui se vend, c'est
« notre SMIA couvre OWASP ». Ce qui est vrai, c'est que plusieurs de ces
risques ne rencontrent AUCUNE mesure de l'annexe A — parce qu'ils sont
d'ordre applicatif et que 42001 est un système de management. Une maison
certifiée 42001 qui en conclut qu'elle a traité le Top 10 se trompe, et le
module nomme exactement sur quoi.

═══ CE QUI N'A PAS PU ÊTRE VÉRIFIÉ DEPUIS CET ENVIRONNEMENT ═════════════
owasp.org, top10.owasp.org et genai.owasp.org sont tous refusés par le
mandataire de sortie de la machine de construction. La liste ci-dessous n'a
donc PAS pu être recoupée avec la publication en ligne au moment de l'écrire.
Elle est déclarée telle quelle dans `A_VERIFIER`, et la vue l'affiche — un
référentiel qu'on n'a pas pu rouvrir se signale, il ne se présente pas comme
vérifié.
"""
import iso42001


SOURCE = {
    "nom": "OWASP Top 10 for Large Language Model Applications",
    "millesime": "2025",
    "tenu_par": "OWASP Foundation",
    "lien": "https://top10.owasp.org/2025/",
    "licence": "Creative Commons — se cite et s'adapte avec attribution.",
    "certifiable": False,
    "dit": "Un inventaire des défaillances les plus fréquentes, pas un "
           "référentiel de conformité. « Conforme OWASP » ne veut rien dire.",
}

A_VERIFIER = {
    "quoi": "La liste des dix risques et leurs intitulés 2025.",
    "pourquoi": "owasp.org, top10.owasp.org et genai.owasp.org sont refusés "
                "par le mandataire de sortie de l'environnement de "
                "construction : la liste n'a pas pu être recoupée avec la "
                "publication en ligne.",
    "quoi_faire": "Rouvrir https://top10.owasp.org/2025/ depuis un poste "
                  "ordinaire et confirmer les dix intitulés avant de "
                  "présenter cette vue à un client.",
}


# ═══════════════════════════════════════════════════════════════════════════
#  LES DIX
# ═══════════════════════════════════════════════════════════════════════════
#
# L'ORDRE EST CELUI DE LA PUBLICATION, et il vaut classement : LLM01 est le
# plus fréquemment rencontré. Le réordonner par gravité ressentie ferait
# perdre la seule information que la liste apporte en propre.

RISQUES = (
    {"cle": "LLM01", "nom": "Injection d'invite",
     "en": "Prompt Injection",
     "quoi": "Le contenu lu par le modèle — document, page, ticket, "
             "description d'outil — porte des instructions qu'il exécute "
             "comme si elles venaient de l'utilisateur.",
     "pourquoi_ca_dure": "Rien ne distingue, dans une invite, la consigne de "
                         "la donnée. C'est une propriété du procédé : aucun "
                         "correctif ne la fera disparaître, et tout ce qui "
                         "se construit ici est de l'atténuation.",
     "iso42001": ("A.6.2.6", "A.6.2.8", "A.9.4"),
     "couvert_par_la_norme": "partiellement"},
    {"cle": "LLM02", "nom": "Divulgation d'informations sensibles",
     "en": "Sensitive Information Disclosure",
     "quoi": "Le modèle rend des données qu'il n'aurait pas dû rendre : "
             "données personnelles, secrets, contenus d'un autre client.",
     "pourquoi_ca_dure": "La donnée entre par trois portes — l'entraînement, "
                         "le contexte récupéré, l'invite — et l'atténuation "
                         "de l'une ne couvre pas les deux autres.",
     "iso42001": ("A.7.3", "A.7.5", "A.8.2"),
     "couvert_par_la_norme": "partiellement"},
    {"cle": "LLM03", "nom": "Chaîne d'approvisionnement",
     "en": "Supply Chain",
     "quoi": "Le modèle, un adaptateur, une bibliothèque ou un jeu de "
             "données arrive déjà compromis.",
     "pourquoi_ca_dure": "Un poids se télécharge comme une image de "
                         "conteneur, sans rien de l'outillage de "
                         "vérification qui existe pour le logiciel.",
     "iso42001": ("A.4.2", "A.4.3", "A.10.3"),
     "couvert_par_la_norme": "oui"},
    {"cle": "LLM04", "nom": "Empoisonnement des données et du modèle",
     "en": "Data and Model Poisoning",
     "quoi": "Ce qui a été introduit dans les données d'entraînement ou "
             "d'ajustement oriente le comportement du modèle.",
     "pourquoi_ca_dure": "La collecte est massive, la relecture ne l'est "
                         "pas, et l'effet n'apparaît qu'à l'usage.",
     "iso42001": ("A.7.2", "A.7.4", "A.7.6"),
     "couvert_par_la_norme": "oui"},
    {"cle": "LLM05", "nom": "Traitement incorrect des sorties",
     "en": "Improper Output Handling",
     "quoi": "La sortie du modèle est reprise telle quelle par le système "
             "d'aval — requête, commande, page rendue — sans être traitée "
             "comme une entrée non fiable.",
     "pourquoi_ca_dure": "Le texte produit ressemble à du texte écrit par un "
                         "humain de confiance. C'est la faute d'injection "
                         "classique, déplacée d'un cran.",
     "iso42001": (),
     "couvert_par_la_norme": "non"},
    {"cle": "LLM06", "nom": "Autonomie excessive",
     "en": "Excessive Agency",
     "quoi": "L'agent dispose de plus d'outils, de droits ou de latitude "
             "que sa tâche n'en demande.",
     "pourquoi_ca_dure": "C'est le chemin le plus court pour livrer, et le "
                         "périmètre d'habilitation ne se resserre jamais "
                         "après coup.",
     "iso42001": ("A.9.2", "A.9.3", "A.9.4"),
     "couvert_par_la_norme": "partiellement"},
    {"cle": "LLM07", "nom": "Fuite de l'invite système",
     "en": "System Prompt Leakage",
     "quoi": "L'invite système, et ce qu'elle contient — règles métier, "
             "clés, noms d'outils, garde-fous — se retrouve entre les mains "
             "de l'utilisateur.",
     "pourquoi_ca_dure": "On y met des secrets parce que c'est l'endroit le "
                         "plus commode. L'atténuation n'est pas de mieux la "
                         "cacher : c'est de n'y rien mettre qui doive "
                         "rester caché.",
     "iso42001": (),
     "couvert_par_la_norme": "non"},
    {"cle": "LLM08", "nom": "Faiblesses des vecteurs et des plongements",
     "en": "Vector and Embedding Weaknesses",
     "quoi": "La base vectorielle d'un RAG rend des fragments que le "
             "demandeur n'avait pas le droit de lire, ou ingère des "
             "fragments empoisonnés.",
     "pourquoi_ca_dure": "L'indexation se fait avec les droits de celui qui "
                         "indexe, la recherche avec ceux de celui qui "
                         "demande — et presque personne ne les réconcilie.",
     "iso42001": ("A.7.5",),
     "couvert_par_la_norme": "partiellement"},
    {"cle": "LLM09", "nom": "Désinformation",
     "en": "Misinformation",
     "quoi": "Le modèle produit un contenu faux, présenté avec assurance, "
             "que le système ou l'utilisateur reprend à son compte.",
     "pourquoi_ca_dure": "La qualité rédactionnelle fait présumer la "
                         "justesse : plus le texte est bien écrit, moins on "
                         "le relit.",
     "iso42001": ("A.6.2.4", "A.8.2"),
     "couvert_par_la_norme": "partiellement"},
    {"cle": "LLM10", "nom": "Consommation non bornée",
     "en": "Unbounded Consumption",
     "quoi": "Des appels coûteux, répétés ou démesurés épuisent le budget, "
             "le quota ou le service — et peuvent servir à extraire le "
             "modèle lui-même.",
     "pourquoi_ca_dure": "Le coût est porté par l'exploitant et non par "
                         "l'appelant : rien, dans l'usage normal, ne "
                         "signale l'abus avant la facture.",
     "iso42001": (),
     "couvert_par_la_norme": "non"},
)

RISQUES_PAR_CLE = {r["cle"]: r for r in RISQUES}

COUVERTURES = {
    "oui": "L'annexe A porte des mesures qui traitent ce risque de front.",
    "partiellement": "L'annexe A l'effleure : elle demande d'encadrer, pas "
                     "de construire la parade technique.",
    "non": "Aucune mesure de l'annexe A ne le rencontre. C'est un risque "
           "applicatif, et 42001 est un système de management.",
}


# ═══════════════════════════════════════════════════════════════════════════
#  L'ÉVALUATION — CE QUI EST TRAITÉ, ET CE QUI NE L'EST PAR PERSONNE
# ═══════════════════════════════════════════════════════════════════════════

ETATS = {
    "non": {"nom": "Non traité", "traite": False},
    "partiel": {"nom": "Partiellement traité", "traite": False},
    "oui": {"nom": "Traité", "traite": True},
    "sans_objet": {"nom": "Sans objet", "traite": None},
}


def evaluer(declares=None, certifie_42001=False):
    """Ce que la maison traite, et ce que sa certification ne lui donne pas.

    ═══ LE CALCUL QUI COMPTE ════════════════════════════════════════════
    L'ANGLE MORT : les risques que la maison ne traite pas ET qu'aucune
    mesure de l'annexe A ne rencontre. Ce sont ceux pour lesquels une
    certification 42001 ne fournit aucun filet — et ce sont ceux dont on se
    croit couvert précisément parce qu'on est certifié.

    ═══ CE QUE LA FONCTION REFUSE ═══════════════════════════════════════
    RENDRE UNE NOTE SUR DIX. « 7/10 OWASP » se citerait en comité, et ne
    voudrait rien dire : les dix ne pèsent pas pareil, la liste n'est pas un
    barème, et l'OWASP ne l'a jamais présentée comme tel.
    """
    d = declares if isinstance(declares, dict) else {}
    mauvais = [k for k in d if k not in RISQUES_PAR_CLE]
    if mauvais:
        return {"ok": False, "motif": "risques_inconnus",
                "detail": sorted(mauvais)[:6]}
    mauvais_etats = [k for k, v in d.items() if v not in ETATS]
    if mauvais_etats:
        return {"ok": False, "motif": "etats_inconnus",
                "detail": sorted(mauvais_etats)[:6]}

    lignes = []
    for r in RISQUES:
        etat = d.get(r["cle"])
        traite = ETATS[etat]["traite"] if etat in ETATS else None
        sans_filet = (r["couvert_par_la_norme"] == "non")
        lignes.append({
            "cle": r["cle"], "nom": r["nom"], "en": r["en"],
            "quoi": r["quoi"], "pourquoi_ca_dure": r["pourquoi_ca_dure"],
            "etat": etat, "etat_nom": ETATS[etat]["nom"] if etat in ETATS else None,
            "traite": traite,
            "iso42001": [{"cle": c,
                          "titre": iso42001.MESURES[c]["titre"]
                          if c in iso42001.MESURES else None}
                         for c in r["iso42001"]],
            "couvert_par_la_norme": r["couvert_par_la_norme"],
            "dit_couverture": COUVERTURES[r["couvert_par_la_norme"]],
            # L'ANGLE MORT SUPPOSE QU'ON AIT DIT QUELQUE CHOSE.
            #
            # LE DÉFAUT CORRIGÉ : la première version marquait comme angle
            # mort tout risque hors portée de la norme que la maison n'avait
            # pas déclaré traité — y compris ceux dont elle n'avait RIEN dit.
            # Sur un dossier vide, la réponse nommait donc trois angles morts
            # sous un titre annonçant que rien n'était renseigné. Les deux
            # étaient vrais séparément et se contredisaient à l'écran.
            #
            # « HORS PORTÉE DE LA NORME » EST UNE PROPRIÉTÉ DE LA NORME, et
            # elle est rendue à part, toujours. « Angle mort » est une
            # propriété de la MAISON : il faut qu'elle ait dit ne pas traiter.
            "angle_mort": bool(sans_filet and traite is False),
        })

    renseignes = [l for l in lignes if l["etat"] in ETATS]
    angles = [l for l in lignes if l["angle_mort"]]
    hors_norme = [l for l in lignes if l["couvert_par_la_norme"] == "non"]

    if not renseignes:
        tete, dit = "vide", (
            "Rien n'est renseigné. La liste ci-dessous n'est pas un barème : "
            "elle sert à vérifier qu'aucune de ces dix défaillances n'a été "
            "oubliée, pas à obtenir une note.")
    elif certifie_42001 and angles:
        tete, dit = "certifie_mais_decouvert", (
            "Votre certification ISO/IEC 42001 ne vous donne rien sur %d de "
            "ces risques : aucune mesure de l'annexe A ne les rencontre, "
            "parce qu'ils sont d'ordre applicatif et que 42001 est un "
            "système de management. Ce sont ceux-là qu'il faut traiter "
            "ailleurs — et ce sont ceux dont on se croit couvert."
            % len(angles))
    elif angles:
        tete, dit = "angles_morts", (
            "%d risque(s) ne sont ni traités chez vous, ni rencontrés par "
            "l'annexe A d'ISO/IEC 42001. Aucun référentiel ne les "
            "rattrapera : ils se traitent dans l'application."
            % len(angles))
    else:
        tete, dit = "couvert", (
            "Aucun angle mort déclaré. Reste la réserve de fond : cette "
            "liste est un millésime, et le prochain portera des risques que "
            "celui-ci ignore.")

    return {
        "ok": True,
        "millesime": SOURCE["millesime"],
        "lignes": lignes,
        "risques": len(RISQUES),
        "renseignes": len(renseignes),
        "angles_morts": [l["cle"] for l in angles],
        "hors_annexe_a": [l["cle"] for l in hors_norme],
        "certifie_42001": bool(certifie_42001),
        "tete": tete,
        "dit": dit,
        "a_verifier": dict(A_VERIFIER),
        "reserve":
            "Le Top 10 OWASP n'est pas un référentiel de conformité : on ne "
            "s'y conforme pas, on s'en sert pour ne rien oublier d'évident. "
            "Il porte un millésime, et celui-ci est %s — le précédent "
            "ignorait la fuite d'invite système, les bases vectorielles et "
            "la consommation non bornée." % SOURCE["millesime"],
    }


def pont_42001():
    """Ce que l'annexe A rencontre, et ce qu'elle laisse passer."""
    return {
        "rencontres": {r["cle"]: list(r["iso42001"]) for r in RISQUES},
        "hors_portee": [r["cle"] for r in RISQUES
                        if r["couvert_par_la_norme"] == "non"],
        "dit": "Une certification ISO/IEC 42001 ne couvre pas le Top 10 : "
               "elle en rencontre une partie, en effleure une autre, et en "
               "laisse %d entièrement hors de sa portée."
               % sum(1 for r in RISQUES if r["couvert_par_la_norme"] == "non"),
    }


def referentiel():
    return {"source": dict(SOURCE), "risques": list(RISQUES),
            "etats": ETATS, "couvertures": dict(COUVERTURES),
            "pont_42001": pont_42001(), "a_verifier": dict(A_VERIFIER)}


# ═══════════════════════════════════════════════════════════════════════════
#  LA GARDE
# ═══════════════════════════════════════════════════════════════════════════

def _verifier():
    fautes = []
    if len(RISQUES) != 10:
        fautes.append("la liste ne compte pas dix risques : %d" % len(RISQUES))
    attendus = ["LLM%02d" % i for i in range(1, 11)]
    if [r["cle"] for r in RISQUES] != attendus:
        fautes.append("les clés ne suivent pas LLM01..LLM10 dans l'ordre")
    for r in RISQUES:
        ou = "le risque « %s »" % r["cle"]
        if r["couvert_par_la_norme"] not in COUVERTURES:
            fautes.append("%s porte une couverture inconnue" % ou)
        # ── LE PONT NE DOIT PAS MENTIR ───────────────────────────────────
        #
        # Une mesure citée qui n'existe pas dans l'annexe A se lirait comme
        # un rattachement et ne mènerait nulle part — et c'est précisément le
        # genre de pont qu'on ne vérifie jamais après l'avoir écrit.
        for c in r["iso42001"]:
            if c not in iso42001.MESURES:
                fautes.append("%s cite la mesure « %s », absente de l'annexe A"
                              % (ou, c))
        # ── LA COUVERTURE DÉCLARÉE S'ACCORDE AVEC LE PONT ────────────────
        if r["couvert_par_la_norme"] == "non" and r["iso42001"]:
            fautes.append("%s est déclaré hors portée de la norme tout en "
                          "citant des mesures" % ou)
        if r["couvert_par_la_norme"] != "non" and not r["iso42001"]:
            fautes.append("%s est déclaré couvert sans citer aucune mesure"
                          % ou)
        if not str(r.get("pourquoi_ca_dure") or "").strip():
            fautes.append("%s ne dit pas pourquoi il persiste" % ou)

    # ── AU MOINS UN ANGLE MORT, SINON LE MODULE NE SERT À RIEN ──────────
    #
    # Si tous les risques trouvaient une mesure, le pont ne dirait rien
    # d'autre que « la norme couvre tout » — ce qui est faux, et ce que le
    # module est écrit pour contredire.
    if not any(r["couvert_par_la_norme"] == "non" for r in RISQUES):
        fautes.append("aucun risque hors portée de l'annexe A : le pont ne "
                      "dit plus rien que la norme ne dise déjà")

    if not str(A_VERIFIER.get("pourquoi") or "").strip():
        fautes.append("la réserve de vérification a perdu son motif")
    if SOURCE.get("certifiable"):
        fautes.append("la source est déclarée certifiable : le Top 10 ne "
                      "se certifie pas")

    if fautes:
        raise RuntimeError("owasp_llm — table incohérente : " + " ; ".join(fautes))
    return []


_FAUTES = _verifier()
