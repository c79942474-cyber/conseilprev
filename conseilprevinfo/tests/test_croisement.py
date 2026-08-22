"""LE CROISEMENT — ce qu'un rapprochement n'a pas le droit de faire.

Un module qui rapproche des fiches est le plus dangereux du site : il produit
un ÉNONCÉ NOUVEAU (« ces deux faits vont ensemble ») que ni l'une ni l'autre
des sources ne porte. Ces contrôles gardent les quatre limites qui empêchent
ce module de dériver vers la suggestion :

  1. UN LIEN SANS MOTIF ÉCRIT N'EST PAS UN LIEN. « Articles similaires » ne
     dit pas au lecteur s'il tient une coïncidence de vocabulaire ou une
     dépendance réelle.
  2. LE CROISEMENT N'OUVRE PAS CE QUE LA PORTE FERME. Une fiche non publiable
     ne doit pas ressortir comme « voisine » d'une fiche publiée.
  3. UNE ÉTIQUETTE DE CATÉGORIE NE FONDE PAS UN LIEN. Relier tout à tout
     apprend au lecteur à ne plus lire les motifs.
  4. LA PROXIMITÉ DE DATE N'EST PAS UNE CAUSE. Elle reste le lien le plus
     faible, et ne s'applique qu'à défaut d'autre chose.
"""
import os
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import croisement as X  # noqa: E402
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


# ── 0. Ce que la source déclare prime sur toute règle écrite ici ──────────

def _declarante(**kw):
    """Une fiche portant une relation que la SOURCE affirme."""
    return _fiche(relations=[{
        "vers": "essai-bbb", "titre": "L'autre",
        "nature": "uses", "nature_nom": "emploie",
        "dit": "Sandworm Team emploie Industroyer, selon le référentiel.",
        "citations": ["ESET Industroyer", "Dragos Crashoverride 2017"],
    }], **kw)


def test_une_relation_declaree_par_la_source_est_le_lien_le_plus_fort():
    """C'est le SEUL lien qui n'engage pas le cabinet : tous les autres sont
    des règles que ce fichier écrit, celui-ci cite un objet publié par le
    référentiel. Il doit donc primer sur toutes les autres règles."""
    assert (X.LIENS["declaree_par_la_source"]["force"]
            == min(l["force"] for l in X.LIENS.values()))
    a = _declarante(id="essai-aaa", editeur="Siemens", technologies=["Modbus"])
    b = _fiche(id="essai-bbb", editeur="Siemens", technologies=["Modbus"])
    v = X.liens(a, [a, b])[0]
    assert v["lien"] == "declaree_par_la_source", v
    assert "selon le référentiel" in v["pourquoi"]


def test_la_chaine_de_preuve_voyage_avec_le_lien():
    """Reprendre l'affirmation d'un référentiel sans les références sur
    lesquelles il s'appuie obligerait à nous croire sur parole — exactement ce
    que ce site reproche aux agrégateurs."""
    a = _declarante(id="essai-aaa")
    b = _fiche(id="essai-bbb")
    assert X.liens(a, [a, b])[0]["citations"] == ["ESET Industroyer",
                                                  "Dragos Crashoverride 2017"]


def test_une_relation_vers_une_fiche_non_publiee_ne_cree_pas_de_lien_mort():
    a = _declarante(id="essai-aaa")
    cachee = dict(_fiche(id="essai-bbb"), statut="a_verifier")
    assert X.liens(a, [a, cachee]) == []


def test_les_liens_ordinaires_ne_portent_aucune_citation():
    """Une citation vide vaut mieux qu'une citation empruntée : un lien fondé
    sur une règle de ce fichier ne doit pas paraître adossé à un rapport."""
    a = _fiche(id="essai-aaa", editeur="Siemens")
    b = _fiche(id="essai-bbb", editeur="Siemens")
    assert X.liens(a, [a, b])[0]["citations"] == []


# ── 1. Un lien sans motif écrit n'est pas un lien ─────────────────────────

def test_tout_voisin_rendu_porte_son_motif_en_toutes_lettres():
    a = _fiche(id="essai-aaa", editeur="Siemens")
    b = _fiche(id="essai-bbb", editeur="Siemens")
    for v in X.liens(a, [a, b]):
        assert v["pourquoi"] and len(v["pourquoi"]) > 10, v
        assert v["lien"] in X.LIENS
        assert v["lien_nom"] == X.LIENS[v["lien"]]["nom"]


def test_le_motif_nomme_ce_qui_est_commun_pas_seulement_le_type():
    """« Même éditeur » sans dire lequel oblige le lecteur à comparer les deux
    fiches lui-même — c'est exactement le travail qu'on prétend faire."""
    a = _fiche(id="essai-aaa", editeur="Siemens")
    b = _fiche(id="essai-bbb", editeur="Siemens")
    assert "Siemens" in X.liens(a, [a, b])[0]["pourquoi"]

    c = _fiche(id="essai-ccc", pays=["FR"], date_fait="2020-01-01")
    d = _fiche(id="essai-ddd", pays=["FR"], date_fait="2020-01-01")
    assert "FR" in X.liens(c, [c, d])[0]["pourquoi"]


def test_une_fiche_n_est_jamais_sa_propre_voisine():
    a = _fiche(id="essai-aaa", editeur="Siemens")
    assert all(v["id"] != "essai-aaa" for v in X.liens(a, [a, a]))


def test_sans_rien_de_commun_aucun_lien_n_est_fabrique():
    """Le cas qui compte : le module doit savoir rendre une liste VIDE plutôt
    que de rapprocher deux fiches sans motif."""
    a = _fiche(id="essai-aaa", sujet="cyber_industriel", date_fait="2026-01-15")
    b = _fiche(id="essai-bbb", sujet="datacenter", date_fait="2019-01-15")
    assert X.liens(a, [a, b]) == []


# ── 2. Le croisement n'ouvre pas ce que la porte ferme ────────────────────

def test_une_fiche_non_publiable_ne_ressort_pas_comme_voisine():
    """Même classe de fuite que les filtres : une porte contournée par une
    fonctionnalité annexe reste une porte contournée."""
    a = _fiche(id="essai-aaa", editeur="Siemens")
    cachee = dict(_fiche(id="essai-cac", editeur="Siemens"),
                  statut="redigee_par_ia", lecture_nature="modele")
    assert all(v["id"] != "essai-cac" for v in X.liens(a, [a, cachee]))


def test_les_dossiers_ne_comptent_que_le_publiable():
    a = _fiche(id="essai-aaa", editeur="Siemens")
    b = _fiche(id="essai-bbb", editeur="Siemens")
    cachee = dict(_fiche(id="essai-cac", editeur="Siemens"),
                  statut="a_verifier")
    d = [x for x in X.dossiers([a, b, cachee]) if x["genre"] == "editeur"]
    assert d and d[0]["n"] == 2, d


# ── 3. Une étiquette de catégorie ne fonde pas un lien ────────────────────

def test_une_technologie_trop_generique_ne_relie_rien():
    """DÉFAUT CORRIGÉ : « mode operatoire » est une étiquette posée par le
    collecteur, pas une technologie. La laisser fonder un lien reliait les
    vingt fiches ATT&CK entre elles par un lien vrai et sans intérêt."""
    a = _fiche(id="essai-aaa", technologies=["Mode opératoire"],
               sujet="cyber_industriel", date_fait="2019-01-01")
    b = _fiche(id="essai-bbb", technologies=["Mode opératoire"],
               sujet="ia", date_fait="2026-01-01")
    assert X.liens(a, [a, b]) == []


def test_une_vraie_technologie_commune_relie_bien():
    a = _fiche(id="essai-aaa", technologies=["Modbus"], sujet="cyber_industriel")
    b = _fiche(id="essai-bbb", technologies=["Modbus"], sujet="datacenter")
    v = X.liens(a, [a, b])
    assert v and v[0]["lien"] == "meme_technologie" and "modbus" in v[0]["pourquoi"]


# ── LA RÈGLE CALCULÉE, ET CE QU'ELLE DOIT ÉPARGNER ───────────────────────
# Le défaut d'étiquette de collecteur est revenu QUATRE FOIS. Les trois
# premières ont été réparées en écrivant le mot dans TROP_GENERIQUES, ce qui
# suppose que quelqu'un y pense au branchement de chaque source. Ces contrôles
# gardent la règle qui n'a plus besoin de cette vigilance — et surtout ils
# gardent les DEUX FORMULATIONS FAUSSES qui l'ont précédée, chacune ayant sa
# propre victime.

def _source(cle, techno, combien, autres=0, sujet="cyber_industriel"):
    """`combien` fiches d'une source portent `techno`, `autres` n'en portent
    pas. Les dates sont espacées de deux mois — au-delà de FENETRE_JOURS —
    pour qu'aucun lien de période ne vienne se mêler à ce qui est mesuré ici,
    et restent dans le passé, que le validateur exige."""
    out = []
    for i in range(combien + autres):
        out.append(_fiche(
            id="%s-%02d" % (cle.replace("_", "-"), i), source_cle=cle,
            sujet=sujet,
            date_fait="%04d-%02d-15" % (2012 + i // 6, (i % 6) * 2 + 1),
            source_url="https://exemple.test/%s/%d" % (cle, i),
            technologies=[techno] if i < combien else ["Divers %d" % i]))
    return out


def test_une_etiquette_de_collecteur_est_reperee_sans_liste_noire():
    """« Risque reconnu » sur les dix fiches OWASP sur dix : c'est une
    étiquette de catégorie, et la règle doit le voir SANS que le mot ait été
    écrit à la main nulle part."""
    corpus = _source("owasp_llm", "Risque reconnu", 10)
    assert "risque reconnu" not in X.TROP_GENERIQUES
    assert "risque reconnu" in X._technos_frequentes(corpus)
    assert X.liens(corpus[0], corpus) == []


def test_une_vraie_technologie_survit_a_sa_source_unique():
    """PREMIÈRE FORMULATION FAUSSE, ET SA VICTIME. « Portée par une seule
    source » supprimait aussi les vraies technologies : sur un corpus mono-
    source, deux entrées de vulnérabilité sur Modbus cessaient de se
    rejoindre. Ce qu'un collecteur pose sur une PARTIE de ses fiches est une
    technologie, quel que soit le nombre de sources qui l'emploient."""
    corpus = _source("cisa_kev", "Modbus", 4, autres=8)
    assert "modbus" not in X._technos_frequentes(corpus)
    v = X.liens(corpus[0], corpus)
    assert v and v[0]["lien"] == "meme_technologie"


def test_la_part_du_corpus_ne_dit_pas_ce_qui_cloche():
    """SECONDE FORMULATION FAUSSE, ET SA VICTIME. « Au-delà d'un cinquième du
    corpus » ne rattrapait rien : dix fiches OWASP dans un corpus de
    quatre-vingt-dix pèsent onze pour cent, tout en produisant à elles seules
    les liens fautifs. Ici l'étiquette pèse moins d'un cinquième du corpus —
    sous l'ancien seuil — et doit tomber quand même."""
    corpus = _source("owasp_llm", "Risque reconnu", 10) \
        + _source("cisa_kev", "Modbus", 20, autres=30)
    part = len([f for f in corpus
                if "Risque reconnu" in f["technologies"]]) / len(corpus)
    assert part < 0.20
    assert "risque reconnu" in X._technos_frequentes(corpus)


def test_une_petite_source_ne_perd_pas_ses_technologies():
    """Une part calculée sur deux fiches ne signifie rien : deux sur deux
    font cent pour cent par accident d'échantillon, pas par nature
    d'étiquette. Sous MINI_FICHES_SOURCE, la source n'est pas jugée."""
    corpus = _source("mlcommons", "Modbus", 2)
    assert len(corpus) < X.MINI_FICHES_SOURCE
    assert X._technos_frequentes(corpus) == set()


def test_un_mot_etiquette_ici_et_technologie_ailleurs_est_conserve():
    """La règle exige la quasi-totalité dans CHAQUE source qui emploie le
    mot. Un collecteur qui appose « Modbus » sur tout ce qu'il produit ne
    doit pas faire disparaître le Modbus d'un catalogue de vulnérabilités,
    où il ne concerne qu'une partie des entrées."""
    corpus = _source("mitre_attack_ics", "Modbus", 8) \
        + _source("cisa_kev", "Modbus", 3, autres=9)
    assert "modbus" not in X._technos_frequentes(corpus)


def test_l_editeur_est_lu_dans_le_champ_declare_jamais_devine():
    """DÉFAUT CORRIGÉ : il était deviné en prenant la première technologie non
    générique, ce qui rangeait des libellés de catégorie parmi les
    fournisseurs et produisait des dossiers intitulés d'après mes propres
    étiquettes."""
    sans = _fiche(id="essai-aaa", technologies=["Rockwell Automation"])
    assert X._editeur(sans) is None
    avec = _fiche(id="essai-bbb", editeur="Rockwell Automation")
    assert X._editeur(avec) == "rockwell automation"


def test_le_lien_retire_ne_peut_pas_revenir_sans_sa_correspondance():
    """Il reliait une CVE aux quatorze modes opératoires du référentiel, avec
    le même motif recopié. Le module refuse de démarrer s'il réapparaît."""
    assert "technique_et_faille" not in X.LIENS
    assert X.LIEN_RETIRE["cle"] == "technique_et_faille"
    assert len(X.LIEN_RETIRE["ce_qu_il_faudrait"]) > 40


# ── 4. La proximité de date n'est pas une cause ───────────────────────────

def test_la_date_reste_le_lien_le_plus_faible():
    assert (X.LIENS["meme_periode"]["force"]
            == max(l["force"] for l in X.LIENS.values()))


def test_la_periode_ne_s_applique_qu_a_defaut_d_autre_chose():
    a = _fiche(id="essai-aaa", editeur="Siemens", date_fait="2026-01-15")
    b = _fiche(id="essai-bbb", editeur="Siemens", date_fait="2026-01-20")
    assert X.liens(a, [a, b])[0]["lien"] == "meme_editeur"


def test_la_periode_ne_traverse_pas_les_sujets():
    """Deux faits du même jour sur deux sujets différents n'ont, eux, rien en
    commun qu'un calendrier."""
    a = _fiche(id="essai-aaa", sujet="cyber_industriel", date_fait="2026-01-15")
    b = _fiche(id="essai-bbb", sujet="datacenter", date_fait="2026-01-16")
    assert X.liens(a, [a, b]) == []


def test_hors_fenetre_la_periode_ne_relie_plus():
    a = _fiche(id="essai-aaa", date_fait="2026-01-15")
    proche = _fiche(id="essai-bbb", date_fait="2026-02-10")
    loin = _fiche(id="essai-ccc", date_fait="2025-01-15")
    rendus = [v["id"] for v in X.liens(a, [a, proche, loin])]
    assert "essai-bbb" in rendus and "essai-ccc" not in rendus


# ── UNE DATE FABRIQUÉE NE RAPPROCHE RIEN ─────────────────────────────────
# DÉFAUT CONSTATÉ EN SERVICE. OWASP date son ÉDITION, pas ses entrées ; le
# collecteur leur a posé le 1er janvier, et l'a écrit honnêtement dans
# l'incertitude de chaque fiche. Mais le croisement ne lit pas l'incertitude :
# il a vu dix fiches à la même date et les a rapprochées. Le site reliait donc
# des fiches par une valeur QU'IL AVAIT LUI-MÊME FABRIQUÉE — en affichant
# sous le rapprochement que la date était « la seule chose qu'elles aient en
# commun ». C'était exact, et c'est ce qui rendait le lien indéfendable.

def _convention(**kw):
    return _fiche(date_convention=True,
                  date_convention_dit="La source date son édition, pas ses "
                                      "entrées : ce jour tient lieu de rang "
                                      "de classement.", **kw)


def test_deux_dates_de_convention_ne_se_rapprochent_pas():
    a = _convention(id="essai-aaa", sujet="sia", date_fait="2025-01-01")
    b = _convention(id="essai-bbb", sujet="sia", date_fait="2025-01-01")
    assert X.liens(a, [a, b]) == []


def test_une_seule_des_deux_suffit_a_retirer_le_rapprochement():
    """Rapprocher une date observée d'une date inventée ne vaut pas mieux :
    l'écart mesuré n'a de sens que si les deux bouts en ont un."""
    a = _convention(id="essai-aaa", sujet="sia", date_fait="2025-01-01")
    b = _fiche(id="essai-bbb", sujet="sia", date_fait="2025-01-10")
    assert X.liens(a, [a, b]) == []
    assert X.liens(b, [a, b]) == []


def test_une_date_reelle_rapproche_toujours():
    """La règle retire ce qui est fabriqué, pas la période elle-même."""
    a = _fiche(id="essai-aaa", sujet="sia", date_fait="2026-01-15")
    b = _fiche(id="essai-bbb", sujet="sia", date_fait="2026-01-20")
    v = X.liens(a, [a, b])
    assert v and v[0]["lien"] == "meme_periode"


def test_le_motif_de_periode_nomme_l_ecart_reel():
    """« À moins de 45 jours » était la MÊME PHRASE sur tous les voisinages du
    site — la seule des cinq à ne rien nommer de ce qui est commun. Un motif
    identique partout apprend à ne plus lire les motifs."""
    a = _fiche(id="essai-aaa", sujet="sia", date_fait="2026-01-15")
    proche = _fiche(id="essai-bbb", sujet="sia", date_fait="2026-01-16")
    loin = _fiche(id="essai-ccc", sujet="sia", date_fait="2026-02-10")
    memejour = _fiche(id="essai-ddd", sujet="sia", date_fait="2026-01-15")
    motifs = {v["id"]: v["pourquoi"]
              for v in X.liens(a, [a, proche, loin, memejour])}
    assert motifs["essai-bbb"] == "Même sujet, à un jour d'écart."
    assert motifs["essai-ccc"] == "Même sujet, à 26 jours d'écart."
    assert motifs["essai-ddd"] == "Même sujet, le même jour."
    assert len(set(motifs.values())) == 3, motifs


def test_le_lien_le_plus_fort_sort_en_premier():
    a = _fiche(id="essai-aaa", editeur="Siemens", pays=["FR"],
               technologies=["Modbus"], date_fait="2026-01-15")
    faible = _fiche(id="essai-per", date_fait="2026-01-16")
    moyen = _fiche(id="essai-tec", technologies=["Modbus"], date_fait="2026-08-01")
    fort = _fiche(id="essai-edi", editeur="Siemens", date_fait="2019-01-01")
    rendus = [v["id"] for v in X.liens(a, [a, faible, moyen, fort])]
    assert rendus[0] == "essai-edi", rendus
    assert rendus.index("essai-tec") < rendus.index("essai-per"), rendus


# ── 5. Reproductible, et sans modèle de langage ───────────────────────────

def test_deux_croisements_du_meme_corpus_rendent_le_meme_ordre():
    """C'est la promesse affichée : deux exécutions sur le même corpus rendent
    les mêmes liens, dans le même ordre."""
    a = _fiche(id="essai-aaa", editeur="Siemens", pays=["FR"])
    corpus = [a] + [_fiche(id="essai-%03d" % i, editeur="Siemens", pays=["FR"],
                           date_fait="2026-01-15") for i in range(6)]
    assert X.liens(a, corpus) == X.liens(a, corpus)


def test_aucun_modele_de_langage_dans_le_croisement():
    assert X.sante()["modeles_de_langage"] == 0
    src = open(os.path.join(ICI, "croisement.py"), encoding="utf-8").read()
    for interdit in ("anthropic", "openai", "mistralai", "import requests"):
        assert interdit not in src.lower(), interdit


# ── 6. Les dossiers de vocabulaire disent ce qu'ils valent ────────────────

_FILLER = ["barrage", "raffinerie", "pompage", "convoyeur", "chaudiere",
           "portique", "compresseur", "vanne", "turbine"]


def _corpus_avec(terme, combien):
    """Un corpus où `terme` est MINORITAIRE.

    Le seuil de généricité se calcule sur la taille du corpus : trois fiches
    qui portent toutes le même mot ne forment pas un dossier, et c'est voulu —
    un mot présent partout désigne le sujet, pas une famille. Il faut donc un
    corpus assez large pour que le mot y soit une minorité.
    """
    fs = [_fiche(id="essai-t%02d" % i, titre="Incident %s numero %d" % (terme, i))
          for i in range(combien)]
    fs += [_fiche(id="essai-f%02d" % i, titre="Incident %s" % m)
           for i, m in enumerate(_FILLER)]
    return fs


def test_un_dossier_de_vocabulaire_annonce_qu_il_ne_prouve_rien():
    d = X.dossiers_par_terme(_corpus_avec("unitronics", 3), mini=2)
    assert [x for x in d if x["libelle"] == "unitronics"], d
    assert all("ne prouve" in x["dit"] for x in d), d


def test_un_article_colle_au_mot_ne_forme_pas_un_terme():
    """DÉFAUT CORRIGÉ : « l'ICS » et « d'électricité » formaient les plus gros
    dossiers du site, alors qu'ils ne désignent que l'article français collé
    au mot suivant.

    Le contrôle porte sur `_termes` et non sur les dossiers : c'est là que la
    règle s'applique, et un contrôle posé en aval passerait au vert pour une
    tout autre raison (un seuil de généricité qui écarte le terme de toute
    façon), sans rien garder du tout."""
    t = X._termes({"titre": "Panne de l'ICS et d'automates réseau"})
    assert not any("'" in x or "’" in x for x in t), t
    # le mot qui SUIT l'article est bien gardé : la règle coupe l'article,
    # elle ne jette pas le terme.
    assert "automates" in t, t


def test_un_terme_present_partout_ne_forme_pas_un_dossier():
    """Il ne désigne plus une famille : il désigne le sujet, que les filtres
    rendent déjà."""
    fs = [_fiche(id="essai-a%02d" % i, titre="Rockwell épisode %d" % i)
          for i in range(12)]
    assert not [d for d in X.dossiers_par_terme(fs, mini=2)
                if d["libelle"] == "rockwell"]


def test_une_reference_technique_ne_regroupe_rien():
    """Un identifiant est unique par construction : CVE-2026-0001 ne peut
    désigner une famille de faits."""
    fs = [_fiche(id="essai-a%02d" % i, titre="CVE-2026-0001 chez G0082 %d" % i)
          for i in range(3)]
    libelles = {d["libelle"] for d in X.dossiers_par_terme(fs, mini=2)}
    assert not any(l.startswith("cve") or l.startswith("g00") for l in libelles), \
        libelles


# ── 7. La tension dit ce que le corpus NE couvre pas ──────────────────────

def test_la_tension_nomme_les_sujets_sans_aucune_fiche():
    """Un site qui n'afficherait que ses rubriques bien fournies laisserait
    croire à une couverture homogène."""
    t = X.tension([_fiche(id="essai-aaa", sujet="cyber_industriel")])
    assert "datacenter" in t["sujets_vides"]
    assert V.SUJETS["datacenter"]["nom"] in t["dit"]


def test_la_tension_couvre_tous_les_sujets_declares():
    t = X.tension([])
    assert set(t["par_sujet"]) == set(V.ORDRE_SUJETS)


def test_un_axe_qui_ne_forme_rien_le_dit_au_lieu_de_se_taire():
    """Sur le corpus réel l'axe par fournisseur ne forme AUCUN dossier : 46
    fiches sur 66 n'en déclarent pas et aucun ne revient deux fois. Rendre une
    liste vide sans rien dire laisse croire à une panne, ou à une absence de
    sujet là où c'est la matière des sources qui ne s'y prête pas."""
    seules = [_fiche(id="essai-aaa", editeur="Siemens"),
              _fiche(id="essai-bbb", editeur="Schneider")]
    m = X.mesure_entites(seules)
    assert m["dossiers_formes"] == 0
    assert m["avec_editeur"] == 2 and m["fiches"] == 2
    assert "Aucun regroupement" in m["dit"] and "panne" in m["dit"], m["dit"]


def test_une_proximite_de_date_n_est_pas_rendue_comme_un_lien():
    """DÉFAUT CORRIGÉ, mesuré sur le corpus réel : 312 rapprochements sur 314
    tenaient au seul « même sujet, à moins de 45 jours ». Le site n'ayant que
    quatre sujets, la condition est presque vide — chaque fiche affichait six
    voisines portant le même motif recopié, sous le mot « Lien ».

    C'est la faute pour laquelle « technique et faille » a été retiré, et le
    module se l'appliquait à lui-même."""
    a = _fiche(id="essai-aaa", date_fait="2026-01-15")
    b = _fiche(id="essai-bbb", date_fait="2026-01-20")
    c = X.croiser(a, [a, b])
    assert c["liens"] == [], c["liens"]
    assert [v["id"] for v in c["voisinage"]] == ["essai-bbb"]
    assert "n'établit aucune relation" in c["voisinage_dit"]


def test_un_vrai_lien_reste_du_cote_des_liens():
    a = _fiche(id="essai-aaa", editeur="Siemens", date_fait="2026-01-15")
    b = _fiche(id="essai-bbb", editeur="Siemens", date_fait="2026-01-20")
    c = X.croiser(a, [a, b])
    assert [v["id"] for v in c["liens"]] == ["essai-bbb"]
    assert c["voisinage"] == []


def test_le_voisinage_est_borne_et_dit_combien_il_en_cache():
    """Non borné, il reprend toute la place qu'on vient de lui retirer."""
    a = _fiche(id="essai-aaa", date_fait="2026-01-15")
    corpus = [a] + [_fiche(id="essai-v%02d" % i, date_fait="2026-01-16")
                    for i in range(9)]
    c = X.croiser(a, corpus, maxi_voisinage=3)
    assert len(c["voisinage"]) == 3
    assert c["voisinage_total"] == 9


def test_le_croisement_mesure_de_quoi_il_est_fait():
    """Sans ce compte, la rubrique garde le vocabulaire du croisement de
    sources alors que tous ses rapprochements tiennent à la règle la plus
    faible — et personne ne s'en aperçoit. C'est ainsi que le défaut a vécu."""
    a = _fiche(id="essai-aaa", date_fait="2026-01-15")
    b = _fiche(id="essai-bbb", date_fait="2026-01-20")
    m = X.mesure_liens([a, b])
    assert m["par_type"]["meme_periode"] == 2
    assert m["liens_forts"] == 0
    assert m["fiches_sans_lien_fort"] == 2
    assert "proximité de date" in m["dit"]


def test_quand_l_axe_forme_quelque_chose_il_le_compte():
    fs = [_fiche(id="essai-aaa", editeur="Siemens"),
          _fiche(id="essai-bbb", editeur="Siemens")]
    m = X.mesure_entites(fs)
    assert m["dossiers_formes"] >= 1
    assert "Aucun regroupement" not in m["dit"], m["dit"]
