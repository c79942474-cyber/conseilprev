# -*- coding: utf-8 -*-
"""prEN 18229-3 — LA SUPERVISION HUMAINE, ET LES DEUX NOMBRES QU'ELLE COMPARE.

CE QUI A DÉCLENCHÉ CE FICHIER. Une demande : « ajouter cette norme à votre
conformité réglementaire dans Sentinel en proposant un cadre d'analyse à cette
norme sous forme de questionnaire, d'analyse qui spécifie les exigences
relatives à la supervision humaine des systèmes d'IA, et de la gestion des
risques en donnant aussi une évaluation du score de conformité, l'attribution
des responsabilités dans le présent document destinée à refléter la distinction
entre les fournisseurs et déployeurs et les exigences ».

CE QUE CES RÈGLES MESURENT, ET POURQUOI CE N'EST PAS DU BRANCHEMENT. Un
douzième questionnaire qui rend un pourcentage est facile. Ce projet de norme
porte cinq pièges qui ressemblent tous à une bonne nouvelle, et chacun se
solde par un client rassuré à tort :

  · AFFICHER UNE PRÉSOMPTION QUI N'EXISTE PAS. Le document est à l'Enquête
    CEN. Sa référence n'est pas au Journal officiel : le tenir entièrement
    n'ouvre AUCUNE présomption de conformité à l'article 14. Un écran qui
    laisserait croire le contraire vendrait une couverture inexistante.

  · POSER LES QUESTIONS DU FOURNISSEUR À UN DÉPLOYEUR. Les exigences
    s'adressent au fournisseur ; ce qui dépend du déploiement lui est transmis
    par la notice d'utilisation. Trente questions d'un côté, six de l'autre :
    les mélanger fausse le chiffre dans les deux sens.

  · MOYENNER LES DEUX RÔLES. Un organisme qui conçoit ET exploite porte deux
    jeux distincts. Une moyenne cacherait le côté défaillant derrière l'autre.

  · DIRE « CONFORME » À UNE MESURE QUI N'ARRIVE PAS À TEMPS. Toute la partie
    calculable tient dans une comparaison : la LATENCE D'INTERVENTION déclarée
    (5.7.1) contre le DÉLAI DE RÉACTION déterminé (5.2.2). La norme ne donne
    aucun seuil ; elle exige que les deux soient déterminés et que la mesure
    choisie tienne. Un moteur qui rendrait un booléen effacerait la différence
    entre « ça ne tient pas » et « on ne sait pas encore ».

  · RECOPIER LE TEXTE. Le document est PROTÉGÉ PAR LE DROIT D'AUTEUR. Un
    module qui « enrichirait » ses questions du texte normatif serait une
    contrefaçon publiée sur une page servie à des clients. Deux règles ferment
    cette porte : l'une structurelle, l'autre MESURÉE contre une empreinte du
    document.

CE QUE CES RÈGLES NE PEUVENT PAS FAIRE. Dire qu'une supervision est efficace :
cela s'éprouve par des essais d'aptitude à l'utilisation que Sentinel ne
détient pas. Elles disent seulement ce qui, à coup sûr, l'en empêche.
"""
import hashlib
import io
import json
import os
import re
import unicodedata

import pytest

import conformite
import en18229_3 as EN
import parcours_normes

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


SENTINEL = _lire("sentinel.html")
PAGEJS = _lire("sentinel.page.js")
APP = _lire("app.py")


# ═══════════════════════════════════════════════════════════════════════════
#  1. LA PRÉSOMPTION QUI N'EXISTE PAS — CE QUI SE DIT AVANT TOUT CHIFFRE
# ═══════════════════════════════════════════════════════════════════════════

def test_la_source_declare_le_stade_ENQUETE_et_REFUSE_la_presomption():
    """LE SEUL POINT DU DOCUMENT QUI DIT CE QU'IL VAUT JURIDIQUEMENT.

    L'annexe ZA est informative et le projet est à l'Enquête CEN : la
    présomption de conformité à l'article 14 naîtra à la citation au Journal
    officiel, pas avant. Trois champs le portent, et aucun n'est décoratif —
    `presomption` commande la réserve, `certifiable` commande le verrou,
    `stade` commande ce que l'écran affiche.
    """
    assert EN.SOURCE["presomption"] is False
    assert EN.SOURCE["certifiable"] is False
    assert "Enquête" in EN.SOURCE["stade"], EN.SOURCE["stade"]
    dit = EN.SOURCE["presomption_dit"]
    assert "Journal officiel" in dit, dit
    assert "2024/1689" in dit, dit


def test_le_taux_du_referentiel_PORTE_sa_reserve_et_ne_se_certifie_PAS():
    """UN TAUX SANS SA RÉSERVE EST UNE PROMESSE. Le taux part vers l'écran du
    taux de conformité : il emporte avec lui `certifiable: False` et la phrase
    qui dit pourquoi — sinon le client lit « 100 % » et comprend « conforme »."""
    r = EN.evaluer({"fournisseur": {e["cle"]: True
                                    for e in EN.applicables("fournisseur")},
                    "scenarios": [{"nom": "Tri de dossiers", "delai": 2,
                                   "delai_unite": "h", "latence": 20,
                                   "latence_unite": "min",
                                   "categories": ["alerte"]}]})
    assert r["ok"] is True
    assert r["taux"] == 100, r["taux"]
    assert r["certifiable"] is False
    assert "Rien ne se certifie" in r["reserve"], r["reserve"]
    assert EN.SOURCE["presomption_dit"] in r["reserve"]


# ═══════════════════════════════════════════════════════════════════════════
#  2. LE DROIT D'AUTEUR — LA PORTE STRUCTURELLE, PUIS LA MESURE
# ═══════════════════════════════════════════════════════════════════════════

def test_la_licence_INTERDIT_la_reproduction_et_le_module_le_declare():
    """LA RÈGLE QUI PROTÈGE LE DÉPÔT AVANT TOUTE INSPECTION DE CONTENU."""
    assert EN.SOURCE["reproduction"] is False
    lic = EN.SOURCE["licence"].upper()
    assert "DROIT D'AUTEUR" in lic, lic[:80]
    assert "CEN" in EN.SOURCE["licence"]


def test_une_exigence_ne_porte_QUE_les_champs_declares():
    """UNE INSPECTION DE CONTENU SE CONTOURNE EN REFORMULANT TROIS MOTS ; une
    énumération de champs autorisés ne se contourne pas. Ajouter un champ
    `texte`, `exigence` ou `extrait` pour « enrichir » la restitution fait
    tomber cette règle AVANT que la contrefaçon n'atteigne une page servie.

    Les deux seuls champs qui citent le document sont `clause` — un numéro —
    et `titre` — un titre de paragraphe, ce qu'un index reproduit."""
    permis = {"cle", "clause", "titre", "role", "question", "pourquoi",
              "piege", "poids", "verrou", "si"}
    for ex in EN.EXIGENCES:
        trop = sorted(set(ex) - permis)
        assert not trop, "l'exigence %s porte %s" % (ex["cle"], trop)
        assert set(ex) == permis, "l'exigence %s manque %s" % (
            ex["cle"], sorted(permis - set(ex)))


#: L'EMPREINTE DU DOCUMENT, ET CE QU'ELLE N'EST PAS. Le fichier ne porte
#: AUCUN mot du texte normatif : il porte des empreintes SHA-256 tronquées
#: (32 bits) de chaque suite de huit mots. Une empreinte ne se remonte pas —
#: on ne peut rien lire du document avec ce fichier ; on peut seulement
#: demander « cette suite de huit mots y est-elle ? ». C'est exactement ce que
#: la règle demande, et rien d'autre. Produit une fois, par le script décrit
#: dans le journal du lot, à partir de prEN_18229-3_F.docx.
EMPREINTES = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "_empreintes_en18229_3.json")

#: LA SEULE SUITE ADMISE, ET POURQUOI. « citée au Journal officiel de l'Union
#: européenne au titre du Règlement (UE) 2024/1689 » est la FORMULE LÉGALE de
#: la citation des normes harmonisées — règlement (UE) n° 1025/2012, art. 10.
#: Elle figure dans l'annexe ZA de toute norme harmonisée parce que c'est la
#: formule du droit de l'Union, pas une expression du CEN. La dire autrement
#: dirait autre chose.
FORMULE_LEGALE = "journal officiel de l union europeenne"


def _mots(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.findall(r"[a-z0-9]+", s)


def _champs_rediges():
    """Tout ce que le module écrit en prose — sans les numéros ni les titres
    de paragraphes, qui sont cités comme un index."""
    out = []
    for ex in EN.EXIGENCES:
        for c in ("question", "pourquoi", "piege", "verrou"):
            if ex.get(c):
                out.append(("exigence:%s:%s" % (ex["cle"], c), ex[c]))
    for cle, _ou, quoi, _clause, _si in EN.DOCUMENTATION:
        out.append(("documentation:%s" % cle, quoi))
    for cle, v in EN.ETATS_SCENARIO.items():
        out.append(("etat:%s:dit" % cle, v["dit"]))
        out.append(("etat:%s:nom" % cle, v["nom"]))
    for c in EN.CATEGORIES:
        out.append(("categorie:%s" % c[0], c[3]))
    for f in EN.FONCTIONS:
        out.append(("fonction:%s" % f[0], f[4] if len(f) > 4 else ""))
    for cle, _nom, dit in EN.ETAPES_PLAN:
        out.append(("etape:%s" % cle, dit))
    for cle in ("presomption_dit", "licence"):
        out.append(("source:%s" % cle, EN.SOURCE[cle]))
    return out


def test_AUCUNE_suite_de_huit_mots_du_module_n_est_dans_le_texte_de_la_norme():
    """LA MESURE, PAS L'INTENTION. Chaque suite de huit mots de la prose du
    module est cherchée dans l'empreinte du document. Huit mots n'est pas un
    seuil arbitraire : c'est la longueur à partir de laquelle une coïncidence
    cesse d'être une coïncidence et devient une reprise.

    MESURÉ AVANT LA CORRECTION : 40 suites partagées. Après réécriture de
    treize formulations : 10. Après six de plus : 3, toutes dans la formule
    légale de la citation au Journal officiel, seule exemption déclarée.
    """
    assert os.path.isfile(EMPREINTES), "tests/_empreintes_en18229_3.json manque"
    emp = set(json.load(io.open(EMPREINTES, encoding="utf-8"))["empreintes"])
    assert len(emp) > 10000, len(emp)
    reprises = []
    for nom, txt in _champs_rediges():
        m = _mots(txt)
        for i in range(len(m) - 7):
            suite = " ".join(m[i:i + 8])
            if FORMULE_LEGALE in suite:
                continue
            if hashlib.sha256(suite.encode()).hexdigest()[:8] in emp:
                reprises.append("%s : « %s »" % (nom, suite))
    assert not reprises, ("%d suite(s) de huit mots reprises du texte "
                          "normatif :\n  %s"
                          % (len(reprises), "\n  ".join(reprises[:10])))


def test_l_exemption_de_la_formule_legale_SERT_vraiment():
    """UNE EXEMPTION QUI NE SERT PLUS EST UNE EXEMPTION QUI DORT, et une
    exemption qui dort s'élargit un jour sans que personne s'en aperçoive.
    Celle-ci couvre trois suites, dans un seul champ : on le vérifie."""
    emp = set(json.load(io.open(EMPREINTES, encoding="utf-8"))["empreintes"])
    couvertes = []
    for nom, txt in _champs_rediges():
        m = _mots(txt)
        for i in range(len(m) - 7):
            suite = " ".join(m[i:i + 8])
            if FORMULE_LEGALE not in suite:
                continue
            if hashlib.sha256(suite.encode()).hexdigest()[:8] in emp:
                couvertes.append(nom)
    assert couvertes, ("l'exemption de la formule légale ne couvre plus rien : "
                       "retirez-la plutôt que de la laisser ouverte")
    assert set(couvertes) == {"source:presomption_dit"}, sorted(set(couvertes))


# ═══════════════════════════════════════════════════════════════════════════
#  3. LES DEUX NOMBRES — LA SEULE PARTIE CALCULABLE DE LA NORME
# ═══════════════════════════════════════════════════════════════════════════

def test_les_unites_se_ramenent_en_millisecondes_et_une_case_VIDE_n_est_PAS_zero():
    """UN DÉLAI NON RENSEIGNÉ ET UN DÉLAI NUL NE DISENT PAS LA MÊME CHOSE. Si
    la chaîne vide valait zéro, un scénario sans délai deviendrait « aucune
    latence ne tient », et le moteur conseillerait sur une donnée absente."""
    assert EN.en_ms(2, "h") == 7200000
    assert EN.en_ms("1,5", "min") == 90000
    assert EN.en_ms(250, "ms") == 250
    assert EN.en_ms("", "h") is None
    assert EN.en_ms(None, "h") is None
    assert EN.en_ms(3, "semaine") is None, "une unité inconnue n'est pas un délai"
    assert EN.en_ms(-1, "h") is None, "une durée négative n'est pas une durée"
    assert EN.en_ms(0, "s") == 0, "zéro seconde EST une durée, et c'est le cas dur"


def test_une_duree_se_lit_avec_LA_VIRGULE_decimale_francaise():
    """« 1.7 heure » dans un rapport remis à un comité se lit comme une
    coquille, et c'est le cabinet qui la porte."""
    assert EN.duree_lisible(6120000) == "1,7 heure", EN.duree_lisible(6120000)
    assert EN.duree_lisible(7200000) == "2 heures"
    assert EN.duree_lisible(900) == "900 millisecondes"
    assert EN.duree_lisible(None) == "—"
    assert "." not in EN.duree_lisible(5400000), EN.duree_lisible(5400000)


@pytest.mark.parametrize("d,attendu", [
    ({}, "sans_delai"),
    ({"delai": 2, "delai_unite": "h"}, "sans_mesure"),
    ({"delai": 2, "delai_unite": "h", "categories": ["alerte"]}, "sans_latence"),
    ({"delai": 2, "delai_unite": "h", "categories": ["alerte"],
      "latence": 20, "latence_unite": "min"}, "tient"),
    ({"delai": 200, "delai_unite": "ms", "categories": ["retrospective"],
      "latence": 900, "latence_unite": "ms"}, "impossible_non_consignee"),
    ({"delai": 200, "delai_unite": "ms", "categories": ["continue"],
      "latence": 900, "latence_unite": "ms",
      "impossibilite_consignee": True}, "impossible_consignee"),
])
def test_l_ORDRE_DES_GARDES_est_celui_de_la_norme(d, attendu):
    """ON NE JUGE PAS L'ADÉQUATION D'UNE MESURE AVANT DE SAVOIR À QUOI ELLE
    DOIT ÊTRE ADÉQUATE. Le délai d'abord (5.2.2), puis la sélection (5.2.3),
    puis la latence (5.7.1) : un moteur qui réclamerait la latence avant le
    délai ferait mesurer une latence contre rien."""
    s = EN.scenario(d)
    assert s["etat"] == attendu, (s["etat"], s.get("manque"))
    assert s["etat"] in EN.ETATS_SCENARIO


def test_le_conseil_d_un_scenario_qui_NE_TIENT_PAS_est_CHIFFRE_et_nomme_la_sortie():
    """UN CONSEIL GÉNÉRAL NE SE MET PAS EN ŒUVRE. Quand la revue
    rétrospective ne tient pas un délai de 200 ms, deux choses se disent : de
    combien ça dépasse, et quelles catégories PLUS RAPIDES restent."""
    s = EN.scenario({"nom": "Refus au guichet", "delai": 200,
                     "delai_unite": "ms", "categories": ["retrospective"],
                     "latence": 900, "latence_unite": "ms"})
    assert s["etat"] == "impossible_non_consignee"
    assert s["depassement_ms"] == 700
    assert s["depassement_dit"] == "700 millisecondes"
    m = " ".join(s["manque"])
    assert "700 millisecondes" in m, m
    assert "alerte" in m.lower() or "Intervention" in m, m
    assert "continue" in m.lower() or "Surveillance" in m, m


def test_quand_la_categorie_la_PLUS_RAPIDE_est_deja_prise_le_conseil_CHANGE():
    """LE 5.2.4 EST LA SORTIE, ET IL FAUT LE DIRE. Conseiller « relevez la
    catégorie » à qui tient déjà la surveillance continue serait un conseil
    impossible à suivre : c'est la consignation de l'impossibilité technique
    qui s'applique."""
    s = EN.scenario({"delai": 200, "delai_unite": "ms",
                     "categories": ["continue"], "latence": 900,
                     "latence_unite": "ms"})
    assert s["rang"] == 3, s["rang"]
    m = " ".join(s["manque"])
    assert "5.2.4" in m, m
    assert "Relevez la catégorie" not in m, m


def test_le_RANG_d_un_lot_de_categories_est_celui_de_la_plus_rapide():
    """TROIS CATÉGORIES, TROIS LATENCES ATTEIGNABLES. Un scénario couvert par
    plusieurs mesures a la réactivité de la meilleure, pas la moyenne."""
    assert EN.rang_categories([]) == 0
    assert EN.rang_categories(["retrospective"]) == 1
    assert EN.rang_categories(["alerte"]) == 2
    assert EN.rang_categories(["continue"]) == 3
    assert EN.rang_categories(["retrospective", "continue"]) == 3
    assert EN.rang_categories(["inventee"]) == 0, "une catégorie hors norme ne cote pas"


def test_les_trois_categories_portent_leur_paragraphe_et_leur_rang():
    """LE RANG N'EST PAS DÉCORATIF : c'est lui qui fait le conseil chiffré."""
    assert len(EN.CATEGORIES) == 3
    attendu = {"retrospective": ("5.3.2", 1), "alerte": ("5.3.3", 2),
               "continue": ("5.3.4", 3)}
    for cle, (clause, rang) in attendu.items():
        c = EN.CATEGORIES_PAR_CLE[cle]
        assert c["clause"] == clause, (cle, c["clause"])
        assert c["rang"] == rang, (cle, c["rang"])


def test_les_QUATRE_fonctions_d_intervention_se_separent_sortie_et_systeme():
    """TROIS AGISSENT SUR UNE SORTIE, UNE AGIT SUR LE SYSTÈME, et la règle du
    5.7.1 est « au moins une des trois PLUS la quatrième » — pas « une des
    quatre ». Confondre les deux laisserait un système qu'on ne peut pas
    arrêter passer pour équipé."""
    assert len(EN.FONCTIONS) == 4
    assert len(EN.FONCTIONS_SUR_SORTIE) == 3, EN.FONCTIONS_SUR_SORTIE
    assert EN.FONCTION_SYSTEME == "etat_sur"
    assert EN.FONCTION_SYSTEME not in EN.FONCTIONS_SUR_SORTIE
    q = EN.EXIGENCES_PAR_CLE["fonctions"]["question"]
    assert "PLUS" in q, q


# ═══════════════════════════════════════════════════════════════════════════
#  4. FOURNISSEUR ET DÉPLOYEUR — DEUX JEUX, DEUX SCORES, LE PLUS FAIBLE
# ═══════════════════════════════════════════════════════════════════════════

def test_le_deployeur_n_est_PAS_note_sur_la_conception():
    """LE CŒUR DE LA DEMANDE : « l'attribution des responsabilités dans le
    présent document destinée à refléter la distinction entre les fournisseurs
    et déployeurs ». Poser au déployeur les questions de conception du
    fournisseur produirait un score faux dans les deux sens — bas pour lui
    parce qu'il ne conçoit rien, et faussement rassurant pour le fournisseur
    parce que ses points seraient dilués."""
    f = {e["cle"] for e in EN.applicables("fournisseur")}
    d = {e["cle"] for e in EN.applicables("deployeur")}
    assert len(f) == 30, len(f)
    assert len(d) == 6, len(d)
    assert not (f & d), "une exigence est posée aux DEUX rôles : %s" % sorted(f & d)
    #  Les points de conception restent au fournisseur.
    for cle in ("retro_interface", "alerte_conception", "continue_ihm",
                "fonctions", "etat_sur", "scenarios", "delai"):
        assert cle in f, cle
        assert cle not in d, "%s est posée au déployeur" % cle


def test_le_PONT_entre_les_deux_roles_est_la_NOTICE_et_il_est_nomme():
    """CE QUI DÉPEND DU DÉPLOIEMENT NE DISPARAÎT PAS : il passe par la notice
    d'utilisation (prEN 18229-2). Les deux bouts du pont sont dans le
    questionnaire — le fournisseur l'écrit (5.4.1), le déployeur la lit (6.1)."""
    ecrite = EN.EXIGENCES_PAR_CLE["deploy_specification"]
    assert ecrite["clause"] == "5.4.1", ecrite["clause"]
    assert ecrite["role"] == ("fournisseur",), ecrite["role"]
    lue = EN.EXIGENCES_PAR_CLE["notice_recue"]
    assert lue["role"] == ("deployeur",), lue["role"]
    famille = " ".join("%s %s %s" % (n, t, p) for n, t, p, _s in EN.FAMILLE)
    assert "prEN 18229-2" in famille, famille


def test_le_taux_retenu_est_celui_du_ROLE_LE_PLUS_FAIBLE_et_il_est_nomme():
    """UNE MOYENNE CACHERAIT LE CÔTÉ DÉFAILLANT. Un organisme parfait comme
    fournisseur et nul comme déployeur n'est pas « à moitié conforme » : il
    est en défaut sur les obligations du déployeur, et c'est ce chiffre-là
    qu'un auditeur regardera."""
    tout = {e["cle"]: True for e in EN.applicables("fournisseur")}
    r = EN.evaluer({
        "fournisseur": tout,
        "deployeur": {e["cle"]: False for e in EN.applicables("deployeur")},
        "scenarios": [{"nom": "Tri", "delai": 2, "delai_unite": "h",
                       "latence": 20, "latence_unite": "min",
                       "categories": ["alerte"]}]})
    assert r["roles"]["fournisseur"]["taux"] == 100
    assert r["roles"]["deployeur"]["taux"] == 0
    assert r["taux"] == 0, r["taux"]
    assert r["role_commande"] == "deployeur"
    assert r["role_commande_nom"] == EN.ROLES["deployeur"]["nom"]


def test_un_role_NON_ENDOSSE_n_entre_NI_au_numerateur_NI_au_denominateur():
    """UN FOURNISSEUR PUR N'A PAS À ÊTRE NOTÉ SUR CE QU'IL NE FAIT PAS. Le
    compter à zéro au dénominateur le mettrait en défaut d'obligations qui ne
    sont pas les siennes."""
    r = EN.evaluer({"fournisseur": {e["cle"]: True
                                    for e in EN.applicables("fournisseur")},
                    "scenarios": [{"nom": "Tri", "delai": 2, "delai_unite": "h",
                                   "latence": 20, "latence_unite": "min",
                                   "categories": ["alerte"]}]})
    assert sorted(r["roles"]) == ["fournisseur"], sorted(r["roles"])
    assert r["taux"] == 100


def test_SANS_ROLE_declare_le_moteur_REFUSE_de_rendre_un_taux():
    """UN TAUX SUR RIEN EST PIRE QU'UN TIRET : il se retient. Le refus porte
    un motif que l'écran peut afficher tel quel."""
    r = EN.evaluer({})
    assert r["ok"] is False
    assert r["motif"] == "aucun_role_declare"
    assert "rôle" in r["dit"]
    assert "taux" not in r, r


# ═══════════════════════════════════════════════════════════════════════════
#  5. LE SCORE — COMPOSÉ, PUIS PLAFONNÉ, ET LE PLAFOND SE NOMME
# ═══════════════════════════════════════════════════════════════════════════

def test_une_question_SANS_REPONSE_n_est_pas_un_NON():
    """LA LEÇON DU MODULE DE MATURITÉ. Une réponse absente ne compte pas comme
    un échec : elle compte comme une question ouverte, et le score dit sur
    combien de questions il porte."""
    s = EN.score("fournisseur", {"scenarios": True})
    assert s["repondues"] == 1, s["repondues"]
    assert len(s["sans_reponse"]) == 29, len(s["sans_reponse"])
    assert s["complet"] is False
    assert EN._valeur(None) is None
    assert EN._valeur(False) == 0.0
    assert EN._valeur("partiel") == 0.5
    assert EN._valeur(True) == 1.0


def test_un_VERROU_ne_retire_PAS_de_points_il_POSE_un_plafond():
    """LA DIFFÉRENCE QUI COMPTE. Vingt-neuf points sur trente tenus, et le
    trentième est celui qui fait tenir tous les autres : une soustraction
    afficherait 95 %, un plafond affiche 25 % et NOMME la raison."""
    tout = {e["cle"]: True for e in EN.applicables("fournisseur")}
    tout["scenarios"] = False
    s = EN.score("fournisseur", tout)
    assert s["brut"] == 95, s["brut"]
    assert s["plafond"] == 25, s["plafond"]
    assert s["taux"] == 25, s["taux"]
    cles = [v["cle"] for v in s["verrous"]]
    assert cles == ["scenarios"], cles
    assert "25 %" in s["verrous"][0]["dit"]
    #  DEUX VERROUS À LA FOIS : C'EST LE PLUS BAS QUI COMMANDE. Avec un seul,
    #  le plus petit et le plus grand se confondent — mesuré : la mutation
    #  qui prenait le PLUS HAUT des plafonds survivait au cas à un verrou.
    deux = dict(tout)
    deux["delai"] = False
    d = EN.score("fournisseur", deux)
    plafonds = sorted(v["plafond"] for v in d["verrous"])
    assert plafonds == [25, 40], plafonds
    assert d["plafond"] == 25, d["plafond"]
    assert d["taux"] == 25, d["taux"]


def test_le_PLAFOND_est_lu_DANS_le_texte_du_verrou_et_pas_dans_un_second_champ():
    """DEUX CHAMPS DÉRIVENT. Un verrou qui annoncerait « 25 % » à l'écran en
    plafonnant à 40 % dans le calcul serait un mensonge invisible — le genre
    de défaut qu'une relecture ne voit pas. Le plafond se LIT dans la phrase
    que le client lit."""
    for ex in EN.EXIGENCES:
        if not ex["verrou"]:
            continue
        p = EN._plafond_du_texte(ex["verrou"])
        assert 0 < p < 100, (ex["cle"], p)
        assert "%d %%" % p in ex["verrou"], (ex["cle"], ex["verrou"])
    assert EN._plafond_du_texte("aucun chiffre ici") == 100


def test_les_TROIS_verrous_du_fournisseur_sont_les_trois_points_qui_COMMANDENT():
    """UN VERROU PARTOUT NE VERROUILLE RIEN. Trois seulement, et chacun est un
    point dont l'absence rend le reste incalculable : pas de scénario, rien
    n'est calibré ; pas de délai, aucun choix de mesure n'est justifiable ;
    pas de fonction d'intervention, la supervision ne peut rien empêcher."""
    v = [e["cle"] for e in EN.applicables("fournisseur") if e["verrou"]]
    assert v == ["scenarios", "delai", "fonctions"], v
    plafonds = [EN._plafond_du_texte(EN.EXIGENCES_PAR_CLE[c]["verrou"]) for c in v]
    assert plafonds == [25, 40, 35], plafonds
    d = [e["cle"] for e in EN.applicables("deployeur") if e["verrou"]]
    assert d == ["deploy_mise_en_oeuvre"], d


def test_LE_VERROU_QU_AUCUNE_CASE_NE_LEVE_vient_de_l_arithmetique():
    """LE SEUL VERROU DU MODULE QUI NE SE COCHE PAS. Un scénario dont la
    latence dépasse le délai SANS consignation au titre du 5.2.4 est le cas
    que la norme refuse nommément. Il ne se voit dans aucune réponse par oui
    ou non : il se CALCULE. Trente questions tenues et le score reste à 50 %,
    parce qu'une supervision qui n'arrive pas à temps n'est pas une mesure."""
    tout = {e["cle"]: True for e in EN.applicables("fournisseur")}
    casse = EN.scenario({"nom": "Refus au guichet", "delai": 200,
                         "delai_unite": "ms", "categories": ["continue"],
                         "latence": 900, "latence_unite": "ms"})
    s = EN.score("fournisseur", tout, scenarios=[casse])
    assert s["brut"] == 100, s["brut"]
    assert s["taux"] == 50, s["taux"]
    v = [x for x in s["verrous"]
         if x["cle"] == "scenario_sans_intervention_possible"]
    assert len(v) == 1, s["verrous"]
    assert "Refus au guichet" in v[0]["dit"]
    assert v[0]["plafond"] == 50
    #  LA CONSIGNATION DU 5.2.4 LÈVE LE VERROU — c'est l'aveu recevable.
    consigne = EN.scenario({"nom": "Refus au guichet", "delai": 200,
                            "delai_unite": "ms", "categories": ["continue"],
                            "latence": 900, "latence_unite": "ms",
                            "impossibilite_consignee": True})
    assert EN.score("fournisseur", tout, scenarios=[consigne])["taux"] == 100


def test_l_accord_du_verrou_arithmetique_SUIT_le_nombre_de_scenarios():
    """« 1 SCÉNARIO ONT UNE LATENCE » SE LIT DANS UN RAPPORT REMIS. Le
    singulier et le pluriel se calculent, comme le reste."""
    def dit(n):
        cs = [EN.scenario({"nom": "S%d" % i, "delai": 200, "delai_unite": "ms",
                           "categories": ["continue"], "latence": 900,
                           "latence_unite": "ms"}) for i in range(n)]
        s = EN.score("fournisseur", {}, scenarios=cs)
        return [v for v in s["verrous"]
                if v["cle"] == "scenario_sans_intervention_possible"][0]["dit"]
    un = dit(1)
    assert "1 scénario " in un, un
    assert " a une latence" in un, un
    assert " son délai" in un, un
    deux = dit(2)
    assert "2 scénarios " in deux, deux
    assert " ont une latence" in deux, deux
    assert " leur délai" in deux, deux


def test_le_verrou_ARITHMETIQUE_ne_frappe_QUE_le_fournisseur():
    """UN DÉPLOYEUR NE CHOISIT PAS LES CATÉGORIES DE MESURE : elles lui
    arrivent par la notice. Lui plafonner le score sur une latence qu'il n'a
    pas conçue le mettrait en défaut d'une obligation qui n'est pas la sienne."""
    casse = EN.scenario({"nom": "S", "delai": 200, "delai_unite": "ms",
                         "categories": ["continue"], "latence": 900,
                         "latence_unite": "ms"})
    d = EN.score("deployeur", {e["cle"]: True
                               for e in EN.applicables("deployeur")},
                 scenarios=[casse])
    assert d["taux"] == 100, d["taux"]
    assert not [v for v in d["verrous"]
                if v["cle"] == "scenario_sans_intervention_possible"]


# ═══════════════════════════════════════════════════════════════════════════
#  6. CE QUI EST APPLICABLE — L'IBD, ET LES NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════

def test_les_NEUF_exigences_du_5_point_8_ne_s_appliquent_QU_A_L_IBD():
    """COMPTER AU DÉNOMINATEUR CE QUI EST SANS OBJET FERAIT BAISSER LE SCORE
    DE QUI N'A RIEN À FAIRE. Neuf exigences ne concernent que
    l'identification biométrique à distance — l'article 14(5)."""
    sans = {e["cle"] for e in EN.applicables("fournisseur", rbi=False)}
    avec = {e["cle"] for e in EN.applicables("fournisseur", rbi=True)}
    ajout = avec - sans
    assert len(ajout) == 8, sorted(ajout)
    assert all(EN.EXIGENCES_PAR_CLE[c]["si"] == "rbi" for c in ajout)
    assert all(EN.EXIGENCES_PAR_CLE[c]["clause"].startswith("5.8") for c in ajout)
    #  La neuvième est la revue par deux personnes : 5.8.3, deux réviseurs.
    rbi = [e for e in EN.EXIGENCES if e["si"] == "rbi"]
    assert len(rbi) == 9, len(rbi)


def test_le_score_d_un_systeme_SANS_IBD_ne_porte_PAS_les_questions_de_l_IBD():
    """MESURÉ : le même jeu de réponses donne 100 % avec ou sans IBD, parce
    que le dénominateur suit l'applicabilité."""
    sans = EN.score("fournisseur",
                    {e["cle"]: True for e in EN.applicables("fournisseur")},
                    rbi=False)
    assert sans["taux"] == 100
    assert sans["applicables"] == 30, sans["applicables"]
    avec = EN.score("fournisseur",
                    {e["cle"]: True for e in EN.applicables("fournisseur")},
                    rbi=True)
    assert avec["applicables"] == 38, avec["applicables"]
    assert avec["taux"] < 100, "les huit questions de l'IBD ne pèsent pas"
    assert len(avec["sans_reponse"]) == 8


def test_l_exigence_du_5_point_4_point_3_n_existe_QUE_si_le_fournisseur_ne_notifie_PAS():
    """LA CONDITION LA MOINS ÉVIDENTE DU DOCUMENT. Si le fournisseur
    implémente les notifications en temps réel, il n'a pas à spécifier au
    déployeur de les implémenter : la question n'a pas d'objet."""
    avec = {e["cle"] for e in EN.applicables("fournisseur",
                                             notifications_fournisseur=True)}
    sans = {e["cle"] for e in EN.applicables("fournisseur",
                                             notifications_fournisseur=False)}
    ajout = sans - avec
    assert len(ajout) == 1, sorted(ajout)
    cle = ajout.pop()
    assert EN.EXIGENCES_PAR_CLE[cle]["si"] == "pas_de_notification_fournisseur"
    assert EN.EXIGENCES_PAR_CLE[cle]["clause"] == "5.4.3"


# ═══════════════════════════════════════════════════════════════════════════
#  7. LA DOCUMENTATION — DÉRIVÉE, JAMAIS UNE LISTE FIXE
# ═══════════════════════════════════════════════════════════════════════════

def test_la_documentation_exigee_SUIT_le_systeme_et_ne_liste_PAS_quatorze_lignes():
    """UNE LISTE FIXE FERAIT TRAVAILLER UN CLIENT SUR DES PIÈCES QU'IL N'A PAS
    À PRODUIRE. Quatorze éléments existent ; trois sont conditionnels. Un
    système ordinaire en doit neuf, un système biométrique qui laisse les
    notifications au déployeur en doit quatorze."""
    assert len(EN.DOCUMENTATION) == 14
    base = EN.documentation()
    assert len(base["notice"]) == 4, len(base["notice"])
    assert len(base["technique"]) == 5, len(base["technique"])
    plein = EN.documentation(rbi=True, notifications_fournisseur=False)
    assert len(plein["notice"]) == 7, len(plein["notice"])
    assert len(plein["technique"]) == 7, len(plein["technique"])
    #  CHAQUE LIGNE PORTE LE PARAGRAPHE QUI LA FONDE : sans lui, un client ne
    #  peut pas vérifier qu'on ne lui demande pas plus que la norme.
    for ou in ("notice", "technique"):
        for e in plein[ou]:
            assert re.match(r"^[0-9]+(\.[0-9]+)*( [a-z]\))?( et [0-9.]+)?$",
                            e["clause"]), (ou, e["cle"], e["clause"])


def test_les_trois_lignes_CONDITIONNELLES_sont_nommees_comme_telles():
    """UN CLIENT DOIT POUVOIR VOIR POURQUOI UNE LIGNE LUI EST DEMANDÉE."""
    plein = EN.documentation(rbi=True, notifications_fournisseur=False)
    cond = [e["cle"] for ou in ("notice", "technique")
            for e in plein[ou] if e["conditionnel"]]
    assert len(cond) == 5, cond
    assert set(cond) == {"spec_notifications", "seuils_confiance",
                         "competences_reviseurs", "justif_notifications",
                         "architecture_rbi"}


# ═══════════════════════════════════════════════════════════════════════════
#  8. L'ANNEXE ZA — UN ALINÉA N'EST PAS TENU À 80 %
# ═══════════════════════════════════════════════════════════════════════════

def test_un_alinea_de_l_article_14_est_COUVERT_ou_il_ne_l_est_PAS():
    """LA GRANULARITÉ EST CELLE DE L'ANNEXE ZA, PAS CELLE DU QUESTIONNAIRE.
    « 80 % de l'article 14 » n'a aucun sens : un alinéa est couvert quand TOUS
    les paragraphes que l'annexe lui associe sont tenus, ou il ne l'est pas."""
    tout = {e["cle"]: True for e in EN.EXIGENCES}
    c = {a["alinea"]: a for a in EN.couverture_article_14(tout, rbi=True)}
    assert len(c) == 10, sorted(c)
    assert all(a["etat"] == "couvert" for a in c.values()), \
        [(k, v["etat"]) for k, v in c.items() if v["etat"] != "couvert"]
    #  UN SEUL NON SUFFIT À DÉCOUVRIR L'ALINÉA.
    tout["biais_conception"] = False
    c2 = {a["alinea"]: a for a in EN.couverture_article_14(tout, rbi=True)}
    assert c2["14(4)(b)"]["etat"] == "non_couvert", c2["14(4)(b)"]
    assert c2["14(4)(c)"]["etat"] == "couvert"


def test_l_alinea_14_5_est_SANS_OBJET_hors_identification_biometrique():
    """LE DIRE « NON COUVERT » METTRAIT EN DÉFAUT QUI N'EST PAS CONCERNÉ."""
    a = {x["alinea"]: x for x in EN.couverture_article_14({}, rbi=False)}
    assert a["14(5)"]["etat"] == "sans_objet"
    assert "biométrique" in a["14(5)"]["dit"]
    b = {x["alinea"]: x for x in EN.couverture_article_14({}, rbi=True)}
    assert b["14(5)"]["etat"] == "sans_reponse", b["14(5)"]


def test_CHAQUE_paragraphe_cite_par_l_annexe_ZA_a_une_question_qui_le_porte():
    """LE DÉFAUT QUE CE CONTRÔLE A TROUVÉ, ET QUI A ÉTÉ CORRIGÉ. L'annexe
    renvoyait à 5.3.1, 5.3.2.3.1, 5.7.2, 5.7.3 et 5.7.4 sans qu'aucune
    question ne les couvre : l'alinéa correspondant se serait affiché
    « couvert » en ne mesurant rien. Le module refuse maintenant de démarrer
    dans cet état ; cette règle le dit à qui lira le fichier."""
    clauses = {e["clause"] for e in EN.EXIGENCES}
    orphelines = sorted({c for _a, _t, cl in EN.ANNEXE_ZA for c in cl}
                        - clauses)
    assert not orphelines, ("l'annexe ZA renvoie à des paragraphes que "
                            "personne ne mesure : %s" % orphelines)


def test_le_module_REFUSE_de_demarrer_sur_une_table_incoherente():
    """UNE FAUTE DE TABLE SE VOIT À L'IMPORT, PAS EN PRODUCTION. Le contrôle
    tourne au chargement et lève : un dépôt cassé ne se déploie pas."""
    assert not EN._FAUTES, EN._FAUTES
    src = _lire("en18229_3.py")
    assert 'raise RuntimeError("en18229_3 — table incohérente' in src
    assert "_FAUTES = _verifier()" in src


# ═══════════════════════════════════════════════════════════════════════════
#  9. LE PLAN — DÉRIVÉ DES ÉCARTS, DANS L'ORDRE OÙ IL SE TIENT
# ═══════════════════════════════════════════════════════════════════════════

def test_le_plan_met_les_VERROUS_EN_TETE_et_pas_dans_l_ordre_des_paragraphes():
    """ON NE CONÇOIT PAS UNE INTERFACE AVANT DE SAVOIR QUEL DÉLAI ELLE DOIT
    TENIR. Cinq étapes, et les verrous d'abord : rien d'autre ne fera monter
    le score tant qu'ils tiennent."""
    p = EN.plan("fournisseur", {})
    etapes = [e["cle"] for e in p["etapes"]]
    assert etapes[0] == "verrous", etapes
    assert etapes == ["verrous", "calibrer", "mesures", "verifier",
                      "documenter"], etapes
    assert p["total"] == 30, p["total"]
    #  UN POINT VERROUILLÉ N'EST PAS COMPTÉ DEUX FOIS.
    cles = [l["cle"] for e in p["etapes"] for l in e["lignes"]]
    assert len(cles) == len(set(cles)), [c for c in cles if cles.count(c) > 1]


def test_un_scenario_CASSE_entre_dans_le_plan_a_l_etape_ou_il_se_repare():
    """UN CONSEIL RANGÉ AILLEURS NE SE SUIT PAS. L'arithmétique du délai se
    répare en calibrant, pas en documentant."""
    casse = EN.scenario({"nom": "Refus au guichet", "delai": 200,
                         "delai_unite": "ms", "categories": ["retrospective"],
                         "latence": 900, "latence_unite": "ms"})
    p = EN.plan("fournisseur",
                {e["cle"]: True for e in EN.applicables("fournisseur")},
                scenarios=[casse])
    par = {e["cle"]: e for e in p["etapes"]}
    assert "calibrer" in par, sorted(par)
    quoi = " ".join(l["quoi"] for l in par["calibrer"]["lignes"])
    assert "700 millisecondes" in quoi, quoi
    titres = [l["titre"] for l in par["calibrer"]["lignes"]]
    assert any("Refus au guichet" in t for t in titres), titres


def test_CHAQUE_exigence_a_son_etape_DECLAREE_et_aucune_ne_tombe_par_defaut():
    """UN `.get(cle, "mesures")` QUI SERT VRAIMENT est un plan où des points
    de calibration se retrouvent rangés dans « concevoir les mesures ». La
    table est explicite, et cette règle le vérifie clé par clé."""
    manquantes = sorted(e["cle"] for e in EN.EXIGENCES
                        if e["cle"] not in EN._ETAPE_DE)
    assert not manquantes, manquantes
    etapes = {c for c, _n, _d in EN.ETAPES_PLAN}
    inconnues = {v for v in EN._ETAPE_DE.values()} - etapes
    assert not inconnues, sorted(inconnues)


# ═══════════════════════════════════════════════════════════════════════════
#  10. L'ANALYSE COMPLÈTE, ET LES DEUX ROUTES
# ═══════════════════════════════════════════════════════════════════════════

def test_l_analyse_rend_les_SIX_parties_et_sa_reserve():
    """CE QUE L'ÉCRAN A BESOIN DE RECEVOIR EN UN SEUL APPEL."""
    a = EN.analyse({"role": "fournisseur", "rbi": False,
                    "reponses": {"scenarios": True},
                    "scenarios": [{"nom": "Tri", "delai": 2,
                                   "delai_unite": "h", "latence": 20,
                                   "latence_unite": "min",
                                   "categories": ["alerte"]}]})
    for cle in ("source", "role", "scenarios", "exigences", "score",
                "documentation", "article_14", "plan", "reserve"):
        assert cle in a, cle
    assert a["scenarios_par_etat"] == {"tient": 1}, a["scenarios_par_etat"]
    assert len(a["exigences"]) == 30
    assert a["exigences"][0]["valeur"] in (None, 0.0, 0.5, 1.0)
    assert EN.SOURCE["presomption_dit"] in a["reserve"]


def test_un_role_INVENTE_retombe_sur_le_fournisseur_sans_lever():
    """UNE ROUTE PUBLIQUE REÇOIT N'IMPORTE QUOI. Le moteur ne lève pas sur un
    rôle inconnu : il retombe sur le jeu du fournisseur, et le dit."""
    a = EN.analyse({"role": "pirate"})
    assert a["role"]["cle"] == "fournisseur", a["role"]
    assert len(EN.applicables("pirate")) == 30


def test_les_DEUX_routes_existent_avec_leur_cadence_et_leur_refus():
    """UNE ROUTE QUI LÈVE REND UNE TRACE D'EXÉCUTION AU CLIENT. Les deux
    routes portent un limiteur et l'analyse porte un 500 nommé."""
    assert "/api/en18229/referentiel" in APP
    assert "/api/en18229/analyse" in APP
    i = APP.index("def api_en18229_referentiel")
    j = APP.index("def api_en18229_analyse")
    avant = APP[max(0, i - 400):i]
    assert "@rate_limit(" in avant, avant[-200:]
    avant2 = APP[max(0, j - 400):j]
    assert "@rate_limit(" in avant2, avant2[-200:]
    corps = APP[j:j + 1400]
    assert "analyse_impossible" in corps, corps[:400]
    assert "500" in corps


# ═══════════════════════════════════════════════════════════════════════════
#  11. LA DOUZIÈME NORME DANS LE TAUX DE CONFORMITÉ
# ═══════════════════════════════════════════════════════════════════════════

def test_la_norme_est_la_DOUZIEME_du_taux_de_conformite():
    """LE TITRE CODÉ EN DUR QUI DIT SEPT QUAND LA GRILLE EN MONTRE NEUF est un
    défaut déjà rencontré. Le compte annoncé est celui de la table."""
    assert conformite.NORMES_ANNONCEES == 12
    assert len(conformite.NORMES) == 12, len(conformite.NORMES)
    cles = [n["cle"] for n in conformite.NORMES]
    assert "en18229_3" in cles
    assert conformite.COULEURS["en18229_3"] == "#00323C"


#: LES NOMBRES ÉCRITS EN TOUTES LETTRES, ET CE QU'ILS COMPTENT.
NOMBRES_EN_LETTRES = {"sept": 7, "huit": 8, "neuf": 9, "dix": 10, "onze": 11,
                      "douze": 12, "treize": 13, "quatorze": 14}


def test_AUCUN_ecran_n_annonce_un_COMPTE_DE_NORMES_autre_que_celui_de_la_table():
    """LE DÉFAUT QUI REVIENT À CHAQUE NORME AJOUTÉE, ET QUI NE CASSE RIEN.

    « Le titre codé en dur dit sept, la grille en montre neuf » : le site a
    déjà porté ce mensonge une fois. La douzième norme l'a fait revenir en
    quatre endroits — le titre du tiroir du taux, son infobulle, le surtitre
    de l'écran et l'appel de la carte d'accueil disaient tous « les onze
    normes » pendant que la grille en peignait douze. Aucune erreur, aucun
    test rouge : juste un client qui compte.

    La règle relève TOUTE mention d'un compte de normes dans les pages
    servies et exige qu'il soit celui de la table. Elle ne dit pas comment
    l'écrire : elle dit qu'un seul nombre est vrai.
    """
    attendu = conformite.NORMES_ANNONCEES
    fautes = []
    for nom, src in (("sentinel.html", SENTINEL), ("index.html",
                     _lire("index.html")), ("index.page.js",
                     _lire("index.page.js")), ("sentinel.page.js", PAGEJS)):
        for m in re.finditer(r"(\d{1,2}|%s)\s+(normes?|standards?|Normen)"
                             % "|".join(NOMBRES_EN_LETTRES), src, re.I):
            brut = m.group(1).lower()
            #  « \u2014 normes » N'EST PAS « 14 NORMES » : dans un littéral
            #  JavaScript, les deux chiffres d'une échappée unicode précèdent
            #  l'espace. Mesuré : le tiret cadratin d'une phrase sur les
            #  normes harmonisées se lisait comme un compte.
            if re.search(r"\\u[0-9a-fA-F]{0,3}$", src[:m.start()]):
                continue
            n = NOMBRES_EN_LETTRES.get(brut, int(brut) if brut.isdigit() else None)
            #  ON NE COMPTE QUE CE QUI RESSEMBLE À UN COMPTE DE RÉFÉRENTIELS :
            #  « 2 normes de l'IA » parle d'un sous-ensemble et le dit.
            if n is None or n < 5 or n > 20:
                continue
            if n != attendu:
                fautes.append("%s : « %s »" % (nom, src[max(0, m.start() - 40):
                                                        m.end() + 10]
                                               .replace("\n", " ")))
    assert not fautes, ("la table annonce %d normes ; ces écrans en annoncent "
                        "un autre nombre :\n  %s"
                        % (attendu, "\n  ".join(fautes[:8])))


def test_les_DEUX_normes_de_l_IA_se_touchent_dans_la_barre():
    """UN CLIENT QUI OUVRE L'UNE TROUVE L'AUTRE À CÔTÉ : prEN 18229-3 sert
    l'article 14 de l'IA Act comme ISO/IEC 42001 sert son système de
    management. L'adjacence des couleurs est mesurée sur CET ordre."""
    o = list(conformite.ORDRE_BARRE)
    assert o.index("en18229_3") == o.index("iso42001") + 1, o


def test_le_taux_de_la_norme_passe_le_pipeline_de_conformite_et_se_PLAFONNE():
    """LE BRANCHEMENT DE BOUT EN BOUT, MESURÉ SUR LE VRAI PIPELINE : un
    scénario qui tient donne 100 %, le même qui ne tient pas plafonne — et
    c'est le verrou arithmétique, pas une réponse, qui l'a décidé."""
    tout = {e["cle"]: True for e in EN.applicables("fournisseur")}
    tient = {"fournisseur": tout,
             "scenarios": [{"nom": "Tri", "delai": 2, "delai_unite": "h",
                            "latence": 20, "latence_unite": "min",
                            "categories": ["alerte"]}]}
    r = conformite.taux_norme("en18229_3", EN.evaluer(tient), tient)
    assert r["taux"] == 100, r["taux"]
    assert r["plafond"] == 100, r["plafond"]
    assert [x["cle"] for x in r["reserves"]] == ["presomption"], r["reserves"]
    casse = dict(tient, scenarios=[
        {"nom": "Refus au guichet", "delai": 200, "delai_unite": "ms",
         "latence": 900, "latence_unite": "ms", "categories": ["continue"]}])
    r2 = conformite.taux_norme("en18229_3", EN.evaluer(casse), casse)
    #  LE TRAVAIL FAIT NE S'EFFACE PAS — le brut reste 100 —, mais le verrou
    #  interdit de s'en prévaloir : 43 %, et c'est un CALCUL qui l'a décidé,
    #  aucune réponse n'ayant changé entre les deux appels.
    assert r2["brut"] == 100, r2["brut"]
    assert r2["taux"] == 43, r2["taux"]
    assert r2["taux"] == r2["plafond"], (r2["taux"], r2["plafond"])
    assert [v["cle"] for v in r2["verrous"]] == \
        ["scenario_sans_intervention"], r2["verrous"]


def test_la_norme_porte_une_RESERVE_de_presomption_dans_le_taux():
    """LE TAUX DE CONFORMITÉ AFFICHE DOUZE NORMES ; UNE SEULE N'OUVRE AUCUNE
    PRÉSOMPTION. Sans réserve nommée, elle se lirait comme les onze autres."""
    res = {x["cle"]: x for x in conformite.RESERVES["en18229_3"]}
    assert "presomption" in res, sorted(res)
    assert "Journal officiel" in res["presomption"]["dit"]
    assert "aucune présomption" in res["presomption"]["dit"]
    assert conformite.VERROUS["en18229_3"], "la norme n'a plus de verrou"


def test_le_verrou_d_une_norme_NON_CERTIFIABLE_est_fonde_sur_l_ARITHMETIQUE():
    """LA DOCTRINE, ÉTENDUE PAR UNE MESURE. Un verrou sur une norme qu'on ne
    certifie pas serait d'ordinaire une réserve : rien ne se « perd » puisque
    rien ne s'obtient. L'exception est le calcul — une supervision qui
    n'arrive pas à temps n'est pas une mesure, et un taux de 100 % sur ce cas
    serait faux, certifiable ou non. La porte reste donc fermée sauf si le
    verrou déclare sur quel calcul il repose, et lequel."""
    v = conformite.VERROUS["en18229_3"]
    arith = [x for x in v if x.get("fonde_sur") == "arithmetique"]
    assert len(arith) == 1, v
    for x in arith:
        assert len(x.get("calcul") or "") >= 40, x.get("calcul")
        assert "latence" in x["calcul"].lower(), x["calcul"]


# ═══════════════════════════════════════════════════════════════════════════
#  12. LE RAIL ET LES QUATRE ÉCRANS
# ═══════════════════════════════════════════════════════════════════════════

def test_les_QUATRE_blocs_du_parcours_declarent_leurs_PREREQUIS():
    """LE VERT NE DIT PAS « OUVERT ». Un score se lit après le cadre, qui se
    remplit après le rôle : sans prérequis déclarés, le rail proposerait le
    score à qui n'a pas choisi son rôle."""
    blocs = parcours_normes.BLOCS["en18229_3"]
    assert [b["cle"] for b in blocs] == ["role", "scenarios", "cadre", "score"]
    assert [b["panneau"] for b in blocs] == [
        "en18229-role", "en18229-scenarios", "en18229-cadre", "en18229-score"]
    assert blocs[0]["prerequis"] == ()
    for b in blocs[1:]:
        assert b["prerequis"], b["cle"]
    assert blocs[3]["nature"] == "lecture", blocs[3]["nature"]
    assert "en18229_3" in parcours_normes.QUI_JUGE
    assert "en18229_3" in parcours_normes.EVALUATEURS


def test_le_rail_de_la_norme_se_remplit_bloc_par_bloc_sur_une_VRAIE_declaration():
    """MESURÉ SUR L'ÉVALUATEUR, pas sur sa signature. Rien de déclaré : le
    premier bloc manque. Le rôle posé : il ne manque plus. Tout posé : plus
    rien ne manque."""
    ev = parcours_normes.EVALUATEURS["en18229_3"]
    manque, sans_objet, _ctx = ev({})
    assert "role" in manque, manque
    #  UN RÔLE COCHÉ SANS UNE SEULE RÉPONSE N'EST PAS UN BLOC REMPLI : la
    #  déclaration du rôle et son questionnaire vont ensemble.
    m2, _s2, _c2 = ev({"fournisseur": {}, "rbi": False})
    assert "role" in m2, sorted(m2)
    m3, _s3, _c3 = ev({"fournisseur": {e["cle"]: True
                                       for e in EN.applicables("fournisseur")},
                       "rbi": False})
    assert "role" not in m3, sorted(m3)
    assert "scenarios" in m3, sorted(m3)
    tout = {"fournisseur": {e["cle"]: True
                            for e in EN.applicables("fournisseur")},
            "rbi": False,
            "scenarios": [{"nom": "Tri", "delai": 2, "delai_unite": "h",
                           "latence": 20, "latence_unite": "min",
                           "categories": ["alerte"]}]}
    m4, s4, _c4 = ev(tout)
    assert not m4, m4
    assert not s4, s4


@pytest.mark.parametrize("panneau", ["p-en18229-role", "p-en18229-scenarios",
                                     "p-en18229-cadre", "p-en18229-score"])
def test_les_quatre_ecrans_existent_et_sont_ATTEIGNABLES_depuis_la_barre(panneau):
    """UN PANNEAU SANS ENTRÉE DANS LA BARRE EST UN ÉCRAN QUE PERSONNE
    N'OUVRE."""
    assert 'id="%s"' % panneau in SENTINEL, panneau
    cible = panneau[2:]
    assert "go('%s'" % cible in SENTINEL, cible


def test_la_barre_porte_le_tiroir_de_la_norme_a_SA_couleur():
    """LA COULEUR EST DÉRIVÉE DE conformite.COULEURS, PAS RECOPIÉE À LA MAIN.
    Une seconde liste de teintes dériverait de la première."""
    coul = conformite.COULEURS["en18229_3"]
    assert 'data-grp="en18229"' in SENTINEL
    assert 'data-norme="en18229_3"' in SENTINEL
    #  DEUX SÉLECTEURS PORTENT LA TEINTE, ET LES DEUX COMPTENT : celui du
    #  TITRE du tiroir et celui de ses ENTRÉES. N'en vérifier qu'un laisse
    #  passer un tiroir dont le titre est pétrole et les onglets bleus —
    #  mesuré : la mutation qui ne changeait qu'un des deux survivait.
    for sel in ('.sb-nav .sb-item[data-norme="en18229_3"]',
                '.sb-nav [data-grp="en18229"]'):
        regle = sel + '{--sb-ic:' + coul + '}'
        assert regle in SENTINEL, regle


def test_les_quatre_ecrans_ne_RECOPIENT_aucune_question_et_vont_les_CHERCHER():
    """LE DROIT D'AUTEUR, CÔTÉ ÉCRAN. Les questions viennent du référentiel
    servi ; une seule recopiée dans le JavaScript ferait deux sources à
    maintenir, et la reprise deviendrait invisible."""
    for ex in EN.EXIGENCES:
        q = ex["question"][:60]
        assert q not in PAGEJS, "%s : question recopiée dans l'écran" % ex["cle"]
    assert "/api/en18229/referentiel" in PAGEJS
    assert "/api/en18229/analyse" in PAGEJS


def test_l_etat_d_un_alinea_se_dit_EN_FRANCAIS_et_pas_par_son_nom_interne():
    """LE DÉFAUT MESURÉ SUR L'ÉCRAN : `a.etat.replace(/_/g, ' ')` affichait
    « sans reponse » — sans accent, et sans rien expliquer — dans une colonne
    que le client lit."""
    assert "a.etat.replace(/_/g, ' ')" not in PAGEJS
    assert "ditEtat" in PAGEJS
    for mot in ("'Sans réponse'", "'Non couvert'", "'Sans objet'", "'Couvert'"):
        assert mot in PAGEJS, mot


def test_le_rail_ne_prend_PAS_une_carte_du_questionnaire_pour_SON_bandeau():
    """LE DÉFAUT QUE LA RECETTE NAVIGATEUR A TROUVÉ, ET QUI NE SE VOYAIT PAS.

    Le rail pose en tête de page un bandeau `.rail-bandeau` qui dit où en est
    le parcours, et il le RETROUVE à chaque peinture pour le mettre à jour.
    Le questionnaire de prEN 18229-3 dessine ses trente questions dans des
    cartes qui portent la même classe — c'est le même dessin, et c'est voulu.

    Le rail cherchait `.rail-bandeau` tout court : il tombait sur la PREMIÈRE
    carte du questionnaire, celle du 5.2.1, et écrivait son bandeau par-dessus.
    Mesuré dans le navigateur : l'en-tête annonçait « Fournisseur — 30
    exigences », et l'écran n'en affichait que vingt-neuf — la disparue étant
    précisément celle qui porte le verrou à 25 %. Aucune erreur de page, aucun
    test rouge : la question n'existait simplement plus pour le client.

    Le `role="status"` n'est posé QUE par le rail, à la création de son
    bandeau : c'est lui, et non la classe, qui l'identifie.
    """
    assert "pg.querySelector('.rail-bandeau[role=\"status\"]')" in PAGEJS, \
        "le rail cherche de nouveau n'importe quelle carte .rail-bandeau"
    #  ET AUCUN PEINTRE NE DOIT S'ATTRIBUER CE RÔLE : la porte se refermerait.
    for m in re.finditer(r"class=\\?[\"']rail-bandeau[^>]{0,120}", PAGEJS):
        assert "role=" not in m.group(0), m.group(0)[:120]


def test_les_boutons_de_reponse_portent_un_NOM_accessible_qui_dit_a_quoi():
    """QUARANTE-SIX QUESTIONS, TROIS BOUTONS CHACUNE. Lus l'un après l'autre,
    « oui, partiellement, non » cent trente-huit fois ne disent à quoi on
    répond que si le nom accessible porte le paragraphe."""
    i = PAGEJS.index("en18229Repondre(\\'")
    bloc = PAGEJS[max(0, i - 700):i + 200]
    assert "aria-label=" in bloc, bloc[-400:]
    assert "esc(e.clause)" in bloc, bloc[-400:]
    j = PAGEJS.index("en18229Rbi(")
    bloc2 = PAGEJS[max(0, j - 600):j + 200]
    assert "aria-label=" in bloc2, bloc2[-400:]
