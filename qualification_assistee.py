# -*- coding: utf-8 -*-
"""
QUALIFIER LES SYSTÈMES DU REGISTRE — PROPOSÉ PAR LA MACHINE, PRONONCÉ PAR
UNE PERSONNE.

Ce module ne classe aucun système. Il prépare une PROPOSITION de
classification au titre du règlement (UE) 2024/1689, et il refuse d'en
préparer une quand la déclaration du registre ne la porte pas.

POURQUOI LE MODÈLE N'ÉCRIT PAS LE REGISTRE.
Le registre des systèmes d'IA est une pièce opposable : l'article 49 en
fait une obligation d'enregistrement, et la classification qu'il porte
commande tout le reste — les obligations des articles 9 à 15, l'évaluation
de conformité, la FRIA de l'article 27. Une classification qui change sans
qu'on sache QUI l'a décidée n'est plus une pièce : c'est une valeur dans
une base. C'est pourquoi la seule écriture que ce module autorise dans le
registre est portée par `appliquer()`, qui EXIGE le nom de la personne qui
décide et refuse sans lui — et c'est aussi pourquoi la proposition vit dans
sa propre table, et non dans la colonne `classification`.

CE QUI EST AUTOMATISÉ, EXACTEMENT.
La lecture de la déclaration, le refus quand elle est trop maigre, la
formulation d'une proposition motivée et l'énumération de ce qui manque.
Pas la décision, pas l'écriture, pas l'article invoqué hors de la liste
fermée ci-dessous.

CE QUI EST VÉRIFIÉ AVANT D'ÊTRE MONTRÉ.
Une réponse de modèle n'est pas crue sur parole. `verifier()` exige que la
classe appartienne au vocabulaire du registre, que l'article appartienne à
la liste fermée, que l'article PUISSE soutenir cette classe, et que chaque
indice avancé se retrouve MOT POUR MOT dans la déclaration. Un indice
paraphrasé — donc invérifiable — fait tomber la proposition entière sur
« à compléter ». Refuser vaut mieux que deviner : une classification
devinée se lit exactement comme une classification établie.

LE CHIFFRE D'APPUI N'EST PAS CELUI DU MODÈLE.
Un modèle à qui l'on demande sa confiance répond un nombre ; ce nombre
n'est pas une mesure. `appui` est calculé ici, à partir de ce qui est
vérifiable : la part des champs réellement déclarés et le nombre d'indices
retrouvés dans le texte. La confiance annoncée par le modèle est conservée
telle quelle, et ne commande rien.
"""

import json
import re
import unicodedata

import finops_ia

VERSION = "2026-09-a"

REGLEMENT = "Règlement (UE) 2024/1689 (AI Act)"

RESERVE = (
    "Cette proposition est un pré-diagnostic. Elle ne vaut pas avis "
    "juridique et ne prononce aucune qualification : la classification "
    "inscrite au registre est celle qu'une personne identifiée a décidée, "
    "et la trace de cette décision est conservée."
)


# ═══════════════════════════════════════════════════════════════════════
# 1. LE VOCABULAIRE — CELUI DU REGISTRE, PAS UN SECOND
# ═══════════════════════════════════════════════════════════════════════
# `finops_ia.CLASSIFICATION_IA_ACT` est déjà la copie contrôlée du
# formulaire du Registre IA, avec son propre garde-fou à l'import. En
# réécrire une ici créerait deux vérités pour une seule colonne. On la lit.

CLASSES = {c["cle"]: c for c in finops_ia.CLASSIFICATION_IA_ACT}

# « À évaluer » est l'état d'un système qui n'a pas de classe. Ce n'est pas
# une classe qu'on propose : proposer « à évaluer » à un système déjà à
# évaluer ne dit rien.
NON_PROPOSABLE = "a_evaluer"
PROPOSABLES = tuple(c["cle"] for c in finops_ia.CLASSIFICATION_IA_ACT
                    if c["cle"] != NON_PROPOSABLE)


# ═══════════════════════════════════════════════════════════════════════
# 2. LA LISTE FERMÉE DES ARTICLES INVOCABLES
# ═══════════════════════════════════════════════════════════════════════
# Un modèle qui cite « l'article 6 bis » a inventé. La seule défense qui
# tienne est une liste fermée : hors de ces six entrées, la proposition
# tombe. Chaque entrée dit AUSSI quelles classes elle peut soutenir — un
# article 50 ne fait pas un haut risque, et le dire ici le rend mesurable.

ARTICLES = [
    {"cle": "art_5",
     "texte": "Art. 5 — pratiques interdites",
     "soutient": ("inacceptable",),
     "quand": "La finalité déclarée relève d'une des pratiques que "
              "l'article 5 interdit (notation sociale, manipulation, "
              "reconnaissance des émotions au travail, police "
              "prédictive, moisson non ciblée d'images faciales)."},
    {"cle": "annexe_iii",
     "texte": "Art. 6 §2 et annexe III — domaines à haut risque",
     "soutient": ("haut",),
     "quand": "La finalité déclarée relève d'un des huit domaines de "
              "l'annexe III (biométrie, infrastructures critiques, "
              "éducation, emploi, services essentiels et crédit, "
              "répression, migration, justice et démocratie)."},
    {"cle": "annexe_i",
     "texte": "Art. 6 §1 et annexe I — composant de sécurité d'un produit "
              "réglementé",
     "soutient": ("haut",),
     "quand": "Le système déclaré est un composant de sécurité d'un "
              "produit couvert par la législation d'harmonisation de "
              "l'annexe I, ou est lui-même un tel produit."},
    {"cle": "art_6_3",
     "texte": "Art. 6 §3 — dérogation au haut risque",
     "soutient": ("limite", "minimal"),
     "quand": "La finalité touche un domaine de l'annexe III, mais le "
              "système ne fait qu'une tâche procédurale étroite, ou "
              "améliore un travail humain déjà fait, sans se substituer "
              "à l'appréciation humaine. La dérogation doit être "
              "documentée avant la mise sur le marché (art. 6 §4)."},
    {"cle": "art_50",
     "texte": "Art. 50 — obligations de transparence",
     "soutient": ("limite",),
     "quand": "Le système interagit directement avec des personnes, ou "
              "produit du contenu de synthèse, sans relever par ailleurs "
              "de l'annexe III ni de l'annexe I."},
    {"cle": "hors_annexes",
     "texte": "Hors annexes I et III, hors art. 5 et hors art. 50",
     "soutient": ("minimal",),
     "quand": "La finalité déclarée ne touche aucun domaine des annexes, "
              "n'est pas interdite, et le système n'interagit pas avec "
              "des personnes ni ne produit de contenu de synthèse."},
]

_ARTICLES = {a["cle"]: a for a in ARTICLES}


# ═══════════════════════════════════════════════════════════════════════
# 3. CE QUE LA DÉCLARATION DOIT PORTER POUR QU'UNE PROPOSITION SOIT
#    SEULEMENT POSSIBLE
# ═══════════════════════════════════════════════════════════════════════
# UNE LIGNE VIDE NE SE QUALIFIE PAS — NI PAR UNE MACHINE, NI PAR UN
# JURISTE. Un système dont la finalité n'est pas écrite ne peut pas être
# rapporté à l'annexe III, qui est une liste de FINALITÉS. Ce premier
# filtre est déterministe et ne consulte aucun modèle : il coûte zéro
# appel, et c'est lui qui empêche la machine de meubler.

CHAMPS = [
    {"cle": "finalite", "nom": "Finalité", "obligatoire": True, "poids": 3,
     "pourquoi": "L'annexe III est une liste de finalités. Sans finalité "
                 "écrite, il n'y a rien à lui comparer."},
    {"cle": "type_systeme", "nom": "Type de système", "obligatoire": True,
     "poids": 2,
     "pourquoi": "L'article 3 §1 définit le système d'IA par sa capacité "
                 "à inférer. Un moteur de règles écrites à la main n'entre "
                 "pas dans le règlement, et le type est ce qui le dit."},
    {"cle": "donnees_utilisees", "nom": "Données utilisées",
     "obligatoire": True, "poids": 2,
     "pourquoi": "La présence de données biométriques ou sensibles "
                 "déplace la qualification, et le RGPD s'y ajoute."},
    {"cle": "secteur", "nom": "Secteur", "obligatoire": False, "poids": 1,
     "pourquoi": "Le secteur oriente vers le bon point de l'annexe III "
                 "sans jamais le décider à lui seul."},
    {"cle": "personnes_concernees", "nom": "Personnes concernées",
     "obligatoire": False, "poids": 1,
     "pourquoi": "Un système qui décide À PROPOS de personnes n'est pas "
                 "le même qu'un système qui n'en touche aucune."},
]

_CHAMPS = {c["cle"]: c for c in CHAMPS}
_POIDS_TOTAL = float(sum(c["poids"] for c in CHAMPS))

# En deçà, la proposition est montrée mais signalée fragile : elle repose
# sur une déclaration maigre ou sur peu d'indices.
SEUIL_FRAGILE = 0.6

INDICES_MIN = 1
INDICES_MAX = 5
INDICE_LONGUEUR_MIN = 4


# ═══════════════════════════════════════════════════════════════════════
# 4. LES ÉTATS D'UNE PROPOSITION
# ═══════════════════════════════════════════════════════════════════════
# Une proposition naît « en attente ». Elle ne peut en sortir que par une
# décision humaine, et une seule fois.

STATUTS = {
    "en_attente": "Proposée, en attente d'une décision humaine",
    "validee": "Retenue par une personne et inscrite au registre",
    "ecartee": "Écartée par une personne ; le registre n'a pas bougé",
}

DECISIONS = {
    "valider": {"statut": "validee", "ecrit_le_registre": True,
                "nom": "Valider la proposition"},
    "ecarter": {"statut": "ecartee", "ecrit_le_registre": False,
                "nom": "Écarter la proposition"},
}

# Motifs de refus. Ils sont nommés pour être mesurables : un test qui
# attend « indice_non_retrouve » ne peut pas passer parce que la
# proposition est tombée pour une autre raison.
MOTIFS = {
    "declaration_illisible": "La ligne du registre n'est pas lisible.",
    "champs_manquants": "La déclaration ne porte pas les champs sans "
                        "lesquels aucune qualification n'est possible.",
    "reponse_vide": "Le moteur n'a rien renvoyé.",
    "reponse_illisible": "La réponse du moteur n'est pas un objet JSON "
                         "exploitable.",
    "classe_inconnue": "La classe proposée n'appartient pas au "
                       "vocabulaire du registre.",
    "classe_non_proposable": "« À évaluer » est l'état d'un système sans "
                             "classification, pas une classification.",
    "article_inconnu": "L'article invoqué n'appartient pas à la liste "
                       "fermée des articles invocables.",
    "article_incompatible": "L'article invoqué ne peut pas soutenir la "
                            "classe proposée.",
    "indices_absents": "Aucun indice n'est avancé à l'appui de la "
                       "proposition.",
    "indice_non_retrouve": "Un indice avancé ne se retrouve pas dans la "
                           "déclaration : il n'est pas vérifiable.",
    "motivation_absente": "La proposition n'est pas motivée.",
}


# ═══════════════════════════════════════════════════════════════════════
# 5. RECEVABILITÉ — LE FILTRE QUI NE CONSULTE PERSONNE
# ═══════════════════════════════════════════════════════════════════════

def _texte(valeur):
    if valeur is None:
        return ""
    if isinstance(valeur, (list, tuple)):
        return " ".join(_texte(v) for v in valeur)
    return str(valeur).strip()


def declaration(systeme):
    """Le texte sur lequel une proposition peut s'appuyer, et rien d'autre.

    C'est aussi le texte contre lequel les indices seront vérifiés : ce qui
    n'est pas ici ne peut pas servir de preuve.
    """
    s = systeme if isinstance(systeme, dict) else {}
    morceaux = []
    for champ in CHAMPS:
        v = _texte(s.get(champ["cle"]))
        if v:
            morceaux.append("%s : %s" % (champ["nom"], v))
    nom = _texte(s.get("nom"))
    if nom:
        morceaux.insert(0, "Nom : %s" % nom)
    return "\n".join(morceaux)


def recevabilite(systeme):
    """Cette ligne porte-t-elle de quoi être qualifiée ?

    Retourne les champs manquants NOMMÉS, avec le motif de chacun : une
    liste de cases vides ne dit pas pourquoi elle bloque.
    """
    if not isinstance(systeme, dict):
        return {"recevable": False, "manquants": [], "declares": [],
                "appui_champs": 0.0, "motif": "declaration_illisible"}

    manquants, declares, poids = [], [], 0
    for champ in CHAMPS:
        if _texte(systeme.get(champ["cle"])):
            declares.append(champ["cle"])
            poids += champ["poids"]
        else:
            manquants.append({"champ": champ["cle"], "nom": champ["nom"],
                              "obligatoire": champ["obligatoire"],
                              "pourquoi": champ["pourquoi"]})

    bloquants = [m for m in manquants if m["obligatoire"]]
    return {
        "recevable": not bloquants,
        "manquants": manquants,
        "bloquants": [m["champ"] for m in bloquants],
        "declares": declares,
        "appui_champs": round(poids / _POIDS_TOTAL, 2),
        "motif": "champs_manquants" if bloquants else None,
    }


# ═══════════════════════════════════════════════════════════════════════
# 6. LA VÉRIFICATION D'UNE RÉPONSE DE MOTEUR
# ═══════════════════════════════════════════════════════════════════════

def _sans_accent(txt):
    return "".join(c for c in unicodedata.normalize("NFD", txt)
                   if unicodedata.category(c) != "Mn")


def _normaliser(txt):
    """Ce qui permet de comparer un indice au texte dont il est tiré.

    Les accents, la casse et les espaces multiples ne sont pas des faits :
    les garder ferait tomber une citation exacte sur une apostrophe.
    L'ORTHOGRAPHE DES MOTS, ELLE, EST GARDÉE — c'est justement ce qu'on
    vérifie.
    """
    t = _sans_accent(_texte(txt)).lower()
    t = t.replace("’", "'").replace("‘", "'")
    t = t.replace("«", '"').replace("»", '"')
    return re.sub(r"[\s ]+", " ", t).strip()


def _extraire_json(brut):
    """Le JSON demandé, même enveloppé dans un bloc de code ou du bavardage."""
    t = _texte(brut)
    if not t:
        return None
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t).strip()
    try:
        obj = json.loads(t)
        return obj if isinstance(obj, dict) else None
    except Exception:
        pass
    debut, fin = t.find("{"), t.rfind("}")
    if debut < 0 or fin <= debut:
        return None
    try:
        obj = json.loads(t[debut:fin + 1])
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def _refus(motif, systeme=None, rec=None, detail=None):
    r = rec if rec is not None else recevabilite(systeme or {})
    return {
        "statut": "en_attente",
        "classe_proposee": None,
        "article": None,
        "motivation": "",
        "indices": [],
        "appui": 0.0,
        "fragile": True,
        "confiance_declaree": None,
        "a_completer": True,
        "motif": motif,
        "motif_texte": MOTIFS.get(motif, motif),
        "detail": detail,
        "manquants": r.get("manquants", []),
    }


def verifier(systeme, brut):
    """Ce que le moteur a répondu vaut-il d'être montré à une personne ?

    Chaque contrôle est un refus nommé. Un contrôle qui passerait « parce
    que la réponse était vide » plutôt que parce qu'elle était juste serait
    exactement le défaut que ce module existe pour éviter.
    """
    rec = recevabilite(systeme)
    if not rec["recevable"]:
        return _refus(rec.get("motif") or "champs_manquants", rec=rec)

    obj = _extraire_json(brut)
    if obj is None:
        return _refus("reponse_vide" if not _texte(brut) else
                      "reponse_illisible", rec=rec)

    classe = _texte(obj.get("classe"))
    if classe == NON_PROPOSABLE:
        return _refus("classe_non_proposable", rec=rec)
    if classe not in PROPOSABLES:
        return _refus("classe_inconnue", rec=rec, detail=classe or None)

    article = _texte(obj.get("article"))
    if article not in _ARTICLES:
        return _refus("article_inconnu", rec=rec, detail=article or None)
    if classe not in _ARTICLES[article]["soutient"]:
        return _refus("article_incompatible", rec=rec,
                      detail="%s / %s" % (article, classe))

    motivation = _texte(obj.get("motivation"))
    if not motivation:
        return _refus("motivation_absente", rec=rec)

    bruts = obj.get("indices")
    if not isinstance(bruts, list):
        bruts = [bruts] if bruts else []
    indices = [_texte(i) for i in bruts]
    indices = [i for i in indices if len(i) >= INDICE_LONGUEUR_MIN]
    if len(indices) < INDICES_MIN:
        return _refus("indices_absents", rec=rec)
    indices = indices[:INDICES_MAX]

    # LE CONTRÔLE QUI COMPTE. Un indice qui ne se retrouve pas dans la
    # déclaration n'est pas un indice : c'est une phrase ajoutée. Elle peut
    # être vraie — elle n'est pas vérifiable, et le reste de la proposition
    # repose dessus.
    texte = _normaliser(declaration(systeme))
    for i in indices:
        if _normaliser(i) not in texte:
            return _refus("indice_non_retrouve", rec=rec, detail=i)

    appui = round(rec["appui_champs"] * 0.7
                  + min(len(indices), 3) / 3.0 * 0.3, 2)

    confiance = obj.get("confiance")
    try:
        confiance = round(float(confiance), 2)
        if not 0.0 <= confiance <= 1.0:
            confiance = None
    except Exception:
        confiance = None

    return {
        "statut": "en_attente",
        "classe_proposee": classe,
        "classe_nom": CLASSES[classe]["libelle"],
        "article": article,
        "article_texte": _ARTICLES[article]["texte"],
        "motivation": motivation,
        "indices": indices,
        "appui": appui,
        "fragile": appui < SEUIL_FRAGILE,
        # CONSERVÉE, JAMAIS UTILISÉE POUR DÉCIDER. Un modèle sûr de lui se
        # trompe de la même façon qu'un modèle hésitant.
        "confiance_declaree": confiance,
        "a_completer": False,
        "motif": None,
        "motif_texte": None,
        "detail": None,
        "manquants": rec["manquants"],
    }


# ═══════════════════════════════════════════════════════════════════════
# 7. LA PROPOSITION — LE MOTEUR EST INJECTÉ, JAMAIS APPELÉ D'ICI
# ═══════════════════════════════════════════════════════════════════════

PROMPT_SYSTEME = (
    "Tu prepares une PROPOSITION de classification au titre du reglement "
    "(UE) 2024/1689 (AI Act), a partir d'une declaration de registre. Tu "
    "ne prononces aucune qualification : une personne decidera apres toi.\n"
    "Regles absolues :\n"
    "1. Tu reponds UNIQUEMENT par un objet JSON, sans texte avant ni "
    "apres, sans bloc de code.\n"
    "2. Le champ \"indices\" contient des extraits COPIES MOT POUR MOT de "
    "la declaration fournie. Ne reformule pas, ne resume pas : un extrait "
    "qui ne figure pas litteralement dans la declaration fait rejeter "
    "toute ta reponse.\n"
    "3. Tu n'inventes aucun article. Tu choisis une cle dans la liste "
    "fermee qui t'est donnee, et aucune autre.\n"
    "4. Si la declaration ne permet pas de trancher, choisis la classe la "
    "plus prudente que les indices soutiennent VRAIMENT, et dis dans la "
    "motivation ce qui manque. Ne comble jamais un silence par une "
    "hypothese."
)


def prompt(systeme):
    """Le message envoyé au moteur — construit ici, pas ailleurs.

    Il porte la liste fermée des articles et le vocabulaire des classes :
    un modèle à qui l'on ne donne pas la liste la devine.
    """
    lignes = ["Declaration du registre :", declaration(systeme), "",
              "Classes possibles (cle : libelle) :"]
    for cle in PROPOSABLES:
        lignes.append("- %s : %s" % (cle, CLASSES[cle]["libelle"]))
    lignes += ["", "Articles invocables (cle : texte — quand l'invoquer) :"]
    for a in ARTICLES:
        lignes.append("- %s : %s — %s" % (a["cle"], a["texte"], a["quand"]))
        lignes.append("  (soutient uniquement : %s)"
                      % ", ".join(a["soutient"]))
    lignes += [
        "",
        "Reponds par cet objet JSON exactement :",
        '{"classe": "<cle de classe>", "article": "<cle d\'article>", '
        '"motivation": "<deux phrases au plus>", '
        '"indices": ["<extrait copie mot pour mot>", ...], '
        '"confiance": <nombre entre 0 et 1>}',
    ]
    return "\n".join(lignes)


def proposer(systeme, repondre=None):
    """Une proposition pour un système, ou un refus motivé.

    `repondre` est une fonction (prompt, systeme) -> (ok, texte). Elle est
    INJECTÉE : ce module ne connaît aucun fournisseur, aucune clé, aucun
    réseau. C'est ce qui permet de mesurer tout ce qui précède sans appeler
    personne — et ce qui empêche le moteur d'avoir un chemin vers la base.
    """
    rec = recevabilite(systeme)
    if not rec["recevable"]:
        return _refus(rec.get("motif") or "champs_manquants", rec=rec)
    if repondre is None:
        return _refus("reponse_vide", rec=rec)
    try:
        ok, texte = repondre(prompt(systeme), PROMPT_SYSTEME)
    except Exception as e:
        return _refus("reponse_vide", rec=rec, detail=str(e)[:200])
    if not ok:
        return _refus("reponse_vide", rec=rec, detail=_texte(texte)[:200])
    return verifier(systeme, texte)


# ═══════════════════════════════════════════════════════════════════════
# 8. L'ÉCART, PUIS LA DÉCISION HUMAINE
# ═══════════════════════════════════════════════════════════════════════

def ecart(systeme, proposition):
    """Ce qu'une validation changerait — avant de la demander.

    Une proposition qui confirme la classe déjà inscrite ne demande aucune
    décision ; le dire évite de faire valider quarante fois la même ligne.
    """
    p = proposition if isinstance(proposition, dict) else {}
    avant = _texte((systeme or {}).get("classification")) or NON_PROPOSABLE
    apres = p.get("classe_proposee")
    if not apres:
        return {"avant": avant, "avant_nom": CLASSES[avant]["libelle"]
                if avant in CLASSES else avant,
                "apres": None, "apres_nom": None,
                "change": False, "premiere_classification": False}
    return {
        "avant": avant,
        "avant_nom": (CLASSES[avant]["libelle"] if avant in CLASSES
                      else avant),
        "apres": apres,
        "apres_nom": CLASSES[apres]["libelle"],
        "change": apres != avant,
        "premiere_classification": avant == NON_PROPOSABLE,
    }


def appliquer(systeme, proposition, decision, qui, classe_retenue=None,
              motif=None):
    """LA SEULE PORTE VERS LE REGISTRE — ET ELLE EXIGE UN NOM.

    Ce module n'écrit rien lui-même : il rend la ligne à écrire, ou un
    refus. Mais il ne la rend JAMAIS sans le nom de la personne qui décide,
    et jamais deux fois pour la même proposition. Une automatisation qui
    pourrait franchir cette porte seule ne serait plus une automatisation
    sous validation humaine — ce serait la même chose sans le mot.

    `classe_retenue` permet de valider en CORRIGEANT : la personne n'est pas
    réduite à approuver ou rejeter, et ce qu'elle retient est tracé à côté
    de ce qui lui avait été proposé.
    """
    p = proposition if isinstance(proposition, dict) else {}
    qui = _texte(qui)
    if not qui:
        return {"ok": False, "motif": "decideur_absent",
                "motif_texte": "Aucune personne identifiée ne porte cette "
                               "décision : le registre ne bouge pas."}
    if decision not in DECISIONS:
        return {"ok": False, "motif": "decision_inconnue",
                "motif_texte": "La décision doit être « valider » ou "
                               "« écarter »."}
    if p.get("statut") != "en_attente":
        return {"ok": False, "motif": "deja_decidee",
                "motif_texte": "Cette proposition a déjà reçu une "
                               "décision ; elle n'en reçoit pas deux."}

    d = DECISIONS[decision]
    if not d["ecrit_le_registre"]:
        return {"ok": True, "statut": d["statut"], "decide_par": qui,
                "ecriture": None, "motif_decision": _texte(motif) or None}

    if p.get("a_completer") or not p.get("classe_proposee"):
        return {"ok": False, "motif": "rien_a_valider",
                "motif_texte": "Cette proposition n'en est pas une : il n'y "
                               "a pas de classe à inscrire."}

    retenue = _texte(classe_retenue) or p["classe_proposee"]
    if retenue not in PROPOSABLES:
        return {"ok": False, "motif": "classe_retenue_inconnue",
                "motif_texte": "La classe retenue n'appartient pas au "
                               "vocabulaire du registre."}

    # LA JUSTIFICATION ÉCRITE AU REGISTRE DIT QUI A DÉCIDÉ, ET SUR QUOI.
    # Une justification qui dirait seulement « annexe III » laisserait
    # croire, six mois plus tard, qu'un juriste l'a écrite.
    justification = "%s — proposition assistée (%s), retenue par %s." % (
        _ARTICLES[p["article"]]["texte"] if p.get("article") in _ARTICLES
        else REGLEMENT,
        CLASSES[p["classe_proposee"]]["libelle"],
        qui)
    if retenue != p["classe_proposee"]:
        justification = "%s — proposition assistée (%s) CORRIGÉE en « %s » " \
                        "par %s." % (
                            _ARTICLES[p["article"]]["texte"]
                            if p.get("article") in _ARTICLES else REGLEMENT,
                            CLASSES[p["classe_proposee"]]["libelle"],
                            CLASSES[retenue]["libelle"], qui)

    return {
        "ok": True,
        "statut": d["statut"],
        "decide_par": qui,
        "motif_decision": _texte(motif) or None,
        "corrigee": retenue != p["classe_proposee"],
        "ecriture": {
            "classification": retenue,
            "justification": justification[:500],
        },
    }


# ═══════════════════════════════════════════════════════════════════════
# 9. LE RÉFÉRENTIEL SERVI À L'ÉCRAN
# ═══════════════════════════════════════════════════════════════════════

def referentiel():
    return {
        "version": VERSION,
        "reglement": REGLEMENT,
        "reserve": RESERVE,
        "classes": [dict(CLASSES[c], cle=c) for c in PROPOSABLES],
        "non_proposable": NON_PROPOSABLE,
        "articles": [dict(a) for a in ARTICLES],
        "champs": [dict(c) for c in CHAMPS],
        "statuts": dict(STATUTS),
        "decisions": {k: dict(v) for k, v in DECISIONS.items()},
        "motifs": dict(MOTIFS),
        "seuil_fragile": SEUIL_FRAGILE,
        "methode_appui": "70 % la part pondérée des champs déclarés, 30 % "
                         "le nombre d'indices retrouvés mot pour mot dans "
                         "la déclaration (plafonné à trois). La confiance "
                         "annoncée par le moteur n'y entre pas.",
    }


# ═══════════════════════════════════════════════════════════════════════
# 10. LE RÉFÉRENTIEL SE CONTREDIT-IL ? CONTRÔLÉ À L'IMPORT
# ═══════════════════════════════════════════════════════════════════════

def _verifier():
    assert NON_PROPOSABLE in CLASSES, \
        "« à évaluer » doit exister dans le vocabulaire du registre"
    assert PROPOSABLES, "aucune classe proposable"
    assert NON_PROPOSABLE not in PROPOSABLES, \
        "« à évaluer » ne se propose pas"

    # Le vocabulaire est celui du registre, et rien d'autre.
    attendu = {c["cle"] for c in finops_ia.CLASSIFICATION_IA_ACT}
    assert set(CLASSES) == attendu, \
        "le vocabulaire des classes a divergé de celui du registre"

    cles = [a["cle"] for a in ARTICLES]
    assert len(cles) == len(set(cles)), "deux articles portent la même clé"
    couvertes = set()
    for a in ARTICLES:
        assert a["soutient"], "l'article %s ne soutient aucune classe" % a["cle"]
        for c in a["soutient"]:
            assert c in PROPOSABLES, \
                "l'article %s soutient une classe inconnue : %s" % (a["cle"], c)
            couvertes.add(c)
        assert a["quand"].strip(), "l'article %s ne dit pas quand l'invoquer" % a["cle"]
    manque = set(PROPOSABLES) - couvertes
    assert not manque, \
        "aucun article ne peut soutenir ces classes : %s" % sorted(manque)

    cles_champs = [c["cle"] for c in CHAMPS]
    assert len(cles_champs) == len(set(cles_champs)), \
        "deux champs portent la même clé"
    assert any(c["obligatoire"] for c in CHAMPS), \
        "aucun champ n'est obligatoire : rien ne serait jamais irrecevable"
    for c in CHAMPS:
        assert c["poids"] > 0, "le champ %s ne pèse rien" % c["cle"]
        assert c["pourquoi"].strip(), "le champ %s ne dit pas pourquoi" % c["cle"]

    # Une décision qui n'écrit pas le registre, et une qui l'écrit.
    assert any(d["ecrit_le_registre"] for d in DECISIONS.values())
    assert any(not d["ecrit_le_registre"] for d in DECISIONS.values())
    for d in DECISIONS.values():
        assert d["statut"] in STATUTS, "statut de décision inconnu"

    assert 0.0 < SEUIL_FRAGILE < 1.0
    assert INDICES_MIN >= 1 and INDICES_MAX >= INDICES_MIN


_verifier()
