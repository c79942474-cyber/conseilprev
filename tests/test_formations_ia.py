# -*- coding: utf-8 -*-
"""« Formations conformité IA » — les sujets, le calendrier, le tarif, mesurés.

CES RÈGLES MESURENT CE QUE LE MODULE PROMET, pas la présence d'un symbole : les
quatre sujets sont EXACTEMENT ceux du visuel ; le calendrier est hebdomadaire,
de 4 h, borné au premier créneau utile et à fin mars 2027 ; la première séance
est gratuite et les suivantes à 800 € HT — dans les deux sens, car un rang
aberrant ne doit ni faire payer une séance gratuite ni offrir une séance due.
"""
import datetime

import formations_ia as F

DEPUIS = datetime.date(2026, 9, 11)


def test_les_quatre_sujets_sont_ceux_du_visuel():
    """Quatre sujets, leurs intitulés au mot près, et un repère de contenu par
    résumé. Un cinquième sujet, ou « Sécurité de l'IA » sans EBIOS RM,
    tromperait le client sur ce qu'il réserve."""
    assert F.NB_SUJETS == 4 and len(F.SUJETS) == 4
    titres = [s["titre"] for s in F.SUJETS]
    assert titres == ["Gouvernance IA", "Gouvernance agentique",
                      "Sécurité de l'IA", "Ingénierie de projet"], titres
    par = {s["cle"]: s["resume"] for s in F.SUJETS}
    assert "Registre" in par["gouvernance-ia"]
    assert "seuils d'escalade" in par["gouvernance-agentique"]
    assert "EBIOS RM" in par["securite-ia"], par["securite-ia"]
    assert "MOE et AMO" in par["ingenierie-projet"]


def test_le_calendrier_est_hebdomadaire_sur_le_jour_de_seance_et_de_4h():
    """Une séance par semaine, sur le jour de séance, de la durée annoncée.
    Un pas de deux semaines, ou un jour qui dérive, casserait « toutes les
    semaines »."""
    c = F.creneaux(DEPUIS)
    assert len(c) >= 20, "trop peu de créneaux : le calendrier ne couvre pas la campagne"
    for x in c:
        d = datetime.date.fromisoformat(x["date"])
        assert d.weekday() == F.JOUR_SEANCE, ("créneau hors jour de séance : %s"
                                              % x["date"])
        assert x["duree_h"] == F.DUREE_H == 4
    for i in range(len(c) - 1):
        a = datetime.date.fromisoformat(c[i]["date"])
        b = datetime.date.fromisoformat(c[i + 1]["date"])
        assert (b - a).days == 7, ("deux créneaux ne sont pas à une semaine : "
                                   "%s → %s" % (c[i]["date"], c[i + 1]["date"]))


def test_le_calendrier_est_borne_au_debut_ET_a_fin_mars_2027():
    """Rien dans le passé, rien après la fin de campagne. Proposer une date
    passée, ou d'après mars 2027, serait promettre ce qu'on ne tiendra pas."""
    c = F.creneaux(DEPUIS)
    assert c[0]["date"] >= DEPUIS.isoformat(), "un créneau est dans le passé"
    # LE DÉLAI DE PRÉVENANCE EST TENU : le premier créneau n'est jamais avant
    # DEPUIS + LEAD_JOURS. Sans ce plancher, une séance pourrait être proposée
    # pour après-demain — invendable et intenable.
    assert c[0]["date"] >= (DEPUIS + datetime.timedelta(days=F.LEAD_JOURS)).isoformat(), (
        "le premier créneau ne respecte pas le délai de prévenance : %s"
        % c[0]["date"])
    assert c[-1]["date"] <= "2027-03-31", (
        "un créneau tombe après la fin de campagne : %s" % c[-1]["date"])
    # une date de référence APRÈS la campagne ne propose plus rien.
    assert F.creneaux(datetime.date(2027, 5, 1)) == [], (
        "des créneaux sont proposés après la fin de campagne")


def test_le_calendrier_est_DETERMINISTE():
    """Deux appels aux mêmes arguments rendent le même calendrier : le module
    ne lit pas l'horloge. Sinon deux visiteurs de la même minute verraient des
    dates différentes."""
    assert F.creneaux(DEPUIS) == F.creneaux(DEPUIS)
    assert F.creneaux("2026-09-11") == F.creneaux(datetime.date(2026, 9, 11))


def test_premiere_seance_gratuite_les_suivantes_a_800_HT():
    """La règle annoncée, mesurée : rang 0 gratuit à 0 €, rangs 1 à 3 à
    800 € HT, TTC calculé, jamais « gratuit » pour une séance due."""
    t0 = F.tarif(0)
    assert t0["gratuit"] and t0["ht_cents"] == 0 and t0["ttc_cents"] == 0
    for r in (1, 2, 3):
        t = F.tarif(r)
        assert not t["gratuit"], "la séance de rang %d ressort gratuite" % r
        assert t["ht_cents"] == 80000, (r, t["ht_cents"])
        assert t["ttc_cents"] == round(80000 * (100 + F.TVA_PCT) / 100.0)


def test_un_rang_aberrant_ne_DERAPE_dans_aucun_sens():
    """LE TÉMOIN DES DEUX CÔTÉS. Un rang négatif ou illisible est traité comme
    la première séance (gratuit) — on ne fait pas payer plus par une entrée
    aberrante ; et une séance due (rang ≥ 1) reste payante — on ne l'offre
    jamais par accident."""
    assert F.tarif(-3)["gratuit"] and F.tarif(-3)["ht_cents"] == 0
    assert F.tarif("bidon")["gratuit"] and F.tarif(None)["ht_cents"] == 0
    assert not F.tarif(1)["gratuit"] and F.tarif(1)["ht_cents"] == 80000


def test_le_tarif_est_une_SOURCE_UNIQUE():
    """Le prix affiché par la règle et le prix d'une séance payante viennent du
    même chiffre : affiché et facturé ne peuvent pas diverger."""
    assert F.regle_tarifaire()["ht_cents"] == F.tarif(1)["ht_cents"] \
        == F.TARIF_HT_CENTS == 80000


def test_le_referentiel_sert_tout_ce_qu_il_faut_a_la_page():
    r = F.referentiel(DEPUIS)
    assert r["offre"]["titre"] and r["offre"]["duree_h"] == 4
    assert len(r["sujets"]) == 4
    assert r["creneaux"] and r["creneaux"] == F.creneaux(DEPUIS)
    assert r["tarif"]["ht_cents"] == 80000 and r["tarif"]["nb_sujets"] == 4
