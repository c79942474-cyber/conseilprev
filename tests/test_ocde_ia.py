# -*- coding: utf-8 -*-
"""LA DILIGENCE OCDE — CE QUE LE MODULE DOIT TENIR, ET CE QU'IL DOIT REFUSER.

CE QUI A ÉTÉ DEMANDÉ : « vas-y pour l'OCDE » — intégrer le guide OCDE sur le
devoir de diligence pour une IA responsable comme quatorzième référentiel de
Sentinel, avec ses quatre écrans.

CE QUE CES RÈGLES MESURENT, ET QUI NE SE DEVINE PAS À LA LECTURE :

  1. LA LICENCE. C'est la première fois qu'une source de ce dépôt autorise la
     reproduction. CC BY 4.0 l'autorise à TROIS conditions, et deux d'entre
     elles sont des phrases à porter MOT POUR MOT. Une règle les relit dans
     le référentiel servi, et une autre vérifie que l'écran les peint : les
     tronquer ferait sortir le module des conditions de la licence. C'est la
     seule règle de ce fichier qui soit juridique.

  2. LE PLAFOND PAR IMPLICATION, ET SON ASYMÉTRIE. « Causer » rend la
     réparation non négociable, « être lié » ne la rend pas. Deux
     déclarations identiques au questionnaire doivent donc rendre DEUX taux
     différents selon l'implication — et c'est le seul endroit de Sentinel où
     la qualification change le plafond de TOUTES les parts.

  3. UNE SEULE ARITHMÉTIQUE. `conformite` recompose le taux d'une norme à
     partir des parts que son moteur lui rend. Un plafond posé sur le seul
     total ne lui parviendrait pas, et l'indice afficherait un chiffre plus
     haut que l'écran. La règle compare les deux nombres.

  4. CE QUE LE TAUX NE S'APPELLE PAS. Le document déclare ses exemples non
     exhaustifs ; le mot « conformité » est donc interdit dans le nom du
     taux, et une règle le vérifie sur la chaîne elle-même.

CE QUE CE FICHIER NE PEUT PAS MESURER, ET QUI LE MESURE :

  · LES QUATRE ÉCRANS SONT PEINTS depuis la route du référentiel ; le HTML ne
    porte qu'un « Chargement… ». Une règle qui lit le fichier voit le gabarit,
    jamais l'écran. C'est `outils/recette_ocde_ecrans.js` qui ouvre les quatre
    panneaux dans un vrai navigateur, lit les deux mentions et la citation À
    L'ÉCRAN, mesure la teinte du tiroir et vérifie qu'un groupe déclaré survit
    au rechargement.

  · LES PORTES DE LA GARDE DU MOTEUR. `ocde_ia` se contrôle à l'import et
    lève : un défaut qu'il attrape empêche de collecter CE fichier, donc
    aucune règle d'ici ne peut le nommer. Les quatre portes qui comptent sont
    dans `tests/test_ocde_ia_socle.py`, qui injecte le défaut dans une copie
    jetable du module et relit le message du refus.
"""
import io
import json
import os

import pytest

import conformite
import ocde_ia as M
import parcours_normes

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


HTML = _lire("sentinel.html")
JS = _lire("sentinel.page.js")
APP = _lire("app.py")

TOUT = {e["cle"]: "tenu" for e in M.EXEMPLES}
UNITE = {e["cle"]: e["unite"] for e in M.EXEMPLES}
PRIO_OK = [{"cle": "r1", "nom": "essai", "echelle": "eleve",
            "portee": "moyen", "irremediabilite": "faible",
            "probabilite": "moyen", "justification": "écrite"}]


def _sans_etape(n):
    return {k: v for k, v in TOUT.items()
            if M.UNITES_PAR_CLE[UNITE[k]]["etape"] != n}


def _d(groupes=("cycle_vie",), implication=None, reponses=None,
       priorisation=None):
    q = {"groupes": list(groupes)}
    if implication:
        q["implication"] = implication
    return {"qualification": q,
            "reponses": TOUT if reponses is None else reponses,
            "priorisation": PRIO_OK if priorisation is None else priorisation}


def _parts(d, plafonnees=True):
    sc = M.score(d)
    k = "etapes_plafonnees" if plafonnees else "etapes"
    return {e["cle"]: e["taux"] for e in sc[k]}


# ══════════════════════════════════════════════════════════════════════════
#  1. LA LICENCE — LA SEULE RÈGLE JURIDIQUE DE CE FICHIER
# ══════════════════════════════════════════════════════════════════════════

def test_les_DEUX_mentions_que_la_licence_impose_sont_au_referentiel_SERVI():
    """CC BY 4.0 AUTORISE À TROIS CONDITIONS, ET DEUX SONT DES PHRASES. La
    traduction doit porter sa mention, l'adaptation la sienne — et ce module
    fait les deux : il traduit les intitulés des étapes, et il adapte le cadre
    en questionnaire. Les tronquer ferait sortir le module de la licence."""
    r = M.referentiel()
    assert ("only the text of the original work should be considered valid"
            in r["mention_traduction"])
    assert ("This is an adaptation of an original work by the OECD"
            in r["mention_adaptation"])
    assert ("should not be reported as representing the official views"
            in r["mention_adaptation"])
    #  LA CITATION PORTE LE DOI : « citer l'œuvre » n'est pas « nommer
    #  l'OCDE ». Sans identifiant, la citation ne ramène à rien.
    assert "doi.org/10.1787/41671712-en" in r["citation"]
    assert "OECD (2026)" in r["citation"]


def test_l_ECRAN_peint_les_deux_mentions_et_la_citation():
    """UNE MENTION DANS LA CHARGE ET PAS À L'ÉCRAN NE VAUT RIEN. La condition
    de la licence porte sur ce que le lecteur voit, et c'est le script qui le
    peint : la règle cherche le bloc dans `sentinel.page.js`."""
    for marque in ("mention_traduction", "mention_adaptation", "citation"):
        assert ("R." + marque) in JS, (
            "l'écran ne peint plus %s : la licence l'impose" % marque)
    assert "_ocdeLicence" in JS
    #  ET IL LE PEINT SUR LES QUATRE ÉCRANS, pas seulement sur l'analyse.
    assert JS.count("_ocdeLicence(R)") >= 3, (
        "la licence ne voyage plus sur tous les écrans qui montrent du "
        "contenu de l'OCDE")


def test_la_licence_INTERDIT_le_logo_et_le_module_le_dit_ET_le_fait():
    """CE N'EST PAS UNE NOTE : la couleur du tiroir en découle. La licence
    interdit l'identité visuelle de l'OCDE — la teinte retenue n'est donc pas
    un bleu, et la règle le mesure sur la composante bleue elle-même."""
    cles = {i["cle"] for i in M.INTERDITS}
    assert {"logo", "adossement", "tiers"} <= cles
    coul = conformite.COULEURS["ocde"]
    r, v, b = (int(coul[i:i + 2], 16) for i in (1, 3, 5))
    assert b < r and b < 0x40, (
        "la teinte %s est bleutée : la licence interdit de reprendre "
        "l'identité visuelle de l'OCDE" % coul)
    assert coul in HTML, "la feuille de style ne porte pas la teinte déclarée"
    #  ET L'INTERDIT DIT CE QUI EN DÉCOULE, dans la charge servie : une
    #  interdiction qui ne nomme pas sa conséquence concrète est une note.
    logo = [i for i in M.referentiel()["interdits"] if i["cle"] == "logo"][0]
    assert "barre latérale" in logo["fait"] and "bleu de l'OCDE" in logo["fait"], (
        "l'interdit du logo ne dit plus ce que le module FAIT : %r"
        % logo["fait"])


def test_les_exemples_pratiques_sont_EN_ANGLAIS_et_c_est_une_decision():
    """LA LICENCE PERMETTRAIT DE LES TRADUIRE. Ils ne le sont pas, pour la
    raison qui vaut déjà pour les 212 actions du profil NIST : c'est le
    libellé qu'un auditeur cherchera. La règle mesure l'absence de français
    plutôt que de croire le commentaire."""
    import sys
    sys.path.insert(0, os.path.join(_RACINE, "outils"))
    import i18n_sentinel as outil
    francais = [e["cle"] for e in M.EXEMPLES if outil.est_francais(e["en"])]
    #  LE DÉTECTEUR LAISSE PASSER QUELQUES TOURNURES (« non », « des ») : on
    #  exige que la très grande majorité soit classée anglaise, pas la
    #  perfection d'une heuristique.
    assert len(francais) <= 4, (
        "%d exemples sur %d sont classés français : ils devraient être "
        "l'anglais du document — %s"
        % (len(francais), len(M.EXEMPLES), francais[:6]))
    assert all(len(e["en"].split()) >= 3 for e in M.EXEMPLES)


# ══════════════════════════════════════════════════════════════════════════
#  2. CE QUE LE MODULE REFUSE DE DIRE
# ══════════════════════════════════════════════════════════════════════════

def test_aucune_presomption_a_aucune_date_et_le_mot_conformite_est_INTERDIT():
    """DEUX REFUS, ET ILS NE SE LÈVENT PAS PAR LE TRAVAIL. L'instrument est
    volontaire — à la différence de prEN 18286, qui vaudra présomption le jour
    de sa citation. Et le document déclare ses exemples non exhaustifs : le
    taux ne peut pas s'appeler « conformité »."""
    assert M.SOURCE["presomption"] is False
    assert M.SOURCE["volontaire"] is True
    assert M.referentiel()["presomption"] is False
    assert M.referentiel()["exhaustif"] is False
    assert "conformité" not in M.NOM_DU_TAUX.lower()
    assert "exhaustive check list" in M.AVERTISSEMENT_EXEMPLES
    #  ET L'ÉVALUATION LE REDIT, quoi qu'on déclare.
    ev = M.evaluer(_d(implication="cause"))
    assert ev["presomption"] is False
    assert ev["nom_du_taux"] == M.NOM_DU_TAUX
    assert {"volontaire", "non_exhaustif", "pas_equivalence"} <= {
        r["cle"] for r in ev["reserves"]}


def test_les_ponts_ne_valent_PAS_equivalence_et_le_document_le_dit():
    """L'AVERTISSEMENT EST DU DOCUMENT, PAS DU CABINET — et c'est ce qui lui
    donne son poids. La règle le relit mot pour mot dans la charge."""
    f = M.feuilles_calculees()
    assert "not an equivalency framework" in f["avertissement"]
    assert "not an equivalency framework" in M.AVERTISSEMENT_FEUILLES
    #  ET IL PART AVEC LE RÉFÉRENTIEL : l'écran le lit là, pas dans le
    #  module. Le laisser en constante seule serait le garder pour nous.
    assert "not an equivalency framework" in M.referentiel()["avertissement_feuilles"]
    assert "exhaustive check list" in M.referentiel()["avertissement_exemples"]
    #  LE CHIFFRE HONNÊTE VOYAGE AVEC : trois cadres mesurés sur vingt.
    assert len(f["cadres_mesures"]) == 3
    assert len(f["cadres_non_mesures"]) == 17
    assert "en mesure 3" in f["dit"] or "mesure 3" in f["dit"]


def test_ce_que_le_document_s_exclut_LUI_MEME_est_declare():
    """DÉCLARÉ PLUTÔT QUE TU, ET DANS LA CHARGE SERVIE : la chaîne du
    matériel, le catalogue de risques et la table d'équivalence sont trois
    choses que le document écarte lui-même, et que l'écran doit pouvoir
    nommer. Une constante que la charge ne porte pas ne se lit nulle part."""
    cles = {h["cle"] for h in M.HORS_PERIMETRE}
    assert {"materiel", "catalogue_de_risques", "equivalence"} <= cles
    servi = {h["cle"] for h in M.referentiel()["hors_perimetre"]}
    assert cles == servi, (
        "le hors-périmètre ne part plus avec le référentiel : %s"
        % sorted(cles ^ servi))


# ══════════════════════════════════════════════════════════════════════════
#  3. LES COMPTES — RELUS DANS LE DOCUMENT, RECOMPTÉS ICI
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("quoi,attendu", [
    ("GROUPES", 3), ("ETAPES", 6), ("UNITES", 12), ("EXEMPLES", 115),
    ("CADRES", 20), ("IMPLICATIONS", 3), ("FACTEURS", 4),
])
def test_les_comptes_du_document(quoi, attendu):
    assert len(getattr(M, quoi)) == attendu


def test_les_six_feuilles_de_route_portent_QUATRE_VINGT_ONZE_lignes():
    assert len(M.FEUILLES) == 6
    assert sum(len(v) for v in M.FEUILLES.values()) == 91
    for num, lignes in M.FEUILLES.items():
        assert num in M.ETAPES_PAR_NUM
        for cle, disposition in lignes:
            assert cle in M.CADRES_PAR_CLE
            assert disposition.strip()


def test_les_cadres_MESURES_sont_des_normes_que_le_taux_connait():
    """UN PONT VERS UNE NORME QUE L'INDICE NE CONNAÎT PAS EST UNE PROMESSE EN
    L'AIR. La règle confronte les trois clés à `conformite.NORMES`."""
    connues = {n["cle"] for n in conformite.NORMES}
    for c in M.CADRES:
        if c["mesure"]:
            assert c["mesure"] in connues, (
                "le cadre %s dit être mesuré par %r, que le taux de "
                "conformité ne connaît pas" % (c["cle"], c["mesure"]))
    assert set(M.CADRES_MESURES) == {"ia_act", "iso42001", "nist"}


# ══════════════════════════════════════════════════════════════════════════
#  4. LES GROUPES — NI RIGIDES NI EXCLUSIFS, ET LE CALCUL LE SUIT
# ══════════════════════════════════════════════════════════════════════════

def test_deux_groupes_retiennent_PLUS_d_exemples_qu_un_seul():
    """LE DOCUMENT ÉCRIT QUE LES GROUPES NE SONT NI RIGIDES NI EXCLUSIFS, et
    les treize autres modules de Sentinel font choisir UN rôle. Celui-ci doit
    en accepter plusieurs — et le vérifier sur le nombre d'exemples retenus,
    pas sur la présence d'une liste."""
    un, _ = M.exemples_retenus(("utilisateur",))
    deux, _ = M.exemples_retenus(("utilisateur", "cycle_vie"))
    assert len(deux) > len(un) > 0
    trois, ecartes = M.exemples_retenus(("intrants", "cycle_vie",
                                        "utilisateur"))
    assert len(trois) == len(M.EXEMPLES) and not ecartes


def test_un_exemple_qu_AUCUN_groupe_ne_vise_SORT_du_calcul():
    """IL NE COMPTE PAS ZÉRO, et c'est tout l'écart. Le document l'adresse à
    quelqu'un d'autre : le compter contre ce client reviendrait à lui
    reprocher de ne pas être un fournisseur de calcul."""
    retenus, ecartes = M.exemples_retenus(("utilisateur",))
    assert ecartes, "le groupe 3 seul devrait écarter des exemples"
    assert len(retenus) + len(ecartes) == len(M.EXEMPLES)
    #  TOUT TENU SUR LES SEULS EXEMPLES RETENUS DONNE 100 %, pas moins : les
    #  écartés ne sont pas au dénominateur.
    rep = {e["cle"]: "tenu" for e in retenus}
    sc = M.score(_d(groupes=("utilisateur",), implication="lien_direct",
                    reponses=rep))
    assert sc["brut"] == 100, sc
    assert sc["exemples_ecartes"] == len(ecartes)


def test_sans_groupe_declare_RIEN_n_est_calcule_et_ce_n_est_pas_un_zero():
    champ = M.applicable({})
    assert champ["ok"] is None
    #  ET JAMAIS False : ce guide n'écarte personne, les PME comprises. Les
    #  autres modules ont un hors-champ ; celui-ci n'en a pas, et c'est une
    #  information.
    for g in (("intrants",), ("cycle_vie",), ("utilisateur",),
              ("intrants", "utilisateur")):
        assert M.applicable(_d(groupes=g))["ok"] is True
    ev = M.evaluer({})
    assert ev["tete"] == "non_qualifie"


# ══════════════════════════════════════════════════════════════════════════
#  5. L'IMPLICATION — LE PLAFOND, ET SON ASYMÉTRIE
# ══════════════════════════════════════════════════════════════════════════

def test_CAUSER_rend_la_reparation_non_negociable_et_plafonne_TOUTES_les_parts():
    """LE CŒUR DOCTRINAL DU MODULE. Un organisme qui cause un dommage et n'a
    aucun dispositif de réparation ne peut pas se prévaloir de ses politiques.
    C'est l'encadré 2.4 du document, pas une règle du cabinet."""
    d = _d(implication="cause", reponses=_sans_etape(6))
    sc = M.score(d)
    brutes, plafonnees = _parts(d, False), _parts(d)
    assert brutes["ancrer"] == 100 and brutes["reparer"] == 0
    assert all(v == 0 for v in plafonnees.values()), plafonnees
    assert sc["brut"] > 0 and sc["taux"] == 0 and sc["plafonne"]
    assert [v["cle"] for v in sc["verrous"]] == ["etape_non_negociable"]
    #  LES PARTS BRUTES RESTENT À CÔTÉ : le travail n'est pas effacé, il n'est
    #  pas revendicable.
    assert M.evaluer(d)["parts_brutes"]["ancrer"] == 100


def test_ETRE_LIE_ne_la_rend_PAS_non_negociable_et_c_est_l_asymetrie():
    """DEUX DÉCLARATIONS IDENTIQUES AU QUESTIONNAIRE, DEUX TAUX. Pour un lien
    direct, le document attend le levier sur la relation d'affaires, pas la
    réparation du dommage : l'étape 6 vide ne plafonne donc rien."""
    rep = _sans_etape(6)
    cause = M.score(_d(implication="cause", reponses=rep))
    lie = M.score(_d(implication="lien_direct", reponses=rep))
    assert cause["brut"] == lie["brut"], "le travail déclaré est le même"
    assert lie["taux"] > cause["taux"], (
        "le plafond ne distingue plus « causer » de « être lié » : "
        "%r vs %r" % (lie["taux"], cause["taux"]))
    assert not lie["verrous"] and cause["verrous"]
    #  ET LE LEVIER, LUI, EST BIEN EXIGÉ : l'étape 3 vide plafonne un lien
    #  direct comme elle plafonnerait une contribution.
    lie3 = M.score(_d(implication="lien_direct", reponses=_sans_etape(3)))
    assert lie3["taux"] < lie3["brut"], lie3


def test_SANS_implication_seules_DEUX_parts_sont_plafonnees():
    """LE VERROU EST CIBLÉ, et il doit l'être : l'encadré 2.4 fait dépendre de
    la réponse le niveau attendu de « faire cesser » et de « réparer ». Les
    quatre autres étapes se tiennent sans elle, et les plafonner les toutes
    punirait un travail que rien ne met en doute."""
    d = _d()
    brutes, plafonnees = _parts(d, False), _parts(d)
    attendu = int(round(100 * M.PLAFOND_SANS_IMPLICATION))
    assert plafonnees["traiter"] == attendu
    assert plafonnees["reparer"] == attendu
    for c in ("ancrer", "identifier", "suivre", "communiquer"):
        assert plafonnees[c] == brutes[c], c
    sc = M.score(d)
    assert [v["cle"] for v in sc["verrous"]] == ["implication_non_declaree"]
    assert M.evaluer(d)["tete"] == "implication_manquante"


def test_l_implication_N_EST_PAS_FIGEE_et_le_module_le_dit():
    assert "CONTRIBUTION" in M.IMPLICATION_NON_FIGEE
    assert M.evaluer(_d(implication="lien_direct"))["implication_non_figee"]
    #  L'ÉCRAN « PROCESSUS » LE LIT DANS LA CHARGE : c'est là qu'il avertit
    #  celui qui se range en « lien direct » et ne fait rien.
    assert "CONTRIBUTION" in M.referentiel()["implication_non_figee"]
    for i in M.IMPLICATIONS:
        assert i["commande"], i["cle"]
        for c in i["commande"]:
            assert c in M.ETAPES_PAR_CLE


# ══════════════════════════════════════════════════════════════════════════
#  6. LA PRIORISATION — LA JUSTIFICATION QUI LA REND CRÉDIBLE
# ══════════════════════════════════════════════════════════════════════════

def test_une_cotation_SANS_justification_plafonne_la_seule_part_identifier():
    sans = [{"cle": "r1", "echelle": "eleve", "portee": "eleve",
             "irremediabilite": "eleve", "probabilite": "eleve"}]
    d = _d(implication="lien_direct", priorisation=sans)
    plafonnees, brutes = _parts(d), _parts(d, False)
    assert plafonnees["identifier"] == int(round(
        100 * M.PLAFOND_PRIORISATION_SANS_JUSTIFICATION))
    for c in ("ancrer", "traiter", "suivre", "communiquer", "reparer"):
        assert plafonnees[c] == brutes[c], c
    assert "priorisation_sans_justification" in [
        v["cle"] for v in M.score(d)["verrous"]]


def test_une_ligne_INCOMPLETE_ne_rend_PAS_de_saillance_et_ne_plafonne_pas():
    """TROIS FACTEURS SUR QUATRE NE FONT PAS UNE PRIORISATION : ils font une
    opinion partiellement chiffrée. L'afficher comme un classement tromperait
    sur ce qui a été fait — mais ce n'est pas une faute, c'est un travail en
    cours, et cela ne plafonne donc rien."""
    pr = M.priorisation({"priorisation": [
        {"cle": "r1", "echelle": "eleve", "portee": "moyen"}]})
    assert pr["lignes"][0]["saillance"] is None
    assert pr["lignes"][0]["gravite"] is None
    assert pr["incompletes"] == ["r1"] and not pr["sans_justification"]
    assert pr["credible"] is False and pr["renseignee"] is True
    d = _d(implication="lien_direct",
           priorisation=[{"cle": "r1", "echelle": "eleve", "portee": "moyen"}])
    assert not M.score(d)["verrous"]


def test_la_gravite_se_lit_sur_TROIS_facteurs_et_la_saillance_les_croise():
    pr = M.priorisation({"priorisation": [
        {"cle": "fort", "echelle": "faible", "portee": "faible",
         "irremediabilite": "eleve", "probabilite": "eleve",
         "justification": "x"},
        {"cle": "faible", "echelle": "faible", "portee": "faible",
         "irremediabilite": "faible", "probabilite": "faible",
         "justification": "x"}]})
    fort, faible = pr["lignes"]
    #  L'IRRÉMÉDIABILITÉ SEULE SUFFIT À FAIRE LA GRAVITÉ : c'est le maximum
    #  des trois, pas leur moyenne — une incidence irréparable sur peu de
    #  monde reste grave.
    assert fort["gravite"] == 3 and faible["gravite"] == 1
    assert fort["saillance"] == 9 and faible["saillance"] == 1
    assert fort["palier"] == "saillant" and faible["palier"] == "a_suivre"
    assert pr["saillants"] == ["fort"] and pr["credible"] is True


# ══════════════════════════════════════════════════════════════════════════
#  7. UNE SEULE ARITHMÉTIQUE — LE MOTEUR ET L'INDICE DISENT LE MÊME NOMBRE
# ══════════════════════════════════════════════════════════════════════════

def test_le_plafond_global_n_est_QUE_la_recomposition_des_parts():
    """LA RÈGLE QUI EMPÊCHE DEUX VÉRITÉS SUR LE MÊME NOMBRE. `conformite`
    recompose le taux à partir des parts : un plafond posé sur le seul total
    ne lui parviendrait jamais."""
    poids = {e["cle"]: e["poids"] for e in M.ETAPES}
    den = float(sum(poids.values()))
    for d in (_d(), _d(implication="cause", reponses=_sans_etape(6)),
              _d(implication="lien_direct"),
              _d(implication="cause",
                 priorisation=[{"cle": "r1", "echelle": "eleve",
                                "portee": "eleve",
                                "irremediabilite": "eleve",
                                "probabilite": "eleve"}])):
        sc = M.score(d)
        recompose = int(round(sum(
            poids[e["cle"]] * (e["taux"] or 0)
            for e in sc["etapes_plafonnees"]) / den))
        assert recompose == sc["plafond"], (recompose, sc["plafond"])


def test_les_POIDS_de_l_indice_sont_ceux_du_moteur():
    """LE DOUBLON EST ASSUMÉ, DONC IL EST SURVEILLÉ. Deux jeux de poids
    rendraient deux taux pour la même déclaration."""
    moteur = {e["cle"]: e["poids"] for e in M.ETAPES}
    indice = {c["cle"]: c["poids"] for c in conformite.COMPOSITIONS["ocde"]}
    assert indice == moteur, (indice, moteur)


def test_l_INDICE_rend_le_MEME_taux_que_le_moteur():
    for d in (_d(implication="cause", reponses=_sans_etape(6)),
              _d(implication="lien_direct"), _d()):
        etat = conformite.etat_des_lieux({"ocde": d})
        o = [n for n in etat["normes"] if n["cle"] == "ocde"][0]
        sc = M.score(d)
        assert o["brut"] == sc["taux"], (
            "l'indice recompose %r là où le moteur retient %r"
            % (o["brut"], sc["taux"]))
        assert o["taux"] == sc["taux"]


def test_la_QUATORZIEME_norme_est_annoncee_et_atteignable():
    assert conformite.NORMES_ANNONCEES == 14
    assert len(conformite.NORMES) == 14
    assert conformite.NORMES_PAR_CLE["ocde"]["nature"] == "cadre"
    assert conformite.ORDRE_BARRE[-1] == "ocde"
    assert "14 normes maîtrisées" in _lire("index.html")
    assert "goto=ocde-processus" in _lire("index.html")


# ══════════════════════════════════════════════════════════════════════════
#  8. LES QUATRE ÉCRANS, ET LE RAIL
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("page", ["processus", "questionnaire", "conformite",
                                  "analyse"])
def test_chaque_ecran_existe_avec_son_corps_et_son_onglet(page):
    assert ('id="p-ocde-%s"' % page) in HTML
    assert ('id="ocde-%s-body"' % page) in HTML
    assert ("go('ocde-%s'" % page) in HTML
    assert ("'ocde-%s':" % page) in JS, "PAGE_META ou le guide manque"


def test_les_quatre_panneaux_portent_la_couleur_du_referentiel():
    """LA COULEUR DIT « QUEL RÉFÉRENTIEL », et elle est celle du moteur — pas
    une teinte recopiée dans la feuille de style. Ici elle porte en plus une
    décision de licence : ce n'est pas le bleu de l'OCDE."""
    coul = conformite.COULEURS["ocde"].lstrip("#")
    rvb = " ".join(str(int(coul[i:i + 2], 16)) for i in (0, 2, 4))
    assert "{--ref:%s}" % rvb in HTML, (
        "les quatre pages du module ne portent pas %s (%s)"
        % (conformite.COULEURS["ocde"], rvb))
    assert '.sb-nav .sb-item[data-norme="ocde"]{--sb-ic:%s}' \
        % conformite.COULEURS["ocde"] in HTML


def test_la_declaration_de_l_ecran_est_RAMASSEE_une_seule_fois():
    """LE RAIL ET LE TAUX LISENT LA MÊME DÉCLARATION. Sans le collecteur, le
    rail et la carte ne voient rien de ce que l'écran a reçu ; avec deux
    collectes, ils finiraient par voir deux états."""
    assert JS.count("ocde: function () { return OCDE_DECL; },") == 1
    assert JS.count("var OCDE_CLE_STOCK = 'cp-sentinel-ocde-v1';") == 1


def test_les_quatre_ecrans_s_ouvrent_aussi_par_un_LIEN_PROFOND():
    """LE DÉFAUT A DÉJÀ ÉTÉ MESURÉ DEUX FOIS — sur prEN 18286 et sur le taux
    de conformité : `;ocdeInit()` ne vit que dans le `onclick` de la barre, et
    `go()` ne l'exécute pas. Sans ce crochet, la carte de l'accueil et le
    parcours guidé ouvrent un « Chargement… » qui ne finit jamais."""
    assert "id.indexOf('ocde') === 0" in JS
    assert "window.ocdeInit" in JS


def test_les_routes_repondent_et_portent_la_reserve():
    import app as A
    c = A.app.test_client()
    rep = c.get("/api/ocde/referentiel")
    assert rep.status_code == 200
    j = json.loads(rep.data.decode("utf-8"))
    assert j["ok"] and j["referentiel"]["presomption"] is False
    assert j["referentiel"]["mention_adaptation"]
    rep = c.post("/api/ocde/evaluer",
                 json={"declaration": _d(implication="cause")})
    assert rep.status_code == 200
    j = json.loads(rep.data.decode("utf-8"))
    assert j["ok"] and j["plan"]["total"] >= 0
    #  UNE CLÉ INCONNUE EST UNE FAUTE, pas un silence.
    rep = c.post("/api/ocde/evaluer",
                 json={"declaration": {"reponses": {"zzz": "tenu"}}})
    assert rep.status_code == 400


def test_la_route_du_referentiel_est_RELEVEE_par_l_inventaire_i18n():
    """SANS ELLE, LES QUATRE ÉCRANS DIRAIENT « RIEN À TRADUIRE » là où tout
    reste à traduire : les écrans sont peints depuis cette route."""
    import sys
    sys.path.insert(0, os.path.join(_RACINE, "outils"))
    import i18n_sentinel as outil
    assert "/api/ocde/referentiel" in outil.ROUTES_REFERENTIEL


def test_le_RAIL_connait_les_quatre_blocs_et_ne_dit_JAMAIS_sans_objet():
    """CE GUIDE N'ÉCARTE PERSONNE, et c'est une différence de fond avec les
    treize autres : toute entreprise de la chaîne de valeur de l'IA est
    attendue sur la diligence, les PME comprises. Le rail ne doit donc jamais
    rendre « sans objet »."""
    blocs = parcours_normes.BLOCS["ocde"]
    assert [b["cle"] for b in blocs] == ["processus", "questionnaire",
                                        "conformite", "analyse"]
    for d in ({}, _d(), _d(implication="cause"),
              _d(groupes=("utilisateur",), implication="lien_direct")):
        a = parcours_normes.avancement("ocde", d)
        for b in a["blocs"]:
            assert b["etat"] != "sans_objet", (b["cle"], d)
    #  ET IL RÉCLAME LA QUALIFICATION AVANT LE QUESTIONNAIRE.
    a = parcours_normes.avancement("ocde", {})
    proc = [b for b in a["blocs"] if b["cle"] == "processus"][0]
    assert proc["manque"], "le rail ne réclame plus les groupes"


def test_la_reserve_du_rail_dit_que_la_date_NE_CHANGERA_RIEN():
    r = parcours_normes.QUI_JUGE["ocde"]
    assert "volontaire" in r and "aucune date" in r
