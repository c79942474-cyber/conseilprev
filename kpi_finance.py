"""EVA, ROCE, FREE CASH FLOW — la lecture de création de valeur du GO / NO GO.

CE QUE CE MODULE AJOUTE, ET CE QU'IL N'INVENTE PAS

Le module d'enveloppe chiffre ce que le projet COÛTE : investissement, DPGF par
lot, exploitation, coût total de possession. Il ne dit rien de ce qu'il
RAPPORTE — et sans cela, aucun des trois indicateurs de pilotage financier ne
peut exister :

  · l'EVA mesure la richesse créée AU-DELÀ du coût du capital engagé ;
  · le ROCE rapporte le résultat opérationnel aux capitaux investis ;
  · le free cash flow mesure la trésorerie réellement disponible APRÈS
    investissements.

Les trois ont besoin d'un revenu, d'un coût du capital et d'un taux d'impôt.
Aucun des trois n'est dans le référentiel, et `finance_dc.A_RENSEIGNER` dit
déjà pourquoi pour la fiscalité : « crédits d'impôt, exonérations et tarifs
d'accès varient par région et par convention ». Ce module applique la même
règle à l'ensemble : CE QUI MANQUE EST DÉCLARÉ NON INSTRUIT, jamais estimé.

  Un EVA nul faute de revenu se lirait « ce projet ne crée pas de valeur ».
  C'est faux : il se lit « personne n'a encore dit ce qu'il rapporte ». La
  différence entre les deux décide d'un GO ou d'un NO GO.

TROIS PARTIS PRIS QUI NE SONT PAS DES DÉTAILS

  1. AUCUN INDICATEUR N'EST RENDU SUR UN SEUL POINT. Un EVA d'une année ne
     s'interprète pas : c'est son ÉVOLUTION, et sa comparaison à un objectif,
     qui portent le sens décisionnel. Le moteur rend donc une série sur tout
     l'horizon, et refuse de conclure sur un exercice isolé.

  2. LA FOURCHETTE EST PROPAGÉE JUSQU'AU VERDICT. L'enveloppe est une
     fourchette ; l'EVA qui en découle aussi. Quand cette fourchette TRAVERSE
     zéro — valeur créée au bas, détruite au haut —, le moteur ne tranche pas.
     Il dit ce qu'il faudrait resserrer pour pouvoir trancher. C'est la réponse
     la plus utile qu'un GO / NO GO puisse donner, et la seule honnête.

  3. LE PIÈGE DU ROCE EST ÉCRIT, PAS MASQUÉ. Les capitaux employés diminuent
     avec l'amortissement : à résultat rigoureusement constant, le ROCE MONTE
     chaque année. Une courbe qui monte ne prouve donc aucune amélioration. Le
     moteur rend les deux lectures — sur capitaux nets et sur capitaux bruts —
     et c'est l'écart entre elles qui dit si la progression est réelle.

CE MODULE EST LA PREMIÈRE BRIQUE d'une feuille de route financière plus
détaillée. Ce qu'il ne fait pas encore est écrit dans SUITE, avec ce qu'il
faudrait pour le faire — plutôt que laissé à deviner.
"""

VERSION = "2026-08-a"

AVERTISSEMENT = (
    "Ces indicateurs se calculent à partir d'HYPOTHÈSES que vous fournissez — "
    "revenu, coût du capital, taux d'impôt. Aucune n'est dans le référentiel, "
    "et aucune n'est estimée à votre place. Ce qui n'est pas renseigné est "
    "rendu « non instruit », jamais zéro.")


# ═══════════════════════════════════════════════════════════════════════════
# 1. CE QUE L'INVESTISSEUR DOIT APPORTER
# ═══════════════════════════════════════════════════════════════════════════
# Chaque entrée porte SA question et SA raison d'être absente du référentiel.
# Une liste d'entrées sans motif finit par accueillir des valeurs « par
# défaut » qui seront crues — c'est le motif écrit qui l'en empêche.
ENTREES = [
    {"cle": "revenu_meur_an", "nom": "Revenu annuel attendu (M€)",
     "unite": "M€/an", "obligatoire": True,
     "pourquoi": "un centre de données se vend au kW réservé, au m² ou au "
                 "service, et le prix dépend du contrat, pas du pays ; aucune "
                 "statistique publique ne prédit VOTRE chiffre d'affaires",
     "question": "Quel revenu annuel le plan d'affaires retient-il à pleine "
                 "charge, et à partir de quelle année l'atteint-il ?"},
    {"cle": "wacc", "nom": "Coût moyen pondéré du capital (%)",
     "unite": "%", "obligatoire": True,
     "pourquoi": "le coût du capital est une décision d'investisseur, au même "
                 "titre que le taux d'actualisation que le module d'enveloppe "
                 "refuse déjà de choisir à votre place",
     "question": "Quel CMPC le comité d'investissement retient-il pour cette "
                 "classe d'actif, et sur quelle durée ?"},
    {"cle": "is_taux", "nom": "Taux d'impôt sur les sociétés (%)",
     "unite": "%", "obligatoire": True,
     "pourquoi": "crédits d'impôt, exonérations et régimes locaux varient par "
                 "région et par convention — le référentiel le dit déjà pour "
                 "la fiscalité du projet",
     "question": "Quel taux effectif s'applique au véhicule qui portera "
                 "l'actif, après crédits et exonérations ?"},
    {"cle": "montee_ans", "nom": "Montée en charge commerciale (ans)",
     "unite": "ans", "obligatoire": False, "defaut": 3,
     "pourquoi": "un site ne se remplit pas le jour de sa mise en service ; la "
                 "durée de remplissage décide du profil des premières années, "
                 "donc du besoin de trésorerie",
     "question": "En combien d'années le site atteint-il sa charge nominale ?"},
    {"cle": "bfr_meur", "nom": "Besoin en fonds de roulement (M€)",
     "unite": "M€", "obligatoire": False, "defaut": 0.0,
     "pourquoi": "il entre dans les capitaux employés et pèse donc sur le ROCE "
                 "comme sur l'EVA ; le négliger flatte les deux",
     "question": "Quel BFR le plan retient-il, une fois le site en régime ?"},
    {"cle": "maintien_part", "nom": "Investissement de maintien (% du CAPEX/an)",
     "unite": "%", "obligatoire": False, "defaut": 1.0,
     "pourquoi": "le free cash flow se distingue du résultat précisément par "
                 "là : sans capex de maintien, on publie une trésorerie qui "
                 "n'existe pas",
     "question": "Quel montant annuel de renouvellement le plan prévoit-il — "
                 "onduleurs, groupes, GTB ?"},
    {"cle": "amort_ans", "nom": "Durée d'amortissement (ans)",
     "unite": "ans", "obligatoire": False, "defaut": 20,
     "pourquoi": "elle commande la dotation, donc le résultat opérationnel, "
                 "donc les trois indicateurs à la fois",
     "question": "Quelle durée le plan comptable retient-il pour le gros "
                 "œuvre et pour les lots techniques ?"},
]

OBLIGATOIRES = [e["cle"] for e in ENTREES if e["obligatoire"]]
DEFAUTS = {e["cle"]: e["defaut"] for e in ENTREES if "defaut" in e}


# ═══════════════════════════════════════════════════════════════════════════
# 2. LES TROIS INDICATEURS — formule, sens, piège
# ═══════════════════════════════════════════════════════════════════════════
# Le champ `piege` n'est pas de la pédagogie décorative : chacun de ces trois
# indicateurs a un mode de tromperie connu, et c'est celui-là qu'un comité
# d'investissement rencontre. L'écrire à côté du chiffre est la seule façon
# qu'il soit lu au moment où il sert.
INDICATEURS = {
    "eva": {
        "nom": "EVA — Economic Value Added",
        "unite": "M€/an",
        "formule": "NOPAT − (capitaux employés × CMPC)",
        "sens": "La richesse créée AU-DELÀ du coût du capital engagé. Positive, "
                "l'activité rémunère le capital et laisse un surplus ; négative, "
                "elle consomme des ressources sans contrepartie suffisante — "
                "même si le résultat comptable est bénéficiaire.",
        "seuil": 0.0,
        "seuil_sens": "zéro : c'est exactement le point où le projet rémunère "
                      "son capital, ni plus ni moins",
        "piege": "Un résultat net positif n'implique PAS un EVA positif. Un "
                 "projet peut être bénéficiaire et détruire de la valeur, s'il "
                 "immobilise un capital qui rapporterait davantage ailleurs. "
                 "C'est précisément ce que cet indicateur sert à voir.",
        "decision": "hausse",
    },
    "roce": {
        "nom": "ROCE — Return on Capital Employed",
        "unite": "%",
        "formule": "résultat opérationnel ÷ capitaux employés",
        "sens": "L'efficience du capital investi, comparable entre unités, "
                "divisions ou projets de tailles différentes. C'est l'indicateur "
                "qui permet de mettre deux sites côte à côte.",
        "seuil": None,
        "seuil_sens": "il n'y a pas de seuil universel : un ROCE se juge contre "
                      "le CMPC — en dessous, le capital serait mieux employé "
                      "ailleurs — et contre l'objectif que vous fixez",
        "piege": "LES CAPITAUX EMPLOYÉS DIMINUENT AVEC L'AMORTISSEMENT. À "
                 "résultat rigoureusement constant, le ROCE monte chaque année. "
                 "Une courbe ascendante ne prouve donc aucune amélioration : "
                 "c'est l'écart avec la lecture à capitaux BRUTS qui le dit.",
        "decision": "hausse",
    },
    "fcf": {
        "nom": "Free Cash Flow",
        "unite": "M€/an",
        "formule": "NOPAT + dotations − investissement de maintien − Δ BFR",
        "sens": "La trésorerie réellement disponible une fois les "
                "investissements payés. C'est elle qui finance la dette, les "
                "distributions et les projets suivants — pas le résultat.",
        "seuil": 0.0,
        "seuil_sens": "zéro : en dessous, le projet APPELLE de la trésorerie au "
                      "lieu d'en dégager, et il faut dire d'où elle vient",
        "piege": "Un free cash flow élevé obtenu en coupant l'investissement de "
                 "maintien n'est pas une performance : c'est un report de "
                 "charge, et il se paie sur la disponibilité du site.",
        "decision": "hausse",
    },
}

ORDRE = ["eva", "roce", "fcf"]


# ═══════════════════════════════════════════════════════════════════════════
# 3. LE MOTEUR
# ═══════════════════════════════════════════════════════════════════════════
def _f(x, n=2):
    return round(float(x), n)


def _num(v):
    """Rend un nombre, ou None si la valeur est absente ou illisible.

    Le distinguo entre « absent » et « zéro » est tout l'objet de ce module :
    une chaîne vide ne doit jamais devenir 0.0 en chemin."""
    if v is None or v == "":
        return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    if x != x or x in (float("inf"), float("-inf")):   # NaN, ±infini
        return None
    return x


def manquantes(hyp):
    """Les hypothèses obligatoires absentes, avec leur question.

    Rendre la QUESTION et pas seulement le nom du champ : « revenu_meur_an
    manquant » n'apprend rien à un directeur financier, « quel revenu annuel le
    plan retient-il à pleine charge » se répond."""
    hyp = hyp or {}
    trous = []
    for e in ENTREES:
        if not e["obligatoire"]:
            continue
        if _num(hyp.get(e["cle"])) is None:
            trous.append({"cle": e["cle"], "nom": e["nom"],
                          "question": e["question"], "pourquoi": e["pourquoi"]})
    return trous


def _charge(annee, montee_ans):
    """Part du revenu nominal atteinte à l'année n (1 = première année).

    Montée LINÉAIRE, et c'est une hypothèse assumée : aucune source de ce
    référentiel ne décrit une courbe de remplissage. Elle est déclarée dans la
    trace pour qu'on puisse la contester."""
    if montee_ans is None or montee_ans <= 1:
        return 1.0
    return min(1.0, annee / float(montee_ans))


def serie(capex_meur, opex_an_meur, annees, hypotheses):
    """La série annuelle des trois indicateurs, en fourchette.

    `capex_meur` et `opex_an_meur` sont les fourchettes du module d'enveloppe.
    La fourchette est propagée jusqu'au bout : le pire cas combine le CAPEX
    haut et l'OPEX haut, le meilleur les deux bas. Résumer l'enveloppe à son
    milieu avant de calculer ferait disparaître exactement l'information qui
    décide — l'incertitude traverse-t-elle le seuil ?
    """
    trous = manquantes(hypotheses)
    if trous:
        return {"ok": False, "instruit": False, "manquantes": trous,
                "annees": [], "avertissement": AVERTISSEMENT,
                "message": "Sans revenu, coût du capital et taux d'impôt, ces "
                           "trois indicateurs n'ont pas de valeur — ils ne "
                           "valent pas zéro, ils ne sont pas instruits."}

    h = dict(DEFAUTS)
    for cle, v in (hypotheses or {}).items():
        x = _num(v)
        if x is not None:
            h[cle] = x

    annees = int(max(1, min(40, annees or 10)))
    cap_bas, cap_haut = float(min(capex_meur)), float(max(capex_meur))
    op_bas, op_haut = float(min(opex_an_meur)), float(max(opex_an_meur))
    rev = h["revenu_meur_an"]
    wacc = h["wacc"] / 100.0
    impot = h["is_taux"] / 100.0
    amort_ans = max(1.0, h["amort_ans"])
    maintien = h["maintien_part"] / 100.0
    bfr = h["bfr_meur"]

    lignes = []
    for n in range(1, annees + 1):
        part = _charge(n, h["montee_ans"])
        r = rev * part
        # Les capitaux employés sont NETS de l'amortissement cumulé : c'est la
        # définition, et c'est aussi ce qui fait monter le ROCE mécaniquement.
        use = min(1.0, (n - 1) / amort_ans)          # part déjà amortie
        ce_bas = cap_bas * (1.0 - use) + bfr
        ce_haut = cap_haut * (1.0 - use) + bfr
        dot_bas, dot_haut = cap_bas / amort_ans, cap_haut / amort_ans

        # Meilleur cas : OPEX bas, dotation basse, capitaux bas.
        ebit_haut = r - op_bas - dot_bas
        ebit_bas = r - op_haut - dot_haut
        nopat_haut = ebit_haut * (1.0 - impot)
        nopat_bas = ebit_bas * (1.0 - impot)

        eva_haut = nopat_haut - ce_bas * wacc
        eva_bas = nopat_bas - ce_haut * wacc
        roce_haut = (ebit_haut / ce_bas * 100.0) if ce_bas > 0 else None
        roce_bas = (ebit_bas / ce_haut * 100.0) if ce_haut > 0 else None
        # ROCE à capitaux BRUTS : la lecture qui ne bouge pas avec
        # l'amortissement, et sans laquelle une hausse ne se lit pas.
        brut_haut = (ebit_haut / (cap_bas + bfr) * 100.0) if (cap_bas + bfr) > 0 else None
        brut_bas = (ebit_bas / (cap_haut + bfr) * 100.0) if (cap_haut + bfr) > 0 else None

        d_bfr = bfr if n == 1 else 0.0
        fcf_haut = nopat_haut + dot_bas - cap_bas * maintien - d_bfr
        fcf_bas = nopat_bas + dot_haut - cap_haut * maintien - d_bfr

        lignes.append({
            "annee": n,
            "charge": _f(part, 3),
            "revenu_meur": _f(r),
            "capitaux_employes_meur": [_f(ce_bas), _f(ce_haut)],
            "ebit_meur": [_f(ebit_bas), _f(ebit_haut)],
            "eva_meur": [_f(eva_bas), _f(eva_haut)],
            "roce_pct": [None if roce_bas is None else _f(roce_bas, 1),
                         None if roce_haut is None else _f(roce_haut, 1)],
            "roce_brut_pct": [None if brut_bas is None else _f(brut_bas, 1),
                              None if brut_haut is None else _f(brut_haut, 1)],
            "fcf_meur": [_f(fcf_bas), _f(fcf_haut)],
        })

    return {"ok": True, "instruit": True, "annees": lignes,
            "hypotheses": {k: _f(v, 3) for k, v in h.items()},
            "avertissement": AVERTISSEMENT,
            "trace": ("Montée en charge linéaire sur %g an(s) — hypothèse de ce "
                      "module, aucune source ne décrit de courbe de remplissage. "
                      "Capitaux employés nets de l'amortissement cumulé, BFR "
                      "compris. Fourchette propagée : le cas bas combine CAPEX "
                      "et OPEX hauts." % h["montee_ans"]),
            "nature": "calcule"}


# ═══════════════════════════════════════════════════════════════════════════
#  CE QUE L'ENVELOPPE PERMET DE PROPOSER — et ce qu'elle ne permettra jamais
#
#  LE PROBLÈME. Ce bloc présentait sept cases vides. Le lecteur venait de faire
#  calculer une enveloppe complète — investissement, exploitation, DPGF, coût
#  total — et on lui redemandait tout à zéro, sans lui dire lesquelles de ces
#  sept valeurs son propre calcul venait de rendre déductibles. Résultat : on
#  saisit au jugé, ou on renonce.
#
#  LA LIGNE À NE PAS FRANCHIR. Proposer n'est pas inventer. Ce module refuse
#  depuis toujours de publier des références sectorielles, faute d'en avoir de
#  publiables — et cette règle ne change pas ici. Ne sont donc proposées que des
#  valeurs de TROIS natures, toutes trois vérifiables :
#     · `defaut`    — la valeur du référentiel, déjà publiée, déjà motivée ;
#     · `enveloppe` — une grandeur reprise du calcul précédent, telle quelle ;
#     · `seuil`     — de l'ARITHMÉTIQUE sur les valeurs présentes, sans aucune
#                     hypothèse extérieure. Un seuil n'est pas une prévision :
#                     il dit ce qu'il FAUT atteindre, jamais ce qu'on atteindra.
#
#  ET DEUX ENTRÉES RESTENT VIDES, DÉLIBÉRÉMENT. Le coût du capital et le taux
#  d'impôt sont des DÉCISIONS — de comité d'investissement, de montage fiscal.
#  Aucun calcul ne les déduit. Les pré-remplir d'une valeur « courante » ferait
#  passer un choix pour un résultat, et c'est précisément ce que tout ce module
#  s'interdit. Le refus est donc SERVI, avec son motif : mieux vaut une case
#  vide qui s'explique qu'une case remplie qu'on croit.
# ═══════════════════════════════════════════════════════════════════════════

#: Les deux entrées qu'aucun calcul ne peut proposer, et pourquoi.
REFUS_PROPOSITION = {}

# ═══════════════════════════════════════════════════════════════════════════
# 1 bis. CE QU'ON PROPOSE POUR LES TROIS ENTREES OBLIGATOIRES
# ═══════════════════════════════════════════════════════════════════════════
# CE MODULE REFUSAIT DE PROPOSER LE COUT DU CAPITAL ET LE TAUX D'IMPOT, avec un
# motif juste : ce sont des decisions, pas des resultats. Mais un champ vide et
# obligatoire n'est pas neutre non plus — il se remplit au juge, ou il arrete
# le lecteur. On propose donc, EN DISANT DE QUELLE NATURE EST CHAQUE CHIFFRE.
# C'est cette distinction qui fait toute la difference entre proposer et
# inventer, et elle est portee par le champ `nature` :
#
#   · « calcule »   — sorti de VOTRE enveloppe par une formule ecrite. Le
#                     revenu d'equilibre et ses paliers en sont : rien n'y est
#                     suppose, tout se refait a la main.
#   · « statutaire » — un taux nominal publie par un Etat. C'est un fait, pas
#                     un avis ; mais c'est le taux NOMINAL, et le taux effectif
#                     s'en ecarte par les credits, les regimes et les deficits
#                     reportables. Il se confirme aupres d'un conseil fiscal.
#   · « jalon »     — NI un calcul NI une donnee de marche : un reper rond,
#                     pose pour eprouver la sensibilite du resultat. Les quatre
#                     couts du capital en sont. Les presenter comme une
#                     reference sectorielle serait un mensonge sur leur source :
#                     ce module n'a aucune enquete de marche publiable, et en
#                     fabriquer une serait pire que de ne rien proposer.
#
# LE LECTEUR DOIT POUVOIR LIRE CETTE NATURE AU MOMENT OU IL CHOISIT — sinon la
# distinction ne sert a rien. Chaque proposition porte donc son libelle, sa
# formule et sa lecture jusqu'a l'ecran.

# QUATRE JALONS DE COUT DU CAPITAL. Ils ne decrivent pas un marche : ils
# decrivent QUATRE STRUCTURES DE FINANCEMENT, de la plus securisee a la plus
# exposee. L'ecart entre le premier et le dernier vaut le double — c'est
# justement ce que le lecteur doit voir avant de trancher.
CMPC_JALONS = [
    {"valeur": 6.0, "nom": "Dette majoritaire, actif sécurisé",
     "quand": "l'actif est loué à un locataire de premier rang sur un bail "
              "long, et la dette porte l'essentiel du financement"},
    {"valeur": 8.0, "nom": "Structure équilibrée",
     "quand": "part de fonds propres et part de dette comparables, locataire "
              "identifié mais bail non encore signé"},
    {"valeur": 10.0, "nom": "Fonds propres dominants",
     "quand": "développement en blanc, sans locataire engagé : le risque de "
              "commercialisation reste chez l'investisseur"},
    {"valeur": 12.0, "nom": "Prime de risque pays ou contrepartie",
     "quand": "pays à prime de risque, contrepartie non notée, ou horizon de "
              "sortie incertain"},
]

CMPC_RESERVE = (
    "Ces quatre taux ne sont PAS une référence de marché : ce module n'en a "
    "aucune de publiable, et en fabriquer une la rendrait crue. Ce sont quatre "
    "structures de financement, posées pour que vous voyiez de combien le "
    "verdict bouge entre elles — l'écart du simple au double. Le taux qui "
    "jugera votre projet est celui de votre comité d'investissement.")

# TAUX D'IMPOT SUR LES SOCIETES — NOMINAUX ET STATUTAIRES, par pays. Ce sont
# des faits publies, non des avis : c'est ce qui les distingue des jalons
# ci-dessus. Mais ce sont les taux NOMINAUX, combines Etat + local la ou le
# local pese (Allemagne, Italie), et le taux EFFECTIF s'en ecarte toujours.
IS_STATUTAIRE = {
    "FR": (25.0, "impôt sur les sociétés au taux normal"),
    "DE": (30.0, "15 % fédéral + contribution de solidarité + taxe "
                 "professionnelle communale — le total varie avec la commune"),
    "IE": (12.5, "taux des bénéfices d'exploitation"),
    "SE": (20.6, "impôt national sur les sociétés"),
    "NL": (25.8, "taux supérieur ; un taux réduit s'applique aux premiers "
                 "bénéfices"),
    "ES": (25.0, "taux general"),
    "IT": (27.9, "24 % IRES + 3,9 % IRAP, l'IRAP variant par région"),
    "BE": (25.0, "taux normal"),
    "PL": (19.0, "taux normal"),
    "DK": (22.0, "taux normal"),
    "FI": (20.0, "taux normal"),
    "PT": (20.0, "taux normal continental, hors derrama municipale et "
                 "derrama d'État sur les bénéfices élevés"),
    "AT": (23.0, "taux normal"),
    "LU": (24.9, "impôt sur le revenu des collectivités + impôt commercial "
                 "communal, Luxembourg-Ville"),
    "CZ": (21.0, "taux normal"),
    "HU": (9.0, "taux normal — le plus bas de l'Union ; une taxe locale "
                "d'entreprise s'y ajoute"),
    "RO": (16.0, "taux normal"),
    "GR": (22.0, "taux normal"),
    "BG": (10.0, "taux normal"),
    "HR": (18.0, "taux normal au-delà du seuil de chiffre d'affaires"),
    "SI": (22.0, "taux normal"),
    "SK": (21.0, "taux normal ; un taux majoré s'applique aux grandes bases"),
    "LT": (16.0, "taux normal"),
    "LV": (20.0, "sur les bénéfices DISTRIBUÉS : les bénéfices réinvestis ne "
                 "sont pas imposés, ce qui change tout le profil de trésorerie"),
    "EE": (22.0, "sur les bénéfices DISTRIBUÉS : les bénéfices réinvestis ne "
                 "sont pas imposés, ce qui change tout le profil de trésorerie"),
    "CY": (12.5, "taux normal"),
    "MT": (35.0, "taux nominal ; un mécanisme de remboursement aux actionnaires "
                 "abaisse fortement la charge effective"),
}

# LE PLANCHER MONDIAL DE 15 %. Il concerne exactement la population de ce
# module : les groupes au-dela de 750 M€ de chiffre d'affaires consolide, donc
# tout operateur de centre de donnees de cette taille. Retenir 12,5 % en
# Irlande pour un groupe dans le champ produirait un impot sous-estime.
PILIER_DEUX = {
    "taux": 15.0,
    "nom": "Plancher mondial de 15 % (Pilier Deux de l'OCDE)",
    "quand": "groupe dont le chiffre d'affaires consolidé dépasse 750 M€ — "
             "c'est le cas de la plupart des porteurs de projets de cette "
             "taille",
    "lecture": "Un impôt complémentaire ramène la charge effective à 15 % dans "
               "les juridictions où elle serait inférieure. Retenir le taux "
               "national quand il est sous ce plancher sous-estime l'impôt.",
}

IS_RESERVE = (
    "Taux NOMINAUX statutaires, servis à titre indicatif : ils changent, et "
    "plusieurs États les ont modifiés récemment. Le taux EFFECTIF de votre "
    "véhicule s'en écarte par les crédits d'impôt, les régimes locaux, les "
    "déficits reportables et les conventions — c'est lui qu'il faut saisir, et "
    "il se confirme auprès de votre conseil fiscal.")


def seuil_revenu(capex_meur, opex_an_meur, annees, wacc_pct, is_pct,
                 amort_ans=None, bfr_meur=None):
    """Le revenu À PLEINE CHARGE qui annule l'EVA — pas une prévision, un seuil.

    C'est l'inversion exacte de `serie` sur son cas le plus défavorable :

        EVA_bas = (r − OPEX_haut − dotation_haute) × (1 − IS) − CE_haut × CMPC

    posée à zéro et résolue en r. Aucune hypothèse ne s'ajoute : tout vient de
    l'enveloppe déjà calculée et des deux décisions que le lecteur vient de
    prendre.

    DEUX ANNÉES, ET C'EST L'ÉCART QUI INSTRUIT. La première année à pleine
    charge porte des capitaux employés presque intacts : c'est l'année la plus
    exigeante. La dernière les porte largement amortis : c'est la plus facile.
    Un seuil unique cacherait que l'exigence DÉCROÎT mécaniquement, et ferait
    juger tout le projet sur son année la plus dure.
    """
    if wacc_pct is None or is_pct is None:
        return None
    h = dict(DEFAUTS)
    if amort_ans is not None:
        h["amort_ans"] = amort_ans
    if bfr_meur is not None:
        h["bfr_meur"] = bfr_meur
    cap_haut = float(max(capex_meur))
    op_haut = float(max(opex_an_meur))
    n_max = int(max(1, min(40, annees or 10)))
    amort = max(1.0, float(h["amort_ans"]))
    bfr = float(h["bfr_meur"])
    wacc = float(wacc_pct) / 100.0
    impot = float(is_pct) / 100.0
    if impot >= 1.0:
        return None
    dot_haut = cap_haut / amort

    def _r(n):
        use = min(1.0, (n - 1) / amort)
        ce_haut = cap_haut * (1.0 - use) + bfr
        return op_haut + dot_haut + ce_haut * wacc / (1.0 - impot)

    # La première année à PLEINE charge : avant, le revenu nominal serait
    # divisé par la part de charge et gonflerait artificiellement le seuil.
    n1 = int(max(1, min(n_max, round(h["montee_ans"]) or 1)))
    return {
        "premiere_annee_pleine": n1,
        "revenu_seuil_meur": [_f(_r(n_max)), _f(_r(n1))],
        "formule": "r = OPEX_haut + dotation_haute + capitaux_employés_hauts "
                   "× CMPC ÷ (1 − IS), résolu sur le cas le plus défavorable "
                   "de la fourchette d'enveloppe",
        "nature": "seuil",
        "lecture": "Au-dessous de cette fourchette, l'EVA reste négative même "
                   "dans l'hypothèse basse de coûts : le projet détruit de la "
                   "valeur au sens de ce calcul. Ce n'est PAS une prévision de "
                   "chiffre d'affaires — c'est le minimum à battre.",
    }


def _cmpc_proposes():
    """Les quatre jalons de cout du capital, servis a l'identique partout.

    Ils ne dependent d'AUCUN calcul : c'est ce qui permet de les offrir des le
    referentiel, avant meme qu'une enveloppe existe. La fonction est unique
    pour que le referentiel et le calcul ne puissent pas diverger."""
    return [{"origine": "jalon", "nature": "jalon",
             "valeur": j["valeur"],
             "libelle": "%s — %s %%" % (j["nom"], _f(j["valeur"], 1)),
             "formule": "jalon de sensibilité, non une donnée de marché",
             "lecture": "À retenir quand %s." % j["quand"]}
            for j in CMPC_JALONS]


def _is_proposes(pays=None, pays_compares=None):
    """QUATRE TAUX D'IMPOT, tires d'une table statutaire — et du plancher OCDE.

    L'ORDRE EST L'ARGUMENT. Le pays retenu vient en premier, parce que c'est
    celui de l'etude. Le plancher mondial vient ensuite, parce qu'il PRIME sur
    le taux national quand celui-ci lui est inferieur — un groupe dans le champ
    du Pilier Deux qui retiendrait 12,5 % en Irlande sous-estimerait son impot.
    Les deux bornes des pays compares ferment la marche : elles disent de
    combien le verdict bougerait ailleurs, ce qui est exactement la question
    d'une etude qui compare des pays.
    """
    out, vus = [], set()

    def _ajouter(code, taux, libelle, lecture):
        if taux is None or round(float(taux), 2) in vus:
            return
        vus.add(round(float(taux), 2))
        out.append({"origine": "statutaire", "nature": "statutaire",
                    "pays": code, "valeur": _f(float(taux), 1),
                    "libelle": libelle,
                    "formule": "taux statutaire nominal publié",
                    "lecture": lecture})

    if pays and pays in IS_STATUTAIRE:
        t, note = IS_STATUTAIRE[pays]
        _ajouter(pays, t, "%s — taux statutaire %s %%" % (pays, _f(t, 1)),
                 ("Pays retenu par l'étude. " + note[0].upper() + note[1:] + ".")
                 if note else "Pays retenu par l'étude.")

    _ajouter("UE", PILIER_DEUX["taux"], PILIER_DEUX["nom"],
             "%s A retenir pour %s." % (PILIER_DEUX["lecture"],
                                        PILIER_DEUX["quand"]))

    connus = [(c, IS_STATUTAIRE[c][0]) for c in (pays_compares or [])
              if c in IS_STATUTAIRE]
    if connus:
        haut = max(connus, key=lambda x: x[1])
        bas = min(connus, key=lambda x: x[1])
        _ajouter(haut[0], haut[1],
                 "%s — le plus imposé des pays comparés (%s %%)"
                 % (haut[0], _f(haut[1], 1)),
                 "Borne haute de votre comparaison : c'est le cas le moins "
                 "favorable à l'EVA parmi les pays que vous étudiez.")
        _ajouter(bas[0], bas[1],
                 "%s — le moins imposé des pays comparés (%s %%)"
                 % (bas[0], _f(bas[1], 1)),
                 "Borne basse de votre comparaison. Vérifiez d'abord si le "
                 "plancher mondial de 15 %% s'applique à votre groupe : il "
                 "annulerait une partie de cet écart.")
    return out[:4]


def revenus_proposes(capex_meur, opex_an_meur, annees, wacc_pct, is_pct,
                     amort_ans=None, bfr_meur=None):
    """QUATRE NIVEAUX DE REVENU, tous CALCULES sur l'enveloppe — aucun suppose.

    LE PREMIER EST LE SEUIL D'EQUILIBRE : le revenu ou l'EVA s'annule. Les
    trois suivants s'en deduisent par une identite exacte, et non par des
    pourcentages ronds choisis au gout. Poser

        EVA = (r − OPEX − dotation) × (1 − IS) − CE × CMPC = s × CE

    puis soustraire le cas s = 0 laisse

        Δr = s × CE ÷ (1 − IS)

    Chaque palier ajoute donc UN POINT D'EVA rapporte aux capitaux employes.
    C'est la grandeur qui decide d'un GO / NO GO — pas un rendement invente.

    CHAQUE NIVEAU EST AUSSI RENDU EN POURCENTAGE DE L'INVESTISSEMENT TOTAL.
    C'est sous cette forme que la profession raisonne : un revenu annuel se
    juge rapporte a ce que l'actif a coute a construire. Le pourcentage n'est
    pas une source de plus, c'est le meme chiffre sous l'autre angle.
    """
    base = seuil_revenu(capex_meur, opex_an_meur, annees, wacc_pct, is_pct,
                        amort_ans, bfr_meur)
    if not base:
        return []
    h = dict(DEFAUTS)
    if amort_ans is not None:
        h["amort_ans"] = amort_ans
    if bfr_meur is not None:
        h["bfr_meur"] = bfr_meur
    cap_haut = float(max(capex_meur))
    amort = max(1.0, float(h["amort_ans"]))
    bfr = float(h["bfr_meur"])
    impot = float(is_pct) / 100.0
    if impot >= 1.0:
        return []
    n1 = int(base["premiere_annee_pleine"])
    use = min(1.0, (n1 - 1) / amort)
    ce_haut = cap_haut * (1.0 - use) + bfr
    r0 = float(base["revenu_seuil_meur"][1])       # l'annee la plus exigeante

    out = []
    for s in (0.0, 0.01, 0.02, 0.03):
        r = r0 + s * ce_haut / (1.0 - impot)
        out.append({
            "origine": "seuil", "nature": "calcule",
            "spread_pct": _f(s * 100, 0),
            "valeur": _f(r),
            "pct_investissement": _f(r / cap_haut * 100, 1) if cap_haut else None,
            "libelle": ("Revenu d'équilibre — l'EVA s'annule" if s == 0 else
                        "Équilibre + %d point%s d'EVA sur capitaux employés"
                        % (round(s * 100), "s" if s > 0.011 else "")),
            "formule": ("r = OPEX_haut + dotation + CE × CMPC ÷ (1 − IS)" if s == 0
                        else "r = seuil + %d %% × CE ÷ (1 − IS)" % round(s * 100)),
            "lecture": (base["lecture"] if s == 0 else
                        "À ce revenu, le projet dégage %d %% de son capital "
                        "employé au-delà du coût de ce capital — soit %s M€ "
                        "d'EVA la première année à pleine charge."
                        % (round(s * 100), _f(s * ce_haut))),
        })
    return out


def propositions(capex_meur=None, opex_an_meur=None, annees=10, hypotheses=None,
                 pays=None, pays_compares=None):
    """Pour chaque entrée : ce qu'on peut proposer, d'où ça vient, ou pourquoi non.

    Rien n'est appliqué ici. Le module PROPOSE et se justifie ; c'est la page
    qui offre, et le lecteur qui retient. Une valeur poussée d'autorité dans un
    formulaire finit par être crue sans être lue.
    """
    h = dict(hypotheses or {})
    out, proposables = {}, 0
    seuil = None
    if capex_meur and opex_an_meur:
        seuil = seuil_revenu(capex_meur, opex_an_meur, annees,
                             _num(h.get("wacc")), _num(h.get("is_taux")),
                             _num(h.get("amort_ans")), _num(h.get("bfr_meur")))

    for e in ENTREES:
        cle = e["cle"]
        props = []
        if cle in REFUS_PROPOSITION:
            out[cle] = {"propositions": [], "refus": REFUS_PROPOSITION[cle]}
            continue
        if cle == "revenu_meur_an":
            props.extend(revenus_proposes(
                capex_meur, opex_an_meur, annees,
                _num(h.get("wacc")), _num(h.get("is_taux")),
                _num(h.get("amort_ans")), _num(h.get("bfr_meur"))))
            if not props:
                out[cle] = {"propositions": [],
                            "refus": "Les niveaux de revenu se calculent dès que "
                                     "le coût du capital et le taux d'impôt sont "
                                     "renseignés : ils se déduisent l'un de "
                                     "l'autre, et sans eux il n'y a rien à "
                                     "inverser."}
                continue
        elif cle == "wacc":
            # QUATRE STRUCTURES DE FINANCEMENT, pas quatre points de marche.
            # La nature « jalon » voyage avec chaque proposition, et la reserve
            # avec l'entree : sans elles, ces chiffres ronds passeraient pour
            # une reference sectorielle que ce module n'a pas.
            props.extend(_cmpc_proposes())
            out[cle] = {"propositions": props, "refus": None,
                        "reserve": CMPC_RESERVE}
            proposables += 1
            continue
        elif cle == "is_taux":
            props.extend(_is_proposes(pays, pays_compares))
            if not props:
                out[cle] = {"propositions": [],
                            "refus": "Aucun taux statutaire n'est connu pour ce "
                                     "pays dans ce référentiel : l'inventer "
                                     "serait pire que de le laisser vide."}
                continue
            out[cle] = {"propositions": props, "refus": None,
                        "reserve": IS_RESERVE}
            proposables += 1
            continue
        elif cle == "amort_ans":
            # LE RAPPROCHEMENT QUI MANQUAIT. L'enveloppe a été calculée sur une
            # durée d'étude ; amortir sur une autre laisse une valeur résiduelle
            # que personne ne commente. On propose donc les deux, et on le dit.
            props.append({
                "origine": "enveloppe", "nature": "reprise",
                "libelle": "Aligner sur la durée d'étude de l'enveloppe",
                "valeur": _f(float(annees or 10), 0),
                "formule": "durée retenue pour le coût total de possession",
                "lecture": "Amortir sur une durée plus longue que l'étude laisse "
                           "une valeur résiduelle à la fin de l'horizon : elle "
                           "n'apparaît dans aucun des trois indicateurs."})
            props.append({"origine": "defaut", "nature": "defaut",
                          "libelle": "Valeur du référentiel", "valeur": e["defaut"],
                          "formule": "hypothèse par défaut de ce module",
                          "lecture": e["pourquoi"]})
        elif "defaut" in e:
            props.append({"origine": "defaut", "nature": "defaut",
                          "libelle": "Valeur du référentiel", "valeur": e["defaut"],
                          "formule": "hypothèse par défaut de ce module",
                          "lecture": e["pourquoi"]})
        out[cle] = {"propositions": props, "refus": None}
        if props:
            proposables += 1

    refusees = [c for c in out if not out[c]["propositions"]]
    return {
        "entrees": out,
        "seuil_revenu": seuil,
        "resume": {
            "proposables": proposables, "total": len(ENTREES),
            "refusees": sorted(refusees),
            "motif": "Ce module propose ce que le calcul permet de déduire et "
                     "REFUSE le reste. Les entrées sans proposition sont des "
                     "décisions, pas des résultats : les pré-remplir ferait "
                     "passer un choix pour un calcul.",
        },
        "nature": "calcule",
    }


def _traverse(fourchette, seuil):
    """La fourchette traverse-t-elle le seuil ? C'est LA question du GO/NO GO."""
    bas, haut = min(fourchette), max(fourchette)
    if bas > seuil:
        return "au-dessus"
    if haut < seuil:
        return "en-dessous"
    return "traverse"


def _tendance(valeurs):
    """« hausse », « baisse » ou « stable » sur une série de milieux."""
    propres = [v for v in valeurs if v is not None]
    if len(propres) < 2:
        return "indeterminee"
    d = propres[-1] - propres[0]
    ampleur = max(abs(propres[0]), abs(propres[-1]), 1e-9)
    if abs(d) / ampleur < 0.02:
        return "stable"
    return "hausse" if d > 0 else "baisse"


def lecture(s, cibles=None):
    """Ce que la série veut dire — et ce qu'elle ne permet pas de dire.

    C'EST ICI QUE LE MODULE REFUSE DE TRANCHER, et c'est sa fonction la plus
    utile. Trois refus explicites :

      · pas d'hypothèses → rien n'est instruit ;
      · une seule année → aucune tendance ne s'en déduit, et l'évolution est
        justement ce qui porte le sens décisionnel ;
      · une fourchette qui traverse le seuil → le projet crée de la valeur au
        bas de l'enveloppe et en détruit au haut. Aucun avis ne peut sortir de
        là ; ce qu'il faut resserrer, si.
    """
    if not s.get("instruit"):
        return {"ok": False, "instruit": False,
                "manquantes": s.get("manquantes", []),
                "message": s.get("message", "")}

    lignes = s["annees"]
    cibles = cibles or {}
    out = {"ok": True, "instruit": True, "indicateurs": [], "reserves": []}

    if len(lignes) < 2:
        out["reserves"].append(
            "Un seul exercice : aucune évolution ne s'en déduit. Ces trois "
            "indicateurs ne s'interprètent pas sur un point — c'est leur "
            "trajectoire, et leur écart à un objectif, qui décident.")

    # Le régime de croisière : on juge sur l'année où la charge est atteinte,
    # pas sur la première, qui ne dit que la montée en puissance.
    regime = next((l for l in lignes if l["charge"] >= 0.999), lignes[-1])

    for cle in ORDRE:
        meta = INDICATEURS[cle]
        champ = {"eva": "eva_meur", "roce": "roce_pct", "fcf": "fcf_meur"}[cle]
        f = regime[champ]
        if f[0] is None or f[1] is None:
            continue
        milieux = [(l[champ][0] + l[champ][1]) / 2.0
                   for l in lignes if l[champ][0] is not None]
        item = {
            "cle": cle, "nom": meta["nom"], "unite": meta["unite"],
            "formule": meta["formule"], "sens": meta["sens"],
            "piege": meta["piege"],
            "annee_regime": regime["annee"],
            "fourchette": f,
            "tendance": _tendance(milieux),
        }

        seuil = meta["seuil"]
        if seuil is not None:
            pos = _traverse(f, seuil)
            item["position"] = pos
            if pos == "traverse":
                item["verdict"] = "indecidable"
                item["dit"] = (
                    "L'incertitude de l'enveloppe TRAVERSE le seuil : de %s à "
                    "%s %s. Le projet crée de la valeur au bas de la fourchette "
                    "et en détruit au haut — aucun avis ne peut sortir de là. "
                    "Ce qui le rendrait décidable : un coût unitaire de vos "
                    "devis à la place de l'hypothèse de filière, et les postes "
                    "encore à renseigner."
                    % (_f(f[0]), _f(f[1]), meta["unite"]))
            elif pos == "au-dessus":
                item["verdict"] = "favorable"
                item["dit"] = ("Positif sur toute la fourchette (%s à %s %s) : "
                               "la conclusion ne dépend pas de l'incertitude "
                               "d'enveloppe." % (_f(f[0]), _f(f[1]), meta["unite"]))
            else:
                item["verdict"] = "defavorable"
                item["dit"] = ("Négatif sur toute la fourchette (%s à %s %s) : "
                               "là non plus, l'incertitude d'enveloppe ne change "
                               "pas la conclusion."
                               % (_f(f[0]), _f(f[1]), meta["unite"]))
        else:
            item["verdict"] = "a_comparer"
            item["dit"] = meta["seuil_sens"]

        # LE PIÈGE DU ROCE, MESURÉ ET NON SEULEMENT ÉNONCÉ.
        if cle == "roce":
            bruts = [(l["roce_brut_pct"][0] + l["roce_brut_pct"][1]) / 2.0
                     for l in lignes if l["roce_brut_pct"][0] is not None]
            t_brut = _tendance(bruts)
            item["tendance_brute"] = t_brut
            if item["tendance"] == "hausse" and t_brut != "hausse":
                item["alerte"] = (
                    "La hausse du ROCE est MÉCANIQUE : elle vient de "
                    "l'amortissement, qui réduit les capitaux employés. À "
                    "capitaux bruts, la tendance est « %s ». Aucune "
                    "amélioration de performance ne s'en déduit." % t_brut)

        cible = _num(cibles.get(cle))
        if cible is not None:
            item["cible"] = cible
            mil = (f[0] + f[1]) / 2.0
            item["ecart_cible"] = _f(mil - cible)
            item["atteint"] = "oui" if f[0] >= cible else (
                "non" if f[1] < cible else "incertain")
        else:
            item["atteint"] = "non_compare"
            item["sans_cible"] = (
                "Aucun objectif n'a été fixé pour cet indicateur, et ce "
                "référentiel n'en propose pas : une référence sectorielle "
                "inventée serait crue. Sans objectif, on lit une trajectoire, "
                "pas une réussite.")

        out["indicateurs"].append(item)

    if all(i.get("verdict") == "favorable"
           for i in out["indicateurs"] if "position" in i) \
            and any("position" in i for i in out["indicateurs"]):
        out["synthese"] = ("Sur les hypothèses fournies, la création de valeur "
                           "est acquise sur toute la fourchette d'enveloppe.")
    elif any(i.get("verdict") == "indecidable" for i in out["indicateurs"]):
        out["synthese"] = ("La décision ne peut pas se prendre sur ces "
                           "indicateurs en l'état : l'incertitude d'enveloppe "
                           "traverse le seuil de création de valeur.")
    else:
        out["synthese"] = ("Les hypothèses fournies ne montrent pas de création "
                           "de valeur sur la fourchette d'enveloppe.")

    out["reserves"].append(
        "Ces indicateurs valent ce que valent les hypothèses de revenu, de coût "
        "du capital et d'impôt. Elles viennent de vous : le référentiel n'en "
        "porte aucune.")
    return out


# ═══════════════════════════════════════════════════════════════════════════
# 4. CE QUE CE MODULE NE FAIT PAS ENCORE
# ═══════════════════════════════════════════════════════════════════════════
# Écrit plutôt que laissé à deviner : un lecteur qui ne trouve pas la VAN dans
# un bloc financier ne sait pas si elle a été jugée inutile, oubliée, ou
# reportée. La feuille de route financière annoncée reprendra ces points.
SUITE = [
    {"quoi": "VAN et TRI actualisés",
     "manque": "un taux d'actualisation — le module d'enveloppe refuse déjà "
               "de le choisir à votre place, et ce refus vaut ici",
     "apporte": "la comparaison entre projets de durées différentes"},
    {"quoi": "Structure de financement — dette, fonds propres, effet de levier",
     "manque": "le plan de financement : montant, taux, durée, covenants",
     "apporte": "le passage du ROCE au ROE, et le service de la dette dans le "
                "free cash flow"},
    {"quoi": "Valeur terminale et sortie",
     "manque": "l'horizon de détention et le multiple de sortie retenus",
     "apporte": "le rendement total pour l'actionnaire, que le TCO ignore"},
    {"quoi": "Sensibilité et scénarios",
     "manque": "rien : c'est le prolongement direct de la fourchette déjà "
               "propagée ici",
     "apporte": "le rang des variables qui décident — prix de l'électricité, "
                "taux de charge, coût unitaire"},
    {"quoi": "Références sectorielles",
     "manque": "une source publiable et datée ; en inventer une la rendrait "
               "crue, et ce module s'interdit ce qu'il reproche aux autres",
     "apporte": "la comparaison qui manque aujourd'hui à chaque indicateur"},
]


def referentiel():
    """Ce que la page doit savoir pour composer le bloc."""
    return {"version": VERSION, "avertissement": AVERTISSEMENT,
            "entrees": ENTREES, "obligatoires": OBLIGATOIRES,
            # LES PROPOSITIONS QUI NE DEPENDENT D'AUCUN CALCUL VOYAGENT AVEC LE
            # REFERENTIEL. Les quatre jalons de cout du capital ne dependent de
            # rien ; le plancher mondial de 15 % non plus. Ne les servir qu'avec
            # le premier calcul les rendait absents au moment ou le lecteur
            # decouvre le formulaire — c'est-a-dire au moment ou il en a besoin.
            # ELLES SONT PRODUITES PAR LES MEMES FONCTIONS que les propositions
            # du POST : recopier la liste ici en ferait deux exemplaires qui
            # divergeraient au premier ajustement.
            "propositions_statiques": {
                "wacc": {"propositions": _cmpc_proposes(),
                         "reserve": CMPC_RESERVE},
                "is_taux": {"propositions": _is_proposes(None, None),
                            "reserve": IS_RESERVE},
            },
            # LES REFUS VOYAGENT AVEC LE REFERENTIEL, et non plus seulement
            # avec le calcul. Une entree obligatoire, vide et sans motif se lit
            # comme un oubli du site : le lecteur la remplit au juge, ou
            # attend. Le motif etait pourtant ecrit — il n'arrivait qu'apres un
            # premier calcul, c'est-a-dire apres le moment ou il servait.
            "refus_proposition": dict(REFUS_PROPOSITION),
            # ORDRE est servi comme LISTE : un dictionnaire JSON se fait
            # réordonner alphabétiquement en chemin, et « eva, fcf, roce » ne
            # raconte pas la même histoire que « eva, roce, fcf ».
            "ordre": ORDRE,
            "indicateurs": {k: dict(INDICATEURS[k]) for k in ORDRE},
            "suite": SUITE}


def sante():
    return {"module": "kpi_finance", "version": VERSION,
            "indicateurs": len(INDICATEURS), "entrees": len(ENTREES),
            "obligatoires": len(OBLIGATOIRES), "suite": len(SUITE),
            "portee": "Ne calcule rien sans hypothèses de revenu, de coût du "
                      "capital et d'impôt. Il en PROPOSE désormais, en disant "
                      "de quelle nature est chaque chiffre : « calculé » pour "
                      "les niveaux de revenu, tirés de votre enveloppe ; "
                      "« statutaire » pour les taux d'impôt nominaux, qui sont "
                      "des faits publiés ; « jalon » pour les coûts du capital, "
                      "qui ne sont NI un calcul NI une donnée de marché — ce "
                      "module n'a aucune enquête sectorielle publiable, et il "
                      "ne prétend pas en avoir une.",
            "propositions": {"revenu": 4, "wacc": len(CMPC_JALONS),
                             "is_pays": len(IS_STATUTAIRE)}}


def _verifier():
    """Refuse de charger si le module ment sur ce qu'il porte."""
    if set(ORDRE) != set(INDICATEURS):
        raise RuntimeError("kpi_finance : ORDRE et INDICATEURS divergent")
    if ORDRE[0] != "eva":
        raise RuntimeError(
            "kpi_finance : l'EVA ouvre la lecture — c'est le seul des trois "
            "qui répond à « ce projet crée-t-il de la valeur ? »")
    for cle, m in INDICATEURS.items():
        for champ in ("nom", "unite", "formule", "sens", "piege", "seuil_sens"):
            if not str(m.get(champ, "")).strip():
                raise RuntimeError("kpi_finance : %s sans %s" % (cle, champ))
        if len(m["piege"]) < 80:
            raise RuntimeError(
                "kpi_finance : le piège de %s est trop court pour être utile — "
                "c'est lui qui empêche de mal lire le chiffre" % cle)
    if not OBLIGATOIRES:
        raise RuntimeError(
            "kpi_finance : aucune hypothèse obligatoire — le module rendrait "
            "alors des chiffres sans que personne ait dit ce que le projet "
            "rapporte")
    for e in ENTREES:
        for champ in ("cle", "nom", "unite", "pourquoi", "question"):
            if not str(e.get(champ, "")).strip():
                raise RuntimeError("kpi_finance : entrée %s sans %s"
                                   % (e.get("cle"), champ))
    for s in SUITE:
        for champ in ("quoi", "manque", "apporte"):
            if not str(s.get(champ, "")).strip():
                raise RuntimeError("kpi_finance : SUITE sans %s" % champ)


_verifier()
