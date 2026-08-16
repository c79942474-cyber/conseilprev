"""La maturité analytique décisionnelle — ce que le diagnostic ne doit jamais
flatter.

Trois règles protégées ici, chacune avec la faute qu'elle empêche :

  1. LE GLOBAL EST LE MINIMUM, PAS LA MOYENNE. Une moyenne aurait affiché
     « intermédiaire » à une organisation dont les données ne sont pas datées
     — et envoyé travailler l'axe qui tenait déjà.
  2. UN CRITÈRE NON INSTRUIT N'EST PAS UN ZÉRO. Confondre les deux abaisse la
     note d'une organisation qui a sauté une question, et rend le diagnostic
     contestable au moment précis où il faut qu'il tienne.
  3. LA RESTITUTION PORTE LE VERDICT EN TÊTE, y compris décevant, avec le
     recalibrage. C'est la raison d'être du diagnostic : présenter tard une
     conclusion déplaisante coûte le projet.
"""
import os
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import maturite_decision as m  # noqa: E402


def _plein(niveau):
    """Tous les critères de tous les axes à ce niveau."""
    return {a["cle"]: {c["cle"]: niveau for c in a["criteres"]} for a in m.AXES}


def test_le_referentiel_est_coherent_au_chargement():
    assert m._verifier() == []
    s = m.sante()
    assert s["axes"] == 4 and s["criteres"] == 13 and s["decisions"] == 3
    # Chaque famille de décision DIT ce qu'elle ne couvre pas : sans cela, le
    # tableau se lit comme un quitus — la garde d'import l'interdit déjà,
    # ce test le dit en clair.
    for d in m.DECISIONS:
        assert d["hors_perimetre"], d["cle"]


def test_le_global_est_le_maillon_faible_pas_la_moyenne():
    """Le cas qui décide de tout : trois axes au niveau 3, un seul critère à
    0 (la donnée non datée). Une moyenne rendrait ~2,8 ; la règle rend 0."""
    rep = _plein(3)
    rep["collecte"]["donnee_datee"] = 0
    d = m.diagnostic(rep)
    assert d["niveau_global"] == 0, d["niveau_global"]
    assert "pas une moyenne" in d["lecture"]
    assert "Collecte de données" in d["lecture"]
    # …et l'axe lui-même tombe au niveau de son critère le plus faible.
    col = [a for a in d["axes"] if a["cle"] == "collecte"][0]
    assert col["niveau"] == 0 and col["faible"] == ["donnee_datee"]
    autres = [a for a in d["axes"] if a["cle"] != "collecte"]
    assert all(a["niveau"] == 3 for a in autres)


def test_un_critere_non_instruit_n_est_pas_un_zero():
    rep = _plein(2)
    del rep["analyse"]["quali"]              # non répondu
    rep["cible"]["maintien"] = "n/a"         # illisible : non répondu aussi
    d = m.diagnostic(rep)
    assert d["niveau_global"] == 2, "un manque a été compté comme un zéro"
    assert d["complet"] is False
    assert "peut encore baisser, jamais monter" in d["lecture"]
    an = [a for a in d["axes"] if a["cle"] == "analyse"][0]
    assert an["manquants"] == ["quali"] and an["instruit"] == 2
    ci = [a for a in d["axes"] if a["cle"] == "cible"][0]
    assert ci["manquants"] == ["maintien"]


def test_aucune_reponse_ne_produit_pas_un_diagnostic():
    d = m.diagnostic({})
    assert d["niveau_global"] is None
    assert "pas de diagnostic" in d["lecture"]
    assert all(x["verdict"] == "non_instruit" for x in d["decisions"])


def test_les_actions_sont_hierarchisees_par_effet_pas_par_facilite():
    rep = _plein(3)
    rep["amelioration"]["jalons"] = 1        # le maillon faible
    d = m.diagnostic(rep)
    r1 = [a for a in d["actions"] if a["rang"] == 1]
    r2 = [a for a in d["actions"] if a["rang"] == 2]
    assert [a["axe"] for a in r1] == ["amelioration"]
    assert all("DÉPLACE" in a["effet"] for a in r1)
    # Les axes déjà au-dessus sont explicitement mis en attente : y investir
    # ne bougerait pas le chiffre, et le plan doit le dire.
    assert {a["axe"] for a in r2} == {"cible", "collecte", "analyse"}
    assert all("aucun sur le chiffre" in a["effet"] for a in r2)


def test_l_apport_de_l_etude_est_CONSTATE_jamais_suppose():
    """Le point de jonction avec l'enveloppe : un bloc non calculé ne doit
    jamais être présenté comme un apport disponible."""
    rep = _plein(2)
    sans = m.diagnostic(rep)                       # aucune étude fournie
    for x in sans["decisions"]:
        assert x["apports_disponibles"] == 0
        assert all(not c["disponible"] for c in x["couvert_par"])
    avec = m.diagnostic(rep, etude={"enveloppe": True, "kpi": True})
    inv = [x for x in avec["decisions"] if x["cle"] == "investissement"][0]
    dispo = {c["bloc"] for c in inv["couvert_par"] if c["disponible"]}
    assert dispo == {"enveloppe", "kpi"}
    assert inv["apports_disponibles"] == 2 and inv["apports_total"] == 3


def test_les_familles_de_decision_suivent_leurs_axes_conditionnants():
    """Le positionnement concurrentiel dépend de la collecte et de l'analyse,
    pas de l'axe d'amélioration : un trou dans l'amélioration ne doit pas le
    déclarer non instruisable, et un trou dans la collecte doit le faire."""
    rep = _plein(3)
    rep["amelioration"]["jalons"] = 0
    d = m.diagnostic(rep)
    pos = [x for x in d["decisions"] if x["cle"] == "positionnement"][0]
    allo = [x for x in d["decisions"] if x["cle"] == "allocation"][0]
    assert pos["niveau"] == 3 and pos["verdict"] == "pilotable"
    assert allo["niveau"] == 0 and allo["verdict"] == "non_instruisable"

    rep2 = _plein(3)
    rep2["collecte"]["donnee_datee"] = 1
    d2 = m.diagnostic(rep2)
    pos2 = [x for x in d2["decisions"] if x["cle"] == "positionnement"][0]
    assert pos2["niveau"] == 1 and pos2["verdict"] == "fragile"


def test_la_restitution_porte_le_verdict_decevant_EN_TETE():
    """La règle de conduite demandée : présenter tôt, même si cela déçoit.
    Le module ne sait pas produire de version ménagée — et le verdict passe
    avant tout le reste, jamais en annexe."""
    rep = _plein(3)
    rep["collecte"]["donnee_datee"] = 0
    d = m.diagnostic(rep, etude={"enveloppe": True})
    note = m.restitution_sponsors(d, "Site de Marseille")
    assert note.startswith("# Diagnostic de maturité analytique")
    assert "Site de Marseille" in note
    # Le verdict est dans le PREMIER tiers du document.
    i_verdict = note.index("Ce que ce diagnostic conclut")
    assert i_verdict < len(note) // 3, "le verdict n'est pas en tête"
    assert "décevante, et c'est la raison de la présenter maintenant" in note
    # Le recalibrage : ce qui est tenable, ce qu'il ne faut PAS promettre.
    assert "Livrable tenable aujourd'hui" in note
    assert "À NE PAS promettre en l'état" in note
    assert m.PROMETTABLE[0]["livrable"] in note
    # …et le palier suivant est nommé avec sa condition.
    assert "Ce qui débloque le palier suivant" in note
    assert "Collecte de données" in note


def test_la_restitution_recalibre_a_chaque_niveau():
    """Un tableau de bord temps réel promis à une organisation de niveau 0
    sera abandonné : chaque niveau a son livrable tenable, et son interdit."""
    for n in range(0, m.NIVEAU_MAX + 1):
        d = m.diagnostic(_plein(n))
        note = m.restitution_sponsors(d)
        assert m.PROMETTABLE[n]["livrable"] in note, n
        assert m.PROMETTABLE[n]["eviter"] in note, n
        if n <= 1:
            assert "décevante" in note, n
        else:
            assert "décevante" not in note, n
    # Au niveau maximal, il n'y a plus de palier suivant à promettre.
    haut = m.restitution_sponsors(m.diagnostic(_plein(m.NIVEAU_MAX)))
    assert "Ce qui débloque le palier suivant" not in haut


def test_la_reserve_distingue_les_deux_questions():
    """« Peut-on l'instruire » n'est pas « est-ce un bon investissement ».
    Confondre les deux valide un mauvais dossier bien présenté."""
    d = m.diagnostic(_plein(3))
    assert "ne dit pas si l'investissement est bon" in d["reserve"]
    assert d["reserve"] in m.restitution_sponsors(d)


def test_le_garde_TOMBE_sur_un_bloc_d_etude_inconnu():
    sauve = m.DECISIONS[0]["couvert_par"][0]["bloc"]
    try:
        m.DECISIONS[0]["couvert_par"][0]["bloc"] = "bloc_inexistant"
        f = m._verifier()
        assert any("bloc d'étude inconnu" in x for x in f), f
    finally:
        m.DECISIONS[0]["couvert_par"][0]["bloc"] = sauve
    assert m._verifier() == []
