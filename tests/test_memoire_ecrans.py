# -*- coding: utf-8 -*-
"""Les écrans de conformité gardent leurs réponses au rechargement.

LA DEMANDE : « NIS 2 perd ses réponses au rechargement de la page. Son rail
repart alors de « Suis-je concerné ? » ; les marques « lu » et « passé en
revue », elles, sont conservées. » Mesuré ensuite : ISO 27001, ISO 42001, le
CRA, DORA et ReCyF aussi.

CE QUI A ÉTÉ MESURÉ DANS UN NAVIGATEUR, AVANT D'ÉCRIRE UNE LIGNE
(recette_memoire_ecrans.js, sur le code d'alors) :
  · la page rechargée, les cinq cartes du taux de conformité retombaient à
    « — » (NIS 2 16 %, ISO 27001 41 %, ISO 42001 1 %, CRA 4 %, DORA 0 %
    avant) ; le rail NIS 2 repartait de « Suis-je concerné ? » ; les
    formulaires étaient vides ;
  · TROIS PERTES SANS MÊME RECHARGER. ReCyF, objectif 16 : cocher « moyens
    alloués » décochait la case au repeint suivant, et l'exigence retombait
    de « acquis » à « déclaré ». CRA : revenir sur l'analyse d'écart
    affichait « non renseigné » sur les exigences cotées. DORA : revenir sur
    le cadre de risque affichait « non déclaré » sur les articles déclarés.
    Dans les trois cas, l'état tenait la réponse et l'écran la taisait.

LE CODE EST EXÉCUTÉ, PAS LU. Le harnais évalue sous node la VRAIE tranche de
sentinel.page.js qui porte les cinq modules, le rail et la mémoire, avec les
VRAIS référentiels servis par l'application. Les réponses passent par les
vrais gestionnaires des champs ; un « rechargement » jette la page et en
évalue une neuve, en ne gardant que le stockage du navigateur ; ce que les
écrans affichent est relu dans le HTML qu'ils écrivent, comme un navigateur
le lirait : l'option `selected`, l'attribut `value`, la case `checked`.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RACINE)

import nis2_recyf  # noqa: E402

PAGE_JS = os.path.join(_RACINE, "sentinel.page.js")
PAGE_HTML = os.path.join(_RACINE, "sentinel.html")
HTML = io.open(PAGE_HTML, encoding="utf-8").read()
NODE = shutil.which("node")

#: LES CINQ RÉFÉRENTIELS DONT LES RÉPONSES SE PERDAIENT, et la clé de
#: chacun dans le stockage du navigateur. ReCyF a la sienne : c'est le
#: calque français de NIS 2, et son rail est celui de NIS 2.
CLES = {"nis2": "cp-sentinel-nis2-v1", "recyf": "cp-sentinel-recyf-v1",
        "iso27001": "cp-sentinel-iso27001-v1",
        "iso42001": "cp-sentinel-iso42001-v1",
        "cra": "cp-sentinel-cra-v1", "dora": "cp-sentinel-dora-v1"}

#: CE QUI GARDAIT DÉJÀ SES RÉPONSES, ET OÙ. Un référentiel du rail qui ne
#: serait ni ici ni dans la mémoire des écrans perdrait les siennes au
#: rechargement — c'est la règle de couverture qui le dit.
DEJA_GARDES = {"nist_ai_rmf": "cp-sentinel-nist-profil-v1",
               "owasp_llm": "cp-sentinel-owasp-declares-v1",
               "nist_800_53": "cp-sentinel-nist53-v1",
               "nist_800_82": "cp-sentinel-nist82-v1",
               "rgpd": "le registre des traitements, sur le serveur",
               "ia_act": "cpAuditState"}


# ══════════════════════════════════════════════════════════════════════════
#  LES VRAIS RÉFÉRENTIELS, tels que les routes les servent à l'écran
# ══════════════════════════════════════════════════════════════════════════

_REFS = {}


def _refs():
    if _REFS:
        return _REFS
    import app as application
    a = application.app
    lien = a.url_map.bind("localhost")
    for nom, url in (("nis2", "/api/nis2/referentiel"),
                     ("recyf", "/api/recyf/referentiel"),
                     ("iso27001", "/api/iso27001/referentiel"),
                     ("iso42001", "/api/iso42001/referentiel"),
                     ("cra", "/api/cra/referentiel"),
                     ("dora", "/api/dora/referentiel")):
        ep, args = lien.match(url, method="GET")
        with a.test_request_context(url, method="GET"):
            r = a.view_functions[ep](**args)
            r = r[0] if isinstance(r, tuple) else r
            _REFS[nom] = r.get_json()
    # L'OBJECTIF 16 TEL QUE LE MOTEUR LE REND pour une entité essentielle :
    # c'est la liste des exigences que l'écran peint.
    _REFS["recyf_analyse"] = dict(
        nis2_recyf.analyse_de_risque({}, "essentielle"), ok=True)
    return _REFS


# ══════════════════════════════════════════════════════════════════════════
#  LE HARNAIS
# ══════════════════════════════════════════════════════════════════════════

_SOCLE = r"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const REFS = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const HTML = fs.readFileSync(process.argv[4], 'utf8');
/* LA TRANCHE : des cinq modules jusqu'à la fin du fichier — leurs états,
   leurs écrans, NIST, ReCyF, le rail, et la mémoire. */
const DEBUT = 'var CRA_REF = null;';
const d0 = src.indexOf(DEBUT);
if (d0 < 0) throw new Error('la tranche des cinq modules est introuvable');
const TRANCHE = src.slice(d0);

/* LE STOCKAGE DU NAVIGATEUR SURVIT AU RECHARGEMENT ; LA PAGE, NON. */
const magasin = {};
let REFUS = false;
global.localStorage = {
  getItem(k) { if (REFUS) throw new Error('stockage refusé');
               return Object.prototype.hasOwnProperty.call(magasin, k) ? magasin[k] : null; },
  setItem(k, v) { if (REFUS) throw new Error('stockage refusé'); magasin[k] = String(v); },
  removeItem(k) { if (REFUS) throw new Error('stockage refusé'); delete magasin[k]; },
};

/* LES IDENTIFIANTS ÉCRITS DANS sentinel.html, et les options de ses
   listes : un champ qui n'y est pas n'existe pas pour le code non plus. */
const STATIQUES = {};
(HTML.match(/\bid="[^"]+"/g) || []).forEach(function (m) { STATIQUES[m.slice(4, -1)] = true; });
function optionsStatiques(id) {
  const m = HTML.match(new RegExp('<select\\b[^>]*\\bid="' + id + '"[^>]*>([\\s\\S]*?)</select>'));
  return m ? (m[1].match(/<option value="([^"]*)"/g) || []).map(function (o) {
    return o.slice(15, -1); }) : null;
}

let page = null;
function El(id, options) {
  this.id = id; this.style = {}; this.dataset = {}; this.checked = false;
  this.className = ''; this.enfants = []; this._options = options || null;
  this._valeur = ''; this._html = '';
  this.classList = { add() {}, remove() {}, contains() { return false; }, toggle() {} };
}
Object.defineProperty(El.prototype, 'value', {
  get() { return this._valeur; },
  /* COMME UN NAVIGATEUR : une valeur qu'aucune option ne porte laisse la
     liste vide. */
  set(v) { v = String(v == null ? '' : v);
           this._valeur = (this._options && this._options.indexOf(v) < 0) ? '' : v; } });
Object.defineProperty(El.prototype, 'innerHTML', {
  get() { return this._html; },
  set(v) { this._html = String(v);
           (this._html.match(/\bid="[^"]+"/g) || []).forEach(function (m) {
             page.rendus[m.slice(4, -1)] = true; }); } });
Object.defineProperty(El.prototype, 'textContent', {
  get() { return this._html.replace(/<[^>]*>/g, ''); }, set(v) { this._html = String(v); } });
Object.defineProperty(El.prototype, 'outerHTML', { get() { return this._html; }, set(v) {} });
El.prototype.setAttribute = function () {};
El.prototype.getAttribute = function () { return null; };
El.prototype.removeAttribute = function () {};
El.prototype.appendChild = function (c) { this.enfants.push(c); if (c && c.id) page.ajoutes[c.id] = c; return c; };
El.prototype.insertAdjacentHTML = function (o, h) { this.innerHTML = this._html + h; };
El.prototype.querySelector = function () { return null; };
El.prototype.querySelectorAll = function () { return []; };
El.prototype.closest = function () { return null; };
El.prototype.remove = function () {};

function chargerPage() {
  page = { elements: {}, rendus: {}, ajoutes: {}, ecouteurs: [], fenetre: [],
           appels: [], actif: null, recharge: 0 };
  global.document = {
    readyState: 'interactive',
    getElementById(id) {
      if (page.ajoutes[id]) return page.ajoutes[id];
      if (!STATIQUES[id] && !page.rendus[id]) return null;
      return page.elements[id] || (page.elements[id] = new El(id, optionsStatiques(id)));
    },
    querySelector(s) { return (s === '.page.on' && page.actif) ? { id: page.actif } : null; },
    querySelectorAll() { return []; },
    createElement(t) { return new El(''); },
    addEventListener(type, f, capture) { page.ecouteurs.push({ type: type, f: f, capture: !!capture }); },
    body: new El('body'),
  };
  (0, eval)(TRANCHE);
}
global.window = global;
global.addEventListener = function (type, f) { page.fenetre.push({ type: type, f: f }); };
global.fetch = function (u) { page.appels.push(String(u)); return new Promise(function () {}); };
global.location = { reload() { page.recharge++; } };
global.confirm = function () { return true; };
global.alert = function () {};
global.navigator = {};
global.requestAnimationFrame = function (f) { return setTimeout(f, 0); };

/* LA PAGE QUI PART : ce que le navigateur envoie avant de la jeter. */
function quitter() {
  page.fenetre.filter(function (e) { return e.type === 'pagehide'; })
    .forEach(function (e) { e.f({ type: 'pagehide' }); });
}
function recharger() { quitter(); chargerPage(); }
/* UNE RÉPONSE DANS LA PAGE : les écouteurs posés en capture passent AVANT
   le gestionnaire du champ, qui n'a encore rien écrit. */
function evenement(type) {
  page.ecouteurs.filter(function (e) { return e.type === type; }).forEach(function (e) {
    try { e.f({ type: type, target: new El('') }); } catch (err) {} });
}
function attendre(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

/* CE QU'UN NAVIGATEUR AFFICHE D'UN MORCEAU DE HTML : pour chaque champ,
   sa valeur visible et, pour une case, si elle est cochée. */
function attributs(s) {
  const a = {}; const re = /([\w:-]+)(?:\s*=\s*"([^"]*)")?/g; let m;
  while ((m = re.exec(s))) {
    a[m[1].toLowerCase()] = m[2] === undefined ? '' : m[2].replace(/&quot;/g, '"')
      .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
  }
  return a;
}
function controles(html) {
  const out = []; let m;
  const ri = /<input\b([^>]*)>/g;
  while ((m = ri.exec(html))) {
    const a = attributs(m[1]);
    out.push({ pos: m.index, balise: 'input', id: a.id || '', type: a.type || 'text',
               attrs: a, valeur: a.value || '', coche: 'checked' in a });
  }
  const rs = /<select\b([^>]*)>([\s\S]*?)<\/select>/g;
  while ((m = rs.exec(html))) {
    const a = attributs(m[1]); const opts = []; let o;
    const ro = /<option\b([^>]*)>/g;
    while ((o = ro.exec(m[2]))) opts.push(attributs(o[1]));
    const choisie = opts.filter(function (x) { return 'selected' in x; })[0] || opts[0];
    out.push({ pos: m.index, balise: 'select', id: a.id || '', attrs: a,
               options: opts.map(function (x) { return x.value; }),
               valeur: choisie ? choisie.value : '' });
  }
  return out.sort(function (x, y) { return x.pos - y.pos; });
}
function affiche(id) {
  const e = document.getElementById(id);
  return e ? controles(e.innerHTML) : null;
}

/* LES RÉPONSES, PAR LES VRAIS GESTIONNAIRES DES CHAMPS. */
const R = {
  porte_nis2: REFS.nis2.hors_taille[0].cle,
  gouv_nis2: REFS.nis2.gouvernance[0].cle,
  exigence_cra: REFS.cra.exigences.I[0][0],
  porte_dora: REFS.dora.qualification.simplifie[0].cle,
  seuil_dora: REFS.dora.incident.seuils[0].cle,
  exclusion_dora: REFS.dora.supervision.exclusions[0].cle,
};
const REPONDRE = {
  nis2() {
    nis2Champ('secteur', 'energie'); nis2Champ('effectif', '300');
    nis2Champ('ca', '60'); nis2Champ('bilan', '50');
    nis2Porte(R.porte_nis2, true);
    nis2Mesure('a', 'conforme'); nis2Gouv(R.gouv_nis2, 'conforme');
    document.getElementById('nis2-ca').value = '450';
    document.getElementById('recyf-statut-sel').value = 'essentielle';
    recyfEtat(1, { value: 'atteint' });
    recyfCoche('gouvernance', true); recyfCoche('moyens_alloues', true);
    recyfEntree('pssi', true); recyfReexamen('12');
  },
  iso27001() {
    iso27Perimetre('SI de production du siège');
    iso27Critere('etabli_le', '2026-01-10'); iso27Critere('apprecie_le', '2026-02-01');
    iso27AjouterRisque(); iso27Risque(0, 'nom', 'Rançongiciel');
    iso27Risque(0, 'proprietaire', 'DSI');
    iso27Decision('5.1', 'retenue'); iso27Justifier('5.1', 'Politique en place');
    iso27Article('4.1', 'conforme');
  },
  iso42001() {
    isoArticle('4.1', 'conforme');
    isoDecision('A.2.2', 'retenue'); isoJustifier('A.2.2', 'Politique IA signée');
  },
  cra() {
    document.getElementById('cra-nom').value = 'Routeur R1';
    craAjouter();
    craRoleCoche({ getAttribute() { return 'je_concois'; }, checked: true });
    craCoter({ getAttribute() { return R.exigence_cra; }, value: 'conforme' });
    document.getElementById('cra-ca').value = '45';
  },
  dora() {
    doraChamp('entite', 'etablissement_credit'); doraChamp('identifiee_nis2', 'oui');
    doraPorte(R.porte_dora, true);
    doraEtat(5, 'tenu');
    doraContrat('fonction_critique', 'oui'); doraContrat('microentreprise', true);
    doraClause('2_a', 'presente');
    doraInc('criticite', 'oui'); doraSeuil(R.seuil_dora, true);
    doraInc('connaissance', '2026-03-01T10:00');
    doraIso('iso27001_certifie', 'oui');
    doraSup(R.exclusion_dora, true); doraSupN('eism', '3');
    doraSupPart('part_nombre', '12');
  },
};
const out = {};
chargerPage();
"""

_FIN = r"""
})().then(function () {
  process.stdout.write(JSON.stringify(out));
  process.exit(0);
}).catch(function (e) {
  process.stderr.write(String(e && e.stack || e));
  process.exit(3);
});
"""


def _executer(scenario):
    if not NODE:
        pytest.skip("node absent : les écrans ne peuvent pas être exécutés")
    with tempfile.TemporaryDirectory() as d:
        h = os.path.join(d, "h.js")
        r_ = os.path.join(d, "refs.json")
        io.open(r_, "w", encoding="utf-8").write(json.dumps(_refs()))
        io.open(h, "w", encoding="utf-8").write(
            _SOCLE + "(async function () {\n" + scenario + _FIN)
        r = subprocess.run([NODE, h, PAGE_JS, r_, PAGE_HTML],
                           capture_output=True, text=True, timeout=90)
    if r.returncode != 0:
        pytest.fail("le scénario n'a pas tourné :\n%s" % (r.stderr or "")[-2500:])
    return json.loads(r.stdout)


def _champ(controles, **attendu):
    """LE champ dont les attributs portent ces valeurs (ou ces morceaux)."""
    for c in controles or []:
        ok = True
        for k, v in attendu.items():
            if k == "onchange_contient":
                ok = ok and v in c["attrs"].get("onchange", "")
            elif k == "balise":
                ok = ok and c["balise"] == v
            else:
                ok = ok and c["attrs"].get(k.replace("_", "-")) == v
        if ok:
            return c
    raise AssertionError("aucun champ ne porte %r parmi %d" % (attendu, len(controles or [])))


# ══════════════════════════════════════════════════════════════════════════
#  1. APRÈS RECHARGEMENT, LE RAIL ET LE TAUX LISENT LES MÊMES RÉPONSES
# ══════════════════════════════════════════════════════════════════════════

#: CE QUE CHAQUE DÉCLARATION DOIT PORTER APRÈS LA SAISIE — la preuve que la
#: comparaison avant/après ne compare pas deux déclarations vides.
TEMOINS = {
    "nis2": ['"secteur":"energie"', '"effectif":300', '"chiffre_affaires":450000000',
             '"statut":"essentielle"', '"1":"atteint"', '"a":"conforme"'],
    "iso27001": ['"perimetre":"SI de production du siège"', '"Rançongiciel"',
                 '"etabli_le":"2026-01-10"', '"4.1":"conforme"', '"decision":"retenue"'],
    "iso42001": ['"4.1":"conforme"', '"A.2.2"', '"justification":"Politique IA signée"'],
    "cra": ['"Routeur R1"', '"je_concois":true', '"conforme"', '"chiffre_affaires":45'],
    "dora": ['"entite":"etablissement_credit"', '"identifiee_nis2":true', '"5":"tenu"',
             '"fonction_critique":true', '"services_critiques":true',
             '"iso27001_certifie":true', '"eism":3'],
}


@pytest.mark.parametrize("norme", sorted(TEMOINS))
def test_apres_rechargement_le_rail_et_le_taux_lisent_les_memes_declarations(norme):
    """LE POINT QUI DÉCIDE. Le rail et le taux lisent tous deux
    `declarationsDesEcrans()`. Si elle est la même avant et après le
    rechargement, le rail ne repart pas de « Suis-je concerné ? » et la
    carte du taux ne retombe pas à « — »."""
    o = _executer("""
      REPONDRE[%(n)s]();
      out.avant = JSON.stringify(declarationsDesEcrans()[%(n)s]);
      recharger();
      out.apres = JSON.stringify(declarationsDesEcrans()[%(n)s]);
    """ % {"n": json.dumps(norme)})
    for t in TEMOINS[norme]:
        assert t in o["avant"], "la saisie n'a pas atteint la déclaration : %s absent de %s" % (
            t, o["avant"][:400])
    assert o["apres"] == o["avant"], (
        "après rechargement, %s ne déclare plus la même chose :\navant %s\naprès %s"
        % (norme, o["avant"][:600], o["apres"][:600]))


def test_chaque_referentiel_du_rail_garde_ses_reponses_quelque_part():
    """LA RÈGLE DE COUVERTURE. Un onzième référentiel branché sur le rail sans
    mémoire perdrait ses réponses au rechargement — exactement le défaut
    mesuré. Chaque norme du rail (et DORA, qui a le sien) est soit dans la
    mémoire des écrans, soit dans la liste de ce qui gardait déjà ses
    réponses."""
    o = _executer("""
      out.rail = Object.keys(RAIL_DECL).concat(['dora']);
      out.memoire = Object.keys(MEMOIRE).map(function (k) { return MEMOIRE[k].norme; });
      out.cles = {};
      Object.keys(MEMOIRE).forEach(function (k) { out.cles[k] = MEMOIRE[k].cle; });
    """)
    sans = [n for n in o["rail"] if n not in o["memoire"] and n not in DEJA_GARDES]
    assert not sans, "référentiels du rail qui perdent leurs réponses : %s" % sans
    assert o["cles"] == CLES, o["cles"]


# ══════════════════════════════════════════════════════════════════════════
#  2. LES CHAMPS AFFICHÉS PORTENT LES RÉPONSES — APRÈS RECHARGEMENT
# ══════════════════════════════════════════════════════════════════════════

def test_NIS2_la_qualification_est_reaffichee():
    o = _executer("""
      REPONDRE.nis2(); recharger();
      NIS2_REF = REFS.nis2; nis2RemplirChamps();
      out.q = affiche('nis2-q');
      out.ca = document.getElementById('nis2-ca').value;
      window.nis2PeindreMesures(); out.mes = affiche('nis2-mesures-body');
      window.nis2PeindreGouvernance(); out.gouv = affiche('nis2-gouv-body');
      out.porte = R.porte_nis2; out.g = R.gouv_nis2;
    """)
    q = o["q"]
    assert _champ(q, id="nis2-secteur")["valeur"] == "energie"
    assert _champ(q, id="nis2-eff")["valeur"] == "300"
    assert _champ(q, id="nis2-ca2")["valeur"] == "60"
    assert _champ(q, id="nis2-bilan")["valeur"] == "50"
    assert _champ(q, onchange_contient="nis2Porte('%s'" % o["porte"])["coche"], (
        "la porte hors taille déclarée est décochée après rechargement")
    assert o["ca"] == "450", "le chiffre d'affaires du groupe est vide : %r" % o["ca"]
    assert _champ(o["mes"], onchange_contient="nis2Mesure('a'")["valeur"] == "conforme"
    assert _champ(o["gouv"], onchange_contient="nis2Gouv('%s'" % o["g"])["valeur"] == "conforme"


def test_RECYF_la_qualification_et_l_objectif_16_sont_reaffiches():
    o = _executer("""
      REPONDRE.nis2(); recharger();
      RECYF_REF = REFS.recyf.referentiel;
      out.statut = document.getElementById('recyf-statut-sel').value;
      out.etats = RECYF_ETATS;
      document.getElementById('recyf-analyse-body').innerHTML =
        recyfRenduAnalyse(REFS.recyf_analyse);
      out.a = affiche('recyf-analyse-body');
    """)
    assert o["statut"] == "essentielle", o["statut"]
    assert o["etats"] == {"1": "atteint"}, o["etats"]
    a = o["a"]
    for id_ in ("recyf-a-gouvernance", "recyf-moyens", "recyf-e-pssi"):
        assert _champ(a, id=id_)["coche"], "%s décochée après rechargement" % id_
    assert not _champ(a, id="recyf-e-ecosysteme")["coche"], (
        "une entrée jamais cochée l'est après rechargement")
    assert _champ(a, id="recyf-reexamen-mois")["valeur"] == "12"


def test_RECYF_une_case_cochee_le_reste_au_repeint_suivant():
    """LE DÉFAUT DE SESSION, MESURÉ AU NAVIGATEUR : cocher « moyens alloués »
    repeignait l'écran, et le repeint rendait la case décochée — la réponse
    suivante l'envoyait donc à `false`, et la gouvernance retombait de
    « acquis » à « déclaré »."""
    o = _executer("""
      RECYF_REF = REFS.recyf.referentiel;
      document.getElementById('recyf-statut-sel').value = 'essentielle';
      recyfCoche('gouvernance', true);
      recyfCoche('moyens_alloues', true);
      document.getElementById('recyf-analyse-body').innerHTML =
        recyfRenduAnalyse(REFS.recyf_analyse);
      out.a = affiche('recyf-analyse-body');
      out.envoi = recyfDeclarationAnalyse();
    """)
    assert _champ(o["a"], id="recyf-moyens")["coche"], "« moyens alloués » décochée par le repeint"
    assert o["envoi"]["moyens_alloues"] is True and o["envoi"]["gouvernance"] is True, o["envoi"]


def test_ISO27001_le_perimetre_et_les_deux_dates_sont_reaffiches():
    o = _executer("""
      REPONDRE.iso27001(); recharger();
      ISO27_REF = REFS.iso27001; iso27RemplirCriteres();
      out.c = affiche('iso27-criteres');
      out.risques = ISO27_ETAT.risques;
    """)
    c = o["c"]
    assert _champ(c, id="iso27-perimetre")["valeur"] == "SI de production du siège"
    assert _champ(c, id="iso27-etabli")["valeur"] == "2026-01-10"
    assert _champ(c, id="iso27-apprecie")["valeur"] == "2026-02-01"
    assert [r.get("nom") for r in o["risques"]] == ["Rançongiciel"], o["risques"]


def test_CRA_le_role_l_ecart_et_le_registre_sont_reaffiches():
    o = _executer("""
      REPONDRE.cra(); recharger();
      CRA_REF = REFS.cra; craRolePeindre(); out.role = affiche('cra-role-q');
      craEcarts(); out.ecarts = affiche('cra-ec-body');
      out.produits = CRA_ETAT.produits.map(function (p) { return p.nom; });
      out.ca = document.getElementById('cra-ca').value;
      out.ex = R.exigence_cra;
    """)
    assert _champ(o["role"], data_q="je_concois")["coche"], "la question du rôle est décochée"
    assert _champ(o["ecarts"], data_ex=o["ex"])["valeur"] == "conforme", (
        "l'exigence cotée est affichée « non renseigné »")
    assert o["produits"] == ["Routeur R1"], o["produits"]
    assert o["ca"] == "45", o["ca"]


def test_CRA_revenir_sur_l_analyse_d_ecart_montre_l_exigence_cotee():
    """LE DÉFAUT DE SESSION : chaque ouverture d'un écran du CRA repeint
    l'analyse d'écart, et le repeint remettait les listes à « non
    renseigné »."""
    o = _executer("""
      CRA_REF = REFS.cra;
      craCoter({ getAttribute() { return R.exigence_cra; }, value: 'partiel' });
      craEcarts(); out.ecarts = affiche('cra-ec-body'); out.ex = R.exigence_cra;
    """)
    assert _champ(o["ecarts"], data_ex=o["ex"])["valeur"] == "partiel"


def test_DORA_la_qualification_est_reaffichee():
    o = _executer("""
      REPONDRE.dora(); recharger();
      DORA_REF = REFS.dora; doraRemplirChamps(); out.q = affiche('dora-q');
      out.iso = document.getElementById('dora-iso-certifie')
        ? document.getElementById('dora-iso-certifie').value : null;
      out.porte = R.porte_dora;
    """)
    assert _champ(o["q"], id="dora-entite")["valeur"] == "etablissement_credit"
    assert _champ(o["q"], id="dora-nis2")["valeur"] == "oui"
    assert _champ(o["q"], onchange_contient="doraPorte('%s'" % o["porte"])["coche"]
    assert o["iso"] == "oui", (
        "la réponse « certifié ISO 27001 » n'est pas réaffichée : %r" % o["iso"])


def test_DORA_le_cadre_de_risque_montre_les_articles_declares():
    """LE DÉFAUT DE SESSION : chaque ouverture de l'écran repeignait les
    quarante articles à « non déclaré », pendant que l'état — et le taux —
    tenaient les réponses."""
    o = _executer("""
      REPONDRE.dora(); recharger();
      DORA_REF = REFS.dora; DORA_REGIME = 'complet';
      doraPeindreRisque(); out.r = affiche('dora-risque-body');
    """)
    assert _champ(o["r"], onchange_contient="doraEtat(5,")["valeur"] == "tenu"
    autres = [c["valeur"] for c in o["r"] if "doraEtat(" in c["attrs"].get("onchange", "")
              and "doraEtat(5," not in c["attrs"]["onchange"]]
    assert autres and set(autres) == {""}, "des articles jamais déclarés le sont : %s" % autres


def test_DORA_contrats_incident_et_supervision_sont_reaffiches():
    o = _executer("""
      REPONDRE.dora(); recharger();
      DORA_REF = REFS.dora;
      doraPeindreTiers(); out.t = affiche('dora-contrat-form');
      doraPeindreIncident(); out.i = affiche('dora-incident-form');
      doraPeindreSup(); out.s = affiche('dora-sup-form');
      out.seuil = R.seuil_dora; out.excl = R.exclusion_dora;
    """)
    assert _champ(o["t"], onchange_contient="doraContrat('fonction_critique'")["valeur"] == "oui"
    assert _champ(o["t"], onchange_contient="doraContrat('microentreprise'")["coche"]
    assert _champ(o["i"], onchange_contient="doraInc('criticite'")["valeur"] == "oui"
    assert _champ(o["i"], onchange_contient="doraSeuil('%s'" % o["seuil"])["coche"]
    assert _champ(o["i"], onchange_contient="doraInc('connaissance'")["valeur"] == "2026-03-01T10:00"
    assert _champ(o["s"], onchange_contient="doraSup('%s'" % o["excl"])["coche"]
    assert _champ(o["s"], onchange_contient="doraSupN('eism'")["valeur"] == "3"
    assert _champ(o["s"], onchange_contient="doraSupPart('part_nombre'")["valeur"] == "12"


def test_DORA_le_regime_se_recalcule_quand_on_rouvre_un_ecran_qui_en_depend():
    """LE RÉGIME N'EST PAS GARDÉ : le serveur le recalcule. Mais un écran qui
    en dépend, rouvert après rechargement, disait « le régime n'est pas
    déterminé » à qui l'avait déterminé la veille."""
    o = _executer("""
      REPONDRE.dora(); recharger();
      DORA_REF = REFS.dora; page.actif = 'p-dora-risque';
      doraPeindreCourant();
      out.appels = page.appels;
      out.corps = document.getElementById('dora-risque-body').innerHTML;
    """)
    assert "/api/dora/qualifier" in o["appels"], o["appels"]
    assert "pas déterminé" not in o["corps"], o["corps"][:200]


# ══════════════════════════════════════════════════════════════════════════
#  3. CE QUE LA MÉMOIRE REFUSE, ET QUAND ELLE ÉCRIT
# ══════════════════════════════════════════════════════════════════════════

def test_une_memoire_illisible_ne_coute_que_son_propre_ecran():
    o = _executer("""
      REPONDRE.nis2(); REPONDRE.iso27001(); quitter();
      localStorage.setItem('cp-sentinel-nis2-v1', '{pas du json');
      chargerPage();
      out.secteur = NIS2_ETAT.secteur;
      out.perimetre = ISO27_ETAT.perimetre;
    """)
    assert o["secteur"] == "", o["secteur"]
    assert o["perimetre"] == "SI de production du siège", o["perimetre"]


def test_une_valeur_d_un_autre_type_est_ecartee_pas_recopiee():
    """UN « mesures » DEVENU UNE CHAÎNE ferait tomber la peinture de l'écran
    entier ; un effectif écrit en texte serait envoyé tel quel au moteur. Une
    mémoire écrite par une version antérieure, ou abîmée, ne doit coûter que
    les valeurs abîmées — entrée par entrée."""
    o = _executer("""
      localStorage.setItem('cp-sentinel-nis2-v1', JSON.stringify({
        etat: { secteur: 'energie', effectif: '300', ca: 60, mesures: 'conforme',
                portes: { a: true, b: 'oui' }, gouvernance: { x: 'conforme', y: 3 } },
        ca_groupe: 450 }));
      localStorage.setItem('cp-sentinel-recyf-v1', JSON.stringify({
        analyse: { moyens_alloues: 'oui', gouvernance: true, entrees: ['pssi', 3] } }));
      localStorage.setItem('cp-sentinel-iso27001-v1', JSON.stringify({
        perimetre: 42, risques: [{ nom: 'R' }, 'S', null],
        criteres: { seuil_acceptation: null, etabli_le: '2026-01-10' },
        mesures: { '5.1': { decision: 'retenue' }, '5.2': 'retenue' } }));
      localStorage.setItem('cp-sentinel-cra-v1', JSON.stringify({
        produits: [{ nom: 'A' }, 'B', [1]] }));
      localStorage.setItem('cp-sentinel-dora-v1', JSON.stringify({
        decl: { entite: 'etablissement_credit', identifiee_nis2: 'oui' } }));
      chargerPage();
      out.etat = NIS2_ETAT; out.ca = document.getElementById('nis2-ca').value;
      out.analyse = RECYF_ANALYSE; out.iso = ISO27_ETAT; out.cra = CRA_ETAT.produits;
      out.dora = DORA_DECL;
    """)
    e = o["etat"]
    assert e["secteur"] == "energie" and e["ca"] == 60, e
    assert e["effectif"] is None, "un effectif en texte a été recopié : %r" % e["effectif"]
    assert e["mesures"] == {}, e["mesures"]
    assert e["portes"] == {"a": True}, e["portes"]
    assert e["gouvernance"] == {"x": "conforme"}, e["gouvernance"]
    assert o["ca"] == "", "un nombre a été posé dans le champ texte : %r" % o["ca"]
    a = o["analyse"]
    assert a["gouvernance"] is True and a["moyens_alloues"] is False, a
    assert a["entrees"] == ["pssi"], a["entrees"]
    i = o["iso"]
    assert i["perimetre"] == "", "un périmètre numérique a été recopié : %r" % i["perimetre"]
    assert i["criteres"]["seuil_acceptation"] == 6 and i["criteres"]["etabli_le"] == "2026-01-10", (
        "un seuil vide a remplacé le seuil par défaut : %r" % i["criteres"])
    assert i["risques"] == [{"nom": "R"}], i["risques"]
    assert i["mesures"] == {"5.1": {"decision": "retenue"}}, i["mesures"]
    assert o["cra"] == [{"nom": "A"}], o["cra"]
    assert o["dora"]["entite"] == "etablissement_credit" and o["dora"]["identifiee_nis2"] is None, o["dora"]


def test_un_stockage_refuse_ne_casse_ni_le_chargement_ni_les_reponses():
    o = _executer("""
      REFUS = true;
      chargerPage(); REPONDRE.nis2(); quitter();
      out.secteur = NIS2_ETAT.secteur;
    """)
    assert o["secteur"] == "energie"


def test_rien_n_est_ecrit_tant_que_rien_n_a_ete_repondu():
    """OUVRIR SENTINEL NE DOIT PAS REMPLIR LE STOCKAGE DE FORMULAIRES VIDES."""
    o = _executer("""
      evenement('click'); await attendre(350); quitter();
      out.cles = Object.keys(magasin);
    """)
    assert not [k for k in o["cles"] if k in CLES.values()], o["cles"]


def test_une_reponse_est_ecrite_APRES_son_gestionnaire():
    """L'ÉCOUTEUR EST EN CAPTURE : il passe avant le gestionnaire du champ.
    Écrire tout de suite enregistrerait l'état d'AVANT la réponse."""
    o = _executer("""
      evenement('change');
      nis2Champ('secteur', 'energie');
      await attendre(400);
      out.brut = magasin['cp-sentinel-nis2-v1'] || '';
    """)
    assert '"secteur":"energie"' in o["brut"], o["brut"][:300]


def test_une_reponse_suivie_d_un_rechargement_immediat_n_est_pas_perdue():
    """LE QUART DE SECONDE D'ATTENTE a un revers : recharger dedans perdrait
    la dernière réponse. La page qui part l'écrit."""
    o = _executer("""
      evenement('change');
      nis2Champ('secteur', 'energie');
      recharger();
      out.secteur = NIS2_ETAT.secteur;
    """)
    assert o["secteur"] == "energie", o["secteur"]


# ══════════════════════════════════════════════════════════════════════════
#  4. GARDER A UN PRIX : ON PEUT EFFACER, ÉCRAN PAR ÉCRAN
# ══════════════════════════════════════════════════════════════════════════

def test_effacer_NIS2_efface_NIS2_et_ReCyF_et_rien_d_autre():
    """QUI REMPLIT NIS 2 POUR UNE ENTITÉ, PUIS POUR UNE AUTRE, sur le même
    poste, retrouverait la première. L'effacement porte sur les réponses ET
    sur les marques « lu » et « passé en revue » du rail de ce référentiel —
    et la page qui part ne les réécrit pas."""
    o = _executer("""
      REPONDRE.nis2(); REPONDRE.iso27001(); quitter();
      localStorage.setItem('cp-sentinel-rail-v1', JSON.stringify(
        { nis2: { lus: ['nis2-signalement'] }, iso27001: { lus: ['iso27001-millesime'] } }));
      chargerPage();
      /* DEUX RÉPONSES QUI N'ONT PAS ENCORE ÉTÉ ÉCRITES, au moment du clic. */
      nis2Champ('secteur', 'transports');
      iso27Perimetre('Le siège et ses deux filiales');
      memoireEffacer('nis2');
      out.recharge = page.recharge;
      quitter();
      out.cles = Object.keys(magasin);
      out.iso = magasin['cp-sentinel-iso27001-v1'] || '';
      out.rail = JSON.parse(magasin['cp-sentinel-rail-v1']);
    """)
    assert o["recharge"] == 1, "la page n'est pas rechargée"
    assert CLES["nis2"] not in o["cles"], (
        "la réponse NIS 2 en attente a ressuscité ce qu'on venait d'effacer")
    assert CLES["recyf"] not in o["cles"], "ReCyF n'est pas effacé avec NIS 2"
    assert "Le siège et ses deux filiales" in o["iso"], (
        "effacer NIS 2 a coûté à ISO 27001 sa dernière réponse")
    assert "nis2" not in o["rail"] and "iso27001" in o["rail"], o["rail"]


def test_effacer_demande_confirmation():
    o = _executer("""
      REPONDRE.nis2(); quitter(); chargerPage();
      global.confirm = function () { return false; };
      memoireEffacer('nis2');
      out.cles = Object.keys(magasin); out.recharge = page.recharge;
    """)
    assert CLES["nis2"] in o["cles"] and o["recharge"] == 0


@pytest.mark.parametrize("norme,panneau", [
    ("nis2", "nis2-qualifier"), ("iso27001", "iso27001-risques"),
    ("iso42001", "iso42001"), ("cra", "cra-role"), ("dora", "dora-qualifier")])
def test_le_premier_ecran_de_chaque_referentiel_dit_ou_sont_les_reponses(norme, panneau):
    """DIRE OÙ SONT LES RÉPONSES, ET COMMENT LES EFFACER, sur l'écran où l'on
    commence à répondre."""
    debut = HTML.index('<div class="page" id="p-%s">' % panneau)
    fin = HTML.index('<div class="page"', debut + 10)
    bloc = HTML[debut:fin]
    assert "memoireEffacer('%s')" % norme in bloc, "aucun bouton d'effacement sur p-%s" % panneau
    assert "ce navigateur" in bloc, "p-%s ne dit pas où sont gardées les réponses" % panneau
