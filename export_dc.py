# -*- coding: utf-8 -*-
"""Dossiers téléchargeables du Panorama « IA & centres de données » — Word et PDF.

POURQUOI CE MODULE EXISTE

Un chiffre lu à l'écran ne sert à rien : il finit dans une note d'investissement,
un dossier de crédit, un mémoire technique de réponse à appel d'offres. Tant
qu'il faut le recopier à la main, il perd en route ce qui fait sa valeur — sa
NATURE, sa SOURCE, son MILLÉSIME et ce que le module refuse de trancher. Ce
module produit le document complet, avec tout cela attaché.

CE QUI DISTINGUE CES DOCUMENTS DES LIVRABLES RÉDIGÉS

Aucun modèle de langage n'intervient ici. Le contenu est composé par ce fichier
à partir des modules de calcul (`finance_dc`, `implantation`, `tendances_dc`,
`datacentres`, `empreinte_sites`), tous déterministes et versionnés. Les
documents portent donc `ia=False` : ils ne reçoivent PAS le marquage article 50,
et le disent en toutes lettres. Apposer ce marquage partout reviendrait à ne
plus rien signaler là où il compte.

CE QUE CHAQUE DOSSIER DOIT PORTER, SANS EXCEPTION

  1. la VERSION de chaque référentiel mobilisé, et la date de génération ;
  2. la NATURE de chaque valeur — relevé publié, calcul, hypothèse, saisie ;
  3. ce que le module NE PEUT PAS trancher, écrit en clair et non masqué ;
  4. les RÉSERVES : les valeurs qu'un fait postérieur rend optimistes.

Un document exporté circule sans nous. Il doit se défendre seul.
"""
from datetime import datetime, timezone

import datacentres
import empreinte_sites
import finance_dc
import implantation
import tendances_dc

VERSION = "2026-08-b"

# LES FIGURES QUE LA PAGE PEUT JOINDRE. Les cartes du Panorama sont dessinees
# par le navigateur a partir de ces memes calculs : lui seul les a sous la
# main. La cle est le contrat entre la page et ce module — elle ne s'invente
# pas des deux cotes. Le chapitre ou chacune se pose est ecrit ci-dessous.
FIGURES = (
    ("carte-parc", "Carte des centres de donnees et des systemes d'IA deployes"),
    ("carte-implantation", "Comparateur pondere — classement des pays"),
    ("carte-enveloppe", "Enveloppe d'investissement — pays compares"),
    # PAS DE CARTE POUR L'EMPREINTE : ce panneau n'en dessine pas. Declarer la
    # cle aurait produit un « figure non jointe » a chaque export, que rien ne
    # pouvait satisfaire.
)

DOSSIERS = {
    "enveloppe": {
        "nom": "Enveloppe d'investissement et DPGF",
        "resume": "Enveloppe, décomposition en 14 lots, exploitation, coût total de "
                  "possession, échéancier 2030, écarts entre pays et postes non chiffrables.",
        "besoin_devis": True,
    },
    "prospectives": {
        "nom": "Prospectives 2026-2030",
        "resume": "Tendances 2026, jalons réglementaires datés, structure de marché et "
                  "réserves sur le référentiel — chaque entrée avec sa citation et sa page.",
        "besoin_devis": False,
    },
    "implantation": {
        "nom": "Référentiel de choix d'implantation",
        "resume": "Par pays : intensité carbone, mix, stress hydrique, climat de "
                  "refroidissement, prix industriels, parc et file de raccordement, "
                  "avantages et inconvénients.",
        "besoin_devis": False,
    },
    "parc": {
        "nom": "Parc de centres de données et empreinte",
        "resume": "Les centres recensés, leur statut, leur gabarit et la confiance de "
                  "chaque source ; empreinte du parc et limites de l'estimation.",
        "besoin_devis": False,
    },
    "complet": {
        "nom": "Dossier complet — centres de données et IA dans l'Union",
        "resume": "Les quatre dossiers réunis, dans l'ordre de lecture d'une décision "
                  "d'investissement.",
        "besoin_devis": True,
    },
    # LE DOSSIER D'INGÉNIERIE FINANCIÈRE. Il verse les réponses des quatre
    # moteurs de la page — équipements, création de valeur, maturité,
    # pilotage — TELLES QUE SERVIES : le document et l'écran montrent la même
    # chose, ou le document écrit qu'un bloc n'a pas été lancé. Il ne recalcule
    # rien : recalculer ferait diverger les deux au premier écart.
    "ingenierie": {
        "nom": "Ingénierie financière — équipements, valeur, maturité, pilotage",
        "resume": "Nomenclature des équipements informatiques et leur carbone, "
                  "EVA / ROCE / flux de trésorerie disponibles, diagnostic de "
                  "maturité et tableau de pilotage — chaque bloc tel que la page "
                  "l'a calculé, avec ses refus et ses incertitudes.",
        "besoin_devis": False,
    },
}

FORMATS = ("docx", "pdf")

# La marque de ce site, et le pied de page qui va avec. Un dossier
# d'investissement en centres de données ne se présente pas sous l'enseigne
# « Cybersécurité industrielle IT / OT / IIoT ».
MARQUE = {
    "marque_suffixe": "Sentinel",
    "bandeau": "Conformité IA Act & RGPD · Panorama des centres de données européens",
    "contact": ("CONSEILPREV · christophe.cerf@outlook.com · +33 6 60 69 21 45 · "
                "conseilprev.onrender.com"),
    "ia": False,
}


# ═══════════════════════════════════════════════════════════════════════════
# Petits formateurs — le français, et rien que le français
# ═══════════════════════════════════════════════════════════════════════════

def _n(x, d=1):
    """Nombre à la française. Un « 1,234.5 » dans une note en français se voit,
    et fait douter de tout le reste du document."""
    if x is None:
        return "—"
    try:
        v = round(float(x), d)
    except (TypeError, ValueError):
        return str(x)
    if d == 0 or v == int(v):
        s = "{:,.0f}".format(v)
    else:
        s = "{:,.{d}f}".format(v, d=d)
    return s.replace(",", " ").replace(".", ",")


def _f(paire, d=1, unite=""):
    """Fourchette. Une valeur unique se donne seule, sans faux intervalle."""
    if not paire:
        return "—"
    if isinstance(paire, (int, float)):
        return _n(paire, d) + (" " + unite if unite else "")
    a, b = paire[0], paire[1]
    if a == b:
        return _n(a, d) + (" " + unite if unite else "")
    return _n(a, d) + " – " + _n(b, d) + (" " + unite if unite else "")


def _pct(x):
    if x is None:
        return "—"
    return str(x).replace(".", ",") + " %"


def _esc(t):
    """Le pipe est le séparateur de colonnes du Markdown : un texte qui en
    contient casse la table sans prévenir."""
    return str("" if t is None else t).replace("|", "/").replace("\n", " ").strip()


def _tab(entetes, lignes):
    out = ["| " + " | ".join(_esc(h) for h in entetes) + " |",
           "|" + "|".join(["---"] * len(entetes)) + "|"]
    for l in lignes:
        out.append("| " + " | ".join(_esc(c) for c in l) + " |")
    return "\n".join(out) + "\n"


def _horodatage():
    return datetime.now(timezone.utc).strftime("%d/%m/%Y à %H:%M UTC")


# ═══════════════════════════════════════════════════════════════════════════
# 1. ENVELOPPE ET DPGF
# ═══════════════════════════════════════════════════════════════════════════

def md_enveloppe(devis_reponse):
    """`devis_reponse` est la charge utile de /api/finance-dc/devis, telle
    quelle : le document et l'écran montrent donc rigoureusement la même chose.
    Reconstituer les chiffres ici ferait diverger les deux au premier écart."""
    j = devis_reponse or {}
    e = j.get("entree") or {}
    L = []
    a = L.append

    a("# Enveloppe d'investissement et DPGF — décision GO / NO GO\n")
    a("![Les pays comparés — coût total de possession](fig:carte-enveloppe)\n")
    a("## Ce que ce dossier chiffre, et ce qu'il refuse de chiffrer\n")
    a("Ce dossier structure une enveloppe d'investissement et sa décomposition par "
      "lot pour un centre de données, puis compare les pays sur le **coût total de "
      "possession**. Trois avertissements doivent être lus avant les chiffres.\n")
    a("**Il ne fabrique pas VOTRE prix.** Le coût au mégawatt provient d'un relevé "
      "publié — Soben (part of Accenture), *Data Centre Trends Report 2026*, p. 8 : "
      "« cloud data centres currently cost between $8 million and $10 million per MW, "
      "GW+ AI data centres are costing as much as $17 million per MW ». La source est "
      "en **dollars** ; la conversion passe par un taux affiché et modifiable, un taux "
      "du jour n'étant pas une donnée de référentiel. Elle couvre le cloud et les "
      "campus d'IA, **pas** la colocation ni le site régional. Elle reste un ordre de "
      "grandeur de marché : rien ici ne remplace vos devis.\n")
    a("**À puissance égale, l'enveloppe est identique d'un pays à l'autre**, faute "
      "d'indice national de coût de construction dans ce référentiel. Ce qui départage "
      "les pays se lit sur le coût total de possession, où le prix de l'électricité "
      "multiplié par le PUE creuse des écarts de plus du quart sur dix ans. Un "
      "classement établi sur le seul investissement afficherait une égalité parfaite.\n")
    a("**Cinq postes s'affichent vides**, avec la question à poser : ils peuvent "
      "renverser le classement à eux seuls, et les masquer donnerait l'illusion d'une "
      "décision complète.\n")

    a("## Paramètres retenus\n")
    a(_tab(["Paramètre", "Valeur"], [
        ["Puissance informatique", _n(e.get("mw"), 1) + " MW"],
        ["Gabarit", (finance_dc.COUT_MW.get(e.get("gabarit")) or {}).get("nom", e.get("gabarit"))],
        ["Scénario", (finance_dc.SCENARIOS.get(e.get("scenario")) or {}).get("nom", e.get("scenario"))],
        ["Densité IA (refroidissement liquide)", "oui" if e.get("densite_ia") else "non"],
        ["Calendrier", (finance_dc.PRIME_VITESSE.get(e.get("vitesse")) or {}).get("nom", e.get("vitesse"))],
        ["Coût unitaire", (_f(e.get("cout_mw"), 2, "M€/MW")
                           if isinstance(e.get("cout_mw"), (list, tuple))
                           else "issu du relevé publié (voir ci-dessus)")],
        ["Horizon d'exploitation", str(e.get("annees")) + " ans"],
        ["Année de démarrage", str(e.get("depart"))],
        ["Pays comparés", ", ".join(e.get("pays") or [])],
    ]))

    # Ce que le lecteur a IMPOSÉ. Un dossier qui tait ses paramètres de
    # conception laisse croire que tout a été déduit — et rend ses chiffres
    # incontestables faute d'être reproductibles.
    C = e.get("conception") or {}
    if C:
        LIB = {"refroidissement": "Famille de refroidissement imposée",
               "classe_ashrae": "Classe d'air admise (ASHRAE TC 9.9)",
               "pue_impose": "PUE imposé par le cahier des charges",
               "charge": "Taux de charge moyen",
               "prix_contrat": "Prix contractuel de l'électricité (€/MWh)",
               "intensite_contrat": "Intensité carbone du contrat (gCO₂e/kWh)",
               "part_sans_carbone": "Part d'énergie sans carbone contractualisée"}
        a("### Critères de conception que vous avez imposés\n")
        a("Chacun remplace une déduction de ce référentiel par **votre** donnée. Les "
          "postes concernés portent la nature *saisi* : le dossier dit que c'est vous "
          "qui les engagez, pas nous.\n")
        a(_tab(["Critère", "Valeur retenue"],
               [[LIB.get(k, k),
                 (finance_dc.REFROIDISSEMENT.get(v, {}).get("nom") if k == "refroidissement"
                  else finance_dc.CLASSES_ASHRAE.get(v, {}).get("nom") if k == "classe_ashrae"
                  else _n(v, 3))]
                for k, v in C.items()]))
    else:
        a("*Aucun critère de conception n'a été imposé : le refroidissement, le PUE, le "
          "taux de charge et le prix de l'électricité sont déduits du référentiel pays. "
          "Le formulaire permet de les remplacer par vos propres données.*\n")

    cl = j.get("classement") or []
    if cl:
        a("## Classement — sur le coût total de possession, pas sur l'investissement\n")
        a(_tab(["Rang", "Pays", "Coût total (M€)", "Exploitation (M€/an)",
                "CO₂e (t/an)", "Durée (mois)", "Livrable avant 2030"],
               [[str(i + 1), x.get("pays"), _f(x.get("tco_meur"), 0),
                 _f(x.get("opex_meur_an"), 1), _f(x.get("co2_t_an"), 0),
                 _f(x.get("duree_mois"), 0),
                 "oui" if x.get("tient_2030") else "**non**"]
                for i, x in enumerate(cl)]))

    for d in (j.get("dossiers") or []):
        dev = d.get("devis") or {}
        ctx = d.get("contexte") or {}
        a("## %s — enveloppe %s M€\n" % (d.get("pays"), _f(dev.get("enveloppe_meur"), 0)))

        cm = dev.get("cout_mw") or {}
        a("**Coût unitaire retenu :** %s M€/MW%s — nature *%s*, source : %s.\n"
          % (_f(cm.get("valeur"), 2),
             (" (%s M$/MW au taux %s)" % (_f(cm.get("musd_mw"), 1),
                                          str(cm.get("taux_eur_usd")).replace(".", ",")))
             if cm.get("musd_mw") else "",
             cm.get("nature"), cm.get("source")))
        vit = dev.get("vitesse") or {}
        if vit and vit.get("coef") not in (None, 1):
            a("**Calendrier %s :** +%d %% sur l'enveloppe pour %d mois gagnés au mieux. "
              "La prime achète la priorité d'une entreprise générale, jamais l'accord du "
              "gestionnaire de réseau : le délai de raccordement reste plancher.\n"
              % (vit.get("nom"), round((vit.get("coef") - 1) * 100), vit.get("mois_gagnes") or 0))
        froid = dev.get("refroidissement") or {}
        racc = dev.get("raccordement") or {}
        a("**Refroidissement retenu :** %s%s (PUE %s — nature *%s*, eau %s), climat *%s* "
          "et stress hydrique *%s*. **Raccordement :** %s — %s projets déclarés pour %s "
          "sites en service. **Durée de projet :** %s mois.\n"
          % (froid.get("nom"), " — **imposé**" if froid.get("impose") else " (déduit)",
             _f(froid.get("pue"), 3), froid.get("pue_nature"), froid.get("eau"),
             (ctx.get("climat") or {}).get("classe"), (ctx.get("eau") or {}).get("classe"),
             racc.get("nom"), ctx.get("pipeline_2030"), ctx.get("en_service"),
             _f(dev.get("duree_mois"), 0)))
        if froid.get("pue_note"):
            a("*%s*\n" % _esc(froid["pue_note"]))

        a("### Décomposition par lot (DPGF)\n")
        # `arenseigner` marque les lots dont une composante n'est PAS chiffrable.
        # Le signe ⚑ le dit dans le tableau, et la colonne « question » donne au
        # lecteur la phrase exacte à poser à son constructeur.
        a(_tab(["Code", "Lot", "Part", "Montant (M€)", "Modulation", "À vérifier auprès du constructeur"],
               [[(l.get("code") or "") + (" ⚑" if l.get("arenseigner") else ""),
                 l.get("nom"), _pct(l.get("part")), _f(l.get("meur"), 1),
                 l.get("detail_coef") or "—", l.get("question") or "—"]
                for l in (dev.get("lots") or [])]))
        a("*Les parts somment à 100 % et les montants reconstituent l'enveloppe : un "
          "tableau qui ne boucle pas est un tableau faux. Les lots marqués ⚑ contiennent "
          "un poste que ce référentiel ne peut pas chiffrer.*\n")
        a("#### Ce que recouvre chaque lot\n")
        for l in (dev.get("lots") or []):
            a("- **%s — %s :** %s\n" % (_esc(l.get("code")), _esc(l.get("nom")),
                                        _esc(l.get("recouvre"))))

        ex = d.get("exploitation") or {}
        tco = d.get("tco") or {}
        a("### Exploitation annuelle\n")
        a("Charge retenue : %s %% de la puissance installée.\n"
          % _n((ex.get("charge") or 0) * 100, 0))
        a(_tab(["Poste", "M€/an", "Nature", "Formule"],
               [[p.get("nom"), _f(p.get("meur_an"), 2), p.get("nature"), p.get("formule")]
                for p in (ex.get("postes") or [])]
               + [["**Total exploitation**", "**" + _f(ex.get("total_meur_an"), 1) + "**",
                   "calcule", "somme des postes"]]))
        carb = ex.get("carbone") or {}
        if carb:
            a("**Émissions du site :** %s tCO₂e par an — %s. Valorisation : %s M€/an "
              "(nature *%s*).\n"
              % (_f(carb.get("t_co2e_an"), 0), _esc(carb.get("formule")),
                 _f(carb.get("cout_meur_an"), 2), carb.get("nature")))

        a("### Coût total de possession\n")
        a(_tab(["Poste", "M€"],
               [["Investissement (CAPEX)", _f(tco.get("capex_meur"), 0)],
                ["Exploitation cumulée sur %s ans" % tco.get("annees"),
                 _f(tco.get("opex_cumule_meur"), 0)],
                ["**Total**", "**" + _f(tco.get("total_meur"), 0) + "**"]]))
        if tco.get("note"):
            a("*" + _esc(tco["note"]) + "*\n")

        inc = d.get("incorpore") or {}
        if inc.get("postes"):
            a("### Carbone incorporé de la construction\n")
            a("L'exploitation seule flatte les sites neufs face à une reprise de bâtiment "
              "existant. Sans cette ligne, la comparaison entre scénarios est biaisée — et "
              "un dossier CSRD est incomplet dès sa première page.\n")
            a(_tab(["Poste", "tCO₂e", "Durée de vie", "tCO₂e/an", "Formule"],
                   [[x.get("nom"), _n(x.get("t_co2e"), 0), str(x.get("duree_vie_ans")) + " ans",
                     _n(x.get("t_co2e_an"), 0), x.get("formule")] for x in inc["postes"]]
                   + [["**Total amorti**", "**" + _n(inc.get("total_t_co2e"), 0) + "**", "—",
                       "**" + _n(inc.get("total_t_co2e_an"), 0) + "**",
                       "nature : " + str(inc.get("nature"))]]))
            a("*%s %s*\n" % (_esc(inc.get("note")), _esc(inc.get("source"))))

        conf = d.get("conformite") or {}
        if conf.get("reperes"):
            a("### Repères de marché\n")
            a(_tab(["Indicateur", "Valeur retenue", "Cible", "Verdict", "Ce que cela veut dire"],
                   [[r.get("nom"), _n(r.get("valeur"), 3), _n(r.get("cible"), 2),
                     r.get("verdict"), r.get("sens")] for r in conf["reperes"]]))
            a("*Source : %s — %s*\n" % (_esc(conf.get("source")), _esc(conf.get("note"))))

        alerte = (d.get("exploitation") or {}).get("charge_alerte")
        if alerte:
            a("**Alerte de charge partielle —** %s\n" % _esc(alerte))

        aren = dev.get("arenseigner") or []
        if aren:
            a("### Ce que ce dossier ne peut PAS trancher — %d postes\n" % len(aren))
            a("Ces postes sont laissés **vides** à dessein. Chacun peut renverser le "
              "classement à lui seul ; les estimer donnerait l'illusion d'une décision "
              "complète.\n")
            a(_tab(["Poste", "Lot", "Pourquoi il manque"],
                   [[x.get("nom"), x.get("lot") or "transverse", x.get("pourquoi")]
                    for x in aren]))

        traj = d.get("trajectoire") or {}
        if traj.get("phases"):
            a("### Échéancier jusqu'en 2030\n")
            a(_tab(["Phase", "Lots", "Début", "Fin", "Durée (mois)", "Part", "Montant (M€)"],
                   [[p.get("nom"), ", ".join(p.get("lots") or []), str(p.get("debut")),
                     str(p.get("fin")) + (" — dépasse 2030" if p.get("depasse_2030") else ""),
                     _f(p.get("duree_mois"), 0), _pct(p.get("part")), _f(p.get("meur"), 1)]
                    for p in traj["phases"]]))
            a("**Mise en service estimée :** %s (durée totale %s mois). %s\n"
              % (_f(traj.get("mise_en_service"), 0), _f(traj.get("duree_totale_mois"), 0),
                 "L'échéance 2030 est tenue."
                 if traj.get("tient_2030") else
                 "**L'échéance 2030 n'est PAS tenue** dans l'hypothèse haute."))
            if traj.get("avis"):
                a("**Ce qu'il faut en faire :** %s\n" % _esc(traj["avis"]))
            jp = traj.get("jalons_pays") or []
            if jp:
                a("**Jalons datés qui pèsent sur ce calendrier :**\n")
                for jl in jp:
                    a("- **%s** — %s *(%s)*\n" % (_esc(jl.get("date")), _esc(jl.get("quoi")),
                                                  _esc(jl.get("source"))))

        pro = d.get("prospective") or {}
        for r in (pro.get("reserves") or []):
            a("### Réserve sur le référentiel — critère « %s », depuis %s\n"
              % (r.get("critere"), r.get("depuis")))
            a("**Valeur utilisée dans ce calcul :** %s\n" % _esc(r.get("valeur_referentiel")))
            a(_esc(r.get("reserve")) + "\n")
            a("*Cette réserve n'est pas appliquée au calcul ci-dessus : elle vous est "
              "remise pour que vous décidiez si elle change votre arbitrage.*\n")

    for ec in (j.get("ecarts") or []):
        pa, pb = (ec.get("a") or {}).get("pays"), (ec.get("b") or {}).get("pays")
        a("## Écart %s / %s\n" % (pa, pb))
        if ec.get("capex_identique"):
            a("**L'investissement est identique entre ces deux pays** (%s M€, écart %s) — "
              "%s\n" % (_n(ec.get("ecart_capex_meur"), 1), _pct(ec.get("ecart_capex_pct")),
                        _esc(ec.get("note_capex"))))
        if ec.get("ecart_tco"):
            t = ec["ecart_tco"]
            a("**Coût total sur %s ans :** %s contre %s M€, soit %s M€ (%s) — avantage "
              "**%s**.\n" % (t.get("annees"), _f(t.get("a_meur"), 0), _f(t.get("b_meur"), 0),
                             _n(t.get("ecart_meur"), 1), _pct(t.get("ecart_pct")),
                             t.get("avantage")))
        if ec.get("ecart_carbone"):
            c = ec["ecart_carbone"]
            a("**Carbone :** %s contre %s tCO₂e par an, soit %s (%s).\n"
              % (_f(c.get("a_t_an"), 0), _f(c.get("b_t_an"), 0),
                 _n(c.get("ecart_t_an"), 0), _pct(c.get("ecart_pct"))))
        if ec.get("ecart_delai_mois") is not None:
            a("**Délai :** %s mois d'écart sur la durée de projet.\n"
              % _n(ec.get("ecart_delai_mois"), 0))
        if ec.get("postes"):
            a("### Lots dont l'écart est justifié par un critère sourcé\n")
            a(_tab([pa + " / " + pb, "Lot", pa + " (M€)", pb + " (M€)", "Écart (M€)",
                    "Écart", "Pourquoi"],
                   [[("justifié" if x.get("justifie") else "report d'enveloppe"),
                     x.get("nom"), _f(x.get("a_meur"), 1), _f(x.get("b_meur"), 1),
                     _n(x.get("ecart_meur"), 1), _pct(x.get("ecart_pct")), x.get("raison")]
                    for x in ec["postes"]]))
        if ec.get("exploitation"):
            a("### Exploitation comparée\n")
            a(_tab(["Poste", pa + " (M€/an)", pb + " (M€/an)", "Écart (M€/an)", "Écart",
                    "Nature"],
                   [[x.get("nom"), _f(x.get("a_meur_an"), 2), _f(x.get("b_meur_an"), 2),
                     _n(x.get("ecart_meur_an"), 2), _pct(x.get("ecart_pct")), x.get("nature")]
                    for x in ec["exploitation"]]))
        aren_ec = ec.get("arenseigner") or []
        if aren_ec:
            a("### Lots dont l'écart n'est PAS interprétable\n")
            a("Ces lots contiennent un poste que le référentiel ne chiffre pas. L'écart "
              "affiché ne vient alors que du report de l'enveloppe globale : il ne dit "
              "rien du pays.\n")
            a(_tab(["Code", "Lot", "Écart (M€)", "Raison"],
                   [[x.get("code"), x.get("nom"), _n(x.get("ecart_meur"), 1), x.get("raison")]
                    for x in aren_ec]))
        if ec.get("note"):
            a("*" + _esc(ec["note"]) + "*\n")

    d0 = (j.get("dossiers") or [{}])[0]
    trace = ((d0.get("devis") or {}).get("trace")) or []
    if trace:
        a("## Trace du calcul\n")
        for t in trace:
            a("- " + _esc(t) + "\n")
    if j.get("avertissement"):
        a("\n*" + _esc(j["avertissement"]) + "*\n")
    return "\n".join(L)


# ═══════════════════════════════════════════════════════════════════════════
# 2. PROSPECTIVES
# ═══════════════════════════════════════════════════════════════════════════

def md_prospectives():
    t = tendances_dc.assemble()
    L = []
    a = L.append
    a("# Prospectives 2026-2030 — ce qui change, et ce que cela périme\n")
    a("Le référentiel d'implantation est un **état des lieux** : il dit où sont les "
      "sites et ce que coûte l'électricité. Une décision d'investissement se prend sur "
      "cinq à dix ans, horizon sur lequel le gel de Francfort jusqu'en 2031 ou la fin "
      "de l'accise finlandaise en mars 2025 pèsent plus lourd que l'écart de notation "
      "entre deux pays voisins.\n")
    a("Chaque entrée porte sa **page** et, quand une phrase se cite seule, sa "
      "**citation verbatim**. Les entrées marquées *prévision* engagent leur auteur, "
      "pas la réalité.\n")

    def src(cle, page):
        S = (t["sources"] or {}).get(cle) or {}
        return "%s, *%s*%s (%s)" % (S.get("editeur", cle), S.get("titre", ""),
                                    ", p. %s" % page if page else "", S.get("date", ""))

    def cit(x):
        if x.get("citation"):
            return "  \n  > « %s »" % _esc(x["citation"])
        return ("  \n  *Reformulé depuis le corps du rapport — aucune phrase citable "
                "isolément ; la page est donnée pour vérification.*")

    def amont(x):
        return (" — d'après %s" % _esc(x["source_amont"])) if x.get("source_amont") else ""

    a("## Réserves sur le référentiel — %d valeurs qu'un fait postérieur rend "
      "optimistes ou incomplètes\n" % len(t["reserves"]))
    a("Aucune de ces réserves n'est appliquée d'office aux notes et aux classes du "
      "référentiel. Un référentiel qui se réécrit sans le dire fait perdre la trace de "
      "ce qui a été cité la semaine précédente : la correction vous est remise, la "
      "décision vous appartient.\n")
    for r in t["reserves"]:
        jal = [z for z in t["jalons"] if z["cle"] == r["jalon"]]
        a("### %s — critère « %s », depuis %s\n" % (r["pays"], r["critere"], r["depuis"]))
        a("**Valeur affichée dans le référentiel :** %s\n" % _esc(r["valeur_referentiel"]))
        a(_esc(r["reserve"]) + "\n")
        if jal:
            a("*Fait déclencheur : %s — %s.*\n"
              % (_esc(jal[0]["titre"]), src(jal[0]["source"], jal[0].get("page"))))

    a("## Jalons réglementaires datés — %d échéances qui structurent un calendrier\n"
      % len(t["jalons"]))
    a(_tab(["Date", "Statut", "Pays", "Jalon", "Ce que cela impose", "Source"],
           [[j["date"], j["statut"], j["pays"], j["titre"], j["impact"],
             src(j["source"], j.get("page"))]
            for j in sorted(t["jalons"], key=lambda z: str(z["date"]))]))
    for j in sorted(t["jalons"], key=lambda z: str(z["date"])):
        a("- **%s — %s (%s)** — %s%s%s\n"
          % (_esc(j["date"]), _esc(j["titre"]), _esc(j["pays"]), _esc(j["detail"]),
             cit(j), amont(j)))

    a("## Les %d tendances 2026, et le critère du comparateur que chacune touche\n"
      % len(t["tendances"]))
    for x in t["tendances"]:
        a("### %d. %s\n" % (x["n"], x["titre"]))
        a(_esc(x["resume"]) + "\n")
        if x.get("chiffre"):
            a("**Chiffre :** %s\n" % _esc(x["chiffre"]))
        a("**Ce que cela change pour vous —** %s\n" % _esc(x["incidence"]))
        a("*Critère du comparateur touché : %s.*%s%s\n"
          % ("« %s »" % x["critere"] if x.get("critere")
             else "aucun — le référentiel ne capte pas tout, et il vaut mieux l'écrire",
             cit(x), amont(x)))
        a("*Source : %s.*\n" % src(x["source"], x.get("page")))

    a("## Structure de marché — ce qui contraint l'exécution, pas la localisation\n")
    a(_tab(["Fait", "Valeur", "Nature", "Date", "Source"],
           [[m["titre"], m["valeur"], m["nature"], m["date"],
             src(m["source"], m.get("page")) + amont(m)] for m in t["marche"]]))
    for m in t["marche"]:
        a("- **%s** — %s%s\n" % (_esc(m["titre"]), _esc(m["sens"]), cit(m)))

    a("## Les %d rapports dépouillés\n" % len(t["sources"]))
    a(_tab(["Rapport", "Éditeur", "Date", "Portée"],
           [[S["titre"], S["editeur"], S["date"], S["portee"]]
            for S in t["sources"].values()]))
    a("\n*" + _esc(t["avertissement"]) + "*\n")
    return "\n".join(L)


# ═══════════════════════════════════════════════════════════════════════════
# 3. RÉFÉRENTIEL D'IMPLANTATION
# ═══════════════════════════════════════════════════════════════════════════

def md_implantation(imp=None):
    imp = imp or implantation.assemble(sites=datacentres.assemble().get("sites"),
                                       intensites=empreinte_sites.INTENSITE)
    L = []
    a = L.append
    a("# Référentiel de choix d'implantation — %d pays\n" % len(imp.get("pays") or []))
    a("![Classement des pays selon les poids réglés à l'écran — carte du "
      "comparateur](fig:carte-implantation)\n")
    a(_esc(imp.get("avertissement")) + "\n")

    a("## Les critères et leur source\n")
    a(_tab(["Critère", "Ce qu'il mesure", "Source"],
           [[c.get("nom") or k, c.get("quoi") or c.get("mesure") or "",
             c.get("source") or ""] for k, c in (imp.get("criteres") or {}).items()]
           if isinstance(imp.get("criteres"), dict) else
           [[c.get("cle"), c.get("nom"), c.get("source")] for c in (imp.get("criteres") or [])]))
    a("## Les sources mobilisées\n")
    for k, s in (imp.get("sources") or {}).items():
        if isinstance(s, dict):
            a("- **%s** — %s (%s)%s\n"
              % (_esc(s.get("titre") or k), _esc(s.get("editeur") or ""),
                 _esc(s.get("nature") or ""),
                 (" — " + _esc(s["note"])) if s.get("note") else ""))

    a("## Comparatif par pays\n")
    a(_tab(["Pays", "Intensité (gCO₂/kWh)", "Stress hydrique", "Climat",
            "Prix (€/MWh)", "En service", "Pipeline 2030"],
           [[p["pays"], _n(p.get("intensite"), 0),
             (p.get("eau") or {}).get("classe_nom") or (p.get("eau") or {}).get("classe"),
             (p.get("climat") or {}).get("classe"),
             _f((p.get("prix") or {}).get("fourchette_eur_mwh"), 0),
             str(p.get("en_service")), str(p.get("pipeline_2030"))]
            for p in (imp.get("pays") or [])]))

    a("## Fiche par pays\n")
    for p in (imp.get("pays") or []):
        a("### %s\n" % p["pays"])
        notes = p.get("notes") or {}
        a(_tab(["Note", "Valeur sur 100"],
               [[k, str(v)] for k, v in notes.items()]))
        mix = p.get("mix") or {}
        a("**Mix de production :** nucléaire %s %%, renouvelables %s %%, fossile %s %%. "
          "**Eau :** %s (irrigation %s ; %s).\n"
          % (mix.get("nucleaire"), mix.get("renouvelables"), mix.get("fossile"),
             (p.get("eau") or {}).get("classe_nom"), (p.get("eau") or {}).get("irrigation"),
             (p.get("eau") or {}).get("bassins")))
        avis = p.get("avis") or {}
        for x in (avis.get("pour") or []):
            a("- **Pour —** %s\n" % _esc(x))
        for x in (avis.get("contre") or []):
            a("- **Contre —** %s\n" % _esc(x))
        if avis.get("comm"):
            a("*%s*\n" % _esc(avis["comm"]))
        for pr in (p.get("perspectives") or []):
            a("- *%s* (%s, %s) — %s\n" % (pr.get("sens"), _esc(pr.get("source")),
                                          pr.get("date"), _esc(pr.get("resume"))))
        pro = tendances_dc.par_pays(p["pays"])
        for r in (pro.get("reserves") or []):
            a("> **Réserve — critère « %s », depuis %s.** Valeur affichée : %s. %s\n"
              % (r["critere"], r["depuis"], _esc(r["valeur_referentiel"]), _esc(r["reserve"])))

    ue = imp.get("perspectives_ue") or []
    if ue:
        a("## Perspectives à l'échelle de l'Union\n")
        a(_tab(["Sens", "Date", "Perspective", "Source"],
               [[x.get("sens"), x.get("date"), x.get("resume"), x.get("source")] for x in ue]))
    return "\n".join(L)


# ═══════════════════════════════════════════════════════════════════════════
# 4. PARC ET EMPREINTE
# ═══════════════════════════════════════════════════════════════════════════

def md_parc(dc=None, emp=None):
    dc = dc or datacentres.assemble()
    L = []
    a = L.append
    a("# Parc de centres de données européens et empreinte du parc\n")
    # La carte se pose ICI, avant les chiffres qu'elle illustre. Placée après,
    # elle serait une décoration ; placée avant, elle est ce que le lecteur
    # regarde en ouvrant le chapitre.
    a("![Carte des centres de données et des systèmes d'IA déployés dans "
      "l'Union](fig:carte-parc)\n")
    a("Référentiel figé par version (%s), compilé puis réfuté site par site. "
      "**%d centres** recensés.\n" % (dc.get("version"), dc.get("n_sites") or 0))
    for lim in (dc.get("limites") or []):
        a("- **Limite —** %s\n" % _esc(lim if isinstance(lim, str) else lim.get("quoi") or lim))

    ag = dc.get("agregats") or {}
    if ag.get("par_statut"):
        a("## Répartition par statut\n")
        a(_tab(["Statut", "Nombre"], [[k, str(v)] for k, v in ag["par_statut"].items()]))
    if ag.get("par_pays"):
        a("## Répartition par pays\n")
        a(_tab(["Pays", "Sites", "Capacité publiée (MW)", "Montant publié (M€)"],
               [[x.get("pays"), str(x.get("n")), _n(x.get("mw"), 0), _n(x.get("meur"), 0)]
                for x in ag["par_pays"]]))
        a("*Les colonnes de capacité et de montant sont massivement à zéro, et c'est "
          "l'information : les exploitants ne publient presque jamais ces valeurs. "
          "Aucun coût au mégawatt n'en est dérivable.*\n")

    a("## Inventaire des sites\n")
    a(_tab(["Opérateur", "Site", "Ville", "Pays", "Statut", "Gabarit",
            "Refroidissement", "Confiance", "Source"],
           [[s.get("operateur"), s.get("nom_site"), s.get("ville"), s.get("pays"),
             s.get("statut"), s.get("gabarit"), s.get("refroidissement"),
             s.get("confiance"), s.get("source_libelle")]
            for s in (dc.get("sites") or [])]))

    if emp is None:
        try:
            import panorama_ia
            emp = empreinte_sites.assemble(sites=dc.get("sites"),
                                           cas=panorama_ia.assemble().get("cas"))
        except Exception:  # noqa: BLE001
            emp = None
    if emp:
        a("## Empreinte du parc cartographié\n")
        a(_esc(emp.get("avertissement")) + "\n")
        tot = emp.get("totaux") or {}
        a(_tab(["Grandeur", "Valeur"],
               [[k, _f(v, 1) if isinstance(v, (list, tuple)) else _n(v, 1)]
                for k, v in tot.items()]))
        for lim in (emp.get("limites") or []):
            a("- **Limite —** %s\n" % _esc(lim if isinstance(lim, str)
                                           else lim.get("quoi") or lim))
        if emp.get("par_pays"):
            a("### Par pays\n")
            cles = [k for k in (emp["par_pays"][0] or {}).keys()]
            a(_tab([str(k) for k in cles],
                   [[_f(x.get(k), 1) if isinstance(x.get(k), (list, tuple)) else x.get(k)
                     for k in cles] for x in emp["par_pays"]]))
    return "\n".join(L)


# ═══════════════════════════════════════════════════════════════════════════
# Assemblage et sortie
# ═══════════════════════════════════════════════════════════════════════════

def _entete(dossier, devis_reponse=None):
    """Le bloc de garde. Il porte les VERSIONS : un dossier sans le millésime de
    ses référentiels ne peut pas être rejoué, donc pas contesté."""
    vers = ["parc %s" % datacentres.assemble().get("version"),
            "implantation %s" % implantation.VERSION,
            "prospectives %s" % tendances_dc.VERSION]
    if DOSSIERS[dossier]["besoin_devis"]:
        vers.insert(0, "enveloppe %s" % finance_dc.VERSION)
    return {
        "label": DOSSIERS[dossier]["nom"],
        "perimetre": DOSSIERS[dossier]["resume"],
        "date": _horodatage(),
        "referentiel": " · ".join(vers),
        "client": ((devis_reponse or {}).get("entree") or {}).get("client") or None,
    }


# Les sections dont l'ABSENCE ne se verrait pas.
#
# Ce garde-fou existe parce que le défaut est arrivé : la clé du bloc « ce que
# nous ne pouvons pas trancher » s'appelle `arenseigner` et non `a_renseigner`.
# Un `.get()` avec valeur par défaut a donc renvoyé une liste vide, et la
# section entière — celle qui porte l'honnêteté du document — a disparu sans
# laisser de trace. Le document restait beau, complet en apparence, et taisait
# exactement ce qu'il devait dire.
#
# Un export ne doit jamais échouer en silence sur ce point : mieux vaut refuser
# de produire le fichier que d'en livrer un qui a perdu ses réserves.
# ═══════════════════════════════════════════════════════════════════════════
# Le dossier d'ingénierie financière — quatre moteurs, versés tels que servis
# ═══════════════════════════════════════════════════════════════════════════

def _abs(titre, geste):
    """Un bloc jamais lancé s'écrit, il ne disparaît pas : un dossier qui
    tait un bloc absent laisse croire à une étude complète."""
    return ("## %s\n*Ce bloc n'a pas été lancé sur la page : rien n'est versé "
            "ici, plutôt qu'un chiffre inventé. %s*\n" % (titre, geste))


def _paire(v, d=1, unite=""):
    """Une fourchette [bas, haut] du moteur, ou une valeur seule."""
    if isinstance(v, (list, tuple)) and len(v) == 2:
        a, b = v
        if a is None or b is None:
            return "non instruit"
        return "%s à %s%s" % (_n(a, d), _n(b, d), (" " + unite if unite else ""))
    if v is None:
        return "non instruit"
    return _n(v, d) + ((" " + unite) if unite else "")


def md_ingenierie(complements):
    """`complements` porte les dernières réponses des moteurs, telles que la
    page les a reçues : equipements, kpi, maturite, pilotage. Rien n'est
    recalculé ici — le document et l'écran montrent la même chose."""
    c = complements or {}
    L = []
    a = L.append

    a("# Ingénierie financière — équipements, valeur, maturité, pilotage\n")
    a("Ce dossier verse les résultats des quatre moteurs de la page, tels que "
      "servis au moment de l'export. Chaque bloc porte ses incertitudes et ses "
      "refus ; **un bloc jamais lancé est écrit comme tel** — le document ne "
      "complète pas ce que la page n'a pas calculé.\n")

    # ── Équipements informatiques ────────────────────────────────────────
    eq = c.get("equipements") or {}
    n = eq.get("nomenclature") or {}
    if not n or not n.get("ok"):
        a(_abs("Équipements informatiques",
               "Lancez le calcul d'équipements sur la page d'enveloppe."))
    else:
        a("## Équipements informatiques — la nomenclature\n")
        a("Puissance informatique %s kW, densité « %s » (%s), %s baie(s) à "
          "%s kW.\n" % (_n(n.get("puissance_it_kw"), 0), n.get("densite_nom"),
                        n.get("densite_note"), _n(n.get("baies"), 0),
                        _n(n.get("kw_par_baie"), 1)))
        a(_tab(["Poste", "Quantité", "Unité", "Prix total (€)",
                "Carbone total (kg)", "Annualisé (kg/an)"],
               [[l.get("nom"), _n(l.get("quantite"), 0), l.get("unite"),
                 _n(l.get("prix_total_eur"), 0), _n(l.get("carbone_total_kg"), 0),
                 _n(l.get("carbone_annualise_kg"), 1)]
                for l in (n.get("lignes") or [])]))
        a("Total **%s €** (indispensable %s €, utile %s €), soit %s €/kW "
          "informatique. Carbone incorporé **%s t**, annualisé **%s t/an** sur "
          "la durée de vie de chaque poste. Incertitudes : ±%s %% sur les "
          "prix, ±%s %% sur le carbone.\n"
          % (_n(n.get("total_eur"), 0), _n(n.get("total_indispensable_eur"), 0),
             _n(n.get("total_utile_eur"), 0), _n(n.get("eur_par_kw_it"), 0),
             _n(n.get("carbone_total_t"), 1), _n(n.get("carbone_annualise_t"), 1),
             _n(n.get("incertitude_prix_pct"), 0),
             _n(n.get("incertitude_carbone_pct"), 0)))
        a("Sources : %s Carbone : %s\n" % (n.get("prix_source", ""),
                                           n.get("carbone_source", "")))
        p = eq.get("part") or {}
        if p.get("ok"):
            a("### Le poste que l'enveloppe travaux ne contient pas\n")
            a((p.get("lecture") or "") + "\n")
        pr = eq.get("prolongation") or {}
        if pr.get("ok"):
            a("### Allonger la durée de vie — le bilan carbone\n")
            a("De %s à %s an(s), pays %s : gain de fabrication %s kg/an, coût "
              "d'exploitation %s kg/an, **net %s t/an** — verdict : %s.\n"
              % (_n(pr.get("duree_base"), 0), _n(pr.get("duree_cible"), 0),
                 pr.get("pays"), _n(pr.get("gain_fabrication_kg_an"), 0),
                 _n(pr.get("cout_exploitation_kg_an"), 0),
                 _n(pr.get("net_t_an"), 2), pr.get("verdict", "")))
            a((pr.get("lecture") or "") + "\n")
            a("*Réserve du moteur : " + (pr.get("reserve") or "") + "*\n")
        s3 = eq.get("scope3") or {}
        if s3.get("ok"):
            a("### Ce que ces équipements pèsent au GHG Protocol (scope 3)\n")
            a("Catégorie 1 (biens achetés) **%s t**, catégorie 2 "
              "(immobilisations) **%s t**, total **%s t**, annualisé %s t/an "
              "(±%s %%).\n" % (_n(s3.get("categorie_1_t"), 1),
                               _n(s3.get("categorie_2_t"), 1),
                               _n(s3.get("total_t"), 1),
                               _n(s3.get("annualise_t"), 1),
                               _n(s3.get("incertitude_pct"), 0)))
            nc = s3.get("non_couvert") or []
            if nc:
                a("Ce que ce chiffre NE couvre PAS :\n")
                for x in nc:
                    a("- " + x + "\n")

    # ── Création de valeur ───────────────────────────────────────────────
    k = c.get("kpi") or {}
    serie = k.get("serie") or {}
    lect = k.get("lecture") or {}
    if not k or not k.get("ok"):
        a(_abs("Création de valeur — EVA, ROCE, flux disponibles",
               "Calculez d'abord l'enveloppe, puis lancez la lecture des "
               "indicateurs."))
    elif not serie.get("instruit"):
        a("## Création de valeur — EVA, ROCE, flux disponibles\n")
        # `manquantes` est une liste d'OBJETS — cle, nom, question, pourquoi.
        # On verse le nom ET la question : c'est elle qui dit au lecteur quoi
        # aller chercher, pas l'identifiant technique.
        a("**Le moteur refuse de produire la série** : hypothèses manquantes."
          + " " + (serie.get("message") or "") + "\n")
        for mq in (serie.get("manquantes") or []):
            if isinstance(mq, dict):
                a("- **%s** — %s\n" % (mq.get("nom", mq.get("cle", "?")),
                                       mq.get("question", "")))
            else:
                a("- " + str(mq) + "\n")
    else:
        a("## Création de valeur — EVA, ROCE, flux disponibles\n")
        a((serie.get("avertissement") or "") + "\n")
        a(_tab(["Année", "Charge", "Revenu (M€)", "Capitaux employés (M€)",
                "EBIT (M€)", "EVA (M€)", "ROCE (%)", "FCF (M€)"],
               [[str(l.get("annee")), _n(l.get("charge"), 2),
                 _n(l.get("revenu_meur"), 1),
                 _paire(l.get("capitaux_employes_meur")),
                 _paire(l.get("ebit_meur")), _paire(l.get("eva_meur")),
                 _paire(l.get("roce_pct")), _paire(l.get("fcf_meur"))]
                for l in (serie.get("annees") or [])]))
        a("*" + (serie.get("trace") or "") + "*\n")
        for ind in (lect.get("indicateurs") or []):
            a("### %s (%s)\n" % (ind.get("nom"), ind.get("unite", "")))
            a("%s — année de régime : %s. %s\n"
              % (ind.get("formule", ""), ind.get("annee_regime", "?"),
                 ind.get("dit") or ""))
            if ind.get("piege"):
                a("*Le piège : " + ind["piege"] + "*\n")
        for r in (lect.get("reserves") or []):
            a("- *Réserve : " + str(r) + "*\n")
        if lect.get("synthese"):
            a("**Synthèse du moteur : " + lect["synthese"] + "**\n")
    sr = k.get("seuil_revenu") or {}
    if sr.get("instruit"):
        a("### Le revenu qui ne détruit pas de valeur\n")
        a((sr.get("dit") or "") + "\n")

    # ── Maturité ─────────────────────────────────────────────────────────
    m = c.get("maturite") or {}
    if not m or not m.get("ok"):
        a(_abs("Maturité analytique de l'organisation",
               "Répondez au diagnostic de maturité sur la page."))
    else:
        a("## Maturité analytique de l'organisation\n")
        a("Niveau global : **%s — %s**. %s\n"
          % (m.get("niveau_global", "?"), m.get("niveau_global_nom", ""),
             m.get("lecture") or ""))
        for ax in (m.get("axes") or []):
            a("- **%s** : niveau %s — %s\n"
              % (ax.get("nom", ax.get("cle", "?")), ax.get("niveau", "?"),
                 ax.get("lecture") or ax.get("dit") or ""))
        if m.get("reserve"):
            a("*" + str(m["reserve"]) + "*\n")

    # ── Pilotage ─────────────────────────────────────────────────────────
    p = c.get("pilotage") or {}
    if not p or not p.get("ok"):
        a(_abs("Pilotage, seuils et alertes",
               "Renseignez les mesures du tableau de pilotage sur la page."))
    else:
        a("## Pilotage, seuils et alertes\n")
        a((p.get("lecture") or "") + "\n")
        a(_tab(["Indicateur", "Valeur", "Cible", "Seuil", "État", "Tendance"],
               [[i.get("nom"), _paire(i.get("valeur")),
                 _paire(i.get("cible")), _paire(i.get("seuil")),
                 str((i.get("risque") or {}).get("etat")
                     if isinstance(i.get("risque"), dict) else i.get("risque") or "—"),
                 str((i.get("tendance") or {}).get("dit")
                     if isinstance(i.get("tendance"), dict) else i.get("tendance") or "—")]
                for i in (p.get("indicateurs") or [])]))
        for al in (p.get("alertes") or []):
            a("- **Alerte** : %s\n" % (al.get("dit") if isinstance(al, dict) else al))
        if p.get("reserve"):
            a("*" + str(p["reserve"]) + "*\n")

    a("## Ce que ce dossier ne dit pas\n")
    a("Les quatre blocs sont des **instruments d'avant-projet** : chaque "
      "moteur écrit ses incertitudes et ses refus, et ce dossier les "
      "reproduit. Aucun de ces chiffres ne remplace un devis, un plan "
      "d'affaires audité ni un bilan carbone opposable.\n")
    return "".join(L)


ATTENDU = {
    "enveloppe": ["Ce que ce dossier ne peut PAS trancher",
                  "Décomposition par lot (DPGF)",
                  "Coût total de possession",
                  "Échéancier jusqu'en 2030",
                  "Carbone incorporé de la construction",
                  "Repères de marché"],
    "prospectives": ["Réserves sur le référentiel",
                     "Jalons réglementaires datés",
                     "tendances 2026",
                     "rapports dépouillés"],
    "implantation": ["Comparatif par pays", "Fiche par pays", "sources mobilisées"],
    "parc": ["Inventaire des sites", "Répartition par pays"],
}
ATTENDU["complet"] = (ATTENDU["enveloppe"] + ATTENDU["implantation"]
                      + ATTENDU["prospectives"] + ATTENDU["parc"])
# Le dossier d'ingénierie n'exige que sa section d'honnêteté : chaque bloc de
# moteur peut légitimement être absent — mais alors il est ÉCRIT absent, et la
# section finale, elle, ne peut jamais manquer.
ATTENDU["ingenierie"] = ["Ce que ce dossier ne dit pas"]


def _verifier(md, dossier):
    # Le lecteur Markdown de l'export reconnaît *italique*, pas _italique_ : un
    # tiret bas s'imprime tel quel, en plein milieu d'une phrase. Et un
    # astérisque orphelin sur une ligne fait la même chose. Le contrôle est ici
    # parce que le défaut est invisible au relecteur du code et bien visible
    # sur la page imprimée, chez le client.
    import re as _re
    if _re.search(r"(?:^|\s)_[^\s_]|[^\s_]_(?:\s|$)", md, _re.M):
        raise RuntimeError("dossier « %s » : italique en tiret bas — il s'imprimerait "
                           "littéralement. Utiliser *…*." % dossier)
    impaires = [l for l in md.split("\n") if l.count("*") % 2]
    if impaires:
        raise RuntimeError("dossier « %s » : astérisque orphelin sur « %s… » — il "
                           "s'imprimerait." % (dossier, impaires[0][:60]))
    manquantes = [t for t in ATTENDU.get(dossier, []) if t not in md]
    if manquantes:
        raise RuntimeError(
            "dossier « %s » incomplet — sections absentes : %s. Une clé du moteur de "
            "calcul a probablement changé de nom ; le document n'est pas produit."
            % (dossier, ", ".join(manquantes)))
    return md


def composer(dossier, devis_reponse=None, complements=None):
    """Le Markdown du dossier demandé. Un seul point d'entrée : le Word et le PDF
    partent du même texte, ils ne peuvent donc pas diverger."""
    if dossier not in DOSSIERS:
        raise ValueError("dossier inconnu : %s" % dossier)
    if DOSSIERS[dossier]["besoin_devis"] and not devis_reponse:
        raise ValueError("ce dossier exige un calcul d'enveloppe préalable")
    if dossier == "enveloppe":
        md = md_enveloppe(devis_reponse)
    elif dossier == "prospectives":
        md = md_prospectives()
    elif dossier == "implantation":
        md = md_implantation()
    elif dossier == "parc":
        md = md_parc()
    elif dossier == "ingenierie":
        md = md_ingenierie(complements)
    else:
        md = "\n\n".join([md_enveloppe(devis_reponse), md_implantation(),
                          md_prospectives(), md_parc()])
    return _verifier(md, dossier)


def produire(dossier, fmt, devis_reponse=None, figures=None, complements=None):
    """Renvoie (octets, type MIME, nom de fichier).

    `figures` : les cartes de la page, en PNG base64, sous les clés de FIGURES.
    Absentes, le document se compose quand même — et ÉCRIT quelle carte
    manque, plutôt que de faire disparaître la ligne."""
    import livrables_export
    if fmt not in FORMATS:
        raise ValueError("format inconnu : %s" % fmt)
    md = composer(dossier, devis_reponse, complements)
    meta = dict(MARQUE)
    meta.update(_entete(dossier, devis_reponse))
    meta["figures"] = figures or {}
    jour = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    nom = "CONSEILPREV-%s-%s.%s" % (dossier, jour, fmt)
    if fmt == "docx":
        return (livrables_export.build_docx(md, meta),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                nom)
    return livrables_export.build_pdf(md, meta), "application/pdf", nom


def catalogue():
    return {"version": VERSION, "formats": list(FORMATS),
            "figures": [{"cle": k, "legende": v} for k, v in FIGURES],
            "dossiers": [dict(cle=k, **v) for k, v in DOSSIERS.items()]}


def sante():
    return {"module": "export_dc", "version": VERSION,
            "dossiers": len(DOSSIERS), "formats": list(FORMATS),
            "figures": len(FIGURES),
            "horodatage": datetime.now(timezone.utc).isoformat(timespec="seconds")}
