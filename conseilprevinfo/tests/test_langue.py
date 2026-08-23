"""LA BASCULE FR/EN — ce qu'elle traduit, et ce qu'elle a le devoir de dire.

UNE INTERFACE ANGLAISE POSÉE SUR UN CORPUS FRANÇAIS EST UN MENSONGE PAR
OMISSION. Le lecteur qui bascule et voit des paragraphes français en conclut
que le site est cassé — ou pire, il ne les lit pas et croit avoir tout vu.

LA LIGNE DE PARTAGE TIENT AU MOTEUR, pas à un choix de confort :

  · Ce que le CABINET écrit — intitulés, rubriques, réserves, libellés du
    référentiel — est traduit à la main. Chaque phrase anglaise a été ÉCRITE ;
    employer une machine à traduire pour l'interface pendant que le site
    l'interdit à son corpus serait une hypocrisie.
  · Ce que la SOURCE porte — titre, chapeau, noms de technologie — garde sa
    langue. Le réécrire reviendrait à réécrire ce que la source déclare.
  · Ce que les GABARITS dérivent — lecture, portée, incertitude — reste
    français : les traduire demanderait des gabarits anglais, un vrai travail,
    et les passer à la machine produirait du texte de modèle de langage.

Ces contrôles gardent la deuxième et la troisième règle, celles qu'on serait
tenté d'assouplir « juste pour cette page-là ».
"""
import json
import os
import re
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import veille as V  # noqa: E402
import croisement as X  # noqa: E402


def _lire(nom):
    return open(os.path.join(ICI, nom), encoding="utf-8").read()


# ── 1. Le référentiel porte les deux langues ──────────────────────────────

def test_chaque_libelle_du_referentiel_a_son_anglais():
    """Sans cela, une interface anglaise garde des pastilles françaises sur
    chaque fiche — c'est-à-dire à l'endroit le plus lu de la page."""
    for nom, table in (("SUJETS", V.SUJETS), ("STATUTS", V.STATUTS),
                       ("LECTURES", V.LECTURES), ("IMPACTS", V.IMPACTS),
                       ("HORIZONS", V.HORIZONS)):
        for cle, v in table.items():
            assert v.get("nom_en"), "%s[%s] sans nom_en" % (nom, cle)
            assert v["nom_en"] != v["nom"], \
                "%s[%s] : le « nom_en » recopie le français" % (nom, cle)


def test_chaque_type_de_lien_a_son_anglais():
    for cle, v in X.LIENS.items():
        assert v.get("nom_en"), "LIENS[%s] sans nom_en" % cle
        assert v["nom_en"] != v["nom"], cle


def test_les_deux_langues_voyagent_avec_le_lien():
    """La page CHOISIT parmi ce que le moteur déclare ; elle ne traduit pas.
    Traduire côté écran remettrait une seconde source de vérité en face du
    moteur, et c'est toujours l'écran qui gagne aux yeux du lecteur."""
    src = _lire("croisement.py")
    i = src.index('"lien": type_')
    assert "lien_nom_en" in src[i:i + 500]


# ── 2. La réserve est MESURÉE, pas affirmée ───────────────────────────────

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
    return V.normaliser(base)["fiche"]


def test_la_reserve_compte_les_analyses_au_lieu_de_les_supposer():
    """Le nombre affiché à côté de la réserve vient du corpus réel. Une phrase
    écrite une fois pour toutes vieillirait sans que personne ne le voie."""
    pub = _fiche()
    cachee = dict(_fiche(id="essai-c2"), statut="a_verifier")
    lg = V.langues([pub, cachee])
    assert lg["total"] == 1 and lg["analyses"] == 1
    assert "1 analyses" in lg["dit_fr"] or "1 analyse" in lg["dit_fr"]
    assert "1 critical readings" in lg["dit_en"]


def test_la_reserve_dit_pourquoi_elle_ne_traduit_pas():
    """Elle ne se contente pas de constater : elle doit nommer la raison, qui
    est la promesse même du site. « Non traduit » sans motif se lit comme un
    chantier en retard."""
    lg = V.langues([_fiche()])
    assert "machine translation" in lg["dit_en"]
    assert "traduction automatique" in lg["dit_fr"]
    assert "MITRE" in lg["dit_en"] and "MITRE" in lg["dit_fr"]


def test_la_reserve_est_servie_avec_le_referentiel():
    """Elle doit arriver par la même requête que les libellés : une seconde
    requête pourrait échouer seule, et la page afficherait alors une interface
    anglaise SANS sa réserve — exactement l'état qu'on veut interdire."""
    src = _lire("app.py")
    i = src.index("def api_referentiel")
    assert "langues=V.langues(" in src[i:i + 900]


# ── 3. Le dictionnaire ne peut pas mentir ─────────────────────────────────

def _dictionnaire():
    d = _lire("langue.js")
    return set(re.findall(r'^\s*"([a-z][\w.]*)":\s*\[', d, re.M))


def _cles_employees():
    usees = set()
    for f in os.listdir(ICI):
        if not (f.endswith(".html") or f.endswith(".js")):
            continue
        s = _lire(f)
        usees |= set(re.findall(r'data-i18n(?:-ph|-aria)?="([\w.]+)"', s))
        usees |= set(re.findall(r'\btr?\("([a-z][\w.]*\.[\w.]+)"\)', s))
    return usees


def test_aucune_cle_employee_sans_definition():
    """UNE CLÉ INCONNUE SE VOIT À L'ÉCRAN — `t()` rend « ‹cle.absente› »
    plutôt qu'une chaîne vide, parce qu'un blanc passerait pour un choix de
    mise en page. Ce contrôle l'attrape avant le lecteur."""
    manquantes = sorted(_cles_employees() - _dictionnaire())
    assert not manquantes, manquantes


def test_chaque_entree_porte_ses_deux_langues():
    """Une entrée à une seule valeur ferait rendre `undefined` en anglais."""
    d = _lire("langue.js")
    seules = re.findall(r'^\s*"([a-z][\w.]*)":\s*\[\s*"[^"]*"\s*\],', d, re.M)
    assert not seules, seules


def test_aucune_traduction_anglaise_ne_recopie_le_francais():
    """Une entrée dont les deux valeurs sont identiques est presque toujours
    un oubli. Les quelques cas légitimes — un nom propre, un sigle — sont
    nommés ici, pour qu'ajouter le suivant soit un geste conscient."""
    d = _lire("langue.js")
    paires = re.findall(r'^\s*"([a-z][\w.]*)":\s*\[\s*"((?:[^"\\]|\\.)*)"\s*,\s*'
                        r'"((?:[^"\\]|\\.)*)"\s*\]', d, re.M)
    assert len(paires) > 80, "le dictionnaire n'a pas été lu : %d" % len(paires)
    ADMIS = {"or.retour", "or.marque", "f.horizon"}
    identiques = sorted(c for c, fr, en in paires if fr == en and c not in ADMIS)
    assert not identiques, identiques


# ── 4. La barre latérale ne s'écrit pas à la main ─────────────────────────

def test_la_barre_lit_les_sections_dans_la_page():
    """Une liste tenue dans `barre.js` promettrait une rubrique le jour où
    elle serait retirée, et le lecteur cliquerait dans le vide. Elle ne peut
    pas diverger de la page parce qu'elle EST la page — même principe que le
    registre des sources, qui dérive de la table qui collecte."""
    b = _lire("barre.js")
    assert 'querySelectorAll("main h2.rubrique[id]")' in b
    # LE CONTRÔLE LIT LE CODE, PAS LA PROSE. Premier essai : chercher le mot
    # dans le fichier entier — il le trouvait dans un commentaire qui CITE
    # « Le fil — tout le corpus filtré » pour expliquer la règle. Un contrôle
    # qui interdit d'expliquer ce qu'il garde pousse à ne plus l'expliquer.
    code = re.sub(r"/\*.*?\*/", "", b, flags=re.S)
    code = re.sub(r"//[^\n]*", "", code)
    corps = code.split("function sections")[1].split("function rendre")[0]
    for mot in ("Dossiers", "À la une", "Le fil", "Pistes", "registre"):
        assert mot not in corps, "« %s » est écrit en dur dans la barre" % mot


def test_chaque_rubrique_de_l_accueil_est_atteignable():
    """Ce que la barre propose doit exister. Le contrôle lit le HTML : une
    rubrique sans identifiant n'apparaîtrait simplement pas, ce qui est le
    comportement voulu — mais l'accueil, lui, doit toutes les porter."""
    h = _lire("index.html")
    ids = set(re.findall(r'<h2 class="rubrique" id="([\w-]+)"', h))
    assert ids >= {"r-dossiers", "r-une", "r-fil", "r-pistes", "r-sources"}, ids


def test_le_compte_de_la_barre_est_celui_de_la_rubrique():
    """Deux nombres différents pour la même chose sur le même écran valent
    moins qu'aucun nombre : la barre RECOPIE le compteur de la rubrique et le
    suit, plutôt que de le recalculer."""
    b = _lire("barre.js")
    assert 'h.querySelector("span[id]")' in b
    assert "MutationObserver" in b
