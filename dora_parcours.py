# -*- coding: utf-8 -*-
"""
DORA — LE PARCOURS QUI SE VALIDE, AU LIEU DE SE VISITER.

═══ CE QUI DISTINGUE CE PARCOURS DE TOUS LES AUTRES DU SITE ════════════
Le guidage de Sentinel peint trois états — ouverte, à faire maintenant,
pas encore atteinte — et il porte partout la même réserve :

    « Le vert dit que chaque étape a été OUVERTE — pas que le travail de
      chacune a été fait. Sentinel ne peut pas mesurer le second. »

C'est vrai de la plupart des écrans : rien ne dit quand une cartographie
est « finie ». Ce n'est PAS vrai de DORA. Chacun des six blocs porte un
jeu FERMÉ de déclarations, et la complétude se constate :

  · le régime est déterminé, ou il ne l'est pas ;
  · les vingt-six articles du titre II portent un état, ou il en manque ;
  · les quinze clauses de l'article 30 sont cotées, ou il en manque ;
  · la criticité de l'incident est déclarée, ou elle ne l'est pas.

CE MODULE MESURE DONC CE QUE LE GUIDAGE GÉNÉRAL S'INTERDIT, et il le peut
parce que le règlement a des listes closes. Le vert de ce parcours dit
« tous les champs attendus sont renseignés » — pas « vous êtes conforme »,
et la réserve le dit encore.

═══ POURQUOI UN BLOC DIT TOUJOURS CE QUI LUI MANQUE ════════════════════
Un bloc qui clignote sans dire ce qu'il attend n'est pas un guidage, c'est
une humeur. Chaque bloc non validé rend donc la LISTE NOMMÉE de ce qui
manque — article 14 non déclaré, clause e) du paragraphe 3 absente — et
c'est cette liste, pas un pourcentage, qui fait avancer quelqu'un.

═══ LE PARCOURS N'EST PAS LE MÊME POUR TOUT LE MONDE ═══════════════════
Un prestataire tiers de services TIC n'a pas de cadre de gestion du risque
à coter : les chapitres II à IV ne lui sont pas opposables. Lui présenter
le bloc « verrouillé » laisserait croire qu'il s'ouvrira plus tard ; il ne
s'ouvrira jamais. Le bloc est donc SANS OBJET, avec son motif — et la
supervision de l'article 31, qui lui est propre, est sans objet pour une
entité financière, que le paragraphe 8, point i), exclut expressément.
"""

import dora
import dora_risque
import dora_tiers

VERSION = "2026-09-a"

RESERVE = (
    "Le vert de ce parcours dit que tous les champs attendus d'un bloc sont "
    "renseignés. Il ne dit pas que vous êtes en conformité : sur DORA, c'est "
    "l'autorité compétente — ACPR ou AMF en France — qui apprécie, sur "
    "pièces, et son périmètre déborde ce qu'un questionnaire couvre."
)


# ═══════════════════════════════════════════════════════════════════════
# 1. LES CINQ ÉTATS, ET CE QUE CHAQUE COULEUR DIT
# ═══════════════════════════════════════════════════════════════════════
# CINQ ET NON TROIS, PARCE QUE DEUX DISTINCTIONS COMPTENT ICI. « Pas
# encore atteinte » et « verrouillée » ne se disent pas de la même façon :
# la première viendra à son tour, la seconde demande de REVENIR en
# arrière. Et « sans objet » n'est ni l'une ni l'autre — ce bloc ne
# s'ouvrira jamais pour vous, et le dire évite de le chercher.

ETATS = {
    "validee": {
        "nom": "Validé",
        "couleur": "vert",
        "puce": "✓",
        "anime": False,
        "dit": "Tous les champs attendus de ce bloc sont renseignés. Cela ne "
               "vaut pas conformité — c'est l'autorité qui apprécie.",
    },
    "courante": {
        "nom": "À remplir maintenant",
        "couleur": "bleu",
        "puce": "▶",
        # LE CLIGNOTEMENT EST RÉSERVÉ À UN SEUL BLOC À LA FOIS. Deux
        # choses qui battent à l'écran ne désignent plus rien.
        "anime": True,
        "dit": "Le bloc que le parcours attend. Il nomme, ci-dessous, "
               "exactement ce qui lui manque.",
    },
    "attente": {
        "nom": "Pas encore atteint",
        "couleur": "gris",
        "puce": "○",
        "anime": False,
        "dit": "Il viendra à son tour. L'ordre des blocs porte une décision : "
               "le régime de l'article 16 commande ce que les suivants "
               "mesurent.",
    },
    "verrouillee": {
        "nom": "Verrouillé",
        "couleur": "ambre",
        "puce": "⚠",
        "anime": False,
        "dit": "Un bloc précédent n'est pas complet, et celui-ci en dépend. "
               "Il ne s'ouvrira pas tant que l'autre n'est pas renseigné.",
    },
    "sans_objet": {
        "nom": "Sans objet pour vous",
        "couleur": "muet",
        "puce": "—",
        "anime": False,
        "dit": "Ce bloc ne vous concerne pas, et il ne s'ouvrira jamais. Le "
               "motif est nommé : ce n'est pas un oubli.",
    },
}

#: UN SEUL BLOC CLIGNOTE, ET LA GARDE LE VÉRIFIE.
ANIMES = tuple(k for k, v in ETATS.items() if v["anime"])


# ═══════════════════════════════════════════════════════════════════════
# 2. LES SIX BLOCS, DANS L'ORDRE DU RAISONNEMENT
# ═══════════════════════════════════════════════════════════════════════
# L'ORDRE N'EST PAS CELUI DU RÈGLEMENT, ET C'EST VOULU. Le pont ISO vient
# en DEUXIÈME, avant l'analyse de risque : savoir ce qu'un système de
# management certifié documente déjà change la façon de coter les
# vingt-six articles, et l'apprendre après revient à coter deux fois.

BLOCS = (
    {"cle": "qualifier", "rang": 1, "panneau": "dora-qualifier",
     "nom": "Qualification et régime",
     "quoi": "Le type d'entité de l'article 2, le régime de l'article 16, et "
             "l'articulation avec NIS 2.",
     "pourquoi": "Il commande tout le reste. Le régime décide si vingt-six "
                 "articles vous sont opposables ou quatorze, et les deux jeux "
                 "ne se recouvrent pas.",
     "piege": "La taille ne décide PAS du régime. Une microentreprise qui "
              "n'est dans aucune des cinq catégories de l'article 16, "
              "paragraphe 1, relève du cadre complet.",
     "prerequis": ()},
    {"cle": "iso", "rang": 2, "panneau": "dora-iso",
     "nom": "Ce qu'un SMSI apporte déjà",
     "quoi": "Ce qu'une certification ISO/IEC 27001 documente déjà parmi les "
             "articles du règlement délégué — et ce qu'elle ne documente pas.",
     "pourquoi": "Avant de coter, savoir ce qui est déjà produit. L'apprendre "
                 "après revient à coter deux fois les mêmes articles.",
     "piege": "Le périmètre du système de management est choisi par "
              "l'organisme ; celui du règlement ne l'est pas. Reprendre le "
              "premier pour le second est l'erreur la plus courante.",
     "affine": "Déclarer les thèmes de l'annexe A réellement en place "
               "précise la carte — c'est facultatif, et le bloc se valide "
               "sans.",
     "prerequis": ("qualifier",)},
    {"cle": "risque", "rang": 3, "panneau": "dora-risque",
     "nom": "Cadre de gestion du risque",
     "quoi": "Les articles du règlement délégué (UE) 2024/1774 que votre "
             "régime rend opposables, chapitre par chapitre.",
     "pourquoi": "C'est l'objet même du règlement, et ce que l'autorité ouvre "
                 "en premier.",
     "piege": "Un article non déclaré compte pour zéro ET reste au "
              "dénominateur : le silence n'allège pas l'exigence.",
     "prerequis": ("qualifier",)},
    {"cle": "tiers", "rang": 4, "panneau": "dora-tiers",
     "nom": "Contrats — article 30",
     "quoi": "Neuf clauses pour tout accord de services TIC, six de plus dès "
             "que la fonction soutenue est critique ou importante.",
     "pourquoi": "Une clause absente ne se rattrape pas après la signature : "
                 "il faut rouvrir le contrat, et le prestataire n'y a aucun "
                 "intérêt.",
     "piege": "La dérogation microentreprise ne vise QUE le point e) du "
              "paragraphe 3, et seulement pour une microentreprise.",
     "prerequis": ("qualifier",)},
    {"cle": "incident", "rang": 5, "panneau": "dora-incident",
     "nom": "Incident majeur et délais",
     "quoi": "La conjonction de l'article 8 du règlement délégué "
             "(UE) 2024/1772, puis les trois échéances.",
     "pourquoi": "La chaîne se répète à blanc, elle ne se coche pas. Les "
                 "délais courent en heures, et la première échue commande.",
     "piege": "La criticité des services touchés est une PORTE, pas un "
              "septième seuil : sans elle, aucun verdict ne peut être rendu.",
     "prerequis": ("qualifier",)},
    {"cle": "supervision", "rang": 6, "panneau": "dora-supervision",
     "nom": "Prestataire critique — supervision",
     "quoi": "Les quatre exclusions de l'article 31, paragraphe 8, puis les "
             "seuils chiffrés de l'étape 1.",
     "pourquoi": "La désignation ouvre un cadre de supervision européen, et "
                 "une redevance dont le plancher est de cinquante mille euros "
                 "par an.",
     "piege": "Ce n'est pas vous qui désignez. Les autorités européennes de "
              "surveillance le font, et franchir l'étape 1 ne vaut pas "
              "désignation.",
     "prerequis": ("qualifier",)},
)

BLOCS_PAR_CLE = {b["cle"]: b for b in BLOCS}


# ═══════════════════════════════════════════════════════════════════════
# 3. CE QUI REND UN BLOC SANS OBJET — ET LE MOTIF SE DIT
# ═══════════════════════════════════════════════════════════════════════
# LE PARCOURS S'ADAPTE À QUI VOUS ÊTES, et il le dit au lieu de masquer.
# Un bloc caché se cherche ; un bloc barré avec son motif se comprend.

def _sans_objet(cle, qualification):
    """Ce bloc peut-il seulement s'ouvrir pour cette entité ? Sinon, pourquoi."""
    q = qualification or {}
    entite = q.get("entite") or {}
    financiere = entite.get("financiere")
    dans_le_champ = q.get("dans_le_champ")

    # ── HORS DU CHAMP : plus rien ne s'applique, sauf la qualification
    #    elle-même qui vient de le dire.
    if dans_le_champ is False and cle != "qualifier":
        return ("L'entité est exclue par l'article 2, paragraphe 3 : le "
                "règlement ne s'applique pas, et ce bloc n'a pas d'objet.")

    if financiere is False:
        # ── LE PRESTATAIRE TIERS N'EST PAS UNE ENTITÉ FINANCIÈRE ────────
        if cle in ("risque", "iso"):
            return ("Les chapitres II à IV ne sont pas opposables à un "
                    "prestataire tiers de services TIC : il n'a pas de cadre "
                    "de gestion du risque à coter au titre de DORA.")
        if cle == "incident":
            return ("La chaîne de notification de l'article 19 pèse sur "
                    "l'entité financière, pas sur son prestataire. Vos "
                    "propres délais se négocient au contrat, article 30, "
                    "paragraphe 3, point b).")
    elif financiere is True and cle == "supervision":
        # ── ET L'INVERSE, QUI SURPREND DAVANTAGE ────────────────────────
        return ("L'article 31, paragraphe 8, point i), exclut expressément de "
                "la désignation les entités financières qui fournissent des "
                "services TIC à d'autres entités financières. Ce bloc est "
                "celui de vos prestataires, pas le vôtre.")
    return None


# ═══════════════════════════════════════════════════════════════════════
# 4. CE QUI MANQUE À CHAQUE BLOC — NOMMÉ, JAMAIS COMPTÉ
# ═══════════════════════════════════════════════════════════════════════

def _manque(cle, declaration, qualification):
    """La liste NOMMÉE de ce que ce bloc attend encore.

    UN BLOC QUI CLIGNOTE SANS DIRE CE QU'IL ATTEND N'EST PAS UN GUIDAGE,
    C'EST UNE HUMEUR. Chaque entrée porte de quoi agir : le champ, ce
    qu'il est, et où il se remplit.
    """
    d = declaration if isinstance(declaration, dict) else {}
    q = qualification or {}
    out = []

    def _il_manque(champ, quoi):
        out.append({"champ": champ, "quoi": quoi})

    if cle == "qualifier":
        if (d.get("entite") or "") not in dora.ENTITES_PAR_CLE:
            _il_manque("entite", "Le type d'entité de l'article 2, "
                                 "paragraphe 1.")
        if d.get("identifiee_nis2") is None:
            _il_manque("identifiee_nis2",
                       "L'identification comme entité essentielle ou "
                       "importante au titre de NIS 2. Sans elle, "
                       "l'articulation de l'article 4 de la directive ne se "
                       "calcule pas — et elle ne se présume pas.")
        return out

    if cle == "iso":
        # UNE SEULE RÉPONSE VALIDE CE BLOC, ET C'EST DÉLIBÉRÉ. Une première
        # version exigeait AUSSI les mesures de l'annexe A déclarées en
        # place — sans qu'aucun champ ne permette de les saisir. Le bloc ne
        # pouvait donc jamais passer au vert, et le parcours s'arrêtait là
        # pour tout organisme certifié : une impasse, créée par une
        # exigence plus lourde que l'objet du bloc.
        #
        # CE QUE LE BLOC SERT À SAVOIR : s'il y a des preuves à reprendre.
        # Les mesures précisent la carte ; elles ne conditionnent pas la
        # réponse, et elles se déclarent ensuite, thème par thème.
        if d.get("iso27001_certifie") is None:
            _il_manque("iso27001_certifie",
                       "Êtes-vous certifié ISO/IEC 27001 ? La réponse décide "
                       "s'il y a des preuves à reprendre.")
        return out

    if cle == "risque":
        regime = q.get("regime")
        if regime not in dora_risque.REGIMES:
            _il_manque("regime", "Le régime n'est pas déterminé : qualifiez "
                                 "l'entité d'abord.")
            return out
        etats = d.get("etats") if isinstance(d.get("etats"), dict) else {}
        for num, titre, _t, _c, _cn in dora_risque.articles(regime):
            if etats.get(num) not in dora_risque.ETATS:
                _il_manque("article_%d" % num,
                           "Article %d — %s" % (num, titre))
        return out

    if cle == "tiers":
        contrats = d.get("contrats")
        contrats = contrats if isinstance(contrats, list) else []
        if not contrats:
            _il_manque("contrats", "Au moins un contrat de services TIC à "
                                   "examiner.")
            return out
        for rang, c in enumerate(contrats, start=1):
            c = c if isinstance(c, dict) else {}
            critique = c.get("fonction_critique")
            if critique is None:
                _il_manque("contrat%d_criticite" % rang,
                           "Contrat %d — la fonction soutenue est-elle "
                           "critique ou importante ? Tant que la réponse "
                           "manque, rien n'est compté." % rang)
                continue
            etats = c.get("clauses") if isinstance(c.get("clauses"), dict) else {}
            attendues = dora_tiers.clauses_attendues(
                critique, bool(c.get("microentreprise")))
            for cl in attendues:
                k = "%s_%s" % (cl["serie"], cl["lettre"])
                if etats.get(k) not in dora_tiers.ETATS:
                    _il_manque("contrat%d_%s" % (rang, k),
                               "Contrat %d — %s" % (rang, cl["article"]))
        return out

    if cle == "incident":
        if d.get("services_critiques") is None:
            _il_manque("services_critiques",
                       "Des services critiques ou importants ont-ils été "
                       "touchés ? C'est la porte de l'article 8, "
                       "paragraphe 1 : sans elle, aucun verdict.")
        if not d.get("connaissance"):
            _il_manque("connaissance",
                       "L'horodatage de la CONNAISSANCE de l'incident. "
                       "L'horloge part de là, pas de la survenance.")
        return out

    if cle == "supervision":
        import dora_supervision
        for x in dora_supervision.EXCLUSIONS:
            if d.get(x["cle"]) is None:
                _il_manque(x["cle"],
                           "Article 31, paragraphe 8, point %s — %s"
                           % (x["point"], x["quoi"]))
        return out

    return out


# ═══════════════════════════════════════════════════════════════════════
# 5. L'AVANCEMENT — UN SEUL ENDROIT LE CALCULE
# ═══════════════════════════════════════════════════════════════════════

def avancement(declaration=None):
    """L'état des six blocs, ce qui manque à chacun, et lequel clignote.

    UN SEUL BLOC EST COURANT, ET C'EST LE PREMIER NON VALIDÉ dont les
    prérequis sont tenus. Pas le suivant du dernier rempli : quelqu'un qui
    a rempli 1, 2 et 5 doit être ramené à 3, qu'il a sauté — l'ordre des
    blocs porte une décision, et le guidage doit la respecter.
    """
    d = declaration if isinstance(declaration, dict) else {}
    q = dora.qualifier(d)
    if not q.get("ok"):
        q = {}

    lignes, valides = [], set()
    for b in BLOCS:
        motif = _sans_objet(b["cle"], q)
        if motif:
            lignes.append(dict(b, etat="sans_objet", motif=motif, manque=[],
                               prerequis_manquants=[]))
            continue
        manque = _manque(b["cle"], d, q)
        absents = [p for p in b["prerequis"] if p not in valides]
        if not manque and not absents:
            valides.add(b["cle"])
            lignes.append(dict(b, etat="validee", motif=None, manque=[],
                               prerequis_manquants=[]))
            continue
        lignes.append(dict(b, etat=None, motif=None, manque=manque,
                           prerequis_manquants=absents))

    # ── LA COURANTE, PUIS LE RESTE ──────────────────────────────────────
    courante = None
    for l in lignes:
        if l["etat"] is not None:
            continue
        if l["prerequis_manquants"]:
            l["etat"] = "verrouillee"
            l["motif"] = ("Ce bloc dépend de : %s. Complétez-le d'abord."
                          % ", ".join(BLOCS_PAR_CLE[p]["nom"]
                                      for p in l["prerequis_manquants"]))
            continue
        if courante is None:
            courante = l["cle"]
            l["etat"] = "courante"
        else:
            l["etat"] = "attente"

    ouvrables = [l for l in lignes if l["etat"] != "sans_objet"]
    faits = [l for l in ouvrables if l["etat"] == "validee"]
    # ── LE SUIVANT EST CALCULÉ ICI, PAS DEVINÉ PAR L'ÉCRAN. C'est lui qui
    #    porte le passage automatique ; le laisser à la page reviendrait à
    #    tenir l'ordre du parcours à deux endroits.
    #
    #    MESURÉ, ET CORRIGÉ : une première version ne retenait que les blocs
    #    « courante » ou « attente ». Sur une déclaration vide, les cinq
    #    blocs suivants sont VERROUILLÉS — faute de qualification — et le
    #    suivant valait donc None. Le passage automatique n'avait aucune
    #    cible au moment précis où il en a le plus besoin : juste après la
    #    validation du premier bloc, qui les déverrouille tous.
    suivant = None
    if courante:
        reste = [l for l in lignes
                 if l["rang"] > BLOCS_PAR_CLE[courante]["rang"]
                 and l["etat"] != "sans_objet"]
        suivant = reste[0]["cle"] if reste else None

    return {
        "ok": True,
        "version": VERSION,
        "blocs": lignes,
        "courante": courante,
        "suivant": suivant,
        "total": len(ouvrables),
        "valides": len(faits),
        "part": (round(100.0 * len(faits) / len(ouvrables), 1)
                 if ouvrables else 0.0),
        "fini": bool(ouvrables) and len(faits) == len(ouvrables),
        # ── CE QUE « FINI » VEUT DIRE DÉPEND DE CE QUI A ÉTÉ TROUVÉ, et
        #    un parcours d'un seul bloc qui se solde par « hors champ » ne
        #    se félicite pas. Un « 100 % » sans cette phrase se lirait
        #    comme une réussite ; c'est une sortie du champ.
        "conclusion": _conclusion(q, lignes, ouvrables, faits),
        "sans_objet": [{"cle": l["cle"], "nom": l["nom"], "motif": l["motif"]}
                       for l in lignes if l["etat"] == "sans_objet"],
        "etats": {k: dict(v) for k, v in ETATS.items()},
        "reserve": RESERVE,
    }


def _conclusion(q, lignes, ouvrables, faits):
    """Ce que la fin du parcours signifie — et elle ne signifie pas la même
    chose selon ce que la qualification a trouvé."""
    if not ouvrables or len(faits) != len(ouvrables):
        return None
    entite = (q or {}).get("entite") or {}
    if (q or {}).get("dans_le_champ") is False:
        return ("Le parcours s'arrête au premier bloc, et c'est le bon "
                "résultat : l'entité est exclue par l'article 2, "
                "paragraphe 3. Cent pour cent ne dit pas que le travail est "
                "fait — il dit qu'il n'y en a pas, parce que le règlement ne "
                "s'applique pas.")
    if entite.get("financiere") is False:
        return ("Les %d blocs qui vous concernent sont renseignés. Les trois "
                "autres sont sans objet : vous n'êtes pas une entité "
                "financière, et les chapitres II à IV ne vous sont pas "
                "opposables." % len(ouvrables))
    return ("Les %d blocs sont renseignés. Ce n'est pas une conformité : la "
            "chaîne de notification et ses délais en heures, les tests de "
            "pénétration fondés sur la menace et le registre d'informations "
            "de l'article 28, paragraphe 3, ne s'évaluent pas par un "
            "questionnaire." % len(ouvrables))


def referentiel():
    return {
        "version": VERSION,
        "reserve": RESERVE,
        "etats": {k: dict(v) for k, v in ETATS.items()},
        "blocs": [dict(b, prerequis=list(b["prerequis"])) for b in BLOCS],
    }


# ═══════════════════════════════════════════════════════════════════════
# 6. LE RÉFÉRENTIEL SE CONTREDIT-IL ? CONTRÔLÉ À L'IMPORT
# ═══════════════════════════════════════════════════════════════════════

def _verifier():
    fautes = []

    if [b["rang"] for b in BLOCS] != list(range(1, len(BLOCS) + 1)):
        fautes.append("les rangs des blocs ne se suivent pas")

    # ── UN SEUL ÉTAT ANIMÉ. Deux choses qui battent à l'écran ne
    #    désignent plus rien, et le clignotement cesse d'être un guidage.
    if len(ANIMES) != 1 or ANIMES[0] != "courante":
        fautes.append("l'animation doit être réservée au seul état "
                      "« courante » : %s" % list(ANIMES))

    for b in BLOCS:
        for champ in ("nom", "quoi", "pourquoi", "piege", "panneau"):
            if not b.get(champ):
                fautes.append("bloc %s : %s manquant" % (b["cle"], champ))
        # ── UN PRÉREQUIS VIENT TOUJOURS AVANT. Un bloc qui dépendrait
        #    d'un bloc postérieur serait verrouillé pour toujours.
        for p in b["prerequis"]:
            if p not in BLOCS_PAR_CLE:
                fautes.append("bloc %s : prérequis inconnu %r" % (b["cle"], p))
            elif BLOCS_PAR_CLE[p]["rang"] >= b["rang"]:
                fautes.append(
                    "bloc %s dépend de %s, qui vient APRÈS lui : il serait "
                    "verrouillé pour toujours" % (b["cle"], p))

    # ── CHAQUE ÉTAT DIT CE QU'IL SIGNIFIE. Une pastille de couleur sans
    #    légende ne se lit pas.
    for k, v in ETATS.items():
        if not v.get("dit") or not v.get("nom") or not v.get("puce"):
            fautes.append("état %s : incomplet" % k)

    # ── LE PREMIER BLOC N'A PAS DE PRÉREQUIS, sans quoi le parcours ne
    #    pourrait jamais commencer.
    if BLOCS[0]["prerequis"]:
        fautes.append("le premier bloc porte un prérequis : le parcours ne "
                      "peut pas commencer")

    return fautes


_FAUTES = _verifier()
assert not _FAUTES, "dora_parcours.py se contredit : %s" % _FAUTES
