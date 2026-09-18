# -*- coding: utf-8 -*-
"""NIS 2 — CE QUE LE MOTEUR DOIT REFUSER DE DIRE.

CE QUI A DÉCLENCHÉ CE FICHIER. Une demande : « créer l'analyse de mise en
conformité NIS2 ». Un tableau des dix mesures de l'article 21 aurait répondu à
la lettre de la demande et manqué tout ce qui coûte de l'argent dans cette
directive.

LES QUATRE FAITS QUE CES RÈGLES GARDENT, ET POURQUOI CHACUN

  1. LE « OU » DES SEUILS FINANCIERS. Une PME est une entreprise de moins de
     250 personnes dont le chiffre d'affaires n'excède PAS 50 M€ **OU** dont le
     bilan n'excède pas 43 M€. Lire ce « ou » comme un « et » surqualifie : une
     entreprise à 60 M€ de CA et 20 M€ de bilan devient « grande », donc entité
     ESSENTIELLE si elle relève de l'annexe I — audits réguliers, palier de
     sanction supérieur, et un dirigeant exposé à une interdiction d'exercer.
     Sur une case mal lue.

  2. L'ANNEXE II NE MÈNE JAMAIS À « ESSENTIELLE » PAR LA TAILLE. Un géant de la
     gestion des déchets, cinq mille personnes, neuf cents millions d'euros,
     reste une entité IMPORTANTE. Un moteur qui classerait par la taille seule
     lui vendrait un régime de supervision ex ante qu'il ne subit pas.

  3. LE MONTANT DE L'ARTICLE 34 EST UN PLANCHER, PAS UN PLAFOND. « Un maximum
     d'AU MOINS » : c'est le minimum que l'État doit rendre possible. Le CRA,
     lui, est un règlement — ses montants sont les montants. Confondre les deux
     régimes sous-estime l'exposition, et c'est le chiffre qu'un comité retient.

  4. LE DÉNOMINATEUR DE L'ARTICLE 20. Cinq lignes de gouvernance, dont QUATRE
     sont des obligations et une un encouragement. Compter les cinq rend 80 % à
     une entreprise qui a manqué la formation de ses dirigeants — le seul
     manquement des cinq qui expose personnellement quelqu'un.

CE QUE CES RÈGLES NE PEUVENT PAS FAIRE. Dire si une entité est réellement
qualifiée : c'est l'autorité nationale qui prononce, sur l'entité réelle. Et
elles ne peuvent rien dire de la loi de TRANSPOSITION, qui est ce qui oblige
vraiment — le module le déclare, et une règle ci-dessous garde cette réserve.
"""
import io
import os

import pytest

import nis2

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ═══════════════════════════════════════════════════════════════════════════
#  1. L'ARITHMÉTIQUE DES SEUILS — LE « OU » QUI SURQUALIFIE
# ═══════════════════════════════════════════════════════════════════════════

def test_le_OU_des_plafonds_financiers_n_est_pas_un_ET():
    """LA RÈGLE CENTRALE DE CE FICHIER, et elle tient en deux cas jumeaux.

    Même effectif (249), même chiffre d'affaires (60 M€, au-dessus du plafond).
    Seul le bilan change. Sous 43 M€, l'entreprise reste une MOYENNE entreprise
    parce qu'il suffit de tenir UN des deux plafonds financiers. Au-dessus des
    deux, elle les dépasse.
    """
    sous = nis2.taille(effectif=249, ca_eur=60000000, bilan_eur=20000000)
    au_dessus = nis2.taille(effectif=249, ca_eur=60000000, bilan_eur=50000000)
    assert sous["cle"] == "moyenne", (
        "60 M€ de chiffre d'affaires avec 20 M€ de bilan reste une MOYENNE "
        "entreprise : il suffit de tenir un des deux plafonds. Rendu : %s"
        % sous["cle"])
    assert au_dessus["cle"] == "grande", (
        "dépasser les DEUX plafonds financiers sort du statut de PME. "
        "Rendu : %s" % au_dessus["cle"])


def test_le_seuil_d_effectif_bascule_a_250_et_pas_ailleurs():
    """LE SEUIL EST STRICT : « moins de 250 personnes ». 249 est dedans, 250
    est dehors — et la différence vaut un régime de supervision."""
    assert nis2.taille(effectif=249, ca_eur=1000000)["cle"] == "moyenne"
    assert nis2.taille(effectif=250, ca_eur=1000000)["cle"] == "grande"


def test_une_taille_non_renseignee_ne_vaut_pas_une_petite_entreprise():
    """LE DÉFAUT LE PLUS COÛTEUX QU'UN MOTEUR PUISSE AVOIR ICI. Deviner
    « petite » par défaut sort du champ une entité qui y est, et lui fait
    classer le dossier. Le module refuse de prononcer et dit ce qui manque."""
    sans_effectif = nis2.taille(ca_eur=1000000)
    sans_finances = nis2.taille(effectif=12)
    assert sans_effectif["cle"] == "indetermine"
    assert sans_finances["cle"] == "indetermine"
    assert "effectif" in sans_effectif["manquants"]
    assert any("bilan" in m for m in sans_finances["manquants"])


def test_la_recommandation_2003_361_est_amputee_de_son_article_3_paragraphe_4():
    """LA PARTICULARITÉ DE NIS 2, et elle change qui est dans le champ.
    L'article 2, §1, second alinéa, écarte la règle qui prive du statut de PME
    une entreprise détenue à 25 % par un organisme public. Sous NIS 2, une
    entreprise publique se mesure comme les autres."""
    e = nis2.ECART_RECOMMANDATION
    # L'ARTICLE CITÉ EST CELUI QUI ÉCARTE (NIS 2), pas celui qui est écarté :
    # les confondre ferait citer la recommandation là où c'est la directive
    # qui parle.
    assert e["article"] == "art. 2, §1, second alinéa", (
        "l'article cité doit être celui de NIS 2 qui écarte la règle : %r"
        % e["article"])
    assert "3, §4" in e["quoi"], (
        "la règle ÉCARTÉE — art. 3, §4, de l'annexe à la recommandation — "
        "n'est plus nommée : %r" % e["quoi"])
    assert "25 %" in e["quoi"], "le seuil de détention publique a disparu"


# ═══════════════════════════════════════════════════════════════════════════
#  2. LA QUALIFICATION — CE QUE L'ANNEXE DÉCIDE, ET CE QU'ELLE NE DÉCIDE PAS
# ═══════════════════════════════════════════════════════════════════════════

def test_l_annexe_II_ne_mene_jamais_a_essentielle_par_la_taille():
    """CINQ MILLE PERSONNES ET NEUF CENTS MILLIONS D'EUROS, et le statut ne
    bouge pas. L'annexe décide quel statut est ATTEIGNABLE ; la taille décide
    seulement si on l'atteint."""
    geant = nis2.qualifier({"secteur": "dechets", "effectif": 5000,
                            "ca_eur": 900000000, "bilan_eur": 800000000})
    assert geant["statut"]["cle"] == "importante", (
        "un secteur d'annexe II ne devient pas essentiel en grandissant. "
        "Rendu : %s" % geant["statut"]["cle"])
    # LE TÉMOIN INVERSE, sans lequel la règle passerait sur un moteur qui
    # rendrait « importante » à tout le monde.
    annexe_i = nis2.qualifier({"secteur": "eau_potable", "effectif": 5000,
                               "ca_eur": 900000000, "bilan_eur": 800000000})
    assert annexe_i["statut"]["cle"] == "essentielle"


def test_la_meme_taille_dans_les_deux_annexes_donne_deux_statuts():
    """LE COUPLE QUI ISOLE LA VARIABLE. Effectif, chiffre d'affaires et bilan
    identiques ; seul le secteur change, et le statut avec."""
    commun = {"effectif": 400, "ca_eur": 120000000, "bilan_eur": 90000000}
    i = nis2.qualifier(dict(commun, secteur="energie"))["statut"]["cle"]
    ii = nis2.qualifier(dict(commun, secteur="chimie"))["statut"]["cle"]
    assert (i, ii) == ("essentielle", "importante"), (
        "annexe I et annexe II doivent diverger à taille égale : %s / %s"
        % (i, ii))


def test_les_telecoms_moyennes_entreprises_sont_essentielles_a_l_envers_des_autres():
    """L'ARTICLE 3, §1, c), SE LIT À L'ENVERS DE TOUT LE RESTE. Partout
    ailleurs, moyenne entreprise = importante. Pour les communications
    électroniques accessibles au public, moyenne suffit à être essentielle."""
    q = nis2.qualifier({"secteur": "infrastructure_numerique", "effectif": 100,
                        "ca_eur": 30000000,
                        "communications_electroniques": True})
    assert q["statut"]["cle"] == "essentielle"
    assert "3, §1, c)" in q["article"], (
        "le cas particulier doit citer l'article qui le porte, pas un autre : "
        "%s" % q["article"])
    # LE TÉMOIN : la même entreprise sans la case reste importante.
    sans = nis2.qualifier({"secteur": "infrastructure_numerique",
                           "effectif": 100, "ca_eur": 30000000})
    assert sans["statut"]["cle"] == "importante"


def test_une_petite_entreprise_entre_dans_le_champ_par_une_porte_hors_taille():
    """HUIT PORTES IGNORENT LA TAILLE, et deux mènent directement au statut
    d'entité essentielle. Un dirigeant de PME qui lit « moins de 50 salariés »
    et referme le dossier passe à côté de celles-là."""
    dehors = nis2.qualifier({"secteur": "sante", "effectif": 20,
                             "ca_eur": 3000000})
    dedans = nis2.qualifier({"secteur": "sante", "effectif": 20,
                             "ca_eur": 3000000, "seul_prestataire": True})
    assert dehors["statut"]["cle"] == "hors_champ"
    assert dedans["statut"]["cle"] == "importante", (
        "la porte de l'article 2, §2, b), doit faire entrer dans le champ une "
        "entité que sa taille en sortait")
    dns = nis2.qualifier({"secteur": "infrastructure_numerique", "effectif": 3,
                          "ca_eur": 400000, "dns_tld": True})
    assert dns["statut"]["cle"] == "essentielle", (
        "un fournisseur de services DNS est essentiel quelle que soit sa "
        "taille — article 3, §1, b)")


def test_la_qualification_nomme_toujours_l_article_qui_la_porte():
    """UN VERDICT SANS SON ARTICLE NE SE CONTESTE PAS. Une qualification qui
    commande des audits réguliers et l'exposition personnelle d'un dirigeant
    doit pouvoir s'attaquer sur son fondement."""
    for d in ({}, {"secteur": "energie", "effectif": 300, "ca_eur": 80000000},
              {"secteur": "dechets", "effectif": 900, "ca_eur": 200000000},
              {"secteur": "sante", "effectif": 5, "ca_eur": 400000}):
        q = nis2.qualifier(d)
        assert q["article"].startswith("art."), (
            "la qualification de %s ne cite aucun article : %r"
            % (d, q["article"]))
        assert q["motif"].strip(), "la qualification de %s ne dit pas pourquoi" % d


# ═══════════════════════════════════════════════════════════════════════════
#  3. LA BASCULE — ANNONCÉE À QUI NE L'A PAS FRANCHIE, ET À PERSONNE D'AUTRE
# ═══════════════════════════════════════════════════════════════════════════

def test_la_bascule_est_annoncee_a_l_entite_importante_de_l_annexe_I():
    """UN OPÉRATEUR D'EAU POTABLE À 240 PERSONNES n'est pas « conforme » : il
    est à dix embauches du régime d'audits réguliers. Le dire coûte une ligne ;
    le découvrir plus tard coûte un budget d'audit non provisionné."""
    q = nis2.qualifier({"secteur": "eau_potable", "effectif": 240,
                        "ca_eur": 40000000})
    assert q["bascule"] is not None
    assert q["bascule"]["vers"] == "essentielle"
    assert "250" in q["bascule"]["fait"]


def test_la_bascule_n_est_PAS_annoncee_a_qui_l_a_deja_franchie():
    """CE QUE CETTE RÈGLE A ATTRAPÉ. Le calcul de la bascule ne regardait que
    le secteur et la taille : un opérateur télécom moyenne entreprise, DÉJÀ
    essentiel par l'article 3, §1, c), s'entendait annoncer qu'il pourrait le
    devenir en grandissant. Faux, et il provisionne deux fois."""
    deja = nis2.qualifier({"secteur": "infrastructure_numerique",
                           "effectif": 100, "ca_eur": 30000000,
                           "communications_electroniques": True})
    assert deja["statut"]["cle"] == "essentielle"
    assert deja["bascule"] is None, (
        "une entité déjà essentielle ne bascule vers rien : %s"
        % deja["bascule"])


def test_l_annexe_II_ne_recoit_aucune_bascule():
    """PARCE QU'IL N'Y EN A PAS. Un secteur d'annexe II ne peut pas devenir
    essentiel en grandissant : lui annoncer une bascule serait un mensonge
    poli."""
    q = nis2.qualifier({"secteur": "dechets", "effectif": 100,
                        "ca_eur": 30000000})
    assert q["statut"]["cle"] == "importante"
    assert q["bascule"] is None


# ═══════════════════════════════════════════════════════════════════════════
#  4. LE RÉGIME DE SUPERVISION — LA DIFFÉRENCE QUI PORTE SUR UNE PERSONNE
# ═══════════════════════════════════════════════════════════════════════════

def test_seule_l_entite_essentielle_expose_son_dirigeant_a_une_interdiction():
    """C'EST LA CONSÉQUENCE LA PLUS LOURDE DE LA QUALIFICATION, et elle
    n'existe que d'un côté. L'article 32, §5, permet d'interdire temporairement
    au directeur général d'exercer ses fonctions. L'article 33 n'a pas
    d'équivalent, et une table qui donnerait l'escalade aux deux effacerait
    exactement ce qui sépare les deux statuts."""
    ex_ante = nis2.REGIMES["ex_ante"]
    ex_post = nis2.REGIMES["ex_post"]
    assert ex_ante["escalade"] is not None
    assert "32, §5" in ex_ante["escalade"]["article"]
    assert ex_post["escalade"] is None, (
        "l'article 33 ne prévoit aucune escalade sur la personne du dirigeant")


def test_le_declencheur_separe_l_ex_ante_de_l_ex_post():
    """CE QUI DISTINGUE VRAIMENT LES DEUX RÉGIMES n'est pas la liste des
    pouvoirs — elle se recoupe largement — mais le DÉCLENCHEUR. L'ex ante n'en
    a aucun ; l'ex post exige des éléments de manquement."""
    assert "Aucun" in nis2.REGIMES["ex_ante"]["declencheur"]
    assert "preuve" in nis2.REGIMES["ex_post"]["declencheur"].lower()


def test_l_evaluation_rattache_chaque_statut_a_son_regime():
    """LE BRANCHEMENT, MESURÉ SUR LA SORTIE et non sur la table : une entité
    essentielle doit recevoir l'article 32, une importante l'article 33."""
    ess = nis2.evaluer({"nom": "A", "secteur": "eau_potable", "effectif": 300,
                        "ca_eur": 80000000})
    imp = nis2.evaluer({"nom": "B", "secteur": "dechets", "effectif": 300,
                        "ca_eur": 80000000})
    assert ess["regime"]["article"] == "art. 32"
    assert imp["regime"]["article"] == "art. 33"
    assert imp["regime"]["escalade"] is None


# ═══════════════════════════════════════════════════════════════════════════
#  5. LA GOUVERNANCE — LE DÉNOMINATEUR QUI FLATTE
# ═══════════════════════════════════════════════════════════════════════════

def test_la_formation_du_personnel_n_entre_pas_au_denominateur_de_l_article_20():
    """LE CAS QUI FAIT LA DÉMONSTRATION. Une entreprise qui a formé tout son
    personnel et RIEN d'autre : sur cinq lignes elle affiche 20 % ; sur les
    quatre obligations elle affiche 0 %. C'est 0 % qui est vrai — elle n'a tenu
    aucune obligation, et surtout pas celle qui l'expose personnellement."""
    g = nis2._ecarts_gouvernance({"formation_personnel": "conforme"})
    assert g["obligatoires"] == 4, (
        "l'article 20 porte quatre obligations et un encouragement : %d"
        % g["obligatoires"])
    assert g["taux"] == 0, (
        "former le personnel ne tient aucune des quatre obligations — taux "
        "rendu : %d %%" % g["taux"])
    assert "formation_dirigeants" in g["manques"]


def test_la_formation_des_dirigeants_compte_quand_elle_est_tenue():
    """LE TÉMOIN INVERSE. Sans lui, la règle précédente passerait sur un
    moteur qui rendrait toujours 0 %."""
    g = nis2._ecarts_gouvernance({"formation_dirigeants": "conforme"})
    assert g["taux"] == 25, "une obligation sur quatre = 25 %%, rendu %d" % g["taux"]
    assert "formation_dirigeants" not in g["manques"]


def test_chaque_ligne_de_gouvernance_dit_quelle_preuve_est_attendue():
    """UNE OBLIGATION SANS PREUVE ATTENDUE EST UNE OBLIGATION QU'ON CROIT
    TENIR. « Les dirigeants suivent une formation » se coche facilement ; « des
    attestations nominatives et datées des dirigeants eux-mêmes » beaucoup
    moins."""
    for g in nis2.GOUVERNANCE:
        assert g.get("preuve", "").strip(), (
            "la ligne « %s » ne dit pas quelle preuve est attendue" % g["cle"])


# ═══════════════════════════════════════════════════════════════════════════
#  6. LE SIGNALEMENT — DEUX NOTIFICATIONS, ET UNE HORLOGE QUI SURPREND
# ═══════════════════════════════════════════════════════════════════════════

def test_l_horloge_demarre_a_la_connaissance_et_le_module_le_dit():
    """« APRÈS AVOIR EU CONNAISSANCE » — pas à la survenance, pas à la
    détection technique. La question cesse d'être « avons-nous détecté » pour
    devenir « qui a compris que c'était important, et quand »."""
    assert "CONNAISSANCE" in nis2.SIGNALEMENT["depart"].upper()
    assert "survenance" in nis2.SIGNALEMENT["depart"].lower()


def test_les_deux_premiers_delais_sont_24h_puis_72h():
    d = [e["delai_h"] for e in nis2.SIGNALEMENT["etapes"]]
    assert d[:2] == [24, 72], "les délais de l'article 23, §4 : %s" % d


def test_le_prestataire_de_confiance_notifie_en_24h_et_pas_72():
    """LA DÉROGATION QUI CONFOND LES DEUX PREMIÈRES ÉCHÉANCES. Pour un
    prestataire de services de confiance, alerte précoce et notification
    tombent le même jour."""
    assert nis2.SIGNALEMENT["derogation_confiance"]["delai_h"] == 24


def test_l_article_23_porte_une_SECONDE_notification_aux_destinataires():
    """CELLE QUE TOUT LE MONDE OUBLIE, et elle est au même paragraphe. Le
    paragraphe 1 impose aussi de notifier aux DESTINATAIRES DES SERVICES les
    incidents susceptibles de nuire à la fourniture ; le paragraphe 2 ajoute,
    en cas de cybermenace, les mesures qu'ils peuvent appliquer eux-mêmes.
    Une chaîne qui s'arrête au CSIRT a l'air complète et laisse une obligation
    dehors."""
    d = nis2.SIGNALEMENT["destinataires"]
    assert "23, §1" in d["incident"]["article"]
    assert "23, §2" in d["menace"]["article"]
    assert "CSIRT" in d["dit"], (
        "le module doit dire que ces notifications ne se substituent pas à "
        "celle au CSIRT")


def test_notifier_n_accroit_pas_la_responsabilite_et_le_module_le_porte():
    """LA CLAUSE QUI DÉSAMORCE LE PIRE CONSEIL POSSIBLE. « Le simple fait de
    notifier un incident n'accroît pas la responsabilité de l'entité qui est à
    l'origine de la notification » — sans elle, « ne notifions pas, ça nous
    incriminerait » reste une position défendable en réunion."""
    assert "23, §1" in nis2.SIGNALEMENT["sans_aveu"]["article"]
    assert "responsabilité" in nis2.SIGNALEMENT["sans_aveu"]["quoi"]


# ═══════════════════════════════════════════════════════════════════════════
#  7. LES SANCTIONS — UN PLANCHER, ET LE MOT QUI LE DIT
# ═══════════════════════════════════════════════════════════════════════════

def test_les_montants_sont_nommes_PLANCHERS_et_jamais_plafonds():
    """LE MOT EST LE FOND. « Un maximum d'AU MOINS » : c'est le minimum que
    l'État doit rendre possible, pas le maximum que l'entreprise risque. Un
    champ nommé `plafond_eur` ferait présenter un minimum comme un maximum
    dans toutes les restitutions, sans qu'aucune ligne de calcul soit fausse."""
    for cle, s in nis2.SANCTIONS.items():
        assert "plancher_eur" in s, (
            "le palier « %s » ne nomme plus son montant comme un plancher" % cle)
        assert "plafond_eur" not in s, (
            "le palier « %s » nomme un plafond là où le texte dit « au "
            "moins »" % cle)


def test_la_difference_avec_le_CRA_est_ecrite_dans_la_reponse():
    """CE QUI SÉPARE UNE DIRECTIVE D'UN RÈGLEMENT, dit à l'endroit où le
    chiffre est lu. Séparée, la réserve finit sous le pli et le nombre part
    seul en comité."""
    e = nis2.exposition(100000000, "essentielle")
    assert "CRA" in e["nature"]["difference_cra"]
    assert "directe" in e["nature"]["difference_cra"]
    assert nis2.SOURCE["nature"] == "directive"
    assert "transposition" in nis2.SOURCE["reserve"].lower()


def test_les_deux_paliers_pivotent_au_meme_chiffre_d_affaires():
    """UN FAIT QU'AUCUNE LECTURE DE L'ARTICLE 34 NE DONNE. 10 M€ / 2 % = 500 M€
    et 7 M€ / 1,4 % = 500 M€ : le législateur a tenu le rapport 10/7 = 2/1,4.
    En dessous, les planchers forfaitaires commandent ; au-dessus, les
    pourcentages — et l'écart entre les deux statuts reste de 43 % partout."""
    a = nis2.seuil_de_bascule("essentielle")
    b = nis2.seuil_de_bascule("importante")
    assert abs(a - b) < 1.0, "les deux pivots divergent : %s / %s" % (a, b)
    assert round(a) == 500000000
    ecart_bas = (nis2.SANCTIONS["essentielle"]["plancher_eur"]
                 / float(nis2.SANCTIONS["importante"]["plancher_eur"]))
    ecart_haut = (nis2.SANCTIONS["essentielle"]["part_ca"]
                  / nis2.SANCTIONS["importante"]["part_ca"])
    assert abs(ecart_bas - ecart_haut) < 0.001, (
        "l'écart entre les deux paliers doit être le même sur les deux bornes "
        ": %.4f / %.4f" % (ecart_bas, ecart_haut))


def test_sous_le_pivot_c_est_le_plancher_qui_commande_au_dessus_le_pourcentage():
    """LA BORNE RETENUE EST NOMMÉE, et pas seulement calculée : une PME qui
    lit « 2 % » se rassure à tort, et une grande entreprise qui lit « 10 M€ »
    se rassure tout autant."""
    petite = nis2.exposition(100000000, "essentielle")["lignes"][0]
    grande = nis2.exposition(900000000, "essentielle")["lignes"][0]
    assert petite["borne_retenue"] == "plancher"
    assert petite["retenu_eur"] == 10000000
    assert grande["borne_retenue"] == "part_ca"
    assert grande["retenu_eur"] == 18000000


def test_l_assiette_est_celle_du_GROUPE_et_la_reponse_le_dit():
    """LE PLUS GROS FACTEUR D'ERREUR DE CE CALCUL. Lire le chiffre d'affaires
    de la seule filiale concernée divise l'exposition par l'écart entre la
    filiale et le groupe."""
    e = nis2.exposition(50000000)
    assert "groupe" in e["assiette"].lower() or "appartient" in e["assiette"]
    assert "seule" in e["assiette"].lower()


# ═══════════════════════════════════════════════════════════════════════════
#  8. L'ENREGISTREMENT — L'OBLIGATION DONT L'ÉCHÉANCE EST DERRIÈRE NOUS
# ═══════════════════════════════════════════════════════════════════════════

def test_l_entite_non_enregistree_est_EN_RETARD_et_pas_en_projet():
    """TOUTES LES AUTRES LIGNES DU MODULE DÉCRIVENT UN CHANTIER. Celle-ci
    décrit un retard déjà constitué : le 17 avril 2025 est passé. C'est la
    seule ligne qui se règle en une semaine, et la seule qu'on ne voit pas
    venir."""
    r = nis2.evaluer({"nom": "X", "secteur": "eau_potable", "effectif": 300,
                      "ca_eur": 80000000}, aujourdhui="2026-09-18")
    assert r["enregistrement"]["en_retard"] is True
    faite = nis2.evaluer({"nom": "X", "secteur": "eau_potable",
                          "effectif": 300, "ca_eur": 80000000,
                          "enregistre": True}, aujourdhui="2026-09-18")
    assert faite["enregistrement"]["en_retard"] is False


def test_avant_l_echeance_l_entite_n_est_pas_en_retard():
    """LE TÉMOIN QUI INTERDIT DE RENDRE `en_retard` EN DUR. Au 1er janvier
    2025, l'échéance n'est pas passée : personne n'est en retard."""
    r = nis2.evaluer({"nom": "X", "secteur": "eau_potable", "effectif": 300,
                      "ca_eur": 80000000}, aujourdhui="2025-01-01")
    assert r["enregistrement"]["en_retard"] is False


def test_le_calendrier_prend_la_date_par_la_porte_et_pas_a_l_horloge():
    """UNE ÉCHÉANCE CALCULÉE SUR `date.today()` REND UNE RÈGLE QUI PASSE
    AUJOURD'HUI ET TOMBE DEMAIN."""
    vieux = nis2.calendrier("2023-01-01")
    recent = nis2.calendrier("2026-09-18")
    assert vieux["en_vigueur"] == []
    assert len(recent["en_vigueur"]) == len(nis2.ECHEANCES)


# ═══════════════════════════════════════════════════════════════════════════
#  9. LES MESURES — UNE CASE VIDE N'EST PAS UNE CASE VERTE
# ═══════════════════════════════════════════════════════════════════════════

def test_le_taux_des_mesures_voyage_toujours_avec_les_non_renseignees():
    """UN 100 % SUR DEUX MESURES NE DIT RIEN DES HUIT AUTRES, et c'est le taux
    qu'on emporte en comité."""
    e = nis2._ecarts_mesures({"a": "conforme", "b": "conforme"})
    assert e["taux"] == 20, (
        "deux conformes sur dix retenues = 20 %%, rendu %s" % e["taux"])
    assert e["non_renseigne"] == 8


def test_sans_objet_sort_du_denominateur_mais_non_renseigne_y_reste():
    """LA DIFFÉRENCE ENTRE « ÇA NE ME CONCERNE PAS » ET « JE N'AI PAS
    REGARDÉ ». La première se retire du calcul, la seconde compte contre."""
    hors = nis2._ecarts_mesures({"a": "conforme", "j": "sans_objet"})
    assert hors["retenus"] == 9
    vide = nis2._ecarts_mesures({"a": "conforme"})
    assert vide["retenus"] == 10


def test_les_dix_mesures_sont_etiquetees_a_a_j():
    cles = [c for c, _n, _d in nis2.MESURES]
    assert cles == list("abcdefghij"), (
        "l'article 21, §2, va de a) à j) : %s" % cles)


def test_le_module_dit_que_les_dix_sont_un_SOCLE_et_non_une_liste():
    """« COMPRENNENT AU MOINS ». Un écran qui présenterait les dix comme une
    liste à épuiser ferait croire qu'on peut finir."""
    assert "au moins" in nis2.MESURES_CLAUSE["socle"].lower()
    assert "plancher" in nis2.MESURES_CLAUSE["socle"].lower()


# ═══════════════════════════════════════════════════════════════════════════
#  10. LE GROUPE — CE QUI COMMANDE N'EST PAS LA MOYENNE
# ═══════════════════════════════════════════════════════════════════════════

def test_le_groupe_est_commande_par_sa_filiale_la_plus_haute():
    """UN GROUPE DE DOUZE FILIALES DONT UNE SEULE EST ESSENTIELLE n'a pas
    « 8 % de supervision ex ante » : il a des audits réguliers à subir et un
    dirigeant exposé. La moyenne ne décrit aucune filiale réelle."""
    g = nis2.evaluer_groupe([
        {"nom": "A", "secteur": "dechets", "effectif": 900, "ca_eur": 200000000},
        {"nom": "B", "secteur": "dechets", "effectif": 900, "ca_eur": 200000000},
        {"nom": "C", "secteur": "eau_potable", "effectif": 300,
         "ca_eur": 80000000},
    ])
    assert g["commande"]["nom"] == "C"
    assert g["commande"]["statut"]["cle"] == "essentielle"
    assert g["essentielles"] == 1 and g["cotes"] == 3


def test_le_groupe_compte_les_ETATS_MEMBRES_parce_que_c_est_le_multiplicateur():
    """LE FAIT QUE SEUL UN GROUPE RÉVÈLE. Une entité qui opère dans cinq États
    membres relève de cinq transpositions : cinq autorités, cinq régimes de
    sanction possiblement plus sévères que le plancher européen. Aucune lecture
    entité par entité ne le fait voir."""
    g = nis2.evaluer_groupe([
        {"nom": "A", "secteur": "eau_potable", "effectif": 300,
         "ca_eur": 80000000, "etats_membres": ["FR", "BE"]},
        {"nom": "B", "secteur": "dechets", "effectif": 900,
         "ca_eur": 200000000, "etats_membres": ["FR", "DE", "IT"]},
    ])
    assert g["etats_membres"] == ["BE", "DE", "FR", "IT"]
    assert "4" in g["dit_transposition"], (
        "le compte d'États membres doit paraître dans la phrase : %r"
        % g["dit_transposition"])


def test_un_groupe_sans_etat_membre_declare_le_dit_au_lieu_de_compter_zero():
    g = nis2.evaluer_groupe([
        {"nom": "A", "secteur": "eau_potable", "effectif": 300,
         "ca_eur": 80000000}])
    assert "ne peut pas être estimée" in g["dit_transposition"]


def test_le_groupe_refuse_deux_filiales_de_meme_nom():
    """SANS CE REFUS, LA SECONDE ÉCRASERAIT SILENCIEUSEMENT LA PREMIÈRE dans
    toute restitution indexée par le nom."""
    g = nis2.evaluer_groupe([
        {"nom": "A", "secteur": "eau_potable", "effectif": 300, "ca_eur": 8e7},
        {"nom": "A", "secteur": "dechets", "effectif": 300, "ca_eur": 8e7}])
    assert g["ok"] is False and g["motif"] == "noms_en_double"


# ═══════════════════════════════════════════════════════════════════════════
#  11. LA GARDE DU MODULE — ELLE DOIT RESTER ARMÉE
# ═══════════════════════════════════════════════════════════════════════════

def test_la_garde_du_module_est_passee_au_chargement():
    """`_FAUTES` EST LA PREUVE QUE `_verifier()` A COURU. Un module dont la
    garde serait commentée se chargerait sans bruit."""
    assert nis2._FAUTES == []


def test_les_annexes_comptent_onze_et_sept_secteurs():
    assert len(nis2.ANNEXE_I) == 11
    assert len(nis2.ANNEXE_II) == 7
    assert len(nis2.SECTEURS) == 18


def test_la_source_declare_sa_licence_et_son_eli():
    """UN TEXTE DU JOURNAL OFFICIEL EST RÉUTILISABLE, mais pas sans dire sous
    quelle licence — c'est la discipline tenue pour le CRA, elle vaut ici."""
    assert "2011/833" in nis2.SOURCE["licence"]
    assert nis2.SOURCE["eli"].startswith("http")


def test_le_moteur_refuse_une_declaration_sans_nom():
    r = nis2.evaluer({"secteur": "energie", "effectif": 300})
    assert r["ok"] is False and r["motif"] == "nom_manquant"
