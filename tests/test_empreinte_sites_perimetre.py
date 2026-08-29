# -*- coding: utf-8 -*-
"""LA CARTE COUVRAIT DEUX SCOPES SUR TROIS SANS LE DIRE.

`empreinte_sites` calcule trois postes — usage, fabrication, eau — pour des
centres de données OBSERVÉS DE L'EXTÉRIEUR. C'est le scope 2 du GHG Protocol
et une partie du scope 3. Le SCOPE 1 n'y est pas : ni les fuites de fluide
frigorigène, ni le carburant des groupes.

CE N'EST PAS UN CALCUL FAUX — c'est un périmètre, et il est le bon : la charge
en fluide et le volume de gazole ne s'obtiennent que sur le site lui-même, et
les estimer pour un tiers reviendrait à inventer. Le module a raison de ne pas
les calculer.

LA FAUTE ÉTAIT DE NE PAS LE DIRE. Six limites étaient déclarées, toutes justes,
et aucune ne mentionnait ce périmètre. Un lecteur qui rapproche ces chiffres
d'un bilan d'entreprise croyait comparer des totaux comparables — alors qu'il
manque un scope entier d'un côté.
"""
import os
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import empreinte_sites  # noqa: E402


def _limite_scope1():
    for l in empreinte_sites.LIMITES:
        if "SCOPE 1" in l:
            return l
    return None


def test_le_perimetre_du_scope_1_est_declare():
    """Un périmètre tu est le seul défaut possible ici : la donnée manquante ne
    s'obtient pas sur le site d'un tiers, mais son absence, elle, se dit."""
    assert _limite_scope1(), (
        "aucune limite ne dit que le scope 1 est hors périmètre : ces chiffres "
        "se lisent comme un bilan complet")


def test_elle_nomme_les_deux_postes_directs():
    """« Le scope 1 n'est pas inclus » n'apprend rien à qui ne sait pas ce
    qu'il contient pour un centre de données."""
    l = _limite_scope1()
    for attendu in ("frigorigène", "électrogène"):
        assert attendu in l, "la limite ne nomme pas les %s" % attendu


def test_elle_dit_pourquoi_ces_valeurs_ne_sont_pas_estimees():
    """Sans la raison, un lecteur croit à un oubli et attend la version
    suivante. La raison est qu'il n'y a rien à attendre : la donnée ne se
    trouve pas de l'extérieur."""
    l = _limite_scope1()
    assert "site lui-même" in l or "site lui-meme" in l
    assert "tiers" in l


def test_elle_dit_ce_que_la_carte_ne_remplace_pas():
    l = _limite_scope1()
    assert "BEGES" in l, (
        "la limite ne dit pas qu'un bilan réglementaire exige ce qui manque")


def test_les_six_limites_anterieures_sont_conservees():
    """L'ajout ne doit pas avoir remplacé ce qui existait — chacune de ces six
    porte un défaut réel constaté ailleurs."""
    assert len(empreinte_sites.LIMITES) >= 7
    plat = " ".join(empreinte_sites.LIMITES)
    for reste in ("PARC ≠ TOTAL", "moyennes annuelles", "REFROIDISSEMENT",
                  "FABRICATION du matériel", "amortie linéairement",
                  "projet annoncé"):
        assert reste in plat, "la limite « %s » a disparu" % reste
