"""LES PISTES — ce qu'un module « d'aide à la décision » doit s'interdire.

C'est le module le plus exposé du site. On attend de lui qu'il fasse émerger
des projets, et la façon paresseuse de le faire est connue : lire trois brèves
sur une technologie, en tirer « le marché va croître, positionnez-vous », et
habiller le tout d'un chiffre trouvé ailleurs. Ces contrôles gardent les
quatre interdits qui séparent une piste d'un argumentaire :

  1. AUCUNE PISTE SANS FICHE. Une piste qui ne pointe rien est une idée du
     rédacteur, pas une dérivation du corpus.
  2. AUCUN CHIFFRE DE MARCHÉ. Le corpus n'en porte aucun ; en produire un
     serait l'inventer, et un chiffre inventé voyage plus loin que son texte.
  3. LA RÉSERVE EST PORTÉE PAR CHAQUE PISTE, pas reléguée en note de bas de
     page — à commencer par le fait qu'aucune n'établit qu'il existe un
     acheteur.
  4. DEUX COÏNCIDENCES NE FONT PAS UN MOTIF. Le seuil de répétition ne
     descend pas sous trois.
"""
import os
import re
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import decision as D  # noqa: E402
import veille as V  # noqa: E402


def _fiche(**kw):
    base = {
        "id": "essai-fiche", "titre": "Titre", "chapeau": "Chapeau.",
        "lecture": "L" * 100, "lecture_nature": "regle",
        "portee": "P" * 80, "incertitude": "I" * 60,
        "sujet": "cyber_industriel", "date_fait": "2026-01-15",
        "source_cle": "cisa_kev", "source_url": "https://www.cisa.gov/x",
        "statut": "verifiee_source_primaire", "impact": "structurant",
        "horizon": "constate",
    }
    base.update(kw)
    n = V.normaliser(base)
    assert n["ok"], n.get("fautes")
    return n["fiche"]


def _corpus_fournisseur(n, editeur="Siemens"):
    return [_fiche(id="essai-f%02d" % i, editeur=editeur) for i in range(n)]


# ── 1. Aucune piste sans fiche ────────────────────────────────────────────

def test_toute_piste_pointe_des_fiches_nommees():
    for p in D.pistes(_corpus_fournisseur(4)):
        assert p["n_fiches"] >= D.MINI_REPETITION, p["titre"]
        assert p["fiches"], p["titre"]
        for f in p["fiches"]:
            assert f["id"] and f["titre"], p["titre"]


def test_un_corpus_vide_ne_produit_aucune_piste():
    """Le cas qui compte : le module doit savoir ne rien proposer. Proposer
    sans matière est exactement ce qu'on lui reproche par avance."""
    assert D.pistes([]) == []
    assert D.mesure([])["total"] == 0


def test_une_fiche_non_publiable_ne_declenche_aucune_piste():
    """Même porte que partout ailleurs : la réserve éditoriale ne s'ouvre pas
    par une fonctionnalité annexe."""
    cachees = [dict(f, statut="redigee_par_ia", lecture_nature="modele")
               for f in _corpus_fournisseur(5)]
    assert D.pistes(cachees) == []


# ── 2. Aucun chiffre de marché ────────────────────────────────────────────

def test_aucune_piste_ne_porte_de_chiffre_de_marche():
    """Un module qui dit « marché de 4,2 Md€ » a inventé les deux chiffres et
    l'unité. Le corpus ne porte aucune donnée de marché."""
    interdits = re.compile(
        r"(md€|milliard|m€|k€|\$|chiffre d'affaires|part de marché|"
        r"taux de croissance|tam\b|roi\b)", re.I)
    for p in D.pistes(_corpus_fournisseur(4)):
        for champ in ("titre", "declencheur", "suppose", "n_etablit_pas",
                      "disqualifie_par"):
            assert not interdits.search(p[champ]), (p["titre"], champ, p[champ])


def test_le_module_declare_ne_produire_aucun_chiffre_de_marche():
    assert D.sante()["chiffres_de_marche"] == 0
    assert D.sante()["modeles_de_langage"] == 0


def test_aucun_modele_de_langage_dans_la_derivation():
    src = open(os.path.join(ICI, "decision.py"), encoding="utf-8").read()
    for interdit in ("anthropic", "openai", "mistralai", "import requests"):
        assert interdit not in src.lower(), interdit


def test_deux_derivations_du_meme_corpus_rendent_les_memes_pistes():
    c = _corpus_fournisseur(4)
    assert D.pistes(c) == D.pistes(c)


# ── 3. Chaque piste porte sa réserve ──────────────────────────────────────

def test_chaque_piste_dit_qu_elle_n_etablit_pas_l_existence_d_un_acheteur():
    """C'est la seule chose qu'un lecteur pressé lira comme acquise."""
    pistes = D.pistes(_corpus_fournisseur(4))
    assert pistes
    for p in pistes:
        assert "acheteur" in p["n_etablit_pas"], p["titre"]
        assert len(p["suppose"]) > 40, p["titre"]
        assert len(p["disqualifie_par"]) > 30, p["titre"]


def test_chaque_piste_dit_sur_quoi_elle_repose():
    for p in D.pistes(_corpus_fournisseur(4)):
        assert p["solidite"] in D.SOLIDITES
        assert p["solidite_nom"] and len(p["solidite_dit"]) >= 40


def test_le_classement_suit_la_solidite_et_non_l_attrait():
    """Un classement qui aurait l'air commercial ferait passer une règle de
    tri pour un jugement de marché, que ce module ne peut pas porter."""
    c = (_corpus_fournisseur(4)
         + [_fiche(id="essai-r%02d" % i, impact="rupture", sujet="datacenter")
            for i in range(5)])
    rangs = [p["solidite"] for p in D.pistes(c)]
    assert rangs == sorted(rangs), rangs


# ── 4. Deux coïncidences ne font pas un motif ─────────────────────────────

def test_le_seuil_de_repetition_ne_descend_pas_sous_trois():
    assert D.MINI_REPETITION >= 3


def test_deux_fiches_concordantes_ne_suffisent_pas():
    assert D.pistes(_corpus_fournisseur(2)) == []
    assert D.pistes(_corpus_fournisseur(3)) != []


# ── 5. Un déclencheur muet le dit ─────────────────────────────────────────

def test_les_declencheurs_muets_sont_nommes():
    """Un module qui n'afficherait que ses déclencheurs féconds laisserait
    croire que les autres ne trouvent rien parce qu'il n'y a rien à trouver.
    Le plus souvent, c'est que la source qui les nourrirait n'est pas
    branchée."""
    m = D.mesure(_corpus_fournisseur(4))
    assert m["par_declencheur"]["fournisseur_recurrent"] >= 1
    assert "projection_declaree" in m["muets"]
    assert "projection_declaree" in m["dit"]


def test_la_mesure_couvre_tous_les_declencheurs():
    m = D.mesure([])
    assert set(m["par_declencheur"]) == {n for n, _ in D.DECLENCHEURS}


# ── 6. Une projection ne peut pas être anonyme ────────────────────────────

def test_une_projection_declenche_une_piste_qui_nomme_son_auteur():
    """Une échéance est le seul matériau qui autorise à parler d'avenir sans
    parier — à condition qu'elle engage quelqu'un."""
    c = [_fiche(id="essai-p%02d" % i, horizon="projete",
                projette_qui="Agence internationale de l'énergie")
         for i in range(3)]
    p = [x for x in D.pistes(c) if x["cle"].startswith("projection-")]
    assert p, D.mesure(c)
    assert "Agence internationale de l'énergie" in p[0]["titre"]
    assert p[0]["solidite"] == 3, "une projection ne vaut pas un fait constaté"
