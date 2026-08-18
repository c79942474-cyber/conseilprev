"""SOUS QUEL MONDE LES CLASSES D'ALÉAS SONT-ELLES ÉCRITES.

DÉFAUT CORRIGÉ. Les six aléas portent une classe à 2030 et une à 2050. Une
seule — la submersion — déclarait la trajectoire d'émissions dont elle dépend,
par ses trois scénarios SSP. Les CINQ AUTRES n'en déclaraient aucune : « feu :
élevé en 2030, très élevé en 2050 » ne disait pas dans quel monde.

LE PIÈGE ÉTAIT DOUBLE. Le seul énoncé de scénario visible disait que « la
trajectoire d'émissions ne change que 4 cm ». C'est vrai, et SEULEMENT pour la
mer. Un lecteur qui étend ce raisonnement au feu ou à la sécheresse conclut
que la trajectoire est indifférente : elle ne l'est pas.

LES CHIFFRES DE TRAJECTOIRE viennent du GIEC AR6 GROUPE III (atténuation,
2022) — le volume qui dit où mènent les politiques, donc quelle colonne
d'aléa un actif de vingt-cinq ans doit lire. Les aléas eux-mêmes n'en
viennent PAS : ils relèvent des groupes I et II, et la source des classes le
dit déjà. Confondre les volumes serait la faute que ces tests interdisent.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import climat_2050 as C


def test_les_classes_declarent_leur_trajectoire():
    t = C.assemble()["trajectoire"]
    assert t["cle"] in C.TRAJECTOIRES
    assert t["dit"] and t["nom"]
    # La trajectoire retenue est celle qu'un actif RENCONTRE, pas un objectif.
    assert t["cle"] == "politiques"
    assert "observée" in t["statut"]


def test_les_reperes_de_trajectoire_portent_LES_CHIFFRES_DU_RAPPORT():
    """AR6 WGIII SPM C.1.3 : politiques fin 2020 → 3,2 [2,2–3,5] °C en 2100.
    SPM C.1.1 : engagements pré-COP26 → 2,8 [2,1–3,4] °C. Recopier un chiffre
    de mémoire est exactement ce qui fait tomber un dossier."""
    T = C.TRAJECTOIRES
    assert "3,2" in T["politiques"]["atteint_2100"]
    assert "2,2" in T["politiques"]["atteint_2100"] and "3,5" in T["politiques"]["atteint_2100"]
    assert "2,8" in T["ndc"]["atteint_2100"]
    assert "2,1" in T["ndc"]["atteint_2100"] and "3,4" in T["ndc"]["atteint_2100"]
    # Les deux catégories du GIEC, avec leur seuil de probabilité.
    assert "50 %" in T["C1"]["definition"] and "67 %" in T["C1"]["definition"]
    assert "67 %" in T["C3"]["definition"]


def test_LE_POINT_QUI_DECIDE_le_constat_des_4_cm_ne_se_generalise_pas():
    """C'est le seul énoncé de scénario que la page portait, et il pouvait
    être lu comme valant pour les six aléas."""
    e = C.ecart_scenarios(2050)
    assert e["porte"] == "submersion"
    assert e["ecart_m"] == 0.04
    g = e["ne_pas_generaliser"]
    assert "NIVEAU DE LA MER" in g
    for autre in ("feu", "sécheresse", "pluies extrêmes", "étiage"):
        assert autre in g, "l'aléa %s n'est pas nommé dans la mise en garde" % autre


def test_le_module_REFUSE_une_classe_par_trajectoire():
    """Il faudrait un jeu d'aléas modélisé par scénario, qui n'existe pas ici.
    En fabriquer un serait exactement ce que ce module reproche ailleurs."""
    t = C.assemble()["trajectoire"]
    assert "AUCUNE CLASSE PAR TRAJECTOIRE" in t["refus"]
    assert "étude d'aléa" in t["refus"]


def test_le_bon_volume_du_GIEC_est_cite_pour_chaque_chose():
    """Le groupe III porte l'atténuation ; les aléas relèvent des groupes I et
    II. Citer le III pour un aléa serait un contresens de source."""
    src = C.assemble()["sources"]
    assert "III" in src["trajectoire"]["titre"]
    assert "wg3" in src["trajectoire"]["url"]
    assert "ATTÉNUATION" in src["trajectoire"]["note"]
    # Les classes d'aléas, elles, ne se réclament PAS du groupe III.
    assert "III" not in src["aleas"]["editeur"]
    assert "groupes I et II" in src["aleas"]["editeur"]


def test_les_niveaux_sont_rapportes_a_la_periode_de_reference_du_GIEC():
    """Un réchauffement sans période de référence ne se compare à rien."""
    assert "1850-1900" in C.SOURCE_TRAJECTOIRES["note"]


# ── LA TRAJECTOIRE VOYAGE AVEC LE CLASSEMENT ──────────────────────────────
#
# Six des seize critères du comparateur d'implantation sont des classes
# d'aléas à 2030 ou 2050. Les servir sans leur trajectoire laissait le lecteur
# croire à un classement de pays valable en toute hypothèse. Il ne l'est pas.

def _classement(horizon=2050):
    import implantation, datacentres, empreinte_sites
    d = datacentres.assemble()
    sites = d.get("sites") or d.get("centres") or []
    return implantation.assemble(sites, empreinte_sites.INTENSITE, horizon)


def test_le_comparateur_sert_la_trajectoire_avec_son_classement():
    r = _classement()
    t = r["trajectoire"]
    assert t["nom"] and t["dit"] and t["refus"]
    assert "3,2" in t["atteint_2100"]


def test_le_comparateur_cite_le_groupe_III_pour_la_trajectoire():
    r = _classement()
    assert "trajectoire" in r["sources"]
    assert "III" in r["sources"]["trajectoire"]["titre"]


def test_les_aleas_pesent_reellement_dans_le_classement():
    """Sans cela, la trajectoire serait une précaution sur un critère
    décoratif — et le contrôle ci-dessus ne prouverait rien."""
    r = _classement()
    aleas = [c for c in r["criteres"] if c["cle"].startswith("alea_")]
    assert len(aleas) == 6, "%d critères d'aléas" % len(aleas)
    assert len(aleas) / len(r["criteres"]) > 0.25
