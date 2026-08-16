"""Le pilotage : formes, seuils, alertes — et les trois refus qui comptent.

Ce que ces tests protègent, avec la faute que chacun empêche :

  1. UNE ALERTE NE SE DÉCLENCHE PAS SUR DU BRUIT. Un écart plus petit que
     l'incertitude de la grandeur n'est pas un écart. Alerter quand même
     produit un faux positif — et au troisième, plus personne ne regarde les
     couleurs, y compris quand elles sont justes.
  2. LE CAMEMBERT EST REFUSÉ QUAND IL SE LIRAIT MAL. Au-delà de six parts ou
     sur des parts voisines, l'ordre visuel cesse d'être l'ordre des valeurs :
     le lecteur tire alors une conclusion fausse d'une figure exacte.
  3. LA FLÈCHE NE DÉCORE PAS. Une tendance dessinée sur trois points dont
     deux se valent invente un mouvement.
"""
import os
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import pilotage_dc as p  # noqa: E402


def test_le_referentiel_est_coherent_au_chargement():
    assert p._verifier() == []
    s = p.sante()
    assert s["indicateurs"] == 5 and s["formes"] == 3
    # Chaque indicateur porte son RISQUE : un indicateur sans conséquence
    # nommée est un chiffre de plus sur un écran.
    for i in p.INDICATEURS:
        assert i["risque"] and i["incertitude"] is not None, i["cle"]


def test_une_alerte_ne_se_declenche_pas_dans_l_incertitude():
    """LE CAS CENTRAL. Enveloppe cible 10 000 €/kW, tolérance 10 %,
    incertitude ±30 % : un dépassement de 12 % est RÉEL au regard de la
    tolérance mais reste dans le bruit de la grandeur. Le rouge serait un
    faux positif."""
    r = p.evaluer_seuil(11200, 10000, 0.10, 0.30)
    assert r["etat"] == "indetermine", r["etat"]
    assert r["couleur"] == "gris"
    assert "n'est pas démontré" in r["lecture"]
    assert "Resserrer la mesure" in r["lecture"]

    # La MÊME valeur, sur une grandeur bien mesurée (±2 %), devient une
    # alerte : c'est l'incertitude qui change le verdict, pas l'écart.
    fine = p.evaluer_seuil(11200, 10000, 0.10, 0.02)
    assert fine["etat"] in ("surveiller", "alerte")
    assert fine["couleur"] in ("orange", "rouge")


def test_le_rouge_exige_de_depasser_tolerance_ET_incertitude():
    grand = p.evaluer_seuil(18000, 10000, 0.10, 0.30)   # +80 %
    assert grand["etat"] == "alerte" and grand["couleur"] == "rouge"
    assert "pas du bruit" in grand["lecture"]
    moyen = p.evaluer_seuil(14500, 10000, 0.10, 0.30)   # +45 %
    assert moyen["etat"] == "surveiller"


def test_le_sens_de_l_indicateur_decide_du_bon_cote():
    """Un dépassement de coût est mauvais ; un dépassement de rendement est
    bon. Déduire le sens du signe de l'écart alerterait sur les bonnes
    nouvelles."""
    cout = p.evaluer_seuil(180, 100, 0.05, 0.02, sens="bas_bon")
    rendement = p.evaluer_seuil(180, 100, 0.05, 0.02, sens="haut_bon")
    assert cout["etat"] == "alerte"
    assert rendement["etat"] == "conforme"
    # …et symétriquement.
    assert p.evaluer_seuil(40, 100, 0.05, 0.02, sens="haut_bon")["etat"] == "alerte"
    assert p.evaluer_seuil(40, 100, 0.05, 0.02, sens="bas_bon")["etat"] == "conforme"


def test_le_camembert_est_refuse_au_dela_de_six_parts():
    ok = p.choisir_forme("parts", 4, [50, 25, 15, 10])
    assert ok["forme"] == "camembert" and ok["impose"] is False
    trop = p.choisir_forme("parts", 8, [20, 18, 16, 14, 12, 10, 6, 4])
    assert trop["forme"] == "histogramme" and trop["impose"] is True
    assert str(p.CAMEMBERT_PARTS_MAX) in trop["pourquoi"]


def test_le_camembert_est_refuse_quand_les_parts_sont_proches():
    """Deux angles voisins ne se classent pas à l'œil : la figure serait
    exacte et sa lecture fausse."""
    r = p.choisir_forme("parts", 4, [30, 29, 21, 20])
    assert r["forme"] == "histogramme" and r["impose"] is True
    assert "trop proches" in r["pourquoi"]
    assert "l'ordre visuel cesse d'être l'ordre des valeurs" in r["pourquoi"]
    # …et le seuil est bien celui du référentiel, pas un chiffre en dur.
    ecart = p.CAMEMBERT_ECART_MIN
    distinct = [100.0, 100.0 * (1 - ecart * 2), 20, 10]
    assert p.choisir_forme("parts", 4, distinct)["forme"] == "camembert"


def test_la_forme_suit_la_nature_de_la_donnee():
    assert p.choisir_forme("temps", 12)["forme"] == "courbe"
    assert p.choisir_forme("categories", 4)["forme"] == "histogramme"
    # Deux points ne font pas une tendance : la courbe est refusée.
    court = p.choisir_forme("temps", 2)
    assert court["forme"] == "histogramme" and court["impose"] is True
    assert "n'a aucun sens" in court["pourquoi"]


def test_la_fleche_reste_plate_quand_la_pente_est_dans_le_bruit():
    plat = p.tendance([10, 12, 9, 11, 10])
    assert plat["fleche"] == "→" and plat["sens"] == "stable"
    assert "ne sort pas du bruit" in plat["lecture"]
    haut = p.tendance([10, 12, 14, 17, 20], sens="haut_bon")
    assert haut["fleche"] == "↗" and haut["favorable"] is True
    # La MÊME série, sur un indicateur où monter est mauvais.
    cout = p.tendance([10, 12, 14, 17, 20], sens="bas_bon")
    assert cout["fleche"] == "↗" and cout["favorable"] is False
    # Moins de trois points : aucune tendance, et la flèche le dit.
    court = p.tendance([10, 20])
    assert court["sens"] == "indeterminee" and court["fleche"] == "→"


def test_le_pilotage_ne_promet_pas_ce_que_la_maturite_ne_tient_pas():
    """La jonction avec le diagnostic : à niveau 0, aucune alerte automatique
    n'est tenable — et le module ne les émet donc pas, au lieu de les
    afficher et de laisser l'organisation découvrir qu'elles n'arrivent
    jamais."""
    mesures = {"enveloppe_kw": {"valeur": 25000, "cible": 10000}}
    bas = p.piloter(mesures, niveau_maturite=0)
    assert bas["alertes"] == []
    assert bas["tenable"]["alertes"] is False
    assert "ne peut pas être franchi" in bas["tenable"]["dit"]

    moyen = p.piloter(mesures, niveau_maturite=1)
    assert len(moyen["alertes"]) == 1
    assert moyen["alertes"][0]["notifiable"] is False
    assert "prochaine revue" in moyen["alertes"][0]["quand"]

    haut = p.piloter(mesures, niveau_maturite=3)
    assert haut["alertes"][0]["notifiable"] is True
    assert "franchissement" in haut["alertes"][0]["quand"]

    # Sans diagnostic, on ne suppose rien.
    inconnu = p.piloter(mesures)
    assert inconnu["alertes"] == []
    assert "n'a pas été diagnostiquée" in inconnu["tenable"]["dit"]


def test_un_tableau_vide_le_dit_au_lieu_de_paraitre_piloter():
    d = p.piloter({}, niveau_maturite=2)
    assert "Aucune mesure saisie" in d["lecture"]
    assert "premier pas vers son abandon" in d["lecture"]
    assert all(c["valeur"] is None for c in d["indicateurs"])


def test_le_pilotage_compte_les_ecarts_non_demontres_a_part():
    """Un écart dans l'incertitude n'est ni une alerte ni un silence : il se
    compte séparément, sinon il disparaît du compte rendu."""
    d = p.piloter({"enveloppe_kw": {"valeur": 11200, "cible": 10000}},
                  niveau_maturite=2)
    assert d["alertes"] == []
    assert "Aucune alerte démontrée" in d["lecture"]
    assert "reste dans l'incertitude" in d["lecture"]
    assert "colorer en rouge serait une fausse alerte" in d["lecture"]
    # L'écart est bien COMPTÉ, pas seulement mentionné : il porte son état.
    env = [c for c in d["indicateurs"] if c["cle"] == "enveloppe_kw"][0]
    assert env["seuil"]["etat"] == "indetermine"
    # …et un indicateur sans mesure n'est pas confondu avec un écart nul.
    autres = [c for c in d["indicateurs"] if c["cle"] != "enveloppe_kw"]
    assert all(c["seuil"]["etat"] == "non_mesure" for c in autres)


def test_le_garde_TOMBE_sur_un_indicateur_sans_risque():
    sauve = p.INDICATEURS[0]["risque"]
    try:
        p.INDICATEURS[0]["risque"] = ""
        assert any("sans risque déclaré" in f for f in p._verifier())
    finally:
        p.INDICATEURS[0]["risque"] = sauve
    assert p._verifier() == []


# ── LES TROIS APPORTS DE L'ANALYSE AUGMENTÉE, SANS MODÈLE DE LANGAGE ──────
# Prédiction, détection d'anomalies, explication. Ce que ces tests
# protègent : chacune doit pouvoir être REFAITE ou CONTESTÉE par un lecteur.
# Une projection qu'on ne peut pas recalculer et un commentaire qui peut
# inventer une cause ne s'annexent pas à un dossier d'investissement.

def test_la_projection_REFUSE_ce_qui_serait_une_invention():
    court = p.predire([10, 11, 12])
    assert court["possible"] is False
    assert "opinion avec des décimales" in court["motif"]
    # Horizon trop long pour l'historique : extrapolation, pas prévision.
    loin = p.predire([10, 11, 12, 13, 14, 15], horizon=5)
    assert loin["possible"] is False
    assert "extrapolation" in loin["motif"]
    assert "Allonger l'historique" in loin["motif"]


def test_la_projection_est_refaisable_a_la_main():
    """Une série parfaitement linéaire doit rendre exactement sa pente : si
    le calcul dérive ici, personne ne pourra le vérifier ailleurs."""
    r = p.predire([10, 12, 14, 16, 18], horizon=1)
    assert r["possible"] is True
    assert abs(r["pente"] - 2.0) < 1e-6
    assert abs(r["points"][0]["valeur"] - 20.0) < 1e-6
    # Série sans bruit : l'intervalle est nul, et c'est juste.
    assert r["sigma_residus"] == 0
    assert "se refait à la main" in r["methode"]
    # Ce qu'elle NE connaît PAS est dit — pas de fausse promesse multivariée.
    assert "variables explicatives" in r["variables_manquantes"]


def test_l_intervalle_s_elargit_avec_l_horizon():
    """Une prévision honnête est moins sûre à trois points qu'à un. Un
    intervalle constant le cacherait."""
    r = p.predire([10, 13, 11, 15, 14, 18, 17, 21], horizon=4)
    assert r["possible"] is True
    marges = [pt["marge"] for pt in r["points"]]
    assert marges == sorted(marges), marges
    assert marges[-1] > marges[0]


def test_la_dispersion_excessive_est_DITE_pas_masquee():
    r = p.predire([10, 90, 15, 85, 20, 80], horizon=2)
    assert r["possible"] is True
    assert "ATTENTION" in r["lecture"]
    assert "sert à surveiller" in r["lecture"]


def test_l_anomalie_distingue_valeur_aberrante_et_rupture():
    """Deux choses différentes, deux actions différentes : vérifier une
    saisie n'est pas expliquer un changement de régime."""
    ab = p.detecter_anomalies([10, 11, 10, 45, 11, 10, 11])
    assert len(ab["aberrantes"]) == 1
    assert ab["aberrantes"][0]["valeur"] == 45
    assert "vérifier" in ab["aberrantes"][0]["pourquoi"].lower()
    assert ab["rupture"] is None

    rup = p.detecter_anomalies([10, 11, 12, 13, 20, 28, 37, 47])
    assert rup["rupture"] is not None
    assert rup["rupture"]["nature"] in ("accélération", "inversion")
    assert "changement de régime" in rup["rupture"]["pourquoi"]
    assert "VÉRIFICATION" in rup["lecture"] or "EXPLICATION" in rup["lecture"]


def test_l_anomalie_emploie_le_MAD_et_dit_pourquoi():
    """L'écart-type est gonflé par l'anomalie qu'on cherche : une valeur
    extrême élève son propre seuil et finit par passer. Le MAD ne bouge pas."""
    r = p.detecter_anomalies([10, 10, 10, 10, 10, 10, 200])
    assert len(r["aberrantes"]) == 1, r["aberrantes"]
    assert "MAD" in r["methode"] and "gonflé par l'anomalie" in r["methode"]
    # Série sans anomalie : rien n'est signalé, et c'est dit.
    calme = p.detecter_anomalies([10, 11, 10, 12, 11, 10])
    assert not calme["aberrantes"] and calme["rupture"] is None
    assert "Aucune anomalie" in calme["lecture"]


def test_l_anomalie_refuse_de_juger_une_serie_trop_courte():
    r = p.detecter_anomalies([10, 40])
    assert r["possible"] is False
    assert "début d'une tendance" in r["motif"]


def test_l_explication_ne_peut_affirmer_que_ce_qui_est_mesure():
    """Le point qui rend le commentaire annexable : il est COMPOSÉ depuis les
    grandeurs calculées, pas généré. Il pose les causes en question."""
    d = p.piloter({"pue_constate": {"valeur": 1.45, "cible": 1.25,
                                    "serie": [1.28, 1.30, 1.31, 1.38, 1.45]}},
                  niveau_maturite=2)
    c = [x for x in d["indicateurs"] if x["cle"] == "pue_constate"][0]
    t = c["explication"]
    assert "sans modèle de langage" in t
    assert "1.45" in t and "1.25" in t          # les valeurs mesurées
    assert c["risque"][:30] in t                 # le risque du référentiel
    # Déterminisme : deux appels, même texte au caractère près.
    d2 = p.piloter({"pue_constate": {"valeur": 1.45, "cible": 1.25,
                                     "serie": [1.28, 1.30, 1.31, 1.38, 1.45]}},
                   niveau_maturite=2)
    c2 = [x for x in d2["indicateurs"] if x["cle"] == "pue_constate"][0]
    assert c2["explication"] == t


def test_l_explication_pose_les_causes_en_QUESTION():
    """Une rupture détectée ne s'explique pas toute seule : le commentaire
    demande l'événement, il ne l'invente pas."""
    d = p.piloter({"delai_raccordement": {
        "valeur": 30, "cible": 18,
        "serie": [12, 13, 14, 15, 22, 27, 30, 34]}}, niveau_maturite=2)
    c = [x for x in d["indicateurs"] if x["cle"] == "delai_raccordement"][0]
    t = c["explication"]
    assert "rupture de tendance" in t
    assert "pourrait l'expliquer ?" in t, t
    assert "parce que" not in t.lower(), "une cause a été affirmée"


def test_l_explication_d_un_indicateur_non_mesure_ne_decrit_pas_un_vide():
    d = p.piloter({}, niveau_maturite=2)
    for c in d["indicateurs"]:
        assert "n'est pas mesuré" in c["explication"]
        assert "décrirait un vide" in c["explication"]


def test_les_trois_apports_sont_branches_sur_chaque_carte():
    d = p.piloter({"avancement_etudes": {
        "valeur": 62, "cible": 80, "serie": [10, 25, 38, 50, 62], "horizon": 2}},
        niveau_maturite=2)
    c = [x for x in d["indicateurs"] if x["cle"] == "avancement_etudes"][0]
    assert c["anomalies"]["possible"] is True
    assert c["prediction"]["possible"] is True
    assert len(c["prediction"]["points"]) == 2
    assert c["explication"]
