# -*- coding: utf-8 -*-
"""LE CYBER RESILIENCE ACT — ce que ces règles MESURENT.

LA DISCIPLINE. Aucune de ces règles ne vérifie « le module répond ». Un module
réglementaire qui répond sans rien décider est un dépliant : ce qui compte est
qu'il TRANCHE, et que ce qu'il tranche change avec les faits. Chaque règle
compare donc deux états du même produit et exige que la réponse diffère — ou
qu'elle ne diffère PAS, là où le règlement ne fait pas de différence.

CE QU'ELLES GARDENT DE PARTICULIER. Le CRA est le premier texte de la
plateforme dont une obligation est DÉJÀ applicable : l'article 14 depuis le
11 septembre 2026. Une règle qui le vérifierait sur l'horloge de la machine
passerait aujourd'hui et aurait échoué la veille, sans qu'une ligne de code
ait bougé. La date est donc injectée partout.
"""
import io
import os
import re

import pytest

import cra


ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _fichier(nom):
    return io.open(os.path.join(ICI, nom), encoding="utf-8").read()


# ═══════════════════════════════════════════════════════════════════════════
#  1. LA BASCULE DE LA CLASSE I — LA RÈGLE QUI PORTE LE MODULE
# ═══════════════════════════════════════════════════════════════════════════

def test_la_classe_I_bascule_chez_l_organisme_notifie_sur_UN_SEUL_fait():
    """L'article 32, §2 en une mesure.

    Le même produit, la même classe, et un seul fait qui change : les normes
    harmonisées sont-elles INTÉGRALEMENT appliquées ? D'un côté le contrôle
    interne — quelques semaines. De l'autre un organisme notifié — un budget
    et plusieurs mois. C'est la bascule la plus coûteuse du règlement.
    """
    base = {"nom": "Passerelle VPN", "marche_ue": True, "classe": "important_i"}
    avec = cra.evaluer_produit(dict(base, normes_harmonisees=True))
    sans = cra.evaluer_produit(dict(base, normes_harmonisees=False))

    assert [r["cle"] for r in avec["routes"]] == ["A"]
    assert avec["organisme_notifie"] is False
    assert sorted(r["cle"] for r in sans["routes"]) == ["B+C", "H"]
    assert sans["organisme_notifie"] is True


def test_ce_fait_ne_change_RIEN_pour_les_autres_classes():
    """CE QUI DONNE SON SENS À LA RÈGLE PRÉCÉDENTE.

    Sans elle, un moteur qui ferait dépendre TOUTES les classes des normes
    harmonisées passerait le premier essai. Or le règlement ne pose cette
    condition que pour la classe I : un produit de classe II va chez
    l'organisme notifié quoi qu'il applique, et un produit ordinaire n'y va
    jamais.
    """
    for classe in ("ordinaire", "important_ii", "critique"):
        avec = cra.procedures_ouvertes(classe, True)
        sans = cra.procedures_ouvertes(classe, False)
        assert avec == sans, \
            "la classe « %s » ne devrait pas dépendre des normes harmonisées " \
            "(%s vs %s)" % (classe, avec, sans)


def test_la_bascule_est_NOMMEE_quand_elle_existe_et_seulement_la():
    """Dire « vous passez par un organisme notifié » ferme la discussion.
    Dire « vous y passez PARCE QUE, et vous n'y passeriez pas sinon » ouvre un
    chantier chiffrable — c'est le seul apport de ce champ."""
    i = cra.evaluer_produit({"nom": "X", "marche_ue": True,
                             "classe": "important_i"})
    assert i["bascule"] is not None
    assert "art. 32" in i["bascule"]["article"]
    for classe in ("ordinaire", "important_ii", "critique"):
        r = cra.evaluer_produit({"nom": "X", "marche_ue": True, "classe": classe})
        assert r["bascule"] is None, \
            "une bascule est annoncée pour « %s », où elle n'existe pas" % classe


def test_un_produit_ordinaire_ne_voit_JAMAIS_d_organisme_notifie():
    for h in (True, False):
        r = cra.procedures_ouvertes("ordinaire", h)
        assert r == ["A"]
        assert not any(cra.PROCEDURES[x]["organisme_notifie"] for x in r)


# ═══════════════════════════════════════════════════════════════════════════
#  2. LE CALENDRIER — ET CE QUI EST DÉJÀ EN VIGUEUR
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("jour,attendu", [
    ("2026-06-10", []),
    ("2026-06-11", ["ch4"]),
    ("2026-09-10", ["ch4"]),
    ("2026-09-11", ["ch4", "art14"]),
    ("2027-12-10", ["ch4", "art14"]),
    ("2027-12-11", ["ch4", "art14", "general"]),
])
def test_le_calendrier_bascule_AU_JOUR_DIT(jour, attendu):
    """LA DATE EST INJECTÉE, ET C'EST LE POINT.

    Une règle qui lirait l'horloge de la machine passerait aujourd'hui et
    aurait échoué le 10 septembre, sans qu'une ligne de code ait bougé. Les
    six bornes ci-dessus encadrent chaque date à un jour près : la veille et
    le jour même.
    """
    c = cra.calendrier(jour)
    assert [e["cle"] for e in c["en_vigueur"]] == attendu


def test_l_article_14_est_en_vigueur_et_le_module_le_DIT_en_tete():
    """Le discours courant parle de « l'échéance de décembre 2027 ». Un
    fabricant qui attend 2027 et découvre aujourd'hui une vulnérabilité
    exploitée a vingt-quatre heures pour alerter, et il l'ignore."""
    c = cra.calendrier("2026-09-18")
    art14 = next(e for e in c["echeances"] if e["cle"] == "art14")
    assert art14["applicable"] is True
    assert art14["jours"] == 7
    general = next(e for e in c["echeances"] if e["cle"] == "general")
    assert general["applicable"] is False


# ═══════════════════════════════════════════════════════════════════════════
#  3. LE PÉRIMÈTRE — ET CE QUI NE SE COCHE PAS
# ═══════════════════════════════════════════════════════════════════════════

def test_hors_marche_de_l_union_le_reglement_ne_s_applique_pas():
    r = cra.evaluer_produit({"nom": "X", "marche_ue": False,
                             "classe": "important_ii"})
    assert r["perimetre"]["dans"] is False
    assert r["perimetre"]["motif"] == "hors_marche_ue"
    # ET LE MOTIF DIT POURQUOI LA RÉPONSE PEUT CHANGER DEMAIN : c'est le
    # produit qui décide, pas le lieu d'établissement.
    assert "produit" in r["perimetre"]["dit"].lower()


def test_une_exclusion_sectorielle_sort_du_perimetre_mais_reste_une_question_de_DROIT():
    r = cra.evaluer_produit({"nom": "Pompe à perfusion", "marche_ue": True,
                             "exclusions": ["medical"]})
    assert r["perimetre"]["dans"] is False
    assert [e["cle"] for e in r["perimetre"]["exclusions"]] == ["medical"]
    assert "droit" in r["perimetre"]["dit"].lower()


def test_la_clause_generale_n_est_PAS_une_case_a_cocher():
    """Les sept exclusions se constatent ; celle-ci s'apprécie texte contre
    texte. La mêler aux autres aurait laissé croire qu'un produit sort du CRA
    parce qu'un commercial a coché une case."""
    assert cra.CLAUSE_GENERALE["cle"] not in {e["cle"] for e in cra.EXCLUSIONS}
    # ET LA COCHER NE SORT PAS DU PÉRIMÈTRE.
    r = cra.evaluer_produit({"nom": "X", "marche_ue": True,
                             "exclusions": ["autre_droit_union"]})
    assert r["perimetre"]["dans"] is True


def test_un_produit_hors_perimetre_ne_recoit_PAS_les_delais_de_signalement():
    """Servir le compte à rebours de l'article 14 à un dispositif médical
    exclu ferait courir une obligation qui n'existe pas."""
    dedans = cra.evaluer_produit({"nom": "A", "marche_ue": True})
    dehors = cra.evaluer_produit({"nom": "B", "marche_ue": True,
                                  "exclusions": ["aviation"]})
    assert dedans["signalement"] is not None
    assert dehors["signalement"] is None


# ═══════════════════════════════════════════════════════════════════════════
#  4. L'ANALYSE D'ÉCART — UNE CASE VIDE N'EST PAS UNE CASE VERTE
# ═══════════════════════════════════════════════════════════════════════════

def test_une_exigence_NON_RENSEIGNEE_n_entre_pas_au_numerateur():
    """Un tableau qui compte les vides comme verts rend le taux qu'on montre
    en comité et qui se défait au premier audit."""
    r = cra.evaluer_produit({"nom": "X", "marche_ue": True,
                             "ecarts": {"ei-01": "conforme",
                                        "ei-02": "conforme",
                                        "ei-03": "conforme"}})
    e = r["ecarts"]
    assert e["total"] == 21
    assert e["conformes"] == 3
    assert e["non_renseigne"] == 18
    assert e["taux"] == 14, "trois conformes sur vingt et une ne font pas %s %%" % e["taux"]


def test_sans_objet_sort_du_denominateur_mais_non_renseigne_y_reste():
    """LA DISTINCTION QUI FAIT LA DIFFÉRENCE ENTRE UN OUTIL ET UN HABILLAGE.
    « Sans objet » est une décision motivée : l'exigence ne concerne pas ce
    produit. « Non renseigné » est une absence de décision. Les traiter pareil
    permettrait d'atteindre 100 % en ne répondant à rien."""
    tout_so = {c: "sans_objet" for c, _n, _d in cra.ANNEXE_I_I}
    tout_so["gv-01"] = "conforme"
    e = cra.evaluer_produit({"nom": "X", "marche_ue": True,
                             "ecarts": tout_so})["ecarts"]
    assert e["retenus"] == 21 - 13, "les « sans objet » ne sortent pas du dénominateur"
    assert e["non_renseigne"] == 7
    assert e["taux"] != 100, "un taux de 100 %% avec sept lignes vides"


def test_les_deux_parties_de_l_annexe_I_sont_TENUES_A_PART():
    """La partie I se vérifie sur une version du produit, la partie II sur
    l'organisation du fabricant, pendant toute la période d'assistance. Les
    fondre rendrait une analyse fausse — et c'est le cas le plus courant qu'un
    produit soit conforme partie I et l'entreprise défaillante partie II."""
    e = cra.evaluer_produit({"nom": "X", "marche_ue": True})["ecarts"]
    assert [x["partie"] for x in e["parties"]] == ["I", "II"]
    assert len(e["parties"][0]["lignes"]) == 13
    assert len(e["parties"][1]["lignes"]) == 8
    for x in e["parties"]:
        assert x["quoi"].strip(), "une partie ne dit pas sur quoi elle se vérifie"


# ═══════════════════════════════════════════════════════════════════════════
#  5. LE PARC — CE QUI COMMANDE N'EST PAS LA MOYENNE
# ═══════════════════════════════════════════════════════════════════════════

def test_un_seul_produit_de_classe_II_commande_TOUT_LE_PARC():
    """Un fabricant de quarante produits dont un seul relève de la classe II
    n'a pas « 2,5 % de son parc chez l'organisme notifié » : il a un
    calendrier d'organisme notifié, point."""
    parc = [{"nom": "P%d" % i, "marche_ue": True, "classe": "ordinaire"}
            for i in range(39)]
    parc.append({"nom": "Hyperviseur", "marche_ue": True,
                 "classe": "important_ii"})
    r = cra.evaluer_parc(parc)
    assert r["commande"]["nom"] == "Hyperviseur"
    assert r["organisme_notifie"] == 1
    moyenne = 100.0 / len(parc)
    assert moyenne < 3, "le parc d'essai ne rend plus la moyenne trompeuse"
    assert "calendrier" in r["dit"]


def test_le_parc_refuse_deux_produits_du_MEME_nom():
    """Deux lignes homonymes se recouvrent en silence dans tout rapport : on
    croit en coter deux, on en cote une."""
    r = cra.evaluer_parc([{"nom": "A", "marche_ue": True},
                          {"nom": "A", "marche_ue": True}])
    assert r["ok"] is False and r["motif"] == "noms_en_double"


def test_un_produit_hors_perimetre_ne_compte_pas_dans_le_parc_mais_est_NOMME():
    """Le retirer en silence ferait disparaître du rapport un produit que
    quelqu'un a pris la peine de déclarer — et l'on ne saurait plus s'il a été
    examiné ou oublié."""
    r = cra.evaluer_parc([{"nom": "Dedans", "marche_ue": True},
                          {"nom": "Dehors", "marche_ue": False}])
    assert r["cotes"] == 1
    assert [x["nom"] for x in r["hors_perimetre"]] == ["Dehors"]


# ═══════════════════════════════════════════════════════════════════════════
#  6. L'ARTICLE 14 — LES DÉLAIS, ET LE DOUBLE DESTINATAIRE
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("cle", ["vulnerabilite", "incident"])
def test_les_deux_premiers_delais_sont_24h_puis_72h_des_DEUX_cotes(cle):
    d = [e["delai_h"] for e in cra.SIGNALEMENT[cle]["etapes"]]
    assert d[0] == 24 and d[1] == 72


def test_le_rapport_final_DIFFERE_entre_vulnerabilite_et_incident():
    """CE QUI SE CONFOND, ET COÛTE. Les deux premiers délais sont identiques ;
    le troisième ne l'est pas — quatorze jours après la mise à disposition
    d'un correctif d'un côté, un mois après la notification de l'autre. Un
    module qui les alignerait ferait rater une échéance."""
    v = cra.SIGNALEMENT["vulnerabilite"]["etapes"][2]
    i = cra.SIGNALEMENT["incident"]["etapes"][2]
    assert v["delai_h"] == 14 * 24
    assert i["delai_h"] == 30 * 24
    assert v["depuis"] != i["depuis"], \
        "les deux rapports finaux partent du même point : ils ne le font pas"


def test_la_notification_part_aux_DEUX_destinataires_simultanement():
    """Prévenir le CSIRT puis l'ENISA, ou l'un seulement, n'est pas ce que le
    texte demande — et c'est l'erreur la plus facile à commettre sous la
    pression des vingt-quatre heures."""
    d = cra.DESTINATAIRES["dit"]
    assert "CSIRT" in d and "ENISA" in d
    assert "SIMULTAN" in d.upper()
    assert "art. 16" in cra.DESTINATAIRES["article"]


# ═══════════════════════════════════════════════════════════════════════════
#  7. LE MODULE NE SE CONFOND AVEC AUCUN DES DEUX AUTRES
# ═══════════════════════════════════════════════════════════════════════════

def test_le_CRA_a_SON_groupe_de_premier_niveau_dans_la_barre_laterale():
    """POURQUOI CETTE RÈGLE EXISTE. Ranger le CRA sous « Cartographier » ou
    dans le registre IA aurait été plus rapide et aurait forcé une identité
    fausse : le CRA compte des PRODUITS, l'IA Act des SYSTÈMES D'IA, le RGPD
    des TRAITEMENTS. Un fabricant n'est ni un fournisseur ni un responsable de
    traitement."""
    h = _fichier("sentinel.html")
    assert 'data-grp="cra"' in h
    assert re.search(r'<div class="sb-section" data-grp="cra">.*?'
                     r'<span>CRA[^<]*</span>', h, re.S), \
        "le CRA n'a pas de section propre dans la barre latérale"
    items = re.findall(r'<div class="sb-item" data-grp="cra"', h)
    assert len(items) == 3, "%d vue(s) CRA au lieu de trois" % len(items)


def _ecran_cra():
    """CE QUE LES VUES CRA CONTIENNENT — ET RIEN D'AUTRE.

    ═══ POURQUOI LA POPULATION EST RESTREINTE, ET CE QUE ÇA A CORRIGÉ ════
    La première version balayait sentinel.html et sentinel.page.js ENTIERS.
    Elle a signalé « Minimisation des données » — qui est un terme du RGPD
    (art. 5.1.c), présent dans ce fichier depuis longtemps et sans le moindre
    rapport avec le CRA. La règle tombait donc pour une raison sans rapport
    avec ce qu'elle prétend garder, et l'aurait fait tant qu'un mot du CRA
    aurait un homonyme ailleurs dans la plateforme — c'est-à-dire souvent,
    puisque trois réglementations voisines partagent leur vocabulaire.

    On lit donc les blocs des trois vues CRA et la section CRA du script.
    """
    h = _fichier("sentinel.html")
    bouts = []
    for vue in ("p-cra", "p-cra-ecarts", "p-cra-signalement"):
        i = h.find('id="%s"' % vue)
        assert i > 0, "la vue « %s » a disparu" % vue
        bouts.append(h[i:h.find('<div class="page"', i + 10)])
    js = _fichier("sentinel.page.js")
    k = js.find("LE CYBER RESILIENCE ACT")
    assert k > 0, "la section CRA du script a disparu"
    bouts.append(js[k:])
    return "\n".join(bouts)


def test_les_vues_CRA_ne_recopient_AUCUN_libelle_d_annexe():
    """Une liste recopiée dans la page aurait divergé du moteur au premier
    amendement — et la divergence se serait vue chez le client, pas ici."""
    ecran = _ecran_cra()
    assert len(ecran) > 4000, "la population lue est trop maigre pour mesurer"
    recopies = [x for x in (cra.ANNEXE_III_I + cra.ANNEXE_III_II + cra.ANNEXE_IV)
                if x[:40] in ecran]
    assert not recopies, "libellés d'annexe recopiés dans l'écran : %s" % recopies[:3]
    exigences = [n for _c, n, _d in cra.ANNEXE_I_I + cra.ANNEXE_I_II
                 if n[:34] in ecran]
    assert not exigences, "exigences recopiées dans l'écran : %s" % exigences[:3]


def test_les_vues_CRA_vont_bien_CHERCHER_ce_qu_elles_ne_recopient_pas():
    """L'AUTRE MOITIÉ DE LA MÊME DÉCISION, et sans elle la première serait
    satisfaite par une page vide : ne rien recopier est facile quand on
    n'affiche rien.

    ═══ ELLE MESURE L'APPEL, PAS LA MENTION ══════════════════════════════
    La première version cherchait « /api/cra/referentiel » n'importe où dans
    la section. Une mutation qui débranchait l'appel a SURVÉCU : l'adresse
    figure aussi dans le commentaire d'en-tête, qui explique justement que
    tout vient de là. La règle lisait donc la PROMESSE écrite en commentaire
    au lieu du code qui la tient — le défaut exact qu'elle est censée
    empêcher, retourné contre elle.
    """
    ecran = _ecran_cra()
    for route in ("/api/cra/referentiel", "/api/cra/evaluer"):
        assert "fetch('%s'" % route in ecran, \
            "« %s » n'est pas APPELÉE par les vues CRA (une mention en " \
            "commentaire ne suffit pas)" % route


def test_le_cadre_normatif_porte_une_QUATRIEME_colonne_sur_CHAQUE_ligne():
    """Un cadre absent de la matrice n'est pas articulé aux autres : il est
    juxtaposé. Et une colonne sans lignes de module propres serait une colonne
    sans porte."""
    h = _fichier("sentinel.html")
    i = h.index('id="p-cadre-normatif"')
    j = h.index('id="p-conformite-globale"')
    bloc = h[i:j] if j > i else h[i:i + 20000]
    entetes = re.findall(r"<thead><tr>(.*?)</tr></thead>", bloc, re.S)
    assert entetes, "la matrice n'a plus de tableau"
    for e in entetes:
        assert e.count("<th>") == 5, "un tableau de la matrice n'a pas 5 colonnes"
        assert "CRA" in e
    for ligne in re.findall(r"<tr><td><a class=\"cn-link\".*?</tr>", bloc, re.S):
        assert ligne.count("<td>") == 5, \
            "une ligne de la matrice n'a pas 5 cellules : %s" % ligne[:90]


def test_la_matrice_conduit_AUX_modules_du_CRA():
    h = _fichier("sentinel.html")
    for vue in ("cra", "cra-ecarts", "cra-signalement"):
        assert "hubGo('%s')" % vue in h, \
            "la matrice ne conduit pas à la vue « %s »" % vue


# ═══════════════════════════════════════════════════════════════════════════
#  8. LE CORPUS DE L'ACCUEIL
# ═══════════════════════════════════════════════════════════════════════════

def test_le_CRA_est_la_DEUXIEME_norme_de_l_accueil_derriere_l_IA_Act():
    """Le poser après ISO 27001 l'aurait rangé parmi les normes volontaires,
    alors qu'il est d'application directe."""
    h = _fichier("index.html")
    i = h.index('id="normes"')
    bloc = h[i:i + 4000]
    noms = [re.sub(r"\s*↗$", "", x).strip()
            for x in re.findall(r'class="nn">([^<]*)<', bloc)]
    assert noms[0] == "IA Act"
    assert noms[1] == "CRA", "les normes sortent dans l'ordre %s" % noms
    assert len(noms) == 7


def test_le_titre_annonce_SEPT_normes_dans_les_trois_langues():
    """Une clé oubliée dans une langue laisse la version anglaise annoncer six
    normes là où la française en annonce sept — et personne ne s'en aperçoit
    avant un prospect étranger."""
    js = _fichier("index.page.js")
    titres = re.findall(r'"nr\.ttl":"(\d+)', js)
    assert len(titres) == 3, "%d titre(s) trouvé(s) au lieu de trois" % len(titres)
    assert set(titres) == {"7"}, "les langues annoncent %s" % titres
    assert js.count('"nr.cra"') == 3, "la clé nr.cra manque à une langue"


def test_l_accueil_renvoie_au_texte_officiel_du_reglement():
    h = _fichier("index.html")
    assert cra.SOURCE["eli"] in h or "2024/2847" in h


# ═══════════════════════════════════════════════════════════════════════════
#  9. LES ROUTES
# ═══════════════════════════════════════════════════════════════════════════

def _cli():
    import app as appli
    return appli.app.test_client()


def test_le_referentiel_sert_TOUT_ce_que_l_ecran_ne_recopie_pas():
    j = _cli().get("/api/cra/referentiel").get_json()
    assert j["ok"] is True
    for cle in ("classes", "procedures", "roles", "exclusions", "annexe_iii_i",
                "annexe_iii_ii", "annexe_iv", "exigences", "signalement",
                "destinataires", "calendrier", "source"):
        assert j.get(cle), "le référentiel ne sert pas « %s »" % cle
    assert len(j["annexe_iii_i"]) == len(cra.ANNEXE_III_I)
    assert j["source"]["licence"], "la source ne dit pas sa licence"


def test_la_route_accepte_LES_DEUX_formes_et_dit_la_meme_chose():
    """Un fabricant n'a jamais un seul produit ; un intégrateur qui en
    qualifie un seul ne doit pas avoir à en déclarer douze."""
    c = _cli()
    seul = {"nom": "A", "marche_ue": True, "classe": "important_ii"}
    un = c.post("/api/cra/evaluer", json=seul).get_json()
    parc = c.post("/api/cra/evaluer", json={"produits": [seul]}).get_json()
    assert un["organisme_notifie"] is True
    assert parc["organisme_notifie"] == 1
    assert parc["commande"]["classe"]["cle"] == un["classe"]["cle"]


def test_un_produit_sans_nom_est_REFUSE_et_pas_evalue_a_vide():
    r = _cli().post("/api/cra/evaluer", json={"marche_ue": True})
    assert r.status_code == 400
    assert r.get_json()["motif"] == "produit_sans_nom"


# ═══════════════════════════════════════════════════════════════════════════
#  10. LA GARDE D'IMPORT, ÉPROUVÉE EN LUI DONNANT UNE FAUTE À TROUVER
# ═══════════════════════════════════════════════════════════════════════════
#
# L'ÉTAT CORRECT EST UNE LISTE VIDE : une règle qui se contenterait de
# `assert cra._FAUTES == []` passerait aussi sur une garde désarmée.

def test_la_garde_refuse_une_classe_qui_ne_cite_aucun_article(monkeypatch):
    classes = {c: dict(v) for c, v in cra.CLASSES.items()}
    classes["important_i"]["article"] = ""
    monkeypatch.setattr(cra, "CLASSES", classes)
    with pytest.raises(RuntimeError) as e:
        cra._verifier()
    assert "article" in str(e.value)


def test_la_garde_refuse_deux_exigences_de_MEME_cle(monkeypatch):
    """Deux clés identiques écraseraient silencieusement une ligne de
    l'analyse d'écart par une autre."""
    monkeypatch.setattr(cra, "ANNEXE_I_II",
                        cra.ANNEXE_I_II + (("ei-01", "Doublon", "…"),))
    with pytest.raises(RuntimeError) as e:
        cra._verifier()
    assert "clé" in str(e.value)


def test_la_garde_refuse_un_signalement_dont_les_delais_ont_change(monkeypatch):
    s = {k: dict(v) for k, v in cra.SIGNALEMENT.items()}
    s["incident"]["etapes"] = [dict(e) for e in s["incident"]["etapes"]]
    s["incident"]["etapes"][0]["delai_h"] = 48
    monkeypatch.setattr(cra, "SIGNALEMENT", s)
    with pytest.raises(RuntimeError) as e:
        cra._verifier()
    assert "24" in str(e.value)


def test_la_source_declare_sous_quelle_licence_elle_est_reprise():
    """Le texte du JO est réutilisable au titre de la décision 2011/833/UE,
    avec attribution. Le module en reprend des libellés de catégories : il
    doit dire à quel titre."""
    assert "2011/833" in cra.SOURCE["licence"]
    assert "Journal officiel" in cra.SOURCE["licence"]
