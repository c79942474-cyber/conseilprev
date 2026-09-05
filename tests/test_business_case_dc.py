# -*- coding: utf-8 -*-
"""Le business case : la demande, le calendrier électrique, le point mort.

CE QUE CES RÈGLES PROTÈGENT, ET DANS QUEL ORDRE D'IMPORTANCE.

  · LE POINT MORT NE DOIT PAS ÊTRE FLATTÉ. Il se calcule sur une séparation
    entre coûts fixes et coûts variables, et cette séparation le déplace de
    moitié. L'électricité n'est PAS entièrement variable : le froid,
    l'onduleur et la distribution tournent pour le volume de la salle, pas
    pour la charge installée. Un modèle qui la ferait varier tout entière
    annoncerait un point mort bien plus bas qu'il n'est — l'erreur la plus
    flatteuse et la plus coûteuse de tout l'exercice. Une règle la mesure.

  · AUCUN PRIX N'EST EMBARQUÉ. Le prix d'hébergement varie d'un facteur trois
    entre deux marchés et se négocie contrat par contrat. Un prix par défaut
    deviendrait le prix du dossier. Une règle mesure le CODE, pas seulement
    les sorties.

  · UN DOSSIER VIDE NE PRODUIT AUCUN FAVORABLE. C'est le témoin négatif qui
    manque le plus souvent : un moteur qui rendrait « favorable » faute de
    donnée contraire validerait tous les projets qu'on ne lui décrit pas.

  · LE VERDICT RESTE UNIQUE. Les constats du business case rejoignent ceux du
    chiffrage dans la MÊME synthèse. Deux avis séparés se contrediraient, et
    c'est le plus flatteur qu'on présenterait — une règle vérifie que le
    format n'a pas divergé, une autre que l'avis se DURCIT quand la demande se
    dégrade.
"""
import io
import os
import re
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import business_case_dc as B  # noqa: E402
import faisabilite_dc as FA  # noqa: E402
import finance_dc as F  # noqa: E402


def _lire(nom):
    return io.open(os.path.join(ICI, nom), encoding="utf-8").read()


def _chiffrage(mw=20):
    d = F.dpgf(mw, pays="FR", climat_classe="tempere", eau_classe="moyenne")
    e = F.exploitation(d["enveloppe_meur"], mw, d["refroidissement"]["pue"],
                       [90, 130])
    return d, e


# ══════════════════════════════════════════════════════════════════════════
# 0. Le garde-fou
# ══════════════════════════════════════════════════════════════════════════

def test_le_referentiel_porte_ce_que_les_regles_mesurent():
    assert len(B.ENTREES) >= 10, len(B.ENTREES)
    assert len(B.RISQUES_CONNUS) >= 5, len(B.RISQUES_CONNUS)
    assert len(B.HYPOTHESES) >= 3, len(B.HYPOTHESES)


# ══════════════════════════════════════════════════════════════════════════
# 1. AUCUN PRIX, AUCUNE DEMANDE : rien n'est deviné
# ══════════════════════════════════════════════════════════════════════════

def test_aucun_prix_d_hebergement_n_est_ecrit_dans_le_module():
    """LA RÈGLE MESURE LE CODE. Un prix glissé en valeur par défaut ne se
    verrait sur aucune sortie tant que personne ne laisse le champ vide — et
    le jour où quelqu'un le laisse vide, il obtient un point mort qu'il croira
    calculé sur SON prix."""
    src = _lire("business_case_dc.py")
    for arg in ("prix_kw_mois", "mw_commercialises", "capacite_concurrente_mw",
                "demande_zone_mw"):
        mauvais = re.findall(r"\b%s\s*=\s*([0-9][0-9.,]*)" % arg, src)
        assert not mauvais, (arg, mauvais)


def test_sans_prix_les_projections_refusent_de_conclure():
    d, e = _chiffrage()
    p = B.projections(20, exploitation=e)
    assert p["ok"] is False and p["verdict"] == "indetermine", p
    assert any("prix" in m for m in p["manques"]), p["manques"]


def test_un_dossier_vide_ne_produit_aucun_favorable():
    """LE TÉMOIN NÉGATIF LE PLUS IMPORTANT. Un moteur qui rendrait
    « favorable » faute de donnée contraire validerait tous les projets qu'on
    ne lui décrit pas — c'est-à-dire les plus risqués."""
    liste, _ = B.constats(20)
    assert not [c for c in liste if c["etat"] == "favorable"], \
        [c["sujet"] for c in liste if c["etat"] == "favorable"]
    assert all(c["etat"] == "indetermine" for c in liste
               if c["sujet"] != "Modularité et phasage"), \
        [(c["sujet"], c["etat"]) for c in liste]


def test_chaque_constat_porte_son_fondement_et_ce_qui_le_renverserait():
    """« Ce qui le changerait » est la seule partie qui se transforme en plan
    de travail. Sans elle, l'avis n'est qu'un jugement."""
    liste, _ = B.constats(20)
    for c in liste:
        assert len(c["fondement"]) > 20, c["sujet"]
        assert len(c["renverse_si"]) > 40, c["sujet"]


# ══════════════════════════════════════════════════════════════════════════
# 2. LE CALENDRIER ÉLECTRIQUE — le seul test qui bloque à lui seul
# ══════════════════════════════════════════════════════════════════════════

def test_une_puissance_ferme_apres_la_mise_en_service_bloque():
    """UN BÂTIMENT LIVRÉ AVANT SA PUISSANCE porte tous ses coûts fixes et ne
    produit rien, et le délai n'est pas rattrapable : il ne dépend pas du
    porteur. C'est le test qui arrête le plus de projets."""
    c = B._test_calendrier_electrique(2029, 2031)
    assert c["etat"] == "bloquant", c
    assert "2031" in c["constat"] and "2029" in c["constat"], c["constat"]


def test_la_meme_annee_n_est_pas_bloquante_mais_ne_passe_pas_non_plus():
    """LE TÉMOIN INTERMÉDIAIRE. Un module qui ne verrait que deux états —
    passe / bloque — classerait « aucune marge » comme « passe »."""
    assert B._test_calendrier_electrique(2029, 2029)["etat"] == "vigilance"


def test_une_marge_confortable_passe():
    c = B._test_calendrier_electrique(2031, 2029)
    assert c["etat"] == "favorable", c
    assert "2 ans de marge" in c["constat"], c["constat"]


def test_sans_les_deux_annees_le_test_reste_indetermine():
    for ms, pf in ((None, 2030), (2030, None), (None, None)):
        assert B._test_calendrier_electrique(ms, pf)["etat"] == "indetermine"


# ══════════════════════════════════════════════════════════════════════════
# 3. LE POINT MORT — la séparation qui le décide
# ══════════════════════════════════════════════════════════════════════════

def test_l_electricite_n_est_pas_entierement_variable():
    """LA RÈGLE QUI PROTÈGE LE CHIFFRE LE PLUS IMPORTANT. Un site à moitié
    rempli ne consomme pas la moitié : le froid, l'onduleur et la distribution
    tournent pour le volume. Classer toute l'électricité en variable
    abaisserait le point mort d'un tiers."""
    d, e = _chiffrage()
    cv = B._cout_fixe_variable(e)
    elec = [x for x in cv["detail"] if x["cle"] == "electricite"][0]
    assert elec["nature"] == "mixte", elec
    assert 0 < elec["part_fixe"] < 1, elec
    # Et la part fixe globale reste substantielle : un point mort calculé sur
    # des coûts presque tous variables serait bas et faux.
    assert cv["fixe_meur_an"][0] > 0 and cv["variable_meur_an"][0] > 0, cv


def test_un_poste_inconnu_est_repute_fixe_et_le_dit():
    """LE SENS PRUDENT EST DÉCLARÉ. Classer un poste inconnu en variable
    abaisserait le point mort, c'est-à-dire flatterait le dossier."""
    faux = {"postes": [{"cle": "poste_inedit", "nom": "Inédit",
                        "meur_an": [1.0, 2.0]}]}
    cv = B._cout_fixe_variable(faux)
    assert cv["variable_meur_an"] == [0.0, 0.0], cv
    assert cv["detail"][0]["nature"] == "fixe_par_defaut", cv["detail"]


def test_le_point_mort_suit_son_equation():
    """VÉRIFIÉE CONTRE LA FORMULE, pas contre elle-même. Une règle qui
    rappellerait la fonction pour se comparer à elle-même serait verte quelle
    que soit l'arithmétique employée."""
    d, e = _chiffrage()
    p = B.projections(20, e, prix_kw_mois=140)
    fixe = B._mi(p["couts"]["fixe_meur_an"])
    var = B._mi(p["couts"]["variable_meur_an"])
    attendu = fixe / (p["revenu_plein_meur_an"] - var)
    assert abs(p["point_mort_taux"] - round(attendu, 4)) < 1e-4, p
    assert p["revenu_plein_meur_an"] == round(20 * 1000 * 140 * 12 / 1e6, 2)


def test_le_point_mort_monte_quand_le_prix_baisse():
    """LE SENS DE LA VARIATION, mesuré. Un point mort qui ne bougerait pas
    avec le prix ne mesurerait rien."""
    d, e = _chiffrage()
    cher = B.projections(20, e, prix_kw_mois=200)["point_mort_taux"]
    modique = B.projections(20, e, prix_kw_mois=100)["point_mort_taux"]
    assert modique > cher, (modique, cher)


def test_les_deux_bornes_de_cout_sortent_avec_le_cas_central():
    """C'EST LA BORNE HAUTE QUI SE PRÉSENTE EN COMITÉ. Un point mort central
    seul laisserait croire à une précision que la fourchette d'exploitation
    n'a pas."""
    d, e = _chiffrage()
    p = B.projections(20, e, prix_kw_mois=140)
    b = p["point_mort_bornes"]
    assert len(b) == 2 and b[0] < p["point_mort_taux"] < b[1], (b, p["point_mort_taux"])


def test_un_point_mort_au_dessus_de_la_pleine_charge_bloque():
    """RELEVÉ EN NAVIGATEUR, et c'était une faute. Sur un pays à électricité
    chère, le point mort central sortait à 146 % — il faudrait remplir le site
    AU-DELÀ de sa capacité pour équilibrer l'exploitation — et le module le
    classait « vigilance », c'est-à-dire un point à lever en parallèle des
    études. Aucun taux de commercialisation n'y suffit : c'est le modèle
    économique qui ne tient pas, et poursuivre les études reviendrait à
    travailler sur une hypothèse déjà démentie.

    LA RÈGLE ÉPROUVE LES TROIS CAS SUR LE MÊME MOTEUR, pays par pays : c'est
    le prix de l'électricité qui les sépare, et il vient du chiffrage.
    """
    attendus = {}
    for pays, prix in (("IE", [200, 260]), ("SE", [45, 70]), ("FR", [90, 130])):
        d = F.dpgf(20, pays=pays, climat_classe="tempere", eau_classe="moyenne")
        e = F.exploitation(d["enveloppe_meur"], 20, d["refroidissement"]["pue"],
                           prix)
        p = B.projections(20, e, prix_kw_mois=140, mw_commercialises=9)
        attendus[pays] = (p["point_mort_taux"], B._test_robustesse(p)["etat"])
    assert attendus["IE"][0] > 1.0 and attendus["IE"][1] == "bloquant", attendus
    assert attendus["SE"][1] == "favorable", attendus
    assert attendus["FR"][1] == "vigilance", attendus


def test_l_equation_s_ecrit_avec_le_separateur_francais():
    """LA MÊME PAGE MONTRE L'ÉQUATION ET LES CARTES. Elle sortait
    « 18.52 M€/an » deux lignes sous « 33,6 M€/an » — deux graphies du même
    genre de nombre, sur le même écran."""
    d, e = _chiffrage()
    eq = B.projections(20, e, prix_kw_mois=140)["equation"]
    assert "," in eq, eq
    assert not re.search(r"\d\.\d", eq), eq


def test_la_marge_de_securite_est_l_ecart_au_point_mort():
    d, e = _chiffrage()
    p = B.projections(20, e, prix_kw_mois=140, mw_commercialises=9)
    assert abs(p["marge_de_securite"]
               - (p["taux_contracte"] - p["point_mort_taux"])) < 1e-9, p


# ══════════════════════════════════════════════════════════════════════════
# 4. LA TRAJECTOIRE — déclarée, jamais prévue
# ══════════════════════════════════════════════════════════════════════════

def test_sans_trajectoire_declaree_aucune_annee_n_est_annoncee():
    """UNE COURBE DE COMMERCIALISATION INVENTÉE serait une prévision de vente
    déguisée en calcul."""
    d, e = _chiffrage()
    t = B.projections(20, e, prix_kw_mois=140)["trajectoire"]
    assert t["ok"] is False
    assert "devinée" in t["message"] or "supposée" in t["message"], t["message"]


def test_la_trajectoire_declaree_donne_l_annee_de_marge_positive():
    d, e = _chiffrage()
    t = B.projections(20, e, prix_kw_mois=140,
                      trajectoire_mw=[4, 9, 14, 18, 20])["trajectoire"]
    assert t["ok"] is True and t["annee_marge_positive"], t
    lignes = t["lignes"]
    avant = [l for l in lignes if l["annee"] < t["annee_marge_positive"]]
    assert all(l["marge_meur"] < 0 for l in avant), avant
    assert lignes[t["annee_marge_positive"] - 1]["marge_meur"] >= 0


def test_une_trajectoire_qui_ne_passe_jamais_positive_le_dit():
    """LE TÉMOIN NÉGATIF : un module qui annoncerait toujours une année de
    passage inventerait un espoir."""
    d, e = _chiffrage()
    t = B.projections(20, e, prix_kw_mois=140,
                      trajectoire_mw=[1, 2, 3])["trajectoire"]
    assert t["annee_marge_positive"] is None, t
    assert "AUCUNE" in t["message"], t["message"]


# ══════════════════════════════════════════════════════════════════════════
# 5. LES AUTRES TESTS — chacun mesuré sur sa sortie
# ══════════════════════════════════════════════════════════════════════════

def test_la_demande_se_confronte_au_point_mort_et_non_a_une_norme():
    """« 45 % de pré-commercialisation » ne veut rien dire dans l'absolu : le
    même taux est confortable sur un point mort à 30 % et insuffisant sur un
    point mort à 61 %."""
    d, e = _chiffrage()
    p = B.projections(20, e, prix_kw_mois=140, mw_commercialises=9)
    faible = B._test_demande(20, 9, p)
    fort = B._test_demande(20, 18, p)
    assert faible["etat"] == "vigilance", faible
    assert fort["etat"] == "favorable", fort
    assert "point mort" in faible["constat"], faible["constat"]


def test_une_densite_client_hors_du_regime_chiffre_bloque():
    """UN SITE CHIFFRÉ POUR DE L'HÉBERGEMENT CLASSIQUE et commercialisé
    auprès de clients qui demandent du calcul accéléré n'est pas cher : il est
    hors sujet."""
    d, _ = _chiffrage()
    assert B._test_besoins_clients(80, d)["etat"] == "bloquant"
    d_ia = F.dpgf(20, pays="FR", climat_classe="tempere", eau_classe="moyenne",
                  densite_ia=True)
    assert B._test_besoins_clients(80, d_ia)["etat"] == "favorable"


def test_la_concurrence_compare_des_capacites_et_ne_nomme_personne():
    """LA RÈGLE ÉPROUVE LES TROIS CAS, et pas deux.

    Sa première version ne distinguait que « vigilance » et « favorable ». Or
    le module a DEUX seuils — une offre qui dépasse la demande, et une offre
    qui la dépasse de moitié —, et ils ne disent pas la même chose : le second
    annonce que le prix sera la première variable qui cède. Une mutation
    supprimant le seuil haut survivait, parce que le cas retombait sur le
    seuil bas avec le même état. La règle lit donc aussi ce qui est DIT.
    """
    tres_serre = B._test_concurrence(20, 120, 90)     # ratio 1,56
    serre = B._test_concurrence(20, 90, 100)          # ratio 1,10
    large = B._test_concurrence(20, 20, 200)          # ratio 0,20
    assert tres_serre["etat"] == "vigilance", tres_serre
    assert serre["etat"] == "vigilance", serre
    assert large["etat"] == "favorable", large
    assert "de moitié" in tres_serre["constat"], tres_serre["constat"]
    assert "de moitié" not in serre["constat"], serre["constat"]
    assert "excède" in serre["constat"], serre["constat"]
    src = _lire("business_case_dc.py")
    assert "ne note aucun" in src.lower() or "NOTE AUCUN" in src, \
        "le module doit dire qu'il ne note pas les concurrents"


def test_l_absence_de_phasage_expose_toute_l_enveloppe():
    d, _ = _chiffrage()
    c = B._test_modularite(20, None, 9, d)
    assert c["etat"] == "vigilance", c
    assert "seul tenant" in c["constat"], c["constat"]


def test_une_premiere_tranche_couverte_par_le_contracte_passe():
    d, _ = _chiffrage()
    assert B._test_modularite(20, [8, 12], 9, d)["etat"] == "favorable"
    assert B._test_modularite(20, [15, 5], 9, d)["etat"] == "vigilance"


def test_un_decoupage_qui_ne_couvre_pas_la_capacite_est_signale():
    d, _ = _chiffrage()
    c = B._test_modularite(20, [5, 5], 9, d)
    assert c["etat"] == "vigilance" and "ne couvre pas" in c["constat"], c


def test_les_risques_non_couverts_sont_nommes_un_par_un():
    c = B._test_risques(["indexation", "taux"])
    assert c["etat"] == "vigilance", c
    for k in ("electricite_repercutee", "change", "penalites_sla"):
        assert B.RISQUES_CONNUS[k]["nom"].lower() in c["constat"], (k, c["constat"])
    assert B._test_risques(list(B.RISQUES_CONNUS))["etat"] == "favorable"
    # UNE LISTE VIDE N'EST PAS UNE DÉCLARATION : le formulaire n'envoie rien
    # quand aucune case n'est cochée, et rendre un verdict là-dessus serait
    # rendre un verdict sur un artefact de saisie.
    assert B._test_risques([])["etat"] == "indetermine"
    assert B._test_risques(None)["etat"] == "indetermine"


def test_greenfield_et_brownfield_ne_disent_pas_la_meme_chose():
    """UN DOSSIER BROWNFIELD INSTRUIT AVEC LA GRILLE DU GREENFIELD passe à
    côté de la seule chose qui compte : ce que le bâtiment existant peut
    encore accepter."""
    g = B._test_nature_projet("greenfield", None)["constat"]
    b = B._test_nature_projet("brownfield", None)["constat"]
    assert "capacité portante" in b.lower() or "PORTANTE" in b, b
    assert "foncière" in g, g
    assert B._test_nature_projet(None, None)["etat"] == "indetermine"


# ══════════════════════════════════════════════════════════════════════════
# 6. UN SEUL VERDICT — la greffe sur faisabilite_dc
# ══════════════════════════════════════════════════════════════════════════

def test_le_format_des_constats_n_a_pas_diverge():
    """LES DEUX MODULES ÉCRIVENT LE MÊME OBJET, chacun de son côté — c'est le
    seul sens possible, faisabilite_dc important business_case_dc. Une clé
    ajoutée d'un côté et pas de l'autre ferait un avis à deux formes."""
    a = set(B._constat("s", "favorable", "c", "f", "r"))
    b = set(FA._constat("s", "favorable", "c", "f", "r"))
    # faisabilite_dc ajoute `etat_nom`, que la greffe pose elle-même.
    assert a == b - {"etat_nom"}, (a, b)
    assert set(B.ETATS) == set(FA.ETATS), (B.ETATS, sorted(FA.ETATS))


def test_sans_business_case_l_avis_est_exactement_celui_d_avant():
    """LA GREFFE NE DOIT INVALIDER AUCUN DOSSIER DÉJÀ RENDU. Un appelant qui
    ne passe pas de business case obtient les cinq constats du chiffrage, et
    rien d'autre."""
    d, _ = _chiffrage()
    a = FA.avis(d)
    assert len(a["constats"]) == 5, [c["sujet"] for c in a["constats"]]
    assert a["par_discipline"] == {"chiffrage": 5, "business_case": 0}
    assert all(c["discipline"] == "chiffrage" for c in a["constats"])


def test_avec_business_case_les_constats_rejoignent_le_meme_avis():
    d, e = _chiffrage()
    bc = B.etude(20, devis=d, exploitation=e, prix_kw_mois=140,
                 mw_commercialises=9, annee_mise_en_service=2029,
                 annee_puissance_ferme=2031)
    a = FA.avis(d, business_case=bc)
    assert a["par_discipline"]["business_case"] == 8, a["par_discipline"]
    assert len(a["constats"]) == 13, len(a["constats"])
    # Un seul avis, une seule synthèse — et le bloquant du calendrier
    # électrique la fait basculer.
    assert a["avis"]["sens"] == "arret", a["avis"]
    assert "électricité" in a["avis"]["phrase"], a["avis"]["phrase"]


def test_l_avis_se_durcit_quand_la_demande_se_degrade():
    """LE POINT QUI COMPTE. Un avis qui resterait au même niveau avec un
    calendrier électrique incompatible ne vaudrait rien."""
    d, e = _chiffrage()
    bon = B.etude(20, devis=d, exploitation=e, annee_mise_en_service=2031,
                  annee_puissance_ferme=2029)
    mauvais = B.etude(20, devis=d, exploitation=e, annee_mise_en_service=2029,
                      annee_puissance_ferme=2031)
    poids = {"poursuivre": 0, "incomplet": 1, "conditions": 2, "arret": 3}
    a = FA.avis(d, business_case=bon)["avis"]["sens"]
    b = FA.avis(d, business_case=mauvais)["avis"]["sens"]
    assert poids[b] > poids[a], (a, b)


def test_les_constats_du_business_case_portent_leur_libelle_d_etat():
    """Sans `etat_nom`, la page afficherait une puce vide : le rendu lit ce
    libellé et non l'état technique."""
    d, e = _chiffrage()
    bc = B.etude(20, devis=d, exploitation=e)
    for c in FA.avis(d, business_case=bc)["constats"]:
        assert c.get("etat_nom"), c["sujet"]
        assert c.get("discipline") in ("chiffrage", "business_case"), c["sujet"]


def test_la_sante_du_module_verifie_ses_deux_proprietes():
    s = B.sante()
    assert s["vide_aucun_favorable"] is True
    assert s["calendrier_incompatible_bloque"] is True
    assert s["tous_portent_un_fondement"] and s["tous_portent_un_renversement"]


# ══════════════════════════════════════════════════════════════════════════
# 7. CE QUI MANQUE, ET LA PAGE
# ══════════════════════════════════════════════════════════════════════════

def test_ce_qui_manque_est_rendu_avec_ce_que_son_absence_empeche():
    """RÉCLAMER « LES DONNÉES MANQUANTES » fait remplir les champs faciles ;
    nommer le test qu'elles débloquent fait chercher la bonne donnée."""
    bc = B.etude(20)
    assert len(bc["manquantes"]) == len(B.ENTREES), bc["manquantes"]
    for m in bc["manquantes"]:
        assert len(m["empeche"]) > 40, m["cle"]
        assert len(m["ou"]) > 20, m["cle"]


def test_le_bloc_existe_dans_la_page_de_l_enveloppe():
    h = _lire("panorama.html")
    for ancre in ('id="fin-bc-plus"', 'id="fin-bc-prix"', 'id="fin-bc-ms"',
                  'id="fin-bc-pf"', 'id="fin-bc-risq"',
                  "function businessCase("):
        assert ancre in h, ancre


def test_la_page_ne_propose_aucun_prix_ni_aucune_annee_par_defaut():
    """UN PLACEHOLDER CHIFFRÉ FAIT OFFICE DE RECOMMANDATION au bout de deux
    lectures, et il ne se conteste pas puisqu'il n'est affirmé nulle part."""
    h = _lire("panorama.html")
    deb = h.index('id="fin-bc-plus"')
    corps = h[deb:h.index("</details>", deb)]
    for champ in ("fin-bc-prix", "fin-bc-ms", "fin-bc-pf", "fin-bc-mwc"):
        i = corps.index('id="%s"' % champ)
        balise = corps[corps.rindex("<input", 0, i):corps.index(">", i) + 1]
        assert "value=" not in balise, (champ, balise)
        m = re.search(r'placeholder="([^"]*)"', balise)
        assert m and not re.search(r"\d", m.group(1)), (champ, balise)


def test_la_page_lit_les_risques_au_referentiel():
    """Une liste figée dans la page annoncerait cinq risques le jour où le
    module en porterait six, et la phrase resterait crédible."""
    h = _lire("panorama.html")
    i = h.index("function risquesFormulaire(")
    corps = h[i:i + 900]
    assert "REF_BC.risques_connus" in corps, corps[:200]
    for cle in B.RISQUES_CONNUS:
        assert '"%s"' % cle not in corps, cle


def test_le_panneau_sentinel_annonce_le_business_case():
    """LE CHAPEAU EST CE QU'ON LIT SANS RIEN DÉPLIER, et c'est lui que la
    règle éprouve.

    Sa première version cherchait « business case » n'importe où dans le
    panneau : la mention subsistant dans un dépliant, elle restait verte alors
    que le chapeau ne l'annonçait plus. Un lecteur qui ne déplie rien ne
    saurait pas que le module éprouve la demande.
    """
    h = _lire("sentinel.html")
    deb = h.index('id="p-enveloppe"')
    corps = h[deb:h.index("</div>\n\n<div class=\"page", deb)]
    chapeau = corps[corps.index('class="page-lead'):corps.index("</p>",
                     corps.index('class="page-lead'))]
    assert "business case" in chapeau.lower(), chapeau
    assert "électricité" in chapeau, chapeau
    # Et le dépliant qui explique POURQUOI un devis parfait n'en est pas un.
    assert "tous du côté de l" in corps, corps[:600]


# ══════════════════════════════════════════════════════════════════════════
# 8. LE REVENU NE SE SAISIT PAS DEUX FOIS
# ══════════════════════════════════════════════════════════════════════════
# LE BLOC « CRÉATION DE VALEUR » DEMANDE UN REVENU, et le business case en
# calcule un : c'est la MÊME grandeur. Le laisser ressaisir ferait exister deux
# revenus pour le même projet — voisins, jamais identiques —, et c'est le plus
# flatteur des deux qu'on présenterait au comité. Il devient donc une
# PROPOSITION du menu de provenance, comme les autres : proposé, jamais posé.

import kpi_finance as K  # noqa: E402


def test_le_revenu_du_business_case_est_propose_au_bloc_de_valeur():
    p = K.propositions([700, 900], [20, 30], 10,
                       {"wacc": 0.08, "is_taux": 0.25},
                       revenu_business_case={"revenu_meur_an": 33.6,
                                             "formule": "20 MW × 140 €/kW/mois"})
    props = p["entrees"]["revenu_meur_an"]["propositions"]
    assert props, p["entrees"]["revenu_meur_an"]
    # CETTE RÈGLE ÉPROUVE LA PRÉSENCE ET LA VALEUR, pas la position : celle-ci
    # a sa propre règle. Deux règles qui affirment la même chose se couvrent
    # l'une l'autre, et la mutation qui casse la position tombe alors sur la
    # mauvaise — la règle dédiée cesse de prouver ce qu'elle annonce.
    repris = [x for x in props if x["origine"] == "business_case"]
    assert len(repris) == 1, [x["origine"] for x in props]
    assert repris[0]["valeur"] == 33.6, repris[0]
    assert "140" in repris[0]["formule"], repris[0]["formule"]


def test_il_arrive_en_tete_des_propositions():
    """L'ORDRE PORTE DU SENS. Les autres propositions sont des SEUILS calculés
    à rebours — « ce que le projet devrait rapporter » —, celle-ci est ce que
    le plan d'affaires déclaré rapporte. La mettre après ferait choisir un
    seuil comme s'il était une prévision."""
    p = K.propositions([700, 900], [20, 30], 10,
                       {"wacc": 0.08, "is_taux": 0.25},
                       revenu_business_case={"revenu_meur_an": 33.6})
    origines = [x["origine"] for x in p["entrees"]["revenu_meur_an"]["propositions"]]
    assert origines[0] == "business_case", origines
    assert "seuil" in origines[1:], origines


def test_la_proposition_previent_qu_elle_suppose_le_site_plein():
    """LE PIÈGE DE CETTE REPRISE. Le revenu du business case est celui de la
    PLEINE CHARGE ; ces trois indicateurs le supposent atteint. Le reprendre
    sans regarder le point mort donnerait une création de valeur pour un site
    qu'on n'a pas encore rempli."""
    p = K.propositions([700, 900], [20, 30], 10,
                       {"wacc": 0.08, "is_taux": 0.25},
                       revenu_business_case={"revenu_meur_an": 33.6})
    tete = p["entrees"]["revenu_meur_an"]["propositions"][0]
    assert "point mort" in tete["lecture"], tete["lecture"]
    assert "PLEINE CHARGE" in tete["lecture"], tete["lecture"]


def test_sans_business_case_les_propositions_sont_celles_d_avant():
    """LA GREFFE N'AJOUTE RIEN QUAND ELLE N'A RIEN À AJOUTER."""
    p = K.propositions([700, 900], [20, 30], 10,
                       {"wacc": 0.08, "is_taux": 0.25})
    origines = [x["origine"]
                for x in p["entrees"]["revenu_meur_an"]["propositions"]]
    assert "business_case" not in origines, origines


def test_la_page_envoie_le_revenu_et_nomme_sa_provenance():
    h = _lire("panorama.html")
    assert "revenu_business_case: revenuBusinessCase()" in h
    assert "function revenuBusinessCase(" in h
    # UNE ORIGINE SANS LIBELLÉ s'afficherait en clé technique sous le champ.
    i = h.index("var KPI_ORIG_NOM = {")
    assert 'business_case: "business case"' in h[i:i + 400], h[i:i + 400]


def test_le_revenu_repris_suit_le_pays_du_dossier_ouvert():
    """DEUX CHOIX DE PAYS DIVERGERAIENT. `enveloppe()` retient déjà le pays du
    dossier ouvert ; refaire ce choix ferait porter la création de valeur sur
    l'enveloppe d'un pays et le revenu d'un autre — dont le prix de
    l'électricité, donc le coût, donc le point mort ne sont pas les mêmes."""
    h = _lire("panorama.html")
    i = h.index("function revenuBusinessCase(")
    corps = h[i:i + 1400]
    assert "enveloppe()" in corps, corps[:400]
    assert "x.pays === e.pays" in corps, corps[:600]


def test_la_route_transmet_le_revenu_du_business_case():
    """LE MAILLON QU'AUCUNE RÈGLE NE TENAIT. Le moteur le propose et la page
    l'envoie — mais entre les deux, la route peut cesser de le transmettre
    sans qu'aucune règle ne s'en aperçoive : le module reste juste, la page
    reste juste, et la proposition disparaît de l'écran.

    Une mutation l'a montré ; la règle passe par la ROUTE, pas par le module.
    """
    import app as A
    A.app.config["TESTING"] = True
    c = A.app.test_client()
    with c.session_transaction() as sess:
        sess["is_conseilprev"] = True
    r = c.post("/api/kpi-finance", json={
        "capex_meur": [700, 900], "opex_an_meur": [20, 30], "annees": 10,
        "hypotheses": {"wacc": 0.08, "is_taux": 0.25},
        "revenu_business_case": {"revenu_meur_an": 33.6,
                                 "formule": "20 MW × 140 €/kW/mois"},
    }, headers={"Origin": "http://localhost"})
    assert r.status_code == 200, r.status_code
    props = r.get_json()["propositions"]["entrees"]["revenu_meur_an"]["propositions"]
    origines = [x["origine"] for x in props]
    assert "business_case" in origines, origines
    assert props[0]["valeur"] == 33.6, props[0]


def test_la_route_refuse_un_revenu_absurde_sans_tomber():
    """Une valeur illisible ou hors bornes ne doit pas devenir une proposition
    — ni faire tomber la réponse entière, qui porte six autres entrées."""
    import app as A
    A.app.config["TESTING"] = True
    c = A.app.test_client()
    with c.session_transaction() as sess:
        sess["is_conseilprev"] = True
    for mauvais in ({"revenu_meur_an": "abc"}, {"revenu_meur_an": -5},
                    {"revenu_meur_an": 10 ** 9}, "pas un objet"):
        r = c.post("/api/kpi-finance", json={
            "capex_meur": [700, 900], "opex_an_meur": [20, 30], "annees": 10,
            "hypotheses": {"wacc": 0.08, "is_taux": 0.25},
            "revenu_business_case": mauvais,
        }, headers={"Origin": "http://localhost"})
        assert r.status_code == 200, (mauvais, r.status_code)
        props = (r.get_json()["propositions"]["entrees"]["revenu_meur_an"]
                 ["propositions"])
        assert "business_case" not in [x["origine"] for x in props], mauvais
