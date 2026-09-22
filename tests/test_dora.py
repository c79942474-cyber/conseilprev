# -*- coding: utf-8 -*-
"""DORA — LES SIX MOTEURS, ET CE QU'ILS REFUSENT DE DIRE.

CE QUI A DÉCLENCHÉ CE FICHIER. Une demande : « dans les 11 normes
maîtrisées de Sentinel, connecter et ajouter DORA à "votre mise en
conformité réglementaire" du menu latéral et proposer une analyse de
risque en fonction des docs jointes claire, fiable, détaillée de DORA
pour les clients ».

CE QUE CES RÈGLES MESURENT, ET POURQUOI CE N'EST PAS DU BRANCHEMENT.
Un module DORA qui rend des taux est facile ; un module DORA qui rend les
BONS taux ne l'est pas, parce que le règlement a quatre pièges qui se
ressemblent tous à une bonne nouvelle :

  · annoncer vingt-six articles à une entité qui n'en doit que quatorze ;
  · compter neuf clauses contractuelles quand quinze sont dues ;
  · rendre « pas un incident majeur » alors que la criticité n'a jamais
    été déclarée ;
  · dire à un hébergeur que DORA « prime » et que NIS 2 ne le concerne
    plus — alors que l'article 1er, §2, ne vise que les entités
    FINANCIÈRES, et qu'il n'en est pas une.

Les quatre se soldent par un client rassuré à tort. Les règles de ce
fichier visent donc les REFUS autant que les résultats.
"""
import io
import os
import re

import pytest

import dora
import dora_incident
import dora_ponts
import dora_risque
import dora_supervision
import dora_tiers
import conformite

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


SENTINEL = _lire("sentinel.html")
PAGEJS = _lire("sentinel.page.js")
APP = _lire("app.py")


# ══════════════════════════════════════════════════════════════════════════
#  1. LE CHAMP ET LE RÉGIME — CE QUI COMMANDE TOUT LE RESTE
# ══════════════════════════════════════════════════════════════════════════

def test_les_vingt_ET_UN_types_de_l_article_2_sont_la_et_VINGT_sont_financieres():
    """LE VINGT ET UNIÈME N'EST PAS UNE ENTITÉ FINANCIÈRE, ET C'EST LE PIVOT.

    L'article 2, §1, énumère vingt et un points, a) à u). L'article 2, §2,
    réserve le terme « entités financières » aux points a) à t). Le point
    u) — le prestataire tiers de services TIC — est dans le champ à un
    AUTRE titre : il est la contrepartie du chapitre V, pas le porteur des
    chapitres II à IV.

    Tout le module en dépend : c'est ce qui décide qu'il n'a pas de régime,
    et que l'article 1er, §2, ne le vise pas.
    """
    assert len(dora.ENTITES) == 21, len(dora.ENTITES)
    lettres = [e[1] for e in dora.ENTITES]
    assert lettres == [chr(c) for c in range(ord("a"), ord("u") + 1)], lettres
    assert len(dora.FINANCIERES) == 20, (
        "l'article 2, §2, réserve « entités financières » aux points a) à "
        "t) : %d sont déclarées telles" % len(dora.FINANCIERES))
    assert dora.ENTITES_PAR_CLE["prestataire_tic"][3] is False


def test_la_TAILLE_ne_decide_PAS_du_regime():
    """LE PIÈGE LE PLUS TENTANT DU RÈGLEMENT.

    L'article 3 définit microentreprise, petite et moyenne entreprise. Ces
    définitions servent ailleurs — notamment pour écarter la règle des
    incidents récurrents. Le cadre simplifié repose sur les cinq catégories
    NOMMÉES de l'article 16, §1, pas sur un seuil d'effectif.

    LA RÈGLE MESURE LA CONSÉQUENCE, PAS LA DÉCLARATION : une
    microentreprise qui n'est dans aucune des cinq doit ressortir en cadre
    COMPLET. Si un jour quelqu'un branche la taille sur le régime, c'est
    ici que ça tombe.
    """
    micro = dora.qualifier({"entite": "etablissement_credit",
                            "effectif": 4, "ca_eur": 900000.0,
                            "bilan_eur": 500000.0})
    assert micro["taille"]["cle"] == "micro", micro["taille"]
    assert micro["regime"] == "complet", (
        "une microentreprise hors des cinq catégories de l'article 16, §1, "
        "reçoit le cadre %r : la taille décide du régime, ce qu'elle ne "
        "doit pas faire" % micro["regime"])


def test_une_des_cinq_categories_de_l_article_16_donne_le_cadre_SIMPLIFIE():
    """LE CADRE SIMPLIFIÉ EXISTE, ET IL SE DÉCLENCHE SUR UNE CATÉGORIE
    NOMMÉE. Si la porte cessait de s'ouvrir, une petite institution de
    retraite professionnelle recevrait les vingt-six articles du titre II —
    douze de plus que ce qu'elle doit — et personne ne le verrait, parce
    que « plus d'exigences » ne ressemble jamais à un défaut."""
    q = dora.qualifier({"entite": "retraite_professionnelle",
                        "petite_irp": True})
    assert q["regime"] == "simplifie", q["regime"]
    assert q["article"] == "Article 16, paragraphe 1", q["article"]
    assert len(q["obligations"]) == 8, (
        "l'article 16, §1, deuxième alinéa, porte huit obligations a) à h)")


def test_le_prestataire_tiers_n_a_PAS_de_regime():
    """LUI EN DONNER UN LUI PRÊTERAIT LES DEVOIRS DE SON CLIENT.

    Il est dans le champ (art. 2, §1, u)) mais les chapitres II à IV ne lui
    sont pas opposables. Un « cadre complet » affiché sur son écran lui
    ferait coter vingt-six articles qui ne le visent pas.
    """
    q = dora.qualifier({"entite": "prestataire_tic"})
    assert q["dans_le_champ"] is True
    assert q["regime"] is None, q["regime"]
    assert q["entite"]["financiere"] is False


def test_une_exclusion_de_l_article_2_paragraphe_3_met_HORS_CHAMP():
    """HORS CHAMP N'EST PAS « CADRE ALLÉGÉ ». Le règlement ne s'applique
    pas : il n'y a pas de régime, et il ne faut pas en annoncer un."""
    q = dora.qualifier({"entite": "retraite_professionnelle",
                        "irp_quinze_affilies": True})
    assert q["dans_le_champ"] is False
    assert q["regime"] == "hors_champ"
    assert q["article"].startswith("Article 2, paragraphe 3"), q["article"]


# ══════════════════════════════════════════════════════════════════════════
#  2. L'ANALYSE DE RISQUE — DEUX RÉGIMES QUI NE SE RECOUVRENT PAS
# ══════════════════════════════════════════════════════════════════════════

def test_les_deux_titres_du_RTS_sont_DISJOINTS_et_comptent_quarante():
    """SI LES DEUX JEUX SE RECOUVRAIENT, UN ARTICLE SERAIT OPPOSÉ AUX DEUX
    RÉGIMES — et le cadre simplifié cesserait d'être simplifié sans que
    personne ne le voie. Vingt-six plus quatorze, plus les deux qui ne
    s'évaluent pas, font les quarante-deux du texte."""
    assert len(dora_risque.ARTICLES_1774) == 42
    complet = {a[0] for a in dora_risque.articles("complet")}
    simple = {a[0] for a in dora_risque.articles("simplifie")}
    assert len(complet) == 26, len(complet)
    assert len(simple) == 14, len(simple)
    assert not (complet & simple), (
        "des articles sont opposés aux DEUX régimes : %s"
        % sorted(complet & simple))
    hors = set(dora_risque.HORS_EVALUATION)
    assert complet | simple | hors == {a[0] for a in dora_risque.ARTICLES_1774}


def test_le_module_de_risque_REFUSE_d_evaluer_sans_regime():
    """LE REFUS EST LE LIVRABLE. Choisir « complet » par défaut ferait
    porter vingt-six articles à une entité qui n'en doit que quatorze ;
    choisir « simplifié » masquerait douze exigences. Aucune des deux
    erreurs ne se rattrape par un avertissement."""
    for regime in (None, "", "moyen", "complet ", 3):
        r = dora_risque.evaluer(regime, {2: "prouve"})
        assert r["ok"] is False, (
            "le module évalue sous le régime %r" % (regime,))
        assert r["motif"] == "regime_absent"


def test_un_article_HORS_REGIME_est_ignore_ET_signale():
    """L'IGNORER SANS LE DIRE SERAIT PIRE QUE DE LE COMPTER. Le client
    croirait avoir renseigné ce qu'il a renseigné ; le taux, lui, ne le
    porterait pas, et l'écart ne se verrait jamais."""
    r = dora_risque.evaluer("simplifie", {2: "prouve", 30: "prouve"})
    assert r["ok"] is True
    verrous = {v["cle"] for v in r["verrous"]}
    assert "articles_hors_regime" in verrous, verrous


def test_le_titre_de_l_article_23_n_est_PAS_tronque():
    """MESURÉ CONTRE LE JOURNAL OFFICIEL, ET CORRIGÉ.

    L'intitulé de l'article 23 court sur deux lignes dans le PDF ; la
    première extraction n'avait gardé que la première, et le titre
    s'arrêtait sur « la réponse à ces » — une phrase sans objet. Un titre
    coupé se relit sans rien remarquer : il faut une règle pour le voir.
    """
    titre = [a[1] for a in dora_risque.ARTICLES_1774 if a[0] == 23][0]
    assert titre.endswith("la réponse à ces incidents"), titre
    # LE DERNIER MOT, PAS LA FIN DE LA CHAÎNE. Une première version
    # comparait la fin de la chaîne à « aux » — elle mordait sur « rése-AUX »
    # et levait sur l'article 13, dont le titre est entier. Une règle qui
    # passe pour une raison sans rapport avec ce qu'elle prétend ne mesure
    # rien : c'est le défaut même qu'elle est censée attraper.
    CREUX = {"à", "ces", "de", "la", "le", "les", "des", "du", "et", "ou",
             "aux", "au", "un", "une", "en", "sur", "par", "pour", "dans"}
    for num, titre_n, _ti, _c, _cn in dora_risque.ARTICLES_1774:
        dernier = titre_n.rstrip().rsplit(" ", 1)[-1].strip("’'\u2019").lower()
        assert dernier not in CREUX, (
            "l'intitulé de l'article %d se termine sur le mot creux %r : "
            "le titre est probablement coupé — %r" % (num, dernier, titre_n))


# ══════════════════════════════════════════════════════════════════════════
#  3. LES CONTRATS — NEUF, OU QUINZE
# ══════════════════════════════════════════════════════════════════════════

def test_neuf_clauses_communes_et_SIX_de_plus_pour_une_fonction_critique():
    """« EN PLUS DE CEUX QUI FIGURENT AU PARAGRAPHE 2 » : c'est un cumul,
    pas un remplacement. Le lire comme un remplacement ferait signer un
    contrat critique à neuf clauses."""
    assert len(dora_tiers.CLAUSES_COMMUNES) == 9
    assert len(dora_tiers.CLAUSES_CRITIQUES) == 6
    assert len(dora_tiers.clauses_attendues(False)) == 9
    assert len(dora_tiers.clauses_attendues(True)) == 15
    # ET LE CONSOMMATEUR AUSSI, PAS SEULEMENT LA TABLE. La garde d'import de
    # `dora_tiers` contrôle déjà `clauses_attendues` ; ce qu'elle ne contrôle
    # pas, c'est qu'`examiner` l'appelle avec LA BONNE criticité. Un contrat
    # critique compté sur neuf clauses rendrait 100 % en en oubliant six.
    assert dora_tiers.examiner({"fonction_critique": True})["attendues"] == 15
    assert dora_tiers.examiner({"fonction_critique": False})["attendues"] == 9


def test_le_contrat_REFUSE_d_etre_note_sans_criticite_declaree():
    """UN TAUX SUR NEUF CLAUSES QUAND QUINZE SONT DUES EST RASSURANT À
    TORT, et c'est la pire des erreurs possibles sur cet écran : elle ne
    se découvre qu'au contrôle, contrat déjà signé."""
    r = dora_tiers.examiner({"clauses": {"commune_a": "presente"}})
    assert r["ok"] is False
    assert r["motif"] == "criticite_non_declaree"


def test_la_derogation_micro_ne_vaut_QUE_pour_le_point_e_ET_QUE_pour_une_micro():
    """DEUX CONDITIONS, ET LES DEUX SE MESURENT ICI.

    Le dernier alinéa de l'article 30, §3, permet à une entité financière
    QUI EST UNE MICROENTREPRISE de déléguer les droits d'accès,
    d'inspection et d'audit du point e). L'accepter ailleurs — autre
    clause, ou autre entité — ferait passer une absence pour un
    aménagement prévu par le texte.
    """
    toutes = dict([("commune_%s" % l, "presente") for l in "abcdefghi"]
                  + [("critique_%s" % l, "presente") for l in "abcdf"])
    micro = dora_tiers.examiner(dict(
        fonction_critique=True, microentreprise=True,
        clauses=dict(toutes, critique_e="deleguee")))
    assert micro["taux"] == 100.0, micro["taux"]

    ordinaire = dora_tiers.examiner(dict(
        fonction_critique=True, microentreprise=False,
        clauses=dict(toutes, critique_e="deleguee")))
    assert ordinaire["taux"] < 100.0, (
        "une entité qui n'est pas une microentreprise obtient 100 %% avec "
        "un audit délégué : la dérogation lui est appliquée à tort")

    ailleurs = dora_tiers.examiner(dict(
        fonction_critique=True, microentreprise=True,
        clauses=dict(toutes, critique_e="presente", critique_f="deleguee")))
    assert ailleurs["taux"] < 100.0, (
        "la délégation est acceptée sur le point f) : la dérogation ne "
        "vise QUE le point e)")


# ══════════════════════════════════════════════════════════════════════════
#  4. L'INCIDENT — UNE CONJONCTION, PAS UNE LISTE
# ══════════════════════════════════════════════════════════════════════════

def test_la_criticite_est_une_PORTE_et_son_absence_rend_None():
    """NI « MAJEUR », NI « PAS MAJEUR » : INDÉTERMINÉ.

    Rendre False sur une criticité non déclarée se lirait comme une bonne
    nouvelle — « rien à notifier » — alors que la question n'a pas été
    posée. Trois seuils atteints sans criticité déclarée doivent rester
    indéterminés.
    """
    r = dora_incident.evaluer({"nombre_clients": 200000,
                               "duree_heures": 48,
                               "etats_membres": 3})
    assert r["ok"] is True
    assert r["majeur"] is None, (
        "la criticité n'est pas déclarée et le verdict vaut %r"
        % r["majeur"])


def test_UN_seuil_ne_suffit_pas_mais_DEUX_oui_et_l_acces_malveillant_SEUL_suffit():
    """LA CONJONCTION DE L'ARTICLE 8, §1, EN TROIS MESURES.

    Services critiques touchés ET (l'accès malveillant réussi à lui seul
    OU deux autres seuils). Lire « ou » là où le texte dit « et »
    surqualifierait tous les incidents ; l'inverse en manquerait.
    """
    base = {"services_critiques": True}
    un = dora_incident.evaluer(dict(base, duree_heures=48))
    assert un["majeur"] is False, un

    deux = dora_incident.evaluer(dict(base, duree_heures=48,
                                      etats_membres=3))
    assert deux["majeur"] is True, deux

    seul = dora_incident.evaluer(dict(base, acces_malveillant=True))
    assert seul["majeur"] is True, (
        "l'accès malveillant réussi ne suffit pas à lui seul : "
        "l'article 9, §5, b), est traité comme un seuil ordinaire")
    # ET LA GARDE-FOU DU SEUIL LUI-MÊME : 24 h n'est PAS « plus de 24 h ».
    pile = dora_incident.evaluer(dict(base, duree_heures=24,
                                      etats_membres=3))
    assert pile["majeur"] is False, (
        "vingt-quatre heures pile franchissent un seuil que le texte fixe "
        "à « plus de vingt-quatre heures »")


def test_sans_services_critiques_AUCUN_nombre_de_seuils_ne_rend_majeur():
    """LA CRITICITÉ EST UNE PORTE, PAS UN SEPTIÈME SEUIL. En faire un
    seuil de plus laisserait six autres suffire à la remplacer."""
    r = dora_incident.evaluer({"services_critiques": False,
                               "acces_malveillant": True,
                               "duree_heures": 48,
                               "etats_membres": 3,
                               "cout_eur": 500000.0})
    assert r["majeur"] is False, r


# ══════════════════════════════════════════════════════════════════════════
#  5. LE PONT NIS 2 — LE VERROU DU MODULE
# ══════════════════════════════════════════════════════════════════════════

def test_RIEN_n_est_ecarte_a_un_prestataire_tiers_de_services_TIC():
    """L'ERREUR DE LECTURE LA PLUS COÛTEUSE DU MARCHÉ, ET C'EST ICI QU'ELLE
    SE FERME.

    « DORA prime sur NIS 2 » circule comme une vérité générale. L'article
    1er, §2, ne vise que les entités FINANCIÈRES, que l'article 2, §2,
    réserve aux points a) à t). Un hébergeur, un exploitant de centre de
    données ou un fournisseur de services gérés qui sert des banques ne
    voit RIEN d'écarté : NIS 2 lui reste pleinement opposable, et DORA
    l'atteint EN PLUS, au titre du chapitre V.
    """
    q = dora.qualifier({"entite": "prestataire_tic"})
    a = dora_ponts.articulation(q, True)
    assert a["issue"] == "cumul", a["issue"]
    assert a["ecarte"] == [], (
        "%d disposition(s) de NIS 2 sont écartées à un prestataire tiers de "
        "services TIC, qui n'est pas une entité financière"
        % len(a["ecarte"]))


def test_l_articulation_REFUSE_de_presumer_l_identification_NIS2():
    """LA MISE À L'ÉCART NE SE PRÉSUME PAS. Supposer l'identification
    annoncerait une mise à l'écart qui n'existe peut-être pas — et c'est
    précisément l'erreur qui coûte cher, parce qu'elle fait cesser de
    répondre à l'autorité nationale."""
    q = dora.qualifier({"entite": "etablissement_credit"})
    a = dora_ponts.articulation(q, None)
    assert a["issue"] == "a_completer", a["issue"]
    assert a["ecarte"] == []


def test_ce_qui_RESTE_DU_est_rendu_meme_quand_tout_est_ecarte():
    """LA MOITIÉ DE LA PHRASE QUE LE CLIENT RETIENT DE TRAVERS.

    « DORA prime » s'entend comme « NIS 2 ne me concerne plus », et
    l'entité cesse de répondre à son autorité nationale. L'identification
    de l'article 3, §3, et l'enregistrement du §4 restent dus : ils sont
    la CONDITION de la mise à l'écart, pas son objet.
    """
    q = dora.qualifier({"entite": "etablissement_credit"})
    a = dora_ponts.articulation(q, True)
    assert a["issue"] == "ecarte"
    articles = " ".join(x["article"] for x in a["reste"])
    assert "article 3, paragraphe 3" in articles, articles
    assert "article 3, paragraphe 4" in articles, articles


def test_chaque_mise_a_l_ecart_dit_AVEC_QUELLE_CERTITUDE():
    """TROIS SONT NOMMÉES PAR UN ARTICLE, UNE SE DÉDUIT. Les annoncer du
    même ton vendrait une certitude qu'on n'a pas : le périmètre des
    « dispositions pertinentes » appartient aux lignes directrices de
    l'article 4, §3."""
    certitudes = {x["cle"]: x["certitude"] for x in dora_ponts.ECARTE}
    assert certitudes["nis2_21"] == "texte"
    assert certitudes["nis2_23"] == "texte"
    assert certitudes["nis2_ch7"] == "texte"
    assert certitudes["nis2_20"] == "deduit", (
        "l'article 20 est annoncé comme nommé par un texte : aucun article "
        "ne le nomme, il tombe sous la formule « dispositions pertinentes »")


def test_TROIS_types_financiers_seulement_figurent_aux_annexes_de_NIS2():
    """LE FAIT QUI DÉCIDE DE PRESQUE TOUS LES DOSSIERS, et il n'est nulle
    part écrit en une phrase. L'annexe I de la directive ne porte, côté
    finance, que les établissements de crédit, les exploitants de
    plates-formes de négociation et les contreparties centrales. Une
    compagnie d'assurance ou une société de gestion n'y figure PAS."""
    assert len(dora_ponts.ANNEXE_I_NIS2) == 3
    assert set(dora_ponts.ANNEXE_I_PAR_ENTITE) == {
        "etablissement_credit", "plateforme_negociation",
        "contrepartie_centrale"}
    for cle in dora_ponts.ANNEXE_I_PAR_ENTITE:
        assert dora.ENTITES_PAR_CLE[cle][3] is True


def test_une_identification_HORS_ANNEXE_est_signalee_au_lieu_de_passer():
    """MESURÉ, ET C'EST CE QUI A FAIT AJOUTER L'ALERTE.

    Une compagnie d'assurance déclarée identifiée rendait exactement le
    même verdict qu'un établissement de crédit — « écarté », quatre
    articles mis de côté — alors que son type ne figure dans AUCUNE annexe
    de la directive. Le verdict n'est pas faux (un État membre peut
    désigner au titre de l'article 2, §2, b) à e)), mais rendre les deux
    du même ton laisserait passer une déclaration erronée sans bruit.
    """
    banque = dora_ponts.articulation(
        dora.qualifier({"entite": "etablissement_credit"}), True)
    assurance = dora_ponts.articulation(
        dora.qualifier({"entite": "assurance"}), True)
    assert banque["issue"] == assurance["issue"] == "ecarte"
    assert banque["alerte"] is None
    assert assurance["alerte"] == "identifiee_hors_annexe", (
        "l'assurance et la banque rendent le même écran : rien ne signale "
        "que le type de l'une ne figure dans aucune annexe")


# ══════════════════════════════════════════════════════════════════════════
#  6. LE PONT ISO 27001 — UNE REPRISE DE PREUVES, PAS UNE CONFORMITÉ
# ══════════════════════════════════════════════════════════════════════════

def test_le_pont_ISO_couvre_TOUS_les_articles_evaluables_et_EUX_SEULS():
    """UN ARTICLE OUBLIÉ FERAIT MENTIR LE DÉNOMINATEUR ; un article en trop
    ferait porter au régime des exigences de l'autre."""
    evaluables = {n for n, _t, _ti, _c, _cn in dora_risque.ARTICLES_1774
                  if n not in dora_risque.HORS_EVALUATION}
    assert set(dora_ponts.CORRESPONDANCE_PAR_ARTICLE) == evaluables


def test_les_deux_rapports_a_l_autorite_n_ont_AUCUN_repondant_dans_la_norme():
    """LE RÉSULTAT LE PLUS UTILE DU PONT, ET LE PLUS FRAGILE.

    Les articles 27 et 41 du règlement délégué demandent un rapport sur le
    réexamen du cadre, dans un format électronique interrogeable, destiné à
    l'autorité compétente. Aucune mesure de l'annexe A ne le produit. Une
    correspondance ajoutée par distraction ferait disparaître ce constat
    sans bruit — et un organisme certifié croirait ces deux-là couverts.
    """
    for n in (27, 41):
        ligne = dora_ponts.CORRESPONDANCE_PAR_ARTICLE[n]
        assert ligne[1] == "aucune", (n, ligne[1])
        assert ligne[2] == (), (n, ligne[2])
    ap = dora_ponts.apport("complet")
    assert [x["article"] for x in ap["propres_a_dora"]] == [27]
    ap = dora_ponts.apport("simplifie")
    assert [x["article"] for x in ap["propres_a_dora"]] == [41]


def test_toute_mesure_citee_EXISTE_dans_l_annexe_A():
    """UN NUMÉRO INVENTÉ SURVIVRAIT À TOUTE RELECTURE : personne ne connaît
    les quatre-vingt-treize par cœur, et « A.8.41 » se lit comme les
    autres."""
    import iso27001
    connues = set(iso27001.MESURES)
    for n, _c, mesures, _ch, _m in dora_ponts.CORRESPONDANCE:
        for m in mesures:
            assert m in connues, (
                "article %d : la mesure %s n'existe pas dans l'annexe A"
                % (n, m))


def test_le_taux_d_appui_DIT_qu_il_n_est_PAS_un_taux_de_conformite():
    """UN CHIFFRE D'APPUI LU COMME UN TAUX DE CONFORMITÉ EST PIRE
    QU'AUCUN CHIFFRE : il rassure. La phrase qui le désamorce doit
    voyager dans la MÊME réponse que le nombre."""
    ap = dora_ponts.apport("complet")
    assert 0 < ap["taux_appui"] < 100
    dit = ap["ce_que_le_taux_ne_dit_pas"]
    assert "pas une conformité" in dit or "pas une conformite" in dit, dit


def test_ce_qu_aucun_certificat_ne_couvre_porte_son_ARTICLE():
    """« LA NORME NE COUVRE PAS TOUT » NE SE DISCUTE PAS ; « la norme ne
    couvre pas l'article 28, §3 » se vérifie. C'est la différence entre un
    avertissement et un argument."""
    articles = " ".join(x["article"] for x in dora_ponts.NE_REMPLACE_PAS)
    for attendu in ("article 28, paragraphe 3", "article 30",
                    "articles 26 et 27", "2025/301"):
        assert attendu in articles, (
            "%r n'est pas nommé parmi ce qu'aucun certificat ne couvre"
            % attendu)
    for x in dora_ponts.NE_REMPLACE_PAS:
        assert x["article"] and x["quoi"], x


def test_le_pont_ISO_REFUSE_de_travailler_sans_regime():
    """MÊME RAISON QUE L'ANALYSE DE RISQUE : les deux titres ne se
    recouvrent pas, et la correspondance n'a de sens que dans un régime."""
    r = dora_ponts.apport(None, ["A.5.1"])
    assert r["ok"] is False and r["motif"] == "regime_absent"


# ══════════════════════════════════════════════════════════════════════════
#  7. LA SUPERVISION — CE QUI SE CONSTATE, ET CE QUI NE SE CALCULE PAS
# ══════════════════════════════════════════════════════════════════════════

def test_les_quatre_exclusions_de_l_article_31_FERMENT_la_designation():
    """ELLES NE S'APPRÉCIENT PAS, ELLES SE CONSTATENT — et c'est la seule
    réponse ferme que le texte permette. Un prestataire intragroupe ne peut
    pas être désigné, quelle que soit sa part de marché."""
    assert len(dora_supervision.EXCLUSIONS) == 4
    for cle in dora_supervision.EXCLUSIONS_PAR_CLE:
        d = dict((x["cle"], False) for x in dora_supervision.EXCLUSIONS)
        d[cle] = True
        r = dora_supervision.eligibilite(d)
        assert r["issue"] == "exclu", (cle, r["issue"])


def test_une_exclusion_NON_DECLAREE_n_est_pas_une_exclusion_ECARTEE():
    """LA PLUS RASSURANTE DES ERREURS, ET LA PIRE. Traiter le silence
    comme un « non » rendrait « éligible » à un prestataire intragroupe qui
    n'aurait simplement pas répondu."""
    d = dict((x["cle"], False) for x in dora_supervision.EXCLUSIONS)
    del d["intragroupe"]
    r = dora_supervision.eligibilite(d)
    assert r["issue"] == "a_completer", r["issue"]
    assert "intragroupe" in r["exclusions_non_declarees"]


def test_l_etape_1_se_calcule_a_DIX_POUR_CENT_et_l_etape_2_JAMAIS():
    """LA LIGNE QUE CE MODULE NE FRANCHIT PAS.

    L'acte délégué C(2024) 896 chiffre l'étape 1 : les deux parts d'une
    même catégorie à dix pour cent chacune. L'étape 2 — intensité de
    l'incidence, dépendance aux mêmes sous-traitants, interdépendance des
    établissements systémiques — est une APPRÉCIATION. Lui donner un seuil
    ferait calculer une désignation que les AES prononcent.
    """
    assert dora_supervision.SEUIL_PART == 10.0
    for s in dora_supervision.SOUS_CRITERES:
        if s["etape"] == 2:
            assert s.get("seuil") is None, (
                "le sous-critère %s est à l'étape 2 et porte un seuil"
                % s["cle"])
    socle = dict((x["cle"], False) for x in dora_supervision.EXCLUSIONS)
    socle.update(eism=2, autres_eis=0, autres_eis_score_sup_3000=0,
                 systemiques_ghij=1, systemiques_autres=0)

    sous = dora_supervision.eligibilite(dict(
        socle,
        categories_servies=[{"part_nombre": 9.9, "part_actifs": 80.0}],
        categories_substituabilite=[{"part_sans_alternative": 90.0,
                                     "part_bascule_difficile": 90.0}]))
    assert sous["issue"] == "etape_1_non_franchie", sous["issue"]

    au_dessus = dora_supervision.eligibilite(dict(
        socle,
        categories_servies=[{"part_nombre": 10.0, "part_actifs": 80.0}],
        categories_substituabilite=[{"part_sans_alternative": 90.0,
                                     "part_bascule_difficile": 90.0}]))
    assert au_dessus["issue"] == "etape_1_franchie", au_dessus["issue"]
    dit = au_dessus["l_etape_2_ne_se_calcule_pas"]
    assert "appréciation" in dit, dit
    assert "ne vaut pas désignation" in dit, (
        "la phrase qui accompagne le verdict ne dit pas que franchir "
        "l'étape 1 ne vaut pas désignation : %r" % dit)


def test_la_lecture_INCERTAINE_de_la_substituabilite_est_DITE_et_non_tranchee():
    """L'ACTE DÉLÉGUÉ NE TRANCHE PAS, ALORS LE MODULE NE TRANCHE PAS NON
    PLUS.

    L'article 2, §4, exige les deux parts dans LA MÊME catégorie ; l'article
    5, §4, ne le dit pas expressément. Choisir en silence ferait dire au
    module une chose que le texte ne dit pas — et dans un sens qui change le
    verdict. Il rend donc les deux lectures et signale la divergence.
    """
    socle = dict((x["cle"], False) for x in dora_supervision.EXCLUSIONS)
    socle.update(eism=2, autres_eis=0, autres_eis_score_sup_3000=0,
                 systemiques_ghij=1, systemiques_autres=0,
                 categories_servies=[{"part_nombre": 20.0,
                                      "part_actifs": 40.0}])
    r = dora_supervision.eligibilite(dict(socle, categories_substituabilite=[
        {"categorie": "a", "part_sans_alternative": 30.0,
         "part_bascule_difficile": 2.0},
        {"categorie": "b", "part_sans_alternative": 2.0,
         "part_bascule_difficile": 30.0}]))
    assert r["issue"] == "lecture_incertaine", r["issue"]
    assert r["etape_1"]["substituabilite"]["diverge"] is True


def test_la_redevance_a_un_PLANCHER_de_cinquante_mille_euros():
    """LA PARTIE QUI SURPREND, ET CELLE QU'ON ANNONCE EN PREMIER. Un petit
    prestataire désigné critique paie 50 000 EUR même si son coefficient de
    chiffre d'affaires en donnerait quatre mille."""
    assert dora_supervision.REDEVANCE_PLANCHER_EUR == 50000.0
    r = dora_supervision.redevance(couts_totaux_eur=20e6,
                                   ca_prestataire_eur=2e6,
                                   ca_tous_prestataires_eur=1e10)
    assert r["ok"] is True
    assert r["brut_eur"] < 50000.0
    assert r["due_eur"] == 50000.0
    assert r["releve_par_le_plancher"] is True


def test_la_redevance_REFUSE_de_chiffrer_sans_les_couts_annuels():
    """LES COÛTS SONT ESTIMÉS CHAQUE ANNÉE PAR LES SUPERVISEURS ; ils ne
    sont dans aucun texte. En inventer un rendrait un montant faux avec
    l'autorité d'un calcul."""
    r = dora_supervision.redevance()
    assert r["ok"] is False and r["motif"] == "couts_absents"
    assert r["plancher_eur"] == 50000.0


# ══════════════════════════════════════════════════════════════════════════
#  8. LE CÂBLAGE — LE TAUX MÈNE À L'ÉCRAN OÙ ON LE CORRIGE
# ══════════════════════════════════════════════════════════════════════════

#: LES SIX PANNEAUX, ÉCRITS ICI UNE SEULE FOIS. Plusieurs règles les
#: parcourent, et les tenir à deux endroits garantirait qu'un panneau neuf
#: soit contrôlé par l'une et ignoré par l'autre.
PANNEAUX = ("dora-qualifier", "dora-risque", "dora-tiers", "dora-incident",
            "dora-iso", "dora-supervision")

ROUTES = ("/api/dora/referentiel", "/api/dora/qualifier", "/api/dora/evaluer",
          "/api/dora/incident", "/api/dora/contrat", "/api/dora/supervision")


@pytest.mark.parametrize("panneau", PANNEAUX)
def test_chaque_panneau_existe_a_la_fois_comme_ECRAN_et_comme_ONGLET(panneau):
    """UN ONGLET SANS PANNEAU OUVRE LE VIDE ; un panneau sans onglet est
    inatteignable autrement que par un lien direct."""
    assert 'id="p-%s"' % panneau in SENTINEL, panneau
    assert "go('%s'," % panneau in SENTINEL, (
        "aucun onglet de la barre latérale ne mène à %s" % panneau)


@pytest.mark.parametrize("route", ROUTES)
def test_chaque_route_DORA_existe(route):
    assert "@app.route('%s'" % route in APP, route


def test_DORA_n_est_plus_sans_instrument_et_mene_a_son_ecran():
    """LA NORME A CHANGÉ DE NATURE, ET LE TAUX DOIT MENER QUELQUE PART.
    Un taux qui n'ouvre pas l'écran où on le corrige est un reproche, pas
    un outil."""
    n = conformite.NORMES_PAR_CLE["dora"]
    assert n["nature"] == "obligation", n["nature"]
    assert n["panneau"] == "dora-qualifier"
    assert n["mesure"]
    assert "dora" in conformite.COMPOSITIONS
    assert "dora" in conformite.LECTEURS
    assert "dora" in conformite.ECARTEURS


def test_le_panneau_du_taux_est_un_panneau_DORA_reellement_declare():
    """LA GARDE-FOU DE LA RÈGLE AU-DESSUS : vérifier que le panneau visé
    est dans la table des six, et pas un identifiant plausible qui
    n'existerait nulle part."""
    assert conformite.NORMES_PAR_CLE["dora"]["panneau"] in PANNEAUX


def test_les_six_panneaux_ont_leur_PAGE_META_et_leurs_cles_anglaises():
    """UN PANNEAU SANS PAGE_META N'A NI SECTION NI LIBELLÉ dans le fil
    d'Ariane ; sans clés anglaises, il reste en français sur la version
    anglaise — et rien ne le signale à qui relit le français."""
    for p in PANNEAUX:
        assert "'%s':" % p in PAGEJS, "%s absent de PAGE_META" % p
        for suffixe in ("eb", "h1", "p"):
            cle = "'pg.%s.%s':" % (p, suffixe)
            assert cle in PAGEJS, "clé anglaise manquante : %s" % cle


def test_go_amorce_les_panneaux_DORA_sans_passer_par_le_menu():
    """LE DÉFAUT DÉJÀ MESURÉ SUR LA QUALIFICATION ASSISTÉE, ET QUI SE
    REPRODUIRAIT ICI.

    Le `;doraInit()` écrit dans le `onclick` de la barre latérale ne
    s'exécute PAS quand on arrive par `?goto=`, par un parcours guidé ou
    par un bouton d'un autre écran. Sans la ligne de dispatch, les six
    panneaux s'ouvrent sur un « Chargement… » qui ne finit jamais — et la
    carte DORA de l'accueil mène précisément par `?goto=dora-qualifier`.
    """
    assert re.search(
        r"if \(id\.indexOf\('dora'\) === 0 && typeof window\.doraInit"
        r" === 'function'\) _apresPeinture\(window\.doraInit\);", PAGEJS), (
        "aucun aiguillage `go()` n'amorce les panneaux DORA")
    assert 'href="/sentinel?goto=dora-qualifier"' in _lire("index.html"), (
        "la carte DORA de l'accueil ne mène plus au panneau")


# ══════════════════════════════════════════════════════════════════════════
#  9. LA BATTERIE DE MUTATIONS RESTE BRANCHÉE
# ══════════════════════════════════════════════════════════════════════════

def test_chaque_ancre_de_la_batterie_de_mutations_EXISTE_ENCORE():
    """UNE BATTERIE DONT LES ANCRES ONT GLISSÉ EST UNE BATTERIE INERTE.

    Chaque mutation remplace un fragment de code par un autre ; si le
    fragment n'existe plus — une refonte, un renommage, une indentation qui
    bouge —, la mutation ne modifie RIEN, le banc la voit « survivre », et
    la règle qu'elle éprouvait n'est plus éprouvée par personne. C'est
    arrivé deux fois dans ce dépôt, et les deux fois c'est cette règle qui
    l'a dit.

    ET L'ANCRE DOIT ÊTRE UNIQUE : deux occurrences feraient muter un
    endroit qu'on n'a pas choisi, et le banc mesurerait autre chose que ce
    qu'il annonce.
    """
    import json
    table = json.load(io.open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "mutations_dora.json"), encoding="utf-8"))
    perimees = []
    for m in table["mutations"]:
        src = _lire(m["fichier"])
        n = src.count(m["avant"])
        if n != 1:
            perimees.append("%s — %s : %d occurrence(s)"
                            % (m["fichier"], m["nom"], n))
    assert not perimees, (
        "%d ancre(s) périmée(s) : ces mutations ne modifient plus rien, et "
        "les règles qu'elles éprouvent ne sont plus éprouvées.\n    %s"
        % (len(perimees), "\n    ".join(perimees)))


def test_chaque_mutation_NOMME_une_regle_QUI_EXISTE():
    """UNE MUTATION QUI VISE UNE RÈGLE DISPARUE se compte comme survivante
    pour une raison qui n'a rien à voir avec le code : le banc rendrait un
    échec là où il n'y a qu'un nom périmé."""
    import json
    ici = io.open(os.path.abspath(__file__), encoding="utf-8").read()
    table = json.load(io.open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "mutations_dora.json"), encoding="utf-8"))
    ailleurs = "".join(_lire(os.path.join("tests", f))
                       for f in ("test_conformite.py",
                                 "test_normes_maitrisees.py",
                                 "test_barre_laterale_conformite.py",
                                 "test_guides_sentinel.py",
                                 "test_parcours_couverture.py"))
    for m in table["mutations"]:
        assert ("def %s(" % m["regle"]) in ici + ailleurs, (
            "la mutation « %s » vise %s, qui n'existe dans aucune cible"
            % (m["nom"], m["regle"]))


def test_les_cibles_de_la_batterie_EXISTENT():
    """LE GARDE-FOU DES DEUX RÈGLES CI-DESSUS : un fichier de cible
    renommé ferait lancer le banc sur un périmètre vide, et TOUTES les
    mutations survivraient — un désastre qui ressemblerait à une régression
    du code."""
    import json
    table = json.load(io.open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "mutations_dora.json"), encoding="utf-8"))
    assert table["cibles"], "la batterie ne vise aucun fichier"
    for c in table["cibles"]:
        assert os.path.exists(os.path.join(_RACINE, c)), c


# ══════════════════════════════════════════════════════════════════════════
#  10. LE RYTHME — UN DÉFAUT QUE SEULE LA RECETTE POUVAIT VOIR
# ══════════════════════════════════════════════════════════════════════════

def test_ouvrir_un_ecran_DORA_ne_peint_QUE_cet_ecran():
    """CENT DOUZE APPELS D'API POUR UNE VISITE DU TIROIR, PUIS L'IP BLOQUÉE.

    `doraInit` est accroché aux SIX entrées du menu ET à l'aiguillage de
    `go()`. Une première version peignait les six panneaux à chaque appel :
    chaque changement d'onglet déclenchait six requêtes, la recette en a
    compté cent douze sur une visite ordinaire, et le limiteur a fini par
    bloquer l'adresse — les écrans mouraient l'un après l'autre.

    AUCUNE RÈGLE DE SOURCE NE POUVAIT LE VOIR, parce que le code était
    juste : c'est son RYTHME qui ne l'était pas. Celle-ci le peut, une fois
    le défaut connu — elle mesure qu'aucune fonction n'appelle plus de deux
    des six peintres, et que l'aiguillage regarde l'écran ouvert.
    """
    peintres = ("doraQualifier", "doraPeindreRisque", "doraPeindreTiers",
                "doraPeindreIncident", "doraPeindreIso", "doraPeindreSup")
    debut = PAGEJS.index("function doraPeindreCourant()")
    corps = PAGEJS[debut:PAGEJS.index("\n}", debut)]
    assert ".page.on" in corps, (
        "l'aiguillage ne regarde pas quel écran est ouvert : il ne peut donc "
        "pas se limiter à celui-là")
    # UN SEUL PEINTRE S'EXÉCUTE PAR APPEL, ET C'EST LE `return` QUI LE
    # GARANTIT. L'aiguillage NOMME les six — c'est son travail — mais
    # chaque branche doit rendre la main aussitôt. Une branche sans
    # `return` laisserait couler les suivantes, et le défaut reviendrait
    # sans qu'aucun nom ne change.
    sans_retour = []
    for ligne in corps.splitlines():
        for peintre in peintres:
            if (peintre + "()") in ligne and "return;" not in ligne:
                sans_retour.append(ligne.strip()[:60])
    assert len(sans_retour) <= 1, (
        "%d branches de l'aiguillage appellent un peintre sans rendre la "
        "main : les suivantes s'exécutent aussi, et chacune interroge le "
        "serveur.\n    %s" % (len(sans_retour), "\n    ".join(sans_retour)))

    # ── ET AUCUNE AUTRE FONCTION NE LES ENCHAÎNE. Rétablir un
    #    `doraPeindre()` qui les appelle tous les six ramènerait le défaut
    #    sans toucher à l'aiguillage.
    for bloc in PAGEJS.split("\nfunction "):
        if bloc.startswith("doraPeindreCourant"):
            continue
        appeles = sum(1 for x in peintres if (x + "()") in bloc)
        assert appeles <= 3, (
            "une fonction enchaîne %d des six peintres DORA : c'est le "
            "défaut des cent douze appels qui revient — %r"
            % (appeles, bloc.split("(")[0][:40]))


def test_le_contrat_ne_va_PAS_demander_au_serveur_un_refus_deja_connu():
    """LE REFUS EST CONNU D'AVANCE, ET IL NE SE PAIE PAS D'UN APPEL.

    Tant que la criticité n'est pas déclarée, le moteur refuse — avec un
    400. Aller chercher ce refus à chaque peinture dépensait une requête
    pour apprendre ce que l'écran savait déjà, et la recette a compté ces
    400 par dizaines juste avant le blocage.
    """
    debut = PAGEJS.index("function doraCalculerTiers()")
    corps = PAGEJS[debut:PAGEJS.index("\nwindow.", debut)]
    garde = corps.index("DORA_CONTRAT.fonction_critique === null")
    envoi = corps.index("fetch('/api/dora/contrat'")
    assert garde < envoi, (
        "l'écran interroge le serveur AVANT de vérifier que la criticité "
        "est déclarée : il paie un appel pour un refus qu'il connaît")
