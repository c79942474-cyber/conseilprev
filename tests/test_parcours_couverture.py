# -*- coding: utf-8 -*-
"""La substance de Sentinel est ATTEINTE par au moins un parcours guidé.

CE QUE LES RÈGLES EXISTANTES MESURAIENT, ET CE QU'ELLES NE VOYAIENT PAS.
`test_parcours_par_role.py` garde déjà l'essentiel : que les parcours par rôle
existent, que chaque étape mène à un panneau QUI EXISTE, que chacune dise quoi
faire et ce qu'elle apporte, que le catalogue et les familles ne divergent pas.
Toutes mesurent la VALIDITÉ de ce qui est écrit. Aucune ne mesurait la
COUVERTURE de ce qui ne l'est pas.

LE RELEVÉ DU 4 SEPTEMBRE 2026 : dix-neuf parcours, cent douze étapes, aucune
cassée — et DIX-NEUF panneaux sur quatre-vingts qu'aucun parcours n'atteignait,
hors les vingt-quatre fiches pays qui se lisent depuis la carte. Parmi eux, le
FinOps de l'IA et l'enveloppe d'investissement, construits quelques semaines
plus tôt ; le tableau d'adoption, qui dit précisément ce que l'indice de
conformité ne dit pas ; le cadre normatif ; la vue d'ensemble IA Act, qui est
le point d'entrée du dispositif. Rien ne plantait ; ces modules n'étaient
atteignables qu'en les cherchant dans une barre latérale de quatre-vingts
entrées.

LA RÈGLE ÉNUMÈRE, ELLE NE NOMME PAS ce qu'il faut couvrir : elle relève les
panneaux de la page, en retire ceux qui sont explicitement déclarés HORS
PARCOURS avec leur raison, et exige que tout le reste soit atteint. Un panneau
ajouté demain tombe dans le filet le jour même.
"""
import io
import os
import re

import pytest

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGE = io.open(os.path.join(RACINE, "sentinel.html"), encoding="utf-8").read()
SRC = io.open(os.path.join(RACINE, "sentinel.page.js"), encoding="utf-8").read()

PANNEAUX = set(re.findall(r'id="p-([a-z0-9-]+)"', PAGE))


def _catalogue():
    """Les parcours, lus dans le VRAI fichier — jamais recopiés ici."""
    deb = SRC.index("var GUIDED_PATHS = [")
    fin = SRC.index("\n];", deb)
    bloc = SRC[deb:fin]
    morceaux = re.split(r"\n  \{\n?\s*id:\s*'", bloc)
    return [(m.split("'")[0], re.findall(r"\{id:'([^']+)'", m))
            for m in morceaux[1:]]


CATALOGUE = _catalogue()
VISITES = set(e for _, etapes in CATALOGUE for e in etapes)


# ══════════════════════════════════════════════════════════════════════════
# Ce qui n'a pas à être dans un parcours — et pourquoi, panneau par panneau
# ══════════════════════════════════════════════════════════════════════════
# Chaque exemption porte sa raison, et la raison est lisible. Un panneau qu'on
# voudrait exempter sans savoir dire pourquoi est un panneau qui devrait être
# dans un parcours.
HORS_PARCOURS = {
    "clients": "Gestion du portefeuille client : c'est l'outil de CONSEILPREV "
               "sur ses propres clients, pas une étape du travail de "
               "conformité d'un abonné.",
    "compte": "Connexion et session : un écran de service, sans contenu "
              "qu'un chemin de lecture aurait à traverser.",
    "espace": "« Mes actions du jour » est un point de reprise personnel — il "
              "s'ouvre en arrivant, il ne se traverse pas dans un ordre.",
    "entreprise": "Offre Entreprise : page commerciale. La faire figurer dans "
                  "un parcours mêlerait la vente à la méthode.",
    "pricing": "Tarification par résultats : page commerciale, pour la même "
               "raison que l'offre Entreprise — un parcours de méthode qui "
               "conduirait au tarif serait un argumentaire déguisé.",
    "rgpd-site": "Le RGPD de CONSEILPREV lui-même — une page de transparence "
                 "sur nos propres traitements, pas un outil de l'abonné.",
}

# LES FICHES PAYS NE SONT PAS DES ÉTAPES, et c'est une décision, pas un oubli.
# Elles se lisent DEPUIS la carte, une fois qu'on a repéré le pays qui
# intéresse : les enfiler dans un parcours obligerait à traverser vingt-trois
# pays sans rapport pour atteindre le vingt-quatrième.
def _de_fond(pid):
    return not pid.startswith("fiche-") and pid not in HORS_PARCOURS


PANNEAUX_DE_FOND = sorted(p for p in PANNEAUX if _de_fond(p))


def test_le_releve_lit_bien_la_page_et_le_catalogue():
    """Garde-fou : une lecture cassée rendrait toutes les règles suivantes
    vertes en ne mesurant rien — le défaut que ces dépôts ont déjà commis."""
    assert len(PANNEAUX) >= 70, "panneaux relevés : %d" % len(PANNEAUX)
    assert len(CATALOGUE) >= 19, "catalogue : %d parcours" % len(CATALOGUE)
    assert len(VISITES) >= 45, "panneaux visités : %d" % len(VISITES)


def test_tout_panneau_de_fond_est_atteint_par_au_moins_un_parcours():
    """Le cœur de cette règle. Un panneau qu'aucun parcours n'atteint n'est
    trouvable qu'en le cherchant dans une barre latérale de quatre-vingts
    entrées — et on ne cherche que ce dont on sait déjà l'existence."""
    orphelins = sorted(p for p in PANNEAUX_DE_FOND if p not in VISITES)
    assert not orphelins, (
        "ces panneaux ne sont atteints par AUCUN parcours : %s. Soit ils ont "
        "leur place dans un parcours — c'est le cas le plus fréquent —, soit "
        "ils rejoignent HORS_PARCOURS avec la raison qui les en dispense."
        % ", ".join(orphelins))


def test_les_exemptions_designent_des_panneaux_qui_existent():
    """Une exemption qui ne désigne plus rien a survécu à son panneau : elle
    ne protège plus rien et fausse le compte."""
    fantomes = sorted(p for p in HORS_PARCOURS if p not in PANNEAUX)
    assert not fantomes, (
        "HORS_PARCOURS dispense des panneaux qui n'existent plus : %s"
        % ", ".join(fantomes))


def test_aucune_exemption_ne_dispense_un_panneau_deja_couvert():
    """Un panneau à la fois exempté ET visité signale une décision qui a
    changé sans que l'exemption suive."""
    doublons = sorted(p for p in HORS_PARCOURS if p in VISITES)
    assert not doublons, (
        "ces panneaux sont dispensés de parcours et pourtant visités : %s — "
        "retirer l'exemption devenue fausse." % ", ".join(doublons))


def test_chaque_exemption_porte_une_raison_lisible():
    """Une exemption sans motif ne pourra pas être contestée dans six mois :
    elle deviendra un fait acquis."""
    courtes = sorted(p for p, r in HORS_PARCOURS.items() if len(r) < 60)
    assert not courtes, (
        "ces exemptions n'expliquent pas ce qu'elles dispensent : %s"
        % ", ".join(courtes))


# ══════════════════════════════════════════════════════════════════════════
# Un parcours est un chemin, pas un lien
# ══════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("pid", [p for p, _ in CATALOGUE])
def test_un_parcours_compte_au_moins_quatre_etapes(pid):
    """Trois étapes, ce sont deux modules et une conclusion : l'ordre de
    lecture n'a alors rien à apprendre à personne."""
    etapes = dict(CATALOGUE)[pid]
    assert len(etapes) >= 4, (
        "le parcours %s ne compte que %d étape(s) : ce n'est pas un chemin de "
        "lecture, c'est un lien." % (pid, len(etapes)))


@pytest.mark.parametrize("pid", [p for p, _ in CATALOGUE])
def test_toute_etape_mene_a_un_panneau_qui_existe(pid):
    """Une étape dont l'identifiant ne correspond à rien n'affiche aucune
    erreur : elle ne va simplement nulle part. Cette règle double celle de
    test_parcours_par_role.py, qui passe par node ; celle-ci tient même
    lorsque node est absent de la machine."""
    inconnus = sorted(set(dict(CATALOGUE)[pid]) - PANNEAUX)
    assert not inconnus, (
        "le parcours %s vise des panneaux inexistants : %s" % (pid, inconnus))


# ══════════════════════════════════════════════════════════════════════════
# Les modules construits récemment ne restent pas hors des chemins
# ══════════════════════════════════════════════════════════════════════════
# CE QUE CETTE RÈGLE AJOUTE À LA PRÉCÉDENTE. La couverture générale se
# satisferait d'un panneau atteint par n'importe quel parcours. Ceux-ci ont été
# construits pour un métier précis, et les y rattacher est ce qui donne son
# sens au module : un FinOps qu'un CEO croise mais qu'aucun CDO ne rencontre
# n'a pas trouvé son lecteur.
ATTENDUS = {
    "finops": ["cdo", "caio"],
    "adoption": ["caio"],
    "cadre-normatif": ["grc_senior"],
    # LE HUB N'EST ATTENDU QUE CHEZ LE DÉPLOYEUR, et ce n'est pas un demi-
    # travail : une règle antérieure borne à TROIS les étapes communes aux deux
    # parcours par rôle, parce que « s'ils portaient les mêmes étapes, les
    # distinguer n'apprendrait rien ». Le mettre aussi chez le fournisseur en
    # aurait fait une quatrième. Chez le déployeur il vient en DEUXIÈME, après
    # la découverte du Shadow AI qu'une autre règle exige en tête.
    "ia-act-hub": ["role_deployeur"],
    "enveloppe": ["dc_implantation", "dc_financement"],
    "empreinte": ["dc_energie", "dc_reporting"],
    "empreinte-parc": ["dc_energie"],
    # LE PANNEAU LIT LE REGISTRE, DONC IL SUIT LE CDO qui le tient, et le
    # reporting extra-financier qui devra citer ses quatre indicateurs. Le
    # mettre ailleurs aurait fait un module que personne dont c'est le métier
    # ne rencontre.
    "empreinte-ia": ["cdo", "dc_reporting"],
    "evals": ["grc_senior"],
    "comp": ["dc_implantation"],
}


@pytest.mark.parametrize("panneau,parcours", sorted(ATTENDUS.items()))
def test_un_module_est_rattache_au_metier_pour_lequel_il_est_fait(panneau, parcours):
    par_id = dict(CATALOGUE)
    manquants = [p for p in parcours if panneau not in par_id.get(p, [])]
    assert not manquants, (
        "le panneau « %s » n'est plus atteint par %s. Soit l'étape a été "
        "retirée par mégarde, soit le rattachement a changé — et il se "
        "redéclare ici." % (panneau, ", ".join(manquants)))


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE_META ET LES PANNEAUX SERVIS — UNE BIJECTION, DANS LES DEUX SENS
# ═══════════════════════════════════════════════════════════════════════════
#
# CE QUE L'AUDIT DES TRENTE PARCOURS A TROUVÉ, ET QUE RIEN NE GARDAIT.
# `PAGE_META` est ce que `go()` lit pour écrire le fil d'Ariane et le titre du
# document. Elle déclarait quatre-vingt-six entrées pour quatre-vingt-six
# panneaux — et ce n'étaient pas les mêmes :
#
#   · `shadow-ai` et `compte` étaient SERVIS SANS ENTRÉE. Un parcours qui y
#     conduit — `role_deployeur` le fait — appelle `go(step.id)` sans section
#     ni page : le visiteur arrivait sur un panneau au fil d'Ariane vide, dans
#     un onglet nommé « Sentinel », au moment précis où un parcours venait de
#     l'y conduire.
#   · `alertes` et `chat` étaient DÉCLARÉS SANS PANNEAU. Le premier a coûté un
#     tour de travail : un parcours neuf l'a visé, et la seule chose qui l'a
#     dit est une règle de couverture — pas PAGE_META, qui affirmait le
#     contraire. Une table qui déclare des panneaux inexistants est pire
#     qu'une table incomplète : elle donne une garantie fausse.

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _bloc_page_meta():
    src = io.open(os.path.join(_RACINE, "sentinel.page.js"), encoding="utf-8").read()
    i = src.index("var PAGE_META = {")
    return src[i:src.index("\n};", i)]


def _page_meta():
    return set(re.findall(r"^\s*'?([a-z0-9-]+)'?\s*:\s*\{\s*section",
                          _bloc_page_meta(), re.M))


def _panneaux_servis():
    h = io.open(os.path.join(_RACINE, "sentinel.html"), encoding="utf-8").read()
    return set(re.findall(r'id="p-([a-z0-9-]+)"', h))


def test_la_lecture_de_PAGE_META_N_EST_PAS_VIDE():
    """LE GARDE-FOU DES TROIS RÈGLES SUIVANTES, et il n'est pas décoratif :
    ces trois règles ont été écrites une première fois SANS ÊTRE AJOUTÉES au
    fichier — une chaîne shell interrompue — et la recette est restée verte,
    parce qu'une règle absente ne tombe pas. Ici, une lecture qui rendrait un
    ensemble vide ferait passer les trois suivantes pour la même raison."""
    assert len(_page_meta()) > 60
    assert len(_panneaux_servis()) > 60


def test_tout_panneau_servi_a_son_entree_dans_PAGE_META():
    """Sans entrée, un panneau atteint par un parcours perd son fil d'Ariane
    et son titre d'onglet."""
    orphelins = sorted(_panneaux_servis() - _page_meta())
    assert not orphelins, (
        "panneaux servis sans entrée PAGE_META — ils arriveront sans fil "
        "d'Ariane ni titre : %s" % orphelins)


def test_toute_entree_de_PAGE_META_a_son_panneau():
    """L'AUTRE SENS, ET C'EST CELUI QUI A COÛTÉ. Une entrée sans panneau fait
    passer pour navigable une destination qui n'existe pas — et un parcours
    écrit de bonne foi s'y appuie."""
    fantomes = sorted(_page_meta() - _panneaux_servis())
    assert not fantomes, (
        "entrées PAGE_META sans panneau servi — elles déclarent navigable ce "
        "qui ne l'est pas : %s" % fantomes)


def test_aucun_libelle_de_PAGE_META_ne_fige_un_COMPTE():
    """« 7 alertes actives » était le libellé d'un menu. Il aurait menti dès la
    huitième alerte, et personne n'a de raison d'aller corriger un libellé de
    menu. Un compte se calcule ou ne s'affiche pas — il ne s'écrit pas en dur
    dans une table de navigation."""
    libelles = re.findall(r"label:\s*'([^']*\d[^']*)'", _bloc_page_meta())
    # UN CHIFFRE N'EST PAS TOUJOURS UN COMPTE : « IEC 62443 » ou « art. 14 »
    # en portent un sans rien dénombrer. Ce qu'on refuse est un NOMBRE SUIVI
    # D'UN NOM AU PLURIEL — la forme d'un inventaire.
    comptes = [x for x in libelles
               if re.search(r"\b\d+\s+[a-zA-Zéèêàâîôûç]+s\b", x)]
    assert not comptes, "libellés de menu qui figent un compte : %s" % comptes
