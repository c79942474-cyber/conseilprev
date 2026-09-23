# -*- coding: utf-8 -*-
"""LES BULLES D'AIDE DE SENTINEL S'OUVRENT AU DOIGT — PAS SEULEMENT À LA SOURIS.

LE DÉFAUT SIGNALÉ. « Ailleurs dans Sentinel, les bulles d'aide ne s'ouvrent
qu'à la souris, pas au toucher. » Le mécanisme partagé (/infobulles.js) ne
connaissait que les bulles écrites dans un ATTRIBUT. Sentinel en porte quatre
autres familles dont le texte est un ÉLÉMENT ENFANT, révélé par `A:hover B` :
maturité, modèles, tarification, budget — cent quatre-vingt-sept
déclencheurs, aucun reconnu.

CE QUE LA MESURE « AVANT » A TROUVÉ, au navigateur, en contexte tactile
(recette_bulles_sentinel.js, 49 contrôles en échec sur 103) :
  · les 118 badges d'article n'ouvraient JAMAIS leur bulle : chacun est posé
    dans une carte cliquable, et l'appui ouvrait la fiche du document ;
  · le « ? » d'une formule CHOISISSAIT la formule, celui d'un libellé de
    champ donnait le focus au champ — la bulle ne s'ouvrait pas ;
  · les trois autres familles s'ouvraient, mais par ACCIDENT — un survol ou
    un focus que Chromium laisse collés à l'élément touché — et ce même
    accident les empêchait de se refermer : opacité 1 après le second appui,
    1 après Échap ;
  · aucune n'était annoncée ; maturité et modèles n'étaient pas atteignables
    au clavier.

ET UN DÉFAUT QUE PERSONNE N'AVAIT SIGNALÉ, TROUVÉ EN RELISANT LE SOCLE. Collée
derrière la liste « [data-tooltip],[data-tip] », la pseudo-classe
`:focus-visible` ne visait que la DERNIÈRE partie : la première restait
`[data-tooltip]` tout court. Mesuré au navigateur : les trente-deux
infobulles de l'accueil — cartes, boutons de navigation, flèches de
défilement — portaient au repos un contour de 2 px.

CES RÈGLES EXÉCUTENT LE SCRIPT, ELLES NE LE LISENT PAS SEULEMENT. Le harnais
charge le VRAI /infobulles.js dans node, sur les VRAIES feuilles de la page
(ses blocs <style>, règle par règle, comme `cssRules` les donne), avec un DOM
réduit à ce que le script touche. On lit ce qu'il publie, et ce qu'il fait
d'un appui, d'un clic, d'un focus et d'Échap. La recette mesure le reste au
navigateur : la géométrie, le survol collé réel, le clavier réel.
"""
import functools
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
from html.parser import HTMLParser

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = shutil.which("node")


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


SCRIPT = _lire("infobulles.js")
SENTINEL = _lire("sentinel.html")
PAGE_JS = _lire("sentinel.page.js")
INDEX = _lire("index.html")

#: LES QUATRE FAMILLES QUE LA RECETTE A RECENSÉES À L'ÉCRAN — [déclencheur,
#: bulle]. Elles sont écrites ICI, et nulle part dans le script : lui les
#: reconnaît à ce qu'elles font. C'est ce que la règle 1 vérifie.
FAMILLES = (
    ("mat-tooltip-wrap", "mat-tooltip"),
    ("tmpl-art-badge", "tmpl-tip"),
    ("prx-tip-icon", "prx-tip-bubble"),
    ("bud-tip", "bud-tip-bubble"),
)
OUVERTE, FERMEE = "bulle-ouverte", "bulle-fermee"
ETEINT = {"display": "none", "visibility": "hidden", "opacity": "0", "content": "none"}


# ══════════════════════════════════════════════════════════════════════════
#  LE HARNAIS — le vrai script, les vraies feuilles, un DOM minuscule
# ══════════════════════════════════════════════════════════════════════════

_HARNAIS = r"""
"use strict";
const fs = require("fs");
const [, , SCRIPT, PAGE, PARAMS] = process.argv;
const src = fs.readFileSync(SCRIPT, "utf8");
const html = fs.readFileSync(PAGE, "utf8");
const familles = JSON.parse(fs.readFileSync(PARAMS, "utf8"));

/* Coupe au séparateur de PREMIER niveau : ni dans des parenthèses, ni dans
   des crochets, ni entre guillemets. */
function couper(txt, sep) {
  const out = []; let prof = 0, q = "", d = 0;
  for (let i = 0; i < txt.length; i++) {
    const c = txt[i];
    if (q) { if (c === q && txt[i - 1] !== "\\") q = ""; continue; }
    if (c === '"' || c === "'") q = c;
    else if (c === "(" || c === "[") prof++;
    else if (c === ")" || c === "]") prof--;
    else if (c === sep && prof === 0) { out.push(txt.slice(d, i)); d = i + 1; }
  }
  out.push(txt.slice(d));
  return out;
}

/* Une déclaration comme le CSSOM la rend : la DERNIÈRE valeur d'une
   propriété l'emporte, `!important` ôté de la valeur. */
function style(decl) {
  const props = [];
  for (const d of couper(decl, ";")) {
    const k = d.indexOf(":"); if (k < 0) continue;
    const nom = d.slice(0, k).trim().toLowerCase();
    let v = d.slice(k + 1).trim();
    const imp = /!\s*important\s*$/i.test(v);
    v = v.replace(/!\s*important\s*$/i, "").trim();
    if (nom) props.push([nom, v, imp]);
  }
  return {
    getPropertyValue(p) { let r = ""; props.forEach(([n, v]) => { if (n === p) r = v; }); return r; },
    get cssText() { return props.map(([n, v, i]) => n + ": " + v + (i ? " !important" : "") + ";").join(" "); },
  };
}

/* Les règles de PREMIER NIVEAU d'une feuille : c'est tout ce que `cssRules`
   rend avec un `selectorText`. Un bloc @media est sauté entier. */
function regles(css) {
  css = css.replace(/\/\*[\s\S]*?\*\//g, "").replace(/@(import|charset|namespace)[^;{]*;/g, "");
  const out = []; let i = 0;
  while (i < css.length) {
    const o = css.indexOf("{", i); if (o < 0) break;
    const sel = css.slice(i, o).trim();
    let prof = 1, j = o + 1, q = "";
    for (; j < css.length && prof; j++) {
      const c = css[j];
      if (q) { if (c === q && css[j - 1] !== "\\") q = ""; continue; }
      if (c === '"' || c === "'") q = c;
      else if (c === "{") prof++;
      else if (c === "}") prof--;
    }
    if (sel && sel[0] !== "@") out.push({ selectorText: sel.replace(/\s+/g, " "), style: style(css.slice(o + 1, j - 1)) });
    i = j;
  }
  return out;
}

/* ── UN DOM RÉDUIT À CE QUE LE SCRIPT TOUCHE. Les sélecteurs qu'il sait
   lire sont les SIMPLES — `.classe`, `[attribut]`, `balise`, `:hover` ; tout
   autre sélecteur LÈVE une erreur, pour qu'un contrôle ne passe jamais sur
   un sélecteur qu'il n'a pas su lire. */
function El(tag, classes, attrs) {
  this.tagName = String(tag).toUpperCase(); this.parentElement = null; this.enfants = [];
  this.attrs = Object.assign({}, attrs || {}); this.textContent = ""; this.id = "";
  this.cls = new Set(classes || []); this.survole = false;
  const moi = this;
  this.classList = { add: c => moi.cls.add(c), remove: c => moi.cls.delete(c), contains: c => moi.cls.has(c) };
}
El.prototype.getAttribute = function (k) { return k in this.attrs ? this.attrs[k] : null; };
El.prototype.hasAttribute = function (k) { return k in this.attrs; };
El.prototype.setAttribute = function (k, v) { this.attrs[k] = String(v); };
El.prototype.appendChild = function (e) { e.parentElement = this; this.enfants.push(e); return e; };
El.prototype.simple = function (s) {
  s = s.trim(); let m;
  if (s === ":hover") return this.survole;
  if ((m = /^\[([\w-]+)\]$/.exec(s))) return this.hasAttribute(m[1]);
  if ((m = /^\.([\w-]+)$/.exec(s))) return this.cls.has(m[1]);
  if ((m = /^([a-z]+)$/i.exec(s))) return this.tagName === m[1].toUpperCase();
  throw new Error("sélecteur hors du harnais : " + s);
};
El.prototype.matches = function (sel) { return couper(sel, ",").some(s => this.simple(s)); };
El.prototype.closest = function (sel) {
  for (let e = this; e; e = e.parentElement) if (e.matches(sel)) return e;
  return null;
};
El.prototype.querySelector = function (sel) {
  for (const c of this.enfants) { if (c.matches(sel)) return c; const r = c.querySelector(sel); if (r) return r; }
  return null;
};
El.prototype.contains = function (o) { for (let e = o; e; e = e.parentElement) if (e === this) return true; return false; };
function tous(e) { return [e].concat(...e.enfants.map(tous)); }

const racine = new El("html"), head = racine.appendChild(new El("head")), body = racine.appendChild(new El("body"));
const ecouteurs = {};
const document = {
  readyState: "complete",
  styleSheets: [...html.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/gi)].map(m => ({ cssRules: regles(m[1]) })),
  head, body, documentElement: racine, activeElement: body,
  getElementById: id => tous(racine).find(e => e.id === id) || null,
  createElement: tag => new El(tag),
  querySelectorAll(sel) {
    if (sel === ":hover") return tous(racine).filter(e => e.survole);
    return tous(racine).filter(e => { try { return e.matches(sel); } catch (x) { return false; } });
  },
  addEventListener(type, fn) { (ecouteurs[type] = ecouteurs[type] || []).push(fn); },
};
const window = { innerWidth: 1280, addEventListener(type, fn) { (ecouteurs["w:" + type] = ecouteurs["w:" + type] || []).push(fn); } };
function MutationObserver() { return { observe() {} }; }
function emettre(type, ev) { (ecouteurs[type] || []).forEach(fn => fn(ev)); return ev; }
function evenement(extra) {
  const ev = Object.assign({ retenu: false, arrete: false }, extra);
  ev.preventDefault = () => { ev.retenu = true; };
  ev.stopPropagation = () => { ev.arrete = true; };
  return ev;
}

new Function("window", "document", "MutationObserver", src)(window, document, MutationObserver);

const api = window.infobulles;
const publiee = document.getElementById("css-bulle-ouverte");
const annonce = () => (document.getElementById("bulle-annonce") || {}).textContent || "";
const etat = el => ({ ouverte: el.cls.has("bulle-ouverte"), fermee: el.cls.has("bulle-fermee") });
const out = { css: publiee ? publiee.textContent : null, selecteur: api.selecteur,
              enfants: api.enfants || null, familles: {} };

/* ── LES SCÉNARIOS, famille par famille : un déclencheur et sa bulle. */
for (const [a, b] of familles) {
  const r = out.familles[a] = {};
  const neuf = (attrs) => {
    const t = new El("span", [a], attrs); const bulle = new El("span", [b]);
    bulle.textContent = "  Texte de la bulle\n  " + a + "  ";
    t.appendChild(bulle); body.appendChild(t); return t;
  };
  try {
    // 1. L'API : ouvrir annonce le texte de la bulle ENFANT ; rouvrir referme À LA DEMANDE.
    let t = neuf();
    api.ouvrir(t); r.annonce = annonce(); r.premier = etat(t);
    api.ouvrir(t); r.second = etat(t);
    api.ouvrir(t); r.troisieme = etat(t);
    api.fermer();

    // 2. Échap quand le déclencheur a le FOCUS : fermé, et le focus n'a pas bougé.
    t = neuf(); document.activeElement = t;
    emettre("keydown", evenement({ key: "Escape" }));
    r.echapFocus = etat(t); r.focusGarde = document.activeElement === t;
    // …la fermeture TOMBE quand le focus part sans survol derrière lui…
    emettre("focusout", evenement({ target: t, relatedTarget: body }));
    r.apresDepart = etat(t);
    // …et TIENT quand un survol collé reste (le libellé qui donne le focus à son champ).
    document.activeElement = t; t.survole = true;
    emettre("keydown", evenement({ key: "Escape" }));
    emettre("focusout", evenement({ target: t, relatedTarget: body }));
    r.departSousSurvol = etat(t);
    t.survole = false; document.activeElement = body;
    emettre("pointerdown", evenement({ pointerType: "touch", target: body }));
    r.appuiAilleurs = etat(t);

    // 3. Échap sous la SOURIS, sans focus : fermé ; la souris qui s'en va rend la bulle.
    t = neuf(); t.survole = true;
    emettre("keydown", evenement({ key: "Escape" }));
    r.echapSouris = etat(t);
    t.survole = false;
    emettre("pointerout", evenement({ pointerType: "mouse", target: t, relatedTarget: body }));
    r.sourisPartie = etat(t);

    // 4. Au DOIGT, dans une carte cliquable : le premier appui lit, le second agit.
    const carte = body.appendChild(new El("div", ["carte"], { onclick: "agir()" }));
    t = neuf({ "data-bulle-avant-clic": "" }); body.enfants.pop(); carte.appendChild(t);
    const cible = t.enfants[0];
    emettre("pointerdown", evenement({ pointerType: "touch", target: cible }));
    const c1 = emettre("click", evenement({ target: cible }));
    r.appui1 = Object.assign(etat(t), { retenu: c1.retenu, arrete: c1.arrete });
    emettre("pointerdown", evenement({ pointerType: "touch", target: cible }));
    const c2 = emettre("click", evenement({ target: cible }));
    r.appui2 = Object.assign(etat(t), { retenu: c2.retenu, arrete: c2.arrete });
  } catch (e) {
    r.erreur = String(e && e.message || e);
  }
}
process.stdout.write(JSON.stringify(out));
"""


@functools.lru_cache(maxsize=None)
def _executer(page, script="infobulles.js"):
    if not NODE:
        pytest.skip("node absent : le script ne peut pas être exécuté")
    with tempfile.TemporaryDirectory() as d:
        h = os.path.join(d, "h.js")
        p = os.path.join(d, "familles.json")
        io.open(h, "w", encoding="utf-8").write(_HARNAIS)
        io.open(p, "w", encoding="utf-8").write(json.dumps([list(f) for f in FAMILLES]))
        r = subprocess.run([NODE, h, os.path.join(_RACINE, script),
                            os.path.join(_RACINE, page), p],
                           capture_output=True, text=True, timeout=90)
    if r.returncode != 0:
        pytest.fail("le script n'a pas tourné sur %s :\n%s" % (page, (r.stderr or "")[-2500:]))
    return json.loads(r.stdout)


def _regles(css):
    """[(sélecteur, {propriété: (valeur, important)})] dans l'ordre publié."""
    out = []
    for sel, corps in re.findall(r"([^{}]+)\{([^{}]*)\}", css or ""):
        decl = {}
        for d in corps.split(";"):
            if ":" not in d:
                continue
            k, v = d.split(":", 1)
            imp = "!important" in v.replace(" ", "")
            decl[k.strip().lower()] = (re.sub(r"!\s*important", "", v).strip(), imp)
        out.append((sel.strip(), decl))
    return out


def _parties(sel):
    """Les parties d'une liste de sélecteurs, aux virgules de premier niveau."""
    out, prof, debut = [], 0, 0
    for i, c in enumerate(sel):
        if c in "([":
            prof += 1
        elif c in ")]":
            prof -= 1
        elif c == "," and prof == 0:
            out.append(sel[debut:i].strip())
            debut = i + 1
    out.append(sel[debut:].strip())
    return out


def _survols_de_la_page(html, declencheur, bulle):
    """Les règles de la PAGE qui révèlent la bulle au survol de son parent :
    {propriété: valeur}, lues dans les blocs <style> — la spécification que
    les jumelles doivent reprendre, lue ici sans passer par le script."""
    css = re.sub(r"/\*.*?\*/", "", "".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S)), flags=re.S)
    trouvees = []
    for sel, corps in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        for p in _parties(re.sub(r"\s+", " ", sel.strip())):
            if p == ".%s:hover .%s" % (declencheur, bulle):
                decl = {}
                for d in corps.split(";"):
                    if ":" in d:
                        k, v = d.split(":", 1)
                        decl[k.strip().lower()] = v.strip()
                trouvees.append(decl)
    return trouvees


# ══════════════════════════════════════════════════════════════════════════
#  1. LES FAMILLES SONT RECONNUES À CE QU'ELLES FONT — ET UN MENU N'EN EST PAS
# ══════════════════════════════════════════════════════════════════════════

def test_les_QUATRE_familles_de_Sentinel_sont_reconnues():
    """LE CŒUR DU DÉFAUT. Avant : zéro famille enfant, cent quatre-vingt-sept
    déclencheurs qu'aucun appui ne concernait."""
    r = _executer("sentinel.html")
    assert r["enfants"] is not None, (
        "le script ne reconnaît aucune bulle ENFANT : les quatre familles de "
        "Sentinel restent à la souris")
    vues = {tuple(e) for e in r["enfants"]}
    manquantes = [f for f in FAMILLES if (".%s" % f[0], ".%s" % f[1]) not in vues]
    assert not manquantes, "familles non reconnues : %s (vues : %s)" % (manquantes, sorted(vues))
    parties = _parties(r["selecteur"])
    absents = [d for d, _b in FAMILLES if ".%s" % d not in parties]
    assert not absents, (
        "ces déclencheurs ne sont pas dans le sélecteur de l'appui : %s — "
        "un appui du doigt les ignorerait (sélecteur : %r)" % (absents, r["selecteur"]))


def test_le_script_ne_NOMME_aucune_famille():
    """DÉRIVÉ, PAS LISTÉ. Une liste de noms écrite dans le script ne saurait
    pas qu'une cinquième famille est née — c'est une règle, pas une relecture,
    qui avait trouvé les deux pages oubliées la fois précédente. On lit le
    CODE : un commentaire peut citer une famille en exemple, pas le code."""
    code = re.sub(r"/\*.*?\*/", "", SCRIPT, flags=re.S)
    code = re.sub(r"(?m)^\s*//.*$", "", code)
    assert "function jumelles" in code, "le code du script n'a pas pu être isolé"
    cites = [d for f in FAMILLES for d in f if d in code]
    assert not cites, "le script cite des familles en dur : %s" % cites


#: LE BANC DE LA RECONNAISSANCE : une feuille écrite pour séparer chaque
#: critère. Deux bulles vraies — par un descendant, par un enfant direct —
#: et cinq imitations, chacune écartée par UN critère et un seul.
_BANC = """<style>
.aide{position:relative}
.aide-texte{display:none;position:absolute;pointer-events:none}
.aide:hover .aide-texte{display:block}
.puce-texte{opacity:0;position:absolute;pointer-events:none}
.puce:hover > .puce-texte{opacity:1}
.fleche{opacity:0;pointer-events:none}
.carte:hover .fleche{opacity:1}
.sous-menu{display:none;position:absolute;pointer-events:none}
.menu:hover .sous-menu{display:block;pointer-events:auto}
.volet{display:none;position:absolute}
.panneau:hover .volet{display:block}
.souligne{position:absolute;pointer-events:none;color:#000}
.lien:hover .souligne{color:#c00}
.deco::after{content:'';position:absolute;pointer-events:none;opacity:0}
.cadre:hover .deco::after{opacity:1}
</style>"""


def test_ce_qui_N_EST_PAS_une_bulle_n_est_pas_pris(tmp_path):
    """CHAQUE CRITÈRE A SON IMITATION. Une flèche décorative révélée au
    survol mais posée DANS le flux ; un menu qui redevient cliquable une
    fois ouvert ; un volet flottant qu'on peut cliquer ; un survol qui
    colore sans rien révéler ; un pseudo-élément, que `querySelector` ne
    sait pas viser pour en lire le texte. Aucune page du dépôt ne les réunit
    toutes : sans ce banc, un critère pourrait disparaître sans que rien ne
    tombe."""
    page = tmp_path / "banc.html"
    page.write_text(_BANC, encoding="utf-8")
    r = _executer(str(page))
    assert r["enfants"] is not None, "le script ne reconnaît aucune bulle enfant"
    vues = sorted(tuple(e) for e in r["enfants"])
    assert vues == [(".aide", ".aide-texte"), (".puce", ".puce-texte")], (
        "reconnues : %s — attendu : les deux bulles vraies, et elles seules" % vues)


def test_un_MENU_deroulant_n_est_PAS_une_bulle():
    """LE FAUX POSITIF MESURÉ. Le menu de l'accueil s'écrit comme une bulle
    — `li.has-dropdown:hover .nav-dropdown`, flottant, `pointer-events:none`
    au repos — et une première version l'a pris pour une : son appui aurait
    été retenu. Ce qui le distingue : ouvert, il REDEVIENT cliquable
    (`pointer-events:all` dans sa règle de survol). Une bulle, jamais."""
    assert re.search(r"has-dropdown:hover \.nav-dropdown,\s*\.nl li\.has-dropdown\.open "
                     r"\.nav-dropdown\{[^}]*pointer-events:all", INDEX), (
        "le menu témoin de l'accueil a changé de forme : cette règle ne "
        "mesure plus rien")
    r = _executer("index.html")
    assert r["enfants"] is not None, "le script ne reconnaît aucune bulle enfant"
    menus = [e for e in r["enfants"] if "nav-dropdown" in e[1]]
    assert not menus, "le menu déroulant est pris pour une bulle : %s" % menus
    assert "has-dropdown" not in r["selecteur"], (
        "l'entrée du menu est un déclencheur de bulle : son appui serait "
        "retenu au doigt — %r" % r["selecteur"])


# ══════════════════════════════════════════════════════════════════════════
#  2. CE QUE LE SCRIPT PUBLIE
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("declencheur,bulle", FAMILLES)
def test_chaque_bulle_enfant_a_ses_TROIS_jumelles(declencheur, bulle):
    """LA CLASSE qui ouvre au doigt, LE FOCUS CLAVIER qui ouvre au clavier, et
    la classe qui FERME à la demande. Les deux premières reprennent les
    déclarations EXACTES du survol de la page — pas une valeur devinée ; la
    troisième n'éteint QUE ce que le survol allume."""
    survols = _survols_de_la_page(SENTINEL, declencheur, bulle)
    assert survols, "la page n'a plus de survol .%s:hover .%s" % (declencheur, bulle)
    publiees = _regles(_executer("sentinel.html")["css"])
    for survol in survols:
        for jumelle in (".%s.%s .%s" % (declencheur, OUVERTE, bulle),
                        ".%s:focus-visible .%s" % (declencheur, bulle)):
            decl = [d for s, d in publiees if jumelle in _parties(s)]
            assert decl, "la jumelle %r n'est pas publiée" % jumelle
            repris = {k: v for k, (v, _i) in decl[0].items()}
            assert repris == survol, (
                "la jumelle %r ne reprend pas le survol : %r au lieu de %r"
                % (jumelle, repris, survol))
        fermee = ".%s.%s .%s" % (declencheur, FERMEE, bulle)
        decl = [d for s, d in publiees if fermee in _parties(s)]
        assert decl, "la fermeture %r n'est pas publiée" % fermee
        attendu = {k: (ETEINT[k], True) for k in survol if k in ETEINT}
        assert attendu and decl[0] == attendu, (
            "la fermeture %r éteint %r au lieu de %r" % (fermee, decl[0], attendu))


@pytest.mark.parametrize("page", ["sentinel.html", "index.html", "formation.html"])
def test_le_script_ne_touche_JAMAIS_un_element_au_repos(page):
    """LE DÉFAUT DU CONTOUR, MESURÉ AU NAVIGATEUR : 32 infobulles sur 32 de
    l'accueil portaient au repos un contour de 2 px. « [data-tooltip],
    [data-tip] » suivi de « :focus-visible{outline…} » laisse la première
    partie nue — `[data-tooltip]` tout court.

    L'INVARIANT : chaque partie de chaque règle publiée exige un état — la
    classe ouverte, la classe fermée, ou le focus clavier. Seule la région
    d'annonce, invisible par construction, y échappe."""
    publiees = _regles(_executer(page)["css"])
    assert publiees, "le script n'a rien publié sur %s" % page
    nues = [p for s, _d in publiees for p in _parties(s)
            if not re.search(r"\.bulle-ouverte|\.bulle-fermee|:focus-visible|#bulle-annonce", p)]
    assert not nues, (
        "ces parties s'appliquent à un élément AU REPOS, sans ouverture ni "
        "focus : %s" % nues[:6])


def test_la_fermeture_est_publiee_EN_DERNIER():
    """À SPÉCIFICITÉ ÉGALE, LA DERNIÈRE RÈGLE L'EMPORTE. `[data-tooltip]:
    focus-visible::after{opacity:1 !important}` et sa fermeture ont le même
    poids : publiée avant, la fermeture perdrait contre le focus, et Échap
    ne refermerait pas la bulle de celui qui tabule."""
    publiees = _regles(_executer("sentinel.html")["css"])
    rangs = [i for i, (s, _d) in enumerate(publiees) if "." + FERMEE in s]
    assert rangs, "aucune règle de fermeture n'est publiée"
    assert rangs == list(range(len(publiees) - len(rangs), len(publiees))), (
        "des règles passent APRÈS la fermeture : %s"
        % [s for i, (s, _d) in enumerate(publiees) if i > rangs[0] and i not in rangs][:3])


def test_fermer_n_eteint_QUE_la_visibilite():
    """ÉTEINDRE, C'EST RENDRE À CE QUE LE SURVOL ALLUME SA VALEUR ÉTEINTE —
    rien d'autre : ni position, ni couleur, ni taille. Une fermeture qui
    toucherait autre chose déplacerait l'élément qu'on vient de fermer."""
    publiees = _regles(_executer("sentinel.html")["css"])
    # SANS FERMETURE PUBLIÉE, IL N'Y AURAIT AUCUNE FAUTE À TROUVER : la règle
    # passerait à vide, sur l'ancien script comme sur un script qui ne
    # fermerait plus rien.
    assert any("." + FERMEE in s for s, _d in publiees), (
        "aucune règle de fermeture n'est publiée")
    fautes = [(s, d) for s, d in publiees if "." + FERMEE in s
              and any(k not in ETEINT or v != (ETEINT[k], True) for k, v in d.items())]
    assert not fautes, "des fermetures touchent autre chose que la visibilité : %s" % fautes[:3]


# ══════════════════════════════════════════════════════════════════════════
#  3. CE QUE LE SCRIPT FAIT — exécuté, famille par famille
# ══════════════════════════════════════════════════════════════════════════

def _scenario(famille):
    r = _executer("sentinel.html")["familles"][famille]
    assert "erreur" not in r, "le scénario a levé : %s" % r.get("erreur")
    return r


@pytest.mark.parametrize("declencheur,bulle", FAMILLES)
def test_la_bulle_enfant_est_ANNONCEE(declencheur, bulle):
    """SON TEXTE N'EST DANS AUCUN ATTRIBUT : il est dans l'élément révélé.
    Avant, la région d'annonce restait vide — mesuré au navigateur pour les
    quatre familles."""
    r = _scenario(declencheur)
    assert r["annonce"] == "Texte de la bulle %s" % declencheur, (
        "l'ouverture annonce %r" % r["annonce"])
    assert r["premier"] == {"ouverte": True, "fermee": False}, r["premier"]


@pytest.mark.parametrize("declencheur,bulle", FAMILLES)
def test_le_second_appui_ferme_A_LA_DEMANDE(declencheur, bulle):
    """LE SURVOL COLLÉ. Au doigt, Chromium garde `:hover` sur l'élément
    touché : retirer la classe ne fermait rien — opacité 1 après le second
    appui, mesurée. La fermeture pose donc sa propre classe."""
    r = _scenario(declencheur)
    assert r["second"] == {"ouverte": False, "fermee": True}, (
        "après le second appui : %r" % r["second"])
    # …ET LE TROISIÈME ROUVRE : une fermeture qui survivrait à la réouverture
    # laisserait la bulle éteinte sous sa propre classe d'ouverture.
    assert r["troisieme"] == {"ouverte": True, "fermee": False}, (
        "après le troisième appui : %r" % r["troisieme"])


@pytest.mark.parametrize("declencheur,bulle", FAMILLES)
def test_Echap_ferme_sans_DEPLACER_ni_le_focus_ni_la_souris(declencheur, bulle):
    """WCAG 1.4.13 : un contenu ouvert au focus ou au survol doit pouvoir se
    fermer sans bouger ni l'un ni l'autre. Avant : Échap ne fermait qu'une
    bulle ouverte au doigt — celle du focus ou du survol restait."""
    r = _scenario(declencheur)
    assert r["echapFocus"]["fermee"], "Échap ne ferme pas la bulle qui a le focus"
    assert r["focusGarde"], "Échap a déplacé le focus"
    assert r["echapSouris"]["fermee"], "Échap ne ferme pas la bulle sous la souris"


@pytest.mark.parametrize("declencheur,bulle", FAMILLES)
def test_la_fermeture_TOMBE_quand_l_element_n_est_plus_tenu(declencheur, bulle):
    """SANS CELA, UNE BULLE FERMÉE LE RESTERAIT POUR TOUJOURS. Elle tombe
    quand le focus part, quand la souris s'en va, sur un appui ailleurs —
    MAIS PAS quand le focus part et que le survol tient encore l'élément :
    la fermeture tient tant que l'élément est tenu, par l'un OU l'autre.
    Ce dernier cas n'a pas été reproduit au navigateur (Chromium y déplace
    le survol avec le défilement) : c'est ce harnais qui l'exerce."""
    r = _scenario(declencheur)
    assert not r["apresDepart"]["fermee"], "le focus parti, la bulle reste fermée"
    assert r["departSousSurvol"]["fermee"], (
        "le focus parti SOUS UN SURVOL COLLÉ, la fermeture est levée : la "
        "bulle se rouvre sous le doigt")
    assert not r["appuiAilleurs"]["fermee"], "un appui ailleurs ne lève pas la fermeture"
    assert not r["sourisPartie"]["fermee"], (
        "la souris partie, la bulle reste fermée : le survol suivant ne la "
        "rouvrirait pas")


@pytest.mark.parametrize("declencheur,bulle", FAMILLES)
def test_dans_une_carte_cliquable_le_premier_appui_LIT_et_le_second_AGIT(declencheur, bulle):
    """LE BADGE D'ARTICLE, MESURÉ : l'appui ouvrait la fiche du document
    par-dessus la page, et la bulle n'était jamais lue. Déclaré « lire
    d'abord », le premier appui ouvre et retient le clic — `preventDefault`
    compris, c'est lui qui empêche un <label for> de donner le focus à son
    champ ; le second laisse passer."""
    r = _scenario(declencheur)
    assert r["appui1"]["ouverte"], "le premier appui n'ouvre pas la bulle : %r" % r["appui1"]
    assert r["appui1"]["retenu"] and r["appui1"]["arrete"], (
        "le premier clic n'est pas retenu : la carte agit avant que la bulle "
        "soit lue — %r" % r["appui1"])
    assert not r["appui2"]["retenu"] and not r["appui2"]["arrete"], (
        "le second clic est retenu : la carte n'agit plus jamais au doigt — %r"
        % r["appui2"])


# ══════════════════════════════════════════════════════════════════════════
#  4. LES ÉLÉMENTS NICHÉS DANS UN CLIQUABLE DÉCLARENT « LIRE D'ABORD »
# ══════════════════════════════════════════════════════════════════════════

def test_les_badges_d_article_declarent_LIRE_D_ABORD():
    """118 BADGES, TOUS DANS UNE CARTE CLIQUABLE — recensés au navigateur."""
    badges = re.findall(r"'<span class=\"tmpl-art-badge\"[^>]*>'", PAGE_JS)
    assert badges, "le badge d'article est introuvable dans le générateur"
    nus = [b for b in badges if "data-bulle-avant-clic" not in b]
    assert not nus, "des badges d'article ne déclarent pas « lire d'abord » : %s" % nus


def test_le_point_d_interrogation_d_une_FORMULE_declare_LIRE_D_ABORD():
    """LA CARTE DE FORMULE SE CHOISIT AU CLIC : au doigt, le « ? » d'un prix
    choisissait la formule au lieu de l'expliquer — mesuré."""
    m = re.search(r"function _t\(h\)\{return '(<span class=\"prx-tip-icon\"[^>]*>)", PAGE_JS)
    assert m, "le générateur du « ? » des formules est introuvable"
    assert "data-bulle-avant-clic" in m.group(1), (
        "le « ? » des formules ne déclare pas « lire d'abord » : %s" % m.group(1))


def test_la_maturite_ARRETE_toujours_son_clic():
    """L'AUTRE PROTECTION, DÉJÀ LÀ. Six bulles de maturité sont posées dans
    une carte qui GÉNÈRE un livrable au clic, quatre dans une étape qui
    ouvre un document : le déclencheur arrête lui-même son clic. S'il cessait
    de le faire, un appui sur « i » lancerait la génération."""
    enveloppes = re.findall(r"<span class=\"mat-tooltip-wrap\"[^>]*>", PAGE_JS)
    assert len(enveloppes) >= 2, "les bulles de maturité sont introuvables"
    nues = [e for e in enveloppes if 'onclick="event.stopPropagation()"' not in e]
    assert not nues, "des bulles de maturité n'arrêtent plus leur clic : %s" % nues


class _Recensement(HTMLParser):
    """Les déclencheurs ÉCRITS dans la page, et le premier ancêtre cliquable
    de chacun — lus comme le navigateur les imbrique."""
    VIDES = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
             "meta", "param", "source", "track", "wbr"}

    def __init__(self, classes):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.classes, self.pile, self.nus, self.niches = set(classes), [], [], 0

    @staticmethod
    def _cliquable(tag, a):
        action = re.sub(r"event\.stopPropagation\(\);?", "", a.get("onclick") or "").strip()
        return (tag == "a" and a.get("href")) or tag == "button" or bool(action) \
            or (tag == "label" and a.get("for")) or a.get("role") == "button"

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.classes & set((a.get("class") or "").split()):
            parent = next((p for p in reversed(self.pile) if self._cliquable(*p)), None)
            if parent:
                self.niches += 1
                arrete = "stopPropagation" in (a.get("onclick") or "")
                if "data-bulle-avant-clic" not in a and not arrete:
                    self.nus.append("%s dans <%s %s>" % (a.get("class"), parent[0],
                                    parent[1].get("id") or parent[1].get("for") or ""))
        if tag not in self.VIDES:
            self.pile.append((tag, a))

    def handle_endtag(self, tag):
        for i in range(len(self.pile) - 1, -1, -1):
            if self.pile[i][0] == tag:
                del self.pile[i:]
                break


def test_AUCUN_declencheur_ecrit_dans_un_element_cliquable_n_est_laisse_nu():
    """LE RECENSEMENT, SUR LA PAGE ÉCRITE. Les familles viennent du SCRIPT
    lui-même — ce qu'il reconnaît —, pas d'une liste : une cinquième famille
    posée demain dans un bouton serait trouvée ici. Avant : le « ? » de la
    formule Entreprise et ceux des deux libellés de champ étaient nus."""
    r = _executer("sentinel.html")
    assert r["enfants"], "le script ne reconnaît aucune bulle enfant"
    classes = [e[0].lstrip(".") for e in r["enfants"]]
    rec = _Recensement(classes)
    rec.feed(SENTINEL)
    assert rec.niches >= 3, (
        "le recensement ne trouve plus de déclencheur niché (%d) : la lecture a "
        "changé de forme, cette règle ne mesure plus rien" % rec.niches)
    assert not rec.nus, "déclencheurs nichés sans « lire d'abord » : %s" % rec.nus


# ══════════════════════════════════════════════════════════════════════════
#  5. LA RECETTE NE SE PÉRIME PAS EN SILENCE
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("ancre", ["tmpl-modal", "plan-card", "plan-selected",
                                   "bulle-annonce", "css-bulle-ouverte"])
def test_la_recette_vise_des_ancres_QUI_EXISTENT(ancre):
    """UNE RECETTE QUI VISE UN IDENTIFIANT DISPARU NE MESURE PLUS RIEN."""
    recette = _lire("recette_bulles_sentinel.js")
    assert ancre in recette, "la recette ne vise plus %r" % ancre
    assert ancre in SENTINEL + PAGE_JS + SCRIPT, (
        "%r a disparu du code : la recette mesure un identifiant mort" % ancre)


@pytest.mark.parametrize("declencheur,bulle", FAMILLES)
def test_la_recette_mesure_les_familles_QUI_EXISTENT(declencheur, bulle):
    recette = _lire("recette_bulles_sentinel.js")
    assert "'.%s'" % declencheur in recette and "'.%s'" % bulle in recette, (
        "la recette ne mesure plus la famille %s" % declencheur)
    assert 'class="%s' % declencheur in SENTINEL + PAGE_JS, (
        "la famille %s a disparu des écrans" % declencheur)
