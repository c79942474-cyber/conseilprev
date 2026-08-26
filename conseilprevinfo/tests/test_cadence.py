"""LES CADENCES — chaque source relue au rythme auquel ELLE change.

POURQUOI CE N'EST PAS UNE OPTIMISATION. Le site rafraîchissait tout d'un bloc,
toutes les trente minutes. Rapprocher cette cadence pour suivre l'actualité de
plus près aurait retéléchargé à chaque tour les référentiels ATT&CK et ATLAS —
neuf mégaoctets — pour des fichiers que MITRE révise quelques fois par an. Ce
n'est pas une dépense de serveur : c'est de la charge prise sur des sources
publiques et gratuites, qui la supportent parce que personne n'en abuse.

Ce fichier garde les trois règles qui rendent la chose tenable, et la
quatrième qui a été trouvée en la mesurant.
"""
import os
import sys
import time

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import ingestion as I  # noqa: E402


def _lire(nom):
    return open(os.path.join(ICI, nom), encoding="utf-8").read()


def test_chaque_collecteur_declare_sa_cadence():
    """Une source sans cadence déclarée est relue à chaque tour : le choix le
    plus prudent pour le site, le moins poli pour la source. L'oubli doit donc
    faire tomber un contrôle, pas passer inaperçu."""
    noms = [n for n, _ in I._table_collecteurs(0, None)]
    manquantes = [n for n in noms if n not in I.CADENCES]
    assert not manquantes, manquantes


def test_les_referentiels_lourds_ne_sont_pas_relus_au_quart_d_heure():
    """ATT&CK et ATLAS pèsent neuf mégaoctets et bougent quelques fois par an.
    Les relire au rythme d'un catalogue de vulnérabilités serait impoli, et
    ferait bannir ce site avant longtemps."""
    for lourd in ("mitre_attack_ics", "mitre_atlas", "mitre_atlas_tech"):
        assert I.CADENCES[lourd] >= 12 * 3600, lourd
    # Et le catalogue qui bouge dans la journée, lui, est relu souvent.
    assert I.CADENCES["cisa_kev"] <= 3600


def test_un_echec_n_est_jamais_mis_en_cache():
    """Garder une erreur pendant toute la cadence servirait la panne un quart
    d'heure, alors qu'une coupure réseau dure souvent quelques secondes."""
    I.oublier_cache()
    r, relu = I._relire("essai", lambda: {"ok": False, "erreur": "reseau"},
                        time.time())
    assert relu is True and r["ok"] is False
    assert "essai" not in I._CACHE
    # Le tour suivant retourne vraiment voir.
    _, relu2 = I._relire("essai", lambda: {"ok": False, "erreur": "reseau"},
                         time.time())
    assert relu2 is True


def test_une_source_momentanement_muette_ne_vide_pas_sa_rubrique():
    """On ressert ce qu'elle avait donné — mais le journal DIT que la
    relecture a échoué. Sans cette ligne, une source muette depuis trois jours
    servirait ses fiches d'origine sans que rien ne le signale, et le lecteur
    daterait le corpus de la dernière collecte réussie du SITE, pas de celle
    de cette source-là."""
    I.oublier_cache()
    t = time.time()
    I._relire("essai", lambda: {"ok": True, "fiches": [{"id": "a"}]}, t)
    r, relu = I._relire("essai", lambda: {"ok": False, "erreur": "reseau",
                                          "message": "injoignable"},
                        t + 10_000)
    assert relu is True
    assert r["ok"] is True and len(r["fiches"]) == 1
    assert r["relecture_echouee"]["erreur"] == "reseau"


def test_le_cache_ne_rend_jamais_les_objets_qu_il_garde():
    """DÉFAUT MESURÉ DÈS LE PREMIER ESSAI : le corpus tombait de 98 à 90 fiches
    au deuxième tour. La cause n'était pas la collecte mais le cache — il
    rendait les MÊMES dictionnaires, et les étapes qui suivent la collecte les
    modifient. Au tour suivant, les fiches portaient déjà leurs liens, l'étape
    croyait n'avoir rien à faire, et huit fiches ne revenaient pas.

    Rien ne plantait, rien ne s'affichait en rouge : le site servait
    simplement huit fiches de moins à partir du deuxième quart d'heure."""
    I.oublier_cache()
    t = time.time()
    original = {"ok": True, "fiches": [{"id": "a", "liens": []}]}
    a, _ = I._relire("essai", lambda: original, t)
    a["fiches"][0]["liens"].append("posé après coup")
    b, relu = I._relire("essai", lambda: original, t + 1)
    assert relu is False
    assert b["fiches"][0]["liens"] == [], b["fiches"][0]
    # Et la première réponse est déjà indépendante du cache, pas seulement la
    # seconde : les deux doivent l'être dès le premier tour.
    assert I._CACHE["essai"]["r"]["fiches"][0]["liens"] == []


def test_le_corpus_est_le_meme_a_chaque_tour():
    """Le contrôle qui aurait attrapé le défaut ci-dessus si on l'avait écrit
    d'abord. Il est lent — deux collectes réelles — mais c'est le seul qui
    mesure ce qui compte : ce que le lecteur reçoit."""
    I.oublier_cache()
    un = I.collecter_tout(limite_kev=4)
    deux = I.collecter_tout(limite_kev=4)
    assert len(deux["corpus"]) == len(un["corpus"]), (
        len(un["corpus"]), len(deux["corpus"]))
    assert ({f["id"] for f in un["corpus"]}
            == {f["id"] for f in deux["corpus"]})
    # ET LE SECOND TOUR N'A ROUVERT AUCUNE SOURCE QUI AVAIT RÉPONDU.
    #
    # « Aucune source », tout court, était trop fort — et ne se voyait pas
    # tant que toutes répondaient depuis cet environnement. La règle écrite
    # dans `_relire` est double : un succès se garde pour la durée de sa
    # cadence, UN ÉCHEC NE SE GARDE PAS, parce que servir l'erreur pendant un
    # quart d'heure serait pire qu'une panne de quelques secondes. Une source
    # en échec est donc rouverte au tour suivant, et c'est voulu.
    #
    # Les flux de presse rendent ce cas ordinaire : la politique réseau de
    # l'environnement de conception les refuse tous les quinze.
    reussies = {j["source"] for j in deux["journal"] if j.get("ok")}
    for j in deux["journal"]:
        if "relu" not in j:
            continue
        if j["source"] in reussies:
            assert j["relu"] is False, "%s a été rouverte alors qu'elle avait répondu" % j["source"]
        else:
            assert j["relu"] is True, (
                "%s a échoué et n'a pas été retentée : l'échec a été mis en "
                "cache, et l'erreur se servira pendant toute la cadence"
                % j["source"])


def test_le_journal_dit_ce_qui_a_ete_relu_et_a_quelle_cadence():
    """« La source a répondu » et « on n'y est pas retourné » ne sont pas la
    même chose, et le lecteur du registre doit pouvoir les distinguer."""
    I.oublier_cache()
    j = I.collecter_tout(limite_kev=4)["journal"]
    lignes = [x for x in j if "relu" in x]
    assert lignes
    for x in lignes:
        assert x["relu"] is True
        assert x.get("cadence_s"), x


def test_le_site_rafraichit_plus_souvent_qu_avant():
    """C'est la demande : suivre l'actualité de plus près. Elle n'était pas
    tenable avant les cadences ; elle l'est maintenant, et le défaut du
    serveur le reflète."""
    src = _lire("app.py")
    i = src.index('TTL = int(os.environ.get("VEILLE_TTL"')
    ligne = src[i:src.index("\n", i)]
    valeur = int(ligne.split('"')[-2])
    assert valeur <= 600, ligne
    # Et le motif est écrit là où quelqu'un serait tenté de le remonter.
    assert "CADENCES" in src[i - 900:i]
