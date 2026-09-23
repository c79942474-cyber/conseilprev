# -*- coding: utf-8 -*-
"""LE CALQUE FRANÇAIS — ET LE TAUX QUI NE DOIT JAMAIS DEVENIR UNE CONFORMITÉ.

CE QUI A ÉTÉ DEMANDÉ. « En fonction des documents joints sur la loi et les
référentiels ANSSI sur la NIS 2, le ReCyF et le guide de protection, dire si
l'on doit compléter ou modifier l'analyse de risque NIS 2 dans Sentinel. »
Réponse mesurée : compléter, et l'écart est structurel.

CE QUE `nis2` MESURAIT, ET OÙ IL S'ARRÊTAIT. Dix mesures de l'article 21 §2,
cinq points de gouvernance. Sa réserve disait déjà que c'est la loi de
transposition qui oblige — et ne disait pas ce que celle-ci prépare. Zéro
occurrence de « ReCyF » ou « ANSSI » dans le module.

CE QUE LA FRANCE PRÉPARE A UNE AUTRE FORME. L'article 14 du projet de loi
remplace les dix mesures par quatre familles et renvoie au ReCyF : vingt
objectifs, 152 moyens acceptables de conformité pour une entité essentielle,
76 pour une importante. C'est la première fois que la distinction
essentielle / importante change LES MESURES, et pas seulement la supervision
et le plafond d'amende.

LA DÉCISION D'ARCHITECTURE QUE CES RÈGLES GARDENT. Aucun de ces deux textes
n'est en vigueur : le projet de loi n'est pas voté, le référentiel porte
« DOCUMENT DE TRAVAIL » sur chaque page, le décret n'existe pas. Le module
rend donc un taux de PRÉPARATION, et il ne se fond dans aucun indice de
conformité. Un chiffre présenté comme une conformité contre un texte qui
n'existe pas encore serait faux d'une manière qui ne se voit pas — et c'est
cette invisibilité qui en fait le défaut le plus grave.
"""
import io
import os
import re

import pytest

import nis2
import nis2_recyf as recyf

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


APP = _lire("app.py")
HTML = _lire("sentinel.html")
JS = _lire("sentinel.page.js")
CONFORMITE = _lire("conformite.py")


# ══════════════════════════════════════════════════════════════════════════
#  1. LE TAUX EST UNE PRÉPARATION, ET RIEN D'AUTRE
# ══════════════════════════════════════════════════════════════════════════

def test_le_taux_se_declare_PREPARATION_et_jamais_conformite():
    """LA RÈGLE QUI PORTE TOUTE LA DÉCISION D'ARCHITECTURE.

    Le nom de la clé n'est pas un détail de présentation : c'est ce qu'un
    écran affichera, ce qu'une capture d'écran emportera en comité, et ce
    qu'un client retiendra. Un module qui rendrait `taux_conformite` contre
    un document de travail aurait menti sans qu'aucune ligne ne soit
    fausse."""
    r = recyf.preparation("essentielle", {})
    assert r["nature"] == "préparation", r["nature"]
    assert "taux_preparation" in r
    assert "taux_conformite" not in r, (
        "le module rend un taux de conformité contre un texte qui n'est pas "
        "en vigueur")
    assert "taux" not in r, (
        "une clé `taux` nue serait lue comme une conformité par le premier "
        "écran qui l'affiche")


def test_la_reserve_VOYAGE_avec_le_chiffre():
    """UNE MENTION POSÉE À CÔTÉ NE SUIT PAS LE NOMBRE. Elle est DANS le
    résultat : un écran qui n'afficherait que `taux_preparation` afficherait
    un taux sans sa nature, et c'est le cas qu'il faut rendre impossible."""
    r = recyf.preparation("essentielle", {1: "atteint"})
    assert r.get("ne_pas_confondre"), "le résultat ne porte plus sa réserve"
    assert "conformité" in r["ne_pas_confondre"], (
        "la réserve ne dit plus ce que le taux N'EST PAS")
    assert r.get("statut_du_texte", {}).get("en_vigueur") is False
    assert r.get("ce_qui_oblige_aujourdhui"), (
        "le résultat ne dit plus ce qui oblige RÉELLEMENT aujourd'hui")


def test_le_statut_declare_que_RIEN_n_est_en_vigueur():
    """LE JOUR OÙ CELA CHANGERA, CE SERA UNE DÉCISION. Cette règle tombera
    alors, et c'est ce qu'on veut : elle signalera qu'il faut reprendre la
    nature du taux, pas la laisser basculer toute seule."""
    assert recyf.STATUT["en_vigueur"] is False
    for attendu in ("vote de la loi", "décret"):
        assert any(attendu in x for x in recyf.STATUT["ce_qui_manque"]), (
            "le statut ne nomme plus %r parmi ce qui manque" % attendu)
    assert "2022/2555" in recyf.STATUT["ce_qui_oblige_aujourdhui"], (
        "le statut ne renvoie plus à la directive, qui est le seul texte "
        "qui oblige aujourd'hui")


def test_l_indice_de_conformite_IGNORE_ce_calque():
    """LE TAUX SÉPARÉ NE L'EST QUE S'IL RESTE DEHORS.

    `conformite.py` consolide les normes en un indice. Y faire entrer un
    taux de préparation le ferait monter ou descendre sur la foi d'un
    document de travail — exactement ce que la séparation devait empêcher.
    La règle est écrite ici, et non dans `conformite`, parce que c'est ce
    module-ci qui a la tentation."""
    assert "nis2_recyf" not in CONFORMITE, (
        "conformite.py consomme le calque français : le taux de préparation "
        "entre dans l'indice de conformité, ce qui le rend faux")
    assert "recyf" not in CONFORMITE.lower(), (
        "conformite.py cite le ReCyF : vérifier qu'il ne le compte pas")


# ══════════════════════════════════════════════════════════════════════════
#  2. LES VINGT OBJECTIFS, ET LA GRADATION
# ══════════════════════════════════════════════════════════════════════════

def test_les_totaux_sont_RECOMPTES_et_non_recopies():
    """LES NOMBRES DU COMMENTAIRE SE PÉRIMENT ; UNE ADDITION, NON. La garde
    du module les ré-additionne à chaque chargement — cette règle vérifie
    que la garde existe et qu'elle porte les bons totaux."""
    assert sum(o[3] for o in recyf.OBJECTIFS) == 152
    assert sum(o[4] for o in recyf.OBJECTIFS) == 76
    assert len(recyf.OBJECTIFS) == 20
    assert recyf._verifier() == (), recyf._verifier()


@pytest.mark.parametrize("numero", recyf.RESERVES_ESSENTIELLES)
def test_les_objectifs_16_a_20_sont_HORS_CHAMP_pour_une_importante(numero):
    """LE PRINCIPE DE PROPORTIONNALITÉ N'EST PAS UNE INDULGENCE. Ces cinq
    objectifs ne sont pas « plus difficiles » pour une entité importante :
    le référentiel ne les lui demande pas. Les afficher comme des écarts
    inventerait une dette qui n'existe pas."""
    o = recyf.OBJECTIFS_PAR_NUMERO[numero]
    assert o[4] == 0, (
        "l'objectif %d attend %d moyen(s) d'une entité importante" % (numero, o[4]))
    lignes = {l["numero"]: l for l in recyf.attendus("importante")["objectifs"]}
    assert lignes[numero]["dans_le_champ"] is False


def test_le_module_REFUSE_de_chiffrer_sans_qualification():
    """LA MOITIÉ DU RÉFÉRENTIEL EN DÉPEND. Un chiffre rendu sans statut
    serait une moyenne entre deux régimes qui ne se moyennent pas — et rien
    à l'écran ne dirait lequel a été pris."""
    for mauvais in (None, "", "moyenne", "inconnue"):
        r = recyf.attendus(mauvais)
        assert r["ok"] is False and r["refus"] == "statut_absent", mauvais
        assert recyf.preparation(mauvais)["taux_preparation"] is None
        # UN REFUS QUI N'EXPLIQUE PAS EST UNE IMPASSE. L'écran affiche cette
        # phrase telle quelle : elle doit dire POURQUOI, avec les deux
        # nombres qui rendent la gradation évidente.
        assert "152" in r["dit"] and "76" in r["dit"], (
            "le refus n'explique plus la gradation : %r" % r["dit"][:80])
        assert r.get("ou_la_trouver"), (
            "le refus ne dit plus où trouver la qualification")


def test_le_HORS_CHAMP_ne_compte_ni_au_numerateur_ni_au_denominateur():
    """LE DÉFAUT QUE CETTE RÈGLE REND IMPOSSIBLE : une entité importante qui
    afficherait un taux gonflé par cinq objectifs qu'elle n'a jamais eu à
    tenir — ou, à l'inverse, plafonné à 75 % pour la même raison.

    QUINZE OBJECTIFS ATTEINTS DOIVENT DONNER CENT POUR CENT."""
    tous = {n: "atteint" for n in range(1, 21)}
    ei = recyf.preparation("importante", tous)
    assert ei["sur"] == 15, ei["sur"]
    assert ei["taux_preparation"] == 100.0, ei["taux_preparation"]
    ee = recyf.preparation("essentielle", tous)
    assert ee["sur"] == 20 and ee["taux_preparation"] == 100.0
    # ET LE DIFFÉRENTIEL : sans lui, les deux régimes pourraient être
    # identiques et la règle passerait quand même.
    assert ei["nombre_moyens"] != ee["nombre_moyens"], (
        "les deux qualifications attendent le même nombre de moyens : la "
        "gradation a disparu")


def test_chaque_objectif_se_rattache_a_la_DIRECTIVE():
    """LE RATTACHEMENT VIENT DU RÉFÉRENTIEL, PAS DE NOUS. Sans lui, un
    client ne pourrait pas relier ce qu'on lui demande à l'article de la
    directive qu'il connaît déjà — et c'est par là qu'il entre."""
    for n, t, p, me, mi, d, corr in recyf.OBJECTIFS:
        assert corr, "l'objectif %d ne se rattache à rien" % n
        for a in corr:
            assert re.match(r"^(20|21\.2(\.[a-j])?)$", a), (
                "l'objectif %d cite %r, qui n'est pas une disposition de "
                "NIS 2" % (n, a))


# ══════════════════════════════════════════════════════════════════════════
#  3. LE VERROU DE PÉRIMÈTRE — OBJECTIF 1
# ══════════════════════════════════════════════════════════════════════════

def test_une_exclusion_motivee_par_la_SECURITE_est_refusee():
    """LE RÉFÉRENTIEL FERME CETTE PORTE EN TOUTES LETTRES : « la mise en
    œuvre de mesures de sécurité sur ces systèmes d'information ne permet
    pas de justifier qu'ils ne sont exposés à aucun des risques précités ».

    C'est le contournement le plus naturel — « c'est cloisonné, donc c'est
    hors périmètre » — et celui qu'un audit cherchera en premier."""
    r = recyf.perimetre([
        {"nom": "A", "exclu": True, "analyse_de_risques": True,
         "justification": "Le système est isolé et chiffré."},
    ])
    assert r["systemes"][0]["recevable"] is False
    assert any("mesures de sécurité" in m for m in r["systemes"][0]["motifs"])


def test_une_exclusion_SANS_justification_ou_SANS_analyse_est_refusee():
    """LES DEUX AUTRES PORTES. L'exclusion et sa justification doivent
    figurer explicitement dans la liste ; la justification s'appuie sur une
    analyse de risques. Une exclusion tacite n'existe pas."""
    r = recyf.perimetre([
        {"nom": "sans texte", "exclu": True, "analyse_de_risques": True},
        {"nom": "sans analyse", "exclu": True,
         "justification": "Ne porte aucune donnée d'activité."},
    ])
    assert r["exclusions_non_recevables"] == 2, r
    assert recyf.perimetre(None)["ok"] is False


def test_une_exclusion_RECEVABLE_le_reste():
    """LE GARDE-FOU DES DEUX RÈGLES PRÉCÉDENTES. Sans lui, un module qui
    refuserait TOUTE exclusion les ferait passer toutes les deux — et
    rendrait le périmètre impossible à borner, ce qui est un autre défaut."""
    r = recyf.perimetre([
        {"nom": "bac à sable", "exclu": True, "analyse_de_risques": True,
         "justification": "Ne porte aucune donnée d'activité et ne soutient "
                          "aucun service rendu ; sa perte n'interrompt rien."},
    ])
    assert r["systemes"][0]["recevable"] is True, r["systemes"][0]


def test_les_TROIS_risques_du_perimetre_sont_nommes():
    """Ils sont la seule grille d'exclusion admise, et ils sont trois."""
    assert len(recyf.RISQUES_DU_PERIMETRE) == 3
    cles = {c for c, _ in recyf.RISQUES_DU_PERIMETRE}
    assert cles == {"interruption", "divulgation", "alteration"}, cles


# ══════════════════════════════════════════════════════════════════════════
#  4. L'ANALYSE DE RISQUE — OBJECTIF 16
# ══════════════════════════════════════════════════════════════════════════

def test_l_analyse_de_risque_est_HORS_CHAMP_pour_une_importante():
    """ET ELLE NE REND SURTOUT PAS ZÉRO. Un 0 % serait lu comme un
    manquement ; le référentiel ne demande simplement rien ici."""
    r = recyf.analyse_de_risque({}, "importante")
    assert r["ok"] is True and r["hors_champ"] is True
    assert r["taux"] is None, (
        "un taux affiché serait lu comme un manquement : le référentiel ne "
        "demande pas cet objectif à une entité importante")
    assert r["ne_veut_pas_dire"], (
        "l'écran ne dit plus qu'une analyse reste nécessaire pour justifier "
        "une exclusion de périmètre")


def test_les_QUATRE_exigences_de_l_objectif_16_sont_distinctes():
    """DANS `nis2`, L'ANALYSE DE RISQUE EST UNE CASE SUR DIX. C'est ce que
    ce module corrige : quatre exigences, chacune vérifiable, chacune avec
    son piège."""
    assert len(recyf.ANALYSE_EXIGENCES) == 4
    refs = [e[1] for e in recyf.ANALYSE_EXIGENCES]
    assert refs == ["16.1", "16.2", "16.3", "16.4"], refs
    for cle, ref, titre, dit, piege in recyf.ANALYSE_EXIGENCES:
        assert len(piege) >= 40, (
            "%s n'a pas de piège utilisable : %r" % (ref, piege))


def test_une_analyse_DECLAREE_mais_incomplete_n_est_pas_acquise():
    """LE DÉFAUT QUE CETTE RÈGLE TRAQUE : une case cochée qui vaudrait
    conformité. Déclarer qu'on couvre chaque système sans citer aucune des
    cinq entrées nommées par le référentiel, c'est déclarer une opinion."""
    r = recyf.analyse_de_risque({
        "gouvernance": True, "moyens_alloues": False,
        "couverture": True, "entrees": [],
        "acceptation": True, "risques_residuels_acceptes": False,
        "plan_date_et_responsable": False,
        "reexamen": True, "dernier_reexamen_mois": 50,
    }, "essentielle")
    assert r["acquises"] == 0, r["acquises"]
    par = {e["cle"]: e for e in r["exigences"]}
    assert par["gouvernance"]["declare"] and not par["gouvernance"]["acquis"]
    assert any("moyen" in m for m in par["gouvernance"]["manque"])
    assert any("entrées" in m for m in par["couverture"]["manque"])
    assert any("résiduels" in m for m in par["acceptation"]["manque"])
    assert any("50" in m for m in par["reexamen"]["manque"])


def test_le_reexamen_a_un_PLANCHER_de_trente_six_mois():
    """« Au minimum tous les trois ans » — c'est une limite haute, pas une
    cadence. Un réexamen à trente-sept mois est un écart."""
    assert recyf.REEXAMEN_MOIS_MAX == 36
    d = {"gouvernance": True, "moyens_alloues": True,
         "couverture": True,
         "entrees": [c for c, _ in recyf.ANALYSE_ENTREES],
         "acceptation": True, "risques_residuels_acceptes": True,
         "plan_date_et_responsable": True, "reexamen": True}
    assert recyf.analyse_de_risque(dict(d, dernier_reexamen_mois=36),
                                   "essentielle")["taux"] == 100.0
    r = recyf.analyse_de_risque(dict(d, dernier_reexamen_mois=37),
                                "essentielle")
    assert r["taux"] != 100.0, "trente-sept mois passe encore"


def test_les_CINQ_entrees_de_l_analyse_sont_celles_du_referentiel():
    """Le référentiel les nomme, et c'est sur elles qu'un contrôle
    s'appuiera pour juger qu'une analyse est autre chose qu'une opinion."""
    assert len(recyf.ANALYSE_ENTREES) == 5
    cles = {c for c, _ in recyf.ANALYSE_ENTREES}
    assert cles == {"pssi", "ecosysteme", "si", "conformite", "audits"}, cles


# ══════════════════════════════════════════════════════════════════════════
#  5. LES DEUX PONTS, ET LEUR BORNE
# ══════════════════════════════════════════════════════════════════════════

def test_le_pont_ISO_est_PLAFONNE_par_son_perimetre_de_certification():
    """UN PONT RECOPIÉ SANS SA BORNE VAUDRAIT MOINS QUE PAS DE PONT. Le
    référentiel l'écrit : la certification vaut « sur les systèmes
    d'information COUVERTS PAR LA CERTIFICATION »."""
    p = {x["cle"]: x for x in recyf.ponts(True, False, False)["ponts"]}
    assert p["iso27001"]["etat"] == "partiel", p["iso27001"]["etat"]
    assert "couverts par la certification" in p["iso27001"]["borne"].lower()
    assert p["iso27001"]["objectifs"] == (2, 16)
    assert recyf.ponts(True, True, False)["ponts"][0]["etat"] == "complet"
    assert recyf.ponts(False, False, False)["ponts"][0]["etat"] == "absent"


def test_le_pont_PACS_est_borne_par_le_SUIVI_du_plan():
    """La prestation qualifiée ne suffit pas : le référentiel exige aussi
    le suivi, PAR L'ENTITÉ, du plan de traitement qui en est issu."""
    p = {x["cle"]: x for x in recyf.ponts(None, None, True)["ponts"]}
    assert p["pacs"]["etat"] == "complet"
    assert "suivi" in p["pacs"]["borne"].lower()
    assert p["pacs"]["objectifs"] == (16,)


def test_la_charge_de_la_PREUVE_bascule_et_le_module_le_dit():
    """ELLE N'EST DANS AUCUN AUTRE MODULE DU DÉPÔT, et c'est pourtant ce qui
    décide de la difficulté d'un contrôle."""
    pr = recyf.PREUVE
    assert "art. 15" in pr["avec_referentiel"]["article"]
    assert "prévaloir" in pr["avec_referentiel"]["dit"]
    assert "démontrer" in pr["sans_referentiel"]["dit"]


# ══════════════════════════════════════════════════════════════════════════
#  6. LE BRANCHEMENT — ET LE RENVOI DEPUIS `nis2`
# ══════════════════════════════════════════════════════════════════════════

def test_nis2_NOMME_le_calque_francais():
    """LA RÉSERVE DE `nis2` ÉTAIT EXACTE ET S'ARRÊTAIT TROP TÔT. Elle disait
    que c'est la loi de transposition qui oblige, sans dire ce que celle-ci
    prépare : un client français mesurait dix mesures quand l'ANSSI le
    contrôlera sur vingt objectifs."""
    t = nis2.TRANSPOSITION_FR
    assert t["module"] == "nis2_recyf"
    assert t["en_vigueur"] is False
    assert "152" in t["quoi"] and "76" in t["quoi"]
    assert "PRÉPARATION" in t["reserve"]
    # ET PAS DE CERCLE D'IMPORT : `nis2_recyf` peut lire `nis2`, l'inverse
    # fermerait la boucle au chargement.
    assert "import nis2_recyf" not in _lire("nis2.py")


@pytest.mark.parametrize("route", [
    "/api/recyf/referentiel", "/api/recyf/attendus", "/api/recyf/preparation",
    "/api/recyf/perimetre", "/api/recyf/analyse", "/api/recyf/ponts",
])
def test_chaque_route_du_calque_EXISTE(route):
    assert "@app.route('%s'" % route in APP, route


@pytest.mark.parametrize("panneau", ["recyf-objectifs", "recyf-analyse"])
def test_chaque_panneau_a_son_ecran_son_META_et_son_GUIDE(panneau):
    """LA CONVENTION DU DÉPÔT, ET ELLE A DÉJÀ COÛTÉ. Un panneau sans entrée
    dans PAGE_META n'a pas de fil d'Ariane ; sans guide, il retombe sur le
    guide générique — et personne ne s'en aperçoit."""
    assert 'id="p-%s"' % panneau in HTML, "le panneau n'existe pas"
    assert "go('%s'" % panneau in HTML, "aucune entrée de barre latérale"
    assert "'%s':" % panneau in JS, "absent de PAGE_META ou des guides"
    assert JS.count("'%s':" % panneau) >= 2, (
        "%s n'a qu'une seule déclaration : il lui manque son META ou son "
        "guide" % panneau)


def test_l_ecran_affiche_la_NATURE_du_taux_avec_le_nombre():
    """UNE RÈGLE PYTHON NE VOIT PAS CE QUE L'ÉCRAN REND — mais elle voit si
    le rendu a cessé de chercher la nature dans la réponse. Le contrôle
    visuel est dans `recette_recyf.js` ; celui-ci garde la mécanique."""
    assert "recyfEsc(j.nature)" in JS, (
        "le rendu n'affiche plus la nature du taux à côté du nombre")
    assert "recyfEsc(j.ne_pas_confondre)" in JS, (
        "le rendu n'affiche plus ce que le taux n'est pas")
    # ON VISE LA FONCTION QUI BÂTIT LE BLOC DU TAUX, PAS N'IMPORTE LAQUELLE.
    # `recyfRenduAnalyse` bâtit une boîte de même forme : une première
    # version de cette règle tombait sur elle et laissait passer une mutation
    # qui sortait le chiffre de SA boîte à lui. Le bloc a ensuite été extrait
    # dans `recyfBloTaux`, pour que le taux se repeigne SANS reconstruire la
    # liste des objectifs — une repeinture complète détachait les champs et
    # faisait perdre une sélection sur deux.
    bloc = re.search(r"function recyfBloTaux\(j\) \{(.*?)\n\}", JS, re.S)
    assert bloc, "la fonction qui bâtit le bloc du taux est introuvable"
    assert re.search(r"class=\"recyf-taux\">'\s*\+\s*'<div class=\"recyf-chiffre\"",
                     bloc.group(1)), (
        "le chiffre n'est plus dans la boîte qui porte sa nature : séparés, "
        "le nombre partira seul en comité")
    assert "recyfEsc(j.nature)" in bloc.group(1), (
        "la nature du taux n'est plus dans le même bloc que le chiffre")
    # ET LE CHANGEMENT D'ÉTAT NE DOIT PAS REPEINDRE LA LISTE.
    assert re.search(r"function recyfEtat\([^)]*\) \{\s*RECYF_ETATS\[numero\]"
                     r" = sel\.value;\s*recyfMajTaux\(\);", JS), (
        "un changement d'état repeint tout le corps du panneau : les "
        "sélecteurs sont détachés, et une sélection se perd")


def test_le_bandeau_de_statut_vient_du_MOTEUR():
    """UNE MENTION RECOPIÉE DANS LE HTML NE SUIVRAIT PAS. Le jour où le
    décret paraît, le statut change côté serveur et le bandeau doit changer
    avec lui — sans qu'on ait à retrouver la phrase dans la page."""
    assert "recyfEsc(s.ce_qui_oblige_aujourdhui)" in JS
    # LE CONTRÔLE VISAIT TROP LARGE. `s.en_vigueur ?` apparaît AUSSI dans le
    # calcul de la classe CSS du bandeau : une mutation qui figeait la PHRASE
    # le traversait sans le faire tomber. On vise donc la branche qui écrit
    # le texte, pas le nom de la variable.
    assert re.search(r"s\.en_vigueur \? 'Texte en vigueur\.' :", JS), (
        "la PHRASE du bandeau ne dépend plus de l'état du texte : elle est "
        "figée, et le jour du décret elle mentira")
    assert re.search(r"s\.en_vigueur \? '' : ' recyf-pas-en-vigueur'", JS), (
        "la marque visuelle de la réserve ne dépend plus de l'état du texte")
    assert 'id="recyf-statut"' in HTML


# ══════════════════════════════════════════════════════════════════════════
#  7. LA GARDE D'IMPORT — CE QU'ELLE REFUSE DE LAISSER CHARGER
# ══════════════════════════════════════════════════════════════════════════
#
# POURQUOI CES RÈGLES EXISTENT, ET ELLES SONT NÉES D'UNE MESURE.
# La batterie de mutations a rendu SIX SURVIVANTES sur ce module. Aucune
# n'était un trou dans les règles : `_verifier()` tourne au chargement et
# lève une assertion, si bien que le module MUTÉ ne s'importe plus du tout.
# Le lanceur lit une erreur de collecte comme une survivante.
#
# La garde fait donc son travail — et personne ne le mesurait. Ces règles
# FABRIQUENT le défaut dans une copie du module, et vérifient que la garde
# le NOMME. Sans elles, on pourrait retirer une vérification de `_verifier()`
# sans qu'aucune règle ne tombe.


def _charger_mute(avant, apres):
    """Charge une COPIE du module avec une substitution, et rend l'erreur.

    On n'écrit rien sur le disque : le module d'origine reste intact, et
    deux règles qui tourneraient en parallèle ne se marcheraient pas dessus.
    """
    src = _lire("nis2_recyf.py")
    assert src.count(avant) == 1, (
        "l'ancre de la mutation n'est plus unique dans le module : %r" % avant)
    espace = {"__name__": "nis2_recyf_mute"}
    try:
        exec(compile(src.replace(avant, apres, 1), "nis2_recyf_mute", "exec"),
             espace)
    except AssertionError as e:
        return str(e)
    return None


# LES IDENTIFIANTS SONT COURTS ET SANS ESPACE, ET C'EST UNE NÉCESSITÉ.
# Le lanceur de mutations compare des NOMS DE TEST exacts : un identifiant
# engendré depuis les paramètres contient des espaces et des guillemets, il
# se coupe au premier blanc, et la mutation est déclarée « mal visée » alors
# qu'elle a fait tomber la bonne règle.
@pytest.mark.parametrize("nom,avant,apres,attendu", [
    pytest.param("le texte se déclare en vigueur",
     '"en_vigueur": False,\n    "dit": "Ni le projet',
     '"en_vigueur": True,\n    "dit": "Ni le projet',
     "en vigueur", id="en-vigueur"),
    pytest.param("un objectif réservé aux EE est attendu d'une EI",
     '     5, 0,\n     "Se faire regarder par quelqu\'un d\'autre',
     '     5, 2,\n     "Se faire regarder par quelqu\'un d\'autre',
     "réservé aux entités essentielles", id="reserve-ee"),
    pytest.param("le total des moyens d'une essentielle change",
     '(20, "Supervision de la sécurité des systèmes d\'information", "defense",\n     6, 0,',
     '(20, "Supervision de la sécurité des systèmes d\'information", "defense",\n     7, 0,',
     "152", id="total-152"),
    pytest.param("le taux cesse de se déclarer préparation",
     '        "nature": "préparation",\n        "ne_pas_confondre"',
     '        "nature": "conformité",\n        "ne_pas_confondre"',
     "préparation", id="nature-preparation"),
    pytest.param("une source ne dit plus si elle a été lue",
     '     "lue": True,\n     "apporte": "Les vingt objectifs',
     '     "apporte": "Les vingt objectifs',
     "apporte", id="source-lue"),
])
def test_la_GARDE_refuse_de_charger_un_module_fausse(nom, avant, apres, attendu):
    """CHAQUE DÉFAUT FABRIQUÉ DOIT ÊTRE NOMMÉ PAR LA GARDE.

    Et elle doit le NOMMER, pas seulement échouer : un message qui ne dit
    pas ce qui ne va pas renvoie le lecteur à la lecture du fichier."""
    message = _charger_mute(avant, apres)
    assert message is not None, (
        "la garde a laissé charger un module où %s" % nom)
    assert attendu in message, (
        "la garde refuse, mais sans nommer le défaut — message : %r" % message)


def test_la_garde_LAISSE_passer_le_module_intact():
    """LE GARDE-FOU DE LA RÈGLE PRÉCÉDENTE. Une garde qui refuserait tout
    ferait passer les cinq cas ci-dessus sans rien mesurer."""
    assert recyf._FAUTES == (), recyf._FAUTES
    # UNE SUBSTITUTION SANS EFFET, sur une ancre unique : le module doit
    # charger. `"nature": "préparation"` apparaît deux fois — dans le taux
    # et dans l'analyse de risque — donc on vise la ligne de la garde.
    assert _charger_mute('    fautes = []\n    if len(OBJECTIFS) != 20:',
                         '    fautes = []  # inchangé\n    if len(OBJECTIFS) != 20:') is None


def test_le_taux_de_preparation_ne_repeint_que_la_DERNIERE_demande():
    """MESURÉ EN RECETTE : quinze objectifs passés à « atteint » d'affilée
    ont affiché 93,3 %. Chaque réponse relance le calcul sans attendre le
    précédent ; celui du quatorzième, revenu APRÈS celui du quinzième, avait
    repeint le taux. Seule la réponse à la dernière demande repeint."""
    i = JS.index("function recyfMajTaux()")
    corps = JS[i:JS.index("\n}", i)]
    assert "var demande = ++RECYF_DEMANDE;" in corps
    assert re.search(r"\.then\(function \(j\) \{\s*if \(demande !== RECYF_DEMANDE\) return;",
                     corps), "une réponse ancienne repeint encore le taux"
