"""CE QUE LA CARTE MONTRE, ET SUR COMBIEN.

CE QUI A DECLENCHE CE FICHIER. « Les Echos » a publie deux cartes des centres
de donnees francais, fondees sur le projet DCWatch (Hubblo) : environ trois
cent cinquante sites, colories par origine geographique de l'operateur
d'infrastructure, dimensionnes par une puissance estimee en megawatts. Notre
referentiel en porte trente-trois pour la France, sans aucune puissance.

L'ECART N'EST PAS UN DEFAUT — c'est une methode differente, et le referentiel
la documente deja : `capacite_mw` est nul partout, volontairement, parce que
les MW qui circulent sont des cibles, des ambitions ou des raccordements. Ce
que le referentiel ne faisait PAS, c'etait le dire pour la France. Il le
disait pour l'Allemagne, en prose, pour un seul pays.

CE QUE CES CONTROLES GARDENT :

  1. Le compte exterieur est une DONNEE datee et sourcee, pas une phrase.
  2. La part reelle est CALCULEE, jamais recopiee — une phrase qui annonce un
     taux devient fausse des qu'une ligne entre.
  3. Les deux provenances sont comptees a part. Les confondre a failli faire
     « corriger » une phrase juste : l'Allemagne est bien « couverte qu'a
     hauteur de quinze » — quinze lignes ETABLIES UNE PAR UNE ; les vingt et
     une autres viennent du registre.
  4. Les reperes nationaux ne se melangent pas aux sites, et chacun porte sa
     reserve.
  5. L'origine de l'operateur, si elle est un jour ajoutee, ne peut pas etre
     presentee comme l'origine des DONNEES : la colocation loue des metres
     carres a des tiers dont l'identite est couverte par le secret des
     affaires. C'est le point de fond de l'article, et il doit survivre.
"""
import os
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import datacentres as D  # noqa: E402


# ── LE COMPTE EXTERIEUR EST UNE DONNEE SOURCEE ───────────────────────────

def test_chaque_compte_exterieur_porte_sa_source_et_sa_methode():
    """Un nombre sans source est une rumeur. Celui de la France vient d'un
    article de presse citant un projet de recherche : les deux doivent etre
    nommes, et la methode dite, parce qu'elle explique l'ecart."""
    assert D.COUVERTURE_NATIONALE, "aucun compte exterieur declare"
    for pays, ref in D.COUVERTURE_NATIONALE.items():
        for champ in ("nom", "recense", "source", "methode"):
            assert ref.get(champ), "%s : champ « %s » manquant" % (pays, champ)
        assert len(ref["methode"]) > 60, (
            "%s : la methode tient en une ligne — elle n'explique pas l'ecart" % pays)


def test_la_france_est_declaree_et_sa_source_nommee():
    fr = D.COUVERTURE_NATIONALE.get("FR")
    assert fr, "la France n'a pas de compte exterieur"
    assert "DCWatch" in fr["source"] or "DCWatch" in fr["methode"]
    assert "Echos" in fr["source"]
    assert fr["approx"] is True, (
        "« environ 350 » n'est pas un compte exact : le champ doit le dire")


# ── LA PART EST CALCULEE, JAMAIS RECOPIEE ────────────────────────────────

def test_la_couverture_est_derivee_du_compte_reel():
    c = D.couverture()
    assert c, "aucune couverture calculee"
    for pays, v in c.items():
        reel = sum(1 for s in D.SITES if s.get("pays") == pays)
        assert v["porte"] == reel, "%s : %s annonce, %d reels" % (pays, v["porte"], reel)
        attendu = round(100.0 * reel / v["recense_ailleurs"], 1)
        assert v["part_pct"] == attendu


def test_les_deux_provenances_sont_comptees_a_part():
    """LE PIEGE. Une version de ce module comptait tout ensemble et concluait
    que la prose allemande avait derive de vingt et une lignes. Elle n'avait
    pas derive : elle parlait des lignes ETABLIES, le compte total en
    additionnait d'autres. Deux denominateurs, deux phrases."""
    c = D.couverture()
    for pays, v in c.items():
        assert v["porte_referentiel"] + v["porte_registre"] == v["porte"]
        reel = sum(1 for s in D.SITES if s.get("pays") == pays
                   and s.get("provenance", "referentiel") == "referentiel")
        assert v["porte_referentiel"] == reel, (
            "%s : le defaut de provenance n'est pas celui de `_enrichir()` — "
            "une ligne sans provenance a ete etablie a la main" % pays)
    assert any(v["porte_referentiel"] > 0 for v in c.values()), (
        "aucune ligne etablie n'est comptee : le defaut de provenance est faux")


# ── LA SOUS-COUVERTURE DOIT ETRE DITE ────────────────────────────────────

def test_aucune_sous_couverture_nest_passee_sous_silence():
    assert not D._limite_couverture(D.couverture())


def test_le_controle_est_branche_sur_sante():
    """UNE REGLE QUI FONCTIONNE NE PROUVE PAS QU'ELLE S'EXECUTE. Une mutation
    a survecu en debranchant simplement l'appel dans `sante()` : les controles
    appelaient `_limite_couverture` directement et ne voyaient rien."""
    vraies = D.LIMITES[:]
    try:
        D.LIMITES[:] = [x.replace("Treize lignes", "Quarante lignes")
                        for x in vraies]
        pb = D.sante()["problemes"]
        assert any("France" in m for m in pb), (
            "sante() n'execute pas le controle de couverture : %s" % pb)
    finally:
        D.LIMITES[:] = vraies
    assert not D.sante()["problemes"]


def test_le_controle_exige_le_compte_DANS_la_limite_qui_nomme_le_pays():
    """DISCRIMINATION, ET C'EST LA QUE DEUX VERSIONS ONT ECHOUE. La premiere
    cherchait le code « DE », qu'on lit dans n'importe quelle prose
    francaise. La seconde cherchait « treize » dans tout le texte, ou ce mot
    figure deja au sujet de la precision geographique. Chercher un mot
    n'importe ou dans un long texte ne verifie rien."""
    vraies = D.LIMITES[:]
    try:
        # Une limite qui nomme la France mais avec le MAUVAIS compte doit
        # etre signalee — c'est exactement la derive qu'on veut empecher.
        D.LIMITES[:] = [x.replace("Treize lignes", "Quarante lignes")
                        for x in vraies]
        maux = D._limite_couverture(D.couverture())
        assert any("France" in m for m in maux), (
            "un compte francais faux passe inapercu : %s" % maux)
    finally:
        D.LIMITES[:] = vraies
    assert not D._limite_couverture(D.couverture())


def test_les_nombres_sacrivent_en_lettres_comme_la_prose():
    """Le controle parle la langue du texte, et non l'inverse : exiger des
    chiffres obligerait a casser le style pour se rendre verifiable."""
    assert D.en_lettres(15) == "quinze"
    assert D.en_lettres(33) == "trente-trois"
    assert D.en_lettres(21) == "vingt et un"
    assert D.en_lettres(40) == "quarante"


# ── LES REPERES NATIONAUX NE SONT PAS DES SITES ──────────────────────────

def test_chaque_repere_porte_sa_source_et_sa_reserve():
    """Un agregat national sans reserve se lit comme une mesure. « 15 GW
    reserves » n'est ni une puissance installee ni une consommation."""
    assert D.REPERES_FR
    for r in D.REPERES_FR:
        for champ in ("cle", "valeur", "unite", "libelle", "source", "reserve"):
            assert r.get(champ) not in (None, ""), (
                "%s : champ « %s » manquant" % (r.get("cle"), champ))
        assert len(r["reserve"]) > 50, (
            "%s : la reserve tient en trois mots" % r["cle"])


def test_les_reperes_ne_sont_deduits_daucun_site():
    """S'ils l'etaient, ils entreraient en contradiction avec l'interdit du
    referentiel : aucun agregat de puissance ne peut etre construit a partir
    des sites."""
    cles = {r["cle"] for r in D.REPERES_FR}
    assert "raccordement_reserve" in cles
    a = D.assemble()
    for r in D.REPERES_FR:
        assert r["cle"] not in (a.get("agregats") or {})


def test_le_referentiel_nattribue_toujours_aucune_puissance():
    """LA REGLE DE FOND, QUE CES AJOUTS NE DOIVENT PAS AVOIR ENTAMEE. Ajouter
    des reperes en megawatts a cote des sites ne doit pas ouvrir la porte a
    une puissance par site."""
    # ON REGARDE LES SITES SERVIS, PAS LA LISTE BRUTE. Une mutation a
    # survecu en posant la capacite dans `_enrichir()` : la liste source
    # restait vierge, et c'est pourtant la version enrichie qui part a la
    # carte.
    for nom, lot in (("SITES", D.SITES), ("assemble()", D.assemble()["sites"])):
        avec = [s for s in lot if s.get("capacite_mw")]
        assert not avec, (
            "%d site(s) de %s portent une capacite_mw : l'interdit du "
            "referentiel est tombe" % (len(avec), nom))


# ── CE QUI MANQUE, ET CE QU'IL NE FAUDRA PAS LUI FAIRE DIRE ──────────────

def test_chaque_source_a_brancher_dit_ce_qui_lempeche():
    """« Une source qu'on ne peut pas atteindre est une intention, pas une
    source. » Une entree qui n'expliquerait pas son blocage se lirait comme
    un oubli plutot que comme une decision."""
    assert D.SOURCES_A_BRANCHER
    for s in D.SOURCES_A_BRANCHER:
        for champ in ("cle", "nom", "apporte", "manque", "reserve"):
            assert s.get(champ), "%s : champ « %s » manquant" % (s.get("cle"), champ)
        assert len(s["manque"]) > 60


def test_dcwatch_est_declaree_avec_sa_licence_non_instruite():
    """Republier n'est pas consulter. Le module Ile-de-France a deja tranche
    ainsi pour l'Observatoire de l'Institut Paris Region ; la meme regle vaut
    ici, et pour la meme raison."""
    d = next((s for s in D.SOURCES_A_BRANCHER if s["cle"] == "dcwatch"), None)
    assert d, "DCWatch n'est pas declaree"
    assert "licence" in d["manque"].lower()
    assert "exhaust" in d["reserve"].lower(), (
        "la reserve ne rappelle pas que DCWatch se declare non exhaustive")


def test_lorigine_de_loperateur_ne_pourra_pas_passer_pour_celle_des_donnees():
    """LE POINT DE FOND DE L'ARTICLE, ET IL DOIT SURVIVRE AU CODE. Les cartes
    publiees colorient par origine de l'operateur d'INFRASTRUCTURE. La
    colocation loue metres carres et megawatts a des tiers dont l'identite
    est couverte par le secret des affaires : une telle carte se lit tres
    facilement comme une carte de la souverainete des donnees, et elle ne
    l'est pas."""
    o = next((s for s in D.SOURCES_A_BRANCHER if s["cle"] == "origine_operateur"), None)
    assert o, "l'axe « origine de l'operateur » n'est pas declare"
    r = o["reserve"].lower()
    assert "colocation" in r
    assert "infrastructure" in r
    assert "utilisateur" in r, (
        "la reserve ne dit pas que l'operateur n'est pas l'utilisateur final")


def test_la_sante_expose_la_couverture_et_les_manques():
    """Un chiffre qui n'apparait nulle part n'aide personne : la carte doit
    pouvoir dire ce qu'elle montre, et sur combien."""
    s = D.sante()
    assert "couverture" in s and s["couverture"]
    assert s.get("reperes_fr") == len(D.REPERES_FR)
    assert set(s.get("a_brancher") or []) == {x["cle"] for x in D.SOURCES_A_BRANCHER}
