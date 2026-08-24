# -*- coding: utf-8 -*-
"""LES REPORTAGES ET LES ENTRETIENS — leur registre, et pourquoi il est vide.

CE MODULE NE PRODUIT AUCUN TEXTE. Il tient le registre des pièces RÉDIGÉES PAR
DES PERSONNES et signées par elles, et il refuse tout ce qui n'est pas signé.
Il est vide aujourd'hui, et cette page-là est la seule honnête : ce site n'a
envoyé personne sur le terrain et n'a interrogé personne.

════════════════════════════════════════════════════════════════════════════
POURQUOI CE REGISTRE PLUTÔT QU'UNE ABSENCE SILENCIEUSE
════════════════════════════════════════════════════════════════════════════
La revue mensuelle a été demandée « avec des reportages et des interviews ».
Trois réponses étaient possibles, et deux sont fausses :

  · LES FABRIQUER. Un modèle de langage écrit un « reportage » plausible en
    quinze secondes, et une « interview » avec les réponses qu'un dirigeant
    aurait pu faire. Ce serait la seule chose que ce site s'interdit
    absolument — et ce serait pire ici qu'ailleurs, parce qu'un entretien
    inventé fait DIRE quelque chose à une personne nommée.
  · NE RIEN DIRE. Servir une revue sans ces rubriques laisserait croire
    qu'elles n'ont pas été demandées, ou qu'un mensuel de veille n'en porte
    pas. Le lecteur ne saurait pas ce qui manque.
  · DÉCLARER LE MANQUE ET TENIR LA PLACE. C'est ce qui est fait : la revue
    porte les deux rubriques, elles sont vides, elles disent pourquoi et ce
    qu'il faudrait. C'est exactement le traitement que `sources.A_BRANCHER`
    applique depuis l'origine aux sources non raccordées.

════════════════════════════════════════════════════════════════════════════
CE QU'UNE PIÈCE DOIT PORTER POUR ENTRER ICI
════════════════════════════════════════════════════════════════════════════
Ces exigences ne sont pas des formalités : chacune répond à une façon
précise dont un faux passe pour un vrai.

  · UN AUTEUR NOMMÉ. « La rédaction » n'est pas une signature. Un texte que
    personne n'endosse ne peut être ni contesté ni corrigé.
  · UNE MÉTHODE ÉCRITE. Comment le fait a été constaté : sur place, par
    téléphone, sur pièces. Sans elle, le lecteur ne peut pas peser ce qu'il
    lit.
  · DES SOURCES. Un reportage sans source vérifiable est un récit.
  · POUR UN ENTRETIEN : LA PERSONNE, SA FONCTION, LA DATE, ET SON ACCORD.
    L'accord de publication est une condition de droit, pas une politesse —
    et la relecture par l'interlocuteur, quand elle a eu lieu, se dit, parce
    qu'elle change le statut du texte.

Une pièce qui manque un seul de ces éléments fait échouer le chargement du
module. Le registre refuse de s'ouvrir plutôt que de publier une pièce dont
on ne pourrait pas répondre.
"""

import re

#: Les deux natures servies, et ce qu'elles engagent. Le nom voyage dans les
#: deux langues, comme partout ailleurs sur ce site.
NATURES = {
    "reportage": {
        "nom": "Reportage", "nom_en": "Report",
        "dit": "Un fait constaté par une personne de ce cabinet, sur place ou "
               "sur pièces, et signé par elle.",
        "dit_en": "A fact observed by someone from this firm, on site or from "
                  "documents, and signed by them.",
    },
    "entretien": {
        "nom": "Entretien", "nom_en": "Interview",
        "dit": "Les propos d'une personne nommée, recueillis à une date "
               "connue et publiés avec son accord.",
        "dit_en": "The words of a named person, gathered on a known date and "
                  "published with their consent.",
    },
}

ORDRE_NATURES = ("reportage", "entretien")

#: LES CHAMPS EXIGÉS, PAR NATURE. Communs d'abord, puis ce que l'entretien
#: ajoute — c'est-à-dire ce qui distingue des propos rapportés d'un récit.
EXIGES = {
    "reportage": ("cle", "nature", "titre", "chapeau", "texte",
                  "auteur", "date", "methode", "sources"),
    "entretien": ("cle", "nature", "titre", "chapeau", "texte",
                  "auteur", "date", "methode", "sources",
                  "interlocuteur", "fonction", "date_entretien", "accord"),
}

#: CE QU'IL FAUDRAIT POUR QUE CES RUBRIQUES EXISTENT — écrit, parce qu'un
#: manque sans remède se lit comme un renoncement définitif.
CE_QU_IL_FAUDRAIT = {
    "reportage": (
        "Quelqu'un de ce cabinet doit aller constater un fait et le signer. "
        "Ce n'est pas un réglage : c'est un déplacement, du temps, et un nom "
        "engagé. Aucun outil ne le remplace.",
        "Someone from this firm must go and observe a fact, then sign it. "
        "This is not a setting: it takes a journey, time, and a name on the "
        "line. No tool replaces it.",
    ),
    "entretien": (
        "Il faut une personne qui accepte de parler, une date, un compte "
        "rendu fidèle et son accord écrit pour publier. Un entretien dont "
        "l'un de ces quatre éléments manque n'est pas un entretien.",
        "It takes a person willing to speak, a date, a faithful account, and "
        "their written consent to publish. An interview missing any one of "
        "these four is not an interview.",
    ),
}

#: CE QUE DIT UNE RUBRIQUE VIDE. La phrase porte sur LA PÉRIODE et non sur le
#: site entier : « aucun entretien n'a été conduit » est vérifiable et borné,
#: là où « ce site ne fait pas d'entretien » serait une politique, que
#: personne n'a arrêtée.
VIDE = {
    "reportage": ("Aucun reportage n'a été mené sur cette période.",
                  "No report was carried out over this period."),
    "entretien": ("Aucun entretien n'a été conduit sur cette période.",
                  "No interview was conducted over this period."),
}

#: LE REGISTRE. Vide, et il le reste tant que personne n'a écrit ni signé.
#: Une pièce s'ajoute ici — pas ailleurs — et elle passe le contrôle ci-dessous.
PIECES = ()


_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _verifier():
    """LE REGISTRE REFUSE DE S'OUVRIR PLUTÔT QUE DE PUBLIER UNE PIÈCE DONT ON
    NE POURRAIT PAS RÉPONDRE.

    Une pièce mal formée ne se voit pas à l'écran : elle s'y voit comme un
    article normal, avec l'autorité d'un article normal. C'est précisément le
    cas où l'erreur doit être bruyante."""
    vues = set()
    for p in PIECES:
        nature = p.get("nature")
        if nature not in NATURES:
            raise ValueError("nature inconnue : %r" % (nature,))
        for champ in EXIGES[nature]:
            if not p.get(champ):
                raise ValueError("pièce %r sans %s" % (p.get("cle"), champ))
        if p["cle"] in vues:
            raise ValueError("clé en double : %s" % p["cle"])
        vues.add(p["cle"])
        for champ in ("date", "date_entretien"):
            if p.get(champ) and not _ISO.match(str(p[champ])):
                raise ValueError("date non ISO sur %s : %r" % (p["cle"], p[champ]))
        # « LA RÉDACTION » N'EST PAS UNE SIGNATURE. Un texte que personne
        # n'endosse ne peut être ni contesté ni corrigé.
        if str(p["auteur"]).strip().lower() in ("la rédaction", "la redaction",
                                                "conseilprev", "l'équipe"):
            raise ValueError("auteur collectif sur %s : ce n'est pas une "
                             "signature" % p["cle"])
        if not isinstance(p.get("sources"), (list, tuple)) or not p["sources"]:
            raise ValueError("pièce %s sans source vérifiable" % p["cle"])
        # L'ACCORD EST UN OUI EXPLICITE. Un champ « accord » à `False` ou à
        # « en attente » vaut refus : dans le doute, on ne publie pas.
        if nature == "entretien" and p.get("accord") is not True:
            raise ValueError("entretien %s sans accord explicite" % p["cle"])


_verifier()


def pieces(nature=None, debut=None, fin=None):
    """Les pièces d'une nature, dans une fenêtre de dates — sur la DATE DE
    PUBLICATION, qui est celle que le lecteur voit en tête.

    Rendues de la plus récente à la plus ancienne. Un registre vide rend une
    liste vide : c'est à l'appelant de le DIRE, pas à cette fonction de
    combler."""
    out = [p for p in PIECES
           if (not nature or p["nature"] == nature)
           and (not debut or str(p["date"]) >= str(debut))
           and (not fin or str(p["date"]) <= str(fin))]
    return sorted(out, key=lambda p: str(p["date"]), reverse=True)


def rubrique(nature, langue="fr", debut=None, fin=None):
    """UNE RUBRIQUE DE LA REVUE — ce qu'elle contient, ou ce qui lui manque.

    ELLE NE REND JAMAIS « rien ». Elle rend une rubrique vide QUI DIT SON
    VIDE, avec le motif et le remède. Une rubrique absente de la page se
    lirait comme une rubrique non prévue ; une rubrique vide et muette se
    lirait comme une panne."""
    i = 1 if langue == "en" else 0
    n = NATURES[nature]
    trouvees = pieces(nature, debut, fin)
    return {
        "nature": nature,
        "nom": n["nom_en"] if i else n["nom"],
        "dit": n["dit_en"] if i else n["dit"],
        "pieces": [_servir(p, langue) for p in trouvees],
        "n": len(trouvees),
        # LE MOTIF N'EST SERVI QUE S'IL Y A UN VIDE À EXPLIQUER. Le jour où
        # une pièce existe, la phrase disparaît d'elle-même — sans quoi la
        # page continuerait d'annoncer une absence démentie juste au-dessus.
        "vide_motif": None if trouvees else VIDE[nature][i],
        "ce_qu_il_faudrait": None if trouvees else CE_QU_IL_FAUDRAIT[nature][i],
    }


def _servir(p, langue):
    """La pièce telle qu'elle s'affiche — signature comprise. La signature
    n'est pas une mention légale reléguée en bas : elle est ce qui distingue
    ce texte d'un texte dérivé, et elle voyage avec lui."""
    out = {k: p.get(k) for k in
           ("cle", "nature", "titre", "chapeau", "texte", "auteur", "date",
            "methode", "sources", "interlocuteur", "fonction",
            "date_entretien", "relu_par_l_interlocuteur")}
    out["signe"] = True
    return out


def sante():
    """CE QUE CE MODULE FAIT, ET CE QU'IL NE FAIT PAS — mesuré, pas annoncé."""
    return {
        "module": "redaction",
        "version": "2026.08.24",
        "portee": "Tient le registre des reportages et entretiens RÉDIGÉS ET "
                  "SIGNÉS par des personnes. N'en produit aucun, n'en dérive "
                  "aucun, et refuse toute pièce non signée.",
        "pieces": len(PIECES),
        "reportages": len(pieces("reportage")),
        "entretiens": len(pieces("entretien")),
        "modeles_de_langage": 0,
        "pourquoi_c_est_vide":
            "Ce cabinet n'a envoyé personne sur le terrain et n'a interrogé "
            "personne. Les deux rubriques existent et le disent, plutôt que "
            "de disparaître de la page ou d'être remplies par une machine.",
    }
