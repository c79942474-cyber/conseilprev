# -*- coding: utf-8 -*-
"""L'OUTILLAGE DE LA TRADUCTION PAR CONTENU — outils/i18n_sentinel.js
(l'inventaire au navigateur) et outils/i18n_sentinel.py (littéraux, verifier,
couverture, lots, assembler), et le catalogue qu'ils ont produit.

CE QUE CES RÈGLES GARDENT. Le corps de Sentinel se traduit par contenu : la
clé d'une traduction est le texte français normalisé, relevé à l'écran par
sentInventaire (sentinel.i18n.js). Tout l'outillage repose sur trois
identités qu'on ne peut pas supposer :
  · la normalisation Python (sentinel_i18n.normaliser, celle de l'outil) est
    LA MÊME que sentNormaliser en JavaScript, au caractère près — sinon une
    clé relevée ici n'est jamais retrouvée là-bas ;
  · le compte des mots est le même des deux côtés — sinon la couverture
    d'une page se mesure avec deux règles ;
  · l'outil d'inventaire emploie sentInventaire DU MODULE, pas une copie.
Puis chaque commande est exécutée sur de petits catalogues et dossiers
d'essai : ce qu'elle refuse, ce qu'elle calcule, ce qu'elle écrit. Enfin, le
catalogue et les fichiers de travail COMMITÉS sont éprouvés : ce sont les
entrées des traducteurs, et une entrée fausse est un mot qui ne se
traduira jamais.
"""
import functools
import glob
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unicodedata

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RACINE)

import sentinel_i18n  # noqa: E402

NODE = shutil.which("node")
MODULE = os.path.join(_RACINE, "sentinel.i18n.js")
OUTIL_JS = os.path.join(_RACINE, "outils", "i18n_sentinel.js")
OUTIL_PY = os.path.join(_RACINE, "outils", "i18n_sentinel.py")
DOSSIER = os.path.join(_RACINE, "i18n", "sentinel")
CATALOGUE = os.path.join(DOSSIER, "CATALOGUE.json")
A_TRADUIRE = os.path.join(DOSSIER, "a_traduire")


def _charger_outil():
    spec = importlib.util.spec_from_file_location("i18n_sentinel_outil", OUTIL_PY)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


outil = _charger_outil()


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


SRC_OUTIL_JS = _lire("outils/i18n_sentinel.js")
SRC_OUTIL_PY = _lire("outils/i18n_sentinel.py")


def _ids(cas):
    out = []
    for c in cas:
        s = unicodedata.normalize("NFKD", c[0]).encode("ascii", "ignore").decode()
        out.append(re.sub(r"-+", "-", re.sub(r"[^A-Za-z0-9]+", "-", s)).strip("-"))
    return out


NBSP, FINE, ESPACE_FINE, BOM = chr(0xA0), chr(0x202F), chr(0x2009), chr(0xFEFF)
E_COMBINE = "e" + chr(0x0301)


# ══════════════════════════════════════════════════════════════════════════
#  LE HARNAIS NODE — le vrai module, le vrai outil
# ══════════════════════════════════════════════════════════════════════════

_HARNAIS = r"""
'use strict';
const fs = require('fs');
const M = require(process.argv[2]);
const O = require(process.argv[3]);
const prog = JSON.parse(fs.readFileSync(process.argv[4], 'utf8'));
const out = [];
for (const op of prog) {
  try {
    if (op.op === 'normaliser') out.push(op.valeurs.map(M.sentNormaliser));
    else if (op.op === 'mots') out.push(op.valeurs.map(O.compterMots));
    else if (op.op === 'fusion') {
      const cat = O.catalogueVide();
      const n = op.pages.map(([page, inv]) => O.fusionnerInventaire(cat, inv, page));
      const c = op.corps ? O.fusionnerCoquille(cat, op.corps) : 0;
      out.push({ nouvelles: n, coquille: c, cat: cat, stats: O.statistiques(cat) });
    }
    else if (op.op === 'options') out.push(O.lireOptions(op.argv));
    else if (op.op === 'panneau') {
      /* UN FAUX DOM, ET RIEN DE PLUS : un panneau, ses cadres, et une
         fonction d'inventaire qui rend ce que le programme a ecrit.
         L'un des cadres LEVE sur contentDocument : c'est le cas d'une
         autre origine, et il doit etre saute sans bruit. */
      const faux = (c) => (c === 'autre-origine'
        ? { get contentDocument() { throw new Error('cross-origin'); } }
        : { contentDocument: c === null ? null : { body: { __inv: c } } });
      const el = { __inv: op.panneau.inv,
                   querySelectorAll: () => (op.panneau.cadres || []).map(faux) };
      const inventorier = (n) => JSON.parse(JSON.stringify(n.__inv));
      out.push(O.inventaireDuPanneau(el, inventorier, op.cadres));
    }
    else if (op.op === 'fusionner') {
      const cat = op.neuf;
      const bilan = O.fusionner(cat, op.ancien);
      out.push({ bilan: bilan, cat: cat });
    }
    else out.push({ erreur: 'op inconnue ' + op.op });
  } catch (e) { out.push({ erreur: String(e && e.stack || e) }); }
}
process.stdout.write(JSON.stringify(out));
"""


@functools.lru_cache(maxsize=None)
def _node_json(programme):
    if not NODE:
        pytest.skip("node absent")
    with tempfile.TemporaryDirectory() as d:
        h = os.path.join(d, "h.js")
        p = os.path.join(d, "prog.json")
        io.open(h, "w", encoding="utf-8").write(_HARNAIS)
        io.open(p, "w", encoding="utf-8").write(programme)
        r = subprocess.run([NODE, h, MODULE, OUTIL_JS, p], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail("node : %s" % (r.stderr or "")[-2000:])
    return r.stdout


def _node(ops):
    out = json.loads(_node_json(json.dumps(ops, ensure_ascii=False, sort_keys=True)))
    for i, r in enumerate(out):
        assert not (isinstance(r, dict) and "erreur" in r), "op %d : %s" % (i, r["erreur"][:500])
    return out


# ══════════════════════════════════════════════════════════════════════════
#  1. LES IDENTITÉS PYTHON / JAVASCRIPT
# ══════════════════════════════════════════════════════════════════════════

PIEGES = [
    "  46" + NBSP + "juridictions" + FINE + "— 2,5 %  ",
    "2024.1 puis 1,5 et 3",
    E_COMBINE + "t" + E_COMBINE + " 2026",
    BOM + "x" + ESPACE_FINE + "y  ",
    "a\n\t b\r\n c",
    "Art. 5 et art5bis",
    "   ",
    "",
    "1.2.3 version 10,5,7",
    "ISO/IEC 42001:2023 — clause 6.1.2",
    "N°" + NBSP + "12" + NBSP + "bis",
    "tab\tulation ligne para",
    "　idéogramme  math  ogham",
    "      espaces en",
    "100 % · 3,5 × 2 = 7,0",
    "€ 1 234 567,89",
    "de 08h30 à 12h00",
    "l'AI Act (2024/1689)",
    "ﬁ ligature et Ⅳ chiffre romain",
    "Ångström Å et Å",
    "ça va ?",
    "a  b   c    d",
    "-5 et +7 et 3e",
    "1er, 2e, 3ème",
    "sept. 2026 — 24/09/2026",
    "x​y zéro-largeur",  # ​ n'est PAS un blanc : les deux le gardent
    "🇫🇷 France 33",
    "Étape 3 sur 12",
    "Toutes (15)",
    "FORMATION 01",
    "Ștefan și Győr 2",  # lettres latines au-delà de U+00FF : un mot chacune
]


def test_les_trente_chaines_pieges_se_normalisent_pareil_en_Python_et_en_JavaScript():
    """LA CLÉ CALCULÉE PAR L'OUTIL (Python) EST CELLE QUE LE NAVIGATEUR
    CHERCHE (JavaScript) — insécables, fines, marque d'ordre des octets,
    séparateurs de ligne et de paragraphe, NFC, nombres décimaux, ligatures
    (que NFC ne décompose pas) : trente pièges, une seule sortie."""
    assert len(PIEGES) >= 30
    js = _node([{"op": "normaliser", "valeurs": PIEGES}])[0]
    py = [outil.normaliser(s) for s in PIEGES]
    ecarts = [(s, a, b) for s, a, b in zip(PIEGES, py, js) if a != b]
    assert not ecarts, "Python ≠ JavaScript sur %d chaîne(s) : %r" % (len(ecarts), ecarts[:3])
    assert outil.normaliser is sentinel_i18n.normaliser, "l'outil n'emploie pas la normalisation du module serveur"


def test_les_mots_se_comptent_pareil_en_Python_et_en_JavaScript():
    """LA COUVERTURE D'UNE PAGE est mots couverts / mots inventoriés : le
    numérateur vient d'ici, le dénominateur du catalogue écrit par node."""
    cas = PIEGES + ["l'AI Act", "état-de-l'art", "A.#", "×", "GB", "c'est-à-dire"]
    js = _node([{"op": "mots", "valeurs": cas}])[0]
    py = [outil.compter_mots(s) for s in cas]
    assert py == js, "écarts : %r" % [(s, a, b) for s, a, b in zip(cas, py, js) if a != b]
    assert outil.compter_mots("Étape 3 sur 12") == 2


def test_l_outil_d_inventaire_emploie_sentInventaire_du_module_et_ne_le_reimplemente_pas():
    """UNE CLÉ RELEVÉE SOUS UNE RÈGLE ET CHERCHÉE SOUS UNE AUTRE ne se
    retrouve jamais : l'inventaire DOIT être celui du module qui traduit."""
    code = re.sub(r"/\*.*?\*/", "", SRC_OUTIL_JS, flags=re.S)
    #  L'INVENTAIRE D'UN PANNEAU PASSE PAR UNE FONCTION NOMMÉE — pour qu'une
    #  règle puisse la jouer — mais c'est TOUJOURS `sentInventaire` du module
    #  qui tranche : l'outil le lui passe en argument au lieu de l'appeler en
    #  son nom. La règle vérifie donc les deux bouts du fil.
    assert "f(el, sentInventaire, arg.cadres)" in code, (
        "la passe ne donne plus l'inventaire du module à la descente")
    assert "sentInventaire(document.body)" in code
    assert "function sentInventaire" not in code and "sentMarcher" not in code, "l'outil réimplémente le parcours"
    assert "typeof sentInventaire === 'function'" in code, "l'outil n'attend pas que le module soit chargé"


# ══════════════════════════════════════════════════════════════════════════
#  2. LA FUSION DES INVENTAIRES (node) — pages, coquille, mots
# ══════════════════════════════════════════════════════════════════════════

INV_A = {"bloc": {"Bonjour le monde !": {"fr": "Bonjour le monde !", "html": "Bonjour <b>le monde</b> !", "pages": ["a"]}},
         "texte": {"Toutes (#)": "Toutes (15)", "Voir le": "Voir le"}, "attr": {"Fermer": "Fermer"}}
INV_B = {"bloc": {}, "texte": {"Voir le": "Voir le", "Deux mots": "Deux mots"}, "attr": {}}
CORPS = {"bloc": {}, "texte": {"Voir le": "Voir le", "Menu principal": "Menu principal"}, "attr": {"Fermer": "Fermer"}}


def test_la_fusion_etiquette_chaque_cle_de_ses_pages_et_compte_ses_mots():
    r = _node([{"op": "fusion", "pages": [["a", INV_A], ["b", INV_B]], "corps": CORPS}])[0]
    cat = r["cat"]
    assert r["nouvelles"] == [4, 1], r["nouvelles"]
    assert cat["texte"]["Voir le"] == {"fr": "Voir le", "pages": ["a", "b"], "mots": 2}, cat["texte"]["Voir le"]
    assert cat["texte"]["Toutes (#)"] == {"fr": "Toutes (15)", "pages": ["a"], "mots": 1}
    assert cat["bloc"]["Bonjour le monde !"] == {"fr": "Bonjour le monde !", "html": "Bonjour <b>le monde</b> !", "pages": ["a"], "mots": 3}
    assert cat["attr"]["Fermer"]["pages"] == ["a"]


def test_ce_qui_est_dans_le_document_mais_dans_aucune_page_est_la_coquille():
    """LE MENU, LA BARRE, LES FENÊTRES ne sont dans aucun `.page` : la
    passe finale sur le document les relève, à la page « _coquille » —
    sans dupliquer ce que les pages ont déjà relevé."""
    r = _node([{"op": "fusion", "pages": [["a", INV_A], ["b", INV_B]], "corps": CORPS}])[0]
    assert r["coquille"] == 1
    assert r["cat"]["texte"]["Menu principal"]["pages"] == ["_coquille"]
    assert r["cat"]["texte"]["Voir le"]["pages"] == ["a", "b"], "une clé de page a été réétiquetée coquille"
    assert r["cat"]["attr"]["Fermer"]["pages"] == ["a"]


def test_les_statistiques_comptent_entrees_et_mots_par_regime_et_par_page():
    r = _node([{"op": "fusion", "pages": [["a", INV_A], ["b", INV_B]], "corps": CORPS}])[0]
    st = r["stats"]
    assert st["regimes"] == {"bloc": {"entrees": 1, "mots": 3}, "texte": {"entrees": 4, "mots": 7}, "attr": {"entrees": 1, "mots": 1}}, st["regimes"]
    assert st["pages"]["a"] == {"entrees": 4, "mots": 7}, st["pages"]
    assert st["pages"]["b"] == {"entrees": 2, "mots": 4}
    assert st["pages"]["_coquille"] == {"entrees": 1, "mots": 2}


def test_la_ligne_de_commande_de_l_outil_node_lit_base_token_port_sortie_attente_et_pages():
    r = _node([{"op": "options", "argv": ["extraire", "--base", "http://x:1/", "--token", "t", "--port", "9905",
                                           "--attente", "250", "--pages", "a,b"]}])[0]
    assert r["commande"] == "extraire" and r["base"] == "http://x:1" and r["token"] == "t"
    assert r["port"] == 9905 and r["attente"] == 250 and r["pages"] == ["a", "b"]
    assert r["sortie"].endswith(os.path.join("i18n", "sentinel", "CATALOGUE.json"))


def test_l_outil_node_lance_le_serveur_sur_un_port_libre_et_n_arrete_que_le_sien():
    """PLUSIEURS RECETTES TOURNENT PARFOIS CÔTE À CÔTE : un serveur qui n'a
    pas pu se lier laisserait l'outil inventorier CELUI D'UN AUTRE dossier.
    Le port est pris libre entre 9900 et 9960, le processus lancé est
    vérifié par son environnement, et seul lui est arrêté."""
    code = re.sub(r"/\*.*?\*/", "", SRC_OUTIL_JS, flags=re.S)
    assert "for (let p = 9900; p <= 9960; p++)" in code
    assert "'PORT=' + port" in code, "l'appartenance du serveur n'est plus vérifiée par son environnement"
    assert "enfant.exitCode !== null || !porteLePort(enfant.pid, port)" in code
    assert "if (!porteLePort(serveur.pid, serveur.port))" in code, "l'arrêt ne vérifie plus le PID"
    assert "requestAnimationFrame(() => requestAnimationFrame(() => setTimeout(r, 300)))" in code, "l'attente du rendu différé a changé"


# ══════════════════════════════════════════════════════════════════════════
#  3. VERIFIER — chaque défaut est refusé, et nommé
# ══════════════════════════════════════════════════════════════════════════

CAT = {
    "genere_le": "x", "pages": 2, "rubriques": {"a": "PILOTAGE", "b": "PILOTAGE", "c": "BUSINESS"},
    "bloc": {"Bonjour le monde !": {"fr": "Bonjour le monde !", "html": "Bonjour <b>le monde</b> !", "pages": ["a"], "mots": 3},
             "Voir NIS # et DORA": {"fr": "Voir NIS 2 et DORA", "html": "Voir <i>NIS 2</i> et DORA", "pages": ["b"], "mots": 4}},
    "texte": {"Toutes (#)": {"fr": "Toutes (15)", "pages": ["a", "_js"], "mots": 1},
              "Un expert CONSEILPREV vous accompagne": {"fr": "Un expert CONSEILPREV vous accompagne", "pages": ["b"], "mots": 5},
              "GB": {"fr": "GB", "pages": ["c"], "mots": 1},
              "Étape # sur #": {"fr": "Étape 3 sur 12", "pages": ["c", "b"], "mots": 2},
              "Programme détaillé": {"fr": "Programme détaillé", "pages": ["_js"], "mots": 2}},
    "attr": {"Fermer la fenêtre": {"fr": "Fermer la fenêtre", "pages": ["_coquille"], "mots": 3}},
}

CAS_REFUS = [
    ("balise hors liste", "bloc", "Bonjour le monde !", "Hello <div>world</div>!", "hors liste blanche"),
    ("balise avec attribut", "bloc", "Bonjour le monde !", 'Hello <b class="x">world</b>!', "avec attribut"),
    ("dièse manquant", "texte", "Toutes (#)", "All", "« # »"),
    ("dièse en trop", "texte", "Étape # sur #", "Step # of # (#)", "« # »"),
    ("nom propre traduit", "bloc", "Voir NIS # et DORA", "See <i>SRI #</i> and DORA", "NIS 2"),
    ("nom propre en minuscules perdu", "texte", "Un expert CONSEILPREV vous accompagne", "An expert supports you", "CONSEILPREV"),
    ("clé périmée", "texte", "Cette clé n'existe plus", "This key is gone", "périmée"),
    ("valeur vide", "texte", "Toutes (#)", "  ", "vide"),
    ("identique au français", "texte", "Programme détaillé", "Programme détaillé", "identique"),
    ("clé non normalisée", "texte", "Toutes (15)", "All (15)", "non normalisée"),
]


@pytest.mark.parametrize("nom,regime,cle,en,motif", CAS_REFUS, ids=_ids(CAS_REFUS))
def test_verifier_refuse_chaque_defaut_et_le_nomme(nom, regime, cle, en, motif):
    """UNE BALISE HORS LISTE ou UN ATTRIBUT dans un bloc anglais serait écrit
    par innerHTML — la seule chose que le régime interdit. UN « # » de trop
    ou de moins : sentDigits refuse d'afficher, le français reste sans que
    personne ne le voie. UN NOM PROPRE traduit est une norme qui n'existe
    pas. UNE CLÉ PÉRIMÉE ne sera jamais cherchée. Chaque défaut est nommé
    pour que le traducteur le corrige, pas seulement compté."""
    motifs = outil.verifier_entree(regime, cle, en, CAT)
    assert motifs, "%s : accepté (%r → %r)" % (nom, cle, en)
    assert any(motif in m for m in motifs), "%s : motifs %r ne nomment pas « %s »" % (nom, motifs, motif)


CAS_ADMIS = [
    ("bloc conforme", "bloc", "Bonjour le monde !", "Hello <b>world</b>!"),
    ("noms propres gardés", "bloc", "Voir NIS # et DORA", "See <i>NIS #</i> and DORA"),
    ("attribut cherché dans texte", "texte", "Fermer la fenêtre", "Close the window"),
    ("sigle identique", "texte", "GB", "GB"),
    ("entité HTML n'est pas un dièse", "texte", "Toutes (#)", "All&#39; (#)"),
]


@pytest.mark.parametrize("nom,regime,cle,en", CAS_ADMIS, ids=_ids(CAS_ADMIS))
def test_verifier_admet_une_entree_conforme(nom, regime, cle, en):
    assert outil.verifier_entree(regime, cle, en, CAT) == [], outil.verifier_entree(regime, cle, en, CAT)


def _ecrire(d, nom, contenu):
    p = os.path.join(d, nom)
    io.open(p, "w", encoding="utf-8").write(json.dumps(contenu, ensure_ascii=False))
    return p


@pytest.fixture
def dossier(tmp_path):
    d = str(tmp_path / "i18n")
    os.mkdir(d)
    _ecrire(d, "CATALOGUE.json", CAT)
    return d


def test_verifier_nomme_un_conflit_entre_deux_fichiers_et_pas_une_valeur_identique(dossier, capsys):
    a = _ecrire(dossier, "a.json", {"texte": {"Toutes (#)": "All (#)", "GB": "GB"}})
    b = _ecrire(dossier, "b.json", {"texte": {"Toutes (#)": "Every (#)", "GB": "GB"}})
    fautes = outil.verifier_fichiers([a, b], CAT)
    assert [(f[0], f[1], f[2]) for f in fautes] == [("b.json", "texte", "Toutes (#)")], fautes
    assert "conflit avec a.json" in fautes[0][3]
    code = outil.main(["verifier", "--catalogue", os.path.join(dossier, "CATALOGUE.json"), "--dossier", dossier])
    sortie = capsys.readouterr().out
    assert code == 1 and "conflit" in sortie and "b.json" in sortie, sortie


def test_verifier_rend_zero_sur_un_dossier_sain_et_ignore_le_catalogue(dossier, capsys):
    _ecrire(dossier, "a.json", {"_lot": "a", "texte": {"Toutes (#)": "All (#)"}, "bloc": {"Bonjour le monde !": "Hello <b>world</b>!"}})
    code = outil.main(["verifier", "--catalogue", os.path.join(dossier, "CATALOGUE.json"), "--dossier", dossier])
    sortie = capsys.readouterr().out
    assert code == 0 and "1 fichier(s), 0 faute(s)" in sortie, sortie


# ══════════════════════════════════════════════════════════════════════════
#  4. COUVERTURE — mots couverts / mots inventoriés
# ══════════════════════════════════════════════════════════════════════════

DICO = {"texte": {"Toutes (#)": "All (#)", "Fermer la fenêtre": "Close the window", "GB": ""},
        "bloc": {"Bonjour le monde !": "Hello <b>world</b>!"}}


def test_couverture_calcule_juste_par_page_et_en_global():
    """Page a : bloc 3 + texte 1 = 4 mots, tout couvert. Page b : 4 + 5 + 2
    = 11 mots, rien. Page c : GB (vide → non couvert) + Étape = 3 mots, rien.
    _coquille : 3 mots couverts. _js : 1 + 2 = 3 mots, 1 couvert. Global :
    chaque entrée UNE fois : 3+4+1+5+1+2+2+3 = 21 mots, 7 couverts."""
    r = outil.couverture(CAT, DICO)
    p = r["pages"]
    assert (p["a"]["mots"], p["a"]["couverts"], p["a"]["pct"]) == (4, 4, 100.0), p["a"]
    assert (p["b"]["mots"], p["b"]["couverts"], p["b"]["pct"]) == (11, 0, 0.0), p["b"]
    assert (p["c"]["mots"], p["c"]["couverts"]) == (3, 0), "une valeur VIDE compte comme couverte"
    assert (p["_coquille"]["mots"], p["_coquille"]["couverts"]) == (3, 3)
    assert (p["_js"]["mots"], p["_js"]["couverts"]) == (3, 1)
    g = r["global"]
    assert (g["mots"], g["couverts"], g["entrees"], g["traduites"]) == (21, 7, 8, 3), g
    assert g["pct"] == 33.3


def test_couverture_classe_les_manquantes_par_mots_decroissants():
    r = outil.couverture(CAT, DICO)
    m = r["pages"]["b"]["manquantes"]
    assert [e["mots"] for e in m] == [5, 4, 2], m
    assert m[0]["cle"] == "Un expert CONSEILPREV vous accompagne" and m[1]["regime"] == "bloc"


def test_couverture_en_ligne_de_commande_ecrit_le_JSON_et_tombe_sous_le_seuil(dossier, tmp_path, capsys):
    _ecrire(dossier, "a.json", DICO)
    j = str(tmp_path / "couv.json")
    code = outil.main(["couverture", "--catalogue", os.path.join(dossier, "CATALOGUE.json"),
                       "--dossier", dossier, "--json", j, "--seuil", "50", "--manquantes", "2"])
    sortie = capsys.readouterr().out
    assert code == 1 and "SOUS LE SEUIL" in sortie, sortie
    assert re.search(r"GLOBAL\s+21\s+7\s+33\.3%", sortie), sortie
    assert json.load(io.open(j, encoding="utf-8"))["global"]["couverts"] == 7
    code = outil.main(["couverture", "--catalogue", os.path.join(dossier, "CATALOGUE.json"),
                       "--dossier", dossier, "--seuil", "30"])
    assert code == 0


# ══════════════════════════════════════════════════════════════════════════
#  5. LOTS — équilibrés, par rubrique, sans doublon, tout couvert
# ══════════════════════════════════════════════════════════════════════════

def _gros_catalogue(n_pages=6, par_page=40):
    cat = {"rubriques": {}, "bloc": {}, "texte": {}, "attr": {}}
    for p in range(n_pages):
        page = "p%d" % p
        cat["rubriques"][page] = "RUBRIQUE %d" % (p % 2)
        for k in range(par_page):
            mots = 1 + (k * 7) % 13
            fr = " ".join("mot%d" % i for i in range(mots))
            cle = "page %s entrée %d : %s" % (page, k, fr)
            regime = ("bloc", "texte", "attr")[k % 3]
            ent = {"fr": cle, "pages": [page], "mots": outil.compter_mots(cle)}
            if regime == "bloc":
                ent["html"] = cle.replace("mot0", "<b>mot0</b>")
            cat[regime][cle] = ent
    cat["texte"]["Menu"] = {"fr": "Menu", "pages": ["_coquille"], "mots": 1}
    #  LA MÊME CLÉ EN TEXTE ET EN ATTRIBUT (un libellé qui est aussi un title) :
    #  une seule case pour la route, qui cherche les deux dans « texte ».
    cat["attr"]["Menu"] = {"fr": "Menu", "pages": ["p0"], "mots": 1}
    cat["texte"]["Rendu par le script"] = {"fr": "Rendu par le script", "pages": ["_js"], "mots": 4}
    return cat


def test_lots_couvrent_tout_le_catalogue_sans_doublon_et_par_rubrique():
    cat = _gros_catalogue()
    lots = outil.decouper_lots(cat, taille=300)
    vues = []
    for lot in lots:
        for cle in list(lot["texte"]) + list(lot["bloc"]):
            vues.append((("bloc" if cle in lot["bloc"] else "texte"), cle))
        assert set(lot["rubriques"]) <= {"RUBRIQUE 0", "RUBRIQUE 1", "_coquille", "_js"}, lot["rubriques"]
        for page in lot["pages"]:
            assert outil.rubrique_de(page, cat["rubriques"]) in lot["rubriques"], (lot["nom"], page)
    attendues = set([("bloc", k) for k in cat["bloc"]] + [("texte", k) for k in cat["texte"]] + [("texte", k) for k in cat["attr"]])
    assert len(vues) == len(set(vues)), "doublons : %s" % [v for v in vues if vues.count(v) > 1][:3]
    assert set(vues) == attendues, "écart : %s" % sorted(attendues ^ set(vues))[:5]


def test_lots_sont_equilibres_autour_de_la_taille_demandee():
    """UNE RUBRIQUE DE 1 000 MOTS coupée en 300 fait 4 parts de ~250, pas
    3 pleines et un fond de tiroir de 100 : les traducteurs reçoivent des
    lots comparables."""
    cat = _gros_catalogue()
    lots = outil.decouper_lots(cat, taille=300)
    for rub in ("RUBRIQUE 0", "RUBRIQUE 1"):
        parts = [l for l in lots if l["rubrique"] == rub]
        total = sum(l["mots"] for l in parts)
        assert len(parts) == -(-total // 300), (rub, total, len(parts))
        attendu = total / float(len(parts))
        for l in parts:
            assert abs(l["mots"] - attendu) <= 15, "%s : %d mots pour une cible de %.0f" % (l["nom"], l["mots"], attendu)
    assert [l["nom"] for l in lots if l["rubrique"] == "_coquille"] and [l["nom"] for l in lots if l["rubrique"] == "_js"]
    noms = [l["nom"] for l in lots]
    assert noms == sorted(noms) and noms[0].startswith("01-") and len(set(noms)) == len(noms), noms


def _catalogue_de_rubriques(poids):
    """Une page par rubrique ; `mots` mots par page, en entrées de DIX mots
    (« entrée », « p », huit « mot » : les chiffres ne comptent pas)."""
    cat = {"rubriques": {}, "bloc": {}, "texte": {}, "attr": {}}
    for i, (rub, mots) in enumerate(poids):
        page = "p%02d" % i
        cat["rubriques"][page] = rub
        for k in range(mots // 10):
            fr = "entrée %s %d " % (page, k) + " ".join(["mot"] * 8)
            cat["texte"][fr] = {"fr": fr, "pages": [page], "mots": outil.compter_mots(fr)}
    return cat


def test_lots_regroupent_les_petites_rubriques_entieres_sans_depasser_la_taille():
    """UNE RUBRIQUE DE 80 MOTS NE FAIT PAS UN FICHIER À ELLE SEULE : les
    rubriques plus légères qu'un lot sont regroupées entières, dans l'ordre
    du menu, jusqu'à la taille d'un lot ; une lourde est coupée seule ; la
    coquille et le JavaScript ne se regroupent avec rien."""
    cat = _catalogue_de_rubriques([("A AUDIT", 100), ("B COMPTE", 100), ("C DORA", 600), ("D EMPREINTE", 400),
                                   ("E GROSSE", 2400), ("F NIS", 500), ("G RECYF", 900)])
    cat["texte"]["Menu principal du site"] = {"fr": "Menu principal du site", "pages": ["_coquille"], "mots": 4}
    lots = outil.decouper_lots(cat, taille=1000)
    compo = [(l["rubriques"], l["mots"]) for l in lots]
    #  D (400) ATTEND F (500) PAR-DESSUS E, LOURDE, COUPÉE SEULE ; G (900) ne
    #  tient plus avec eux (1 800 > 1 100) : il reste seul.
    assert [c[0] for c in compo] == [["A AUDIT", "B COMPTE", "C DORA"], ["D EMPREINTE", "F NIS"], ["E GROSSE"],
                                     ["E GROSSE"], ["E GROSSE"], ["G RECYF"], ["_coquille"]], compo
    assert [c[1] for c in compo][:2] == [800, 900], compo
    for l in lots:
        if l["parts"] == 1 and len(l["rubriques"]) > 1:
            assert l["mots"] <= 1100, "regroupement de %d mots pour une taille de 1000" % l["mots"]
    assert lots[0]["nom"] == "01-a-audit-b-compte-c-dora" and lots[0]["rubrique"] == "A AUDIT + B COMPTE + C DORA", lots[0]["nom"]
    assert [l["nom"] for l in lots][1:5] == ["02-d-empreinte-f-nis", "03-e-grosse-1", "04-e-grosse-2", "05-e-grosse-3"]


def test_un_fichier_de_lot_porte_le_format_des_traducteurs():
    cat = _gros_catalogue(n_pages=1, par_page=3)
    lot = [l for l in outil.decouper_lots(cat, taille=1000) if l["rubrique"] == "RUBRIQUE 0"][0]
    f = outil.fichier_de_lot(lot)
    assert set(f) == {"_lot", "_rubrique", "_pages", "_mots", "texte", "bloc"}, sorted(f)
    b = list(f["bloc"].values())[0]
    assert set(b) == {"fr", "html", "en"} and b["en"] == "" and "<b>" in b["html"], b
    t = list(f["texte"].values())[0]
    assert set(t) == {"fr", "en"} and t["en"] == "", t
    assert len(f["texte"]) == 2 and len(f["bloc"]) == 1, "l'attribut n'est pas rangé dans texte"


def test_lots_ne_recouvrent_pas_un_fichier_de_travail_deja_rempli_sans_forcer(dossier, tmp_path, capsys):
    cat = _gros_catalogue(n_pages=1, par_page=3)
    c = _ecrire(dossier, "CATALOGUE.json", cat)
    d = str(tmp_path / "a_traduire")
    assert outil.main(["lots", "--catalogue", c, "--dossier", d, "--taille", "1000"]) == 0
    fichiers = sorted(os.listdir(d))
    assert fichiers == ["01-rubrique-0.json", "02-coquille.json", "03-js.json"], fichiers
    p = os.path.join(d, fichiers[0])
    lot = json.load(io.open(p, encoding="utf-8"))
    cle = list(lot["texte"])[0]
    lot["texte"][cle]["en"] = "Translated"
    io.open(p, "w", encoding="utf-8").write(json.dumps(lot, ensure_ascii=False))
    outil.main(["lots", "--catalogue", c, "--dossier", d, "--taille", "1000"])
    assert json.load(io.open(p, encoding="utf-8"))["texte"][cle]["en"] == "Translated", "le travail rempli a été écrasé"
    assert "gardé" in capsys.readouterr().out
    outil.main(["lots", "--catalogue", c, "--dossier", d, "--taille", "1000", "--forcer"])
    assert json.load(io.open(p, encoding="utf-8"))["texte"][cle]["en"] == ""


def test_lots_retirent_un_fichier_de_travail_perime_vide_et_gardent_un_rempli(dossier, tmp_path, capsys):
    """LA DÉCOUPE CHANGE QUAND LE CATALOGUE CHANGE : un ancien fichier vide
    laissé là doublerait des clés d'un autre lot ; un ancien fichier REMPLI
    est du travail de traducteur, gardé."""
    c = _ecrire(dossier, "CATALOGUE.json", _gros_catalogue(n_pages=1, par_page=3))
    d = str(tmp_path / "a_traduire")
    os.mkdir(d)
    _ecrire(d, "07-ancienne-decoupe.json", {"_lot": "07-ancienne-decoupe", "texte": {"Menu": {"fr": "Menu", "en": ""}}, "bloc": {}})
    _ecrire(d, "08-deja-traduit.json", {"_lot": "08-deja-traduit", "texte": {"Menu": {"fr": "Menu", "en": "Menu bar"}}, "bloc": {}})
    assert outil.main(["lots", "--catalogue", c, "--dossier", d, "--taille", "1000"]) == 0
    fichiers = sorted(os.listdir(d))
    assert "07-ancienne-decoupe.json" not in fichiers, fichiers
    assert "08-deja-traduit.json" in fichiers, "du travail rempli a été effacé"
    assert "1 périmé(s) retiré(s)" in capsys.readouterr().out


def test_lots_restants_laissent_de_cote_ce_qui_est_deja_traduit():
    cat = _gros_catalogue(n_pages=1, par_page=6)
    cle_t = [k for k in cat["texte"] if k.startswith("page p0")][0]
    cle_b = list(cat["bloc"])[0]
    lots = outil.decouper_lots(cat, taille=1000, dico={"texte": {cle_t: "done"}, "bloc": {cle_b: "done", "autre": ""}})
    cles = [k for l in lots for k in list(l["texte"]) + list(l["bloc"])]
    assert cle_t not in cles and cle_b not in cles
    assert len(cles) == 6 + 2 - 2, len(cles)


# ══════════════════════════════════════════════════════════════════════════
#  6. ASSEMBLER — du travail rempli au format de la route
# ══════════════════════════════════════════════════════════════════════════

TRAVAIL = {"_lot": "01-pilotage", "_rubrique": "PILOTAGE", "_pages": ["a"], "_mots": 9,
           "texte": {"Toutes (#)": {"fr": "Toutes (15)", "en": "All (#)"},
                     "Fermer la fenêtre": {"fr": "Fermer la fenêtre", "en": ""},
                     "Programme détaillé": {"fr": "Programme détaillé", "en": "Programme détaillé"}},
           "bloc": {"Bonjour le monde !": {"fr": "Bonjour le monde !", "html": "Bonjour <b>le monde</b> !", "en": "Hello <b>world</b>!"},
                    "Voir NIS # et DORA": {"fr": "Voir NIS 2 et DORA", "html": "Voir <i>NIS 2</i> et DORA", "en": 'See <a href="x">NIS #</a> and DORA'}}}


def test_assembler_produit_le_format_de_la_route_sans_les_entrees_vides_ni_refusees(dossier, tmp_path, capsys):
    d = str(tmp_path / "a_traduire")
    os.mkdir(d)
    _ecrire(d, "01-pilotage.json", TRAVAIL)
    code = outil.main(["assembler", "--catalogue", os.path.join(dossier, "CATALOGUE.json"), "--dossier", d, "--sortie", dossier])
    sortie = capsys.readouterr().out
    assert code == 1, sortie
    produit = json.load(io.open(os.path.join(dossier, "01-pilotage.json"), encoding="utf-8"))
    assert produit == {"_lot": "01-pilotage", "texte": {"Toutes (#)": "All (#)"},
                       "bloc": {"Bonjour le monde !": "Hello <b>world</b>!"}}, produit
    assert "identique" in sortie and "hors liste blanche" in sortie and "2 entrée(s) refusée(s)" in sortie, sortie
    #  ET LA ROUTE LE SERT TEL QUEL : le format est celui de fusionner().
    dico, fautes = sentinel_i18n.fusionner(dossier)
    assert not fautes and dico["texte"]["Toutes (#)"] == "All (#)" and dico["bloc"]["Bonjour le monde !"] == "Hello <b>world</b>!"


def test_assembler_refuse_un_conflit_avec_un_dictionnaire_deja_en_place(dossier, tmp_path):
    _ecrire(dossier, "00-avant.json", {"texte": {"Toutes (#)": "Every (#)"}})
    d = str(tmp_path / "a_traduire")
    os.mkdir(d)
    _ecrire(d, "01-pilotage.json", TRAVAIL)
    code = outil.main(["assembler", "--catalogue", os.path.join(dossier, "CATALOGUE.json"), "--dossier", d, "--sortie", dossier])
    assert code == 1
    produit = json.load(io.open(os.path.join(dossier, "01-pilotage.json"), encoding="utf-8"))
    assert "Toutes (#)" not in produit["texte"], produit
    #  UN LOT RÉASSEMBLÉ N'EST PAS EN CONFLIT AVEC SA PROPRE VERSION PRÉCÉDENTE.
    os.remove(os.path.join(dossier, "00-avant.json"))
    outil.main(["assembler", "--catalogue", os.path.join(dossier, "CATALOGUE.json"), "--dossier", d, "--sortie", dossier])
    assert "Toutes (#)" in json.load(io.open(os.path.join(dossier, "01-pilotage.json"), encoding="utf-8"))["texte"]


# ══════════════════════════════════════════════════════════════════════════
#  7. LITTERAUX — ce que sentinel.page.js porte en dur
# ══════════════════════════════════════════════════════════════════════════

JS = r"""
/* commentaire : « ce texte n'est pas rendu » */
// ni celui-ci : 'une chaîne dans un commentaire, pas rendue non plus'
var a = 'Aucune activité récente pour ce compte';
var b = "Il n’y a rien à afficher";
var c = 'Programme d\'accompagnement';
var d = `Total : ${n} systèmes enregistrés sur ${m}`;
var e = x.replace(/'de la'/g, '');
var f = '<p>Texte <b>gras</b> et suite</p>';
var g = '<p>Voir la <a href="#">page des règles</a> ici</p>';
var h = '<button title="Fermer la fenêtre">OK</button>';
var i = '<style>body{color:red}</style><span class="k">Réglé</span>';
var j = 'display:flex;color:red';
var k = 'Report';
var l = 'The training programme';
var m2 = '\', true)">Voir les détails du compte';
var n2 = ' title="Effacer les données saisies">';
var o = '<p>Note <b>importante</b> sur la <a href="#">page</a></p>';
var p = '/api/conformite/etat-des-lieux';
var q = 'non_mise_en_oeuvre';
var r = 'nav.sec.evaluer-le-risque';
var s = "go('fria',null,'CONFORMITÉ','FRIA')";
var t = 'Finalité(s)';
var u = 'Coût/an';
"""


def test_litteraux_lit_les_chaines_et_saute_commentaires_et_expressions_regulieres():
    lits = outil.litteraux_js(JS)
    assert "Aucune activité récente pour ce compte" in lits
    assert "Il n’y a rien à afficher" in lits, "les \\u ne sont pas décodés"
    assert "Programme d'accompagnement" in lits
    assert "Total : " in lits and " systèmes enregistrés sur " in lits, "le gabarit n'est pas coupé à ses expressions"
    assert not any("pas rendu" in s for s in lits), "une chaîne citée dans un commentaire a été relevée"
    assert not any("de la" in s and "/" in s for s in lits)


def test_litteraux_ne_garde_que_le_francais_d_au_moins_deux_mots():
    ent = outil.entrees_des_litteraux(JS)
    t = ent["texte"]
    assert "Aucune activité récente pour ce compte" in t
    assert "systèmes enregistrés sur" in t
    assert "Report" not in t and "The training programme" not in t, "de l'anglais a été relevé"
    assert "display:flex;color:red" not in t
    assert "Réglé" not in t, "un seul mot n'est pas une entrée"
    assert not any("commentaire" in k for k in t), "une chaîne citée dans un commentaire a été relevée"
    assert t["Aucune activité récente pour ce compte"] == {"fr": "Aucune activité récente pour ce compte", "mots": 6}


def test_litteraux_ecarte_les_identifiants_et_garde_les_libelles_sans_espace():
    """UNE ROUTE, UNE VALEUR DE LISTE, UNE CLÉ DE TRADUCTION, UN APPEL ont des
    mots-outils (« des », « en ») mais ne sont jamais lus : les traduire
    casserait le code qui les compare. « Finalité(s) » et « Coût/an », sans
    espace eux aussi, sont des libellés affichés."""
    t = outil.entrees_des_litteraux(JS)["texte"]
    for ident in ("/api/conformite/etat-des-lieux", "non_mise_en_oeuvre", "nav.sec.evaluer-le-risque",
                  "go('fria',null,'CONFORMITÉ','FRIA')"):
        assert ident not in t, "identifiant relevé comme texte : %r" % ident
    assert "Finalité(s)" in t and "Coût/an" in t, sorted(k for k in t if " " not in k)


def test_litteraux_classe_un_fragment_HTML_comme_le_module_classerait_le_DOM():
    """UN <p> QUI NE PORTE QUE DU GRAS NU est un BLOC dans le DOM : sa clé
    est le textContent, sa valeur l'innerHTML. UN <p> AVEC UN LIEN est du
    TEXTE nœud par nœud. Un `title` est un attribut. Un <style> n'est pas
    parcouru. Une queue de balise coupée par une concaténation n'est pas du
    texte."""
    ent = outil.entrees_des_litteraux(JS)
    assert ent["bloc"]["Texte gras et suite"] == {"fr": "Texte gras et suite", "html": "Texte <b>gras</b> et suite", "mots": 4}, ent["bloc"]
    assert "Voir la" in ent["texte"] and "page des règles" in ent["texte"], sorted(ent["texte"])
    assert not any("Voir la page" in k for k in ent["bloc"]), "un paragraphe à lien a été classé bloc"
    #  « Note <b>importante</b> sur la » précède un LIEN dans le même <p> :
    #  dans le DOM, ce <p> est du régime TEXTE — le gras n'y change rien.
    assert not any(k.startswith("Note importante") for k in ent["bloc"]), "un morceau suivi d'un lien a été classé bloc"
    assert "sur la" in ent["texte"]
    assert ent["attr"]["Fermer la fenêtre"]["mots"] == 3
    assert not any("color" in k for r in ent for k in ent[r]), "le CSS d'un <style> a été relevé"
    assert "Voir les détails du compte" in ent["texte"] and not any("true)" in k for k in ent["texte"])
    assert not any("Effacer les données" in k for k in ent["texte"]), "une queue d'attribut a été relevée comme texte"


def test_litteraux_en_ligne_de_commande_ajoute_la_page_js_au_catalogue(dossier, tmp_path, capsys):
    js = str(tmp_path / "page.js")
    io.open(js, "w", encoding="utf-8").write(JS + "\nvar z = 'Programme détaillé';\n")
    c = os.path.join(dossier, "CATALOGUE.json")
    assert outil.main(["litteraux", "--catalogue", c, "--js", js]) == 0
    cat = json.load(io.open(c, encoding="utf-8"))
    assert cat["texte"]["Aucune activité récente pour ce compte"]["pages"] == ["_js"]
    assert cat["texte"]["Programme détaillé"]["pages"] == ["_js"], "une clé déjà _js est dédoublée"
    #  « Toutes (#) » portait « _js » d'un passage précédent, mais ce code-ci ne
    #  la rend plus : l'étiquette part, la page d'écran reste.
    assert cat["texte"]["Toutes (#)"]["pages"] == ["a"], "pages d'écran perdues ou « _js » périmé gardé : %r" % cat["texte"]["Toutes (#)"]["pages"]
    assert cat["js"]["fichier"] == "page.js" and cat["js"]["entrees"]["texte"] >= 4
    assert "nouvelles au catalogue" in capsys.readouterr().out
    #  REJOUÉ APRÈS UNE CORRECTION DU CODE, le passage précédent est effacé :
    #  une chaîne disparue du JavaScript disparaît du catalogue, une clé vue
    #  à l'écran garde ses pages, et rien n'est dédoublé.
    io.open(js, "w", encoding="utf-8").write("var y = 'Une seule chaîne restante ici';\n")
    assert outil.main(["litteraux", "--catalogue", c, "--js", js]) == 0
    cat = json.load(io.open(c, encoding="utf-8"))
    assert "Aucune activité récente pour ce compte" not in cat["texte"], "une chaîne disparue du code reste au catalogue"
    assert "Programme détaillé" not in cat["texte"], "une entrée « _js » seule survit à son retrait"
    assert cat["texte"]["Toutes (#)"]["pages"] == ["a"], cat["texte"]["Toutes (#)"]
    assert cat["texte"]["Une seule chaîne restante ici"]["pages"] == ["_js"]
    assert "passage précédent effacé" in capsys.readouterr().out


# ══════════════════════════════════════════════════════════════════════════
#  7 ter. LA TROISIÈME SOURCE — ce que le SERVEUR peint
# ══════════════════════════════════════════════════════════════════════════
#
# LE TROU QUE CES RÈGLES MESURENT. Le catalogue avait deux entrées : le DOM
# qu'une passe navigateur relève, et les littéraux de sentinel.page.js. Les
# écrans de normes n'étaient dans ni l'une ni l'autre : leur contenu vient
# d'une route JSON peinte APRÈS coup, et la passe ne la relève que si le
# compte a déclaré quelque chose. MESURÉ : 1 671 entrées, 26 538 mots que les
# routes servent et que le catalogue n'avait jamais vus — et « couverture »
# annonçait 99,6 % sur un inventaire aveugle à ce texte-là.
#
# POURQUOI LE CLIENT DE TEST ET NON LES MODULES. Treize routes sur seize sont
# minces (`jsonify(module.referentiel())`), mais trois composent leur charge
# SUR PLACE : conformité, ISO 42001, ISO 27001. Les appeler par leurs modules
# perdrait leurs 2 764 mots, et le perdrait en silence.


CHARGE = {
    "titre": "Le contexte de l'organisme",
    "note": "Une phrase <strong>appuyée</strong> et servie telle quelle",
    "anglais": "Review vendor contracts and avoid arbitrary termination of services",
    "route": "/api/en18286/referentiel",
    "paragraphes": [{"num": "4.1", "dit": "Le contexte de l'organisme"},
                    {"num": "4.2", "dit": "Les parties intéressées et leurs attentes"}],
    "Le libellé qui est une CLÉ": "oui",
    #  UNE CLÉ DÉJÀ AU CATALOGUE par une page d'écran : la route doit s'ajouter
    #  à ses pages, jamais les remplacer.
    "deja": "Un expert CONSEILPREV vous accompagne",
}


def test_les_charges_des_routes_se_classent_comme_le_DOM_les_classerait():
    """UNE CHAÎNE SERVIE PAR UNE ROUTE est du texte d'écran : plate elle est
    un TEXTE, porteuse de balises nues elle est un BLOC — le même
    `entrees_d_un_html` que les littéraux du JavaScript en décide. L'anglais
    et les identifiants n'entrent pas, et un libellé en position de CLÉ de
    dictionnaire entre, parce qu'il s'affiche tout autant."""
    e = outil.entrees_des_charges([CHARGE])
    assert "Le contexte de l'organisme" in e["texte"]
    assert e["texte"]["Le contexte de l'organisme"]["mots"] == 5
    assert "Les parties intéressées et leurs attentes" in e["texte"], "une chaîne imbriquée est perdue"
    assert "Le libellé qui est une CLÉ" in e["texte"], "une clé de dictionnaire n'est pas relevée"
    assert "Une phrase appuyée et servie telle quelle" in e["bloc"], sorted(e["bloc"])
    assert e["bloc"]["Une phrase appuyée et servie telle quelle"]["html"] == \
        "Une phrase <strong>appuyée</strong> et servie telle quelle"
    assert not any("Review vendor" in c for c in e["texte"]), "de l'anglais entre comme du français à traduire"
    assert not any(c.startswith("/api/") for c in e["texte"]), "une route est prise pour un libellé"
    #  LE MÊME TEXTE SERVI DEUX FOIS n'est qu'une entrée : « 4.1 » et le titre
    #  portent la même phrase, et elle ne se traduit qu'une fois.
    assert sum(1 for c in e["texte"] if c == "Le contexte de l'organisme") == 1


class _Reponse(object):
    def __init__(self, code, corps):
        self.status_code, self.data = code, corps.encode("utf-8")


class _Client(object):
    """Le client de test de Flask, réduit à ce que l'outil lui demande."""
    def __init__(self, table):
        self.table = table

    def get(self, route):
        return self.table[route]


def test_les_charges_sont_LUES_des_routes_et_une_route_muette_est_une_FAUTE(monkeypatch):
    """LA SEULE PIÈCE QUI PARLE AU SERVEUR. Une route qui répond autre chose
    que 200, ou autre chose que du JSON, doit remonter comme une FAUTE
    NOMMÉE : la rendre comme une charge vide ferait croire la passe complète,
    et le passage suivant retirerait du catalogue tout ce que cette route y
    apportait — le défaut exact qui avait rendu la dette des cadres
    impayable."""
    faux = types.ModuleType("app")
    faux.app = types.SimpleNamespace(test_client=lambda: _Client({
        "/ok": _Reponse(200, '{"t": "Le contexte de l\'organisme"}'),
        "/muette": _Reponse(401, '{}'),
        "/pas-json": _Reponse(200, '<html>une page d\'erreur</html>'),
    }))
    monkeypatch.setitem(sys.modules, "app", faux)
    charges, fautes = outil.charges_des_routes(["/ok", "/muette", "/pas-json"])
    assert charges == [{"t": "Le contexte de l'organisme"}], charges
    assert [f[0] for f in fautes] == ["/muette", "/pas-json"], fautes
    assert "401" in fautes[0][1], fautes[0]
    assert "JSON" in fautes[1][1], fautes[1]


def test_une_route_qui_ne_repond_pas_est_une_FAUTE_et_rien_n_est_ecrit(dossier, capsys, monkeypatch):
    """UN INVENTAIRE PARTIEL RETIRERAIT DU CATALOGUE ce que la route muette y
    apporte — exactement le défaut qui avait rendu la dette des cadres
    impayable. La commande refuse donc d'écrire, et le dit."""
    c = os.path.join(dossier, "CATALOGUE.json")
    avant = io.open(c, encoding="utf-8").read()
    monkeypatch.setattr(outil, "charges_des_routes",
                        lambda routes: ([], [("/api/x/referentiel", "HTTP 401")]))
    assert outil.main(["routes", "--catalogue", c]) == 1
    sortie = capsys.readouterr().out
    assert "HTTP 401" in sortie and "RIEN N'EST ÉCRIT" in sortie, sortie
    assert io.open(c, encoding="utf-8").read() == avant, "le catalogue a été réécrit malgré la faute"
    #  FORCÉ, la commande écrit — et c'est alors un choix nommé.
    assert outil.main(["routes", "--catalogue", c, "--malgre-les-fautes"]) == 0


def test_routes_en_ligne_de_commande_ajoute_la_page_des_routes_et_la_REJOUE_sans_rien_garder(
        dossier, capsys, monkeypatch):
    c = os.path.join(dossier, "CATALOGUE.json")
    monkeypatch.setattr(outil, "charges_des_routes", lambda routes: ([CHARGE], []))
    #  LES SONDES SONT NEUTRALISÉES ICI, et c'est voulu : cette règle éprouve
    #  la comptabilité du catalogue — ce qui entre, ce qui sort, ce qui garde
    #  ses pages d'écran — sur une charge d'essai qu'elle maîtrise. Laisser
    #  partir les dix-huit vraies sondes y verserait quarante-cinq mille mots
    #  du dépôt, et l'assertion ne porterait plus sur rien de lisible. Leur
    #  propre règle est `test_les_sondes_du_depot_passent_TOUTES…`.
    monkeypatch.setattr(outil, "charges_des_sondes", lambda sondes: ([], []))
    assert outil.main(["routes", "--catalogue", c]) == 0
    cat = json.load(io.open(c, encoding="utf-8"))
    assert cat["texte"]["Le contexte de l'organisme"]["pages"] == ["_routes"]
    #  UNE CLÉ DÉJÀ VUE À L'ÉCRAN reçoit « _routes » EN PLUS de ses pages.
    assert cat["texte"]["Un expert CONSEILPREV vous accompagne"]["pages"] == ["b", "_routes"], \
        cat["texte"]["Un expert CONSEILPREV vous accompagne"]["pages"]
    assert cat["routes"]["routes"] == 1 and cat["routes"]["mots"]["texte"] >= 4
    assert "nouvelles au catalogue" in capsys.readouterr().out
    #  REJOUÉ APRÈS UNE CORRECTION DU MOTEUR : ce que la route ne sert plus
    #  quitte le catalogue, et la page d'écran d'une clé partagée reste.
    monkeypatch.setattr(outil, "charges_des_routes",
                        lambda routes: ([{"a": "Une seule phrase servie encore"}], []))
    monkeypatch.setattr(outil, "charges_des_sondes", lambda sondes: ([], []))
    assert outil.main(["routes", "--catalogue", c]) == 0
    cat = json.load(io.open(c, encoding="utf-8"))
    assert "Le contexte de l'organisme" not in cat["texte"], "une chaîne que la route ne sert plus reste"
    assert cat["texte"]["Un expert CONSEILPREV vous accompagne"]["pages"] == ["b"], \
        cat["texte"]["Un expert CONSEILPREV vous accompagne"]["pages"]
    assert cat["texte"]["Une seule phrase servie encore"]["pages"] == ["_routes"]
    assert "passage précédent effacé" in capsys.readouterr().out


def test_la_liste_des_routes_RELEVEES_couvre_toutes_celles_d_app_py():
    """UNE ROUTE DE RÉFÉRENTIEL QUI N'EST NI RELEVÉE NI ÉCARTÉE serait un trou
    silencieux : le jour où une quatorzième norme arrive, son questionnaire
    entier resterait hors de l'inventaire et « couverture » n'en saurait
    rien. Chaque écart porte donc sa raison, écrite."""
    src = io.open(os.path.join(_RACINE, "app.py"), encoding="utf-8").read()
    servies = set(re.findall(r"@app\.route\('(/api/[^']*referentiel[^']*)'", src))
    assert len(servies) >= 18, "%d routes de référentiel relevées dans app.py" % len(servies)
    relevees = set(outil.ROUTES_REFERENTIEL)
    ecartees = set(outil.ROUTES_HORS_INVENTAIRE)
    oubliees = sorted(servies - relevees - ecartees)
    assert not oubliees, (
        "routes de référentiel ni relevées ni écartées : %s — leur texte "
        "n'entrerait dans aucun lot" % oubliees)
    fantomes = sorted((relevees | ecartees) - servies)
    assert not fantomes, (
        "déclarées mais absentes d'app.py : %s — la déclaration ne protège "
        "plus rien" % fantomes)
    assert not (relevees & ecartees), sorted(relevees & ecartees)
    for r, raison in outil.ROUTES_HORS_INVENTAIRE.items():
        assert len(raison.split()) >= 5, (
            "« %s » est écartée sans raison lisible : %r" % (r, raison))


def test_les_pages_hors_menu_ne_se_regroupent_avec_aucune_rubrique():
    """« _routes » rejoint « _coquille » et « _js » : ce ne sont pas des
    rubriques du menu, et un lot ne les mélange pas à une rubrique légère."""
    assert outil.PAGES_HORS_MENU == ("_coquille", "_js", "_routes")
    assert outil.rubrique_de("_routes", {"_routes": "ÉVALUER"}) == "_routes", (
        "une rubrique déclarée pour une page hors menu la capturerait")
    cat = {"bloc": {}, "attr": {},
           "texte": {"r%d" % i: {"fr": "r%d" % i, "mots": 1, "pages": ["_routes"]} for i in range(3)},
           "rubriques": {"p": "AUDIT"}}
    cat["texte"]["p1"] = {"fr": "p1", "mots": 1, "pages": ["p"]}
    lots = outil.decouper_lots(cat, taille=2500)
    rubs = {l["rubrique"] for l in lots}
    assert "_routes" in rubs and "AUDIT" in rubs, rubs
    assert not any(l["rubrique"] not in ("_routes", "AUDIT") for l in lots), rubs


def test_le_catalogue_du_depot_porte_la_page_des_routes_et_son_inventaire():
    """CE QUE LE DÉPÔT DOIT MONTRER : la troisième source est relevée, et son
    volume est annoncé. Un catalogue qui perdrait « _routes » redirait
    « rien à traduire » sur les treize questionnaires de normes."""
    cat = _catalogue_reel()
    pages = set(p for r in ("bloc", "texte", "attr") for e in cat[r].values() for p in e["pages"])
    #  LA DETTE EST PAYÉE, ET LE SAUT A DONC DISPARU. La règle sautait tant
    #  que la passe « routes » n'avait pas été jouée sur le catalogue du
    #  dépôt : ses 26 143 mots inédits attendaient leur traduction, et le
    #  plancher de couverture (i18n/sentinel/SEUIL_COUVERTURE) interdisait de
    #  les parker ici non traduits. Ils le sont — la couverture en mots du
    #  catalogue entier, routes comprises, est mesurée à 99,5 %. La règle
    #  EXIGE donc désormais la page, au lieu de l'attendre.
    assert "_routes" in pages, (
        "le catalogue du dépôt ne porte plus la page « _routes » : les treize "
        "questionnaires de normes rediraient « rien à traduire » là où les "
        "routes servent 33 830 mots de français")
    n = sum(1 for r in ("bloc", "texte", "attr") for e in cat[r].values() if "_routes" in e["pages"])
    mots = sum(e["mots"] for r in ("bloc", "texte", "attr") for e in cat[r].values() if "_routes" in e["pages"])
    assert n >= 2000 and mots >= 30000, "%d entrées, %d mots sous « _routes »" % (n, mots)
    assert cat["routes"]["routes"] == len(outil.ROUTES_REFERENTIEL), cat["routes"]
    #  ET LES SONDES, COMPTÉES À PART. Les additionner aux routes ferait
    #  croire à dix-huit référentiels de plus ; les omettre laisserait croire
    #  que les POST d'évaluation ne sont pas relevés.
    assert cat["routes"]["sondes"] == len(outil.SONDES_EVALUATION), cat["routes"]
    assert cat["routes"]["mots"]["texte"] >= 30000, cat["routes"]["mots"]


# ══════════════════════════════════════════════════════════════════════════
#  8. LE CATALOGUE ET LES LOTS COMMITÉS — les entrées des traducteurs
# ══════════════════════════════════════════════════════════════════════════

@functools.lru_cache(maxsize=None)
def _catalogue_reel():
    assert os.path.exists(CATALOGUE), "i18n/sentinel/CATALOGUE.json n'est pas dans le dépôt"
    return json.load(io.open(CATALOGUE, encoding="utf-8"))


#: LA DETTE EST PAYÉE, ET LA DÉCLARATION A DONC DISPARU. Quatre pages de
#: prEN 18286 manquaient au catalogue : nées après le dernier relevé
#: navigateur, elles étaient nommées ici plutôt que tues. La règle disait
#: elle-même ce qui devait arriver — « une page nommée ici que le catalogue
#: COUVRIRAIT fait tomber la règle à son tour » — et c'est ce qui est
#: arrivé : la passe refaite les couvre, et la liste est tombée avec.
#: Ce que la règle mesure redevient simple : le catalogue couvre EXACTEMENT
#: les pages de PAGE_META. Pour qu'une dette puisse se redéclarer un jour,
#: elle devra s'écrire ici de nouveau, avec sa raison — jamais se taire.


# ══════════════════════════════════════════════════════════════════════════
#  7 bis. REFAIRE LE CATALOGUE SANS RIEN PERDRE
# ══════════════════════════════════════════════════════════════════════════
#
# LE DÉFAUT QUI RENDAIT LA DETTE IMPAYABLE, ET IL A ÉTÉ MESURÉ. Le catalogue
# « se refait », disait la règle ci-dessous. En pratique, non : une passe
# refaite PERDAIT 1 920 clés (22 421 mots) sur les quatre pages à document
# embarqué. `querySelectorAll` ne traverse pas la frontière d'un document, donc
# l'inventaire s'arrêtait à la bordure de l'<iframe> ; les clés présentes au
# catalogue y étaient entrées par un script d'appoint, une fois, qui n'est pas
# au dépôt. Refaire le catalogue effaçait donc du travail déjà traduit, et
# l'inventaire concluait « ces pages n'ont rien à traduire ».
#
# DEUX OPTIONS LE RÉPARENT, ET CES RÈGLES LES MESURENT :
#   --cadres  descend dans les documents embarqués de MÊME origine ;
#   --fusion  reprend d'une passe précédente ce que celle-ci n'a pas vu.


PANNEAU = {
    "inv": {"texte": {"du panneau": {"fr": "du panneau", "pages": [], "mots": 2}},
            "bloc": {}, "attr": {}},
    "cadres": [
        {"texte": {"du cadre": {"fr": "du cadre", "pages": [], "mots": 2},
                   "du panneau": {"fr": "ECRASERAIT", "pages": [], "mots": 1}},
         "bloc": {"bloc du cadre": {"fr": "bloc", "pages": [], "mots": 1}},
         "attr": {}},
        "autre-origine",
        None,
    ],
}


def test_l_outil_sait_DESCENDRE_dans_les_documents_embarques():
    """LA DESCENTE SE JOUE, ELLE NE SE LIT PAS. La première version de cette
    règle cherchait « contentDocument » dans le source : la batterie de
    mutations a montré qu'on pouvait ANNULER la descente sans la faire
    tomber. Elle est donc une fonction nommée, jouée ici sur un faux DOM.

    TROIS CADRES, TROIS CAS : un lisible, un d'une autre origine — dont le
    `contentDocument` LÈVE, et ce n'est pas une faute : un document qu'on ne
    peut pas lire n'est pas un document qu'on traduit —, et un sans corps."""
    [sans, avec] = _node([
        {"op": "panneau", "panneau": PANNEAU, "cadres": False},
        {"op": "panneau", "panneau": PANNEAU, "cadres": True},
    ])
    assert sorted(sans["texte"]) == ["du panneau"], sans
    assert sans["bloc"] == {}, sans
    assert sorted(avec["texte"]) == ["du cadre", "du panneau"], avec
    assert sorted(avec["bloc"]) == ["bloc du cadre"], avec
    #  CE QUE LE PANNEAU PORTE PRIME SUR CE QUE LE CADRE EN DIT : la clé est
    #  la même, et c'est l'écran principal qui la tranche.
    assert avec["texte"]["du panneau"]["fr"] == "du panneau", avec["texte"]

    #  LE DRAPEAU EST LU, et son défaut est FAUX : une option toujours active
    #  changerait la mesure sans qu'on l'ait demandée.
    [vide, drapeau] = _node([
        {"op": "options", "argv": ["extraire"]},
        {"op": "options", "argv": ["extraire", "--cadres"]},
    ])
    assert vide["cadres"] is False, vide
    assert drapeau["cadres"] is True, drapeau


def test_la_passe_DIT_ce_qu_elle_laisse_dans_les_cadres():
    """UNE MESURE QU'ON NE VOIT PAS NE SE FAIT PAS. Quand la passe n'ouvre
    pas les cadres — c'est son défaut —, elle doit dire que --cadres les
    relève, et combien : sinon le trou se redevine à chaque fois."""
    assert "documents embarqués NON ouverts" in SRC_OUTIL_JS
    #  LE COMPTE DOIT ÊTRE DANS LA LIGNE QUE LA PASSE IMPRIME, et non
    #  seulement dans l'en-tête du fichier : la batterie de mutations a montré
    #  qu'on pouvait vider le message sans faire tomber la règle, parce que le
    #  même nombre figure aussi dans le commentaire du haut.
    i = SRC_OUTIL_JS.index("documents embarqués NON ouverts")
    ligne = SRC_OUTIL_JS[i:i + 400]
    assert "--cadres les relève" in ligne, ligne[:160]
    assert "19 000 mots" in ligne, (
        "la passe ne dit plus COMBIEN elle laisse dans les cadres : %r"
        % ligne[:200])
    #  LA LIGNE EST CONDITIONNELLE : la dire quand on VIENT de les ouvrir
    #  serait un contresens.
    assert "if (!opts.cadres) {" in SRC_OUTIL_JS, (
        "la passe annonce le trou des cadres même quand elle les a ouverts")


def test_une_passe_refaite_NE_PERD_PAS_ce_qu_elle_n_a_pas_visite():
    """LE CŒUR DE LA RÉPARATION. La fusion reprend les clés de l'ancienne passe
    que la nouvelle n'a pas vues ; elle NE touche à rien de ce que la nouvelle
    a vu — un texte réécrit à l'écran ne se fait pas remplacer par son
    ancienne version ; et elle laisse partir les clés d'une page que PAGE_META
    ne connaît plus."""
    neuf = {
        "rubriques": {"alpha": "A", "beta": "B"},
        "bloc": {}, "attr": {},
        "texte": {"vue a l ecran": {"fr": "neuf", "pages": ["alpha"], "mots": 1}},
    }
    ancien = {
        "bloc": {}, "attr": {},
        "texte": {
            "vue a l ecran": {"fr": "ANCIEN", "pages": ["alpha"], "mots": 9},
            "jamais revue": {"fr": "gardee", "pages": ["beta"], "mots": 4},
            "page disparue": {"fr": "perdue", "pages": ["gamma"], "mots": 7},
            "coquille": {"fr": "gardee aussi", "pages": ["_coquille"], "mots": 3},
        },
    }
    [r] = _node([{"op": "fusionner", "neuf": neuf, "ancien": ancien}])
    cat = r["cat"]
    assert r["bilan"]["reprises"] == 2, r["bilan"]
    assert r["bilan"]["mots"] == 7, r["bilan"]
    #  CE QUE LA NOUVELLE PASSE A VU N'EST PAS ÉCRASÉ.
    assert cat["texte"]["vue a l ecran"]["fr"] == "neuf", cat["texte"]
    #  CE QU'ELLE N'A PAS VU EST GARDÉ, avec sa page.
    assert cat["texte"]["jamais revue"]["pages"] == ["beta"], cat["texte"]
    assert "coquille" in cat["texte"], cat["texte"]
    #  ET LA PAGE QUE PAGE_META NE CONNAÎT PLUS S'EN VA AVEC SES CLÉS.
    assert "page disparue" not in cat["texte"], cat["texte"]


def test_la_fusion_se_demande_et_ne_s_impose_pas():
    """UNE FUSION TOUJOURS ACTIVE EMPÊCHERAIT DE MESURER CE QU'UNE PASSE
    TROUVE SEULE — et c'est précisément la mesure qui a montré le défaut."""
    [vide, avec] = _node([
        {"op": "options", "argv": ["extraire"]},
        {"op": "options", "argv": ["extraire", "--fusion", "vieux.json"]},
    ])
    assert vide["fusion"] == "", vide
    assert avec["fusion"] == "vieux.json", avec
    #  ET L'APPEL EST GARDÉ PAR L'OPTION. Sans cette ligne, la batterie de
    #  mutations rendait la fusion inconditionnelle sans rien faire tomber :
    #  `extraire` ne se joue pas sans navigateur, donc c'est la GARDE qui se
    #  mesure ici — une passe qui fusionnerait toujours ne pourrait plus dire
    #  ce qu'elle trouve SEULE, et c'est cette mesure-là qui a révélé le
    #  trou des 1 920 clés.
    assert "  if (opts.fusion) {" in SRC_OUTIL_JS, (
        "la fusion n'est plus gardée par son option : elle s'imposerait à "
        "chaque passe, et une passe ne se mesurerait plus seule")


def test_le_catalogue_du_depot_couvre_les_pages_de_PAGE_META_et_la_coquille():
    cat = _catalogue_reel()
    rubriques = outil.lire_rubriques_page_js()
    #  LE COMPTE N'EST PLUS ÉCRIT ICI, ET C'EST CE QUI A DÛ CHANGER. La règle
    #  finissait par « == 122 » : le jour où PAGE_META en a porté 126, elle
    #  est tombée sur sa propre constante. Ce qu'elle doit mesurer est
    #  l'ACCORD entre le catalogue et PAGE_META, aux pages déclarées près.
    assert len(rubriques) >= 122, "%d rubriques relevées" % len(rubriques)
    assert cat["pages"] == len(rubriques), (
        "le catalogue couvre %d pages et PAGE_META en porte %d : une page "
        "servie que l'inventaire ne voit pas dirait « rien à traduire » là "
        "où tout reste à traduire"
        % (cat["pages"], len(rubriques)))
    pages_vues = set(p for r in ("bloc", "texte", "attr") for e in cat[r].values() for p in e["pages"])
    manquantes = sorted(set(rubriques) - pages_vues)
    assert not manquantes, "pages sans aucune entrée : %s" % manquantes
    assert "_coquille" in pages_vues and "_js" in pages_vues
    assert cat["js"]["fichier"] == "sentinel.page.js"


def test_chaque_entree_du_catalogue_est_sa_propre_normalisation_avec_ses_mots_et_ses_pages():
    """UNE CLÉ NON NORMALISÉE ne sera jamais cherchée ; un compte de mots faux
    fausse la couverture ; une entrée sans page n'entre dans aucun lot."""
    cat = _catalogue_reel()
    n = 0
    for r in ("bloc", "texte", "attr"):
        for cle, e in cat[r].items():
            n += 1
            assert outil.normaliser(cle) == cle, "%s : %r" % (r, cle[:60])
            assert outil.normaliser(e["fr"]) == cle, "%s : fr %r ne donne pas la clé %r" % (r, e["fr"][:40], cle[:40])
            assert e["mots"] == outil.compter_mots(e["fr"]), (r, cle[:60], e["mots"])
            assert e["pages"], "%s : %r sans page" % (r, cle[:60])
            if r == "bloc":
                assert not re.search(r"<\w+\s", e["html"]), "un bloc du catalogue porte un attribut : %r" % e["html"][:60]
    assert n >= 3000, n


#: LES TEXTES QU'UNE PASSE D'INVENTAIRE NE PEUT PAS VOIR — déclarés, avec
#: le fichier qui les porte, et non tus. L'inventaire lit le DOM APRÈS la
#: peinture : il ne peut donc voir ni un texte d'attente que le JavaScript
#: remplace, ni une note qui dépend d'un état du serveur que la recette
#: locale n'a pas (le flux de veille y est vide, et l'écran affiche
#: « Signaux en attente… » à la place). Leur anglais est servi en
#: production, et le supprimer rendrait ces deux textes au français.
#:
#: CE QUE LA DÉCLARATION NE PERMET PAS. Elle ne couvre que ces deux clés :
#: toute AUTRE entrée périmée fait toujours tomber la règle. Une clé nommée
#: ici dont le français aurait disparu de son fichier la fait tomber aussi
#: — la déclaration ne protégerait plus rien. Et le jour où le catalogue en
#: voit une, la règle tombe pour le dire : la dette est payée, la ligne doit
#: disparaître. C'est ainsi que PAGES_APRES_LE_CATALOGUE a disparu.
HORS_DE_PORTEE_DE_LA_PASSE = {
    #  UNE SEULE RESTE, ET C'EST UNE VRAIE. Son français vit dans le document
    #  EMBARQUÉ de panorama.html : `querySelectorAll` ne traverse pas la
    #  frontière d'un document, et la passe n'ouvre les cadres que sur
    #  --cadres (qui ferait tomber le plancher de couverture, faute que les
    #  19 000 mots de ces cadres soient traduits). Que ce texte-là soit bien
    #  en anglais est mesuré ailleurs, dans un navigateur :
    #  tests/test_sentinel_cadres_traduits.
    u"CNIL · ANSSI · EU AI Act · Commission — rafraîchi côté serveur (# min)":
        "panorama.html",
}
#  « Chargement du moteur… » N'Y EST PLUS, ET C'EST LA RÈGLE QUI L'A EXIGÉ.
#  Elle disait : « le jour où le catalogue en voit une, la règle tombe pour le
#  dire : la dette est payée, la ligne doit disparaître. » C'est arrivé. La
#  passe d'inventaire ne spoofait que deux des trois signaux que
#  sentinel.page.js envoie à /api/client-signal : le serveur la prenait pour un
#  navigateur automatisé et bloquait l'adresse 1 800 s, donc TOUT ce qu'une
#  API peint s'inventoriait sur son texte d'attente. Le troisième signal posé,
#  la passe voit la peinture — et ce texte d'attente avec elle.


def test_les_dictionnaires_du_depot_passent_verifier_contre_le_catalogue_du_depot():
    """_exemple.json vise du VRAI texte : chaque clé est au catalogue, y
    compris celles que seul le JavaScript rend (les cartes de formation)."""
    fichiers = outil.fichiers_du_dossier(DOSSIER)
    assert fichiers and all(os.path.basename(f) != "CATALOGUE.json" for f in fichiers)
    cat = _catalogue_reel()
    fautes = [f for f in outil.verifier_fichiers(fichiers, cat)
              if not (f[2] in HORS_DE_PORTEE_DE_LA_PASSE
                      and f[3].startswith(u"périmée"))]
    assert not fautes, fautes[:5]
    #  LA DÉCLARATION SE MESURE DES DEUX CÔTÉS : le français existe encore à la
    #  source, et le catalogue ne le voit toujours pas.
    for cle, fichier in sorted(HORS_DE_PORTEE_DE_LA_PASSE.items()):
        src = io.open(os.path.join(_RACINE, fichier), encoding="utf-8").read()
        motif = u"[0-9 ]+".join(re.escape(p) for p in cle.split(u"#"))
        assert re.search(motif, src), (
            u"« %s » est déclaré hors de portée de la passe, mais %s ne le "
            u"porte plus : la déclaration ne protège plus rien" % (cle[:40], fichier))
        assert not (cle in cat["texte"] or cle in cat["bloc"] or cle in cat["attr"]), (
            u"« %s » est au catalogue : la passe le voit désormais, la "
            u"déclaration doit disparaître" % cle[:40])


#: LE POIDS QU'ON A LE DROIT DE GARER DANS « RIEN À TRADUIRE ». Mesuré au
#: 5 octobre 2026 : 1 752 mots sur 206 282, soit 0,85 % du catalogue. Le
#: plafond est posé À PEINE AU-DESSUS. Pourquoi un plafond : la table dispense
#: de traduire, donc elle peut tout dispenser. Un module entier qu'on y
#: garerait ferait monter la couverture à 100 % sans qu'une ligne soit
#: traduite — et le plancher de SEUIL_COUVERTURE ne garderait plus rien.
PLAFOND_SANS_TRADUCTION = 2200


def test_la_table_SANS_TRADUCTION_ne_peut_pas_servir_a_garer_du_francais():
    """CE QU'ELLE DÉCLARE EST VRAI, ET BORNÉ. Chaque clé est au catalogue,
    porte une raison écrite, et le poids total garé reste sous un plafond —
    sans quoi la table deviendrait le moyen de tenir le plancher de couverture
    sans traduire."""
    chemin = os.path.join(DOSSIER, "SANS_TRADUCTION.json")
    assert os.path.isfile(chemin), "i18n/sentinel/SANS_TRADUCTION.json manque"
    cles = outil.lire_sans_traduction(chemin)
    assert cles, "la table est vide : lire_sans_traduction ne lit pas le fichier"
    cat = _catalogue_reel()
    #  1. AUCUNE CLÉ FANTÔME. Une clé qui n'est plus au catalogue dispenserait
    #     de traduire un texte que personne ne sert plus — et masquerait le
    #     jour où un texte VOISIN arriverait, lui, en français.
    absentes = sorted(c for c in cles
                      if not (c in cat["texte"] or c in cat["bloc"] or c in cat["attr"]))
    assert not absentes, (
        u"déclarées « rien à traduire » mais plus au catalogue : %s" % absentes[:5])
    #  2. CHAQUE CLÉ PORTE SA RAISON, et une raison d'une ligne n'en est pas une.
    muettes = sorted(c for c, r in cles.items() if not isinstance(r, str) or len(r.strip()) < 40)
    assert not muettes, u"déclarées sans raison écrite : %s" % muettes[:5]
    #  3. LE POIDS GARÉ EST BORNÉ, et c'est la garde qui compte.
    poids = 0
    for regime in ("bloc", "texte", "attr"):
        for c, e in cat[regime].items():
            if c in cles:
                poids += e.get("mots", 0)
    assert poids <= PLAFOND_SANS_TRADUCTION, (
        u"%d mots garés dans « rien à traduire », plafond %d : la table sert à "
        u"nommer ce qui n'a pas de traduction, pas à dispenser un module de la "
        u"sienne" % (poids, PLAFOND_SANS_TRADUCTION))
    #  4. ET ELLE NE PEUT PAS ÊTRE AUSSI UN DICTIONNAIRE. Une clé déclarée ici
    #     ET traduite ailleurs dirait deux choses contraires du même texte.
    dico, _ = sentinel_i18n.fusionner(DOSSIER)
    doubles = sorted(c for c in cles
                     if (dico.get("texte") or {}).get(c) or (dico.get("bloc") or {}).get(c))
    assert not doubles, (
        u"déclarées « rien à traduire » ET traduites : %s" % doubles[:5])


def test_la_route_ne_sert_pas_le_catalogue_et_le_dossier_reel_se_fusionne_sans_faute():
    """LE CATALOGUE EST DANS LE DOSSIER SERVI : ses valeurs sont des fiches,
    pas des chaînes. Le servir ferait 900 Ko de plus et une faute par
    entrée dans le journal."""
    assert all(os.path.basename(p) != "CATALOGUE.json" for p in sentinel_i18n._fichiers(DOSSIER))
    dico, fautes = sentinel_i18n.fusionner(DOSSIER)
    assert not fautes, fautes[:3]
    assert all(isinstance(v, str) for r in dico for v in dico[r].values())


def test_les_fichiers_de_travail_du_depot_couvrent_le_catalogue_sans_doublon_et_sont_remplis():
    """CE SONT LES ENTRÉES DES TRADUCTEURS : chaque clé du catalogue est
    dans exactement un fichier. La traduction est faite : chaque case « en »
    est REMPLIE — une case vide est un texte qui resterait en français à
    l'écran sans que rien ne le dise."""
    cat = _catalogue_reel()
    fichiers = sorted(glob.glob(os.path.join(A_TRADUIRE, "*.json")))
    assert len(fichiers) >= 20, len(fichiers)
    vues, remplies = [], 0
    for f in fichiers:
        lot = json.load(io.open(f, encoding="utf-8"))
        assert lot["_lot"] == os.path.splitext(os.path.basename(f))[0]
        assert set(lot) == {"_lot", "_rubrique", "_pages", "_mots", "texte", "bloc"}, sorted(lot)
        for cle, e in lot["texte"].items():
            vues.append(("texte", cle))
            remplied = bool(e["en"])
            remplies += remplied
        for cle, e in lot["bloc"].items():
            vues.append(("bloc", cle))
            remplies += bool(e["en"])
    #  UN ATTRIBUT DONT LA CLÉ EST AUSSI UN TEXTE est une seule case pour la
    #  route : les deux se cherchent dans « texte ».
    attendues = set([("bloc", k) for k in cat["bloc"]] + [("texte", k) for k in cat["texte"]] + [("texte", k) for k in cat["attr"]])
    #  ET CE QUI N'A RIEN À TRADUIRE N'EST PAS DU TRAVAIL. Une citation d'un
    #  texte anglais, un nom propre, un identifiant ou une valeur n'entre pas
    #  dans l'inbox des traducteurs : y laisser une case vide ferait compter
    #  comme en attente ce qui n'attend rien. La table est bornée par
    #  test_la_table_SANS_TRADUCTION_ne_peut_pas_servir_a_garer_du_francais —
    #  elle ne peut donc pas servir à vider l'inbox d'un module entier.
    sans = outil.lire_sans_traduction()
    attendues = set((r, k) for r, k in attendues if k not in sans)
    assert len(vues) == len(set(vues)), "doublons entre fichiers de travail : %s" % [v for v in vues if vues.count(v) > 1][:3]
    assert set(vues) == attendues, "écart catalogue / lots : %s" % sorted(attendues ^ set(vues))[:5]
    assert remplies == len(vues), (
        "%d entrée(s) sans traduction dans les fichiers de travail"
        % (len(vues) - remplies))


def test_le_catalogue_a_l_inventaire_annonce_par_regime():
    """LA MESURE DE CE QU'IL Y A À TRADUIRE, telle que rapportée : un
    catalogue qui maigrit sans qu'on sache pourquoi est une page qui a cessé
    d'être inventoriée."""
    cat = _catalogue_reel()
    ecran = {r: sum(1 for e in cat[r].values() if e["pages"] != ["_js"]) for r in ("bloc", "texte", "attr")}
    assert ecran["bloc"] >= 300 and ecran["texte"] >= 2500 and ecran["attr"] >= 350, ecran
    js = sum(1 for r in ("bloc", "texte", "attr") for e in cat[r].values() if "_js" in e["pages"])
    assert js >= 4000, js
    mots = sum(e["mots"] for r in ("bloc", "texte", "attr") for e in cat[r].values())
    assert mots >= 80000, mots


def test_l_outil_python_est_documente_et_expose_ses_cinq_commandes(capsys):
    with pytest.raises(SystemExit):
        outil.main(["--help"])
    aide = capsys.readouterr().out
    for c in ("litteraux", "verifier", "couverture", "lots", "assembler"):
        assert c in aide, c
    assert "outils/i18n_sentinel.js" in SRC_OUTIL_PY and "sentInventaire" in SRC_OUTIL_JS


# ══════════════════════════════════════════════════════════════════════════
#  LES SONDES — CE QUE LES ROUTES D'ÉVALUATION SERVENT
# ══════════════════════════════════════════════════════════════════════════

#: LE PLAFOND DE LA DETTE DÉCLARÉE. Une sonde dont `tete_attendue` vaut
#: `None` n'ouvre que la tête « rien de déclaré » du module : les phrases du
#: taux de ce module-là restent hors inventaire. C'est une dette, elle est
#: bornée ici, et le plafond ne monte pas sans qu'on l'écrive.
#:
#: IL VAUT EXACTEMENT LA MESURE, PAS UN CHIFFRE ROND AU-DESSUS. Onze sondes
#: sont dans ce cas aujourd'hui ; un plafond à douze aurait laissé une
#: douzième s'ajouter en silence, et un plafond qui ne mord jamais n'est pas
#: une mesure. Le faire descendre est un progrès, le faire monter demande
#: d'écrire pourquoi.
PLAFOND_SONDES_SANS_TETE = 11


def test_les_routes_d_EVALUATION_sont_toutes_SONDEES_ou_ecartees_avec_leur_raison():
    """UNE ROUTE D'ÉVALUATION QUI N'EST NI SONDÉE NI ÉCARTÉE EST LE TROU QUE
    CETTE SÉRIE VIENT DE BOUCHER.

    CE QUI A ÉTÉ MESURÉ. `ROUTES_REFERENTIEL` ne relève que des GET : ce
    qu'un module sait dire AVANT qu'on lui parle. Les routes d'évaluation
    sont des POST, et leurs phrases sont COMPOSÉES au moment de répondre —
    elles n'existent dans aucun fichier HTML, donc ni la passe navigateur ni
    la passe de routes ne pouvait les voir. Relevé : 52 chaînes de français,
    958 mots, que le catalogue ignorait et que le plancher de couverture
    comptait donc pour rien. Un lecteur anglophone qui remplissait un
    questionnaire les lisait en français.

    Cette règle refuse que le trou se rouvre : une dix-septième route
    d'évaluation sans sonde, et elle tombe."""
    src = io.open(os.path.join(_RACINE, "app.py"), encoding="utf-8").read()
    servies = set(re.findall(
        r"@app\.route\('(/api/[^']*(?:evaluer|exposition|analyser)[^']*)'", src))
    assert len(servies) >= 16, (
        "%d routes d'évaluation relevées dans app.py" % len(servies))
    sondees = {s['route'] for s in outil.SONDES_EVALUATION}
    oubliees = sorted(servies - sondees)
    assert not oubliees, (
        "routes d'évaluation sans sonde : %s — leurs phrases composées "
        "n'entreraient dans aucun lot" % oubliees)
    fantomes = sorted(sondees - servies)
    assert not fantomes, (
        "sondées mais absentes d'app.py : %s — la sonde ne protège plus "
        "rien" % fantomes)


def test_chaque_sonde_PORTE_sa_raison_et_une_charge_qui_la_justifie():
    """UNE SONDE SANS RAISON EST UNE CHARGE QU'ON N'OSE PLUS TOUCHER. Six
    mois plus tard, personne ne sait si `{'qualites': ['intermediaire']}`
    visait la tête du taux ou un hasard de copie, et la corriger devient un
    pari. Chaque sonde dit donc ce qu'elle va chercher."""
    for s in outil.SONDES_EVALUATION:
        assert s['route'].startswith('/api/'), s
        assert isinstance(s['charge'], dict), s
        assert 'tete_attendue' in s, (
            "« %s » ne dit pas quelle tête elle ouvre, même pour dire "
            "« aucune »" % s['route'])
        assert len(s.get('pourquoi', '').split()) >= 8, (
            "« %s » est sondée sans raison lisible : %r"
            % (s['route'], s.get('pourquoi')))


def test_une_sonde_qui_n_ouvre_PAS_sa_tete_est_une_FAUTE_et_non_une_charge_vide():
    """CE QUI REND UNE SONDE VÉRIFIABLE. Une charge qui cesserait d'être
    acceptée — un vocabulaire de qualification qui change, une clé de
    réponse renommée — retomberait sur la tête « rien de déclaré » et
    n'inventorierait plus les phrases pour lesquelles elle a été écrite.
    Rien ne le dirait : le catalogue serait simplement plus petit, et la
    couverture resterait à 100 % de moins en moins de choses."""
    bonne = {'route': '/api/dga/evaluer',
             'charge': {'qualites': ['intermediaire'],
                        'reponses': {'art12_a': 'tenu'}},
             'tete_attendue': 'mesure', 'pourquoi': u'x' * 40}
    charges, fautes = outil.charges_des_sondes([bonne])
    assert len(charges) == 1 and not fautes, fautes

    mauvaise = dict(bonne, tete_attendue='hors_champ')
    charges, fautes = outil.charges_des_sondes([mauvaise])
    assert not charges, "une sonde qui vise à côté a quand même été relevée"
    assert len(fautes) == 1 and 'tête' in fautes[0][1], fautes

    refusee = {'route': '/api/nis2/evaluer', 'charge': {},
               'tete_attendue': None, 'pourquoi': u'x' * 40}
    charges, fautes = outil.charges_des_sondes([refusee])
    assert not charges and fautes and 'HTTP' in fautes[0][1], fautes


def test_les_sondes_du_depot_passent_TOUTES_et_apportent_du_francais():
    """ET ELLES APPORTENT QUELQUE CHOSE. Une sonde qui répond 200, ouvre sa
    tête et ne rend aucune phrase française n'inventorie rien : elle coûte un
    appel et donne l'illusion d'une couverture. La dette qui reste — les
    modules dont seule la tête « rien de déclaré » est atteinte — est bornée
    par PLAFOND_SONDES_SANS_TETE, et ce plafond est écrit."""
    charges, fautes = outil.charges_des_sondes(outil.SONDES_EVALUATION)
    assert not fautes, "sondes en faute : %s" % (fautes,)
    assert len(charges) == len(outil.SONDES_EVALUATION)
    entrees = outil.entrees_des_charges(charges)
    mots = sum(e['mots'] for r in entrees for e in entrees[r].values())
    assert mots > 5000, (
        "les sondes ne rapportent que %d mots de français — elles n'ouvrent "
        "plus les charges qu'elles visaient" % mots)
    sans_tete = [s['route'] for s in outil.SONDES_EVALUATION
                 if s['tete_attendue'] is None]
    assert len(sans_tete) <= PLAFOND_SONDES_SANS_TETE, (
        "%d sonde(s) n'ouvrent que la tête « rien de déclaré » (plafond %d) : "
        "%s" % (len(sans_tete), PLAFOND_SONDES_SANS_TETE, sorted(sans_tete)))


def test_le_catalogue_du_depot_PORTE_ce_que_les_sondes_ont_releve():
    """LA MESURE EST FAITE SUR LE CATALOGUE COMMITÉ, pas sur une passe qu'on
    relance. Si le catalogue du dépôt ne porte pas les phrases des sondes,
    c'est que la passe n'a pas été rejouée après les avoir ajoutées — et le
    plancher de couverture est alors tenu contre un inventaire périmé."""
    cat = outil.charger_catalogue(outil.CATALOGUE)
    assert cat.get('routes', {}).get('sondes'), (
        "le catalogue ne dit pas combien de sondes l'ont alimenté")
    assert cat['routes']['sondes'] == len(outil.SONDES_EVALUATION), (
        cat['routes']['sondes'], len(outil.SONDES_EVALUATION))
    #  TROIS PHRASES QUE SEULE UNE SONDE PEUT AVOIR FAIT ENTRER : la tête du
    #  taux (qui n'apparaît qu'un questionnaire rempli), le hors-champ du
    #  DGA, et le régime national du Data Act.
    temoins = [
        u"# % des obligations attendues de vos qualités sont déclarées "
        u"tenues, sur # points attendus dont # renseigné(s).",
        u"HORS CHAMP. Vous n'êtes ni un organisme du secteur public",
        u"Article # §# du Data Act, par renvoi à l'article # §# du RGPD",
    ]
    cles = cat['texte']
    for t in temoins:
        assert any(c.startswith(t) for c in cles), (
            "le catalogue ne porte pas « %s… » : la passe des routes n'a pas "
            "été rejouée avec les sondes" % t[:60])
