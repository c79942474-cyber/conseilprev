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

#: LES VUES DU MODULE, NOMMÉES UNE SEULE FOIS. Plusieurs règles balayent cette
#: liste ; la tenir à deux endroits aurait garanti qu'une vue neuve soit
#: contrôlée par l'une et ignorée par l'autre.
VUES_CRA = ("cra-role", "cra", "cra-ecarts", "cra-chiffre", "cra-signalement")


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
    traitement.

    ═══ CE QUI A CHANGÉ, ET CE QUI N'A PAS CHANGÉ ════════════════════════
    Le CRA est désormais RANGÉ sous « Votre Mise en Conformité
    Réglementaire », à côté de RGPD & Privacy, ISO 42001 et NIS 2. Cela ne
    contredit pas ce que cette règle protège : il n'est PAS devenu une
    rubrique du RGPD ni de l'IA Act. Il reste une `.sb-section` à part
    entière, avec ses propres entrées — le titre de famille n'en est pas
    une, précisément pour que les quatre cadres restent quatre sections
    frères et non une hiérarchie.

    CE QUE LA RÈGLE MESURE DONC MAINTENANT : que la section CRA existe, que
    son groupe reste `cra`, et qu'elle soit rattachée à la famille de
    conformité plutôt qu'absorbée par un autre cadre."""
    h = _fichier("sentinel.html")
    assert 'data-grp="cra"' in h
    assert re.search(r'<div class="sb-section sb-pliable" data-grp="cra" '
                     r'data-fam="conformite".*?<span>CRA[^<]*</span>', h, re.S), \
        "le CRA n'a plus de section propre rattachée à la famille de conformité"
    # LE TÉMOIN : il n'est PAS rangé sous un autre cadre. Les quatre tiroirs
    # sont des sections FRÈRES ; si le CRA devenait un `.sb-item` du groupe
    # RGPD, cette ligne tomberait.
    assert '<div class="sb-item" data-grp="rgpd-et-privacy" role="button" ' \
           'tabindex="0" onclick="go(\'cra' not in h, \
        "le CRA est devenu une entrée du groupe RGPD : deux unités de compte " \
        "différentes rangées comme si elles n'en faisaient qu'une"
    # ═══ ON NOMME LES VUES, ON NE LES COMPTE PAS ══════════════════════
    # La première version comptait trois entrées. Elle est tombée le jour où
    # le module en a gagné deux — pour la bonne raison, mais sans rien dire de
    # ce qui manquait : un compte ne nomme pas la vue absente. Les nommer fait
    # tomber la règle sur la seule chose qui compte, et le message dit quoi.
    manquantes = [v for v in VUES_CRA if ("go('%s'," % v) not in h]
    assert not manquantes, "vues CRA absentes de la barre : %s" % manquantes
    items = re.findall(r'<div class="sb-item" data-grp="cra"', h)
    assert len(items) == len(VUES_CRA), \
        "%d entrées dans la barre pour %d vues déclarées : une vue est " \
        "servie sans être déclarée ici, ou l'inverse" % (len(items), len(VUES_CRA))


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
    for vue in ("p-" + v for v in VUES_CRA):
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
    # LE NOMBRE N'EST PAS FIGÉ ICI : ce qui se mesure est la PLACE du CRA,
    # pas la taille du bloc. Le figer faisait tomber cette règle-ci le jour
    # où une norme s'ajoutait ailleurs dans la grille, pour une raison sans
    # aucun rapport avec le rang du CRA.
    assert len(noms) >= 7, "le bloc a perdu des normes : %s" % noms


def test_les_trois_langues_annoncent_LE_MEME_nombre_de_normes():
    """Une clé oubliée dans une langue laisse la version anglaise annoncer un
    nombre différent de la française — et personne ne s'en aperçoit avant un
    prospect étranger.

    LE NOMBRE LUI-MÊME N'EST PLUS ÉCRIT ICI. La règle exigeait « 7 » dans les
    trois langues ; elle est tombée quand le bloc est passé à neuf, alors que
    les trois langues s'accordaient parfaitement. Ce qui compte n'a jamais
    été le chiffre : c'est que les trois disent LE MÊME.
    """
    js = _fichier("index.page.js")
    titres = re.findall(r'"nr\.ttl":"(\d+)', js)
    assert len(titres) == 3, "%d titre(s) trouvé(s) au lieu de trois" % len(titres)
    assert len(set(titres)) == 1, (
        "les trois langues annoncent des nombres différents : %s" % titres)
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


# ═══════════════════════════════════════════════════════════════════════════
#  11. LES CINQ RÔLES — ET L'ARBRE QUI DIT LEQUEL EST LE VÔTRE
# ═══════════════════════════════════════════════════════════════════════════
#
# CE QUE CES RÈGLES GARDENT. Le CRA ne demande pas comment vous vous appelez,
# il regarde ce que vous faites du produit. Deux gestes ordinaires du commerce
# — apposer sa marque, modifier substantiellement — font de vous un fabricant.
# Un arbre qui se tromperait là ferait travailler un revendeur sous les
# obligations d'un distributeur alors qu'il porte celles d'un fabricant, dont
# le signalement en vingt-quatre heures, déjà applicable.

@pytest.mark.parametrize("declaration,attendu", [
    ({"je_concois": True}, "fabricant"),
    ({"fabricant_hors_union": True}, "importateur"),
    ({}, "distributeur"),
    ({"je_distribue": True}, "distributeur"),
    # LES DEUX GESTES QUI REQUALIFIENT, chacun seul puis combinés.
    ({"fabricant_hors_union": True, "sous_ma_marque": True}, "requalifie"),
    ({"je_distribue": True, "sous_ma_marque": True}, "requalifie"),
    ({"je_distribue": True, "modification_substantielle": True}, "requalifie"),
    ({"fabricant_hors_union": True, "modification_substantielle": True}, "requalifie"),
    # L'ARTICLE 22 — ni fabricant, ni importateur, ni distributeur.
    ({"modification_substantielle": True}, "integrateur"),
])
def test_l_arbre_rend_LE_role_du_reglement_et_pas_celui_qu_on_croit(declaration, attendu):
    q = cra.qualifier_role(declaration)
    assert q["role"]["cle"] == attendu, \
        "%s → %s au lieu de %s" % (declaration, q["role"]["cle"], attendu)


def test_la_requalification_PRIME_sur_l_import():
    """L'ORDRE DES TESTS EST CELUI DU RÈGLEMENT, PAS LE PLUS COMMODE.

    Un importateur qui appose sa marque n'est pas « importateur et un peu
    fabricant » : il EST fabricant. Tester l'import d'abord aurait rendu
    « importateur » — réponse vraie en apparence, et qui masque la seule
    information qui change quelque chose.
    """
    q = cra.qualifier_role({"fabricant_hors_union": True, "sous_ma_marque": True})
    assert q["role"]["cle"] == "requalifie"
    assert q["role"]["palier"] == "lourd", \
        "la requalification n'emporte plus le palier de sanction du fabricant"


def test_l_etendue_distingue_la_PARTIE_modifiee_du_produit_ENTIER():
    """LA NUANCE QUI DÉCIDE DU COÛT, et que les résumés du CRA omettent.

    L'article 22, §2 borne l'obligation à la partie modifiée — SAUF si la
    modification a des répercussions sur la cybersécurité de l'ensemble. Entre
    une carte réseau et une baie entière, l'étendue de la documentation
    technique à produire n'est pas du même ordre.
    """
    partie = cra.qualifier_role({"modification_substantielle": True})
    entier = cra.qualifier_role({"modification_substantielle": True,
                                 "modification_affecte_ensemble": True})
    assert partie["etendue"]["ensemble"] is False
    assert entier["etendue"]["ensemble"] is True
    assert "PARTIE" in partie["etendue"]["dit"]
    assert "ENTIER" in entier["etendue"]["dit"]
    assert partie["etendue"]["article"] == "art. 22, §2"


def test_sans_modification_il_n_y_a_PAS_d_etendue_a_annoncer():
    """Annoncer une étendue à un distributeur qui ne modifie rien lui ferait
    chercher une frontière qui n'existe pas dans son cas."""
    for d in ({}, {"je_concois": True}, {"fabricant_hors_union": True}):
        assert cra.qualifier_role(d)["etendue"] is None


def test_le_verdict_redescend_avec_le_CHEMIN_qui_y_mene():
    """Une qualification juridique doit pouvoir se contester. Un verdict sans
    son raisonnement ne le peut pas."""
    q = cra.qualifier_role({"je_distribue": True, "sous_ma_marque": True})
    assert len(q["trace"]) >= 4
    for pas in q["trace"]:
        assert pas["question"].strip() and pas["effet"].strip()
    assert any(p["reponse"] for p in q["trace"]), \
        "le chemin ne montre aucune réponse positive : il n'explique rien"


def test_la_tracabilite_de_l_article_23_est_TENUE_A_PART_des_roles():
    """Elle pèse sur TOUS les opérateurs. La ranger dans une fiche de rôle
    aurait laissé croire que les autres en sont dispensés."""
    assert "art. 23" in cra.TRACABILITE["article"]
    for r in cra.ROLES.values():
        assert not any("23" in x for x in r["porte"]), \
            "l'article 23 est rattaché à un rôle particulier"


# ═══════════════════════════════════════════════════════════════════════════
#  12. L'EXPOSITION CHIFFRÉE — ARTICLE 64
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("palier,seuil_m", [
    ("lourd", 600), ("moyen", 500), ("leger", 500)])
def test_le_seuil_ou_le_POURCENTAGE_depasse_le_montant_fixe(palier, seuil_m):
    """LE CHIFFRE QUE PRESQUE TOUS LES RÉSUMÉS OUBLIENT.

    « 15 millions OU 2,5 % » n'est pas un choix de l'autorité : c'est le plus
    élevé des deux. Il existe donc un chiffre d'affaires en dessous duquel le
    montant fixe commande TOUJOURS. Une PME qui lit « 2,5 % de mon chiffre
    d'affaires » entend un chiffre dix fois trop bas.
    """
    assert cra.seuil_de_bascule(palier) == seuil_m * 10 ** 6


@pytest.mark.parametrize("ca_m,commande", [
    (12, "montant_fixe"),        # PME
    (599, "montant_fixe"),       # juste sous le seuil
    (600, "montant_fixe"),       # AU seuil : les deux sont égaux, le fixe tient
    (601, "pourcentage"),        # juste au-dessus
    (2400, "pourcentage"),       # ETI
])
def test_ce_qui_commande_bascule_AU_SEUIL_et_pas_avant(ca_m, commande):
    l = cra.exposition(ca_m * 10 ** 6, ["lourd"])["lignes"][0]
    assert l["commande"] == commande, \
        "à %d M€, c'est « %s » qui commande et non « %s »" % (ca_m, l["commande"], commande)
    assert l["retenu_eur"] == max(15 * 10 ** 6, ca_m * 10 ** 6 * 0.025)


def test_sans_chiffre_d_affaires_on_ne_suppose_PAS_zero():
    """Un chiffre d'affaires inconnu traité comme nul donnerait l'exposition
    d'une entreprise sans activité — c'est-à-dire un tableau rassurant et
    faux."""
    e = cra.exposition(None)
    assert e["ca_declare"] is False
    for l in e["lignes"]:
        assert l["montant_part"] is None
        assert l["retenu_eur"] == cra.SANCTIONS[l["cle"]]["plafond_eur"]
        assert l["commande"] == "montant_fixe"


@pytest.mark.parametrize("mauvais", ["", "beaucoup", None, -1])
def test_un_chiffre_d_affaires_illisible_retombe_sur_le_montant_fixe(mauvais):
    e = cra.exposition(mauvais)
    assert e["ca_declare"] is False


def test_l_exposition_ne_rend_JAMAIS_un_montant_seul():
    """L'article 64, §5 impose de tenir compte de la nature, de la gravité et
    de la durée de l'infraction, des antécédents et de la taille. Un plafond
    n'est pas une prévision, et l'afficher seul le ferait lire comme tel."""
    e = cra.exposition(45 * 10 ** 6)
    assert len(e["modulation"]) >= 3
    assert "PLAFONDS" in e["reserve"]
    assert "État membre" in e["reserve"], \
        "la réserve ne dit plus que le régime est fixé par chaque État membre"


def test_les_trois_paliers_sont_ORDONNES_sur_leurs_DEUX_bornes():
    """Un palier « plus lourd » sur l'euro mais plus léger sur le pourcentage
    inverserait le classement dès qu'on dépasse le seuil de bascule."""
    ordre = sorted(cra.SANCTIONS, key=lambda c: cra.SANCTIONS[c]["rang"])
    for a, b in zip(ordre, ordre[1:]):
        assert cra.SANCTIONS[a]["plafond_eur"] > cra.SANCTIONS[b]["plafond_eur"]
        assert cra.SANCTIONS[a]["part_ca"] > cra.SANCTIONS[b]["part_ca"]


def test_chaque_role_dit_a_quel_palier_il_expose():
    """Sans cela, le parcours chiffré ne pourrait pas relier un rôle à un
    montant — et c'est exactement ce qu'on lui demande."""
    for cle, r in cra.ROLES.items():
        assert r["palier"] in cra.SANCTIONS, \
            "le rôle « %s » n'expose à aucun palier connu" % cle
    # ET LES DEUX RÔLES REQUALIFIÉS EXPOSENT AU PALIER LOURD, comme le
    # fabricant : c'est ce qui rend la requalification coûteuse.
    for cle in ("fabricant", "requalifie", "integrateur"):
        assert cra.ROLES[cle]["palier"] == "lourd"
    for cle in ("importateur", "distributeur"):
        assert cra.ROLES[cle]["palier"] == "moyen"


def test_les_routes_de_role_et_d_exposition_repondent():
    c = _cli()
    r = c.post("/api/cra/role", json={"je_distribue": True,
                                      "sous_ma_marque": True}).get_json()
    assert r["role"]["cle"] == "requalifie"
    e = c.post("/api/cra/exposition",
               json={"chiffre_affaires": 45 * 10 ** 6}).get_json()
    assert e["lignes"][0]["retenu_eur"] == 15 * 10 ** 6


# ═══════════════════════════════════════════════════════════════════════════
#  13. LES CINQ PARCOURS — CHACUN AVEC SES ÉTAPES PROPRES
# ═══════════════════════════════════════════════════════════════════════════

PARCOURS_CRA = ("cra_fabricant", "cra_importateur", "cra_distributeur",
                "cra_integrateur", "cra_chiffre")

#: COMBIEN D'ÉTAPES PROPRES UN PARCOURS DOIT PORTER. Deux, et c'est la
#: discipline déjà écrite ailleurs dans ce dépôt pour les familles de
#: parcours : en dessous, les distinguer n'apprend rien et il aurait fallu
#: n'en écrire qu'un.
PROPRES_MINIMUM = 2


def _etapes_des_parcours():
    js = _fichier("sentinel.page.js")
    i = js.index("var GUIDED_PATHS = [")
    j = js.index("var GP_FAMILLES", i)
    bloc = js[i:j]
    out = {}
    for pid in PARCOURS_CRA:
        k = bloc.index("id: '%s'," % pid)
        fin = bloc.find("\n  {\n    id: '", k)
        corps = bloc[k:fin if fin > 0 else len(bloc)]
        out[pid] = re.findall(r"\{id:'([a-z0-9-]+)'", corps)
    return out


def test_les_cinq_parcours_du_CRA_existent_et_sont_dans_LEUR_famille():
    js = _fichier("sentinel.page.js")
    i = js.index("var GP_FAMILLES")
    famille = js[i:js.index("];", i)]
    k = famille.index("Cyber Resilience Act")
    bloc = famille[k:k + 400]
    for pid in PARCOURS_CRA:
        assert "id: '%s'," % pid in js, "le parcours « %s » n'existe pas" % pid
        assert pid in bloc, \
            "« %s » n'est pas rattaché à la famille CRA" % pid


@pytest.mark.parametrize("pid", PARCOURS_CRA)
def test_chaque_parcours_CRA_porte_au_moins_deux_etapes_QUI_LUI_SONT_PROPRES(pid):
    """S'ils portaient presque les mêmes étapes, les distinguer n'apprendrait
    rien et il aurait fallu en écrire un seul. C'était d'ailleurs mon premier
    arbitrage, et il était trop rapide : les articles 19, 20, 21 et 22 portent
    chacun un geste propre, et cette règle mesure que les parcours le suivent.
    """
    t = _etapes_des_parcours()
    autres = set()
    for x, v in t.items():
        if x != pid:
            autres |= set(v)
    propres = sorted(set(t[pid]) - autres)
    assert len(propres) >= PROPRES_MINIMUM, \
        "« %s » n'a que %d étape(s) propre(s) : %s — il se confond avec les " \
        "autres parcours du CRA" % (pid, len(propres), propres)


def test_chaque_parcours_de_ROLE_commence_par_ce_qui_le_distingue():
    """L'ORDRE PORTE UNE DÉCISION, ET IL SE MESURE.

    Les trois parcours qui ne sont PAS celui du fabricant commencent par la
    qualification du rôle — parce que c'est précisément ce que leur lecteur
    ignore : un revendeur sous marque propre qui commencerait par classer ses
    produits le ferait sous un rôle qui n'est pas le sien, donc avec les
    mauvaises obligations. Le fabricant, lui, sait ce qu'il est : son parcours
    commence par ce qui court déjà, l'article 14.
    """
    t = _etapes_des_parcours()
    assert t["cra_fabricant"][0] == "cra-signalement"
    for pid in ("cra_importateur", "cra_distributeur", "cra_integrateur"):
        assert t[pid][0] == "cra-role", \
            "« %s » ne commence pas par la qualification du rôle" % pid
    assert t["cra_chiffre"][0] == "cra-chiffre"


def test_tous_les_parcours_CRA_menent_a_l_exposition_chiffree():
    """C'est ce que « parcours chiffré » veut dire : non pas un parcours à
    part que personne n'ouvre, mais un chiffre au bout de chaque chemin."""
    t = _etapes_des_parcours()
    for pid, etapes in t.items():
        assert "cra-chiffre" in etapes, \
            "« %s » ne mène pas à l'exposition chiffrée" % pid


def test_les_deux_panneaux_neufs_ont_leur_guide():
    """Un panneau sans guide retombe sur « Guide non encore disponible » —
    c'est-à-dire sur un aveu, à l'endroit précis où le client cherche de
    l'aide."""
    js = _fichier("sentinel.page.js")
    i = js.index("var PAGE_GUIDES = {")
    bloc = js[i:i + 400000]
    for vue in ("cra-role", "cra-chiffre"):
        assert "'%s': {" % vue in bloc, "« %s » n'a pas de guide" % vue


def test_le_parcours_chiffre_dit_ce_qu_il_NE_chiffre_PAS():
    """LA RÈGLE QUI EMPÊCHE CE MODULE DE DEVENIR UN FAUX DEVIS.

    Estimer un coût de mise en conformité — jours-homme, honoraires
    d'organisme notifié — produirait un document qui a l'air d'un devis sans
    en être un, et il serait cité en comité. Le parcours doit dire qu'il ne le
    fait pas, et l'écran aussi.
    """
    js = _fichier("sentinel.page.js")
    k = js.index("id: 'cra_chiffre',")
    pitch = js[k:k + 1400]
    assert "estimer" in pitch and "coût" in pitch
    ecran = _ecran_cra()
    assert "ne chiffre que ce que le texte chiffre" in ecran.lower()
    assert "plafond" in ecran.lower()


def test_la_garde_refuse_un_role_qui_n_expose_a_AUCUN_palier(monkeypatch):
    """LE TROU QUE LA BATTERIE DE MUTATIONS A TROUVÉ.

    La garde vérifiait déjà que chaque rôle dit à quel palier il expose — et
    aucune règle ne l'éprouvait : neutraliser cette clause ne faisait tomber
    personne. Or c'est elle qui empêche qu'un rôle ajouté demain entre dans le
    parcours chiffré sans montant, et y apparaisse à zéro.
    """
    roles = {c: dict(v) for c, v in cra.ROLES.items()}
    roles["distributeur"]["palier"] = "inconnu"
    monkeypatch.setattr(cra, "ROLES", roles)
    with pytest.raises(RuntimeError) as e:
        cra._verifier()
    assert "palier" in str(e.value)


def test_la_garde_refuse_un_role_qui_ne_porte_AUCUNE_obligation(monkeypatch):
    """Un rôle sans obligation écrite s'afficherait dans la qualification
    comme une case vide — et le lecteur conclurait qu'il n'a rien à faire."""
    roles = {c: dict(v) for c, v in cra.ROLES.items()}
    roles["importateur"]["porte"] = []
    monkeypatch.setattr(cra, "ROLES", roles)
    with pytest.raises(RuntimeError) as e:
        cra._verifier()
    assert "obligation" in str(e.value)


def test_la_garde_refuse_un_palier_ampute_d_une_de_ses_deux_bornes(monkeypatch):
    """« Le montant le plus élevé étant retenu » suppose qu'il y en ait deux.
    Un palier réduit au seul montant fixe ferait disparaître le pourcentage —
    et l'exposition d'une ETI serait sous-estimée d'un ordre de grandeur."""
    s = {c: dict(v) for c, v in cra.SANCTIONS.items()}
    s["lourd"]["part_ca"] = 0
    monkeypatch.setattr(cra, "SANCTIONS", s)
    with pytest.raises(RuntimeError) as e:
        cra._verifier()
    assert "bornes" in str(e.value)
