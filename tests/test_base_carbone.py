"""LA BASE CARBONE ADEME — lue sur le fichier, et elle ne remplace rien.

POURQUOI CES CONTRÔLES. Verser une base réglementaire au dépôt crée deux
tentations opposées, et les deux sont des fautes :

  — la recopier dans du code Python, où elle se démodera sans que personne
    ne le voie ;
  — l'employer PARTOUT parce qu'elle est réglementaire, y compris là où son
    millésime la rend fausse.

Mesuré à l'intégration : les facteurs d'électricité étrangère de la v22.0
portent une validité de décembre 2017 (décembre 2019 pour six pays), quand la
table employée suit Ember 2024. Écart médian 41,7 % sur 31 pays. Substituer
rendrait le calcul MOINS juste pour un usage 2026, et plus juste pour un bilan
réglementaire français. Le module sert donc les deux et refuse de trancher.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import base_carbone as BC


def test_la_base_est_bien_versee_au_depot():
    assert BC.disponible(), "le fichier ADEME n'est pas dans donnees/ademe/"
    s = BC.sante()
    assert s["lignes"] > 10000, "%d lignes lues" % s["lignes"]


def test_les_facteurs_sont_LUS_et_non_recopies():
    """Aucune valeur d'électricité n'est écrite dans ce module : elles viennent
    toutes du fichier. Un facteur recopié cesserait d'être vrai à la première
    version de la base, sans que rien ne le signale."""
    src = open(os.path.join(os.path.dirname(BC.__file__), "base_carbone.py"),
               encoding="utf-8").read()
    # Le code cite des valeurs dans SA DOCUMENTATION — c'est du commentaire.
    # Ce qu'on interdit, c'est une table de facteurs dans le code exécuté.
    code = "\n".join(l for l in src.splitlines()
                     if not l.strip().startswith("#"))
    for interdit in ('"FR": 79', "'FR': 79", '"DE": 461', "'DE': 461"):
        assert interdit not in code, "facteur recopié : %s" % interdit


def test_les_deux_frontieres_sont_distinguees():
    """« consommation » intègre les importations, « production » non. Les
    confondre fausse tout pour un pays importateur."""
    e = BC.electricite()
    lt = e.get("LT") or {}
    assert "production" in lt and "consommation" in lt
    # Mesuré : la Lituanie importe massivement — l'écart dépasse le facteur deux.
    assert lt["production"]["g_kwh"] > lt["consommation"]["g_kwh"] * 1.5


def test_chaque_facteur_porte_son_millesime_et_son_incertitude():
    e = BC.electricite()
    sans = [p for p, v in e.items()
            for f in v.values() if not f.get("incertitude_pct")]
    assert not sans, "facteurs sans incertitude : %s" % sorted(set(sans))[:5]
    dates = [f.get("validite") for v in e.values() for f in v.values()]
    assert any(d and "17" in d for d in dates), "aucun millésime 2017 trouvé"


def test_un_pays_absent_est_ABSENT_jamais_estime():
    """Le refus plutôt que l'invention : un pays hors base doit le dire."""
    assert BC.facteur("XX") is None
    c = BC.comparer("XX", 100)
    assert c["connu"] is False
    assert "ne figure pas" in c["dit"]


def test_LE_POINT_QUI_DECIDE_la_comparaison_ne_rend_pas_un_verdict():
    """Elle mesure un écart et nomme l'usage de chaque référence. Rendre
    « juste / faux » ferait croire qu'une des deux est à jeter."""
    c = BC.comparer("FR", 45)
    assert c["connu"] is True
    assert c["ademe_g_kwh"] > 70          # lu du fichier, pas écrit ici
    assert "Aucune des deux n'est fausse" in c["dit"]
    assert "bilan réglementaire français" in c["dit"]
    assert "décrit le réseau de l'année en cours" in c["dit"]


def test_la_confrontation_publie_la_MEDIANE_et_dit_ce_qui_deforme_la_moyenne():
    """La moyenne des écarts relatifs est détruite par un dénominateur quasi
    nul : l'Islande est à 0,2 gCO2e/kWh, son écart relatif vaut 14 900 % et
    tirait la moyenne de 42 à 522 %."""
    import empreinte_sites
    r = BC.confronter(empreinte_sites.INTENSITE)
    assert r["ecart_median_pct"] is not None
    assert r["ecart_median_pct"] < r["ecart_moyen_pct"]
    assert r["references_quasi_nulles"], "aucune référence quasi nulle repérée"
    assert "MÉDIAN" in r["lecture"]
    assert "sans portée" in r["lecture"]


def test_l_ecart_avec_notre_table_est_REEL_et_explique_par_le_millesime():
    """Sans écart, tout ce dispositif n'aurait rien à dire — et le contrôle
    passerait sans rien prouver."""
    import empreinte_sites
    r = BC.confronter(empreinte_sites.INTENSITE)
    assert r["pays_compares"] >= 25
    assert r["ecart_median_pct"] > 20, "écart médian %s %%" % r["ecart_median_pct"]


def test_LA_PHRASE_DIT_CE_QUE_LE_CALCUL_CALCULE_meme_denominateur():
    """LE DÉFAUT MESURÉ, ET IL ÉTAIT PUBLIÉ.

    L'écart est calculé en rapportant la valeur employée au facteur ADEME :
    (employé − ADEME) / ADEME. La phrase, elle, prenait le facteur ADEME pour
    sujet et la valeur employée pour référence — l'inverse. Deux conséquences,
    toutes deux constatées sur des chiffres réels :

      — sur l'Islande, « le facteur ADEME est INFÉRIEUR DE 14 900 % » : un
        manque plafonne à 100 %, l'énoncé était impossible ;
      — sur la France, la phrase annonçait 43 % là où sa propre grammaire —
        un écart rapporté à la valeur employée — valait 76 %.

    Ce contrôle reconstruit le pourcentage à partir des DEUX nombres que la
    phrase cite, et exige qu'il retombe sur celui qu'elle annonce."""
    import re
    import empreinte_sites
    for pays, employe in sorted(empreinte_sites.INTENSITE.items()):
        c = BC.comparer(pays, employe)
        if not c["connu"]:
            continue
        dit = c["dit"]
        m = re.search(r"\(([\d.,]+) gCO2e/kWh\).*?(supérieure|inférieure) de "
                      r"([\d.,]+) %.*?\(([\d.,]+) gCO2e/kWh", dit)
        assert m, "phrase illisible pour %s : %s" % (pays, dit)
        sujet = float(m.group(1).replace(",", "."))
        sens = m.group(2)
        pct = float(m.group(3).replace(",", "."))
        reference = float(m.group(4).replace(",", "."))
        # 1. UN MANQUE PLAFONNE À 100 %. Un dépassement, non.
        assert not (sens == "inférieure" and pct > 100), (
            "%s : « inférieure de %s %% » est impossible — %s" % (pays, pct, dit))
        # 2. LE SENS ANNONCÉ EST CELUI DES NOMBRES CITÉS.
        if sujet > reference:
            assert sens == "supérieure", "%s : %s > %s mais « %s »" % (
                pays, sujet, reference, sens)
        elif sujet < reference:
            assert sens == "inférieure", "%s : %s < %s mais « %s »" % (
                pays, sujet, reference, sens)
        # 3. LE POURCENTAGE SE RECALCULE SUR LES NOMBRES DE LA PHRASE.
        attendu = abs(sujet - reference) / reference * 100.0
        assert abs(attendu - pct) <= 1.0, (
            "%s : la phrase annonce %s %% ; ses deux nombres donnent %.0f %% — %s"
            % (pays, pct, attendu, dit))
        # 4. …ET C'EST BIEN L'ÉCART PUBLIÉ DANS LA DONNÉE.
        assert abs(abs(c["ecart_pct"]) - pct) <= 1.0, (
            "%s : donnée %s %%, phrase %s %%" % (pays, c["ecart_pct"], pct))


def test_le_registre_de_verification_porte_le_constat():
    import factcheck
    c = factcheck.par_cle("ademe_base_carbone")
    assert c is not None
    assert "millésime" in c["constat"]
    assert "BEGES" in c["constat"]
    assert factcheck.recoupement(c)["recoupe"] is True
