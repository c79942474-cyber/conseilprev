"""LA DISCIPLINE ÉDITORIALE — ce que ce site ne doit jamais pouvoir faire.

Ces contrôles ne vérifient pas que le code « marche ». Ils gardent les quatre
règles qui font la différence entre une veille et un agrégateur, et chacune
est écrite pour tomber le jour où quelqu'un tentera de l'assouplir « juste
pour cette fiche-là » :

  1. UNE FICHE SANS SOURCE ADMISE N'EXISTE PAS. Pas « affichée avec une
     réserve » : refusée.
  2. UNE LECTURE DE MODÈLE DE LANGAGE NE SORT JAMAIS. Ni par le statut, ni
     par la nature de lecture, ni par la combinaison des deux.
  3. CE QU'ON NE SAIT PAS EST OBLIGATOIRE. Une fiche sans incertitude
     déclarée est une fiche qui promet plus qu'elle ne tient.
  4. LES FILTRES NE PEUVENT PAS OUVRIR CE QUE LA PORTE FERME. Aucun
     paramètre d'URL ne doit faire sortir une fiche non publiable.
"""
import os
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import ingestion as I  # noqa: E402
import sources as SRC  # noqa: E402
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
    return base


# ── 1. Pas de source admise, pas de fiche ─────────────────────────────────

def test_une_fiche_sans_source_est_refusee():
    f = _fiche()
    del f["source_cle"]
    assert any("source_cle" in x for x in V.valider(f))


def test_une_source_hors_registre_est_refusee():
    """C'est ce qui empêche d'inventer une provenance : on ne peut citer que
    ce qui a été admis ET sondé."""
    fautes = V.valider(_fiche(source_cle="mon_blog"))
    assert any("hors registre" in x for x in fautes), fautes


def test_toute_source_du_registre_dit_ce_qu_elle_ne_couvre_pas():
    for s in SRC.registre():
        assert len(s["ne_couvre_pas"]) >= 40, s["cle"]


def test_toute_source_porte_une_adresse_de_donnee_chiffree():
    for s in SRC.registre():
        assert s["url_donnee"].startswith("https://"), s["cle"]


# ── 2. Une lecture de modèle ne sort jamais ───────────────────────────────

def test_une_lecture_de_modele_ne_peut_pas_etre_publiable():
    fautes = V.valider(_fiche(lecture_nature="modele"))
    assert any("modèle de langage" in x for x in fautes), fautes


def test_le_statut_redige_par_ia_n_est_pas_publiable():
    assert V.STATUTS["redigee_par_ia"]["publiable"] is False
    assert V.LECTURES["modele"]["publiable"] is False


def test_la_porte_croise_le_statut_ET_la_nature_de_lecture():
    """Deux verrous indépendants : oublier l'un ne doit pas suffire à
    publier. C'est le contrôle qui rattrape une erreur de saisie."""
    n = V.normaliser(_fiche())
    assert n["ok"]
    bonne = n["fiche"]
    # statut publiable mais lecture de modèle → ne sort pas
    mauvaise = dict(bonne, lecture_nature="modele")
    assert V.publiables([bonne, mauvaise]) == [bonne]
    # lecture publiable mais statut en réserve → ne sort pas non plus
    reserve = dict(bonne, statut="a_verifier")
    assert V.publiables([bonne, reserve]) == [bonne]


def test_aucun_modele_de_langage_dans_la_chaine_de_collecte():
    """La promesse affichée en tête de site. Elle doit être vraie dans le
    code, pas seulement dans le bandeau."""
    assert I.sante()["modeles_de_langage"] == 0
    src = open(os.path.join(ICI, "ingestion.py"), encoding="utf-8").read()
    for interdit in ("anthropic", "openai", "mistralai", "import requests"):
        assert interdit not in src.lower(), interdit


# ── 3. Ce qu'on ne sait pas est obligatoire ───────────────────────────────

def test_une_fiche_sans_incertitude_est_refusee():
    f = _fiche()
    del f["incertitude"]
    assert any("incertitude" in x for x in V.valider(f))


def test_une_lecture_trop_courte_est_refusee():
    """Une « analyse critique » de six mots est un slogan."""
    fautes = V.valider(_fiche(lecture="Intéressant."))
    assert any("trop courte" in x for x in fautes), fautes


def test_une_projection_doit_nommer_qui_la_porte():
    """Sans cela, une hypothèse à 2030 se lit comme un fait établi — c'est la
    faute la plus coûteuse d'un site de veille."""
    fautes = V.valider(_fiche(horizon="projete"))
    assert any("projette_qui" in x for x in fautes), fautes
    assert not V.valider(_fiche(horizon="projete",
                                projette_qui="Agence internationale de l'énergie"))


def test_une_date_dans_l_avenir_est_refusee():
    assert any("avenir" in x for x in V.valider(_fiche(date_fait="2099-01-01")))


# ── 4. Les filtres n'ouvrent pas ce que la porte ferme ────────────────────

def test_aucun_filtre_ne_fait_sortir_une_fiche_non_publiable():
    bonne = V.normaliser(_fiche())["fiche"]
    cachee = dict(bonne, id="essai-cachee", statut="redigee_par_ia",
                  lecture_nature="modele")
    corpus = [bonne, cachee]
    for kw in ({}, {"sujet": "cyber_industriel"}, {"impact": "structurant"},
               {"horizon": "constate"}, {"depuis": "2000-01-01"},
               {"statut": "redigee_par_ia"}):
        sortie = V.filtrer(corpus, **kw)
        assert all(f["id"] != "essai-cachee" for f in sortie), kw


def test_les_facettes_ne_comptent_que_le_publiable():
    bonne = V.normaliser(_fiche(pays=["FR"]))["fiche"]
    cachee = dict(V.normaliser(_fiche(id="essai-c2", pays=["DE"]))["fiche"],
                  statut="a_verifier")
    f = V.facettes([bonne, cachee])
    codes = [p["cle"] for p in f["pays"]]
    assert "FR" in codes and "DE" not in codes


def test_le_plus_important_sort_en_premier():
    """Trier d'abord par date ferait descendre une rupture sous trois brèves
    du lendemain."""
    vieux_rupture = V.normaliser(_fiche(id="essai-r1", impact="rupture",
                                        date_fait="2020-01-01"))["fiche"]
    recent_mineur = V.normaliser(_fiche(id="essai-i1", impact="incremental",
                                        date_fait="2026-08-01"))["fiche"]
    assert V.filtrer([recent_mineur, vieux_rupture])[0]["id"] == "essai-r1"


# ── 5. La détection industrielle ne classe pas au hasard ──────────────────

def test_un_mot_ordinaire_ne_vaut_pas_un_sigle_industriel():
    """DÉFAUT CORRIGÉ : « Ethernet DIAGNOSTICS Driver » entrait au périmètre
    industriel parce que « diagnostics » contient « ics », et « VIRTUAL
    System » parce que « virtual » contient « rtu »."""
    assert I._industriel("Intel", "Ethernet Diagnostics Driver")[0] is False
    assert I._industriel("Kaseya", "Virtual System/Server Administrator")[0] is False


def test_un_prefixe_de_modele_ne_vaut_pas_un_sigle():
    """DÉFAUT CORRIGÉ : les caméras « D-Link DCS-2530L » entraient par le
    sigle DCS, qui n'y est qu'une référence de gamme."""
    assert I._industriel("D-Link", "DCS-2530L and DCS-2670L Devices")[0] is False
    assert I._industriel("Acme", "DCS Controller")[0] is True


def test_les_vrais_produits_industriels_restent_detectes():
    for v, p in (("Siemens", "SIMATIC CP"), ("Unitronics", "Vision PLC and HMI"),
                 ("Acme", "SCADA Server"), ("Moxa", "NPort")):
        assert I._industriel(v, p)[0] is True, (v, p)


def test_un_acteur_n_est_ni_un_editeur_ni_une_technologie():
    """DÉFAUT CORRIGÉ. Le champ `actor` d'ATLAS alimentait `editeur` — dont le
    lien annonce « même contrat, même fenêtre de maintenance », phrase fausse
    appliquée à un attaquant — et `technologies`, ce qui offrait des noms de
    chercheurs dans le filtre par technologie et fondait les DEUX seuls liens
    forts du corpus sur « Unknown Threat Actor », c'est-à-dire sur l'aveu de
    la source qu'elle ne sait pas qui c'est."""
    r = I.collecter_atlas(limite_cas=8)
    if not r.get("ok"):
        import pytest
        pytest.skip("ATLAS injoignable : %s" % r.get("erreur"))
    for f in r["fiches"]:
        assert f.get("editeur") is None, f["id"]
        for t in f.get("technologies") or []:
            assert "unknown" not in t.lower(), (f["id"], t)
        assert set(f.get("technologies") or []) <= {
            "MITRE ATLAS", "Sécurité des systèmes d'IA", "Incident réel"}, f["id"]


def test_l_entite_nommee_reste_lisible_avec_son_role():
    """Retirer l'acteur des clés de tri ne doit pas le faire disparaître : ce
    qu'un libellé unique ne peut pas porter, une phrase le porte — et elle dit
    lequel des deux rôles c'est, puisque la source distingue l'incident de
    l'exercice."""
    r = I.collecter_atlas(limite_cas=8)
    if not r.get("ok"):
        import pytest
        pytest.skip("ATLAS injoignable")
    nommees = [f for f in r["fiches"] if "La source nomme" in f["lecture"]]
    assert nommees, "aucune entité nommée sur huit cas"
    for f in nommees:
        assert ("l'équipe qui a conduit l'exercice" in f["lecture"]
                or "l'entité à laquelle elle rattache l'incident" in f["lecture"]), \
            f["id"]


def test_une_relation_atlas_ne_relie_que_des_fiches_reellement_servies():
    """Pointer vers une entité dont ce site ne publie rien donnerait un lien
    mort. ATLAS référence 145 techniques ; le site en sert huit."""
    a = {"id": "atlas-aml-cs0051", "titre": "Le cas"}
    b = {"id": "atlas-tech-aml-t0054", "titre": "La technique"}
    n = I._relier_atlas([a, b])
    if n == 0:
        import pytest
        pytest.skip("ATLAS injoignable ou couple absent du référentiel")
    for f in (a, b):
        for rel in f.get("relations") or []:
            assert rel["vers"] in {"atlas-aml-cs0051", "atlas-tech-aml-t0054"}


_ATLAS_REPETE = {"case-studies": [{
    "id": "AML.CS9001", "name": "Cas d'essai",
    "references": [{"title": "Rapport d'origine"}],
    "procedure": [
        {"technique": "AML.T0054", "description": "Première étape."},
        {"technique": "AML.T0054", "description": "Deuxième étape, même "
                                                  "technique."},
        {"technique": "AML.T0054", "description": "Troisième étape."},
    ],
}]}


def test_une_technique_employee_a_trois_etapes_ne_donne_qu_un_lien():
    """Sinon le lecteur lit trois faits là où il n'y en a qu'un.

    Le document est fourni plutôt qu'allé chercher : aucune étude de cas du
    référentiel n'emploie aujourd'hui deux fois une technique que ce site
    sert, si bien qu'un contrôle branché sur les données réelles passerait au
    vert sans rien garder."""
    a = {"id": "atlas-aml-cs9001", "titre": "Le cas"}
    b = {"id": "atlas-tech-aml-t0054", "titre": "La technique"}
    n = I._relier_atlas([a, b], atlas=_ATLAS_REPETE)
    assert n == 1, n
    assert len(a["relations"]) == 1 and len(b["relations"]) == 1
    assert "Première étape" in a["relations"][0]["dit"]


def test_le_motif_d_une_relation_atlas_est_la_phrase_de_la_source():
    """Ce qui distingue ce lien de tous les autres : son motif n'est pas une
    catégorie que nous posons, c'est le récit de l'étape par la source."""
    a = {"id": "atlas-aml-cs0051", "titre": "Le cas"}
    b = {"id": "atlas-tech-aml-t0054", "titre": "La technique"}
    if I._relier_atlas([a, b]) == 0:
        import pytest
        pytest.skip("ATLAS injoignable ou couple absent du référentiel")
    rel = a["relations"][0]
    assert rel["dit"].startswith("ATLAS décrit ainsi cette étape")
    assert len(rel["dit"]) > 60, rel["dit"]


def test_une_relation_sans_les_deux_bouts_n_est_pas_creee():
    seule = {"id": "atlas-aml-cs0051", "titre": "Le cas"}
    I._relier_atlas([seule])
    assert not seule.get("relations")


def test_le_repertoire_d_editeurs_est_declare_comme_un_jugement():
    """Il n'est pas une donnée de source : le catalogue KEV ne dit pas qui est
    automaticien. Le code doit le reconnaître par écrit."""
    src = open(os.path.join(ICI, "ingestion.py"), encoding="utf-8").read()
    i = src.index("EDITEURS_INDUSTRIELS")
    entete = src[max(0, i - 900):i]
    assert "JUGEMENT DU CABINET" in entete


# ── 6. La lecture par règles est reproductible ────────────────────────────

def test_deux_lectures_de_la_meme_donnee_rendent_le_meme_texte():
    """C'est toute la raison de ne pas employer de modèle de langage : une
    veille dont l'analyse change à chaque passage n'est pas une veille."""
    from datetime import date
    e = {"cveID": "CVE-2026-0001", "vendorProject": "Siemens",
         "product": "SIMATIC", "vulnerabilityName": "Essai",
         "dateAdded": "2026-02-01", "dueDate": "2026-03-01",
         "knownRansomwareCampaignUse": "Known"}
    a = I._lecture_kev(e, True, "éditeur au répertoire", date(2026, 8, 22))
    b = I._lecture_kev(e, True, "éditeur au répertoire", date(2026, 8, 22))
    assert a == b and len(a) > 200


# ── 7. Le registre ne peut plus annoncer ce qu'il ne lit pas ──────────────

def test_le_registre_dit_quelles_sources_sont_reellement_lues():
    """DÉFAUT CORRIGÉ. Le registre annonçait neuf sources — chacune avec son
    bouton « Sonder » prouvant qu'elle répond — alors que quatre seulement
    nourrissaient le corpus. Un lecteur en concluait que le site s'appuie sur
    neuf sources, et l'écart ne se voyait de nulle part."""
    lues = I.sources_collectees()
    assert lues <= set(SRC.SOURCES), sorted(lues - set(SRC.SOURCES))
    for s in SRC.registre():
        assert s["collectee"] in (True, False), s["cle"]
        if not s["collectee"]:
            assert len(s["pourquoi_pas_lue"]) >= 60, s["cle"]


def test_l_etat_de_lecture_se_derive_de_la_table_des_collecteurs():
    """Il ne peut pas diverger de la réalité parce qu'il EST la réalité : une
    seconde liste écrite à côté aurait recommencé la dérive qu'on répare."""
    src = open(os.path.join(ICI, "ingestion.py"), encoding="utf-8").read()
    assert "def _table_collecteurs" in src
    # la boucle de collecte et la déclaration lisent la MÊME table
    i = src.index("def collecter_tout")
    assert "_table_collecteurs(limite_kev, limite_mix)" in src[i:i + 900]
    j = src.index("def sources_collectees")
    assert "_table_collecteurs(" in src[j:j + 500]


def test_une_source_qui_cesse_d_etre_lue_ne_peut_pas_passer_inapercue():
    """Le contrôle qui garde la correction : toute source du registre est soit
    lue, soit accompagnée du motif écrit de son sommeil."""
    muettes = [s["cle"] for s in SRC.registre()
               if not s["collectee"] and not s["pourquoi_pas_lue"]]
    assert not muettes, muettes


# ── 8. Une filière n'est pas une technologie de la fiche ──────────────────

def test_une_fiche_de_zone_ne_porte_pas_ses_filieres_en_technologies():
    """DÉFAUT CORRIGÉ AVANT MISE EN LIGNE. Les trois filières les plus
    émettrices entraient dans `technologies` : mesuré, cela produisait 132
    liens « même technologie » portant tous le motif identique « charbon,
    fioul, gaz » — ces trois-là sont en tête dans presque tous les pays. Le
    champ reliait donc chaque zone à toutes les autres, avec la même phrase
    recopiée. C'est mot pour mot la faute pour laquelle « mode operatoire » a
    été écarté du croisement."""
    r = I.collecter_electricity_maps(limite=3)
    if not r.get("ok"):
        import pytest
        pytest.skip("Electricity Maps injoignable")
    for f in r["fiches"]:
        assert set(f["technologies"]) == {"Mix électrique", "Empreinte carbone"}, \
            (f["id"], f["technologies"])


def test_chaque_facteur_servi_porte_sa_source_et_son_millesime():
    """C'est ce que cette source apporte que les autres n'ont pas : ailleurs
    une valeur porte la source du jeu entier, ici elle porte la sienne."""
    r = I.collecter_electricity_maps(limite=2)
    if not r.get("ok"):
        import pytest
        pytest.skip("Electricity Maps injoignable")
    import re as _re
    for f in r["fiches"]:
        # « charbon 1028 gCO2e/kWh (2025, EU-ETS 2025, ENTSO-E 2025; IPCC 2014) »
        assert _re.search(r"gCO2e/kWh \(\d{4}, ", f["chapeau"]), f["chapeau"][:120]
        assert "CYCLE DE VIE" in f["lecture"]


def test_la_date_de_la_fiche_est_celle_du_facteur_le_plus_recent():
    """Dater d'aujourd'hui une valeur de 2020 la ferait passer pour neuve."""
    r = I.collecter_electricity_maps(limite=2)
    if not r.get("ok"):
        import pytest
        pytest.skip("Electricity Maps injoignable")
    from datetime import date as _d
    for f in r["fiches"]:
        assert f["date_fait"] <= _d.today().isoformat(), f["id"]
        assert f["date_fait"] >= "2000-01-01", f["id"]
