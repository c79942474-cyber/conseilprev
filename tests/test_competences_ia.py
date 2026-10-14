# -*- coding: utf-8 -*-
"""LE RÉFÉRENTIEL DE COMPÉTENCES IA — CE QUE LE MODULE DOIT TENIR.

CE QUI A ÉTÉ DEMANDÉ : un module dans la barre latérale de Sentinel, rattaché
au Hub Training, qui prenne en entrée QUATRE listes déroulantes — type de
personne, secteur d'activité, fonction métier, niveau de connaissances IA — et
rende en sortie la formation ou la sensibilisation appropriée à cette
personne, avec son niveau de maturité de départ et le niveau final ciblé.

CE QUE CES RÈGLES MESURENT, ET QUI NE SE DEVINE PAS À LA LECTURE :

  1. LA CIBLE EST UN MAXIMUM, PAS UNE SOMME. Trois entrées exigent chacune un
     niveau sur la même famille. Les additionner enverrait un collaborateur du
     marketing dans la santé au niveau 9 d'une échelle qui s'arrête à 5. La
     règle recalcule le maximum depuis les tables, pour les 1 320 triplets, et
     le compare à ce que le moteur rend.

  2. LE PLAFOND DE RÔLE. Les niveaux 4 et 5 de l'échelle décrivent un RÔLE —
     transmettre, concevoir. Un secteur sensible et une direction technique
     élèvent l'exigence portée sur une personne ; ils ne lui donnent pas ce
     rôle. Sans ce plafond, mesuré avant qu'il existe : un collaborateur du
     marketing dans la santé ressortait à « Piloter et transmettre », et un
     collaborateur des systèmes d'information à « Concevoir ou expertiser ».
     Les règles éprouvent les deux sens — le rabattement s'applique à la
     fonction et au secteur, il ne s'applique JAMAIS à la population, qui est
     ce qui porte le rôle.

  3. RIEN N'EST PROPOSÉ AU-DELÀ DE LA CIBLE, ET RIEN N'EST PERDU EN SILENCE.
     Une formation n'est retenue que si elle répond à un besoin sans dépasser
     la cible ; mais une fois retenue, ce qu'elle apporte est crédité jusqu'à
     la cible. Mesuré avant cette distinction : la famille « comprendre » d'un
     collaborateur restait en écart parce que la seule sensibilisation du
     catalogue y mène au niveau 2 quand sa cible est 1 — et rien ne le disait.

  4. LA COUVERTURE EST COMPLÈTE OU DÉCLARÉE INCOMPLÈTE. Pour chaque famille en
     écart, ou les formations retenues atteignent la cible, ou la famille
     figure dans `non_couvert`. Il n'existe aucun troisième cas, et c'est la
     règle qui l'interdit : un besoin qui disparaît entre l'écart et la
     proposition serait un besoin qu'on a oublié de servir.

  5. LA RÉDUCTION NE JETTE QUE DU REDONDANT. Un manager parti du niveau 1
     voyait les QUINZE formations du catalogue « retenues » — c'est-à-dire le
     catalogue, pas une proposition. La réduction se fait sur la couverture :
     la règle vérifie que chaque écartée pour redondance est bien couverte,
     au niveau qu'elle porte, par les formations gardées.

  6. UNE SEULE LISTE DE SECTEURS, ET UN SEUL CATALOGUE. Les vingt-deux
     sections viennent de `secteurs_nace` ; les quinze formations sont citées
     par numéro, avec le titre ATTENDU, et la règle relit les vrais titres
     dans `FORMATIONS_CAT`. Une dérive du catalogue fait tomber la règle au
     lieu de faire proposer un titre qui n'existe plus.

CE QUE CE FICHIER NE PEUT PAS MESURER, ET QUI LE MESURE :

  · L'ÉCRAN. Les quatre listes déroulantes se remplissent en JavaScript après
    chargement, et la sortie est peinte par un second appel : un fichier qui
    lit `sentinel.html` voit le gabarit, jamais l'écran.
    `outils/recette_competences_ia.js` ouvre le panneau dans un vrai
    navigateur, après une vraie connexion, choisit dans les listes et lit la
    sortie peinte — y compris que le rabattement du plafond arrive jusque-là.

  · LA GARDE DU MOTEUR. `competences_ia` se contrôle à l'import et lève : un
    défaut qu'elle attrape empêcherait de collecter CE fichier. Les portes qui
    comptent sont dans `tests/test_competences_ia_socle.py`, qui injecte le
    défaut dans une copie jetable et relit le message du refus.
"""
import io
import itertools
import os

import pytest

import competences_ia as M
import secteurs_nace

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


HTML = _lire("sentinel.html")
JS = _lire("sentinel.page.js")
APP = _lire("app.py")

#  LES TRIPLETS : six populations × dix fonctions × vingt-deux secteurs. On ne
#  tire pas au hasard et on n'en choisit pas trois — la table des secteurs
#  n'exige quelque chose que sur cinq sections, et un échantillon pourrait
#  n'en toucher aucune.
TRIPLETS = list(itertools.product(M._CLES_POPULATIONS, M._CLES_FONCTIONS,
                                  M._CODES_SECTEURS))
NIVEAUX = list(range(M.NIVEAU_MIN, M.NIVEAU_MAX + 1))


def _exig(pop, fon, sec, fam):
    """Ce que chaque entrée exige, lu dans les tables — sans passer par le
    moteur. C'est le seul moyen de mesurer son arithmétique : la recalculer
    depuis sa propre sortie ne prouverait rien."""
    s = M.CIBLE_SECTEUR.get(sec, ({}, ""))[0]
    return (M.CIBLE_POPULATION[pop].get(fam, 0),
            M.CIBLE_FONCTION[fon].get(fam, 0),
            s.get(fam, 0))


# ══════════════════════════════════════════════════════════════════════════
#  1. LA CIBLE — UN MAXIMUM RABATTU, JAMAIS UNE SOMME
# ══════════════════════════════════════════════════════════════════════════

def test_la_cible_est_le_MAXIMUM_des_trois_entrees_et_jamais_leur_somme():
    """TROIS ENTRÉES EXIGENT SUR LA MÊME FAMILLE. Pour un collaborateur du
    marketing dans la santé, « protéger » est exigé à 2 par la population, 3
    par la fonction et 4 par le secteur : la cible est 3 — le maximum, rabattu
    au plafond du rôle — et non 9."""
    for pop, fon, sec in TRIPLETS:
        c = M.cible(pop, fon, sec)
        assert c["ok"], (pop, fon, sec)
        plaf = M.PLAFOND_ROLE[pop]
        for f in c["familles"]:
            p, fo, se = _exig(pop, fon, sec, f["famille"])
            plancher = (M.PLANCHER_ART4_NIVEAU
                        if f["famille"] in M.PLANCHER_ART4 else 0)
            attendu = max(p, min(fo, plaf), min(se, plaf), plancher)
            assert f["cible"] == attendu, (
                "%s/%s/%s, famille %s : le moteur rend %d, le maximum des "
                "trois entrées rabattu vaut %d (population %d, fonction %d, "
                "secteur %d, plafond %d)"
                % (pop, fon, sec, f["famille"], f["cible"], attendu,
                   p, fo, se, plaf))
            assert f["cible"] <= M.NIVEAU_MAX


def test_la_cible_ne_depasse_JAMAIS_le_haut_de_l_echelle():
    """UNE SOMME SORTIRAIT DE L'ÉCHELLE, et le nom du niveau serait introuvable
    — l'écran afficherait une cible sans nom."""
    for pop, fon, sec in TRIPLETS:
        for f in M.cible(pop, fon, sec)["familles"]:
            assert f["cible"] in M._NIVEAUX_PAR_N
            assert f["cible_nom"] == M._NIVEAUX_PAR_N[f["cible"]]["nom"]


def test_CE_QUI_COMMANDE_est_une_entree_qui_atteint_vraiment_la_cible():
    """SANS CELA, UN COMITÉ QUI TROUVE UNE CIBLE TROP HAUTE NE SAIT PAS QUEL
    ARGUMENT DISCUTER. Et nommer une entrée dont l'exigence a été RABATTUE
    sous la cible dirait qu'elle commande alors qu'elle a été bornée."""
    for pop, fon, sec in TRIPLETS:
        plaf = M.PLAFOND_ROLE[pop]
        for f in M.cible(pop, fon, sec)["familles"]:
            if f["cible"] == 0:
                assert f["commande"] == []
                continue
            if f["commande"] == ["article 4"]:
                assert f["cible"] == M.PLANCHER_ART4_NIVEAU
                assert f["famille"] in M.PLANCHER_ART4
                for q in f["parts"]:
                    assert q["retenu"] < f["cible"]
                continue
            for nom in f["commande"]:
                q = [x for x in f["parts"] if x["entree"] == nom][0]
                assert q["retenu"] == f["cible"], (
                    "%s/%s/%s %s : « %s » est donnée comme commandant la "
                    "cible %d, mais elle n'exige que %d après rabattement"
                    % (pop, fon, sec, f["famille"], nom, f["cible"],
                       q["retenu"]))
            assert plaf >= f["cible"] or f["famille"] in M.PLANCHER_ART4


# ══════════════════════════════════════════════════════════════════════════
#  1 bis. LA COMPOSITION NUE — DEUX PROPRIÉTÉS QUE LA SORTIE NE MONTRE PAS
# ══════════════════════════════════════════════════════════════════════════
#
# POURQUOI CES DEUX RÈGLES EXISTENT, ET C'EST LA BATTERIE DE MUTATIONS QUI
# L'A DIT. Deux mutations SURVIVAIENT à toutes les règles écrites sur
# `cible()` : supprimer le plancher de l'article 4, et appliquer le plafond
# de rôle à la population aussi. Ni l'une ni l'autre ne change une sortie du
# dépôt — les six populations exigent déjà au moins 1 sur « comprendre » et
# « protéger », et la seule population plafonnée n'exige que 2 d'elle-même.
# Ce n'étaient pas des règles faibles : ces propriétés ne sont pas
# observables depuis les tables d'aujourd'hui. `composer()` les rend
# mesurables sur des exigences qui n'y existent pas.

def test_le_PLANCHER_de_l_article_4_mord_quand_AUCUNE_entree_n_exige_rien():
    """UNE TABLE QUI DESCENDRAIT UNE POPULATION À ZÉRO sur « comprendre » ou
    « protéger » sortirait sous l'article 4 sans que rien ne le dise. Le
    plancher garde ce cas-là, et il est nommé dans la sortie."""
    for fam in M.PLANCHER_ART4:
        niv, _, commande = M.composer(0, 0, 0, M.NIVEAU_MAX, fam)
        assert niv == M.PLANCHER_ART4_NIVEAU, (fam, niv)
        assert commande == ["article 4"], (fam, commande)
    for fam in M._CLES_FAMILLES:
        if fam in M.PLANCHER_ART4:
            continue
        #  ET PAS DE PLANCHER AILLEURS : un collaborateur qui n'emploie pas
        #  d'IA dans son activité n'a aucune raison d'être noté sur
        #  « appliquer ».
        niv, _, commande = M.composer(0, 0, 0, M.NIVEAU_MAX, fam)
        assert niv == 0 and commande == [], (fam, niv, commande)


def test_le_plafond_de_role_ne_rabat_JAMAIS_la_population():
    """LA POPULATION PORTE LE RÔLE : la rabattre sous son propre rôle
    donnerait un plafond qui se contredit. La garde d'import refuse déjà une
    table où une population exigerait plus que son plafond ; ici on éprouve
    l'arithmétique elle-même, sur une exigence que les tables n'ont pas."""
    niv, retenus, commande = M.composer(5, 5, 5, 3, "appliquer")
    par = {r[0]: r for r in retenus}
    assert par["population"][1] == 5, "l'exigence de la population a été rabattue"
    assert par["population"][2] == 5
    assert par["fonction"][1] == 3 and par["secteur"][1] == 3
    assert niv == 5 and commande == ["population"]


# ══════════════════════════════════════════════════════════════════════════
#  2. LE PLAFOND DE RÔLE — DANS LES DEUX SENS
# ══════════════════════════════════════════════════════════════════════════

def test_un_COLLABORATEUR_n_est_jamais_envoye_a_un_niveau_de_ROLE():
    """LES NIVEAUX 4 ET 5 DÉCRIVENT UN RÔLE. « Collaborateur sans
    encadrement » est l'intitulé de la population : ni un secteur sensible ni
    une direction technique ne lui donnent ce rôle. Mesuré avant le plafond :
    la fonction « systèmes d'information » exige 5 sur « protéger », et un
    collaborateur de ce service ressortait à « Concevoir ou expertiser »."""
    plaf = M.PLAFOND_ROLE["collaborateur"]
    assert plaf < M.NIVEAU_MAX, ("le plafond du collaborateur vaut %d : il ne "
                                 "plafonne plus rien" % plaf)
    for fon, sec in itertools.product(M._CLES_FONCTIONS, M._CODES_SECTEURS):
        for f in M.cible("collaborateur", fon, sec)["familles"]:
            assert f["cible"] <= plaf, (
                "collaborateur/%s/%s : « %s » est visée au niveau %d, au-delà "
                "du plafond de rôle %d" % (fon, sec, f["famille"],
                                           f["cible"], plaf))


def test_le_rabattement_est_DIT_la_ou_il_mord_et_PAS_la_ou_il_ne_mord_pas():
    """UN RABATTEMENT MUET SE LIT COMME UNE ERREUR DE CALCUL : la fonction
    affiche 5, la cible affiche 3, et rien n'explique l'écart."""
    mordu = 0
    for pop, fon, sec in TRIPLETS:
        c = M.cible(pop, fon, sec)
        plaf = M.PLAFOND_ROLE[pop]
        for f in c["familles"]:
            for q in f["parts"]:
                brut = dict(zip(("population", "fonction", "secteur"),
                                _exig(pop, fon, sec, f["famille"])))[q["entree"]]
                assert q["exige"] == brut
                borne = q["entree"] != "population"
                attendu = min(brut, plaf) if borne else brut
                assert q["retenu"] == attendu
                assert q["plafonne"] == (brut > attendu)
                if q["plafonne"]:
                    mordu += 1
        assert c["plafond_mord"] == any(q["plafonne"] for f in c["familles"]
                                        for q in f["parts"])
    assert mordu > 0, ("aucun rabattement sur les 1 320 triplets : le plafond "
                       "de rôle ne porte sur rien, et sa raison écrite "
                       "décrirait un mécanisme mort")


def test_l_exigence_de_la_POPULATION_passe_ENTIERE_car_c_est_elle_le_role():
    """L'EXPERT TECHNIQUE EXIGE 5 SUR « PROTÉGER » ET SUR « ENCADRER ». Un
    plafond appliqué à la population aussi aurait rabattu le rôle sous
    lui-même, et personne n'aurait plus jamais été visé au niveau 5."""
    hauts = 0
    for pop in M._CLES_POPULATIONS:
        for fam, niv in M.CIBLE_POPULATION[pop].items():
            c = M.cible(pop, M._CLES_FONCTIONS[0], "A")
            rendu = [f for f in c["familles"] if f["famille"] == fam][0]
            assert rendu["cible"] >= niv, (
                "%s exige %d sur « %s » et le moteur ne vise que %d : "
                "l'exigence de la population a été rabattue"
                % (pop, niv, fam, rendu["cible"]))
            if niv >= 4:
                hauts += 1
    assert hauts > 0


def test_le_PLANCHER_de_l_article_4_tient_sur_les_1320_triplets():
    """L'ARTICLE 4 VISE LES PERSONNES QUI UTILISENT LES SYSTÈMES POUR LE COMPTE
    DU DÉPLOYEUR : aucune population n'est donc à zéro sur « comprendre » ni
    sur « protéger ». Et le niveau 1 est la lecture du cabinet, pas une
    exigence du texte — la source servie doit le dire."""
    for pop, fon, sec in TRIPLETS:
        for f in M.cible(pop, fon, sec)["familles"]:
            if f["famille"] in M.PLANCHER_ART4:
                assert f["cible"] >= M.PLANCHER_ART4_NIVEAU, (pop, fon, sec)
    assert "2024/1689" in M.PLANCHER_SOURCE
    assert "lecture du cabinet" in M.PLANCHER_SOURCE


# ══════════════════════════════════════════════════════════════════════════
#  3. LA PROPOSITION — CE QU'ELLE REFUSE DE FAIRE
# ══════════════════════════════════════════════════════════════════════════

_ECHANTILLON = [
    ("collaborateur", "marketing", "Q"), ("collaborateur", "si_data", "K"),
    ("manager", "rh", "O"), ("dirigeant", "direction", "J"),
    ("referent_ia", "rd", "A"), ("expert_technique", "si_data", "K"),
    ("expert_conformite", "qualite_hse", "P"), ("collaborateur", "operations", "A"),
]
_CAS = [(p, f, s, n) for (p, f, s) in _ECHANTILLON for n in NIVEAUX]


@pytest.mark.parametrize("pop,fon,sec,niv", _CAS)
def test_aucune_formation_RETENUE_ne_l_est_pour_depasser_la_cible(pop, fon, sec, niv):
    """UNE PERSONNE DONT LA CIBLE EST 3 N'A PAS BESOIN DU NIVEAU 5, et le lui
    proposer coûte des jours et de la crédibilité. Une formation n'entre donc
    que si elle répond à un besoin SANS dépasser — ce qu'elle apporte au-delà
    est un supplément, jamais le motif de son choix."""
    r = M.proposer(pop, fon, sec, niv)
    assert r["ok"]
    cibles = {f["famille"]: f["cible"] for f in r["familles"]}
    for f in r["formations"]:
        porte = [a for a in M.APPORTS if a["n"] == f["n"]][0]["porte"]
        motifs = [fam for fam, p in porte.items()
                  if cibles.get(fam, 0) > niv and niv < p <= cibles[fam]]
        assert motifs, (
            "la formation n°%d est retenue pour %s/%s/%s au niveau %d sans "
            "répondre à aucun besoin en deçà de la cible : %s"
            % (f["n"], pop, fon, sec, niv, porte))
        for a in f["ajoute"]:
            assert a["porte_a"] <= cibles[a["famille"]]


@pytest.mark.parametrize("pop,fon,sec,niv", _CAS)
def test_chaque_famille_en_ECART_est_couverte_OU_declaree_NON_COUVERTE(pop, fon, sec, niv):
    """IL N'EXISTE AUCUN TROISIÈME CAS. Un besoin qui disparaît entre l'écart
    et la proposition est un besoin qu'on a oublié de servir, et une absence
    silencieuse se lit comme un oubli."""
    r = M.proposer(pop, fon, sec, niv)
    atteint = {}
    for f in r["formations"]:
        for a in f["ajoute"]:
            atteint[a["famille"]] = max(atteint.get(a["famille"], 0), a["porte_a"])
    trous = {x["famille"]: x for x in r["non_couvert"]}
    for f in r["familles"]:
        if f["ecart"] <= 0:
            assert f["famille"] not in trous
            continue
        if atteint.get(f["famille"], niv) >= f["cible"]:
            assert f["famille"] not in trous, (
                "« %s » est couverte jusqu'à %d et pourtant déclarée non "
                "couverte" % (f["famille"], atteint[f["famille"]]))
        else:
            assert f["famille"] in trous, (
                "%s/%s/%s niveau %d : « %s » est en écart de %d, les "
                "formations retenues ne l'atteignent pas, et rien ne le dit"
                % (pop, fon, sec, niv, f["famille"], f["ecart"]))
            assert trous[f["famille"]]["atteint"] == atteint.get(f["famille"], niv)
            assert trous[f["famille"]]["dit"]


@pytest.mark.parametrize("pop,fon,sec,niv", _CAS)
def test_une_formation_ECARTEE_pour_REDONDANCE_l_est_vraiment(pop, fon, sec, niv):
    """LA RÉDUCTION SE MESURE SUR LA COUVERTURE, ce n'est pas un plafond sur le
    nombre de lignes. Mesuré avant elle : un manager parti du niveau 1 voyait
    les quinze formations du catalogue retenues — le catalogue, pas une
    proposition."""
    r = M.proposer(pop, fon, sec, niv)
    atteint = {}
    for f in r["formations"]:
        for a in f["ajoute"]:
            atteint[a["famille"]] = max(atteint.get(a["famille"], 0), a["porte_a"])
    cibles = {f["famille"]: f["cible"] for f in r["familles"]}
    ecart = {f["famille"] for f in r["familles"] if f["ecart"] > 0}
    for x in r["redondantes"]:
        porte = [a for a in M.APPORTS if a["n"] == x["n"]][0]["porte"]
        for fam, p in porte.items():
            if fam not in ecart or p <= niv:
                continue
            credit = min(p, cibles[fam])
            assert atteint.get(fam, niv) >= credit, (
                "la formation n°%d est écartée comme redondante alors qu'elle "
                "porterait « %s » au niveau %d, et les retenues n'y vont "
                "qu'à %d" % (x["n"], fam, credit, atteint.get(fam, niv)))
        assert "n'ajoute aucun palier" in x["motif"]


@pytest.mark.parametrize("pop,fon,sec,niv", _CAS)
def test_le_nombre_de_formations_retenues_reste_une_PROPOSITION(pop, fon, sec, niv):
    """SIX FAMILLES, DONC AU PLUS SIX FORMATIONS UTILES : chacune doit élever
    au moins une famille, et une famille ne peut être élevée qu'une fois à son
    plafond de cible. Au-delà, ce n'est plus une proposition."""
    r = M.proposer(pop, fon, sec, niv)
    assert len(r["formations"]) <= len(M.FAMILLES), (
        "%d formations retenues pour %s/%s/%s au niveau %d"
        % (len(r["formations"]), pop, fon, sec, niv))
    vus = set()
    for f in r["formations"]:
        assert f["ajoute"], "la formation n°%d est gardée sans rien ajouter" % f["n"]
        assert f["n"] not in vus
        vus.add(f["n"])
    #  LES TROIS SACS SONT DISJOINTS, et leur union ne dépasse pas le
    #  catalogue : une formation à la fois retenue et écartée serait deux
    #  réponses contradictoires sur le même écran.
    ec = {x["n"] for x in r["ecartees"]}
    rd = {x["n"] for x in r["redondantes"]}
    assert not (vus & ec) and not (vus & rd) and not (ec & rd)
    assert len(vus | ec | rd) <= len(M.APPORTS)


@pytest.mark.parametrize("pop,fon,sec,niv", _CAS)
def test_l_arrivee_ne_descend_JAMAIS_sous_le_depart(pop, fon, sec, niv):
    """UNE PERSONNE AU NIVEAU 5 DONT LA PLUS HAUTE CIBLE EST 4 NE « VA » PAS AU
    NIVEAU 4 : elle est déjà au-delà. L'écrire autrement donnerait une
    trajectoire descendante, qui n'a aucun sens dans un plan de formation."""
    r = M.proposer(pop, fon, sec, niv)
    assert r["depart"]["niveau"] == niv
    assert r["arrivee"]["niveau"] >= niv, (
        "%s/%s/%s : départ %d, arrivée %d"
        % (pop, fon, sec, niv, r["arrivee"]["niveau"]))
    haute = max(f["cible"] for f in r["familles"])
    assert r["arrivee"]["niveau"] == max(haute, niv)
    assert r["arrivee"]["cible_la_plus_haute"] == haute
    assert r["arrivee"]["au_dela_de_la_cible"] == (niv > haute)
    if niv > haute:
        assert "dépasse déjà" in r["arrivee"]["dit"]


@pytest.mark.parametrize("pop,fon,sec,niv", _CAS)
def test_la_NATURE_suit_le_PIRE_ecart_et_rien_d_autre(pop, fon, sec, niv):
    """« CURSUS » N'EST PAS UN MOT PLUS FORT POUR DIRE « FORMATION » : il dit
    qu'aucune séance isolée ne comble l'écart. Trois paliers sur une seule
    famille suffisent, et la moyenne des six n'y change rien."""
    r = M.proposer(pop, fon, sec, niv)
    pire = max(f["ecart"] for f in r["familles"])
    assert r["pire_ecart"] == pire
    if pire == 0:
        attendu = "atteint"
    elif pire >= 3:
        attendu = "cursus"
    elif pire == 1 and niv <= 1:
        attendu = "sensibilisation"
    else:
        attendu = "formation"
    assert r["nature"] == attendu, (
        "%s/%s/%s niveau %d : pire écart %d, nature « %s »"
        % (pop, fon, sec, niv, pire, r["nature"]))
    assert r["nature_dit"] == M.NATURES[attendu]
    if attendu == "atteint":
        assert r["formations"] == []
        assert r["non_couvert"] == []


# ══════════════════════════════════════════════════════════════════════════
#  4. UNE SEULE SOURCE POUR LES SECTEURS, UNE SEULE POUR LE CATALOGUE
# ══════════════════════════════════════════════════════════════════════════

def test_les_secteurs_sont_LUS_dans_secteurs_nace_et_jamais_recopies():
    """DEUX LISTES DE SECTEURS DANS UN DÉPÔT DIVERGENT. Le module lit les
    vingt-deux sections de la nomenclature ; la règle compare code par code,
    et refuse qu'un intitulé officiel soit retapé dans ce fichier."""
    lus = M.secteurs()
    assert [s["code"] for s in lus] == [s["code"] for s in secteurs_nace.SECTIONS]
    for a, b in zip(lus, secteurs_nace.SECTIONS):
        assert a["nom"] == b["intitule"]
        assert a["officiel"] == b["intitule_officiel"]
    src = _lire("competences_ia.py")
    for s in secteurs_nace.SECTIONS:
        assert s["intitule_officiel"] not in src, (
            "l'intitulé officiel de la section %s est recopié dans "
            "competences_ia.py" % s["code"])


def test_toute_exigence_SECTORIELLE_porte_une_raison_ECRITE_et_SERVIE():
    """UNE EXIGENCE SECTORIELLE SANS MOTIF NE SE DISCUTE PAS. Et la raison doit
    arriver avec la proposition : reléguée au code, elle ne répond à personne."""
    for code, (exig, raison) in M.CIBLE_SECTEUR.items():
        assert exig and raison and len(raison) > 40, code
        r = M.proposer("collaborateur", "operations", code, 1)
        assert r["raison_secteur"] == raison
        assert r["secteur_neutre"] is False
    neutre = [c for c in M._CODES_SECTEURS if c not in M.CIBLE_SECTEUR][0]
    r = M.proposer("collaborateur", "operations", neutre, 1)
    assert r["secteur_neutre"] is True
    assert "pas une réponse" not in r["raison_secteur"]
    assert r["raison_secteur"] == M._SECTEURS_NEUTRES_DIT


def test_le_secteur_choisi_CHANGE_vraiment_la_cible_pour_les_cinq_sections():
    """SI UNE EXIGENCE SECTORIELLE NE DÉPLAÇAIT RIEN, les vingt-deux entrées de
    la liste déroulante seraient un décor.

    LA RÈGLE CHERCHE, POUR CHAQUE SECTION, UN TRIPLET QU'ELLE ÉLÈVE — et non
    un triplet choisi d'avance. Première version : elle comparait sur
    « manager / opérations », dont la population exige déjà 3 sur « évaluer »
    et « protéger » ; les sections P et J n'y changeaient rien et la règle
    tombait sur son propre choix de témoin, pas sur un défaut du module."""
    neutre = [c for c in M._CODES_SECTEURS if c not in M.CIBLE_SECTEUR][0]
    for code in M.CIBLE_SECTEUR:
        eleve = []
        for pop, fon in itertools.product(M._CLES_POPULATIONS, M._CLES_FONCTIONS):
            avant = {f["famille"]: f["cible"]
                     for f in M.cible(pop, fon, neutre)["familles"]}
            apres = {f["famille"]: f["cible"]
                     for f in M.cible(pop, fon, code)["familles"]}
            for fam in apres:
                #  JAMAIS À LA BAISSE : un secteur élève une exigence, il
                #  n'en dispense aucune.
                assert apres[fam] >= avant[fam], (code, pop, fon, fam)
                if apres[fam] > avant[fam]:
                    eleve.append((pop, fon, fam))
        assert eleve, (
            "la section %s n'élève AUCUNE cible sur les soixante couples "
            "population/fonction : son exigence est morte" % code)


def _catalogue_js():
    """LES VRAIS TITRES, LUS DANS `FORMATIONS_CAT`. Le moteur cite les
    formations par numéro et porte le titre ATTENDU ; si le catalogue dérive,
    c'est cette règle qui tombe — pas l'écran qui propose un titre mort.

    LE CATALOGUE EST DU JSON, ET ON LE LIT COMME TEL. Une expression
    régulière sur des guillemets simples n'y trouvait rien — et une règle qui
    ne trouve rien passe pour une règle qui ne mesure rien."""
    import json as _json
    i = JS.index("window.FORMATIONS_CAT")
    deb = JS.index("[", i)
    fin = JS.index("];", deb)
    return {f["n"]: f["t"] for f in _json.loads(JS[deb:fin + 1])}


def test_chaque_formation_CITEE_existe_au_catalogue_avec_le_titre_ATTENDU():
    cat = _catalogue_js()
    assert len(cat) >= len(M.APPORTS), (
        "le catalogue lu dans sentinel.page.js ne porte que %d titres pour %d "
        "formations rattachées" % (len(cat), len(M.APPORTS)))
    for a in M.APPORTS:
        assert a["n"] in cat, ("la formation n°%d n'existe pas au catalogue"
                               % a["n"])
        assert cat[a["n"]] == a["titre_attendu"], (
            "la formation n°%d s'appelle « %s » au catalogue et « %s » dans le "
            "référentiel : le catalogue a dérivé"
            % (a["n"], cat[a["n"]], a["titre_attendu"]))
    assert "FORMATIONS_CAT" in M.CATALOGUE_SOURCE


def test_une_SEULE_formation_est_la_porte_d_entree_de_qui_part_de_zero():
    """DEUX SENSIBILISATIONS LAISSERAIENT CHOISIR, et le module n'a aucun
    élément pour trancher ; zéro laisserait sans porte celui qui part de rien."""
    sensib = [a for a in M.APPORTS if a.get("sensibilisation")]
    assert len(sensib) == 1
    r = M.proposer("collaborateur", "operations", "A", 0)
    assert sensib[0]["n"] in [f["n"] for f in r["formations"]], (
        "la sensibilisation n'est pas proposée à qui n'a aucun repère")


# ══════════════════════════════════════════════════════════════════════════
#  5. LES RÉSERVES — ELLES PARTENT AVEC LE RÉSULTAT
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("niv", NIVEAUX)
def test_la_reserve_du_niveau_DECLARE_part_avec_CHAQUE_reponse(niv):
    """LE MODULE NE CONSTATE AUCUNE COMPÉTENCE. Une sortie qui rendrait
    « niveau 2 » sans cette réserve laisserait croire à une évaluation qui n'a
    pas eu lieu — et une réserve reléguée en bas d'écran s'applique à un
    chiffre qu'on ne regarde plus."""
    r = M.proposer("collaborateur", "operations", "A", niv)
    quois = [x["quoi"] for x in r["reserves"]]
    assert any("déclaré, pas mesuré" in q for q in quois)
    assert len(r["reserves"]) >= 3
    #  AU-DESSUS DE L'AUTONOMIE, UNE RÉSERVE DE PLUS : c'est à partir de là que
    #  l'écart entre l'aisance ressentie et le contrôle exercé se creuse.
    assert (len(r["reserves"]) == 4) == (niv >= 3)
    for x in r["reserves"]:
        assert x["quoi"] and x["pourquoi"] and x["quoi_faire"]


def test_le_PLAFOND_de_role_porte_sa_raison_et_elle_part_avec_la_reponse():
    r = M.proposer("collaborateur", "si_data", "K", 1)
    assert r["plafond_mord"] is True
    assert r["plafond_role"] == M.PLAFOND_ROLE["collaborateur"]
    assert "ne confèrent pas le rôle" in r["plafond_role_dit"]
    assert M.PLAFOND_ROLE_DIT


# ══════════════════════════════════════════════════════════════════════════
#  6. LES ENTRÉES REFUSÉES — LE MODULE NE DEVINE PAS
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("pop,fon,sec", [
    ("", "marketing", "Q"), ("inconnue", "marketing", "Q"),
    ("collaborateur", "", "Q"), ("collaborateur", "marketing", ""),
    ("collaborateur", "marketing", "ZZ"), (None, None, None),
])
def test_une_entree_VIDE_ou_INCONNUE_est_refusee_et_le_refus_NOMME(pop, fon, sec):
    """UNE CIBLE DEVINÉE À PARTIR D'UNE ENTRÉE VIDE EST UNE CIBLE INVENTÉE. Et
    le refus doit dire LAQUELLE manque : « entrée invalide » laisse chercher
    dans quatre listes déroulantes."""
    for r in (M.cible(pop, fon, sec), M.proposer(pop, fon, sec, 1)):
        assert r["ok"] is False
        assert r["manque"]
        for nom in r["manque"]:
            assert nom in r["dit"]


@pytest.mark.parametrize("niv", [-1, 6, 99, "deux", None, 1.5, True])
def test_un_niveau_HORS_ECHELLE_est_refuse(niv):
    r = M.proposer("collaborateur", "marketing", "Q", niv)
    assert r["ok"] is False, "le niveau %r a été accepté" % (niv,)
    assert str(M.NIVEAU_MAX) in r["dit"]


# ══════════════════════════════════════════════════════════════════════════
#  7. LES DEUX ROUTES, L'ÉCRAN ET LA BARRE
# ══════════════════════════════════════════════════════════════════════════

def test_les_DEUX_routes_existent_et_portent_la_CADENCE_des_autres():
    """UNE ROUTE SANS CADENCE EST UNE PORTE OUVERTE : les trente-cinq autres
    routes de référentiel portent la même borne, et une seule sans elle
    suffirait à épuiser le service."""
    for chemin, methode in (("/api/competences-ia/referentiel", "GET"),
                            ("/api/competences-ia/proposer", "POST")):
        decl = "@app.route('%s', methods=['%s'])" % (chemin, methode)
        assert decl in APP, "la route %s manque" % chemin
        suite = APP[APP.index(decl):APP.index(decl) + 400]
        assert "@rate_limit(limit=120, window=60)" in suite, (
            "la route %s ne porte pas la cadence des autres" % chemin)
    assert "import competences_ia" in APP


def test_la_route_de_PROPOSITION_accepte_un_niveau_ECRIT_par_une_liste():
    """UN `<select>` REND UNE CHAÎNE, TOUJOURS. Une route qui n'accepterait que
    l'entier refuserait tout ce que l'écran lui envoie — mais elle doit
    refuser « deux », qui n'est pas un niveau."""
    i = APP.index("def api_competences_ia_proposer")
    bloc = APP[i:APP.index("@app.route", i)]
    assert "isdigit()" in bloc and "int(" in bloc
    assert "competences_ia.proposer" in bloc
    assert "400" in bloc, "la route rend 200 sur une entrée refusée"


def test_l_ecran_porte_les_QUATRE_listes_que_la_demande_nomme():
    """LES QUATRE ENTRÉES DEMANDÉES : type de personne, secteur d'activité,
    fonction métier, niveau de connaissances. Chacune est une liste
    déroulante, chacune porte l'identifiant que le JavaScript remplit, et
    chacune rappelle la proposition en changeant."""
    i = HTML.index('id="p-competences"')
    panneau = HTML[i:HTML.index('<!-- MON ESPACE -->', i)]
    for cle in ("population", "fonction", "secteur", "niveau"):
        sel = '<select class="form-el" id="comp-%s" onchange="compProposer()">' % cle
        assert sel in panneau, "la liste déroulante « %s » manque à l'écran" % cle
        assert "_compRemplir('comp-%s'" % cle in JS, (
            "rien ne remplit la liste « %s » : elle resterait vide" % cle)
        assert 'for="comp-%s"' % cle in panneau, (
            "la liste « %s » n'a pas d'étiquette associée" % cle)
    assert 'id="comp-sortie"' in panneau
    assert "window.compInit" in JS and "window.compProposer" in JS


def test_la_barre_mene_a_l_ecran_et_l_AMORCE_est_dans_son_appel():
    """UN ONGLET SANS AMORCE PEINT UN ÉCRAN VIDE. Le mécanisme générique de
    `go()` lit les fonctions nommées dans l'appel de l'onglet : si l'appel
    n'en nomme aucune, les quatre listes restent vides."""
    import re as _re
    items = _re.findall(r'class="sb-item[^"]*"[^>]*onclick="([^"]+)"', HTML)
    notre = [o for o in items if "go('competences'" in o]
    assert len(notre) == 1, ("l'écran a %d entrée(s) de barre" % len(notre))
    assert "compInit()" in notre[0], (
        "l'onglet n'amorce rien : l'écran s'ouvrirait avec quatre listes vides")
    #  LE VOISINAGE EST LA DEMANDE : « intégrer dans hub training ».
    assert 'data-grp="equipe-et-formation"' in \
        HTML[HTML.index("go('competences'") - 400:HTML.index("go('competences'")]
    assert HTML.index("go('training'") < HTML.index("go('competences'")
    assert "competences:" in JS, "PAGE_META ne connaît pas l'écran"


def test_tout_le_FRANCAIS_neuf_de_l_ecran_est_TRADUIT():
    """LE PLANCHER DE COUVERTURE EST À 1,0 : une chaîne servie en français et
    absente du dictionnaire anglais fait tomber le gardien. La règle relit
    les clés du panneau et les cherche dans le dictionnaire."""
    import re as _re
    i = HTML.index('id="p-competences"')
    panneau = HTML[i:HTML.index('<!-- MON ESPACE -->', i)]
    cles = set(_re.findall(r'data-i18n(?:-bloc)?="([^"]+)"', panneau))
    cles.add("nav.item.competences")
    assert len(cles) >= 9, ("le panneau ne porte que %d clés de traduction : "
                            "du français y est écrit sans clé" % len(cles))
    for c in sorted(cles):
        assert "'%s':" % c in JS, (
            "la clé « %s » n'a aucune traduction anglaise" % c)
