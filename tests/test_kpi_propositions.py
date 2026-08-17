"""Les propositions des trois entrées obligatoires : calculées, statutaires, jalons.

CE QUE CES TESTS PROTÈGENT, ET LA FAUTE QU'ILS EMPÊCHENT.

Ce module refusait de proposer le coût du capital et le taux d'impôt, avec un
motif juste : ce sont des décisions, pas des résultats. Mais un champ vide et
obligatoire n'est pas neutre non plus — il se remplit au jugé, ou il arrête le
lecteur. On propose donc, EN DISANT DE QUELLE NATURE EST CHAQUE CHIFFRE.

C'est cette distinction qui sépare proposer d'inventer, et c'est elle que ces
tests gardent :

  1. LES NIVEAUX DE REVENU SONT DE L'ARITHMÉTIQUE, pas un rendement de marché.
     Chaque palier ajoute exactement un point d'EVA rapporté aux capitaux
     employés, et l'identité Δr = s × CE ÷ (1 − IS) est vérifiée sur les
     écarts eux-mêmes. Un jour où quelqu'un remplacerait ces paliers par des
     pourcentages ronds « qui se pratiquent », ce test tomberait.

  2. LES COÛTS DU CAPITAL NE DOIVENT JAMAIS SE DIRE CALCULÉS. Ce sont quatre
     structures de financement, et le module n'a aucune enquête de marché
     publiable. Les servir sans leur nature « jalon » ni leur réserve les
     ferait passer pour une référence sectorielle — exactement le mensonge que
     ce module s'interdit depuis l'origine.

  3. LE PLANCHER MONDIAL DE 15 % DOIT ÊTRE OFFERT. Un groupe au-delà de
     750 M€ de chiffre d'affaires qui retiendrait 12,5 % en Irlande
     sous-estimerait son impôt : c'est la population même de ce module.
"""
import os
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import kpi_finance as k  # noqa: E402

CAPEX = [736.0, 920.0]
OPEX = [53.29, 121.55]


def test_les_paliers_de_revenu_sont_de_l_arithmetique_exacte():
    """LE TEST QUI COMPTE. On ne vérifie pas que les montants « semblent
    plausibles » — on vérifie l'identité qui les produit."""
    wacc, impot, amort = 8.0, 25.0, 10.0
    r = k.revenus_proposes(CAPEX, OPEX, 10, wacc, impot, amort_ans=amort)
    assert len(r) == 4, len(r)
    assert [x["spread_pct"] for x in r] == [0, 1, 2, 3]

    # Les capitaux employés de l'année servant de référence, refaits à part.
    n1 = int(k.seuil_revenu(CAPEX, OPEX, 10, wacc, impot,
                            amort_ans=amort)["premiere_annee_pleine"])
    ce = max(CAPEX) * (1.0 - min(1.0, (n1 - 1) / amort)) + k.DEFAUTS["bfr_meur"]

    base = r[0]["valeur"]
    for i, x in enumerate(r):
        attendu = base + (i / 100.0) * ce / (1.0 - impot / 100.0)
        assert abs(x["valeur"] - attendu) < 0.02, (i, x["valeur"], attendu)
    # Chaque palier est STRICTEMENT au-dessus du précédent : sans quoi les
    # quatre lignes du menu proposeraient quatre fois la même chose.
    assert all(r[i]["valeur"] < r[i + 1]["valeur"] for i in range(3))


def test_chaque_niveau_de_revenu_est_aussi_donne_en_part_de_l_investissement():
    """C'est sous cette forme qu'un revenu se juge : un montant seul ne dit pas
    s'il est ambitieux au regard de ce que l'actif aura coûté."""
    r = k.revenus_proposes(CAPEX, OPEX, 10, 8.0, 25.0, amort_ans=10)
    for x in r:
        assert x["pct_investissement"] is not None, x["libelle"]
        attendu = x["valeur"] / max(CAPEX) * 100
        assert abs(x["pct_investissement"] - attendu) < 0.15, x


def test_sans_les_deux_taux_aucun_revenu_n_est_propose():
    """Les paliers s'inversent depuis le coût du capital et l'impôt. Sans eux,
    il n'y a rien à inverser — et deviner serait pire que se taire."""
    assert k.revenus_proposes(CAPEX, OPEX, 10, None, 25.0) == []
    assert k.revenus_proposes(CAPEX, OPEX, 10, 8.0, None) == []
    p = k.propositions(CAPEX, OPEX, 10, {})
    e = p["entrees"]["revenu_meur_an"]
    assert e["propositions"] == []
    assert "coût du capital" in e["refus"] and "impôt" in e["refus"]


def test_les_couts_du_capital_ne_se_disent_jamais_calcules():
    """LA LIGNE À NE PAS FRANCHIR. Quatre chiffres ronds dans un menu passent
    pour une référence de marché : c'est la nature « jalon » et la réserve qui
    les en empêchent. Les perdre serait perdre l'honnêteté du menu."""
    p = k.propositions(CAPEX, OPEX, 10, {})
    e = p["entrees"]["wacc"]
    assert len(e["propositions"]) == 4, len(e["propositions"])
    for x in e["propositions"]:
        assert x["nature"] == "jalon", x
        assert "marché" in x["formule"], x["formule"]
    assert e.get("reserve"), "la réserve du coût du capital a disparu"
    assert "PAS une référence de marché" in e["reserve"]
    # Ils ne sont pas non plus des refus déguisés : ils sont bien offerts.
    assert e["refus"] is None
    # L'écart du simple au double est ce que le lecteur doit voir.
    vals = [x["valeur"] for x in e["propositions"]]
    assert vals == sorted(vals) and vals[-1] >= 2 * vals[0], vals


def test_les_taux_d_impot_viennent_du_pays_de_l_etude():
    p = k.propositions(CAPEX, OPEX, 10, {}, pays="SE",
                       pays_compares=["IE", "SE", "FR"])
    e = p["entrees"]["is_taux"]
    props = e["propositions"]
    assert len(props) == 4, [x["libelle"] for x in props]
    assert all(x["nature"] == "statutaire" for x in props)
    # LE PAYS RETENU VIENT EN PREMIER : c'est celui de l'étude.
    assert props[0]["pays"] == "SE"
    assert abs(props[0]["valeur"] - k.IS_STATUTAIRE["SE"][0]) < 0.01
    # LE PLANCHER MONDIAL EST OFFERT — sans lui, un groupe dans son champ
    # retiendrait 12,5 % en Irlande et sous-estimerait son impôt.
    assert any(abs(x["valeur"] - 15.0) < 0.01 for x in props), props
    # LES BORNES SONT CELLES DES PAYS RÉELLEMENT COMPARÉS, pas de la table.
    codes = {x["pays"] for x in props}
    assert "FR" in codes and "IE" in codes
    assert "MT" not in codes, "une borne vient d'un pays non comparé"
    assert e.get("reserve") and "NOMINAUX" in e["reserve"]


def test_un_pays_inconnu_est_refuse_plutot_qu_invente():
    p = k.propositions(CAPEX, OPEX, 10, {}, pays="ZZ", pays_compares=["ZZ"])
    e = p["entrees"]["is_taux"]
    # Le plancher mondial reste offert : il ne dépend d'aucun pays.
    assert len(e["propositions"]) == 1
    assert abs(e["propositions"][0]["valeur"] - 15.0) < 0.01


def test_aucun_doublon_dans_les_taux_proposes():
    """Deux lignes identiques dans un menu de quatre en gaspillent une."""
    p = k.propositions(CAPEX, OPEX, 10, {}, pays="FR",
                       pays_compares=["FR", "ES", "BE"])
    vals = [x["valeur"] for x in p["entrees"]["is_taux"]["propositions"]]
    assert len(vals) == len(set(vals)), vals


def test_la_table_statutaire_est_plausible_et_datee():
    """Un garde-fou grossier, mais il attrape la faute de frappe qui ferait
    lire 250 % ou 2,5 % à la place de 25 %."""
    assert len(k.IS_STATUTAIRE) >= 20
    for code, (taux, note) in k.IS_STATUTAIRE.items():
        assert len(code) == 2, code
        assert 5.0 <= taux <= 40.0, (code, taux)
        assert note, code
    assert "NOMINAUX" in k.IS_RESERVE and "conseil fiscal" in k.IS_RESERVE


def test_la_sante_ne_pretend_plus_ne_rien_proposer():
    """Le module annonçait « ne propose aucune référence sectorielle ». C'était
    vrai ; ça ne l'est plus tout à fait, et un module qui se décrit faussement
    est le premier pas vers un lecteur qui ne le croit plus."""
    s = k.sante()
    assert "jalon" in s["portee"]
    assert "statutaire" in s["portee"]
    assert s["propositions"]["wacc"] == len(k.CMPC_JALONS)
