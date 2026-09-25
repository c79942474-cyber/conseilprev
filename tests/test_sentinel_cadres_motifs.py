# -*- coding: utf-8 -*-
"""SENTINEL EN ANGLAIS — LES CADRES ET LES LIBELLÉS COMPOSÉS.

CE QUE LA MESURE NAVIGATEUR A MONTRÉ (i18n/sentinel/MESURE_APRES.json), ET
QUE LE DICTIONNAIRE SEUL NE POUVAIT PAS COMBLER :

  1. LES CADRES. Cinq pages de Sentinel embarquent un autre document en
     <iframe> de même origine — /map, /panorama, /enveloppe, /empreinte-parc,
     /observatoire. Leur texte restait à 98 % en français en anglais : le
     moteur de traduction par contenu n'y était pas chargé. Désormais ces
     documents chargent sentinel.i18n.js avec `data-sent-cadre`, lisent la
     langue (celle de Sentinel s'ils sont dans son cadre, sinon la langue
     mémorisée), traduisent leur corps, observent leurs rendus différés — par
     LA MÊME mécanique que Sentinel (sentBrancher) — et suivent un changement
     de langue fait dans Sentinel (message du parent, événement `storage`).
     En français, rien ne change.

  2. LES LIBELLÉS COMPOSÉS. « Supprimer <nom du système> du registre » : une
     phrase d'interface qui encadre une donnée. Une clé exacte ne peut pas les
     couvrir ; la section « motif » du dictionnaire les écrit une fois, la
     donnée en « {} ».

CES RÈGLES EXÉCUTENT LE CODE : le vrai module sous node, sur le DOM réduit
de tests/_dom_sentinel_corps.js pour la traduction, sur une fenêtre et un
parent simulés pour les cadres ; la vraie route Flask sur un dossier d'essai.
Elles lisent aussi les vrais fichiers servis : une page de cadre qui ne
charge pas le module est une page qui reste en français.
"""
import functools
import io
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RACINE)
os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
os.environ.setdefault('FLASK_SECRET_KEY', 'recette-sentinel-cadres')

import sentinel_i18n  # noqa: E402

NODE = shutil.which("node")
MODULE = os.path.join(_RACINE, "sentinel.i18n.js")
HARNAIS = os.path.join(_RACINE, "tests", "_dom_sentinel_corps.js")


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


SRC_MODULE = _lire("sentinel.i18n.js")
PAGE_JS = _lire("sentinel.page.js")
SENTINEL = _lire("sentinel.html")

#: LA BALISE QUI BRANCHE UN DOCUMENT EMBARQUÉ — et rien d'autre ne le fait.
BALISE_CADRE = '<script src="/sentinel.i18n.js" data-sent-cadre defer></script>'


# ══════════════════════════════════════════════════════════════════════════
#  LE HARNAIS DE TRADUCTION — le vrai module, le DOM réduit
# ══════════════════════════════════════════════════════════════════════════

@functools.lru_cache(maxsize=None)
def _jouer_json(programme):
    if not NODE:
        pytest.skip("node absent : le module ne peut pas être exécuté")
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "prog.json")
        io.open(p, "w", encoding="utf-8").write(programme)
        r = subprocess.run([NODE, HARNAIS, MODULE, p],
                           capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail("le module n'a pas tourné :\n%s" % (r.stderr or "")[-2500:])
    return r.stdout


def _jouer(html, ops, dico):
    out = json.loads(_jouer_json(json.dumps(
        {"html": html, "dico": dico, "ops": ops}, ensure_ascii=False, sort_keys=True)))
    for i, r in enumerate(out):
        assert not (isinstance(r, dict) and "erreur" in r), (
            "l'opération %d (%s) a levé : %s" % (i, ops[i]["op"], r["erreur"][:600]))
    return out


def _dico(motif, texte=None, bloc=None):
    return {"texte": texte or {}, "bloc": bloc or {}, "motif": motif}


# ══════════════════════════════════════════════════════════════════════════
#  1. LES MOTIFS — exécutés
# ══════════════════════════════════════════════════════════════════════════

REGISTRE = {"Supprimer {} du registre": "Delete {} from the register"}


def test_un_libelle_compose_est_traduit_et_la_donnee_passe_intacte_title_ET_aria_label():
    """LE CAS MESURÉ : le « × » d'une ligne du registre IA porte le nom du
    système dans son title et son aria-label. Le nom passe tel quel."""
    html = ('<button id="x" title="Supprimer Chatbot service client du registre" '
            'aria-label="Supprimer Chatbot service client du registre">×</button>')
    r = _jouer(html, [{"op": "traduire", "langue": "en"},
                      {"op": "attr", "sel": "#x", "nom": "title"},
                      {"op": "attr", "sel": "#x", "nom": "aria-label"}], _dico(REGISTRE))
    assert r[1] == "Delete Chatbot service client from the register", r[1]
    assert r[2] == r[1], r[2]
    assert r[0] == 2, "deux attributs écrits attendus, %r" % r[0]


def test_un_libelle_compose_en_noeud_texte_garde_ses_blancs_et_revient_en_francais():
    html = '<p id="p"> Supprimer Maintenance predictive reseau du registre </p>'
    r = _jouer(html, [{"op": "traduire", "langue": "en"},
                      {"op": "texte", "sel": "#p", "enfant": 0},
                      {"op": "traduire", "langue": "fr"},
                      {"op": "texte", "sel": "#p", "enfant": 0}], _dico(REGISTRE))
    assert r[1] == " Delete Maintenance predictive reseau from the register ", repr(r[1])
    assert r[3] == " Supprimer Maintenance predictive reseau du registre ", repr(r[3])


def test_les_chiffres_d_un_motif_reviennent_dans_l_ordre():
    """« Fiche 30% complète (10 questions…) » : deux nombres, les
    parenthèses et le « % » du motif ne sont pas de la syntaxe."""
    html = '<span id="s" title="Fiche 30% complète (10 questions essentielles IA Act)">30%</span>'
    motif = {"Fiche #% complète (# questions essentielles IA Act)":
             "Record #% complete (# essential AI Act questions)"}
    r = _jouer(html, [{"op": "traduire", "langue": "en"}, {"op": "attr", "sel": "#s", "nom": "title"}],
               _dico(motif))
    assert r[1] == "Record 30% complete (10 essential AI Act questions)", r[1]


def test_un_morceau_capture_qui_est_une_cle_exacte_est_traduit_les_autres_sont_recopies():
    """LE NOM D'UN BLOC est une phrase d'interface déjà traduite ; le nom d'un
    système saisi par l'utilisateur ne l'est pas. Chiffres et captures
    ensemble : « Bloc 2 sur 5 · <nom> — Verrouillé »."""
    motif = {"Bloc # sur # · {} — Verrouillé": "Block # of # · {} — Locked"}
    texte = {"Qualifier mon rôle": "Qualify my role"}
    html = ('<b id="a">Bloc 2 sur 5 · Qualifier mon rôle — Verrouillé</b>'
            '<b id="b">Bloc 3 sur 5 · Mon système maison — Verrouillé</b>')
    r = _jouer(html, [{"op": "traduire", "langue": "en"},
                      {"op": "texte", "sel": "#a", "enfant": 0},
                      {"op": "texte", "sel": "#b", "enfant": 0}], _dico(motif, texte))
    assert r[1] == "Block 2 of 5 · Qualify my role — Locked", r[1]
    assert r[2] == "Block 3 of 5 · Mon système maison — Locked", r[2]


def test_la_cle_exacte_passe_AVANT_le_motif():
    motif = {"Supprimer {} du registre": "Delete {} from the register"}
    texte = {"Supprimer Recette du registre": "Delete the test run from the register"}
    html = '<p id="p">Supprimer Recette du registre</p>'
    r = _jouer(html, [{"op": "traduire", "langue": "en"}, {"op": "texte", "sel": "#p", "enfant": 0}],
               _dico(motif, texte))
    assert r[1] == "Delete the test run from the register", r[1]


def test_le_motif_le_plus_long_gagne_quel_que_soit_l_ordre_du_fichier():
    """L'ORDRE D'ESSAI EST DÉTERMINISTE : du plus long au plus court, puis
    par clé. Le générique est écrit EN PREMIER dans le fichier ; c'est le
    précis qui doit gagner."""
    motif = {"Étape # — {} · {}": "Step # — {} · {}",
             "Étape # — {} · vous y êtes": "Step # — {} · you are here"}
    html = '<span id="s" title="Étape 3 — Registre · vous y êtes">·</span>'
    r = _jouer(html, [{"op": "traduire", "langue": "en"}, {"op": "attr", "sel": "#s", "nom": "title"},
                      {"op": "motifs", "motif": motif}], _dico(motif))
    assert r[1] == "Step 3 — Registre · you are here", r[1]
    assert r[2]["cles"] == ["Étape # — {} · vous y êtes", "Étape # — {} · {}"], r[2]


def test_les_motifs_sont_compiles_UNE_fois_par_dictionnaire_du_plus_long_au_plus_court():
    """L'ordre du FICHIER ne compte pas : du plus long au plus court, puis
    par ordre des clés à longueur égale (« aa » avant « dd », bien que
    « dd » soit écrit avant)."""
    paires = [["b {}", "B {}"], ["dd {}", "DD {}"], ["ccc {}", "CCC {}"], ["aa {}", "AA {}"]]
    r = _jouer("<p>x</p>", [{"op": "motifs", "paires": paires}], _dico({}))
    assert r[0]["meme"] is True, "la liste compilée est reconstruite à chaque appel"
    assert r[0]["cles"] == ["ccc {}", "aa {}", "dd {}", "b {}"], r[0]["cles"]


_NE_PAS_ATTRAPER = [
    ("capture-vide", '<p id="p">Supprimer () du registre</p>',
     {"Supprimer ({}) du registre": "Delete ({}) from the register"},
     "« {} » capture un morceau NON VIDE : « Supprimer () du registre » n'a pas de nom"),
    ("motif-sans-rien-de-fixe", '<p id="p">Texte quelconque</p>', {"{}": "HIJACK {}"},
     "un motif sans rien de fixe attraperait tout"),
    ("trous-differents", '<p id="p">Supprimer X du registre</p>', {"Supprimer {} du registre": "Delete from the register"},
     "une traduction qui perd la donnée ne s'affiche pas"),
    ("regime-bloc", '<p id="p">Supprimer <b>X</b> du registre</p>', REGISTRE,
     "un bloc est du HTML : les motifs ne s'y appliquent pas"),
    ("ancre-debut", '<p id="p">Ne pas Supprimer X du registre</p>', REGISTRE,
     "un motif couvre le libellé ENTIER, pas un morceau"),
    ("ancre-fin", '<p id="p">Supprimer X du registre demain</p>', REGISTRE,
     "un motif couvre le libellé ENTIER, pas un morceau"),
]


@pytest.mark.parametrize("nom,html,motif,pourquoi", _NE_PAS_ATTRAPER, ids=[c[0] for c in _NE_PAS_ATTRAPER])
def test_ce_qu_un_motif_ne_doit_pas_attraper_reste_en_francais(nom, html, motif, pourquoi):
    r = _jouer(html, [{"op": "html", "sel": "#p"}, {"op": "traduire", "langue": "en"},
                      {"op": "html", "sel": "#p"}], _dico(motif))
    assert r[2] == r[0], "%s — %r devenu %r" % (pourquoi, r[0], r[2])


def test_les_caracteres_speciaux_d_un_motif_sont_du_texte_pas_une_expression():
    """« (…) », « . », « ? », « + » dans une clé : échappés. Sans échappement,
    « Dernières évaluations (# sur #) » ne se retrouverait jamais."""
    motif = {"Dernières évaluations (# sur #)": "Latest assessments (# of #)",
             "a.b {}": "A.B {}"}
    html = '<p id="p">Dernières évaluations (6 sur 9)</p><p id="q">axb Z</p>'
    r = _jouer(html, [{"op": "traduire", "langue": "en"}, {"op": "texte", "sel": "#p", "enfant": 0},
                      {"op": "texte", "sel": "#q", "enfant": 0}], _dico(motif))
    assert r[1] == "Latest assessments (6 of 9)", r[1]
    assert r[2] == "axb Z", "« . » a été lu comme « n'importe quel caractère » : %r" % r[2]


# ══════════════════════════════════════════════════════════════════════════
#  2. LA FUSION ET LA ROUTE
# ══════════════════════════════════════════════════════════════════════════

NAVIGATEUR = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Firefox/130.0',
              'Accept-Language': 'fr', 'Accept-Encoding': 'identity'}


@pytest.fixture
def dossier(tmp_path, monkeypatch):
    d = tmp_path / "i18n"
    d.mkdir()
    monkeypatch.setattr(sentinel_i18n, "DOSSIER", str(d))
    sentinel_i18n._CACHE.clear()
    yield d
    sentinel_i18n._CACHE.clear()


def _ecrire(d, nom, contenu):
    (d / nom).write_text(json.dumps(contenu, ensure_ascii=False), encoding="utf-8")


def _get(chemin="/sentinel.en.json"):
    import app as A
    return A.app.test_client().get(chemin, headers=NAVIGATEUR)


def test_la_route_sert_les_motifs_de_deux_fichiers_fusionnes(dossier):
    _ecrire(dossier, "a.json", {"texte": {"Un": "One"}, "motif": {"Supprimer {} du registre": "Delete {} from the register"}})
    _ecrire(dossier, "b.json", {"motif": {"Retirer {} du comparateur": "Remove {} from the comparator"}})
    r = _get()
    assert r.status_code == 200, r.status_code
    assert r.get_json() == {"texte": {"Un": "One"}, "bloc": {},
                            "motif": {"Supprimer {} du registre": "Delete {} from the register",
                                      "Retirer {} du comparateur": "Remove {} from the comparator"}}, r.get_json()


def test_sans_motif_le_dictionnaire_servi_est_celui_d_avant(dossier):
    """PAS DE MOTIF, PAS DE SECTION : ce qu'un navigateur d'avant recevait,
    il le reçoit encore octet pour octet."""
    _ecrire(dossier, "a.json", {"texte": {"Un": "One"}, "motif": {}})
    assert _get().get_json() == {"texte": {"Un": "One"}, "bloc": {}}


def test_un_conflit_de_motif_est_journalise_et_le_premier_gagne(dossier, caplog):
    _ecrire(dossier, "a.json", {"motif": {"Supprimer {} du registre": "Delete {} from the register"}})
    _ecrire(dossier, "b.json", {"motif": {"Supprimer {} du registre": "Erase {} from the register"}})
    with caplog.at_level(logging.ERROR):
        d = _get().get_json()
    assert d["motif"] == {"Supprimer {} du registre": "Delete {} from the register"}, d
    assert any("SENTINEL_I18N_CONFLIT" in m and "b.json" in m and "motif" in m for m in caplog.messages), caplog.messages


_FAUTIFS = [
    ("rien-de-fixe", "{} {}", "{} {}", "rien de fixe"),
    ("non-normalise", "Supprimer  {} du 12 registre", "Delete {} from the # register", "normalisé"),
    ("trous-differents", "Supprimer {} du registre", "Delete from the register", "« {} »"),
    ("dieses-differents", "Bloc # sur # · {}", "Block # · {}", "« # »"),
    ("pas-une-chaine", "Supprimer {} du registre", 3, "chaîne"),
]


@pytest.mark.parametrize("nom,cle,val,mot", _FAUTIFS, ids=[c[0] for c in _FAUTIFS])
def test_un_motif_fautif_est_NOMME_et_ecarte_les_autres_sont_servis(dossier, caplog, nom, cle, val, mot):
    _ecrire(dossier, "a.json", {"motif": {cle: val, "Retirer {} du comparateur": "Remove {} from the comparator"}})
    with caplog.at_level(logging.ERROR):
        d = _get().get_json()
    assert d.get("motif") == {"Retirer {} du comparateur": "Remove {} from the comparator"}, d
    fautes = [m for m in caplog.messages if "a.json" in m and mot in m]
    assert fautes, (mot, caplog.messages)


# ══════════════════════════════════════════════════════════════════════════
#  3. LE FICHIER DES MOTIFS — des libellés RÉELS de Sentinel
# ══════════════════════════════════════════════════════════════════════════

def _motifs_du_depot():
    with io.open(os.path.join(sentinel_i18n.DOSSIER, "motifs.json"), encoding="utf-8") as f:
        return json.load(f)


def test_le_fichier_des_motifs_a_la_forme_d_un_lot_et_se_fusionne_sans_faute():
    lot = _motifs_du_depot()
    assert lot["_lot"] == "motifs" and lot["texte"] == {} and lot["bloc"] == {}, sorted(lot)
    assert len(lot["motif"]) >= 20, len(lot["motif"])
    for cle, val in lot["motif"].items():
        assert sentinel_i18n.motif_faute(cle, val) is None, (cle, sentinel_i18n.motif_faute(cle, val))
    dico, fautes = sentinel_i18n.fusionner()
    assert not fautes, fautes
    assert dico["motif"] == lot["motif"]


def _sources():
    """Où un libellé composé peut naître : le script de Sentinel (accents
    échappés ou non), son HTML, et les modules serveur qui écrivent les
    motifs du rail de validation."""
    src = [PAGE_JS, SENTINEL]
    for nom in ("parcours_normes.py", "dora_parcours.py"):
        src.append(_lire(nom))
    #  APLANIES AUSSI : le code écrit « réponse(s)&nbsp;: » avec une
    #  insécable, la clé porte l'espace que le navigateur calcule.
    return src + [sentinel_i18n.aplanir(x) for x in src]


def test_chaque_motif_vise_un_libelle_que_le_code_construit_vraiment():
    """UN MOTIF QUI NE VISE RIEN NE PROUVE RIEN. Chaque morceau fixe de
    chaque motif (entre ses « {} » et ses « # ») doit se trouver dans le
    code qui construit le libellé — tel quel, ou avec ses accents échappés
    comme sentinel.page.js les écrit souvent."""
    sources = _sources()
    for cle in _motifs_du_depot()["motif"]:
        #  « — » ET « · » SONT LA COLLE DES CONCATÉNATIONS : « Bloc N sur M · »
        #  + nom + « — » + état, l'état venant du serveur (dora_parcours.py).
        for morceau in re.split(r"\{\}|#|—|·", cle):
            morceau = morceau.strip()
            if not re.search(r"[A-Za-zÀ-ɏ]{2}", morceau):
                continue
            echappe = json.dumps(morceau, ensure_ascii=True)[1:-1]
            assert any(morceau in s or echappe in s for s in sources), (
                "motif %r : le morceau %r n'est construit nulle part" % (cle, morceau))


# ══════════════════════════════════════════════════════════════════════════
#  4. LES CADRES — les pages embarquées chargent le module
# ══════════════════════════════════════════════════════════════════════════

def _cadres_de_sentinel():
    """Les adresses que sentinel.html embarque en <iframe>, sans requête."""
    out = []
    for m in re.finditer(r"<iframe\b[^>]*>", SENTINEL):
        a = re.search(r'\s(?:data-src|src)="(/[^"]*)"', m.group(0))
        assert a, "une iframe sans adresse : %s" % m.group(0)[:120]
        out.append(a.group(1).split("?")[0])
    return out


def test_les_cinq_cadres_de_sentinel_sont_les_cinq_attendus():
    assert sorted(_cadres_de_sentinel()) == sorted(
        ["/map", "/panorama", "/enveloppe", "/empreinte-parc", "/observatoire"]), _cadres_de_sentinel()


def test_chaque_document_embarque_charge_le_module_en_mode_cadre_une_fois():
    """LA ROUTE DIT QUEL FICHIER : /enveloppe et /empreinte-parc servent
    panorama.html. Un document servi en cadre sans la balise reste en
    français — c'est exactement le trou mesuré."""
    import app as A
    table = dict(A.PAGES)
    table.update(A.PAGES_RESERVEES)
    for route in _cadres_de_sentinel():
        assert route in table, "%s : aucune route ne sert ce cadre" % route
        html = _lire(table[route])
        assert html.count(BALISE_CADRE) == 1, "%s (%s) : %d balise(s)" % (route, table[route], html.count(BALISE_CADRE))
        assert html.count("sentinel.i18n.js") == 1, table[route]
        assert html.index(BALISE_CADRE) < html.index("</body>"), table[route]


def test_sentinel_lui_meme_ne_se_branche_pas_en_cadre():
    """Sentinel branche son document par sentinel.page.js ; la marque de
    cadre y ferait DEUX branchements, deux observateurs, deux passes."""
    assert "data-sent-cadre" not in SENTINEL


def test_la_carte_publique_sert_la_balise_et_le_module_est_servi():
    """CE QUE LE NAVIGATEUR REÇOIT, pas le fichier : le serveur versionne
    les scripts (« ?v=<empreinte> ») ; la marque doit survivre à la
    réécriture."""
    r = _get("/map")
    assert r.status_code == 200, r.status_code
    servi = re.findall(r'<script src="/sentinel\.i18n\.js(?:\?v=[0-9a-f]+)?" data-sent-cadre defer></script>',
                       r.get_data(as_text=True))
    assert len(servi) == 1, servi
    m = _get("/sentinel.i18n.js")
    assert m.status_code == 200 and "javascript" in (m.mimetype or ""), (m.status_code, m.mimetype)


# ══════════════════════════════════════════════════════════════════════════
#  5. LE CADRE SE BRANCHE, SUIT LA LANGUE, ET NE CHANGE RIEN EN FRANÇAIS
# ══════════════════════════════════════════════════════════════════════════

_CADRE_PRELUDE = r"""
var opts = JSON.parse(process.argv[2]);
var appels = [], observateurs = [], images = [], fetchs = 0, ecouteurs = {};
var etat = { stockage: opts.stockage };
var attrs = { lang: 'fr' };
var docEl = {
  getAttribute: function (n) { return n in attrs ? attrs[n] : null; },
  setAttribute: function (n, v) { attrs[n] = String(v); },
  removeAttribute: function (n) { delete attrs[n]; }
};
var corps = { id: 'body', nodeType: 1, contains: function () { return true; } };
var win = {
  location: { origin: 'http://ici' },
  addEventListener: function (t, f) { (ecouteurs[t] = ecouteurs[t] || []).push(f); },
  localStorage: opts.stockage === 'bloque'
    ? { getItem: function () { throw new Error('stockage bloqué'); } }
    : { getItem: function (k) { return k === 'cp-sentinel-langue-v1' ? etat.stockage : null; } }
};
win.document = { body: corps, documentElement: docEl,
  currentScript: opts.auto ? { hasAttribute: function (n) { return n === opts.auto; } } : null };
if (opts.parent === 'seul') win.parent = win;
else if (opts.parent === 'etranger') {
  win.parent = {};
  Object.defineProperty(win.parent, 'SENT_LANG', { get: function () { throw new Error('SecurityError'); } });
} else win.parent = { SENT_LANG: opts.parent };
var window = win, document = win.document;
"""

_CADRE_TEMOINS = r"""
function sentTraduireCorps(r, d, l) { appels.push([r.id || '?', !!d, l]); return 0; }
function MutationObserver(cb) {
  this.actif = true;
  this.observe = function (t, o) { this.cible = t.id; this.options = o; observateurs.push(this); };
  this.disconnect = function () { this.actif = false; };
  this.takeRecords = function () { return []; };
}
function requestAnimationFrame(fn) { images.push(fn); }
function fetch(url, o) {
  fetchs++;
  return Promise.resolve({ ok: true, json: function () {
    return Promise.resolve({ texte: { a: 'b' }, bloc: {}, motif: { 'x {}': 'X {}' } }); } });
}
"""

_CADRE_EPILOGUE = r"""
(async function () {
  var attendre = function () { return new Promise(function (r) { setTimeout(r, 5); }); };
  var b = opts.auto ? win.SENT_CADRE : (opts.demarrer ? sentCadreDemarrer(win) : null);
  var releve = function () {
    return { appels: appels.slice(), fetchs: fetchs, lang: 'lang' in attrs ? attrs.lang : null,
             observe: !!(b && b.obs), observateurs: observateurs.length };
  };
  var faits = { etapes: [] };
  await attendre();
  faits.etapes.push(releve());
  for (var i = 0; i < (opts.evenements || []).length; i++) {
    var ev = opts.evenements[i];
    if (ev.type === 'storage') {
      etat.stockage = ev.valeur;
      (ecouteurs.storage || []).forEach(function (f) { f({ key: ev.key }); });
    } else {
      var src = ev.source === 'parent' ? win.parent : {};
      (ecouteurs.message || []).forEach(function (f) {
        f({ source: src, origin: ev.origin || 'http://ici', data: ev.data }); });
    }
    await attendre();
    faits.etapes.push(releve());
  }
  faits.ecouteurs = Object.keys(ecouteurs).sort();
  faits.branche = typeof win.SENT_CADRE;
  faits.options = observateurs.length ? observateurs[0].options : null;
  faits.dico = b && b.dico;
  process.stdout.write(JSON.stringify(faits));
})().catch(function (e) { process.stdout.write(JSON.stringify({ erreur: String(e && e.stack || e) })); });
"""


@functools.lru_cache(maxsize=None)
def _cadre_json(opts_json):
    if not NODE:
        pytest.skip("node absent")
    with tempfile.TemporaryDirectory() as d:
        h = os.path.join(d, "cadre.js")
        io.open(h, "w", encoding="utf-8").write(_CADRE_PRELUDE + SRC_MODULE + _CADRE_TEMOINS + _CADRE_EPILOGUE)
        r = subprocess.run([NODE, h, opts_json], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail("le cadre n'a pas tourné :\n%s" % (r.stderr or "")[-2500:])
    out = json.loads(r.stdout)
    assert "erreur" not in out, out.get("erreur", "")[:800]
    return out


def _cadre(**opts):
    base = {"stockage": "fr", "parent": "seul", "auto": None, "demarrer": True, "evenements": []}
    base.update(opts)
    if base["auto"]:
        base["demarrer"] = False
    return _cadre_json(json.dumps(base, sort_keys=True))


MSG_EN = {"type": "message", "source": "parent", "data": {"type": "cp-sentinel-langue", "langue": "en"}}
MSG_FR = {"type": "message", "source": "parent", "data": {"type": "cp-sentinel-langue", "langue": "fr"}}


def test_en_francais_un_cadre_ne_fait_RIEN_ni_telechargement_ni_observateur_ni_ecriture():
    """LE COMPORTEMENT FRANÇAIS EST INCHANGÉ : pas un octet téléchargé, pas
    une écriture, pas d'observateur, la langue du document intacte. Seuls
    deux écouteurs attendent."""
    f = _cadre(stockage="fr", parent="seul")
    e = f["etapes"][0]
    assert e == {"appels": [], "fetchs": 0, "lang": "fr", "observe": False, "observateurs": 0}, e
    assert f["ecouteurs"] == ["message", "storage"], f["ecouteurs"]


def test_la_langue_memorisee_en_anglais_traduit_le_cadre_et_l_observe():
    f = _cadre(stockage="en", parent="seul")
    e = f["etapes"][0]
    assert e["fetchs"] == 1 and e["appels"] == [["body", True, "en"]], e
    assert e["observe"] is True and e["lang"] == "en", e
    assert f["options"] == {"childList": True, "subtree": True, "characterData": True}, f["options"]
    assert f["dico"]["motif"] == {"x {}": "X {}"}, "les motifs reçus ne sont pas gardés : %r" % f["dico"]


def test_dans_le_cadre_de_Sentinel_la_langue_AFFICHEE_du_parent_fait_foi():
    """Le parent a décidé : sa langue affichée l'emporte sur un stockage
    périmé ou bloqué."""
    assert _cadre(stockage="fr", parent="en")["etapes"][0]["appels"] == [["body", True, "en"]]
    assert _cadre(stockage="bloque", parent="en")["etapes"][0]["appels"] == [["body", True, "en"]]
    assert _cadre(stockage="en", parent="fr")["etapes"][0]["appels"] == []


def test_un_parent_qui_n_a_pas_encore_decide_ou_etranger_laisse_la_langue_memorisee():
    assert _cadre(stockage="en", parent=None)["etapes"][0]["appels"] == [["body", True, "en"]]
    assert _cadre(stockage="en", parent="etranger")["etapes"][0]["appels"] == [["body", True, "en"]]
    assert _cadre(stockage="bloque", parent="seul")["etapes"][0]["appels"] == []


def test_le_cadre_suit_le_message_de_Sentinel_aller_ET_retour():
    """SENTINEL BASCULE, LE CADRE SUIT : en anglais, traduction et
    observateur ; au retour, restitution, observateur arrêté, et la langue
    du document rendue à l'original."""
    f = _cadre(stockage="fr", parent="seul", evenements=[MSG_EN, MSG_FR])
    avant, en, fr = f["etapes"]
    assert avant["appels"] == [], avant
    assert en["appels"] == [["body", True, "en"]] and en["observe"] is True and en["lang"] == "en", en
    assert fr["appels"][-1] == ["body", False, "fr"] and fr["observe"] is False and fr["lang"] == "fr", fr


_ETRANGERS = [
    ("autre-source", dict(MSG_EN, source="autre")),
    ("autre-origine", dict(MSG_EN, origin="http://ailleurs")),
    ("autre-type", dict(MSG_EN, data={"type": "autre", "langue": "en"})),
]


@pytest.mark.parametrize("nom,ev", _ETRANGERS, ids=[c[0] for c in _ETRANGERS])
def test_un_message_qui_ne_vient_pas_de_Sentinel_est_ignore(nom, ev):
    f = _cadre(stockage="fr", parent="seul", evenements=[ev])
    assert f["etapes"][1]["appels"] == [] and f["etapes"][1]["fetchs"] == 0, f["etapes"][1]


def test_le_cadre_suit_l_evenement_storage_de_la_cle_de_langue_et_d_elle_seule():
    f = _cadre(stockage="fr", parent="seul", evenements=[
        {"type": "storage", "key": "autre-cle", "valeur": "en"},
        {"type": "storage", "key": "cp-sentinel-langue-v1", "valeur": "en"}])
    assert f["etapes"][1]["appels"] == [], "une autre clé a fait basculer la langue"
    assert f["etapes"][2]["appels"] == [["body", True, "en"]], f["etapes"][2]


def test_deux_annonces_de_la_meme_langue_ne_traduisent_pas_deux_fois():
    f = _cadre(stockage="fr", parent="seul", evenements=[
        MSG_EN, {"type": "storage", "key": "cp-sentinel-langue-v1", "valeur": "en"}])
    assert f["etapes"][2]["appels"] == [["body", True, "en"]] and f["etapes"][2]["fetchs"] == 1, f["etapes"][2]


@pytest.mark.parametrize("attribut,attendu", [("data-sent-cadre", "object"), ("data-autre", "undefined")],
                         ids=["marque", "sans-marque"])
def test_le_module_se_branche_seul_QUAND_la_balise_porte_data_sent_cadre(attribut, attendu):
    f = _cadre(stockage="en", parent="seul", auto=attribut)
    assert f["branche"] == attendu, f["branche"]
    assert f["etapes"][0]["appels"] == ([["body", True, "en"]] if attendu == "object" else []), f["etapes"][0]


# ══════════════════════════════════════════════════════════════════════════
#  6. SENTINEL PRÉVIENT SES CADRES
# ══════════════════════════════════════════════════════════════════════════

_PREVENIR = r"""
var recus = [];
var doc = { location: { origin: 'http://ici' }, getElementsByTagName: function (t) {
  return t !== 'iframe' ? [] : [
    { contentWindow: { postMessage: function (m, o) { recus.push([m, o]); } } },
    { contentWindow: null } ]; } };
var n = sentPrevenirCadres(doc, 'en');
process.stdout.write(JSON.stringify({ n: n, recus: recus }));
"""

_SETLANG = r"""
var ordre = [], stock = {};
var window = {}, document = { id: 'doc' };
var localStorage = { setItem: function (k, v) { stock[k] = v; } };
var SENT_LANG = 'fr', SENT_LANG_CLE = 'cp-sentinel-langue-v1';
function sentAppliquer() { ordre.push('appliquer:' + SENT_LANG); }
function sentPrevenirCadres(d, l) { ordre.push('cadres:' + (d && d.id) + ':' + l); return 0; }
"""


def _node(src):
    if not NODE:
        pytest.skip("node absent")
    with tempfile.TemporaryDirectory() as d:
        h = os.path.join(d, "x.js")
        io.open(h, "w", encoding="utf-8").write(src)
        r = subprocess.run([NODE, h], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-2000:]
    return json.loads(r.stdout)


def test_sentPrevenirCadres_ecrit_a_chaque_cadre_a_SA_propre_origine_et_survit_a_un_cadre_absent():
    f = _node(SRC_MODULE + _PREVENIR)
    assert f["n"] == 1, f
    assert f["recus"] == [[{"type": "cp-sentinel-langue", "langue": "en"}, "http://ici"]], f["recus"]


def test_sentSetLang_previent_les_cadres_APRES_avoir_applique_la_langue():
    i = PAGE_JS.index("window.sentSetLang = function")
    fn = PAGE_JS[i:PAGE_JS.index("\n};", i) + 3]
    f = _node(_SETLANG + fn + r"""
window.sentSetLang('en');
process.stdout.write(JSON.stringify({ ordre: ordre, stock: stock }));
""")
    assert f["ordre"] == ["appliquer:en", "cadres:doc:en"], f["ordre"]
    assert f["stock"] == {"cp-sentinel-langue-v1": "en"}, f["stock"]
