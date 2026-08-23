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
import re
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


def test_une_date_de_convention_doit_dire_de_quoi_elle_tient_lieu():
    """DÉFAUT CONSTATÉ EN SERVICE. Une source qui date son ÉDITION sans dater
    ses entrées oblige le collecteur à poser un jour. Le poser est légitime ;
    le poser SANS LE DIRE ne l'est pas — le lecteur ne peut pas distinguer un
    fait daté d'un rang de classement."""
    fautes = V.valider(_fiche(date_convention=True))
    assert any("convention" in x for x in fautes), fautes
    assert not V.valider(_fiche(
        date_convention=True,
        date_convention_dit="OWASP date son édition, pas ses entrées."))


def test_l_horizon_constate_cesse_de_promettre_une_date_qu_il_n_a_pas():
    """« Constaté » dit « Établi à la date indiquée » — précisément la
    promesse qu'une date fabriquée ne tient pas. Aucun autre horizon ne
    conviendrait : un risque reconnu EST établi, il n'est ni engagé ni
    projeté. C'est donc la PHRASE qui doit dire vrai, pas l'horizon qu'il faut
    fausser."""
    ordinaire = V.normaliser(_fiche())["fiche"]
    assert ordinaire["horizon_dit"] == V.HORIZONS["constate"]["dit"]
    convenue = V.normaliser(_fiche(
        date_convention=True,
        date_convention_dit="La source date son édition, pas ses entrées."))["fiche"]
    assert "PAS à la date affichée" in convenue["horizon_dit"]
    assert "édition" in convenue["horizon_dit"]


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
    motif = ("éditeur au répertoire", "vendor in the directory")
    a = I._lecture_kev(e, True, motif, date(2026, 8, 22))
    b = I._lecture_kev(e, True, motif, date(2026, 8, 22))
    # LA LECTURE REND DEUX LANGUES : la reproductibilité vaut pour les deux,
    # et pas seulement pour la colonne qu'on regarde.
    assert a == b
    assert len(a) == 2 and all(len(x) > 200 for x in a)
    # ET LES DEUX SUIVENT LES MÊMES CONDITIONS. Une lecture française à quatre
    # phrases en face d'une anglaise à trois voudrait dire que la logique de
    # choix s'est dédoublée — ce que `gabarits.Deux` existe pour empêcher.
    assert a[0].count(".") == a[1].count(".")


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


# ── 9. OWASP : une source qu'on lit mal ressemble à une source muette ─────
#
# La rubrique « systèmes d'IA » ne portait que des INCIDENTS (ATLAS). OWASP
# apporte l'autre face — ce qu'une communauté RECONNAÎT comme menaçant. Trois
# choses doivent être gardées : que les dix entrées soient réellement lues,
# que ce qui est lu vienne de la SECTION ANNONCÉE, et que chaque fiche dise
# laquelle des deux natures elle porte.

_OWASP_DOCS = {}


def _owasp_reels():
    """Les dix documents d'OWASP, lus UNE SEULE FOIS pour tout le fichier.

    Trois contrôles portent sur les données réelles ; en laissant chacun aller
    les chercher, le fichier faisait trente lectures réseau, et l'une d'elles
    a fini par échouer — rendant rouge un contrôle qui n'avait rien à
    reprocher au code. Un test qui rougit au hasard apprend à relancer jusqu'au
    vert, et c'est exactement ainsi qu'une vraie panne finit ignorée.
    """
    if not _OWASP_DOCS:
        for fichier, _, _en in I.OWASP_LLM:
            r = I._lire(I._OWASP_BASE + fichier + ".md", delai=25)
            if not r["ok"]:
                import pytest
                pytest.skip("OWASP injoignable")
            _OWASP_DOCS[fichier] = r["corps"].decode("utf-8", "replace")
    return _OWASP_DOCS


def test_les_dix_entrees_owasp_sont_toutes_lues():
    """LE CONTRÔLE QUI AURAIT ATTRAPÉ LE PREMIER DÉFAUT. En cherchant un
    libellé de section EXACT, le collecteur rejetait deux entrées sur trois —
    et les comptait « illisibles », c'est-à-dire du même mot qu'une source qui
    ne répond pas. Rien à l'écran ne distinguait « OWASP est en panne » de
    « nous lisons mal OWASP ».

    CE CONTRÔLE NE SUFFIT PAS, et il faut l'écrire ici : il mesure qu'une
    section SORT, pas qu'elle soit la bonne. C'est le contrôle suivant qui
    porte cette seconde question."""
    r = I.collecter_owasp_llm(documents=_owasp_reels())
    assert r["ok"], r
    assert r["retenues"] == len(I.OWASP_LLM), r["dit"]
    assert "illisibles" not in r["dit"], r["dit"]


def test_une_section_qu_on_ne_sait_pas_lire_est_comptee():
    """LE TROU QUE LA MUTATION A RÉVÉLÉ. Rétablir le libellé exact — le défaut
    d'origine — laissait passer TOUS les contrôles : les manifestations
    n'entrent pas dans le garde-fou de publication, si bien que sept entrées
    sur dix repartaient amputées de leur section, sans que rien ne bouge.

    OWASP publie ces exemples sur les dix entrées. Un compteur non nul ne dit
    donc pas que la source s'est tue : il dit que NOUS la lisons mal, et il le
    dit à l'écran, pas seulement ici."""
    r = I.collecter_owasp_llm(documents=_owasp_reels())
    assert r["ok"], r
    assert r["sans_manifestation"] == 0, r["dit"]


def test_owasp_declare_que_sa_date_est_une_convention():
    """DÉFAUT CONSTATÉ EN SERVICE, et le contrôle qui manquait. La règle
    « une date fabriquée ne rapproche rien » vit dans le croisement, et elle
    y est gardée ; mais RIEN NE VÉRIFIAIT que le collecteur qui invente la
    date la déclare. Sans ce contrôle, retirer une ligne d'`ingestion.py`
    rouvrait le défaut d'origine sans faire tomber un seul essai.

    OWASP date son édition, pas ses entrées : ce jour est de nous."""
    r = I.collecter_owasp_llm(documents=_owasp_reels())
    assert r["ok"], r
    for f in r["fiches"]:
        assert f.get("date_convention") is True, f["id"]
        assert "ÉDITION" in f["date_convention_dit"], f["id"]
        assert "PAS à la date affichée" in f["horizon_dit"], f["id"]


def test_aucune_fiche_owasp_n_est_rapprochee_par_sa_date():
    """LE CONTRÔLE DE BOUT EN BOUT. Les deux précédents gardent chacun une
    moitié du chemin — la déclaration ici, la règle dans le croisement. Celui-
    ci mesure ce que le lecteur voit : dix fiches portant toutes le 1er
    janvier ne doivent former aucun voisinage entre elles."""
    import croisement as X
    fiches = I.collecter_owasp_llm(documents=_owasp_reels())["fiches"]
    ids = {f["id"] for f in fiches}
    for f in fiches:
        periode = [v for v in X.liens(f, fiches)
                   if v["lien"] == "meme_periode" and v["id"] in ids]
        assert not periode, (f["id"], periode[:2])


def test_le_compteur_de_section_manquante_se_dit_quand_il_n_est_pas_nul():
    """Un compteur qu'on tient sans l'afficher ne garde rien : il faut que
    l'écart se voie là où le lecteur lit la source."""
    ampute = ("## LLM01:2025 Essai\n\n### Description\n\nUne description assez "
              "longue pour tenir lieu de chapeau.\n\n"
              "### Prevention and Mitigation Strategies\n\n"
              "- Une parade publiée par la source, assez longue.\n")
    fichier = I.OWASP_LLM[0][0]
    r = I.collecter_owasp_llm(limite=1, documents={fichier: ampute})
    assert r["ok"] and r["retenues"] == 1        # la fiche vaut sans elles
    assert r["sans_manifestation"] == 1
    assert "manifestation" in r["dit"], r["dit"]


def test_une_section_lue_s_arrete_avant_la_suivante():
    """LE SECOND DÉFAUT, ET IL ÉTAIT PIRE. Le motif s'appliquait sous `re.S`,
    où le point franchit les retours à la ligne : « Types of .+ » avalait le
    document entier et rendait sa QUEUE. La fiche LLM01 publiait donc
    « AML.T0054 — LLM Jailbreak Injection » en exemple de manifestation : le
    pied de page des références, servi comme un contenu de section.

    L'INVARIANT A DÛ ÊTRE REFORMULÉ, et le premier essai mérite d'être écrit :
    « un bloc lu ne contient aucun titre » ne garde rien du tout, puisque le
    regard-avant `(?=\\n#{2,3})` l'assure quelle que soit la faute. Ce qui
    déraille n'est pas où le bloc FINIT, c'est où il COMMENCE. Le contrôle
    porte donc là : le texte rendu doit être précédé, immédiatement, d'une
    ligne qui est le titre demandé — ce qu'un titre débordant sur les lignes
    suivantes ne peut pas produire. L'invariant ne connaît rien du texte
    d'OWASP et survivra donc à ses rééditions."""
    for fichier, t in _owasp_reels().items():
        for motif in ("Description",
                      r"(?:Common Examples? of \w+|Types of .+)",
                      "Prevention and Mitigation Strategies"):
            bloc = I._owasp_bloc(t, motif)
            assert bloc, (fichier, motif)
            avant = t[:t.index(bloc)].rstrip("\n").rsplit("\n", 1)[-1]
            assert re.match(r"^#{2,4}[ \t]*(?:%s)[ \t]*$" % motif, avant,
                            re.I), (fichier, motif, avant[:120])


_OWASP_MODELE = """## LLM0X:2025 Essai

### Description

Une description suffisamment longue pour que la fiche apprenne quelque chose
au lecteur qui la reçoit, et non un intitulé recopié.

### %s

1. **Premier cas** : ce qui se produit concrètement.
2. **Deuxième cas** : une autre manifestation du même risque.

### Prevention and Mitigation Strategies

#### 1. Contraindre le comportement du modèle
Une parade publiée par la source.

#### 2. Valider le format attendu en sortie
Une seconde parade publiée par la source.
"""


def test_les_quatre_intitules_de_la_meme_section_sont_tous_lus():
    """Les dix entrées n'emploient pas le même titre pour la section des
    manifestations : quatre formulations sur dix entrées. Le motif les couvre
    par FAMILLE, jamais par libellé exact — sinon chaque édition d'OWASP
    rouvre le défaut."""
    for titre in ("Common Examples of Risks", "Common Examples of Risk",
                  "Common Examples of Vulnerability",
                  "Types of Prompt Injection Vulnerabilities"):
        items = I._owasp_puces(_OWASP_MODELE % titre,
                               r"(?:Common Examples? of \w+|Types of .+)")
        assert len(items) == 2, (titre, items)
        assert items[0] == "Premier cas : ce qui se produit concrètement.", items


def test_une_parade_en_sous_titre_numerote_est_lue_comme_une_puce():
    """Les parades sont tantôt des puces, tantôt des sous-titres numérotés.
    Ne lire que les puces revenait à déclarer SANS PARADE les entrées les
    mieux structurées — et une fiche sans parade n'est pas servie."""
    p = I._owasp_puces(_OWASP_MODELE % "Common Examples of Risks",
                       r"Prevention and Mitigation Strategies")
    assert p == ["Contraindre le comportement du modèle",
                 "Valider le format attendu en sortie"], p


def test_une_entree_sans_parade_n_est_pas_servie_vide():
    """On ne sert pas une entrée creuse sous prétexte que la source l'annonce.
    Le document est FOURNI plutôt qu'allé chercher : les dix entrées réelles
    portent toutes leurs parades, si bien qu'un contrôle branché sur le réseau
    passerait au vert sans rien garder."""
    creuse = "## LLM01:2025 Essai\n\n### Description\n\nUne description.\n"
    fichier = I.OWASP_LLM[0][0]
    r = I.collecter_owasp_llm(limite=1, documents={fichier: creuse})
    assert not r["ok"] and r["erreur"] == "aucune_entree"


def test_chaque_fiche_owasp_dit_qu_elle_n_est_pas_un_incident():
    """LA DISTINCTION EST LE TOUT. « C'est arrivé » et « c'est reconnu comme
    un risque » sont deux énoncés différents, qu'un empilement confondrait.
    ATLAS et OWASP se retrouvent dans la même rubrique : sans cette phrase, le
    lecteur lit dix incidents de plus."""
    fichier = I.OWASP_LLM[0][0]
    r = I.collecter_owasp_llm(
        limite=1,
        documents={fichier: _OWASP_MODELE % "Common Examples of Risks"})
    assert r["ok"], r
    f = r["fiches"][0]
    assert "CONSENSUS DE PRATICIENS" in f["lecture"]
    assert "ATLAS" in f["lecture"]
    assert "pas une norme opposable" in f["incertitude"]
    assert "convention" in f["incertitude"]      # la date est une convention


# ── 10. Le pont entre les deux natures de la rubrique ─────────────────────
#
# ATLAS documente ce qui EST ARRIVÉ, OWASP ce qui EST RECONNU comme menaçant.
# Les deux cohabitaient sans se toucher, et les fiches OWASP se retrouvaient
# isolées une fois retiré le faux rapprochement par leur date de convention.
# OWASP publie lui-même la correspondance : ce site la reprend, il ne
# l'invente pas — c'est le seul type de lien qui n'engage pas le cabinet.

_LIENS_OWASP = """## LLM01:2025 Essai

### Description

Une description assez longue pour tenir lieu de chapeau de fiche.

### Prevention and Mitigation Strategies

- Une parade publiée par la source, assez longue pour être retenue.

### Related Frameworks and Taxonomies

- [AML.T0051.000 - LLM Prompt Injection: Direct](https://atlas.mitre.org/x) **MITRE ATLAS**
- [AML.T0051.001 - LLM Prompt Injection: Indirect](https://atlas.mitre.org/y) **MITRE ATLAS**

### References

- [Un article](https://arxiv.org/abs/0000) **arXiv**
- [AML.T0999 - Une technique citée en bibliographie](https://atlas.mitre.org/z) **MITRE ATLAS**
"""


def test_la_correspondance_est_lue_dans_la_section_qu_owasp_lui_consacre():
    """Elle est DÉCLARÉE par la source, pas déduite par ce site. Les
    références du pied de page, elles, ne sont pas des correspondances : les
    confondre servirait un article de recherche comme s'il était une
    technique du référentiel."""
    r = I._owasp_atlas(_LIENS_OWASP)
    assert [x[0] for x in r] == ["AML.T0051.000", "AML.T0051.001"], r
    assert r[0][1] == "LLM Prompt Injection: Direct", r
    # AML.T0999 est cité en BIBLIOGRAPHIE, pas dans la section des cadres
    # apparentés. Lire tout le document confondrait « OWASP renvoie à cette
    # lecture » avec « OWASP affirme la correspondance » — deux énoncés que
    # la source, elle, prend soin de séparer.
    assert "AML.T0999" not in [x[0] for x in r], r


def test_une_sous_technique_n_est_pas_repliee_sur_sa_mere():
    """Rendre « AML.T0051 » là où la source écrit « AML.T0051.000 » dirait
    « injection d'invite » quand elle dit « injection d'invite DIRECTE » —
    c'est-à-dire moins que ce qu'elle affirme."""
    refs = [x[0] for x in I._owasp_atlas(_LIENS_OWASP)]
    assert "AML.T0051" not in refs
    assert len(set(refs)) == 2


def test_une_correspondance_sans_les_deux_bouts_n_est_pas_posee():
    """Même règle que pour ATLAS, et pour la même raison : ce site sert seize
    techniques sur cent quarante et quelques. Un lien vers une fiche absente
    est un lien mort."""
    ow = {"id": "owasp-llm-llm01", "titre": "Le risque",
          "_owasp_atlas": [("AML.T0051.000", "Direct"),
                           ("AML.T9999", "Une technique non servie")]}
    tech = {"id": "atlas-tech-aml-t0051-000", "titre": "La technique"}
    n = I.relier_owasp_atlas([ow, tech])
    assert n == 1
    assert [r["vers"] for r in ow["relations"]] == ["atlas-tech-aml-t0051-000"]
    assert [r["vers"] for r in tech["relations"]] == ["owasp-llm-llm01"]


def test_la_correspondance_dit_qu_elle_vient_de_la_source():
    """C'est ce qui la sépare de toutes les autres règles de ce site : le
    lecteur doit pouvoir remonter à OWASP sans nous croire sur parole."""
    ow = {"id": "owasp-llm-llm01", "titre": "Le risque",
          "_owasp_atlas": [("AML.T0051.000", "LLM Prompt Injection: Direct")]}
    tech = {"id": "atlas-tech-aml-t0051-000", "titre": "La technique"}
    I.relier_owasp_atlas([ow, tech])
    rel = ow["relations"][0]
    assert "OWASP rattache lui-même" in rel["dit"]
    assert "pas de ce site" in rel["dit"]
    assert rel["citations"] and "Related Frameworks" in rel["citations"][0]


def test_le_champ_de_transport_ne_survit_pas_a_la_publication():
    """`_owasp_atlas` sert à porter les références jusqu'au corpus réuni. Il
    n'a rien à faire dans ce que le site sert, et un champ technique qui
    fuit dans l'API finit par être lu comme une donnée."""
    ow = {"id": "owasp-llm-llm01", "titre": "Le risque",
          "_owasp_atlas": [("AML.T0051.000", "Direct")]}
    I.relier_owasp_atlas([ow])
    assert "_owasp_atlas" not in ow


def test_une_technique_est_servie_parce_qu_une_source_la_nomme():
    """LE CRITÈRE AJOUTÉ, ET POURQUOI IL VAUT MIEUX QUE L'ANCIEN. Le
    collecteur retenait les huit techniques « les plus récemment révisées » —
    un proxy qui ne dit rien de ce corpus : sur les onze correspondances
    qu'OWASP déclare, DEUX seulement tombaient sur une fiche servie."""
    corpus = [{"id": "owasp-llm-llm01", "titre": "Le risque",
               "_owasp_atlas": [("AML.T0051.000", "Direct")]}]
    ajoutees, perdues = I.completer_atlas_techniques(corpus)
    if ajoutees == 0 and perdues:
        import pytest
        pytest.skip("ATLAS injoignable")
    assert ajoutees == 1 and perdues == 0
    ajoutee = corpus[-1]
    assert ajoutee["id"] == "atlas-tech-aml-t0051-000"
    assert ajoutee["source"]["cle"] == "mitre_atlas"


def test_rien_n_est_ajoute_pour_une_technique_deja_servie():
    """Sinon la même technique sortirait deux fois dans le fil, et le lecteur
    y lirait deux faits."""
    corpus = [{"id": "owasp-llm-llm01", "titre": "Le risque",
               "_owasp_atlas": [("AML.T0051.000", "Direct")]},
              {"id": "atlas-tech-aml-t0051-000", "titre": "Déjà là"}]
    assert I.completer_atlas_techniques(corpus) == (0, 0)
    assert len(corpus) == 2


def test_une_reference_absente_du_referentiel_est_comptee_pas_ignoree():
    """Le cas ne se produit pas aujourd'hui, mais un identifiant retiré
    d'ATLAS le produirait — et il ne doit pas passer en silence."""
    corpus = [{"id": "owasp-llm-llm01", "titre": "Le risque",
               "_owasp_atlas": [("AML.T9999", "Une technique qui n'existe pas")]}]
    ajoutees, perdues = I.completer_atlas_techniques(corpus)
    assert (ajoutees, perdues) == (0, 1)


def test_le_pont_est_pose_apres_la_completion_jamais_avant():
    """L'ORDRE EST LA RÈGLE, pas un détail d'écriture. Poser les liens avant
    de servir les techniques que la source nomme, c'est les poser sur des
    fiches absentes : ils sont écartés, et le pont ne relie plus rien. C'est
    exactement l'état mesuré avant cette passe — deux correspondances sur
    onze."""
    def _ow():
        return [{"id": "owasp-llm-llm01", "titre": "Le risque",
                 "_owasp_atlas": [("AML.T0051.000", "Direct")]}]

    avant = _ow()
    assert I.relier_owasp_atlas(avant) == 0     # la technique n'est pas servie

    apres = _ow()
    ajoutees, perdues = I.completer_atlas_techniques(apres)
    if ajoutees == 0 and perdues:
        import pytest
        pytest.skip("ATLAS injoignable")
    assert I.relier_owasp_atlas(apres) == 1

    # et la chaîne de collecte les appelle DANS CET ORDRE
    src = open(os.path.join(ICI, "ingestion.py"), encoding="utf-8").read()
    bloc = src[src.index("def collecter_tout"):src.index("def _relier_atlas")]
    assert (bloc.index("completer_atlas_techniques(corpus)")
            < bloc.index("relier_owasp_atlas(corpus)")), \
        "la complétion doit précéder la pose des liens"


def test_le_journal_dit_pourquoi_ces_techniques_ont_ete_servies():
    """Servir une technique parce qu'une source la nomme est un CRITÈRE
    ÉDITORIAL, différent de celui qu'annonce le collecteur (« les plus
    récemment révisées »). Un lecteur du registre doit pouvoir le lire, sinon
    le site sert selon une règle qu'il n'affiche pas."""
    src = open(os.path.join(ICI, "ingestion.py"), encoding="utf-8").read()
    bloc = src[src.index("croisement_owasp_atlas"):][:1200]
    # Le message est écrit en littéraux concaténés sur plusieurs lignes ; on
    # les recolle avant de chercher, sinon le contrôle tomberait au premier
    # reformatage sans que la phrase ait changé.
    plat = re.sub(r'"\s*\n\s*"', "", bloc)
    assert "parce qu'OWASP les nomme" in plat, plat[:300]
    assert "et non parce qu'elles ont été révisées récemment" in plat


_TECHNIQUES = [
    {"id": "AML.T0051", "name": "LLM Prompt Injection", "tactics": ["AML.TA0005"],
     "modified_date": "2025-11-05", "description": "La technique mère, décrite."},
    {"id": "AML.T0051.000", "name": "Direct", "specializes": "AML.T0051",
     "modified_date": "2023-10-25", "description": "Le cas particulier, décrit."},
]
_TACTIQUES = {"AML.TA0005": "Execution"}


def _par_ref():
    return {t["id"]: t for t in _TECHNIQUES}


def test_une_sous_technique_porte_le_nom_de_sa_mere():
    """DÉFAUT CONSTATÉ EN SERVICE, apparu avec les sous-techniques qu'OWASP
    désigne. ATLAS ne nomme qu'un SUFFIXE : « AML.T0051.000 » s'appelle
    « Direct ». Servie telle quelle, elle donnait une fiche intitulée
    « Direct — technique documentée contre l'IA » : un titre qui ne dit rien,
    et surtout pas de quoi il est le cas particulier."""
    f = I._fiche_technique_atlas(_TECHNIQUES[1], _TACTIQUES, "2023-10-25",
                                 _par_ref())
    assert f["titre"].startswith("LLM Prompt Injection : Direct —"), f["titre"]
    assert "AML.T0051.000" in f["titre"]


def test_une_technique_mere_ne_recoit_aucun_prefixe():
    """La règle ne doit pas inventer un parent à qui n'en a pas."""
    f = I._fiche_technique_atlas(_TECHNIQUES[0], _TACTIQUES, "2025-11-05",
                                 _par_ref())
    assert f["titre"].startswith("LLM Prompt Injection —"), f["titre"]


def test_une_sous_technique_herite_la_tactique_de_sa_mere():
    """Le référentiel ne la répète pas sur l'enfant. Sans héritage, la lecture
    disait « rattachée à une tactique du référentiel » — une phrase qui
    remplit la place sans rien apprendre."""
    f = I._fiche_technique_atlas(_TECHNIQUES[1], _TACTIQUES, "2023-10-25",
                                 _par_ref())
    assert "« Execution »" in f["lecture"], f["lecture"][:120]
    assert "une tactique du référentiel" not in f["lecture"]


def test_un_parent_absent_ne_fait_pas_tomber_la_fiche():
    """Un identifiant retiré du référentiel ne doit pas empêcher de servir
    l'enfant : mieux vaut un titre court qu'aucune fiche."""
    f = I._fiche_technique_atlas(_TECHNIQUES[1], _TACTIQUES, "2023-10-25", {})
    assert f["titre"].startswith("Direct —"), f["titre"]


# ── 11. Les facettes décrivent LES FICHES TROUVÉES ────────────────────────
#
# DÉFAUT MESURÉ À L'ÉCRAN, ET C'ÉTAIT LE PIRE GENRE. Les menus étaient calculés
# sur tout le corpus, quels que soient les filtres. Choisir « Systèmes d'IA »
# laissait le menu Pays proposer quatorze pays avec leurs comptes — alors
# qu'AUCUNE des vingt-huit fiches de cette rubrique ne porte de pays. Le
# lecteur cliquait « DE (2) », obtenait un écran vide, et n'avait aucun moyen
# de savoir si le site était cassé ou le corpus pauvre.

def _corpus_facettes():
    """Deux rubriques : l'une porte des pays, l'autre non — exactement la
    forme qui produisait l'impasse."""
    out = []
    for i, p in enumerate(("FR", "DE")):
        out.append(V.normaliser(_fiche(
            id="dc-%s" % p.lower(), sujet="datacenter", pays=[p],
            technologies=["Mix électrique"],
            date_fait="2026-0%d-15" % (i + 1)))["fiche"])
    for i in range(3):
        out.append(V.normaliser(_fiche(
            id="sia-%d" % i, sujet="sia", pays=[],
            date_fait="2025-0%d-15" % (i + 1)))["fiche"])
    return out


def test_un_menu_ne_propose_jamais_une_impasse():
    """LE CONTRÔLE QUI GARDE LA CORRECTION. La rubrique « sia » ne porte aucun
    pays : son menu Pays doit être VIDE, et non offrir ceux d'une autre
    rubrique."""
    c = _corpus_facettes()
    assert len(V.facettes(c)["pays"]) == 2, "sans filtre, les deux pays"
    assert V.facettes(c, sujet="sia")["pays"] == [], \
        "le menu Pays propose des pays absents de la rubrique"
    assert V.facettes(c, sujet="datacenter")["pays"], \
        "le menu Pays s'est vidé là où il y a des pays"


def test_chaque_axe_est_compte_hors_de_son_propre_filtre():
    """SANS CETTE RÈGLE, ON NE PEUT PLUS CHANGER D'AVIS. Choisir la France
    réduirait le menu Pays à la seule France, et il faudrait tout remettre à
    zéro pour regarder l'Allemagne. L'axe voit donc l'effet des AUTRES
    filtres, jamais du sien."""
    c = _corpus_facettes()
    f = V.facettes(c, pays="FR")
    assert {p["cle"] for p in f["pays"]} == {"FR", "DE"}, \
        "le menu Pays s'est réduit à son propre choix"
    # les autres axes, eux, voient bien le filtre pays
    assert {s["cle"] for s in f["sujets"]} == {"datacenter"}, \
        "le menu Sujet propose une rubrique sans fiche française"


def test_le_compte_annonce_est_celui_des_fiches_trouvees():
    """`total_publiable` disait la taille du corpus ; les menus décrivaient
    autre chose que ce que la page affiche, et l'écart ne se voyait pas."""
    c = _corpus_facettes()
    f = V.facettes(c, sujet="sia")
    assert f["total_trouve"] == 3
    assert f["total_publiable"] == 5
    assert f["filtre"] == {"sujet": "sia"}


def test_la_recherche_libre_resserre_aussi_les_menus():
    """Le champ de recherche est un filtre comme les autres : les menus
    doivent décrire ce qu'il laisse."""
    c = _corpus_facettes()
    f = V.facettes(c, q="mix")
    assert f["total_trouve"] <= 2
    assert {s["cle"] for s in f["sujets"]} <= {"datacenter"}


def test_un_pays_porte_son_nom_et_pas_son_code():
    """DÉFAUT CONSTATÉ À L'ÉCRAN. Le menu proposait « BE (2) », « DK (2) » :
    un lecteur qui cherche la France doit savoir qu'elle s'écrit FR, et la
    trouver entre ES et GB dans une liste de sigles."""
    c = _corpus_facettes()
    noms = {p["cle"]: (p["nom"], p["nom_en"]) for p in V.facettes(c)["pays"]}
    assert noms["FR"] == ("France", "France")
    assert noms["DE"] == ("Allemagne", "Germany")


def test_un_pays_hors_registre_reste_proposable():
    """Le masquer ferait disparaître du menu un pays réellement présent : mieux
    vaut un code lisible qu'une fiche introuvable."""
    c = _corpus_facettes() + [V.normaliser(_fiche(
        id="zz-1", sujet="datacenter", pays=["ZZ"]))["fiche"]]
    noms = {p["cle"]: p["nom"] for p in V.facettes(c)["pays"]}
    assert noms.get("ZZ") == "ZZ"


def test_les_pays_suivis_derivent_de_la_table_editoriale():
    """Deux tables auraient divergé au premier pays ajouté, et l'écart se
    serait vu comme une source « injoignable » plutôt que comme une faute de
    recopie. Le nom employé pour l'appariement n'est pas le nom affiché : les
    séparer est ce qui permet de traduire l'un sans casser l'autre."""
    assert I.PAYS_SUIVIS == {c: v["owid"] for c, v in V.PAYS.items()}
    assert V.PAYS["DE"]["fr"] != V.PAYS["DE"]["owid"]


def test_l_api_des_facettes_lit_les_memes_filtres_que_le_fil():
    """Deux listes de paramètres auraient divergé, et les menus se seraient
    mis à décrire autre chose que ce que la page affiche."""
    src = open(os.path.join(ICI, "app.py"), encoding="utf-8").read()
    i = src.index("_FILTRES_FIL = (")
    noms = set(re.findall(r'"(\w+)"', src[i:src.index(")", i)]))
    api = src[src.index("def api_veille"):src.index("def page_abonnement")]
    for n in noms - {"q"}:
        assert 'request.args.get("%s")' % n in api, n
    assert "V.facettes(corpus(), **_filtres_demandes())" in src


# ── Les sources qu'on ne peut pas brancher, et pourquoi ───────────────────

def test_chaque_source_a_brancher_dit_la_NATURE_de_son_obstacle():
    """« Bloqué par la politique réseau de l'environnement » et « licence
    commerciale requise » se lisaient pareil, et ce n'est pas pareil du tout :
    le premier se règle en déployant, le second demande un contrat. Un lecteur
    — ou le cabinet dans six mois — doit trier d'un coup d'œil ce qui est un
    chantier de ce qui est une dépense."""
    for x in SRC.A_BRANCHER:
        assert x.get("nature_obstacle") in SRC.NATURES_OBSTACLE, x.get("cle")
        assert x.get("obstacle"), x.get("cle")


def test_une_source_bloquee_par_une_licence_dit_ce_qu_il_faudrait():
    """Sans cela, « licence requise » est un mur sans porte. Avec, c'est une
    décision chiffrable."""
    payantes = [x for x in SRC.A_BRANCHER
                if x["nature_obstacle"] == "licence"]
    assert payantes, "aucune source à licence déclarée"
    for x in payantes:
        assert x.get("ce_qu_il_faudrait"), x["cle"]


def test_les_depeches_d_agence_sont_declarees_et_non_branchees():
    """DEMANDE DU CABINET, ET RÉPONSE ÉCRITE. AFP et Reuters couvrent les
    quatre thèmes, mais ni l'un ni l'autre ne publie de flux libre : AFP passe
    par un contrat, Reuters a retiré ses flux RSS publics. Ce site cite la
    licence de chaque source SOUS CHAQUE FICHE — publier sans licence
    reviendrait à écrire une mention fausse à l'endroit précis où il promet de
    dire vrai. Elles sont donc au registre des sources à brancher, avec le
    motif, plutôt qu'absentes sans explication."""
    cles = {x["cle"] for x in SRC.A_BRANCHER}
    assert {"afp", "reuters"} <= cles, sorted(cles)
    for cle in ("afp", "reuters"):
        x = next(y for y in SRC.A_BRANCHER if y["cle"] == cle)
        assert x["nature_obstacle"] == "licence"
    # Et surtout : elles ne sont PAS au registre des sources admises, où leur
    # présence autoriserait une fiche à les citer.
    assert "afp" not in SRC.SOURCES and "reuters" not in SRC.SOURCES
