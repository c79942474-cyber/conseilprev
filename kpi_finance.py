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
                      "capital et d'impôt ; ne propose aucune référence "
                      "sectorielle, faute de source publiable."}


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
