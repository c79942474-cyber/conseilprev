"""Les cinq communes de la carte, et l'emprunt ODbL qu'elles ont coûté.

CE QUI A DÉCLENCHÉ CE FICHIER. La vérification de la carte « Les Echos » a nommé
onze sites français ; cinq communes n'existaient nulle part dans le référentiel
— Val-de-Reuil, Amilly, Saint-Saturnin, Prévessin-Moëns, Bruges. Elles y entrent
avec un POINT GÉOGRAPHIQUE repris de DCWatch, base publiée sous ODbL, faute de
tout géocodeur joignable.

CE QUE CES RÈGLES PROTÈGENT, ET LA FAUTE QU'ELLES EMPÊCHENT :

  1. UN GARDE-FOU QUI RESTE VERT PENDANT QU'ON LE CONTOURNE.
     `test_le_referentiel_de_centres_de_donnees_n_importe_rien_de_dcwatch`
     interdit l'`import`. Recopier cinq coordonnées à la main n'a besoin
     d'aucun import : la règle serait restée verte pendant que ce qu'elle
     gardait était entamé. C'est exactement le défaut corrigé la veille sur la
     mesure des documents — une règle qui passe pour une raison sans rapport
     avec ce qu'elle prétend. L'interdit muet devient donc un BUDGET DÉCLARÉ :
     ces cinq lignes, nommées, attribuées, comptées, et pas une de plus.

  2. QUE L'EMPRUNT GROSSISSE SANS DÉCISION. Cinq points sur cinq cent vingt se
     défendent par l'insubstantialité ; cinquante, non. C'est l'AMPLEUR, pas le
     principe, qui ferait basculer la lecture de l'article 4.4 — d'où un
     plafond, et une règle qui le tient.

  3. QUE LA PUISSANCE SUIVE LE POINT. La tentation est immédiate : la base
     porte les MW à côté des coordonnées. Ce sont des estimations de BÂTIMENT
     par imagerie satellite. `capacite_mw` reste nul sur les 254 lignes.

  4. QUE LA MENTION DE PROVENANCE RESTE EN ARRIÈRE. L'article 4.3 veut qu'elle
     accompagne ce qui est servi. Elle est dans chaque note ET dans la charge.

  5. QUE LA PROSE SE DÉSYNCHRONISE DES COMPTES. Cinq lignes de plus déplacent
     trois nombres écrits en toutes lettres, et `sante()` le vérifie.
"""
import os
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import datacentres as D  # noqa: E402
import dcwatch  # noqa: E402

# Les cinq communes attendues, écrites ici et nulle part ailleurs : c'est la
# liste de référence contre laquelle le référentiel est comparé.
COMMUNES = ("Val-de-Reuil", "Amilly", "Saint-Saturnin", "Prevessin-Moens", "Bruges")

# LE PLAFOND. Il n'est pas décoratif : cinq points sur cinq cent vingt se
# défendent par l'insubstantialité, cinquante non.
PLAFOND_EMPRUNTS = 5


def _empruntes():
    return [s for s in D.SITES if s.get("point_source")]


# ── 1. Les cinq communes sont là, une ligne chacune ────────────────────────

def test_les_cinq_communes_sont_au_referentiel():
    villes = [s["ville"] for s in D.SITES if s.get("pays") == "FR"]
    for c in COMMUNES:
        assert villes.count(c) == 1, (
            "%s : %d ligne(s) au lieu d'une" % (c, villes.count(c)))


def test_val_de_reuil_tient_en_une_ligne_pour_deux_batiments():
    """La carte annonce « 2 data centers » ; la base porte deux enregistrements
    à la MÊME adresse et au MÊME point. Deux lignes ici feraient croire à deux
    sites distants — le référentiel agrège déjà les campus OVHcloud ainsi."""
    lot = [s for s in D.SITES if s["ville"] == "Val-de-Reuil"]
    assert len(lot) == 1
    assert "deux" in lot[0]["note"].lower() or "2 data centers" in lot[0]["note"]


def test_les_cinq_sont_en_service_et_en_france():
    for s in _empruntes():
        assert s["pays"] == "FR"
        assert s["statut"] == "service"
        assert s["source_type"] == "presse"
        assert s["confiance"] == "moyenne"
        assert s.get("lat") is not None and s.get("lon") is not None


def test_le_cern_dit_qu_il_n_est_pas_le_doublon_de_meyrin():
    """Le référentiel porte déjà « CERN Geneva » (Meyrin, CH) à 2,6 km, importé
    de PeeringDB. Sans un mot, la nouvelle ligne se lit comme une répétition."""
    p = [s for s in D.SITES if s["ville"] == "Prevessin-Moens"][0]
    assert "Meyrin" in p["note"], "la note ne distingue pas les deux centres du CERN"
    assert p["pays"] == "FR"
    meyrin = [s for s in D.SITES if s.get("nom_site") == "CERN Geneva"]
    assert meyrin and meyrin[0]["pays"] == "CH", (
        "la ligne suisse a disparu : la note en parle dans le vide")


# ── 2. L'emprunt est déclaré, borné, attribué ──────────────────────────────

def test_l_emprunt_est_exactement_celui_qui_est_declare():
    """Ni plus — un sixième emprunt entrerait sans décision — ni moins : une
    ligne qui perdrait sa marque redeviendrait un point d'origine inconnue."""
    marques = {s["ville"] for s in _empruntes()}
    assert marques == set(COMMUNES), (
        "les lignes marquées ne sont pas les cinq déclarées : %s" % sorted(marques))


def test_l_emprunt_ne_depasse_pas_le_plafond():
    n = len(_empruntes())
    assert n <= PLAFOND_EMPRUNTS, (
        "%d lignes empruntées à une base ODbL : au-delà de %d, l'argument "
        "d'insubstantialité ne tient plus et l'article 4.4 s'applique"
        % (n, PLAFOND_EMPRUNTS))


def test_chaque_ligne_empruntee_porte_la_mention_de_provenance():
    """Article 4.3 : la mention accompagne le contenu. Une notice rangée dans
    une page voisine ne suit pas la ligne qu'elle doit accompagner."""
    for s in _empruntes():
        assert D.MENTION_ODBL in s["note"], (
            "%s : la note ne porte pas la mention ODbL" % s["ville"])
        assert "DCWatch" in s["note"]


def test_la_mention_recopiee_est_mot_pour_mot_celle_de_la_licence():
    """`datacentres.py` n'importe pas `dcwatch` — une règle l'interdit. La
    mention y est donc recopiée, et deux copies dérivent : ce contrôle est le
    seul lien entre elles."""
    assert D.MENTION_ODBL == dcwatch.MENTION, (
        "la mention du référentiel a divergé de celle du module ODbL")


def test_la_charge_servie_porte_la_mention_et_nomme_les_emprunts():
    a = D.assemble()
    assert a["mention_odbl"] == D.MENTION_ODBL
    assert len(a["emprunts_odbl"]) == len(_empruntes())
    assert all(n for n in a["emprunts_odbl"]), "un emprunt servi sans nom"


def test_le_risque_residuel_est_nomme_et_non_tranche():
    txt = " ".join(D.LIMITES)
    assert "ODbL" in txt and "4.4" in txt
    assert "insubstantialite" in txt.lower(), (
        "seule la lecture stricte est exposée : la limite tranche au lieu de "
        "poser la question")
    for c in COMMUNES:
        assert c in txt, "%s n'est pas nommée dans les limites" % c


# ── 3. Ce que l'emprunt n'a PAS fait entrer ────────────────────────────────

def test_aucune_estimation_de_la_base_n_a_suivi_le_point():
    """LA TENTATION IMMÉDIATE : la puissance est à côté des coordonnées dans la
    même ligne de la base. Elle reste dehors, et pas seulement elle."""
    for s in _empruntes():
        for champ in ("capacite_mw", "gabarit", "eau_m3_an", "elec_gwh_an",
                      "annee_service", "investissement_meur"):
            assert not s.get(champ), (
                "%s : le champ « %s » porte une valeur — seul le point devait "
                "être repris" % (s["ville"], champ))


def test_l_interdit_de_puissance_tient_toujours_sur_tout_le_referentiel():
    for nom, lot in (("SITES", D.SITES), ("assemble()", D.assemble()["sites"])):
        avec = [s for s in lot if s.get("capacite_mw")]
        assert not avec, "%d site(s) de %s portent une capacite_mw" % (len(avec), nom)


def test_le_referentiel_n_importe_toujours_pas_le_module_odbl():
    """L'emprunt est fait de valeurs recopiées, pas d'un accès à la base : le
    référentiel servi ne la consomme pas à chaque appel."""
    import ast
    src = open(os.path.join(ICI, 'datacentres.py'), encoding='utf-8').read()
    importe = [n for n in ast.walk(ast.parse(src))
               if isinstance(n, (ast.Import, ast.ImportFrom))
               and 'dcwatch' in ast.unparse(n)]
    assert not importe


# ── 4. Les comptes et la prose ont suivi ───────────────────────────────────

def test_la_sante_ne_signale_rien():
    """C'est ce qui prouve que la prose des LIMITES a suivi les comptes :
    `_limite_couverture` compare la phrase au dénombrement réel."""
    assert D.sante()["problemes"] == []


def test_la_couverture_francaise_est_derivee_du_compte_reel():
    c = D.couverture()["FR"]
    reels = [s for s in D.SITES if s.get("pays") == "FR"]
    assert c["porte"] == len(reels) == 38
    assert c["porte_referentiel"] == 18
    assert c["porte_registre"] == 20


def test_en_lettres_couvre_dix_sept_a_dix_neuf():
    """LE DÉFAUT QUE CE CHANTIER A RÉVEILLÉ. `_LETTRES` s'arrête à seize,
    `_DIZAINES` commence à vingt : la fonction rendait le CHIFFRE pour
    dix-sept, dix-huit et dix-neuf. `_limite_couverture` aurait alors exigé
    « 18 » dans la prose — ce que son propre docstring interdit, un « 18 » se
    lisant dans n'importe quelle date du texte."""
    assert D.en_lettres(17) == "dix-sept"
    assert D.en_lettres(18) == "dix-huit"
    assert D.en_lettres(19) == "dix-neuf"
    assert D.en_lettres(16) == "seize"
    assert D.en_lettres(20) == "vingt"


def test_la_version_a_bouge_avec_le_referentiel():
    assert D.VERSION > "2026-08-d", (
        "254 lignes servies sous le numéro de version de 249 : un consommateur "
        "qui compare des versions ne verrait pas le changement")


# ── 5. Aucun doublon involontaire ──────────────────────────────────────────

def test_aucun_point_emprunte_ne_double_une_ligne_existante():
    """Sauf le CERN, dont la note documente les 2,6 km qui séparent Prévessin
    de Meyrin. Un doublon non dit gonfle silencieusement le dénombrement."""
    import math

    def km(a, b, c, d):
        return 111.0 * math.hypot(a - c, (b - d) * math.cos(math.radians(a)))

    for s in _empruntes():
        for autre in D.SITES:
            if autre is s or autre.get("lat") is None:
                continue
            d = km(s["lat"], s["lon"], autre["lat"], autre["lon"])
            if d < 2.0:
                assert False, ("%s est à %.1f km de « %s » : doublon probable"
                               % (s["ville"], d, autre.get("nom_site")))
