# -*- coding: utf-8 -*-
"""Le FinOps de l'IA — et la seule règle qui décide de tout le module.

UN VOLUME ABSENT NE VAUT PAS ZÉRO EURO.

C'est le piège que `kpi_finance` décrit pour l'EVA — « un EVA nul faute de
revenu se lirait "ce projet ne crée pas de valeur" ; c'est faux, il se lit
"personne n'a encore dit ce qu'il rapporte" » — et il est pire ici, parce qu'un
total de zéro RASSURE. Un parc de vingt systèmes dont trois sont instruits
affiche un coût mensuel crédible, et le comité qui le lit conclut que l'IA coûte
peu. Personne ne le contredit : un total ne dit pas ce qu'il ignore.

CE QUE CES RÈGLES ÉPROUVENT, dans cet ordre :

  · qu'aucun chemin ne fabrique un zéro — ni un volume vide, ni une unité de
    facturation qu'on ne sait pas chiffrer, ni un modèle sans tarif relevé ;
  · que la couverture accompagne TOUJOURS le montant, dans la structure comme
    à l'écran, parce que c'est elle qui en décide la lecture ;
  · que les devises ne s'additionnent pas entre elles ;
  · que le dimensionnement rend une QUESTION et jamais un verdict ;
  · qu'un plafond posé sur un groupe non instruit sorte comme non vérifiable,
    et non comme respecté — un vert par ignorance est pire qu'un rouge.

CE QU'ELLES N'ÉPROUVENT PAS, ET POURQUOI. Aucune ne vérifie que les tarifs sont
« les bons » : ce sont des prix catalogue relevés à une date, et cette date est
le seul fait vérifiable ici. Une règle qui figerait un montant deviendrait
fausse à la première révision tarifaire, en désignant un défaut du code là où il
n'y aurait qu'un marché qui bouge.
"""
import datetime
import os
import re
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import finops_ia as F                                              # noqa: E402


def _sys(**champs):
    base = {"id": 1, "nom": "Système de recette"}
    base.update(champs)
    return base


COMPLET = _sys(modele="claude-sonnet-5", unite_facturation="jetons",
               volume_entree_mois=10_000_000, volume_sortie_mois=1_000_000,
               volume_source="console de facturation, relevé du 31/08",
               service="Support", centre_cout="CC-410",
               classe_tache="extraction")


# ═══════════════════════════════════════════════════════════════════════════
#  1. LE POINT QUI DÉCIDE : AUCUN CHEMIN NE FABRIQUE UN ZÉRO
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("manque,attendu", [
    ({"volume_entree_mois": None, "volume_sortie_mois": None}, "volume"),
    ({"volume_entree_mois": "", "volume_sortie_mois": ""}, "volume"),
    ({"volume_source": ""}, "source"),
    ({"modele": ""}, "modèle"),
    ({"modele": "un-modele-sans-tarif"}, "tarif"),
    ({"unite_facturation": ""}, "unité"),
    ({"unite_facturation": "sieges"}, "sieges"),
    ({"unite_facturation": "poussieres"}, "inconnue"),
])
def test_LE_POINT_QUI_DECIDE_aucune_lacune_ne_se_lit_zero_euro(manque, attendu):
    """HUIT MANIÈRES DE NE PAS SAVOIR, ET AUCUNE NE RESSORT À ZÉRO.

    Chaque cas est une lacune réelle rencontrée sur un registre : le champ
    laissé vide, le chiffre sans provenance, le modèle d'un éditeur dont le
    tarif n'est pas relevé, la facturation au siège qu'une table de prix au
    jeton ne sait pas traiter. Le montant vaut None, `instruit` vaut faux, et
    le motif nomme ce qui manque — sans quoi personne ne saurait quoi
    corriger."""
    ligne = F.cout_ligne(dict(COMPLET, **manque))
    assert ligne["instruit"] is False, ligne
    assert ligne["montant"] is None, (
        "une lacune rend un montant : c'est un zéro déguisé — %s" % ligne)
    assert ligne["motif"], "le refus ne dit pas ce qui manque"
    assert attendu in ligne["motif"], (manque, ligne["motif"])


def test_un_volume_reellement_nul_se_distingue_d_un_champ_vide():
    """UN SYSTÈME QUI N'A RIEN CONSOMMÉ CE MOIS-CI EXISTE, et son coût est zéro
    — un vrai zéro, celui-là. Le confondre avec un champ vide effacerait la
    seule information que ce module produit : la différence entre « rien
    consommé » et « rien déclaré »."""
    nul = F.cout_ligne(dict(COMPLET, volume_entree_mois=0, volume_sortie_mois=0))
    assert nul["instruit"] is True
    assert nul["montant"] == 0.0

    vide = F.cout_ligne(dict(COMPLET, volume_entree_mois="", volume_sortie_mois=""))
    assert vide["instruit"] is False and vide["montant"] is None


def test_le_montant_suit_la_formule_et_la_formule_est_dite():
    """Le calcul est une multiplication, et il est vérifiable à la main : c'est
    la condition pour qu'un contradicteur puisse le refaire."""
    t = F.TARIFS["claude-sonnet-5"]
    attendu = (10_000_000 / 1e6) * t["entree"] + (1_000_000 / 1e6) * t["sortie"]
    ligne = F.cout_ligne(COMPLET)
    assert ligne["montant"] == round(attendu, 2)
    assert ligne["devise"] == t["devise"]
    assert "1e6" in ligne["formule"], "la formule n'est pas rendue"


# ═══════════════════════════════════════════════════════════════════════════
#  2. LA COUVERTURE ACCOMPAGNE TOUJOURS LE MONTANT
# ═══════════════════════════════════════════════════════════════════════════

def test_un_parc_entierement_non_instruit_ne_rend_pas_zero():
    """LE CAS QUI COÛTE LE PLUS CHER. Vingt systèmes déclarés, aucun chiffré :
    le total doit être ILLISIBLE, pas nul. `lisible` est faux et les montants
    valent None — un appelant qui ne lirait que le montant tombe sur None."""
    parc = [_sys(id=i, nom="S%d" % i) for i in range(20)]
    couts = F.cout_parc(parc)
    assert couts["lisible"] is False
    assert couts["mensuel_par_devise"] is None
    assert couts["annuel_par_devise"] is None
    assert couts["couverture"]["instruites"] == 0
    assert couts["couverture"]["total"] == 20


def test_le_total_ne_sort_jamais_sans_sa_couverture():
    """LA STRUCTURE INTERDIT DE CITER L'UN SANS L'AUTRE. Ce n'est pas une
    commodité de mise en page : c'est la couverture qui décide si le montant se
    lit. Un `cout_parc` qui rendrait un flottant nu permettrait de l'afficher
    seul, et c'est exactement l'usage qu'on veut rendre impossible."""
    couts = F.cout_parc([COMPLET] + [_sys(id=9, nom="muet")])
    assert "couverture" in couts
    assert couts["couverture"]["total"] == 2
    assert couts["couverture"]["instruites"] == 1
    assert couts["couverture"]["part_instruite"] == 0.5
    assert couts["lisible"] is True
    # Et l'avertissement de tarif catalogue voyage avec le montant.
    assert "catalogue" in couts["avertissement"].lower()


def test_les_motifs_sont_comptes_et_non_seulement_listes():
    """« Trois lignes sans volume » se corrige ; « des lignes sans volume » se
    remet à plus tard. Le compte par motif dit par où commencer."""
    parc = [COMPLET,
            _sys(id=2, modele="claude-sonnet-5", unite_facturation="jetons"),
            _sys(id=3, modele="claude-sonnet-5", unite_facturation="jetons"),
            _sys(id=4, unite_facturation="sieges")]
    couv = F.couverture(parc)
    assert couv["motifs"]["aucun volume déclaré pour ce mois"] == 2
    assert sum(couv["motifs"].values()) == couv["non_instruites"] == 3


def test_les_devises_ne_s_additionnent_pas_entre_elles(monkeypatch):
    """Additionner des dollars et des euros pour rendre un nombre unique serait
    faux d'une manière que personne ne verrait à l'écran. Le total est rendu
    PAR DEVISE, et un jour où deux devises coexistent, les deux sortent."""
    monkeypatch.setitem(F.TARIFS, "modele-en-euros",
                        {"entree": 2.0, "sortie": 8.0, "devise": "EUR"})
    parc = [COMPLET, dict(COMPLET, id=2, modele="modele-en-euros")]
    couts = F.cout_parc(parc)
    assert set(couts["mensuel_par_devise"]) == {"USD", "EUR"}
    assert couts["annuel_par_devise"]["EUR"] == round(
        couts["mensuel_par_devise"]["EUR"] * 12, 2)


# ═══════════════════════════════════════════════════════════════════════════
#  3. L'ATTRIBUTION NE FAIT DISPARAÎTRE AUCUN GROUPE
# ═══════════════════════════════════════════════════════════════════════════

def test_un_groupe_sans_ligne_instruite_reste_affiche():
    """UN GROUPE ABSENT SE LIT « CE SERVICE NE CONSOMME RIEN ». Un groupe à
    zéro instruit se lit « personne n'a encore dit ce qu'il consomme ». La
    première lecture est fausse et rassurante — c'est celle qu'on obtient en
    filtrant les groupes vides."""
    parc = [COMPLET,
            _sys(id=2, service="Juridique", modele="claude-opus-5",
                 unite_facturation="jetons")]
    att = F.attribution(parc, "service")
    cles = {g["cle"] for g in att["groupes"]}
    assert "Juridique" in cles, "le service non instruit a disparu du tableau"
    juridique = next(g for g in att["groupes"] if g["cle"] == "Juridique")
    assert juridique["systemes"] == 1 and juridique["instruites"] == 0
    assert juridique["lisible"] is False
    assert juridique["mensuel_par_devise"] is None
    assert juridique["motifs"], "le groupe ne dit pas pourquoi il n'est pas chiffré"


def test_un_champ_d_attribution_vide_est_nomme_et_non_efface():
    """Les lignes sans centre de coût forment le groupe le plus intéressant du
    tableau : c'est la dépense que personne ne porte."""
    att = F.attribution([_sys(id=1)], "centre_cout")
    assert att["groupes"][0]["cle"] == "— non renseigné —"


# ═══════════════════════════════════════════════════════════════════════════
#  4. LE DIMENSIONNEMENT REND UNE QUESTION, JAMAIS UN VERDICT
# ═══════════════════════════════════════════════════════════════════════════

def test_le_surdimensionnement_se_voit_et_reste_une_heuristique():
    """« Un modèle de grande taille pour une tâche simple est un gaspillage
    courant » — le cas d'école : Opus sur du tri de tickets. Le module dit
    l'écart et ce qu'il faudrait essayer ; il ne dit jamais « trop gros », ce
    qui supposerait de connaître la qualité attendue et ce qu'une erreur
    coûte."""
    d = F.dimensionnement(dict(COMPLET, modele="claude-opus-5",
                               classe_tache="extraction"))
    assert d["instruit"] is True
    assert d["ecart"] == 2 and d["a_regarder"] is True
    assert d["heuristique"] is True, "le module rend un verdict"
    assert "essayé" in d["note"] and "mesuré" in d["note"]


def test_la_classe_de_tache_ne_se_devine_pas():
    """Elle ne se déduit pas de la finalité, qui est du texte libre et dirait
    n'importe quoi. Non déclarée, le dimensionnement se tait."""
    d = F.dimensionnement(dict(COMPLET, classe_tache="",
                               finalite="tri automatique très simple de tickets"))
    assert d["instruit"] is False
    assert "ne se devine pas" in d["motif"]


def test_un_modele_sous_dimensionne_parle_de_qualite_et_non_de_cout():
    """L'écart inverse existe et ne se traite pas de la même façon : un modèle
    en dessous de la tâche ne coûte pas trop cher, il rend mal."""
    d = F.dimensionnement(dict(COMPLET, modele="claude-haiku-4-5",
                               classe_tache="raisonnement"))
    assert d["ecart"] < 0 and d["a_regarder"] is False
    assert "qualité" in d["note"]


# ═══════════════════════════════════════════════════════════════════════════
#  5. UN PLAFOND QU'ON NE PEUT PAS VÉRIFIER NE VAUT PAS UN PLAFOND TENU
# ═══════════════════════════════════════════════════════════════════════════

def test_un_plafond_sur_un_groupe_non_instruit_sort_comme_non_verifiable():
    """LE VERT PAR IGNORANCE. Un plafond posé sur un centre de coût dont aucune
    ligne n'est chiffrée ne peut être ni respecté ni dépassé. Le compter parmi
    les groupes « sous le plafond » ferait exactement ce que ce module existe
    pour empêcher."""
    parc = [_sys(id=1, centre_cout="CC-999", modele="claude-opus-5",
                 unite_facturation="jetons")]
    dep = F.depassements(parc, {"CC-999": {"plafond": 100, "devise": "USD"}})
    assert dep["atteints"] == []
    assert len(dep["non_verifiables"]) == 1
    assert dep["non_verifiables"][0]["cle"] == "CC-999"


def test_un_depassement_reel_est_nomme_avec_sa_part():
    depasse = F.depassements([COMPLET], {"CC-410": {"plafond": 10, "devise": "USD"}})
    a = depasse["atteints"][0]
    assert a["depasse"] is True
    assert a["part"] == round(a["montant"] / 10, 3)


def test_un_groupe_partiellement_instruit_le_dit():
    """Un plafond comparé à un montant qui ne couvre qu'une partie du groupe
    est un plafond comparé à trop peu. Le signaler ne coûte qu'un booléen."""
    parc = [COMPLET, dict(COMPLET, id=2, volume_entree_mois="",
                          volume_sortie_mois="")]
    dep = F.depassements(parc, {"CC-410": {"plafond": 1000, "devise": "USD"}})
    assert dep["atteints"][0]["partiel"] is True


# ═══════════════════════════════════════════════════════════════════════════
#  6. LES TARIFS SONT DATÉS, ET CE QUI VIEILLIT SE SIGNALE
# ═══════════════════════════════════════════════════════════════════════════

def test_le_tarif_porte_sa_date_et_sa_source():
    """Un tarif sans date est une rumeur. La source nomme l'émetteur, la date
    dit de quand elle parle — les deux sont exigées, le montant ne l'est pas."""
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", F.TARIFS_RELEVE_LE)
    assert "relev" in F.TARIFS_SOURCE.lower()
    assert F.tarif_age_jours(datetime.date.fromisoformat(F.TARIFS_RELEVE_LE)) == 0


def test_un_tarif_trop_vieux_se_signale_sur_chaque_montant():
    """LA PÉREMPTION VOYAGE AVEC LE CHIFFRE, et non dans une note de bas de
    page qu'on ne lit pas. Un an après le relevé, chaque ligne le dit."""
    vieux = datetime.date.fromisoformat(F.TARIFS_RELEVE_LE) + datetime.timedelta(
        days=F.TARIF_PEREMPTION_JOURS + 1)
    assert F.tarif_perime(vieux) is True
    assert F.cout_ligne(COMPLET, aujourdhui=vieux)["tarif_perime"] is True
    assert F.cout_parc([COMPLET], aujourdhui=vieux)["tarif_perime"] is True
    frais = datetime.date.fromisoformat(F.TARIFS_RELEVE_LE)
    assert F.tarif_perime(frais) is False


def test_chaque_tarif_porte_une_devise_et_deux_prix():
    """Une entrée incomplète produirait une KeyError au calcul, c'est-à-dire au
    pire moment. La table est vérifiée pour ce qu'elle promet, pas pour ses
    valeurs — celles-ci changent avec le marché."""
    for nom, t in F.TARIFS.items():
        assert set(t) == {"entree", "sortie", "devise"}, nom
        assert t["entree"] > 0 and t["sortie"] > 0, nom
        assert t["devise"], nom
        assert nom in F.RANG_MODELE, (
            "%s a un tarif mais aucun rang : le dimensionnement se taira sur "
            "un modèle qu'on sait pourtant chiffrer" % nom)


def test_ce_qui_manque_est_declare_plutot_qu_estime():
    """La faute que `finance_dc` refuse pour le coût au mégawatt : une valeur
    inventée habillée en référentiel. Les tarifs des autres éditeurs, le taux
    de change, les remises et les coûts hors modèle sont ABSENTS ET NOMMÉS."""
    for cle in ("tarifs_autres_editeurs", "taux_de_change", "remises_et_contrats"):
        assert cle in F.A_RENSEIGNER
        assert len(F.A_RENSEIGNER[cle]) > 60, cle
    # Et aucun tarif ne sort dans une devise convertie.
    assert all(t["devise"] == "USD" for t in F.TARIFS.values())


# ═══════════════════════════════════════════════════════════════════════════
#  7. L'ÉTAT SERVI AU PANNEAU
# ═══════════════════════════════════════════════════════════════════════════

def test_l_etat_place_la_couverture_avant_les_couts():
    """L'ORDRE DES CLÉS N'EST PAS COSMÉTIQUE : c'est le contrat entre le moteur
    et le panneau. La couverture précède les montants dans la structure comme
    elle doit les précéder à l'écran."""
    e = F.etat([COMPLET])
    cles = list(e)
    assert cles.index("couverture") < cles.index("couts")
    assert e["couverture"]["total"] == 1
    for attendu in ("par_service", "par_centre_cout", "par_modele",
                    "dimensionnement", "depassements", "a_renseigner"):
        assert attendu in e


def test_les_leviers_sont_une_question_posee_a_chaque_ligne():
    """Déclarés, jamais mesurés — le module ne peut pas savoir si un cache est
    branché. Ce qu'il apporte est la question : une case jamais cochée sur
    vingt lignes se voit."""
    assert F.leviers_manquants(_sys()) == sorted(F.LEVIERS)
    partiel = F.leviers_manquants(_sys(leviers=["cache"]))
    assert "cache" not in partiel and "differe" in partiel
    # Une liste stockée en JSON qui remonterait en chaîne compterait des
    # CARACTÈRES : les deux formes sont acceptées.
    assert F.leviers_manquants(_sys(leviers="cache,differe")) == \
        sorted(set(F.LEVIERS) - {"cache", "differe"})


# ═══════════════════════════════════════════════════════════════════════════
#  8. LE REGISTRE PORTE LES HUIT CHAMPS, ET ILS SURVIVENT À L'ALLER-RETOUR
# ═══════════════════════════════════════════════════════════════════════════
#
# C'EST ICI QU'UNE COLONNE AJOUTÉE SE PERD, en silence, parce qu'un `?` manque
# quelque part. La règle exécute l'INSERT et l'UPDATE d'`app.py` TELS QU'ILS
# SONT ÉCRITS, contre la table qu'`app.py` crée : un décalage de paramètre tombe
# ici plutôt qu'en production, où il se lit « le champ ne s'enregistre pas ».
import io                                                          # noqa: E402
import sqlite3                                                     # noqa: E402

SOURCE = io.open(os.path.join(ICI, "app.py"), encoding="utf-8").read()
PAGE = io.open(os.path.join(ICI, "sentinel.html"), encoding="utf-8").read()
MOTEUR = io.open(os.path.join(ICI, "sentinel.page.js"), encoding="utf-8").read()

CHAMPS_FINOPS = ("modele", "unite_facturation", "volume_entree_mois",
                 "volume_sortie_mois", "volume_source", "centre_cout",
                 "classe_tache", "leviers")


def _table_sqlite():
    ddl = [m for m in re.findall(
        r"CREATE TABLE IF NOT EXISTS systemes_ia \([^)]*?\)", SOURCE, re.S)
        if "AUTOINCREMENT" in m]
    assert ddl, "la création de table SQLite est introuvable dans app.py"
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(ddl[0])
    for col, decl in re.findall(
            r"""registre_ajouter_colonne\(cur,\s*'systemes_ia',\s*'(\w+)',\s*"""
            r"""("[^"]*"|'[^']*')\s*\)""", SOURCE):
        conn.execute("ALTER TABLE systemes_ia ADD COLUMN %s %s" % (col, decl[1:-1]))
    return conn


def test_les_huit_colonnes_sont_migrees_et_enumerables():
    """ÉNUMÉRABLES, ET PAS SEULEMENT PRÉSENTES. La première version de cette
    migration les ajoutait dans une BOUCLE : six lignes de moins, et invisible à
    la recette, qui reconstruit la table en lisant les appels littéraux. La
    table de recette repartait sans les huit et l'INSERT tombait. Une migration
    qu'on ne peut pas énumérer est une migration qu'on ne peut pas vérifier."""
    colonnes = {r[1] for r in _table_sqlite().execute(
        "PRAGMA table_info(systemes_ia)")}
    manquantes = [c for c in CHAMPS_FINOPS if c not in colonnes]
    assert not manquantes, manquantes


def test_aucune_colonne_de_volume_ne_porte_une_valeur_par_defaut():
    """LA DÉCISION QUI TIENT TOUT LE MODULE, ÉCRITE DANS LE SCHÉMA. Un
    `DEFAULT 0` ferait qu'un parc jamais instruit afficherait un coût mensuel de
    zéro, crédible et faux. NULL se lit « personne n'a encore dit », zéro se lit
    « cela ne coûte rien »."""
    for col in ("volume_entree_mois", "volume_sortie_mois"):
        motif = re.search(
            r"registre_ajouter_colonne\(cur, 'systemes_ia', '%s', \"([^\"]*)\"\)"
            % col, SOURCE)
        assert motif, col
        assert "DEFAULT" not in motif.group(1).upper(), (
            "%s porte une valeur par défaut : un parc non instruit afficherait "
            "un coût de zéro" % col)


def test_les_huit_champs_survivent_a_l_aller_retour_en_base():
    """Écrits par l'INSERT, relus, puis modifiés par l'UPDATE — les deux
    instructions telles qu'`app.py` les écrit."""
    conn = _table_sqlite()
    insert = re.sub(r"\s+", " ", re.search(
        r"INSERT INTO systemes_ia\s*\n\s*\(nom,[^)]*\)\s*\n\s*VALUES \(\?[^)]*\)",
        SOURCE, re.S).group(0)).strip()
    colonnes = [x.strip() for x in
                re.search(r"\((nom,[^)]*)\)", insert).group(1).split(",")]
    for champ in CHAMPS_FINOPS:
        assert champ in colonnes, (
            "`%s` n'est pas insérée : le champ sera saisi puis perdu" % champ)
    temoins = {"modele": "claude-haiku-4-5", "unite_facturation": "jetons",
               "volume_entree_mois": "1200000", "volume_sortie_mois": "90000",
               "volume_source": "console, relevé du 31/08",
               "centre_cout": "CC-410", "classe_tache": "extraction",
               "leviers": '["cache"]'}
    valeurs = [temoins.get(c, 0 if c in ("score_risque", "client_id") else "x")
               for c in colonnes]
    conn.execute(insert, valeurs)
    ligne = conn.execute("SELECT * FROM systemes_ia").fetchone()
    for champ, attendu in temoins.items():
        assert ligne[champ] == attendu, (
            "%s ne traverse pas l'INSERT : vaut %r" % (champ, ligne[champ]))

    update = re.sub(r"\s+", " ", re.search(
        r"UPDATE systemes_ia SET nom=\?.*?WHERE id=\? AND client_id=\?",
        SOURCE, re.S).group(0)).strip()
    champs_maj = [m for m in re.findall(r"(\w+)=\?", update)]
    for champ in CHAMPS_FINOPS:
        assert champ in champs_maj, (
            "`%s` n'est pas mise à jour : elle se saisit puis se fige" % champ)


def test_le_moteur_lit_bien_ces_champs_la():
    """LES NOMS DOIVENT ÊTRE LES MÊMES DES DEUX CÔTÉS. `finops_ia` lit des clés
    sur les lignes que `/api/registre` rend ; un champ renommé d'un seul côté
    donnerait un parc éternellement « non instruit » sans qu'aucune erreur ne
    s'affiche — le pire des symptômes, parce qu'il ressemble à un registre mal
    rempli."""
    lu_par_le_moteur = set(re.findall(
        r'systeme\.get\("(\w+)"\)',
        io.open(os.path.join(ICI, "finops_ia.py"), encoding="utf-8").read()))
    for champ in CHAMPS_FINOPS:
        assert champ in lu_par_le_moteur or champ in ("centre_cout",), champ
    rendus = re.search(r"def registre_row_to_dict.*?\n    \}", SOURCE, re.S).group(0)
    for champ in CHAMPS_FINOPS:
        assert "'%s'" % champ in rendus, (
            "`%s` n'est pas rendue par /api/registre : le moteur ne la verra "
            "jamais" % champ)


# ═══════════════════════════════════════════════════════════════════════════
#  9. LA ROUTE ET LE PANNEAU
# ═══════════════════════════════════════════════════════════════════════════

def test_la_route_est_reservee_comme_le_registre_qu_elle_lit():
    """Elle rend le même contenu que le registre, vu sous un autre angle : la
    laisser plus ouverte que lui ouvrirait par la bande ce que l'autre ferme."""
    bloc = re.search(r"@app\.route\('/api/finops'.*?\ndef finops_etat", SOURCE, re.S)
    assert bloc, "la route /api/finops est introuvable"
    assert "@require_paid_plan" in bloc.group(0)
    assert "@rate_limit" in bloc.group(0)


def test_la_route_ne_se_tait_pas_sur_un_seuil_illisible():
    """Sans ce refus, un comité lirait « aucun dépassement » d'un paramètre que
    le serveur n'a pas compris — un vert par malentendu."""
    corps = re.search(r"def finops_etat\(\):.*?\n@app\.route", SOURCE, re.S).group(0)
    assert "seuils_illisibles" in corps
    assert "400" in corps


def test_le_panneau_montre_la_couverture_avant_le_moindre_montant():
    """L'ORDRE D'AFFICHAGE EST LA MOITIÉ DE L'HONNÊTETÉ. Un total placé avant sa
    couverture se cite seul — et c'est exactement l'usage qu'on veut rendre
    impossible. La règle lit la position dans le balisage, pas une intention."""
    i = PAGE.index('id="p-finops"')
    bloc = PAGE[i:PAGE.index('<div class="page"', i + 10)]
    assert bloc.index('id="fo-couverture"') < bloc.index('id="fo-montants"'), (
        "les montants sont peints avant la couverture qui en décide la lecture")


def _bloc_du_panneau():
    """Le CORPS de `finopsLoad`, et non sa première mention.

    `MOTEUR.index("window.finopsLoad")` tombait sur la ligne du répartiteur —
    « if (id === 'finops' … ) _apresPeinture(window.finopsLoad); » — c'est-à-dire
    huit mille caractères d'un tout autre code. Les deux règles qui suivent
    étaient vertes en lisant la mauvaise portion du fichier : elles ne
    vérifiaient rien, et rien ne le disait. On ancre donc sur la DÉFINITION.
    """
    i = MOTEUR.index("window.finopsLoad = function()")
    return MOTEUR[i:MOTEUR.index("\n})();", i)]


def test_le_panneau_ne_recalcule_rien_de_son_cote():
    """Recalculer côté navigateur donnerait un second exemplaire du moteur, et
    c'est celui qu'on oublie de corriger qui resterait. Le panneau met en page
    ce que le serveur rend — aucun tarif, aucune multiplication."""
    bloc = _bloc_du_panneau()
    assert len(bloc) > 2000, "l'extraction n'a pas trouvé le corps du panneau"
    for interdit in ("TARIFS", "1e6", "* 3.0", "/ 1000000"):
        assert interdit not in bloc, (
            "le panneau refait le calcul du serveur (%s)" % interdit)


def test_le_panneau_dit_que_le_non_instruit_n_est_pas_un_zero():
    """La phrase est le seul endroit où le lecteur apprend la différence entre
    « ne consomme rien » et « rien n'a été déclaré ». Une règle la garde parce
    que la première relecture qui trouve le ton lourd la supprimerait."""
    bloc = _bloc_du_panneau()
    assert "ne coûtent pas" in bloc and "zéro" in bloc
    assert "non instruit" in bloc
