"""LE CADRE NIST ET LE TOP 10 OWASP — DEUX RÉFÉRENTIELS QUI NE SE CERTIFIENT PAS.

CE QUE CES DEUX MODULES AJOUTENT AUX SEPT AUTRES, et c'est ce qui les rend
délicats : ils ne délivrent rien. ISO 42001 délivre un certificat, le RGPD et
NIS 2 sont du droit. Le cadre NIST est volontaire, le Top 10 est un inventaire.
« Conforme NIST AI RMF » et « conforme OWASP » ne veulent rien dire — et ce sont
exactement les phrases qu'un commercial pressé écrira sur une plaquette.

CE QUE CES RÈGLES ÉPROUVENT :
  1. les comptes du cadre sont ceux du document — 4 / 19 / 72 — et ils se
     recomptent plutôt que de se croire ;
  2. la non-certifiabilité voyage avec CHAQUE réponse, jamais en note ;
  3. le profil est rendu PAR FONCTION et jamais en note globale — une moyenne
     des quatre monte quand on cartographie beaucoup et qu'on ne décide rien ;
  4. l'avertissement de socle tombe quand l'aval devance GOVERN ;
  5. le pont OWASP → annexe A ne cite que des mesures qui existent, et il
     laisse DÉLIBÉRÉMENT des risques sans mesure en face ;
  6. la réserve de vérification d'OWASP est déclarée : owasp.org est refusé
     par le mandataire de sortie, la liste n'a pas pu être recoupée.
"""
import io
import json
import os
import re
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import iso42001        # noqa: E402
import nist_ai_rmf as N  # noqa: E402
import owasp_llm as O   # noqa: E402


def _lire(nom):
    with io.open(os.path.join(ICI, nom), encoding="utf-8") as f:
        return f.read()


# ══════════════════════════════════════════════════════════════════════════
#  1. LES COMPTES SONT CEUX DU DOCUMENT
# ══════════════════════════════════════════════════════════════════════════

def test_le_cadre_a_la_forme_du_document():
    """4 FONCTIONS, 19 CATÉGORIES, 72 SOUS-CATÉGORIES.

    Ces nombres ont été comptés dans NIST AI 100-1, pas repris d'un
    commentaire. Une catégorie perdue en chemin ne planterait nulle part :
    l'écran en afficherait dix-huit, et personne ne recompte.
    """
    assert len(N.FONCTIONS) == 4
    assert len(N.CATEGORIES) == 19, len(N.CATEGORIES)
    assert len(N.SOUS_CATEGORIES) == 72, len(N.SOUS_CATEGORIES)
    assert len(N.CARACTERISTIQUES) == 7
    assert len(N.RISQUES_GENAI) == 12


def test_la_repartition_par_fonction_est_celle_du_document():
    """GOVERN 19, MAP 18, MEASURE 22, MANAGE 13.

    Le total peut rester juste alors que la répartition est fausse : une
    sous-catégorie déplacée d'une fonction à l'autre laisse 72 intact.
    """
    compte = {}
    for cle, _ in N.SOUS_CATEGORIES:
        compte[cle.split()[0]] = compte.get(cle.split()[0], 0) + 1
    assert compte == {"GOVERN": 19, "MAP": 18, "MEASURE": 22, "MANAGE": 13}, compte


def test_chaque_sous_categorie_se_rattache_a_une_categorie_declaree():
    """UNE SOUS-CATÉGORIE ORPHELINE COMPTE DANS LES 72 ET NE S'AFFICHE JAMAIS."""
    orphelines = [c for c, _ in N.SOUS_CATEGORIES
                  if c.rsplit(".", 1)[0] not in N.CATEGORIES_PAR_CLE]
    assert not orphelines, orphelines[:6]


# ══════════════════════════════════════════════════════════════════════════
#  2. CE QUI NE SE CERTIFIE PAS LE DIT, PARTOUT
# ══════════════════════════════════════════════════════════════════════════

def test_le_cadre_NIST_ne_se_declare_jamais_certifiable():
    assert all(not s["certifiable"] for s in N.SOURCES)
    assert N.referentiel()["certifiable"] is False
    r = N.evaluer({"GOVERN 1": "tenu"}, aujourdhui="2026-09-19")
    assert r["certifiable"] is False
    assert "certifie" in r["reserve"] or "certifi" in r["reserve"]


def test_la_reserve_voyage_avec_CHAQUE_evaluation():
    """RELÉGUÉE EN NOTE DE BAS D'ÉCRAN, elle se lirait après qu'on a déjà
    retenu un score — et c'est le score qu'on citerait en comité."""
    r = N.evaluer({"MAP 1": "prouve"}, aujourdhui="2026-09-19")
    assert len(r["reserve"]) > 120, "la réserve a été raccourcie ou vidée"
    o = O.evaluer({"LLM01": "partiel"})
    assert len(o["reserve"]) > 100
    assert o["a_verifier"]["pourquoi"], (
        "la réserve de vérification d'OWASP a perdu son motif")


def test_OWASP_declare_n_avoir_PAS_pu_etre_reverifie():
    """owasp.org EST REFUSÉ PAR LE MANDATAIRE DE SORTIE de la machine de
    construction. Un référentiel qu'on n'a pas pu rouvrir se signale ; il ne
    se présente pas comme vérifié."""
    av = O.A_VERIFIER
    assert "owasp" in av["pourquoi"].lower()
    assert av["quoi_faire"], "la réserve ne dit pas quoi faire"
    page = _lire("sentinel.html")
    assert 'id="owasp-reserve"' in page, (
        "l'écran ne réserve aucune place pour la réserve de vérification")


# ══════════════════════════════════════════════════════════════════════════
#  3. LE PROFIL — PAR FONCTION, JAMAIS EN NOTE GLOBALE
# ══════════════════════════════════════════════════════════════════════════

def test_aucune_note_GLOBALE_n_est_rendue():
    """ADDITIONNER LES QUATRE FONCTIONS produit un chiffre qui monte quand on
    cartographie beaucoup et qu'on ne décide rien — c'est-à-dire sur le profil
    le plus répandu, et celui que le cadre est écrit pour corriger.

    La règle cherche la VALEUR, pas un nom de champ : interdire la clé
    « global » n'empêcherait pas le même nombre de revenir sous « score ».
    """
    etats = {"GOVERN 1": "absent", "MAP 1": "prouve",
             "MEASURE 1": "prouve", "MANAGE 1": "prouve"}
    r = N.evaluer(etats, aujourdhui="2026-09-19")
    moyenne = (0 + 3 + 3 + 3) / 4.0
    interdits = {moyenne, round(moyenne, 1), round(moyenne, 2),
                 round(moyenne / 3.0 * 100, 1)}
    trouves = []

    def fouiller(x, chemin):
        if isinstance(x, dict):
            for k, v in x.items():
                fouiller(v, chemin + "." + str(k))
        elif isinstance(x, list):
            for i, v in enumerate(x):
                fouiller(v, "%s[%d]" % (chemin, i))
        elif isinstance(x, float) and x in interdits:
            trouves.append(chemin + " = " + repr(x))

    fouiller(r, "r")
    assert not trouves, "une note globale est rendue : %s" % trouves


def test_l_avertissement_de_socle_tombe_quand_l_aval_devance_GOVERN():
    """LE CŒUR DU MODULE. Une maison qui note bien sur le traitement et mal
    sur la gouvernance ne gère rien — elle éteint des feux. Sans cet
    avertissement, le module rendrait quatre notes dont trois flatteuses."""
    devant = N.evaluer({"GOVERN 1": "absent", "MAP 1": "prouve"},
                       aujourdhui="2026-09-19")
    assert devant["tete"] == "aval_devant_socle", devant["tete"]
    assert devant["devancent_le_socle"]
    # ET LA RÉCIPROQUE : sans elle, la règle mesurerait « la tête est
    # toujours aval_devant_socle », ce qui serait vrai pour une raison sans
    # rapport avec ce qu'elle prétend.
    accorde = N.evaluer({"GOVERN 1": "prouve", "MAP 1": "prouve"},
                        aujourdhui="2026-09-19")
    assert accorde["tete"] == "coherent", accorde["tete"]
    assert accorde["devancent_le_socle"] == []


def test_un_profil_vide_n_est_pas_un_profil_a_zero():
    r = N.evaluer({}, aujourdhui="2026-09-19")
    assert r["tete"] == "vide"
    assert all(p["note"] is None for p in r["profils"]), (
        "une fonction non renseignée est notée : zéro et « pas regardé » se "
        "ressemblent sur un écran et ne se ressemblent pas en revue")


@pytest.mark.parametrize("etats,motif", [
    ({"GOUVERNANCE 1": "tenu"}, "categories_inconnues"),
    ({"GOVERN 1": "excellent"}, "etats_inconnus"),
])
def test_l_evaluation_NOMME_son_refus(etats, motif):
    r = N.evaluer(etats)
    assert r["ok"] is False and r["motif"] == motif, r


# ══════════════════════════════════════════════════════════════════════════
#  4. LE PONT OWASP → ISO 42001
# ══════════════════════════════════════════════════════════════════════════

def test_le_pont_ne_cite_que_des_mesures_QUI_EXISTENT():
    """UNE MESURE INVENTÉE SE LIRAIT COMME UN RATTACHEMENT et ne mènerait
    nulle part — et c'est le genre de pont qu'on ne revérifie jamais."""
    fautes = [(r["cle"], c) for r in O.RISQUES for c in r["iso42001"]
              if c not in iso42001.MESURES]
    assert not fautes, fautes


def test_le_pont_laisse_DELIBEREMENT_des_risques_sans_mesure():
    """SI TOUT TROUVAIT UNE MESURE, LE PONT NE DIRAIT RIEN.

    Il ne servirait qu'à confirmer « la norme couvre tout » — ce qui est
    faux, et ce que le module est écrit pour contredire. Ce sont ces
    risques-là qui donnent sa valeur à la page.
    """
    hors = [r["cle"] for r in O.RISQUES if r["couvert_par_la_norme"] == "non"]
    assert hors, "plus aucun risque hors portée : le pont ne dit plus rien"
    for cle in hors:
        assert not O.RISQUES_PAR_CLE[cle]["iso42001"], (
            "%s est déclaré hors portée tout en citant des mesures" % cle)


def test_l_angle_mort_est_ce_qui_n_est_NI_traite_NI_couvert():
    """LE CALCUL QUI COMPTE. Un risque traité chez soi n'est pas un angle
    mort, même si la norme l'ignore — et un risque que la norme couvre n'en
    est pas un non plus."""
    hors = [r["cle"] for r in O.RISQUES if r["couvert_par_la_norme"] == "non"]
    # TOUT TRAITÉ : plus aucun angle mort, bien que la norme n'y soit pour rien.
    tout = O.evaluer({c: "oui" for c in hors}, certifie_42001=True)
    assert tout["angles_morts"] == [], tout["angles_morts"]
    # RIEN DIT : aucun angle mort, parce qu'un angle mort suppose qu'on ait
    # dit ne pas traiter. La liste « hors portée » reste rendue, elle : c'est
    # une propriété de la NORME et pas de la maison.
    muet = O.evaluer({}, certifie_42001=True)
    assert muet["angles_morts"] == [], (
        "un dossier vide nomme des angles morts sous un titre qui annonce "
        "que rien n'est renseigné : %s" % muet["angles_morts"])
    assert sorted(muet["hors_annexe_a"]) == sorted(hors)
    assert muet["tete"] == "vide", muet["tete"]
    # DÉCLARÉ NON TRAITÉ : les trois ressortent, et la tête change.
    dit = O.evaluer({c: "non" for c in hors}, certifie_42001=True)
    assert sorted(dit["angles_morts"]) == sorted(hors)
    assert dit["tete"] == "certifie_mais_decouvert", dit["tete"]


def test_aucune_note_SUR_DIX_n_est_rendue():
    """« 7/10 OWASP » SE CITERAIT EN COMITÉ et ne voudrait rien dire : les dix
    ne pèsent pas pareil, et l'OWASP n'a jamais présenté la liste comme un
    barème."""
    r = O.evaluer({"LLM01": "oui", "LLM02": "oui", "LLM03": "oui"})
    texte = json.dumps(r, ensure_ascii=False)
    assert "/10" not in texte, "une note sur dix est rendue"
    assert not any(isinstance(v, float) and 0 < v <= 10
                   for v in r.values() if isinstance(v, float))


def test_le_millesime_accompagne_TOUJOURS_la_liste():
    """« LE TOP 10 OWASP LLM » SANS SON ANNÉE désigne une liste qu'on n'a pas
    relue — le millésime précédent ignorait trois des dix risques actuels."""
    assert O.SOURCE["millesime"]
    r = O.evaluer({"LLM01": "oui"})
    assert r["millesime"] == O.SOURCE["millesime"]
    assert O.SOURCE["millesime"] in r["reserve"]


# ══════════════════════════════════════════════════════════════════════════
#  5. L'ÉCRAN, LES ROUTES, ET LES NEUF NORMES
# ══════════════════════════════════════════════════════════════════════════

def test_l_ecran_ne_recopie_AUCUN_enonce_du_cadre():
    """SOIXANTE-DOUZE ÉNONCÉS RECOPIÉS auraient divergé du module au premier
    amendement — et le NIST annonce lui-même réviser le cadre."""
    page = _lire("sentinel.html")
    js = _lire("sentinel.page.js")
    fautes = [c for c, t in N.SOUS_CATEGORIES if t[:60] in page or t[:60] in js]
    assert not fautes, "énoncé(s) recopiés : %s" % fautes[:5]


def test_l_ecran_appelle_bien_les_deux_referentiels():
    """SANS CELA, LA RÈGLE D'AU-DESSUS SERAIT TRIVIALEMENT VRAIE : une page
    qui n'appelle rien ne recopie évidemment rien."""
    js = _lire("sentinel.page.js")
    for route in ("/api/nist-ai-rmf/referentiel", "/api/owasp-llm/referentiel"):
        assert "fetch('" + route + "')" in js, "la vue n'appelle pas %s" % route


@pytest.mark.parametrize("pid", ["nist-profil", "nist-cadre", "nist-genai",
                                 "owasp-dix", "owasp-pont"])
def test_chaque_panneau_existe_UNE_SEULE_FOIS_et_porte_son_guide(pid):
    """LE LIEN PROFOND `?goto=` VISE UN PANNEAU UNIQUE. Deux panneaux de même
    identifiant, et le lien ouvre le premier — au hasard de l'ordre du
    fichier."""
    page = _lire("sentinel.html")
    assert page.count('id="p-%s"' % pid) == 1, (
        "%d panneau(x) portent cet identifiant" % page.count('id="p-%s"' % pid))
    js = _lire("sentinel.page.js")
    assert "'%s': {" % pid in js or "'%s':{" % pid in js, (
        "le panneau %s n'a pas d'entrée dans PAGE_GUIDES" % pid)


def test_les_deux_cartes_de_l_accueil_menent_a_leur_module():
    """UNE CARTE QUI NE MÈNE NULLE PART est pire qu'une carte absente : elle
    promet un module."""
    index = _lire("index.html")
    for cible in ("/sentinel?goto=nist-profil", "/sentinel?goto=owasp-dix"):
        assert cible in index, "l'accueil ne mène pas à %s" % cible


def test_le_titre_de_l_accueil_compte_les_NEUF_cartes():
    """LE NOMBRE EST DÉRIVÉ DES DEUX CÔTÉS, jamais écrit ici : ce qui se
    mesure est l'accord entre le titre et la grille."""
    index = _lire("index.html")
    js = _lire("index.page.js")
    i = index.index('id="normes"')
    bloc = index[i:index.index("</section>", i)]
    cartes = len(re.findall(r'<div class="nc ', bloc))
    titres = set(re.findall(r'"nr\.ttl":"(\d+)', js))
    assert len(titres) == 1, "les langues annoncent %s" % titres
    assert int(titres.pop()) == cartes, (
        "le titre et la grille ne comptent pas pareil")
    assert cartes == 9, "neuf normes attendues, %d trouvées" % cartes
